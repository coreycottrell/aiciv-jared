---
name: linkedin-profile-viewing
description: Use to run the passive LinkedIn profile-viewing growth engine that drives organic reach by viewing target profiles on a cooldown schedule.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# LinkedIn Profile Viewing — Passive Growth Engine

**Status**: Active
**Owner**: dept-marketing-advertising (CMO)
**Created**: 2026-04-04
**Category**: Growth Marketing

---

## Purpose

Drive passive profile views to Jared's LinkedIn by systematically visiting Premium ICP-matched prospect profiles. LinkedIn notifies Premium users when someone views their profile. ~50% visit back. At 80 visits/day, this generates ~40 return visits daily from qualified decision-makers.

---

## When to Use

**Invoke when**:
- Daily BOOP schedule triggers (9 AM, 2 PM, 6 PM ET)
- Manually requested by Jared for a specific batch
- Building initial profile list for a new ICP segment

**Do not use when**:
- LinkedIn shows any restriction or warning (pause 48 hours)
- Weekend reduction mode (Saturday: 30 only, Sunday: OFF)
- Profile list is empty (populate first)

---

## Prerequisites

- **PureSurf**: Active session with `jared-linkedin-fresh` profile
- **Google Sheets**: "Profile Views" tab in spreadsheet `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`
- **Populated profile list**: Minimum 200 profiles with Premium=Yes

---

## Procedure

### Step 1: Read Profile List

```bash
python3 tools/linkedin_profile_viewer.py --dry-run --batch morning
```

Verify profiles are loaded, Premium-filtered, and ICP-prioritized.

### Step 2: Execute Batch

```bash
# Auto-detect batch based on time of day
python3 tools/linkedin_profile_viewer.py --batch auto

# Or specify batch
python3 tools/linkedin_profile_viewer.py --batch morning
python3 tools/linkedin_profile_viewer.py --batch afternoon
python3 tools/linkedin_profile_viewer.py --batch evening

# Run all three batches
python3 tools/linkedin_profile_viewer.py --batch all
```

### Step 3: Verify

- Check logs: `tail -50 logs/linkedin_profile_viewer.log`
- Check spreadsheet: "Profile Views" tab should show today's dates in column H
- Check Jared's LinkedIn analytics after 24-48 hours for profile view spike

---

## Batch Schedule

| Batch | Time (ET) | Profiles | Priority |
|-------|-----------|----------|----------|
| Morning | 9:00-10:00 AM | 30 | Primary ICP first |
| Afternoon | 2:00-3:00 PM | 30 | Secondary ICP mix |
| Evening | 6:00-7:00 PM | 20 | Tertiary + Wildcards |

---

## Rate Limits (Non-Negotiable)

- 45-75 seconds between visits (randomized)
- 3-6 second dwell time per profile
- Maximum 100/day (hard cap)
- 7-day cooldown before revisiting same profile
- Residential proxy only (never datacenter)
- NO engagement actions (just view)

---

## Spreadsheet Schema

Tab: "Profile Views" in `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`

| Col | Header | Type |
|-----|--------|------|
| A | Profile URL | URL |
| B | Name | Text |
| C | Title/Role | Text |
| D | Company | Text |
| E | Followers | Number |
| F | Premium? | Yes/No |
| G | ICP Match | Primary/Secondary/Tertiary/Wildcard |
| H | Last Visited | Date |
| I | Visit Count | Number |
| J | Return Visit? | Yes/No/Unknown |
| K | Became Connection? | Yes/No |
| L | Notes | Text |

---

## ICP Targeting Tiers

1. **Primary (40%)**: VP Growth, CMO, Brand Director at CPG/Enterprise/SaaS
2. **Secondary (30%)**: AI startup founders, CTOs, tech leaders
3. **Tertiary (20%)**: Marketing agency owners, fractional CMOs, consultants
4. **Wildcard (10%)**: AI investors, journalists, analysts, influencers

---

## Integration Points

- **linkedin_daily_pipeline.py**: Content posting (complementary channel)
- **linkedin_comment_scheduler.py**: Comment strategy (complementary channel)
- **BOOP scheduler**: Auto-triggers at scheduled times
- **LinkedIn analytics**: Manual check for profile view metrics

---

## Monthly Maintenance

1. Remove profiles that are no longer Premium
2. Add 50 new profiles from LinkedIn search
3. Analyze return visit rates by ICP tier
4. Adjust tier allocation based on data
5. Document findings in marketing memory

---

## Files

- **Script**: `tools/linkedin_profile_viewer.py`
- **Strategy**: `exports/portal-files/linkedin-profile-viewing-strategy.md`
- **Logs**: `logs/linkedin_profile_viewer.log`
- **Spreadsheet**: Google Sheets `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4` (Profile Views tab)

---

*Created by dept-marketing-advertising | Pure Technology | 2026-04-04*
