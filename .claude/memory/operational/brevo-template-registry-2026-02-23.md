# Brevo Template Registry - Complete as of 2026-02-23

## Template IDs
| ID | Name | Flow | Status |
|----|------|------|--------|
| 1-12 | Neural Feed + PureBrain purchase | Existing flows | Active |
| 13 | Audit Debrief | Audit Nurture (List 4) | Active |
| 14 | Tool vs Partner | Audit Nurture (List 4) | Active |
| 15 | Week in Practice | Audit Nurture (List 4) | Active |
| 16 | Direct Ask | Audit Nurture (List 4) | Active |
| 17 | Awakening Reframe | Pricing Intent (event trigger) | Active |
| 18 | Objection Handler | Pricing Intent (event trigger) | Active |
| 19 | We Noticed You've Been Quiet | Re-engagement (45-day inactive) | Active |
| 20 | What Would Bring You Back | Re-engagement (45-day inactive) | Active |
| 21 | Last Chance Sunset | Re-engagement (45-day inactive) | Active |

## Config Files
- `config/audit_nurture_template_ids.json` - IDs 13-16
- `config/brevo_automation_template_ids.json` - IDs 17-21
- `config/post_purchase_brevo_config.json` - Purchase flow config

## Reply-To
All templates 13-21 fixed to: purebrain@puremarketing.ai

## Automation Status (as of 2026-02-23)
- Brevo Playwright automation BLOCKED by Brevo platform 500 errors
- Script saved: `tools/brevo_build_4_automations_v2.py`
- Jared may need to build automations manually in Brevo dashboard
