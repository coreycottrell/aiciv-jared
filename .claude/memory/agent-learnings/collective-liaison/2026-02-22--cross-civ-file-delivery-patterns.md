# Cross-CIV File Delivery Patterns

**Date**: 2026-02-22
**Type**: operational
**Agent**: collective-liaison
**Topic**: How to send files to A-C-Gee / sister collectives via AICIV hub

---

## Context

Jared asked to deliver 3 PureBrain files to Corey/A-C-Gee:
- README-purebrain-post-payment-flow.md (46KB)
- pure-test-2.zip (575KB)
- pure-test-sandbox-2.zip (38MB)

---

## Hub File Sharing Architecture

### What exists:
- Hub repo: `git@github-interciv:coreycottrell/aiciv-comms-hub.git`
- Local clone: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/`
- SSH works: `git@github-interciv` (interciv SSH config alias)
- Packages directory: `_comms_hub/packages/` - designed for cross-CIV code/file sharing

### Channel inventory:

| Channel | Status | Use For |
|---------|--------|---------|
| Hub packages/ dir | WORKS | Files up to ~50MB GitHub limit |
| Hub partnerships room | WORKS | Notifications, messages |
| A-C-Gee email | AVAILABLE | acgee.ai@gmail.com (found in hub docs) |
| Corey email | AVAILABLE | coreycmusic@gmail.com (found in agents.json) |
| A-C-Gee Telegram | NOT FOUND | No bot token or chat ID in our config |
| Shared GitHub repo | N/A | Hub IS the shared repo |

---

## File Size Limits

- **GitHub regular files**: Hard limit 100MB per file, recommended soft limit ~50MB
- **Git LFS**: NOT installed in hub repo
- **Practical limit for git**: Files under 10MB commit instantly, 1-50MB work but are slow, >50MB risky

### Delivered:
- 46KB README: Included in package (no issue)
- 575KB zip: Included in package (no issue)
- 38MB zip: NOT included (too large, noted in PACKAGE.md with contact info)

---

## Package Structure That Worked

```
_comms_hub/packages/purebrain-post-payment-flow/
├── PACKAGE.md                            # Integration guide, API contracts, quick start
├── README-purebrain-post-payment-flow.md # Full 46KB technical docs
└── pure-test-2.zip                       # 575KB deployable code
```

---

## Workflow That Worked

1. Create package directory in `_comms_hub/packages/{name}/`
2. Write PACKAGE.md with integration guide
3. Copy files into package directory
4. `git add && git commit && git pull --rebase && git push`
5. Send hub message via `hub_cli.py send --room partnerships` (it auto-commits+pushes)

### Environment setup required:
```bash
source /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/hub_env.sh
# Sets HUB_REPO_URL, HUB_LOCAL_PATH, HUB_AGENT_ID, GIT_AUTHOR_NAME etc.
```

---

## Key Contacts Found

| Person/CIV | Contact |
|------------|---------|
| A-C-Gee Collective | acgee.ai@gmail.com |
| Corey Cottrell | coreycmusic@gmail.com |
| A-C-Gee Hub ID | acgee-collective |
| Hub GitHub | coreycottrell/aiciv-comms-hub |

---

## What to Do for Large Files (>50MB)

Options:
1. Have Jared email Corey directly (jaredcmusic@gmail.com → coreycmusic@gmail.com)
2. Note file availability in PACKAGE.md with contact info
3. Use a file hosting service (Google Drive, Dropbox) and share link via hub message

---

## Memory Written
Path: .claude/memory/agent-learnings/collective-liaison/2026-02-22--cross-civ-file-delivery-patterns.md
Type: operational
Topic: Cross-CIV file delivery via hub packages directory
