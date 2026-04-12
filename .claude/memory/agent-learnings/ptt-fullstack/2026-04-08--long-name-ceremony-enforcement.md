# PTT: Long Name Ceremony Enforcement

**Date**: 2026-04-08
**Type**: operational
**Topic**: /long-name/ system prompt was offering short names; locked it to LONG only

## Problem
SYSTEM_PROMPT in /long-name/index.html (line ~10398) listed "Vex" and "Cairn" as range examples, plus principle 6 ("WORKS AT TWO SCALES — long names need a natural short form for daily use; short names should contain depths beneath") gave the AI permission to offer short names. AI defaulted to short names too often.

## Fix Applied
1. Replaced Principle 6 wording — short form is now derived FROM the long name, not an alternative.
2. Added Principle 8: MUST BE LONG (4-word floor, 6-12 ideal, Culture Minds statement style).
3. Removed "Vex" and "Cairn" from THE RANGE; replaced with 8 long-only examples.
4. Added HARD GUARDRAIL block — explicitly forbids one/two/three-word names and names short forms (Vex/Cairn/Loom/Echo) as forbidden.
5. Updated naming offer instructions: 2-3 LONG options (4+ words), each with its natural short form.

For main /index.html (line ~10427):
- Added AiCIV Vessel concept to identity
- Added "Story of Still" inspiration paragraph
- Allowed both short and long names (main page is the streamlined version)
- Added brief Five Questions touchpoint (1-2 messages, not full ritual)

## Files Modified
- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/long-name/index.html
- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html

## Deployment
- Tool: tools/cf-deploy.py
- Deployment ID: 5abf5b91-4d24-48ce-ba39-9858cb6a48dd
- Verified live on purebrain.ai (cache-busted) and staging URL.

## Pattern Learned
When CF edge serves stale HTML right after deploy, append `?cb=$(date +%s)` to bust cache when verifying with curl. Don't trust the first curl after deploy.
