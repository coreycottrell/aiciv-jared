#!/usr/bin/env python3
"""PRICING CORRECTION for Purelicious Food Trucks PayPal billing plans.

Jared's pricing sheet is canon (confirmed via Chy 2026-06-11). The 3 tiers
minted ~30 min earlier by tools/create_purelicious_foodtruck_tiers.py were
from a SUPERSEDED request. All affected plans are brand new, ZERO subscribers,
never wired to any page. Deactivation is the sanctioned "void".

CORRECTED CANON (USD, monthly, infinite cycles), product PROD-9E164079YF369242V:
  Operator   — $250.00/mo  (1 truck, AI included)        [MINT NEW]
  Fleet      — $497.00/mo  (up to 3 trucks)              [MINT NEW]
  Enterprise — $1097.00/mo (up to 10 trucks)             [KEEP P-30318719KE1149043NIVSVLI]

VOID (deactivate, guarded):
  P-0D1534491U821574CNIVSVKY  "Awakened"  $297/mo  — tier does not exist in canon
  P-6PE54881235657116NIVSVLA  "Operator"  $497/mo  — wrong name for this price

DO NOT TOUCH: old heat-map plans P-20N28177822286433NITSQVI /
P-49T5523746060730VNITSQCA and product PROD-30N67904YR8674902.

═══════════════════════════════════════════════════════════════════════════
MONEY-SAFETY GUARDS (inherited from tools/create_purelicious_foodtruck_tiers.py)
═══════════════════════════════════════════════════════════════════════════
GUARD 0 — DEACTIVATE-TARGET ASSERTION: before any deactivate, GET the plan
  and assert exact plan_id ∈ allow-list AND product_id, name, numeric price
  all match expectations. ANY mismatch → STOP the entire run (fail-closed),
  report verbatim, exit 1. Refuses to deactivate anything else.

GUARD 1 — IDEMPOTENCY / CLAIM-LOCK: registry-aware (the correction KNOWS the
  current OPERATOR registry entry points at the wrong $497 plan and repoints
  it). Mint skipped only if an ACTIVE live plan with same name + numeric
  price already exists under THIS product. Atomic O_EXCL claim-lock
  (config/.paypal_create_lock_PURELICIOUS_FT_CORRECTION) for the whole run.

GUARD 2 — AUTONOMOUS-MONEY-CREATE GATE: fail-closed; refuses live mutation
  without --human-confirmed --owner conductor (or env equivalents).

GUARD 3 — PAYPAL-SIDE IDEMPOTENCY: fixed PayPal-Request-Id on every create.
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
GATE = 'PURELICIOUS_FT_CORRECTION'
REGISTRY_PATH = BASE_DIR / 'config' / 'paypal_plan_registry.json'
LOCK_PATH = BASE_DIR / 'config' / f'.paypal_create_lock_{GATE}'
RESULTS_PATH = BASE_DIR / 'config' / 'paypal_plans_purelicious_foodtrucks.json'

PRODUCT_ID = 'PROD-9E164079YF369242V'
PRODUCT_NAME = 'Purelicious Food Trucks'
PRODUCT_REG_KEY = 'PURELICIOUS_FT_PRODUCT'

# Plans to VOID (deactivate). Guard asserts ALL fields before acting.
VOID_TARGETS = [
    {
        'plan_id': 'P-0D1534491U821574CNIVSVKY',
        'expected_name': 'Awakened',
        'expected_price': '297.00',
        'reg_key': 'PURELICIOUS_FT_AWAKENED',
        'reason': 'Tier does not exist in corrected canon (superseded request)',
    },
    {
        'plan_id': 'P-6PE54881235657116NIVSVLA',
        'expected_name': 'Operator',
        'expected_price': '497.00',
        'reg_key': 'PURELICIOUS_FT_OPERATOR',
        'reason': 'Wrong name for $497 price point (corrected canon: $497 tier is "Fleet")',
    },
]

# Plan to KEEP (Enterprise) — description PATCH is best-effort only.
ENTERPRISE_PLAN_ID = 'P-30318719KE1149043NIVSVLI'
ENTERPRISE_NEW_DESC = 'Purelicious Enterprise — up to 10 trucks'
ENTERPRISE_REG_KEY = 'PURELICIOUS_FT_ENTERPRISE'
ENTERPRISE_PRICE = '1097.00'

# Plans to MINT under PRODUCT_ID.
NEW_TIERS = [
    {
        'reg_key': 'PURELICIOUS_FT_OPERATOR',
        'name': 'Operator',
        'description': 'Purelicious Operator — 1 truck, AI included',
        'price': '250.00',
        'request_id': 'purelicious-ft-operator-250usd-20260611',
    },
    {
        'reg_key': 'PURELICIOUS_FT_FLEET',
        'name': 'Fleet',
        'description': 'Purelicious Fleet — up to 3 trucks',
        'price': '497.00',
        'request_id': 'purelicious-ft-fleet-497usd-20260611',
    },
]

# Absolute do-not-touch list (old heat-map artifacts).
FORBIDDEN_PLAN_IDS = {'P-20N28177822286433NITSQVI', 'P-49T5523746060730VNITSQCA'}
FORBIDDEN_PRODUCT_IDS = {'PROD-30N67904YR8674902'}


# ═══════════════════════════════════════════════════════════════════════════
# GUARD 2 — Autonomous-money-create gate (fail-closed)
# ═══════════════════════════════════════════════════════════════════════════
def autonomous_context() -> bool:
    if os.getenv('BOOP_TASK_ID'):
        return True
    for k, v in os.environ.items():
        if 'BOOP' in k.upper() or (isinstance(v, str) and 'BOOP [' in v):
            return True
    return False


def human_confirmed(args) -> bool:
    flag = bool(getattr(args, 'human_confirmed', False))
    owner = getattr(args, 'owner', None) or os.getenv('PAYPAL_CREATE_OWNER', '')
    env_conf = os.getenv('PAYPAL_CREATE_HUMAN_CONFIRMED', '').lower() == 'yes'
    confirmed = flag or env_conf
    return bool(confirmed and owner == 'conductor')


def check_create_gate(args) -> bool:
    auto = autonomous_context()
    confirmed = human_confirmed(args)
    if confirmed:
        return True
    if auto:
        print('[BLOCKED] Live PayPal plan mutation requires human confirmation. '
              'Detected autonomous/BOOP context. Re-run with '
              '--human-confirmed --owner conductor (or set '
              'PAYPAL_CREATE_HUMAN_CONFIRMED=yes PAYPAL_CREATE_OWNER=conductor). '
              'Refusing to mutate from autonomous context.')
        return False
    print('[BLOCKED] Live PayPal plan mutation requires human confirmation. '
          'Re-run with --human-confirmed --owner conductor '
          '(or set PAYPAL_CREATE_HUMAN_CONFIRMED=yes PAYPAL_CREATE_OWNER=conductor).')
    return False


# ═══════════════════════════════════════════════════════════════════════════
# Registry / claim-lock helpers
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


def acquire_lock() -> bool:
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
# PayPal helpers
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


def get_plan(token, plan_id):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    r = requests.get(f'{BASE}/v1/billing/plans/{plan_id}', headers=headers, timeout=30)
    if r.status_code != 200:
        print(f'[ERROR] GET plan {plan_id} failed: HTTP {r.status_code}')
        print(r.text[:800])
        return None
    return r.json()


def plan_price(plan) -> tuple:
    """Return (value, currency, interval_unit, interval_count) from first cycle."""
    cycles = plan.get('billing_cycles', [])
    cycle = cycles[0] if cycles else {}
    freq = cycle.get('frequency', {})
    fixed = cycle.get('pricing_scheme', {}).get('fixed_price', {})
    return (fixed.get('value'), fixed.get('currency_code'),
            freq.get('interval_unit'), freq.get('interval_count'))


def prices_equal(a, b) -> bool:
    try:
        return float(a) == float(b)  # PayPal strips trailing zeros
    except (TypeError, ValueError):
        return False


# ═══════════════════════════════════════════════════════════════════════════
# GUARD 0 — Deactivate-target assertion + deactivate
# ═══════════════════════════════════════════════════════════════════════════
def assert_void_target(token, target):
    """GET the plan and assert identity. Returns ('ok', plan) | ('already_inactive',
    plan) | ('FAIL', message). ANY mismatch is a hard failure for the whole run."""
    pid = target['plan_id']
    if pid in FORBIDDEN_PLAN_IDS:
        return ('FAIL', f'plan {pid} is on the FORBIDDEN do-not-touch list')
    plan = get_plan(token, pid)
    if plan is None:
        return ('FAIL', f'could not GET plan {pid} for pre-deactivate assertion')

    got_product = plan.get('product_id')
    got_name = plan.get('name')
    got_status = plan.get('status')
    value, currency, unit, count = plan_price(plan)

    problems = []
    if got_product != PRODUCT_ID:
        problems.append(f'product_id mismatch: got {got_product!r}, expected {PRODUCT_ID!r}')
    if got_product in FORBIDDEN_PRODUCT_IDS:
        problems.append(f'product_id {got_product!r} is on the FORBIDDEN do-not-touch list')
    if got_name != target['expected_name']:
        problems.append(f'name mismatch: got {got_name!r}, expected {target["expected_name"]!r}')
    if not prices_equal(value, target['expected_price']):
        problems.append(f'price mismatch: got {value!r}, expected {target["expected_price"]!r}')
    if currency != 'USD':
        problems.append(f'currency mismatch: got {currency!r}, expected USD')

    if problems:
        return ('FAIL',
                f'PRE-DEACTIVATE ASSERTION FAILED for {pid}: ' + '; '.join(problems)
                + f' | full identity readback: name={got_name!r} status={got_status!r} '
                  f'product={got_product!r} price={value!r} {currency!r} {unit}/{count}')

    print(f'[GUARD-OK] {pid}: name={got_name!r} price={value} {currency} '
          f'product={got_product} status={got_status} — matches void target.')
    if got_status == 'INACTIVE':
        return ('already_inactive', plan)
    return ('ok', plan)


def deactivate_plan(token, plan_id, dry_run=False):
    if dry_run:
        print(f'[DRY-RUN] would POST /v1/billing/plans/{plan_id}/deactivate')
        return True
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json',
               'Content-Type': 'application/json'}
    r = requests.post(f'{BASE}/v1/billing/plans/{plan_id}/deactivate',
                      headers=headers, timeout=30)
    if r.status_code == 204:
        print(f'[OK] Deactivated plan {plan_id} (HTTP 204)')
        return True
    print(f'[ERROR] Deactivate failed for {plan_id}: HTTP {r.status_code}')
    print(r.text[:800])
    return False


# ═══════════════════════════════════════════════════════════════════════════
# Mint + verify (inherited patterns)
# ═══════════════════════════════════════════════════════════════════════════
def live_active_name_price_match(token, tier) -> str:
    """Defense-in-depth: list ALL plans under PRODUCT_ID; if an ACTIVE plan with
    same name AND same numeric price exists, return its id (skip mint)."""
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    page = 1
    candidates = []
    while True:
        try:
            r = requests.get(
                f'{BASE}/v1/billing/plans?product_id={PRODUCT_ID}'
                f'&page_size=20&page={page}&total_required=true',
                headers=headers, timeout=30)
        except Exception as e:
            print(f'[WARN] Live plan list failed (page {page}): {e} — '
                  'treating as no live match (PayPal-Request-Id still guards).')
            return ''
        if r.status_code != 200:
            print(f'[WARN] Live plan list HTTP {r.status_code} (page {page}) — '
                  'treating as no live match (PayPal-Request-Id still guards).')
            return ''
        body = r.json()
        plans = body.get('plans', [])
        for p in plans:
            if p.get('status') == 'ACTIVE' and p.get('name') == tier['name']:
                candidates.append(p.get('id'))
        total_pages = body.get('total_pages')
        if not plans or (total_pages is not None and page >= total_pages):
            break
        page += 1
        if page > 50:
            break
    # Name match alone is not enough (old "Operator" was $497) — confirm price via GET.
    for pid in candidates:
        plan = get_plan(token, pid)
        if not plan:
            continue
        value, currency, _, _ = plan_price(plan)
        if currency == 'USD' and prices_equal(value, tier['price']) \
                and plan.get('status') == 'ACTIVE':
            return pid
    return ''


def create_plan(token, tier, dry_run=False):
    if dry_run:
        print(f'[DRY-RUN] would create plan "{tier["name"]}" ${tier["price"]}/mo '
              f'under product {PRODUCT_ID} (PayPal-Request-Id: {tier["request_id"]})')
        return f'P-DRYRUN-{tier["reg_key"]}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'PayPal-Request-Id': tier['request_id'],  # GUARD 3: retry-safe
    }
    payload = {
        'product_id': PRODUCT_ID,
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
    print(f'[ERROR] Plan creation failed for "{tier["name"]}": HTTP {r.status_code}')
    print(r.text[:800])
    return None


def verify_plan(token, plan_id, name, price, expect_status='ACTIVE'):
    plan = get_plan(token, plan_id)
    if plan is None:
        return None
    status = plan.get('status')
    value, currency, unit, count = plan_price(plan)
    price_ok = prices_equal(value, price) and currency == 'USD'
    interval_ok = (unit == 'MONTH' and count == 1)
    status_ok = (status == expect_status)
    print('\n' + '-' * 50)
    print(f'READ-BACK VERIFICATION (GET) — "{name}" {plan_id}:')
    print(f'  status         : {status}  ({expect_status} expected: {status_ok})')
    print(f'  fixed_price    : {value} {currency}  ({price} USD numeric: {price_ok})')
    print(f'  interval       : {unit}/{count}  (MONTH/1: {interval_ok})')
    print('-' * 50)
    return {
        'status': status, 'price_value': value, 'currency': currency,
        'interval_unit': unit, 'interval_count': count,
        'price_confirmed': price_ok, 'interval_confirmed': interval_ok,
        'status_confirmed': status_ok,
        'all_ok': price_ok and interval_ok and status_ok,
    }


def patch_enterprise_description(token, dry_run=False) -> dict:
    """Best-effort PATCH of Enterprise description. Failure is reported, NOT fatal."""
    if dry_run:
        print(f'[DRY-RUN] would PATCH {ENTERPRISE_PLAN_ID} description -> '
              f'{ENTERPRISE_NEW_DESC!r}')
        return {'attempted': True, 'dry_run': True}
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json',
               'Content-Type': 'application/json'}
    body = [{'op': 'replace', 'path': '/description', 'value': ENTERPRISE_NEW_DESC}]
    try:
        r = requests.patch(f'{BASE}/v1/billing/plans/{ENTERPRISE_PLAN_ID}',
                           headers=headers, json=body, timeout=30)
    except Exception as e:
        print(f'[WARN] Enterprise description PATCH errored: {e} — moving on (non-fatal).')
        return {'attempted': True, 'success': False, 'error': str(e)}
    if r.status_code == 204:
        print(f'[OK] Enterprise description PATCHed (HTTP 204): {ENTERPRISE_NEW_DESC!r}')
        return {'attempted': True, 'success': True}
    print(f'[WARN] Enterprise description PATCH failed: HTTP {r.status_code} — '
          f'moving on (non-fatal). Body: {r.text[:400]}')
    return {'attempted': True, 'success': False,
            'http_status': r.status_code, 'body': r.text[:400]}


def save_results(operator_res, fleet_res, enterprise_res, voided, patch_res):
    results = {
        'product_id': PRODUCT_ID,
        'product_name': PRODUCT_NAME,
        'currency': 'USD',
        'environment': 'LIVE',
        'base_url': BASE,
        'corrected_at': datetime.now(timezone.utc).isoformat(),
        'correction': 'Pricing correction 2026-06-11 — Jared sheet canon via Chy; '
                      'conductor single owner',
        'tiers': {
            'PURELICIOUS_FT_OPERATOR': operator_res,
            'PURELICIOUS_FT_FLEET': fleet_res,
            'PURELICIOUS_FT_ENTERPRISE': enterprise_res,
        },
        'enterprise_description_patch': patch_res,
        'voided': voided,
    }
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n[OK] Results saved to {RESULTS_PATH}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--human-confirmed', action='store_true', dest='human_confirmed',
                        help='Explicit human confirmation for live money mutation.')
    parser.add_argument('--owner', default=None,
                        help='Single-owner routing; must be "conductor".')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run',
                        help='Run guards + read-only GET assertions; NO mutating calls.')
    args = parser.parse_args()

    print('=' * 60)
    print('PRICING CORRECTION: Purelicious Food Trucks PayPal Tiers [LIVE]')
    print('Void Awakened $297 + Operator $497; mint Operator $250 + Fleet $497;')
    print('keep Enterprise $1097.')
    print('=' * 60)

    # ── GUARD 2: fail-closed human gate, checked FIRST ──
    if not check_create_gate(args):
        return False

    if not CLIENT_ID or not SECRET:
        print('[ERROR] Missing PAYPAL_CLIENT_ID or PAYPAL_SECRET in .env')
        return False

    # ── GUARD 1: atomic claim-lock for the whole correction run ──
    if not acquire_lock():
        print(f'[SKIP] Correction lock held for {GATE} ({LOCK_PATH.name}) — '
              f'another run is in progress. Skipping.')
        return True

    try:
        token = get_access_token()
        if not token:
            return False

        # ════ STEP 1: GUARDED DEACTIVATION of the two wrong plans ════
        voided = []
        for target in VOID_TARGETS:
            verdict, payload = assert_void_target(token, target)
            if verdict == 'FAIL':
                print(f'\n[ABORT] {payload}')
                print('[ABORT] STOPPING ENTIRE RUN — no deactivations, mints, or '
                      'registry writes past a failed assertion.')
                return False
            if verdict == 'already_inactive':
                print(f'[SKIP] {target["plan_id"]} already INACTIVE — idempotent.')
            else:
                if not deactivate_plan(token, target['plan_id'], dry_run=args.dry_run):
                    print('[ABORT] Deactivation failed — stopping before any mint.')
                    return False
            # Post-deactivate readback (skip mutation-dependent check in dry-run)
            if args.dry_run:
                post_status = 'DRY-RUN (no mutation)'
            else:
                post = get_plan(token, target['plan_id'])
                post_status = post.get('status') if post else 'READBACK-FAILED'
                if post_status != 'INACTIVE':
                    print(f'[ABORT] Post-deactivate readback for {target["plan_id"]} '
                          f'is {post_status!r}, expected INACTIVE. Stopping.')
                    return False
                print(f'[OK] Post-deactivate readback {target["plan_id"]}: INACTIVE')
            voided.append({
                'plan_id': target['plan_id'],
                'name': target['expected_name'],
                'price': target['expected_price'],
                'post_deactivate_status': post_status,
                'reason': target['reason'],
            })

        # ════ STEP 2: MINT Operator $250 + Fleet $497 ════
        new_results = {}
        for tier in NEW_TIERS:
            # Defense-in-depth: ACTIVE live plan, same name AND same numeric price?
            existing = live_active_name_price_match(token, tier)
            if existing:
                print(f'[SKIP] Live ACTIVE plan "{tier["name"]}" ${tier["price"]} '
                      f'already exists under {PRODUCT_ID}: {existing} — '
                      f'recording, not re-minting.')
                plan_id = existing
            else:
                plan_id = create_plan(token, tier, dry_run=args.dry_run)
                if not plan_id:
                    print('[ABORT] Mint failed — stopping. Voided plans remain '
                          'INACTIVE (correct); registry NOT yet rewritten.')
                    return False
            if args.dry_run:
                new_results[tier['reg_key']] = {
                    'plan_id': plan_id, 'name': tier['name'],
                    'price': tier['price'], 'verification': {'dry_run': True}}
                continue
            verification = verify_plan(token, plan_id, tier['name'], tier['price'])
            if not verification or not verification['all_ok']:
                print(f'[ABORT] Readback verification failed for new plan '
                      f'{plan_id} ("{tier["name"]}"). Stopping before registry write.')
                return False
            new_results[tier['reg_key']] = {
                'plan_id': plan_id, 'name': tier['name'],
                'price': tier['price'], 'description': tier['description'],
                'verification': verification,
            }

        # ════ STEP 3: Enterprise — keep; best-effort description PATCH ════
        patch_res = patch_enterprise_description(token, dry_run=args.dry_run)
        enterprise_ver = None
        if not args.dry_run:
            enterprise_ver = verify_plan(token, ENTERPRISE_PLAN_ID, 'Enterprise',
                                         ENTERPRISE_PRICE)
            if not enterprise_ver or not enterprise_ver['all_ok']:
                print('[WARN] Enterprise readback not all_ok — reporting, NOT voiding.')

        if args.dry_run:
            print('\n[DRY-RUN] All guards + GET assertions passed. '
                  'No mutating API calls made; registry untouched.')
            return True

        # ════ STEP 4: Registry update ════
        now = datetime.now(timezone.utc).isoformat()
        reg = load_registry()
        # Awakened → VOIDED (keep plan_id for audit)
        awk = reg.get('PURELICIOUS_FT_AWAKENED', {})
        awk.update({'status': 'VOIDED-PRICING-CORRECTION', 'voided_at': now,
                    'reason': VOID_TARGETS[0]['reason']})
        reg['PURELICIOUS_FT_AWAKENED'] = awk
        # Audit entry for the voided $497 Operator (before repointing the key)
        old_op = reg.get('PURELICIOUS_FT_OPERATOR', {})
        if old_op.get('plan_id') == 'P-6PE54881235657116NIVSVLA':
            reg['PURELICIOUS_FT_OPERATOR_497_VOIDED'] = {
                **old_op, 'status': 'VOIDED-PRICING-CORRECTION',
                'voided_at': now, 'reason': VOID_TARGETS[1]['reason']}
        # Repoint OPERATOR to the new $250 plan
        op_new = new_results['PURELICIOUS_FT_OPERATOR']
        reg['PURELICIOUS_FT_OPERATOR'] = {
            'plan_id': op_new['plan_id'], 'product_id': PRODUCT_ID,
            'name': 'Operator', 'price': '250.00',
            'status': op_new['verification']['status'],
            'created_at': now,
            'request_id': NEW_TIERS[0]['request_id'],
            'note': 'Pricing correction 2026-06-11; replaces voided $497 '
                    'P-6PE54881235657116NIVSVLA',
        }
        # Add FLEET
        fl_new = new_results['PURELICIOUS_FT_FLEET']
        reg['PURELICIOUS_FT_FLEET'] = {
            'plan_id': fl_new['plan_id'], 'product_id': PRODUCT_ID,
            'name': 'Fleet', 'price': '497.00',
            'status': fl_new['verification']['status'],
            'created_at': now,
            'request_id': NEW_TIERS[1]['request_id'],
        }
        # ENTERPRISE left as-is (untouched).
        write_registry(reg)
        print(f'[OK] Registry updated at {REGISTRY_PATH}')

        # ════ STEP 5: Rewrite results JSON to corrected final state ════
        enterprise_res = {
            'plan_id': ENTERPRISE_PLAN_ID, 'name': 'Enterprise',
            'price': ENTERPRISE_PRICE, 'description': ENTERPRISE_NEW_DESC,
            'verification': enterprise_ver,
        }
        save_results(op_new, fl_new, enterprise_res, voided, patch_res)

        print('\n' + '=' * 60)
        print('CORRECTION RESULTS:')
        print('=' * 60)
        print(f'PRODUCT_ID: {PRODUCT_ID}')
        for v in voided:
            print(f'VOIDED: {v["plan_id"]} ("{v["name"]}" ${v["price"]}) -> '
                  f'{v["post_deactivate_status"]}')
        for key, res in new_results.items():
            print(f'{key}: plan_id={res["plan_id"]} price=${res["price"]} '
                  f'all_ok={res["verification"].get("all_ok")}')
        print(f'PURELICIOUS_FT_ENTERPRISE: plan_id={ENTERPRISE_PLAN_ID} '
              f'price=${ENTERPRISE_PRICE} '
              f'all_ok={enterprise_ver.get("all_ok") if enterprise_ver else "n/a"} '
              f'(kept; desc patch success={patch_res.get("success")})')
        all_ok = (all(r['verification'].get('all_ok') for r in new_results.values())
                  and bool(enterprise_ver and enterprise_ver.get('all_ok')))
        return all_ok
    finally:
        release_lock()


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
