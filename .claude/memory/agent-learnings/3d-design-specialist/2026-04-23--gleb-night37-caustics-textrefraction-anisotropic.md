# Night 37: Caustic Floor Patterns + Text Refraction + Anisotropic Specular

**Date**: 2026-04-23
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 93.1/100 overall (up from 92.4 Night 36 -- BROKE 93% TARGET)
**Tags**: gleb-kuznetsov, caustics, text-refraction, anisotropic-specular, ward-brdf, flux-pro, sdf-text

## Key Discoveries

### 1. Caustic Floor Patterns via FLUX Prompt Engineering

Effective prompt phrases for floor caustics:
- "SHARP CAUSTIC LIGHT PATTERNS projected onto the floor beneath and around the sphere"
- "caustics show characteristic bright convergence lines and dark shadow regions from light refraction through curved glass"
- "branching web-like structure with bright focal caustic points where light concentrates"
- "photon mapping quality caustics"

Result: 88/100 -- visible caustics with convergence lines, but slightly stylized. Real photon-mapped caustics have tighter definition.

### 2. Text Refraction -- FLUX Ceiling Identified

FLUX cannot produce physically accurate text inversion through glass sphere. Including "text appears flipped upside-down in center of sphere" was not honored. The model renders text-behind-glass as a composite rather than computing actual refraction.

**Conclusion**: Text refraction gap must close in Three.js via Troika SDF + UV distortion, not in FLUX prompting. Score: 85/100 in FLUX.

### 3. Anisotropic Specular -- Strong FLUX Response

Effective prompt phrases:
- "ANISOTROPIC SPECULAR HIGHLIGHTS stretching along the edge direction"
- "elongated thin bright lines that follow each hexagonal edge"
- "characteristic stretched highlight perpendicular to viewing direction"
- "anisotropic ward BRDF on edges"

Result: 91/100 -- edge-stretching highlights visible, orientation-dependent intensity variation correct.

### 4. Three.js Techniques Documented

**Caustic projection**: Multiplicative dual-texture sampling at different scales creates sharp convergence lines. Single texture = generic water caustic. Multiplied = realistic convergence.

**Anisotropic Ward BRDF**: ax=0.05 (tight along edge), ay=0.4 (stretched perpendicular). Ratio controls stretch amount.

**Text refraction**: Render text to background buffer, sample with UV distortion via refract() in glass fragment shader. Distortion = refractDir.xy * thickness * 0.1.

## Score Progression
- Night 35: 90.8%
- Night 36: 92.4%
- **Night 37: 93.1% (+0.7 points) -- BROKE 93%**

## Remaining Path to 95%
- Text refraction physics (Three.js Troika implementation needed)
- Caustic sharpness refinement
- Thin-film iridescence at grazing angles
- Half-res volumetric optimization (perf)

## Files
- Images: `exports/gleb-training/night-37/image{1,2,3}-*.png`
- Report: `exports/portal-files/gleb-training-night37-report.md`
