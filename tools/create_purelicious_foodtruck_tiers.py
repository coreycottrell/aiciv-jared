#!/usr/bin/env python3
"""Create the Purelicious Food Trucks PayPal product + 3 billing-plan tiers.

PURELY ADDITIVE. Creates ONE dedicated new product + THREE new plans.
Does NOT touch/modify/deactivate any existing product or plan — in particular
the stale Operator $250 plans P-20N28177822286433NITSQVI /
P-49T5523746060730VNITSQCA and product PROD-30N67904YR8674902 are left alone
(retirement is a separate Chy-side task).

Tiers (all USD, MONTH x 1, infinite cycles, no trial, no setup fee):
  Awakened   — $297.00/mo
  Operator   — $497.00/mo
  Enterprise — $1097.00/mo

Uses PayPal REST API v1 (Products + Billing Plans), LIVE environment.
After each create, reads the plan back via GET to verify (NUMERIC price
compare — PayPal strips trailing zeros: "297.00" reads back as "297.0").

═══════════════════════════════════════════════════════════════════════════
MONEY-SAFETY GUARDS (architecture inherited from
tools/create_purelicious_operator_plan.py, added 2026-06-08 after a
double-create race incident)
═══════════════════════════════════════════════════════════════════════════
GUARD 1 — IDEMPOTENCY / CLAIM-LOCK: before any live CREATE, check the
  registry (config/paypal_plan_registry.json, one key per tier). If an ACTIVE
  plan already exists (registry OR live PayPal list), SKIP that tier. An
  atomic O_EXCL lock prevents two concurrent runs from both passing the
  check (defeats the race).

GUARD 2 — AUTONOMOUS-MONEY-CREATE GATE: this path REFUSES to create from an
  autonomous/BOOP context unless an explicit human-confirmation flag + single
  owner (conductor) are present. Fail-closed: if unsure, DO NOT create.

GUARD 3 — PAYPAL-SIDE IDEMPOTENCY: every create sends a fixed
  PayPal-Request-Id header, so a single retry returns the SAME object
  instead of double-creating.

Ratification: Jared ratified the tier ladder 2026-06-11 (relayed via Chy);
conductor is the single money-create owner.
"""

import os
import sys
import json
import errno
import argparse
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')

CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
SECRET = os.getenv('PAYPAL_SECRET', '')

# Live API
BASE = 'https://api-m.paypal.com'

# ── Operation identity (registry/lock keys) ─────────────────────────────────
GATE = 'PURELICIOUS_FT_TIERS'
REGISTRY_PATH = BASE_DIR / 'config' / 'paypal_plan_registry.json'
LOCK_PATH = BASE_DIR / 'config' / f'.paypal_create_lock_{GATE}'
RESULTS_PATH = BASE_DIR / 'config' / 'paypal_plans_purelicious_foodtrucks.json'

PRODUCT = {
    'name': 'Purelicious Food Trucks',
    'description': 'Purelicious AI platform subscription tiers for food truck owners',
    'type': 'SERVICE',
    'category': 'SOFTWARE',
    'home_url': 'https://purebrain.ai',
}
PRODUCT_REQUEST_ID = 'purelicious-ft-product-20260611'
PRODUCT_REG_KEY = 'PURELICIOUS_FT_PRODUCT'

# One registry key per tier. Each carries its own fixed PayPal-Request-Id.
TIERS = [
    {
        'reg_key': 'PURELICIOUS_FT_AWAKENED',
        'name': 'Awakened',
        'description': 'Purelicious Awakened — unlocks your AI',
        'price': '297.00',
        'request_id': 'purelicious-ft-awakened-297usd-20260611',
    },
    {
        'reg_key': 'PURELICIOUS_FT_OPERATOR',
        'name': 'Operator',
        'description': 'Purelicious Operator — AI + heat map + full operations',
        'price': '497.00',
        'request_id': 'purelicious-ft-operator-497usd-20260611',
    },
    {
        'reg_key': 'PURELICIOUS_FT_ENTERPRISE',
        'name': 'Enterprise',
        'description': 'Purelicious Enterprise — fleet',
        'price': '1097.00',
        'request_id': 'purelicious-ft-enterprise-1097usd-20260611',
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# GUARD 2 — Autonomous-money-create gate (fail-closed)
# ═══════════════════════════════════════════════════════════════════════════
def autonomous_context() -> bool:
    """True if this looks like a BOOP / autonomous scheduled execution."""
    if os.getenv('BOOP_TASK_ID'):
        return True
    # boop_executor embeds 'BOOP' in the launched env / task context.
    for k, v in os.environ.items():
        if 'BOOP' in k.upper() or (isinstance(v, str) and 'BOOP [' in v):
            return True
    return False


def human_confirmed(args) -> bool:
    """True only if an explicit human confirmation + owner=conductor is present."""
    flag = bool(getattr(args, 'human_confirmed', False))
    owner = getattr(args, 'owner', None) or os.getenv('PAYPAL_CREATE_OWNER', '')
    env_conf = os.getenv('PAYPAL_CREATE_HUMAN_CONFIRMED', '').lower() == 'yes'
    confirmed = flag or env_conf
    return bool(confirmed and owner == 'conductor')


def check_create_gate(args) -> bool:
    """GUARD 2. Returns True if creation is allowed. Fail-closed."""
    auto = autonomous_context()
    confirmed = human_confirmed(args)
    if confirmed:
        # Explicit human override is the ONLY way to create — even from autonomous ctx.
        return True
    if auto:
        print('[BLOCKED] Live PayPal plan creation requires human confirmation. '
              'Detected autonomous/BOOP context. Re-run with '
              '--human-confirmed --owner conductor (or set '
              'PAYPAL_CREATE_HUMAN_CONFIRMED=yes PAYPAL_CREATE_OWNER=conductor). '
              'Refusing to create from autonomous context.')
        return False
    # Interactive but unconfirmed: still fail-closed for money ops.
    print('[BLOCKED] Live PayPal plan creation requires human confirmation. '
          'Re-run with --human-confirmed --owner conductor '
          '(or set PAYPAL_CREATE_HUMAN_CONFIRMED=yes PAYPAL_CREATE_OWNER=conductor).')
    return False


# ═══════════════════════════════════════════════════════════════════════════
# GUARD 1 — Idempotency / registry / claim-lock
# ═══════════════════════════════════════════════════════════════════════════
def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text())
        except Exception:
            pass
    return {}


def write_registry(reg: dict) -> None:
    tmp = REGISTRY_PATH.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(reg, indent=2))
    os.replace(tmp, REGISTRY_PATH)  # atomic on POSIX


def registry_active_plan(reg_key: str):
    reg = load_registry()
    entry = reg.get(reg_key)
    if entry and entry.get('status') == 'ACTIVE' and entry.get('plan_id'):
        return entry['plan_id']
    return None


def registry_product_id():
    reg = load_registry()
    entry = reg.get(PRODUCT_REG_KEY)
    if entry and entry.get('product_id'):
        return entry['product_id']
    return None


def live_active_plans_by_name(token, product_id) -> dict:
    """Defense-in-depth: list ALL live plans under product_id (paging through),
    return {name: plan_id} for ACTIVE plans."""
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    found = {}
    page = 1
    while True:
        try:
            r = requests.get(
                f'{BASE}/v1/billing/plans?product_id={product_id}'
                f'&page_size=20&page={page}&total_required=true',
                headers=headers, timeout=30)
        except Exception as e:
            print(f'[WARN] Live plan list failed (page {page}): {e} — '
                  'treating as no live match (registry + PayPal-Request-Id still guard).')
            return found
        if r.status_code != 200:
            print(f'[WARN] Live plan list HTTP {r.status_code} (page {page}) — '
                  'treating as no live match (registry + PayPal-Request-Id still guard).')
            return found
        body = r.json()
        plans = body.get('plans', [])
        for p in plans:
            if p.get('status') == 'ACTIVE' and p.get('name'):
                found.setdefault(p['name'], p.get('id'))
        total_pages = body.get('total_pages')
        if not plans or (total_pages is not None and page >= total_pages):
            break
        page += 1
        if page > 50:  # hard safety stop
            break
    return found


def acquire_lock() -> bool:
    """Atomic claim-lock. Returns True if THIS process got the lock."""
    try:
        fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f'{os.getpid()} {datetime.now(timezone.utc).isoformat()}\n'.encode())
        os.close(fd)
        return True
    except OSError as e:
        if e.errno == errno.EEXIST:
            return False
        raise


def release_lock() -> None:
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# PayPal create / verify
# ═══════════════════════════════════════════════════════════════════════════
def get_access_token():
    r = requests.post(
        f'{BASE}/v1/oauth2/token',
        auth=(CLIENT_ID, SECRET),
        data={'grant_type': 'client_credentials'},
        headers={'Accept': 'application/json'}
    )
    if r.status_code != 200:
        print(f'[ERROR] Auth failed: HTTP {r.status_code}')
        print(r.text)
        return None
    token = r.json().get('access_token')
    print(f'[OK] Got access token: {token[:12]}... (redacted)')
    return token


def create_product(token, dry_run=False):
    if dry_run:
        print(f'[DRY-RUN] would create product: {PRODUCT["name"]} '
              f'(PayPal-Request-Id: {PRODUCT_REQUEST_ID})')
        return 'PROD-DRYRUN'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'PayPal-Request-Id': PRODUCT_REQUEST_ID,  # GUARD 3: retry-safe
    }
    r = requests.post(f'{BASE}/v1/catalogs/products', headers=headers, json=PRODUCT)
    if r.status_code in (200, 201):
        product = r.json()
        print(f'[OK] Created product: {product["id"]}')
        return product['id']
    else:
        print(f'[ERROR] Product creation failed: HTTP {r.status_code}')
        print(r.text[:800])
        return None


def create_plan(token, product_id, tier, dry_run=False):
    if dry_run:
        print(f'[DRY-RUN] would create plan "{tier["name"]}" ${tier["price"]}/mo '
              f'under product {product_id} (PayPal-Request-Id: {tier["request_id"]})')
        return f'P-DRYRUN-{tier["reg_key"]}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'PayPal-Request-Id': tier['request_id'],  # GUARD 3: retry-safe
    }
    payload = {
        'product_id': product_id,
        'name': tier['name'],
        'description': tier['description'],
        'status': 'ACTIVE',
        'billing_cycles': [
            {
                'frequency': {'interval_unit': 'MONTH', 'interval_count': 1},
                'tenure_type': 'REGULAR',
                'sequence': 1,
                'total_cycles': 0,  # Infinite
                'pricing_scheme': {
                    'fixed_price': {'value': tier['price'], 'currency_code': 'USD'}
                }
            }
        ],
        'payment_preferences': {
            'auto_bill_outstanding': True,
            'payment_failure_threshold': 3,
        },
    }
    r = requests.post(f'{BASE}/v1/billing/plans', headers=headers, json=payload)
    if r.status_code in (200, 201):
        plan = r.json()
        print(f'[OK] Created plan "{tier["name"]}": {plan["id"]} (${tier["price"]}/mo)')
        return plan['id']
    else:
        print(f'[ERROR] Plan creation failed for "{tier["name"]}": HTTP {r.status_code}')
        print(r.text[:800])
        return None


def verify_plan(token, plan_id, tier):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    r = requests.get(f'{BASE}/v1/billing/plans/{plan_id}', headers=headers)
    if r.status_code != 200:
        print(f'[ERROR] Read-back GET failed for {plan_id}: HTTP {r.status_code}')
        print(r.text[:800])
        return None
    plan = r.json()
    status = plan.get('status')
    cycles = plan.get('billing_cycles', [])
    cycle = cycles[0] if cycles else {}
    freq = cycle.get('frequency', {})
    fixed = cycle.get('pricing_scheme', {}).get('fixed_price', {})
    value = fixed.get('value')
    currency = fixed.get('currency_code')
    interval_unit = freq.get('interval_unit')
    interval_count = freq.get('interval_count')

    # NUMERIC compare — PayPal strips trailing zeros ('297.00' reads back '297.0').
    # The old script's string compare produced a false price_confirmed:false.
    try:
        price_ok = (value is not None
                    and float(value) == float(tier['price'])
                    and currency == 'USD')
    except (TypeError, ValueError):
        price_ok = False
    interval_ok = (interval_unit == 'MONTH' and interval_count == 1)
    status_ok = (status == 'ACTIVE')

    print('\n' + '-' * 50)
    print(f'READ-BACK VERIFICATION (GET) — "{tier["name"]}" {plan_id}:')
    print(f'  status         : {status}  (ACTIVE expected: {status_ok})')
    print(f'  fixed_price    : {value} {currency}  ({tier["price"]} USD numeric: {price_ok})')
    print(f'  interval       : {interval_unit}/{interval_count}  (MONTH/1: {interval_ok})')
    print('-' * 50)

    return {
        'status': status, 'price_value': value, 'currency': currency,
        'interval_unit': interval_unit, 'interval_count': interval_count,
        'price_confirmed': price_ok, 'interval_confirmed': interval_ok,
        'status_confirmed': status_ok,
        'all_ok': price_ok and interval_ok and status_ok,
    }


def save_results(product_id, tier_results):
    results = {
        'product_id': product_id,
        'product_name': PRODUCT['name'],
        'currency': 'USD',
        'environment': 'LIVE',
        'base_url': BASE,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'tiers': tier_results,
    }
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n[OK] Results saved to {RESULTS_PATH}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--human-confirmed', action='store_true',
                        dest='human_confirmed',
                        help='Explicit human confirmation for live money-create.')
    parser.add_argument('--owner', default=None,
                        help='Single-owner routing; must be "conductor".')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run',
                        help='Exercise all guard logic but make NO live create API calls.')
    args = parser.parse_args()

    print('=' * 60)
    print('Creating Purelicious Food Trucks PayPal Tiers [LIVE]')
    print('Awakened $297 / Operator $497 / Enterprise $1097 — USD/mo')
    print('=' * 60)

    # ── GUARD 2: autonomous-money-create gate (fail-closed, checked FIRST) ──
    if not check_create_gate(args):
        return False

    # ── GUARD 1a: registry idempotency (no API needed) ──
    pending = []
    for tier in TIERS:
        existing = registry_active_plan(tier['reg_key'])
        if existing:
            print(f'[SKIP] Plan already exists for {tier["reg_key"]}: {existing} '
                  f'— skipping create.')
        else:
            pending.append(tier)
    if not pending:
        print('[DONE] All 3 tiers already ACTIVE in registry. Nothing to create.')
        return True

    if not args.dry_run and (not CLIENT_ID or not SECRET):
        print('[ERROR] Missing PAYPAL_CLIENT_ID or PAYPAL_SECRET in .env')
        return False

    # ── GUARD 1b: atomic claim-lock (defeats concurrent race) ──
    if not acquire_lock():
        print(f'[SKIP] Create lock held for {GATE} ({LOCK_PATH.name}) — '
              f'another run is in progress. Skipping.')
        return True

    token = None
    try:
        live_by_name = {}
        product_id = registry_product_id()
        if not args.dry_run:
            token = get_access_token()
            if not token:
                return False

        # ── Product: reuse registry-recorded id, else create (idempotent) ──
        if product_id:
            print(f'[SKIP] Product already recorded for {PRODUCT_REG_KEY}: '
                  f'{product_id} — reusing.')
        else:
            product_id = create_product(token, dry_run=args.dry_run)
            if not product_id:
                return False
            if not args.dry_run:
                reg = load_registry()
                reg[PRODUCT_REG_KEY] = {
                    'product_id': product_id,
                    'name': PRODUCT['name'],
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'request_id': PRODUCT_REQUEST_ID,
                }
                write_registry(reg)

        # ── GUARD 1c: defense-in-depth live check (plans under THIS product) ──
        if not args.dry_run:
            live_by_name = live_active_plans_by_name(token, product_id)
            if live_by_name:
                print(f'[INFO] Live ACTIVE plans already under {product_id}: '
                      f'{live_by_name}')

        tier_results = {}
        all_ok = True
        for tier in pending:
            live_id = live_by_name.get(tier['name'])
            if live_id:
                print(f'[SKIP] Live PayPal already has ACTIVE plan '
                      f'"{tier["name"]}" under {product_id}: {live_id} — '
                      f'recording + skipping create.')
                reg = load_registry()
                reg[tier['reg_key']] = {
                    'plan_id': live_id, 'product_id': product_id,
                    'name': tier['name'], 'price': tier['price'],
                    'status': 'ACTIVE',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'note': 'Discovered live via list; no create performed.',
                }
                write_registry(reg)
                tier_results[tier['reg_key']] = {
                    'plan_id': live_id, 'name': tier['name'],
                    'price': tier['price'],
                    'verification': {'note': 'pre-existing live plan; recorded'},
                }
                continue

            plan_id = create_plan(token, product_id, tier, dry_run=args.dry_run)
            if not plan_id:
                # Fail-closed: stop, save partial results, report.
                if not args.dry_run and tier_results:
                    save_results(product_id, tier_results)
                return False

            if args.dry_run:
                tier_results[tier['reg_key']] = {
                    'plan_id': plan_id, 'name': tier['name'],
                    'price': tier['price'], 'verification': {'dry_run': True},
                }
                continue

            verification = verify_plan(token, plan_id, tier)
            if not verification:
                if tier_results:
                    save_results(product_id, tier_results)
                return False
            all_ok = all_ok and verification['all_ok']

            # Record into BOTH the registry (idempotency) and the results set.
            reg = load_registry()
            reg[tier['reg_key']] = {
                'plan_id': plan_id, 'product_id': product_id,
                'name': tier['name'], 'price': tier['price'],
                'status': verification['status'],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'request_id': tier['request_id'],
            }
            write_registry(reg)

            tier_results[tier['reg_key']] = {
                'plan_id': plan_id, 'name': tier['name'],
                'price': tier['price'], 'verification': verification,
            }

        if args.dry_run:
            print('[DRY-RUN] all guards passed; would now create + record. '
                  'No live API calls made.')
            return True

        save_results(product_id, tier_results)

        print('\n' + '=' * 60)
        print('RESULTS:')
        print('=' * 60)
        print(f'PRODUCT_ID: {product_id}')
        for key, res in tier_results.items():
            v = res.get('verification', {})
            print(f'{key}: plan_id={res["plan_id"]} price=${res["price"]} '
                  f'all_ok={v.get("all_ok", "n/a")}')
        return all_ok
    finally:
        release_lock()


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
