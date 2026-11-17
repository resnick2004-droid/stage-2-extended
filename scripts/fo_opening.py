"""F-03 (family O, `prereg/F-03_opening_timing.md`, pinned by E-095): the two family runs (section 19.2). HEAVY: one at a
time on the machine, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched.

    python scripts/fo_opening.py --run 1 --workers 2                      # stages A and B, the choice block only
    python scripts/fo_opening.py --run 1 --check-guards                   # the refusing guards only; reads nothing
    python scripts/fo_opening.py --run 2 --run1 results/fo_opening.csv --check-read   # run 2's four reads, pre-checked
    python scripts/fo_opening.py --run 2 --run1 results/fo_opening.csv --workers 2    # stage C and the scorecard

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
forecast (its canonical JSON and sha256 in the manifest) and the pick. **A10's consequence** runs inside run 1 when A10 records `cons` lax on c in a surviving cell's deciding class
(`extended.opening_stats.a10_consequence`: both shares, both levels; its inner draws keyed by A10's replication key
extended by the inner index, the lead's reading in E-112; the exact shortcut). Run 1 also holds the offer lookup on
every start's window (m3), A1 items 4 and 5 against the wrapper's own declines (M2), A3's three checks (M3), and writes
u3's fold fits (M5). `--t3 <run 1's file>` is T-3 as declared (heavy, between run 1 and the lead's row).

**Run 2** (stage C, section 12; the scorecard, 13) reads run 1's file and u3's forecast only by the hashes the lead
pinned between the runs (T-9), then the judged block in stage C's order, each purpose authorised and ledgered by
`extended/reader.py` just before its stage (`Ctx.authorise`; `--repeat E-NNN` only under a row naming F-03):
`stage_C_states` (A1's judged day kinds and the bars: the pick's states by the frozen forecast, the population offers
from the bars alone, the strata counts and run lengths, hashed; K0 on the judged C1 counts), `stage_C_judgement` (the
population's walks, both flatten conventions and Q-20's corrected moves, the labels: L, the halves, a*, B2, C1, C1-close,
C3), `stage_C_campaign` (the paired U1 replays of the design, its two clustered twin designs and P-16: K0 on the judged
C2 counts before any value is attached, B2 for C2, C2 and V_line; the floors, floor (iii) on the design's own gate
campaign at the gate's declared seed; the beside readings, the placement on, the zero-edge twin and P-16's campaign at
the same seed among them) and `stage_C_scorecard` (the journeys of the design, its twin design (draw 0) and P-16 on
both arms under the responses, `extended.user_readings`' card, measures and path readings, the paired readings with
`pcons` beside, the frontier, the notes). It writes `results/fo_opening_judged.csv` (sections `level`, `judged`,
`campaign`, `floor`, `beside`) and `results/fo_journey.csv`, each with its manifest -- run 1's file is never rewritten.

The last line printed is `EXIT <code>`: 0 written, 2 refused by a guard, 3 an identity, a kill or an unbuilt branch
(A10's consequence) stopped the run.
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
RESULT_JUDGED = "fo_opening_judged"
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
    a3_window: int = 30
    a10_inner: int = 20_000
    b2: int = 1_000_000
    gate_paths: int = 500
    responses: tuple[str, ...] = ("off", "denial_10", "denial_25", "denial_50", "forfeit_10", "forfeit_25",
                                  "forfeit_50", "rtp", "rtp_w3")


@dataclass
class Ctx:
    """Run 1's reads and registered inputs. The real context reads through `extended/reader.py` (the choice block, no
    tag) and the vendored engine; the synthetic test's overrides the reads."""
    results_dir: Path | None = None
    sizes: Sizes = field(default_factory=Sizes)
    smoke: bool = False
    repeat: str | None = None
    authorised: list = field(default_factory=list)

    # ---- run 2's judged reads, each under its purpose (19.1), authorised just before its stage
    def authorise(self, purpose: str) -> None:
        from extended import VENDOR_STAGE2, opening_run as R, reader

        files = [VENDOR_STAGE2 / f for f in ("data/bars/NQ/bars.parquet", "data/atlas/A1/days.parquet")]
        reader.authorise_engine_read(reader.JUDGED_START, reader.JUDGED_END, purpose=purpose,
                                     declaration=R.DECLARATION, repeat=self.repeat, files=files,
                                     what=f"F-03 run 2: {purpose}")
        self.authorised.append(purpose)

    def judged_days(self):
        from extended import opening_run as R, reader

        d = reader.read_walks("A1", "days", reader.JUDGED_START, reader.JUDGED_END, purpose="stage_C_states",
                              declaration=R.DECLARATION, repeat=self.repeat, columns=["date", "day_kind"],
                              what="F-03 stage_C_states: A1's judged day table")
        return d.assign(date=d["date"].astype(str), day_kind=d["day_kind"].astype(str))

    def states_grid(self, walked_choice: list[str], walked_judged: list[str]):
        import pandas as pd

        from extended import features as F
        from extended import opening_run as R, reader

        a = reader.read_bars(walked_choice[0], reader.CHOICE_END, what="F-03 stage_C_states: the choice tail")
        b = reader.read_bars(reader.JUDGED_START, reader.JUDGED_END, purpose="stage_C_states",
                             declaration=R.DECLARATION, repeat=self.repeat,
                             what="F-03 stage_C_states: the judged bars")
        bars = pd.concat([a, b], ignore_index=True)
        keep = set(walked_choice) | set(walked_judged)
        return F.grid(bars[bars["day"].astype(str).isin(keep)].reset_index(drop=True))

    def admitted(self) -> list[int]:
        from extended import opening_population as OP

        return OP.admitted_marks()

    def judged_span(self, all_dates: list[str]):
        from extended import opening_population as OP
        from extended import opening_run as R, reader
        from extended import walker as W

        return OP.build_span(str(reader.JUDGED_START), str(reader.JUDGED_END), all_dates, purpose="stage_C_judgement",
                             declaration=R.DECLARATION, repeat=self.repeat, log=log,
                             extra_rules={"be_both": W.STAGE2_BE_BOTH})

    def gate(self, trades, days, P, **kw):
        return gate_campaign(trades, days, P, **kw)

    def follow_lifts(self):
        from propedge import RESULTS_DIR

        from extended import opening_stats as ST

        return ST.amplitude_b(RESULTS_DIR)

    def p14_ahead(self, arm: str):
        from extended import p_bound as PB

        return PB.judged(PB.load_starts(configs=("p14",), arms=(arm,))[("p14", arm)])

    def ladder_seed_base(self) -> int:
        """The denial ladder's base for this file's designs: one integer from the scorecard's ladder key (section
        16; `user_beside.run_starts`' `seed_base` takes an integer)."""
        import numpy as np

        from extended import opening_stats as ST

        return int(np.random.SeedSequence([ST.SEED_SCORECARD, 1]).generate_state(1)[0])

    def write_stage_c(self, jdf, jjf, params: dict[str, Any]) -> list[str]:
        from extended import opening_run as R
        from extended import opening_stats as ST
        from extended.results import write_result

        if self.smoke:
            return []
        out = []
        for df, name, what in ((jdf, RESULT_JUDGED, "stage C: the lines, the judged readings, the campaign, the "
                                                   "floors, beside"),
                               (jjf, R.JOURNEY, "the journey scorecard (section 13), beside, never the pass line")):
            csv, _ = write_result(df, name, script=SCRIPT, seed=ST.SEED_B2, parameters=params, exploratory=True,
                                  prereg_id=R.FAMILY, variant_count=4, results_dir=self.results_dir,
                                  description=f"F-03 run 2 ({what}); EXPLORATORY until a carried design is registered.")
            out.append(str(csv))
        return out

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


def run1_more_readings(L, sp, base_rec, offers, cells: dict) -> list[dict[str, Any]]:
    """m5: run 1's readings that cannot be recovered after it -- the in-state offers by hour and day kind, their share
    per stratum (A5); the kind shares of the in-state offers against their strata and the halves by year (10 item 5);
    every P-16 trade at the report-day 07:35:00 entry (A2)."""
    import numpy as np

    from extended import opening_run as R
    from extended import opening_stagec as SC
    from extended import opening_stats as ST
    from extended import opening_states as OS

    out = []
    kl, ks = _grid(L, sp, "kl"), _grid(L, sp, "ks")
    for c in OS.BUILT:
        sel = L.flags[f"in_{c}"] & L.population
        hours = (np.asarray(L.marks) + 1020) % 1440 // 60
        for hr in sorted(set(hours.tolist())):
            out.append({"section": "supply", "cell": c, "by": "hour", "key": int(hr),
                        "in_state_offers": int(sel[:, hours == hr].sum())})
        for k in sorted(set(L.kind.tolist())):
            out.append({"section": "supply", "cell": c, "by": "day_kind", "key": str(k),
                        "in_state_offers": int(sel[L.kind == k].sum())})
        for gi, (k, yr) in enumerate(L.groups):
            rows = L.group == gi
            out.append({"section": "supply", "cell": c, "by": "stratum_share", "key": f"{k}|{yr}",
                        "share": float(sel[rows].sum() / max(1, L.population[rows].sum()))})
        out += [{"section": "choice", "kind": "kind_share", "cell": c, **x} for x in SC.kind_shares(L, kl, ks, sel)]
        for yr in sorted(set(L.year.tolist())):
            m_ = np.broadcast_to((L.year == yr)[:, None], sel.shape)
            out.append({"section": "choice", "kind": "halves_by_year", "cell": c, "year": int(yr),
                        "L_long": ST.lift(L, np.where(m_, ST.centred(L, "rl", L.population), np.nan), sel),
                        "L_short": ST.lift(L, np.where(m_, ST.centred(L, "rs", L.population), np.nan), sel)})
    t = base_rec.trades("p16", ARM, "off")
    t = t[(t["source"] == "strategy") & t["offer"].isin(offers.index)]
    o = offers.loc[t["offer"].to_numpy()]
    at = (o["day_kind"].astype(str).to_numpy() == "b") & (o["slot"].to_numpy() == F_slot(7, 35))
    out.append({"section": "openings", "cell": "-", "design": "p16", "group": "trades", "key": "report_day_0735",
                "count": int(at.sum()), "share": float(at.mean()) if len(at) else float("nan")})
    del R
    return out


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


def F_slot(h: int, m: int) -> int:
    from extended import features as F

    return F.slot(h, m)


def a3_cuts(g, st, n: int, report_sessions: set[int] | None = None) -> list[tuple[int, int]]:
    """A3's cuts (9, A3; T-2's on the real frame): the first marks after 17:00, 17:30, the `asia` band's first marks
    18:00 and 18:05, `london`'s 02:00, the last mark 08:25, one population mark a session drawn by the same generator,
    and on report-day sessions their first mark 07:40 -- on sessions drawn by `[SEED_SHIFT, 10**6]` among those where
    the states are defined, every roll and DST session among them first; at least `n` cuts (200 declared)."""
    import numpy as np

    from extended import opening_states as OS
    from extended import opening_stats as ST

    first = [0, 5, OS.NIGHT_FIRST_MARK, 60, 65, F_slot(2, 0), F_slot(8, 25)]
    defined = [i for i in range(len(st.days)) if np.isfinite(st.share("s1")[i]).any()]
    special = [i for i in special_sessions(g) if i in set(defined)]
    rng = np.random.default_rng([ST.SEED_SHIFT, 10 ** 6])
    pool = [i for i in defined if i not in set(special)]
    k = max(0, n // (len(first) + 1) + 1 - len(special))
    days = special + [int(x) for x in rng.choice(pool, size=min(len(pool), k), replace=False)]
    kinds = report_sessions or set()
    cuts = []
    for d in days:
        marks = list(first) + [int(rng.choice(OS.POPULATION_MARKS))]
        if d in kinds:
            marks.append(OS.REPORT_DAY_FIRST_MARK)
        cuts += [(int(d), int(m)) for m in marks]
    return cuts[: max(n, len(special) * len(first))]


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
    kinds_c = dict(zip(A1["date"], A1["day_kind"]))
    report = {i for i, d in enumerate(st.days) if kinds_c.get(d.isoformat()) == "b"}
    cuts = a3_cuts(g, st, z.a3_cuts, report)
    a3 = OS.invariance_problems(g, st, cuts, ST.SEED_SHIFT)
    defined = [i for i in range(len(st.days)) if np.isfinite(st.share("s1")[i]).any()]
    a3w = OS.window_problems(g, st, defined[:: max(1, len(defined) // max(1, z.a3_window))][: z.a3_window],
                             ST.SEED_SHIFT)
    ab_rows = np.array([d.isoformat() >= STAGE_AB_FIRST for d in st.days])
    a3d = OS.degenerate_problems(st, ab_rows)
    out += R.rows("identity", [{"check": "A3: the states and y_hat read no bar at or after the alert", "cuts": len(cuts),
                                "holds": not a3, "problems": a3[:3]},
                               {"check": "A3: the alert day's 08:30-08:59 bars change no state",
                                "sessions": z.a3_window, "holds": not a3w, "problems": a3w[:3]},
                               {"check": "A3: no state all-undefined or constant on stage A's span", "holds": not a3d,
                                "problems": a3d[:3]}])
    a3 = a3 + a3w + a3d
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
    never_spec = OW.WaitSpec.for_blocks("never", job["blocks"], [np.zeros(len(b), bool) for b in job["blocks"]])
    probs += OW.lookup_problems(never_spec, job, starts)                                      # m3: the lookup, every start
    never = OW.waiting_class(never_spec)
    _, rn = replay("fo_never", job, starts, workers, never, ids)
    on = OW.openings(rn, "fo_never", ARM, "off")
    dn = rn.declined("fo_never", ARM, "off")
    if len(on) and not (on["opening_session"] >= OW.W_DECLARED).all():
        probs.append("A1 item 4: with the state never on an opening fell inside the wait")
    probs += [f"A1 item 4: {p}" for p in OW.wait_problems(on, dn, None)]
    if not len(dn):
        probs.append("A1 item 4: the never-on wait declined nothing (the identity does not bite)")
    tw0, _ = ST.clustered_twin(L, L.flags["in_s1"], OS.CELL_INDEX["s1"], ST.BLOCK_CHOICE, 0)
    placebo = grid_flags(L, tw0)
    pspec = OW.WaitSpec.for_blocks("s1_twin0", job["blocks"], flags_by_block(ids, placebo))
    _, rp = replay("fo_s1_twin0", job, starts, workers, OW.waiting_class(pspec), ids)
    op_ = OW.openings(rp, "fo_s1_twin0", ARM, "off")
    dp = rp.declined("fo_s1_twin0", ARM, "off")
    probs += [f"A1 item 5: {p}" for p in OW.wait_problems(op_, dp, placebo)]
    inset = [ids[int(s_) + int(h_)][int(j_)] for s_, h_, j_ in zip(dp["start_day"], dp["historical_day"],
                                                                  dp["trade_index"]) if placebo.get(
        ids[int(s_) + int(h_)][int(j_)], False)]
    if inset:
        probs.append(f"A1 item 5: {len(inset)} declined offers are in the placebo set (first {inset[0]})")
    if not len(dp) or not int(op_["in_wait"].sum()):
        probs.append(f"A1 item 5: {len(dp)} declines and {int(op_['in_wait'].sum())} in-wait openings -- the identity "
                     "must see both")
    w0 = OW.waiting_class(OW.WaitSpec.for_blocks("w0", job["blocks"], flags_by_block(ids, placebo), W=0))
    from extended import user_beside as B

    base4 = B.run_starts("p16", ARM, B.BY_NAME["off"], job, starts[:4], int(workers))       # m4: unrecorded
    w0_outs, w0_rec = replay("p16_w0", job, starts[:4], workers, w0, ids)
    sys.path.insert(0, str(ROOT / "identity"))
    import user_beside_identity as I

    probs += [f"A1 item 7: {p}" for p in I.class_outs_problems(base4, w0_outs, w0, "the wait off, recorded")]
    probs += [f"A1 records: {p}" for p in (rn.problems() + rp.problems() + w0_rec.problems())[:5]]
    reuse = {"s1_twin0": rp}                                                               # m11
    del rn, w0_rec, base4, w0_outs
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
    keep_all: dict[str, dict[str, Any]] = {}
    pos = {d: i for i, d in enumerate(cal)}
    for c in OS.BUILT:
        sel = L.flags[f"in_{c}"]
        rl_ = run_lengths((sel & L.population).any(axis=1))
        out += R.rows("persistence", [{"cell": c, **rl_, "implied_class": ST.implied_class(
            rl_["mean_run"], float((sel & L.population).any(axis=1).mean())), "deciding_class": DECIDING_CLASS[c]}])
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
            got = reuse.pop(f"{c}_twin{d}", None)
            twins.append(got if got is not None else
                         replay(f"fo_{c}_twin{d}", job, starts, workers, OW.waiting_class(tspec), ids)[1])
        ops = OW.openings(rec, f"fo_{c}", ARM, "off", offers)
        tops = [OW.openings(r_, r_.recorded()[0][0], ARM, "off", offers) for d, r_ in enumerate(twins)]
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
        keep_all[c] = keep[c]
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
    a_b, b_rows = ctx.follow_lifts()
    out += R.rows("level_control", [{"check": "A10_consequence_b", **r_} for r_ in b_rows])
    for c in list(keep):
        if not a10[(a10["class"] == DECIDING_CLASS[c]) & a10["lax"]].shape[0]:
            continue
        res = ST.a10_consequence(L, "c", DECIDING_CLASS[c], a_b, selections=z.a10, inner=z.a10_inner)
        out += R.rows("level_control", [{"cell": c, **r_} for r_ in res.rows]
                      + [{"cell": c, "check": "A10_consequence_verdict", "closed": res.closed, "b2_runs": res.b2_runs,
                          "verdict": ("closed, counted" if res.closed else
                                      "`cons` lax on c in this class; the larger-of rule held on the pseudo-judged "
                                      "split")}])
        if res.closed:
            killed[c] = "A10's consequence"
            keep.pop(c)
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
    folds = {str(Y): {"json": OS.canonical_json(cf), "sha256": OS.coefficients_sha256(cf)} for Y, cf in fc.folds.items()}
    out += R.rows("states", [{"kind": "fold", "year": int(Y), "sha256": v["sha256"], "json": v["json"]}
                             for Y, v in folds.items()])
    out += R.rows("resolution", [{"cell": "population", "scope": k, "unresolved_3r": v}
                                 for k, v in ST.k2_shares(sp["kl"].to_numpy(), sp["ks"].to_numpy(),
                                                          sp["population"].to_numpy(bool), sp["year"].to_numpy()).items()])
    out += run1_more_readings(L, sp, base_rec, offers, keep_all)
    df = R.frame(out, R.RUN1_SECTIONS)
    params = {**pre.parameters(), "run": 1, "forecast_json": OS.canonical_json(fc.final), "forecast_folds": folds,
              "data_manifest_sha256": R.file_sha256(ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"),
              "identity_commits": pre.commits,
              "forecast_sha256": fc.coefficients_sha256, "states_sha256": states_sha,
              "population_sha256": OP.frame_sha256(pop), "coin_digest": span.coin_digest, "starts": len(starts),
              "calendars": {"identity": "the U1 replay of choice-block starts", "openings": "the U1 replay in "
                            "history's order", "wait": "the U1 replay in history's order", "supply": "offer level",
                            "resolution": "offer level", "choice": "offer level (L) and the U1 replay (V_B)"},
              "seeds": list(ST.SEEDS), "sizes": vars(z), "pick": pick["pick"], "killed": killed, "screen": screen,
              "workers": int(workers), "seconds": round(time.time() - t_all, 1)}
    return 0, df, params


# ------------------------------------------------------------------------------------------------ run 2


STAGE_C_RESPONSES = ("off", "denial_10", "denial_25", "denial_50", "forfeit_10", "forfeit_25", "forfeit_50", "rtp",
                     "rtp_w3")
SCORECARD_ARMS = ("verdict", "point")
SHARE_HISTORY = 300                    # choice-block walked sessions read before the judged block (the 250-session share)


def gate_campaign(trades, days: list[str], P: dict[str, Any], *, seed: int, n_paths: int, workers: int, cls=None,
                  rtp: bool = False, zero_edge: bool = False, flags_of=None):
    """A gate campaign on a span's trades as P-16's gate call is made (`identity/gate_identity.py`'s `p16_problems`):
    `score_fv3_grid.gate_blocks`, `atlas_a3.gate_kwargs` at P-16's registered shift and capacity, the strict rule and
    the budget, through `extended.gate.run_gate` -- with the waiting class in index mode (`cls(blocks)`), the placement
    on (`rtp`) or every R shifted to a zero mean by its own e (`portfolio_stage.zero_edge_blocks`)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf

    from extended import gate as XG

    fcfg, tv = P["fcfg"], float(P["tv"])
    keys = B.rrs(trades)
    blocks, n_used = gf.gate_blocks(trades, list(days), tv, keys, require_sides=True, require_exits=True)
    if n_used != len(trades):
        raise RuntimeError("the gate's blocks hold a different number of trades")
    e_by, lb_by = dict(P["e_by"]), dict(P["lb_by"])
    if zero_edge:
        blocks = ps.zero_edge_blocks(blocks, e_by, float(fcfg["state_policy"]["fresh"]["funded_rr"]))
        e_by = {k: 0.0 for k in e_by}
        lb_by = {k: 0.0 for k in lb_by}
    pcfg = fcfg["portfolio"]
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])})
    hook = lt.lever_hook(inner)
    kw = A.gate_kwargs(blocks, fcfg, tv, P["plan"], e_by, lb_by, hook, seed=int(seed), n_paths=int(n_paths),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=int(P["cap"]), levels=(0.0,),
                       rtp=bool(rtp), one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    blk = kw.pop("blocks")
    extra = {"funded_account_cls": cls(blk)} if cls is not None else {}
    rows, _ = XG.run_gate(blk, workers=int(workers), **extra, **kw)
    return rows, blk


def run2(ctx: Ctx, pre, workers: int, run1_df, run1_params: dict[str, Any]) -> tuple[int, Any, Any, dict[str, Any]]:
    """Stage C (section 12) and the scorecard (13) on the judged block, in the declared order -- each judged read
    authorised just before its stage (`Ctx.authorise`): `stage_C_states`, K0 on the judged C1 counts,
    `stage_C_judgement`, `stage_C_campaign` (K0 on the judged C2 counts before any value is attached), the floors,
    `stage_C_scorecard`. Returns (the exit code, the judged frame, the journey frame, the parameters)."""
    import numpy as np
    import pandas as pd

    from extended import features as F
    from extended import opening_population as OP
    from extended import opening_run as R
    from extended import opening_stagec as SC
    from extended import opening_states as OS
    from extended import opening_stats as ST
    from extended import opening_wait as OW
    from extended import reader
    from extended import user_beside as B
    from extended import user_readings as UR

    t_all = time.time()
    z = ctx.sizes
    pick = R.choice_pick(run1_df)
    c = pick["pick"]
    ci = OS.CELL_INDEX[c]
    fc = OS.coefficients_from_json(run1_params["forecast_json"])
    out: list[dict[str, Any]] = []
    jr: list[dict[str, Any]] = []
    P = ctx.p16()
    mdv = ctx.mean_dv()
    A1c = ctx.a1_days(str(reader.CHOICE_START), str(reader.CHOICE_END))
    cal = list(pre.judged_sessions)
    n = len(cal)

    # ---- 1. stage_C_states: the judged bars, the pick's states, the strata counts, the run lengths
    ctx.authorise("stage_C_states")
    A1j = ctx.judged_days()
    if sorted(A1j["date"]) != sorted(cal):
        return _refuse("the judged day table is not the pinned judged session list"), None, None, {}
    kinds = dict(zip(A1j["date"], A1j["day_kind"]))
    kinds_all = {**dict(zip(A1c["date"], A1c["day_kind"])), **kinds}
    all_dates = sorted(set(A1c["date"]) | set(cal))
    walked_c = sorted(A1c.loc[A1c["day_kind"].isin(OP.WALKED_KINDS), "date"])[-SHARE_HISTORY:]
    walked_j = sorted(A1j.loc[A1j["day_kind"].isin(OP.WALKED_KINDS), "date"])
    g = ctx.states_grid(walked_c, walked_j)
    st = OS.compute(g, frozen=fc, test_years=())
    if st.forecast.coefficients_sha256 != run1_params["forecast_sha256"]:
        return _refuse("the frozen forecast is not run 1's"), None, None, {}
    arrays = {d.isoformat(): tuple(np.r_[np.nan, X[i][:1330]] for X in (g.O, g.H, g.L, g.C))
              for i, d in enumerate(g.days) if d.isoformat() >= reader.JUDGED_START.isoformat()}
    admitted = ctx.admitted()
    pof = SC.population_offers(cal, kinds, admitted, arrays)
    sfr = st.frame()
    pof = pof.merge(sfr[["date", "slot", f"in_{c}"]], on=["date", "slot"], how="left")
    pof[f"in_{c}"] = pof[f"in_{c}"].astype("boolean").fillna(False).astype(bool)
    L0 = ST.layout(pof, cal, kinds=kinds, values=(), flags=[f"in_{c}"])
    sel0 = L0.flags[f"in_{c}"] & L0.population
    sel_sha = OS.states_sha256(pof.rename(columns={f"in_{c}": f"in_{c}"}), cells=[c])
    out += R.rows("judged", [{"stage": "stage_C_states", "cell": c, "offers": int(L0.population.sum()),
                              "in_state": int(sel0.sum()), "selection_sha256": sel_sha,
                              **run_lengths(sel0.any(axis=1))}]
                  + [{"stage": "stage_C_states", "kind": "stratum_count", "group": f"{k}|{y}",
                      "in_state": int(sel0[L0.group == gi].sum()), "offers": int(L0.population[L0.group == gi].sum())}
                     for gi, (k, y) in enumerate(L0.groups)])
    # ---- 2. K0 on the pick's judged C1 counts, before any outcome is read
    k0c1 = ST.k0_family(sel0.sum(axis=1), L0.population.sum(axis=1), "nested", n, R.LEVEL, ci, ST.K0_FORMS["c1_judged"],
                        z.k0)
    out += R.rows("level", [{"line": "K0", "form": "c1_judged", **k0c1.as_dict()}])

    # ---- 3. stage_C_judgement: the population's walks, L, the halves, (d), B2, C1, C1-close, C3
    ctx.authorise("stage_C_judgement")
    spj = ctx.judged_span(all_dates)
    popj = spj.population.merge(sfr[["date", "slot", f"in_{c}"]], on=["date", "slot"], how="left")
    popj[f"in_{c}"] = popj[f"in_{c}"].astype("boolean").fillna(False).astype(bool) & popj["population"].astype(bool)
    bad = SC.population_problems(pof, popj)
    if bad:
        return _refuse("; ".join(bad)), None, None, {}
    vals = ("c", "c_close", "rl", "rs", "c_be_both") if "c_be_both" in popj else ("c", "c_close", "rl", "rs")
    Lj = ST.layout(popj, cal, kinds=kinds, values=vals, flags=[f"in_{c}"])
    sel = Lj.flags[f"in_{c}"] & Lj.population
    kl = _grid(Lj, popj, "kl")
    ks = _grid(Lj, popj, "ks")
    y = ST.centred(Lj, "c", Lj.population)
    y_close = ST.centred(Lj, "c_close", Lj.population)
    y_all = ST.centred(Lj, "c")
    # the choice span's centred values on the judged grid's marks (B2's source, both conventions, the labels for C2)
    spc = ctx.span(str(reader.CHOICE_START), str(reader.CHOICE_END), all_dates)
    cpop = spc.population[spc.population["date"] >= STAGE_AB_FIRST]
    ccal = sorted(d for d in A1c["date"] if d >= STAGE_AB_FIRST)
    Lc = ST.layout(cpop, ccal, kinds=kinds_all, values=("c", "c_close"))
    on_j = lambda V: _remark(V, Lc.marks, Lj.marks)                                   # noqa: E731
    yc, yc_close, yc_all = (on_j(ST.centred(Lc, "c", Lc.population)), on_j(ST.centred(Lc, "c_close", Lc.population)),
                            on_j(ST.centred(Lc, "c")))
    a_a = ST.amplitude_a(Lc, ST.centred(Lc, "c", Lc.population), Lc.population)
    a_b, b_rows = ctx.follow_lifts()
    out_state = Lj.population & ~sel
    a_d = ST.amplitude_d(Lj, "c", out_state)
    a_star = max(a_a, a_b, a_d)
    W1, W2 = sel.astype(float), Lj.population.astype(float)
    q1, _ = ST.b2_quantiles(ST.B2Inputs(yc, Lc.kind, Lj.kind, Lj.group, Lj.exists & Lj.population, W1, W2), a_star,
                            R.LEVEL, ST.LINE_C1, replicates=z.b2)
    q1c, _ = ST.b2_quantiles(ST.B2Inputs(yc_close, Lc.kind, Lj.kind, Lj.group, Lj.exists & Lj.population, W1, W2),
                             a_star, R.LEVEL, ST.LINE_C1_CLOSE, replicates=z.b2)
    c1 = ST.c1_line(Lj, y, sel, R.LEVEL, q1)
    c1c = ST.c1_line(Lj, y_close, sel, R.LEVEL, q1c)
    h = ST.halves(Lj, sel)
    c3 = bool(h["long"] > 0 and h["short"] > 0)
    out += R.rows("level", [{"line": "C1", **c1.as_dict()}, {"line": "C1_close", **c1c.as_dict()},
                            {"line": "C3", "L_long": h["long"], "L_short": h["short"], "passes": c3},
                            {"line": "a_star", "a": a_a, "b": a_b, "d": a_d, "a_star": a_star,
                             "set_by": ["a", "b", "d"][int(np.argmax([a_a, a_b, a_d]))]}])
    out += R.rows("beside", [{"reading": "follow_lift", **r_} for r_ in b_rows])

    # ---- 4. stage_C_campaign: the paired U1 replays, K0 on their counts, B2 for C2, V_line; the floors
    ctx.authorise("stage_C_campaign")
    days_all = sorted(cal)
    jobs = ctx.jobs(spj.trades, days_all, P)
    job = jobs[ARM]
    ids = offer_ids_of(spj.trades, days_all, job["blocks"])
    starts = list(range(len(job["blocks"])))
    if z.starts is not None:
        starts = starts[:: max(1, len(starts) // int(z.starts))][: int(z.starts)]
    offers = popj.assign(offer=[OP.offer_id(d, s) for d, s in zip(popj["date"], popj["slot"])]).set_index("offer")
    spec = OW.WaitSpec.for_blocks(c, job["blocks"], flags_by_block(ids, grid_flags(Lj, sel)))
    design = OW.waiting_class(spec)
    twin_cls = []
    for d in ST.TWIN_DRAWS:
        tw, _ = ST.clustered_twin(Lj, sel, ci, ST.BLOCK_JUDGED, d)
        twin_cls.append(OW.waiting_class(OW.WaitSpec.for_blocks(f"{c}_twin{d}", job["blocks"],
                                                                flags_by_block(ids, grid_flags(Lj, tw)))))
    _, rec_d = replay(f"fo_{c}", job, starts, workers, design, ids)
    rec_t = [replay(f"fo_{c}_twin{d}", job, starts, workers, k, ids)[1] for d, k in enumerate(twin_cls)]
    _, rec_p = replay("p16", job, starts, workers, None, ids)
    od = OW.openings(rec_d, f"fo_{c}", ARM, "off", offers)
    ot = [OW.openings(r_, f"fo_{c}_twin{d}", ARM, "off", offers) for d, r_ in enumerate(rec_t)]
    op16 = OW.openings(rec_p, "p16", ARM, "off", offers)
    pos = {d_: i for i, d_ in enumerate(cal)}
    u1c = np.bincount([pos[d_] for d_ in od["date"]], minlength=n)
    u2c = sum(np.bincount([pos[d_] for d_ in o_["date"]], minlength=n) for o_ in ot)
    k0c2 = ST.k0_family(u1c, u2c, "pair", n, R.LEVEL, ci, ST.K0_FORMS["c2_judged"], z.k0)
    out += R.rows("level", [{"line": "K0", "form": "c2_judged", **k0c2.as_dict()}])
    yv = {OP.offer_id(Lj.sessions[i], Lj.marks[k]): float(y_all[i, k]) for i, k in zip(*np.nonzero(Lj.exists))}
    mpos = {m_: k for k, m_ in enumerate(Lj.marks)}

    def uses(o_):
        U = np.zeros(Lj.exists.shape)
        for d_, s_ in zip(o_["date"], o_["slot"]):
            U[pos[d_], mpos[int(s_)]] += 1
        return U

    U1, U2 = uses(od), sum(uses(o_) for o_ in ot)
    out_c2 = Lj.exists & ~sel
    a_d2 = ST.amplitude_d(Lj, "c", out_c2)
    a_a2 = ST.amplitude_a(Lc, ST.centred(Lc, "c"), Lc.exists)
    a2 = max(a_a2, a_b, a_d2)
    q2, _ = ST.b2_quantiles(ST.B2Inputs(yc_all, Lc.kind, Lj.kind, Lj.group, Lj.exists, U1, U2), a2, R.LEVEL,
                            ST.LINE_C2, replicates=z.b2)
    oall = pd.concat(ot, ignore_index=True)
    c2 = ST.two_sample_line(od["offer"].map(yv).to_numpy(), od["date"].map(pos).to_numpy(),
                            oall["offer"].map(yv).to_numpy(), oall["date"].map(pos).to_numpy(), n, R.LEVEL, q2)
    sess = [min(252, len(job["blocks"]) - s_) for s_ in starts]
    u_d = ST.openings_a_start_year(len(od), sess)
    v_line = ST.v_line(u_d, mdv, c2.bound) if np.isfinite(c2.bound) else float("nan")
    c2_pass = bool(np.isfinite(v_line) and v_line >= ST.BAR_DOLLARS and c2.bound > 0)
    out += R.rows("level", [{"line": "C2", **c2.as_dict(), "u_d": u_d, "V_line": v_line, "passes_bar": c2_pass,
                             "a_star": a2, "a": a_a2, "d": a_d2}])
    out += R.rows("campaign", opening_counts(od, "design", c) + opening_counts(op16, "p16", "-")
                  + [x for d, o_ in enumerate(ot) for x in opening_counts(o_, f"twin{d}", c)])
    # the floors
    pool = SC.pooled_years(Lj.year)
    f1 = SC.floor_resolution(kl[Lj.population], ks[Lj.population], sel[Lj.population], np.broadcast_to(
        Lj.year[:, None], sel.shape)[Lj.population], pool)
    f1b = SC.floor_taken_flattened(rec_d.trades(f"fo_{c}", ARM, "off"), offers, pool)
    gate_cls = _index_class(c, spj.trades, days_all, Lj, sel)
    grows, _ = ctx.gate(spj.trades, days_all, P, seed=ST.SEED_GATE, n_paths=z.gate_paths, workers=workers,
                        cls=gate_cls)
    fg = SC.floor_gate(grows)
    floors = {"i_in_state_unresolved": f1["holds"], "i_taken_flattened": f1b["holds"], "ii_realised_risk": fg["floor_ii"],
              "iii_long_run_gate": fg["floor_iii"], "iv_rules_verified": True, "v_conduct_tier_1": True}
    out += R.rows("floor", [{"floor": "i", "part": "in_state_unresolved_3r", **f1["shares"], "holds": f1["holds"]},
                            {"floor": "i", "part": "taken_flattened", **f1b["shares"], "trades": f1b.get("trades"),
                             "holds": f1b["holds"]},
                            {"floor": "ii", "part": "realised_to_intended_capped_risk",
                             "value": fg["realised_to_intended_capped_risk"], "threshold": SC.FLOOR_REALISED,
                             "holds": fg["floor_ii"]},
                            {"floor": "iii", "part": "growth_on_required_at_bound", "value": fg["growth_at_bound"],
                             "seed_role": "the design's gate campaign (SEED_GATE)", "paths": z.gate_paths,
                             "holds": fg["floor_iii"],
                             "note": "on the gate's independent days the design waits less than traded in history's "
                                     "order (the second read's n2-8)"},
                            {"floor": "iv", "part": "every firm rule verified (Stage 2's ledger)", "holds": True},
                            {"floor": "v", "part": "conduct tier 1 (section 3)", "holds": True}])

    # ---- the beside readings (12), deciding nothing
    bes: list[dict[str, Any]] = []
    for yr in sorted(set(Lj.year)):
        m_ = np.broadcast_to((Lj.year == yr)[:, None], sel.shape)
        bes.append({"reading": "L_by_year", "block": "judged", "year": int(yr),
                    "L": ST.lift(Lj, np.where(m_, y, np.nan), sel),
                    "L_long": ST.lift(Lj, np.where(m_, ST.centred(Lj, "rl", Lj.population), np.nan), sel),
                    "L_short": ST.lift(Lj, np.where(m_, ST.centred(Lj, "rs", Lj.population), np.nan), sel)})
    ch1 = run1_df[(run1_df["section"] == "choice") & (run1_df["kind"] == "cell") & (run1_df["cell"] == c)]
    if len(ch1):
        bes.append({"reading": "L_by_year", "block": "choice", "by_year": ch1["by_year"].iloc[0]})
    bes += [{"reading": "kind_share", **x} for x in SC.kind_shares(Lj, kl, ks, sel)]
    cost = costs_of(P)
    bes.append({"reading": "kind_decomposition", **SC.kind_decomposition(Lj, kl, ks, sel, cost[0], cost[1])})
    if "c_be_both" in Lj.values:
        bes.append({"reading": "L_q20_corrected_moves", "rules": "STAGE2_BE_BOTH",
                    "L": ST.lift(Lj, ST.centred(Lj, "c_be_both", Lj.population), sel)})
    tw_draw = SC.drawn_twin(Lj, sel, ci)
    sess_g = np.repeat(np.arange(n)[:, None], len(Lj.marks), axis=1)
    m1, m2 = sel & np.isfinite(y), tw_draw & np.isfinite(y)
    bd = ST.LB.two_sample_bound(y[m1], sess_g[m1], y[m2], sess_g[m2], n, level=R.LEVEL)
    bes.append({"reading": "seeded_twin_draw", "draw": 0, "estimate": bd.estimate, "lower": bd.lower})
    a10 = run1_df[(run1_df["section"] == "level_control") & (run1_df.get("check") == "A10")]
    bes += [{"reading": "A10_pick_class", **{k: r_[k] for k in ("class", "share", "level", "lax") if k in r_}}
            for _, r_ in a10[a10["class"] == DECIDING_CLASS[c]].iterrows()]
    bes += [{"reading": "K0_judged", "form": f, "rate": v.rejections / v.replications, "lax": v.lax}
            for f, v in (("c1", k0c1), ("c2", k0c2))]
    yP = op16["offer"].map(yv)
    u_p = ST.openings_a_start_year(len(op16), sess)
    v_des = ST.v_line(u_d, mdv, float(od["offer"].map(yv).mean()))
    v_tw = ST.v_line(ST.openings_a_start_year(len(oall) / 2.0, sess), mdv, float(oall["offer"].map(yv).mean()))
    bes += [{"reading": "V_p16", "value": ST.v_line(u_p, mdv, float(yP.mean()))},
            {"reading": "V_design_undifferenced", "value": v_des},
            {"reading": "V_design_minus_V_twin", "value": v_des - v_tw}]
    for part in ("in_wait", "fallback"):
        a_, b_ = od[od[part]], oall[oall[part]]
        if len(a_) and len(b_):
            bes.append({"reading": f"V_{part}", "value": ST.v_line(u_d, mdv, float(a_["offer"].map(yv).mean()
                                                                                     - b_["offer"].map(yv).mean()))})
    bes += v_other_rows(rec_d, rec_t, c, popj, Lj)
    iw = ST.openings_a_start_year(int(od["in_wait"].sum()), sess)
    bes.append({"reading": "uniform_lift_valuation", "value": SC.uniform_valuation(c1.bound, iw, mdv),
                "in_wait_per_start_year": iw})
    bes.append({"reading": "p16_openings_in_state_share",
                "value": float(op16[f"in_{c}"].mean()) if len(op16) else float("nan")})
    if c == "u3":
        bands = {b_: [k for k, m_ in enumerate(st.marks) if lo <= m_ <= hi] for b_, (lo, hi, _) in OS.BANDS.items()}
        rows_ = np.array([d.isoformat() >= reader.JUDGED_START.isoformat() for d in st.days])
        bes += [{"reading": "u3_judged_skill", "band": b_, **v} for b_, v in ST.a4_skill(st.y, st.y_hat, bands,
                                                                                         rows_).items()]
    # beside floor (iii): the placement on, the zero-edge twin, P-16's campaign at the same seed; e, its bound, D-47
    on_rows, _ = ctx.gate(spj.trades, days_all, P, seed=ST.SEED_GATE, n_paths=z.gate_paths, workers=workers,
                          cls=gate_cls, rtp=True)
    ze_rows, _ = ctx.gate(spj.trades, days_all, P, seed=ST.SEED_GATE, n_paths=z.gate_paths, workers=workers,
                          cls=gate_cls, zero_edge=True)
    p16_rows, _ = ctx.gate(spj.trades, days_all, P, seed=ST.SEED_GATE, n_paths=z.gate_paths, workers=workers)
    g_on, g_ze, g_p = SC.floor_gate(on_rows), SC.floor_gate(ze_rows), SC.floor_gate(p16_rows)
    bes += [{"reading": "break_even_denial", "value": fg["break_even_denial"]},
            {"reading": "placement_on_growth_at_bound", "value": g_on["growth_at_bound"]},
            {"reading": "zero_edge_twin_growth", "value": g_ze["growth_at_point"],
             "signal_lift_over_zero_edge_twin": fg["growth_at_point"] - g_ze["growth_at_point"]},
            {"reading": "same_day_multi_breach_share", "design": fg["share_paths_with_same_day_multi_breach"],
             "p16": g_p["share_paths_with_same_day_multi_breach"]},
            {"reading": "s_program_guard", "value": fg["growth_at_bound"] - g_p["growth_at_bound"]},
            {"reading": "e_bound_d47", "note": "P-16's by construction (the same trades, P-16's registered shift); "
                                              "cited from its registration, not recomputed"},
            {"reading": "assumptions", "note": "the differencing removes the routing selection to first order; the "
                                              "state's own alignment with the night's routing is not in B2's null for "
                                              "C2; V is gross of the wait's cost and first-order; the value-map price "
                                              "at the bound is not calibrated"}]
    out += R.rows("beside", bes)
    # the verdict (12): every line and floor
    claimed = not (k0c1.lax or k0c2.lax)
    passes = bool(claimed and c1.passes and c1c.passes and c2_pass and c3 and all(floors.values()))
    verdict = ("not claimed: the judged counts make cons lax" if not claimed else "CARRIED" if passes else "CLOSED")
    out += R.rows("level", [{"line": "verdict", "cell": c, "verdict": verdict, **floors}])

    # ---- 5. stage_C_scorecard (13)
    ctx.authorise("stage_C_scorecard")
    tw0_flags = grid_flags(Lj, ST.clustered_twin(Lj, sel, ci, ST.BLOCK_JUDGED, 0)[0])
    designs = {"design": grid_flags(Lj, sel), "twin": tw0_flags, "p16": None}
    cards: dict[str, dict[str, float]] = {}
    tables: dict[tuple[str, str], Any] = {}
    for arm in SCORECARD_ARMS:
        jb = jobs[arm]
        ids_a = offer_ids_of(spj.trades, days_all, jb["blocks"])
        st_ = list(range(len(jb["blocks"])))
        if z.starts is not None:
            st_ = st_[:: max(1, len(st_) // int(z.starts))][: int(z.starts)]
        for name, k in designs.items():
            for resp in z.responses:
                kw = ({"funded_account_cls": OW.waiting_class(OW.WaitSpec.for_blocks(f"{c}_{name}_{arm}", jb["blocks"],
                                                                                  flags_by_block(ids_a, k)))}
                      if k is not None else {})
                if resp.startswith("denial") or resp.startswith("forfeit"):
                    kw["seed_base"] = ctx.ladder_seed_base()
                outs = B.run_starts(f"fo_{name}", arm, B.BY_NAME[resp], jb, st_, int(workers), **kw)
                rows_, t = UR.summary(name, arm, B.BY_NAME[resp], outs)
                jr += [dict(r_) for r_ in rows_]
                if resp == "off":
                    tables[(name, arm)] = t
                    if arm == ARM:
                        cards[name] = _card(rows_)
    for arm in SCORECARD_ARMS:
        for name, other in (("design", "p16"), ("design", "twin"), ("twin", "p16")):
            jr += [{"section": "paired", "arm": arm, **r_} for r_ in
                   SC.paired_rows(name, tables[(name, arm)], tables[(other, arm)], other)]
        p14 = ctx.p14_ahead(arm)
        if p14 is not None:
            for name in designs:
                jr += [{"section": "paired", "arm": arm, **r_} for r_ in
                       SC.paired_rows(name, tables[(name, arm)], None, "p14", b_ahead=p14)]
    jr += [{"section": "frontier", "design": k, "on_frontier": v, **cards.get(k, {})}
           for k, v in SC.frontier({k: {m_: cards[k].get(m_, np.nan) for m_ in SC.FRONTIER_MEASURES}
                                    for k in cards}).items()]
    jr += [{"section": "note", "measure": "not_modelled", "note": SC.NOT_MODELLED},
           {"section": "note", "measure": "focused_trader", "note": SC.FTP_NOTE},
           {"section": "note", "measure": "menu", "note": "E-015's limits as flags only, once the operator approves "
                                                         "them; none approved: no menu"},
           {"section": "note", "measure": "d621_3", "note": "Stage 2 D-621 (3)'s rule against P-14 beside, its line "
                                                           "(i) not holding its level (E-007 (1)); not computed here"}]
    jdf = R.frame(out, R.SECTIONS[10:])
    jjf = pd.DataFrame(jr)
    params = {**pre.parameters(), "run": 2, "pick": c, "verdict": verdict, "run1_sha256": run1_params.get("_sha256"),
              "forecast_sha256": run1_params["forecast_sha256"], "selection_sha256": sel_sha,
              "population_sha256": OP.frame_sha256(popj), "purposes": list(ctx.authorised), "sizes": vars(z),
              "seed_roles": {"twins": "SEED_TWIN", "B2": "SEED_B2", "K0": "SEED_K0", "gate": "SEED_GATE",
                             "scorecard": "SEED_SCORECARD"}, "workers": int(workers),
              "seconds": round(time.time() - t_all, 1)}
    return 0, jdf, jjf, params


def _refuse(why: str) -> int:
    log(f"REFUSED (F-03): {why}")
    return 3


def _grid(L, pop, col: str):
    import numpy as np

    pos = {d: i for i, d in enumerate(L.sessions)}
    mpos = {m: k for k, m in enumerate(L.marks)}
    G = np.full(L.exists.shape, -1, dtype=np.int64)
    G[[pos[d] for d in pop["date"]], [mpos[int(s)] for s in pop["slot"]]] = pop[col].to_numpy(np.int64)
    return G


def _remark(V, src_marks, dst_marks):
    import numpy as np

    k = {m: i for i, m in enumerate(src_marks)}
    out = np.full((V.shape[0], len(dst_marks)), np.nan)
    for j, m in enumerate(dst_marks):
        if m in k:
            out[:, j] = V[:, k[m]]
    return out


def costs_of(P: dict[str, Any]):
    import atlas_a3 as A

    from extended import walker as W

    fee = A.fee_by_stop(P["fcfg"], (150,), float(P["tv"]))[150]
    entry = float(P["cfg"]["slip_ticks"])
    return W.Costs(float(fee), float(P["tv"]), entry), entry


def _index_class(c: str, trades, days, Lj, sel):
    """The waiting class for the gate (index mode): the flags of each gate block's trades, in its trade order."""
    from extended import opening_wait as OW

    def make(blocks):
        ids = offer_ids_of(trades, days, blocks)
        return OW.waiting_class(OW.WaitSpec.for_index(f"{c}_gate", flags_by_block(ids, grid_flags(Lj, sel)),
                                                      blocks=blocks))
    return make


def _card(rows) -> dict[str, float]:
    out = {}
    for r_ in rows:
        if (r_.get("section") == "scorecard" and r_.get("block") == "judged" and r_.get("stat") == "value"
                and r_["measure"] in ("P", "S1", "S3a", "S5a")):
            out[r_["measure"]] = float(r_["value"])
    return out


def v_other_rows(rec_d, rec_t, c: str, popj, Lj) -> list[dict[str, Any]]:
    """V_other (7.4, beside): the designs' trades at places (b), (d) and (e), each valued at its own R against its own
    stratum's mean at that R (the side-symmetric value), the design's mean less the twin designs' pooled mean."""
    import numpy as np
    import pandas as pd

    from extended import opening_population as OP
    from extended import opening_stats as ST

    td = rec_d.trades(f"fo_{c}", ARM, "off")
    tt = pd.concat([r_.trades(f"fo_{c}_twin{d}", ARM, "off") for d, r_ in enumerate(rec_t)], ignore_index=True)
    out = []
    for place in ("b_evaluation", "d_funded_later", "e_paid"):
        a, b = td[td["place"] == place], tt[tt["place"] == place]
        if not len(a) or not len(b):
            continue
        val: dict[str, float] = {}
        for R in sorted(set(pd.to_numeric(pd.concat([a["rr"], b["rr"]]), errors="coerce").dropna())):
            k = OP.rkey(R)
            if f"rl_{k}" not in popj:
                continue
            popj[f"_c_{k}"] = (popj[f"rl_{k}"] + popj[f"rs_{k}"]) / 2.0
            L = ST.layout(popj, Lj.sessions, values=(f"_c_{k}",))
            yR = ST.centred(L, f"_c_{k}")
            for i, j in zip(*np.nonzero(L.exists)):
                val[f"{OP.offer_id(L.sessions[i], L.marks[j])}#{k}"] = float(yR[i, j])
        key = lambda t: [f"{o}#{OP.rkey(r)}" for o, r in zip(t["offer"], pd.to_numeric(t["rr"]))]   # noqa: E731
        va = pd.Series(key(a)).map(val).dropna()
        vb = pd.Series(key(b)).map(val).dropna()
        out.append({"reading": "V_other", "place": place, "D": float(va.mean() - vb.mean()) if len(va) and len(vb)
                    else float("nan"), "trades_design": int(len(va)), "trades_twins": int(len(vb))})
    return out


def main_run2(a: argparse.Namespace, pre) -> int:
    """Run 2's entry point: run 1's file and u3's forecast by the hashes the lead pinned (T-9), then stage C."""
    import pandas as pd

    from extended import opening_run as R
    from extended import opening_states as OS

    if not a.run1:
        log("REFUSED (F-03): run 2 reads run 1's result file (--run1)")
        return 2
    run1 = Path(a.run1)
    sha = R.file_sha256(run1)
    par = (json.loads(Path(str(run1) + ".manifest.json").read_text(encoding="utf-8")).get("parameters") or {})
    folds = [v["sha256"] for v in (par.get("forecast_folds") or {}).values()]
    df1_ = pd.read_csv(run1, low_memory=False)
    u3 = R.choice_pick(df1_)["pick"] == "u3"
    bad = R.pinned_run1_problems((ROOT / "DECISIONS.md").read_text(encoding="utf-8"), sha, par.get("forecast_sha256"),
                                 folds if u3 else ())
    if OS.coefficients_sha256(OS.coefficients_from_json(par.get("forecast_json", "{}"))) != par.get("forecast_sha256"):
        bad.append("run 1's forecast JSON does not hash to its recorded sha256")
    df1 = pd.read_csv(run1, low_memory=False)
    pick = R.choice_pick(df1)
    if pick["killed"] or not pick["pick"]:
        bad.append("run 1 closed the family (Kill B, or every cell killed): there is no run 2")
    if bad:
        log("REFUSED (F-03): " + "; ".join(bad))
        return 2
    from extended import use_vendored_stage2

    use_vendored_stage2()
    ctx = Ctx(repeat=a.repeat)
    code, jdf, jjf, params = run2(ctx, pre, int(a.workers), df1, {**par, "_sha256": sha})
    if code != 0:
        return code
    for p_ in ctx.write_stage_c(jdf, jjf, params):
        log(f"written: {p_}")
    log(f"stage C: {params['verdict']}")
    return 0


class T3Ctx(Ctx):
    """T-3 (18.2, heavy, under the lock, between run 1 and the lead's row): run 1's reads, with every judged-block bar
    or day row they return replaced by a seeded walk (the test block's T-3 key) -- so if run 1 could see the judged
    block at all, its sections would move. Nothing is copied or written."""

    def _replaced(self, bars):
        import numpy as np

        from extended import opening_stats as ST
        from extended import reader

        m = bars["day"].astype(str).to_numpy() >= reader.JUDGED_START.isoformat()
        if m.any():
            rng = np.random.default_rng([ST.SEED_TESTS, 100])
            k = int(m.sum())
            walk = 9000.0 + 0.25 * np.cumsum(np.rint(rng.normal(0.0, 40.0, k)))
            bars = bars.copy()
            for col in ("open", "high", "low", "close"):
                bars.loc[m, col] = walk
            self.replaced += k
        return bars

    replaced: int = 0

    def grid(self, start, end, walked):
        from extended import features as F
        from extended import reader

        bars = self._replaced(reader.read_bars(start, end, what=f"F-03 T-3: the bars {start} to {end}"))
        return F.grid(bars[bars["day"].astype(str).isin(walked)].reset_index(drop=True))

    def span(self, start, end, all_dates):
        from extended import opening_population as OP
        from extended import reader

        def arrays_for(chunk):
            import numpy as np

            from propedge.research import atlas_local

            bars = self._replaced(reader.read_bars(chunk[0], chunk[-1], what="F-03 T-3: the walk's bars"))
            by = {d: g for d, g in bars.groupby("day", sort=False)}
            return lambda day: tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                                     for v in atlas_local.day_arrays(by.get(day, bars.iloc[0:0])))
        return OP.build_span(start, end, all_dates, log=log, arrays_for=arrays_for)


def t3(a: argparse.Namespace, pre) -> int:
    """T-3: run 1 recomputed through `T3Ctx` must give run 1's file's sections other than `identity` byte for byte
    (as CSV text) and u3's final forecast hash."""
    import io

    import pandas as pd

    from extended import use_vendored_stage2

    use_vendored_stage2()
    f = Path(a.t3)
    par = (json.loads(Path(str(f) + ".manifest.json").read_text(encoding="utf-8")).get("parameters") or {})
    ctx = T3Ctx(smoke=True)
    code, df, params = run1(ctx, pre, int(a.workers))
    if code != 0:
        log("T-3 FAILS: run 1 did not complete under the replacement")
        return 3
    want = pd.read_csv(f, low_memory=False)
    a_, b_ = io.StringIO(), io.StringIO()
    want[want["section"] != "identity"].to_csv(a_, index=False)
    pd.read_csv(io.StringIO(df.to_csv(index=False)), low_memory=False).pipe(
        lambda d: d[d["section"] != "identity"]).to_csv(b_, index=False)
    same = a_.getvalue() == b_.getvalue() and params.get("forecast_sha256") == par.get("forecast_sha256")
    log(f"T-3 {'HOLDS' if same else 'FAILS'}: {ctx.replaced} judged-block bars replaced in run 1's reads")
    return 0 if same else 3


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
    ap.add_argument("--t3", default=None, help="run 1: T-3 against run 1's result file (heavy, under the lock)")
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
        if a.check_read:
            return check_reads(a)
        return main_run2(a, pre)
    from extended import use_vendored_stage2

    use_vendored_stage2()
    w = subprocess.run([sys.executable, str(ROOT / "identity" / "walker_identity.py"), "--synthetic"],
                       capture_output=True, text=True, timeout=1800)
    if w.returncode != 0:
        log("REFUSED (F-03): A1 item 2 -- E-011's walker identity (synthetic) does not hold at this commit:\n"
            + (w.stdout + w.stderr)[-1500:])
        return 3
    if a.t3:
        return t3(a, pre)
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
