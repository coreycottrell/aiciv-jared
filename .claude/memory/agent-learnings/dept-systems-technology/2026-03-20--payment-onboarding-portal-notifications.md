# Payment/Onboarding Portal Notifications

**Date**: 2026-03-20
**Type**: operational
**Topic**: Added tmux + Telegram notifications for all three payment/onboarding endpoints

## What Was Done

Added real-time notifications to three endpoints in `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`:

### 1. verify_payment (line ~725)
- Fires when someone pays via PayPal
- tmux injection + Telegram message
- Message format: fire NEW PAYMENT {name} just paid ${amount} ({tier}) on {page} / Subscription: {sub_id} / Email: {email}

### 2. send_seed (line ~1462)
- Fires when seed email is dispatched to Witness
- tmux injection + Telegram message
- Message format: seedling SEED FIRED {human_name} (AI: {ai_name}) — seed sent to Witness / Email / Tier / UUID

### 3. seed_addendum (line ~1637)
- Fires when customer clicks ENTER YOUR AI'S BRAIN STREAM
- tmux injection only (no Telegram — lower priority event)
- Message format: clipboard SEED ADDENDUM {ai_name} for {human_name} — questionnaire data sent to Witness

## Pattern Used

Each notification function uses default-argument capture to avoid closure variable bugs.
Fires in daemon=True background threads so API response is not delayed.
Uses existing _send_telegram_notification() helper for TG delivery.
tmux send-keys uses '' (empty string) not 'Enter' — message appears passively.

## Files Changed
- /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py
- Backup: tools/purebrain_log_server.py.bak.payment-notifications-20260320

## Verification
- python3 -m py_compile — Syntax OK
- sudo systemctl restart aether-logserver.service — Active (running) confirmed
