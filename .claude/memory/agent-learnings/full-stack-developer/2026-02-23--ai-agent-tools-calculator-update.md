# Memory: AI Agent Builder Tools Added to Calculator

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational
**Topic**: AI Tool Stack Calculator - AI Agents category expansion

## What Was Done

Added 5 new AI agent builder tools to the "AI Agents / Automation Platforms" category in the AI Tool Stack Calculator at `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`.

Deployed to WordPress page 777 at purebrain.ai.

## Tools Added

| Tool | Price/mo | Description |
|------|----------|-------------|
| StackAI Starter | $199 | No-code enterprise AI agent builder (stack-ai.com) |
| Voiceflow Pro | $60 | Build + deploy conversational AI agents |
| CrewAI Basic | $99 | Multi-agent collaboration framework |
| Gumloop Solo | $37 | No-code AI workflow automation |
| Botpress Plus | $89 | Visual AI agent builder + chat deployment |

Note: Adept AI was researched but is enterprise-only with no public pricing - not added.

## Pricing Sources
- StackAI: $199/mo Starter (from Capterra/review sites - their pricing page is JS-rendered)
- Voiceflow: $60/mo/editor Pro plan (from voiceflow.com/pricing)
- CrewAI: $99/mo Basic (from ZenML blog + CrewAI pricing)
- Gumloop: $37/mo Solo (from gumloop.com/pricing - confirmed via fetch)
- Botpress: $89/mo Plus (from botpress.com/pricing research)

## Calculator Stats After Update
- Total tools: 143 (was ~138)
- Total categories: 30
- Category marketRate updated: 99 → 199 to reflect expanded tool set

## File Modification Pattern (CRITICAL)
- ONLY modify the JavaScript CATEGORIES array - never touch the `<style>` block
- Style block: 35,747 chars - must remain unchanged
- Deploy uses regex extraction of `<style>` and `<body>` content
- WordPress page 777: ai-tool-stack-calculator at purebrain.ai
- Credentials: PUREBRAIN_WP_USER=Aether, PUREBRAIN_WP_APP_PASSWORD in .env

## Deployment Pattern
```python
import re, requests
with open('exports/ai-tool-stack-calculator-v3.html', 'r') as f:
    html = f.read()
style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
wp_override = "body.page { background: #080a12 !important; ... }\n"
clean_content = f"<style>\n{wp_override}{style_match.group(1)}\n</style>\n{body_match.group(1)}"
wp_content = f"<!-- wp:html -->\n{clean_content}\n<!-- /wp:html -->"
# POST to /wp-json/wp/v2/pages/777 with auth=(Aether, app_password)
# Then DELETE /wp-json/elementor/v1/cache
```
