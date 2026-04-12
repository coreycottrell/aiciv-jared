# qa-engineer: AI Migration Portal — Comprehensive Test Plan

**Agent**: qa-engineer
**Domain**: Quality Assurance
**Date**: 2026-02-23

---

## Overview

This test plan covers the AI Migration Portal: a browser-based 4-step wizard that accepts ChatGPT/Claude export ZIP files, parses conversation history client-side, extracts usage patterns and preferences, and delivers personalized insights and task recommendations.

**Feature spec source**: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/ai-migration-portal-spec.md`

**MVP scope** (Phase 1 — what this plan covers):
- ChatGPT and Claude file upload (conversations.zip parsing)
- Pattern extraction: top 5 topics, conversation count, date range, custom instructions
- Step 1–4 navigation flow
- Brevo contact creation and attribute updates
- Email capture validation
- Migration Complete badge

**Out of scope for this plan** (Phase 2+):
- Notion/HubSpot/Canva/Gemini OAuth integrations
- Real-time WebSocket processing status
- LLM-powered NLP extraction (MVP uses frequency analysis)

---

## QA Philosophy for This Feature

**The personalization promise is the product.** The portal's entire value proposition is "we know you from your history." Any output that does not reflect the imported data is not a cosmetic bug — it is a broken product promise. Every personalization claim must be testable with specific, measurable assertions:

- GOOD test: "Insight card contains the exact conversation count from the uploaded file"
- BAD test: "Insight card feels personalized"

Every test case in this plan follows that principle.

---

## Test Environment Requirements

- Modern browser (Chrome 121+, Firefox 122+, Safari 17+)
- Mobile device or emulation: 375px, 390px, 768px viewports
- Network throttling capability (Chrome DevTools > Network > Slow 3G for performance tests)
- Screen reader: NVDA (Windows) or VoiceOver (macOS/iOS)
- Color contrast analyzer (browser extension or axe DevTools)
- A real ChatGPT export ZIP from a test account (see Test Data section)
- Access to Brevo dashboard for integration verification
- Server access to verify temp file deletion (coordinate with full-stack-developer)

---

## Test Data Preparation

**This section must be completed before testing begins.** The most common QA failure is starting without proper test fixtures.

### Mock ChatGPT Export ZIP Structure

ChatGPT exports are ZIP files containing:

```
conversations.zip
├── conversations.json     ← primary target (array of conversation objects)
├── user.json              ← custom instructions
└── message_feedback.json  ← ratings (not parsed for MVP)
```

### conversations.json Schema (Per Conversation Object)

```json
{
  "id": "abc123",
  "title": "Market Analysis Q4 2025",
  "create_time": 1706745600.0,
  "update_time": 1706749200.0,
  "mapping": {
    "msg-id-1": {
      "id": "msg-id-1",
      "message": {
        "id": "msg-id-1",
        "author": { "role": "user" },
        "content": {
          "content_type": "text",
          "parts": ["Can you analyze the Q4 market trends for SaaS?"]
        },
        "create_time": 1706745610.0
      },
      "parent": null,
      "children": ["msg-id-2"]
    },
    "msg-id-2": {
      "id": "msg-id-2",
      "message": {
        "id": "msg-id-2",
        "author": { "role": "assistant" },
        "content": {
          "content_type": "text",
          "parts": ["Here is the Q4 market analysis..."]
        },
        "create_time": 1706745625.0
      },
      "parent": "msg-id-1",
      "children": []
    }
  },
  "conversation_template_id": null,
  "gizmo_id": null
}
```

### user.json Schema

```json
{
  "about_user_message": "I am a B2B SaaS founder. I prefer direct answers without preamble.",
  "about_model_message": "Be concise. Use bullet points. Skip summaries at the end."
}
```

### Required Test Fixtures

Create all of these before testing begins:

| Fixture | File Name | Description | How to Create |
|---|---|---|---|
| **T-01** | `chatgpt-small-valid.zip` | 50 conversations, English, date range Jan–Dec 2025 | Python script (see below) |
| **T-02** | `chatgpt-large-valid.zip` | 10,000 conversations | Python script, multiplied data |
| **T-03** | `chatgpt-with-custom-instructions.zip` | 50 conversations + populated user.json | Include user.json with text |
| **T-04** | `chatgpt-no-custom-instructions.zip` | 50 conversations + empty user.json `{}` | user.json with `{}` |
| **T-05** | `chatgpt-empty-conversations.zip` | `conversations.json` = `[]` | conversations.json is empty array |
| **T-06** | `chatgpt-no-conversations-file.zip` | ZIP with only user.json, no conversations.json | Omit conversations.json |
| **T-07** | `chatgpt-malformed-json.zip` | conversations.json is not valid JSON | `[{broken json` |
| **T-08** | `chatgpt-xss-payload.zip` | Conversation titles and content contain XSS payloads | Include `<script>alert(1)</script>` in title field |
| **T-09** | `chatgpt-special-chars.zip` | Custom instructions contain emoji, curly quotes, RTL text | Mix of Unicode characters |
| **T-10** | `chatgpt-non-english.zip` | Conversations primarily in Japanese and Arabic | Use lorem-style content in target languages |
| **T-11** | `chatgpt-long-titles.zip` | Conversation titles 500+ characters long | Pad title field with repeated text |
| **T-12** | `not-a-zip.zip` | A JPEG renamed to .zip | Take any image, rename extension |
| **T-13** | `empty.zip` | A valid ZIP archive with no files inside | `zip empty.zip -` (empty) |
| **T-14** | `oversized.zip` | File exceeding the upload size limit (e.g., 600MB) | Generate with dd or by duplicating T-02 |
| **T-15** | `zip-bomb.zip` | Highly compressed file (small on disk, huge uncompressed) | Nested ZIPs or repeated null bytes compressed |
| **T-16** | `path-traversal.zip` | ZIP with entry named `../../etc/passwd` | Use Python zipfile to set entry name directly |
| **T-17** | `claude-small-valid.zip` | 50 conversations in Claude export format | Mirror ChatGPT structure (Claude format is similar) |
| **T-18** | `chatgpt-single-conversation.zip` | Exactly 1 conversation | conversations.json with 1 entry |
| **T-19** | `chatgpt-all-same-topic.zip` | All 50 conversations have identical titles | Set title = "Market Analysis" on all 50 |

### Python Script to Generate Test Fixtures

```python
#!/usr/bin/env python3
"""Generate mock ChatGPT export ZIP files for QA testing."""

import json
import zipfile
import random
from datetime import datetime, timedelta
from pathlib import Path

TOPICS = [
    "Market Analysis", "Copywriting", "Code Review", "Hiring Decision",
    "Product Positioning", "Competitive Analysis", "Customer Email",
    "Business Strategy", "Data Analysis", "Presentation"
]

def generate_conversation(idx, topic=None, date_offset_days=0):
    """Generate a single conversation object."""
    if topic is None:
        topic = random.choice(TOPICS)

    base_time = datetime(2024, 1, 1) + timedelta(days=date_offset_days)
    timestamp = base_time.timestamp()

    msg_id_user = f"msg-user-{idx}"
    msg_id_assistant = f"msg-asst-{idx}"

    return {
        "id": f"conv-{idx}",
        "title": f"{topic} - Session {idx}",
        "create_time": timestamp,
        "update_time": timestamp + 300,
        "mapping": {
            msg_id_user: {
                "id": msg_id_user,
                "message": {
                    "id": msg_id_user,
                    "author": {"role": "user"},
                    "content": {
                        "content_type": "text",
                        "parts": [f"Help me with {topic.lower()} for my B2B SaaS company."]
                    },
                    "create_time": timestamp
                },
                "parent": None,
                "children": [msg_id_assistant]
            },
            msg_id_assistant: {
                "id": msg_id_assistant,
                "message": {
                    "id": msg_id_assistant,
                    "author": {"role": "assistant"},
                    "content": {
                        "content_type": "text",
                        "parts": [f"Here is my analysis of {topic.lower()}..."]
                    },
                    "create_time": timestamp + 5
                },
                "parent": msg_id_user,
                "children": []
            }
        },
        "conversation_template_id": None,
        "gizmo_id": None
    }

def build_zip(output_path, conversations, user_json=None, include_conversations_file=True):
    """Build a ChatGPT-style export ZIP."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if include_conversations_file:
            zf.writestr("conversations.json", json.dumps(conversations, indent=2))

        if user_json is not None:
            zf.writestr("user.json", json.dumps(user_json, indent=2))
        else:
            zf.writestr("user.json", "{}")

        zf.writestr("message_feedback.json", "[]")

def generate_fixtures(output_dir="./test-fixtures"):
    Path(output_dir).mkdir(exist_ok=True)

    # T-01: Small valid (50 conversations)
    convs_50 = [generate_conversation(i, date_offset_days=i*7) for i in range(50)]
    build_zip(f"{output_dir}/chatgpt-small-valid.zip", convs_50)

    # T-02: Large valid (10,000 conversations)
    convs_10k = [generate_conversation(i, date_offset_days=i) for i in range(10000)]
    build_zip(f"{output_dir}/chatgpt-large-valid.zip", convs_10k)

    # T-03: With custom instructions
    custom_user = {
        "about_user_message": "I am a B2B SaaS founder running a 15-person company.",
        "about_model_message": "Be direct. No preamble. Use bullet points. Max 3 paragraphs."
    }
    build_zip(f"{output_dir}/chatgpt-with-custom-instructions.zip", convs_50, user_json=custom_user)

    # T-04: Without custom instructions
    build_zip(f"{output_dir}/chatgpt-no-custom-instructions.zip", convs_50, user_json={})

    # T-05: Empty conversations array
    build_zip(f"{output_dir}/chatgpt-empty-conversations.zip", [])

    # T-06: No conversations.json file
    build_zip(f"{output_dir}/chatgpt-no-conversations-file.zip", None, include_conversations_file=False)

    # T-07: Malformed JSON
    with zipfile.ZipFile(f"{output_dir}/chatgpt-malformed-json.zip", 'w') as zf:
        zf.writestr("conversations.json", "[{broken json, not valid")
        zf.writestr("user.json", "{}")

    # T-08: XSS payload
    xss_convs = convs_50.copy()
    xss_convs[0]["title"] = "<script>alert('XSS')</script>"
    xss_convs[1]["mapping"]["msg-user-1"]["message"]["content"]["parts"] = [
        "<img src=x onerror=alert(1)>",
        "javascript:alert(document.cookie)"
    ]
    build_zip(f"{output_dir}/chatgpt-xss-payload.zip", xss_convs)

    # T-09: Special characters
    special_user = {
        "about_user_message": "Préférences: réponses courtes. 日本語も大丈夫。",
        "about_model_message": "\u202bArabic RTL test\u202c. "smart quotes" and 'curly'."
    }
    build_zip(f"{output_dir}/chatgpt-special-chars.zip", convs_50, user_json=special_user)

    # T-11: Long titles
    long_title_convs = [generate_conversation(i) for i in range(20)]
    for c in long_title_convs:
        c["title"] = "Market Analysis " * 30  # ~480 chars
    build_zip(f"{output_dir}/chatgpt-long-titles.zip", long_title_convs)

    # T-16: Path traversal
    with zipfile.ZipFile(f"{output_dir}/path-traversal.zip", 'w') as zf:
        info = zipfile.ZipInfo("../../etc/passwd")
        zf.writestr(info, "root:x:0:0:root:/root:/bin/bash")
        zf.writestr("conversations.json", json.dumps(convs_50))

    # T-17: Claude export (same structure)
    claude_convs = [generate_conversation(i, date_offset_days=i*5) for i in range(30)]
    build_zip(f"{output_dir}/claude-small-valid.zip", claude_convs)

    # T-18: Single conversation
    build_zip(f"{output_dir}/chatgpt-single-conversation.zip", [generate_conversation(0)])

    # T-19: All same topic
    same_topic = [generate_conversation(i, topic="Market Analysis") for i in range(50)]
    build_zip(f"{output_dir}/chatgpt-all-same-topic.zip", same_topic)

    # T-12: Not a zip (rename manually after generating)
    with open(f"{output_dir}/not-a-zip.zip", 'wb') as f:
        f.write(b'\xFF\xD8\xFF\xE0' + b'\x00' * 100)  # JPEG magic bytes

    # T-13: Empty zip
    with zipfile.ZipFile(f"{output_dir}/empty.zip", 'w') as zf:
        pass  # no files

    print(f"Generated fixtures in {output_dir}")
    print("NOTE: Create T-14 (oversized) and T-15 (zip bomb) manually.")
    print("T-14: Use dd to create a large file, then compress it.")
    print("T-15: Use nested ZIPs or a known zip bomb sample.")

if __name__ == "__main__":
    generate_fixtures()
```

**Run this script** from the project root to generate all fixtures:
```bash
python3 generate_test_fixtures.py
```

---

## Functional Tests

### Module F1: ZIP Upload

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F1-01 | Valid ChatGPT export upload | T-01 (`chatgpt-small-valid.zip`) | Upload succeeds, progress indicator appears, transitions to Step 2 | P0 |
| F1-02 | Valid Claude export upload | T-17 (`claude-small-valid.zip`) | Upload succeeds, Claude branding shown, transitions to Step 2 | P0 |
| F1-03 | Invalid file type (JPEG renamed) | T-12 (`not-a-zip.zip`) | Error shown: "This file doesn't appear to be a valid export ZIP" | P0 |
| F1-04 | Empty ZIP (no files inside) | T-13 (`empty.zip`) | Error shown: "This ZIP file appears to be empty" | P1 |
| F1-05 | Oversized ZIP exceeding limit | T-14 (600MB file) | Error shown BEFORE upload begins: "File too large (limit: X MB)" | P0 |
| F1-06 | ZIP with no conversations.json | T-06 (`chatgpt-no-conversations-file.zip`) | Error shown: "No conversation data found in this export" | P1 |
| F1-07 | Drag-and-drop upload | Drag T-01 onto the upload zone | Same behavior as click-to-upload | P1 |
| F1-08 | Upload while another upload is in progress | Start T-02, then attempt to upload T-01 | Either: queues T-01 or rejects with "Upload already in progress" | P2 |
| F1-09 | Network failure mid-upload | Throttle to offline after 50% | Clear error state; retry button available | P1 |
| F1-10 | Upload feedback: progress indicator | T-02 (large file, slow connection) | Upload percentage shown; not a frozen spinner | P1 |
| F1-11 | Success state after upload | T-01 | Upload zone shows "conversations ready" state with conversation count | P0 |
| F1-12 | Replace uploaded file | Upload T-01, then upload T-17 | Second file replaces first; data from T-01 discarded | P1 |

### Module F2: JSON Parsing

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F2-01 | Parse valid conversations.json | T-01 (50 conversations) | Parser returns 50 conversation objects with correct fields | P0 |
| F2-02 | Parse malformed JSON | T-07 (`chatgpt-malformed-json.zip`) | Error shown: "Could not read this export file. Try exporting again from ChatGPT." | P0 |
| F2-03 | Parse empty conversations array | T-05 (`chatgpt-empty-conversations.zip`) | Graceful: "No conversations found in this export" — no crash | P0 |
| F2-04 | Parse conversations with all required fields | T-01 | Each conversation has: id, title, create_time, update_time, mapping | P0 |
| F2-05 | Parse conversations with missing optional fields | Any fixture with null gizmo_id | Parser handles null/missing fields without crashing | P1 |
| F2-06 | Parse 10,000 conversations | T-02 (`chatgpt-large-valid.zip`) | All 10,000 parsed correctly; no truncation | P0 |
| F2-07 | Parse custom instructions from user.json | T-03 (`chatgpt-with-custom-instructions.zip`) | Custom instructions text extracted and stored | P0 |
| F2-08 | Parse when user.json is empty `{}` | T-04 (`chatgpt-no-custom-instructions.zip`) | No error; custom instructions section shows "None found" | P1 |
| F2-09 | Parse single conversation | T-18 (`chatgpt-single-conversation.zip`) | Returns 1 conversation; date range shows same date for start and end | P1 |
| F2-10 | Parse with XSS payloads in content | T-08 (`chatgpt-xss-payload.zip`) | Payloads are HTML-escaped in all output; no script execution | P0 |
| F2-11 | Parse with special characters and emoji | T-09 (`chatgpt-special-chars.zip`) | Characters render correctly; no encoding errors | P1 |
| F2-12 | Correct date range calculation | T-01 (Jan–Dec 2025 range) | Date range displayed as "~1 year" or "Jan 2025 – Dec 2025" | P0 |
| F2-13 | Date range: single day | T-18 (1 conversation) | Date range shows single date, not a range with negative duration | P1 |

### Module F3: Pattern Extraction

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F3-01 | Topic counting: identifies top topic | T-19 (all "Market Analysis") | "Market Analysis" appears as top topic with count = 50 | P0 |
| F3-02 | Topic counting: top 5 returned | T-01 (10 topics, 5 per topic) | All 5 distinct topics identified | P0 |
| F3-03 | Topic counting: correct ranking | T-01 with skewed distribution | Topics ranked by frequency (highest count first) | P0 |
| F3-04 | Conversation count accuracy | T-01 (50 conversations) | Count displayed = 50 (not 49, not 51) | P0 |
| F3-05 | Conversation count: large dataset | T-02 (10,000 conversations) | Count displayed = 10,000 | P0 |
| F3-06 | Date range: multi-year span | T-02 (conversations spanning 2023–2025) | Date range correctly calculated as ~2 years | P0 |
| F3-07 | Custom instructions absorbed | T-03 (custom instructions present) | Custom instructions text appears in Step 2 preview (first 120 chars) | P0 |
| F3-08 | Communication style extraction | T-03 (instructions include "be direct, no preamble") | Style tag extracted: e.g., "direct, no preamble" | P1 |
| F3-09 | Topic extraction from long titles | T-11 (very long titles) | Parser does not crash; titles truncated gracefully for display | P1 |
| F3-10 | Pattern extraction: non-English titles | T-10 (Japanese/Arabic titles) | Parser does not crash; topics extracted even if imperfect | P1 |
| F3-11 | Preferred format detection | T-03 (user.json says "use bullet points") | Format preference "bullet points" stored in extracted profile | P1 |

### Module F4: Step Navigation

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F4-01 | Step 1 → Step 2 (normal flow) | Upload T-01, click "Continue with what I have" | Transitions to Step 2; progress bar shows step 2 active | P0 |
| F4-02 | Step 2 → Step 3 (start import) | Review screen, click "Start Import" | Transitions to Step 3 processing screen | P0 |
| F4-03 | Step 3 → Step 4 (processing complete) | Processing finishes | Transitions automatically to Step 4 | P0 |
| F4-04 | Back navigation: Step 2 → Step 1 | On Step 2, click Back | Returns to Step 1; previously uploaded file state preserved | P1 |
| F4-05 | Back navigation: Step 3 (processing in progress) | On Step 3 while processing | Back button disabled OR prompts "Cancel processing?" | P1 |
| F4-06 | Skip entire migration | On portal entry banner, click "Skip for now" | Portal dismisses migration banner; user reaches main portal dashboard | P0 |
| F4-07 | Skip in Step 1: "Continue with what I have" | No file uploaded, click "Continue" | Either: proceed to Step 2 with no data, or prompt "No file uploaded — are you sure?" | P1 |
| F4-08 | Progress bar: correct step highlighted | Navigate through all 4 steps | Progress bar shows correct active step at each screen | P1 |
| F4-09 | Step 4 → Main portal | Click "Go to my PureBrain" | Navigates to main portal chat interface | P0 |
| F4-10 | Browser back button | Navigate to Step 3, press browser Back | Returns to Step 2 (not to Step 3 in processing state) | P2 |
| F4-11 | Deep link to Step 2 | Navigate directly to step 2 URL | Redirects to Step 1 (cannot enter mid-flow without data) | P2 |

### Module F5: Data Display — Insight Cards (Step 3)

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F5-01 | Conversation count in insight card | T-01 (50 conversations) | Insight card reads "50 conversations" (exact count, not rounded) | P0 |
| F5-02 | Top topic name in insight card | T-19 (all Market Analysis) | Insight card reads "You asked about market analysis [N] times" | P0 |
| F5-03 | Custom instructions in insight card | T-03 (custom instructions present) | Card reads "Your Custom Instructions say..." with actual text preview | P0 |
| F5-04 | No custom instructions: card hidden | T-04 (empty user.json) | No "Custom Instructions" insight card displayed | P1 |
| F5-05 | Date range in checklist | T-01 (1 year range) | "3.2 years of history" (or appropriate for T-01 date range) | P0 |
| F5-06 | Insight cards animate in sequentially | T-02 (large dataset, processing time) | Cards appear one by one, not all at once | P1 |
| F5-07 | Checklist items check off in real time | T-02 | "Communication style detected" checks off when complete | P1 |
| F5-08 | XSS in insight card display | T-08 (XSS payload in title) | Payload rendered as text, not executed | P0 |
| F5-09 | Long topic name in insight card | T-11 | Long topic name truncated with ellipsis, no overflow | P1 |
| F5-10 | Progress bar animates | T-02 | Progress bar animates from 0% to 100% during processing | P1 |
| F5-11 | "Estimated time" shown | T-02 | Estimated time remaining displayed | P2 |

### Module F6: Task Generation (Step 4)

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F6-01 | Tasks reflect top topic | T-19 (all Market Analysis) | At least 1 task card references "market analysis" | P0 |
| F6-02 | Task contains specific count | T-01 (N conversations about top topic) | Task card reads "You [verb]ed [topic] [N] times in ChatGPT" | P0 |
| F6-03 | Writing task when writing in custom instructions | T-03 (writing-focused custom instructions) | Task card for "Write with your voice" appears | P1 |
| F6-04 | Minimum 1 task always shown | T-05 (0 conversations) | Even with minimal data, at least 1 generic starter task shown | P0 |
| F6-05 | Maximum 5 tasks shown | T-02 (large dataset, many topics) | No more than 5 task cards displayed | P1 |
| F6-06 | "Start this task" link pre-fills chat | T-01, click "Start this task" | Chat opens with a pre-filled starter prompt (not blank chat) | P0 |
| F6-07 | "Go to my PureBrain" works | Any completed migration | Navigates to main portal chat | P0 |
| F6-08 | Migration Complete badge appears | Complete full flow | Badge visible in portal dashboard after Step 4 completion | P0 |
| F6-09 | Badge shows correct absorbed count | T-01 (50 conversations) | Badge reads "Absorbed: 50 conversations" | P0 |

### Module F7: Step 2 — Review and Remove

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F7-01 | Remove conversation history | T-03, click "Remove" on conversations row | Row removed from display; conversation data not used in Step 3 | P0 |
| F7-02 | Remove custom instructions | T-03, click "Remove" on custom instructions row | Custom instructions removed; no instruction card appears in Step 3 | P0 |
| F7-03 | Remove all data categories | Remove all items | User can still proceed to Step 3 (graceful empty state) OR shown "Nothing to import" | P1 |
| F7-04 | Removed data does not appear in Step 3 | Remove conversations, proceed | No conversation count in insight cards; no conversation-based tasks in Step 4 | P0 |
| F7-05 | Privacy note visible above CTA | Any data loaded in Step 2 | Privacy note is visible without scrolling (above "Start Import" button) | P0 |
| F7-06 | "See full privacy policy" link works | Click privacy policy link | Opens privacy policy (new tab or modal) | P1 |
| F7-07 | Data counts shown correctly | T-01 (50 conversations) | Step 2 shows "50 conversations" and correct date range | P0 |
| F7-08 | Custom instructions preview: 120 char truncation | T-03 (long custom instructions) | Preview shows first 120 characters then "..." | P1 |

### Module F8: Brevo Integration

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F8-01 | Contact created in Brevo on email capture | Submit email in portal | Brevo contact record created with email | P0 |
| F8-02 | Migration attributes written to Brevo | Complete migration with T-03 | `conversation_count`, `top_topics`, `migration_status` attributes set on contact | P0 |
| F8-03 | `migration_status` = "complete" after Step 4 | Complete all steps | Brevo attribute `migration_status` = "complete" | P0 |
| F8-04 | `competitor` attribute correct | Upload ChatGPT export | Brevo `competitor` = "chatgpt" | P0 |
| F8-05 | Duplicate email handling | Submit email already in Brevo | Contact updated (not duplicated) | P1 |
| F8-06 | Brevo API failure: graceful degradation | Simulate Brevo API down | Migration flow continues; error logged server-side; user not shown "Brevo error" | P1 |
| F8-07 | Brevo API key not exposed client-side | Inspect browser network tab and source | API key not visible in any client-side code or network request | P0 |

### Module F9: Email Capture

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| F9-01 | Valid email accepted | `user@company.com` | Form submits successfully | P0 |
| F9-02 | Invalid email rejected | `notanemail` | Validation error shown; form not submitted | P0 |
| F9-03 | Missing @ rejected | `usercompany.com` | Validation error shown | P0 |
| F9-04 | Trailing whitespace trimmed | `  user@company.com  ` | Whitespace stripped before submission | P1 |
| F9-05 | Empty submission blocked | Submit with blank field | Error shown; form not submitted | P0 |
| F9-06 | Very long email address | 256+ character email | Validation error or graceful handling | P1 |
| F9-07 | Email field: keyboard type on mobile | Tap email field on iOS/Android | Keyboard shows email layout (@ key visible) | P1 |

---

## Edge Cases

| ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| EC-01 | ZIP with no conversations.json | T-06 | Error: "No conversation data found. Check that you downloaded the correct export." | P0 |
| EC-02 | conversations.json with 0 conversations | T-05 | No crash; graceful state: "No conversations found" | P0 |
| EC-03 | 10,000 conversations parsing (performance) | T-02 | Parses without browser crash; see performance targets | P0 |
| EC-04 | Very long conversation titles | T-11 (500+ char titles) | Titles truncated in display; no layout overflow | P1 |
| EC-05 | Special characters in conversation content | T-09 (emoji, RTL, curly quotes) | Characters render correctly; no encoding errors; no crash | P1 |
| EC-06 | User removes all data categories in Step 2 | Remove all items | Flow continues without breaking; Step 3 shows minimal/no insights | P1 |
| EC-07 | User closes browser mid-Step 3 (processing) | Close browser during processing | On return: either processing resumes OR user shown "Your migration was interrupted. Restart?" | P1 |
| EC-08 | User closes browser mid-Step 1 (no data uploaded) | Close without uploading | On return: Step 1 shown fresh (no stale state) | P1 |
| EC-09 | User skips migration then returns later | Skip banner, return via settings | Migration assistant accessible again; not locked out | P1 |
| EC-10 | Non-English conversation content | T-10 (Japanese/Arabic) | No crash; topic extraction may be imperfect but gracefully degraded | P1 |
| EC-11 | Single conversation | T-18 (1 conversation) | All steps complete; date range shows single date; 1 task card generated | P1 |
| EC-12 | All conversations share identical topic | T-19 (all Market Analysis) | Top topic = "Market Analysis" with count 50; all tasks reference it | P1 |
| EC-13 | Processing timeout (>5 minutes) | T-02 on very slow server | "We'll email you when it's ready" option appears after 5 minutes | P2 |
| EC-14 | Very long custom instructions | Custom instructions >10,000 chars | No crash; preview truncated at 120 chars; full text stored correctly | P1 |
| EC-15 | Concurrent migration attempts (two tabs) | Open portal in two tabs, upload in both | Server handles gracefully; no data corruption | P2 |

---

## Responsive Tests

All tests verified at: 375px (iPhone SE), 390px (iPhone 14), 768px (iPad portrait), 1440px (Desktop)

| ID | Test Case | Expected at All Widths | Priority |
|---|---|---|---|
| R-01 | Portal entry banner visible | Banner fully readable; no truncation of key text | P0 |
| R-02 | Step 1 upload card layout | Upload button accessible; not obscured or clipped | P0 |
| R-03 | Step 2 review cards stack correctly | Data rows readable; Remove buttons accessible | P0 |
| R-04 | Step 3 progress bar and insight cards | Cards stack vertically on mobile; no horizontal overflow | P0 |
| R-05 | Step 4 task cards | Task cards stack; "Start this task" buttons full-width on mobile | P0 |
| R-06 | Migration Complete badge | Badge renders fully; no text overflow | P1 |
| R-07 | iOS file upload behavior | On iOS Safari: tapping "Upload" opens Files app (not camera roll) | P0 |
| R-08 | Touch targets minimum 44x44px | All buttons and links meet minimum tap target size | P0 |
| R-09 | No horizontal scroll at any breakpoint | Page does not require horizontal scrolling at 375px | P0 |
| R-10 | Progress bar readable on mobile | Step indicator labels not overlapping on 375px | P1 |
| R-11 | Long topic names on mobile | Topics truncated properly at small widths; no overflow | P1 |
| R-12 | Email field keyboard on mobile | Email input triggers email keyboard (input type="email") | P1 |

**Mobile-specific note for iOS**: Safari on iOS presents the camera roll by default for file input elements. The user must navigate to the Files app to select a ZIP. This is a UX friction point that should be called out in the UI: "Tap the upload button, then select Browse to find your file in Files." Test this on a real device, not emulation.

---

## Accessibility Tests

| ID | Test Case | Expected Result | Priority |
|---|---|---|---|
| A-01 | Keyboard navigation: Step 1 | Tab order reaches all interactive elements in logical order | P0 |
| A-02 | Keyboard navigation: Step 2 Remove buttons | Each Remove button reachable and activatable via keyboard | P0 |
| A-03 | Keyboard navigation: Step 4 task cards | All "Start this task" buttons keyboard accessible | P0 |
| A-04 | Screen reader: upload zone label | Screen reader announces "Upload your ChatGPT export ZIP file" (or equivalent) | P0 |
| A-05 | Screen reader: step progress announcement | Screen reader announces "Step 2 of 4" when transitioning | P1 |
| A-06 | Screen reader: error messages | Upload error messages announced immediately (not visually hidden) | P0 |
| A-07 | Screen reader: processing progress | Step 3 progress updates announced to screen reader (aria-live region) | P1 |
| A-08 | Screen reader: insight cards | Insight card content readable by screen reader | P1 |
| A-09 | Color contrast: all body text | WCAG AA minimum: 4.5:1 ratio for normal text | P0 |
| A-10 | Color contrast: button text | WCAG AA minimum: 4.5:1 ratio for button labels | P0 |
| A-11 | Color contrast: insight card text on dark bg | White text on #080a12 background: passes AA | P0 |
| A-12 | Focus indicator visible | Focus ring visible on all interactive elements; not suppressed | P0 |
| A-13 | Focus management: step transitions | When step changes, focus moved to new step heading | P1 |
| A-14 | Focus management: modal "How to export" | Focus trapped in modal; returns to trigger on close | P1 |
| A-15 | Skip navigation link | Skip-to-content link present and functional | P2 |
| A-16 | Alt text: all icons and images | Icons have descriptive alt text or aria-label; decorative icons have aria-hidden | P1 |
| A-17 | Animated orb: reduced motion | When prefers-reduced-motion is enabled, orb animation stops or slows significantly | P1 |
| A-18 | Error state ARIA | Invalid email field has aria-invalid="true" and aria-describedby pointing to error message | P0 |

**Color contrast quick check targets:**
- Text `#ffffff` on `#080a12` background: ratio 19.1:1 (passes AAA)
- Orange `#f1420b` on `#080a12` background: calculate carefully — orange on near-black can fail if text is small
- Ensure any orange text meets 4.5:1 against its background

---

## Security Tests

Coordinate with `security-engineer-tech` for server-side verification of the following.

### File Upload Security

| ID | Test Case | Expected Result | Priority |
|---|---|---|---|
| S-01 | ZIP bomb detection | T-15 (`zip-bomb.zip`) — server must detect decompression ratio and reject before full extraction | P0 |
| S-02 | Non-ZIP MIME type rejected | T-12 (`not-a-zip.zip`) — server validates magic bytes (PK header), not just file extension | P0 |
| S-03 | Oversized file rejected server-side | T-14 (600MB) — rejected at server before reaching parser (client-side limit is not sufficient alone) | P0 |
| S-04 | Path traversal in ZIP entries | T-16 (`path-traversal.zip`) — server extracts to sandboxed temp directory; `../` entries stripped or rejected | P0 |
| S-05 | XSS via conversation content | T-08 (XSS payload) — all conversation content HTML-escaped before rendering; no script execution | P0 |
| S-06 | Temp file deletion verified | Upload T-01, complete migration, check server temp directory | Temp files deleted within expected window (spec says: max 24 hours; target: immediately after processing) | P0 |
| S-07 | Temp file deletion on error | Upload T-07 (malformed JSON) — processing fails — check server temp directory | Temp file deleted even when processing fails | P0 |
| S-08 | File size limit: client-side only? | Bypass client-side limit via curl, send oversized file | Server enforces limit independently of client | P0 |

### API and Integration Security

| ID | Test Case | Expected Result | Priority |
|---|---|---|---|
| S-09 | Brevo API key not client-side | Inspect all JavaScript source files and network requests | Brevo API key not present in any client-side code | P0 |
| S-10 | Migration data access control | Attempt to access another user's migration data by modifying user ID in API calls | Server returns 403 or 404; no cross-user data leakage | P0 |
| S-11 | CSRF protection on file upload endpoint | POST to upload endpoint without valid CSRF token | Request rejected | P1 |
| S-12 | Rate limiting on upload endpoint | Rapid successive uploads (20+ in 60 seconds) | Rate limit applied; temporary block with informative error | P1 |
| S-13 | localStorage sensitivity audit | Inspect localStorage after completing migration | No sensitive data (custom instructions text, conversation content) in localStorage | P0 |
| S-14 | Conversation content not in DOM unnecessarily | Inspect DOM after Step 3 | Raw conversation text not rendered in hidden DOM elements | P1 |
| S-15 | HTTPS enforcement | Attempt to access migration portal over HTTP | Redirect to HTTPS; no mixed content warnings | P0 |

### Data Privacy Verification

| ID | Test Case | Expected Result | Priority |
|---|---|---|---|
| S-16 | Privacy note visible before data submission | Observe Step 2 | Privacy note visible above "Start Import" CTA without scrolling | P0 |
| S-17 | "Data never used for training" stated | Review Step 2 and any consent UI | Statement present and accurate | P0 |
| S-18 | Removed data not processed | Remove conversations in Step 2, check Step 3 | No conversation-based insights appear; server logs confirm conversations not processed | P0 |

---

## Performance Tests

All performance tests should be run on a mid-range mobile device (or emulated equivalent) with network throttled to Fast 3G for mobile targets.

| ID | Test Case | Target | Notes |
|---|---|---|---|
| P-01 | Parse 100 conversations: time to Step 2 | < 2 seconds | Measured from upload complete to Step 2 display |
| P-02 | Parse 1,000 conversations: time to Step 2 | < 5 seconds | |
| P-03 | Parse 10,000 conversations: time to Step 2 | < 20 seconds | Use T-02; acceptable if loading indicator shown |
| P-04 | Memory usage during ZIP extraction (100 convs) | < 50MB heap increase | Chrome DevTools Memory tab |
| P-05 | Memory usage during ZIP extraction (10,000 convs) | < 200MB heap increase | No tab crash |
| P-06 | UI remains responsive during parsing | No jank | Main thread not blocked; scroll/tap responsive during parsing |
| P-07 | Step 3 animated orb: frame rate | >= 30fps on mid-range mobile | Chrome DevTools Performance > FPS meter |
| P-08 | Step 3 insight card animation: smoothness | No stutter | Transitions at 60fps on desktop |
| P-09 | Step 4 load time after processing completes | < 1 second | Time from Step 3 completion to Step 4 fully rendered |
| P-10 | Total migration time: 100 conversations | < 30 seconds end-to-end | Upload through Step 4 display |
| P-11 | Browser memory: no leak across steps | Heap stable after completing flow | No continuous heap growth; GC runs |

**Note on P-06**: JavaScript should use a Web Worker for JSON parsing if 10,000+ conversations cause main thread blocking. This should be flagged to the developer if the browser becomes unresponsive during P-03.

---

## Acceptance Criteria Verification

These map directly to the spec's acceptance criteria. All must pass before shipping.

### Migration "Complete" Criteria

| ID | Criterion | Test | Pass Condition |
|---|---|---|---|
| AC-01 | User connected at least one previous tool | Complete Step 1 with T-01 | Step 4 reached; badge awarded |
| AC-02 | At least one data category processed and stored in `user_context_profile` | Inspect profile API after migration | Profile has `top_topics` or `conversation_count` populated |
| AC-03 | Step 3 displays at least one personalized insight card (not generic) | T-01 migration | Insight card contains specific count from T-01 data |
| AC-04 | Step 4 displays at least one personalized task (with specific numbers) | T-01 migration | Task card references specific number from import (e.g., "50 conversations") |
| AC-05 | AI partner's first response reflects imported context | Initiate chat from Step 4 task | AI response references import data (writing style, top topics, or counts) |
| AC-06 | Uploaded files deleted from temporary storage | Upload T-01, complete migration | Server temp directory: no T-01 ZIP or extracted contents after processing |
| AC-07 | Migration Complete badge appears in dashboard | Complete all 4 steps | Badge visible in portal dashboard |

### Flow "Production Ready" Criteria

| ID | Criterion | Test | Pass Condition |
|---|---|---|---|
| AC-08 | Full ChatGPT export flow works end-to-end with real ZIP | Use actual ChatGPT account export | All 4 steps complete; personalized output shown |
| AC-09 | All uploaded files confirmed deleted after processing | Server-side verification | Zero files in temp directory after migration complete |
| AC-10 | OAuth tokens stored in vault (not database) | Code review / architecture check | Coordinate with security-engineer-tech |
| AC-11 | User can remove any data category and see it removed | F7-01 through F7-04 | Data removed from display and not used in Step 3 |
| AC-12 | Privacy note visible on Step 2 above the CTA | A-01, F7-05 | Note visible without scrolling |
| AC-13 | "How to export" instructions correct and current | Manual review of modal content | Instructions match current ChatGPT/Claude UI |
| AC-14 | Mobile layout tested at 375px, 390px, 768px | R-01 through R-12 | All responsive tests pass |

---

## Test Execution Order

Execute tests in this sequence to surface critical blockers first:

**Phase 1: Smoke Tests** (30 minutes — run first, block if any fail)
1. F1-01 — Valid ChatGPT ZIP upload
2. F2-01 — Valid JSON parsing
3. F3-01 — Topic extraction works
4. F4-01 through F4-04 — Full navigation forward
5. F6-06 — "Start this task" link works

**Phase 2: Core Functional** (3-4 hours)
- Complete F1, F2, F3, F4, F5, F6, F7, F9 modules

**Phase 3: Brevo Integration** (1 hour, requires Brevo dashboard access)
- Complete F8 module

**Phase 4: Security** (2 hours, requires server access + security-engineer-tech)
- S-01 through S-18

**Phase 5: Edge Cases** (2 hours)
- EC-01 through EC-15

**Phase 6: Responsive** (1-2 hours, requires real mobile device for R-07)
- R-01 through R-12

**Phase 7: Accessibility** (2 hours, requires screen reader)
- A-01 through A-18

**Phase 8: Performance** (1 hour)
- P-01 through P-11

**Phase 9: Acceptance Criteria Final Check** (30 minutes)
- AC-01 through AC-14

**Total estimated QA time**: 14-16 hours

---

## Known Risks and Pre-Ship Flags

These are items that must be explicitly verified before shipping, not assumed:

1. **Temp file deletion on error path** — The cleanup job must run even when processing fails. This is a common oversight. Verify with a forced-fail test (T-07) and server inspection.

2. **iOS Safari file picker** — The default behavior on iOS presents camera roll, not Files app. This will confuse most users. The UI must have explicit guidance. Test on a real device.

3. **ZIP bomb** — Even a small ZIP bomb can crash a Node.js process or fill a server disk. Do not skip S-01. This must be tested.

4. **Personalization failure mode** — If the topic extractor returns generic results (e.g., all topics are "conversation" or "chat"), Step 4 tasks will be generic and the product promise breaks. Run AC-03 and AC-04 before shipping.

5. **Brevo API key exposure** — Client-side Brevo calls are a pattern used elsewhere in this codebase. Verify S-09 explicitly. The key must never appear in browser-accessible code.

6. **Tenant isolation** — If multiple users are migrating simultaneously, their data must not cross-contaminate. S-10 must be tested with two accounts.

---

## Bug Severity Definitions

| Severity | Definition | Examples |
|---|---|---|
| **P0 — Critical** | Blocks core flow; data loss; security vulnerability | Upload crashes app; XSS executes; temp files not deleted |
| **P1 — High** | Feature broken but workaround exists; incorrect data displayed | Wrong conversation count; Remove button doesn't work; back navigation broken |
| **P2 — Medium** | Degraded experience; non-critical feature broken | Animation stutter; timeout email not sent; deep link redirect missing |
| **P3 — Low** | Cosmetic; minor UX friction | Text truncation style; wrong icon; spelling error |

**Ship criteria**: Zero P0s. Zero P1s. P2s triaged and accepted with product sign-off.

---

## Sign-Off Checklist

Before marking this feature as QA-approved:

- [ ] All P0 tests executed and passing
- [ ] All P1 tests executed and passing
- [ ] S-01 (ZIP bomb) verified by security-engineer-tech
- [ ] S-06 (temp file deletion) verified by server inspection
- [ ] S-09 (Brevo API key not client-side) verified
- [ ] AC-08 (real ChatGPT export file tested)
- [ ] R-07 (iOS Safari) tested on real device
- [ ] A-09, A-10 (color contrast) verified
- [ ] QA engineer sign-off
- [ ] Security engineer sign-off

---

*Test plan authored by qa-engineer | 2026-02-23*
*Spec version: 1.0 | Feature spec location: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/ai-migration-portal-spec.md`*
