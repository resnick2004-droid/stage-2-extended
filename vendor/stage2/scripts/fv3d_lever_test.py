"""EXPLORATORY (D-365, D-368): FV3-D's lever tests on the development years -- the number of accounts sharing the
signals (D-365); the XFA's collect phase (D-368: from a balance T, a take-profit at the shortfall to the winning-day
minimum); an XFA's second trade on a day its first left short of the minimum (D-368, built, tested after) -- by the
procedure D-365 fixed before any run.

    python scripts/fv3d_lever_test.py --period identity          # must reproduce fv3_corrected_v1 first
    python scripts/fv3d_lever_test.py --period choice            # N = 3, 4, 5 on 2021-2023
    python scripts/fv3d_lever_test.py --period check             # the CHOICE winner and N = 5 on 2024 to June 2025
    python scripts/fv3d_lever_test.py --lever collect_from --period identity|choice|check   # off (-1), T = 500/1000/2000
    python scripts/fv3d_lever_test.py --lever second_trade --period identity|choice|check   # off (0) and on (1)
    python scripts/fv3d_lever_test.py --lever a3_filter --period identity|choice|check      # off (0) and on (1)
    python scripts/fv3d_lever_test.py --lever table_collect --period identity|choice|check  # v12 (0) and v17 (1)
    python scripts/fv3d_lever_test.py --lever collect_menu --period identity|y2021|...|y2025h1  # v12 (0), v18 + stream (1)
    python scripts/fv3d_lever_test.py --lever collect_menu --wfo        # D-382 (A): the folds and the keep rule
    python scripts/fv3d_lever_test.py --lever speed_first --period identity|y2021|...|y2025h1   # FV3-C (0), SPEED-2 1-3
    python scripts/fv3d_lever_test.py --lever speed_first --wfo --rule payouts   # D-395: the operator's speed-first rule
    python scripts/fv3d_lever_test.py --lever steady --period identity    # D-402: FV3-C's steadiness baseline (FV3-S, T22)
    python scripts/fv3d_lever_test.py --lever steady --period y2021 --prereg P-xx   # D-405: FV3-S's tables, registered only

FV3-C exactly as frozen (`config/fv3_corrected_portfolio.yaml`) with one lever set: `accounts` sets only
`gate.campaign.accounts` and `.combines` to N; `collect_from` sets only `fidelity.xfa_collect_from` to T dollars (-1:
not declared, FV3-C as frozen); `second_trade` sets only `fidelity.xfa_second_trade` (0 off, 1 on). Its development
trades are rebuilt as the scorer built them (`fv3_xfa_time_budget.rebuild_trades`, checked equal to the run's
`gate_inputs`). In a period, the trades of that period's days only; each R's net edge and its one-sided 95 % t bound
over the period's 21-session blocks (P-06's rule, `confirm_fv3.edge_stats`); the policy cell nearest the funded leg's
bound (`policy_for_edge`, the frozen rule); the campaign (`portfolio_stage.run_campaign`: 500 paths over 504 days
resampled from the period's days, seed 20261019, placement off) at 0 and 10 % denial, both arms, with the portfolio
measures (`composed_hook`) and the collect-phase and second trades beside them.

* `identity`: every development day, the development scorer's YEARLY bound, the lever at its baseline (N = 5; the
  collect phase not declared; the second trade declared off) -- each row must equal `results/fv3_corrected_v1.csv`'s
  placement-off row at the same arm and denial, or the script refuses.
* `choice`: 2021-01-01 to 2023-12-31, every value. The measure: the lower-bound arm's growth on its required bankroll
  at 0 % denial (`pf_growth_on_base_p50`).
* `check`: 2024-01-01 to 2025-06-30, the CHOICE winner and the baseline. **The rule (D-365 (4)):** the winner is kept
  only if it also beats the baseline on CHECK; otherwise FV3-C's setting stays.
* D-382 (A), from the collect menu on (D-384): `y2021` ... `y2024`, `y2025h1` -- every value, one campaign a year (the
  period's own days, edge and bound, P-06's 21-session blocks); `--wfo` reads them and applies the anchored yearly
  walk-forward: four folds (choose on 2021 and test 2022, 2021-2022 and 2023, 2021-2023 and 2024, 2021-2024 and 2025
  H1), each fold's pick the best mean of its choice years (a tie keeps the baseline); kept only if the picks agree in
  at least three folds, the pick beats the baseline in at least three test segments, and the stitched test reading
  (the picks' mean over the four segments) beats the baseline's.

Writes results/fv3d_levers_<lever>_<period>.csv with its manifest; each configuration is recorded in
results/variants.jsonl under the family `fv3d_levers` (D-365 (6)).
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign import steadiness as st  # noqa: E402

SCRIPT = "scripts/fv3d_lever_test.py"
CONFIG = ROOT / "config" / "fv3_corrected_portfolio.yaml"
RUN = "fv3_corrected_v1"
PERIODS = {"identity": (None, None), "choice": ("2021-01-01", "2023-12-31"), "check": ("2024-01-01", "2025-06-30"),
           "y2021": ("2021-01-01", "2021-12-31"), "y2022": ("2022-01-01", "2022-12-31"),     # D-382 (A): a year each
           "y2023": ("2023-01-01", "2023-12-31"), "y2024": ("2024-01-01", "2024-12-31"),
           "y2025h1": ("2025-01-01", "2025-06-30")}
VALUES = (3, 4, 5)
BASELINE = 5
OFF = -1                                             # D-368: the collect phase not declared (FV3-C as frozen)
# D-368: each lever's values, the baseline FV3-C carries and the decision that declared it
LEVERS = {"accounts": {"values": VALUES, "baseline": BASELINE, "decision": "D-365"},
          "collect_from": {"values": (OFF, 500, 1000, 2000), "baseline": OFF, "decision": "D-368"},
          "second_trade": {"values": (0, 1), "baseline": 0, "decision": "D-368"},
          "a3_filter": {"values": (0, 1), "baseline": 0, "decision": "D-377"},
          "table_collect": {"values": (0, 1), "baseline": 0, "decision": "D-379"},
          "collect_menu": {"values": (0, 1), "baseline": 0, "decision": "D-384"},
          "after_win": {"values": (0, 1, 2), "baseline": 0, "decision": "D-390"},
          "speed_first": {"values": (0, 1, 2, 3), "baseline": 0, "decision": "D-395"},
          # D-402: FV3-S (T22) -- FV3-C as frozen at 0, the steadiness baseline; D-405: 1, 2, 3 the tables under
          # exponential utility (versions 19, 20, 21), run only under a registered pre-registration (`--prereg`)
          "steady": {"values": (0, 1, 2, 3), "baseline": 0, "decision": "D-405"}}
#: D-405: the steady lever's tables by value (0 is FV3-C's v12 as frozen)
STEADY_TABLES = {v: {"file": f"results/state_policy_v{18 + v}.csv",
                     "policies_json": f"results/state_policy_v{18 + v}_policies.json"} for v in (1, 2, 3)}
#: D-390: the after-win layer's modes by the lever's value (0 is FV3-C as frozen)
AFTER_WIN = {1: "speed", 2: "growth"}
#: D-395: the speed-first layer's bracket after a payout by the lever's value (0 is FV3-C as frozen)
SPEED_FIRST = {1: "2x", 2: "1x", 3: "adaptive"}
DAYS = "median_days_to_first_payout"
#: D-395: the operator's speed-first rule -- the payouts a path collects, and the required bankroll as its guardrail
PAYOUTS = "mean_payouts_per_path"
BANK = "pf_required_p90"
#: D-379: the state table with the funded menu's collect action (export v17) in place of FV3-C's (v12)
COLLECT_TABLE = {"file": "results/state_policy_v17.csv", "policies_json": "results/state_policy_v17_policies.json"}
#: D-384: the state table with the collect menu (export v18) and the collect stream the engine draws from, priced on the
#: period's own years (`years`, set per run)
MENU_TABLE = {"file": "results/state_policy_v18.csv", "policies_json": "results/state_policy_v18_policies.json"}
MENU_STREAM = {"source": "collect_map", "map_file": "results/collect_map_nq.csv",
               "counts_file": "results/manual_R145_collect_NQ.csv", "spread_file": "results/manual_R137_flipmap_NQ.csv",
               "copy": True, "table_config": "config/state_policy_v18.yaml"}
#: D-382 (A): the anchored folds -- (choice periods, test period)
FOLDS = ((("y2021",), "y2022"), (("y2021", "y2022"), "y2023"), (("y2021", "y2022", "y2023"), "y2024"),
         (("y2021", "y2022", "y2023", "y2024"), "y2025h1"))
LEVELS = (0.0, 0.10)
MEASURE = "pf_growth_on_base_p50"
COMPARE = ("median_final_cash", "mean_final_cash", "share_accounts_ever_paid", "mean_accounts_funded",
           "mean_combine_purchases", "pf_growth_on_base_p50", "pf_required_p90", "pf_net_p50")
BESIDE = ("pf_net_p50", "pf_required_p90", "pf_cash_per_slot_day_p50", "share_accounts_ever_paid",
          "median_days_to_first_payout", "pf_slot_days_per_xfa", "pf_slot_days_per_attempt", "mean_accounts_funded",
          "mean_combine_purchases", "share_trades_skipped_no_flat_account", "share_trades_skipped_opposite",
          "mean_same_day_multi_breach_days", "mean_collect_trades", "share_collect_qualified", "mean_second_trades",
          "share_seconds_qualified", "a3_trades_rth", "a3_aligned_n", "a3_counter_n", "a3_aligned_mean_r1",
          "a3_counter_mean_r1", "a3_trades_kept", "mean_collect_brackets", "share_collect_brackets_won",
          "given_back_mean", "given_back_p90", "share_xfa_paid_given_back_over_500", PAYOUTS,
          "median_payouts_per_path", "mean_payout_gross", "share_paid_xfa_closed",
          *st.columns())                                     # D-402, D-403: the steadiness measures


def with_accounts(cfg: dict, n: int) -> dict:
    """FV3-C's config with N accounts: the accounts, the Combines at once and the joint cap (D-365 (2))."""
    out = copy.deepcopy(cfg)
    out["gate"]["campaign"]["accounts"] = int(n)
    out["gate"]["campaign"]["combines"] = int(n)
    return out


def with_collect_from(cfg: dict, T: int) -> dict:
    """D-368: FV3-C's config with the collect phase from a balance of T dollars; OFF leaves it undeclared."""
    out = copy.deepcopy(cfg)
    if int(T) != OFF:
        out["fidelity"]["xfa_collect_from"] = float(T)
    return out


def with_second_trade(cfg: dict, on: int) -> dict:
    """D-368: FV3-C's config with the second-trade switch declared -- off (0) or on (1); nothing else."""
    out = copy.deepcopy(cfg)
    out["fidelity"]["xfa_second_trade"] = bool(int(on))
    return out


def configure(cfg: dict, lever: str, value: int, years: list[int] | None = None) -> dict:
    if lever == "accounts":
        return with_accounts(cfg, value)
    if lever == "collect_from":
        return with_collect_from(cfg, value)
    if lever == "second_trade":
        return with_second_trade(cfg, value)
    if lever == "a3_filter":
        return copy.deepcopy(cfg)                    # D-377: the filter acts on the trades (`a3_filter_trades`), not the config
    if lever == "steady":                            # D-405: v12 for 0; the exponential-utility table for 1, 2, 3
        out = copy.deepcopy(cfg)
        if int(value) != 0:
            out["state_policy"].update(STEADY_TABLES[int(value)])
        return out
    if lever == "table_collect":                     # D-379: v17's table (the collect action) for 1; FV3-C's v12 for 0
        out = copy.deepcopy(cfg)
        if int(value) == 1:
            out["state_policy"].update(COLLECT_TABLE)
        return out
    if lever == "after_win":                         # D-390: FV3-C's table with the after-win layer (speed 1, growth 2)
        out = copy.deepcopy(cfg)
        mode = AFTER_WIN.get(int(value))
        if mode is not None:
            out["after_win"] = {"mode": mode}
        if mode == "speed":
            if not years:
                raise ValueError("the collect stream is priced on the period's own years (D-390 (3))")
            out.setdefault("streams", {})["flip"] = {**{k: v for k, v in MENU_STREAM.items() if k != "table_config"},
                                                     "years": [int(y) for y in years]}
        return out
    if lever == "speed_first":                       # D-395: FV3-C's table with the speed-first layer (1, 2, 3)
        out = copy.deepcopy(cfg)
        post = SPEED_FIRST.get(int(value))
        if post is not None:
            if not years:
                raise ValueError("the collect stream is priced on the period's own years (D-395 (4))")
            out["after_win"] = {"mode": "speed_first", "post_payout": post}
            out.setdefault("streams", {})["flip"] = {**{k: v for k, v in MENU_STREAM.items() if k != "table_config"},
                                                     "years": [int(y) for y in years]}
        return out
    if lever == "collect_menu":                      # D-384: v18's table and the collect stream for 1; FV3-C's v12 for 0
        out = copy.deepcopy(cfg)
        if int(value) == 1:
            if not years:
                raise ValueError("the collect stream is priced on the period's own years (D-384 (3))")
            out["state_policy"].update(MENU_TABLE)
            out.setdefault("streams", {})["flip"] = {**MENU_STREAM, "years": [int(y) for y in years]}
        return out
    raise ValueError(f"unknown lever {lever!r}")


A3_FILE = "manual_R143_flipany_NQ.csv"
A3_FIRST, A3_STEP, A3_END = 930, 30, 1320            # R143's slots: 08:30 to 14:30 CT every half hour; the session ends 15:00


def a3_signs(rd: Path | None = None) -> dict[tuple[str, int], int]:
    """D-377: A3's sign (D-374: the last sixty minutes' move) per (date, slot on the minute clock) from R143's record."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    a = read_result((Path(rd) if rd is not None else RESULTS_DIR) / A3_FILE)
    out = {}
    for d, i, m in zip(a["date"].astype(str), a["slot_index"].astype(int), a["a3_last60"]):
        if m == m and m is not None:
            out[(d, A3_FIRST + A3_STEP * int(i))] = int(np.sign(float(m)))
    return out


def a3_split(t: pd.DataFrame, signs: dict[tuple[str, int], int]) -> pd.Series:
    """D-377: per trade +1 when its side agrees with A3 at the latest half-hour mark at or before its entry, -1 when it
    disagrees, 0 when there is no such mark (before 08:30 or from 15:00 CT), no record, or no move."""
    side = np.where(t["side"].astype(str) == "long", 1, -1)
    e = t["entry_t"].astype(float).to_numpy()
    out = np.zeros(len(t), int)
    for i, (d, x, sd) in enumerate(zip(t["date"].astype(str), e, side)):
        if A3_FIRST <= x < A3_END:
            s = signs.get((d, int(A3_FIRST + A3_STEP * ((x - A3_FIRST) // A3_STEP))), 0)
            out[i] = 0 if s == 0 else (1 if s == sd else -1)
    return pd.Series(out, index=t.index)


def a3_filter_trades(t: pd.DataFrame, signs: dict[tuple[str, int], int]) -> pd.DataFrame:
    """D-377: the trades without those that go against A3 (`a3_split` -1); the evening, the night and every trade
    without a reading are kept."""
    return t[a3_split(t, signs) >= 0].reset_index(drop=True)


def lever_hook(base):
    """D-368: the portfolio hook plus the collect-phase and second trades -- per path, and the share of them that made
    the day a winning day -- from each path's XFA records."""
    def _hook(shift: str, p: float, paths) -> dict[str, float]:
        out = base(shift, p, paths)
        for mean_col, share_col, trades, won in (
                ("mean_collect_trades", "share_collect_qualified", "collect_trades", "collect_qualified"),
                ("mean_second_trades", "share_seconds_qualified", "second_trades", "second_qualified")):
            per = [sum(int(getattr(r, trades, 0)) for r in x.funded) for x in paths]
            ok = sum(int(getattr(r, won, 0)) for x in paths for r in x.funded)
            out[mean_col] = float(np.mean(per)) if per else float("nan")
            out[share_col] = ok / sum(per) if sum(per) else float("nan")
        # D-384: the collect brackets a path takes and the share at the target; the secured balance given back per XFA
        per = [sum(int(getattr(r, "flips", 0)) for r in x.funded) for x in paths]
        won = sum(int(getattr(r, "flips_won", 0)) for x in paths for r in x.funded)
        out["mean_collect_brackets"] = float(np.mean(per)) if per else float("nan")
        out["share_collect_brackets_won"] = won / sum(per) if sum(per) else float("nan")
        gb = np.array([float(r.given_back) for x in paths for r in x.funded if hasattr(r, "given_back")], float)
        paid = np.array([float(r.given_back) for x in paths for r in x.funded
                         if hasattr(r, "given_back") and int(getattr(r, "n_payouts", 0)) > 0], float)
        out["given_back_mean"] = float(gb.mean()) if gb.size else float("nan")
        out["given_back_p90"] = float(np.percentile(gb, 90)) if gb.size else float("nan")
        out["share_xfa_paid_given_back_over_500"] = float(np.mean(paid > 500.0)) if paid.size else float("nan")
        # D-395: the payouts each path collects, their mean size, and the paid XFAs that ended closed
        npay = np.array([sum(int(r.n_payouts) for r in x.funded) for x in paths], float)
        gross = float(sum(float(r.gross_paid) for x in paths for r in x.funded))
        out[PAYOUTS] = float(npay.mean()) if npay.size else float("nan")
        out["median_payouts_per_path"] = float(np.median(npay)) if npay.size else float("nan")
        out["mean_payout_gross"] = gross / npay.sum() if npay.sum() else float("nan")
        closed = [bool(r.closed) for x in paths for r in x.funded if int(r.n_payouts) > 0]
        out["share_paid_xfa_closed"] = float(np.mean(closed)) if closed else float("nan")
        out.update(st.measures(paths))                                  # D-402, D-403: the steadiness measures
        return out
    if hasattr(base, "state"):
        _hook.state = base.state                                        # type: ignore[attr-defined]
    return _hook


def in_period(t: pd.DataFrame, days: list[str], lo: str | None, hi: str | None) -> tuple[pd.DataFrame, list[str]]:
    """The trades and trading days inside [lo, hi] (all when unbounded)."""
    keep = [d for d in days if (lo is None or d >= lo) and (hi is None or d <= hi)]
    ks = set(keep)
    return t[t["date"].astype(str).isin(ks)].reset_index(drop=True), keep


def period_stats(t: pd.DataFrame, days: list[str], menu: list[float], rule: str) -> dict[float, dict[str, float]]:
    """Each R's net edge and bound: `blocks21` (P-06's 21-session blocks) or `yearly` (the development scorer's)."""
    import confirm_fv3 as cf
    import score_orb5_grid as g5

    if rule == "blocks21":
        return cf.edge_stats(t, menu, days, 21, None)
    out = {}
    for R in menu:
        v = t[f"r_{R:g}"].dropna()
        by = v.groupby(t.loc[v.index, "year"]).mean()
        out[float(R)] = {"e": float(v.mean()), "lb": g5.bound(by), "n": int(len(v))}
    return out


def decide(choice: pd.DataFrame, check: pd.DataFrame | None, baseline: int = BASELINE) -> dict:
    """D-365 (4): the CHOICE winner by the measure; kept only if it beats the baseline on CHECK."""
    def gate(df: pd.DataFrame) -> pd.Series:
        g = df[(df["shift"] == "lower_bound") & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        return g.set_index(g["value"].astype(int))[MEASURE].astype(float).sort_index()
    c = gate(choice)
    winner = int(c.idxmax())
    out = {"winner": winner, "choice_measure": float(c[winner]), "choice_baseline": float(c[baseline])}
    if check is not None:
        k = gate(check)
        out.update({"check_measure": float(k[winner]), "check_baseline": float(k[baseline]),
                    "kept": bool(winner != baseline and k[winner] > k[baseline])})
    return out


def run_one(cfg: dict, n: int, t: pd.DataFrame, days: list[str], tv: float, rule: str,
            lever: str = "accounts", sink: list | None = None, label: str = "") -> pd.DataFrame:
    """One setting's campaign on the period's trades and days. With `sink` (D-392) every path's record is appended to
    it under `label`, as the scorer's per-path record (D-310)."""
    import portfolio_stage as ps
    import score_fv3_grid as gf

    c = configure(cfg, lever, n, sorted({int(str(d)[:4]) for d in days}))
    a3 = {}
    if lever == "a3_filter":                         # D-377: the split beside, and the filter when on
        signs = a3_signs()
        sp = a3_split(t, signs)
        r1 = t["r_1"].astype(float)
        a3 = {"a3_trades_rth": int((sp != 0).sum()), "a3_aligned_n": int((sp > 0).sum()),
              "a3_counter_n": int((sp < 0).sum()), "a3_aligned_mean_r1": float(r1[sp > 0].mean()),
              "a3_counter_mean_r1": float(r1[sp < 0].mean())}
        if int(n) == 1:
            t = a3_filter_trades(t, signs)
        a3["a3_trades_kept"] = int(len(t))
    menu = [float(R) for R in gf.rr_menu(c)]
    stats = period_stats(t, days, menu, rule)
    f = gf.fidelity_of(c)
    blocks, n_used = gf.gate_blocks(t, days, tv, menu, require_sides=bool(f.get("cross_account_rule", False)),
                                    require_exits=bool(f.get("hold_to_own_exit", False)))
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    fr = float(c["state_policy"]["fresh"]["funded_rr"])
    if not np.isfinite(stats[fr]["lb"]):
        raise SystemExit("REFUSED: the funded leg's bound is undefined in this period.")
    policy, e_used, pid = gf.policy_for_edge(c, stats[fr]["lb"])
    if c.get("after_win"):                           # D-390: the after-win layer over the table's policy
        from propedge.campaign.after_win import SPEED_FIRST as SF, AfterWinPolicy, brackets_of

        aw = c["after_win"]
        extra = ({"post_payout": str(aw["post_payout"]), "brackets": brackets_of(gf.flip_spec_of(c))}
                 if aw["mode"] == SF else {})            # D-395: the stream's own brackets and full losses
        policy = AfterWinPolicy.over(policy, str(aw["mode"]), **extra)
        pid = policy.id
    if lever == "steady" and int(n) != 0:            # D-405: the table's version beside v12's cell id
        _, e_v12, _ = gf.policy_for_edge(cfg, stats[fr]["lb"])
        if not np.isclose(float(e_used), float(e_v12)):
            raise SystemExit(f"REFUSED (D-405): the bound reads the cell {e_used:+.3f} of table v{18 + int(n)} but "
                             f"{e_v12:+.3f} of v12 -- that cell is not solved for FV3-S; solve it by its own row.")
        pid = f"{pid}_v{18 + int(n)}"
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    camp = c["gate"]["campaign"]
    hook = lever_hook(ps.composed_hook(c["portfolio"], sink=sink))
    hook.state["label"] = label
    df = ps.run_campaign(blocks, c, int(c["seeds"]["gate"]), tv, policy, e=e_by[fr], lb=lb_by[fr], e_by=e_by,
                         lb_by=lb_by, levels=LEVELS, n_paths=int(camp["n_paths"]), horizon=int(camp["horizon_days"]),
                         hook=hook, rtp=False)
    df.insert(0, "value", int(n))
    df.insert(0, "lever", lever)
    df["policy_id"], df["policy_edge"], df["bound_rule"] = pid, e_used, rule
    df["trades"], df["days"], df["first_day"], df["last_day"] = len(t), len(days), days[0], days[-1]
    df["e_funded"], df["lb_funded"] = e_by[fr], lb_by[fr]
    for k, v in a3.items():
        df[k] = v
    return df


def wfo(lever: str, rd: Path, base: int, values: list[int] | None = None, rule: str = "money") -> pd.DataFrame:
    """D-382 (A): the anchored yearly walk-forward from the per-year files -- per fold the pick (the best mean of its
    choice years on the measure, a tie keeping the baseline), its in-sample and test readings beside the baseline's,
    and the keep rule's three lines with their values; the per-year readings beside. `values` restricts the settings
    compared (the baseline always among them); D-390's `speed` rule picks by the fewer median days to the first payout
    and keeps a pick that is faster in three test years of four and whose stitched growth is not below the baseline's."""
    from propedge.reporting.results import read_result

    if rule not in ("money", "speed", "payouts"):
        raise ValueError("the walk-forward's rule is 'money' (D-382), 'speed' (D-390) or 'payouts' (D-395)")
    years = sorted({p for ch, t in FOLDS for p in (*ch, t)}, key=lambda x: PERIODS[x][0])
    tabs = {p: read_result(rd / f"fv3d_levers_{lever}_{p}.csv") for p in years}
    keep = None if values is None else sorted({int(v) for v in values} | {int(base)})

    def gate(df: pd.DataFrame) -> pd.DataFrame:
        g = df[(df["shift"] == "lower_bound") & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        return g if keep is None else g[g["value"].astype(int).isin(keep)]

    per = {p: gate(t).set_index(gate(t)["value"].astype(int))[MEASURE].astype(float) for p, t in tabs.items()}
    days = ({p: gate(t).set_index(gate(t)["value"].astype(int))[DAYS].astype(float) for p, t in tabs.items()}
            if rule == "speed" else {})
    pays = ({p: gate(t).set_index(gate(t)["value"].astype(int))[PAYOUTS].astype(float) for p, t in tabs.items()}
            if rule == "payouts" else {})
    bank = ({p: gate(t).set_index(gate(t)["value"].astype(int))[BANK].astype(float) for p, t in tabs.items()}
            if rule == "payouts" else {})
    span = {p: (str(gate(t)["first_day"].iloc[0]), str(gate(t)["last_day"].iloc[0])) for p, t in tabs.items()}
    rows = []
    for p in years:
        for _, r in gate(tabs[p]).iterrows():
            rows.append({"section": "year", "period": p, "value": int(r["value"]), "first_day": span[p][0],
                         "last_day": span[p][1], MEASURE: float(r[MEASURE]),
                         **{k: r[k] for k in BESIDE if k in r.index}})
    folds = []
    for k, (ch, test) in enumerate(FOLDS, 1):
        g_in = pd.concat([per[p] for p in ch], axis=1).mean(axis=1)
        if rule == "money":
            score = g_in
        elif rule == "speed":
            d_in = pd.concat([days[p] for p in ch], axis=1).mean(axis=1)
            score = -d_in
        else:                                        # D-395: the most payouts per path over the choice years
            score = pd.concat([pays[p] for p in ch], axis=1).mean(axis=1)
        top = score[np.isclose(score, score.max(), rtol=0, atol=1e-12)].index
        pick = int(base) if int(base) in top else int(score.idxmax())
        row = {"section": "fold", "fold": k, "choose": ",".join(ch), "test": test,
               "choose_first": span[ch[0]][0], "choose_last": span[ch[-1]][1], "test_first": span[test][0],
               "test_last": span[test][1], "pick": pick, "in_sample_pick": float(g_in[pick]),
               "in_sample_baseline": float(g_in[int(base)]), "test_pick": float(per[test][pick]),
               "test_baseline": float(per[test][int(base)])}
        if rule == "money":
            row["pick_beats_baseline"] = bool(pick != int(base) and per[test][pick] > per[test][int(base)])
        elif rule == "payouts":
            row.update({"in_sample_payouts_pick": float(score[pick]), "in_sample_payouts_baseline": float(score[int(base)]),
                        "test_payouts_pick": float(pays[test][pick]), "test_payouts_baseline": float(pays[test][int(base)]),
                        "test_bankroll_pick": float(bank[test][pick]), "test_bankroll_baseline": float(bank[test][int(base)]),
                        "pick_beats_baseline": bool(pick != int(base) and pays[test][pick] > pays[test][int(base)])})
        else:
            row.update({"in_sample_days_pick": float(d_in[pick]), "in_sample_days_baseline": float(d_in[int(base)]),
                        "test_days_pick": float(days[test][pick]), "test_days_baseline": float(days[test][int(base)]),
                        "pick_beats_baseline": bool(pick != int(base) and days[test][pick] < days[test][int(base)])})
        folds.append(row)
    f = pd.DataFrame(folds)
    mode = int(f["pick"].mode().iloc[0])
    agree, beats = int((f["pick"] == mode).sum()), int(f["pick_beats_baseline"].sum())
    sp_, sb = float(f["test_pick"].mean()), float(f["test_baseline"].mean())
    if rule == "money":
        lines = [{"section": "rule", "check": "picks_agree", "line": "the same pick in at least three of the four folds",
                  "value": agree, "pass": bool(mode != int(base) and agree >= 3), "pick": mode},
                 {"section": "rule", "check": "beats_in_tests", "line": "the pick beats the baseline in at least three of "
                  "the four test segments", "value": beats, "pass": bool(beats >= 3), "pick": mode},
                 {"section": "rule", "check": "stitched", "line": "the picks' mean over the four test segments above the "
                  "baseline's", "value": sp_ - sb, "stitched_pick": sp_, "stitched_baseline": sb, "pass": bool(sp_ > sb),
                  "pick": mode}]
    elif rule == "payouts":
        bp, bb = float(f["test_bankroll_pick"].mean()), float(f["test_bankroll_baseline"].mean())
        lines = [{"section": "rule", "check": "picks_agree", "line": "the same pick in at least three of the four folds",
                  "value": agree, "pass": bool(mode != int(base) and agree >= 3), "pick": mode},
                 {"section": "rule", "check": "more_payouts_in_tests", "line": "the pick collects more payouts per path "
                  "than the baseline in at least three of the four test segments", "value": beats,
                  "pass": bool(beats >= 3), "pick": mode},
                 {"section": "rule", "check": "bankroll_guardrail", "line": "the picks' required bankroll over the four "
                  "test segments not above the baseline's", "value": bp - bb, "stitched_pick": bp, "stitched_baseline": bb,
                  "pass": bool(bp <= bb), "pick": mode}]
    else:
        lines = [{"section": "rule", "check": "picks_agree", "line": "the same pick in at least three of the four folds",
                  "value": agree, "pass": bool(mode != int(base) and agree >= 3), "pick": mode},
                 {"section": "rule", "check": "faster_in_tests", "line": "the pick reaches the first payout in fewer "
                  "median days than the baseline in at least three of the four test segments", "value": beats,
                  "pass": bool(beats >= 3), "pick": mode},
                 {"section": "rule", "check": "growth_guardrail", "line": "the picks' growth over the four test segments "
                  "not below the baseline's", "value": sp_ - sb, "stitched_pick": sp_, "stitched_baseline": sb,
                  "pass": bool(sp_ >= sb), "pick": mode}]
    kept = all(r["pass"] for r in lines)
    lines.append({"section": "rule", "check": "kept", "line": "all three", "value": float(kept), "pass": kept, "pick": mode})
    return pd.concat([pd.DataFrame(rows), f, pd.DataFrame(lines)], ignore_index=True)


def identity_problems(df: pd.DataFrame, rd: Path) -> list[str]:
    from propedge.reporting.results import read_result

    run = read_result(rd / f"{RUN}.csv")
    g = run[(run["section"] == "gate") & (run["placement"].astype(str) == "off")]
    out = []
    for _, r in df.iterrows():
        m = g[(g["shift"] == r["shift"]) & np.isclose(g["enforcement_p"].astype(float), float(r["enforcement_p"]))]
        if len(m) != 1:
            out.append(f"no single recorded row at {r['shift']} {r['enforcement_p']}")
            continue
        for k in COMPARE:
            if not np.isclose(float(r[k]), float(m.iloc[0][k]), rtol=0, atol=1e-6):
                out.append(f"{r['shift']} {r['enforcement_p']}: {k} {r[k]} != {m.iloc[0][k]}")
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result

    import fv3_xfa_time_budget as xb
    import score_fv3_grid as gf

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--period", choices=tuple(PERIODS), default=None)
    ap.add_argument("--lever", choices=tuple(LEVERS), default="accounts")
    ap.add_argument("--wfo", action="store_true", help="D-382 (A): the folds and the keep rule from the per-year files")
    ap.add_argument("--values", default=None, help="D-390: the settings the walk-forward compares, e.g. 0,2")
    ap.add_argument("--rule", choices=("money", "speed", "payouts"), default="money",
                    help="D-390, D-395: the walk-forward's keep rule")
    ap.add_argument("--prereg", default=None,
                    help="D-405: the registered pre-registration FV3-S's settings run under (the steady lever)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.lever == "steady" and not a.wfo and a.period not in (None, "identity"):
        # D-405: FV3-S's settings run only under a registered, runnable pre-registration -- enforcement, not etiquette
        from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

        try:
            PreregRegistry.load().require_runnable(a.prereg)
        except UnregisteredRunError as exc:
            print(f"REFUSED (D-405): {exc}")
            return 2
    cfg = gf.config(CONFIG)
    lever, spec = a.lever, LEVERS[a.lever]
    base, dec = int(spec["baseline"]), str(spec["decision"])
    name = f"fv3d_levers_{lever}"
    if a.wfo:
        missing = [p for ch, t in FOLDS for p in (*ch, t) if not (rd / f"{name}_{p}.csv").is_file()]
        if missing:
            print(f"REFUSED: the per-year runs are not all on record: {sorted(set(missing))}.")
            return 2
        vals = None if a.values is None else [int(x) for x in str(a.values).split(",")]
        res = wfo(lever, rd, base, vals, a.rule)
        suffix = "" if (vals is None and a.rule == "money") else (
            f"_{a.rule}" + ("" if vals is None else "_v" + "".join(str(v) for v in sorted(set(vals) | {base}))))
        write_result(res, f"fv3d_wfo_{lever}{suffix}", script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                     results_dir=results_dir,
                     parameters={"lever": lever, "baseline": base, "folds": [list(ch) + [t] for ch, t in FOLDS],
                                 "measure": MEASURE, "arm": "lower_bound", "enforcement_p": 0.0, "decision": "D-382",
                                 "rule": a.rule, "values": vals, "days_measure": DAYS,
                                 "lever_decision": dec,
                                 "sources": [f"results/{name}_{p}.csv" for p in sorted({x for ch, t in FOLDS for x in (*ch, t)})]},
                     notes={"status": "EXPLORATORY: D-382 (A)'s anchored yearly walk-forward over the per-year runs"},
                     description=f"EXPLORATORY: the anchored yearly walk-forward (D-382 (A)) of the lever {lever} ({dec}): "
                                 "per year the measure and the readings beside, per fold the pick and its test against "
                                 "the baseline, and the keep rule's three lines.")
        pd.set_option("display.width", 220)
        print(res[res["section"] != "year"].dropna(axis=1, how="all").round(4).to_string(index=False))
        return 0
    if a.period is None:
        print("REFUSED: --period is required without --wfo.")
        return 2
    if a.period != "identity" and not (rd / f"{name}_identity.csv").is_file():
        print(f"REFUSED: the identity run is not on record (D-365 (5)): {name}_identity.csv.")
        return 2
    print("rebuilding the development trades...")
    t, days, tv = xb.rebuild_trades(cfg)
    lo, hi = PERIODS[a.period]
    tp, dp = in_period(t, days, lo, hi)
    rule = "yearly" if a.period == "identity" else "blocks21"
    if a.period == "identity":
        values = (base,)
    elif a.period == "choice" or a.period in {p for ch, t in FOLDS for p in (*ch, t)}:     # D-382 (A): every value a year
        values = tuple(spec["values"])
    else:
        choice = read_result(rd / f"{name}_choice.csv")
        values = tuple(sorted({decide(choice, None, base)["winner"], base}))
    frames = []
    counter = VariantCounter(path=rd / "variants.jsonl")
    for n in values:
        print(f"{a.period}: {lever} = {n} ({len(tp)} trades over {len(dp)} days)...")
        frames.append(run_one(cfg, n, tp, dp, tv, rule, lever))
        counter.record(prereg_id=f"{a.prereg if (lever == 'steady' and a.prereg) else dec}:fv3d_levers",
                       seed=int(cfg["seeds"]["gate"]), exploratory=True,
                       params={"lever": lever, "value": int(n), "period": a.period, "bound_rule": rule,
                               "config": "config/fv3_corrected_portfolio.yaml"},
                       label=f"FV3-D lever test: {lever} = {n}, {a.period} ({dec})")
    out = pd.concat(frames, ignore_index=True)
    if a.period == "identity":
        bad = identity_problems(out, rd)
        if bad:
            print("REFUSED: the harness does not reproduce the run: " + "; ".join(bad[:8]))
            return 2
    verdict = None
    if a.period == "check":
        verdict = decide(read_result(rd / f"{name}_choice.csv"), out, base)
    keep = ["lever", "value", "shift", "enforcement_p", "placement", MEASURE, *BESIDE, "policy_id", "policy_edge",
            "bound_rule", "trades", "days", "first_day", "last_day", "e_funded", "lb_funded"]
    res = out[[k for k in keep if k in out.columns]].copy()
    if verdict is not None:
        res = pd.concat([res, pd.DataFrame([{"lever": lever, "shift": "rule", **verdict}])], ignore_index=True)
    # the family's variants -- every lever's (D-365 (6))
    n_var = len({r["variant_id"] for r in counter.all() if str(r.get("prereg_id", "")).endswith(":fv3d_levers")})
    what = {"accounts": "N accounts sharing the signals",
            "collect_from": "the XFA's collect phase from a balance T (a take-profit at the shortfall to $150)",
            "second_trade": "an XFA's second trade after a first short of the winning-day minimum",
            "a3_filter": "the regular session's trades against the last hour's move skipped (A3, D-374)",
            "table_collect": "the state table with the funded menu's collect action (v17, D-379)",
            "collect_menu": "the state table with the collect menu and the collect stream (v18, D-384)",
            "after_win": "FV3-C's table with the after-win layer -- the daily collect bracket (1) or $500 trades (2) (D-390)",
            "speed_first": "FV3-C's table with the speed-first layer -- after a payout the 2x (1), the 1x (2) or adaptive (3) "
                           "(D-395)",
            "steady": "its own setting, the steadiness baseline for FV3-S (D-402)"}[lever]
    write_result(res, f"{name}_{a.period}", script=SCRIPT, seed=int(cfg["seeds"]["gate"]),
                 exploratory=True, results_dir=results_dir, variant_count=n_var,
                 parameters={"lever": lever, "values": list(values), "period": a.period, "range": [lo, hi],
                             "bound_rule": rule, "levels": list(LEVELS), "measure": MEASURE,
                             "config": "config/fv3_corrected_portfolio.yaml", "decision": dec},
                 notes={"status": "EXPLORATORY: FV3-D's lever test on development data, by D-365's procedure"},
                 description=f"EXPLORATORY: FV3-C with {what}, {a.period} period ({dec}): "
                             "both arms at 0 and 10 % denial, the gate's measure and the efficiency readings beside.")
    pd.set_option("display.width", 220)
    print(res.dropna(axis=1, how="all").round(4).to_string(index=False))
    if verdict is not None:
        print(f"RULE (D-365 (4)): winner {lever} = {verdict['winner']}; kept: {verdict['kept']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
