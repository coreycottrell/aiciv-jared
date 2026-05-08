# Signup Feature — Ready for Deploy

**Date**: 2026-04-16 sprint
**Author**: Chy
**Bundle**: worker-v1.1-p2-signup.js + frontend-with-signup.html

## WORKER CHANGE
New endpoint: **POST /api/signup**
- Fields: email, password (12+ chars), name, team_name (optional)
- Creates team + user atomically (D1 batch)
- Role = 'owner', billing_tier = 'free'
- Returns session token (same pattern as login) + next_steps array
- Rate limit: 10 signups / hour / IP (anti-abuse)
- Duplicate email → 409

## FRONTEND CHANGE
- Auth gate now has login + signup views (toggle via "Create one →" / "Sign in →" links)
- Signup form: name, email, team name (optional), password
- 12-char password minimum enforced client + server
- Enter key submits active form
- On success: same bootApp() flow as login

## DEPLOY ORDER
1. `wrangler deploy` (no migration needed — uses existing users + teams tables)
2. Test: POST https://social-api.in0v8.workers.dev/api/signup with {name,email,password,team_name} — expect 201 + token
3. Visit social.purebrain.ai, click "Create one →", sign up as a new user
4. Verify bootApp shows empty-state onboarding

## REMAINING
- Welcome email on signup (nobody's scoped yet)
- Account connection flow wizard (next sprint item)
- Approval UI polish (next sprint item)
