"""RD-01's reading (`prereg/RD-01_firm_contracts.md` 6, 7, 9.2, 9.3, 10): one run's cells, the scorecard per plan paired
with TS by month, the beside readings (E-007 (e)'s measures, the denial ladder, the gate), 9.3's counts and A-10's
price grid -- as rows for `scripts/rd01_reading.py`'s result files. The adapters are `extended.firms`' and
`extended.firm_accounts`', used as built (Q-104); nothing here changes a rule.

**A cell** is one run of 7.3 (or a ladder response) at one arm: every chosen start through A-9 (`user_beside.run_starts`,
one start at a time with that start's own classes, as `firms.run_plan` composes them) -- the runner's output -- and,
beside it, the same start's runs replayed directly (`direct_start`: the long replay with the engine's per-trade ledger
on, and U1's exact-length runs where A-9 makes them), composed exactly as A-9's task composes them. **Refusing:** at the
run's own price and with no fee added the direct composition equals A-9's output bit for bit on every start
(`user_beside_identity.first_difference`), so A-10's arithmetic is applied to the runner's own replays.

**A-10 in every reading.** DayTraders' recurring Pro fee (`daytraders.eod50k.funded_monthly_fee`, every 21 sessions
after activation while the account lives) is not charged by the engine: every DT reading is the direct composition with
the fee charged by `firms.repriced` on every run of the start (long and exact-length). The price grid (10.1 item 9)
reprices every run of every start to each grid price; it must equal the one-at-a-time price run at the bracket's other
end on every start to 1e-6 (`grid_problems`). The break-even price against TS: bisection on the repriced readings.

**Pairing** (10.1 item 4, 10.2): the plan's start records against TS's on the same stream and arm, start for start;
each measure at its horizon (months 1-3: 63 sessions; month 6: 126; month 12: 252) on the blocks `all`, `early` and
`late` (`u_select.block`), the paired uncertainty of `firm_uncertainty.paired_reading`, its coverage label
(`firm_uncertainty.coverage` on the worst shape at the reading's h and n_w, seed 20261991, computed once per (h, n_w)).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Sequence

import numpy as np

from extended import use_vendored_stage2

use_vendored_stage2()

from extended import firm_accounts as A  # noqa: E402
from extended import firm_counts as C  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import firm_uncertainty as FU  # noqa: E402
from extended import firms as F  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import walker as W  # noqa: E402

DECLARATION = "prereg/RD-01_firm_contracts.md"
PURPOSES = ("firm_scorecard", "firm_ladder_beside", "firm_gate_beside")
BLOCKS = ("all", "early", "late")
#: 6 item 4: the horizon of a month's reading
HORIZON_OF_MONTH = {1: 63, 2: 63, 3: 63, 6: 126, 9: 252, 12: 252}
PAIRED_MONTHS = (1, 2, 3, 6, 9, 12)
LADDER = ("denial_10", "denial_25", "denial_50")
#: 10.2 item 7: series per coverage setting
COVERAGE_SERIES = 20_000
#: the ledger fields 9.3's counts read (the rest of each row dropped where the start ran: memory)
LEDGER_KEEP = ("kind", "index", "day", "historical_day", "trade_index", "contracts", "pnl", "fee", "u", "rr",
               "rr_used", "fee_adj_r", "at_need", "stretch")


# ------------------------------------------------------------------------------------------------ a run's inputs


def stream_of(run: T.Run) -> str:
    return {"P-16": "p16", "P-14": "p14"}[run.stream]


def arm_inputs(point: dict[str, Any], arm_job: dict[str, Any], s: T.Settings, arm: str
               ) -> tuple[list[Any], list[Any] | None, dict[str, int]]:
    """One arm's blocks for a plan: TradeDay's tier-1 booking on the point blocks then the arm's own shift (A-11);
    every other plan the arm's blocks as built. Also the run's point-arm blocks Quick Pay's bracket reads on every arm
    (M3: A-11's booking applied, no shift), and A-11's counts."""
    delta_r, dby = (0.0, None) if arm == "point" else F.arm_delta(point["blocks"], arm_job["blocks"])
    counts: dict[str, int] = {}
    blocks = list(arm_job["blocks"])
    ref = list(point["blocks"])
    if s.plan in ("FP", "QP"):
        ref, counts = F.tier1_arm(point["blocks"], point["dates"], s.tier1)
        blocks = ref if arm == "point" else F.tier1_arm(point["blocks"], point["dates"], s.tier1, delta_r, dby)[0]
    return blocks, (ref if s.plan == "QP" else None), counts


def cell_job(arm_job: dict[str, Any], s: T.Settings, blocks: Sequence[Any], *, ladder: bool = False
             ) -> tuple[dict[str, Any], dict[str, Any]]:
    """The cell's job (A-1's arguments; the classes are made per start) and A-9's keywords."""
    args, kw = F.plan_args(arm_job["args"], s, blocks=blocks if s.plan not in ("TS", "LU") else None, ladder=ladder)
    if s.plan not in ("TS", "LU"):
        args = {**args, "path": {k: v for k, v in args["path"].items() if k != "combine_account_cls"}}
        kw = {k: v for k, v in kw.items() if k != "funded_account_cls"}
    return {**arm_job, "blocks": list(blocks), "args": args}, kw


# ------------------------------------------------------------------------------------------------ one start


def _pay_totals(lag: int) -> tuple[Callable, Callable]:
    from propedge.research import user_journey as U

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    return pay, totals


def compose(design: str, arm: str, resp: Any, s: int, date: str, long_run: Any, exact: dict[int, Any] | None,
            sub: float, lag: int, seed: int, named: dict[str, Any]) -> dict[str, Any]:
    """A start's output from its runs, exactly as `user_beside._task` composes it (`exact` None: the long replay's
    record alone, as `_task` makes it on a start without exact-length runs)."""
    import customer_journey as CJ
    import customer_slices as cs
    import user_journey as UJ

    from propedge.research import user_journey as U

    pay, totals = _pay_totals(lag)
    mine = B.long_record(s, date, long_run, pay, totals)
    if exact is not None:
        o = UJ._one_start(design, arm, s, date, long_run, exact, sub, CJ.single_events, pay, totals, cs.slice_measures)
        r0 = {k: v for k, v in o["rec"].items() if k != "alt"}
        same = not U.record_problems(r0, mine["rec"]) and r0["start_date"] == mine["rec"]["start_date"] and \
            all(o[f"{k}_bad"] == mine[f"{k}_bad"] for k in ("pay", "cash", "fee"))
        o = {**o, "record_same": bool(same)}
    else:
        o = {**mine, "differs": [], "checked": [], "record_same": None}
    rel = np.asarray(long_run.path.cash_series, float) - float(long_run.path.initial_bankroll)
    return {"rec": o["rec"], "differs": o["differs"], "checked": o["checked"], "pay_bad": o["pay_bad"],
            "cash_bad": o["cash_bad"], "fee_bad": o["fee_bad"], "record_same": o["record_same"],
            "daily": M.daily(rel), "response": B.response_record(long_run, resp, None), "seed": int(seed), **named}


def _slim(lp: Any) -> Any:
    return dataclasses.replace(lp, trades=(), account_days=(), campaign_days=())


def direct_start(design: str, arm: str, resp: Any, job: dict[str, Any], s: T.Settings, start: int,
                 kw: dict[str, Any], point: list[Any] | None, every: int) -> dict[str, Any]:
    """One start, replayed directly as A-9's task replays it: the long run (its ledger kept for 9.3) and the
    exact-length runs where A-9 makes them, with the start's classes. Returns the runs and the ledger."""
    from propedge.research import user_journey as U

    if resp.kind == "forfeit":
        raise ValueError("RD-01 reads no forfeiture")
    c_cls, f_cls = F.start_classes(s, job["dates"], int(start), point)
    f_cls = f_cls if f_cls is not None else kw.get("funded_account_cls")
    args = job["args"] if c_cls is None else {**job["args"], "path": {**job["args"]["path"], "combine_account_cls": c_cls}}
    hc = kw.get("household_closure")
    a = B.response_args(args, resp, f_cls, household_closure=hc) if (f_cls is not None or hc is not None) \
        else B.response_args(args, resp)
    base = B.DENIAL_SEED if kw.get("seed_base") is None else int(kw["seed_base"])
    seed = B.start_seed(int(start), base)
    n = len(job["blocks"])
    L = min(U.HORIZON, n - int(start))
    A.TALLY.clear()
    rec_args = {**a, "path": {**a["path"], "record_trades": True}}
    long_full = B.replay(job["blocks"][start:start + L], rec_args, seed)
    counts = F.split_runs(A.collect())[:1]
    exact = None
    if int(start) % int(every) == 0:
        exact = {h: B.replay(job["blocks"][start:start + h], a, seed) for h in U.EXACT if h < L}
        A.TALLY.clear()
    named = {**B.seam_parameters(hc, kw.get("seed_base")), **B.class_parameters(f_cls)}
    return {"start": int(start), "date": str(job["dates"][start]), "long": _slim(long_full), "exact": exact,
            "ledger": [{k: r.get(k) for k in LEDGER_KEEP} for r in long_full.trades if r.get("contracts")],
            "seed": seed, "named": named, "counts": counts[0] if counts else [],
            "sub": float(a["path"]["subscription"]), "lag": int(a["path"]["payout_lag_days"]),
            "billing_days": int(a["path"]["billing_days"])}


def priced_output(design: str, arm: str, resp: Any, d: dict[str, Any], run_price: float, price: float,
                  pro_fee: float = 0.0, pro_billing_days: int | None = None) -> dict[str, Any]:
    """A start's output with every run repriced to `price` (and DayTraders' Pro fee charged): A-10."""
    def rp(lp):
        if price == run_price and not pro_fee:
            return lp
        return F.repriced(lp, run_price, price, d["billing_days"], pro_fee=pro_fee, pro_billing_days=pro_billing_days)

    exact = None if d["exact"] is None else {h: rp(lp) for h, lp in d["exact"].items()}
    sub = d["sub"] if price == run_price else float(price)
    return compose(design, arm, resp, d["start"], d["date"], rp(d["long"]), exact, sub, d["lag"], d["seed"],
                   d["named"])


# ------------------------------------------------------------------------------------------------ a cell


def run_cell(design: str, arm: str, resp: Any, job: dict[str, Any], s: T.Settings, starts: Sequence[int],
             kw: dict[str, Any], point: list[Any] | None, *, direct: bool = True,
             exact_every: int | None = None) -> dict[str, Any]:
    """Every chosen start of one cell: A-9's outputs (the runner), and -- `direct` -- each start's direct runs, held
    equal to A-9's output at the run price (refusing: `problems`)."""
    every = 1 if resp.kind == "off" else int(B.EXACT_EVERY if exact_every is None else exact_every)
    runs = F.run_plan(design, arm, resp, job, s, list(starts), kw, point=point)
    outs = [o for o, _ in runs]
    counts = [c[0] if c else [] for _, c in runs]
    problems: list[str] = []
    directs = []
    checks = {"trades": 0, "accounts": 0}
    if direct:
        from user_beside_identity import first_difference

        for o, st in zip(outs, starts):
            d = direct_start(design, arm, resp, job, s, int(st), kw, point, every)
            mine = priced_output(design, arm, resp, d, d["sub"], d["sub"])
            diff = first_difference(o, mine)
            if diff:
                problems.append(f"{design} {arm} {resp.name} start {st}: the direct runs are not A-9's -- {diff}")
            # 9.1 items 4 and 5 on every replay (m4): the trades are the base's; no other plan's class
            tp = trade_problems(d["ledger"], job["blocks"][int(st):])
            problems += [f"{design} {arm} {resp.name} start {st}: item 4: {p}" for p in tp[:3]]
            problems += [f"{design} {arm} {resp.name} start {st}: item 5: {p}" for p in class_problems(d["counts"], s)]
            checks["trades"] += len(d["ledger"])
            checks["accounts"] += len(d["counts"])
            directs.append(d)
    return {"outs": outs, "counts": counts, "directs": directs, "problems": problems, "checks": checks}


def trade_problems(ledger: Sequence[dict[str, Any]], blocks: Sequence[Any]) -> list[str]:
    """9.1 item 4 on one replay's ledger: each trade's day and index are a trade of `blocks` (the replay's own), its
    outcome the block's own at its R plus its fee re-pricing (D-324) -- or, at Quick Pay, at most that (a breach at a
    floor its own peak raised ends it sooner, 5.4)."""
    probs = []
    for r in ledger:
        h, j = int(r.get("historical_day", -1)), int(r.get("trade_index", -1))
        if not (0 <= h < len(blocks)) or not (0 <= j < len(blocks[h].pnl)):
            probs.append(f"a trade at day {h} index {j} is not in the design's blocks")
            continue
        R = r.get("rr_used", r.get("rr"))
        if R is None or blocks[h].r_by_rr is None or r.get("at_need") or r.get("stretch") or r.get("u") is None:
            continue
        want = float(blocks[h].r_by_rr[float(R)][j]) + float(r.get("fee_adj_r") or 0.0)
        if not np.isclose(float(r["u"]), want, atol=1e-9):
            probs.append(f"the trade at day {h} index {j} books {r['u']} at R {R}, the block's own is {want}")
    return probs


def class_problems(counts: Sequence[dict[str, Any]], s: T.Settings) -> list[str]:
    """9.1 item 5 on one replay (m4): at TS and LU no adapter account; at a plan every adapter account of exactly the
    class `classes_for` names for its kind (through the per-start subclasses' bases)."""
    c_cls, f_cls = A.classes_for(s)
    want = {"combine": None if c_cls is None else c_cls.__name__, "funded": None if f_cls is None else f_cls.__name__}
    bad = [g for g in counts if g.get("family") != want.get(g["kind"])]
    return [f"{len(bad)} accounts not of the plan's own class (first: {bad[0]['class']} as {bad[0]['kind']}, want "
            f"{want.get(bad[0]['kind'])})"] if bad else []


def reading_outs(cell: dict[str, Any], design: str, arm: str, resp: Any, s: T.Settings) -> list[dict[str, Any]]:
    """The outputs a reading reads: A-9's, except at DayTraders, where the recurring Pro fee is charged (A-10)."""
    if s.plan != "DT":
        return cell["outs"]
    t = T.plan_terms("DT")
    return [priced_output(design, arm, resp, d, d["sub"], d["sub"], pro_fee=float(t.funded_recurring_fee),
                          pro_billing_days=int(T.stage2_value("billing_days"))) for d in cell["directs"]]


# ------------------------------------------------------------------------------------------------ the scorecard, paired


def _net(rec: dict[str, Any], m: int) -> float:
    nm = rec.get("net_month") or []
    v = nm[m - 1] if len(nm) >= m else None
    return float("nan") if v is None else float(v)


def _block_days(recs: Sequence[dict[str, Any]], which: str, h: int) -> list[int]:
    from propedge.research import u_select as S

    sel = S.block(list(recs), None if which == "all" else which, int(h))
    return sorted(int(r["start_day"]) for r in sel)


_COVERAGE: dict[tuple[int, int], float] = {}


def coverage_of(h: int, n_w: int) -> float:
    """10.2 item 7: the worst coverage over the declared shapes at (h, n_w), seed 20261991, cached."""
    key = (int(h), int(n_w))
    if key not in _COVERAGE:
        _COVERAGE[key] = min(FU.coverage(sh, int(h), int(n_w), COVERAGE_SERIES, FU.SEED) for sh in FU.coverage_shapes())
    return _COVERAGE[key]


def paired_rows(plan: list[dict[str, Any]], ts: list[dict[str, Any]], *, coverage: bool = True) -> list[dict[str, Any]]:
    """10.1 item 4 on the plan's and TS's start records (same stream and arm): by month and block, the per-start
    difference's distribution, the shares better / equal / worse, the share-ahead cross tab (months 1-3), and the mean
    difference with 10.2's reading."""
    pr = {int(r["start_day"]): r for r in plan}
    tr = {int(r["start_day"]): r for r in ts}
    common = sorted(set(pr) & set(tr))
    rows = []
    for m in PAIRED_MONTHS:
        h = HORIZON_OF_MONTH[m]
        for b in BLOCKS:
            days = [d for d in _block_days([pr[d] for d in common], b, h) if d in tr]
            x = np.array([_net(pr[d], m) for d in days], float)
            y = np.array([_net(tr[d], m) for d in days], float)
            ok = np.isfinite(x) & np.isfinite(y)
            diff = (x - y)[ok]
            n = int(ok.sum())
            base = {"section": "paired", "block": b, "month": m, "horizon": h, "measure": f"net_month_{m}", "n": n}
            q = M.quantiles(diff)
            rows += [{**base, "stat": f"p{p}", "value": q[f"p{p}"]} for p in M.PERCENTILES]
            for k, v in (("better", diff > 1e-9), ("equal", np.abs(diff) <= 1e-9), ("worse", diff < -1e-9)):
                rows.append({**base, "stat": f"share_{k}", "value": float(v.mean()) if n else float("nan")})
            if m <= 3:
                ax, ay = x[ok] > 0, y[ok] > 0
                for k, v in (("plan_not_ts", ax & ~ay), ("both", ax & ay), ("neither", ~ax & ~ay),
                             ("ts_not_plan", ~ax & ay)):
                    rows.append({**base, "measure": f"ahead_month_{m}", "stat": f"share_{k}",
                                 "value": float(v.mean()) if n else float("nan")})
            r = FU.paired_reading(diff, h)
            rows.append({**base, "stat": "mean", "value": r["mean"], "note": r["note"]})
            rows.append({**base, "stat": "n_w", "value": float(r["n_w"])})
            rows.append({**base, "stat": "n_eff", "value": float(r["n_eff"])})
            for k in ("above", "equal", "below"):
                rows.append({**base, "stat": f"windows_{k}", "value": float(r["signs"][k])})
            if r["interval"] is not None:
                rows.append({**base, "stat": "interval_lo", "value": float(r["interval"][0])})
                rows.append({**base, "stat": "interval_hi", "value": float(r["interval"][1])})
                rows.append({**base, "stat": "mdd", "value": float(r["mdd"])})
                if coverage:
                    cov = coverage_of(h, int(r["n_w"]))
                    rows.append({**base, "stat": "coverage", "value": cov, "note": FU.coverage_label(cov)})
    return rows


def paired_scorecard_rows(plan: list[dict[str, Any]], ts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The card (P, S1 ... S5c) on the plan's starts paired with TS's (`u_select.scorecard(paired_with=)`), and TS's
    on the same starts, by block."""
    from propedge.research import u_select as S

    out = []
    for b in BLOCKS:
        which = None if b == "all" else b
        mine = S.scorecard(plan, which, paired_with=ts)
        theirs = S.scorecard(ts, which, paired_with=plan)
        for k in mine:
            out.append({"section": "paired_card", "block": b, "measure": k, "stat": "plan", "value": mine[k]["value"],
                        "n": mine[k]["n"]})
            out.append({"section": "paired_card", "block": b, "measure": k, "stat": "ts", "value": theirs[k]["value"],
                        "n": theirs[k]["n"]})
    return out


# ------------------------------------------------------------------------------------------------ 9.3


def tier1_count_rows(stream: str, blocks: Sequence[Any], dates: Sequence[Any]) -> list[dict[str, Any]]:
    """G-3's count (9.3's first line): the offered trades open at a window's start at any offered R, and the entries
    inside a window, by release and year."""
    from datetime import date as _d

    days, spec = C.tier1_days(), C.window_spec()
    tab: dict[tuple[str, int, str], int] = {}
    for b, dd in zip(blocks, dates):
        d = dd if isinstance(dd, _d) else _d.fromisoformat(str(dd)[:10])
        kinds = days.get(d)
        if not kinds or b.r_by_rr is None or b.exit_by_rr is None or b.entry_t is None:
            continue
        for kind in kinds:
            w = C.windows_of([kind])[0]
            for j in range(len(b.pnl)):
                ex = {float(k): float(v[j]) for k, v in b.exit_by_rr.items() if np.isfinite(float(b.r_by_rr[k][j]))}
                if C.entry_inside(float(b.entry_t[j]), w):
                    tab[(kind, d.year, "entries_inside")] = tab.get((kind, d.year, "entries_inside"), 0) + 1
                elif C.open_at(float(b.entry_t[j]), ex, spec[w][0]):
                    tab[(kind, d.year, "open_at_start")] = tab.get((kind, d.year, "open_at_start"), 0) + 1
    return [{"section": "tier1_count", "stream": stream, "release": k, "year": y, "measure": what, "value": float(v)}
            for (k, y, what), v in sorted(tab.items())]


def p16_count_nonzero(rows: Sequence[dict[str, Any]]) -> bool:
    """5.5: the four conditional runs are added when P-16's count of trades open at a window's start is not zero."""
    return any(r["stream"] == "p16" and r["measure"] == "open_at_start" and r["value"] > 0 for r in rows)


def ledger_rows(cell: dict[str, Any], s: T.Settings, ts_cell: dict[str, Any] | None) -> list[dict[str, Any]]:
    """9.3's ledger counts on each start's long replay: the trades and their fees against the plan's schedule (9.2),
    exits after 15:10 CT, trades on an early-close session, martingale steps (DT), trades a session (FP, QP), and the
    share of trades whose contracts differ from TS's, by account kind."""
    out: dict[str, float] = {"trades": 0, "fee_off_schedule": 0, "exits_after_flat": 0, "early_close_trades": 0,
                             "martingale_per_account": 0, "martingale_firm_wide": 0, "max_trades_session_account": 0,
                             "max_trades_session_across": 0, "sessions_above_trade_line": 0,
                             "contracts_compared": 0, "contracts_differ": 0}
    ts_led = {} if ts_cell is None else {d["start"]: d["ledger"] for d in ts_cell["directs"]}
    sched = None if s.plan in ("TS",) else T.fee_schedule(s.plan, s.fee_basis) if s.plan != "LU" else None
    for d in cell["directs"]:
        led = [r for r in d["ledger"] if r.get("contracts")]
        out["trades"] += len(led)
        for r in led:
            if sched is not None and "fee" in r:
                n = int(r["contracts"])
                want = (n // 10) * sched[1] + (n - (n // 10) * 10) * sched[0]
                out["fee_off_schedule"] += int(abs(float(r["fee"]) - want) > 1e-9)
        trades = [{"account": (r["kind"], r["index"]), "day": int(r["day"]), "entry": float(r["trade_index"]),
                   "contracts": int(r["contracts"]), "pnl": float(r["pnl"])} for r in led]
        if s.plan == "DT":
            mg = C.martingale_steps(trades)
            out["martingale_per_account"] += mg["per_account"]
            out["martingale_firm_wide"] += mg["firm_wide"]
        if s.plan in ("FP", "QP"):
            ta = C.trades_a_session(trades)
            out["max_trades_session_account"] = max(out["max_trades_session_account"], ta["max_per_account"])
            out["max_trades_session_across"] = max(out["max_trades_session_across"], ta["max_across"])
            out["sessions_above_trade_line"] += ta["sessions_above_line"]
        if d["start"] in ts_led:
            mine = {(r["historical_day"], r["trade_index"], r["kind"]): int(r["contracts"]) for r in led}
            theirs = {(r["historical_day"], r["trade_index"], r["kind"]): int(r["contracts"])
                      for r in ts_led[d["start"]] if r.get("contracts")}
            both = set(mine) & set(theirs)
            out["contracts_compared"] += len(both)
            out["contracts_differ"] += sum(mine[k] != theirs[k] for k in both)
    return [{"section": "counts", "measure": k, "value": float(v)} for k, v in out.items()]


def exit_problems(blocks: Sequence[Any], dates: Sequence[Any]) -> dict[str, int]:
    """9.3's must-be-zero checks on the offered trades: any exit after 15:10 CT at any offered R; any trade on an
    early-close session (E-029's calendar)."""
    from extended import calendar_early_closes as E

    if C._lf_sha256(E.CALENDAR_CSV) != C.EARLY_CLOSES_SHA256:
        raise ValueError("config/calendar_early_closes.csv is not the text's pinned calendar (E-029)")
    early = {r["date"] for r in E.read_calendar() if r["close_ct"] and r["close_ct"] < "15:20"}
    late = sum(int(np.nansum(np.where(np.isfinite(np.asarray(v, float)), np.asarray(v, float) > W.C_FLAT, False)))
               for b in blocks if b.exit_by_rr is not None for v in b.exit_by_rr.values())
    on_early = sum(len(b.pnl) for b, d in zip(blocks, dates) if str(d)[:10] in early)
    return {"exits_after_flat": int(late), "trades_on_early_close": int(on_early)}


def account_count_rows(cell: dict[str, Any]) -> list[dict[str, Any]]:
    """9.3's adapter counts (each account's counters, `firm_accounts.collect`), summed over the cell's long replays,
    by account class family."""
    tot: dict[str, float] = {}
    for per in cell["counts"]:
        for g in per:
            for k, v in g.items():
                if k in ("class", "kind", "index", "day") or not isinstance(v, (int, float)):
                    continue
                key = f"{g['kind']}.{k}"
                tot[key] = tot.get(key, 0.0) + float(v)
    return [{"section": "counts", "measure": k, "value": v} for k, v in sorted(tot.items())]


def differs_rows(cell: dict[str, Any], ts_cell: dict[str, Any]) -> list[dict[str, Any]]:
    """9.3: the share of starts on which the plan differs from TS at all within 63, 126 and 252 sessions (the long
    replays' daily cash)."""
    ts = {d["start"]: np.asarray(d["long"].path.cash_series, float) for d in ts_cell["directs"]}
    out = []
    for h in (63, 126, 252):
        flags = []
        for d in cell["directs"]:
            if d["start"] not in ts:
                continue
            a, b = np.asarray(d["long"].path.cash_series, float), ts[d["start"]]
            if len(a) <= h or len(b) <= h:
                continue
            flags.append(bool(np.any(np.abs(a[:h + 1] - b[:h + 1]) > 1e-9)))
        out.append({"section": "counts", "measure": f"share_starts_differing_by_{h}",
                    "value": float(np.mean(flags)) if flags else float("nan"), "n": len(flags)})
    return out


# ------------------------------------------------------------------------------------------------ A-10's grid


def grid_prices(s: T.Settings) -> list[float]:
    """10.1 item 9: U-2's grid and every listed price (DT, FP, QP); Lucid's struck list price beside its own."""
    if s.plan == "LU":
        return [T.lucid_list_price()]
    listed = {"FP": T.declared("FP.price.listed"), "QP": T.declared("QP.price.listed")}.get(s.plan, ())
    return sorted(set(T.DT_PRICE_GRID) | {float(p) for p in listed})


def _card(recs: list[dict[str, Any]], which: str | None) -> dict[str, float]:
    from propedge.research import u_select as S

    return {k: float(v["value"]) for k, v in S.scorecard(recs, which).items()}


def grid_rows(cell: dict[str, Any], design: str, arm: str, resp: Any, s: T.Settings,
              ts_recs: list[dict[str, Any]] | None) -> tuple[list[dict[str, Any]], dict[float, list[dict]]]:
    """Every money measure and P at each price, by A-10's arithmetic on every run of every start; and the break-even
    price against TS for P, S5a and the mean month-3 net (`firms.break_even_price`, $0 to $250). Returns (rows, the
    records at each price)."""
    pro = (float(T.plan_terms("DT").funded_recurring_fee), int(T.stage2_value("billing_days"))) if s.plan == "DT" \
        else (0.0, None)
    run_price = float(cell["directs"][0]["sub"]) if cell["directs"] else float("nan")

    def recs_at(p: float) -> list[dict[str, Any]]:
        return [priced_output(design, arm, resp, d, run_price, p, pro[0], pro[1])["rec"] for d in cell["directs"]]

    rows, at = [], {}
    for p in [run_price] + [q for q in grid_prices(s) if q != run_price]:
        recs = recs_at(p)
        at[p] = recs
        for b in BLOCKS:
            card = _card(recs, None if b == "all" else b)
            for k, v in card.items():
                rows.append({"section": "price_grid", "block": b, "price": p, "measure": k, "value": v})
            m3 = [_net(r, 3) for r in recs if int(r["observed"]) >= 63]
            rows.append({"section": "price_grid", "block": b, "price": p, "measure": "mean_net_month_3",
                         "value": float(np.nanmean(m3)) if m3 else float("nan")})
    if ts_recs is not None and s.plan != "LU":
        ts_card = _card(ts_recs, None)
        ts_m3 = float(np.nanmean([_net(r, 3) for r in ts_recs if int(r["observed"]) >= 63]))
        for key, target in (("P", ts_card.get("P")), ("S5a", ts_card.get("S5a")), ("mean_net_month_3", ts_m3)):
            if target is None or not np.isfinite(target):
                continue

            def measure(p: float, key=key) -> float:
                recs = recs_at(p)
                if key == "mean_net_month_3":
                    return float(np.nanmean([_net(r, 3) for r in recs if int(r["observed"]) >= 63]))
                return _card(recs, None)[key]

            be = F.break_even_price(measure, float(target), 0.0, float(T.DT_PRICE_GRID[-1]), tol=0.01)
            rows.append({"section": "break_even", "block": "all", "price": float("nan") if be is None else be,
                         "measure": key, "value": float(target), "note": "none in range" if be is None else ""})
    return rows, at


def grid_problems(at: dict[float, list[dict]], other: dict[str, Any] | None, other_price: float, tol: float = 1e-6
                  ) -> list[str]:
    """10.1 item 9's refusing check: the arithmetic at the bracket's other end equals that price's own run on every
    start, every money field and the event days, to 1e-6."""
    if other is None or other_price not in at:
        return []
    mine = {int(r["start_day"]): r for r in at[other_price]}
    probs = []
    for o in other["outs"]:
        r = o["rec"]
        m = mine.get(int(r["start_day"]))
        if m is None:
            probs.append(f"start {r['start_day']}: no repriced record")
            continue
        for k in ("net_month", "fees_month", "pay_days", "pay_cash", "pass_days", "funded_days"):
            a, b = m.get(k), r.get(k)
            a = [np.nan if v is None else float(v) for v in (a or [])]
            b = [np.nan if v is None else float(v) for v in (b or [])]
            if len(a) != len(b) or any(not (np.isnan(x) and np.isnan(y)) and abs(x - y) > tol for x, y in zip(a, b)):
                probs.append(f"start {r['start_day']}: {k} at ${other_price:g} is not the price run's")
                break
    return probs


# ------------------------------------------------------------------------------------------------ the gate beside


def gate_rows(blocks: Sequence[Any], kw: dict[str, Any], s: T.Settings, run_gate: Callable, *, workers: int = 1,
              hook_factory: Callable[[str], tuple[Any, list]] | None = None
              ) -> tuple[list[dict[str, Any]], dict[str, list], list[str]]:
    """10.1 item 8 for one corner: the gate's rows at the plan's arguments (A-1 on the gate, A-8's seams; the placement
    off), point and bound, and its zero-edge twin -- the bound arm with every bound at 0 (every R's outcomes shifted to a
    zero mean). One call each, at every plan: Quick Pay's class holds the gate's point blocks and classifies on them on
    both arms (M3), which settles E-089's route. Labelled: A-11 off; DayTraders' inactivity on 21 sessions; its
    recurring fee left out. `kw`: the registered call's keywords (its `e`, `lb`, `e_by_rr`, `lb_by_rr` among them);
    `hook_factory(label)`: each call's own path hook and the list it fills. Returns (rows, sinks by call, labels)."""
    g = F.gate_args(kw, s, point_blocks=blocks if s.plan == "QP" else None)
    e, lb = float(g["e"]), float(g["lb"])
    e_by_rr, lb_by_rr = dict(g["e_by_rr"]), dict(g["lb_by_rr"])
    g = {k: v for k, v in g.items() if k not in ("e", "lb", "e_by_rr", "lb_by_rr", "path_hook")}
    if s.plan != "TS" and g.get("rtp", True) is not False:
        raise ValueError("RD-01's gate beside runs with the placement off (rtp=False) at every plan but TS")
    sinks: dict[str, list] = {}
    labels = []
    if s.plan in ("FP", "QP"):
        labels.append("tier-1 liquidation not applied")
    if s.plan == "DT":
        labels += ["inactivity on 21 sessions, not 30 calendar days", "recurring Pro fee left out: an upper bound"]
    zero = {k: 0.0 for k in lb_by_rr}

    def call(label: str, lb_s: float, lb_by: dict[float, float], keep: tuple[str, ...]) -> list[dict[str, Any]]:
        k = dict(g)
        if hook_factory is not None:
            k["path_hook"], sinks[label] = hook_factory(label)
        rows, _passed = run_gate(blocks, e=e, lb=lb_s, e_by_rr=e_by_rr, lb_by_rr=lb_by, workers=workers, **k)
        return [{**r, "reading": label} for r in rows.to_dict("records") if r.get("shift") in keep]

    out = call("plan", lb, lb_by_rr, ("point", "lower_bound")) + call("zero_edge", 0.0, zero, ("lower_bound",))
    return [{**r, "section": "gate", "labels": "; ".join(labels)} for r in out], sinks, labels


__all__ = ["DECLARATION", "PURPOSES", "BLOCKS", "LADDER", "stream_of", "arm_inputs", "cell_job", "compose",
           "direct_start", "priced_output", "run_cell", "reading_outs", "paired_rows", "paired_scorecard_rows",
           "tier1_count_rows", "p16_count_nonzero", "ledger_rows", "exit_problems", "account_count_rows",
           "differs_rows", "grid_prices", "grid_rows", "grid_problems", "gate_rows", "coverage_of", "compact",
           "trade_problems", "class_problems"]


def compact(cell: dict[str, Any]) -> dict[str, Any]:
    """What a TS cell keeps for the pairing (9.3's differs and contracts): each start's long cash series and ledger."""
    from types import SimpleNamespace

    return {"directs": [{"start": d["start"], "ledger": d["ledger"],
                         "long": SimpleNamespace(path=SimpleNamespace(cash_series=np.asarray(d["long"].path.cash_series,
                                                                                             float)))}
                        for d in cell["directs"]]}
