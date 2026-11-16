"""The campaign gate of D-145: does a strategy-plus-protocol make money over time inside the contract?

    passes  <=>  median log growth (D-14) > 0
                 with the strategy's trade outcomes shifted down so their mean equals the one-sided 95 % lower
                 bound of e, fees, payout latency and the Responsible Trading Program consequences applied
                 (tier 2), and payouts from accounts showing the stacking pattern denied with probability 0 %
                 (tier 3; the operator's rule, D-234 -- D-145 had 25 %)

Everything else is reported beside it, never instead of it: the same campaign at the point estimate of e, at
enforcement probabilities 10 / 25 / 50 %, ruin, drawdown, latency, and the pattern's own measures.

The shift is in units of each trade's own risk: a trade that risked `risked` dollars gains `(lb - e) * risked`
dollars (a loss when lb < e), so the log's mean R moves from e to lb and its spread and ordering are untouched.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.outcomes.distribution import DayBlock

#: The gate's tier-3 denial probability -- 0 by the operator's rule (D-234; D-145 had 0.25) -- and the levels reported
#: beside it.
GATE_ENFORCEMENT_P = 0.0
ENFORCEMENT_LEVELS = (0.0, 0.10, 0.25, 0.50)


def shifted_blocks(blocks: Sequence[DayBlock], delta_r: float,
                   delta_by_rr: dict[float, float] | None = None) -> list[DayBlock]:
    """Every trade's P&L moved by `delta_r` times its own dollar risk; days without trades unchanged. A trade's MAE
    (D-156) is kept, and never below the loss it now closes at. With outcomes at several R (D-162), each R's outcomes
    move by that R's own delta (`delta_by_rr`, in R), and each R's MAE is floored at its new loss."""
    out = []
    for b in blocks:
        pnl = b.pnl + float(delta_r) * b.risked
        kw: dict = {"pnl": pnl, "mae": None if b.mae is None else np.maximum(b.mae, -pnl)}
        if b.r_by_rr is not None:
            if delta_by_rr is None or set(delta_by_rr) != set(b.r_by_rr):
                raise ValueError("outcomes at several R need a delta for each R (D-162): the gate shifts each R to "
                                 "its own lower bound")
            r = {k: v + float(delta_by_rr[k]) for k, v in b.r_by_rr.items()}
            kw["r_by_rr"] = r
            if b.mae_by_rr is not None:
                kw["mae_by_rr"] = {k: np.maximum(v, -r[k]) for k, v in b.mae_by_rr.items()}
        out.append(replace(b, **kw))
    return out


def mean_r(blocks: Sequence[DayBlock]) -> float:
    r = np.concatenate([b.pnl / b.risked for b in blocks if len(b)]) if any(len(b) for b in blocks) else np.zeros(0)
    return float(r.mean()) if r.size else float("nan")


class _GateDraws:
    """The gate's draws for one campaign, a path at a time (R11: a module-level class, so it pickles to a path worker).
    Called with a path's seed it builds that path's `SharedDayDraws` and returns its lockstep factories; it keeps each
    path's trade router so the row can count the trades routed and skipped. In a worker the routers stay there:
    `export_state` hands back their counts, in path order, and `import_state` takes them here."""

    def __init__(self, blk: list[DayBlock], *, protocol: Any, mode: str, sizing: Any, settlement: str,
                 markets: int | Sequence[str] | None, routing: str, cross_account: bool, flip: Any,
                 hold_to_own_exit: bool, one_at_a_time: float | None, routing_rule: str | None = None,
                 mean_block: float | None = None):
        self.blk = blk
        self.kw = dict(protocol=protocol, mode=mode, sizing=sizing, settlement=settlement, markets=markets,
                       route_able=(routing == "able"), cross_account=bool(cross_account), flip=flip,
                       hold_to_own_exit=bool(hold_to_own_exit),                                      # D-351
                       one_at_a_time=one_at_a_time)                                                  # D-429
        if routing_rule is not None:                  # D-568: only when set, so every recorded call is unchanged
            self.kw["routing_rule"] = routing_rule
        if mean_block is not None:                    # D-663: only when set, so every recorded call and state is unchanged
            self.kw["mean_block"] = float(mean_block)
        self.routers: list = []                       # D-159: trades skipped when no account was flat
        self.imported: list = []

    def __call__(self, s: int) -> tuple:
        from propedge.campaign.shared_days import SharedDayDraws

        sd = SharedDayDraws({0: self.blk}, seed=s, **self.kw)
        self.routers.append(sd.router)
        # the two factories and the day hook, which rotation's trade router needs (D-157); with a flip stream the flip
        # draw factory and the spec (D-339)
        return tuple(sd.lockstep_kwargs().values())

    @staticmethod
    def _tally(r: Any) -> tuple | None:
        if r is None:
            return None
        return (r.routed, r.skipped, getattr(r, "skipped_opposite", 0), getattr(r, "skipped_busy", 0),
                getattr(r, "passed_over", 0), r.times is not None)

    def export_state(self) -> list:
        return [self._tally(r) for r in self.routers]

    def __getstate__(self) -> dict:
        # a router holds its day table and the accounts' draws; what crosses to a worker is the counts so far
        return {**self.__dict__, "routers": [], "imported": self.tallies()}

    def import_state(self, state: list) -> None:
        self.imported.extend(state)

    def tallies(self) -> list:
        """Every path's router counts in path order -- (routed, skipped, skipped opposite, skipped busy, passed over,
        flat routing), None where the layout has no router."""
        return self.imported + self.export_state()


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
) -> tuple[pd.DataFrame, bool]:
    """Run the campaign at the point estimate and at the lower bound, at every enforcement level, on common random
    numbers (one seed for all). Returns one row per run and whether the gate row passes. `settlement` is how a trade
    that risks more than the room settles (D-156); None: `mae` when the blocks carry it, else `pessimistic`. `mode`
    is the account layout, `rotation` by default (D-157: each trade to the next live account, so accounts carry
    different trades; copying every trade to every account is not a candidate layout and is run only to reproduce a
    pre-D-157 result). `combines` is how many Combines run at once (the engine's default, one, unless a protocol
    declares more); `total_accounts` caps live accounts of both kinds together (D-34), None for no joint cap.
    `risk_policy` (D-147, D-162) sets each account's risk, R and trade limit by state; with blocks carrying outcomes at
    several R, `e_by_rr` and `lb_by_rr` give each R's edge and lower bound, and the lower-bound run shifts each R's
    outcomes by its own gap. `payout_timing` is when a funded account requests its payout (8284233,
    `propedge.contract.payout_timing`); None is the campaign's default, a request made after 5:00 PM CT whose next
    trading day is the Payout request day, left out of the new cycle. `markets` is how many markets the log trades (a
    count or the names), overriding the blocks' `DayBlock.markets` labels; None reads the labels. A log with more than
    one market is refused under `rotation` when its blocks carry no entry and exit times (no flat routing, D-159) and
    under `independent`, since either would stack several markets' overlapping positions in one account (audit
    2026-09-27, finding 5). Every row records the settlement, the mode, the number of Combines, the joint cap, the
    policy, the payout timing and the market count. `path_hook(shift, enforcement_p, paths)`, when given, returns extra
    columns for that run's row from its `LockstepPath`s (P-04's kill line 1 reads the Combine records there); it cannot
    change the gate's verdict. `rtp` is whether the Responsible Trading Program's placement and its consequences run
    (D-145's tier 2); D-289 puts them OFF in a gate's base case and reports the placement-on reading beside it, so a
    scorer passes its declared value for each arm and the row records it (`rtp`). The default keeps every earlier
    gate's record reproducible (D-301). `cross_account` (D-339; D-336 (iv)) turns on the firm's rule in routing -- no
    signal to any account while an opposite-side position is open on another -- and `flip` (D-339) is the flip
    stream's `FlipSpec`: the point arm runs it at its measured edge, the lower-bound arm at its own lower bound
    (`FlipSpec.shifted`), as the strategy's trades are. Every row records both (`cross_account_rule`, `flip`,
    `flip_edge`), the refused signals' share, the flips taken and won, and the protocol's seat switch.
    `hold_to_own_exit` (D-351): flat-account routing holds a routed position to its exit at the R its account trades
    (the blocks' per-R exits) without the rule; the rule implies it; every row records the effective value.
    `one_at_a_time` (D-429; the operator's R2, D-409): no trade while any account holds a position or within that many
    minutes of one closing; None (the default) routes as before; every row records it and the refused share.
    `routing_rule` (D-568): one of `shared_days.ROUTING_RULES`, the order in which rotation offers each trade to the
    accounts (every other routing check unchanged); None (the default) routes in the longest-waiting order as before,
    and only a set rule is recorded on the row (`routing_rule`).
    `workers` (R11): each campaign's paths split across that many processes, one pool for all of the call's campaigns,
    never more than the free memory carries (`lockstep.guarded_workers`, `memory_per_worker_gb` per worker, default
    `lockstep.WORKER_MEMORY_GB`); 1 (the default) runs in this process as before. The rows and the paths `path_hook`
    receives are bit-for-bit the same either way (`tests/test_parallel_paths.py`); the caller needs an
    `if __name__ == "__main__"` guard and picklable inputs.

    `focused_trader` (D-495 (4)): a `lockstep.FocusedTraderModel` -- Topstep's Focused Trader Program at a declared
    threshold and path -- runs on every arm, and every row gains the `ftp_*` columns (the model, the share of paths
    placed, the placement day, what a Corrective placement closed and denied, the pattern measures' maxima). It is read
    beside a verdict, never as it (D-234, D-495): with it on no row is the gate row and the returned flag is False.
    None (the default) runs none of it, and the rows are exactly as before (no `ftp_*` column).

    `purchase_budget` (D-501): `(K, window_days)`, the campaign's own restraint -- a Combine purchase or reset refused
    while its purchases and resets in the last `window_days` trading days have reached K (`lockstep`'s option) -- on
    every arm; every row then gains the `budget_*` columns (the budget, the days it alone refused a purchase, the resets
    it refused, the purchases and resets in its window at most). None (the default) runs none of it, and the rows are
    exactly as before (no `budget_*` column).

    `wallet_stop`, `pause_after_funded`, `seat_ramp` (D-630; `lockstep`'s three entry options, each the campaign's own
    restraint on buying Combines): W dollars -- no purchase while the cash out of pocket is above W; F -- none at a
    purchase step where the campaign holds at least F funded accounts and its first payout has not arrived (D-632's
    wording, no latch); s0 -- s0 seats at first and one more for each payout arrived, up to `total_accounts`, which
    the ramp needs. Each runs on every arm, and every row then
    gains that option's columns (`entry_columns`); as with the budget its rows stay gate rows. None (the default) runs
    none of it, and the rows are exactly as before (no `wallet_stop_*`, `pause_*` or `seat_ramp_*` column).

    `mean_block` (D-663): every path's calendar drawn by the stationary bootstrap of days at that mean block length in
    sessions (`shared_days.StationaryDayTable`; rotation only) in place of one independent draw a day, on every arm. It
    is read beside a verdict, never as it: with it set no row is the gate row and the returned flag is False, and every
    row records it (`mean_block`). None (the default) draws as before, and the rows are exactly as before (no
    `mean_block` column)."""
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING, check_payout_timing
    from propedge.outcomes.settlement import default_trade_log_settlement

    payout_timing = check_payout_timing(DEFAULT_PAYOUT_TIMING if payout_timing is None else payout_timing)
    settlement = settlement or default_trade_log_settlement(list(blocks))
    from propedge.campaign.lockstep import ConductModel, simulate_lockstep_campaign
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

                summary, paths = simulate_lockstep_campaign(
                    protocol, edge=0.0, seed=seed, rules=rules, initial_bankroll=bankroll, horizon_days=horizon_days,
                    n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=accounts,
                    max_concurrent_combines=int(combines), max_total_accounts=total_accounts,
                    require_verified_cap=False, ledger=ledger, conduct=conduct, risk_policy=risk_policy,
                    draw_factories_for_path=draws, payout_timing=payout_timing,
                    workers=n_workers, pool=pool,                                                       # R11
                    **ftp_kw,                                                                           # D-495 (4)
                )
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
                if focused_trader is not None:           # D-495 (4): beside a verdict, never the gate (D-234)
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


# ------------------------------------------------------------------------- the Focused Trader Program (D-495 (4))


def ftp_columns(model: Any, paths: Sequence[Any]) -> dict[str, Any]:
    """D-495 (4): one run's Focused Trader Program columns from its `LockstepPath`s' `focused_trader` records -- the
    declared model, the share of paths placed (on each path), the median placement day of the placed paths, and per
    path the placements, what a Corrective placement closed and denied, the purchases and resets the program refused,
    and the pattern measures' rolling maxima."""
    recs = [dict(getattr(x, "focused_trader", None) or {}) for x in paths]
    n = len(recs)

    def mean(key: str) -> float:
        return float(np.mean([float(r.get(key, 0) or 0) for r in recs])) if n else float("nan")

    first = [r["placements"][0] for r in recs if r.get("placements")]
    days = [int(p["day"]) for p in first]
    return {
        "ftp_label": model.label, "ftp_path": model.path, "ftp_window_days": int(model.window_days),
        "ftp_combine_purchases": (float(model.combine_purchases) if model.combine_purchases is not None
                                  else float("nan")),
        "ftp_funded_lost": float(model.funded_lost) if model.funded_lost is not None else float("nan"),
        "ftp_account_limit": int(model.account_limit), "ftp_corrective_days": int(model.corrective_days),
        "ftp_repeat": bool(model.repeat),
        "share_paths_ftp_placed": float(len(first) / n) if n else float("nan"),
        "share_paths_ftp_slowdown": float(sum(p["path"] == "slowdown" for p in first) / n) if n else float("nan"),
        "share_paths_ftp_corrective": float(sum(p["path"] == "corrective" for p in first) / n) if n else float("nan"),
        "ftp_first_placed_day_p50": float(np.median(days)) if days else float("nan"),
        "mean_ftp_placements": (float(np.mean([len(r.get("placements") or ()) for r in recs])) if n
                                else float("nan")),
        **{f"mean_ftp_{k}": mean(k) for k in ("combines_closed", "funded_closed", "passes_removed", "payouts_denied",
                                               "payout_cash_denied", "purchase_days_blocked", "resets_refused",
                                               "max_combine_purchases_in_window", "max_funded_lost_in_window")},
    }


def budget_columns(budget: tuple[int, int], paths: Sequence[Any]) -> dict[str, Any]:
    """D-501: one run's purchase-budget columns from its `LockstepPath`s' `purchase_budget` records -- the budget, and
    per path the days the budget alone refused a purchase, the resets it refused, the purchases and resets taken and
    their most in any window of the budget's length."""
    recs = [dict(getattr(x, "purchase_budget", None) or {}) for x in paths]
    n = len(recs)

    def mean(key: str) -> float:
        return float(np.mean([float(r.get(key, 0) or 0) for r in recs])) if n else float("nan")

    return {"budget_k": int(budget[0]), "budget_window_days": int(budget[1]),
            "mean_budget_purchase_days_blocked": mean("purchase_days_blocked"),
            "mean_budget_resets_refused": mean("resets_refused"),
            "mean_budget_purchases_and_resets": mean("purchases_and_resets"),
            "max_budget_purchases_in_window": (int(max(int(r.get("max_purchases_in_window", 0)) for r in recs))
                                               if n else 0)}


def entry_columns(paths: Sequence[Any], *, wallet_stop: float | None = None, pause_after_funded: int | None = None,
                  seat_ramp: int | None = None) -> dict[str, Any]:
    """D-630: one run's columns for each entry option that is on, from its `LockstepPath`s' `wallet_stop`,
    `pause_after_funded` and `seat_ramp` records -- the option's value, and per path the days it alone refused a
    purchase, the resets it refused and what became of it (a stop that became final; a pause that refused, its spells
    and how often purchases resumed with fewer than F funded accounts held; the seats the ramp ended on). An option
    that is off (None) adds no column."""
    n = len(paths)

    def recs(name: str) -> list[dict[str, Any]]:
        return [dict(getattr(x, name, None) or {}) for x in paths]

    def mean(rs: list[dict[str, Any]], key: str) -> float:
        return float(np.mean([float(r.get(key, 0) or 0) for r in rs])) if n else float("nan")

    def share(rs: list[dict[str, Any]], key: str) -> float:
        return float(np.mean([int(r.get(key, -1)) >= 0 for r in rs])) if n else float("nan")

    out: dict[str, Any] = {}
    if wallet_stop is not None:
        rs = recs("wallet_stop")
        out.update({
            "wallet_stop_w": float(wallet_stop),
            "mean_wallet_stop_purchase_days_blocked": mean(rs, "purchase_days_blocked"),
            "mean_wallet_stop_resets_refused": mean(rs, "resets_refused"),
            "share_paths_wallet_stop_bound": share(rs, "first_blocked_day"),
            "share_paths_wallet_stop_final": share(rs, "final_on"),
            "share_paths_wallet_stop_on_at_end": mean(rs, "on_at_end"),
            "max_wallet_stop_out_of_pocket_at_purchase": (
                float(max(float(r.get("max_out_of_pocket_at_purchase", 0.0)) for r in rs)) if n else float("nan"))})
    if pause_after_funded is not None:
        rs = recs("pause_after_funded")
        waits = [int(r["released_on"]) - int(r["paused_on"]) for r in rs
                 if int(r.get("paused_on", -1)) >= 0 and int(r.get("released_on", -1)) >= 0]
        out.update({
            "pause_after_funded_f": int(pause_after_funded),
            "mean_pause_purchase_days_blocked": mean(rs, "purchase_days_blocked"),
            "mean_pause_resets_refused": mean(rs, "resets_refused"),
            "share_paths_pause_begun": share(rs, "paused_on"),
            "share_paths_pause_released": share(rs, "released_on"),
            "mean_pause_in_force_days": mean(rs, "in_force_days"),
            "mean_pause_spells": mean(rs, "spells"),
            "mean_pause_resumed_below_f": mean(rs, "resumed_below_f"),
            "pause_days_p50": float(np.median(waits)) if waits else float("nan")})
    if seat_ramp is not None:
        rs = recs("seat_ramp")
        out.update({
            "seat_ramp_s0": int(seat_ramp),
            "mean_seat_ramp_purchase_days_blocked": mean(rs, "purchase_days_blocked"),
            "mean_seat_ramp_seats_at_end": mean(rs, "seats_at_end"),
            "share_paths_seat_ramp_full": share(rs, "full_on")})
    return out


def ftp_models(paths: Sequence[str] = ("slowdown", "corrective"), *, combine_purchases: Sequence[int] = (),
               funded_lost: Sequence[int] = (), window_days: int = 21, **kw: Any) -> list[Any]:
    """D-495 (4): a declared grid of Focused Trader Program models -- each threshold of each measure watched alone, on
    each path (path-major, purchases before losses); `kw` passes to every `FocusedTraderModel` (account limit, the
    Corrective's days, `repeat`)."""
    from propedge.campaign.lockstep import FocusedTraderModel

    out = []
    for p in paths:
        out += [FocusedTraderModel(path=p, combine_purchases=int(t), window_days=int(window_days), **kw)
                for t in combine_purchases]
        out += [FocusedTraderModel(path=p, funded_lost=int(t), window_days=int(window_days), **kw) for t in funded_lost]
    return out


def ftp_sweep(blocks: Sequence[DayBlock], models: Sequence[Any], *, include_off: bool = True,
              path_hook: Any = None, margin: float | None = None, block_days: int | None = None,
              on_run: Any = None, **run_gate_kwargs: Any) -> pd.DataFrame:
    """D-495 (4): one campaign -- `run_gate`'s arguments in `run_gate_kwargs` -- without the Focused Trader Program
    (`include_off`, labelled "off") and under each declared model, on common random numbers (the same seed). Returns
    every run's rows with `ftp_label`, and the scoreboard's reading on each: `growth_on_required` (growth on the
    bankroll the run itself required, `pf_growth_on_base_p50` at `pf_required_p90`, D-312) at the point and at the
    bound, `required_p90`, and the share of paths placed on each path. Read beside a verdict, never as it (D-234):
    no row of a model is a gate row.

    `path_hook`: the caller's (it must give `pf_growth_on_base_p50` and `pf_required_p90`, as
    `portfolio_stage.composed_hook` does); None uses `portfolio.hook` at `margin` and `block_days` (its defaults when
    None). `on_run(label)`, when given, is called before each run (a per-path record names its run there). `levels`
    defaults to the gate's 0 % alone."""
    from propedge.campaign import portfolio as pf

    if path_hook is None:
        path_hook = pf.hook(margin=pf.DEFAULT_MARGIN if margin is None else float(margin),
                            block=pf.BLOCK_DAYS if block_days is None else int(block_days))
    run_gate_kwargs.setdefault("levels", (GATE_ENFORCEMENT_P,))
    if "focused_trader" in run_gate_kwargs:
        raise ValueError("ftp_sweep sets focused_trader itself: pass the models")
    out = []
    for m in ([None] if include_off else []) + list(models):
        label = "off" if m is None else m.label
        if on_run is not None:
            on_run(label)
        df, _ = run_gate(blocks, path_hook=path_hook, focused_trader=m, **run_gate_kwargs)
        missing = [c for c in ("pf_growth_on_base_p50", "pf_required_p90") if c not in df.columns]
        if missing:
            raise ValueError(f"the path hook gave no {missing}: the sweep reads growth on the required bankroll")
        if m is None:
            df["ftp_label"] = "off"
            df["ftp_path"] = "off"
            for c in ("share_paths_ftp_placed", "share_paths_ftp_slowdown", "share_paths_ftp_corrective"):
                df[c] = 0.0
        df["growth_on_required"] = df["pf_growth_on_base_p50"]
        df["required_p90"] = df["pf_required_p90"]
        out.append(df)
    return pd.concat(out, ignore_index=True)


__all__ = ["GATE_ENFORCEMENT_P", "ENFORCEMENT_LEVELS", "shifted_blocks", "mean_r", "run_gate", "ftp_columns",
           "budget_columns", "entry_columns", "ftp_models", "ftp_sweep"]
