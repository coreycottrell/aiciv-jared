#!/usr/bin/env python3
"""Post-deployment verification: confirm new text present, old text gone."""
import json
import subprocess

USER = "Aether"
PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_IDS = [688, 689, 468, 439]

def fetch_page(page_id):
    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit"
    result = subprocess.run(
        ["curl", "-s", "-u", f"{USER}:{PASS}",
         "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
         url],
        capture_output=True, text=True
    )
    return result.stdout

OLD_UNIQUE = "make sure you're logged into Telegram"
NEW_UNIQUE_1 = "If you're on a desktop, visit"
NEW_UNIQUE_2 = "telegram.org/dl"

all_pass = True

for page_id in PAGE_IDS:
    raw = fetch_page(page_id)
    data = json.loads(raw)
    content = data.get('content', {}).get('raw', '')
    elementor = data.get('meta', {}).get('_elementor_data', '') or ''

    # Check old text is gone
    old_in_pc = OLD_UNIQUE in content
    old_in_ed = OLD_UNIQUE in elementor

    # Check new text is present
    new1_in_pc = NEW_UNIQUE_1 in content
    new1_in_ed = NEW_UNIQUE_1 in elementor
    new2_in_pc = NEW_UNIQUE_2 in content
    new2_in_ed = NEW_UNIQUE_2 in elementor

    pc_pass = (not old_in_pc) and new1_in_pc and new2_in_pc
    ed_pass = (not old_in_ed) and new1_in_ed and new2_in_ed

    status = "PASS" if (pc_pass and ed_pass) else "FAIL"
    if not (pc_pass and ed_pass):
        all_pass = False

    print(f"Page {page_id}: {status}")
    print(f"  post_content  - old_gone={not old_in_pc}, new_desktop={new1_in_pc}, new_dl={new2_in_pc}")
    print(f"  _elementor    - old_gone={not old_in_ed}, new_desktop={new1_in_ed}, new_dl={new2_in_ed}")

    # Show the actual new text in context
    idx = content.find(NEW_UNIQUE_1)
    if idx != -1:
        start = content.rfind("// --- BotFather", max(0, idx-300), idx)
        if start == -1:
            start = max(0, idx-50)
        print(f"  Actual new text in post_content:")
        print(f"    {repr(content[idx:idx+len(NEW_UNIQUE_1)+200])}")
    print()

print("=" * 40)
print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
