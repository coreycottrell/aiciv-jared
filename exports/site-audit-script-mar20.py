"""
PureBrain.ai Full Site Audit — March 20, 2026
Checks: broken links, broken images, JS errors, form/button functionality
"""
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

PAGES = [
    "https://purebrain.ai/",
    "https://purebrain.ai/blog/",
    "https://purebrain.ai/blog-neural-feed-memories/",
    "https://purebrain.ai/live/",
    "https://purebrain.ai/insiders/",
    "https://purebrain.ai/awakened/",
    "https://purebrain.ai/partnered/",
    "https://purebrain.ai/unified/",
    "https://purebrain.ai/pay-test-sandbox-3/",
    "https://purebrain.ai/refer/",
    "https://purebrain.ai/invitation/",
    "https://purebrain.ai/governance/",
    "https://purebrain.ai/ai-partnership-guide/",
    "https://purebrain.ai/compare/",
    "https://purebrain.ai/brainiac-mastermind-training/",
    "https://purebrain.ai/investors-v8/?open=1",
]

BLOG_SAMPLES = [
    "https://purebrain.ai/blog/52-billion-ai-agents-market-is-not-the-story/",
    "https://purebrain.ai/blog/age-of-ai-agents-next-18-months/",
    "https://purebrain.ai/blog/teach-your-ai-something-no-one-else-can/",
    "https://purebrain.ai/blog/the-context-tax/",
    "https://purebrain.ai/blog/why-ai-memory-changes-everything/",
    "https://purebrain.ai/blog/your-ai-has-no-idea-who-you-are/",
]


async def audit_page(page, url):
    result = {
        "url": url,
        "http_status": None,
        "loaded": False,
        "title": None,
        "js_errors": [],
        "console_errors": [],
        "broken_links": [],
        "broken_images": [],
        "redirect_to": None,
        "notes": [],
    }

    js_errors = []
    console_errors = []

    page.on("pageerror", lambda err: js_errors.append(str(err)))
    page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

    # Track response status
    responses = {}
    page.on("response", lambda r: responses.update({r.url: r.status}))

    try:
        # Navigate
        is_heavy = any(x in url for x in ["/insiders/", "purebrain.ai/", "/investors-v8/"])
        wait_time = 8 if is_heavy else 5

        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        result["http_status"] = response.status if response else None

        if response and response.status >= 400:
            result["notes"].append(f"HTTP {response.status} error")
            return result

        # Check for redirect
        final_url = page.url
        if final_url.rstrip("/") != url.rstrip("/"):
            result["redirect_to"] = final_url

        await asyncio.sleep(wait_time)

        result["loaded"] = True
        result["title"] = await page.title()

        # Check for 404/error page content
        page_text = await page.evaluate("() => document.body ? document.body.innerText.substring(0, 500) : ''")
        if any(x in page_text.lower() for x in ["404", "page not found", "not found"]):
            result["notes"].append("Page content indicates 404/not found")

        # Check broken images
        img_data = await page.evaluate("""() => {
            const imgs = [...document.querySelectorAll('img')];
            return imgs.map(img => ({
                src: img.src || img.getAttribute('src') || '',
                alt: img.alt || '',
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete
            }));
        }""")

        broken_imgs = []
        for img in img_data:
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
            # Image broken if complete but 0x0 size (and not a tracking pixel)
            if img.get("complete") and img.get("naturalWidth") == 0 and img.get("naturalHeight") == 0:
                broken_imgs.append(src)

        result["broken_images"] = broken_imgs

        # Check all links on the page
        links_data = await page.evaluate("""() => {
            const links = [...document.querySelectorAll('a[href]')];
            return links.map(a => ({
                href: a.href,
                text: (a.textContent || '').trim().substring(0, 80),
                visible: a.offsetWidth > 0 || a.offsetHeight > 0
            })).filter(l => l.href && !l.href.startsWith('javascript:') && !l.href.startsWith('mailto:') && !l.href.startsWith('tel:'));
        }""")

        # Check key internal links for 404 (check a sample)
        checked_links = set()
        broken_links = []
        internal_links = [l for l in links_data if "purebrain.ai" in l.get("href", "") and l.get("href")]

        # Deduplicate
        unique_links = {}
        for l in internal_links:
            href = l["href"].split("#")[0].split("?")[0].rstrip("/")
            if href and href not in checked_links:
                unique_links[href] = l["text"]
                checked_links.add(href)

        # Use fetch to check link statuses (batch check)
        if unique_links:
            link_urls = list(unique_links.keys())[:30]  # Cap at 30 per page
            link_statuses = await page.evaluate("""async (urls) => {
                const results = {};
                const checks = urls.map(async url => {
                    try {
                        const r = await fetch(url, {method: 'HEAD', redirect: 'follow'});
                        results[url] = r.status;
                    } catch(e) {
                        results[url] = 'error: ' + e.message;
                    }
                });
                await Promise.allSettled(checks);
                return results;
            }""", link_urls)

            for link_url, status in link_statuses.items():
                if isinstance(status, int) and status >= 400:
                    broken_links.append({"url": link_url, "status": status, "text": unique_links.get(link_url, "")})
                elif isinstance(status, str) and "error" in status:
                    broken_links.append({"url": link_url, "status": status, "text": unique_links.get(link_url, "")})

        result["broken_links"] = broken_links

        # Check for key interactive elements
        # Form inputs and buttons
        button_info = await page.evaluate("""() => {
            const buttons = [...document.querySelectorAll('button, input[type="submit"], [role="button"]')];
            const forms = [...document.querySelectorAll('form')];
            return {
                button_count: buttons.length,
                form_count: forms.length,
                visible_buttons: buttons.filter(b => b.offsetWidth > 0).length
            };
        }""")
        result["notes"].append(f"Buttons: {button_info['visible_buttons']}/{button_info['button_count']} visible, Forms: {button_info['form_count']}")

        # Check chatbox presence on pages that should have it
        chatbox_pages = ["/", "/insiders/", "/awakened/", "/partnered/", "/unified/", "/pay-test-sandbox-3/"]
        if any(p in url for p in chatbox_pages):
            chatbox = await page.evaluate("""() => {
                const el = document.querySelector('#chat-widget, #chatbox, .chat-container, [id*="chat"]');
                return el ? {found: true, id: el.id, visible: el.offsetWidth > 0} : {found: false};
            }""")
            result["notes"].append(f"Chatbox: {chatbox}")

    except Exception as e:
        result["notes"].append(f"Error during audit: {str(e)}")

    result["js_errors"] = js_errors[:10]  # Cap at 10
    result["console_errors"] = console_errors[:10]

    return result


async def run_audit():
    all_pages = PAGES + BLOG_SAMPLES
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        for url in all_pages:
            print(f"Auditing: {url}")
            try:
                result = await audit_page(page, url)
                results.append(result)
                print(f"  Status: {result['http_status']} | JS errors: {len(result['js_errors'])} | Broken imgs: {len(result['broken_images'])} | Broken links: {len(result['broken_links'])}")
            except Exception as e:
                results.append({"url": url, "error": str(e)})
                print(f"  ERROR: {e}")

            await asyncio.sleep(2)  # Brief pause between pages

        await browser.close()

    return results


if __name__ == "__main__":
    print(f"Starting audit at {datetime.now().isoformat()}")
    results = asyncio.run(run_audit())

    # Save raw results
    with open("/home/jared/projects/AI-CIV/aether/exports/site-audit-raw-mar20.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nAudit complete. {len(results)} pages checked.")
    print("Raw results saved to site-audit-raw-mar20.json")
