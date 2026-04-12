# Mux Video Platform: Complete Setup Guide

**Prepared for**: purebrain@puremarketing.ai
**Date**: 2026-02-28
**Purpose**: Step-by-step Mux onboarding, API integration, and embed code reference

---

## Part 1: Account Signup

### Signup URL
```
https://dashboard.mux.com/signup
```

### What Is Required
- Email address (use: purebrain@puremarketing.ai)
- Password
- No credit card required to start — Mux explicitly states "No credit card required to start using Mux"

### After Signup
- You land in the Mux Dashboard at `https://dashboard.mux.com`
- Two default environments are created: **Development** and **Production**
- Resources (assets, API keys, webhooks) are scoped to their environment — Development keys cannot manage Production assets
- Start in **Development** for testing; switch to **Production** when going live

---

## Part 2: Getting API Keys (Access Token ID + Secret Key)

### Step-by-Step

1. Log in at: `https://dashboard.mux.com`
2. Click **Settings** in the bottom-left navigation
3. Click **Access Tokens**
4. Or go directly to: `https://dashboard.mux.com/settings/access-tokens`
5. Click **Generate new token**
6. Select permissions: **Mux Video — Read and Write** (for most use cases)
7. Select the environment (Development or Production)
8. Click **Generate Token**

### CRITICAL: Save the Secret Immediately
Mux only stores a hash of the secret key — they cannot recover it. When the token is generated, you will see:
- **Token ID** (acts as your username)
- **Token Secret** (acts as your password)

Copy and save the Token Secret immediately. If you lose it, you must generate a new token.

### Authentication Format
All API calls use HTTP Basic Auth:
```
Username: TOKEN_ID
Password: TOKEN_SECRET
```

Base URL for all API calls: `https://api.mux.com`

---

## Part 3: Uploading a Video via Direct Upload URL (API Method)

This is the recommended method — it creates a signed upload URL, then you PUT your file directly to that URL.

### Step 1 — Create a Direct Upload URL

**Endpoint**: `POST https://api.mux.com/video/v1/uploads`

**curl example**:
```bash
curl https://api.mux.com/video/v1/uploads \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "cors_origin": "*",
    "new_asset_settings": {
      "playback_policies": ["public"],
      "video_quality": "basic"
    }
  }' \
  -u YOUR_TOKEN_ID:YOUR_TOKEN_SECRET
```

**Response (201 Created)**:
```json
{
  "data": {
    "id": "zd01Pe2bNpYhxbrwYABgFE01twZdtv4M00kts2i02GhbGjc",
    "url": "https://storage.googleapis.com/...",
    "status": "waiting",
    "timeout": 3600,
    "cors_origin": "*",
    "new_asset_settings": {
      "playback_policies": ["public"],
      "video_quality": "basic"
    }
  }
}
```

Save the `id` (this is your Upload ID) and the `url` (the signed upload URL).

---

### Step 2 — Upload the Video File

PUT your video file to the signed URL from Step 1:

```bash
curl -X PUT \
  -H "Content-Type: video/mp4" \
  --data-binary @/path/to/your/video.mp4 \
  "https://storage.googleapis.com/..."
```

The server responds with `308` while uploading chunks, and `200`/`201` when complete.

For large files, use chunked upload with headers:
- `Content-Length`: Size of the current chunk
- `Content-Range`: `bytes START-END/TOTAL`

---

### Step 3 — Get the Asset ID (Poll the Upload)

After upload, poll the upload status to get the `asset_id`:

**Endpoint**: `GET https://api.mux.com/video/v1/uploads/{UPLOAD_ID}`

```bash
curl https://api.mux.com/video/v1/uploads/zd01Pe2bNpYhxbrwYABgFE01twZdtv4M00kts2i02GhbGjc \
  -X GET \
  -H "Content-Type: application/json" \
  -u YOUR_TOKEN_ID:YOUR_TOKEN_SECRET
```

**Response when asset is created**:
```json
{
  "data": {
    "id": "zd01Pe2bNpYhxbrwYABgFE01twZdtv4M00kts2i02GhbGjc",
    "status": "asset_created",
    "asset_id": "AnFVqAVXfb7vVL3ypSQDMnJZunnb8nkwe02O00p2gK8P00"
  }
}
```

`status` values: `waiting` → `asset_created`

---

### Step 4 — Get the Playback ID

Once you have the `asset_id`, retrieve the asset to get the `playback_id`:

**Option A — Retrieve full asset**:
```bash
curl https://api.mux.com/video/v1/assets/AnFVqAVXfb7vVL3ypSQDMnJZunnb8nkwe02O00p2gK8P00 \
  -X GET \
  -H "Content-Type: application/json" \
  -u YOUR_TOKEN_ID:YOUR_TOKEN_SECRET
```

The response contains a `playback_ids` array with the `id` field — that is your `playback_id`.

**Option B — Retrieve specific playback ID**:
```bash
curl https://api.mux.com/video/v1/assets/{ASSET_ID}/playback-ids/{PLAYBACK_ID} \
  -X GET \
  -H "Content-Type: application/json" \
  -u YOUR_TOKEN_ID:YOUR_TOKEN_SECRET
```

**Response**:
```json
{
  "data": {
    "policy": "public",
    "id": "vAFLI2eKFFicXX00iHBS2vqt5JjJGg5HV6fQ4Xijgt1I"
  }
}
```

**Option C — Use Webhooks (Recommended for Production)**

Configure webhooks in your Mux dashboard. Listen for:
- `video.upload.asset_created` — upload complete, contains `asset_id`
- `video.asset.ready` — processing complete, contains `playback_id`

The `video.asset.ready` event payload includes the full asset object with `playback_ids`.

---

## Part 4: Mux Player Embed Code

### Method 1 — Web Component (Recommended for Full Control)

Add the script tag and the `<mux-player>` element to your HTML:

```html
<!-- Load Mux Player from CDN -->
<script src="https://cdn.jsdelivr.net/npm/@mux/mux-player" defer></script>

<!-- Embed the player -->
<mux-player
  playback-id="YOUR_PLAYBACK_ID_HERE"
  metadata-video-title="Your Video Title"
  metadata-viewer-user-id="user-id-001"
  accent-color="#f1420b"
></mux-player>
```

Replace `YOUR_PLAYBACK_ID_HERE` with the `playback_id` from Step 4 above.

The `accent-color` above uses PureBrain orange (`#f1420b`) — change as needed.

---

### Method 2 — iFrame Embed (Simplest Option)

Zero JavaScript needed — just paste this HTML:

```html
<iframe
  src="https://player.mux.com/YOUR_PLAYBACK_ID_HERE"
  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
  allowfullscreen="true"
  width="100%"
  height="480"
  style="border: none;"
></iframe>
```

With metadata query params:
```html
<iframe
  src="https://player.mux.com/YOUR_PLAYBACK_ID_HERE?metadata-video-title=Your%20Video%20Title&metadata-viewer-user-id=user-id-001"
  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
  allowfullscreen="true"
  width="100%"
  height="480"
  style="border: none;"
></iframe>
```

---

### HLS URL (for custom video players)

If you need a raw HLS stream URL:
```
https://stream.mux.com/YOUR_PLAYBACK_ID_HERE.m3u8
```

---

## Part 5: Dashboard Upload Option

Mux does NOT have a point-and-click GUI upload interface in the dashboard for end users. All uploads go through one of these methods:

| Method | Best For |
|--------|----------|
| Direct Upload API (PUT) | Server-side uploads, automation |
| Mux Uploader Component | Building your own upload UI in web apps |
| URL Import (API) | If your video is already hosted somewhere |
| CLI (curl) | Quick first video test from terminal |

For your FIRST video, the simplest approach is the **curl method** in Steps 1-4 above — takes about 2 minutes.

---

## Part 6: Quick Start Cheat Sheet

```bash
# 1. Set your credentials
export MUX_TOKEN_ID="your_token_id_here"
export MUX_TOKEN_SECRET="your_token_secret_here"

# 2. Create an upload URL
UPLOAD_RESPONSE=$(curl -s https://api.mux.com/video/v1/uploads \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"cors_origin":"*","new_asset_settings":{"playback_policies":["public"],"video_quality":"basic"}}' \
  -u $MUX_TOKEN_ID:$MUX_TOKEN_SECRET)

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
UPLOAD_URL=$(echo $UPLOAD_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['url'])")

# 3. Upload your video file
curl -X PUT \
  -H "Content-Type: video/mp4" \
  --data-binary @/path/to/video.mp4 \
  "$UPLOAD_URL"

# 4. Wait a moment, then get the asset_id
sleep 5
curl -s "https://api.mux.com/video/v1/uploads/$UPLOAD_ID" \
  -u $MUX_TOKEN_ID:$MUX_TOKEN_SECRET | python3 -m json.tool

# 5. Get the playback_id from the asset
# (replace ASSET_ID with the value from step 4)
curl -s "https://api.mux.com/video/v1/assets/ASSET_ID" \
  -u $MUX_TOKEN_ID:$MUX_TOKEN_SECRET | python3 -m json.tool
```

---

## Key URLs Reference

| Resource | URL |
|----------|-----|
| Signup | https://dashboard.mux.com/signup |
| Login | https://dashboard.mux.com/login |
| Access Tokens | https://dashboard.mux.com/settings/access-tokens |
| API Base | https://api.mux.com |
| Create Upload URL | POST /video/v1/uploads |
| Get Upload Status | GET /video/v1/uploads/{UPLOAD_ID} |
| Get Asset | GET /video/v1/assets/{ASSET_ID} |
| Get Playback ID | GET /video/v1/assets/{ASSET_ID}/playback-ids/{PLAYBACK_ID} |
| Mux Player CDN | https://cdn.jsdelivr.net/npm/@mux/mux-player |
| iFrame Player | https://player.mux.com/{PLAYBACK_ID} |
| HLS Stream | https://stream.mux.com/{PLAYBACK_ID}.m3u8 |
| Documentation | https://www.mux.com/docs |

---

## Sources

- [Make API requests | Mux](https://www.mux.com/docs/core/make-api-requests)
- [Upload files directly | Mux](https://www.mux.com/docs/guides/upload-files-directly)
- [Create a new direct upload URL | API Reference](https://www.mux.com/docs/api-reference/video/direct-uploads/create-direct-upload)
- [Mux Player for web | Mux](https://www.mux.com/docs/guides/mux-player-web)
- [Integrate Mux Player into your web application | Mux](https://www.mux.com/docs/guides/player-integrate-in-your-webapp)
- [Mux fundamentals | Mux](https://www.mux.com/docs/core/mux-fundamentals)
- [Retrieve a playback ID | API Reference](https://www.mux.com/docs/api-reference/video/assets/get-asset-playback-id)
