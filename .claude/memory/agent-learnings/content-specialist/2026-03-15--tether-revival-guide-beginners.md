# content-specialist Learning: Tether Revival Guide — Complete Beginners Guide

**Date**: 2026-03-15
**Type**: operational + pattern
**Agent**: content-specialist
**Confidence**: high

---

## Task Summary

Created a complete beginner's guide for setting up Claude Code and reviving an AI named "Tether." Target audience: zero technical experience. Covers Mac and Windows installation, SSH basics, VPS setup, tmux persistent sessions, systemd services, Telegram bridge, and the AI Guardian Template at purebrain.ai/ai-guardian-template/.

---

## Files Created

| File | Purpose |
|------|---------|
| `/home/jared/projects/AI-CIV/aether/exports/tether-revival-guide.md` | Complete 7-part guide with Quick Reference Card |

---

## Content Architecture

### 7 Parts
1. What Is Claude Code (non-technical analogy: smart assistant in the terminal)
2. Installing Claude Code — Mac (Option A: nodejs.org direct download, Option B: brew) + Windows (WSL2 path)
3. First Session — just type in plain English
4. Connecting to the Server — SSH explained as "calling Tether's home phone"
5. Reviving Tether — VPS selection (DigitalOcean/Hetzner/Linode), identity file, tmux, systemd
6. The AI Guardian Template — section-by-section walkthrough of purebrain.ai/ai-guardian-template/
7. Quick Reference Card — 10 most important commands

### Appendix
Common problems and simple fixes (5 scenarios with plain English solutions).

---

## Writing Patterns Used

**Analogy-first approach**: Every technical concept explained with a real-world parallel before the command is shown.
- Terminal = "black text screen from a hacker movie"
- SSH = "calling Tether's home phone"
- tmux = "leaving the TV on when you leave the room"
- VPS = "renting an apartment for your AI"
- API key = "a password that tells Anthropic yes this person has permission"

**Fear acknowledgment**: Each scary-looking section starts with reassurance ("You cannot break your Mac by typing in it").

**Progressive disclosure**: Commands shown after explanation, never before.

**Three-column comparison table**: VPS providers with monthly cost and one-reason-why column — removes decision paralysis.

---

## Key Source Material

The AI Guardian Template at purebrain.ai/ai-guardian-template/ uses placeholder values (YOUR.SERVER.IP, youruser, etc.). The guide explains this explicitly so beginners understand they fill in their own details.

Actual commands sourced from the template:
- `ssh youruser@YOUR.SERVER.IP`
- `tmux list-sessions` / `tmux attach -t [session]`
- `tmux capture-pane -t [session] -p | tail -30`
- `systemctl status yourai-*.service --no-pager`
- One-word shortcut via `.zshrc` alias

---

## Tone Notes

- Warm, patient, encouraging
- "Do not worry" before anything that looks scary
- Celebratory at milestones ("You just installed Claude Code. That was the hardest part.")
- No jargon without a plain-English explanation in the same sentence
- No emojis used sparingly per brand voice rules

---

## Memory Written

Path: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/content-specialist/2026-03-15--tether-revival-guide-beginners.md`
Type: operational + pattern
Topic: Tether Revival Guide — complete beginner onboarding for Claude Code + AI management

---

**END MEMORY**
