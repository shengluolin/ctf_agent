from __future__ import annotations

from fastapi import APIRouter

from ctf_agent.web.db import get_conn
from ctf_agent.web.models import StdoutLine

router = APIRouter(prefix="/api/challenges", tags=["stream"])


@router.get("/{cid}/stdout", response_model=list[StdoutLine])
def get_stdout(cid: int, since_id: int = 0, limit: int = 200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM stdout_log WHERE challenge_id = ? AND id > ? ORDER BY id ASC LIMIT ?",
            (cid, since_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
