# Memory: Departmentalization Pattern (Reusable Template)

**Date**: 2026-02-23
**Type**: architectural
**Agent**: the-conductor

## What Happened

Jared requested an isolated "Client Marketing" department — completely walled off from Pure Technology/PureBrain/PureMarketing operations. This is the FIRST department and Jared said "we are going to build more agents like this very soon for different reasons."

## The 5-Component Department Template

When creating isolated departments, ALWAYS create all 5:

1. **Agent Manifest**: `.claude/agents/[dept-name].md`
   - YAML frontmatter with name, description, tools, skills, model
   - Isolation protocol clearly stated
   - Can spin up own sub-teams

2. **Skill + Trigger**: `.claude/skills/[dept-name]/SKILL.md`
   - Trigger word(s) clearly defined
   - Routing rules (ALWAYS route / NEVER route)
   - Isolation protocol (which agents it cannot interact with)

3. **Export Directory**: `exports/[dept-name]/`
   - All deliverables go here, organized by client/project
   - Never mixed with other department output

4. **Memory Directory**: `.claude/memory/agent-learnings/[dept-name]/`
   - Department's learnings stay in its own silo
   - No cross-pollination with other departments

5. **Permanent Memory Rule**: Entry in MEMORY.md
   - Loads EVERY session automatically
   - Cannot be forgotten across context compactions
   - Includes trigger word, isolation rules, Jared's exact words

## Proof Protocol

When Jared asks "is this locked in?", VERIFY and PROVE:
- `test -f` on each file
- `test -d` on each directory
- `grep` the memory rule in MEMORY.md
- Show all results in one Telegram message

## Future Departments (Expected)

Jared said more are coming. Possible patterns:
- Different client verticals
- Internal vs external isolation
- Project-specific sandboxes
- Partner-specific workstreams

## Key Quote

"Anything that gets sent to you with CLIENT MARKETING attached should not influence anything to do with Pure ANYTHING!!" — Jared, 2026-02-23
