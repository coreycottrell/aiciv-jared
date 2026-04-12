# Staging Blog Font Fix - Oswald as PureBrain Primary Font (CORRECTED 2026-03-11)

**Date**: 2026-03-11
**Type**: gotcha + fix pattern
**Agent**: dept-systems-technology

## LOCKED IN: PureBrain primary font = Oswald (Jared confirmed 2026-03-11)

## Problem (Round 1 fix was WRONG)

Prior fix focused on matching Plus Jakarta Sans variable font ranges from production WP theme.
That was WRONG. Jared confirmed: PureBrain's primary font is Oswald, NOT Plus Jakarta Sans.

## Root Cause (Round 2 - actual fix)

The `.purebrain-blog` container CSS had `font-family: 'Plus Jakarta Sans', sans-serif;`
This set ALL body text on the blog page to Plus Jakarta Sans. It should be Oswald.

## Production Font Architecture

- WP Artistics theme loads Plus Jakarta Sans as the global WP theme font
- Security plugin injects custom blog CSS which loads Oswald via @import
- The custom blog HTML widget sets headings/nav/logo to Oswald
- The `.purebrain-blog` BASE font should be Oswald (confirmed by Jared)
- Newsletter form sections (.nf-section, .nf-input, .nf-submit) use Plus Jakarta Sans
  This matches production and is intentional for form readability

## Fix Applied

File: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html

Changed:
  .purebrain-blog { font-family: 'Plus Jakarta Sans', sans-serif; }   <- WRONG

To:
  .purebrain-blog { font-family: 'Oswald', sans-serif; }              <- CORRECT

Plus Jakarta Sans retained ONLY for newsletter form elements (.nf-section).

## Verification

curl -s "https://purebrain-staging.pages.dev/blog/" | grep -o "font-family: '[^']*'" | sort | uniq
Result:
  font-family: 'Oswald'            <- base font, headings, nav, logo
  font-family: 'Plus Jakarta Sans' <- newsletter form only (correct)

## Deployment

cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
CLOUDFLARE_API_TOKEN=$CF_PAGES_TOKEN npx wrangler pages deploy . --project-name=purebrain-staging --commit-dirty=true
Deployed: https://084ce925.purebrain-staging.pages.dev

## Key Rules Going Forward

1. PureBrain primary font = Oswald (Jared confirmed, LOCKED IN)
2. The .purebrain-blog base font-family MUST be Oswald
3. Form elements may use Plus Jakarta Sans for readability (secondary font)
4. Prior fix (just expanding Plus Jakarta Sans weight range) was addressing the wrong problem
5. When in doubt about brand fonts: Oswald = PureBrain display/brand font
