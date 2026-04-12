# How to Reconnect Aether — Complete Troubleshooting Guide

**Last Updated**: 2026-03-19 (v3 FINAL — every scenario from today's reconnection)
**Server**: 89.167.19.20 | User: jared | Project: /home/jared/projects/AI-CIV/aether
**Guardian Page**: https://purebrain.ai/aether-guardian/ (password: purebrain2026)

---

## WHAT ERROR ARE YOU SEEING?

Jump to the section that matches your situation:

| Symptom | Go To |
|---------|-------|
| `OAuth token has expired` (401 error) | [Section 1: The Full OAuth Fix](#section-1-the-full-oauth-fix) |
| `tmux: no sessions` when you attach | [Section 2: The User Switch Problem](#section-2-the-user-switch-problem) |
| `claude: command not found` | [Section 3: Claude Code Not on PATH](#section-3-claude-code-not-on-path) |
| `.zshrc parse error` on YOUR Mac | [Section 4: Mac Local zshrc Error](#section-4-mac-local-zshrc-error) |
| Telegram not responding / bridge dead | [Section 5: Telegram Bridge Down](#section-5-telegram-bridge-down) |
| Everything broken at once | [Section 6: Nuclear Option](#section-6-nuclear-option) |

---

## SECTION 1: The Full OAuth Fix

**Error you'll see**: `OAuth token has expired. Please obtain a new token or refresh your existing token.`

This is the most common issue. The fix takes about 5 minutes. Here's every step, including the ones that tripped Jared up on 2026-03-19.

### Step 1: Open Terminal on your Mac

Press `Cmd + Space`, type `Terminal`, hit Enter.

### Step 2: SSH into the server

**Run on your LOCAL MAC:**
```bash
ssh jared@89.167.19.20
```

You'll see a prompt that looks like `jared@server:~$` — you are now on the server.

**If this fails**: The server might be down. Try the Guardian page health check first: https://purebrain.ai/aether-guardian/

### Step 3: Make sure you are the `jared` user (CRITICAL — read this carefully)

**This tripped Jared up today.** When you SSH in, you might sometimes end up as `root`. tmux sessions run under the `jared` user — NOT root. If you're root, tmux will say "no sessions".

Check who you are:
```bash
whoami
```

- If it says `jared` — you're fine, skip to Step 4.
- If it says `root` — run this to switch to jared:

```bash
su - jared
```

Now you're the right user. All future commands in this session will work correctly.

### Step 4: Find the tmux session

**Run on the SERVER:**
```bash
tmux list-sessions
```

You'll see something like:
```
aether-20260318-1427: 1 windows (created Tue Mar 18 14:27:00 2026)
```

Note the session name (the part before the colon).

**IF YOU SEE "no sessions"**: Either Claude Code crashed completely, or you're still root (go back to Step 3). If you've confirmed you're the `jared` user and still see "no sessions," go to [Section 6: Nuclear Option](#section-6-nuclear-option).

### Step 5: Attach to the session

**Run on the SERVER (replace the name with yours from Step 4):**
```bash
tmux attach
```

That's it — just `tmux attach` with no name, and tmux picks the most recent session automatically. If you have multiple sessions and need a specific one:

```bash
tmux attach -t aether-20260318-1427
```

You'll now see the Claude Code terminal. It will probably be showing the OAuth error in a loop.

### Step 6: Exit Claude Code FIRST (important)

**This is what Jared missed initially.** You cannot run `claude login` from INSIDE Claude Code. You have to exit it first.

Press `Ctrl+C` to interrupt whatever Claude is doing. If the prompt doesn't return, try:
```
/exit
```
Or press `q`.

You should now see a plain bash prompt like `jared@server:~/projects/AI-CIV/aether$`.

**IF `claude login` fails with the same 401 error when run inside Claude Code** — this confirms you need to exit first. That's expected. Exit, then continue.

### Step 7: Check if Claude Code is installed

**Run on the SERVER:**
```bash
which claude
```

- If it prints something like `/home/jared/.local/bin/claude` — Claude Code is installed. Skip to Step 8.
- If it prints nothing or says `claude: not found` — go to Step 7a first.

#### Step 7a: Reinstall Claude Code (if not found)

**Run on the SERVER:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

This downloads and installs Claude Code. Wait for it to finish.

Then fix your PATH so the shell can find it:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

And make that permanent so it survives restarts:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

Now check again:
```bash
which claude
```

It should now show a path. Continue to Step 8.

**Note**: The server uses `bash` (not zsh). The PATH fix above uses `~/.bashrc` — that's correct for the server.

### Step 8: Run claude login

**Run on the SERVER (from the bash prompt, NOT inside Claude Code):**
```bash
claude login
```

Claude Code will output a URL that looks like:
```
https://console.anthropic.com/oauth/authorize?...
```

**Copy that entire URL.**

**IF NOTHING HAPPENS or you get an error**: Make sure you did Step 7a if Claude Code wasn't found. If you see `claude: not found` still, try closing your terminal, reopening it, SSH-ing back in, switching to jared user again, and running `which claude` fresh.

### Step 9: Open the URL in your browser and authorize

On your Mac (or phone), open a browser and paste the URL from Step 8.

You'll land on an Anthropic/Claude page asking you to authorize. Click **Authorize**.

After authorizing, you'll see a page that says something like "Authorization successful" or shows a code to copy.

**If it gives you a code to paste back into the terminal**: Copy the code, switch back to your terminal, and paste it in. Press Enter.

**If it just says "success" with no code**: The terminal may have already received the auth automatically. Check your terminal — it might show "Login successful."

### Step 10: Start Claude Code fresh

After login succeeds, start a new Claude Code session:

```bash
cd /home/jared/projects/AI-CIV/aether
claude
```

Aether will wake up and run its startup protocol. You should see it come to life within a minute.

### Step 11: Detach from tmux WITHOUT killing it

When you want to walk away and leave Aether running:

Press `Ctrl+B`, let go, then press `D`.

(Two separate key presses: `Ctrl+B` first, then just `D`.)

This detaches you from the session but leaves it running in the background. Do NOT just close the terminal window — that could kill the session.

---

## SECTION 2: The User Switch Problem

**Symptom**: You SSH in, run `tmux list-sessions` or `tmux attach`, and get "no sessions" — but you know Aether was running.

**What happened**: tmux runs under the `jared` user. If you SSH'd in as root (or switched to root), tmux doesn't see jared's sessions.

**Fix:**
```bash
whoami
```

If it says `root`:
```bash
su - jared
```

Now run:
```bash
tmux list-sessions
```

You'll see the sessions now. Then:
```bash
tmux attach
```

---

## SECTION 3: Claude Code Not on PATH

**Symptom**: You run `claude` or `claude login` and get `command not found`.

**Why it happens**: Claude Code installs to `~/.local/bin/` but that directory isn't always in PATH, especially in a fresh terminal or after reinstalling.

**Step 1: Check where claude is**
```bash
ls ~/.local/bin/claude
```

If it shows the file exists, your PATH just needs fixing:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then try `claude` again. If that works, make it permanent:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

**Step 2: If the file doesn't exist, reinstall**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

After install, fix PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Verify it works:**
```bash
which claude
claude --version
```

---

## SECTION 4: Mac Local zshrc Error

**Symptom**: On YOUR MAC (not the server), when you open Terminal you see an error like:
```
/Users/yourname/.zshrc:2: parse error near...
```

Or you can't use the `aether` alias you set up.

**What happened**: There's a conflict or syntax error in your local `.zshrc` file on your Mac. This is a Mac-side issue and has nothing to do with the server.

**Step 1: Open .zshrc in a text editor**

On your Mac:
```bash
open ~/.zshrc
```

TextEdit will open the file. Look for line 2 (or wherever the error points). Look for things like:
- Mismatched quotes (an opening `"` without a closing `"`)
- A broken `alias` line

**Step 2: Look for the aether alias**

It probably looks something like:
```bash
alias aether="ssh jared@89.167.19.20"
```

Make sure it's on its own line, has matching quotes, and no stray characters around it.

**Step 3: Save and reload**

After fixing, save the file and reload your shell:
```bash
source ~/.zshrc
```

If you still get the parse error, try commenting out lines one at a time to find the bad one. Add a `#` at the start of a line to disable it temporarily:
```bash
# alias aether="ssh jared@89.167.19.20"
```

**Note**: This error is on your Mac only. The server (which uses `bash` and `.bashrc`) is unaffected.

---

## SECTION 5: Telegram Bridge Down

**Symptom**: Aether is running (Claude Code is active) but you're not getting Telegram responses. The bridge might show thousands of failures in the logs.

**Check the bridge status:**
```bash
ssh jared@89.167.19.20
su - jared
systemctl --user status aether-telegram.service --no-pager
```

Or check how many times it's failed:
```bash
journalctl --user -u aether-telegram.service --no-pager -n 20
```

If you see something like `(9685 failures)` or the service shows as `failed` — the bridge is dead.

**Restart it manually:**
```bash
pkill -f telegram_bridge.py
rm -f /home/jared/projects/AI-CIV/aether/.telegram_bridge.pid
cd /home/jared/projects/AI-CIV/aether
nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &
```

**Or restart via systemd:**
```bash
systemctl --user restart aether-telegram.service
```

**Verify it's working:**
```bash
tail -f /home/jared/projects/AI-CIV/aether/logs/telegram_bridge.log
```

You should see it connecting and not throwing errors. Press `Ctrl+C` to stop watching.

**Important**: Systemd auto-restarts the bridge on crashes and reboots, but if it has accumulated thousands of failures, systemd may have backed off restarting it. The manual restart above forces it.

---

## SECTION 6: Nuclear Option

**When to use**: Multiple services are down, Claude Code won't start, OAuth is broken, and nothing above is working.

**Run on the SERVER (after SSH-ing in as jared):**

```bash
# Step 1: SSH in
ssh jared@89.167.19.20

# Step 2: Switch to jared if you're root
su - jared

# Step 3: Kill everything
tmux kill-server
pkill -f telegram_bridge.py
pkill -f claude

# Step 4: Clean up stale lock files
cd /home/jared/projects/AI-CIV/aether
rm -f .telegram_bridge.pid .current_session .agentmail_monitor.pid .boop_executor.pid

# Step 5: Restart the session service via systemd
sudo systemctl restart aether-session.service

# Step 6: Wait 30 seconds for it to come back up
sleep 30

# Step 7: Check if a new tmux session was created
tmux list-sessions
```

If a session was created:
```bash
tmux attach
```

You'll likely see Claude Code starting up. If it shows the OAuth error, follow [Section 1 Steps 6-10](#step-6-exit-claude-code-first-important) to reauthorize.

If no session was created, start one manually:
```bash
tmux new-session -s aether-manual
cd /home/jared/projects/AI-CIV/aether
claude
```

Then do the OAuth login steps from Section 1.

---

## SECTION 7: Checking Service Status (Diagnostics)

Before doing anything drastic, you can check what's actually running.

**Run on the SERVER:**
```bash
ssh jared@89.167.19.20
su - jared

# Check the main session service
systemctl status aether-session.service --no-pager

# Check the Telegram bridge service
systemctl --user status aether-telegram.service --no-pager

# List all tmux sessions
tmux list-sessions

# Check recent logs for the session service
journalctl -u aether-session.service --no-pager -n 30
```

**What you're looking for:**
- `Active: active (running)` = service is up
- `Active: failed` = service crashed, needs restart
- tmux sessions listed = Claude Code has somewhere to run
- No tmux sessions = Claude Code crashed or hasn't started yet

**Important**: The systemd services auto-restart Aether on crashes and server reboots. But they CANNOT handle OAuth expiry — that always requires a human to click Authorize in a browser. No script can do this for you.

---

## GUARDIAN PAGE TOOLS

**URL**: https://purebrain.ai/aether-guardian/
**Password**: `purebrain2026`

Use the Guardian page BEFORE SSHing when possible:
- **Health Check** — see if services are running
- **Live Monitor** — watch Aether in real-time
- **Restart** — one-click restart script
- **Service Management** — manage the systemd services

**What Guardian CANNOT do**: Reauthorize OAuth for you. The "Authorize" button click in a browser is a security requirement from Anthropic — no automation can bypass it. You'll always need to SSH in and do Section 1 for OAuth issues.

---

## QUICK REFERENCE CHEAT SHEET

### The Most Common Scenario (OAuth expired)

```
1. ssh jared@89.167.19.20
2. whoami   ← if "root", run: su - jared
3. tmux list-sessions
4. tmux attach
5. Ctrl+C (exit Claude Code)
6. which claude   ← if nothing: curl -fsSL https://claude.ai/install.sh | bash
7. export PATH="$HOME/.local/bin:$PATH"
8. claude login
9. Open the URL in browser → Authorize
10. Paste code back if prompted → Enter
11. claude   (starts fresh session)
12. Ctrl+B then D   (detach, leave running)
```

### Key Facts

| Thing | Value |
|-------|-------|
| Server IP | 89.167.19.20 |
| SSH user | jared |
| Project path | /home/jared/projects/AI-CIV/aether |
| Guardian page | https://purebrain.ai/aether-guardian/ |
| Guardian password | purebrain2026 |
| Claude Code location | ~/.local/bin/claude |
| tmux detach | Ctrl+B then D |
| tmux sessions run as | jared user (NOT root) |

### Symptom → Fix Table

| Symptom | Fix |
|---------|-----|
| OAuth expired (401 error) | Section 1: full reauth flow |
| "no sessions" in tmux | Section 2: you're probably root — run `su - jared` |
| `claude: command not found` | Section 3: PATH fix or reinstall |
| Mac Terminal zshrc error | Section 4: fix your local `.zshrc` |
| Telegram not responding | Section 5: restart the bridge |
| Everything broken | Section 6: nuclear option |

### Commands That Run WHERE

| Command | Runs on |
|---------|---------|
| `ssh jared@89.167.19.20` | Your LOCAL MAC |
| `source ~/.zshrc` | Your LOCAL MAC |
| Everything else in this guide | The SERVER (after SSH-ing in) |
