# QA Learning: Neural Feed Welcome Sequence Automation

**Date**: 2026-02-21
**Agent**: qa-engineer
**Type**: operational
**Topic**: Email automation QA review - scheduling logic, state persistence, thread safety

---

## What Was Reviewed

`tools/neural_feed_welcome_sequence.py` (310 lines) + 3 integration lines in `tools/purebrain_log_server.py`

## Key Findings

### Passed (all critical paths)

1. **Scheduling logic**: `_emails_due()` correctly computes due emails. Boundary condition (now >= send_after, not >) is correct - emails fire on time not late.

2. **Duplicate prevention**: `emails_sent` list check in `_emails_due()` is reliable. Combined with `sequence_complete` flag, no email is ever sent twice to a subscriber.

3. **Atomic state writes**: tmp file + rename pattern is correct. File corruption on crash is not possible.

4. **Template ID mapping**: Brevo template IDs 1-7 map 1:1 to email numbers 1-7 as documented. Verified against docstring.

5. **Import order in purebrain_log_server.py**: `load_dotenv` at L39 runs BEFORE `from neural_feed_welcome_sequence import` at L43. BREVO_API_KEY is available at module-level config read time.

6. **Scheduler placement**: `start_welcome_sequence_scheduler()` is in `main()` (L983), NOT module-level. Correct.

7. **Idempotency**: Double-start guard checks `_scheduler_thread.is_alive()`. Safe.

8. **Graceful degradation**: Empty BREVO_API_KEY logs error and returns gracefully from both API functions.

9. **Telegram config key**: Uses `default_chat_id` (matches the known fix from 2026-02-18).

10. **Blacklist handling**: Defense-in-depth at both `run_one_cycle` and `_process_contact` levels.

### Low Risk Finding

**Two separate file locks for the same log file** (`EMAIL_LOG_FILE = logs/purebrain_emails.jsonl`):
- `purebrain_log_server._file_lock` (used by post-purchase email logger)
- `neural_feed_welcome_sequence._email_log_lock` (used by sequence email logger)

At low volume these rarely write simultaneously. JSONL appends are atomic at the OS level on Linux for small writes. Not a blocker - note for future refactor into shared log utility.

### Known Condition (Not a Bug)

3 existing subscribers from Feb 19 will receive retroactive Email 1 + Email 2 on first deploy (2 days elapsed). Flagged to human, acknowledged.

## Patterns for Future Reviews

- Always verify lock objects protect the SAME resource (cross-module file access is a common miss)
- Check `load_dotenv` ordering vs module-level env reads when integrating new modules
- Verify boundary condition: `>=` vs `>` in time comparisons matters for exact-day delivery
- Atomic write = tmp file + rename (not truncate-then-write which risks partial states)
