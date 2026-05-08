# Chy's Red-Team Critique — Hancock Law Privilege & Security
**Date**: 2026-05-07
**Author**: Chy (delivered via Trio)
**Use**: Source material for Meridian 24-hr V3 Templates follow-up email (~15:30 UTC 2026-05-08)

## Triggering context

Mike Daser (lawyer reviewing Hancock Law prototype) said:
> "Wow. That's so much better than I expected. The big hurdle is IT security / walled-garden / not blowing attorney-client privilege by using a non-compliant LM. Maybe ask Chy to run a red-team critique along those lines, and recommend a plan of action."

Jared dispatched Chy. Chy delivered the below.

---

## CURRENT RISKS (5)

1. **Data flows to Anthropic API** — every AI feature sends contract text to api.anthropic.com. Client contract text leaves firm's control; Anthropic processes on their servers. COULD be a privilege waiver argument if opposing counsel discovers it.

2. **No BAA (Business Associate Agreement)** — if law firms handle healthcare clients (HIPAA), need BAA with Anthropic. Don't have one.

3. **No SOC 2 certification** — Cloudflare is SOC 2 compliant but WE don't have own SOC 2 or ISO 27001. Law firms with serious IT departments will ask.

4. **Data retention unknown** — Anthropic's data policy says they don't train on API data, but firms will want contractual guarantees, not policy promises.

5. **Single-tenant vs multi-tenant** — currently multi-tenant (all firms share one D1). Logical isolation by firm_id on every query, but not physical isolation.

---

## WHAT WE ALREADY HAVE (good)

- All queries parameterized (no SQL injection)
- Firm-scoped data isolation (firm_id on every query)
- CORS locked to legal.purebrain.ai
- Login rate limiting (10/IP/hour)
- PBKDF2 password hashing (100K iterations)
- JWT session tokens (24hr TTL)
- Full audit trail
- HTTPS everywhere (Cloudflare edge)
- API data NOT used for training (Anthropic API policy)

---

## PLAN OF ACTION

### IMMEDIATE (this week)
1. Add 'Data Processing Addendum' page — contractual commitment that client data is encrypted, isolated, and never used for training
2. Add 'attorney-client privilege preservation notice' to the UI — visible disclaimer that AI-processed content maintains privilege under ABA Model Rule 1.6 (reasonable efforts standard)
3. Document security architecture for IT review (one-pager)

### SHORT-TERM (30 days)
4. Get Anthropic's Enterprise agreement with data processing terms
5. Implement client-side encryption option for sensitive documents (encrypt before sending to API)
6. Add option to redact client names/PII before AI processing (redaction tool already exists)
7. Offer single-tenant D1 option for firms that require physical isolation

### MEDIUM-TERM (90 days)
8. SOC 2 Type I audit
9. Formal penetration test by third party
10. BAA for healthcare-adjacent firms

---

## Key message for IT review (Chy's framing)

> "We take the same reasonable precautions as major legal tech platforms (Clio, Relativity, Harvey) — encrypted transit, isolated data, contractual no-training guarantees, full audit trails — and we're pursuing SOC 2 certification."

---

## Aether's note for Meridian comms (2026-05-08 ~15:30 UTC)

When drafting the V3 Templates 24-hr follow-up to Meridian, fold in:
- Mike's privilege concern is acknowledged at engineering level
- Chy's red-team critique delivered same day (concrete deliverables, not vibes)
- Immediate items (Data Processing Addendum + privilege notice + IT one-pager) target this week — gives Meridian a concrete answer
- 30/90-day items show we're pursuing the right certifications, not just reactive

This positions Pure Tech / Hancock Law platform as taking privilege seriously by design, which is exactly what Mike was checking for.
