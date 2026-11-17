"""Q-126's plan (`docs/calibration/DRAFT_Q-126_one_sample_plan_2.md`): its arithmetic -- no bar, no market outcome, no
random number. Every figure the plan states is printed here, from three kinds of input only:

- the plan's declared constants: the validation's exposure (23 subsets at each of five sizes, two values, five exact
  side models), the sizing rule's two probabilities, the family levels 0.05/(k(k+1)) at k = 13..20, 200,000
  replications, the 1,123 Monte Carlo nulls of Q-108's class;
- columns of Q-108's result files, read as a calibration (they are not market outcomes): `results/q108_choice.csv`
  (`P`, `p_mc`), `results/q108_cal_size.csv` (`admitted_share`) and `results/q108_val_size.csv` (`count_k*`);
- optionally, the per-null timing lines of Q-108's two run logs (`... of <den>; <t> s, ws <MB> MB`), for the cost.

    python docs/calibration/scripts/q126/q126_arith.py [--repo ROOT] [--cal-log PATH] [--val-log PATH]

`main()` prints everything; the functions are imported by `tests/test_q126_draft.py`, which holds the plan's stated
figures to them."""
from __future__ import annotations

import argparse
import math
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

LINE = re.compile(r"\]   (?:fixed|sub):\S*:(flip42|flip55|flip63|alt45|alt55): .*; ([0-9.]+) s, ws ([0-9]+) MB")


def log_timings(path: Path) -> dict[str, float]:
    """The median seconds of one exact enumeration per model, from a Q-108 run log's per-null lines."""
    by: dict[str, list[float]] = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.search(line)
        if m:
            by.setdefault(m.group(1), []).append(float(m.group(2)))
    return {k: float(np.median(v)) for k, v in by.items()}


def sizing_hours(per_subset_value_s: float, extra_subsets: int | None = None) -> float:
    extra = (CAL_SUBSETS_PER_SIZE - VAL_SUBSETS_PER_SIZE) * len(SIZES) if extra_subsets is None else extra_subsets
    return extra * len(VALUES) * per_subset_value_s / 3600.0


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

    print("== 7 scope D's coverage (q108_cal_size.csv admitted_share, cons_m1.25 D, in-rule fixed and subset nulls)")
    mean, lo, hi = coverage(a.repo)
    for m in mean.index:
        print(f"   {m}: mean {mean[m]:.3f}; over sizes {lo.get(m, float('nan')):.3f} to {hi.get(m, float('nan')):.3f}")

    print("== 6.2 the cost")
    for name, p in (("calibration", a.cal_log), ("validation", a.val_log)):
        if p is not None and Path(p).is_file():
            t = log_timings(Path(p))
            tot = sum(t.get(m, 0.0) for m in EXACT_MODELS)
            print(f"   Q-108's {name} log, median s an enumeration: {t}; a subset-value {tot:.1f} s; the sized part "
                  f"{sizing_hours(tot):.1f} h")


if __name__ == "__main__":
    main()
