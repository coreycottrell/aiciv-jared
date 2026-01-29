#!/usr/bin/env python3
"""
Aether Telegram Message Sender

Send messages to Jared via Telegram.

Usage:
    python3 tools/send_telegram.py "Your message here"
    python3 tools/send_telegram.py --chat_id 548906264 "Message to specific chat"
"""

import sys
import json
import argparse
from pathlib import Path
import requests


def load_config():
    """Load Telegram config from config/telegram_config.json"""
    config_path = Path(__file__).parent.parent / "config" / "telegram_config.json"
    if not config_path.exists():
        print(f"Error: Config not found at {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)


def send_message(message: str, chat_id: str = None) -> bool:
    """Send a message via Telegram Bot API"""
    config = load_config()

    bot_token = config["bot_token"]
    chat_id = chat_id or config["default_chat_id"]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Split long messages
    max_length = config.get("settings", {}).get("max_message_length", 4096)

    messages = []
    if len(message) > max_length:
        # Split at line boundaries
        lines = message.split('\n')
        current_chunk = ""
        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_length:
                if current_chunk:
                    messages.append(current_chunk)
                current_chunk = line
            else:
                current_chunk = current_chunk + '\n' + line if current_chunk else line
        if current_chunk:
            messages.append(current_chunk)
    else:
        messages = [message]

    success = True
    for i, msg in enumerate(messages):
        if len(messages) > 1:
            msg = f"({i+1}/{len(messages)})\n{msg}"

        data = {
            "chat_id": chat_id,
            "text": msg
        }

        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                success = False
            else:
                result = response.json()
                if not result.get("ok"):
                    print(f"Error: {result}")
                    success = False
        except Exception as e:
            print(f"Error sending message: {e}")
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="Send Telegram message")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--chat_id", help="Target chat ID (default: from config)")

    args = parser.parse_args()

    success = send_message(args.message, args.chat_id)

    if success:
        print("Message sent successfully")
        sys.exit(0)
    else:
        print("Failed to send message")
        sys.exit(1)


if __name__ == "__main__":
    main()
