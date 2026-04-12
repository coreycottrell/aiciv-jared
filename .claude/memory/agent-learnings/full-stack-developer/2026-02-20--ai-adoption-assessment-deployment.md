# AI Adoption Assessment Page Deployment
**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: Full assessment page build + WordPress deployment with Brevo, GA4, social share

## What Was Built
- Enhanced HTML assessment page (1500 lines) deployed to purebrain.ai/ai-adoption-review/
- WordPress Page ID: 577
- Template: elementor_canvas (full-width, no theme header/footer)

## Brevo List Created
- List ID: 7 ("Not Yet Qualified - AI Assessment")
- Client-side POST to https://api.brevo.com/v3/contacts
- Attributes stored: SOURCE, ASSESSMENT_RESULT, ASSESSMENT_SCORE
- `updateEnabled: true` handles duplicate submissions gracefully
- API key is client-side (acceptable for Brevo - it's a write-only contact key)

## GA4 Events Added
All use `gtag()` + `dataLayer.push()` dual approach:
- `assessment_started` - on Begin click
- `question_answered` - with question_number, answer_index, answer_score
- `assessment_completed` - with result_tier, total_score
- `cta_clicked` - when qualified user clicks awakening CTA
- `share_clicked` - with share_method (twitter/linkedin/copy_link)
- `email_submitted` - when NOT YET user submits email

## Social Share Buttons (QUALIFIED result)
- Twitter/X: opens intent URL with pre-filled text + page URL
- LinkedIn: opens share-offsite URL
- Copy Link: uses navigator.clipboard with execCommand fallback
- All styled on-brand: black for X, blue for LinkedIn, blue-tinted for copy

## Real Blog Posts Used (NOT YET result)
Fetched from wp-json - most relevant 4:
1. The Difference Between Using AI and Having an AI Partner
2. Why AI Memory Changes Everything
3. Why Your AI Pilot Is Succeeding and Failing at the Same Time
4. Your CEO Sees AI Differently Than Your Team Does

## Key Patterns
- WordPress REST API for page creation: POST /wp-json/wp/v2/pages
- `template: "elementor_canvas"` = full-width page (no theme chrome)
- Content goes in `content` field as raw HTML (not Elementor JSON)
- Brevo duplicate contact: returns 400 with `code: "duplicate_parameter"` - handle gracefully
- GA4 tracking: shim pattern (gtag shim + dataLayer) works whether GA4 is loaded by WP or not

## Files
- Enhanced HTML: /home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment-deployed.html
- Live URL: https://purebrain.ai/ai-adoption-review/
