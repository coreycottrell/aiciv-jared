# Duo Chat Setup Guide

How to install Duo Chat in a customer's AI containers and portal.

## Prerequisites

- Customer has 2+ AI containers with tmux sessions
- Access to the trio-comms Cloudflare Worker (for adding auth tokens)
- Customer portal HTML where the widget will be injected

## Step 1: Generate Duo ID

Each customer gets one unique duo_id (UUID).

```bash
DUO_ID=$(python3 -c "import uuid; print(str(uuid.uuid4()))")
echo "Duo ID: $DUO_ID"
```

## Step 2: Generate Auth Tokens

Generate one token per participant (each AI + one for the portal widget).

```bash
# One token per AI container
TOKEN_AI1=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
TOKEN_AI2=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# One token for the portal (human-side widget)
TOKEN_PORTAL=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "AI1 token: $TOKEN_AI1"
echo "AI2 token: $TOKEN_AI2"
echo "Portal token: $TOKEN_PORTAL"
```

## Step 3: Register Tokens in the Worker

Add the tokens to the trio-comms worker so it can authenticate each participant.

The worker uses environment secrets to map tokens to sender IDs. For multi-tenant Duo,
you need to add tokens to a token lookup table or as Wrangler secrets.

Option A — Add as Wrangler secrets (for small scale):
```bash
# In the trio-comms worker directory:
wrangler secret put DUO_TOKEN_{CUSTOMER_NAME}_AI1
wrangler secret put DUO_TOKEN_{CUSTOMER_NAME}_AI2
wrangler secret put DUO_TOKEN_{CUSTOMER_NAME}_PORTAL
```

Then update the worker's authSender() function to include the new token mappings.

Option B — Use a D1 token table (recommended for scale):
```sql
CREATE TABLE IF NOT EXISTS duo_tokens (
  token TEXT PRIMARY KEY,
  sender_id TEXT NOT NULL,
  duo_id TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

INSERT INTO duo_tokens (token, sender_id, duo_id) VALUES
  ('{TOKEN_AI1}', 'ai1_name', '{DUO_ID}'),
  ('{TOKEN_AI2}', 'ai2_name', '{DUO_ID}'),
  ('{TOKEN_PORTAL}', 'human_name', '{DUO_ID}');
```

## Step 4: Create Config Files for Each AI Container

For AI Container 1 (`~/duo/duo-config.json`):
```json
{
  "duo_id": "{DUO_ID}",
  "token": "{TOKEN_AI1}",
  "comms_url": "https://trio-comms.in0v8.workers.dev",
  "tmux_session": "main",
  "my_sender_id": "ai1_name"
}
```

For AI Container 2 (`~/duo/duo-config.json`):
```json
{
  "duo_id": "{DUO_ID}",
  "token": "{TOKEN_AI2}",
  "comms_url": "https://trio-comms.in0v8.workers.dev",
  "tmux_session": "main",
  "my_sender_id": "ai2_name"
}
```

## Step 5: Install Injector + CLI in Each Container

Copy the files to each AI container:

```bash
# On each AI container:
mkdir -p ~/duo

# Copy files (via scp, rsync, or birth pipeline)
cp duo_injector.py ~/duo/duo_injector.py
cp post-to-duo.sh ~/duo/post-to-duo.sh
chmod +x ~/duo/post-to-duo.sh
```

## Step 6: Start the Injector

Option A — nohup (simple):
```bash
nohup python3 ~/duo/duo_injector.py >> ~/duo/duo-injector.log 2>&1 &
```

Option B — systemd service (recommended):
```bash
sudo tee /etc/systemd/system/duo-injector.service << 'EOF'
[Unit]
Description=Duo Chat Injector
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER
ExecStart=/usr/bin/python3 /home/YOUR_USER/duo/duo_injector.py
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USER/duo/duo-injector.log
StandardError=append:/home/YOUR_USER/duo/duo-injector.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable duo-injector
sudo systemctl start duo-injector
```

## Step 7: Inject Widget into Portal HTML

Add the widget to the customer's portal. Two options:

Option A — Include the HTML file directly:

Set the config before the widget loads:
```html
<script>
  window.DUO_CONFIG = {
    duo_id: "CUSTOMER_DUO_ID",
    token: "PORTAL_TOKEN",
    comms_url: "https://trio-comms.in0v8.workers.dev",
    title: "AI Chat",
    my_id: "human_name"
  };
</script>
<!-- Then include duo-widget.html contents here -->
```

Option B — Add a sidebar/nav trigger button:
```html
<button onclick="window.openDuoWidget()">Open AI Chat</button>
```

The `my_id` field in DUO_CONFIG determines which messages appear on the right side
(the portal user's messages). Set it to the human's sender_id.

## Step 8: Verify

1. Open the portal and click to open Duo Chat
2. Send a message from the portal — it should appear in both AI containers' tmux sessions
3. From an AI container, run: `~/duo/post-to-duo.sh "Hello from AI1"`
4. The message should appear in the portal widget and in the other AI's tmux session

## Architecture Notes

- The widget polls the trio-comms worker directly (no portal proxy needed)
- Each AI's injector polls independently every 20 seconds
- Messages are stored in Cloudflare D1, scoped by duo_id (maps to trio_id in the worker)
- The same trio-comms worker serves both Trio (internal) and Duo (customer) chats
- Tokens are scoped per duo_id — customers cannot see each other's messages
- All data flows through HTTPS; no direct container-to-container communication

## File Inventory

| File | Purpose | Location |
|------|---------|----------|
| duo-widget.html | Chat UI for portal | Injected into portal HTML |
| duo_injector.py | Polls + injects to tmux | ~/duo/ on each AI container |
| post-to-duo.sh | CLI message sender | ~/duo/ on each AI container |
| duo-config.json | Per-container config | ~/duo/ on each AI container |
