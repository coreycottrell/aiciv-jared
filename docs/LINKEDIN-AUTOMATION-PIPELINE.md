# LinkedIn 5-Stage Automation Pipeline

**Built**: 2026-04-14
**Status**: Live (code + BOOPs). Blocked on: seeding real LinkedIn profile URLs in `configs/linkedin_icps.json` (Drive folder `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3` contained only persona descriptions, not profile URLs).

---

## Per-post flow (5 stages)

```
T-60min: PRE-COMMENTS   — 3-5 ICP posts, 90s spacing          (linkedin_icp_commenter.py)
T-0    : MAIN POST       — scheduled LinkedIn post             (linkedin_scheduled_poster.py)
T+2min : FIRST COMMENT   — own post, ref URL                   (linkedin_scheduled_poster.py, auto)
T+30min: POST-COMMENTS   — 3-5 more ICP posts, 90s spacing    (linkedin_icp_commenter.py)
T+60min: REACTIONS       — rotate Support/Celebrate/Insightful/Love (inside commenter)
```

Blog posts stay on PureSurf separately — this pipeline covers everything else.

---

## BOOP schedule (UTC)

Each of the 4 daily post slots has 2 companion BOOPs (pre + post). All daily.

| Slot (ET) | Pre-comment (UTC) | Main post (UTC) | Post-comment (UTC) |
|-----------|-------------------|------------------|--------------------|
| 8:30am    | 11:30             | 12:30            | 13:00              |
| 11am      | 14:00             | 15:00            | 15:30              |
| 1pm       | 16:00             | 17:00            | 17:30              |
| 3pm       | 18:00             | 19:00            | 19:30              |

BOOPs registered in `.claude/scheduled-tasks-state.json` (backup saved as `.bak`):
- `linkedin-pre-comment-{0830,1100,1300,1500}`
- `linkedin-post-comment-{0830,1100,1300,1500}`

First-comment on own post runs **inside** `linkedin_scheduled_poster.py` (T+2min sleep).

---

## Files

| File | Role |
|------|------|
| `tools/linkedin_scheduled_poster.py` | Main post + first-comment (T+2min) |
| `tools/linkedin_icp_commenter.py`    | Pre/post ICP comments, reaction rotation, 90s spacing, block-list |
| `configs/linkedin_icps.json`         | ICP profiles + segments + team block-list |
| `configs/linkedin_icp_state.json`    | Auto-created rotation state (last_commented_at per handle) |
| `linkedin-posts-log.md`              | Human-readable pipeline telemetry |
| `logs/linkedin_scheduled_poster.log` | Poster + first-comment debug |
| `logs/linkedin_icp_commenter.log`    | Commenter + reaction debug |

---

## Adding ICPs

Edit `configs/linkedin_icps.json`. Add entries to the `profiles` array:

```json
{
  "handle": "some-person",
  "url": "https://linkedin.com/in/some-person/",
  "segment": "smb-founder",
  "added": "2026-04-15"
}
```

`segment` key should match one of the 6 segment keys loaded from the Drive folder
(agency-director, ecommerce-owner, finance-realestate, ops-manager, smb-founder,
solo-consultant).

The commenter picks **least-recently-engaged** profiles first — rotation is automatic.

---

## Block-list

`configs/linkedin_icps.json` has a `block_list` array. NEVER comment on these handles.
Seeded with: jareddsanborn, jared-sanborn, coreycottrell + 3 placeholders for Nathan /
Greg / Chris (update with real handles).

If Jared adds new team members, add their handle here.

---

## Pausing / resuming

**Pause all comment companions**:
```bash
python3 -c "
import json
from pathlib import Path
p = Path('.claude/scheduled-tasks-state.json')
d = json.loads(p.read_text())
for k in list(d['tasks']):
    if 'linkedin-pre-comment' in k or 'linkedin-post-comment' in k:
        d['tasks'][k]['status'] = 'paused'
p.write_text(json.dumps(d, indent=2))
print('Paused')"
```

Flip `'paused'` back to `'active'` to resume.

---

## Dry-run + tests

```bash
# Commenter dry-run (no API calls, prints decisions):
python3 tools/linkedin_icp_commenter.py --user jared --count 1 --dry-run

# Poster first-comment simulation (no post, no sleep):
python3 tools/linkedin_scheduled_poster.py --test-first-comment
```

---

## Known limitations

1. **LinkedIn API scope for reading others' posts is restricted.** Free/personal
   tokens cannot fetch strangers' recent post URNs. `fetch_recent_post_urn()` in
   `linkedin_icp_commenter.py` is the single swap-point — wire in a PureSurf
   browser-side scrape when ready.
2. **Reactions endpoint** (`/v2/reactions`) also typically needs elevated scope;
   commenter logs warnings and continues on 403.
3. **Drive folder `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3`** holds persona docs, not
   profile URLs. `profiles` array is intentionally empty until seeded.

---

## Troubleshooting

- **Commenter says "No eligible profiles"**: `configs/linkedin_icps.json.profiles` is empty. Add some.
- **First-comment skipped**: URL didn't embed a URN. Check `logs/linkedin_scheduled_poster.log` for the "could not extract URN" warning.
- **All comments failing 403**: token scope insufficient. See limitations #1.
- **BOOPs not firing**: check `.claude/scheduled-tasks-state.json` status field. Also confirm the BOOP runner itself is alive.
