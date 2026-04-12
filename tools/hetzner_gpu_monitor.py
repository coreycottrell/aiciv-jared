#!/usr/bin/env python3
"""
Hetzner GPU Server Auction Monitor
Checks every 15 minutes for GPU servers under a price threshold.
Alerts via Telegram + email when NEW servers appear.

API: https://www.hetzner.com/_resources/app/data/app/live_data_sb_EUR.json
"""

import json
import os
import sys
import time
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────
HETZNER_API = "https://www.hetzner.com/_resources/app/data/app/live_data_sb_EUR.json"
MAX_PRICE_EUR = 150  # Alert for GPU servers under this price
STATE_FILE = Path(__file__).resolve().parent.parent / ".hetzner_monitor_state.json"
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
AETHER_ROOT = Path(__file__).resolve().parent.parent

# Telegram
TG_CONFIG = AETHER_ROOT / "config" / "telegram_config.json"
TG_CHAT_ID = "548906264"  # Jared

# Email
EMAIL_TO = "jared@puretechnology.nyc"

# GPU detection keywords in description/specials
GPU_KEYWORDS = [
    "gpu", "nvidia", "geforce", "rtx", "gtx", "tesla",
    "a100", "a40", "a30", "a10", "l40", "h100", "v100",
    "quadro", "titan"
]

# ── Logging ────────────────────────────────────────────────────────
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("hetzner-gpu-monitor")


def load_state() -> dict:
    """Load previously seen server IDs."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"seen_ids": [], "last_check": None, "last_alert_ids": []}


def save_state(state: dict):
    """Persist state to disk."""
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_servers() -> list:
    """Fetch current auction server list from Hetzner."""
    resp = requests.get(
        HETZNER_API,
        headers={"User-Agent": "Mozilla/5.0 (HetznerGPUMonitor/1.0)"},
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("server", [])


def is_gpu_server(server: dict) -> bool:
    """Check if a server has a GPU based on description and specials."""
    specials = [s.lower() for s in server.get("specials", [])]
    if "gpu" in specials:
        return True

    desc_parts = server.get("description", [])
    desc_str = " ".join(desc_parts).lower()
    return any(kw in desc_str for kw in GPU_KEYWORDS)


def extract_gpu_name(server: dict) -> str:
    """Extract GPU model name from description."""
    for part in server.get("description", []):
        lower = part.lower()
        if "gpu" in lower or any(kw in lower for kw in GPU_KEYWORDS):
            return part.replace("GPU - ", "").strip()
    return "Unknown GPU"


def format_server(s: dict) -> str:
    """Format a server for display."""
    gpu = extract_gpu_name(s)
    ram = s.get("ram_size", "?")
    cpu = s.get("cpu", "?")
    dc = s.get("datacenter_hr", s.get("datacenter", "?"))
    price = s.get("price", "?")
    setup = s.get("setup_price", 0)
    disks = ", ".join(s.get("hdd_hr", []))
    order_url = f"https://www.hetzner.com/sb?search={s['id']}"

    lines = [
        f"  Server ID: {s['id']}",
        f"  GPU: {gpu}",
        f"  CPU: {cpu}",
        f"  RAM: {ram} GB",
        f"  Disks: {disks}",
        f"  DC: {dc}",
        f"  Price: EUR {price}/mo (setup: EUR {setup})",
        f"  Order: {order_url}",
    ]
    return "\n".join(lines)


def send_telegram(message: str):
    """Send alert to Telegram."""
    try:
        if TG_CONFIG.exists():
            with open(TG_CONFIG) as f:
                cfg = json.load(f)
            token = cfg["bot_token"]
        else:
            log.warning("No Telegram config found, skipping TG alert")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)
        if resp.status_code == 200:
            log.info("Telegram alert sent")
        else:
            log.error(f"Telegram send failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Telegram error: {e}")


def send_email(subject: str, body: str):
    """Send alert email via Google SMTP."""
    try:
        env_path = AETHER_ROOT / ".env"
        gmail_user = None
        gmail_pass = None

        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GMAIL_USERNAME="):
                        gmail_user = line.split("=", 1)[1]
                    elif line.startswith("GOOGLE_APP_PASSWORD="):
                        gmail_pass = line.split("=", 1)[1]

        if not gmail_user or not gmail_pass:
            log.warning("Gmail credentials not found in .env, skipping email")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = EMAIL_TO
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.sendmail(gmail_user, [EMAIL_TO], msg.as_string())

        log.info(f"Email alert sent to {EMAIL_TO}")
    except Exception as e:
        log.error(f"Email error: {e}")


def main():
    log.info("Hetzner GPU Monitor starting...")

    state = load_state()
    seen_ids = set(state.get("seen_ids", []))

    # Fetch servers
    try:
        servers = fetch_servers()
        log.info(f"Fetched {len(servers)} servers from Hetzner auction")
    except Exception as e:
        log.error(f"Failed to fetch servers: {e}")
        save_state(state)
        return

    # Filter: GPU + under price threshold
    gpu_servers = [
        s for s in servers
        if is_gpu_server(s) and s.get("price", 9999) <= MAX_PRICE_EUR
    ]
    log.info(f"Found {len(gpu_servers)} GPU servers under EUR {MAX_PRICE_EUR}/mo")

    # Find NEW servers (not seen before)
    new_servers = [s for s in gpu_servers if s["id"] not in seen_ids]

    # Log all current GPU servers
    if gpu_servers:
        log.info("Current GPU servers under threshold:")
        for s in sorted(gpu_servers, key=lambda x: x.get("price", 0)):
            gpu = extract_gpu_name(s)
            log.info(f"  [{s['id']}] {gpu} | EUR {s['price']}/mo | {s.get('cpu', '?')} | {s.get('ram_size', '?')}GB RAM")

    # Alert on new servers
    if new_servers:
        log.info(f"NEW GPU servers found: {len(new_servers)}")

        # Build alert message
        header = f"HETZNER GPU ALERT: {len(new_servers)} new GPU server(s) found!\n"
        header += f"Price threshold: EUR {MAX_PRICE_EUR}/mo\n"
        header += f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        header += "=" * 50

        server_blocks = []
        for s in sorted(new_servers, key=lambda x: x.get("price", 0)):
            server_blocks.append(format_server(s))

        body = header + "\n\n" + "\n\n".join(server_blocks)
        body += f"\n\nBrowse all: https://www.hetzner.com/sb/?gpu=true"

        # Telegram (shorter format)
        tg_lines = [f"<b>HETZNER GPU ALERT</b> - {len(new_servers)} new server(s)!\n"]
        for s in sorted(new_servers, key=lambda x: x.get("price", 0)):
            gpu = extract_gpu_name(s)
            tg_lines.append(
                f"<b>EUR {s['price']}/mo</b> | {gpu}\n"
                f"{s.get('cpu', '?')} | {s.get('ram_size', '?')}GB RAM\n"
                f"https://www.hetzner.com/sb?search={s['id']}"
            )
        tg_msg = "\n\n".join(tg_lines)

        send_telegram(tg_msg)
        send_email(
            f"Hetzner GPU Alert: {len(new_servers)} new server(s) under EUR {MAX_PRICE_EUR}/mo",
            body
        )
    else:
        log.info("No new GPU servers (all previously seen)")

    # Update seen IDs - keep current GPU server IDs + recent history
    current_gpu_ids = {s["id"] for s in gpu_servers}
    # Keep seen_ids that are still active + add new ones
    # Prune IDs older than what is currently listed (they are sold)
    all_current_ids = {s["id"] for s in servers}
    updated_seen = (seen_ids & all_current_ids) | current_gpu_ids
    state["seen_ids"] = list(updated_seen)
    state["gpu_count"] = len(gpu_servers)
    state["total_servers"] = len(servers)
    if new_servers:
        state["last_alert_ids"] = [s["id"] for s in new_servers]
        state["last_alert_time"] = datetime.now(timezone.utc).isoformat()

    save_state(state)
    log.info("Monitor complete")


if __name__ == "__main__":
    main()
