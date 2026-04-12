# SEMRush Current State Audit - 2026-02-23

**Date**: 2026-02-23
**Agent**: browser-vision-tester
**Type**: operational
**Topic**: SEMRush purebrain.ai current state - site health, position tracking, domain authority

---

## Context

Jared provided SEMRush credentials (support@puremarketing.ai / c2!2gurK:m3T!rc) and asked to check current state of purebrain.ai in SEMRush. Used existing v2 script as base, built updated audit script.

## Findings

### Login
- Still works headlessly with Playwright (no CAPTCHA block)
- Redirects to /home/ after successful login
- Same patterns as before: `wait_until="load"` + `time.sleep(5)` required

### Projects on Account (from dashboard)
5 active projects visible:
1. njdog.com - Site Health 95%, Visibility 17.73%, Traffic 1.1K, Keywords 2.4K, Backlinks 612
2. PMG (puremarketing.ai) - Site Health 92%, Visibility 5.6%, Traffic 25, Keywords 68, Backlinks 924
3. purebrain.ai - Site Health 83%, Visibility 0.08%, Traffic n/a, Keywords n/a, Backlinks 10
4. pureinfluence.ai - Site Health 98%, Visibility 0%, Traffic 6, Keywords 49, Backlinks 539
5. www.shorelinehd.com - Site Health 75%, Visibility 29.78%, Traffic 3.6K, Keywords 2K, Backlinks 30.9K

### purebrain.ai Site Audit
- Configured and RUNNING (last crawled Mon Feb 23, 2026 - today!)
- Crawled 75/100 pages (mobile mode, JS rendering disabled)
- Thematic Reports scores:
  - Crawlability: 93%
  - HTTPS: 100% (excellent)
  - Site Performance: 94%
  - Internal Linking: 85%
  - Markup: 100%
  - Core Web Vitals: 0% (NOT YET SCORED - needs real user data)
  - International SEO: Not implemented (expected - not needed)
  - Robots.txt: No changes
- "Outranking Competitors' SEO" section shows competitors with weaknesses: poor readability, outdated pages, low word count, slow pages - opportunity for purebrain.ai content

### purebrain.ai Position Tracking
- Configured and running
- Keywords: 10 being tracked
- Average Position: 97.30 (very low - not ranking yet)
- Rankings Distribution: Top 100 has 1 keyword
- Top Keywords visible: "purebrain" at pos 73 (0.08% visibility)
- "ai assistant for entrepreneurs" and "ai awakening" also tracked
- All positions N/A or very low - brand new domain

### purebrain.ai Domain Overview
- Authority Score: 0 (no authority yet - brand new)
- Organic Traffic: Nothing found (0 measurable traffic)
- Organic Keywords: n/a
- Backlinks: 10 total
- Referring Domains: 1 (very limited)
- AI Search: 0 visibility, 0 mentions
- Distribution by Country: Worldwide=0, AE=0, AU=0, BR=0

### Backlinks Detail
- Total backlinks: 10
- Referring domains: 1
- Authority Score trend: 0 (flat)
- "Follow backlinks not found" - all 10 are likely nofollow

### Keyword Magic Tool (searched "ai partner for business")
- Tool is functional and returns keyword suggestions
- Relevant keywords visible in results for business AI partnership space

## Recommendations for Jared

1. **Core Web Vitals: 0%** - This needs attention. SEMRush can't score it without real user data. Google PageSpeed Insights should be run to check CWV scores manually.

2. **Internal Linking: 85%** - There are internal linking issues. With 14 blog posts published, we should check what's broken.

3. **Position Tracking setup** - 10 keywords tracked but all at position 97+. Need to verify the RIGHT keywords are being tracked. "Purebrain" at 73 is the only one showing.

4. **0 referring domains with authority** - Link building is next major need. The 10 backlinks are all from 1 domain (likely self-referential or a directory).

5. **Site Health 83%** - Needs investigation. Crawlability at 93% suggests some redirect or access issues.

6. **No organic traffic yet** - Expected for a 3-week-old domain. Content marketing and backlinks are the path forward.

## Script Patterns Updated

```python
# dismiss_cookie helper works well:
def dismiss_cookie(page):
    for txt in ["Allow all", "Accept all", "Accept cookies", "I agree"]:
        btn = page.locator(f'button:has-text("{txt}")').first
        if btn.is_visible(timeout=1500):
            btn.click()
            return

# Navigate to specific tools:
# Site Audit: https://www.semrush.com/siteaudit/
# Position Tracking: https://www.semrush.com/position-tracking/
# Domain Overview: https://www.semrush.com/analytics/overview/?q=purebrain.ai&searchType=domain
# Organic Research: https://www.semrush.com/analytics/organic/overview/?q=purebrain.ai&searchType=domain
# Backlinks: https://www.semrush.com/analytics/backlinks/overview/?q=purebrain.ai&searchType=domain
# Keyword Magic: https://www.semrush.com/analytics/keywordmagic/?q=[keyword]&db=us
```

## Files

- Audit script: `/home/jared/projects/AI-CIV/aether/tools/semrush_audit_2026_02_23.py`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/semrush_audit23_*.png`
- Results JSON: `/home/jared/projects/AI-CIV/aether/exports/screenshots/semrush_audit23_results_20260223_172709.json`

---

**Key Learning**: SEMRush login still works headlessly in Feb 2026. Dashboard now shows "AI Visibility" column (new feature - tracking brand mentions in ChatGPT/AI tools). purebrain.ai has 0 AI visibility which is worth addressing as AI search becomes important.
