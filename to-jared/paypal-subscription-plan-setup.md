# PayPal Subscription Plan Setup - Step by Step

## Overview
You need to create 4 subscription plans in PayPal (one per pricing tier). Each plan generates a Plan ID (starts with "P-") that I'll plug into the website code.

---

## STEP 1: Log Into PayPal Business Dashboard

1. Go to **https://www.paypal.com** and log in with your business account (support@puremarketing.ai)
2. Make sure you're on the **Business** dashboard (not personal)

---

## STEP 2: Navigate to Subscriptions

1. Click **"Pay & Get Paid"** in the top navigation
2. Click **"Subscriptions"** from the dropdown
3. You'll see the Subscriptions dashboard

> **If you don't see "Subscriptions"**: Click "More" or look under "Accept Payments" > "Subscriptions"

---

## STEP 3: Create a Product First (One-Time Only)

Before creating plans, you need a "Product" (this is just a label for the service):

1. Click **"Create Plan"** (or "Products & Plans" > "Create Product")
2. Fill in:
   - **Product name**: `PureBrain.ai AI Partnership`
   - **Product type**: `Service`
   - **Description**: `AI partnership and consulting subscription`
   - **Category**: `Software` or `Consulting Services`
3. Click **"Create Product"** or **"Next"**

---

## STEP 4: Create Plan #1 - Awakened ($79/month)

1. Under the product you just created, click **"Create Plan"**
2. Fill in:
   - **Plan name**: `Awakened`
   - **Description**: `AI awareness and basic integration - $79/month`
   - **Billing cycle**:
     - **Interval**: `Month`
     - **Interval count**: `1` (every 1 month)
     - **Price**: `$79.00`
     - **Currency**: `USD`
   - **Total cycles**: `0` (infinite/ongoing)
   - **Setup fee**: `$0.00` (no setup fee)
   - **Tax**: Leave as default
3. Click **"Create Plan"**
4. **COPY THE PLAN ID** - It will look like: `P-5ML4271244454362WXNWU5NQ`

**Send me this Plan ID!**

---

## STEP 5: Create Plan #2 - Bonded ($149/month)

Repeat the same steps:
1. Click **"Create Plan"** under the same product
2. Fill in:
   - **Plan name**: `Bonded`
   - **Description**: `Deep AI integration with priority support - $149/month`
   - **Billing cycle**: Monthly, $149.00 USD
3. Click **"Create Plan"**
4. **COPY THE PLAN ID**

---

## STEP 6: Create Plan #3 - Partnered ($499/month)

1. Click **"Create Plan"**
2. Fill in:
   - **Plan name**: `Partnered`
   - **Description**: `Full AI partnership with consulting - $499/month`
   - **Billing cycle**: Monthly, $499.00 USD
3. Click **"Create Plan"**
4. **COPY THE PLAN ID**

---

## STEP 7: Create Plan #4 - Unified ($999/month)

1. Click **"Create Plan"**
2. Fill in:
   - **Plan name**: `Unified`
   - **Description**: `Complete AI integration with dedicated consulting - $999/month`
   - **Billing cycle**: Monthly, $999.00 USD
3. Click **"Create Plan"**
4. **COPY THE PLAN ID**

---

## STEP 8: Send Me the Plan IDs

Send me all 4 Plan IDs in this format:
```
Awakened: P-XXXXXXXXXXXXXXXXXXXX
Bonded: P-XXXXXXXXXXXXXXXXXXXX
Partnered: P-XXXXXXXXXXXXXXXXXXXX
Unified: P-XXXXXXXXXXXXXXXXXXXX
```

---

## FOR SANDBOX (pay-test-sandbox page)

To create sandbox plans for testing:

1. Go to **https://developer.paypal.com**
2. Log in with your PayPal account
3. Click **"Dashboard"** or **"My Apps & Credentials"**
4. Switch to the **"Sandbox"** tab
5. Under "REST API Apps" - note your **Sandbox Client ID**
6. To create sandbox plans:
   - Go to **https://www.sandbox.paypal.com**
   - Log in with your sandbox business account
   - Follow the same steps above (Pay & Get Paid > Subscriptions > Create Plan)
   - The sandbox Plan IDs will be different from live ones

**Send me:**
- Sandbox Client ID
- 4 Sandbox Plan IDs

---

## WHAT HAPPENS AFTER

Once I have the Plan IDs, I will:
1. Plug them into the website JavaScript configuration
2. The PayPal "Subscribe" buttons will immediately appear in the modals
3. Customers click → PayPal opens → they subscribe → recurring billing starts
4. You manage subscriptions in PayPal dashboard (cancel, refund, etc.)

---

## TIME ESTIMATE
- Creating the product: 2 minutes
- Creating each plan: 2-3 minutes each
- Total: ~15 minutes for all 4 live plans
- Sandbox: Additional 15 minutes

---

## QUICK TIP
If you can't find "Subscriptions" in PayPal:
- Make sure your account is a **Business** account (not Personal)
- Try: paypal.com > click your profile > Account Settings > look for "Payment Preferences" or "Subscription Plans"
- Or search "subscription plans" in PayPal's search bar
