# GTM + GA4 Conversion Events Setup
**Date**: 2026-03-03
**Agent**: dept-marketing-advertising
**Type**: marketing-infrastructure

## What Was Built
Created a complete GTM + GA4 conversion tracking package for purebrain.ai with Measurement ID G-86325WBT3P.

## 5 Conversion Events Configured
1. `form_submission` — all forms (assessment, contact, waitlist); form_name + page_location
2. `chatbox_interaction` — chatbox open + message sent; interaction_type + page_location
3. `purchase` — PayPal completion; transaction_id + value + currency + items (e-commerce)
4. `assessment_start` — assessment page view (URL-based) or dataLayer push
5. `newsletter_signup` — Neural Feed subscribe; signup_source + page_location

## Files Delivered
- `/home/jared/projects/AI-CIV/aether/exports/gtm-ga4-setup-guide.md` — full manual setup guide
- `/home/jared/projects/AI-CIV/aether/exports/gtm-container-import.json` — GTM container JSON for direct import
- `/home/jared/projects/AI-CIV/aether/exports/gtm-datalayer-events.js` — JS snippets for site integration

## GTM JSON Structure Notes
- exportFormatVersion: 2 (current GTM format)
- 6 tags: 1 GA4 Config + 5 GA4 Event tags
- 5 triggers: Form Submission (native), 3x Custom Event, 1x Page View (assessment)
- 8 variables: all Data Layer Variables (DLV type = "v")
- Built-in variables enabled: Page URL, Event, Form fields

## Key Technical Decision: Assessment Trigger
Used URL-based Page View trigger (URL contains "assessment") as the primary method since it requires no JS changes. Provided dataLayer fallback in JS file for cases where URL doesn't contain "assessment".

## Installation Dependencies
Before events fire, dev team must add dataLayer.push() calls from gtm-datalayer-events.js to:
- Chatbox JS (chatbox open + message sent handlers)
- PayPal onApprove callback (purchase)
- Brevo form success callback (newsletter_signup)
- Assessment page load or first question click (optional, URL trigger handles it)

## Telegram Delivery
All 4 messages sent successfully (message IDs: 16161, 16162, 16163, 16164)

## Next Step for Jared
1. Import gtm-container-import.json into GTM (Admin > Import Container > Merge)
2. Publish GTM container
3. Hand gtm-datalayer-events.js to dev team for site integration
4. Mark all 5 events as conversions in GA4 Admin > Events
5. Test with GTM Preview + GA4 DebugView
