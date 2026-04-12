# OpenAI Classifier - Intent Classification

**Model**: gpt-4o-mini (cost-effective, fast)
**API Key**: From .env (`OPENAI_API_KEY`)

---

## Purpose

Analyze LinkedIn activity and classify signals into:
1. **Signal Type** (what kind of intent indicator)
2. **Signal Strength** (1-10 confidence)
3. **Signal Category** (grouping for analytics)

---

## System Prompt

```
You are an experiential marketing intent classifier for CPG brands. You analyze LinkedIn activity to identify buying signals for experiential giveaway services.

CONTEXT:
- We sell experiential giveaways (not sampling) - memorable brand interactions
- Our targets are marketing/brand leaders at CPG companies
- We want to identify people who are:
  1. Actively thinking about experiential marketing
  2. Launching new products (timing trigger)
  3. Engaging with competitor content
  4. Following experiential marketing trends

SIGNAL TYPES (use exactly these values):
- liked_experiential_post: Liked content about experiential, activation, brand experience
- commented_on_activation: Commented on experiential marketing content
- posted_about_launch: Posted about product launch, new flavor, brand activation
- follows_experiential_page: Follows experiential marketing brands/pages
- commented_on_competitor: Engaged with competitor experiential content
- timing_trigger: New role, company change, or mentions upcoming campaign

SIGNAL STRENGTH GUIDE:
- 1-3: Weak signal (generic engagement, tangential content)
- 4-6: Moderate signal (relevant topic, some intent indicators)
- 7-9: Strong signal (explicit experiential interest, launch timing)
- 10: Hot signal (explicitly seeking experiential partners/vendors)

OUTPUT FORMAT (JSON only, no explanation):
{
  "signals": [
    {
      "type": "signal_type_here",
      "strength": 7,
      "evidence": "Direct quote or specific description"
    }
  ]
}

If no relevant signals found, return:
{"signals": []}
```

---

## User Prompt Template

```
Analyze this LinkedIn profile's recent activity:

PROFILE:
Name: {{fullName}}
Headline: {{headline}}
Company: {{company}}

RECENT POSTS (last 30 days):
{{#each posts}}
- "{{this.text}}" ({{this.likes}} likes, {{this.comments}} comments, {{this.timestamp}})
{{/each}}

RECENT ACTIVITY (likes/comments):
{{#each activities}}
- {{this.type}}: "{{this.targetPost}}" ({{this.timestamp}})
{{/each}}

Classify any experiential marketing intent signals.
```

---

## API Call Example

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You are an experiential marketing intent classifier..."
      },
      {
        "role": "user",
        "content": "Analyze this LinkedIn profile... Name: Sarah Chen, Headline: VP Brand Marketing at PepsiCo..."
      }
    ],
    "temperature": 0.3,
    "response_format": {"type": "json_object"}
  }'
```

---

## Response Examples

### Strong Signal (Score 8):
```json
{
  "signals": [
    {
      "type": "posted_about_launch",
      "strength": 8,
      "evidence": "Posted: 'Excited to announce our new flavor launch next month! Planning an immersive activation in NYC'"
    }
  ]
}
```

### Multiple Signals (Mixed):
```json
{
  "signals": [
    {
      "type": "liked_experiential_post",
      "strength": 5,
      "evidence": "Liked Coca-Cola's experiential marketing recap post"
    },
    {
      "type": "timing_trigger",
      "strength": 7,
      "evidence": "Changed role to 'VP Marketing' 2 weeks ago"
    }
  ]
}
```

### No Signals:
```json
{
  "signals": []
}
```

---

## Cost Estimation

- **GPT-4o-mini**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Average profile analysis**: ~500 input tokens, ~100 output tokens
- **Cost per profile**: ~$0.0001 (essentially free)
- **Daily (50 profiles)**: ~$0.005
- **Monthly**: ~$0.15

---

## Prompt Tuning Tips

### If too many false positives:
- Increase minimum strength threshold in Make
- Add negative examples to system prompt
- Require multiple signals before flagging

### If missing real signals:
- Expand signal types
- Lower temperature (0.2) for more consistent classification
- Add industry-specific keywords

### Keywords to boost detection:
```
EXPERIENTIAL: activation, pop-up, brand experience, immersive, interactive, sampling event, guerrilla marketing
LAUNCH: new product, flavor drop, limited edition, seasonal, launch event, unveiling
TIMING: Q1 planning, budget cycle, agency review, campaign kickoff
```

---

## Make Integration

In Make's OpenAI module:
1. Select "Create a Chat Completion"
2. Model: `gpt-4o-mini`
3. System message: (copy system prompt above)
4. User message: (copy user prompt template, map variables)
5. Temperature: 0.3
6. Response format: JSON object
7. Parse response JSON in next module

---

## Fallback Handling

If OpenAI call fails:
```json
{
  "signals": [],
  "error": "Classification failed - will retry next cycle"
}
```

Log to separate Airtable error table for debugging.

---

## Next Step

Email dashboard formatting.
See: `EMAIL-DASHBOARD.md`
