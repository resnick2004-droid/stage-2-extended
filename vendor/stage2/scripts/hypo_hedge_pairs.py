"""HYPOTHETICAL structure study (D-153): what a cross-account hedge would do to the contract's economics.

    python scripts/hypo_hedge_pairs.py

NOT A CANDIDATE. Holding opposite positions across accounts is prohibited (Prohibited Conduct 10296582,
"Cross-account hedging (single-user)"), a tier-1 rule under D-145 that this study does not change. The operator asked
(2026-09-26) to understand the contract's structure, not to trade it; nothing here is ranked, sized or carried into a
model, and no payout denial is applied because the question is what the structure would do if the rule did not exist.

The pair: every day at 08:35 CT, the bracket map's LONG and SHORT entries at the session-scale stop (0.4 of D) from the
same real price path (NQ and ES, 2009-2019 development data). One account takes the long, the other the short, from
the same start day; each then lives its own lifecycle: the Combine at stage one's zero-edge geometry, 1:1 at $1,500 one
trade a day (propsim D-08), and on a pass the funded account at stage one's static 2:1 at $750 (propsim D-10), both
read from the same entries, until the account closes or the window ends. Compared with one account always long and one
account whose side is a coin flip each day (seeded).

Every start day in the history is one attempt over the next WINDOW sessions, replayed on the days as they happened,
through `propedge.campaign.lockstep`'s CombineAccount and FundedAccount with the verified rules. Fees: the Combine
subscription per billing period and the activation fee on a pass; payouts net of split and fee. Adjacent start days
share most of their history, so the spreads are descriptive, not inference. Writes results/hypo_hedge_pairs.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.campaign.lockstep import CombineAccount, FundedAccount  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import bmap_score as bs  # noqa: E402

SCRIPT = "scripts/hypo_hedge_pairs.py"
SEED = 20261110
WI, T = 2, 35                   # the session-scale stop, 0.4 of D; 08:35 CT
WINDOW = 504                    # sessions per attempt, as the campaign horizon
PROTOCOL = Protocol("hypo_hedge_s1", combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=750.0,
                    trades_per_day=1, family="hypothetical", source="propsim D-08, D-10",
                    note="D-153: a structure study of a prohibited pattern, never a candidate")
LABEL = "HYPOTHETICAL: cross-account hedging is prohibited (10296582, tier 1); a structure study, not a candidate"


#: D-156: how a trade that risks more than the room settles. The bracket map records no MAE, so the default is the
#: pessimistic bound; `--settlement legacy` reproduces the pre-D-156 files (the optimistic bound).
SETTLEMENT = sys.argv[sys.argv.index("--settlement") + 1] if "--settlement" in sys.argv else "pessimistic"
SUFFIX = "" if SETTLEMENT == "legacy" else "_d156"


class _Seq:
    """A draw over a fixed sequence of daily P&L from `offset` (NaN = no trade that day), each trade risking `risk`
    dollars and settled against the room the engine hands it (D-156)."""

    def __init__(self, pnl, offset, risk, settlement=None):
        self.pnl, self.offset, self.risk = pnl, offset, float(risk)
        self.settlement = settlement or SETTLEMENT

    def __call__(self, n, day, slot, cushion):
        from propedge.outcomes.settlement import settle

        i = self.offset + day
        v = self.pnl[i] if slot == 0 and i < len(self.pnl) else np.nan
        return settle(np.array([v]), self.risk, None, np.asarray(cushion, dtype=float), self.settlement)


def _lifecycle(c_pnl, f_pnl, start, rules, cap):
    """One account from `start`: the Combine, then the funded account on a pass, to start + WINDOW."""
    end = min(start + WINDOW, len(c_pnl))
    cpol, fpol = PROTOCOL.combine_policy(), PROTOCOL.funded_policy()
    acc = CombineAccount(index=0, purchase_day=start - 1, draw=_Seq(c_pnl, start, PROTOCOL.combine_risk),
                         floor_start=-rules.mll)
    d = start
    while acc.alive and d < end:
        acc.trade_day(rules, cpol, d - start, d)
        d += 1
    combine_fees = rules.subscription * (1 + max(acc.days - 1, 0) // rules.billing_days)
    out = {"passed": acc.passed, "combine_fees": combine_fees, "activation": 0.0, "payouts": 0.0,
           "first_payout": -1, "combine_days": acc.days}
    if not acc.passed or d >= end:
        return out
    out["activation"] = rules.activation
    fa = FundedAccount(index=0, activation_day=d - 1, draw=_Seq(f_pnl, d, PROTOCOL.funded_risk), horizon_days=end - d,
                       floor_start=rules.xfa_mll_start)
    f0 = d
    while fa.alive and d < end:
        net = fa.trade_day(rules, fpol, cap, d - f0, d)
        if net is not None:
            out["payouts"] += net
            if out["first_payout"] < 0:
                out["first_payout"] = d - start
        d += 1
    return out


def _structure(market, name, parts):
    """Summarise one structure: `parts` is a list of per-attempt frames whose rows are summed (a pair has two)."""
    passes = sum(p["passed"].astype(int) for p in parts)
    cfees = sum(p["combine_fees"] for p in parts)
    fees = cfees + sum(p["activation"] for p in parts)
    pay = sum(p["payouts"] for p in parts)
    net = pay - fees
    firsts = np.column_stack([p["first_payout"].to_numpy() for p in parts]).astype(float)
    firsts[firsts < 0] = np.nan
    first = np.nanmin(np.where(np.isnan(firsts), np.inf, firsts), axis=1)
    first[np.isinf(first)] = np.nan
    per100 = 100 * net / fees
    # what two accounts with these same chances would give if their outcomes were unrelated (the product rule)
    q = [float((~p["passed"]).mean()) for p in parts]
    a = [float((p["first_payout"] >= 0).mean()) for p in parts]
    return {"market": market, "structure": name, "accounts": len(parts), "attempts": len(net),
            "combine_passes_per_attempt": float(passes.mean()),
            "combine_passes_per_100_usd_combine_fees": float(100 * passes.sum() / cfees.sum()),
            "share_no_combine_pass": float((passes == 0).mean()),
            "mean_fees": float(fees.mean()), "mean_payouts_net": float(pay.mean()), "mean_net_cash": float(net.mean()),
            "net_cash_per_100_usd_fees": float(100 * net.sum() / fees.sum()),
            "share_with_any_payout": float(np.isfinite(first).mean()),
            "share_losing_money": float((net < 0).mean()),
            "sd_net_per_100_usd_fees": float(per100.std(ddof=1)),
            "p05_net_per_100_usd_fees": float(np.percentile(per100, 5)),
            "median_days_to_first_payout": float(np.nanmedian(first)) if np.isfinite(first).any() else float("nan"),
            "if_unrelated_share_no_combine_pass": float(np.prod(q)),
            "if_unrelated_share_with_any_payout": float(1 - np.prod([1 - x for x in a]))}


def _entries(cfg, fm, market, runs):
    """The 08:35 entries of `runs` for one market, and the fill costs to read them with."""
    mk = cfg["markets"][market]
    fills = {"target": fm.target_slippage_ticks, "stop": fm.stop_slippage_ticks,
             "flatten": fm.flatten_slippage_ticks, "round_turn": float(mk["round_turn"]),
             "tick_value": float(mk["tick_value"])}
    parts = [bs.split(read_result(ROOT / "results" / f"manual_{r.replace('-', '_')}.csv")) for r in runs]
    ent = pd.concat([p[1].assign(n=p[1]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
    return ent[ent["t"] == T], fills


def _sequences(ent, fills, rng):
    """Daily P&L by (side, leg) -- side 1 long, -1 short, 0 the coin flip; leg c Combine, f funded -- over the days
    both sides have an entry, and those days' numbers."""
    seq = {}
    for side in (1, -1):
        e = ent[ent["side"] == side].sort_values("n")
        for leg, k, risk in (("c", PROTOCOL.combine_rr, PROTOCOL.combine_risk),
                             ("f", PROTOCOL.funded_rr, PROTOCOL.funded_risk)):
            o = bs.outcome(e, WI, k, fills)
            seq[(side, leg)] = pd.Series(np.where(o["ok"], o["r_net"], np.nan) * risk, index=e["n"].to_numpy())
    days = sorted(set(seq[(1, "c")].index) & set(seq[(-1, "c")].index))
    s = {key: v.reindex(days).to_numpy() for key, v in seq.items()}
    flip = rng.random(len(days)) < 0.5
    s[(0, "c")] = np.where(flip, s[(1, "c")], s[(-1, "c")])
    s[(0, "f")] = np.where(flip, s[(1, "f")], s[(-1, "f")])
    return s, days


def _sweep(market, s, rules, cap):
    """Every start day's lifecycle for the long, short and coin-flip accounts; the four structures' summaries."""
    rows = {1: [], -1: [], 0: []}
    for start in range(0, len(s[(1, "c")]) - WINDOW + 1):
        for side in rows:
            rows[side].append(_lifecycle(s[(side, "c")], s[(side, "f")], start, rules, cap))
    long_, short_, coin = (pd.DataFrame(rows[k]) for k in (1, -1, 0))
    return [_structure(market, "single_long", [long_]),
            _structure(market, "single_short", [short_]),
            _structure(market, "single_coin_flip", [coin]),
            _structure(market, "hedged_pair_long_and_short", [long_, short_])], len(long_)


def _high_vix(dates):
    """The operator's entry idea with the implied-volatility data on hand (R040, 2009-2014): VIX relative to its
    trailing 120-session median, known at the previous close, in the top tercile -- the definition of
    results/bmap_vix_check.csv, whose tercile cut is taken on the sample itself. VIX is the S&P 500's implied
    volatility; for NQ it stands in for VXN, which the atlas did not record. Returns (high, known) per date."""
    vix = read_result(ROOT / "results" / "manual_R040_atlas_context2.csv")
    vix["date"] = pd.to_datetime(vix["d"].astype(int).astype(str), format="%Y%m%d")
    vix = vix.sort_values("date")
    vix["vix_rel"] = vix["vix"] / vix["vix"].rolling(120, min_periods=60).median()
    vix["vix_rel_prev"] = vix["vix_rel"].shift(1)
    x = pd.DataFrame({"date": pd.to_datetime(dates)}).merge(vix[["date", "vix_rel_prev"]], on="date", how="left")
    x = x["vix_rel_prev"]
    return (x >= x.dropna().quantile(2 / 3)).to_numpy(), x.notna().to_numpy()


def main_vix() -> int:
    """`--vix`: the same pair and single accounts on 2009-2014, trading every day or only on high relative VIX days;
    on the other days every account sits out (the days still pass, and the subscription with them)."""
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    rules = rules_for_method("aeropay")
    cap = rules.std_cap if PROTOCOL.payout_path == "standard" else rules.cons_cap
    fm = FillModel.load("assumed")
    rng = np.random.default_rng(SEED)
    summary = []
    for market, runs in cfg["runs"].items():
        ent, fills = _entries(cfg, fm, market, runs[:1])        # the 2009-2014 run: the span VIX covers
        dates = ent.drop_duplicates("n").set_index("n")["date"]
        _, known = _high_vix(dates.to_numpy())
        ent = ent[ent["n"].isin(dates.index[known])]
        s, days = _sequences(ent, fills, rng)
        high, _ = _high_vix(dates.reindex(days).to_numpy())
        for label, mask in (("every day", np.ones(len(days), bool)), ("high relative VIX (top tercile)", high)):
            masked = {key: np.where(mask, v, np.nan) for key, v in s.items()}
            rows, starts = _sweep(market, masked, rules, cap)
            summary += [{"days_traded": label, "share_of_days_traded": float(mask.mean()), **r} for r in rows]
            print(f"[{market}] {label}: {len(days)} sessions, {starts} start days", flush=True)
    out = pd.DataFrame(summary)
    VariantCounter().record(prereg_id="D-153:hypothetical_hedge", params={"structures": sorted(set(out["structure"])),
                            "markets": sorted(set(out["market"])), "window": WINDOW, "days": "high relative VIX"},
                            seed=SEED, exploratory=True, label=LABEL)
    write_result(out, "hypo_hedge_pairs_vix" + SUFFIX, script=SCRIPT + " --vix", seed=SEED, exploratory=True,
                 parameters={"combine": "1:1 at $1,500, one trade a day (propsim D-08)",
                             "funded": "static 2:1 at $750, standard path (propsim D-10)", "entry": "08:35 CT",
                             "stop": "0.4 of D", "window_sessions": WINDOW, "data": "2009-06 to 2014-05 (R049, R051)",
                             "vix": "R040, prior close, relative to its trailing 120-session median; top tercile, cut "
                                    "on the sample (as results/bmap_vix_check.csv); VIX stands in for VXN on NQ",
                             "rules": "rules_for_method('aeropay') from the verified ledger", "denial_p": 0.0, "settlement": SETTLEMENT,
                             "conduct_model": "none: the pattern is tier 1"},
                 notes={"decision": "D-153", "status": LABEL + "; the tercile cut sees the whole sample"},
                 description="HYPOTHETICAL: the long/short pair and single accounts trading every day or only on "
                             "high relative VIX days, through the Combine and funded lifecycle, 2009-2014.")
    pd.set_option("display.width", 250)
    print(LABEL)
    cols = ["market", "days_traded", "structure", "combine_passes_per_attempt", "share_no_combine_pass",
            "if_unrelated_share_no_combine_pass", "share_with_any_payout", "if_unrelated_share_with_any_payout",
            "mean_fees", "net_cash_per_100_usd_fees", "share_losing_money", "median_days_to_first_payout"]
    print(out[cols].round(3).to_string(index=False))
    return 0


def main() -> int:
    if "--vix" in sys.argv[1:]:
        return main_vix()
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    rules = rules_for_method("aeropay")
    cap = rules.std_cap if PROTOCOL.payout_path == "standard" else rules.cons_cap
    fm = FillModel.load("assumed")
    rng = np.random.default_rng(SEED)
    summary = []
    for market, runs in cfg["runs"].items():
        ent, fills = _entries(cfg, fm, market, runs)
        s, days = _sequences(ent, fills, rng)
        rows, starts = _sweep(market, s, rules, cap)
        summary += rows
        print(f"[{market}] {len(days)} sessions, {starts} start days", flush=True)
    out = pd.DataFrame(summary)
    VariantCounter().record(prereg_id="D-153:hypothetical_hedge", params={"structures": sorted(set(out["structure"])),
                            "markets": sorted(set(out["market"])), "window": WINDOW}, seed=SEED, exploratory=True,
                            label=LABEL)
    write_result(out, "hypo_hedge_pairs" + SUFFIX, script=SCRIPT, seed=SEED, exploratory=True,
                 parameters={"combine": "1:1 at $1,500, one trade a day (propsim D-08)",
                             "funded": "static 2:1 at $750, standard path (propsim D-10)", "entry": "08:35 CT",
                             "stop": "0.4 of D", "window_sessions": WINDOW, "data": "2009-2019 development (D-144)",
                             "rules": "rules_for_method('aeropay') from the verified ledger", "denial_p": 0.0, "settlement": SETTLEMENT,
                             "conduct_model": "none: the pattern is tier 1"},
                 notes={"decision": "D-153", "status": LABEL},
                 description="HYPOTHETICAL: a long account and a short account started together, against single "
                             "accounts, through the Combine and funded lifecycle on the days as they happened.")
    pd.set_option("display.width", 250)
    print(LABEL)
    print(out.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
