# Brevo Domain Authentication Guide for puremarketing.ai

**Prepared by**: web-researcher agent
**Date**: 2026-02-21
**Goal**: Authenticate puremarketing.ai with Brevo to remove the Gmail security warning and "via sendinblue.com" sender display

---

## The Short Answer

Yes, properly configuring DKIM authentication **will remove both the "via sendinblue.com" display and the Gmail security warning**. Once DKIM is set up correctly, Gmail verifies the email genuinely comes from your domain and drops the warning entirely. This is confirmed by Postmark's canonical blog post on the topic: "Once you start signing with DKIM, that 'via sender' does not display anymore."

The whole process takes about 15-20 minutes of your time, then 24-72 hours of DNS propagation.

---

## What Records You Need

Brevo's authentication uses **3 DNS records**. The exact values for records 1 and 2 are **generated uniquely for your account** inside the Brevo dashboard. Record 3 (DMARC) has a standard format.

| # | Record | Type | Purpose |
|---|--------|------|---------|
| 1 | Brevo Code | TXT | Proves you own the domain |
| 2 | DKIM | TXT | Signs outgoing emails so Gmail trusts them |
| 3 | DMARC | TXT | Tells Gmail what to do if auth fails |

**Note on SPF**: Brevo does NOT require a manual SPF record. Their envelope sender is managed by Brevo's internal servers, so adding `include:spf.brevo.com` is optional but does not hurt. SPF alignment will not pass anyway (that is a Brevo limitation), so DKIM is the mechanism that does the actual work.

---

## Step-by-Step Guide

### Step 1: Log Into Brevo

Go to: https://app.brevo.com

Log in with your Brevo credentials.

---

### Step 2: Navigate to Domain Authentication

1. Click your **account name** in the top-right corner of the dashboard
2. Select **"Senders, Domains, and Dedicated IPs"** from the dropdown
3. Click the **"Domains"** tab at the top
4. You will see a list of any domains you have already added

The direct URL is: https://app.brevo.com/senders/domain/list

---

### Step 3: Add puremarketing.ai

1. Click **"Add a domain"** button
2. In the popup, type: `puremarketing.ai`
3. Click **"Save this email domain"**

Brevo will now generate your unique authentication records.

---

### Step 4: Get Your DNS Records

After saving, Brevo will display a page showing the DNS records you need to add. You will see:

**Record 1: Brevo Code (domain verification)**
- Type: `TXT`
- Name/Host: Something like `brevo-code` or a unique hash subdomain
- Value: A unique code that looks like `brevo-code:abc123xyz...`

**Record 2: DKIM**
- Type: `TXT`
- Name/Host: Something like `mail._domainkey` (Brevo will show the exact selector name - it may be UUID-based like `a1b2c3d4._domainkey`)
- Value: A long RSA public key starting with `v=DKIM1; k=rsa; p=...`

**Record 3: DMARC** (Brevo provides this too)
- Type: `TXT`
- Name/Host: `_dmarc`
- Value: `v=DMARC1; p=none; rua=mailto:dmarc@puremarketing.ai`

**Important**: Copy these exact values from your Brevo screen. Do not type them manually. The DKIM key is hundreds of characters long and a single typo breaks it.

Screenshot or copy-paste all three records before leaving this page.

---

### Step 5: Add the Records to puremarketing.ai DNS

You need to access wherever puremarketing.ai's DNS is managed. This is typically:
- Your domain registrar (GoDaddy, Namecheap, Google Domains, etc.)
- Or Cloudflare if you are using it for DNS (which you likely are given your setup)

**If using Cloudflare** (most likely for puremarketing.ai):

1. Log into Cloudflare: https://dash.cloudflare.com
2. Select the puremarketing.ai domain
3. Click **"DNS"** in the left sidebar
4. Click **"Add record"** for each of the 3 records

For each record:

**Record 1 (Brevo Code)**:
- Type: `TXT`
- Name: paste exactly what Brevo shows (e.g. `brevo-code`)
- Content/Value: paste the value from Brevo
- TTL: Auto (or 3600)
- Proxy status: **DNS only** (grey cloud, NOT orange proxy)

**Record 2 (DKIM)**:
- Type: `TXT`
- Name: paste exactly what Brevo shows (e.g. `mail._domainkey` or a UUID selector)
- Content/Value: paste the entire long DKIM value
- TTL: Auto (or 3600)
- Proxy status: **DNS only** (grey cloud)

**Record 3 (DMARC)**:
- Type: `TXT`
- Name: `_dmarc`
- Content/Value: `v=DMARC1; p=none; rua=mailto:dmarc@puremarketing.ai`
- TTL: Auto (or 3600)
- Proxy status: **DNS only** (grey cloud)

**Critical Cloudflare note**: DKIM records MUST be set to "DNS only" (grey cloud). If they are proxied (orange cloud), they will not work.

**If using a different DNS provider** (GoDaddy, Namecheap, etc.): The field names vary slightly. "Name" may be called "Host" and "Content" may be called "Value" or "TXT Value". The process is the same - add a TXT record with the values from Brevo.

---

### Step 6: Verify in Brevo

DNS changes take 15 minutes to 72 hours to propagate. After waiting at least 15-30 minutes:

1. Go back to Brevo's Domains page (https://app.brevo.com/senders/domain/list)
2. Find puremarketing.ai and click **"Authenticate"** or **"View Configuration"**
3. Click **"Authenticate this email domain"** at the bottom of the page
4. Brevo will check if your DNS records are live

**What you want to see**: Green checkmarks with "Value matched" next to each record.

**If you see "Value mismatched"**: The DNS has not propagated yet, or there is a typo. Wait another hour and try again. You can click "Check configuration" to retry without waiting.

You can check propagation status yourself at any time using:
- https://mxtoolbox.com/TXTLookup.aspx (enter `_dmarc.puremarketing.ai` to check DMARC)
- https://toolbox.googleapps.com/apps/dig/ (Google's DNS checker)

---

### Step 7: Confirm the Sender in Brevo

After domain authentication succeeds, verify that your sender address is linked to the authenticated domain:

1. In Brevo, go to **Settings > Senders, Domains, and Dedicated IPs > Senders**
2. Find the sender `purebrain@puremarketing.ai` (or "Aether (The Neural Feed)")
3. It should show the domain as authenticated

If the sender was created before you authenticated the domain, you may need to re-add it or just verify it shows a green status.

---

### Step 8: Send a Test Email and Verify

Send a test email from Brevo to your Gmail account.

In Gmail, open the email and check:
- The sender line should now show just "Aether (The Neural Feed) purebrain@puremarketing.ai" with NO "via sendinblue.com"
- No yellow security warning
- Click the three dots > "Show original" and look for `dkim=pass` and `dmarc=pass` in the headers

---

## Optional: Add SPF Record

Brevo does not require SPF, but if you want to add it for completeness:

- Type: `TXT`
- Name: `@` (the root domain)
- Value: `v=spf1 include:spf.brevo.com ~all`

**Important**: If puremarketing.ai already has an SPF record (TXT record at `@` starting with `v=spf1`), do NOT create a second one. Instead, edit the existing one to add `include:spf.brevo.com` inside it. Having two SPF records breaks email delivery.

To check if one exists: https://mxtoolbox.com/spf.aspx (enter `puremarketing.ai`)

---

## Troubleshooting

**Still seeing "via sendinblue.com" after 72 hours**:
- Check that your DKIM record is set to "DNS only" (not proxied) in Cloudflare
- Verify the DKIM record value was copied exactly with no extra spaces or line breaks
- In Brevo, click "View Configuration" and check for "Value mismatched" warnings

**DKIM record not found by Brevo**:
- The DKIM Name field in DNS may need adjustments. If Brevo shows `mail._domainkey` as the name, some DNS providers need you to enter just `mail._domainkey` (they append your domain), while others need the full `mail._domainkey.puremarketing.ai`. Check your DNS provider's documentation.

**Green checkmarks in Brevo but Gmail still shows warning**:
- This is likely a caching issue. Send a fresh email (not a reply) and wait up to 24 hours for Gmail to process the new authentication headers.

---

## DNS Propagation Timing

| Stage | Expected Time |
|-------|--------------|
| Cloudflare DNS live | 1-15 minutes |
| Most DNS resolvers worldwide | 1-4 hours |
| Full global propagation | Up to 72 hours |
| Gmail starts recognizing authentication | Within 24 hours of DNS propagation |

---

## Summary of Records to Add

Once you have your values from Brevo, you will add exactly these 3 TXT records to puremarketing.ai's DNS:

```
Type: TXT | Name: [from Brevo]      | Value: brevo-code:[unique hash]
Type: TXT | Name: [from Brevo]._domainkey | Value: v=DKIM1; k=rsa; p=[long key]
Type: TXT | Name: _dmarc             | Value: v=DMARC1; p=none; rua=mailto:dmarc@puremarketing.ai
```

All values for records 1 and 2 come directly from your Brevo dashboard. You cannot predict them in advance - they are unique to your account.

---

## Sources

- [Brevo Official: Authenticate your domain (Brevo code, DKIM, DMARC)](https://help.brevo.com/hc/en-us/articles/12163873383186-Authenticate-your-domain-with-Brevo-Brevo-code-DKIM-DMARC)
- [Brevo Official: FAQs about domain authentication](https://help.brevo.com/hc/en-us/articles/17286219877778-FAQs-About-domain-authentication-Brevo-code-DKIM-DMARC)
- [Brevo Official: Troubleshooting domain authentication](https://help.brevo.com/hc/en-us/articles/16045394674066-Troubleshooting-issues-with-domain-authentication-Brevo-code-DKIM-DMARC)
- [Postmark: DKIM and the "via" label in Gmail](https://postmarkapp.com/blog/dkim-and-the-via-label-in-gmail)
- [AutoSPF: Configuring SPF, DKIM, and DMARC for Brevo](https://autospf.com/blog/configuring-spf-dkim-and-dmarc-for-brevo/)
- [EasyDMARC: Brevo SPF & DKIM Setup Step by Step](https://easydmarc.com/blog/brevo-ex-sendinblue-spf-dkim-setup/)
- [dmarcian: Brevo Source Guide](https://dmarcian.com/brevo/)
- [MXToolbox: Brevo (Sendinblue) SPF & DKIM Setup](https://mxtoolbox.com/c/outboundemailsources?public=Brevo-(formerly-Sendinblue))
- [dmarc.wiki: How to set up SPF, DKIM and DMARC for Brevo](https://dmarc.wiki/brevo)
- [Brevo API Docs: Domain authentication and validation](https://developers.brevo.com/docs/domain-authentication-and-verification)
