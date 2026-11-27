"""W42-R2's power check (`docs/plans/WAVE42_SETTING_RULE_R2.md` section 7): synthetic journeys only (no bar, no result
file, nothing written). A strict line must show power, not only size.

Each replication:
1. draws four synthetic baselines' full readings on a synthetic search calendar (every weekday of the search years) at
   H4's seed count: W42-R1's tests' generator for every W42-R1 measure, and `net_month_12` from the scenario's
   per-unit law (blank off E_252, as H4's units are);
2. applies **W42-R2's rule end to end** (`extended.wave42_r2.setting_rule`) to set the floor -- its value, and whether
   the worst baseline or the headroom binds;
3. for each design, draws its held-out units -- `TEST_SEEDS` seeds by the complete held-out starts at 252 of a
   synthetic held-out calendar -- `HELD_OUT_DRAWS` times, and reads the floor through W42-R2's `limit_estimate` at the
   point estimate (inside when at or above the value, E-230).

Randomness: one root `numpy.random.SeedSequence` whose entropy is derived from this check's name by sha256 (no
literal, no other block's seed), children by `spawn_key` (scenario, replication, stream). Per-unit laws are iid
across start days and seeds: the check bounds coin luck, as W42-R1's headroom does, not a lucky history.

    python tests/w42r2_power.py [--search-draws N] [--held-out-draws M] [--scenario NAME]

prints each scenario's figures; `tests/test_wave42_r2.py` runs it at a reduced count.
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
from typing import Any, Callable

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import wave42 as R  # noqa: E402
from extended import wave42_r2 as R2  # noqa: E402

CHECK_NAME = "W42-R2 power check, Q-221"
ROOT_ENTROPY = int.from_bytes(hashlib.sha256(CHECK_NAME.encode("utf-8")).digest()[:16], "big")
SEARCH_DRAWS = 40                      # search-year replications per scenario (the full check)
HELD_OUT_DRAWS = 10                    # held-out draws per design per search replication
CURVE_T = (-2.0, 0.0, 2.0, 4.0, 6.0)   # design medians at the anchor baseline's + t held-out coin standard errors
SYNTH_UNITS_SHA = "e" * 64             # a synthetic units-file sha256 (the application checks the real one)


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


# ---------------------------------------------------------------------------------------------- per-unit laws
@dataclass(frozen=True)
class Law:
    """A per-unit law of `net_month_12`, in fee units: `normal` (mu, sd) or `two_humped` (p paid; paid mu, sd;
    unpaid mu, sd) -- a unit paid or not, the lumpy case where a median is least stable."""
    kind: str
    p: tuple[float, ...]

    def draw(self, rng: np.random.Generator, shape: tuple[int, ...], fee: float) -> np.ndarray:
        if self.kind == "normal":
            mu, sd = self.p
            return fee * rng.normal(mu, sd, shape)
        if self.kind == "zero":
            return np.zeros(shape)
        p, pm, ps, um, us = self.p
        paid = rng.random(shape) < p
        return fee * np.where(paid, rng.normal(pm, ps, shape), rng.normal(um, us, shape))

    def median(self, fee: float) -> float:
        if self.kind == "normal":
            return fee * self.p[0]
        if self.kind == "zero":
            return 0.0
        p, pm, ps, um, us = self.p
        cdf = lambda x: p * stats.norm.cdf(x, pm, ps) + (1 - p) * stats.norm.cdf(x, um, us) - 0.5   # noqa: E731
        return fee * optimize.brentq(cdf, min(pm, um) - 20 * max(ps, us), max(pm, um) + 20 * max(ps, us))

    def median_se(self, fee: float, n: int) -> float:
        """The sd of the pooled median of n iid units: 1 / (2 f(m) sqrt(n))."""
        if self.kind == "zero":
            return 0.0
        m = self.median(1.0)
        if self.kind == "normal":
            dens = stats.norm.pdf(m, self.p[0], self.p[1])
        else:
            p, pm, ps, um, us = self.p
            dens = p * stats.norm.pdf(m, pm, ps) + (1 - p) * stats.norm.pdf(m, um, us)
        return fee / (2.0 * dens * math.sqrt(n))

    def shifted(self, d: float) -> "Law":
        if self.kind != "normal":
            raise ValueError("a curve shifts a normal law only")
        return Law("normal", (self.p[0] + d, self.p[1]))


DO_NOTHING = Law("zero", ())

#: the scenarios: four baselines' laws (in W42-R1's baseline order), and the designs read at the held-out test.
#: `shared`: the four share one draw of the first law, each shifted by its own median's difference (paired baselines,
#: their differences exact), so the best is always the same one and the headroom's regime is fixed. `anchor`: the
#: baseline the pass curve is placed around (the worst where the worst binds, the best where the headroom binds).
SCENARIOS: dict[str, dict[str, Any]] = {
    "distinct": {"what": "four baselines with distinct, positive medians: the worst binds",
                 "baselines": [Law("normal", (mu, 20.0)) for mu in (2.0, 4.0, 6.0, 8.0)],
                 "margin": Law("normal", (10.0, 20.0)), "curve": True, "anchor": "worst"},
    "equal": {"what": "four baselines of one law, drawn independently: the worst's estimate binds",
              "baselines": [Law("normal", (4.0, 20.0))] * 4,
              "margin": Law("normal", (6.0, 20.0)), "curve": True, "anchor": "worst"},
    "identical": {"what": "four baselines with one shared draw of one law: the headroom binds",
                  "baselines": [Law("normal", (4.0, 20.0))] * 4, "shared": True,
                  "margin": Law("normal", (6.0, 20.0)), "curve": True, "anchor": "best"},
    "two_humped": {"what": "paid or not: a lumpy law, its median near the gap between the humps",
                   "baselines": [Law("two_humped", (p, 12.0, 4.0, -4.0, 1.5)) for p in (0.51, 0.53, 0.55, 0.57)],
                   "margin": Law("two_humped", (0.65, 12.0, 4.0, -4.0, 1.5)), "curve": False, "anchor": "worst"},
    "behind": {"what": "every baseline's typical user behind after a year: the floor at or below zero",
               "baselines": [Law("normal", (mu, 10.0)) for mu in (-6.0, -4.0, -3.0, -2.0)],
               "margin": Law("normal", (2.0, 10.0)), "curve": True, "anchor": "worst"},
    "distinct_headroom": {"what": "four distinct baselines, paired (one shared draw, medians a fiftieth of a fee unit "
                                  "apart): the headroom binds with the baselines distinct",
                          "baselines": [Law("normal", (mu, 20.0)) for mu in (4.0, 4.02, 4.04, 4.06)], "shared": True,
                          "margin": Law("normal", (6.0, 20.0)), "curve": True, "anchor": "best"},
}


# ------------------------------------------------------------------------------------------------- the check
def _ints(ss: np.random.SeedSequence) -> int:
    return int(ss.generate_state(1, dtype=np.uint64)[0] % (2 ** 63))


def _search_readings(laws, ss: np.random.SeedSequence, cal, nJ: int, shared: bool = False):
    """Four baselines' full readings: W42-R1's generator for its measures, `net_month_12` from each law (one draw of
    the first law for all four when `shared`, each shifted by its median's difference from the first's)."""
    sl = T._sl(cal, cal)
    kids = ss.spawn(2 * len(R.BASELINES))
    out, base = {}, {}
    common = laws[0].draw(np.random.default_rng(kids[1]), (len(cal), nJ), T.FEE) if shared else None
    for i, (b, law) in enumerate(zip(R.BASELINES, laws)):
        _, pay, spend = T.PARAMS[b]
        r = T._reading(b, _ints(kids[2 * i]), pay=pay, spend=spend, J=nJ, starts=cal, cal=cal)
        if shared:
            x = common + (law.median(T.FEE) - laws[0].median(T.FEE))
        else:
            x = law.draw(np.random.default_rng(kids[2 * i + 1]), (len(cal), nJ), T.FEE)
        x[sl < R2.YEAR] = np.nan
        base[b] = r
        out[b] = R.BaselineReading(r.name, r.block, r.reading, r.starts, r.seeds, {**dict(r.values), R2.NET12_KEY: x})
    return out, base


def _read_design(values, x: np.ndarray) -> float:
    """The design's point estimate of the added limit through W42-R2's public path (the other measures zero)."""
    z = np.broadcast_to(0.0, x.shape)
    unit = {k: z for k in R2.REQUIRED}
    unit[R2.NET12_KEY] = x
    return R2.limit_estimate(values, np.full(x.shape[0], R2.YEAR), unit, R2.NET12_LIMIT.name)


FORMS = ("new", "old")      # W42-R2's corrected headroom (E-296), and W42-R1's (`value_w42_r1_headroom`), one draw


def run_scenario(name: str, search_draws: int = SEARCH_DRAWS, held_out_draws: int = HELD_OUT_DRAWS,
                 nJ: int | None = None, cal=None, nho: int | None = None,
                 log: Callable[[str], None] | None = None) -> dict[str, Any]:
    """One scenario's figures: per design and per headroom form, the share of (search, held-out) draws whose estimate
    is inside the floor. Both floors come from the same W42-R2 run and are read on the same held-out draws."""
    from extended import h4_audit as HA

    sc = SCENARIOS[name]
    nJ = HA.H4_J if nJ is None else nJ
    cal = T._calendar(1) if cal is None else cal
    nho = T.NHO if nho is None else nho
    test_starts = {h: R.complete_starts(nho, h) for h in R.HORIZONS}
    src = {"file": R.HELD_OUT_CALENDAR, "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": nho}
    n_test = test_starts[R2.YEAR]
    J = R.TEST_SEEDS
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
    sidx = list(SCENARIOS).index(name)
    root = np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(sidx,))
    inside = {f: {d: 0 for d in designs} for f in FORMS}
    floors = {f: [] for f in FORMS}
    binds = {f: [] for f in FORMS}
    t0 = time.perf_counter()
    for r, ss in enumerate(root.spawn(search_draws)):
        k_search, k_ho = ss.spawn(2)
        rs, base = _search_readings(laws, k_search, cal, nJ, bool(sc.get("shared")))
        v = R2.setting_rule(rs, h4=T._bind(base, cal), search_calendar=cal, fee_unit=T.FEE,
                            fee_source=R.FEE_SOURCE, test_starts=test_starts, test_starts_source=src,
                            net12_source={b: SYNTH_UNITS_SHA for b in R.BASELINES}).values
        net = next(x for x in v["limits"]["values"] if x["name"] == R2.NET12_LIMIT.name)
        fl = {"new": float(net["value"]), "old": float(net["value_w42_r1_headroom"])}
        bd = {"new": net["binds"], "old": net["binds_w42_r1_headroom"]}
        for f in FORMS:
            floors[f].append(fl[f])
            binds[f].append(bd[f])
        kids = k_ho.spawn(len(designs))
        for (dname, law), kd in zip(designs.items(), kids):
            for kh in kd.spawn(held_out_draws):
                e = _read_design(v, law.draw(np.random.default_rng(kh), (n_test, J), T.FEE))
                for f in FORMS:
                    inside[f][dname] += int(e >= fl[f])
        if log:
            log(f"  [{name}] search draw {r + 1}/{search_draws}, floor new {fl['new']:.2f} old {fl['old']:.2f}, "
                f"{time.perf_counter() - t0:.0f}s")
    n = search_draws * held_out_draws
    z = R.limit_z(len(R2.LIMITS))
    return {
        "scenario": name, "what": sc["what"], "search_draws": search_draws, "held_out_draws": held_out_draws,
        "h4_seeds": nJ, "search_sessions": len(cal), "test_seeds": J, "test_starts_252": n_test,
        "limits_set": len(R2.LIMITS), "headroom_z": z, "nominal_false_refusal": float(stats.norm.sf(z)),
        "baseline_true_medians": dict(zip(R.BASELINES, meds)),
        "design_true_medians": {d: law.median(T.FEE) for d, law in designs.items()},
        "curve_anchor": sc["anchor"], "held_out_se_at_anchor": se_ho,
        "floor_mean": {f: float(np.mean(floors[f])) for f in FORMS},
        "floor_sd": {f: float(np.std(floors[f], ddof=1)) if search_draws > 1 else 0.0 for f in FORMS},
        "share_binds_headroom": {f: float(np.mean([x == "headroom" for x in binds[f]])) for f in FORMS},
        "pass_rate": {f: {d: inside[f][d] / n for d in designs} for f in FORMS},
        "false_refusal": {f: {d: 1.0 - inside[f][d] / n for d in ("equal_to_best", "equal_to_worst")} for f in FORMS},
        "power_margin": {f: inside[f]["margin"] / n for f in FORMS},
        "do_nothing_refused": {f: 1.0 - inside[f]["do_nothing"] / n for f in FORMS},
        "reads": n, "elapsed_s": round(time.perf_counter() - t0, 1),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--search-draws", type=int, default=SEARCH_DRAWS)
    ap.add_argument("--held-out-draws", type=int, default=HELD_OUT_DRAWS)
    ap.add_argument("--scenario", choices=list(SCENARIOS), action="append")
    a = ap.parse_args(argv)
    for name in a.scenario or list(SCENARIOS):
        res = run_scenario(name, a.search_draws, a.held_out_draws, log=lambda s: print(s, flush=True))
        print(json.dumps(res, indent=1, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
