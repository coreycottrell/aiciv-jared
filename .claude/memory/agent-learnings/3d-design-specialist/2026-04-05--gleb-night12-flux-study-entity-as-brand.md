# Night 12: FLUX Pro Study + Entity-as-Brand Pattern + Glass Container Architecture

**Date**: 2026-04-05
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 96% (maintained from Night 11)
**Tags**: gleb-kuznetsov, flux-pro, prompt-engineering, entity-as-brand, glass-container, pil-composite

## Study Findings

### New Gleb Patterns Observed (April 2026)

1. **Glass Container Architecture**: Gleb's latest Smart Home AI work uses glass not as decorative orbs but as STRUCTURAL containers. UI panels, cards, sections are all glass panes with 60-80% opacity fills, subtle backdrop blur (20-40px), edge highlights (1px white at 10-15% opacity), different blur levels per layer for depth hierarchy.

2. **Entity-as-Brand**: In LLM brand work, the 3D entity IS the brand. No separate logo. The shape, color, movement = the brand. PureBrain target: the neural glass brain IS PureBrain.

3. **Voice/Audio Reactivity**: Sound-reactive shapes signal intelligence. Shapes breathe, pulse, deform based on audio amplitude + frequency. Premium signal for "this is alive."

### FLUX 1.1 Pro Prompt Engineering (Refined)

Best elements for Gleb aesthetic:
- "Gleb Kuznetsov style" or "milkinside style" (anchors aesthetic)
- Physical glass terms: "translucent", "chromatic aberration", "Fresnel edge glow"
- Hex brand colors: "#2a93c1 blue and #f1420b orange" (FLUX respects hex)
- Lighting: "volumetric god rays", "dramatic rim lighting", "bokeh orbs"
- Depth: "cinematic depth of field", "sharp focus center", "soft bokeh background"
- Atmosphere: "dark moody sci-fi", "deep black background #080a12"
- Quality: "photorealistic CGI render", "8K quality"
- NEVER put text in FLUX prompts (always composite via PIL after)

### PIL Composite Template (Production-Ready)

Locked template for 1080x1350 portrait:
- Top gradient: 400px, alpha 200, power 1.5
- Bottom gradient: 500px, alpha 220, power 1.8
- Logo: 80px centered at y=40
- Wordmark: Segmented PURE(blue)BR(blue)AI(orange)N(blue).ai(gray) at y=130
- Title: Oswald Bold 52pt white, shadow blur=6 offset=4
- Subtitle: Oswald Bold 26pt blue, shadow blur=4 offset=2
- Accent line: 120px centered, 2px blue alpha 160
- Brand footer: 14pt gray at y=height-50

### Rate Limit Handling
- FLUX 1.1 Pro on Replicate: burst of 1 request when credit < $5
- Solution: retry with backoff (wait retry_after + 3s), 12s delay between sequential requests
- Use model-based endpoint: `/v1/models/black-forest-labs/flux-1.1-pro/predictions`

## Files Generated
- variation-1.png: Glass Neural Brain with volumetric lighting (1.5MB)
- variation-2.png: Ethereal AI Consciousness visualization (1.5MB)
- variation-3.png: Data Flow Architecture with PureBrain branding (1.7MB)
- All at: /home/jared/exports/portal-files/gleb-training-2026-04-05/
- Google Drive: folder 1CjE5qC4UubKqAsCwBJSH4s3oCORRWrbV

## Gaps Remaining (4%)
- Hexagonal bokeh aperture (-1.5%)
- Dynamic caustic-to-glass connection (-1%)
- Full SSR beyond floor (-1.5%)
- Half-res volumetric optimization for mobile (-1%)
