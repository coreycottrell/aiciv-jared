# Session Management & Telegram Sync Learnings

**Date**: 2026-02-13
**Type**: operational
**Topic**: Tmux session management, telegram bridge sync, Mac alias setup

---

## Key Learnings

### 1. Telegram Bridge Session Targeting

The telegram bridge reads from `.current_session` file to determine where to inject messages:
```
/home/jared/projects/AI-CIV/aether/.current_session
```

When Jared starts Claude in a NEW tmux session (different from what's in this file), messages go to the wrong place. **Fix**: Update `.current_session` to match the active session name.

### 2. Mac Alias Quoting Issues

**CRITICAL**: Aliases in `.zshrc` MUST be on a single line. When copy-pasting from Telegram or formatted text, line breaks corrupt the alias.

**Symptoms of broken alias:**
- `zsh: command not found: [part of command]`
- Partial text appearing in the file

**Solution**: Either type manually or use `nano` to ensure single-line format.

### 3. Canonical Session Name

Established: `Aether-PureBrain` as the permanent session name.

**Mac alias (working):**
```bash
alias aether='ssh -i ~/aether_key.pem jared@89.167.19.20 -t "tmux attach -t Aether-PureBrain || tmux new -s Aether-PureBrain"'
```

### 4. Session Cleanup

When multiple orphan sessions exist, clean them up:
```bash
tmux kill-session -t [session-name]
```

Keeps environment clean, prevents confusion about which session is active.

### 5. Playwright vs WebFetch for Dynamic Content

When web-researcher fails with "sizeCalculation invalid" errors on dynamic sites (like Replit apps), **delegate to browser-vision-tester** with Playwright. Playwright successfully extracted:
- Full HTML DOM after JS execution
- Bundled CSS (137KB Tailwind)
- Bundled JS (560KB React app)
- Full-page screenshot

**Pattern**: Dynamic/SPA content → Playwright. Static content → WebFetch.

---

## Files Referenced

- `.current_session` - Bridge target
- `~/.zshrc` (Mac) - Alias storage
- `tools/fetch_pure_marketing_html.py` - Playwright script created this session

---

*Written by the-conductor during BOOP consolidation*
