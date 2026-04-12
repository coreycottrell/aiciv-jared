# Memory: Client Tech Support Team Creation + Joe (Tether) Incident

**Date**: 2026-03-16
**Type**: founding-context + active-incident
**Team**: client-tech-support-team

---

## Team Creation Context

The Client Tech Support Team was created on 2026-03-16 by Jared via ST# directive. It is the 3rd tech team under the CTO:
1. Portal Tech Team
2. Website Tech Team
3. Client Tech Support Team (new)

The triggering incident was Joe (a PureBrain customer running Tether) reporting `Permission denied (publickey)` when trying to SSH into his server at `37.27.237.109` port `2219`.

Going forward, every new PureBrain portal deployment must receive a support keypair provisioned before going live. This is mandatory per Jared's directive.

---

## Active Incident: Joe (Tether) — SSH Permission Denied

**Customer**: Joe
**Product**: Tether (PureBrain portal deployment)
**Host**: 37.27.237.109
**Port**: 2219
**Issue**: `Permission denied (publickey)`
**Status**: Open as of 2026-03-16

**Root cause diagnosis**: Support keypair has not yet been provisioned for this customer. The customer may also be experiencing issues with their own key. Both need to be addressed.

**Resolution steps needed**:
1. Provision purebrain-support-tether-joe keypair
2. Deliver public key to Joe with installation instructions
3. Verify connection once Joe confirms key is installed
4. Update SSH key registry status to `active`
5. Separately: ask Joe if his own SSH key issues are resolved or if he needs help with that too

**Lesson learned**: No PureBrain portal deployment should go live without a support keypair already provisioned. The customer should have the support public key installed at deployment time, not after an incident occurs.

---

## Process Established

- SSH key registry created: `exports/departments/client-tech-support/ssh-key-registry.md`
- Keypair naming convention: `purebrain_support_[customer-slug]`
- Key type: ed25519
- Rotation cycle: 90 days standard
