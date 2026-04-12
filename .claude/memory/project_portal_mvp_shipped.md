---
name: Portal MVP Shipped
description: PureBrain Portal MVP approved and shipped on 2026-03-17, multi-user data isolation confirmed
type: project
---

Portal MVP approved by Jared on 2026-03-17 and marked SHIP READY.

**Key facts:**
- Multi-user data isolation: agents/tasks/departments show blank for new users (not Aether's data)
- 44/47 QA tests passed (March 16 comprehensive audit)
- Final QA: 17 pass / 0 fail (March 17 pre-ship)
- Code pushed to coreycottrell/purebrain-portal on GitHub
- Portal server runs on same host as Aether (systemd managed)
- Corey (True Bearing) has access to the code

**Why:** This is PureBrain's customer-facing product. All paying customers interact through the portal.

**How to apply:** Portal is in production. Changes need QA before deploy. Coordinate with Witness CIV for their deployment. Don't break existing customer sessions.
