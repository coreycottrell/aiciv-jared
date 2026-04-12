#!/usr/bin/env python3
"""FIX 3: Reset rate limiter and reduce tightening multiplier from 1.2x to 1.1x."""
import json, sys

# Part A: Reset the rate limits state file
rate_file = '/opt/baas/proactive_rate_limits.json'
try:
    with open(rate_file, 'r') as f:
        state = json.load(f)
except:
    state = {}

# Reset linkedin.com entry
state['linkedin.com'] = {
    "tightening_factor": 1.0,
    "total_429s": 0,
    "last_429": None,
    "cooldown_until": 0,
    "blocked_requests": 0,
    "navigations": [],
    "actions": [],
    "sessions": []
}

with open(rate_file, 'w') as f:
    json.dump(state, f, indent=2)
print("FIX 3a: Reset linkedin.com rate limits (tightening_factor=1.0, total_429s=0, cooldown=0)")

# Part B: Reduce tightening multiplier from 1.2 to 1.1 in baas_server_simple.py
filepath = '/opt/baas/baas_server_simple.py'
with open(filepath, 'r') as f:
    content = f.read()

old_tighten = "tracker['tightening_factor'] = min(3.0, old_tf * 1.2)  # Cap at 3x tighter"
new_tighten = "tracker['tightening_factor'] = min(2.0, old_tf * 1.1)  # Cap at 2x tighter (reduced from 1.2/3.0)"

count = content.count(old_tighten)
if count == 0:
    print("WARNING: Could not find tightening multiplier line to replace")
    # Try alternate form
    old_tighten2 = "tracker['tightening_factor'] = min(3.0, old_tf * 1.2)"
    count2 = content.count(old_tighten2)
    if count2 > 0:
        content = content.replace(old_tighten2, new_tighten)
        print(f"FIX 3b: Reduced tightening multiplier 1.2->1.1, cap 3.0->2.0 ({count2} occurrences)")
    else:
        print("ERROR: Could not find any tightening multiplier to modify")
        sys.exit(1)
else:
    content = content.replace(old_tighten, new_tighten)
    print(f"FIX 3b: Reduced tightening multiplier 1.2->1.1, cap 3.0->2.0 ({count} occurrences)")

with open(filepath, 'w') as f:
    f.write(content)

print("FIX 3: COMPLETE — Rate limiter reset and tightening reduced")
