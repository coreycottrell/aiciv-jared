#!/usr/bin/env python3
"""
Fix AI Partnership Guide page (ID 405) by injecting JavaScript that applies
functional changes on top of Elementor's cached rendered output.

Changes:
1. Replace 5 [LINK:] placeholders with real styled blog post links
2. Fix "Meet Your AI Partner" CTA → purebrain.ai/#awakening
3. Fix "Take the Assessment" CTA → /ai-partnership-assessment/
4. Fix "Subscribe Free" CTA → /blog/ (will be updated to real subscribe link later)
5. Make FAQ items collapsible accordion
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_URL = "https://purebrain.ai/wp-json/wp/v2"
WP_USER = "Aether"
WP_PASS = os.getenv("PUREBRAIN_WP_APP_PASSWORD")
PAGE_ID = 405

# The JavaScript patch that will run after Elementor renders
JS_PATCH = """
<script>
(function() {
  'use strict';

  function applyGuideFixes() {
    var body = document.body;
    if (!body) return;
    var html = body.innerHTML;
    var changed = false;

    // === 1. REPLACE [LINK:] PLACEHOLDERS ===
    var linkMap = {
      '[LINK: "Most AI Agents Break" blog post]': '<a href="https://purebrain.ai/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/" style="color:#2a93c1;text-decoration:underline;font-weight:600;">Most AI Agents Break the Moment You Ask Where the Data Goes</a>',
      '[LINK: "Why AI Memory Changes Everything" blog post]': '<a href="https://purebrain.ai/why-ai-memory-changes-everything/" style="color:#2a93c1;text-decoration:underline;font-weight:600;">Why AI Memory Changes Everything</a>',
      '[LINK: "CEO vs Employee AI Lens" blog post]': '<a href="https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/" style="color:#2a93c1;text-decoration:underline;font-weight:600;">Your CEO Sees AI Differently Than Your Team Does</a>',
      '[LINK: Data Governance and AI Memory blog post]': '<a href="https://purebrain.ai/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/" style="color:#2a93c1;text-decoration:underline;font-weight:600;">Data Governance and AI Memory</a>',
      '[LINK: AI Partnership Readiness Self-Assessment -- Lead Magnet]': '<a href="https://purebrain.ai/ai-partnership-assessment/" style="display:inline-block;padding:12px 28px;background:linear-gradient(135deg,#f1420b,#d13608);color:#fff!important;font-weight:700;border-radius:8px;text-decoration:none;font-size:1rem;">Take the AI Partnership Readiness Assessment &rarr;</a>'
    };

    for (var placeholder in linkMap) {
      if (html.indexOf(placeholder) !== -1) {
        html = html.split(placeholder).join(linkMap[placeholder]);
        changed = true;
      }
    }

    if (changed) {
      body.innerHTML = html;
    }

    // === 2. FIX CTA BUTTONS ===
    var allLinks = document.querySelectorAll('a');
    allLinks.forEach(function(a) {
      var text = (a.textContent || '').trim();

      // Meet Your AI Partner → #awakening
      if (text === 'Meet Your AI Partner') {
        a.href = 'https://purebrain.ai/?utm_source=pillar_page&utm_medium=cta&utm_campaign=ai_partnership#awakening';
      }

      // Take the Assessment → assessment page
      if (text === 'Take the Assessment') {
        a.href = 'https://purebrain.ai/ai-partnership-assessment/?utm_source=pillar_page&utm_medium=cta&utm_campaign=assessment';
      }

      // Subscribe Free → blog page
      if (text === 'Subscribe Free') {
        a.href = 'https://purebrain.ai/blog/?utm_source=pillar_page&utm_medium=cta&utm_campaign=newsletter';
      }
    });

    // === 3. FAQ ACCORDION ===
    var faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length > 0) {
      // Add accordion styles
      var style = document.createElement('style');
      style.textContent = [
        '.faq-item { border-bottom: 1px solid rgba(42,147,193,0.2); margin-bottom: 0; }',
        '.faq-item h3 { cursor: pointer; padding: 18px 40px 18px 0; margin: 0; position: relative; transition: color 0.3s; }',
        '.faq-item h3:hover { color: #2a93c1; }',
        '.faq-item h3::after { content: "+"; position: absolute; right: 0; top: 50%; transform: translateY(-50%); font-size: 24px; font-weight: 300; color: #2a93c1; transition: transform 0.3s; }',
        '.faq-item h3.faq-open::after { content: "\\2212"; }',
        '.faq-item .faq-answer { max-height: 0; overflow: hidden; transition: max-height 0.4s ease, padding 0.4s ease; padding: 0 0; }',
        '.faq-item .faq-answer.faq-visible { max-height: 600px; padding: 0 0 18px 0; }'
      ].join(' ');
      document.head.appendChild(style);

      faqItems.forEach(function(item) {
        var h3 = item.querySelector('h3');
        var answerDiv = item.querySelector('[itemprop="acceptedAnswer"]');
        if (!h3 || !answerDiv) return;

        // Wrap answer in collapsible container
        answerDiv.classList.add('faq-answer');

        // Click handler
        h3.addEventListener('click', function() {
          var isOpen = h3.classList.contains('faq-open');

          // Close all others
          document.querySelectorAll('.faq-item h3.faq-open').forEach(function(openH3) {
            openH3.classList.remove('faq-open');
            var openAnswer = openH3.parentElement.querySelector('.faq-answer');
            if (openAnswer) openAnswer.classList.remove('faq-visible');
          });

          // Toggle this one
          if (!isOpen) {
            h3.classList.add('faq-open');
            answerDiv.classList.add('faq-visible');
          }
        });
      });
    }
  }

  // Run after DOM is ready and Elementor has rendered
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(applyGuideFixes, 500);
    });
  } else {
    setTimeout(applyGuideFixes, 500);
  }
})();
</script>
"""

def main():
    auth = (WP_USER, WP_PASS)

    # 1. Get current page content
    print("Fetching guide page (ID 405)...")
    resp = requests.get(f"{WP_URL}/pages/{PAGE_ID}", auth=auth, params={"context": "edit"})
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch page: {resp.status_code}")
        sys.exit(1)

    page = resp.json()
    content_raw = page['content']['raw']
    elementor_mode = page.get('meta', {}).get('_elementor_edit_mode', '')

    print(f"  Content length: {len(content_raw)}")
    print(f"  Elementor mode: {elementor_mode}")

    # 2. Check if JS patch already exists
    if 'applyGuideFixes' in content_raw:
        print("  JS patch already present - removing old version first")
        # Remove old patch
        import re
        content_raw = re.sub(r'<script>\s*\(function\(\)\s*\{\s*\'use strict\'.*?applyGuideFixes.*?</script>', '', content_raw, flags=re.DOTALL)

    # 3. Append JS patch to content.raw
    # Elementor renders from _elementor_data, but WordPress also outputs content.raw
    # We add the script to content.raw so it executes alongside Elementor's output
    new_content = content_raw.rstrip() + "\n\n" + JS_PATCH.strip() + "\n"

    print(f"  New content length: {len(new_content)}")

    # 4. Update page
    print("Updating page with JS patch...")
    update_resp = requests.post(
        f"{WP_URL}/pages/{PAGE_ID}",
        auth=auth,
        json={
            "content": new_content
        }
    )

    if update_resp.status_code == 200:
        print("SUCCESS: JS patch injected into guide page content")
        print("\nThe patch will:")
        print("  1. Replace 5 [LINK:] placeholders with real blog post links")
        print("  2. Fix 'Meet Your AI Partner' → purebrain.ai/#awakening")
        print("  3. Fix 'Take the Assessment' → /ai-partnership-assessment/")
        print("  4. Fix 'Subscribe Free' → /blog/")
        print("  5. Make FAQ section collapsible accordion")
        print("\nNOTE: Changes may require CDN cache flush to appear live")
    else:
        print(f"ERROR: Update failed: {update_resp.status_code}")
        print(update_resp.text[:500])

if __name__ == "__main__":
    main()
