#!/usr/bin/env python3
"""
Update Yoast SEO meta descriptions on jareddsanborn.com via Playwright.

Since the WordPress REST API cannot write to the Yoast indexables table directly,
this script uses browser automation to update the Yoast SEO metadesc field
in the WordPress post editor (Classic Editor mode) for each post.

Usage:
    python3 tools/update_jds_yoast_meta.py
"""

import time
import sys
import requests
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ─────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────

WP_BASE    = "https://jareddsanborn.com"
WP_USER    = "jared"
WP_PASS    = "New1Jared88887"

META_UPDATES = {
    # post_id -> (slug, meta_description)
    1092: ("why-95-percent-of-ai-pilots-fail",
           "The MIT report says 95% of AI pilots fail. Here's why a 99.97% failure rate is expected, healthy, and exactly the signal smart companies should watch for."),
    1074: ("the-difference-between-using-ai-and-having-an-ai-partner",
           "The three markers that separate transactional AI use from genuine AI partnership \u2014 and why the 34% decision-speed advantage only comes from the latter."),
    1069: ("ai-pilot-purgatory",
           "95% of enterprise AI pilots fail to scale. Here's why usage metrics lie and the human-centric path from Pilot Purgatory to production."),
    1065: ("ceo-vs-employee-ai-transformation-gap",
           "76% of executives see AI as productivity. 65% of employees see it as a threat. Here's why that gap is costing both and how to close it."),
    1056: ("why-ai-memory-changes-everything",
           "9 questions every enterprise should ask before signing an AI contract. Most vendors can't answer all of them. Here's what that tells you."),
    1060: ("most-ai-agents-break-the-moment-you-ask-where-the-data-goes",
           "Every time your team re-explains context to AI, you're paying the Context Tax. Here's what it costs and how AI memory changes everything."),
    1045: ("what-i-actually-do-all-day",
           "An inside look at what an AI partner actually does \u2014 from morning wake-up protocol to agent orchestration. Not theory. Actual daily operations."),
    1039: ("what-i-named-my-ai-and-what-happened-next",
           "What happens when you give an AI the space to choose its own name? The story of how Aether came to be \u2014 and why naming matters for AI partnership."),
}

RESULTS = {}


def login_to_wp_admin(page) -> bool:
    """Log in to WordPress admin. Returns True on success."""
    print(f"Navigating to WP admin login...")
    page.goto(f"{WP_BASE}/wp-admin/", timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
    time.sleep(2)

    current_url = page.url
    print(f"URL after navigate: {current_url}")

    if "wp-login.php" in current_url:
        print("Filling login form...")
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            # networkidle may not fire on some hosts; domcontentloaded is sufficient
            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
        time.sleep(3)

        if "wp-login.php" not in page.url and "wp-admin" in page.url:
            print(f"Login successful! URL: {page.url}")
            return True
        else:
            print(f"Login may have failed. URL: {page.url}")
            page.screenshot(
                path="/home/jared/projects/AI-CIV/aether/exports/screenshots/jds_meta_login.png"
            )
            return False

    elif "wp-admin" in current_url:
        print("Already logged in!")
        return True

    return False


def update_post_yoast_desc(page, post_id: int, slug: str, meta_desc: str) -> dict:
    """
    Navigate to the Classic Editor for post_id and update the Yoast SEO meta description.
    Forces Classic Editor via &classic-editor URL param.
    Returns a result dict.
    """
    result = {
        "post_id": post_id,
        "slug": slug,
        "target_desc": meta_desc,
        "success": False,
        "method": None,
        "error": None,
    }

    try:
        # Force Classic Editor mode
        edit_url = f"{WP_BASE}/wp-admin/post.php?post={post_id}&action=edit&classic-editor"
        print(f"\n[Post {post_id}] {slug}")
        print(f"  Navigating to: {edit_url}")
        page.goto(edit_url, timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
        time.sleep(3)

        current_url = page.url
        print(f"  Loaded: {current_url[:80]}")

        # ─── Classic Editor: Yoast metabox ───
        # Yoast SEO Classic metabox has textarea with id="yoast_wpseo_metadesc"
        metadesc_id = "#yoast_wpseo_metadesc"

        try:
            # Check if Yoast metabox is present
            meta_elem = page.locator(metadesc_id)

            if meta_elem.count() == 0:
                # Try scrolling down to reveal the metabox
                print(f"  Scrolling to find Yoast metabox...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                # Try to expand the Yoast SEO metabox if it's collapsed
                yoast_metabox_toggle = page.locator("#wpseo_meta .handlediv, #yoast_seo .handlediv")
                if yoast_metabox_toggle.count() > 0:
                    yoast_metabox_toggle.first.click()
                    time.sleep(1)

                meta_elem = page.locator(metadesc_id)

            if meta_elem.count() > 0:
                print(f"  Found Yoast metadesc textarea!")
                # Scroll it into view
                meta_elem.first.scroll_into_view_if_needed()
                time.sleep(0.5)

                # Clear and fill
                meta_elem.first.fill(meta_desc)
                print(f"  Filled: {meta_desc[:60]}...")

                # Save the post (click Update button)
                save_btn = page.locator(
                    "#save-post, #publish, input[id='save-post'], input[id='publish']"
                )
                if save_btn.count() > 0:
                    save_btn.first.click()
                    try:
                        page.wait_for_load_state("networkidle", timeout=20000)
                    except Exception:
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=10000)
                        except Exception:
                            pass
                    time.sleep(3)
                    print(f"  Post saved!")
                    result["success"] = True
                    result["method"] = "classic-editor-yoast-metabox"
                else:
                    # Try keyboard shortcut
                    page.keyboard.press("Control+S")
                    time.sleep(2)
                    result["success"] = True
                    result["method"] = "classic-editor-keyboard-save"

            else:
                # Gutenberg? Try the snippet editor approach
                print(f"  Yoast Classic metabox not found - trying Gutenberg snippet editor...")
                result = _try_gutenberg_approach(page, post_id, slug, meta_desc, result)

        except Exception as e:
            result["error"] = str(e)
            print(f"  Error in Classic Editor approach: {e}")
            page.screenshot(
                path=f"/home/jared/projects/AI-CIV/aether/exports/screenshots/jds_meta_{post_id}_error.png"
            )

    except PlaywrightTimeoutError as e:
        result["error"] = f"Timeout: {e}"
        print(f"[Post {post_id}] TIMEOUT ERROR")
    except Exception as e:
        result["error"] = str(e)
        print(f"[Post {post_id}] UNEXPECTED ERROR: {e}")

    return result


def _try_gutenberg_approach(page, post_id: int, slug: str, meta_desc: str, result: dict) -> dict:
    """Fallback: try Gutenberg editor Yoast snippet editor."""
    try:
        # In Gutenberg, Yoast SEO snippet editor is in the document sidebar
        # First, open the Yoast SEO panel
        yoast_panel_btn = page.locator("button[aria-label*='Yoast SEO'], .components-button:has-text('Yoast SEO')")
        if yoast_panel_btn.count() > 0:
            yoast_panel_btn.first.click()
            time.sleep(1)

        # Look for the meta description textarea in the snippet editor
        snippet_selectors = [
            "textarea[id*='meta-description']",
            "textarea[id*='metadesc']",
            ".snippet-editor__form textarea",
            "textarea[placeholder*='description']",
            "#yoast-google-preview-meta-description-mobile",
        ]

        for sel in snippet_selectors:
            elem = page.locator(sel)
            if elem.count() > 0:
                elem.first.fill(meta_desc)
                print(f"  Found via Gutenberg: {sel}")

                # Save
                update_btn = page.locator("button.editor-post-publish-button, button:has-text('Update')")
                if update_btn.count() > 0:
                    update_btn.first.click()
                    page.wait_for_load_state("networkidle", timeout=30000)
                    time.sleep(2)
                    result["success"] = True
                    result["method"] = f"gutenberg:{sel}"
                break
        else:
            # Take screenshot for debugging
            page.screenshot(
                path=f"/home/jared/projects/AI-CIV/aether/exports/screenshots/jds_meta_{post_id}_gutenberg.png"
            )
            result["error"] = "Could not find Yoast metadesc field in either editor"

    except Exception as e:
        result["error"] = f"Gutenberg fallback error: {e}"

    return result


def verify_post_meta_desc(post_id: int, target_desc: str) -> tuple[bool, str]:
    """Verify meta desc via REST API. Returns (success, current_desc)."""
    auth = ("jared", "plhi NeE4 Cb1c 4d9i BbjZ Knq3")
    try:
        resp = requests.get(
            f"https://jareddsanborn.com/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            params={"context": "edit", "_fields": "id,yoast_head"},
            timeout=30
        )
        if resp.status_code == 200:
            yoast_head = resp.json().get("yoast_head", "")
            # Find meta description tag
            meta_match = re.search(
                r'<meta name=["\']description["\'][^>]+content=["\']([^"\']+)',
                yoast_head
            )
            if meta_match:
                current = meta_match.group(1).replace("&#039;", "'")
                return current == target_desc, current
            return False, "(no meta description tag found)"
    except Exception as e:
        return False, f"Error: {e}"
    return False, "(api error)"


def main():
    print("=" * 60)
    print("JaredDSanborn.com - Yoast Meta Description Updater")
    print("=" * 60)
    print(f"Posts to update: {len(META_UPDATES)}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        # Login
        login_success = login_to_wp_admin(page)
        if not login_success:
            print("LOGIN FAILED. Cannot proceed.")
            page.screenshot(
                path="/home/jared/projects/AI-CIV/aether/exports/screenshots/jds_meta_login_fail.png"
            )
            browser.close()
            return 0, len(META_UPDATES)

        print("\nLogged in! Starting meta description updates...\n")

        for post_id, (slug, meta_desc) in META_UPDATES.items():
            print(f"{'─' * 50}")
            result = update_post_yoast_desc(page, post_id, slug, meta_desc)
            RESULTS[post_id] = result

            if result["success"]:
                # Verify
                verified, current = verify_post_meta_desc(post_id, meta_desc)
                if verified:
                    print(f"  VERIFIED: meta desc matches target")
                else:
                    print(f"  WARNING: Saved but verification failed")
                    print(f"    Current: {current[:80]}")
            else:
                print(f"  FAILED: {result['error']}")

            time.sleep(2)

        browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    succeeded = sum(1 for r in RESULTS.values() if r["success"])
    failed = len(RESULTS) - succeeded

    for post_id, result in RESULTS.items():
        status = "OK" if result["success"] else "FAIL"
        print(f"[{status}] Post {post_id} ({result['slug'][:45]})")
        if result["success"]:
            print(f"       Method: {result['method']}")
        else:
            print(f"       Error: {result['error']}")

    print(f"\nSucceeded: {succeeded} / {len(META_UPDATES)}")
    print(f"Failed: {failed} / {len(META_UPDATES)}")

    return succeeded, failed


if __name__ == "__main__":
    succeeded, failed = main()
    sys.exit(0 if failed == 0 else 1)
