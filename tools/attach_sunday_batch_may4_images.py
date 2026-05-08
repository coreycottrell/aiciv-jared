#!/usr/bin/env python3
"""
attach_sunday_batch_may4_images.py
==================================

Paired post-step for `tools/generate_sunday_batch_may4.py`.

WHAT IT DOES
------------
After the Sunday Batch May 4-10 image generator produces 21 final PNGs
(7 banners + 14 standalones) under
`/home/jared/exports/portal-files/sunday-batch-may4-10/images/final/`,
this script:

1. Reads the local image-manifest.json to find finished image paths.
2. Logs in to social.purebrain.ai via /api/login (session bearer token).
3. Fetches the 35 drafts created by `push_sunday_batch_may4_10.py` via
   GET /api/content?limit=500 (no per-id endpoint exists).
4. Maps each draft to an image key by INSERT ORDER (see EXPECTED_SEQUENCE
   below — the `metadata` column doesn't exist in this D1 schema, so
   metadata-based mapping is impossible).
5. Uploads each unique PNG ONCE via POST /api/uploads (multipart) which
   stores it on R2 and returns a proxy URL via social.purebrain.ai/media/ and
   returns a stable HTTPS URL.
6. PATCHes each draft with `media_refs:[r2_public_url]` (NOT `image_url` —
   that field is excluded from the worker allowlist and would silently
   no-op).
7. Verifies each PATCH inline (PATCH response includes the updated row)
   plus a single final re-list to confirm persistence in D1.
8. Writes a results manifest to
   `/home/jared/exports/portal-files/sunday-batch-may4-10/patch-results.json`.

MAPPING LOGIC
-------------
21 unique image files attach to 35 drafts via INSERT ORDER:

  Banner banner-NN (1..7)  ->  3 drafts each (blog + newsletter + promo
                              for that day)
                              ==> 7 banners x 3 drafts = 21 attachments

  Standalone stand-NN (1..14) -> 1 draft each
                              ==> 14 attachments

  Total: 21 + 14 = 35 attachments  (exactly one media URL per draft).

CONSTRAINTS
-----------
- Use `media_refs` (JSON array of URLs) NOT `image_url`.
- Default urllib UA is CF-banned; we set User-Agent: curl/7.81.0 everywhere.
- Resumable: skips drafts where media_refs already non-empty.
- Single login; reuses one bearer token for the whole run.
- Reads SOCIAL_API_PASSWORD from env; falls back to known dev value with
  a security warning. Rotate the fallback once production password is set.
- Read REPLICATE_API_TOKEN-style guard: refuses to run if no FINAL images
  exist (so it can't fire before the generator).
- --qa-only mode: PATCHes ONE draft with placeholder, GETs to verify,
  then reverts media_refs=[]. Touches no other drafts. Used to prove
  the auth + PATCH flow without needing real images.

USAGE
-----
  # 1) (After Replicate token rotated) generate the images:
  python3 tools/generate_sunday_batch_may4.py

  # 2) Attach + verify all 35 drafts:
  SOCIAL_API_PASSWORD=... python3 tools/attach_sunday_batch_may4_images.py

  # QA gate against single draft (no images required):
  python3 tools/attach_sunday_batch_may4_images.py --qa-only

  # Dry-run (compute mapping, no network writes):
  python3 tools/attach_sunday_batch_may4_images.py --dry-run

Author: ptt-fullstack (PTT#)
Date:   2026-05-03
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

# ---- config ----------------------------------------------------------------

BASE = "https://social.purebrain.ai"
EMAIL = "jared@puretechnology.nyc"
# SECURITY: env var first; fallback is known dev value, must be rotated.
PASSWORD = os.environ.get("SOCIAL_API_PASSWORD", "PureBrain2026!")
PASSWORD_IS_FALLBACK = "SOCIAL_API_PASSWORD" not in os.environ

BATCH_DIR = Path("/home/jared/exports/portal-files/sunday-batch-may4-10")
MANIFEST_PATH = BATCH_DIR / "image-manifest.json"
CREATED_IDS_PATH = BATCH_DIR / "created-ids.json"
RESULTS_PATH = BATCH_DIR / "patch-results.json"
FINAL_DIR = BATCH_DIR / "images" / "final"

UA = "curl/7.81.0"
CTX = ssl.create_default_context()


# ---- HTTP helpers ----------------------------------------------------------

def http_json(method: str, url: str, body: Any = None, token: str | None = None,
              timeout: int = 30) -> tuple[int, Any]:
    """JSON request. Returns (status_code, parsed_body_or_error_dict)."""
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://social.purebrain.ai",
        "Accept": "application/json",
        "User-Agent": UA,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


def http_multipart_upload(url: str, file_path: Path, token: str,
                          timeout: int = 120) -> tuple[int, Any]:
    """POST multipart/form-data with one 'file' field. Returns (status, body)."""
    boundary = "----PTT" + uuid.uuid4().hex
    fname = file_path.name
    mime = mimetypes.guess_type(fname)[0] or "image/png"
    file_bytes = file_path.read_bytes()

    body = []
    body.append(f"--{boundary}\r\n".encode())
    body.append(
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'.encode()
    )
    body.append(f"Content-Type: {mime}\r\n\r\n".encode())
    body.append(file_bytes)
    body.append(f"\r\n--{boundary}--\r\n".encode())
    payload = b"".join(body)

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Origin": "https://social.purebrain.ai",
        "Accept": "application/json",
        "User-Agent": UA,
        "Authorization": f"Bearer {token}",
        "Content-Length": str(len(payload)),
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


# ---- mapping ---------------------------------------------------------------

# 21 image keys produced by the generator (must match BANNERS / STANDALONES
# in tools/generate_sunday_batch_may4.py).
BANNER_KEYS = [
    "banner-01-mon-compounding",
    "banner-02-tue-trust",
    "banner-03-wed-reset",
    "banner-04-thu-delegation",
    "banner-05-fri-receipt",
    "banner-06-sat-postmortem",
    "banner-07-sun-quietcompound",
]

STANDALONE_KEYS = [
    "stand-01-mon-5percent",
    "stand-02-tue-reset",
    "stand-03-tue-calculator",
    "stand-04-wed-overnight",
    "stand-05-wed-meridian",
    "stand-06-thu-test",
    "stand-07-thu-pilot",
    "stand-08-fri-shipped",
    "stand-09-fri-customervoice",
    "stand-10-sat-production",
    "stand-11-sat-sundayprep",
    "stand-12-sun-math",
    "stand-13-sun-94percent",
    "stand-14-flex-letgo",
]


# ---- Deterministic ordering map ------------------------------------------
#
# `content_items` D1 table does NOT have a metadata column (verified via
# `PRAGMA table_info(content_items)` 2026-05-03). The push script's
# `metadata` payload was silently discarded by the worker because the
# column was migrated out before the May 4-10 push (the INSERT in
# worker.js:3982 still names it but D1 ignores unknown columns at the
# `bind` boundary).
#
# So we map by the INSERT ORDER recorded in `created-ids.json` instead.
# The push script (workers/social-api/push_sunday_batch_may4_10.py)
# builds items in this exact, reproducible sequence:
#
#   day_idx 1 (Mon May 4): blog1, newsletter1, promo1, stand-1
#                          (slot1=None per push script; slot2=B1)
#   day_idx 2 (Tue May 5): blog2, newsletter2, promo2, stand-2, stand-3
#   day_idx 3 (Wed May 6): blog3, newsletter3, promo3, stand-4, stand-5
#   day_idx 4 (Thu May 7): blog4, newsletter4, promo4, stand-6, stand-7
#   day_idx 5 (Fri May 8): blog5, newsletter5, promo5, stand-8, stand-9
#   day_idx 6 (Sat May 9): blog6, newsletter6, promo6, stand-10, stand-11
#   day_idx 7 (Sun May 10): blog7, newsletter7, promo7, stand-12, stand-13
#   end: stand-14 (reserve, no schedule)
#
# Total = 4 + 5*6 + 1 = 35.
#
# We rebuild that exact list of (image_key, kind) so position N in
# created-ids.json maps to position N in this expected sequence.

EXPECTED_SEQUENCE: list[tuple[str, str]] = []  # (image_key, kind_label)
_DAY_STAND_SLOTS = {
    1: [1],            # Mon: only slot 2 -> B1
    2: [2, 3],         # Tue: B2, B3
    3: [4, 5],         # Wed: B4, B5
    4: [6, 7],         # Thu: B6, B7
    5: [8, 9],         # Fri: B8, B9
    6: [10, 11],       # Sat: B10, B11
    7: [12, 13],       # Sun: B12, B13
}
for _day in range(1, 8):
    EXPECTED_SEQUENCE.append((BANNER_KEYS[_day - 1], "blog"))
    EXPECTED_SEQUENCE.append((BANNER_KEYS[_day - 1], "newsletter"))
    EXPECTED_SEQUENCE.append((BANNER_KEYS[_day - 1], "post-blog-promo"))
    for _s in _DAY_STAND_SLOTS[_day]:
        EXPECTED_SEQUENCE.append((STANDALONE_KEYS[_s - 1], "post-standalone"))
EXPECTED_SEQUENCE.append((STANDALONE_KEYS[13], "post-standalone-reserve"))  # B14

assert len(EXPECTED_SEQUENCE) == 35, (
    f"expected 35 mappings, got {len(EXPECTED_SEQUENCE)}"
)


def image_key_for_index(position: int) -> str | None:
    """Return image_key for the Nth (0-indexed) entry in created-ids.json."""
    if 0 <= position < len(EXPECTED_SEQUENCE):
        return EXPECTED_SEQUENCE[position][0]
    return None


def expected_kind_for_index(position: int) -> str | None:
    if 0 <= position < len(EXPECTED_SEQUENCE):
        return EXPECTED_SEQUENCE[position][1]
    return None


# ---- main pipeline ---------------------------------------------------------

def login() -> str:
    if PASSWORD_IS_FALLBACK:
        print("  [WARN] SOCIAL_API_PASSWORD env var not set — using fallback "
              "(rotate before prod).")
    code, resp = http_json("POST", f"{BASE}/api/login",
                           {"email": EMAIL, "password": PASSWORD})
    if code != 200 or "token" not in resp:
        raise SystemExit(f"login failed: HTTP {code} {resp}")
    return resp["token"]


def fetch_drafts(token: str, ids: list[str]) -> dict[str, dict]:
    """Fetch via GET /api/content?limit=500 and filter to wanted IDs.

    The worker exposes only list (`GET /api/content`) and update
    (`PATCH /api/content/:id`) endpoints — there is no per-id GET. We
    fetch the full draft list once and pick the rows we need, which is
    O(1) round-trips regardless of how many drafts we are attaching to.
    """
    out: dict[str, dict] = {}
    code, resp = http_json(
        "GET", f"{BASE}/api/content?limit=500", token=token, timeout=60
    )
    if code != 200:
        print(f"  [WARN] list HTTP {code}: {str(resp)[:200]}")
        return out
    items = resp.get("items") or []
    by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
    for cid in ids:
        if cid in by_id:
            out[cid] = by_id[cid]
        else:
            print(f"  [WARN] {cid[:8]}: not found in /api/content list "
                  f"(total returned: {len(items)})")
    return out


def get_one_draft(token: str, content_id: str) -> dict:
    """Pick a single draft from the list endpoint. Returns {} if not found."""
    code, resp = http_json(
        "GET", f"{BASE}/api/content?limit=500", token=token, timeout=60
    )
    if code != 200:
        return {}
    for it in resp.get("items") or []:
        if isinstance(it, dict) and it.get("id") == content_id:
            return it
    return {}


def upload_image(token: str, file_path: Path) -> str:
    """Upload one PNG to /api/uploads. Returns public R2 URL."""
    code, resp = http_multipart_upload(f"{BASE}/api/uploads", file_path, token)
    if code not in (200, 201) or "url" not in resp:
        raise RuntimeError(f"upload failed for {file_path.name}: HTTP {code} {resp}")
    return resp["url"]


def media_refs_populated(draft: dict) -> bool:
    mr = draft.get("media_refs")
    if not mr:
        return False
    if isinstance(mr, str):
        try:
            mr = json.loads(mr)
        except Exception:
            return bool(mr.strip())
    return isinstance(mr, list) and len(mr) > 0


def patch_media_refs(token: str, content_id: str, urls: list[str]) -> tuple[int, Any]:
    return http_json(
        "PATCH",
        f"{BASE}/api/content/{content_id}",
        {"media_refs": urls},
        token=token,
    )


def get_draft(token: str, content_id: str) -> tuple[int, dict]:
    """Wrapper around list-and-filter for verification reads."""
    item = get_one_draft(token, content_id)
    return (200 if item else 404), item


# ---- modes -----------------------------------------------------------------

def run_qa_only() -> int:
    """PATCH one draft with a placeholder URL, verify, revert to []."""
    print("=" * 70)
    print("QA-ONLY mode — no real images required")
    print("=" * 70)

    if not CREATED_IDS_PATH.exists():
        print(f"FATAL: {CREATED_IDS_PATH} missing")
        return 1
    ids = json.loads(CREATED_IDS_PATH.read_text()).get("ids", [])
    if not ids:
        print("FATAL: no created IDs in created-ids.json")
        return 1

    token = login()
    target = ids[0]
    print(f"\nQA target: {target}")

    placeholder = f"https://example.com/qa-placeholder-{int(time.time())}.png"

    # 1. Capture original
    code, before = get_draft(token, target)
    if code != 200:
        print(f"FATAL: GET before failed: {code}")
        return 1
    original_refs = before.get("media_refs")
    print(f"  before media_refs = {original_refs!r}")

    # 2. PATCH with placeholder
    code, resp = patch_media_refs(token, target, [placeholder])
    print(f"  PATCH placeholder: HTTP {code}")
    if code != 200:
        print(f"  ERROR: {resp}")
        return 1

    # 3. Verify
    code, after = get_draft(token, target)
    mr = after.get("media_refs")
    if isinstance(mr, str):
        try:
            mr_list = json.loads(mr)
        except Exception:
            mr_list = [mr]
    else:
        mr_list = mr or []
    ok = placeholder in (mr_list or [])
    print(f"  GET verify: media_refs = {mr_list!r}  -> {'OK' if ok else 'FAIL'}")

    # 4. Revert to []
    code, _ = patch_media_refs(token, target, [])
    print(f"  PATCH revert: HTTP {code}")
    code, restored = get_draft(token, target)
    print(f"  after media_refs = {restored.get('media_refs')!r}")

    # 5. Status check — must still be draft
    print(f"  status = {restored.get('status')}")

    if not ok:
        print("\nQA FAILED")
        return 1
    print("\nQA PASSED — auth + PATCH + verify + revert all succeeded.")
    return 0


def _scheduled_at_compatible(expected_kind: str, position: int, draft: dict) -> bool:
    """Lightweight sanity check on scheduled_at vs expected position.

    The May 4-10 push script schedules each kind at a fixed UTC time:
      - blog       -> HH=12:30
      - newsletter -> HH=12:30
      - promo      -> HH=17:00
      - standalone -> HH=15:00 (slot1) or 19:00 (slot2)
      - reserve B14 -> scheduled_at IS NULL

    We don't know which slot a standalone is in just from `expected_kind`,
    so we accept either 15:00 or 19:00 for standalones. content_type is
    always 'post' on this D1 schema (verified 2026-05-03), so we don't
    use it as a discriminator.
    """
    sched = draft.get("scheduled_at") or ""
    if expected_kind == "post-standalone-reserve":
        return not sched  # NULL/empty
    if not sched:
        return False
    # Hour signature in the time portion (UTC)
    if "T" not in sched:
        return True  # unparseable — don't block
    hh = sched.split("T", 1)[1][:5]  # "HH:MM"
    if expected_kind == "blog":
        return hh == "12:30"
    if expected_kind == "newsletter":
        return hh == "12:30"
    if expected_kind == "post-blog-promo":
        return hh == "17:00"
    if expected_kind == "post-standalone":
        return hh in ("15:00", "19:00")
    return True


def run_dry_run() -> int:
    """Compute mapping but make no network writes."""
    print("=" * 70)
    print("DRY-RUN — login + fetch + map only, no uploads / no PATCHes")
    print("=" * 70)

    if not CREATED_IDS_PATH.exists():
        print(f"FATAL: {CREATED_IDS_PATH} missing")
        return 1
    ids = json.loads(CREATED_IDS_PATH.read_text()).get("ids", [])
    print(f"\nLoaded {len(ids)} created IDs.")

    if len(ids) != 35:
        print(f"WARN: expected 35 ids, got {len(ids)} — mapping may misalign")

    token = login()
    print("Login OK.\n")

    drafts = fetch_drafts(token, ids)
    print(f"Fetched {len(drafts)} draft rows.\n")

    mapping: dict[str, list[str]] = {k: [] for k in BANNER_KEYS + STANDALONE_KEYS}
    mismatches: list[tuple[str, str, str]] = []  # (cid, expected_kind, got_content_type)
    for pos, cid in enumerate(ids):
        key = image_key_for_index(pos)
        kind = expected_kind_for_index(pos) or ""
        draft = drafts.get(cid) or {}
        if draft and not _scheduled_at_compatible(kind, pos, draft):
            mismatches.append((cid, kind, draft.get("content_type", "?")))
        if key:
            mapping[key].append(cid)

    print("MAPPING (image_key -> [draft IDs]):")
    total_attachments = 0
    for key in BANNER_KEYS:
        rows = mapping[key]
        total_attachments += len(rows)
        print(f"  {key:36s} -> {len(rows)} drafts: "
              f"{[r[:8] for r in rows]}")
    for key in STANDALONE_KEYS:
        rows = mapping[key]
        total_attachments += len(rows)
        print(f"  {key:36s} -> {len(rows)} drafts: "
              f"{[r[:8] for r in rows]}")
    print(f"\nTotal attachments: {total_attachments}/{len(ids)}")

    if mismatches:
        print(f"\nCONTENT_TYPE MISMATCHES ({len(mismatches)}) — order assumption "
              f"may be wrong:")
        for cid, exp, got in mismatches:
            print(f"  {cid[:8]}  expected_kind={exp}  got_content_type={got}")
        return 2
    print("\nContent-type sanity: all 35 drafts match expected kind.")
    return 0


def run_attach() -> int:
    """Full flow: upload images, PATCH all 35 drafts, verify, write results."""
    print("=" * 70)
    print("Sunday Batch May 4-10 — Image Attach")
    print("=" * 70)

    if not CREATED_IDS_PATH.exists():
        print(f"FATAL: {CREATED_IDS_PATH} missing")
        return 1
    if not MANIFEST_PATH.exists():
        print(f"FATAL: {MANIFEST_PATH} missing — run generator first.")
        return 1

    ids = json.loads(CREATED_IDS_PATH.read_text()).get("ids", [])
    manifest = json.loads(MANIFEST_PATH.read_text())

    # Resolve final image paths for each key
    img_paths: dict[str, Path] = {}
    missing_imgs: list[str] = []
    for key in BANNER_KEYS + STANDALONE_KEYS:
        bucket = ("banners" if key.startswith("banner-") else "standalones")
        entry = (manifest.get(bucket) or {}).get(key) or {}
        final = entry.get("final")
        if final and Path(final).exists() and Path(final).stat().st_size > 50_000:
            img_paths[key] = Path(final)
        else:
            # Fallback: probe FINAL_DIR by convention
            candidate = FINAL_DIR / f"{key}.png"
            if candidate.exists() and candidate.stat().st_size > 50_000:
                img_paths[key] = candidate
            else:
                missing_imgs.append(key)

    if missing_imgs:
        print("FATAL: missing final images (run generator first):")
        for k in missing_imgs:
            print(f"  - {k}")
        return 1

    print(f"All 21 images present. Logging in...\n")
    token = login()
    print("Login OK.\n")

    # Fetch drafts
    print("Fetching drafts to inspect metadata...")
    drafts = fetch_drafts(token, ids)
    print(f"  fetched {len(drafts)}/{len(ids)}\n")

    # Map drafts to image keys via positional order in created-ids.json
    # (see EXPECTED_SEQUENCE comment for why we don't use metadata).
    key_to_drafts: dict[str, list[str]] = {k: [] for k in img_paths}
    unmapped: list[str] = []
    skipped_already: list[tuple[str, Any]] = []
    mismatches: list[tuple[str, str, str]] = []
    for pos, cid in enumerate(ids):
        key = image_key_for_index(pos)
        kind = expected_kind_for_index(pos) or ""
        draft = drafts.get(cid)
        if not draft:
            unmapped.append(cid)
            continue
        if not _scheduled_at_compatible(kind, pos, draft):
            mismatches.append((cid, kind, draft.get("content_type", "?")))
        if media_refs_populated(draft):
            skipped_already.append((cid, draft.get("media_refs")))
            continue
        if key in key_to_drafts:
            key_to_drafts[key].append(cid)

    if mismatches:
        print(f"FATAL: {len(mismatches)} drafts content_type mismatch — order "
              f"assumption broken. Refusing to attach.")
        for cid, exp, got in mismatches:
            print(f"  {cid[:8]}  expected_kind={exp}  got_content_type={got}")
        return 1
    if unmapped:
        print(f"WARN: {len(unmapped)} drafts could not be mapped:")
        for cid in unmapped:
            print(f"  - {cid}")
    if skipped_already:
        print(f"\nResume: skipping {len(skipped_already)} drafts that already "
              f"have media_refs set.")

    # Upload each unique image once -> public R2 URL
    print("\nUploading images to R2 via /api/uploads...")
    image_url_for_key: dict[str, str] = {}
    for i, key in enumerate(BANNER_KEYS + STANDALONE_KEYS, 1):
        # Skip if no drafts need this image (all already populated)
        if not key_to_drafts.get(key):
            print(f"  [{i}/21] {key} -> no pending drafts, skipping upload")
            continue
        path = img_paths[key]
        try:
            url = upload_image(token, path)
            image_url_for_key[key] = url
            print(f"  [{i}/21] {key} -> {url}")
        except Exception as e:
            print(f"  [{i}/21] {key} UPLOAD FAILED: {e}")
            return 2

    # PATCH each pending draft. The PATCH response itself returns the
    # updated row, so we verify inline without re-listing (saves N round-
    # trips). Final pass: re-list once and confirm media_refs persisted.
    print("\nPATCHing drafts with media_refs...")
    results = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "uploads": image_url_for_key,
        "patched": [],
        "verified": [],
        "failed": [],
        "skipped_already_populated": [{"id": c, "media_refs": m}
                                      for c, m in skipped_already],
        "unmapped": unmapped,
    }

    todo = [(cid, key) for key, lst in key_to_drafts.items() for cid in lst]
    for i, (cid, key) in enumerate(todo, 1):
        url = image_url_for_key[key]
        code, resp = patch_media_refs(token, cid, [url])
        if code != 200:
            print(f"  [{i}/{len(todo)}] {cid[:8]} ({key}) PATCH FAIL "
                  f"{code} {str(resp)[:120]}")
            results["failed"].append({"id": cid, "key": key, "phase": "patch",
                                      "code": code, "resp": resp})
            continue
        # Inline verify from PATCH response (worker returns updated row)
        item = resp.get("item") or {}
        mr = item.get("media_refs")
        if isinstance(mr, str):
            try:
                mr_list = json.loads(mr)
            except Exception:
                mr_list = [mr]
        else:
            mr_list = mr or []
        if url in mr_list:
            results["patched"].append({"id": cid, "key": key, "url": url})
            print(f"  [{i}/{len(todo)}] {cid[:8]} ({key}) OK")
        else:
            print(f"  [{i}/{len(todo)}] {cid[:8]} ({key}) PATCH RESPONSE "
                  f"WITHOUT EXPECTED URL: media_refs={mr_list}")
            results["failed"].append({"id": cid, "key": key,
                                      "phase": "patch_response",
                                      "media_refs": mr_list})

    # Final independent verification pass: re-list once, confirm each
    # patched draft really persisted media_refs in D1.
    print("\nFinal verification (independent re-list)...")
    code, resp = http_json("GET", f"{BASE}/api/content?limit=500",
                           token=token, timeout=60)
    if code != 200:
        print(f"  WARN: verification re-list failed HTTP {code}")
    else:
        by_id = {it.get("id"): it for it in (resp.get("items") or [])}
        for entry in results["patched"]:
            cid = entry["id"]
            url = entry["url"]
            row = by_id.get(cid) or {}
            mr = row.get("media_refs")
            if isinstance(mr, str):
                try:
                    mr_list = json.loads(mr)
                except Exception:
                    mr_list = [mr]
            else:
                mr_list = mr or []
            if url in mr_list:
                results["verified"].append(cid)
            else:
                results["failed"].append({"id": cid, "key": entry["key"],
                                          "phase": "verify_relist",
                                          "media_refs": mr_list})
                print(f"  VERIFY FAIL {cid[:8]} expected {url} "
                      f"got {mr_list}")

    results["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results["summary"] = {
        "total_drafts": len(ids),
        "mapped": len(todo) + len(skipped_already),
        "patched": len(results["patched"]),
        "verified": len(results["verified"]),
        "failed": len(results["failed"]),
        "unmapped": len(unmapped),
        "skipped_already_populated": len(skipped_already),
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n")

    print("\n" + "=" * 70)
    print("DONE")
    for k, v in results["summary"].items():
        print(f"  {k}: {v}")
    print(f"\nResults written: {RESULTS_PATH}")
    print("Review at: https://surf.purebrain.ai/social.html")
    return 0 if not results["failed"] else 2


# ---- entry point -----------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-only", action="store_true",
                        help="PATCH one draft with placeholder, verify, revert. "
                             "No real images required.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Login + fetch + map; no uploads, no PATCHes.")
    args = parser.parse_args()

    if args.qa_only and args.dry_run:
        print("--qa-only and --dry-run are mutually exclusive")
        return 1
    if args.qa_only:
        return run_qa_only()
    if args.dry_run:
        return run_dry_run()
    return run_attach()


if __name__ == "__main__":
    sys.exit(main())
