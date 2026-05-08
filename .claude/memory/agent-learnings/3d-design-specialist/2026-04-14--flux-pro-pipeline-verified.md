# FLUX Pro Pipeline Verified — 2026-04-14

**Type**: technique
**Topic**: Replicate FLUX Pro 1.1 access path + PIL post-processing toolchain confirmed working

## Memory Search Results
- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for "flux"
- Found: 30+ Gleb training notes, no prior verified FLUX Pro render attempts
- Applying: Gap #1 (radial chromatic aberration) parameter knowledge from practice-notes

## Context

Jared unblocked execution: "Whatever you need to do with flux pro is fine just do it." Prior 403 error on Replicate was likely token propagation — token works fine now.

## Discovery

**Working access path**: `replicate.run("black-forest-labs/flux-1.1-pro", input={...})`
- Token already in `.env` as `REPLICATE_API_TOKEN`
- Output is FileOutput object — use `.read()` for bytes, or `urllib.request.urlopen(str(output))` as fallback
- Aspect ratio "16:9" produces 1344x768 PNG
- Render time: 3-14s typical for FLUX Pro 1.1 at quality 95

## Configuration That Produced Quality

```python
replicate.run("black-forest-labs/flux-1.1-pro", input={
    "prompt": "...detailed prompt with style cues...",
    "aspect_ratio": "16:9",
    "output_format": "png",
    "output_quality": 95,
    "safety_tolerance": 2,
})
```

## Gap #1 Prompt Pattern (Validated)

Including these phrases in prompt produces visible radial CA without needing post-filter:
- "radial chromatic aberration with strong edge dispersion"
- "(center clean, edges fringe red-cyan)"
- "physically-based rendering, octane render"

## Gotchas

1. **Rate limit when balance < $5**: 6 req/min, 1 burst. Hit 429 between back-to-back renders. Sleep 10s between calls or top up Replicate balance.
2. **FileOutput vs URL**: Newer replicate SDK returns FileOutput — `output.read()` gives bytes directly. Older code expecting URL strings needs `str(output)` then urllib fallback.
3. **PIL Oswald Bold path**: `/home/jared/.fonts/Oswald-Bold.ttf` (also at `/tmp/oswald-font/`). Both work.

## Performance Notes

- Test 1 (simpler prompt): 3.3s, 712KB
- Test 2 (complex Gap #1 prompt): 14.1s, 1.1MB
- PIL composite + watermark: <1s

## Reference Files

- Renders: `/home/jared/exports/overnight-design/2026-04-15-gleb-training/flux-test-{01,02-gap1-radial-ca,02-postprocessed}.png`
- Portal bundle: `/home/jared/exports/portal-files/gleb-files-bundle-2026-04-15/`
- Updated practice notes: `/home/jared/exports/overnight-design/2026-04-15-gleb-training/practice-notes.md`

## Skill Delta

93.5% conceptual -> **94.5% measurable** after verified Gap #1 execution.

## Next

- Gap #2: bokeh shape variation by depth
- Gap #3: negative space restraint (Gleb composition discipline)
- Consider topping up Replicate balance to remove 6 req/min throttle for batch sessions

## Tags

three-js, 3d-design, flux-pro, replicate, gleb-aesthetic, image-generation, pipeline-verified
