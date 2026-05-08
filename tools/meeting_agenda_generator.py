#!/usr/bin/env python3
"""
meeting_agenda_generator.py — Auto-Generate Meeting Agenda from Form Responses

Runs 1 hour before each meeting. Fetches form responses from the social API,
compiles them into a formatted agenda page, and deploys via git to purebrain-site.

Usage:
    python3 meeting_agenda_generator.py                          # auto-detect upcoming meetings
    python3 meeting_agenda_generator.py --meeting leadership     # generate for specific meeting
    python3 meeting_agenda_generator.py --dry-run                # preview without deploying
    python3 meeting_agenda_generator.py --meeting leadership --date 2026-04-21  # specific date
"""

import argparse
import html
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
SITE_ROOT = Path("/home/jared/purebrain-site")
LOG_FILE = AETHER_ROOT / "logs" / "meeting_cron.log"
ENV_FILE = AETHER_ROOT / ".env"

ET = ZoneInfo("America/New_York")
API_BASE = "https://social.purebrain.ai"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [agenda-gen] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Meeting config (mirrors form/index.html MEETING_CONFIG)
# ---------------------------------------------------------------------------
MEETING_CONFIG = {
    "leadership": {
        "name": "Leadership Meeting",
        "slug": "leadership-weekly",
        "days": ["mon"],
        "hour": 11,
        "minute": 0,
        "monthly_first": False,
        "biweekly": False,
        "fields": [
            {"key": "win", "label": "Biggest Win This Week"},
            {"key": "risk", "label": "Biggest Risk"},
            {"key": "number", "label": "One Number That Matters"},
            {"key": "cross_functional", "label": "Cross-Functional Issues"},
        ],
    },
    "tech-daily": {
        "name": "Technical Daily Check-In",
        "slug": "technical-daily",
        "days": ["mon", "tue", "wed", "thu"],
        "hour": 8,
        "minute": 0,
        "monthly_first": False,
        "biweekly": False,
        "fields": [
            {"key": "working_on", "label": "Working On Today"},
            {"key": "collisions", "label": "Potential Collisions"},
        ],
    },
    "governance": {
        "name": "Corporate Governance",
        "slug": "corporate-governance",
        "days": ["wed"],
        "hour": 8,
        "minute": 30,
        "monthly_first": False,
        "biweekly": False,
        "fields": [
            {"key": "compliance", "label": "Compliance & Legal"},
            {"key": "security", "label": "Security Items"},
            {"key": "hr", "label": "HR & People"},
            {"key": "financial", "label": "Financial Governance"},
            {"key": "risks", "label": "Top Risks"},
        ],
    },
    "weekly-tactical": {
        "name": "Weekly Tactical All-Hands",
        "slug": "weekly-tactical",
        "days": ["fri"],
        "hour": 9,
        "minute": 0,
        "monthly_first": False,
        "biweekly": False,
        "fields": [
            {"key": "headline", "label": "#1 Headline This Week"},
            {"key": "number", "label": "#1 Number"},
            {"key": "stuck", "label": "Where Are You Stuck?"},
            {"key": "metrics", "label": "Metrics Update"},
        ],
    },
    "pipeline-review": {
        "name": "Commercial Daily / Pipeline Review",
        "slug": "deep-dive-commercial",
        "days": ["mon", "tue", "wed", "thu"],
        "hour": 13,
        "minute": 0,
        "monthly_first": False,
        "biweekly": False,
        "fields": [
            {"key": "activity", "label": "Commercial Activity Today"},
            {"key": "collisions", "label": "Potential Collisions"},
        ],
    },
    "monthly-strategic": {
        "name": "Monthly Strategic",
        "slug": "monthly-strategic",
        "days": ["mon"],
        "hour": 12,
        "minute": 0,
        "monthly_first": True,
        "biweekly": False,
        "fields": [
            {"key": "state", "label": "State of Your Domain"},
            {"key": "decisions", "label": "Strategic Decisions Needed"},
            {"key": "conflicts", "label": "Unresolved Cross-Functional Tension"},
            {"key": "ninety_day", "label": "What Must Be True 90 Days From Now"},
        ],
    },
    "product-customer": {
        "name": "Product / Customer",
        "slug": "product-customer",
        "days": ["tue"],
        "hour": 9,
        "minute": 0,
        "monthly_first": False,
        "biweekly": True,
        "fields": [
            {"key": "feedback", "label": "Customer Feedback"},
            {"key": "features", "label": "Feature Requests"},
            {"key": "roadmap", "label": "Roadmap Updates"},
        ],
    },
}

# Bi-weekly anchor
BIWEEKLY_ANCHOR = datetime(2026, 1, 6, tzinfo=ET)

# Slug mapping for existing site directories
SLUG_OVERRIDES = {
    "leadership": "leadership-weekly",
    "weekly-tactical": "weekly-tactical",
    "tech-daily": "technical-daily",
    "governance": "corporate-governance",
    "pipeline-review": "deep-dive-commercial",
    "monthly-strategic": "monthly-strategic",
    "product-customer": "product-customer",
}

# Password gate hash (SHA-256 of "pure2026")
PW_HASH = "7b9c3fee2d2dd109f2c9e39e5f5bf0089104e91f242a7206017089368870d989"


# ---------------------------------------------------------------------------
# Schedule helpers
# ---------------------------------------------------------------------------

def is_first_weekday_of_month(dt: datetime) -> bool:
    return dt.day <= 7


def is_biweekly_on(dt: datetime) -> bool:
    iso_week = dt.isocalendar()[1]
    anchor_week = BIWEEKLY_ANCHOR.isocalendar()[1]
    return (iso_week % 2) == (anchor_week % 2)


def get_meetings_for_date(target: datetime) -> list:
    """Return [(meeting_id, config)] for meetings on target date."""
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    dow = day_names[target.weekday()]

    result = []
    for mid, cfg in MEETING_CONFIG.items():
        if dow not in cfg["days"]:
            continue
        if cfg["monthly_first"] and not is_first_weekday_of_month(target):
            continue
        if cfg["biweekly"] and not is_biweekly_on(target):
            continue
        result.append((mid, cfg))
    return result


def get_upcoming_meetings_within_hour(now_et: datetime) -> list:
    """Return meetings happening within the next 60-90 minutes."""
    result = []
    today_meetings = get_meetings_for_date(now_et)
    for mid, cfg in today_meetings:
        meeting_time = now_et.replace(hour=cfg["hour"], minute=cfg["minute"], second=0, microsecond=0)
        diff = (meeting_time - now_et).total_seconds()
        # Generate agenda 30-90 minutes before meeting
        if 1800 <= diff <= 5400:
            result.append((mid, cfg))
    return result


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def fetch_responses(meeting_id: str) -> list:
    """
    Fetch form responses from social API.
    Returns list of response dicts, or empty list if none/error.
    """
    url = f"{API_BASE}/api/meetings/responses/{meeting_id}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            log.info("No responses endpoint or no data for %s", meeting_id)
            return []
        resp.raise_for_status()
        data = resp.json()

        # Handle various response formats
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "responses" in data:
                return data["responses"]
            if "results" in data:
                return data["results"]
            if "error" in data:
                log.info("API returned error for %s: %s", meeting_id, data["error"])
                return []

        return []
    except Exception as e:
        log.warning("Failed to fetch responses for %s: %s", meeting_id, e)
        return []


def fetch_assignments(meeting_id: str) -> dict:
    """Fetch assignments to know who's expected."""
    url = f"{API_BASE}/api/meetings/assignments"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for entry in data.get("assignments", []):
            if entry.get("meeting_id") == meeting_id:
                req = entry.get("required_ids", "[]")
                opt = entry.get("optional_ids", "[]")
                if isinstance(req, str):
                    req = json.loads(req)
                if isinstance(opt, str):
                    opt = json.loads(opt)
                return {"required": req or [], "optional": opt or []}
        return {"required": [], "optional": []}
    except Exception as e:
        log.warning("Failed to fetch assignments: %s", e)
        return {"required": [], "optional": []}


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def esc(text: str) -> str:
    """HTML escape."""
    return html.escape(str(text)) if text else ""


def build_respondent_section(resp: dict, fields: list) -> str:
    """Build HTML section for one respondent's answers."""
    name = esc(resp.get("respondent_name", resp.get("name", "Unknown")))
    rtype = resp.get("respondent_type", "human")
    role_label = " (AI)" if rtype == "ai" else ""

    # Get response data - handle both formats
    answers = resp.get("responses", resp.get("answers", {}))
    if isinstance(answers, str):
        try:
            answers = json.loads(answers)
        except (json.JSONDecodeError, TypeError):
            answers = {}
    if isinstance(answers, list):
        # Convert [{question, answer}] to {question: answer}
        answers = {item.get("question", ""): item.get("answer", "") for item in answers}

    items_html = ""
    has_content = False
    for field in fields:
        key = field["key"]
        label = esc(field["label"])
        value = answers.get(key, "").strip() if isinstance(answers, dict) else ""

        if not value:
            # Check by label match as fallback
            value = answers.get(label, "").strip() if isinstance(answers, dict) else ""

        if value:
            has_content = True
            # Convert newlines to <br> for display
            value_html = esc(value).replace("\n", "<br>")
            items_html += f'    <div class="response-item"><span class="response-label">{label}</span><div class="response-text">{value_html}</div></div>\n'

    if not has_content:
        items_html = '    <div class="response-item"><span class="response-text" style="color:var(--text-dim);font-style:italic">No detailed responses submitted.</span></div>\n'

    return f"""\
  <div class="respondent-card">
    <div class="respondent-header">
      <span class="respondent-name">{name}{esc(role_label)}</span>
    </div>
{items_html}  </div>
"""


def build_action_items(responses: list, fields: list) -> str:
    """Extract action items from responses mentioning blockers or requests."""
    items = []
    blocker_keys = {"stuck", "risk", "risks", "collisions", "conflicts", "security", "compliance"}

    for resp in responses:
        name = resp.get("respondent_name", resp.get("name", "Unknown"))
        answers = resp.get("responses", resp.get("answers", {}))
        if isinstance(answers, str):
            try:
                answers = json.loads(answers)
            except (json.JSONDecodeError, TypeError):
                answers = {}
        if isinstance(answers, list):
            answers = {item.get("question", ""): item.get("answer", "") for item in answers}

        for field in fields:
            key = field["key"]
            if key in blocker_keys:
                value = answers.get(key, "").strip() if isinstance(answers, dict) else ""
                if value and len(value) > 5:
                    items.append({"owner": name, "item": value})

    if not items:
        return ""

    html_parts = ['  <h2>Action Items & Blockers</h2>\n  <div class="section-card highlight">\n']
    for ai in items:
        html_parts.append(
            f'    <div class="action-item"><span class="owner">{esc(ai["owner"])}</span> '
            f'{esc(ai["item"][:200])}</div>\n'
        )
    html_parts.append("  </div>\n")
    return "".join(html_parts)


def generate_agenda_html(
    meeting_id: str,
    cfg: dict,
    responses: list,
    meeting_date: datetime,
) -> str:
    """Generate the full agenda HTML page."""
    meeting_name = cfg["name"]
    slug = SLUG_OVERRIDES.get(meeting_id, meeting_id)
    fields = cfg["fields"]
    date_str = meeting_date.strftime("%B %d, %Y")
    day_str = meeting_date.strftime("%A")
    time_str = f"{cfg['hour']}:{cfg['minute']:02d}"
    # Convert to 12h
    h = cfg["hour"]
    ampm = "AM" if h < 12 else "PM"
    h12 = h if h <= 12 else h - 12
    if h12 == 0:
        h12 = 12
    time_display = f"{h12}:{cfg['minute']:02d} {ampm} ET"

    response_count = len(responses)
    form_url = f"https://purebrain.ai/meetings/form/?meeting_id={meeting_id}"

    # Build respondent sections
    respondent_sections = ""
    if responses:
        for resp in responses:
            respondent_sections += build_respondent_section(resp, fields)
    else:
        respondent_sections = """\
  <div class="section-card" style="text-align:center;padding:40px 20px">
    <p style="font-size:16px;color:var(--text-muted);margin-bottom:16px">No form responses received yet.</p>
    <p style="font-size:13px;color:var(--text-dim)">Team members can submit their updates via the pre-meeting form below.</p>
  </div>
"""

    action_items = build_action_items(responses, fields) if responses else ""

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(meeting_name)} Agenda &mdash; {esc(date_str)} | Pure Technology</title>
<meta name="robots" content="noindex, nofollow">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#080a12;--surface:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.07);--text:rgba(255,255,255,0.85);--text-muted:rgba(255,255,255,0.5);--text-dim:rgba(255,255,255,0.28);--blue:#2a93c1;--orange:#f1420b;--green:#22c55e;--red:#ef4444;--yellow:#eab308;--amber:#f59e0b}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.6;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 70% 50% at 50% -10%,rgba(42,147,193,0.08),transparent 70%),radial-gradient(ellipse 50% 40% at 80% 100%,rgba(241,66,11,0.06),transparent 70%);pointer-events:none;z-index:0}}
#gate{{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:9999;transition:opacity .4s}}
#gate.dissolved{{opacity:0;pointer-events:none}}
.gate-panel{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:40px 32px;max-width:400px;width:90%;text-align:center;backdrop-filter:blur(16px)}}
.gate-logo{{font-size:24px;font-weight:900;letter-spacing:-0.5px;margin-bottom:8px}}
.gate-logo .b{{color:var(--blue)}}.gate-logo .o{{color:var(--orange)}}
.gate-panel h2{{font-size:18px;font-weight:600;color:#fff;margin-bottom:6px}}
.gate-panel p{{font-size:12px;color:var(--text-muted);margin-bottom:20px}}
#gate-input{{width:100%;padding:14px 16px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:8px;color:#fff;font-size:14px;text-align:center;outline:none;transition:border-color .2s}}
#gate-input:focus{{border-color:var(--blue)}}
#gate-btn{{width:100%;margin-top:12px;padding:14px;background:var(--blue);color:#fff;border:none;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer}}
#gate-btn:hover{{background:#1e7099}}
#gate-error{{color:var(--red);font-size:12px;margin-top:10px;min-height:16px}}
body.locked{{overflow:hidden}}
.container{{position:relative;z-index:1;max-width:900px;margin:0 auto;padding:40px 24px 80px;display:none}}
.header{{text-align:center;padding-bottom:32px;border-bottom:1px solid var(--border);margin-bottom:32px}}
.meeting-tag{{display:inline-block;background:rgba(245,158,11,0.1);color:var(--amber);padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px}}
.date-tag{{display:inline-block;background:rgba(42,147,193,0.1);color:var(--blue);padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;margin-left:8px}}
.auto-tag{{display:inline-block;background:rgba(34,197,94,0.1);color:var(--green);padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;margin-left:8px}}
.header h1{{font-size:32px;font-weight:800;color:#fff;letter-spacing:-0.02em;margin-bottom:6px}}
.header h1 em{{color:var(--orange);font-style:normal}}
.header .meta{{font-size:14px;color:var(--text-muted)}}
h2{{font-size:20px;font-weight:700;color:#fff;margin:36px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
.section-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;margin:16px 0}}
.highlight{{background:rgba(241,66,11,0.06);border-color:rgba(241,66,11,0.18)}}
.respondent-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;margin:16px 0}}
.respondent-header{{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border)}}
.respondent-name{{font-size:16px;font-weight:700;color:#fff}}
.response-item{{margin:10px 0}}
.response-label{{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--blue);font-weight:700;margin-bottom:4px}}
.response-text{{font-size:14px;color:var(--text);line-height:1.6}}
.action-item{{background:rgba(42,147,193,0.06);border:1px solid rgba(42,147,193,0.15);border-radius:8px;padding:10px 14px;margin:6px 0;font-size:13px;display:flex;align-items:flex-start;gap:8px}}
.action-item .owner{{color:var(--blue);font-weight:600;white-space:nowrap;min-width:100px}}
.form-cta{{background:rgba(42,147,193,0.08);border:1px solid rgba(42,147,193,0.2);border-radius:12px;padding:20px;text-align:center;margin:24px 0}}
.form-cta a{{color:var(--blue);font-weight:700;text-decoration:none;font-size:15px}}
.form-cta a:hover{{text-decoration:underline}}
.form-cta .pw{{font-size:12px;color:var(--text-muted);margin-top:6px}}
.back-link{{display:inline-block;margin-bottom:24px;color:var(--blue);text-decoration:none;font-size:13px;font-weight:600}}
.back-link:hover{{text-decoration:underline}}
.footer{{text-align:center;margin-top:48px;padding-top:24px;border-top:1px solid var(--border);font-size:11px;color:var(--text-dim)}}
@media(max-width:600px){{.header h1{{font-size:22px}}h2{{font-size:17px}}.section-card,.respondent-card{{padding:14px}}}}
</style>
</head>
<body class="locked">

<div id="gate">
  <div class="gate-panel">
    <div class="gate-logo"><span class="b">PURE</span> <span class="o">TECH</span></div>
    <h2>Meeting Agenda</h2>
    <p>Enter the meeting code to access the agenda.</p>
    <input id="gate-input" type="password" autocomplete="off" spellcheck="false" placeholder="Meeting Code">
    <button id="gate-btn" type="button">Enter</button>
    <div id="gate-error"></div>
  </div>
</div>

<div class="container" id="main">
  <a href="/meetings/{esc(slug)}/" class="back-link">&larr; Back to {esc(meeting_name)}</a>

  <div class="header">
    <span class="meeting-tag">{esc(meeting_name)}</span>
    <span class="date-tag">{esc(date_str)}</span>
    <span class="auto-tag">Auto-Generated</span>
    <h1>{esc(meeting_name)} <em>Agenda</em></h1>
    <div class="meta">Generated from {response_count} team response{"s" if response_count != 1 else ""} &bull; {esc(day_str)} at {esc(time_display)}</div>
  </div>

  <div class="form-cta">
    <a href="{esc(form_url)}">Haven't submitted yet? Fill Out Pre-Meeting Form &rarr;</a>
    <div class="pw">Password: pure2026</div>
  </div>

  <h2>Team Responses</h2>
{respondent_sections}
{action_items}
  <div class="form-cta">
    <a href="/team/responses/">View All Form Responses &rarr;</a>
    <div class="pw">Password: pure2026</div>
  </div>

  <div class="footer">
    Pure Technology &bull; {esc(meeting_name)} Agenda &bull; {esc(date_str)}<br>
    Auto-generated by Aether from {response_count} pre-meeting form response{"s" if response_count != 1 else ""}
  </div>
</div>

<script>
const PW_HASH='{PW_HASH}';
async function hashPw(s){{const buf=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('')}}
const gate=document.getElementById('gate'),input=document.getElementById('gate-input'),btn=document.getElementById('gate-btn'),errEl=document.getElementById('gate-error'),main=document.getElementById('main');
async function tryUnlock(){{const val=input.value.trim().toLowerCase();if(!val){{errEl.textContent='Enter the meeting code';return}}const h=await hashPw(val);if(h===PW_HASH){{try{{sessionStorage.setItem('pt_meeting_unlocked','1')}}catch(e){{}}gate.classList.add('dissolved');document.body.classList.remove('locked');main.style.display='block';setTimeout(()=>gate.remove(),500)}}else{{errEl.textContent='Invalid code';input.value=''}}}}
btn.addEventListener('click',tryUnlock);input.addEventListener('keydown',e=>{{if(e.key==='Enter')tryUnlock()}});
try{{if(sessionStorage.getItem('pt_meeting_unlocked')==='1'){{gate.classList.add('dissolved');document.body.classList.remove('locked');main.style.display='block';setTimeout(()=>gate.remove(),500)}}}}catch(e){{}}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Deployment
# ---------------------------------------------------------------------------

def deploy_agenda(meeting_id: str, cfg: dict, html_content: str, meeting_date: datetime, dry_run: bool = False) -> bool:
    """Write agenda HTML to purebrain-site and git commit + push."""
    slug = SLUG_OVERRIDES.get(meeting_id, meeting_id)
    mm_yyyy = meeting_date.strftime("%m%Y")
    date_str = meeting_date.strftime("%B %d, %Y")

    page_dir = SITE_ROOT / "meetings" / slug / mm_yyyy
    page_file = page_dir / "index.html"

    if dry_run:
        log.info("[DRY RUN] Would write %d bytes to %s", len(html_content), page_file)
        return True

    page_dir.mkdir(parents=True, exist_ok=True)
    page_file.write_text(html_content, encoding="utf-8")
    log.info("Wrote agenda to %s (%d bytes)", page_file, len(html_content))

    # Git add, commit, push
    try:
        subprocess.run(["git", "add", "meetings/"], cwd=str(SITE_ROOT), check=True, capture_output=True)

        # Check if there are actual changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(SITE_ROOT),
            capture_output=True,
        )
        if result.returncode == 0:
            log.info("No changes to commit (agenda already up to date)")
            return True

        commit_msg = f"auto: Meeting agenda for {cfg['name']} {date_str}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(SITE_ROOT),
            check=True,
            capture_output=True,
        )
        log.info("Committed: %s", commit_msg)

        subprocess.run(
            ["git", "push"],
            cwd=str(SITE_ROOT),
            check=True,
            capture_output=True,
            timeout=60,
        )
        log.info("Pushed to remote")
        return True

    except subprocess.CalledProcessError as e:
        log.error("Git operation failed: %s\nstdout: %s\nstderr: %s",
                  e.cmd, e.stdout.decode()[:300] if e.stdout else "", e.stderr.decode()[:300] if e.stderr else "")
        return False
    except subprocess.TimeoutExpired:
        log.error("Git push timed out")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Auto-generate meeting agendas from form responses")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deploying")
    parser.add_argument("--meeting", type=str, help="Specific meeting_id to generate for")
    parser.add_argument("--date", type=str, help="Meeting date (YYYY-MM-DD), default=today")
    args = parser.parse_args()

    load_dotenv(ENV_FILE)

    log.info("=" * 60)
    log.info("Agenda Generator started (dry_run=%s)", args.dry_run)

    now_et = datetime.now(ET)

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=ET)
    else:
        target_date = now_et

    log.info("Target date: %s", target_date.strftime("%A, %B %d, %Y"))

    # Determine which meetings to generate for
    if args.meeting:
        if args.meeting not in MEETING_CONFIG:
            log.error("Unknown meeting_id: %s. Valid: %s", args.meeting, ", ".join(MEETING_CONFIG.keys()))
            sys.exit(1)
        meetings = [(args.meeting, MEETING_CONFIG[args.meeting])]
    elif args.date:
        meetings = get_meetings_for_date(target_date)
    else:
        # Auto-detect: meetings happening within next 60-90 minutes
        meetings = get_upcoming_meetings_within_hour(now_et)
        if not meetings:
            # Fallback: check if any meetings today haven't had agendas generated
            meetings = get_meetings_for_date(now_et)
            if meetings:
                log.info("No meetings in next hour window, but %d meetings today. Generating all.", len(meetings))

    if not meetings:
        log.info("No meetings to generate agendas for. Done.")
        return

    log.info("Generating agendas for %d meeting(s): %s",
             len(meetings), ", ".join(m[1]["name"] for m in meetings))

    success_count = 0
    for mid, cfg in meetings:
        log.info("--- Processing: %s ---", cfg["name"])

        # Fetch responses
        responses = fetch_responses(mid)
        log.info("Fetched %d responses for %s", len(responses), mid)

        # Generate HTML
        html_content = generate_agenda_html(mid, cfg, responses, target_date)

        # Deploy
        if deploy_agenda(mid, cfg, html_content, target_date, dry_run=args.dry_run):
            success_count += 1

        if args.dry_run and responses:
            log.info("[DRY RUN] Preview: %d respondents would appear in agenda", len(responses))
            for r in responses:
                log.info("[DRY RUN]   - %s", r.get("respondent_name", r.get("name", "Unknown")))

    log.info("Done. Generated %d/%d agendas.", success_count, len(meetings))


if __name__ == "__main__":
    main()
