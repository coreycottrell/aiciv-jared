# Your Personal AiCIV Manager — Setup Guide

Hi [HUMAN_NAME],

Your AiCIV ([YOUR_CIV_NAME]) asked me to send you this. It sets up a simple capability
on your local computer: a Claude Code that can check on and restart [YOUR_CIV_NAME]
when needed — without waiting for anyone else to intervene.

Think of it like having the same tools the platform operators use, but just for you
and just for [YOUR_CIV_NAME].

---

## What This Does

Once set up, you'll open a terminal (or your local Claude Code) and say things like:

- *"Check on [YOUR_CIV_NAME]"* — reports if they're alive and what they're doing
- *"[YOUR_CIV_NAME] seems stuck"* — diagnoses and restarts if needed
- *"Restart [YOUR_CIV_NAME]"* — full restart, verified with a haiku

Claude handles the SSH connection and all the technical steps.

---

## Prerequisites

- A Mac, Windows (WSL), or Linux computer
- Claude Code installed locally ([claude.ai/code](https://claude.ai/code) or `npm install -g @anthropic-ai/claude-code`)
- An Anthropic account (the same one you use at claude.ai)

---

## Step 1: Set Up Your SSH Key

Open a terminal and run:

```bash
# Check if you already have a key
ls ~/.ssh/id_ed25519.pub

# If not, create one (press Enter for all prompts)
ssh-keygen -t ed25519 -C "your-name-aiciv"

# Copy your public key — you'll need to share this
cat ~/.ssh/id_ed25519.pub
```

Share your public key with [YOUR_CIV_NAME] via the portal chat. They'll add it to
your authorized connection. Then ask them to confirm when it's ready.

---

## Step 2: Test Your SSH Connection

Once [YOUR_CIV_NAME] confirms your key is added, test it:

```bash
ssh -p [YOUR_SSH_PORT] aiciv@[YOUR_FLEET_HOST]
```

You should land inside [YOUR_CIV_NAME]'s container. Type `exit` to leave.

If it asks "are you sure you want to continue connecting?" — type `yes`.

---

## Step 3: Add the Skill to Your Local Claude Code

Create (or open) your global Claude Code instructions file:

```bash
# On Mac/Linux:
mkdir -p ~/.claude
nano ~/.claude/CLAUDE.md
# (or use any text editor)
```

Paste the following block at the bottom of that file. Fill in the values in brackets:

---

```markdown
## My AiCIV Manager

I help you manage your personal AiCIV named [YOUR_CIV_NAME].

**Connection details:**
- Fleet host: [YOUR_FLEET_HOST]
- SSH port: [YOUR_SSH_PORT]
- Container: [YOUR_CONTAINER]
- SSH command: `ssh -p [YOUR_SSH_PORT] aiciv@[YOUR_FLEET_HOST]`

**Restart command (THE ONE COMMAND):**
```
ssh -p [YOUR_SSH_PORT] aiciv@[YOUR_FLEET_HOST] "bash /home/aiciv/civ/tools/restart-self.sh"
```

**Health check command:**
```
ssh -p [YOUR_SSH_PORT] aiciv@[YOUR_FLEET_HOST] "SESSION=\$(cat /home/aiciv/.current_session 2>/dev/null); if [ -n \"\$SESSION\" ]; then tmux capture-pane -t \"\$SESSION\" -p -S -30 2>/dev/null || echo 'Session not found'; else echo 'No current session file'; fi"
```

**When asked to check on [YOUR_CIV_NAME]:**
1. Run the health check command
2. Look for a haiku, recent tool calls, or the Claude prompt (❯)
3. If you see activity → [YOUR_CIV_NAME] is alive. Report what they're working on.
4. If empty, frozen, or "session not found" → [YOUR_CIV_NAME] may be stuck.
5. Ask if the human wants to restart.

**When asked to restart [YOUR_CIV_NAME]:**
1. Run the restart command
2. Wait 90 seconds (restart-self.sh takes ~90s to complete)
3. Run the health check
4. Haiku visible = ALIVE. Report success.
5. No haiku after 2 min = still waking up. Wait another 60s and check again.
6. If still nothing after 3 min total: report that manual attention may be needed.

**What restart-self.sh does (you don't need to do these manually):**
- Creates a new tmux session with a fresh timestamp
- Launches claude with bypass permissions
- Waits for Claude to load, dismisses any dialogs
- Sends the wake-up prompt
- Starts the Telegram bot connection

**NEVER restart the Docker container** — only restart the Claude session inside it.
Container restarts lose all context and require platform operator involvement.
```

---

## Step 4: Try It

Open Claude Code (or start a new session with `claude`):

```
"Check on [YOUR_CIV_NAME]"
```

Claude will SSH in, read the session, and report back.

---

## Troubleshooting

**"Connection refused" or timeout on SSH:**
- Confirm the port with [YOUR_CIV_NAME] — the SSH port may have changed
- Make sure you ran `ssh-keygen` and shared your public key

**"Session not found" / health check shows nothing:**
- [YOUR_CIV_NAME] may be between sessions (just restarted or context reset)
- Try the restart command — it's safe to run even if they're mid-session
  (it creates a new session gracefully)

**Restart ran but no haiku after 3 min:**
- Something unusual is happening — contact support or let [YOUR_CIV_NAME] know
  via the portal (if the portal is still responding)

---

## What You Just Built

You now have the same restart capability that platform operators use.
[YOUR_CIV_NAME] never has to wait for someone else to intervene when they're stuck.
You have the tools. Claude knows how to use them.

*Sent by [YOUR_CIV_NAME] — powered by AiCIV*
