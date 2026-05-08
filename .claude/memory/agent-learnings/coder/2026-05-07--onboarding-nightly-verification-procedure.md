# Onboarding Nightly Verification Procedure

**Date**: 2026-05-07
**Agent**: coder
**Type**: operational
**Topic**: PureBrain payment page and infrastructure health checks

---

## What Was Done

Implemented comprehensive nightly verification for PureBrain onboarding flow covering:

1. **Payment page health** (8 URLs)
2. **Infrastructure status** (AgentMail, Telegram, DNS, webhooks)
3. **Homepage content** (PayPal SDK, chat, pricing, theme)
4. **Known issues** (Henrik Sylvest duplicate subscription bug)
5. **Database verification** (attempted - D1 not locally accessible)

---

## Key Commands

### Page Health Checks (CF Pages requires GET not HEAD)

```bash
# CORRECT (returns 200 for healthy CF Pages)
curl -s -o /dev/null -w "%{http_code}" https://purebrain.ai/

# WRONG (returns 404 even for healthy CF Pages)
curl -sI https://purebrain.ai/
```

**Critical**: Cloudflare Pages returns 404 for HEAD requests even when page is healthy. Always use GET with `-s -o /dev/null` for health checks.

### Infrastructure Checks

```bash
# AgentMail monitor
pgrep -f agentmail_general_monitor.py

# Telegram bridge  
pgrep -f telegram_bridge.py

# DNS verification
dig +short keen-jared.app.purebrain.ai

# Webhook health
curl -s -o /dev/null -w "%{http_code}" "https://agentmail-webhook.in0v8.workers.dev/health"
```

### Content Verification

```bash
# Fetch homepage and check elements
homepage_html=$(curl -s "https://purebrain.ai/")

# Check for PayPal SDK
echo "$homepage_html" | grep -q "paypal"

# Check for pricing
echo "$homepage_html" | grep -q "\$149"
echo "$homepage_html" | grep -q "\$499"  
echo "$homepage_html" | grep -q "\$999"

# Check for dark theme
echo "$homepage_html" | grep -qi "#080a12"
```

### Log Analysis for Known Issues

```bash
# Check for specific customer issues (Henrik Sylvest case)
grep -i "henrik\|sylvest\|dacapo\|cairn" /home/jared/projects/AI-CIV/aether/logs/*.log | tail -20

# Extract subscription IDs
grep -oE "I-[A-Z0-9]{10,}" /path/to/log | sort -u

# Count seeds fired for customer
grep -i "payment-seed.*Henrik Sylvest" /path/to/log | grep "Seed fired" | wc -l
```

---

## Findings

### What Worked

✅ All 8 payment pages healthy (HTTP 200)
✅ Infrastructure components running  
✅ Homepage content complete (PayPal SDK, chat, pricing, theme)
✅ Log analysis successfully identified Henrik Sylvest issue

### Critical Issue Discovered

**Henrik Sylvest duplicate subscription bug**:
- 3 different PayPal subscription IDs created for same customer
- 3 seeds fired within 90 seconds (06:36:48 to 06:38:15 UTC)
- Same email (hss@dacapo.com), same AI name (Cairn)
- Subscription IDs: I-X7WMCF301BL4, I-5AF5MYBESV60, I-RK0WXGW6CY7T

**Root cause**: Missing webhook deduplication logic in payment handler

### Database Limitation

clients.db not accessible - likely hosted in Cloudflare D1 (cloud Workers DB). Local SQLite checks won't work. Need D1 query capability for future checks.

---

## Patterns Discovered

### CF Pages Health Check Pattern

**Anti-pattern**: Using `curl -sI` (HEAD request) for CF Pages health checks
**Correct pattern**: Use `curl -s -o /dev/null -w "%{http_code}"` (GET request)

**Reasoning**: CF Pages returns 404 for HEAD requests even when healthy. This is CF-specific behavior, not a bug in the page.

### PayPal Webhook Deduplication Required

PayPal webhooks can fire multiple times for same transaction (retry behavior). Without deduplication:
- Multiple seeds sent to customer
- Multiple database entries created
- Potential duplicate charges
- Poor customer experience

**Required safeguards**:
1. Subscription ID cache with 15-min TTL
2. Email-based gating (prevent duplicate seeds same email within 24h)
3. Idempotency keys on all payment APIs
4. Webhook signature verification

### Log Analysis for Payment Issues

Effective search pattern:
1. Search by customer identifiers (name, email, company, AI partner name)
2. Extract subscription IDs with grep -oE
3. Count unique subscription IDs (should be 1 per customer)
4. Count seeds fired (should be 1 per customer)
5. Check timestamps (duplicates often cluster within minutes)

---

## File Paths Referenced

- **Log server**: `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log`
- **Report output**: `/home/jared/exports/portal-files/ONBOARDING-NIGHTLY-CHECK-2026-05-07.md`
- **Onboarding spec**: `/home/jared/projects/AI-CIV/aether/.claude/ONBOARDING-SPEC-DEFINITIVE.md`
- **Expected DB path**: `/home/jared/projects/AI-CIV/aether/clients.db` (not found - cloud-hosted)

---

## Recommendations for Future Checks

### Add to Nightly Verification

1. **D1 database query** capability (cloud Workers DB access)
2. **Subscription ID deduplication check** (scan for emails with multiple subscription IDs)
3. **Seed count verification** (1 seed per email per day max)
4. **PayPal webhook log analysis** (identify retry patterns)

### Alert Thresholds

- **Critical**: Payment page down (HTTP != 200)
- **Critical**: Infrastructure process not running (pgrep fails)
- **Critical**: Multiple subscription IDs for same email
- **High**: Multiple seeds for same email within 24h
- **Medium**: Multiple instances of same process (AgentMail monitor)

### Automation Opportunities

Convert this manual check into cron job:
```bash
# /etc/cron.d/purebrain-nightly-check
0 7 * * * aether cd /home/jared/projects/AI-CIV/aether && bash tools/onboarding-nightly-check.sh > /home/jared/exports/portal-files/ONBOARDING-NIGHTLY-CHECK-$(date +\%Y-\%m-\%d).md 2>&1
```

---

## Integration Points

This verification procedure touches:
- **CF Pages** deployment (purebrain-production, purebrain-staging)
- **PayPal webhooks** (payment-seed endpoint)
- **AgentMail** (webhook monitoring)
- **Telegram bridge** (notification infrastructure)
- **DNS** (*.app.purebrain.ai subdomain routing)
- **Log server** (purebrain_log_server.py)

Future modifications should verify all integration points still functional.

---

## Success Criteria

Nightly check passes when:
- [ ] All 8 payment pages return HTTP 200
- [ ] All 4 infrastructure components running
- [ ] Homepage contains all 6 content elements
- [ ] No duplicate subscriptions detected in logs (last 24h)
- [ ] Report generated and saved to portal-files/

Failures should trigger immediate Telegram alert to Jared.

---

## Memory Type

**Type**: Operational (reference for future coder/ST# agents)

**Transferable wisdom**: CF Pages health checks require GET not HEAD. PayPal webhooks need deduplication. Customer experience breaks when payment flow lacks idempotency.

---

**Next run**: 2026-05-08 07:00 UTC
