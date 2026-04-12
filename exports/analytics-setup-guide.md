# PureBrain.ai Analytics Setup Guide

**Date**: 2026-02-17
**Purpose**: Connect 4 analytics/tracking tools to purebrain.ai

---

## Overview

We're setting up a complete analytics stack:

| Tool | Purpose | What It Tracks |
|------|---------|----------------|
| **Google Analytics 4** | Core analytics | Traffic, conversions, user behavior |
| **Google Search Console** | SEO analytics | Search rankings, indexing, clicks |
| **Google Tag Manager** | Tag management | Central hub for all tracking codes |
| **Microsoft Clarity** | Behavior analytics | Heatmaps, session recordings, rage clicks |

**Recommended Install Order**:
1. Google Tag Manager (container for other tags)
2. Google Analytics (via GTM)
3. Microsoft Clarity (via GTM)
4. Google Search Console (separate - DNS/meta verification)

---

## 1. Google Tag Manager Setup

### What You Need:
- Google account with access to purebrain.ai

### Steps:
1. Go to https://tagmanager.google.com/
2. Create account → Account name: "Pure Technology" or "PureBrain"
3. Create container → Container name: "purebrain.ai" → Target platform: "Web"
4. Accept Terms of Service
5. **Copy the GTM container code** (2 snippets - head and body)

### WordPress Integration:
**Option A - Plugin (Recommended):**
- Install "Site Kit by Google" or "GTM4WP" plugin
- Paste GTM container ID (format: GTM-XXXXXXX)

**Option B - Manual (via Elementor):**
- Paste `<head>` snippet into: Elementor → Settings → Custom Code → Header
- Paste `<body>` snippet into body opening section

### Verify:
- Use Google Tag Assistant Chrome extension
- Should show GTM container firing on all pages

---

## 2. Google Analytics 4 Setup

### What You Need:
- Same Google account as GTM

### Steps:
1. Go to https://analytics.google.com/
2. Create property → Property name: "PureBrain.ai"
3. Business info → Choose relevant options
4. Create Web data stream → URL: purebrain.ai
5. **Copy Measurement ID** (format: G-XXXXXXXXXX)

### Connect via GTM:
1. In GTM → Tags → New
2. Tag type: "Google Analytics: GA4 Configuration"
3. Measurement ID: Paste G-XXXXXXXXXX
4. Trigger: "All Pages"
5. Save → Submit (publish container)

### Key Events to Track:
- Page views (automatic)
- Form submissions
- CTA button clicks
- Scroll depth
- Video plays

---

## 3. Microsoft Clarity Setup

### What You Need:
- Microsoft account (can use existing or create new)

### Steps:
1. Go to https://clarity.microsoft.com/
2. Sign up / Sign in
3. Add new project → Name: "PureBrain.ai" → URL: purebrain.ai
4. **Copy Clarity tracking code** (or just the project ID)

### Connect via GTM:
1. In GTM → Tags → New
2. Tag type: "Custom HTML"
3. Paste Clarity tracking script
4. Trigger: "All Pages"
5. Save → Submit

### What You'll See:
- **Heatmaps**: Where users click, scroll, move
- **Session recordings**: Watch actual user sessions
- **Insights**: Rage clicks, dead clicks, quick backs

---

## 4. Google Search Console Setup

### What You Need:
- Google account
- Ability to add DNS record OR meta tag to site

### Steps:
1. Go to https://search.google.com/search-console/
2. Add property → Choose "URL prefix": https://purebrain.ai
3. Verify ownership via one of:
   - **HTML tag** (easiest) - add meta tag to `<head>`
   - **Domain verification** - add TXT record to DNS
   - **Google Analytics** - if GA already connected
   - **Google Tag Manager** - if GTM already connected

### Recommended Verification:
If GTM is already installed, use "Google Tag Manager" verification method (automatic).

### After Verification:
- Submit sitemap: https://purebrain.ai/sitemap.xml
- Request indexing for key pages
- Monitor search performance

---

## Quick Checklist

### Before We Start:
- [ ] Jared has Google account logged in
- [ ] WordPress admin access confirmed
- [ ] Can install plugins (or edit theme code)

### Setup Order:
1. [ ] Google Tag Manager - container created, code installed
2. [ ] Google Analytics 4 - property created, connected via GTM
3. [ ] Microsoft Clarity - project created, connected via GTM
4. [ ] Google Search Console - property verified

### Verification:
- [ ] GTM showing in Tag Assistant
- [ ] GA4 receiving real-time data
- [ ] Clarity recording sessions
- [ ] Search Console verified and sitemap submitted

---

## What I Can Do vs What You Need To Do

### Aether Can Do:
- Guide you through each step
- Provide exact code snippets
- Install plugins via WordPress admin (browser automation)
- Paste tracking codes into WordPress
- Verify installation is working

### Jared Needs To Do:
- Log into Google accounts (I can't access your Google)
- Create the GTM/GA4/Clarity accounts (requires your auth)
- Copy the tracking IDs and share with me
- DNS verification if needed (GoDaddy access)

---

## Ready to Start?

When CSS updates are done, we'll:
1. Start with GTM - you create the container, share the ID
2. I'll install it in WordPress
3. Then we'll add GA4 and Clarity through GTM
4. Finally Search Console verification

This gives us the full analytics stack to track the UX improvements we're making!
