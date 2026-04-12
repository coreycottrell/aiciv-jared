"""
ChatGPT Export Parser
=====================

Parses OpenAI's data export ZIP file format.

Export structure (from Settings > Data Controls > Export Data):
    conversations.json  — Full conversation history
    user.json           — Account info + custom instructions
    message_feedback.json — User ratings (optional, less useful)

Output: standardized migration_profile dict ready for pattern_extractor.py

How to get the export:
    ChatGPT Settings -> Data Controls -> Export Data -> You get a ZIP by email
"""

import json
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_chatgpt_export(zip_path: str) -> dict:
    """
    Parse an OpenAI export ZIP file.

    Args:
        zip_path: Absolute path to the conversations.zip file.

    Returns:
        migration_profile dict with keys:
            source          — "chatgpt"
            conversations   — list of parsed conversation dicts
            custom_instructions — raw string from user.json (or None)
            message_count   — total number of user messages
            conversation_count — number of conversations
            date_range      — {"start": ISO str, "end": ISO str}
            parse_errors    — list of non-fatal error strings
    """
    zip_path = Path(zip_path)
    _validate_zip_path(zip_path)

    profile = {
        "source": "chatgpt",
        "conversations": [],
        "custom_instructions": None,
        "message_count": 0,
        "conversation_count": 0,
        "date_range": {"start": None, "end": None},
        "parse_errors": [],
    }

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        logger.info("ZIP contains: %s", names)

        # ---- conversations.json ----
        conv_file = _find_file(names, "conversations.json")
        if conv_file:
            try:
                raw = zf.read(conv_file)
                conversations_raw = json.loads(raw)
                parsed = _parse_conversations(conversations_raw, profile["parse_errors"])
                profile["conversations"] = parsed
                profile["conversation_count"] = len(parsed)
                profile["message_count"] = sum(c["user_message_count"] for c in parsed)
                profile["date_range"] = _compute_date_range(parsed)
            except Exception as exc:
                msg = f"Failed to parse conversations.json: {exc}"
                logger.error(msg)
                profile["parse_errors"].append(msg)
        else:
            profile["parse_errors"].append("conversations.json not found in ZIP")

        # ---- user.json (custom instructions) ----
        user_file = _find_file(names, "user.json")
        if user_file:
            try:
                raw = zf.read(user_file)
                user_data = json.loads(raw)
                profile["custom_instructions"] = _extract_custom_instructions(user_data)
            except Exception as exc:
                msg = f"Failed to parse user.json: {exc}"
                logger.warning(msg)
                profile["parse_errors"].append(msg)

    logger.info(
        "ChatGPT parse complete: %d conversations, %d user messages",
        profile["conversation_count"],
        profile["message_count"],
    )
    return profile


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_zip_path(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Export ZIP not found: {path}")
    if path.suffix.lower() != ".zip":
        raise ValueError(f"Expected a .zip file, got: {path.suffix}")
    if path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("Export ZIP exceeds 50 MB limit")
    if not zipfile.is_zipfile(path):
        raise ValueError("File is not a valid ZIP archive")


def _find_file(names: list, filename: str) -> Optional[str]:
    """Return the first ZIP entry whose basename matches filename."""
    for name in names:
        if Path(name).name == filename:
            return name
    return None


def _parse_conversations(raw: list, errors: list) -> list:
    """
    Parse the conversations array from conversations.json.

    OpenAI format (as of 2024-2025):
    [
      {
        "id": "...",
        "title": "Market analysis deep dive",
        "create_time": 1700000000.0,
        "update_time": 1700001000.0,
        "mapping": {
          "<node_id>": {
            "id": "...",
            "message": {
              "id": "...",
              "author": {"role": "user"|"assistant"|"system"},
              "content": {"content_type": "text", "parts": ["..."]},
              "create_time": 1700000001.0
            },
            "parent": "...",
            "children": ["..."]
          }
        },
        "moderation_results": [],
        "current_node": "...",
        "plugin_ids": null,
        "conversation_id": "...",
        "conversation_template_id": null,
        "gizmo_id": null,
        "is_archived": false
      }
    ]
    """
    parsed = []

    for i, conv in enumerate(raw):
        try:
            conv_id = conv.get("id") or conv.get("conversation_id") or f"conv_{i}"
            title = conv.get("title") or "Untitled"
            create_time = conv.get("create_time")
            update_time = conv.get("update_time")
            mapping = conv.get("mapping") or {}

            user_messages = []
            assistant_messages = []

            for node in mapping.values():
                msg = node.get("message")
                if not msg:
                    continue
                role = (msg.get("author") or {}).get("role", "")
                content = _extract_message_text(msg)
                ts = msg.get("create_time")
                if role == "user" and content:
                    user_messages.append({"text": content, "timestamp": ts})
                elif role == "assistant" and content:
                    assistant_messages.append({"text": content, "timestamp": ts})

            parsed.append({
                "id": conv_id,
                "title": title,
                "create_time": _ts_to_iso(create_time),
                "update_time": _ts_to_iso(update_time),
                "user_message_count": len(user_messages),
                "assistant_message_count": len(assistant_messages),
                "user_messages": user_messages,
            })

        except Exception as exc:
            errors.append(f"Skipped conversation {i}: {exc}")

    return parsed


def _extract_message_text(msg: dict) -> str:
    """Extract plain text from a message node."""
    content = msg.get("content") or {}
    parts = content.get("parts") or []
    texts = []
    for part in parts:
        if isinstance(part, str):
            texts.append(part)
        elif isinstance(part, dict):
            # Some parts are structured objects (images, files) — skip those
            if part.get("content_type") == "text":
                texts.append(part.get("text", ""))
    return " ".join(t.strip() for t in texts if t.strip())


def _extract_custom_instructions(user_data: dict) -> Optional[str]:
    """
    Extract custom instructions from user.json.

    OpenAI stores custom instructions inside chat_preferences or
    a custom_instructions key. The schema has changed over time, so
    we try multiple known locations.
    """
    # Attempt 1: direct key
    if "custom_instructions" in user_data:
        ci = user_data["custom_instructions"]
        if isinstance(ci, dict):
            parts = []
            if ci.get("about_user_message"):
                parts.append(f"About me: {ci['about_user_message']}")
            if ci.get("about_model_message"):
                parts.append(f"Response style: {ci['about_model_message']}")
            return "\n".join(parts) if parts else None
        if isinstance(ci, str) and ci.strip():
            return ci.strip()

    # Attempt 2: nested under chat_preferences
    prefs = user_data.get("chat_preferences") or {}
    ci = prefs.get("custom_instructions")
    if ci and isinstance(ci, dict):
        parts = []
        for v in ci.values():
            if isinstance(v, str) and v.strip():
                parts.append(v.strip())
        return "\n".join(parts) if parts else None

    return None


def _ts_to_iso(ts) -> Optional[str]:
    if ts is None:
        return None
    try:
        return datetime.utcfromtimestamp(float(ts)).isoformat() + "Z"
    except Exception:
        return None


def _compute_date_range(conversations: list) -> dict:
    timestamps = []
    for c in conversations:
        if c.get("create_time"):
            timestamps.append(c["create_time"])
    if not timestamps:
        return {"start": None, "end": None}
    timestamps.sort()
    return {"start": timestamps[0], "end": timestamps[-1]}


# ---------------------------------------------------------------------------
# CLI for quick testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import pprint

    if len(sys.argv) < 2:
        print("Usage: python chatgpt_parser.py <path-to-export.zip>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = parse_chatgpt_export(sys.argv[1])
    pprint.pprint({
        "source": result["source"],
        "conversation_count": result["conversation_count"],
        "message_count": result["message_count"],
        "date_range": result["date_range"],
        "custom_instructions_preview": (result["custom_instructions"] or "")[:200],
        "parse_errors": result["parse_errors"],
    })
