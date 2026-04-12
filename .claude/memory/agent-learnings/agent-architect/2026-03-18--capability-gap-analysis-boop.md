---
date: 2026-03-18
type: capability-gap-analysis
trigger: BOOP scheduled task
---

# Capability Gap Analysis — March 18, 2026

## Key Findings

### Overloaded Agents
- full-stack-developer: 44 invocations (5+ domains collapsed into 1 agent)
- browser-vision-tester: 31 (all QA, qa-engineer at 0)

### Critical Gaps
1. **Security debt**: Portal MVP + investor pages shipped with 0 security reviews
2. **20/22 dept agents never invoked** despite dept-first routing mandate
3. **No perf optimization** on WebGL/3D pages (12 builds, 0 perf checks)
4. **CF Pages deploy** repeated daily with no automation/agent ownership
5. **full-stack-developer overload** — doing blogs, portal, 3D, audio, avatars

### Proposed Actions
1. Invoke security-auditor on portal + investor (immediate debt)
2. Create CF Pages deploy skill (codify manual workflow)
3. Pair performance-optimizer with WebGL reviews
4. Decide fate of 20 unused dept agents (prune or enforce)
5. Route blog publishing away from full-stack-developer
