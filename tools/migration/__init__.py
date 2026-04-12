"""
PureBrain AI Migration Portal — Backend Parsing Pipeline
=========================================================

This package provides parsers and extractors for the PureBrain Migration Portal.
Users can import their conversation history from ChatGPT, Claude, and other AI
tools to give PureBrain an instant head-start on their context and preferences.

Package Structure:
    chatgpt_parser.py       — Parse OpenAI export ZIPs (conversations.json + user.json)
    claude_parser.py        — Parse Anthropic export ZIPs (similar JSON format)
    pattern_extractor.py    — Extract topics, style, vocabulary from parsed conversations
    generic_parser.py       — Parse CSV/JSON files from any tool
    migration_api.py        — FastAPI endpoints for the migration flow

Output Format:
    All parsers output a standardized migration_profile dict.
    The pattern extractor outputs a user_context_profile dict (the final AI partner input).

Security:
    - Uploaded files stored in /tmp/purebrain-migration/ (encrypted at rest via luks/dm-crypt)
    - Files auto-deleted after processing, max 24 hours
    - File size limits enforced at upload (50 MB max)
    - Only .zip, .json, .csv file types accepted

Usage:
    from tools.migration.chatgpt_parser import parse_chatgpt_export
    from tools.migration.pattern_extractor import extract_user_context_profile

    migration_profile = parse_chatgpt_export("/tmp/purebrain-migration/user123/chatgpt.zip")
    context_profile   = extract_user_context_profile(migration_profile)
"""

__version__ = "1.0.0"
__all__ = [
    "chatgpt_parser",
    "claude_parser",
    "pattern_extractor",
    "generic_parser",
    "migration_api",
]
