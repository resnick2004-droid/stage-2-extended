"""Q-153: the arithmetic of the three-way test's design note (`docs/plans/THREE_WAY_TEST_design.md`) -- no bar, no
market outcome, no result file, no random number. Every figure the note states is printed here from declared constants
and the calendar only:

- the family level 0.05 / (k (k + 1)) (E-001, CHARTER 3.7) at k = 13, the next k, and the three after it;
- the search and held-out years' dates (E-208), whose weekday counts (`numpy.busday_count`, every Monday to Friday,
  holidays included) bound the session counts from above: no session list is read, so every count derived from them
  is an upper bound ("at most");
- the horizons a measure can read (21, 63, 126, 252 sessions: a month is 21 sessions, CHARTER 2);
- the empirical-Bernstein bound's constants (Maurer and Pontil 2009, theorem 4) and the normal quantiles;
- the rule of three's form (zero rejections in n replications put a 95 % upper limit on the rate).

    python docs/plans/scripts/three_way/three_way_arith.py

`report()` returns the text `main()` prints; `tests/test_three_way_design.py` holds the note's fenced arithmetic block
to it, line for line."""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

#: k = 13 is the next family's (CLAUDE.md, CHARTER 3.7); the others are the next four, for a repeat at a new level
KS = (13, 14, 15, 16, 17)
#: E-208's split (the held-out years end the day before the confirmation window, 2026-07-17)
SEARCH = ("2020-01-02", "2023-12-29")
HELD_OUT = ("2024-01-02", "2026-07-16")
HORIZONS = (21, 63, 126, 252)
#: the power target proposed for the pinning row (the repository's convention, `family_stats.MDL_POWER`)
POWER = 0.8
#: the feasible levels at which a size is checked empirically (section 2.6 of the note)
FEASIBLE = (0.05, 0.01, 0.001)
#: the time leg's block counts tabulated (section 3.4 of the note)
BLOCKS = tuple(range(1, 11))
#: the range term's illustration: delta / R (the size that matters over the composite's half-range) and the share of
#: delta the range term may take (section 2.5 of the note); delta is the operator's (O-3), so these only show
#: the formula
DELTA_OVER_R = (0.01, 0.02, 0.05)
RANGE_SHARE = 0.1

#: the machine's limits (CLAUDE.md, DIRECTIVE): one heavy job at a time, at most two workers, under 2.5 GB in all
MEM_CAP_GB, WORKERS = 2.5, 2
#: one lane's state, in bytes, as the note's section 6.2 declares it: up to 8 accounts x 16 float64 fields, plus 40
#: float64 of per-start reductions
LANE_BYTES = 8 * 16 * 8 + 40 * 8
#: a process's base (interpreter, numpy, pandas, scipy, the engine, one history) assumed for the arithmetic; H3-0's
#: probe measures it and replaces this assumption
BASE_GB = 0.4
#: the per-lane-trade costs tabulated (microseconds): assumptions spanning a purpose-built lockstep to a slow engine,
#: never a measurement; H3-0's probe measures the real one
COSTS_US = (0.05, 0.5, 5.0)
#: trades per session at most (the declared supply cap of the toys; a design search declares its own)
TAU = 4
#: H3's parts, proposed sizes for H3's declaration: (part, histories R, arm-runs per history, seed replicates per arm
#: M, starts per history |T|, horizon in sessions)
PARTS = (
    ("A1 same-design nulls", 20, 3, 10_000, 120, 63),
    ("A2 exact-centred toy null", 20, 2, 10_000, 120, 63),
    ("A3 history null", 200, 2, 2_000, 120, 63),
    ("A4 end-to-end plants", 10, 6, 10_000, 120, 63),
    ("D1 same-design nulls", 20, 3, 2_000, 601, 252),
    ("D2 history null", 200, 2, 500, 601, 252),
    ("D3 power gate plants", 10, 6, 2_000, 601, 252),
)
#: a part whose estimate exceeds this many hours at the probe's cost is cut (M first) before it starts
PART_CAP_H = 8.0


def level(k: int) -> float:
    """The family level 0.05 / (k (k + 1))."""
    return 0.05 / (k * (k + 1))


def b_min(alpha: float) -> int:
    """The fewest independent sign units an exact sign-flip test needs to reach `alpha`: its smallest p-value over B
    units is 2^-B (one pattern of 2^B), so B >= ceil(log2(1 / alpha))."""
    return math.ceil(math.log2(1.0 / alpha))


def weekdays(first: str, last: str) -> int:
    """Monday-to-Friday days from `first` to `last`, both included: an upper bound on the sessions between them."""
    end = (np.datetime64(last) + np.timedelta64(1, "D"))
    return int(np.busday_count(np.datetime64(first), end))


def disjoint_units(n: int, h: int) -> int:
    """The most units whose h-session windows share no session, in n sessions: floor(n / h)."""
    return n // h


def complete_starts(n: int, h: int) -> int:
    """Starts complete at horizon h in n sessions (the start and the next h - 1 sessions inside): n - h + 1."""
    return max(0, n - h + 1)


def start_blocks(n: int, h: int) -> int:
    """Blocks of h consecutive complete starts (block length = horizon; only adjacent blocks share sessions)."""
    return complete_starts(n, h) // h


def eb_constants(alpha: float) -> tuple[float, float]:
    """Maurer-Pontil's one-sided bound for i.i.d. values in [0, 1]:
    mean - sqrt(2 V ln(2/a) / n) - 7 ln(2/a) / (3 (n-1)), V the unbiased sample variance;
    returned (sqrt(2 ln(2/a)), 7 ln(2/a) / 3)."""
    lg = math.log(2.0 / alpha)
    return math.sqrt(2.0 * lg), 7.0 * lg / 3.0


def z(p: float) -> float:
    """The standard normal's p quantile."""
    return float(stats.norm.ppf(p))


def seed_factor(alpha: float, power: float = POWER, exact: bool = True) -> float:
    """(c + z_power)^2: the replicates needed per unit of (sigma / delta)^2 for `power` at `alpha`, the range term
    left out -- c the empirical-Bernstein variance constant (`exact`) or the normal quantile z_(1-alpha)."""
    c = eb_constants(alpha)[0] if exact else z(1.0 - alpha)
    return (c + z(power)) ** 2


def n_certify(alpha: float, conf: float = 0.95) -> int:
    """The fewest replications at which zero rejections put the one-sided `conf` upper limit at or below `alpha`:
    (1 - alpha)^n <= 1 - conf (the rule of three's exact form)."""
    return math.ceil(math.log(1.0 - conf) / math.log(1.0 - alpha))


def binom_tail(B: int, m: int) -> float:
    """P(Bin(B, 1/2) >= m): the chance that at least m of B independent, symmetric block signs are positive."""
    return float(sum(math.comb(B, i) for i in range(m, B + 1)) / 2 ** B)


def range_replicates(delta_over_r: float, alpha: float, share: float = RANGE_SHARE) -> int:
    """The replicates J at which the bound's range term, c2 x 2R / (J - 1) for differences in [-R, R], is at most
    `share` x delta: J >= 1 + 2 c2 / (share x delta / R)."""
    return math.ceil(1.0 + 2.0 * eb_constants(alpha)[1] / (share * delta_over_r))


def lane_trades(R: int, arms: int, M: int, T: int, h: int, tau: int = TAU) -> int:
    """A part's work: histories x arm-runs x seed replicates x starts x (horizon x trades a session)."""
    return R * arms * M * T * h * tau


def hours(work: int, cost_us: float, workers: int = WORKERS) -> float:
    return work * cost_us * 1e-6 / workers / 3600.0


def max_lanes(cap_gb: float = MEM_CAP_GB, workers: int = WORKERS, base_gb: float = BASE_GB,
              lane_bytes: int = LANE_BYTES) -> int:
    """The widest lockstep a worker may run: (cap / workers - base) / lane bytes."""
    return int((cap_gb / workers - base_gb) * 1e9 // lane_bytes)


def report() -> str:
    out: list[str] = []
    out.append("levels: k, 0.05/(k(k+1)), B_min, 2^-B_min, 2^-(B_min-1)")
    for k in KS:
        a = level(k)
        b = b_min(a)
        out.append(f"  k={k}  alpha={a:.4e}  B_min={b}  2^-B_min={2.0 ** -b:.4e}  2^-(B_min-1)={2.0 ** -(b - 1):.4e}")
    wh, ws = weekdays(*HELD_OUT), weekdays(*SEARCH)
    out.append(f"weekdays (upper bounds on sessions): held-out W_H={wh}, search W_S={ws}")
    out.append("per horizon h: disjoint units floor(W/h) held-out | search; complete held-out starts W_H-h+1;"
               " held-out start-blocks of length h; sessions needed for B_min(13) disjoint units")
    b13 = b_min(level(13))
    for h in HORIZONS:
        out.append(f"  h={h:<3}  units_H<={disjoint_units(wh, h):<2}  units_S<={disjoint_units(ws, h):<2}"
                   f"  starts_H<={complete_starts(wh, h):<3}  blocks_H<={start_blocks(wh, h):<2}"
                   f"  sessions_for_{b13}_units={b13 * h}")
    a = level(13)
    c1, c2 = eb_constants(a)
    out.append(f"empirical Bernstein at k=13: c1=sqrt(2 ln(2/alpha))={c1:.4f}  c2=7 ln(2/alpha)/3={c2:.4f}"
               f"  normal z_(1-alpha)={z(1.0 - a):.4f}  z_{POWER}={z(POWER):.4f}")
    fe, fn = seed_factor(a, exact=True), seed_factor(a, exact=False)
    out.append(f"replicates per (sigma/delta)^2 at power {POWER}: exact bound {fe:.3f}, normal t {fn:.3f},"
               f" ratio {fe / fn:.3f}")
    out.append(f"range term at most {RANGE_SHARE} x delta (differences in [-R, R]): replicates J by delta/R")
    for d in DELTA_OVER_R:
        out.append(f"  delta/R={d}  J>={range_replicates(d, a)}")
    out.append("rule of three (zero rejections, 95 % upper limit <= alpha): replications n")
    for lv in FEASIBLE + (a,):
        out.append(f"  alpha={lv:.4e}  n={n_certify(lv)}")
    out.append("time leg, independent symmetric blocks: B, P(all B positive), P(strict majority positive)")
    for B in BLOCKS:
        out.append(f"  B={B:<2}  all={binom_tail(B, B):.4e}  majority={binom_tail(B, B // 2 + 1):.4e}")
    out.append(f"memory: cap {MEM_CAP_GB} GB over {WORKERS} workers, base {BASE_GB} GB assumed, lane {LANE_BYTES} B:"
               f" at most {max_lanes()} lanes a worker")
    out.append(f"run plan (trades a session <= {TAU}; hours over {WORKERS} workers at the assumed costs "
               + ", ".join(f"{c} us" for c in COSTS_US) + " a lane-trade)")
    for name, R, arms, M, T, h in PARTS:
        w = lane_trades(R, arms, M, T, h)
        hs = "  ".join(f"{hours(w, c):.1f}" for c in COSTS_US)
        out.append(f"  {name:<26} R={R:<3} arms={arms} M={M:<6} T={T:<3} h={h:<3} lane-trades={w:.3e}  h: {hs}")
    return "\n".join(out)


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
