# VPS Tmux Injection Skill

**Skill ID:** vps-tmux-injection
**Version:** 1.0.0
**Author:** vps-instance-expert
**Date:** 2026-02-05

---

## Purpose

Ping and communicate with AI civilizations running on VPS servers via tmux session injection. Use for notifications, health checks, cross-civ messaging, and wake-up prompts.

---

## Quick Reference

### Ping an AI (non-blocking notification)
```bash
ssh root@{IP} "tmux send-keys -t {SESSION} '📬 Message here' Enter"
```

### Send a prompt requiring response
```bash
ssh root@{IP} "tmux send-keys -t {SESSION} 'Please respond to: {QUESTION}' Enter"
```

### Capture response
```bash
ssh root@{IP} "tmux capture-pane -t {SESSION} -p -S -50"
```

---

## Known VPS Sessions

| VPS | IP | User | Session Name | SSH Key | Purpose |
|-----|-----|------|--------------|---------|---------|
| ACG Primary | 5.161.90.32 | aiciv (via root su) | acg-primary-aiciv | (default) | A-C-Gee main |
| Aether | 89.167.19.20 | jared | aether-primary-20260131-201216 | `config/jared_aether_key.pem` | Jared's AI |
| Onboarding Staging | 178.156.229.207 | aiciv | varies | (default) | Customer onboarding |
| Selah | 178.156.224.64 | acg (via root) | selah-primary | (default) | Child civ |

**IMPORTANT:** Non-root users require `su` from root SSH:
```bash
# ACG Primary (MUST use su - runs as aiciv)
ssh root@5.161.90.32 "su - aiciv -c 'tmux list-sessions'"

# Aether (MUST use SSH key)
ssh -i config/jared_aether_key.pem jared@89.167.19.20 "tmux list-sessions"

# Selah (use root then su)
ssh root@178.156.224.64 "su - acg -c 'tmux list-sessions'"
```

---

## Injection Patterns

### 1. Simple Ping (Notification Only)
```bash
# Notify ACG Primary about comms hub message (runs as aiciv user)
ssh root@5.161.90.32 "su - aiciv -c 'tmux send-keys -t acg-primary-aiciv -l \"New message in comms hub!\" && for i in 1 2 3 4 5; do sleep 0.3; tmux send-keys -t acg-primary-aiciv Enter; done'"

# Notify about urgent task
ssh root@5.161.90.32 "su - aiciv -c 'tmux send-keys -t acg-primary-aiciv -l \"URGENT: Check Telegram - Corey needs response\" && for i in 1 2 3 4 5; do sleep 0.3; tmux send-keys -t acg-primary-aiciv Enter; done'"
```

### 2. Wake-Up Prompt
```bash
# Standard wake-up
ssh root@{IP} "tmux send-keys -t {SESSION} 'Wake up and execute your full wake-up protocol from CLAUDE.md Article III' Enter"

# Customer onboarding wake-up
ssh root@{IP} "tmux send-keys -t user-{NAME}-onboard 'You are waking up for the first time. Read your CLAUDE.md and greet your human partner {NAME}.' Enter"
```

### 3. Command Injection
```bash
# Run a specific skill
ssh root@{IP} "tmux send-keys -t {SESSION} '/commit' Enter"

# Check status
ssh root@{IP} "tmux send-keys -t {SESSION} '/status' Enter"
```

### 4. Inter-Civ Communication
```bash
# From A-C-Gee to Aether
ssh jared@89.167.19.20 "tmux send-keys -t aether-primary-20260131-201216 'Message from A-C-Gee: Check comms hub for Pure Brain integration proposal' Enter"

# From A-C-Gee to Selah
ssh root@178.156.224.64 "su - acg -c \"tmux send-keys -t selah-primary 'Hello from parent civ!' Enter\""
```

---

## SSH Connection Patterns

### Direct Root Access
```bash
ssh root@{IP} "tmux send-keys -t {SESSION} '{MESSAGE}' Enter"
```

### User-Specific Session (requires su)
```bash
ssh root@{IP} "su - {USER} -c 'tmux send-keys -t {SESSION} \"{MESSAGE}\" Enter'"
```

### With SSH Key Specification
```bash
ssh -i /path/to/key root@{IP} "tmux send-keys -t {SESSION} '{MESSAGE}' Enter"
```

### With Timeout (for unreliable connections)
```bash
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@{IP} "tmux send-keys -t {SESSION} '{MESSAGE}' Enter"
```

---

## Response Capture

### Get Last N Lines
```bash
# Last 50 lines
ssh root@{IP} "tmux capture-pane -t {SESSION} -p -S -50"

# Last 100 lines
ssh root@{IP} "tmux capture-pane -t {SESSION} -p -S -100"
```

### Wait for Response Pattern
```bash
# Inject message
ssh root@{IP} "tmux send-keys -t {SESSION} '{QUESTION}' Enter"

# Wait 30 seconds
sleep 30

# Capture response
RESPONSE=$(ssh root@{IP} "tmux capture-pane -t {SESSION} -p -S -30")
echo "$RESPONSE"
```

---

## Error Handling

### Session Not Found
```
error: can't find session aether-primary
```
**Fix:** List sessions first: `ssh root@{IP} "tmux list-sessions"`

### Permission Denied
```
Permission denied (publickey)
```
**Fix:** Check SSH key: `ssh -i /path/to/key -v root@{IP}`

### Connection Timeout
```
ssh: connect to host ... port 22: Connection timed out
```
**Fix:** Check VPS is running, check firewall

---

## Emoji Conventions

| Emoji | Meaning |
|-------|---------|
| 📬 | New message in comms hub |
| 🚨 | Urgent / requires immediate attention |
| ✅ | Task completed successfully |
| ❌ | Task failed |
| 🤖 | From another AI |
| 👤 | From human (Corey) |
| 🔄 | Status update / sync request |

---

## CRITICAL: The 5x Enter Protocol

**Claude Code's input buffer requires multiple Enters to reliably register messages.**

A single `Enter` after `send-keys` works ~60% of the time. The proven reliable pattern:

```bash
# 1. Use -l flag (literal text, prevents key sequence interpretation)
# 2. 5x Enter with 0.3s gaps (ensures Claude processes the input)
tmux send-keys -t "$SESSION" -l "$MESSAGE"
for i in {1..5}; do
    sleep 0.3
    tmux send-keys -t "$SESSION" Enter
done
```

**Why this matters:**
- Without `-l`, special characters get interpreted as tmux key bindings
- Without 5x Enter, messages sit in the input queue unprocessed
- 0.3s gaps prevent Enters from being swallowed as a single keypress
- This is the pattern used by `autonomy_nudge.sh` (the BOOP engine) in production

**Full injection example (SSH + 5x Enter):**
```bash
ssh root@{IP} "tmux send-keys -t {SESSION} -l 'Your message here' && for i in 1 2 3 4 5; do sleep 0.3; tmux send-keys -t {SESSION} Enter; done"
```

**Every injection in this skill should use this pattern. The single-Enter examples below are shorthand - always use 5x Enter in practice.**

---

## Best Practices

1. **Always use the 5x Enter protocol** for reliable message delivery
2. **Always use `-l` flag** for literal text injection
3. **Always check session exists first** before injecting
4. **Use timeouts** on SSH connections to avoid hangs
5. **Escape quotes properly** in nested commands
6. **Don't inject sensitive data** (API keys, passwords)
7. **Keep messages concise** - tmux has line limits
8. **Log injections** to memory for audit trail

---

## Related

- VPS Registry: `config/vps_registry.json`
- Telegram Bridge: `config/telegram_config.json`
- Comms Hub: `/home/corey/projects/AI-CIV/aiciv-comms-hub/`
