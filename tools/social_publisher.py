#!/usr/bin/env python3
"""
Social Publisher Service
========================

Long-running poller that fires scheduled LinkedIn posts through the
`/api/linkedin/post-with-image` Worker endpoint on apex.purebrain.ai.

Wave 1b of the LinkedIn API build (BUILD -> SECURITY -> QA -> SHIP).

Behavior
--------
- Polls `https://surf.purebrain.ai/social/scheduled` every 60 seconds
- For each post where:
    auto_publish == True
    status == "approved"
    scheduled_time <= now() UTC
    linkedin_post_url is empty/null
  fires a POST to apex Worker endpoint with X-Internal-Auth header.
- On success: PATCH back with published status + linkedin_post_url.
- On failure: log + Telegram alert; does NOT mark published; next cycle retries.

Safety Features
---------------
1. Idempotency - skip posts that already have linkedin_post_url
2. Rate limit - max 5 posts/hour (tracked in state file)
3. Kill switch - presence of .social_publisher_disabled pauses cycles
4. Dry run - --dry-run flag logs POSTs without firing them
5. Rotating logs - 10MB, 5 backups at logs/social_publisher.log
6. Secret via dotenv - INTERNAL_AUTH_TOKEN never hardcoded
7. Graceful SIGTERM/SIGINT handling
8. Per-post try/except so one failure never kills the loop

State File Schema
-----------------
Path: /home/jared/projects/AI-CIV/aether/.social_publisher_state.json

{
    "published_timestamps": [
        "2026-04-08T14:23:01+00:00",
        "2026-04-08T14:45:12+00:00"
    ],
    "last_cycle": "2026-04-08T14:50:00+00:00",
    "total_published": 42,
    "total_failures": 3
}

`published_timestamps` is a rolling window pruned to the last 60 minutes on
every check. Rate limit = len(published_timestamps) < 5.

CLI
---
    python3 tools/social_publisher.py              # normal long-running mode
    python3 tools/social_publisher.py --dry-run    # simulate only, no POSTs
    python3 tools/social_publisher.py --once       # single cycle then exit
    python3 tools/social_publisher.py --post-id X  # target a specific post id

Author: full-stack-developer (Aether collective)
Date: 2026-04-08
"""

from __future__ import annotations

import argparse
import json
import logging
import logging.handlers
import os
import signal
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Constants                                                                    #
# --------------------------------------------------------------------------- #

PROJECT_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_PATH = PROJECT_ROOT / ".env"
LOG_PATH = PROJECT_ROOT / "logs" / "social_publisher.log"
STATE_PATH = PROJECT_ROOT / ".social_publisher_state.json"
KILL_SWITCH_PATH = PROJECT_ROOT / ".social_publisher_disabled"
TELEGRAM_CONFIG_PATH = PROJECT_ROOT / "config" / "telegram_config.json"
TELEGRAM_CHAT_ID = "548906264"

SCHEDULE_URL = "https://surf.purebrain.ai/social/scheduled"
WORKER_URL = "https://apex.purebrain.ai/api/linkedin/post-with-image"

POLL_INTERVAL_SECONDS = 60
RATE_LIMIT_MAX_POSTS_PER_HOUR = 5
REQUEST_TIMEOUT = 30

# --------------------------------------------------------------------------- #
# Globals                                                                      #
# --------------------------------------------------------------------------- #

load_dotenv(ENV_PATH)
INTERNAL_AUTH_TOKEN = os.environ.get("INTERNAL_AUTH_TOKEN", "")

_shutdown_requested = False


def _handle_signal(signum: int, _frame: Any) -> None:
    """Flag shutdown; current cycle will finish then main loop exits."""
    global _shutdown_requested
    _shutdown_requested = True
    logging.getLogger("social_publisher").warning(
        "Shutdown signal received (%s). Will exit after current cycle.", signum
    )


# --------------------------------------------------------------------------- #
# Logging                                                                      #
# --------------------------------------------------------------------------- #


def setup_logging() -> logging.Logger:
    """Configure rotating file handler + stdout for systemd."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("social_publisher")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_PATH, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    logger.addHandler(stdout_handler)

    return logger


# --------------------------------------------------------------------------- #
# Telegram alert                                                               #
# --------------------------------------------------------------------------- #


def telegram_alert(msg: str) -> None:
    """Best-effort Telegram alert. Never raises."""
    try:
        with open(TELEGRAM_CONFIG_PATH) as f:
            token = json.load(f)["bot_token"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        # Never let telegram failures break the loop.
        pass


# --------------------------------------------------------------------------- #
# State management                                                             #
# --------------------------------------------------------------------------- #


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {
            "published_timestamps": [],
            "last_cycle": None,
            "total_published": 0,
            "total_failures": 0,
        }
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {
            "published_timestamps": [],
            "last_cycle": None,
            "total_published": 0,
            "total_failures": 0,
        }


def save_state(state: dict) -> None:
    try:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2, default=str)
    except Exception as e:
        logging.getLogger("social_publisher").error("Failed to save state: %s", e)


def prune_rate_window(state: dict) -> None:
    """Remove published_timestamps older than 60 minutes."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    fresh: list[str] = []
    for ts in state.get("published_timestamps", []):
        try:
            parsed = datetime.fromisoformat(ts)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            if parsed >= cutoff:
                fresh.append(ts)
        except Exception:
            continue
    state["published_timestamps"] = fresh


def under_rate_limit(state: dict) -> bool:
    prune_rate_window(state)
    return len(state["published_timestamps"]) < RATE_LIMIT_MAX_POSTS_PER_HOUR


# --------------------------------------------------------------------------- #
# Fetching and filtering scheduled posts                                       #
# --------------------------------------------------------------------------- #


def fetch_scheduled() -> list[dict]:
    """Return the list of scheduled posts from surf.purebrain.ai."""
    log = logging.getLogger("social_publisher")
    try:
        resp = requests.get(SCHEDULE_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Accept either a bare list or {"posts": [...]}.
        if isinstance(data, dict) and "posts" in data:
            return data["posts"]
        if isinstance(data, list):
            return data
        log.warning("Unexpected schedule payload shape: %s", type(data).__name__)
        return []
    except requests.RequestException as e:
        log.warning("Schedule fetch failed (will retry next cycle): %s", e)
        return []
    except Exception as e:
        log.error("Unexpected schedule fetch error: %s", e)
        return []


def is_due(post: dict) -> bool:
    """Decide whether a post is eligible to publish right now."""
    if not post.get("auto_publish"):
        return False
    if post.get("status") != "approved":
        return False
    if post.get("linkedin_post_url"):
        # Idempotency guard (belt + suspenders).
        return False

    scheduled_time = post.get("scheduled_time") or post.get("scheduled_at")
    if not scheduled_time:
        return False
    try:
        parsed = datetime.fromisoformat(str(scheduled_time).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return False
    return parsed <= datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Publishing                                                                   #
# --------------------------------------------------------------------------- #


def fire_post(post: dict, dry_run: bool) -> tuple[bool, str | None, str | None]:
    """
    POST the payload to the apex Worker.

    Returns (ok, linkedin_post_url, error_message)
    """
    log = logging.getLogger("social_publisher")
    post_id = post.get("id") or post.get("post_id") or "<unknown>"

    payload = {
        "text": post.get("content") or post.get("text") or "",
        "image_url": post.get("banner_url") or post.get("image_url"),
    }

    if dry_run:
        log.info(
            "DRY-RUN | post_id=%s | would POST %s | payload_keys=%s",
            post_id,
            WORKER_URL,
            sorted(payload.keys()),
        )
        return True, "https://linkedin.com/posts/dry-run", None

    if not INTERNAL_AUTH_TOKEN:
        return False, None, "INTERNAL_AUTH_TOKEN not set in .env"

    try:
        resp = requests.post(
            WORKER_URL,
            headers={
                "X-Internal-Auth": INTERNAL_AUTH_TOKEN,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as e:
        return False, None, f"network error: {e}"

    if resp.status_code >= 400:
        # Truncate body so no secrets leak into logs.
        body = (resp.text or "")[:200]
        return False, None, f"HTTP {resp.status_code}: {body}"

    try:
        data = resp.json()
    except Exception:
        return False, None, "worker returned non-JSON response"

    linkedin_url = data.get("linkedin_post_url") or data.get("post_url") or data.get("url")
    if not linkedin_url:
        return False, None, f"worker response missing linkedin_post_url: {data}"

    return True, linkedin_url, None


def mark_published(post: dict, linkedin_url: str, dry_run: bool) -> bool:
    """PATCH the schedule endpoint with published state."""
    log = logging.getLogger("social_publisher")
    post_id = post.get("id") or post.get("post_id")
    if not post_id:
        log.error("Cannot mark published - post has no id")
        return False

    update_url = f"{SCHEDULE_URL}/{post_id}"
    body = {
        "status": "published",
        "publish_status": "published",
        "linkedin_post_url": linkedin_url,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        log.info("DRY-RUN | post_id=%s | would PATCH %s", post_id, update_url)
        return True

    try:
        resp = requests.patch(update_url, json=body, timeout=REQUEST_TIMEOUT)
        if resp.status_code >= 400:
            # Fallback to PUT.
            resp = requests.put(update_url, json=body, timeout=REQUEST_TIMEOUT)
        if resp.status_code >= 400:
            log.error(
                "Failed to mark post_id=%s published: HTTP %s",
                post_id,
                resp.status_code,
            )
            return False
        return True
    except requests.RequestException as e:
        log.error("PATCH/PUT failed for post_id=%s: %s", post_id, e)
        return False


# --------------------------------------------------------------------------- #
# Cycle                                                                        #
# --------------------------------------------------------------------------- #


def run_cycle(state: dict, dry_run: bool, target_post_id: str | None = None) -> None:
    log = logging.getLogger("social_publisher")

    # Kill switch check
    if KILL_SWITCH_PATH.exists():
        log.warning("KILL SWITCH active (%s) - skipping cycle", KILL_SWITCH_PATH.name)
        state["last_cycle"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    posts = fetch_scheduled()
    log.info("Cycle start | fetched=%d posts | dry_run=%s", len(posts), dry_run)

    due_posts = []
    for p in posts:
        try:
            if target_post_id is not None:
                pid = str(p.get("id") or p.get("post_id") or "")
                if pid != str(target_post_id):
                    continue
                # --post-id bypasses is_due() for debugging (still respects idempotency).
                if p.get("linkedin_post_url"):
                    log.info("post_id=%s already has linkedin_post_url - skip", pid)
                    continue
                due_posts.append(p)
            elif is_due(p):
                due_posts.append(p)
        except Exception as e:
            log.error("Error evaluating post for due-ness: %s", e)

    log.info("Due posts: %d", len(due_posts))

    for post in due_posts:
        if _shutdown_requested:
            log.warning("Shutdown requested - aborting remaining posts in cycle")
            break

        post_id = post.get("id") or post.get("post_id") or "<unknown>"

        # Rate limit check (per post, since limit can fill mid-cycle).
        if not under_rate_limit(state):
            log.warning(
                "Rate limit hit (%d in last hour) - deferring post_id=%s",
                RATE_LIMIT_MAX_POSTS_PER_HOUR,
                post_id,
            )
            break

        try:
            ok, linkedin_url, err = fire_post(post, dry_run=dry_run)
            if not ok:
                log.error("FIRE FAIL | post_id=%s | error=%s", post_id, err)
                state["total_failures"] = state.get("total_failures", 0) + 1
                telegram_alert(
                    f"social_publisher: FAIL post_id={post_id} err={err}"
                )
                continue

            log.info("FIRE OK   | post_id=%s | url=%s", post_id, linkedin_url)

            if mark_published(post, linkedin_url, dry_run=dry_run):
                log.info("MARKED    | post_id=%s | status=published", post_id)
                state["published_timestamps"].append(
                    datetime.now(timezone.utc).isoformat()
                )
                state["total_published"] = state.get("total_published", 0) + 1
            else:
                log.error(
                    "MARK FAIL | post_id=%s | posted OK but could not update schedule",
                    post_id,
                )
                telegram_alert(
                    f"social_publisher: posted OK but mark-published FAILED "
                    f"post_id={post_id} url={linkedin_url}"
                )
        except Exception as e:
            log.exception("Unhandled error processing post_id=%s: %s", post_id, e)
            state["total_failures"] = state.get("total_failures", 0) + 1
            # Error isolation - loop continues.

    state["last_cycle"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    log.info("Cycle end | state saved")


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Social Publisher - fires scheduled LinkedIn posts via apex Worker."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log intended POST/PATCH calls without firing them.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle and exit (cron/debug).",
    )
    parser.add_argument(
        "--post-id",
        default=None,
        help="Target a specific post id (debug). Implies --once.",
    )
    args = parser.parse_args()

    log = setup_logging()
    log.info(
        "social_publisher starting | dry_run=%s | once=%s | post_id=%s",
        args.dry_run,
        args.once,
        args.post_id,
    )
    log.info("log_path=%s state_path=%s", LOG_PATH, STATE_PATH)
    if not INTERNAL_AUTH_TOKEN and not args.dry_run:
        log.error("INTERNAL_AUTH_TOKEN missing from .env - refusing to run live")
        telegram_alert("social_publisher: INTERNAL_AUTH_TOKEN missing - aborted")
        return 2

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    state = load_state()
    single_shot = args.once or (args.post_id is not None)

    if single_shot:
        run_cycle(state, dry_run=args.dry_run, target_post_id=args.post_id)
        log.info("Single-cycle run complete - exiting")
        return 0

    while not _shutdown_requested:
        try:
            run_cycle(state, dry_run=args.dry_run)
        except Exception as e:
            log.exception("Top-level cycle error: %s", e)
            telegram_alert(f"social_publisher: cycle crashed: {e}")

        # Sleep in small slices so shutdown signal is responsive.
        slept = 0
        while slept < POLL_INTERVAL_SECONDS and not _shutdown_requested:
            time.sleep(1)
            slept += 1

    log.info("social_publisher exited cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
