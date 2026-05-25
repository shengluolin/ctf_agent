# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

CTF Agent is an automated CTF challenge solver that runs Claude Code inside a Kali Docker container to solve BUUCTF challenges. The orchestrator manages container lifecycles, streams Claude's output in real-time, and tracks progress via a web dashboard.

## Running the Agent

```bash
# Run all challenges (ordered by difficulty)
python -m ctf_agent --config config.yaml

# Run a specific challenge by ID
python -m ctf_agent --config config.yaml --challenge 703

# Skip already-solved challenges
python -m ctf_agent --config config.yaml --skip-solved
```

Configuration lives in `config.yaml` (BUUCTF credentials, Docker driver settings, timeouts). There are no tests in this project.

## Architecture

```
Entry: ctf_agent/__main__.py → runner.main()
         │
         ├─ runner.py          Orchestrates challenge loop, Docker setup, web dashboard
         ├─ solver.py          Core solve logic per challenge (container lifecycle, Claude execution)
         ├─ buuctf.py          BUUCTF API client (CSRF, container start/renew/destroy, flag submit)
         ├─ config.py          Pydantic config models loaded from config.yaml
         ├─ models.py          Challenge, SolveResult, ProgressEntry dataclasses
         ├─ output_parser.py   Extracts writeups/flags from Claude's stream-json output
         ├─ progress.py        JSON-based solve tracking (progress.json)
         ├─ fact_extractor.py  Real-time URL/vuln/tool extraction from stdout → SQLite
         ├─ writeup_search.py  Auto-searches public writeups at 25min if unsolved
         │
         ├─ drivers/
         │   ├─ base.py        Abstract WorkerDriver interface
         │   └─ claude_cli.py  Docker-based driver (runs Claude CLI in kali-ctf container)
         │
         └─ web/
             ├─ app.py         FastAPI app with routers
             ├─ db.py          SQLite config (dashboard.db)
             ├─ state.py       Database operations for challenges, stdout, facts, hints
             └─ routers/       API endpoints for the web dashboard
```

### Challenge Lifecycle

1. `runner` selects next challenge from `scripts/challenge_list.py`
2. `solver.solve_challenge()` starts a BUUCTF container via `buuctf.py`
3. Prompt rendered from `templates/solve.md` with challenge info + container paths
4. `ClaudeCliDriver` runs Claude Code CLI inside Kali Docker container
5. Output streamed and parsed in real-time (`_StreamParser`, `fact_extractor`)
6. Background threads: container renewal at 50min, writeup search at 25min
7. Flag extracted → submitted via BUUCTF API → writeup saved to `wps/`

### Key Patterns

- **Driver pattern**: `drivers/base.py` defines abstract `WorkerDriver`; `claude_cli.py` implements Docker-based execution with volume mounting and API key injection
- **Adaptive timeouts**: `DriverConfig` has separate timeouts for easy (20min), medium (45min), hard (60min) challenges
- **Hint injection**: Web dashboard can write hint files to the challenge directory; the solver's prompt template instructs Claude to check for them periodically
- **Container renewal**: Signal file `.container_renew_ask` appears when the 1-hour BUUCTF container nears expiry

## Key Directories

- `challenges/` — Per-challenge data (source downloads, exploit scripts). Naming: `{id}_{name}`
- `wps/` — Generated writeups in YAML frontmatter + Markdown format
- `.claude/skills/` — CTF skill documentation (web, crypto, pwn, reverse, forensics, misc, osint, malware, ai-ml) with detailed attack technique references
- `templates/solve.md` — The prompt template injected into each Claude Code session

## Important Files

- `scripts/challenge_list.py` — Ordered list of 60+ BUUCTF challenges (the solve queue)
- `progress.json` — Persistent solve state (attempts, timestamps, status)
- `data/dashboard.db` — SQLite database for the web dashboard

## Dependencies

- Python 3.10+, pydantic, pyyaml, fastapi, uvicorn, requests, docker (Python SDK)
- No `requirements.txt` — dependencies installed in the Docker image
