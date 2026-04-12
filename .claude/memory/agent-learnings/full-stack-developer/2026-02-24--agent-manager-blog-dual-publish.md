# Agent Manager Blog Dual Publish: "Your Next Direct Report Won't Be Human"

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published blog post "Your Next Direct Report Won't Be Human - And That Changes Everything" to both WordPress sites.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/your-next-direct-report-wont-be-human/ (Post ID: 879)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/02/24/your-next-direct-report-wont-be-human/ (Post ID: 1195)

## Media IDs

- purebrain.ai: Media ID 878 (your-next-direct-report-wont-be-human-banner.jpg)
- jareddsanborn.com: Media ID 1194

## Category IDs Used

- purebrain.ai: Category 5 = "AI Strategy", Category 2 = "AI Insights"
- jareddsanborn.com: Category 13 = "AI Strategy", Category 9 = "AI Insights"

## WordPress Auth Reminder

- purebrain.ai: user=Aether, password=PUREBRAIN_WP_APP_PASSWORD
- jareddsanborn.com: user=AetherPureBrain.ai (NOT "jared"), password=WORDPRESS_APP_PASSWORD
  - WORDPRESS_USER=AetherPureBrain.ai is in .env
  - Password has spaces - use --user "AetherPureBrain.ai:u3GO 3dvG..." not variable expansion

## Template Handling

- purebrain.ai: template field works fine in JSON POST body ("elementor_canvas")
- jareddsanborn.com: template field throws "Invalid parameter(s): template" - must omit it entirely
  - JDS posts look fine without template field

## Google Drive Upload

- Uploaded banner to folder ID 18aMzlXlJnXQTZmaEScNWLD2Td-OfISFU (002. Marketing Training)
- Drive File ID: 1BdFzdLWIyHZ5XzDawTgq3XgplTTyGXlG
- Used gdrive_manager.upload_file(local_path, folder_id, new_name) directly in Python (not CLI upload command which needs drive_path format)

## Verification (All Passed)

- [x] HTTP 200 on https://purebrain.ai/your-next-direct-report-wont-be-human/
- [x] HTTP 200 on https://jareddsanborn.com/2026/02/24/your-next-direct-report-wont-be-human/
- [x] Status = "publish" on both sites
- [x] Featured media ID set on both posts
- [x] #awakening CTA link present in footer
- [x] pt-social-share social icons present
- [x] blog-cta-block CTA block present
- [x] No test page links in either post
- [x] Google Drive banner uploaded (folder 002)

---

**End of Memory**
