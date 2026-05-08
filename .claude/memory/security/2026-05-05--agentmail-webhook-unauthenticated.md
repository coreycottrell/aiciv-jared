---
name: agentmail-webhook unauthenticated POST exposure
description: HIGH severity — onboarding-api.purebrain.ai/webhook accepts unauthenticated POSTs and triggers Telegram + D1 + email side effects
type: project
---

# 🚨 SECURITY ALERT — agentmail-webhook (HIGH)

**Date**: 2026-05-05
**Found by**: security-engineer-tech BOOP (security-posture-boop)
**Endpoint**: `https://onboarding-api.purebrain.ai/webhook`
**Worker**: `workers/agentmail-webhook/src/worker.js`
**Commit introducing**: `1601cf1` (Apr 30, 2026)
**Status**: LIVE / EXPLOITABLE / CONFIRMED

## Vulnerability

`handleWebhook()` lines 294–313: webhook secret check is in "learning mode" — logs mismatches but **proceeds anyway**. Any internet caller can POST and trigger:

1. **Telegram spam to Jared** (chat_id 548906264) with attacker-controlled subject/body
2. **D1 writes** to `magic_links` table if attacker crafts a body matching `FIELD_PATTERNS` (line 33)
3. **Welcome emails to arbitrary addresses** via welcome-email-api (Brevo) — phishing/abuse vector
4. **Updates to `clients` table** (`ai_name`, `magic_link`) for any matching email

## Proof

```bash
curl -s -X POST https://onboarding-api.purebrain.ai/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"sec.test","data":{"from":"sec-audit@aether.local","subject":"sec-posture-boop noop probe","text":"NOT a magic link, just a noop probe"}}'
# → {"ok":true,"action":"notified","reason":"not_magic_link"}
```

Result: 200 OK, Telegram notification dispatched (you should have received this probe).

## Secondary Findings (MEDIUM)

- **`handleProcessEmail` env mutation** (lines 616–619): mutates `env.AGENTMAIL_WEBHOOK_SECRET = null` then restores. If `handleWebhook` throws, secret stays null. Not currently exploitable (auth check is already broken) but is a footgun once auth is fixed.
- **`handleMagicLinkPoll` no auth + CORS `*`**: Any site can probe `/api/magic-link/:uuid?email=X`. UUIDs are random-enough, but emails are guessable. An attacker who knows a customer email can race the legit user to the magic link before they click.
- **PII in worker logs**: line 355 logs first 500 chars of email body. Cloudflare workers logs may surface to dashboards.

## Fix (ST#)

```js
// In handleWebhook, replace lines 309-312 with:
if (!matched) {
  return jsonResponse({ ok: false, error: 'Unauthorized' }, 401);
}
```

Before deploying:
1. Confirm AgentMail's actual webhook header format (check `tail logs` for what AgentMail sent on Apr 30 → today).
2. `wrangler secret put AGENTMAIL_WEBHOOK_SECRET` if not already set.
3. Tighten the matched header list to one canonical name once known.
4. For `handleMagicLinkPoll`: require both UUID AND email match for the row (not OR), or rate-limit by email lookup.
5. Remove auth-header logging (lines 283–290) — once verified, attackers can fingerprint our header acceptance.

## Other commits reviewed (last 7 days)

| Commit | Risk | Notes |
|--------|------|-------|
| `b90ce6d` SEO og:image | None | Static HTML only |
| `cc517f6` FAQPage JSON-LD | None | Schema markup only |
| `4f729a3` FAQPage blog | None | Static HTML only |
| `83eccfc` 777-api sheet alias | LOW | Origin-locked to 777.purebrain.ai (already vetted) |
| `08eb247` og:image | None | Static HTML only |
| `95499ee` PureSurf BaaS rotate | RESOLVED | Dead key replaced; Worker proxy migration noted as TODO |
| `1601cf1` agentmail-webhook | **HIGH** | This finding |

## CVE check

No matching CVEs for Cloudflare Workers / D1 / Brevo SDK in the last 7 days that affect this stack. Watch:
- Cloudflare Workers runtime advisories
- AgentMail webhook signing format (no public spec yet — see why we're in "learning mode")
