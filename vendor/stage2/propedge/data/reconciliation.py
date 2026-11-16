"""The `docs/PIPELINE.md` §5 reconciliation comparison (D-80, D-83).

Each trade record from a reconciliation run (`R002`-`R004`, ingested by
`scripts/ingest_manual_run.py`) carries LEAN's fills and the evidence needed to decide, without
LEAN, what `propedge`'s fill model says should have happened: the intended entry price, the
highest high and lowest low **before** the exit bar, and the exit bar itself. This module replays
every trade through `propedge.execution.fills.FillModel` and compares.

Stage rules, from §5:

  **A** (profile `zero_cost_gap_fill`, D-83): exit reason identical on every trade, and
        `pnl_gross` identical **to the tick** on every trade. No tolerance: both sides are
        deterministic given the same bars, and a tolerance would hide the disagreements the test
        exists to find.
  **B** (profile `assumed`): `pnl_net` to the cent per trade, and `commission` and
        `slippage_dollars` to the cent per trade -- not in aggregate, where a sign error on one leg
        can net off.
  **C** (LEAN's defaults, compared against stage A's profile): the **negative control**. It passes
        only if each named failure mode is caught at least once: a target filled on a touch, a gapped
        stop filled at the stop price, and fraction-of-price slippage. A failure mode the year never
        exercised is reported as *not exercised*, and the control has then not been shown to work.

Exit reasons `flatten` and `flatten_close` (an early close) are both a market exit to propedge.
Tie-break inside one bar is declared, not inferred: **the stop wins** (qc_algorithms.RepoFillModel).
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from propedge.data import qc_algorithms as alg
from propedge.execution.fills import ExitReason, FillModel, Side
from propedge.execution.instruments import get_instrument

PRICE_EPS = 1e-9          # prices are exact multiples of the tick; this only absorbs float noise
CENT = 0.005              # "to the cent"

STAGE_NAMES = {"A": "A_zero_cost_exact", "B": "B_costs_on", "C": "C_negative_control_failed"}
C_FAILURE_MODES = ("touch_filled_target", "gapped_stop_filled_at_stop", "fraction_of_price_slippage")

_NUMERIC = ["ref", "ent", "st", "tg", "xf", "mx", "mn", "xo", "xh", "xl", "xc", "efee", "fee"]


def _num(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in _NUMERIC:
        if c in out:
            out[c] = pd.to_numeric(out[c].replace("", float("nan")), errors="coerce")
    return out


@dataclass(frozen=True)
class Replay:
    reason: str
    entry: float
    exit: float
    stop: float
    target: float
    gross: float
    net: float
    commission: float
    slippage: float
    earlier_trigger: bool


def replay_trade(row: pd.Series, fm: FillModel) -> Replay:
    """What propedge's fill model says this trade should have been, from its evidence alone."""
    es = get_instrument("ES")
    entry = fm.entry_fill_price(es, float(row["ref"]), Side.LONG)
    entry = round(entry / es.tick_size) * es.tick_size      # levels on the grid, as in the algorithm
    stop = entry - alg.RECON_STOP_TICKS * es.tick_size
    target = entry + alg.RECON_TARGET_TICKS * es.tick_size

    # Would our rules have exited before LEAN's exit bar? Pre-exit extremes must not trigger.
    mx, mn = row.get("mx"), row.get("mn")
    earlier = (pd.notna(mn) and mn <= stop) or (pd.notna(mx) and mx > target)

    xo, xh, xl, xc = (float(row[k]) for k in ("xo", "xh", "xl", "xc"))
    gapped = False
    if xl <= stop:                                   # stop first on a tie (declared)
        reason, intended, gapped = ExitReason.STOP, stop, xo <= stop
    elif xh > target:                                # strict trade-through
        reason, intended = ExitReason.TARGET, target
    else:
        reason, intended = ExitReason.FLATTEN, xc
    f = fm.fill(es, side=Side.LONG, contracts=1, intended_entry=float(row["ref"]),
                intended_exit=intended, exit_reason=reason,
                next_available_price=xo if gapped else None, gapped=gapped)
    return Replay(reason.value, f.entry_price, f.exit_price, stop, target, f.gross_pnl,
                  f.net_pnl, f.commission, f.slippage_dollars, bool(earlier))


def _lean_reason(xr: str) -> str:
    return "flatten" if str(xr).startswith("flatten") else str(xr)


def compare(df: pd.DataFrame, fm: FillModel) -> pd.DataFrame:
    """One row per trade: LEAN's figures, propedge's replay, and every per-trade agreement flag."""
    es = get_instrument("ES")
    pv = es.point_value
    d = _num(df)
    rows = []
    for _, r in d.iterrows():
        rp = replay_trade(r, fm)
        lean_gross = (r["xf"] - r["ent"]) * pv
        lean_comm = (r.get("efee") or 0.0) + (r.get("fee") or 0.0)
        lean_net = lean_gross - lean_comm
        intended_exit = {"stop": r["st"], "target": r["tg"]}.get(_lean_reason(r["xr"]), r["xc"])
        lean_slip = ((intended_exit - r["ref"]) - (r["xf"] - r["ent"])) * pv
        ticks_off = (r["ent"] - r["ref"]) / es.tick_size
        rows.append({
            "n": int(r["n"]), "lean_reason": _lean_reason(r["xr"]), "our_reason": rp.reason,
            "lean_entry": r["ent"], "our_entry": rp.entry, "lean_exit": r["xf"], "our_exit": rp.exit,
            "lean_gross": lean_gross, "our_gross": rp.gross,
            "lean_net": lean_net, "our_net": rp.net,
            "lean_commission": lean_comm, "our_commission": rp.commission,
            "lean_slippage": lean_slip, "our_slippage": rp.slippage,
            "earlier_trigger": rp.earlier_trigger,
            "reason_ok": _lean_reason(r["xr"]) == rp.reason and not rp.earlier_trigger,
            "gross_ok": abs(lean_gross - rp.gross) < PRICE_EPS * pv,
            "net_ok": abs(lean_net - rp.net) < CENT,
            "commission_ok": abs(lean_comm - rp.commission) < CENT,
            "slippage_ok": abs(lean_slip - rp.slippage) < CENT,
            # stage C diagnostics
            "touch_filled_target": (_lean_reason(r["xr"]) == "target"
                                    and r["xh"] <= r["tg"] + PRICE_EPS),
            "gapped_stop_filled_at_stop": (_lean_reason(r["xr"]) == "stop"
                                           and r["xo"] < r["st"] - PRICE_EPS
                                           and abs(r["xf"] - r["st"]) < PRICE_EPS),
            "fraction_of_price_slippage": abs(ticks_off - round(ticks_off)) > 1e-6,
        })
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class StageVerdict:
    stage: str
    passed: bool
    trades: int
    detail: dict

    def summary(self) -> str:
        word = "PASS" if self.passed else "FAIL"
        return f"stage {self.stage}: {word} over {self.trades} trades -- {self.detail}"


def verdict(stage: str, cmp: pd.DataFrame) -> StageVerdict:
    n = len(cmp)
    if n == 0:
        return StageVerdict(stage, False, 0, {"reason": "no trades"})
    lean_mix = cmp["lean_reason"].value_counts().to_dict()
    our_mix = cmp["our_reason"].value_counts().to_dict()
    if stage == "A":
        bad = {k: int((~cmp[k]).sum()) for k in ("reason_ok", "gross_ok")}
        ok = not any(bad.values()) and lean_mix == our_mix
        return StageVerdict("A", ok, n, {"disagreements": bad, "exit_mix_lean": lean_mix,
                                         "exit_mix_ours": our_mix})
    if stage == "B":
        bad = {k: int((~cmp[k]).sum())
               for k in ("reason_ok", "net_ok", "commission_ok", "slippage_ok")}
        return StageVerdict("B", not any(bad.values()), n, {"disagreements": bad,
                                                            "exit_mix_lean": lean_mix})
    caught = {m: int(cmp[m].sum()) for m in C_FAILURE_MODES}
    ok = all(v > 0 for v in caught.values())
    status = {m: ("caught" if v else "NOT EXERCISED") for m, v in caught.items()}
    return StageVerdict("C", ok, n, {"caught": caught, "status": status,
                                     "any_disagreement": int((~(cmp["reason_ok"]
                                                                & cmp["gross_ok"])).sum())})


# ================================================================ version 2 (D-94)
#
# Version 1 above is kept as it ran on R002-R004. Version 2 differs in three ways:
#   * every evidence field must sit on the tick grid, or the run is UNUSABLE (not pass, not fail):
#     one price series, trade bars, is the whole point of the fix (D-93);
#   * entry and exit prices are compared on their own (`entry_ok`, `exit_ok`), so a fault on one
#     leg is seen without the other's noise;
#   * stage C is a planted-fault run: the algorithm labels each fill a fault decided (`flt`), and
#     the verdict asks that the comparison flag EVERY labelled fault with the check that owns it.

STAGE_NAMES_V2 = {"A": "A2_zero_cost_exact", "B": "B2_costs_on",
                  "C": "C2_planted_faults_caught"}
#: The fields that must be on the grid in every stage. `ent` is off-grid by design in stage C.
GRID_FIELDS = ("ref", "st", "tg", "mx", "mn", "xo", "xh", "xl", "xc")
#: Planted fault -> the per-trade check that must flag it.
C2_FAULTS = {"touch": "reason_ok", "gapstop": "exit_ok", "frac": "entry_ok"}


class UnusableEvidence(ValueError):
    """A v2 run whose recorded prices are not all trade prices on the tick grid."""


def off_grid(df: pd.DataFrame, fields=GRID_FIELDS) -> dict[str, int]:
    """Count, per field, recorded prices that are not a multiple of the ES tick."""
    tick = get_instrument("ES").tick_size
    d = _num(df)
    out = {}
    for f in fields:
        if f in d:
            v = d[f].dropna() / tick
            out[f] = int(((v - v.round()).abs() > 1e-6).sum())
    return {k: v for k, v in out.items() if v}


def compare_v2(df: pd.DataFrame, fm: FillModel) -> pd.DataFrame:
    """`compare`, after the grid check, plus per-leg price agreement and the fault labels."""
    bad = off_grid(df)
    if bad:
        raise UnusableEvidence(f"off-grid recorded prices {bad}: the run mixed price series.")
    cmp = compare(df, fm)
    cmp["entry_ok"] = (cmp["lean_entry"] - cmp["our_entry"]).abs() < PRICE_EPS
    cmp["exit_ok"] = (cmp["lean_exit"] - cmp["our_exit"]).abs() < PRICE_EPS
    flt = df["flt"].fillna("").astype(str).tolist() if "flt" in df else [""] * len(df)
    cmp["flt"] = flt
    return cmp


def verdict_v2(stage: str, cmp: pd.DataFrame) -> StageVerdict:
    """Stages A and B as in version 1. Stage C: each planted fault flagged wherever it fired."""
    if stage in ("A", "B") or len(cmp) == 0:
        return verdict(stage, cmp)
    detail, ok = {}, True
    for fault, check in C2_FAULTS.items():
        fired = cmp["flt"].eq(fault) if fault != "frac" else pd.Series(True, index=cmp.index)
        n_fired = int(fired.sum())
        n_flagged = int((fired & ~cmp[check]).sum())
        if n_fired == 0:
            status = "NOT EXERCISED"
            ok = ok and fault == "gapstop"          # declared in D-94 before the run
        elif n_flagged == n_fired:
            status = "caught"
        else:
            status = "MISSED"
            ok = False
        detail[fault] = {"fired": n_fired, "flagged": n_flagged, "by": check, "status": status}
    return StageVerdict("C", ok, len(cmp), {"faults": detail})
