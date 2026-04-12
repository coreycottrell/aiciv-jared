# Pure Technology Team Dossier Research

**Date**: 2026-02-23
**Agent**: web-researcher
**Type**: synthesis
**Topic**: Pure Technology / Pure Marketing Group team members - A/B/C delegation framework
**Confidence**: high (sourced from official company team page + LinkedIn + business databases)

---

## Context

Jared shared a Google Drive folder for team bios/resumes but it requires authentication. Built complete dossier from public sources instead. Drive folder needs service account access grant to enable automated file downloads.

---

## Key Findings

### Team Structure (19 identified members)

**Executive Leadership**:
- Jared Sanborn - CEO/Founder
- Nathan Olson - President (PMG)
- Matthew Keough - CIO (Pure Technology)
- Melanie Salvador - Vice Chairman/Deputy CEO
- Mike Daser PHRi - People/HR

**Sales**:
- Baruch Santana - Business Development (NYC, entertainment background)
- John Smith - VP of Sales

**Marketing**:
- Phil Bliss - Marketing (Canada-based)
- Robert Orlowski - Marketing (NJ, freelance/consulting basis)
- Moises Guerra - Social Media Specialist

**Content**:
- John Paris - Content

**Technology**:
- Timothy "Brill" DeVore - CTO (Columbus OH)
- Emmanuel Akinleye - Web Developer (NJ, joined Dec 2024)

**Web3**:
- Russell Korus - Web3 (EZ365 co-founder, TEDx speaker, blockchain expert)

**Operations**:
- Natasha Carrasco - Operations Manager
- Ashley Tom - Client Success

**Philippines Team**:
- Rodelina P. - Social
- Arlene T. - Social (confirmed Aether collaborator from prior session)

**Specialized**:
- Akande F. - SEO
- Rose F. - Video

### Google Drive Access Pattern

To access a private Drive folder shared by a human:
1. The folder must be shared with the service account: `aether-drive-access@aether-integration.iam.gserviceaccount.com`
2. The `tools/gdrive_manager.py` tool can then list and download files
3. OAuth token (`oauth-token.json`) would give full access as the account owner - but it doesn't exist in `.credentials/`
4. Web fetch cannot bypass Google auth - returns 302 redirect to login page

### Key Collaboration Pattern

Aether already has an established pattern of creating task lists for Arlene T. (Philippines social team). This should be extended to other team members as automation expands.

---

## When to Apply

- Any session where Jared asks "who should handle X?" - route to this dossier
- When building automation that involves team handoffs
- When creating content briefs that need human execution (route to John Paris, Arlene, Rodelina)
- When technical builds need handoff to Emmanuel or Timothy DeVore
- When sales tasks need routing to Baruch or John Smith

---

## Sources

- https://puremarketing.ai/team/
- https://puremarketing.ai/about-us/
- https://theorg.com/org/pure-technology/org-chart
- https://www.linkedin.com/in/nathan0lson/
- https://www.linkedin.com/in/baruchsantana/
- https://rocketreach.co/nathan-olson-email_752431854
- https://www.zoominfo.com/p/Moises-Guerra/8683512843
- https://www.zoominfo.com/p/Emmanuel-Akinleye/11646306678
- https://coinagenda.com/russell-korus/
- https://castlehr.wpcomstaging.com/team-details/mike-daser-phri/
- Deliverable: `/home/jared/projects/AI-CIV/aether/exports/pure-tech-team-dossier.md`
