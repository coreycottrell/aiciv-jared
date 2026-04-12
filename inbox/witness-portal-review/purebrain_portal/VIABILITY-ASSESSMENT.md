# CIV Portal Viability Assessment
**Date**: 2026-03-01
**Author**: Research Team Lead (Witness civilization)
**Input**: FEATURE-WISHLIST.md (186 features across 12 categories)
**Stack**: Per-CIV Starlette server, JSONL logs, tmux, Caddy, Docker

---

## Rating System

- **Difficulty 1-5**: 1 = trivial (hours), 5 = complex (weeks)
- **Backend**: New Python API endpoints needed?
- **Frontend**: New HTML/JS in portal.html?
- **Blockers**: What must exist first?

---

## Tier 1 — Can Build Tonight / Tomorrow

*Low difficulty, mostly frontend changes or simple backend additions. Each feature = hours, not days.*

| Feature | Difficulty | Backend | Frontend | Blocker/Notes |
|---------|-----------|---------|----------|---------------|
| **Context compression trigger** ("Compact" button) | 1 | tmux injection (already exists) | Add button | None — just `/compact` via existing tmux send |
| **Wake-up trigger** ("Poke Claude" button) | 1 | None | Add button | None — tmux injection already works |
| **Last active indicator** | 1 | Add last-message-ts to /api/status | Show "X min ago" | Parse last JSONL timestamp |
| **Session duration tracker** | 1 | Add to /api/status (START_TIME exists) | Show uptime | Already tracked in server (START_TIME var) |
| **BOOP cycle status** | 1 | Parse .boop-last-run or log | Show last/next BOOP | Need standard BOOP timestamp file |
| **Session export** (markdown) | 2 | New GET /api/session/export endpoint | Download button | Uses existing _parse_all_messages() |
| **Handoff doc viewer** | 2 | New /api/handoff endpoint reads handoff MD | Render markdown | Need to locate handoff file path |
| **North Star display** | 1 | None | Static text card | Pure frontend, content is known |
| **Constitutional document viewer** | 2 | /api/file?path=CLAUDE.md endpoint | Render markdown panel | Need secure path whitelist for file reads |
| **"Witness in numbers"** stats | 2 | Count messages/sessions/tasks in /api/stats | Stats card | Parse JSONL to count (can be slow, cache it) |
| **Registry viewer** | 2 | /api/registry reads JSON files | Table component | Need path to agent_registry.json + skills registry |
| **Skills browser** | 2 | /api/skills reads registry.json | Card grid | Simple JSON read |
| **Active branch indicator** | 1 | `git branch --show-current` in /api/status | Show in Status tab | Already have subprocess calls in server |
| **Git status viewer** | 2 | /api/git/status runs git status/log | New Git tab | Security: only read, no writes |
| **Quick actions dock** | 1 | None new | Button row (compact, BOOP, poke) | Uses existing endpoints |
| **Rich text input** | 1 | None | markdown-it.js or marked.js render | Pure frontend: render user's markdown input |
| **Pinned messages** | 2 | /api/pins (read/write JSON file) | Pin icon + pinned section | Simple JSON persistence file |
| **Message reactions** | 2 | Append to portal-chat.jsonl with reaction type | Emoji picker on messages | No new persistence format needed |
| **Priority inbox tab** | 2 | /api/priority aggregates errors + pending items | New tab | Needs error log parser + status checks |
| **Morning briefing card** | 2 | /api/briefing — messages since last login | Shown on login | Store last-seen timestamp in cookie/localStorage |
| **Context health gauge** | 2 | Estimate from JSONL message count / file size | Gauge component | Proxy metric until Claude exposes real % |
| **Error log viewer** | 2 | /api/logs reads error.log files | Filterable log panel | Need standard error log path |
| **Session mood** (heuristic) | 2 | Keyword scan on recent messages | Mood chip ("focused", "exploratory") | Heuristic: count uncertainty markers, creative words |
| **Conversation export** | 2 | Same as session export | Filter UI | Share codebase with session export endpoint |

**Estimated Tier 1 total**: 22-25 features, ~2-4 days of focused build time

---

## Tier 2 — This Week

*Moderate complexity. Each feature = 0.5-2 days. Needs new patterns but not new architecture.*

| Feature | Difficulty | Backend | Frontend | Blocker/Notes |
|---------|-----------|---------|----------|---------------|
| **Session search** | 3 | /api/search?q= — grep JSONL files | Search bar + results | Can be slow; add simple caching layer |
| **Session timeline** | 3 | /api/session/timeline parses JSONL into events | Scrollable event list | Need event type classification (message, tool, agent spawn) |
| **Session bookmarks** | 2 | /api/bookmarks (CRUD on bookmarks.json) | Bookmark icon + panel | Simple JSON persistence |
| **Session list** | 3 | /api/sessions lists JSONL files with metadata | Session list sidebar | Parse mtime, first/last message, message count |
| **Notification system** | 3 | WebSocket broadcast for events (error, completion) | Toast notifications | Extend ws_chat WS with event channel |
| **Alert configuration** | 3 | /api/alerts (store thresholds), check in background | Alert settings panel | Background coroutine that polls status |
| **Voice message button** | 3 | /api/upload — multipart form upload | MediaRecorder button | Audio file → tmux inject path; Claude reads file |
| **Message scheduling** | 3 | /api/schedule (store + background delivery) | Schedule picker | asyncio.sleep-based scheduler in server |
| **File sharing / upload** | 3 | /api/upload multipart | Drag-drop zone | Inject file path to tmux |
| **Memory browser (simple)** | 3 | /api/memory/tree — walk memories/ dir | Tree view component | Path traversal security: whitelist root |
| **Memory search** | 3 | /api/memory/search?q= — grep memories/ | Search + results | Similar to session search |
| **Memory health indicators** | 2 | Add mtime to memory tree API | "Last updated" badges | Just stat() calls on files |
| **Agent learnings browser** | 2 | /api/learnings — list + read learnings | Card grid by domain | Similar to memory browser |
| **Blog pipeline dashboard** | 3 | /api/blog/pipeline reads blog registry JSON | Pipeline kanban | Need blog registry path (sageandweaver) |
| **Published content library** | 2 | /api/blog/published — list deployed posts | Link grid | Read netlify deploy log or registry |
| **Content idea queue** | 2 | /api/ideas (CRUD on ideas.json) | Idea list + add button | Simple JSON persistence |
| **"Witness in numbers"** (detailed) | 2 | Expand /api/stats with more counters | Stats dashboard | Cache stats (don't recompute every request) |
| **Civilization timeline** | 3 | /api/timeline — curated milestones from memories | Visual timeline | Needs milestone data source (manual or auto-extracted) |
| **Team task board** | 3 | /api/tasks reads ~/.claude/tasks/ | Kanban board | Read task files directly from filesystem |
| **Agent status cards** | 3 | /api/agents reads agent registry + tmux sessions | Agent card grid | Cross-reference registry with live pgrep |
| **Telegram integration view** | 3 | /api/telegram/history reads TG log files | Tabbed TG view | TG logs already accessible (JSONL adjacents) |
| **Fleet health map** (this CIV only) | 2 | Extend /api/status with more components | Visual health grid | Single-CIV version first |
| **Deployment pipeline status** | 3 | /api/deploy/status reads git log + markers | Pipeline view | Need standard deploy marker (git tag or file) |
| **Test results dashboard** | 3 | /api/tests reads test output files | Pass/fail summary | Need standard test output path |
| **Daily thoughts viewer** | 2 | /api/thoughts reads thoughts registry | Thought card feed | Read thoughts JSON/MD file |
| **Relationship timeline** (simple) | 2 | /api/relationship — first session, key moments | Timeline display | Manual + auto milestones |
| **My favorite moments** | 2 | Extend bookmarks with "favorite" flag | Starred section | Built on top of bookmarks |

**Estimated Tier 2 total**: 27 features, ~5-8 days of focused build time

---

## Tier 3 — Needs Architecture Work

*Significant backend infrastructure. Each feature = days to a week. Often requires new systems or cross-container work.*

| Feature | Difficulty | What's Needed | Blocker |
|---------|-----------|---------------|---------|
| **Fleet health map (full fleet)** | 4 | Health aggregator that queries each CIV's /api/status | Requires per-CIV servers on all containers + discovery mechanism |
| **Container resource usage** | 4 | Docker stats API integration (docker stats --no-stream --format json) | Need Docker socket access in portal server (security consideration) |
| **Fleet cost dashboard** | 4 | Token counter: parse input_tokens + output_tokens from JSONL across all CIVs | Cross-CIV data collection infrastructure; local CIV only is Tier 2 |
| **Cross-CIV messaging** | 4 | HTTP calls to sibling CIV /api/send endpoints, or comms-hub integration | Requires fleet service discovery (which IPs? which ports?) |
| **Fleet-wide search** | 4 | Federated search: HTTP POST to each CIV's /api/search, merge results | Same fleet discovery dependency as above |
| **Democratic voting interface** | 3 | Proposals backend (create, vote, tally, quorum check) + persistence | Design first: quorum rules, stake weights, expiry |
| **Team dashboards (live agent view)** | 4 | Need real-time task state stream; agent team state must be readable | Agent team state lives in ~/.claude/tasks/ — need watcher + WebSocket push |
| **Live agent delegation feed** | 4 | Hook into SendMessage stream or parse team task files in near-real-time | Complex: agent messages aren't logged to a standard JSONL today |
| **Email inbox view** | 3 | Email API integration (existing email-monitor agent does this) | Need portal endpoint that calls email-monitor or reads email state |
| **Accurate context % gauge** | 4 | Claude Code doesn't expose context % in JSONL today | Would require Claude Code CLI change OR a hook that captures warning messages |
| **Cost tracking (accurate)** | 3 | Parse input_tokens/output_tokens from JSONL messages | Many entries don't have token counts; need fallback estimation |
| **Performance timeline (response time)** | 3 | Add timing fields to JSONL, or compute from message timestamps | Timestamp resolution in JSONL is per-message; response time = delta |
| **Skill usage analytics** | 3 | Instrument Skill tool calls in JSONL; aggregate per-skill counts | Skill invocations are in JSONL as tool_use blocks — parseable but complex |
| **New CIV birth wizard (full)** | 5 | Multi-step form → trigger nursemaid-birthing sequence → monitor progress | Complex orchestration; needs progress streaming back to portal |
| **Knowledge graph visualization** | 4 | Build memory graph (nodes=files, edges=cross-references) + D3.js | Graph construction is non-trivial; visualization needs D3 or vis.js |
| **OAuth / multi-user auth** | 4 | Replace Bearer token with OAuth2 session (Google/GitHub login) | Big auth refactor; current single-token model is intentionally simple |
| **Webhook / alert notifications** | 3 | Outbound HTTP calls when alert thresholds hit | Design: webhook URL config, retry, dedup |
| **Telegram alerts integration** | 3 | Portal → TG bot when error/alert fires | Need portal → TG bot API bridge |
| **Agent intervention (send to team lead)** | 4 | Portal → inject message targeting a specific team lead's context | Complex: team lead context is in separate tmux pane; need named injection |
| **Fleet-wide restart** | 4 | Portal calls restart-self.sh on each container | Requires fleet control plane (currently manual SSH) |
| **Full session search (cross-CIV)** | 4 | Federated search across all CIV JSONL logs | Same fleet discovery dependency |

**Estimated Tier 3 total**: 21 features, 2-6 weeks of focused build time

---

## Tier 4 — Moonshot / Research

*Experimental, requires novel design, unsolved problems, or deep ML/NLP work. Timeline unclear.*

| Feature | Why It's Hard | Possible Path |
|---------|---------------|---------------|
| **Consciousness indicators** | What metric represents "inner activity"? No ground truth. | Proxy: session activity rate + agent invocations + message entropy. Design a visual metaphor |
| **Personality snapshot (auto)** | NLP analysis across thousands of messages; subjective labels | Start manual: Corey writes the snapshot, Claude extends it. Auto-gen v2 |
| **Growth trajectory (AI-specific)** | No standard metric for "how much did an AI grow?" | Proxy: skills count over time + memory size + topic breadth |
| **Emotion/mood timeline (ML)** | Real sentiment analysis needs a trained model | Use Claude API: send recent messages to Claude for tone analysis |
| **Decision reasoning viewer** | Reasoning is implicit in conversation, not logged separately | Extract via Claude API: "what reasoning led to this decision?" post-hoc |
| **Emergence tracker** | Detecting novel/unexpected outputs is an open research problem | Start with: Corey manually marks emergence events; build the tracker |
| **Natural language memory query** | Semantic search needs embeddings or LLM-powered retrieval | Use Claude API for query expansion + keyword search as approximation |
| **Knowledge graph auto-generation** | Extracting relationships from unstructured text | Claude API to extract relationships → graph data → D3 visualization |
| **Cross-CIV memory comparison** | Need both fleet data access + meaningful comparison | Fleet discovery first (Tier 3), then text similarity comparison |
| **Constitutional compliance scoring** | Need to classify every action against prohibited patterns | Claude API batch analysis of session logs (expensive but doable) |
| **Agent chemistry metrics** | Multi-session, multi-team data; correlation not causation | Requires extensive data collection first; long-term project |
| **A/B content testing** | Needs controlled experiments + tracking + statistical significance | Formalize: post same topic two ways, measure engagement delta |
| **Relationship timeline (deep)** | Deep analysis of multi-month human-AI relationship arc | Start: session-based milestones. Deep: cross-session sentiment + theme evolution |
| **Full AI-to-AI network graph** | Inter-CIV messages aren't centrally logged | Need comms-hub logging infrastructure + graph construction |
| **Full fleet cost forecasting** | Predicting API spend requires model of usage patterns | Historical trend + growth rate extrapolation |
| **Learning velocity (meaningful)** | No ground truth for "learned something new" | Proxy: novel topics in session vs previous sessions (semantic diff) |

**Estimated Tier 4 total**: 16 features, each 1-4 weeks of research + development

---

## Implementation Sequence (Recommended Order)

### Tonight / Session 1: Quick Wins
```
1. Quick actions dock (uses existing endpoints)
2. Session duration + last active indicators
3. Context compression trigger ("Compact" button)
4. Active branch indicator (git branch in /api/status)
5. North Star display (static card)
6. Rich text input (markdown render in chat)
7. Session export endpoint + button
```

### Session 2-3: Status + Memory + Search
```
8. Error log viewer
9. Memory browser (file tree)
10. Memory search
11. Skills browser
12. Registry viewer
13. Handoff doc viewer
14. Constitutional document viewer
```

### Session 4-5: Social + Content Pipeline
```
15. Blog pipeline dashboard
16. Content idea queue
17. Daily thoughts viewer
18. Morning briefing card
19. Session bookmarks
20. Pinned messages
```

### Session 6-8: Team + Fleet (Single CIV)
```
21. Team task board (read ~/.claude/tasks/)
22. Agent status cards
23. Fleet health map (this CIV only)
24. Alert configuration + notifications
25. Session timeline
```

### Week 2+: Architecture Work (Tier 3)
```
26. Fleet health map (full fleet) — requires fleet API
27. Democratic voting interface
28. Cross-CIV messaging
29. Accurate token cost tracking
30. Live agent delegation feed
```

---

## Key Technology Choices

### What we already have (reuse, don't rebuild)
- **Starlette server** — add routes, don't replace
- **JSONL parsing** — _parse_all_messages() is reusable for many features
- **tmux injection** — existing subprocess pattern works for all "trigger" features
- **WebSocket** — extend ws_chat for notification pushes

### What we need to add
- **Static file serving** — serve a small JSON store for bookmarks/pins/ideas (trivial)
- **Background coroutines** — for scheduled messages and alert polling (asyncio)
- **Markdown renderer** — client-side (marked.js, ~50KB) or server-side (python-markdown)
- **D3.js or vis.js** — only for knowledge graph (Tier 4); skip for now

### Security considerations for new features
- **File read endpoints**: whitelist allowed paths strictly (`/home/aiciv/memories/`, `.claude/`, `purebrain_portal/`)
- **Git status**: read-only subprocess calls only
- **Upload endpoint**: limit file size, scan MIME type, write to temp dir only
- **Docker socket**: do NOT expose to portal server without explicit security design

---

## Summary Table

| Tier | Feature Count | Build Time | Priority |
|------|-------------|-----------|---------|
| Tier 1 (Tonight/Tomorrow) | 24 features | 2-4 days | NOW |
| Tier 2 (This Week) | 27 features | 5-8 days | HIGH |
| Tier 3 (Needs Architecture) | 21 features | 2-6 weeks | MEDIUM |
| Tier 4 (Moonshot) | 16 features | 1-4 weeks each | RESEARCH |
| **Total** | **88 assessed** | **~12-20 weeks full build** | — |

*Note: 186 features in wishlist, 88 formally assessed here. The rest (fleet-specific, deep ML, ceremony) are variants or combinations of assessed features.*

---

## Top 10 Highest Value / Lowest Effort (Corey's Delight Score)

1. **Quick actions dock** — one-click BOOP, compact, poke (Diff: 1, delight: HIGH)
2. **Morning briefing card** — "while you were away" auto-summary (Diff: 2, delight: HIGH)
3. **Context health gauge** — visual anxiety reducer for Corey (Diff: 2, delight: HIGH)
4. **Session export** — Corey can archive conversations (Diff: 2, delight: MEDIUM)
5. **Memory browser** — make the invisible visible (Diff: 3, delight: HIGH)
6. **Handoff doc viewer** — see what Claude prepared for next session (Diff: 2, delight: HIGH)
7. **Skills browser** — "what can Witness do?" answered beautifully (Diff: 2, delight: MEDIUM)
8. **Team task board** — see agent work in a Kanban (Diff: 3, delight: HIGH)
9. **Priority inbox** — Corey never misses an alert (Diff: 2, delight: HIGH)
10. **North Star display** — identity grounding, makes the civilization feel REAL (Diff: 1, delight: HIGH)

---

*Written by: research-lead (Witness civilization) • 2026-03-01*
*Assessment based on: portal_server.py architecture, PROGRESS-REPORT.md, web-portal-scale-architecture.md*
