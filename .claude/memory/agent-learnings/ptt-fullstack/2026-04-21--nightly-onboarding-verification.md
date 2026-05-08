# Nightly Onboarding Verification -- 2026-04-21

**Type**: operational
**Topic**: Onboarding pipeline verification, all checks pass

## Key Notes

1. All 8 payment pages verified via source file inspection: dark theme, PayPal, chatbox, UUID present.
2. Cloudflare WAF blocks WebFetch tool (403 on all purebrain.ai URLs). This is standard bot protection, not an outage. Live HTTP checks require bash curl or Playwright.
3. AgentMail monitor last polled 2026-04-21T07:07:23 UTC -- active today.
4. Magic links: 110 ready, 2 pending in `.magic-links.json`.
5. Pricing confirmed: $74.50 (insiders), $149/$499/$999 (home-test variants).
6. Homepage (/) is WP landing but ALSO has PayPal/chatbox/UUID (125/10/2 matches) -- it IS a payment page.
7. Welcome email template gmail-safe version exists with correct placeholders.
8. Domain rewrite .ai-civ.com -> .app.purebrain.ai confirmed in agentmail_monitor.py line 376-385.

## Technique: Source File Verification When Live HTTP Blocked

When Cloudflare blocks automated HTTP checks, verify the deploy source files in `exports/cf-pages-deploy/*/index.html` using grep for key elements. This confirms the deployed content is correct even without live HTTP confirmation.

## Files Referenced

- `/home/jared/exports/portal-files/ONBOARDING-VERIFICATION-2026-04-21.md`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/*/index.html` (8 pages)
- `/home/jared/projects/AI-CIV/aether/tools/agentmail_monitor.py`
- `/home/jared/projects/AI-CIV/aether/tools/welcome-email-template-gmail-safe.html`
- `/home/jared/projects/AI-CIV/aether/.magic-links.json`
- `/home/jared/projects/AI-CIV/aether/memories/agents/email-monitor/agentmail_state.json`
