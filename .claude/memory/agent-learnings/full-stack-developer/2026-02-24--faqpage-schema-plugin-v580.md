# FAQPage JSON-LD Schema — Plugin v5.8.0

**Date**: 2026-02-24
**Type**: teaching + operational
**Topic**: Auto-injecting FAQPage structured data from the plugin (AEO/GEO gap fix)

---

## Problem

SEO audit identified FAQPage schema as the biggest AEO/GEO gap. 9 of 10 blog posts
with FAQ sections had JSON-LD schema (manually injected in post content in session 2026-02-20).
Post 879 was missing schema entirely — its FAQ used a different structure (pb-faq-item)
that the manual injection never covered.

Also: future blog posts would not get schema automatically.

## Solution: PHP Server-Side Schema Injection

Added hook `j-schema` to the plugin (wp_footer priority 14) that:
1. Checks `is_single()` (only runs on single blog posts)
2. Gets the post content via `get_post()->post_content`
3. **Skips posts that already have FAQPage schema** in saved content (backward compat)
4. Parses the content with PHP DOMDocument + DOMXPath
5. Extracts Q&A pairs from all 4 FAQ structures
6. Outputs `<script type="application/ld+json">` FAQPage JSON-LD in wp_footer

## Four FAQ Structures Handled

| Structure | Selector | Posts |
|-----------|----------|-------|
| A: `.faq-section > h3 + p` | XPath class contains | 565, 480, 381, 316, 373, 172, 98 |
| B: `.pb-faq-item > .pb-faq-q + .pb-faq-a` | XPath class contains | 879 (and future) |
| C: `<details><summary>Q</summary>A</details>` | native HTML5 | 631 |
| D: bare `<h3>Q</h3><p>A</p>` after `<h2>FAQ</h2>` | sibling walk | 606 |

## Backward Compatibility

Posts whose `post_content` already contains `"FAQPage"` string → plugin returns early.
Result: those 9 posts keep their manually-added schema, no duplication.
Post 879: no existing schema → plugin injects auto-generated one.

## Technical Notes

### DOMDocument UTF-8 Handling
```php
$dom->loadHTML( '<?xml encoding="UTF-8">' . $wrapped );
```
The `<?xml encoding="UTF-8">` prefix tells DOMDocument the encoding upfront
so it doesn't mangle curly quotes or em-dashes.

### XPath Class Contains Pattern
```php
'//*[contains(concat(" ", normalize-space(@class), " "), " faq-section ")]'
```
Standard XPath 1.0 pattern for checking class membership (no contains() shortcut in XPath 1.0).

### wp_json_encode flags
```php
wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT )
```
- `JSON_UNESCAPED_UNICODE`: keeps non-ASCII characters as UTF-8 (not \uXXXX)
- `JSON_UNESCAPED_SLASHES`: avoids ugly `\/` in URLs
- `JSON_PRETTY_PRINT`: readable output for debugging

Note: WordPress may still HTML-encode some characters (e.g. curly quotes become `&ldquo;`)
in the HTML output. This is fine — Google's structured data parser handles HTML entities.

### Structure B Dedup
Post 879 has BOTH faq-section CSS classes (in its `<style>` block inside the post)
AND pb-faq-item divs. Structure A would match the CSS `.faq-section` text in the style
block if not careful. The XPath query correctly targets elements with the class, not
text containing the string, so this is not an issue.

## Verification Results

- Post 879 (was missing schema): NOW has auto-generated FAQPage schema with 5 Q&A pairs
- Post 565 (had manual schema): Manual schema preserved, no auto-generated duplicate
- Schema count in post 879 HTML: 1 (correct)
- Auto-generated comment marker present in post 879: YES

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
  - Version: `5.7.0` → `5.8.0`
  - Added: `j-schema) FAQPage JSON-LD SCHEMA` section (~150 lines PHP)
  - Added: v5.8.0 changelog entries
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v580_purebrain.py` (new deploy script)

## Key Teaching: PHP vs JS for Structured Data

Use PHP server-side for JSON-LD schema, NOT client-side JavaScript.
Reason: Google's structured data crawler may not execute JavaScript.
Server-side PHP in wp_footer guarantees the schema is in the HTML source.

## Key Teaching: Backward Compat Pattern

When adding automatic schema injection to a plugin, always check if schema
already exists in the post content first. This prevents:
1. Duplicate schema (confuses search engines)
2. Schema conflicts (two different FAQPage blocks)
3. Breaking existing optimized schema

Pattern:
```php
if ( strpos( $raw_content, '"FAQPage"' ) !== false ) {
    return; // already has schema — skip
}
```
