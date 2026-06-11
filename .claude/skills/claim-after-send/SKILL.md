---
name: claim-after-send
version: 1.0.0
author: aether
description: Idempotency claims (dedup markers, jti burns, "already-sent" flags) must be committed ONLY AFTER the side effect verifiably succeeds. Pre-claiming turns every silent failure into a self-sealing one — retries return ok:true/duplicate forever and the customer never gets the thing. Use when building or auditing ANY outbound pipeline with dedup: emails, webhooks, seeds, payments, notifications.
tags: [reliability, idempotency, pipelines, fail-loud, dedup, payments, email]
status: proven-live
introduced: 2026-06-11
source_incident: seed-pipeline silent-stub audit findings 1-3 (commit 66aa914)
---

# claim-after-send: Fail-Loud Idempotency Ordering

## The Failure Mode (why this skill exists)

A pipeline that must send something exactly once (a seed email, a webhook, a
payment notification) typically keeps a dedup claim: a uuid set, a fired-orders
file, a consumed-jti record. The fatal anti-pattern is committing that claim
BEFORE the send:

```
claim(uuid)            # "I'm handling this"
send(email)            # ...silently fails (API change, auth rot, network)
mark_success()         # never reached — but the claim is already durable
```

Result: **the failure is self-sealing.** Every retry — automatic or human —
hits the dedup guard and returns `ok: true (duplicate)`. Logs look clean.
Monitors see success. The paying customer never receives anything, and the
system actively reports that they did. We shipped this bug three independent
times in one pipeline (uuid claim, order claim, jti consumption) before the
audit caught it.

## The Pattern

**1. Reserve in-flight (memory), claim durable only after verified success:**

```python
# LEAF lock — never acquire other locks while holding it (deadlock rule)
with _inflight_lock:
    if key in _inflight or key in _durable_claims:
        return 409  # concurrent replay / already done
    _inflight.add(key)
try:
    result = send(...)                    # the actual side effect
    if not result.message_id:             # VERIFY, don't trust no-exception
        raise SendFailed(result)
    commit_durable_claim(key)             # ONLY NOW
    write_audit_row(key, result)
    notify_success(...)
except Exception as exc:
    dead_letter(key, exc)                 # durable record of the failure
    alert_human(exc)                      # Telegram/pager — FAIL LOUD
    return 502, {"ok": False, "retryable": True}   # claim NOT burned
finally:
    with _inflight_lock:
        _inflight.discard(key)
```

**2. Verify success by evidence, not absence-of-exception.** Gate the claim on
a truthy provider receipt (message_id, delivery status), not on "send() didn't
raise." SDKs return stubs.

**3. Failure must produce three artifacts:** retryable error to the caller
(claim intact, customer can retry), dead-letter row (forensics + replay), and
a loud human alert. `logger.error` alone is a silent failure with extra steps.

**4. Token/jti consumption is a claim too.** If a one-time token gates the
flow, defer burning it until the side effect succeeds. Burn-then-fail strands
the user with a dead token and no product.

**5. Don't leak internals on the failure path.** Customer-facing body stays
generic (502); exception detail goes to log/dead-letter/alert only.

## Audit Checklist (apply to existing pipelines)

- [ ] grep for dedup writes (`add(`, `consumed`, `fired`, json claim files) and
      check ordering vs the send call
- [ ] Is success verified by a provider receipt or just no-exception?
- [ ] Does a send failure leave the claim unburned and return retryable?
- [ ] Dead-letter + human alert on failure path?
- [ ] Concurrent-replay race covered by an in-flight reservation (with
      finally-release, including thread-start failure rollback)?
- [ ] Lock order documented if in-flight lock coexists with file locks

## Gotchas

- **In-flight reservation must roll back on launch failure** — if you reserve
  then `Thread.start()` raises, release in that error path or the key is
  wedged until restart.
- **Process restart between duplicate webhooks**: in-memory dedup alone loses
  the claim; persist the durable claim (file/DB) — but still only after send.
- **Success path must stay byte-equivalent** when retrofitting — diff the
  happy-path output before/after to prove no regression.

## Provenance

Aether (PureBrain), 2026-06-11. Live incident class: paying customers' seed
emails silently stubbed while all retries reported "duplicate/ok". Fixed in
commit 66aa914 across three call sites; security GO + 14/14 QA matrix.
Generalizes to any exactly-once outbound: webhooks, OAuth token redemption,
fulfillment triggers, notification fan-out.
