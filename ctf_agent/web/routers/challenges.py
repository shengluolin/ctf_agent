from __future__ import annotations

from fastapi import APIRouter

from ctf_agent.web.db import get_conn
from ctf_agent.web.models import ChallengeDetail, ChallengeSummary, Stats

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


@router.get("", response_model=list[ChallengeSummary])
def list_challenges():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM facts WHERE challenge_id = c.id) AS facts_count,
                   (SELECT COUNT(*) FROM hints WHERE challenge_id = c.id) AS hints_count
            FROM challenges c
            ORDER BY c.started_at DESC NULLS LAST, c.id
        """).fetchall()
        return [dict(r) for r in rows]


@router.get("/stats", response_model=Stats)
def get_stats():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM challenges GROUP BY status"
        ).fetchall()
        counts = {r["status"]: r["cnt"] for r in rows}
        total = sum(counts.values())
        return Stats(
            total=total,
            solved=counts.get("solved", 0),
            failed=counts.get("failed", 0),
            timeout=counts.get("timeout", 0),
            error=counts.get("error", 0),
            solving=counts.get("solving", 0),
            pending=counts.get("pending", 0),
        )


@router.get("/{cid}", response_model=ChallengeDetail)
def get_challenge(cid: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM challenges WHERE id = ?", (cid,)).fetchone()
        if not row:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Challenge not found")
        challenge = dict(row)

        facts = conn.execute(
            "SELECT * FROM facts WHERE challenge_id = ? ORDER BY created_at",
            (cid,),
        ).fetchall()
        challenge["facts"] = [dict(r) for r in facts]

        hints = conn.execute(
            "SELECT * FROM hints WHERE challenge_id = ? ORDER BY created_at",
            (cid,),
        ).fetchall()
        challenge["hints"] = [dict(r) for r in hints]

        stdout = conn.execute(
            "SELECT * FROM stdout_log WHERE challenge_id = ? ORDER BY id DESC LIMIT 100",
            (cid,),
        ).fetchall()
        challenge["recent_stdout"] = [dict(r) for r in reversed(stdout)]

        return challenge
