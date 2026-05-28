from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from ctf_agent.web.db import get_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/challenges", tags=["renew"])

# Set by solver.py at startup
_client = None
_last_renew_time: dict[int, float] = {}  # Track last renew time per challenge
RENEW_COOLDOWN = 65  # BUUCTF requires 60s between container operations


def set_client(client) -> None:
    global _client
    _client = client


@router.post("/{cid}/renew")
def renew_container(cid: int, recreate: bool = False):
    """Renew or recreate a challenge container.

    Args:
        cid: Challenge ID
        recreate: If True, destroy and create new container. If False, just renew.

    Returns:
        {"success": bool, "url": str} on success
        {"success": False, "error": str} on failure
    """
    if _client is None:
        return {"success": False, "error": "BUUCTF client not configured"}

    row = None
    with get_conn() as conn:
        row = conn.execute("SELECT status FROM challenges WHERE id = ?", (cid,)).fetchone()

    if not row or row["status"] != "solving":
        return {"success": False, "error": "Challenge not currently solving"}

    # Check cooldown
    last_renew = _last_renew_time.get(cid, 0)
    elapsed = time.time() - last_renew
    if elapsed < RENEW_COOLDOWN:
        wait_time = int(RENEW_COOLDOWN - elapsed) + 1
        logger.info("Renew cooldown: waiting %ds before renewing challenge %d", wait_time, cid)
        time.sleep(wait_time)

    try:
        _last_renew_time[cid] = time.time()

        if recreate:
            # Destroy and recreate container
            logger.info("Destroying and recreating container for challenge %d", cid)
            _client.destroy_container(cid)
            time.sleep(5)  # Wait after destroy

            # Poll for new container URL (with longer retry delay for rate limit)
            new_url = _client.start_container(cid, max_retries=3, retry_delay=70)
            if new_url:
                logger.info("Container recreated for challenge %d: %s", cid, new_url)
                return {"success": True, "url": new_url}
            else:
                return {"success": False, "error": "Failed to start new container"}
        else:
            # Just renew existing container
            ok = _client.renew_container(cid)
            logger.info("Container renew via API for challenge %d: %s", cid, ok)

            # Get current URL
            container_info = _client.get_container(cid)
            url = container_info.get("url") if container_info else None

            if ok:
                return {"success": True, "url": url}
            else:
                return {"success": False, "error": "Renewal failed"}
    except Exception as e:
        logger.error("Container operation failed for challenge %d: %s", cid, e)
        return {"success": False, "error": str(e)}
