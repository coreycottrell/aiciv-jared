#!/usr/bin/env python3
"""
Webhook Firehose
================
Reusable module for firing payment events to subscribed webhook endpoints.

Features:
  - Non-blocking dispatch (background threads)
  - HMAC-SHA256 signature per RFC convention
  - Retry with exponential backoff (configurable per subscriber)
  - Dead-letter queue on final failure
  - Telegram alert on dead-letter
  - Delivery log (JSONL) for observability / health endpoint

Dependencies: stdlib only (hmac, hashlib, urllib.request, json, uuid, threading, datetime)

Author: full-stack-developer (via ST#)
Date: 2026-04-08
"""

import hmac
import hashlib
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request as urlrequest
from urllib import error as urlerror


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _iso_now() -> str:
    """ISO-8601 UTC timestamp with millisecond precision."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def _unix_now() -> int:
    return int(time.time())


def _make_event_id() -> str:
    return f"evt_{uuid.uuid4()}"


def _atomic_append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, default=str) + "\n"
    # Open in append mode; on POSIX small appends are atomic enough for logs.
    with open(path, 'a') as f:
        f.write(line)
    # Best-effort permission lock for sensitive files.
    try:
        if path.stat().st_mode & 0o077:
            os.chmod(path, 0o600)
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# WebhookFirehose                                                              #
# --------------------------------------------------------------------------- #

class WebhookFirehose:
    """
    Fires events to configured subscribers with signed HMAC delivery.

    Usage:
        fh = WebhookFirehose(
            config_path="config/payment_webhook_subscribers.json",
            delivery_log_path="logs/payment_webhook_delivery.jsonl",
            dead_letter_path="data/failed_webhook_events.jsonl",
        )
        fh.fire_event("payment.completed", {"tier": "awakened", ...})
    """

    def __init__(
        self,
        config_path,
        delivery_log_path,
        dead_letter_path,
        telegram_config_path: Optional[str] = None,
        blocking: bool = False,
    ):
        self.config_path = Path(config_path)
        self.delivery_log_path = Path(delivery_log_path)
        self.dead_letter_path = Path(dead_letter_path)
        self.telegram_config_path = Path(telegram_config_path) if telegram_config_path else None
        self.blocking = blocking  # If True, don't spawn threads (for tests)

    # ---- config ----------------------------------------------------------- #

    def _load_subscribers(self) -> List[Dict[str, Any]]:
        if not self.config_path.exists():
            return []
        try:
            with open(self.config_path) as f:
                data = json.load(f)
            return data.get('subscribers', []) or []
        except Exception as e:
            self._log_delivery({
                'level': 'error',
                'msg': f'failed to load subscriber config: {e}',
                'ts': _iso_now(),
            })
            return []

    # ---- payload + signing ------------------------------------------------ #

    @staticmethod
    def _build_payload(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'event_type': event_type,
            'event_id': _make_event_id(),
            'timestamp': _iso_now(),
            'data': data,
        }

    @staticmethod
    def sign(body_bytes: bytes, secret: str) -> str:
        """Return 'sha256=<hex>' HMAC header value."""
        mac = hmac.new(secret.encode('utf-8'), body_bytes, hashlib.sha256)
        return f"sha256={mac.hexdigest()}"

    # ---- logging ---------------------------------------------------------- #

    def _log_delivery(self, record: Dict[str, Any]) -> None:
        _atomic_append_jsonl(self.delivery_log_path, record)

    def _log_dead_letter(self, record: Dict[str, Any]) -> None:
        _atomic_append_jsonl(self.dead_letter_path, record)

    # ---- telegram alert --------------------------------------------------- #

    def _alert_telegram(self, message: str) -> None:
        """Non-fatal. Uses stdlib urllib so no new deps."""
        try:
            cfg_path = self.telegram_config_path
            if cfg_path is None:
                cfg_path = Path(__file__).parent.parent / 'config' / 'telegram_config.json'
            if not cfg_path.exists():
                return
            with open(cfg_path) as f:
                tg = json.load(f)
            token = tg.get('bot_token', '')
            chat_id = tg.get('default_chat_id', '548906264')
            if not token:
                return
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            body = json.dumps({'chat_id': chat_id, 'text': message}).encode('utf-8')
            req = urlrequest.Request(
                url, data=body, method='POST',
                headers={'Content-Type': 'application/json'},
            )
            urlrequest.urlopen(req, timeout=10).read()
        except Exception:
            pass  # alerts are best-effort

    # ---- delivery core ---------------------------------------------------- #

    def _deliver(
        self,
        subscriber: Dict[str, Any],
        payload: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Deliver one payload to one subscriber with retries."""
        name = subscriber.get('name', 'unknown')
        url = subscriber.get('url', '')
        secret_env = subscriber.get('shared_secret_env', '')
        secret = os.getenv(secret_env, '') if secret_env else ''
        retry_policy = subscriber.get('retry_policy', {}) or {}
        max_retries = int(retry_policy.get('max_retries', 3))
        backoff = retry_policy.get('backoff_seconds', [5, 30, 120]) or [5, 30, 120]

        body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        signature = self.sign(body_bytes, secret) if secret else 'sha256=UNSIGNED'
        ts = str(_unix_now())

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Timestamp': ts,
            'User-Agent': 'AetherWebhookFirehose/1.0',
        }
        if extra_headers:
            headers.update(extra_headers)

        attempt = 0
        last_error: Optional[str] = None
        last_status: Optional[int] = None

        while attempt <= max_retries:
            attempt += 1
            start = time.time()
            try:
                req = urlrequest.Request(url, data=body_bytes, method='POST', headers=headers)
                with urlrequest.urlopen(req, timeout=10) as resp:
                    status = resp.getcode()
                    last_status = status
                    duration_ms = int((time.time() - start) * 1000)
                    if 200 <= status < 300:
                        self._log_delivery({
                            'ts': _iso_now(),
                            'subscriber': name,
                            'event_id': payload['event_id'],
                            'event_type': payload['event_type'],
                            'status': 'success',
                            'http_status': status,
                            'attempt': attempt,
                            'duration_ms': duration_ms,
                        })
                        return
                    # Non-2xx: treat 4xx as terminal (no retry); 5xx as retryable
                    last_error = f"http {status}"
                    if 400 <= status < 500:
                        self._log_delivery({
                            'ts': _iso_now(),
                            'subscriber': name,
                            'event_id': payload['event_id'],
                            'event_type': payload['event_type'],
                            'status': 'failure',
                            'http_status': status,
                            'attempt': attempt,
                            'error': last_error,
                            'terminal': True,
                        })
                        break  # do not retry 4xx
            except urlerror.HTTPError as e:
                last_status = e.code
                last_error = f"http {e.code}"
                self._log_delivery({
                    'ts': _iso_now(),
                    'subscriber': name,
                    'event_id': payload['event_id'],
                    'event_type': payload['event_type'],
                    'status': 'failure',
                    'http_status': e.code,
                    'attempt': attempt,
                    'error': last_error,
                })
                if 400 <= e.code < 500:
                    break  # terminal
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                self._log_delivery({
                    'ts': _iso_now(),
                    'subscriber': name,
                    'event_id': payload['event_id'],
                    'event_type': payload['event_type'],
                    'status': 'failure',
                    'attempt': attempt,
                    'error': last_error,
                })

            # Sleep before next attempt (if any retries remain)
            if attempt <= max_retries:
                idx = min(attempt - 1, len(backoff) - 1)
                sleep_s = backoff[idx]
                time.sleep(sleep_s)

        # All retries exhausted — dead letter + alert
        self._log_dead_letter({
            'ts': _iso_now(),
            'subscriber': name,
            'url': url,
            'event_id': payload['event_id'],
            'event_type': payload['event_type'],
            'payload': payload,
            'last_error': last_error,
            'last_status': last_status,
            'attempts': attempt,
        })
        self._alert_telegram(
            f"[Webhook DEAD LETTER] subscriber={name} "
            f"event={payload['event_type']} id={payload['event_id']} "
            f"attempts={attempt} last_error={last_error}"
        )

    # ---- public API ------------------------------------------------------- #

    def fire_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Fire an event to all enabled subscribers that match the event filter.

        Returns the constructed payload (synchronous; delivery is async unless
        blocking=True was set on init).
        """
        payload = self._build_payload(event_type, data)
        subscribers = self._load_subscribers()

        for sub in subscribers:
            if not sub.get('enabled', False):
                self._log_delivery({
                    'ts': _iso_now(),
                    'subscriber': sub.get('name', 'unknown'),
                    'event_id': payload['event_id'],
                    'event_type': event_type,
                    'status': 'skipped',
                    'reason': 'subscriber disabled',
                })
                continue

            allowed = sub.get('events', []) or []
            if allowed and event_type not in allowed:
                self._log_delivery({
                    'ts': _iso_now(),
                    'subscriber': sub.get('name', 'unknown'),
                    'event_id': payload['event_id'],
                    'event_type': event_type,
                    'status': 'skipped',
                    'reason': 'event not in filter',
                })
                continue

            if self.blocking:
                self._deliver(sub, payload, extra_headers=extra_headers)
            else:
                t = threading.Thread(
                    target=self._deliver,
                    args=(sub, payload),
                    kwargs={'extra_headers': extra_headers},
                    daemon=True,
                    name=f"firehose-{sub.get('name', 'x')}-{payload['event_id'][:12]}",
                )
                t.start()

        return payload

    # ---- stats ------------------------------------------------------------ #

    def get_stats(self, subscriber_name: str) -> Dict[str, Any]:
        """Compute delivery stats from the JSONL log for one subscriber."""
        total_sent = 0
        total_failed = 0
        last_delivery_ts: Optional[str] = None
        last_failure_ts: Optional[str] = None
        retry_queue_depth = 0  # dead-letter count

        if self.delivery_log_path.exists():
            try:
                with open(self.delivery_log_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        if rec.get('subscriber') != subscriber_name:
                            continue
                        if rec.get('status') == 'success':
                            total_sent += 1
                            last_delivery_ts = rec.get('ts') or last_delivery_ts
                        elif rec.get('status') == 'failure':
                            total_failed += 1
                            last_failure_ts = rec.get('ts') or last_failure_ts
            except Exception:
                pass

        if self.dead_letter_path.exists():
            try:
                with open(self.dead_letter_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        if rec.get('subscriber') == subscriber_name:
                            retry_queue_depth += 1
            except Exception:
                pass

        attempts = total_sent + total_failed
        success_rate = (total_sent / attempts) if attempts > 0 else 0.0

        return {
            'success_rate': round(success_rate, 4),
            'last_delivery_ts': last_delivery_ts,
            'last_failure_ts': last_failure_ts,
            'retry_queue_depth': retry_queue_depth,
            'total_sent': total_sent,
            'total_failed': total_failed,
        }


# --------------------------------------------------------------------------- #
# Singleton accessor (convenience for paypal_auto_split integration)           #
# --------------------------------------------------------------------------- #

_default_instance: Optional[WebhookFirehose] = None


def get_default_firehose() -> WebhookFirehose:
    global _default_instance
    if _default_instance is None:
        root = Path(__file__).parent.parent
        _default_instance = WebhookFirehose(
            config_path=root / 'config' / 'payment_webhook_subscribers.json',
            delivery_log_path=root / 'logs' / 'payment_webhook_delivery.jsonl',
            dead_letter_path=root / 'data' / 'failed_webhook_events.jsonl',
            telegram_config_path=root / 'config' / 'telegram_config.json',
        )
    return _default_instance


if __name__ == '__main__':
    # Smoke test: print a signed payload without sending.
    fh = WebhookFirehose(
        config_path='/tmp/no-such-config.json',
        delivery_log_path='/tmp/firehose-test.jsonl',
        dead_letter_path='/tmp/firehose-dead.jsonl',
        blocking=True,
    )
    payload = fh._build_payload('payment.completed', {'tier': 'awakened', 'amount': 149.00})
    body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    print('PAYLOAD:', json.dumps(payload, indent=2))
    print('SIGNATURE:', fh.sign(body, 'test-secret'))
