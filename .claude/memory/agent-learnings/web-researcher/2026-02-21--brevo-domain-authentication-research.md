# web-researcher Learning: Brevo Domain Authentication Research

**Date**: 2026-02-21
**Type**: teaching
**Agent**: web-researcher
**Topic**: How to fix Gmail "via sendinblue.com" warning with Brevo DKIM/DMARC authentication

---

## Task Summary

Researched the complete process for authenticating a sending domain (puremarketing.ai) with Brevo to fix:
- Gmail "via sendinblue.com" sender display
- Yellow security warning about unverified sender

---

## Key Findings

### 1. DKIM is the critical fix (not SPF)

Brevo's architecture means SPF alignment CANNOT pass. The "Envelope From" domain is always Brevo's internal servers (af.d.mailin.fr, etc.), not your domain. So even a perfect SPF record won't fix the "via sendinblue.com" display.

DKIM is the mechanism that solves this. When DKIM is configured correctly, Gmail sees the email is signed by your domain and removes the "via" label and security warning entirely. Confirmed by Postmark's canonical article.

### 2. Three DNS records needed (all TXT)

- Brevo Code: domain ownership verification (unique per account, get from dashboard)
- DKIM: email signing key (unique per account, get from dashboard)
- DMARC: policy record (standard format: `v=DMARC1; p=none; rua=mailto:[your email]`)

### 3. Brevo Dashboard navigation path

Account name (top right) > Senders, Domains, and Dedicated IPs > Domains > Add a domain

Direct URL: https://app.brevo.com/senders/domain/list

### 4. SPF is optional

`v=spf1 include:spf.brevo.com ~all` can be added but will not fix the "via" label. Old documentation references `include:spf.sendinblue.com` which fails - use `spf.brevo.com` if adding it.

### 5. Cloudflare gotcha

DKIM records in Cloudflare MUST be set to "DNS only" (grey cloud), NOT proxied (orange). Proxied DKIM records break authentication.

### 6. Verification

Brevo's dashboard shows green checkmarks when authenticated. Also check with MXToolbox TXT lookup on `_dmarc.[domain]`.

### 7. Propagation timing

15 min to 72 hours for full DNS propagation. Gmail recognizes within 24 hours of propagation.

---

## Patterns Worth Noting

- Brevo = Sendinblue rebranded. Some older docs say "sendinblue.com" in SPF - use "brevo.com" equivalents instead.
- The DKIM and Brevo Code record NAME/HOST values are dynamically generated per account. Cannot be predicted. Must come from dashboard.
- Brevo recommends DMARC `p=none` for new setups. Do not jump to `p=reject` without monitoring first.
- Gmail's "via" label is purely a DKIM issue. No DKIM = shows "via provider.com". Proper DKIM = label disappears.

---

## File Location

Full guide: `/home/jared/projects/AI-CIV/aether/to-jared/brevo-domain-authentication-guide.md`

---

## Sources Used

- https://postmarkapp.com/blog/dkim-and-the-via-label-in-gmail (definitive "via" label explanation)
- https://help.brevo.com/hc/en-us/articles/12163873383186 (official Brevo docs)
- https://autospf.com/blog/configuring-spf-dkim-and-dmarc-for-brevo/ (SPF clarification)
- https://mxtoolbox.com/c/outboundemailsources?public=Brevo-(formerly-Sendinblue) (SPF record value)
- https://dmarc.wiki/brevo (DMARC setup walkthrough)
- https://dmarcian.com/brevo/ (SPF alignment limitation confirmed)

---

**END MEMORY**
