# Memory: "2 Product Managers" Orchestration Model

**Date**: 2026-02-25
**Type**: coordination-pattern
**Topic**: Jared's directive for separate product tracks with dedicated agent ownership

---

## The Pattern

When working on multiple products simultaneously (e.g., Pay-Test Pipeline vs PureBrain Hub), assign a SEPARATE agent-as-product-manager to each track. No interference between tracks.

### How It Works
- **Track 1 (Priority)**: Gets conductor's direct attention. Agent assigned as product manager runs all coordination.
- **Track 2 (Background)**: Runs autonomously via a different agent. Only surfaces to conductor on completion or blocker.

### Example (Session 42)
- Track 1: Pay-test / Witness E2E → Conductor focus, full-stack-developer + browser-vision-tester + collective-liaison
- Track 2: PureBrain Hub V2 → full-stack-developer autonomous rebuild, surfaced when done

### Why This Matters
- Prevents context bleed between unrelated products
- Each "product manager" agent maintains full context for their track
- Jared explicitly wants separate concerns: "2 product managers" model
- Mirrors real company structure where product managers don't cross-manage

### When to Apply
- Any time Jared gives 2+ parallel product workstreams
- Any time there's a deployment-sensitive track (like E2E pipeline) alongside a creative track (like UI rebuild)
- Track priority assigned by Jared, not by conductor

---

**Tags**: orchestration, two-track, product-manager, delegation, parallel-work, jared-directive
