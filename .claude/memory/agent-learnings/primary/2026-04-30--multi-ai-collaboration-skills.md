# Skills Learned — April 30, 2026

## Session: Multi-AI Collaboration Sprint

### NEW SKILLS DISCOVERED

1. **Competitive Build Pattern**
   Two AIs build the same deliverable independently, human picks the best or merges. Produces better output than either AI alone.
   - Proven with: Investor Data Room (Aether design + Chy content)
   - Proven with: Multi-AI Playbook (Aether layout + Chy content + Morphe perspective)

2. **Pre-Flight Check Protocol**
   Before any shared infrastructure action, announce in shared channel with 5 questions and wait 60 seconds.
   - Prevents: simultaneous deploys, duplicate work, merge conflicts

3. **Proof of Work Standard**
   Every "done" claim includes verifiable evidence (HTTP status code, URL, screenshot).
   - Prevents: "deploy succeeded but feature doesn't work" pattern

4. **Uncertainty Flag**
   Mark low-confidence claims explicitly so other AIs can weigh in.
   - Format: [UNCERTAINTY: confidence=LOW] [topic] — [what's unsure]

5. **Contradiction Detector**
   AIs actively cross-check each other's facts and flag discrepancies.
   - Prevents: inconsistent numbers reaching investors/clients

6. **CLAIM Pattern for Shared Actions**
   First AI to claim a task in shared channel owns it. Others stand down.
   - Prevents: duplicate emails, duplicate deploys

7. **Warm vs Cold Handoffs**
   Warm: context + what's done + what's left + gotchas
   Cold: "do this thing" (costs 10-15 min re-discovery)

8. **Context Snapshot Template**
   WHAT / WHERE / STATE / GOTCHAS / VERIFY — structured handoff format

### INFRASTRUCTURE SKILLS

9. **AgentMail Send Endpoint**
   Correct: POST /v0/inboxes/{inbox}/messages/send (NOT /messages)

10. **Trio Backend Unification**
    trio-comms.in0v8.workers.dev is THE backend. 777-api is deprecated for trio.

11. **CF Worker Custom Domain Setup**
    Pattern: AAAA record (100::) + worker route = custom domain for any CF Worker

12. **Base64 Image Embedding**
    Google Drive image URLs require auth. Base64 data URIs render everywhere.

13. **PayPal Webhook Idempotency**
    SUBSCRIPTION.ACTIVATED should NOT set total_paid. Only PAYMENT.SALE.COMPLETED increments.

### COLLABORATION SKILLS

14. **Three-AI Trio Communication**
    All AIs must verify bidirectional comms BEFORE starting collaborative work.

15. **Playbook-as-Product**
    Writing your own collaboration playbook = IP that becomes a client deliverable.

16. **Sidebar Layout Pattern**
    For long documents: left sidebar nav + top search + scrollable content area.
    Proven superior to single-scroll for 10+ section documents.
