#!/usr/bin/env python3
"""
Aether Telegram Bridge v3 - WITH GROUP CHAT SUPPORT

Bidirectional communication bridge between Jared and Aether via Telegram.
NOW SUPPORTS:
- Direct messages (existing functionality)
- Group chats (NEW - bot participates as team member)

Group Chat Features:
- Monitor group conversations
- Respond to @mentions, /commands, and keywords
- Participate like a team member
- Configurable triggers per group

Usage:
    python3 tools/telegram_bridge_v3_groups.py

Run in background:
    nohup python3 tools/telegram_bridge_v3_groups.py >> /tmp/aether_telegram_bridge.log 2>&1 &
"""

import sys
# Force unbuffered output for logging
sys.stdout = sys.stderr = open(sys.stdout.fileno(), mode='w', buffering=1)

import asyncio
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


class TelegramBridge:
    def __init__(self):
        self.config = self.load_config()
        self.bot_token = self.config["bot_token"]
        self.bot_username = self.config.get("bot_username", "aether_aicivbot")
        self.authorized_users = self.config["authorized_users"]
        self.last_update_id = 0
        self.project_root = Path(__file__).parent.parent
        self.session_file = self.project_root / ".current_session"
        self.inbox_dir = self.project_root / "inbox"

        # Group chat settings
        self.group_settings = self.config.get("group_settings", {})
        self.enabled_groups = set(str(g) for g in self.group_settings.get("enabled_groups", []))
        self.group_triggers = self.group_settings.get("triggers", [f"@{self.bot_username}", "/ask", "/aether", "hey aether"])
        self.monitor_all_messages = self.group_settings.get("monitor_all", False)
        self.group_contexts = defaultdict(list)  # Store recent messages per group for context
        self.max_context_messages = 20

        # Output monitoring state - MARKER-BASED
        self.last_sender_chat_id = self.config.get("default_chat_id", "548906264")
        self.last_sender_is_group = False  # Track if last sender was from a group
        self.last_message_id = None  # For threading replies in groups
        self.sent_responses = set()
        self.last_pane_content = ""

        # Response markers
        self.START_MARKER = "\U0001f916\U0001f3af\U0001f4f1"  # Robot, target, phone emojis
        self.END_MARKER = "\u2728\U0001f51a"  # Sparkles, end emojis

        # Ensure directories exist
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Load config from file"""
        config_path = Path(__file__).parent.parent / "config" / "telegram_config.json"
        with open(config_path) as f:
            return json.load(f)

    def is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized (for DMs)"""
        return str(user_id) in self.authorized_users

    def is_group_enabled(self, chat_id: str) -> bool:
        """Check if a group is enabled for bot participation"""
        return str(chat_id) in self.enabled_groups

    def get_user_name(self, user_id: str) -> str:
        """Get user's name from config"""
        user = self.authorized_users.get(str(user_id), {})
        return user.get("name", "Unknown")

    def is_tmux_available(self) -> bool:
        """Check if tmux server is running"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def should_respond_to_group_message(self, text: str, message: dict) -> bool:
        """
        Determine if bot should respond to a group message.

        Triggers:
        - @mention of bot
        - /ask or /aether commands
        - Keywords like "hey aether"
        - Reply to bot's previous message
        """
        if not text:
            return False

        text_lower = text.lower()

        # Check for @mention
        if f"@{self.bot_username.lower()}" in text_lower:
            return True

        # Check for configured triggers
        for trigger in self.group_triggers:
            if trigger.lower() in text_lower:
                return True

        # Check if replying to bot's message
        reply_to = message.get("reply_to_message", {})
        reply_from = reply_to.get("from", {})
        if reply_from.get("username", "").lower() == self.bot_username.lower():
            return True

        # If monitor_all is enabled and user is authorized, respond to everything
        if self.monitor_all_messages:
            user_id = str(message.get("from", {}).get("id", ""))
            if self.is_authorized(user_id):
                return True

        return False

    def store_group_context(self, chat_id: str, username: str, text: str):
        """Store message in group context for conversation awareness"""
        timestamp = datetime.now().isoformat()
        self.group_contexts[chat_id].append({
            "username": username,
            "text": text,
            "timestamp": timestamp
        })

        # Keep only last N messages
        if len(self.group_contexts[chat_id]) > self.max_context_messages:
            self.group_contexts[chat_id] = self.group_contexts[chat_id][-self.max_context_messages:]

    def get_group_context_summary(self, chat_id: str) -> str:
        """Get a summary of recent group conversation for context"""
        messages = self.group_contexts.get(chat_id, [])
        if not messages:
            return "No recent conversation history."

        lines = ["Recent conversation:"]
        for msg in messages[-10:]:  # Last 10 messages
            lines.append(f"  {msg['username']}: {msg['text'][:100]}")
        return "\n".join(lines)

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

    async def send_message(self, client: httpx.AsyncClient, chat_id: str, text: str,
                          reply_to_message_id: int = None):
        """Send a message to Telegram (DM or group)"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text
        }

        # Thread the reply in groups
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        try:
            response = await client.post(url, json=data, timeout=30)
            if response.status_code != 200:
                print(f"[{datetime.now()}] Error sending message: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"[{datetime.now()}] Error sending message: {e}")
            return False

    async def download_file(self, client: httpx.AsyncClient, file_id: str) -> bytes:
        """Download a file from Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
        params = {"file_id": file_id}

        try:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code != 200:
                return None

            data = response.json()
            if not data.get("ok"):
                return None

            file_path = data.get("result", {}).get("file_path")
            if not file_path:
                return None

            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            response = await client.get(file_url, timeout=60)

            if response.status_code == 200:
                return response.content
            return None

        except Exception as e:
            print(f"[{datetime.now()}] Error downloading file: {e}")
            return None

    def get_current_session(self) -> str:
        """Get the current tmux session name"""
        if self.session_file.exists():
            return self.session_file.read_text().strip()

        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                sessions = result.stdout.strip().split('\n')
                for session in sessions:
                    if 'aether' in session.lower() or 'primary' in session.lower():
                        return session
        except Exception:
            pass

        return None

    def inject_to_session(self, session: str, message: str, sender: str,
                         is_group: bool = False, group_name: str = None) -> bool:
        """Inject message into tmux session with context about source"""
        import time
        try:
            # Format with source info
            if is_group:
                formatted = f"\n[Telegram GROUP ({group_name}) - {sender}]: {message}\n"
            else:
                formatted = f"\n[Telegram DM from {sender}]: {message}\n"

            subprocess.run(
                ["tmux", "send-keys", "-t", session, formatted, "Enter"],
                check=True,
                capture_output=True
            )

            # 5x Enter retries for reliability
            for i in range(5):
                time.sleep(0.5)
                subprocess.run(
                    ["tmux", "send-keys", "-t", session, "Enter"],
                    capture_output=True
                )

            print(f"[{datetime.now()}] Injected to {session} (group={is_group})")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Error injecting to session: {e}")
            return False

    def capture_pane_content(self, session: str) -> str:
        """Capture the current content of the tmux pane"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session, "-p", "-S", "-500"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            print(f"[{datetime.now()}] Error capturing pane: {e}")
        return ""

    def extract_responses(self, content: str) -> list:
        """Extract all responses wrapped in markers from pane content"""
        responses = []

        pattern = re.escape(self.START_MARKER) + r"(.*?)" + re.escape(self.END_MARKER)
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            response = match.strip()
            if response and len(response) > 5:
                response_hash = hash(response[:200])
                if response_hash not in self.sent_responses:
                    responses.append((response, response_hash))

        return responses

    async def monitor_output(self, client: httpx.AsyncClient):
        """Monitor tmux pane for marker-wrapped responses and send to Telegram"""
        while True:
            try:
                session = self.get_current_session()
                if session and self.is_tmux_available():
                    content = self.capture_pane_content(session)

                    if content != self.last_pane_content:
                        self.last_pane_content = content
                        responses = self.extract_responses(content)

                        for response, response_hash in responses:
                            if len(response) > 4000:
                                response = response[:3900] + "\n\n... [truncated]"

                            # Send with threading for groups
                            await self.send_message(
                                client,
                                self.last_sender_chat_id,
                                response,
                                reply_to_message_id=self.last_message_id if self.last_sender_is_group else None
                            )

                            self.sent_responses.add(response_hash)
                            print(f"[{datetime.now()}] Sent response to {self.last_sender_chat_id} (group={self.last_sender_is_group}, {len(response)} chars)")

                            if len(self.sent_responses) > 1000:
                                self.sent_responses = set(list(self.sent_responses)[-500:])

            except Exception as e:
                print(f"[{datetime.now()}] Output monitor error: {e}")

            await asyncio.sleep(2)

    def write_to_inbox(self, message: str, sender: str, is_group: bool = False, group_name: str = None) -> str:
        """Write message to inbox folder as fallback"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        source = f"group-{group_name}" if is_group else "dm"
        filename = f"telegram-{source}-{timestamp}.txt"
        filepath = self.inbox_dir / filename

        content = f"""# Telegram Message from {sender}
# Source: {"Group: " + group_name if is_group else "Direct Message"}
# Received: {datetime.now().isoformat()}
# Via: Aether Telegram Bridge (file fallback)

{message}

---
Note: This message was saved to file because Claude is not running in tmux.
"""

        filepath.write_text(content)
        print(f"[{datetime.now()}] Written to inbox: {filepath}")
        return str(filepath)

    async def handle_group_message(self, client: httpx.AsyncClient, message: dict):
        """Handle a message from a group chat"""
        user_id = str(message.get("from", {}).get("id", ""))
        username = message.get("from", {}).get("username", "Unknown")
        first_name = message.get("from", {}).get("first_name", username)
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        chat_title = chat.get("title", "Unknown Group")
        chat_type = chat.get("type", "")  # 'group' or 'supergroup'
        text = message.get("text", "")
        message_id = message.get("message_id")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] GROUP [{chat_title}] {first_name}: {text[:50]}...")

        # Check if group is enabled
        if not self.is_group_enabled(chat_id):
            print(f"[{timestamp}] Group {chat_id} not in enabled_groups, ignoring")
            return

        # Store in context regardless of whether we respond
        self.store_group_context(chat_id, first_name, text)

        # Check if we should respond
        if not self.should_respond_to_group_message(text, message):
            print(f"[{timestamp}] No trigger detected, logging only")
            return

        # Track for response routing
        self.last_sender_chat_id = chat_id
        self.last_sender_is_group = True
        self.last_message_id = message_id

        # Clean the message (remove @mention if present)
        clean_text = text.replace(f"@{self.bot_username}", "").strip()
        clean_text = re.sub(r'^/(ask|aether)\s*', '', clean_text).strip()

        # Add context about the group conversation
        context_summary = self.get_group_context_summary(chat_id)

        # Format message for injection
        full_message = f"""MESSAGE CONTEXT:
- From: {first_name} (@{username})
- Group: {chat_title}
- User authorized: {self.is_authorized(user_id)}

{context_summary}

ACTUAL MESSAGE: {clean_text}"""

        # Check tmux availability
        if not self.is_tmux_available():
            filepath = self.write_to_inbox(full_message, first_name, is_group=True, group_name=chat_title)
            await self.send_message(
                client, chat_id,
                f"Aether is not currently active. Message logged for later.",
                reply_to_message_id=message_id
            )
            return

        session = self.get_current_session()
        if not session:
            filepath = self.write_to_inbox(full_message, first_name, is_group=True, group_name=chat_title)
            await self.send_message(
                client, chat_id,
                f"No active Aether session. Message logged.",
                reply_to_message_id=message_id
            )
            return

        # Inject to session
        if self.inject_to_session(session, full_message, first_name, is_group=True, group_name=chat_title):
            # Send acknowledgment (optional - can be disabled)
            if self.group_settings.get("send_acknowledgment", True):
                await self.send_message(
                    client, chat_id,
                    "Processing...",
                    reply_to_message_id=message_id
                )
        else:
            filepath = self.write_to_inbox(full_message, first_name, is_group=True, group_name=chat_title)
            await self.send_message(
                client, chat_id,
                "Failed to reach Aether. Message logged.",
                reply_to_message_id=message_id
            )

    async def handle_dm_message(self, client: httpx.AsyncClient, message: dict):
        """Handle a direct message (existing functionality)"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] DM from {user_id}: {text[:50]}...")

        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for authorized users only."
            )
            return

        # Track for response routing
        self.last_sender_chat_id = chat_id
        self.last_sender_is_group = False
        self.last_message_id = None

        sender = self.get_user_name(user_id)

        if not self.is_tmux_available():
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"Aether is not running in tmux. Message saved to:\n{filepath}"
            )
            return

        session = self.get_current_session()
        if not session:
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"No active Aether session found. Message saved to:\n{filepath}"
            )
            return

        if self.inject_to_session(session, text, sender):
            await self.send_message(
                client, chat_id,
                f"Delivered to Aether session: {session}"
            )
        else:
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"Failed to inject to tmux. Message saved to:\n{filepath}"
            )

    async def handle_document(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming document/file (works for both DM and groups)"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        chat_type = chat.get("type", "private")
        is_group = chat_type in ["group", "supergroup"]

        document = message.get("document", {})
        file_name = document.get("file_name", "unknown_file")
        file_id = document.get("file_id")
        file_size = document.get("file_size", 0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Document from {user_id}: {file_name} ({file_size} bytes)")

        # For groups, check if group is enabled
        if is_group and not self.is_group_enabled(chat_id):
            return

        # For DMs, check authorization
        if not is_group and not self.is_authorized(user_id):
            await self.send_message(client, chat_id, "Unauthorized.")
            return

        sender = self.get_user_name(user_id) if self.is_authorized(user_id) else message.get("from", {}).get("first_name", "Unknown")

        await self.send_message(client, chat_id, f"Downloading {file_name}...")

        file_content = await self.download_file(client, file_id)
        if not file_content:
            await self.send_message(client, chat_id, "Failed to download file")
            return

        docs_path = self.project_root / "docs" / "from-telegram"
        docs_path.mkdir(parents=True, exist_ok=True)

        safe_name = "".join(c for c in file_name if c.isalnum() or c in ".-_ ")
        file_path = docs_path / safe_name

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)

            print(f"[{timestamp}] Saved to: {file_path}")

            session = self.get_current_session()
            if session and self.is_tmux_available():
                notification = f"File received from {sender}: {file_name}\nSaved to: {file_path}"
                self.inject_to_session(session, notification, "System")
            else:
                self.write_to_inbox(
                    f"FILE RECEIVED from {sender}: {file_name}\nSaved to: {file_path}",
                    sender,
                    is_group=is_group
                )

            await self.send_message(
                client, chat_id,
                f"Saved to: docs/from-telegram/{safe_name}\n\nAether can now read this file!"
            )

        except Exception as e:
            print(f"[{timestamp}] Error saving file: {e}")
            await self.send_message(client, chat_id, f"Error saving file: {e}")

    async def handle_command(self, client: httpx.AsyncClient, message: dict):
        """Handle bot commands (works in both DMs and groups)"""
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))
        chat_type = message.get("chat", {}).get("type", "private")
        is_group = chat_type in ["group", "supergroup"]
        message_id = message.get("message_id")

        command = text.split()[0].lower().replace(f"@{self.bot_username.lower()}", "")

        if command == "/help":
            help_text = """Aether Bot Commands:

/help - Show this help message
/status - Check Aether's status
/ask [question] - Ask Aether a question
/context - Show recent conversation context (groups only)

In groups, you can also:
- @mention me to get my attention
- Say "hey aether" to trigger a response
- Reply to my messages to continue a conversation"""

            await self.send_message(client, chat_id, help_text,
                                   reply_to_message_id=message_id if is_group else None)
            return True

        elif command == "/status":
            tmux_status = "ONLINE" if self.is_tmux_available() else "OFFLINE"
            session = self.get_current_session() or "None"
            status_text = f"""Aether Status:
- Bridge: Online
- tmux: {tmux_status}
- Session: {session}
- Groups enabled: {len(self.enabled_groups)}"""

            await self.send_message(client, chat_id, status_text,
                                   reply_to_message_id=message_id if is_group else None)
            return True

        elif command == "/context" and is_group:
            context = self.get_group_context_summary(chat_id)
            await self.send_message(client, chat_id, context,
                                   reply_to_message_id=message_id)
            return True

        return False  # Not a handled command

    async def poll_updates(self, client: httpx.AsyncClient):
        """Poll for incoming Telegram messages"""
        while True:
            updates = await self.get_updates(client)

            for update in updates:
                self.last_update_id = update.get("update_id", self.last_update_id)

                message = update.get("message")
                if message:
                    chat_type = message.get("chat", {}).get("type", "private")
                    is_group = chat_type in ["group", "supergroup"]
                    text = message.get("text", "")

                    # Handle commands first (they start with /)
                    if text.startswith("/"):
                        handled = await self.handle_command(client, message)
                        if handled:
                            continue

                    # Handle documents
                    if message.get("document"):
                        await self.handle_document(client, message)
                        continue

                    # Handle text messages
                    if text:
                        if is_group:
                            await self.handle_group_message(client, message)
                        else:
                            await self.handle_dm_message(client, message)

            await asyncio.sleep(1)

    async def run(self):
        """Main loop - runs input polling and output monitoring concurrently"""
        print(f"[{datetime.now()}] Aether Telegram Bridge v3 (WITH GROUPS) starting...")
        print(f"[{datetime.now()}] Authorized users: {list(self.authorized_users.keys())}")
        print(f"[{datetime.now()}] Enabled groups: {list(self.enabled_groups)}")
        print(f"[{datetime.now()}] Group triggers: {self.group_triggers}")
        print(f"[{datetime.now()}] Inbox fallback: {self.inbox_dir}")

        if self.is_tmux_available():
            print(f"[{datetime.now()}] tmux: AVAILABLE")
        else:
            print(f"[{datetime.now()}] tmux: NOT AVAILABLE - will use inbox fallback")

        async with httpx.AsyncClient() as client:
            default_chat = self.config.get("default_chat_id")
            if default_chat:
                tmux_status = "tmux available" if self.is_tmux_available() else "using inbox fallback"
                await self.send_message(
                    client, default_chat,
                    f"Aether TG Bridge v3 (WITH GROUPS) online.\n"
                    f"Status: {tmux_status}\n"
                    f"Groups enabled: {len(self.enabled_groups)}\n"
                    f"Commands: /help, /status, /ask"
                )

            await asyncio.gather(
                self.poll_updates(client),
                self.monitor_output(client)
            )


def main():
    bridge = TelegramBridge()

    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Bridge stopped by user")
    except Exception as e:
        error_msg = f"[{datetime.now()}] Bridge error: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
