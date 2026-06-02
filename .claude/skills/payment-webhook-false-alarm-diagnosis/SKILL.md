---
name: payment-webhook-false-alarm-diagnosis
description: Diagnose false alarm "missing seed" reports caused by PayPal double-fired webhooks creating misleading blocked_seeds entries
type: process
domain: payment-infrastructure, seed-flow, incident-triage
created: 2026-05-26
trigger: "when a seed appears missing for a paying customer, when blocked_seeds has an entry for a customer, when investigating payment completion issues"
status: provisional
tick_count: 0
last_used: 2026-05-26
introduced: 2026-05-26
---

# Payment Webhook False Alarm Diagnosis

**Purpose**: Prevent misdiagnosis of "missing seed" incidents when PayPal double-fires webhooks. The second webhook attempt arrives with a truncated UUID, gets correctly blocked by the deduplication guard, and creates a `blocked_seeds` log entry that looks like the seed was never sent -- when in fact the first webhook succeeded and the seed WAS delivered.

**Origin**: 2026-05-26 -- Corneille Zamilus payment investigation. Initial triage concluded seed was missing based on `blocked_seeds` entry. Deeper investigation of portal server logs revealed the first webhook fired successfully and the seed was sent. The `blocked_seeds` entry was from the second (duplicate) webhook, not a failure of the first.

## Steps

### Step 1: Gather the Customer Identifier

Get the customer name, email, or payment reference from the report.

### Step 2: Check blocked_seeds FIRST (But Do Not Trust It Alone)

```bash
# Search for blocked entries
grep -i "<customer_name_or_email>" /path/to/blocked_seeds.log
# Or in D1 if applicable:
# SELECT * FROM blocked_seeds WHERE payer_name LIKE '%<name>%' OR payer_email LIKE '%<email>%';
```

If you find a blocked entry, do NOT conclude the seed was not sent. This may be the duplicate webhook, not the original.

### Step 3: Check Portal Server Logs for the ORIGINAL Webhook

```bash
# Search portal server logs for the payment event
grep -i "<customer_name_or_email>" /home/jared/purebrain_portal/logs/portal_server.log
# Look for seed-send confirmation
grep -i "seed.*sent\|send.*seed\|seed.*deliver" /home/jared/purebrain_portal/logs/portal_server.log | grep -i "<customer_name_or_email>"
# Check PayPal webhook arrivals (look for TWO entries close together)
grep -i "paypal.*webhook\|payment.*complete\|IPN" /home/jared/purebrain_portal/logs/portal_server.log | grep -i "<customer_name_or_email>"
```

**Key signal**: If you see TWO webhook entries for the same customer within seconds/minutes, the first succeeded and the second was (correctly) blocked.

### Step 4: Check Seed Delivery Confirmation

```bash
# Verify the seed email was actually sent
grep -i "seed.*<customer_email>" /home/jared/purebrain_portal/logs/portal_server.log
# Check the send-seed API endpoint logs
grep -i "send-seed\|/api/send-seed" /home/jared/purebrain_portal/logs/portal_server.log | grep -i "<identifier>"
```

### Step 5: Verify UUID Integrity

```bash
# Compare UUIDs between the successful and blocked entries
# Double-fired webhooks often have truncated or malformed UUIDs on the second attempt
# The original UUID (full-length, valid) = successful delivery
# The truncated UUID = blocked duplicate
```

### Step 6: Confirm or Escalate

- **If Step 3 shows two webhooks AND Step 4 shows seed sent**: FALSE ALARM. The seed was delivered. Close the investigation.
- **If Step 3 shows only ONE webhook AND it was blocked**: REAL ISSUE. The seed genuinely was not sent. Escalate to ST# for manual seed delivery.
- **If logs are ambiguous**: Check the customer's email inbox status if possible, or contact the customer to confirm receipt.

## Gotchas

1. **blocked_seeds is a symptom, not a diagnosis**: A `blocked_seeds` entry means the deduplication guard worked. It does NOT mean the original seed failed. Always check for the original successful delivery before concluding anything.

2. **PayPal webhooks can double-fire**: PayPal retries webhooks if it does not receive a timely 200 response, or network issues cause duplicate delivery. This is normal PayPal behavior, not a bug in our system.

3. **Truncated UUIDs on retry**: The second webhook attempt may arrive with a slightly different or truncated UUID. The deduplication logic catches this, but the log entry can look like a fresh (failed) attempt rather than a retry.

4. **Time gap between fires varies**: The second webhook can arrive seconds, minutes, or even hours after the first. Do not assume double-fires must be within milliseconds.

5. **Do NOT re-send the seed without full investigation**: If you conclude the seed is missing and re-send, the customer may receive a duplicate seed, causing confusion. Always complete all 6 steps before taking corrective action.

## Examples

### Real Incident: Corneille Zamilus (2026-05-26)

**Report**: "Corneille Zamilus paid but seed appears missing."

**Initial Finding**: `blocked_seeds` contained an entry for Corneille with a truncated UUID. Appeared to confirm seed was never sent.

**Deeper Investigation**: Portal server logs showed:
1. First PayPal webhook arrived at T+0 -- processed successfully, seed sent
2. Second PayPal webhook arrived at T+12s -- UUID truncated, correctly blocked by deduplication guard
3. `blocked_seeds` entry was from attempt #2, not attempt #1

**Resolution**: Seed WAS sent. No action needed. `blocked_seeds` entry was a correct deduplication, not a failure indicator.

**Lesson**: Always check portal server logs for the complete webhook history before trusting `blocked_seeds` as evidence of failure. The deduplication guard working correctly can look identical to a delivery failure if you only check the blocked log.
