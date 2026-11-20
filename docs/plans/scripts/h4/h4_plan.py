"""H4 (the re-baseline, the restart plan's Wave 4): its seed count J and its run plan, printed from declared constants
and the calendar only -- no bar, no outcome, no result file, no random number, no seed value (seeds are named by role;
their values are the draft's section 15). `prereg/DRAFT_H4_rebaseline.md` holds this script's output between its
markers, line for line (`tests/test_h4_draft.py`).

**J, H4's coin seeds on the search years** (the draft's section 7). W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md` at
wt/wt-infra 2bde318) reads H4's per-seed composites: a gap between two adjacent baselines is *resolved* when it exceeds
`RESOLVE_Z` times its coin-noise standard error over H4's seeds (its 5.1), and the size that matters is never below
`DELTA_MIN`. H4's J is set so that a true gap of `DELTA_MIN` is resolved with probability `POWER`: the three-way
note's 2.5 form n >= ((c + z_pi) / delta)^2 with c = `RESOLVE_Z` (W42-R1's resolution line in place of the test's
c_h), and W42-R1 5.3's variance Q = 1 / (J n) at the horizon with the fewest complete starts (Q's largest value: Q is
convex in the weights, so its worst case is all weight on the smallest E_h; every per-unit difference lies in [-1, 1],
so its standard deviation is at most one). n is taken at a lower bound of the search years' sessions (the weekdays less
`HOLIDAYS_A_YEAR` a year), so J is not short when holidays thin the calendar; J is then rounded up to a power of two, so
H3-D can cut H4's seeds into disjoint seed sets of any power-of-two size m.

**The work** is lane-trades (arm-runs x seeds x starts x horizon x trades a session, `three_way_arith.lane_trades`),
with U1's exact-length runs (`EXACT`, read from the vendored `user_journey.py`) on every start of the `off` arm-runs and
on every `EXACT_EVERY`-th start of the stress arms; the hours are at the note's assumed costs, never a measurement --
H4-0 measures the firm path's real cost a lane-trade (the race's and R-10's walk's terms) and the vendored replay's
cost a start, and the cut rule is applied at those costs and at H4-S's counted supply before any part starts.

    python docs/plans/scripts/h4/h4_plan.py
"""
from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
VENDORED_U1 = ROOT / "vendor" / "stage2" / "propedge" / "research" / "user_journey.py"


def _arith():
    spec = importlib.util.spec_from_file_location("three_way_arith_for_h4_plan", ARITH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _arith()


def _vendored_exact() -> tuple[int, ...]:
    """U1's exact-length horizons, `EXACT` of the vendored `propedge/research/user_journey.py` (D-620 (3)(f)), read
    from its source (nothing vendored is imported or edited)."""
    tree = ast.parse(VENDORED_U1.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXACT" for t in node.targets):
            return tuple(int(v) for v in ast.literal_eval(node.value))
    raise RuntimeError("the vendored user_journey.py defines no EXACT")


#: W42-R1's constants H4's J reads (WAVE42_SETTING_RULE.md section 2 at wt/wt-infra 2bde318; `tests/test_h4_draft.py`
#: holds each equal to `extended/wave42.py` at that commit)
W42_COMMIT = "2bde318"
RESOLVE_Z = 2.0
DELTA_MIN = 0.01
POWER = A.POWER                       # W42-R1's POWER_TARGET, `family_stats.MDL_POWER`
W42_W = 126                           # W42-R1's first-payout window W
#: H4's windows W (the brief): W42-R1's, and the twelve-month window beside it
WINDOWS = (W42_W, 252)
#: the horizons W42-R1's dimensions sit at (its 4.1): P_B at months 1-3, the W-window measures, the twelve-month ones
DIM_HORIZONS = (63, W42_W, 252)
#: at most this many weekdays a search year are not sessions (exchange holidays): the sessions' lower bound
HOLIDAYS_A_YEAR = 12
SEARCH_YEARS = 4                      # 2020 to 2023 (E-208)
EXACT = _vendored_exact()
#: `extended/user_beside.py`'s EXACT_EVERY (held equal by the test): the stress arms' exact-run spacing
EXACT_EVERY = 21
#: the baselines, in W42-R1's order (its BASELINES; the runner's)
BASELINES = ("naive_coin", "p14", "p15", "p16")
#: each baseline's arm-runs through the firm path: (name, reading, exact runs on every start)
ARM_RUNS = (("off", "deciding", True), ("off", "as-walked, beside", True),
            ("worse_1", "deciding", False), ("missed_0.1", "deciding", False))
#: the registered designs H4-A replays as traded (the naive coin has no registered replay)
AS_TRADED = ("p14", "p15", "p16")
#: starts in one lockstep batch: the lanes a batch are J x this
BATCH_STARTS = 21


def sessions_upper() -> int:
    return A.weekdays(*A.SEARCH)


def sessions_lower() -> int:
    return sessions_upper() - HOLIDAYS_A_YEAR * SEARCH_YEARS


def units_needed() -> int:
    """Start-seed units n at which a true gap of DELTA_MIN clears RESOLVE_Z standard errors with probability POWER."""
    return math.ceil(((RESOLVE_Z + A.z(POWER)) / DELTA_MIN) ** 2)


def j_needed() -> int:
    """At the strictest horizon's complete starts, from the sessions' lower bound."""
    n = A.complete_starts(sessions_lower(), max(DIM_HORIZONS))
    return -(-units_needed() // n)


def j_h4() -> int:
    """The next power of two at or above `j_needed()`."""
    return 1 << (j_needed() - 1).bit_length()


def resolvable_gap(J: int, n: int) -> float:
    """The gap resolved with probability POWER at J seeds and n complete starts (Q = 1 / (J n), sd at most one)."""
    return (RESOLVE_Z + A.z(POWER)) / math.sqrt(J * n)


def exact_factor(every_start: bool) -> float:
    """The exact-length runs' work, in long runs of the largest window."""
    share = sum(EXACT) / max(WINDOWS)
    return 1.0 + (share if every_start else share / EXACT_EVERY)


def part_work(J: int) -> int:
    """One baseline's H4-B part: every arm-run, every start (the weekday bound), the largest window, the toys' supply."""
    T, h = sessions_upper(), max(WINDOWS)
    return int(round(sum(A.lane_trades(1, 1, J, T, h) * exact_factor(every) for _, _, every in ARM_RUNS)))


def replays_a() -> int:
    """H4-A's vendored replays, in long-run units: every start of every registered design, with every exact run."""
    return int(round(len(AS_TRADED) * sessions_upper() * exact_factor(True)))


def c_max_us(work: int) -> float:
    return A.PART_CAP_H * 3600.0 * 1e6 * A.WORKERS / work


def report() -> str:
    J, Jn = j_h4(), j_needed()
    up, lo = sessions_upper(), sessions_lower()
    out = ["H4's seed count J (section 7): a true gap of DELTA_MIN resolved at RESOLVE_Z standard errors with "
           "probability POWER, at W42-R1's worst-case variance Q = 1 / (J n)"]
    out.append(f"  W42-R1 at {W42_COMMIT}: RESOLVE_Z={RESOLVE_Z:g} DELTA_MIN={DELTA_MIN:g} POWER={POWER:g} "
               f"(z={A.z(POWER):.4f}); units needed n = ((RESOLVE_Z + z) / DELTA_MIN)^2 = {units_needed()}")
    out.append(f"  search-year sessions: at most {up} (weekdays {A.SEARCH[0]} to {A.SEARCH[1]}), at least {lo} "
               f"(less {HOLIDAYS_A_YEAR} a year)")
    for h in DIM_HORIZONS:
        out.append(f"  complete starts at h={h}: {A.complete_starts(lo, h)} to {A.complete_starts(up, h)}")
    out.append(f"  J_needed = ceil(n / complete starts at h={max(DIM_HORIZONS)}, lower) = {Jn}; "
               f"J_H4 = the next power of two = {J}")
    for h in DIM_HORIZONS:
        out.append(f"  at J_H4, h={h}: gap resolved with probability POWER from "
                   f"{resolvable_gap(J, A.complete_starts(up, h)):.4f} to "
                   f"{resolvable_gap(J, A.complete_starts(lo, h)):.4f}")
    out.append(f"  sigma's relative standard error at J_H4 (a normal sd from J seeds, per start day): "
               f"{1.0 / math.sqrt(2.0 * (J - 1)):.4f}")
    out.append(f"H4's heavy slots: part | reads | work | hours over {A.WORKERS} workers at the assumed costs "
               + ", ".join(f"{c} us" for c in A.COSTS_US) + f" a lane-trade | c_max (fits {A.PART_CAP_H:g} h)")
    probe = A.lane_trades(1, 1, 64, 40, 63)
    out.append(f"  H4-0 probe        | synthetic toys; the vendored replay timed on P-14's first {EXACT_EVERY} "
               f"search-year starts, nothing kept | {probe:.3e} lane-trades | "
               + "  ".join(f"{A.hours(probe, c):.1f}" for c in A.COSTS_US) + f" | c_max={c_max_us(probe):.2f} us")
    out.append(f"  H4-S schedules    | the search years' bars and registered trades through the cut | not "
               f"lane-trades: timed in its log, under the {A.PART_CAP_H:g} h cap")
    ra = replays_a()
    out.append(f"  H4-A as traded    | {', '.join(AS_TRADED)} by user_beside.run_starts, journey_block search | "
               f"{ra} long-run replays | c_max={A.PART_CAP_H * 3600.0 * A.WORKERS / ra:.2f} s a replay")
    w = part_work(J)
    for b in BASELINES:
        out.append(f"  H4-B {b:<12} | the firm path, J={J} seeds, {len(ARM_RUNS)} arm-runs "
                   f"({'; '.join(f'{n} {r}' for n, r, _ in ARM_RUNS)}) | {w:.3e} lane-trades | "
                   + "  ".join(f"{A.hours(w, c):.1f}" for c in A.COSTS_US) + f" | c_max={c_max_us(w):.2f} us")
    lanes = J * BATCH_STARTS
    out.append(f"memory: cap {A.MEM_CAP_GB} GB over {A.WORKERS} workers, base {A.BASE_GB} GB assumed (H4-0 measures "
               f"it), lane {A.LANE_BYTES} B: at most {A.max_lanes()} lanes a worker; a batch of {BATCH_STARTS} starts "
               f"x J = {lanes} lanes")
    out.append(f"the cut rule: a part runs only if H4-0's measured cost (the race's and the walks' terms at H4-S's "
               f"time-limited share and mean steps) times H4-S's counted supply fits {A.PART_CAP_H:g} h; otherwise "
               f"it is split by disjoint start ranges, never by seeds, in the lead's sizing row before it starts")
    out.append("the crash rule: no reading is made until every part completes; a crashed part is re-run whole from its "
               "declared seeds, never resumed; each crash is recorded in the part ledger (E-195)")
    return "\n".join(out)


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
