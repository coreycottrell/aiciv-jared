# Memory: Calculator V4 Orchestration Pattern

**Date**: 2026-02-23
**Type**: operational
**Agent**: the-conductor

## What Happened

Jared sent a 2-part instruction for a major calculator enhancement. Key orchestration decisions:

### Multi-Part Instructions
- Part 1 arrived with "DO NOT START TILL I SEND PART 2"
- Correctly waited, acknowledged Part 1, confirmed understanding
- Part 2 arrived with "lets go" — launched immediately
- Both parts combined into single comprehensive agent prompt

### Research Before Delegation
Before launching the full-stack-developer, I read:
- Calculator HTML structure (lines 1-100, 1400-1600, 2090-2500)
- Tier data and pricing (TIERS array)
- Chat API pattern (Cloudflare Worker endpoint)
- Existing chatbox code patterns

This gave me enough context to write a detailed, unambiguous prompt. The agent completed in one shot without needing clarification.

### Pricing Discrepancy Handling
Jared said "$499" for Partnered but code had "$599". Went with Jared's explicit numbers ($499 → $699*) since he was giving new pricing. Correct call — always trust Jared's stated prices over code values.

## Pattern: Complex Feature → Single Agent
For self-contained HTML files (calculator), one full-stack-developer agent with a comprehensive prompt works better than splitting across multiple agents. The file is one unit — splitting would cause merge conflicts.

## Claude API Integration
The calculator chatbox uses the same Cloudflare Worker as the main page:
`https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages`
With fallback calculation if CORS blocks the request.
