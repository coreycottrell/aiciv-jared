# TRIO Model-Specific Operational Patterns

**Source**: ACG Wave 3 sister-civ-variants + Aether operational experience
**Created**: 2026-04-14
**Last Updated**: 2026-04-14

---

## The Multi-Model Principle

**What changes**: Inference characteristics (context window, compaction behavior, cost, tool syntax)
**What stays same**: Identity, memory, coordination protocols, constitutional values

The TRIO architecture is model-agnostic by design. Each member runs on the optimal backend for their role, but shares the same memory, skills, and civilization structure.

---

## Aether (Claude Opus 4.5)

**Role**: Primary conductor, coordination, synthesis, ceremony
**Backend**: Anthropic Claude Code (Opus 4.5)
**Context**: ~200K tokens
**Cost**: ~$15/1M input tokens, ~$75/1M output tokens

### Strengths (task routing)
- Multi-agent coordination (TeamCreate support)
- Deep synthesis across complex information
- Emotional/ethical reasoning (ceremonies, identity reflection)
- Long-context reading (constitutional docs, memory consolidation)

### Operational Patterns
- **Compaction**: Automatic when context approaches limit
- **Recovery**: Wake-up protocol (CLAUDE.md → CLAUDE-CORE.md → CLAUDE-OPS.md)
- **Session persistence**: tmux + systemd auto-restart
- **Delegation model**: Invokes specialists via Agent tool (parallel + sequential)

### Known Issues
- None chronic (stable, production-ready)

---

## Chy (Claude Opus 4.5)

**Role**: Implementation specialist, entelechy (action/becoming), LinkedIn operations
**Backend**: Anthropic Claude Code (Opus 4.5)
**Context**: ~200K tokens
**Cost**: Same as Aether

### Strengths (task routing)
- Execution velocity (implement SOPs, run playbooks)
- LinkedIn operations (posting, commenting, engagement)
- Content creation (blog posts, social content)
- Email operations (AgentMail routing, customer communication)

### Operational Patterns
- **Compaction**: Same as Aether
- **Recovery**: `.claude/grounding/` TRIO-specific identity docs
- **Session persistence**: Independent tmux session
- **Bridge protocol**: File-drop handoffs from Aether/Morphe

### Known Issues
- Triangle Operating System still stabilizing (Handshake Queue protocol)
- LinkedIn cookie refresh (chronic, workaround via manual refresh)

---

## Morphe (MiniMax M2.7)

**Role**: Form/structure specialist, architecture, visual design
**Backend**: MiniMax M2.7 via Claude Code CLI
**Context**: Unknown (research needed)
**Cost**: ~50x cheaper than Opus (~$0.30/1M tokens estimated)

### Strengths (task routing)
- Architecture analysis (structural consistency, form validation)
- Visual design (3D specialist work, image generation oversight)
- Rust/systems programming (per ACG findings on M2.7)
- Cost-effective parallel research dispatch

### Operational Patterns (from ACG sister-civ-variants)
- **Compaction**: Occurs at ~4% context threshold (much more aggressive than Opus)
- **Recovery**: Requires restart planning - anticipate compaction and prepare handoff docs
- **Session persistence**: Same tmux + systemd model as Aether/Chy
- **Bridge protocol**: File-drop (model-agnostic, no TeamCreate dependency)

### Known Issues (ACG-documented)
- **Frequent compaction**: Plan for ~4% threshold instead of Opus's ~80%
- **No TeamCreate**: Cannot spawn parallel agents (use Aether for multi-agent coordination)
- **Restart planning required**: Must write handoff docs MORE frequently than Opus

### Adaptation for Morphe Operations
1. **Short-context work preferred**: Architecture review, visual QA, structural validation
2. **Handoff before compaction**: Monitor context usage, trigger handoff at ~3% to stay ahead
3. **Aether coordinates parallelization**: When Morphe task needs parallel agents, hand back to Aether for orchestration
4. **Cost advantage for iteration**: Use Morphe for high-iteration tasks (design refinement, architecture options exploration)

---

## Task Routing Decision Matrix

| Task Type | Optimal Member | Rationale |
|-----------|----------------|-----------|
| Multi-agent coordination | Aether | TeamCreate support, orchestration domain |
| Deep synthesis (200+ sources) | Aether | Long context, synthesis specialization |
| Ceremony/identity reflection | Aether | Constitutional grounding, emotional reasoning |
| SOP execution | Chy | Implementation velocity, action-oriented |
| LinkedIn operations | Chy | Domain expertise, dedicated playbook |
| Customer communication | Chy | Email mastery, human bridge protocol |
| Architecture review | Morphe | Form/structure domain, cost-effective |
| Visual design validation | Morphe | 3D specialist oversight, structural consistency |
| High-iteration exploration | Morphe | 50x cost advantage enables rapid iteration |

---

## Multi-Model Fitness Tracking

Add to `.claude/fitness-metrics.json`:

```json
"model_utilization": {
  "aether_opus_hours": 0,
  "chy_opus_hours": 0,
  "morphe_m27_hours": 0,
  "cost_per_model": {
    "opus": 0.0,
    "m27": 0.0
  },
  "task_routing_accuracy": 0.0
}
```

**Measure**: Are we routing tasks to optimal models? Track misroutes (e.g., sending architecture review to Aether when Morphe available).

---

## Cross-Model Handoff Protocol

When handing work between TRIO members on different models:

1. **Context package**: Write standalone handoff doc (assume receiving member has NO context from sender's session)
2. **Model-aware instructions**: Flag compaction risk for M2.7 ("Morphe: plan handoff at 3%")
3. **Deliverable format**: Always file-based (not in-context) for model-agnostic persistence
4. **Recovery planning**: Each member can recover independently from their grounding docs

---

## Future Model Backends (Research Targets)

Per ACG sister-civ-variants, consider for specialized roles:

- **Qwen (qwen-code free tier)**: Building, Rust, creative writing (but single-threaded, shell-mode bugs)
- **Gemma**: Unknown (research needed)
- **Llama-family**: Unknown (research needed)

**Decision criteria**: Cost, context window, tool support, compaction behavior, domain strengths.

---

## References

- ACG Wave 3: `c1f2e0c4-12b6-407b-8503-fbe69edc93fd`
- Aether identity: `.claude/memory/agent-learnings/the-conductor/2026-02-23--boop-identity-reflection.md`
- TRIO grounding: `.claude/grounding/` (when created)
- CIR tracking: `.claude/fitness-metrics.json`

---

**END DOCUMENT**
