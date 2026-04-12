#!/usr/bin/env python3
"""
Get Telegram Group Chat ID Helper

Run this script, then send a message in the target group.
The script will print the group's chat_id.

Usage:
    python3 tools/get_telegram_group_id.py

Press Ctrl+C to exit after getting the ID.
"""

import json
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


def main():
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "telegram_config.json"
    with open(config_path) as f:
        config = json.load(f)

    bot_token = config["bot_token"]
    last_update_id = 0

    print("=" * 60)
    print("Telegram Group ID Finder")
    print("=" * 60)
    print()
    print("Send a message in the target Telegram group.")
    print("The group's chat_id will be printed below.")
    print()
    print("Press Ctrl+C to exit.")
    print()
    print("-" * 60)

    with httpx.Client() as client:
        while True:
            try:
                url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                params = {
                    "offset": last_update_id + 1,
                    "timeout": 30,
                    "allowed_updates": ["message"]
                }

                response = client.get(url, params=params, timeout=35)
                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    continue

                data = response.json()
                if not data.get("ok"):
                    continue

                for update in data.get("result", []):
                    last_update_id = update.get("update_id", last_update_id)

                    message = update.get("message", {})
                    chat = message.get("chat", {})
                    chat_type = chat.get("type", "")
                    chat_id = chat.get("id")
                    chat_title = chat.get("title", "")

                    if chat_type in ["group", "supergroup"]:
                        print()
                        print("=" * 60)
                        print(f"GROUP FOUND!")
                        print(f"  Name: {chat_title}")
                        print(f"  Type: {chat_type}")
                        print(f"  Chat ID: {chat_id}")
                        print("=" * 60)
                        print()
                        print(f"Add this to your config/telegram_config.json:")
                        print(f'  "enabled_groups": ["{chat_id}"]')
                        print()
                        print("-" * 60)
                    elif chat_type == "private":
                        user = message.get("from", {})
                        print(f"  (DM from {user.get('first_name', 'Unknown')}, chat_id: {chat_id})")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
