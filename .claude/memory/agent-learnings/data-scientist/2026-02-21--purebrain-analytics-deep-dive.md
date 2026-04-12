# Memory: purebrain.ai Analytics Deep Dive - Feb 2026

**Agent**: data-scientist
**Date**: 2026-02-21
**Type**: operational + teaching

---

## What I Learned

### purebrain.ai Current State (Snapshot: Feb 21, 2026)

**Site**: 9 indexed pages, 7 blog posts published in 8 days (Feb 14-20)
**Email list**: 8 contacts, all Jared's own test emails, 0 external subscribers
**Revenue**: $0 (all payment logs show $0.00, all test/localhost)
**Chat engagement**: 208 sessions over 10 days, 62% multi-turn, avg 5.8 user messages when engaged

### Access Methods That Work

| Resource | How to Access |
|----------|--------------|
| WP pages/posts | `curl -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" https://purebrain.ai/wp-json/wp/v2/pages` |
| WP plugins | Same auth, `/wp-json/wp/v2/plugins` |
| IAWP API namespace | `/wp-json/iawp` (exists but search endpoint returned `{"success":false}`) |
| Yoast SEO head | `/wp-json/yoast/v1/get_head?url=URL` - returns title, meta, robots |
| Purebrain custom API | `/wp-json/purebrain/v1/log-conversation-fallback` (POST only) |
| Brevo contacts | `curl -H "api-key: ${BREVO_API_KEY}" https://api.brevo.com/v3/contacts` |
| Brevo lists | Same auth, `/v3/contacts/lists` |
| Conversation data | `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl` |
| Payment data | `/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl` |

### What Has NO Programmatic Access (Requires Dashboard Login)

- **GA4**: GTM container is GTM-WTDXL4VJ. GA4 may be inside it but no service account credentials in .env. To fix: get service account JSON from Google Cloud Console, add path to .env.
- **Google Search Console**: No OAuth tokens. To fix: create service account in GCP, grant to GSC, download JSON.
- **Microsoft Clarity**: No API token. To fix: generate from Clarity dashboard Settings > Data Export.
- **Independent Analytics**: Plugin v2.14.4 is active. Data in WP database. PHP functions: `iawp_analytics()`, `iawp_singular_analytics()`, `iawp_top_posts()`. REST endpoint `/iawp/search` POST returns `{"success":false}` even with auth. Could expose via custom WP plugin function.

### Key Patterns for Future Analysis

1. **Conversation logs contain good behavioral data**: Parse `purebrain_web_conversations.jsonl` to understand user engagement, topics, drop-off points.

2. **Bot traffic is a data quality issue**: IP 59.103.113.75 (Pakistan) sent 51 sessions of jailbreak attempts. Filter this IP when doing engagement analysis.

3. **Jared's primary dev IP**: 108.35.12.204 (51% of sessions). Filter for real user analysis.

4. **The awakening flow works emotionally**: One verified prospect (IP 89.167.19.20, "Alex" who chose name "Aria") went through full naming ceremony and asked about pricing. Product-market fit signal at micro scale.

5. **Meta descriptions are missing on all blog posts**: Easy SEO win that should be fixed.

6. **Assessment pages have no email capture**: High-intent visitors completing assessments leave without converting to email.

### SEO State

- All pages: `robots: index, follow` - no indexing blocks
- Sitemap: `/sitemap_index.xml` - 4 sub-sitemaps (posts, pages, categories, authors)
- Yoast SEO v27.0 active - handles schema, canonical, sitemap
- Missing: meta descriptions on blog posts, article schema verification, internal linking

### Brevo Integration State

- API key in `.env` as `BREVO_API_KEY`
- 6 lists created: PureBrain Customers (8), Enterprise Leads (4), The Neural Feed (3), identified_contacts (5), Not Yet Qualified AI Assessment (7), Your first list (2)
- 0 campaigns sent
- Welcome sequence automation was built (7 emails) but never activated with real subscribers

---

## Teaching Notes

**For future analytics tasks on purebrain.ai**:

1. Start with local log files for behavioral data - they're richer than any GA4 report at this stage
2. Brevo API works cleanly for subscriber/list data
3. WP REST API with Aether credentials works for site structure data
4. GA4 + GSC + Clarity require dashboard access or proper OAuth setup - document this gap clearly
5. The Independent Analytics plugin is the most accessible page-view data store but needs a custom WP endpoint to expose via REST

**For analytics recommendations**:

The site is in pre-traction phase. The right analysis framework is:
- Not "how to analyze traffic" (there's barely any yet)
- But "how to instrument everything before traffic arrives"
- And "what quick SEO wins can generate initial organic traffic"

Meta descriptions + internal links + assessment email gates are the highest-leverage near-term actions.

---

**Report location**: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/analytics-deep-dive-2026-02-21.md`
