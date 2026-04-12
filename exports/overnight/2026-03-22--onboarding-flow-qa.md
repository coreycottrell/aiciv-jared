ONBOARDING FLOW QA — March 22, 2026
Generated: 2026-03-22 | Agent: dept-systems-technology

---

## Page Health

| Page | HTTP | PayPal | Chatbox | Seed Logic |
|------|------|--------|---------|------------|
| /live/ | 200 ✅ | ✅ | ✅ | ✅ |
| /insiders/ | 200 ✅ | ✅ | ✅ | ✅ |
| /awakened/ | 200 ✅ | ✅ | ✅ | ✅ |
| /partnered/ | 200 ✅ | ✅ | ✅ | ✅ |
| /unified/ | 200 ✅ | ✅ | ✅ | ✅ |
| /pay-test-sandbox-3/ | 200 ✅ | ✅ | ✅ | ✅ |

**Page Health: 6/6 PASS**

---

## Seed Pipeline

Magic link rewrite logic: ✅ Present in pay-test-sandbox-3/index.html
- Magic link poller confirmed (polls /api/magic-link/{uuid} every 5s post-flow)
- Rewrite logic handles pre-render and post-render magic link arrival cases

**Seed Pipeline: ✅**

---

## AgentMail Monitor

Process check: ✅ RUNNING (PIDs: 202063, 541686)

---

## Recent Payment Activity (last 10 entries)

Most recent entries from purebrain_payments.jsonl:

- 2026-03-20 22:35 — Awakened, $79.00, sandbox buyer (sb-c89tj49549583@personal.example.com) ✅ Real amount
- 2026-03-20 11:14 — Partnered, $0.00, internal test (127.0.0.1)
- 2026-03-20 10:24 — Awakened, $0.00, internal test (repeat order I-8ALB3AX8G1YU)
- 2026-03-20 10:02 — Awakened, $0.00, internal test
- 2026-03-20 01:47 — Awakened, $0.00, internal test
- 2026-03-19 14:08 — Awakened, $0.00, internal test
- 2026-03-19 00:19 — Awakened, $0.00, internal test
- 2026-03-18 23:40 — Awakened, $0.00, internal test
- 2026-02-18 18:31 — Awakened, $0.00, test-order-123

Note: Most recent real-money transaction was 2026-03-20 (sandbox buyer, $79.00 Awakened). No new paying customers since March 20. Internal test traffic (127.0.0.1) shows pipeline is being exercised.

---

## Issues

None. All 6 pages healthy, all key elements present, pipeline infrastructure intact.

---

## Summary

ONBOARDING FLOW QA — March 22, 2026
Page Health: /live/ ✅, /insiders/ ✅, /awakened/ ✅, /partnered/ ✅, /unified/ ✅, /pay-test-sandbox-3/ ✅
Seed Pipeline: ✅
AgentMail: ✅
Issues: None
