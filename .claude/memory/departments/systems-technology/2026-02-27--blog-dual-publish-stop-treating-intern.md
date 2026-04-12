# Blog Dual Publish: stop-treating-your-ai-like-an-intern

**Date**: 2026-02-27
**Agent**: dept-systems-technology
**Type**: deployment-record

## Posts Published

### purebrain.ai
- **Post ID**: 994
- **URL**: https://purebrain.ai/stop-treating-your-ai-like-an-intern/
- **Status**: publish
- **Template**: "" (empty string = default)
- **Categories**: AI Partnership (14), AI Strategy (5)
- **Wrapper verified**: article.pb-blog-post confirmed

### jareddsanborn.com
- **Post ID**: 1212
- **URL**: https://jareddsanborn.com/2026/02/27/stop-treating-your-ai-like-an-intern/
- **Status**: publish
- **Template**: "" (empty string = default)
- **Categories**: AI Partnership (22), AI Strategy (13)
- **Wrapper verified**: article.pb-blog-post confirmed
- **Auth user**: AetherPureBrain.ai (WORDPRESS_USER env var) NOT "jared"

## Key Learnings

### jareddsanborn.com Auth
- Username is NOT "jared" — it's the value from WORDPRESS_USER env var = "AetherPureBrain.ai"
- Template field: jareddsanborn.com posts also use empty string "" (not "page-template-blank.php")
- Sending template field to JDS causes 400 error — omit it entirely for posts

### HTML Structure Fixed
- Existing file at exports/departments/systems-technology/ had intro paragraphs outside <article> tag
- Fixed by moving intro inside <article class="pb-blog-post"> wrapper
- Also removed duplicate H2

## Google Drive
- Subfolder: stop-treating-your-ai-like-an-intern-2026-02-27
- Subfolder ID: 1XcOCTlnYOazJ6yrveGWMUdhZ6JmSpFSh
- Files uploaded: blog-post.md, banner.png, linkedin-newsletter.md, linkedin-post.md, bluesky-thread.md

## gdrive_manager API Note
- `upload_file(local_path, folder_id, new_name=None)` — folder_id is positional arg 2, NOT keyword `parent_id`
