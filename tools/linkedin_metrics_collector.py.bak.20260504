#!/usr/bin/env python3
"""
LinkedIn Metrics Collector
==========================
Collects post performance metrics from LinkedIn analytics via PureSurf
and logs them back to the LinkedIn Domination tracking spreadsheet.

USAGE:
    # Collect metrics for a specific post
    python3 tools/linkedin_metrics_collector.py --post-url "https://linkedin.com/posts/..." --row 5

    # Collect metrics for ALL posts missing metrics (weekly Monday job)
    python3 tools/linkedin_metrics_collector.py --collect-all

    # Dry run - show what would be collected
    python3 tools/linkedin_metrics_collector.py --collect-all --dry-run

SPREADSHEET:
    ID: 1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4
    Tab: "Linkedin Post Content Calendar"
    Metrics columns: Q (Views), R (Reach), S (Profile Views), T (Followers Gained),
                     U (Reactions), V (Comments), W (Reposts), X (Saves),
                     Y (Sends), Z (Clicks), AA (Engagement Rate - auto-calc)

PURESURF:
    URL: http://surf.purebrain.ai (157.180.69.225:8901)
    Profile: jared-linkedin-fresh (residential proxy, authenticated session)

AUTOMATION:
    Scheduled as weekly BOOP task (Mondays) — collects metrics for all
    posts from the previous week that have LinkedIn URLs but missing metrics.

Author: dept-systems-technology
Date: 2026-04-04
"""

import argparse
import json
import os
import sys
import time
import re
import random
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'linkedin_metrics.log'

SHEET_ID = '1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4'
SHEET_TAB = 'Linkedin Post Content Calendar'

# PureSurf config
PURESURF_URL = 'http://157.180.69.225:8901'
PURESURF_PROFILE = 'jared-linkedin-fresh'
PURESURF_API_KEY = 'O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg'  # Aether key (owns jared-linkedin-fresh profile)

# Backfill delay between individual post navigations (seconds)
BACKFILL_DELAY_MIN = 30
BACKFILL_DELAY_MAX = 60

# Column mapping (0-indexed in API, but we use A1 notation for reads/writes)
# Updated 2026-04-07: Jared reorganized the spreadsheet header.
# Old mapping was H-S, new mapping is Q-AA per the current header row.
METRIC_COLUMNS = {
    'views': 'Q',
    'reach': 'R',
    'profile_views': 'S',
    'followers_gained': 'T',
    'reactions': 'U',
    'comments': 'V',
    'reposts': 'W',
    'saves': 'X',
    'sends': 'Y',
    'clicks': 'Z',
    # 'engagement_rate': 'AA',  # Auto-calculated by spreadsheet formula - do NOT overwrite
}

# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [linkedin_metrics] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ── Google Sheets Auth ─────────────────────────────────────────────────────────

def get_sheets_service():
    """Get authenticated Google Sheets service using OAuth2."""
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_path = ROOT / '.credentials' / 'oauth-token.json'
    with open(token_path) as f:
        token_data = json.load(f)

    creds = OAuthCredentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes')
    )
    if creds.expired:
        creds.refresh(Request())
        # Save refreshed token
        with open(token_path, 'w') as f:
            json.dump({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': list(creds.scopes) if creds.scopes else [],
            }, f, indent=2)

    return build('sheets', 'v4', credentials=creds)


# ── Spreadsheet Operations ─────────────────────────────────────────────────────

def read_all_posts(sheets_service) -> List[Dict]:
    """Read all posts from the spreadsheet and return as list of dicts."""
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f'{SHEET_TAB}!A1:AA200'
    ).execute()

    values = result.get('values', [])
    if not values:
        return []

    header = values[0]
    posts = []
    for i, row in enumerate(values[1:], start=2):
        # Pad row to header length
        row_padded = row + [''] * (len(header) - len(row))
        post = {header[j]: row_padded[j] for j in range(len(header))}
        post['_row'] = i  # 1-indexed row number in sheet
        posts.append(post)

    return posts


def get_posts_needing_metrics(posts: List[Dict]) -> List[Dict]:
    """Filter posts that have a LinkedIn URL but are missing metrics."""
    needing = []
    for post in posts:
        # Check both 'Link' and 'LinkedIn URL' columns for the post URL
        link = post.get('LinkedIn URL', '').strip() or post.get('Link', '').strip()
        views = post.get('Views', '').strip()
        status = post.get('Status', '').strip()

        # Also handle old-format rows where Status might be in 'Post Text' column
        # due to header misalignment with legacy data
        if not status:
            status = post.get('Post Text', '').strip()

        # Must be Live, have a linkedin link, and be missing views
        if status == 'Live' and link and 'linkedin.com' in link and not views:
            # Store the resolved LinkedIn URL for downstream use
            post['_linkedin_url'] = link
            needing.append(post)

    return needing


def write_metrics_to_sheet(sheets_service, row: int, metrics: Dict[str, str]):
    """Write collected metrics to the spreadsheet for a given row."""
    updates = []
    for metric_key, col_letter in METRIC_COLUMNS.items():
        value = metrics.get(metric_key, '')
        if value:
            updates.append({
                'range': f'{SHEET_TAB}!{col_letter}{row}',
                'values': [[value]]
            })

    if updates:
        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
        ).execute()
        logger.info(f"Written metrics to row {row}: {metrics}")


# ── PureSurf API Helpers ────────────────────────────────────────────────────────

def puresurf_request(method: str, path: str, data: dict = None, timeout: int = 30) -> dict:
    """Make an authenticated request to PureSurf API."""
    url = f"{PURESURF_URL}{path}"
    headers = {
        "X-API-Key": PURESURF_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data or {}, timeout=timeout)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unknown method: {method}")

        if resp.status_code >= 400:
            logger.error(f"PureSurf {method} {path} -> {resp.status_code}: {resp.text[:200]}")
            return {"error": True, "status": resp.status_code, "message": resp.text[:200]}

        return resp.json()
    except requests.exceptions.Timeout:
        logger.error(f"PureSurf {method} {path} -> timeout ({timeout}s)")
        return {"error": True, "message": "timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"PureSurf {method} {path} -> connection refused")
        return {"error": True, "message": "connection_refused"}
    except Exception as e:
        logger.error(f"PureSurf {method} {path} -> {e}")
        return {"error": True, "message": str(e)}


def create_session() -> Optional[str]:
    """Create a single PureSurf session with Jared's LinkedIn profile."""
    logger.info(f"Creating PureSurf session with {PURESURF_PROFILE} profile...")
    result = puresurf_request("POST", "/sessions", {
        "profile_name": PURESURF_PROFILE,
        "proxy_provider": "residential",
        "device_profile": "macbook",
    }, timeout=60)

    if result.get("error"):
        logger.error(f"Failed to create session: {result}")
        return None

    session_id = result.get("session_id")
    if not session_id:
        logger.error(f"No session_id in response: {result}")
        return None

    logger.info(f"Session created: {session_id}")
    return session_id


def close_session(session_id: str):
    """Close a PureSurf session (saves cookies)."""
    logger.info(f"Closing session {session_id}")
    puresurf_request("DELETE", f"/sessions/{session_id}", timeout=15)


def navigate_session(session_id: str, url: str, wait_seconds: int = 5, max_retries: int = 3) -> dict:
    """Navigate to a URL within an existing session. Handles PureSurf rate limiting automatically."""
    logger.info(f"Navigating to {url[:100]}")
    for attempt in range(max_retries):
        result = puresurf_request("POST", f"/sessions/{session_id}/navigate", {
            "url": url,
            "wait_after": wait_seconds,
        }, timeout=60)

        # Handle proactive rate limiting
        if isinstance(result, dict) and result.get("status") == "proactive_rate_limited":
            retry_after = result.get("retry_after", 10)
            logger.info(f"Rate limited, waiting {retry_after + 1}s before retry ({attempt+1}/{max_retries})...")
            time.sleep(retry_after + 1)
            continue

        return result

    logger.error(f"Navigation failed after {max_retries} retries (rate limited)")
    return {"error": True, "message": "rate_limited_exhausted"}


def execute_js(session_id: str, script: str) -> dict:
    """Execute JavaScript in the page context via PureSurf evaluate endpoint."""
    return puresurf_request("POST", f"/sessions/{session_id}/evaluate", {
        "script": script,
    }, timeout=30)


def take_screenshot(session_id: str) -> dict:
    """Take a screenshot for debugging."""
    return puresurf_request("POST", f"/sessions/{session_id}/screenshot", timeout=30)


def verify_linkedin_login(session_id: str) -> bool:
    """Navigate to LinkedIn feed and verify we're logged in. Returns True if logged in."""
    logger.info("Verifying LinkedIn login status...")

    nav_result = navigate_session(session_id, "https://www.linkedin.com/feed/", wait_seconds=8)
    if nav_result.get("error"):
        logger.error(f"Navigation to feed failed: {nav_result}")
        return False

    check_js = """
    (() => {
        const isLogin = document.querySelector('[data-test-id="sign-in-btn"]')
            || document.title.toLowerCase().includes('login')
            || document.title.toLowerCase().includes('sign in')
            || document.querySelector('input[name="session_key"]');
        const hasFeed = document.querySelector('.feed-shared-update-v2')
            || document.querySelector('[data-view-name="feed-card"]')
            || document.querySelector('.scaffold-layout__main');
        return JSON.stringify({
            logged_in: !isLogin && hasFeed,
            title: document.title,
            url: window.location.href
        });
    })()
    """

    result = execute_js(session_id, check_js)
    if result.get("error"):
        logger.warning(f"Login check failed: {result}")
        return False

    raw = result.get('result', '{}')
    data = json.loads(raw) if isinstance(raw, str) else raw
    logged_in = data.get('logged_in', False)
    logger.info(f"Login status: {'logged in' if logged_in else 'NOT logged in'} (page: {data.get('title', '?')})")

    if not logged_in:
        logger.error(
            "LinkedIn session is NOT logged in. The cookies for jared-linkedin-fresh may have expired. "
            "Please run the comment scheduler or manually log in via PureSurf to refresh cookies, "
            "then retry the metrics collector."
        )

    return logged_in


# ── PureSurf Metrics Scraping ──────────────────────────────────────────────────

def collect_metrics_via_puresurf(session_id: str, post_url: str) -> Optional[Dict[str, str]]:
    """
    Use an existing PureSurf session to navigate to a LinkedIn post and scrape its analytics.
    Returns dict with keys matching METRIC_COLUMNS or None on failure.
    """
    try:
        # Navigate to the post
        logger.info(f"Navigating to post: {post_url}")
        nav_result = navigate_session(session_id, post_url, wait_seconds=8)

        if nav_result.get("error"):
            logger.error(f"Navigation failed: {nav_result}")
            return None

        time.sleep(3)  # Extra wait for dynamic content

        # Extract metrics from the post page via JS
        js_extract = """
        (() => {
            const metrics = {};

            // Try to find the social counts bar
            const socialCounts = document.querySelector('.social-details-social-counts');
            if (socialCounts) {
                const reactionsEl = socialCounts.querySelector('.social-details-social-counts__reactions-count');
                if (reactionsEl) metrics.reactions = reactionsEl.textContent.trim();

                const commentsEl = socialCounts.querySelector('[data-test-id="social-actions__comments"]') ||
                                   socialCounts.querySelector('.social-details-social-counts__comments');
                if (commentsEl) metrics.comments = commentsEl.textContent.trim().replace(/[^0-9]/g, '');

                const repostsEl = socialCounts.querySelector('.social-details-social-counts__reposts') ||
                                  socialCounts.querySelector('[data-test-id="social-actions__reposts"]');
                if (repostsEl) metrics.reposts = repostsEl.textContent.trim().replace(/[^0-9]/g, '');
            }

            // Try analytics section (visible to post author)
            const analyticsSection = document.querySelector('.feed-shared-analytics');
            if (analyticsSection) {
                const items = analyticsSection.querySelectorAll('.analytics-entry-point');
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    const num = item.querySelector('.analytics-entry-point__value, .t-bold');
                    const value = num ? num.textContent.trim().replace(/,/g, '') : '';

                    if (text.includes('impression') || text.includes('view')) metrics.views = value;
                    if (text.includes('reaction')) metrics.reactions = value || metrics.reactions;
                    if (text.includes('comment')) metrics.comments = value || metrics.comments;
                    if (text.includes('repost')) metrics.reposts = value || metrics.reposts;
                });
            }

            // Alternative: check for the "X impressions" text
            const allText = document.body.innerText;
            const impressionMatch = allText.match(/([\d,]+)\\s*impressions?/i);
            if (impressionMatch && !metrics.views) {
                metrics.views = impressionMatch[1].replace(/,/g, '');
            }

            return JSON.stringify(metrics);
        })()
        """

        eval_result = execute_js(session_id, js_extract)

        if eval_result.get("error"):
            logger.error(f"JS evaluation failed: {eval_result}")
            return None

        raw = eval_result.get('result', '{}')
        if isinstance(raw, str):
            metrics = json.loads(raw)
        else:
            metrics = raw
        logger.info(f"Extracted metrics: {metrics}")
        return metrics if metrics else None

    except Exception as e:
        logger.error(f"PureSurf collection failed: {e}")
        return None


def collect_analytics_page_metrics(session_id: str) -> Optional[Dict[str, Dict]]:
    """
    Navigate to LinkedIn creator analytics page and scrape all post metrics at once.
    Uses past_365_days to cover all posts in one page load.
    Returns dict keyed by post URL with metric values, or None on failure.
    """
    try:
        analytics_url = 'https://www.linkedin.com/analytics/creator/content/?metricType=IMPRESSIONS&timeRange=past_365_days'

        logger.info("Navigating to LinkedIn creator analytics (past 365 days)...")
        nav_result = navigate_session(session_id, analytics_url, wait_seconds=10)

        if nav_result.get("error"):
            logger.error(f"Analytics page navigation failed: {nav_result}")
            return None

        time.sleep(5)  # Wait for the analytics page to fully load

        # Scroll down to load all posts (LinkedIn lazy-loads content)
        scroll_js = """
        (async () => {
            let lastHeight = 0;
            let scrollAttempts = 0;
            while (scrollAttempts < 10) {
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(r => setTimeout(r, 2000));
                const newHeight = document.body.scrollHeight;
                if (newHeight === lastHeight) break;
                lastHeight = newHeight;
                scrollAttempts++;
            }
            return JSON.stringify({scrolled: scrollAttempts, height: lastHeight});
        })()
        """
        scroll_result = execute_js(session_id, scroll_js)
        logger.info(f"Scroll result: {scroll_result.get('result', 'unknown')}")

        time.sleep(3)  # Final settle after scrolling

        # Extract all post rows from analytics table/cards
        js_extract = """
        (() => {
            const results = {};

            // Strategy 1: Table rows
            const rows = document.querySelectorAll('table tbody tr, .content-analytics-table tbody tr, .analytics-content-table-row');
            rows.forEach(row => {
                const linkEl = row.querySelector('a[href*="/posts/"], a[href*="/pulse/"], a[href*="activity"]');
                const cells = row.querySelectorAll('td');
                if (linkEl && cells.length >= 3) {
                    const url = linkEl.href;
                    const metrics = {};
                    if (cells[1]) metrics.views = cells[1].textContent.trim().replace(/,/g, '');
                    if (cells[2]) metrics.reactions = cells[2].textContent.trim().replace(/,/g, '');
                    if (cells[3]) metrics.comments = cells[3].textContent.trim().replace(/,/g, '');
                    if (cells[4]) metrics.reposts = cells[4].textContent.trim().replace(/,/g, '');
                    results[url] = metrics;
                }
            });

            // Strategy 2: Card-based layout (newer LinkedIn analytics UI)
            if (Object.keys(results).length === 0) {
                const cards = document.querySelectorAll('[class*="content-analytics"] [class*="card"], [class*="analytics-content"] li, [class*="content-table"] [class*="row"]');
                cards.forEach(card => {
                    const linkEl = card.querySelector('a[href*="/posts/"], a[href*="/pulse/"], a[href*="activity"]');
                    if (!linkEl) return;
                    const url = linkEl.href;
                    const text = card.textContent;
                    const metrics = {};

                    // Try to extract numbers from the card text
                    const nums = text.match(/([\d,]+)/g) || [];
                    if (nums.length >= 1) metrics.views = nums[0].replace(/,/g, '');
                    if (nums.length >= 2) metrics.reactions = nums[1].replace(/,/g, '');
                    if (nums.length >= 3) metrics.comments = nums[2].replace(/,/g, '');
                    if (nums.length >= 4) metrics.reposts = nums[3].replace(/,/g, '');
                    results[url] = metrics;
                });
            }

            // Strategy 3: Get all links and nearby numbers as fallback
            if (Object.keys(results).length === 0) {
                const allLinks = document.querySelectorAll('a[href*="/posts/"], a[href*="activity-"]');
                allLinks.forEach(link => {
                    const url = link.href;
                    const parent = link.closest('tr, li, [class*="row"], [class*="card"]') || link.parentElement;
                    if (parent) {
                        const text = parent.textContent;
                        const nums = text.match(/([\d,]+)/g) || [];
                        const metrics = {};
                        if (nums.length >= 1) metrics.views = nums[0].replace(/,/g, '');
                        if (nums.length >= 2) metrics.reactions = nums[1].replace(/,/g, '');
                        results[url] = metrics;
                    }
                });
            }

            // Also capture the page title and any debug info
            const debug = {
                url: window.location.href,
                title: document.title,
                postCount: Object.keys(results).length,
                bodyLength: document.body.innerText.length,
            };

            return JSON.stringify({posts: results, debug: debug});
        })()
        """

        eval_result = execute_js(session_id, js_extract)

        if eval_result.get("error"):
            logger.error(f"Analytics extraction failed: {eval_result}")
            return None

        raw = eval_result.get('result', '{}')
        data = json.loads(raw) if isinstance(raw, str) else raw

        debug_info = data.get('debug', {})
        posts_data = data.get('posts', {})
        logger.info(f"Analytics page: found metrics for {len(posts_data)} posts (page: {debug_info.get('title', '?')}, body length: {debug_info.get('bodyLength', 0)})")

        if not posts_data:
            # Dump page text for debugging
            text_js = "document.body.innerText.substring(0, 3000)"
            text_result = execute_js(session_id, text_js)
            logger.warning(f"Analytics page text preview: {str(text_result.get('result', ''))[:500]}")

        return posts_data if posts_data else None

    except Exception as e:
        logger.error(f"Analytics page collection failed: {e}")
        return None


# ── URL Matching ───────────────────────────────────────────────────────────────

def normalize_linkedin_url(url: str) -> str:
    """Normalize a LinkedIn post URL for comparison (strip UTM params, etc.)."""
    # Extract the activity ID which is the stable identifier
    match = re.search(r'activity-(\d+)', url)
    if match:
        return match.group(1)
    return url.strip().rstrip('/')


def match_analytics_to_posts(analytics: Dict, posts: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """Match analytics data to spreadsheet posts by URL."""
    matches = []
    for post in posts:
        post_url = post.get('Link', '').strip()
        if not post_url:
            continue

        post_activity = normalize_linkedin_url(post_url)

        for analytics_url, metrics in analytics.items():
            analytics_activity = normalize_linkedin_url(analytics_url)
            if post_activity == analytics_activity:
                matches.append((post, metrics))
                break

    return matches


# ── Main Collection Logic ──────────────────────────────────────────────────────

def collect_single_post(post_url: str, row: int, dry_run: bool = False):
    """Collect metrics for a single post and write to spreadsheet."""
    logger.info(f"Collecting metrics for row {row}: {post_url[:80]}...")

    session_id = create_session()
    if not session_id:
        logger.error("Failed to create PureSurf session")
        return False

    try:
        if not verify_linkedin_login(session_id):
            logger.error("Cannot collect metrics - not logged into LinkedIn. Aborting.")
            return False

        # Wait for rate limit between login check navigation and post navigation
        time.sleep(15)

        metrics = collect_metrics_via_puresurf(session_id, post_url)
        if not metrics:
            logger.warning(f"No metrics collected for row {row}")
            return False

        if dry_run:
            logger.info(f"[DRY RUN] Would write to row {row}: {metrics}")
            return True

        sheets = get_sheets_service()
        write_metrics_to_sheet(sheets, row, metrics)
        return True
    finally:
        close_session(session_id)


def collect_all_missing(dry_run: bool = False):
    """Collect metrics for all posts that are missing them. Uses ONE session for all posts."""
    logger.info("Starting bulk metrics collection...")

    sheets = get_sheets_service()
    posts = read_all_posts(sheets)
    needing = get_posts_needing_metrics(posts)

    logger.info(f"Total posts: {len(posts)}, needing metrics: {len(needing)}")

    if not needing:
        logger.info("No posts need metrics collection.")
        return

    # Create ONE session and reuse it for everything
    session_id = create_session()
    if not session_id:
        logger.error("Failed to create PureSurf session - aborting collection")
        return

    collected = 0

    try:
        # Verify we're logged in before attempting anything
        if not verify_linkedin_login(session_id):
            logger.error("Cannot collect metrics - not logged into LinkedIn. Aborting.")
            return

        # Strategy 1: Try analytics page first (bulk collection - one page load for all posts)
        logger.info("Attempting bulk collection from LinkedIn creator analytics page...")
        analytics = collect_analytics_page_metrics(session_id)

        if analytics:
            matches = match_analytics_to_posts(analytics, needing)
            logger.info(f"Matched {len(matches)} posts from analytics page")

            for post, metrics in matches:
                row = post['_row']
                if dry_run:
                    logger.info(f"[DRY RUN] Row {row} ({post.get('Post ID', '?')}): {metrics}")
                else:
                    write_metrics_to_sheet(sheets, row, metrics)
                collected += 1
                needing = [p for p in needing if p['_row'] != row]

        # Strategy 2: Visit individual posts for any remaining (SLOW - 30-60s gaps)
        if needing:
            logger.info(f"Falling back to individual collection for {len(needing)} remaining posts...")
            logger.info(f"Using {BACKFILL_DELAY_MIN}-{BACKFILL_DELAY_MAX}s delays between navigations to avoid rate limits")

            for i, post in enumerate(needing):
                row = post['_row']
                url = post.get('Link', '')
                if not url:
                    continue

                metrics = collect_metrics_via_puresurf(session_id, url)
                if metrics:
                    if dry_run:
                        logger.info(f"[DRY RUN] Row {row} ({post.get('Post ID', '?')}): {metrics}")
                    else:
                        write_metrics_to_sheet(sheets, row, metrics)
                    collected += 1

                # Slow backfill: random delay between 30-60 seconds
                if i < len(needing) - 1:  # Don't delay after the last post
                    delay = random.randint(BACKFILL_DELAY_MIN, BACKFILL_DELAY_MAX)
                    logger.info(f"Waiting {delay}s before next post ({i+1}/{len(needing)} done)...")
                    time.sleep(delay)

    finally:
        close_session(session_id)

    logger.info(f"Collection complete: {collected} posts updated")


def weekly_monday_collection():
    """
    Weekly Monday BOOP task entry point.
    Collects metrics for all posts from the previous week.
    """
    logger.info("=== WEEKLY MONDAY METRICS COLLECTION ===")
    collect_all_missing(dry_run=False)
    logger.info("=== WEEKLY COLLECTION COMPLETE ===")


# ── CLI Entry Point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='LinkedIn Metrics Collector — scrapes post analytics via PureSurf'
    )
    parser.add_argument('--post-url', type=str, help='LinkedIn post URL to collect metrics for')
    parser.add_argument('--row', type=int, help='Spreadsheet row number (1-indexed)')
    parser.add_argument('--collect-all', action='store_true', help='Collect metrics for all posts missing data')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be collected without writing')
    parser.add_argument('--weekly', action='store_true', help='Run weekly Monday collection (BOOP entry)')

    args = parser.parse_args()

    if args.weekly:
        weekly_monday_collection()
    elif args.collect_all:
        collect_all_missing(dry_run=args.dry_run)
    elif args.post_url and args.row:
        collect_single_post(args.post_url, args.row, dry_run=args.dry_run)
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python3 tools/linkedin_metrics_collector.py --collect-all --dry-run')
        print('  python3 tools/linkedin_metrics_collector.py --post-url "https://linkedin.com/posts/..." --row 5')
        print('  python3 tools/linkedin_metrics_collector.py --weekly')


if __name__ == '__main__':
    main()
