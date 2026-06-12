#!/usr/bin/env python3
"""
Social Queue Monitor — canonical, FAIL-LOUD reader for social.purebrain.ai queues.

Created 2026-06-12 after the "queues all 0" incident: ad-hoc probes using a stale
.env SOCIAL_API_PASSWORD got HTTP 401 and reported 0 counts instead of alarming.
This is the ONLY sanctioned way to read queue counts for reports/BOOPs.

Rules encoded here (constitutional):
  1. NEVER emit counts on auth failure. 401/403/login-failure => exit 2 + loud
     AUTH-BROKEN banner + alert file in .claude/dispatch-needed/.
  2. NEVER trust "HTTP 200 + count=0" on a status filter until the status name is
     cross-checked against the live status vocabulary from an unfiltered query.
     Unknown-status-with-zero while data exists => STATUS-DRIFT, exit 3.
  3. READ-ONLY. GET + login POST only. This tool must never PATCH/POST content,
     and must never touch the poster/ContentRouter.

Exit codes: 0 = OK report, 2 = AUTH BROKEN, 3 = STATUS DRIFT, 4 = transport error.
"""

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE = "https://social.purebrain.ai"
EMAIL = "jared@puretechnology.nyc"
# Documented queue statuses. The live vocabulary is ALWAYS re-derived from data;
# this list is only what we report counts for by default.
KNOWN_STATUSES = ["draft", "pending_approval", "scheduled", "posted", "failed", "rejected"]
# Content types the live social-api CF Worker cron EXCLUDES BY DESIGN
# (worker processScheduledPosts SQL: AND ci.content_type NOT IN (...), live
# script line ~3064, verified 2026-06-12). Overdue items of these types are
# informational, NOT a poster-death signal — they are fulfilled by the
# blog-pipeline / manual LinkedIn newsletter path, never by the cron.
CRON_EXCLUDED_TYPES = {"newsletter", "newsletter_promo", "blog"}
ALERT_DIR = PROJECT_ROOT / ".claude" / "dispatch-needed"
CTX = ssl.create_default_context()


def _load_env_password() -> str:
    pw = os.environ.get("SOCIAL_API_PASSWORD")
    if pw:
        return pw
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("SOCIAL_API_PASSWORD="):
                return line.split("=", 1)[1].strip()
    return ""


def _http(method: str, url: str, body=None, token=None):
    headers = {
        "Content-Type": "application/json",
        "Origin": BASE,
        "Accept": "application/json",
        # CF zone bans default python UA with error 1010 — never remove this.
        "User-Agent": "curl/7.81.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"error": str(e)}


def _fail_loud(kind: str, detail: str, exit_code: int):
    """Write alert file + scream on stderr. NEVER print 0 counts."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    banner = (
        f"SOCIAL QUEUE MONITOR {kind}\n"
        f"time: {ts}\n"
        f"detail: {detail}\n"
        "RULE: counts were NOT emitted. Do NOT report queues as 0/empty.\n"
        "Monitor-alive != monitor-seeing. Route to ST# for credential/vocab fix.\n"
    )
    sys.stderr.write("\n" + "=" * 64 + "\n" + banner + "=" * 64 + "\n")
    try:
        ALERT_DIR.mkdir(parents=True, exist_ok=True)
        alert = ALERT_DIR / f"{ts[:10]}-social-queue-monitor-{kind.lower().replace(' ', '-')}.md"
        alert.write_text(f"# {kind}: social queue monitor\n\n```\n{banner}```\n")
        sys.stderr.write(f"alert file: {alert}\n")
    except Exception as e:  # alert write failure must not mask the alarm
        sys.stderr.write(f"(could not write alert file: {e})\n")
    sys.exit(exit_code)


def main():
    pw = _load_env_password()
    if not pw:
        _fail_loud("AUTH BROKEN", "SOCIAL_API_PASSWORD missing from env and .env", 2)

    # --- 1. Login: any failure is LOUD, never a 0-count report -------------
    try:
        code, resp = _http("POST", f"{BASE}/api/login", {"email": EMAIL, "password": pw})
    except Exception as e:
        _fail_loud("TRANSPORT ERROR", f"login transport failure: {e}", 4)
    if code == 429:
        _fail_loud(
            "RATE LIMITED",
            f"POST /api/login HTTP 429 ({resp.get('error', '')}). Login throttled — "
            "do NOT report counts; retry after the cool-down.",
            4,
        )
    if code in (401, 403) or "token" not in resp:
        _fail_loud(
            "AUTH BROKEN",
            f"POST /api/login HTTP {code} ({resp.get('error', 'no token')}). "
            ".env SOCIAL_API_PASSWORD is stale or account changed.",
            2,
        )
    token = resp["token"]

    # --- 2. Unfiltered pull => live status vocabulary (ground truth) -------
    code, resp = _http("GET", f"{BASE}/api/content?limit=500", token=token)
    if code in (401, 403):
        _fail_loud("AUTH BROKEN", f"GET /api/content HTTP {code} after successful login", 2)
    if code != 200:
        _fail_loud("TRANSPORT ERROR", f"GET /api/content HTTP {code}", 4)
    items = resp.get("items", [])
    live_vocab = Counter(i.get("status") or "NULL" for i in items)
    total = len(items)

    # --- 3. Per-status counts with field-presence sanity -------------------
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = {}
    drift = []
    for status in KNOWN_STATUSES:
        code, resp = _http("GET", f"{BASE}/api/content?status={status}&limit=500", token=token)
        if code in (401, 403):
            _fail_loud("AUTH BROKEN", f"GET status={status} HTTP {code} mid-run", 2)
        n = len(resp.get("items", [])) if code == 200 else None
        counts[status] = n
        # Sanity: 200+0 on a status that does NOT exist in live vocab, while
        # the platform clearly has data => probable status-name drift.
        if n == 0 and total > 0 and status not in live_vocab and status not in ("failed", "rejected"):
            drift.append(status)

    # Any live status we are NOT querying (vocab drift in the other direction)
    unqueried = [s for s in live_vocab if s not in KNOWN_STATUSES]

    # --- 4. Overdue-scheduled signal ---------------------------------------
    # Split by cron eligibility (2026-06-12, ST# false-alarm hardening):
    #   overdue_eligible            -> types the cron WILL pick up = REAL alarm
    #   overdue_excluded_by_design  -> newsletter/newsletter_promo/blog = info only
    #   overdue_scheduled           -> sum of both (backward compatibility)
    overdue = [
        i for i in items
        if (i.get("status") == "scheduled") and ((i.get("scheduled_at") or "9999") <= now)
    ]
    overdue_excluded = [i for i in overdue if (i.get("content_type") or "") in CRON_EXCLUDED_TYPES]
    overdue_eligible = [i for i in overdue if (i.get("content_type") or "") not in CRON_EXCLUDED_TYPES]

    report = {
        "ts": now,
        "auth": "ok",
        "total_items": total,
        "counts": counts,
        "live_status_vocabulary": dict(live_vocab),
        "overdue_eligible": len(overdue_eligible),
        "overdue_excluded_by_design": len(overdue_excluded),
        "overdue_scheduled": len(overdue),  # = eligible + excluded (legacy sum)
        "field_present_rate": (
            round(sum(1 for i in items if i.get("status") is not None) / total, 3) if total else None
        ),
    }
    print(json.dumps(report, indent=2))

    if drift or unqueried:
        _fail_loud(
            "STATUS DRIFT",
            f"queried-but-absent-from-live-vocab={drift}; live-but-unqueried={unqueried}. "
            f"Counts above ARE valid, but vocabulary needs reconciling before any 'empty' claim.",
            3,
        )

    if total == 0:
        # Plausible but extraordinary — demand human eyes rather than silent 0.
        _fail_loud("STATUS DRIFT", "unfiltered query returned 0 items — verify platform before reporting empty", 3)


if __name__ == "__main__":
    main()
