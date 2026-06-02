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
(/proc, /sys/fs/cgroup, os.getloadavg, resource limits) and returns a
recommended integer.

DESIGN CHANGE (2026-06-02, ramfix) — PRIMARY signal is RAM, not PIDs
--------------------------------------------------------------------
The original governor inherited a hardcoded "PID >= 190 crit / 150-190 warn"
band from the Hetzner *container* fleet, where a cgroup pids.max enforced a
real ~190 PID ceiling. THIS box is a 2-core / 3.7GB KVM VM with NO cgroup PID
cap (kernel.pid_max=4194304, ulimit -u≈15127). System-wide /proc PID counts of
~180 are completely normal here and do NOT indicate pressure. Throttling on
that phantom constraint floored concurrency to 2 regardless of real headroom.

New stance:
  - PRIMARY limiter  = available RAM (each claude agent ≈ PER_AGENT_MB).
  - SECONDARY limiter = CPU load (don't exceed ~cpu_count CPU-heavy agents).
  - PID limiter is CGROUP/ULIMIT-AWARE: only gates when a *real* cap exists
    (cgroup pids.max as an integer) or the per-user RLIMIT_NPROC headroom is
    genuinely tight. On a host with no cap, PIDs never force the floor.

Design stance: still CONSERVATIVE on REAL signals. When a genuine pressure
signal fires (RAM below the OS reserve + one agent, real cgroup/ulimit
exhaustion, or very high load), return the floor. But do NOT floor on phantom
constraints. It is cheap to under-spawn; it is also wasteful to floor a box
that has 1.5 GB of free RAM.

Signals consulted
-----------------
- RAM:   /proc/meminfo MemAvailable (psutil used only if present; soft dep).
- CPU:   os.getloadavg() compared against os.cpu_count() (load per-core).
- PIDs:  cgroup pids.max/pids.current if a real integer cap is present;
         otherwise per-user RLIMIT_NPROC headroom vs counted user processes.

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
import resource
from dataclasses import dataclass, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Tunable module constants
# ---------------------------------------------------------------------------

# RAM (PRIMARY). Reserve this much for the OS + base services before budgeting
# any agents, then allow ~PER_AGENT_MB of available RAM per concurrent agent.
OS_RESERVE_MB = 600              # headroom we never hand out to agents
PER_AGENT_MB = 400               # observed footprint of one claude agent

# CPU (SECONDARY). load-per-core above this is a soft-busy signal that tapers
# the CPU budget toward the floor; at/above HARD it forces the floor.
LOAD_SOFT_PER_CORE = 0.9         # begin tapering CPU budget
LOAD_HARD_PER_CORE = 1.75        # genuine overload -> floor

# PID handling. Only meaningful when a REAL cap exists.
#   - cgroup: reserve this many PIDs below pids.max before budgeting.
#   - ulimit: reserve this many below RLIMIT_NPROC before budgeting.
# Each remaining PID is divided by PIDS_PER_AGENT to estimate an agent budget.
CGROUP_PID_RESERVE = 40
ULIMIT_PID_RESERVE = 200         # generous; ulimit caps are usually huge
PIDS_PER_AGENT = 12              # rough PIDs spawned per agent/team

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
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().available / (1024 * 1024)
    except Exception:
        pass
    try:
        with open("/proc/meminfo", "r") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    kb = float(line.split()[1])
                    return kb / 1024.0
    except (OSError, ValueError, IndexError):
        pass
    return None


def _read_int_file(path: str) -> Optional[int]:
    """Read a single integer from a sysfs/cgroup file. Returns None on any miss
    or on the literal 'max' (meaning: no cap)."""
    try:
        with open(path, "r") as fh:
            raw = fh.read().strip()
    except OSError:
        return None
    if raw == "" or raw == "max":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _cgroup_pid_cap() -> Optional[tuple]:
    """
    Detect a REAL cgroup PID cap.

    Returns (pids_max, pids_current) if an integer cap is present (cgroup v2 or
    v1), else None. A value of "max" (no cap) returns None — we treat that as
    'no cgroup limiter here', not as a constraint.
    """
    # cgroup v2 (unified)
    pmax = _read_int_file("/sys/fs/cgroup/pids.max")
    if pmax is not None:
        pcur = _read_int_file("/sys/fs/cgroup/pids.current")
        return (pmax, pcur if pcur is not None else 0)
    # cgroup v1
    pmax = _read_int_file("/sys/fs/cgroup/pids/pids.max")
    if pmax is not None:
        pcur = _read_int_file("/sys/fs/cgroup/pids/pids.current")
        return (pmax, pcur if pcur is not None else 0)
    return None


def _ulimit_nproc() -> Optional[int]:
    """Soft RLIMIT_NPROC for the current user. None if unlimited/unknown."""
    try:
        soft, _hard = resource.getrlimit(resource.RLIMIT_NPROC)
    except (ValueError, OSError, AttributeError):
        return None
    if soft is None or soft < 0 or soft == resource.RLIM_INFINITY:
        return None
    return int(soft)


def _user_proc_count() -> Optional[int]:
    """
    Count processes owned by the CURRENT user (not system-wide).

    This is the honest denominator for ulimit headroom: RLIMIT_NPROC is a
    per-user cap, so a system-wide /proc count would be misleading.
    """
    try:
        my_uid = os.getuid()
    except AttributeError:
        return None
    count = 0
    try:
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            try:
                st = os.stat(f"/proc/{entry}")
            except OSError:
                continue
            if st.st_uid == my_uid:
                count += 1
        return count
    except OSError:
        return None


def _system_pid_count() -> Optional[int]:
    """Total /proc PID count — observability only, NOT a gating signal here."""
    try:
        return sum(1 for n in os.listdir("/proc") if n.isdigit())
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Signals + headroom report (observability)
# ---------------------------------------------------------------------------

@dataclass
class Signals:
    cpu_count: int
    load_1min: float
    load_per_core: float
    mem_avail_mb: Optional[float]
    cgroup_pid_cap: Optional[int]      # pids.max if a real cap, else None
    cgroup_pid_current: Optional[int]
    ulimit_nproc: Optional[int]
    user_proc_count: Optional[int]
    system_pid_count: Optional[int]    # observability only


def _collect_signals() -> Signals:
    cpu = _cpu_count()
    load = _load_1min()
    mem = _mem_avail_mb()
    cg = _cgroup_pid_cap()
    cg_max = cg[0] if cg else None
    cg_cur = cg[1] if cg else None
    return Signals(
        cpu_count=cpu,
        load_1min=round(load, 3),
        load_per_core=round(load / cpu, 3) if cpu else load,
        mem_avail_mb=round(mem, 1) if mem is not None else None,
        cgroup_pid_cap=cg_max,
        cgroup_pid_current=cg_cur,
        ulimit_nproc=_ulimit_nproc(),
        user_proc_count=_user_proc_count(),
        system_pid_count=_system_pid_count(),
    )


def headroom_report() -> dict:
    """
    Return live signals AND the chosen per-resource budgets, for honest
    observability. Includes mem_avail_mb, the ram/load/pid budgets, whether a
    real cgroup pid cap was detected, and user_proc_count (not just the
    system-wide pid_count).
    """
    s = _collect_signals()
    floor, ceiling = 2, 10
    ram_b = _ram_budget(s.mem_avail_mb, floor=floor, ceiling=ceiling)
    load_b = _load_budget(s.load_1min, s.cpu_count, floor=floor, ceiling=ceiling)
    pid_b, pid_cap_detected = _pid_budget(
        cgroup_pid_cap=s.cgroup_pid_cap,
        cgroup_pid_current=s.cgroup_pid_current,
        ulimit_nproc=s.ulimit_nproc,
        user_proc_count=s.user_proc_count,
        floor=floor, ceiling=ceiling,
    )
    d = asdict(s)
    d.update({
        "ram_budget": ram_b,
        "load_budget": load_b,
        "pid_budget": pid_b,
        "cgroup_pid_cap_detected": pid_cap_detected,
        "recommended_concurrency": _compute_concurrency(
            cpu_count=s.cpu_count,
            load_1min=s.load_1min,
            mem_avail_mb=s.mem_avail_mb,
            cgroup_pid_cap=s.cgroup_pid_cap,
            cgroup_pid_current=s.cgroup_pid_current,
            ulimit_nproc=s.ulimit_nproc,
            user_proc_count=s.user_proc_count,
            floor=floor, ceiling=ceiling,
        ),
        "budget_constants": {
            "OS_RESERVE_MB": OS_RESERVE_MB,
            "PER_AGENT_MB": PER_AGENT_MB,
            "LOAD_SOFT_PER_CORE": LOAD_SOFT_PER_CORE,
            "LOAD_HARD_PER_CORE": LOAD_HARD_PER_CORE,
        },
    })
    return d


# ---------------------------------------------------------------------------
# Per-resource budget helpers (pure — explicit values in, int out)
# ---------------------------------------------------------------------------

def _ram_budget(mem_avail_mb: Optional[float], *, floor: int, ceiling: int) -> int:
    """
    PRIMARY budget. ram_agents = max(0, (mem_avail - OS_RESERVE) // PER_AGENT).
    Unknown RAM -> conservative floor. Clamped to ceiling.
    """
    if mem_avail_mb is None:
        return floor
    usable = mem_avail_mb - OS_RESERVE_MB
    if usable < PER_AGENT_MB:
        return 0  # not even one agent's worth of headroom -> real pressure
    return min(ceiling, int(usable // PER_AGENT_MB))


def _load_budget(load_1min: float, cpu_count: int, *, floor: int, ceiling: int) -> int:
    """
    SECONDARY budget. Cap at ~cpu_count CPU-heavy agents. Taper from full
    cpu_count (at load_per_core <= SOFT) down toward floor as load climbs to
    HARD. At/above HARD -> floor.
    """
    cpu_count = max(1, cpu_count)
    lpc = load_1min / cpu_count
    if lpc >= LOAD_HARD_PER_CORE:
        return floor
    if lpc <= LOAD_SOFT_PER_CORE:
        return min(ceiling, cpu_count)
    # Linear taper between SOFT and HARD.
    span = LOAD_HARD_PER_CORE - LOAD_SOFT_PER_CORE
    frac = (LOAD_HARD_PER_CORE - lpc) / span  # 1.0 at soft -> 0.0 at hard
    budget = floor + int(round((cpu_count - floor) * max(0.0, frac)))
    return max(floor, min(ceiling, budget))


def _pid_budget(
    *,
    cgroup_pid_cap: Optional[int],
    cgroup_pid_current: Optional[int],
    ulimit_nproc: Optional[int],
    user_proc_count: Optional[int],
    floor: int,
    ceiling: int,
) -> tuple:
    """
    CGROUP/ULIMIT-AWARE PID budget.

    Returns (budget, real_cap_detected).

    - If a REAL cgroup pids.max integer exists, gate on
      (pids.max - pids.current - reserve) // PIDS_PER_AGENT.  real_cap=True.
    - Else fall back to per-user RLIMIT_NPROC headroom:
      (ulimit - user_proc_count - reserve) // PIDS_PER_AGENT.  real_cap=False.
    - If neither yields a meaningful integer, PIDs are NOT a limiter:
      return ceiling so min() ignores them.  real_cap=False.

    Crucially: a host with no cgroup cap and a huge ulimit will NOT be floored
    just because the system-wide /proc count is high.
    """
    # Real cgroup cap takes precedence.
    if cgroup_pid_cap is not None:
        cur = cgroup_pid_current if cgroup_pid_current is not None else 0
        remaining = cgroup_pid_cap - cur - CGROUP_PID_RESERVE
        budget = max(0, remaining // PIDS_PER_AGENT)
        return (min(ceiling, budget), True)

    # Fall back to per-user ulimit headroom.
    if ulimit_nproc is not None and user_proc_count is not None:
        remaining = ulimit_nproc - user_proc_count - ULIMIT_PID_RESERVE
        if remaining <= 0:
            # Genuine per-user exhaustion (rare).
            return (0, False)
        budget = remaining // PIDS_PER_AGENT
        # On typical hosts ulimit is huge -> budget >> ceiling -> not a limiter.
        return (min(ceiling, budget), False)

    # No real signal -> PIDs do not limit.
    return (ceiling, False)


# ---------------------------------------------------------------------------
# Core decision logic (pure function over explicit signal values — testable)
# ---------------------------------------------------------------------------

def _compute_concurrency(
    *,
    cpu_count: int,
    load_1min: float,
    mem_avail_mb: Optional[float],
    cgroup_pid_cap: Optional[int] = None,
    cgroup_pid_current: Optional[int] = None,
    ulimit_nproc: Optional[int] = None,
    user_proc_count: Optional[int] = None,
    floor: int,
    ceiling: int,
) -> int:
    """
    Pure mapping from explicit signal values -> concurrency in [floor, ceiling].

    Takes NO live readings — callers (or tests) inject values. Deterministically
    verifiable.

    recommended = min(ram_budget, load_budget, pid_budget, ceiling),
                  clamped to [floor, ceiling].

    Hard-floor ONLY on a REAL pressure signal:
      - mem_avail < OS_RESERVE_MB + PER_AGENT_MB (can't afford even one agent)
      - genuine cgroup/ulimit PID exhaustion (pid_budget == 0)
      - load_per_core >= LOAD_HARD_PER_CORE
    Phantom signals (high system /proc count with no real cap) do NOT floor.
    """
    if floor < 1:
        floor = 1
    if ceiling < floor:
        ceiling = floor
    cpu_count = max(1, cpu_count)

    ram_b = _ram_budget(mem_avail_mb, floor=floor, ceiling=ceiling)
    load_b = _load_budget(load_1min, cpu_count, floor=floor, ceiling=ceiling)
    pid_b, _real_cap = _pid_budget(
        cgroup_pid_cap=cgroup_pid_cap,
        cgroup_pid_current=cgroup_pid_current,
        ulimit_nproc=ulimit_nproc,
        user_proc_count=user_proc_count,
        floor=floor, ceiling=ceiling,
    )

    # --- Real hard-floor conditions --------------------------------------
    # Can't afford even one agent's RAM beyond the OS reserve.
    if ram_b == 0:
        return floor
    # Genuine PID exhaustion (real cap fully consumed).
    if pid_b == 0:
        return floor
    # Genuine CPU overload.
    if (load_1min / cpu_count) >= LOAD_HARD_PER_CORE:
        return floor

    recommended = min(ram_b, load_b, pid_b, ceiling)
    recommended = max(floor, recommended)
    return int(recommended)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommended_concurrency(floor: int = 2, ceiling: int = 10) -> int:
    """
    How many parallel agents are safe RIGHT NOW, clamped to [floor, ceiling].

    PRIMARY = RAM headroom; SECONDARY = CPU load; PID gating is cgroup/ulimit
    aware (no phantom throttling on hosts without a real PID cap).
    """
    s = _collect_signals()
    return _compute_concurrency(
        cpu_count=s.cpu_count,
        load_1min=s.load_1min,
        mem_avail_mb=s.mem_avail_mb,
        cgroup_pid_cap=s.cgroup_pid_cap,
        cgroup_pid_current=s.cgroup_pid_current,
        ulimit_nproc=s.ulimit_nproc,
        user_proc_count=s.user_proc_count,
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
    reduced the desired count, log WHY (the raw headroom signals + budgets).
    """
    if desired_n < 0:
        desired_n = 0
    rec = recommended_concurrency(floor, ceiling)
    allowed = min(desired_n, rec)
    if allowed < desired_n:
        s = _collect_signals()
        log.warning(
            "concurrency throttled: desired=%d -> allowed=%d (rec=%d) | "
            "load_per_core=%.3f mem_avail_mb=%s cgroup_pid_cap=%s "
            "user_procs=%s ulimit=%s cpu=%d",
            desired_n, allowed, rec,
            s.load_per_core, s.mem_avail_mb, s.cgroup_pid_cap,
            s.user_proc_count, s.ulimit_nproc, s.cpu_count,
        )
    return allowed


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _selftest(floor: int = 2, ceiling: int = 10) -> int:
    print("=" * 68)
    print("CONCURRENCY GOVERNOR — SELFTEST (RAM-primary, cgroup/ulimit-aware)")
    print("=" * 68)

    # 1) Live headroom report ------------------------------------------------
    report = headroom_report()
    print("\n[1] headroom_report() — live signals + budgets:")
    for k, v in report.items():
        print(f"      {k:24} = {v}")

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

    # 4) low-RAM (512MB) -> floor -------------------------------------------
    print("\n[4] low-RAM(512MB) -> floor:")
    n = _compute_concurrency(
        cpu_count=8, load_1min=0.1, mem_avail_mb=512.0,
        cgroup_pid_cap=None, ulimit_nproc=15000, user_proc_count=40,
        floor=floor, ceiling=ceiling,
    )
    print(f"      low_ram(512MB) -> {n}")
    assert n == floor, f"expected floor={floor}, got {n}"
    print(f"      OK: insufficient RAM clamps to floor={floor}")

    # 5) ample-RAM + low-load + no-cap -> approaches ceiling -----------------
    print("\n[5] ample-RAM(8000MB) + low-load + NO cgroup cap -> approaches ceiling:")
    ample = float(OS_RESERVE_MB + PER_AGENT_MB * (ceiling + 6))  # > ceiling worth
    n_hi = _compute_concurrency(
        cpu_count=16, load_1min=0.0, mem_avail_mb=ample,
        cgroup_pid_cap=None, ulimit_nproc=15000, user_proc_count=40,
        floor=floor, ceiling=ceiling,
    )
    print(f"      ample_ram({ample:.0f}MB) -> {n_hi} (ceiling={ceiling})")
    assert n_hi == ceiling, f"expected ceiling={ceiling}, got {n_hi}"
    print(f"      OK: abundant RAM + cores reaches ceiling={ceiling}")

    # 6) cgroup cap present AND tight -> throttles --------------------------
    print("\n[6] cgroup pids.max present and TIGHT -> throttles below ceiling:")
    # cap=190, current=180 -> remaining=190-180-40 = -30 -> budget 0 -> floor.
    n_tight = _compute_concurrency(
        cpu_count=16, load_1min=0.0, mem_avail_mb=8000.0,
        cgroup_pid_cap=190, cgroup_pid_current=180,
        ulimit_nproc=15000, user_proc_count=180,
        floor=floor, ceiling=ceiling,
    )
    print(f"      cgroup cap=190 cur=180 -> {n_tight}")
    assert n_tight == floor, f"expected floor={floor}, got {n_tight}"
    # cap=300, current=120 -> remaining=300-120-40=140 -> 140//12=11 -> ceiling.
    n_room = _compute_concurrency(
        cpu_count=16, load_1min=0.0, mem_avail_mb=8000.0,
        cgroup_pid_cap=300, cgroup_pid_current=120,
        ulimit_nproc=15000, user_proc_count=120,
        floor=floor, ceiling=ceiling,
    )
    print(f"      cgroup cap=300 cur=120 -> {n_room}")
    assert n_room == ceiling, f"expected ceiling={ceiling}, got {n_room}"
    print("      OK: real cgroup cap gates; loose cap does not")

    # 7) no cgroup cap -> PID is NOT a limiter even with high system PIDs ----
    print("\n[7] NO cgroup cap + huge ulimit -> PIDs are NOT a limiter:")
    # This mirrors THIS box: no cap, ulimit≈15127, ~180 system PIDs / ~43 user.
    # With ample RAM + low load it must reach ceiling, NOT floor.
    n_nopid = _compute_concurrency(
        cpu_count=16, load_1min=0.0, mem_avail_mb=ample,
        cgroup_pid_cap=None, cgroup_pid_current=None,
        ulimit_nproc=15127, user_proc_count=43,
        floor=floor, ceiling=ceiling,
    )
    print(f"      no_cap, ulimit=15127, user_procs=43 -> {n_nopid}")
    assert n_nopid == ceiling, (
        f"PIDs must not floor without a real cap; expected ceiling={ceiling}, "
        f"got {n_nopid}"
    )
    # Even with NO cgroup AND no ulimit info, PIDs must not floor.
    n_nopid2 = _compute_concurrency(
        cpu_count=16, load_1min=0.0, mem_avail_mb=ample,
        cgroup_pid_cap=None, cgroup_pid_current=None,
        ulimit_nproc=None, user_proc_count=None,
        floor=floor, ceiling=ceiling,
    )
    print(f"      no_cap, no ulimit info -> {n_nopid2}")
    assert n_nopid2 == ceiling, f"expected ceiling={ceiling}, got {n_nopid2}"
    print("      OK: phantom PID pressure does NOT throttle")

    # 8) genuine CPU overload -> floor --------------------------------------
    print("\n[8] genuine CPU overload (load_per_core >= HARD) -> floor:")
    n_load = _compute_concurrency(
        cpu_count=2, load_1min=4.0, mem_avail_mb=ample,
        cgroup_pid_cap=None, ulimit_nproc=15000, user_proc_count=40,
        floor=floor, ceiling=ceiling,
    )
    print(f"      load=4.0 on 2 cores (lpc=2.0) -> {n_load}")
    assert n_load == floor, f"expected floor={floor}, got {n_load}"
    print(f"      OK: real overload clamps to floor={floor}")

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

    print(recommended_concurrency(args.floor, args.ceiling))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
