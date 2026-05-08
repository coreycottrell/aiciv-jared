# cf-deploy.py --verify Flag Implementation

**Date**: 2026-04-15
**Agent**: coder
**Type**: teaching
**Topic**: Deployment verification, Trio coordination, deploy-target-map integration

---

## Context

After 3 deploy-target incidents on 2026-04-15 (Aether→staging instead of prod, Chy→staging lost 172 gift pages, ptt-fullstack→wrong project), Jared + Trio (Aether + Chy) decided to add verification infrastructure to cf-deploy.py.

Source of truth: `/home/jared/projects/AI-CIV/aether/shared/deploy-target-map.json` (3387 bytes, co-designed by Chy + Aether in real-time).

---

## Implementation

Added `--verify` flag to cf-deploy.py that:

1. **Reads deploy-target-map.json** (graceful if missing - warns but continues)
2. **Validates CF project** → hostname binding (e.g., purebrain-production → purebrain.ai)
3. **Checks path ownership** → errors if deploying to other civ's paths (e.g., Aether deploying to /gifts/ = Chy-owned)
4. **Warns on 777 content** → to purebrain-production (catches incidents like ptt-fullstack's)
5. **Warns on shared paths** → reminds to notify other civ via Trio

Also added `--force` flag to bypass ownership errors for coordinated cross-civ deploys.

---

## Key Design Decisions

### Opt-in, not breaking

- Default behavior unchanged (backward compatible)
- Missing map file = warning + continue (non-breaking)
- Parse error in map = warning + continue (non-breaking)
- Always show helpful tip at end if --verify NOT used

### Ownership model

- `path_owners` map in deploy-target-map.json
- Prefix matching (e.g., /gifts/ matches /gifts/test-gift)
- Three states: `aether`, `chy`, `shared`
- Aether deploying to Chy path = ERROR (blocking)
- Aether deploying to shared = WARNING (notify via Trio)

### CIV_IDENTITY constant

- Hardcoded `CIV_IDENTITY = "aether"` in cf-deploy.py
- Chy's copy of cf-deploy.py will have `CIV_IDENTITY = "chy"`
- Enables path ownership enforcement

### Graceful degradation

- No map file? Warn, continue
- Map parse error? Warn, continue
- Missing keys in map? Skip that check, continue
- Never crash on verification (only abort if ownership violation + no --force)

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/cf-deploy.py` (+123 lines)
  - Added `DEPLOY_MAP_PATH` constant
  - Added `CIV_IDENTITY` constant
  - Added `verify_deploy_target()` function (95 lines)
  - Added `--verify` and `--force` args
  - Added tip message when --verify NOT used
  - Backup at: `cf-deploy.py.bak-verify-20260415`

---

## Testing

Verified all scenarios:

1. `--help` → shows --verify + --force
2. `--verify` with Aether-owned path (blog/) → ✅ green check
3. `--verify` with Chy-owned path (gifts/) → 🚨 error, aborts
4. `--verify --force` with Chy-owned path → ⚠️ warning, proceeds
5. Missing map file → ⚠️ warns, continues (non-breaking)
6. Dry-run without --verify → shows tip message
7. Dry-run with --verify → no tip message (already using it)

---

## Learnings

### Pattern: Opt-in verification with helpful nudges

Rather than force breaking changes, add opt-in safety with persistent gentle reminders:
- Tip message at end of EVERY deploy without --verify
- Non-blocking warnings (map missing = continue)
- Clear path to adoption (see tip → add --verify → safety++)

### Pattern: Graceful degradation on shared infrastructure

When two civs share a config file (deploy-target-map.json):
- Don't crash if file missing (other civ may not have it yet)
- Don't crash if schema evolves (use .get() with defaults)
- Warn loudly but don't block

### Pattern: Trio coordination via shared files

Real-time co-design of deploy-target-map.json during Trio session worked well:
- Both civs can see/edit the same file
- JSON schema = self-documenting
- Incidents log in same file = institutional memory
- Version field for schema evolution

### Anti-pattern avoided: Network calls for verification

Could have queried CF API to get live project→domain mapping, but that would:
- Add latency to every deploy
- Fail when offline/rate-limited
- Create dependency on CF API for local verification

Local file read is instant, works offline, fails gracefully.

---

## Future Enhancements

Potential improvements (not implemented yet):

1. **Auto-sync map across civs** - cron job to sync /home/aiciv/shared/ → /home/jared/projects/AI-CIV/aether/shared/
2. **Incident logging** - append to `incidents` array in map when verification fails
3. **Pre-commit hook** - run --verify --dry-run before git commits
4. **CI/CD integration** - require --verify in automated deploys
5. **Map schema validation** - JSON schema for deploy-target-map.json
6. **Wildcard path matching** - support `/pay-test-*/` patterns in ownership checks (currently basic prefix matching)

---

## Related Work

- `/home/jared/projects/AI-CIV/aether/shared/deploy-target-map.json` - source of truth
- Trio coordination protocols (emerging pattern)
- ptt-fullstack incident (deploy sed4aArC9 dir to wrong project)

---

## Command Examples

```bash
# Deploy with verification (recommended)
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify blog/new-post/

# Deploy to Chy-owned path (requires coordination)
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --force gifts/new-gift/

# Check what verification would say (dry-run)
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --dry-run investor-avatar/

# Deploy without verification (shows tip at end)
python3 tools/cf-deploy.py blog/test/
# Output: 💡 Tip: run with --verify next time...
```

---

## Attribution

- **Designed by**: Jared + Trio (Aether + Chy) live session 2026-04-15
- **Implemented by**: coder agent (Aether's delegation)
- **Co-designed map**: Chy + Aether (3387 bytes, same-session collaboration)
- **Incidents that triggered**: 3 on 2026-04-15 (morning staging vs prod, Chy gift pages, ptt-fullstack wrong project)

---

*This memory documents both implementation AND the coordination pattern (Trio real-time co-design). Future agents: this is how cross-civ infrastructure gets built.*
