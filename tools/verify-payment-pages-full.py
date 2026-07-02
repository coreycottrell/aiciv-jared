#!/usr/bin/env python3
# =============================================================================
# verify-payment-pages-full.py
# -----------------------------------------------------------------------------
# STAGED (2026-07-02) — additive overnight money-path probe. NOT activated.
#
# WHY THIS EXISTS (the regression class it catches):
#   A checkout page can return HTTP 200 while (a) its PayPal/Stripe button never
#   renders, or (b) the naming-conversation logging path silently diverges from
#   the store the seed is read from — producing EMPTY SEEDS. That second class
#   rotted ~5 weeks unnoticed because the old nightly probe asserted only "200".
#   This probe asserts THREE things per money-path page:
#
#     (A) PAGE LOADS         — HTTP 200 via GET (CF Pages 404s on HEAD).
#     (B) CHECKOUT IS LIVE    — the PayPal SDK button AND/OR the Stripe embedded
#                               checkout element is actually WIRED (script/element
#                               detected in served HTML; or, in --render mode, the
#                               live DOM element/iframe is asserted for JS-rendered
#                               React pages that curl is blind to).
#     (C) CONVERSATION-LOGGING WITH IDENTITY-LINKAGE WORKS —
#         a SYNTHETIC naming-conversation is captured with a unique test
#         sessionUuid, then we confirm it (1) PERSISTS to the SAME store the seed
#         is read from (logs/purebrain_web_conversations.jsonl) and (2) is
#         STRONG-KEY findable by that sessionUuid — i.e. a strict
#         _lookup_naming_conversation-style S2 lookup would bind it. If the
#         frontend->store->seed path is broken, THIS FAILS the night it happens.
#
# This is ADDITIVE. It does NOT replace or weaken:
#   - tools/verify-payment-pages.sh                 (live pricing / banned-ID gate)
#   - tools/verify-payment-pages-pbsessionuuid.sh   (static pbSessionUuid gate)
#
# SAFETY (no real seed / no real payment / no live customer touched):
#   - The synthetic sessionUuid is prefixed  BOOP-SYNTH-  and carries NO orderId,
#     NO payer email in content, and a NON-payment page_url. By construction it
#     can NEVER be bound to any real order by the seed lookup:
#         S0(account_id) — we send none          -> unreachable
#         S1(orderId)    — we send none          -> unreachable
#         S2(sessionUuid)— BOOP-SYNTH-<uuid4>    -> only matches ITSELF
#         S3(email)      — no email in content   -> unreachable
#         S4(recency)    — non-payment page_url + 4 msgs (needs payment URL +
#                          >5 msgs) -> unreachable on TWO counts
#   - The probe NEVER calls /api/verify-payment, /api/send-seed,
#     /api/finish-wakeup, or /api/create-checkout-session. It only exercises the
#     conversation-LOG write path and a read-only replica of the lookup.
#   - --dry-run writes the synthetic record to a TEMP COPY of the store, never to
#     the production file, and runs the lookup against that copy (CI-safe).
#
# EXIT CODES:  0 = all assertions passed;  1 = at least one FAIL.
#
# USAGE:
#   tools/verify-payment-pages-full.py                 # full run (POSTs synth to
#                                                      # live endpoint, polls store)
#   tools/verify-payment-pages-full.py --render        # + browser DOM assertion
#                                                      #   for JS-rendered pages
#   tools/verify-payment-pages-full.py --dry-run       # no network POST; temp-copy
#                                                      #   store; logic self-test
#   tools/verify-payment-pages-full.py --no-alert      # never call portal_deliver
#
# ENV:
#   LOG_ENDPOINT   default https://api.purebrain.ai/api/log-conversation
#   STORE_PATH     default <repo>/logs/purebrain_web_conversations.jsonl
#   PORTAL_ALERT   default 1 (0 disables portal delivery on failure)
#   PERSIST_WAIT_S default 20 (seconds to poll store for the synthetic record)
# =============================================================================

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEFAULT_STORE = os.path.join(REPO_ROOT, "logs", "purebrain_web_conversations.jsonl")
LOG_ENDPOINT = os.environ.get("LOG_ENDPOINT", "https://api.purebrain.ai/api/log-conversation")
STORE_PATH = os.environ.get("STORE_PATH", DEFAULT_STORE)
PORTAL_DELIVER = os.path.join(REPO_ROOT, "tools", "portal_deliver.sh")
PERSIST_WAIT_S = int(os.environ.get("PERSIST_WAIT_S", "20"))

# ANSI
R = "\033[0;31m"; G = "\033[0;32m"; Y = "\033[0;33m"; NC = "\033[0m"

# -----------------------------------------------------------------------------
# PAGE CONFIG — the 9 money-path pages.
#   gate:  human-readable gate context (code / ?ref / ?aid / open). The checkout
#          markers on the gated pages live in the served HTML regardless of the
#          client-side gate, so curl grep reaches the checkout wiring without
#          "unlocking". In --render mode the gate_code is typed into the gate.
#   rails: which checkout rails MUST be detected for this page. "paypal" and/or
#          "stripe". A page passes (B) if ANY of its required rails is detected
#          (a page can be PayPal-only). Missing an OPTIONAL rail is INFO only.
#   js_rendered: True for Next.js/React pages where the button is injected client
#          side and curl is blind. In fast mode these are INFO (not FAIL); in
#          --render mode they are asserted against the live DOM.
#   pending: True = future page, skip until live (one-line flip to activate).
# -----------------------------------------------------------------------------
PAGES = [
    {
        "id": 1, "name": "/awakening/", "url": "https://purebrain.ai/awakening/",
        "gate": "open", "gate_code": None,
        "rails": ["paypal", "stripe"], "js_rendered": True, "pending": False,
    },
    {
        "id": 2, "name": "/insiders/", "url": "https://purebrain.ai/insiders/",
        "gate": "code:PureBrainInviteOnly26+", "gate_code": "PureBrainInviteOnly26+",
        "rails": ["paypal", "stripe"], "js_rendered": False, "pending": False,
    },
    {
        "id": 3, "name": "/old-pricing/", "url": "https://purebrain.ai/old-pricing/",
        "gate": "code:oldpricing2026", "gate_code": "oldpricing2026",
        "rails": ["paypal", "stripe"], "js_rendered": False, "pending": False,
    },
    {
        "id": 4, "name": "/tiers/", "url": "https://purebrain.ai/tiers/",
        "gate": "code:puretiers2026", "gate_code": "puretiers2026",
        "rails": ["paypal", "stripe"], "js_rendered": False, "pending": False,
    },
    {
        "id": 5, "name": "/partnered-how-this-levels-you-up/",
        "url": "https://purebrain.ai/partnered-how-this-levels-you-up/",
        "gate": "open", "gate_code": None,
        "rails": ["paypal", "stripe"], "js_rendered": False, "pending": False,
    },
    {
        "id": 6, "name": "/unified-how-this-levels-you-up/",
        "url": "https://purebrain.ai/unified-how-this-levels-you-up/",
        "gate": "open", "gate_code": None,
        "rails": ["paypal", "stripe"], "js_rendered": False, "pending": False,
    },
    {
        "id": 7, "name": "ce.purebrain.ai/check-out (?ref=PB-H28G)",
        "url": "https://ce.purebrain.ai/check-out/?ref=PB-H28G",
        "gate": "ref:PB-H28G", "gate_code": None,
        # ce page is PayPal-only today (Stripe not wired) — Stripe is INFO here.
        "rails": ["paypal"], "js_rendered": False, "pending": False,
    },
    {
        "id": 8, "name": "/sme-awakening/ (?aid=123)",
        "url": "https://purebrain.ai/sme-awakening/?aid=123",
        "gate": "aid:123", "gate_code": None,
        "rails": ["paypal", "stripe"], "js_rendered": True, "pending": False,
    },
    {
        "id": 9, "name": "/migrate-awakening (FUTURE)",
        "url": "https://purebrain.ai/migrate-awakening",
        "gate": "open", "gate_code": None,
        "rails": ["paypal", "stripe"], "js_rendered": True,
        "pending": True,  # skip-until-live: flip to False to activate (one line).
    },
]

# Checkout-rail marker sets (server-rendered detection via served HTML).
RAIL_MARKERS = {
    "paypal": ["paypal.com/sdk/js", "paypal.Buttons", "data-pb-tier"],
    "stripe": ["js.stripe.com", "EmbeddedCheckout", "initEmbeddedCheckout",
               "create-checkout-session"],
}
# A leaked secret key is a CRITICAL fail regardless of page.
SK_LIVE_MARK = "sk_live"


class Result:
    def __init__(self):
        self.failures = []   # list of (page, assertion, evidence)
        self.lines = []      # human-readable transcript

    def log(self, s):
        self.lines.append(s)
        print(s)

    def fail(self, page, assertion, evidence):
        self.failures.append((page, assertion, evidence))
        self.log(f"  {R}FAIL{NC}  [{assertion}] {evidence}")

    def ok(self, msg):
        self.log(f"  {G}PASS{NC}  {msg}")

    def info(self, msg):
        self.log(f"  {Y}INFO{NC}  {msg}")


def http_get(url, timeout=30):
    """GET (never HEAD — CF Pages 404s on HEAD). Returns (status, body)."""
    if requests is not None:
        try:
            r = requests.get(url, timeout=timeout, allow_redirects=True,
                             headers={"User-Agent": "BOOP-SYNTH-probe/1.0"})
            return r.status_code, r.text
        except Exception as e:
            return -1, f"__ERR__ {e}"
    # curl fallback (no requests lib)
    try:
        out = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-w", "\n%{http_code}", url],
            capture_output=True, text=True, timeout=timeout + 5)
        body = out.stdout
        nl = body.rfind("\n")
        code = int(body[nl + 1:].strip() or "-1")
        return code, body[:nl]
    except Exception as e:
        return -1, f"__ERR__ {e}"


def detect_rails(html):
    """Return dict rail->bool present in served HTML, plus sk_live leak bool."""
    present = {}
    for rail, marks in RAIL_MARKERS.items():
        present[rail] = any(m in html for m in marks)
    sk_leak = SK_LIVE_MARK in html
    return present, sk_leak


# -----------------------------------------------------------------------------
# (B) CHECKOUT-LIVE — optional browser DOM assertion for JS-rendered pages.
# -----------------------------------------------------------------------------
def render_check(page, res):
    """Load the page in headless chromium; assert a PayPal button iframe or a
    Stripe frame/EmbeddedCheckout mount actually renders. Fills the gate code if
    present. Returns True if a checkout element rendered."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        res.info(f"{page['name']} :: --render requested but playwright not installed "
                 "(pip install playwright && playwright install chromium) — falling back to curl grep")
        return None
    found = False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context()
            pg = ctx.new_page()
            pg.goto(page["url"], wait_until="networkidle", timeout=45000)
            # Best-effort gate fill (client-side gate input).
            if page.get("gate_code"):
                for sel in ["input[type=password]", "input[name*=code]",
                            "input[id*=code]", "input[placeholder*=code]"]:
                    try:
                        el = pg.query_selector(sel)
                        if el:
                            el.fill(page["gate_code"])
                            pg.keyboard.press("Enter")
                            pg.wait_for_timeout(2500)
                            break
                    except Exception:
                        continue
            pg.wait_for_timeout(3500)  # allow SDK/button injection
            selectors = [
                "iframe[title*='PayPal']", ".paypal-buttons", "iframe[name^='__paypal']",
                "iframe[name^='__privateStripeFrame']", "#embedded-checkout",
                "[data-testid='embedded-checkout']",
            ]
            for sel in selectors:
                try:
                    if pg.query_selector(sel):
                        found = True
                        break
                except Exception:
                    continue
            browser.close()
    except Exception as e:
        res.info(f"{page['name']} :: render check error: {e}")
        return None
    finally:
        # Playwright cleanup is MANDATORY per project rule.
        subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
        subprocess.run(["pkill", "-f", "playwright"], capture_output=True)
    return found


def check_page(page, res, use_render):
    res.log(f"\n--- [{page['id']}] {page['name']}  (gate: {page['gate']}) ---")
    if page.get("pending"):
        res.info(f"{page['name']} :: PENDING/skip-until-live — set pending=False to activate")
        return

    # (A) PAGE LOADS
    code, html = http_get(page["url"])
    if code != 200:
        res.fail(page["name"], "page-not-loading", f"HTTP {code} (expected 200)")
        return
    res.ok("HTTP 200 (page loads)")

    # (B) CHECKOUT IS LIVE
    present, sk_leak = detect_rails(html)
    if sk_leak:
        res.fail(page["name"], "sk_live-leaked",
                 "CRITICAL: sk_live secret key present in client-served HTML")

    required = page["rails"]
    any_required = any(present.get(r) for r in required)
    # Report each rail's status.
    for r in ["paypal", "stripe"]:
        if r in required:
            if present.get(r):
                res.ok(f"checkout rail '{r}' WIRED (marker in served HTML)")
            elif not page["js_rendered"]:
                res.info(f"checkout rail '{r}' not detected in served HTML for this page")
        else:
            if present.get(r):
                res.info(f"checkout rail '{r}' present (not required for this page)")

    if any_required and not page["js_rendered"]:
        res.ok("checkout is LIVE (at least one required rail wired)")
    elif page["js_rendered"]:
        if use_render:
            rendered = render_check(page, res)
            if rendered is True:
                res.ok("checkout is LIVE (browser DOM: PayPal/Stripe element rendered)")
            elif rendered is False:
                res.fail(page["name"], "checkout-not-live",
                         "JS-rendered page: no PayPal button iframe / Stripe element in DOM after load")
            else:
                # render unavailable -> fall back to grep; JS pages rarely expose markers.
                if any_required:
                    res.ok("checkout markers found in served HTML (render unavailable, grep fallback)")
                else:
                    res.info(f"{page['name']} :: JS-rendered, curl-blind, render unavailable — "
                             "run with --render for a DOM assertion (INFO, not FAIL)")
        else:
            res.info(f"{page['name']} :: JS-rendered (Next.js); checkout injected client-side — "
                     "curl-blind. Run with --render to assert the DOM element (INFO, not FAIL)")
    else:
        # server-rendered page, 200, but NO required rail marker => real failure.
        res.fail(page["name"], "checkout-not-live",
                 f"HTTP 200 but no required checkout rail {required} detected in served HTML")


# -----------------------------------------------------------------------------
# (C) CONVERSATION-LOGGING WITH IDENTITY-LINKAGE — synthetic capture.
# -----------------------------------------------------------------------------
def build_synth_payload(synth_uuid):
    """A naming-ceremony-shaped conversation carrying the strong key (sessionUuid)
    in BOTH the top-level session_id AND metadata.sessionUuid — matching the real
    frontend record shape so the S2 strong-key lookup binds it. Deliberately:
      - NO orderId, NO account_id  -> S0/S1 unreachable
      - NO payer email in content  -> S3 unreachable
      - page_url is a NON-payment synthetic marker + only 4 msgs -> S4 unreachable
    """
    return {
        "session_id": synth_uuid,
        "sessionId": synth_uuid,
        "aiName": "SynthProbeAI",
        "messages": [
            {"role": "assistant", "content": "Welcome. What would you like to name me?"},
            {"role": "user", "content": "I'll name you SynthProbeAI."},
            {"role": "assistant", "content": "SynthProbeAI — I love it. That's who I am now."},
            {"role": "user", "content": "Great, SynthProbeAI it is."},
        ],
        "metadata": {
            "event_type": "synthetic_probe_naming",
            "sessionUuid": synth_uuid,
            "ai_name": "SynthProbeAI",
            "message_count": 4,
            # NON-payment URL on purpose (keeps S4 recency from ever selecting it).
            "page_url": "https://purebrain.ai/__BOOP_SYNTH_PROBE__ (synthetic; not a payment page)",
            "synthetic": True,
            "note": "BOOP overnight probe — inert, unbindable to any real order.",
        },
    }


def load_store_records(path):
    recs = []
    if not os.path.exists(path):
        return recs
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except Exception:
                continue
    return recs


def find_by_sessionuuid(records, synth_uuid):
    """Replica of the strict S2 strong-key branch of _lookup_naming_conversation.
    Returns (best_record, ai_name, msg_count) or (None, '', 0)."""
    best = None
    best_count = 0
    for e in records:
        meta = e.get("metadata") or {}
        entry_suuid = (e.get("session_uuid") or "").strip()
        meta_suuid = (meta.get("sessionUuid") or "").strip()
        sid = (e.get("session_id") or "").strip()
        if synth_uuid in (entry_suuid, meta_suuid, sid):
            mc = len(e.get("messages") or [])
            if mc > best_count:
                best = e
                best_count = mc
    if best is None:
        return None, "", 0
    ai_name = (best.get("aiName") or (best.get("metadata") or {}).get("ai_name") or "").strip()
    return best, ai_name, best_count


def check_conversation_logging(res, dry_run):
    res.log("\n=== (C) CONVERSATION-LOGGING WITH IDENTITY-LINKAGE (synthetic) ===")
    synth_uuid = "BOOP-SYNTH-" + uuid.uuid4().hex
    payload = build_synth_payload(synth_uuid)
    res.info(f"synthetic sessionUuid = {synth_uuid} (inert; unbindable to any real order)")

    if dry_run:
        # Never touch production store. Copy -> append -> lookup against the copy.
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        tmp.close()
        if os.path.exists(STORE_PATH):
            shutil.copy(STORE_PATH, tmp.name)
        # Simulate the server write shape (log_conversation() adds these).
        rec = dict(payload)
        rec["server_timestamp"] = datetime.now(timezone.utc).isoformat()
        rec["client_ip"] = "127.0.0.1"
        with open(tmp.name, "a") as f:
            f.write(json.dumps(rec) + "\n")
        res.info(f"[dry-run] wrote synthetic record to TEMP copy {tmp.name} (production store untouched)")
        store_for_lookup = tmp.name
        posted_ok = True
    else:
        # POST to the SAME endpoint the frontend uses.
        if requests is None:
            res.info("requests lib unavailable; using curl for POST")
        posted_ok, post_evidence = post_synth(payload)
        if not posted_ok:
            res.fail("conversation-logging", "conversation-not-persisted",
                     f"POST to {LOG_ENDPOINT} failed: {post_evidence}")
            return synth_uuid
        res.ok(f"POST accepted by {LOG_ENDPOINT} ({post_evidence})")
        store_for_lookup = STORE_PATH

    # (C-1) PERSISTENCE — poll the store the seed is read from.
    deadline = time.time() + (0 if dry_run else PERSIST_WAIT_S)
    found_rec = None
    while True:
        recs = load_store_records(store_for_lookup)
        best, ai_name, mc = find_by_sessionuuid(recs, synth_uuid)
        if best is not None:
            found_rec = best
            break
        if time.time() >= deadline:
            break
        time.sleep(2)

    if found_rec is None:
        res.fail("conversation-logging", "conversation-not-persisted",
                 f"synthetic record NOT found in store {store_for_lookup} within "
                 f"{PERSIST_WAIT_S}s of POST — frontend->store path is BROKEN "
                 "(this is the empty-seed regression class)")
        return synth_uuid
    res.ok(f"persisted to seed-read store ({os.path.basename(store_for_lookup)})")

    # (C-2) STRONG-KEY FINDABILITY — strict S2 lookup would bind it.
    best, ai_name, mc = find_by_sessionuuid(load_store_records(store_for_lookup), synth_uuid)
    if best is not None and ai_name and mc > 0:
        res.ok(f"strong-key findable by sessionUuid (S2): ai_name='{ai_name}', {mc} msgs — "
               "a strict _lookup_naming_conversation would BIND this")
    else:
        res.fail("conversation-logging", "not-strong-key-findable",
                 f"record persisted but NOT strong-key findable (ai_name='{ai_name}', msgs={mc}) — "
                 "seed would fire EMPTY / stay unfired")
    return synth_uuid


def post_synth(payload):
    """POST the synthetic conversation. Returns (ok, evidence)."""
    body = json.dumps(payload)
    if requests is not None:
        try:
            r = requests.post(LOG_ENDPOINT, data=body,
                             headers={"Content-Type": "application/json"}, timeout=30)
            return (200 <= r.status_code < 300), f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    try:
        out = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "30", "-X", "POST",
             "-H", "Content-Type: application/json", "-d", body,
             "-w", "\n%{http_code}", LOG_ENDPOINT],
            capture_output=True, text=True, timeout=35)
        resp = out.stdout
        nl = resp.rfind("\n")
        code = int(resp[nl + 1:].strip() or "-1")
        return (200 <= code < 300), f"HTTP {code}"
    except Exception as e:
        return False, str(e)


# -----------------------------------------------------------------------------
# PORTAL ALERT
# -----------------------------------------------------------------------------
def send_portal_alert(res, synth_uuid):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# PAYMENT-PAGE PROBE FAILURE",
        "",
        f"**When:** {ts}",
        f"**Probe:** verify-payment-pages-full.py",
        f"**Synthetic sessionUuid:** {synth_uuid}",
        f"**Failures:** {len(res.failures)}",
        "",
        "| Page | Assertion Failed | Evidence |",
        "|------|------------------|----------|",
    ]
    for page, assertion, evidence in res.failures:
        ev = evidence.replace("|", "\\|")
        lines.append(f"| {page} | **{assertion}** | {ev} |")
    lines += [
        "",
        "Assertion legend: `checkout-not-live` = PayPal/Stripe element not wired; "
        "`conversation-not-persisted` = synthetic naming-convo did not reach the "
        "seed-read store (empty-seed regression); `not-strong-key-findable` = "
        "persisted but a strict sessionUuid lookup would not bind it.",
    ]
    alert_dir = os.path.join(REPO_ROOT, "exports", "departments", "systems-technology")
    os.makedirs(alert_dir, exist_ok=True)
    alert_path = os.path.join(alert_dir, f"payment-probe-failure-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
    with open(alert_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    res.log(f"\nAlert written: {alert_path}")

    if os.environ.get("PORTAL_ALERT", "1") != "0" and os.path.exists(PORTAL_DELIVER):
        try:
            subprocess.run(
                ["bash", PORTAL_DELIVER, alert_path,
                 f"PAYMENT-PAGE PROBE: {len(res.failures)} money-path failure(s) — see report"],
                capture_output=True, text=True, timeout=30)
            res.log("Portal alert delivered via portal_deliver.sh")
        except Exception as e:
            res.log(f"Portal delivery error (alert file still written): {e}")
    else:
        res.log("Portal delivery skipped (PORTAL_ALERT=0 or --no-alert or deliver script missing)")


def main():
    ap = argparse.ArgumentParser(description="Full money-path payment-page probe (3 assertions/page).")
    ap.add_argument("--render", action="store_true",
                    help="Use headless chromium to assert checkout DOM element on JS-rendered pages.")
    ap.add_argument("--dry-run", action="store_true",
                    help="No network POST; write synthetic to a TEMP COPY of the store; self-test logic.")
    ap.add_argument("--no-alert", action="store_true", help="Never call portal_deliver on failure.")
    ap.add_argument("--only-conversation", action="store_true",
                    help="Run only the (C) conversation-logging assertion.")
    args = ap.parse_args()

    if args.no_alert:
        os.environ["PORTAL_ALERT"] = "0"

    res = Result()
    res.log("=" * 62)
    res.log("  FULL MONEY-PATH PAYMENT-PAGE PROBE")
    res.log(f"  {datetime.now(timezone.utc).isoformat()}")
    res.log(f"  endpoint={LOG_ENDPOINT}")
    res.log(f"  store={STORE_PATH}")
    res.log(f"  mode={'DRY-RUN' if args.dry_run else 'LIVE'}  render={args.render}")
    res.log("=" * 62)

    if not args.only_conversation:
        for page in PAGES:
            check_page(page, res, args.render)

    synth_uuid = check_conversation_logging(res, args.dry_run)

    res.log("\n" + "=" * 62)
    if res.failures:
        res.log(f"  {R}RESULT: {len(res.failures)} FAILURE(S){NC}")
        for page, assertion, evidence in res.failures:
            res.log(f"    - [{assertion}] {page}: {evidence}")
        send_portal_alert(res, synth_uuid)
        res.log("=" * 62)
        sys.exit(1)
    res.log(f"  {G}RESULT: ALL MONEY-PATH ASSERTIONS PASSED{NC}")
    res.log("=" * 62)
    sys.exit(0)


if __name__ == "__main__":
    main()
