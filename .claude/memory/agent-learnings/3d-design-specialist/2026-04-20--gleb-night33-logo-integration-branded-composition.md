# Night 33: Logo Integration + Branded Image Composition

**Date**: 2026-04-20
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 87.8/100 overall (up from 86.2 Night 32)
**Tags**: gleb-kuznetsov, logo-placement, brand-integration, quiet-zone, brand-halo, blog-banner, composition

## Key Discoveries

### 5 Logo Integration Principles (NEW -- first session on this topic)

**Principle 4: Quiet Zone / Active Zone Model**
- Active Zone = center 60-70% of frame (3D objects, lights, bloom, caustics)
- Quiet Zone = margins (upper/lower 15%, corners) -- unbroken negative space
- Logo ONLY in Quiet Zone. No bloom spill crosses into Quiet Zone.
- Jared's rule: "upper-right or upper-left, never overlaps main content" = Quiet Zone principle

**Principle 5: Logo Flat; Glass Rich**
- Logo has NO glow, emission, gradient, shadow, glass treatment
- Logo: flat white, 65-85% opacity, clean vector
- The contrast between flat logo and rich glass IS the hierarchy

**Principle 6: Brand Halo (Light Bridge)**
- Glass object's CA fringing extends TOWARD logo zone but stops short
- Creates soft colored gradient in the gap (logo feels lit by scene, not pasted)
- UNTESTED in actual renders -- needs validation next session

**Principle 7: Logo Scale = 3-5% of Frame Width**
- Icon: ~72-120px at 2400px width
- Wordmark: ~192-360px at 2400px width
- If eye goes to logo before 3D scene, logo is too large

**Principle 8: Corner Anchoring with Breathing Room**
- 3-4% margin from edges (72-96px horizontal, 38-50px vertical at 2400x1260)
- Never flush to corner -- breathing room prevents "trapped" feeling

### Composition Planning Now Starts with Logo Territory

Previous: "Where does the object go?" -> build scene
Now: "Where is the logo?" -> protect that zone -> place objects in remaining space -> verify buffer

### FLUX Prompt Engineering for Logo-Safe Renders

Include explicit: "upper-right/left corner completely empty and dark for logo placement" in every FLUX prompt for branded images. This creates protected territory in the base render.

### Gleb's Brand Integration Patterns (from study)

1. **Separate Spatial Zones**: Brand text never shares space with 3D hero objects
2. **Whisper Text**: Logo/wordmark at 50-80% opacity, thin weight, wide tracking -- whispers while glass shouts
3. **Title Card Approach**: When brand name must be prominent, build a SCENE for it (glass frames it, doesn't overlap it)
4. **Brand Through Material**: Brand color lives in glass attenuation/tint, NOT in typography color

## 3 Blog Banner Specs Created

1. **"The Context Tax"** (Mon) -- Calendar shattering, fragments scatter left/down, logo upper-right
2. **"Day 100 vs Day 1"** (Tue) -- Two glass tubes, stagnant vs exponential overflow, warm gold, logo upper-left
3. **"32 Agents Architecture"** (Wed) -- Radial network, conductor center, 3 rings of agent nodes, logo upper-right

Each spec includes: full geometry, materials, lights, camera, postprocessing, animation keyframes, composition map, FLUX prompt, PIL composite code, pre-ship checklist.

## Gotchas

- Brand Halo technique is THEORETICAL -- needs render validation (does CA extend create "lit by scene" or "color bleed"?)
- Logo zone must be planned BEFORE composition, not after
- Dense scenes (32 Agents) need intentional agent-sparse quadrants for logo territory
- FLUX prompts need explicit negative space instructions or the AI fills every corner

## Score Progression
- Night 28: 78.6%
- Night 31: 83.8%
- Night 32: 86.2%
- Night 33: 87.8% (+1.6 points)
- Biggest gains: Composition +5% (logo territory planning), Emotional resonance +2%

## Files Generated
- Training report: `/home/jared/exports/portal-files/OVERNIGHT-3D-TRAINING-V3-2026-04-20.md`
- 3 blog banner specifications with full logo integration
- Cumulative techniques: 39
