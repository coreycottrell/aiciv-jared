#!/usr/bin/env python3
"""Upgrade post-payment chat UI on pay-test pages (439 and 468).

Adds:
  1. Padding/margins so chat feels like overlay on top of website
  2. Chat header with PureBrain logo + AI name + status dot
  3. Spinning background logo (aether-orb animation)
  4. Logo avatar next to AI messages (gradient ring with icon)
  5. Spinning logo when AI is "thinking"
  6. AI name in input placeholder ("Message [AI Name]...")
  7. Google Fonts for Oswald + Plus Jakarta Sans

Applied to _elementor_data on BOTH pages.

Usage:
    python3 tools/upgrade_chat_ui.py              # Apply to both pages
    python3 tools/upgrade_chat_ui.py --dry-run     # Preview without saving
    python3 tools/upgrade_chat_ui.py --page 439    # Apply to one page only
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGES = [439, 468]

# PureBrain icon - uploaded to purebrain.ai media library
ICON_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-hexagon-icon.jpg'
# Fallback: puremarketing.ai icon
ICON_URL_FALLBACK = 'https://puremarketing.ai/wp-content/uploads/2025/07/2.-Main-Icon-Orange-to-Blue-PM-2.png'


# ═══════════════════════════════════════════════════════════════════════════
# NEW CSS to inject into injectStyles()
# ═══════════════════════════════════════════════════════════════════════════

NEW_CSS = r"""
    /* ── Google Fonts ──────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* ── Chat outer shell (overlay feel) ───────────────────────────── */
    .ptc-outer-shell {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 100vh;
      padding: 24px 32px;
      background: #050508;
      overflow: hidden;
    }

    @media (max-width: 768px) {
      .ptc-outer-shell { padding: 12px 10px; }
    }

    /* ── Background spinning logo ──────────────────────────────────── */
    .ptc-bg-orb {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 340px;
      height: 340px;
      opacity: 0.06;
      pointer-events: none;
      z-index: 0;
    }

    .ptc-bg-orb img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      animation: ptc-bg-spin 30s linear infinite;
    }

    @keyframes ptc-bg-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }

    /* ── Chat header ───────────────────────────────────────────────── */
    .ptc-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      background: rgba(20, 20, 20, 0.95);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px 16px 0 0;
      flex-shrink: 0;
      position: relative;
      z-index: 2;
    }

    .ptc-header__logo {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2px;
      flex-shrink: 0;
    }

    .ptc-header__logo-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-header__logo-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    .ptc-header__info {
      flex: 1;
    }

    .ptc-header__title {
      font-family: 'Oswald', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: #f0f0f0;
    }

    .ptc-header__status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      color: #888;
    }

    .ptc-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22c55e;
      animation: ptc-status-pulse 2s ease-in-out infinite;
    }

    @keyframes ptc-status-pulse {
      0%, 100% { opacity: 1; }
      50%      { opacity: 0.5; }
    }

    .ptc-header__brand {
      font-family: 'Oswald', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      color: #888;
      display: flex;
      align-items: center;
      gap: 2px;
    }

    .ptc-header__brand-blue  { color: #2a93c1; }
    .ptc-header__brand-orange { color: #f1420b; }

    /* ── Avatar for AI messages ────────────────────────────────────── */
    .ptc-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 2px;
    }

    .ptc-avatar-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-avatar-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    /* ── Spinning avatar for typing indicator ──────────────────────── */
    .ptc-avatar--spinning img {
      animation: ptc-logo-spin 1.5s linear infinite;
    }

    @keyframes ptc-logo-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }
"""

# ═══════════════════════════════════════════════════════════════════════════
# Replacement map for specific code changes
# ═══════════════════════════════════════════════════════════════════════════


def get_replacements(icon_url):
    """Return list of (old, new) tuples for string replacement in the code."""
    return [
        # 1. WRAPPER: Add border-radius and position relative (for background orb)
        (
            """.ptc-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 500px;
      background: var(--dark);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 15px;
      line-height: 1.55;
    }""",
            """.ptc-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 500px;
      background: rgba(10, 10, 10, 0.97);
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 15px;
      line-height: 1.55;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.08);
      position: relative;
      z-index: 1;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }"""
        ),

        # 2. MESSAGE LIST: slightly more padding
        (
            """.ptc-messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }""",
            """.ptc-messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scroll-behavior: smooth;
      position: relative;
      z-index: 2;
    }"""
        ),

        # 3. INPUT ROW: match rounded bottom
        (
            """.ptc-input-row {
      padding: 12px 20px 20px;
      display: flex;
      gap: 10px;
      background: var(--dark);
      border-top: 1px solid #1e1e1e;
    }""",
            """.ptc-input-row {
      padding: 12px 24px 20px;
      display: flex;
      gap: 10px;
      background: transparent;
      border-top: 1px solid rgba(255,255,255,0.06);
      position: relative;
      z-index: 2;
    }"""
        ),

        # 4. INPUT FIELD: better styling
        (
            """.ptc-input {
      flex: 1;
      background: var(--surface);
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 15px;
      padding: 10px 14px;
      outline: none;
      transition: border-color 0.2s;
      resize: none;
      min-height: 42px;
      max-height: 120px;
    }""",
            """.ptc-input {
      flex: 1;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      font-size: 15px;
      padding: 12px 16px;
      outline: none;
      transition: border-color 0.2s;
      resize: none;
      min-height: 42px;
      max-height: 120px;
    }"""
        ),

        # 5. SEND BUTTON: gradient instead of flat orange
        (
            """.ptc-send-btn {
      background: var(--bright-orange);
      border: none;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      padding: 10px 20px;
      transition: opacity 0.2s;
      white-space: nowrap;
    }""",
            """.ptc-send-btn {
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      border: none;
      border-radius: 12px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      padding: 10px 22px;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .ptc-send-btn:hover { transform: scale(1.03); }"""
        ),

        # 6. AI BUBBLE: better border
        (
            """.ptc-msg--ai   .ptc-bubble {
      background: var(--surface-2);
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
    }""",
            """.ptc-msg--ai   .ptc-bubble {
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
    }"""
        ),

        # 7. USER BUBBLE: gradient
        (
            """.ptc-msg--user .ptc-bubble {
      background: var(--light-blue);
      color: #fff;
      border-bottom-right-radius: 4px;
    }""",
            """.ptc-msg--user .ptc-bubble {
      background: linear-gradient(135deg, #f1420b, #ed6626);
      color: #fff;
      border-bottom-right-radius: 4px;
    }"""
        ),

        # 8. TYPING INDICATOR: better background
        (
            """.ptc-typing {
      display: flex;
      gap: 5px;
      align-items: center;
      padding: 12px 16px;
      background: var(--surface-2);
      border-radius: var(--radius);
      border-bottom-left-radius: 4px;
      width: fit-content;
    }""",
            """.ptc-typing {
      display: flex;
      gap: 5px;
      align-items: center;
      padding: 12px 16px;
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: var(--radius);
      border-bottom-left-radius: 4px;
      width: fit-content;
    }"""
        ),

        # 9. TYPING DOTS: blue instead of muted
        (
            """.ptc-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--text-muted);
      animation: ptc-bounce 1.2s infinite ease-in-out;
    }""",
            """.ptc-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #2a93c1;
      animation: ptc-bounce 1.2s infinite ease-in-out;
    }"""
        ),

        # 10. buildLayout: Add header, background orb, and update structure
        (
            """function buildLayout(container) {
  container.innerHTML = '';
  container.classList.add('ptc-wrapper');

  const msgList = document.createElement('div');
  msgList.className = 'ptc-messages';
  msgList.id = 'ptc-messages';

  const actions = document.createElement('div');
  actions.className = 'ptc-actions';
  actions.id = 'ptc-actions';

  const inputRow = document.createElement('div');
  inputRow.className = 'ptc-input-row';
  inputRow.id = 'ptc-input-row';
  inputRow.style.display = 'none'; // hidden until needed

  const textarea = document.createElement('textarea');
  textarea.className = 'ptc-input';
  textarea.id = 'ptc-input';
  textarea.rows = 1;
  textarea.placeholder = 'Type your reply…';

  const sendBtn = document.createElement('button');
  sendBtn.className = 'ptc-send-btn';
  sendBtn.id = 'ptc-send-btn';
  sendBtn.textContent = 'Send';

  inputRow.appendChild(textarea);
  inputRow.appendChild(sendBtn);

  container.appendChild(msgList);
  container.appendChild(actions);
  container.appendChild(inputRow);

  return { msgList, actions, inputRow, textarea, sendBtn };
}""",
            f"""function buildLayout(container) {{
  // Wrap in outer shell for padding/overlay feel
  const shell = container.closest('.ptc-outer-shell') || container.parentElement;
  if (!shell.classList.contains('ptc-outer-shell')) {{
    const outerShell = document.createElement('div');
    outerShell.className = 'ptc-outer-shell';
    // Background spinning logo
    outerShell.innerHTML = '<div class="ptc-bg-orb"><img src="{icon_url}" alt="PureBrain"></div>';
    container.parentElement.insertBefore(outerShell, container);
    outerShell.appendChild(container);
  }}

  container.innerHTML = '';
  container.classList.add('ptc-wrapper');

  // Chat header with logo + AI name
  const header = document.createElement('div');
  header.className = 'ptc-header';
  header.id = 'ptc-header';
  header.innerHTML = `
    <div class="ptc-header__logo">
      <div class="ptc-header__logo-inner">
        <img src="{icon_url}" alt="PureBrain">
      </div>
    </div>
    <div class="ptc-header__info">
      <div class="ptc-header__title">Chat with ${{payTestData.aiName || 'Your AI'}}</div>
      <div class="ptc-header__status">
        <span class="ptc-status-dot"></span>
        Online &middot; Ready to assist
      </div>
    </div>
    <div class="ptc-header__brand">
      <span class="ptc-header__brand-blue">PUREBR</span><span class="ptc-header__brand-orange">AI</span><span class="ptc-header__brand-blue">N</span>
    </div>
  `;

  const msgList = document.createElement('div');
  msgList.className = 'ptc-messages';
  msgList.id = 'ptc-messages';

  const actions = document.createElement('div');
  actions.className = 'ptc-actions';
  actions.id = 'ptc-actions';

  const inputRow = document.createElement('div');
  inputRow.className = 'ptc-input-row';
  inputRow.id = 'ptc-input-row';
  inputRow.style.display = 'none'; // hidden until needed

  const textarea = document.createElement('textarea');
  textarea.className = 'ptc-input';
  textarea.id = 'ptc-input';
  textarea.rows = 1;
  textarea.placeholder = 'Message ' + (payTestData.aiName || 'your AI') + '…';

  const sendBtn = document.createElement('button');
  sendBtn.className = 'ptc-send-btn';
  sendBtn.id = 'ptc-send-btn';
  sendBtn.textContent = 'Send';

  inputRow.appendChild(textarea);
  inputRow.appendChild(sendBtn);

  container.appendChild(header);
  container.appendChild(msgList);
  container.appendChild(actions);
  container.appendChild(inputRow);

  return {{ msgList, actions, inputRow, textarea, sendBtn }};
}}"""
        ),

        # 11. showTyping: Add spinning avatar
        (
            """function showTyping(msgList) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  const indicator = document.createElement('div');
  indicator.className = 'ptc-typing';
  indicator.innerHTML = '<span></span><span></span><span></span>';

  wrapper.appendChild(indicator);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  return () => wrapper.remove();
}""",
            f"""function showTyping(msgList) {{
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  // Spinning avatar
  const avatar = document.createElement('div');
  avatar.className = 'ptc-avatar ptc-avatar--spinning';
  avatar.innerHTML = '<div class="ptc-avatar-inner"><img src="{icon_url}" alt=""></div>';

  const indicator = document.createElement('div');
  indicator.className = 'ptc-typing';
  indicator.innerHTML = '<span></span><span></span><span></span>';

  wrapper.appendChild(avatar);
  wrapper.appendChild(indicator);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  return () => wrapper.remove();
}}"""
        ),

    ]


def get_raw_replacements(icon_url):
    """Return list of (old, new) tuples for direct raw string replacement.

    These operate on the actual _elementor_data string as returned by
    the WP REST API. In that string:
      - Line breaks in JS code appear as literal \\n (backslash + n)
      - The regex /\\n/g appears as /\\\\n/g (two backslashes + n)
    """
    # Build old/new using the exact character sequences in the data
    NL = '\\n'  # literal backslash-n (how line breaks appear in the data)
    REGEX_NL = '\\\\n'  # literal \\n (how the regex /\\n/g appears)

    old_aisay = (
        f"async function aiSay(msgList, text, delayMs = null) {{{NL}"
        f"  const removeTyping = showTyping(msgList);{NL}"
        f"  await sleep(delayMs !== null ? delayMs : jitter(600, 1400));{NL}"
        f"  removeTyping();{NL}"
        f"{NL}"
        f"  const wrapper = document.createElement('div');{NL}"
        f"  wrapper.className = 'ptc-msg ptc-msg--ai';{NL}"
        f"{NL}"
        f"  const bubble = document.createElement('div');{NL}"
        f"  bubble.className = 'ptc-bubble';{NL}"
        f"  bubble.innerHTML = text.replace(/{REGEX_NL}/g, '<br>');{NL}"
        f"{NL}"
        f"  wrapper.appendChild(bubble);{NL}"
        f"  msgList.appendChild(wrapper);{NL}"
        f"  scrollBottom(msgList);{NL}"
        f"}}"
    )

    new_aisay = (
        f"async function aiSay(msgList, text, delayMs = null) {{{NL}"
        f"  const removeTyping = showTyping(msgList);{NL}"
        f"  await sleep(delayMs !== null ? delayMs : jitter(600, 1400));{NL}"
        f"  removeTyping();{NL}"
        f"{NL}"
        f"  const wrapper = document.createElement('div');{NL}"
        f"  wrapper.className = 'ptc-msg ptc-msg--ai';{NL}"
        f"{NL}"
        f"  // Avatar with PureBrain icon{NL}"
        f"  const avatar = document.createElement('div');{NL}"
        f"  avatar.className = 'ptc-avatar';{NL}"
        f'  avatar.innerHTML = \'<div class="ptc-avatar-inner"><img src="{icon_url}" alt=""></div>\';{NL}'
        f"{NL}"
        f"  const bubble = document.createElement('div');{NL}"
        f"  bubble.className = 'ptc-bubble';{NL}"
        f"  bubble.innerHTML = text.replace(/{REGEX_NL}/g, '<br>');{NL}"
        f"{NL}"
        f"  wrapper.appendChild(avatar);{NL}"
        f"  wrapper.appendChild(bubble);{NL}"
        f"  msgList.appendChild(wrapper);{NL}"
        f"  scrollBottom(msgList);{NL}"
        f"{NL}"
        f"  // Update header with AI name if available{NL}"
        f"  const hdr = document.getElementById('ptc-header');{NL}"
        f"  if (hdr && payTestData.aiName) {{{NL}"
        f"    const titleEl = hdr.querySelector('.ptc-header__title');{NL}"
        f"    if (titleEl) titleEl.textContent = 'Chat with ' + payTestData.aiName;{NL}"
        f"    const inputEl = document.getElementById('ptc-input');{NL}"
        f"    if (inputEl) inputEl.placeholder = 'Message ' + payTestData.aiName + '\\u2026';{NL}"
        f"  }}{NL}"
        f"}}"
    )

    return [(old_aisay, new_aisay)]


def apply_to_page(page_id, dry_run=False):
    """Fetch page, apply CSS+JS modifications to _elementor_data, save back."""
    print(f'\n{"="*60}')
    print(f'Processing page {page_id}...')
    print(f'{"="*60}')

    # Fetch current page data
    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    page_data = r.json()

    elem_data = page_data.get('meta', {}).get('_elementor_data', '')
    if not elem_data:
        print(f'[ERROR] No _elementor_data found on page {page_id}')
        return False

    print(f'[OK] Fetched _elementor_data: {len(elem_data)} chars')

    modified = elem_data
    change_count = 0

    # Apply CSS additions - inject new CSS before the closing backtick of the style
    # Find the end of injectStyles CSS content
    css_injection_marker = '.ptc-link-btn:hover { opacity: 0.88; }'
    css_close = '  `;'
    # Find the pattern where CSS ends
    css_end_idx = modified.find(css_injection_marker)
    if css_end_idx >= 0:
        # Find the next closing backtick+semicolon after the marker
        close_idx = modified.find(css_close, css_end_idx)
        if close_idx >= 0:
            # Escape the new CSS for JSON embedding
            escaped_css = NEW_CSS.replace('\n', '\\n').replace('"', '\\"').replace("'", "\\'")
            # Insert new CSS before the closing
            insert_point = close_idx
            modified = modified[:insert_point] + escaped_css + modified[insert_point:]
            change_count += 1
            print(f'[OK] Injected new CSS styles ({len(NEW_CSS)} chars)')
    else:
        print('[WARN] Could not find CSS injection point')

    # Apply all code replacements
    replacements = get_replacements(ICON_URL)
    for i, (old, new) in enumerate(replacements):
        # Escape for JSON context - the _elementor_data stores JS as JSON-escaped strings
        old_escaped = old.replace('\n', '\\n').replace('"', '\\"')
        new_escaped = new.replace('\n', '\\n').replace('"', '\\"')

        if old_escaped in modified:
            modified = modified.replace(old_escaped, new_escaped, 1)
            change_count += 1
            label = old[:60].replace('\n', ' ').strip()
            print(f'[OK] Replacement {i+1}: {label}...')
        else:
            # Try without the escaped quotes (some parts may differ)
            old_alt = old.replace('\n', '\\n')
            new_alt = new.replace('\n', '\\n')
            if old_alt in modified:
                modified = modified.replace(old_alt, new_alt, 1)
                change_count += 1
                label = old[:60].replace('\n', ' ').strip()
                print(f'[OK] Replacement {i+1} (alt): {label}...')
            else:
                label = old[:80].replace('\n', ' ').strip()
                print(f'[MISS] Replacement {i+1}: {label}...')

    # Apply raw replacements (for patterns with tricky escaping like regex)
    raw_replacements = get_raw_replacements(ICON_URL)
    for i, (old_raw, new_raw) in enumerate(raw_replacements):
        if old_raw in modified:
            modified = modified.replace(old_raw, new_raw, 1)
            change_count += 1
            print(f'[OK] Raw replacement {i+1}: aiSay avatar injection')
        else:
            print(f'[MISS] Raw replacement {i+1}: aiSay (checking data...)')
            # Debug: show what's around aiSay in the data
            idx = modified.find('async function aiSay')
            if idx >= 0:
                snippet = modified[idx:idx+300]
                print(f'  Found aiSay at {idx}, starts with: {snippet[:150]}...')

    print(f'\n[SUMMARY] {change_count} changes applied to page {page_id}')

    if change_count == 0:
        print('[WARN] No changes made - nothing to save')
        return False

    if modified == elem_data:
        print('[WARN] No actual changes detected after replacements')
        return False

    # Save back
    if dry_run:
        print(f'[DRY RUN] Would save {len(modified)} chars to page {page_id}')
        return True

    save_data = {'meta': {'_elementor_data': modified}}
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json=save_data
    )

    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {page_id} ({len(modified)} chars)')
        return True
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False


def clear_caches():
    """Clear Elementor and other caches."""
    print('\n--- Clearing caches ---')
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r.status_code}')


def main():
    parser = argparse.ArgumentParser(description='Upgrade pay-test chat UI')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--page', type=int, help='Apply to specific page only')
    args = parser.parse_args()

    pages = [args.page] if args.page else PAGES
    results = {}

    for page_id in pages:
        success = apply_to_page(page_id, dry_run=args.dry_run)
        results[page_id] = success

    if not args.dry_run and any(results.values()):
        clear_caches()

    print('\n' + '='*60)
    print('RESULTS:')
    for page_id, success in results.items():
        status = 'SUCCESS' if success else 'FAILED'
        print(f'  Page {page_id}: {status}')
    print('='*60)

    return all(results.values())


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
