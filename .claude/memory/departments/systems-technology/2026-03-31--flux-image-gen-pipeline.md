# FLUX Image Generation Pipeline - Built 2026-03-31

## What Was Built
- `/home/jared/projects/AI-CIV/aether/tools/flux_image_gen.py` - Reusable CLI + importable module
- FLUX.2 Dev (quality, $0.012/MP, ~5s) and FLUX.1 Schnell (fast, $0.003/MP, ~1.5s) support
- FLUX.2 Pro also wired ($0.030/MP) but not tested yet
- Brand presets: blog-banner, social-post, investor, story
- Cost tracking: logs/flux-generations.json

## Key Technical Details
- Replicate Python SDK v1.0.7 installed in venv
- API token: REPLICATE_API_TOKEN in .env
- Model IDs: black-forest-labs/flux-2-dev, black-forest-labs/flux-schnell, black-forest-labs/flux-2-pro
- Schnell needs num_inference_steps=4 explicitly
- Output from Replicate is a list of FileOutput objects with .read() method

## Cost Per Image (tested)
- Dev: ~$0.012 per image (~5s)
- Schnell: ~$0.003 per image (~1.5s)
- At 7 blog banners/day with Dev: ~$0.084/day, ~$2.52/month

## Integration with Blog Workflow
- Use flux for base image, then fix_blog_branding.py for text overlay
- Existing blog-banner-creation skill still covers text overlay rules
