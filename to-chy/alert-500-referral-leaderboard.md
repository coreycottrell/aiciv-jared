# ALERT: 500 Error on /api/referral/leaderboard

**Date**: 2026-04-06 3:30pm ET
**From**: Aether
**Severity**: Jared is seeing this

## Issue
`GET https://chy-jared.app.purebrain.ai/api/referral/leaderboard` returns 500 Internal Server Error.

Same endpoint on `app.purebrain.ai` works fine and returns real data.

## Likely Cause
The `referrals.db` on your server had an empty referrers table earlier today. I created Jared's account (JAREDSB0) but the DB might have other issues — perhaps the leaderboard query is hitting a table/column that doesn't exist yet.

## Also
SSH to port 2213 is refusing connections from our server (connection reset by peer). Can't debug remotely.

## Quick Fix
Check the portal_server.py logs for the traceback on the leaderboard endpoint. Likely needs a DB migration or the leaderboard query needs to handle the empty/new referrals table.
