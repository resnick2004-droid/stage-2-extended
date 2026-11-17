"""Q-126's plan (`docs/calibration/DRAFT_Q-126_one_sample_plan_2.md`, second text): its arithmetic -- no bar, no market
outcome, no random number. Every figure the plan states is printed here, from three kinds of input only:

- the plan's declared constants: the validation's exposure (23 subsets at each of five sizes, two values, five exact
  side models), the sizing rule's two probabilities, the family levels 0.05/(k(k+1)) at k = 13..20, 200,000
  replications, the 1,123 Monte Carlo nulls of Q-108's class;
- columns of Q-108's result files, read as a calibration (they are not market outcomes): `results/q108_choice.csv`
  (`P`, `p_mc`), `results/q108_cal_size.csv` (`admitted_share`) and `results/q108_val_size.csv` (`count_k*`);
- Q-108's two run logs (`%LOCALAPPDATA%/stage2-extended-runs/q108-calibrate.log` and `q108-validate.log` by default):
  their per-null timing lines (`... of <den>; <t> s, ws <MB> MB`), their `EXIT 0 (<s> s)` lines and the pairs step's
  peak working set, for the cost (section 6.2). Without the logs the cost lines are not printed.

    python docs/calibration/scripts/q126/q126_arith.py [--repo ROOT] [--cal-log PATH] [--val-log PATH]

`main()` prints everything; the functions are imported by `tests/test_q126_draft.py`, which holds the plan's stated
figures to them."""
from __future__ import annotations

import argparse
import math
import os
import re
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]

# ------------------------------------------------------------------------------------------- declared constants

KS = tuple(range(13, 21))
LEV = {k: 0.05 / (k * (k + 1)) for k in KS}
REPS = 200_000
SIZES = (200, 500, 1000, 2000, 5000)
VALUES = ("win1", "net3")
EXACT_MODELS = ("flip42", "flip55", "flip63", "alt45", "alt55")
#: the validation's exposure: Q-108's class, unchanged (23 fresh subsets at each size)
VAL_SUBSETS_PER_SIZE = 23
#: the Monte Carlo nulls of Q-108's class (its plan's 3.5), unchanged in the validation
MC_NULLS = 1123
#: the sizing rule: a pooled bad-subset rate at which the validation passes with probability at most VAL_PASS is seen
#: at least once in the calibration with probability at least DETECT (the rule of three's form)
VAL_PASS = 0.9
DETECT = 0.95
#: the declared calibration subsets at each size (the plan's 3.2): the rule's minimum rounded up to a multiple of 20
CAL_SUBSETS_PER_SIZE = 660
#: the margins of the scope-D grid (the plan's 2.2), ascending; the scope-Q branch takes those of at least 1.5
GRID = (1.0, 1.125, 1.25, 1.375, 1.5, 1.75, 2.0)
Q_BRANCH_MIN = 1.5
#: the reference against which power costs are stated (the brief's item 7)
REFERENCE = ("cons_m1.25", "Q")


def n_val() -> int:
    """The validation's exposed subsets, pooled over sizes (each at both values and every exact model)."""
    return VAL_SUBSETS_PER_SIZE * len(SIZES)


def punished_rate(n: int | None = None, val_pass: float = VAL_PASS) -> float:
    """The pooled bad-subset rate r_V at which the validation's n subsets all hold with probability val_pass."""
    n = n_val() if n is None else n
    return 1.0 - val_pass ** (1.0 / n)


def min_cal_subsets(n: int | None = None, val_pass: float = VAL_PASS, detect: float = DETECT) -> int:
    """The least N with 1 - (1 - r_V)^N >= detect: N = ceil(ln(1 - detect) / ln(1 - r_V))."""
    r = punished_rate(n, val_pass)
    return math.ceil(math.log(1.0 - detect) / math.log(1.0 - r) - 1e-9)


def detection(N: int, r: float) -> float:
    return 1.0 - (1.0 - r) ** N


def minimax_one(a: float) -> float:
    """sup over r of P(the calibration's N subsets hold) x P(the validation's n fail), a = n / N: max over x in (0, 1)
    of x^(1/a) (1 - x), attained at x = 1 / (1 + a)."""
    x = 1.0 / (1.0 + a)
    return x ** (1.0 / a) * (1.0 - x)


def minimax_nested(a: float) -> float:
    """For candidates nested in their margin (a larger margin's rejections are a subset of a smaller's, so its
    eligibility is implied), the choice -- the smallest eligible margin -- fails the validation's exact part with
    probability at most the integral of 1 - p^a over p in (0, 1), which is a / (1 + a), whatever the rates."""
    return a / (1.0 + a)


# ------------------------------------------------------------------------------------------- the floor's allowance (M2)

#: the declared allowance (the plan's 3.2): zero tolerance, no bad subset among the 3,300 (the lead's E-176, which
#: reverses E-173's allowance after its computed cost)
ALLOWANCE = 0
#: beside, a reading: E-173's reversed ruling -- at the bad-subset rate where the validation's exact part passes a
#: candidate with probability GUARD_PASS, the floor (at most c bad subsets) refuses it with at most MAX_REFUSAL; c the
#: least such count. `allowance()` computes it; it must equal E173_ALLOWANCE
GUARD_PASS = 0.95
MAX_REFUSAL = 0.10
E173_ALLOWANCE = 3
#: the allowances compared in the plan's 4.3 reading
COMPARED = (0, 1, 2, 3)
#: the rates at which the floor's power is tabulated (the plan's 4.3), beside r_95 and r_V
FLOOR_RATES = (1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 2e-3)


def guard_rate(n: int | None = None) -> float:
    """r_95: the pooled bad-subset rate at which the validation's n subsets all hold with probability GUARD_PASS."""
    return punished_rate(n, GUARD_PASS)


def floor_admits(r: float, N: int | None = None, c: int | None = None) -> float:
    """P(at most c bad subsets among N | rate r): the floor's chance of admitting a candidate."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    c = ALLOWANCE if c is None else c
    return float(stats.binom.cdf(c, N, r))


def allowance(N: int | None = None, n: int | None = None) -> int:
    """E-173's c (beside): the least c whose floor refuses a candidate at r_95 with probability at most MAX_REFUSAL."""
    r = guard_rate(n)
    c = 0
    while 1.0 - floor_admits(r, N, c) > MAX_REFUSAL:
        c += 1
    return c


def bound_nested_c(N: int, n: int, c: int) -> float:
    """The nested branch's bound with an allowance c: the choice fails the validation's exact part with probability at
    most the integral over p in (0, 1) of 1 - (1 - G^-1(p))^n, G(r) = P(Bin(N, r) <= c). Substituting p = G(r), it is
    1 - E[(1 - R)^n] with R ~ Beta(c + 1, N - c): 1 - prod_{i < n} (N - c + i) / (N + 1 + i). At c = 0 it is
    n / (N + n) = a / (1 + a)."""
    return 1.0 - math.exp(sum(math.log((N - c + i) / (N + 1 + i)) for i in range(n)))


def bound_one_c(N: int, n: int, c: int) -> float:
    """One candidate's bound with an allowance c: sup over r of P(Bin(N, r) <= c) (1 - (1 - r)^n), on a fine log grid
    of r (the maximum is interior and smooth)."""
    r = np.exp(np.linspace(math.log(1e-7), math.log(0.2), 400_001))
    return float((stats.binom.cdf(c, N, r) * (1.0 - (1.0 - r) ** n)).max())


def cp_upper(x: int, m: int, conf: float = 0.95) -> float:
    """The one-sided Clopper-Pearson upper limit on a rate after x bad among m."""
    return float(stats.beta.ppf(conf, x + 1, m - x))


def rule_bounds(N: int | None = None, n: int | None = None, c: int | None = None) -> dict[str, float]:
    """The bounds on the chance that a statistic the rule chooses holds the calibration and fails the validation's
    exact part: the primary (scope D's nested grid plus C6; or, when scope D has none, the scope-Q branch alone) and
    the second statistic (the scope-Q branch's choice, validated beside when scope D chooses; M3)."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    n = n_val() if n is None else n
    c = ALLOWANCE if c is None else c
    nest, one = bound_nested_c(N, n, c), bound_one_c(N, n, c)
    return {"nested": nest, "one": one, "primary": nest + one, "second": nest, "all": 2 * nest + one}


def bound_by_subsets(Ns=(3300, 6600, 13200, 26400), n: int | None = None) -> list[tuple[int, int, float]]:
    """Beside, not taken: (N, the ruled allowance at N, the nested bound) for larger calibrations. Under the ruling the
    floor admits a candidate at r_95, which the validation's exact part fails with 1 - GUARD_PASS, so the bound tends
    to 1 - GUARD_PASS from above as N grows and never falls below it."""
    n = n_val() if n is None else n
    return [(N, allowance(N, n), bound_nested_c(N, n, allowance(N, n))) for N in Ns]


# ------------------------------------------------------------------------------------------- the Monte Carlo probe (M1)

#: at each size, the sizing subsets with the largest exact size (the plan's 3.2) carry the four persistent Monte Carlo
#: models at both values
PROBE_PER_SIZE = 23
PROBE_MODELS = ("flip21", "markov30", "markov50", "markov80")


def probe_nulls() -> int:
    return PROBE_PER_SIZE * len(SIZES) * len(PROBE_MODELS) * len(VALUES)


def probe_refusal(rho: float, m: int | None = None) -> float:
    """The probe's chance of refusing a candidate with m probed nulls at rho times nominal at every k: each null is
    refused exactly as the validation fails a null (E-052's failure counts)."""
    m = probe_nulls() if m is None else m
    return 1.0 - (1.0 - null_fail(rho)) ** m


# ------------------------------------------------------------------------------------------- the criterion's power


def failure_count(level: float, reps: int = REPS) -> int:
    """E-052's failure: the least count whose 95 % Clopper-Pearson lower limit lies above the level."""
    c = max(1, int(level * reps))
    while stats.beta.ppf(0.025, c, reps - c + 1) <= level:
        c += 1
    return c


FAIL = {k: failure_count(LEV[k]) for k in KS}


def p_holds(rates, fail=None, reps: int = REPS) -> float:
    """P(X_k < fail_k at every k) for X_13 ~ Bin(reps, rates[0]), X_{k+1} | X_k ~ Bin(X_k, rates[i+1] / rates[i])
    (Q-108's 4.2 computation, by dynamic programming over the counts)."""
    fail = FAIL if fail is None else fail
    f = [int(fail[k]) for k in KS]
    r = [float(x) for x in rates]
    if r[0] <= 0.0:
        return 1.0
    prob = stats.binom.pmf(np.arange(f[0]), reps, r[0])
    for i in range(1, len(f)):
        q = r[i] / r[i - 1] if r[i - 1] > 0 else 0.0
        x = np.arange(prob.size)
        y = np.arange(f[i])
        prob = stats.binom.pmf(y[:, None], x[None, :], q) @ prob
    return float(prob.sum())


def null_fail(rho: float) -> float:
    """One Monte Carlo null at rho times nominal at every k: the chance it breaks E-052's criterion somewhere."""
    return 1.0 - p_holds([rho * LEV[k] for k in KS])


def mc_pass(rho: float, nulls: int = MC_NULLS) -> float:
    return (1.0 - null_fail(rho)) ** nulls


def tolerated(rho: float, target: float = VAL_PASS) -> float:
    """How many Monte Carlo nulls at rho times nominal the criterion passes with probability target."""
    f = null_fail(rho)
    return math.inf if f <= 0 else math.log(target) / math.log(1.0 - f)


# ------------------------------------------------------------------------------------------- Q-108's files


def choice_p(repo: Path = ROOT) -> dict[tuple[str, str], float]:
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[d["row"] == "candidate"]
    return {(str(r.candidate), str(r.scope)): float(r.P) for r in d.itertuples()}


def choice_p_mc(repo: Path = ROOT) -> dict[tuple[str, str], float]:
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[d["row"] == "candidate"]
    return {(str(r.candidate), str(r.scope)): float(r.p_mc) for r in d.itertuples()}


def name_of(m: float) -> str:
    return "cons" if m == 1.0 else f"cons_m{m:g}"


def power_costs(repo: Path = ROOT) -> dict[str, tuple[str, float, float]]:
    """{candidate: (how, low, high)} -- P / P(cons_m1.25, Q). From the file where Q-108 measured the candidate
    ("file", low = high); bracketed by its grid neighbours' file values where it did not ("bracket": a margin's MDL is
    m crit se - est, increasing in m on every replication, so P is too)."""
    P = choice_p(repo)
    ref = P[REFERENCE]
    measured = {m: P[(name_of(m), "D")] / ref for m in GRID if (name_of(m), "D") in P}
    out = {}
    for m in GRID:
        if m in measured:
            out[name_of(m)] = ("file", measured[m], measured[m])
        else:
            lo = max(x for x in measured if x < m)
            hi = min(x for x in measured if x > m)
            out[name_of(m)] = ("bracket", measured[lo], measured[hi])
    out["cons_bm_m1.25"] = ("file", P[("cons_bm_m1.25", "D")] / ref, P[("cons_bm_m1.25", "D")] / ref)
    return out


def interpolated(repo: Path = ROOT) -> dict[str, float]:
    """The bracketed margins' cost by linear interpolation in m between the neighbours (an estimate, not a file
    value)."""
    P = choice_p(repo)
    ref = P[REFERENCE]
    pts = {m: P[(name_of(m), "D")] for m in GRID if (name_of(m), "D") in P}
    out = {}
    for m in GRID:
        if m not in pts:
            lo = max(x for x in pts if x < m)
            hi = min(x for x in pts if x > m)
            out[name_of(m)] = (pts[lo] + (pts[hi] - pts[lo]) * (m - lo) / (hi - lo)) / ref
    return out


def worst_flip42(cand: str, scope: str, repo: Path = ROOT) -> float:
    """`q108_choice.csv`'s `worst_ratio_flip42` for one candidate and scope (the plan's section 5, M3)."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[(d["row"] == "candidate") & (d["candidate"] == cand) & (d["scope"] == scope)]
    return float(d["worst_ratio_flip42"].iloc[0])


def grid_p(repo: Path = ROOT) -> dict[str, float]:
    """Each grid margin's P / P(cons_m1.25): the file's value, or the linear interpolation where Q-108 did not run it."""
    pc, ip = power_costs(repo), interpolated(repo)
    return {name_of(m): (pc[name_of(m)][1] if pc[name_of(m)][0] == "file" else ip[name_of(m)]) for m in GRID}


def step_costs(repo: Path = ROOT) -> list[tuple[str, str, float]]:
    """The MDL cost of one grid step: P(next) / P(this) - 1, from `grid_p` (an estimate where a margin is
    interpolated)."""
    g = grid_p(repo)
    names = [name_of(m) for m in GRID]
    return [(a, b, g[b] / g[a] - 1.0) for a, b in zip(names, names[1:])]


def coverage(repo: Path = ROOT):
    """Scope D's admitted share under each side model: the mean of `admitted_share` over the in-rule fixed-data and
    subset nulls of `cons_m1.25` in scope D (the admission reads sides only, so every candidate's is the same), and
    its range over the five sizes."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_cal_size.csv", low_memory=False)
    d = d[d["row"].isna() & (d["candidate"] == "cons_m1.25") & (d["scope"] == "D")
          & d["group"].isin(["fixed", "subset"])]
    d = d[d["in_rule"].astype(str) == "True"]
    mean = d.groupby("model")["admitted_share"].mean()
    by = d[d["group"] == "subset"].groupby(["model", "size"])["admitted_share"].mean().unstack()
    return mean, by.min(axis=1), by.max(axis=1)


def q108_val_mc_headroom(repo: Path = ROOT) -> tuple[float, str, int]:
    """In Q-108's validation, `cons_m1.25` scope Q: the largest Monte Carlo null's count as a share of E-052's
    failure count, over every k (its null and k)."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_val_size.csv", low_memory=False)
    d = d[d["row"].isna() & (d["candidate"] == "cons_m1.25") & (d["scope"] == "Q") & (d["kind"] == "mc")
          & (d["in_rule"].astype(str) == "True")]
    best = (0.0, "", 0)
    for k in KS:
        share = d[f"count_k{k}"] / FAIL[k]
        i = share.idxmax()
        if share[i] > best[0]:
            best = (float(share[i]), str(d.loc[i, "null"]), k)
    return best


# ------------------------------------------------------------------------------------------- the cost

#: the plan's 3.3: the drift populations, each enumerated at every exact model
DRIFT_SCENARIOS = 8
DRIFT_POPULATIONS = 150
DRIFT_MODELS = EXACT_MODELS
RUNS = Path(os.environ.get("LOCALAPPDATA", "")) / "stage2-extended-runs"
CAL_LOG = RUNS / "q108-calibrate.log"
VAL_LOG = RUNS / "q108-validate.log"

EXACT_LINE = re.compile(r"\]   (?:fixed|sub):\S*:(flip42|flip55|flip63|alt45|alt55): .*; ([0-9.]+) s, ws ([0-9]+) MB")
MC_LINE = re.compile(r"\]   sub:\S*:(flip21|markov30|markov50|markov80): .*; ([0-9.]+) s, ws ([0-9]+) MB")
EXIT_LINE = re.compile(r"\] EXIT 0 \(([0-9]+) s\)")
PAIRS_PEAK = re.compile(r"peak working set ([0-9]+) MB")


def log_stats(path: Path) -> dict:
    """From a Q-108 run log: per exact model the median and mean seconds of one enumeration; the mean seconds of one
    persistent Monte Carlo subset null; the run's EXIT seconds; the largest per-null working set and the pairs step's
    peak (MB)."""
    ex: dict[str, list[float]] = {}
    mc: list[float] = []
    ws: list[int] = []
    out = {"exit_s": None, "pairs_peak_mb": None}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = EXACT_LINE.search(line)
        if m:
            ex.setdefault(m.group(1), []).append(float(m.group(2)))
            ws.append(int(m.group(3)))
            continue
        m = MC_LINE.search(line)
        if m:
            mc.append(float(m.group(2)))
            ws.append(int(m.group(3)))
            continue
        m = EXIT_LINE.search(line)
        if m:
            out["exit_s"] = int(m.group(1))
        m = PAIRS_PEAK.search(line)
        if m:
            out["pairs_peak_mb"] = int(m.group(1))
    out["median"] = {k: float(np.median(v)) for k, v in ex.items()}
    out["mean"] = {k: float(np.mean(v)) for k, v in ex.items()}
    out["mc_mean"] = float(np.mean(mc)) if mc else None
    out["ws_max_mb"] = max(ws) if ws else None
    return out


def logs_present() -> bool:
    return CAL_LOG.is_file() and VAL_LOG.is_file()


def sizing_hours(per_subset_value_s: float, extra_subsets: int | None = None) -> float:
    extra = (CAL_SUBSETS_PER_SIZE - VAL_SUBSETS_PER_SIZE) * len(SIZES) if extra_subsets is None else extra_subsets
    return extra * len(VALUES) * per_subset_value_s / 3600.0


def per_subset_value(st: dict) -> float:
    """The mean seconds of one subset-value's five exact enumerations."""
    return sum(st["mean"][m] for m in EXACT_MODELS)


def cost(cal: dict, val: dict) -> dict[str, tuple[float, float]]:
    """(low, high) hours of each part of the calibration run: low from the validation log (two candidates), high from
    the calibration log (ten); means throughout; the core from the two runs' EXIT seconds."""
    out = {
        "core": (val["exit_s"] / 3600.0, cal["exit_s"] / 3600.0),
        "sizing": (sizing_hours(per_subset_value(val)), sizing_hours(per_subset_value(cal))),
        "probe": (probe_nulls() * val["mc_mean"] / 3600.0, probe_nulls() * cal["mc_mean"] / 3600.0),
        "drift": (DRIFT_SCENARIOS * DRIFT_POPULATIONS * per_subset_value(val) / 3600.0,
                  DRIFT_SCENARIOS * DRIFT_POPULATIONS * per_subset_value(cal) / 3600.0),
    }
    out["total"] = (sum(v[0] for v in out.values()), sum(v[1] for v in out.values()))
    return out


# ------------------------------------------------------------------------------------------- print


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--cal-log", type=Path, default=None)
    ap.add_argument("--val-log", type=Path, default=None)
    a = ap.parse_args()

    n = n_val()
    N = CAL_SUBSETS_PER_SIZE * len(SIZES)
    rV = punished_rate(n)
    print("== 3.2 the sizing rule")
    print(f"validation exposure: {VAL_SUBSETS_PER_SIZE} x {len(SIZES)} = {n} subsets, each at {len(VALUES)} values x "
          f"{len(EXACT_MODELS)} exact models = {n * len(VALUES) * len(EXACT_MODELS)} exact subset nulls")
    print(f"punished rate r_V = 1 - {VAL_PASS}^(1/{n}) = {rV:.4e}")
    Nmin = min_cal_subsets(n)
    print(f"least calibration subsets: {Nmin} pooled ({math.ceil(Nmin / len(SIZES))} a size); declared "
          f"{CAL_SUBSETS_PER_SIZE} a size = {N}, of which {VAL_SUBSETS_PER_SIZE} a size carry the whole class")
    print(f"at {N}: P(see r_V) = {detection(N, rV):.4f}; rule-of-three bound 3/N = {3 / N:.4e}; validation passes at "
          f"that bound with {(1 - 3 / N) ** n:.4f}")
    aa = n / N
    print(f"a = n/N = {aa:.5f}; worst P(calibration holds, validation fails) one candidate {minimax_one(aa):.4f}; "
          f"a nested branch {minimax_nested(aa):.4f}; the rule (D's nested grid + C6 + Q's nested branch) "
          f"{2 * minimax_nested(aa) + minimax_one(aa):.4f}")
    print(f"exact enumerations: {N} x {len(VALUES)} x {len(EXACT_MODELS)} = {N * len(VALUES) * len(EXACT_MODELS)}; "
          f"at L = 42 alone {N * len(VALUES)}")
    print(f"Q-108's own design (a = 1): one candidate {minimax_one(1.0):.4f}, a nested branch "
          f"{minimax_nested(1.0):.4f}; "
          f"its 115 subsets saw r_V with {detection(n, rV):.4f}")
    for r in (1e-4, rV, 3 / N, 1e-3, 3 / n, 0.01):
        print(f"   bad-subset rate {r:.2e}: the validation's exact part passes with {(1 - r) ** n:.4f}; the "
              f"calibration sees one with {detection(N, r):.4f}")

    print("== 4.3 the criterion's power (E-052's, unchanged)")
    print("failure counts at 200,000:", FAIL)
    for rho in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        print(f"   every MC null at {rho} x nominal: one null fails with {null_fail(rho):.3e}; all {MC_NULLS} pass "
              f"with "
              f"{mc_pass(rho):.4f}; nulls tolerated at {VAL_PASS}: {tolerated(rho):.0f}")
    pm = choice_p_mc(a.repo)
    for c in [("cons_m1.25", "Q"), ("cons_m1.25", "D"), ("cons_m1.5", "Q"), ("cons_bm_m1.25", "D")]:
        print(f"   Q-108's P_MC (q108_choice.csv p_mc) {c}: {pm[c]:.6f}")
    s, nm, k = q108_val_mc_headroom(a.repo)
    print(f"   Q-108's validation, cons_m1.25 Q: the largest MC count is {s:.3f} of its failure count ({nm}, k = {k})")

    print("== 5 the power costs against cons_m1.25 (q108_choice.csv P)")
    P = choice_p(a.repo)
    print(f"   P(cons_m1.25, Q) = {P[REFERENCE]:.5f}; P(cons_m1.25, D) = {P[('cons_m1.25', 'D')]:.5f}")
    ip = interpolated(a.repo)
    for c, (how, lo, hi) in power_costs(a.repo).items():
        extra = f"; linear interpolation {ip[c]:.3f}" if c in ip else ""
        print(f"   {c}: {how} {lo:.3f}" + (f" to {hi:.3f}" if hi != lo else "") + extra)

    print(f"   Q-108's worst flip-42 ratio, cons_m1.5 in scope Q: {worst_flip42('cons_m1.5', 'Q', a.repo):.3f}")

    print("== 7 scope D's coverage (q108_cal_size.csv admitted_share, cons_m1.25 D, in-rule fixed and subset nulls)")
    mean, lo, hi = coverage(a.repo)
    for m in mean.index:
        print(f"   {m}: mean {mean[m]:.3f}; over sizes {lo.get(m, float('nan')):.3f} to {hi.get(m, float('nan')):.3f}")

    print(f"== 3.2 / 4.3 the floor: declared c = {ALLOWANCE} (E-176); E-173's allowance beside")
    N = CAL_SUBSETS_PER_SIZE * len(SIZES)
    r95 = guard_rate(n)
    c = allowance(N, n)
    print(f"r_95 = 1 - {GUARD_PASS}^(1/{n}) = {r95:.4e}; E-173's least allowance c = {c} (recorded {E173_ALLOWANCE}); "
          f"it refuses at r_95 with {1 - floor_admits(r95, N, c):.4f} (at c - 1: {1 - floor_admits(r95, N, c - 1):.4f})")
    print("   c | refuses at r_95 | refuses at r_V | one | nested | primary | second | rule")
    for cc in COMPARED:
        bb = rule_bounds(N, n, cc)
        print(f"   {cc} | {1 - floor_admits(r95, N, cc):.4f} | {1 - floor_admits(rV, N, cc):.4f} | {bb['one']:.4f} | "
              f"{bb['nested']:.4f} | {bb['primary']:.4f} | {bb['second']:.4f} | {bb['all']:.4f}")
    print(f"at c = {c}: r_V refused with {1 - floor_admits(rV, N, c):.4f}; the 95 % upper limit after {c} bad of {N}: "
          f"{cp_upper(c, N):.4e}, at which the validation's exact part passes with {(1 - cp_upper(c, N)) ** n:.4f}")
    print(f"   per size: 0 bad of {CAL_SUBSETS_PER_SIZE} bound that size at {cp_upper(0, CAL_SUBSETS_PER_SIZE):.4e}; "
          f"{c} bad of {CAL_SUBSETS_PER_SIZE} at {cp_upper(c, CAL_SUBSETS_PER_SIZE):.4e}")
    b = rule_bounds(N, n, c)
    print(f"bounds at c = {c}: one candidate {b['one']:.4f}; a nested branch {b['nested']:.4f}; the primary "
          f"{b['primary']:.4f}; the second statistic {b['second']:.4f}; the whole rule {b['all']:.4f}")
    b0 = rule_bounds(N, n, 0)
    print(f"   (at c = 0: {b0['one']:.4f}, {b0['nested']:.4f}, {b0['primary']:.4f}, {b0['second']:.4f}, {b0['all']:.4f})")
    for NN, cc, bb in bound_by_subsets(n=n):
        print(f"   beside, not taken: {NN} subsets, allowance {cc}, nested bound {bb:.4f} (its limit {1 - GUARD_PASS:.2f})")
    for r in (*FLOOR_RATES[:4], r95, rV, *FLOOR_RATES[4:]):
        print(f"   rate {r:.4e}: floor admits (c = {c}) {floor_admits(r, N, c):.4f}; (c = 0) {floor_admits(r, N, 0):.4f}; "
              f"the validation's exact part passes {(1 - r) ** n:.4f}")
    print("   grid steps:", [(x, y, round(z, 3)) for x, y, z in step_costs(a.repo)])
    print(f"   the first text's floor (c = 0) refused at 1e-04 with {1 - floor_admits(1e-4, N, 0):.4f} and at r_95 with "
          f"{1 - floor_admits(r95, N, 0):.4f}; the validation's {n} subsets catch a rate of 1e-03 with "
          f"{1 - (1 - 1e-3) ** n:.4f}")

    print("== 4.2 / 4.3 the Monte Carlo probe (M1)")
    m = probe_nulls()
    print(f"probed nulls: {PROBE_PER_SIZE} x {len(SIZES)} x {len(PROBE_MODELS)} x {len(VALUES)} = {m}")
    for rho in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        print(f"   rho {rho}: one probed null refused {null_fail(rho):.3e}; all {m} at rho {probe_refusal(rho):.4f}; "
              f"the validation's {MC_NULLS} all at rho pass {mc_pass(rho):.4f}")

    print("== 6.2 the cost")
    cal_p = a.cal_log or CAL_LOG
    val_p = a.val_log or VAL_LOG
    if Path(cal_p).is_file() and Path(val_p).is_file():
        cs, vs = log_stats(Path(cal_p)), log_stats(Path(val_p))
        for name, st in (("calibration", cs), ("validation", vs)):
            print(f"   Q-108's {name} log: median s an enumeration {st['median']}; mean {st['mean']}; a subset-value "
                  f"(means) {per_subset_value(st):.2f} s; a persistent MC subset null {st['mc_mean']:.2f} s; EXIT "
                  f"{st['exit_s']} s; per-null working set at most {st['ws_max_mb']} MB; pairs step peak "
                  f"{st['pairs_peak_mb']} MB")
        for part, (lo, hi) in cost(cs, vs).items():
            print(f"   {part}: {lo:.1f} to {hi:.1f} h")
    else:
        print("   the logs are not present: no cost line")


if __name__ == "__main__":
    main()
