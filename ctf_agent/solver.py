from __future__ import annotations

import json
import logging
import threading
import time
import uuid

from ctf_agent.buuctf import BuuctfClient
from ctf_agent.config import AppConfig
from ctf_agent.drivers.claude_cli import ClaudeCliDriver
from ctf_agent.fact_extractor import process_chunk
from ctf_agent.models import Challenge, SolveResult, SolveStatus
from ctf_agent.output_parser import parse_output
from ctf_agent.progress_monitor import ProgressMonitor
from ctf_agent.prompting import load_template, render_template
from ctf_agent.web import state as web_state
from ctf_agent.writeup_search import set_proxy

logger = logging.getLogger(__name__)


class _StreamParser:
    """Parse Claude CLI stream-json output into readable text lines."""

    def __init__(self, on_line: callable) -> None:
        self._on_line = on_line
        self._buffer = ""
        self._tool_inputs: dict[str, str] = {}
        self._turn_had_deltas = False

    def feed(self, chunk: str) -> None:
        self._buffer += chunk
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                self._parse_line(line)

    def flush(self) -> None:
        if self._buffer.strip():
            self._parse_line(self._buffer.strip())
        self._buffer = ""

    def _parse_line(self, line: str) -> None:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            self._on_line(line)
            return

        event_type = event.get("type", "")

        if event_type == "content_block_delta":
            self._turn_had_deltas = True
            delta = event.get("delta", {})
            delta_type = delta.get("type", "")
            if delta_type == "text_delta":
                text = delta.get("text", "")
                if text:
                    self._on_line(text)
            elif delta_type == "input_json_delta":
                idx = event.get("index", 0)
                partial = delta.get("partial_json", "")
                self._tool_inputs.setdefault(str(idx), "")
                self._tool_inputs[str(idx)] += partial

        elif event_type == "content_block_start":
            self._turn_had_deltas = True
            block = event.get("content_block", {})
            if block.get("type") == "tool_use":
                name = block.get("name", "unknown")
                self._on_line(f"\n[Tool: {name}]")
                idx = event.get("index", 0)
                self._tool_inputs[str(idx)] = ""

        elif event_type == "content_block_stop":
            idx = str(event.get("index", 0))
            accumulated = self._tool_inputs.pop(idx, "")
            if accumulated:
                try:
                    tool_input = json.loads(accumulated)
                    if "command" in tool_input:
                        self._on_line(f"  $ {tool_input['command']}")
                    else:
                        for k, v in tool_input.items():
                            self._on_line(f"  {k}: {v}")
                except json.JSONDecodeError:
                    if accumulated.strip():
                        self._on_line(f"  {accumulated.strip()}")

        elif event_type == "assistant":
            if not self._turn_had_deltas:
                msg = event.get("message", {})
                for block in msg.get("content", []):
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        if text:
                            for tl in text.splitlines():
                                self._on_line(tl)
                    elif block.get("type") == "tool_use":
                        name = block.get("name", "unknown")
                        self._on_line(f"\n[Tool: {name}]")
                        inp = block.get("input", {})
                        if "command" in inp:
                            self._on_line(f"  $ {inp['command']}")
                        else:
                            for k, v in inp.items():
                                self._on_line(f"  {k}: {v}")
            self._turn_had_deltas = False

        elif event_type == "tool_result":
            content = event.get("content", "")
            if isinstance(content, str) and content:
                for line in content.splitlines()[:20]:
                    self._on_line(f"  {line}")
                if content.count("\n") > 20:
                    self._on_line(f"  ... ({content.count(chr(10)) - 20} more lines)")

        elif event_type == "result":
            if not self._turn_had_deltas:
                result = event.get("result", "")
                if result:
                    for line in result.splitlines():
                        self._on_line(line)
            self._turn_had_deltas = False


def solve_challenge(
    challenge: Challenge,
    config: AppConfig,
    client: BuuctfClient,
    driver: ClaudeCliDriver,
    template: str,
    timeout_override: int | None = None,
) -> SolveResult:
    start_time = time.time()
    container_url: str | None = None

    # Set proxy for writeup search
    if config.retry.proxy:
        set_proxy(config.retry.proxy)

    try:
        # Start BUUCTF challenge container
        logger.info("[%d] %s - Starting challenge container", challenge.id, challenge.name)
        container_url = client.start_container(
            challenge.id,
            max_retries=config.retry.max_container_retries,
            retry_delay=config.retry.container_retry_delay,
        )
        if not container_url:
            logger.error("[%d] Challenge container failed to start", challenge.id)
            return SolveResult(
                challenge_id=challenge.id,
                status=SolveStatus.ERROR,
                error_message="Challenge container failed to start",
                duration_seconds=time.time() - start_time,
            )
        logger.info("[%d] Challenge URL: %s", challenge.id, container_url)

        # Pre-flight: verify target is reachable
        import requests as _requests
        try:
            probe = _requests.get(container_url, timeout=15, verify=False)
            logger.info("[%d] Target reachable (HTTP %d)", challenge.id, probe.status_code)
        except _requests.RequestException as e:
            logger.warning("[%d] Target not reachable: %s — retrying in 30s", challenge.id, e)
            time.sleep(30)
            try:
                probe = _requests.get(container_url, timeout=15, verify=False)
                logger.info("[%d] Target reachable on retry (HTTP %d)", challenge.id, probe.status_code)
            except _requests.RequestException as e2:
                logger.error("[%d] Target still unreachable: %s", challenge.id, e2)
                client.destroy_container(challenge.id)
                container_url = None
                return SolveResult(
                    challenge_id=challenge.id,
                    status=SolveStatus.ERROR,
                    error_message=f"Target unreachable: {e2}",
                    duration_seconds=time.time() - start_time,
                )

        # Ensure host directories exist
        challenge.challenge_dir.mkdir(parents=True, exist_ok=True)
        challenge.writeup_path.parent.mkdir(parents=True, exist_ok=True)
        challenge.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Save container URL for reference (agent doesn't need to call renew - backend handles it)
        _container_url_file = challenge.challenge_dir / ".container_url"
        _container_url_file.write_text(container_url)

        # Convert host paths to container paths
        container_challenges = f"{driver.WORKSPACE}/challenges"
        container_wps = f"{driver.WORKSPACE}/wps"
        container_challenge_dir = f"{container_challenges}/{challenge.challenge_dir.name}"
        container_wp_path = f"{container_wps}/{challenge.writeup_path.name}"

        # Render prompt with container paths
        prompt = render_template(
            template,
            name=challenge.name,
            url=container_url,
            cid=str(challenge.id),
            challenge_dir=container_challenge_dir,
            wp_path=container_wp_path,
        )

        # Inject user hints
        pending_hints = web_state.get_pending_hints(challenge.id)
        if pending_hints:
            hint_lines = "\n".join(f"- {h['content']}" for h in pending_hints)
            prompt += f"\n\n## User Hints (Follow These Closely)\n{hint_lines}\n"

        _injected_hint_ids: set[int] = set(h["id"] for h in (pending_hints or []))
        _hint_ids_to_mark: list[int] = [h["id"] for h in (pending_hints or [])]

        # Execute via Docker worker with real-time streaming
        timeout = timeout_override if timeout_override is not None else config.driver.timeout
        logger.info("[%d] Executing in Docker worker (timeout=%ds)", challenge.id, timeout)

        # Initialize progress monitor
        monitor = ProgressMonitor(
            challenge_id=challenge.id,
            challenge_dir=challenge.challenge_dir,
            challenge_name=challenge.name,
            target_url=container_url,
        )

        # Start container renewal background thread
        renew_stop = threading.Event()
        last_activity = time.time()
        renew_signal_dir = challenge.challenge_dir
        renew_signal_dir.mkdir(parents=True, exist_ok=True)

        # Accumulated output for progress monitoring
        _output_buffer: list[str] = []
        _OUTPUT_BUFFER_MAX = 10000  # Keep last 10k chars for progress detection

        def _on_readable_line(line: str) -> None:
            nonlocal last_activity
            last_activity = time.time()
            readable_lines.append(line)
            print(line, flush=True)
            web_state.append_stdout_line(challenge.id, line)

        _last_hint_check: float = 0.0
        _HINT_CHECK_INTERVAL = 5.0

        def _on_chunk(text: str) -> None:
            nonlocal last_activity, _output_buffer
            last_activity = time.time()
            parser.feed(text)
            process_chunk(challenge.id, text)
            _check_new_hints()

            # Track output for progress monitoring
            _output_buffer.append(text)
            if len(_output_buffer) > _OUTPUT_BUFFER_MAX:
                _output_buffer = _output_buffer[-_OUTPUT_BUFFER_MAX:]

        def _check_progress() -> None:
            """Check progress and inject hints if needed."""
            output = "".join(_output_buffer)
            monitor.check_output(output)
            hint = monitor.get_progress_hint()
            if hint:
                logger.info("[%d] Injecting progress hint", challenge.id)
                _inject_hint_prompt(hint, urgent=True)

        def _check_new_hints() -> None:
            nonlocal _last_hint_check
            now = time.time()
            if now - _last_hint_check < _HINT_CHECK_INTERVAL:
                return
            _last_hint_check = now
            try:
                new_hints = web_state.get_pending_hints(challenge.id)
                fresh = [h for h in new_hints if h["id"] not in _injected_hint_ids]
                if not fresh:
                    return
                for h in fresh:
                    _injected_hint_ids.add(h["id"])
                hint_text = "\n".join(f"- {h['content']}" for h in fresh)
                _inject_hint_prompt(f"\n## 用户提示\n{hint_text}\n")
                web_state.mark_hints_used([h["id"] for h in fresh], attempt=1)
                logger.info("[%d] Queued %d new hints for injection", challenge.id, len(fresh))
            except Exception as e:
                logger.warning("[%d] _check_new_hints failed: %s", challenge.id, e)

        def _renew_loop():
            """Auto-renew container every 8 minutes to prevent expiry.

            BUUCTF containers expire after 1 hour. This loop proactively
            renews the container every 8 minutes while the agent is active,
            so the agent never needs to call renew itself.
            """
            nonlocal container_url
            import requests as _req
            check_interval = 60  # Check every minute
            last_renew = time.time()
            last_renew_time_global = 0  # Track global renew time for cooldown

            while not renew_stop.wait(check_interval):
                try:
                    # Check if container is still alive
                    r = _req.get(container_url, timeout=10, verify=False, allow_redirects=True)
                    if "Instance can't be reached" in r.text or "实例无法访问" in r.text:
                        alive = False
                        logger.warning("[%d] Container expired (BUUCTF error page)", challenge.id)
                    else:
                        alive = r.status_code < 500
                except _req.RequestException as e:
                    alive = False
                    logger.warning("[%d] Container health check failed: %s", challenge.id, e)

                idle = time.time() - last_activity
                elapsed_since_renew = time.time() - last_renew

                # Auto-renew if agent is active and > 8 minutes since last renew
                if idle < 5 * 60 and elapsed_since_renew > 8 * 60:
                    # Check global cooldown to avoid conflicts
                    time_since_global = time.time() - last_renew_time_global
                    if time_since_global < 70:  # 70s global cooldown
                        logger.debug("[%d] Skipping renew due to global cooldown", challenge.id)
                        continue

                    logger.info("[%d] Agent active, auto-renewing container", challenge.id)
                    try:
                        ok = client.renew_container(challenge.id)
                        if ok:
                            last_renew = time.time()
                            last_renew_time_global = time.time()
                            logger.info("[%d] Auto-renew successful", challenge.id)
                        else:
                            logger.warning("[%d] Auto-renew returned False", challenge.id)
                    except Exception as e:
                        logger.error("[%d] Auto-renew failed: %s", challenge.id, e)

                # If container is dead, recreate and inject new URL
                if not alive:
                    logger.warning("[%d] Container dead, recreating...", challenge.id)
                    # Check global cooldown
                    time_since_global = time.time() - last_renew_time_global
                    if time_since_global < 70:
                        logger.info("[%d] Waiting for global cooldown (%ds left)", challenge.id, 70 - int(time_since_global))
                        continue

                    pause_hint = "\n## ⚠️ 容器已过期，正在重建...\n\n请立即停止当前所有操作，等待新URL注入！\n"
                    _inject_hint_prompt(pause_hint, urgent=True)

                    try:
                        client.destroy_container(challenge.id)
                        time.sleep(5)
                        new_url = client.start_container(challenge.id, max_retries=3, retry_delay=70)
                        if new_url:
                            container_url = new_url
                            last_renew = time.time()
                            last_renew_time_global = time.time()
                            logger.info("[%d] Container recreated: %s", challenge.id, new_url)
                            hint_text = f"\n## ✅ 新容器已就绪\n\n新的 URL: {new_url}\n请立即使用新 URL 继续解题！\n"
                            _inject_hint_prompt(hint_text)
                        else:
                            logger.error("[%d] Container recreation failed", challenge.id)
                            _inject_hint_prompt("\n## ❌ 容器重建失败，正在重试...\n")
                    except Exception as e:
                        logger.error("[%d] Container recreation error: %s", challenge.id, e)
                    except Exception as e:
                        logger.error("[%d] Container recreation error: %s", challenge.id, e)
                        error_hint = f"\n## ❌ 容器重建出错\n\n错误: {e}\n请等待系统重试...\n"
                        _inject_hint_prompt(error_hint)

        readable_lines: list[str] = []
        parser = _StreamParser(on_line=_on_readable_line)

        session_id = str(uuid.uuid4())  # Claude CLI requires full UUID format
        logger.info("[%d] Session ID: %s", challenge.id, session_id)

        _pending_hint_prompts: list[str] = []
        _pending_hint_lock = threading.Lock()
        _hint_ready = threading.Event()  # Signal for immediate injection

        renew_thread = threading.Thread(target=_renew_loop, daemon=True)
        renew_thread.start()

        _writeup_searched = False

        def _writeup_search_loop():
            nonlocal _writeup_searched
            delay = config.retry.writeup_search_delay
            check_interval = 60
            elapsed = 0
            while not renew_stop.wait(check_interval):
                elapsed += check_interval
                if elapsed >= delay and not _writeup_searched:
                    logger.info("[%d] Suggesting Agent to search writeups after %ds", challenge.id, elapsed)
                    hint_text = "\n## 建议搜索 Writeup\n\n已经过了 %d 分钟，建议使用以下方式搜索 writeup:\n- WebSearch 工具搜索题目名 + writeup\n- 访问 CSDN、先知社区、博客园等中文 writeup 网站\n- 如果找到思路，不要直接复制 payload，要理解原理后调整\n" % (elapsed // 60)
                    _inject_hint_prompt(hint_text)
                    _writeup_searched = True
                    break

        def _inject_hint_prompt(hint_text: str, urgent: bool = False) -> None:
            with _pending_hint_lock:
                _pending_hint_prompts.append(hint_text)
            if urgent:
                _hint_ready.set()  # Trigger immediate injection

        def _progress_monitor_loop():
            """Periodically check progress and inject hints if needed."""
            check_interval = 60  # Check every minute
            while not renew_stop.wait(check_interval):
                try:
                    _check_progress()
                    status = monitor.get_status()
                    logger.debug(
                        "[%d] Progress: elapsed=%ds scan=%s source=%s writeup=%s flag=%s",
                        challenge.id,
                        status["elapsed"],
                        status["checkpoints"]["scan"],
                        status["checkpoints"]["source"],
                        status["checkpoints"]["writeup"],
                        status["checkpoints"]["flag"],
                    )
                except Exception as e:
                    logger.warning("[%d] Progress check failed: %s", challenge.id, e)

        writeup_thread = threading.Thread(target=_writeup_search_loop, daemon=True)
        writeup_thread.start()

        progress_thread = threading.Thread(target=_progress_monitor_loop, daemon=True)
        progress_thread.start()

        def _hint_injector_loop():
            while not renew_stop.wait(1):  # Check every 1 second
                # Wait for either hints or timeout (30s)
                if not _hint_ready.wait(30):
                    # Timeout - check if there are pending hints anyway
                    pass
                _hint_ready.clear()

                with _pending_hint_lock:
                    prompts = list(_pending_hint_prompts)
                    _pending_hint_prompts.clear()
                if prompts:
                    combined = "\n".join(prompts)
                    logger.info("[%d] Injecting hints via session resume", challenge.id)
                    try:
                        driver.resume(
                            session_id,
                            combined,
                            timeout=120,
                            workdir=container_challenge_dir,
                        )
                        logger.info("[%d] Hint injection completed", challenge.id)
                    except Exception as e:
                        logger.warning("[%d] Hint injection failed: %s", challenge.id, e)

        hint_injector_thread = threading.Thread(target=_hint_injector_loop, daemon=True)
        hint_injector_thread.start()

        try:
            result = driver.execute(prompt, timeout, on_stdout=_on_chunk, workdir=container_challenge_dir, session_id=session_id)
        finally:
            renew_stop.set()
            writeup_thread.join(timeout=10)
            progress_thread.join(timeout=10)
            hint_injector_thread.join(timeout=10)
        parser.flush()

        elapsed = time.time() - start_time

        readable_stdout = "\n".join(readable_lines)
        _save_log(challenge, readable_stdout, result.stderr, "TIMEOUT" if result.timed_out else "")

        if result.timed_out:
            logger.warning("[%d] Timed out after %.0fs", challenge.id, elapsed)
            return SolveResult(
                challenge_id=challenge.id,
                status=SolveStatus.TIMEOUT,
                duration_seconds=elapsed,
            )

        if _hint_ids_to_mark:
            web_state.mark_hints_used(_hint_ids_to_mark, attempt=1)

        stdout_for_parsing = result.stdout if result.stdout is not None and result.stdout != "" else readable_stdout
        parsed = parse_output(stdout_for_parsing, result.stderr)

        if parsed.flag:
            submit_result = client.submit_flag(challenge.id, parsed.flag)
            if submit_result.get("error"):
                logger.error("[%d] Flag submission failed: %s", challenge.id, submit_result["error"])
                return SolveResult(
                    challenge_id=challenge.id,
                    status=SolveStatus.ERROR,
                    flag=parsed.flag,
                    error_message=f"Flag submission failed: {submit_result['error']}",
                    duration_seconds=elapsed,
                )
            status = submit_result.get("data", {}).get("status")
            if status in ("correct", "already_solved"):
                logger.info("[%d] Flag correct! %s", challenge.id, parsed.flag)
                if parsed.writeup:
                    challenge.writeup_path.write_text(parsed.writeup, encoding="utf-8")
                return SolveResult(
                    challenge_id=challenge.id,
                    status=SolveStatus.SOLVED,
                    flag=parsed.flag,
                    writeup_saved=True,
                    duration_seconds=elapsed,
                )
            else:
                logger.info("[%d] Flag incorrect: %s (response: %s)", challenge.id, parsed.flag, submit_result)
                return SolveResult(
                    challenge_id=challenge.id,
                    status=SolveStatus.FAILED,
                    flag=parsed.flag,
                    error_message=f"Flag rejected: {submit_result}",
                    duration_seconds=elapsed,
                )

        logger.info("[%d] No flag found in output", challenge.id)
        return SolveResult(
            challenge_id=challenge.id,
            status=SolveStatus.FAILED,
            error_message="No flag found in output",
            duration_seconds=elapsed,
        )

    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception("[%d] Unexpected error: %s", challenge.id, e)
        return SolveResult(
            challenge_id=challenge.id,
            status=SolveStatus.ERROR,
            error_message=str(e),
            duration_seconds=elapsed,
        )

    finally:
        if container_url:
            client.destroy_container(challenge.id)
            logger.info("[%d] Challenge container destroyed", challenge.id)


def _save_log(challenge: Challenge, stdout: str, stderr: str, prefix: str = "") -> None:
    challenge.log_path.parent.mkdir(parents=True, exist_ok=True)
    label = f"{prefix} " if prefix else ""
    content = f"=== {label}STDOUT ===\n{stdout}\n=== {label}STDERR ===\n{stderr}"
    challenge.log_path.write_text(content, encoding="utf-8")
