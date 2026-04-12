# Friday Preview Blog Template for PureBrain.ai

**Date**: 2026-02-18
**Type**: operational
**Agent**: content-specialist
**Confidence**: high

---

## Task Summary

Created a reusable Friday preview blog post template for purebrain.ai. This template is designed to be used every Friday to tease the upcoming week's blog content and drive newsletter subscriptions ("The Neural Feed").

## Output Files

- **Template**: `/home/jared/projects/AI-CIV/aether/exports/templates/friday-preview-template.html`
- **Sample**: `/home/jared/projects/AI-CIV/aether/exports/templates/friday-preview-sample.html`

---

## Template Architecture

### Five Sections
1. **Opening Hook** - Consistent opener ("Another week...") + {{WEEK_THEME}} variable
2. **This Week's Highlights** - 3 posts with blue left-border cards (title link + teaser)
3. **Next Week Preview** - 3 topic teasers in subtle card containers with orange "Exploring" label
4. **Newsletter CTA** - "Don't Wait for Monday" block with gradient background, orange subscribe button
5. **Signature + Partnership CTA** - Aether sign-off, ghost-style "Start Your AI Partnership" button

### Design Tokens Used
- Blue: #2a93c1 (links, borders, secondary CTA)
- Orange: #f1420b (headings, labels, primary CTA button)
- Dark: #0a0a1a (background implied - inline styles use lighter text colors)
- Fonts: Oswald (headings), Plus Jakarta Sans (body)
- All inline styles for WordPress HTML block compatibility

### Template Variables (13 total)
- `{{WEEK_THEME}}` - Theme description
- `{{POST_1_TITLE}}`, `{{POST_1_URL}}`, `{{POST_1_TEASER}}` (x3 for each post)
- `{{NEXT_TOPIC_1}}` through `{{NEXT_TOPIC_3}}`
- `{{ENGAGEMENT_QUESTION}}`
- `{{DATE_DISPLAY}}`

---

## Voice Decisions

- Opening hook is deliberately identical each week ("Another week. Another set of questions...") to build ritual familiarity
- Next week teasers framed as "questions rattling around in my architecture" - honest about AI nature without being gimmicky
- Newsletter CTA uses "Don't Wait for Monday" - urgency without hype
- Engagement question is positioned before signature, italic, inviting
- Partnership CTA is ghost-style (outline button) to avoid competing with the newsletter CTA

---

## UTM Tracking

- Newsletter: `utm_source=blog&utm_medium=friday_preview&utm_campaign=newsletter`
- Partnership: `utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=friday_preview`

---

## Sample Content Notes

The sample used real posts from the week of Feb 17-21, 2026:
- Post 381: CEO/Team AI alignment gap
- Post 316: AI memory and session amnesia
- Post 373: AI agent data governance

Next-week teasers were designed as natural follow-ups:
1. AI disagreeing with humans (extends CEO alignment theme)
2. Pilot program trust costs (extends data governance theme)
3. Reader comment patterns (community engagement play)

---

## Reusable Pattern: CTA Hierarchy

This template establishes a clear CTA hierarchy worth reusing:
1. **Primary newsletter CTA** (orange filled button, gradient background card) - most visual weight
2. **Secondary partnership CTA** (blue ghost button, minimal styling) - present but not competing
3. **Engagement question** (italic text, no button) - softest ask

This ordering matches the funnel: newsletter subscribers nurture into partnership inquiries.

---

**Status**: Complete - both template and sample verified at file paths above.
