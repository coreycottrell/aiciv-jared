#!/usr/bin/env python3
"""
Email State Management for Aether

Persistent email state tracking that survives session boundaries.
Enables instant differentiation between "truly new" emails and "already seen" messages.

Usage:
    # Check email stats (for BOOP/wake-up)
    python3 tools/email_state.py stats

    # List new messages (not yet seen)
    python3 tools/email_state.py new

    # List unprocessed directives from Jared
    python3 tools/email_state.py directives

    # Full help
    python3 tools/email_state.py --help

Author: Aether
Created: 2026-02-04
"""

import json
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# State file location
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "memories" / "agents" / "email-monitor"
STATE_FILE = STATE_DIR / "email_state.json"
BACKUP_FILE = STATE_DIR / ".email_state.json.bak"

# Jared's known email addresses
JARED_ADDRESSES = [
    "jaredcmusic@gmail.com",
    "jared@cottrell.co",
    "purebrain@puremarketing.ai",
    "jared@puremarketing.ai"
]


def initialize_state() -> dict:
    """Create a fresh state structure"""
    return {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat(),
        "session_id": None,
        "messages": {},
        "directives": [],
        "stats": {
            "new_count": 0,
            "seen_count": 0,
            "responded_count": 0,
            "ignored_count": 0,
            "archived_count": 0,
            "new_from_jared": 0,
            "unprocessed_directives": 0
        }
    }


def load_state() -> dict:
    """Load email state from JSON file"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file, try backup
            if BACKUP_FILE.exists():
                with open(BACKUP_FILE) as f:
                    return json.load(f)
    return initialize_state()


def save_state(state: dict):
    """Save email state to JSON file (atomic write with backup)"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Backup existing state
    if STATE_FILE.exists():
        shutil.copy(STATE_FILE, BACKUP_FILE)

    # Update modification time
    state["last_modified"] = datetime.now().isoformat()

    # Recompute stats
    state["stats"] = compute_stats(state)

    # Atomic write via temp file
    temp_file = STATE_FILE.with_suffix('.json.tmp')
    with open(temp_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)

    temp_file.rename(STATE_FILE)


def compute_stats(state: dict) -> dict:
    """Compute current statistics from state"""
    messages = state.get("messages", {})
    directives = state.get("directives", [])

    stats = {
        "new_count": 0,
        "seen_count": 0,
        "responded_count": 0,
        "ignored_count": 0,
        "archived_count": 0,
        "new_from_jared": 0,
        "unprocessed_directives": 0
    }

    for msg_id, msg in messages.items():
        status = msg.get("status", "new")
        stats[f"{status}_count"] = stats.get(f"{status}_count", 0) + 1

        if status == "new" and msg.get("is_from_jared"):
            stats["new_from_jared"] += 1

    for directive in directives:
        if directive.get("status") in ["unprocessed", "in_progress"]:
            stats["unprocessed_directives"] += 1

    return stats


def is_from_jared(from_addr: str) -> bool:
    """Check if email is from one of Jared's addresses"""
    from_lower = from_addr.lower()
    return any(addr.lower() in from_lower for addr in JARED_ADDRESSES)


def is_message_new(msg_id: str) -> bool:
    """Check if a message ID is new (not in state)"""
    state = load_state()
    return msg_id not in state.get("messages", {})


def get_message_status(msg_id: str) -> Optional[str]:
    """Get the status of a message by ID"""
    state = load_state()
    msg = state.get("messages", {}).get(msg_id)
    return msg.get("status") if msg else None


def mark_message_seen(msg_id: str):
    """Mark a message as seen"""
    state = load_state()
    if msg_id in state.get("messages", {}):
        state["messages"][msg_id]["status"] = "seen"
        state["messages"][msg_id]["seen_at"] = datetime.now().isoformat()
        save_state(state)


def mark_message_responded(msg_id: str, response_summary: str = ""):
    """Mark a message as responded"""
    state = load_state()
    if msg_id in state.get("messages", {}):
        state["messages"][msg_id]["status"] = "responded"
        state["messages"][msg_id]["responded_at"] = datetime.now().isoformat()
        state["messages"][msg_id]["response_summary"] = response_summary
        save_state(state)


def mark_message_ignored(msg_id: str, reason: str = ""):
    """Mark a message as intentionally ignored"""
    state = load_state()
    if msg_id in state.get("messages", {}):
        state["messages"][msg_id]["status"] = "ignored"
        state["messages"][msg_id]["ignored_at"] = datetime.now().isoformat()
        state["messages"][msg_id]["ignore_reason"] = reason
        save_state(state)


def mark_message_archived(msg_id: str):
    """Mark a message as archived (fully processed)"""
    state = load_state()
    if msg_id in state.get("messages", {}):
        state["messages"][msg_id]["status"] = "archived"
        state["messages"][msg_id]["archived_at"] = datetime.now().isoformat()
        save_state(state)


def add_message(msg_id: str, from_addr: str, subject: str, date: str = None,
                preview: str = "", thread_id: str = None) -> dict:
    """Add a new message to tracking"""
    state = load_state()

    if msg_id not in state.get("messages", {}):
        state.setdefault("messages", {})[msg_id] = {
            "status": "new",
            "from": from_addr,
            "subject": subject,
            "date": date or datetime.now().isoformat(),
            "preview": preview[:200],
            "thread_id": thread_id,
            "is_from_jared": is_from_jared(from_addr),
            "added_at": datetime.now().isoformat()
        }
        save_state(state)

    return state["messages"][msg_id]


def add_directive(msg_id: str, text: str, priority: str = "medium") -> dict:
    """Add a directive (instruction from Jared) to tracking"""
    state = load_state()

    directive = {
        "id": hashlib.md5(f"{msg_id}:{text[:50]}".encode()).hexdigest()[:8],
        "msg_id": msg_id,
        "text": text,
        "priority": priority,  # critical, high, medium, low
        "status": "unprocessed",  # unprocessed, in_progress, completed, deferred
        "created_at": datetime.now().isoformat()
    }

    state.setdefault("directives", []).append(directive)
    save_state(state)

    return directive


def update_directive_status(directive_id: str, status: str, notes: str = ""):
    """Update the status of a directive"""
    state = load_state()

    for directive in state.get("directives", []):
        if directive.get("id") == directive_id:
            directive["status"] = status
            directive["updated_at"] = datetime.now().isoformat()
            if notes:
                directive["notes"] = notes
            break

    save_state(state)


def sync_from_gmail(messages: List[Dict]):
    """Bulk update state from Gmail inbox fetch"""
    state = load_state()

    for msg in messages:
        msg_id = msg.get("id") or msg.get("message_id")
        if not msg_id:
            continue

        if msg_id not in state.get("messages", {}):
            state.setdefault("messages", {})[msg_id] = {
                "status": "new",
                "from": msg.get("from", ""),
                "subject": msg.get("subject", ""),
                "date": msg.get("date", datetime.now().isoformat()),
                "preview": msg.get("body", "")[:200] if msg.get("body") else "",
                "thread_id": msg.get("thread_id"),
                "is_from_jared": is_from_jared(msg.get("from", "")),
                "added_at": datetime.now().isoformat()
            }

    save_state(state)


def get_stats() -> dict:
    """Get quick stats for BOOP/wake-up checks"""
    state = load_state()
    return state.get("stats", compute_stats(state))


def get_new_messages() -> List[Dict]:
    """Get all messages with status 'new'"""
    state = load_state()
    return [
        {"msg_id": msg_id, **msg}
        for msg_id, msg in state.get("messages", {}).items()
        if msg.get("status") == "new"
    ]


def get_unprocessed_directives() -> List[Dict]:
    """Get all unprocessed directives"""
    state = load_state()
    return [
        d for d in state.get("directives", [])
        if d.get("status") in ["unprocessed", "in_progress"]
    ]


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Email State Management")
    parser.add_argument("command", choices=["stats", "new", "directives", "init", "reset"],
                        help="Command to run")

    args = parser.parse_args()

    if args.command == "stats":
        stats = get_stats()
        print(f"\n📊 Email State Stats:")
        print(f"  New: {stats['new_count']}")
        print(f"  New from Jared: {stats['new_from_jared']} {'⚠️' if stats['new_from_jared'] > 0 else ''}")
        print(f"  Seen: {stats['seen_count']}")
        print(f"  Responded: {stats['responded_count']}")
        print(f"  Ignored: {stats['ignored_count']}")
        print(f"  Archived: {stats['archived_count']}")
        print(f"  Unprocessed directives: {stats['unprocessed_directives']} {'⚠️' if stats['unprocessed_directives'] > 3 else ''}")

    elif args.command == "new":
        messages = get_new_messages()
        print(f"\n📬 New Messages ({len(messages)}):")
        for msg in messages[:10]:
            jared_flag = "⭐" if msg.get("is_from_jared") else ""
            print(f"  {jared_flag} {msg['from'][:30]}... - {msg['subject'][:40]}...")

    elif args.command == "directives":
        directives = get_unprocessed_directives()
        print(f"\n📋 Unprocessed Directives ({len(directives)}):")
        for d in directives:
            print(f"  [{d['priority'].upper()}] {d['text'][:60]}... ({d['status']})")

    elif args.command == "init":
        state = initialize_state()
        save_state(state)
        print("Email state initialized")

    elif args.command == "reset":
        confirm = input("Are you sure you want to reset all email state? (yes/no): ")
        if confirm.lower() == "yes":
            state = initialize_state()
            save_state(state)
            print("Email state reset")
        else:
            print("Reset cancelled")


if __name__ == "__main__":
    main()
