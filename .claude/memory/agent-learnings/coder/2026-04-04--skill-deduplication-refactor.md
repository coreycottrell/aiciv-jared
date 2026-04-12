# Skill Deduplication Refactoring

**Date**: 2026-04-04
**Type**: Teaching
**Topic**: Documentation structure - single authoritative source pattern

## Problem

5 LinkedIn content skills had duplicated information written in multiple places. When one document updated, others went stale. The reviewer found violations of "one topic = one source."

## Solution

Implemented the **authoritative source reference pattern**:
- Each topic has ONE authoritative document
- Other docs reference it instead of duplicating content
- Quick summaries OK, but point to full spec

## Files Changed

### 1. content-creation-sop/SKILL.md (5 edits)
- Comment Rules → Reference `linkedin-commenting-strategy`
- Platform Dimensions → Reference `purebrain-social-design`
- Filing Structure → Reference `linkedin-drive-organization`
- Daily Schedule → Reference `linkedin-daily-operations`
- **REMOVED** Target Account Tiers (moved to linkedin-commenting-strategy)

### 2. purebrain-social-design/SKILL.md
- **ADDED** Agent Routing section (3d-design-specialist only, never MA#)

### 3. linkedin-commenting-strategy/SKILL.md
- **ADDED** Target Account Tiers (moved from content-creation-sop)
- **ADDED** First Comment Protocol
- **ADDED** Pre-Post and Post-Post Timing

### 4. linkedin-daily-operations/SKILL.md
- Google Drive Filing → Reference `linkedin-drive-organization`

### 5. linkedin-drive-organization/SKILL.md
- No changes (already authoritative)

## Pattern Learned

**Reference Format**:
```markdown
### Topic Name
**Authoritative Source**: See `skill-name` skill for the complete [details].

[Brief summary for quick reference]
```

**Benefits**:
- Single source of truth
- Updates propagate via reference, not copy-paste
- Readers know where to go for full details
- Quick summaries still available for convenience

## Verification

```bash
# Check references added
grep -n "Authoritative Source" .claude/skills/*/SKILL.md

# Verify removal
grep -n "Tier 1" .claude/skills/content-creation-sop/SKILL.md  # Should return nothing

# Verify additions
grep -n "TARGET ACCOUNT TIERS" .claude/skills/linkedin-commenting-strategy/SKILL.md
```

## Application to Future Skill Work

When creating or updating skills:
1. Ask: "Is this THE authoritative source for this information?"
2. If NO → add reference to authoritative source
3. If YES → keep it, let others reference you
4. Never duplicate content across multiple skills
5. Quick summaries with references > full duplication

## Files Paths
- `.claude/skills/content-creation-sop/SKILL.md`
- `.claude/skills/purebrain-social-design/SKILL.md`
- `.claude/skills/linkedin-commenting-strategy/SKILL.md`
- `.claude/skills/linkedin-daily-operations/SKILL.md`
- `.claude/skills/linkedin-drive-organization/SKILL.md`
