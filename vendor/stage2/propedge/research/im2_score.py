"""IM2's scorer (P-04 §4 and §5): from the ingested kits R053-R060 to e and its bound per R at both scales, the day
blocks the campaign replays, the D-145 gate at both scales and the two kill lines.

Everything here is fixed by P-04 before any IM2 bar is read:

* **Fees.** One micro's round turn per trade (`config/fills.yaml`), and nothing is scored until MCL and MNG carry the
  totals Topstep 8284213 states when re-read on or after 2026-10-01, at no less than the derived floors (`fees`).
* **Net outcomes.** Per entry, scale s ('p' the reference price, D-106; 'a' actual prices) and R: `u{R}_{s}` = the
  kit's R after the fills' ticks less one micro's round turn over one micro's risk, `dist_{s}` x the micro's point
  value (`trade_audit.im2_cost_checks` checks it). A trade's risk per micro is `rpc_{s}`.
* **The price-lock rule** (Topstep 10296582; `config/model_im2.yaml` `price_lock`): an ES entry whose lowest price
  while held (`mn`) came within the declared distance of the day-session lock is flagged; its outcome at every R is
  the lower of its net outcome and minus its costs (`v{R}_{s}`): a gain on it is forfeited, a loss kept. The verdict
  uses `v`; the count of flagged entries is reported beside it.
* **The cost sensitivity** (`cost_sensitivity_extra_ticks`): `w{R}_{s}` = `v` less the declared extra ticks of the
  micro over its risk, on CL and NG; the gate on `w` is reported beside the verdict, never instead of it.
* **The day set.** Every date in the period that at least one market's exchange calendar schedules as a full session
  (`cal` F, or listed in `gone`: a scheduled session with no bar); days without an entry are empty blocks.
* **Tradable entries.** Sessions scheduled as full (`cal` F) and not skipped (`sk` empty): late opens (`sk` late) are
  computed for the record and never enter e, its bound or the campaign.
* **e and its bound** per R and scale: the mean over every tradable entry, and the lower of the 20-day moving-block
  bootstrap over the day set (days without an entry included) and the normal bound clustered by day.
* **Micro expiry (D-198).** MCL and MNG stop trading one business day before CL and NG: an entry on the standard
  contract's last trading day is flagged untradable as a micro (`micro_untradable`), one on the business day before
  it as on the micro's own last day (`micro_last_day`). The verdict keeps every entry, as P-04 registers; the scorer
  reports the gate again without the untradable ones and again without both sets (D-199), and the chart review
  over-samples the last-day ones in proportion to each market's count (D-199). The last trading day is QuantConnect's
  code for the contract unless the exchange's record differs (`LAST_TRADE_CORRECTIONS`, D-199).
* **Blocks.** One per day of the day set; its trades in entry order, ties in the order ES, CL, 6E, NG; each at one
  micro (`risk_per_contract` = `rpc`), with outcomes and MAE at R = 1 and 2 (D-162), its 2:1 outcome as base P&L, and
  its entry and 2:1 exit times on one clock (minutes CT) for flat routing (D-159). An entry with no walk at a scale
  (through its stop there) is absent from that scale's blocks and counted.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR, REPO_ROOT, RESULTS_DIR
from propedge.outcomes.distribution import DayBlock

MARKETS = ("ES", "CL", "6E", "NG")          # also the order of simultaneous entries (P-04 §3)
SCALES = ("p", "a")                         # the reference price (D-106) and actual prices: P-04 requires both
RR_ALL = (1, 2, 3)
RR_GATE = (1, 2)                            # the lifecycle's; R = 3 is reported only
SEED = 20261120
BOOT_LEN, REPS = 20, 10_000                 # the bootstrap's length in days; "block" means one trading day (D-197)
BANKROLL, HORIZON, PATHS, ACCOUNTS = 5_000.0, 504, 500, 5
COMBINE_DAYS_LIMIT = 21                     # kill line 1 (D-154): one billing period
DEVELOPMENT = ("20090601", "20191231")
POLICY_ID = "im2_s1_lifecycle"
#: D-198: MCL and MNG stop trading one business day before CL and NG (NYMEX rules); M6E and MES expire with 6E and ES.
MICRO_ENDS_EARLY = ("CL", "NG")
_MONTH_CODES = "FGHJKMNQUVXZ"
_EXPIRY_IN_PRIOR_MONTH = ("CL", "NG")     # CL and NG expire in the month before the contract month; ES and 6E in it
#: D-199, a data-boundary rule, not a roll rule: a business day's predecessor is at most 4 calendar days earlier
#: (Fri -> Tue; Thu -> Mon after Good Friday), so an expiry past the data's edge flags nothing. It moves no entry or roll.
_MAX_BUSINESS_GAP_DAYS = 4
#: D-199: where QuantConnect's code dates a contract's last trade differently from the exchange's record. NG November
#: 2012: QuantConnect's calendar closes NYMEX on 2012-10-29/30 (Hurricane Sandy) and so dates it 2012-10-25; the
#: contract expired on Monday 2012-10-29 (EIA Natural Gas Weekly Update, 2012-11-01), as CME's rule gives.
LAST_TRADE_CORRECTIONS = {"NG25X12": date(2012, 10, 29)}


def expiry_date(market: str, sym: str) -> date | None:
    """A contract's last trading day from QuantConnect's code for it: the root, the two-digit day, the month code and a
    one- or two-digit year (`CL20N14`: CL July 2014, last traded 2014-06-20; `6E14U9`: September 2009, 2009-09-14).
    None when the code does not parse."""
    s = str(sym)
    if not s.startswith(market):
        return None
    rest = s[len(market):]
    try:
        day, m, y = int(rest[:2]), _MONTH_CODES.index(rest[2]) + 1, 2000 + int(rest[3:])
    except (ValueError, IndexError):
        return None
    if market in _EXPIRY_IN_PRIOR_MONTH:
        m, y = (12, y - 1) if m == 1 else (m - 1, y)
    try:
        return date(y, m, day)
    except ValueError:
        return None


def last_trade_date(market: str, sym: str) -> date | None:
    """The contract's last trading day: QuantConnect's code for it (`expiry_date`), unless the exchange's record differs
    (`LAST_TRADE_CORRECTIONS`, D-199)."""
    return LAST_TRADE_CORRECTIONS.get(str(sym)) or expiry_date(market, sym)


def review_split(counts: dict[str, int], n: int) -> dict[str, int]:
    """D-199: n review draws shared across markets in proportion to their flagged counts, by largest remainder (ties in
    the order given); every flagged entry when there are no more than n."""
    total = sum(counts.values())
    if total <= n:
        return dict(counts)
    exact = {m: n * c / total for m, c in counts.items()}
    share = {m: int(x) for m, x in exact.items()}
    for m in sorted(counts, key=lambda m: -(exact[m] - share[m]))[:n - sum(share.values())]:
        share[m] += 1
    return share


def _previous_session(sessions: Sequence[str], x: str) -> str | None:
    """The last session (YYYYMMDD) before date x, when it is a business-day predecessor (at most 4 calendar days
    earlier); None otherwise, e.g. when the data end before x."""
    earlier = [s for s in sessions if s < x]
    if not earlier:
        return None
    gap = (date.fromisoformat(f"{x[:4]}-{x[4:6]}-{x[6:]}")
           - date.fromisoformat(f"{earlier[-1][:4]}-{earlier[-1][4:6]}-{earlier[-1][6:]}")).days
    return earlier[-1] if gap <= _MAX_BUSINESS_GAP_DAYS else None


def micro_expiry_flags(market: str, sessions: pd.DataFrame, d: pd.Series, sym: pd.Series
                       ) -> tuple[list[bool], list[bool]]:
    """D-198, for entries on dates `d` held in contracts `sym`: (untradable as a micro -- on the standard contract's last
    trading day, when the micro has already stopped; on the micro's own last day -- the business day before it). All
    False for markets whose micro expires with the standard contract. The business days are the market's sessions,
    those with no data (`gone`) included."""
    if market not in MICRO_ENDS_EARLY:
        return [False] * len(d), [False] * len(d)
    days = sorted(set(sessions["d"]) | {x for g in sessions["gone"] for x in str(g).split(",") if x})
    exp = [last_trade_date(market, s) for s in sym]
    exp = [e.strftime("%Y%m%d") if e else "" for e in exp]
    prev = {x: _previous_session(days, x) for x in set(exp) if x}
    return ([bool(x) and a == x for a, x in zip(d, exp)],
            [bool(x) and a == prev.get(x) for a, x in zip(d, exp)])


class FeesNotReady(RuntimeError):
    """P-04 §3: nothing is scored before the 2026-10-01 re-read of the MCL and MNG round turns is recorded."""


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG_DIR / "model_im2.yaml").read_text(encoding="utf-8"))


def fees(cfg: dict | None = None, fills_path: Path | None = None) -> dict[str, float]:
    """{market: its micro's round turn}. Refuses (`FeesNotReady`) unless MCL and MNG were re-read on or after the
    declared date (`provenance.<micro>.date_read`) and stand at no less than the declared floors."""
    cfg = cfg or config()
    doc = yaml.safe_load(Path(fills_path or CONFIG_DIR / "fills.yaml").read_text(encoding="utf-8"))
    rt = doc["round_turn_by_instrument"]
    vals, prov = rt["values"], rt.get("provenance") or {}
    need = date.fromisoformat(str(cfg["fees_reread_on_or_after"]))
    problems = []
    for sym, floor in cfg["fee_floor_round_turn"].items():
        read = (prov.get(sym) or {}).get("date_read")
        if read is None or date.fromisoformat(str(read)) < need:
            problems.append(f"{sym} last read {read}, before {need}")
        if float(vals[sym]) < float(floor) - 1e-9:
            problems.append(f"{sym} at {vals[sym]}, below the declared floor {floor}")
    if problems:
        raise FeesNotReady("P-04 §3: nothing is scored before Topstep 8284213 is re-read on or after "
                           f"{need} and MCL and MNG are recorded in config/fills.yaml: " + "; ".join(problems))
    return {m: float(vals[cfg["markets"][m]["micro"]]) for m in MARKETS}


def micro_specs(cfg: dict | None = None) -> dict[str, dict[str, float]]:
    """{market: {'point_value', 'tick_value', 'tick'}} of its traded micro, from config/instruments.yaml."""
    from propedge.execution.instruments import load_instruments

    cfg = cfg or config()
    inst = load_instruments()
    out = {}
    for m in MARKETS:
        mk = cfg["markets"][m]
        i = inst[mk["micro"]]
        if abs(i.tick_size - float(mk["micro_tick"])) > 1e-12:
            raise ValueError(f"{m}: config/model_im2.yaml's micro tick {mk['micro_tick']} is not "
                             f"config/instruments.yaml's {i.tick_size} for {mk['micro']}")
        out[m] = {"point_value": i.point_value, "tick_value": i.tick_value, "tick": i.tick_size}
    return out


# ------------------------------------------------------------------------------------------------ the logs


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("d", "sk", "cal", "rel", "gone", "sym"):
        if c in df:
            df[c] = df[c].fillna("").astype(str)
    return df


def read_run(run_id: str, results_dir: Path | None = None, runs_dir: Path | None = None
             ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """One ingested IM2 run: (sessions, entries, the scheduled sessions HEAD lists after the last one opened)."""
    import json

    from propedge.reporting.results import verify_result

    path = Path(results_dir or RESULTS_DIR) / f"manual_{run_id.replace('-', '_')}.csv"
    ok, msg = verify_result(path)
    if not ok:
        raise ValueError(msg)
    df = _clean(pd.read_csv(path, dtype={c: str for c in ("d", "sk", "cal", "rel", "gone", "sym")}))
    ing = Path(runs_dir or REPO_ROOT / "runs") / run_id / "ingested.json"
    tail = str((json.loads(ing.read_text(encoding="utf-8")).get("summary") or {}).get("gone") or "") \
        if ing.exists() else ""
    return (df[df["kind"] == "day"].reset_index(drop=True), df[df["kind"] == "entry"].reset_index(drop=True),
            [x for x in tail.split(",") if x])


def day_set(sessions: dict[str, pd.DataFrame], tails: dict[str, list[str]] | None = None,
            start: str = DEVELOPMENT[0], end: str = DEVELOPMENT[1]) -> list[str]:
    """P-04 §3: every date (YYYYMMDD) in [start, end] that at least one market schedules as a full session."""
    s: set[str] = set()
    for m, days in sessions.items():
        s |= set(days.loc[days["cal"] == "F", "d"])
        for g in days["gone"]:
            s |= {x for x in str(g).split(",") if x}
        s |= set((tails or {}).get(m, []))
    return sorted(x for x in s if start <= x <= end)


def hot_slots(rel: str, open_min: int, hot_minutes: int) -> set[int]:
    return {int(m) - open_min + k for m in str(rel).split(",") if m for k in range(hot_minutes)}


def entry_table(market: str, sessions: pd.DataFrame, entries: pd.DataFrame, *, round_turn: float,
                spec: dict[str, float], cfg: dict | None = None) -> pd.DataFrame:
    """The tradable entries of one market with their net outcomes and treatments (see the module docstring)."""
    from propedge.data.qc_algorithms import im2_params

    cfg = cfg or config()
    q = im2_params(market)
    day = sessions.set_index("d")
    t = entries.copy()
    t["market"] = market
    for c in ("cal", "sk", "pc", "rel"):
        t[c] = t["d"].map(day[c])
    t = t[(t["cal"] == "F") & (t["sk"] == "")].copy()
    t["sym"] = t["d"].map(day["sym"]) if "sym" in day else ""
    t["micro_untradable"], t["micro_last_day"] = micro_expiry_flags(market, sessions, t["d"], t["sym"])   # D-198
    t["entry_t"] = q["open_min"] + t["j0"]                                 # the entry bar's start, minutes CT
    hm = int(cfg["release_hot_minutes"])
    t["release_entry"] = [int(j) in hot_slots(r, q["open_min"], hm) for j, r in zip(t["j0"], t["rel"])]
    lock = (cfg.get("price_lock") or {}).get(market)
    t["lock_flag"] = (t["mn"] <= t["pc"] * (1.0 - lock["limit_down"] + lock["within"])) if lock else False
    extra = float((cfg.get("cost_sensitivity_extra_ticks") or {}).get(market, 0))
    for s in SCALES:
        rpc = t[f"dist_{s}"] * spec["point_value"]
        t[f"rpc_{s}"] = rpc
        t[f"exit_t_{s}"] = q["open_min"] + t[f"j2_{s}"] + 1                # the 2:1 exit bar's end
        cost = round_turn / rpc
        for R in RR_ALL:
            u = t[f"r{R}_{s}"] - cost
            t[f"u{R}_{s}"] = u
            v = np.where(t["lock_flag"], np.minimum(u, -cost), u)
            t[f"v{R}_{s}"] = v
            t[f"w{R}_{s}"] = v - extra * spec["tick_value"] / rpc
            t[f"release_exit{R}_{s}"] = [int(j) in hot_slots(r, q["open_min"], hm)
                                         for j, r in zip(t[f"j{R}_{s}"], t["rel"])]
    return t.reset_index(drop=True)


# ------------------------------------------------------------------------------------------------ statistics


def edge(table: pd.DataFrame, days: Sequence[str], R: int, scale: str, col: str = "v", *,
         seed: int = SEED, boot_len: int = BOOT_LEN, reps: int = REPS) -> dict[str, Any]:
    """e at R and scale over every tradable entry with a walk there, its two lower bounds and the lower of them."""
    from propedge.backtest.metrics import normal_lower_bound
    from propedge.research.fv_score import block_lower_bound

    x = table[table[f"dist_{scale}"].notna() & table["d"].isin(days)]
    r = x[f"{col}{R}_{scale}"].to_numpy(float)
    pos = {d: i for i, d in enumerate(days)}
    idx = x["d"].map(pos).to_numpy(int)
    sums = np.bincount(idx, weights=r, minlength=len(days)) if len(r) else np.zeros(len(days))
    counts = np.bincount(idx, minlength=len(days)) if len(r) else np.zeros(len(days))
    lb_boot = block_lower_bound(sums, counts, block=boot_len, reps=reps, seed=seed)   # P-04's registered call
    lb_norm = normal_lower_bound(r, idx) if len(r) > 1 else float("nan")
    kinds = x[f"kind{R}_{scale}"].value_counts(normalize=True) if len(x) else pd.Series(dtype=float)
    return {"R": R, "scale": scale, "outcome": col, "entries": int(len(r)), "days": len(days),
            "e": float(r.mean()) if len(r) else float("nan"),
            "lb_bootstrap": lb_boot, "lb_normal": lb_norm,
            "lb": float(np.nanmin([lb_boot, lb_norm])) if np.isfinite([lb_boot, lb_norm]).any() else float("nan"),
            "sd": float(r.std(ddof=1)) if len(r) > 1 else float("nan"),
            "hit_rate": float((r > 0).mean()) if len(r) else float("nan"),
            "share_target": float(kinds.get("t", 0.0)), "share_stop": float(kinds.get("s", 0.0)),
            "share_gap": float(kinds.get("g", 0.0)), "share_close": float(kinds.get("m", 0.0)),
            "cost_drag_r": float((x[f"r{R}_{scale}"] - x[f"u{R}_{scale}"]).mean()) if len(x) else float("nan")}


def blocks(table: pd.DataFrame, days: Sequence[str], scale: str, col: str = "v") -> list[DayBlock]:
    """One block per day of `days` (empty when no entry), trades in entry order with ties ES, CL, 6E, NG."""
    order = {m: i for i, m in enumerate(MARKETS)}
    x = table[table[f"dist_{scale}"].notna()].copy()
    x["_o"] = x["market"].map(order)
    g = {d: y.sort_values(["entry_t", "_o"], kind="stable") for d, y in x.groupby("d")}
    out = []
    for d in days:
        y = g.get(d)
        if y is None or not len(y):
            out.append(DayBlock(pnl=np.zeros(0), risked=np.zeros(0), exit_reasons=(), risk_per_contract=np.zeros(0),
                                mae=np.zeros(0), entry_t=np.zeros(0), exit_t=np.zeros(0),
                                r_by_rr={float(R): np.zeros(0) for R in RR_GATE},
                                mae_by_rr={float(R): np.zeros(0) for R in RR_GATE}))
            continue
        rpc = y[f"rpc_{scale}"].to_numpy(float)
        r_by = {float(R): y[f"{col}{R}_{scale}"].to_numpy(float) for R in RR_GATE}
        # a trade went at least as far against it as the loss it closed at (fv_score.day_blocks' rule, D-156)
        mae_by = {float(R): np.maximum(y[f"mae{R}_{scale}"].to_numpy(float), -y[f"r{R}_{scale}"].to_numpy(float))
                  for R in RR_GATE}
        out.append(DayBlock(pnl=r_by[2.0] * rpc, risked=rpc.copy(),
                            exit_reasons=tuple(y[f"kind2_{scale}"].map({"m": "flatten"}).fillna("bracket")),
                            risk_per_contract=rpc.copy(), mae=mae_by[2.0] * rpc,
                            entry_t=y["entry_t"].to_numpy(float), exit_t=y[f"exit_t_{scale}"].to_numpy(float),
                            r_by_rr=r_by, mae_by_rr=mae_by, markets=tuple(y["market"])))
    return out


# ------------------------------------------------------------------------------------------------ the campaign


def policy():
    """P-04 §3's lifecycle, exactly as registered."""
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    return RiskPolicy(id=POLICY_ID, root=Phase(
        combine=Leaf("combine 1:1 $1,500", risk=1500, rr=1.0, max_trades=1),
        funded=Tiers(on="balance", name="funded", tiers=(
            (0, Leaf("build 2:1 $1,000", risk=1000, rr=2.0, max_trades=1)),
            (2000, Leaf("harvest 1:1 $300", risk=300, rr=1.0, max_trades=3))))))


def protocol(busiest_day: int):
    """P-04 §3's base legs; the policy sets every trade."""
    from propedge.campaign.protocols import Protocol

    return Protocol(name="im2_p04", combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=1000.0,
                    trades_per_day=max(1, int(busiest_day)), payout_path="standard", keep_balance=0.0,
                    payout_frac=1.0, max_concurrent_accounts=ACCOUNTS, family="im2",
                    source="prereg/P-04_im2_lifecycle_v3.md §3", note="IM2 under stage one's lifecycle, rotated")


def combine_stats(paths: Sequence[Any]) -> dict[str, Any]:
    """Kill line 1's reading (P-04 §5): the median `CombineRecord.days` over every resolved Combine (passed, failed or
    abandoned), with the counts; Combines still open at the horizon are left out and counted. Beside it (P-04 §4):
    trades per account per trading day in the Combine and funded, and the share of funded accounts put on the
    Consistency path by the Responsible Trading Program (D-174)."""
    recs = [c for p in paths for c in p.combines]
    res = [c for c in recs if c.resolved_on is not None]
    funded = [f for p in paths for f in p.funded]
    ratio = lambda xs: (float(sum(x.trades for x in xs) / sum(x.days for x in xs))           # noqa: E731
                        if sum(x.days for x in xs) else float("nan"))
    return {"combines_resolved": len(res), "combines_open_at_horizon": len(recs) - len(res),
            "combines_passed": sum(c.passed for c in res), "combines_failed": sum(c.failed for c in res),
            "combines_abandoned": sum(c.abandoned for c in res),
            "median_combine_days_resolved": float(np.median([c.days for c in res])) if res else float("nan"),
            "trades_per_combine_day": ratio(recs), "trades_per_funded_day": ratio(funded),
            "share_funded_consistency_forced": (float(np.mean([bool(getattr(f, "consistency_forced", False))
                                                               for f in funded])) if funded else float("nan"))}


def run_gate(day_blocks: Sequence[DayBlock], stats: dict[float, dict[str, float]], *, seed: int = SEED,
             n_paths: int = PATHS, horizon_days: int = HORIZON, bankroll: float = BANKROLL
             ) -> tuple[pd.DataFrame, bool]:
    """P-04 §4's primary metric: `propedge.campaign.gate.run_gate` with rotation across five accounts in total, five
    Combines at the start, the lifecycle policy, MAE settlement, each R shifted to its own lower bound; `stats` maps
    R (1.0, 2.0) to {'e', 'lb'}. Rows carry kill line 1's reading."""
    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC, SizingRule

    e_by = {float(R): float(stats[float(R)]["e"]) for R in RR_GATE}
    lb_by = {float(R): float(stats[float(R)]["lb"]) for R in RR_GATE}
    busiest = max((len(b) for b in day_blocks), default=1)
    df, passed = gate.run_gate(
        day_blocks, e=e_by[2.0], lb=lb_by[2.0], protocol=protocol(busiest), bankroll=bankroll,
        horizon_days=horizon_days, n_paths=n_paths, seed=seed, accounts=ACCOUNTS,
        sizing=SizingRule.from_ledger(CURRENT_TIER, headroom_frac=DEFAULT_HEADROOM_FRAC),
        rules=rules_for_method("aeropay"), mode="rotation", settlement="mae", combines=ACCOUNTS,
        total_accounts=ACCOUNTS, risk_policy=policy(), e_by_rr=e_by, lb_by_rr=lb_by, markets=list(MARKETS),
        path_hook=lambda shift, p, paths: combine_stats(paths))                # D-176: four markets, declared
    if not bool(df["flat_routing"].all()):
        raise RuntimeError("P-04 §3: every trade is routed only to an account flat at its entry (D-159); a gate row "
                           "ran without flat routing, so one account could have held several markets at once")
    return df, passed


def kill_lines(gate_df: pd.DataFrame, passed: bool) -> dict[str, Any]:
    """P-04 §5 on one scale's development gate: line 1, the gate row's median resolved-Combine days above 21 (or no
    Combine resolved at all, whose median is undefined); line 2, the gate failing."""
    g = gate_df[gate_df["is_gate_row"]].iloc[0]
    med = float(g["median_combine_days_resolved"])
    line1 = bool(not np.isfinite(med) or med > COMBINE_DAYS_LIMIT)
    return {"kill_line_1": line1, "median_combine_days_resolved": med, "kill_line_2": not passed,
            "killed": line1 or not passed}


def harvest_day_share(table: pd.DataFrame, days: Sequence[str], scale: str = "p", *, risk: float = 300.0,
                      max_trades: int = 3, cap_micros: int = 37, minimum: float = 150.0) -> float:
    """Descriptive (P-04 §4), from the log alone: the share of days with an entry on which one account harvesting at
    1:1 with `risk` dollars, taking up to `max_trades` of the day's entries in order (whole micros, capped), would
    net at least `minimum` dollars."""
    x = table[table[f"dist_{scale}"].notna() & table["d"].isin(days)].sort_values(["d", "entry_t"])
    ok = n = 0
    for _, y in x.groupby("d"):
        y = y.head(max_trades)
        c = np.minimum(np.floor(risk / y[f"rpc_{scale}"].to_numpy(float)), cap_micros)
        pnl = float((c * y[f"rpc_{scale}"].to_numpy(float) * y[f"v1_{scale}"].to_numpy(float)).sum())
        n += 1
        ok += pnl >= minimum
    return ok / n if n else float("nan")


#: Topstep's temporary MCL restriction (13613539, read 2026-09-27; not modelled, P-04 §3): the 50K Combine's ceiling,
#: and the 50K XFA's restricted-symbol ladder read as mini-equivalents of ten micros (UNVERIFIED reading).
MCL_RESTRICTION = {"combine_micros": 30, "xfa_below_2000_micros": 10, "xfa_from_2000_micros": 30}
#: The sizing caps P-04 §3 applies in each state (75 % headroom, D-117): the Combine's 50 micros; the build state's
#: lowest XFA tier, 2 minis (20 micros, below a $1,500 balance); the harvest state's 5 minis (from $2,000).
STATE_CAP_MICROS = {"combine": 37, "build": 15, "harvest": 37}


def mcl_restriction_exposure(table: pd.DataFrame, scale: str = "p") -> dict[str, float]:
    """Descriptive (P-04 §4): the share of CL entries whose size in each lifecycle state (whole micros at the state's
    risk, capped as P-04 sizes that state) would exceed Topstep's temporary MCL restriction."""
    x = table[(table["market"] == "CL") & table[f"dist_{scale}"].notna()]
    if not len(x):
        return {"mcl_entries": 0}
    rpc = x[f"rpc_{scale}"].to_numpy(float)
    n = lambda risk, state: np.minimum(np.floor(risk / rpc), STATE_CAP_MICROS[state])    # noqa: E731
    return {"mcl_entries": int(len(x)),
            "share_over_restriction_combine": float((n(1500.0, "combine") > MCL_RESTRICTION["combine_micros"]).mean()),
            "share_over_restriction_build": float((n(1000.0, "build") > MCL_RESTRICTION["xfa_below_2000_micros"]).mean()),
            "share_over_restriction_harvest": float((n(300.0, "harvest")
                                                     > MCL_RESTRICTION["xfa_from_2000_micros"]).mean())}


def session_counts(market: str, sessions: pd.DataFrame, days: Sequence[str],
                   tail: Sequence[str] = ()) -> dict[str, int]:
    """P-04 §3's per-market counts: sessions traded, scheduled full sessions skipped by reason, late opens (record
    only) and scheduled full sessions with no data (the sessions' `gone` lists and HEAD's `tail`, as `day_set` reads
    them), inside the period's day set."""
    s = sessions[sessions["d"].isin(days)]
    full = s[s["cal"] == "F"]
    gone = {x for g in sessions["gone"] for x in str(g).split(",") if x} | set(tail)
    out = {f"{market}_sessions_traded": int((full["sk"] == "").sum()),
           f"{market}_late_opens_record_only": int((s["cal"] == "L").sum()),
           f"{market}_scheduled_no_data": len(gone & set(days))}
    for reason, k in full.loc[full["sk"] != "", "sk"].value_counts().items():
        out[f"{market}_skipped_{reason}"] = int(k)
    return out


__all__ = ["MARKETS", "SCALES", "RR_ALL", "RR_GATE", "SEED", "MICRO_ENDS_EARLY", "expiry_date", "micro_expiry_flags",
           "LAST_TRADE_CORRECTIONS", "last_trade_date", "review_split", "FeesNotReady", "config", "fees", "micro_specs",
           "read_run", "day_set", "hot_slots", "entry_table", "edge", "blocks", "policy", "protocol",
           "combine_stats", "run_gate", "kill_lines", "harvest_day_share", "MCL_RESTRICTION", "STATE_CAP_MICROS",
           "mcl_restriction_exposure", "session_counts"]
