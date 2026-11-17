"""Q-47 (E-025 (2)): Stage 2's campaign gate, re-composed so that a design can declare another funded-account class.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import gate as XG
    df, passed = XG.run_gate(blocks, ..., funded_account_cls=MyFundedAccount)   # every vendored argument, plus this one
    df, passed = XG.run_gate(blocks, ..., payout_lag_days=2, household_closure=True,   # Q-71: and these three
                             combine_account_cls=MyCombineAccount)

**Why it exists.** The vendored engine already takes another funded-account class, path by path
(`simulate_lockstep_path(funded_account_cls=...)`, `simulate_lockstep_campaign(funded_account_cls=...)`; R7). Its
gate, `propedge.campaign.gate.run_gate`, does not pass one on. F-P's held-state policy (its draft's 13.1 item 3) needs
the gate with its own `FundedAccount` subclass.

The vendored tree is read-only (E-002). A module attribute of it substituted during a call is the kind of change that
moved A3's cache key in E-011's first run, so it is not done. Instead, `run_gate` below is the vendored function's
body, with exactly three additions:

1. the keyword `funded_account_cls` (default None), checked to be a subclass of the vendored `FundedAccount`, and able
   to pickle when the paths run in workers;
2. it is passed to `simulate_lockstep_campaign` only when given, so with None the engine call is the vendored one
   argument for argument;
3. a row column `funded_account_cls` (the class's module and name), added only when a class is given, as the engine
   names the class in its provenance only when given.

Every helper the body calls is the vendored one, imported, never copied: `shifted_blocks`, `mean_r`, `_GateDraws`,
`ftp_columns`, `budget_columns`, `entry_columns`, the conduct model, the campaign, the layout checks and the path pool.

**The guard, refusing.** The body was composed from the vendored `run_gate` whose source text (LF line endings) has the
sha256 `VENDORED_RUN_GATE_SHA256`. Every call checks it first and refuses (`RuntimeError`) if the vendored function has
changed -- a newer Stage 2 snapshot is a new decision row, and this module is re-composed and re-checked under it.

**Q-71 (the other-firms reading's A-8, `prereg/DRAFT_RD_firms.md` 4.6; E-038): the gate for another plan.** Three more
keywords, each None by default, each checked before anything runs, each passed to the campaign only when given and
named on every row only when given (so with all three absent the rows are the vendored gate's):

4. `payout_lag_days` -- the sessions from a payout's request to its arrival, a whole number of at least 0. None takes
   the vendored gate's own lag: the campaign's `payout_method="aeropay"` read from Stage 2's verified ledger
   (`topstep_payout_lag_days()`). A plan's lag is given with that plan's own `rules` (its payout fee): Stage 2 D-24's
   rule that a lag is never paired with another method's fee is the caller's to keep (A-1's);
5. `household_closure` -- a funded class's household rule (Stage 2 R7, multi-firm D-30): True closes every other live
   account at the first close an account raises it, and the path buys nothing more; False only counts the triggers;
   None takes the class's own default (`HOUSEHOLD_CLOSES_AT_LIVE`). True is refused (`ValueError`) for a funded class
   that declares no household rule -- Topstep's has none;
6. `combine_account_cls` -- the evaluation account's class on every path of every arm, the vendored `CombineAccount`
   or a subclass of it (Stage 2 D-619), checked as `funded_account_cls` is (a subclass; able to pickle when the paths
   run in workers). The vendored campaign does not pass it to its paths, so the gate calls `extended.campaign`'s
   re-composed campaign -- on every call, with or without it: that campaign with no class is the vendored one.

Rows gain `payout_lag_days`, `household_closure` and `combine_account_cls` (the class's module and name), each only when
given. `gate_recomposition_problems` checks that this `run_gate`, with every line marked Q-47, Q-71 or Q-70 removed,
parses to the vendored `run_gate` statement for statement.

**The identities** (`identity/gate_identity.py`):

- synthetic, in the fast tier: the adapter equals the vendored gate, with no class, with `PassThroughFundedAccount`,
  and with every seam given at Topstep's values; each Q-71 keyword has its documented effect on toy campaigns;
- slow: P-14's and P-16's registered gate paths at 4 paths, under the run lock;
- heavy, the lead's: all 500 paths of each.

**Q-70's addition, the place recorder** (`extended/place_records.py`): the keyword `recorder` (default None), an
`extended.place_records.PlaceRecorder`. For each (shift, level) it records, the campaign (`extended.campaign`'s) gets
one more keyword, `path_reducer`, which runs every path with the engine's ledger and day recorder on and reads each
path into compact columns where it ran, dropping the rows; after the call the records go to the recorder and the paths
handed on are the unrecorded campaign's (`recorded_paths`). Every other (shift, level), and every call with None, calls
the campaign exactly as without a recorder: the rows, the hooks and the gate flag are unchanged and the row carries no
new column (`identity/place_records_identity.py`). Its lines in `run_gate` are marked Q-70.
"""
from __future__ import annotations

import hashlib
import inspect
import pickle
from typing import Any, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign import gate as _vg  # noqa: E402
from propedge.campaign.gate import (  # noqa: E402
    ENFORCEMENT_LEVELS,
    GATE_ENFORCEMENT_P,
    _GateDraws,
    budget_columns,
    entry_columns,
    ftp_columns,
    mean_r,
    shifted_blocks,
)
from propedge.campaign.lockstep import CombineAccount, FundedAccount  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

from extended import campaign as _xc  # noqa: E402  (Q-71: the campaign re-composed to pass combine_account_cls)

#: the comment markers on every added line of `run_gate` (Q-47's class, Q-71's seams, Q-70's recorder, Q-105's
#: counters' channel for RD-02)
GATE_MARKERS = ("Q-47", "Q-71", "Q-70", "Q-105")

#: sha256 of the vendored `propedge.campaign.gate.run_gate`'s source text (LF), from which `run_gate` below was composed
#: (Stage 2 f1b42e2, vendored under E-002)
VENDORED_RUN_GATE_SHA256 = "c59e1f9dfbe7f460ee5b33ce22b012fc51d171005a6ded45b1861af836079763"


def vendored_run_gate_sha256() -> str:
    """The sha256 of the vendored `run_gate`'s source text, with line endings normalised to LF."""
    src = inspect.getsource(_vg.run_gate).replace("\r\n", "\n")
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def check_vendored_source(expected: str | None = None) -> None:
    """Refuse (`RuntimeError`) unless the vendored `run_gate` is the one this module was composed from."""
    want = VENDORED_RUN_GATE_SHA256 if expected is None else str(expected)
    got = vendored_run_gate_sha256()
    if got != want:
        raise RuntimeError(f"REFUSED (Q-47): the vendored gate.run_gate's source hashes to {got}, not the {want} this "
                           "adapter was composed from; re-compose extended/gate.py under the new snapshot's row")


class PassThroughFundedAccount(FundedAccount):
    """Topstep's funded account, unchanged: a subclass that overrides nothing. It is given through the seam to show
    that passing a class changes nothing -- the identity's second arm."""


def check_funded_account_cls(funded_account_cls: type | None, workers: int) -> None:
    """Refuse a class that is not the vendored `FundedAccount` or a subclass of it (`TypeError`), and, when the paths
    run in workers, one that cannot pickle (a class defined inside a function cannot reach a worker)."""
    if funded_account_cls is None:
        return
    if not (isinstance(funded_account_cls, type) and issubclass(funded_account_cls, FundedAccount)):
        raise TypeError(f"funded_account_cls must be the vendored FundedAccount or a subclass of it, got "
                        f"{funded_account_cls!r}")
    if int(workers) > 1:
        try:
            pickle.loads(pickle.dumps(funded_account_cls))
        except Exception as exc:          # noqa: BLE001 -- any failure means it cannot reach a path worker
            raise TypeError(f"funded_account_cls {funded_account_cls!r} cannot reach a path worker (it does not "
                            f"pickle: {exc}); define it at a module's top level") from exc


def class_name(funded_account_cls: type) -> str:
    return f"{funded_account_cls.__module__}.{funded_account_cls.__qualname__}"


# ------------------------------------------------------------------------------------------------ Q-71 (A-8)


class PassThroughCombineAccount(CombineAccount):
    """Topstep's evaluation account, unchanged: a subclass that overrides nothing, given through the Q-71 seam to show
    that passing an evaluation class changes nothing."""


def check_combine_account_cls(combine_account_cls: type | None, workers: int) -> None:
    """Refuse a class that is not the vendored `CombineAccount` or a subclass of it (`TypeError`), and, when the paths
    run in workers, one that cannot pickle (a class defined inside a function cannot reach a worker)."""
    if combine_account_cls is None:
        return
    if not (isinstance(combine_account_cls, type) and issubclass(combine_account_cls, CombineAccount)):
        raise TypeError(f"combine_account_cls must be the vendored CombineAccount or a subclass of it, got "
                        f"{combine_account_cls!r}")
    if int(workers) > 1:
        try:
            pickle.loads(pickle.dumps(combine_account_cls))
        except Exception as exc:          # noqa: BLE001 -- any failure means it cannot reach a path worker
            raise TypeError(f"combine_account_cls {combine_account_cls!r} cannot reach a path worker (it does not "
                            f"pickle: {exc}); define it at a module's top level") from exc


def check_payout_lag_days(payout_lag_days: Any) -> int | None:
    """None, or the lag as a whole number of sessions of at least 0. Refused: a bool, a float or anything else that is
    not an integer (`TypeError`) -- the vendored campaign would truncate 2.5 to 2 silently -- and a negative lag
    (`ValueError`)."""
    if payout_lag_days is None:
        return None
    if isinstance(payout_lag_days, (bool, np.bool_)) or not isinstance(payout_lag_days, (int, np.integer)):
        raise TypeError(f"payout_lag_days must be a whole number of sessions, got {payout_lag_days!r}")
    if int(payout_lag_days) < 0:
        raise ValueError(f"payout_lag_days must be at least 0, got {payout_lag_days!r}")
    return int(payout_lag_days)


def check_household_closure(household_closure: Any, funded_account_cls: type | None) -> bool | None:
    """None, or the household rule's reading as a bool (`TypeError` for anything else). True is refused
    (`ValueError`, as the vendored path refuses it) unless the funded class -- the vendored `FundedAccount` when none is
    given -- declares a household rule (`HOUSEHOLD_CLOSES_AT_LIVE`)."""
    if household_closure is None:
        return None
    if not isinstance(household_closure, (bool, np.bool_)):
        raise TypeError(f"household_closure must be None, True or False, got {household_closure!r}")
    cls = FundedAccount if funded_account_cls is None else funded_account_cls
    if bool(household_closure) and not hasattr(cls, "HOUSEHOLD_CLOSES_AT_LIVE"):
        raise ValueError(f"{cls.__qualname__} has no household rule: household_closure=True applies only to a funded "
                         "class that declares one (HOUSEHOLD_CLOSES_AT_LIVE)")
    return bool(household_closure)


def seam_arguments(payout_lag_days: Any, household_closure: Any, combine_account_cls: type | None,
                   funded_account_cls: type | None, workers: int) -> dict[str, Any]:
    """Q-71's three keywords, checked, as the campaign's keywords: each present only when given, in the order
    `payout_lag_days`, `household_closure`, `combine_account_cls`. Empty when none is given."""
    lag = check_payout_lag_days(payout_lag_days)
    household = check_household_closure(household_closure, funded_account_cls)
    check_combine_account_cls(combine_account_cls, int(workers))
    out: dict[str, Any] = {}
    if lag is not None:
        out["payout_lag_days"] = lag
    if household is not None:
        out["household_closure"] = household
    if combine_account_cls is not None:
        out["combine_account_cls"] = combine_account_cls
    return out


def seam_columns(seam_kw: dict[str, Any]) -> dict[str, Any]:
    """The row columns that name Q-71's keywords given: the lag (sessions), the household reading (bool), the
    evaluation class (its module and name)."""
    return {k: (class_name(v) if k == "combine_account_cls" else v) for k, v in seam_kw.items()}


def topstep_payout_lag_days(ledger: Any | None = None) -> int:
    """The lag the gate takes when `payout_lag_days` is None: its campaign's `payout_method="aeropay"`, read from Stage
    2's verified ledger (`ledger`, or the vendored `config/rules.yaml` when None) by the vendored
    `payout_method_terms`."""
    from propedge.campaign.payout_method import payout_method_terms

    return int(payout_method_terms("aeropay", ledger=ledger).lag_days)


def gate_recomposition_problems() -> list[str]:
    """This module's `run_gate` against the vendored one, statement for statement, with every line marked Q-47, Q-71,
    Q-70 or Q-105 removed (`extended.campaign.recomposition_problems`); empty when the only differences are the marked
    lines."""
    return _xc.recomposition_problems(run_gate, _vg.run_gate, GATE_MARKERS)


# ------------------------------------------------------------------------------------------------ Q-70 (the recorder)


def check_recorder(recorder: Any) -> None:
    """None, or an `extended.place_records.PlaceRecorder` (`TypeError` for anything else); with one, the vendored path
    runner it re-composes is checked against its pins first."""
    if recorder is None:
        return
    from extended.place_records import PlaceRecorder, check_vendored_runner_source

    if not isinstance(recorder, PlaceRecorder):
        raise TypeError(f"recorder must be an extended.place_records.PlaceRecorder, got {type(recorder).__name__}")
    check_vendored_runner_source()


def recorder_arguments(recorder: Any, shift: str, enforcement_p: float, blk: Sequence[DayBlock], rules: Any
                       ) -> dict[str, Any]:
    """The campaign's keyword for one (shift, level): `path_reducer` when the recorder records it, else nothing (so
    the campaign is called exactly as without a recorder)."""
    if recorder is None or not recorder.wants(shift, float(enforcement_p)):
        return {}
    return {"path_reducer": recorder.reducer(shift, float(enforcement_p), blk, rules)}


def check_gate_counters(counters: Any, funded_account_cls: type | None, recorder: Any) -> None:
    """Q-105 (RD-02's counters' channel, its 13.1 items 1 and 3): None, or an `extended.payout_policy.GateCounters`
    (`TypeError` otherwise) with one of RD-02's funded classes declared (`TypeError` otherwise). Refused with a recorder
    too (`ValueError`): RD-02 runs its gates without one, and the two have not been composed."""
    if counters is None:
        return
    from extended import payout_policy as PP

    PP.check_counters(counters, PP.GateCounters)
    PP.check_counted_class(funded_account_cls)
    if recorder is not None:
        raise ValueError("counters and recorder together are not composed (RD-02 runs its gates with no recorder)")


def recorded_paths(recorder: Any, rec_kw: dict[str, Any], paths: list, *, shift: str, enforcement_p: float,
                   n_paths: int, horizon_days: int, seed: int) -> list:
    """The campaign's paths as the gate reads them: unchanged when nothing was recorded; else each path's record taken
    into the recorder and the path handed on as the unrecorded campaign's (`PlaceRecorder.collect`)."""
    if not rec_kw:
        return paths
    return recorder.collect(shift, float(enforcement_p), paths, n_paths=int(n_paths), horizon_days=int(horizon_days),
                            seed=int(seed))


def run_gate(
    blocks: Sequence[DayBlock],
    *,
    e: float,
    lb: float,
    protocol: Any,
    bankroll: float,
    horizon_days: int,
    n_paths: int,
    seed: int,
    accounts: int,
    sizing: Any,
    rules: Any,
    mode: str = "rotation",
    levels: Sequence[float] = ENFORCEMENT_LEVELS,
    ledger: Any | None = None,
    settlement: str | None = None,
    combines: int = 1,
    total_accounts: int | None = None,
    risk_policy: Any = None,
    e_by_rr: dict[float, float] | None = None,
    lb_by_rr: dict[float, float] | None = None,
    payout_timing: str | None = None,
    markets: int | Sequence[str] | None = None,
    path_hook: Any = None,
    rtp: bool = True,
    routing: str = "longest_waiting",
    cross_account: bool = False,
    one_at_a_time: float | None = None,
    routing_rule: str | None = None,
    flip: Any = None,
    hold_to_own_exit: bool = False,
    workers: int = 1,
    memory_per_worker_gb: float | None = None,
    focused_trader: Any = None,
    purchase_budget: tuple[int, int] | None = None,
    wallet_stop: float | None = None,
    pause_after_funded: int | None = None,
    seat_ramp: int | None = None,
    mean_block: float | None = None,
    funded_account_cls: type | None = None,                                     # Q-47
    payout_lag_days: int | None = None,                                         # Q-71
    household_closure: bool | None = None,                                      # Q-71
    combine_account_cls: type | None = None,                                    # Q-71
    recorder: Any = None,                                                       # Q-70
    counters: Any = None,                                                       # Q-105
) -> tuple[pd.DataFrame, bool]:
    """The vendored `propedge.campaign.gate.run_gate` (its docstring holds every argument's meaning), plus
    `funded_account_cls` (Q-47): the funded account's class on every path of every arm -- the vendored `FundedAccount`
    or a subclass of it -- passed to the campaign only when given, and named on every row (`funded_account_cls`) only
    when given; and Q-71's `payout_lag_days`, `household_closure` and `combine_account_cls` (the module docstring, items
    4-6), each passed and named only when given. With none of the four given the engine call is the vendored one --
    through `extended.campaign`'s re-composed campaign, which with no evaluation class is the vendored campaign.

    `recorder` (Q-70): an `extended.place_records.PlaceRecorder`; the (shift, level) campaigns it asks for are recorded
    into it (its `trades()`, `accounts()`, `per_year()`, `problems()` afterwards), every row and path unchanged."""
    check_vendored_source()                                                     # Q-47
    _xc.check_vendored_source()                                                 # Q-71
    check_funded_account_cls(funded_account_cls, int(workers))                  # Q-47
    cls_kw: dict[str, Any] = {} if funded_account_cls is None else {"funded_account_cls": funded_account_cls}  # Q-47
    seam_kw = seam_arguments(payout_lag_days, household_closure, combine_account_cls,  # Q-71
                             funded_account_cls, int(workers))                  # Q-71
    check_recorder(recorder)                                                    # Q-70
    check_gate_counters(counters, funded_account_cls, recorder)                 # Q-105

    # ---- from here to the end, the vendored body; the additions are marked Q-47, Q-71 and Q-70
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING, check_payout_timing
    from propedge.outcomes.settlement import default_trade_log_settlement

    payout_timing = check_payout_timing(DEFAULT_PAYOUT_TIMING if payout_timing is None else payout_timing)
    settlement = settlement or default_trade_log_settlement(list(blocks))
    from propedge.campaign.lockstep import ConductModel, simulate_lockstep_campaign
    simulate_lockstep_campaign = _xc.simulate_lockstep_campaign  # noqa: F811  # Q-71: the re-composed campaign
    from propedge.campaign.shared_days import check_layout, flat_routing_available

    n_markets = check_layout(mode, list(blocks), flat_routing=flat_routing_available(list(blocks)), markets=markets)
    # D-318: `able` hands each trade to the longest-waiting account that can take it; the default routes as before
    if routing not in ("longest_waiting", "able"):
        raise ValueError(f"routing must be 'longest_waiting' or 'able', got {routing!r}")

    if GATE_ENFORCEMENT_P not in levels:
        raise ValueError(f"the gate's level {GATE_ENFORCEMENT_P} must be among the levels run")
    if not 1 <= int(accounts) <= 5:
        raise ValueError(f"accounts={accounts}: the firm's cap is 5 active funded accounts (D-21)")
    rows = []
    passed = False
    delta_by_rr = None
    if e_by_rr is not None or lb_by_rr is not None:
        if e_by_rr is None or lb_by_rr is None or set(e_by_rr) != set(lb_by_rr):
            raise ValueError("e_by_rr and lb_by_rr must name the same R values")
        delta_by_rr = {float(k): float(lb_by_rr[k]) - float(e_by_rr[k]) for k in e_by_rr}
    seat_frees = str((getattr(protocol, "params", None) or {}).get("seat_frees", "next_session"))   # D-339
    # R11: one pool of path workers for every campaign of the call (none at workers=1, or when the guard allows one);
    # what the workers receive must pickle whatever the guard then allows
    from propedge.campaign.lockstep import check_parallel_inputs, path_pool

    if focused_trader is not None:                       # D-495 (4)
        from propedge.campaign.lockstep import FocusedTraderModel

        if not isinstance(focused_trader, FocusedTraderModel):
            raise TypeError(f"focused_trader must be a FocusedTraderModel, got {type(focused_trader).__name__}")
    ftp_kw = {} if focused_trader is None else {"focused_trader": focused_trader}
    if purchase_budget is not None:                      # D-501
        from propedge.campaign.lockstep import check_purchase_budget

        purchase_budget = check_purchase_budget(purchase_budget)
        ftp_kw["purchase_budget"] = purchase_budget
    entry_kw: dict[str, Any] = {}                        # D-630: each passed only when given
    if wallet_stop is not None or pause_after_funded is not None or seat_ramp is not None:
        from propedge.campaign.lockstep import check_pause_after_funded, check_seat_ramp, check_wallet_stop

        if wallet_stop is not None:
            entry_kw["wallet_stop"] = check_wallet_stop(wallet_stop)
        if pause_after_funded is not None:
            entry_kw["pause_after_funded"] = check_pause_after_funded(pause_after_funded)
        if seat_ramp is not None:
            entry_kw["seat_ramp"] = check_seat_ramp(seat_ramp, total_accounts)
        ftp_kw.update(entry_kw)
    block_kw: dict[str, Any] = {}                        # D-663: passed only when set
    if mean_block is not None:
        if mode != "rotation":
            raise ValueError(f"block-resampled days are verified under rotation only (D-663); mode {mode!r} is refused")
        if not float(mean_block) >= 1.0:
            raise ValueError(f"the mean block is at least one session, got {mean_block!r}")
        block_kw["mean_block"] = float(mean_block)
    if int(workers) > 1:
        check_parallel_inputs(list(blocks), protocol, sizing, rules, risk_policy, flip)
    pool, n_workers = (path_pool(int(workers), n_tasks=int(n_paths), memory_per_worker_gb=memory_per_worker_gb)
                       if int(workers) > 1 and int(n_paths) > 1 else (None, 1))
    try:
        for shift, blk in (("point", list(blocks)), ("lower_bound", shifted_blocks(blocks, lb - e, delta_by_rr))):
            # D-339: the flip stream's spec for the arm -- at its measured edge, or at its own lower bound where the file
            # carries one (a spec without a bound runs as measured on both arms, and the row says so)
            spec = flip
            if flip is not None and shift == "lower_bound":
                spec = flip.at_lower_bound()                     # D-384: a menu shifts each bracket to its own bound
            for p in levels:
                conduct = ConductModel(rtp=bool(rtp), enforcement_p=float(p))
                draws = _GateDraws(blk, protocol=protocol, mode=mode, sizing=sizing, settlement=settlement,
                                   markets=markets, routing=routing, cross_account=cross_account, flip=spec,
                                   hold_to_own_exit=hold_to_own_exit, one_at_a_time=one_at_a_time,
                                   routing_rule=routing_rule, **block_kw)

                draws = draws if counters is None else counters.wrap(draws)                            # Q-105
                rec_kw = recorder_arguments(recorder, shift, float(p), blk, rules)                     # Q-70
                summary, paths = simulate_lockstep_campaign(
                    protocol, edge=0.0, seed=seed, rules=rules, initial_bankroll=bankroll, horizon_days=horizon_days,
                    n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=accounts,
                    max_concurrent_combines=int(combines), max_total_accounts=total_accounts,
                    require_verified_cap=False, ledger=ledger, conduct=conduct, risk_policy=risk_policy,
                    draw_factories_for_path=draws, payout_timing=payout_timing,
                    workers=n_workers, pool=pool,                                                       # R11
                    **ftp_kw,                                                                           # D-495 (4)
                    **cls_kw,                                                                           # Q-47
                    **seam_kw,                                                                          # Q-71
                    **rec_kw,                                                                           # Q-70
                )
                if counters is not None:                 # Q-105: each path's counts, by its seed           # Q-105
                    counters.collect(shift, float(p), draws)                                            # Q-105
                paths = recorded_paths(recorder, rec_kw, paths, shift=shift, enforcement_p=float(p),     # Q-70
                                       n_paths=n_paths, horizon_days=horizon_days, seed=seed)          # Q-70
                every = draws.tallies()                  # each path's router counts, in path order (R11)
                tallies = [x for x in every if x is not None]
                routed = sum(x[0] for x in tallies)
                skipped = sum(x[1] for x in tallies)
                skipped_opp = sum(x[2] for x in tallies)                                                # D-339
                skipped_busy = sum(x[3] for x in tallies)                                               # D-429
                offered = routed + skipped + skipped_opp + skipped_busy
                flips = sum(int(getattr(x.path, "funded_flips", 0)) for x in paths)
                flips_won = sum(int(getattr(x.path, "funded_flips_won", 0)) for x in paths)
                c = pd.DataFrame([x.conduct for x in paths])
                req = c["payouts_requested"].sum()
                row = {
                    "shift": shift, "mode": mode, "settlement": settlement, "mean_r_used": mean_r(blk),
                    "enforcement_p": float(p), "rtp": bool(rtp), "accounts": accounts, "combines": int(combines),
                    "total_accounts": total_accounts, "risk_policy": getattr(risk_policy, "id", None),
                    "payout_timing": payout_timing, "markets": n_markets,
                    "flat_routing": bool(every and every[0] is not None and every[0][5]),
                    "share_trades_skipped_no_flat_account": (float(skipped / (routed + skipped))
                                                             if routed + skipped else float("nan")),
                    "routing": routing,
                    "mean_passed_over_per_routed_trade": (float(sum(x[4] for x in tallies) / routed)
                                                          if routed else float("nan")),
                    # D-339: the firm's cross-account rule and the flip stream, both recorded on every row
                    "cross_account_rule": bool(cross_account),
                    "hold_to_own_exit": (bool(hold_to_own_exit) or bool(cross_account)       # D-351: the effective holding
                                         or one_at_a_time is not None),                      # D-429
                    "one_at_a_time": one_at_a_time,                                          # D-429: the strict rule's gap
                    "share_trades_skipped_busy": float(skipped_busy / offered) if offered else float("nan"),
                    "share_trades_skipped_opposite": float(skipped_opp / offered) if offered else float("nan"),
                    "seat_frees": seat_frees,
                    "flip": flip is not None,
                    # D-384: a menu of brackets has no single edge (each bracket's is on the flip rows)
                    "flip_edge": float(getattr(spec, "net_edge", float("nan"))) if spec is not None else float("nan"),
                    "mean_funded_flips": float(flips / len(paths)) if (flip is not None and len(paths)) else float("nan"),
                    "share_flips_won": float(flips_won / flips) if flips else float("nan"),
                    "bankroll": bankroll, "horizon_days": horizon_days, "paths": n_paths,
                    **{k: v for k, v in summary.as_dict().items()
                       if k in ("median_log_growth", "share_log_growth_undefined", "mean_final_cash", "median_final_cash",
                                "p10_final_cash", "p90_final_cash", "ruin_probability", "mean_max_drawdown",
                                "p90_max_drawdown", "median_days_to_first_payout", "share_accounts_ever_paid",
                                "mean_accounts_funded", "mean_same_day_multi_breach_days", "share_trades_at_tier_cap",
                                "share_trades_unsized", "share_trades_stood_aside", "realised_to_intended_risk",
                                "realised_to_intended_capped_risk", "share_trades_need_exits", "share_trades_room_capped",
                                "share_combines_out_of_room")},
                    "share_paths_rtp_placed": float((c["rtp_placed_day"] >= 0).mean()),
                    "share_payouts_exposed": float(c["payouts_exposed"].sum() / req) if req else float("nan"),
                    "mean_payouts_denied": float(c["payouts_denied"].mean()),
                    "mean_combine_purchases": float(c["combine_purchases"].mean()),
                    "mean_max_combine_purchases_21d": float(c["max_combine_purchases_in_window"].mean()),
                    "mean_max_mll_breaches_21d": float(c["max_mll_breaches_in_window"].mean()),
                    "is_gate_row": shift == "lower_bound" and float(p) == GATE_ENFORCEMENT_P,
                }
                if funded_account_cls is not None:       # Q-47: named only when given, as the engine's provenance does
                    row["funded_account_cls"] = class_name(funded_account_cls)                         # Q-47
                if seam_kw:                              # Q-71: each named only when given
                    row.update(seam_columns(seam_kw))                                                   # Q-71
                if focused_trader is not None:          # D-495 (4): beside a verdict, never the gate (D-234)
                    row.update(ftp_columns(focused_trader, paths))
                    row["is_gate_row"] = False
                if purchase_budget is not None:          # D-501
                    row.update(budget_columns(purchase_budget, paths))
                if entry_kw:                             # D-630
                    row.update(entry_columns(paths, **entry_kw))
                if routing_rule is not None:             # D-568: recorded only when set, every recorded row unchanged
                    row["routing_rule"] = routing_rule
                if mean_block is not None:               # D-663: beside a verdict, never the gate; recorded only when set
                    row["mean_block"] = float(mean_block)
                    row["is_gate_row"] = False
                if path_hook is not None:
                    extra = dict(path_hook(shift, float(p), paths) or {})
                    clash = set(extra) & set(row)
                    if clash:
                        raise ValueError(f"path_hook may only add columns; it returned {sorted(clash)}")
                    row.update(extra)
                if row["is_gate_row"]:
                    passed = bool(np.isfinite(row["median_log_growth"]) and row["median_log_growth"] > 0)
                rows.append(row)
    finally:
        if pool is not None:
            pool.shutdown()
    return pd.DataFrame(rows), passed


__all__ = ["VENDORED_RUN_GATE_SHA256", "vendored_run_gate_sha256", "check_vendored_source", "PassThroughFundedAccount",
           "check_funded_account_cls", "class_name", "PassThroughCombineAccount", "check_combine_account_cls",
           "check_payout_lag_days", "check_household_closure", "seam_arguments", "seam_columns",
           "topstep_payout_lag_days", "gate_recomposition_problems", "GATE_MARKERS", "check_recorder",
           "recorder_arguments", "recorded_paths", "check_gate_counters", "run_gate"]
