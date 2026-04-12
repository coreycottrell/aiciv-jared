#!/usr/bin/env python3
"""
Update PureBrain.ai Blog Page (ID 319) Social Icons:
1. Add X/Twitter icon to both social sections
2. Remove orange borders from social icons (update CSS)

ONLY alters social icon sections and CSS border definitions.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
BASE = 'https://purebrain.ai/wp-json/wp/v2'
PAGE_ID = 319

# X/Twitter SVG icon (official X logo)
X_ICON_SVG = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'

X_ICON_LINK = '''        <a href="https://x.com/PureBrainAI" class="social-link x-twitter" aria-label="X (Twitter)" rel="noopener noreferrer" target="_blank">
            {svg}
        </a>'''.format(svg=X_ICON_SVG)

def main():
    if not AUTH[1]:
        print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set in .env")
        return 1

    print("=" * 60)
    print("PureBrain Blog Page 319 - Social Icons Update")
    print("=" * 60)

    # Fetch page
    print("\n[1] Fetching page 319...")
    r = requests.get(f'{BASE}/pages/{PAGE_ID}?context=edit', auth=AUTH, timeout=30)
    if r.status_code != 200:
        print(f"ERROR: {r.status_code} - {r.text[:200]}")
        return 1

    data = r.json()
    content = data['content']['raw']
    print(f"  Content length: {len(content)} chars")

    # --- CHANGE 1: Add X/Twitter icon to both social sections ---
    # The X icon goes AFTER Instagram and BEFORE </div> (closing social-links div)
    # Pattern: Instagram closing </a>\n    </div> -> insert X before    </div>

    # First social section (top of page)
    INSTA_END_PATTERN_1 = '2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>\n        </a>\n    </div>\n</div>\n\n<div class="neural-divider">'
    INSTA_END_REPLACEMENT_1 = '2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>\n        </a>\n{x_icon}\n    </div>\n</div>\n\n<div class="neural-divider">'.format(x_icon=X_ICON_LINK)

    # Second social section (footer)
    INSTA_END_PATTERN_2 = '2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>\n        </a>\n    </div>\n</div>\n\n<style>\n/* ========== BLOG PAGE COLOR FIXES'
    INSTA_END_REPLACEMENT_2 = '2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>\n        </a>\n{x_icon}\n    </div>\n</div>\n\n<style>\n/* ========== BLOG PAGE COLOR FIXES'.format(x_icon=X_ICON_LINK)

    # --- CHANGE 2: Update CSS to remove orange borders ---
    # Original .social-link CSS has:
    #   border: 1px solid rgba(255, 255, 255, 0.1);
    #   -webkit-tap-highlight-color: rgba(241, 66, 11, 0.3);
    # And .social-link:hover has: border-color: #f1420b;
    # We want: remove border entirely, remove orange tap-highlight

    OLD_BASE_CSS = '''    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #ffffff;
    text-decoration: none;
    transition: all 0.3s ease;
    font-size: 1.3rem;
    /* Ensure tap area covers full element */
    touch-action: manipulation;
    -webkit-tap-highlight-color: rgba(241, 66, 11, 0.3);'''

    NEW_BASE_CSS = '''    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: #ffffff;
    text-decoration: none;
    transition: all 0.3s ease;
    font-size: 1.3rem;
    /* Ensure tap area covers full element */
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;'''

    OLD_HOVER_CSS = '''.social-link:hover {
    background: rgba(241, 66, 11, 0.2);
    border-color: #f1420b;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(241, 66, 11, 0.3);
    color: #f1420b;
}'''

    NEW_HOVER_CSS = '''.social-link:hover {
    background: rgba(42, 147, 193, 0.15);
    border-color: transparent;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(42, 147, 193, 0.2);
    color: #2a93c1;
}'''

    # X icon hover CSS - add after existing .social-link.twitter:hover rule
    OLD_TWITTER_HOVER = '.social-link.twitter:hover { background: rgba(255, 255, 255, 0.1); border-color: #ffffff; color: #ffffff; }'
    NEW_TWITTER_HOVER = '.social-link.twitter:hover { background: rgba(255, 255, 255, 0.1); border-color: transparent; color: #ffffff; }\n.social-link.x-twitter:hover { background: rgba(255, 255, 255, 0.1); border-color: transparent; color: #ffffff; }'

    # Apply all changes
    new_content = content

    # Verify patterns exist before replacing
    changes = [
        ("Social section 1 - X icon", INSTA_END_PATTERN_1, INSTA_END_REPLACEMENT_1),
        ("Social section 2 - X icon", INSTA_END_PATTERN_2, INSTA_END_REPLACEMENT_2),
        ("Base CSS border removal", OLD_BASE_CSS, NEW_BASE_CSS),
        ("Hover CSS orange removal", OLD_HOVER_CSS, NEW_HOVER_CSS),
        ("Twitter hover border removal", OLD_TWITTER_HOVER, NEW_TWITTER_HOVER),
    ]

    for label, old, new in changes:
        count = new_content.count(old)
        if count == 0:
            print(f"\nWARNING: Pattern not found: {label}")
            print(f"  Looking for: {old[:80]!r}...")
        elif count > 1:
            print(f"\nWARNING: Pattern found {count} times: {label} - replacing all")
            new_content = new_content.replace(old, new)
        else:
            print(f"\n  OK: {label} (found 1 match)")
            new_content = new_content.replace(old, new)

    print(f"\n[2] Content size: {len(content)} -> {len(new_content)} chars")

    if new_content == content:
        print("ERROR: No changes made! Check patterns.")
        return 1

    # Update page
    print("\n[3] Updating page 319...")
    update_r = requests.post(
        f'{BASE}/pages/{PAGE_ID}',
        auth=AUTH,
        json={'content': new_content},
        timeout=60
    )

    if update_r.status_code in (200, 201):
        print(f"  SUCCESS! Status: {update_r.status_code}")
        updated = update_r.json()
        print(f"  Modified: {updated.get('modified', 'unknown')}")
        return 0
    else:
        print(f"  ERROR: {update_r.status_code}")
        print(f"  Response: {update_r.text[:500]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
