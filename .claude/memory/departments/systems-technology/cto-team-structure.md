# CTO Team Structure — PERMANENT DIRECTIVE
**Established**: 2026-03-06
**Authority**: Jared (CEO) — Permanent Lock
**CTO enforces this at all times**

---

## Two Separate Teams — NEVER Crossover

The Systems & Technology department operates as TWO fully independent product teams.
They are isolated by domain and never share specialists unless explicit cross-reference
for architecture cogency is needed.

---

## Team A: Website Team (purebrain.ai)

**Domain**: The public-facing marketing and sales website
**URL**: https://purebrain.ai
**Owner**: CTO → Website Team Lead

### Scope
- All pages: landing pages, blog posts, pricing pages, tier pages
- WordPress CMS: plugins, themes, Elementor content
- SEO / GEO / AIO optimizations on purebrain.ai
- Calculators, comparison pages, lead capture pages
- Blog publishing pipeline
- Public-facing PayPal/payment integration pages (sandbox + production)
- Invitation / waitlist pages

### Specialists (Website Team)
| Role | Responsibility |
|------|---------------|
| Full-Stack Developer (Web) | WordPress pages, HTML/CSS/JS, plugin builds |
| QA Engineer (Web) | Visual QA, browser-vision-tester for purebrain.ai |
| SEO Specialist | On-page SEO, GEO/AIO, schema markup |
| Content Engineer | Blog deployment, FAQ sections, content formatting |
| Security Engineer | WAF rules, CSP headers — site surface only |

---

## Team B: Portal Team (app.purebrain.ai)

**Domain**: The logged-in product portal and application
**URL**: https://app.purebrain.ai
**Owner**: CTO → Portal Team Lead

### Scope
- Portal authentication (login, OAuth, birth pipeline)
- Chat/terminal interface and AI streaming
- Portal dashboard: calendar, email, team, fleet
- Referral system, settings, user account management
- Container/session management (witness birth pipeline)
- Portal demo video, onboarding flows
- app.purebrain.ai Netlify deployment

### Specialists (Portal Team)
| Role | Responsibility |
|------|---------------|
| Full-Stack Developer (Portal) | Portal features, API integrations, React/JS |
| QA Engineer (Portal) | E2E flow testing, auth flows, chat streams |
| DevOps Engineer | Netlify deploys, container pool, Cloudflare |
| Security Engineer | OAuth security, token management, session hardening |
| Integration Engineer | Witness birth pipeline, external API contracts |

---

## Rules of Engagement

1. **No crossover by default** — A task touching purebrain.ai goes to Team A. A task touching app.purebrain.ai goes to Team B. This is non-negotiable.

2. **Cross-reference exception** — Teams may consult each other ONLY when a feature requires architectural alignment (e.g., a pricing page links to a portal flow). This is reference/consultation only — each team still builds their side independently.

3. **Routing logic for Aether**:
   - "Update the pricing page" → Team A (Website)
   - "Fix the chatbox in the portal" → Team B (Portal)
   - "The blog post is broken" → Team A (Website)
   - "The login is failing" → Team B (Portal)
   - "Payment sandbox page" → Team A (Website, page688/689 are on purebrain.ai)
   - "Birth pipeline / witness" → Team B (Portal)

4. **Each team has its own security engineer** so a website security fix never bleeds into portal code and vice versa.

5. **Sprint planning is separate** — Team A and Team B have independent roadmaps and sprints. The CTO oversees both but does not merge them.

---

## CTO Oversight Model

```
Jared (CEO)
    │
   CTO
  ┌──┴──┐
Team A  Team B
(Web)  (Portal)
```

The CTO attends both teams' standups, reviews architecture decisions, and escalates blockers to Jared. Team leads handle day-to-day delegation internally.

---

## History
- 2026-03-06: Structure established per Jared's directive
- Replaces prior single-team model where web and portal work was mixed
