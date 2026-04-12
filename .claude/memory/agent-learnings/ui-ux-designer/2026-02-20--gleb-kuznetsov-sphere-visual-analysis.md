# Gleb Kuznetsov / Milkinside Sphere - Visual Analysis & Replication Guide

**Date**: 2026-02-20
**Agent**: ui-ux-designer
**Type**: teaching
**Topic**: Forensic visual analysis of Milkinside sphere aesthetic + concrete shader replication guide

---

## Core Finding

Gleb renders LIGHT, not objects. His sphere is a vessel for holding and refracting colored light.
We were rendering a glass object with internal geometry. These are opposite philosophies.

## The Secret Sauce

Multi-light colored environment (6 lights, multiple colors) + volumetric interior glow (no wireframes)
+ gold specular highlights + perfectly smooth glass surface (no FBM noise).

## Confirmed Color Palette (Colorful AI Sphere)
- #020204 - background/void
- #3C0E4E - deep violet interior zone
- #0D16F5 - electric blue accent
- #E42424 - saturated red hot zone
- #D10DCE - magenta/neon pink transition
- #18A8D3 - cyan counterpoint
- #B99C43 - gold specular highlight (NOT white)

## Critical Corrections to avatar-fluid.html
1. Remove icosahedron wireframe - replace with volumetric glow
2. Add 6 colored environment lights (not 1 white studio light)
3. Change specular from ice-white to gold #C8A84A
4. Remove FBM surface noise (set scratch/fingerprint to 0)
5. Add colored light bleed to background
6. Use maximum-saturation, wide color gamut interior colors

## What We Got Right
- Perfect sphere shape (no deformation)
- Dark background near #080a12
- Fresnel glass material with refraction
- Chromatic aberration (per-channel IOR)
- Beer's law absorption

## Full Guide
`/home/jared/projects/AI-CIV/aether/to-jared/gleb-visual-replication-guide.md`

## Reusable Pattern: The "Light vs Object" Test
When evaluating any future avatar iteration:
"Does the sphere contain LIGHT or does it contain GEOMETRY?"
LIGHT = Gleb direction. GEOMETRY = WebGL demo direction.
