"""Search public writeups for a CTF challenge and extract key hints."""
from __future__ import annotations

import logging
import re
import urllib.parse

import requests

logger = logging.getLogger(__name__)

# Global proxy setting, set by solver before searching
_proxy: str = ""

def set_proxy(proxy: str) -> None:
    """Set proxy for writeup searches."""
    global _proxy
    _proxy = proxy

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

_MAX_RESPONSE_SIZE = 512 * 1024  # 512KB limit

# Domains that should NOT use proxy (China domestic sites)
_DOMESTIC_DOMAINS = [
    "csdn.net", "blog.csdn.net", "cnblogs.com", "xz.aliyun.com",
    "freebuf.com", ".anquanke.com", "seebug.org", "paper.seebug.org"
]

def _get_proxies(url: str) -> dict:
    """Get proxy configuration for requests. Skip proxy for domestic sites."""
    if not _proxy:
        return {}
    # Check if URL is a domestic site
    for domain in _DOMESTIC_DOMAINS:
        if domain in url:
            return {}  # No proxy for domestic sites
    return {"http": _proxy, "https": _proxy}

_HTML_TAG_RE = re.compile(r"<[^>]+>")

_CODE_BLOCK_RE = re.compile(
    r"```(.*?)```|<code[^>]*>(.*?)</code>|<pre[^>]*>(.*?)</pre>",
    re.DOTALL,
)


def search_writeup(challenge_name: str, max_results: int = 3) -> list[dict]:
    """Search for writeups and return structured hints.

    Returns list of dicts with keys: title, url, hints (list of strings)
    """
    results: list[dict] = []
    seen_urls: set[str] = set()

    # Try multiple search sources
    search_functions = [
        _search_csdn,
        _search_aliyun_xz,
        _search_bing,
    ]

    for search_func in search_functions:
        if len(results) >= max_results:
            break
        try:
            found = search_func(challenge_name, seen_urls)
            for item in found:
                if len(results) >= max_results:
                    break
                hints = _extract_hints(item["url"], challenge_name)
                if hints:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item["url"],
                        "hints": hints,
                    })
                    seen_urls.add(item["url"])
        except Exception as e:
            logger.warning("Writeup search failed with %s: %s", search_func.__name__, e)

    return results


def _search_csdn(challenge_name: str, seen_urls: set[str]) -> list[dict]:
    """Search CSDN for writeups."""
    query = urllib.parse.quote(f"{challenge_name} writeup CTF")
    url = f"https://so.csdn.net/so/search?q={query}&t=blog&domain="
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        if r.status_code != 200:
            return []
    except Exception:
        return []

    items = []
    # CSDN search results are in JSON format
    try:
        data = r.json()
        for item in data.get("result", [])[:5]:
            link = item.get("url", "")
            if link in seen_urls:
                continue
            title = item.get("title", "")
            items.append({"url": link, "title": title})
    except Exception:
        pass

    return items


def _search_aliyun_xz(challenge_name: str, seen_urls: set[str]) -> list[dict]:
    """Search 先知社区 (Aliyun XZ) for writeups."""
    query = urllib.parse.quote(challenge_name)
    url = f"https://xz.aliyun.com/search?q={query}"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        if r.status_code != 200:
            return []
    except Exception:
        return []

    items = []
    # Parse HTML for search results
    for match in re.finditer(r'<a[^>]+href="(/t/[^"]+)"[^>]*>([^<]+)</a>', r.text):
        link = "https://xz.aliyun.com" + match.group(1)
        if link in seen_urls:
            continue
        title = match.group(2).strip()
        if len(title) > 5:  # Filter out short/irrelevant titles
            items.append({"url": link, "title": title})
    return items[:5]


def _search_bing(challenge_name: str, seen_urls: set[str]) -> list[dict]:
    """Search Bing for writeups (fallback)."""
    query = urllib.parse.quote(f"{challenge_name} writeup CTF")
    url = f"https://www.bing.com/search?q={query}"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10, proxies=_get_proxies(url))
        if r.status_code != 200:
            return []
    except Exception:
        return []

    items = []
    for match in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>', r.text):
        link = match.group(1)
        if link in seen_urls:
            continue
        # Skip bing.com and other irrelevant domains
        skip_domains = ["bing.com", "microsoft.com", "youtube.com", "facebook.com"]
        if any(d in link for d in skip_domains):
            continue
        title = match.group(2).strip()
        if len(title) > 5:
            items.append({"url": link, "title": title})

    return items[:5]


def _name_matches(text: str, challenge_name: str) -> bool:
    """Check if page text is about this challenge. Handles Chinese names."""
    clean = re.sub(r"[\[\]【】()（）]", "", challenge_name).strip()
    # Split on spaces, underscores, and common separators
    parts = re.split(r"[\s_]+", clean)
    parts = [p for p in parts if len(p) > 1]
    if not parts:
        # Single token — use substring match on the full cleaned name
        return clean in text if clean else True
    # At least 2 parts must match
    return sum(1 for p in parts if p in text) >= min(2, len(parts))


def _extract_hints(url: str, challenge_name: str) -> list[str]:
    """Fetch a writeup page and extract key hints."""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10, stream=True, proxies=_get_proxies(url))
        if r.status_code != 200:
            return []
        # Limit response size
        content = b""
        for chunk in r.iter_content(chunk_size=64 * 1024):
            content += chunk
            if len(content) > _MAX_RESPONSE_SIZE:
                break
        text = content.decode("utf-8", errors="replace")
    except Exception:
        return []

    # Extract code blocks BEFORE stripping HTML tags
    code_blocks = []
    for m in _CODE_BLOCK_RE.finditer(text):
        for group in m.groups():
            if group:
                group = _HTML_TAG_RE.sub("", group).strip()
                if 20 < len(group) < 500:
                    code_blocks.append(group)
    code_blocks = code_blocks[:3]

    # Now strip HTML tags for text analysis
    text = _HTML_TAG_RE.sub(" ", text)
    # Truncate for regex safety
    text = text[:200000]

    # Check relevance
    if not _name_matches(text, challenge_name):
        return []

    hints: list[str] = []

    # Extract payload-like code blocks
    for block in code_blocks:
        if any(kw in block.lower() for kw in [
            "select", "union", "system", "cat ", "flag", "eval",
            "include", "file", "exec", "shell_exec", "passthru",
        ]):
            hints.append(f"可能的payload: {block[:200]}")

    # Extract sentences with key terms
    for sent in re.split(r"[。\n\.!?]", text):
        sent = sent.strip()
        if len(sent) < 15 or len(sent) > 200:
            continue
        if any(kw in sent for kw in [
            "关键", "思路", "方法", "利用", "绕过", "bypass",
            "payload", "trick", "考点", "flag",
        ]):
            hints.append(sent[:200])

    return hints[:5]


def format_writeup_hints(results: list[dict]) -> str:
    """Format writeup search results into hint text for injection."""
    if not results:
        return ""

    lines = ["\n## 自动搜索到的 Writeup 提示（仅供参考思路，payload 可能不同）\n"]
    for r in results:
        title = r.get("title", "") or r.get("url", "")[:50]
        lines.append(f"### 来源: {title[:50]}")
        lines.append(f"URL: {r['url']}")
        for hint in r["hints"]:
            lines.append(f"- {hint}")
        lines.append("")

    return "\n".join(lines)
