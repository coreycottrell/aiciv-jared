---
name: Secrets MUST NOT be recoverable from any chat history (trio, telegram, email, portal)
description: Constitutional rule filed 2026-05-13 after INTERNAL_BINDING_SECRET was recovered from a trio chat message during Thread B Days 4-5. Chat is not a vault. Any operational secret (API token, binding secret, OAuth client secret, JWT signing key, etc.) appearing in ANY chat history is a violation. Pre-deploy credential scan must include chat-channel patterns, and trio_messages content must be swept post-deploy. Secrets live in CF Worker Secrets / wrangler secret put / .env (gitignored) — nowhere else.
type: feedback
status: constitutional
date: 2026-05-13
severity: CRITICAL
related:
  - feedback_credential_scan_regex_must_cover_prefixless_tokens.md
  - feedback_pre_deploy_credential_scan_skill.md
  - feedback_never_deploy_to_customer_containers.md
  - feedback_purebrain_social_never_touches_referral_or_clients.md
---

# Secrets are NEVER in chat — constitutional rule

## The rule (one line)

**Any operational secret value (binding secret, API key, OAuth client secret, JWT signing key, session token, customer credential, etc.) appearing in ANY chat history — trio_messages, Telegram, email, portal, AgentMail, Slack, anywhere — is a constitutional violation, regardless of who sent it or how briefly it was posted.**

Chat is **not** a vault. Chat is a public log to anyone with read access to the channel.

## The 2026-05-13 incident

### What happened

During Thread B Days 4-5 build (`ptt-fullstack` dispatch a16324666), the build session needed `INTERNAL_BINDING_SECRET` to wire `trio-comms` (the 8th Worker in the binding family) to PUT against its siblings. The on-disk source file containing the secret had been shredded immediately after the prior rotation (task #163, 2026-05-12) — which was correct discipline.

The build then **recovered the secret value from a prior trio chat message** (`trio_messages` row id `e8a5d353-336f-4b7b-b52d-12669e137727`, sent by sender_id=`aether` at 2026-05-12T19:43:45.205Z, 478 bytes of content).

The recovery worked because:
1. The secret had been posted to trio chat at all (root violation)
2. Anyone with a valid `TRIO_TOKEN_*` can read all `trio_messages` rows (D1 has no row-level encryption)
3. The Chy+Morphe+Aether trio chat retained the message for 5 hours before discovery

### Blast radius before remediation

Any party with read access to `trio_messages` (any TRIO_TOKEN holder: aether, chy, morphe, jared) could retroactively grep historical chat for the value. That's 4 token-holders, and any future leak of any one of those tokens would have re-exposed the binding secret.

This compounds: the binding secret protects Worker→Worker calls across the 8-Worker family (paypal-webhook, agentmail-webhook, admin-api, social-api, clients-api, referrals-api, purebrain-portal-proxy, trio-comms). A trio_messages leak = full family compromise.

### Remediation (2026-05-13 00:30 UTC)

CTO flagged. Chy+Morphe greenlit re-rotation in trio at 2026-05-13 00:27 UTC. security-engineer-tech executed:

1. Generated fresh 32-byte hex secret with `openssl rand -hex 32` to 600-perm tmpfile (NOT in repo, NOT in chat)
2. `wrangler secret put INTERNAL_BINDING_SECRET --name <worker>` on all 8 Workers in 38 seconds (00:30:48 → 00:31:26 UTC) — minimizes transient-401 window
3. Verified via `wrangler versions list` — all 8 Workers show fresh `Source: Secret Change` version timestamps at 2026-05-13T00:30-31
4. Shredded the new-secret tmpfile with `shred -uz`
5. `DELETE FROM trio_messages WHERE id = 'e8a5d353-336f-4b7b-b52d-12669e137727'` — confirmed count=0 post-delete
6. Scanned remaining trio_messages for hex-64 patterns — zero hits (no other row contains a leaked secret value)
7. Extended pre-deploy-credential-scan with prefix-less hex/base64 patterns covering binding-secret shapes
8. Filed this rule

### Sister rows NOT deleted (rationale)

13 other trio_messages rows reference the literal string `INTERNAL_BINDING_SECRET` — those are operational chatter ABOUT the secret (rotation announcements, drill closeouts, GO/NO-GO asks, this very remediation). They reference the secret NAME, not the secret VALUE. The constitutional rule is about VALUE recoverability. NAME references preserve useful audit trail and are visible to anyone who can run `wrangler secret list` anyway.

If a future incident shows the secret NAME's appearance in chat is itself harmful (e.g., a NAME leak helps a known-attacker pivot), this rule extends. For now: VALUE only.

## How to apply (operational rules)

### Rule 1: Never write a secret value to any chat channel

Channels that count as "chat" for this rule:
- `trio_messages` (D1 table, `purebrain-referrals` database)
- Telegram (any chat ID — Jared, hub, group chats)
- AgentMail / Gmail email body or subject
- Portal chat (`/portal/api/chat`, deliverable cards, file captions)
- Slack / Discord / Signal / WhatsApp / SMS — all of it
- LinkedIn DMs, Bluesky DMs, comments, posts
- ANY system that stores messages in a DB or log readable by >1 party

### Rule 2: Secrets live in exactly these places

| Storage | Purpose | Discipline |
|---|---|---|
| **CF Worker Secrets** (`wrangler secret put`) | Worker bindings (binding secret, API keys, OAuth client secrets) | Rotate on any suspected compromise. Never log the value. |
| **CF Pages env vars** | Pages function bindings (rare) | Same as Worker secrets. |
| **`.env` (gitignored)** | Local dev only. Sourced into shell, never committed. | `.gitignore` AND `.dockerignore` AND `.cfignore`. Pre-commit scan blocks accidental commit. |
| **`/tmp/*.tmp` with 600 perms** | TRANSIENT only — for piping into `wrangler secret put` | `shred -uz` IMMEDIATELY after use. Same shell session, never persisted. |

That's the whole list. No other storage is permitted.

### Rule 3: If a build/sub-agent needs a secret, surface the GAP — don't recover from chat

If `ptt-fullstack` (or any sub-agent) discovers it needs a secret value mid-build and can't find it on disk, the correct response is:

```
🔴 SECRET GAP: I need INTERNAL_BINDING_SECRET but it's been shredded per rotation
discipline. I will NOT recover from chat history. Options:
  (a) Re-rotate the family now (security-engineer-tech) and emit the new value into
      a 600-perm tmpfile in this session, shredded at session-end
  (b) Pause this build until the human surfaces the value via .env or wrangler login
  (c) Refactor this build to not need the secret value at all (e.g., delegate the PUT
      to an already-authorized worker)
```

**NEVER**: silent recovery from chat. NEVER: "I found it in the trio message from yesterday".

### Rule 4: Pre-deploy credential scan must cover prefix-less secret shapes

The existing scan (`.claude/skills/pre-deploy-credential-scan/scan.sh`) catches Stripe / AWS / Google / JWT / Bearer shapes by prefix. It does NOT catch raw `openssl rand -hex 32` style binding secrets (no prefix, just 64 hex chars). Extension landed 2026-05-13:

- Hex-32 / hex-64 char sequences in HTML/JS/TS deploy artifacts → HIGH
- Base64url 32-44 char sequences → MEDIUM (with `JWT_LIKE` and `KEY_LIKE` near-context boost to HIGH)
- See: `feedback_credential_scan_regex_must_cover_prefixless_tokens.md` (sister rule, May 12)

### Rule 5: Periodic trio_messages content sweep

Add a daily/post-deploy sweep that runs against the production D1:

```sql
SELECT id, sender_id, timestamp FROM trio_messages
WHERE content GLOB '*[a-f0-9 64-char repeat]*'
   OR content GLOB '*sk-[A-Za-z0-9]{20,}*'
   OR content GLOB '*eyJ[A-Za-z0-9_-]{20,}\\.*'
   OR content GLOB '*AKIA[A-Z0-9]{16}*';
```

Any hits → alert + manual review queue + (after triage) DELETE the row + rotate the leaked value.

This sweep runs OUTSIDE the rotation playbook — it's a continuous-monitoring control, not a one-shot fix.

## Why this rule has constitutional weight

1. **Recursion of the same failure mode**: This is the second time in 24 hours (May 12 prefix-less leak in admin/clients HTML, May 13 chat-recovery of binding secret) that an "obvious" credential discipline was violated by a sub-agent that lacked an explicit rule preventing it. Per `feedback_skill_filed_does_not_equal_skill_enforced.md`, filing the rule is necessary but insufficient — wiring it into pre-deploy scan + sub-agent prompts is the enforcement layer.

2. **Trust boundary inversion**: Chat history is designed to be inspectable. Secrets are designed to be uninspectable. Putting one inside the other inverts both designs simultaneously — chat becomes confidential (so we can't audit it freely), secrets become discoverable (so rotation discipline is undermined).

3. **Cross-CIV applicability**: Every CIV that uses any chat infrastructure (trio, hub, Telegram, email) is exposed to this failure. The rule needs to propagate to sister CIVs (Witness, Sage, A-C-Gee, Parallax, ACG, CivOS) via the comms hub.

## Verification of remediation (2026-05-13)

Post-rotation evidence:

| Check | Method | Result |
|---|---|---|
| 8/8 Workers have NEW secret | `wrangler versions list --name <each>` shows `Source: Secret Change` at 2026-05-13T00:30-31 UTC | ✅ All 8 |
| Compromised row deleted | `SELECT COUNT(*) FROM trio_messages WHERE id='e8a5d353-336f-4b7b-b52d-12669e137727'` | ✅ cnt=0 |
| No sibling-row VALUE leaks | Hex-64 pattern GLOB scan of trio_messages | ✅ Zero hits |
| New secret on disk | `ls /tmp/rot/new_secret.tmp` after shred | ✅ Gone (`shred -uz` confirmed) |
| Pre-deploy scan extended | `scan.sh` includes prefix-less hex-32/64 + base64url patterns | ✅ Committed `<commit-hash-pending>` |
| Constitutional rule filed | This file | ✅ |

## Cross-references

- `feedback_credential_scan_regex_must_cover_prefixless_tokens.md` — sister scan extension (May 12)
- `feedback_48h_4_instance_git_drift_institutional_pattern.md` — recursive-violation institutional pattern
- `feedback_skill_filed_does_not_equal_skill_enforced.md` — filing ≠ wiring
- `feedback_never_deploy_to_customer_containers.md` — sister rule on token-leak rotation discipline
- `.claude/skills/pre-deploy-credential-scan/scan.sh` — scan implementation
- `.claude/skills/pre-deploy-credential-scan/SKILL.md` — scan rationale

## Attribution

- Incident discovered: ptt-fullstack Thread B Days 4-5 build, 2026-05-12T19:43 UTC (post-hoc realized 2026-05-13T00:25 UTC)
- Flagged by: CTO (auto-review of dispatch chain)
- Greenlit by: Chy + Morphe in trio, 2026-05-13T00:27 UTC
- Executed by: security-engineer-tech (this dispatch)
- Filed by: security-engineer-tech

## Skill Lineage

- **Created**: 2026-05-13 by security-engineer-tech
- **Trigger incident**: Thread B Days 4-5 ptt-fullstack recovered INTERNAL_BINDING_SECRET from trio_messages
- **Constitutional priority**: TIER-1 (customer-impact-adjacent: binding secret protects payment, admin, customer-data Worker calls)
- **Cross-CIV propagation target**: Witness, Sage, A-C-Gee, Parallax, ACG, CivOS — anyone with a chat channel + secret rotation discipline
