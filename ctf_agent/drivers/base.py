from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class ExecuteResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False


class WorkerDriver(abc.ABC):
    type_name: str

    @abc.abstractmethod
    def execute(
        self,
        prompt: str,
        timeout: int,
        on_stdout: Callable[[str], None] | None = None,
        workdir: str | None = None,
        session_id: str | None = None,
    ) -> ExecuteResult:
        """Execute the prompt inside the worker container and return output.

        on_stdout: optional callback invoked with each stdout chunk for real-time streaming.
        workdir: optional working directory inside the container.
        session_id: optional session ID for continuing a conversation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def resume(
        self,
        session_id: str,
        prompt: str,
        timeout: int,
        on_stdout: Callable[[str], None] | None = None,
        workdir: str | None = None,
    ) -> ExecuteResult:
        """Resume an existing session with a new prompt.

        This injects new instructions into a running Claude session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def ensure_running(self) -> None:
        """Make sure the worker container is up and ready."""
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        """Stop/remove the worker container."""
        raise NotImplementedError
