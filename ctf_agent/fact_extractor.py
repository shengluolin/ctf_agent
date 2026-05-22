from __future__ import annotations

import re

from ctf_agent.web import state

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("flag_candidate", re.compile(r"flag\{[^}]+\}", re.IGNORECASE)),
    ("vulnerability", re.compile(
        r"(?:SQL\s*injection|XSS|SSTI|LFI|RFI|SSRF|RCE|command\s*injection|"
        r"file\s*upload|deseriali[sz]ation|buffer\s*overflow|"
        r"path\s*traversal|privilege\s*escalation)",
        re.IGNORECASE,
    )),
    ("url", re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)),
    ("tool_output", re.compile(
        r"(?:nmap|sqlmap|dirsearch|gobuster|nikto|burp|hashcat|john|wfuzz|ffuf|feroxbuster).*"
        r"(?:found|discovered|open|valid|password|credential|match)",
        re.IGNORECASE,
    )),
    ("discovery", re.compile(
        r"(?:port\s+\d+/(?:tcp|udp)\s+open|password\s*[:=]\s*\S+|secret\s*[:=]\s*\S+)",
        re.IGNORECASE,
    )),
]

_MIN_LINE_LENGTH = 4


def process_chunk(challenge_id: int, text: str) -> None:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for category, pattern in _PATTERNS:
            match = pattern.search(line)
            if match:
                # Skip length check for flag candidates (flags can be short like flag{a})
                if category != "flag_candidate" and len(line) < _MIN_LINE_LENGTH:
                    continue
                state.insert_fact(challenge_id, category, match.group(0), line)
                break
