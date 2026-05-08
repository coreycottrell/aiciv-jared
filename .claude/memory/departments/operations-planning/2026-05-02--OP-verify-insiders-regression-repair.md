# OP# Pair Verification: /insiders/ Regression Repair

**Date**: 2026-05-02  
**Type**: operational  
**Agent**: operations-analyst (OP#)  
**Trigger**: Pair-verification BOOP following ST# ship (`2026-05-02--insiders-regression-repair.md`)  
**Independence**: OP# ran all probes independently — no curl output copied from ST# memo.

---

## Verification Summary: ALL 7 PASS — ROUTE CLOSED

| Probe | Assertion | Result | Evidence |
|-------|-----------|--------|---------|
| 1 | `curl -sI /insiders/awakened/` returns HTTP 200 | PASS | `HTTP/2 200` — cf-ray `9f59c6418d1c362a-FRA` |
| 2 | Response contains `meta http-equiv="refresh"` with `url=/awakened/` + canonical `/awakened/` | PASS | Both tags present (see raw below) |
| 3 | `/awakened/` (redirect target) serves `'149.00'` + `P-2SA65600MT088594TNGLTFKY` | PASS | Both strings present |
| 4 | `curl -sI /insiders/pay-test-awakened/` returns HTTP 200 | PASS | `HTTP/2 200` — cf-ray `9f59c67c9d54d3c2-FRA` |
| 5 | Forbidden markers count = 0 (`launchPostPaymentFlow`, `_postPaymentLaunched`, `postPaymentOverlay`) | PASS | `grep -cE` returned `0` |
| 6 | `fireSeed` count >= 4 | PASS | Count = `5` |
| 7 | `/insiders/pay-test-awakened/` serves `'149.00'` + `P-2SA65600MT088594TNGLTFKY` | PASS | Both strings present |

**Stretch (Playwright click-through)**: Not executed. Playwright not available in this environment. Noted as skipped per task instructions.

---

## Raw Probe Evidence

### Probe 1
```
HTTP/2 200
content-type: text/html; charset=utf-8
cf-ray: 9f59c6418d1c362a-FRA
```

### Probe 2
```
<meta http-equiv="refresh" content="0; url=/awakened/">
<link rel="canonical" href="https://purebrain.ai/awakened/">
// Hard redirect — preserves spec-compliant pricing on canonical /awakened/.
```

### Probe 3
```
Awakened:  'P-2SA65600MT088594TNGLTFKY',
Awakened:  '149.00',
```

### Probe 4
```
HTTP/2 200
content-type: text/html; charset=utf-8
cf-ray: 9f59c67c9d54d3c2-FRA
```

### Probe 5
```
0
```

### Probe 6
```
5
```

### Probe 7
```
Awakened:  'P-2SA65600MT088594TNGLTFKY',
Awakened:  '149.00',
```

---

## Disposition

- ST# ship verified independently. All 7 assertions hold.
- Route closed. No escalation to ST# required.
- Outstanding item NOT in scope: `/insiders/` index pricing drift ($74.50 vs $149) — held correctly by ST# per investor-frozen rule. Awaiting Jared approval. OP# confirms this was correctly NOT shipped.

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/operations-analyst/` for prior verification patterns
- Found: `2026-05-02--777-api-probe-pair-audit.md` (same-day pair-audit for 777 API — confirms probe methodology is established)
- Applying: same independent-curl probe pattern from 777 audit

---

## Memory Written

Path: `.claude/memory/departments/operations-planning/2026-05-02--OP-verify-insiders-regression-repair.md`  
Type: operational  
Topic: Independent pair verification of /insiders/ regression repair (ST# ship, May 2 2026)
