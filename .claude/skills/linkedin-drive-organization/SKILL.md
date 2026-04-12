---
name: linkedin-drive-organization
description: Google Drive folder organization SOP for LinkedIn Operations — where to file content at every stage of the pipeline
trigger: filing to Drive, Google Drive organization, where to file, content filing, Drive structure
agents: [dept-marketing-advertising, linkedin-writer, linkedin-specialist, content-specialist, blogger]
---

# LinkedIn Drive Organization Skill

## Purpose

This skill provides the canonical filing rules for the LinkedIn Operations Google Drive folder. Every agent that creates LinkedIn content must know where to file it.

## Drive Root

**LinkedIn Operations** folder ID: `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`

## Weekly Content Engine Flow

```
SUNDAY: Create all content -> File to Pending Approval -> Column G = "Draft" (red)
MONDAY: Jared approves -> Move to Final -> Column G = "Final" (yellow)
DAILY: Publish -> Move to Live folder -> Column G = "Live" (green)
```

## Master Folder Routing (Locked 2026-04-05)

| # | Content Type | Folder | Folder ID |
|---|-------------|--------|-----------|
| 1 | Overnight distribution strategies | Blog Newsletter Distribution Strategies | `1PH13K9qHL7Y61ePFoT8JxmeHIMOKB0Ak` |
| 2 | Overnight blog/site analysis | Blog Newsletter Analysis | `1Kv7luobZJpXBaJ2GwvTpl1RAV5Uyza7O` |
| 3 | Overnight LinkedIn strategies | Linkedin Strategy | `1krOCvWZfWGLEPqQ0c-nYiQmtnVjE-aH1` |
| 4 | Aether AI Influencer info | Aether the AI Influencer | `1CkqoiLEJZwRJ16BLsnAFeH0ga6_w5JiM` |
| 5 | Pending approval (Sunday delivery) | Content Drafts (Pending Approval) | `1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz` |
| 6 | Approved/Final | Content Approved (Final) | `1lNl8zeI4Uprhh0awvKjp3LTf7Z-dQLt7` |
| 7 | Live blog/newsletter posts | Blog Posts Live | `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv` |
| 8 | Live regular LinkedIn posts | Regular LinkedIn Posts Live | `1fy9QKMKw_ulVIRWhMEmdP_Li4d6GDCl_` |
| 9 | Content calendars | Content Calendar | `1-KFSFp89A4iVibJ5Q0sPXpk6elZXExF_` |
| 10 | Analytics/tracking spreadsheet | Analytics & Performance | `1ucpRi0kQs_i-624nrqWGCPj4_c_hmqX6` |
| 11 | Skills/SOPs | Skills | `1ACyxaXI9DwJHg6PZt3pV5ccne9lUL0hJ` |
| 12 | Profile viewing strategy + script | Profile Viewing Strategy | `1hEcL49OKvPLcOQzmFqGl--bnccSyrbD_` |
| 13 | Design training (ALL) | Content Training | `1CjE5qC4UubKqAsCwBJSH4s3oCORRWrbV` |

### Additional Folders

| Folder | ID | Purpose |
|--------|----|---------|
| Content Posted (Live) parent | `1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx` | Contains Blog Posts Live + LinkedIn Posts Live |
| Training - Blog-to-LinkedIn Flow | `1YR_G98g3EyyOT6hKoOExNKLBgQ4aAi4D` | Blog repurposing training |
| Targeting Training | `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3` | ICP profiles |
| Comment Strategy & Targets | `12De54gpykzE5d4Ks3w7OoqC06DtbtH5E` | Commenting playbooks |
| comments | `1jC6KfTJue9Y_Sl5UH3uZxRSgTdmqAKj6` | Daily comment logs |
| Images & Carousels | `1AQLffcLZs1DN30XYjrxo-UwB-_yaLcGK` | Standalone image assets |
| Reddit Push | `1pbENzoJYid5F7mKiFYWQyg7lGJVi5VD_` | Reddit distribution |

## Spreadsheet Lifecycle

**Spreadsheet**: `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`
**Location**: Analytics & Performance folder (`1ucpRi0kQs_i-624nrqWGCPj4_c_hmqX6`)

- **Column F** = post text (clipped)
- **Column G** = Draft (red) > Final (yellow) > Live (green)

## Filing by Pipeline Phase

### Creation (Sunday Batch)
**Where**: `Content Drafts (Pending Approval)/YYYY-MM-DD -- [Post Title]/`
Include: post-details.md, post copy, image versions, blog article, bluesky thread.
Clip text to Column F. Set Column G = "Draft".

### Approval (Monday)
**Where**: Move to `Content Approved (Final)/`
Column G = "Final".

### Published (Daily)
**Where**: Move to respective Live folder.
- Blog/newsletter -> `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
- Regular LinkedIn -> `1fy9QKMKw_ulVIRWhMEmdP_Li4d6GDCl_`
Column G = "Live". Each post gets own subfolder with images + text.

### Documentation (48-72h Post-Publish)
Add metrics to post-details.md in the Live folder.

### Training Extraction
New learnings -> `Content Training/` (`1CjE5qC4UubKqAsCwBJSH4s3oCORRWrbV`).
ALL design training (FLUX, 3D, static, Gleb) goes here -- no exceptions.

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Post subfolder | `YYYY-MM-DD -- [Title]` | `2026-04-07 -- AI Memory Changes Everything` |
| Post image | `linkedin-[topic]-YYYY-MM-DD-v[N].png` | `linkedin-ai-memory-2026-04-07-v1.png` |
| Post text | `linkedin-[topic]-post-YYYY-MM-DD.md` | `linkedin-ai-memory-post-2026-04-07.md` |
| Blog article | `blog-[topic]-YYYY-MM-DD.md` | `blog-ai-memory-2026-04-07.md` |
| Blog banner | `blog-banner-[topic]-YYYY-MM-DD.png` | `blog-banner-ai-memory-2026-04-07.png` |
| Bluesky thread | `bluesky-thread-[topic]-YYYY-MM-DD.md` | `bluesky-thread-ai-memory-2026-04-07.md` |

### Rules
- `--` (double dash with spaces) in folder names
- `-` (single hyphen) in file names
- Always YYYY-MM-DD dates
- Version images with `-v[N]`
- Pending Approval cleaned within one week
- Live folders = permanent archive, never delete

## Full SOP Reference

- Google Drive: LinkedIn Operations / `DRIVE-ORGANIZATION-SOP.md` (ID: `1xZ5eVF26iQaBcJ30upGVaba2ybSOTgCz`)
- Local: `.claude/skills/linkedin-drive-organization/SKILL.md`
