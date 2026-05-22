from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class SolveStatus(str, Enum):
    SOLVED = "solved"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


def _short_name(name: str) -> str:
    return re.sub(r"[^\w]", "_", name).strip("_")


@dataclass(slots=True)
class Challenge:
    id: int
    name: str
    short_name: str = field(init=False)
    challenge_dir: Path = field(init=False)
    writeup_path: Path = field(init=False)
    log_path: Path = field(init=False)
    base_challenges: Path = field(default=Path("challenges"), repr=False)
    base_wps: Path = field(default=Path("wps"), repr=False)
    base_logs: Path = field(default=Path("logs"), repr=False)

    def __post_init__(self) -> None:
        self.short_name = _short_name(self.name)
        self.challenge_dir = self.base_challenges / f"{self.id}_{self.short_name}"
        self.writeup_path = self.base_wps / f"{self.id}_{self.short_name}.md"
        self.log_path = self.base_logs / f"{self.id}_{self.short_name}.log"


@dataclass(slots=True)
class SolveResult:
    challenge_id: int
    status: SolveStatus
    flag: str | None = None
    writeup_saved: bool = False
    error_message: str | None = None
    duration_seconds: float = 0.0


@dataclass(slots=True)
class ProgressEntry:
    challenge_id: int
    status: SolveStatus
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    attempts: int = 1
