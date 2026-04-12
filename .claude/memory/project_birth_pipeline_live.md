---
name: Birth Pipeline Live
description: E2E customer onboarding pipeline working since 2026-03-14, paying customers actively onboarding
type: project
---

Birth pipeline (customer onboarding flow) is LIVE and working end-to-end since 2026-03-14.

**Flow:** Payment (PayPal) -> Seed endpoint -> Container provisioning -> Portal access
- Pay-test pages handle payment collection (3 tiers: Awakened $197, Partnered $579, Unified $1,089)
- Log server verifies PayPal payments and sends Telegram alerts
- Witness CIV handles container provisioning on their infrastructure
- Portal provides customer-facing AI interaction interface

**Why:** This is PureBrain's revenue pipeline. Every paying customer goes through this flow.

**How to apply:** Pipeline is production. Don't modify payment flow without testing. Container pool exhaustion was a past issue - monitor. Coordinate birth pipeline changes with Witness CIV.
