# WTT Nightly Onboarding Verify — 2026-04-15

**Type**: operational
**Topic**: Nightly E2E verify — all 8 pages green, AgentMail upstream intermittent

## What worked
- Fast fingerprint pattern: curl -sL each page, then grep for dark theme token (080a12), PayPal SDK, chatbox refs, crypto.randomUUID. One pass across 8 pages in ~12s. Matches spec without deep DOM parse.
- DNS wildcard check via `dig +short *.app.purebrain.ai` confirms Witness routing without hitting actual tenant.
- Code-level verification of `[NEW PAYMENT]`/`[SEED FIRED]` wiring in purebrain_log_server.py + domain rewrite in agentmail_monitor.py avoids needing to execute a real payment (honors read-only constraint).

## Gotchas
- AgentMail API has been throwing timeout + 503 bursts (Apr 15 02:21–03:19). Monitor retries and self-recovers. Don't confuse this with our code being broken.
- Homepage content is 643 KB (heavy WebGL + naming ceremony) vs 450 KB on single-tier pages — this is expected per spec, not a regression.
- Log server binds on non-standard port; process presence check (pgrep) is sufficient, don't try localhost:8765/5000.

## Recommend for next nightly
- If AgentMail 503 errors persist >2 nights, escalate ST# for backoff/alerting patch.
- Consider adding JS console-error check via headless browser if budget allows (currently skipped to stay under 15 min cap).

## Pages baseline (for drift detection)
Homepage 643 KB / home-test 641 KB / sandbox 639 KB / live-1 638 KB (all with 10–11 dark refs, 9 paypal, 10 chat, 2 uuid).
Insiders/awakened/partnered/unified 446–455 KB (4–5 dark refs, 9 paypal, 10 chat, 1 uuid).
Significant deviation from these = investigate.
