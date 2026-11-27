"""W42-R2: W42-R1 with one added limit, a floor on the median 12-month net cash (`docs/plans/WAVE42_SETTING_RULE_R2.md`).

W42-R1 (`extended/wave42.py`, pinned by E-283 and never edited) has no dollar magnitude of profit among its limits or
its composite: its "money" dimension is P_B, a share. W42-R2 adds **one limit in W42-R1's own `LimitSpec` form**:

    net_month_12_p50: measure (12) at m = 12, key `net_month_12`, a floor, horizon 252, statistic p50

and adds `net_month_12` to the required inputs, with its a priori range (-inf, inf) (W42-R1's own range for
`net_month_1` to `net_month_3`). Nothing else changes: the six dimensions, their weights, the budgets, delta*, the
power and the limits' formula are W42-R1's.

**One code path.** The rule is not re-implemented. `setting_rule` runs **W42-R1's own function objects** -- the same
code objects, byte for byte -- over a fresh copy of W42-R1's module namespace in which only the tables named in
`OVERRIDES` differ (`rebind`). W42-R1's module is never mutated. So the added limit's value comes from W42-R1's limit
formula as written (section 6 of W42-R1: the worst baseline's estimate, or the best's minus z_L times its test
standard error when that is stricter, z_L joint over the limits set), and every other output from W42-R1's code.

After W42-R1's code has run, three named steps complete the output (the declaration's section 3):
1. the application record names W42-R2's script and output;
2. the added limit's vacuity is read against its own a priori range (W42-R1's code reads "a floor at 0" as the end
   of a range, which holds for its counts but not for net cash, which runs below zero); the value is not touched;
3. the block `r2`: the parent rule and its pin, the added limit's value, where `net_month_12` came from, and whether
   the floor refuses the do-nothing journey (it does exactly when its value is above zero).

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

#: W42-R2's constants: W42-R1's, with these replaced or added (the doc's delta table)
CONSTANTS_DELTA: dict[str, Any] = {
    "RULE_ID": RULE_ID, "OUTPUT_NAME": OUTPUT_NAME, "PARENT_RULE_ID": PARENT_RULE_ID, "PARENT_ROW": PARENT_ROW,
    "PARENT_PIN_COMMIT": PARENT_PIN_COMMIT, "YEAR": YEAR, "NET12_KEY": NET12_KEY, "NET12_KIND": NET12_KIND,
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


def namespace(net_floor: bool = True) -> dict[str, Any]:
    """W42-R1's namespace over W42-R2's tables (or W42-R1's), built afresh at each call."""
    return rebind(R, tables(net_floor))


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

    # step 2: the added floor's vacuity against its own a priori range (-inf, inf): only "beyond every unit" applies
    vals = {b: np.asarray(readings[b].values[NET12_KEY], dtype=float) for b in R.BASELINES}
    sl = np.asarray(_sessions_left(readings[R.BASELINES[0]].starts, search_calendar))
    pooled = np.concatenate([vals[b][sl >= YEAR].ravel() for b in R.BASELINES])
    lims = [dict(x) for x in out["limits"]["values"]]
    net = next(x for x in lims if x["name"] == NET12_LIMIT.name)
    beyond = bool(net["value"] <= float(pooled.min()))
    net["vacuous"] = beyond
    net["vacuous_reason"] = "beyond every baseline unit (no baseline's unit distribution crosses it)" if beyond else None
    net["a_priori_range"] = ["-inf", "inf"]
    out["limits"] = {**out["limits"], "values": lims}

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
        "limits_set": out["limits"]["limits_set"], "headroom_z": out["limits"]["headroom_z"],
        "net12_source": ("the collection (its readings_sha256 covers it)" if net12_source is None
                         else {"units_files_sha256": dict(sorted(net12_source.items()))}),
        "null_journeys": checks,
        "inactivity": ("live: the floor is above zero, so the do-nothing journey (zero on every unit) fails it"
                       if bites else "not a guard: the floor is at or below zero, so the do-nothing journey passes "
                                     "it; W42-R1's guards (not_paid_within_B, the do-nothing composite floor, the "
                                     "long-run gate) stand as before"),
        "floor_refuses_do_nothing": bites,
    }
    return R.Wave42Values(out)


def _sessions_left(starts: Sequence[str], calendar: Sequence[str]) -> list[int]:
    """W42-R1's sessions left (section 1.2): calendar sessions from the start to the last, the start counted."""
    cal = [str(d) for d in calendar]
    pos = {d: i for i, d in enumerate(cal)}
    return [len(cal) - pos[str(d)] for d in starts]


__all__ = ["RULE_ID", "PARENT_RULE_ID", "PARENT_ROW", "PARENT_SHA256", "PARENT_PIN_COMMIT", "OUTPUT_NAME",
           "APPLY_SCRIPT", "YEAR", "NET12_KEY", "NET12_KIND", "NET12_LIMIT", "LIMITS", "REQUIRED", "HORIZONS",
           "CONSTANTS", "CONSTANTS_DELTA", "OVERRIDES", "rebind", "tables", "namespace", "setting_rule",
           "limit_estimate", "limit_per_seed_sd", "limit_check", "composite_per_seed", "null_composites",
           "do_nothing_floor", "above_floor", "pinned_inputs", "values_from_rows", "null_net12"]
