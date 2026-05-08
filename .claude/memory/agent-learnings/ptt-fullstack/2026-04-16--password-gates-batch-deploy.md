# Password Gates Batch Deploy Pattern

**Date**: 2026-04-16
**Type**: operational
**Topic**: Adding password gates to CF Pages client pages

## What Was Done

Added password gates to 8 client pages (9th already had one) using the sales-playbook pattern:
- Fixed overlay with z-index 99999 (above the Aether footer at 9999)
- PureBrain branded gate with gradient button
- sessionStorage-based auth persistence per page
- Each page gets unique sessionStorage key to prevent cross-page auth leakage

## Pages + Passwords

| Page | Password | Session Key |
|------|----------|-------------|
| hunden-partners | hunden2026 | hp-auth |
| hunden-placer-blueprint | hunden2026 | hpb-auth |
| purebrain-for-graham-martin | skybet47 | gm-auth |
| bloomberg-bpipe-demo | PureBrain.ai253443$ | bb-auth |
| toast-marketing-plan | purebrain2026 | tmp-auth |
| baystate-plan | purebrain2026 | bp-auth |
| purebrain-x-hovr-ai-partnership-brief | hovr2026 | hovr-auth |
| php-point-of-sale-payment-processing-partnership | PureBrain.ai253443$ | php-auth |
| aether-awakening | pureinvestor2026 | awaken-auth (pre-existing) |

## Pattern

Gate HTML injected right after first `<body>` tag. Python script approach works well for batch operations. cf-deploy.py positional args (not --paths flag) for deploying specific files.

## Gotcha

Many WP-exported pages have multiple `<body>` tags from embedded content. Only the first one is the real page body - inject gate there. The duplicate body tags are inside inner content that gets hidden behind the gate overlay anyway.
