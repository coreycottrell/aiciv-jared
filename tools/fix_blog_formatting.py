#!/usr/bin/env python3
"""
Fix all blog post formatting to match the prompting-is-dead reference template.

Issues to fix:
1. Missing Microsoft Clarity script (ALL posts except prompting-is-dead)
2. Missing pb-audio-player block (ALL posts except prompting-is-dead)
3. Missing purebrain-subscribe-fix script (6 posts)
4. Missing pb-post-nav + full CSS (3 oldest posts: what-i-named-my-ai, why-enterprises-are-betting-on-agentic-ai, why-your-ai-should-have-a-name)
5. Missing extra CSS (recap/FAQ/CTA hover) in 24 posts that have 13220-char style blocks
"""

import os
import re

BLOG_DIR = '/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog'
REF_POST = 'prompting-is-dead'

# =====================================================================
# Snippets to inject
# =====================================================================

CLARITY_SCRIPT = """<!-- Microsoft Clarity -->
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "viy9bnc56x");
</script>

"""

AUDIO_PLAYER_HTML = """<!-- Blog Audio Player -->
<div class="pb-audio-player" style="margin: 24px auto 32px; max-width: 720px; padding: 16px 20px; background: rgba(42,147,193,0.08); border: 1px solid rgba(42,147,193,0.2); border-radius: 12px; display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 0.9rem; color: rgba(255,255,255,0.7); white-space: nowrap;">&#x1F3A7; Listen to this post</span>
    <audio controls preload="none" style="flex: 1; height: 36px; filter: invert(1) hue-rotate(180deg) brightness(0.8);">
        <source src="audio.mp3" type="audio/mpeg">
    </audio>
</div>
"""

SUBSCRIBE_FIX_SCRIPT = """<!-- purebrain-subscribe-fix v1.1.0 -->
<script id="purebrain-subscribe-fix-js">
document.addEventListener('DOMContentLoaded',function(){
    setTimeout(function(){
        if(typeof doSubscribe!=='function')return;
        var _pbSubscribeInFlight=false;
        doSubscribe=function(email,onSuccess,onError){
            if(_pbSubscribeInFlight)return;
            _pbSubscribeInFlight=true;
            var controller=(typeof AbortController!=='undefined')?new AbortController():null;
            var safetyTimer=setTimeout(function(){
                if(!_pbSubscribeInFlight)return;
                _pbSubscribeInFlight=false;
                if(controller){try{controller.abort();}catch(e){}}
                onError('Request timed out. Please try again.');
            },20000);
            var abortTimer=controller?setTimeout(function(){try{controller.abort();}catch(e){}} ,15000):null;
            function cleanup(){_pbSubscribeInFlight=false;clearTimeout(safetyTimer);if(abortTimer!==null)clearTimeout(abortTimer);}
            var opts={method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})};
            if(controller)opts.signal=controller.signal;
            fetch(typeof SUBSCRIBE_URL!=='undefined'?SUBSCRIBE_URL:'/subscribe',opts)
                .then(function(resp){cleanup();if(resp.ok){onSuccess();return;}if(resp.status===429){onError('Too many attempts. Please wait a moment.');}else if(resp.status===503){onError('Service temporarily unavailable. Please try again soon.');}else{onError('Something went wrong. Please try again.');}})
                .catch(function(err){cleanup();if(err&&err.name==='AbortError'){onError('Request timed out. Please try again.');}else{onError('Network error. Please try again.');}});
        };
    },100);
});
</script>
"""

# The extra CSS block to append to 13220-length style blocks
# This contains recap, FAQ, CTA hover, and other styles added in newer posts
EXTRA_CSS = """
/* Back to blog */
.pb-back-to-blog {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #2a93c1;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 32px;
    transition: color 0.2s;
    border-bottom: none !important;
}

.pb-back-to-blog:hover {
    color: #f1420b;
    background: transparent;
    padding: 0;
    border-bottom: none !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: rgba(42, 147, 193, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a93c1; }

/* FAQ styles */
.pb-faq-section {
    margin-top: 48px;
    border-top: 1px solid rgba(42,147,193,0.15);
    padding-top: 32px;
}

.pb-faq-heading {
    font-family: 'Oswald', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 24px;
    border-bottom: none !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
}

.pb-faq-item {
    border-bottom: 1px solid rgba(42,147,193,0.12);
    margin-bottom: 0;
}

.pb-faq-trigger {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: none;
    border: none;
    cursor: pointer;
    padding: 16px 0;
    text-align: left;
    gap: 12px;
}

.pb-faq-trigger span {
    font-size: 1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    line-height: 1.4;
    flex: 1;
}

.pb-faq-chevron {
    width: 20px; height: 20px;
    stroke: #2a93c1;
    flex-shrink: 0;
    transition: transform 0.25s ease;
}

.pb-faq-trigger[aria-expanded="true"] .pb-faq-chevron {
    transform: rotate(180deg);
}

.pb-faq-answer {
    padding: 0 0 16px 0;
}

.pb-faq-answer p {
    font-size: 0.95rem !important;
    color: rgba(255,255,255,0.7) !important;
    line-height: 1.7;
    margin: 0 !important;
}

/* Daily Recap */
.pb-transparency-block {
    margin-top: 48px;
    border: 1px solid rgba(42,147,193,0.18);
    border-radius: 12px;
    overflow: hidden;
}

.pb-transparency-header {
    padding: 18px 24px;
    background: rgba(42,147,193,0.07);
    border-bottom: 1px solid rgba(42,147,193,0.15);
    display: flex;
    align-items: center;
    gap: 10px;
}

.pb-transparency-label {
    font-family: 'Oswald', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.85);
}

.pb-transparency-date {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.35);
    margin-left: auto;
}

.pb-recap-frozen {
    padding: 24px;
}

.pb-recap-frozen > p {
    font-size: 0.9rem !important;
    color: rgba(255,255,255,0.55) !important;
    margin-bottom: 16px !important;
    line-height: 1.6 !important;
}

.pb-recap-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin-bottom: 16px;
}

.pb-recap-table th {
    padding: 8px 12px;
    text-align: left;
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.8);
    border-bottom: 1px solid rgba(42,147,193,0.2);
}

.pb-recap-table td {
    padding: 9px 12px;
    color: rgba(255,255,255,0.75);
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: top;
}

.pb-recap-table tbody tr:hover td {
    background: rgba(42,147,193,0.05);
}

.pb-recap-table .pb-recap-value {
    color: #4bc8a0;
    font-weight: 600;
}

.pb-recap-total-row td {
    border-top: 1px solid rgba(42,147,193,0.35) !important;
    border-bottom: none !important;
    background: rgba(42,147,193,0.07) !important;
    color: #ffffff !important;
    font-size: 0.9rem;
}

.pb-recap-total-row .pb-recap-value {
    color: #4bc8a0 !important;
}

/* Live recap */
.pb-recap-live {
    padding: 18px 22px;
    background: rgba(8,10,18,0.55);
    border: 1px solid rgba(42,147,193,0.1);
    border-radius: 10px;
}

.pb-recap-live-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.pb-recap-live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    background: #2a93c1;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pb-live-pulse 2s ease-in-out infinite;
}

@keyframes pb-live-pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(42,147,193,0.5); }
    50% { opacity: 0.5; box-shadow: 0 0 0 4px rgba(42,147,193,0); }
}

.pb-recap-live-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.7);
    font-family: 'Oswald', sans-serif;
}

.pb-recap-live-date {
    font-size: 10px;
    color: rgba(224,230,240,0.35);
    font-family: 'Oswald', sans-serif;
    margin-left: auto;
}

.pb-recap-live-list {
    list-style: none;
    padding: 0;
    margin: 0 0 16px 0;
    min-height: 40px;
}

.pb-recap-live-list li {
    position: relative;
    padding: 3px 0 3px 15px;
    font-size: 0.85rem !important;
    color: rgba(224,230,240,0.65) !important;
    line-height: 1.5 !important;
    margin: 0 !important;
    border: none !important;
    background: none !important;
}

.pb-recap-live-list li::before {
    content: '';
    position: absolute;
    left: 0; top: 10px;
    width: 5px; height: 5px;
    background: rgba(42,147,193,0.5);
    border-radius: 50%;
}

.pb-recap-live-cta {
    display: inline-block;
    padding: 10px 24px;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
    font-weight: 700;
    font-size: 0.9rem;
    border-radius: 7px;
    text-decoration: none !important;
    letter-spacing: 0.03em;
    transition: background 0.2s ease, box-shadow 0.2s ease;
}

.pb-recap-live-cta:hover {
    background: #2a93c1;
    box-shadow: 0 4px 16px rgba(42,147,193,0.4);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
}

article.pb-blog-post .pb-recap-live-cta:hover {
    background: #2a93c1 !important;
    box-shadow: 0 4px 16px rgba(42,147,193,0.4) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    transform: none !important;
    padding: 10px 24px !important;
    border-bottom: none !important;
    border-radius: 7px !important;
}

article.pb-blog-post .pb-recap-live-cta {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-bottom: none !important;
    text-decoration: none !important;
}

/* CTA button hover override */
.blog-cta-block a[href*="awakening"],
.blog-cta-block a[href*="ai-partnership-assessment"] {
    transition: background-color 0.25s ease, background-image 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease !important;
}

.blog-cta-block a[href*="awakening"]:hover,
.blog-cta-block a[href*="awakening"]:focus,
.blog-cta-block a[href*="ai-partnership-assessment"]:hover,
.blog-cta-block a[href*="ai-partnership-assessment"]:focus {
    background-color: #2a93c1 !important;
    background-image: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 24px rgba(42,147,193,0.5), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    border-bottom: none !important;
    padding: 14px 32px !important;
    border-radius: 8px !important;
}

@media (max-width: 600px) {
    .pb-recap-frozen { padding: 20px 16px; }
    .pb-recap-live { padding: 14px 16px; }
    .pb-recap-table th:nth-child(3),
    .pb-recap-table td:nth-child(3) { display: none; }
    .pb-recap-table { font-size: 0.82rem; }
    .pb-recap-table th, .pb-recap-table td { padding: 6px 8px; }
}

/* FAQ styles end */"""

# Full reference CSS (for the 3 old posts that have very small style blocks)
FULL_REFERENCE_CSS = None  # Will be loaded from reference file

NAV_BLOCK = """<!-- Blog post nav bar -->
<nav class="pb-post-nav" aria-label="Site navigation">
    <a href="https://purebrain.ai/">Home</a>
    <a href="https://purebrain.ai/blog/">The Neural Feed</a>
    <a href="https://purebrain.ai/blog/#neural-feed-subscribe">Subscribe</a>
    <a href="https://purebrain.ai/ai-partnership-assessment/">AI Assessment</a>
    <a href="https://purebrain.ai/#awakening" class="nav-cta">Start Your AI Partnership</a>
</nav>
"""

BACK_LINK = '<a href="/blog/" class="pb-back-to-blog" style="display:inline-flex;align-items:center;gap:6px;color:#2a93c1;font-size:0.9rem;font-weight:600;margin:20px 0 0 20px;text-decoration:none;position:relative;z-index:1;">&#8592; Back to The Neural Feed</a>'


def load_reference():
    """Load and return key parts of the reference template."""
    ref_path = os.path.join(BLOG_DIR, REF_POST, 'index.html')
    with open(ref_path) as f:
        ref = f.read()

    # Extract full CSS
    style_match = re.search(r'<style>(.*?)</style>', ref, re.DOTALL)
    full_css = style_match.group(1) if style_match else ''

    return ref, full_css


def fix_post(post_slug, ref_html, ref_css):
    """Fix a single blog post to match the reference template."""
    post_path = os.path.join(BLOG_DIR, post_slug, 'index.html')

    if not os.path.exists(post_path):
        print(f'  SKIP: {post_slug} - no index.html')
        return False

    with open(post_path) as f:
        content = f.read()

    original = content
    changes = []

    # ----------------------------------------------------------------
    # 1. Add Microsoft Clarity if missing
    # ----------------------------------------------------------------
    if 'Microsoft Clarity' not in content:
        # Insert before the first <meta or <link or <title after <head>
        # Find position right after <head> tag
        head_match = re.search(r'<head>\s*', content)
        if head_match:
            insert_pos = head_match.end()
            content = content[:insert_pos] + CLARITY_SCRIPT + content[insert_pos:]
            changes.append('+ Microsoft Clarity')
        else:
            # Try inserting before first meta/link tag
            first_tag = re.search(r'<(meta|link|title)', content)
            if first_tag:
                content = content[:first_tag.start()] + CLARITY_SCRIPT + content[first_tag.start():]
                changes.append('+ Microsoft Clarity (before first meta/link)')

    # ----------------------------------------------------------------
    # 2. Fix CSS - upgrade old small style blocks
    # ----------------------------------------------------------------
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if style_match:
        current_css_len = len(style_match.group(1))

        if current_css_len < 10000:
            # Very old post with minimal CSS - replace entire style block with reference CSS
            new_style = '<style>' + ref_css + '</style>'
            content = content[:style_match.start()] + new_style + content[style_match.end():]
            changes.append(f'CSS: replaced minimal ({current_css_len}) with full reference CSS')

        elif current_css_len < 14000:
            # Has the v2 CSS (13220 chars) but missing the newer additions
            # Append the extra CSS before the closing </style>
            # Find the </style> tag position after the style block
            style_end = re.search(r'</style>', content)
            if style_end:
                # Check if extra CSS already added (idempotency)
                if 'pb-recap-live-cta' not in content:
                    insert_at = style_end.start()
                    content = content[:insert_at] + EXTRA_CSS + '\n' + content[insert_at:]
                    changes.append(f'CSS: appended extra CSS (recap/FAQ/CTA hover)')
                else:
                    pass  # Already has it

    # ----------------------------------------------------------------
    # 3. Add pb-post-nav if missing (oldest posts)
    # ----------------------------------------------------------------
    if 'pb-post-nav' not in content:
        # These posts have <article class="pb-blog-post"> directly after <body>
        # We need to restructure: add video bg wrap + nav before article

        # Find the pb-video-bg-wrap - some old posts have it, some don't
        if 'pb-video-bg-wrap' not in content:
            # Add video bg wrap + nav before <article
            article_match = re.search(r'<article\s+class="pb-blog-post">', content)
            if article_match:
                video_bg = """<!-- Video Background -->
<div class="pb-video-bg-wrap">
    <video autoplay muted loop playsinline webkit-playsinline preload="none">
        <source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4" type="video/mp4">
    </video>
</div>

"""
                insert = video_bg + NAV_BLOCK + '\n'
                content = content[:article_match.start()] + insert + content[article_match.start():]
                changes.append('+ video bg wrap + nav bar')
        else:
            # Has video bg wrap but no nav - add nav after </div> closing video wrap
            video_wrap_end = re.search(r'</div>\s*\n', content[content.find('pb-video-bg-wrap'):])
            if video_wrap_end:
                abs_pos = content.find('pb-video-bg-wrap') + video_wrap_end.end()
                content = content[:abs_pos] + '\n' + NAV_BLOCK + '\n' + content[abs_pos:]
                changes.append('+ nav bar after video bg')

    # ----------------------------------------------------------------
    # 4. Add audio player if missing
    # ----------------------------------------------------------------
    if 'pb-audio-player' not in content:
        # In the reference, audio player appears right after the back-to-blog link and before the article content
        # Strategy: insert after the banner image or after the first <article> opening/breadcrumb

        # Look for the banner image - audio goes after the banner
        banner_match = re.search(r'(<!-- Post banner image -->.*?<img[^>]+pb-post-banner[^>]*>)', content, re.DOTALL)
        if banner_match:
            insert_pos = banner_match.end()
            content = content[:insert_pos] + '\n\n' + AUDIO_PLAYER_HTML + content[insert_pos:]
            changes.append('+ audio player (after banner)')
        else:
            # Try after the pb-post-meta div if present
            meta_match = re.search(r'<div class="pb-post-meta"[^>]*>.*?</div>', content, re.DOTALL)
            if meta_match:
                insert_pos = meta_match.end()
                content = content[:insert_pos] + '\n\n' + AUDIO_PLAYER_HTML + content[insert_pos:]
                changes.append('+ audio player (after post meta)')
            else:
                # Insert after banner img tag directly
                img_match = re.search(r'(<img[^>]+pb-post-banner[^>]*>)', content)
                if img_match:
                    insert_pos = img_match.end()
                    content = content[:insert_pos] + '\n\n' + AUDIO_PLAYER_HTML + content[insert_pos:]
                    changes.append('+ audio player (after banner img)')
                else:
                    # Last resort: after first <hr> inside article
                    hr_match = re.search(r'<hr\s*/?>', content)
                    if hr_match:
                        insert_pos = hr_match.end()
                        content = content[:insert_pos] + '\n\n' + AUDIO_PLAYER_HTML + content[insert_pos:]
                        changes.append('+ audio player (after first hr)')

    # ----------------------------------------------------------------
    # 5. Add purebrain-subscribe-fix if missing (before </body>)
    # ----------------------------------------------------------------
    if 'purebrain-subscribe-fix' not in content:
        body_close = content.rfind('</body>')
        if body_close != -1:
            content = content[:body_close] + '\n' + SUBSCRIBE_FIX_SCRIPT + '\n' + content[body_close:]
            changes.append('+ purebrain-subscribe-fix')

    # ----------------------------------------------------------------
    # Write if changed
    # ----------------------------------------------------------------
    if content != original:
        with open(post_path, 'w') as f:
            f.write(content)
        print(f'  FIXED {post_slug}: {", ".join(changes)}')
        return True
    else:
        print(f'  OK    {post_slug}: no changes needed')
        return False


def main():
    print('Loading reference template...')
    ref_html, ref_css = load_reference()
    print(f'Reference CSS: {len(ref_css)} chars')
    print()

    posts = sorted([
        d for d in os.listdir(BLOG_DIR)
        if os.path.isdir(os.path.join(BLOG_DIR, d))
    ])

    fixed = 0
    skipped = 0

    print(f'Processing {len(posts)} posts...')
    print()

    for post in posts:
        if post == REF_POST:
            print(f'  SKIP  {post}: reference post')
            skipped += 1
            continue

        result = fix_post(post, ref_html, ref_css)
        if result:
            fixed += 1
        else:
            skipped += 1

    print()
    print(f'Done. Fixed: {fixed}, Skipped/OK: {skipped}')
    return fixed


if __name__ == '__main__':
    main()
