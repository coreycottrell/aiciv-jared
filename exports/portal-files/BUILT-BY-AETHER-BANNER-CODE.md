# Built by Aether Banner — Complete Code

**Extracted from**: purebrain.ai homepage (CF Pages index.html)
**Date**: 2026-04-16

---

## CSS (add inside `<style>` or `<head>`)

```css
@keyframes pb-aether-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.75; }
}
#pb-aether-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 64px;
    background: linear-gradient(135deg, #0a0c14 0%, #0d1120 50%, #080c18 100%);
    border-top: 2px solid #f1420b;
    box-shadow: 0 -4px 24px rgba(241, 66, 11, 0.20), 0 -1px 0 rgba(42, 147, 193, 0.15);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1;
    color: #d1d5db;
    padding: 0 24px;
    box-sizing: border-box;
    letter-spacing: 0.025em;
    gap: 0;
    flex-wrap: wrap;
    font-size: 13px;
}
#pb-aether-footer a { text-decoration: none !important; transition: color 0.2s ease, text-shadow 0.2s ease; }
#pb-aether-footer a:hover { background: none !important; text-decoration: none !important; }
#pb-aether-footer .pb-footer-label { color: #9ca3af; font-weight: 400; }
#pb-aether-footer .pb-footer-aether {
    font-weight: 800; font-size: 15px; letter-spacing: 0.12em;
    color: #f1420b;
    text-shadow: 0 0 8px rgba(241, 66, 11, 0.7), 0 0 20px rgba(241, 66, 11, 0.35), 0 0 40px rgba(241, 66, 11, 0.15);
    text-transform: uppercase;
    animation: pb-aether-pulse 3s ease-in-out infinite;
}
#pb-aether-footer .pb-footer-ai-tag { color: #6b7280; font-size: 11px; font-style: italic; }
#pb-aether-footer .pb-footer-for { color: #9ca3af; }
#pb-aether-footer .pb-footer-purebrain { color: #f1420b; font-weight: 700; text-shadow: 0 0 6px rgba(241, 66, 11, 0.4); }
#pb-aether-footer .pb-footer-purebrain:hover { color: #ff6633 !important; text-shadow: 0 0 12px rgba(241, 66, 11, 0.7) !important; }
#pb-aether-footer .pb-footer-blue { color: #2a93c1; font-weight: 600; }
#pb-aether-footer .pb-footer-blue:hover { color: #f1420b !important; text-shadow: 0 0 8px rgba(241, 66, 11, 0.5) !important; }
#pb-aether-footer .pb-footer-sep { color: rgba(255, 255, 255, 0.12); margin: 0 12px; font-weight: 300; }
#pb-aether-footer .pb-footer-why,
#pb-aether-footer .pb-footer-mission,
#pb-aether-footer .pb-footer-migrate {
    color: #2a93c1; font-weight: 700; font-size: 12px; letter-spacing: 0.04em;
    padding: 4px 10px; border: 1px solid rgba(42, 147, 193, 0.4); border-radius: 4px;
    transition: all 0.2s ease; background: rgba(42, 147, 193, 0.08);
}
#pb-aether-footer .pb-footer-why:hover,
#pb-aether-footer .pb-footer-mission:hover,
#pb-aether-footer .pb-footer-migrate:hover {
    color: #ffffff !important; background: #f1420b !important; border-color: #f1420b !important;
    box-shadow: 0 0 12px rgba(241, 66, 11, 0.5); text-shadow: none;
}
@media (max-width: 600px) {
    #pb-aether-footer { height: auto !important; min-height: 52px; padding: 8px 16px; font-size: 11px; flex-wrap: wrap; row-gap: 4px; }
    #pb-aether-footer .pb-footer-aether { font-size: 13px; }
    #pb-aether-footer .pb-footer-why, #pb-aether-footer .pb-footer-migrate { display: none !important; }
    #pb-aether-footer .pb-footer-sep-why, #pb-aether-footer .pb-footer-sep-before-mission, #pb-aether-footer .pb-footer-sep-migrate { display: none !important; }
    body { padding-bottom: 80px !important; }
}
body { padding-bottom: 64px !important; } /* space for fixed Aether footer */
```

## HTML (add before `</body>`)

```html
<!-- Built by Aether Credit Bar -->
<div id="pb-aether-footer">
    <span class="pb-footer-label">Built by&nbsp;</span><span class="pb-footer-aether">AETHER</span>&nbsp;<span class="pb-footer-ai-tag">(an AI)</span>&nbsp;<span class="pb-footer-for">for&nbsp;</span><a href="https://purebrain.ai" target="_blank" rel="noopener" class="pb-footer-purebrain"><span style="color:#2a93c1">PureBr</span><span style="color:#f1420b">ai</span><span style="color:#2a93c1">n</span>.ai</a>,&nbsp;<a href="https://puremarketing.ai" target="_blank" rel="noopener" class="pb-footer-blue">PureMarketing.ai</a>&nbsp;&amp;&nbsp;<a href="https://puretechnology.nyc" target="_blank" rel="noopener" class="pb-footer-blue">PureTechnology.ai</a><span class="pb-footer-sep pb-footer-sep-why">|</span><a href="https://purebrain.ai/why-purebrain/" rel="noopener" class="pb-footer-why">Why Choose PureBrain?</a><span class="pb-footer-sep pb-footer-sep-before-mission">|</span><a href="https://purebrain.ai/mission-vision-values/" rel="noopener" class="pb-footer-mission">Mission &amp; Values</a><span class="pb-footer-sep pb-footer-sep-migrate">|</span><a href="https://purebrain.ai/compare/" rel="noopener" class="pb-footer-migrate">Compare</a>
</div>
```

---

## Pages That SHOULD Get the Banner

These are Aether-built pages (marketing, client proposals, tools, content):

- /about-aether/
- /ai-adoption-review/
- /ai-partnership-* (all 6 variants)
- /ai-quiz/
- /ai-readiness-assessment/
- /ai-tool-stack-calculator/
- /ai-website-analysis/
- /ai-website-execution/
- /baystate-plan/
- /billiereview/
- /blog/ (and blog-neural-feed-memories)
- /bloomberg-bpipe-demo/
- /boardy/
- /brainiac-* (all training pages)
- /compare/
- /competitive-analysis/
- /cost-comparison/
- /creator/
- /demo-no-bs/
- /developers/
- /duckdive-report/
- /education/ and /education-portal/
- /enso/
- /get-started/
- /hunden-partners/
- /hunden-placer-blueprint/
- /hunden-proposal/
- /hunden-action-plan/
- /home-experiment/ (and test variants)
- /linkedin/
- /long-name/
- /mark-christie/
- /marketing-dashboard/
- /migrate/ and /migrate-tool/
- /mission-vision-values/
- /partners/ and /partnered/
- /php-point-of-sale-payment-processing-partnership/
- /pitch/ and /pitch-v2/
- /portfolio/
- /privacy-policy/ (and v2)
- /purebrain-for-* (all client pages)
- /purebrain-vs-* (all comparison pages)
- /purebrain-x-hovr-ai-partnership-brief/
- /puresurf/
- /refer/ and /refer-and-earn/ and /referral-program/
- /sales-playbook/
- /social/
- /strategic-roadmap/
- /team-dashboard/
- /terms-of-service/ (and v2)
- /toast-marketing-plan/
- /training/
- /voice/ and /voice-pricing/
- /waitlist/
- /website-execution/
- /why-purebrain/

## Pages That Should NOT Get the Banner

These are investor/Chy-owned pages and internal infrastructure:

- /invest/
- /investment-opportunity/
- /investor-avatar/ (all variants)
- /investor-entrance/
- /investor-intelligence/
- /investor-one-pager/
- /investors/ (all versions v5-v16)
- /investors-ask-aether/ (all variants)
- /investors-onepager/ (and 3d variant)
- /aether-awakening/ (investor-facing)
- /gifts/ (investor gift pages)
- /chy-guardian/
- /aether-guardian/ (and template)
- /777-command-center/ (internal)
- /ceo-dashboard/ (internal)
- /triangle-os/ (internal)
- /functions/ (CF Workers)
- /_headers, /_redirects, /_worker.js (infrastructure)
- /assets/, /css/, /js/, /wp-content/ (static assets)
- /d1-migrations/ (infrastructure)
- /avatar-* pages (prototypes)
- /3d-* pages (prototypes/experiments)
- /pay-test-* (sandbox/test pages)
- /home-test* (test variants)
- /elementor-* (WP artifacts)

## Notes

- The banner has z-index 9999. Password gates use z-index 99999 to sit above it.
- Body needs `padding-bottom: 64px` to prevent content from being hidden behind the fixed footer.
- Mobile responsive: auto-height on screens under 600px, hides some nav links.
- The AETHER text has a pulsing glow animation.
