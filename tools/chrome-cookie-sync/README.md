# PureSurf Cookie Sync — Chrome Extension

Manifest V3 Chrome extension that captures cookies from your real browser session (including httpOnly cookies like LinkedIn's `li_at`) and syncs them to PureSurf profiles for automated session management.

---

## Installation

1. **Download** the extension folder or unzip the `.zip` package
2. Open Chrome and navigate to `chrome://extensions`
3. Enable **Developer mode** (toggle in the top-right)
4. Click **Load unpacked**
5. Select the `chrome-cookie-sync` folder (the one containing `manifest.json`)
6. The PureSurf hexagon icon appears in your toolbar

> **Tip:** Pin the extension by clicking the puzzle icon in the toolbar and pinning "PureSurf Cookie Sync".

---

## Setup

### Get Your Config from PureSurf

Each PureSurf profile has a Cookie Sync config. You need:

```json
{
  "apiUrl": "https://surf.purebrain.ai",
  "apiKey": "your-api-key-here",
  "profileName": "jared-linkedin",
  "label": "Jared LinkedIn"
}
```

| Field | Description |
|-------|-------------|
| `apiUrl` | Your PureSurf server URL (e.g. `https://surf.purebrain.ai` or `http://157.180.69.225:8900`) |
| `apiKey` | API key for authentication (from PureSurf dashboard) |
| `profileName` | Exact profile name in PureSurf to sync cookies to |
| `label` | Friendly display name (shown in extension dropdown) |

### Add a Profile

1. Click the extension icon to open the popup
2. Click the **+** button next to the profile dropdown
3. Paste your JSON config
4. Click **Save Profile**

You can add multiple profiles (one per PureSurf profile you manage).

---

## How to Sync Cookies

### Manual Sync (Primary Flow)

1. **Navigate** to the platform in your browser (e.g. `linkedin.com`)
2. **Log in** normally (handle any 2FA prompts yourself)
3. **Click** the PureSurf extension icon
4. **Select** the target profile from the dropdown
5. **Click** "Sync Cookies Now"
6. **Done** — you'll see a success status with cookie count

### Quick Platform Buttons

The popup has preset buttons for LinkedIn, Twitter/X, Instagram, Facebook, and Google.

- If you're already on the platform: clicking the preset triggers an immediate sync
- If you're on a different site: clicking the preset opens the platform in a new tab (sync after you log in)

---

## What Gets Captured

The extension uses `chrome.cookies.getAll()` which captures:

- Regular cookies (session, persistent)
- **httpOnly cookies** (like LinkedIn's `li_at` — the whole reason this extension exists)
- Secure cookies
- All subdomains of the current domain

Cookies are converted to Playwright-compatible format before syncing:
- `sameSite` values mapped correctly (Chrome's `no_restriction` becomes `None`)
- Expiration dates preserved for persistent cookies
- Domain, path, secure, and httpOnly flags all included

---

## API Details

The extension pushes cookies to:

```
PUT /api/v1/profiles/{profileName}/cookies
```

**Headers:**
- `Content-Type: application/json`
- `X-Api-Key: {your-api-key}`

**Body:**
```json
{
  "cookies": [
    {
      "name": "li_at",
      "value": "AQE...",
      "domain": ".linkedin.com",
      "path": "/",
      "httpOnly": true,
      "secure": true,
      "sameSite": "None",
      "expires": 1745000000
    }
  ]
}
```

**Response:**
```json
{
  "status": "synced",
  "profile": "jared-linkedin",
  "cookies_synced": 42,
  "total_stored": 356,
  "domains": [".linkedin.com", ".www.linkedin.com"],
  "session_injected": false,
  "synced_at": 1712200000
}
```

The API merges incoming cookies with existing ones (by name+domain), encrypts at rest with Fernet, and optionally injects into a live browser session if one is running.

---

## Multi-Profile Management

- **Add profiles** with the + button
- **Switch** between profiles with the dropdown
- **Delete** profiles with the x button (requires confirmation)
- Each profile stores its own API URL, key, and target profile name
- All configs stored in `chrome.storage.local` (encrypted at rest by Chrome)

---

## Troubleshooting

### "No cookies found for [domain]"
- Make sure you are **logged in** to the platform
- Some sites require you to visit specific pages to set all cookies
- Try refreshing the page, then syncing again

### "API error 401" or "API error 403"
- Your API key is incorrect or expired
- Edit the profile config with a valid key

### "API error 404"
- The profile name doesn't match any PureSurf profile
- Check spelling (case-sensitive, use exact profile name from PureSurf)

### "Failed to fetch" or network error
- PureSurf server may be down or unreachable
- Check that the `apiUrl` is correct and the server is running
- If using HTTPS, ensure the certificate is valid

### Cookies sync but PureSurf sessions don't work
- Some platforms (LinkedIn especially) tie sessions to IP address
- Make sure PureSurf is using a proxy in the same region as your browser
- Cookie freshness matters — re-sync periodically (every few days)

### Extension not capturing httpOnly cookies
- This should work out of the box — `chrome.cookies.getAll()` returns httpOnly cookies
- Verify in the sync response that the cookie count looks right (LinkedIn typically has 20-40 cookies)

---

## Security Notes

- **API keys** are stored in `chrome.storage.local`, which Chrome encrypts at rest
- **No external calls** are made except to your PureSurf server
- **Cookies are sensitive** — they grant full session access to your accounts
- **Internal distribution only** — this extension is sideloaded, not on the Chrome Web Store
- **Never share** your extension config or PureSurf API key with untrusted parties
- **Only sync accounts you own** — using this on accounts that aren't yours violates platform ToS

---

## File Structure

```
chrome-cookie-sync/
  manifest.json        Manifest V3 config
  popup.html           Extension popup UI
  popup.js             Cookie capture and sync logic
  popup.css            Dark theme styling (PureBrain brand)
  background.js        Service worker (lifecycle, message handling)
  icons/
    icon16.png         Toolbar icon
    icon48.png         Extensions page icon
    icon128.png        Install dialog icon
  README.md            This file
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-04 | Initial release. Manual sync, multi-profile, platform presets. |

---

Built by the Systems & Technology department for Pure Technology.
