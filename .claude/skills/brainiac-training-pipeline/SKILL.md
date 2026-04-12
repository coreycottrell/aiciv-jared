---
name: brainiac-training-pipeline
description: Auto-generate AI training snippets when new Brainiac Mastermind Training videos/modules are added. Detects new videos, summarizes transcripts, generates structured AI-optimized content, injects HTML into the training page, and deploys to CF Pages. Idempotent - skips modules that already have snippets.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# Brainiac Training Snippet Pipeline

**Purpose**: Automatically generate dense AI training snippets for each Brainiac Mastermind Training module and inject them into the live training page.

**Trigger**: New video/module added to the training page OR new transcript file detected in `exports/brainiac-training/transcripts/`

**Philosophy**: Every video module deserves rich AI-optimized companion content - not just for human learners, but as training material for agents. Dense, structured, searchable.

---

## Pipeline Overview

```
STEP 1: DETECT     → Check for new modules without snippets
STEP 2: EXTRACT    → Summarize transcript into dense AI format
STEP 3: GENERATE   → Create structured training snippet (4-section format)
STEP 4: INJECT     → Insert snippet HTML under module in training page
STEP 5: DEPLOY     → CF Pages deploy + cache purge
```

**Output**: Updated training page HTML + saved summary markdown + updated manifest JSON

---

## File Paths (Absolute)

```
TRAINING PAGE:
  /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html

TRANSCRIPTS (input):
  /home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/
  - module-{N}-transcript.txt       (raw text transcript)
  - module-{N}-{slug}.md            (pre-formatted transcript)
  - *.vtt                           (WebVTT caption files)

SUMMARIES (output):
  /home/jared/projects/AI-CIV/aether/exports/brainiac-training/summaries/
  - module-{N}-{slug}.md            (AI-optimized summary)

MANIFEST (output):
  /home/jared/projects/AI-CIV/aether/exports/brainiac-training/ai-training-manifest.json
```

---

## Step 1: Detect New Modules

### Check What Already Has Snippets

```bash
# List all transcript files
ls /home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/

# Check which modules already have AI training snippets in the page
grep -c "ai-training-snippet" /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html

# Check which module IDs have snippets (idempotency check)
grep -oP 'ai-training-snippet-module-\K[0-9]+' /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html | sort -u
```

### Identify Modules Needing Snippets

```bash
# List all transcripts
ls /home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/ | grep -E "module-[0-9]+"

# Cross-reference: modules with transcripts but WITHOUT snippets = need processing
# If module-N appears in transcripts but module-N NOT in grep above → process it
```

### Check for Pre-Existing Summaries

```bash
ls /home/jared/projects/AI-CIV/aether/exports/brainiac-training/summaries/
```

If `module-{N}-{slug}.md` exists in summaries, skip re-extraction and go directly to Step 3.

---

## Step 2: Extract and Summarize Transcript

### Input Sources (Priority Order)

1. **Pre-formatted transcript** (`module-{N}-{slug}.md`) - use directly
2. **Raw text transcript** (`module-{N}-transcript.txt`) - summarize
3. **VTT caption file** (`*.vtt`) - strip timecodes, then summarize
4. **Video URL only** - document that transcript extraction is needed; do NOT generate snippet without content

### VTT Stripping Pattern

```python
import re

def strip_vtt(vtt_path):
    with open(vtt_path) as f:
        content = f.read()
    # Remove WEBVTT header
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    # Remove timestamp lines (00:00:00.000 --> 00:00:00.000)
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}[^\n]*\n', '', content)
    # Remove position/alignment metadata
    content = re.sub(r'^[A-Z]+=.*$', '', content, flags=re.MULTILINE)
    # Collapse whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    # Deduplicate consecutive duplicate lines
    lines = content.split('\n')
    deduped = [lines[0]] if lines else []
    for line in lines[1:]:
        if line.strip() != deduped[-1].strip():
            deduped.append(line)
    return '\n'.join(deduped).strip()
```

### Summarization Approach

Read the full transcript. Extract:
- Main thesis / core teaching of this module
- The 5-8 most important conceptual points
- Specific techniques, methods, or frameworks taught
- Memorable phrases or quotes from the presenter
- Actionable items a learner should do after watching
- Any tools, systems, or software mentioned

Write the summary to:
```
/home/jared/projects/AI-CIV/aether/exports/brainiac-training/summaries/module-{N}-{slug}.md
```

Summary format:
```markdown
# Module {N}: {Title} - AI Training Summary

**Source**: {transcript filename}
**Generated**: {YYYY-MM-DD}
**Module Slug**: {slug}

## Core Teaching
{1-2 sentence thesis of the entire module}

## Key Concepts
{Dense paragraph covering the conceptual landscape}

## Specific Techniques
{List of named techniques/frameworks mentioned}

## Key Quotes
{Verbatim or near-verbatim standout lines from transcript}

## Actionable Items
{What a learner should DO after watching}

## Tools/Systems Mentioned
{Any specific tools, platforms, software referenced}

## AI Training Notes
{How this module's content applies to AI/agent systems - meta-analysis}
```

---

## Step 3: Generate Training Snippet

Transform the summary into a structured HTML training snippet.

### Four-Section Format

Every snippet has exactly four sections:

**Section 1: Core Concepts** (bullet points)
- Dense conceptual bullets, not marketing language
- Each bullet = one discrete teachable idea
- 5-10 bullets max

**Section 2: Key Techniques** (numbered list)
- Specific named methods, frameworks, approaches
- Numbered for reference ("see Technique 3")
- 4-8 techniques

**Section 3: Implementation Checklist** (actionable checkboxes)
- What to DO after watching this module
- Concrete, specific, measurable actions
- 5-8 items

**Section 4: Key Quotes / Insights** (blockquote format)
- Verbatim or near-verbatim memorable lines
- Only include if genuinely quotable
- 2-4 quotes

### HTML Template

```html
<!-- AI TRAINING SNIPPET: MODULE {N} -->
<div class="ai-training-snippet ai-training-snippet-module-{N}" id="ai-training-snippet-module-{N}">
  <div class="snippet-header">
    <span class="snippet-icon">🧠</span>
    <h4>AI Training Snippet — Module {N}: {Title}</h4>
    <span class="snippet-badge">AI-Optimized</span>
  </div>
  <div class="snippet-body">

    <div class="snippet-section">
      <h5>Core Concepts</h5>
      <ul>
        <li>{concept 1}</li>
        <li>{concept 2}</li>
        <!-- ... -->
      </ul>
    </div>

    <div class="snippet-section">
      <h5>Key Techniques</h5>
      <ol>
        <li><strong>{Technique Name}</strong> — {brief description}</li>
        <li><strong>{Technique Name}</strong> — {brief description}</li>
        <!-- ... -->
      </ol>
    </div>

    <div class="snippet-section">
      <h5>Implementation Checklist</h5>
      <ul class="checklist">
        <li><label><input type="checkbox"> {action item 1}</label></li>
        <li><label><input type="checkbox"> {action item 2}</label></li>
        <!-- ... -->
      </ul>
    </div>

    <div class="snippet-section">
      <h5>Key Insights</h5>
      <blockquote>"{quote 1}"</blockquote>
      <blockquote>"{quote 2}"</blockquote>
    </div>

  </div>
</div>
<!-- END AI TRAINING SNIPPET: MODULE {N} -->
```

### CSS (Inject Once at Page Top if Not Present)

```html
<!-- AI TRAINING SNIPPET STYLES -->
<style>
.ai-training-snippet {
  margin: 24px 0 32px;
  background: rgba(42, 147, 193, 0.06);
  border: 1px solid rgba(42, 147, 193, 0.25);
  border-radius: 12px;
  overflow: hidden;
}
.snippet-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: rgba(42, 147, 193, 0.12);
  border-bottom: 1px solid rgba(42, 147, 193, 0.2);
}
.snippet-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #2a93c1;
  flex: 1;
}
.snippet-icon { font-size: 1.2rem; }
.snippet-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: rgba(241, 66, 11, 0.15);
  color: #f1420b;
  border-radius: 20px;
  border: 1px solid rgba(241, 66, 11, 0.3);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.snippet-body { padding: 20px; }
.snippet-section { margin-bottom: 20px; }
.snippet-section:last-child { margin-bottom: 0; }
.snippet-section h5 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7a8299;
  margin: 0 0 10px;
  font-weight: 600;
}
.snippet-section ul, .snippet-section ol {
  margin: 0;
  padding-left: 20px;
  color: #c8ccd8;
  font-size: 0.9rem;
  line-height: 1.7;
}
.snippet-section ul.checklist { list-style: none; padding-left: 0; }
.snippet-section ul.checklist li { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; }
.snippet-section ul.checklist label { display: flex; align-items: flex-start; gap: 8px; cursor: pointer; }
.snippet-section ul.checklist input[type="checkbox"] { margin-top: 3px; accent-color: #2a93c1; flex-shrink: 0; }
.snippet-section blockquote {
  margin: 0 0 10px;
  padding: 10px 16px;
  border-left: 3px solid #2a93c1;
  background: rgba(42, 147, 193, 0.04);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  color: #a8b0c4;
  font-size: 0.88rem;
  line-height: 1.6;
}
</style>
<!-- END AI TRAINING SNIPPET STYLES -->
```

---

## Step 4: Inject into Training Page

### Find the Injection Point

Each module in the training page HTML has a structure like:

```html
<div class="module-card" data-module="{N}">
  ...video player, title, description...
</div>
```

OR a comment marker like:
```html
<!-- MODULE {N} END -->
```

**Injection strategy**: Insert the snippet HTML immediately AFTER the closing tag of the module's video card div (before the next module or section break).

### Injection Pattern

```python
import re

def inject_snippet(page_html, module_n, snippet_html):
    """
    Inject snippet after the module-{N} card.
    Idempotent: if snippet for module-{N} already exists, skip.
    """
    # Idempotency check
    if f'ai-training-snippet-module-{module_n}' in page_html:
        print(f"Module {module_n} snippet already exists - skipping")
        return page_html

    # Try to find module end comment first
    pattern_comment = f'<!-- MODULE {module_n} END -->'
    if pattern_comment in page_html:
        return page_html.replace(
            pattern_comment,
            snippet_html + '\n' + pattern_comment
        )

    # Fall back: find the module card closing div
    # Look for data-module="{N}" and find its closing tag
    # This requires careful parsing - use BeautifulSoup if available
    # or use the CSS class pattern

    print(f"WARNING: Could not find injection point for module {module_n}")
    print("Manual injection may be required. Snippet saved to summaries/.")
    return page_html
```

### Bash Alternative (for Simple Cases)

```bash
MODULE_N=2
SNIPPET_FILE="/tmp/snippet-module-${MODULE_N}.html"
PAGE="/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html"

# Verify injection point exists
grep -n "MODULE ${MODULE_N} END\|data-module=\"${MODULE_N}\"" "${PAGE}"

# Insert snippet at line after injection marker
# (adjust line number based on grep output)
```

---

## Step 5: Deploy

### Deploy to CF Pages

```bash
# 1. Verify the updated file looks correct
wc -l /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html

# 2. Run CF Pages deploy
cd /home/jared/projects/AI-CIV/aether
# Deploy script (use existing CF Pages deploy mechanism)
# Check tools/ or exports/cf-pages-deploy/ for the deploy command

# 3. Purge CF cache for the training page URL
# Per CF CACHE FLUSH rule (PERMANENT LOCK 2026-03-12):
# After EVERY CF Pages deploy, IMMEDIATELY purge CF cache
ZONE_ID=$(grep CF_ZONE_ID .env | cut -d= -f2)
CF_TOKEN=$(grep CF_API_TOKEN .env | cut -d= -f2)

curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://purebrain.ai/brainiac-mastermind-training/"]}'
```

---

## Manifest Update

After each successful snippet generation, update the AI training manifest:

```bash
MANIFEST="/home/jared/projects/AI-CIV/aether/exports/brainiac-training/ai-training-manifest.json"
```

**Manifest structure**:
```json
{
  "last_updated": "YYYY-MM-DD",
  "total_modules": 0,
  "modules_with_snippets": 0,
  "modules": [
    {
      "module_number": 1,
      "slug": "foundations",
      "title": "Module 1: Foundations",
      "has_transcript": true,
      "has_snippet": true,
      "summary_path": "exports/brainiac-training/summaries/module-1-foundations.md",
      "snippet_injected": "YYYY-MM-DD",
      "transcript_source": "module-1-transcript.txt"
    }
  ]
}
```

**Update after each module**:
```python
import json

manifest_path = "/home/jared/projects/AI-CIV/aether/exports/brainiac-training/ai-training-manifest.json"

# Load or create manifest
try:
    with open(manifest_path) as f:
        manifest = json.load(f)
except FileNotFoundError:
    manifest = {"modules": [], "total_modules": 0, "modules_with_snippets": 0}

# Update module entry
module_entry = {
    "module_number": N,
    "slug": slug,
    "title": title,
    "has_transcript": True,
    "has_snippet": True,
    "summary_path": f"exports/brainiac-training/summaries/module-{N}-{slug}.md",
    "snippet_injected": "YYYY-MM-DD",
    "transcript_source": transcript_filename
}

# Upsert
existing = [m for m in manifest["modules"] if m["module_number"] == N]
if existing:
    manifest["modules"].remove(existing[0])
manifest["modules"].append(module_entry)
manifest["modules"].sort(key=lambda x: x["module_number"])
manifest["total_modules"] = len(manifest["modules"])
manifest["modules_with_snippets"] = sum(1 for m in manifest["modules"] if m["has_snippet"])
manifest["last_updated"] = "YYYY-MM-DD"

with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
```

---

## Idempotency Rules

**ALWAYS check before processing**:

1. Does `exports/brainiac-training/summaries/module-{N}-{slug}.md` already exist?
   - YES → Skip Steps 1-2, use existing summary, go to Step 3
   - NO → Run full pipeline

2. Does `ai-training-snippet-module-{N}` appear in the training page HTML?
   - YES → Skip this module entirely, log "already done"
   - NO → Proceed with injection

3. Does manifest show `has_snippet: true` for this module?
   - YES → Double-check HTML, skip if confirmed
   - NO → Process

**Idempotency log output**:
```
[SKIP] Module 1 - snippet already injected (2026-03-10)
[SKIP] Module 2 - snippet already injected (2026-03-11)
[NEW]  Module 3 - no snippet found - processing...
  [OK] Transcript found: module-3-transcript.txt
  [OK] Summary generated: summaries/module-3-advanced-workflows.md
  [OK] Snippet generated: 4 sections, 892 chars
  [OK] Injected into training page
  [OK] Deployed to CF Pages
  [OK] Cache purged
  [OK] Manifest updated
```

---

## Triggering This Pipeline

### Manual Trigger

```
Invoke full-stack-developer (or appropriate tech agent via dept-systems-technology):
"Run the brainiac-training-pipeline skill. Check for new modules in
/home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/
that don't yet have AI training snippets in the training page.
For each new module found, run all 5 pipeline steps."
```

### When Jared Adds a New Recording

When Jared says "I added Module X to the training page" or "here's the new recording":
1. Check if transcript exists in `transcripts/`
2. If transcript exists → run pipeline immediately
3. If transcript doesn't exist → respond: "I can see the module was added. Once a transcript is available in exports/brainiac-training/transcripts/, I'll auto-generate the training snippet. Do you have a transcript file?"

### No Transcript Available Protocol

If only a video URL exists (no transcript):
1. Save a placeholder in summaries: `module-{N}-{slug}-NEEDS-TRANSCRIPT.md`
2. Update manifest with `has_transcript: false`
3. Do NOT generate snippet (would be fabricated content)
4. Note in Telegram: "Module N detected - waiting for transcript to generate AI training snippet"

---

## Quality Standards for Snippets

**A good training snippet**:
- Teaches something without requiring you to watch the video
- Contains specific, named techniques (not generic descriptions)
- Implementation checklist items are concrete ("Create a folder called X" not "organize your files")
- Quotes are verbatim or near-verbatim, not paraphrased
- Core Concepts bullets are dense - compress maximum insight into minimum words

**Reject and regenerate if**:
- Any section is vague or generic
- Checklist items are not actionable
- "Key Insights" are filler rather than genuine memorable lines
- Content duplicates without adding synthesis

---

## Related Files

- Training page: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html`
- Transcripts dir: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/`
- Summaries dir: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/summaries/`
- Manifest: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/ai-training-manifest.json`
- CF cache flush rule: See MEMORY.md "CF CACHE FLUSH AFTER EVERY DEPLOY"

---

**Created**: 2026-03-12
**Author**: agent-architect
**Domain**: Brainiac Training Content Pipeline
