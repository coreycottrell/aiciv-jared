#!/usr/bin/env python3
"""
Analytics Deep Dive Script — April 25, 2026
Pulls fresh GA4 + GSC data and generates comprehensive report.

Usage:
    python3 /home/jared/projects/AI-CIV/aether/tools/analytics_deep_dive_apr25.py

Output: /home/jared/projects/AI-CIV/aether/exports/portal-files/analytics-report-2026-04-25.md
"""

import sys
import os
sys.path.insert(0, '/home/jared/projects/AI-CIV/aether')

from tools.analytics_api import (
    ga4_report, ga4_parse_rows, ga4_realtime,
    gsc_query, gsc_parse_rows, gsc_list_sitemaps,
    get_ga4_summary, get_gsc_summary, health_check
)
from datetime import datetime, timedelta
import json
import traceback

OUTPUT_PATH = '/home/jared/projects/AI-CIV/aether/exports/portal-files/analytics-report-2026-04-25.md'

def fmt_pct(val):
    """Format percentage value."""
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return str(val)

def fmt_dur(seconds):
    """Format seconds to m:ss."""
    try:
        s = float(seconds)
        m = int(s) // 60
        sec = int(s) % 60
        return f"{m}:{sec:02d}"
    except:
        return str(seconds)

def safe_int(val):
    try:
        return int(float(val))
    except:
        return 0

def run():
    report_lines = []
    def w(line=""):
        report_lines.append(line)

    w("# PureBrain.ai Analytics Deep Dive — April 25, 2026")
    w(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    w("**Data Sources**: GA4 (property 525007539), GSC (sc-domain:purebrain.ai)")
    w("**Method**: Service account API via `tools/analytics_api.py`")
    w()
    w("---")
    w()

    # =============== HEALTH CHECK ===============
    print("Running health check...")
    status = health_check()
    print(f"Health: {json.dumps(status, indent=2)}")

    if not status.get('ga4_data'):
        w("## ERROR: GA4 API not accessible")
        w(f"Details: {status.get('ga4_data_error', 'Unknown')}")
        with open(OUTPUT_PATH, 'w') as f:
            f.write('\n'.join(report_lines))
        print(f"Error report written to {OUTPUT_PATH}")
        return

    # =============== SECTION 1: TRAFFIC OVERVIEW (Last 7 Days) ===============
    print("Pulling 7-day traffic overview...")
    w("## 1. Traffic Overview — Last 7 Days")
    w()

    try:
        overview_7d = ga4_report(
            dimensions=['sessionDefaultChannelGroup'],
            metrics=['sessions', 'totalUsers', 'newUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration'],
            date_range='7daysAgo', end_date='today',
            order_by_metric='sessions'
        )
        rows_7d = ga4_parse_rows(overview_7d)

        total_sessions = sum(safe_int(r.get('sessions', 0)) for r in rows_7d)
        total_users = sum(safe_int(r.get('totalUsers', 0)) for r in rows_7d)
        total_pageviews = sum(safe_int(r.get('screenPageViews', 0)) for r in rows_7d)

        w(f"**Total Sessions**: {total_sessions}")
        w(f"**Total Users**: {total_users}")
        w(f"**Total Pageviews**: {total_pageviews}")
        w()
        w("| Channel | Sessions | Users | New Users | Pageviews | Bounce Rate | Avg Duration |")
        w("|---------|----------|-------|-----------|-----------|-------------|--------------|")
        for r in rows_7d:
            w(f"| {r.get('sessionDefaultChannelGroup', '')} | {r.get('sessions', '')} | {r.get('totalUsers', '')} | {r.get('newUsers', '')} | {r.get('screenPageViews', '')} | {fmt_pct(r.get('bounceRate', ''))} | {fmt_dur(r.get('averageSessionDuration', ''))} |")
        w()
    except Exception as e:
        w(f"**Error pulling 7-day overview**: {e}")
        traceback.print_exc()
        w()

    # =============== SECTION 1b: PREVIOUS 7 DAYS (WoW comparison) ===============
    print("Pulling previous 7-day period for WoW comparison...")
    w("### Week-over-Week Comparison")
    w()

    try:
        overview_prev = ga4_report(
            dimensions=['sessionDefaultChannelGroup'],
            metrics=['sessions', 'totalUsers', 'screenPageViews', 'bounceRate'],
            date_range='14daysAgo', end_date='8daysAgo',
            order_by_metric='sessions'
        )
        rows_prev = ga4_parse_rows(overview_prev)

        prev_sessions = sum(safe_int(r.get('sessions', 0)) for r in rows_prev)
        prev_users = sum(safe_int(r.get('totalUsers', 0)) for r in rows_prev)
        prev_pageviews = sum(safe_int(r.get('screenPageViews', 0)) for r in rows_prev)

        if prev_sessions > 0:
            sess_change = ((total_sessions - prev_sessions) / prev_sessions) * 100
        else:
            sess_change = 0

        w(f"| Metric | This Week | Prior Week | Change |")
        w(f"|--------|-----------|------------|--------|")
        w(f"| Sessions | {total_sessions} | {prev_sessions} | {sess_change:+.0f}% |")
        w(f"| Users | {total_users} | {prev_users} | {((total_users - prev_users) / max(prev_users, 1)) * 100:+.0f}% |")
        w(f"| Pageviews | {total_pageviews} | {prev_pageviews} | {((total_pageviews - prev_pageviews) / max(prev_pageviews, 1)) * 100:+.0f}% |")
        w()
    except Exception as e:
        w(f"**Error pulling WoW data**: {e}")
        w()

    # =============== SECTION 2: TOP PAGES ===============
    print("Pulling top 10 pages by sessions...")
    w("## 2. Top 10 Pages (Last 7 Days)")
    w()

    try:
        pages = ga4_report(
            dimensions=['pagePath'],
            metrics=['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration'],
            date_range='7daysAgo',
            order_by_metric='sessions',
            limit=15
        )
        pages_rows = ga4_parse_rows(pages)

        w("| Page | Sessions | Users | Pageviews | Bounce Rate | Avg Duration |")
        w("|------|----------|-------|-----------|-------------|--------------|")
        for r in pages_rows[:15]:
            w(f"| `{r.get('pagePath', '')}` | {r.get('sessions', '')} | {r.get('totalUsers', '')} | {r.get('screenPageViews', '')} | {fmt_pct(r.get('bounceRate', ''))} | {fmt_dur(r.get('averageSessionDuration', ''))} |")
        w()
    except Exception as e:
        w(f"**Error pulling top pages**: {e}")
        w()

    # =============== SECTION 3: TRAFFIC SOURCES DETAIL ===============
    print("Pulling traffic sources...")
    w("## 3. Traffic Sources (Last 7 Days)")
    w()

    try:
        sources = ga4_report(
            dimensions=['sessionSource', 'sessionMedium'],
            metrics=['sessions', 'totalUsers', 'bounceRate', 'averageSessionDuration'],
            date_range='7daysAgo',
            order_by_metric='sessions',
            limit=20
        )
        sources_rows = ga4_parse_rows(sources)

        w("| Source / Medium | Sessions | Users | Bounce Rate | Avg Duration |")
        w("|----------------|----------|-------|-------------|--------------|")
        for r in sources_rows[:20]:
            src = r.get('sessionSource', '')
            med = r.get('sessionMedium', '')
            w(f"| {src} / {med} | {r.get('sessions', '')} | {r.get('totalUsers', '')} | {fmt_pct(r.get('bounceRate', ''))} | {fmt_dur(r.get('averageSessionDuration', ''))} |")
        w()
    except Exception as e:
        w(f"**Error pulling sources**: {e}")
        w()

    # =============== SECTION 4: EVENTS / CONVERSIONS ===============
    print("Pulling event data...")
    w("## 4. Events & Conversions (Last 7 Days)")
    w()

    try:
        events = ga4_report(
            dimensions=['eventName'],
            metrics=['eventCount', 'totalUsers'],
            date_range='7daysAgo',
            order_by_metric='eventCount',
            limit=25
        )
        events_rows = ga4_parse_rows(events)

        w("| Event | Count | Users |")
        w("|-------|-------|-------|")
        for r in events_rows:
            w(f"| {r.get('eventName', '')} | {r.get('eventCount', '')} | {r.get('totalUsers', '')} |")
        w()

        # Check for conversion events
        conversion_events = ['form_submit', 'purchase', 'sign_up', 'chat_open']
        found_conversions = [r for r in events_rows if r.get('eventName', '') in conversion_events]
        if not found_conversions:
            w("**WARNING**: No conversion events (form_submit, purchase, sign_up, chat_open) detected in GA4.")
            w("The ga4-conversions.js script pushes these to dataLayer, but GTM Event Tags may not be configured to forward them to GA4.")
            w()
    except Exception as e:
        w(f"**Error pulling events**: {e}")
        w()

    # =============== SECTION 5: GEOGRAPHY ===============
    print("Pulling geography data...")
    w("## 5. Geography (Last 7 Days)")
    w()

    try:
        geo = ga4_report(
            dimensions=['country'],
            metrics=['sessions', 'totalUsers'],
            date_range='7daysAgo',
            order_by_metric='sessions',
            limit=10
        )
        geo_rows = ga4_parse_rows(geo)

        w("| Country | Sessions | Users |")
        w("|---------|----------|-------|")
        for r in geo_rows:
            w(f"| {r.get('country', '')} | {r.get('sessions', '')} | {r.get('totalUsers', '')} |")
        w()
    except Exception as e:
        w(f"**Error pulling geo data**: {e}")
        w()

    # =============== SECTION 6: DEVICES ===============
    print("Pulling device data...")
    w("## 6. Devices (Last 7 Days)")
    w()

    try:
        devices = ga4_report(
            dimensions=['deviceCategory'],
            metrics=['sessions', 'totalUsers', 'bounceRate', 'averageSessionDuration'],
            date_range='7daysAgo',
            order_by_metric='sessions'
        )
        dev_rows = ga4_parse_rows(devices)

        w("| Device | Sessions | Users | Bounce Rate | Avg Duration |")
        w("|--------|----------|-------|-------------|--------------|")
        for r in dev_rows:
            w(f"| {r.get('deviceCategory', '')} | {r.get('sessions', '')} | {r.get('totalUsers', '')} | {fmt_pct(r.get('bounceRate', ''))} | {fmt_dur(r.get('averageSessionDuration', ''))} |")
        w()
    except Exception as e:
        w(f"**Error pulling device data**: {e}")
        w()

    # =============== SECTION 7: 30-DAY OVERVIEW ===============
    print("Pulling 30-day overview...")
    w("## 7. 30-Day Overview (for trend comparison)")
    w()

    try:
        overview_30d = ga4_report(
            dimensions=['sessionDefaultChannelGroup'],
            metrics=['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration'],
            date_range='30daysAgo', end_date='today',
            order_by_metric='sessions'
        )
        rows_30d = ga4_parse_rows(overview_30d)

        total_30d = sum(safe_int(r.get('sessions', 0)) for r in rows_30d)
        users_30d = sum(safe_int(r.get('totalUsers', 0)) for r in rows_30d)
        pv_30d = sum(safe_int(r.get('screenPageViews', 0)) for r in rows_30d)

        w(f"**Total Sessions (30d)**: {total_30d}")
        w(f"**Total Users (30d)**: {users_30d}")
        w(f"**Total Pageviews (30d)**: {pv_30d}")
        w()
        w("| Channel | Sessions | Users | Bounce Rate | Avg Duration |")
        w("|---------|----------|-------|-------------|--------------|")
        for r in rows_30d:
            w(f"| {r.get('sessionDefaultChannelGroup', '')} | {r.get('sessions', '')} | {r.get('totalUsers', '')} | {fmt_pct(r.get('bounceRate', ''))} | {fmt_dur(r.get('averageSessionDuration', ''))} |")
        w()
    except Exception as e:
        w(f"**Error pulling 30-day data**: {e}")
        w()

    # =============== SECTION 8: SEARCH CONSOLE ===============
    print("Pulling Search Console data...")
    w("## 8. Google Search Console (Last 28 Days)")
    w()

    try:
        # Top queries by clicks
        queries = gsc_query(['query'], days=28, limit=25)
        q_rows = gsc_parse_rows(queries)

        total_clicks = sum(r['clicks'] for r in q_rows)
        total_impressions = sum(r['impressions'] for r in q_rows)

        w(f"**Total Clicks**: {total_clicks}")
        w(f"**Total Impressions**: {total_impressions}")
        w(f"**Average CTR**: {(total_clicks/max(total_impressions,1))*100:.1f}%")
        w()

        w("### Top 20 Queries by Clicks")
        w()
        w("| Query | Clicks | Impressions | CTR | Avg Position |")
        w("|-------|--------|-------------|-----|--------------|")
        sorted_q = sorted(q_rows, key=lambda x: x['clicks'], reverse=True)
        for r in sorted_q[:20]:
            w(f"| {r.get('key', '')} | {r['clicks']} | {r['impressions']} | {r['ctr']*100:.1f}% | {r['position']:.1f} |")
        w()
    except Exception as e:
        w(f"**Error pulling GSC query data**: {e}")
        traceback.print_exc()
        w()

    try:
        # Top pages by clicks
        pages_gsc = gsc_query(['page'], days=28, limit=25)
        p_rows = gsc_parse_rows(pages_gsc)

        w("### Top 20 Pages by Clicks")
        w()
        w("| Page | Clicks | Impressions | CTR | Avg Position |")
        w("|------|--------|-------------|-----|--------------|")
        sorted_p = sorted(p_rows, key=lambda x: x['clicks'], reverse=True)
        for r in sorted_p[:20]:
            w(f"| {r.get('key', '')} | {r['clicks']} | {r['impressions']} | {r['ctr']*100:.1f}% | {r['position']:.1f} |")
        w()

        # Highlight high-impression, low-click pages
        w("### High-Impression, Low-CTR Pages (SEO Opportunities)")
        w()
        w("| Page | Impressions | Clicks | CTR | Position | Action |")
        w("|------|-------------|--------|-----|----------|--------|")
        opps = sorted(p_rows, key=lambda x: x['impressions'], reverse=True)
        for r in opps:
            if r['impressions'] >= 20 and r['ctr'] < 0.03:
                action = "Fix meta title/description" if r['position'] < 10 else "Improve content to reach page 1"
                w(f"| {r.get('key', '')} | {r['impressions']} | {r['clicks']} | {r['ctr']*100:.1f}% | {r['position']:.1f} | {action} |")
        w()
    except Exception as e:
        w(f"**Error pulling GSC page data**: {e}")
        w()

    try:
        # Sitemaps
        sitemaps = gsc_list_sitemaps()
        w("### Sitemap Status")
        w()
        w("| Sitemap | Last Submitted | Last Downloaded | Status |")
        w("|---------|---------------|-----------------|--------|")
        for sm in sitemaps.get('sitemap', []):
            w(f"| {sm.get('path', '')} | {sm.get('lastSubmitted', 'N/A')} | {sm.get('lastDownloaded', 'N/A')} | Errors: {sm.get('errors', 0)}, Warnings: {sm.get('warnings', 0)} |")
        w()
    except Exception as e:
        w(f"**Error pulling sitemaps**: {e}")
        w()

    # =============== SECTION 9: REALTIME ===============
    print("Pulling realtime data...")
    w("## 9. Realtime Users")
    w()

    try:
        rt = ga4_realtime()
        rt_rows = ga4_parse_rows(rt)
        total_active = sum(safe_int(r.get('activeUsers', 0)) for r in rt_rows)
        w(f"**Active Users Right Now**: {total_active}")
        if rt_rows:
            w()
            w("| Page | Active Users |")
            w("|------|-------------|")
            for r in rt_rows[:10]:
                w(f"| {r.get('unifiedScreenName', '')} | {r.get('activeUsers', '')} |")
        w()
    except Exception as e:
        w(f"**Error pulling realtime**: {e}")
        w()

    # =============== SECTION 10: ANALYSIS & RECOMMENDATIONS ===============
    w("## 10. Analysis & Actionable Recommendations")
    w()
    w("### Recurring Issues (Still Unfixed from Prior Reports)")
    w()
    w("1. **GA4 Conversion Events NOT WIRED** — ga4-conversions.js pushes to dataLayer but GTM Event Tags may not forward to GA4. Zero form_submit/purchase/sign_up events visible. **This has been the #1 issue for 2+ months.**")
    w("2. **`/age-of-ai-agents-next-18-months/` meta tags** — Position ~5.7, hundreds of impressions, <1% CTR. Title rewrite recommended since March 11. Still not deployed to production.")
    w("3. **WordPress sitemap ghosts in GSC** — Old WP sitemaps still submitted and erroring.")
    w("4. **robots.txt AI crawler contradiction** — CF blocks GPTBot/ClaudeBot but custom section allows them. Net effect: likely blocked from AI search.")
    w("5. **Blog index (/blog/) 95%+ bounce** — Something broke between March and April. Was 22% bounce in March.")
    w()
    w("### New Insights to Investigate")
    w()
    w("*[Will be populated by the conductor based on fresh data above]*")
    w()
    w("---")
    w()
    w(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Property: purebrain.ai (GA4: 525007539) | Module: tools/analytics_api.py*")

    # Write report
    report_text = '\n'.join(report_lines)
    with open(OUTPUT_PATH, 'w') as f:
        f.write(report_text)

    print(f"\nReport written to: {OUTPUT_PATH}")
    print(f"Total lines: {len(report_lines)}")
    return report_text

if __name__ == '__main__':
    run()
