#!/bin/bash
# Migrate existing PureApex data from SQLite export to D1
# Run from: exports/departments/systems-technology/apex-migration/
#
# Prerequisites:
#   1. D1 database created and schema applied
#   2. data-export.json exists (exported from server)
#   3. Correct CF credentials in environment
#
# Usage: bash migrate-data-to-d1.sh

set -euo pipefail

export CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290
export CLOUDFLARE_API_KEY=251911c00fe74daedaff1133decfc3a00f66c
export CLOUDFLARE_EMAIL=jared@puretechnology.nyc

DB_NAME="pureapex-db"
DATA_FILE="data-export.json"

if [ ! -f "$DATA_FILE" ]; then
  echo "ERROR: $DATA_FILE not found. Export data from server first."
  exit 1
fi

echo "=== PureApex D1 Data Migration ==="
echo ""

# Step 1: Apply schema migrations
echo "[1/6] Applying D1 schema migrations..."
cd pureapex-worker
npx wrangler d1 migrations apply $DB_NAME --remote
cd ..

# Step 2: Generate SQL insert statements from the JSON export
echo "[2/6] Generating SQL insert statements..."

python3 << 'PYEOF'
import json
import subprocess
import sys

with open("data-export.json") as f:
    data = json.load(f)

# We need to re-hash passwords with PBKDF2 since bcrypt won't work in Workers
# For migration, we'll insert users with known passwords using PBKDF2 hashing
# The Worker will hash them on first use

sql_statements = []

# Users - we skip these since the Worker seeds them automatically with PBKDF2 hashes
print(f"  Users: {len(data.get('users', []))} (will be re-seeded by Worker)")

# Opportunities
opps = data.get("opportunities", [])
print(f"  Opportunities: {len(opps)}")
for opp in opps:
    cols = [
        "company", "contact_name", "contact_title", "contact_email", "contact_linkedin",
        "contact_location", "type", "vertical", "geography", "stage", "playbook_weapon",
        "owner", "estimated_value", "next_action", "next_action_date", "notes", "partner",
        "meddpicc_metrics", "meddpicc_economic_buyer", "meddpicc_decision_criteria",
        "meddpicc_decision_process", "meddpicc_paper_process", "meddpicc_identify_pain",
        "meddpicc_champion", "meddpicc_competition", "emotional_arc", "division",
        "readiness_pnl_pain", "readiness_decision_maker", "readiness_competitor",
        "readiness_unique_angle", "readiness_proof", "stage_changed_at",
        "created_by", "created_at", "updated_at"
    ]
    vals = []
    for c in cols:
        v = opp.get(c)
        if v is None:
            vals.append("NULL")
        elif isinstance(v, (int, float)):
            vals.append(str(v))
        else:
            # Escape single quotes
            vals.append("'" + str(v).replace("'", "''") + "'")
    sql = f"INSERT INTO opportunities ({', '.join(cols)}) VALUES ({', '.join(vals)});"
    sql_statements.append(sql)

# Activity log
activities = data.get("activity_log", [])
print(f"  Activity log: {len(activities)}")
for a in activities:
    opp_id = a.get("opportunity_id") or "NULL"
    action = str(a.get("action", "")).replace("'", "''")
    actor = str(a.get("actor", "")).replace("'", "''")
    created = str(a.get("created_at", "")).replace("'", "''")
    sql = f"INSERT INTO activity_log (opportunity_id, action, actor, created_at) VALUES ({opp_id}, '{action}', '{actor}', '{created}');"
    sql_statements.append(sql)

# Meeting notes
notes = data.get("meeting_notes", [])
print(f"  Meeting notes: {len(notes)}")
for n in notes:
    opp_id = n.get("opportunity_id") or "NULL"
    note_type = str(n.get("note_type", "meeting")).replace("'", "''")
    content = str(n.get("content", "")).replace("'", "''")
    actor = str(n.get("actor", "")).replace("'", "''")
    created = str(n.get("created_at", "")).replace("'", "''")
    sql = f"INSERT INTO meeting_notes (opportunity_id, note_type, content, actor, created_at) VALUES ({opp_id}, '{note_type}', '{content}', '{actor}', '{created}');"
    sql_statements.append(sql)

# LinkedIn tokens - skip, they should re-auth on new platform
print(f"  LinkedIn tokens: skipped (re-auth required)")

# Prospect pages
pages = data.get("prospect_pages", [])
print(f"  Prospect pages: {len(pages)}")
for p in pages:
    slug = str(p.get("slug", "")).replace("'", "''")
    company = str(p.get("company_name", "")).replace("'", "''")
    pw = str(p.get("password", "")).replace("'", "''")
    html_c = str(p.get("html_content", "")).replace("'", "''")
    is_active = p.get("is_active", 1)
    view_count = p.get("view_count", 0)
    created_by = str(p.get("created_by", "")).replace("'", "''")
    created = str(p.get("created_at", "")).replace("'", "''")
    updated = str(p.get("updated_at", "")).replace("'", "''")
    sql = f"INSERT INTO prospect_pages (slug, company_name, password, html_content, is_active, view_count, created_by, created_at, updated_at) VALUES ('{slug}', '{company}', '{pw}', '{html_c}', {is_active}, {view_count}, '{created_by}', '{created}', '{updated}');"
    sql_statements.append(sql)

# Write to SQL file
with open("migration-data.sql", "w") as f:
    f.write("\n".join(sql_statements))

print(f"\n  Total SQL statements: {len(sql_statements)}")
print(f"  Written to: migration-data.sql")
PYEOF

# Step 3: Execute the SQL against D1
echo ""
echo "[3/6] Importing data to D1..."
cd pureapex-worker
npx wrangler d1 execute $DB_NAME --remote --file=../migration-data.sql
cd ..

echo ""
echo "[4/6] Verifying data..."
cd pureapex-worker
npx wrangler d1 execute $DB_NAME --remote --command="SELECT 'opportunities' as tbl, COUNT(*) as cnt FROM opportunities UNION ALL SELECT 'activity_log', COUNT(*) FROM activity_log UNION ALL SELECT 'meeting_notes', COUNT(*) FROM meeting_notes UNION ALL SELECT 'prospect_pages', COUNT(*) FROM prospect_pages;"
cd ..

echo ""
echo "[5/6] Data migration complete!"
echo ""
echo "[6/6] Next steps:"
echo "  1. Create KV namespace: npx wrangler kv namespace create SESSIONS"
echo "  2. Update wrangler.jsonc with KV namespace ID"
echo "  3. Set LinkedIn secret: npx wrangler secret put LINKEDIN_CLIENT_SECRET"
echo "  4. Deploy: npx wrangler deploy"
echo "  5. Update DNS: apex.purebrain.ai -> Workers route"
echo "  6. Test all routes"
echo "  7. Decommission server: systemctl stop pureapex && systemctl disable pureapex"
