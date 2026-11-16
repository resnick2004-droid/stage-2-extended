"""EXPLORATORY (D-649; program U, measurement U2): the funded account's day budget on the three rows to beat -- P-14
(A3-BRK30-CB20), P-15 (`rc_s100_all`) and P-16 (`rc_s150_all`) -- after D-363's script for FV3-C
(`scripts/fv3_xfa_time_budget.py`). It runs no new design, counts no variant and selects nothing.

    python scripts/u_xfa_day_budget.py --check                 # every identity and the whole pipeline on 4 paths a
                                                               #   design and arm; identity lines, row counts and timing
                                                               #   only; written to a temporary folder, since removed
    python scripts/u_xfa_day_budget.py --workers 2             # the measurement (from a clean checkout, D-474)

**The runs (D-649 (1)).** Each design's registered gate campaign is rebuilt as its registered run built it -- the
trades (`a3_brk30.cell_trades`; `rc_dev_test.build_cells`; `rc150_dev_test.build_cells`), the era rule's 0.05 bounds
(`atlas_a3.bounds`), the blocks (`score_fv3_grid.gate_blocks`), the day capacity (`a3_brk30.capacity`) and the gate's
arguments (`atlas_a3.gate_kwargs`: FV3-C's protocol, the no-closure table, 20 purchases and resets in 21 trading days,
the strict one-at-a-time rule, five seats, the placement off, 504 days) at the registered campaign seed -- and its
first `--paths` paths (100) are run at 0 % denial on the Standard path, the bound arm (`verdict`: every R shifted to
its bound, `customer_slices.arm_blocks`) and the point arm, with the engine's EXISTING per-trade ledger and daily
account recorder on (`record_trades`, `record_days`). The engine call is `gate.run_gate`'s, one path at a time: the
path seeds are the campaign seed's (`lockstep.path_seeds`), the draws' and the path's arguments are
`customer_slices.engine_args` (D-508's, tied argument for argument to `gate.run_gate`) with the gate's own funded
horizon, and each path is `lockstep.simulate_lockstep_path` on its own `SharedDayDraws`. A path's records are read and
dropped before the next runs, so memory does not grow with `--paths`. No engine file is changed.

**Identities first, each refusing (D-649 (2)); nothing is read or written if one fails:**

* the build is D-649's row (its sha256 and the phrases the constants rest on);
* the trades are the registered run's (P-14: the screen's cell and P-13's edge rows, `a3_brk30.identity_with_screen`
  and `a3_brk30_cb20.p13_trade_problems`; P-15 and P-16: the screen's row and the registered content hash,
  `rc_dev_test.trade_problems`);
* the campaign's settings are the registered gate row's (`<design>_gate.csv`, section `gate`, 0 %: seats, table,
  strict rule, budget, routing, mode, settlement, payout timing, horizon, the placement off) and its seed the
  manifest's;
* **each re-run path's final cash, fees, payouts, funded accounts, evaluations (Combine attempts), funded accounts
  activated and trades** -- and its sized trades, attempts started, realised and intended risk, days to the first
  payout, slot-days and abandoned accounts -- **equal the registered run's per-path row** for the same path
  (`<design>_gate_paths.csv`, run `gate`, 0 %, the same arm; the first `--paths` of the registered seed's sequence),
  to 1e-6. All three registered runs wrote a per-path file, so no gate row is recomputed;
* the records agree with the engine's own counts: every account's day rows and ledger rows number its days and
  trades, its payout requests its payouts, its first request's session and balance the engine's; D-363's reader
  (`fv3_xfa_time_budget.xfa_rows`) and this script's classify every day alike; the session an account's qualifying
  days reach the Standard path's count is the engine's first eligible close; the verified rule values in the ledger
  are the ones the campaign's rules carry; no leaf name of the table carries two trade limits;
* the tables add up (`u_xfa_day_budget.table_problems`): the endings, the day classes, the opening trade's outcomes,
  the leaves and the router's outcomes each to one, the budget's groups and classes to their totals.

**The readings (D-649 (3)), per design and arm** (`propedge/research/u_xfa_day_budget.py`): D-363's sections -- the
evaluation funnel; the funded funnel and how each account ended; each funded account's days by class (no trade routed
to it, sat out by the table, a losing day, a winning day under the minimum, a qualifying winning day), overall and for
accounts paid and never paid; timing; survival and accrual by session since activation; payouts against the cap;
trades per live account-day with the router's counts beside; the table's leaves by share of funded days -- and the
additions: the opening funded trade; after it, the trading days and sessions to the fifth winning day and to the first
payout request; winning days per account-week; beside, what the Consistency test (the ledger's `xfa_cons_min_days` and
`xfa_cons_max_day_frac`; the engine's arithmetic) would have read day by day -- a description from the records, never
a run on that path, labelled in every row; and the account-days before a first payout arranged as D-649 (4) asks. What
the existing records cannot give is a row of section `missing` with its reason; no recorder is added.

Writes `results/u_xfa_day_budget.csv` (long format: design, prereg, arm, section, group, measure, value, n, basis,
note) with its manifest; EXPLORATORY. No variant is recorded: it is a measurement of registered designs (D-649, as
D-363's script recorded none). Outside `--check` only the declared run is run: three designs, 100 paths.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import u_xfa_day_budget as DB  # noqa: E402

SCRIPT = DB.SCRIPT
DECISION = DB.DECISION
ARMS = DB.ARMS
CHECK_PATHS = 4
CHUNK_PATHS = 10                            # paths a task in one process (progress lines; memory is a path's)
TOL = 1e-6
GATE_RUN = "gate"                           # the registered per-path record's label of the gate campaign
#: D-649 (2)'s figures of a path, and what else of it the per-path record carries path by path
IDENTITY_COLS = ("final_cash", "fees", "payouts", "accounts_funded", "combine_attempts", "xfas", "trades")
IDENTITY_MORE = ("trades_sized", "attempts_started", "realised_risk", "intended_capped_risk", "days_to_first_payout",
                 "combine_slot_days", "xfa_slot_days", "combines_abandoned", "xfas_abandoned")
#: the registered gate row's settings a rebuilt campaign must carry
SETTING_COLS = ("accounts", "combines", "total_accounts", "risk_policy", "one_at_a_time", "rtp", "routing",
                "cross_account_rule", "mode", "settlement", "payout_timing", "bankroll", "horizon_days", "budget_k",
                "budget_window_days")
#: the ledger's rows the readings lean on, and the campaign's rules' names for them
RULE_ROWS = (("xfa_std_winning_day_min", "std_winning_day_min"), ("xfa_std_winning_days", "std_winning_days"),
             ("xfa_std_cap", "std_cap"), ("xfa_cons_min_days", "cons_min_days"),
             ("xfa_cons_max_day_frac", "cons_max_day_frac"), ("xfa_cons_cap", "cons_cap"),
             ("payout_min", "payout_min"))

#: the three designs (D-649): the registration, its model and cell, and its registered files
DESIGN_DEFS: dict[str, dict[str, str]] = {
    "p14": dict(prereg="P-14", model="A3-BRK30-CB20", cell="a3_brk30_cb20", gate_file="a3_brk30_cb20_gate.csv",
                paths_file="a3_brk30_cb20_gate_paths.csv"),
    "p15": dict(prereg="P-15", model="RC", cell="rc_s100_all", gate_file="rc_s100_all_gate.csv",
                paths_file="rc_s100_all_gate_paths.csv"),
    "p16": dict(prereg="P-16", model="RC150", cell="rc_s150_all", gate_file="rc_s150_all_gate.csv",
                paths_file="rc_s150_all_gate_paths.csv"),
}


# ------------------------------------------------------------------------------------------------ the inputs


def build_p14(rd: Path) -> dict[str, Any]:
    """P-14's trades as its registered run and every later identity build them (`rc_screen.inputs`: A3's walk read
    only, the no-closure plan pinned; `a3_brk30.cell_trades`), with the registered test's two trade pins."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import rc_screen as S

    I = S.inputs()
    t, days = B.cell_trades(I["L"])
    bad = B.identity_with_screen(Path(rd), t, days, I["L"]) + C.p13_trade_problems(Path(rd), t, days, I["L"])
    return {"I": I, "t": t, "days": [str(d) for d in days], "seed": int(C.SEED), "trade_problems": bad,
            "trade_check": "the trades are the screen's rank-1 cell (a3_brk30.identity_with_screen: the screen file's "
                           "sha256, the rung walk's cache inputs, every fact, edge and era row) and P-13's "
                           "(a3_brk30_cb20.p13_trade_problems: each R's e, bounds, count, blocks and sd, the trade and "
                           "day counts)"}


def _rc(rd: Path, build, spec) -> dict[str, Any]:
    import rc_dev_test as D

    I, b = build()
    t = b["cells"][spec.cell]["trades"]
    if t is None:
        raise SystemExit(f"REFUSED ({DECISION}): the cell {spec.cell} holds no trade.")
    bad = D.trade_problems(Path(rd), b, I["L"]["fcfg"], spec=spec)
    return {"I": I, "t": t, "days": [str(d) for d in b["days"]], "seed": int(spec.seed), "trade_problems": bad,
            "trade_check": f"the trades are results/{spec.screen_file}'s {spec.cell} (count, busiest day, capacity, "
                           "long share, candidates a day, every R's unresolved share) and their content hash is the "
                           f"registered {spec.trades_sha256}"}


def build_p15(rd: Path) -> dict[str, Any]:
    """P-15's cell as `rc_dev_test` builds it (`build_cells`), its trades by the screen's row and the content hash."""
    import rc_dev_test as D

    return _rc(rd, D.build_cells, D.P15)


def build_p16(rd: Path) -> dict[str, Any]:
    """P-16's cell as `rc150_dev_test` builds it (`build_cells`), its trades by the screen's row and the content
    hash."""
    import rc150_dev_test as R

    return _rc(rd, R.build_cells, R.SPEC)


BUILDERS = {"p14": build_p14, "p15": build_p15, "p16": build_p16}


def gate_arguments(X: dict[str, Any], n_paths: int) -> dict[str, Any]:
    """`gate.run_gate`'s arguments for a design's gate campaign, as its registered run's `go("gate", ...)` builds them
    (`a3_brk30_cb20._registered_run`, `rc_dev_test.run`): the era rule's 0.05 bounds, the blocks, the day capacity, the
    no-closure plan, P-14's budget and strict rule, the placement off, 0 % denial, the registered seed."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import score_fv3_grid as gf

    L = X["I"]["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = X["t"], X["days"]
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    return A.gate_kwargs(blocks, fcfg, tv, X["I"]["plan"], e_by, lb_by, None, seed=int(X["seed"]),
                         n_paths=int(n_paths), horizon=int(fcfg["gate"]["campaign"]["horizon_days"]),
                         capacity=B.capacity(t, fcfg), levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP,
                         purchase_budget=C.BUDGET)


def campaign_of(design: str, kw: dict[str, Any], dates: list[str]):
    """The gate's arguments as a `customer_slices.Campaign` (its point blocks, its dates, the arguments)."""
    import customer_slices as cs

    kw = dict(kw)
    blocks = kw.pop("blocks")
    return cs.Campaign(design, list(blocks), list(dates), kw)


def engine_args(camp: Any, arm: str) -> dict[str, Any]:
    """One path's arguments at this arm, 0 % denial: `customer_slices.engine_args` (what `gate.run_gate` hands
    `SharedDayDraws` and `simulate_lockstep_campaign` hands `simulate_lockstep_path`; D-508's test ties it to the gate's
    call argument for argument) with the gate's own two horizons in place of the replay's -- the campaign's defaults,
    read off `simulate_lockstep_campaign`'s signature -- and the gate's horizon and seed beside."""
    import inspect

    import customer_slices as cs

    from propedge.campaign.lockstep import simulate_lockstep_campaign

    kw = camp.kw
    a = cs.engine_args(kw, arm, camp.blocks, purchase_budget=kw.get("purchase_budget"))
    sig = inspect.signature(simulate_lockstep_campaign).parameters
    for k in ("funded_horizon_days", "combine_max_days"):
        a["path"][k] = sig[k].default
    a["horizon"] = int(kw["horizon_days"])
    return a


def rule_of(kw: dict[str, Any], ledger: Any = None) -> tuple[DB.Rule, list[str]]:
    """The rule values the readings lean on, each from the verified ledger (`RULE_ROWS`), and every one the campaign's
    own rules carry differently (the problems; empty when they agree). The balance's payable share is the rules' own;
    the payout fraction and kept balance the campaign's protocol's; the tolerance the engine's."""
    from propedge.campaign.lockstep import EPS
    from propedge.contract.rules import load_rules

    led = load_rules() if ledger is None else ledger
    rules, proto = kw["rules"], kw["protocol"]
    v = {name: led.value(name) for name, _ in RULE_ROWS}
    bad = [f"{name} is {v[name]!r} in the ledger and {getattr(rules, attr)!r} in the campaign's rules"
           for name, attr in RULE_ROWS if float(v[name]) != float(getattr(rules, attr))]
    if str(proto.payout_path) != "standard":
        bad.append(f"the campaign's payout path is {proto.payout_path!r}, not the Standard path")
    rule = DB.Rule(win_min=float(v["xfa_std_winning_day_min"]), win_days=int(v["xfa_std_winning_days"]),
                   std_cap=float(v["xfa_std_cap"]), cons_min_days=int(v["xfa_cons_min_days"]),
                   cons_max_day_frac=float(v["xfa_cons_max_day_frac"]), cons_cap=float(v["xfa_cons_cap"]),
                   payout_min=float(v["payout_min"]), payout_max_frac=float(rules.payout_max_frac_of_balance),
                   payout_frac=float(proto.payout_frac), keep_balance=float(proto.keep_balance), eps=float(EPS))
    return rule, bad


def spec_of(kw: dict[str, Any], rule: DB.Rule, payout_timing: str) -> tuple[dict[str, Any], list[str]]:
    """What a path's reading needs beside its records: the table's trade limit by leaf name (D-363's
    `leaf_trade_caps`), the rule, and whether the session after a request is left out of the cycle. The problems: a
    leaf name carrying two limits (a day under it could not be classed)."""
    import fv3_xfa_time_budget as xb

    from propedge.contract.payout_timing import request_day_excluded

    caps = xb.leaf_trade_caps(kw["risk_policy"].as_dict())
    two = sorted(k for k, v in caps.items() if v is None)
    return ({"caps": caps, "rule": rule, "request_day_excluded": bool(request_day_excluded(payout_timing))},
            [f"the leaf name {k!r} carries two trade limits" for k in two[:5]])


# ------------------------------------------------------------------------------------------------ one path


def one_path(blk: list, args: dict[str, Any], path_seed: int, *, records: bool = True):
    """One path of the gate campaign from its seed, as `lockstep._one_path` runs it for `gate.run_gate`: the path's own
    `SharedDayDraws` on the arm's blocks, then `simulate_lockstep_path` -- with the engine's per-trade ledger and daily
    recorder on (`records`). (the path; the router's counts, None where the layout has no router)."""
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    sd = SharedDayDraws({0: list(blk)}, seed=int(path_seed), **args["draws"])
    x = simulate_lockstep_path(args["draws"]["protocol"], seed=int(path_seed), horizon_days=int(args["horizon"]),
                               record_trades=bool(records), record_days=bool(records), **args["path"],
                               **sd.lockstep_kwargs())
    r = sd.router
    tally = None if r is None else {"routed": int(r.routed), "skipped": int(r.skipped),
                                    "skipped_opposite": int(getattr(r, "skipped_opposite", 0)),
                                    "skipped_busy": int(getattr(r, "skipped_busy", 0)),
                                    "passed_over": int(getattr(r, "passed_over", 0))}
    return x, tally


def path_figures(i: int, x: Any) -> dict[str, Any]:
    """A path's figures as the registered per-path record carries them (`portfolio_stage.composed_hook`'s sink)."""
    from propedge.campaign.portfolio import slot_use

    p, su = x.path, slot_use(x)
    tbd = getattr(p, "trades_by_day", ())
    return {"path": int(i), "final_cash": float(p.final_cash), "fees": float(p.total_fees),
            "payouts": float(p.total_payouts), "accounts_funded": int(p.accounts_funded),
            "combine_attempts": int(su["combine_attempts"]), "xfas": int(su["xfas"]),
            "trades": int(sum(tbd)) if len(tbd) else None, "trades_sized": int(p.trades_sized),
            "attempts_started": int(p.attempts_started), "realised_risk": float(p.realised_risk_total),
            "intended_capped_risk": float(getattr(p, "intended_capped_risk_total", 0.0)),
            "days_to_first_payout": p.days_to_first_payout, "combine_slot_days": float(su["combine_slot_days"]),
            "xfa_slot_days": float(su["xfa_slot_days"]), "combines_abandoned": float(su["combines_abandoned"]),
            "xfas_abandoned": float(su["xfas_abandoned"])}


def reduce_path(i: int, x: Any, tally: dict[str, int] | None, spec: dict[str, Any], horizon: int) -> dict[str, Any]:
    """Everything the readings need of one recorded path, so the path itself can be dropped: its figures; one row a
    funded account (D-363's reader's columns, `fv3_xfa_time_budget.xfa_rows`, and `account_measures`' additions); one
    row a Combine attempt (D-363's `combine_rows`); the supply counts; and every way its records disagree with the
    engine's own counts (`problems`)."""
    import fv3_xfa_time_budget as xb

    caps, rule = spec["caps"], spec["rule"]
    fig = path_figures(i, x)
    problems: list[str] = []
    n_days: Counter = Counter()
    n_trades: Counter = Counter()
    leaves: Counter = Counter()
    days_by: dict[int, list] = defaultdict(list)
    trades_by: dict[int, list] = defaultdict(list)
    for r in x.account_days:
        kind = r.get("kind")
        n_days[kind] += 1
        if kind == "funded":
            days_by[int(r["index"])].append(r)
            leaves[xb.leaf_of(r["regime"])] += 1
    for r in x.trades:
        kind = r.get("kind")
        n_trades[kind] += 1
        if kind == "funded":
            trades_by[int(r["index"])].append(r)
    if fig["trades"] is not None and len(x.trades) != fig["trades"]:
        problems.append(f"path {i}: {len(x.trades)} ledger rows against {fig['trades']} trades")
    if n_days["combine"] != sum(int(c.days) for c in x.combines) or n_trades["combine"] != sum(
            int(c.trades) for c in x.combines):
        problems.append(f"path {i}: the Combines' day or ledger rows are not their days and trades")
    d363 = {int(r["index"]): r for r in xb.xfa_rows([x], caps, rule.win_min).to_dict("records")}
    accounts, request_days = [], 0
    for f in x.funded:
        idx = int(f.index)
        ds = sorted(days_by.get(idx, []), key=lambda r: int(r["day"]))
        ts = sorted(trades_by.get(idx, []), key=lambda r: (int(r["day"]), int(r["slot"])))
        per_day = Counter(int(r["day"]) for r in ts)
        pos = {int(r["day"]): k for k, r in enumerate(ds)}
        bad: list[str] = []
        if len(ds) != int(f.days) or len(pos) != len(ds):
            bad.append("its day rows are not its days")
        if len(ts) != int(f.trades) or any(d not in pos for d in per_day):
            bad.append("its ledger rows are not its trades")
        traded = [per_day.get(int(r["day"]), 0) > 0 for r in ds]
        classes = [xb.classify_day(tr, float(r["day_pnl"]), caps.get(xb.leaf_of(r["regime"])), rule.win_min)
                   for tr, r in zip(traded, ds)]
        opening = None
        if ts and int(ts[0]["day"]) in pos:
            o = ts[0]
            opening = {"session": pos[int(o["day"])], "pnl": float(o["pnl"]),
                       "balance_after": float(o["balance_after"]), "floor": float(o["floor"]),
                       "policy_risk": o.get("policy_risk"), "policy_rr": o.get("policy_rr"),
                       "realised_risk": o.get("realised_risk"), "contracts": o.get("contracts")}
        row = d363[idx]
        req = [float(r.get("requested") or 0.0) for r in ds]
        m, more = DB.account_measures(pnl=[float(r["day_pnl"]) for r in ds], traded=traded, classes=classes,
                                      requested=req, eligible=[bool(r.get("eligible")) for r in ds],
                                      balance=[float(r["balance"]) for r in ds], end=str(row["end"]),
                                      opening=opening, rule=rule)
        bad += more
        if sum(1 for v in req if v > 0) != int(f.n_payouts):
            bad.append("its payout requests are not its payouts")
        if int(f.n_payouts) > 0:
            if m["req1_session"] != float(int(f.first_payout_day) + 1):
                bad.append("its first request's session is not the engine's first payout day")
            if not abs(float(m["profit_at_req1"]) - float(f.balance_at_first_payout)) <= TOL:
                bad.append("its profit at its first request is not the engine's balance at the first payout")
        if any(int(row[c]) != sum(1 for k in classes if k == c) for c in DB.DAY_CLASSES):
            bad.append("D-363's reader and this one class its days differently")
        if spec.get("request_day_excluded"):
            request_days += sum(1 for v in req[:-1] if v > 0)
        accounts.append({**row, "path": int(i), "observable_sessions": int(horizon) - (int(f.activation_day) + 1),
                         **m})
        problems += [f"path {i} funded account {idx}: {b}" for b in bad]
    combines = [{**r, "path": int(i)} for r in xb.combine_rows([x]).to_dict("records")]
    p = x.path
    supply = {"account_days": dict(n_days), "trades": dict(n_trades), "leaves": dict(leaves),
              "request_days": int(request_days),
              "multi_breach_days": int((np.asarray(x.breaches_per_day) >= 2).sum()), "router": tally,
              "sizing": {k: int(getattr(p, k, 0) or 0) for k in ("trades_sized", "trades_unsized",
                                                                  "trades_stood_aside")}}
    return {"figures": fig, "accounts": accounts, "combines": combines, "supply": supply, "problems": problems,
            "units": len(accounts) + len(combines)}


def memory_mb() -> tuple[float, float]:
    """This process's (peak working set, working set now) in MB (Windows: `GetProcessMemoryInfo`; elsewhere
    `ru_maxrss` for both); NaN unread."""
    nan = float("nan")
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class _Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]

            k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Counters), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            c = _Counters()
            c.cb = ctypes.sizeof(_Counters)
            if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
                return nan, nan
            return float(c.PeakWorkingSetSize) / 2**20, float(c.WorkingSetSize) / 2**20
        import resource

        peak = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
        return peak, peak
    except (OSError, ValueError, AttributeError, ImportError):
        return nan, nan


def _chunk(task: tuple) -> dict[str, Any]:
    """(the arm's blocks, the path's arguments, [(path, its seed), ...], the reading's spec) -> each path run with the
    records on, read (`reduce_path`) and dropped; the seconds and this process's memory beside (its peak working set
    and the largest working set seen after a path)."""
    import warnings

    warnings.filterwarnings("ignore")
    blk, args, items, spec = task
    t0 = time.time()
    out, held = [], float("nan")
    for i, s in items:
        x, tally = one_path(blk, args, s)
        out.append(reduce_path(i, x, tally, spec, int(args["horizon"])))
        now = memory_mb()[1]                 # the path's records still held: the most a path adds
        held = now if not held >= now else held
        del x
    return {"paths": out, "seconds": time.time() - t0, "peak_mb": memory_mb()[0], "working_mb": held,
            "pid": os.getpid()}


def run_arm(camp: Any, arm: str, n_paths: int, workers: int, spec: dict[str, Any], what: str) -> dict[str, Any]:
    """One design's arm: its first `n_paths` paths (the campaign seed's sequence, `lockstep.path_seeds`), each run with
    the records on and read, across a guarded pool (`customer_journey._pool_run`) or here (one worker). (the paths'
    readings in path order; the seconds; the largest peak and working memory of a process that ran paths)."""
    import customer_journey as CJ
    import customer_slices as cs

    from propedge.campaign.lockstep import path_seeds

    t0 = time.time()
    args = engine_args(camp, arm)
    blk = cs.arm_blocks(camp, arm)
    items = list(enumerate(path_seeds(int(camp.kw["seed"]), int(n_paths))))
    k = -(-len(items) // CHUNK_PATHS) if int(workers) <= 1 else min(len(items), 4 * int(workers))
    bounds = [round(j * len(items) / k) for j in range(k + 1)]
    tasks = [(blk, args, items[bounds[j]:bounds[j + 1]], spec) for j in range(k)]
    if int(workers) > 1 and len(tasks) > 1:     # what each path worker is handed (the arm's blocks, mostly)
        import pickle

        print(f"  {what}: a task pickles to {len(pickle.dumps(tasks[0])) / 2**20:.0f} MB", flush=True)
    res = CJ._pool_run(tasks, _chunk, int(workers), what)
    paths = [p for c in res for p in c["paths"]]
    if [p["figures"]["path"] for p in paths] != list(range(len(items))):
        raise RuntimeError(f"{what}: the paths came back out of order")
    def most(key: str) -> float:
        v = [float(c[key]) for c in res if np.isfinite(c[key])]
        return max(v) if v else float("nan")

    return {"paths": paths, "seconds": time.time() - t0, "path_seconds": float(sum(c["seconds"] for c in res)),
            "peak_mb": most("peak_mb"), "working_mb": most("working_mb"), "processes": len({c["pid"] for c in res})}


# ------------------------------------------------------------------------------------------------ the identities

_TEXT: dict[str, pd.DataFrame] = {}


def _text(rd: Path, name: str) -> pd.DataFrame:
    """A result file on record as text (its manifest checked first), read once."""
    from propedge.reporting.results import verify_result

    key = str(Path(rd) / name)
    if key not in _TEXT:
        ok, msg = verify_result(Path(rd) / name)
        if not ok:
            raise SystemExit(f"REFUSED ({DECISION}): {name}: {msg}")
        _TEXT[key] = pd.read_csv(Path(rd) / name, dtype=str, keep_default_na=False, low_memory=False)
    return _TEXT[key]


def _at_zero(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["enforcement_p"], errors="coerce") == 0.0


def setting_problems(rd: Path, d: dict[str, str], kw: dict[str, Any], args: dict[str, dict[str, Any]], seed: int
                     ) -> list[str]:
    """The rebuilt campaign against the registered gate rows (`gate_file`, section `gate`, 0 %, each arm's shift):
    `SETTING_COLS`, the placement off and the Standard path; the registered manifest's seed and registration."""
    import customer_journey as CJ

    ref = _text(rd, d["gate_file"])
    g = ref[(ref["section"] == GATE_RUN) & _at_zero(ref)]
    out = []
    man = json.loads((Path(rd) / (d["gate_file"] + ".manifest.json")).read_text(encoding="utf-8"))
    if int(man.get("seed") or -1) != int(seed):
        out.append(f"the campaign seed is not {d['gate_file']}'s registered seed")
    if str(man.get("prereg_id")) != d["prereg"]:
        out.append(f"{d['gate_file']} is registered as {man.get('prereg_id')}, not {d['prereg']}")
    budget = kw.get("purchase_budget") or (None, None)
    for arm in ARMS:
        r = g[g["shift"] == DB.SHIFT_OF[arm]]
        if len(r) != 1:
            out.append(f"{d['gate_file']} holds {len(r)} gate rows at 0 % for {DB.SHIFT_OF[arm]}")
            continue
        r = r.iloc[0]
        a = args[arm]
        mine = {"accounts": kw["accounts"], "combines": kw["combines"], "total_accounts": kw["total_accounts"],
                "risk_policy": getattr(kw["risk_policy"], "id", None), "one_at_a_time": kw.get("one_at_a_time"),
                "rtp": bool(a["path"]["conduct"].rtp), "routing": kw["routing"],
                "cross_account_rule": bool(a["draws"]["cross_account"]), "mode": a["draws"]["mode"],
                "settlement": a["draws"]["settlement"], "payout_timing": a["path"]["payout_timing"],
                "bankroll": kw["bankroll"], "horizon_days": a["horizon"], "budget_k": budget[0],
                "budget_window_days": budget[1]}
        out += [f"{arm} {k}: the campaign's differs from {d['gate_file']}'s" for k in SETTING_COLS
                if not CJ._same(mine[k], r[k])]
        if float(a["path"]["conduct"].enforcement_p) != 0.0 or bool(a["path"]["conduct"].rtp):
            out.append(f"{arm}: the campaign is not at 0 % denial with the placement off")
    if int(args[ARMS[0]]["horizon"]) != DB.HORIZON:
        out.append(f"the campaign's horizon is not {DB.HORIZON} days")
    return out


def path_problems(figures: list[dict[str, Any]], ref: pd.DataFrame, shift: str) -> list[str]:
    """The re-run paths against the registered per-path record's gate run at 0 % for the same paths, on
    `IDENTITY_COLS` and `IDENTITY_MORE` to 1e-6 (a blank equal to a blank). A problem names the column and how many
    paths differ, never a value."""
    n = len(figures)
    b = ref[(ref["run"] == GATE_RUN) & (ref["shift"] == shift) & _at_zero(ref)].copy()
    b["path"] = pd.to_numeric(b["path"], errors="coerce")
    b = b.sort_values("path").head(n).reset_index(drop=True)
    if len(b) != n or b["path"].tolist() != list(range(n)):
        return [f"{shift}: the record holds {len(b)} of the first {n} paths"]
    a = pd.DataFrame(figures).sort_values("path").reset_index(drop=True)
    out = []
    for c in (*IDENTITY_COLS, *IDENTITY_MORE):
        x = pd.to_numeric(a[c], errors="coerce").to_numpy(float)
        y = pd.to_numeric(b[c], errors="coerce").to_numpy(float)
        same = (np.isnan(x) & np.isnan(y)) | np.isclose(x, y, rtol=0.0, atol=TOL)
        if not same.all():
            out.append(f"{shift} {c}: {int((~same).sum())} of {n} paths differ (first: path {int(np.argmin(same))})")
    return out


def _ident(design: str, arm: str, measure: str, check: str, problems: list[str], compared: int | None = None
           ) -> dict[str, Any]:
    d = DESIGN_DEFS.get(design, {})
    return {"design": design, "prereg": d.get("prereg", ""), "arm": arm, "section": "identity", "group": "",
            "measure": measure, "value": float(not problems), "n": int(compared or 0), "basis": DB.IDENTITY,
            "note": check, "problems": "; ".join(problems[:4]), "differing": len(problems)}


# ------------------------------------------------------------------------------------------------ the readings


def assemble(paths: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """The paths' readings as one table of funded accounts, one of Combine attempts and the supply counts summed."""
    acc = pd.DataFrame([a for p in paths for a in p["accounts"]], columns=list(DB.ACC_COLS))
    cmb = pd.DataFrame([c for p in paths for c in p["combines"]], columns=["path", "index", "days", "trades", "end"])
    supply: dict[str, Any] = {"account_days": Counter(), "trades": Counter(), "leaves": Counter(), "request_days": 0,
                              "multi_breach_days": 0, "sizing": Counter(),
                              "router": Counter({"paths": 0})}
    for p in paths:
        s = p["supply"]
        for k in ("account_days", "trades", "leaves", "sizing"):
            supply[k].update(s[k])
        supply["request_days"] += int(s["request_days"])
        supply["multi_breach_days"] += int(s["multi_breach_days"])
        if s["router"] is not None:
            supply["router"].update(s["router"])
            supply["router"]["paths"] += 1
    return acc, cmb, {k: (dict(v) if isinstance(v, Counter) else v) for k, v in supply.items()}


def readings(design: str, arm: str, paths: list[dict[str, Any]], rule: DB.Rule, horizon: int, n_leaves: int
             ) -> list[dict[str, Any]]:
    """One design and arm's rows: every section of `u_xfa_day_budget.summarise`, labelled."""
    acc, cmb, supply = assemble(paths)
    rows = DB.summarise(acc, cmb, supply, rule, len(paths), int(horizon))
    rows.append({"section": "notes", "group": "", "measure": "table_leaf_names", "value": float(n_leaves), "n": 0,
                 "basis": DB.NOTE, "note": "leaf names of the table, each with one trade limit (a limit of 0: the "
                                           "table sits the session out)"})
    head = {"design": design, "prereg": DESIGN_DEFS[design]["prereg"], "arm": arm}
    return [{**head, **r} for r in rows]


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import tempfile

    import fv3_xfa_time_budget as xb

    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every identity and the pipeline on a few paths; identity "
                    "lines, row counts and timing only; written to a temporary folder, since removed")
    ap.add_argument("--paths", type=int, default=None, help=f"the first N paths of each registered seed's sequence "
                    f"(the measurement: {DB.PATHS}; --check: {CHECK_PATHS} unless given)")
    ap.add_argument("--workers", type=int, default=1, help="path workers (the memory guard may grant fewer)")
    ap.add_argument("--designs", default=None, help="a comma-separated subset of " + ",".join(DB.DESIGNS)
                    + " (--check only)")
    a = ap.parse_args(argv)
    names = DB.DESIGNS if a.designs is None else tuple(x.strip() for x in a.designs.split(",") if x.strip())
    unknown = [x for x in names if x not in DB.DESIGNS]
    if unknown:
        print(f"REFUSED ({DECISION}): not a design: {unknown}")
        return 2
    names = tuple(x for x in DB.DESIGNS if x in names)
    n_paths = int(a.paths) if a.paths is not None else (CHECK_PATHS if a.check else DB.PATHS)
    if n_paths < 1:
        print(f"REFUSED ({DECISION}): --paths must be at least 1.")
        return 2
    if not a.check and (n_paths != DB.PATHS or names != DB.DESIGNS):
        print(f"REFUSED ({DECISION}): the measurement is the declared one -- {', '.join(DB.DESIGNS)} at {DB.PATHS} "
              "paths; a smaller or partial run is --check (which writes nothing to results/).")
        return 2
    rd = RESULTS_DIR
    t_all = time.time()

    # ---- the declaration
    decl = DB.declaration()
    bad = DB.declaration_problems(decl)
    if tuple(xb.DAY_CLASSES) != DB.DAY_CLASSES or tuple(xb.SINCE) != DB.SINCE:
        bad.append("D-363's day classes or days since activation are not the module's")
    if tuple(DESIGN_DEFS) != DB.DESIGNS:
        bad.append("the designs are not the module's")
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-649's declaration -- " + "; ".join(bad[:8]))
        return 3
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}) and every phrase the build's "
          "constants rest on", flush=True)
    idents: list[dict[str, Any]] = [_ident("", "", "declaration", f"DECISIONS.md's {DECISION} row (sha256 "
                                           f"{decl['sha256']}) and every phrase this build's constants rest on", [])]
    failures: list[str] = []
    rows: list[dict[str, Any]] = []
    timing: dict[str, dict[str, Any]] = {}
    seeds: dict[str, int] = {}
    rule_used: dict[str, Any] = {}
    policy_ids: dict[str, Any] = {}

    def settle(new: list[dict[str, Any]]) -> bool:
        """Print each identity's line and keep its row; False when one fails."""
        ok = True
        for r in new:
            idents.append(r)
            who = " ".join(x for x in (r["design"], r["arm"]) if x) or DECISION
            count = f" [{r['n']} compared]" if r["n"] else ""
            if r["value"] == 1.0:
                print(f"identity HOLDS: {who}: {r['note']}{count}", flush=True)
            else:
                print(f"identity FAILS: {who}: {r['note']}{count} -- {r['problems']}", flush=True)
                failures.append(f"{who}: {r['problems']}")
                ok = False
        return ok

    for design in names:
        d = DESIGN_DEFS[design]
        print(f"{design} ({d['prereg']}, {d['model']}): the inputs...", flush=True)
        t0 = time.time()
        X = BUILDERS[design](rd)
        kw = gate_arguments(X, n_paths)
        camp = campaign_of(design, kw, X["days"])
        args = {arm: engine_args(camp, arm) for arm in ARMS}
        rule, rule_bad = rule_of(kw)
        spec, leaf_bad = spec_of(kw, rule, args[ARMS[0]]["path"]["payout_timing"])
        seeds[design], rule_used[design], policy_ids[design] = int(X["seed"]), rule.as_dict(), kw["risk_policy"].id
        trades, days_n = int(len(X["t"])), int(len(X["days"]))
        trade_bad, trade_check = X["trade_problems"], X["trade_check"]
        del X
        gc.collect()
        t_in = time.time() - t0
        peak, now = memory_mb()
        print(f"timing: {design} inputs: {t_in:.0f} s ({trades} trades offered on {days_n} sessions); memory: this "
              f"process holds {now:.0f} MB after them (its peak so far {peak:.0f} MB)", flush=True)
        ok = settle([
            _ident(design, "", "trades", trade_check, trade_bad, trades),
            _ident(design, "", "settings", f"the campaign's settings are results/{d['gate_file']}'s gate rows' at 0 % "
                   "(seats, the table, the strict rule, the budget, routing, mode, settlement, payout timing, the "
                   f"bankroll, {DB.HORIZON} days, the placement off) and its seed the registered {kw['seed']}",
                   setting_problems(rd, d, kw, args, kw["seed"]), len(SETTING_COLS) * len(ARMS)),
            _ident(design, "", "rule_values", "the ledger's verified values (" + ", ".join(k for k, _ in RULE_ROWS)
                   + ") are the ones the campaign's rules carry, on the Standard path", rule_bad, len(RULE_ROWS)),
            _ident(design, "", "table_leaves", "no leaf name of the table carries two trade limits", leaf_bad,
                   len(spec["caps"]))])
        timing[design] = {"inputs_seconds": round(t_in, 1), "trades": trades, "sessions": days_n,
                          "inputs_peak_mb": round(peak, 0), "inputs_working_mb": round(now, 0)}
        if not ok:
            continue
        ref = _text(rd, d["paths_file"])
        for arm in ARMS:
            v = run_arm(camp, arm, n_paths, a.workers, spec, f"{design} {arm}")
            secs = float(v["seconds"])
            timing[design][arm] = {"paths": n_paths, "seconds": round(secs, 1),
                                   "seconds_a_path": round(float(v["path_seconds"]) / max(n_paths, 1), 3),
                                   "working_mb": round(float(v["working_mb"]), 0),
                                   "peak_mb": round(float(v["peak_mb"]), 0), "processes": int(v["processes"])}
            print(f"timing: {design} {arm}: {n_paths} paths in {secs:.1f} s ({v['path_seconds'] / max(n_paths, 1):.2f} "
                  f"s a path in its process; {v['processes']} process(es)); memory: a path process held at most "
                  f"{v['working_mb']:.0f} MB with a path's records (its peak {v['peak_mb']:.0f} MB)", flush=True)
            record_bad = [b for p in v["paths"] for b in p["problems"]]
            ok = settle([
                _ident(design, arm, "paths", "each re-run path's " + ", ".join(IDENTITY_COLS) + " -- and "
                       + ", ".join(IDENTITY_MORE) + f" -- equal results/{d['paths_file']}'s {GATE_RUN} run at 0 % ("
                       f"{DB.SHIFT_OF[arm]}) for the same paths, the first {n_paths} of seed {kw['seed']}'s sequence, "
                       f"to {TOL:g}", path_problems([p["figures"] for p in v["paths"]], ref, DB.SHIFT_OF[arm]),
                       n_paths),
                _ident(design, arm, "records", "every account's day rows and ledger rows number its days and trades; "
                       "its payout requests are its payouts, its first request's session and balance the engine's; "
                       "D-363's reader (fv3_xfa_time_budget.xfa_rows) and this one class every day alike; the session "
                       "its qualifying days reach the Standard path's count is the engine's first eligible close; its "
                       "balance before a first request is the sum of its day P&L", record_bad,
                       int(sum(p["units"] for p in v["paths"])))])
            if ok:
                new = readings(design, arm, v["paths"], rule, args[arm]["horizon"], len(spec["caps"]))
                if settle([_ident(design, arm, "tables", "the tables add up: the endings, the day classes, the opening "
                                  "trade's outcomes, the leaves and the router's outcomes each to one, the paid and "
                                  "never-paid accounts to all, the budget's groups and classes to their totals, every "
                                  "share of a count between 0 and 1", DB.table_problems(new), len(new))]):
                    rows += new
            del v
            gc.collect()
        del camp, args, kw
        gc.collect()
    if failures:
        print(f"REFUSED ({DECISION}): {len(failures)} identities fail; nothing read, nothing written -- "
              + "; ".join(failures[:8]))
        return 3

    # ---- the file (only now)
    for r in idents:
        r.pop("problems", None)
        r.pop("differing", None)
    res = DB.frame(idents + rows)
    seconds = time.time() - t_all
    files = sorted({DESIGN_DEFS[x][k] for x in names for k in ("gate_file", "paths_file")})
    params = {"decision": DECISION, "study": DB.STUDY, "declaration_sha256": decl["sha256"],
              "designs": {x: {**DESIGN_DEFS[x], "seed": seeds[x], "policy_id": policy_ids[x]} for x in names},
              "seeds": seeds, "paths": int(n_paths), "horizon": DB.HORIZON,
              "arms": {"verdict": "every R shifted to its 0.05 bound (the gate row's lower-bound arm)",
                       "point": "as traded"},
              "conditions": "0 % denial, the Standard path, the placement off (D-234, D-289); the engine's per-trade "
                            "ledger and daily account recorder on, no engine file changed",
              "rule": rule_used, "rule_rows": [k for k, _ in RULE_ROWS],
              "identity_columns": list(IDENTITY_COLS), "identity_columns_more": list(IDENTITY_MORE),
              "identity_tolerance": TOL, "day_classes": dict(DB.CLASS_LABEL), "since": list(DB.SINCE),
              "week_sessions": DB.WEEK,
              "words": {"session": "a trading session an account was live for, its first counted 1",
                        "trading_day": "a session with at least one trade (8284208)",
                        "before_a_first_payout": "the sessions up to and including the first request's, or to the "
                                                 "account's end",
                        "lost_on_the_opening_trade": "the balance after the account's first trade is at or under its "
                                                     "floor",
                        "n": "the units the value rests on (a share's denominator, a percentile's sample)",
                        "percentiles": "numpy's linear"},
              "references": {f: sha256_of(rd / f) for f in files}, "timing": timing, "workers": int(a.workers),
              "seconds": round(seconds, 1)}
    notes = {"status": DB.READING,
             "variant_count_rule": "none: a measurement of registered designs; no design run, no variant recorded "
                                   "(D-649; D-363's script recorded none)",
             "seed": "none of its own: each design's paths are drawn at its registered campaign seed "
                     "(parameters.seeds)",
             "consistency": DB.DESCRIPTION, "selection": "none (D-649 (4): its reading gets its own decision row)"}

    def write(target: Path | None) -> Path:
        csv, _ = write_result(res, DB.RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                              results_dir=target, parameters=params, notes=notes,
                              description="EXPLORATORY (D-649, program U's U2): the registered gate campaigns of "
                                          "P-14, P-15 and P-16 re-run identically with the engine's records on -- "
                                          "the evaluation and funded funnels, each funded account's days by class, "
                                          "survival and accrual, the table's leaves, signal supply (D-363's "
                                          "sections); the opening funded trade, the sessions and trading days to the "
                                          "fifth winning day and the first payout request, winning days per "
                                          "account-week; and, beside, what the Consistency test would have read day "
                                          "by day (a description from the records, not a run on that path). The "
                                          "identities first (section identity). No design run; nothing selected.")
        return Path(csv)

    by = res.groupby(["design", "arm"], sort=False).size()
    counts = ", ".join(f"{k[0] or 'all'} {k[1] or '-'}: {int(v)}" for k, v in by.items())
    if a.check:
        with tempfile.TemporaryDirectory(prefix="u_xfa_day_budget_check_") as td:
            write(Path(td))
            wrote = sorted(p.name for p in Path(td).iterdir())
        print(f"every identity holds; the pipeline ran on {n_paths} path(s) of {list(names)} at both arms and wrote "
              f"{wrote} ({len(res)} rows: {counts}) to a temporary folder, since removed; nothing written to results/, "
              f"no reading printed (--check). {seconds:.0f} s")
        return 0
    write(results_dir)
    print(f"written: {DB.RESULT}.csv ({len(res)} rows: {counts}); {seconds:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
