# PayPal API Setup - Full Walkthrough

## Step 1: Go to developer.paypal.com
- Open https://developer.paypal.com in your browser
- Click "Log in to Dashboard" (top right)
- Log in with your PayPal business account credentials

## Step 2: Create a Live App
- In the left sidebar, click **"Apps & Credentials"**
- Make sure the toggle at top says **"Live"** (NOT Sandbox)
- Click **"Create App"**
- App Name: `PureBrain Subscriptions` (or whatever you prefer)
- App Type: **Merchant**
- Click **"Create App"**

## Step 3: Copy Your Credentials
After creating the app, you'll see:
- **Client ID**: A long string starting with something like `AV8r...`
- **Secret**: Click "Show" to reveal it

**Send me BOTH of these via Telegram.** I'll use them to:
1. Create 4 subscription plans (Starter $49, Growth $149, Scale $499, Unified $999)
2. Plug the Plan IDs into the pay-test pages
3. Make the PayPal buttons actually process real payments

## Step 4: (Optional) Sandbox Credentials for Testing
- Toggle from "Live" to **"Sandbox"** at the top
- Either use the default sandbox app or create a new one
- Copy the Sandbox Client ID and Secret too
- These let us test on pay-test-sandbox without real charges

## What I'll Do Once I Have the Credentials
1. **Create a Products resource** (PureBrain AI subscriptions)
2. **Create 4 Billing Plans** with correct pricing:
   - Starter: $49/month
   - Growth: $149/month
   - Scale: $499/month
   - Unified: $999/month
3. **Get Plan IDs** back from PayPal
4. **Update pay-test pages** with real Plan IDs
5. **Test the full purchase flow** on sandbox first
6. **Go live** on the real pay-test page

## Security Note
- The Client ID is semi-public (it appears in browser JS)
- The Secret is PRIVATE - I'll store it securely in .env
- Never share the Secret publicly

## Time Estimate
Once I have the credentials, the API setup takes about 5-10 minutes. The subscription plans will be created programmatically - no manual PayPal dashboard work needed on your end.
