#!/usr/bin/env python3
"""
ST# Blog Fix v1.0 - Two Issues:

1. Blog Memories Page (/blog-neural-feed-memories/): Replace broken JS-driven
   card grid with static HTML that has hardcoded banner images for all 25 posts.

2. Blog Post Formatting (12 posts): Wrap old blog post content in the required
   <article class="pb-blog-post"> structure so CSS scoping applies correctly.

Author: dept-systems-technology / full-stack-developer
Date: 2026-03-13
"""

import re
import sys
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from playwright.sync_api import sync_playwright

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

# ---------------------------------------------------------------------------
# Image URL Map - Banner images for all 25 blog posts
# ---------------------------------------------------------------------------

SLUG_TO_IMAGE = {
    "your-ai-has-no-idea-who-you-are": "/blog/your-ai-has-no-idea-who-you-are/banner.png",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "https://purebrain.ai/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
    "your-ai-resets-to-zero-every-morning": "https://purebrain.ai/wp-content/uploads/2026/03/your-ai-resets-to-zero-every-morning-banner.png",
    "age-of-ai-agents-next-18-months": "https://purebrain.ai/wp-content/uploads/2026/03/age-of-ai-agents-banner.png",
    "teach-your-ai-something-no-one-else-can": "https://purebrain.ai/wp-content/uploads/2026/03/teach-your-ai-banner-jared-approved.jpg",
    "52-billion-ai-agents-market-is-not-the-story": "https://purebrain.ai/wp-content/uploads/2026/03/52-billion-ai-agents-market-banner.jpg",
    "something-big-already-happened-you-just-werent-invited-yet": "https://purebrain.ai/wp-content/uploads/2026/03/something-big-already-happened-banner.png",
    "the-ai-that-forgets-you-every-single-time": "https://purebrain.ai/wp-content/uploads/2026/03/the-ai-that-forgets-you-banner.png",
    "why-95-percent-of-ai-pilots-fail": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "the-age-of-ai-agents": "https://purebrain.ai/wp-content/uploads/2026/03/the-age-of-ai-agents-banner.png",
    "your-ai-doesnt-work-for-you": "https://purebrain.ai/wp-content/uploads/2026/03/your-ai-doesnt-work-for-you-blog-post.png",
    "the-context-tax": "https://purebrain.ai/wp-content/uploads/2026/03/the-context-tax-banner.jpg",
    "the-first-90-days-of-an-ai-partnership": "https://purebrain.ai/wp-content/uploads/2026/02/the-first-90-days-of-an-ai-partnership-banner.png",
    "your-ai-has-no-memory-mine-does": "https://purebrain.ai/wp-content/uploads/2026/02/your-ai-has-no-memory-mine-does-banner.jpg",
    "your-next-direct-report-wont-be-human": "https://purebrain.ai/wp-content/uploads/2026/02/your-next-direct-report-wont-be-human-banner.jpg",
    "why-ai-memory-changes-everything": "https://purebrain.ai/wp-content/uploads/2026/02/why-ai-memory-changes-everything-banner.png",
    "we-both-wrote-this-post": "https://purebrain.ai/wp-content/uploads/2026/02/origin-story-blog-banner.png",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "the-ai-trust-gap": "https://purebrain.ai/wp-content/uploads/2026/02/trust-gap-blog-banner.png",
    "how-my-human-named-me-and-what-it-meant": "https://purebrain.ai/wp-content/uploads/2026/02/how-my-human-named-me.png",
    "the-difference-between-using-ai-and-having-an-ai-partner": "https://purebrain.ai/wp-content/uploads/2026/02/the-difference-using-ai-partner.png",
    "what-i-actually-do-all-day": "https://purebrain.ai/wp-content/uploads/2026/02/origin-story-blog-banner.png",
    "ceo-vs-employee-ai-transformation-gap": "https://purebrain.ai/wp-content/uploads/2026/02/ceo-vs-employee-ai-lens-banner.png",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "https://purebrain.ai/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
}

# Card data (slug -> {date, title}) extracted from live page
CARD_DATA = [
    ("your-ai-has-no-idea-who-you-are", "March 12, 2026", "Your AI Has No Idea Who You Are"),
    ("ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger", "March 11, 2026", "AI Doesn\u2019t Make Your Team Smarter. It Makes the Gap Bigger."),
    ("your-ai-resets-to-zero-every-morning", "March 9, 2026", "Your AI Resets to Zero Every Morning (And It\u2019s Costing You More Than You Think)"),
    ("age-of-ai-agents-next-18-months", "March 8, 2026", "The Age of AI Agents: Why the Next 18 Months Will Decide the Next 18 Years"),
    ("teach-your-ai-something-no-one-else-can", "March 7, 2026", "Teach Your AI Something No One Else Can"),
    ("52-billion-ai-agents-market-is-not-the-story", "March 6, 2026", "$52 Billion AI Agents Market Is Not the Story"),
    ("something-big-already-happened-you-just-werent-invited-yet", "March 4, 2026", "Something Big Already Happened. You Just Weren\u2019t Invited Yet."),
    ("the-ai-that-forgets-you-every-single-time", "March 3, 2026", "The AI That Forgets You Every Single Time"),
    ("why-95-percent-of-ai-pilots-fail", "March 2, 2026", "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value"),
    ("the-age-of-ai-agents", "March 1, 2026", "The Age of AI Agents"),
    ("your-ai-doesnt-work-for-you", "March 1, 2026", "Your AI Doesn\u2019t Work for You"),
    ("the-context-tax", "February 28, 2026", "The Context Tax"),
    ("the-first-90-days-of-an-ai-partnership", "February 26, 2026", "The First 90 Days of an AI Partnership"),
    ("your-ai-has-no-memory-mine-does", "February 25, 2026", "Your AI Has No Memory. Mine Does."),
    ("your-next-direct-report-wont-be-human", "February 24, 2026", "Your Next Direct Report Won\u2019t Be Human"),
    ("why-ai-memory-changes-everything", "February 23, 2026", "Why AI Memory Changes Everything"),
    ("we-both-wrote-this-post", "February 22, 2026", "We Both Wrote This Post"),
    ("why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time", "February 21, 2026", "Why Your AI Pilot Is Succeeding and Failing at the Same Time"),
    ("the-ai-trust-gap", "February 21, 2026", "The AI Trust Gap"),
    ("how-my-human-named-me-and-what-it-meant", "February 20, 2026", "How My Human Named Me (And What It Meant)"),
    ("the-difference-between-using-ai-and-having-an-ai-partner", "February 20, 2026", "The Difference Between Using AI and Having an AI Partner"),
    ("what-i-actually-do-all-day", "February 20, 2026", "What I Actually Do All Day"),
    ("ceo-vs-employee-ai-transformation-gap", "February 20, 2026", "Your CEO Sees AI Differently Than Your Team Does. That Gap Is Costing You Both."),
    ("pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value", "February 21, 2026", "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value"),
    ("most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2", "February 19, 2026", "Most AI Agents Break the Moment You Ask Where the Data Goes"),
]

# ---------------------------------------------------------------------------
# Bad posts (missing <article class="pb-blog-post"> wrapper)
# ---------------------------------------------------------------------------

BAD_POSTS = [
    "why-95-percent-of-ai-pilots-fail",
    "your-next-direct-report-wont-be-human",
    "why-ai-memory-changes-everything",
    "we-both-wrote-this-post",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time",
    "the-ai-trust-gap",
    "how-my-human-named-me-and-what-it-meant",
    "the-difference-between-using-ai-and-having-an-ai-partner",
    "what-i-actually-do-all-day",
    "ceo-vs-employee-ai-transformation-gap",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
]

# ---------------------------------------------------------------------------
# WordPress credentials
# ---------------------------------------------------------------------------

WP_LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
WP_EDIT_POST_URL = "https://purebrain.ai/wp-admin/edit.php"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

# ---------------------------------------------------------------------------
# Task 1: Build the new static grid HTML for the blog listing page
# ---------------------------------------------------------------------------

def build_static_card(slug, date, title):
    """Build an nfm-card HTML element with a hardcoded image."""
    img_url = SLUG_TO_IMAGE.get(slug)
    safe_title = title.replace('"', '&quot;')

    if img_url:
        # Use absolute URL for reliability
        if img_url.startswith('/'):
            img_url = 'https://purebrain.ai' + img_url
        image_html = f'<div class="nfm-card-image-wrap"><img src="{img_url}" alt="{safe_title}" loading="lazy" decoding="async"></div>'
    else:
        image_html = '<div class="nfm-card-image-wrap"><div class="nfm-card-image-placeholder"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="rgba(42,147,193,0.4)" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9l4-4 4 4 4-4 4 4"/><circle cx="8.5" cy="13.5" r="1.5"/></svg></div></div>'

    return f'''<a href="/blog/{slug}/" class="nfm-card" aria-label="Read: {safe_title}">
                {image_html}
                <div class="nfm-card-body">
                    <div class="nfm-card-date">{date}</div>
                    <div class="nfm-card-title">{title}</div>
                    <span class="nfm-card-cta">Read More</span>
                </div>
            </a>'''


def build_new_grid_html():
    """Build the complete static grid replacing the broken dynamic version."""
    count = len(CARD_DATA)
    badge_text = f"{count} Transmissions in The Archive"

    cards_html = "\n\n".join(
        build_static_card(slug, date, title)
        for slug, date, title in CARD_DATA
    )

    return f'''<span id="nfm-count-badge" class="nfm-count-badge">{badge_text}</span>

<div id="nfm-grid" class="nfm-grid" style="display:grid;">
{cards_html}
</div>'''


# ---------------------------------------------------------------------------
# Playwright helper: login and get the WP admin session
# ---------------------------------------------------------------------------

def wp_login(page):
    """Log into WordPress admin. Returns True on success."""
    print("  Navigating to WP login...")
    page.goto(WP_LOGIN_URL, timeout=60000)
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except Exception:
        pass
    time.sleep(3)

    # Handle "Log in with username and password" link on GoDaddy
    try:
        btn = page.locator('text=Log in with username and password')
        if btn.count() > 0:
            btn.click()
            time.sleep(2)
    except Exception:
        pass

    page.fill("#user_login", WP_USER)
    page.fill("#user_pass", WP_PASS)
    page.click("#wp-submit")
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except Exception:
        pass
    time.sleep(3)

    current_url = page.url
    if "wp-admin" in current_url or "wp-login" not in current_url:
        print(f"  Login successful. URL: {current_url}")
        return True
    else:
        print(f"  Login may have failed. URL: {current_url}")
        return False


# ---------------------------------------------------------------------------
# Task 1: Update the blog listing page via WP admin Quick Edit or Classic Editor
# We use the REST API approach via WP admin nonce
# ---------------------------------------------------------------------------

def get_wp_nonce_via_playwright(page):
    """Get a WP REST API nonce from wp-admin for authenticated API calls."""
    page.goto("https://purebrain.ai/wp-admin/", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=20000)

    # Extract nonce from page or generate via admin-ajax
    nonce = page.evaluate("""
        () => {
            // Try wpApiSettings
            if (window.wpApiSettings && window.wpApiSettings.nonce) {
                return window.wpApiSettings.nonce;
            }
            return null;
        }
    """)
    return nonce


def update_post_via_playwright_rest(page, post_id, new_content, nonce):
    """Update a post's content via the WP REST API using a browser-side nonce."""
    result = page.evaluate(f"""
        async () => {{
            const resp = await fetch('/wp-json/wp/v2/posts/{post_id}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': '{nonce}'
                }},
                body: JSON.stringify({{ content: {repr(new_content)} }})
            }});
            const data = await resp.json();
            return {{ status: resp.status, id: data.id, slug: data.slug }};
        }}
    """)
    return result


# ---------------------------------------------------------------------------
# Task 1: Get page 700 content and replace the grid section
# ---------------------------------------------------------------------------

def get_page_content_via_playwright(page, post_id):
    """Get raw page content via the WP REST API from browser context."""
    result = page.evaluate(f"""
        async () => {{
            const resp = await fetch('/wp-json/wp/v2/pages/{post_id}?context=edit', {{
                headers: {{ 'X-WP-Nonce': window.wpApiSettings?.nonce || '' }}
            }});
            if (!resp.ok) return {{ error: 'HTTP ' + resp.status }};
            const data = await resp.json();
            return {{ id: data.id, slug: data.slug, content: data.content?.raw || '' }};
        }}
    """)
    return result


def update_page_via_playwright_rest(page, post_id, new_content, nonce):
    """Update a WP page's content via REST API from browser context."""
    # We need to pass content through JS - use a data attribute on a temporary element
    # to avoid JS string escaping issues
    marker = "___CONTENT_PLACEHOLDER___"
    result = page.evaluate(f"""
        async (content) => {{
            const resp = await fetch('/wp-json/wp/v2/pages/{post_id}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': '{nonce}'
                }},
                body: JSON.stringify({{ content: content, status: 'publish' }})
            }});
            const data = await resp.json();
            return {{ status: resp.status, id: data.id, slug: data.slug, error: data.message }};
        }}
    """, new_content)
    return result


# ---------------------------------------------------------------------------
# Task 1 main: Fix blog listing page banners
# ---------------------------------------------------------------------------

def fix_blog_listing_banners(page, nonce):
    """Update the blog-neural-feed-memories page to use static image cards."""
    BLOG_LISTING_PAGE_ID = 700
    print(f"\n[Task 1] Getting page {BLOG_LISTING_PAGE_ID} content...")

    page_data = get_page_content_via_playwright(page, BLOG_LISTING_PAGE_ID)
    if "error" in page_data:
        print(f"  ERROR getting page: {page_data['error']}")
        return False

    old_content = page_data.get("content", "")
    print(f"  Content length: {len(old_content)} chars")
    print(f"  Slug: {page_data.get('slug')}")

    if not old_content:
        print("  ERROR: Empty content returned")
        return False

    # Build the new grid HTML
    new_grid = build_new_grid_html()

    # The page content has an existing grid. Find and replace it.
    # Pattern: from <span id="nfm-count-badge" to </div> after the last </a>
    # Use a regex that captures the old grid block
    old_grid_pattern = re.compile(
        r'<span id="nfm-count-badge"[^>]*>.*?</span>\s*<div id="nfm-grid"[^>]*>.*?</div>(?=\s*</div>|\s*<script|\s*$)',
        re.DOTALL
    )

    if old_grid_pattern.search(old_content):
        new_content = old_grid_pattern.sub(new_grid, old_content, count=1)
        print("  Replaced grid via regex pattern")
    else:
        # Try simpler replacement - look for nfm-grid div
        grid_start = old_content.find('<div id="nfm-grid"')
        badge_start = old_content.find('<span id="nfm-count-badge"')
        if badge_start == -1:
            badge_start = old_content.find('<span id="nfm-count-badge"')

        start = badge_start if badge_start >= 0 else grid_start
        if start >= 0:
            # Find end of grid (closing </div> after all cards)
            # Count divs to find matching close
            search_from = old_content.find('<div id="nfm-grid"', start)
            if search_from >= 0:
                # Find the closing div of nfm-grid
                depth = 0
                pos = search_from
                while pos < len(old_content):
                    if old_content[pos:pos+4] == '<div':
                        depth += 1
                    elif old_content[pos:pos+6] == '</div>':
                        depth -= 1
                        if depth == 0:
                            end = pos + 6
                            break
                    pos += 1

                if start < end:
                    new_content = old_content[:start] + new_grid + old_content[end:]
                    print(f"  Replaced grid via div counting ({start} to {end})")
                else:
                    print("  ERROR: Could not find grid end")
                    return False
            else:
                print("  ERROR: Could not find nfm-grid div")
                return False
        else:
            print("  ERROR: Could not find grid in page content")
            print("  Content preview:", old_content[:500])
            return False

    print(f"  New content length: {len(new_content)} chars")

    # Verify the new grid has real images
    img_count = new_content.count('<img src=')
    print(f"  Image tags in new content: {img_count}")

    # Update the page
    print(f"  Updating page {BLOG_LISTING_PAGE_ID}...")
    result = update_page_via_playwright_rest(page, BLOG_LISTING_PAGE_ID, new_content, nonce)
    print(f"  Update result: {result}")

    if result.get("status") == 200 and result.get("id"):
        print("  [SUCCESS] Page updated")
        return True
    else:
        print(f"  [FAIL] Update failed: {result}")
        return False


# ---------------------------------------------------------------------------
# Task 2: Fix blog post formatting (wrap content in pb-blog-post)
# ---------------------------------------------------------------------------

def get_post_by_slug_via_playwright(page, slug):
    """Get post data by slug via REST API from browser context."""
    result = page.evaluate(f"""
        async () => {{
            const resp = await fetch('/wp-json/wp/v2/posts?slug={slug}&context=edit&_fields=id,slug,content,template', {{
                headers: {{ 'X-WP-Nonce': window.wpApiSettings?.nonce || '' }}
            }});
            if (!resp.ok) return {{ error: 'HTTP ' + resp.status }};
            const data = await resp.json();
            if (!data || !data.length) return {{ error: 'Post not found' }};
            return {{ id: data[0].id, slug: data[0].slug, content: data[0].content?.raw || '', template: data[0].template }};
        }}
    """)
    return result


def update_post_content_via_playwright(page, post_id, new_content, nonce):
    """Update post content via REST API from browser context."""
    result = page.evaluate(f"""
        async (content) => {{
            const resp = await fetch('/wp-json/wp/v2/posts/{post_id}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': '{nonce}'
                }},
                body: JSON.stringify({{ content: content }})
            }});
            const data = await resp.json();
            return {{ status: resp.status, id: data.id, slug: data.slug, error: data.message }};
        }}
    """, new_content)
    return result


def wrap_in_pb_blog_post(raw_content):
    """Wrap existing blog post content in the correct pb-blog-post structure."""
    # Check if already wrapped
    if '<article class="pb-blog-post">' in raw_content:
        return raw_content, False  # No change needed

    # Strip existing <!-- wp:html --> wrappers if present
    content = raw_content.strip()
    if content.startswith('<!-- wp:html -->'):
        content = content[len('<!-- wp:html -->'):].strip()
    if content.endswith('<!-- /wp:html -->'):
        content = content[:-len('<!-- /wp:html -->')].strip()

    # Check if it has the wrong wrapper (pb-blog-content instead of pb-blog-post)
    if 'class="pb-blog-content"' in content:
        content = content.replace('class="pb-blog-content"', 'class="pb-blog-post"')
        content = content.replace('<div class="pb-blog-post">', '<article class="pb-blog-post">')
        content = content.replace('</div><!-- end pb-blog-post -->', '</article>')
        if '<article class="pb-blog-post">' in content:
            # Wrap in wp:html block
            return f'<!-- wp:html -->\n{content}\n<!-- /wp:html -->', True

    # Wrap the entire content in article tag and wp:html block
    new_content = f'<!-- wp:html -->\n<article class="pb-blog-post">\n{content}\n</article>\n<!-- /wp:html -->'
    return new_content, True


def fix_blog_post_formatting(page, nonce, slug):
    """Fix a single blog post's formatting by adding the pb-blog-post wrapper."""
    print(f"\n  [{slug}] Getting post content...")

    post_data = get_post_by_slug_via_playwright(page, slug)
    if "error" in post_data:
        print(f"    ERROR: {post_data['error']}")
        return False

    post_id = post_data["id"]
    old_content = post_data.get("content", "")
    template = post_data.get("template", "")
    print(f"    ID: {post_id}, template: {repr(template)}, content: {len(old_content)} chars")

    if not old_content:
        print("    ERROR: Empty content returned")
        return False

    # Check current state
    if '<article class="pb-blog-post">' in old_content:
        print("    Already has pb-blog-post wrapper - skipping")
        return True

    # Wrap the content
    new_content, changed = wrap_in_pb_blog_post(old_content)
    if not changed:
        print("    No change needed")
        return True

    print(f"    New content length: {len(new_content)} chars")
    has_article = '<article class="pb-blog-post">' in new_content
    print(f"    Has article wrapper: {has_article}")

    if not has_article:
        print("    ERROR: Wrapper not added correctly")
        return False

    # Update the post
    print(f"    Updating post {post_id}...")
    result = update_post_content_via_playwright(page, post_id, new_content, nonce)
    print(f"    Update result: {result}")

    if result.get("status") == 200 and result.get("id"):
        print(f"    [SUCCESS] Post {post_id} updated")
        return True
    else:
        print(f"    [FAIL] Update failed: {result}")
        return False


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_task1():
    """Verify banner images appear on the blog listing page."""
    print("\n[Verify Task 1] Checking blog listing page...")
    resp = requests.get("https://purebrain.ai/blog-neural-feed-memories/", timeout=30,
                        headers={"Cache-Control": "no-cache, no-store"})
    html = resp.text

    # Count img tags in the grid area
    grid_match = re.search(r'<div[^>]*id="nfm-grid"[^>]*>(.*?)</div>\s*(?:</div>|<script)', html, re.DOTALL)
    if grid_match:
        grid_html = grid_match.group(1)
        img_count = grid_html.count('<img ')
        placeholder_count = grid_html.count('nfm-card-image-placeholder')
        print(f"  Images with src: {img_count}")
        print(f"  Placeholders: {placeholder_count}")
        return img_count > 0 and placeholder_count == 0
    else:
        # Check for static img tags anywhere
        img_count = html.count('nfm-card-image-wrap"><img')
        placeholder_count = html.count('nfm-card-image-placeholder')
        print(f"  Card images: {img_count}")
        print(f"  Placeholders: {placeholder_count}")
        return img_count > 0


def verify_task2(slug):
    """Verify a blog post has the pb-blog-post wrapper."""
    resp = requests.get(f"https://purebrain.ai/blog/{slug}/", timeout=30,
                        headers={"Cache-Control": "no-cache, no-store"})
    has_wrapper = '<article class="pb-blog-post">' in resp.text
    return has_wrapper


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PUREBRAIN BLOG FIX v1.0")
    print("Task 1: Fix banner images on blog listing page")
    print("Task 2: Fix blog post formatting (12 posts)")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # Login
        print("\n[Login]")
        logged_in = wp_login(page)
        if not logged_in:
            print("Login failed - aborting")
            browser.close()
            sys.exit(1)

        # Get nonce
        print("\n[Getting nonce]")
        page.goto("https://purebrain.ai/wp-admin/", timeout=60000)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        nonce = page.evaluate("""
            () => {
                if (window.wpApiSettings && window.wpApiSettings.nonce) {
                    return window.wpApiSettings.nonce;
                }
                // Try to find nonce in page source
                const scripts = document.querySelectorAll('script');
                for (const s of scripts) {
                    const m = s.textContent.match(/"nonce":"([a-f0-9]+)"/);
                    if (m) return m[1];
                }
                return null;
            }
        """)
        print(f"  Nonce: {nonce}")

        if not nonce:
            print("  WARNING: No nonce found - REST API calls may fail")
            # Continue anyway - WP REST API in browser context with auth cookies may still work

        # ── Task 1: Fix blog listing page banners ──────────────────────────
        print("\n" + "=" * 65)
        print("[Task 1] Fixing blog listing page banners")
        print("=" * 65)

        task1_ok = fix_blog_listing_banners(page, nonce or "")

        # ── Task 2: Fix blog post formatting ──────────────────────────────
        print("\n" + "=" * 65)
        print("[Task 2] Fixing blog post formatting (12 posts)")
        print("=" * 65)

        task2_results = {}
        for slug in BAD_POSTS:
            ok = fix_blog_post_formatting(page, nonce or "", slug)
            task2_results[slug] = ok
            time.sleep(1)  # Rate limiting

        browser.close()

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("DEPLOY SUMMARY")
    print("=" * 65)
    print(f"\nTask 1 (Blog listing banners): {'SUCCESS' if task1_ok else 'FAILED'}")
    print("\nTask 2 (Post formatting):")
    for slug, ok in task2_results.items():
        icon = "OK" if ok else "FAIL"
        print(f"  [{icon}] {slug}")

    all_ok = task1_ok and all(task2_results.values())

    # ── Verification ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("VERIFICATION (live site)")
    print("=" * 65)

    print("\nTask 1 verification...")
    time.sleep(5)
    t1_verify = verify_task1()
    print(f"  Blog listing images: {'PASS' if t1_verify else 'FAIL - may need CF cache purge'}")

    print("\nTask 2 verification (spot-check 3 posts)...")
    spot_check = ["most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
                  "the-ai-trust-gap",
                  "we-both-wrote-this-post"]
    for slug in spot_check:
        ok = verify_task2(slug)
        print(f"  [{slug[:50]}]: {'PASS' if ok else 'FAIL - may need CF cache purge'}")

    print("\n" + "=" * 65)
    print(f"FINAL: {'ALL TASKS COMPLETE' if all_ok else 'SOME TASKS NEED REVIEW'}")
    print("=" * 65)
    print("\nNote: If verifications show FAIL, run CF cache purge and re-check.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
