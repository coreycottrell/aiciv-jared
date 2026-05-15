# disk-telemetry-daemon systemd install

## One-time host setup

```bash
# 1. State directory (owned by the User= in the unit)
sudo mkdir -p /var/lib/disk-telemetry
sudo chown jared:jared /var/lib/disk-telemetry
sudo chmod 0750 /var/lib/disk-telemetry

# 2. Environment file (contains HMAC token — 0600!)
sudo mkdir -p /etc/disk-telemetry
sudo tee /etc/disk-telemetry/daemon.env >/dev/null <<'EOF'
CIV_NAME=aether
DISK_TELEMETRY_INGEST_URL=https://disk-telemetry-ingest.in0v8.workers.dev/ingest
DISK_TELEMETRY_INGEST_TOKEN=<paste-from-wrangler-secret>
DISK_TELEMETRY_ENABLED=1
DISK_TELEMETRY_POLL_SECONDS=300
EOF
sudo chown root:root /etc/disk-telemetry/daemon.env
sudo chmod 0600 /etc/disk-telemetry/daemon.env

# 3. Install service unit
sudo cp /home/jared/projects/AI-CIV/aether/systemd/disk-telemetry-daemon.service \
        /etc/systemd/system/disk-telemetry-daemon.service
sudo systemctl daemon-reload

# 4. Enable + start
sudo systemctl enable --now disk-telemetry-daemon.service

# 5. Verify
systemctl status disk-telemetry-daemon
journalctl -u disk-telemetry-daemon -n 50 --no-pager
```

## Kill switch (no code deploy required)

```bash
sudo sed -i 's/^DISK_TELEMETRY_ENABLED=.*/DISK_TELEMETRY_ENABLED=0/' \
         /etc/disk-telemetry/daemon.env
sudo systemctl restart disk-telemetry-daemon
```

## Rollout order

1. **Canary**: `46.62.187.74` (purebrain-3) — well-understood from Gary incident
2. After 24h clean: roll to remaining Hetzner Aether/CIV hosts
3. Wave 3: container-resident CIVs install daemon inside container (mount point = container `/`)
