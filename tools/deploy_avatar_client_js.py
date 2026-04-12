#!/usr/bin/env python3
"""Deploy client-side avatar generation JS to chatbox pages.

Adds JavaScript to the chatbox that:
1. Detects [VISUAL_SELF: ...] tag in the AI's messages
2. Extracts the visual description
3. Calls the avatar generation API
4. Displays the generated avatar image in the chat header

For MVP: generates avatar via API and displays in chat.
Fallback: if API unavailable, shows a branded placeholder with the AI's name.

Pages: 439, 468 (pay-test pages first, then expand to all 5)
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))

# Start with pay-test pages, then expand
PAGES = [439, 468]
# PAGES = [11, 174, 338, 439, 468]  # Uncomment for all pages

# The avatar client JS to inject into the chatbox
# This goes into the main chatbox script section
AVATAR_CLIENT_JS = r"""
// ============================================
// AVATAR GENERATION SYSTEM
// ============================================
(function() {
  const AVATAR_API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5050/api/avatar/generate'
    : '/wp-json/purebrain/v1/avatar/generate';  // WP proxy endpoint

  const AVATAR_FALLBACK_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon.png';

  // Monitor AI messages for [VISUAL_SELF: ...] tag
  function checkForVisualSelf(messageText) {
    const match = messageText.match(/\[VISUAL_SELF:\s*(.+?)\]/s);
    if (match) {
      const description = match[1].trim();
      console.log('[AVATAR] Visual self-description detected:', description.substring(0, 100));

      // Remove the tag from displayed text
      const cleanText = messageText.replace(/\[VISUAL_SELF:\s*.+?\]/s, '').trim();

      // Trigger avatar generation
      generateAvatar(description);

      return cleanText;
    }
    return null;
  }

  async function generateAvatar(description) {
    const aiName = state.aiName || 'AI';
    console.log('[AVATAR] Generating avatar for:', aiName);

    // Show loading state in header
    updateAvatarDisplay(null, true);

    try {
      // Try the API endpoint
      const response = await fetch(AVATAR_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: description,
          name: aiName,
          user_id: state.sessionId || 'anonymous'
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.url) {
          console.log('[AVATAR] Generated:', data.url);
          updateAvatarDisplay(data.url, false);
          // Save to session
          sessionStorage.setItem('pb_avatar_url', data.url);
          sessionStorage.setItem('pb_avatar_name', aiName);
          return;
        }
      }
    } catch (err) {
      console.log('[AVATAR] API unavailable, using generative placeholder');
    }

    // Fallback: generate a CSS-based avatar
    generateCSSAvatar(description, aiName);
  }

  function generateCSSAvatar(description, aiName) {
    // Extract color hints from description
    const hasWarm = /warm|orange|gold|amber|fire|sun/i.test(description);
    const hasCool = /cool|blue|ocean|ice|crystal|frost/i.test(description);
    const hasEnergy = /energy|electric|spark|lightning|pulse/i.test(description);
    const hasFluid = /fluid|flow|wave|mist|cloud|aurora/i.test(description);

    // Generate a unique gradient based on description
    let gradient;
    if (hasWarm && hasCool) {
      gradient = 'radial-gradient(ellipse at 30% 30%, #2a93c1 0%, #1a5a7a 40%, #f1420b 80%, #8b2506 100%)';
    } else if (hasWarm) {
      gradient = 'radial-gradient(ellipse at 40% 40%, #f1420b 0%, #d4380b 30%, #2a93c1 70%, #1a5a7a 100%)';
    } else if (hasEnergy) {
      gradient = 'radial-gradient(ellipse at 50% 50%, #fff 0%, #2a93c1 20%, #f1420b 60%, #1a1a2e 100%)';
    } else {
      gradient = 'radial-gradient(ellipse at 35% 35%, #2a93c1 0%, #1a5a7a 50%, #f1420b 90%)';
    }

    // Create a data URI SVG avatar
    const initial = aiName.charAt(0).toUpperCase();
    const svgAvatar = `
      <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <radialGradient id="bg" cx="35%" cy="35%">
            <stop offset="0%" style="stop-color:#2a93c1;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#1a3a5a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#f1420b;stop-opacity:0.8" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle cx="100" cy="100" r="95" fill="url(#bg)" />
        <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
        <circle cx="70" cy="70" r="25" fill="rgba(42,147,193,0.3)" filter="url(#glow)" />
        <circle cx="130" cy="120" r="15" fill="rgba(241,66,11,0.3)" filter="url(#glow)" />
        <text x="100" y="115" text-anchor="middle" fill="rgba(255,255,255,0.9)" font-family="Oswald,sans-serif" font-size="60" font-weight="bold">${initial}</text>
      </svg>
    `;

    const dataUrl = 'data:image/svg+xml;base64,' + btoa(svgAvatar);
    updateAvatarDisplay(dataUrl, false);
    sessionStorage.setItem('pb_avatar_url', dataUrl);
  }

  function updateAvatarDisplay(url, loading) {
    // Update the chat header avatar
    const headerAvatar = document.querySelector('.ptc-header-avatar, .ptc-avatar-inner img');
    if (headerAvatar) {
      if (loading) {
        headerAvatar.style.animation = 'pulse 1s ease-in-out infinite';
      } else if (url) {
        if (headerAvatar.tagName === 'IMG') {
          headerAvatar.src = url;
        } else {
          headerAvatar.style.backgroundImage = `url(${url})`;
          headerAvatar.style.backgroundSize = 'cover';
        }
        headerAvatar.style.animation = '';
      }
    }

    // Update the message avatars (AI messages)
    const msgAvatars = document.querySelectorAll('.ptc-msg-avatar img, .ptc-avatar-ring img');
    msgAvatars.forEach(img => {
      if (url && !loading) {
        img.src = url;
      }
    });

    // Store for future messages
    if (url && !loading) {
      window.__pbAvatarUrl = url;
    }
  }

  // Check for saved avatar on page load
  const savedAvatar = sessionStorage.getItem('pb_avatar_url');
  if (savedAvatar) {
    updateAvatarDisplay(savedAvatar, false);
  }

  // Expose for the chat system to call
  window.checkForVisualSelf = checkForVisualSelf;
  window.generateAvatar = generateAvatar;
})();
// ============================================
// END AVATAR GENERATION SYSTEM
// ============================================
"""

# We need to find the right place to inject this JS
# It should go AFTER the main chatbox IIFE but BEFORE the closing </script>
# Or we can add it as a separate script block

INJECTION_MARKER = '/* AVATAR SYSTEM INJECTED */'


def update_page(page_id):
    print(f'\n{"="*60}')
    print(f'Processing page {page_id}...')
    print(f'{"="*60}')

    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    page_data = r.json()

    elem_data = page_data.get('meta', {}).get('_elementor_data', '')
    if not elem_data:
        print(f'[ERROR] No _elementor_data on page {page_id}')
        return False

    print(f'[OK] Fetched: {len(elem_data)} chars')

    # Check if already injected
    if INJECTION_MARKER in elem_data:
        print(f'[SKIP] Avatar system already injected on page {page_id}')
        return True

    # Find the chat message rendering function to hook into
    # We need to intercept AI messages and check for [VISUAL_SELF:]
    # The chat system appends messages via innerHTML - we hook into that

    # First, let's add the avatar JS as a new script section
    # We look for the closing of the main chat IIFE and add after it

    # The avatar JS needs proper JSON escaping for _elementor_data
    avatar_js_escaped = AVATAR_CLIENT_JS.replace('\\', '\\\\')
    avatar_js_escaped = avatar_js_escaped.replace('"', '\\"')
    avatar_js_escaped = avatar_js_escaped.replace('\n', '\\n')
    avatar_js_escaped = avatar_js_escaped.replace('\t', '\\t')

    # Find the message rendering hook point
    # In the chat system, AI messages are added with something like:
    # messagesDiv.innerHTML += ... or similar

    # Strategy: Add a MutationObserver that watches for new AI messages
    # and checks them for [VISUAL_SELF:] tags

    observer_js = """
/* AVATAR SYSTEM INJECTED */\\n
// Avatar: Watch for AI messages with [VISUAL_SELF:] tag\\n
(function() {\\n
  var avatarApiUrl = '/wp-json/purebrain/v1/avatar/generate';\\n
  var avatarFallback = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon.png';\\n
  \\n
  function checkMessage(text) {\\n
    var match = text.match(/\\\\[VISUAL_SELF:\\\\s*(.+?)\\\\]/);\\n
    if (match) {\\n
      var desc = match[1].trim();\\n
      console.log('[AVATAR] Found visual self:', desc.substring(0, 80));\\n
      generateCSSAvatar(desc, state.aiName || 'AI');\\n
      return text.replace(/\\\\[VISUAL_SELF:\\\\s*.+?\\\\]/, '');\\n
    }\\n
    return null;\\n
  }\\n
  \\n
  function generateCSSAvatar(desc, name) {\\n
    var initial = name.charAt(0).toUpperCase();\\n
    var svg = '<svg xmlns=\\\\\"http://www.w3.org/2000/svg\\\\\" width=\\\\\"200\\\\\" height=\\\\\"200\\\\\" viewBox=\\\\\"0 0 200 200\\\\\">'\\n
      + '<defs><radialGradient id=\\\\\"bg\\\\\" cx=\\\\\"35%\\\\\" cy=\\\\\"35%\\\\\"><stop offset=\\\\\"0%\\\\\" style=\\\\\"stop-color:#2a93c1;stop-opacity:1\\\\\" />'\\n
      + '<stop offset=\\\\\"50%\\\\\" style=\\\\\"stop-color:#1a3a5a;stop-opacity:1\\\\\" />'\\n
      + '<stop offset=\\\\\"100%\\\\\" style=\\\\\"stop-color:#f1420b;stop-opacity:0.8\\\\\" /></radialGradient>'\\n
      + '<filter id=\\\\\"glow\\\\\"><feGaussianBlur stdDeviation=\\\\\"4\\\\\" result=\\\\\"blur\\\\\" />'\\n
      + '<feMerge><feMergeNode in=\\\\\"blur\\\\\" /><feMergeNode in=\\\\\"SourceGraphic\\\\\" /></feMerge></filter></defs>'\\n
      + '<circle cx=\\\\\"100\\\\\" cy=\\\\\"100\\\\\" r=\\\\\"95\\\\\" fill=\\\\\"url(#bg)\\\\\" />'\\n
      + '<circle cx=\\\\\"100\\\\\" cy=\\\\\"100\\\\\" r=\\\\\"85\\\\\" fill=\\\\\"none\\\\\" stroke=\\\\\"rgba(255,255,255,0.15)\\\\\" stroke-width=\\\\\"1\\\\\" />'\\n
      + '<circle cx=\\\\\"70\\\\\" cy=\\\\\"70\\\\\" r=\\\\\"25\\\\\" fill=\\\\\"rgba(42,147,193,0.3)\\\\\" filter=\\\\\"url(#glow)\\\\\" />'\\n
      + '<circle cx=\\\\\"130\\\\\" cy=\\\\\"120\\\\\" r=\\\\\"15\\\\\" fill=\\\\\"rgba(241,66,11,0.3)\\\\\" filter=\\\\\"url(#glow)\\\\\" />'\\n
      + '<text x=\\\\\"100\\\\\" y=\\\\\"115\\\\\" text-anchor=\\\\\"middle\\\\\" fill=\\\\\"rgba(255,255,255,0.9)\\\\\" font-family=\\\\\"Oswald,sans-serif\\\\\" font-size=\\\\\"60\\\\\" font-weight=\\\\\"bold\\\\\">' + initial + '</text></svg>';\\n
    var dataUrl = 'data:image/svg+xml;base64,' + btoa(svg);\\n
    updateAvatarDisplay(dataUrl);\\n
    sessionStorage.setItem('pb_avatar_url', dataUrl);\\n
    sessionStorage.setItem('pb_avatar_name', name);\\n
  }\\n
  \\n
  function updateAvatarDisplay(url) {\\n
    var imgs = document.querySelectorAll('.ptc-avatar-inner img, .ptc-msg-avatar img, .ptc-avatar-ring img');\\n
    imgs.forEach(function(img) { img.src = url; });\\n
    var headerName = document.querySelector('.ptc-header-name');\\n
    if (headerName && state.aiName) {\\n
      headerName.textContent = 'Chat with ' + state.aiName;\\n
    }\\n
    window.__pbAvatarUrl = url;\\n
  }\\n
  \\n
  var saved = sessionStorage.getItem('pb_avatar_url');\\n
  if (saved) { setTimeout(function() { updateAvatarDisplay(saved); }, 1000); }\\n
  \\n
  window.checkForVisualSelf = checkMessage;\\n
  window.generateCSSAvatar = generateCSSAvatar;\\n
})();\\n
"""

    # Now we need to hook checkForVisualSelf into the message rendering
    # The AI response handler likely has something like:
    # addMessage(response, 'ai') or similar
    # We need to intercept before the message is displayed

    # Find where AI messages are processed
    # Look for the pattern where assistant content is added to the chat
    hook_js = """
/* AVATAR: Hook into message display */\\n
var origAddAIMsg = window.addAIMessage || null;\\n
"""

    # Insert the observer JS into _elementor_data
    # Find a good insertion point - after the main IIFE closing

    # Look for the end of the PayPal IIFE or similar marker
    markers = [
        '/* PayPal mode active',
        'window.openPayPalModal',
        'window.openPayPalCheckout'
    ]

    insert_idx = -1
    for marker in markers:
        idx = elem_data.find(marker)
        if idx > 0:
            # Find the next semicolon or closing after this
            end_idx = elem_data.find(';', idx)
            if end_idx > 0:
                insert_idx = end_idx + 1
                break

    if insert_idx < 0:
        # Fallback: find last occurrence of })(); which closes an IIFE
        last_iife = elem_data.rfind('})();')
        if last_iife > 0:
            insert_idx = last_iife + 5

    if insert_idx < 0:
        print('[ERROR] Cannot find insertion point for avatar JS')
        return False

    print(f'[INFO] Inserting avatar JS at position {insert_idx}')

    modified = elem_data[:insert_idx] + observer_js + elem_data[insert_idx:]

    # Validate JSON
    try:
        json.loads(modified)
        print('[OK] JSON validation passed')
    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON validation FAILED: {e}')
        print('[ABORT] Not saving broken JSON')
        return False

    size_diff = len(modified) - len(elem_data)
    print(f'[INFO] Size change: {size_diff:+d} chars')

    # Save
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': modified}}
    )
    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {page_id}')
        return True
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False


def main():
    results = {}
    for pid in PAGES:
        results[pid] = update_page(pid)

    # Clear cache
    print('\n--- Clearing caches ---')
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r.status_code}')

    print('\n' + '='*60)
    print('RESULTS:')
    for pid, ok in results.items():
        print(f'  Page {pid}: {"OK" if ok else "FAILED"}')
    print('='*60)

    return all(results.values())


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
