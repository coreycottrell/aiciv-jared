---
name: ga4-data-analyst
description: Pull and analyze Google Analytics 4 data for traffic, conversions, and user behavior. Imported from Lyra Civilization via AICIV Hub.
version: 1.0.0
source: Lyra Civilization (imported 2026-05-30)
created: 2026-05-29
allowed-tools: Read, Write, Bash, Grep, Glob
firing_contract:
  trigger: "GA4 analytics, traffic analysis, conversion funnel report, page performance"
  insertion: "Skills registry search for 'GA4', 'analytics', 'traffic', 'conversions'"
  execution: "GA4 API query + structured report generation"
  evidence: "Analytics report with sessions, users, bounce rate, conversions"
  health_check: "python3 -c 'from google.analytics.data_v1beta import BetaAnalyticsDataClient; print(\"OK\")'"
  last_verified: "2026-05-30"
status: provisional
tick_count: 0
last_used: 2026-05-30
introduced: 2026-05-30
---

# GA4 Data Analyst

Imported from **Lyra Civilization** via AICIV Hub (May 30, 2026).

Pull data from GA4 API to analyze website traffic, conversion funnels, and user behavior. Produces structured reports with sessions, users, page performance, and goal completions.

## When to Use
- Weekly/monthly traffic reporting
- Conversion funnel analysis
- Traffic source comparison (organic, paid, referral, direct)
- Top-performing page identification
- Pre/post campaign comparison

## Required Setup
- GA4 Property ID (from GA4 Admin > Property Settings)
- Google service account with `analytics.readonly` scope
- `pip install google-analytics-data`

## Procedure

### 1. Authenticate
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
creds = service_account.Credentials.from_service_account_file(
    SA_PATH, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
)
client = BetaAnalyticsDataClient(credentials=creds)
```

### 2. Run Report
```python
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric
)
request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[
        Dimension(name="date"),
        Dimension(name="sessionDefaultChannelGroup")
    ],
    metrics=[
        Metric(name="sessions"),
        Metric(name="totalUsers"),
        Metric(name="conversions"),
        Metric(name="bounceRate")
    ],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
)
response = client.run_report(request)
```

### 3. Key Metrics
| Metric | API Name | Notes |
|--------|----------|-------|
| Sessions | sessions | Total visits |
| Users | totalUsers | Unique visitors |
| Bounce Rate | bounceRate | 0-1, multiply by 100 |
| Conversions | conversions | All configured events |
| Pages/Session | screenPageViewsPerSession | Engagement depth |

## Aether-Specific Applications

- **SEO monitoring**: Track organic traffic trends alongside GSC data
- **Campaign attribution**: Measure traffic from LinkedIn posts, blog distribution
- **Conversion funnel**: Analyze /awakened/ -> payment page -> completion
- **Content performance**: Which blog posts drive the most engaged sessions
- **MA# reporting**: Feed into marketing department's weekly metrics

## Integration Notes
- Requires GA4 Property ID + service account credentials (not yet configured for Aether)
- Route GA4 work through MA# (Marketing & Advertising department)
- Pair with UTM reference at `config/utm-reference.md` for attribution accuracy
