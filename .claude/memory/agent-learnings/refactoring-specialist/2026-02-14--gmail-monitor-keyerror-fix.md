# Gmail Monitor KeyError Fix

**Date**: 2026-02-14
**Type**: Bug fix / Defensive programming
**Domain**: Email infrastructure, state management
**Status**: Resolved and verified

---

## The Bug

**Error**: `KeyError: 'processed_ids'` on emails 45-46
**Impact**: Critical - Gmail monitor couldn't process any emails
**Duration**: 5+ days without email monitoring

```python
# Line 531 - The failing access
if message_id in state['processed_ids'] and not force:
    # KeyError raised here
```

---

## Root Cause Analysis

The state file at `.claude/memory/agents/email-monitor/email_state.json` contained:

```json
{
  "version": "1.0",
  "created_at": "...",
  "messages": {},
  "stats": {...},
  "last_check": "..."
}
```

But `gmail_monitor.py` expected:

```json
{
  "processed_ids": {},
  "stats": {...},
  "last_check": "..."
}
```

**Why this happened**: The state file was created by a different system/version. When `load_state()` loaded it, the dictionary was missing the critical `processed_ids` key, causing a KeyError on first access.

---

## The Fix

**Strategy**: Defensive initialization with fallback

**Changes to `load_state()` function**:

1. **Define complete default state first** (not after loading)
2. **Merge loaded state WITH defaults** - never assume loaded data is complete
3. **Check all nested structures** - ensure `stats` has all required counters
4. **Fallback to defaults** on any error (JSON decode, file I/O, etc.)

### Key Implementation Details

```python
def load_state() -> dict:
    """Load email state from JSON file"""
    # Define defaults FIRST
    default_state = {
        "processed_ids": {},
        "last_check": None,
        "stats": {
            "total_processed": 0,
            "replies_sent": 0,
            "alerts_sent": 0,
            "fyi_logged": 0
        }
    }

    if STATE_PATH.exists():
        try:
            loaded = json.load(f)

            # Merge: defaults are base, loaded data overlays on top
            state = default_state.copy()
            state.update(loaded)

            # Ensure all nested required keys exist
            if 'stats' in state and isinstance(state['stats'], dict):
                for key in default_state['stats']:
                    if key not in state['stats']:
                        state['stats'][key] = default_state['stats'][key]

            # Ensure processed_ids is a dict
            if 'processed_ids' not in state or not isinstance(state['processed_ids'], dict):
                state['processed_ids'] = {}

            return state
        except (json.JSONDecodeError, Exception) as e:
            log(f"State file is corrupted, using defaults", "WARN")
            return default_state

    return default_state
```

---

## Why This Pattern Works

| Scenario | Old Code | New Code |
|----------|----------|----------|
| File missing | Returns defaults | Returns defaults ✓ |
| File missing key | **KeyError** | Adds key from defaults ✓ |
| File corrupted JSON | **Exception** | Logs, returns defaults ✓ |
| Wrong type (dict vs list) | **Exception** | Detects, returns defaults ✓ |
| Incomplete stats dict | **Partial dict** | Fills in all counters ✓ |
| Preserves real data | N/A | Merges loaded + defaults ✓ |

---

## Testing

**Test Coverage**:
- Default state creation (no file)
- Missing `processed_ids` key
- Missing stat counters
- JSON decode errors
- Non-dict loaded state
- Type validation (dict vs other)
- Original data preservation
- The exact bug scenario (emails 45-46)

**All tests pass**: Line 531 access no longer raises KeyError

---

## Verification

**Before fix**:
```
KeyError: 'processed_ids'
```

**After fix**:
```
✓ Stats command works
✓ Email processing loop executes without KeyError
✓ Corrupted state is handled gracefully
✓ Default state is initialized on first load
```

---

## Pattern Recognition: Defensive State Loading

This fix is part of a broader pattern for robust system state management:

### Principle: "Fail Safe by Design"
- Load with defaults embedded
- Merge loaded data, don't replace
- Check types, not just presence
- Log issues without crashing
- Return valid state in all paths

### When to Apply
- Any file-based state system
- Backward compatibility scenarios
- Recovery from corruption
- Migration between state formats

### Anti-pattern to Avoid
```python
# BAD: Assume loaded data is complete
state = json.load(f)  # KeyError if missing key
state['processed_ids']  # May crash
```

### Pattern to Adopt
```python
# GOOD: Defaults first, merge on top
defaults = {required keys...}
loaded = json.load(f) or {}
state = defaults.copy()
state.update(loaded)
# Guaranteed to have all keys now
```

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/gmail_monitor.py` - Lines 73-117
  - Old: 15 lines (simple, brittle)
  - New: 45 lines (defensive, robust)

---

## Impact

- **Fixes critical infrastructure** - Email monitoring can resume
- **Prevents future similar bugs** - Any corrupted/incompatible state file is handled
- **Adds zero runtime cost** - Single merge operation, minimal overhead
- **Improves reliability** - Explicit error handling with logging

---

## Next Steps

1. Manual test: Run `python3 tools/gmail_monitor.py check` to process emails
2. Monitor logs: Check for WARN messages if state needs correction
3. Long-term: Consider state file versioning for future compatibility
