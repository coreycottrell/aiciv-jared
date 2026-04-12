#!/usr/bin/env python3
"""
Payment Webhook Backfill
========================
Replays historical payments from logs/purebrain_payments.jsonl through the
WebhookFirehose to a specified subscriber.

Usage:
    python3 tools/payment_webhook_backfill.py \
        --subscriber prodigy-growth-dashboard \
        --since 2026-03-01 \
        [--dry-run]

Rate limit: max 10 events/sec (100ms sleep between fires).
Each event is stamped with header `X-Backfill: true`.

Author: full-stack-developer (via ST#)
Date: 2026-04-08
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

from webhook_firehose import WebhookFirehose  # noqa: E402

PAYMENT_LOG = ROOT / 'logs' / 'purebrain_payments.jsonl'
CONFIG_PATH = ROOT / 'config' / 'payment_webhook_subscribers.json'
DELIVERY_LOG = ROOT / 'logs' / 'payment_webhook_delivery.jsonl'
DEAD_LETTER = ROOT / 'data' / 'failed_webhook_events.jsonl'

RATE_LIMIT_SLEEP = 0.1  # 10/sec


def parse_args():
    p = argparse.ArgumentParser(description='Backfill payment webhook events')
    p.add_argument('--subscriber', required=True, help='Subscriber name (must exist in config)')
    p.add_argument('--since', required=True, help='YYYY-MM-DD lower bound (inclusive)')
    p.add_argument('--dry-run', action='store_true', help='Do not send; print what would fire')
    p.add_argument('--limit', type=int, default=0, help='Max events (0 = unlimited)')
    return p.parse_args()


def normalize_event(record: dict) -> dict:
    """Convert a purebrain_payments.jsonl row into firehose event data."""
    try:
        amount = float(record.get('amount', 0) or 0)
    except (ValueError, TypeError):
        amount = 0.0
    return {
        'tier': record.get('tier', 'Unknown'),
        'amount': amount,
        'currency': 'USD',
        'customer_email': record.get('payerEmail', '') or '',
        'customer_name': record.get('payerName', '') or '',
        'order_id': record.get('orderId', '') or '',
        'subscription_id': record.get('subscriptionId', '') or '',
        'referral_code': record.get('referralCode', '') or '',
        'source_page': record.get('sourcePage', 'backfill') or 'backfill',
    }


def extract_ts(record: dict):
    ts = record.get('server_timestamp') or record.get('timestamp')
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        return None


def main():
    args = parse_args()

    try:
        since = datetime.strptime(args.since, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"ERROR: --since must be YYYY-MM-DD, got {args.since!r}", file=sys.stderr)
        sys.exit(2)

    if not PAYMENT_LOG.exists():
        print(f"ERROR: payment log not found: {PAYMENT_LOG}", file=sys.stderr)
        sys.exit(2)

    # Validate subscriber exists in config
    if not CONFIG_PATH.exists():
        print(f"ERROR: subscriber config not found: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(2)
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    names = [s.get('name') for s in cfg.get('subscribers', [])]
    if args.subscriber not in names:
        print(f"ERROR: subscriber {args.subscriber!r} not in config. Known: {names}", file=sys.stderr)
        sys.exit(2)

    firehose = WebhookFirehose(
        config_path=CONFIG_PATH,
        delivery_log_path=DELIVERY_LOG,
        dead_letter_path=DEAD_LETTER,
        telegram_config_path=ROOT / 'config' / 'telegram_config.json',
        blocking=True,  # backfill wants deterministic ordering / rate-limit
    )

    total_read = 0
    total_fired = 0
    total_filtered = 0

    with open(PAYMENT_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            total_read += 1

            ts = extract_ts(rec)
            if ts is None or ts < since:
                total_filtered += 1
                continue

            # Only payment verifications (skip other types)
            if rec.get('type') != 'payment_verification':
                total_filtered += 1
                continue

            data = normalize_event(rec)

            if args.dry_run:
                print(f"[DRY] would fire payment.completed -> {args.subscriber} :: "
                      f"order={data['order_id']} amount=${data['amount']:.2f}")
            else:
                firehose.fire_event(
                    'payment.completed',
                    data,
                    extra_headers={'X-Backfill': 'true'},
                )
                time.sleep(RATE_LIMIT_SLEEP)

            total_fired += 1
            if args.limit and total_fired >= args.limit:
                break

    print(f"\nBackfill summary:")
    print(f"  Subscriber: {args.subscriber}")
    print(f"  Since:      {args.since}")
    print(f"  Read:       {total_read}")
    print(f"  Filtered:   {total_filtered}")
    print(f"  Fired:      {total_fired}{' (dry-run)' if args.dry_run else ''}")


if __name__ == '__main__':
    main()
