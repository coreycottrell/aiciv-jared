# PayPal vs D1 Clients Audit - 2026-05-02

## Summary

**Webhook was dead**: Before Apr 23, the PayPal webhook URL was pointing to a dead endpoint. Webhooks started arriving Apr 23 but all 29 were stuck in "processing" status (handler not completing). Marked all as "audited-2026-04-30".

**Good news**: All paying customers from April/May ARE present in D1. No clients are missing. The frontend signup flow (not the webhook) is correctly inserting clients into D1 at subscription creation time.

---

## Issues Found & Fixed

### 1. Daniel Joshua Grand (danieljoshua@me.com) - CANCELLED
- **Subscription**: I-NB2WYP735X4N
- **Cancelled**: 2026-05-01 (yesterday)
- **Last payment**: $149 on 2026-04-25
- **D1 was**: payment_status = "active"
- **FIX APPLIED**: Updated to payment_status = "cancelled"

### 2. Joseph Diosana (Joseph@ThePropertyJoesGroup.com) - DOUBLE BILLED
- **Sub 1**: I-5JNMHY07WPCV (created Apr 3, ACTIVE, $149/mo)
- **Sub 2**: I-TA6PY6KGP6SB (created Apr 17, ACTIVE, $149/mo)
- **Both are ACTIVE** on the same plan for the same email
- **He is being charged $298/mo instead of $149/mo**
- **FIX APPLIED**: Added note to D1 record flagging dual subscription
- **ACTION NEEDED**: Cancel one subscription (likely I-5JNMHY07WPCV, the older one) or reach out to Joseph to confirm intent

### 3. Hannah Khokhar (hannahkhokhar@hotmail.co.uk) - PAYMENT FAILED
- **Subscription**: I-X5X26YGNYY6G (status: ACTIVE, PayPal retrying)
- **Last successful payment**: 2026-03-09 ($74.50 Insiders)
- **Failed payments**: 1
- **April payment never collected**
- **FIX APPLIED**: Added note to D1 record
- **ACTION NEEDED**: Monitor - if PayPal exhausts retries, will auto-suspend

---

## Webhook Status

- **29 webhook events** received Apr 23 - Apr 30, all stuck at "processing"
- Marked as "audited-2026-04-30" since underlying data is correct
- **Root cause**: Webhook handler is receiving events but not completing processing logic
- **Recommend**: Check the webhook worker code - it logs to D1 but doesn't update client records

---

## Full April/May Paying Subscribers (37 unique subscriptions with payments)

All confirmed present in D1:

| Email | Name | Tier | Sub ID | Amount |
|-------|------|------|--------|--------|
| fred@thedoghouseps.com | Fredrick Williams | Bonded | I-TW88EKMY9UTX | $149 |
| farisasmar@hotmail.com | FARIS ASMAR | Insiders | I-8C6DLSP8N9FB | $74.50 |
| joseph@thepropertyjoesgroup.com | Joseph Diosana | Awakened | I-5JNMHY07WPCV | $149 |
| bwnordal@gmail.com | Bradley Nordal | Insiders | I-VK69SJ07X9DU | $74.50 |
| nidhin.nandakumar1@gmail.com | Nidhin Nandakumar | Insiders | I-DDRTL2AW9MG0 | $74.50 |
| tess@makrvf.com | Tess Verneuil | Bonded | I-N2DV819PXT4Y | $149 |
| itr766@yahoo.com | Travis Thompson | Awakened | I-423U34V2YF7E | $149 |
| pay@processpal.us | Matthew Keough | Insiders | I-MHM4NGXG1WLN | $74.50 |
| donatobsms@outlook.com | John Perkins | Bonded | I-07P7MX2HVAXR | $149 |
| t_schoessow@yahoo.com | trevor schoessow | Awakened | I-910M3CNJ2LA5 | $149 |
| lhneuteufel@gmail.com | Lucas Neuteufel | Awakened | I-R9WR4YUNRUY4 | $149 |
| lrosanio@think-traffic.com | Linda Rosanio | Awakened | I-DH8H7KFBSEPT | $149 |
| bethanie@hunden.com | Bethanie DeRose | Awakened | I-VKWHK69HF4UY | $149 |
| billing@lauthinvestigations.com | Lauth Investigations | Awakened | I-FTCE38N671WA | $149 |
| gadamo1314@gmail.com | Gregory Adamo | Awakened | I-11RA7X486Y80 | $149 |
| carogerding@yahoo.com | Carolina Gerding | Insiders | I-B8K8DJCDGLPK | $74.50 |
| bryce.lohr@gmail.com | Bryce Lohr | Awakened | I-0V9BWYFK2NTC | $149 |
| joseph@thepropertyjoesgroup.com | Joseph Diosana | Awakened | I-TA6PY6KGP6SB | $149 (DUPLICATE) |
| foreignaidauto@gmail.com | KIRK MARCOU | Awakened | I-X5FJ82H2TBW6 | $149 |
| jhutton@vsblty.net | James Hutton | Insiders | I-SKVNSUGX1K2H | $74.50 |
| harrison@bisnce.com | Harrison Amit | Awakened | I-H6AC73U9HARH | $149 |
| vishal@vidonaresidential.com | Vishal Doddanna | Awakened | I-4G5C7R3ESJF0 | $149 |
| garydouglaskohn@gmail.com | Gary Kohn | Awakened | I-31X7CKHXCTJA | $149 |
| katy@kattychick.com | Katy Huang | Awakened | I-U0P1VUTPAGSC | $149 |
| smcauley@texmg.com | Scott McAuley | Awakened | I-546U9NKK19XV | $149 |
| mthancock@gmail.com | Michael Hancock | Insiders | I-K7P63D6TDHAB | $74.50 |
| pyeleer@reagan.com | Eric Turbaville | Awakened | I-Y1U2G9JBLAEB | $149 |
| danieljoshua@me.com | Daniel Joshua Grand | Awakened | I-NB2WYP735X4N | $149 (CANCELLED May 1) |
| donna@thedoghouseps.com | Donna Olson | Awakened | I-NUGXM538UX2H | $149 |
| jeromevpub@gmail.com | JEROME VASAMILLET | Awakened | I-2AST5U4G6JDN | $149 |
| michaeltfoley@hotmail.com | Michael Foley | Awakened | I-5S3FTJV68DHB | $149 |
| piasknudsen@gmail.com | pia knudsen | Awakened | I-AW4DMVSC63P0 | $149 |
| mrewers22@gmail.com | Mark Rewers | Awakened | I-5PA89EK2WE81 | $149 |
| darrenrowan@gmail.com | Darren Rowan | Awakened | I-T6ERGTV7HWWL | $149 |
| lapc@att.net | Laurie Clifton | Awakened | I-FXYUSSW4GPA2 | $149 |
| jay@couplify.com | Jay Whitehurst | Partnered | I-P4WNDS799EYY | $499 |

---

## D1 Changes Made

```sql
UPDATE clients SET payment_status = 'cancelled' WHERE email = 'danieljoshua@me.com';
UPDATE clients SET notes = 'DUAL SUBSCRIPTION...' WHERE email = 'Joseph@ThePropertyJoesGroup.com';
UPDATE clients SET notes = 'April payment FAILED...' WHERE email = 'hannahkhokhar@hotmail.co.uk';
UPDATE paypal_webhook_log SET status = 'audited-2026-04-30' WHERE status = 'processing';
```

---

## Action Items for Jared

1. **Joseph Diosana double-billing** - Cancel subscription I-5JNMHY07WPCV (older) or contact Joseph. He's paying $298/mo for a $149 plan.
2. **Hannah Khokhar failed payment** - Her April Insiders payment failed. PayPal is retrying. May need manual outreach if it doesn't resolve.
3. **Webhook handler** - Events are being logged but not processed. The worker needs debugging to actually update client records on payment/cancellation events.
