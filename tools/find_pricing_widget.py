#!/usr/bin/env python3
"""
Inspect the Elementor JSON to find the HTML widget containing the pricing section.
"""
import json
import sys

def find_widgets_with_content(data, target_text, path="root"):
    """Recursively find all widgets/elements that contain target_text in their settings."""
    results = []

    if isinstance(data, list):
        for i, item in enumerate(data):
            results.extend(find_widgets_with_content(item, target_text, f"{path}[{i}]"))
    elif isinstance(data, dict):
        # Check if this element has 'html' setting containing the target
        settings = data.get('settings', {})
        if isinstance(settings, dict):
            html_content = settings.get('html', '') or settings.get('editor', '') or settings.get('content', '')
            if isinstance(html_content, str) and target_text in html_content:
                results.append({
                    'path': path,
                    'id': data.get('id'),
                    'elType': data.get('elType'),
                    'widgetType': data.get('widgetType'),
                    'html_length': len(html_content),
                    'html_preview': html_content[:200]
                })

        # Recurse into elements
        elements = data.get('elements', [])
        results.extend(find_widgets_with_content(elements, target_text, f"{path}.elements"))

    return results


def inspect_element(data, path="root", depth=0):
    """Print tree structure of elements."""
    indent = "  " * depth
    if isinstance(data, list):
        for i, item in enumerate(data):
            inspect_element(item, f"{path}[{i}]", depth)
    elif isinstance(data, dict):
        el_type = data.get('elType', '?')
        widget_type = data.get('widgetType', '')
        el_id = data.get('id', '?')
        settings = data.get('settings', {})

        # Show what settings keys this has
        setting_keys = list(settings.keys()) if isinstance(settings, dict) else []

        type_str = f"{el_type}"
        if widget_type:
            type_str += f"/{widget_type}"

        print(f"{indent}[{el_id}] {type_str} — settings: {setting_keys[:5]}")

        elements = data.get('elements', [])
        if elements and depth < 4:
            inspect_element(elements, f"{path}.elements", depth + 1)


print("Loading Elementor JSON...")
with open('/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data.json', 'r') as f:
    elementor_data = json.load(f)

print(f"Type: {type(elementor_data)}, length: {len(elementor_data) if isinstance(elementor_data, list) else 'N/A'}")

print("\n--- Tree Structure (depth 4) ---")
inspect_element(elementor_data)

print("\n--- Searching for widget with 'pricing-grid' ---")
results = find_widgets_with_content(elementor_data, 'pricing-grid')
print(f"Found {len(results)} widgets with 'pricing-grid':")
for r in results:
    print(f"  path: {r['path']}")
    print(f"  id: {r['id']}, type: {r['elType']}/{r['widgetType']}")
    print(f"  html_length: {r['html_length']}")
    print(f"  preview: {r['html_preview'][:100]}")
    print()

print("\n--- Searching for widget with 'Bonded' ---")
results2 = find_widgets_with_content(elementor_data, 'Bonded')
print(f"Found {len(results2)} widgets with 'Bonded':")
for r in results2:
    print(f"  id: {r['id']}, type: {r['elType']}/{r['widgetType']}, length: {r['html_length']}")
