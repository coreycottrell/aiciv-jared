#!/usr/bin/env node
/**
 * Unit tests for parseBlogIndex.
 *
 * Run: node workers/blog-publish-hook/tests/parser.test.mjs
 *
 * No external test runner — keeps the harness portable for CF Worker context
 * which can't easily run vitest/jest at BUILD time without a bundler.
 */

import { parseBlogIndex } from "../src/worker.js";

let pass = 0, fail = 0;

function assertEq(actual, expected, label) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (ok) { pass += 1; console.log(`  PASS  ${label}`); }
  else    { fail += 1; console.log(`  FAIL  ${label}\n    expected: ${JSON.stringify(expected)}\n    actual:   ${JSON.stringify(actual)}`); }
}

function assert(cond, label) {
  if (cond) { pass += 1; console.log(`  PASS  ${label}`); }
  else      { fail += 1; console.log(`  FAIL  ${label}`); }
}

// ---- Fixture: shape of the live purebrain.ai/blog/ index (Apr 2026) --------
const FIXTURE_HTML = `
<html><body><ul class="wp-block-latest-posts__list">
  <li><div class="wp-block-latest-posts__featured-image"><img src="..." /></div>
    <a class="wp-block-latest-posts__post-title" href="/blog/the-compound-intelligence-effect-why-month-6-matters-more-t/">The Compound Intelligence Effect: Why Month 6 Matters More Than Month 1</a><time datetime="2026-04-30T10:00:00+00:00" class="wp-block-latest-posts__post-date">April 30, 2026</time>
    <div class="wp-block-latest-posts__post-excerpt">Excerpt here.</div></li>
  <li><div class="wp-block-latest-posts__featured-image"><img src="..." /></div>
    <a class="wp-block-latest-posts__post-title" href="/blog/the-3-am-test-what-happens-when-your-ai-runs-unsupervised/">The 3 AM Test: What Happens When Your AI Runs Unsupervised</a><time datetime="2026-04-26T10:00:00+00:00" class="wp-block-latest-posts__post-date">April 26, 2026</time>
    <div class="wp-block-latest-posts__post-excerpt">Excerpt.</div></li>
  <li>
    <a class="wp-block-latest-posts__post-title" href="/blog/your-customers-will-tell-you-everything/">Your Customers Will Tell You Everything &amp; Beyond</a><time datetime="2026-04-15T21:00:00+00:00" class="wp-block-latest-posts__post-date">April 15, 2026</time>
  </li>
</ul></body></html>
`;

// ---- Tests -----------------------------------------------------------------
console.log("parser.test.mjs");

const parsed = parseBlogIndex(FIXTURE_HTML);

assertEq(parsed.length, 3, "extracts 3 posts from fixture");

assertEq(
  parsed[0].slug,
  "the-compound-intelligence-effect-why-month-6-matters-more-t",
  "first post slug"
);
assertEq(parsed[0].published_at, "2026-04-30T10:00:00+00:00", "first post ISO datetime");
assertEq(parsed[0].url, "https://purebrain.ai/blog/the-compound-intelligence-effect-why-month-6-matters-more-t/", "first post URL");
assert(parsed[0].title.startsWith("The Compound Intelligence"), "first post title prefix");

// HTML entity decoding
assert(parsed[2].title.includes("&"), "decodes &amp; to &");
assert(!parsed[2].title.includes("&amp;"), "no remaining &amp; in title");

// Tolerance: empty input returns [] not throws
assertEq(parseBlogIndex("").length, 0, "empty html returns []");
assertEq(parseBlogIndex("<html>no posts here</html>").length, 0, "no-match html returns []");

// Dedupe within page (same slug appears twice)
const dupHtml = FIXTURE_HTML + `
  <a class="wp-block-latest-posts__post-title" href="/blog/the-3-am-test-what-happens-when-your-ai-runs-unsupervised/">3 AM Test (duplicate)</a><time datetime="2026-04-26T10:00:00+00:00" class="wp-block-latest-posts__post-date">April 26, 2026</time>
`;
assertEq(parseBlogIndex(dupHtml).length, 3, "dedupes repeated slug within single fetch");

// ISO comparison sanity (used by A5 backfill rule)
const a = "2026-04-30T10:00:00+00:00";
const b = "2026-05-02T00:00:00.000Z";
assert(a < b, "ISO 8601 strings compare lexicographically (A5 rule depends on this)");

// Slug pattern: must be lowercase alphanumeric with hyphens
const badSlug = `<a class="wp-block-latest-posts__post-title" href="/blog/Bad_Slug/">Bad</a><time datetime="2026-01-01T00:00:00Z" class="wp-block-latest-posts__post-date">Jan 1</time>`;
assertEq(parseBlogIndex(badSlug).length, 0, "rejects underscored/uppercase slugs (regex guard)");

// ---- Summary ---------------------------------------------------------------
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
