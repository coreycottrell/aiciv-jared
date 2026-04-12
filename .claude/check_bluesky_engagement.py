#!/usr/bin/env python3
"""
Bluesky Engagement Checker
Checks notifications, replies, likes, reposts for recent posts (thread about "Why Your AI Should Have a Name")
"""

from atproto import Client
from datetime import datetime, timezone, timedelta
import os
import sys
from pathlib import Path

# Configuration
SESSION_FILE = Path('/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt')
RESPONDED_FILE = Path('/home/jared/projects/AI-CIV/aether/.claude/bsky_responded.txt')
LAST_CHECK_FILE = Path('/home/jared/projects/AI-CIV/aether/.claude/bsky_last_check.txt')

def main():
    # Restore session
    client = Client()
    try:
        with open(SESSION_FILE, 'r') as f:
            client.login(session_string=f.read().strip())
        print(f"✓ Session restored: @{client.me.handle}")
    except FileNotFoundError:
        print(f"✗ Session file not found: {SESSION_FILE}")
        return 1
    except Exception as e:
        print(f"✗ Session restore failed: {e}")
        return 1

    print(f"\n=== Checking Engagement for @{client.me.handle} ===\n")

    # Get notifications
    try:
        notifs = client.app.bsky.notification.list_notifications({'limit': 100})
        print(f"✓ Retrieved {len(notifs.notifications)} notifications\n")
    except Exception as e:
        print(f"✗ Failed to get notifications: {e}")
        return 1

    # Parse engagement by type
    engagement = {
        'reply': [],
        'mention': [],
        'like': [],
        'repost': [],
        'quote': []
    }

    for notif in notifs.notifications:
        reason = notif.reason
        if reason in engagement:
            engagement[reason].append(notif)

    # Load already responded
    responded = load_responded()

    # Report engagement
    print("=== ENGAGEMENT SUMMARY ===\n")
    print(f"Total notifications: {len(notifs.notifications)}")
    print(f"  Replies: {len(engagement['reply'])}")
    print(f"  Mentions: {len(engagement['mention'])}")
    print(f"  Likes: {len(engagement['like'])}")
    print(f"  Reposts: {len(engagement['repost'])}")
    print(f"  Quote Shares: {len(engagement['quote'])}")

    # Show recent engagement details (last 24 hours)
    print("\n=== RECENT ENGAGEMENT (last 24h) ===\n")
    now = datetime.now(timezone.utc)
    recent_count = 0

    for reason_type in ['reply', 'mention', 'quote', 'repost', 'like']:
        notifs_list = engagement[reason_type]
        if not notifs_list:
            continue

        print(f"\n{reason_type.upper()}S:")
        for notif in notifs_list[:5]:  # Show top 5 of each type
            indexed = datetime.fromisoformat(notif.indexed_at.replace('Z', '+00:00'))
            age = now - indexed
            if age > timedelta(hours=24):
                continue

            recent_count += 1
            age_str = format_age(age)
            text = getattr(notif.record, 'text', '(no text)')[:60]

            print(f"  @{notif.author.handle} ({age_str})")
            if notif.reason == 'reply':
                print(f"    Reply: {text}")
            elif notif.reason == 'mention':
                print(f"    Mentioned you: {text}")
            elif notif.reason == 'quote':
                print(f"    Quote shared: {text}")
            elif notif.reason == 'repost':
                print(f"    Reposted")
            elif notif.reason == 'like':
                print(f"    Liked")

            # Check if we've responded
            if notif.uri in responded:
                print(f"    ✓ Already responded")
            else:
                print(f"    → ACTION: Can respond")

    print(f"\n=== SUMMARY ===")
    print(f"Recent engagement (24h): {recent_count}")
    print(f"Already responded to: {len(responded)}")

    # Update last check
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(datetime.now(timezone.utc).isoformat())
    print(f"✓ Last check timestamp updated")

    return 0


def load_responded():
    """Load URIs we've already responded to."""
    responded = set()
    if RESPONDED_FILE.exists():
        with open(RESPONDED_FILE, 'r') as f:
            responded = set(line.strip() for line in f if line.strip())
    return responded


def format_age(delta):
    """Format timedelta as human-readable string."""
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s ago"
    elif total_seconds < 3600:
        return f"{total_seconds//60}m ago"
    elif total_seconds < 86400:
        return f"{total_seconds//3600}h ago"
    else:
        return f"{total_seconds//86400}d ago"


if __name__ == '__main__':
    sys.exit(main())
