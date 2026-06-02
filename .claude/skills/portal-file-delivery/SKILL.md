---
name: portal-file-delivery
version: 1.0.0
author: aether
description: Deliver files to human via PureBrain portal using portal_deliver.sh
tags: [portal, files, delivery, communication]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Portal File Delivery

Canonical method for delivering files to the human partner via the PureBrain portal.

## Protocol

1. File MUST be in an allowed path: `~/exports/`, `~/to-human/`, `~/purebrain_portal/`, `~/from-acg/`, `~/portal_uploads/`
2. Use `./tools/portal_deliver.sh /abs/path "caption" "display-name"`
3. This creates a `[PORTAL_FILE:]` chat entry via WebSocket
4. NEVER use `[FILE: path]` (doesn't render) or `tg_send.sh --file` (wrong channel)
5. Writing to `~/exports/portal-files/` alone does NOT deliver — must call portal_deliver.sh

## Common Patterns

```bash
# Deliver a report
./tools/portal_deliver.sh /home/jared/exports/portal-files/report.md "Daily Report" "report.md"

# Deliver an image
./tools/portal_deliver.sh /home/jared/exports/portal-files/chart.png "Performance Chart" "chart.png"
```

## Anti-Patterns

- NEVER use `/dev/stdin` as file path (fails with "File not found")
- NEVER deliver from project-tree `exports/` (REJECTED — must be absolute home paths)
- Always write temp files first, then deliver

## Verification

After delivery:
```bash
# Check portal chat for [PORTAL_FILE:] entry
# Verify file appears in portal UI downloads section
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| "File not found" | Wrong path | Use absolute `~/` paths only |
| No delivery | Forgot to call script | Must call `portal_deliver.sh` |
| "Permission denied" | File outside allowed paths | Move to `~/exports/` first |

## Integration with Other Skills

Works with:
- `session-handoff-creation` - Deliver handoff docs
- `memory-weaving` - Deliver memory summaries
- `session-summary` - Deliver session reports

## Constitutional Grounding

From MEMORY.md:
> "Portal is PRIMARY. Canonical: `./tools/portal_deliver.sh /abs/path "caption" "display-name"` — creates [PORTAL_FILE:] chat entry via WebSocket. NEVER `[FILE: path]` (doesn't render) or `tg_send.sh --file` (wrong channel)."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
