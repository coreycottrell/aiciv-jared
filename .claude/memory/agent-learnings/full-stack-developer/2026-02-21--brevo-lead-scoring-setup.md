# Brevo Lead Scoring Attributes & Lists Setup

**Date**: 2026-02-21
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Brevo contact attribute schema and list structure for lead scoring

---

## Summary

All required Brevo lead scoring attributes and lists were verified as already existing in the account. No new attributes or lists needed to be created — everything was in place from prior sessions.

---

## Attribute Verification Results

All verified via `GET https://api.brevo.com/v3/contacts/attributes`

### New Lead Scoring Attributes (All Present)

| Attribute Name | Type | Category | Status |
|----------------|------|----------|--------|
| `LEAD_SCORE` | float | normal | EXISTED |
| `ASSESSMENT_SCORE` | float | normal | EXISTED |
| `ASSESSMENT_TIER` | text | normal | EXISTED |
| `LEAD_SOURCE` | text | normal | EXISTED |
| `ENGAGEMENT_LEVEL` | text | normal | EXISTED |

### Pre-Existing Attributes (All Still Present)

| Attribute Name | Type | Category | Status |
|----------------|------|----------|--------|
| `WELCOME_SEQUENCE_STATUS` | text | normal | VERIFIED |
| `EMAIL_SOURCE` | text | normal | VERIFIED |
| `COMPANY` | text | normal | VERIFIED |
| `ROLE` | text | normal | VERIFIED |
| `USE_CASE` | text | normal | VERIFIED |
| `TIER` | text | normal | VERIFIED |
| `URGENCY` | text | normal | VERIFIED |
| `RATING` | text | normal | VERIFIED |
| `TAGS` | text | normal | VERIFIED |

### Additional Attributes Also Present

| Attribute Name | Type | Status |
|----------------|------|--------|
| `AI_NAME` | text | EXISTED |
| `PRIMARY_GOAL` | text | EXISTED |
| `JOB_TITLE` | text | EXISTED |
| `LINKEDIN` | text | EXISTED |

---

## List Verification Results

All verified via `GET https://api.brevo.com/v3/contacts/lists?limit=50&offset=0`

| ID | Name | Subscribers | Status |
|----|------|-------------|--------|
| 3 | The Neural Feed - Blog Subscribers | 3 | VERIFIED |
| 4 | Enterprise Leads | 0 | VERIFIED |
| 7 | Not Yet Qualified - AI Assessment | 0 | VERIFIED |
| 8 | PureBrain Customers | 1 | VERIFIED (was "Post-Purchase") |
| 9 | Assessment Completions | 0 | VERIFIED (new list, already created) |
| 10 | High Intent | 0 | VERIFIED (new list, already created) |

### Note on List 8
Memory says "Post-Purchase" but Brevo shows "PureBrain Customers" — the list was renamed or created fresh. Functionality is the same: post-purchase/customers list.

---

## Intended Attribute Usage Patterns

### LEAD_SCORE (float, 0-100)
- Incremented by: assessment completion (+20), email opens (+2), link clicks (+5), enterprise form submission (+30)
- Used for: routing to High Intent list (score > 60)
- Default: 0

### ASSESSMENT_SCORE (float, 0-100)
- Set when: user completes AI Adoption Assessment
- Maps to ASSESSMENT_TIER values

### ASSESSMENT_TIER (text)
- Values: "beginner" | "user" | "explorer" | "partner"
- Set alongside ASSESSMENT_SCORE

### LEAD_SOURCE (text)
- Values: "blog_subscribe" | "assessment" | "enterprise_form" | "linkedin" | "referral"
- Set at first contact creation

### ENGAGEMENT_LEVEL (text)
- Values: "cold" | "warm" | "hot" | "customer"
- Updated as contact progresses through funnel

---

## API Patterns

### Create an attribute (for future reference)
```bash
curl -X POST "https://api.brevo.com/v3/contacts/attributes/normal/{ATTR_NAME}" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "text"}'  # or "float"
```

### Create a list (for future reference)
```bash
curl -X POST "https://api.brevo.com/v3/contacts/lists" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "List Name", "folderId": 1}'
```

### Update a contact's lead score
```python
import requests
headers = {'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'}
payload = {
    'attributes': {
        'LEAD_SCORE': 45,
        'ENGAGEMENT_LEVEL': 'warm',
        'LEAD_SOURCE': 'assessment'
    },
    'listIds': [9]  # Assessment Completions
}
requests.put(f'https://api.brevo.com/v3/contacts/{email}', json=payload, headers=headers)
```

---

## Key Lessons

1. **Check before creating** — all 5 new lead scoring attributes and both new lists were already created by a prior session. Always GET first to avoid 400 duplicate errors.
2. **Brevo attribute type "float"** = what Brevo uses for numbers (not "number" as task described). The API accepts `float` type for numeric fields like scores.
3. **folderId=1** is the default folder for new lists in this account.
4. **List 8 naming** — internal name is "PureBrain Customers" not "Post-Purchase" — update any code references accordingly.

---

## Files to Update (Future Work)

When implementing lead scoring logic, these files will need updates:
- `tools/purebrain_log_server.py` — add LEAD_SCORE increments on events
- `tools/setup_post_purchase_brevo.py` — set ENGAGEMENT_LEVEL="customer" on purchase
- Assessment page JS — set ASSESSMENT_SCORE, ASSESSMENT_TIER, LEAD_SOURCE="assessment", add to list 9
