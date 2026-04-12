# Portal Login & MVV Page Deployment Patterns

**Date**: 2026-02-24
**Context**: Multiple page deployments to purebrain.ai in Session 39

## Portal Login (app.purebrain.ai)
- Built: 1,064 lines, glass orb, particles, PureBrain branded
- Iterated through v2-v5 based on Jared's feedback
- Key iterations: PUREBRAIN colors (AI=orange, N=blue), icon, headline, button, gateway removed
- CTO architecture brief provided (phased approach, zero-risk CSS restyling)
- Strategy: soft gate (not hard block) recommended and accepted

## Migration Portal v2 (purebrain.ai/migrate/)
- Deployed to page 800
- elementor_data cleared for clean deployment
- Quiz Continue button fix: pointer-events `all` → `auto`
- Icons updated per Jared's screenshots

## MVV Page (purebrain.ai/mission-vision-values/)
- Built: 1,030 lines, 7 sections, all 7 pillars
- Deployed to WP page 929
- Footer link + homepage section deployed via plugin v5.2.0

## Key Patterns
- PUREBRAIN brand rule enforced everywhere: PUREBR(blue) + AI(orange) + N(blue)
- Self-contained HTML → wp:html block (prevents wpautop destruction)
- Plugin version bumps for footer/nav changes
- Elementor canvas template still loads theme CSS — always need nuclear defense
