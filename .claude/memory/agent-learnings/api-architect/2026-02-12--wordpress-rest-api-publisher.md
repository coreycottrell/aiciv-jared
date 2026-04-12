# WordPress REST API Publisher Implementation

**Date**: 2026-02-12
**Agent**: api-architect
**Type**: pattern
**Topic**: WordPress REST API integration for blog publishing

---

## Context

Built a WordPress REST API publisher tool for jaredsanborn.com to enable programmatic blog post publishing. This integrates with the existing content pipeline.

## Key Patterns Learned

### 1. WordPress Authentication

WordPress REST API uses Basic Auth with Application Passwords:

```python
# Credentials format
credentials = f"{username}:{app_password}"
encoded = base64.b64encode(credentials.encode()).decode()
header = f"Basic {encoded}"
```

**Important**: Application passwords CAN have spaces (they're valid per WordPress spec). Don't strip them.

### 2. API Endpoints Structure

| Resource | Endpoint | Methods |
|----------|----------|---------|
| Posts | `/wp-json/wp/v2/posts` | GET, POST |
| Media | `/wp-json/wp/v2/media` | GET, POST |
| Categories | `/wp-json/wp/v2/categories` | GET |
| Tags | `/wp-json/wp/v2/tags` | GET, POST |
| Users | `/wp-json/wp/v2/users/me` | GET |

### 3. Content Format

WordPress expects HTML content, not Markdown. Need conversion if writing in Markdown.

### 4. Category vs Tag Handling

- **Categories**: Must pre-exist in WordPress (created by admin)
- **Tags**: Can be auto-created via API if they don't exist

```python
# Categories - search only
def _get_category_id_by_name(self, name: str) -> Optional[int]:
    resp = self.client.get(f"{api}/categories", params={"search": name})
    # Return first match

# Tags - search or create
def _get_or_create_tag(self, name: str) -> Optional[int]:
    resp = self.client.get(f"{api}/tags", params={"search": name})
    if not found:
        resp = self.client.post(f"{api}/tags", json={"name": name})
    return resp.json().get("id")
```

### 5. Media Upload Flow

1. Upload media file with proper Content-Type and Content-Disposition headers
2. Get back `media_id`
3. Use `media_id` as `featured_media` when creating post

```python
upload_headers = {
    "Authorization": auth_header,
    "Content-Type": content_type,  # From mimetypes.guess_type()
    "Content-Disposition": f'attachment; filename="{filename}"'
}
```

### 6. Post Status Values

| Status | Visibility |
|--------|------------|
| `draft` | Not visible, editable |
| `publish` | Live and public |
| `pending` | Awaiting review |
| `private` | Admins only |
| `future` | Scheduled |

## Files Created

1. **Tool**: `/home/jared/projects/AI-CIV/aether/tools/wordpress_publisher.py`
   - CLI interface with subcommands
   - `WordPressPublisher` class for programmatic use
   - Context manager support (`with` statement)

2. **Skill**: `/home/jared/projects/AI-CIV/aether/.claude/skills/wordpress-publishing/SKILL.md`
   - Documentation for agents
   - Quick reference commands
   - Integration guidance

## CLI Usage

```bash
# Test connection
python3 tools/wordpress_publisher.py test

# Publish draft
python3 tools/wordpress_publisher.py publish --title "Title" --content "<p>Content</p>" --status draft

# Publish with file
python3 tools/wordpress_publisher.py publish --title "Title" --content-file post.html --status publish

# Upload media
python3 tools/wordpress_publisher.py upload-media --file image.jpg --alt "Description"

# List resources
python3 tools/wordpress_publisher.py list-posts
python3 tools/wordpress_publisher.py list-categories
python3 tools/wordpress_publisher.py list-tags
```

## Integration with Daily Pipeline

This complements the existing workflow:

```
intel-scan -> deep-research -> daily-blog -> verify-publish
                                                  |
                                                  v
                                     wordpress_publisher.py
                                                  |
                                                  v
                                        jaredsanborn.com/blog/
```

## When to Apply

- Publishing Jared's personal blog content
- Cross-posting content to WordPress sites
- Automating content distribution pipeline
- Any WordPress REST API integration

---

**Tags**: wordpress, api, rest-api, publishing, blog, jaredsanborn.com
