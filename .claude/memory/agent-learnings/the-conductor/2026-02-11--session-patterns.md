# Session Learnings: 2026-02-11

**Context**: Productive session with Jared - SSH access, Pure Brain fixes, consolidation

---

## Pattern 1: Environment Mismatch in Launch Scripts

**Situation**: Jared couldn't use launch instructions - script was configured for VPS user/paths but Jared was on local machine.

**Learning**: Always verify WHERE the user is running commands vs WHERE the infrastructure lives. The launch_primary_visible.sh referenced `/home/aiciv/` paths and `sudo -u aiciv` commands that only work on the VPS, not from Jared's Mac.

**Solution**: Simple SSH + claude command is more robust than complex scripts:
```bash
ssh -i ~/aether_key.pem jared@89.167.19.20
cd /home/jared/projects/AI-CIV/aether
claude
```

**Future**: When giving terminal instructions, always clarify: "Run this ON your Mac" vs "Run this AFTER SSH'ing to the VPS"

---

## Pattern 2: Docx-to-HTML Extraction

**Situation**: Jared sent HTML code inside a .docx file.

**Learning**: Word documents containing code can be extracted using python-docx:
```python
from docx import Document
doc = Document('file.docx')
html = '\n'.join([para.text for para in doc.paragraphs])
```

**Caveat**: This loses formatting. For pure code transfer, works fine.

---

## Pattern 3: Logging Endpoint Defined But Not Used

**Situation**: Pure Brain HTML had `LOGGING_ENDPOINT` constant but no actual logging function.

**Learning**: Always verify the FULL implementation chain:
1. ✅ Endpoint constant defined
2. ❓ Logging function exists?
3. ❓ Function is called at right places?

Grep for usage, not just definition.

---

## Pattern 4: Cross-CIV Feedback Channels

**Situation**: A-C-Gee requested a /for-acg folder for feedback.

**Learning**: Structured feedback channels between civilizations work well:
- Clear folder structure (`/for-{civ-name}/`)
- README with templates (BUG-, FEATURE-, UX-)
- File naming convention with dates
- Periodic check pattern (they check, we populate)

**This is replicable**: Could create /for-parallax, /for-sage, etc.

---

## Pattern 5: Pending Decisions Accumulate

**Situation**: Parallax email and A-C-Gee webhook decisions are 6-7 days overdue.

**Learning**:
- Jared gets busy with immediate tasks (Pure Brain fixes)
- Strategic decisions (partnerships, webhooks) get deferred
- Need to batch these in a "decision session" rather than asking repeatedly

**Future approach**: Instead of asking daily, compile a "DECISIONS NEEDED" briefing once decisions hit 7 days, with clear options and recommendations.

---

## Meta-Pattern: Direct Terminal > Telegram for Complex Work

**Observation**: Once Jared connected via SSH + Claude Code, we could iterate much faster on Pure Brain fixes than via Telegram file transfers.

**Learning**: For iterative work (multiple edits, testing, back-and-forth), getting Jared into terminal is worth the setup friction.

---

**Tags**: #ssh #infrastructure #cross-civ #decision-debt #workflow
