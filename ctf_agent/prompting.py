from __future__ import annotations

from pathlib import Path


def load_template(template_path: str | Path) -> str:
    p = Path(template_path)
    return p.read_text(encoding="utf-8")


def render_template(template: str, **kwargs: str) -> str:
    return template.format(**kwargs)
