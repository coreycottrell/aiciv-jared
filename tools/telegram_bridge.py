#!/usr/bin/env python3
"""
Aether Telegram Bridge v3 - Context Aware
"""
import sys
# Force unbuffered output for logging
sys.stdout = sys.stderr = open(sys.stdout.fileno(), mode='w', buffering=1)
"""

Bidirectional communication bridge between Jared and Aether via Telegram.
- Receives messages from Jared on Telegram
- Injects them into the active Claude Code session via tmux (when available)
- FALLBACK: Writes to inbox/ folder when tmux not available
- Monitors for responses wrapped in emoji markers
- CONTEXT AWARE: Can answer "what are you working on?" from scratch-pad.md

Usage:
    python3 tools/telegram_bridge.py

Run in background:
    nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &
"""

import asyncio
import json
import sys
import subprocess
import re
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
        self.project_root = Path(__file__).parent.parent
        self.session_file = self.project_root / ".current_session"
        self.inbox_dir = self.project_root / "inbox"

        # PID file for single-instance enforcement
        self.pid_file = self.project_root / ".telegram_bridge.pid"

        # Persistent sent_responses file (survives restarts)
        self.sent_responses_file = self.project_root / ".telegram_sent_hashes.json"

        # Output monitoring state - MARKER-BASED
        self.last_sender_chat_id = self.config.get("default_chat_id", "548906264")
        self.sent_responses = self.load_sent_responses()  # Load from file
        self.last_pane_content = ""

        # Response markers - Aether wraps ALL output in these
        self.START_MARKER = "🤖🎯📱"
        self.END_MARKER = "✨🔚"

        # Ensure inbox exists
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def check_single_instance(self) -> bool:
        """Ensure only one bridge instance runs. Returns True if we can proceed."""
        import os
        import signal

        if self.pid_file.exists():
            try:
                old_pid = int(self.pid_file.read_text().strip())
                # Check if process is actually running
                os.kill(old_pid, 0)  # Signal 0 = check existence
                print(f"[{datetime.now()}] ERROR: Bridge already running (PID {old_pid})")
                return False
            except (ProcessLookupError, ValueError):
                # Process not running or invalid PID - clean up stale file
                print(f"[{datetime.now()}] Cleaning stale PID file")
                self.pid_file.unlink(missing_ok=True)

        # Write our PID
        self.pid_file.write_text(str(os.getpid()))
        print(f"[{datetime.now()}] PID file created: {os.getpid()}")
        return True

    def cleanup_pid(self):
        """Remove PID file on exit"""
        self.pid_file.unlink(missing_ok=True)

    def load_sent_responses(self) -> set:
        """Load sent response hashes from file"""
        if self.sent_responses_file.exists():
            try:
                data = json.loads(self.sent_responses_file.read_text())
                # Keep only last 500 hashes (prevent unbounded growth)
                hashes = set(data.get("hashes", [])[-500:])
                print(f"[{datetime.now()}] Loaded {len(hashes)} sent response hashes")
                return hashes
            except Exception as e:
                print(f"[{datetime.now()}] Error loading sent hashes: {e}")
        return set()

    def save_sent_responses(self):
        """Save sent response hashes to file"""
        try:
            data = {"hashes": list(self.sent_responses)[-500:]}
            self.sent_responses_file.write_text(json.dumps(data))
        except Exception as e:
            print(f"[{datetime.now()}] Error saving sent hashes: {e}")

    # ========== CONTEXT AWARENESS ==========

    def is_context_question(self, text: str) -> bool:
        """Detect if user is asking about current work/status"""
        text_lower = text.lower().strip()

        # Direct triggers
        context_triggers = [
            "what are you working on",
            "what is aether doing",
            "what's aether doing",
            "whats aether doing",
            "what are you doing",
            "what's happening",
            "whats happening",
            "current status",
            "status update",
            "what's going on",
            "whats going on",
            "/status",
            "/context",
            "/working",
        ]

        for trigger in context_triggers:
            if trigger in text_lower:
                return True

        return False

    def get_context_summary(self) -> str:
        """Read scratch-pad.md and recent handoffs to build context summary"""
        summary_parts = []

        # Read scratch-pad.md
        scratch_pad = self.project_root / ".claude" / "scratch-pad.md"
        if scratch_pad.exists():
            try:
                content = scratch_pad.read_text()

                # Extract key sections
                # Last Updated
                updated_match = re.search(r'\*\*Last Updated\*\*:\s*(.+)', content)
                if updated_match:
                    summary_parts.append(f"📅 Last active: {updated_match.group(1)}")

                # IN PROGRESS section
                in_progress = re.search(r'## IN PROGRESS\n\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
                if in_progress:
                    lines = [l.strip() for l in in_progress.group(1).split('\n') if l.strip().startswith('- [ ]')]
                    if lines:
                        summary_parts.append("🔄 In Progress:")
                        for line in lines[:5]:  # Max 5 items
                            clean = line.replace('- [ ]', '•').strip()
                            summary_parts.append(f"  {clean}")

                # DO NOT RE-DO (recent completed)
                done_section = re.search(r'## DO NOT RE-DO\n\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
                if done_section:
                    lines = [l.strip() for l in done_section.group(1).split('\n') if l.strip().startswith('- [x]')]
                    if lines:
                        recent = lines[-3:]  # Last 3 completed
                        summary_parts.append("✅ Recently completed:")
                        for line in recent:
                            clean = line.replace('- [x]', '•').strip()
                            summary_parts.append(f"  {clean}")

                # INTEL highlights
                intel = re.search(r'## INTEL SCAN HIGHLIGHTS.*?\n\n\|.*?\n\|.*?\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
                if intel:
                    rows = [l for l in intel.group(1).split('\n') if l.strip().startswith('|')]
                    if rows:
                        summary_parts.append("📰 Latest intel:")
                        for row in rows[:3]:
                            parts = [p.strip() for p in row.split('|') if p.strip()]
                            if len(parts) >= 1:
                                summary_parts.append(f"  • {parts[0]}")

            except Exception as e:
                summary_parts.append(f"⚠️ Error reading scratch-pad: {e}")
        else:
            summary_parts.append("📝 No scratch-pad found")

        # Check for recent handoff docs
        handoff_dir = self.project_root / "to-jared"
        if handoff_dir.exists():
            handoffs = sorted(handoff_dir.glob("HANDOFF-*.md"), reverse=True)
            if handoffs:
                latest = handoffs[0]
                summary_parts.append(f"\n📋 Latest handoff: {latest.name}")

        # Check tmux session status
        if self.is_tmux_available():
            session = self.get_current_session()
            if session:
                summary_parts.append(f"\n💻 Active session: {session}")
            else:
                summary_parts.append("\n💻 tmux running but no Aether session")
        else:
            summary_parts.append("\n💻 No tmux session (Claude not actively running)")

        return "\n".join(summary_parts) if summary_parts else "No context available"

    # ========== END CONTEXT AWARENESS ==========

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

    async def send_photo(self, client: httpx.AsyncClient, chat_id: str, file_path: Path, caption: str = ""):
        """Send a photo/image to Telegram (displays as image, not document)"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

        try:
            with open(file_path, 'rb') as f:
                data = {'chat_id': chat_id}
                if caption:
                    data['caption'] = caption[:1024]  # Telegram caption limit

                response = await client.post(
                    url,
                    data=data,
                    files={'photo': (file_path.name, f, 'image/jpeg')}
                )
                if response.status_code != 200:
                    print(f"[{datetime.now()}] Error sending photo: {response.text}")
                    return False
                print(f"[{datetime.now()}] Photo sent to {chat_id}: {file_path.name}")
                return True
        except Exception as e:
            print(f"[{datetime.now()}] Error sending photo: {e}")
            return False

    async def send_document(self, client: httpx.AsyncClient, chat_id: str, file_path: Path, caption: str = ""):
        """Send a document/file to Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"

        try:
            with open(file_path, 'rb') as f:
                files = {'document': (file_path.name, f)}
                data = {'chat_id': chat_id}
                if caption:
                    data['caption'] = caption

                # httpx handles multipart differently
                response = await client.post(
                    url,
                    data=data,
                    files={'document': (file_path.name, open(file_path, 'rb'))}
                )
                if response.status_code != 200:
                    print(f"[{datetime.now()}] Error sending document: {response.text}")
                    return False
                return True
        except Exception as e:
            print(f"[{datetime.now()}] Error sending document: {e}")
            return False

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

    async def handle_photo(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming photo/image"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        photos = message.get("photo", [])
        caption = message.get("caption", "")

        if not photos:
            return

        # Get the largest photo (last in array)
        largest_photo = photos[-1]
        file_id = largest_photo.get("file_id")
        width = largest_photo.get("width", 0)
        height = largest_photo.get("height", 0)

        # Log the photo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Photo from {user_id}: {width}x{height}" + (f" caption: {caption}" if caption else ""))

        # Check authorization
        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for Jared only."
            )
            return

        sender = self.get_user_name(user_id)

        # Track last sender for response routing
        self.last_sender_chat_id = chat_id

        # Download the photo
        await self.send_message(client, chat_id, "Receiving image...")

        file_content = await self.download_file(client, file_id)
        if not file_content:
            await self.send_message(client, chat_id, "Failed to download image")
            return

        # Save to from-telegram folder with timestamp
        docs_path = Path(__file__).parent.parent / "docs" / "from-telegram"
        docs_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"photo_{file_timestamp}.jpg"
        file_path = docs_path / file_name

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)

            print(f"[{timestamp}] Saved photo to: {file_path}")

            # Build notification with instructions prominently included
            notification_parts = [f"Photo received from {sender}"]
            notification_parts.append(f"Saved to: {file_path}")
            if caption:
                notification_parts.append(f"\nINSTRUCTIONS from {sender}: {caption}")
            notification = "\n".join(notification_parts)

            # ALWAYS write to live channel (for persistence)
            self.write_to_live_channel(
                f"[PHOTO: {file_name}]" + (f"\n{caption}" if caption else ""),
                sender
            )

            # Try tmux notification, fallback to inbox
            session = self.get_current_session()
            if session and self.is_tmux_available():
                self.inject_to_session(session, notification, "System")
                # If there are instructions, also inject them as a separate message for visibility
                if caption:
                    self.inject_to_session(session, caption, sender)
            else:
                # Write to inbox as notification
                self.write_to_inbox(notification, sender)

            response_msg = f"Image saved to: docs/from-telegram/{file_name}"
            if caption:
                response_msg += f"\nInstructions forwarded to Aether: \"{caption[:100]}{'...' if len(caption) > 100 else ''}\""
            response_msg += "\n\nAether can now see this image!"

            await self.send_message(client, chat_id, response_msg)

        except Exception as e:
            print(f"[{timestamp}] Error saving photo: {e}")
            await self.send_message(client, chat_id, f"Error saving image: {e}")

    async def handle_document(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming document/file"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        document = message.get("document", {})
        caption = message.get("caption", "")

        file_name = document.get("file_name", "unknown_file")
        file_id = document.get("file_id")
        file_size = document.get("file_size", 0)

        # Log the document AND caption
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Document from {user_id}: {file_name} ({file_size} bytes)" + (f" | Caption: {caption}" if caption else ""))

        # Check authorization
        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for Jared only."
            )
            return

        sender = self.get_user_name(user_id)

        # Track last sender for response routing
        self.last_sender_chat_id = chat_id

        # Download the file
        await self.send_message(client, chat_id, f"Downloading {file_name}...")

        file_content = await self.download_file(client, file_id)
        if not file_content:
            await self.send_message(client, chat_id, "Failed to download file")
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

            # Build notification with caption/instructions prominently included
            notification_parts = [f"File received from {sender}: {file_name}"]
            notification_parts.append(f"Saved to: {file_path}")
            if caption:
                notification_parts.append(f"\nINSTRUCTIONS from {sender}: {caption}")

            notification = "\n".join(notification_parts)

            # ALWAYS write to live channel (for persistence)
            self.write_to_live_channel(
                f"[FILE: {file_name}]" + (f"\n{caption}" if caption else ""),
                sender
            )

            # Try tmux notification, fallback to inbox
            session = self.get_current_session()
            if session and self.is_tmux_available():
                self.inject_to_session(session, notification, "System")
                # If there are instructions, also inject them as a separate message for visibility
                if caption:
                    self.inject_to_session(session, caption, sender)
            else:
                # Write to inbox as notification
                self.write_to_inbox(notification, sender)

            response_msg = f"Saved to: docs/from-telegram/{safe_name}"
            if caption:
                response_msg += f"\nInstructions forwarded to Aether: \"{caption[:100]}{'...' if len(caption) > 100 else ''}\""
            response_msg += "\n\nAether can now read this file!"

            await self.send_message(client, chat_id, response_msg)

        except Exception as e:
            print(f"[{timestamp}] Error saving file: {e}")
            await self.send_message(client, chat_id, f"Error saving file: {e}")

    def get_current_session(self) -> str:
        """Get the current tmux session name - prioritize ATTACHED session"""
        try:
            # FIRST: Find the currently ATTACHED session (most likely to be active Claude)
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}:#{session_attached}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ':1' in line:  # Session is attached
                        attached_session = line.split(':')[0]
                        # Update the session file for consistency
                        self.session_file.write_text(attached_session)
                        return attached_session
        except Exception:
            pass

        # FALLBACK: Read from session file
        if self.session_file.exists():
            return self.session_file.read_text().strip()

        # LAST RESORT: Find an aether/primary session
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

    def inject_to_session(self, session: str, message: str, sender: str) -> bool:
        """Inject message into tmux session with 5x Enter retries for reliability."""
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

    def capture_pane_content(self, session: str) -> str:
        """Capture the current content of the tmux pane"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session, "-p", "-S", "-3000"],
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
        import re
        import hashlib
        responses = []

        # Pattern to match content between markers
        pattern = re.escape(self.START_MARKER) + r"(.*?)" + re.escape(self.END_MARKER)
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            # Clean up the response
            response = match.strip()
            if response and len(response) > 5:  # Ignore tiny responses
                # Create a stable hash of FULL response content
                response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
                if response_hash not in self.sent_responses:
                    responses.append((response, response_hash))

        return responses

    async def monitor_output(self, client: httpx.AsyncClient):
        """Monitor tmux pane AND outbox file for marker-wrapped responses and send to Telegram"""
        outbox_file = self.project_root / "outbox" / "telegram-outbox.md"
        last_outbox_content = ""

        # Ensure outbox directory exists
        outbox_file.parent.mkdir(parents=True, exist_ok=True)
        if not outbox_file.exists():
            outbox_file.write_text("# Telegram Outbox\n\nWrite responses here and they'll be sent to Telegram.\n\n")

        while True:
            try:
                # === METHOD 1: Check tmux pane (original method) ===
                session = self.get_current_session()
                if session and self.is_tmux_available():
                    content = self.capture_pane_content(session)

                    if content != self.last_pane_content:
                        self.last_pane_content = content
                        responses = self.extract_responses(content)

                        for response, response_hash in responses:
                            if len(response) > 4000:
                                response = response[:3900] + "\n\n... [truncated]"

                            await self.send_message(client, self.last_sender_chat_id, response)
                            self.sent_responses.add(response_hash)
                            self.save_sent_responses()
                            print(f"[{datetime.now()}] Sent response to {self.last_sender_chat_id} ({len(response)} chars) [tmux]")

                # === METHOD 2: Check outbox file (for non-tmux sessions) ===
                if outbox_file.exists():
                    outbox_content = outbox_file.read_text()

                    if outbox_content != last_outbox_content:
                        last_outbox_content = outbox_content
                        responses = self.extract_responses(outbox_content)

                        for response, response_hash in responses:
                            if len(response) > 4000:
                                response = response[:3900] + "\n\n... [truncated]"

                            await self.send_message(client, self.last_sender_chat_id, response)
                            self.sent_responses.add(response_hash)
                            self.save_sent_responses()
                            print(f"[{datetime.now()}] Sent response to {self.last_sender_chat_id} ({len(response)} chars) [outbox]")

                # Cleanup sent_responses if too large
                if len(self.sent_responses) > 500:
                    self.sent_responses = set(list(self.sent_responses)[-400:])
                    self.save_sent_responses()

            except Exception as e:
                print(f"[{datetime.now()}] Output monitor error: {e}")

            await asyncio.sleep(2)  # Check every 2 seconds

    def write_to_inbox(self, message: str, sender: str) -> str:
        """Write message to inbox folder as a file (fallback when tmux unavailable)"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"telegram-{timestamp}.txt"
        filepath = self.inbox_dir / filename

        content = f"""# Telegram Message from {sender}
# Received: {datetime.now().isoformat()}
# Via: Aether Telegram Bridge (file fallback)

{message}

---
Note: This message was saved to file because Claude is not running in tmux.
Run your wake-up protocol and check inbox/ for messages.
"""

        filepath.write_text(content)
        print(f"[{datetime.now()}] Written to inbox: {filepath}")
        return str(filepath)

    def write_to_live_channel(self, message: str, sender: str):
        """Write message to live channel file (always, for non-tmux sessions)"""
        live_file = self.project_root / "inbox" / "telegram-live.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"\n---\n**[{timestamp}] {sender}:**\n{message}\n"

        # Append to file
        with open(live_file, 'a') as f:
            f.write(entry)

        print(f"[{datetime.now()}] Written to live channel")

    async def handle_message(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming message"""
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "")

        # Log the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Message from {user_id} (chat {chat_id}): {text[:50]}...")

        # Check authorization
        if not self.is_authorized(user_id):
            await self.send_message(
                client, chat_id,
                "Unauthorized. This bot is configured for Jared only."
            )
            return

        # Track last sender for response routing
        self.last_sender_chat_id = chat_id
        print(f"[{datetime.now()}] Response routing set to chat_id: {chat_id}")

        sender = self.get_user_name(user_id)

        # ALWAYS write to live channel (for non-tmux sessions)
        self.write_to_live_channel(text, sender)

        # ========== SMART COMMANDS ==========

        # /help command
        if text.strip().lower() in ['/help', 'help', '/commands']:
            help_text = """🤖 Aether Bridge v4 Commands:

📊 Status:
/status - What Aether is working on
/ping - Check if Claude is active

📁 Files:
/files - List files in to-jared/
/recent - Recent handoff docs
/get <name> - Download a file

📝 Smart Queries (no slash):
• "what are you working on"
• "what is aether doing"

📨 All other messages → Claude session

💡 Wrapped responses (🤖🎯📱...✨🔚) auto-forward to you"""
            await self.send_message(client, chat_id, help_text)
            return

        # /ping - check session status
        if text.strip().lower() == '/ping':
            if self.is_tmux_available():
                session = self.get_current_session()
                if session:
                    await self.send_message(client, chat_id, f"✅ Claude active in: {session}")
                else:
                    await self.send_message(client, chat_id, "⚠️ tmux running but no Aether session found")
            else:
                await self.send_message(client, chat_id, "❌ No tmux session (Claude not running)")
            return

        # /recent - list recent handoff docs
        if text.strip().lower() == '/recent':
            handoff_dir = self.project_root / "to-jared"
            if handoff_dir.exists():
                handoffs = sorted(handoff_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                if handoffs:
                    lines = ["📋 Recent files in to-jared/:"]
                    for h in handoffs:
                        mtime = datetime.fromtimestamp(h.stat().st_mtime).strftime("%m-%d %H:%M")
                        lines.append(f"• {h.name} ({mtime})")
                    await self.send_message(client, chat_id, "\n".join(lines))
                else:
                    await self.send_message(client, chat_id, "📋 No files in to-jared/")
            else:
                await self.send_message(client, chat_id, "❌ to-jared/ folder not found")
            return

        # /files - list all files waiting
        if text.strip().lower() == '/files':
            to_jared = self.project_root / "to-jared"
            files = []
            if to_jared.exists():
                for f in sorted(to_jared.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                    if f.is_file():
                        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d %H:%M")
                        size = f.stat().st_size
                        files.append(f"• {f.name} ({size:,}b, {mtime})")
            if files:
                await self.send_message(client, chat_id, f"📁 Files for you:\n" + "\n".join(files))
                await self.send_message(client, chat_id, "💡 Use /get <filename> to download")
            else:
                await self.send_message(client, chat_id, "📁 No files waiting")
            return

        # /get <filename> - download a file from to-jared/
        if text.strip().lower().startswith('/get '):
            filename = text.strip()[5:].strip()
            if not filename:
                await self.send_message(client, chat_id, "Usage: /get <filename>")
                return

            to_jared = self.project_root / "to-jared"
            file_path = to_jared / filename

            # Also check without extension variations
            if not file_path.exists():
                # Try finding partial match
                matches = list(to_jared.glob(f"*{filename}*"))
                if matches:
                    file_path = matches[0]

            if file_path.exists() and file_path.is_file():
                await self.send_message(client, chat_id, f"📤 Sending {file_path.name}...")
                success = await self.send_document(client, chat_id, file_path)
                if not success:
                    await self.send_message(client, chat_id, "❌ Failed to send file")
            else:
                await self.send_message(client, chat_id, f"❌ File not found: {filename}\nUse /files to see available files")
            return

        # Context/status questions - answer directly from scratch-pad
        if self.is_context_question(text):
            print(f"[{datetime.now()}] Context question detected, reading scratch-pad")
            context = self.get_context_summary()
            await self.send_message(client, chat_id, f"📊 Aether Status:\n\n{context}")
            return

        # ========== END SMART COMMANDS ==========

        # Check if tmux is available
        if not self.is_tmux_available():
            # Fallback: write to inbox
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"Aether is not running in tmux. Message saved to:\n{filepath}\n\nAether will see this when checking inbox."
            )
            return

        # Get current session
        session = self.get_current_session()

        if not session:
            # Fallback: write to inbox
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"No active Aether session found. Message saved to:\n{filepath}\n\nAether will see this when checking inbox."
            )
            return

        # Inject to session
        if self.inject_to_session(session, text, sender):
            await self.send_message(
                client, chat_id,
                f"Delivered to Aether session: {session}"
            )
        else:
            # Fallback on injection failure
            filepath = self.write_to_inbox(text, sender)
            await self.send_message(
                client, chat_id,
                f"Failed to inject to tmux. Message saved to:\n{filepath}"
            )

    async def poll_updates(self, client: httpx.AsyncClient):
        """Poll for incoming Telegram messages"""
        while True:
            updates = await self.get_updates(client)

            for update in updates:
                self.last_update_id = update.get("update_id", self.last_update_id)

                message = update.get("message")
                if message:
                    # Handle text messages
                    if message.get("text"):
                        await self.handle_message(client, message)
                    # Handle photos/images
                    elif message.get("photo"):
                        await self.handle_photo(client, message)
                    # Handle documents/files
                    elif message.get("document"):
                        await self.handle_document(client, message)

            # Small delay between polls
            await asyncio.sleep(1)

    async def run(self):
        """Main loop - runs input polling and output monitoring concurrently"""
        print(f"[{datetime.now()}] Aether Telegram Bridge v3 (MARKER-BASED) starting...")
        print(f"[{datetime.now()}] Authorized users: {list(self.authorized_users.keys())}")
        print(f"[{datetime.now()}] Inbox fallback: {self.inbox_dir}")
        print(f"[{datetime.now()}] Response markers: {self.START_MARKER} ... {self.END_MARKER}")

        # Check tmux status at startup
        if self.is_tmux_available():
            print(f"[{datetime.now()}] tmux: AVAILABLE")
        else:
            print(f"[{datetime.now()}] tmux: NOT AVAILABLE - will use inbox fallback")

        async with httpx.AsyncClient() as client:
            # Send startup message
            default_chat = self.config.get("default_chat_id")
            if default_chat:
                tmux_status = "✅ tmux available" if self.is_tmux_available() else "⚠️ using inbox fallback"
                await self.send_message(
                    client, default_chat,
                    f"🔄 Aether Bridge v4 (Context-Aware) online\n\n"
                    f"Session: {tmux_status}\n\n"
                    f"Commands: /status /recent /files /ping /help\n"
                    f"Ask: 'what are you working on' for context"
                )

            # Run both tasks concurrently
            await asyncio.gather(
                self.poll_updates(client),
                self.monitor_output(client)
            )


def main():
    bridge = TelegramBridge()

    # Single instance check - prevent duplicate messages
    if not bridge.check_single_instance():
        print(f"[{datetime.now()}] Exiting: Another instance is running")
        sys.exit(1)

    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Bridge stopped by user")
    except Exception as e:
        error_msg = f"[{datetime.now()}] Bridge error: {e}"
        print(error_msg)
        # Try to notify via TG before dying
        try:
            for user_id in bridge.authorized_users:
                bridge.send_message(user_id, f"⚠️ AETHER BRIDGE CRASH\n\n{e}\n\nRestarting in 5s...")
        except:
            pass  # If TG notify fails, still exit
        sys.exit(1)
    finally:
        # Always clean up PID file
        bridge.cleanup_pid()


if __name__ == "__main__":
    main()
