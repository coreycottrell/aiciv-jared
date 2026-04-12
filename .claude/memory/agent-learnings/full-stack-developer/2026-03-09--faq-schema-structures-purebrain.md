# FAQ Schema Injection — Structure Map for purebrain.ai + jareddsanborn.com

**Date**: 2026-03-09
**Task**: Task 2 from CTO blog fix plan
**Outcome**: 13/13 posts injected with FAQPage JSON-LD schema

---

## Four FAQ Structures in Use Across the Sites

### Structure 1: .pb-faq-item (newer posts)
Used in: PB 1189, 1139, 1084; JDS 1220, 1195
```html
<div class="pb-faq-item">
  <p class="pb-faq-q">Question text</p>
  <p class="pb-faq-a">Answer text</p>
</div>
```
Parser: `FAQHTMLParser` in original inject_faq_schema.py handles this correctly.

### Structure 2: button.faq-question (post 1245, JDS 1222 — "The AI That Forgets You")
```html
<div class="faq-item" style="...">
  <button class="faq-question" onclick="...">Question text <span class="faq-toggle">+</span></button>
  <div class="faq-answer" style="display:none;">Answer text</div>
</div>
```
Parser needed: regex matching `<button class="faq-question">...</button>` then `<div class="faq-answer">...</div>`.
Key gotcha: The `<span class="faq-toggle">` inside the button gets included in naive text extraction. Strip all tags.

### Structure 3: Strong Q:/A: paragraphs after h2 (966, 950, JDS 1210, 1207, 1216)
```html
<h2>FAQ</h2>  (or "Frequently Asked Questions")
<p><strong>Q: Question text</strong></p>
<p>A: Answer text</p>
<!-- OR (JDS 1216 — no Q: prefix) -->
<p><strong>Question text</strong></p>
<p>Answer text (no A: prefix)</p>
```
Parser needed: find h2 with FAQ/Frequently Asked text, extract everything until next h2, find `<p>` with `<strong>` child (question), pair with next `<p>` (answer), strip Q:/A: prefixes.

### Structure 4: p.faq-question class (JDS 1212 — "Stop Treating Your AI Like an Intern")
```html
<div class="faq-item">
  <p class="faq-question">Question text</p>
  <p>Answer text</p>
</div>
```
Parser needed: find `.faq-item` divs, extract `<p class="faq-question">` (question) and first plain `<p>` (answer).

---

## Critical Gotcha: Ordering of Parsers Matters

The multi-parser approach tried `strong-qa-after-h2` before `button-faq-question` for posts 1245/1222. This was wrong because post 1245 has an ROI table earlier in content that contains `<strong>` + `<p>` pairs that matched the pattern, producing garbage schema with the ROI table row as the "question".

**Fix**: Always try the most specific/structural parsers first (button-faq-item, pb-faq-item) before falling back to heuristic ones (strong-qa-after-h2).

**Correct order**:
1. button.faq-question + div.faq-answer
2. .pb-faq-item / p.faq-question class
3. bare strong Q:/A: paragraphs after FAQ h2 (most ambiguous, try last)

---

## urllib vs requests for WordPress App Passwords

App passwords contain spaces (e.g., `41w3 xWWZ 11em UXgj hjAF sx2T`). `urllib.request` with Basic Auth encoding handles these fine for the auth header, but there were HTTP 403 errors in testing. Using `requests` library with `auth=(user, pass)` tuple is more reliable — it handles encoding correctly.

---

## Schema Injection Placement

Prefer: before `</article>` tag (cleanest placement, after all content)
Fallback: before `<!-- /wp:html -->` comment
Last resort: append to end of content

When replacing a bad schema, remove old `<script type="application/ld+json">...</script>` blocks first before injecting new one.

---

## Verification Protocol

After injection, re-fetch post via REST API and:
1. Confirm `"FAQPage"` string is present in `content.raw`
2. Parse the schema JSON and count `mainEntity` array length
3. Confirm count matches expected FAQ pair count
