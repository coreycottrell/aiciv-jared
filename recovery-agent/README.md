# recovery-agent

**Status**: Phase 1 staging in aether repo. Deploys to Hetzner customer-portal hosts.
**Spec**: `specs/customer-portal-recovery-2026-05-15.md`
**CTO review**: `specs/cto-review-4-specs-2026-05-15.md` (verdict: AMEND)
**Jared greenlight**: 2026-05-15 22:40 UTC — Whitehurst as Phase-2 canary, silent recovery + audit log.

## Purpose

Production replacement for ad-hoc `ssh + pkill + docker restart` ops on customer-portal hosts. Exposes exactly ONE HTTP endpoint — `POST /restart` — gated by HMAC (nonce + timestamp), idempotency, loop detection, and a docker-restart sudoers allowlist.

## CTO amendments folded in

| # | Amendment | Where |
|---|---|---|
| 1 | Docker socket via **sudoers**, NOT docker-group | `systemd/recovery-agent.sudoers` |
| 2 | **Cloudflare Tunnel** (cloudflared) — not direct HTTPS | `systemd/cloudflared-config.yml` template |
| 3 | `/health` returns `ai_alive: bool` (PID + thread check) | `health_probe.py` |
| 4 | HMAC with **nonce + timestamp** replay protection | `recovery_agent.py` |
| 5 | Bind to **127.0.0.1:9877** as break-glass fallback | `recovery_agent.py` |
| 6 | Idempotency cache for restart commands (60s) | `recovery_agent.py` |
| 7 | Loop detection: >2 restarts in 10 min → page TRIO + stop | `recovery_agent.py` |

## Files

```
recovery-agent/
  recovery_agent.py          # HTTP server (stdlib http.server) on 127.0.0.1:9877
  health_probe.py            # docker exec probe — returns ai_alive: bool
  requirements.txt           # stdlib only — no extra deps needed
  systemd/
    recovery-agent.service   # systemd unit (hardened)
    recovery-agent.sudoers   # sudoers entry — narrow allowlist
    cloudflared-config.yml   # Tunnel config template
  config/
    allowlist.txt.example    # /etc/recovery-agent/allowlist.txt template
  tests/
    test_recovery_agent.py   # HMAC + allowlist + idempotency + loop tests
```

## Phase plan

- **Phase 1 (NOW)**: Deploy daemon to `purebrain-3` (46.62.187.74). NO customer-container changes.
- **Phase 2 canary**: Whitehurst monitored + auto-restartable.
- **Phase 3**: Roll out after 7-day clean run on Whitehurst.

## Constitutional guarantees

- Bound to `127.0.0.1` — never publicly reachable. Tunnel is the only ingress.
- Sudoers allowlist enforced — daemon CANNOT restart anything outside the allowlist.
- Audit log: every action POST'd to CF Worker → D1 `customer_portal_recovery_log`. Silent recovery still leaves a paper trail.
- NO customer-container deploys in this commit cycle. Container-side `/health` is a Phase-2 spec amendment.

## Deploy (Aether will execute)

```bash
# On the Hetzner host (purebrain-3) as root:
useradd --system --home /var/lib/recovery-agent --shell /usr/sbin/nologin recovery-agent
mkdir -p /etc/recovery-agent /var/log/recovery-agent /var/lib/recovery-agent
cp config/allowlist.txt.example /etc/recovery-agent/allowlist.txt   # then edit
cp systemd/recovery-agent.sudoers /etc/sudoers.d/recovery-agent
chmod 0440 /etc/sudoers.d/recovery-agent
visudo -c                                                            # verify syntax
cp systemd/recovery-agent.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now recovery-agent.service

# Cloudflared (Aether handles tunnel registration separately)
```
