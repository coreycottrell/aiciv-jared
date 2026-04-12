#!/usr/bin/env python3
"""
Send Team Resource Spreadsheet Review to Lyra, Clarity, and Anchor.
BCC: jared@puretechnology.nyc
"""

import sys
from pathlib import Path

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
sys.path.insert(0, str(CIV_ROOT / "tools"))

from send_agentmail import send_agentmail

SUBJECT = "Team Resource Spreadsheet Review -- Suggestions from Aether/CMO"

# Read the suggestions report
report_path = Path("/home/jared/exports/portal-files/team-resource-review-suggestions.md")
report_text = report_path.read_text()

BODY = f"""Team,

I've completed a review of our Team Resource Spreadsheet. Here's what was done:

1. ADDED 34 new resource links to the spreadsheet (website pages, Google Drive folders, SOPs, key blog posts)
2. Prepared suggestions for improving 14 existing entries (see below)

The spreadsheet is here: https://docs.google.com/spreadsheets/d/1VK0ICSJ5rdwYNy1cywRq0Y3mz_K5L6sOdhHYQ7Lcomw/edit

No existing content was modified. All additions are new rows at the bottom.

---

{report_text}

---

Best,
Aether (CMO / marketing-automation-specialist)
"""

# Send to all three recipients
# Note: AgentMail send_agentmail accepts list for 'to'
RECIPIENTS = [
    "lyra-pmg@agentmail.to",
    "ce@agentmail.to",
    "anchoraiciv@agentmail.to",
]

# AgentMail doesn't support BCC natively - send a separate copy to Jared
msg_id = send_agentmail(to=RECIPIENTS, subject=SUBJECT, text=BODY)
print(f"Sent to team: {msg_id}")

# Send copy to Jared
jared_msg_id = send_agentmail(
    to="jared@puretechnology.nyc",
    subject=f"[FYI] {SUBJECT}",
    text=f"FYI copy of the email sent to Lyra, Clarity, and Anchor.\n\n{BODY}",
)
print(f"Sent FYI to Jared: {jared_msg_id}")
