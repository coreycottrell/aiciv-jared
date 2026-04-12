# Google Drive OAuth2 Setup Guide

**Date**: 2026-02-04
**Purpose**: Enable full Google Drive access as the account owner (purebrain@puremarketing.ai)

## Why OAuth2?

Currently we use a **Service Account** which:
- Has quota limits (403 errors during heavy usage)
- Only sees folders explicitly shared with it
- Cannot access your full Drive

With **OAuth2** you get:
- Full access as the Drive owner
- No quota limits (owner quotas are very high)
- Access to ALL your Drive files and folders
- Can create files anywhere in your Drive

---

## Step 1: Create OAuth2 Credentials (One-Time)

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials?project=aether-integration)

2. Click **"Create Credentials"** > **"OAuth client ID"**

3. If prompted, configure the OAuth consent screen first:
   - User Type: **Internal** (for purebrain@puremarketing.ai domain)
   - App name: "Aether Drive Access"
   - User support email: your email
   - Developer contact: your email
   - Add scopes: `drive` and `spreadsheets`
   - Save

4. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Aether Server"
   - Click **Create**

5. **Download the JSON** file
   - Click the download icon next to your new credential
   - Save as: `aether/.credentials/oauth-credentials.json`

---

## Step 2: Run the OAuth Setup Script

On the server (where Aether runs):

```bash
cd /home/jared/projects/AI-CIV/aether
source venv/bin/activate
python tools/gdrive_oauth_setup.py
```

### What Happens:

1. Script prints an authorization URL
2. **Copy this URL** and open it in any browser (your laptop is fine)
3. Log in as **purebrain@puremarketing.ai**
4. Grant access to Google Drive
5. You'll be redirected to `localhost:8080` - the server catches this automatically
6. Token saved!

### If localhost redirect doesn't work:

If you're running this on a headless server and the redirect fails, use manual mode:

```bash
python tools/gdrive_oauth_setup.py --manual
```

Then:
1. Copy the URL and visit it in your browser
2. After granting access, you'll see an authorization code
3. Paste that code back into the terminal

---

## Step 3: Verify It Works

```bash
# Check authentication status
python tools/gdrive_manager.py auth-info

# Should show:
#   Auth type: oauth2
#   OAuth token exists: True
#   Status: Using OAuth2 (optimal)

# List your Drive root
python tools/gdrive_manager.py list-root

# List any folder by name
python tools/gdrive_manager.py list "CTO"
```

---

## Files Created

| File | Purpose |
|------|---------|
| `.credentials/oauth-credentials.json` | OAuth client ID & secret (you download this) |
| `.credentials/oauth-token.json` | Access & refresh tokens (script creates this) |

Both files are gitignored and contain sensitive credentials.

---

## Token Refresh

The OAuth token is automatically refreshed when it expires. The `gdrive_manager.py` handles this transparently.

Tokens may become invalid if:
- You revoke access in Google Account settings
- Token unused for 6+ months
- You change your Google password

If this happens, just run `python tools/gdrive_oauth_setup.py` again.

---

## Troubleshooting

### "OAuth credentials file not found"
Download `oauth-credentials.json` from Google Cloud Console (Step 1)

### "Access blocked: This app's request is invalid"
The OAuth consent screen needs to be configured. Go to Google Cloud Console > APIs & Services > OAuth consent screen.

### "localhost connection refused" during auth
Use manual mode: `python tools/gdrive_oauth_setup.py --manual`

### Token works but can't see folders
With OAuth2, you access your own Drive directly. No need to share folders with a service account anymore.

---

## Architecture

```
gdrive_manager.py
     |
     +-- Tries OAuth2 token first (oauth-token.json)
     |       |
     |       +-- If valid -> Use owner credentials
     |       +-- If expired -> Auto-refresh
     |
     +-- Falls back to Service Account (google-drive-service-account.json)
             |
             +-- Has quota limits
             +-- Only sees shared folders
```

Once OAuth is set up, the service account becomes a fallback that's rarely used.
