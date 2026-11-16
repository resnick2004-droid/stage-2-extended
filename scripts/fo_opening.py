"""F-03 (family O, `prereg/F-03_opening_timing.md`, pinned by E-095): the two family runs (section 19.2). HEAVY: one at a
time on the machine, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched.

    python scripts/fo_opening.py --run 1 --workers 2                      # stages A and B, the choice block only
    python scripts/fo_opening.py --run 1 --check-guards                   # the refusing guards only; reads nothing
    python scripts/fo_opening.py --run 2 --run1 results/fo_opening.csv --check-read   # run 2's four reads, pre-checked

**Before anything is read** (`extended.opening_run.pre_run`, refusing): the pass-line blobs, the level
`family_level(12)`, the judged session list (657, E-094's sha256), the pinned text and its reads line, the waited
identities by E-104's positional token (Q-89, Q-93, Q-101, Q-80 and A0's, each
with its covered files), a clean run. Then A1 item 2 (E-011's walker identity,
its synthetic mode, at this commit).

**Run 1** reads the choice block only (no tag): A1's day table, the bars (P-16's walked sessions), and P-16's
registered files (its screen's admitted marks, its gate file's per-R shift and day capacity, U1's start rows, U5's
value map). It builds the population and labels (`extended.opening_population.build_span`), the states and u3's
walk-forward (`extended.opening_states`), P-16's U1 job on the choice block at P-16's registered shift, and replays it
through Q-17's adapter with the family's class (`extended.opening_wait`) and Q-94's recorder: A1 (items 4 to 7), stage
A (A2 to A11) and stage B (`run1`). It writes `results/fo_opening.csv`, sections `identity` .. `choice`, u3's frozen
forecast (its canonical JSON and sha256 in the manifest) and the pick. **A10's consequence** (a lax `cons` on c in a
surviving cell's class) is not built -- its inner draws' seeds are not declared and its declared cost is far below its
real one -- so if A10 flags it, run 1 stops before stage B (EXIT 3) for the lead's decision, writing nothing.

**Run 2** (stage C) is built through its reads' pre-check (`--check-read`: the four purposes in stage C's order through
`extended.reader.authorise`, nothing read) and its pinned inputs (T-9: run 1's sha256 and u3's forecast hash in one
row naming F-03); its statistics are `extended.opening_stats`'; **its end-to-end composition is not built**: run 2
refuses (EXIT 3) after the pinned inputs check.

The last line printed is `EXIT <code>`: 0 written, 2 refused by a guard, 3 an identity, a kill or an unbuilt branch
stopped the run.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

SCRIPT = "scripts/fo_opening.py"
STAGE_AB_FIRST = "2021-01-04"
ARM = "verdict"
DECIDING_CLASS = {"s1": "window", "s2": "window", "u3": "block5"}      # 6.6's one deciding class a cell
A3_CUTS = 200
#: the record columns run 1 keeps (every check runs on the full record where the start ran)
RECORD_COLUMNS = ("place", "account", "day", "rel_day", "account_session", "historical_day", "trade_index", "date",
                  "offer", "entry_t", "rr", "source", "realised_risk", "intended_capped_risk", "kind")


def log(msg: str) -> None:
    print(msg, flush=True)


# ------------------------------------------------------------------------------------------------ the context


@dataclass
class Sizes:
    """The declared sizes; a smoke (`Ctx.smoke`) shrinks them and writes nothing."""
    starts: int | None = None
    k0: int = 200_000
    a10: int = 2000
    stage_b: int = 2000
    a3_cuts: int = A3_CUTS


@dataclass
class Ctx:
    """Run 1's reads and registered inputs. The real context reads through `extended/reader.py` (the choice block, no
    tag) and the vendored engine; the synthetic test's overrides the reads."""
    results_dir: Path | None = None
    sizes: Sizes = field(default_factory=Sizes)
    smoke: bool = False

    def a1_days(self, start: str, end: str):
        from extended import reader

        d = reader.read_walks("A1", "days", start, end, columns=["date", "day_kind"],
                              what=f"F-03 run 1: A1's day table {start} to {end}")
        return d.assign(date=d["date"].astype(str), day_kind=d["day_kind"].astype(str))

    def span(self, start: str, end: str, all_dates: list[str]):
        from extended import opening_population as OP

        return OP.build_span(start, end, all_dates, log=log)

    def grid(self, start: str, end: str, walked: set[str]):
        from extended import features as F
        from extended import reader

        bars = reader.read_bars(start, end, what=f"F-03 states: the bars {start} to {end}")
        return F.grid(bars[bars["day"].astype(str).isin(walked)].reset_index(drop=True))

    def p16(self) -> dict[str, Any]:
        return p16_inputs()

    def jobs(self, trades, days: list[str], P: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return u1_job(trades, days, P)

    def restricted_replay_problems(self, job: dict, starts: list[int], workers: int) -> list[str]:
        return a1_restricted_replay_problems(job, starts, workers)

    def mean_dv(self) -> float:
        return mean_dv_c()

    def write(self, df, params: dict[str, Any]) -> str | None:
        from extended import opening_run as R
        from extended import opening_stats as ST
        from extended.results import write_result

        if self.smoke:
            return None
        csv, _ = write_result(df, R.RESULT, script=SCRIPT, seed=ST.SEED_STAGE_B, parameters=params, exploratory=True,
                              prereg_id=R.FAMILY, variant_count=4, results_dir=self.results_dir,
                              description="F-03 run 1 (stages A and B, the choice block): identities, states, supply, "
                                          "openings, resolution, waits, power, level controls, the choice; "
                                          "EXPLORATORY until a carried design is registered.")
        return str(csv)


# ------------------------------------------------------------------------------------------------ the vendored inputs


def p16_inputs() -> dict[str, Any]:
    """P-16's configuration and registered constants (`extended.opening_population.p16_inputs`, A0's item 1 holds
    them)."""
    from extended import opening_population as OP

    return OP.p16_inputs()


def u1_job(trades, days: list[str], P: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """P-16's U1 job on a span (both arms), as `user_journey.build_p16` makes it -- `rc_dev_test.rc_campaign` on the
    span's trades and sessions at P-16's registered shift and capacity, `user_journey._single_jobs`."""
    import a3_brk30_cb20 as Cb
    import rc150_dev_test as P16
    import rc_dev_test as D
    import user_journey as UJ

    I = {"L": {"fcfg": P["fcfg"], "tv": P["tv"], "cfg": P["cfg"]}, "plan": P["plan"]}
    camp = D.rc_campaign(I, trades, list(days), P["e_by"], P["lb_by"], int(P["cap"]), P16.SPEC)
    return UJ._single_jobs(camp, P["plan"], Cb.BUDGET)


def a1_restricted_replay_problems(job: dict, starts: list[int], workers: int) -> list[str]:
    """A1 item 6: with each start's history ending at 2023-12-29, the replay's start rows equal U1's
    (`user_journey.csv`) on every start whose horizon ends inside the choice block."""
    sys.path.insert(0, str(ROOT / "identity"))
    import stage2_identity as SI
    import user_beside_identity as I
    import user_journey as UJ

    from propedge import RESULTS_DIR
    from propedge.research import user_journey as U

    from extended import user_beside as B

    ref = I.u1_reference(Path(RESULTS_DIR), ["p16"])
    c = {x["config"]: x for x in UJ.CONFIG_DEFS}["p16"]
    n = len(job["blocks"])
    inside = [s for s in starts if s + U.HORIZON <= n]
    outs = B.run_starts("p16", ARM, B.BY_NAME["off"], job, inside, int(workers))
    mine = [{**r, "reading": U.READING} for r in UJ.start_rows(c, ARM, outs)]
    st = ref["start"]
    want = {str(job["dates"][s]) for s in inside}
    theirs = st[(st["config"] == "p16") & (st["arm"] == ARM) & st["start_date"].astype(str).isin(want)]
    return [f"A1 item 6: {p}" for p in SI.u1_compare(mine, theirs.to_dict("records"), ref["columns"],
                                                     f"p16 {ARM} (choice block)", all_starts=False)]


def mean_dv_c() -> float:
    """`u_value_map.csv`, section `place_values`, base `p16`, place `c_funded_opening`, measure `mean_dv` (7.4)."""
    import pandas as pd

    from propedge import RESULTS_DIR

    from extended.results import verify_result

    p = Path(RESULTS_DIR) / "u_value_map.csv"
    ok, msg = verify_result(p)
    if not ok:
        raise SystemExit(f"REFUSED (F-03): u_value_map.csv: {msg}")
    d = pd.read_csv(p, float_precision="round_trip", low_memory=False)
    d = d[(d["section"] == "place_values") & (d["base"].astype(str) == "p16")
          & (d["place"].astype(str) == "c_funded_opening")]
    if "mean_dv" not in d.columns or len(d) != 1:
        raise SystemExit(f"REFUSED (F-03): u_value_map.csv holds {len(d)} p16 place (c) rows with mean_dv")
    return float(d["mean_dv"].iloc[0])


# ------------------------------------------------------------------------------------------------ helpers


def offer_ids_of(trades, days, blocks):
    from extended import opening_population as OP
    from extended import place_records as PR

    t = trades.copy()
    t["fo_offer"] = [OP.offer_id(d, int(s)) for d, s in zip(t["date"].astype(str), t["decision_slot_minutes"])]
    return PR.block_offer_ids(t, days, blocks, "fo_offer")


def flags_by_block(ids: list, flag_of: dict) -> list:
    import numpy as np

    return [np.array([bool(flag_of.get(x, False)) for x in blk], dtype=bool) for blk in ids]


def grid_flags(L, flags) -> dict[str, bool]:
    import numpy as np

    from extended import opening_population as OP

    return {OP.offer_id(L.sessions[i], L.marks[k]): True for i, k in zip(*np.nonzero(flags))}


def replay(design: str, job: dict, starts: list[int], workers: int, cls=None, ids=None):
    from extended import opening_wait as OW
    from extended import user_beside as B

    rec = OW.FamilyRecorder(offer_ids=ids, columns=RECORD_COLUMNS)
    kw: dict[str, Any] = {"recorder": rec}
    if cls is not None:
        kw["funded_account_cls"] = cls
    outs = B.run_starts(design, ARM, B.BY_NAME["off"], job, starts, int(workers), **kw)
    return outs, rec


def run_lengths(on) -> dict[str, float]:
    """A session-level indicator's in-state runs (6.6 at run time): their count, mean and longest."""
    import numpy as np

    x = np.asarray(on, bool).astype(np.int8)
    if not x.any():
        return {"runs": 0, "mean_run": 0.0, "longest_run": 0}
    edges = np.diff(np.r_[0, x, 0])
    lens = np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)
    return {"runs": int(len(lens)), "mean_run": float(lens.mean()), "longest_run": int(lens.max())}


def opening_counts(ops, design: str, cell: str) -> list[dict[str, Any]]:
    """A2's counts (counts only): by mark, hour, day kind, the 08:30-09:00 share, the report-day share, the report-day
    07:35 entries, the sessions from activation, the in-state share, the wait and the fallback share."""
    from extended import features as F

    n = len(ops)
    rows = [{"cell": cell, "design": design, "group": "all", "key": "openings", "count": n}]
    if not n:
        return rows
    hour = (ops["slot"].astype(int) + 1020) % 1440 // 60
    win = ops["slot"].astype(int).between(F.slot(8, 30), F.slot(9, 0))
    rep = ops["day_kind"].astype(str) == "b"
    at735 = rep & (ops["slot"].astype(int) == F.slot(7, 35))
    for name, s in (("mark", ops["slot"].astype(int).map(F.slot_label)), ("hour", hour),
                    ("day_kind", ops["day_kind"].astype(str)), ("wait", ops["opening_session"].astype(int))):
        for k, v in s.value_counts().sort_index().items():
            rows.append({"cell": cell, "design": design, "group": name, "key": str(k), "count": int(v)})
    rows += [{"cell": cell, "design": design, "group": "share", "key": k, "count": int(v.sum()), "share": float(v.mean())}
             for k, v in (("window_0830_0900", win), ("report_day", rep), ("report_day_0735", at735),
                          ("fallback", ops["fallback"]))]
    return rows


def special_sessions(g) -> list[int]:
    """The roll sessions (the contract changes) and the first sessions after a DST change (17:00 CT's UTC offset
    differs from the previous session's) -- A3's cuts include them."""
    from datetime import datetime, timedelta

    from extended import features as F

    out = [i for i in range(1, len(g.days)) if g.contract[i] != g.contract[i - 1]]

    def off(d):
        e = d - timedelta(days=1)
        return datetime(e.year, e.month, e.day, 17, 0, tzinfo=F.CHICAGO).utcoffset()

    out += [i for i in range(1, len(g.days)) if off(g.days[i]) != off(g.days[i - 1])]
    return sorted(set(out))


def a3_cuts(g, st, n: int) -> list[tuple[int, int]]:
    """A3's cuts (9, A3; T-2's on the real frame): the first marks after 17:00, 17:30 and the `asia` band's first marks
    18:00 and 18:05, on sessions drawn by `[20261981, 10**6]` among those where the states are defined, every roll and
    DST session among them first; `n` cuts (200 declared)."""
    import numpy as np

    from extended import opening_states as OS
    from extended import opening_stats as ST

    first = [0, 5, OS.NIGHT_FIRST_MARK, 60, 65]
    defined = [i for i in range(len(st.days)) if np.isfinite(st.share("s1")[i]).any()]
    special = [i for i in special_sessions(g) if i in set(defined)]
    rng = np.random.default_rng([ST.SEED_SHIFT, 10 ** 6])
    pool = [i for i in defined if i not in set(special)]
    k = max(0, n // len(first) + 1 - len(special))
    days = special + [int(x) for x in rng.choice(pool, size=min(len(pool), k), replace=False)]
    return [(int(d), int(m)) for d in days for m in first][:n]


# ------------------------------------------------------------------------------------------------ run 1


def run1(ctx: Ctx, pre, workers: int) -> tuple[int, Any, dict[str, Any]]:
    """Stages A and B on the choice block (the module docstring): (the exit code, the result frame, its parameters)."""
    import numpy as np
    import pandas as pd

    from extended import opening_population as OP
    from extended import opening_run as R
    from extended import opening_states as OS
    from extended import opening_stats as ST
    from extended import opening_wait as OW
    from extended import reader

    t_all = time.time()
    out: list[dict[str, Any]] = []
    z = ctx.sizes
    nj = len(pre.judged_sessions)
    P = ctx.p16()
    A1 = ctx.a1_days(str(reader.CHOICE_START), str(reader.CHOICE_END))
    all_dates = sorted(set(A1["date"]) | set(pre.judged_sessions))
    log(f"run 1: {len(A1)} choice-block days; the coin's grid {len(all_dates)} sessions")
    span = ctx.span(str(reader.CHOICE_START), str(reader.CHOICE_END), all_dates)
    walked = set(span.days.loc[span.days["day_kind"].isin(OP.WALKED_KINDS), "date"])
    g = ctx.grid(str(reader.CHOICE_START), str(reader.CHOICE_END), walked)
    st = OS.compute(g)
    fc = st.forecast
    pop = span.population.merge(st.frame(), on=["date", "slot"], how="left", validate="many_to_one")
    for c in OS.BUILT:
        pop[f"in_{c}"] = pop[f"in_{c}"].astype("boolean").fillna(False).astype(bool) & pop["population"].astype(bool)
    states_sha = OS.states_sha256(pop)
    log(f"states: {len(pop)} offers, u3's final fit {fc.coefficients_sha256[:16]}, states {states_sha[:16]}")
    # A3: no look-ahead on these bars (refusing)
    cuts = a3_cuts(g, st, z.a3_cuts)
    a3 = OS.invariance_problems(g, st, cuts, ST.SEED_SHIFT)
    out += R.rows("identity", [{"check": "A3: the states and y_hat read no bar at or after the alert", "cuts": len(cuts),
                                "holds": not a3, "problems": a3[:3]}])
    if a3:
        log("REFUSED (F-03): A3 fails -- " + "; ".join(a3[:3]))
        return 3, None, {}

    # ---- the span of stages A and B: its calendar, strata and centred values
    kinds = dict(zip(A1["date"], A1["day_kind"]))
    cal = sorted(d for d in A1["date"] if d >= STAGE_AB_FIRST)
    sp = pop[pop["date"] >= STAGE_AB_FIRST].reset_index(drop=True)
    L = ST.layout(sp, cal, kinds=kinds, values=("c", "c_close", "rl", "rs"), flags=[f"in_{c}" for c in OS.BUILT])
    y = ST.centred(L, "c", L.population)
    y_close = ST.centred(L, "c_close", L.population)
    y_all = ST.centred(L, "c")                                     # with the labels, each its own stratum (C2's)
    yv = {OP.offer_id(L.sessions[i], L.marks[k]): float(y_all[i, k]) for i, k in zip(*np.nonzero(L.exists))}
    offers = sp.assign(offer=[OP.offer_id(d, s) for d, s in zip(sp["date"], sp["slot"])]).set_index("offer")
    offers = offers[["slot", "day_kind", "year", "population", *[f"in_{c}" for c in OS.BUILT]]]
    labels = pop[pop["date"] >= STAGE_AB_FIRST]
    offers = pd.concat([offers, labels[~labels["population"]].assign(
        offer=[OP.offer_id(d, s) for d, s in zip(labels.loc[~labels["population"], "date"],
                                                 labels.loc[~labels["population"], "slot"])]).set_index("offer")[
        offers.columns]]).loc[lambda d: ~d.index.duplicated()]

    # ---- the U1 job on the choice block; A1's replay identities (items 4-7)
    days_all = sorted(A1["date"])
    jobs = ctx.jobs(span.trades, days_all, P)
    job = jobs[ARM]
    ids = offer_ids_of(span.trades, days_all, job["blocks"])
    starts = [i for i, d in enumerate(job["dates"]) if str(d) >= STAGE_AB_FIRST]
    if z.starts is not None:
        starts = starts[:: max(1, len(starts) // int(z.starts))][: int(z.starts)]
    probs: list[str] = []
    never = OW.waiting_class(OW.WaitSpec.for_blocks("never", job["blocks"],
                                                    [np.zeros(len(b), bool) for b in job["blocks"]]))
    _, rn = replay("fo_never", job, starts, workers, never, ids)
    on = OW.openings(rn, "fo_never", ARM, "off")
    if len(on) and not (on["opening_session"] >= OW.W_DECLARED).all():
        probs.append("A1 item 4: with the state never on an opening fell inside the wait")
    tw0, _ = ST.clustered_twin(L, L.flags["in_s1"], OS.CELL_INDEX["s1"], ST.BLOCK_CHOICE, 0)
    placebo = grid_flags(L, tw0)
    _, rp = replay("fo_placebo", job, starts, workers, OW.waiting_class(
        OW.WaitSpec.for_blocks("placebo", job["blocks"], flags_by_block(ids, placebo))), ids)
    probs += [f"A1 item 5: {p}" for p in OW.wait_problems(OW.openings(rp, "fo_placebo", ARM, "off"),
                                                         rp.declined("fo_placebo", ARM, "off"), placebo)]
    w0 = OW.waiting_class(OW.WaitSpec.for_blocks("w0", job["blocks"], flags_by_block(ids, placebo), W=0))
    base_outs, base_rec = replay("p16", job, starts[:4], workers, None, ids)
    w0_outs, w0_rec = replay("p16_w0", job, starts[:4], workers, w0, ids)
    sys.path.insert(0, str(ROOT / "identity"))
    import user_beside_identity as I

    probs += [f"A1 item 7: {p}" for p in I.class_outs_problems(base_outs, w0_outs, w0, "the wait off, recorded")]
    probs += [f"A1 records: {p}" for p in (rn.problems() + rp.problems() + w0_rec.problems())[:5]]
    probs += ctx.restricted_replay_problems(job, starts, workers)
    out += R.rows("identity", [{"check": "A1 items 4-7 (never on, the placebo set, the wait off recorded, the "
                                         "restricted replay)", "starts": len(starts), "holds": not probs,
                                "problems": probs[:6]}])
    if probs:
        log("REFUSED (F-03): A1 fails -- " + "; ".join(probs[:6]))
        return 3, None, {}
    _, base_rec = replay("p16", job, starts, workers, None, ids)
    base_ops = OW.openings(base_rec, "p16", ARM, "off", offers)
    out += R.rows("openings", opening_counts(base_ops, "p16", "-"))
    out += R.rows("openings", [{"cell": c, "design": "p16", "group": "in_state", "key": c,
                                "count": int(base_ops[f"in_{c}"].sum()), "share": float(base_ops[f"in_{c}"].mean())}
                               for c in OS.BUILT if len(base_ops)])

    # ---- stage A, cell by cell
    mdv = ctx.mean_dv()
    killed: dict[str, str] = {}
    keep: dict[str, dict[str, Any]] = {}
    pos = {d: i for i, d in enumerate(cal)}
    for c in OS.BUILT:
        sel = L.flags[f"in_{c}"]
        out += R.rows("persistence", [{"cell": c, **run_lengths((sel & L.population).any(axis=1))}])
        by_year = ST.k1_sessions_by_year(L, sel)
        k2 = ST.k2_shares(sp["kl"].to_numpy(), sp["ks"].to_numpy(), sp[f"in_{c}"].to_numpy(bool),
                          sp["year"].to_numpy())
        out += R.rows("supply", [{"cell": c, "year": y_, "sessions_in_state": n,
                                  "in_state_offers": int((sel & L.population)[L.year == y_].sum())}
                                 for y_, n in by_year.items()])
        out += R.rows("resolution", [{"cell": c, "scope": k, "unresolved_3r": v} for k, v in k2.items()])
        if ST.k1_killed(by_year):
            killed[c] = "K1"
            continue
        if ST.k2_killed(k2):
            killed[c] = "K2"
            continue
        spec = OW.WaitSpec.for_blocks(c, job["blocks"], flags_by_block(ids, grid_flags(L, sel)))
        _, rec = replay(f"fo_{c}", job, starts, workers, OW.waiting_class(spec), ids)
        twins = []
        for d in ST.TWIN_DRAWS:
            tw, _ = ST.clustered_twin(L, sel, OS.CELL_INDEX[c], ST.BLOCK_CHOICE, d)
            tspec = OW.WaitSpec.for_blocks(f"{c}_twin{d}", job["blocks"], flags_by_block(ids, grid_flags(L, tw)))
            twins.append(replay(f"fo_{c}_twin{d}", job, starts, workers, OW.waiting_class(tspec), ids)[1])
        ops = OW.openings(rec, f"fo_{c}", ARM, "off", offers)
        tops = [OW.openings(r_, f"fo_{c}_twin{d}", ARM, "off", offers) for d, r_ in enumerate(twins)]
        out += R.rows("openings", opening_counts(ops, "design", c)
                      + [x for d, o_ in enumerate(tops) for x in opening_counts(o_, f"twin{d}", c)])
        cen = OW.censored(rec, f"fo_{c}", ARM, "off")
        fb = float(ops["fallback"].mean()) if len(ops) else float("nan")
        real = ops["realised_risk"] / ops["intended_capped_risk"] if len(ops) and "realised_risk" in ops else []
        out += R.rows("wait", [{"cell": c, "design": "design", "openings": len(ops), "fallback_share": fb,
                                "censored": len(cen), "censored_inside_wait": int(cen["inside_wait"].sum()),
                                "declined": len(rec.declined(f"fo_{c}", ARM, "off")),
                                "realised_to_intended_capped_risk": float(np.mean(real)) if len(real) else float("nan")}]
                      + [{"cell": c, "design": f"twin{d}", "openings": len(o_),
                          "fallback_share": float(o_["fallback"].mean()) if len(o_) else float("nan")}
                         for d, o_ in enumerate(tops)])
        if ST.k5_killed(fb):
            killed[c] = "K5"
            continue
        n1, n2 = (sel & L.population).sum(axis=1), L.population.sum(axis=1)
        v1 = ST.k0_family(n1, n2, "nested", nj, R.LEVEL, OS.CELL_INDEX[c], ST.K0_FORMS["c1_choice"], z.k0)
        u1c = np.bincount([pos[d] for d in ops["date"] if d in pos], minlength=len(cal))
        u2c = sum(np.bincount([pos[d] for d in o_["date"] if d in pos], minlength=len(cal)) for o_ in tops)
        v2 = ST.k0_family(u1c, u2c, "pair", nj, R.LEVEL, OS.CELL_INDEX[c], ST.K0_FORMS["c2_choice"], z.k0)
        out += R.rows("level_control", [{"cell": c, "check": "K0", "form": f, **v.as_dict()}
                                        for f, v in (("c1", v1), ("c2", v2))])
        if v1.lax or v2.lax:
            killed[c] = "K0"
            continue
        u_c = ST.openings_a_start_year(len(ops), [min(252, len(job["blocks"]) - s) for s in starts])
        mdl = ST.a9_mdl(L, y, sel, nj, R.LEVEL)
        out += R.rows("power", [{"cell": c, "mdl": mdl["mdl"], "windows": mdl["windows"], "u_c": u_c,
                                 "lambda_bar": ST.lambda_bar(mdv, u_c)}])
        keep[c] = {"ops": ops, "tops": tops, "mdl": mdl["mdl"], "lambda_bar": ST.lambda_bar(mdv, u_c), "u_d": u_c}
    if "u3" in keep:
        rows_ = np.array([d.isoformat() >= STAGE_AB_FIRST for d in st.days])
        bands = {b: [k for k, m in enumerate(st.marks) if lo <= m <= hi] for b, (lo, hi, _) in OS.BANDS.items()}
        sk = ST.a4_skill(st.y, st.y_hat, bands, rows_)
        out += R.rows("level_control", [{"cell": "u3", "check": "A4", "band": b, **v} for b, v in sk.items()])
        if not all(v["skill"] for v in sk.values()):
            killed["u3"] = "A4"
            keep.pop("u3")
    a10 = ST.a10(L, y, selections=z.a10)
    out += R.rows("level_control", [{"check": "A10", **r} for r in a10.to_dict("records")])
    lax = [c for c in keep if a10[(a10["class"] == DECIDING_CLASS[c]) & a10["lax"]].shape[0]]
    if lax:
        log(f"STOPPED (F-03): A10 records `cons` lax on c in the class of {lax}; A10's consequence (the pseudo-judged "
            "split) is not built -- the lead decides (nothing written)")
        return 3, R.frame(out, R.RUN1_SECTIONS), {}
    surviving = list(keep)
    screen = bool(surviving) and all(keep[c]["mdl"] > ST.MDL_FACTOR * keep[c]["lambda_bar"] for c in surviving)
    out += R.rows("power", [{"check": "screen", "declared_screen": screen, "surviving": surviving}])

    # ---- stage B (10)
    sels = {c: L.flags[f"in_{c}"] for c in surviving}
    b = ST.stage_b_bootstrap(L, "c", sels, draws=z.stage_b) if surviving else {"estimate": {}, "se": {},
                                                                                  "q_B": float("nan")}
    eligible, vlow = {}, {}
    for c in surviving:
        h = ST.halves(L, sels[c])
        close = ST.lift(L, y_close, sels[c])
        k2 = ST.k2_shares(sp["kl"].to_numpy(), sp["ks"].to_numpy(), sp[f"in_{c}"].to_numpy(bool), sp["year"].to_numpy())
        eligible[c] = bool(ST.k2_worst_year(k2) <= ST.K2_PICK_MAX + 1e-12 and h["long"] > 0 and h["short"] > 0
                           and close > 0)
        o1 = keep[c]["ops"]
        o2 = pd.concat(keep[c]["tops"], ignore_index=True)
        o1, o2 = o1[o1["offer"].isin(yv) & o1["date"].isin(pos)], o2[o2["offer"].isin(yv) & o2["date"].isin(pos)]
        D, se_d = ST.d_bootstrap_se(o1["offer"].map(yv).to_numpy(), o1["date"].map(pos).to_numpy(),
                                    o2["offer"].map(yv).to_numpy(), o2["date"].map(pos).to_numpy(), L.n,
                                    draws=z.stage_b)
        vlow[c] = ST.v_line(keep[c]["u_d"], mdv, D - b["q_B"] * se_d)
        parts = {f"V_B_{k}": ST.v_line(keep[c]["u_d"], mdv, float(o1.loc[o1[k], "offer"].map(yv).mean() -
                                                                    o2.loc[o2[k], "offer"].map(yv).mean()))
                 for k in ("in_wait", "fallback") if o1[k].any() and o2[k].any()}
        out += R.rows("choice", [{"kind": "cell", "cell": c, "L": b["estimate"][c], "SE": b["se"][c],
                                  "L_long": h["long"], "L_short": h["short"], "L_close": close,
                                  "by_year": {int(y_): ST.lift(L, np.where(L.year[:, None] == y_, y, np.nan), sels[c])
                                              for y_ in sorted(set(L.year))},
                                  "eligible": eligible[c], "D_B": D, "SE_D_B": se_d, "V_B_lower": vlow[c], **parts}])
    if base_ops is not None and len(base_ops):
        yb = base_ops["offer"].map(yv)
        out += R.rows("choice", [{"kind": "V_B_p16", "value": ST.v_line(
            ST.openings_a_start_year(len(base_ops), [min(252, len(job["blocks"]) - s) for s in starts]), mdv,
            float(yb.mean()))}])
    pick = (ST.stage_b_pick(surviving, b["estimate"], b["se"], b["q_B"], eligible, vlow) if surviving
            else {"killed": True, "pick": None})
    out += R.rows("choice", [{"kind": "q_B", "value": b["q_B"]},
                             {"kind": "pick", "cell": pick["pick"] or "none", "killed": pick["killed"]}]
                  + [{"kind": "killed", "cell": c, "reason": r} for c, r in killed.items()]
                  + [{"kind": "dropped", "cell": c, "reason": "dropped at the pin by 6.6's rule (E-095)"}
                     for c in OS.DROPPED])
    out += R.rows("states", [{"kind": "forecast", "band": band, "terms": ["intercept", *OS.BANDS[band][2]],
                              "beta": [repr(x) for x in fc.final[band]]} for band in sorted(fc.final)]
                  + [{"kind": "share_in_state", "cell": c, "year": int(y_),
                      "share": float((L.flags[f"in_{c}"] & L.population)[L.year == y_].sum()
                                     / max(1, L.population[L.year == y_].sum()))}
                     for c in OS.BUILT for y_ in sorted(set(L.year))])
    df = R.frame(out, R.RUN1_SECTIONS)
    params = {**pre.parameters(), "run": 1, "forecast_json": OS.canonical_json(fc.final),
              "forecast_sha256": fc.coefficients_sha256, "states_sha256": states_sha,
              "population_sha256": OP.frame_sha256(pop), "coin_digest": span.coin_digest, "starts": len(starts),
              "calendars": {"identity": "the U1 replay of choice-block starts", "openings": "the U1 replay in "
                            "history's order", "wait": "the U1 replay in history's order", "supply": "offer level",
                            "resolution": "offer level", "choice": "offer level (L) and the U1 replay (V_B)"},
              "seeds": list(ST.SEEDS), "sizes": vars(z), "pick": pick["pick"], "killed": killed, "screen": screen,
              "workers": int(workers), "seconds": round(time.time() - t_all, 1)}
    return 0, df, params


# ------------------------------------------------------------------------------------------------ run 2


def run2(a: argparse.Namespace) -> int:
    import pandas as pd

    from extended import opening_run as R
    from extended import opening_states as OS

    run1 = Path(a.run1)
    sha = R.file_sha256(run1)
    man = json.loads(Path(str(run1) + ".manifest.json").read_text(encoding="utf-8"))
    par = man.get("parameters") or {}
    fsha = par.get("forecast_sha256")
    bad = R.pinned_run1_problems((ROOT / "DECISIONS.md").read_text(encoding="utf-8"), sha, fsha)
    if OS.coefficients_sha256(OS.coefficients_from_json(par.get("forecast_json", "{}"))) != fsha:
        bad.append("run 1's forecast JSON does not hash to its recorded sha256")
    if bad:
        log("REFUSED (F-03): " + "; ".join(bad))
        return 2
    pick = R.choice_pick(pd.read_csv(run1, low_memory=False))
    if pick["killed"] or not pick["pick"]:
        log("REFUSED (F-03): run 1 closed the family (Kill B, or every cell killed): there is no run 2")
        return 2
    log(f"run 2: the pick {pick['pick']} (run 1 {sha[:16]}, forecast {fsha[:16]})")
    log("STOPPED (F-03): stage C's end-to-end composition is not built (the build's hand-back); nothing read")
    return 3


def check_reads(a: argparse.Namespace) -> int:
    """Run 2's four purposes pre-checked with `reader.authorise` in stage C's order (nothing read, nothing ledgered)."""
    from extended import opening_run as R
    from extended import reader

    ok = True
    for p in R.PURPOSES:
        try:
            reader.authorise(reader.JUDGED_START, reader.JUDGED_END, purpose=p, declaration=R.DECLARATION,
                             repeat=a.repeat, what=f"F-03 {p}")
            log(f"reader: {p} AUTHORISED")
        except reader.ReadRefused as exc:
            ok = False
            log(f"reader: {p} {exc}")
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", type=int, choices=(1, 2), required=True)
    ap.add_argument("--run1", default=None, help="run 2: run 1's result file (its sha256 pinned by the lead's row)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--repeat", default=None, help="run 2: E-NNN, a row naming F-03 that authorises one more read")
    ap.add_argument("--check-guards", action="store_true", help="the refusing guards only; reads and writes nothing")
    ap.add_argument("--check-read", action="store_true", help="run 2: the four purposes pre-checked; reads nothing")
    a = ap.parse_args(argv)
    if not 1 <= int(a.workers) <= 2:
        log("REFUSED (F-03): at most two workers (CLAUDE.md)")
        return 2
    from extended import opening_run as R

    try:
        pre = R.pre_run(ROOT, need_clean=not (a.check_guards or a.check_read))
    except R.RunRefused as exc:
        log(str(exc))
        return 2
    log("guards HOLD: blobs, level, session list, the pinned text, the waited identities "
        + json.dumps(pre.rows, sort_keys=True))
    if a.check_guards:
        return 0
    if a.run == 2:
        return check_reads(a) if a.check_read else run2(a)
    from extended import use_vendored_stage2

    use_vendored_stage2()
    w = subprocess.run([sys.executable, str(ROOT / "identity" / "walker_identity.py"), "--synthetic"],
                       capture_output=True, text=True, timeout=1800)
    if w.returncode != 0:
        log("REFUSED (F-03): A1 item 2 -- E-011's walker identity (synthetic) does not hold at this commit:\n"
            + (w.stdout + w.stderr)[-1500:])
        return 3
    ctx = Ctx()
    code, df, params = run1(ctx, pre, int(a.workers))
    if code != 0:
        return code
    path = ctx.write(df, params)
    log(f"written: {path} ({len(df)} rows); the pick {params['pick']}")
    return 0


if __name__ == "__main__":
    code = main()
    print(f"EXIT {code}", flush=True)
    sys.exit(code)
