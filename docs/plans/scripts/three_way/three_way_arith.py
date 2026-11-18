"""Q-153: the arithmetic of the three-way test's design note (`docs/plans/THREE_WAY_TEST_design.md`) -- no bar, no
market outcome, no result file, no random number. Every figure the note states is printed here from declared constants
and the calendar only:

- the family level 0.05 / (k (k + 1)) (E-001, CHARTER 3.7) at k = 13, the next k, and the four after it;
- the search and held-out years' dates (E-208). Their weekday counts (`numpy.busday_count`, every Monday to Friday,
  holidays included) bound the session counts from above. No session list is read, so every count derived from them
  is an upper bound ("at most");
- the horizons a measure can read (21, 63, 126, 252 sessions: a month is 21 sessions, CHARTER 2), and D-145's gate
  horizon H_g = 504 sessions (`horizon_days: 504` in `vendor/stage2/config/fv2_grid.yaml` and
  `fv3_corrected_portfolio.yaml`);
- the deciding bounds' constants: Hoeffding's (independent terms in [-1, 1]) and the empirical-Bernstein bound's
  (Maurer and Pontil 2009, theorem 4), with the normal quantiles;
- the rule of three's form, and what E-052's criterion can and cannot show at a given count;
- the time conditions' stated size: independent blocks (a binomial tail) and the start-year groups of (Y) with their
  windows' overlap counted, under a white-noise model of the per-session contributions (Gaussian orthant
  probabilities);
- the run plan's work and hours, at assumed costs.

The reference helpers the build follows are also here, and the tests use them: the race redraw (B-1), and the
fixed-length seed key (m-4). They draw nothing.

    python docs/plans/scripts/three_way/three_way_arith.py

`report()` returns the text `main()` prints. `tests/test_three_way_design.py` holds the note's fenced arithmetic block
to it, line for line."""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
from scipy import stats

#: k = 13 is the next family's (CLAUDE.md, CHARTER 3.7); the others are the next four, for a repeat at a new level
KS = (13, 14, 15, 16, 17)
#: E-208's split (the held-out years end the day before the confirmation window, 2026-07-17)
SEARCH = ("2020-01-02", "2023-12-29")
HELD_OUT = ("2024-01-02", "2026-07-16")
#: D-145's gate horizon, as Stage 2's gate campaigns declare it (m-11)
H_GATE = 504
HORIZONS = (21, 63, 126, 252, H_GATE)
#: the power target proposed for the pinning row (the repository's convention, `family_stats.MDL_POWER`)
POWER = 0.8
#: the feasible levels at which a size is checked empirically (section 2.6 of the note)
FEASIBLE = (0.05, 0.01, 0.001)
#: "no laxity detected" with power: the Clopper-Pearson upper limit at most KAPPA x alpha' with probability POWER when
#: the true rate is alpha' (section 2.6)
KAPPA = 2.0
#: the time leg's block counts tabulated (section 3.4 of the note)
BLOCKS = tuple(range(1, 11))
#: the illustrations of delta (the size that matters, on a scale whose differences lie in [-1, 1]); delta is the
#: operator's (O-3), so these only show the formulas
DELTA = (0.01, 0.02, 0.05)
RANGE_SHARE = 0.1
#: the composite's half-range R after clipping (section 2.2: every dimension clipped into [0, 1], weights summing to one)
R_HALF = 1.0

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
#: finalists assumed for the held-out test's cost (the search declares its own)
FINALISTS = 3
BASELINES = 4
#: a part whose estimate exceeds this many hours at the probe's cost is cut (M first) before it starts
PART_CAP_H = 8.0

# --------------------------------------------------------------------------------------- the seed key (m-4)

#: every draw's key is [role seed, kind tag, then exactly the kind's fields]; the tag is nonzero and distinct per kind,
#: so two keys of different kinds differ in their second word and two keys of one kind have one length -- numpy's
#: trailing-zero equivalence (default_rng([a, b]) is default_rng([a, b, 0, 0])) cannot join two keys
KEY_KINDS = {
    "history": (1, ("part", "history")),
    "symmetry": (2, ("part", "history", "block")),
    "coin": (3, ("part", "history", "seed_index", "start", "instrument", "moment", "draw_kind")),
    "plant": (4, ("part", "history", "plant", "replicate")),
    "test": (5, ("test", "replicate")),
}


def seed_key(seed: int, kind: str, **fields: int) -> list[int]:
    """The fixed-length key of one draw: [seed, tag, fields in the kind's order]; every field given, none extra, all
    non-negative integers."""
    tag, names = KEY_KINDS[kind]
    if set(fields) != set(names):
        raise ValueError(f"a {kind} key takes exactly {names}, not {sorted(fields)}")
    vals = [int(fields[n]) for n in names]
    if int(seed) <= 0 or any(v < 0 for v in vals):
        raise ValueError("a seed is positive and every index non-negative")
    return [int(seed), tag, *vals]


def stripped(key) -> tuple[int, ...]:
    """A key as numpy's SeedSequence reads it: trailing zero words carry no entropy, so they are dropped."""
    k = list(key)
    while k and k[-1] == 0:
        k.pop()
    return tuple(k)


# --------------------------------------------------------------------------------------- the race redraw (B-1)


def race_redraw(l: int, g: int, c: int) -> tuple[Fraction, int, int]:
    """(win probability, win, loss) of a trade on the martingale-outcome reading, with stop l, target g and the
    account's cushion c (the room to the nearer barrier: the floor, or the daily loss limit's room), in ticks: a
    driftless first exit races the nearer of the stop and the cushion, as Stage 2's `BinaryDraw` (settlement `race`,
    D-156) does. The loss is min(l, c); a trade with no cushion is not taken."""
    if l <= 0 or g <= 0 or c <= 0:
        raise ValueError("stop, target and cushion are positive tick counts")
    loss = min(l, c)
    return Fraction(loss, loss + g), g, loss


def gross_expectation(p: Fraction, win: int, loss: int) -> Fraction:
    return p * win - (1 - p) * loss


def unraced_edge(l: int, g: int, c: int) -> Fraction:
    """The gross expectation of the defect B-1 names: a win at l / (l + g), the loss clipped at the cushion."""
    p = Fraction(l, l + g)
    return gross_expectation(p, g, min(l, c))


# --------------------------------------------------------------------------------------- levels and units


def level(k: int) -> float:
    """The family level 0.05 / (k (k + 1))."""
    return 0.05 / (k * (k + 1))


def b_min(alpha: float) -> int:
    """The fewest independent sign units an exact sign-flip test needs to reach `alpha`: its smallest p-value over B
    units is 2^-B (one pattern of 2^B), so B >= ceil(log2(1 / alpha))."""
    return math.ceil(math.log2(1.0 / alpha))


def weekday_dates(first: str, last: str) -> np.ndarray:
    """Every Monday to Friday from `first` to `last`, both included (holidays kept): a superset of the sessions."""
    days = np.arange(np.datetime64(first), np.datetime64(last) + np.timedelta64(1, "D"))
    return days[np.is_busday(days)]


def weekdays(first: str, last: str) -> int:
    """Monday-to-Friday days from `first` to `last`, both included: an upper bound on the sessions between them."""
    end = (np.datetime64(last) + np.timedelta64(1, "D"))
    return int(np.busday_count(np.datetime64(first), end))


def disjoint_units(n: int, h: int) -> int:
    """The most units whose h-session windows share no session, in n sessions: floor(n / h)."""
    return n // h


def partial_units(n: int, h: int) -> int:
    """The units counting a final partial one: ceil(n / h)."""
    return -(-n // h)


def complete_starts(n: int, h: int) -> int:
    """Starts complete at horizon h in n sessions (the start and the next h - 1 sessions inside): n - h + 1."""
    return max(0, n - h + 1)


def start_blocks(n: int, h: int) -> int:
    """Blocks of h consecutive complete starts (block length = horizon; only adjacent blocks share sessions)."""
    return complete_starts(n, h) // h


# --------------------------------------------------------------------------------------- the deciding bounds


def hoeffding_constant(alpha: float) -> float:
    """Hoeffding's one-sided bound for the mean of n independent terms in [-1, 1]: mean - sqrt(2 ln(1/alpha) / n);
    returned sqrt(2 ln(1/alpha))."""
    return math.sqrt(2.0 * math.log(1.0 / alpha))


def hoeffding_lower(x, alpha: float) -> float:
    x = np.asarray(x, dtype=float)
    return float(x.mean() - hoeffding_constant(alpha) / math.sqrt(x.size))


def eb_constants(alpha: float) -> tuple[float, float]:
    """Maurer-Pontil's one-sided bound for i.i.d. values in [0, 1]:
    mean - sqrt(2 V ln(2/a) / n) - 7 ln(2/a) / (3 (n-1)), V the unbiased sample variance;
    returned (sqrt(2 ln(2/a)), 7 ln(2/a) / 3)."""
    lg = math.log(2.0 / alpha)
    return math.sqrt(2.0 * lg), 7.0 * lg / 3.0


def eb_lower(x, alpha: float, R: float = R_HALF) -> float:
    """The bound for replicates in [-R, R], applied to (x + R) / (2R) and mapped back."""
    x = np.asarray(x, dtype=float)
    n = x.size
    c2 = eb_constants(alpha)[1]
    return float(x.mean() - math.sqrt(2.0 * x.var(ddof=1) * math.log(2.0 / alpha) / n) - c2 * 2.0 * R / (n - 1))


def z(p: float) -> float:
    """The standard normal's p quantile."""
    return float(stats.norm.ppf(p))


def hoeffding_units(delta: float, alpha: float, power: float = POWER) -> int:
    """The independent units n (start-seed terms, each difference in [-1, 1], sd at most 1) at which Hoeffding's bound
    rejects with probability `power` at true mean delta: sqrt(n) >= (c_h + z_power) / delta."""
    return math.ceil(((hoeffding_constant(alpha) + z(power)) / delta) ** 2)


def eb_range_replicates(delta: float, alpha: float, share: float = RANGE_SHARE, R: float = R_HALF) -> int:
    """The replicates J at which the empirical-Bernstein bound's range term, c2 x 2R / (J - 1), is at most `share` x
    delta: J >= 1 + 2 c2 R / (share x delta). The variance term needs (c1 + z)^2 (sigma / delta)^2 more or less."""
    return math.ceil(1.0 + 2.0 * eb_constants(alpha)[1] * R / (share * delta))


def seed_factor(alpha: float, power: float = POWER, exact: bool = True) -> float:
    """(c + z_power)^2: the replicates needed per unit of (sigma / delta)^2 for `power` at `alpha`, the range term
    left out -- c the empirical-Bernstein variance constant (`exact`) or the normal quantile z_(1-alpha)."""
    c = eb_constants(alpha)[0] if exact else z(1.0 - alpha)
    return (c + z(power)) ** 2


# --------------------------------------------------------------------------------------- what a size check can show


def n_certify(alpha: float, conf: float = 0.95) -> int:
    """The fewest replications at which zero rejections put the one-sided `conf` upper limit at or below `alpha`:
    (1 - alpha)^n <= 1 - conf (the rule of three's exact form)."""
    return math.ceil(math.log(1.0 - conf) / math.log(1.0 - alpha))


def cp_upper(x: int, n: int, conf: float = 0.95) -> float:
    """The one-sided Clopper-Pearson upper limit of a rate from x of n."""
    return 1.0 if x >= n else float(stats.beta.ppf(conf, x + 1, n - x))


def cp_lower(x: int, n: int, conf: float = 0.95) -> float:
    """The lower limit of the two-sided 95 % Clopper-Pearson interval (E-052's criterion reads that interval)."""
    return 0.0 if x <= 0 else float(stats.beta.ppf((1.0 - conf) / 2.0, x, n - x + 1))


def e052_fail_count(alpha: float, n: int) -> int:
    """The fewest rejections of n at which E-052's criterion fails (the interval wholly above nominal)."""
    x = 0
    while cp_lower(x, n) <= alpha:
        x += 1
    return x


def e052_blind_ratio(alpha: float, n: int, power: float = 0.5) -> float:
    """The true rate, as a multiple of alpha, that E-052's criterion detects with probability `power` at n tests."""
    x = e052_fail_count(alpha, n)
    lo, hi = alpha, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if stats.binom.sf(x - 1, n, mid) >= power:
            hi = mid
        else:
            lo = mid
    return hi / alpha


def n_no_laxity(alpha: float, kappa: float = KAPPA, power: float = POWER, step: int | None = None) -> int:
    """The smallest n (on a grid of `step`) at which, when the true rate is alpha, the Clopper-Pearson upper limit is
    at most kappa x alpha with probability `power`: the count that shows "no laxity beyond kappa" with power."""
    step = step or max(1, int(round(0.5 / alpha)))
    n = step
    while True:
        x = -1
        while cp_upper(x + 1, n) <= kappa * alpha:
            x += 1
        if x >= 0 and stats.binom.cdf(x, n, alpha) >= power:
            return n
        n += step


# --------------------------------------------------------------------------------------- the time conditions


def binom_tail(B: int, m: int) -> float:
    """P(Bin(B, 1/2) >= m): the chance that at least m of B independent, symmetric block signs are positive."""
    return float(sum(math.comb(B, i) for i in range(m, B + 1)) / 2 ** B)


def start_year_groups(h: int) -> dict[int, np.ndarray]:
    """{year: the session indices of the held-out starts complete at h whose start falls in that year}, on the
    weekday calendar (an upper bound on the sessions; the build reads the pinned session list)."""
    d = weekday_dates(*HELD_OUT)
    idx = np.arange(complete_starts(len(d), h))
    years = d[idx].astype("datetime64[Y]").astype(int) + 1970
    return {int(y): idx[years == y] for y in np.unique(years)}


def group_weights(starts: np.ndarray, h: int, n: int) -> np.ndarray:
    """A group mean's weights on the n sessions when each start's value is the mean of its window's per-session
    contributions: w(k) = (1/|g|) sum over starts i of 1[i <= k <= i + h - 1] / h."""
    w = np.zeros(n)
    for i in starts:
        w[i:i + h] += 1.0 / h
    return w / len(starts)


def group_correlations(h: int, n_min: int) -> tuple[list[int], np.ndarray, list[int]]:
    """(the years with at least n_min complete starts, their pairwise correlation matrix under i.i.d. per-session
    contributions, every year's start count)."""
    n = weekdays(*HELD_OUT)
    groups = start_year_groups(h)
    counts = [len(groups[y]) for y in sorted(groups)]
    ok = [y for y in sorted(groups) if len(groups[y]) >= n_min]
    W = np.array([group_weights(groups[y], h, n) for y in ok])
    G = W @ W.T
    s = np.sqrt(np.diag(G))
    return ok, G / np.outer(s, s), counts


def orthant(rho: np.ndarray) -> float:
    """P(all positive) for a centred Gaussian vector of 1, 2 or 3 components with correlations rho (exact formulas:
    1/2; 1/4 + asin(r)/(2 pi); 1/8 + (asin r12 + asin r13 + asin r23)/(4 pi))."""
    k = rho.shape[0]
    if k == 1:
        return 0.5
    if k == 2:
        return 0.25 + math.asin(rho[0, 1]) / (2 * math.pi)
    if k == 3:
        return 0.125 + (math.asin(rho[0, 1]) + math.asin(rho[0, 2]) + math.asin(rho[1, 2])) / (4 * math.pi)
    raise ValueError("one to three groups")


def y_size(h: int, n_min: int) -> tuple[int, float, float, float]:
    """(|Y_ok|, the smallest pairwise correlation, P(all positive), P(strict majority positive)) for (Y)'s start-year
    groups at h* = h; P(strict majority) is 1/2 for one or three symmetric groups and P(all) for two."""
    ok, rho, _ = group_correlations(h, n_min)
    k = len(ok)
    r_min = float(rho[np.triu_indices(k, 1)].min()) if k > 1 else float("nan")
    p_all = orthant(rho)
    p_maj = p_all if k == 2 else 0.5
    return k, r_min, p_all, p_maj


# --------------------------------------------------------------------------------------- the run plan


def lane_trades(R: int, arms: int, M: int, T: int, h: int, tau: int = TAU) -> int:
    """A part's work: histories x arm-runs x seed replicates x starts x (horizon x trades a session)."""
    return R * arms * M * T * h * tau


def hours(work: int, cost_us: float, workers: int = WORKERS) -> float:
    return work * cost_us * 1e-6 / workers / 3600.0


def max_lanes(cap_gb: float = MEM_CAP_GB, workers: int = WORKERS, base_gb: float = BASE_GB,
              lane_bytes: int = LANE_BYTES) -> int:
    """The widest lockstep a worker may run: (cap / workers - base) / lane bytes."""
    return int((cap_gb / workers - base_gb) * 1e9 // lane_bytes)


def parts() -> tuple[tuple[str, int, int, int, int, int], ...]:
    """H3's parts and the held-out test, proposed sizes for H3's declaration: (part, histories R, arm-runs per history,
    seed replicates per arm M, starts per history |T|, horizon in sessions). The held-out test's J is the formulas' at
    delta = 0.02: Hoeffding's for a mean-type composite, the empirical-Bernstein range term's for a quantile one."""
    wh = weekdays(*HELD_OUT)
    t63, t252 = complete_starts(wh, 63), complete_starts(wh, 252)
    a = level(13)
    j_h = -(-hoeffding_units(0.02, a) // t63)
    j_eb = eb_range_replicates(0.02, a)
    arms = FINALISTS + BASELINES
    return (
        ("A1 same-design nulls", 20, 3, 10_000, 120, 63),
        ("A2 exact-centred toy null", 20, 2, 10_000, 120, 63),
        ("A3 history null", 200, 2, 2_000, 120, 63),
        ("A4 plants, copy-stagger", 10, 8, 10_000, 120, 63),
        ("D1 same-design nulls", 20, 3, 2_000, t252, 252),
        ("D2 history null", 200, 2, 500, t252, 252),
        ("D3 power gate plants", 10, 6, 2_000, t252, 252),
        ("D3 full-J check (EB)", 5, 2, j_eb, t252, 252),
        ("H7 held-out, Hoeffding", 1, arms, j_h, t63, 63),
        ("H7 held-out, EB sets", 1, arms, j_eb, t252, 252),
    )


# --------------------------------------------------------------------------------------- the report


def report() -> str:
    out: list[str] = []
    out.append("levels: k, 0.05/(k(k+1)), B_min, 2^-B_min, 2^-(B_min-1)")
    for k in KS:
        a = level(k)
        b = b_min(a)
        out.append(f"  k={k}  alpha={a:.4e}  B_min={b}  2^-B_min={2.0 ** -b:.4e}  2^-(B_min-1)={2.0 ** -(b - 1):.4e}")
    wh, ws = weekdays(*HELD_OUT), weekdays(*SEARCH)
    out.append(f"weekdays (upper bounds on sessions): held-out W_H={wh}, search W_S={ws}")
    out.append("per horizon h: disjoint units floor(W/h) held-out (with a partial one) | search; complete held-out"
               " starts W_H-h+1; held-out start-blocks of length h; sessions needed for B_min(13) disjoint units")
    b13 = b_min(level(13))
    for h in HORIZONS:
        out.append(f"  h={h:<3}  units_H<={disjoint_units(wh, h):<2} (partial {partial_units(wh, h):<2})"
                   f"  units_S<={disjoint_units(ws, h):<2}  starts_H<={complete_starts(wh, h):<3}"
                   f"  blocks_H<={start_blocks(wh, h):<2}  sessions_for_{b13}_units={b13 * h}")
    a = level(13)
    ch = hoeffding_constant(a)
    c1, c2 = eb_constants(a)
    out.append(f"k=13 constants: Hoeffding c_h=sqrt(2 ln(1/alpha))={ch:.4f}; empirical Bernstein"
               f" c1=sqrt(2 ln(2/alpha))={c1:.4f}, c2=7 ln(2/alpha)/3={c2:.4f}; normal z_(1-alpha)={z(1.0 - a):.4f},"
               f" z_{POWER}={z(POWER):.4f}")
    fe, fn = seed_factor(a, exact=True), seed_factor(a, exact=False)
    out.append(f"EB variance term, replicates per (sigma/delta)^2 at power {POWER}: {fe:.3f} (normal t {fn:.3f},"
               f" ratio {fe / fn:.3f})")
    t63 = complete_starts(wh, 63)
    out.append(f"power {POWER} at k=13 by delta (differences in [-1, 1]): Hoeffding units n, its seeds J at"
               f" |T|={t63}; EB seed sets J from the range term alone (at most {RANGE_SHARE} x delta)")
    for d in DELTA:
        n = hoeffding_units(d, a)
        out.append(f"  delta={d}  Hoeffding n>={n}  J>={-(-n // t63)}  EB J>={eb_range_replicates(d, a)}")
    out.append("what a size check shows at n tests (95 %): rule-of-three n; E-052 fails from x rejections; the rate"
               f" E-052 detects half the time; n for 'no laxity beyond {KAPPA:g} x' with power {POWER}")
    for lv in FEASIBLE + (a,):
        n0 = n_certify(lv)
        out.append(f"  alpha={lv:.4e}  n={n0}  E-052 fails at x>={e052_fail_count(lv, n0)}"
                   f"  detects {e052_blind_ratio(lv, n0):.2f} x alpha  no-laxity n={n_no_laxity(lv)}")
    out.append("time leg, independent symmetric blocks: B, P(all B positive), P(strict majority positive)")
    for B in BLOCKS:
        out.append(f"  B={B:<2}  all={binom_tail(B, B):.4e}  majority={binom_tail(B, B // 2 + 1):.4e}")
    out.append("(Y) start-year groups (calendar only), white-noise overlap: h*, n_min, starts per year, |Y_ok|,"
               " smallest correlation, P(all positive), P(strict majority)")
    for h in (63, 126, 252):
        _, _, counts = group_correlations(h, h)
        for nm in (h, 21):
            k, r, pa, pm = y_size(h, nm)
            out.append(f"  h*={h:<3}  n_min={nm:<3}  starts {counts}  |Y_ok|={k}  rho_min={r:.4f}  all={pa:.4f}"
                       f"  majority={pm:.4f}")
    out.append(f"gate horizon H_g={H_GATE}: complete held-out starts <= {complete_starts(wh, H_GATE)},"
               f" disjoint held-out blocks <= {disjoint_units(wh, H_GATE)}, search <= {disjoint_units(ws, H_GATE)}")
    out.append(f"memory: cap {MEM_CAP_GB} GB over {WORKERS} workers, base {BASE_GB} GB assumed, lane {LANE_BYTES} B:"
               f" at most {max_lanes()} lanes a worker")
    out.append(f"run plan (trades a session <= {TAU}; {FINALISTS} finalists + {BASELINES} baselines in H7; hours over"
               f" {WORKERS} workers at the assumed costs " + ", ".join(f"{c} us" for c in COSTS_US) + " a lane-trade)")
    for name, R, arms, M, T, h in parts():
        w = lane_trades(R, arms, M, T, h)
        hs = "  ".join(f"{hours(w, c):.1f}" for c in COSTS_US)
        out.append(f"  {name:<26} R={R:<3} arms={arms} M={M:<6} T={T:<3} h={h:<3} lane-trades={w:.3e}  h: {hs}")
    return "\n".join(out)


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
