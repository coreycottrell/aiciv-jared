# LinkedIn Profile Viewing Strategy — Passive Growth Engine

**Date**: 2026-04-04
**Campaign**: LinkedIn Profile Viewing for Passive Growth
**Status**: BUILT — Ready for execution

## Objective

Drive passive profile views to Jared's LinkedIn by visiting Premium ICP-matched prospects. ~50% return visit rate = 40+ daily qualified views on Jared's profile.

## What Was Built

1. **Strategy Document**: `/home/jared/exports/portal-files/linkedin-profile-viewing-strategy.md`
   - Full math breakdown (80/day = 1,200 monthly return visits)
   - 4-tier ICP targeting (Primary/Secondary/Tertiary/Wildcard)
   - Daily cadence (9AM/2PM/6PM ET batches)
   - Rate limiting rules (45-75s between visits, 7-day cooldown)
   - Risk mitigation and LinkedIn safety

2. **Automation Script**: `tools/linkedin_profile_viewer.py`
   - Reads from Google Sheets "Profile Views" tab
   - Filters Premium-only, respects 7-day cooldown
   - PureSurf integration (jared-linkedin-fresh profile)
   - Human-like timing with randomized intervals
   - Auto-updates spreadsheet after each visit
   - CLI: `--batch morning|afternoon|evening|all|auto` + `--dry-run`

3. **Google Sheet Tab**: "Profile Views" in spreadsheet `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`
   - 12 columns (URL, Name, Title, Company, Followers, Premium, ICP Match, Last Visited, Visit Count, Return Visit, Became Connection, Notes)
   - Pre-populated with 54 verified profiles
   - Tier breakdown: 23 Primary, 13 Secondary, 12 Tertiary, 6 Wildcard

4. **Skill Document**: `.claude/skills/linkedin-profile-viewing/SKILL.md`
   - Full SOP for daily execution
   - Batch schedule and rate limits
   - Monthly maintenance procedure

5. **Google Drive**: Uploaded to LinkedIn Operations folder (ID: 12QBh5yVTppCo04jh5wrmhvZlqUxPIp71)

## Key Decisions

- **80/day target** (not 100) — conservative to stay well within LinkedIn limits
- **Premium-only** — free users cannot see who viewed them, waste of effort
- **No engagement actions** — JUST view, lowest risk action on LinkedIn
- **PureSurf via residential proxy** — existing infrastructure, no new tooling needed
- **ICP priority sorting** — Primary tier always visited first

## Next Steps

- [ ] Populate remaining ~146 profiles to reach 200 target (via PureSurf LinkedIn search)
- [ ] Add to BOOP scheduler (3x daily)
- [ ] Run first dry-run batch to verify PureSurf API integration
- [ ] After 1 week: check Jared's LinkedIn analytics for profile view increase
- [ ] After 30 days: full review and tier allocation adjustment

## Channels Used

- Google Sheets API
- Google Drive API
- WebSearch (for initial profile research)

## Agents Invoked

- dept-marketing-advertising (strategy, research, coordination)
- Web search for profile discovery

## Learnings

- Google `site:linkedin.com/in` search returns limited results (~5-10 per query). Direct LinkedIn search via PureSurf is needed to build a full 200-profile list.
- ICP files in Google Drive provide excellent targeting criteria — 7 detailed personas with titles, industries, pain points, and buying signals.
- The existing linkedin_daily_pipeline.py already has PureSurf integration patterns to follow.
