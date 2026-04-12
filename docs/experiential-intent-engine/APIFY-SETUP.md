# Apify Setup - LinkedIn Signal Collection

**Component**: LinkedIn Activity Monitoring
**Actor**: `apify/linkedin-profile-scraper` or `curious_coder/linkedin-profile-scraper`

---

## Overview

Apify pulls LinkedIn activity for prospects in your People table, detecting signals like:
- Posts about experiential marketing
- Engagement with competitor content
- Role changes (timing triggers)
- Comments on activation/launch content

---

## Step 1: Create Apify Actor Task

### In Apify Console:
1. Go to https://console.apify.com/actors
2. Search for "LinkedIn Profile Scraper"
3. Click "Create new task"
4. Name it: `experiential-intent-signals`

### Configure Input:
```json
{
  "startUrls": [],
  "proxy": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  },
  "scrapeCompany": false,
  "scrapeJobTitle": true,
  "scrapeEducation": false,
  "scrapePosts": true,
  "scrapeActivities": true,
  "maxPosts": 10,
  "maxConnections": 0
}
```

---

## Step 2: Create Webhook to Make

After each run, Apify can POST results directly to Make:

### Webhook URL (from Make scenario):
```
https://hook.us1.make.com/YOUR_WEBHOOK_ID
```

### In Apify Task Settings:
1. Go to "Integrations" tab
2. Add webhook: "On run succeeded"
3. Paste Make webhook URL
4. Payload template:
```json
{
  "actorTaskId": "{{actorTaskId}}",
  "actorRunId": "{{actorRunId}}",
  "datasetId": "{{defaultDatasetId}}"
}
```

---

## Step 3: Schedule Daily Run

### In Apify Console:
1. Go to your task
2. Click "Schedules" tab
3. Add schedule:
   - **Cron**: `0 6 * * *` (6 AM daily)
   - **Timezone**: America/New_York

---

## Step 4: Pull LinkedIn URLs from Airtable

Before each run, we need fresh LinkedIn URLs from People table.

### Option A: Apify Integration (recommended)
Use Apify's Airtable integration actor to pull URLs:

```json
{
  "baseId": "app3PhIudYCZ8VCCF",
  "tableId": "tblzttcsprjQFWBmt",
  "apiKey": "patcjYGyBxRGQfjdj...",
  "view": "Grid view",
  "fields": ["LinkedIn URL"]
}
```

### Option B: Make Pre-Step
Create Make scenario that:
1. Pulls People records from Airtable
2. Extracts LinkedIn URLs
3. Triggers Apify run with URL list

---

## Expected Output Format

Apify returns data like:
```json
{
  "linkedinUrl": "https://www.linkedin.com/in/johndoe/",
  "fullName": "John Doe",
  "headline": "VP Marketing at Coca-Cola",
  "posts": [
    {
      "text": "Just wrapped an amazing experiential activation...",
      "timestamp": "2026-02-01T14:30:00Z",
      "likes": 145,
      "comments": 23
    }
  ],
  "activities": [
    {
      "type": "like",
      "targetPost": "...",
      "timestamp": "2026-02-02T09:15:00Z"
    }
  ]
}
```

---

## Signal Detection Logic (for Make/OpenAI)

### Signal Types to Detect:
| Signal Type | Detection Pattern | Strength |
|-------------|-------------------|----------|
| `posted_about_launch` | Post mentions "launch", "activation", "experiential" | 8-10 |
| `commented_on_activation` | Comment on experiential marketing content | 6-8 |
| `liked_experiential_post` | Liked post from experiential page/brand | 4-6 |
| `follows_experiential_page` | Following known experiential brands | 3-5 |
| `timing_trigger` | New role in last 90 days | 7-9 |
| `commented_on_competitor` | Engaged with competitor content | 5-7 |

---

## API Usage (Programmatic)

### Start a Run:
```bash
curl -X POST "https://api.apify.com/v2/actor-tasks/YOUR_TASK_ID/runs?token=apify_api_2rKl2AsE9ZBsuk0R9tBWk0E2qV2mDq3896Ls" \
  -H "Content-Type: application/json" \
  -d '{
    "startUrls": [
      {"url": "https://www.linkedin.com/in/prospect1/"},
      {"url": "https://www.linkedin.com/in/prospect2/"}
    ]
  }'
```

### Get Results:
```bash
curl "https://api.apify.com/v2/datasets/DATASET_ID/items?token=apify_api_2rKl2AsE9ZBsuk0R9tBWk0E2qV2mDq3896Ls"
```

---

## Cost Estimation

- **LinkedIn Scraper**: ~$5-10 per 1000 profiles
- **Daily run** (50 profiles): ~$0.50/day
- **Monthly**: ~$15

---

## Next Step

After Apify collects data, it webhooks to Make for processing.
See: `MAKE-WORKFLOWS.md`
