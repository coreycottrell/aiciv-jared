# PayPal Setup - What I Need From You

## Current State (What I Found)
- PayPal SDK is loaded with Client ID `AWgWNlBQ...`
- The modals display tier info correctly (Awakened $79, Bonded $149, Partnered $499)
- **BUT**: No PayPal buttons appear because **Subscription Plan IDs are empty**
- The "Unified" ($999) tier has "Contact Us" button and isn't connected to PayPal at all
- Enterprise tier has "Let's Talk" button

## Why Buttons Are Blank
The PayPal SDK needs **Subscription Plan IDs** to create recurring payment buttons. Without them, it tries to render one-time payment buttons but may be failing due to the Client ID configuration.

Plan IDs look like: `P-5ML4271244454362WXNWU5NQ`

## What I Need From You

### 1. SUBSCRIPTION PLANS (Most Important)
Have you created recurring subscription plans in your PayPal dashboard?

**Where to find/create them:**
- Log into paypal.com
- Go to: **Pay & Get Paid > Subscriptions > Subscription Plans**
- You need a plan for each tier:
  - Awakened ($79/month)
  - Bonded ($149/month)
  - Partnered ($499/month)
  - Unified ($999/month)
- Each plan has a **Plan ID** starting with `P-`

**If NOT created yet**, I can walk you through creating them (5 min each).

### 2. SANDBOX (For pay-test-sandbox page)
For the sandbox version, you need:
- A **Sandbox Client ID** (separate from live)
- **Sandbox Plan IDs** (separate from live plans)

**Where to find:**
- Go to: developer.paypal.com > My Apps & Credentials > **Sandbox** tab
- Create a sandbox app if you don't have one
- The sandbox Client ID will let you test payments without real charges

### 3. ENTERPRISE "Let's Talk" Button
Where should this link? Options:
- a) Email: mailto:support@puremarketing.ai
- b) Contact form page on purebrain.ai
- c) Calendar booking link (Calendly, etc.)
- d) Something else?

### 4. Is `AWgWNlBQ...` a Live or Sandbox Client ID?
I need to know which environment this belongs to, so I can configure the right page correctly.

## Once I Have These
I'll:
1. Plug Plan IDs into the existing script configuration
2. Add Unified ($999) tier to the payment system
3. Change "Contact Us" → "Get Started" on both pages
4. Configure sandbox version for pay-test-sandbox
5. Configure live version for pay-test
6. Verify PayPal buttons render in all modals
