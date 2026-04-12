"""
OAuth Button Visual Audit - 2026-02-27 v2
Tests pay-test-sandbox-2 vs pay-test-2 for OAuth/birth button behavior.
Walks through the FULL chat flow to reach the OAuth trigger point.

Key patterns from memory:
- Password: PureBrain.ai253443$$$
- Chat flow: "Begin" btn -> name -> email -> company -> role -> birth/start fires
- Bypass: use the sandbox bypass button (#pb-sandbox-bypass-btn) if present,
  or type 'pb-full-bypass' in the ORDER CODE input that appears after paying
- PTC loads when payment is verified (or bypassed)
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

PASSWORD = "PureBrain.ai253443$$$"
BASE = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-audit-20260227-v2")
BASE.mkdir(parents=True, exist_ok=True)

PAGES = [
    {
        "name": "pay-test-sandbox-2",
        "url": "https://purebrain.ai/pay-test-sandbox-2/",
        "slug": "sandbox2",
    },
    {
        "name": "pay-test-2",
        "url": "https://purebrain.ai/pay-test-2/",
        "slug": "paytest2",
    },
]


async def ss(page, slug, label):
    path = str(BASE / f"{slug}-{label}.png")
    await page.screenshot(path=path, full_page=False, clip={"x": 0, "y": 0, "width": 1280, "height": 900})
    print(f"  [SS] {slug}-{label}.png")
    return path


async def ss_full(page, slug, label):
    path = str(BASE / f"{slug}-{label}-full.png")
    await page.screenshot(path=path, full_page=True)
    print(f"  [SS-FULL] {slug}-{label}-full.png")
    return path


async def test_page(browser, cfg):
    slug = cfg["slug"]
    name = cfg["name"]
    url = cfg["url"]

    print(f"\n{'=' * 60}")
    print(f" {name}")
    print(f"{'=' * 60}")

    ctx = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        ignore_https_errors=True,
    )
    page = await ctx.new_page()

    console = []
    page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
    page.on("pageerror", lambda e: console.append({"type": "pageerror", "text": str(e)}))

    # --- STEP 1: Load page ---
    print("[1] Loading page...")
    resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(4000)
    print(f"    HTTP: {resp.status}")
    await ss(page, slug, "01-initial")

    # --- STEP 2: Enter WP password ---
    pw_input = await page.query_selector('input[name="post_password"]')
    if pw_input:
        print("[2] WP password form found — entering password...")
        await pw_input.fill(PASSWORD)
        submit = await page.query_selector('input[type="submit"]')
        if submit:
            await submit.click()
        await page.wait_for_timeout(5000)
        print(f"    Page title after PW: {await page.title()}")
        await ss(page, slug, "02-after-password")
    else:
        print("[2] No WP password form — page may be public")

    # --- STEP 3: Source analysis ---
    print("[3] Analyzing page source...")
    indicators = await page.evaluate("""() => {
        const body = document.body.innerHTML;
        const text = document.body.innerText;
        return {
            has_ptc_wrapper: body.includes('ptc-wrapper') || body.includes('ptcWrapper'),
            has_birth_init: body.includes('runBirthInit') || body.includes('birth/start'),
            has_witness: body.includes('WITNESS') || body.includes('witness'),
            has_chat_widget: body.includes('chat-initial') || body.includes('chatbox'),
            has_sandbox_bypass: body.includes('pb-sandbox-bypass') || body.includes('pb-full-bypass'),
            has_paypal: body.includes('paypal') || body.includes('PayPal'),
            has_oauth: body.includes('oauth') || body.includes('OAuth'),
            has_begin_btn: !!document.querySelector('.chat-initial__btn'),
            chat_section_visible: (() => {
                const s = document.querySelector('.chat-section, #awakening');
                return s ? s.offsetHeight > 0 : false;
            })(),
            body_length: body.length,
        };
    }""")
    print(f"    Source indicators: {json.dumps(indicators, indent=4)}")

    await ss_full(page, slug, "03-full-page")

    # --- STEP 4: Click Begin button ---
    print("[4] Looking for Begin/Start button...")
    begin_btn = await page.query_selector(".chat-initial__btn, button.chat-btn, [class*=chat-initial]")
    if begin_btn:
        print("    Found Begin button — clicking...")
        await page.evaluate("el => el.scrollIntoView({block: 'center'})", begin_btn)
        await page.wait_for_timeout(1000)
        await ss(page, slug, "04-before-begin")
        await begin_btn.click()
        await page.wait_for_timeout(3000)
        await ss(page, slug, "05-after-begin")
        print("    Begin button clicked")
    else:
        print("    No Begin button found — checking for visible chat input...")

    # --- STEP 5: Fill chat questionnaire (name, email, company, role) ---
    print("[5] Filling chat questionnaire...")

    async def send_chat_message(text, step_name):
        """Type in chat input and submit"""
        # Try multiple selectors for chat input
        for selector in ["#userInput", "input#userInput", ".chat-input input", "[name=userInput]"]:
            inp = await page.query_selector(selector)
            if inp:
                is_visible = await inp.is_visible()
                if is_visible:
                    await inp.fill(text)
                    await page.wait_for_timeout(500)
                    # Press Enter or click send
                    await inp.press("Enter")
                    await page.wait_for_timeout(3000)
                    await ss(page, slug, step_name)
                    print(f"    Sent: '{text}' via {selector}")
                    return True
        print(f"    [WARN] Could not find visible chat input for step {step_name}")
        return False

    # Send name
    await send_chat_message("Test User", "06-name-entered")
    # Send email
    await send_chat_message("test@example.com", "07-email-entered")
    # Send company
    await send_chat_message("Test Company", "08-company-entered")
    # Send role (this triggers birth/start in v4.3.3)
    await send_chat_message("CEO", "09-role-entered")

    # Wait longer for birth/start to fire and complete/fail
    print("[5b] Waiting for birth/start API call + response...")
    await page.wait_for_timeout(8000)
    await ss(page, slug, "10-after-birth-attempt")

    # --- STEP 6: Look for OAuth button ---
    print("[6] Searching for OAuth button...")

    oauth_check = await page.evaluate("""() => {
        // Look for any OAuth/auth/birth-related buttons
        const allBtns = Array.from(document.querySelectorAll('button, a[role=button], .oauth-btn, [id*=oauth], [class*=oauth]'));
        const visible = allBtns.filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
        const chatMessages = Array.from(document.querySelectorAll('.chat-message, .message-bubble, [class*=message]'))
            .map(m => m.innerText.trim().substring(0, 200));

        // Get current ptc-wrapper state
        const ptcWrapper = document.querySelector('#ptc-wrapper, .ptc-wrapper');
        const retryBtn = document.querySelector('[onclick*=retry], [id*=retry], .retry-btn');
        const continueBtn = document.querySelector('[onclick*=continue], [id*=continue-without]');

        return {
            visible_buttons: visible.map(b => ({
                tag: b.tagName,
                id: b.id,
                class: b.className.substring(0, 80),
                text: b.innerText.trim().substring(0, 100),
                onclick: (b.getAttribute('onclick') || '').substring(0, 100),
            })),
            ptc_wrapper_exists: !!ptcWrapper,
            ptc_wrapper_display: ptcWrapper ? getComputedStyle(ptcWrapper).display : 'N/A',
            retry_btn_visible: retryBtn ? (retryBtn.offsetWidth > 0) : false,
            continue_btn_visible: continueBtn ? (continueBtn.offsetWidth > 0) : false,
            last_messages: chatMessages.slice(-5),
            chat_message_count: chatMessages.length,
        };
    }""")

    print(f"    OAuth check result:")
    print(f"      ptc_wrapper_exists: {oauth_check['ptc_wrapper_exists']}")
    print(f"      ptc_wrapper_display: {oauth_check['ptc_wrapper_display']}")
    print(f"      retry_btn_visible: {oauth_check['retry_btn_visible']}")
    print(f"      continue_btn_visible: {oauth_check['continue_btn_visible']}")
    print(f"      visible_button_count: {len(oauth_check['visible_buttons'])}")
    print(f"      last_messages:")
    for m in oauth_check.get("last_messages", []):
        print(f"        - {m[:120]}")

    print(f"      Visible buttons:")
    for b in oauth_check["visible_buttons"][:10]:
        print(f"        {b}")

    await ss(page, slug, "11-oauth-search-state")
    await ss_full(page, slug, "11-full")

    # --- STEP 7: Console error summary ---
    errors = [m for m in console if m["type"] in ("error", "warning", "pageerror")]
    birth_errors = [m for m in console if "birth" in m["text"].lower() or "witness" in m["text"].lower()]
    csp_errors = [m for m in console if "csp" in m["text"].lower() or "content security" in m["text"].lower() or "violates" in m["text"].lower()]
    oauth_errors = [m for m in console if "oauth" in m["text"].lower()]

    print(f"\n--- CONSOLE SUMMARY ({len(console)} total) ---")
    print(f"  Errors/warnings: {len(errors)}")
    print(f"  Birth/witness related: {len(birth_errors)}")
    print(f"  CSP violations: {len(csp_errors)}")
    print(f"  OAuth related: {len(oauth_errors)}")
    print(f"\n  All errors:")
    for m in errors[:20]:
        print(f"    [{m['type']}] {m['text'][:150]}")
    if birth_errors:
        print(f"\n  Birth errors:")
        for m in birth_errors[:10]:
            print(f"    [{m['type']}] {m['text'][:150]}")

    await ctx.close()

    return {
        "name": name,
        "http": resp.status,
        "indicators": indicators,
        "oauth_check": oauth_check,
        "errors": errors,
        "birth_errors": birth_errors,
        "csp_errors": csp_errors,
        "total_console": len(console),
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--ignore-certificate-errors"],
        )
        results = {}
        for cfg in PAGES:
            try:
                results[cfg["slug"]] = await test_page(browser, cfg)
            except Exception as e:
                print(f"ERROR testing {cfg['name']}: {e}")
                results[cfg["slug"]] = {"name": cfg["name"], "error": str(e)}

        await browser.close()

    # Final comparison
    print("\n\n" + "=" * 60)
    print(" FINAL COMPARISON")
    print("=" * 60)
    for slug, r in results.items():
        if "error" in r:
            print(f"\n{r['name']}: ERROR - {r['error']}")
            continue
        ind = r.get("indicators", {})
        oc = r.get("oauth_check", {})
        print(f"\n{r['name']}:")
        print(f"  HTTP: {r['http']}")
        print(f"  has_birth_init:  {ind.get('has_birth_init')}")
        print(f"  has_witness:     {ind.get('has_witness')}")
        print(f"  has_oauth:       {ind.get('has_oauth')}")
        print(f"  ptc_wrapper:     {oc.get('ptc_wrapper_exists')} / display={oc.get('ptc_wrapper_display')}")
        print(f"  retry_visible:   {oc.get('retry_btn_visible')}")
        print(f"  continue_visible:{oc.get('continue_btn_visible')}")
        print(f"  birth_errors:    {len(r.get('birth_errors', []))}")
        print(f"  csp_errors:      {len(r.get('csp_errors', []))}")
        print(f"  total_console:   {r.get('total_console', 0)}")

    print(f"\nScreenshots saved to: {BASE}")
    print("Done.")


asyncio.run(main())
