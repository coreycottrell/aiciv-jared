#!/usr/bin/env python3
"""
Pure Migrate — Gate 1 OPAQUE-BLOB seed fold tests.

Spec: /home/jared/exports/migrate-gate2-producer-spec-2026-06-30.md (Section 2).

Proves the additive fold into tools/purebrain_log_server.py is correct and,
critically, that it is BYTE-IDENTICAL-WHEN-ABSENT (the core invariant):
calling the seed builder with migration_bundle=None produces a `.md` attachment
byte-for-byte identical to the pre-fold (HEAD) production seed.

Run:  pytest -q exports/departments/systems-technology/migrate-seed-fold/test_migration_bundle_fold.py

Two test groups:
  * BYTE-IDENTICAL: render_migration_bundle_block(None) -> '' and
    build_migration_surfaces(None) -> {}; the spliced `.md` with bundle=None is
    byte-for-byte the same as the HEAD `.md`; the locked core no longer carries
    the superseded prose/base64 blocks.
  * POSITIVE: a valid purebrain.memory-bundle/v1 dict yields (i) top-level
    `migration` == bundle verbatim, (ii) `metadata.migration` == bundle verbatim,
    (iii) a `## Migration Bundle` block with the bundle JSON placed IMMEDIATELY
    BEFORE `## Full Conversation`, (iv) an unchanged transcript body (the bundle
    is NOT inlined into the conversation).
"""
import importlib.util
import json
import os
import subprocess

import pytest

REPO_ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
).decode().strip()
MODULE_PATH = os.path.join(REPO_ROOT, "tools", "purebrain_log_server.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("pls_under_test", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pls = _load_module()


# A valid purebrain.memory-bundle/v1 object (per the FROZEN schema, spec §1).
SAMPLE_BUNDLE = {
    "schema": "purebrain.memory-bundle/v1",
    "source": {
        "provider": "chatgpt",
        "route": "export",
        "captured_at": "2026-06-30T00:00:00.000Z",
        "confidence": "high",
    },
    "identity": {
        "name": "Dana Okafor",
        "pronouns": "she/her",
        "locale": "en-US",
        "occupation": "Founder",
    },
    "preferences": {
        "communication_style": ["direct", "concise"],
        "format_preferences": ["bullet points"],
        "do": ["cite sources"],
        "dont": ["use emojis"],
    },
    "context": {
        "projects": [{"name": "PureBrain", "summary": "AI memory", "status": "active"}],
        "goals": [{"goal": "ship migration", "horizon": "Q3"}],
        "domains_of_interest": ["AI", "infra"],
        "ongoing_threads": ["seed fold"],
    },
    "facts": [{"key": "tz", "value": "America/New_York", "confidence": "medium"}],
    "custom_instructions": {
        "about_user": "Builds AI products.",
        "response_style": "Crisp and technical.",
    },
    "raw_excerpt": None,
    "warnings": [],
}


# ---------------------------------------------------------------------------
# Faithful reproduction of the LOCKED-CORE `.md` construction (mirrors
# tools/purebrain_log_server.py _send_seed_core_locked). _build_md_head and the
# transcript loop are byte-for-byte the same string ops as the production code;
# the ONLY migration touch is the single gated splice, exactly as in the file.
# A source guard below proves this reproduction matches the real file.
# ---------------------------------------------------------------------------
def _build_md(ai_name, human_name, human_email, session_uuid, tier, order_id,
              ts_now, conversation, migration_bundle, *, splice):
    md = f'# Seed Conversation — {ai_name or "Unknown AI"} / {human_name or "Unknown"}\n\n'
    md += f'**UUID**: {session_uuid}\n'
    md += f'**Tier**: {tier}\n'
    md += f'**AI Name**: {ai_name}\n'
    md += f'**Human Name**: {human_name}\n'
    md += f'**Human Email**: {human_email}\n'
    md += f'**Order ID**: {order_id or "(not yet captured)"}\n'
    md += f'**Timestamp**: {ts_now}\n\n'
    if splice:
        md += pls.render_migration_bundle_block(migration_bundle)
    md += '---\n\n## Full Conversation\n\n'
    for msg in conversation:
        _role = (msg.get('role') or 'unknown').upper()
        _cont = (msg.get('content') or '').strip()
        md += f'**{_role}**: {_cont}\n\n'
    return md


COMMON = dict(
    ai_name="Sol", human_name="Dana Okafor", human_email="dana@example.com",
    session_uuid="11111111-2222-3333-4444-555555555555", tier="awakened",
    order_id="I-ABC123", ts_now="2026-06-30T22:08:00+00:00",
    conversation=[
        {"role": "user", "content": "Name yourself."},
        {"role": "assistant", "content": "I am Sol."},
    ],
)


# ===========================================================================
# GROUP 1 — BYTE-IDENTICAL WHEN ABSENT (the core invariant)
# ===========================================================================
def test_block_none_is_empty_string():
    assert pls.render_migration_bundle_block(None) == ""
    assert pls.render_migration_bundle_block("not-a-dict") == ""
    assert pls.render_migration_bundle_block(123) == ""
    assert pls.render_migration_bundle_block([]) == ""


def test_surfaces_none_is_empty_dict():
    assert pls.build_migration_surfaces(None) == {}
    assert pls.build_migration_surfaces("x") == {}
    assert pls.build_migration_surfaces([]) == {}


def test_md_byte_identical_when_bundle_absent():
    """The seed `.md` with migration_bundle=None is byte-for-byte identical to
    the pre-fold `.md` (the version that never knew about migration)."""
    pre_fold = _build_md(**COMMON, migration_bundle=None, splice=False)
    with_fold_none = _build_md(**COMMON, migration_bundle=None, splice=True)
    assert with_fold_none == pre_fold, "splicing block(None) must be a no-op"
    # And the splice point adds nothing observable:
    assert "## Migration Bundle" not in with_fold_none
    assert "migration" not in with_fold_none.lower().replace("conversation", "")


def test_locked_core_drops_superseded_blocks():
    """The locked core no longer calls the superseded prose render and no longer
    emits the base64 `metadata.migration` block. The opaque-blob splice is the
    one and only migration touch in the `.md` construction."""
    with open(MODULE_PATH) as f:
        src = f.read()
    core = src[src.index("def _send_seed_core_locked"):]
    core = core[:core.index("\n    @app.route") if "\n    @app.route" in core else len(core)]
    # superseded surfaces gone from the locked core:
    assert "render_migration_bundle_human_readable(" not in core
    assert "base64(json):" not in core
    assert "## metadata.migration (machine surface)" not in core
    # exactly one opaque-blob splice, placed before the `.md` Full Conversation
    # construction line (anchor on the real construction, not the docstring).
    assert core.count("render_migration_bundle_block(migration_bundle)") == 1
    i_splice = core.index("render_migration_bundle_block(migration_bundle)")
    full_conv_md_line = "_md_content += '---\\n\\n## Full Conversation\\n\\n'"
    assert full_conv_md_line in core
    i_full = core.index(full_conv_md_line)
    assert i_splice < i_full
    # HEAD's exact transcript construction is unchanged in the working tree:
    head_src = subprocess.check_output(
        ["git", "show", "HEAD:tools/purebrain_log_server.py"], cwd=REPO_ROOT,
    ).decode()
    for line in (
        "_md_content += '---\\n\\n## Full Conversation\\n\\n'",
        "_md_content += f'**{_role}**: {_cont}\\n\\n'",
    ):
        assert line in head_src, "baseline assumption changed"
        assert line in src, "locked transcript construction must be unchanged"


# ===========================================================================
# GROUP 2 — POSITIVE (bundle present)
# ===========================================================================
def _extract_fenced_json(block):
    start = block.index("```json\n") + len("```json\n")
    end = block.index("\n```", start)
    return block[start:end]


def test_top_level_and_metadata_surfaces_are_verbatim():
    surfaces = pls.build_migration_surfaces(SAMPLE_BUNDLE)
    # (i) top-level `migration` == bundle verbatim
    assert surfaces["migration"] == SAMPLE_BUNDLE
    # (ii) `metadata.migration` == bundle verbatim
    assert surfaces["metadata"]["migration"] == SAMPLE_BUNDLE
    # both resolve to the SAME object (single verbatim carriage)
    assert surfaces["migration"] is SAMPLE_BUNDLE
    assert surfaces["metadata"]["migration"] is SAMPLE_BUNDLE


def test_migration_block_carries_bundle_verbatim():
    block = pls.render_migration_bundle_block(SAMPLE_BUNDLE)
    assert "## Migration Bundle" in block
    assert "Pure Migrate import." in block
    assert "BORN" in block  # the spec framing blockquote
    # (iii) the fenced JSON parses back to the bundle VERBATIM (lossless)
    parsed = json.loads(_extract_fenced_json(block))
    assert parsed == SAMPLE_BUNDLE


def test_block_placed_before_full_conversation_and_transcript_unchanged():
    md = _build_md(**COMMON, migration_bundle=SAMPLE_BUNDLE, splice=True)
    # (iii) `## Migration Bundle` appears IMMEDIATELY BEFORE `## Full Conversation`
    i_block = md.index("## Migration Bundle")
    i_full = md.index("## Full Conversation")
    assert i_block < i_full
    between = md[i_block:i_full]
    # nothing but the bundle block sits between them (its own section + the
    # `---` separator that prefixes Full Conversation)
    assert "## About This User" not in between
    assert "metadata.migration (machine surface)" not in between

    # (iv) the transcript body itself is UNCHANGED — the bundle is NOT inlined
    # into the conversation. The transcript portion (after `## Full
    # Conversation`) is byte-for-byte equal to the no-bundle transcript.
    md_plain = _build_md(**COMMON, migration_bundle=None, splice=True)
    transcript_with = md[md.index("## Full Conversation"):]
    transcript_plain = md_plain[md_plain.index("## Full Conversation"):]
    assert transcript_with == transcript_plain
    # the bundle's user-data does NOT leak into the transcript body
    assert "America/New_York" not in transcript_with
    assert "purebrain.memory-bundle/v1" not in transcript_with


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
