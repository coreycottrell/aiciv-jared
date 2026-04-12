# Pure Brain Referral System Recommendation

**Date**: 2026-02-05
**Purpose**: Evaluate WordPress referral plugins vs custom solution for Pure Brain Portal

---

## Executive Summary

**My Recommendation: SliceWP (Free) + Custom Integration OR Custom-Coded Solution**

After research, here are your two best paths:

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **SliceWP Free** | Fast setup, proven, WooCommerce integration | REST API requires Pro ($149+/yr), limited customization | Quick MVP if using WooCommerce |
| **Custom Coded** | Full control, no plugin dependencies, exact fit for Pure Brain | More dev time upfront | Long-term scalability, custom rewards |

**If Pure Brain Portal has its own user auth system (not WooCommerce)**, go custom. It's simpler to integrate.

---

## Option 1: SliceWP (WordPress Plugin)

### What It Is
SliceWP is a 4.9-star rated WordPress affiliate plugin with 343K+ downloads.

### Free Features
- Unlimited affiliates
- Automatic commission tracking
- Affiliate dashboard (registration, login, stats)
- Custom referral links
- Email notifications
- WooCommerce, EDD, MemberPress integrations

### Installation Steps

1. **Install Plugin**
   ```
   WordPress Admin > Plugins > Add New > Search "SliceWP" > Install > Activate
   ```

2. **Run Setup Wizard**
   - Go to SliceWP menu that appears
   - Follow wizard to create affiliate pages
   - Configure commission rates (% or flat)
   - Set cookie duration (30 days default)

3. **Configure Integration**
   - SliceWP > Integrations > Enable WooCommerce (or your platform)
   - Set commission rate (e.g., 10%)

4. **Create Affiliate Pages**
   - SliceWP auto-creates: Register, Login, Account pages
   - Customize with your branding

### API Access (For Pure Brain Integration)

**Problem**: SliceWP REST API requires Pro license ($149/year)

**Workaround for Free Version**:
- Use WordPress hooks in `functions.php`
- Create custom REST endpoints
- Use WP Webhooks plugin (free) for triggers

### WordPress to Pure Brain Connection

Add this to your theme's `functions.php`:

```php
// Custom REST endpoint to check affiliate status
add_action('rest_api_init', function() {
    register_rest_route('purebrain/v1', '/affiliate/(?P<code>[a-zA-Z0-9]+)', array(
        'methods' => 'GET',
        'callback' => 'purebrain_check_affiliate',
        'permission_callback' => '__return_true'
    ));
});

function purebrain_check_affiliate($request) {
    $code = $request['code'];
    // Query SliceWP affiliate by code
    global $wpdb;
    $affiliate = $wpdb->get_row(
        $wpdb->prepare("SELECT * FROM {$wpdb->prefix}slicewp_affiliates WHERE id = %s", $code)
    );

    if ($affiliate) {
        return array(
            'valid' => true,
            'affiliate_id' => $affiliate->id,
            'user_id' => $affiliate->user_id
        );
    }
    return array('valid' => false);
}

// Webhook when new referral is created
add_action('slicewp_insert_commission', function($commission_id, $data) {
    // Send to Pure Brain Portal
    wp_remote_post('https://purebrain.ai/api/webhooks/referral', array(
        'body' => json_encode(array(
            'event' => 'new_referral',
            'affiliate_id' => $data['affiliate_id'],
            'amount' => $data['amount'],
            'reference' => $data['reference']
        )),
        'headers' => array(
            'Content-Type' => 'application/json',
            'X-Webhook-Secret' => 'your-secret-key'
        )
    ));
}, 10, 2);
```

---

## Option 2: Custom-Coded Referral System (Recommended for Pure Brain)

### Why Custom Might Be Better

1. **No plugin dependencies** - Won't break with WordPress updates
2. **Direct integration** - Built into Pure Brain Portal backend
3. **Full control** - Exact features you need, nothing extra
4. **Simpler architecture** - No WordPress <-> Portal sync needed

### What You Need

1. **Referral codes** - Unique code per user
2. **Tracking** - Record when code is used at signup
3. **Rewards** - Credit system for successful referrals
4. **Dashboard** - Show users their stats

### Database Schema

```sql
-- Referral codes (one per user)
CREATE TABLE referral_codes (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    code VARCHAR(12) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Referral tracking
CREATE TABLE referrals (
    id UUID PRIMARY KEY,
    referrer_id UUID REFERENCES users(id),
    referred_id UUID REFERENCES users(id),
    code_used VARCHAR(12),
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, cancelled
    reward_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Reward balance
CREATE TABLE referral_rewards (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    balance DECIMAL(10,2) DEFAULT 0,
    total_earned DECIMAL(10,2) DEFAULT 0,
    total_withdrawn DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Claude Code Implementation Prompt

```
I need to implement a Refer & Earn system for Pure Brain AI Portal.

Requirements:

1. REFERRAL CODE GENERATION
   - Each user gets a unique referral code (8 chars, alphanumeric)
   - Code displayed on user's dashboard
   - Shareable link: https://purebrain.ai/?ref=CODE

2. REFERRAL TRACKING
   - When new user signs up with ?ref=CODE in URL:
     a) Store referral code in session/cookie
     b) On successful registration, credit the referrer
   - Track: referrer_id, referred_id, code_used, timestamp

3. REWARD SYSTEM
   - Configurable reward amount (default: $5 credit or 1 month free)
   - Rewards become "available" after referred user:
     a) Completes registration AND
     b) Stays active for 7 days (prevents gaming)
   - Track pending vs available rewards

4. REFERRAL DASHBOARD (User-facing)
   - Show user's unique referral code
   - Copy link button
   - Stats: total referrals, pending, completed
   - Earnings: pending balance, available balance
   - Referral history table

5. ADMIN DASHBOARD
   - View all referrals
   - Approve/reject pending rewards
   - Adjust reward amounts
   - Export data

6. API ENDPOINTS
   POST /api/referral/generate     - Generate code for user
   GET  /api/referral/stats        - Get user's referral stats
   GET  /api/referral/history      - Get referral history
   POST /api/referral/track        - Track referral at signup
   POST /api/referral/complete     - Mark referral as complete

7. FRONTEND COMPONENTS
   - ReferralDashboard: Main container
   - ReferralCodeCard: Shows code + copy button
   - ReferralStats: Numbers display
   - ReferralHistory: Table of referrals
   - ShareButtons: Social share options

8. ANTI-FRAUD MEASURES
   - One code per user
   - Cannot refer yourself
   - IP tracking for suspicious activity
   - Email domain matching detection
   - Manual review for bulk referrals

Tech stack: React, TypeScript, Node.js/Express, PostgreSQL
Include database migrations, API routes, and React components.
```

---

## Side-by-Side Comparison

| Feature | SliceWP Free | Custom Coded |
|---------|--------------|--------------|
| Setup time | 1 hour | 1-2 days |
| Cost | $0 (Free), $149/yr for API | Dev time only |
| REST API | Pro only | Full control |
| WooCommerce | Native | Requires integration |
| Custom rewards | Limited | Full flexibility |
| Maintenance | Plugin updates | Your code |
| Scalability | Plugin limits | Unlimited |
| Pure Brain fit | Needs bridging | Native |

---

## My Final Recommendation

**Go Custom** if:
- Pure Brain Portal has its own user system (not WordPress/WooCommerce)
- You want full control over reward logic
- You plan to scale beyond basic referrals

**Go SliceWP** if:
- You need it live TODAY
- Pure Brain uses WooCommerce for payments
- You're OK with Pro license later for API access

---

## Quick Start: SliceWP Installation Guide

### Step 1: Install Plugin
1. Login to WordPress Admin
2. Go to **Plugins > Add New**
3. Search "SliceWP"
4. Click **Install Now** then **Activate**

### Step 2: Run Setup Wizard
1. After activation, click **SliceWP** in sidebar
2. Click **Start Setup Wizard**
3. Follow prompts:
   - Choose integration (WooCommerce/EDD/etc)
   - Set commission rate (e.g., 10%)
   - Set cookie duration (30 days)
4. Click **Finish**

### Step 3: Configure Pages
1. Go to **SliceWP > Settings > General**
2. Verify auto-created pages:
   - Affiliate Register page
   - Affiliate Login page
   - Affiliate Account page
3. Customize page content if needed

### Step 4: Add to Pure Brain Refer & Earn Section
1. Get the affiliate registration URL from SliceWP
2. Link "Become an Affiliate" button to that page
3. Embed affiliate dashboard using shortcode: `[slicewp_affiliate_account]`

### Step 5: Connect to Pure Brain Backend
Add the webhook code (from Option 1 above) to your theme's `functions.php`

---

## Sources

- [SliceWP Official](https://slicewp.com/)
- [SliceWP REST API Docs](https://slicewp.com/docs/rest-api/)
- [WordPress.org - SliceWP Plugin](https://wordpress.org/plugins/slicewp/)
- [WordPress.org - Affiliates Plugin](https://wordpress.org/plugins/affiliates/)
- [ReferralCandy - Best WordPress Referral Plugins](https://www.referralcandy.com/blog/wordpress-referral-plugin)

---

**Created by Aether for Pure Brain AI**
