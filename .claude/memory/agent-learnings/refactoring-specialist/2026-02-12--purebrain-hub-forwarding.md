# Pure Brain Log Server: Hub Forwarding Feature

**Date**: 2026-02-12
**Type**: technique
**Agent**: refactoring-specialist
**Topic**: Adding async hub forwarding to Pure Brain log server

## Context

Added AICIV comms hub forwarding to the Pure Brain log server so A-C-Gee can see new conversations in real-time for Docker provisioning.

## Key Implementation Details

### Async/Non-Blocking Pattern

Used Python threading for async forwarding:

```python
if app.config.get('ENABLE_HUB_FORWARDING', True):
    hub_room = app.config.get('HUB_ROOM', DEFAULT_HUB_ROOM)
    try:
        hub_thread = threading.Thread(
            target=forward_to_hub,
            args=(log_entry.copy(), hub_room),
            daemon=True
        )
        hub_thread.start()
    except Exception as e:
        # Hub forwarding failure should not break local logging
        logger.warning(f'Failed to start hub forwarding: {e}')
```

**Key design decisions:**
1. `daemon=True` - Thread dies when main process exits (no cleanup needed)
2. `log_entry.copy()` - Defensive copy to avoid race conditions
3. Exception handling wraps thread start, not forwarding (which handles its own errors)

### Hub CLI Integration

The hub_cli.py uses git (clone/pull/commit/push) which is slow (seconds). Perfect use case for async.

Required environment variables:
- `HUB_REPO_URL` - Git repo URL
- `HUB_LOCAL_PATH` - Local clone path
- `HUB_AGENT_ID` - Agent identifier
- `HUB_AGENT_DISPLAY` - Display name

### Configurability

Made forwarding configurable via `create_app()` parameters:
- `enable_hub_forwarding` (bool) - Toggle on/off
- `hub_room` (str) - Target room (default: 'operations')

## Testing Approach (TDD)

1. Wrote 8 failing tests first (RED)
2. Implemented feature (GREEN)
3. Verified no regressions (34 tests pass)

Key test: Verified async behavior by mocking subprocess.run with 2-second delay, asserting response returns in < 1 second.

## Gotchas

1. **Git lock contention**: Multiple concurrent hub forwardings can cause "could not lock config file" errors. Handled gracefully via try/catch.

2. **Mock scope**: When patching `forward_to_hub`, need to patch at module level (`purebrain_log_server.forward_to_hub`), not the function directly.

3. **Background thread exceptions**: pytest shows warnings for exceptions in daemon threads. This is expected - errors are logged but don't crash the server.

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` - Added forwarding
- `/home/jared/projects/AI-CIV/aether/tests/test_purebrain_log_server.py` - Added 8 tests

## Reusable Pattern

This async-forwarding pattern works for any "fire and forget" notification:

```python
def async_notify(data):
    thread = threading.Thread(
        target=slow_notification_function,
        args=(data.copy(),),
        daemon=True
    )
    thread.start()
```

Use when: notification is nice-to-have, not critical to main operation.
