#!/usr/bin/env python3
"""Pre-flight checks for Jason King INSERT — read-only.

1. Verify Sheila row exists (for FK context — no household_id col yet per Amy precedent)
2. Pull Amy Housand canonical row from purebrain-clients (template shape)
3. Confirm Jason absent
4. Snapshot pre-INSERT count
5. Probe magic link
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

    print("=== STEP 1: Sheila Whitehurst lookup (FK context) ===")
    sheila = d1_query(acct, token, CLIENTS_DB_ID,
                      "SELECT id, email, name, ai_name, tier, payment_status, paypal_subscription_id, total_paid FROM clients WHERE LOWER(email)=LOWER(?)",
                      ["sheila@couplify.com"])
    print(json.dumps(sheila["result"][0]["results"], indent=2))

    print("\n=== STEP 2: Amy Housand canonical row (template shape) ===")
    amy = d1_query(acct, token, CLIENTS_DB_ID,
                   "SELECT * FROM clients WHERE LOWER(email)=LOWER(?)",
                   ["amy@couplify.com"])
    print(json.dumps(amy["result"][0]["results"], indent=2))

    print("\n=== STEP 3: confirm Jason absent ===")
    jason_check = d1_query(acct, token, CLIENTS_DB_ID,
                           "SELECT count(*) AS cnt, GROUP_CONCAT(id) AS ids FROM clients WHERE LOWER(email)=LOWER(?)",
                           ["jason@couplify.com"])
    print(json.dumps(jason_check["result"][0]["results"], indent=2))

    print("\n=== STEP 4: pre-INSERT total client count ===")
    cnt = d1_query(acct, token, CLIENTS_DB_ID, "SELECT count(*) AS cnt FROM clients")
    print(f"pre-INSERT count: {cnt['result'][0]['results'][0]['cnt']}")

    print("\n=== STEP 5: list all Couplify rows (verify household map) ===")
    couplify = d1_query(acct, token, CLIENTS_DB_ID,
                        "SELECT id, email, name, ai_name, tier, payment_status, paypal_subscription_id, total_paid FROM clients WHERE email LIKE '%@couplify.com' ORDER BY id")
    print(json.dumps(couplify["result"][0]["results"], indent=2))


if __name__ == "__main__":
    main()
