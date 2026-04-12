# Local Multi-Agent Launcher (Mac Desktop)

**Created**: 2026-02-09
**Purpose**: Spin up multiple independent Claude Code instances on Jared's Mac

---

## When to Use

- Parallel independent work on unrelated projects
- Separate contexts that shouldn't cross-pollinate
- Working locally on Mac (not VPS)
- Visual/design work that needs local file access

## When NOT to Use

- Coordinated multi-agent work → Use Aether's Task delegation instead
- Shared memory/context needed → Use Aether
- Orchestrated missions → Use Aether

---

## The Script: ~/start-agents.sh

```bash
#!/bin/bash
# Multi-Agent Launcher for Mac

# Agent 1: MAIN DEV - Pitch decks, slides, main work
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop && echo \"🎯 MAIN DEV AGENT\" && claude"
    set custom title of front window to "🎯 MAIN DEV"
end tell'

# Agent 2: RESEARCH - Market research, analysis
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop/research && echo \"🔍 RESEARCH AGENT\" && claude"
    set custom title of front window to "🔍 RESEARCH"
end tell'

# Agent 3: DESIGN - Visual identity, UI work
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop/design && echo \"🎨 DESIGN AGENT\" && claude"
    set custom title of front window to "🎨 DESIGN"
end tell'

# Agent 4: AETHER VPS - Remote AI agent
osascript -e 'tell application "Terminal"
    do script "ssh jared@89.167.19.20 && echo \"🌐 AETHER VPS\" && claude"
    set custom title of front window to "🌐 AETHER VPS"
end tell'

echo "All agents launched! Use CMD+\` to switch between windows."
```

---

## Setup Instructions

1. Create the script:
```bash
nano ~/start-agents.sh
# Paste the script above
```

2. Make it executable:
```bash
chmod +x ~/start-agents.sh
```

3. Create working directories:
```bash
mkdir -p ~/Desktop/research ~/Desktop/design
```

4. Run it:
```bash
~/start-agents.sh
```

---

## Customization

### Add More Agents
Add another `osascript` block with different:
- Working directory (`cd ~/path`)
- Title emoji and name
- Purpose description

### Agent Templates

| Agent Type | Directory | Purpose |
|------------|-----------|---------|
| 🎯 MAIN DEV | ~/Desktop | Primary work |
| 🔍 RESEARCH | ~/Desktop/research | Market research |
| 🎨 DESIGN | ~/Desktop/design | Visual work |
| 📝 CONTENT | ~/Desktop/content | Writing/copy |
| 🧪 TESTING | ~/projects/test | QA work |
| 🌐 REMOTE | SSH to VPS | Server work |

---

## Switching Between Agents

- **CMD+`** - Cycle through Terminal windows
- **CMD+1/2/3/4** - Jump to specific window (if configured)
- Each window has its own Claude Code context

---

## Key Difference from Aether Orchestration

| Local Agents | Aether Orchestration |
|--------------|---------------------|
| Independent contexts | Shared memory |
| Manual coordination | Automatic coordination |
| No cross-learning | Agents learn together |
| Good for parallel solo work | Good for team missions |

---

*When Jared asks to "spin up local agents", refer to this technique.*
