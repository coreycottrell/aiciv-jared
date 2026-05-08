# Batch Banner LinkedIn-Safe Shift Fix

**Date**: 2026-04-21
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Batch-fixed 28 blog/content banners on social.purebrain.ai to ensure text visibility in LinkedIn's center-crop.

## Method
- PIL shift: crop left edge, paste shifted right, fill left margin with #080a12
- Shift amount: 4.2% of image width (~100px for 2400w, ~45px for 1080w)
- Upload fixed image to R2 via POST /api/uploads
- Update content item media_refs via PATCH /api/content/:id

## API Details
- Login: POST /api/login returns {"status": ..., "token": ...}
- List: GET /api/content?limit=500&status=draft (also scheduled, pending)
- Upload: POST /api/uploads (multipart form-data) returns key/url
- Update: PATCH /api/content/:id with {"media_refs": "new_url"}

## Gotchas
- Some items have empty media_refs arrays [] -- these have no image, skip
- One item had double-encoded JSON string for media_refs ("[\\"url\\"]") -- treat as empty/skip
- media_refs field can be: string URL, JSON array string, or empty array
- Always convert RGBA to RGB before saving JPEG
- 0.5s delay between items prevents rate limiting

## Results
- 35 total items (33 draft, 2 scheduled)
- 28 successfully fixed
- 7 had no media (empty arrays)
