"""Q-132's child checks (`tests/test_breakeven_fidelity_2.py` runs this in its own process: the vendored pure modules
are imported here, never into the test runner). Synthetic U1 records only -- no bar, atlas or engine run.

    python tests/breakeven2_checks.py <check>      # prints one JSON line: {"problems": [...], "seen": {...}}

The synthetic starts: business days from 2022-01-03, one start a day, each observed to 252 sessions or the calendar's
end; Combine fees on day 0 and every 21 sessions, a pass and a funded account on some starts, payouts on dates drawn
once per calendar day (so neighbouring starts share them, as real starts share sessions) and arriving relative to each
start; every 9th start carries an exact 63-session run that differed (`alt`), its cash shifted far down, so a reading at
63 sessions reads it. Seeded from `extended.breakeven_readings.TEST_SEED`, by key.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "identity"))         # walker_identity, as the runner puts it

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import breakeven_readings as BR  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import user_readings as R  # noqa: E402

N_DAYS = 760
FIRST = "2022-01-03"


def synthetic_outs(key: int, n_days: int = N_DAYS, alt_every: int = 9, pay_rate: float = 0.03) -> list[dict]:
    from propedge.research import user_journey as U

    rng = np.random.default_rng([BR.TEST_SEED, int(key)])
    dates = pd.bdate_range(FIRST, periods=n_days).strftime("%Y-%m-%d").tolist()
    pay_on = rng.random(n_days + 300) < pay_rate
    pay_amt = np.round(rng.uniform(150.0, 1800.0, n_days + 300), 2)
    reset = rng.random(n_days + 300) < 0.04
    outs = []
    for s in range(n_days):
        L = min(int(U.HORIZON), n_days - s)
        fee = np.zeros(L + 1)
        fee[0] += 49.0
        fee[21::21] += 49.0
        fee[1:] += np.where(reset[s + 1:s + L + 1], 99.0, 0.0)
        passes = [int(d) for d in range(5, L + 1) if rng.random() < 0.01][:3]
        funded = [p + 1 for p in passes if p + 1 <= L]
        start_pay = (funded[0] + 8) if funded else L + 1
        pays = [(int(j), float(pay_amt[s + j])) for j in range(start_pay, L + 1) if pay_on[s + j]]
        got = np.zeros(L + 1)
        for j, c in pays:
            got[j] += c
        init = 2000.0
        cash = init - np.cumsum(fee) + np.cumsum(got)
        rec = {"start_day": s, "start_date": dates[s], **U.start_record(cash, init, passes, funded, pays)}
        differs = []
        if s % alt_every == 0 and L > 63:
            c2 = cash[:64] - 5000.0
            rec["alt"] = {"63": U.start_record(c2, init, passes, funded, [p for p in pays if p[0] <= 63])}
            differs = [63]
        rel = cash - init
        outs.append({"rec": rec, "differs": differs, "checked": [21, 63, 126], "pay_bad": 0, "cash_bad": 0,
                     "fee_bad": 0, "record_same": True, "daily": M.daily(rel),
                     "response": {"response_day": float("nan"), "payouts_denied": 0.0, "cash_forfeited": 0.0},
                     "seed": 0})
    return outs


def summary(design: str, outs):
    from extended import user_beside as B

    srows, _ = R.summary(design, "verdict", B.BY_NAME["off"], outs, blocks=R.Q44_BLOCKS)   # W3.1: named
    return srows


def check_frame() -> tuple[list[str], dict]:
    """D1: the per-start frame's columns; its CSV text read back gives the same records (alt included) and the same
    scorecard, extra and path rows; a flipped net, a dropped alt and a dropped start are each refused."""
    from propedge.research import user_journey as U

    outs = synthetic_outs(1)
    probs = []
    st = BR.start_frame("p16", "stage2", "verdict", outs)
    if list(st.columns) != list(BR.START_FILE_COLS):
        probs.append(f"columns {list(st.columns)[:6]} are not START_FILE_COLS")
    back = BR.read_text_csv(st.to_csv(index=False))
    recs = BR.records_from_frame(back)
    for a, b in zip(outs, recs):
        r0 = a["rec"]
        if U.record_problems(r0, b) or r0["start_date"] != b["start_date"] or int(r0["start_day"]) != b["start_day"]:
            probs.append(f"start {r0['start_day']}: the record read back differs ({U.record_problems(r0, b)})")
            break
        if json.dumps(r0.get("alt"), sort_keys=True) != json.dumps(b.get("alt"), sort_keys=True):
            probs.append(f"start {r0['start_day']}: the alt read back differs")
            break
    if len(recs) != len(outs):
        probs.append(f"{len(recs)} records read back from {len(outs)}")
    raw = [float(x["rec"]["net_month"][0]) for x in outs]
    if not np.array_equal(np.asarray(raw), back["net_month_1"].to_numpy(float), equal_nan=True):
        probs.append("net_month_1 is not the engine's value bit for bit (rounded?)")
    srows = summary("p16", outs)
    ok = BR.rederive_problems(back, srows, "synthetic")
    probs += [f"the honest file: {p}" for p in ok]
    seen = {"starts": len(outs), "alt_starts": int(sum(1 for x in outs if x["rec"].get("alt"))),
            "eligible_p": int(np.isfinite(back["p_months_ahead"]).sum())}
    # negative controls, each must be refused
    i = int(np.flatnonzero((back["observed"] >= 63).to_numpy() & (back["alt"].isna()).to_numpy())[5])
    bad = back.copy()
    bad.loc[i, "net_month_2"] = -bad.loc[i, "net_month_2"] if bad.loc[i, "net_month_2"] != 0 else 1.0
    seen["flipped"] = len(BR.rederive_problems(bad, srows, "flipped"))
    noalt = back.copy()
    noalt["alt"] = np.nan
    seen["no_alt"] = len(BR.rederive_problems(noalt, srows, "no alt"))
    short = back.drop(index=3).reset_index(drop=True)
    seen["dropped"] = len(BR.rederive_problems(short, srows, "dropped"))
    for k in ("flipped", "no_alt", "dropped"):
        if not seen[k]:
            probs.append(f"the negative control {k} is not refused")
    # P's per-start unit is the card's P
    recs0 = [x["rec"] for x in outs]
    card = {(r["block"]): float(r["value"]) for r in srows if r["section"] == "scorecard" and r["measure"] == "P"}
    for block, which in BR.BLOCKS:
        d = BR.p_months_ahead(recs0, which)
        p = float(np.mean(list(d.values())) / 3.0) if d else float("nan")
        if not abs(p - card[block]) <= 1e-12:
            probs.append(f"{block}: months ahead / 3 averages {p}, the card's P is {card[block]}")
        seen[f"p_{block}_n"] = len(d)
    filled = back["p_months_ahead"].dropna()
    if not abs(float(filled.mean()) / 3.0 - card["all"]) <= 1e-12:
        probs.append("the file's p_months_ahead column does not average to the card's P")
    return probs, seen


def check_paired() -> tuple[list[str], dict]:
    """C2: the paired rows on two synthetic rule sets; the mean equals the cards' difference; the all block prints an
    interval and the judged block too few windows; identical rule sets print "identical on these trades"; a start on
    one side only is refused; the honesty label and the rare line appear once the settings are given."""
    probs, seen = [], {}
    o0, o1 = synthetic_outs(1), synthetic_outs(2)
    ahead, cards = {}, {}
    for rules, outs in (("stage2", o0), ("delay5", o1), ("stop_first", o0)):
        srows = summary("p16", outs)
        recs = [x["rec"] for x in outs]
        for block, which in BR.BLOCKS:
            ahead[("p16", rules, "verdict", block)] = BR.p_months_ahead(recs, which)
        for r in srows:
            if r["section"] == "scorecard" and r["measure"] == "P":
                cards[("p16", rules, "verdict", r["block"])] = float(r["value"])
    names = ["stage2", "stop_first", "delay5"]
    rows, bad, need = BR.paired_rows(ahead, cards, ["p16"], names, ["verdict"])
    probs += [f"honest pair: {p}" for p in bad]
    by = {(r["rules"], r["block"], r["stat"]): r for r in rows}
    for rules in ("stop_first", "delay5"):
        for block in ("all", "judged"):
            m = by[(rules, block, "mean")]["value"]
            want = cards[("p16", rules, "verdict", block)] - cards[("p16", "stage2", "verdict", block)]
            if not abs(m - want) <= 1e-12:
                probs.append(f"{rules} {block}: mean {m} against the cards' {want}")
    if by.get(("stop_first", "all", "interval"), {}).get("note") != "identical on these trades":
        probs.append("identical rule sets do not print 'identical on these trades'")
    if ("delay5", "all", "ci90_low") not in by or ("delay5", "all", "mdd") not in by:
        probs.append("the all block prints no interval and MDD")
    if by.get(("delay5", "judged", "interval"), {}).get("note") != "too few separated windows for an interval":
        probs.append(f"the judged block prints {by.get(('delay5', 'judged', 'interval'))}")
    lo, hi = by[("delay5", "all", "ci90_low")]["value"], by[("delay5", "all", "ci90_high")]["value"]
    km = by[("delay5", "all", "kept_mean")]["value"]
    if not lo < km < hi:
        probs.append("the interval is not about the kept mean")
    seen["need"] = sorted(need)
    seen["n_w_all"] = by[("delay5", "all", "n_w")]["value"]
    hon = BR.honesty(need, reps=200)
    rows2, _, _ = BR.paired_rows(ahead, cards, ["p16"], names, ["verdict"], honesty=hon)
    stats = {(r["rules"], r["block"], r["stat"]) for r in rows2}
    if ("delay5", "all", "interval_label") not in stats or ("delay5", "all", "rare_coverage") not in stats:
        probs.append("the honesty label and the rare line are missing with the settings given")
    hr = BR.honesty_rows(hon, BR.HONESTY_SEED, 200)
    if len(hr) != 3 * 21 * len(need):
        probs.append(f"{len(hr)} honesty rows, not 3 x 21 a setting")
    again = BR.honesty(need, reps=200)
    if json.dumps({str(k): v for k, v in again.items()}, sort_keys=True) != \
            json.dumps({str(k): v for k, v in hon.items()}, sort_keys=True):
        probs.append("the honesty series are not reproducible from their seed")
    # a start on one side only
    lop = dict(ahead)
    k = ("p16", "delay5", "verdict", "all")
    lop[k] = {d: v for i, (d, v) in enumerate(ahead[k].items()) if i != 7}
    _, bad2, _ = BR.paired_rows(lop, cards, ["p16"], names, ["verdict"])
    seen["one_side_refused"] = len(bad2)
    if not bad2:
        probs.append("a start on one side only is not refused")
    return probs, seen


def check_mdd() -> tuple[list[str], dict]:
    """mdd_P filled in place: blank for P-14 and for the all block with their reasons; a finite value for the others
    on the judged block, reproducible from its seed."""
    probs, seen = [], {}
    outs = {"p14": synthetic_outs(1, n_days=1000), "p16": synthetic_outs(3, n_days=1000)}
    rows, ahead = [], {}
    for design, o in outs.items():
        srows = summary(design, o)
        rows += [{**r, "rules": "stage2"} for r in srows if r["section"] == "extra" and r["measure"] == "mdd_P"]
        recs = [x["rec"] for x in o]
        for block, which in BR.BLOCKS:
            ahead[(design, "stage2", "verdict", block)] = BR.p_months_ahead(recs, which)
    done = BR.fill_mdd_p(rows, ahead, ["p14", "p16"], ["stage2"], ["verdict"], reps=400)
    by = {(r["design"], r["block"]): r for r in rows}
    if not (np.isnan(by[("p14", "judged")]["value"]) and "R* itself" in by[("p14", "judged")]["note"]):
        probs.append(f"P-14's mdd_P is {by[('p14', 'judged')]}")
    if not (np.isnan(by[("p16", "all")]["value"]) and "judged block" in by[("p16", "all")]["note"]):
        probs.append(f"the all block's mdd_P is {by[('p16', 'all')]}")
    v = by[("p16", "judged")]["value"]
    if not (np.isfinite(v) and v > 0):
        probs.append(f"P-16's judged mdd_P is {v}")
    rows2 = [dict(r, value=float("nan")) for r in rows]
    BR.fill_mdd_p(rows2, ahead, ["p14", "p16"], ["stage2"], ["verdict"], reps=400)
    if {(r["design"], r["block"]): r["value"] for r in rows2}[("p16", "judged")] != v:
        probs.append("mdd_P is not reproducible from its seed")
    seen.update(value=v, n=by[("p16", "judged")]["n"], computed=done)
    return probs, seen


def check_variants() -> tuple[list[str], dict]:
    """C6: the nine variants into a temporary variants.jsonl through the vendored VariantCounter, distinct ids."""
    import tempfile

    from extended import breakeven as BE

    probs = []
    with tempfile.TemporaryDirectory() as td:
        vs = [(d, n, BR.variant_params(d, n, BE.RULES[n], 4, 4)) for d in ("p14", "p15", "p16")
              for n in ("stop_first", "delay5", "both")]
        ids = BR.record_variants(Path(td), "Q-132:test", 20261920, vs)
        lines = [json.loads(x) for x in (Path(td) / "variants.jsonl").read_text(encoding="utf-8").splitlines() if x]
    if len(lines) != 9 or len(set(ids)) != 9 or [x["variant_id"] for x in lines] != ids:
        probs.append(f"{len(lines)} lines, {len(set(ids))} distinct ids")
    if any(x["prereg_id"] != "Q-132:test" or x["exploratory"] is not True for x in lines):
        probs.append("a line without the id or the exploratory flag")
    return probs, {"lines": len(lines)}


def check_p15_substitution() -> tuple[list[str], dict]:
    """C1: `extended.breakeven.p15_cells` with `rc_screen.inputs` and `rc_reentry_screen.build` replaced by probes:
    the inputs load under Stage 2's `atlas_a3.walk_minutes`, the cells are built under the given walk, Stage 2's walk is
    restored after -- also after an error inside the build -- and with no walk given nothing is substituted. The
    vendored `rc_dev_test.build_cells` is the two lines reproduced."""
    import inspect

    import atlas_a3 as A
    import rc_dev_test as D
    import rc_reentry_screen as RS
    import rc_screen as S

    from extended import breakeven as BE

    probs, seen = [], {}
    src = inspect.getsource(D.build_cells)
    if not all(x in src for x in BE.P15_BUILD_CELLS_LINES):
        probs.append("rc_dev_test.build_cells is not the two lines p15_cells reproduces")
    stage2 = A.walk_minutes
    real_inputs, real_build = S.inputs, RS.build

    def mine(*a, **k):
        raise AssertionError("never called by a probe")

    try:
        S.inputs = lambda: (seen.__setitem__("inputs_walk", A.walk_minutes is stage2) or {"probe": "inputs"})
        RS.build = lambda I: (seen.__setitem__("build_walk", A.walk_minutes is mine) or
                              seen.__setitem__("build_inputs", I == {"probe": "inputs"}) or {"probe": "cells"})
        I, b = BE.p15_cells(mine)
        seen["after"] = A.walk_minutes is stage2
        seen["returned"] = (I, b) == ({"probe": "inputs"}, {"probe": "cells"})

        def boom(I):
            raise RuntimeError("inside the build")

        RS.build = boom
        try:
            BE.p15_cells(mine)
        except RuntimeError:
            pass
        seen["after_error"] = A.walk_minutes is stage2
        RS.build = lambda I: (seen.__setitem__("none_walk", A.walk_minutes is stage2) or {"probe": "cells"})
        BE.p15_cells(None)
    finally:
        S.inputs, RS.build, A.walk_minutes = real_inputs, real_build, stage2
    for k in ("inputs_walk", "build_walk", "build_inputs", "after", "returned", "after_error", "none_walk"):
        if seen.get(k) is not True:
            probs.append(f"the substitution's probe {k} is {seen.get(k)!r}")
    return probs, seen


def check_runner() -> tuple[list[str], dict]:
    """The runner's plumbing: `scripts/breakeven_fidelity_2.py`'s `main(--check --paths 4)` with every engine step
    replaced by a fake (the read's authorisation, U1's reference and comparison, the builders, the identities, the
    gates, the replay -- synthetic starts, a rule set's key choosing its draws), the honesty series and mdd_P at a few
    hundred replications, the temporary folder kept: exit 0; both files and their manifests verify; the start file holds
    every design, rule set and arm's starts and its sha256 is in the summary's manifest; sections paired, honesty and
    assumptions present; mdd_P filled on the judged block for P-15 and P-16 and blank for P-14; the assumptions in the
    manifest's parameters and notes; nine variants recorded; the log's first line the provenance line. No bar is read."""
    import contextlib
    import functools
    import importlib.util
    import io
    import tempfile

    import rc150_dev_test as P16
    import rc_dev_test as D

    from extended import breakeven as BE
    from extended import reader
    from extended import user_beside as B
    from extended.results import read_result

    spec = importlib.util.spec_from_file_location("q132_runner", ROOT / "scripts" / "breakeven_fidelity_2.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    probs: list[str] = []
    keep = Path(tempfile.mkdtemp(prefix="q132_runner_"))
    rnames = [n for n, _ in BE.RULE_SETS]
    state = {"rules": None}
    n_days = 820                                   # the judged block's common starts above MDD_MIN_STARTS
    proto = type("Proto", (), {"payout_path": "standard", "payout_frac": 1.0, "keep_balance": None})()

    def build(design):
        def f(rules, rd=None):
            name = next(n for n, r in BE.RULE_SETS if r is rules) if not isinstance(rules, str) else rules
            state["rules"] = name
            k = 10 * ("p14", "p15", "p16").index(design) + rnames.index(name)
            t = pd.DataFrame({"date": ["2024-01-02"] * 4, "entry_t": [1, 2, 3, 4], "side": [1, -1, 1, -1],
                              "o_1": ["t", "s", "b" if name != "stage2" else "t", "f"], "r_1": [1.0, -1.0, 0.0, 0.2],
                              "g_1": [4.0, -4.0, 0.0 if name != "stage2" else 4.0, 1.0]})
            jobs = {arm: {"blocks": list(range(n_days)), "dates": [], "key": (k, arm),
                          "args": {"path": {"payout_lag_days": 3, "payout_timing": "after_5pm",
                                            "purchase_budget": (20, 21),
                                            "risk_policy": type("T", (), {"id": "state_dp_test"})()},
                                   "draws": {"protocol": proto, "one_at_a_time": 5.0}}} for arm in ("verdict", "point")}
            return {"jobs": jobs, "trades": t, "days": [], "I": None, "b": None}
        return f

    def gate(b, n_paths, workers):
        df = pd.DataFrame([{"section": "gate", "enforcement_p": 0.0, "shift": s, **{c: 1.0 for c in BE.GATE_COLS}}
                           for s in ("point", "lower_bound")])
        return df, []

    outs_cache: dict = {}

    def run_starts(design, arm, resp, job, chosen, workers, **kw):
        k = job["key"]
        if k not in outs_cache:
            outs_cache[k] = synthetic_outs(int(k[0]) * 2 + (arm == "point"), n_days=n_days)
        return [outs_cache[k][i] for i in chosen]

    patches = [
        (reader, "authorise_engine_read", lambda *a, **k: None),
        (m.I.SI, "engine_files", lambda *a, **k: []),
        (m.I, "u1_reference", lambda rd, designs: {"fake": True}),
        (m.I, "u1_compare_outs", lambda *a, **k: []),
        (BE, "registered_gate", lambda design: {s: {c: 1.0 for c in BE.GATE_COLS} for s in ("point", "lower_bound")}),
        (BE, "a3_inputs", lambda: {"cached": None}),
        (BE, "a3_frame", lambda rules, X: rules),
        (BE, "frame_problems", lambda a, b: []),
        (BE, "p14_build", lambda frame, rd: build("p14")(frame)),
        (BE, "p15_build", build("p15")), (BE, "p16_build", build("p16")),
        (BE, "p15_trade_problems", lambda b, rd: []),
        (BE, "p14_gate", gate), (BE, "p15_gate", gate), (BE, "p16_gate", gate),
        (D, "trades_hash", lambda t: P16.SPEC.trades_sha256),
        (B, "run_starts", run_starts),
        (m.BR, "honesty", functools.partial(m.BR.honesty, reps=100)),
        (m.BR, "fill_mdd_p", functools.partial(m.BR.fill_mdd_p, reps=200)),
        (m.tempfile, "TemporaryDirectory", lambda prefix="": contextlib.nullcontext(str(keep))),
    ]
    saved = [(o, n, getattr(o, n)) for o, n, _ in patches]
    buf = io.StringIO()
    try:
        for o, n, v in patches:
            setattr(o, n, v)
        with contextlib.redirect_stdout(buf):
            rc = m.main(["--check", "--paths", "4"])
    finally:
        for o, n, v in saved:
            setattr(o, n, v)
    log = buf.getvalue()
    seen: dict = {"rc": rc, "log_head": log.splitlines()[0] if log else "", "kept": str(keep)}
    if rc != 0:
        return [f"main returned {rc}: {log[-2500:]}"], seen
    if not seen["log_head"].startswith("provenance: commit "):
        probs.append(f"the log's first line is {seen['log_head']!r}")
    summ = read_result(keep / "breakeven_fidelity_2.csv")
    st = read_result(keep / "breakeven_fidelity_2_starts.csv")
    man = json.loads((keep / "breakeven_fidelity_2.csv.manifest.json").read_text(encoding="utf-8"))
    import hashlib

    sha = hashlib.sha256((keep / "breakeven_fidelity_2_starts.csv").read_bytes()).hexdigest()
    if man["parameters"]["start_file"]["sha256"] != sha:
        probs.append("the summary's manifest does not name the start file's sha256")
    combos = st.groupby(["design", "rules", "arm"]).size()
    if len(combos) != 3 * 4 * 2 or set(combos) != {n_days}:
        probs.append(f"the start file holds {len(combos)} (design, rules, arm) groups of sizes {sorted(set(combos))}")
    for sec in ("identity", "trades", "gate", "scorecard", "extra", "path", "paired", "honesty", "assumptions"):
        if not (summ["section"] == sec).any():
            probs.append(f"no section {sec}")
    if (summ.loc[summ["section"] == "identity", "value"] != 1.0).any():
        probs.append("an identity row is not 1")
    mdd = summ[(summ["section"] == "extra") & (summ["measure"] == "mdd_P")]
    j = mdd[mdd["block"] == "judged"]
    other = j[j["design"] != "p14"]
    ok_other = (np.isfinite(other["value"]) | other["note"].astype(str).str.startswith("infinite:")).all()
    if not (ok_other and np.isfinite(other["value"]).any() and j[j["design"] == "p14"]["value"].isna().all()
            and len(other) == 2 * 4 * 2):
        probs.append("mdd_P is not filled for p15 and p16 on the judged block, blank for p14: "
                     + str(j[["design", "rules", "arm", "value", "n", "note"]].to_dict("records")[:4]))
    if not mdd[mdd["block"] == "all"]["value"].isna().all():
        probs.append("mdd_P on the all block is not blank")
    pr = summ[summ["section"] == "paired"]
    if set(pr["rules"]) != {"stop_first", "delay5", "both"} or set(pr["design"]) != {"p14", "p15", "p16"}:
        probs.append("the paired rows do not cover every correction and design")
    if not (pr["stat"] == "ci90_low").any():
        probs.append("no paired interval printed")
    if "assumptions" not in man["parameters"] or "Assumed:" not in man.get("notes", {}).get("assumptions", ""):
        probs.append("the assumptions are not in the manifest's parameters and notes")
    if set(man["parameters"].get("licence_guard", {})) != {"results/breakeven_fidelity_2_starts.csv",
                                                             "results/breakeven_fidelity_2.csv"}:
        probs.append("the licence guard's scan is not recorded for both tables")
    if not any(x.startswith("licence guard (results/breakeven_fidelity_2_starts.csv)") for x in log.splitlines()):
        probs.append("the licence guard's scan is not in the log")
    if man.get("variant_count") != 9:
        probs.append(f"variant_count {man.get('variant_count')}")
    lines = (keep / "variants.jsonl").read_text(encoding="utf-8").splitlines()
    if len(lines) != 9:
        probs.append(f"{len(lines)} variant lines")
    seen.update(summary_rows=int(len(summ)), start_rows=int(len(st)), paired_rows=int(len(pr)))
    import shutil

    if not probs:
        shutil.rmtree(keep, ignore_errors=True)
    return probs, seen


CHECKS = {"frame": check_frame, "paired": check_paired, "mdd": check_mdd, "variants": check_variants,
          "p15_substitution": check_p15_substitution, "runner": check_runner}

if __name__ == "__main__":
    p, s = CHECKS[sys.argv[1]]()
    print(json.dumps({"problems": p, "seen": s}, default=str))
