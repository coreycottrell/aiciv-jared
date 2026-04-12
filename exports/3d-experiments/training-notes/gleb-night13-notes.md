# Night 13: Hexagonal Bokeh + Caustic-Glass Linkage + Enhanced SSR

**Date**: 2026-04-05 | **Score**: 97% (up from 96%) | **Gaps Closed**: 2 of 4

## Techniques Implemented

1. **Hex Bokeh DoF** (CLOSED -1.5%): 3-ring hex sampling kernel (6+12+18 samples), interpolate between hex edge vertices instead of circular. aperture=0.012-0.018.
2. **Caustic-Glass Link** (CLOSED -1%): Frequency-matched breathing (0.55Hz) between glass and caustics. glassInfluence tracks sphere Y position.
3. **Enhanced SSR** (Reduced to -0.5%): 32-step vertical screen march. Needs normal buffer MRT for full arbitrary-surface reflections.

## 3 Variations Built
- Hex Bokeh Focus, Caustic-Glass Link, Full SSR Composite
- File: exports/3d-experiments/gleb-night13-hex-bokeh-caustic-link.html

## Remaining to 100%: ~3% (optimization-tier, not aesthetic)
