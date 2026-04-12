# Migration Portal Brevo Integration — Build Complete

**Date**: 2026-02-23
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Brevo API integration for AI Migration Portal — contact attributes + drip lists + JS module

---

## What Was Built

Complete Brevo data pipeline for the PureBrain AI Migration Portal (spec: `docs/from-telegram/ai-migration-portal-spec.md`).

### Files Created

| File | Purpose |
|------|---------|
| `/home/jared/projects/AI-CIV/aether/exports/migration-brevo-integration.js` | JS module — 3 core functions for migration data flow |
| `/home/jared/projects/AI-CIV/aether/tools/setup_brevo_migration_attributes.py` | Python setup script — creates Brevo attributes + lists |
| `/home/jared/projects/AI-CIV/aether/config/migration_brevo_config.json` | Config output — IDs of all created resources |

---

## Brevo Resources Created (Live, 2026-02-23)

### Contact Attributes (9 new + 1 existing TAGS)

| Attribute | Type | Purpose |
|-----------|------|---------|
| COMPETITOR | text | Competitor slug (chatgpt, claude, gemini, etc.) |
| PRIMARY_USE_CASES | text | Comma-separated use cases from quiz |
| USAGE_FREQUENCY | text | How often they used the competitor tool |
| HAD_CUSTOM_CONFIG | boolean | Had custom instructions set up |
| MAIN_FRUSTRATION | text | Primary pain point that drove the switch |
| MIGRATION_STATUS | text | not_started / in_progress / complete |
| MIGRATION_PROFILE | text | Full JSON profile from export analysis |
| CONVERSATION_COUNT | number | Total imported conversations |
| TOP_TOPICS | text | Comma-separated top 5 topics |
| TAGS | text | Already existed — reused |

### Migration Lists (8 new, all created successfully)

| List Name | ID | Purpose |
|-----------|-----|---------|
| PureBrain Migration Leads | 11 | General pool — all migration intent |
| PureBrain Migration — ChatGPT | 12 | ChatGPT drip trigger list |
| PureBrain Migration — Claude | 13 | Claude drip trigger list |
| PureBrain Migration — Gemini | 14 | Gemini drip trigger list |
| PureBrain Migration — Perplexity | 15 | Perplexity drip trigger list |
| PureBrain Migration — Midjourney | 16 | Midjourney drip trigger list |
| PureBrain Migration — Copilot | 17 | Copilot drip trigger list |
| PureBrain Migration — Other | 18 | Fallback drip trigger list |

---

## JS Module Architecture

### `saveMigrationIntent(data)` — Module 1
- Called on Exodus quiz completion
- Upserts Brevo contact with all 9 migration attributes
- Adds to List 3 (Neural Feed) + List 11 (Migration Leads)
- Tags: migration-intent, from-[competitor]
- Uses `updateEnabled: true` for upsert pattern (same as existing PureBrain pattern)

### `saveMigrationProfile(email, profile)` — Module 2
- Called after portal processes ChatGPT/Claude export
- Updates MIGRATION_STATUS to 'complete'
- Stores full profile JSON in MIGRATION_PROFILE attribute
- Stores CONVERSATION_COUNT as number for segmentation
- Stores TOP_TOPICS as comma-separated text

### `triggerMigrationDrip(email, competitor)` — Module 3
- Adds contact to competitor-specific list (IDs 12-18)
- Adding to list triggers Brevo automation with "Contact added to list" trigger
- Reads list IDs from BREVO_DRIP_LIST_* env vars OR hardcoded defaults
- Graceful fallback: logs warning if list ID not configured, returns success: false with reason

### `handleExodusQuizCompletion(data)` — Composite helper
- Runs Intent + Drip in sequence
- Use this single function on Exodus landing page quiz completion

---

## Critical Brevo Patterns (Reuse These)

### Contact upsert pattern
```javascript
await brevoRequest('POST', '/contacts', {
  email,
  attributes: { COMPETITOR: 'chatgpt', MIGRATION_STATUS: 'not_started', ... },
  listIds: [3, 11],
  updateEnabled: true,  // CRITICAL — upsert not create-only
});
```

### Contact attribute update
```javascript
await brevoRequest('PUT', `/contacts/${encodeURIComponent(email)}`, {
  attributes: { MIGRATION_STATUS: 'complete', MIGRATION_PROFILE: jsonString },
});
```

### Add to list (triggers automation)
```javascript
await brevoRequest('POST', `/contacts/lists/${listId}/contacts/add`, {
  emails: [email],
});
```

### Brevo attribute types for API
- text fields → `'text'`
- number fields → `'float'` (Brevo calls it float internally)
- boolean fields → `'boolean'`

---

## Important: Automation Workflows NOT Created Yet

Brevo has no REST API for automation workflows (confirmed in prior session).
The 8 drip lists exist. The automation workflows that READ from those lists
must be created manually in Brevo UI:

For each competitor list (IDs 12-18):
1. Brevo UI → Automations → Create new
2. Trigger: "Contact added to a list" → select the competitor list
3. Build email sequence for that competitor's pain points

---

## .env Variables Needed (Add After Setup)

```bash
BREVO_MIGRATION_LEADS_LIST_ID=11
BREVO_DRIP_LIST_CHATGPT=12
BREVO_DRIP_LIST_CLAUDE=13
BREVO_DRIP_LIST_GEMINI=14
BREVO_DRIP_LIST_PERPLEXITY=15
BREVO_DRIP_LIST_MIDJOURNEY=16
BREVO_DRIP_LIST_COPILOT=17
BREVO_DRIP_LIST_UNKNOWN=18
```

These are already hardcoded as defaults in the JS module (from the live run).
The env vars allow override without code changes.

---

## Dead Ends Avoided

1. **HAD_CUSTOM_CONFIG as text vs boolean**: Stored as `boolean` in Brevo — passes as `Boolean(value)` in JS
2. **Arrays in Brevo**: No native array attribute type — serialise with `value.join(',')` for text fields
3. **MIGRATION_PROFILE size**: Brevo text attributes have no documented limit but keep JSON compact — no raw conversation text
4. **TAGS already existed**: Setup script uses `already_exists` detection — idempotent, safe to re-run
