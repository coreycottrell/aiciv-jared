#!/usr/bin/env python3
"""
update_transparency_data.py
===========================
Updates the Aether Transparency Section data on purebrain.ai and jareddsanborn.com.
Calls POST /wp-json/purebrain/v1/transparency-data on each site.

Usage
-----
1. Pass a JSON file:
   python3 tools/update_transparency_data.py --file /path/to/transparency.json

2. Pass individual args (minimal):
   python3 tools/update_transparency_data.py \\
       --week-of "February 17, 2026" \\
       --summary "This week the collective completed..." \\
       --biggest-win "The AI adoption assessment went live." \\
       --agents 14 --domains 5 --deliverables "28+" --hours "80-120"

3. Full example with work breakdown (JSON string):
   python3 tools/update_transparency_data.py \\
       --week-of "February 17, 2026" \\
       --summary "..." \\
       --biggest-win "..." \\
       --agents 14 --domains 5 --deliverables "28+" --hours "80-120" \\
       --breakdown '[{"domain":"Engineering","description":"...","effort":"High","value":"Significant"}]'

Environment
-----------
Reads from .env in the aether project root:
  PUREBRAIN_WP_USER          WordPress user for purebrain.ai (default: Aether)
  PUREBRAIN_WP_APP_PASSWORD  App password for purebrain.ai
  WORDPRESS_USER             WordPress user for jareddsanborn.com (default: AetherPureBrain.ai)
  WORDPRESS_APP_PASSWORD     App password for jareddsanborn.com

Sites updated
-------------
  https://purebrain.ai/wp-json/purebrain/v1/transparency-data
  https://jareddsanborn.com/wp-json/purebrain/v1/transparency-data
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate project root (.env lives here)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # aether/
ENV_FILE = PROJECT_ROOT / '.env'


def load_env() -> dict:
    """Parse the .env file and return a dict of key=value pairs."""
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip("'\"")
        env[key] = value
    return env


# ---------------------------------------------------------------------------
# Target sites configuration
# ---------------------------------------------------------------------------

def build_site_configs(env: dict) -> list:
    """Return list of site config dicts with url, user, password."""
    configs = []

    # purebrain.ai
    pb_user = env.get('PUREBRAIN_WP_USER', 'Aether')
    pb_pass = env.get('PUREBRAIN_WP_APP_PASSWORD', '')
    if pb_pass:
        configs.append({
            'name': 'purebrain.ai',
            'url': 'https://purebrain.ai/wp-json/purebrain/v1/transparency-data',
            'user': pb_user,
            'password': pb_pass,
        })
    else:
        print('[WARN] PUREBRAIN_WP_APP_PASSWORD not set in .env — skipping purebrain.ai')

    # jareddsanborn.com
    jared_user = env.get('WORDPRESS_USER', 'AetherPureBrain.ai')
    jared_pass = env.get('WORDPRESS_APP_PASSWORD', '')
    if jared_pass:
        configs.append({
            'name': 'jareddsanborn.com',
            'url': 'https://jareddsanborn.com/wp-json/purebrain/v1/transparency-data',
            'user': jared_user,
            'password': jared_pass,
        })
    else:
        print('[WARN] WORDPRESS_APP_PASSWORD not set in .env — skipping jareddsanborn.com')

    return configs


# ---------------------------------------------------------------------------
# REST API call
# ---------------------------------------------------------------------------

def post_transparency_data(site: dict, payload: dict) -> dict:
    """POST the transparency data to a single site. Returns response dict."""
    body = json.dumps(payload).encode('utf-8')

    # Basic auth header (WordPress application passwords)
    credentials = f"{site['user']}:{site['password']}"
    b64 = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    req = urllib.request.Request(
        site['url'],
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {b64}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8')
            return {'status': resp.status, 'body': json.loads(raw)}
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='replace')
        try:
            body_json = json.loads(raw)
        except json.JSONDecodeError:
            body_json = {'raw': raw}
        return {'status': e.code, 'body': body_json, 'error': str(e)}
    except urllib.error.URLError as e:
        return {'status': 0, 'body': {}, 'error': str(e)}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description='Update the Aether Transparency Section on all PureBrain sites.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Source: JSON file OR individual args
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        '--file', '-f',
        metavar='PATH',
        help='Path to a JSON file containing the full transparency payload.',
    )

    # Individual field args
    parser.add_argument('--week-of',    metavar='DATE',   help='e.g. "February 17, 2026"')
    parser.add_argument('--summary',    metavar='TEXT',   help='2-3 sentence executive summary (Aether voice).')
    parser.add_argument('--biggest-win', metavar='TEXT',  help='One-sentence biggest win of the week.')
    parser.add_argument('--agents',     metavar='N',      type=int, help='Number of specialist agents.')
    parser.add_argument('--domains',    metavar='N',      type=int, help='Number of work domains covered.')
    parser.add_argument('--deliverables', metavar='STR',  help='e.g. "28+" (string, shown as-is).')
    parser.add_argument('--hours',      metavar='STR',    help='e.g. "80-120" (string, shown as-is).')
    parser.add_argument(
        '--breakdown', metavar='JSON',
        help='JSON array of work breakdown rows: [{"domain":...,"description":...,"effort":...,"value":...}]',
    )
    parser.add_argument(
        '--cta-text', metavar='TEXT',
        help='Optional override for the CTA paragraph text.',
    )

    # Targeting
    parser.add_argument(
        '--site', metavar='NAME',
        choices=['purebrain.ai', 'jareddsanborn.com', 'all'],
        default='all',
        help='Which site to update. Default: all',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Print the payload but do not POST to any site.',
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Build payload
# ---------------------------------------------------------------------------

def build_payload_from_args(args) -> dict:
    """Construct the transparency payload from individual CLI args."""
    if not args.week_of:
        print('[ERROR] --week-of is required when not using --file.', file=sys.stderr)
        sys.exit(1)
    if not args.summary:
        print('[ERROR] --summary is required when not using --file.', file=sys.stderr)
        sys.exit(1)
    if not args.biggest_win:
        print('[ERROR] --biggest-win is required when not using --file.', file=sys.stderr)
        sys.exit(1)

    stats = {
        'specialist_agents': args.agents      or 0,
        'work_domains':      args.domains     or 0,
        'deliverables':      args.deliverables or '0',
        'human_hours':       args.hours        or '0',
    }

    breakdown = []
    if args.breakdown:
        try:
            breakdown = json.loads(args.breakdown)
        except json.JSONDecodeError as e:
            print(f'[ERROR] --breakdown is not valid JSON: {e}', file=sys.stderr)
            sys.exit(1)

    payload = {
        'week_of':        args.week_of,
        'summary':        args.summary,
        'stats':          stats,
        'work_breakdown': breakdown,
        'biggest_win':    args.biggest_win,
    }

    if args.cta_text:
        payload['cta_text'] = args.cta_text

    return payload


def build_payload_from_file(path: str) -> dict:
    """Load transparency payload from a JSON file."""
    p = Path(path)
    if not p.exists():
        print(f'[ERROR] File not found: {path}', file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        print(f'[ERROR] Invalid JSON in {path}: {e}', file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    required = ['week_of', 'summary', 'biggest_win']
    for field in required:
        if field not in data:
            print(f'[ERROR] Missing required field in JSON file: {field}', file=sys.stderr)
            sys.exit(1)

    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    env = load_env()

    # Build payload
    if args.file:
        payload = build_payload_from_file(args.file)
    else:
        payload = build_payload_from_args(args)

    # Ensure stats and work_breakdown keys exist
    if 'stats' not in payload:
        payload['stats'] = {
            'specialist_agents': 0,
            'work_domains': 0,
            'deliverables': '0',
            'human_hours': '0',
        }
    if 'work_breakdown' not in payload:
        payload['work_breakdown'] = []

    print()
    print('=== Aether Transparency Section — Update ===')
    print(f"  Week of:     {payload.get('week_of', '(unset)')}")
    print(f"  Agents:      {payload['stats'].get('specialist_agents', 0)}")
    print(f"  Domains:     {payload['stats'].get('work_domains', 0)}")
    print(f"  Deliverables:{payload['stats'].get('deliverables', '0')}")
    print(f"  Hours:       {payload['stats'].get('human_hours', '0')}")
    print(f"  Rows:        {len(payload['work_breakdown'])}")
    print()

    if args.dry_run:
        print('--- DRY RUN: payload (not sent) ---')
        print(json.dumps(payload, indent=2))
        print()
        return

    # Build site list
    all_configs = build_site_configs(env)
    if not all_configs:
        print('[ERROR] No valid site credentials found in .env. Cannot update any site.', file=sys.stderr)
        sys.exit(1)

    if args.site != 'all':
        configs = [c for c in all_configs if c['name'] == args.site]
        if not configs:
            print(f'[ERROR] Site "{args.site}" not configured or missing credentials.', file=sys.stderr)
            sys.exit(1)
    else:
        configs = all_configs

    # POST to each site
    any_error = False
    for site in configs:
        print(f'Updating {site["name"]} ...')
        result = post_transparency_data(site, payload)
        status = result.get('status', 0)
        body = result.get('body', {})

        if status == 200 and body.get('success'):
            print(f'  [OK]  week_of={body.get("week_of")}  '
                  f'rows={body.get("rows")}  '
                  f'updated_at={body.get("updated_at")}')
        else:
            print(f'  [FAIL] HTTP {status}')
            print(f'         {json.dumps(body, indent=4)}')
            if 'error' in result:
                print(f'         Error: {result["error"]}')
            any_error = True
        print()

    if any_error:
        print('[WARN] One or more sites failed to update.')
        sys.exit(1)
    else:
        print('All sites updated successfully.')


if __name__ == '__main__':
    main()
