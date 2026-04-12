# Portal Thinking Stream — Build Record

**Date**: 2026-03-03
**Type**: Feature build
**Status**: Shipped

---

## What Was Built

Real-time thinking/reasoning stream in the PureBrain portal chatbox. Aether's internal reasoning (white dots — the `thinking` blocks in JSONL session files) now appear live in the portal UI as dimmed italic messages.

---

## Files Changed

- `/home/jared/purebrain_portal/portal_server.py`
- `/home/jared/purebrain_portal/portal-pb-styled.html`

---

## Backend Architecture (portal_server.py)

### New globals
```python
_chat_ws_clients: set = set()        # Active WebSocket connections
_sent_thinking_hashes: set = set()   # Dedup — prevents re-sending same block
```

### New async functions
- `_push_thinking_to_clients(text, ts)` — broadcasts a thinking message to all connected WS clients. Cleans dead connections automatically.
- `_thinking_monitor_loop()` — background asyncio task that tails the latest JSONL session file, extracts `thinking` blocks, deduplicates by SHA-256 hash, and pushes to all connected clients.
- `_startup()` — Starlette on_startup hook that initialises portal log IDs and spawns the monitor task.

### ws_chat changes
- Now registers websocket into `_chat_ws_clients` on connect.
- Deregisters via `finally: _chat_ws_clients.discard(websocket)` on disconnect.

### Filtering rules (same as Telegram bridge)
- Skip messages where any block is `tool_use` (bash/tool noise)
- Skip `isSidechain` entries (background agents)
- Only extract blocks where `type == "thinking"`
- Minimum length 10 chars
- SHA-256 dedup to prevent repeats

### Message format pushed to frontend
```json
{"role": "thinking", "text": "...", "timestamp": 1234567890, "id": "thinking-abc123def456"}
```

### Startup change
```python
app = Starlette(routes=routes, on_startup=[_startup])
```

---

## Frontend Architecture (portal-pb-styled.html)

### New CSS
```css
.msg.thinking .msg-bubble {
  color: var(--text-dim);
  font-style: italic;
  font-size: 0.75rem;
  background: rgba(42,147,193,0.04);
  border: 1px solid rgba(42,147,193,0.15);
  border-left: 2px solid rgba(42,147,193,0.3);
  opacity: 0.8;
}
.msg.thinking .msg-bubble::before { content: '💭  '; font-style: normal; }
.thinking-expand { color: var(--gold); cursor: pointer; font-size: 0.68rem; }
```

### addMessage changes
- `divClass` logic: `role === 'thinking'` maps to `'msg assistant thinking'`
- `senderName`: thinking shows as `'Aether (thinking)'`
- New `else if (role === 'thinking')` branch: uses `textContent` (not innerHTML/markdown) for safety; truncates at 300 chars with expand/collapse toggle (`Show full reasoning ▾` / `Collapse ▴`)

### ws_chat onmessage changes
- `if (msg.role === 'thinking')` detected before the normal `addMessage` call, routes to `addMessage(msg.text, 'thinking', ...)` with early return.

---

## Patterns Learned

1. **Shared client registry pattern**: `_chat_ws_clients: set` + register on accept + deregister in `finally` is the clean way to broadcast from background tasks to all portal WS clients.

2. **Background monitor as asyncio task**: Using `asyncio.create_task()` in an `on_startup` hook is the right Starlette pattern. Do NOT use `threading` — the WS send calls require the asyncio event loop.

3. **Tail-and-seek pattern**: Track `last_pos` per file. On file change or truncation, reset to 0. `f.seek(last_pos)` then read new bytes — same pattern as the Telegram bridge.

4. **JS textContent vs innerHTML for thinking**: Thinking content is raw text, not markdown. Using `textContent` prevents XSS and avoids markdown rendering noise in reasoning blocks.

5. **Expand/collapse UX**: For long thinking blocks, `bubble.textContent = truncated; bubble.appendChild(expandBtn)` — then on click toggle. Must re-append expandBtn after setting textContent because textContent wipes all children.

---

## Test Instructions

1. Refresh portal at purebrain.ai portal URL
2. Trigger any non-trivial Claude Code task (causes thinking blocks to appear in JSONL)
3. Watch for dimmed italic messages with blue left border and 💭 prefix appearing in real time
4. Long reasoning blocks show "Show full reasoning ▾" — click to expand
