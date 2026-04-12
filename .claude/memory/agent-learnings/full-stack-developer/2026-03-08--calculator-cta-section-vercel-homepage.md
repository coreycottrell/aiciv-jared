# Calculator CTA Section — Vercel Homepage

**Date**: 2026-03-08
**Type**: operational
**Topic**: Adding "FREE TOOL" calculator CTA section to Vercel index.html

## What Was Done

Extracted the "FREE TOOL" calculator promotion section from purebrain.ai/pay-test-sandbox-3/ and added it to the Vercel static homepage at `/home/jared/projects/AI-CIV/aether/purebrain-site/public/index.html`.

## Placement

Inserted between the testimonials section (line ~8804) and the FOOTER comment block. The section has its own comment marker `<!-- FREE TOOL: CALCULATOR CTA -->`.

## Section Specs

- **Section id**: `calculator-cta`
- **Background**: `linear-gradient(135deg, #0d1120 0%, #1a1f35 100%)`
- **Border**: 1px rgba(42,147,193,0.2) top + bottom
- **Label**: "Free Tool" — color #2a93c1, 12px, 700 weight, uppercase, 2.5px letter-spacing
- **Heading**: "How Much Are You Wasting on AI Tool Sprawl?" — white, 28px, 700
- **Description**: gray #8892a4, 16px, 1.6 line-height
- **Button**: orange #f1420b → #d93a09 on hover, links to https://purebrain.ai/ai-tool-stack-calculator/

## Deployment

- Deployed via `npx vercel --prod --yes`
- Live at: https://purebrain-site.vercel.app/
- Inspect: https://vercel.com/pure-marketing-groups-projects/purebrain-site/FzhjmgJoWXBftDE713d551SJTVJV

## Key File

`/home/jared/projects/AI-CIV/aether/purebrain-site/public/index.html` — line ~8807
