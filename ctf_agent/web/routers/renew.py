from __future__ import annotations

import logging

from fastapi import APIRouter

from ctf_agent.web.db import get_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/challenges", tags=["renew"])

# Set by solver.py at startup
_client = None


def set_client(client) -> None:
    global _client
    _client = client


@router.post("/{cid}/renew")
def renew_container(cid: int):
    if _client is None:
        return {"success": False, "error": "BUUCTF client not configured"}

    row = None
    with get_conn() as conn:
        row = conn.execute("SELECT status FROM challenges WHERE id = ?", (cid,)).fetchone()

    if not row or row["status"] != "solving":
        return {"success": False, "error": "Challenge not currently solving"}

    try:
        ok = _client.renew_container(cid)
        logger.info("Container renew via API for challenge %d: %s", cid, ok)
        return {"success": ok}
    except Exception as e:
        logger.error("Container renew failed for challenge %d: %s", cid, e)
        return {"success": False, "error": str(e)}
