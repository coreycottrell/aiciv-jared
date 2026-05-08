# GREENLIT: Disable S5-payerName Fuzzy Fallback in Seed Dispatcher

**Authority**: Jared (CEO) greenlit 2026-05-07
**Priority**: High - Constitutional seed-flow safety
**Flow**: SPEC → **CTO REVIEW** → BUILD → SECURITY → QA → SHIP
**Your phase**: BUILD (after CTO review approves)

---

## Context

Sheila Keeper incident (2026-05-07): S5 fuzzy fallback matched her payment to Jay Hutton's container via shared first name "Jay". This is the cross-customer collision class we're permanently eliminating.

**Constitutional rule**: `feedback_seed_flow_never_deviate.md` - "AI name MUST populate before send"

Once S5 is disabled, when S1-S4 all fail, the system will BLOCK the seed dispatch and queue for manual human review with Telegram alert instead of making a potentially wrong guess.

---

## Reference Files

**Source code**:
- `tools/purebrain_log_server.py:1029-1062` (S1-S5 dispatcher logic)

**Specifications**:
- `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` Section 8
- `feedback_seed_flow_never_deviate.md` (constitutional memory)

**Evidence**:
- `exports/portal-files/sheila-keeper-seed-trace-2026-05-07.md` (incident trace)

---

## Your Mission (BUILD Phase)

### Step 1: Read Current S5 Logic
Read `tools/purebrain_log_server.py:1020-1100` (broader context around S5).
Document the existing 5-strategy chain: what each S1-S5 does, what each returns.

### Step 2: Design the Replacement
Replace S5 with a hard-block:

**When S1-S4 all return 0 conversation matches**:
- DO NOT fall back to fuzzy first-name match
- Log "no match" event
- Fire Telegram alert: `./tools/tg_send.sh "🚨 SEED BLOCKED: no S1-S4 match for payment <orderId> / <payerEmail> / <amount>. Manual review required."`
- Write "blocked-seed" record to structured queue file (e.g., `logs/blocked_seeds.jsonl`) with all payment metadata for human reconciliation
- Return early without calling Witness (no seed sent)

### Step 3: Implement
Edit `tools/purebrain_log_server.py:1029-1062`:

- Comment out S5 logic with clear explanatory header citing today's incident
- Add hard-block + Telegram alert + JSONL queue write
- Preserve all existing dedup, idempotency, and logging
- Keep function signature identical (don't break callers)

### Step 4: Add Feature Flag (Defensive)
Add env-var flag `ALLOW_S5_FUZZY_FALLBACK=false` (default false) so we can re-enable S5 in an emergency without redeploy. Hard-block is default; S5 is explicit opt-in.

### Step 5: Test Locally
Synthetic calls to dispatcher:

- **S5 trigger case**: Payload that would have triggered S5 → verify it now blocks + logs + Telegram + JSONL
- **S2 success case**: sessionUuid matches → verify succeeds normally
- **S3 success case**: payerEmail matches → verify succeeds normally
- **Edge case**: Empty fields → should also block

### Step 6: Commit on Main Branch
- Run pre-commit hooks (NEVER skip)
- Commit message: `feat(dispatcher): disable S5-payerName fuzzy fallback per constitutional seed-flow rule. Blocks cross-customer collisions like Sheila/Jay (2026-05-07). Hard-block + Telegram alert + manual-review JSONL queue. ALLOW_S5_FUZZY_FALLBACK env var = false default.`

### Step 7: DO NOT Deploy Yet
Per engineering flow: **CTO REVIEW** → BUILD (you) → **SECURITY** → **QA** → SHIP. 

Your job ends at commit. Do NOT restart any service or push to origin. Aether will route through remaining gates.

### Step 8: Receipt
File: `exports/portal-files/disable-s5-fuzzy-fallback-2026-05-07.md` under 400 words.

**Sections**:
- Current S5 logic (with line citations)
- Replacement design
- Code changes (file:line for each)
- Local test results (3-4 synthetic cases)
- Commit hash
- Status: BUILD-COMPLETE-PENDING-SECURITY-AND-QA

**After Write, READ BACK the file.**

---

## Critical Constraints

- ❌ DO NOT deploy
- ❌ DO NOT push origin without Aether explicit auth
- ✅ Commit on main (backend dispatcher fix, not referral-v1 sprint)
- ✅ Pre-commit hooks REQUIRED
- ✅ Test locally before commit
- ✅ After every code change, read back the file
- ✅ Constitutional: preserve "AI name MUST populate before send" - hard-block enforces this

---

## Completion Signal

Report back with:
- Commit hash
- Local test results (4 cases)
- Status: BUILD-COMPLETE-PENDING-SECURITY-AND-QA
- Receipt file path

---

## Why This Matters

This change permanently eliminates the cross-customer collision vulnerability class. After this:
- S1-S4 fail → human reviews manually (safe)
- S5 fuzzy match → NEVER happens (vulnerability closed)

Sheila's case was the proof. This is the fix.

---

**Awaiting CTO pre-build review, then execute BUILD phase.**
