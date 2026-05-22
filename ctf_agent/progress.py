from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from ctf_agent.models import ProgressEntry, SolveStatus

logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[int, ProgressEntry] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                raw = json.loads(self._path.read_text(encoding="utf-8"))
                for cid_str, entry in raw.items():
                    cid = int(cid_str)
                    self._data[cid] = ProgressEntry(
                        challenge_id=cid,
                        status=SolveStatus(entry["status"]),
                        timestamp=entry.get("timestamp", ""),
                        attempts=entry.get("attempts", 1),
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Failed to load progress from %s: %s", self._path, e)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for cid, entry in self._data.items():
            data[str(cid)] = {
                "status": entry.status.value,
                "timestamp": entry.timestamp,
                "attempts": entry.attempts,
            }
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def is_solved(self, cid: int) -> bool:
        entry = self._data.get(cid)
        return entry is not None and entry.status == SolveStatus.SOLVED

    def record(self, cid: int, status: SolveStatus) -> None:
        existing = self._data.get(cid)
        if existing:
            existing.status = status
            existing.timestamp = datetime.now().isoformat()
            existing.attempts += 1
        else:
            self._data[cid] = ProgressEntry(challenge_id=cid, status=status)
        self._save()

    def get_stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._data.values():
            key = entry.status.value
            counts[key] = counts.get(key, 0) + 1
        return counts
