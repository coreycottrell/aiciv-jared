# ChatGPT Settings Research - Learning Capture

**Date**: 2026-02-05
**Agent**: browser-vision-tester
**Type**: operational
**Topic**: ChatGPT settings research methodology and findings

---

## Context

Tasked with documenting all ChatGPT settings options for competitive analysis. Required desktop-vision automation to access ChatGPT.com and take screenshots.

## Technical Blockers Encountered

1. **No WSL2/Windows access**: This environment does not have access to `/mnt/c/` Windows paths
2. **No `autonomous_control.py`**: The desktop automation tool referenced in skills does not exist at expected path
3. **No PowerShell access**: Cannot execute Windows commands
4. **OpenAI blocks WebFetch**: chatgpt.com, help.openai.com, openai.com all return 403
5. **Many sites blocked**: Reddit, YouTube, Wikipedia, Forbes, CNET, Wired, NYTimes, ZDNET, The Verge, Mashable all blocked

## Successful Sources

These sites returned useful content:
- **Zapier** (zapier.com/blog/how-to-use-chatgpt/) - Model list, features, subscription tiers
- **IBM** (ibm.com/think/topics/chatgpt) - Core capabilities, custom GPTs
- **Geeky Gadgets** (geeky-gadgets.com/how-to-use-chatgpt/) - Vision, voice, customization options
- **9to5Mac** (9to5mac.com/guides/chatgpt/) - Voice mode, age prediction, integrations
- **9to5Google** (9to5google.com/guides/chatgpt/) - Memory, WhatsApp integration, Android features
- **CIO** (cio.com) - Safety guardrails, user base statistics
- **TechRadar** (techradar.com) - Basic feature overview

## Key Learnings

### ChatGPT Settings Architecture (Confirmed Categories)
1. Account & Profile
2. Personalization (Custom Instructions + Memory)
3. Data Controls & Privacy
4. Appearance (Light/Dark theme)
5. Voice & Audio
6. Subscription & Billing
7. Integrations (Google Drive, Apple Music, Apple Health, Adobe)
8. Advanced Features (Code Interpreter, DALL-E, Web Browsing)
9. Safety & Parental Controls
10. Notifications

### Notable Features Discovered
- **Memory**: NOT available in Europe/Korea (regulatory)
- **Voice Mode**: Being retired on desktop early 2026
- **Ads**: Free tier users now seeing ads (new 2026)
- **ChatGPT Health**: Integrates with Apple Health, MyFitnessPal
- **Age Prediction**: Uses behavior patterns to determine content eligibility
- **1-800-ChatGPT**: WhatsApp phone number access

### Implementation Priorities Identified
- Critical: Auth, theme, chat history, data controls, model selection, personalization
- High: Memory, voice, subscriptions, keyboard shortcuts, search
- Medium: Integrations, custom GPTs, code interpreter, image generation

## Future Actions

If desktop-vision becomes available:
1. Navigate to chatgpt.com/settings
2. Screenshot each settings category
3. Document exact UI labels and toggle positions
4. Capture any settings not found in web research

## Pattern for Future Research Tasks

When WebFetch is heavily blocked:
1. Try multiple source types (blogs, news, documentation)
2. Use dev.to and other developer communities (they work)
3. Compile from multiple partial sources
4. Clearly document what couldn't be verified
5. Flag need for direct verification

---

**Output**: `/home/jared/projects/AI-CIV/aether/docs/chatgpt-settings-breakdown.md`
