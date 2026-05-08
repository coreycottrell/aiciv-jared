# LinkedIn ICP Re-seed + PureSurf Queue Reschedule — 2026-05-01

**Type**: operational + teaching
**Owner**: dept-marketing-advertising (MA#)
**Trigger**: Self-fix follow-up to today's BOOP (LinkedIn pipeline shipped 0 posts)
**Pair verifier scheduled**: OP# 24h verification

---

## Ground-Truth State (verified, not assumed)

### Issue 1: `configs/linkedin_icps.json`

**Framing said**: "empty — re-seed"
**Actual state**: file is 2,194 bytes, structurally valid JSON. What's empty is the `profiles: []` array. Schema is intact:
- `_meta` (seeded 2026-04-14 from Drive `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3`)
- `segments` — 6 ICP types (agency-director, ecommerce-owner, finance-realestate, ops-manager, smb-founder, solo-consultant), each with `drive_id` to the persona doc
- `profiles` — `[]` since file was created
- `block_list` — 6 entries (jareddsanborn, jared-sanborn, coreycottrell, nathan-puretech placeholder, greg-advisor placeholder, chris-advisor placeholder)

**Why profiles is empty**:
- The 6 persona docs in `configs/icp_personas/` are **avatar descriptions** (Priya Mehta, etc.) — fictional ICP composites, not real LinkedIn profiles
- Discovery pipeline (`linkedin_icp_commenter.py`) ran 15 times Apr 14 (`configs/linkedin_icp_discovery_log.jsonl`), every run returned `backend: "none", raw_results: 0` — no search backend wired
- `configs/linkedin_icp_candidates.json` is `{candidates: []}`
- Backup `linkedin_icps.json.bak-2026-04-15` is identical (also empty profiles)

**Critical conclusion**: This is **not a re-seed problem** (nothing to restore from). It is a **discovery problem** — real LinkedIn handles for the 6 segments have never been collected. Manufacturing handles would violate the never-comment-team-members principle's spirit (we'd be commenting on strangers we haven't human-vetted).

**Constitutional gate**: only Jared (or a manual research pipeline he approves) can populate real profile handles. MA# cannot make that call alone.

### Issue 2: PureSurf scheduled queue

**Framing said**: "24 posts but 0 in today's slots — bulk reschedule"
**Actual state**: confirmed exact match.
- API: `GET https://surf.purebrain.ai/social/scheduled` (X-API-Key from `BAAS_API_KEY` in `.env`)
- Returns: `{posts: [...], count: 24}` (note: wrapper object, not bare array — schema gotcha)
- All 24 `scheduled_time` values fall in **April 7-19** (12+ days stale)
- Status breakdown: 21 `approved` (pending publish) + 3 `posted` (already shipped, kept in queue)
- 0 posts scheduled for May 1 or any future date
- Prior cadence (ET): 8:30am, 11:00am, 1:00pm, 3:00pm — exactly the 4 slot definitions in `tools/linkedin_scheduled_poster.py`
- Reschedule API per code comment: `PUT https://surf.purebrain.ai/social/schedule/{id}` with new `scheduled_time`

**21 posts to redistribute across May 1-31 = 31 days × 4 slots = 124 available slots.** Easy fit.

---

## Delegation Decisions

**MA# does not execute. Per conductor-of-conductors:** spawn specialists, synthesize, report.

### Issue 1 → escalated to Jared (cannot self-fix)

Spawning `linkedin-researcher` to **manufacture** real profile URLs from the persona docs would be wrong:
- Pure-tech principle: engineer resonance, don't spray. Random matched-keyword profiles ≠ resonance.
- Constitutional: never comment on team members. Auto-discovered handles haven't been vetted against the team whitelist (`1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`).
- The original `_meta.note` from Apr 14 explicitly says "must be populated by Jared or the research pipeline."

**MA# action**: surface this back to Jared as a sourcing decision, not a re-seed task. Recommend three options:
1. Jared drops a CSV/list of vetted LinkedIn handles per segment (fastest, highest quality)
2. ST# wires a search backend (SerpAPI / phantombuster) into `linkedin_icp_commenter.py` and runs supervised discovery (Jared approves each batch before it lands in `profiles[]`)
3. linkedin-researcher manually collects 5 candidates per segment from public posts in Jared's existing engagement history (slowest, but human-vettable)

### Issue 2 → delegated to linkedin-specialist for execution plan + linkedin-researcher for cadence sanity

linkedin-specialist deliverables:
- Distribution plan: 21 approved posts × May 1-31 / slots 8:30a, 11a, 1p, 3p ET
- Order by current `scheduled_time` (preserve original sequence) or content theme cluster
- Avoid weekends if Jared's pattern excludes them (verify from prior posted history)
- Generate exact `PUT` payloads (id → new `scheduled_time` ISO UTC)
- Stop short of executing — return the plan as a JSON list for human approval, then run the reschedule loop (PureSurf-first, then Sheet, then Drive, per source-of-truth doctrine)

linkedin-researcher deliverable: 1-paragraph cadence sanity check (algorithmic windows, May holidays to avoid: Memorial Day May 25 weekend).

---

## Out of Scope (ST# owns)

- LinkedIn cookie/session refresh
- PureSurf session lifecycle fix
- Any actual posting/commenting (gated until ST# verifies cookies + session)

---

## Verification Plan

- 24h pair with OP# verifier: confirm
  - (a) ICP sourcing decision unblocked by Jared
  - (b) PureSurf queue actually has approved posts in future May slots
  - (c) Next BOOP post-ST# fix actually ships content
- Per `feedback_verifier_independence_audit_separation.md`: OP# is independent verifier, not MA#

---

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/configs/linkedin_icps.json` — 2,194 bytes, profiles=[], segments=6, block_list=6
- `/home/jared/projects/AI-CIV/aether/configs/linkedin_icps.json.bak-2026-04-15` — identical to current
- `/home/jared/projects/AI-CIV/aether/configs/linkedin_icp_candidates.json` — `{candidates: []}`
- `/home/jared/projects/AI-CIV/aether/configs/linkedin_icp_discovery_log.jsonl` — 15 runs, all 0 results
- `/home/jared/projects/AI-CIV/aether/configs/icp_personas/icp-*.md` — 6 avatar docs (no real handles)
- `/home/jared/projects/AI-CIV/aether/tools/linkedin_icp_commenter.py` — schema + commenter logic
- `/home/jared/projects/AI-CIV/aether/tools/linkedin_scheduled_poster.py` — slot definitions, reschedule API
- `https://surf.purebrain.ai/social/scheduled` — source of truth (returns `{posts, count}`)
