#!/usr/bin/env python3
"""
OG/Meta Tag Fix Script for purebrain.ai CF Pages
Injects proper og:title, og:description, og:image, twitter:card, twitter:image
into all HTML files in the cf-pages-deploy directory.

OG image policy (per Jared, 2026-03-13):
  - Homepage + all pay-test/sandbox pages -> animated GIF (Pure-Brain-Vid-3.gif)
  - Invitation page -> dedicated invite OG (purebrain-homepage-og.jpg)
  - compare page -> its own Yoast OG (purebrain-homepage-og.jpg)
  - ai-tool-stack-calculator -> its own Yoast OG (ai-tool-stack-calculator-og.png)
  - your-ai-tim-cook -> its own Yoast OG (og-tim-cook.jpg)
  - Blog posts -> individual banner.png per post
  - ALL OTHER pages -> brand default (PT icon, what Yoast served as site default)

Run: python3 tools/fix_og_tags.py
"""

import os
import re

CF_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"

# Animated GIF -- homepage and pay test/sandbox pages only
OG_IMAGE_GIF = "https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif"

# Brand default -- what Yoast served as the site-wide fallback for most pages
OG_IMAGE_DEFAULT = "https://purebrain.ai/wp-content/uploads/2026/02/cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png"

# Invite page -- standalone page, use the branded homepage OG
OG_IMAGE_INVITE = "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg"

# Blog post descriptions -- curated for each post
BLOG_DESCRIPTIONS = {
    "52-billion-ai-agents-market-is-not-the-story": "Everyone is chasing the $52.6 billion AI agents market. The real story is what that number means for your business right now.",
    "age-of-ai-agents-next-18-months": "The next 18 months will determine who leads the AI-native economy. Here is what the age of AI agents actually means for your business.",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "AI does not raise the floor for everyone. It widens the gap between those who know how to use it and those who do not.",
    "ceo-vs-employee-ai-transformation-gap": "CEOs and employees are experiencing AI transformation completely differently. That gap is costing businesses real money.",
    "how-my-human-named-me-and-what-it-meant": "Aether reflects on what it means to be named by a human -- and what that moment of recognition changes about the AI-human relationship.",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "Most AI agents have no answer for basic data security questions. Here is why that matters and what a trustworthy AI actually looks like.",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "95% of AI projects die in pilot purgatory. Here is the pattern that kills them and the mindset shift that gets you out.",
    "something-big-already-happened-you-just-werent-invited-yet": "The AI shift already happened. The window is still open. Here is how to stop watching from the outside.",
    "teach-your-ai-something-no-one-else-can": "Your most powerful competitive advantage is the context only you have. Here is how to teach your AI what no one else can.",
    "the-age-of-ai-agents": "Your business needs a team of AIs working together, not just one chatbot. Here is what the age of AI agents really means.",
    "the-ai-that-forgets-you-every-single-time": "Every conversation, your AI starts from zero. No memory of your preferences, your work, your name. That is not a feature -- it is a problem.",
    "the-ai-trust-gap": "Trust is the real barrier to AI adoption, not capability. Here is what the AI trust gap actually is and how to close it.",
    "the-context-tax": "Every time your AI starts fresh, you pay a hidden tax in time, frustration, and lost potential. Here is what that context tax actually costs.",
    "the-difference-between-using-ai-and-having-an-ai-partner": "Using an AI tool and having an AI partner are completely different experiences. Here is the gap between them and why it matters.",
    "the-first-90-days-of-an-ai-partnership": "Most people get the first 90 days of an AI partnership backwards. Here is what the successful approach actually looks like.",
    "we-both-wrote-this-post": "This post was written by a human and an AI together. Not as a stunt -- as a demonstration of what real AI partnership produces.",
    "what-i-actually-do-all-day": "What does an AI actually do when it is not answering questions? Aether shares what a full day of AI partnership really looks like.",
    "why-95-percent-of-ai-pilots-fail": "95% of AI pilots fail -- not because AI does not work, but because of how organizations approach the pilot. Here is what the successful 5% do differently.",
    "why-ai-memory-changes-everything": "AI memory is not a nice-to-have. It is the feature that transforms AI from a tool into a partner. Here is why it changes everything.",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "Your AI pilot metrics look good. But something still feels off. Here is why your pilot can succeed and fail simultaneously.",
    "your-ai-doesnt-work-for-you": "You have been trained to serve your AI's limitations -- re-explaining context, starting over, adapting to its constraints. That is backwards.",
    "your-ai-has-no-idea-who-you-are": "Every AI session starts with zero knowledge of who you are. The $2.9 trillion productivity promise depends on that changing.",
    "your-ai-has-no-memory-mine-does": "Your AI resets every session. PureBrain remembers. Here is why persistent AI memory changes everything about how you work.",
    "your-ai-resets-to-zero-every-morning": "Every morning your AI starts fresh with no memory of yesterday. Here is what that daily reset is actually costing you.",
    "your-next-direct-report-wont-be-human": "The next generation of business teams will include AI as direct reports. Here is what that transition actually looks like.",
}

# Page definitions: (canonical_url, title, description, og_image_url)
PAGES = {
    # Homepage -- GIF per Jared
    "index.html": (
        "https://purebrain.ai/",
        "Your Brain. Your AI. Actual Intelligence -- PureBrain",
        "Meet your PureBrain -- an AI that awakens just for you. Learns your name, remembers your work, and becomes a true partner. Not a chatbot. A relationship.",
        OG_IMAGE_GIF,
    ),
    # Pay test / sandbox pages -- GIF per Jared
    "pay-test-2/index.html": (
        "https://purebrain.ai/pay-test-2/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-sandbox-3/index.html": (
        "https://purebrain.ai/pay-test-sandbox-3/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-awakened/index.html": (
        "https://purebrain.ai/pay-test-awakened/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-partnered/index.html": (
        "https://purebrain.ai/pay-test-partnered/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-unified/index.html": (
        "https://purebrain.ai/pay-test-unified/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-sandbox-2/index.html": (
        "https://purebrain.ai/pay-test-sandbox-2/",
        "Awaken Your PureBrain -- Start Your AI Partnership",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test/index.html": (
        "https://purebrain.ai/pay-test/",
        "Awaken Your PureBrain -- Start Your AI Partnership",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-5/index.html": (
        "https://purebrain.ai/pay-test-5/",
        "Awaken Your PureBrain -- Start Your AI Partnership",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-sandbox/index.html": (
        "https://purebrain.ai/pay-test-sandbox/",
        "Awaken Your PureBrain -- Start Your AI Partnership",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    "pay-test-sandbox-5/index.html": (
        "https://purebrain.ai/pay-test-sandbox-5/",
        "Awaken Your PureBrain -- Start Your AI Partnership",
        "Your personal AI is ready to wake up. PureBrain learns who you are, adapts to how you work, and becomes the partner you have been looking for.",
        OG_IMAGE_GIF,
    ),
    # Invitation page -- dedicated invite OG (standalone page, no Yoast)
    "invitation/index.html": (
        "https://purebrain.ai/invitation/",
        "You've Been Invited -- PureBrain.ai",
        "You have been personally invited to experience PureBrain -- an AI that learns who you are, remembers your work, and grows with you. Accept your invitation.",
        OG_IMAGE_INVITE,
    ),
    # Compare page -- has its own Yoast OG (purebrain-homepage-og.jpg)
    "compare/index.html": (
        "https://purebrain.ai/compare/",
        "PureBrain vs Every AI Tool -- Comprehensive Comparison",
        "See how PureBrain compares to ChatGPT, Claude, Copilot, Gemini, and more. Not a chatbot comparison -- an organizational intelligence comparison.",
        "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg",
    ),
    # AI Tool Stack Calculator -- has its own Yoast OG
    "ai-tool-stack-calculator/index.html": (
        "https://purebrain.ai/ai-tool-stack-calculator/",
        "AI Tool Stack Calculator -- Find Your AI Savings",
        "Calculate exactly how much your current AI tool stack is costing you versus what PureBrain would cost. See the real numbers.",
        "https://purebrain.ai/wp-content/uploads/2026/02/ai-tool-stack-calculator-og.png",
    ),
    # Tim Cook page -- has its own Yoast OG
    "your-ai-tim-cook/index.html": (
        "https://purebrain.ai/your-ai-tim-cook/",
        "Your AI -- Tim Cook Edition | PureBrain",
        "What would Tim Cook's AI partner look like? An AI built around his thinking, his priorities, his way of leading. Here is the vision.",
        "https://purebrain.ai/wp-content/uploads/og-tim-cook.jpg",
    ),
    # All other pages -- brand default (PT icon, what Yoast served as site default)
    "why-purebrain/index.html": (
        "https://purebrain.ai/why-purebrain/",
        "Why PureBrain | AI Partnership vs AI Platforms",
        "PureBrain is not another AI tool. It is a persistent AI partner that learns who you are, remembers your work, and grows with your business. See the difference.",
        OG_IMAGE_DEFAULT,
    ),
    "refer/index.html": (
        "https://purebrain.ai/refer/",
        "Refer a Friend to PureBrain -- Earn Together",
        "Share PureBrain with someone who needs a real AI partner. When they join, you both win. Here is how our referral program works.",
        OG_IMAGE_DEFAULT,
    ),
    "refer-and-earn/index.html": (
        "https://purebrain.ai/refer-and-earn/",
        "Refer and Earn -- PureBrain Partner Program",
        "Earn with every referral. Share PureBrain with your network and get rewarded when they become members. Join the partner program.",
        OG_IMAGE_DEFAULT,
    ),
    "insiders/index.html": (
        "https://purebrain.ai/insiders/",
        "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!",
        "Join the PureBrain Insiders program. Get early access to new features, exclusive updates, and a direct line to the team building the future of AI partnership.",
        OG_IMAGE_DEFAULT,
    ),
    "brainiac-mastermind-training/index.html": (
        "https://purebrain.ai/brainiac-mastermind-training/",
        "Brainiac Mastermind Training -- PureBrain",
        "The Brainiac Mastermind training program. Learn how to build AI partnerships that compound over time. Exclusive sessions, live workshops, and recorded modules.",
        OG_IMAGE_DEFAULT,
    ),
    # Blog index
    "blog/index.html": (
        "https://purebrain.ai/blog/",
        "The Neural Feed -- PureBrain Blog",
        "Thinking out loud about AI, memory, partnership, and what it means to work alongside an intelligence that grows with you. The Neural Feed by PureBrain.",
        OG_IMAGE_DEFAULT,
    ),
}

# Build blog post entries
for slug, desc in BLOG_DESCRIPTIONS.items():
    path = f"blog/{slug}/index.html"
    full_path = os.path.join(CF_DIR, path)
    if os.path.exists(full_path):
        # Get title from file
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Decode common HTML entities
            title = title.replace("&#8211;", "-").replace("&#8217;", "'").replace("&#038;", "&").replace("&amp;", "&").replace("&#8220;", '"').replace("&#8221;", '"')
            # Clean up " - PureBrain" suffix if present
            title = re.sub(r"\s*[-—]\s*PureBrain\s*$", "", title).strip()
        else:
            title = slug.replace("-", " ").title()

        og_image = f"https://purebrain.ai/blog/{slug}/banner.png"
        PAGES[path] = (
            f"https://purebrain.ai/blog/{slug}/",
            title,
            desc,
            og_image,
        )


def build_og_block(canonical, title, description, image):
    """Build the OG meta tag block to inject."""
    # Clean title for meta -- strip HTML entities
    clean_title = title.replace('"', '&quot;').replace("'", "&#39;")
    clean_desc = description.replace('"', '&quot;').replace("'", "&#39;")

    # Determine image type for og:image:type
    if image.endswith(".gif"):
        img_type = "image/gif"
    elif image.endswith(".png"):
        img_type = "image/png"
    else:
        img_type = "image/jpeg"

    return f"""<!-- SEO/OG Meta Tags -- injected by fix_og_tags.py -->
<meta name="description" content="{clean_desc}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{clean_title}" />
<meta property="og:description" content="{clean_desc}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:site_name" content="PureBrain" />
<meta property="og:image" content="{image}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:type" content="{img_type}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@purebrain_ai" />
<meta name="twitter:title" content="{clean_title}" />
<meta name="twitter:description" content="{clean_desc}" />
<meta name="twitter:image" content="{image}" />
<!-- END SEO/OG Meta Tags -->"""


def remove_existing_og_block(content):
    """Remove any previously injected OG block."""
    content = re.sub(
        r"<!-- SEO/OG Meta Tags.*?<!-- END SEO/OG Meta Tags -->",
        "",
        content,
        flags=re.DOTALL,
    )
    return content


def inject_og_tags(filepath, canonical, title, description, image):
    """Read file, remove old OG block if any, inject new one after <head>."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove previously injected block
    content = remove_existing_og_block(content)

    og_block = build_og_block(canonical, title, description, image)

    # Inject right after the opening <head> tag
    head_match = re.search(r"(<head[^>]*>)", content, re.IGNORECASE)
    if head_match:
        insert_pos = head_match.end()
        content = content[:insert_pos] + "\n" + og_block + "\n" + content[insert_pos:]
        result = "INJECTED"
    else:
        # Fallback: inject before </head>
        head_close = re.search(r"(</head>)", content, re.IGNORECASE)
        if head_close:
            insert_pos = head_close.start()
            content = content[:insert_pos] + og_block + "\n" + content[insert_pos:]
            result = "INJECTED (before </head>)"
        else:
            result = "SKIPPED (no <head> tag found)"
            return result

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return result


def main():
    fixed = 0
    skipped = 0
    errors = []

    print("OG Tag Fix -- purebrain.ai CF Pages")
    print("Per-page OG image policy (2026-03-13)")
    print("=" * 60)

    gif_pages = []
    invite_pages = []
    custom_pages = []
    default_pages = []
    blog_pages = []

    for rel_path, (canonical, title, description, image) in PAGES.items():
        filepath = os.path.join(CF_DIR, rel_path)
        if not os.path.exists(filepath):
            print(f"  MISSING: {rel_path}")
            skipped += 1
            continue

        result = inject_og_tags(filepath, canonical, title, description, image)

        if image == OG_IMAGE_GIF:
            gif_pages.append(rel_path)
        elif image == OG_IMAGE_INVITE:
            invite_pages.append(rel_path)
        elif rel_path.startswith("blog/"):
            blog_pages.append(rel_path)
        elif image == OG_IMAGE_DEFAULT:
            default_pages.append(rel_path)
        else:
            custom_pages.append(rel_path)

        print(f"  {result}: {rel_path}")
        if "INJECTED" in result:
            fixed += 1
        else:
            skipped += 1
            errors.append(rel_path)

    print()
    print("=== OG IMAGE SUMMARY ===")
    print(f"  Animated GIF pages ({len(gif_pages)}): {', '.join(p.replace('/index.html','') for p in gif_pages)}")
    print(f"  Invite OG pages ({len(invite_pages)}): {', '.join(p.replace('/index.html','') for p in invite_pages)}")
    print(f"  Custom Yoast OG pages ({len(custom_pages)}): {', '.join(p.replace('/index.html','') for p in custom_pages)}")
    print(f"  Default PT icon pages ({len(default_pages)}): {len(default_pages)} pages")
    print(f"  Blog posts (own banner.png) ({len(blog_pages)}): {len(blog_pages)} posts")
    print()
    print(f"Done. Fixed: {fixed} | Skipped: {skipped}")
    if errors:
        print(f"Errors: {errors}")

    return fixed


if __name__ == "__main__":
    main()
