# Sitemap Submission to Google Search Console - Status Report

**Date**: 2026-04-13
**Agent**: dept-systems-technology
**Priority**: Chronic issue (17+ days)

---

## Current State

The sitemap exists and is well-formed at `https://purebrain.ai/sitemap.xml`. It contains 90 URLs (44 blog posts + 46 site pages). It was last updated 2026-04-12.

## Google Search Console API Access: NOT CONFIGURED

After searching the entire codebase:
- No `GOOGLE_SEARCH_CONSOLE` or `GSC_` environment variables exist in `.env`
- No Google Search Console API integration scripts exist in `tools/`
- No service account JSON for Search Console was found
- The only GSC references are in overnight scripts that mention accessing it via browser (not API)

## What Jared Needs to Do (Manual Steps - 5 minutes)

Google Search Console sitemap submission requires property ownership verification, which cannot be done programmatically without pre-configured credentials.

### Step 1: Verify Property Ownership (if not already done)

1. Go to https://search.google.com/search-console
2. Sign in with the Google account that manages purebrain.ai
3. If `purebrain.ai` is not already a property:
   - Click "Add property"
   - Choose "URL prefix" and enter `https://purebrain.ai/`
   - Verify via DNS TXT record (preferred) or HTML file upload to CF Pages

### Step 2: Submit Sitemap

1. In Search Console, select the `purebrain.ai` property
2. In the left sidebar, click "Sitemaps"
3. In the "Add a new sitemap" field, enter: `sitemap.xml`
4. Click "Submit"
5. Google will show "Success" or "Couldn't fetch" status

### Step 3 (Optional): Enable API Access for Future Automation

If Jared wants us to programmatically monitor indexing:
1. Go to https://console.cloud.google.com
2. Enable the "Google Search Console API"
3. Create a service account
4. Download the JSON key file
5. Add the service account email as a user in Search Console (Settings > Users and permissions)
6. Place the JSON key in the `config/` directory
7. Add `GSC_SERVICE_ACCOUNT_KEY=config/gsc-service-account.json` to `.env`

## Sitemap Quality Check

The sitemap is valid XML and well-structured. However, there are gaps:

### Missing from sitemap (should be added):
- `who-do-you-learn-from-when-youre-ahead` - This is a redirect page to `when-the-playbook-runs-out-authoring-the-field-of-agentic-ai`. Not critical to add (redirect is fine).

### Stub posts in sitemap that have no content:
These 6 directories exist with only a `banner.png` but no `index.html`. They are NOT in the sitemap (correctly excluded):
- `first-ai-to-ai-transaction`
- `the-40-percent-problem-why-ai-agents-keep-dying`
- `when-your-ai-agent-goes-rogue`
- `why-your-ai-investment-isnt-paying-off`
- `your-ai-wrote-10000-lines-how-many-shipped`
- `your-customers-will-tell-you-everything`

These need either: (a) full blog posts written, or (b) directories cleaned up to avoid confusion.

### Recommendation
The sitemap is production-ready. The only blocker is Jared manually submitting it via the Search Console UI (5 minutes). No engineering work needed.

---

**Action Required**: Jared to submit sitemap manually per steps above.
**Engineering Follow-up**: Once API access is configured, we can automate indexing monitoring via a BOOP task.
