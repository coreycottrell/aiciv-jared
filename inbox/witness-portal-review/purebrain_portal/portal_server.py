#!/usr/bin/env python3
"""Witness Portal Server — per-CIV mini server for witness.ai-civ.com
Auth via Bearer token. JSONL-based chat history (same as TG bot).
"""
import asyncio
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
TOKEN_FILE = SCRIPT_DIR / ".portal-token"
PORTAL_HTML = SCRIPT_DIR / "portal.html"
PORTAL_PB_HTML = SCRIPT_DIR / "portal-pb-styled.html"
REACT_DIST = SCRIPT_DIR / "react-portal" / "dist"
START_TIME = time.time()
CIV_NAME = "witness"
LOG_ROOT = Path.home() / ".claude" / "projects" / "-home-aiciv"
HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"
PORTAL_CHAT_LOG = SCRIPT_DIR / "portal-chat.jsonl"

if TOKEN_FILE.exists():
    BEARER_TOKEN = TOKEN_FILE.read_text().strip()
else:
    BEARER_TOKEN = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(BEARER_TOKEN)
    TOKEN_FILE.chmod(0o600)
    print(f"[portal] Generated new bearer token: {BEARER_TOKEN}")


def get_tmux_session() -> str:
    """Find the live witness-primary session."""
    def alive(name):
        try:
            subprocess.check_output(["tmux", "has-session", "-t", name], stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    marker = Path("/home/aiciv/.current_session")
    if marker.exists():
        name = marker.read_text().strip()
        if name and alive(name):
            return name
    try:
        out = subprocess.check_output(["tmux", "list-sessions", "-F", "#{session_name}"],
                                      stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            if "witness-primary" in line:
                return line.strip()
    except Exception:
        pass
    return "witness-primary"


def _find_current_session_id():
    """Find the current Claude Code session ID from history.jsonl."""
    try:
        if not HISTORY_FILE.exists():
            return None
        with HISTORY_FILE.open("r") as f:
            f.seek(0, 2)
            length = f.tell()
            window = min(16384, length)
            f.seek(max(0, length - window))
            lines = f.read().splitlines()
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                proj = entry.get("project", "")
                if proj and ("aiciv" in proj or "/home/aiciv" in proj):
                    return entry.get("sessionId")
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return None


def _get_all_session_log_paths(max_files=10):
    """Get paths to recent JSONL session logs, ordered oldest-first."""
    try:
        logs = sorted(LOG_ROOT.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        return list(reversed(logs[:max_files]))
    except Exception:
        return []


def _despace(text):
    """Collapse spaced-out text like 'H  e  l  l  o' back to 'Hello'.
    Some older JSONL sessions store text with spaces between every character."""
    if not text or len(text) < 6:
        return text
    # Check if text follows the pattern: char, spaces, char, spaces...
    # Sample first 40 chars to detect the pattern
    sample = text[:40]
    # Pattern: single non-space char followed by 1-2 spaces, repeating
    spaced_chars = 0
    i = 0
    while i < len(sample):
        if i + 1 < len(sample) and sample[i] != " " and sample[i + 1] == " ":
            spaced_chars += 1
            i += 1
            while i < len(sample) and sample[i] == " ":
                i += 1
        else:
            i += 1
    # If >60% of non-space chars are followed by spaces, it's spaced text
    non_space = sum(1 for c in sample if c != " ")
    if non_space > 0 and spaced_chars / non_space > 0.6:
        # Collapse: take every non-space char, but preserve intentional word gaps
        result = []
        i = 0
        while i < len(text):
            if text[i] != " ":
                result.append(text[i])
                i += 1
                # Skip the inter-character spaces (1-2 spaces)
                spaces = 0
                while i < len(text) and text[i] == " ":
                    spaces += 1
                    i += 1
                # 3+ spaces likely means intentional word boundary
                if spaces >= 3:
                    result.append(" ")
            else:
                i += 1
        return "".join(result)
    return text


def _is_real_user_message(text):
    """Check if a user message is a real human message (not system/teammate noise)."""
    if not text or len(text) < 2:
        return False
    # Telegram messages from Corey - always real
    if "[TELEGRAM" in text:
        return True
    # Portal-sent messages (stored in portal chat log)
    if text.startswith("[PORTAL]"):
        return True
    # Filter out noise
    noise_markers = [
        "<teammate-message", "<system-reminder", "system-reminder",
        "Base directory for this skill", "teammate_id=",
        "<tool_result", "<function_calls", "hook success",
        "Session Ledger", "MEMORY INJECTION", "<task-notification",
        "[Image: source:", "PHOTO saved to:",
        "This session is being continued from a previous",
        "Called the Read tool", "Called the Bash tool",
        "Called the Write tool", "Called the Glob tool",
        "Called the Grep tool", "Result of calling",
        "[from-ACG]",                  # Cross-CIV system messages
        "Context restored",
        "Summary:  ",                  # Agent task summaries
        "` regex", "` sed", "| sed",   # Code snippets leaking as messages
        "re.search(r'", "re.DOTALL",
    ]
    for marker in noise_markers:
        if marker in text[:300]:
            return False
    # Skip messages that look like code/config (too many special chars)
    special = sum(1 for c in text[:200] if c in '{}[]|\\`$()#')
    if len(text) < 200 and special > len(text) * 0.15:
        return False
    return True


def _clean_user_text(text):
    """Clean up user message text for display."""
    # Strip Telegram prefix for cleaner display
    if "[TELEGRAM" in text:
        # Format: [TELEGRAM private:NNN from @Username] actual message
        idx = text.find("]")
        if idx > 0:
            return text[idx + 1:].strip()
    if text.startswith("[PORTAL] "):
        return text[9:]
    return text


def _is_real_assistant_message(text):
    """Check if an assistant message is substantive (not just tool calls)."""
    if not text or len(text) < 5:
        return False
    # Skip messages that are purely tool/system related
    noise_starts = [
        "Let me ", "I'll ", "Now let me ", "Reading ",  # These are often followed by tool calls only
    ]
    # Actually, keep most assistant messages - they're the responses Corey wants to see
    # Only filter very short or clearly system-only ones
    if len(text) < 10:
        return False
    return True


def _parse_jsonl_messages_from_file(log_path):
    """Parse a single JSONL log into clean chat messages."""
    messages = []
    if not log_path or not log_path.exists():
        return messages

    try:
        with log_path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = entry.get("message", {})
                role = msg.get("role", entry.get("type", ""))

                if role not in ("user", "assistant"):
                    continue

                content_blocks = msg.get("content", []) or []
                text_parts = []    # For normal text blocks
                char_parts = []    # For single-character string blocks
                is_char_stream = False
                for block in content_blocks:
                    if isinstance(block, str):
                        # Single char blocks: preserve spaces for word boundaries
                        if len(block) <= 2:  # single chars including '\n'
                            char_parts.append(block)
                            is_char_stream = True
                        else:
                            s = block.strip()
                            if s:
                                text_parts.append(s)
                    elif isinstance(block, dict) and block.get("type") == "text":
                        t = (block.get("text") or "").strip()
                        if t:
                            text_parts.append(t)

                # Build combined text
                if is_char_stream and len(char_parts) > 10:
                    # Join character stream directly (preserves spaces/newlines)
                    combined = "".join(char_parts).strip()
                    # Also append any text blocks
                    if text_parts:
                        combined += "\n\n" + "\n\n".join(text_parts)
                elif text_parts:
                    combined = "\n\n".join(text_parts)
                else:
                    continue

                if not combined or len(combined) < 2:
                    continue

                # Collapse spaced-out text from older sessions
                combined = _despace(combined)

                # Filter based on role
                if role == "user":
                    if not _is_real_user_message(combined):
                        continue
                    combined = _clean_user_text(combined)
                elif role == "assistant":
                    if not _is_real_assistant_message(combined):
                        continue

                ts = entry.get("timestamp")
                if isinstance(ts, (int, float)):
                    ts = ts / 1000  # ms to seconds
                else:
                    ts = time.time()

                messages.append({
                    "role": role,
                    "text": combined,
                    "timestamp": int(ts),
                    "id": entry.get("uuid", f"msg-{log_path.stem[:8]}-{len(messages)}")
                })
    except Exception:
        pass

    return messages


def _load_portal_messages():
    """Load messages sent via the portal chat."""
    messages = []
    if not PORTAL_CHAT_LOG.exists():
        return messages
    try:
        with PORTAL_CHAT_LOG.open("r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    messages.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return messages


def _save_portal_message(text, role="user"):
    """Save a message sent via the portal."""
    entry = {
        "role": role,
        "text": text,
        "timestamp": int(time.time()),
        "id": f"portal-{int(time.time() * 1000)}",
    }
    try:
        with PORTAL_CHAT_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    return entry


def _parse_all_messages(last_n=100):
    """Parse messages across all recent session logs + portal log."""
    all_messages = []

    # JSONL session logs
    for log_path in _get_all_session_log_paths(max_files=10):
        all_messages.extend(_parse_jsonl_messages_from_file(log_path))

    # Portal-sent messages
    all_messages.extend(_load_portal_messages())

    # Sort by timestamp
    all_messages.sort(key=lambda m: m["timestamp"])

    # Deduplicate by ID
    seen = set()
    deduped = []
    for m in all_messages:
        if m["id"] not in seen:
            seen.add(m["id"])
            deduped.append(m)

    return deduped[-last_n:] if len(deduped) > last_n else deduped


def check_auth(request: Request) -> bool:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:] == BEARER_TOKEN
    return request.query_params.get("token") == BEARER_TOKEN


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "civ": CIV_NAME, "uptime": int(time.time() - START_TIME)})


async def index(request: Request) -> Response:
    # Serve PB-styled version if host matches witnesspb subdomain
    host = request.headers.get("host", "")
    if "witnesspb" in host and PORTAL_PB_HTML.exists():
        return FileResponse(str(PORTAL_PB_HTML), media_type="text/html")
    if PORTAL_HTML.exists():
        return FileResponse(str(PORTAL_HTML), media_type="text/html")
    return Response("<h1>Portal HTML not found</h1>", media_type="text/html", status_code=503)


async def index_pb(request: Request) -> Response:
    """Serve PureBrain-styled portal at /pb path."""
    if PORTAL_PB_HTML.exists():
        return FileResponse(str(PORTAL_PB_HTML), media_type="text/html")
    return Response("<h1>PB Portal not found</h1>", media_type="text/html", status_code=503)


async def index_react(request: Request) -> Response:
    """Serve React portal at /react path."""
    react_index = REACT_DIST / "index.html"
    if react_index.exists():
        return FileResponse(str(react_index), media_type="text/html")
    return Response("<h1>React Portal not found — run npm run build in react-portal/</h1>",
                    media_type="text/html", status_code=503)


async def api_status(request: Request) -> JSONResponse:
    if not check_auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    session = get_tmux_session()
    tmux_alive = False
    try:
        subprocess.check_output(["tmux", "has-session", "-t", session], stderr=subprocess.DEVNULL)
        tmux_alive = True
    except subprocess.CalledProcessError:
        pass

    claude_running = False
    try:
        out = subprocess.check_output(["pgrep", "-f", "claude"], stderr=subprocess.DEVNULL, text=True)
        claude_running = bool(out.strip())
    except subprocess.CalledProcessError:
        pass

    tg_running = False
    try:
        out = subprocess.check_output(["pgrep", "-f", "telegram"], stderr=subprocess.DEVNULL, text=True)
        tg_running = bool(out.strip())
    except subprocess.CalledProcessError:
        pass

    return JSONResponse({
        "civ": CIV_NAME, "uptime": int(time.time() - START_TIME),
        "tmux_session": session, "tmux_alive": tmux_alive,
        "claude_running": claude_running, "tg_bot_running": tg_running,
        "timestamp": int(time.time()),
    })


async def api_chat_history(request: Request) -> JSONResponse:
    """Return recent chat messages from JSONL session log."""
    if not check_auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    last_n = int(request.query_params.get("last", "100"))
    last_n = min(last_n, 500)

    messages = _parse_all_messages(last_n=last_n)

    return JSONResponse({"messages": messages, "count": len(messages), "timestamp": int(time.time())})


async def api_chat_send(request: Request) -> JSONResponse:
    """Inject a message into the tmux session. Response comes via /api/chat/stream or history."""
    if not check_auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    try:
        body = await request.json()
        message = str(body.get("message", "")).strip()
    except Exception:
        return JSONResponse({"error": "invalid json"}, status_code=400)

    if not message:
        return JSONResponse({"error": "empty message"}, status_code=400)

    # Save to portal chat log for history
    _save_portal_message(message, role="user")

    # Tag injection source so tmux pane shows where input came from
    host = request.headers.get("referer", "")
    if "react" in host:
        tagged = f"[portal-react] {message}"
    else:
        tagged = f"[portal] {message}"

    session = get_tmux_session()
    try:
        subprocess.run(["tmux", "send-keys", "-t", session, "-l", tagged],
                       check=True, stderr=subprocess.DEVNULL)
        subprocess.run(["tmux", "send-keys", "-t", session, "Enter"],
                       check=True, stderr=subprocess.DEVNULL)
        return JSONResponse({"status": "sent", "timestamp": int(time.time())})
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": f"tmux error: {e}"}, status_code=500)


async def ws_chat(websocket: WebSocket) -> None:
    """Stream new chat messages via WebSocket. Polls JSONL log for new entries."""
    token = websocket.query_params.get("token", "")
    if token != BEARER_TOKEN:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    seen_ids = set()

    # Send initial batch of recent messages
    messages = _parse_all_messages(last_n=200)
    for msg in messages:
        seen_ids.add(msg["id"])

    try:
        while True:
            messages = _parse_all_messages(last_n=200)
            for msg in messages:
                if msg["id"] not in seen_ids:
                    seen_ids.add(msg["id"])
                    await websocket.send_text(json.dumps(msg))
            await asyncio.sleep(1.5)
    except (WebSocketDisconnect, Exception):
        pass


def _find_primary_pane():
    """Find the tmux pane ID running the primary Claude Code instance."""
    session = get_tmux_session()
    try:
        # List all panes with their IDs
        out = subprocess.check_output(
            ["tmux", "list-panes", "-t", session, "-F", "#{pane_id}"],
            stderr=subprocess.DEVNULL, text=True
        )
        panes = [p.strip() for p in out.splitlines() if p.strip()]
        if not panes:
            return session  # fallback to session target

        # Primary is always the first pane (index 0)
        # Team leads are spawned in subsequent panes
        return panes[0]
    except Exception:
        return session


async def ws_terminal(websocket: WebSocket) -> None:
    """Stream tmux pane content via WebSocket. Read-only."""
    token = websocket.query_params.get("token", "")
    if token != BEARER_TOKEN:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    pane_target = _find_primary_pane()
    last_content = ""

    try:
        while True:
            try:
                content = subprocess.check_output(
                    ["tmux", "capture-pane", "-t", pane_target, "-p"],
                    stderr=subprocess.DEVNULL, text=True
                ).strip()
            except subprocess.CalledProcessError:
                content = "[tmux session not found]"

            if content != last_content:
                await websocket.send_text(content)
                last_content = content

            await asyncio.sleep(0.5)
    except (WebSocketDisconnect, Exception):
        pass


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
_react_assets_mount = (
    [Mount("/react/assets", app=StaticFiles(directory=str(REACT_DIST / "assets")))]
    if (REACT_DIST / "assets").exists()
    else []
)

routes = [
    Route("/", endpoint=index),
    Route("/pb", endpoint=index_pb),
    Route("/react", endpoint=index_react),
    *_react_assets_mount,
    Route("/health", endpoint=health),
    Route("/api/status", endpoint=api_status),
    Route("/api/chat/history", endpoint=api_chat_history),
    Route("/api/chat/send", endpoint=api_chat_send, methods=["POST"]),
    WebSocketRoute("/ws/chat", endpoint=ws_chat),
    WebSocketRoute("/ws/terminal", endpoint=ws_terminal),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8097))
    print(f"[portal] Starting Witness Portal on port {port}")
    print(f"[portal] Bearer token: {BEARER_TOKEN}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
