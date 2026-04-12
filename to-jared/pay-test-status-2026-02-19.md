# Pay-Test Pages Status Report
**Date**: 2026-02-19
**Pages**: pay-test (439) + pay-test-sandbox (468)

---

## Current State

| Feature | pay-test (439) | pay-test-sandbox (468) |
|---------|---------------|----------------------|
| **PayPal Mode** | LIVE (real charges) | SANDBOX (no real charges) |
| **Client ID** | Live: AWgWNlBQ... | Sandbox: AYTFob05... |
| **Buttons** | 4x openPayPalModal + 1x Enterprise waitlist | Same |
| **PayPal SDK** | Loaded, ready | Loaded, ready |
| **Exit-intent popup** | Armed at naming (before celebration) | Same |
| **Naming ceremony** | Enhanced (Still's 7 principles) | Same |
| **Testing backdoor** | "pb-admin-bypass" as first message | Same |
| **Testimonials** | Headshot + LinkedIn links synced | Same |
| **Password** | PureBrain.ai253443$$$ | Same |
| **Page status** | Published (password-protected) | Published (password-protected) |

---

## PayPal Plan IDs

### LIVE (page 439)
| Tier | Price | Plan ID |
|------|-------|---------|
| Awakened | $79/mo | P-1AG936074F0953120NGLTFKY |
| Bonded | $149/mo | P-2SA65600MT088594TNGLTFKY |
| Partnered | $499/mo | P-3VH43554A66001716NGLTFKY |
| Unified | $999/mo | P-43A28944XN5237411NGLTFLA |
| Enterprise | Custom | "Let's Talk" → Brevo + Google Sheet |

### SANDBOX (page 468)
| Tier | Price | Plan ID |
|------|-------|---------|
| Awakened | $79/mo | P-9KA28683EF7622051NGLUFJY |
| Bonded | $149/mo | P-1JL98851AU229172RNGLUFJY |
| Partnered | $499/mo | P-6JY35646YA5259513NGLUFKA |
| Unified | $999/mo | P-6DU61407NY0900135NGLUFKI |
| Enterprise | Custom | "Let's Talk" → Brevo + Google Sheet |

---

## Testing the Sandbox

**IMPORTANT**: You CANNOT use your real PayPal account on the sandbox page. PayPal blocks merchants from paying themselves.

### How to test sandbox checkout:
1. Go to `developer.paypal.com/dashboard/accounts`
2. Find the **Personal** (buyer) sandbox account
3. Click `...` → `View/Edit Account`
4. Copy the **Email ID** and **System Generated Password**
5. Open `purebrain.ai/pay-test-sandbox` in incognito
6. Enter page password: `PureBrain.ai253443$$$`
7. Use backdoor: type `pb-admin-bypass` to skip onboarding
8. Click any pricing button → PayPal popup
9. Log in with the sandbox **Personal** account credentials
10. Complete the test subscription

### How to test LIVE checkout:
1. Open `purebrain.ai/pay-test` in incognito
2. Enter page password: `PureBrain.ai253443$$$`
3. Use backdoor or go through full onboarding
4. Click pricing button → real PayPal checkout
5. This charges real money

---

## Testing Backdoor

Type `pb-admin-bypass` as your **first message** in the chat.

The AI will:
- Greet you as Jared
- Pick a unique name instantly
- Skip entire 12-message onboarding
- Be ready for testing immediately

---

## Bugs Fixed Today (2026-02-19)

1. **Exit-intent not triggering** → Was only armed after celebration. Moved to naming moment.
2. **PayPal buttons showing waitlist form** → Override script was hijacking openPayPalModal after 100ms. Removed override + added proper alias.
3. **Orange page (JSON breakage)** → Literal `\n` in PayPal alias broke _elementor_data JSON. Fixed with proper escaping.

---

## Still Pending

- [ ] Page visibility decision: keep password-protected or make public?
- [ ] Russell's + Corey's LinkedIn URLs for testimonial linking
- [ ] app.purebrain.ai login page branding (repo URL needed)
- [ ] CDN cache flush from GoDaddy dashboard (for older cached changes)

---

## Config Files

| File | Purpose |
|------|---------|
| `config/paypal_plans.json` | Live PayPal plan IDs |
| `config/paypal_sandbox_plans.json` | Sandbox PayPal plan IDs |
| `.env` | PayPal credentials (live + sandbox) |

## Key Scripts

| Script | Purpose |
|--------|---------|
| `tools/fix_exit_intent.py` | Exit-intent popup upgrade |
| `tools/fix_exit_intent_timing.py` | Exit-intent timing fix |
| `tools/plug_sandbox_plans.py` | Deploy sandbox credentials to page 468 |
| `tools/sync_testimonials_to_paytest.py` | Sync testimonials from homepage |
| `tools/enhance_naming_ceremony.py` | Enhanced naming in SYSTEM_PROMPT |
