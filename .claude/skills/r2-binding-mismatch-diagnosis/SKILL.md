---
status: provisional
tick_count: 0
last_used: 2026-05-19
introduced: 2026-05-19
---
# R2 Binding Mismatch Diagnosis

**Purpose**: Systematic investigation protocol when CF Worker→R2 media serving returns 404 despite objects having been uploaded successfully. Catches the three overlapping failure modes: objects deleted/moved, bucket binding mismatch, and deployed code != git HEAD.

**Source**: 2026-05-19 social.purebrain.ai 107-image 404 incident. Root cause was Chy's rollback binding worker to `purebrain-social-uploads` instead of `purebrain-uploads`.

## When to Use

- Worker-proxied R2 media returns 404 but was previously serving
- Upload success logs exist but objects return "not found"
- After any CF Dashboard deploy or rollback (manual deploys bypass wrangler.toml)

## Investigation Steps

### Step 1: Confirm Objects Exist in EXPECTED Bucket

```bash
# List objects in the bucket wrangler.toml says we bind to
npx wrangler r2 object get <bucket-name>/<key> --pipe > /dev/null 2>&1
echo $?  # 0 = exists, non-zero = missing

# Check BOTH buckets if naming is ambiguous
npx wrangler r2 object head <bucket-a>/<key>
npx wrangler r2 object head <bucket-b>/<key>
```

### Step 2: Check Binding Mismatch (Critical)

Three sources of truth for R2 bindings — they can diverge:

| Source | How to Check |
|--------|-------------|
| `wrangler.toml` | `grep -A3 'r2_buckets' wrangler.toml` |
| Deploy script | `grep 'bucket_name' deploy-*.sh` |
| CF Dashboard | Settings → Variables → R2 Bucket Bindings |
| Deployed code | `curl <worker>/some-media-path` and inspect error shape |

**The deployed binding wins.** If Dashboard shows a different bucket than wrangler.toml, that's your mismatch.

### Step 3: Verify Deployed Code Matches Git HEAD

```bash
# Compare error response shapes
curl -s <worker>/known-missing-key | head -1
# vs
grep -A5 'handleMedia' src/worker.js | grep 'Response'
```

If deployed returns `{"error":"media not found"}` but git HEAD returns `new Response("not found")`, the deployed worker is NOT from git HEAD.

### Step 4: Check R2 Lifecycle Rules

CF Dashboard → R2 → <bucket> → Settings → Lifecycle rules. Auto-delete policies can silently purge objects.

### Step 5: Check CF Account Scope

Workers and R2 buckets can live in different CF accounts. Verify:
- Worker account ID (from `wrangler whoami` or Dashboard URL)
- R2 bucket account ID (from R2 S3 API credentials)

If they differ, the worker cannot access the bucket even with correct binding name.

## Resolution Checklist

- [ ] Identify which bucket actually has the objects
- [ ] Verify deployed binding points to that bucket
- [ ] Redeploy from git if deployed code is stale
- [ ] Fix upload handler return URLs if they reference old R2 public domains
- [ ] Add post-deploy probe: `curl <worker>/known-good-media-key` returns 200

## Gotchas

- CF Dashboard deploys do NOT use wrangler.toml — bindings can diverge silently
- `wrangler deploy` reads wrangler.toml but Dashboard "Edit Code" does not
- R2 public URLs (`pub-*.r2.dev`) are deprecated — always proxy through Worker
- Two CF accounts = two R2 namespaces, even if bucket names are identical
