#!/usr/bin/env python3
"""
Aether Telegram Bridge

Bidirectional communication bridge between Jared and Aether via Telegram.
- Receives messages from Jared on Telegram
- Injects them into the active Claude Code session via tmux
- Monitors for responses wrapped in emoji markers

Usage:
    python3 tools/telegram_bridge.py

Run in background:
    nohup python3 tools/telegram_bridge.py >> /tmp/aether_telegram_bridge.log 2>&1 &
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


class TelegramBridge:
    def __init__(self):
        self.config = self.load_config()
        self.bot_token = self.config["bot_token"]
        self.authorized_users = self.config["authorized_users"]
        self.last_update_id = 0
        self.session_file = Path(__file__).parent.parent / ".current_session"

    def load_config(self):
        """Load config from file"""
        config_path = Path(__file__).parent.parent / "config" / "telegram_config.json"
        with open(config_path) as f:
            return json.load(f)

    def is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized"""
        return str(user_id) in self.authorized_users

    def get_user_name(self, user_id: str) -> str:
        """Get user's name from config"""
        user = self.authorized_users.get(str(user_id), {})
        return user.get("name", "Unknown")

    async def get_updates(self, client: httpx.AsyncClient) -> list:
        """Get new messages from Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30,
            "allowed_updates": ["message"]
        }

        try:
            response = await client.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data.get("result", [])
        except Exception as e:
            print(f"[{datetime.now()}] Error getting updates: {e}")

        return []

    async def send_message(self, client: httpx.AsyncClient, chat_id: str, text: str):
        """Send a message back to Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text
        }

        try:
            response = await client.post(url, json=data, timeout=30)
            if response.status_code != 200:
                print(f"[{datetime.now()}] Error sending message: {response.text}")
        except Exception as e:
            print(f"[{datetime.now()}] Error sending message: {e}")

    async def download_file(self, client: httpx.AsyncClient, file_id: str) -> bytes:
        """Download a file from Telegram"""
        # Get file path
        url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
        params = {"file_id": file_id}

        try:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"[{datetime.now()}] Error getting file path: {response.text}")
                return None

            data = response.json()
            if not data.get("ok"):
                return None

            file_path = data.get("result", {}).get("file_path")
            if not file_path:
                return None

            # Download the file
            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            response = await client.get(file_url, timeout=60)

            if response.status_code == 200:
                return response.content
            else:
                print(f"[{datetime.now()}] Error downloading file: {response.status_code}")
                return None

        except Exception as e:
            print(f"[{datetime.now()}] Error downloading file: {e}")
            return None

    async def handle_document(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming document/file"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        document = message.get("document", {})

        file_name = document.get("file_name", "unknown_file")
        file_id = document.get("file_id")
        file_size = document.get("file_size", 0)

        # Log the document
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Document from {user_id}: {file_name} ({file_size} bytes)")

        # Check authorization
        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for Jared only."
            )
            return

        sender = self.get_user_name(user_id)

        # Download the file
        await self.send_message(client, chat_id, f"📥 Downloading {file_name}...")

        file_content = await self.download_file(client, file_id)
        if not file_content:
            await self.send_message(client, chat_id, "❌ Failed to download file")
            return

        # Save to docs folder
        docs_path = Path(__file__).parent.parent / "docs" / "from-telegram"
        docs_path.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_name = "".join(c for c in file_name if c.isalnum() or c in ".-_ ")
        file_path = docs_path / safe_name

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)

            print(f"[{timestamp}] Saved to: {file_path}")

            # Notify via tmux
            session = self.get_current_session()
            if session:
                notification = f"📄 File received from {sender}: {file_name}\nSaved to: {file_path}"
                self.inject_to_session(session, notification, "System")

            await self.send_message(
                client, chat_id,
                f"✅ Saved to: docs/from-telegram/{safe_name}\n\nI can now read this file!"
            )

        except Exception as e:
            print(f"[{timestamp}] Error saving file: {e}")
            await self.send_message(client, chat_id, f"❌ Error saving file: {e}")

    def get_current_session(self) -> str:
        """Get the current tmux session name"""
        if self.session_file.exists():
            return self.session_file.read_text().strip()

        # Try to find an aether session
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True
            )
            sessions = result.stdout.strip().split('\n')
            for session in sessions:
                if 'aether' in session.lower() or 'primary' in session.lower():
                    return session
        except Exception:
            pass

        return None

    def inject_to_session(self, session: str, message: str, sender: str) -> bool:
        """Inject message into tmux session with 5x Enter retries for reliability.

        AICIV Standard Pattern: 5x Enter retries with 0.3s delay ensures Claude
        processes the injected message. This is mandatory for ALL prompt injection.
        """
        import time
        try:
            # Format the message for injection
            formatted = f"\n[Telegram from {sender}]: {message}\n"

            # Use tmux send-keys to inject the message with initial Enter
            subprocess.run(
                ["tmux", "send-keys", "-t", session, formatted, "Enter"],
                check=True,
                capture_output=True
            )

            # 5x Enter retries to ensure Claude processes the message
            # AICIV standard: 0.5s delays for reliability (per Corey directive 2026-01-30)
            for i in range(5):
                time.sleep(0.5)
                subprocess.run(
                    ["tmux", "send-keys", "-t", session, "Enter"],
                    capture_output=True
                )

            print(f"[{datetime.now()}] Injected to {session} with 5x Enter retries")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Error injecting to session: {e}")
            return False

    async def handle_message(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming message"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "")

        # Log the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Message from {user_id}: {text[:50]}...")

        # Check authorization
        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for Jared only."
            )
            return

        sender = self.get_user_name(user_id)

        # Get current session
        session = self.get_current_session()

        if not session:
            await self.send_message(
                client, chat_id,
                "Aether session not currently active. Message logged but not delivered to live session."
            )
            # Log to a file for later
            log_path = Path(__file__).parent.parent / "logs" / "telegram_pending.log"
            log_path.parent.mkdir(exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"[{timestamp}] {sender}: {text}\n")
            return

        # Inject to session
        if self.inject_to_session(session, text, sender):
            await self.send_message(
                client, chat_id,
                f"Message delivered to Aether session: {session}"
            )
        else:
            await self.send_message(
                client, chat_id,
                "Failed to deliver message to session. Please try again."
            )

    async def run(self):
        """Main loop"""
        print(f"[{datetime.now()}] Aether Telegram Bridge starting...")
        print(f"[{datetime.now()}] Authorized users: {list(self.authorized_users.keys())}")

        async with httpx.AsyncClient() as client:
            # Send startup message
            default_chat = self.config.get("default_chat_id")
            if default_chat:
                await self.send_message(
                    client, default_chat,
                    "Aether Telegram Bridge online. I can receive your messages now."
                )

            while True:
                updates = await self.get_updates(client)

                for update in updates:
                    self.last_update_id = update.get("update_id", self.last_update_id)

                    message = update.get("message")
                    if message:
                        # Handle text messages
                        if message.get("text"):
                            await self.handle_message(client, message)
                        # Handle documents/files
                        elif message.get("document"):
                            await self.handle_document(client, message)

                # Small delay between polls
                await asyncio.sleep(1)


def main():
    bridge = TelegramBridge()

    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Bridge stopped by user")
    except Exception as e:
        print(f"[{datetime.now()}] Bridge error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
