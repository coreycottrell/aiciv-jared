"""
Claude Export Parser
====================

Parses Anthropic's data export ZIP file format.

Export structure (from Account Settings > Export Data):
    conversations.json  — Full conversation history
    (No user.json equivalent — Anthropic doesn't expose system prompts via export)

Anthropic's export format is similar to OpenAI's but with some differences:
    - Timestamps are ISO strings, not Unix floats
    - No mapping/tree structure — messages are a flat array
    - No custom instructions in the export (captured via manual paste in UI)

Output: standardized migration_profile dict (same schema as chatgpt_parser)

How to get the export:
    claude.ai -> Settings -> Account -> Export Data -> ZIP file emailed
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

def parse_claude_export(zip_path: str, custom_instructions: Optional[str] = None) -> dict:
    """
    Parse an Anthropic export ZIP file.

    Args:
        zip_path:            Absolute path to the export ZIP file.
        custom_instructions: Optional text the user pasted into the UI.
                             Anthropic doesn't include this in the export file,
                             so the API accepts it separately.

    Returns:
        migration_profile dict with the same schema as parse_chatgpt_export.
    """
    zip_path = Path(zip_path)
    _validate_zip_path(zip_path)

    profile = {
        "source": "claude",
        "conversations": [],
        "custom_instructions": custom_instructions,
        "message_count": 0,
        "conversation_count": 0,
        "date_range": {"start": None, "end": None},
        "parse_errors": [],
    }

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        logger.info("ZIP contains: %s", names)

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
            # Anthropic may name the file differently — try other candidates
            candidates = [n for n in names if n.endswith(".json") and "conv" in n.lower()]
            if candidates:
                try:
                    raw = zf.read(candidates[0])
                    conversations_raw = json.loads(raw)
                    parsed = _parse_conversations(conversations_raw, profile["parse_errors"])
                    profile["conversations"] = parsed
                    profile["conversation_count"] = len(parsed)
                    profile["message_count"] = sum(c["user_message_count"] for c in parsed)
                    profile["date_range"] = _compute_date_range(parsed)
                    logger.info("Used fallback conversation file: %s", candidates[0])
                except Exception as exc:
                    profile["parse_errors"].append(f"Fallback parse failed: {exc}")
            else:
                profile["parse_errors"].append("No conversation JSON found in ZIP")

    logger.info(
        "Claude parse complete: %d conversations, %d user messages",
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
    for name in names:
        if Path(name).name == filename:
            return name
    return None


def _parse_conversations(raw, errors: list) -> list:
    """
    Parse Anthropic's conversations format.

    Anthropic export format (observed 2024-2025):
    [
      {
        "uuid": "...",
        "name": "Draft quarterly review email",
        "created_at": "2024-03-15T10:22:33.000Z",
        "updated_at": "2024-03-15T10:25:00.000Z",
        "chat_messages": [
          {
            "uuid": "...",
            "text": "...",
            "sender": "human"|"assistant",
            "created_at": "2024-03-15T10:22:34.000Z",
            "updated_at": "..."
          }
        ]
      }
    ]

    NOTE: Anthropic may also export as a flat array of messages (no nesting).
    We handle both formats.
    """
    parsed = []

    # Detect format: list of conversation objects vs flat message list
    if not raw:
        return parsed

    first = raw[0] if isinstance(raw, list) else None

    # Format A: list of conversation objects (preferred / newer format)
    if first and ("chat_messages" in first or "messages" in first or "uuid" in first):
        for i, conv in enumerate(raw):
            try:
                parsed.append(_parse_conversation_object(conv, i))
            except Exception as exc:
                errors.append(f"Skipped conversation {i}: {exc}")
        return parsed

    # Format B: flat list of messages — group by conversation_id
    if first and ("sender" in first or "role" in first or "conversation_id" in first):
        try:
            return _parse_flat_messages(raw, errors)
        except Exception as exc:
            errors.append(f"Flat message parse failed: {exc}")
            return parsed

    # Format C: single conversation object (not a list)
    if isinstance(raw, dict):
        try:
            return [_parse_conversation_object(raw, 0)]
        except Exception as exc:
            errors.append(f"Single-object parse failed: {exc}")
            return parsed

    errors.append("Unrecognized conversations.json format")
    return parsed


def _parse_conversation_object(conv: dict, index: int) -> dict:
    conv_id = conv.get("uuid") or conv.get("id") or f"conv_{index}"
    title = conv.get("name") or conv.get("title") or "Untitled"
    create_time = conv.get("created_at") or conv.get("create_time")
    update_time = conv.get("updated_at") or conv.get("update_time")

    messages = conv.get("chat_messages") or conv.get("messages") or []
    user_messages = []
    for m in messages:
        role = m.get("sender") or m.get("role") or ""
        if role in ("human", "user"):
            text = m.get("text") or m.get("content") or ""
            if isinstance(text, list):
                # Handle content blocks
                text = " ".join(
                    b.get("text", "") for b in text
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            if text.strip():
                user_messages.append({
                    "text": text.strip(),
                    "timestamp": m.get("created_at") or m.get("create_time"),
                })

    return {
        "id": conv_id,
        "title": title,
        "create_time": _normalize_timestamp(create_time),
        "update_time": _normalize_timestamp(update_time),
        "user_message_count": len(user_messages),
        "assistant_message_count": len([
            m for m in messages
            if (m.get("sender") or m.get("role")) in ("assistant", "ai")
        ]),
        "user_messages": user_messages,
    }


def _parse_flat_messages(raw: list, errors: list) -> list:
    """Group flat messages by conversation_id."""
    groups: dict = {}
    for msg in raw:
        cid = msg.get("conversation_id") or msg.get("conversation_uuid") or "default"
        if cid not in groups:
            groups[cid] = []
        groups[cid].append(msg)

    result = []
    for i, (cid, msgs) in enumerate(groups.items()):
        user_messages = []
        ts_list = []
        for m in msgs:
            role = m.get("sender") or m.get("role") or ""
            ts = m.get("created_at") or m.get("create_time")
            if ts:
                ts_list.append(ts)
            if role in ("human", "user"):
                text = m.get("text") or m.get("content") or ""
                if text.strip():
                    user_messages.append({"text": text.strip(), "timestamp": ts})

        ts_list.sort()
        result.append({
            "id": cid,
            "title": f"Conversation {i + 1}",
            "create_time": ts_list[0] if ts_list else None,
            "update_time": ts_list[-1] if ts_list else None,
            "user_message_count": len(user_messages),
            "assistant_message_count": len([
                m for m in msgs
                if (m.get("sender") or m.get("role")) in ("assistant", "ai")
            ]),
            "user_messages": user_messages,
        })
    return result


def _normalize_timestamp(ts) -> Optional[str]:
    """Accept ISO string or Unix float, return ISO string."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(ts)).isoformat() + "Z"
        except Exception:
            return None
    if isinstance(ts, str):
        ts = ts.strip()
        if ts.endswith("Z") or "+" in ts:
            return ts
        # Try to parse and re-format
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(ts, fmt).isoformat() + "Z"
            except ValueError:
                continue
        return ts
    return None


def _compute_date_range(conversations: list) -> dict:
    timestamps = [c["create_time"] for c in conversations if c.get("create_time")]
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
        print("Usage: python claude_parser.py <path-to-export.zip> [custom_instructions_text]")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    ci = sys.argv[2] if len(sys.argv) > 2 else None
    result = parse_claude_export(sys.argv[1], custom_instructions=ci)
    pprint.pprint({
        "source": result["source"],
        "conversation_count": result["conversation_count"],
        "message_count": result["message_count"],
        "date_range": result["date_range"],
        "custom_instructions_preview": (result["custom_instructions"] or "")[:200],
        "parse_errors": result["parse_errors"],
    })
