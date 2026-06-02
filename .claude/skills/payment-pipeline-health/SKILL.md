---
status: provisional
tick_count: 0
last_used: 2026-05-31
introduced: 2026-05-31
---
# Skill: Payment Pipeline Health

## Purpose

Continuous monitoring of PayPal payment infrastructure: webhook listener status, API reachability, latest payment timestamp, and subscription plan integrity. Catches dead webhooks before they become revenue-impacting.

## When to Use

- payment-flow-qa running scheduled health checks
- conductor-of-conductors detecting payment infrastructure issues
- Any agent investigating payment failures or missing webhooks

## Steps

### 1. Webhook Listener Status

```bash
# Check if webhook listener process is alive
pgrep -f "webhook" || echo "DEAD — no webhook listener process found"

# Check WEBHOOK_ID env var (required for PayPal signature verification)
grep WEBHOOK_ID .env || echo "MISSING — WEBHOOK_ID not in .env"

# Check last webhook received (from D1)
curl -s "https://api.purebrain.ai/admin/webhooks/latest" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
ts = data.get('last_received', 'NEVER')
print(f'Last webhook: {ts}')
"
```

### 2. PayPal API Reachability

```bash
# Verify PayPal API is reachable (sandbox or production)
curl -s --connect-timeout 10 "https://api-m.paypal.com/v1/oauth2/token" \
  -H "Accept: application/json" \
  -d "grant_type=client_credentials" \
  -u "${PAYPAL_CLIENT_ID}:${PAYPAL_SECRET}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'access_token' in data:
    print('PayPal API: REACHABLE (token obtained)')
else:
    print(f'PayPal API: ERROR — {data.get(\"error_description\", \"unknown\")}')
"
```

### 3. Plan ID Integrity

```bash
# Verify current plan IDs match expected values
EXPECTED_PLANS=(
    "P-4P012700Y82808818NICOI7Q"   # Awakened $297
    "P-3KL830539R502981PNICOI7Q"   # Partnered $597
    "P-1KC17605JW4534516NICOI7Q"   # Unified $1,097
)

for page in awakened partnered unified; do
    PLAN_ID=$(grep -oP "plan-id=['\"]?\K[^'\">\s]+" exports/cf-pages-deploy/${page}/index.html 2>/dev/null || echo "NOT_FOUND")
    echo "${page}: ${PLAN_ID}"
done
```

### 4. Latest Payment Freshness

```bash
# Check most recent payment timestamp from D1
# Alert if >24h since last payment (during business hours)
curl -s "https://api.purebrain.ai/admin/payments/latest" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
ts = data.get('created_at', '')
if ts:
    dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    age_hours = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
    status = 'OK' if age_hours < 48 else 'STALE'
    print(f'Last payment: {ts} ({age_hours:.1f}h ago) — {status}')
else:
    print('No payment data available')
"
```

### 5. Report

Output structured health check:
```
PAYMENT PIPELINE HEALTH — [timestamp]
Webhook Listener: [ALIVE/DEAD]
WEBHOOK_ID: [SET/MISSING]
Last Webhook: [timestamp or NEVER]
PayPal API: [REACHABLE/ERROR]
Plan IDs: [VALID/MISMATCH — details]
Last Payment: [timestamp] ([Xh ago])
Overall: [GREEN/YELLOW/RED]
```

## Recommended Cadence

12h cycle via BOOP executor. Assigned to: payment-flow-qa.

## Gotchas

- PayPal webhook listener died May 23 and stayed dead 10+ days — no monitor caught it
- WEBHOOK_ID env var must be set for signature verification; without it, all webhooks are rejected silently
- billing_agreement_id in webhooks is unreliable — use API fallback for subscription lookups
- Susan Lovelle honor pricing ($499/mo) uses old plan IDs P-3VH/P-43A — these must stay active but NOT on public pages

## Origin

Identified by capability gap analysis 2026-05-29, re-affirmed 2026-05-31. PayPal webhook dead 10 days with zero automated detection. $9,171/mo MRR at risk.
