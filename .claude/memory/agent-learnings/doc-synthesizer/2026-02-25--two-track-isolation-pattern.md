# Two-Track Isolation Pattern

**Date**: 2026-02-25
**Source**: Jared's directive ~12:37 UTC, Session 42

## Pattern

When Jared assigns two concurrent product streams, they MUST be isolated:

### Track 1 (Priority): Pay-test / Pay-test-sandbox
- Pages 688 (sandbox) + 689 (production)
- E2E flow testing, PayPal sandbox checkout, Witness coordination
- Gets conductor attention first

### Track 2 (Background): PureBrain Hub Master Build
- ST# agent (dept-systems-technology) runs independently
- Combining: Dashboard v4 + Hub MVP + Portal Preview
- Rebrand: Agents → "Brains"
- DO NOT let Track 2 interfere with Track 1

## Key Learnings

1. **"2 product managers" model** — assign separate agents as PM for separate products
2. **Track isolation prevents context bleed** — don't let background build distract from priority testing
3. **Jared escalates priority explicitly** — when he says "PRIORITY", that track gets all conductor focus
4. **Background agents can run autonomously** — ST# doesn't need conductor babysitting

## Netlify Deploy History Recovery (Related)

- When a dashboard gets overwritten, Netlify keeps ALL deploy history
- Recovery: visit Netlify dashboard → Deploys → find previous deploy → use its preview URL
- This is faster than git archaeology for frontend assets
- Used to recover original v2 dashboard after v4 merge overwrote it

## Reusable Pattern

```
TRACK 1 (PRIORITY): [product] — conductor focus, direct testing
TRACK 2 (BACKGROUND): [product] — delegated agent, autonomous build
Rule: Track 2 NEVER blocks or distracts from Track 1
```
