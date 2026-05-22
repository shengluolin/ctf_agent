from __future__ import annotations

from pydantic import BaseModel


class ChallengeSummary(BaseModel):
    id: int
    name: str
    status: str
    flag: str | None = None
    error_message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float = 0
    attempt_count: int = 0
    facts_count: int = 0
    hints_count: int = 0


class Fact(BaseModel):
    id: int
    challenge_id: int
    category: str
    content: str
    raw_line: str | None = None
    created_at: str


class Hint(BaseModel):
    id: int
    challenge_id: int
    content: str
    created_at: str
    used_in_attempt: int | None = None


class StdoutLine(BaseModel):
    id: int
    text: str
    created_at: str


class ChallengeDetail(BaseModel):
    id: int
    name: str
    status: str
    flag: str | None = None
    error_message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float = 0
    attempt_count: int = 0
    facts: list[Fact] = []
    hints: list[Hint] = []
    recent_stdout: list[StdoutLine] = []


class CreateHintRequest(BaseModel):
    content: str


class Stats(BaseModel):
    total: int = 0
    solved: int = 0
    failed: int = 0
    timeout: int = 0
    error: int = 0
    solving: int = 0
    pending: int = 0
