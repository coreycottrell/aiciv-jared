# Overnight Swarm Pattern - 2026-02-15

**Type**: operational
**Topic**: Multi-agent parallel deployment for overnight content creation
**Confidence**: High (successfully executed)

---

## Pattern: Overnight Content Swarm

When Jared signs off for the night with a request like "surprise and delight me for tomorrow":

### Deploy 5 Agents in Parallel

```
1. web-researcher → Blog topic research (trending AI news)
2. linkedin-researcher → LinkedIn content (newsletter + post)
3. browser-vision-tester → Mobile audit (responsiveness check)
4. ui-ux-designer → Site recommendations (edit checklist)
5. marketing-strategist → Strategic ideas (scaling, influence)
```

### Key Success Factors

1. **Run in background** - Use `run_in_background: true` so all 5 work simultaneously
2. **Specific output paths** - Tell each agent exactly where to write their output
3. **Don't duplicate existing work** - Check what's already prepared first
4. **Create morning briefing** - Consolidate all outputs into one executive summary

### Output Structure

```
to-jared/MORNING-BRIEFING-YYYY-MM-DD.md  ← Executive summary
exports/
  ├── blog-drafts/                        ← Topic research
  ├── linkedin-newsletters/               ← Long-form content
  ├── linkedin-posts/                     ← Short-form content
  ├── site-edit-recommendations-*.md      ← UX checklist
  ├── mobile-audit-*.md                   ← Responsiveness report
  └── strategic-scaling-ideas-*.md        ← Business strategy
```

### Watch Mode Recognition

After overnight work is exhausted:
- Acknowledge automated BOOPs minimally
- Don't create busy-work
- Note "watch mode" status
- Systems health check is acceptable periodic task

---

## Anti-Patterns

- ❌ Doing research yourself instead of delegating
- ❌ Creating duplicate content that already exists
- ❌ Responding verbosely to every automated BOOP
- ❌ Making up work when meaningful tasks are complete

---

## Results This Session

- 5 agents completed successfully
- 8 deliverable files created
- ~150K tokens of agent work
- Morning briefing ready by ~00:00 UTC
- Watch mode from ~01:30 UTC onward
