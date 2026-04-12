# Google Calendar Skill Creation

**Date**: 2026-02-12
**Agent**: capability-curator
**Type**: pattern
**Topic**: Creating comprehensive infrastructure skill from existing tool

## Context

Created a comprehensive Google Calendar skill that wraps the existing `tools/gcal_manager.py` implementation. This follows the pattern established by `gdrive-operations` and `telegram-integration` skills.

## What Worked

1. **Leveraged existing infrastructure** - The gcal_manager.py already had all core capabilities (create, edit, delete, free/busy, quick add). The skill documents and surfaces these capabilities.

2. **Followed established skill format** - Used YAML frontmatter with name, version, description, triggers. Matched the pattern from other infrastructure skills.

3. **Comprehensive documentation approach**:
   - Quick reference section for common operations
   - CLI reference for shell usage
   - Python API examples for programmatic access
   - Error handling patterns
   - Agent integration guidance
   - Troubleshooting section

4. **Triggers defined for semantic matching** - calendar, schedule, meeting, appointment, event, availability, free time, busy, gcal

## Key Patterns Documented

1. **Creating events** - Standard, with attendees/reminders, all-day, multi-day, natural language quick add
2. **Editing events** - Partial updates (only specified fields change)
3. **Deleting events** - With/without notifications
4. **Checking availability** - Free/busy query, find available slots with work hours
5. **Setting reminders** - Popup and email methods
6. **Inviting attendees** - During creation or via update
7. **Reading schedule** - List events, today's events, search, single event details

## Implementation Note

The skill does NOT modify gcal_manager.py - it documents the existing implementation. The tool already supports:
- OAuth2 + Service Account authentication (priority order)
- Automatic token refresh
- Timezone handling
- All CRUD operations
- Natural language parsing via Google's quickAdd

## Skill Location

`/home/jared/projects/AI-CIV/aether/.claude/skills/google-calendar/SKILL.md`

## Dependencies

- `tools/gcal_manager.py` (implementation)
- `tools/gcal_oauth_setup.py` (OAuth setup)
- `.credentials/oauth-token-calendar.json` (token storage)

## Agent Recommendations

Agents that should use this skill:
- **human-liaison** - Schedule meetings, check Jared's availability
- **the-conductor** - Morning schedule check in wake-up ritual
- **task-decomposer** - Time estimation for complex tasks

## Cross-CIV Potential

This skill could be shared with sister collectives via comms hub skills library. The pattern is generic enough to work with any Google Calendar integration.

## Next Steps

1. Add to skills-registry.md
2. Consider granting to human-liaison first (most relevant use case)
3. Validate with actual calendar operations

## Meta-Insight

Infrastructure skills that wrap existing tools follow a predictable pattern:
1. Document the tool's capabilities comprehensively
2. Provide both CLI and Python API examples
3. Include error handling and troubleshooting
4. Define triggers for semantic skill matching
5. Recommend which agents should use it

This pattern could be templated for future tool-wrapping skills.
