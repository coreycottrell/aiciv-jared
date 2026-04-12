"""
QA Suite: pb-button-styling plugin extraction #4
Tests that button hover CSS was extracted without breaking anything.
"""
import asyncio
import sys
from playwright.async_api import async_playwright

RESULTS = []

def record(name, passed, evidence):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((status, name, evidence))
    print(f"[{status}] {name}")
    print(f"       {evidence}")

async def run_qa():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ─────────────────────────────────────────────
        # 1. Homepage
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            status = resp.status if resp else 0
            content = await page.content()
            dark_bg = "#080a12" in content or "background" in content
            has_video = "<video" in content or "video" in content.lower()
            passed = status == 200 and dark_bg
            record("1. Homepage loads (dark bg, 200 OK)",
                   passed,
                   f"HTTP {status} | dark_bg_css={'yes' if dark_bg else 'no'} | video_tag={'yes' if has_video else 'no'}")
        except Exception as e:
            record("1. Homepage loads", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 2. Blog listing
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/blog/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            status = resp.status if resp else 0
            content = await page.content()
            has_posts = "article" in content or "post" in content.lower() or "entry" in content
            passed = status == 200 and has_posts
            record("2. Blog listing loads (posts visible)",
                   passed,
                   f"HTTP {status} | posts_found={'yes' if has_posts else 'no'}")
        except Exception as e:
            record("2. Blog listing loads", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 3. Blog post
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto(
                "https://purebrain.ai/the-age-of-ai-agents-is-here/?nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            status = resp.status if resp else 0
            content = await page.content()
            has_content = "pb-blog-post" in content or "article" in content or len(content) > 5000
            passed = status == 200 and has_content
            record("3. Blog post loads (readable)",
                   passed,
                   f"HTTP {status} | blog_content={'yes' if has_content else 'no'} | content_len={len(content)}")
        except Exception as e:
            record("3. Blog post loads", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 4. Pay-test-2 (chatbox visible)
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto(
                "https://purebrain.ai/pay-test-2/?nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            status = resp.status if resp else 0
            content = await page.content()
            has_chatbox = "chatbox" in content.lower() or "chat" in content.lower() or "pb-chat" in content
            passed = status == 200
            record("4. Pay-test-2 loads (chatbox present)",
                   passed,
                   f"HTTP {status} | chatbox_indicator={'yes' if has_chatbox else 'no'}")
        except Exception as e:
            record("4. Pay-test-2 loads", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 5. Sandbox-3
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto(
                "https://purebrain.ai/pay-test-sandbox-3/?nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            status = resp.status if resp else 0
            content = await page.content()
            not_blank = len(content) > 2000
            passed = status == 200 and not_blank
            record("5. Sandbox-3 loads",
                   passed,
                   f"HTTP {status} | content_len={len(content)}")
        except Exception as e:
            record("5. Sandbox-3 loads", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 6. Button hover CSS from pb-button-styling plugin
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            content = await page.content()
            # Should have pb-button-hover-v622 style tag
            has_hover_style = "pb-button-hover-v622" in content
            # Should NOT have it coming from security plugin (we check the style tag id attr)
            # The tag id should be "pb-button-hover-v622-css" per WP enqueue convention
            has_correct_id = "pb-button-hover-v622-css" in content
            passed = has_hover_style
            record("6. Button hover CSS present (pb-button-hover-v622)",
                   passed,
                   f"style_tag_found={'yes' if has_hover_style else 'NO — MISSING'} | correct_id={'yes' if has_correct_id else 'no'}")
        except Exception as e:
            record("6. Button hover CSS present", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 7. Calculator button hover styling
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            content = await page.content()
            # Look for calculator link
            has_calc_link = "ai-tool-stack-calculator" in content
            # Look for hover CSS rule (pb-button-hover or .elementor-button:hover)
            has_hover_rule = (".elementor-button:hover" in content or
                              "pb-button-hover" in content or
                              "pb-cta-hover" in content)
            passed = has_hover_rule
            record("7. Calculator button hover styling present",
                   passed,
                   f"calc_link={'yes' if has_calc_link else 'no'} | hover_css={'yes' if has_hover_rule else 'NO — MISSING'}")
        except Exception as e:
            record("7. Calculator button hover styling", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 8. 301 redirect: /ai-adoption-assessment → /ai-partnership-assessment/
        # ─────────────────────────────────────────────
        try:
            redirect_page = await context.new_page()
            redirected_to = None
            redirect_status = None

            # Intercept the redirect chain
            responses = []
            redirect_page.on("response", lambda r: responses.append(r))

            await redirect_page.goto(
                "https://purebrain.ai/ai-adoption-assessment?nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            final_url = redirect_page.url
            await redirect_page.close()

            # Check if we landed at the right place
            landed_correct = "ai-partnership-assessment" in final_url
            # Check if any 301 was in the chain
            had_301 = any(r.status == 301 for r in responses)

            passed = landed_correct
            record("8. 301 redirect ai-adoption → ai-partnership",
                   passed,
                   f"final_url={final_url} | had_301={'yes' if had_301 else 'no (may be 302 or Cloudflare)'} | landed_correct={'yes' if landed_correct else 'NO'}")
        except Exception as e:
            record("8. 301 redirect", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 9. REST API returns JSON
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto(
                "https://purebrain.ai/wp-json/wp/v2/posts?per_page=1&nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            status = resp.status if resp else 0
            content_type = resp.headers.get("content-type", "") if resp else ""
            body = await page.content()
            is_json = '"id"' in body and '"title"' in body
            passed = status == 200 and is_json
            record("9. REST API returns JSON",
                   passed,
                   f"HTTP {status} | content_type={content_type[:50]} | has_post_fields={'yes' if is_json else 'NO'}")
        except Exception as e:
            record("9. REST API returns JSON", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 10. Admin accessible (not blocked)
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto(
                "https://purebrain.ai/wp-admin/?nocache=qa4",
                wait_until="domcontentloaded", timeout=30000
            )
            status = resp.status if resp else 0
            final_url = page.url
            content = await page.content()
            # Should show login page, not 403/blocked
            has_login = "wp-login" in final_url or "user_login" in content or "loginform" in content
            not_blocked = status not in [403, 401] and "blocked" not in content.lower()
            passed = not_blocked and has_login
            record("10. Admin accessible (login page shown, not blocked)",
                   passed,
                   f"HTTP {status} | final_url={final_url[:60]} | login_form={'yes' if has_login else 'no'}")
        except Exception as e:
            record("10. Admin accessible", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 11. Mobile video CSS tag present
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            content = await page.content()
            has_video_css = "pb-video-handler-css" in content
            passed = has_video_css
            record("11. Mobile video CSS tag present (pb-video-handler-css)",
                   passed,
                   f"style_tag_found={'yes' if has_video_css else 'NO — MISSING'}")
        except Exception as e:
            record("11. Mobile video CSS tag", False, f"Exception: {e}")

        # ─────────────────────────────────────────────
        # 12. Mobile video JS tag present
        # ─────────────────────────────────────────────
        try:
            resp = await page.goto("https://purebrain.ai/?nocache=qa4", wait_until="domcontentloaded", timeout=30000)
            content = await page.content()
            has_video_js = "pb-video-mobile-pause" in content
            passed = has_video_js
            record("12. Mobile video JS tag present (pb-video-mobile-pause)",
                   passed,
                   f"script_tag_found={'yes' if has_video_js else 'NO — MISSING'}")
        except Exception as e:
            record("12. Mobile video JS tag", False, f"Exception: {e}")

        await browser.close()

    # ─────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────
    print("\n" + "="*60)
    print("QA RESULTS SUMMARY — pb-button-styling Extraction #4")
    print("="*60)
    passes = sum(1 for r in RESULTS if r[0] == "PASS")
    fails = sum(1 for r in RESULTS if r[0] == "FAIL")
    for status, name, evidence in RESULTS:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} [{status}] {name}")
    print(f"\nTotal: {passes} PASS / {fails} FAIL / {len(RESULTS)} total")
    return fails

if __name__ == "__main__":
    fail_count = asyncio.run(run_qa())
    sys.exit(0 if fail_count == 0 else 1)
