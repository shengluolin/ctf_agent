from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ctf_agent.web.db import get_conn
from ctf_agent.web.models import CreateHintRequest, Hint

router = APIRouter(prefix="/api", tags=["hints"])


@router.get("/challenges/{cid}/hints", response_model=list[Hint])
def list_hints(cid: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM hints WHERE challenge_id = ? ORDER BY created_at",
            (cid,),
        ).fetchall()
        return [dict(r) for r in rows]


@router.post("/challenges/{cid}/hints", response_model=Hint, status_code=201)
def create_hint(cid: int, body: CreateHintRequest):
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO hints (challenge_id, content) VALUES (?, ?)",
            (cid, body.content),
        )
        hint_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM hints WHERE id = ?", (hint_id,)).fetchone()
        return dict(row)


@router.delete("/hints/{hint_id}", status_code=204)
def delete_hint(hint_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM hints WHERE id = ?", (hint_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hint not found")
        conn.execute("DELETE FROM hints WHERE id = ?", (hint_id,))
