# Disk Space Cleanup - March 19 2026

**Date**: 2026-03-19
**Type**: operational
**Agent**: dept-systems-technology
**Result**: 93% → 82% used, freed ~4.3GB

## What Was Removed

### System Caches (~1.3GB freed)
- apt package cache: `sudo apt clean` (891 files removed)
- pip cache: `pip cache purge`
- npm cache: `npm cache clean --force`

### WP/WordPress-Era Archives (921MB freed)
- `exports/purebrain-site-repo-2026-03-07.tar.gz` (298M)
- `exports/wp-full-export-2026-03-10.zip` (296M)
- `exports/purebrain-site-media.zip` (289M) - media already in cf-pages-deploy
- `exports/pure-test-sandbox-2.zip` (38M)

### WP/Elementor/Amplify Platform Export Dirs (272MB freed)
- `exports/elementor-footer-edit/` (97M)
- `exports/wp-social-links/` (61M)
- `exports/divi-blog-setup/` (34M)
- `exports/package-sandbox-2/` (42M)

### Video Pipeline Intermediates (633MB freed)
- `tools/video-pipeline/hls-output/` - both portal demo dirs (r2_uploaded=True)
- `tools/video-pipeline/gui/work/hls/` (455M) - intermediate transcode work
- `tools/video-pipeline/gui/work/uploads/` - removed 4 files (R2-done or failed)

### Old Screenshots (131MB freed)
- `tools/screenshots/hover-fix-2026-02-18/` through all Feb 2026 screenshot dirs
- Individual WP nav/cat screenshots

### /tmp Old Files (~183MB freed)
- Two PureResearch.mp4 copies (71M each)
- canva-deck.pdf (41M)
- Various tmp session dirs

### docs/ Old Files (~149MB freed)
- `docs/bypass-test/` (54M) - WP bypass test screenshots
- `docs/from-telegram/Screenshot 2026-02-*.png` (54 files, ~95M)

### Log Rotation
- Truncated `/home/jared/tg_bridge.log` (was 21M)
- git gc --aggressive on aether repo

## What Was Kept (Intentionally)

- `exports/brainiac-training/` - ACTIVE: 2026-03-18 recording not yet uploaded to R2
- `exports/cf-pages-deploy/` - LIVE SITE
- `tools/video-pipeline/gui/work/uploads/` - 2 files not yet R2 uploaded
- `docs/gdrive/` (1.7G) - agent training data
- All .claude/ memory and config
- All payment/conversation logs
- docs/team-files/ and docs/team-dossiers/

## Decision Framework for Future Cleanups

1. WP-era exports: safe once CF Pages migration confirmed
2. Video pipeline: only remove after r2_uploaded=True in jobs.json
3. Screenshots: safe if >30 days old and from WP era
4. Brainiac downloads/hls-work: keep until recordings-index.json confirms R2 upload
5. /tmp: anything >1 week old is fair game
6. docs/from-telegram: screenshots >30 days old safe; keep brand assets/headshots
