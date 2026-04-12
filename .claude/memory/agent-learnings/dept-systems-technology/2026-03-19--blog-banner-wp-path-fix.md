# Blog Banner WP Path Fix — 2026-03-19

**Type**: operational
**Topic**: 19 blog posts had broken banner images due to WordPress /wp-content/ absolute paths

## Root Cause

When the site migrated from WordPress to CF Pages, the individual blog post HTML files still
referenced banners via absolute WordPress paths:
  src="/wp-content/uploads/2026/02/some-banner.png"

CF Pages does not serve those paths (no WordPress running), so banners were broken/missing on
individual post pages.

## What Was Fixed

- 19 posts had broken WP banner paths in their index.html
- 12 posts were already correct with ./banner.png or ./banner.jpg relative paths
- All 19 were fixed to use ./banner.xxx (relative path pointing to the local banner file)

## Fix Method

Used Python string replacement (not sed) to precisely target src="/wp-content/..." attribute
and replace with src="./banner.png" or src="./banner.jpg" based on which local file exists.

Key lesson: sed matched the wrong WP reference first (a CSS background-image GIF reference)
before the img src attribute. Python with exact string matching was required.

## Posts Fixed (19)
- ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger
- ceo-vs-employee-ai-transformation-gap
- how-my-human-named-me-and-what-it-meant
- most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2
- pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value
- something-big-already-happened-you-just-werent-invited-yet
- the-age-of-ai-agents
- the-ai-that-forgets-you-every-single-time
- the-ai-trust-gap
- the-difference-between-using-ai-and-having-an-ai-partner
- the-first-90-days-of-an-ai-partnership
- we-both-wrote-this-post
- what-i-actually-do-all-day
- why-95-percent-of-ai-pilots-fail
- why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time
- your-ai-doesnt-work-for-you
- your-ai-has-no-memory-mine-does
- your-ai-resets-to-zero-every-morning
- your-next-direct-report-wont-be-human

## Blog Index / Memories Page

Both the blog index (/blog/index.html) and the memories page
(/blog-neural-feed-memories/index.html) were ALREADY correct - they use /blog/{slug}/banner.xxx
absolute paths which resolve correctly on CF Pages.

## Deployment

Deployed to purebrain-staging CF Pages. 19 files uploaded (matching 19 fixed posts).
CF Pages auto-invalidates CDN cache on deploy.

## Gotcha: Logo WP Ref in Blog Index

Blog index has one WP path left: the header logo image. This is fine. The file actually
exists at wp-content/uploads/2026/02/cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png
in the CF Pages deploy directory. It resolves correctly. Do NOT touch it.
