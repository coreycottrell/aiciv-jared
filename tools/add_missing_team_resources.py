#!/usr/bin/env python3
"""
Add missing resources to the Team Resource Spreadsheet.
Spreadsheet ID: 1VK0ICSJ5rdwYNy1cywRq0Y3mz_K5L6sOdhHYQ7Lcomw

Only ADDS new rows. Does NOT modify existing content.
"""

import os
import sys
from pathlib import Path

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
sys.path.insert(0, str(CIV_ROOT / "tools"))

try:
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SPREADSHEET_ID = "1VK0ICSJ5rdwYNy1cywRq0Y3mz_K5L6sOdhHYQ7Lcomw"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_creds():
    token_path = CIV_ROOT / ".credentials" / "oauth-token.json"
    import json
    with open(token_path) as f:
        data = json.load(f)
    creds = OAuthCredentials.from_authorized_user_info(data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        }
        with open(token_path, "w") as f:
            json.dump(token_data, f, indent=2)
    return creds


# New rows to append (matching existing column order):
# Asset Name, Type, Funnel Stage, ICP Fit, Format, Link/Location, Status, Channel, Notes
NEW_ROWS = [
    # --- Website Pages Missing ---
    [
        "Blog Index (The Neural Feed)",
        "Landing Page",
        "TOFU",
        "All",
        "Web",
        "https://purebrain.ai/blog/",
        "Live",
        "SEO / Organic",
        "Central blog hub. 40+ published articles on AI agents, memory, partnerships.",
    ],
    [
        "Blog Neural Feed Memories Archive",
        "Landing Page",
        "TOFU",
        "All",
        "Web",
        "https://purebrain.ai/blog-neural-feed-memories/",
        "Live",
        "SEO / Organic",
        "Historical archive of all Neural Feed posts.",
    ],
    [
        "Investment Opportunity Page",
        "Landing Page",
        "BOFU",
        "Enterprise",
        "Web",
        "https://purebrain.ai/investment-opportunity/",
        "Live",
        "Investor / Direct",
        "Investor-facing page with Chy avatar. Claude API powered.",
    ],
    [
        "Rootcode Page",
        "Landing Page",
        "MOFU",
        "SME",
        "Web",
        "https://purebrain.ai/rootcode/",
        "Live",
        "Direct / Website",
        "Rootcode positioning page.",
    ],
    [
        "Payment Page - Live Tier",
        "Payment Page",
        "BOFU",
        "SMB",
        "Web",
        "https://purebrain.ai/live/",
        "Live",
        "Sales / Direct",
        "Primary payment page for Live tier.",
    ],
    [
        "Payment Page - Awakened Tier",
        "Payment Page",
        "BOFU",
        "SME",
        "Web",
        "https://purebrain.ai/awakened/",
        "Live",
        "Sales / Direct",
        "Payment page for Awakened tier.",
    ],
    [
        "Payment Page - Partnered Tier",
        "Payment Page",
        "BOFU",
        "SME",
        "Web",
        "https://purebrain.ai/partnered/",
        "Live",
        "Sales / Direct",
        "Payment page for Partnered tier.",
    ],
    [
        "Payment Page - Unified Tier",
        "Payment Page",
        "BOFU",
        "Enterprise",
        "Web",
        "https://purebrain.ai/unified/",
        "Live",
        "Sales / Direct",
        "Payment page for Unified (enterprise) tier.",
    ],
    [
        "PureSurf Browser Extension Hub",
        "Product Page",
        "MOFU",
        "All",
        "Web",
        "https://surf.purebrain.ai",
        "Live",
        "Product / Direct",
        "PureSurf v5.5. Cookie sync extension + mobile sync at /sync.",
    ],
    [
        "Voice TTS Platform",
        "Product Page",
        "MOFU",
        "All",
        "Web",
        "https://voice.purebrain.ai",
        "Live",
        "Product / Direct",
        "Chatterbox TTS. Per-customer voice_id. Voice pricing product planned.",
    ],
    [
        "Social Dashboard",
        "Dashboard",
        "Internal",
        "All",
        "Web",
        "https://surf.purebrain.ai/social.html",
        "Live",
        "Internal / Ops",
        "Social media monitoring and engagement dashboard.",
    ],
    [
        "AI Quiz",
        "Lead Magnet",
        "TOFU",
        "All",
        "Web",
        "https://purebrain.ai/ai-quiz/",
        "Live",
        "Direct / Website",
        "Interactive AI readiness quiz for lead capture.",
    ],
    [
        "Thank You Page",
        "Landing Page",
        "BOFU",
        "All",
        "Web",
        "https://purebrain.ai/thank-you/",
        "Live",
        "Conversion",
        "Post-conversion thank you page.",
    ],
    [
        "Voice Pricing Page",
        "Product Page",
        "MOFU",
        "All",
        "Web",
        "https://purebrain.ai/voice-pricing/",
        "Live",
        "Product / Direct",
        "Pricing page for voice services.",
    ],
    # --- Google Drive Resources Missing ---
    [
        "Upcoming Content Folder (Google Drive)",
        "Folder",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz",
        "Active",
        "Content Pipeline",
        "Staging folder for upcoming LinkedIn/blog content.",
    ],
    [
        "Posted Content Archive (Google Drive)",
        "Folder",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx",
        "Active",
        "Content Pipeline",
        "Archive of all published content assets.",
    ],
    [
        "3D Design Skill Package",
        "Training Doc",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/file/d/1WbS2p58DbaBh66FRq1OZDG7jsJ56iuVQ/view",
        "Active",
        "Design / Brand",
        "Design system and visual standards. Oswald Bold font. 93% mastery (30+ nights Gleb training).",
    ],
    [
        "Voice/TTS Training Folder",
        "Training Doc",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ",
        "Active",
        "Product / Voice",
        "Chatterbox TTS training materials and configuration.",
    ],
    [
        "Skills & Training Master Folder",
        "Training Doc",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1ACyxaXI9DwJHg6PZt3pV5ccne9lUL0hJ",
        "Active",
        "Onboarding / Training",
        "Master folder of all agent and team skills training.",
    ],
    [
        "LinkedIn Operations Folder",
        "SOP",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/12QBh5yVTppCo04jh5wrmhvZlqUxPIp71",
        "Active",
        "LinkedIn",
        "6 core skills: content-creation-sop, linkedin-daily-ops, commenting-strategy, social-design, drive-org, post-tracking.",
    ],
    [
        "Never Forget Folder (Constitutional)",
        "Reference",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1J2GLiYBlucBGQTofXsrVQ42t1EwVIeqK",
        "Active",
        "Ops / Constitutional",
        "10 foundational docs (identity, behavioral rules, onboarding, team roster, business ref). 1,833 lines.",
    ],
    [
        "C-Level Training Folder",
        "Training Doc",
        "Internal",
        "All",
        "Google Drive",
        "https://drive.google.com/drive/folders/1baZ8CNryYL3gfW5daM4nGdARB_OCaDJW",
        "Active",
        "Onboarding / Training",
        "Executive-level agent training materials for department leads.",
    ],
    # --- SOPs and Playbooks Missing ---
    [
        "Content Creation SOP",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "Content Pipeline",
        "Covers ideation, writing, image generation, quality gates. Skill: content-creation-sop.",
    ],
    [
        "Social Operations Guide",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "Social / LinkedIn",
        "Filing, distribution, scheduling, tracking, engagement post-creation. Skill: social-operations-guide.",
    ],
    [
        "LinkedIn Daily Operations SOP",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "LinkedIn",
        "Daily cadence: posting, commenting (90s spacing), reactions (rotate Support/Celebrate/Insightful/Love).",
    ],
    [
        "LinkedIn Commenting Strategy",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "LinkedIn",
        "Traveling Comment Framework. Direct profile targeting (/in/{handle}/recent-activity/all/). 185K appearances in 7 days.",
    ],
    [
        "PureBrain Social Design Standards",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "Design / Brand",
        "Visual standards for all social assets. Brand orange #FA6600. Newsletter banner = LinkedIn image (1200x630).",
    ],
    [
        "LinkedIn Post Tracking System",
        "SOP",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "LinkedIn",
        "Weekly engine: Sunday batch -> Monday approval -> daily autopilot. Spreadsheet: Draft->Final->Live.",
    ],
    [
        "LinkedIn Content Pipeline (End-to-End)",
        "Framework",
        "Internal",
        "All",
        "Skill/Doc",
        "",
        "Active",
        "LinkedIn / Content",
        "Research -> Blog -> LinkedIn Post -> Bluesky Thread -> Image. ~25 min/target. 50 occupations + 50 industries mapped.",
    ],
    # --- Email/Automation Assets ---
    [
        "Brevo Email Automation Hub",
        "Platform",
        "Internal",
        "All",
        "Web",
        "https://app.brevo.com/automation/list",
        "Live",
        "Email",
        "Already listed in 30+ Email Templates row, but this is the direct automation dashboard link.",
    ],
    # --- Blog Posts (Top Performers / Key Content) ---
    [
        "Blog: The Context Tax",
        "Blog Post",
        "TOFU",
        "All",
        "Web",
        "https://purebrain.ai/blog/the-context-tax/",
        "Live",
        "Content / SEO",
        "Key thought leadership piece. Also has LinkedIn post template.",
    ],
    [
        "Blog: Prompting Is Dead",
        "Blog Post",
        "TOFU",
        "All",
        "Web",
        "https://purebrain.ai/blog/prompting-is-dead/",
        "Live",
        "Content / SEO",
        "Contrarian angle on prompting vs. partnership with AI.",
    ],
    [
        "Blog: Why AI Memory Changes Everything",
        "Blog Post",
        "MOFU",
        "All",
        "Web",
        "https://purebrain.ai/blog/why-ai-memory-changes-everything/",
        "Live",
        "Content / SEO",
        "Core product differentiator content. Memory = PureBrain advantage.",
    ],
    [
        "Blog: Your Next Direct Report Won't Be Human",
        "Blog Post",
        "TOFU",
        "SME",
        "Web",
        "https://purebrain.ai/blog/your-next-direct-report-wont-be-human/",
        "Live",
        "Content / SEO",
        "Enterprise-angle thought leadership.",
    ],
    [
        "Blog: Pilot Purgatory - Why 95% of AI Projects Die",
        "Blog Post",
        "MOFU",
        "SME",
        "Web",
        "https://purebrain.ai/blog/pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value/",
        "Live",
        "Content / SEO",
        "Pain point content. Directly supports sales conversations.",
    ],
    [
        "Blog: The $5.2B AI Agents Market Is Not the Story",
        "Blog Post",
        "TOFU",
        "Enterprise",
        "Web",
        "https://purebrain.ai/blog/52-billion-ai-agents-market-is-not-the-story/",
        "Live",
        "Content / SEO",
        "Market trend thought leadership with contrarian take.",
    ],
]


def main():
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # Append new rows
    body = {"values": NEW_ROWS}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Content & Media Assets!A:I",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

    updated = result.get("updates", {}).get("updatedRows", 0)
    print(f"Added {updated} new rows to the Team Resource Spreadsheet.")
    print(f"Rows added: {len(NEW_ROWS)}")
    for row in NEW_ROWS:
        print(f"  + {row[0]}")


if __name__ == "__main__":
    main()
