from __future__ import annotations

import logging
import re
import time

import requests

from ctf_agent.config import BuuctfConfig

logger = logging.getLogger(__name__)

_CSRF_RE = re.compile(r'csrf_nonce\s*=\s*["\']([^"\']+)["\']')


class BuuctfClient:
    def __init__(self, config: BuuctfConfig) -> None:
        self._base_url = config.base_url.rstrip("/")
        self._cookie = config.cookie
        self._csrf_token: str | None = None

    def _ensure_csrf(self, *, force: bool = False) -> None:
        if self._csrf_token and not force:
            return
        self._csrf_token = None
        logger.info("Fetching CSRF nonce from BUUCTF")
        r = requests.get(
            f"{self._base_url}/challenges",
            headers={"Cookie": self._cookie},
            timeout=15,
        )
        match = _CSRF_RE.search(r.text)
        if not match:
            raise RuntimeError("Failed to extract CSRF nonce from BUUCTF")
        self._csrf_token = match.group(1)
        logger.info("CSRF nonce: %s...", self._csrf_token[:16])

    def _headers(self) -> dict:
        self._ensure_csrf()
        return {
            "Cookie": self._cookie,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "CSRF-Token": self._csrf_token,
        }

    def _request(self, path: str, method: str = "GET", data: dict | None = None) -> dict:
        url = f"{self._base_url}{path}"
        try:
            if method == "POST":
                r = requests.post(url, headers=self._headers(), json=data or {}, timeout=15)
            elif method == "DELETE":
                r = requests.delete(url, headers=self._headers(), timeout=15)
            else:
                r = requests.get(url, headers=self._headers(), timeout=15)
            if r.status_code == 403:
                logger.warning("Got 403, refreshing CSRF token")
                self._ensure_csrf(force=True)
                return {"error": f"HTTP 403 - CSRF refreshed, retry needed"}
            if not (200 <= r.status_code < 300):
                return {"error": f"HTTP {r.status_code}", "http_status": r.status_code}
            return r.json()
        except requests.exceptions.JSONDecodeError:
            logger.error("BUUCTF %s %s returned non-JSON (status=%d)", method, path, r.status_code)
            return {"error": f"Non-JSON response (HTTP {r.status_code})"}
        except Exception as e:
            logger.error("BUUCTF request %s %s failed: %s", method, path, e)
            return {"error": str(e)}

    def start_container(self, cid: int, max_retries: int = 2, retry_delay: int = 60) -> str | None:
        for attempt in range(max_retries):
            if attempt > 0:
                logger.info("Container start retry %d/%d for challenge %d", attempt + 1, max_retries, cid)
                self.destroy_container(cid)
                time.sleep(retry_delay)

            create_result = self._request(f"/plugins/ctfd-whale/challenge/{cid}/container", "POST")
            if create_result.get("error"):
                logger.warning("[%d] Container create returned error: %s", cid, create_result["error"])

            for _ in range(20):
                time.sleep(3)
                d = self._request(f"/plugins/ctfd-whale/challenge/{cid}/container")

                if d.get("error"):
                    continue

                if d.get("domain"):
                    return f"http://{d['domain']}:{d.get('http_port', 80)}"
                if d.get("lan_domain") and d.get("port"):
                    ip = d.get("ip")
                    if ip:
                        return f"http://{d['lan_domain']}.{ip}:{d['port']}"

            if attempt < max_retries - 1:
                logger.warning("Container for %d not ready, retrying in %ds", cid, retry_delay)

        return None

    def renew_container(self, cid: int) -> bool:
        """Renew (extend lifetime of) a running challenge container. Returns True on success."""
        try:
            result = self._request(f"/plugins/ctfd-whale/challenge/{cid}/container", "POST")
            if result.get("success") or result.get("domain") or result.get("lan_domain"):
                logger.info("[%d] Container renewed successfully", cid)
                return True
            logger.warning("[%d] Container renewal response: %s", cid, result)
            return False
        except Exception as e:
            logger.error("[%d] Container renewal failed: %s", cid, e)
            return False

    def destroy_container(self, cid: int) -> None:
        self._request(f"/plugins/ctfd-whale/challenge/{cid}/container", "DELETE")

    def submit_flag(self, cid: int, flag: str) -> dict:
        return self._request("/api/v1/challenges/attempt", "POST", {
            "challenge_id": cid,
            "submission": flag,
        })
