#!/usr/bin/env python3
"""
extract_homepage_css.py — Extract inline CSS from homepage into external stylesheet.

Extracts all <style> blocks from index.html into style.css.
Deduplicates exact-duplicate blocks.
Replaces all <style> tags with a single <link rel="stylesheet" href="/style.css">.

Usage:
    python3 tools/extract_homepage_css.py
"""

import re
import os

HOMEPAGE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html"
CSS_OUT = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/style.css"


def extract_css():
    with open(HOMEPAGE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all <style> blocks
    style_pattern = re.compile(
        r"<style([^>]*)>(.*?)</style>", re.DOTALL | re.IGNORECASE
    )
    styles = list(style_pattern.finditer(content))

    print(f"Found {len(styles)} <style> blocks")
    total_before = sum(len(s.group(2)) for s in styles)
    print(f"Total inline CSS: {total_before:,} chars ({total_before // 1024}KB)")

    # Collect unique CSS blocks (deduplicate by content)
    seen_content = set()
    css_parts = []
    dup_count = 0

    for i, s in enumerate(styles):
        attrs = s.group(1).strip()
        css = s.group(2)

        # Skip exact duplicate content
        if css in seen_content:
            dup_count += 1
            print(f"  Block {i+1}: DUPLICATE - skipped ({len(css)} chars)")
            continue
        seen_content.add(css)

        # Extract id for comment
        id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
        block_id = id_match.group(1) if id_match else f"block-{i+1}"

        css_parts.append(f"/* ---- {block_id} ---- */")
        css_parts.append(css.strip())
        css_parts.append("")

    combined_css = "\n".join(css_parts)
    total_after = len(combined_css)

    print(f"Duplicate blocks removed: {dup_count}")
    print(f"Unique CSS blocks: {len(styles) - dup_count}")
    print(f"Combined CSS size: {total_after:,} chars ({total_after // 1024}KB)")

    # Write external CSS file
    with open(CSS_OUT, "w", encoding="utf-8") as f:
        f.write(combined_css)
    print(f"Written to: {CSS_OUT}")

    # Replace all <style> blocks in HTML with a single <link> tag
    # Remove all style blocks
    new_content = style_pattern.sub("", content)

    # Insert <link> in <head> after <meta charset>
    link_tag = '<link rel="stylesheet" href="/style.css">'

    # Insert after </title> or before </head>
    title_end = new_content.find("</title>")
    if title_end != -1:
        insert_pos = title_end + len("</title>")
        new_content = (
            new_content[:insert_pos]
            + "\n"
            + link_tag
            + new_content[insert_pos:]
        )
    else:
        new_content = new_content.replace("</head>", link_tag + "\n</head>", 1)

    # Measure size reduction
    original_size = len(content)
    new_size = len(new_content)
    reduction = original_size - new_size
    print(f"\nHTML size before: {original_size:,} bytes")
    print(f"HTML size after:  {new_size:,} bytes")
    print(f"Size reduction:   {reduction:,} bytes ({reduction * 100 // original_size}%)")
    print(f"CSS file size:    {total_after:,} bytes ({total_after // 1024}KB)")

    # Write new HTML
    with open(HOMEPAGE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Homepage updated: {HOMEPAGE}")

    # Verify
    with open(HOMEPAGE, "r", encoding="utf-8") as f:
        verify = f.read()
    remaining_styles = len(re.findall(r"<style[^>]*>", verify))
    has_link = "/style.css" in verify
    print(f"\nVerification:")
    print(f"  Remaining <style> tags: {remaining_styles}")
    print(f"  <link> to style.css: {has_link}")

    return {
        "blocks_extracted": len(styles),
        "duplicates_removed": dup_count,
        "css_file_kb": total_after // 1024,
        "html_reduction_kb": reduction // 1024,
    }


if __name__ == "__main__":
    result = extract_css()
    print(f"\n--- SUMMARY ---")
    print(f"Style blocks extracted: {result['blocks_extracted']}")
    print(f"Duplicates removed: {result['duplicates_removed']}")
    print(f"CSS file size: {result['css_file_kb']}KB")
    print(f"HTML size reduction: {result['html_reduction_kb']}KB")
