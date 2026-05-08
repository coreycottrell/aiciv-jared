#!/usr/bin/env python3
"""
meeting_reminder_cron.py — Day-Before Meeting Email Reminders

Runs daily at 6pm ET. For each meeting happening TOMORROW, emails all assigned
participants with the pre-meeting form link.

Usage:
    python3 meeting_reminder_cron.py                # live send
    python3 meeting_reminder_cron.py --dry-run      # print what would be sent
    python3 meeting_reminder_cron.py --dry-run --date 2026-04-21  # simulate a specific "tomorrow"
"""

import argparse
import json
import logging
import os
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

import gspread
import requests
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
LOG_FILE = AETHER_ROOT / "logs" / "meeting_cron.log"
ENV_FILE = AETHER_ROOT / ".env"
CREDENTIALS_FILE = AETHER_ROOT / ".credentials" / "google-drive-service-account.json"
SPREADSHEET_ID = "1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E"

ET = ZoneInfo("America/New_York")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [meeting-reminder] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Meeting schedule
# ---------------------------------------------------------------------------
MEETING_SCHEDULE = {
    "leadership": {
        "name": "Leadership Meeting",
        "days": ["mon"],
        "time": "11:00 AM ET",
        "monthly_first": False,
        "biweekly": False,
    },
    "tech-daily": {
        "name": "Technical Daily Check-In",
        "days": ["mon", "tue", "wed", "thu"],
        "time": "8:00 AM ET",
        "monthly_first": False,
        "biweekly": False,
    },
    "governance": {
        "name": "Corporate Governance",
        "days": ["wed"],
        "time": "8:30 AM ET",
        "monthly_first": False,
        "biweekly": False,
    },
    "weekly-tactical": {
        "name": "Weekly Tactical All-Hands",
        "days": ["fri"],
        "time": "9:00 AM ET",
        "monthly_first": False,
        "biweekly": False,
    },
    "pipeline-review": {
        "name": "Commercial Daily / Pipeline Review",
        "days": ["mon", "tue", "wed", "thu"],
        "time": "1:00 PM ET",
        "monthly_first": False,
        "biweekly": False,
    },
    "monthly-strategic": {
        "name": "Monthly Strategic",
        "days": ["mon"],
        "time": "12:00 PM ET",
        "monthly_first": True,
        "biweekly": False,
    },
    "product-customer": {
        "name": "Product / Customer",
        "days": ["tue"],
        "time": "9:00 AM ET",
        "monthly_first": False,
        "biweekly": True,
    },
}

# Bi-weekly reference date (even ISO weeks). We use a fixed anchor.
BIWEEKLY_ANCHOR = datetime(2026, 1, 6, tzinfo=ET)  # A known "on" Monday

# Hardcoded fallback email map (matches the CF Worker TEAM_EMAIL_MAP)
TEAM_EMAIL_MAP_FALLBACK = {
    "jared": "jared@puretechnology.nyc",
    "melanie": "melanie@puretechnology.nyc",
    "nils": "NWaschkau@puretechnology.nyc",
    "metis": "mthancock@gmail.com",
    "rimah": "rimah@puretechnology.nyc",
    "schuman": "mike@puretechnology.nyc",
    "logie": "alex@puretechnology.nyc",
    "nathan": "nathan@puremarketing.ai",
    "johnsmith": "JSmith@puretechnology.nyc",
    "phil": "philip@puretechnology.nyc",
    "orlowski": "robert.orlowski@puretechnology.nyc",
    "ashley": "support@puremarketing.ai",
    "moises": "mo@puremarketing.ai",
    "roger": "roger.beaini@puretechnology.nyc",
    "mireille": "mireille@puretechnology.nyc",
    "baruch": "baruch@puremarketing.ai",
    "natasha": "support@puremarketing.ai",
    "brennan": "edward@puretechnology.nyc",
    "ahsen": "ahsen@puretechnology.nyc",
    "alex": "alex.seant@puretechnology.nyc",
    "waqas": "waqas@puretechnology.nyc",
    "shahbaz": "shahbaz@puretechnology.nyc",
    "zafeer": "zafeer@puretechnology.nyc",
    "corey": "coreycmusic@gmail.com",
    "russell": "russell@puretechnology.nyc",
    "faris": "fasmar@cynoratech.com",
    "mikedaser": "MDaser@puretechnology.nyc",
    "weinberg": "james@puretechnology.nyc",
    "paris": "john.paris@puretechnology.nyc",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env():
    """Load .env and return GMAIL credentials."""
    load_dotenv(ENV_FILE)
    username = os.getenv("GMAIL_USERNAME", "purebrain@puremarketing.ai")
    password = os.getenv("GOOGLE_APP_PASSWORD", "")
    if not password:
        raise RuntimeError("GOOGLE_APP_PASSWORD not found in .env")
    return username, password


def get_team_email_map() -> dict:
    """
    Build person_id -> email map from Google Sheets whitelist.
    Falls back to hardcoded map if Sheets is unreachable.
    """
    try:
        creds = Credentials.from_service_account_file(
            str(CREDENTIALS_FILE),
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        rows = sh.sheet1.get_all_values()

        # Build a name -> email mapping
        name_to_email = {}
        for row in rows[1:]:
            name = row[0].strip() if row[0] else ""
            email = row[2].strip() if len(row) > 2 else ""
            if name and email:
                # Use first occurrence (avoids duplicates)
                if name not in name_to_email:
                    name_to_email[name] = email

        # Map known IDs to names
        id_to_name = {
            "jared": "Jared Sanborn",
            "melanie": "Melanie Salvador",
            "nils": "Nils Waschkau",
            "metis": "Michael Hancock",
            "rimah": "Rimah Harb",
            "schuman": "Michael Schuman",
            "logie": "Alexander Logie",
            "nathan": "Nathan Olson",
            "johnsmith": "John Smith",
            "phil": "Phil Bliss",
            "orlowski": "Robert Orlowski",
            "ashley": "Ashley Tom",
            "moises": "Moises Guerra",
            "roger": "Roger Beaini",
            "mireille": "Mireille Dirany",
            "baruch": "Baruch Santana",
            "natasha": "Natasha Green",
            "brennan": "Edward Brennan",
            "ahsen": "Ahsen Awan",
            "alex": "Alex Seant",
            "waqas": "Waqas Nasir",
            "shahbaz": "Shahbaz Ali",
            "zafeer": "Muhammed Zafeer UL Hassan",
            "corey": "Corey Cottrell",
            "russell": "Russell Korus",
            "faris": "Faris Asmar",
            "mikedaser": "Mike Daser",
            "weinberg": "James Weinberg",
            "paris": "John Paris",
        }

        result = {}
        for pid, name in id_to_name.items():
            if name in name_to_email:
                result[pid] = name_to_email[name]
            elif pid in TEAM_EMAIL_MAP_FALLBACK:
                result[pid] = TEAM_EMAIL_MAP_FALLBACK[pid]

        # Merge any fallback entries not yet present
        for pid, email in TEAM_EMAIL_MAP_FALLBACK.items():
            if pid not in result:
                result[pid] = email

        log.info("Loaded %d team emails from Google Sheets + fallback", len(result))
        return result

    except Exception as e:
        log.warning("Google Sheets failed (%s), using fallback email map", e)
        return dict(TEAM_EMAIL_MAP_FALLBACK)


def get_assignments() -> dict:
    """
    Fetch meeting assignments from the social API.
    Returns {meeting_id: {"required": [id,...], "optional": [id,...]}}.
    """
    url = "https://social.purebrain.ai/api/meetings/assignments"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        result = {}
        for entry in data.get("assignments", []):
            mid = entry.get("meeting_id", "")
            req = entry.get("required_ids", "[]")
            opt = entry.get("optional_ids", "[]")
            if isinstance(req, str):
                req = json.loads(req)
            if isinstance(opt, str):
                opt = json.loads(opt)
            result[mid] = {"required": req or [], "optional": opt or []}
        log.info("Fetched assignments for %d meetings", len(result))
        return result
    except Exception as e:
        log.error("Failed to fetch assignments: %s", e)
        return {}


def is_first_weekday_of_month(dt: datetime, weekday_name: str) -> bool:
    """Check if dt is the first occurrence of weekday_name in its month."""
    return dt.day <= 7


def is_biweekly_on(dt: datetime) -> bool:
    """Check if dt falls on a bi-weekly cadence (even ISO weeks)."""
    iso_week = dt.isocalendar()[1]
    anchor_week = BIWEEKLY_ANCHOR.isocalendar()[1]
    # Both on same parity = "on" week
    return (iso_week % 2) == (anchor_week % 2)


def get_tomorrow_meetings(tomorrow: datetime) -> list:
    """Return list of (meeting_id, meeting_config) for meetings happening on `tomorrow`."""
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    dow = day_names[tomorrow.weekday()]  # Monday=0

    result = []
    for mid, cfg in MEETING_SCHEDULE.items():
        if dow not in cfg["days"]:
            continue
        if cfg["monthly_first"] and not is_first_weekday_of_month(tomorrow, dow):
            continue
        if cfg["biweekly"] and not is_biweekly_on(tomorrow):
            continue
        result.append((mid, cfg))

    return result


def build_email_html(meeting_name: str, meeting_time: str, form_url: str, date_str: str) -> str:
    """Build the HTML email body."""
    return f"""\
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#333;max-width:600px;margin:0 auto;padding:20px">
<div style="background:#0f1220;padding:24px 28px;border-radius:10px;color:#e2e8f0;margin-bottom:20px">
  <h2 style="color:#2a93c1;margin:0 0 4px;font-size:20px">REMINDER: {meeting_name} Tomorrow</h2>
  <p style="color:#94a3b8;margin:0;font-size:14px">{date_str} at {meeting_time}</p>
</div>

<p>Please take 2 minutes to fill out the pre-meeting form so we can make the most of our time together.</p>

<div style="background:#f0f7ff;border:1px solid #d0e3f7;border-radius:8px;padding:16px 20px;margin:20px 0">
  <p style="margin:0 0 12px;font-weight:600;color:#1a1a1a;font-size:14px">What to include in your form:</p>
  <ul style="margin:0;padding-left:20px;color:#555;font-size:13px;line-height:1.8">
    <li>Agenda items you want to discuss</li>
    <li>Blockers or challenges you need help with</li>
    <li>Updates or wins to share with the team</li>
    <li>Questions for other attendees</li>
  </ul>
</div>

<div style="text-align:center;margin:28px 0">
  <a href="{form_url}" style="display:inline-block;background:#2a93c1;color:#fff;text-decoration:none;padding:14px 36px;border-radius:8px;font-weight:700;font-size:16px">Fill Out Pre-Meeting Form</a>
</div>

<div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:8px;padding:14px 20px;margin:20px 0;font-size:13px">
  <table style="border-collapse:collapse;width:100%">
    <tr><td style="padding:4px 8px;color:#888;width:120px">Form Link:</td><td style="padding:4px 8px"><a href="{form_url}" style="color:#0066cc">{form_url}</a></td></tr>
    <tr><td style="padding:4px 8px;color:#888">Password:</td><td style="padding:4px 8px;font-family:monospace;font-weight:700">pure2026</td></tr>
    <tr><td style="padding:4px 8px;color:#888">Meeting:</td><td style="padding:4px 8px">{date_str} at {meeting_time}</td></tr>
  </table>
</div>

<p style="color:#999;font-size:12px;margin-top:32px;border-top:1px solid #eee;padding-top:16px">
  Pure Technology &mdash; Pre-meeting preparation<br>
  <em>Your responses help Aether auto-generate the meeting agenda. The more context you provide, the better prepared we all are.</em>
</p>
</body>
</html>"""


def build_email_text(meeting_name: str, meeting_time: str, form_url: str, date_str: str) -> str:
    """Build plain-text fallback."""
    return f"""\
REMINDER: {meeting_name} Tomorrow
{date_str} at {meeting_time}

Please fill out the pre-meeting form before the meeting:

Form: {form_url}
Password: pure2026

What to include:
- Agenda items you want to discuss
- Blockers or challenges
- Updates or wins to share
- Questions for other attendees

Your responses help auto-generate the meeting agenda.

-- Pure Technology"""


def send_email(
    smtp_user: str,
    smtp_pass: str,
    to_addr: str,
    bcc_addrs: list,
    subject: str,
    html_body: str,
    text_body: str,
    dry_run: bool = False,
) -> bool:
    """Send an email via Gmail SMTP. Returns True on success."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Pure Technology <{smtp_user}>"
    msg["To"] = to_addr
    msg["Subject"] = subject
    # BCC is not added to headers (that's how BCC works) - we pass in rcpt list

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    all_recipients = [to_addr] + bcc_addrs

    if dry_run:
        log.info("[DRY RUN] Would send to %s (+ %d BCC): %s", to_addr, len(bcc_addrs), subject)
        for addr in bcc_addrs:
            log.info("[DRY RUN]   BCC: %s", addr)
        return True

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, all_recipients, msg.as_string())
        log.info("Sent email for '%s' to %d recipients", subject, len(all_recipients))
        return True
    except Exception as e:
        log.error("Failed to send email: %s", e)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Day-before meeting email reminders")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be sent without sending")
    parser.add_argument("--date", type=str, help="Simulate a specific 'tomorrow' date (YYYY-MM-DD)")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("Meeting Reminder Cron started (dry_run=%s)", args.dry_run)

    # Load credentials
    smtp_user, smtp_pass = load_env()

    # Determine "tomorrow" in ET
    now_et = datetime.now(ET)
    if args.date:
        tomorrow = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=ET)
        log.info("Simulating tomorrow = %s", tomorrow.strftime("%A, %B %d, %Y"))
    else:
        tomorrow = now_et + timedelta(days=1)

    date_str = tomorrow.strftime("%A, %B %d, %Y")
    log.info("Tomorrow: %s (%s)", date_str, tomorrow.strftime("%Y-%m-%d"))

    # Find tomorrow's meetings
    meetings = get_tomorrow_meetings(tomorrow)
    if not meetings:
        log.info("No meetings tomorrow. Done.")
        return

    log.info("Found %d meeting(s) tomorrow: %s", len(meetings), ", ".join(m[1]["name"] for m in meetings))

    # Load team email map and assignments
    email_map = get_team_email_map()
    assignments = get_assignments()

    # Jared's email for TO field
    jared_email = email_map.get("jared", "jared@puretechnology.nyc")

    sent_count = 0
    for mid, cfg in meetings:
        meeting_name = cfg["name"]
        meeting_time = cfg["time"]
        form_url = f"https://purebrain.ai/meetings/form/?meeting_id={mid}"

        # Get attendee IDs (required + optional)
        assign = assignments.get(mid, {"required": [], "optional": []})
        all_ids = list(set(assign["required"] + assign["optional"]))

        if not all_ids:
            log.warning("No attendees assigned to %s, skipping", meeting_name)
            continue

        # Resolve IDs to emails (deduplicate)
        seen = set()
        bcc_list = []
        for pid in all_ids:
            email = email_map.get(pid)
            if email and email not in seen and email != jared_email:
                seen.add(email)
                bcc_list.append(email)

        # Skip AI-only addresses from BCC
        ai_emails = {"aethergottaeat@agentmail.to", "chy@agentmail.to", "morphe-pt@agentmail.to"}
        bcc_list = [e for e in bcc_list if e not in ai_emails]

        subject = f"REMINDER: {meeting_name} Tomorrow \u2014 Please Fill Out Pre-Meeting Form"
        html_body = build_email_html(meeting_name, meeting_time, form_url, date_str)
        text_body = build_email_text(meeting_name, meeting_time, form_url, date_str)

        log.info("Sending reminder for %s to %d recipients (Jared TO + %d BCC)",
                 meeting_name, len(bcc_list) + 1, len(bcc_list))

        success = send_email(
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            to_addr=jared_email,
            bcc_addrs=bcc_list,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            dry_run=args.dry_run,
        )
        if success:
            sent_count += 1

    log.info("Done. Sent %d/%d meeting reminders.", sent_count, len(meetings))


if __name__ == "__main__":
    main()
