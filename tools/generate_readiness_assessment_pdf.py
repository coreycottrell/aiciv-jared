#!/usr/bin/env python3
"""
AI Partnership Readiness Assessment - PDF Lead Magnet Generator

Creates a professional 1-page PDF lead magnet for PureBrain.ai
with 5 self-assessment questions that help professionals evaluate
their readiness for an AI partnership.

Usage:
    python3 tools/generate_readiness_assessment_pdf.py

Output:
    exports/lead-magnets/ai-partnership-readiness-assessment.pdf
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Brand Colors
PT_BLUE = HexColor("#2a93c1")
PT_ORANGE = HexColor("#f1420b")
DARK_BG = HexColor("#1a1a2e")
LIGHT_GRAY = HexColor("#f5f5f5")
MEDIUM_GRAY = HexColor("#666666")
DARK_TEXT = HexColor("#222222")


def create_readiness_assessment_pdf(output_path: str):
    """Generate the AI Partnership Readiness Assessment PDF."""

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create canvas for custom drawing
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # --- HEADER SECTION ---
    # Blue header bar
    c.setFillColor(PT_BLUE)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)

    # Header text
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 55, "AI Partnership Readiness Assessment")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 80, "5 Questions to Evaluate Your AI Strategy")

    # Subheader
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(width/2, height - 120, "Discover if you're ready to move from AI tools to an AI partnership that actually learns your business.")

    # --- QUESTIONS SECTION ---
    questions = [
        {
            "number": "1",
            "question": "When you close a chat with ChatGPT or Claude, what happens to your conversation history?",
            "options": [
                ("A", "It's gone forever - I start fresh every time"),
                ("B", "I can scroll back, but it doesn't really help my next task"),
                ("C", "I try to copy/paste context, but it's tedious"),
                ("D", "I wish it remembered my preferences, projects, and past decisions")
            ]
        },
        {
            "number": "2",
            "question": "How do you currently use AI in your daily workflow?",
            "options": [
                ("A", "I don't - I'm curious but haven't started"),
                ("B", "Occasionally for one-off tasks (writing emails, quick research)"),
                ("C", "Regularly, but I repeat myself constantly explaining my context"),
                ("D", "I've tried to build systems but hit walls with memory and continuity")
            ]
        },
        {
            "number": "3",
            "question": "What's your biggest frustration with current AI tools?",
            "options": [
                ("A", "I don't know where to start"),
                ("B", "The outputs feel generic - they don't understand MY business"),
                ("C", "I spend more time prompting than doing actual work"),
                ("D", "Every session feels like training a new employee from scratch")
            ]
        },
        {
            "number": "4",
            "question": "If you could describe your ideal AI relationship, it would be:",
            "options": [
                ("A", "A smart search engine that answers questions"),
                ("B", "A writing assistant that drafts content"),
                ("C", "A team member who knows my work history and preferences"),
                ("D", "A partner who anticipates needs and grows with my business")
            ]
        },
        {
            "number": "5",
            "question": "What would you pay for an AI that genuinely learned your business over time?",
            "options": [
                ("A", "Nothing - free tools are good enough for me"),
                ("B", "A small monthly fee if it saved me a few hours"),
                ("C", "Whatever my most valuable team member costs per hour"),
                ("D", "The question isn't cost - it's whether it actually works")
            ]
        }
    ]

    y_position = height - 155

    for q in questions:
        # Question number circle
        c.setFillColor(PT_ORANGE)
        c.circle(50, y_position - 5, 12, fill=True, stroke=False)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(50, y_position - 10, q["number"])

        # Question text
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica-Bold", 11)

        # Handle long questions with wrapping
        question_text = q["question"]
        c.drawString(70, y_position, question_text)

        y_position -= 20

        # Options in 2x2 grid
        c.setFont("Helvetica", 9)
        c.setFillColor(MEDIUM_GRAY)

        options = q["options"]
        col1_x = 80
        col2_x = 320

        for i, (opt_letter, text) in enumerate(options):
            x = col1_x if i % 2 == 0 else col2_x
            if i == 2:
                y_position -= 14

            # Option circle
            c.setFillColor(LIGHT_GRAY)
            c.circle(x - 8, y_position - 3, 6, fill=True, stroke=False)
            c.setFillColor(DARK_TEXT)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(x - 8, y_position - 6, opt_letter)

            # Option text
            c.setFont("Helvetica", 9)
            c.setFillColor(MEDIUM_GRAY)
            # Truncate if too long
            display_text = text if len(text) <= 38 else text[:35] + "..."
            c.drawString(x, y_position - 5, display_text)

        y_position -= 35

    # --- SCORING SECTION ---
    y_position -= 5

    # Light background box for scoring
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(40, y_position - 70, width - 80, 75, 8, fill=True, stroke=False)

    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(55, y_position - 15, "Your Results:")

    c.setFont("Helvetica", 10)
    scoring_text = [
        "Mostly A's & B's: You're at the starting line. Perfect time to build your AI foundation right.",
        "Mostly B's & C's: You've felt the friction. You know AI can do more - you just haven't found how.",
        "Mostly C's & D's: You're ready. You've outgrown generic tools and need a real AI partnership."
    ]

    y_score = y_position - 32
    for line in scoring_text:
        c.drawString(55, y_score, line)
        y_score -= 14

    # --- CTA SECTION ---
    y_position -= 95

    # Orange CTA bar
    c.setFillColor(PT_ORANGE)
    c.roundRect(40, y_position - 55, width - 80, 55, 8, fill=True, stroke=False)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y_position - 20, "Ready to see what this looks like?")

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, y_position - 42, "Fill the 60-second Fit Check")

    # Website
    c.setFont("Helvetica", 11)
    c.drawCentredString(width/2, y_position - 68, "purebrain.ai")

    # --- FOOTER ---
    c.setFillColor(PT_BLUE)
    c.rect(0, 0, width, 30, fill=True, stroke=False)

    c.setFillColor(white)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 10, "PureBrain.ai | AI That Learns Your Business | Pure Technology Inc.")

    # Save PDF
    c.save()

    return output_path


def send_to_telegram(file_path: str, chat_id: str = "437939400"):
    """Send the PDF to Telegram."""
    import json
    import requests

    config_path = project_root / "config" / "telegram_config.json"

    with open(config_path) as f:
        config = json.load(f)

    bot_token = config["bot_token"]

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': chat_id,
            'caption': "AI Partnership Readiness Assessment - Lead Magnet for PureBrain.ai\n\n5-question self-assessment to help professionals evaluate their AI partnership readiness. Ready for your review!"
        }

        response = requests.post(url, files=files, data=data, timeout=60)

        if response.status_code == 200:
            print(f"Successfully sent PDF to Telegram chat {chat_id}")
            return True
        else:
            print(f"Failed to send to Telegram: {response.status_code} - {response.text}")
            return False


def main():
    """Generate PDF and send to Telegram."""

    output_path = str(project_root / "exports" / "lead-magnets" / "ai-partnership-readiness-assessment.pdf")

    print("Generating AI Partnership Readiness Assessment PDF...")
    pdf_path = create_readiness_assessment_pdf(output_path)
    print(f"PDF created: {pdf_path}")

    print("\nSending to Telegram (chat_id: 437939400)...")
    send_to_telegram(pdf_path)

    print("\nDone!")


if __name__ == "__main__":
    main()
