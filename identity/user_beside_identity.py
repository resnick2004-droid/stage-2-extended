"""Q-17's identities (`extended/user_beside.py`, the user's replay under the firm's responses), refusing.

    python identity/user_beside_identity.py --synthetic                 # light: the adapter's mechanics on synthetic
                                                                        #   binary-draw campaigns (no bars)
    python identity/user_beside_identity.py --u1-starts 4               # slow: U1's start rows for P-14 and P-16 at 4
                                                                        #   starts a configuration and arm
    python identity/user_beside_identity.py --u1-starts all --configs p14,p15,p16 --workers 1   # heavy (the run lock)

**`--u1-starts` (the brief's item 3).** With every response off (`off`: 0 % denial, the placement off, no Focused
Trader model) the adapter's replay -- its own path seed per start, `extended.user_beside.replay` -- reproduces
`vendor/stage2/results/user_journey.csv`'s section `start` for each configuration and arm, **every column of the file**,
by the comparison E-010's identity uses (`identity/stage2_identity.py`'s `u1_compare`: money and the ratio to 1e-6,
counts and days exactly, dates and text exactly), on N starts spread as `user_journey.py --check --starts N` spreads
them, or on every start (then the file's starts must all be reproduced); beside it the study's own refusing checks on
the same runs (D-620's declaration, the builders' identity rows, every run's payouts and fees against the engine's
totals).

**`--synthetic` (light).** The mechanics the identity cannot see, on campaigns of stage one's binary draws through the
vendored `simulate_lockstep_path` (five seats, a declared draw seed, Stage 2's verified rules ledger):
(1) at 0 % with the placement off the path seed changes nothing (it feeds only the enforcement stream);
(2) at 50 % denial the path seed decides which payouts are denied (two seeds differ somewhere);
(3) forfeiture, at 10, 25 and 50 %: on every path whose coin denies a payout, the forfeiture close is the denial
arm's first denial close at the same level and seed, the two paths' closes before it are equal, nothing is bought after it, every account has ended by
it, the view's cash is constant from it on, no payout arrives after it, the view passes U1's own checks (arrival days
equal the campaign's pay days, their cash the total payouts, the fees derived from the cash the engine's total), and
some payout is forfeited on some path; on a path with no denial (short paths at 10 %) the forfeiture arm is the
off arm close for close and the view leaves it unchanged;
(4) the placement (RTP) and a Focused Trader model reach the engine (a placement recorded, the path changed);
(5) the adapter refuses arguments that are not the vendored 0 %, placement-off call, and a flip stream;
(6) the binding Focused Trader models are the vendored grid's under the budget (D-512 (4)); the start seeds are
distinct over 3,000 starts.

`--control <response>` (a negative control, E-010's kind): the same comparison with that response on must be refused
-- the identity can tell a response on from off.

**The read (Q-48).** With `--u1-starts` (and `--control`), before anything runs, `main` authorises Stage 2's engine's
read through `extended.reader.authorise_engine_read` (purpose `identity`, declaration **E-024**, the window 2020-01-02
to 2026-07-16; the files: A1's events and days and A3's cached walk for every configuration, the bars for P-15's and
P-16's walks); a refusal ends the run (exit 3) before anything is read. Ledgered only inside a clean run (E-026).
`--synthetic` reads no bar or walk and authorises nothing.

Exit 0 when every part run holds; 3 when one is refused. Nothing is written (inside a clean run, the read's ledger
line). Peak memory printed last.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

import stage2_identity as SI  # noqa: E402  (identity/stage2_identity.py: u1_compare, the file's name, peak memory)

from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402

#: the Stage 2 tree the engine reads (its data checked and named for the read's authorisation, Q-48)
VENDOR = ROOT / "vendor" / "stage2"
#: the decision row that registered this identity (Q-17's, merged under E-024)
READ_ROW = "E-024"
U1_CONFIGS = ("p14", "p16")
#: the synthetic campaigns' declared draw seed and the path seeds tried (the brief's block)
SYN_DRAW_SEED = B.SEED_BLOCK[1]
SYN_PATH_SEEDS = tuple(range(B.SEED_BLOCK[2], B.SEED_BLOCK[2] + 6))
SYN_HORIZON = 253
#: the short paths of (3b): about two months, where some paths see no denial at 10 %
SYN_SHORT = 43


# ------------------------------------------------------------------------------------------------ synthetic


def _syn_args(edge: float = 0.10):
    from propedge.campaign.lockstep import ConductModel, binary_draw_factories
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.campaign.protocols import Protocol
    from propedge.contract.adapter import rules_from_ledger
    from propedge.contract.rules import load_rules

    rules = rules_from_ledger()
    proto = Protocol(name="q17_synthetic", combine_rr=2.0, combine_risk=1000.0, funded_rr=2.0, funded_risk=1000.0,
                     trades_per_day=1, max_concurrent_accounts=5)
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)

    def path_args():
        c, f = binary_draw_factories(proto, edge, SYN_DRAW_SEED, rules)
        return dict(edge=edge, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                    subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                    activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                    max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                    funded_horizon_days=100_000, combine_draw_factory=c, funded_draw_factory=f)

    return proto, path_args, lag


def _syn_run(proto, path_args, resp, seed: int, horizon: int = SYN_HORIZON):
    from propedge.campaign.lockstep import simulate_lockstep_path

    a = B.response_args({"path": path_args(), "draws": {"flip": None}, "seed": SYN_DRAW_SEED}, resp)
    return simulate_lockstep_path(proto, seed=int(seed), horizon_days=int(horizon), **a["path"])


def _arrivals(lp, lag: int, obs: int):
    from propedge.research import user_journey as U

    return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)


def _u1_checks(lp, lag: int) -> list[str]:
    """U1's own checks of a run (`user_journey._one_start`'s `record`)."""
    import customer_journey as CJ

    from propedge.research import user_journey as U

    cash, init, _, _, pays = CJ.single_events(lp)
    obs = len(cash) - 1
    arr = _arrivals(lp, lag, obs)
    got = float(sum(c for _, c in arr))
    out = []
    if sorted(d for d, _ in arr) != sorted(int(d) for d in pays):
        out.append("arrival days are not the campaign's pay days")
    if abs(got - float(lp.path.total_payouts)) > U.TOL:
        out.append("arrivals' cash is not the total payouts")
    if abs(U.fees_paid(float(cash[-1]) - float(init), got) - float(lp.path.total_fees)) > U.TOL:
        out.append("the fees derived from the cash are not the engine's total")
    return out


def synthetic_problems() -> tuple[list[str], dict[str, Any]]:
    from propedge.campaign.lockstep import ConductModel, child_seed

    proto, path_args, lag = _syn_args()
    off, d50 = B.BY_NAME["off"], B.BY_NAME["denial_50"]
    probs: list[str] = []
    seen = {"forfeited_paths": 0, "payouts_forfeited": 0, "no_denial_paths": 0, "denied": []}

    # (1) the path seed feeds only the enforcement stream
    a, b = (_syn_run(proto, path_args, off, s) for s in SYN_PATH_SEEDS[:2])
    if not np.array_equal(a.path.cash_series, b.path.cash_series) or a.funded != b.funded:
        probs.append("(1) at 0 % with the placement off two path seeds give different paths")
    # (2) the path seed decides the denials
    denials = [_syn_run(proto, path_args, d50, s) for s in SYN_PATH_SEEDS]
    seen["denied"] = [int(x.conduct["payouts_denied"]) for x in denials]
    if not any(x > 0 for x in seen["denied"]):
        probs.append("(2) no payout denied at 50 % on any synthetic path (the campaign shows no exposure)")
    if len({tuple(np.round(x.path.cash_series, 6)) for x in denials}) < 2:
        probs.append("(2) at 50 % every path seed gives the same path: the seed does not reach the denial draws")
    # (3) forfeiture, at every level of the ladder against the denial arm at the same level and seed (at 50 % the
    # forfeiture comes at a start's first or second payout, before any other is in flight; at 10 % later, with some)
    off_runs = {s: _syn_run(proto, path_args, off, s) for s in SYN_PATH_SEEDS}
    pairs = []
    for p in B.DENIAL_LEVELS:
        dn, fn = B.BY_NAME[f"denial_{round(100 * p)}"], B.BY_NAME[f"forfeit_{round(100 * p)}"]
        for s in SYN_PATH_SEEDS:
            pairs.append((f"{fn.name} seed {s}", s, dn, fn,
                          next(x for x, t in zip(denials, SYN_PATH_SEEDS) if t == s) if dn is d50 else None))
    for what, s, dn, fn, den in pairs:
        den = den if den is not None else _syn_run(proto, path_args, dn, s)
        raw = _syn_run(proto, path_args, fn, s)
        view, info = B.forfeit_view(raw, lag)
        d = int(raw.household.get("closed_on", -1))
        first = B.response_record(den, dn)["first_denial_day"]
        if d < 0:
            seen["no_denial_paths"] += 1
            if int(den.conduct["payouts_denied"]) != 0:
                probs.append(f"(3) {what}: the denial arm denies a payout, the forfeiture arm forfeits nothing")
            if not np.array_equal(raw.path.cash_series, off_runs[s].path.cash_series):
                probs.append(f"(3) {what}: without a denial the forfeiture arm is not the off arm")
            continue
        seen["forfeited_paths"] += 1
        seen["payouts_forfeited"] += int(info["payouts_forfeited"])
        if not (np.isfinite(first) and int(first) == d):
            probs.append(f"(3) {what}: the forfeiture close {d} is not the denial arm's first denial close {first}")
        if not np.array_equal(raw.path.cash_series[:d], den.path.cash_series[:d]):
            probs.append(f"(3) {what}: the closes before the forfeiture differ from the denial arm's")
        if any(c.purchase_day > d for c in raw.combines):
            probs.append(f"(3) {what}: a Combine bought after the forfeiture close")
        if any(c.resolved_on is None or int(c.resolved_on) > d for c in raw.combines):
            probs.append(f"(3) {what}: a Combine still live after the forfeiture close")
        if any(f.ended_on is None or int(f.ended_on) > d for f in raw.funded):
            probs.append(f"(3) {what}: a funded account still live after the forfeiture close")
        cash = np.asarray(view.path.cash_series, float)
        if not np.all(cash[d:] == cash[d]):
            probs.append(f"(3) {what}: the view's cash moves after the forfeiture close")
        obs = len(cash) - 1
        if any(day > d for day, _ in _arrivals(view, lag, obs)):
            probs.append(f"(3) {what}: a payout arrives after the forfeiture close")
        probs += [f"(3) {what}: the view: {p}" for p in _u1_checks(view, lag)]
        probs += [f"(3) {what}: the raw run: {p}" for p in _u1_checks(raw, lag)]
    # (3b) a path the coin never denies: the forfeiture arm is the off arm, close for close (short paths at 10 %)
    for s in SYN_PATH_SEEDS:
        raw = _syn_run(proto, path_args, B.BY_NAME["forfeit_10"], s, SYN_SHORT)
        if int(raw.household.get("closed_on", -1)) >= 0:
            continue
        seen["no_denial_paths"] += 1
        o = _syn_run(proto, path_args, off, s, SYN_SHORT)
        if not np.array_equal(raw.path.cash_series, o.path.cash_series) or len(raw.funded) != len(o.funded) or any(
                (x.payout_days, x.payout_cash) != (y.payout_days, y.payout_cash) for x, y in zip(raw.funded, o.funded)):
            probs.append(f"(3b) seed {s}: without a denial the forfeiture arm is not the off arm")
        if B.forfeit_view(raw, lag)[0] is not raw:
            probs.append(f"(3b) seed {s}: without a denial the view changes the path")
    if not seen["no_denial_paths"]:
        probs.append("(3b) every short path forfeits: the no-denial case is not exercised")
    if not seen["forfeited_paths"]:
        probs.append("(3) no synthetic path forfeits: the forfeiture is not exercised")
    if not seen["payouts_forfeited"]:
        probs.append("(3) no pending payout was forfeited on any path: the arrivals' removal is not exercised")
    # (4) RTP and FTP reach the engine
    rtp = [_syn_run(proto, path_args, B.BY_NAME["rtp"], s) for s in SYN_PATH_SEEDS[:3]]
    if not any(int(x.conduct.get("rtp_placed_day", -1)) >= 0 for x in rtp):
        probs.append("(4) the placement is never recorded")
    if all(np.array_equal(x.path.cash_series, off_runs[s].path.cash_series) for x, s in zip(rtp, SYN_PATH_SEEDS)):
        probs.append("(4) the placement changes no path")
    for name in ("ftp_slowdown_purchases_10", "ftp_corrective_lost_3"):
        x = _syn_run(proto, path_args, B.BY_NAME[name], SYN_PATH_SEEDS[0])
        ftp = dict(x.focused_trader or {})
        if not ftp or ftp.get("first_placed_day", -1) < 0:
            probs.append(f"(4) {name}: no placement recorded")
        if np.array_equal(x.path.cash_series, off_runs[SYN_PATH_SEEDS[0]].path.cash_series):
            probs.append(f"(4) {name}: the model changes no path")
        rec = B.response_record(x, B.BY_NAME[name])
        if not np.isfinite(rec["response_day"]):
            probs.append(f"(4) {name}: the response record has no placement day")
    # (5) refusals
    base = {"path": path_args(), "draws": {"flip": None}, "seed": SYN_DRAW_SEED}
    for what, args in (("conduct on", {**base, "path": {**base["path"], "conduct": ConductModel(rtp=True)}}),
                       ("a model given", {**base, "path": {**base["path"], "focused_trader": object()}}),
                       ("a flip stream", {**base, "draws": {"flip": object()}})):
        try:
            B.response_args(args, off)
            probs.append(f"(5) the adapter accepts arguments with {what}")
        except ValueError:
            pass
    # (6) the grid and the seeds
    if tuple(B.binding_ftp(B.FTP_BUDGET)) != B.FTP_BINDING:
        probs.append(f"(6) the vendored grid's binding models are {B.binding_ftp(B.FTP_BUDGET)}, not {B.FTP_BINDING}")
    seeds = [B.start_seed(s) for s in range(3000)]
    if len(set(seeds)) != len(seeds) or seeds[7] != child_seed(B.DENIAL_SEED, B.START_KIND, 7):
        probs.append("(6) the start seeds collide or are not child_seed(DENIAL_SEED, 0, start)")
    return probs, seen


# ------------------------------------------------------------------------------------------------ U1


def u1_reference(rd: Path, configs: Sequence[str]) -> dict[str, Any]:
    """U1's file (its manifest verified first): its columns, the recorded starts, and the configurations' start rows."""
    import gc

    import user_journey as UJ

    from propedge.reporting.results import read_manifest, read_result
    from propedge.research import user_journey as U

    decl = U.declaration()
    bad = U.declaration_problems(decl)
    if bad:
        raise SystemExit("REFUSED: the vendored build is not D-620's declaration -- " + "; ".join(bad[:4]))
    path = rd / SI.U1_FILE
    man = read_manifest(path)
    ref = read_result(path)
    arms = tuple(man.parameters["arms"])
    if set(arms) != set(UJ.ARMS) or len(arms) != len(UJ.ARMS):
        raise SystemExit(f"REFUSED: the file's arms {arms} are not the study's {UJ.ARMS}")
    columns = list(man.columns)
    if list(ref.columns) != columns:
        raise SystemExit("REFUSED: the file's columns are not its manifest's")
    st = ref[(ref["section"] == "start") & ref["config"].isin(list(configs))].copy()
    del ref
    gc.collect()
    return {"columns": columns, "recorded": man.parameters["starts"], "start": st}


def build_p15(rd: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """P-15 as `user_journey.build_p15` builds it -- `rc_dev_test.build_cells`, `_rc_campaign`, `_single_jobs` at the
    plan and budget -- with its trades' check reduced to the pinned content hash (`rc_dev_test.P15.trades_sha256`):
    the check's first step reads P-15's screen file (`results/rc_reentry_screen.csv`), which is not in the vendored
    snapshot. The off arm's start rows against U1's file, every start and column, stand beside it."""
    import a3_brk30_cb20 as C
    import rc_dev_test as D
    import user_journey as UJ

    I, b = D.build_cells()
    t = b["cells"][D.P15.cell]["trades"]
    th = D.trades_hash(t)
    bad = [] if th == D.P15.trades_sha256 else [f"P-15's trades' content hash {th[:12]} is not the pinned "
                                                f"{D.P15.trades_sha256[:12]}"]
    ident = {"check": f"the trades' content hash is P-15's registered {D.P15.trades_sha256} (the screen row's check "
                      f"needs results/{D.P15.screen_file}, not vendored)", "holds": not bad, "refuses": True,
             "problems": "; ".join(bad)}
    return {"p15": UJ._single_jobs(UJ._rc_campaign(I, b, D.P15.cell, D.P15), I["plan"], C.BUDGET)}, [ident]


def build(rd: Path, name: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    """A configuration's two arms' jobs by U1's own builder (`user_journey.BUILDERS`; P-15's by `build_p15`), its
    definition, and the builder's refusing identity rows' failures."""
    import user_journey as UJ

    defs = {c["config"]: c for c in UJ.CONFIG_DEFS}
    c = defs[name]
    jobs, idents = build_p15(rd) if name == "p15" else UJ.BUILDERS[c["group"]](rd, [name])
    probs = [f"{name}: the study's identity fails: {r['check'][:120]} -- {r['problems']}" for r in idents
             if not r["holds"] and r["refuses"]]
    for arm in UJ.ARMS:
        probs += [f"{name} {arm}: {p}" for p in B.base_problems(jobs[name][arm]["args"])]
    return jobs[name], c, probs


def u1_compare_outs(name: str, c: dict[str, Any], arm: str, outs: list[dict[str, Any]], ref: dict[str, Any],
                    n_window: int, starts: int | None) -> list[str]:
    """The off arm's start rows against U1's file for one configuration and arm (E-010's comparison)."""
    import user_journey as UJ

    from propedge.research import user_journey as U

    probs = []
    want = int(ref["recorded"][f"{name}|{arm}"])
    if n_window != want:
        probs.append(f"{name} {arm}: the window holds {n_window} starts, the file's manifest records {want}")
    if starts is not None and [x["rec"]["start_day"] for x in outs] != UJ.start_choice(n_window, starts):
        probs.append(f"{name} {arm}: the starts run are not user_journey.start_choice's")
    for k in ("pay", "cash", "fee"):
        n = int(sum(x[f"{k}_bad"] for x in outs))
        if n:
            probs.append(f"{name} {arm}: {n} runs' {k} check against the engine's totals fails")
    mine = [{**r, "reading": U.READING} for r in UJ.start_rows(c, arm, outs)]
    st = ref["start"]
    theirs = st[(st["config"] == name) & (st["arm"] == arm)].to_dict("records")
    if len(theirs) != want:
        probs.append(f"{name} {arm}: the file holds {len(theirs)} start rows, its manifest records {want}")
    probs += SI.u1_compare(mine, theirs, ref["columns"], f"{name} {arm}", all_starts=starts is None)
    return probs


def u1_problems(configs: Sequence[str], starts: int | None, workers: int, response: str = "off"
                ) -> dict[str, dict[str, Any]]:
    import gc

    import user_journey as UJ

    from propedge import RESULTS_DIR

    rd = RESULTS_DIR
    ref = u1_reference(rd, configs)
    out: dict[str, dict[str, Any]] = {}
    for name in configs:
        t0 = time.time()
        print(f"Q-17 identity {name}: the inputs (user_journey.BUILDERS)...", flush=True)
        jobs, c, probs = build(rd, name)
        ran = of = 0
        for arm in UJ.ARMS:
            job = jobs[arm]
            of = len(job["blocks"])
            chosen = UJ.start_choice(of, starts)
            outs = B.run_starts(name, arm, B.BY_NAME[response], job, chosen, workers)
            ran = len(outs)
            probs += u1_compare_outs(name, c, arm, outs, ref, of, starts)
        del jobs
        gc.collect()
        out[name] = {"problems": probs, "starts": ran, "of": of, "seconds": time.time() - t0,
                     "columns": len(ref["columns"])}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--u1-starts", default=None, help="N starts a configuration and arm, or 'all'")
    ap.add_argument("--configs", default=",".join(U1_CONFIGS))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--control", default=None, help="a negative control: the same comparison with this response on "
                    "must be REFUSED (exit 0 when it is)")
    a = ap.parse_args(argv)
    if not a.synthetic and a.u1_starts is None:
        ap.error("give --synthetic and/or --u1-starts")
    configs = tuple(x for x in a.configs.split(",") if x)
    if a.u1_starts is not None:
        root = VENDOR / "data"
        if not ((root / "bars").is_dir() and (root / "atlas").is_dir()):
            print("REFUSED: no bars or atlas (scripts/vendor_stage2.py --data)")
            return 3
        files = SI.engine_files(VENDOR, bars=any(c in SI.U1_WALKED for c in configs))
        what = (f"{READ_ROW}'s identity (identity/user_beside_identity.py): U1's start rows for {', '.join(configs)} "
                f"({a.u1_starts} starts) through the adapter, "
                + ("every response off" if a.control is None else f"the negative control {a.control}"))
        try:                                        # Q-48: the engine's read authorised (ledgered in a clean run only)
            reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                         declaration=READ_ROW, files=files, what=what)
        except (reader.ReadRefused, FileNotFoundError) as exc:
            print(SI.refusal(exc), flush=True)
            return 3
    rc = 0
    if a.synthetic:
        t0 = time.time()
        probs, seen = synthetic_problems()
        if probs:
            rc = 3
            print("REFUSED: the synthetic identity FAILS -- " + "; ".join(probs[:12]), flush=True)
        else:
            print(f"synthetic identity HOLDS ({len(SYN_PATH_SEEDS)} paths of {SYN_HORIZON - 1} sessions: payouts "
                  f"denied at 50 % by path {seen['denied']}, {seen['forfeited_paths']} paths forfeited, "
                  f"{seen['payouts_forfeited']} pending payouts forfeited, {seen['no_denial_paths']} paths without a "
                  f"denial; {time.time() - t0:.0f} s)", flush=True)
    if a.u1_starts is not None:
        starts = None if a.u1_starts == "all" else int(a.u1_starts)
        if a.control is not None:
            for name, r in u1_problems(configs, starts, a.workers, a.control).items():
                if r["problems"]:
                    print(f"negative control HOLDS: {a.control} on {name.upper()} is refused by the comparison "
                          f"({len(r['problems'])} differences; first: {r['problems'][0][:160]})", flush=True)
                else:
                    rc = 3
                    print(f"REFUSED: negative control: {a.control} on {name.upper()} passes the comparison -- the "
                          "identity cannot tell a response on from off", flush=True)
            mem = SI.peak_memory()
            if mem:
                print(mem, flush=True)
            return rc
        for name, r in u1_problems(configs, starts, a.workers).items():
            if r["problems"]:
                rc = 3
                print(f"REFUSED: Q-17 U1 {name.upper()} is not reproduced ({r['seconds']:.0f} s) -- "
                      + "; ".join(r["problems"][:12]), flush=True)
            else:
                print(f"identity HOLDS: Q-17 U1 {name.upper()} = results/{SI.U1_FILE}'s start rows for {name}, both "
                      f"arms, {r['starts']} of {r['of']} starts each, all {r['columns']} columns, through the adapter "
                      f"with every response off ({r['seconds']:.0f} s)", flush=True)
    mem = SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
