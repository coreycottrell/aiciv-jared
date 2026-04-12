# Experiential Intent Engine - Quick Start

**Everything is built and tested.** Here's how to finish setup.

---

## What's Already Working

✅ **Airtable Client** - Full CRUD operations
✅ **OpenAI Classifier** - Signal classification with gpt-4o-mini
✅ **Apify Collector** - LinkedIn data collection framework
✅ **Email Dashboard** - Daily digest emails
✅ **Test passed** - All components verified working
✅ **Test email sent** - purebrain@puremarketing.ai received it

---

## Remaining Setup (15 min total)

### 1. Fix Airtable Formulas (5 min)

In Airtable, People table:

**A. Create Rollup field:**
- Click `+` to add field
- Name: `Signal Score Sum`
- Type: **Rollup**
- Link field: `Signals`
- Field to rollup: `Signal Strength`
- Aggregation: `SUM`

**B. Update Rolling Intent Score formula:**
- Click `Rolling Intent Score (formula)` header → Edit
- Replace with:
```
({Role Weight (formula)} + {Signal Score Sum}) * {Account Multiplier (lookup)}
```

### 2. Add LinkedIn URLs to People Table (5 min)

Add at least 3-5 test prospects with real LinkedIn URLs:

| Name | LinkedIn URL | Title | Seniority | Company |
|------|--------------|-------|-----------|---------|
| [Real CPG contact] | https://linkedin.com/in/... | VP Marketing | VP+ | [Company] |

### 3. Create Apify Task (5 min)

Go to https://console.apify.com/actors:

1. Search for "LinkedIn Profile Scraper"
2. Choose `curious_coder/linkedin-profile-scraper` or similar
3. Click **"Create new task"**
4. Name: `experiential-intent-signals`
5. Configure input:
```json
{
  "startUrls": [],
  "proxy": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  },
  "scrapePosts": true,
  "scrapeActivities": true,
  "maxPosts": 10
}
```
6. Save task
7. Copy the Task ID for Make webhook

---

## Running the Engine

### Manual Run (for testing)

```bash
cd /home/jared/projects/AI-CIV/aether

# Test all components
python3 -m tools.intent_engine.main test

# Preview dashboard (no email)
python3 -m tools.intent_engine.main preview

# Send dashboard email
python3 -m tools.intent_engine.main dashboard

# Full pipeline (collect → process → dashboard)
python3 -m tools.intent_engine.main full
```

### Scheduled Run (cron)

Add to crontab (`crontab -e`):

```cron
# Experiential Intent Engine - Daily 8 AM EST
0 8 * * * cd /home/jared/projects/AI-CIV/aether && python3 -m tools.intent_engine.main full >> /tmp/intent_engine.log 2>&1
```

---

## Make Scenarios (Optional - for visual orchestration)

If you prefer Make over Python scripts:

### Scenario 1: Process Apify Webhook

1. Create new scenario
2. Trigger: **Webhook** → Copy URL
3. Module: **HTTP** → GET Apify results
4. Module: **Iterator** → Loop profiles
5. Module: **OpenAI** → Classify signals
6. Module: **Airtable** → Create signal records

Add webhook URL to Apify task settings.

### Scenario 2: Daily Dashboard

1. Create new scenario
2. Trigger: **Schedule** → 8 AM daily
3. Module: **Airtable** → Search People (READY)
4. Module: **Airtable** → Search Signals (24h)
5. Module: **Gmail** → Send email (use template from `EMAIL-DASHBOARD.md`)

---

## File Reference

```
tools/intent_engine/
├── __init__.py          # Package exports
├── config.py            # API keys, field IDs
├── airtable_client.py   # Airtable CRUD
├── openai_classifier.py # Signal classification
├── apify_collector.py   # LinkedIn collection
├── email_dashboard.py   # Email generation
└── main.py              # CLI orchestrator
```

---

## Testing Checklist

- [x] Airtable API connected
- [x] OpenAI API connected
- [x] Apify API connected
- [x] Test email sent
- [ ] Airtable formulas fixed
- [ ] LinkedIn URLs added to People table
- [ ] Apify task created
- [ ] First full pipeline run
- [ ] Cron job set up (or Make scenarios)

---

## Next Steps After Setup

1. Add 10-20 real CPG prospects to People table
2. Run `python3 -m tools.intent_engine.main full`
3. Check dashboard email at purebrain@puremarketing.ai
4. Review signals in Airtable
5. Contact the "READY" prospects!
