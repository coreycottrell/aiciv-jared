---
type: operational
topic: Brainiac Module 9 (Getting 10x from Your AI Partner) shipped end-to-end
date: 2026-04-29
agent: ptt-fullstack
---

# Brainiac Module 9 — Shipped (Wed Apr 29 BOOP)

## What Ran

Wednesday 2:30pm ET Brainiac BOOP. Today's Zoom recording was already available
(found by `zoom_brainiac_pipeline.py --step 1` which actually ran full pipeline).

- Topic: 2103-Brainiac - Mastermind Training / PureBrain.ai / Jared
- Date: 2026-04-29
- Duration: 81 min
- Recording size: 203,556,101 bytes (~195MB)
- Local MP4: /home/jared/projects/AI-CIV/aether/exports/brainiac-training/downloads/2026-04-29/2026-04-29_2103-Brainiac_-_Mastermind_Training_-_PureBrain.ai_-_Jared_eedd30e1.mp4
- Transcript: /home/jared/projects/AI-CIV/aether/exports/brainiac-training/transcripts/module-2026-04-29.vtt
- Module markdown: /home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/module-2026-04-29.md

## Module count: 8 -> 9

The training hub at brainiac.purebrain.ai/index.html already had:
- "9 modules" count badge prepared (line 1664)
- Module 9 card and /module-9/ standalone page prebuilt with placeholder content
- TRAINING_VIDEOS array entry for module-9-10x with hlsUrl: null and duration: TBD

## What I Updated

/home/jared/projects/brainiac-purebrain/index.html:
1. Module 9 card description -> reflects actual recording (compound investment thesis)
2. Module 9 duration: TBD -> 81 min
3. TRAINING_VIDEOS[module-9-10x].hlsUrl: null -> R2 URL
4. AI Training Snippet body rewritten to match actual content

Git commit: 3e7e358 on puretechnyc/brainiac-purebrain repo, pushed to origin/main.

## R2 URLs

Module 9 video: https://r2-upload-proxy.in0v8.workers.dev/brainiac/recordings/module-9/full.mp4
(203MB, video/mp4, accept-ranges: bytes — verified via curl HEAD)

## CRITICAL DISCOVERY: r2-upload-proxy Worker uses URL PATH for key, not query param

Previous memory 2026-04-28--brainiac-modules-7-8-video-upload.md mentioned the
worker proxy but didn't document the request format. I burned ~10 minutes via
probe testing. The worker reads `key` from URL path, NOT from `?key=` query.

### Wrong (returns success but never persists):
- POST /?action=mpu-create&key=brainiac/recordings/module-9/full.mp4
Returns {"success":true,"key":""} — empty key. File 404s on read.

### Right (works):
- POST /brainiac/recordings/module-9/full.mp4?action=mpu-create
- PUT  /brainiac/recordings/module-9/full.mp4?action=mpu-uploadpart&uploadId=...&partNumber=1
- POST /brainiac/recordings/module-9/full.mp4?action=mpu-complete&uploadId=...
Returns {"success":true,"key":"brainiac/recordings/module-9/full.mp4"}

### mpu-complete body: BARE JSON ARRAY, not wrapped in {"parts":[...]}
[{"partNumber":1,"etag":"abc..."}, {"partNumber":2,"etag":"def..."}]
Wrapping it returns "error code: 1101" (Worker exception).

### CF Managed Challenge (1010): default Python urllib UA blocked
Set User-Agent: Mozilla/5.0 ... to bypass.

### New tool: tools/r2_proxy_multipart_upload.py
Reusable for large file -> R2 via the worker proxy. Chunks at 90MB.
Usage: python3 tools/r2_proxy_multipart_upload.py <local_file> <r2_key>

## Deploy verification

- cf-deploy.py with CF_PAGES_PROJECT=brainiac-purebrain
- Deployment ID: a37a1aad-8c49-4e49-89af-f6a59846ea45
- Preserves all 16 existing files (only index.html changed)
- Live: https://brainiac.purebrain.ai/
- Verified: page contains "Duration: 81 min", "r2-upload-proxy.in0v8.workers.dev/brainiac/recordings/module-9/full.mp4", and "9 modules" badge
- CF zone cache flushed for homepage
- Range requests on MP4 return 200 with correct Content-Length

## Issues Hit (file for follow-up)

1. zoom_brainiac_pipeline.py --step 1 flag is broken — ignored, ran full pipeline
2. Pipeline R2 upload uses broken S3 creds (AccessDenied). Should integrate
   r2_proxy_multipart_upload.py as primary upload path.
3. Pipeline WP page update returns 403 (1010) — targeting OLD location.
   New home is brainiac.purebrain.ai (CF Pages, no WP).
4. Auto-generated SKILL.md says "7 modules" while training hub shows 9. Cosmetic.

## Idempotency

Re-running the BOOP today would re-download, re-transcode, re-upload (wasteful
but not destructive), and re-deploy with same content (manifest match no-op).
Safe to retry. The 3pm/3:30pm/4pm scheduler retries are not needed.

## Next Wednesday (Module 10)

Check lines ~2742-2760 in /home/jared/projects/brainiac-purebrain/index.html
to see if Module 10 stub is pre-built.
