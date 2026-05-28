from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

from ctf_agent.buuctf import BuuctfClient
from ctf_agent.config import AppConfig
from ctf_agent.drivers import get_driver
from ctf_agent.models import Challenge, SolveStatus
from ctf_agent.progress import ProgressTracker
from ctf_agent.prompting import load_template
from ctf_agent.solver import solve_challenge
from ctf_agent.web.app import start_web_server
from ctf_agent.web import state as web_state
from ctf_agent.web.routers import renew, challenges

logger = logging.getLogger(__name__)

_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    if _shutdown:
        logger.warning("Force exit (second signal)")
        sys.exit(1)
    _shutdown = True
    logger.warning("Shutdown requested (Ctrl+C again to force)")


def _find_project_root() -> Path:
    """Walk up from this file to find the directory containing challenge_list.py."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "scripts" / "challenge_list.py").exists():
            return parent
    return current


def _add_challenge(cid: int, name: str, project_root: Path) -> bool:
    """Add a new challenge to the challenge list."""
    import sys
    sys.path.insert(0, str(project_root / "scripts"))
    from challenge_list import CHALLENGE_LIST

    # Check if already exists
    for existing_id, existing_name in CHALLENGE_LIST:
        if existing_id == cid:
            logger.warning("Challenge %d already in list: %s", cid, existing_name)
            return False

    # Read the file
    list_path = project_root / "scripts" / "challenge_list.py"
    with open(list_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the line with the closing bracket
    new_entry = f"    ({cid}, \"{name}\"),\n"
    new_lines = []
    inserted = False

    for line in lines:
        if line.strip() == "]" and not inserted:
            # Insert new entry before the closing bracket
            new_lines.append(new_entry)
            inserted = True
        new_lines.append(line)

    if not inserted:
        # Fallback: append before last line
        new_lines.insert(-1, new_entry)

    # Write back
    with open(list_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Also update the in-memory list
    CHALLENGE_LIST.append((cid, name))

    logger.info("Added challenge %d: %s", cid, name)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="CTF Agent - Automated CTF solver")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--skip-solved", action="store_true", help="Skip challenges with existing writeups")
    parser.add_argument("--one", action="store_true", help="Solve only one challenge then exit")
    parser.add_argument("--add", metavar="ID", type=int, help="Add a challenge to the list by ID (fetches info from BUUCTF)")
    parser.add_argument("--add-name", metavar="NAME", type=str, help="Challenge name (use with --add to override)")
    parser.add_argument("challenge_id", nargs="?", type=int, help="Solve only this challenge ID")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error("Config not found: %s", config_path)
        sys.exit(1)
    config = AppConfig.load(config_path)

    # Resolve paths relative to project root
    project_root = _find_project_root()
    config.paths.base_dir = str(project_root)

    # Load challenge list
    sys.path.insert(0, str(project_root / "scripts"))
    from challenge_list import CHALLENGE_LIST

    # Create client
    client = BuuctfClient(config.buuctf)

    # Wire client into renewal API and challenges API
    renew.set_client(client)
    challenges.set_buuctf_client(client)

    # Handle --add: add new challenge and optionally run it
    if args.add:
        cid = args.add
        if args.add_name:
            name = args.add_name
        else:
            # Fetch challenge info from BUUCTF
            info = client.get_challenge_info(cid)
            if info:
                name = info.get("name", f"Challenge {cid}")
                print(f"Found challenge: {cid} - {name}", flush=True)
            else:
                logger.error("Failed to fetch challenge %d info from BUUCTF", cid)
                logger.info("Use --add-name to provide a name manually")
                sys.exit(1)

        added = _add_challenge(cid, name, project_root)
        if added:
            print(f"Added [{cid}] {name} to challenge list", flush=True)
        else:
            print(f"Challenge {cid} already in list", flush=True)

        # If also running, continue to solve
        if not args.challenge_id and not args.one:
            sys.exit(0)

    # Create progress tracker
    tracker = ProgressTracker(config.paths.resolve_progress())

    # Load template
    template_path = project_root / "templates" / "solve.md"
    if not template_path.exists():
        logger.error("Template not found: %s", template_path)
        sys.exit(1)
    template = load_template(template_path)

    # Ensure host directories exist
    challenges_dir = config.paths.resolve_challenges()
    wps_dir = config.paths.resolve_wps()
    logs_dir = config.paths.resolve_logs()
    challenges_dir.mkdir(parents=True, exist_ok=True)
    wps_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Create driver, mount host dirs, start worker container
    driver = get_driver(config.driver)
    driver.mount(str(challenges_dir), "challenges")
    driver.mount(str(wps_dir), "wps")
    driver.mount(str(logs_dir), "logs")
    # Mount skills into container
    skills_dir = project_root / ".claude"
    if skills_dir.exists():
        driver.mount(str(skills_dir), ".claude")
    print(f"Starting Docker worker container...", flush=True)
    driver.ensure_running()
    print(f"Worker container ready (image: {config.driver.docker_image})", flush=True)

    # Start web dashboard
    db_path = Path(config.paths.base_dir) / "data" / "dashboard.db"
    start_web_server(
        host=config.web.host,
        port=config.web.port,
        db_path=str(db_path),
    )

    print(f"=== CTF Agent (Claude Code) ===", flush=True)
    print(f"Challenges: {len(CHALLENGE_LIST)}", flush=True)
    print(f"Config: {config_path}", flush=True)
    print(f"Timeout: easy={config.driver.timeout_easy}s, medium={config.driver.timeout_medium}s, hard={config.driver.timeout_hard}s", flush=True)

    results: list[tuple[int, str, SolveStatus]] = []

    # Tier boundaries based on challenge list ordering
    # First ~20 are easy/gift, next ~20 beginner, rest medium/hard
    EASY_THRESHOLD = 19  # first 19 challenges
    MEDIUM_THRESHOLD = 60  # next ~40 challenges

    for idx, (cid, name) in enumerate(CHALLENGE_LIST):
        if args.challenge_id and cid != args.challenge_id:
            continue

        # Calculate timeout based on challenge position (difficulty proxy)
        if idx < EASY_THRESHOLD:
            challenge_timeout = config.driver.timeout_easy
        elif idx < MEDIUM_THRESHOLD:
            challenge_timeout = config.driver.timeout_medium
        else:
            challenge_timeout = config.driver.timeout_hard

        challenge = Challenge(
            id=cid,
            name=name,
            base_challenges=config.paths.resolve_challenges(),
            base_wps=config.paths.resolve_wps(),
            base_logs=config.paths.resolve_logs(),
        )

        print(f"\n{'='*50}", flush=True)
        print(f"[{cid}] {name}", flush=True)

        if _shutdown:
            logger.warning("Skipping remaining challenges (shutdown requested)")
            break

        # Skip solved
        if args.skip_solved:
            if tracker.is_solved(cid) or challenge.writeup_path.exists():
                print(f"  SKIP: Already solved", flush=True)
                results.append((cid, name, SolveStatus.SOLVED))
                continue

        web_state.notify_challenge_start(cid, name)

        # Solve
        result = solve_challenge(challenge, config, client, driver, template, timeout_override=challenge_timeout)
        tracker.record(cid, result.status)
        web_state.notify_challenge_done(cid, result.status.value, result.flag, result.error_message)

        status_icon = {
            SolveStatus.SOLVED: "OK",
            SolveStatus.TIMEOUT: "TIMEOUT",
            SolveStatus.FAILED: "FAIL",
            SolveStatus.ERROR: "ERROR",
        }.get(result.status, "???")

        print(f"  [{status_icon}] {result.status.value} ({result.duration_seconds:.0f}s)", flush=True)
        if result.flag:
            print(f"  Flag: {result.flag}", flush=True)
        if result.error_message:
            print(f"  Error: {result.error_message}", flush=True)

        results.append((cid, name, result.status))

        # Exit after one challenge if --one flag is set
        if args.one:
            logger.info("Exiting after one challenge (--one flag)")
            break

        # Interruptible inter-challenge delay
        for _ in range(config.retry.inter_challenge_delay):
            if _shutdown:
                break
            time.sleep(1)

    # Summary
    print(f"\n{'='*50}", flush=True)
    solved = sum(1 for _, _, s in results if s == SolveStatus.SOLVED)
    print(f"Done! {solved}/{len(results)} solved", flush=True)

    for cid, name, status in results:
        icon = "OK" if status == SolveStatus.SOLVED else ".."
        print(f"  [{icon}] [{cid}] {name} - {status.value}", flush=True)

    stats = tracker.get_stats()
    if stats:
        print(f"\nAll-time stats: {stats}", flush=True)

    # Cleanup worker container
    print(f"\nCleaning up worker container...", flush=True)
    driver.cleanup()


if __name__ == "__main__":
    main()
