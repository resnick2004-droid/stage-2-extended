"""W42-R2: W42-R1 with one added limit (a floor on the median 12-month net cash) and a corrected headroom
(`docs/plans/WAVE42_SETTING_RULE_R2.md`; Q-221, E-296).

W42-R1 (`extended/wave42.py`, pinned by E-283 and never edited) has no dollar magnitude of profit among its limits or
its composite: its "money" dimension is P_B, a share. W42-R2 adds **one limit in W42-R1's own `LimitSpec` form**:

    net_month_12_p50: measure (12) at m = 12, key `net_month_12`, a floor, horizon 252, statistic p50

and adds `net_month_12` to the required inputs, with its a priori range (-inf, inf) (W42-R1's own range for
`net_month_1` to `net_month_3`). And (E-296) every limit's headroom counts M_best's own search-year noise beside the
held-out test's (`headroom`). Nothing else changes: the six dimensions, their weights, the budgets, delta*, the power
and the rest of the limits' formula are W42-R1's.

**One code path.** The rule is not re-implemented. `setting_rule` runs **W42-R1's own function objects** -- the same
code objects, byte for byte -- over a fresh copy of W42-R1's module namespace in which only the tables named in
`OVERRIDES` differ (`rebind`). W42-R1's module is never mutated. Every output but the limits' headroom comes from
W42-R1's code; the limits' estimates and per-seed sds too (section 6 of W42-R1: the worst baseline's estimate, or the
best's minus z_L times the headroom's error when that is stricter, z_L joint over the limits set).

After W42-R1's code has run, three named steps complete the output (the declaration's sections 3 and 4):
1. the application record names W42-R2's script and output;
2. **the corrected headroom, for every one of the seven limits (E-296; the red team's B-1, the lead's ruling):**
   W42-R1's headroom counts only the held-out test's coin noise of the drawn winner (`extended/wave42.py` lines
   809-810); W42-R2's (`headroom`) counts the held-out test's and M_best's own search-year noise at H4's seed count,
   combined as independent errors, **both at sd*, the largest per-seed sd among the four baselines** (the drawn
   winner's sd is selected by the same draw that selects the winner). Each limit's value, which term binds and its
   vacuity are then re-selected by W42-R1's section 6 steps 3-4 (`limit_value`; the added limit's vacuity read against
   its own a priori range, (-inf, inf)), and its baseline checks re-read at the new value through W42-R1's
   `limit_check`; W42-R1's own value is kept beside (`value_w42_r1_headroom`), and beside, deciding nothing, sd*'s
   95 % chi-square interval (m-2) and the refusal share a design equal to the best meets at other read sizes (m-1);
3. the block `r2`: the parent rule and its pin, the added limit's value, where `net_month_12` came from, and whether
   the floor refuses the do-nothing journey (it does exactly when its value is above zero).

This is the one place W42-R2 does not run W42-R1's code unchanged: W42-R1's inline headroom is computed and then
replaced. Everything else is W42-R1's code.

`net_floor=False` runs W42-R1's tables through the same mechanism and returns W42-R1's output unchanged; it exists for
the identity test only (`tests/test_wave42_r2.py`). The declared application, `scripts/wave42_r2_apply.py`, never
passes it.

Nothing here draws randomness, reads a file, a bar or a result.
"""
from __future__ import annotations

import math
import re
import types
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import stats

from extended import wave42 as R

# ---------------------------------------------------------------------------------- the constants (the doc, 2)
RULE_ID = "W42-R2"
PARENT_RULE_ID = R.RULE_ID
PARENT_ROW = "E-283"
#: W42-R1's pinned files, by the LF sha256 E-283 records (the parent this rule is a delta of)
PARENT_SHA256 = {
    "docs/plans/WAVE42_SETTING_RULE.md": "2179ff4a366d7ba61ecd425674dab8fd361d80a1713d4b8630943c5683662441",
    "extended/wave42.py": "dc6d84c69bcff7210eb5564b613e488c95f72cbe8e783796190c364ad5b723e2",
    "scripts/wave42_apply.py": "b817eada1f00115253ed7e02b7f9eed40b4afa17c5166da6e775296369b1cc77",
    "config/w42_r1_pin.json": "ae7f6044c382c316c9005acba73c7b54ab5768dfa4a78f1a19f83d021fb56dc4",
}
PARENT_PIN_COMMIT = "5e6da6e8c99e6cf2284af19781c2116549cb28e4"
OUTPUT_NAME = "w42_r2_values.csv"
APPLY_SCRIPT = "scripts/wave42_r2_apply.py"
YEAR = 12 * R.MONTH                                   # the 252-session year window (W42-R1's horizon 252)
NET12_KEY = "net_month_12"                            # measure (12) at m = 12: rel_u[252], the 12-month net cash
NET12_KIND = "net_dollars"                            # dollars with no a priori lower end (net cash runs below zero)

#: the one added limit, in W42-R1's `LimitSpec` form
NET12_LIMIT = R.LimitSpec("net_month_12_p50", "(12)", NET12_KEY, "floor", YEAR, "p50", False, NET12_KIND)
LIMITS = R.LIMITS + (NET12_LIMIT,)
#: the per-unit measures W42-R2 requires: W42-R1's, and `net_month_12` on E_252 with W42-R1's net range
REQUIRED = {**R.REQUIRED, NET12_KEY: (YEAR, -math.inf, math.inf)}
HORIZONS = tuple(sorted({d.horizon for d in R.DIMENSIONS} | {lim.horizon for lim in LIMITS}))

#: E-296: the headroom's error term, the held-out test's coin noise and M_best's own search-year noise combined
HEADROOM_FORM = ("sqrt(se_test^2 + se_search^2); se_test = sd* sqrt(n_search / (J n_test)), "
                 "se_search = sd* / sqrt(J_H4), sd* = the largest per-seed sd among the four baselines")
_VACUOUS_END = "at or beyond the a priori end of its range"
_VACUOUS_UNITS = "beyond every baseline unit (no baseline's unit distribution crosses it)"
#: m-1: other read sizes, beside, deciding nothing -- DRAFT_F-13's screen and deciding sizes (wt/wt-fs1 f543e25,
#: lines 471-475): (its seed count, its start stride)
READS_BESIDE = {"f13_screen": (4, 4), "f13_deciding": (16, 1)}
SD_INTERVAL_LEVEL = 0.95                               # m-2: sd*'s chi-square interval, beside, deciding nothing

#: W42-R2's constants: W42-R1's, with these replaced or added (the doc's delta table)
CONSTANTS_DELTA: dict[str, Any] = {
    "RULE_ID": RULE_ID, "OUTPUT_NAME": OUTPUT_NAME, "PARENT_RULE_ID": PARENT_RULE_ID, "PARENT_ROW": PARENT_ROW,
    "PARENT_PIN_COMMIT": PARENT_PIN_COMMIT, "YEAR": YEAR, "NET12_KEY": NET12_KEY, "NET12_KIND": NET12_KIND,
    "HEADROOM_FORM": HEADROOM_FORM,
}
CONSTANTS: dict[str, Any] = {**R.CONSTANTS, **CONSTANTS_DELTA}

#: the only names of W42-R1's namespace W42-R2 replaces; everything else is W42-R1's
OVERRIDES = ("RULE_ID", "OUTPUT_NAME", "LIMITS", "REQUIRED", "HORIZONS", "CONSTANTS")

_HEX64 = re.compile(r"[0-9a-f]{64}")


# ------------------------------------------------------------------------------------------- the one code path
def rebind(module: types.ModuleType, overrides: Mapping[str, Any]) -> dict[str, Any]:
    """A fresh copy of `module`'s namespace with `overrides` applied, in which every function defined in `module` is
    re-made from **its own code object** with the copy as its globals: the same code, reading the copy's tables. The
    module itself is never changed. Every override must name a table the module already has."""
    src = vars(module)
    unknown = sorted(set(overrides) - set(src))
    if unknown:
        raise KeyError(f"{module.__name__} has no {unknown}: an override replaces an existing table only")
    ns = dict(src)
    ns.update(overrides)
    for name, f in list(ns.items()):
        if isinstance(f, types.FunctionType) and f.__globals__ is src:
            g = types.FunctionType(f.__code__, ns, f.__name__, f.__defaults__, f.__closure__)
            g.__kwdefaults__ = None if f.__kwdefaults__ is None else dict(f.__kwdefaults__)
            g.__doc__, g.__qualname__, g.__module__ = f.__doc__, f.__qualname__, f.__module__
            g.__dict__.update(f.__dict__)
            ns[name] = g
    return ns


def tables(net_floor: bool = True) -> dict[str, Any]:
    """The overrides: W42-R2's tables, or (net_floor False) W42-R1's own, read from its module at call time."""
    if not net_floor:
        return {k: getattr(R, k) for k in OVERRIDES}
    return {"RULE_ID": RULE_ID, "OUTPUT_NAME": OUTPUT_NAME, "LIMITS": LIMITS, "REQUIRED": REQUIRED,
            "HORIZONS": HORIZONS, "CONSTANTS": CONSTANTS}


_NS_CACHE: dict[bool, tuple[tuple, dict[str, Any]]] = {}


def _fingerprint(net_floor: bool) -> tuple:
    return tuple(vars(R).items()) + tuple(tables(net_floor).items())


def _same(a: tuple, b: tuple) -> bool:
    return len(a) == len(b) and all(x[0] == y[0] and x[1] is y[1] for x, y in zip(a, b))


def namespace(net_floor: bool = True) -> dict[str, Any]:
    """W42-R1's namespace over W42-R2's tables (or W42-R1's), built once per process (m-6) and built again only when
    an object in W42-R1's module or in the tables is not the one it was built from (so a test's monkeypatch reaches
    it, and its restoration too)."""
    fp = _fingerprint(net_floor)
    hit = _NS_CACHE.get(net_floor)
    if hit is None or not _same(hit[0], fp):
        _NS_CACHE[net_floor] = (fp, rebind(R, tables(net_floor)))
    return _NS_CACHE[net_floor][1]


# --------------------------------------------------------------------------- the public scoring path (the survey's)
def limit_estimate(values: Mapping[str, Any], sessions_left: Sequence[int], out: Mapping[str, Any],
                   name: str) -> float:
    """W42-R1's `limit_estimate` over W42-R2's limits (the added one among them)."""
    return namespace()["limit_estimate"](values, sessions_left, out, name)


def limit_per_seed_sd(values: Mapping[str, Any], sessions_left: Sequence[int], out: Mapping[str, Any],
                      name: str) -> float:
    """W42-R1's `limit_per_seed_sd` over W42-R2's limits."""
    return namespace()["limit_per_seed_sd"](values, sessions_left, out, name)


def limit_check(values: Mapping[str, Any], sessions_left: Sequence[int], out: Mapping[str, Any], name: str,
                value: float, level_: float = R.LIMIT_CHECK_LEVEL) -> dict[str, Any]:
    """W42-R1's `limit_check` over W42-R2's limits: the point estimate decides (E-230), the check beside."""
    return namespace()["limit_check"](values, sessions_left, out, name, value, level_)


#: unchanged by W42-R2 (they read no limit table): the survey imports these from W42-R1 as before
composite_per_seed = R.composite_per_seed
null_composites = R.null_composites
do_nothing_floor = R.do_nothing_floor
above_floor = R.above_floor
pinned_inputs = R.pinned_inputs
values_from_rows = R.values_from_rows


def null_net12(fee_unit: float) -> dict[str, float]:
    """The null journeys' 12-month net cash, from W42-R1's `null_journeys` (V-4): each stops in its first month, so its
    net at month 12 is its net at month 3 -- zero for the do-nothing journey, minus one fee unit for the quitter."""
    return {k: float(v["net_month_3"]) for k, v in R.null_journeys(fee_unit).items()}


# ----------------------------------------------------------------------------- the corrected headroom (E-296)
def headroom(m_best: float, sd: float, n_search: int, n_test: int, j_test: int, j_h4: int, z: float,
             direction: str) -> dict[str, float]:
    """The needed value of a limit (the declaration's section 4.2), at the per-seed sd `sd` the rule passes -- sd*,
    the largest among the four baselines (B-1). A design equal to the best baseline is read at the held-out test with
    error se_test = sd sqrt(n_search / (j_test n_test)) (W42-R1's term: the per-seed statistic's sd, scaled from one
    seed's n_search starts to the test's j_test x n_test units), and M_best itself, pooled over H4's j_h4 seeds,
    carries se_search = sd / sqrt(j_h4). The two are independent (other coins, other days), so the design's estimate
    minus M_best has sd at most se = sqrt(se_test^2 + se_search^2) when sd bounds both baselines' per-seed sds, and the
    needed value is M_best + z se (a ceiling) or M_best - z se (a floor)."""
    sd_best = sd
    if direction not in ("ceiling", "floor"):
        raise ValueError(f"a limit is a ceiling or a floor, not {direction!r}")
    if min(n_search, n_test, j_test, j_h4) < 1 or not math.isfinite(sd_best) or sd_best < 0:
        raise ValueError("the headroom needs positive counts and a finite, non-negative per-seed sd")
    se_test = sd_best * math.sqrt(n_search / (j_test * n_test))
    se_search = sd_best / math.sqrt(j_h4)
    se = math.sqrt(se_test * se_test + se_search * se_search)
    sign = 1.0 if direction == "ceiling" else -1.0
    return {"se_test": se_test, "se_search": se_search, "se": se, "needed": m_best + sign * z * se}


def refusal_at_read(z: float, n_search: int, n_test: int, j_test: int, j_h4: int, n_read: int, j_read: int) -> float:
    """m-1, beside, deciding nothing: the share of reads in which a design equal to the best baseline, read on n_read
    starts by j_read seeds of the same history, falls beyond a headroom-bound value set for the held-out read: the sd
    cancels, 1 - Phi(z sqrt(n_s / (j_test n_test) + 1 / j_h4) / sqrt(n_s / (j_read n_read) + 1 / j_h4)). At the
    held-out read itself it is 1 - Phi(z), the nominal share."""
    held = math.sqrt(n_search / (j_test * n_test) + 1.0 / j_h4)
    read = math.sqrt(n_search / (j_read * n_read) + 1.0 / j_h4)
    return float(stats.norm.sf(z * held / read))


def sd_interval(sd: float, j_h4: int, level: float = SD_INTERVAL_LEVEL) -> list[float]:
    """m-2, beside, deciding nothing: the chi-square interval of a per-seed sd over j_h4 seeds (normal-theory; for a
    lumpy or lattice statistic only indicative). Not propagated into the headroom."""
    a = (1.0 - level) / 2.0
    k = j_h4 - 1
    return [float(sd * math.sqrt(k / stats.chi2.ppf(1.0 - a, k))), float(sd * math.sqrt(k / stats.chi2.ppf(a, k)))]


def limit_value(direction: str, kind: str, m_worst: float, needed: float, pooled: np.ndarray) -> dict[str, Any]:
    """W42-R1's section 6 steps 3-4, as written: the limit is the worst baseline's estimate unless that is inside the
    needed value (a tie is the worst's), then its vacuity -- at or beyond the a priori end of its range (a share
    ceiling at 1, a days ceiling at W + 1, a floor at 0; net cash has no end), or beyond every pooled baseline unit."""
    ceil_ = direction == "ceiling"
    if (ceil_ and m_worst >= needed) or (not ceil_ and m_worst <= needed):
        val, binds = float(m_worst), "worst_baseline"
    else:
        val, binds = float(needed), "headroom"
    top = {"share": 1.0, "days": R.W + 1.0}.get(kind, math.inf)
    bottom = -math.inf if kind == NET12_KIND else 0.0
    if (ceil_ and val >= top) or (not ceil_ and val <= bottom):
        vac = _VACUOUS_END
    elif (ceil_ and val >= float(pooled.max())) or (not ceil_ and val <= float(pooled.min())):
        vac = _VACUOUS_UNITS
    else:
        vac = None
    return {"value": val, "binds": binds, "vacuous": vac is not None, "vacuous_reason": vac}


def _spec(name: str) -> R.LimitSpec:
    return next(L for L in LIMITS if L.name == name)


# ------------------------------------------------------------------------------------------------------- the rule
def _refuse(msg: str) -> R.Wave42Refused:
    return R.Wave42Refused(f"W42-R2 refuses its input: {msg}")


def _without_net12(readings: Mapping[str, R.BaselineReading]) -> dict[str, R.BaselineReading]:
    return {k: R.BaselineReading(b.name, b.block, b.reading, b.starts, b.seeds,
                                 {m: x for m, x in b.values.items() if m != NET12_KEY})
            for k, b in readings.items()}


def _binding(readings: Mapping[str, R.BaselineReading], h4: R.H4Binding,
             net12_source: Mapping[str, str] | None) -> R.H4Binding:
    """The binding W42-R1's code checks the readings against. `net12_source` None: the collection carries
    `net_month_12`, and its `readings_sha256` must cover it (W42-R1's own check). Otherwise `net_month_12` came from
    H4-B's units files beside the collection (one sha256 per baseline, which the application checks against the
    collection's `units_files_sha256`): the readings without it must reproduce the collection's `readings_sha256`,
    and the binding then carries the digest of the readings with it. A mismatch leaves the collection's binding in
    place, so W42-R1's own digest check refuses -- after its held-out guard, which runs first."""
    if net12_source is None:
        return h4
    if not isinstance(net12_source, Mapping) or sorted(net12_source) != sorted(R.BASELINES) \
            or any(not (isinstance(v, str) and _HEX64.fullmatch(v)) for v in net12_source.values()):
        raise _refuse(f"net_month_12's source names one units file sha256 (64 hex digits) per baseline {R.BASELINES}")
    if not isinstance(h4, R.H4Binding) or not isinstance(h4.manifest, Mapping):
        return h4
    if R.readings_digest(_without_net12(readings)) != h4.manifest.get("readings_sha256"):
        return h4
    return R.H4Binding(h4.result_sha256, {**h4.manifest, "readings_sha256": R.readings_digest(readings)})


def setting_rule(readings: Mapping[str, R.BaselineReading] | Sequence[R.BaselineReading], *, h4: R.H4Binding,
                 search_calendar: Sequence[str], fee_unit: float, fee_source: str, test_starts: Mapping[int, int],
                 test_starts_source: Mapping[str, Any], net12_source: Mapping[str, str] | None = None,
                 net_floor: bool = True) -> R.Wave42Values:
    """W42-R2: W42-R1's `setting_rule`, its own code, over W42-R2's tables; then the three steps of the module's
    docstring. `net_floor=False` is W42-R1 itself (the identity test's switch; the application never passes it)."""
    if not isinstance(readings, Mapping):
        readings = {b.name: b for b in readings}
    ns = namespace(net_floor)
    kw = dict(search_calendar=search_calendar, fee_unit=fee_unit, fee_source=fee_source, test_starts=test_starts,
              test_starts_source=test_starts_source)
    if not net_floor:
        return ns["setting_rule"](readings, h4=h4, **kw)
    hx = _binding(readings, h4, net12_source)
    out = dict(ns["setting_rule"](readings, h4=hx, **kw).values)

    # step 1: the application record
    out["application"] = {"script": APPLY_SCRIPT, "output": OUTPUT_NAME,
                          "rule": "applied once: the script refuses when any Wave 4.2 output exists"}

    # step 2: the corrected headroom for every limit (E-296), then W42-R1's steps 3-4 at it
    sl = np.asarray(_sessions_left(readings[R.BASELINES[0]].starts, search_calendar))
    vals = {b: readings[b].values for b in R.BASELINES}
    B = float(out["budgets"]["primary"])
    per = {b: ns["unit_values"](vals[b], B) for b in R.BASELINES}
    j_h4 = int(out["seeds"])
    lims = []
    for x in out["limits"]["values"]:
        x = dict(x)
        if x.get("status") != "set":
            lims.append(x)
            continue
        L = _spec(x["name"])
        rows = sl >= L.horizon
        sds = {b: float(ns["limit_per_seed_sd"](out, sl, vals[b], L.name)) for b in R.BASELINES}
        sd_b = max(R.BASELINES, key=lambda b: (sds[b], -R.BASELINES.index(b)))   # B-1: the largest of the four
        n_s, n_t = int(rows.sum()), int(test_starts[L.horizon])
        z = float(x["headroom_z"])
        hr = headroom(x["baseline_values"][x["best"]], sds[sd_b], n_s, n_t, R.TEST_SEEDS, j_h4, z, L.direction)
        pooled = np.concatenate([per[b][L.key][rows].ravel() for b in R.BASELINES])
        sel = limit_value(L.direction, L.kind, x["baseline_values"][x["worst"]], hr["needed"], pooled)
        x.update({"value_w42_r1_headroom": x["value"], "binds_w42_r1_headroom": x["binds"],
                  "headroom_needed_w42_r1": x["headroom_needed"], **sel, "headroom_needed": hr["needed"],
                  "best_se_test": hr["se_test"], "best_se_search": hr["se_search"], "headroom_se": hr["se"],
                  "best_sd_per_seed": sds[x["best"]], "sd_per_seed": sds, "sd_star": sds[sd_b],
                  "sd_star_baseline": sd_b, "headroom_form": HEADROOM_FORM,
                  "beside": {"sd_star_interval": sd_interval(sds[sd_b], j_h4), "sd_star_interval_level":
                             SD_INTERVAL_LEVEL, "refusal_at_read": {
                                 "held_out": refusal_at_read(z, n_s, n_t, R.TEST_SEEDS, j_h4, n_t, R.TEST_SEEDS),
                                 **{k: refusal_at_read(z, n_s, n_t, R.TEST_SEEDS, j_h4, -(-n_s // stride), j)
                                    for k, (j, stride) in READS_BESIDE.items()}},
                             "decides": "nothing (m-1, m-2): the headroom's rate is the held-out read's"}})
        x["baseline_checks"] = {b: ns["limit_check"](out, sl, vals[b], L.name, sel["value"]) for b in R.BASELINES}
        if L.kind == NET12_KIND:
            x["a_priori_range"] = ["-inf", "inf"]
        lims.append(x)
    out["limits"] = {**out["limits"], "values": lims, "headroom_form": HEADROOM_FORM, "h4_seeds": j_h4}
    net = next(x for x in lims if x["name"] == NET12_LIMIT.name)
    npw = next(x for x in lims if x["name"] == "not_paid_within_B")
    out["inactivity_guards"] = {**out["inactivity_guards"], "not_paid_within_B":
                                "vacuous: only CHARTER 3.8 (c)'s long-run gate stops a quitter" if npw["vacuous"]
                                else "live"}

    # step 3: the r2 block
    nn = null_net12(fee_unit)
    reach = [max(R.HORIZONS)]
    checks = {}
    for name, x in nn.items():
        arm = {k: np.zeros((1, 1)) for k in REQUIRED}
        arm.update({k: np.full((1, 1), float(v)) for k, v in R.null_journeys(fee_unit)[name].items()})
        arm[NET12_KEY] = np.full((1, 1), x)
        c = ns["limit_check"](out, reach, arm, NET12_LIMIT.name, net["value"])
        checks[name] = {"net_month_12": x, "inside": c["inside"]}
    bites = bool(net["value"] > nn["do_nothing"])
    out["h4"] = {**out["h4"], "collection_readings_sha256": h4.manifest["readings_sha256"]}
    out["r2"] = {
        "rule_id": RULE_ID, "parent": {"rule_id": PARENT_RULE_ID, "row": PARENT_ROW, "commit": PARENT_PIN_COMMIT,
                                       "sha256": dict(PARENT_SHA256)},
        "added_limit": NET12_LIMIT.name, "key": NET12_KEY, "horizon": YEAR, "stat": NET12_LIMIT.stat,
        "direction": NET12_LIMIT.direction, "value": net["value"], "binds": net["binds"],
        "value_w42_r1_headroom": net["value_w42_r1_headroom"], "headroom_form": HEADROOM_FORM,
        "limits_set": out["limits"]["limits_set"], "headroom_z": out["limits"]["headroom_z"],
        "net12_source": ("the collection (its readings_sha256 covers it)" if net12_source is None
                         else {"units_files_sha256": dict(sorted(net12_source.items()))}),
        "null_journeys": checks,
        "inactivity": ("live: the floor is above zero, so the do-nothing journey (zero on every unit) fails it"
                       if bites else "not a guard: the floor is at or below zero, so the do-nothing journey passes "
                                     "it; W42-R1's guards (not_paid_within_B, the do-nothing composite floor, the "
                                     "long-run gate) stand as before"),
        "floor_refuses_do_nothing": bites,
        "report_with_and_without_floor": ("F-13's finalists are shown with and without this floor, deciding nothing "
                                          "(B-3: the floor's form was ruled after the early look)"),
    }
    return R.Wave42Values(out)


def _sessions_left(starts: Sequence[str], calendar: Sequence[str]) -> list[int]:
    """W42-R1's sessions left (section 1.2): calendar sessions from the start to the last, the start counted."""
    cal = [str(d) for d in calendar]
    pos = {d: i for i, d in enumerate(cal)}
    return [len(cal) - pos[str(d)] for d in starts]


__all__ = ["RULE_ID", "PARENT_RULE_ID", "PARENT_ROW", "PARENT_SHA256", "PARENT_PIN_COMMIT", "OUTPUT_NAME",
           "APPLY_SCRIPT", "YEAR", "NET12_KEY", "NET12_KIND", "NET12_LIMIT", "LIMITS", "REQUIRED", "HORIZONS",
           "CONSTANTS", "CONSTANTS_DELTA", "OVERRIDES", "HEADROOM_FORM", "READS_BESIDE", "headroom", "limit_value",
           "refusal_at_read", "sd_interval", "rebind", "tables", "namespace", "setting_rule",
           "limit_estimate", "limit_per_seed_sd", "limit_check", "composite_per_seed", "null_composites",
           "do_nothing_floor", "above_floor", "pinned_inputs", "values_from_rows", "null_net12"]
