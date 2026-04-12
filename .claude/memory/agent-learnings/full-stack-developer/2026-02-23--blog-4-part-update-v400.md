# Blog 4-Part Update — Plugin v4.0.0

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer

---

## What Was Built

### Task 1: Uniform READ MORE Button

- Plugin v4.0.0 section `n) BLOG LISTING READ MORE BUTTON`
- Two-part implementation: CSS in `wp_head`, JS in `wp_footer` (priority 5)
- JS scans `.wp-block-latest-posts__list-item` elements — if no `.wp-block-latest-posts__read-more` or `.pb-read-more-btn` or `a[class*="read-more"]`, injects a button
- Gets post URL from the first `<a>` in the card (the title link)
- Inserts button after `.wp-block-latest-posts__post-excerpt` (or appends to card if no excerpt)
- Also runs `setTimeout(fn, 800)` to catch Elementor re-renders
- PERMANENT RULE: All blog post cards must have READ MORE

### Task 2: posts_per_page Cap

- `pre_get_posts` filter: `is_page(319) && !$query->is_main_query()` → set to 10
- Server-side backstop — the `wp:latest-posts` block already sets `postsToShow:10`

### Task 3: Neural Feed Memories Archive Page

- Created as new WordPress page via REST API: `POST /wp-json/wp/v2/pages`
- ID: 700, slug: `blog-neural-feed-memories`, template: `elementor_canvas`
- Full custom HTML/CSS/JS — dynamic grid that fetches all posts via REST API on page load
- JavaScript: `fetch('/wp-json/wp/v2/posts?per_page=100')` — automatically shows new posts
- Grid: 3-col default, 4-col on 1200px+, 2-col on tablet, 1-col mobile
- Card anatomy: 16:9 featured image (lazy), date, Oswald title, excerpt 180chars, orange READ MORE CTA

### Task 4: Memories Link on Blog Page 319

- REST API: `GET /wp-json/wp/v2/pages/319?context=edit` → extract raw content
- Insert `nfm-archive-link-row` div AFTER `.social-links` closing `</div>`
- Pattern: `'    </div>\n</div>\n\n<div class="neural-divider">'`
- Replacement: insert new HTML before the outer `</div>` that closes the header section

## Key Technical Learnings

### WP Plugin Editor via Playwright
- `deploy_plugin_v393_purebrain.py` is the reference pattern
- CodeMirror `.setValue(content)` works reliably — check returned value contains version markers
- GoDaddy SSO toggle: `.wpaas-sso-login-toggle` — click it to reveal standard username/password form
- Success indicator: "File edited successfully" in page body text
- Fallback: check CodeMirror `.getValue()` contains version string if success text unclear

### REST API Pattern for Page Content Injection
- Always use `context=edit` to get `raw` content (not `rendered` HTML)
- Find insertion point with a unique surrounding pattern
- Replace with `str.replace(pattern, new_string, 1)` — the count=1 prevents multiple replacements
- Verify the change: `new_content == raw_content` means pattern not found

### Archive Page Pattern (Dynamic REST API Grid)
- Best approach for archive pages: pure client-side JS + REST API
- Avoid static embedding of posts — it goes stale as new posts are published
- `fetch(wpBase + '/posts?per_page=100&orderby=date&order=desc')` gets all posts
- Featured images: need a second fetch per post to `/wp-json/wp/v2/media/{id}` for sized URLs
- Use `Promise.all(imagePromises)` to fetch all images in parallel

### Insertion Point for Below-Social-Icons Link
- Blog page 319 raw content structure (line ~667):
  ```
      </div>     <!-- closes .social-links -->
  </div>         <!-- closes outer header container -->

  <div class="neural-divider">
  ```
- Search pattern: `'    </div>\n</div>\n\n<div class="neural-divider">'`
- Insert new content between `</div>` (social links) and `</div>` (outer header)
