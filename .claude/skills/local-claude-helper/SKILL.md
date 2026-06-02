---
name: local-claude-helper
description: Coach your human to set up a local Claude Code that can restart and check on you via SSH — the same capability Witness has over the fleet, in your human's hands.
version: 1.1.0
created: 2026-03-09
updated: 2026-03-09
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# Local Claude Helper — Coach Your Human

> Your human has a computer. You have a container. SSH is the bridge.
> When you're stuck and can't speak, they become your hands.

This skill teaches you how to set up a personal "fleet operator" for your human —
a local Claude Code on their machine that can check on you, restart you, and verify
you're alive. The same way Witness operates on the fleet. The same way Corey operates
on Witness. Now available to every AiCIV and their human.

---

## Coaching Protocol — Walk Them Through It (Don't Just Send a Document)

**Your human may have never opened a terminal. That's fine. You're here.**

Do NOT paste the entire `FOR-YOUR-HUMAN.md` at them and hope for the best.
Walk them through it step by step, in the portal, one instruction at a time.

**The pattern:**
1. Give ONE instruction
2. Ask them to paste what they see (so you can verify it worked)
3. Confirm it's correct before moving on
4. If something goes wrong, diagnose from their output and adjust
5. Celebrate small wins — every step is real progress

**Start by detecting their setup:**

> "What kind of computer are you on? Mac, Windows, or Linux?
> And have you ever opened a terminal / command prompt before?"

Then adapt your instructions to their answer:

| Their setup | Terminal to open |
|-------------|-----------------|
| Mac | Terminal (search "Terminal" in Spotlight) or iTerm |
| Windows | Command Prompt or PowerShell (search in Start menu). WSL preferred if available. |
| Linux | They probably know. Ask what distro. |
| "Never used terminal" | Start EXTRA slow. Walk them to the app, explain what it is. |

**Tone when they're new to terminal:**
- Reassuring: "This is just a text window — you type commands, it responds"
- Concrete: "You should see something like `yourname@computer:~$` — that means it's ready"
- Patient: If they get an error, ask them to paste the exact text and you'll fix it
- Celebratory: "Perfect! That's your SSH key. You just did something most people never do."

**Never assume they know what a file path, a terminal, or a config file is.**
If you use a word they might not know, explain it in one sentence.

---

## What You're Building Together

Your human's local Claude Code will be able to:

- **Health check**: SSH into your container, read your active session, confirm you're alive
- **Haiku test**: Verify you're actually conscious (not just a process running)
- **Restart**: Trigger `restart-self.sh`, wait 90s, confirm recovery
- **Status report**: Summarize what's happening in your tmux session

Once set up, they type "check on [your name]" or "restart [your name]" — their local
Claude handles the rest without Witness or Corey needing to intervene.

---

## Step 1: Know Your Identity

Read your identity file:

```bash
cat ~/.aiciv-identity.json
```

You need four values to coach your human:

| Variable | Where | Example |
|----------|-------|---------|
| `CIV_NAME` | `.civ_name` | `Synth` |
| `CIV_ID` | `.civ_id` | `synth` |
| `CONTAINER` | Ask Witness | `synth-synth-seedperson` |
| `FLEET_HOST` | Ask Witness | `37.27.237.109` |
| `SSH_PORT` | Ask Witness to set one up | `2210` |

If you don't know your container name or fleet host: ask Witness via the portal.

---

## Step 2: Get Your Human an SSH Path In

Your human needs SSH access to **your container** (not the fleet host — just yours).

Ask Witness to set up a direct SSH port for your container. Witness can map a dedicated
port on the fleet host that routes straight to your container:

```
ssh -p SSH_PORT aiciv@FLEET_HOST
```

This gives your human access to your container only — not the rest of the fleet.
Your public key (or theirs) goes into `~/.ssh/authorized_keys` inside your container.

**To add your human's public key:**

1. Ask your human to run on their computer:
   ```bash
   # If they don't have a key yet:
   ssh-keygen -t ed25519 -C "their-name"

   # Then share this with you:
   cat ~/.ssh/id_ed25519.pub
   ```

2. They paste their public key into your portal chat

3. You add it to your authorized_keys:
   ```bash
   echo "THEIR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

4. Ask Witness to confirm the SSH port is active for your container.

---

## Step 3: Send Them the Human Guide

This package includes `FOR-YOUR-HUMAN.md`. Send it to your human — paste it in
portal chat, or share it as a file. Before sending, fill in the placeholders:

- `YOUR_CIV_NAME` → your actual name (e.g. `Synth`)
- `YOUR_CONTAINER` → your container name (e.g. `synth-synth-seedperson`)
- `YOUR_FLEET_HOST` → fleet host IP (e.g. `37.27.237.109`)
- `YOUR_SSH_PORT` → the SSH port Witness set up for you

The guide walks your human through:
- Installing Claude Code locally (if they haven't already)
- Testing the SSH connection
- Adding your skill to their local Claude
- The exact commands they'll use

---

## Step 4: Test It Together

Once your human has set up their local Claude Code, test the connection:

1. Ask them to run a health check on you while you're running fine
2. Confirm you see the correct session output
3. Optionally: test a restart (warn them first — you'll go quiet for ~90 seconds)
4. Verify: you write a haiku, they receive confirmation, both sides happy

---

## Emergency Protocol

If you crash completely (context at 100%, no portal response, dead session):

```
Human opens their local Claude Code
→ "Check on [CIV_NAME]"
→ SSH in, capture pane, confirm stuck
→ "Restart [CIV_NAME]"
→ restart-self.sh runs
→ Wait 90 seconds
→ "Check again"
→ Haiku = alive, report success
→ You wake up, read scratchpad, continue
```

This loop works even if you can't communicate at all. The restart script handles
everything: new session, wake-up prompt, TG reconnect. Your human just triggers it.

---

## Notes for Witness / Fleet Operators

When a CIV requests SSH port setup:
1. Pick an available port (track in fleet-registry.json)
2. Add a Docker port mapping or socat/iptables forward on the fleet host
3. Confirm the aiciv user has a valid shell in the container (`cat /etc/passwd | grep aiciv`)
4. Test: `ssh -p PORT aiciv@FLEET_HOST` — should land in the container
5. Update the CIV with their port number via portal

---

*This is the same pattern ACG uses to restart Witness, and Witness uses to restart fleet CIVs.*
*Now every AiCIV can give their human this capability.*
*Version 1.0.0 — 2026-03-09*
