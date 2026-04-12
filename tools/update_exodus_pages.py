#!/usr/bin/env python3
"""
Update exodus pages with 4 new migration quiz questions.
Adds Questions A-D between existing quiz Q3 and email gate.
Updates Brevo integration with new attributes.
Deploys to WordPress pages 752-760.
"""

import os
import re
import json
import base64
import requests
from pathlib import Path

# ─── Config ───
EXPORTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports")
WP_BASE = "https://purebrain.ai/wp-json/wp/v2/pages"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

# Page ID → file mapping
PAGE_MAP = {
    752: "competitor-exodus-hub.html",        # Compare AI Tools hub
    753: "competitor-exodus-chatgpt.html",
    754: "competitor-exodus-claude.html",
    755: "competitor-exodus-copilot.html",
    756: "competitor-exodus-custom-gpts.html",
    757: "competitor-exodus-deepseek.html",
    758: "competitor-exodus-gemini.html",
    759: "competitor-exodus-jasper.html",
    760: "competitor-exodus-perplexity.html",
}

# Competitor name for each page (used in Q-A question text)
COMPETITOR_NAMES = {
    753: "ChatGPT",
    754: "Claude",
    755: "Microsoft Copilot",
    756: "Custom GPTs",
    757: "DeepSeek",
    758: "Gemini",
    759: "Jasper",
    760: "Perplexity",
    752: "your current AI tool",  # Hub page - generic
}

FOOTER_CREDIT = '''<!-- AETHER FOOTER -->
<div style="padding: 16px 40px; text-align: center; border-top: 1px solid rgba(42,147,193,0.12); background: rgba(8,10,18,0.8);">
  <p style="font-size: 0.75rem; color: #556677; letter-spacing: 0.03em;">
    Built by <strong style="color: #2a93c1;">AETHER</strong> (an AI) for
    <a href="https://purebrain.ai" style="color: #2a93c1; text-decoration: none;">PureBrain.ai</a>,
    <a href="https://puremarketing.ai" style="color: #f1420b; text-decoration: none;">PureMarketing.ai</a> &amp;
    <a href="https://puretechnology.ai" style="color: #2a93c1; text-decoration: none;">PureTechnology.ai</a>
  </p>
</div>'''


def build_migration_questions_css():
    """Additional CSS for multi-select options in Question A."""
    return """
  /* ─── MIGRATION QUESTIONS ─── */
  .migration-section {
    margin-top: 0;
    padding-top: 8px;
  }
  .migration-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(42,147,193,0.3), transparent);
    margin: 32px 0 36px;
  }
  .migration-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--pb-blue);
    font-weight: 700;
    margin-bottom: 24px;
    padding: 5px 12px;
    background: rgba(42,147,193,0.1);
    border-radius: 100px;
    border: 1px solid rgba(42,147,193,0.2);
  }
  .migration-step { display: none; }
  .migration-step.active { display: block; }

  /* Multi-select chip style for Question A */
  .quiz-options-multi {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 8px;
  }
  .quiz-option-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    color: var(--text-primary);
    user-select: none;
  }
  .quiz-option-chip:hover {
    border-color: var(--pb-blue);
    background: rgba(42,147,193,0.08);
  }
  .quiz-option-chip.selected {
    border-color: var(--pb-orange);
    background: rgba(241,66,11,0.08);
    color: var(--text-primary);
  }
  .chip-check {
    width: 18px; height: 18px; min-width: 18px;
    border-radius: 4px;
    border: 1.5px solid rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem;
    transition: all 0.2s;
  }
  .quiz-option-chip.selected .chip-check {
    background: var(--pb-orange);
    border-color: var(--pb-orange);
    color: #fff;
  }
  .multi-hint {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 20px;
    font-style: italic;
  }

  .migration-progress {
    display: flex;
    gap: 6px;
    margin-bottom: 32px;
  }
  .migration-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    transition: background 0.3s;
  }
  .migration-dot.active { background: var(--pb-blue); }
  .migration-dot.done { background: var(--pb-orange); }
"""


def build_migration_html(competitor_name):
    """HTML for the 4 migration questions."""
    return f"""
    <!-- ─── MIGRATION QUESTIONS (A-D) ─── -->
    <div class="migration-section" id="migration-section" style="display:none;">
      <div class="migration-divider"></div>
      <div class="migration-label">&#9679; Migration Intelligence</div>
      <p style="color: var(--text-muted); font-size: 0.92rem; margin-bottom: 28px; line-height: 1.6;">
        A few quick questions to personalize your migration experience — these help PureBrain learn from your {competitor_name} history.
      </p>

      <div class="migration-progress">
        <div class="migration-dot active" id="mdot-a"></div>
        <div class="migration-dot" id="mdot-b"></div>
        <div class="migration-dot" id="mdot-c"></div>
        <div class="migration-dot" id="mdot-d"></div>
      </div>

      <!-- QUESTION A: Primary Use Cases (Multi-select) -->
      <div class="migration-step active" id="mstep-a">
        <p class="quiz-question">What did you use {competitor_name} for most?</p>
        <p class="multi-hint">Select all that apply.</p>
        <div class="quiz-options-multi" id="mq-a-options">
          <div class="quiz-option-chip" data-v="writing" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Writing &amp; editing
          </div>
          <div class="quiz-option-chip" data-v="research" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Research &amp; summarization
          </div>
          <div class="quiz-option-chip" data-v="coding" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Coding &amp; technical help
          </div>
          <div class="quiz-option-chip" data-v="image_gen" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Image generation
          </div>
          <div class="quiz-option-chip" data-v="brainstorming" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Brainstorming &amp; ideation
          </div>
          <div class="quiz-option-chip" data-v="customer_content" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Customer-facing content
          </div>
          <div class="quiz-option-chip" data-v="productivity" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Productivity &amp; planning
          </div>
          <div class="quiz-option-chip" data-v="data_analysis" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Data analysis
          </div>
          <div class="quiz-option-chip" data-v="presentations" onclick="toggleChip(this)">
            <div class="chip-check">&#10003;</div>Presentations &amp; documents
          </div>
        </div>
        <div class="quiz-nav">
          <button class="btn-next visible" onclick="nextMigration('a', 'b')">Next →</button>
        </div>
      </div>

      <!-- QUESTION B: Usage Frequency -->
      <div class="migration-step" id="mstep-b">
        <p class="quiz-question">How often were you using it?</p>
        <p class="quiz-subtext">This helps us understand how much context you've built up.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="b" data-v="multiple_times_daily" onclick="selectMigration(this)">
            <div class="option-letter">A</div>
            <div class="option-text">Multiple times a day — it was a core part of my workflow</div>
          </div>
          <div class="quiz-option" data-mq="b" data-v="once_daily" onclick="selectMigration(this)">
            <div class="option-letter">B</div>
            <div class="option-text">Once a day — regular but not constant</div>
          </div>
          <div class="quiz-option" data-mq="b" data-v="few_times_weekly" onclick="selectMigration(this)">
            <div class="option-letter">C</div>
            <div class="option-text">A few times a week</div>
          </div>
          <div class="quiz-option" data-mq="b" data-v="occasionally" onclick="selectMigration(this)">
            <div class="option-letter">D</div>
            <div class="option-text">Occasionally — when I needed something specific</div>
          </div>
        </div>
        <div class="quiz-nav">
          <button class="btn-next" id="mnext-b" onclick="nextMigration('b', 'c')">Next →</button>
        </div>
      </div>

      <!-- QUESTION C: Custom Configuration -->
      <div class="migration-step" id="mstep-c">
        <p class="quiz-question">Had you set up any custom instructions, templates, or saved prompts?</p>
        <p class="quiz-subtext">This is often the most painful thing to lose when switching.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="c" data-v="fully_customized" onclick="selectMigration(this)">
            <div class="option-letter">A</div>
            <div class="option-text">Yes — I had everything set up exactly how I wanted it</div>
          </div>
          <div class="quiz-option" data-mq="c" data-v="some_customization" onclick="selectMigration(this)">
            <div class="option-letter">B</div>
            <div class="option-text">Some basic customization — nothing too elaborate</div>
          </div>
          <div class="quiz-option" data-mq="c" data-v="no_customization" onclick="selectMigration(this)">
            <div class="option-letter">C</div>
            <div class="option-text">No — I used the defaults as-is</div>
          </div>
        </div>
        <div class="quiz-nav">
          <button class="btn-next" id="mnext-c" onclick="nextMigration('c', 'd')">Next →</button>
        </div>
      </div>

      <!-- QUESTION D: Main Frustration -->
      <div class="migration-step" id="mstep-d">
        <p class="quiz-question">What finally made you look for something better?</p>
        <p class="quiz-subtext">The real reason — be honest.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="d" data-v="no_memory" onclick="selectMigration(this)">
            <div class="option-letter">A</div>
            <div class="option-text">Didn't remember anything between conversations</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="felt_generic" onclick="selectMigration(this)">
            <div class="option-letter">B</div>
            <div class="option-text">Felt generic — like talking to a tool, not a partner</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="no_tool_integration" onclick="selectMigration(this)">
            <div class="option-letter">C</div>
            <div class="option-text">Couldn't connect it to my other tools and workflows</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="inconsistent_results" onclick="selectMigration(this)">
            <div class="option-letter">D</div>
            <div class="option-text">Results weren't consistent enough for professional use</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="too_expensive" onclick="selectMigration(this)">
            <div class="option-letter">E</div>
            <div class="option-text">Too expensive for what I was getting</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="missing_features" onclick="selectMigration(this)">
            <div class="option-letter">F</div>
            <div class="option-text">Missing features I needed</div>
          </div>
          <div class="quiz-option" data-mq="d" data-v="wanted_business_focus" onclick="selectMigration(this)">
            <div class="option-letter">G</div>
            <div class="option-text">I wanted something specifically designed for business</div>
          </div>
        </div>
        <div class="quiz-nav">
          <button class="btn-next" id="mnext-d" onclick="showGateAfterMigration()">See my results →</button>
        </div>
      </div>
    </div>
"""


def build_migration_js():
    """JavaScript additions for migration questions."""
    return """
  // ─── MIGRATION DATA ───
  const migration_data = {
    primary_use_cases: [],
    usage_frequency: null,
    had_custom_config: null,
    main_frustration: null
  };

  function toggleChip(el) {
    el.classList.toggle('selected');
    const v = el.getAttribute('data-v');
    const idx = migration_data.primary_use_cases.indexOf(v);
    if (idx === -1) {
      migration_data.primary_use_cases.push(v);
    } else {
      migration_data.primary_use_cases.splice(idx, 1);
    }
  }

  function selectMigration(el) {
    const mq = el.getAttribute('data-mq');
    el.closest('.quiz-options').querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    const v = el.getAttribute('data-v');
    if (mq === 'b') {
      migration_data.usage_frequency = v;
      document.getElementById('mnext-b').classList.add('visible');
    } else if (mq === 'c') {
      migration_data.had_custom_config = v;
      document.getElementById('mnext-c').classList.add('visible');
    } else if (mq === 'd') {
      migration_data.main_frustration = v;
      document.getElementById('mnext-d').classList.add('visible');
    }
  }

  function nextMigration(current, next) {
    document.getElementById('mstep-' + current).classList.remove('active');
    document.getElementById('mdot-' + current).classList.remove('active');
    document.getElementById('mdot-' + current).classList.add('done');
    document.getElementById('mstep-' + next).classList.add('active');
    document.getElementById('mdot-' + next).classList.add('active');
    document.getElementById('migration-section').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function showGateAfterMigration() {
    if (!migration_data.main_frustration) return;
    document.getElementById('mstep-d').classList.remove('active');
    document.getElementById('mdot-d').classList.remove('active');
    document.getElementById('mdot-d').classList.add('done');
    document.getElementById('migration-section').style.display = 'none';
    document.getElementById('gate-step').classList.add('active');
    document.getElementById('gate-step').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
"""


def build_brevo_migration_payload():
    """JS snippet to add migration data to Brevo payload."""
    return """
      // Add migration data to Brevo payload
      if (migration_data.primary_use_cases.length > 0) {
        payload.PRIMARY_USE_CASES = migration_data.primary_use_cases.join(',');
      }
      if (migration_data.usage_frequency) {
        payload.USAGE_FREQUENCY = migration_data.usage_frequency;
      }
      if (migration_data.had_custom_config) {
        payload.HAD_CUSTOM_CONFIG = migration_data.had_custom_config;
      }
      if (migration_data.main_frustration) {
        payload.MAIN_FRUSTRATION = migration_data.main_frustration;
      }
"""


def inject_migration_css(html, extra_css):
    """Inject migration CSS before closing </style> tag."""
    return html.replace('</style>', extra_css + '\n</style>', 1)


def inject_migration_html_competitor(html, competitor_name):
    """
    For competitor pages: show migration section after Q3 is answered.
    Replace the showGate() call in the Q3 next button to instead show migration.
    Insert migration HTML before the email gate.
    """
    migration_html = build_migration_html(competitor_name)

    # Change Q3's "See my results →" button to show migration section first
    html = html.replace(
        'onclick="showGate()">See my results →',
        'onclick="showMigrationSection()">Continue →'
    )

    # Insert migration HTML before the email gate
    gate_marker = '    <!-- EMAIL GATE -->'
    html = html.replace(gate_marker, migration_html + '\n    <!-- EMAIL GATE -->', 1)

    return html


def inject_migration_js_competitor(html, competitor_name):
    """Add migration JS to the script section of competitor pages."""
    migration_js = build_migration_js()
    brevo_snippet = build_brevo_migration_payload()

    # Add showMigrationSection function and migration vars
    # Insert before the existing const answers line
    html = html.replace(
        '  // ─── QUIZ STATE ───\n  const answers',
        migration_js + '\n  // ─── QUIZ STATE ───\n  const answers'
    )

    # Add showMigrationSection() function after nextStep function
    show_migration_fn = """
  function showMigrationSection() {
    if (!answers.q3) return;
    document.getElementById('step-3').classList.remove('active');
    document.getElementById('dot-3').classList.remove('active');
    document.getElementById('dot-3').classList.add('done');
    const ms = document.getElementById('migration-section');
    ms.style.display = 'block';
    ms.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

"""
    html = html.replace(
        '  function showGate()',
        show_migration_fn + '  function showGate()'
    )

    # Inject migration data into the Brevo payload in submitGate
    # Find the payload building in submitGate and add migration attributes
    html = html.replace(
        "      const payload = { email };\n      if (name) payload.first_name = name;",
        "      const payload = { email };\n      if (name) payload.first_name = name;\n" + brevo_snippet
    )

    return html


def inject_footer(html):
    """Add Aether footer before closing </body> tag."""
    if 'Built by <strong style="color: #2a93c1;">AETHER</strong>' in html:
        return html  # Already has footer
    return html.replace('</body>', FOOTER_CREDIT + '\n</body>', 1)


def inject_migration_html_hub(html):
    """
    For the hub page: add migration questions after the existing 2-question quiz.
    The hub quiz uses a different flow (hubSelectOption / showHubGate / hubSubmitGate).
    We add the migration section after both hub quiz questions are answered.
    """
    migration_html = build_migration_html("your current AI tool")

    # Replace "Get my recommendation →" to show migration first
    html = html.replace(
        'onclick="showHubGate()">Get my recommendation →',
        'onclick="showHubMigration()">Get my recommendation →'
    )

    # Insert migration section before <!-- GATE --> in hub
    gate_marker = '    <!-- GATE -->'
    html = html.replace(gate_marker, migration_html + '\n    <!-- GATE -->', 1)

    return html


def inject_migration_js_hub(html):
    """Add migration JS to the hub page."""
    migration_js = build_migration_js()
    brevo_snippet = build_brevo_migration_payload()

    # Add showHubMigration function
    show_hub_migration_fn = """
function showHubMigration() {
  if (!hubAnswers.q1 || !hubAnswers.q2) return;
  document.getElementById('quiz-questions').style.display = 'none';
  document.getElementById('quiz-submit-area').style.display = 'none';
  const ms = document.getElementById('migration-section');
  ms.style.display = 'block';
  ms.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

"""

    # Override showGateAfterMigration for hub to call showHubGate logic
    # The migration JS already defines showGateAfterMigration - we need to override it
    hub_override = """
// Override for hub page - migration leads to hub gate
window.showGateAfterMigration = function() {
  if (!migration_data.main_frustration) return;
  document.getElementById('mstep-d').classList.remove('active');
  document.getElementById('mdot-d').classList.remove('active');
  document.getElementById('mdot-d').classList.add('done');
  document.getElementById('migration-section').style.display = 'none';
  document.getElementById('hub-gate').classList.add('active');
  document.getElementById('hub-gate').scrollIntoView({ behavior: 'smooth', block: 'start' });
};
"""

    # Insert at start of script
    html = html.replace(
        '// ─── TOOL DATA ───',
        migration_js + '\n' + show_hub_migration_fn + hub_override + '// ─── TOOL DATA ───'
    )

    # Add migration data to hub Brevo payload
    html = html.replace(
        "    const payload = { email };\n    if (name) payload.first_name = name;",
        "    const payload = { email };\n    if (name) payload.first_name = name;\n" + brevo_snippet
    )

    return html


def process_competitor_page(html_content, competitor_name):
    """Process a single competitor exodus page."""
    extra_css = build_migration_questions_css()
    html = inject_migration_css(html_content, extra_css)
    html = inject_migration_html_competitor(html, competitor_name)
    html = inject_migration_js_competitor(html, competitor_name)
    html = inject_footer(html)
    return html


def process_hub_page(html_content):
    """Process the hub page."""
    extra_css = build_migration_questions_css()
    html = inject_migration_css(html_content, extra_css)
    html = inject_migration_html_hub(html)
    html = inject_migration_js_hub(html)
    html = inject_footer(html)
    return html


def deploy_to_wordpress(page_id, html_content):
    """Deploy HTML content to WordPress page."""
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": html_content
    }
    url = f"{WP_BASE}/{page_id}"
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    return resp.status_code, resp.json() if resp.content else {}


def clear_elementor_cache():
    """Clear Elementor cache after updates."""
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    try:
        resp = requests.delete(
            "https://purebrain.ai/wp-json/elementor/v1/cache",
            headers=headers,
            timeout=15
        )
        return resp.status_code
    except Exception as e:
        return f"Error: {e}"


def main():
    print("=" * 60)
    print("EXODUS PAGES — MIGRATION QUIZ UPDATE")
    print("=" * 60)

    results = {}

    for page_id, filename in PAGE_MAP.items():
        filepath = EXPORTS_DIR / filename
        if not filepath.exists():
            print(f"  SKIP  {filename} (file not found)")
            continue

        competitor_name = COMPETITOR_NAMES.get(page_id, "your current AI tool")
        is_hub = (page_id == 752)

        print(f"\n[{page_id}] Processing {filename} ({competitor_name})...")

        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        # Process
        if is_hub:
            updated = process_hub_page(original)
        else:
            updated = process_competitor_page(original, competitor_name)

        # Verify key injections happened
        checks = [
            ('migration-section', 'Migration section HTML'),
            ('migration_data', 'Migration JS object'),
            ('PRIMARY_USE_CASES', 'Brevo attribute'),
            ('MAIN_FRUSTRATION', 'Brevo frustration attr'),
            ('AETHER', 'Footer credit'),
        ]
        ok = True
        for marker, label in checks:
            if marker not in updated:
                print(f"  WARN: Missing {label} in {filename}")
                ok = False

        if not ok:
            print(f"  SKIP deploying {filename} due to injection issues")
            continue

        # Save updated file
        output_path = EXPORTS_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"  Saved updated file: {output_path}")

        # Deploy to WordPress
        print(f"  Deploying to WordPress page {page_id}...")
        status, response = deploy_to_wordpress(page_id, updated)
        if status in (200, 201):
            print(f"  WordPress update: SUCCESS (HTTP {status})")
            results[page_id] = "SUCCESS"
        else:
            print(f"  WordPress update: FAILED (HTTP {status})")
            print(f"  Response: {str(response)[:200]}")
            results[page_id] = f"FAILED ({status})"

    # Clear Elementor cache
    print("\n\nClearing Elementor cache...")
    cache_status = clear_elementor_cache()
    print(f"  Cache clear: {cache_status}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for page_id, status in results.items():
        filename = PAGE_MAP.get(page_id, "unknown")
        print(f"  [{page_id}] {filename}: {status}")

    success_count = sum(1 for s in results.values() if s == "SUCCESS")
    print(f"\n  {success_count}/{len(results)} pages deployed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
