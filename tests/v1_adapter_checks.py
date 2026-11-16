"""Q-18: `extended/v1_adapter.py` and `scripts/p14_validation.py` against the vendored V1 parts they adapt, on synthetic
data -- no bars, no engine run. Run by `tests/test_p14_validation.py` in a process of its own (it puts the vendored tree
on `sys.path`, CLAUDE.md).

    python tests/v1_adapter_checks.py          # every check: 'HOLDS: <name>' for each, exit 0; 'FAILS: <name>' exit 3

* `engine_hook`: `X.Engine`'s path hook with `mc_seed=[SEED_B1, 9]` is the vendored `Engine`'s, value for value; with
  another seed only the two Monte-Carlo errors move; `run`, `_run` and `path_problems` are the vendored methods.
* `b1_era` / `b1_pooled`: `X.part_b1(seed=V.SEED_B1)` gives the vendored `part_b1`'s rows exactly on a subject named S1
  (the era rule, flagged) and on one without eras (the pooled rule); another seed moves the replicates; a subject
  named P14 with `era_spans` takes the era rule (the vendored part would not).
* `c1`: `X.part_c1(seed=V.SEED_C1)` gives the vendored `part_c1`'s rows (all but the note naming the seed function), the
  same engine calls with the same trade sets; another seed draws other realisations.
* `slip`: `X.part_slip` runs D-583's eight stressed arms (never the base) on `p16_slip_stress.stress`'s trades with
  `rebound`'s e and bound, reads the base from the registered run, and its reading is the lowest level whose growth at
  the bound is at or below zero, recomputed here; an unknown exit kind is refused.
* `rows` / `writing` / `refusals`: the runner's registered-row picker, its file and variant ledger (a temporary folder),
  and its refusals before anything is built (a declared run outside a clean checkout, one part, three workers).
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import v1_adapter as X  # noqa: E402  (puts the vendored tree on sys.path)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

VS, V, ps16 = X.VS, X.V, X.ps16
KEYS = [1.0, 2.0]
ERAS = ((2020, 2022), (2023, 2026))
MARGIN = 49.0


# ------------------------------------------------------------------------------------------------ synthetic inputs


def trades(seed: int = 7, n_days: int = 300) -> tuple[pd.DataFrame, list[str]]:
    """Synthetic offered trades over `n_days` sessions spread from 2020 to 2026: 0-3 a day, a 100-tick stop, at 1R and
    2R a net outcome, gross, cost and exit kind (2R offered on about four in five)."""
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range("2020-01-02", "2026-07-16")
    days = [d.strftime("%Y-%m-%d") for d in cal[np.sort(rng.choice(len(cal), n_days, replace=False))]]
    rows = []
    for d in days:
        for k in range(int(rng.integers(0, 4))):
            row = {"date": d, "year": int(d[:4]), "entry_t": float(k), "side": "long" if rng.random() < 0.5 else "short",
                   "S": 100, "stop_ticks": 100.0}
            for R in KEYS:
                on = R == 1.0 or rng.random() < 0.8
                kind = str(rng.choice(["s", "t", "f", "b"], p=[0.45, 0.35, 0.05, 0.15]))
                gross = {"s": -1.0, "t": R, "f": float(rng.normal(0, 0.5)), "b": 0.0}[kind]
                cost = 0.03 + 0.01 * (kind in "sfb")
                row[f"r_{R:g}"] = gross - cost if on else np.nan
                row[f"g_{R:g}"] = gross if on else np.nan
                row[f"c_{R:g}"] = cost if on else np.nan
                row[f"o_{R:g}"] = kind if on else ""
            rows.append(row)
    return pd.DataFrame(rows), days


class FakeSubject(VS.Subject):
    """A V1 subject whose `rebuild` is a fingerprint of the trade set (no `score_fv3_grid.gate_blocks`)."""

    def rebuild(self, t: pd.DataFrame) -> dict:
        return {"n": int(len(t)), "sum_r1": float(np.nansum(t["r_1"].to_numpy(float))),
                "sum_r2": float(np.nansum(t["r_2"].to_numpy(float))), "days": int(t["date"].nunique())}


def hook_base(sink: list):
    def base(shift, p, paths):
        v = V.path_values(paths, MARGIN)
        g, b = V.growth_on_required(v["net"], v["required"], len(paths[0].path.cash_series))
        return {"pf_growth_on_base_p50": g, "pf_required_p90": b}

    return object(), base


def subject(name: str, *, eras: bool, flagged: bool, n_led: int = 50, seed: int = 7) -> FakeSubject:
    t, days = trades(seed)
    sums, cnts = V.day_sums(t, days, KEYS)
    alphas = (V.ALPHA, V.ALPHA / n_led)
    yrs = np.array([int(d[:4]) for d in days])
    if eras and flagged:
        idx = [np.nonzero((yrs >= lo) & (yrs <= hi))[0][None, :] for lo, hi in ERAS]
        b = V.era_rule_bounds(sums, cnts, idx, 21, alphas)
    else:
        b = V.block_bounds(sums, cnts, np.arange(len(days))[None, :], 21, alphas)
    lb05 = {R: float(b["lb"][0, 0, j]) for j, R in enumerate(KEYS)}
    lbn = {R: float(b["lb"][1, 0, j]) for j, R in enumerate(KEYS)}
    e_by = {R: float(np.nanmean(t[f"r_{R:g}"])) for R in KEYS}
    extra = {"era_spans": ERAS, "flagged": flagged, "lb05_by": lb05} if eras else {}
    return FakeSubject(
        name=name, describe=f"synthetic {name}", t=t, days=days, keys=list(KEYS), tv=0.5, e_by=e_by, lb_by=lbn,
        kw={}, blocks=[], margin=MARGIN, block_days=21, crr=1.0, frr=2.0, n_led=n_led, alpha_verdict=V.ALPHA / n_led,
        seed=1, hook_base=hook_base, arm_names={"bound": "verdict", "point": "point"}, ref_file="", ref_rows=None,
        ref_paths="", ref_pairs={}, extra=extra)


class FakeEngine:
    """`Engine.run`'s interface: each call recorded; its rows a deterministic function of the blocks (the trade set's
    fingerprint) and the bound."""

    def __init__(self, sub):
        self.sub, self.calls, self.labels = sub, [], []

    def growth(self, blocks, lb_by) -> float:
        if blocks is None:
            return 0.25
        shift = 0.0 if lb_by is None else float(lb_by[self.sub.frr])
        return 0.02 + blocks["sum_r1"] / max(blocks["n"], 1) + 0.5 * shift

    def run(self, label, *, blocks=None, e_by=None, lb_by=None, mean_block=None):
        self.calls.append({"label": label, "blocks": blocks, "e_by": e_by, "lb_by": lb_by, "mean_block": mean_block})
        self.labels.append(label)
        g = self.growth(blocks, lb_by)
        out = {}
        for k, arm in enumerate(("bound", "point")):
            row = {c: float(i + 1) + 0.5 * k for i, c in enumerate(dict.fromkeys(VS.READ + VS.BESIDE + VS.IDENT_COLS))}
            row["pf_growth_on_base_p50"] = g + 0.1 * k
            row["mean_combine_purchases"] = float(blocks["n"]) if blocks else 0.0
            out[arm] = row
        return out


def registered(sub) -> dict:
    return FakeEngine(sub).run("registered")


def same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    if isinstance(a, (float, np.floating)) or isinstance(b, (float, np.floating)):
        try:
            return float(a) == float(b)
        except (TypeError, ValueError):
            return False
    return a == b


def rows_same(xs: list[dict], ys: list[dict], skip: tuple[str, ...] = ()) -> list[str]:
    if len(xs) != len(ys):
        return [f"{len(xs)} rows against {len(ys)}"]
    out = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        keys = (set(x) | set(y)) - set(skip)
        out += [f"row {i} {k}: {x.get(k)!r} against {y.get(k)!r}" for k in sorted(keys) if not same(x.get(k), y.get(k))]
    return out


# ------------------------------------------------------------------------------------------------ the checks


def check_engine_hook() -> list[str]:
    rng = np.random.default_rng(11)
    paths = []
    for _ in range(40):
        cash = np.concatenate([[10000.0], 10000.0 + np.cumsum(rng.normal(5, 120, 60))])
        pays = sorted(rng.choice(60, int(rng.integers(0, 4)), replace=False).tolist())
        paths.append(SimpleNamespace(path=SimpleNamespace(
            cash_series=cash.tolist(), initial_bankroll=10000.0, days_to_first_payout=(pays[0] if pays else None),
            payout_gaps=[b - a for a, b in zip(pays, pays[1:])])))
    sub = subject("S1", eras=False, flagged=False)
    a = VS.Engine(sub, 4, 1, None).hook("point", 0.0, paths)
    b = X.Engine(sub, 4, 1, None, mc_seed=[V.SEED_B1, 9]).hook("point", 0.0, paths)
    c = X.Engine(sub, 4, 1, None, mc_seed=20261952).hook("point", 0.0, paths)
    out = rows_same([a], [b])
    moved = {k for k in a if not same(a[k], c[k])}
    if not moved or not moved <= {"growth_se", "required_p90_se"}:
        out.append(f"another seed moved {sorted(moved)}, not only the Monte-Carlo errors")
    for m in ("run", "_run", "path_problems"):
        if getattr(X.Engine, m) is not getattr(VS.Engine, m):
            out.append(f"X.Engine.{m} is not the vendored method")
    return out


def check_b1_era() -> list[str]:
    sub = subject("S1", eras=True, flagged=True)
    a = VS.part_b1(sub, 0, 300, 2, 3)
    b = X.part_b1(sub, seed=V.SEED_B1, reps=300, verify=2, auto=3, subject_index=0)
    out = rows_same(a, b)
    if not any(r["rule"] == "era_rule" and r["registered_rule"] for r in a):
        out.append("the vendored part read no era rule (the check would be vacuous)")
    c = X.part_b1(sub, seed=20261950, reps=300, verify=2, auto=3)
    if not rows_same(a, c, skip=()):
        out.append("another seed gave the same replicates")
    p14 = subject("P14", eras=True, flagged=True)
    d = X.part_b1(p14, seed=V.SEED_B1, reps=300, verify=2, auto=3)
    out += rows_same([{**r, "subject": "S1"} for r in d], a)
    e = VS.part_b1(p14, 0, 300, 0, 3)
    if any(r["rule"] == "era_rule" for r in e):
        out.append("the vendored part read the era rule for a subject not named S1 (the adapter's reason is gone)")
    return out


def check_b1_pooled() -> list[str]:
    sub = subject("S2", eras=False, flagged=False)
    a = VS.part_b1(sub, 1, 300, 2, 2)
    b = X.part_b1(sub, seed=V.SEED_B1, reps=300, verify=2, auto=2, subject_index=1)
    out = rows_same(a, b)
    if {r["rule"] for r in a} != {"pooled"}:
        out.append("the pooled subject read another rule")
    return out


def check_c1() -> list[str]:
    sub = subject("S1", eras=False, flagged=False)
    reg = registered(sub)
    ea, eb, ec = FakeEngine(sub), FakeEngine(sub), FakeEngine(sub)
    a = VS.part_c1(ea, reg, 1)
    b = X.part_c1(eb, reg, seed=V.SEED_C1, subject_index=1)
    out = rows_same(a, b, skip=("note",))
    if [c["label"] for c in ea.calls] != [c["label"] for c in eb.calls] or \
            [c["blocks"] for c in ea.calls] != [c["blocks"] for c in eb.calls]:
        out.append("the engine calls differ")
    if len(ea.calls) != len(V.C1_ARMS) * V.C1_REALISATIONS:
        out.append(f"{len(ea.calls)} engine calls")
    c = X.part_c1(ec, reg, seed=20261951)
    seeds_a = {r["realisation_seed"] for r in a if r["section"] == "c1"}
    seeds_c = {r["realisation_seed"] for r in c if r["section"] == "c1"}
    if seeds_a & seeds_c or [x["blocks"] for x in ec.calls] == [x["blocks"] for x in ea.calls]:
        out.append("another seed drew the same realisations")
    if not all("20261951" in r["note"] for r in c if r["section"] == "c1"):
        out.append("the note does not name the seed")
    return out


def check_slip() -> list[str]:
    sub = subject("P14", eras=False, flagged=False)
    reg = registered(sub)
    eng = FakeEngine(sub)

    def rebound(tt):
        e = {R: float(np.nanmean(tt[f"r_{R:g}"])) for R in KEYS}
        return e, {R: e[R] - 0.05 for R in KEYS}, {"era_flagged": False}

    rows = X.part_slip(eng, reg, rebound)
    out = []
    arms = ps16.arms()
    want = [f"slip {a['arm']}" for a in arms if a["arm"] != "base"]
    if eng.labels != want:
        out.append(f"the runs {eng.labels}, not {want}")
    for a, call in zip([a for a in arms if a["arm"] != "base"], eng.calls):
        tt = ps16.stress(sub.t, a)
        e, lb, _ = rebound(tt)
        if call["blocks"] != sub.rebuild(tt) or call["e_by"] != e or call["lb_by"] != lb:
            out.append(f"{a['arm']}: not run on its stressed trades with their re-read bounds")
    base = [r for r in rows if r["section"] == "slip" and r["scheme"] == "base"]
    if len(base) != 2 or any(not same(r["pf_growth_on_base_p50"], reg["bound" if r["arm"] == "verdict" else "point"][
            "pf_growth_on_base_p50"]) for r in base):
        out.append("the base rows are not the registered run's")
    g = {"base": reg["bound"]["pf_growth_on_base_p50"]}
    for a in arms:
        if a["arm"] != "base":
            tt = ps16.stress(sub.t, a)
            g[a["arm"]] = eng.growth(sub.rebuild(tt), rebound(tt)[1])
    for fam, levels in (("A", ps16.LEVELS_A), ("B", ps16.LEVELS_B)):
        names = {a["level"]: a["arm"] for a in arms if a["family"] in ("base", fam)}
        exp = next((lv for lv in levels if not g[names[lv]] > 0), ps16.NONE)
        got = [r for r in rows if r["section"] == "slip_reading" and r["family"] == fam]
        if len(got) != 1 or got[0]["lowest_level_growth_at_bound_at_or_below_zero"] != exp:
            out.append(f"family {fam}: the reading {got} is not {exp}")
    if all(r["lowest_level_growth_at_bound_at_or_below_zero"] == ps16.NONE for r in rows
           if r["section"] == "slip_reading"):
        out.append("no family turned: the synthetic case does not exercise the reading")
    bad = sub.t.copy()
    bad.loc[bad.index[0], "o_1"] = "x"                # an offered 1R outcome with no D-583 kind
    try:
        X.part_slip(FakeEngine(dataclasses.replace(sub, t=bad)), reg, rebound)
        out.append("an unknown exit kind was not refused")
    except (ValueError, SystemExit):
        pass
    return out


def runner():
    spec = importlib.util.spec_from_file_location("p14_validation", ROOT / "scripts" / "p14_validation.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_rows() -> list[str]:
    m = runner()
    d = pd.DataFrame([
        {"section": "gate", "shift": "point", "enforcement_p": 0.0, "v": 1},
        {"section": "gate", "shift": "point", "enforcement_p": 0.1, "v": 2},
        {"section": "gate", "shift": "lower_bound", "enforcement_p": 0.0, "v": 3},
        {"section": "gate_at_ledger_n", "shift": "lower_bound", "enforcement_p": 0.0, "v": 4},
        {"section": "placement_on", "shift": "point", "enforcement_p": 0.0, "v": 5}])
    out = []
    r = m.p14_rows(d, "gate_at_ledger_n")
    if (r["bound"]["v"], r["point"]["v"]) != (4, 1):
        out.append(f"verdict rows {r['bound']['v']}, {r['point']['v']}")
    r = m.p14_rows(d, "gate")
    if (r["bound"]["v"], r["point"]["v"]) != (3, 1):
        out.append(f"0.05 rows {r['bound']['v']}, {r['point']['v']}")
    try:
        m.p14_rows(pd.concat([d, d.iloc[[3]]]), "gate_at_ledger_n")
        out.append("two verdict rows were not refused")
    except SystemExit:
        pass
    seeds = {m.SEED_B1, m.SEED_C1, m.SEED_MC}
    if seeds != {20261950, 20261951, 20261952} or m.P14_CAMPAIGN_SEED != 20261131:
        out.append(f"the seeds {sorted(seeds)}, {m.P14_CAMPAIGN_SEED}")
    return out


def check_writing() -> list[str]:
    m = runner()
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        rows = [{"section": "identity", "subject": "P14", "holds": True, "check": "x"},
                {"section": "a1", "subject": "P14", "arm": "verdict", "pf_growth_on_base_p50": 0.1}]
        csv = m.write_reading(rows, {"paths": 4, "parts": ["A1"]}, ["a1 mean_block 5", "a1 mean_block 21"],
                              Path(tmp), 20261131)
        man = json.loads(Path(str(csv) + ".manifest.json").read_text(encoding="utf-8"))
        if man.get("variant_count") != 2 or man.get("exploratory") is not True or man.get("seed") != 20261131:
            out.append(f"the manifest's count, label or seed: {man.get('variant_count')}, {man.get('exploratory')}, "
                       f"{man.get('seed')}")
        if man.get("script") != "scripts/p14_validation.py":
            out.append(f"the manifest's script {man.get('script')}")
        led = [json.loads(x) for x in (Path(tmp) / "variants.jsonl").read_text(encoding="utf-8").splitlines() if x]
        if len(led) != 2 or {x["prereg_id"] for x in led} != {"Q-18:p14_validation"} or not all(x["exploratory"]
                                                                                              for x in led):
            out.append(f"the variant ledger {led}")
        back = pd.read_csv(csv)
        if list(back.columns[:2]) != ["section", "reading"] or len(back) != 2:
            out.append(f"the file's columns {list(back.columns)[:3]}")
    return out


def check_refusals() -> list[str]:
    m = runner()
    out = []
    for argv in ([], ["--part", "B1"], ["--check", "--workers", "3"], ["--check", "--part", "A2"]):
        try:
            code = m.main(argv)
        except SystemExit as e:
            code = e.code
        if code != 2:
            out.append(f"{argv}: exit {code}, not 2")
    return out


CHECKS = {"engine_hook": check_engine_hook, "b1_era": check_b1_era, "b1_pooled": check_b1_pooled, "c1": check_c1,
          "slip": check_slip, "rows": check_rows, "writing": check_writing, "refusals": check_refusals}


def main() -> int:
    code = 0
    for name, fn in CHECKS.items():
        try:
            bad = fn()
        except Exception as e:                     # noqa: BLE001 -- a check that raises fails, with its reason
            bad = [f"raised {type(e).__name__}: {e}"]
        if bad:
            code = 3
            print(f"FAILS: {name} -- " + "; ".join(bad[:6]), flush=True)
        else:
            print(f"HOLDS: {name}", flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
