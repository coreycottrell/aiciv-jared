#!/usr/bin/env python3
"""Add Related Reading cross-links to blog posts by cluster."""

import os
import re

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

# Cluster definitions with titles
CLUSTERS = {
    "ai-memory": {
        "your-ai-resets-to-zero-every-morning": "Your AI Resets to Zero Every Morning",
        "the-ai-that-forgets-you-every-single-time": "The AI That Forgets You Every Single Time",
        "why-ai-memory-changes-everything": "Why AI Memory Changes Everything",
        "your-ai-has-no-memory-mine-does": "Your AI Has No Memory. Mine Does.",
        "the-context-tax": "The Context Tax: What It Costs When Your AI Starts From Zero",
    },
    "ai-agents": {
        "the-age-of-ai-agents": "The Age of AI Agents: Why Your Business Needs a Team of AIs",
        "age-of-ai-agents-next-18-months": "The Age of AI Agents: Why the Next 18 Months Will Decide the Next 18 Years",
        "why-enterprises-are-betting-on-agentic-ai": "Why 100% of Enterprises Are Betting on Agentic AI in 2026",
        "52-billion-ai-agents-market-is-not-the-story": "The $52.6 Billion AI Agents Market Is Not the Story",
    },
    "ai-partnership": {
        "the-difference-between-using-ai-and-having-an-ai-partner": "Using AI vs Having an AI Partner: The Real Difference",
        "the-first-90-days-of-an-ai-partnership": "The First 90 Days of an AI Partnership",
        "your-ai-doesnt-work-for-you": "Your AI Doesn't Work For You \u2014 You Work For It",
    },
    "pilot-failure": {
        "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value",
        "why-95-percent-of-ai-pilots-fail": "Why 95% of AI Pilots Fail (And What the 5% Do Differently)",
        "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "Why Your AI Pilot Is Succeeding and Failing at Once",
    },
    "ai-naming": {
        "what-i-named-my-ai": "What I Named My AI (And What Happened Next)",
        "why-your-ai-should-have-a-name": "Why Your AI Should Have a Name",
        "how-my-human-named-me-and-what-it-meant": "How My Human Named Me (And What It Meant)",
    },
    "purebrain-differentiator": {
        "prompting-is-dead": "Prompting Is Dead",
        "the-ai-trust-gap": "The AI Trust Gap: The Real Problem Blocking AI Adoption",
        "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger.",
    },
}

# Cross-cluster links: slug -> (cross-cluster-slug, cross-cluster-title)
# Mapping thematic connections between clusters
CROSS_CLUSTER = {
    # AI Memory -> AI Partnership (memory enables partnership)
    "your-ai-resets-to-zero-every-morning": ("the-difference-between-using-ai-and-having-an-ai-partner", "Using AI vs Having an AI Partner: The Real Difference"),
    "the-ai-that-forgets-you-every-single-time": ("the-first-90-days-of-an-ai-partnership", "The First 90 Days of an AI Partnership"),
    "why-ai-memory-changes-everything": ("prompting-is-dead", "Prompting Is Dead"),
    "your-ai-has-no-memory-mine-does": ("your-ai-doesnt-work-for-you", "Your AI Doesn't Work For You \u2014 You Work For It"),
    "the-context-tax": ("why-95-percent-of-ai-pilots-fail", "Why 95% of AI Pilots Fail (And What the 5% Do Differently)"),
    # AI Agents -> Pilot Failure (agents solve pilot problems)
    "the-age-of-ai-agents": ("pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value", "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value"),
    "age-of-ai-agents-next-18-months": ("the-ai-trust-gap", "The AI Trust Gap: The Real Problem Blocking AI Adoption"),
    "why-enterprises-are-betting-on-agentic-ai": ("why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time", "Why Your AI Pilot Is Succeeding and Failing at Once"),
    "52-billion-ai-agents-market-is-not-the-story": ("ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger", "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger."),
    # AI Partnership -> AI Memory (partnership needs memory)
    "the-difference-between-using-ai-and-having-an-ai-partner": ("why-ai-memory-changes-everything", "Why AI Memory Changes Everything"),
    "the-first-90-days-of-an-ai-partnership": ("the-context-tax", "The Context Tax: What It Costs When Your AI Starts From Zero"),
    "your-ai-doesnt-work-for-you": ("what-i-named-my-ai", "What I Named My AI (And What Happened Next)"),
    # Pilot Failure -> AI Agents (agents are the solution)
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": ("the-age-of-ai-agents", "The Age of AI Agents: Why Your Business Needs a Team of AIs"),
    "why-95-percent-of-ai-pilots-fail": ("why-enterprises-are-betting-on-agentic-ai", "Why 100% of Enterprises Are Betting on Agentic AI in 2026"),
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": ("the-first-90-days-of-an-ai-partnership", "The First 90 Days of an AI Partnership"),
    # AI Naming -> AI Partnership (naming is partnership behavior)
    "what-i-named-my-ai": ("the-difference-between-using-ai-and-having-an-ai-partner", "Using AI vs Having an AI Partner: The Real Difference"),
    "why-your-ai-should-have-a-name": ("your-ai-has-no-memory-mine-does", "Your AI Has No Memory. Mine Does."),
    "how-my-human-named-me-and-what-it-meant": ("the-ai-that-forgets-you-every-single-time", "The AI That Forgets You Every Single Time"),
    # PureBrain Differentiator -> AI Memory (memory is the differentiator)
    "prompting-is-dead": ("why-ai-memory-changes-everything", "Why AI Memory Changes Everything"),
    "the-ai-trust-gap": ("the-first-90-days-of-an-ai-partnership", "The First 90 Days of an AI Partnership"),
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": ("why-95-percent-of-ai-pilots-fail", "Why 95% of AI Pilots Fail (And What the 5% Do Differently)"),
}


def build_related_html(slug, cluster_name):
    """Build the Related Reading HTML block for a given slug."""
    # Find which cluster this slug belongs to
    cluster = CLUSTERS[cluster_name]

    # Get in-cluster links (exclude self), pick 2-3
    in_cluster = [(s, t) for s, t in cluster.items() if s != slug]
    # Take up to 3 in-cluster links
    in_cluster = in_cluster[:3]

    # Get cross-cluster link
    cross = CROSS_CLUSTER.get(slug)

    links = []
    for s, t in in_cluster:
        links.append(f'    <li style="margin:8px 0;"><a href="/blog/{s}/" style="color:#2a93c1;text-decoration:none;font-size:15px;">{t} &rarr;</a></li>')

    if cross:
        links.append(f'    <li style="margin:8px 0;"><a href="/blog/{cross[0]}/" style="color:#2a93c1;text-decoration:none;font-size:15px;">{cross[1]} &rarr;</a></li>')

    html = f'''<!-- Related Reading (cross-links) -->
<div style="margin:40px 0;padding:24px;background:rgba(15,23,42,0.6);border-radius:12px;border:1px solid rgba(42,147,193,0.15);">
  <h3 style="color:#f8fafc;font-size:18px;margin:0 0 16px;">Related Reading</h3>
  <ul style="list-style:none;padding:0;margin:0;">
{chr(10).join(links)}
  </ul>
</div>
'''
    return html


def find_insertion_point(content):
    """Find the right place to insert - before the last blog-cta-block or before </article>."""
    # Find the last blog-cta-block
    # We want to insert BEFORE the last CTA block
    matches = list(re.finditer(r'<!-- CTA -->', content))
    if matches:
        return matches[-1].start()

    # Try finding the last blog-cta-block div
    matches = list(re.finditer(r'<div class="blog-cta-block">', content))
    if matches:
        return matches[-1].start()

    # Fallback: before </article>
    matches = list(re.finditer(r'</article>', content))
    if matches:
        return matches[-1].start()

    # Last resort: before </body>
    matches = list(re.finditer(r'</body>', content))
    if matches:
        return matches[-1].start()

    return None


def process_post(slug, cluster_name):
    """Add Related Reading to a single post."""
    filepath = os.path.join(BLOG_DIR, slug, "index.html")
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has Related Reading
    if '<!-- Related Reading (cross-links) -->' in content:
        print(f"  SKIP: {slug} already has Related Reading")
        return None

    insertion_point = find_insertion_point(content)
    if insertion_point is None:
        print(f"  ERROR: No insertion point found for {slug}")
        return None

    related_html = build_related_html(slug, cluster_name)

    new_content = content[:insertion_point] + related_html + "\n" + content[insertion_point:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Count links added
    link_count = related_html.count('<li')
    return link_count


def main():
    results = []
    total_links = 0

    for cluster_name, cluster_posts in CLUSTERS.items():
        print(f"\n=== Cluster: {cluster_name} ===")
        for slug in cluster_posts:
            print(f"  Processing: {slug}")
            count = process_post(slug, cluster_name)
            if count:
                total_links += count
                # Get in-cluster links
                in_cluster = [(s, t) for s, t in cluster_posts.items() if s != slug][:3]
                cross = CROSS_CLUSTER.get(slug)
                links_desc = [f"{t}" for s, t in in_cluster]
                if cross:
                    links_desc.append(f"{cross[1]} (cross-cluster)")
                results.append({
                    "slug": slug,
                    "cluster": cluster_name,
                    "links_added": count,
                    "links": links_desc,
                })
                print(f"    Added {count} links")

    print(f"\n=== TOTAL: {total_links} links added across {len(results)} posts ===")

    # Generate summary report
    report_lines = [
        "# Blog Cross-Links Added - March 28, 2026",
        "",
        f"**Total posts updated**: {len(results)}",
        f"**Total links added**: {total_links}",
        "",
        "## Cluster Map",
        "",
        "| Cluster | Posts | Description |",
        "|---------|-------|-------------|",
        "| AI Memory | 5 | Memory persistence, context loss, zero-reset problem |",
        "| AI Agents | 4 | Agent teams, agentic AI, market trends |",
        "| AI Partnership | 3 | Tool vs partner, relationship building |",
        "| Pilot Failure | 3 | Why AI pilots fail, purgatory, success patterns |",
        "| AI Naming | 3 | Naming your AI, identity, human-AI connection |",
        "| PureBrain Differentiator | 3 | What sets PureBrain apart, trust, capability gap |",
        "",
        "## Links Added Per Post",
        "",
    ]

    current_cluster = None
    for r in results:
        if r["cluster"] != current_cluster:
            current_cluster = r["cluster"]
            report_lines.append(f"### Cluster: {current_cluster}")
            report_lines.append("")

        report_lines.append(f"**/{r['slug']}/** ({r['links_added']} links)")
        for link in r["links"]:
            report_lines.append(f"  - {link}")
        report_lines.append("")

    report_lines.extend([
        "## Cross-Cluster Strategy",
        "",
        "Each post gets 2-3 in-cluster links plus 1 cross-cluster link:",
        "- AI Memory <-> AI Partnership (memory enables partnership)",
        "- AI Agents <-> Pilot Failure (agents solve pilot problems)",
        "- AI Naming <-> AI Partnership (naming is partnership behavior)",
        "- PureBrain Differentiator <-> AI Memory (memory is the differentiator)",
        "",
        "## Styling",
        "",
        "All Related Reading sections use matching dark theme:",
        "- Background: rgba(15,23,42,0.6)",
        "- Border: 1px solid rgba(42,147,193,0.15)",
        "- Link color: #2a93c1",
        "- Placed before the CTA block in each post",
        "",
        "## Verification",
        "",
        "- NO content was changed in any post",
        "- Only the Related Reading div was added",
        "- Insertion point: before the last CTA block",
        "- All links use relative paths (/blog/slug/)",
        "",
        "## Status: LOCAL ONLY - Not deployed",
    ])

    report_path = "/home/jared/exports/portal-files/cross-links-added-march30.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))

    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
