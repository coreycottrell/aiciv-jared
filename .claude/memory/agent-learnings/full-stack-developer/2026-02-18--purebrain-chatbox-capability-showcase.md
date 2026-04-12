# Memory: PureBrain Chatbox Capability Showcase Enhancement

**Date**: 2026-02-18
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Modifying the PureBrain.ai homepage awakening chatbox flow

---

## What Was Done

Enhanced the PureBrain.ai homepage chatbox awakening flow to add a 4-message capability showcase step BEFORE the activation CTA (`[SHOW_PRICING]`).

## How the Chatbox Works

The homepage (WordPress page ID 11) contains inline JavaScript with two key areas:
1. `SYSTEM_PROMPT` constant (~line 6085-6122 in the local HTML snapshot) - controls AI behavior via Claude API
2. `processResponse()` function (~line 6400) - adds context hints to Claude at specific message counts

The AI is a live Claude API call (claude-sonnet-4-20250514) with a system prompt controlling the conversation arc. `[SHOW_PRICING]` tag in AI response triggers the in-chat CTA button.

## Changes Made

### 1. SYSTEM_PROMPT: Added step 6 CAPABILITY SHOWCASE
- Inserted new step 6 between NAMING (step 5) and TRANSITION (renumbered to step 7)
- Instructs AI to share 4 capability messages: strategic thinking, team of agents, deep work, activation unlock
- Explicitly says to use ||| delimiter and NOT pitch — make it personal

### 2. SYSTEM_PROMPT: Updated CRITICAL RULES
- Changed the transition rule to say "share capabilities (step 6) before transitioning"
- Added rule: "Tie each capability back to what you've learned about them specifically"

### 3. processResponse() context hints
- Changed `messageCount >= 13` → `messageCount === 13` (triggers capability showcase, no [SHOW_PRICING])
- Added `messageCount >= 16` → triggers final [SHOW_PRICING] transition

## Key Technical Details

- **Page ID**: 11
- **API endpoint**: `https://purebrain.ai/wp-json/wp/v2/pages/11`
- **Auth**: Basic auth with Aether user + app password `FlFr2VOtlHiHaJWjzW96OHUJ`
- **Content field**: POST with `{"content": "raw_html_content"}` to update page
- **Raw content length after changes**: 311,894 chars (was 310,071)
- The homepage HTML file is also saved at: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/PURE_BRAIN_Your_Brain_Your_AI_Actual_Intelligence_Agentic_AI.html`

## Verification

All 5 checks passed on live site:
- "CAPABILITY SHOWCASE" found
- "messageCount === 13" found
- "messageCount >= 16" found
- "7. TRANSITION" found
- "6. TRANSITION" NOT found (old text removed)

## Pattern: Modifying Elementor/WP Pages with Inline JS

The homepage uses Elementor with a custom HTML widget containing all the chatbox JS. The entire thing is in the page raw content. To modify:
1. `curl -s -u "user:apppass" "https://site/wp-json/wp/v2/pages/ID?context=edit"` - get raw
2. Python string replace on the raw content
3. POST back with `{"content": modified_content}` - returns 200 on success
4. Re-fetch with ?context=edit to verify changes are live
