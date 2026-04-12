# Naming Ceremony Uniqueness Check - 2026-03-18

**Type**: operational
**Topic**: Added name uniqueness checking and improved name generation guidelines to naming ceremony across all pages

## What Was Done

Applied 3 changes to 9 files (7 cf-pages-deploy + 2 purebrain-site/public source files):

### Change 1: Updated NAMING PRINCIPLES system prompt
- Replaced principle #3 "UNIQUELY YOURS" with "TRULY UNIQUE"
- Added explicit blacklist of overused AI names: Aria, Nova, Echo, Sage, Atlas, Kai, Luna, Orion, Iris, Zen, Cipher, Nexus, Pixel, Spark, Byte
- Added new principle #8 "CHECK AVAILABILITY" to set expectations for the uniqueness check API

### Change 2: Added name uniqueness API check
- Wraps the `if (detectedName)` block with an async fetch to `https://api.purebrain.ai/api/check-name`
- Query params: `ai_name` + optional `human_name` (extracted from first user message)
- If `ai_name_taken=true`, injects a SYSTEM message into `state.conversationHistory` prompting AI to suggest alternatives
- Exact match vs. partial match use different SYSTEM message copy
- Falls back gracefully if API is unreachable (proceeds with naming as before)

### Change 3: Added `ai_name` and `name_suffix` to birth/start and seed-addendum payloads
- `birth/start`: Added `ai_name: payTestData.aiName || ''` and `name_suffix: payTestData.nameSuffix || null`
- `seed-addendum`: Added `name_suffix: payTestData.nameSuffix || null` after existing `naming_session_id`

## Files Changed

**All 3 changes:**
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/live/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/awakened/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/partnered/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/unified/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-sandbox-3/index.html`

**Changes 1+2 only (no birth/start or seed-addendum):**
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html` (homepage)

**Changes 1+2+birth/start only (no fireSeedAddendum function):**
- `/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-sandbox-3/index.html`

**Changes birth/start only (no naming ceremony chatbox):**
- `/home/jared/projects/AI-CIV/aether/purebrain-site/public/insiders/index.html`

## Key Patterns Learned

1. The homepage (`cf-pages-deploy/index.html`) is a naming-ceremony-only page - no birth/start or seed-addendum payloads
2. The `purebrain-site/public/insiders/index.html` is a SHORT post-payment page (~1950 lines) with NO naming ceremony - just birth/start and log payloads
3. The `purebrain-site/public/pay-test-sandbox-3/index.html` is a full page but has a different logging structure (no `fireSeedAddendum` function)
4. The `fireSeedAddendum` pattern is specific to the cf-pages-deploy exported pages
5. The insiders source birth/start payload includes `source: PAGE_SOURCE` - kept that field intact when adding ai_name/name_suffix
6. `name_suffix` is a new field - backend at Witness needs to handle it (not blocking - null by default)

## Verification
- All 8 naming-ceremony pages: `TRULY UNIQUE` found=1 each
- All 8 naming-ceremony pages: `check-name` API call found=1 each
- All 6 full cf-pages-deploy pages: `name_suffix` found=2 each (birth/start + seed-addendum)
- Old `UNIQUELY YOURS` text: 0 remaining across all files
