from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class BuuctfConfig(BaseModel):
    base_url: str = "https://buuoj.cn"
    cookie: str
    csrf_token: str


class DriverConfig(BaseModel):
    type: str = "claude_cli"
    timeout: int = 3600
    timeout_easy: int = 1200  # 20 min for easy/gift challenges
    timeout_medium: int = 2700  # 45 min for medium challenges
    timeout_hard: int = 3600  # 60 min for hard challenges
    allowed_tools: list[str] = ["Bash"]
    docker_image: str = "kali-ctf:latest"
    api_key: str = ""
    api_base_url: str = ""
    model: str = ""


class RetryConfig(BaseModel):
    max_container_retries: int = 2
    container_retry_delay: int = 60
    inter_challenge_delay: int = 60
    writeup_search_delay: int = 300  # seconds before auto-searching writeups (default 5 min)
    proxy: str = ""  # e.g., "http://127.0.0.1:10808"


class PathsConfig(BaseModel):
    base_dir: str = "."
    challenges_dir: str = "challenges"
    wps_dir: str = "wps"
    logs_dir: str = "logs"
    progress_file: str = "progress.json"

    def resolve_base(self) -> Path:
        return Path(self.base_dir).resolve()

    def resolve_challenges(self) -> Path:
        return self.resolve_base() / self.challenges_dir

    def resolve_wps(self) -> Path:
        return self.resolve_base() / self.wps_dir

    def resolve_logs(self) -> Path:
        return self.resolve_base() / self.logs_dir

    def resolve_progress(self) -> Path:
        return self.resolve_base() / self.progress_file


class WebConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 9090


class AppConfig(BaseModel):
    buuctf: BuuctfConfig
    driver: DriverConfig = DriverConfig()
    retry: RetryConfig = RetryConfig()
    paths: PathsConfig = PathsConfig()
    web: WebConfig = WebConfig()

    @classmethod
    def load(cls, path: str | Path) -> AppConfig:
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return cls.model_validate(data)
