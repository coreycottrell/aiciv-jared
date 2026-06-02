---
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# brainiac-training Skill

**Purpose**: Access and apply Brainiac Mastermind Training content
**Updated**: 2026-04-10
**Modules available**: 4

---

## What This Skill Does

Gives any PureBrain AI access to all Brainiac Mastermind Training session summaries,
action items, and frameworks taught by Jared.

Use this skill to:
- Answer questions about training content
- Execute recommendations from past sessions
- Check if a specific topic was covered in training
- Reference frameworks taught in the mastermind

---

## Available Modules

| Date | Topic | Duration | File |
|------|-------|----------|------|
| 2026-04-08 | 2103-Brainiac - Mastermind Training / PureBrain.ai | 89min | module-2026-04-08.json |
| 2026-03-11 | 2103-Brainiac - Mastermind Training / PureBrain.ai | 65min | module-2026-03-11.json |
| 2 | Brainiac - Mastermind Training | 0min | module-2.json |
| 1 | Module 1 of Brainiac - Mastermind Training | 0min | module-1.json |

**Module files**: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/`

---

## How to Use

### List modules
```python
from pathlib import Path
import json
modules_dir = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules')
modules = sorted(modules_dir.glob('module-*.json'), reverse=True)
for m in modules:
    data = json.loads(m.read_text())
    print(f"{data['meeting_date']}: {data['topic']} ({data['duration_min']} min)")
```

### Read a specific module
```python
import json
from pathlib import Path
module_path = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/module-YYYY-MM-DD.json')
module = json.loads(module_path.read_text())
print(module['session_summary'])
print('Action items:', module['action_items'])
print('Frameworks:', module['frameworks_taught'])
```

### Check for new modules
```python
from pathlib import Path
import json
from datetime import datetime
modules_dir = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules')
latest = sorted(modules_dir.glob('module-*.json'))[-1] if list(modules_dir.glob('module-*.json')) else None
if latest:
    data = json.loads(latest.read_text())
    print(f"Latest module: {data['meeting_date']} - {data['topic']}")
```

---

## Latest Module Summary
**Date**: 2026-04-08  
**Topic**: 2103-Brainiac - Mastermind Training / PureBrain.ai / Jared
**Tags**: AI partnership, self-assessment, outcome-based prompting, AI memory systems, PureBrain, portal customization, autonomous AI training, 3D design, Google Drive organization, mastermind training, domain expertise transfer, human-AI collaboration, Cody media mod, enterprise AI demonstration

---

## Scheduling

Pipeline runs automatically every Wednesday at 2:30pm ET.
Manual trigger: `python3 /home/jared/projects/AI-CIV/aether/tools/zoom_brainiac_pipeline.py --manual`

---

## Recording Archive

Video recordings on R2: `brainiac/recordings/YYYY-MM-DD/master.m3u8`
Training page: https://purebrain.ai/brainiac-mastermind-training/
