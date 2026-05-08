#!/usr/bin/env python3
"""PureSurf Session Health Probe — P1+P2 combined service.
Polls BaaS for active session health, posts heartbeats to social-api on status change.
Designed by Morphe, integrated by Aether.
"""
import json, os, sys, time, logging, urllib.request, urllib.error
from pathlib import Path

# === CONFIG (env vars) ===
BAAS_BASE = os.environ.get("BAAS_BASE", "http://157.180.69.225:8901")
BAAS_API_KEY = os.environ.get("BAAS_API_KEY", "")
SOCIAL_API = os.environ.get("SOCIAL_API", "https://social-api.in0v8.workers.dev")
SURF_PROBE_TOKEN = os.environ.get("SURF_PROBE_TOKEN", "")
STALE_DAYS = int(os.environ.get("SURF_STALE_DAYS", "14"))
DEAD_DAYS = int(os.environ.get("SURF_DEAD_DAYS", "30"))
POLL_INTERVAL = int(os.environ.get("SURF_PROBE_INTERVAL", "900"))  # 15 min
STATE_DIR = Path("/var/lib/surf-health-probe")
STATE_FILE = STATE_DIR / "state.json"

PLATFORM_THRESHOLDS = {
    "twitter": {"stale": STALE_DAYS, "dead": DEAD_DAYS},
    "linkedin": {"stale": STALE_DAYS, "dead": DEAD_DAYS},
    "facebook": {"stale": 30, "dead": 60},
    "instagram": {"stale": 30, "dead": 60},
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/jared/projects/AI-CIV/aether/logs/surf_health_probe.log"),
    ]
)
log = logging.getLogger("surf-health-probe")

def baas_headers():
    return {"X-API-Key": BAAS_API_KEY, "User-Agent": "surf-health-probe/1.0"}

def social_headers():
    h = {"Content-Type": "application/json"}
    if SURF_PROBE_TOKEN:
        h["Authorization"] = f"Bearer {SURF_PROBE_TOKEN}"
    return h

def get_active_sessions():
    url = f"{BAAS_BASE}/sessions"
    req = urllib.request.Request(url, headers=baas_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("sessions", [])
    except Exception as e:
        log.warning(f"Failed to fetch sessions: {e}")
        return []

def get_session_health(profile_name):
    url = f"{BAAS_BASE}/sessions/{profile_name}/health"
    req = urllib.request.Request(url, headers=baas_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else {}
    except:
        return {}

def determine_status(health, platform="twitter"):
    if health is None:
        return "failed", 0
    t = PLATFORM_THRESHOLDS.get(platform, {"stale": 14, "dead": 30})
    cookie_age = health.get("cookie_age_days", 0)
    if cookie_age >= t["dead"]:
        return "failed", cookie_age
    if cookie_age >= t["stale"]:
        return "stale", cookie_age
    if health.get("captcha_detected"):
        return "captcha_pending", cookie_age
    if health.get("ban_detected"):
        return "locked", cookie_age
    return "healthy", cookie_age

def post_heartbeat(session_id, status, cookie_age, captcha=0, ban=0, http_status=200):
    url = f"{SOCIAL_API}/api/surf/heartbeat"
    payload = {
        "social_account_id": session_id,
        "status": status,
        "cookie_age_seconds": int(cookie_age * 86400),
        "captcha_detected": captcha,
        "ban_detected": ban,
        "http_status": http_status,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=social_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.info(f"Heartbeat posted: {session_id} → {status}")
    except Exception as e:
        log.error(f"Failed to post heartbeat for {session_id}: {e}")

def load_state():
    try:
        return json.loads(STATE_FILE.read_text()).get("status", {})
    except:
        return {}

def save_state(status_map):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"status": status_map, "updated": time.time()}, indent=2))

def probe_cycle(cycle_num):
    prev = load_state()
    sessions = get_active_sessions()
    next_state = dict(prev)
    changes = 0

    for s in sessions:
        pid = s.get("profile_name", s.get("id", ""))
        platform = s.get("platform", "twitter").lower()
        health = get_session_health(pid)
        status, cookie_age = determine_status(health, platform)

        if status != prev.get(pid):
            captcha = 1 if health and health.get("captcha_detected") else 0
            ban = 1 if health and health.get("ban_detected") else 0
            post_heartbeat(pid, status, cookie_age, captcha, ban)
            changes += 1

        next_state[pid] = status

    save_state(next_state)
    log.info(f"Cycle {cycle_num}: {len(sessions)} sessions checked, {changes} status changes")

def main():
    if not BAAS_API_KEY:
        log.error("BAAS_API_KEY not set. Exiting.")
        sys.exit(1)
    
    log.info(f"Surf Session Health Probe started. BaaS={BAAS_BASE}, interval={POLL_INTERVAL}s, stale={STALE_DAYS}d, dead={DEAD_DAYS}d")
    cycle = 0
    while True:
        cycle += 1
        try:
            probe_cycle(cycle)
        except Exception as e:
            log.error(f"Cycle {cycle} error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
