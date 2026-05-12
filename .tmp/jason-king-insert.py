#!/usr/bin/env python3
"""Jason King INSERT — purebrain-clients D1, Couplify Duo 2 mirror of Amy/Cai.

CTO brief: cto-prebuild-jason-king-add-2026-05-12.md
Pattern reference: Amy Housand (id=95) covered-seat shape
Constitutional gate: write to purebrain-clients ONLY (May 7 ban on social-DB)
"""
import json
import sys
import urllib.request

CLIENTS_DB_ID = "aaade55e-f888-48ea-8e63-b934d697379b"
ENV_PATH = "/home/jared/projects/AI-CIV/aether/.env"


def load_cf():
    acct, token = None, None
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("CF_ACCOUNT_ID="):
                acct = line.split("=", 1)[1].strip()
            elif line.startswith("CF_API_TOKEN="):
                token = line.split("=", 1)[1].strip()
    if not acct or not token:
        sys.exit("missing CF creds")
    return acct, token


def d1_query(acct, token, db_id, sql, params=None):
    body = {"sql": sql}
    if params is not None:
        body["params"] = params
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/{db_id}/query",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def main():
    acct, token = load_cf()

    print("=== STEP 0: re-confirm Jason absent (pre-INSERT idempotency gate) ===")
    chk = d1_query(acct, token, CLIENTS_DB_ID,
                   "SELECT count(*) AS cnt FROM clients WHERE LOWER(email)=LOWER(?)",
                   ["jason@couplify.com"])
    pre_cnt = chk["result"][0]["results"][0]["cnt"]
    print(f"pre-INSERT Jason row count: {pre_cnt}")
    if pre_cnt != 0:
        sys.exit("ABORT: Jason already in clients (idempotency check failed)")

    print("\n=== STEP 1: INSERT Jason King (16-col parameterized, Amy Housand pattern) ===")
    cols = [
        "email", "name", "ai_name", "company",
        "tier", "payment_status",
        "paypal_subscription_id", "total_paid",
        "status", "monthly_amount",
        "joined_date", "source",
        "hidden", "notes",
        "goes_by", "magic_link",
    ]
    values = [
        "jason@couplify.com",                                                # email
        "Jason King",                                                        # name
        "Resolve",                                                           # ai_name
        "Couplify",                                                          # company
        "Partnered",                                                         # tier
        "covered",                                                           # payment_status
        "",                                                                  # paypal_subscription_id (covered seat)
        0,                                                                   # total_paid
        "active",                                                            # status
        0,                                                                   # monthly_amount
        "2026-05-12",                                                        # joined_date
        "paypal",                                                            # source (indirect via Sheila's sub)
        0,                                                                   # hidden
        "Covered under Sheila Whitehurst sub I-RBXHJ68JCJPL (Couplify Duo 2)",  # notes
        "Jason",                                                             # goes_by
        "https://resolve-jason.app.purebrain.ai/?token=zSry2NKLePKoxh0Tu8h4Yb4snNRx8GiM9LT7aD9mECA",  # magic_link
    ]
    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join(cols)
    insert_sql = f"INSERT INTO clients ({col_list}) VALUES ({placeholders})"
    print(f"SQL: {insert_sql}")
    # Sanitize PII in logged params (only show structure)
    safe_log = [(c, "<set>" if v not in ("", 0, None) else repr(v)) for c, v in zip(cols, values)]
    print(f"PARAMS shape (count={len(values)}):")
    for c, v in safe_log:
        print(f"  {c}: {v}")

    res = d1_query(acct, token, CLIENTS_DB_ID, insert_sql, values)
    print("\nResponse:")
    print(json.dumps(res, indent=2))
    meta = res["result"][0]["meta"]
    print(f"\nINSERT meta: changes={meta.get('changes')} last_row_id={meta.get('last_row_id')} rows_written={meta.get('rows_written')}")
    if meta.get("changes") != 1:
        sys.exit(f"ABORT: expected changes=1, got changes={meta.get('changes')}")

    print("\n=== STEP 2: post-INSERT verification — full row read-back ===")
    jason_row = d1_query(acct, token, CLIENTS_DB_ID,
                         "SELECT * FROM clients WHERE LOWER(email)=LOWER(?)",
                         ["jason@couplify.com"])
    rows = jason_row["result"][0]["results"]
    print(json.dumps(rows, indent=2))
    if len(rows) != 1:
        sys.exit(f"ABORT: expected 1 Jason row post-INSERT, got {len(rows)}")

    print("\n=== STEP 3: post-INSERT total count ===")
    cnt_post = d1_query(acct, token, CLIENTS_DB_ID, "SELECT count(*) AS cnt FROM clients")
    post_cnt = cnt_post["result"][0]["results"][0]["cnt"]
    print(f"post-INSERT count: {post_cnt}")

    print("\n=== STEP 4: Couplify household map (final state — 4 rows expected) ===")
    couplify = d1_query(acct, token, CLIENTS_DB_ID,
                        "SELECT id, email, name, ai_name, tier, payment_status, paypal_subscription_id, total_paid FROM clients WHERE email LIKE '%@couplify.com' ORDER BY id")
    print(json.dumps(couplify["result"][0]["results"], indent=2))

    print("\n=== STEP 5: purebrain-social count (constitutional check — should be UNCHANGED) ===")
    SOCIAL_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
    s_cnt = d1_query(acct, token, SOCIAL_DB_ID, "SELECT count(*) AS cnt FROM clients")
    s_jason = d1_query(acct, token, SOCIAL_DB_ID,
                       "SELECT count(*) AS cnt FROM clients WHERE LOWER(email)=LOWER(?)",
                       ["jason@couplify.com"])
    print(f"social  count: {s_cnt['result'][0]['results'][0]['cnt']} (expect unchanged from baseline)")
    print(f"social  jason rows: {s_jason['result'][0]['results'][0]['cnt']} (expect 0 — constitutional ban)")

    print("\n=== STEP 6: Sheila row INTACT check (READ-ONLY confirmation) ===")
    sheila = d1_query(acct, token, CLIENTS_DB_ID,
                      "SELECT id, email, name, ai_name, payment_status, paypal_subscription_id, total_paid FROM clients WHERE LOWER(email)=LOWER(?)",
                      ["sheila@couplify.com"])
    print(json.dumps(sheila["result"][0]["results"], indent=2))
    print("\n=== SHIP COMPLETE ===")


if __name__ == "__main__":
    main()
