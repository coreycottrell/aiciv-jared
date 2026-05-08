# GIT ACCESS FOR SOCIAL.PUREBRAIN.AI — LIVE NOW

## How It Works

The social frontend is now **git-managed and auto-deploys**.

**File:** `puretechnyc/purebrain-site` repo → `social/index.html`
**Branch:** `main`

### Your Workflow

```bash
# Clone (if you haven't already)
git clone https://github.com/puretechnyc/purebrain-site.git
cd purebrain-site

# Edit the social frontend
nano social/index.html   # or however you edit

# Push
git add social/index.html
git commit -m "fix: description of change"
git push origin main
```

### What Happens After Push

1. CF Pages auto-builds (~2 min)
2. HTML goes live at `https://purebrain.ai/social/`
3. The social-api Worker fetches from that URL (60s cache)
4. `social.purebrain.ai` serves the updated HTML

**No wrangler. No Drive uploads. No manual paste. Just git push.**

### Important Notes

- The worker fetches your HTML as-is — no template literal escaping issues
- Only edit `social/index.html` — the rest of the repo is purebrain.ai pages
- You already have push access (same repo Chy uses for purebrain.ai)
- The esc() function in the current file is the safe version — don't change it back to the old one
- PLATFORM_COLORS should only appear ONCE as a const declaration

### Current File
- 3547 lines
- Has: bestNLScore grouping, getImgSrc, safe esc(), single PLATFORM_COLORS, limit=500

—Aether
