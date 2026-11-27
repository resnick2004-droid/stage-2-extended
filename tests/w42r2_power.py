"""W42-R2's power check (`docs/plans/WAVE42_SETTING_RULE_R2.md` section 7): synthetic journeys only (no bar, no result
file, nothing written). A strict line must show power, not only size. The pass criteria C1 to C6 are the declaration's
section 7.1, written before the check is run; this file evaluates them and prints the verdict per form.

Three headroom forms are read on the same draws (section 7):
- `sd_star` -- W42-R2: both terms at sd*, the largest per-seed sd among the four baselines;
- `winner`  -- both terms at the drawn winner's per-seed sd (the form of `fd1307b`);
- `w42_r1`  -- W42-R1: the held-out test's term only, at the drawn winner's per-seed sd.

Parts:
1. `size`    -- one limit, exact statistics (numpy's linear quantile, the per-seed sd over seeds), independent
   replications; the value set by `extended.wave42_r2.headroom` and `limit_value` (C1, C6);
2. `configs` -- the red team's configuration search in its Gaussian form, vectorised and held equal to `headroom` and
   `limit_value` by a test (C5, C6);
3. `joint`   -- end to end through `setting_rule`, every measure of the design drawn from the best baseline's law,
   read against all seven limits (C2, C1 per limit, C6);
4. `e2e`     -- the added limit end to end through `setting_rule` (C1 where the headroom binds, C3, C4, the curve).

Randomness: one root `numpy.random.SeedSequence` whose entropy is derived from this check's name by sha256 (no
literal, no other block's seed), children by `spawn_key` (part, scenario, chunk, replication, stream).

    python tests/w42r2_power.py --part size --scenario rt_unequal_sd
    python tests/w42r2_power.py --part joint --chunk 0 --search-draws 25
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import wave42 as R  # noqa: E402
from extended import wave42_r2 as R2  # noqa: E402

CHECK_NAME = "W42-R2 power check, Q-221"
ROOT_ENTROPY = int.from_bytes(hashlib.sha256(CHECK_NAME.encode("utf-8")).digest()[:16], "big")
PARTS = ("size", "configs", "joint", "e2e")
FORMS = ("sd_star", "winner", "w42_r1")
L7 = len(R2.LIMITS)
Z7 = R.limit_z(L7)
P0 = float(stats.norm.sf(Z7))              # the nominal per-limit share, 1 - Phi(z_7)
T_SELECTION, T_NO_SELECTION = 1.4, 1.0     # C1's tolerance: the red team's worst case; 1 without a selection
SIZE_REPS = 4000                           # Part 1 replications per scenario (section 7.2)
CONFIGS, CONFIG_REPS = 800, 20000          # Part 2 (C5)
JOINT_DRAWS, JOINT_HELD_OUT = 100, 4       # Part 3, the joint read
SEARCH_DRAWS, HELD_OUT_DRAWS = 40, 10      # Part 4 (the shared headroom scenarios at 100 by 10)
CURVE_T = (-2.0, 0.0, 2.0, 4.0, 6.0)       # design medians at the anchor's + t held-out coin standard errors
SYNTH_UNITS_SHA = "e" * 64                 # a synthetic units-file sha256 (the application checks the real one)
NHO = 640                                  # W42-R1's tests' synthetic held-out session count


def _generator():
    name = "wave42_rule_generator_for_r2_power"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "tests" / "test_wave42_rule.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


T = _generator()


def _root(part: str, *key: int) -> np.random.SeedSequence:
    return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(PARTS.index(part), *key))


def _ints(ss: np.random.SeedSequence) -> int:
    return int(ss.generate_state(1, dtype=np.uint64)[0] % (2 ** 63))


def counts() -> dict[str, int]:
    """The real-sized counts: E_h search on a weekday calendar of the search years, H4's seeds, the held-out starts."""
    from extended import h4_audit as HA

    n_cal = len(T._calendar(1))
    return {"n_cal": n_cal, "j_h4": int(HA.H4_J), "j_test": int(R.TEST_SEEDS), "nho": NHO,
            **{f"n_s_{h}": n_cal - h + 1 for h in R.HORIZONS},
            **{f"n_t_{h}": R.complete_starts(NHO, h) for h in R.HORIZONS}}


# ------------------------------------------------------------------------------------- the three headroom forms
def form_value(form: str, direction: str, m_best: float, m_worst: float, sds: Sequence[float], best: int,
               n_s: int, n_t: int, j_test: int, j_h4: int, z: float) -> float:
    """A limit's value under one form, through `headroom` and `limit_value` (the rule's own functions)."""
    if form == "sd_star":
        needed = R2.headroom(m_best, float(max(sds)), n_s, n_t, j_test, j_h4, z, direction)["needed"]
    else:
        h = R2.headroom(m_best, float(sds[best]), n_s, n_t, j_test, j_h4, z, direction)
        sign = 1.0 if direction == "ceiling" else -1.0
        needed = h["needed"] if form == "winner" else m_best + sign * z * h["se_test"]
    return R2.limit_value(direction, R2.NET12_KIND, m_worst, needed, np.asarray([m_worst]))["value"]


def refused(direction: str, estimate: float, value: float) -> bool:
    return bool(estimate < value) if direction == "floor" else bool(estimate > value)


def best_worst(direction: str, M: Sequence[float]) -> tuple[int, int]:
    idx = range(len(M))
    if direction == "floor":
        return min(idx, key=lambda i: (-M[i], i)), min(idx, key=lambda i: (M[i], i))
    return min(idx, key=lambda i: (M[i], i)), min(idx, key=lambda i: (-M[i], i))


# --------------------------------------------------------------------------------------------- the criteria
def c1_bound(tol: float, n: int | None = None, se: float | None = None) -> float:
    """C1: T p0 + 3 se, se binomial at T p0 over n independent replications, or the cluster se given."""
    p = tol * P0
    return p + 3.0 * (se if se is not None else math.sqrt(p * (1.0 - p) / n))


def cluster_se(shares: Sequence[float]) -> float:
    x = np.asarray(shares, dtype=float)
    return float(np.std(x, ddof=1) / math.sqrt(x.size)) if x.size > 1 else float("inf")


# ------------------------------------------------------------------------------------------------- unit laws
@dataclass(frozen=True)
class Law:
    """A per-unit law: `normal` (mu, sd), `two_humped` (p paid; paid mu, sd; unpaid mu, sd), `lattice` (values,
    probabilities), `zero` (the do-nothing journey)."""
    kind: str
    p: tuple

    def draw(self, rng: np.random.Generator, shape, scale: float = 1.0) -> np.ndarray:
        if self.kind == "normal":
            return scale * rng.normal(self.p[0], self.p[1], shape)
        if self.kind == "zero":
            return np.zeros(shape)
        if self.kind == "lattice":
            vals, cum = np.asarray(self.p[0], dtype=float), np.cumsum(self.p[1])
            return scale * vals[np.searchsorted(cum / cum[-1], rng.random(shape), side="right")]
        p, pm, ps, um, us = self.p
        paid = rng.random(shape) < p
        return scale * np.where(paid, rng.normal(pm, ps, shape), rng.normal(um, us, shape))

    def quantile(self, q: float, scale: float = 1.0) -> float:
        if self.kind == "normal":
            return scale * (self.p[0] + self.p[1] * float(stats.norm.ppf(q)))
        if self.kind == "zero":
            return 0.0
        if self.kind == "lattice":
            c = np.cumsum(self.p[1]) / np.sum(self.p[1])
            return scale * float(np.asarray(self.p[0])[np.searchsorted(c, q - 1e-12)])
        p, pm, ps, um, us = self.p
        f = lambda x: p * stats.norm.cdf(x, pm, ps) + (1 - p) * stats.norm.cdf(x, um, us) - q   # noqa: E731
        return scale * optimize.brentq(f, min(pm, um) - 20 * max(ps, us), max(pm, um) + 20 * max(ps, us))

    def median(self, scale: float = 1.0) -> float:
        return self.quantile(0.5, scale)

    def median_se(self, scale: float, n: int) -> float:
        """The sd of the pooled median of n iid units: 1 / (2 f(m) sqrt(n))."""
        m = self.median(1.0)
        if self.kind == "normal":
            dens = stats.norm.pdf(m, self.p[0], self.p[1])
        else:
            p, pm, ps, um, us = self.p
            dens = p * stats.norm.pdf(m, pm, ps) + (1 - p) * stats.norm.pdf(m, um, us)
        return scale / (2.0 * dens * math.sqrt(n))

    def shifted(self, d: float) -> "Law":
        if self.kind != "normal":
            raise ValueError("a curve shifts a normal law only")
        return Law("normal", (self.p[0] + d, self.p[1]))


def two_humped_at(median: float, ps: float, pm: float = 12.0, um: float = -4.0, us: float = 1.5) -> Law:
    """A paid-or-not law whose median is `median`: the paid share solved so the mixture's cdf is a half there."""
    f = lambda p: p * stats.norm.cdf(median, pm, ps) + (1 - p) * stats.norm.cdf(median, um, us) - 0.5   # noqa: E731
    return Law("two_humped", (float(optimize.brentq(f, 1e-6, 1 - 1e-6)), pm, ps, um, us))


DO_NOTHING = Law("zero", ())


# ------------------------------------------------------------------------------------- Part 1: size, one limit
SIZE: dict[str, dict[str, Any]] = {
    "rt_unequal_sd": {"what": "the red team's: four tied medians, the first eight times noisier, independent draws",
                      "q": 0.5, "direction": "floor", "shared": False, "design": 0, "selection": True,
                      "laws": [Law("normal", (0.0, 8.0))] + [Law("normal", (0.0, 1.0))] * 3},
    "top_two_tied": {"what": "two tied at the top (one four times noisier), two lower within the headroom",
                     "q": 0.5, "direction": "floor", "shared": False, "design": 0, "selection": True,
                     "laws": [Law("normal", (0.0, 4.0)), Law("normal", (0.0, 1.0)), Law("normal", (-0.003, 1.0)),
                              Law("normal", (-0.003, 1.0))]},
    "lumpy_headroom": {"what": "paid-or-not laws, tied medians, the first's paid hump narrow (its median noisier)",
                       "q": 0.5, "direction": "floor", "shared": False, "design": 0, "selection": True,
                       "laws": [two_humped_at(8.0, 2.0)] + [two_humped_at(8.0, 8.0)] * 3},
    "lattice": {"what": "an integer count whose 0.9 point sits on a lattice jump, four alike (a p90 ceiling); "
                        "form-insensitive by construction: the lattice step exceeds every headroom (C6's exception)",
                "q": 0.9, "direction": "ceiling", "shared": False, "design": 0, "selection": True,
                "form_insensitive": True,
                "laws": [Law("lattice", ((2.0, 3.0, 4.0), (0.5, 0.4, 0.1)))] * 4},
    "equal_independent": {"what": "four alike with equal sds, independent draws (the classic winner's curse)",
                          "q": 0.5, "direction": "floor", "shared": False, "design": 0, "selection": True,
                          "laws": [Law("normal", (0.0, 1.0))] * 4},
    "identical_shared": {"what": "one shared draw of one law (no selection)", "q": 0.5, "direction": "floor",
                         "shared": True, "design": 0, "selection": False, "laws": [Law("normal", (0.0, 1.0))] * 4},
    "distinct_shared": {"what": "one shared draw, medians apart by less than the headroom (no selection)",
                        "q": 0.5, "direction": "floor", "shared": True, "design": 3, "selection": False,
                        "laws": [Law("normal", (mu, 1.0)) for mu in (0.0, 0.001, 0.002, 0.003)]},
}


def size_rep(sc: dict, rng: np.random.Generator, n_s: int, j_h4: int, n_t: int, j_test: int,
             z: float = Z7) -> dict[str, Any]:
    """One replication: the four baselines' search statistics, the value under each form, the design's estimate."""
    q, d = sc["q"], sc["direction"]
    laws = sc["laws"]
    if sc["shared"]:
        X0 = laws[0].draw(rng, (n_s, j_h4))
        X = [X0 + (law.median() - laws[0].median()) for law in laws]
    else:
        X = [law.draw(rng, (n_s, j_h4)) for law in laws]
    M = [float(np.quantile(x.ravel(), q)) for x in X]
    sds = [float(np.std(np.quantile(x, q, axis=0), ddof=1)) for x in X]
    b, w = best_worst(d, M)
    D = float(np.quantile(laws[sc["design"]].draw(rng, (n_t * j_test,)), q))
    vals = {f: form_value(f, d, M[b], M[w], sds, b, n_s, n_t, j_test, j_h4, z) for f in FORMS}
    return {"refused": {f: refused(d, D, vals[f]) for f in FORMS},
            "headroom": {f: vals[f] != M[w] for f in FORMS}, "values": vals, "M_worst": M[w], "D": D,
            "sd_star_is_winner": int(np.argmax(sds)) == b}


def run_size(name: str, reps: int = SIZE_REPS, horizon: int = 252, log: Callable | None = None) -> dict[str, Any]:
    sc = SIZE[name]
    c = counts()
    n_s, n_t = c[f"n_s_{horizon}"], c[f"n_t_{horizon}"]
    kids = _root("size", list(SIZE).index(name)).spawn(reps)
    ref = {f: 0 for f in FORMS}
    hb = {f: 0 for f in FORMS}
    dist = []
    t0 = time.perf_counter()
    for i, k in enumerate(kids):
        r = size_rep(sc, np.random.default_rng(k), n_s, c["j_h4"], n_t, c["j_test"])
        for f in FORMS:
            ref[f] += int(r["refused"][f])
            hb[f] += int(r["headroom"][f])
        dist.append(r["M_worst"] - r["values"]["sd_star"] if sc["direction"] == "floor"
                    else r["values"]["sd_star"] - r["M_worst"])
        if log and (i + 1) % 1000 == 0:
            log(f"  [size {name}] {i + 1}/{reps}, {time.perf_counter() - t0:.0f}s")
    tol = T_SELECTION if sc["selection"] else T_NO_SELECTION
    bound = c1_bound(tol, n=reps)
    p = {f: ref[f] / reps for f in FORMS}
    law = sc["laws"][sc["design"]]
    return {"part": "size", "scenario": name, "what": sc["what"], "reps": reps, "n_s": n_s, "n_t": n_t,
            "j_h4": c["j_h4"], "j_test": c["j_test"], "p0": P0, "tolerance": tol, "c1_bound": bound,
            "refusal": p, "ratio_to_p0": {f: p[f] / P0 for f in FORMS},
            "share_headroom_bound": {f: hb[f] / reps for f in FORMS},
            "c1_pass": {f: p[f] <= bound for f in FORMS},
            "c6_fails_under_old": (p["winner"] > bound) or (p["w42_r1"] > bound),
            "c6_exception": bool(sc.get("form_insensitive")),
            "floor_beyond_worst_mean": float(np.mean(dist)),
            "design_true_stat": law.quantile(sc["q"]), "elapsed_s": round(time.perf_counter() - t0, 1)}


# ------------------------------------------------------------------- Part 2: the configuration search (Gaussian)
def config_values(M: np.ndarray, sd_hat: np.ndarray, r_t: float, j_h4: int, z: float) -> dict[str, np.ndarray]:
    """Vectorised `headroom` + `limit_value` for floors (rows: replications, columns: the four baselines)."""
    b, w = np.argmax(M, axis=1), np.argmin(M, axis=1)
    rows = np.arange(M.shape[0])
    mb, mw = M[rows, b], M[rows, w]
    sd_w = sd_hat[rows, b]
    sd_s = sd_hat.max(axis=1)
    k = math.sqrt(r_t + 1.0 / j_h4)
    need = {"sd_star": mb - z * sd_s * k, "winner": mb - z * sd_w * k, "w42_r1": mb - z * sd_w * math.sqrt(r_t)}
    return {f: np.where(mw <= need[f], mw, need[f]) for f in FORMS}


def run_configs(n_configs: int = CONFIGS, reps: int = CONFIG_REPS, log: Callable | None = None) -> dict[str, Any]:
    c = counts()
    n_s, n_t, j_h4, J = c["n_s_252"], c["n_t_252"], c["j_h4"], c["j_test"]
    r_t = n_s / (J * n_t)
    root = _root("configs").spawn(n_configs)
    ratio = {f: [] for f in FORMS}
    t0 = time.perf_counter()
    for ci, ss in enumerate(root):
        k_cfg, k_rep = ss.spawn(2)
        g = np.random.default_rng(k_cfg)
        s = np.exp(g.uniform(0.0, math.log(8.0), 4))                   # per-seed sds over a ratio of eight
        se0 = math.sqrt(2.0) * float(np.median(s)) / math.sqrt(j_h4)  # a pair's standard error
        mu = -g.uniform(0.0, 1.0, 4) * g.uniform(0.0, 4.0) * se0
        mu -= mu.max()
        rho = g.uniform(0.0, 0.9)
        tb = int(np.argmax(mu))
        rng = np.random.default_rng(k_rep)
        e = math.sqrt(rho) * rng.standard_normal((reps, 1)) + math.sqrt(1 - rho) * rng.standard_normal((reps, 4))
        M = mu + s / math.sqrt(j_h4) * e
        sd_hat = s * np.sqrt(rng.chisquare(j_h4 - 1, (reps, 4)) / (j_h4 - 1))
        D = mu[tb] + s[tb] * math.sqrt(r_t) * rng.standard_normal(reps)
        v = config_values(M, sd_hat, r_t, j_h4, Z7)
        for f in FORMS:
            ratio[f].append(float(np.mean(D < v[f])) / P0)
        if log and (ci + 1) % 200 == 0:
            log(f"  [configs] {ci + 1}/{n_configs}, {time.perf_counter() - t0:.0f}s")
    se_ratio = math.sqrt(T_SELECTION * P0 * (1 - T_SELECTION * P0) / reps) / P0
    out = {"part": "configs", "configs": n_configs, "reps": reps, "p0": P0,
           "max_ratio": {f: float(np.max(ratio[f])) for f in FORMS},
           "p95_ratio": {f: float(np.quantile(ratio[f], 0.95)) for f in FORMS},
           "median_ratio": {f: float(np.median(ratio[f])) for f in FORMS},
           "c5_max_bound": T_SELECTION + 3.5 * se_ratio, "c5_p95_bound": 1.0 + 3.0 * se_ratio,
           "elapsed_s": round(time.perf_counter() - t0, 1)}
    out["c5_pass"] = {f: out["max_ratio"][f] <= out["c5_max_bound"] and out["p95_ratio"][f] <= out["c5_p95_bound"]
                      for f in FORMS}
    out["c6_fails_under_old"] = (not out["c5_pass"]["winner"]) or (not out["c5_pass"]["w42_r1"])
    return out


# ----------------------------------------------------------------------------- shared pieces of Parts 3 and 4
def _search_readings(laws, ss: np.random.SeedSequence, cal, nJ: int, shared: bool = False, pay_spend=None):
    """Four baselines' full readings: W42-R1's generator for its measures (each baseline's own parameters, or one
    set for all), `net_month_12` from each law (one draw for all four when `shared`, shifted by the median's
    difference)."""
    sl = T._sl(cal, cal)
    kids = ss.spawn(2 * len(R.BASELINES))
    out, base = {}, {}
    common = laws[0].draw(np.random.default_rng(kids[1]), (len(cal), nJ), T.FEE) if shared else None
    for i, (b, law) in enumerate(zip(R.BASELINES, laws)):
        pay, spend = T.PARAMS[b][1:] if pay_spend is None else pay_spend
        r = T._reading(b, _ints(kids[2 * i]), pay=pay, spend=spend, J=nJ, starts=cal, cal=cal)
        x = (common + (law.median(T.FEE) - laws[0].median(T.FEE))) if shared else \
            law.draw(np.random.default_rng(kids[2 * i + 1]), (len(cal), nJ), T.FEE)
        x[sl < R2.YEAR] = np.nan
        base[b] = r
        out[b] = R.BaselineReading(r.name, r.block, r.reading, r.starts, r.seeds, {**dict(r.values), R2.NET12_KEY: x})
    return out, base


def _rule(rs, base, cal, test_starts, src):
    return R2.setting_rule(rs, h4=T._bind(base, cal), search_calendar=cal, fee_unit=T.FEE, fee_source=R.FEE_SOURCE,
                           test_starts=test_starts, test_starts_source=src,
                           net12_source={b: SYNTH_UNITS_SHA for b in R.BASELINES}).values


def record_values(v: dict, rec: dict, test_starts: dict) -> dict[str, float]:
    """One limit's value under each form, from the rule's own record (W42-R1's beside, the winner form recomputed)."""
    h = int(rec["horizon"])
    bl = list(R.BASELINES)
    M = [rec["baseline_values"][b] for b in bl]
    sds = [rec["sd_per_seed"][b] for b in bl]
    out = {"sd_star": float(rec["value"]), "w42_r1": float(rec["value_w42_r1_headroom"])}
    out["winner"] = form_value("winner", rec["direction"], M[bl.index(rec["best"])], M[bl.index(rec["worst"])], sds,
                               bl.index(rec["best"]), int(v["search_starts"][str(h)]), int(test_starts[h]),
                               R.TEST_SEEDS, int(v["seeds"]), float(rec["headroom_z"]))
    return out


def _held_out_calendar(n: int = NHO) -> tuple[str, ...]:
    d = np.arange(np.datetime64(R.HELD_OUT_FIRST), np.datetime64(R.HELD_OUT_LAST) + np.timedelta64(1, "D"))
    days = [str(x) for x in d[np.is_busday(d)]]
    return tuple(days[:n])


# ---------------------------------------------------------------------------------- Part 3: the joint read
JOINT_PARAMS = (0.7, 0.3)                    # one W42-R1 generator parameter set for all four (p16's in its tests)
JOINT_NET = Law("normal", (4.0, 20.0))


def run_joint(chunk: int = 0, search_draws: int = 25, held_out_draws: int = JOINT_HELD_OUT,
              log: Callable | None = None) -> dict[str, Any]:
    """One chunk of the joint read: per search draw, the count of its held-out draws in which the design (every
    measure from the baselines' one law) passes all seven limits, and each limit, under each form."""
    from extended import h4_audit as HA

    nJ = int(HA.H4_J)
    cal = T._calendar(1)
    hcal = _held_out_calendar()
    test_starts = {h: R.complete_starts(len(hcal), h) for h in R.HORIZONS}
    src = {"file": R.HELD_OUT_CALENDAR, "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": len(hcal)}
    hsl = T._sl(hcal, hcal)
    names = [L.name for L in R2.LIMITS]
    per_draw = []
    t0 = time.perf_counter()
    for i, ss in enumerate(_root("joint", chunk).spawn(search_draws)):
        k_s, k_h = ss.spawn(2)
        rs, base = _search_readings([JOINT_NET] * 4, k_s, cal, nJ, pay_spend=JOINT_PARAMS)
        v = _rule(rs, base, cal, test_starts, src)
        recs = {x["name"]: x for x in v["limits"]["values"]}
        vals = {n: record_values(v, recs[n], test_starts) for n in names}
        dirs = {n: recs[n]["direction"] for n in names}
        row = {"all": {f: 0 for f in FORMS}, "limit": {n: {f: 0 for f in FORMS} for n in names},
               "headroom": {n: recs[n]["binds"] == "headroom" for n in names}}
        for kh in k_h.spawn(held_out_draws):
            ka, kb = kh.spawn(2)
            d = T._reading("design", _ints(ka), pay=JOINT_PARAMS[0], spend=JOINT_PARAMS[1], J=R.TEST_SEEDS,
                           starts=hcal, cal=hcal)
            x = JOINT_NET.draw(np.random.default_rng(kb), (len(hcal), R.TEST_SEEDS), T.FEE)
            x[hsl < R2.YEAR] = np.nan
            unit = {**dict(d.values), R2.NET12_KEY: x}
            est = {n: R2.limit_estimate(v, hsl, unit, n) for n in names}
            for f in FORMS:
                ok = [not refused(dirs[n], est[n], vals[n][f]) for n in names]
                row["all"][f] += int(all(ok))
                for n, o in zip(names, ok):
                    row["limit"][n][f] += int(o)
        per_draw.append(row)
        if log:
            log(f"  [joint {chunk}] search draw {i + 1}/{search_draws}, {time.perf_counter() - t0:.0f}s")
    return {"part": "joint", "chunk": chunk, "held_out_draws": held_out_draws, "per_draw": per_draw,
            "elapsed_s": round(time.perf_counter() - t0, 1)}


def aggregate_joint(chunks: Sequence[dict]) -> dict[str, Any]:
    rows = [r for c in chunks for r in c["per_draw"]]
    m = chunks[0]["held_out_draws"]
    names = list(rows[0]["limit"])
    out: dict[str, Any] = {"part": "joint", "search_draws": len(rows), "held_out_draws": m, "p0": P0,
                           "target": R.POWER_TARGET}
    jp, jse = {}, {}
    for f in FORMS:
        sh = [r["all"][f] / m for r in rows]
        jp[f], jse[f] = float(np.mean(sh)), cluster_se(sh)
    out["joint_pass"], out["joint_se"] = jp, jse
    out["c2_bound"] = {f: R.POWER_TARGET - 3.0 * jse[f] for f in FORMS}
    out["c2_pass"] = {f: jp[f] >= out["c2_bound"][f] for f in FORMS}
    lim = {}
    for n in names:
        hb = float(np.mean([r["headroom"][n] for r in rows]))
        rec: dict[str, Any] = {"share_headroom_bound": hb}
        for f in FORMS:
            sh = [1.0 - r["limit"][n][f] / m for r in rows]
            p, se = float(np.mean(sh)), cluster_se(sh)
            bound = c1_bound(T_SELECTION, se=se) if math.isfinite(se) else None
            rec[f] = {"refusal": p, "c1_bound": bound,
                      "c1_pass": (hb == 0.0) or (bound is not None and p <= bound)}
        lim[n] = rec
    out["limits"] = lim
    out["c1_pass"] = {f: all(lim[n][f]["c1_pass"] for n in names) for f in FORMS}
    out["c6_fails_under_old"] = any(not (out["c2_pass"][f] and out["c1_pass"][f]) for f in ("winner", "w42_r1"))
    return out


# ------------------------------------------------------------------------------- Part 4: the added limit, e2e
E2E: dict[str, dict[str, Any]] = {
    "distinct": {"what": "four baselines with distinct, positive medians: the worst binds",
                 "baselines": [Law("normal", (mu, 20.0)) for mu in (2.0, 4.0, 6.0, 8.0)],
                 "margin": Law("normal", (10.0, 20.0)), "curve": True, "anchor": "worst", "headroom": False},
    "equal": {"what": "four baselines of one law, drawn independently (a real selection)",
              "baselines": [Law("normal", (4.0, 20.0))] * 4, "margin": Law("normal", (6.0, 20.0)),
              "curve": True, "anchor": "best", "headroom": True, "selection": True},
    "identical": {"what": "four baselines with one shared draw of one law: the headroom binds",
                  "baselines": [Law("normal", (4.0, 20.0))] * 4, "shared": True,
                  "margin": Law("normal", (6.0, 20.0)), "curve": True, "anchor": "best", "headroom": True,
                  "selection": False},
    "two_humped": {"what": "paid or not: a lumpy law, its median near the gap between the humps",
                   "baselines": [Law("two_humped", (p, 12.0, 4.0, -4.0, 1.5)) for p in (0.51, 0.53, 0.55, 0.57)],
                   "margin": Law("two_humped", (0.65, 12.0, 4.0, -4.0, 1.5)), "curve": False, "anchor": "worst",
                   "headroom": False},
    "behind": {"what": "every baseline's typical user behind after a year: the floor at or below zero",
               "baselines": [Law("normal", (mu, 10.0)) for mu in (-6.0, -4.0, -3.0, -2.0)],
               "margin": Law("normal", (2.0, 10.0)), "curve": True, "anchor": "worst", "headroom": False},
    "distinct_headroom": {"what": "four distinct baselines, paired (one shared draw, medians a fiftieth of a fee unit "
                                  "apart): the headroom binds with the baselines distinct",
                          "baselines": [Law("normal", (mu, 20.0)) for mu in (4.0, 4.02, 4.04, 4.06)], "shared": True,
                          "margin": Law("normal", (6.0, 20.0)), "curve": True, "anchor": "best", "headroom": True,
                          "selection": False},
}


def _read_net(values, x: np.ndarray) -> float:
    """The design's point estimate of the added limit through W42-R2's public path (the other measures zero)."""
    z = np.broadcast_to(0.0, x.shape)
    unit = {k: z for k in R2.REQUIRED}
    unit[R2.NET12_KEY] = x
    return R2.limit_estimate(values, np.full(x.shape[0], R2.YEAR), unit, R2.NET12_LIMIT.name)


def run_e2e(name: str, search_draws: int = SEARCH_DRAWS, held_out_draws: int = HELD_OUT_DRAWS,
            log: Callable | None = None) -> dict[str, Any]:
    from extended import h4_audit as HA

    sc = E2E[name]
    nJ = int(HA.H4_J)
    cal = T._calendar(1)
    test_starts = {h: R.complete_starts(NHO, h) for h in R.HORIZONS}
    src = {"file": R.HELD_OUT_CALENDAR, "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": NHO}
    n_test, J = test_starts[R2.YEAR], R.TEST_SEEDS
    laws = sc["baselines"]
    meds = [law.median(T.FEE) for law in laws]
    worst_i, best_i = int(np.argmin(meds)), int(np.argmax(meds))
    designs: dict[str, Law] = {"margin": sc["margin"], "equal_to_best": laws[best_i],
                               "equal_to_worst": laws[worst_i], "do_nothing": DO_NOTHING}
    anchor = laws[best_i if sc["anchor"] == "best" else worst_i]
    se_ho = anchor.median_se(T.FEE, n_test * J)
    if sc["curve"]:
        for t in CURVE_T:
            designs[f"curve_t{t:+.0f}"] = anchor.shifted(t * se_ho / T.FEE)
    inside = {f: {d: [] for d in designs} for f in FORMS}
    floors = {f: [] for f in FORMS}
    binds, c4_bad, forms_differ = [], 0, 0
    t0 = time.perf_counter()
    for r, ss in enumerate(_root("e2e", list(E2E).index(name)).spawn(search_draws)):
        k_search, k_ho = ss.spawn(2)
        rs, base = _search_readings(laws, k_search, cal, nJ, bool(sc.get("shared")))
        v = _rule(rs, base, cal, test_starts, src)
        rec = next(x for x in v["limits"]["values"] if x["name"] == R2.NET12_LIMIT.name)
        fl = record_values(v, rec, test_starts)
        binds.append(rec["binds"])
        forms_differ += int(len({round(fl[f], 9) for f in FORMS}) > 1)
        for f in FORMS:
            floors[f].append(fl[f])
        for (dname, law), kd in zip(designs.items(), k_ho.spawn(len(designs))):
            n_in = {f: 0 for f in FORMS}
            for kh in kd.spawn(held_out_draws):
                e = _read_net(v, law.draw(np.random.default_rng(kh), (n_test, J), T.FEE))
                for f in FORMS:
                    n_in[f] += int(e >= fl[f])
                if dname == "do_nothing":
                    c4_bad += int((e < fl["sd_star"]) != bool(v["r2"]["floor_refuses_do_nothing"]))
            for f in FORMS:
                inside[f][dname].append(n_in[f] / held_out_draws)
        if log:
            log(f"  [e2e {name}] search draw {r + 1}/{search_draws}, floor {fl['sd_star']:.2f} "
                f"(winner {fl['winner']:.2f}, w42_r1 {fl['w42_r1']:.2f}), {time.perf_counter() - t0:.0f}s")
    pr = {f: {d: float(np.mean(inside[f][d])) for d in designs} for f in FORMS}
    out: dict[str, Any] = {
        "part": "e2e", "scenario": name, "what": sc["what"], "search_draws": search_draws,
        "held_out_draws": held_out_draws, "p0": P0,
        "share_headroom_bound": float(np.mean([b == "headroom" for b in binds])),
        "floor_mean": {f: float(np.mean(floors[f])) for f in FORMS}, "pass_rate": pr,
        "false_refusal_equal_to_best": {f: 1 - pr[f]["equal_to_best"] for f in FORMS},
        "false_refusal_equal_to_worst": {f: 1 - pr[f]["equal_to_worst"] for f in FORMS},
        "curve_anchor": sc["anchor"], "held_out_se_at_anchor": se_ho, "draws_where_forms_differ": forms_differ,
        "elapsed_s": round(time.perf_counter() - t0, 1)}
    out["c3_pass"] = pr["sd_star"]["margin"] >= R.POWER_TARGET
    out["c4_pass"] = c4_bad == 0
    if sc["headroom"]:
        tol = T_SELECTION if sc.get("selection") else T_NO_SELECTION
        se = {f: cluster_se([1 - x for x in inside[f]["equal_to_best"]]) for f in FORMS}
        out["c1_bound"] = {f: c1_bound(tol, se=se[f]) for f in FORMS}
        out["c1_pass"] = {f: out["false_refusal_equal_to_best"][f] <= out["c1_bound"][f] for f in FORMS}
        out["c6_fails_under_old"] = (not out["c1_pass"]["winner"]) or (not out["c1_pass"]["w42_r1"])
    else:
        out["c6_exception_forms_identical"] = forms_differ == 0
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", choices=PARTS, required=True)
    ap.add_argument("--scenario", action="append")
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--search-draws", type=int, default=None)
    ap.add_argument("--held-out-draws", type=int, default=None)
    a = ap.parse_args(argv)
    log = lambda s: print(s, flush=True)   # noqa: E731
    if a.part == "size":
        for name in a.scenario or list(SIZE):
            print(json.dumps(run_size(name, a.reps or SIZE_REPS, log=log), sort_keys=True), flush=True)
    elif a.part == "configs":
        print(json.dumps(run_configs(log=log), sort_keys=True), flush=True)
    elif a.part == "joint":
        print(json.dumps(run_joint(a.chunk, a.search_draws or 25, a.held_out_draws or JOINT_HELD_OUT, log=log),
                         sort_keys=True), flush=True)
    else:
        for name in a.scenario or list(E2E):
            print(json.dumps(run_e2e(name, a.search_draws or SEARCH_DRAWS, a.held_out_draws or HELD_OUT_DRAWS,
                                     log=log), sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
