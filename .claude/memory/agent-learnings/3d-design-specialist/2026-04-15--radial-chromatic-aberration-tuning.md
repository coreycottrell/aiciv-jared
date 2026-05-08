# Radial Chromatic Aberration Tuning for Gleb-Level Lens Sim

**Date**: 2026-04-15
**Type**: technique
**Confidence**: high (conceptual), pending render verification

## Context
Overnight Gleb training session. Self-assessment identified flat/uniform chromatic aberration as gap #1 between our current ~93% Gleb mastery and the 98%+ target.

## Discovery
React Three postprocessing `ChromaticAberration` supports `radialModulation={true}` + `modulationOffset` parameter. This shifts CA from uniform post-filter to edge-biased physical lens simulation. Gleb's work uses radial modulation consistently — it's a primary differentiator between "3D render with CA filter" and "looks like a real photograph."

## Configuration (Signature Gleb Default)
```jsx
<ChromaticAberration
  offset={[0.0008, 0.0008]}
  radialModulation={true}
  modulationOffset={0.15}
/>
```

## Parameter Sweet Spots
- Subtle: offset 0.0005, modulation 0.12
- Signature: offset 0.0008, modulation 0.15
- Dramatic: offset 0.0015, modulation 0.18
- Avoid: offset > 0.003 (VHS/glitch territory)

## Gotchas
- Flat CA (our previous default) reads synthetic even with correct transmission materials
- Too-high modulation makes edges feel fisheye-distorted
- Must pair with high-segment geometry (128+) or edge dispersion reveals facets

## Next Step
Verify via rendered output once FLUX Pro / Gemini 3 Pro Image key situation is reconciled (ST# routing needed — conflicting guidance from Jared vs ground truth doc).

## Reference
- Practice notes: /home/jared/exports/overnight-design/2026-04-15-gleb-training/practice-notes.md
- Morning deliverable: /home/jared/exports/portal-files/overnight-design-training-2026-04-15.md
