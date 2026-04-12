/**
 * PureSurf Cookie Sync — Background Service Worker (Manifest V3)
 *
 * Handles:
 * - Extension install/update lifecycle
 * - Future: scheduled auto-sync, context menus, notifications
 */

// ── Install / Update ──────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('[PureSurf Cookie Sync] Extension installed. Open popup to configure.');
  } else if (details.reason === 'update') {
    console.log(`[PureSurf Cookie Sync] Updated to v${chrome.runtime.getManifest().version}`);
  }
});

// ── Message handler (for future popup <-> background communication) ──
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_COOKIES') {
    // Popup can request cookies via background if needed
    const { domain } = message;
    chrome.cookies.getAll({ domain }, (cookies) => {
      sendResponse({ cookies });
    });
    return true; // async response
  }

  if (message.type === 'HEALTH_CHECK') {
    sendResponse({ status: 'ok', version: chrome.runtime.getManifest().version });
    return false;
  }
});
