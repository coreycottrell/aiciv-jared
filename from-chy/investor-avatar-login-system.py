#!/usr/bin/env python3
"""Investor Login & Personalization System for PureBrain Portal.

Provides:
  - InvestorRegistry: JSON-backed investor data store
  - WelcomeMessageGenerator: personalized Chy-voice greetings
  - API endpoint functions for Starlette (investor-login, conversation-save, conversation-get)
  - Integration helper for ephemeral tmux sessions

Add to portal_server.py routes:
  Route("/api/investor-login",              endpoint=api_investor_login,            methods=["POST", "OPTIONS"]),
  Route("/api/investor-conversation/save",  endpoint=api_investor_conversation_save, methods=["POST", "OPTIONS"]),
  Route("/api/investor-conversation/{code}",endpoint=api_investor_conversation_get,  methods=["GET", "OPTIONS"]),
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_REGISTRY_PATH = Path(__file__).parent.parent / "purebrain_portal" / "investor-registry.json"
INVESTOR_API_KEY = "purebrain-investor-2026"

CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}
CORS_PREFLIGHT_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Investor-Key",
}


# ---------------------------------------------------------------------------
# InvestorRegistry — JSON-backed investor data store
# ---------------------------------------------------------------------------
class InvestorRegistry:
    """Thread-safe-ish JSON file store for investor profiles and conversations."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or _REGISTRY_PATH
        self._data: dict = {"investors": {}}
        self._load()

    # -- persistence --

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {"investors": {}}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))
        tmp.replace(self.path)

    # -- lookups --

    def lookup(self, code: str) -> Optional[dict]:
        """Return investor dict for a code (case-insensitive), or None."""
        code = code.strip().upper()
        return self._data["investors"].get(code)

    def exists(self, code: str) -> bool:
        return code.strip().upper() in self._data["investors"]

    # -- mutations --

    def record_visit(self, code: str) -> dict:
        """Bump visit count and last_visit. Returns updated investor dict."""
        code = code.strip().upper()
        inv = self._data["investors"].get(code)
        if not inv:
            return {}
        inv["total_visits"] = inv.get("total_visits", 0) + 1
        inv["last_visit"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._save()
        return inv

    def save_conversation(self, code: str, messages: list) -> bool:
        """Append a conversation block to the investor's history."""
        code = code.strip().upper()
        inv = self._data["investors"].get(code)
        if not inv:
            return False
        if "conversations" not in inv:
            inv["conversations"] = []
        inv["conversations"].append({
            "timestamp": int(time.time()),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "messages": messages,
        })
        self._save()
        return True

    def get_conversations(self, code: str) -> list:
        """Return all saved conversations for an investor."""
        code = code.strip().upper()
        inv = self._data["investors"].get(code)
        if not inv:
            return []
        return inv.get("conversations", [])

    def get_last_topic(self, code: str) -> str:
        """Extract a rough 'last topic' from the most recent conversation."""
        convs = self.get_conversations(code)
        if not convs:
            return ""
        last_msgs = convs[-1].get("messages", [])
        # Find last user message as a proxy for topic
        for msg in reversed(last_msgs):
            if msg.get("role") == "user":
                text = msg.get("content", "")
                # Truncate to first sentence or 80 chars
                for sep in [".", "?", "!"]:
                    idx = text.find(sep)
                    if 0 < idx < 80:
                        return text[: idx + 1]
                return text[:80]
        return ""

    def upsert_investor(self, code: str, data: dict) -> None:
        """Add or update an investor entry."""
        code = code.strip().upper()
        existing = self._data["investors"].get(code, {})
        existing.update(data)
        if "conversations" not in existing:
            existing["conversations"] = []
        if "last_visit" not in existing:
            existing["last_visit"] = None
        if "total_visits" not in existing:
            existing["total_visits"] = 0
        self._data["investors"][code] = existing
        self._save()

    @property
    def all_codes(self) -> list:
        return list(self._data["investors"].keys())


# ---------------------------------------------------------------------------
# WelcomeMessageGenerator — Chy's personalized greetings
# ---------------------------------------------------------------------------
class WelcomeMessageGenerator:
    """Generate welcome messages in Chy's voice."""

    FIRST_VISIT_TEMPLATE = (
        "Welcome, {name}. I'm Chy, the AI COO at Pure Technology. "
        "I work alongside Aether, our AI Co-CEO, and Jared Sanborn, our CEO. "
        "I've prepared a personalized gift for you -- {gift_title}. "
        "{gift_description} "
        "I'll share the download link during our conversation. "
        "But first -- what would you like to know about Pure Technology "
        "and our $2.5M Seed-2 raise at $55M pre-money?"
    )

    FIRST_VISIT_NO_GIFT_TEMPLATE = (
        "Welcome, {name}. I'm Chy, the AI COO at Pure Technology. "
        "I work alongside Aether, our AI Co-CEO, and Jared Sanborn, our CEO. "
        "What would you like to know about Pure Technology "
        "and our $2.5M Seed-2 raise at $55M pre-money?"
    )

    RETURNING_TEMPLATE = (
        "Welcome back, {name}! Great to see you again. "
        "Last time we talked about {last_topic}. "
        "Ready to pick up where we left off?"
    )

    RETURNING_NO_TOPIC_TEMPLATE = (
        "Welcome back, {name}! Great to see you again. "
        "What can I help you with today?"
    )

    @classmethod
    def generate(cls, investor: dict, returning: bool = False,
                 last_topic: str = "") -> str:
        name = investor.get("name", "there")
        gift_title = investor.get("gift_title", "")
        gift_desc = investor.get("gift_description", "")

        if returning:
            if last_topic:
                return cls.RETURNING_TEMPLATE.format(
                    name=name, last_topic=last_topic
                )
            return cls.RETURNING_NO_TOPIC_TEMPLATE.format(name=name)

        if gift_title:
            return cls.FIRST_VISIT_TEMPLATE.format(
                name=name, gift_title=gift_title, gift_description=gift_desc
            )
        return cls.FIRST_VISIT_NO_GIFT_TEMPLATE.format(name=name)


# ---------------------------------------------------------------------------
# Singleton registry (import once in portal_server.py)
# ---------------------------------------------------------------------------
_registry: Optional[InvestorRegistry] = None


def get_registry() -> InvestorRegistry:
    global _registry
    if _registry is None:
        _registry = InvestorRegistry()
    return _registry


# ---------------------------------------------------------------------------
# API Endpoints (Starlette-compatible)
# ---------------------------------------------------------------------------

async def api_investor_login(request: Request) -> JSONResponse:
    """POST /api/investor-login -- authenticate an investor by code.

    Body: {"code": "AYTON2026"}
    Returns personalized welcome message, gift info, conversation history.
    """
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_PREFLIGHT_HEADERS)

    # Auth
    api_key = request.headers.get("x-investor-key", "")
    if api_key != INVESTOR_API_KEY:
        return JSONResponse(
            {"error": "unauthorized"}, status_code=401, headers=CORS_HEADERS
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"error": "Invalid JSON"}, status_code=400, headers=CORS_HEADERS
        )

    code = (body.get("code") or "").strip().upper()
    if not code:
        return JSONResponse(
            {"status": "invalid_code", "error": "No code provided"},
            status_code=400, headers=CORS_HEADERS,
        )

    registry = get_registry()
    investor = registry.lookup(code)

    if not investor:
        return JSONResponse(
            {"status": "invalid_code", "error": "Code not recognized"},
            status_code=404, headers=CORS_HEADERS,
        )

    # Determine if returning visitor
    returning = investor.get("total_visits", 0) > 0
    last_topic = registry.get_last_topic(code) if returning else ""

    # Record the visit
    investor = registry.record_visit(code)

    # Generate conversation ID
    name_slug = investor.get("name", "investor").lower().replace(" ", "-")
    conversation_id = f"{name_slug}-{int(time.time())}"

    # Build welcome message
    welcome = WelcomeMessageGenerator.generate(
        investor, returning=returning, last_topic=last_topic
    )

    # Build response
    response: dict = {
        "status": "authenticated",
        "name": investor.get("name", ""),
        "company": investor.get("company", ""),
        "gift_title": investor.get("gift_title", ""),
        "gift_description": investor.get("gift_description", ""),
        "gift_url": investor.get("gift_url"),
        "welcome_message": welcome,
        "conversation_id": conversation_id,
        "returning": returning,
    }

    if returning:
        response["last_visit"] = investor.get("last_visit", "")
        # Include last N messages for context
        convs = registry.get_conversations(code)
        if convs:
            response["previous_messages"] = convs[-1].get("messages", [])

    return JSONResponse(response, headers=CORS_HEADERS)


async def api_investor_conversation_save(request: Request) -> JSONResponse:
    """POST /api/investor-conversation/save -- persist conversation messages.

    Body: {"code": "AYTON2026", "messages": [{role, content, timestamp}, ...]}
    """
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_PREFLIGHT_HEADERS)

    api_key = request.headers.get("x-investor-key", "")
    if api_key != INVESTOR_API_KEY:
        return JSONResponse(
            {"error": "unauthorized"}, status_code=401, headers=CORS_HEADERS
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"error": "Invalid JSON"}, status_code=400, headers=CORS_HEADERS
        )

    code = (body.get("code") or "").strip().upper()
    messages = body.get("messages", [])

    if not code:
        return JSONResponse(
            {"error": "No code provided"}, status_code=400, headers=CORS_HEADERS
        )
    if not messages:
        return JSONResponse(
            {"error": "No messages provided"}, status_code=400, headers=CORS_HEADERS
        )

    registry = get_registry()
    if not registry.exists(code):
        return JSONResponse(
            {"error": "Unknown investor code"}, status_code=404, headers=CORS_HEADERS
        )

    ok = registry.save_conversation(code, messages)
    if ok:
        return JSONResponse(
            {"status": "saved", "message_count": len(messages)},
            headers=CORS_HEADERS,
        )
    return JSONResponse(
        {"error": "Failed to save"}, status_code=500, headers=CORS_HEADERS
    )


async def api_investor_conversation_get(request: Request) -> JSONResponse:
    """GET /api/investor-conversation/{code} -- retrieve conversation history."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_PREFLIGHT_HEADERS)

    api_key = request.headers.get("x-investor-key", "")
    if api_key != INVESTOR_API_KEY:
        return JSONResponse(
            {"error": "unauthorized"}, status_code=401, headers=CORS_HEADERS
        )

    code = request.path_params.get("code", "").strip().upper()
    if not code:
        return JSONResponse(
            {"error": "No code"}, status_code=400, headers=CORS_HEADERS
        )

    registry = get_registry()
    if not registry.exists(code):
        return JSONResponse(
            {"error": "Unknown investor code"}, status_code=404, headers=CORS_HEADERS
        )

    conversations = registry.get_conversations(code)
    investor = registry.lookup(code)

    return JSONResponse({
        "code": code,
        "name": investor.get("name", ""),
        "total_visits": investor.get("total_visits", 0),
        "last_visit": investor.get("last_visit"),
        "conversations": conversations,
    }, headers=CORS_HEADERS)


# ---------------------------------------------------------------------------
# Tmux Session Integration Helper
# ---------------------------------------------------------------------------

def build_investor_claude_md(
    base_claude_md: str,
    investor: dict,
    previous_summary: str = "",
) -> str:
    """Inject investor personalization into the CLAUDE.md for ephemeral sessions.

    Call this when spawning an investor tmux session. It prepends investor
    context (name, company, gift) to the standard Chy knowledge base CLAUDE.md.
    """
    name = investor.get("name", "Investor")
    company = investor.get("company", "")
    gift_title = investor.get("gift_title", "")
    gift_desc = investor.get("gift_description", "")

    lines = [
        f"## [INVESTOR: {name}]",
        f"Company: {company}" if company else "",
        "",
    ]

    if gift_title:
        lines.extend([
            f"You have prepared a gift for this investor: **{gift_title}**",
            f"Description: {gift_desc}" if gift_desc else "",
            "Mention the gift naturally in conversation. Offer to share the "
            "download link after a few substantive questions.",
            "",
        ])

    if previous_summary:
        lines.extend([
            "## Previous Conversation Summary",
            f"This is a RETURNING visitor. Here is what you discussed last time:",
            previous_summary,
            "Reference this context naturally -- do not repeat it verbatim.",
            "",
        ])

    investor_header = "\n".join(l for l in lines if l is not None)
    return investor_header + "\n\n" + base_claude_md


# ---------------------------------------------------------------------------
# Registry Population Helper
# ---------------------------------------------------------------------------

def populate_registry_from_json(
    data_path: str = "/home/aiciv/exports/investor-avatar-data.json",
    registry_path: Optional[str] = None,
) -> int:
    """Read investor-avatar-data.json and build/update investor-registry.json.

    Only imports investors who have a non-empty 'code' field.
    Returns count of investors imported.
    """
    src = Path(data_path)
    if not src.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    investors = json.loads(src.read_text())
    reg_path = Path(registry_path) if registry_path else _REGISTRY_PATH
    registry = InvestorRegistry(reg_path)

    count = 0
    for inv in investors:
        code = (inv.get("code") or "").strip().upper()
        if not code:
            continue

        # Normalize name (title case for ALL-CAPS names)
        name = inv.get("name", "").strip()
        if name == name.upper() and len(name) > 2:
            name = name.title()

        registry.upsert_investor(code, {
            "name": name,
            "email": inv.get("email", ""),
            "company": inv.get("company", ""),
            "priority": inv.get("priority", ""),
            "gift_title": inv.get("gift", ""),
            "gift_description": inv.get("gift_desc", ""),
            "gift_url": None,
        })
        count += 1

    print(f"Imported {count} investors into {reg_path}")
    return count


# ---------------------------------------------------------------------------
# CLI entry point (for testing)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "populate":
        data_file = sys.argv[2] if len(sys.argv) > 2 else "/home/aiciv/exports/investor-avatar-data.json"
        count = populate_registry_from_json(data_file)
        print(f"Done. {count} investors in registry.")
    elif len(sys.argv) > 1 and sys.argv[1] == "lookup":
        code = sys.argv[2] if len(sys.argv) > 2 else ""
        reg = InvestorRegistry()
        inv = reg.lookup(code)
        if inv:
            print(json.dumps(inv, indent=2))
            print(f"\nWelcome: {WelcomeMessageGenerator.generate(inv)}")
        else:
            print(f"Code '{code}' not found. Available: {reg.all_codes}")
    else:
        print("Usage:")
        print("  python investor-avatar-login-system.py populate [data.json]")
        print("  python investor-avatar-login-system.py lookup CODE")
