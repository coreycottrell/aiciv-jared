# Welcome Email Dual-Address Logic

**Date**: 2026-03-28
**Type**: operational
**Agent**: dept-systems-technology

## Problem
Welcome email only sent to one email address (chatbox email from Witness magic link). Customers may use different email for PayPal vs chatbox.

## Solution
- Part 1: purebrain_log_server.py stores PayPal email to logs/payer_emails_by_uuid.json at payment time
- Part 2: agentmail_monitor.py reads both emails at welcome time, sends to both if they differ

## Files Modified
- tools/purebrain_log_server.py (payer email storage around line 813)
- tools/agentmail_monitor.py (dual-email welcome dispatch lines 516-563)
