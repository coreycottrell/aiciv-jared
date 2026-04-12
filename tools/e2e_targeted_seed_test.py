#!/usr/bin/env python3
"""
Targeted seed fire detection test
Date: 2026-03-02
"""
import asyncio
import json
import time
from datetime import datetime

LIVE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

all_reqs = []
console_logs = []

def ts():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
    print(f"[{ts()}] {msg}", flush=True)


async def targeted_test():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"
        )
        page = await ctx.new_page()

        page.on("console", lambda m: console_logs.append({
            "t": m.type, "text": m.text, "ts": ts()
        }))

        async def on_req(req):
            url = req.url
            notable = any(x in url for x in [
                "api.purebrain", "intake", "seed", "birth", "verify-payment",
                "8099", "8200", "104.248", "178.156"
            ])
            if notable:
                log(f"NOTABLE REQ: {req.method} {url[:150]}")
                try:
                    pd = await req.post_data()
                    if pd:
                        log(f"  Payload ({len(pd)}): {pd[:300]}")
                        all_reqs.append({
                            "method": req.method,
                            "url": url[:200],
                            "payload": pd[:800],
                            "ts": ts()
                        })
                except Exception:
                    pass
            else:
                all_reqs.append({"method": req.method, "url": url[:200]})

        page.on("request", on_req)

        # Load
        log("Loading page...")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Password
        pw = await page.query_selector('input[name="post_password"]')
        if pw:
            await pw.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw.press("Enter")
            log("Password submitted, waiting 10s...")
            await asyncio.sleep(10)

        await asyncio.sleep(5)

        # Check initial state
        state = await page.evaluate("""() => ({
            begin: !!document.querySelector(".chat-initial__btn"),
            openPayPalModal_type: typeof window.openPayPalModal,
            openPayPalCheckout_type: typeof window.openPayPalCheckout,
            initPayTestFlow_type: typeof window.initPayTestFlow,
        })""")
        log(f"Initial state: {json.dumps(state)}")

        # Click Begin Awakening
        await page.evaluate("var b = document.querySelector('.chat-initial__btn'); if(b) b.click();")
        log("Clicked Begin Awakening")
        await asyncio.sleep(3)

        # Bypass code
        await page.evaluate("""
            var i = document.getElementById('userInput');
            if (i) {
                i.value = 'pb-full-bypass';
                i.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var s = document.getElementById('submitBtn');
            if (s) s.click();
        """)
        log("Sent bypass code")
        await asyncio.sleep(6)

        bypass_state = await page.evaluate("""() => ({
            ai_msgs: document.querySelectorAll(".message--ai").length,
            procta_exists: !!document.getElementById("proCta"),
            procta_text: document.getElementById("proCta") ? document.getElementById("proCta").innerText : null,
        })""")
        log(f"After bypass: {json.dumps(bypass_state)}")

        # Click proCta
        click_result = await page.evaluate("""() => {
            var el = document.getElementById("proCta");
            if (!el) return "not found";
            el.click();
            return "clicked: " + el.innerText;
        }""")
        log(f"proCta click: {click_result}")
        await asyncio.sleep(5)

        # Check modal state
        modal = await page.evaluate("""() => {
            var overlay = document.getElementById("pb-paypal-overlay");
            var sb = document.getElementById("pb-sandbox-bypass-btn");
            return {
                overlay_active: overlay ? overlay.classList.contains("pb-active") : false,
                overlay_display: overlay ? window.getComputedStyle(overlay).display : "not_found",
                sandbox_btn: sb ? {exists: true, visible: window.getComputedStyle(sb).display !== "none", text: sb.innerText} : {exists: false},
            };
        }""")
        log(f"Modal after proCta: {json.dumps(modal)}")

        # If modal not open, force open it
        if not modal.get("overlay_active"):
            log("Overlay not active, calling openPayPalModal directly...")
            r = await page.evaluate("""() => {
                if (typeof window.openPayPalModal === 'function') {
                    window.openPayPalModal('Awakened');
                    return 'openPayPalModal called';
                }
                if (typeof window.openPayPalCheckout === 'function') {
                    window.openPayPalCheckout('Awakened');
                    return 'openPayPalCheckout called';
                }
                return 'no fn';
            }""")
            log(f"Modal call: {r}")
            await asyncio.sleep(3)

        # Re-check sandbox btn
        sb_check = await page.evaluate("""() => {
            var sb = document.getElementById("pb-sandbox-bypass-btn");
            if (!sb) return {exists: false};
            return {
                exists: true,
                visible: window.getComputedStyle(sb).display !== "none",
                text: sb.innerText.trim()
            };
        }""")
        log(f"Sandbox btn: {json.dumps(sb_check)}")

        if sb_check.get("exists") and sb_check.get("visible"):
            log("CLICKING SANDBOX BYPASS BTN")
            await page.evaluate("""
                var btn = document.getElementById("pb-sandbox-bypass-btn");
                if (btn) btn.click();
            """)
            log("Waiting 15s for seed fires...")
            await asyncio.sleep(15)

            # Check ptc
            ptc = await page.evaluate("""() => {
                var w = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
                var msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                return {
                    ptc_exists: !!w,
                    ptc_visible: w ? window.getComputedStyle(w).display !== "none" : false,
                    msg_count: msgs.length,
                    last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                    paymentConfirmed: window.paymentConfirmed,
                    paymentTier: window.paymentTier,
                };
            }""")
            log(f"PTC state after bypass: {json.dumps(ptc)}")

        else:
            log("Sandbox btn not found or not visible - trying launchPostPaymentFlow directly")
            r = await page.evaluate("""() => {
                if (typeof launchPostPaymentFlow === 'function') {
                    launchPostPaymentFlow('Awakened');
                    return 'called launchPostPaymentFlow';
                }
                if (typeof window.initPayTestFlow === 'function') {
                    var container = document.createElement('div');
                    container.id = 'pay-test-post-payment';
                    container.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;background:#0a0a0a;display:flex;flex-direction:column;padding:7.5% 12%;box-sizing:border-box;';
                    document.body.appendChild(container);
                    window.initPayTestFlow(container, 'Keen', 'Awakened');
                    return 'called initPayTestFlow directly';
                }
                return 'no fn found';
            }""")
            log(f"Direct launch: {r}")
            await asyncio.sleep(10)

            ptc = await page.evaluate("""() => {
                var w = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
                var msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                return {
                    ptc_exists: !!w,
                    ptc_visible: w ? window.getComputedStyle(w).display !== "none" : false,
                    msg_count: msgs.length,
                    last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                };
            }""")
            log(f"PTC state after direct launch: {json.dumps(ptc)}")

        # PB logs
        pb_logs = [c for c in console_logs if any(x in c["text"].lower() for x in [
            "paypal", "payment", "seed", "witness", "birth", "bypass", "ptc",
            "verify", "awaken", "purebrain", "[pb", "intake", "fireseed"
        ])]
        log(f"\nPB console logs ({len(pb_logs)}):")
        for l in pb_logs[:40]:
            log(f"  [{l['ts']}][{l['t']}] {l['text'][:200]}")

        # Notable requests
        notable = [r for r in all_reqs if "payload" in r]
        log(f"\nNotable requests with payload ({len(notable)}):")
        for r in notable:
            log(f"  [{r['ts']}] {r['method']} {r['url'][:120]}")
            try:
                p = json.loads(r["payload"])
                log(f"    type: {p.get('type')}")
                log(f"    event: {p.get('metadata', {}).get('event_type')}")
                log(f"    stage: {p.get('metadata', {}).get('stage')}")
                log(f"    human: {p.get('human')}")
                log(f"    conv_len: {len(p.get('conversation_history', []))}")
            except Exception:
                log(f"    raw: {r['payload'][:300]}")

        await ctx.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(targeted_test())
