# Social Platform Security Audit -- 2026-04-16

**Type**: operational + teaching
**Topic**: Full security audit of social.purebrain.ai + ContentRouter + PureSurf BaaS

## Key Findings

- 2 Critical, 3 High, 4 Medium, 3 Low issues found
- C1: D1 stores credentials as plaintext despite column names suggesting encryption
- C2: BaaS server has NO session ownership enforcement -- any API key holder can hijack any other user's browser session (navigate, evaluate JS, screenshot, type)
- H1: No rate limiting on /api/login
- H2: ContentRouter fetches arbitrary media_url with no SSRF protection
- H3: baas_keys.json is world-readable (644) with predictable key names
- CORS policy correctly restricts to purebrain.ai origin (PASSED)
- .env and .credentials are properly git-ignored (PASSED)
- systemd service has good hardening (NoNewPrivileges, ProtectSystem, ProtectHome) (PASSED)

## Patterns Learned

1. **CF Worker source access gap**: social-api worker deployed from Chy's side, not available locally. Need cross-team source sharing for full audit coverage.
2. **BaaS session isolation is an easy miss**: Auth middleware checks API key but never compares user identity to session ownership. Classic IDOR pattern at the session level.
3. **SSRF via media_url in content pipelines**: Any system that fetches user-provided URLs needs URL validation + internal IP blocking. ContentRouter downloads from media_url with zero checks.
4. **baas_keys.json predictable naming**: Keys like `{name}-baas-key-001` are guessable. Cryptographic randomness needed.
5. **File permissions drift**: Even when .credentials/ dir is 700, individual files can be 644 if created without explicit umask. Always verify per-file.

## Files Audited

- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` (1,066 lines)
- `/home/jared/projects/AI-CIV/aether/tools/browser-manager/baas_server.py`
- `/home/jared/projects/AI-CIV/aether/.credentials/` (13 files)
- `/home/jared/projects/AI-CIV/aether/.env`
- `/etc/systemd/system/aether-content-router.service`
- Live endpoints: social.purebrain.ai (black-box)

## Output

Report: `/home/jared/exports/portal-files/security-audit-social-platform-2026-04-16.md`
