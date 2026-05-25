from __future__ import annotations

import re
from dataclasses import dataclass

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)", re.DOTALL | re.MULTILINE)
FENCED_BLOCK_RE = re.compile(r"```(?:markdown|md)?\s*\n?(.*?)```", re.IGNORECASE | re.DOTALL)

# Flag regex: flag{...} where content has no newlines and is reasonably short.
# Real CTF flags are typically 20-100 chars; cap at 128 to avoid matching
# prose that happens to start with "flag{" and end with "}".
FLAG_RE = re.compile(r"flag\{[^\n}]{1,120}\}", re.IGNORECASE)

# Extract the value after "flag:" in YAML frontmatter (more precise than regex)
FLAG_YAML_RE = re.compile(r'^flag:\s*["\']?(flag\{[^\n}]+\})["\']?\s*$', re.MULTILINE)

# Patterns that look like flags but are actually placeholders in writeup templates
_PLACEHOLDER_FLAGS = {"flag{...}", "flag{xxx}", "flag{flag}", "flag{placeholder}", "flag{example}", "flag{your_flag}", "flag{here}"}

_MAX_FLAG_LEN = 128


@dataclass(slots=True)
class ParsedOutput:
    writeup: str | None
    flag: str | None
    has_frontmatter: bool


def parse_output(stdout: str, stderr: str = "") -> ParsedOutput:
    text = stdout.strip()
    if not text:
        return ParsedOutput(writeup=None, flag=_find_flag(stderr), has_frontmatter=False)

    # If stdout looks like stream-json, extract text from events first
    # Require multiple JSON lines to avoid false positives on model JSON output
    if text.startswith("{") and '"type"' in text[:100] and text.count("\n") > 1:
        text = _extract_from_stream_json(text) or text

    # Strategy 1: Extract YAML frontmatter block (search, not match — writeup may not start at beginning)
    match = FRONTMATTER_RE.search(text)
    if match:
        frontmatter = match.group(1)
        body = match.group(2).strip()
        full_writeup = f"---\n{frontmatter}\n---\n\n{body}" if body else f"---\n{frontmatter}\n---"
        flag = _find_flag_yaml(frontmatter) or _find_flag(frontmatter) or _find_flag(body) or _find_flag(stderr)
        return ParsedOutput(writeup=full_writeup, flag=flag, has_frontmatter=True)

    # Strategy 2: Look in fenced code blocks
    for block_match in FENCED_BLOCK_RE.finditer(text):
        block = block_match.group(1).strip()
        fm = FRONTMATTER_RE.match(block)
        if fm:
            frontmatter = fm.group(1)
            body = fm.group(2).strip()
            full_writeup = f"---\n{frontmatter}\n---\n\n{body}" if body else f"---\n{frontmatter}\n---"
            flag = _find_flag_yaml(frontmatter) or _find_flag(frontmatter) or _find_flag(body) or _find_flag(stderr)
            return ParsedOutput(writeup=full_writeup, flag=flag, has_frontmatter=True)

    # Strategy 3: Fallback - extract flag from anywhere
    flag = _find_flag(text) or _find_flag(stderr)
    return ParsedOutput(writeup=None, flag=flag, has_frontmatter=False)


def _extract_from_stream_json(text: str) -> str | None:
    """Extract concatenated text content from Claude CLI stream-json events."""
    import json as _json

    parts: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = _json.loads(line)
        except _json.JSONDecodeError:
            continue

        event_type = event.get("type", "")

        if event_type == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                t = delta.get("text", "")
                if t:
                    parts.append(t)

        elif event_type == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    parts.append(block["text"])

        elif event_type == "result":
            result_text = event.get("result", "")
            if result_text:
                parts.append(result_text)

    return "".join(parts) if parts else None


def _find_flag_yaml(text: str) -> str | None:
    """Extract flag from a YAML 'flag:' line (most reliable source)."""
    if not text:
        return None
    for match in FLAG_YAML_RE.finditer(text):
        candidate = match.group(1)
        if candidate.lower() not in _PLACEHOLDER_FLAGS and len(candidate) <= _MAX_FLAG_LEN:
            return candidate
    return None


def _find_flag(text: str) -> str | None:
    if not text:
        return None
    for match in FLAG_RE.finditer(text):
        candidate = match.group(0)
        if candidate.lower() not in _PLACEHOLDER_FLAGS and len(candidate) <= _MAX_FLAG_LEN:
            return candidate
    return None
