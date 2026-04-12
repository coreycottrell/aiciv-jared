# Incident: Greg Adamo Portal 502 — Resolved

**Date**: 2026-03-20
**Customer**: Greg Adamo (human_email: gadamo1314@gmail.com)
**AI CIV Name**: Common Ground
**Type**: operational | incident-resolved
**Resolution Time**: ~15 minutes

---

## Incident Summary

Greg Adamo's PureBrain portal (vyasagreg-adamo.purebrain.ai) was returning 502.
Portal server process had been killed and the auto-restart loop in tmux had exited.

---

## Container Facts

| Field | Value |
|-------|-------|
| SSH Port | 2226 |
| Host | 37.27.237.109 |
| SSH User | aiciv |
| Container IP | 172.17.0.2 (default Docker bridge — older container) |
| Portal Port | 8097 |
| CIV Name | Common Ground |
| Human | Greg Adamo (gadamo1314@gmail.com) |
| Public URL | vyasagreg-adamo.purebrain.ai |
| Alt URL | vyasagreg-adamo.ai-civ.com |
| Old URL | vyasagreg-adamo.app.purebrain.ai (still works via tunnel) |

---

## Root Cause

Portal server (portal_server.py) had been killed (OOM or manual) and the
tmux auto-restart loop in session portal-server had exited to a bash prompt.
No portal process was running. Port 8097 had no listener. Caddy on the host
could connect to the container via Docker port mapping but got connection refused.

---

## Key Investigation Finding: Wrong Container Initially Targeted

The task specified port 2237 for Greg's container. That was INCORRECT.
Port 2237 is "Greg" the AI (CIV name=Greg, human=Lucas Neuteufel / Hunden.com).
Port 2226 is Greg Adamo's actual container (CIV name=Common Ground).

LESSON: Always verify container identity via portal_owner.json before diagnosing.
The SSH port is NOT reliably associated with the human name — check the owner file.

---

## Network Architecture for Port 2226 Container

This is an OLDER container on the default Docker bridge (172.17.0.x):
- Container IP: 172.17.0.2
- Docker bridge gateway (host): 172.17.0.1
- Caddy on host uses Docker port mapping (NOT direct container IP)
- Caddy logs show requests from 172.17.0.1 (the host bridge)

Newer containers (ports 2235+) use 192.168.64.x network.

---

## Fix Applied

ssh -p 2226 aiciv@37.27.237.109
tmux send-keys -t portal-server 'while true; do cd /home/aiciv/purebrain_portal && python3 portal_server.py; echo portal-crashed-restarting; sleep 2; done' Enter

---

## Verification

- Port 8097: listening on 0.0.0.0 (confirmed via /proc/net/tcp)
- localhost:8097: HTTP 200
- vyasagreg-adamo.ai-civ.com: HTTP 200
- vyasagreg-adamo.purebrain.ai: HTTP 200
- vyasagreg-adamo.app.purebrain.ai: HTTP 200

---

## Prevention

1. Auto-restart loop in portal-server tmux exiting to bash = portal goes dark.
   Witness should add a systemd or cron watchdog for port 8097 per container.
2. CTS support keypair NOT yet provisioned for Greg Adamo / port 2226. Add to registry.

---

## Fleet Map Update (2026-03-20 additions)

| Port | CIV Name | Human | Email |
|------|----------|-------|-------|
| 2221 | True Bearing | Corey Cottrell | coreycmusic@gmail.com |
| 2223 | (test) | Witness TestUser | witness-test@test.ai-civ.com |
| 2226 | Common Ground | Greg Adamo | gadamo1314@gmail.com |
| 2228 | Anchor | John Smith | jsmith@puretechnolgy.nyc |
| 2235 | Present | Travis Moorhead | cryptoconsultants1@gmail.com |
| 2236 | Still | Bethanie DeRose | bethanie@hunden.com |
| 2237 | Greg (AI name) | Lucas Neuteufel | lucas@hunden.com |
| 2238 | testbirth-march19 | Test Human | test.example.com |
