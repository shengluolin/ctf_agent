from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from ctf_agent.web.db import get_conn
from ctf_agent.web.models import ChallengeDetail, ChallengeSummary, Stats

router = APIRouter(prefix="/api/challenges", tags=["challenges"])
logger = logging.getLogger(__name__)


class AddChallengeRequest(BaseModel):
    challenge_id: int
    name: str | None = None


class AddChallengeResponse(BaseModel):
    success: bool
    message: str
    challenge_id: int
    name: str = ""


# BUUCTF client for fetching challenge info
_buuctf_client = None


def set_buuctf_client(client):
    global _buuctf_client
    _buuctf_client = client


def _find_project_root() -> Path:
    """Find project root containing scripts/challenge_list.py."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "scripts" / "challenge_list.py").exists():
            return parent
    return current


@router.post("/add", response_model=AddChallengeResponse)
def add_challenge(req: AddChallengeRequest):
    """Add a new challenge to the list."""
    project_root = _find_project_root()
    list_path = project_root / "scripts" / "challenge_list.py"

    # Import current list
    import sys
    sys.path.insert(0, str(project_root / "scripts"))
    from challenge_list import CHALLENGE_LIST

    # Check if already exists
    for existing_id, existing_name in CHALLENGE_LIST:
        if existing_id == req.challenge_id:
            return AddChallengeResponse(
                success=False,
                message=f"Challenge {req.challenge_id} already exists: {existing_name}",
                challenge_id=req.challenge_id,
                name=existing_name,
            )

    # Get name from request or fetch from BUUCTF
    name = req.name
    if not name and _buuctf_client:
        info = _buuctf_client.get_challenge_info(req.challenge_id)
        if info:
            name = info.get("name", f"Challenge {req.challenge_id}")
        else:
            return AddChallengeResponse(
                success=False,
                message=f"Challenge {req.challenge_id} not found on BUUCTF. Use 'name' parameter to specify manually.",
                challenge_id=req.challenge_id,
            )

    if not name:
        return AddChallengeResponse(
            success=False,
            message="Name required (BUUCTF client not configured or challenge not found)",
            challenge_id=req.challenge_id,
        )

    # Add to file
    new_entry = f"    ({req.challenge_id}, \"{name}\"),\n"
    with open(list_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    for line in lines:
        if line.strip() == "]" and not inserted:
            new_lines.append(new_entry)
            inserted = True
        new_lines.append(line)

    if not inserted:
        new_lines.insert(-1, new_entry)

    with open(list_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Update in-memory list
    CHALLENGE_LIST.append((req.challenge_id, name))

    logger.info("Added challenge %d: %s via web API", req.challenge_id, name)

    return AddChallengeResponse(
        success=True,
        message=f"Added [{req.challenge_id}] {name}",
        challenge_id=req.challenge_id,
        name=name,
    )


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
