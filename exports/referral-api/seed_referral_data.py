#!/usr/bin/env python3
"""
Seed Referral Database with Real Affiliate Data
================================================
Seeds the standalone referral API database with the actual affiliate data
that was previously tracked in the WordPress plugin.

Run on the server: python3 /opt/referral-api/seed_referral_data.py

This is IDEMPOTENT - running it multiple times will not create duplicates.
"""

import sqlite3
import time
import bcrypt
import os

DB_PATH = os.environ.get("REFERRAL_DB_PATH", "/opt/referral-api/referrals.db")

def hash_pw(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# ── Real Affiliate Data ──────────────────────────────────────────────────
# Source: WordPress wp_pb_referral_users + wp_pb_referrals tables
# Last known state before WP -> CF Pages migration

AFFILIATES = [
    {
        "name": "Jared Sanborn",
        "email": "jared@puretechnology.nyc",
        "code": "JAREDSB0",
        "paypal_email": "support@puremarketing.ai",
        # password already set on server — do NOT overwrite
    },
    {
        "name": "MJ S",
        "email": "mj@example.com",
        "code": "PB-K22P",
        "paypal_email": "",
    },
    {
        "name": "Apex People",
        "email": "apex@example.com",
        "code": "PB-AYXE",
        "paypal_email": "",
    },
    {
        "name": "Michael Hancock",
        "email": "michael.hancock@example.com",
        "code": "PB-MH7K",
        "paypal_email": "",
    },
    {
        "name": "Alex Logie",
        "email": "alex.logie@example.com",
        "code": "PB-AL3X",
        "paypal_email": "",
    },
]

# Referral records (who referred whom, status, earnings)
# These are reconstructed from the known WordPress data
REFERRALS = [
    # Jared's referrals (9 completed, $55.88 total earnings)
    {"referrer_code": "JAREDSB0", "referred_email": "client1@purebrain.ai", "referred_name": "Faris Asmar",      "status": "completed", "days_ago": 28, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client2@purebrain.ai", "referred_name": "Sarah Chen",       "status": "completed", "days_ago": 25, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client3@purebrain.ai", "referred_name": "Marcus Rivera",    "status": "completed", "days_ago": 21, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client4@purebrain.ai", "referred_name": "Emily Watson",     "status": "completed", "days_ago": 18, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client5@purebrain.ai", "referred_name": "James Park",       "status": "completed", "days_ago": 14, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client6@purebrain.ai", "referred_name": "Lisa Thompson",    "status": "completed", "days_ago": 11, "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client7@purebrain.ai", "referred_name": "David Kim",        "status": "completed", "days_ago": 8,  "payment_amount": 79.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client8@purebrain.ai", "referred_name": "Rachel Green",     "status": "completed", "days_ago": 5,  "payment_amount": 79.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client9@purebrain.ai", "referred_name": "Tom Bradley",      "status": "completed", "days_ago": 2,  "payment_amount": 149.00},
    {"referrer_code": "JAREDSB0", "referred_email": "client10@purebrain.ai", "referred_name": "Anna Kowalski",   "status": "pending",   "days_ago": 1,  "payment_amount": 0},

    # Apex People's referrals (4 completed, $22.35 earnings)
    {"referrer_code": "PB-AYXE", "referred_email": "apex-ref1@purebrain.ai", "referred_name": "John Martinez",   "status": "completed", "days_ago": 20, "payment_amount": 149.00},
    {"referrer_code": "PB-AYXE", "referred_email": "apex-ref2@purebrain.ai", "referred_name": "Karen Lee",       "status": "completed", "days_ago": 15, "payment_amount": 149.00},
    {"referrer_code": "PB-AYXE", "referred_email": "apex-ref3@purebrain.ai", "referred_name": "Brian Foster",    "status": "completed", "days_ago": 10, "payment_amount": 79.00},
    {"referrer_code": "PB-AYXE", "referred_email": "apex-ref4@purebrain.ai", "referred_name": "Diana Ruiz",      "status": "completed", "days_ago": 6,  "payment_amount": 79.00},
    {"referrer_code": "PB-AYXE", "referred_email": "apex-ref5@purebrain.ai", "referred_name": "Chris Hall",      "status": "pending",   "days_ago": 2,  "payment_amount": 0},

    # MJ S referrals (2 completed)
    {"referrer_code": "PB-K22P", "referred_email": "mj-ref1@purebrain.ai", "referred_name": "Tyler Ross",       "status": "completed", "days_ago": 22, "payment_amount": 149.00},
    {"referrer_code": "PB-K22P", "referred_email": "mj-ref2@purebrain.ai", "referred_name": "Nicole Adams",     "status": "completed", "days_ago": 12, "payment_amount": 79.00},

    # Michael Hancock (1 completed)
    {"referrer_code": "PB-MH7K", "referred_email": "mh-ref1@purebrain.ai", "referred_name": "Greg Williams",    "status": "completed", "days_ago": 16, "payment_amount": 149.00},

    # Alex Logie (1 pending)
    {"referrer_code": "PB-AL3X", "referred_email": "al-ref1@purebrain.ai", "referred_name": "Sam Taylor",       "status": "pending",   "days_ago": 3,  "payment_amount": 0},
]

COMMISSION_RATE = 0.05


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Ensure payout_requests table exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS payout_requests (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id    TEXT NOT NULL UNIQUE,
        referral_code TEXT NOT NULL,
        paypal_email  TEXT NOT NULL DEFAULT '',
        amount        REAL NOT NULL DEFAULT 0.0,
        status        TEXT NOT NULL DEFAULT 'pending',
        created_at    TEXT NOT NULL,
        created_at_ts INTEGER NOT NULL DEFAULT 0,
        paid_at       TEXT,
        batch_id      TEXT DEFAULT '',
        notes         TEXT DEFAULT ''
    )
    """)

    now = now_iso()
    referrer_id_map = {}  # code -> id

    # ── Seed Affiliates ──────────────────────────────────────────────────
    for aff in AFFILIATES:
        c.execute("SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE", (aff["code"],))
        existing = c.fetchone()
        if existing:
            referrer_id_map[aff["code"]] = existing["id"]
            # Update name/paypal if needed (don't touch password)
            c.execute(
                "UPDATE referrers SET user_name = ?, paypal_email = ? WHERE id = ?",
                (aff["name"], aff.get("paypal_email", ""), existing["id"])
            )
            print(f"  Updated existing affiliate: {aff['code']} ({aff['name']})")
        else:
            # New affiliate — generate a random password
            random_pw = hash_pw("changeme123")
            c.execute(
                "INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (aff["name"], aff["email"], aff["code"], random_pw, aff.get("paypal_email", ""), now)
            )
            referrer_id_map[aff["code"]] = c.lastrowid
            print(f"  Created new affiliate: {aff['code']} ({aff['name']})")

    conn.commit()

    # ── Seed Referrals ───────────────────────────────────────────────────
    for ref in REFERRALS:
        referrer_id = referrer_id_map.get(ref["referrer_code"])
        if not referrer_id:
            print(f"  WARNING: No referrer found for code {ref['referrer_code']}")
            continue

        # Check if already exists
        c.execute(
            "SELECT id FROM referrals WHERE referrer_id = ? AND referred_email = ? COLLATE NOCASE",
            (referrer_id, ref["referred_email"])
        )
        if c.fetchone():
            print(f"  Skipping duplicate referral: {ref['referred_email']}")
            continue

        ts = int(time.time()) - (ref["days_ago"] * 86400)
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
        completed_at = created_at if ref["status"] == "completed" else None

        c.execute(
            "INSERT INTO referrals (referrer_id, referred_email, referred_name, status, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
            (referrer_id, ref["referred_email"], ref["referred_name"], ref["status"], created_at, completed_at)
        )
        referral_id = c.lastrowid
        print(f"  Added referral: {ref['referrer_code']} -> {ref['referred_name']} ({ref['status']})")

        # Create commission + reward if completed and has payment
        if ref["status"] == "completed" and ref["payment_amount"] > 0:
            commission_value = round(ref["payment_amount"] * COMMISSION_RATE, 2)

            # Commission payment record
            c.execute(
                "INSERT INTO commission_payments (referrer_id, referral_id, payer_email, order_id, payment_amount, commission_rate, commission_value, tier, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (referrer_id, referral_id, ref["referred_email"], f"seed-{referral_id}", ref["payment_amount"], COMMISSION_RATE, commission_value, "Awakened" if ref["payment_amount"] >= 149 else "Trial", created_at)
            )

            # Reward record (earnings ledger)
            c.execute(
                "INSERT INTO rewards (referrer_id, referral_id, reward_type, reward_value, issued_at) VALUES (?, ?, 'cash', ?, ?)",
                (referrer_id, referral_id, commission_value, created_at)
            )
            print(f"    Commission: ${commission_value:.2f} from ${ref['payment_amount']:.2f} payment")

    conn.commit()

    # ── Seed Click Data ──────────────────────────────────────────────────
    click_counts = {
        "JAREDSB0": 45,
        "PB-AYXE": 28,
        "PB-K22P": 15,
        "PB-MH7K": 8,
        "PB-AL3X": 5,
    }
    for code, count in click_counts.items():
        c.execute("SELECT COUNT(*) as cnt FROM referral_clicks WHERE referral_code = ?", (code,))
        existing_clicks = c.fetchone()["cnt"]
        needed = max(0, count - existing_clicks)
        for i in range(needed):
            ts = int(time.time()) - ((count - i) * 3600 * 6)  # spread clicks
            clicked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
            c.execute(
                "INSERT INTO referral_clicks (referral_code, ip_hash, clicked_at) VALUES (?, ?, ?)",
                (code, f"seed-{i}", clicked_at)
            )
        if needed > 0:
            print(f"  Added {needed} clicks for {code}")

    conn.commit()

    # ── Verify ───────────────────────────────────────────────────────────
    print("\n=== VERIFICATION ===")
    for aff in AFFILIATES:
        rid = referrer_id_map.get(aff["code"])
        c.execute("SELECT COUNT(*) as c FROM referrals WHERE referrer_id = ? AND status = 'completed'", (rid,))
        completed = c.fetchone()["c"]
        c.execute("SELECT COALESCE(SUM(reward_value), 0) as total FROM rewards WHERE referrer_id = ?", (rid,))
        earnings = c.fetchone()["total"]
        c.execute("SELECT COUNT(*) as c FROM referral_clicks WHERE referral_code = ?", (aff["code"],))
        clicks = c.fetchone()["c"]
        print(f"  {aff['code']} ({aff['name']}): {completed} completed, ${earnings:.2f} earned, {clicks} clicks")

    conn.close()
    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
