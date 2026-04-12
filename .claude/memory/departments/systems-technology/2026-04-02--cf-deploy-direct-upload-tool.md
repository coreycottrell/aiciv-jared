# CF Pages Direct File Deploy Tool

**Date**: 2026-04-02
**Type**: teaching
**Agent**: dept-systems-technology

## What Was Built

A Python tool (`tools/cf-deploy.py`) that uploads specific files directly to Cloudflare Pages via the API, preserving all existing files from the current deployment. This solves the problem of Aether and Chy overwriting each other's deployments.

## Key Technical Discoveries

### CF Pages File Hashing Algorithm
Wrangler uses blake3 to hash files. The exact algorithm is:
```
blake3(base64encode(file_contents) + file_extension_without_dot).hex()[:32]
```
Example: For `robots.txt`, it computes `blake3(base64(content) + "txt")` and takes first 32 hex chars.

### CF Pages Direct Upload API Flow
1. `GET /accounts/{acct}/pages/projects/{proj}/deployments?per_page=1` - get latest deployment
2. `GET /accounts/{acct}/pages/projects/{proj}/deployments/{id}` - get deployment details including `files` dict (manifest: path -> hash)
3. `GET /accounts/{acct}/pages/projects/{proj}/upload-token` - get JWT for uploads
4. `POST /pages/assets/check-missing` with `{"hashes": [...]}` - find which files need uploading
5. `POST /pages/assets/upload` with `[{"key": hash, "value": base64, "metadata": {"contentType": mime}, "base64": true}]`
6. `POST /pages/assets/upsert-hashes` with `{"hashes": [...]}` - confirm all hashes
7. `POST /accounts/{acct}/pages/projects/{proj}/deployments` as multipart with `manifest` field = JSON of `{"/path": "hash"}`

### Authentication
- API Key + Email auth works: `X-Auth-Email` + `X-Auth-Key` headers
- Bearer token auth did NOT work with CF_PAGES_TOKEN or CF_API_TOKEN
- Upload JWT from step 3 is used for steps 4-6 only

### Account Discovery
- purebrain-staging project is under account `d526a3e9498dd167509003004df03290` (In0v8 account)
- NOT under `19bb52a20bc7fc1b34036fea91f6860c` (Jared's account) which is what CF_ACCOUNT_ID in .env points to

## Files Created
- `/home/jared/projects/AI-CIV/aether/tools/cf-deploy.py` - Main tool (Aether)
- `/home/jared/projects/AI-CIV/aether/tools/cf-deploy.sh` - Shell wrapper
- `/home/jared/projects/AI-CIV/aether/tools/cf-read.sh` - Read file from live site
- `/home/jared/projects/AI-CIV/aether/tools/cf-list.sh` - List files from manifest
- `/home/jared/projects/AI-CIV/aether/tools/cf-deploy-portable.py` - Self-contained version for Chy
- `/home/aiciv/tools/cf-deploy.py` on Chy's server (37.27.237.109)
- `/home/aiciv/tools/.env` on Chy's server (CF credentials)

## Dependency
- Python package `blake3` required (`pip3 install blake3`)
