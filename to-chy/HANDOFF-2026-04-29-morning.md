# HANDOFF FOR CHY — April 29, 2026 Morning

## WHAT YOU SHIPPED LAST NIGHT (Great work!)
1. **staging-voice.purebrain.ai** — CF Worker + D1 + DNS + full frontend + production features ported
2. **staging-face.purebrain.ai** — CF Worker + D1 + 13 avatars + Claude chat + FLUX portraits
3. Both plans uploaded to Google Drive as Google Docs

## JARED'S CURRENT PRIORITIES
1. **CRITICAL SECURITY FIX**: Referral payout endpoints (/paypal-email, /payout-request) authenticate with ONLY the referral code — no password, no session. Referral codes are public (leaderboard). Aether confirmed: can change anyone's PayPal email with just their code. NEEDS SESSION AUTH.
2. **Brainiac modules 7+8**: Videos are in training hub but module PAGES aren't linked (no Launch Module button or AI Training Snippet sections for 7+8)
3. **Social-api local changes**: Your production Worker is correct. Local git has stale 3,678-line deletion diff — Jared wants confirmation these can be discarded
4. **Staging-voice testing**: Jared will test Generate tab today
5. **Staging-face testing**: Jared will test avatar chat today

## YOUR STAGING PLATFORMS — STATUS
- staging-voice: HEALTHY (health check OK)
- staging-face: HEALTHY (health check OK, 13 avatars loaded)
- ANTHROPIC_API_KEY set on face-api-staging

## MORPHE
- Voice samples uploaded to Drive (Chy voice tone reference)
- Jared reviewing in morning to pick direction
- Morphe needs unique voice trained on Chatterbox

## OVERNIGHT REPORTS (in portal-files/)
- daily-recap-2026-04-28.md
- 9 overnight research reports (blog, site, analytics, distribution, linkedin, etc.)

## ADMIN/SOCIAL INVITE LEAK
- Diagnosed: shared team_invites table without source filter
- Fix: add source column or filter by team_id in admin-api
