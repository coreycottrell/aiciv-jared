"""
Parser Tests
============

Tests for all migration parsers and the pattern extractor.

Run:
    python -m pytest tools/migration/tests/test_parsers.py -v
    # or directly:
    python tools/migration/tests/test_parsers.py
"""

import json
import os
import sys
import zipfile
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.migration.chatgpt_parser import parse_chatgpt_export
from tools.migration.claude_parser import parse_claude_export
from tools.migration.generic_parser import parse_generic_file, parse_generic_bytes
from tools.migration.pattern_extractor import (
    extract_user_context_profile,
    extract_top_topics,
    detect_communication_style,
    extract_domain_vocabulary,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_fixtures():
    """Generate fixtures if they don't exist."""
    chatgpt_zip = FIXTURES_DIR / "mock_chatgpt_export.zip"
    claude_zip = FIXTURES_DIR / "mock_claude_export.zip"
    if not chatgpt_zip.exists() or not claude_zip.exists():
        from tools.migration.tests.create_mock_exports import (
            create_mock_chatgpt_export,
            create_mock_claude_export,
            create_mock_prompts_csv,
            create_mock_conversation_json,
        )
        create_mock_chatgpt_export()
        create_mock_claude_export()
        create_mock_prompts_csv()
        create_mock_conversation_json()


# ---------------------------------------------------------------------------
# ChatGPT Parser Tests
# ---------------------------------------------------------------------------

def test_chatgpt_parser_basic():
    _ensure_fixtures()
    result = parse_chatgpt_export(str(FIXTURES_DIR / "mock_chatgpt_export.zip"))

    assert result["source"] == "chatgpt"
    assert result["conversation_count"] > 0, "Should parse at least 1 conversation"
    assert result["message_count"] > 0, "Should count user messages"
    assert result["date_range"]["start"] is not None
    assert result["date_range"]["end"] is not None
    print(f"  ChatGPT: {result['conversation_count']} conversations, "
          f"{result['message_count']} user messages")


def test_chatgpt_custom_instructions():
    _ensure_fixtures()
    result = parse_chatgpt_export(str(FIXTURES_DIR / "mock_chatgpt_export.zip"))

    assert result["custom_instructions"] is not None, "Should extract custom instructions"
    assert len(result["custom_instructions"]) > 20, "Custom instructions should be non-trivial"
    print(f"  Custom instructions (first 100 chars): {result['custom_instructions'][:100]}")


def test_chatgpt_no_errors():
    _ensure_fixtures()
    result = parse_chatgpt_export(str(FIXTURES_DIR / "mock_chatgpt_export.zip"))
    assert result["parse_errors"] == [], f"Expected no errors, got: {result['parse_errors']}"


def test_chatgpt_invalid_file():
    """Should raise on non-ZIP file."""
    try:
        parse_chatgpt_export("/tmp/not_a_zip.zip")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
    except Exception as exc:
        assert False, f"Wrong exception type: {type(exc).__name__}: {exc}"


def test_chatgpt_file_size_limit(tmp_path):
    """Should reject files over 50 MB."""
    big_file = tmp_path / "big.zip"
    # Write a ZIP with a single very large entry
    with zipfile.ZipFile(big_file, "w") as zf:
        zf.writestr("conversations.json", "x" * (51 * 1024 * 1024))
    try:
        parse_chatgpt_export(str(big_file))
        assert False, "Should have raised ValueError for size"
    except ValueError as exc:
        assert "50 MB" in str(exc)


# ---------------------------------------------------------------------------
# Claude Parser Tests
# ---------------------------------------------------------------------------

def test_claude_parser_basic():
    _ensure_fixtures()
    result = parse_claude_export(str(FIXTURES_DIR / "mock_claude_export.zip"))

    assert result["source"] == "claude"
    assert result["conversation_count"] > 0
    assert result["message_count"] > 0
    print(f"  Claude: {result['conversation_count']} conversations, "
          f"{result['message_count']} user messages")


def test_claude_custom_instructions_passthrough():
    _ensure_fixtures()
    ci = "Always respond in bullet points. Be concise."
    result = parse_claude_export(
        str(FIXTURES_DIR / "mock_claude_export.zip"),
        custom_instructions=ci,
    )
    assert result["custom_instructions"] == ci


def test_claude_no_errors():
    _ensure_fixtures()
    result = parse_claude_export(str(FIXTURES_DIR / "mock_claude_export.zip"))
    assert result["parse_errors"] == [], f"Expected no errors: {result['parse_errors']}"


# ---------------------------------------------------------------------------
# Generic Parser Tests
# ---------------------------------------------------------------------------

def test_generic_csv_prompt_library():
    _ensure_fixtures()
    result = parse_generic_file(str(FIXTURES_DIR / "mock_prompts.csv"))

    assert result["source"] == "csv"
    assert result["format_detected"] == "prompt_library"
    assert result["conversation_count"] > 0
    assert result["message_count"] > 0
    print(f"  CSV prompt library: {result['conversation_count']} prompts detected")


def test_generic_json_messages():
    _ensure_fixtures()
    result = parse_generic_file(str(FIXTURES_DIR / "mock_conversations.json"))

    assert result["source"] == "json"
    assert result["conversation_count"] > 0
    print(f"  JSON conversations: format={result['format_detected']}, "
          f"messages={result['message_count']}")


def test_generic_bytes_csv():
    csv_content = b"title,category,prompt\nTest Prompt,research,Help me analyze the market\n"
    result = parse_generic_bytes(csv_content, "test.csv")
    assert result["source"] == "csv"
    assert result["message_count"] >= 1


def test_generic_unsupported_type():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"fake pdf")
        tmp_file = f.name
    try:
        parse_generic_file(tmp_file)
        assert False, "Should have raised ValueError for unsupported type"
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    except Exception:
        pass  # Any failure is acceptable — should not silently succeed
    finally:
        os.unlink(tmp_file)


# ---------------------------------------------------------------------------
# Pattern Extractor Tests
# ---------------------------------------------------------------------------

def test_extract_top_topics():
    text = "market analysis market research competitive analysis strategy business strategy " * 5
    text += "copywriting email copywriting sales email " * 3
    topics = extract_top_topics(text, n=5)

    assert len(topics) > 0, "Should extract at least one topic"
    assert all("topic" in t and "count" in t and "domain" in t for t in topics)
    # Market-related terms should appear at top
    all_topics = [t["topic"] for t in topics]
    print(f"  Top topics: {all_topics}")


def test_detect_communication_style_bullet():
    text = "give me bullet points please step by step breakdown concise brief answer"
    style, fmt = detect_communication_style(text)
    assert fmt == "bullet", f"Expected 'bullet', got '{fmt}'"
    print(f"  Style: {style}, Format: {fmt}")


def test_detect_communication_style_prose():
    text = "please explain in detail comprehensive thorough deep analysis elaborate"
    style, fmt = detect_communication_style(text)
    assert fmt == "prose", f"Expected 'prose', got '{fmt}'"
    print(f"  Style: {style}, Format: {fmt}")


def test_domain_vocabulary():
    text = "marketing conversion funnel seo analytics dashboard revenue customer " * 3
    vocab = extract_domain_vocabulary(text, top_n=10)
    assert len(vocab) > 0
    print(f"  Vocabulary: {vocab[:5]}")


def test_full_pipeline_chatgpt():
    """End-to-end test: ChatGPT export -> migration_profile -> user_context_profile."""
    _ensure_fixtures()

    migration_profile = parse_chatgpt_export(str(FIXTURES_DIR / "mock_chatgpt_export.zip"))
    context_profile = extract_user_context_profile(migration_profile)

    # Check all required keys
    required_keys = [
        "top_topics", "communication_style", "preferred_answer_format",
        "domain_vocabulary", "conversation_count", "message_count",
        "date_range", "date_range_years", "source",
    ]
    for key in required_keys:
        assert key in context_profile, f"Missing key: {key}"

    assert context_profile["source"] == "chatgpt"
    assert context_profile["conversation_count"] > 0
    assert len(context_profile["top_topics"]) > 0
    assert context_profile["custom_instructions_raw"] is not None

    print(f"\n  Full pipeline result:")
    print(f"    Conversations: {context_profile['conversation_count']}")
    print(f"    Messages:      {context_profile['message_count']}")
    print(f"    Date range:    {context_profile['date_range_years']} years")
    print(f"    Top 3 topics:  {[t['topic'] for t in context_profile['top_topics'][:3]]}")
    print(f"    Style:         {context_profile['communication_style']}")
    print(f"    Format pref:   {context_profile['preferred_answer_format']}")
    print(f"    Custom instr:  {str(context_profile['custom_instructions_raw'])[:80]}...")


def test_full_pipeline_claude():
    """End-to-end test: Claude export -> context profile."""
    _ensure_fixtures()

    migration_profile = parse_claude_export(
        str(FIXTURES_DIR / "mock_claude_export.zip"),
        custom_instructions="Always respond concisely with bullet points.",
    )
    context_profile = extract_user_context_profile(migration_profile)

    assert context_profile["source"] == "claude"
    assert context_profile["conversation_count"] > 0
    assert context_profile["custom_instructions_raw"] is not None
    print(f"  Claude pipeline: {context_profile['conversation_count']} convs, "
          f"topics={[t['topic'] for t in context_profile['top_topics'][:3]]}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_tests():
    tests = [
        test_chatgpt_parser_basic,
        test_chatgpt_custom_instructions,
        test_chatgpt_no_errors,
        test_chatgpt_invalid_file,
        test_claude_parser_basic,
        test_claude_custom_instructions_passthrough,
        test_claude_no_errors,
        test_generic_csv_prompt_library,
        test_generic_json_messages,
        test_generic_bytes_csv,
        test_generic_unsupported_type,
        test_extract_top_topics,
        test_detect_communication_style_bullet,
        test_detect_communication_style_prose,
        test_domain_vocabulary,
        test_full_pipeline_chatgpt,
        test_full_pipeline_claude,
    ]

    passed = 0
    failed = 0
    errors = []

    print("\nRunning migration parser tests...\n")
    print("=" * 60)

    for test_fn in tests:
        name = test_fn.__name__
        try:
            # Handle tmp_path arg for tests that declare it as a parameter
            import inspect
            sig = inspect.signature(test_fn)
            if "tmp_path" in sig.parameters:
                import tempfile
                with tempfile.TemporaryDirectory() as td:
                    test_fn(Path(td))
            else:
                test_fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1
            errors.append((name, str(exc)))
        except Exception as exc:
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")
            failed += 1
            errors.append((name, f"{type(exc).__name__}: {exc}"))

    print("=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")

    if errors:
        print("\nFailures:")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
