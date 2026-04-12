#!/usr/bin/env python3
"""
Add blog link to pricing section on the homepage (page 11)
2026-02-20

Task: Add "Read Our Blog" link to the pricing section's teams/individual tier area
- Adds a subtle blog link below the pricing steps section
- Links to https://purebrain.ai/blog/
- Styled to match the page's dark theme
"""

import json
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_URL = "https://purebrain.ai"
USER = "Aether"
APP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
PAGE_ID = 11
AUTH = (USER, APP_PASS)

# Blog link HTML to insert - styled to match the dark theme
BLOG_LINK_HTML = (
    '\n            <div class="pricing-blog-link" style="text-align: center; '
    'margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.08);">'
    '\n                <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; '
    'margin-bottom: 10px;">Want to learn more about AI partnerships before diving in?</p>'
    '\n                <a href="https://purebrain.ai/blog/?utm_source=pricing'
    '&amp;utm_medium=link&amp;utm_campaign=pricing_blog" '
    'style="color: #2a93c1; text-decoration: none; font-weight: 600; font-size: 0.95rem;" '
    'onmouseover="this.style.color=\'#5ab8e0\'" onmouseout="this.style.color=\'#2a93c1\'">'
    'Read Our Blog &rarr;</a>'
    '\n            </div>'
)


def main():
    print(f"Fetching homepage (page {PAGE_ID})...")
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
        params={"context": "edit"},
        auth=AUTH
    )
    r.raise_for_status()
    page = r.json()
    content = page['content']['raw']
    print(f"Content length: {len(content)} chars")

    # Check if blog link already inserted
    if 'pricing-blog-link' in content:
        print("Blog link already exists! Skipping.")
        return True

    # Find the pricing__steps section and its closing
    steps_idx = content.find('<div class="pricing__steps">')
    if steps_idx < 0:
        print("ERROR: Could not find pricing__steps div!")
        return False

    print(f"Found pricing__steps at position {steps_idx}")

    # After pricing__steps, find the closing sequence
    # The structure is:
    #   <div class="pricing__steps">
    #     ...
    #   </div>          <- closes pricing__steps
    # </div>            <- closes pricing section container
    # </section>        <- closes the section
    #
    # We want to insert our blog link before the </div>\n        </div>\n    </section>

    # Find the end of pricing__steps div
    # The pricing section container closes with 2 </div> tags then </section>
    # Looking at the repr: '            </div>\n        </div>\n    </section>\n\n    <!-- COMPETITIVE'

    # Find the COMPETITIVE COMPARISON comment that follows the pricing section
    competitive_idx = content.find('COMPETITIVE COMPARISON (reveals after awakening)', steps_idx)
    if competitive_idx < 0:
        print("ERROR: Could not find COMPETITIVE COMPARISON section marker!")
        return False

    print(f"Found COMPETITIVE COMPARISON at position {competitive_idx}")

    # The text we need to insert before is the </div>\n        </div>\n    </section> near the competitive marker
    # Search backwards from competitive_idx for </section>
    section_end_idx = content.rfind('</section>', steps_idx, competitive_idx)
    if section_end_idx < 0:
        print("ERROR: Could not find </section> before competitive comparison!")
        return False

    print(f"Found </section> at position {section_end_idx}")
    print(f"Context: ...{repr(content[max(0,section_end_idx-100):section_end_idx+20])}...")

    # Insert the blog link just before the </div>\n        </div>\n    </section>
    # Find the </div>\n        </div> before </section>
    div_before_section = content.rfind('</div>', steps_idx, section_end_idx)
    print(f"Found last </div> before </section> at position {div_before_section}")
    print(f"Context: ...{repr(content[max(0,div_before_section-50):div_before_section+30])}...")

    # The insert position should be AFTER the pricing__steps </div> (first close)
    # and BEFORE the outer container </div>
    # Let's find the exact close of pricing__steps
    # Structure: <div class="pricing__steps">...</div>\n        </div>\n    </section>
    # We want to insert after the first </div> (pricing__steps close)

    # Find the closing </div> of pricing__steps div
    # by looking for </div> after the list close
    steps_end = content.find('</div>\n        </div>\n    </section>', steps_idx)
    if steps_end < 0:
        # Try with different whitespace
        steps_end = content.find('</div>\n            </div>', steps_idx)
        if steps_end < 0:
            print("Trying alternative closing pattern...")
            # Find closest </div> before section end
            steps_end = div_before_section
            print(f"Using div_before_section: {steps_end}")

    print(f"steps_end: {steps_end}")

    if steps_end < 0:
        print("ERROR: Could not find insertion point!")
        return False

    # Insert after the pricing__steps closing </div>
    # The text at steps_end should be: </div>\n        </div>\n    </section>
    closing_text = content[steps_end:steps_end + 10]
    print(f"Text at insertion point: {repr(closing_text)}")

    # Insert blog link after the </div> at steps_end
    insert_pos = steps_end + len('</div>')
    new_content = content[:insert_pos] + BLOG_LINK_HTML + content[insert_pos:]

    print(f"New content length: {len(new_content)} chars")
    print(f"Blog link will appear at: {insert_pos}")

    # Verify the insertion
    if 'pricing-blog-link' not in new_content:
        print("ERROR: Blog link not found in new content after insertion!")
        return False

    # Show what was inserted
    verify_idx = new_content.find('pricing-blog-link')
    print(f"Blog link context: ...{new_content[max(0,verify_idx-50):verify_idx+200]}...")

    print("\nUpdating page via REST API...")
    update_r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
        auth=AUTH,
        json={"content": {"raw": new_content}}
    )
    update_r.raise_for_status()
    result = update_r.json()
    print(f"Updated! Modified: {result.get('modified', '?')}")

    # Clear Elementor cache
    print("Clearing Elementor cache...")
    try:
        cache_r = requests.delete(
            f"{WP_URL}/wp-json/elementor/v1/cache",
            auth=AUTH
        )
        print(f"Cache cleared: {cache_r.status_code}")
    except Exception as e:
        print(f"Cache clear: {e}")

    # Also flush GoDaddy CDN cache
    print("Flushing CDN cache...")
    try:
        cdn_r = requests.post(
            f"{WP_URL}/wp-json/wpaas/v1/flush-cache",
            auth=AUTH
        )
        print(f"CDN cache: {cdn_r.status_code} - {cdn_r.text[:100]}")
    except Exception as e:
        print(f"CDN cache: {e}")

    return True


if __name__ == '__main__':
    result = main()
    print(f"\n{'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
