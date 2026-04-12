#!/usr/bin/env python3
"""
EXECUTE: Fetch sandbox-3, pay-test-5, sandbox-5. Analyze and fix pricing section.
"""
import os, sys, json, re, requests
from requests.auth import HTTPBasicAuth

WP_USER = "purebrain@puremarketing.ai"
WP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE    = "https://purebrain.ai/wp-json/wp/v2/pages"
LIVE_ID = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"
SAND_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"
DIR     = "/home/jared/projects/AI-CIV/aether/exports/cto-pricing-fix"

auth = HTTPBasicAuth(WP_USER, WP_PASS)
os.makedirs(DIR, exist_ok=True)

def fetch(pid):
    r = requests.get(f"{BASE}/{pid}?context=edit", auth=auth, timeout=30)
    print(f"  GET page {pid}: HTTP {r.status_code}")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:300]}")
        return None
    return r.json()

def raw(data):
    return data.get("content", {}).get("raw", "")

def save(name, content):
    p = f"{DIR}/{name}"
    with open(p, "w") as f: f.write(content)
    print(f"  Saved {p} ({len(content):,} chars)")

def post(pid, content):
    r = requests.post(f"{BASE}/{pid}", auth=auth, json={"content": content}, timeout=60)
    print(f"  POST page {pid}: HTTP {r.status_code}")
    if r.status_code not in (200, 201):
        print(f"  ERROR: {r.text[:400]}")
        return False
    return True

def bust_cache():
    r = requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth, timeout=30)
    print(f"  Cache bust: HTTP {r.status_code}")

def markers(html, label):
    keys = ["Reserve Keen Now","Activate Keen Now",'id="pricing"',"pricing-section",
            "Claude Max Account","Requirement:","paypal.com/sdk",LIVE_ID[:25],SAND_ID[:25],
            "Fully Online","wp:html","wp-block-html"]
    print(f"\n  Markers in {label}:")
    for k in keys:
        i = html.find(k)
        if i >= 0:
            ctx = html[max(0,i-40):i+80].replace('\n',' ')
            print(f"    [{i:7d}] FOUND '{k}': ...{ctx}...")
        else:
            print(f"    [      -] not found: '{k}'")

def extract_section_by_id(html, sid):
    """Find <section id="sid"> and extract it with balanced tag counting."""
    pat = rf'<(section|div)[^>]+id=["\']' + re.escape(sid) + r'["\'][^>]*>'
    m = re.search(pat, html)
    if not m:
        print(f"  Not found: element with id='{sid}'")
        return None, None
    tag = m.group(1)  # 'section' or 'div'
    start = m.start()
    print(f"  Found <{tag} id='{sid}'> at position {start}")
    depth, pos = 0, start
    open_pat  = re.compile(rf'<{tag}[\s>]', re.IGNORECASE)
    close_pat = re.compile(rf'</{tag}>', re.IGNORECASE)
    while pos < len(html):
        o = open_pat.search(html, pos)
        c = close_pat.search(html, pos)
        if not c: break
        o_pos = o.start() if o else len(html)+1
        c_pos = c.start()
        if o_pos < c_pos:
            depth += 1; pos = o_pos + 1
        else:
            depth -= 1
            if depth == 0:
                end = c.end()
                return start, end
            pos = c_pos + 1
    print(f"  Could not find matching close tag for id='{sid}'")
    return None, None

def swap_paypal(html, target_id):
    """Replace any known PayPal client-id with target_id."""
    for cid in [LIVE_ID, SAND_ID]:
        if cid in html and cid != target_id:
            html = html.replace(cid, target_id)
            print(f"  PayPal: swapped ...{cid[:20]}... -> ...{target_id[:20]}...")
        elif cid in html:
            print(f"  PayPal: already correct (...{target_id[:20]}...)")
    return html

# ==================== MAIN ====================
print("=" * 60)
print("CTO FIX: pay-test-5 (1527) + sandbox-5 (1528) pricing section")
print("=" * 60)

print("\n[FETCH]")
d1232 = fetch(1232)  # sandbox-3 (source) - CORRECT page ID
d1527 = fetch(1527)  # pay-test-5
d1528 = fetch(1528)  # sandbox-5

if not all([d1232, d1527, d1528]):
    print("FATAL: Failed to fetch one or more pages.")
    sys.exit(1)

r1232 = raw(d1232)
r1527 = raw(d1527)
r1528 = raw(d1528)

print(f"\n  1232 sandbox-3:  {len(r1232):,} chars")
print(f"  1527 pay-test-5: {len(r1527):,} chars")
print(f"  1528 sandbox-5:  {len(r1528):,} chars")

# Save originals
save("1232-sandbox3-orig.html", r1232)
save("1527-paytest5-orig.html", r1527)
save("1528-sandbox5-orig.html", r1528)

# Analyze
markers(r1232, "sandbox-3 (1232)")
markers(r1527, "pay-test-5 (1527)")
markers(r1528, "sandbox-5 (1528)")

# Extract the pricing section from sandbox-3
print("\n[EXTRACT PRICING FROM SANDBOX-3]")
s_start, s_end = extract_section_by_id(r1232, "pricing")
if s_start is None:
    print("FATAL: Cannot extract #pricing from sandbox-3.")
    print(f"Inspect: {DIR}/1232-sandbox3-orig.html")
    sys.exit(1)

sb3_pricing = r1232[s_start:s_end]
save("sandbox3-pricing-extracted.html", sb3_pricing)
print(f"  Extracted: {len(sb3_pricing):,} chars")

# Verify the extracted content
checks = [
    ("Activate Keen Now", True),
    ("Reserve Keen Now",  False),
    ("Claude Max",        True),
    ("Requirement",       True),
]
for text, should_exist in checks:
    found = text in sb3_pricing
    ok = "OK" if found == should_exist else "WARN"
    print(f"  [{ok}] '{text}': {'found' if found else 'not found'} (expected: {'found' if should_exist else 'not found'})")

# ---- FIX pay-test-5 (1527) LIVE PayPal ----
print("\n[FIX pay-test-5 (1527) — LIVE PayPal]")
pt5_s, pt5_e = extract_section_by_id(r1527, "pricing")

if pt5_s is None:
    print("  #pricing section NOT found in pay-test-5. Trying 'Reserve Keen Now' context search...")
    reserve_idx = r1527.find("Reserve Keen Now")
    if reserve_idx >= 0:
        print(f"  'Reserve Keen Now' at pos {reserve_idx}")
        ctx = r1527[max(0,reserve_idx-2000):reserve_idx+2000]
        save("1527-reserve-context.html", ctx)
        print(f"  Context saved. Manual inspection required.")
    else:
        print("  Neither #pricing nor 'Reserve Keen Now' found in pay-test-5!")
    pt5_ok = False
else:
    old_pt5 = r1527[pt5_s:pt5_e]
    save("1527-old-pricing.html", old_pt5)

    new_pricing_live = swap_paypal(sb3_pricing, LIVE_ID)
    new_r1527 = r1527[:pt5_s] + new_pricing_live + r1527[pt5_e:]
    # Also swap any stray PayPal IDs elsewhere in the page
    new_r1527 = swap_paypal(new_r1527, LIVE_ID)
    save("1527-paytest5-new.html", new_r1527)

    print(f"  New content: {len(new_r1527):,} chars")
    print(f"  Deploying...")
    pt5_ok = post(1527, new_r1527)

# ---- FIX sandbox-5 (1528) SANDBOX PayPal ----
print("\n[FIX sandbox-5 (1528) — SANDBOX PayPal]")
s5_s, s5_e = extract_section_by_id(r1528, "pricing")

if s5_s is None:
    print("  #pricing section NOT found in sandbox-5. Trying 'Reserve Keen Now' context search...")
    reserve_idx = r1528.find("Reserve Keen Now")
    if reserve_idx >= 0:
        print(f"  'Reserve Keen Now' at pos {reserve_idx}")
        ctx = r1528[max(0,reserve_idx-2000):reserve_idx+2000]
        save("1528-reserve-context.html", ctx)
    s5_ok = False
else:
    old_s5 = r1528[s5_s:s5_e]
    save("1528-old-pricing.html", old_s5)

    new_pricing_sand = swap_paypal(sb3_pricing, SAND_ID)
    new_r1528 = r1528[:s5_s] + new_pricing_sand + r1528[s5_e:]
    new_r1528 = swap_paypal(new_r1528, SAND_ID)
    save("1528-sandbox5-new.html", new_r1528)

    print(f"  New content: {len(new_r1528):,} chars")
    print(f"  Deploying...")
    s5_ok = post(1528, new_r1528)

# ---- Clear Elementor cache ----
print("\n[CACHE BUST]")
bust_cache()

# ---- Summary ----
print("\n" + "=" * 60)
print("RESULT SUMMARY")
print("=" * 60)
print(f"  pay-test-5 (1527): {'SUCCESS' if pt5_ok else 'NEEDS MANUAL FIX'}")
print(f"  sandbox-5  (1528): {'SUCCESS' if s5_ok else 'NEEDS MANUAL FIX'}")
print(f"  Files: {DIR}/")
print("\nQA STEPS:")
print("  1. Visit pay-test-5 page, go through chatbox flow, see pricing")
print("     Expect: 'Activate Keen Now', 'Requirement: Claude Max Account', PayPal modal")
print("  2. Visit sandbox-5 page, same flow")
print("     Expect: same but sandbox PayPal client ID")
print("  3. Hero, testimonials, video sections unchanged")
