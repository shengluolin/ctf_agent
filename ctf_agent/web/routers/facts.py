from __future__ import annotations

from fastapi import APIRouter

from ctf_agent.web.db import get_conn
from ctf_agent.web.models import Fact

router = APIRouter(prefix="/api", tags=["facts"])


@router.get("/facts", response_model=list[Fact])
def list_facts(limit: int = 200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM facts ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


@router.get("/challenges/{cid}/facts", response_model=list[Fact])
def list_challenge_facts(cid: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM facts WHERE challenge_id = ? ORDER BY created_at",
            (cid,),
        ).fetchall()
        return [dict(r) for r in rows]
