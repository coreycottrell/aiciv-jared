# content-specialist Learning: Website Analysis Delivery Email Template

**Date**: 2026-02-24
**Type**: operational + pattern
**Agent**: content-specialist
**Topic**: Post-purchase transactional email for AI Website Analysis product delivery

---

## Task Summary

Created a complete HTML + plain text email template for automated delivery of password-protected website analysis reports. Triggered after purchase of the AI Website Analysis product at purebrain.ai/ai-website-analysis/.

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/email-templates/website-analysis-delivery.html`
- `/home/jared/projects/AI-CIV/aether/exports/email-templates/website-analysis-delivery.txt`

---

## Template Variables

Four variables used in this template (simpler than PureBrain partner emails):

- `{{FIRST_NAME}}` — Buyer's first name
- `{{REPORT_URL}}` — Full URL to the password-protected report page (e.g., https://purebrain.ai/client-report-duckdive/)
- `{{REPORT_PASSWORD}}` — Password to enter on the report page
- `{{COMPANY_NAME}}` — Company name whose site was analyzed
- `{{UNSUBSCRIBE_URL}}` — Brevo unsubscribe link (standard Brevo variable)

---

## Key Design Decisions

### 1. "Analysis Complete" Badge in Orange

The hero uses an orange badge (not blue) to signal completion/action. This follows the established CTA color logic from the post-purchase welcome email: orange = action/energy. The badge creates immediate status clarity before the reader processes any text.

### 2. Password in Monospace with Left Border Accent

The password field uses `font-family: 'Courier New'` with a left border in orange (#f1420b) and a slightly lit background. This makes the password visually distinct, easy to copy, and impossible to miss. Placing it inside a labeled box (not just inline text) prevents the password from being skimmed past.

### 3. "What's Inside" 2x2 Grid

Four panels (SEO/Visibility, AI Readability, Conversion/UX, Priority Action Plan) give the buyer a preview of value before they even click. This reinforces the purchase decision and reduces buyer's remorse. The alternating blue/orange border treatment mirrors PureBrain brand colors systematically.

### 4. Three-Step "Next Steps" Section

Numbered steps with circle badges reduce cognitive friction. Step 3 ("Reply to this email") explicitly invites reply engagement — which is intentional. For a paid analysis product, human conversation is a natural upsell vector.

### 5. Sign-Off Framing

"Use it well" closing is brief, confident, and treats the buyer as capable. Avoids over-explaining or hedging. Consistent with PureBrain's "intelligent partner" tone rather than generic SaaS support speak.

### 6. "AI Readability (GEO)" Naming

The report section label deliberately uses "AI Readability (GEO)" — this surfaces PureBrain's GEO/AIO positioning inside the product delivery email. First touchpoint for many buyers to encounter the term.

---

## Tone Register for This Email

This email is a product delivery, not a relationship-building sequence. The tone is:
- **Congratulatory but not gushing** — buyer made a smart decision, not a miraculous one
- **Confident** — the report is good, no hedging about findings
- **Direct** — the email has one job: get them to click and access the report
- **Personal close** — "a real person reads every message" because this is a premium paid product

---

## Structural Sections (in order)

1. Header (logo + tagline)
2. Hero (badge + headline + congratulations)
3. Report Access (heading + CTA button + password box + URL helper)
4. What's Inside (4-panel grid)
5. Next Steps (3-step numbered list)
6. Questions / Support (reply CTA)
7. Sign-off (personal close)
8. Footer (social links + legal)

---

## Brevo Configuration Notes

- Trigger: purchase completion webhook from payment processor (PayPal)
- Template type: Transactional (not automation sequence)
- Sender name: PureBrain or "Jared at PureBrain"
- Reply-to: should be a monitored inbox (purebrain@puremarketing.ai)
- Subject line recommendation: "{{FIRST_NAME}}, your website analysis is ready — here's your password"
- Preview text recommendation: "Your AI-powered analysis of {{COMPANY_NAME}} is complete. Click to access your private report."

---

## Reusable Patterns

### Password Delivery Box Pattern

```html
<div style="font-size: 11px; letter-spacing: 2px; color: rgba(42, 147, 193, 0.65); text-transform: uppercase; font-weight: 600; margin-bottom: 12px;">
  Report Access Password
</div>
<div style="font-size: 22px; font-weight: 700; color: #ffffff; font-family: 'Courier New', Courier, monospace; letter-spacing: 3px; padding: 10px 16px; background: rgba(42, 147, 193, 0.08); border-radius: 6px; border-left: 3px solid #f1420b;">
  {{REPORT_PASSWORD}}
</div>
```

Reusable for any product that delivers credentials (login passwords, API keys, access codes).

### "What's Inside" 2x2 Preview Grid

Alternating blue/orange border cells. Useful for any product delivery that has 4 distinct value areas. The cell pattern is table-based and email-safe.

---

## Memory Search Applied

- `2026-02-20--post-purchase-welcome-email-templates.md`: HTML structure (table-based, 600px, dark theme), logo wordmark treatment, CTA color logic, "partnership not subscription" language
- `2026-02-23--migration-email-sequences-chatgpt-claude-gemini.md`: Voice calibration, avoided generic SaaS language
- `2026-02-18--purebrain-nurture-email-sequence.md`: Sign-off tone, emotional arc principles

---

**END MEMORY**
