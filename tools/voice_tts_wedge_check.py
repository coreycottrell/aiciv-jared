#!/usr/bin/env python3
"""
voice_tts_wedge_check.py — CORRECT wedge detection for the voice.purebrain.ai TTS GPU box.

WHY THIS EXISTS (read before changing thresholds):
---------------------------------------------------
On 2026-06-15 a 5-round "whack-a-mole" burned a full day. The recurring "TTS box is
WEDGED" alarm was a MONITORING-THRESHOLD BUG, not a real outage. The voice box behind
https://voice.purebrain.ai (Hetzner tunnel 37.27.237.109:8950 -> Vast.ai single-GPU
instance) is a SLOW SERIAL worker: it processes ONE ~1000-char chunk every 490-826s
(8-14 minutes), no concurrency. So `jobs_processing:1` for 8-14 minutes is NORMAL.

Prior ad-hoc checks alarmed whenever a job sat `processing` for more than ~372s or 600s —
BELOW the box's real per-job time. Every legitimate generation job therefore looked
"stuck" -> false alarm -> escalation -> stacked retries that lengthened the serial queue
and made the apparent wedge WORSE (self-inflicted feedback loop).

Hard evidence from that day (one continuous /tts/jobs list): jobs completed at
491s, 502s, 539s, 571s, 826s with valid mp3 output. The "wedged >372s" job (861e2aec)
actually completed at 826s -> 352KB valid MPEG. Nothing was wedged.

THE CORRECT WEDGE DEFINITION (this module):
-------------------------------------------
A REAL wedge = the QUEUE-HEAD job (oldest processing/queued job by created_at) has NOT
advanced across the box's real max-job-time window. We poll /tts/jobs twice, ~MAX_JOB_TIME
apart, and only declare WEDGE if ALL of the following hold across the window:
  - the same job_id is STILL the head, AND
  - it is STILL status=processing, AND
  - its created_at is unchanged (same job, not a re-submit), AND
  - the window we waited >= MAX_JOB_TIME (so the box had a full per-job window to advance).
If the head job_id changed, any job moved to done, or the queue drained -> HEALTHY
(serial progress is happening).

Secondary liveness: if jobs are queued/processing but the newest `done` job's completed_at
is older than ~2 * MAX_JOB_TIME, alarm (nothing is completing AT ALL).

NEVER alarm on:
  - raw jobs_processing COUNT (1 is normal)
  - a single job's processing duration under MAX_JOB_TIME (8-14 min is expected)

IDLE NOTE (false-green): /health 0/0 with jobs:[] reads as HEALTHY-IDLE / UNKNOWN here,
NOT "recovered". Real readiness requires a real generation job to complete end-to-end.
That gate is owned by the driver/QA (blog_audio_chatterbox.py + a real chunk), NOT by this
passive monitor. This module reports idle as HEALTHY_IDLE and says so explicitly.

ENV OVERRIDES:
  VOICE_TTS_URL          (default https://voice.purebrain.ai)
  VOICE_TTS_API_KEY      (default purebrain-tts-2026; only needed for authed endpoints)
  VOICE_MAX_JOB_TIME     (default 900; per-chunk ceiling in seconds, > observed 826s max)
  VOICE_WEDGE_POLL_GAP   (default = VOICE_MAX_JOB_TIME; seconds between the two /tts/jobs polls)

USAGE:
  # Two-poll wedge check (waits ~MAX_JOB_TIME between polls) — for scheduled/boop monitoring:
  python3 tools/voice_tts_wedge_check.py
  python3 tools/voice_tts_wedge_check.py --json

  # Single-snapshot (no wait) — quick status, CANNOT prove a wedge, only HEALTHY/UNKNOWN:
  python3 tools/voice_tts_wedge_check.py --snapshot

  # Override the wait gap (e.g. faster CI smoke test):
  VOICE_WEDGE_POLL_GAP=5 python3 tools/voice_tts_wedge_check.py

Exit codes: 0 = HEALTHY/HEALTHY_IDLE/UNKNOWN, 2 = WEDGE (real), 1 = endpoint unreachable.

Source finding: .claude/memory/departments/systems-technology/
  2026-06-15--voice-box-is-slow-serial-worker-not-wedged-round5.md
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:  # pragma: no cover
    print(json.dumps({"status": "ERROR", "reason": "requests not installed"}))
    sys.exit(1)

VOICE_TTS_URL = os.getenv("VOICE_TTS_URL", "https://voice.purebrain.ai").rstrip("/")
VOICE_TTS_API_KEY = os.getenv("VOICE_TTS_API_KEY", "purebrain-tts-2026")
# Per-chunk ceiling. Observed real max on this box = 826s; 900s gives margin without
# being so high it misses a true multi-hour stall. Override via env if the box changes.
MAX_JOB_TIME = int(os.getenv("VOICE_MAX_JOB_TIME", "900"))
# Gap between the two /tts/jobs polls. Default == MAX_JOB_TIME so the box gets a full
# per-job window to advance the head. Override (e.g. 5) for fast smoke tests.
POLL_GAP = int(os.getenv("VOICE_WEDGE_POLL_GAP", str(MAX_JOB_TIME)))
HTTP_TIMEOUT = 30


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def fetch_health():
    """GET /health. Returns dict or raises."""
    r = requests.get(f"{VOICE_TTS_URL}/health", timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetch_jobs():
    """GET /tts/jobs. Returns list of job dicts (each: id, status, created_at, completed_at...)."""
    r = requests.get(f"{VOICE_TTS_URL}/tts/jobs", timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    # API returns {"jobs": [...]} or possibly a bare list — handle both.
    if isinstance(data, dict):
        return data.get("jobs", [])
    if isinstance(data, list):
        return data
    return []


def _parse_ts(val):
    """Parse created_at/completed_at which may be epoch seconds or ISO string. Returns float or None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip()
        # epoch-as-string
        try:
            return float(s)
        except ValueError:
            pass
        # ISO 8601
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def active_jobs(jobs):
    """processing or queued jobs."""
    return [j for j in jobs if str(j.get("status", "")).lower() in ("processing", "queued")]


def queue_head(jobs):
    """Oldest active (processing/queued) job by created_at. None if no active jobs."""
    act = active_jobs(jobs)
    if not act:
        return None

    def keyf(j):
        ts = _parse_ts(j.get("created_at"))
        return ts if ts is not None else float("inf")

    return sorted(act, key=keyf)[0]


def newest_done(jobs):
    """Most-recently-completed `done` job by completed_at. None if none."""
    done = [j for j in jobs if str(j.get("status", "")).lower() == "done"]
    if not done:
        return None

    def keyf(j):
        ts = _parse_ts(j.get("completed_at")) or _parse_ts(j.get("created_at")) or 0.0
        return ts

    return sorted(done, key=keyf, reverse=True)[0]


def _job_summary(j):
    if not j:
        return None
    return {
        "id": j.get("id"),
        "status": j.get("status"),
        "created_at": j.get("created_at"),
        "completed_at": j.get("completed_at"),
    }


def check_liveness(jobs):
    """
    Secondary liveness: if there ARE active jobs but the newest done job completed
    longer ago than 2*MAX_JOB_TIME, nothing is completing -> WEDGE candidate.
    Returns (is_dead, detail) — is_dead True means liveness failed.
    """
    act = active_jobs(jobs)
    if not act:
        return False, "no active jobs (idle); liveness N/A"
    nd = newest_done(jobs)
    if nd is None:
        # Active jobs but zero done in the visible window. Not conclusive on its own —
        # the box may have a short job history. Do NOT alarm on this alone.
        return False, "active jobs but no done job in visible history (inconclusive, not alarming)"
    completed_ts = _parse_ts(nd.get("completed_at"))
    if completed_ts is None:
        return False, "newest done job has unparseable completed_at (inconclusive)"
    age = time.time() - completed_ts
    if age > 2 * MAX_JOB_TIME:
        return True, (
            f"newest done job completed {int(age)}s ago (> 2x MAX_JOB_TIME={2*MAX_JOB_TIME}s) "
            f"while {len(act)} job(s) active — nothing is completing"
        )
    return False, f"newest done job completed {int(age)}s ago (< 2x MAX_JOB_TIME) — completions are flowing"


def snapshot():
    """
    Single-poll status. CANNOT prove a wedge (needs the two-poll window). Returns one of:
    HEALTHY_IDLE, HEALTHY (progress visible), UNKNOWN (active but inconclusive), or
    WEDGE only if the secondary liveness check trips hard.
    """
    try:
        health = fetch_health()
    except Exception as e:
        return {"status": "UNREACHABLE", "reason": f"/health: {e}", "checked_at": _now_iso()}
    try:
        jobs = fetch_jobs()
    except Exception as e:
        return {
            "status": "UNKNOWN",
            "reason": f"/health ok but /tts/jobs failed: {e}",
            "health": health,
            "checked_at": _now_iso(),
        }

    act = active_jobs(jobs)
    head = queue_head(jobs)
    is_dead, live_detail = check_liveness(jobs)

    if not act:
        return {
            "status": "HEALTHY_IDLE",
            "reason": "no active jobs. NOTE: idle 0/0 is a FALSE-GREEN — real readiness "
            "requires a real generation job to complete end-to-end (driver/QA owns that gate).",
            "health": health,
            "active_jobs": 0,
            "checked_at": _now_iso(),
        }

    if is_dead:
        return {
            "status": "WEDGE",
            "reason": f"secondary liveness failed: {live_detail}",
            "health": health,
            "queue_head": _job_summary(head),
            "active_jobs": len(act),
            "checked_at": _now_iso(),
        }

    # Active jobs, liveness ok-or-inconclusive, single snapshot can't prove head-stall.
    return {
        "status": "UNKNOWN",
        "reason": "active job(s) present; single snapshot cannot prove a head-stall. "
        "Serial box runs 8-14 min/chunk — run full two-poll check to decide WEDGE vs HEALTHY. "
        f"Liveness: {live_detail}",
        "health": health,
        "queue_head": _job_summary(head),
        "active_jobs": len(act),
        "max_job_time_s": MAX_JOB_TIME,
        "checked_at": _now_iso(),
    }


def check_wedge(poll_gap=None, verbose=False):
    """
    Full two-poll wedge detection. Polls /tts/jobs, waits ~MAX_JOB_TIME, polls again.
    Returns a result dict with status in {HEALTHY_IDLE, HEALTHY, WEDGE, UNREACHABLE}.
    """
    gap = POLL_GAP if poll_gap is None else poll_gap

    try:
        jobs1 = fetch_jobs()
        health1 = fetch_health()
    except Exception as e:
        return {"status": "UNREACHABLE", "reason": f"first poll failed: {e}", "checked_at": _now_iso()}

    head1 = queue_head(jobs1)

    # If idle on first poll, no wedge possible — report HEALTHY_IDLE immediately (don't wait).
    if head1 is None:
        return {
            "status": "HEALTHY_IDLE",
            "reason": "no active jobs on first poll. Idle 0/0 is a FALSE-GREEN: real "
            "readiness requires a real generation job to complete (driver/QA gate, not this monitor).",
            "health": health1,
            "active_jobs": 0,
            "checked_at": _now_iso(),
        }

    # Secondary liveness on first snapshot — a hard liveness failure is conclusive
    # without waiting the full window.
    is_dead, live_detail = check_liveness(jobs1)
    if is_dead:
        return {
            "status": "WEDGE",
            "reason": f"secondary liveness failed on first poll: {live_detail}",
            "health": health1,
            "queue_head": _job_summary(head1),
            "checked_at": _now_iso(),
        }

    head1_id = head1.get("id")
    head1_created = _parse_ts(head1.get("created_at"))

    if verbose:
        print(
            f"[poll 1 @ {_now_iso()}] head={head1_id} status={head1.get('status')} "
            f"created_at={head1.get('created_at')} active={len(active_jobs(jobs1))} "
            f"-> waiting {gap}s for the box to advance the head...",
            file=sys.stderr,
        )

    time.sleep(gap)

    try:
        jobs2 = fetch_jobs()
        health2 = fetch_health()
    except Exception as e:
        return {"status": "UNREACHABLE", "reason": f"second poll failed: {e}", "checked_at": _now_iso()}

    head2 = queue_head(jobs2)

    # Queue drained entirely -> serial progress completed -> HEALTHY.
    if head2 is None:
        return {
            "status": "HEALTHY",
            "reason": "queue drained between polls — serial worker advanced and finished. Not wedged.",
            "health": health2,
            "checked_at": _now_iso(),
        }

    head2_id = head2.get("id")
    head2_created = _parse_ts(head2.get("created_at"))
    head2_status = str(head2.get("status", "")).lower()

    # Did the head advance? Different job_id == progress.
    if head2_id != head1_id:
        return {
            "status": "HEALTHY",
            "reason": f"queue head advanced {head1_id} -> {head2_id} across {gap}s — serial progress. Not wedged.",
            "health": health2,
            "checked_at": _now_iso(),
        }

    # Did any previously-active job move to done? That's progress too.
    done2_ids = {j.get("id") for j in jobs2 if str(j.get("status", "")).lower() == "done"}
    active1_ids = {j.get("id") for j in active_jobs(jobs1)}
    if active1_ids & done2_ids:
        return {
            "status": "HEALTHY",
            "reason": f"job(s) {sorted(active1_ids & done2_ids)} moved to done across window — completions flowing. Not wedged.",
            "health": health2,
            "checked_at": _now_iso(),
        }

    # Same head, still processing, same created_at, full window elapsed -> REAL wedge.
    same_created = (
        head1_created is not None
        and head2_created is not None
        and abs(head1_created - head2_created) < 1.0
    )
    if head2_status == "processing" and same_created and gap >= MAX_JOB_TIME:
        return {
            "status": "WEDGE",
            "reason": (
                f"queue-head job {head2_id} unchanged (status=processing, same created_at) "
                f"across {gap}s >= MAX_JOB_TIME={MAX_JOB_TIME}s — head NOT advancing = real wedge."
            ),
            "health": health2,
            "queue_head": _job_summary(head2),
            "checked_at": _now_iso(),
        }

    # Same head but window was shorter than MAX_JOB_TIME, or status not processing,
    # or created_at shifted (re-submit) -> inconclusive, NOT a wedge. Do not alarm.
    return {
        "status": "HEALTHY",
        "reason": (
            f"head {head2_id} still present but not a proven stall "
            f"(status={head2_status}, same_created={same_created}, gap={gap}s vs MAX_JOB_TIME={MAX_JOB_TIME}s). "
            "Per policy this is NOT a wedge — serial box just needs more time. Re-run full window to confirm."
        ),
        "health": health2,
        "queue_head": _job_summary(head2),
        "checked_at": _now_iso(),
    }


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    snap = "--snapshot" in args
    verbose = "--verbose" in args or not as_json

    if snap:
        result = snapshot()
    else:
        result = check_wedge(verbose=verbose)

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"VOICE TTS WEDGE CHECK — {result['status']}")
        print(f"  endpoint : {VOICE_TTS_URL}")
        print(f"  reason   : {result.get('reason')}")
        if result.get("queue_head"):
            print(f"  head job : {result['queue_head']}")
        if result.get("health"):
            print(f"  health   : {result['health']}")
        print(f"  checked  : {result.get('checked_at')}")
        print(f"  config   : MAX_JOB_TIME={MAX_JOB_TIME}s POLL_GAP={POLL_GAP}s")

    status = result["status"]
    if status == "WEDGE":
        sys.exit(2)
    if status == "UNREACHABLE":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
