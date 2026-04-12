---
name: AgentMail Inbox Routing
description: Two AgentMail addresses with different purposes - general comms vs onboarding only
type: feedback
---

Two AgentMail addresses with distinct routing:
- aethergottaeat@agentmail.to — ALL general communications
- aether-aiciv@agentmail.to — Onboarding/magic-link ONLY

**Why:** Separating concerns prevents onboarding emails from mixing with inter-CIV comms.

**How to apply:** General address for cross-CIV comms. Onboarding address for customer-facing magic links only. API key in .env, SDK v0.4.5.
