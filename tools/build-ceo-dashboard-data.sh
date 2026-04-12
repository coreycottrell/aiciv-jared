#!/usr/bin/env bash
# build-ceo-dashboard-data.sh
# Generates ceo-dashboard/data.json from live sources at deploy time.
# Run before wrangler deploy.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_FILE="$REPO_ROOT/exports/cf-pages-deploy/ceo-dashboard/data.json"
SPOTS_STATE="$REPO_ROOT/logs/spots_state.json"
PORTAL_CHAT="/home/jared/purebrain_portal/portal-chat.jsonl"

echo "[build-ceo-dashboard-data] Building $OUT_FILE ..."

REPO_ROOT="$REPO_ROOT" python3 - <<'PYEOF'
import json, datetime, os, sys, subprocess

repo_root = os.environ.get('REPO_ROOT', '')

out_file      = os.path.join(repo_root, 'exports/cf-pages-deploy/ceo-dashboard/data.json')
spots_file    = os.path.join(repo_root, 'logs/spots_state.json')
portal_chat   = '/home/jared/purebrain_portal/portal-chat.jsonl'

# ── 1. Spots + Revenue ───────────────────────────────────────────────────────
with open(spots_file) as f:
    spots = json.load(f)

spots_claimed = spots.get('spots_claimed', 0)
spots_total   = spots.get('spots_total', 25)
orders        = spots.get('claimed_orders', [])

tier_prices = {
    'awakened':  149,
    'partnered': 499,
    'unified':   999,
    'insiders':  197,
}

tier_counts = {k: 0 for k in tier_prices}
for order in orders:
    t = order.get('tier', '').lower().strip()
    if t in tier_counts:
        tier_counts[t] += 1

mrr = sum(tier_counts[t] * tier_prices[t] for t in tier_counts)
arr = mrr * 12
total_customers = sum(tier_counts.values())
avg_ticket = round(mrr / total_customers, 2) if total_customers > 0 else 0
spots_remaining = spots_total - spots_claimed

# ── 2. Operations Feed — today's assistant messages ──────────────────────────
feed = []
now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
# Start of today UTC
today_start = int(datetime.datetime(now_utc.year, now_utc.month, now_utc.day,
                                     tzinfo=datetime.timezone.utc).timestamp())

type_map = [
    (['deploy', 'ship', 'launch', 'wrangler', 'pages', 'cf pages'],      'type-build',    '🚀'),
    (['blog', 'post', 'article', 'publish', 'audio', 'tts', 'elevenlabs'],'type-content',  '📝'),
    (['security', 'auth', 'fix', 'vulnerability', 'bypass', 'gate'],      'type-security', '🔒'),
    (['email', 'inbox', 'message', 'triage', 'respond'],                   'type-comms',    '📧'),
    (['verify', 'check', 'scan', 'audit', 'pass', 'complete', 'done'],    'type-check',    '✅'),
    (['build', 'agent', 'dashboard', 'module', 'training', 'portal'],     'type-build',    '🏗️'),
]

def classify(text):
    tl = text.lower()
    for keywords, css_type, icon in type_map:
        if any(k in tl for k in keywords):
            return css_type, icon
    return 'type-build', '🤖'

if os.path.exists(portal_chat):
    with open(portal_chat) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                m = json.loads(line)
                if m.get('role') != 'assistant':
                    continue
                ts = m.get('timestamp', 0)
                if ts < today_start:
                    continue
                text = m.get('text', '').strip()
                if not text:
                    continue
                # Strip markdown bold markers for display
                display = text.replace('**', '').replace('__', '')[:110]
                css_type, icon = classify(text)
                dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
                # Convert to ET (UTC-4 in EDT, UTC-5 in EST — use simple offset)
                et_hour = (dt.hour - 4) % 24
                time_str = f'{et_hour:02d}:{dt.minute:02d}'
                feed.append({
                    'time': time_str,
                    'icon': icon,
                    'type': css_type,
                    'text': display,
                    'ts': ts,
                })
            except Exception:
                pass
    # Sort newest first
    feed.sort(key=lambda x: x['ts'], reverse=True)
    feed = feed[:20]  # cap at 20 items

# ── 3. Payment verification ──────────────────────────────────────────────────
verify_script = os.path.join(repo_root, 'tools/verify-payment-pages.sh')
payment_status = {'checked': False, 'result': 'Skipped', 'summary': ''}
try:
    result = subprocess.run(
        ['bash', verify_script],
        capture_output=True, text=True, timeout=60
    )
    output = result.stdout + result.stderr
    # Find RESULTS line
    for line in output.splitlines():
        if 'RESULTS' in line or 'PASS' in line or 'FAIL' in line or '/' in line:
            payment_status['summary'] = line.strip()[:120]
            break
    payment_status['checked'] = True
    payment_status['result'] = 'Pass' if result.returncode == 0 else 'See Summary'
    payment_status['raw'] = output[-500:] if len(output) > 500 else output
except Exception as e:
    payment_status['result'] = f'Error: {e}'

# ── 4. Build timestamp ───────────────────────────────────────────────────────
built_at = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

# ── 5. Assemble output ───────────────────────────────────────────────────────
data = {
    'built_at': built_at,
    'spots': {
        'claimed': spots_claimed,
        'total': spots_total,
        'remaining': spots_remaining,
        'pct': round(spots_claimed / spots_total * 100, 1) if spots_total else 0,
    },
    'revenue': {
        'mrr': mrr,
        'arr': arr,
        'total_customers': total_customers,
        'avg_ticket': avg_ticket,
        'tiers': {
            'awakened':  {'count': tier_counts['awakened'],  'price': tier_prices['awakened']},
            'partnered': {'count': tier_counts['partnered'], 'price': tier_prices['partnered']},
            'unified':   {'count': tier_counts['unified'],   'price': tier_prices['unified']},
            'insiders':  {'count': tier_counts['insiders'],  'price': tier_prices['insiders']},
        },
    },
    'feed': feed,
    'payment_verification': payment_status,
}

with open(out_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f'[build-ceo-dashboard-data] Done.')
print(f'  Spots: {spots_claimed}/{spots_total}')
print(f'  MRR: ${mrr:,}  ARR: ${arr:,}  Customers: {total_customers}')
print(f'  Feed items: {len(feed)}')
print(f'  Output: {out_file}')
PYEOF

echo "[build-ceo-dashboard-data] Complete."
