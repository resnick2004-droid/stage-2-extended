"""A synthetic Q-17 readings file pair for the journey scorecard page's tests (Q-69): `user_beside.csv` (sections
`identity`, `scorecard`, `extra`, `path`, `response`) and `user_beside_starts.csv`, made **by the writer's own code**
from toy start records -- nothing about the schema is copied by hand except the identity rows, which only the writer's
`main` makes (mirrored from `scripts/user_beside.py`'s `ident`).

    import journey_synth as SY
    summary, starts = SY.write_pair(base / "results", seed=SY.SEEDS[0])

What is the writer's: the designs, arms, file names and reading label (`scripts/user_beside.py`, loaded by path);
the responses (`extended.user_beside.RESPONSES`) and what a response did (`user_beside.response_record`, handed a toy
engine record); each start's record (Stage 2's `user_journey.start_record`, as `user_beside.long_record` composes it)
and its daily path measures (`extended.user_measures.daily`); every summary row and the per-start table
(`extended.user_readings.summary`, `rounded`) and the writer's refusing checks (`consistency_problems`, which must find
nothing here); both files written through `extended.results.write_result` with the manifest keys `main` writes.

What is toy (not a model of anything): each start day's events -- day 0 buys an evaluation, a later session may buy
another, the first pass on a random session, payouts after it, some of them "exposed" (the pattern a firm response
acts on) -- and how each response changes them, with common random numbers across responses as the writer has them.
Late start days have fewer sessions left, so every reading's eligibility (63, 126, 252 sessions) is exercised, and the
start dates straddle 2024-01-01 so the judged block has start days with the whole year left.

Q-86's money file (`write_spend`, `results/user_spend.csv`) is made the same way, by `extended.user_spend`'s own code
from the same toy events with every response off, and `write_u1_starts` writes Stage 2's U1 start rows of the same
toy records (the vendored `user_journey.start_rows`) for the page's build-time identity.

Seeds (Q-69 tests): 20266901, 20266902 -- fixed here, used nowhere else. Imports the vendored engine's pure modules:
run it in a process of its own (`tests/journey_cases.py`).
"""
from __future__ import annotations

import importlib.util
import random
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SEEDS = (20266901, 20266902)
INITIAL = 50_000.0
SCRIPT = "tests/journey_synth.py"

#: toy designs: fee, re-buy chance a session, pass chance a session, payout chance a session once funded, payout cash
#: range, the chance a payout is exposed (the pattern a firm response acts on), the chance a start day never passes
TOY = {
    "p14": (110.0, 0.10, 0.10, 0.07, (300.0, 1500.0), 0.55, 0.12),
    "p15": (110.0, 0.13, 0.07, 0.05, (400.0, 2400.0), 0.45, 0.15),
    "p16": (95.0, 0.08, 0.12, 0.04, (300.0, 1200.0), 0.35, 0.10),
}
#: the as-traded (point) arm pays a little more often than the cautious (verdict) arm
POINT_LIFT = 1.25


@lru_cache(maxsize=1)
def writer() -> Any:
    """`scripts/user_beside.py`, loaded by path (it is not importable by name), for its names and label."""
    spec = importlib.util.spec_from_file_location("s2x_user_beside_writer", ROOT / "scripts" / "user_beside.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dates(n: int, first: date) -> list[str]:
    d, out = first, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def base_events(seed: int, design: str, arm: str, s: int, observed: int) -> dict[str, Any]:
    """One start day's toy events before any firm response: fees [(day, $)], the pass day, payouts [(day, $,
    exposed)] in arrival order."""
    fee, rebuy, p_pass, p_pay, (lo, hi), p_exp, dud = TOY[design]
    if arm == "point":
        p_pay = min(0.9, p_pay * POINT_LIFT)
    rng = random.Random(f"{seed}:{design}:{arm}:{s}")
    if rng.random() < dud:
        p_pass = 0.0
    fees = [(0, fee)]
    passed = None
    pays: list[tuple[int, float, bool]] = []
    for k in range(1, observed + 1):
        if rng.random() < rebuy:
            fees.append((k, fee))
        if passed is None and rng.random() < p_pass:
            passed = k
        if passed is not None and k > passed + 1 and rng.random() < p_pay:
            pays.append((k, round(rng.uniform(lo, hi), 2), rng.random() < p_exp))
    return {"fees": fees, "pass": passed, "pays": pays}


def respond(ev: dict[str, Any], resp: Any, u: list[float]) -> dict[str, Any]:
    """The toy events under one response (`u`: the start's enforcement uniforms, one per exposed payout in order --
    shared by every response, as the writer's common random numbers are). Returns the kept fees and payouts and a toy
    engine record for `user_beside.response_record`."""
    fees, pays = list(ev["fees"]), list(ev["pays"])
    exposed = [i for i, p in enumerate(pays) if p[2]]
    conduct = {"payouts_requested": float(len(pays)), "payouts_exposed": float(len(exposed)), "payouts_denied": 0.0,
               "rtp_placed_day": -1}
    ftp: dict[str, Any] = {}
    funded: list[Any] = []
    info = None
    if resp.kind in ("denial", "forfeit"):
        denied = [i for j, i in enumerate(exposed) if u[j] < resp.enforcement_p]
        conduct["payouts_denied"] = float(len(denied) if resp.kind == "denial" else min(1, len(denied)))
        if resp.kind == "denial":
            funded = [SimpleNamespace(denied=1, ended_on=pays[i][0]) for i in denied]
            pays = [p for i, p in enumerate(pays) if i not in set(denied)]
        else:
            info = {"forfeit_day": float("nan"), "cash_forfeited": 0.0, "payouts_forfeited": 0}
            if denied:
                day = pays[denied[0]][0]
                funded = [SimpleNamespace(denied=1, ended_on=day)]
                gone = [p for i, p in enumerate(pays) if i == denied[0] or p[0] > day]
                info = {"forfeit_day": float(day), "cash_forfeited": float(sum(p[1] for p in gone if p[0] > day)),
                        "payouts_forfeited": sum(1 for p in gone if p[0] > day)}
                pays = [p for i, p in enumerate(pays) if i != denied[0] and p[0] <= day]
                fees = [f for f in fees if f[0] <= day]
    elif resp.kind == "rtp":
        nth = 3 if not resp.rtp_warnings else 3 + int(resp.rtp_warnings)
        if len(exposed) >= nth:
            day = pays[exposed[nth - 1]][0]
            conduct["rtp_placed_day"] = day
            pays = [p for p in pays if not day < p[0] <= day + 21]
    elif resp.kind == "ftp":
        ftp = {"first_placed_day": -1, "payouts_denied": 0}
        days = [f[0] for f in fees] if resp.ftp_measure == "combine_purchases" else [pays[i][0] for i in exposed]
        thr = max(1, int(resp.ftp_threshold) // (4 if resp.ftp_measure == "combine_purchases" else 1))
        for d in days:
            if sum(1 for x in days if d - 21 < x <= d) >= thr:
                ftp["first_placed_day"] = d
                break
        if ftp["first_placed_day"] >= 0:
            d0, span = ftp["first_placed_day"], (10 if resp.ftp_path == "slowdown" else 21)
            kept = [p for p in pays if not d0 < p[0] <= d0 + span]
            ftp["payouts_denied"] = len(pays) - len(kept)
            pays = kept
    return {"fees": fees, "pays": pays,
            "lp": SimpleNamespace(conduct=conduct, focused_trader=ftp or None, funded=tuple(funded)), "info": info}


def one_start(seed: int, design: str, arm: str, resp: Any, s: int, d: str, observed: int) -> dict[str, Any]:
    """One start's output in `user_beside.run_starts`' form, its record and measures made by the writer's code."""
    import numpy as np

    from extended import user_beside as B
    from extended import user_measures as M
    from propedge.research import user_journey as U

    ev = base_events(seed, design, arm, s, observed)
    n_exposed = sum(1 for p in ev["pays"] if p[2])
    er = random.Random(f"{seed}:enforcement:{s}")      # one uniform an exposed payout, the same in every response
    u = [er.random() for _ in range(n_exposed)]
    got = respond(ev, resp, u)
    rel = np.zeros(observed + 1)
    for day, f in got["fees"]:
        rel[day:] -= f
    arr = [(day, c) for day, c, _ in got["pays"]]
    for day, c in arr:
        rel[day:] += c
    cash = INITIAL + rel
    rec = {"start_day": int(s), "start_date": d,
           **U.start_record(cash, INITIAL, [ev["pass"]] if ev["pass"] is not None else [],
                            [ev["pass"] + 1] if ev["pass"] is not None and ev["pass"] + 1 <= observed else [], arr)}
    return {"rec": rec, "differs": [], "checked": [], "pay_bad": 0, "cash_bad": 0, "fee_bad": 0, "record_same": None,
            "daily": M.daily(cash - INITIAL), "response": B.response_record(got["lp"], resp, got["info"]),
            "seed": B.start_seed(s)}


#: a subset of the responses with one of every kind, for the fast tier (each reading costs the writer's scorecard,
#: about a third of a second, whatever the start count)
FAST_RESPONSES = ("off", "denial_25", "forfeit_25", "rtp_w3", "ftp_corrective_lost_3")


def observed_days(starts: int, full: int) -> list[int]:
    """The sessions each start day has left: the whole year for the first `full`, then fewer and fewer down to 30 --
    the window's end, compressed (the real file's last 252 start days fall away one session a day)."""
    tail = starts - full
    return [252 if s < full else int(round(245 - (245 - 30) * (s - full) / max(1, tail - 1))) for s in range(starts)]


def frames(seed: int = SEEDS[0], *, starts: int = 130, full: int = 80, first: date = date(2023, 10, 2),
           designs: tuple[str, ...] | None = None, responses: tuple[str, ...] | None = None):
    """(the summary frame, the per-start frame, the parameters) as `scripts/user_beside.py`'s `main` assembles them.
    `starts` start days from `first` (weekdays), the first `full` with the whole year left; every design, both arms,
    the responses named (default: all of the writer's)."""
    import pandas as pd

    from extended import user_beside as B
    from extended import user_readings as R
    from propedge.research import user_journey as U

    W = writer()
    designs = tuple(W.DESIGNS) if designs is None else designs
    resps = B.RESPONSES if responses is None else tuple(B.BY_NAME[r] for r in responses)
    dates = _dates(starts, first)
    obs = observed_days(starts, full)
    if max(obs) != U.HORIZON:
        raise ValueError("the whole year is the writer's horizon")
    idents: list[dict] = []
    rows: list[dict] = []
    parts = []

    def ident(design, arm, check, compared=0):              # scripts/user_beside.py's `ident`, every check holding
        idents.append({"section": "identity", "design": design, "arm": arm, "response": "off", "measure": check,
                       "stat": "holds", "value": 1.0, "n": compared, "note": ""})

    for name in designs:
        ident(name, "", "D-620's declaration; the builder's identity rows; the vendored 0 %, placement-off replay "
                        "call; the binding Focused Trader models")
        for arm in U.ARMS:
            for resp in resps:
                outs = [one_start(seed, name, arm, resp, s, dates[s], obs[s]) for s in range(starts)]
                srows, table = R.summary(name, arm, resp, outs, blocks=R.Q44_BLOCKS)       # W3.1: named
                probs = R.consistency_problems(srows, outs, f"{name}|{arm}|{resp.name}", blocks=R.Q44_BLOCKS)
                if probs:
                    raise RuntimeError("the synthetic readings fail the writer's own checks: " + "; ".join(probs[:4]))
                ident(name, arm, f"{resp.name}: every run's payouts and fees against the engine's totals; the extra P "
                                 "equal to the card's; the limits' P ordered; shares in [0, 1]", len(outs))
                rows += srows
                parts.append(R.rounded(table))
                idents.append({"section": "identity", "design": name, "arm": arm, "response": resp.name,
                               "measure": "exact-length runs whose event days differ from the long replay's (read "
                               "from the exact run where made)", "stat": "count", "value": 0.0,
                               "n": len(outs) if resp.name == "off" else len(outs[::B.EXACT_EVERY]),
                               "note": "every start" if resp.name == "off" else
                               f"the starts whose index is a multiple of {B.EXACT_EVERY}"})
    res = pd.DataFrame(idents + rows)
    res.insert(1, "reading", W.READING)
    st = pd.concat(parts, ignore_index=True)
    params = {"task": "Q-69 test fixture", "designs": list(designs), "arms": list(U.ARMS),
              "responses": [r.as_dict() for r in resps], "starts": starts, "denial_seed": B.DENIAL_SEED,
              "bankroll_limits": list(R.BANKROLL_LIMITS), "n_eff": f"Bartlett, lag {R.N_EFF_LAG}", "mdd": R.MDD_NOTE,
              "first_window": R.FIRST_WINDOW, "year_window": R.YEAR_WINDOW, "generator": SCRIPT, "seed": seed,
              "conventions": {
                  "forfeiture": "toy: a denied payout ends every later payout and purchase",
                  "bankroll_limit": "a start counts as ahead at a month only if its cash spent before the first payout "
                                    "is within the limit (the replay's own path, not a re-run with a wallet)",
                  "path_measures": "each start's toy path (daily closes)",
                  "break_even": "the first close k >= 1 with cumulative net at or above zero (to 1e-6)",
                  "months": "sessions 21(m-1)+1 .. 21m are month m; a payout belongs to the month its cash arrives in"}}
    return res, st, params


def spend_outs(seed: int = SEEDS[0], *, starts: int = 130, full: int = 80, first: date = date(2023, 10, 2),
               designs: tuple[str, ...] | None = None) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Q-86's per-start outputs (`extended.user_spend._task`'s form: the U1 record and the money) for every design and
    arm with every response off, from the same toy events as the readings pair: each start day's fees and payouts
    session by session, its evaluations' purchase days (every toy fee is an evaluation bought), its first pass and
    first payout from the record (`one_start`'s, made by U1's `start_record`)."""
    import numpy as np

    from extended import user_beside as B
    from extended import user_spend as US
    from propedge.research import user_journey as U

    W = writer()
    designs = tuple(W.DESIGNS) if designs is None else designs
    dates = _dates(starts, first)
    obs = observed_days(starts, full)
    off = B.BY_NAME["off"]
    out = {}
    for name in designs:
        for arm in U.ARMS:
            outs = []
            for s in range(starts):
                o = one_start(seed, name, arm, off, s, dates[s], obs[s])
                ev = base_events(seed, name, arm, s, obs[s])
                f, p = np.zeros(obs[s] + 1), np.zeros(obs[s] + 1)
                for d, v in ev["fees"]:
                    f[d] += v
                for d, c, _ in ev["pays"]:
                    p[d] += c
                r = o["rec"]
                outs.append({"rec": r, "differs": [], "spend": US.spend_record(f, p, [d for d, _ in ev["fees"]], [],
                                                                                r["first_pass"], r["first_payout"])})
            out[(name, arm)] = outs
    return out


def write_spend(results_dir: Path, seed: int = SEEDS[0], *, script: str = SCRIPT, exploratory: bool = True,
                **kw) -> Path:
    """Q-86's money file as `scripts/user_spend.py`'s `main` writes it (`extended.user_spend.frame`, the identity rows
    mirrored from its `ident`, every check holding), through `extended.results.write_result`."""
    from extended import user_beside as B
    from extended import user_spend as US
    from extended.results import write_result

    outs = spend_outs(seed, **kw)
    idents, tables, summary = [], [], []
    for name in dict.fromkeys(n for n, _ in outs):
        idents.append(US.identity_row(name, US.DESIGN_IDS[name], "", "the build (toy)", 2))
        for arm in US.ARMS:
            t = US.start_table(name, US.DESIGN_IDS[name], arm, outs[(name, arm)])
            tables.append(t)
            summary += US.summary_rows(t)
            idents.append(US.identity_row(name, US.DESIGN_IDS[name], arm, "the replay (toy)", len(t)))
    res = US.frame(idents, tables, summary, US.READING)
    idents.append(US.identity_row("", "", "", "the written frame", len(res)))
    res = US.frame(idents, tables, summary, US.READING)
    bad = US.output_problems(res)
    if bad:
        raise RuntimeError("the synthetic money file fails the writer's own checks: " + "; ".join(bad[:4]))
    csv, _ = write_result(res, "user_spend", script=script, seed=B.DENIAL_SEED, results_dir=results_dir,
                          parameters={"task": "Q-86 test fixture", "generator": SCRIPT, "seed": seed},
                          description="Q-86 test: a synthetic money file in the form of scripts/user_spend.py's",
                          exploratory=exploratory, variant_count=len(outs), notes={"status": US.READING})
    return csv


def write_u1_starts(results_dir: Path, seed: int = SEEDS[0], **kw) -> Path:
    """Stage 2's U1 start rows (`user_journey.start_rows`, the vendored script's own) for the toy records, as a result
    file with its manifest -- the build-time identity's stand-in for `vendor/stage2/results/user_journey.csv`."""
    import pandas as pd
    import user_journey as UJ

    from extended.results import write_result

    rows = []
    for (name, arm), outs in spend_outs(seed, **kw).items():
        rows += UJ.start_rows({"config": name, "label": "", "cell": ""}, arm, outs)
    csv, _ = write_result(pd.DataFrame(rows), "user_journey_toy", script=SCRIPT, seed=seed, results_dir=results_dir,
                          parameters={"task": "Q-86 test fixture"}, description="Q-86 test: toy U1 start rows")
    return csv


def write_pair(results_dir: Path, seed: int = SEEDS[0], *, exploratory: bool = True, script: str = SCRIPT,
               **kw) -> tuple[Path, Path]:
    """Both files with their manifests through `extended.results.write_result`, as `main` writes them."""
    from extended import user_beside as B
    from extended.results import write_result

    W = writer()
    res, st, params = frames(seed, **kw)
    n_read = len(params["designs"]) * len(params["arms"]) * len(params["responses"])
    a = write_result(res, W.RESULT, script=script, seed=B.DENIAL_SEED, parameters=params, results_dir=results_dir,
                     description="Q-69 test: a synthetic readings file in the form of scripts/user_beside.py's",
                     exploratory=exploratory, variant_count=n_read,
                     notes={"status": W.READING, "selection": "none"})
    b = write_result(st, W.STARTS_RESULT, script=script, seed=B.DENIAL_SEED, results_dir=results_dir,
                     parameters={"result": f"{W.RESULT}.csv", "columns": list(st.columns), "money": "to the cent"},
                     description="Q-69 test: the synthetic per-start companion", exploratory=exploratory,
                     variant_count=n_read, notes={"status": W.READING, "companion_of": f"{W.RESULT}.csv"})
    return a[0], b[0]

