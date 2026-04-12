# PayPal Email Self-Service — Referral System v2.2.0

**Date**: 2026-03-06
**Type**: operational
**Agent**: cto

## What Was Built

Added PayPal email self-service capability to the PureBrain Referral System plugin.

## File Changed

`/home/jared/projects/AI-CIV/aether/tools/security/purebrain-referral/purebrain-referral-system.php`
Version bumped: 2.1.0 → 2.2.0

## Changes Made

### 1. Database
- Added `paypal_email VARCHAR(255) DEFAULT NULL` column to `pb_referral_users` CREATE TABLE
- Added `pb_referral_maybe_add_paypal_email_column()` for ALTER TABLE migration on existing installs
- Migration runs on both activation hook AND `plugins_loaded` action (idempotent, safe to call repeatedly)
- Uses `information_schema.COLUMNS` check before altering — no duplicate column errors

### 2. New REST Endpoints
- `POST /wp-json/pb-referral/v1/paypal-email`
  - Body: `{ "email": "user@example.com", "paypal_email": "paypal@example.com" }`
  - Validates both emails with `is_email()`
  - Verifies user exists by account email before writing
  - Returns `{ ok, referral_code, paypal_email, message }`
- `GET /wp-json/pb-referral/v1/paypal-email?email=user@example.com`
  - Returns `{ email, referral_code, paypal_email }` (paypal_email is null if not set)

### 3. Modified Dashboard Endpoint
- `pb_referral_api_dashboard` now returns `paypal_email` field in response
- Dashboard shortcode JS reads `d.paypal_email` and pre-fills both the PayPal email field in the self-service card AND the payout form input

### 4. Modified Payout Request
- Looks up `$user->paypal_email` (saved on file) when building payout entry
- Payout JSONL entry now includes both `paypal_email` (provided at request time) and `saved_paypal_email` (on file)
- Telegram notification to Jared now includes "Saved PayPal" line with comparison note (matches / different / none on file)
- Payout request still uses the email the user provides at request time — saved email is informational

### 5. Dashboard UI
- New "PayPal Email" card in dashboard shortcode with input + "Save PayPal Email" button
- Pre-fills from `d.paypal_email` on dashboard load
- Saving also pre-fills the payout request form field
- Payout form input label updated to note "Pre-filled from your saved PayPal email"

## Architecture Notes
- Referral plugin is separate from security plugin — safe to modify per SECURITY PLUGIN ISOLATION RULE
- Both GET and POST registered under the same `/paypal-email` route path — WP_REST_Server dispatches by HTTP method
- `sanitize_email()` used for all email inputs; `is_email()` used for validation
- No authentication enforced (consistent with rest of plugin) — ownership gated by requiring a valid account email that matches an existing user row
