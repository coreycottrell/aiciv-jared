# Experiential Intent Engine - Automation Stack

**Created**: 2026-02-03
**Purpose**: Automated CPG prospect signal collection, scoring, and daily action queue

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LinkedIn      │────▶│    Apify        │────▶│   Airtable      │
│   (Signals)     │     │  (Collector)    │     │  (Signals Tbl)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Email         │◀────│    Make         │◀────│   OpenAI        │
│  (Dashboard)    │     │ (Orchestrator)  │     │  (Classifier)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Components

### 1. Apify Automation (LinkedIn Signal Collection)
- **Actor**: LinkedIn Profile Scraper or custom actor
- **Trigger**: Daily at 6 AM EST
- **Input**: List of LinkedIn URLs from People table
- **Output**: Push signals to Airtable Signals table

### 2. Make Workflows (Orchestration)
- **Workflow 1**: Process new signals → Score → Update People
- **Workflow 2**: Daily "Who to Contact" queue generation
- **Workflow 3**: Email dashboard to purebrain@puremarketing.ai

### 3. OpenAI Classification (Intent Scoring)
- **Model**: GPT-4o-mini (cost-effective)
- **Task**: Classify signal intent (experiential, competitor, timing)
- **Output**: Signal strength (1-10) and category

### 4. Email Automation (Daily Dashboard)
- **Frequency**: Daily at 8 AM EST
- **Recipients**: purebrain@puremarketing.ai
- **Content**: Top 10 prospects to contact today

---

## API Credentials

All stored in `/home/jared/projects/AI-CIV/aether/.env`:
- `AIRTABLE_API_KEY` - Airtable Personal Access Token
- `AIRTABLE_BASE_ID` - Base ID: app3PhIudYCZ8VCCF
- `OPENAI_API_KEY` - OpenAI API key
- `APIFY_API_KEY` - Apify API token
- `MAKE_API_KEY` - Make API key

---

## Airtable Schema Reference

### Tables
- **People** (tblzttcsprjQFWBmt) - Prospects
- **Signals** (tbl7w57ZbGh2Z7BkE) - LinkedIn activity signals
- **Companies** (tblOlRcyiCGrZbFDx) - Account data
- **Outreach Log** (tblEgIl2FZvnwFTYn) - Contact history

### Key Fields for Automation
| Table | Field | ID | Purpose |
|-------|-------|-----|---------|
| People | LinkedIn URL | fldrTikuYF69C3YOy | Apify input |
| People | Rolling Intent Score | fld243TU1PVaP1hGa | Prioritization |
| People | Readiness Flag | fldeax1jrHPGSi02H | Queue filter |
| Signals | Signal Type | fldVKlz7ECv4PkVxi | OpenAI output |
| Signals | Signal Strength | fld0lX4uPeznrtW36 | OpenAI output |
| Signals | Source | fldhZds8meNYhyXfh | "LinkedIn" |
| Signals | Signal Timestamp | fldsomMOtxnOaaEZ1 | When detected |

---

## Implementation Status

- [x] Airtable schema created
- [x] Formulas verified (1 needs fix - Rolling Intent Score)
- [ ] Apify actor configured
- [ ] Make workflows built
- [ ] OpenAI prompt tuned
- [ ] Email template designed
- [ ] End-to-end test

---

## Next Steps

See individual component docs:
1. `APIFY-SETUP.md` - LinkedIn signal collection
2. `MAKE-WORKFLOWS.md` - Orchestration flows
3. `OPENAI-CLASSIFIER.md` - Intent classification
4. `EMAIL-DASHBOARD.md` - Daily report
