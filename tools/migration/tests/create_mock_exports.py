"""
Create mock export files for testing.

Run this to generate fixture ZIPs that the parsers can test against:

    python tools/migration/tests/create_mock_exports.py

Generates:
    tests/fixtures/mock_chatgpt_export.zip
    tests/fixtures/mock_claude_export.zip
    tests/fixtures/mock_prompts.csv
    tests/fixtures/mock_conversations.json
"""

import json
import zipfile
import csv
from pathlib import Path
from datetime import datetime, timedelta

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


def make_timestamp(days_ago: int, seconds_offset: int = 0) -> float:
    """Return Unix timestamp for a moment N days ago."""
    dt = datetime.utcnow() - timedelta(days=days_ago) + timedelta(seconds=seconds_offset)
    return dt.timestamp()


def make_iso(days_ago: int) -> str:
    dt = datetime.utcnow() - timedelta(days=days_ago)
    return dt.isoformat() + "Z"


# ---------------------------------------------------------------------------
# Mock ChatGPT Export
# ---------------------------------------------------------------------------

def create_mock_chatgpt_export():
    """Create a realistic mock conversations.zip in OpenAI format."""

    conversations = [
        # Conversation 1: Market analysis (appears many times)
        {
            "id": "conv_001",
            "title": "Q3 Market Analysis Report",
            "create_time": make_timestamp(365),
            "update_time": make_timestamp(364),
            "mapping": {
                "node_1": {
                    "id": "node_1",
                    "message": {
                        "id": "msg_1",
                        "author": {"role": "user"},
                        "content": {
                            "content_type": "text",
                            "parts": ["Can you help me with a market analysis for the SaaS industry? "
                                      "I need to understand competitive landscape, pricing strategies, "
                                      "and market segments. Be direct and use bullet points please."]
                        },
                        "create_time": make_timestamp(365, 100),
                    },
                    "parent": None,
                    "children": ["node_2"]
                },
                "node_2": {
                    "id": "node_2",
                    "message": {
                        "id": "msg_2",
                        "author": {"role": "assistant"},
                        "content": {
                            "content_type": "text",
                            "parts": ["Here's a market analysis for the SaaS industry:\n\n**Market segments:**\n- SMB\n- Enterprise\n- Vertical SaaS"]
                        },
                        "create_time": make_timestamp(365, 200),
                    },
                    "parent": "node_1",
                    "children": []
                }
            },
            "moderation_results": [],
            "current_node": "node_2",
        },
        # Conversation 2: Copywriting
        {
            "id": "conv_002",
            "title": "Email copywriting for product launch",
            "create_time": make_timestamp(300),
            "update_time": make_timestamp(299),
            "mapping": {
                "node_1": {
                    "id": "node_1",
                    "message": {
                        "id": "msg_3",
                        "author": {"role": "user"},
                        "content": {
                            "content_type": "text",
                            "parts": ["Write a short product launch email for our new analytics dashboard. "
                                      "Target audience is B2B marketing managers. "
                                      "Keep it concise, no fluff, direct CTA at the end. "
                                      "Our brand voice is professional but not stuffy."]
                        },
                        "create_time": make_timestamp(300, 100),
                    },
                    "parent": None,
                    "children": []
                }
            },
            "moderation_results": [],
            "current_node": "node_1",
        },
        # Conversation 3: Hiring decision
        {
            "id": "conv_003",
            "title": "Hiring: Head of Product evaluation",
            "create_time": make_timestamp(200),
            "update_time": make_timestamp(199),
            "mapping": {
                "node_1": {
                    "id": "node_1",
                    "message": {
                        "id": "msg_5",
                        "author": {"role": "user"},
                        "content": {
                            "content_type": "text",
                            "parts": ["I'm evaluating candidates for Head of Product. "
                                      "I have two finalists: one from a large enterprise background, "
                                      "one from early-stage startup. We're a Series A company. "
                                      "What framework should I use to make this hiring decision? "
                                      "Give me a structured decision matrix."]
                        },
                        "create_time": make_timestamp(200, 100),
                    },
                    "parent": None,
                    "children": []
                }
            },
            "moderation_results": [],
            "current_node": "node_1",
        },
        # Conversations 4-10: More market analysis (to boost frequency)
        *[
            {
                "id": f"conv_{i:03d}",
                "title": f"Market research: {topic}",
                "create_time": make_timestamp(300 - i * 20),
                "update_time": make_timestamp(299 - i * 20),
                "mapping": {
                    "node_1": {
                        "id": "node_1",
                        "message": {
                            "id": f"msg_{i}",
                            "author": {"role": "user"},
                            "content": {
                                "content_type": "text",
                                "parts": [text]
                            },
                            "create_time": make_timestamp(300 - i * 20, 100),
                        },
                        "parent": None,
                        "children": []
                    }
                },
                "moderation_results": [],
                "current_node": "node_1",
            }
            for i, (topic, text) in enumerate([
                ("competitive analysis", "Run a competitive analysis for our product vs Salesforce and HubSpot. Focus on pricing and market positioning."),
                ("pricing strategy", "Help me develop a pricing strategy for our new SaaS product. I need tiered pricing with clear value differentiation."),
                ("product positioning", "Write a product positioning statement for our analytics platform targeting enterprise customers."),
                ("customer segmentation", "Help me segment our customer base by company size and use case for a market analysis report."),
                ("go-to-market strategy", "What's the best go-to-market strategy for a B2B SaaS tool in the HR tech space?"),
                ("revenue modeling", "Build a simple revenue model for a SaaS business with monthly and annual billing options."),
            ], start=10)
        ]
    ]

    user_data = {
        "id": "user_mock_001",
        "email": "test@example.com",
        "custom_instructions": {
            "about_user_message": "I'm a B2B SaaS founder focused on growth-stage companies. "
                                  "I have an MBA and 10 years in enterprise software.",
            "about_model_message": "Be direct and concise. No preamble. "
                                   "Use bullet points for lists. "
                                   "Assume I know business fundamentals — skip basics. "
                                   "When giving recommendations, be opinionated."
        }
    }

    # Write ZIP
    output_path = FIXTURES_DIR / "mock_chatgpt_export.zip"
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("conversations.json", json.dumps(conversations, indent=2))
        zf.writestr("user.json", json.dumps(user_data, indent=2))
        zf.writestr("message_feedback.json", "[]")

    print(f"Created: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path


# ---------------------------------------------------------------------------
# Mock Claude Export
# ---------------------------------------------------------------------------

def create_mock_claude_export():
    """Create a mock Claude export ZIP in Anthropic format."""

    conversations = [
        {
            "uuid": "claude_conv_001",
            "name": "Quarterly business review prep",
            "created_at": make_iso(180),
            "updated_at": make_iso(179),
            "chat_messages": [
                {
                    "uuid": "msg_001",
                    "text": "I need to prepare a quarterly business review presentation for our board. "
                            "We're a 50-person B2B software company with $3M ARR. "
                            "What slides should I include and what metrics matter most?",
                    "sender": "human",
                    "created_at": make_iso(180),
                },
                {
                    "uuid": "msg_002",
                    "text": "Here's a recommended structure for your QBR...",
                    "sender": "assistant",
                    "created_at": make_iso(180),
                }
            ]
        },
        {
            "uuid": "claude_conv_002",
            "name": "Content strategy brainstorm",
            "created_at": make_iso(120),
            "updated_at": make_iso(119),
            "chat_messages": [
                {
                    "uuid": "msg_003",
                    "text": "Help me brainstorm content topics for our company blog. "
                            "Our audience is HR leaders at mid-market companies. "
                            "I want thought leadership content, not product marketing.",
                    "sender": "human",
                    "created_at": make_iso(120),
                },
                {
                    "uuid": "msg_004",
                    "text": "Great topic area to focus on...",
                    "sender": "assistant",
                    "created_at": make_iso(120),
                },
                {
                    "uuid": "msg_005",
                    "text": "Can you also give me a content calendar template? "
                            "Weekly cadence, mix of short and long form. "
                            "Give me the template in a table format please.",
                    "sender": "human",
                    "created_at": make_iso(119),
                }
            ]
        },
        {
            "uuid": "claude_conv_003",
            "name": "Sales email sequence draft",
            "created_at": make_iso(90),
            "updated_at": make_iso(89),
            "chat_messages": [
                {
                    "uuid": "msg_006",
                    "text": "Write a 5-email cold outreach sequence for enterprise prospects. "
                            "We sell workflow automation software to operations teams. "
                            "Each email should be short — under 100 words. Direct subject lines. "
                            "No corporate jargon.",
                    "sender": "human",
                    "created_at": make_iso(90),
                }
            ]
        },
    ]

    output_path = FIXTURES_DIR / "mock_claude_export.zip"
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("conversations.json", json.dumps(conversations, indent=2))

    print(f"Created: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path


# ---------------------------------------------------------------------------
# Mock CSV Prompt Library
# ---------------------------------------------------------------------------

def create_mock_prompts_csv():
    """Create a mock prompt library CSV."""
    output_path = FIXTURES_DIR / "mock_prompts.csv"

    rows = [
        {"title": "Competitive Analysis", "category": "research",
         "prompt": "Analyze the competitive landscape for [PRODUCT] vs [COMPETITOR]. "
                   "Include pricing, positioning, feature gaps, and market share estimates."},
        {"title": "Email Subject Lines", "category": "copywriting",
         "prompt": "Generate 10 email subject lines for [CAMPAIGN]. "
                   "Target audience: [AUDIENCE]. Goal: [GOAL]. Be direct, no clickbait."},
        {"title": "Meeting Agenda", "category": "productivity",
         "prompt": "Create a 30-minute meeting agenda for [MEETING_TYPE]. "
                   "Attendees: [ROLES]. Expected outcome: [OUTCOME]."},
        {"title": "OKR Review", "category": "business",
         "prompt": "Review these OKRs for Q[QUARTER]: [OKRS]. "
                   "Identify which are on track, at risk, and off track. Give a traffic light summary."},
        {"title": "Job Description", "category": "hiring",
         "prompt": "Write a job description for [ROLE] at a Series B B2B SaaS company. "
                   "Team: [TEAM]. Must-haves: [REQUIREMENTS]. Avoid generic corporate language."},
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "category", "prompt"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path


# ---------------------------------------------------------------------------
# Mock Conversation JSON
# ---------------------------------------------------------------------------

def create_mock_conversation_json():
    """Create a mock message-array JSON (generic format)."""
    output_path = FIXTURES_DIR / "mock_conversations.json"

    messages = [
        {"role": "user", "content": "What are the best practices for B2B pricing strategy?",
         "timestamp": make_iso(50)},
        {"role": "assistant", "content": "Value-based pricing is typically most effective...",
         "timestamp": make_iso(50)},
        {"role": "user", "content": "We're considering a freemium model. What are the conversion benchmarks?",
         "timestamp": make_iso(45)},
        {"role": "assistant", "content": "Industry benchmarks for freemium...",
         "timestamp": make_iso(45)},
        {"role": "user", "content": "Draft an announcement for our enterprise tier launch. "
                                     "Target: existing customers. Tone: excited but professional.",
         "timestamp": make_iso(30)},
    ]

    with open(output_path, "w") as f:
        json.dump(messages, f, indent=2)

    print(f"Created: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Creating mock export fixtures...\n")
    create_mock_chatgpt_export()
    create_mock_claude_export()
    create_mock_prompts_csv()
    create_mock_conversation_json()
    print(f"\nAll fixtures created in: {FIXTURES_DIR}")
