from __future__ import annotations

import json
import logging
import threading
import time

from ctf_agent.buuctf import BuuctfClient
from ctf_agent.config import AppConfig
from ctf_agent.drivers.claude_cli import ClaudeCliDriver
from ctf_agent.fact_extractor import process_chunk
from ctf_agent.models import Challenge, SolveResult, SolveStatus
from ctf_agent.output_parser import parse_output
from ctf_agent.prompting import load_template, render_template
from ctf_agent.web import state as web_state
from ctf_agent.writeup_search import format_writeup_hints, search_writeup

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
                container_url = None  # prevent double-destroy in finally
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

        # Convert host paths to container paths via driver mount mapping
        # e.g. host "E:\share\...\challenges\703_Havefun" → container "/home/kali/workspace/challenges/703_Havefun"
        container_challenges = f"{driver.WORKSPACE}/challenges"
        container_wps = f"{driver.WORKSPACE}/wps"
        container_challenge_dir = f"{container_challenges}/{challenge.challenge_dir.name}"
        container_wp_path = f"{container_wps}/{challenge.writeup_path.name}"

        # Render prompt with container paths
        # Note: do NOT pass cookie/csrf to the prompt — agent should only
        # attack the challenge target, never the BUUCTF platform itself.
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

        # Track injected hint IDs to avoid duplicates
        _injected_hint_ids: set[int] = set(h["id"] for h in (pending_hints or []))
        _hint_ids_to_mark: list[int] = [h["id"] for h in (pending_hints or [])]

        # Execute via Docker worker with real-time streaming
        timeout = timeout_override if timeout_override is not None else config.driver.timeout
        logger.info("[%d] Executing in Docker worker (timeout=%ds)", challenge.id, timeout)

        # Start container renewal background thread
        renew_stop = threading.Event()
        last_activity = time.time()
        renew_check_interval = 50 * 60  # Check at 50 min, auto-renew if agent active (BUUCTF limit is 1h)
        renew_signal_dir = challenge.challenge_dir
        renew_signal_dir.mkdir(parents=True, exist_ok=True)

        def _on_readable_line(line: str) -> None:
            nonlocal last_activity
            last_activity = time.time()
            readable_lines.append(line)
            print(line, flush=True)
            web_state.append_stdout_line(challenge.id, line)

        _last_hint_check: float = 0.0
        _HINT_CHECK_INTERVAL = 5.0  # seconds between hint DB queries

        def _on_chunk(text: str) -> None:
            nonlocal last_activity
            last_activity = time.time()
            parser.feed(text)
            process_chunk(challenge.id, text)
            _check_new_hints()

        def _check_new_hints() -> None:
            """Check for new hints and write them to challenge dir as signal file."""
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
                _append_hints_file(hint_text)
                web_state.mark_hints_used([h["id"] for h in fresh], attempt=1)
                logger.info("[%d] Injected %d new hints via signal file", challenge.id, len(fresh))
            except Exception as e:
                logger.warning("[%d] _check_new_hints failed: %s", challenge.id, e)

        def _renew_loop():
            import requests as _req
            check_interval = 5 * 60  # Health check every 5 minutes
            last_renew = time.time()
            while not renew_stop.wait(check_interval):
                # 1. Health check: is the target still reachable?
                try:
                    r = _req.get(container_url, timeout=10, verify=False, allow_redirects=True)
                    alive = r.status_code < 500  # 404 is fine, container is still up
                except _req.RequestException:
                    alive = False
                    logger.warning("[%d] Container health check FAILED (unreachable)", challenge.id)

                # 2. Auto-renew if agent is active (regardless of health check result,
                #    since the container may briefly flap)
                idle = time.time() - last_activity
                elapsed_since_renew = time.time() - last_renew
                if idle < 5 * 60 and elapsed_since_renew > 10 * 60:
                    logger.info("[%d] Agent active (idle %.0fs), auto-renewing container", challenge.id, idle)
                    try:
                        ok = client.renew_container(challenge.id)
                        if ok:
                            last_renew = time.time()
                        logger.info("[%d] Auto-renew result: %s", challenge.id, ok)
                    except Exception as e:
                        logger.error("[%d] Auto-renew failed: %s", challenge.id, e)

                # 3. If container is dead, try to renew aggressively
                if not alive:
                    logger.warning("[%d] Container unreachable, attempting emergency renew", challenge.id)
                    try:
                        ok = client.renew_container(challenge.id)
                        if ok:
                            last_renew = time.time()
                            logger.info("[%d] Emergency renew succeeded", challenge.id)
                            time.sleep(15)  # Wait for container to come up
                        else:
                            logger.error("[%d] Emergency renew failed — container may be gone", challenge.id)
                    except Exception as e:
                        logger.error("[%d] Emergency renew error: %s", challenge.id, e)

        readable_lines: list[str] = []
        parser = _StreamParser(on_line=_on_readable_line)

        renew_thread = threading.Thread(target=_renew_loop, daemon=True)
        renew_thread.start()

        # Writeup auto-search background thread
        _writeup_searched = False

        _hints_file_lock = threading.Lock()

        def _append_hints_file(hint_text: str) -> None:
            """Thread-safe append to .hints_new signal file."""
            signal_file = renew_signal_dir / ".hints_new"
            with _hints_file_lock:
                try:
                    existing = signal_file.read_text(encoding="utf-8") if signal_file.exists() else ""
                except FileNotFoundError:
                    existing = ""
                signal_file.write_text(existing + "\n" + hint_text, encoding="utf-8")

        def _writeup_search_loop():
            nonlocal _writeup_searched
            delay = config.retry.writeup_search_delay
            check_interval = 60
            elapsed = 0
            while not renew_stop.wait(check_interval):
                elapsed += check_interval
                if elapsed >= delay and not _writeup_searched:
                    logger.info("[%d] Auto-searching writeups after %ds", challenge.id, elapsed)
                    try:
                        results = search_writeup(challenge.name)
                        hint_text = format_writeup_hints(results)
                        if hint_text:
                            _append_hints_file(hint_text)
                            logger.info("[%d] Injected writeup hints from %d sources", challenge.id, len(results))
                        else:
                            logger.info("[%d] No useful writeups found", challenge.id)
                    except Exception as e:
                        logger.warning("[%d] Writeup search failed: %s", challenge.id, e)
                        continue  # retry on next check
                    _writeup_searched = True
                    break

        writeup_thread = threading.Thread(target=_writeup_search_loop, daemon=True)
        writeup_thread.start()

        try:
            result = driver.execute(prompt, timeout, on_stdout=_on_chunk, workdir=container_challenge_dir)
        finally:
            renew_stop.set()
            # Wait for writeup thread to finish so it doesn't write after cleanup
            writeup_thread.join(timeout=10)
            # Clean up signal files
            for name in (".container_renew_ask", ".hints_new"):
                sf = renew_signal_dir / name
                try:
                    if sf.exists():
                        sf.unlink()
                except FileNotFoundError:
                    pass
        parser.flush()

        elapsed = time.time() - start_time

        # Save readable log to host
        readable_stdout = "\n".join(readable_lines)
        _save_log(challenge, readable_stdout, result.stderr, "TIMEOUT" if result.timed_out else "")

        if result.timed_out:
            logger.warning("[%d] Timed out after %.0fs", challenge.id, elapsed)
            return SolveResult(
                challenge_id=challenge.id,
                status=SolveStatus.TIMEOUT,
                duration_seconds=elapsed,
            )

        # Mark hints as used after execution completes (regardless of outcome)
        if _hint_ids_to_mark:
            web_state.mark_hints_used(_hint_ids_to_mark, attempt=1)

        # Parse output — use raw stdout for flag parsing (contains all JSON events)
        stdout_for_parsing = result.stdout if result.stdout is not None and result.stdout != "" else readable_stdout
        parsed = parse_output(stdout_for_parsing, result.stderr)

        if parsed.flag:
            # Try to submit flag
            submit_result = client.submit_flag(challenge.id, parsed.flag)
            # Check for network/API errors first
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
                # Writeup may have been written by Claude inside container (volume mount),
                # but also save from parsed output as fallback
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
        # Destroy BUUCTF challenge container
        if container_url:
            client.destroy_container(challenge.id)
            logger.info("[%d] Challenge container destroyed", challenge.id)


def _save_log(challenge: Challenge, stdout: str, stderr: str, prefix: str = "") -> None:
    challenge.log_path.parent.mkdir(parents=True, exist_ok=True)
    label = f"{prefix} " if prefix else ""
    content = f"=== {label}STDOUT ===\n{stdout}\n=== {label}STDERR ===\n{stderr}"
    challenge.log_path.write_text(content, encoding="utf-8")
