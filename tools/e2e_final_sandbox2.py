#!/usr/bin/env python3
"""
E2E Final: pay-test-sandbox-2 full flow audit
Date: 2026-03-02
No full_page screenshots (causes timeout with WebGL content)
"""

import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime

SESSION_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-live-sandbox2-20260302"
REPORT_PATH = "/home/jared/projects/AI-CIV/aether/exports/e2e-live-sandbox2-report-20260302.md"
os.makedirs(SESSION_DIR, exist_ok=True)

LIVE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

SEED_ENDPOINTS = [
    "104.248.239.98",
    "178.156.229.207",
    "api.purebrain.ai/api/intake",
    ":8099",
    ":8200",
]

sc = [0]
network_requests = []
console_all = []
page_errors = []
seed_fires = []


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def ss(label):
    sc[0] += 1
    return f"{SESSION_DIR}/{sc[0]:03d}-{label}.png"


def is_seed(url):
    return any(ep in url for ep in SEED_ENDPOINTS)


def classify(url):
    if ":8099" in url: return "BIRTH_WEBHOOK"
    if ":8200" in url: return "WITNESS_SEED"
    if "104.248" in url or "178.156" in url: return "WITNESS_DIRECT"
    if "api.purebrain.ai" in url: return "PUREBRAIN_API"
    if "paypal" in url.lower(): return "PAYPAL"
    if "workers.dev" in url: return "CF_WORKER"
    return "OTHER"


async def screenshot(page, label):
    path = ss(label)
    try:
        await page.screenshot(path=path, timeout=10000)
        log(f"SS: {path.split('/')[-1]}")
    except Exception as e:
        log(f"SS FAILED [{label}]: {e}")
    return path


async def main():
    from playwright.async_api import async_playwright

    log("=" * 60)
    log("E2E pay-test-sandbox-2 LIVE TEST")
    log("=" * 60)

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

        page.on("console", lambda m: console_all.append({
            "type": m.type, "text": m.text, "ts": datetime.now().strftime("%H:%M:%S")
        }))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        async def on_req(req):
            url = req.url
            entry = {
                "ts": datetime.now().strftime("%H:%M:%S"),
                "method": req.method,
                "url": url[:200],
                "type": classify(url),
                "is_seed": is_seed(url),
            }
            if entry["is_seed"]:
                log(f"*** SEED FIRE: {req.method} {url[:120]} ***")
                try:
                    pd = await req.post_data()
                    if pd:
                        entry["payload"] = pd[:1200]
                except Exception:
                    pass
                seed_fires.append(entry)
            elif entry["type"] in ["BIRTH_WEBHOOK", "WITNESS_SEED", "WITNESS_DIRECT", "PUREBRAIN_API", "CF_WORKER"]:
                log(f"  [{entry['type']}] {req.method} {url[:80]}")
            network_requests.append(entry)

        page.on("request", on_req)

        # ---- Phase 0: Load ----
        log("\n--- Phase 0: Load page ---")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        await screenshot(page, "p0-load")

        # ---- Phase 1: Password ----
        pw_inp = await page.query_selector('input[name="post_password"]')
        if pw_inp:
            log("\n--- Phase 1: Password unlock ---")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            log("Waiting for unlock (10s)...")
            await asyncio.sleep(10)
            await screenshot(page, "p1-after-pw")

            pw_check = await page.evaluate("""() => ({
                url: window.location.href,
                begin_btn: !!document.querySelector(".chat-initial__btn"),
                captcha: document.body.innerText.includes("verify you are human"),
            })""")
            log(f"Post-pw: {json.dumps(pw_check)}")

            if pw_check.get("captcha"):
                log("[CRITICAL] WAF CAPTCHA - cannot proceed")
                await ctx.close()
                await browser.close()
                return

        # ---- Phase 2: Pre-payment chat ----
        log("\n--- Phase 2: Pre-payment chat ---")
        await asyncio.sleep(5)
        await screenshot(page, "p2-pre-chat")

        begin_btn = await page.query_selector(".chat-initial__btn")
        log(f"Begin btn: {begin_btn is not None}")

        if begin_btn:
            await page.evaluate("document.querySelector('.chat-initial__btn').click()")
            log("Clicked Begin Awakening")
            await asyncio.sleep(4)
            await screenshot(page, "p2a-after-begin")

            # Bypass code
            await page.evaluate("""
                var inp = document.getElementById('userInput');
                if (inp) {
                    inp.value = 'pb-full-bypass';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
            """)
            await asyncio.sleep(0.3)
            await page.evaluate("""
                var sub = document.getElementById('submitBtn');
                if (sub) { sub.click(); }
                else {
                    var f = document.querySelector('.chat-input__form');
                    if (f) f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
                }
            """)
            log("Bypass code 'pb-full-bypass' sent")
            await asyncio.sleep(6)
            await screenshot(page, "p2b-after-bypass")

            bypass = await page.evaluate("""() => {
                var msgs = document.querySelectorAll(".message--ai");
                var procta = document.getElementById("proCta");
                return {
                    ai_msgs: msgs.length,
                    last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                    procta_text: procta ? procta.innerText.trim() : null,
                };
            }""")
            log(f"Bypass state: {json.dumps(bypass)}")

        # ---- Phase 3: Payment ----
        log("\n--- Phase 3: Payment trigger ---")

        # Click #proCta via JS
        procta_result = await page.evaluate("""() => {
            var el = document.getElementById("proCta");
            if (!el) return "not found";
            el.click();
            return "clicked: " + el.innerText.trim();
        }""")
        log(f"#proCta: {procta_result}")
        await asyncio.sleep(4)
        await screenshot(page, "p3a-after-procta")

        # Check for sandbox bypass btn and PayPal modal
        modal = await page.evaluate("""() => {
            var sb = document.getElementById("pb-sandbox-bypass-btn");
            var overlay = document.getElementById("pb-paypal-overlay");
            var wm = document.getElementById("waitlistModal");
            return {
                sandbox_btn: sb ? {exists: true, text: sb.innerText.trim(), visible: window.getComputedStyle(sb).display !== "none"} : null,
                overlay_active: overlay ? overlay.classList.contains("pb-active") : false,
                waitlist_active: wm ? wm.classList.contains("active") : false,
                openPayPalModal_type: typeof window.openPayPalModal,
            };
        }""")
        log(f"Payment modal state: {json.dumps(modal)}")

        if not modal.get("sandbox_btn"):
            log("No sandbox btn - opening PayPal modal via JS")
            open_result = await page.evaluate("""() => {
                if (typeof window.openPayPalModal === "function") {
                    window.openPayPalModal("Awakened");
                    return "openPayPalModal(Awakened)";
                }
                if (typeof window.openWaitlistModal === "function") {
                    window.openWaitlistModal("Awakened");
                    return "openWaitlistModal(Awakened)";
                }
                return "no modal fn";
            }""")
            log(f"Modal open: {open_result}")
            await asyncio.sleep(3)

        await screenshot(page, "p3b-modal-open")

        # Click sandbox bypass btn
        sandbox_exists = await page.evaluate("""!!document.getElementById("pb-sandbox-bypass-btn")""")
        log(f"Sandbox bypass btn exists: {sandbox_exists}")

        if sandbox_exists:
            seeds_before = len(seed_fires)
            await page.evaluate("""
                var btn = document.getElementById("pb-sandbox-bypass-btn");
                if (btn) btn.click();
            """)
            log("Clicked sandbox bypass (simulating payment)")
            await asyncio.sleep(8)
            seeds_after = len(seed_fires)
            log(f"Seeds fired by payment: {seeds_after - seeds_before}")

            for sf in seed_fires[seeds_before:]:
                log(f"  Seed: {sf['type']} {sf['url'][:80]}")

            await screenshot(page, "p3c-after-payment-bypass")

        # ---- Phase 4: Post-payment chat ----
        log("\n--- Phase 4: Post-payment chatbox ---")
        await asyncio.sleep(5)

        ptc = await page.evaluate("""() => {
            var w = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
            var msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            return {
                exists: !!w,
                visible: w ? window.getComputedStyle(w).display !== "none" : false,
                msg_count: msgs.length,
                first_msg: msgs.length > 0 ? msgs[0].innerText.substring(0, 200) : null,
                last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
            };
        }""")
        log(f"Post-payment chatbox: {json.dumps(ptc)}")
        await screenshot(page, "p4a-ptc-initial")

        final_ptc = ptc  # will be updated

        if ptc.get("exists") and ptc.get("visible"):
            log("POST-PAYMENT CHATBOX IS LIVE")

            async def get_cnt():
                return await page.evaluate("""document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai").length""")

            async def get_last():
                return await page.evaluate("""() => {
                    var m = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                    return m.length > 0 ? m[m.length-1].innerText.trim() : "";
                }""")

            async def wait_msg(prev, timeout=25):
                deadline = time.time() + timeout
                while time.time() < deadline:
                    if await get_cnt() > prev:
                        await asyncio.sleep(2)
                        return True
                    await asyncio.sleep(0.5)
                return False

            async def send_msg(text):
                r = await page.evaluate(f"""() => {{
                    var inps = Array.from(document.querySelectorAll("textarea, .ptc-input")).filter(
                        i => window.getComputedStyle(i).display !== "none"
                    );
                    if (!inps.length) return "no input";
                    inps[0].value = {json.dumps(text)};
                    inps[0].dispatchEvent(new Event("input", {{bubbles: true}}));
                    var send = document.querySelector("button.ptc-send-btn, .ptc-send");
                    if (send) {{ send.click(); return "button"; }}
                    inps[0].dispatchEvent(new KeyboardEvent("keydown", {{key: "Enter", bubbles: true}}));
                    return "enter";
                }}""")
                log(f"  Sent '{text}': {r}")
                return r

            async def click_primary():
                return await page.evaluate("""() => {
                    var btns = Array.from(document.querySelectorAll(".ptc-btn.ptc-btn--primary, .ptc-btn--primary")).filter(
                        b => b.offsetHeight > 0 && window.getComputedStyle(b).display !== "none"
                    );
                    if (btns.length) { btns[0].click(); return btns[0].innerText.trim(); }
                    return null;
                }""")

            # v4.9 Claude Max check
            last = ptc.get("last_msg", "") or ""
            if "Claude Max" in last or "claude.ai" in last.lower() or "Max account" in last:
                log("Claude Max check (v4.9) - clicking Yes")
                prev = await get_cnt()
                await page.evaluate("""() => {
                    var btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    var yes = btns.find(b => b.innerText.includes("Yes") && !b.innerText.includes("No"));
                    if (yes) { yes.click(); return; }
                    var primary = document.querySelector(".ptc-btn.ptc-btn--primary");
                    if (primary) primary.click();
                }""")
                await wait_msg(prev)
                last = await get_last()
                log(f"After Claude Max: {last[:80]}")

            # Q1 Name
            prev = await get_cnt()
            await send_msg("Alex TestUser")
            await wait_msg(prev)
            await screenshot(page, "p4b-q1-name")

            # Q2 Email
            prev = await get_cnt()
            await send_msg("alex@testcompany.com")
            await wait_msg(prev)
            await screenshot(page, "p4c-q2-email")

            # Q3 Company
            prev = await get_cnt()
            await send_msg("TestCo Industries")
            await wait_msg(prev)
            await screenshot(page, "p4d-q3-company")

            # Q4 Role (auto birth init v4.5+)
            seeds_before_q4 = len(seed_fires)
            prev = await get_cnt()
            await send_msg("CEO")
            await wait_msg(prev)
            await asyncio.sleep(10)
            seeds_after_q4 = len(seed_fires)
            log(f"Seeds from Q4/birth auto-fire: {seeds_after_q4 - seeds_before_q4}")
            await screenshot(page, "p4e-q4-role")

            last = await get_last()
            log(f"After Q4: {last[:150]}")

            # Check for manual birth btn
            birth_clicked = await page.evaluate("""() => {
                var btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                var m = btns.find(b => b.innerText.includes("Birth") || b.innerText.includes("Start AI"));
                if (m) { m.click(); return m.innerText.trim(); }
                return null;
            }""")
            if birth_clicked:
                log(f"Manual birth btn: '{birth_clicked}'")
                await asyncio.sleep(8)
                await screenshot(page, "p4f-after-birth")

            # Q5 Primary Goal
            last = await get_last()
            log(f"Current: {last[:120]}")
            if any(x in last.lower() for x in ["goal", "one thing", "exceptionally", "what would it"]):
                prev = await get_cnt()
                await send_msg("Automate my business operations and free up time")
                await wait_msg(prev)
                await screenshot(page, "p4g-q5-goal")

            # Slides
            log("Navigating slides...")
            for i in range(15):
                await asyncio.sleep(1)
                txt = await click_primary()
                if txt is None:
                    log(f"  No primary btn at slide {i}")
                    break
                log(f"  Slide {i}: '{txt}'")
                if any(x in txt.lower() for x in ["let's go", "incredible", "keep going", "connection established"]):
                    await asyncio.sleep(2)
                    break
            await screenshot(page, "p4h-after-slides")

            # Telegram
            last = await get_last()
            log(f"After slides: {last[:100]}")
            if "Telegram" in last:
                await page.evaluate("""() => {
                    var btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    var yes = btns.find(b => b.innerText.includes("Yes") && b.innerText.includes("Telegram"));
                    if (yes) yes.click();
                }""")
                await asyncio.sleep(4)

            await screenshot(page, "p4i-pre-learn")

            # Learn more (starts portal watcher)
            learn = await page.evaluate("""() => {
                var btns = Array.from(document.querySelectorAll("button, .ptc-btn, a.ptc-btn"));
                var b = btns.find(b => b.innerText.toLowerCase().includes("learn more"));
                if (b) { b.click(); return b.innerText.trim(); }
                return null;
            }""")
            if learn:
                log(f"Clicked 'Learn more': '{learn}'")
                await asyncio.sleep(3)

        else:
            log("Post-payment chatbox not visible - trying initPayTestFlow directly")
            result = await page.evaluate("""() => {
                if (typeof window.initPayTestFlow === "function") {
                    try {
                        window.initPayTestFlow({aiName: "Keen", tier: "Awakened", orderId: "e2e-test-001"});
                        return "called";
                    } catch(e) { return "error: " + e.message; }
                }
                return "not found";
            }""")
            log(f"initPayTestFlow: {result}")
            await asyncio.sleep(5)
            await screenshot(page, "p4-debug-init")

        # ---- Phase 5: Portal button + Seed 3 ----
        log("\n--- Phase 5: Portal monitoring ---")

        portal_found = False
        for i in range(8):
            await asyncio.sleep(5)
            portal_check = await page.evaluate("""() => {
                var btn = document.querySelector(".ptc-portal-btn, a[href*='portal']");
                var msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                return {
                    portal: btn ? {href: btn.href || btn.getAttribute("href"), text: btn.innerText.substring(0, 80)} : null,
                    msg_count: msgs.length,
                    last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 300) : null,
                };
            }""")
            msg_cnt = portal_check.get("msg_count", 0)
            log(f"  [Check {i+1}] Portal: {portal_check.get('portal')}, msgs: {msg_cnt}")
            if portal_check.get("last_msg"):
                log(f"  Last msg: {portal_check['last_msg'][:100]}")

            if portal_check.get("portal"):
                log("PORTAL BUTTON APPEARED!")
                await screenshot(page, "p5-portal-found")
                portal_found = True
                break
            if i % 2 == 0:
                await screenshot(page, f"p5-wait-{i+1}")

        # Final
        await screenshot(page, "FINAL")
        final = await page.evaluate("""() => {
            var msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            var allMsgs = Array.from(msgs).map(m => m.innerText.trim().substring(0, 200));
            return {
                total_ptc_msgs: msgs.length,
                last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 400) : null,
                portal_btn: !!document.querySelector(".ptc-portal-btn"),
                welcome_card: document.body.innerText.includes("Welcome to the Family"),
                all_msgs_preview: allMsgs.slice(0, 5),
            };
        }""")
        log(f"FINAL: {json.dumps(final, indent=2)}")

        await ctx.close()
        await browser.close()

    # ---- Summary ----
    log("\n" + "=" * 60)
    log("SEED FIRE SUMMARY")
    log("=" * 60)
    log(f"Total seed fires: {len(seed_fires)}")
    for i, sf in enumerate(seed_fires, 1):
        log(f"\n  Seed #{i}:")
        log(f"    Time: {sf['ts']}")
        log(f"    Type: {sf['type']}")
        log(f"    URL:  {sf['url']}")
        log(f"    Method: {sf['method']}")
        if "payload" in sf:
            try:
                payload = json.loads(sf["payload"])
                log(f"    Event: {payload.get('metadata', {}).get('event_type', '?')}")
                log(f"    Stage: {payload.get('metadata', {}).get('stage', '?')}")
                log(f"    Human: {payload.get('human', {})}")
                log(f"    AI name: {payload.get('ai_identity', {}).get('name', '?')}")
                log(f"    Tier: {payload.get('metadata', {}).get('tier', '?')}")
                log(f"    Container: {payload.get('metadata', {}).get('containerName', '?')}")
                log(f"    Conv history: {len(payload.get('conversation_history', []))} messages")
            except Exception as e:
                log(f"    Payload (raw, parse failed: {e}): {sf['payload'][:400]}")

    errors = [c for c in console_all if c["type"] == "error"]
    pb_logs = [c for c in console_all if any(x in c["text"].lower() for x in
               ["seed", "witness", "birth", "webhook", "paypal", "ptc", "bypass",
                "fireseed", "purebrain api", "intake", "openPayPalModal"])]

    log("\n" + "=" * 60)
    log("CONSOLE SUMMARY")
    log("=" * 60)
    log(f"Total: {len(console_all)}, Errors: {len(errors)}, PB-related: {len(pb_logs)}")
    if errors:
        log("Errors:")
        for e in errors[:15]:
            log(f"  [{e['ts']}] {e['text'][:200]}")
    if pb_logs:
        log("PureBrain logs:")
        for l in pb_logs[:30]:
            log(f"  [{l['ts']}] {l['text'][:200]}")

    all_ss = sorted(Path(SESSION_DIR).glob("*.png"))
    log(f"\nScreenshots: {len(all_ss)}")
    log("=" * 60)

    # Write report
    lines = [
        "# E2E Pay-Test-Sandbox-2 Live Audit",
        "",
        f"**Date**: 2026-03-02",
        f"**Version**: v4.9 (Claude Max check + 3-stage seed firing)",
        f"**URL**: {LIVE_URL}",
        "",
        "---",
        "",
        "## Seed Fire Results",
        f"**Total seeds fired**: {len(seed_fires)}",
        "",
    ]

    if seed_fires:
        for i, sf in enumerate(seed_fires, 1):
            lines.append(f"### Seed #{i}: {sf['type']}")
            lines.append(f"- **Time**: {sf['ts']}")
            lines.append(f"- **URL**: `{sf['url']}`")
            lines.append(f"- **Method**: {sf['method']}")
            if "payload" in sf:
                try:
                    p = json.loads(sf["payload"])
                    lines.append(f"- **Event**: `{p.get('metadata', {}).get('event_type', '?')}` (Stage {p.get('metadata', {}).get('stage', '?')})")
                    lines.append(f"- **Human**: name=`{p.get('human', {}).get('name', '?')}` email=`{p.get('human', {}).get('email', '?')}`")
                    lines.append(f"- **AI name**: `{p.get('ai_identity', {}).get('name', '?')}`")
                    lines.append(f"- **Tier**: `{p.get('metadata', {}).get('tier', '?')}`")
                    lines.append(f"- **Container**: `{p.get('metadata', {}).get('containerName', '?')}`")
                    lines.append(f"- **Conv history**: {len(p.get('conversation_history', []))} messages")
                except Exception:
                    lines.append(f"- **Payload**: `{sf['payload'][:400]}`")
            lines.append("")
    else:
        lines.append("**NO SEED FIRES DETECTED**")
        lines.append("")
        lines.append("Note: Seeds fire to external HTTP endpoints from the browser.")
        lines.append("If the Witness endpoint is down or unreachable, seeds may fail silently.")
        lines.append("")

    lines.extend([f"## Console Errors ({len(errors)})", ""])
    for e in errors[:15]:
        lines.append(f"- `{e['text'][:200]}`")

    lines.extend(["", f"## PureBrain Logs ({len(pb_logs)})", ""])
    for l in pb_logs[:20]:
        lines.append(f"- `[{l['ts']}] {l['text'][:200]}`")

    lines.extend([
        "",
        "## Final State",
        "```json",
        json.dumps(final, indent=2),
        "```",
        "",
        f"## Screenshots ({len(all_ss)})",
        f"Location: `{SESSION_DIR}/`",
        "",
    ])
    for ss_f in all_ss:
        lines.append(f"- `{ss_f.name}`")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
    log(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
