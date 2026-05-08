# 2026-05-03 — Sunday Batch May 4-10 Image Attach Pattern

**Type**: technique + gotcha
**Topic**: PATCH `media_refs` on social.purebrain.ai drafts after FLUX
generation, with positional mapping and shared-banner economics.

---

## What the script does

Tool: `tools/attach_sunday_batch_may4_images.py` (paired post-step for
`tools/generate_sunday_batch_may4.py`).

For 21 generated images → 35 drafts:
1. Login → bearer token (UA = curl/7.81.0; default urllib UA = CF-banned).
2. Upload each unique PNG ONCE via `POST /api/uploads` (multipart form).
   Worker stores it in R2 bucket `purebrain-uploads` and returns a public
   URL on `pub-8f8cf3b34e354e108283ed11c59db125.r2.dev`.
3. PATCH each draft with `media_refs: [r2_url]` — never `image_url`.
4. Inline-verify from PATCH response (worker returns full updated row).
5. Final independent re-list to confirm persistence.

## CRITICAL gotchas

### 1. `metadata` column does NOT exist on D1 `content_items`
**Verified via `PRAGMA table_info(content_items)` 2026-05-03.**

The push script (`workers/social-api/push_sunday_batch_may4_10.py`) sent
`metadata: {kind, day, blog_index, ...}` in the create payload. The
worker's INSERT statement at `worker.js:3982` still names `metadata` as a
column, but D1 has it migrated out — meaning the bind silently drops it
(D1 doesn't fail on unknown column names in `bind` for CURRENT schemas;
only the `prepare()` parser cares). So **all 35 drafts have no usable
metadata server-side** for resolving image keys.

Fix: map by **insert order in `created-ids.json`** instead. The push
script builds items in a deterministic per-day pattern (blog →
newsletter → promo → standalone-A → standalone-B). Position N in the
ids array = position N in the expected sequence. See `EXPECTED_SEQUENCE`
in the attach script.

Defense-in-depth: a `_scheduled_at_compatible` check verifies the row's
`scheduled_at` UTC hour matches what the position should look like
(blog/newsletter=12:30, promo=17:00, standalone=15:00 or 19:00, B14
reserve=null). 35/35 verified locally against D1.

### 2. content_type is always 'post' on this schema
The push script set `content_type='blog'` / `'newsletter'`, but D1 stores
all 35 as `'post'`. Don't use content_type as a discriminator.

### 3. There is no `GET /api/content/{id}`
Worker exposes:
- `GET /api/content` (list, optional `?status=` and `?limit=` filters)
- `GET /api/content/team`
- `GET /api/content/ready`
- `PATCH /api/content/{id}`

For per-id reads, fetch `?limit=500` and filter client-side.

### 4. `media_refs` is the field, NOT `image_url`
PATCH allowlist (`worker.js:4031`) includes
`body, media_refs, scheduled_at, status, content_type, title, ...`
but NOT `image_url` — it would silently no-op.

`media_refs` is JSON-encoded array of URLs (D1 stringifies array input
automatically; comes back as `'["..."]'`). Pass an array; the worker
calls `JSON.stringify` on it.

### 5. UA must be non-default
Default Python `urllib` UA → CF 1010 (browser_signature_banned, HTTP 403).
Set `User-Agent: curl/7.81.0` on every request.

### 6. /api/login has heavy rate limit
After 1-2 retries you hit `429 too many login attempts`. Window is in
the minutes range — long enough to block local debug loops. Single
login per script run; reuse the token.

## Hosting decision: R2 via /api/uploads

Two viable paths existed:
- **Inline `media_base64` on PATCH** (worker uploads to R2 internally
  and overwrites media_refs on that single draft). Simple for 14
  standalones (1:1) but bad for shared banners (need same URL on 3
  drafts each — would re-upload the same banner 3 times).
- **`POST /api/uploads`** → multipart upload → returns a stable public
  R2 URL → then PATCH each draft with that URL. **One upload per unique
  image**, 35 PATCHes. Cheaper, simpler reasoning, easier to verify.

Chose `POST /api/uploads`. Total ops: 21 uploads + 35 PATCHes + 1
verification re-list = 57 round-trips for the full attach.

## Mapping logic (the cheat sheet)

```
21 unique images -> 35 drafts:

  banner-01..07  -> attaches to (blog, newsletter, promo) for that day = 3 drafts each
  stand-01..14   -> attaches to its single standalone post

  Position-in-created-ids.json -> Image key:
    0: blog1, 1: newsletter1, 2: promo1, 3: stand1
    4: blog2, 5: newsletter2, 6: promo2, 7: stand2, 8: stand3
    9: blog3, 10: newsletter3, 11: promo3, 12: stand4, 13: stand5
    ... (5 per day Tue-Sun)
    34: stand14 (B14 reserve, no schedule)
```

## Modes

- `--qa-only` — PATCH 1 draft with placeholder, verify in re-fetch,
  revert to `[]`, status check confirms `draft`. **VERIFIED LIVE
  2026-05-03 against `3d8a0bde-64eb-4f9a-8361-015f90f4e80d`** —
  HTTP 200 round-trip, placeholder appeared, revert restored, status
  unchanged. Auth + PATCH path is gold.
- `--dry-run` — login + list + map; print 21-key → drafts table; no
  uploads or writes.
- (default) — full upload + PATCH + verify of all 35.

## Security notes (flagged for security-engineer-tech rotation)

1. Hardcoded password fallback (line: `PASSWORD = os.environ.get("SOCIAL_API_PASSWORD", "PureBrain2026!")`).
   Same pattern exists in `push_sunday_batch_may4_10.py` (line 24).
   Both must be rotated and the fallback removed once
   `SOCIAL_API_PASSWORD` is set everywhere.
2. No login throttling visible at app layer (only CF UA filter). 429
   suggests CF rate-limit rule exists, but it's aggressive enough that
   a few accidental retries lock out for minutes — fine for security,
   awful for batch ops debug. Document the 1-shot login pattern.

## Reusable bits for future content-attach work

- `image_key_for_index(position)` — positional mapping
- `_scheduled_at_compatible(kind, pos, draft)` — UTC-hour sanity gate
- `http_multipart_upload(url, file_path, token)` — manual urllib
  multipart (no `requests` dep)
- `patch_media_refs(token, content_id, urls)` — one-shot helper

## Outcome

Script written, QA passed (live PATCH+revert against draft
3d8a0bde...), mapping verified against D1 (35/35, 0 mismatches).
**NOT EXECUTED** — Replicate token still expired, no images yet.
Single command after rotation:
`SOCIAL_API_PASSWORD=... python3 tools/attach_sunday_batch_may4_images.py`
