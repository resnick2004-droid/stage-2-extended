"""Model verification (D-148): every exported trade checked against the rules its model declared, and a seeded
sample of trades for the operator to review on a chart.

Two questions, answered separately (docs/MODEL_VERIFICATION.md):

* **Does the code follow the written rules?** `run_checks` applies a model's declared checks to every trade the cloud
  exported -- sessions, sequencing, stops, exits, costs -- and counts violations. Zero is required before a result
  is used; a violation is a kit or scorer defect, diagnosed under the failure protocol, never waved through.
* **Do the written rules match the idea?** No automated check can answer that. `review_sample` draws a seeded set
  of trades (random, plus the best and worst) for the operator to check on a one-minute chart; the sheet carries the
  times in CT and ET and, for kits made under D-148, the prices of every level the rules used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
import pandas as pd

#: What every kit made under D-148 exports per trade, at ACTUAL prices (never the rescaled ones), beside the model's
#: own key levels (FV1's would be fair value and the swing level broken). D-156 adds `mae_px`, the worst price against
#: the position before its exit.
AUDIT_PRICE_FIELDS = ("entry_px", "stop_px", "target_px", "exit_px", "mae_px")

#: D-156: what every kit exports per trade so the campaign can settle it exactly -- its maximum adverse excursion
#: before its exit, in R at the trade's stop (`mae`). A trade that risks more than the room above the barrier ends at
#: the barrier if its path reached it (`propedge.outcomes.settlement`); without `mae` the campaign gives only the
#: pessimistic bound.
SETTLEMENT_FIELDS = ("mae",)

#: Questions every chart review answers per trade; a model adds its own (FV1: is it a displacement candle? would you
#: call the break a BOS or MSB?).
REVIEW_QUESTIONS = ("setup valid on the chart (y/n)", "entry, stop and target where the rules put them (y/n)",
                    "exit where and when the chart says (y/n)", "note")
#: D-185: the reviewer also records how far each fill sat from the modelled price, in ticks (blank = none).
FILL_DISCREPANCY_COL = "fill discrepancy (ticks from the modelled price)"
#: D-185's acceptance criterion: zero rule violations (no "n" to any y/n question) and at most this many fills more
#: than one tick from the modelled price; anything else fails the run's verification and blocks scoring.
MAX_FILL_DISCREPANCIES, FILL_TICK_THRESHOLD = 2, 1.0


@dataclass(frozen=True)
class Check:
    """One declared rule, as a function from the trade table to a boolean Series (True = violated) or a count."""

    name: str
    fn: Callable[[pd.DataFrame], "pd.Series | int"]


def run_checks(trades: pd.DataFrame, checks: Sequence[Check]) -> dict[str, int]:
    """Violations per check, every check listed (zeros included)."""
    out = {}
    for c in checks:
        v = c.fn(trades)
        out[c.name] = int(v) if np.isscalar(v) else int(np.asarray(v, dtype=bool).sum())
    return out


def missing_fields(trades: pd.DataFrame) -> list[str]:
    """The D-148 audit prices and D-156 settlement fields a trade table lacks; a kit made after D-156 lacks none."""
    return [f for f in (*AUDIT_PRICE_FIELDS, *SETTLEMENT_FIELDS) if f not in trades.columns]


def mae_checks(r_col: str = "r_price") -> list[Check]:
    """D-156: every model's MAE checked for what any path must satisfy. `r_col` is the trade's price-only R (before
    costs); a trade's MAE is at least the loss it closed at, less one tick of fill where `stop_ticks` is known."""

    def below_loss(t):
        tick = 1.0 / t["stop_ticks"] if "stop_ticks" in t else 0.05
        return t["mae"] < -t[r_col] - tick - 1e-3

    return [
        Check("MAE missing (D-156)", lambda t: t["mae"].isna() if "mae" in t else len(t)),
        Check("MAE negative", lambda t: t["mae"] < -1e-9 if "mae" in t else 0),
        Check("MAE smaller than the loss the trade closed at", lambda t: below_loss(t) if "mae" in t else 0),
    ]


# ------------------------------------------------------------------------------------------------ FV1's rules


def fv1_checks(params: dict) -> list[Check]:
    """FV1's declared rules (config/model_fv.yaml; `qc_algorithms.fv_params(market)`) as checks on its trade table
    (`fv_score.split`)."""
    P, F = params["p"], params["fills"]
    S = {s["name"]: s for s in P["sessions"]}
    first = lambda t: t["session"].map(lambda s: S[s]["first"])            # noqa: E731
    last = lambda t: t["session"].map(lambda s: S[s]["last"])              # noqa: E731
    cont = lambda t: t["session"].map(lambda s: S[s]["cont_until"])        # noqa: E731
    inv = lambda t: 1.0 / t["stop_ticks"]                                  # noqa: E731
    slip = {"t": F["target"], "s": F["stop"], "g": F["stop"], "m": F["flatten"]}

    def costs(t):
        want = (t["r_price"] - (t["exit_kind"].map(slip) + F["entry"]) / t["stop_ticks"]
                - F["round_turn"] / (t["stop_ticks"] * F["tick_value"]))
        return (t["r_net"] - want).abs() > 2e-4

    def sequencing(t, what):
        n = 0
        for _, g in t.groupby(["n", "family", "scale"], sort=False):
            g = g.sort_values("t")
            if what == "overlap":
                n += int((g["t"].values[1:] <= g["j_exit"].values[:-1]).sum())
            elif what == "daily_stop":
                n += int((np.cumsum(g["r_net"].values < 0)[:-1] >= P["max_losses"]).sum())
            else:
                ph = np.where(g["t"].values <= g["session"].map(lambda s: S[s]["cont_until"]).values, "c", "r")
                n += int(pd.Series(list(zip(g["session"], ph))).value_counts().gt(P["attempts"]).sum())
        return n

    return [
        Check("signal outside its session window", lambda t: (t["t"] < first(t)) | (t["t"] > last(t))),
        Check("entry not after the signal bar", lambda t: t["j0"] <= t["t"]),
        Check("exit before entry or after the time exit",
              lambda t: (t["j_exit"] < t["j0"]) | (t["j_exit"] > P["last_slot"])),
        Check("stop inside the cost floor", lambda t: t["stop_ticks"] < P["floor_ticks"]),
        Check("continuation tag outside the continuation phase", lambda t: (t["tag"] == "cont") & (t["t"] > cont(t))),
        Check("reversion tag inside the continuation phase",
              lambda t: t["tag"].isin(["rev", "recont"]) & (t["t"] <= cont(t))),
        Check("ATR band inconsistent with the stop family",
              lambda t: ((t["family"] == "atr_bands") & (t["band"] < 0)) | ((t["family"] == "structural")
                                                                           & (t["band"] != -1))),
        Check("target exit not at +1.5R",
              lambda t: (t["exit_kind"] == "t") & ((t["r_price"] - (P["rr"] + inv(t))).abs() > 2e-4)),
        Check("stop exit not at -1R", lambda t: (t["exit_kind"] == "s") & ((t["r_price"] - (-1 + inv(t))).abs() > 2e-4)),
        Check("gap exit better than the stop", lambda t: (t["exit_kind"] == "g") & (t["r_price"] > -1 + inv(t) + 2e-4)),
        Check("time exit outside the bracket",
              lambda t: (t["exit_kind"] == "m") & ((t["r_price"] < -1 + inv(t) - 2e-4)
                                                   | (t["r_price"] > P["rr"] + inv(t) + 2e-4))),
        Check("target filled without the price trading through it",
              lambda t: (t["exit_kind"] == "t") & (t["mfe"] < P["rr"] - 1e-3)),
        Check("stop filled without the price reaching it", lambda t: (t["exit_kind"] == "s") & (t["mae"] < 1.0 - 1e-3)),
        Check("costs not applied as declared", costs),
        Check("overlapping positions", lambda t: sequencing(t, "overlap")),
        Check("trade after the daily stop", lambda t: sequencing(t, "daily_stop")),
        Check("more attempts in a phase than allowed", lambda t: sequencing(t, "attempts")),
    ]


# ------------------------------------------------------------------------------------------------ IM2's rules


def im2_checks(params: dict, days: pd.DataFrame, scale: str = "p") -> list[Check]:
    """IM2's declared rules (P-04 §3; `qc_algorithms.im2_params(market)`) as checks on one market's entry table
    (`manual_parsers.parse_im2`, kind 'entry'), at one scale ('p' the reference price, 'a' actual prices). `days` is
    the same run's session table (kind 'day'), for the calendar, the open, the prior close and the release minutes."""
    P, F = params["p"], params["fills"]
    rr = list(P["rr"])
    day = days.set_index("d")
    tol = 1e-4
    open_min, hot_n = int(params["open_min"]), int(params["hot_minutes"])

    def on(t, col):
        return t["d"].map(day[col])

    def hot(t, j):
        """Whether slot j of each row's session is inside a release window (P-04: the release minute and the next)."""
        rel = on(t, "rel").fillna("").astype(str)
        return pd.Series([any(0 <= int(jj) - (int(m) - open_min) < hot_n for m in s.split(",") if m)
                          for s, jj in zip(rel, j)], index=t.index)

    def inv(t, kind="stop"):
        """The fill's ticks for an exit kind ('stop' or 'flatten'), in R."""
        return F["tick"] * F[kind] / t[f"dist_{scale}"]

    def by_r(fn):
        def run(t):
            bad = pd.Series(False, index=t.index)
            for R in rr:
                bad |= fn(t, R, t[f"kind{R}_{scale}"], t[f"r{R}_{scale}"], t[f"mae{R}_{scale}"], t[f"j{R}_{scale}"])
            return bad & t[f"dist_{scale}"].notna()
        return run

    def monotone(t):
        bad = pd.Series(False, index=t.index)
        for lo, hi in zip(rr, rr[1:]):
            kl, kh = t[f"kind{lo}_{scale}"], t[f"kind{hi}_{scale}"]
            jl, jh = t[f"j{lo}_{scale}"], t[f"j{hi}_{scale}"]
            bad |= (kl == "t") & (jh < jl)                                  # a farther target cannot come sooner
            bad |= (kl != "t") & ((kh != kl) | (jh != jl))                  # no nearer target: the same exit
        return bad & t[f"dist_{scale}"].notna()

    def sequencing(t):
        """P-04: the market waits for the later of the two scales' 2:1 exits (a missing walk's slot is -1), so at
        neither scale does a new entry open while the market is held."""
        n = 0
        for _, g in t.groupby("d", sort=False):
            g = g.sort_values("t")
            end = np.maximum(g[f"j{P['seq_rr']}_p"].to_numpy(float), g[f"j{P['seq_rr']}_a"].to_numpy(float))
            n += int((g["t"].values[1:] < end[:-1] + P["wait"]).sum())
        return n

    def signal(t):
        up = (t["cl"] > t["ub"]) & (t["cl"] > t["vw"])
        dn = (t["cl"] < t["lb"]) & (t["cl"] < t["vw"])
        return ~(((t["side"] > 0) & up) | ((t["side"] < 0) & dn))

    def bands(t):
        ref, pc = on(t, "ref"), on(t, "pc")
        s_up = t["ub"] / np.maximum(ref, pc) - 1.0
        s_dn = 1.0 - t["lb"] / np.minimum(ref, pc)
        return ((s_up - s_dn).abs() > 1e-7) | (s_up < 0)

    def session(t):
        cal, sk = on(t, "cal"), on(t, "sk").fillna("")
        ok = ((cal == "F") & (sk == "")) | ((cal == "L") & (sk == "late"))    # a late open's entries: record only
        return ~ok | (on(t, "np") < P["lookback"])

    return [
        Check("entry on a session not traded (calendar, prior close, lookback)", session),
        Check("decision off the half-hour grid", lambda t: ~t["t"].isin(P["times"])),
        Check("entry not after the decision bar", lambda t: t["j0"] <= t["t"]),
        Check("signal does not satisfy the band and VWAP rule", signal),
        Check("bands not max/min(open, prior close) x (1 +/- one sigma)", bands),
        Check("no walk at the reference price", lambda t: t["dist_p"].isna() | (t["dist_p"] <= 0)),
        Check("stop distance not a whole number of ticks (orders off the grid, P-04)",
              lambda t: t[f"dist_{scale}"].notna() & ((t[f"dist_{scale}"] / F["tick"]
                                                       - (t[f"dist_{scale}"] / F["tick"]).round()).abs() > 1e-5)),
        Check("exit before entry or after the close",
              by_r(lambda t, R, k, r, m, j: (j < t["j0"]) | (j > P["last_slot"]))),
        Check("target exit not at +R", by_r(lambda t, R, k, r, m, j: (k == "t") & ((r - R).abs() > tol))),
        Check("stop exit not at the stop's fill (a release minute: no better than it)",
              by_r(lambda t, R, k, r, m, j: (k == "s") & (((r + 1 + inv(t)).abs() > tol) & ~hot(t, j)
                                                          | ((r > -1 - inv(t) + tol) & hot(t, j))))),
        Check("gap exit better than the stop", by_r(lambda t, R, k, r, m, j: (k == "g") & (r > -1 + tol))),
        Check("time exit outside the bracket",
              by_r(lambda t, R, k, r, m, j: (k == "m") & ((r < -1 - inv(t, "flatten") - tol) | (r > R + tol)))),
        Check("MAE below the loss closed at, or negative", by_r(lambda t, R, k, r, m, j: (m < -r - tol) | (m < -1e-9))),
        Check("MAE reached the stop without a stop exit",
              by_r(lambda t, R, k, r, m, j: ((k == "t") & (m >= 1 - 1e-9))
                   | ((k == "m") & (m > 1 + inv(t, "flatten") + tol)))),
        Check("brackets on one entry disagree", monotone),
        Check("a market entered inside the 2:1 bracket plus the wait", sequencing),
    ]


def im2_cost_checks(round_turn: dict[str, float], point_value: dict[str, float], rr: Sequence[int],
                    scale: str = "p") -> list[Check]:
    """P-04: the scorer's net outcomes (`im2_score.entry_table`, `u{R}_{scale}`) against the kit's outcomes after the
    fills' ticks (`r{R}_{scale}`) less one micro's round turn over one micro's risk (`dist_{scale}` x the micro's
    point value), per market, before the cost sensitivity and the price-lock treatment (which the scorer applies in
    separate columns)."""

    def costs(t):
        rpc = t[f"dist_{scale}"] * t["market"].map(point_value)
        cost = t["market"].map(round_turn) / rpc
        bad = pd.Series(False, index=t.index)
        for R in rr:
            r, u = t[f"r{R}_{scale}"], t[f"u{R}_{scale}"]
            bad |= r.notna() & (u.isna() | ((u - (r - cost)).abs() > 1e-9))
        return bad

    return [Check("costs not applied as declared (one micro's round turn over its risk)", costs)]


# ------------------------------------------------------------------------------------------------ the chart review


def _et(ct: str) -> str:
    h, m = (int(x) for x in ct.split(":"))
    return f"{h + 1:02d}:{m:02d}"


def review_sample(log: pd.DataFrame, *, n: int, seed: int, extremes: int = 3, r_col: str = "r_net") -> pd.DataFrame:
    """A seeded sample for the chart review: `n` trades at random plus the `extremes` best and worst by `r_col`,
    in date order, with ET times beside CT ones and a blank column per review question."""
    rng = np.random.default_rng(seed)
    pick = set(rng.choice(len(log), size=min(n, len(log)), replace=False).tolist())
    order = np.argsort(log[r_col].to_numpy())
    # `order[-0:]` is the whole array, so no extremes must mean none (D-198 draws a stratum with extremes=0)
    best = set(order[-extremes:].tolist()) if extremes > 0 else set()
    worst = set(order[:extremes].tolist()) if extremes > 0 else set()
    pick |= best | worst
    s = log.iloc[sorted(pick)].copy()
    s.insert(0, "why", ["best" if i in best else "worst" if i in worst else "random" for i in sorted(pick)])
    for col in [c for c in s.columns if c.endswith("_ct")]:
        s[col.replace("_ct", "_et")] = s[col].map(_et)
    for q in REVIEW_QUESTIONS:
        s[q] = ""
    s[FILL_DISCREPANCY_COL] = ""
    return s.reset_index(drop=True)


def review_verdict(sheet: pd.DataFrame, *, max_fill_discrepancies: int = MAX_FILL_DISCREPANCIES,
                   tick_threshold: float = FILL_TICK_THRESHOLD) -> dict:
    """D-185: the completed chart-review sheet against the acceptance criterion. Every y/n question must be answered
    on every trade (else the review is incomplete and does not pass); any "n" is a rule violation; a fill
    discrepancy above `tick_threshold` ticks counts, and more than `max_fill_discrepancies` of them fail."""
    yn = [q for q in REVIEW_QUESTIONS if q.endswith("(y/n)")]
    ans = sheet[yn].astype(str).apply(lambda c: c.str.strip().str.lower())
    incomplete = int((~ans.isin(["y", "n"])).any(axis=1).sum())
    violations = int((ans == "n").sum().sum())
    ticks = pd.to_numeric(sheet[FILL_DISCREPANCY_COL], errors="coerce").fillna(0.0) if FILL_DISCREPANCY_COL in sheet \
        else pd.Series(0.0, index=sheet.index)
    over = int((ticks > tick_threshold).sum())
    complete = incomplete == 0
    return {"trades": int(len(sheet)), "incomplete": incomplete, "rule_violations": violations,
            "fill_discrepancies_over_one_tick": over, "max_fill_discrepancies": int(max_fill_discrepancies),
            "complete": complete, "passed": bool(complete and violations == 0 and over <= max_fill_discrepancies)}


__all__ = ["AUDIT_PRICE_FIELDS", "SETTLEMENT_FIELDS", "REVIEW_QUESTIONS", "Check", "run_checks", "missing_fields",
           "mae_checks", "fv1_checks", "im2_checks", "im2_cost_checks", "review_sample", "review_verdict",
           "FILL_DISCREPANCY_COL", "MAX_FILL_DISCREPANCIES", "FILL_TICK_THRESHOLD"]
