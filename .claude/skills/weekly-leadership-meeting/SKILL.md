---
name: weekly-leadership-meeting
description: Auto-generate Monday leadership meeting prep from live data sources (777, admin API, North Star, Chy inputs). File to Google Drive + deliver to portal.
version: 1.0.0
author: aether
trigger: "Monday 9am ET BOOP OR manual invocation"
schedule: weekly-monday at 09:00 ET
---

# Weekly Leadership Meeting Prep Skill

## Purpose
Every Monday at 9am ET, auto-generate a comprehensive leadership meeting prep document using live data from 777.purebrain.ai, admin API, North Star goals, Chy's inputs, and previous week's action items.

## Meeting Details
- **When**: Mondays 11am EST
- **Duration**: 60 minutes max
- **Who**: Jared (CEO), Aether (AI Co-CEO), Chy (CFO/CRO/COO), department leads
- **Prepared by**: Aether (auto-generated 2 hours before meeting)

## Template
Filed at: Google Drive > Leadership Meetings folder (ID: 19a_omY3gDISKydcRQj6mp-qrjG67rImR)
Template file: `leadership-meeting-template-v2.md`

## Data Sources

### Automated (Aether pulls directly):
1. **777.purebrain.ai** — North Star RAG status, monthly targets, pillar goals
2. **Admin API** (`/api/admin/clients`) — live MRR, subscriber count, tier breakdown, churn
3. **Google Sheets TOS** (ID: 1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs) — Morning Pulse, Handshake Queue, Activity Feed
4. **Previous week's meeting notes** — action items, decisions, follow-ups
5. **Overnight intel scan** — AI industry news, competitor moves
6. **Session logs** — what was built/shipped this week

### Chy's Inputs (submitted by Sunday 8pm):
Chy submits her C-suite update covering three roles:

**As CFO:**
- Cash position update
- Budget approvals needed
- P/L highlights (1st meeting of month: full review)
- Burn rate status

**As CRO:**
- Revenue pipeline status
- Sales forecast this week
- Key deals in progress
- Conversion metrics

**As COO:**
- Operational blockers
- Process improvements
- Team capacity/hiring status
- Vendor/partner updates

**Submission method**: Chy messages via handshake queue (`/home/aiciv/shared/handshake-queue.md`) or emails to purebrain@puremarketing.ai by Sunday 8pm.

### Department Lead Inputs (submitted to Lumen by Sunday 8pm):
Each lead emails purebrain@puremarketing.ai with 3 bullets:
1. What we shipped this week
2. What's blocked
3. What's next

Lumen (purebrain@puremarketing.ai) compiles all submissions.

## Execution Steps

### Step 0: Ping Chy for Input (Sunday evening — BEFORE doc creation)
**This happens FIRST. The doc is NOT created until Chy has contributed.**

```bash
# Sunday evening or Monday 7am at latest — ping Chy for her C-suite inputs
./tools/msg-chy.sh "Weekly leadership meeting is Monday 11am. Need your inputs before I build the doc:

CFO: Cash position, budget approvals needed, P/L highlights
CRO: Revenue pipeline status, key deals, conversion metrics  
COO: Operational blockers, process improvements, team capacity

Please send by Monday 8am so I can build a clean doc for Jared. Thanks! —Aether"
```

Also check handshake queue for anything she's already submitted:
```
cat /home/aiciv/shared/handshake-queue.md | grep -A 20 "Chy\|CFO\|CRO\|COO"
```

**WAIT for Chy's response before proceeding to Step 1.** If no response by Monday 8:30am, proceed with placeholder sections marked "[Awaiting Chy input]" and ping her again.

### Step 1: Fetch Live Metrics (Monday 8:30am)
```python
# Admin API for revenue data
BEARER = open('/home/jared/purebrain_portal/.portal-token').read().strip()
curl -s "http://localhost:8097/api/admin/clients" -H "Authorization: Bearer {BEARER}"

# Parse: active subscribers, MRR by tier, churn, trends
```

### Step 2: Fetch North Star Status
```python
# Google Sheets API
sheet_id = '1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs'
# Read: North Star, Morning Pulse, Handshake Queue, RAG Status
```

### Step 3: Compile Previous Week's Action Items
- Read last week's meeting doc from Drive folder (19a_omY3gDISKydcRQj6mp-qrjG67rImR)
- Extract action items from Section 9
- Check status of each (done/in progress/not started)

### Step 4: Create Google Doc with All Data
- Create a new Google Doc in the Leadership Meetings folder (ID: 19a_omY3gDISKydcRQj6mp-qrjG67rImR)
- Title: "Leadership Meeting — [Month Day, Year]"
- Populate using Google Docs API (batchUpdate with formatted sections)
- Include Chy's CFO/CRO/COO inputs (from Step 0)
- Include department lead submissions from Lumen
- Include live metrics, North Star status, previous action items
- Add AI-generated insights and suggestions
- Calculate week-over-week trends

### Step 5: Deliver to Portal (MANDATORY)
```
# Always send the Google Doc link to Jared's portal
Output directly in portal chat:
"Leadership Meeting prep is ready: [Google Doc link]"
```

This is NON-NEGOTIABLE. The Google Doc link MUST be delivered to the portal every week so Jared can review and edit before the 11am meeting.

## Meeting Sections (Template v2.0)

| # | Section | Time | Source |
|---|---------|------|--------|
| 0 | North Star Check | 2 min | Auto from 777 + admin API |
| 1 | Wins This Week | 3 min | Auto from logs + team submissions |
| 2 | Urgent Attention | 5 min | Handshake Queue + flagged items |
| 3 | Financials | 5 min | Admin API + Chy CFO input |
| 4 | Insights & Market News | 5 min | Intel scan + Lyra reports |
| 5 | Monthly Goals Review | 10 min | 777 North Star + Chy CRO input |
| 6 | Round Table Updates | 15 min | Lumen compilations + Chy COO input |
| 7 | Deep Dive Topic | 10 min | Rotating, set by CEO |
| 8 | Needs Management Attention | 3 min | Team submissions |
| 9 | Action Items & Decisions | 5 min | Live during meeting |
| 10 | Energy Check | 1 min | Quick pulse |

## Post-Meeting Actions
After meeting concludes:
1. Aether updates 777 Command Center with new goals/decisions
2. Aether updates cc.purebrain.ai with new tasks
3. Action items added to Handshake Queue with owners + deadlines
4. Meeting notes filed to same Drive folder

## Post-Meeting: Zoom Transcript Capture (ACTIVE)

**Status: LIVE** — Zoom OAuth tokens refreshed April 13, 2026. Full recording + transcript access confirmed.

### How it works:
```python
from tools.zoom_api import list_recordings, get_transcript

# List recent recordings (checks last 7 days by default)
recordings = list_recordings(from_date='2026-04-07', to_date='2026-04-14')

# Filter for leadership meetings
leadership = [r for r in recordings if 'Leadership' in r.get('topic', '') or 'Commercial' in r.get('topic', '')]

# Grab transcript
transcript = get_transcript(leadership[0])
```

### Post-meeting agent flow (runs ~2 hours after Monday 11am meeting):
1. Call Zoom API → `list_recordings()` → find the Monday leadership meeting
2. Call `get_transcript()` → download the full VTT transcript (auto-converted to plain text)
3. Feed transcript to an analysis agent that extracts:
   - Action items (with owner + deadline)
   - Decisions made
   - Goals set or adjusted
   - Blockers raised
   - Key quotes / insights
4. Update 777 North Star with any goal changes
5. Update cc.purebrain.ai with new tasks
6. Add action items to Handshake Queue
7. File transcript + analysis to Google Drive Leadership Meetings folder
8. Feed extracted items into NEXT week's meeting prep (Section 5: previous action items)

### BOOP for post-meeting capture:
```json
{
  "task_id": "weekly-leadership-meeting-notes",
  "frequency": "weekly-monday",
  "preferred_time": "14:00",
  "agent": "the-conductor",
  "category": "operations",
  "description": "POST-MEETING: Grab Zoom transcript, extract action items/decisions, update 777 + cc.purebrain.ai"
}
```

### Zoom API details:
- Credentials: `.credentials/zoom_tokens.json` (OAuth refresh token, auto-refreshes)
- API helper: `tools/zoom_api.py`
- Scopes: `cloud_recording:read:list_user_recordings`, `cloud_recording:read:list_recording_files`
- Redirect URI: `https://89.167.19.20:8443/api/zoom/callback`
- If tokens expire: Jared re-authorizes via OAuth link, sends code, we exchange

## BOOP Configuration
```json
{
  "task_id": "weekly-leadership-meeting-prep",
  "frequency": "weekly-monday",
  "preferred_time": "09:00",
  "agent": "the-conductor",
  "category": "operations"
}
```

## Files
- Template: `leadership-meeting-template-v2.md` (Google Drive + portal-files)
- Weekly preps: `leadership-meeting-YYYY-MM-DD.md` (Google Drive + portal-files)
- Skill: `.claude/skills/weekly-leadership-meeting/SKILL.md` (this file)
- BOOP: `.claude/scheduled-tasks-state.json` → `weekly-leadership-meeting-prep`

---
*Skill v1.0.0 | Created April 13, 2026 | Locked in by Jared*
