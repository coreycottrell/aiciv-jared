"""
Generic CSV / JSON Parser
==========================

Handles the CSV/JSON file upload fallback for any AI tool.

Auto-detects the type of file based on:
    - File extension (.csv, .json)
    - Column/key names
    - Content structure

Supported formats:
    - Prompt library (CSV: title, content/prompt, category)
    - Contact list  (CSV: name, company, role, notes/email)
    - Conversation  (JSON: array with role/content or sender/text keys)
    - Generic docs  (any CSV/JSON — extract text for keyword analysis)

Output: migration_profile dict (same schema as chatgpt_parser output)
"""

import csv
import json
import logging
import io
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Max file size: 10 MB for CSV/JSON (no ZIP overhead here)
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {".csv", ".json"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_generic_file(file_path: str) -> dict:
    """
    Parse a CSV or JSON file uploaded via the "Other Tool" card.

    Args:
        file_path: Absolute path to the uploaded file.

    Returns:
        migration_profile dict with:
            source          — "csv" | "json"
            format_detected — human-readable format description
            conversations   — list of conversation-like dicts (may be empty)
            custom_instructions — None (CSV uploads don't have custom instructions)
            message_count
            conversation_count
            date_range
            raw_records     — list of raw parsed records (for further inspection)
            parse_errors
    """
    path = Path(file_path)
    _validate_file(path)

    profile = {
        "source": path.suffix.lower().lstrip("."),
        "format_detected": "unknown",
        "conversations": [],
        "custom_instructions": None,
        "message_count": 0,
        "conversation_count": 0,
        "date_range": {"start": None, "end": None},
        "raw_records": [],
        "parse_errors": [],
    }

    if path.suffix.lower() == ".csv":
        _parse_csv(path, profile)
    elif path.suffix.lower() == ".json":
        _parse_json(path, profile)
    else:
        profile["parse_errors"].append(f"Unsupported file type: {path.suffix}")

    logger.info(
        "Generic parse complete: format=%s, records=%d, conversations=%d",
        profile["format_detected"],
        len(profile["raw_records"]),
        profile["conversation_count"],
    )
    return profile


def parse_generic_bytes(content: bytes, filename: str) -> dict:
    """
    Parse file content provided as bytes (useful in API context).

    Args:
        content:  Raw file bytes
        filename: Original filename (used to determine file type)

    Returns:
        Same as parse_generic_file
    """
    path = Path(filename)

    profile = {
        "source": path.suffix.lower().lstrip("."),
        "format_detected": "unknown",
        "conversations": [],
        "custom_instructions": None,
        "message_count": 0,
        "conversation_count": 0,
        "date_range": {"start": None, "end": None},
        "raw_records": [],
        "parse_errors": [],
    }

    if len(content) > MAX_FILE_SIZE:
        profile["parse_errors"].append(f"File exceeds 10 MB limit ({len(content)} bytes)")
        return profile

    if path.suffix.lower() == ".csv":
        _parse_csv_bytes(content, profile)
    elif path.suffix.lower() == ".json":
        _parse_json_bytes(content, profile)
    else:
        profile["parse_errors"].append(f"Unsupported file type: {path.suffix}")

    return profile


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def _parse_csv(path: Path, profile: dict):
    try:
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        _parse_csv_bytes(content.encode("utf-8"), profile)
    except Exception as exc:
        profile["parse_errors"].append(f"CSV read error: {exc}")


def _parse_csv_bytes(content: bytes, profile: dict):
    try:
        text = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        profile["raw_records"] = rows

        if not rows:
            profile["format_detected"] = "empty_csv"
            return

        headers = [h.lower().strip() for h in (reader.fieldnames or [])]
        format_type = _detect_csv_format(headers)
        profile["format_detected"] = format_type

        if format_type == "prompt_library":
            _convert_prompts_to_conversations(rows, profile)
        elif format_type == "contact_list":
            _convert_contacts_to_summary(rows, profile)
        elif format_type == "conversation":
            _convert_csv_conversation(rows, headers, profile)
        else:
            # Generic: treat any text-ish column as messages
            _convert_generic_csv(rows, headers, profile)

    except Exception as exc:
        profile["parse_errors"].append(f"CSV parse error: {exc}")


def _detect_csv_format(headers: list) -> str:
    """Detect what kind of CSV this is based on column names."""
    header_set = set(headers)

    prompt_signals = {"prompt", "content", "message", "instruction", "title", "category"}
    contact_signals = {"name", "company", "email", "role", "phone", "linkedin"}
    conv_signals = {"role", "sender", "author", "text", "message"}

    if len(header_set & prompt_signals) >= 2:
        return "prompt_library"
    if len(header_set & contact_signals) >= 2:
        return "contact_list"
    if len(header_set & conv_signals) >= 2:
        return "conversation"
    return "generic"


def _convert_prompts_to_conversations(rows: list, profile: dict):
    """Convert a prompt library CSV into conversations."""
    conversations = []
    for i, row in enumerate(rows):
        # Try common column names for prompt text
        text = (row.get("content") or row.get("prompt") or
                row.get("message") or row.get("instruction") or "")
        title = row.get("title") or row.get("name") or f"Prompt {i + 1}"
        category = row.get("category") or row.get("type") or ""

        if text.strip():
            conversations.append({
                "id": f"prompt_{i}",
                "title": title,
                "create_time": None,
                "update_time": None,
                "user_message_count": 1,
                "assistant_message_count": 0,
                "user_messages": [{"text": text.strip(), "timestamp": None}],
                "category": category,
            })

    profile["conversations"] = conversations
    profile["conversation_count"] = len(conversations)
    profile["message_count"] = len(conversations)


def _convert_contacts_to_summary(rows: list, profile: dict):
    """Contact lists don't map to conversations — store as metadata summary."""
    profile["format_detected"] = "contact_list"
    # Extract company/role info as synthetic conversation queries
    # This simulates "what context does this CRM give us about the user's world"
    companies = list({
        row.get("company", "").strip()
        for row in rows
        if row.get("company", "").strip()
    })[:20]

    roles = list({
        row.get("role", "").strip()
        for row in rows
        if row.get("role", "").strip()
    })[:20]

    # Store as a single synthetic "conversation" for pattern extraction
    synthetic_text = f"Companies: {', '.join(companies)}. Roles: {', '.join(roles)}."
    if synthetic_text.strip(". "):
        profile["conversations"] = [{
            "id": "contact_summary",
            "title": "Contact List Context",
            "create_time": None,
            "update_time": None,
            "user_message_count": 1,
            "assistant_message_count": 0,
            "user_messages": [{"text": synthetic_text, "timestamp": None}],
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = 1


def _convert_csv_conversation(rows: list, headers: list, profile: dict):
    """Convert a CSV that has role/content columns into conversations."""
    user_messages = []
    for row in rows:
        role = (row.get("role") or row.get("sender") or row.get("author") or "").lower()
        text = (row.get("text") or row.get("message") or row.get("content") or "").strip()
        ts = row.get("timestamp") or row.get("created_at") or row.get("date")

        if role in ("user", "human") and text:
            user_messages.append({"text": text, "timestamp": ts})

    if user_messages:
        profile["conversations"] = [{
            "id": "csv_conversation",
            "title": "Imported Conversation",
            "create_time": user_messages[0].get("timestamp"),
            "update_time": user_messages[-1].get("timestamp"),
            "user_message_count": len(user_messages),
            "assistant_message_count": 0,
            "user_messages": user_messages,
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = len(user_messages)


def _convert_generic_csv(rows: list, headers: list, profile: dict):
    """Best-effort: find the most text-heavy column and treat it as content."""
    if not rows:
        return

    # Find the column with the longest average content
    best_col = None
    best_avg = 0
    for col in headers:
        values = [str(r.get(col) or "") for r in rows]
        avg_len = sum(len(v) for v in values) / max(len(values), 1)
        if avg_len > best_avg:
            best_avg = avg_len
            best_col = col

    if not best_col:
        return

    user_messages = []
    for row in rows:
        text = str(row.get(best_col) or "").strip()
        if text and len(text) > 10:
            user_messages.append({"text": text, "timestamp": None})

    if user_messages:
        profile["conversations"] = [{
            "id": "generic_csv",
            "title": f"CSV Import ({best_col})",
            "create_time": None,
            "update_time": None,
            "user_message_count": len(user_messages),
            "assistant_message_count": 0,
            "user_messages": user_messages,
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = len(user_messages)


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def _parse_json(path: Path, profile: dict):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        _parse_json_bytes(content.encode("utf-8"), profile)
    except Exception as exc:
        profile["parse_errors"].append(f"JSON read error: {exc}")


def _parse_json_bytes(content: bytes, profile: dict):
    try:
        text = content.decode("utf-8", errors="replace")
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        profile["parse_errors"].append(f"Invalid JSON: {exc}")
        return
    except Exception as exc:
        profile["parse_errors"].append(f"JSON decode error: {exc}")
        return

    format_type = _detect_json_format(data)
    profile["format_detected"] = format_type
    profile["raw_records"] = data if isinstance(data, list) else [data]

    if format_type == "chatgpt_conversations":
        # This is already handled by chatgpt_parser — re-route hint
        profile["parse_errors"].append(
            "This looks like a ChatGPT conversations.json file. "
            "Use chatgpt_parser.parse_chatgpt_export() for best results."
        )
        # But still parse it as best we can
        _parse_chatgpt_json_direct(data, profile)

    elif format_type == "prompt_library":
        _convert_json_prompts(data, profile)

    elif format_type == "message_array":
        _convert_json_messages(data, profile)

    elif format_type == "config_object":
        _convert_json_config(data, profile)

    else:
        _convert_generic_json(data, profile)


def _detect_json_format(data) -> str:
    """Detect JSON format from structure."""
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            keys = set(first.keys())
            if "mapping" in keys or ("title" in keys and "create_time" in keys):
                return "chatgpt_conversations"
            if "chat_messages" in keys or ("name" in keys and "uuid" in keys):
                return "claude_conversations"
            if "prompt" in keys or "instruction" in keys:
                return "prompt_library"
            if "role" in keys or "sender" in keys:
                return "message_array"
    if isinstance(data, dict):
        keys = set(data.keys())
        if "name" in keys or "description" in keys or "instructions" in keys:
            return "config_object"
    return "generic"


def _parse_chatgpt_json_direct(data: list, profile: dict):
    """Minimal parse of ChatGPT conversations.json without the full ZIP wrapper."""
    conversations = []
    for i, conv in enumerate(data):
        title = conv.get("title") or f"Conversation {i + 1}"
        mapping = conv.get("mapping") or {}
        user_messages = []
        for node in mapping.values():
            msg = node.get("message")
            if not msg:
                continue
            role = (msg.get("author") or {}).get("role", "")
            if role == "user":
                content = msg.get("content") or {}
                parts = content.get("parts") or []
                text = " ".join(p for p in parts if isinstance(p, str)).strip()
                if text:
                    user_messages.append({"text": text, "timestamp": msg.get("create_time")})

        conversations.append({
            "id": conv.get("id") or f"conv_{i}",
            "title": title,
            "create_time": conv.get("create_time"),
            "update_time": conv.get("update_time"),
            "user_message_count": len(user_messages),
            "assistant_message_count": 0,
            "user_messages": user_messages,
        })

    profile["conversations"] = conversations
    profile["conversation_count"] = len(conversations)
    profile["message_count"] = sum(c["user_message_count"] for c in conversations)


def _convert_json_prompts(data: list, profile: dict):
    conversations = []
    for i, item in enumerate(data):
        text = (item.get("prompt") or item.get("instruction") or
                item.get("content") or item.get("text") or "")
        title = item.get("title") or item.get("name") or f"Prompt {i + 1}"
        if isinstance(text, str) and text.strip():
            conversations.append({
                "id": f"prompt_{i}",
                "title": title,
                "create_time": None,
                "update_time": None,
                "user_message_count": 1,
                "assistant_message_count": 0,
                "user_messages": [{"text": text.strip(), "timestamp": None}],
            })
    profile["conversations"] = conversations
    profile["conversation_count"] = len(conversations)
    profile["message_count"] = len(conversations)


def _convert_json_messages(data: list, profile: dict):
    user_messages = []
    for m in data:
        role = (m.get("role") or m.get("sender") or "").lower()
        text = (m.get("content") or m.get("text") or m.get("message") or "").strip()
        if role in ("user", "human") and text:
            user_messages.append({"text": text, "timestamp": m.get("timestamp")})

    if user_messages:
        profile["conversations"] = [{
            "id": "json_conversation",
            "title": "Imported Conversation",
            "create_time": None,
            "update_time": None,
            "user_message_count": len(user_messages),
            "assistant_message_count": 0,
            "user_messages": user_messages,
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = len(user_messages)


def _convert_json_config(data: dict, profile: dict):
    """Parse a config/GPT config JSON (e.g., Custom GPT export)."""
    text_parts = []
    for key in ("instructions", "description", "system_prompt", "name", "context"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            text_parts.append(val.strip())

    if text_parts:
        profile["custom_instructions"] = "\n".join(text_parts)
        profile["conversations"] = [{
            "id": "config_import",
            "title": data.get("name") or "Custom Config",
            "create_time": None,
            "update_time": None,
            "user_message_count": 1,
            "assistant_message_count": 0,
            "user_messages": [{"text": " ".join(text_parts), "timestamp": None}],
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = 1


def _convert_generic_json(data, profile: dict):
    """Best-effort extraction from any JSON structure."""
    texts = _extract_text_from_json(data, depth=0)
    if texts:
        profile["conversations"] = [{
            "id": "generic_json",
            "title": "JSON Import",
            "create_time": None,
            "update_time": None,
            "user_message_count": len(texts),
            "assistant_message_count": 0,
            "user_messages": [{"text": t, "timestamp": None} for t in texts],
        }]
        profile["conversation_count"] = 1
        profile["message_count"] = len(texts)


def _extract_text_from_json(node, depth: int, max_depth: int = 4) -> list:
    """Recursively extract string values from a JSON structure."""
    if depth > max_depth:
        return []
    texts = []
    if isinstance(node, str) and len(node) > 20:
        texts.append(node.strip())
    elif isinstance(node, list):
        for item in node[:100]:
            texts.extend(_extract_text_from_json(item, depth + 1, max_depth))
    elif isinstance(node, dict):
        for v in node.values():
            texts.extend(_extract_text_from_json(v, depth + 1, max_depth))
    return texts


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}. Allowed: {ALLOWED_EXTENSIONS}")
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds 10 MB limit")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import pprint

    if len(sys.argv) < 2:
        print("Usage: python generic_parser.py <path-to-file.csv|.json>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = parse_generic_file(sys.argv[1])
    pprint.pprint({
        "source": result["source"],
        "format_detected": result["format_detected"],
        "conversation_count": result["conversation_count"],
        "message_count": result["message_count"],
        "parse_errors": result["parse_errors"],
    })
