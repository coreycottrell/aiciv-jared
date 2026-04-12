# Bridge Session Pointer Must Match Tmux Session Name

**Date**: 2026-02-25
**Context**: Session 43 — Telegram bridge not injecting messages to correct session

## Problem
`.current_session` file contained a stale session name that didn't match the active tmux session. Bridge was sending messages to a non-existent session.

## Fix
```bash
echo "$(tmux display-message -p '#{session_name}')" > .current_session
```

## Rule
**Every session startup** must update `.current_session` to match the actual tmux session name. This is already in the wake-up protocol but easy to skip. If Telegram messages stop appearing in the terminal, this is the first thing to check.

## Quick Diagnostic
```bash
cat .current_session          # What bridge thinks the session is
tmux display-message -p '#{session_name}'  # What the actual session is
# These MUST match
```
