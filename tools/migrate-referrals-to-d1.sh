#!/usr/bin/env bash
# migrate-referrals-to-d1.sh — Export referral data from portal SQLite and import to CF D1.
#
# Prerequisites:
#   1. D1 database "purebrain-referrals" must be created:
#      wrangler d1 create purebrain-referrals
#   2. Schema must be applied:
#      wrangler d1 execute purebrain-referrals --file=exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql
#   3. SSH access to portal server
#
# Usage:
#   ./tools/migrate-referrals-to-d1.sh
#
# This script:
#   1. SSHs to portal server, dumps referrers/referrals/clicks/rewards/commissions as SQL INSERT
#   2. Writes to a local .sql file
#   3. Imports via wrangler d1 execute

set -euo pipefail

REMOTE="aiciv@37.27.237.109"
REMOTE_PORT="2213"
REMOTE_DB="/home/aiciv/purebrain_portal/referrals.db"
LOCAL_DUMP="/tmp/referral-data-dump.sql"
D1_DB="purebrain-referrals"

echo "=== Step 1: Dump data from portal server ==="

ssh -p "$REMOTE_PORT" "$REMOTE" "sqlite3 '$REMOTE_DB' <<'EOSQL'
.mode insert referrers
SELECT * FROM referrers;
.mode insert referrals
SELECT * FROM referrals;
.mode insert referral_clicks
SELECT * FROM referral_clicks;
.mode insert rewards
SELECT * FROM rewards;
.mode insert commission_payments
SELECT * FROM commission_payments;
.mode insert admin_tokens
SELECT * FROM admin_tokens;
EOSQL" > "$LOCAL_DUMP"

# Count rows
LINES=$(wc -l < "$LOCAL_DUMP")
echo "Dumped $LINES INSERT statements to $LOCAL_DUMP"

if [ "$LINES" -eq 0 ]; then
    echo "WARNING: No data to migrate. Check SSH connection and DB path."
    exit 1
fi

echo ""
echo "=== Step 2: Preview data ==="
head -5 "$LOCAL_DUMP"
echo "..."
echo ""

echo "=== Step 3: Import to D1 ==="
echo "Run the following command to import:"
echo ""
echo "  wrangler d1 execute $D1_DB --file=$LOCAL_DUMP"
echo ""
echo "Or to do it in one shot (be careful — this is production data):"
echo "  wrangler d1 execute $D1_DB --file=$LOCAL_DUMP --yes"
echo ""
echo "Note: Payout requests (currently in JSONL) must be migrated separately."
echo "Check /home/aiciv/purebrain_portal/payout_requests.jsonl on the server."
