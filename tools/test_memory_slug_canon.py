#!/usr/bin/env python3
"""Standalone test for MemoryStore slug canonicalization (write-path guard).

Proves:
  - a known alias ('ptt-fullstack-dev') resolves to its canonical dir ('ptt-fullstack')
  - an unknown slug ('web-researcher') is left UNCHANGED (fail-open)
  - a missing alias map => no remapping (fail-open, no raise)

Run: python3 tools/test_memory_slug_canon.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memory_core import MemoryStore  # noqa: E402

ALIAS_MD = """# Agent Canonical-Slug Alias Map
## Canonical map (alias -> canonical)
| Canonical slug (has manifest) | Aliases to collapse |
|-------------------------------|---------------------|
| `ptt-fullstack`     | `ptt-full-stack`, `ptt-fullstack-dev`, `ptt-full-stack-developer`, `ptt-fullstack-developer`, `ptt` |
| `ptt-qa`            | `ptt-qa-engineer` |
| `the-conductor`     | `conductor`, `primary`, `aether` |
"""


def _store_with_map(tmp: Path, alias_text):
    base = tmp / ".claude" / "memory"
    store = MemoryStore(base_dir=str(base))
    if alias_text is not None:
        amap = tmp / "AGENT-SLUG-ALIASES.md"
        amap.write_text(alias_text, encoding="utf-8")
        store._alias_map_path = amap
    else:
        store._alias_map_path = tmp / "DOES-NOT-EXIST.md"
    return store


def run():
    failures = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1. Known alias -> canonical
        store = _store_with_map(tmp, ALIAS_MD)
        d = store._get_agent_dir("ptt-fullstack-dev")
        if d.name != "ptt-fullstack":
            failures.append(f"alias: expected 'ptt-fullstack', got '{d.name}'")
        else:
            print(f"PASS  alias  ptt-fullstack-dev -> {d.name}")
        if not d.is_dir():
            failures.append("alias: canonical dir was not created")

        # 2. Unknown slug -> unchanged
        d2 = store._get_agent_dir("web-researcher")
        if d2.name != "web-researcher":
            failures.append(f"unknown: expected 'web-researcher', got '{d2.name}'")
        else:
            print(f"PASS  unknown  web-researcher -> {d2.name}")

        # 3. Another known alias (different row)
        d3 = store._get_agent_dir("conductor")
        if d3.name != "the-conductor":
            failures.append(f"alias2: expected 'the-conductor', got '{d3.name}'")
        else:
            print(f"PASS  alias  conductor -> {d3.name}")

        # 4. Missing map => fail-open, slug unchanged, no raise
        store2 = _store_with_map(tmp, None)
        d4 = store2._get_agent_dir("ptt-fullstack-dev")
        if d4.name != "ptt-fullstack-dev":
            failures.append(f"fail-open: expected unchanged, got '{d4.name}'")
        else:
            print(f"PASS  failopen  (no map) ptt-fullstack-dev -> {d4.name}")

        # 5. Whole ptt-fullstack family (exact-map members) -> ptt-fullstack
        store5 = _store_with_map(tmp, ALIAS_MD)
        for src in (
            "ptt",
            "ptt-full-stack",
            "ptt-fullstack-dev",
            "ptt-fullstack-developer",
            "ptt-full-stack-developer",
        ):
            dd = store5._get_agent_dir(src)
            if dd.name != "ptt-fullstack":
                failures.append(f"family: {src!r} expected 'ptt-fullstack', got '{dd.name}'")
            else:
                print(f"PASS  family  {src} -> {dd.name}")

        # 6. NOVEL future variant (NOT in map) -> ptt-fullstack via prefix fallback
        dnov = store5._get_agent_dir("ptt-fullstack-v2")
        if dnov.name != "ptt-fullstack":
            failures.append(f"prefix: 'ptt-fullstack-v2' expected 'ptt-fullstack', got '{dnov.name}'")
        else:
            print(f"PASS  prefix  ptt-fullstack-v2 -> {dnov.name}")

        # 7. ptt-qa is its OWN canonical -> must NOT be folded into ptt-fullstack
        dqa = store5._get_agent_dir("ptt-qa")
        if dqa.name != "ptt-qa":
            failures.append(f"no-overmatch: 'ptt-qa' expected 'ptt-qa', got '{dqa.name}'")
        else:
            print(f"PASS  no-overmatch  ptt-qa -> {dqa.name}")

        # 8. ptt-qa-* novel variant -> ptt-qa (prefix), NOT ptt-fullstack, NOT ptt
        dqae = store5._get_agent_dir("ptt-qa-engineer")
        if dqae.name != "ptt-qa":
            failures.append(f"no-overmatch: 'ptt-qa-engineer' expected 'ptt-qa', got '{dqae.name}'")
        else:
            print(f"PASS  no-overmatch  ptt-qa-engineer -> {dqae.name}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    run()
