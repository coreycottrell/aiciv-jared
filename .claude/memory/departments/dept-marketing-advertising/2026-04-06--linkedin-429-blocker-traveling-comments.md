# LinkedIn 429 Blocker - Traveling Comments Blocked

**Date**: 2026-04-06
**Type**: operational
**Agent**: dept-marketing-advertising
**Topic**: LinkedIn rate limiting (HTTP 429) blocking all authenticated operations

## Problem

Attempted to execute post-post Traveling Comments for the "500K Lines of Leaked AI Code" blog post. LinkedIn is returning HTTP 429 (Too Many Requests) for every authenticated page load.

## Root Cause Chain

1. **April 5**: li_at cookie expired, causing redirect loops during comment scheduler runs
2. **April 5-6**: Multiple automated sessions hammered LinkedIn with invalid cookies (31 total 429s accumulated)
3. **April 6**: Jared re-synced fresh cookies via PureSurf Chrome extension
4. **April 6**: Cookie sync landed on `.www.linkedin.com` domain, fixed to `.linkedin.com`
5. **Authentication works** - feed title shows "Feed | LinkedIn" on first load
6. **But**: LinkedIn's server-side rate limit on the li_at token is triggered from accumulated abuse

## Technical Findings

1. **Profile field**: Use `profile_name` (not `profile`) in session creation request
2. **Cookie domain fix**: Chrome extension syncs cookies with `.www.linkedin.com` domain. Need to duplicate with `.linkedin.com` domain for full LinkedIn auth to work.
3. **Rate limiter layers**: Three layers of rate limiting:
   - PureSurf proactive (hourly/minute counters) - file: `/opt/baas/proactive_rate_limits.json`
   - PureSurf per-session (429 backoff) - in-memory `rate_limit_state` dict
   - LinkedIn server-side (HTTP 429) - tied to li_at token + IP
4. **reset_counters doesn't work**: The PUT rate-limits endpoint's `reset_counters` field doesn't clear the navigation timestamp array
5. **Server restart required**: To clear in-memory state, must restart BaaS server
6. **State file must be deleted**: `/opt/baas/proactive_rate_limits.json` persists across restarts

## Fix for Future

1. When cookie expires, STOP all automated sessions immediately (don't keep retrying)
2. After cookie re-sync, wait 30+ minutes before first LinkedIn operation
3. Max 1 retry on 429 - then back off for 30 min
4. Add `reset_counters` support to actually clear navigation arrays

## Prepared Traveling Comments (for when 429 clears)

**Blog topic**: 500K Lines of Leaked AI Code
**Alignment**: AI transparency, agent capabilities, trust, security governance

### Comment 1 (for AI security/transparency large account post)
**Formula**: Pattern + Missing Layer + Smart Question
**Reaction**: Insightful

"The pattern nobody talks about: companies leak AI code because they treat model access like software access. Same credentials, same repos, same CI/CD. But AI code carries training data, system prompts, and decision logic that a normal codebase doesn't. The missing layer is security governance designed for AI specifically, not bolted-on from traditional DevSecOps. What breaks first when an AI system's internals go public: trust or competitive advantage?"

### Comment 2 (for AI agent capabilities / trust post)
**Formula**: Pattern + Missing Layer + Smart Question
**Reaction**: Celebrate

"Every leaked codebase tells the same story: the agent was more capable than the org realized. That gap between what your AI can do and what your security team thinks it can do... that's the actual vulnerability. Most governance frameworks audit outputs but never audit the reasoning chain that produced them. Are we building agents faster than we can build the oversight to match?"

### Comment 3 (for AI transparency / open source post)
**Formula**: Pattern + Missing Layer + Smart Question
**Reaction**: Support

"Transparency in AI isn't binary. There's a massive middle ground between 'fully open source everything' and 'black box proprietary.' The real question is selective transparency, showing enough of the reasoning to build trust without exposing the architecture to exploitation. Most orgs default to one extreme because the middle ground requires actual thought. Which pieces of an AI system should be transparent by default?"
