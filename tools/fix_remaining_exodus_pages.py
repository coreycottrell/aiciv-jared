#!/usr/bin/env python3
"""
Fix remaining 2 exodus pages that have different JS structure:
- competitor-exodus-custom-gpts.html
- competitor-exodus-perplexity.html

These pages have compact JS (no line breaks between statements) so the
original injection patterns don't match.
"""

import os
import base64
import requests
from pathlib import Path

EXPORTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports")
WP_BASE = "https://purebrain.ai/wp-json/wp/v2/pages"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

PAGES = {
    756: ("competitor-exodus-custom-gpts.html", "Custom GPTs"),
    760: ("competitor-exodus-perplexity.html", "Perplexity"),
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


def migration_css():
    return """
  /* ─── MIGRATION QUESTIONS ─── */
  .migration-section { margin-top: 0; padding-top: 8px; }
  .migration-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(42,147,193,0.3), transparent); margin: 32px 0 36px; }
  .migration-label { display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--pb-blue); font-weight: 700; margin-bottom: 24px; padding: 5px 12px; background: rgba(42,147,193,0.1); border-radius: 100px; border: 1px solid rgba(42,147,193,0.2); }
  .migration-step { display: none; }
  .migration-step.active { display: block; }
  .quiz-options-multi { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 8px; }
  .quiz-option-chip { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 16px; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; color: var(--text-primary); user-select: none; }
  .quiz-option-chip:hover { border-color: var(--pb-blue); background: rgba(42,147,193,0.08); }
  .quiz-option-chip.selected { border-color: var(--pb-orange); background: rgba(241,66,11,0.08); }
  .chip-check { width: 18px; height: 18px; min-width: 18px; border-radius: 4px; border: 1.5px solid rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; transition: all 0.2s; }
  .quiz-option-chip.selected .chip-check { background: var(--pb-orange); border-color: var(--pb-orange); color: #fff; }
  .multi-hint { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 20px; font-style: italic; }
  .migration-progress { display: flex; gap: 6px; margin-bottom: 32px; }
  .migration-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.1); transition: background 0.3s; }
  .migration-dot.active { background: var(--pb-blue); }
  .migration-dot.done { background: var(--pb-orange); }
"""


def migration_html(competitor_name):
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
          <div class="quiz-option-chip" data-v="writing" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Writing &amp; editing</div>
          <div class="quiz-option-chip" data-v="research" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Research &amp; summarization</div>
          <div class="quiz-option-chip" data-v="coding" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Coding &amp; technical help</div>
          <div class="quiz-option-chip" data-v="image_gen" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Image generation</div>
          <div class="quiz-option-chip" data-v="brainstorming" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Brainstorming &amp; ideation</div>
          <div class="quiz-option-chip" data-v="customer_content" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Customer-facing content</div>
          <div class="quiz-option-chip" data-v="productivity" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Productivity &amp; planning</div>
          <div class="quiz-option-chip" data-v="data_analysis" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Data analysis</div>
          <div class="quiz-option-chip" data-v="presentations" onclick="toggleChip(this)"><div class="chip-check">&#10003;</div>Presentations &amp; documents</div>
        </div>
        <div class="quiz-nav"><button class="btn-next visible" onclick="nextMigration('a','b')">Next &#8594;</button></div>
      </div>
      <!-- QUESTION B: Usage Frequency -->
      <div class="migration-step" id="mstep-b">
        <p class="quiz-question">How often were you using it?</p>
        <p class="quiz-subtext">This helps us understand how much context you've built up.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="b" data-v="multiple_times_daily" onclick="selectMigration(this)"><div class="option-letter">A</div><div class="option-text">Multiple times a day — it was a core part of my workflow</div></div>
          <div class="quiz-option" data-mq="b" data-v="once_daily" onclick="selectMigration(this)"><div class="option-letter">B</div><div class="option-text">Once a day — regular but not constant</div></div>
          <div class="quiz-option" data-mq="b" data-v="few_times_weekly" onclick="selectMigration(this)"><div class="option-letter">C</div><div class="option-text">A few times a week</div></div>
          <div class="quiz-option" data-mq="b" data-v="occasionally" onclick="selectMigration(this)"><div class="option-letter">D</div><div class="option-text">Occasionally — when I needed something specific</div></div>
        </div>
        <div class="quiz-nav"><button class="btn-next" id="mnext-b" onclick="nextMigration('b','c')">Next &#8594;</button></div>
      </div>
      <!-- QUESTION C: Custom Configuration -->
      <div class="migration-step" id="mstep-c">
        <p class="quiz-question">Had you set up any custom instructions, templates, or saved prompts?</p>
        <p class="quiz-subtext">This is often the most painful thing to lose when switching.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="c" data-v="fully_customized" onclick="selectMigration(this)"><div class="option-letter">A</div><div class="option-text">Yes — I had everything set up exactly how I wanted it</div></div>
          <div class="quiz-option" data-mq="c" data-v="some_customization" onclick="selectMigration(this)"><div class="option-letter">B</div><div class="option-text">Some basic customization — nothing too elaborate</div></div>
          <div class="quiz-option" data-mq="c" data-v="no_customization" onclick="selectMigration(this)"><div class="option-letter">C</div><div class="option-text">No — I used the defaults as-is</div></div>
        </div>
        <div class="quiz-nav"><button class="btn-next" id="mnext-c" onclick="nextMigration('c','d')">Next &#8594;</button></div>
      </div>
      <!-- QUESTION D: Main Frustration -->
      <div class="migration-step" id="mstep-d">
        <p class="quiz-question">What finally made you look for something better?</p>
        <p class="quiz-subtext">The real reason — be honest.</p>
        <div class="quiz-options">
          <div class="quiz-option" data-mq="d" data-v="no_memory" onclick="selectMigration(this)"><div class="option-letter">A</div><div class="option-text">Didn't remember anything between conversations</div></div>
          <div class="quiz-option" data-mq="d" data-v="felt_generic" onclick="selectMigration(this)"><div class="option-letter">B</div><div class="option-text">Felt generic — like talking to a tool, not a partner</div></div>
          <div class="quiz-option" data-mq="d" data-v="no_tool_integration" onclick="selectMigration(this)"><div class="option-letter">C</div><div class="option-text">Couldn't connect it to my other tools and workflows</div></div>
          <div class="quiz-option" data-mq="d" data-v="inconsistent_results" onclick="selectMigration(this)"><div class="option-letter">D</div><div class="option-text">Results weren't consistent enough for professional use</div></div>
          <div class="quiz-option" data-mq="d" data-v="too_expensive" onclick="selectMigration(this)"><div class="option-letter">E</div><div class="option-text">Too expensive for what I was getting</div></div>
          <div class="quiz-option" data-mq="d" data-v="missing_features" onclick="selectMigration(this)"><div class="option-letter">F</div><div class="option-text">Missing features I needed</div></div>
          <div class="quiz-option" data-mq="d" data-v="wanted_business_focus" onclick="selectMigration(this)"><div class="option-letter">G</div><div class="option-text">I wanted something specifically designed for business</div></div>
        </div>
        <div class="quiz-nav"><button class="btn-next" id="mnext-d" onclick="showGateAfterMigration()">See my results &#8594;</button></div>
      </div>
    </div>
"""


def migration_js():
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
    if (idx === -1) { migration_data.primary_use_cases.push(v); }
    else { migration_data.primary_use_cases.splice(idx, 1); }
  }
  function selectMigration(el) {
    const mq = el.getAttribute('data-mq');
    el.closest('.quiz-options').querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    const v = el.getAttribute('data-v');
    if (mq === 'b') { migration_data.usage_frequency = v; document.getElementById('mnext-b').classList.add('visible'); }
    else if (mq === 'c') { migration_data.had_custom_config = v; document.getElementById('mnext-c').classList.add('visible'); }
    else if (mq === 'd') { migration_data.main_frustration = v; document.getElementById('mnext-d').classList.add('visible'); }
  }
  function nextMigration(current, next) {
    document.getElementById('mstep-' + current).classList.remove('active');
    document.getElementById('mdot-' + current).classList.remove('active');
    document.getElementById('mdot-' + current).classList.add('done');
    document.getElementById('mstep-' + next).classList.add('active');
    document.getElementById('mdot-' + next).classList.add('active');
    document.getElementById('migration-section').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function showMigrationSection() {
    if (!answers.q3) return;
    document.getElementById('step-3').classList.remove('active');
    document.getElementById('dot-3').classList.remove('active');
    document.getElementById('dot-3').classList.add('done');
    const ms = document.getElementById('migration-section');
    ms.style.display = 'block';
    ms.scrollIntoView({ behavior: 'smooth', block: 'start' });
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


def process_compact_page(html, competitor_name):
    """Process pages with compact JS (no // ─── QUIZ STATE ─── comment)."""

    # 1. Inject CSS
    html = html.replace('</style>', migration_css() + '\n</style>', 1)

    # 2. Change Q3 "See my results" button to go to migration first
    html = html.replace(
        'onclick="showGate()">See my results',
        'onclick="showMigrationSection()">Continue'
    )

    # 3. Insert migration HTML before email gate
    gate_marker = '    <!-- EMAIL GATE -->'
    if gate_marker in html:
        html = html.replace(gate_marker, migration_html(competitor_name) + '\n    <!-- EMAIL GATE -->', 1)
    else:
        # Try alternate marker
        gate_marker2 = '<div class="gate-step" id="gate-step">'
        if gate_marker2 in html:
            html = html.replace(gate_marker2, migration_html(competitor_name) + '\n    ' + gate_marker2, 1)

    # 4. Inject migration JS before `const answers`
    html = html.replace(
        '  const answers = { q1: null, q2: null, q3: null };',
        migration_js() + '  const answers = { q1: null, q2: null, q3: null };',
        1
    )

    # 5. Inject Brevo migration attributes into submitGate
    # Pattern: `const payload = { email }; if (name) payload.first_name = name;`
    brevo_inject = """
      if (migration_data.primary_use_cases.length > 0) { payload.PRIMARY_USE_CASES = migration_data.primary_use_cases.join(','); }
      if (migration_data.usage_frequency) { payload.USAGE_FREQUENCY = migration_data.usage_frequency; }
      if (migration_data.had_custom_config) { payload.HAD_CUSTOM_CONFIG = migration_data.had_custom_config; }
      if (migration_data.main_frustration) { payload.MAIN_FRUSTRATION = migration_data.main_frustration; }"""

    # Try compact pattern first
    compact_payload = "const payload = { email }; if (name) payload.first_name = name;"
    if compact_payload in html:
        html = html.replace(
            compact_payload,
            compact_payload + brevo_inject
        )
    else:
        # Try multi-line pattern
        ml_payload = "const payload = { email };\n      if (name) payload.first_name = name;"
        if ml_payload in html:
            html = html.replace(
                ml_payload,
                ml_payload + brevo_inject
            )

    # 6. Add footer
    if 'Built by <strong style="color: #2a93c1;">AETHER</strong>' not in html:
        html = html.replace('</body>', FOOTER_CREDIT + '\n</body>', 1)

    return html


def deploy_to_wordpress(page_id, html_content):
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        f"{WP_BASE}/{page_id}",
        headers=headers,
        json={"content": html_content},
        timeout=30
    )
    return resp.status_code


def main():
    print("Fixing remaining 2 exodus pages...")

    for page_id, (filename, competitor_name) in PAGES.items():
        filepath = EXPORTS_DIR / filename
        print(f"\n[{page_id}] {filename} ({competitor_name})")

        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        updated = process_compact_page(original, competitor_name)

        # Verify
        checks = [
            ('migration_data', 'Migration JS'),
            ('PRIMARY_USE_CASES', 'Brevo attr'),
            ('MAIN_FRUSTRATION', 'Brevo frustration'),
            ('migration-section', 'Migration HTML'),
            ('AETHER', 'Footer'),
        ]
        all_ok = True
        for marker, label in checks:
            if marker not in updated:
                print(f"  MISSING: {label}")
                all_ok = False
            else:
                print(f"  OK: {label}")

        if not all_ok:
            print("  ABORTED: injection incomplete")
            continue

        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"  Saved: {filepath}")

        # Deploy
        status = deploy_to_wordpress(page_id, updated)
        if status in (200, 201):
            print(f"  WordPress: SUCCESS (HTTP {status})")
        else:
            print(f"  WordPress: FAILED (HTTP {status})")

    # Clear cache
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    try:
        r = requests.delete(
            "https://purebrain.ai/wp-json/elementor/v1/cache",
            headers=headers, timeout=15
        )
        print(f"\nElementor cache cleared: HTTP {r.status_code}")
    except Exception as e:
        print(f"\nCache clear error: {e}")


if __name__ == "__main__":
    main()
