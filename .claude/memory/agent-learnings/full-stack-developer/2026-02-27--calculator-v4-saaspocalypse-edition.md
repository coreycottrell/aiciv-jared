# Calculator v4: SaaSpocalypse Edition

**Date**: 2026-02-27
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Updated the AI Tool Stack Calculator from v3 (162 tools, 31 categories) to v4 (188 tools, 35 categories).

## Output File
`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v4.html`

## Key Changes

### Tool Count
- v3: 162 tools, 31 categories
- v4: 188 tools, 35 categories  
- Marketed as: 195+ tools, 35 categories

### New Tools Added to Existing Legal Category
- Thomson Reuters Westlaw ($460/mo) — stock −16%
- LexisNexis ($300/mo) — stock −14%
- LegalZoom Business ($49/mo) — stock −20%
- Category renamed: "AI Legal ⚡ SaaSpocalypse Wave 1"

### New Category: Cybersecurity & Identity (Wave 2)
ID: `cybersecurity`
Tools: CrowdStrike, Okta, SailPoint, Zscaler, JFrog, Cloudflare Zero Trust, Snyk, Veracode
Note: Each tool description includes the stock drop % for narrative impact

### New Category: Enterprise Software (Wave 1)
ID: `enterprise_software`
Tools: Salesforce, ServiceNow, Adobe Creative Cloud, Workday, DocuSign, Oracle Cloud, Palantir
Note: Each description references the SaaSpocalypse stock impact

### New Category: Project Management & Productivity
ID: `project_mgmt`
Tools: Monday.com, Asana, Trello, ClickUp, Notion Plus, Linear, Basecamp, Jira
Note: Different IDs from existing PM category (monday_pm vs monday_ai, etc.) — no collision

### SaaSpocalypse Alert Banner
- Class: `.calc-saas-alert`
- Position: Below hero h1 and personalized chatbox, above hero stats
- Content: Live stats ($285B Wave 1, $15B Wave 2, −32% IGV, $14B Anthropic revenue, $380B valuation)
- Animated pulse dot for "live" feel
- Wave 1 and Wave 2 breakdown in compact format
- Full WP color override CSS for page-id-777

### New Preset
- ID: `saaspocalypse`
- Label: "SaaSpocalypse Stack"
- Tools: All the disrupted enterprise tools (Salesforce, CrowdStrike, Workday, etc.)
- Button styled with orange border to stand out

## Pattern: ID Collision Avoidance
When adding standalone PM tools while existing PM-AI category exists:
- Existing: `monday_ai`, `notion_ai`, `clickup`, `asana` (in `pm` category)
- New: `monday_pm`, `notion_pm`, `clickup_pm`, `asana_pm` (in `project_mgmt` category)
- Both can coexist — user can check both if they use the standalone + AI versions

## Pattern: Narrative Tool Descriptions
For SaaSpocalypse wave tools, description includes the stock impact:
`'CrowdStrike Falcon Go', price: 300, desc: 'AI endpoint security — stock −11.6% when Claude Code found 500+ hidden vulns'`
This makes the calculator itself tell the narrative story.

## Verification Results
- All 24 key element checks passed
- HTML structure valid (open/close tags balanced)
- All CTAs point to https://purebrain.ai/#awakening
- No test page links
- File: 163,804 chars, ~5600 lines
