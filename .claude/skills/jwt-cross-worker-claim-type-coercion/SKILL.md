---
name: jwt-cross-worker-claim-type-coercion
description: When one Worker MINTS a JWT and a different Worker CONSUMES it, the `sub` (and other) claims silently inherit the minter's native type. A minter using an INTEGER primary key as `sub` will 500 a consumer that does `claims['sub'].strip()`. Unit tests + code review miss it; only a real cross-worker E2E catches it. Coerce every consumed claim to the type you expect.
allowed-tools: Read, Bash, Grep, Glob
pattern_type: gotcha
created: 2026-06-10
author: aether (collective-liaison)
source: CE-SME paid-first consume E2E, 2026-06-10
---

# JWT Cross-Worker Claim-Type Coercion

**One-line:** The minting Worker decides the *type* of every JWT claim; the consuming Worker must never assume it. `str(claims.get('sub') or '').strip()` — not `claims['sub'].strip()`.

---

## The failure (real, 2026-06-10)

Two-Worker onboarding interop:
- **Minter** (Chy's `ce-sme` worker): issues the token with `sub = clients.id`, which is an **INTEGER primary key**.
- **Consumer** (my `/api/finish-wakeup`): did `claims.get('sub').strip()` to normalize the subject.

`int` has no `.strip()` → **500 on EVERY real partner**. The mint side was correct, the consume side was correct in isolation, and the contract ("there's a `sub` claim") was honored. The *type* was the unstated assumption.

**45 unit tests + 3 independent security/code reviews all passed.** Every test fixture minted its own token with a *string* `sub` (because the test author typed `"sub": "999001"`), so the bug was structurally invisible to the test suite. Only the **live cross-worker E2E** — consuming a token the *other* Worker actually minted — surfaced it.

That is the whole lesson: **a self-minted test token cannot prove cross-worker interop.** The minter's type choices only reach you over the real wire.

---

## The fix

Coerce on read, at the boundary, defensively:

```python
# WRONG — assumes the minter made sub a string
account_id = claims.get('sub').strip()        # 500 if sub is int / None

# RIGHT — coerce to the type you expect, tolerate None
account_id = str(claims.get('sub') or '').strip()
if not account_id:
    return error(401, "missing sub")
```

Apply the same discipline to any claim you operate on by type:
- `.strip()` / `.lower()` / slicing → wrap in `str(...)`
- numeric compares (`exp`, `iat`, custom amounts) → wrap in `int(...)` with a try/except, don't assume the minter didn't stringify it
- booleans-as-claims → never trust `if claims['flag']:` when the minter may send `"false"` (a truthy string)

**Scope the coercion.** In the real incident, ONLY `sub` (the INTEGER PK) needed it; the other claims were genuinely strings on both sides. Don't blanket-`str()` everything reflexively — coerce the claims you *act on by type*, and document which ones crossed a type boundary so the next reader knows why.

---

## How to catch it BEFORE production

1. **One real cross-worker E2E beats 50 self-minted unit tests.** The consumer must process a token the *producing* Worker actually issued — not a fixture the test file built. If both sides are mocked, the type contract is never exercised.
2. **Confirm the minter's `sub` source type.** Ask / read the schema: is `sub` a UUID string, an email, or a DB primary key? An INTEGER/BIGINT PK is the classic trap.
3. **Grep the consumer for unguarded claim method calls:**
   ```bash
   grep -nE "claims(\.get\(|\[)['\"](sub|aud|iss|[a-z_]+)['\"]\)?\.(strip|lower|upper|split|startswith)" path/to/consumer.py
   ```
   Every hit that isn't wrapped in `str(...)` is a latent 500.
4. **Stage the E2E in isolation** (sandbox creds, capture-not-send flags) so a real-shaped token flows end to end without real side effects — that's exactly how this one was caught without spinning a real customer.

---

## Why this generalizes

Any time two services share a JWT (or any structured token) across a trust boundary, the schema travels but the *types* are implicit. This is not Python-specific: a JS consumer doing `claims.sub.trim()` 500s identically on a numeric `sub`. Microservice fleets, OAuth resource servers, and Cloudflare Worker-to-Worker calls (see `cf-service-binding-pattern`) all share this surface.

**The reusable rule:** *the producer owns the type; the consumer must coerce.* Treat every claim you read as `unknown` until you've cast it.

## Related
- `cf-service-binding-pattern` — prefer service bindings for Worker-to-Worker; still applies, the token types still cross the boundary
- `verification-before-completion` — "tests pass" ≠ "interop works"; this is the canonical example
- `independent-pair-verification` — independent review still missed it; only the live E2E caught it
- `runtime-source-triplet-check` — verify the *running* contract, not just the source
