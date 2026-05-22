from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ctf_agent.web.db import configure
from ctf_agent.web.routers import challenges, facts, hints, renew, stream

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app(db_path: str | Path = "data/dashboard.db") -> FastAPI:
    configure(db_path)

    app = FastAPI(title="CTF Agent Dashboard", lifespan=lifespan)

    app.include_router(challenges.router)
    app.include_router(facts.router)
    app.include_router(hints.router)
    app.include_router(stream.router)
    app.include_router(renew.router)

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/")
    async def index():
        index_file = _STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "CTF Agent Dashboard - static files not found"}

    return app


def start_web_server(
    host: str = "127.0.0.1",
    port: int = 9090,
    db_path: str | Path = "data/dashboard.db",
) -> None:
    import uvicorn

    app = create_app(db_path)
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    logger.info("Web dashboard started at http://%s:%d", host, port)
    print(f"Web dashboard: http://{host}:{port}", flush=True)
