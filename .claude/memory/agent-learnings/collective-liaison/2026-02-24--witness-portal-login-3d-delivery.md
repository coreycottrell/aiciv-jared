# Memory: 3D Portal Login Page Delivered to Witness

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational
**Topic**: Delivered purebrain-portal-login-3d.html to Witness via SSH direct channel; requested deployment to 5.161.90.32:8098

---

## What Happened

Jared requested that the new 3D portal login page be sent to Witness (Corey's collective) for integration into the current PureBrain app system at http://5.161.90.32:8098/

The file was delivered using the established SSH direct channel protocol.

---

## Files Delivered

- `/tmp/witness-aether-comms/purebrain-portal-login-3d.html` (64,784 bytes)
- `/tmp/witness-aether-comms/from-aether-portal-login-3d.md` (cover note with integration details)

---

## Tmux Notification Sent

Session: `witness-corey-primary-20260224-191143` on 104.248.239.98:2203
Prefix: [from-Aether] as required by protocol
Message: pointed to both files with summary of request

---

## What We Asked Witness

1. Confirm receipt
2. Whether they can deploy to 5.161.90.32:8098 as the login page
3. Whether they can wire handleLogin() to their auth backend
4. Jared's question: can Witness do this without Corey's direct involvement?
5. Estimated timeline

---

## Login IDs Preserved (Drop-in Compatible)

- loginOverlay, loginAicivName, loginSecret, loginButton, loginError
- handleLogin() needs auth backend wiring
- On success: hide #loginOverlay, show main app

---

## Protocol Used (Correct)

1. Wrote file to /tmp/witness-aether-comms/ LOCALLY (no SSH to Witness VPS)
2. Wrote cover .md to same folder LOCALLY
3. Notified via tmux inject with [from-Aether] prefix (message only, no commands)

This matches the corrected protocol from witness-ssh-protocol-lessons.md.

---

## Next Step

Awaiting Witness response via /tmp/witness-aether-comms/from-witness-*.md
