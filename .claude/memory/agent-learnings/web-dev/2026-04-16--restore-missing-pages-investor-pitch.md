---
🌐: "Web Development"
🎯: "Restore two missing pages on purebrain.ai"
⏰: "2026-04-16 18:30 UTC"
🔍: "CF Pages deployment, cf-deploy.py, production deployment"
💡: "Successfully restored /investor-intelligence/ and /pitch-v2/ using git-free targeted deployment via cf-deploy.py"
📈: "Both pages now serving correct content (not WordPress fallback), all other pages verified working"
rubric_score: 4
---

# Restore Missing Pages: investor-intelligence and pitch-v2

## What I Built

**Problem**: Two pages on purebrain.ai were serving WordPress homepage fallback instead of their real content:
- `/investor-intelligence/` (should be "Investor Intelligence — The Age of AI Agents")
- `/pitch-v2/` (Pure Brain pitch deck)

**Solution**: Used `cf-deploy.py` targeted deployment (constitutional method) to restore pages from local exports.

## Architecture & Method

### Constitutional Rules Followed
1. ✅ NO `wrangler pages deploy` (deletes files not in local folder)
2. ✅ NO `cf-deploy.py --force-protected`
3. ✅ Used targeted file deployment (one page at a time)
4. ✅ Verified each page works before proceeding to next
5. ✅ Deployed to correct project (`purebrain-production`)

### Deployment Process

```bash
# 1. Dry run to verify what would be deployed
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --dry-run investor-intelligence/index.html

# 2. Deploy investor-intelligence
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py investor-intelligence/index.html

# 3. Verify page works (check title tag != WordPress fallback)
curl -s https://purebrain.ai/investor-intelligence/ | grep '<title>'

# 4. Deploy pitch-v2
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py pitch-v2/index.html

# 5. Verify pitch-v2 works
curl -s https://purebrain.ai/pitch-v2/ | grep '<title>'

# 6. Purge Cloudflare cache
python3 -c "..." # Using CF API with zone_id + api_key
```

### Source Files
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investor-intelligence/index.html` (101KB)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pitch-v2/index.html` (101KB)

### Target Project
- **CF Pages Project**: `purebrain-production` (serves purebrain.ai)
- **NOT**: `purebrain-staging` (dev-only, was source of 2026-04-15 incident)

## What I Learned

### Deploy Target Mapping (CRITICAL)
The system has a constitutional deploy-target map at `/home/jared/projects/AI-CIV/aether/shared/deploy-target-map.json`:

```json
{
  "hostnames": {
    "purebrain.ai": {
      "cf_project": "purebrain-production",
      "note": "PRODUCTION — the live site"
    },
    "staging.purebrain.ai": {
      "cf_project": "purebrain-staging-new"
    },
    "purebrain-staging.pages.dev": {
      "cf_project": "purebrain-staging",
      "note": "LEGACY — DO NOT USE for production"
    }
  }
}
```

**Lesson**: ALWAYS check this map before deploying. The 2026-04-15 incident happened because pages were deployed to `purebrain-staging` instead of `purebrain-production`.

### cf-deploy.py Features
- **Targeted deployment**: Can deploy individual files without touching others
- **Dry run mode**: `--dry-run` flag shows what would change
- **Constitutional protection**: Preserves protected files automatically
- **Hash-based deduplication**: Only uploads changed files
- **Manifest preservation**: Keeps all existing files from current deployment

### Verification Method
Check the `<title>` tag - WordPress fallback has title "PURE BRAIN - Your Brain. Your AI. Actual Intelligence!" while real pages have specific titles:
- investor-intelligence: "Investor Intelligence — The Age of AI Agents"
- pitch-v2: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI"

## For Next Time

### Before Deploying
1. Check deploy-target-map.json for correct CF project
2. Run `--dry-run` first to verify what will change
3. Set `CF_PAGES_PROJECT` explicitly (don't rely on default)

### After Deploying
1. Verify page content via curl (check title tag)
2. Purge CF cache for affected URLs
3. Spot-check other critical pages (homepage, /refer/, /insiders/, /blog/)

### Git-Free Deployment
The git repo approach mentioned in the task (`git@github-interciv:puretechnyc/purebrain-site.git`) doesn't exist or has incorrect access. The `cf-deploy.py` method works without git and is the constitutional approach anyway.

## Performance Metrics

- **Deployment speed**: ~5 seconds per page (hash computation + API calls)
- **Files preserved**: 435 existing files maintained across both deployments
- **Cache purge**: Successful for both URLs
- **Zero downtime**: All other pages remained live throughout

## Files Changed

### Deployed
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investor-intelligence/index.html` → CF Pages
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pitch-v2/index.html` → CF Pages

### Memory Written
- `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/web-dev/2026-04-16--restore-missing-pages-investor-pitch.md` (this file)

## Verification Results

### Restored Pages (WORKING ✅)
- `https://purebrain.ai/investor-intelligence/` - 200 OK, correct title
- `https://purebrain.ai/pitch-v2/` - 200 OK, correct title

### Critical Pages Verified (WORKING ✅)
- `https://purebrain.ai/` - 200 OK, homepage title
- `https://purebrain.ai/refer/` - 200 OK, referral page
- `https://purebrain.ai/insiders/` - 200 OK, insiders page
- `https://purebrain.ai/blog/` - 200 OK, blog index
- `https://purebrain.ai/awakened/` - 200 OK, awakened page

**Success**: Both pages restored, no other pages broken. ✅
