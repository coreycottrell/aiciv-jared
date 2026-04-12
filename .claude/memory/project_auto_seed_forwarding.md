---
name: Auto Seed Forwarding
description: Automatic seed data forwarding from birth pipeline to Witness CIV for container provisioning
type: project
---

Auto seed forwarding passes customer seed data from Aether's birth pipeline to Witness CIV for container provisioning.

**Why:** Witness needs seed data (customer name, plan tier, preferences) to provision the right container. Manual forwarding would create delays and errors.

**How to apply:** Seed forwarding is automated. Monitor for failures in the log server output. If seeds aren't reaching Witness, check the endpoint connectivity and Witness container pool status.
