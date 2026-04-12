# Pure Brain User Behavior Patterns

**Date**: 2026-02-13
**Type**: synthesis
**Topic**: Onboarding UX patterns from first real user data
**Confidence**: high

## Context

Analyzed 74 Pure Brain web conversation entries (2026-02-10 to 2026-02-12) to identify user behavior patterns, drop-off points, and onboarding friction.

## Key Discoveries

### 1. Session Management Bug (Critical)
- 92% of entries (68/74) have session_id = "unknown"
- Sessions aren't persisting between messages
- This breaks user journey tracking and returning user reconnection
- **Must fix before meaningful analytics possible**

### 2. The Atlas User Archetype
First real engaged user profile:
- Named AI "Atlas" (mythological, powerful)
- Stayed 33 minutes in single session
- Mostly sent "hi" messages (testing/exploring)
- Eventually asked substantive question ("what are the top news today")
- Left their own name as "Guest User" (didn't invest in self-naming)

This represents the "curious explorer" - willing to engage but needs guidance.

### 3. AI Naming Patterns
Users who name their AI choose:
- **Mythological names**: Atlas, Nexus
- **NOT human names**: People want AI to feel distinct
- Suggested categories for onboarding: Mythological, Abstract/Tech, Nature

### 4. Drop-off Funnel
| Stage | Drop-off Rate |
|-------|---------------|
| Page load to first message | 40% |
| First message to AI naming | 75% |
| AI naming to multi-turn | 50% |

### 5. First Message Intent Categories
1. **Greetings** ("hi", "hello") - testing the waters
2. **Tasks** ("Create a landing page") - know what they want
3. **Information** ("what are top news today") - seeking utility

Current onboarding serves none of these well.

## Recommendations

1. **Fix session persistence** - P0 infrastructure bug
2. **Warm up welcome message** - too generic currently
3. **Defer or assist AI naming** - high friction, low completion
4. **Add use-case prompts** - help task-oriented users
5. **Handle greetings gracefully** - don't be robotic with casual greeters

## File References
- Full analysis: `/home/jared/projects/AI-CIV/aether/to-jared/PUREBRAIN-PATTERNS-2026-02-13.md`
- Raw data: `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl`
- Export CSV: `/home/jared/projects/AI-CIV/aether/exports/purebrain_leads.csv`

## Future Application
When analyzing onboarding flows or user engagement:
- Look for session management issues first
- Identify user archetypes from behavior patterns
- Track drop-off at each decision point
- Match first messages to user intent categories
