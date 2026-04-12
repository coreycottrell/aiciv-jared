"""Script load audit — find why startConversation is not defined"""
import asyncio
from playwright.async_api import async_playwright

PASSWORD = "PureBrain.ai253443$$$"


async def check_scripts(url, slug):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--ignore-certificate-errors"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True,
        )
        page = await ctx.new_page()
        console = []
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))

        failed_reqs = []
        all_responses = []
        page.on("requestfailed", lambda r: failed_reqs.append({"url": r.url, "failure": r.failure}))
        page.on("response", lambda r: all_responses.append({"status": r.status, "url": r.url}))

        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Password
        pw_input = await page.query_selector('input[name="post_password"]')
        if pw_input:
            await pw_input.fill(PASSWORD)
            await page.click('input[type="submit"]')
            await page.wait_for_timeout(5000)

        print(f"\n{'='*60}")
        print(f" {slug}: {url}")
        print(f"{'='*60}")

        # Get ALL script tags
        all_scripts = await page.eval_on_selector_all(
            "script",
            """els => els.map(e => ({
                src: e.src || "(inline)",
                type: e.type || "text/javascript",
                hasContent: e.textContent.length > 0,
                contentLen: e.textContent.length,
                contentPreview: e.src ? "" : e.textContent.substring(0, 200)
            }))""",
        )

        print(f"\nTotal script tags: {len(all_scripts)}")
        ext_count = sum(1 for s in all_scripts if s["src"] != "(inline)")
        inline_count = len(all_scripts) - ext_count
        print(f"  External: {ext_count}, Inline: {inline_count}")

        print("\nExternal scripts:")
        for s in all_scripts:
            if s["src"] != "(inline)":
                print(f"  {s['src'][:150]}")

        print("\nLarge inline scripts (>1000 chars):")
        for s in all_scripts:
            if s["src"] == "(inline)" and s["contentLen"] > 1000:
                preview = s["contentPreview"].replace("\n", " ")
                print(f"  [{s['contentLen']} chars] {preview[:150]}")

        # Check if the PTC script URL is in any responses
        print("\nJS responses (script files):")
        js_responses = [r for r in all_responses if ".js" in r["url"] and r.get("status")]
        for r in js_responses[:20]:
            print(f"  [{r['status']}] {r['url'][:150]}")

        # Failed requests
        print(f"\nFailed network requests: {len(failed_reqs)}")
        for r in failed_reqs[:10]:
            print(f"  {r}")

        # CSP-specific errors
        csp_errors = [m for m in console if "violates" in m["text"] or "Content Security Policy" in m["text"]]
        print(f"\nCSP errors: {len(csp_errors)}")
        for e in csp_errors[:5]:
            print(f"  {e['text'][:300]}")

        # What is the full CSP?
        csp_header = resp.headers.get("content-security-policy", "NOT SET")
        print(f"\nPage CSP: {csp_header[:600]}")

        # Check if any script is about PTC/birth
        ptc_scripts = [s for s in all_scripts if "ptc" in s["src"].lower() or "birth" in s["src"].lower() or "chatbox" in s["src"].lower()]
        print(f"\nPTC/birth/chatbox scripts: {len(ptc_scripts)}")
        for s in ptc_scripts:
            print(f"  {s}")

        # Look for the big inline HTML widget
        html_widgets = await page.eval_on_selector_all(
            ".elementor-widget-html",
            """els => els.map(e => ({
                height: e.offsetHeight,
                contentLen: e.innerHTML.length,
                hasPTC: e.innerHTML.includes('ptc-wrapper') || e.innerHTML.includes('runBirthInit'),
                hasBirth: e.innerHTML.includes('birth'),
                hasChatInit: e.innerHTML.includes('chat-initial'),
                preview: e.innerHTML.substring(0, 300)
            }))""",
        )
        print(f"\nElementor HTML widgets: {len(html_widgets)}")
        for w in html_widgets:
            print(f"  height={w['height']}, len={w['contentLen']}, hasPTC={w['hasPTC']}, hasBirth={w['hasBirth']}, hasChatInit={w['hasChatInit']}")

        await ctx.close()
        await browser.close()


async def main():
    await check_scripts("https://purebrain.ai/pay-test-sandbox-2/", "sandbox2")
    await check_scripts("https://purebrain.ai/pay-test-2/", "paytest2")


asyncio.run(main())
