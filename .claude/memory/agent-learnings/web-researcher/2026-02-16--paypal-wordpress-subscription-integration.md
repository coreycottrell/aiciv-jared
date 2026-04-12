# PayPal WordPress Subscription Integration Research

**Date**: 2026-02-16
**Agent**: web-researcher
**Type**: synthesis
**Topic**: PayPal subscription button integration for WordPress/Elementor

## Context

Researched how to connect company PayPal to WordPress for accepting monthly subscription payments ($79/mo, $149/mo, $499/mo tiers).

## Key Findings

### Three Integration Approaches (Simplest to Most Robust)

1. **Elementor Pro PayPal Button Widget**
   - Native widget, no plugins needed
   - Transaction Type: Subscription
   - Billing Cycle: Daily/Weekly/Monthly/Yearly
   - Auto-renewal toggle available
   - Just need PayPal merchant email
   - ~15 minute setup

2. **PayPal Smart Subscribe Buttons**
   - Create plans in PayPal dashboard
   - Get Plan ID (starts with "P-")
   - Copy/paste JavaScript code to site
   - More control over subscription management
   - Path in PayPal: Pay & Get Paid > Subscriptions > Subscription Plans

3. **WooCommerce + Subscription Plugin**
   - Options: Flexible Subscriptions (free), YITH WooCommerce Subscription (free), WP Swings
   - Full e-commerce functionality
   - Customer accounts in WordPress
   - Overkill for simple subscription tiers

### Where to Find PayPal Plan IDs
1. Log into PayPal Business account
2. Navigate: Pay & Get Paid > Accept Payments > Subscriptions
3. Click "Subscription Plans" tab
4. Plan IDs in "Plan" column, start with "P-"

### Elementor Widget Settings for Subscriptions
```
Transaction Type: Subscription
Item Name: [Product name]
SKU: [Unique identifier]
Price: [Amount]
Currency: USD
Billing Cycle: Monthly
Auto Renewal: ON
```

### PayPal Smart Subscribe Code Structure
```html
<!-- SDK (once per page) -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&vault=true&intent=subscription"></script>

<!-- Button container -->
<div id="paypal-button-container"></div>

<!-- Render script with Plan ID -->
<script>
paypal.Buttons({
  createSubscription: function(data, actions) {
    return actions.subscription.create({ plan_id: 'YOUR_PLAN_ID' });
  },
  onApprove: function(data, actions) {
    window.location.href = '/thank-you/';
  }
}).render('#paypal-button-container');
</script>
```

## Recommendation

For Pure Brain 2.0 (existing Elementor site, 3 tiers):
- **Start with Elementor Pro PayPal Widget** (simplest)
- PayPal handles all subscription management
- Can upgrade to WooCommerce later if needed

## Sources

- https://elementor.com/help/paypal-button-widget-pro/
- https://elementor.com/academy/how-to-use-the-paypal-button-widget-in-elementor-pro/
- https://www.paypal.com/us/cshelp/article/how-do-i-create-a-subscription-button-help269
- https://developer.paypal.com/docs/subscriptions/integrate/
- https://support.emailmeform.com/hc/en-us/articles/20152234844429-PayPal-Checkout-Where-to-find-Plan-ID-in-Paypal-Business-Account

## When to Apply

- Setting up subscription/membership payment buttons
- Connecting PayPal to WordPress/Elementor
- Choosing between Elementor widgets vs native PayPal code
- Evaluating WooCommerce subscription plugins
