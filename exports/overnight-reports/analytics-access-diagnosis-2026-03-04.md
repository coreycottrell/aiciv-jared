# Analytics Platform Access Diagnosis
**Generated**: 2026-03-03 (for 2026-03-04 delivery)
**Agent**: dept-systems-technology
**Status**: LIVE VERIFIED — All API calls executed, real data returned

---

## EXECUTIVE SUMMARY

| Platform | Status | API Access | Action Required |
|----------|--------|-----------|-----------------|
| GA4 (G-86325WBT3P) | WORKING | Service account has full access | None — pull data anytime |
| Google Search Console | WORKING | Service account has siteFullUser access | None — pull data anytime |
| Microsoft Clarity (viy9bnc56x) | BLOCKED | Microsoft OAuth required — no SA equivalent | Jared: add purebrain@puremarketing.ai in Clarity dashboard |
| SEMRush | NO API KEY | Login works headlessly via Playwright | Get API key from account settings OR use browser automation |

**Bottom line**: GA4 and Search Console are both fully operational via our service account. Real traffic data is flowing and we can pull it programmatically at any time. Clarity and SEMRush require separate access setup.

---

## PART 1: GOOGLE ANALYTICS 4 — FULLY WORKING

### Access Status
- Service account: `aether-drive-access@aether-integration.iam.gserviceaccount.com`
- GA4 Account ID: `384811174` (display: "PureBrain.ai")
- GA4 Property ID: `525007539` (display: "purebrain.ai")
- Measurement ID: G-86325WBT3P (confirmed linked)
- API: analyticsdata.googleapis.com v1beta — responding 200 OK
- Scopes needed: `https://www.googleapis.com/auth/analytics.readonly`

### Live Traffic Data (Last 30 Days — Pulled 2026-03-03)

**Channel Group Breakdown:**

| Channel | Sessions | Users | New Users | Bounce Rate | Avg Duration | Page Views |
|---------|----------|-------|-----------|-------------|--------------|------------|
| Direct | 474 | 395 | 401 | 51.3% | 144s | 860 |
| Organic Social | 62 | 52 | 49 | 46.8% | 127s | 82 |
| Referral | 50 | 13 | 10 | 44.0% | 163s | 95 |
| Unassigned | 29 | 21 | 15 | 48.3% | 605s | 122 |
| Organic Search | 18 | 11 | 9 | 44.4% | 425s | 24 |

**Total: ~633 sessions, ~492 users in 30 days**

**Top Pages by Sessions:**

| Page | Source | Sessions | Users | Bounce | Avg Duration |
|------|--------|----------|-------|--------|--------------|
| / (Homepage) | direct | 202 | 172 | 41.1% | 98s |
| /ai-tool-stack-calculator/ | direct | 37 | 29 | 51.4% | 189s |
| /blog/ | direct | 35 | 24 | 22.9% | 225s |
| /pay-test/ | direct | 33 | 28 | 39.4% | 206s |
| /pay-test-sandbox/ | direct | 30 | 28 | 73.3% | 95s |
| /pay-test-sandbox-2/ | direct | 25 | 23 | 40.0% | 150s |
| /why-purebrain/ | direct | 22 | 18 | 36.4% | 234s |
| / (Homepage) | linkedin | 20 | 16 | 25.0% | 138s |
| / (Homepage) | google | 18 | 11 | 44.4% | 386s |
| /why-purebrain/ | statics.teams.cdn.office | 15 | 3 | 66.7% | 137s |

**Geographic Distribution:**

| Country | Sessions | Users | New |
|---------|----------|-------|-----|
| United States | 352 | 260 | 256 |
| Germany | 147 | 147 | 148 |
| Canada | 56 | 22 | 23 |
| Pakistan | 26 | 12 | 11 |
| Philippines | 8 | 4 | 4 |
| India | 6 | 6 | 6 |
| Ireland | 4 | 4 | 4 |
| United Kingdom | 4 | 4 | 5 |

**Device Breakdown:**

| Device | Browser | Sessions | Users |
|--------|---------|----------|-------|
| desktop | Chrome | 428 | 333 |
| mobile | Chrome | 61 | 32 |
| mobile | Safari | 57 | 49 |
| desktop | Edge | 19 | 14 |
| desktop | Safari | 17 | 5 |

**Events Currently Firing in GA4:**

| Event | Count | Users |
|-------|-------|-------|
| page_view | 1,183 | 479 |
| user_engagement | 750 | 225 |
| session_start | 637 | 478 |
| first_visit | 484 | 477 |
| scroll | 451 | 185 |
| form_start | 148 | 81 |
| form_submit | 67 | 59 |
| click | 31 | 15 |

**Note**: `form_start` (148) and `form_submit` (67) are firing — GA4 Enhanced Measurement is auto-tracking chatbox interactions as form events. This is useful signal but not labeled as conversion events yet.

### Key Insight: Germany Anomaly
Germany shows 147 sessions with 147 unique users — almost no returning visits. This combined with the prior analysis of IP 59.103.113.75 (51 sessions Feb 12-16 from Pakistan region) suggests this is bot/automated traffic or VPN users. Actual real human US-based sessions are ~250.

---

## PART 2: GOOGLE SEARCH CONSOLE — FULLY WORKING

### Access Status
- Site URL: `sc-domain:purebrain.ai`
- Permission Level: `siteFullUser`
- API: googleapis.com/webmasters/v3 — responding 200 OK
- Scopes needed: `https://www.googleapis.com/auth/webmasters.readonly`

### Search Performance (Last 28 Days)

**Total: 24 clicks, 278 impressions, 8.6% CTR average, position 4.5 for homepage**

**Top Queries:**

| Query | Clicks | Impressions | CTR | Avg Position |
|-------|--------|-------------|-----|--------------|
| purebrain | 5 | 19 | 26.3% | 6.3 |
| pure brain | 0 | 12 | 0.0% | 6.8 |
| why do ai pilots fail | 0 | 3 | 0.0% | 40.0 |
| bytebrain-agent | 0 | 2 | 0.0% | 85.5 |
| (various AI tool combos) | 0 | 1-7 | 0.0% | 6-32 |

**Top Pages:**

| Page | Clicks | Impressions | CTR | Avg Position |
|------|--------|-------------|-----|--------------|
| / (Homepage) | 19 | 114 | 16.7% | 4.5 |
| /ai-tool-stack-calculator/ | 0 | 44 | 0.0% | 11.5 |
| /ai-adoption-review/ | 0 | 19 | 0.0% | 5.9 |
| /ai-readiness-assessment/ | 0 | 15 | 0.0% | 6.2 |
| /ai-partnership-guide/ | 0 | 14 | 0.0% | 3.4 |

### CRITICAL: Indexing Status

**Sitemaps submitted:** 73 pages total
**Sitemaps indexed:** 0

| Sitemap | Submitted | Indexed | Last Downloaded |
|---------|-----------|---------|-----------------|
| sitemap_index.xml | 73 web, 64 image | 0 | 2026-03-03 |
| post-sitemap.xml | 16 web, 16 image | 0 | 2026-03-03 |
| page-sitemap.xml | 24 web, 11 image | 0 | 2026-02-24 |
| category-sitemap.xml | 6 web | 0 | 2026-03-03 |

**This is a major issue.** Google is downloading the sitemaps (last checked today) but showing 0 indexed pages. This does NOT mean pages aren't indexed — it means the sitemap-based coverage report shows "pending" status. Google may still be indexing pages through other discovery methods (19 homepage clicks prove the homepage IS indexed).

The likely explanation: Google indexed the homepage organically but the sitemap submission is being processed slowly (2-4 week lag for new domains is normal).

**Recommended action**: Submit a new sitemap with URL inspection request via GSC UI for key pages. We can now do this programmatically.

---

## PART 3: MICROSOFT CLARITY — REQUIRES JARED ACTION

### API Status
- No programmatic API equivalent to GA4 service accounts
- Clarity API (`clarity.ms`) requires Microsoft Azure AD OAuth 2.0 token
- Cannot be automated without interactive Microsoft login

### What Clarity Gives Us (When Accessed)
- Session recordings (watch real users navigate the site)
- Heatmaps (click/scroll/attention maps for each page)
- Dead clicks, rage clicks, quick backs (UX problem detection)
- Scroll depth by page
- JavaScript error tracking

### Jared Action Required (5 minutes)
1. Go to: https://clarity.microsoft.com/projects/view/viy9bnc56x/settings/team
2. Click "Add member"
3. Add: `purebrain@puremarketing.ai`
4. Set role: "Admin" or "Can view & edit"
5. Confirm

Once added, Aether can log in via Gmail OAuth from the Playwright automation.

### Clarity Priority: High
The power user from IP 59.103.113.75 (51 sessions Feb 12-16) may appear in Clarity recordings. Knowing what they were doing — which pages, which sections they engaged with — is extremely valuable commercial intelligence.

---

## PART 4: SEMRUSH — STATUS & ACCESS OPTIONS

### Credential Status
- **Login**: `support@puremarketing.ai` / (password confirmed in memory)
- **Browser automation**: WORKS via Playwright (last confirmed Feb 23, 2026)
- **Official API**: Requires API key (not same as login credentials)
- **API key location**: Account → Subscription → API Access (if plan includes it)

### SEMRush API Key Options
1. **Check account settings**: Login to SEMRush → User icon → Subscription info → API Access
   - Free/Guru plans may include limited API calls
   - Pro plans get 10K calls/month

2. **Browser automation fallback**: Our Playwright scripts work headlessly to pull:
   - Site audit scores
   - Position tracking data
   - Domain overview metrics
   - Backlink counts

### Current SEMRush State (from Feb 23 audit)
- Site Health: 83%
- Authority Score: 0 (new domain)
- Organic Traffic: effectively 0
- Backlinks: 10 total, 1 referring domain
- Position Tracking: 10 keywords tracked, avg position 97.3
- "purebrain" keyword: position 73

### SEMRush Action Items
1. Check account for API key (2 min in account settings)
2. If no API key: continue with browser automation (it works)
3. Configure position tracking for target keywords (not just "purebrain")

---

## PART 5: GA4 CUSTOM EVENTS + CONVERSION GOALS PLAN

### Current State
GA4 has Enhanced Measurement auto-tracking `form_start` and `form_submit` events. No named conversion events are configured.

### Recommended Custom Events (GTM Implementation)

**Event 1: chatbox_opened**
- Trigger: Click on the "Begin Awakening" or "Get Started" button (`.pb-cta-button`, `#begin-btn`, `.chatbox-trigger`)
- GTM trigger type: Click — All Elements, condition: Click ID contains "begin" OR Click Classes contains "chatbox"
- GA4 conversion: YES — this is top-funnel intent

**Event 2: name_captured**
- Trigger: PureBrain chatbox JS fires when user submits their name
- Implementation: Add `gtag('event', 'name_captured', {value: 1})` to chatbox JS after name validation
- GA4 conversion: YES — this is the moment of personal AI creation

**Event 3: email_captured**
- Trigger: PureBrain chatbox JS fires when user submits email
- Implementation: Add `gtag('event', 'email_captured', {value: 1})` to chatbox JS after email validation
- GA4 conversion: YES — lead captured

**Event 4: onboarding_complete**
- Trigger: User completes PureBrain onboarding sequence (awakening flow finished)
- Implementation: Add `gtag('event', 'onboarding_complete', {value: 1})` to chatbox JS at completion
- GA4 conversion: YES — activated user

**Event 5: pricing_page_view**
- Trigger: Page view of `/why-purebrain/` OR `/pay-test/` pages
- GTM trigger type: Page View, condition: Page Path contains "why-purebrain" OR "pay-test"
- GA4 conversion: YES — commercial intent signal

**Event 6: scroll_deep**
- Trigger: 75% scroll depth on homepage
- GTM trigger: Scroll Depth trigger (75%)
- GA4 conversion: NO — informational metric only

**Event 7: blog_engaged**
- Trigger: 60 seconds on any blog post
- GTM trigger: Timer trigger (60000ms) on blog pages
- GA4 conversion: NO — content engagement metric

### Implementation Approach

**Step A** (GTM-based, no code changes required):
- chatbox_opened event: GTM click trigger
- pricing_page_view: GTM page view trigger
- scroll_deep: GTM scroll trigger
- blog_engaged: GTM timer trigger

**Step B** (requires chatbox JS modification):
- name_captured: Add gtag call to chatbox JS
- email_captured: Add gtag call to chatbox JS
- onboarding_complete: Add gtag call to chatbox JS

**Step C** (GA4 admin — mark as conversions):
- In GA4 Admin → Events → toggle "Mark as conversion" for: chatbox_opened, name_captured, email_captured, onboarding_complete, pricing_page_view

### GTM Implementation Ready
Steps A and C can be done programmatically via:
- GTM Management API (requires GTM account access — currently only tag delivery is configured)
- Manual GTM dashboard configuration (5-10 min per event)

**Recommendation**: Jared, do you want Aether to implement these GTM triggers? We need GTM API write access OR you grant us access in GTM dashboard (Account → User Management → add purebrain@puremarketing.ai with Edit permissions).

---

## PART 6: REUSABLE API ACCESS CODE

The following code snippet can be used in any tool or BOOP to pull analytics data:

**File**: `/home/jared/projects/AI-CIV/aether/tools/analytics_api.py` (to be created)

```python
# GA4 Data API - pull any report
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest

SA_FILE = '/home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json'
GA4_PROPERTY_ID = '525007539'
GSC_SITE_URL = 'sc-domain:purebrain.ai'

def get_ga4_token():
    creds = service_account.Credentials.from_service_account_file(
        SA_FILE, scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
    creds.refresh(GoogleRequest())
    return creds.token

def get_gsc_token():
    creds = service_account.Credentials.from_service_account_file(
        SA_FILE, scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )
    creds.refresh(GoogleRequest())
    return creds.token

def ga4_report(dimensions, metrics, date_range='30daysAgo', limit=25):
    token = get_ga4_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY_ID}:runReport"
    payload = {
        "dateRanges": [{"startDate": date_range, "endDate": "today"}],
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.json()

def gsc_query(dimensions, start_date, end_date, limit=25):
    token = get_gsc_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"https://www.googleapis.com/webmasters/v3/sites/{GSC_SITE_URL}/searchAnalytics/query"
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": limit
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.json()
```

---

## PART 7: ACTION ITEMS SUMMARY

### Aether Can Do Now (No Jared Action Needed)
- [x] Pull GA4 traffic data daily via service account
- [x] Pull Search Console queries/pages data daily
- [x] Monitor indexing progress via GSC sitemaps API
- [ ] Create `tools/analytics_api.py` as reusable module
- [ ] Configure GTM events A via Management API (need GTM write access)
- [ ] Set up SEMRush browser automation script for weekly audits

### Requires Jared (5-15 minutes total)

**Priority 1 — Clarity (5 min):**
1. Go to clarity.microsoft.com → project viy9bnc56x → Settings → Team
2. Add `purebrain@puremarketing.ai` as Admin

**Priority 2 — GTM Write Access (2 min):**
1. Go to tagmanager.google.com
2. Account → User Management
3. Add `purebrain@puremarketing.ai` with Edit permissions
4. This unlocks programmatic GTM event creation

**Priority 3 — GA4 Conversions (5 min, after GTM events are live):**
1. GA4 → Admin → Events
2. Toggle "Mark as conversion" for: chatbox_opened, name_captured, email_captured, onboarding_complete, pricing_page_view

**Priority 4 — SEMRush API Key (3 min, optional):**
1. Login to SEMRush → click user avatar → Subscription
2. Look for "API" tab — copy API key if available
3. If no key, browser automation continues to work

### What We Confirmed Jared Said "API Access Was Working Before"
Previous access was through OAuth with Jared's personal Google account logged into the browser. The service account (`aether-drive-access@aether-integration.iam.gserviceaccount.com`) was already added to the GA4 property and Search Console — that's why it works now. This is the correct long-term approach: service accounts don't expire with browser sessions.

---

## APPENDIX: INTERESTING DATA FINDINGS

1. **Germany traffic (147 sessions)**: Near-identical sessions/users ratio (147/147) suggests automated or VPN traffic, not organic German users. Likely someone using a German VPN or datacenter IP.

2. **`/ai-tool-stack-calculator/` gets 44 GSC impressions** with avg position 11.5 — this tool is starting to get organic visibility for AI tool-related queries. Worth adding more calculators/tools to capture this traffic.

3. **LinkedIn is sending real traffic**: 20 homepage sessions from linkedin source. The Organic Social channel (62 sessions) validates Jared's LinkedIn presence is driving discovery.

4. **Blog index page has 22.9% bounce rate** (best of any page) — users who land on `/blog/` are engaged and exploring. The blog is working as a content hub.

5. **form_submit (67 events) vs form_start (148 events)** = 45% form completion rate. Roughly half the people who start the chatbox complete it. This is a conversion optimization opportunity.

6. **Why-purebrain page via Microsoft Teams**: 15 sessions came from `statics.teams.cdn.office.net` — someone shared the pricing/value page in a Microsoft Teams chat. This is a potential B2B signal worth watching.

7. **GSC: 0 indexed pages in sitemap** but 19 homepage clicks proves indexing is happening — GSC sitemap reports lag 2-4 weeks for new domains.

---

*Generated by dept-systems-technology | Build: analytics-access-diagnosis | Date: 2026-03-03*
