from __future__ import annotations

from ctf_agent.web.db import get_conn


def notify_challenge_start(cid: int, name: str) -> None:
    with get_conn() as conn:
        # Stale cleanup: mark any leftover "solving" challenges as error
        # (happens when previous run crashed/timed out without calling notify_challenge_done)
        conn.execute("""
            UPDATE challenges SET
                status = 'error',
                error_message = 'interrupted (stale solving state)',
                finished_at = datetime('now')
            WHERE status = 'solving' AND id != ?
        """, (cid,))
        # Clear old stdout and facts from previous attempts
        conn.execute("DELETE FROM stdout_log WHERE challenge_id = ?", (cid,))
        conn.execute("DELETE FROM facts WHERE challenge_id = ?", (cid,))
        # Reset hint usage so hints can be re-injected on retry
        conn.execute(
            "UPDATE hints SET used_in_attempt = NULL WHERE challenge_id = ?", (cid,)
        )
        conn.execute("""
            INSERT INTO challenges (id, name, status, started_at)
            VALUES (?, ?, 'solving', datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                status = 'solving',
                started_at = datetime('now'),
                finished_at = NULL,
                flag = NULL,
                error_message = NULL,
                duration_seconds = 0,
                attempt_count = attempt_count + 1
        """, (cid, name))


def notify_challenge_done(
    cid: int,
    status: str,
    flag: str | None,
    error: str | None,
) -> None:
    with get_conn() as conn:
        conn.execute("""
            UPDATE challenges SET
                status = ?,
                flag = ?,
                error_message = ?,
                finished_at = datetime('now'),
                duration_seconds = CASE
                    WHEN started_at IS NOT NULL
                    THEN (julianday('now') - julianday(started_at)) * 86400
                    ELSE 0
                END
            WHERE id = ?
        """, (status, flag, error, cid))


def append_stdout_line(cid: int, line: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO stdout_log (challenge_id, text) VALUES (?, ?)",
            (cid, line),
        )
        conn.execute("""
            DELETE FROM stdout_log
            WHERE challenge_id = ? AND id <= (
                SELECT MAX(id) - 2000 FROM stdout_log WHERE challenge_id = ?
            )
        """, (cid, cid))


def append_stdout(cid: int, text: str) -> None:
    with get_conn() as conn:
        for line in text.splitlines():
            conn.execute(
                "INSERT INTO stdout_log (challenge_id, text) VALUES (?, ?)",
                (cid, line),
            )
        conn.execute("""
            DELETE FROM stdout_log
            WHERE challenge_id = ? AND id <= (
                SELECT MAX(id) - 2000 FROM stdout_log WHERE challenge_id = ?
            )
        """, (cid, cid))


def insert_fact(
    cid: int,
    category: str,
    content: str,
    raw_line: str | None = None,
) -> None:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT 1 FROM facts WHERE challenge_id = ? AND content = ?",
            (cid, content),
        ).fetchone()
        if existing:
            return
        conn.execute(
            "INSERT INTO facts (challenge_id, category, content, raw_line) VALUES (?, ?, ?, ?)",
            (cid, category, content, raw_line),
        )


def get_pending_hints(cid: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, content FROM hints WHERE challenge_id = ? AND used_in_attempt IS NULL ORDER BY created_at",
            (cid,),
        ).fetchall()
        return [dict(r) for r in rows]


def mark_hints_used(hint_ids: list[int], attempt: int) -> None:
    if not hint_ids:
        return
    with get_conn() as conn:
        placeholders = ",".join("?" * len(hint_ids))
        conn.execute(
            f"UPDATE hints SET used_in_attempt = ? WHERE id IN ({placeholders})",
            (attempt, *hint_ids),
        )
