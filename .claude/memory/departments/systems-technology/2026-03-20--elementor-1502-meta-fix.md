# Elementor #1502 Meta Tag Fix — Homepage + Insiders

**Date**: 2026-03-20
**Type**: operational, teaching
**Topic**: CF Pages HTML meta tag surgery — Elementor draft page leaking into social share tags

## Problem

Homepage and Insiders CF Pages exports had broken social sharing because WordPress exported metadata from Elementor draft page #1502 into the outer WP head section. Twitter/LinkedIn/iMessage showed "Elementor #1502" as the page title.

## Root Cause

WP shell rendered in context of Elementor page 1502 (draft/template). Yoast emitted schema + canonical for page 1502. Correct meta tags existed inside the Elementor widget (nested HTML-in-HTML) but social crawlers only read outer <head>.

## What Was Fixed

### Homepage
- Removed oEmbed link (elementor-1502)
- Removed elementor-post-1502-css link
- Removed shortlink ?p=1502
- Fixed both duplicate twitter:title tags
- Cleaned body class (page-id-1502, elementor-page-1502)

### Insiders
- Fixed Yoast canonical, og:title, og:url (elementor-1502 -> insiders/)
- Fixed both twitter:title tags
- Fixed entire Yoast JSON-LD schema block (all elementor-1502 URLs + names)
- Fixed breadcrumb name: "Elementor #1502" -> "PureBrain Insiders"
- Removed both oEmbed links (JSON + XML)
- Removed elementor-post-1502-css
- Removed shortlink ?p=1502
- Removed wp-json/wp/v2/pages/1502 alternate link

## Pattern: Social Crawlers Only Read <head>

Twitter/LinkedIn/iMessage only parse meta tags in <head>. Nested HTML-in-HTML inside Elementor widgets is invisible. Wrong social title = look in outer head first.

## Fix Method

Python string replacements — handles JSON schema block isolation cleanly.

## Verification
- Remaining 'Elementor #1502': 0 (both files)
- Remaining page-id-1502: 0
- Deploy: https://8ea082b6.purebrain-staging.pages.dev

Tags: meta-tags, social-sharing, elementor, og-title, twitter-title, canonical, yoast, cf-pages
