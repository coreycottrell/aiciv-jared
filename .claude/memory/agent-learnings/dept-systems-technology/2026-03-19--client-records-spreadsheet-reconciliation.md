# Client Records Spreadsheet Reconciliation

**Date**: 2026-03-19
**Type**: operational
**Agent**: dept-systems-technology

---

## Task

Reconcile clients.db against Jared's Google Spreadsheet as source of truth.
Spreadsheet ID: 1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ

---

## Spreadsheet Access Pattern

Use gspread with service account at:
/home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json
Scopes: https://www.googleapis.com/auth/spreadsheets.readonly

Sheet1 = full payment history by customer (cols: #, date, name, email, PayPal transaction ID, amount, subscription status)
Sheet2 = PMG accounting records by reference number

---

## Fixes Applied (2026-03-19)

1. Tess Verneuil: tier Insiders->Awakened, $74.50->$149, sub ID set to I-N2DV819PXT4Y
2. Jay Hutton: tier Awakened->Insiders (PayPal sub on $74.50 Insiders plan P-8AU4270420374002JNGY3VYQ)
3. Michael Hancock: payment_status none->paid, total_paid $0->$149 (spreadsheet shows $149 one-off 2/26)
4. Harrison Amit (Harrison@bisnce.com): NEW CLIENT added - Awakened/$149, sub I-H6AC73U9HARH (signed up today)
5. Andrew Ryan (ryandoha@gmail.com): NEW CLIENT added - Awakened/paid one-off $79 (spreadsheet row 2, 2/26)

---

## Flagged for Jared (NOT auto-changed)

- Lucas Neuteufel: DB email lucas@hunden.com vs PayPal/spreadsheet lhneuteufel@gmail.com
- Fredrick Williams: DB email fred@mypetcredentials.com vs PayPal/spreadsheet fred@thedoghouseps.com
- Hannah Khokhar: sub ID still unknown (capture API doesn't embed sub IDs)

---

## Plan ID Reference (CONFIRMED)

- P-2SA65600MT088594TNGLTFKY = $149/mo Awakened
- P-8AU4270420374002JNGY3VYQ = $74.50/mo Insiders

---

## Key Insight: PayPal Captures Don't Embed Subscription IDs

v2/payments/captures/{id} supplementary_data.related_ids is empty for subscription captures.
To get subscription transactions: GET /v1/billing/subscriptions/{sub_id}/transactions

## Database Location
/home/jared/purebrain_portal/clients.db
