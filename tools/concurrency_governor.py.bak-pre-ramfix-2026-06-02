#!/usr/bin/env python3
"""
Concurrency Governor — Phase-4 fork pilot headroom-scaled team-count gate.

Purpose
-------
Decide how many parallel agents/teams are safe to run RIGHT NOW based on live
machine headroom, so "run more teams at once" never recreates our historical
failure modes: OOM, zombie-BOOP pileups, and PID/resource exhaustion.

This is a LIBRARY + SELFTEST. It does NOT touch the running boop_executor, the
scheduled-tasks state, any .pid file, or any service. It only READS live signals
(/proc, os.getloadavg, process list) and returns a recommended integer.

Signals consulted
-----------------
- CPU load:  os.getloadavg() compared against os.cpu_count() (load per-core).
- RAM:       /proc/meminfo MemAvailable (psutil used only if present; soft dep).
- PID press: count of /proc PIDs + count of running claude/python boop procs,
             measured against Hetzner-observed limits (~150 warn / ~190 crit).

Design stance: CONSERVATIVE. When in doubt, return the floor. It is always
cheaper to under-spawn and re-check between batches than to OOM the box.

Usage
-----
    from tools.concurrency_governor import (
        recommended_concurrency, can_spawn_another, gate, headroom_report,
    )

    n = gate(desired_n=8)          # min(8, what's safe now), logs if throttled
    if can_spawn_another(running): ...

    python3 tools/concurrency_governor.py --selftest
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from dataclasses import dataclass, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Tunable thresholds (sourced from collective memory + observed Hetzner limits)
# ---------------------------------------------------------------------------

# RAM: below this much available, we refuse to scale up (return floor).
MIN_RAM_AVAIL_MB = 1536          # ~1.5 GB

# Headroom band for RAM: we budget roughly this much RAM per additional agent
# when computing how many *more* we can afford. Conservative estimate for a
# claude/python worker footprint.
RAM_PER_AGENT_MB = 600

# CPU: load-per-core above this means the box is busy; clamp to floor.
MAX_LOAD_PER_CORE = 0.8

# PID pressure: total /proc PID count thresholds (Hetzner-observed).
PID_WARN = 150                   # start throttling
PID_CRIT = 190                   # hard floor

# Logger — library should be quiet unless the host app configures logging.
log = logging.getLogger("concurrency_governor")
if not log.handlers:
    log.addHandler(logging.NullHandler())


# ---------------------------------------------------------------------------
# Raw signal collection
# ---------------------------------------------------------------------------

def _cpu_count() -> int:
    return os.cpu_count() or 1


def _load_1min() -> float:
    try:
        return os.getloadavg()[0]
    except (OSError, AttributeError):
        return 0.0


def _mem_avail_mb() -> Optional[float]:
    """Available RAM in MB. Prefer psutil if present, else parse /proc/meminfo."""
    # Soft dependency on psutil — guard the import, never hard-require it.
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().available / (1024 * 1024)
    except Exception:
        pass
    try:
        with open("/proc/meminfo", "r") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    # Format: "MemAvailable:    2051496 kB"
                    kb = float(line.split()[1])
                    return kb / 1024.0
    except (OSError, ValueError, IndexError):
        pass
    return None


def _pid_count() -> Optional[int]:
    """Total number of PIDs currently on the system."""
    try:
        return sum(1 for n in os.listdir("/proc") if n.isdigit())
    except OSError:
        return None


def _boop_proc_count() -> int:
    """Count running claude / python boop-worker processes (best effort)."""
    count = 0
    # Try psutil first if available.
    try:
        import psutil  # type: ignore
        for p in psutil.process_iter(["name", "cmdline"]):
            try:
                name = (p.info.get("name") or "").lower()
                cmd = " ".join(p.info.get("cmdline") or []).lower()
                if "claude" in name or "claude" in cmd or "boop_executor" in cmd:
                    count += 1
            except Exception:
                continue
        return count
    except Exception:
        pass
    # Fall back to pgrep.
    for pat in ("claude", "boop_executor"):
        try:
            out = subprocess.run(
                ["pgrep", "-fc", pat],
                capture_output=True, text=True, timeout=5,
            )
            if out.returncode == 0:
                count += int(out.stdout.strip() or "0")
        except (subprocess.SubprocessError, ValueError, FileNotFoundError):
            continue
    return count


# ---------------------------------------------------------------------------
# Headroom report (observability)
# ---------------------------------------------------------------------------

@dataclass
class Signals:
    cpu_count: int
    load_1min: float
    load_per_core: float
    mem_avail_mb: Optional[float]
    pid_count: Optional[int]
    boop_proc_count: int


def _collect_signals() -> Signals:
    cpu = _cpu_count()
    load = _load_1min()
    mem = _mem_avail_mb()
    pids = _pid_count()
    boops = _boop_proc_count()
    return Signals(
        cpu_count=cpu,
        load_1min=round(load, 3),
        load_per_core=round(load / cpu, 3) if cpu else load,
        mem_avail_mb=round(mem, 1) if mem is not None else None,
        pid_count=pids,
        boop_proc_count=boops,
    )


def headroom_report() -> dict:
    """Return the raw signals as a dict for logging/observability."""
    return asdict(_collect_signals())


# ---------------------------------------------------------------------------
# Core decision logic (pure function over explicit signal values — testable)
# ---------------------------------------------------------------------------

def _compute_concurrency(
    *,
    cpu_count: int,
    load_1min: float,
    mem_avail_mb: Optional[float],
    pid_count: Optional[int],
    floor: int,
    ceiling: int,
) -> int:
    """
    Pure mapping from explicit signal values -> concurrency in [floor, ceiling].

    This function takes NO live readings — callers (or tests) inject values.
    That makes the clamping behavior deterministically verifiable.

    Conservative rules (any single one can force the floor):
      - RAM available < MIN_RAM_AVAIL_MB           -> floor
      - load per-core > MAX_LOAD_PER_CORE          -> floor
      - PID count >= PID_CRIT                       -> floor

    Otherwise, the recommendation is the MINIMUM of three budgets:
      - CPU budget:  cpu_count (one agent per core as the saturation baseline)
      - RAM budget:  floor( (mem_avail - reserve) / RAM_PER_AGENT_MB )
      - PID budget:  reduced if pid_count in the warn band

    Result is always clamped into [floor, ceiling].
    """
    if floor < 1:
        floor = 1
    if ceiling < floor:
        ceiling = floor

    cpu_count = max(1, cpu_count)

    # --- Hard floor conditions -------------------------------------------
    if mem_avail_mb is not None and mem_avail_mb < MIN_RAM_AVAIL_MB:
        return floor
    load_per_core = load_1min / cpu_count
    if load_per_core > MAX_LOAD_PER_CORE:
        return floor
    if pid_count is not None and pid_count >= PID_CRIT:
        return floor

    # --- Per-resource budgets --------------------------------------------
    # CPU budget: how much load headroom remains, expressed in cores.
    # At load_per_core==MAX we have ~0 spare; at 0 we have full cpu_count.
    spare_core_fraction = max(0.0, MAX_LOAD_PER_CORE - load_per_core) / MAX_LOAD_PER_CORE
    cpu_budget = max(1, int(round(cpu_count * spare_core_fraction)))

    # RAM budget: reserve MIN_RAM_AVAIL_MB as a safety cushion, then divide
    # the remainder by per-agent footprint.
    if mem_avail_mb is None:
        ram_budget = floor  # unknown RAM -> be conservative
    else:
        usable = mem_avail_mb - MIN_RAM_AVAIL_MB
        ram_budget = max(0, int(usable // RAM_PER_AGENT_MB))

    # PID budget: in the warn band, shrink toward floor proportionally.
    if pid_count is None:
        pid_budget = ceiling
    elif pid_count < PID_WARN:
        pid_budget = ceiling
    else:
        # Linear taper from ceiling (at PID_WARN) down to floor (at PID_CRIT).
        span = max(1, PID_CRIT - PID_WARN)
        frac = (PID_CRIT - pid_count) / span  # 1.0 at warn, 0.0 at crit
        pid_budget = floor + int(round((ceiling - floor) * max(0.0, frac)))

    recommended = min(cpu_budget, ram_budget, pid_budget, ceiling)
    recommended = max(floor, recommended)
    return int(recommended)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommended_concurrency(floor: int = 2, ceiling: int = 10) -> int:
    """
    How many parallel agents are safe RIGHT NOW, clamped to [floor, ceiling].

    Reads live headroom (CPU load, available RAM, PID/process pressure) and maps
    it to a conservative integer. Returns `floor` whenever the box is tight.
    """
    s = _collect_signals()
    return _compute_concurrency(
        cpu_count=s.cpu_count,
        load_1min=s.load_1min,
        mem_avail_mb=s.mem_avail_mb,
        pid_count=s.pid_count,
        floor=floor,
        ceiling=ceiling,
    )


def can_spawn_another(current_running: int, floor: int = 2, ceiling: int = 10) -> bool:
    """
    True only if live headroom supports at least one more agent beyond
    `current_running`. Use this for incremental spawn loops.
    """
    if current_running < 0:
        current_running = 0
    return current_running + 1 <= recommended_concurrency(floor, ceiling)


def gate(desired_n: int, floor: int = 2, ceiling: int = 10) -> int:
    """
    Return min(desired_n, recommended_concurrency()). If the recommendation
    reduced the desired count, log WHY (the raw headroom signals).
    """
    if desired_n < 0:
        desired_n = 0
    rec = recommended_concurrency(floor, ceiling)
    allowed = min(desired_n, rec)
    if allowed < desired_n:
        s = _collect_signals()
        log.warning(
            "concurrency throttled: desired=%d -> allowed=%d (rec=%d) | "
            "load_per_core=%.3f mem_avail_mb=%s pid_count=%s boop_procs=%d cpu=%d",
            desired_n, allowed, rec,
            s.load_per_core, s.mem_avail_mb, s.pid_count, s.boop_proc_count, s.cpu_count,
        )
    return allowed


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _selftest(floor: int = 2, ceiling: int = 10) -> int:
    print("=" * 68)
    print("CONCURRENCY GOVERNOR — SELFTEST")
    print("=" * 68)

    # 1) Live headroom report ------------------------------------------------
    report = headroom_report()
    print("\n[1] headroom_report() — live signals:")
    for k, v in report.items():
        print(f"      {k:18} = {v}")

    # 2) Live recommendation -------------------------------------------------
    rec = recommended_concurrency(floor, ceiling)
    print(f"\n[2] recommended_concurrency(floor={floor}, ceiling={ceiling}) = {rec}")
    assert isinstance(rec, int), "recommendation must be an int"
    assert floor <= rec <= ceiling, f"recommendation {rec} out of [{floor},{ceiling}]"
    print(f"      OK: int within [{floor}, {ceiling}]")

    # 3) gate() never exceeds recommendation --------------------------------
    g_hi = gate(ceiling + 5, floor, ceiling)
    g_lo = gate(1, floor, ceiling)
    print(f"\n[3] gate({ceiling + 5}) = {g_hi}  (<= rec={rec}); gate(1) = {g_lo}")
    assert g_hi <= rec, "gate must not exceed recommendation"
    assert g_lo <= 1, "gate must not exceed desired"
    print("      OK: gate clamps to min(desired, recommended)")

    # 4) Injected LOW-headroom inputs must clamp to floor -------------------
    print("\n[4] simulated low-RAM / high-load / high-PID inputs -> floor:")
    low_cases = {
        "low_ram": dict(cpu_count=8, load_1min=0.1, mem_avail_mb=512.0, pid_count=40),
        "high_load": dict(cpu_count=2, load_1min=4.0, mem_avail_mb=8000.0, pid_count=40),
        "pid_crit": dict(cpu_count=8, load_1min=0.1, mem_avail_mb=8000.0, pid_count=PID_CRIT),
        "unknown_ram": dict(cpu_count=8, load_1min=0.1, mem_avail_mb=None, pid_count=40),
    }
    for name, sig in low_cases.items():
        n = _compute_concurrency(floor=floor, ceiling=ceiling, **sig)
        print(f"      {name:12} -> {n}")
        assert n == floor, f"{name}: expected floor={floor}, got {n}"
    print(f"      OK: all low-headroom cases clamp to floor={floor}")

    # 5) Injected HIGH-headroom inputs must approach ceiling ----------------
    print("\n[5] simulated high-headroom input -> approaches ceiling:")
    high = dict(
        cpu_count=16, load_1min=0.0,
        mem_avail_mb=float(MIN_RAM_AVAIL_MB + RAM_PER_AGENT_MB * (ceiling + 4)),
        pid_count=30,
    )
    n_hi = _compute_concurrency(floor=floor, ceiling=ceiling, **high)
    print(f"      high_headroom -> {n_hi} (ceiling={ceiling})")
    assert n_hi == ceiling, f"expected ceiling={ceiling}, got {n_hi}"
    print(f"      OK: abundant headroom reaches ceiling={ceiling}")

    # 6) PID warn-band taper sanity -----------------------------------------
    print("\n[6] PID warn-band taper (high headroom otherwise):")
    base = dict(cpu_count=16, load_1min=0.0,
                mem_avail_mb=float(MIN_RAM_AVAIL_MB + RAM_PER_AGENT_MB * 40))
    at_warn = _compute_concurrency(floor=floor, ceiling=ceiling, pid_count=PID_WARN, **base)
    mid = _compute_concurrency(floor=floor, ceiling=ceiling,
                               pid_count=(PID_WARN + PID_CRIT) // 2, **base)
    print(f"      pid={PID_WARN} (warn) -> {at_warn}; pid={(PID_WARN+PID_CRIT)//2} (mid) -> {mid}")
    assert floor <= mid <= at_warn <= ceiling, "warn-band should taper down monotonically"
    print("      OK: warn-band tapers ceiling -> floor as PIDs climb")

    print("\n" + "=" * 68)
    print("ALL ASSERTIONS PASSED")
    print("=" * 68)
    return 0


def _main() -> int:
    ap = argparse.ArgumentParser(description="Phase-4 concurrency governor")
    ap.add_argument("--selftest", action="store_true", help="run selftest + proofs")
    ap.add_argument("--floor", type=int, default=2)
    ap.add_argument("--ceiling", type=int, default=10)
    ap.add_argument("--report", action="store_true", help="print headroom_report() only")
    args = ap.parse_args()

    if args.report:
        import json
        print(json.dumps(headroom_report(), indent=2))
        return 0
    if args.selftest:
        return _selftest(args.floor, args.ceiling)

    # Default: print the live recommendation.
    print(recommended_concurrency(args.floor, args.ceiling))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
