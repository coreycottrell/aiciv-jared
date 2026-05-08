#!/usr/bin/env python3
"""
bsky-session-health — daily self-healing BOOP for the @purebrain.ai session token.

Spec: .claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md (v2.5)
B7 sub-task — folded into the same BUILD as the publish-hook Worker.

Why this exists:
    The 20-day @purebrain.ai dormancy from 2026-04-12 → 2026-05-02 was caused by a
    silently-revoked Bluesky session token. Without auto-relog, this WILL recur.
    This BOOP detects ExpiredToken / InvalidToken / no-session, re-logs from .env
    credentials, and rewrites both canonical session files at perms 600.

Run daily via cron / scheduled task. Exit codes:
    0 — session healthy (or healed successfully)
    1 — session unhealthy AND heal failed (Jared must investigate)
    2 — environment misconfigured (.env missing creds, etc.)

Notification (optional):
    If TG_BOT_TOKEN + TG_CHAT_ID env vars are present, Telegram alerts on
    heal-success and heal-failure. Silent on healthy ticks.

Constitutional:
    - Reads BSKY_USERNAME / BSKY_PASSWORD from .env (CIV_ROOT/.env)
    - Writes session string to BOTH canonical paths with perms 0600
    - Never commits session contents (callers must keep these paths gitignored)
"""
import os
import sys
import json
import stat
import urllib.request
import urllib.parse
from pathlib import Path

# Resolve project root robustly: this file lives at <root>/tools/bsky-session-health/check_and_heal.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_SESSION_PATHS = [
    PROJECT_ROOT / ".claude" / "bsky_session.txt",
    PROJECT_ROOT / ".claude" / "from-jared" / "bsky" / "bsky_automation" / "bsky_session.txt",
]

ENV_FILE = PROJECT_ROOT / ".env"
HANDLE = "purebrain.ai"


def load_env():
    """Minimal .env loader (avoid a hard dependency on python-dotenv)."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    # Allow process env to override .env
    for k in ("BSKY_USERNAME", "BSKY_PASSWORD", "TG_BOT_TOKEN", "TG_CHAT_ID"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def telegram_notify(env, text):
    """Best-effort Telegram notify. Failures are swallowed (this is a notifier, not a primary)."""
    token = env.get("TG_BOT_TOKEN")
    chat_id = env.get("TG_CHAT_ID")
    if not (token and chat_id):
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(url, data=data, timeout=5).read()
    except Exception:
        pass


def write_session_string(session_str):
    """Persist session string to both canonical paths with perms 600."""
    written = []
    for p in CANONICAL_SESSION_PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(session_str)
        try:
            p.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
        except Exception:
            pass
        written.append(str(p))
    return written


def check_session():
    """
    Returns (status, detail).
        status in {"healthy", "expired", "missing", "unknown_error"}
        detail = string with extra context
    """
    try:
        from atproto import Client
    except ImportError:
        return ("unknown_error", "atproto package not installed in this environment")

    # If no session file exists at all → missing
    primary = CANONICAL_SESSION_PATHS[0]
    if not primary.exists() or primary.stat().st_size == 0:
        return ("missing", f"session file not found or empty: {primary}")

    try:
        session_str = primary.read_text().strip()
        c = Client()
        c.login(session_string=session_str)
        # Probe: getAuthorFeed for our own handle.
        c.get_author_feed(actor=HANDLE, limit=1)
        return ("healthy", "getAuthorFeed succeeded")
    except Exception as e:
        msg = str(e)
        # Recognized "needs heal" signals:
        #   - ExpiredToken / InvalidToken / "Token has been revoked"  → server rejected
        #   - "not enough values to unpack" / parse errors            → file is malformed/corrupt
        #   - "Authentication Required"                               → upstream session gone
        heal_signals = (
            "ExpiredToken", "InvalidToken", "Token has been revoked",
            "Authentication Required", "not enough values to unpack",
            "AuthMissing", "AuthFactorTokenRequired",
        )
        if any(sig in msg for sig in heal_signals):
            return ("expired", msg[:300])
        return ("unknown_error", msg[:300])


def heal(env):
    """Re-login from credentials, write fresh session file."""
    try:
        from atproto import Client
    except ImportError:
        return False, "atproto package not installed"

    user = env.get("BSKY_USERNAME")
    pw = env.get("BSKY_PASSWORD")
    if not (user and pw):
        return False, "BSKY_USERNAME / BSKY_PASSWORD missing in .env"

    try:
        c = Client()
        c.login(user, pw)
        session_str = c.export_session_string()
        # Verify the new session works before persisting (probe).
        c2 = Client()
        c2.login(session_string=session_str)
        c2.get_author_feed(actor=HANDLE, limit=1)
        written = write_session_string(session_str)
        return True, f"session refreshed; persisted to {len(written)} paths"
    except Exception as e:
        return False, f"heal failed: {str(e)[:300]}"


def main():
    env = load_env()
    status, detail = check_session()

    if status == "healthy":
        print(f"[bsky-session-health] OK — {detail}")
        sys.exit(0)

    print(f"[bsky-session-health] {status.upper()} — {detail}", file=sys.stderr)

    # Unhealthy → attempt heal
    if status in ("expired", "missing"):
        if not (env.get("BSKY_USERNAME") and env.get("BSKY_PASSWORD")):
            telegram_notify(env, f"[bsky-session-health] {status.upper()} but BSKY creds missing — manual intervention required")
            print(f"[bsky-session-health] HEAL ABORTED — credentials missing in .env", file=sys.stderr)
            sys.exit(2)
        ok, info = heal(env)
        if ok:
            print(f"[bsky-session-health] HEALED — {info}")
            telegram_notify(env, f"[bsky-session-health] AUTO-HEALED — session was {status}, regenerated successfully. {info}")
            sys.exit(0)
        else:
            print(f"[bsky-session-health] HEAL FAILED — {info}", file=sys.stderr)
            telegram_notify(env, f"[bsky-session-health] HEAL FAILED — {info}. Manual intervention required.")
            sys.exit(1)
    else:
        # unknown_error — don't auto-heal blindly. Notify and exit.
        telegram_notify(env, f"[bsky-session-health] UNKNOWN ERROR — {detail}. Investigate manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()
