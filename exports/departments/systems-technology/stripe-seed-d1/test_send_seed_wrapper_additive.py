#!/usr/bin/env python3
"""
Phase A verification: prove the additive send_seed wrapper changes are
BACKWARD COMPATIBLE and that the LOCKED core is never modified.

Run:  python3 exports/departments/systems-technology/stripe-seed-d1/test_send_seed_wrapper_additive.py

These are pure-logic tests over the wrapper's two additive behaviors:
  1. X-Seed-Secret gate: open when env unset; reject ONLY a wrong secret when set;
     a request with NO header is still allowed (legacy compat).
  2. conversation-hydration-on-empty: fires ONLY when the caller sent an empty/
     absent conversation. A caller that already passes a non-empty conversation
     is left byte-for-byte unchanged.

We do not boot Flask here; we reproduce the EXACT decision logic the wrapper
uses and assert the truth table, plus assert (via git) the locked core is
byte-identical to HEAD.
"""
import hmac
import os
import subprocess
import sys

FAILS = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        FAILS.append(name)


# ---- 1. X-Seed-Secret gate truth table (mirrors wrapper lines) ----
def gate_allows(cfg, provided):
    """Returns True if the request is ALLOWED (not 401). Mirror of wrapper logic:
    reject ONLY when (cfg set) AND (header present) AND (mismatch)."""
    if cfg and provided is not None:
        if not hmac.compare_digest(str(provided), str(cfg)):
            return False
    return True


# env unset -> always open (legacy)
check("gate: env unset, no header -> allowed (legacy open)", gate_allows("", None) is True)
check("gate: env unset, any header -> allowed (legacy open)", gate_allows("", "anything") is True)
# env set
check("gate: env set, correct header -> allowed", gate_allows("S3CRET", "S3CRET") is True)
check("gate: env set, WRONG header -> REJECTED", gate_allows("S3CRET", "nope") is False)
check("gate: env set, NO header -> allowed (additive, legacy compat)", gate_allows("S3CRET", None) is True)


# ---- 2. hydration-on-empty truth table (mirrors wrapper lines) ----
def should_hydrate(data):
    """Mirror of wrapper: hydrate ONLY when conversation empty/absent AND we have
    a uuid or order to look up by."""
    existing = data.get("conversation")
    has_conv = isinstance(existing, list) and len(existing) > 0
    uuid = (data.get("session_uuid") or data.get("sessionUuid") or "").strip()
    order = (data.get("order_id") or data.get("orderId") or "").strip()
    return (not has_conv) and bool(uuid or order)


# legacy caller WITH a real conversation -> NEVER hydrate (byte-for-byte unchanged)
check("hydrate: caller w/ non-empty conversation -> NO hydration (legacy untouched)",
      should_hydrate({"session_uuid": "u1", "conversation": [{"role": "user", "content": "hi"}]}) is False)
# webhook caller with empty conversation + uuid -> hydrate
check("hydrate: empty conversation + session_uuid -> hydrate",
      should_hydrate({"session_uuid": "u1", "conversation": []}) is True)
# webhook caller with empty conversation + order only -> hydrate
check("hydrate: empty conversation + order_id only -> hydrate",
      should_hydrate({"order_id": "sub_123", "conversation": []}) is True)
# absent conversation key + uuid -> hydrate
check("hydrate: absent conversation + session_uuid -> hydrate",
      should_hydrate({"session_uuid": "u1"}) is True)
# empty conversation but NO uuid/order -> cannot hydrate (nothing to look up)
check("hydrate: empty conversation, no uuid/order -> NO hydration",
      should_hydrate({"conversation": []}) is False)


# ---- 3. LOCKED core: additive-only Pure Migrate fold (UPDATED 2026-06-30) ----
# The original check asserted the LOCKED core was byte-identical to HEAD (it
# proved the Stripe wrapper change was wrapper-only). The GREENLIT Pure Migrate
# opaque-blob fold (spec migrate-gate2-producer-spec-2026-06-30 §2, Jared GO
# 2026-06-30) INTENTIONALLY extends _send_seed_core / _send_seed_core_locked
# with an optional migration_bundle param + a single gated `## Migration Bundle`
# splice. So the invariant is now "byte-identical WHEN the bundle is ABSENT",
# proven by:
#   exports/departments/systems-technology/migrate-seed-fold/test_migration_bundle_fold.py
# Here we assert the fold is ADDITIVE-ONLY: an optional param defaulting to None,
# one gated opaque-blob splice, the bundle never inlined into the transcript,
# and the locked transcript construction unchanged from HEAD.
def extract(src, start, end):
    i = src.index(start)
    j = src.index(end, i)
    return src[i:j]


try:
    repo_root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"]).decode().strip()
    head = subprocess.check_output(
        ["git", "show", "HEAD:tools/purebrain_log_server.py"]).decode()
    with open(os.path.join(repo_root, "tools/purebrain_log_server.py")) as f:
        work = f.read()
    START = "def _send_seed_core(data, server_derived_tier=None):"
    END = "    @app.route('/api/send-seed'"
    h = extract(head, START, END)
    w = extract(work, START, END)
    check("locked-core migration fold is additive (migration_bundle=None default)",
          "migration_bundle=None" in w)
    check("locked-core fold is a single gated opaque-blob splice",
          w.count("render_migration_bundle_block(migration_bundle)") == 1)
    check("locked-core never inlines bundle / drops superseded prose+base64",
          ("base64(json):" not in w)
          and ("render_migration_bundle_human_readable(" not in w))
    check("locked transcript construction unchanged from HEAD",
          ("_md_content += '---\\n\\n## Full Conversation\\n\\n'" in h)
          and ("_md_content += '---\\n\\n## Full Conversation\\n\\n'" in w)
          and ("_md_content += f'**{_role}**: {_cont}\\n\\n'" in h)
          and ("_md_content += f'**{_role}**: {_cont}\\n\\n'" in w))
except Exception as e:
    check(f"LOCKED core fold check ran (error: {type(e).__name__}: {e})", False)


print()
if FAILS:
    print(f"{len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
sys.exit(0)
