from __future__ import annotations

from ctf_agent.config import DriverConfig
from ctf_agent.drivers.base import WorkerDriver
from ctf_agent.drivers.claude_cli import ClaudeCliDriver

_DRIVERS: dict[str, type[WorkerDriver]] = {
    "claude_cli": ClaudeCliDriver,
}


def get_driver(config: DriverConfig) -> WorkerDriver:
    cls = _DRIVERS.get(config.type)
    if cls is None:
        raise ValueError(f"Unknown driver type: {config.type!r}. Available: {list(_DRIVERS)}")
    return cls(config)
