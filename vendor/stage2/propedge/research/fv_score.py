"""Scoring FV1 (config/model_fv.yaml, D-142) from the cloud's trade records, and its prop simulation.

Input: the ingested run file (`results/manual_R045_fv1_NQ.csv`, `..._R046_fv1_ES.csv`), one row per day (kind 'day':
integrity and the scaling reference) and one per trade (kind 'trade'). Nothing here re-runs the model; it measures
the trades the cloud produced from the shared core (`propedge/outcomes/fv_core.py`).

Day filter (declared here before any configuration is scored): the atlas's declared day filter
(`propedge.research.atlas.scoreable`) without its previous-settlement parts, which FV1 does not use -- the day
settled (its 15:00 bar exists), the 08:30 anchor bar exists, and at least 90 % of the bars from the anchor to 15:00
exist. Excluded days are counted and the unfiltered result is reported beside the filtered one.

A configuration is a stop family (atr_bands, structural) and a window (am: the morning session's trades only; am_pm:
all). The morning's trades are the same in both windows: the afternoon session comes after the morning's and
cannot change it. Scale p_ref is primary (D-106); actual is reported.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.outcomes.distribution import DayBlock

FAMILIES = ("atr_bands", "structural")
WINDOWS = ("am", "am_pm")
SCALES = ("p_ref", "actual")
MIN_COVERAGE = 0.9
REC_FIRST_MIN = 8 * 60          # slot 0 is the bar ENDING 08:00 CT (config recording.first)


# ------------------------------------------------------------------------------------------------ the data


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(days, trades) from the run file, days in order, dates parsed."""
    days = df[df["kind"] == "day"].copy()
    trades = df[df["kind"] == "trade"].copy()
    for x in (days, trades):
        x["n"] = x["n"].astype(int)
        x["date"] = pd.to_datetime(x["d"].astype(str).str.replace(r"\.0$", "", regex=True), format="%Y%m%d")
    days = days.sort_values("n").reset_index(drop=True)
    trades = trades.sort_values(["n", "j0"], kind="stable").reset_index(drop=True)
    for col in ("side", "t", "j0", "j_exit", "stop_ticks", "band"):
        trades[col] = trades[col].astype(int)
    return days, trades


def eligible(days: pd.DataFrame) -> pd.Series:
    """The declared day filter (module docstring)."""
    return ((days["st"].astype(float) == 1) & days["r0"].notna()
            & (days["cov"].astype(float) >= MIN_COVERAGE))


def configuration(trades: pd.DataFrame, family: str, window: str, scale: str) -> pd.DataFrame:
    """The trades one configuration takes, in day and time order."""
    if family not in FAMILIES or window not in WINDOWS or scale not in SCALES:
        raise ValueError(f"unknown configuration {family}/{window}/{scale}")
    m = (trades["family"] == family) & (trades["scale"] == scale)
    if window == "am":
        m &= trades["session"] == "am"
    return trades[m]


# ----------------------------------------------------------------------------------------------- statistics


def block_lower_bound(day_sums: np.ndarray, day_counts: np.ndarray, *, block: int, reps: int, seed: int,
                      alpha: float = 0.05) -> float:
    """One-sided (1 - alpha) lower bound of the mean R per trade from a moving-block bootstrap of days.

    Days are resampled in blocks of `block` consecutive days (days without a trade included, so a quiet stretch
    stays quiet); each replicate's mean is its total R over its number of trades."""
    s = np.asarray(day_sums, float)
    k = np.asarray(day_counts, float)
    n = len(s)
    if n < 2 or k.sum() < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    nb = math.ceil(n / block)
    out = np.empty(reps)
    chunk = max(1, min(reps, 4_000_000 // max(n, 1)))
    for lo in range(0, reps, chunk):
        r = min(chunk, reps - lo)
        starts = rng.integers(0, max(n - block + 1, 1), size=(r, nb))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(r, -1)[:, :n]
        idx = np.minimum(idx, n - 1)
        cnt = k[idx].sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[lo:lo + r] = np.where(cnt > 0, s[idx].sum(axis=1) / cnt, np.nan)
    return float(np.nanquantile(out, alpha))


def max_drawdown(r: np.ndarray) -> float:
    """Largest peak-to-trough fall of the cumulative sum, starting from zero (in the units of r)."""
    r = np.asarray(r, float)
    if not len(r):
        return 0.0
    eq = np.concatenate([[0.0], np.cumsum(r)])
    return float((np.maximum.accumulate(eq) - eq).max())


def summarise(tr: pd.DataFrame, day_ns: Sequence[int], *, block: int, reps: int, seed: int) -> dict[str, Any]:
    """The declared per-configuration measures over the days `day_ns` (in order)."""
    day_ns = list(day_ns)
    tr = tr[tr["n"].isin(day_ns)]
    r = tr["r_net"].to_numpy(float)
    by_day = tr.groupby("n")["r_net"].agg(["sum", "count"]).reindex(day_ns, fill_value=0)
    wins, losses = r[r > 0], r[r <= 0]
    kinds = tr["exit_kind"].value_counts(normalize=True) if len(tr) else pd.Series(dtype=float)
    return {
        "days": len(day_ns), "trades": int(len(r)),
        "trades_per_day": len(r) / len(day_ns) if day_ns else float("nan"),
        "win_rate": float((r > 0).mean()) if len(r) else float("nan"),
        "avg_win_r": float(wins.mean()) if len(wins) else float("nan"),
        "avg_loss_r": float(losses.mean()) if len(losses) else float("nan"),
        "e": float(r.mean()) if len(r) else float("nan"),
        "lb": block_lower_bound(by_day["sum"].to_numpy(), by_day["count"].to_numpy(), block=block, reps=reps,
                                seed=seed),
        "e_zero_cost": float(tr["r_price"].mean()) if len(r) else float("nan"),
        "sd_r": float(r.std(ddof=1)) if len(r) > 1 else float("nan"),
        "total_r": float(r.sum()),
        "max_dd_r": max_drawdown(r),
        "mean_stop_ticks": float(tr["stop_ticks"].mean()) if len(r) else float("nan"),
        "share_target": float(kinds.get("t", 0.0)), "share_stop": float(kinds.get("s", 0.0)),
        "share_gap": float(kinds.get("g", 0.0)), "share_time": float(kinds.get("m", 0.0)),
    }


def select(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The declared selection: the highest lower bound of e on the selection half (ties: more trades, then the
    declared order of families and windows)."""
    ok = [r for r in rows if np.isfinite(r["lb"])]
    if not ok:
        raise ValueError("no configuration has a computable lower bound on the selection half")
    order = {(f, w): i for i, (f, w) in enumerate((f, w) for f in FAMILIES for w in WINDOWS)}
    return max(ok, key=lambda r: (r["lb"], r["trades"], -order[(r["family"], r["window"])]))


# ---------------------------------------------------------------------------------------------- trade log


def clock(slot: int, *, start: bool = False) -> str:
    """CT clock time of slot `slot`'s bar END (or its start, one minute earlier)."""
    m = REC_FIRST_MIN + int(slot) - (1 if start else 0)
    return f"{m // 60:02d}:{m % 60:02d}"


def trade_log(tr: pd.DataFrame, *, tick_value: float, risk: float, cap_micros: int) -> pd.DataFrame:
    """The configuration's trades as a readable log: when, which setup, how it ended, R, and the dollars one
    Combine account would have made at `risk` dollars (contracts = min(floor(risk / (stop ticks x tick value)),
    cap), D-117)."""
    rpc = tr["stop_ticks"].to_numpy(float) * float(tick_value)
    contracts = np.minimum(np.floor(float(risk) / rpc), int(cap_micros)).astype(int)
    out = pd.DataFrame({
        "date": tr["date"].dt.strftime("%Y-%m-%d").to_numpy(),
        "session": tr["session"].to_numpy(), "setup": tr["tag"].to_numpy(),
        "side": np.where(tr["side"].to_numpy() > 0, "long", "short"),
        "signal_bar_close_ct": [clock(t) for t in tr["t"]],
        "entry_ct": [clock(j, start=True) for j in tr["j0"]],
        "exit_bar_ct": [clock(j) for j in tr["j_exit"]],
        "exit": tr["exit_kind"].map({"t": "target", "s": "stop", "g": "stop (gap through)", "m": "time 15:00"})
                               .to_numpy(),
        "stop_ticks": tr["stop_ticks"].to_numpy(), "atr_band": tr["band"].to_numpy(),
        "r_net": tr["r_net"].to_numpy(), "r_zero_cost": tr["r_price"].to_numpy(),
        "mfe_r": tr["mfe"].to_numpy(), "mae_r": tr["mae"].to_numpy(),
        "micro_contracts": contracts, "risk_usd": contracts * rpc,
        "pnl_usd": tr["r_net"].to_numpy() * contracts * rpc,
    })
    out["cum_r"] = out["r_net"].cumsum()
    out["cum_pnl_usd"] = out["pnl_usd"].cumsum()
    return out


# ------------------------------------------------------------------------------------------- the prop draw


def day_blocks(tr: pd.DataFrame, day_ns: Sequence[int], *, tick_value: float) -> list[DayBlock]:
    """One block per day in `day_ns` (days without a trade are empty blocks, so the trade rate is kept), each
    trade at one micro contract: P&L = R net x its risk; risk per contract = stop ticks x tick value. Each trade's
    MAE, which the kits export in R at its stop, rides along in dollars so the campaign settles a trade that risks
    more than the room exactly (D-156)."""
    g = {n: x for n, x in tr.groupby("n")}
    blocks = []
    for n in day_ns:
        x = g.get(n)
        if x is None:
            blocks.append(DayBlock(pnl=np.zeros(0), risked=np.zeros(0), exit_reasons=(),
                                   risk_per_contract=np.zeros(0), mae=np.zeros(0)))
            continue
        x = x.sort_values("j0", kind="stable")
        rpc = x["stop_ticks"].to_numpy(float) * float(tick_value)
        # The kit's MAE stops before a bar that opens through the stop (fv_core), so a gap exit's is short of the
        # loss it closed at; any trade went at least as far against it as that loss.
        mae_r = np.maximum(x["mae"].to_numpy(float), -x["r_price"].to_numpy(float))
        blocks.append(DayBlock(pnl=x["r_net"].to_numpy(float) * rpc, risked=rpc.copy(),
                               exit_reasons=tuple(x["exit_kind"].map({"m": "flatten"}).fillna("bracket")),
                               risk_per_contract=rpc.copy(), mae=mae_r * rpc))
    return blocks


@dataclass(frozen=True)
class PropSettings:
    risk: float = 500.0
    n_paths: int = 5000
    seed: int = 20261102
    combine_max_days: int = 252
    funded_horizon_days: int = 252
    bankroll: float = 5000.0
    headroom_frac: float = 0.75


def prop_simulation(blocks: Sequence[DayBlock], settings: PropSettings, *, name: str,
                    ledger: Any | None = None) -> tuple[dict[str, Any], pd.DataFrame]:
    """One Combine attempt per path, and the funded account it leads to, through the lockstep engine with the
    verified rules (Aeropay terms), tier sizing (D-117, current tier) and days resampled independently.

    Returns (summary, one row per path)."""
    from dataclasses import replace

    from propedge.campaign.lockstep import simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import REGISTRY
    from propedge.campaign.shared_days import INDEPENDENT, SharedDayDraws
    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    busiest = max(len(b) for b in blocks)
    base = REGISTRY.get("fast_take_max")          # 1.5:1 at $500 both legs, take the maximum (T5_RESULTS 2a)
    protocol = replace(base, name=name, combine_risk=settings.risk, funded_risk=settings.risk,
                       trades_per_day=max(busiest, 1), family="fv1", note="FV1's trade log through the contract")
    rules = rules_for_method("aeropay", ledger=ledger)
    sizing = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=settings.headroom_frac, ledger=ledger)
    horizon = settings.combine_max_days + settings.funded_horizon_days + 5
    summary, paths = simulate_lockstep_campaign(
        protocol, edge=0.0,                     # unused: the draws are the log's own trades
        seed=settings.seed, rules=rules, initial_bankroll=settings.bankroll,
        horizon_days=horizon, n_paths=settings.n_paths, payout_method="aeropay", max_concurrent_accounts=1,
        require_verified_cap=False, max_attempts=1, combine_max_days=settings.combine_max_days,
        funded_horizon_days=settings.funded_horizon_days, record_trades=True, ledger=ledger,
        draw_factories_for_path=lambda s: SharedDayDraws({0: list(blocks)}, protocol=protocol, seed=s,
                                                         mode=INDEPENDENT, sizing=sizing).factories(),
    )
    rows = []
    for i, p in enumerate(paths):
        c = p.combines[0]
        f = p.funded[0] if p.funded else None
        led = [t for t in p.trades if t["kind"] == "combine"]
        bal = np.array([0.0] + [t["balance_after"] for t in led])
        rows.append({
            "path": i, "combine": ("passed" if c.passed else "failed" if c.failed else "unresolved"),
            "combine_days": c.days, "combine_trades": c.trades,
            "combine_max_dd_usd": float((np.maximum.accumulate(bal) - bal).max()),
            "combine_subscriptions": c.subscriptions_paid,
            "funded": f is not None, "funded_closed": bool(f.closed) if f else False,
            "funded_days": f.days if f else 0, "funded_trades": f.trades if f else 0,
            "n_payouts": f.n_payouts if f else 0,
            "first_payout_day": f.first_payout_day if f else -1,
            "gross_paid": f.gross_paid if f else 0.0, "net_payouts": f.cash if f else 0.0,
            "fees": p.path.total_fees, "net_cash": p.path.final_cash - settings.bankroll,
            "at_cap": sum((a.sizing or {}).get("at_cap", 0) for a in (c, f) if a is not None),
            "sized": sum((a.sizing or {}).get("trades", 0) for a in (c, f) if a is not None),
            "unsized": sum((a.sizing or {}).get("unsized", 0) for a in (c, f) if a is not None),
        })
    df = pd.DataFrame(rows)
    passed = df["combine"] == "passed"
    paid = df["n_payouts"] > 0
    out = {
        "paths": len(df), "p_pass": float(passed.mean()), "p_fail": float((df["combine"] == "failed").mean()),
        "p_unresolved": float((df["combine"] == "unresolved").mean()),
        "median_days_to_pass": float(df.loc[passed, "combine_days"].median()) if passed.any() else float("nan"),
        "mean_days_to_pass": float(df.loc[passed, "combine_days"].mean()) if passed.any() else float("nan"),
        "median_days_to_fail": (float(df.loc[df["combine"] == "failed", "combine_days"].median())
                                if (df["combine"] == "failed").any() else float("nan")),
        "median_combine_max_dd_usd": float(df["combine_max_dd_usd"].median()),
        "p_any_payout": float(paid.mean()),
        "p_funded_closed_given_funded": (float(df.loc[df["funded"], "funded_closed"].mean())
                                         if df["funded"].any() else float("nan")),
        "mean_payouts_given_funded": (float(df.loc[df["funded"], "n_payouts"].mean())
                                      if df["funded"].any() else float("nan")),
        "median_first_payout_day": (float(df.loc[paid, "first_payout_day"].median()) if paid.any()
                                    else float("nan")),
        "mean_net_payouts": float(df["net_payouts"].mean()), "mean_fees": float(df["fees"].mean()),
        "mean_net_cash": float(df["net_cash"].mean()), "median_net_cash": float(df["net_cash"].median()),
        "share_at_tier_cap": float(df["at_cap"].sum() / max(df["sized"].sum(), 1)),
        "share_unsized": float(df["unsized"].sum() / max(df["sized"].sum(), 1)),
        "trades_per_day_slots": int(protocol.trades_per_day),
        "engine": "propedge.campaign.lockstep.simulate_lockstep_campaign", "summary_ruin": summary.ruin_probability,
    }
    return out, df


__all__ = ["FAMILIES", "WINDOWS", "SCALES", "MIN_COVERAGE", "split", "eligible", "configuration",
           "block_lower_bound", "max_drawdown", "summarise", "select", "clock", "trade_log", "day_blocks",
           "PropSettings", "prop_simulation"]
