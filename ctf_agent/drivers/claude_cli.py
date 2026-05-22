from __future__ import annotations

import io
import logging
import tarfile
import threading
import time
from pathlib import PurePosixPath
from typing import Any, Callable

import docker
from docker.errors import DockerException, NotFound

from ctf_agent.config import DriverConfig
from ctf_agent.drivers.base import ExecuteResult, WorkerDriver

logger = logging.getLogger(__name__)

_CONTAINER_PREFIX = "ctf-agent-worker-"
_KILL_JOIN_TIMEOUT = 5.0


class ClaudeCliDriver(WorkerDriver):
    """Runs Claude Code CLI inside a long-lived Kali Docker container via exec."""

    type_name = "claude_cli"

    # Container-internal mount point for host data dirs
    WORKSPACE = "/home/kali/workspace"

    def __init__(self, config: DriverConfig) -> None:
        self._image = config.docker_image
        self._client = docker.from_env()
        self._container = None
        self._volumes: dict[str, dict] = {}
        self._env: dict[str, str] = {}
        self._env["PYTHONUNBUFFERED"] = "1"
        if config.api_key:
            self._env["ANTHROPIC_AUTH_TOKEN"] = config.api_key
        if config.api_base_url:
            self._env["ANTHROPIC_BASE_URL"] = config.api_base_url
        if config.model:
            self._env["ANTHROPIC_MODEL"] = config.model
            self._env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = config.model
            self._env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = config.model
            self._env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = config.model

    def mount(self, host_path: str, container_subdir: str) -> str:
        """Register a host directory to mount into the container. Returns container path."""
        container_path = f"{self.WORKSPACE}/{container_subdir}"
        self._volumes[host_path] = {"bind": container_path, "mode": "rw"}
        return container_path

    def ensure_running(self) -> None:
        name = self._container_name()
        container = self._get_container(name)
        if container is not None:
            container.reload()
            state = container.attrs.get("State", {}).get("Status")
            # Always remove old container and recreate with current volumes
            logger.info("Removing existing container: %s (state=%s)", name, state)
            container.remove(force=True)

        logger.info("Creating worker container: %s image=%s", name, self._image)
        logger.info("Mounting volumes: %s", self._volumes)
        self._container = self._client.containers.run(
            self._image,
            ["sleep", "infinity"],
            detach=True,
            name=name,
            network_mode="host",
            volumes=self._volumes,
            entrypoint=[],
        )
        logger.info("Worker container created: %s", name)

    def execute(
        self,
        prompt: str,
        timeout: int,
        on_stdout: Callable[[str], None] | None = None,
        workdir: str | None = None,
    ) -> ExecuteResult:
        assert self._container is not None
        command = [
            "claude",
            "--dangerously-skip-permissions",
            "--output-format", "stream-json",
            "--verbose",
            "-p", "--", prompt,
        ]

        return self._exec_command(command, self._env, timeout, on_stdout, workdir=workdir)

    def write_prompt_file(self, content: str) -> str:
        """Write prompt to a file inside the container, return the path."""
        path = "/home/kali/workspace/prompt.md"
        self._write_file(path, content)
        return path

    def cleanup(self) -> None:
        name = self._container_name()
        container = self._get_container(name)
        if container is None:
            return
        try:
            container.remove(force=True)
            logger.info("Worker container removed: %s", name)
        except (NotFound, DockerException) as e:
            logger.warning("Failed to remove container %s: %s", name, e)

    def _container_name(self) -> str:
        return f"{_CONTAINER_PREFIX}main"

    def _get_container(self, name: str):
        try:
            return self._client.containers.get(name)
        except NotFound:
            return None

    def _exec_command(
        self,
        command: list[str],
        env: dict[str, str],
        timeout: int,
        on_stdout: Callable[[str], None] | None = None,
        workdir: str | None = None,
    ) -> ExecuteResult:
        api = self._container.client.api
        exec_info = api.exec_create(
            self._container.id,
            ["timeout", "-k", f"{timeout + 5}s", f"{timeout}s"] + command,
            stdout=True,
            stderr=True,
            stdin=False,
            tty=False,
            environment=env,
            workdir=workdir,
        )
        exec_id = exec_info["Id"]

        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        timed_out = False
        read_error: str | None = None
        done = threading.Event()

        def _read():
            nonlocal read_error
            try:
                stream = api.exec_start(exec_id, detach=False, tty=False, stream=True, demux=True)
                for chunk in stream:
                    so, se = _split_chunk(chunk)
                    if so:
                        stdout_chunks.append(so)
                        if on_stdout:
                            on_stdout(so)
                    if se:
                        stderr_chunks.append(se)
            except DockerException as e:
                read_error = str(e)
            finally:
                _close_stream(stream)
                done.set()

        reader = threading.Thread(target=_read, daemon=True)
        reader.start()

        # Wait for completion with a buffer beyond the container timeout
        reader.join(timeout=timeout + 30)
        if reader.is_alive():
            timed_out = True
            # Try to kill the exec process
            _kill_exec(api, self._container, exec_id)
            reader.join(timeout=_KILL_JOIN_TIMEOUT)

        if read_error and not stderr_chunks:
            stderr_chunks.append(read_error)

        returncode = _resolve_exit_code(api, exec_id, timed_out)

        return ExecuteResult(
            stdout="".join(stdout_chunks),
            stderr="".join(stderr_chunks),
            returncode=returncode,
            timed_out=timed_out,
        )

    def _write_file(self, path: str, content: str) -> None:
        archive_path, archive = _text_file_archive(path, content)
        ok = self._container.put_archive(archive_path, archive)
        if not ok:
            raise RuntimeError(f"Failed to write file to container: {path}")


def _split_chunk(chunk: Any) -> tuple[str, str]:
    if isinstance(chunk, tuple):
        stdout, stderr = chunk
    else:
        stdout, stderr = chunk, None
    return _decode(stdout), _decode(stderr)


def _decode(chunk: bytes | str | None) -> str:
    if chunk is None:
        return ""
    if isinstance(chunk, bytes):
        return chunk.decode("utf-8", errors="replace")
    return chunk


def _close_stream(stream: Any) -> None:
    if stream is None:
        return
    close = getattr(stream, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass
    response = getattr(stream, "_response", None)
    rc = getattr(response, "close", None)
    if callable(rc):
        try:
            rc()
        except Exception:
            pass


def _kill_exec(api, container, exec_id: str) -> None:
    try:
        details = api.exec_inspect(exec_id)
    except DockerException:
        return
    if not details.get("Running"):
        return
    pid = details.get("Pid")
    if pid:
        container.exec_run(["kill", "-KILL", str(pid)], stdout=False, stderr=False)


def _resolve_exit_code(api, exec_id: str, timed_out: bool) -> int:
    deadline = time.monotonic() + _KILL_JOIN_TIMEOUT
    while True:
        try:
            details = api.exec_inspect(exec_id)
        except DockerException:
            return 137 if timed_out else 1
        exit_code = details.get("ExitCode")
        if exit_code is not None:
            return int(exit_code)
        if time.monotonic() >= deadline:
            return 137 if timed_out else 1
        time.sleep(0.1)


def _text_file_archive(path: str, content: str) -> tuple[str, bytes]:
    target = PurePosixPath(path)
    parts = target.parts[1:]
    if len(parts) == 1:
        archive_path = "/"
    else:
        archive_path = f"/{parts[0]}"
        parts = parts[1:]

    payload = content.encode("utf-8")
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        file_name = "/".join(parts)
        info = tarfile.TarInfo(file_name)
        info.size = len(payload)
        info.mode = 0o644
        archive.addfile(info, io.BytesIO(payload))
    return archive_path, stream.getvalue()
