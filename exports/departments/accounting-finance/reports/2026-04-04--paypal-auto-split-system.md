# AF# Report: PayPal Auto-Split Payout System

**Department**: Accounting & Finance
**Date**: 2026-04-04
**Prepared by**: dept-accounting-finance

---

## System Overview

Built and deployed the PayPal auto-split payout system per Jared's approved configuration:

- **Option A**: PayPal Payouts from bank (all revenue hits PT bank first)
- **Option C**: Approval mode (Jared clicks approve before each payout fires)

## Split Formula

```
Gross Payment
  - $35.00  AICIV Ops Fee (fixed)
  - 5%      Referral Fee (of gross)
  = Net After Fees
    -> 60% to Corey (AICIV) via PayPal: weaver.aiciv@gmail.com
    -> 40% to Pure Tech (Jared)
```

### Example: $149 Awakened Tier

| Line Item | Amount |
|-----------|--------|
| Gross | $149.00 |
| Ops Fee | -$35.00 |
| Referral (5%) | -$7.45 |
| **Net After Fees** | **$106.55** |
| Corey's Share (60%) | $63.93 |
| Pure Tech Share (40%) | $42.62 |

## Components Delivered

### 1. Payout Tracker Tab (Google Sheets)
- **Spreadsheet**: `1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ`
- **Tab**: "Payout Tracker"
- 13 columns: Date, Customer, Tier, Gross, Ops Fee, Referral, Net, Corey Share, PT Share, Status, Payout ID, Payout Date, Notes
- Auto-calculating formulas in E (ops fee), F (referral), G (net), H (60%), I (40%)
- Conditional formatting on Status column: Yellow=Pending, Blue=Approved, Green=Sent, Red=Failed
- Summary section at top: Total Revenue, Total Paid to Corey, Total Pending, Total Pure Tech
- Frozen header rows

### 2. Payout Script (`tools/paypal_auto_split.py`)

**CLI Commands**:
```bash
# Setup the spreadsheet tab (already done)
python3 tools/paypal_auto_split.py --setup-sheet

# Add a payment (status: Pending Approval)
python3 tools/paypal_auto_split.py --add-payment --customer "Faris Asmar" --tier "Awakened" --amount 149

# View all pending payouts
python3 tools/paypal_auto_split.py --status

# View financial summary
python3 tools/paypal_auto_split.py --summary

# Approve and fire PayPal payout (Jared's action)
python3 tools/paypal_auto_split.py --approve --row 8

# Run webhook listener (for automated payment detection)
python3 tools/paypal_auto_split.py --webhook

# Use sandbox for testing
python3 tools/paypal_auto_split.py --sandbox --add-payment --customer "Test" --tier "Awakened" --amount 149
```

**Webhook Mode**: Listens on port 8960 for `PAYMENT.SALE.COMPLETED` events from PayPal.

## Credentials Status

| Credential | Status |
|-----------|--------|
| PAYPAL_CLIENT_ID | Present in .env (live) |
| PAYPAL_SECRET | Present in .env (live) |
| PAYPAL_SANDBOX_CLIENT_ID | Present in .env |
| PAYPAL_SANDBOX_SECRET | Present in .env |
| Google Sheets OAuth | Working (.credentials/oauth-token.json) |

## Approval Flow

1. Payment received (via webhook or manual `--add-payment`)
2. Row added to Payout Tracker with status "Pending Approval" (yellow)
3. Jared reviews in spreadsheet or portal notification
4. Jared runs `--approve --row N` (or future portal button)
5. PayPal Payout fires to weaver.aiciv@gmail.com
6. Row updated: status "Sent" (green), Payout ID recorded, date stamped

## Bottom Line

System is built, tested, and ready. Spreadsheet tab is live with formatting. Script handles the full lifecycle: record payment, calculate split, await approval, fire PayPal payout, track status. All PayPal credentials are in .env and verified.

## Files

- Script: `/home/jared/projects/AI-CIV/aether/tools/paypal_auto_split.py`
- Report: `/home/jared/projects/AI-CIV/aether/exports/departments/accounting-finance/reports/2026-04-04--paypal-auto-split-system.md`
- Logs: `/home/jared/projects/AI-CIV/aether/logs/paypal_auto_split.log`
- Spreadsheet: https://docs.google.com/spreadsheets/d/1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ
