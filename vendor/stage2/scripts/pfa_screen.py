"""EXPLORATORY (D-611, corrected by D-612): family PFA's cheap screen -- the P&F catapult's natural bracket at the operator's latency
(`config/pf_arm_a.yaml`). Kill lines are contract-fit lines (supply, resolution, risk consistency); every P&L reading
is beside them and decides nothing.

    python scripts/pfa_screen.py --check            # 2020-01-02 .. 2020-03-31: the pins and identities, every policy
                                                    #   and the walk run on the span; prints and writes no reading
    python scripts/pfa_screen.py --workers 1        # the screen (a clean checkout, D-474)

**The pieces, each reused** (the rules in `propedge.research.pfa_screen`'s docstring): the orders are D-607's
ALERTS (`pnf.scan`'s `alerts`, D-612 (2); `pfa_screen.alert_rows`) on NQ's development bars read once through `scripts/pf_fit.py`'s `load` (the window
guard, purpose development, never past 2026-07-16), at boxes 2.5, 5, 6.25, 7.5 and 10 points; a day's arrays are
`atlas_local.day_arrays`' (P-16's, `atlas_a3.bar_arrays`); P-16's entry slip is `config/atlas_a3.yaml`'s `slip_ticks`
(`atlas_a3.config`), its fee at each trade's stop `atlas_a3.fee_by_stop` (FV3-C's config through `atlas_a3.fv3_config`),
its report days A1's day records (`a3_resolution_map.load_a1`, read only and refused when stale); P-16's fresh Combine
and fresh funded risks are its no-closure table's (`a3_brk30_cb20.noclose_plan`, hash-pinned there, read by
`a3_brk30.fresh_decisions`), Topstep's full allowance `model_card.full_allowance`, K3 by stop width
`model_card.by_stop_shares` (D-312 (1), D-612 (1)); the bound's bootstrap `a4_coin_atlas.stationary_counts`.

**Identities first, refusing:** `config/pf_arm_a.yaml` by sha256 on its LF text and its declared constants; at boxes
2.5, 5, 7.5 and 10 the engine's setups equal `results/pf_fit_setups.csv`'s rows (the file pinned by sha256, its
manifest verified; in `--check` the rows dated in the span); the engine's alerts are additive (the triggered
alerts are its setups field for field, every other fate its own count); A1's day list is the development day list; the walk equals
`fv3_rung_walk.walk` record for record (entries at a bar's open on sampled days, three stops and three R) wherever FV3's
breakeven move does not act; P-16's fresh risks under the full allowance buy, at its 150-tick stop, the dollars its card
declares by stop (`docs/candidates/cards/RC150.md`, D-312 (1)); no filled trade is a report day's before 07:35 CT; on the
alerts the engine triggered, the bars' missed flag equals D-607's `missed_L5`.

Writes `results/pfa_screen.csv` (sections identity, kill, k3_reference, beside, year, window, verdict) and
`results/pfa_trades.csv` (one row per filled trade, every cell), with manifests, EXPLORATORY; seed 20261811 (the
bound's bootstrap and the coin). D-611's 20 cells (the catapult at every box under rest, skip and chase; the plain
triple top / bottom at every box under rest) are recorded in `results/variants.jsonl` under `D-611:pfa_screen` by the
full run only.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
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
import yaml  # noqa: E402

from propedge.research import pf_fit as PF  # noqa: E402
from propedge.research import pfa_screen as P  # noqa: E402
from propedge.research import pnf  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/pfa_screen.py"
DECISION = P.DECISION
CHECK_SPAN = ("2020-01-02", "2020-03-31")  # pf_fit's --check span (one roll)
P16_CARD = "docs/candidates/cards/RC150.md"
P16_STOP_TICKS = 150                       # P-16's 37.5-point stop (D-544)
WALK_SAMPLE_DAYS = 40                      # the walk identity: every k-th day of the span, up to this many
WALK_SLOT_STEP = 37                        # an entry at the first bar after every 37th slot, both sides
WALK_STOPS = (40, 150, 300)                # ticks
WALK_RR = (0.5, 1.0, 2.0)
WALK_MIN_COMPARED = 200
READING = ("EXPLORATORY (D-611): family PFA's cheap screen -- the P&F catapult's natural bracket at L = 5; the kill "
           "lines are contract fit (supply, resolution, risk consistency); every P&L reading is beside and decides "
           "nothing")


# ------------------------------------------------------------------------------------------------ pins and inputs


def config_problems(text: bytes) -> list[str]:
    """`config/pf_arm_a.yaml` pinned by sha256 on its LF text, then its constants and phrases checked against this
    script's."""
    out = []
    if P.lf_sha256(text) != P.CONFIG_SHA256_LF:
        return [f"{P.CONFIG} is not the file D-611 declared (LF sha256 {P.lf_sha256(text)[:12]}, want "
                f"{P.CONFIG_SHA256_LF[:12]})"]
    s = yaml.safe_load(text.decode("utf-8"))["screen"]
    want = {"id": P.FAMILY, "decision": DECISION, "latency_minutes": P.LATENCY_MIN, "cells": len(P.CELLS)}
    for k, v in want.items():
        if s.get(k) != v:
            out.append(f"the config's {k} is {s.get(k)!r}, not {v!r}")
    if tuple(s.get("policies") or ()) != P.POLICIES:
        out.append(f"the config's policies are {list(s.get('policies') or ())}, not {list(P.POLICIES)}")
    phrases = [("setups", "boxes 2.5, 5, 6.25, 7.5, 10 points"), ("setups", "r7_low"), ("setups", "07:35 CT"),
               ("bracket", "15:10 CT reached first = unresolved"), ("bracket", "no time exit"),
               ("walk", "counts as the stop"), ("data", "2026-07-16")]
    for key, ph in phrases:
        if ph not in " ".join(str(s.get(key, "")).split()):
            out.append(f"the config's {key} does not say {ph!r}")
    beside = " ".join(" ".join(str(x).split()) for x in s.get("beside") or [])
    for ph in ("block 21", "2,000 reps", f"seed {P.SEED}", "D-271"):
        if ph not in beside:
            out.append(f"the config's beside does not say {ph!r}")
    k = s.get("kill_lines") or {}
    for key, ph in (("K1_supply", "below 1.0"), ("K2_resolution", "more than 5 %"), ("K2_resolution", "63 sessions"),
                    ("K3_risk", "risk_consistency"), ("K3_risk", "full micro allowance")):
        if ph not in " ".join(str(k.get(key, "")).split()):
            out.append(f"the config's {key} does not say {ph!r}")
    return out


def setups_file(rd: Path) -> tuple[pd.DataFrame | None, list[str]]:
    """`results/pf_fit_setups.csv`, its manifest verified and its bytes pinned (raw and LF), read to the last digit."""
    from propedge.reporting.results import verify_result

    path = Path(rd) / P.SETUPS_FILE
    if not path.is_file():
        return None, [f"{P.SETUPS_FILE} is missing"]
    ok, msg = verify_result(path)
    raw = path.read_bytes()
    import hashlib

    bad = [] if ok else [f"{P.SETUPS_FILE}: {msg}"]
    if hashlib.sha256(raw).hexdigest() != P.SETUPS_SHA256 and P.lf_sha256(raw) != P.SETUPS_SHA256_LF:
        bad.append(f"{P.SETUPS_FILE} is not D-609's file (sha256 {hashlib.sha256(raw).hexdigest()[:12]})")
    if bad:
        return None, bad
    return pd.read_csv(path, float_precision="round_trip", low_memory=False), []


def _cell(x: Any) -> str:
    if x is None or x is pd.NA or (isinstance(x, float) and np.isnan(x)):
        return ""
    if isinstance(x, (bool, np.bool_)):
        return str(bool(x))
    return str(x)


def _same(a: pd.Series, b: pd.Series) -> bool:
    num = (pd.api.types.is_numeric_dtype(a) and not pd.api.types.is_bool_dtype(a)
           and pd.api.types.is_numeric_dtype(b) and not pd.api.types.is_bool_dtype(b))
    if num:
        return bool(np.allclose(a.to_numpy(float), b.to_numpy(float), rtol=0.0, atol=1e-9, equal_nan=True))
    return bool((a.map(_cell).to_numpy() == b.map(_cell).to_numpy()).all())


def setups_identity(file_rows: pd.DataFrame, rows: dict[float, pd.DataFrame], last_day: str) -> list[str]:
    """At each of the file's boxes, the engine's setups (dated at or before `last_day`) equal the file's rows, in
    order, column by column."""
    out = []
    cols = [c for c in file_rows.columns if c != "reading"]
    for box in P.FIT_BOXES:
        f = file_rows[np.isclose(file_rows["box_points"].astype(float), box)
                      & (file_rows["date"].astype(str) <= str(last_day))].reset_index(drop=True)
        r = rows[box]
        r = r[r["date"].astype(str) <= str(last_day)].reset_index(drop=True)
        if len(f) != len(r):
            out.append(f"box {box:g}: {len(r)} setups, the file {len(f)}")
            continue
        diff = [c for c in cols if c not in r.columns or not _same(r[c], f[c])]
        if diff:
            out.append(f"box {box:g}: the setups differ from the file in {diff}")
    return out


def p16_inputs(rd: Path) -> dict[str, Any]:
    """P-16's pieces: A3's config (the slip, the tick), FV3-C's config (the fee), the no-closure table's fresh risks,
    A1's day kinds, the full allowance and P-16's card's by-stop declaration."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import a3_resolution_map as m0
    import atlas_a3 as A

    from propedge.backtest.prereg import _parse_fields
    from propedge.research.model_card import full_allowance, risk_by_stop

    cfg = A.config("A3")
    fcfg = A.fv3_config(cfg)
    fresh = B.fresh_decisions(C.noclose_plan(Path(rd)))
    _, _, days, _ = m0.load_a1()
    by_stop, problem = risk_by_stop(_parse_fields((ROOT / P16_CARD).read_text(encoding="utf-8")))
    return {"A": A, "cfg": cfg, "fcfg": fcfg, "fresh": fresh,
            "risks": {"combine": float(fresh["combine"]["risk"]), "funded": float(fresh["funded"]["risk"])},
            "allowance": full_allowance(), "days": days, "card_by_stop": by_stop, "card_problem": problem,
            "band": P._band()}


def p16_problems(I: dict[str, Any]) -> list[str]:
    out = []
    cfg = I["cfg"]
    if int(cfg["slip_ticks"]) != P.ENTRY_SLIP_TICKS:
        out.append(f"P-16's entry slip is {cfg['slip_ticks']} ticks, not {P.ENTRY_SLIP_TICKS}")
    if float(cfg["contract"]["tick"]) != P.TICK or str(cfg["market"]) != P.MARKET:
        out.append("A3's contract is not NQ at 0.25 points a tick")
    if float(I["A"].TICK_VALUE) != P.TICK_VALUE:
        out.append(f"atlas_a3's tick value is {I['A'].TICK_VALUE}, not {P.TICK_VALUE}")
    from propedge.research import fv3_rung_walk as RW

    if dict(RW.EXIT_TICKS) != {0: 1, 1: 0, 2: 2, 3: 1} or RW.FLATTEN_SLIP_TICKS != P.FLATTEN_SLIP_TICKS:
        out.append("the rung walk's exit ticks are not the ones this screen books")
    fr = I["fcfg"]["state_policy"]["fresh"]
    if (float(fr["combine_risk"]), float(fr["funded_risk"])) != (I["risks"]["combine"], I["risks"]["funded"]):
        out.append(f"the no-closure table's fresh risks {I['risks']} are not FV3-C's declared fresh legs {fr}")
    if I["card_problem"] or not I["card_by_stop"]:
        out.append(f"P-16's card declares no risk by stop ({I['card_problem']})")
    else:
        for state in ("combine", "funded"):
            want = I["card_by_stop"][state].get(float(P16_STOP_TICKS))
            got = P.realised_dollars(P16_STOP_TICKS, I["risks"][state], I["allowance"][state])
            if want is None or abs(float(want) - got) > 1e-9:
                out.append(f"P-16's fresh {state} ${I['risks'][state]:,.0f} under the full allowance "
                           f"({I['allowance'][state]} micros) buys ${got:,.0f} at {P16_STOP_TICKS} ticks; its card "
                           f"declares {want}")
    return out


# ------------------------------------------------------------------------------------------------ the trades


def day_arrays_of(bars: pd.DataFrame):
    """{trading day: (o, h, l, c)} on demand -- `atlas_a3.bar_arrays`' arrays from the bars already read."""
    from propedge.research import atlas_local

    by_day = {str(d): g for d, g in bars.groupby("day", sort=False)}
    cache: dict[str, tuple] = {}

    def arrays(day: str) -> tuple:
        day = str(day)
        if day not in cache:
            cache[day] = tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                               for v in atlas_local.day_arrays(by_day.get(day, bars.iloc[0:0])))
        return cache[day]
    return arrays


def universe(alerts: dict[float, pd.DataFrame]) -> pd.DataFrame:
    """D-612 (2)'s orders: every fixed-reading catapult alert and every plain alert whose alert bar ends in Topstep's
    hours, whatever its fate in the engine, every box, in the coin's fixed order (box, group, alert bar, kind, column)."""
    parts = []
    for box in P.BOXES:
        r = alerts[box]
        cat = r["kind"].isin(pnf.CATAPULTS) & r[P.FIXED_CHOICE].astype(bool)
        pla = r["kind"].isin(pnf.PLAINS)
        u = r[(cat | pla) & r["in_hours"].astype(bool)].copy()
        u["group"] = np.where(u["kind"].isin(pnf.CATAPULTS), P.CATAPULT, P.PLAIN)
        parts.append(u)
    u = pd.concat(parts, ignore_index=True)
    u["_g"] = (u["group"] == P.PLAIN).astype(int)
    u = u.sort_values(["box_points", "_g", "alert_bar", "kind", "column_k"], kind="stable").drop(columns="_g")
    return u.reset_index(drop=True)


def attempts(u: pd.DataFrame, arrays, day_kind: dict[str, str], coins: np.ndarray) -> tuple[pd.DataFrame, list]:
    """Every (order, policy) of D-611's cells placed on its alert's trading day; filled ones walked on the alert's
    side and on the coin's: one row each with the outcome and the bars' missed flag."""
    out = []
    for i, s in enumerate(u.itertuples(index=False)):
        alert = {"side": int(s.side), "entry_T": float(s.entry_T), "stop": float(s.stop), "target": float(s.target),
                 "alert_end_slot": int(s.alert_end_slot)}
        arr = arrays(str(s.date))
        dk = day_kind.get(str(s.date))
        if dk is None:
            raise SystemExit(f"REFUSED ({DECISION}): {s.date} is not in A1's day records")
        policies = P.POLICIES if s.group == P.CATAPULT else (P.CARD_POLICY,)
        for pol in policies:
            r = P.place(pol, arr, alert)
            rec = {"u": i, "policy": pol, "outcome": r["outcome"], "missed": bool(r["missed"]), "day_kind": dk}
            if r["outcome"] == P.FILLED:
                if P.news_cut(dk, r["fill_slot"]):
                    rec["outcome"] = "news_cut"
                else:
                    o, h, l, c = arr
                    w = P.walk_bracket(o, h, l, c, r["fill_slot"], r["walk_entry"], alert["side"], r["S"], r["Tt"])
                    cw = P.walk_bracket(o, h, l, c, r["fill_slot"], r["walk_entry"], int(coins[i]), r["S"], r["Tt"])
                    rec.update({k: r[k] for k in ("fill_slot", "walk_entry", "how", "S", "Tt")})
                    rec.update({"kind_w": w["kind"], "exit_slot": w["exit"], "gross": w["gross"], "mae": w["mae"],
                                "coin_side": int(coins[i]), "coin_kind": cw["kind"], "coin_gross": cw["gross"]})
            out.append(rec)
    return pd.DataFrame(out), []


def trade_frame(u: pd.DataFrame, a: pd.DataFrame, fees: dict[int, float], I: dict[str, Any]) -> pd.DataFrame:
    """One row per filled trade: the alert, the fill, the walk, the costs, each state's realised dollars and the coin
    twin."""
    f = a[a["outcome"] == P.FILLED].reset_index(drop=True)
    s = u.iloc[f["u"].to_numpy()].reset_index(drop=True)
    side = s["side"].astype(int).to_numpy()
    S = f["S"].astype(int).to_numpy()
    fee = np.array([fees[int(x)] for x in S], dtype=float)
    kind = f["kind_w"].astype(int).to_numpy()
    ckind = f["coin_kind"].astype(int).to_numpy()
    fill_price = f["walk_entry"].to_numpy(float) + side * P.ENTRY_SLIP_TICKS * P.TICK
    rr = side * (fill_price - s["stop"].to_numpy(float))
    t = pd.DataFrame({
        "box_points": s["box_points"].astype(float), "group": s["group"], "kind": s["kind"], "policy": f["policy"],
        "side": side, "date": s["date"].astype(str), "year": s["date"].astype(str).str[:4].astype(int),
        "day_kind": f["day_kind"], "fate": s["fate"], "chart": s["chart"], "column_k": s["column_k"],
        "alert_end_ct": s["alert_end_ct"], "alert_end_slot": s["alert_end_slot"].astype(int),
        "alert_window": s["window"], "missed": f["missed"].astype(bool), "how": f["how"],
        "fill_slot": f["fill_slot"].astype(int), "fill_end_ct": f["fill_slot"].astype(int).map(rc.ct),
        "window": f["fill_slot"].astype(int).map(P.window_of_slot),
        "entry_T": s["entry_T"].astype(float), "stop": s["stop"].astype(float), "target": s["target"].astype(float),
        "D_points": s["D_points"].astype(float), "walk_entry": f["walk_entry"].astype(float), "fill_price": fill_price,
        "S_ticks": S, "target_ticks": f["Tt"].astype(int), "realised_risk_points": rr,
        "realised_risk_over_D": rr / s["D_points"].to_numpy(float),
        "reward_to_risk": f["Tt"].to_numpy(float) / S,
        "realised_combine_dollars": P.realised_dollars(S, I["risks"]["combine"], I["allowance"]["combine"]),
        "realised_funded_dollars": P.realised_dollars(S, I["risks"]["funded"], I["allowance"]["funded"]),
        "exit_kind": [P.KIND_NAME[int(k)] for k in kind],
        "exit_slot": f["exit_slot"].astype(int), "exit_end_ct": f["exit_slot"].astype(int).map(rc.ct),
        "minutes_held": f["exit_slot"].astype(int) - f["fill_slot"].astype(int),
        "gross_ticks": f["gross"].astype(int), "gross_R": f["gross"].to_numpy(float) / S,
        "fee_micro_eq": fee, "cost_R": P.cost_r(kind, S, fee),
        "net_R": P.net_r(f["gross"].to_numpy(float), kind, S, fee), "mae_R": f["mae"].to_numpy(float) / S,
        "coin_side": f["coin_side"].astype(int), "coin_exit_kind": [P.KIND_NAME[int(k)] for k in ckind],
        "coin_gross_R": f["coin_gross"].to_numpy(float) / S,
        "coin_net_R": P.net_r(f["coin_gross"].to_numpy(float), ckind, S, fee)})
    return t


def missed_identity(u: pd.DataFrame, a: pd.DataFrame, rows: dict[float, pd.DataFrame]) -> tuple[list[str], int]:
    """On the alerts the engine triggered on the alert's own trading day, the bars' missed flag equals D-607's
    `missed_L5` (pf_fit.setup_rows). (problems, compared)."""
    flag = a.drop_duplicates("u").set_index("u")["missed"].astype(bool)
    key = ["box_points", "kind", "chart", "column_k", "alert_bar"]
    trig = u.assign(missed=flag.reindex(range(len(u))).to_numpy(), u=np.arange(len(u)))
    trig = trig[trig["fate"] == "triggered"]
    srow = pd.concat([rows[b] for b in P.BOXES], ignore_index=True)
    srow = srow[srow["date"].astype(str) == srow["alert_date"].astype(str)]
    m = trig.merge(srow[key + ["missed_L5"]], on=key, how="inner")
    # D-615: the day arrays end at the bar ending 15:10 CT (atlas_local.FLAT_MIN), so an alert whose missed window
    # (alert .. alert + 5) runs past it cannot be compared; such an order has no working bar before the walk's last
    # entry bar (15:08 CT), so it never fills under any policy -- checked here, refusing otherwise.
    from propedge.research.atlas_local import FLAT_MIN
    late = (m["alert_end_slot"].astype(int) + int(P.LATENCY_MIN)) > int(FLAT_MIN)
    late_u = set(m.loc[late, "u"].astype(int)) if "u" in m.columns else set()
    out = []
    if late.any():
        if "u" not in m.columns:
            out.append("the late alerts cannot be traced to their orders (no `u` column)")
        else:
            filled_late = a[a["u"].astype(int).isin(late_u) & (a["outcome"] == P.FILLED)]
            if len(filled_late):
                out.append(f"{len(filled_late)} fills on orders whose missed window runs past 15:10 CT")
    mm = m[~late]
    bad = mm[mm["missed"].astype(bool) != mm["missed_L5"].astype(bool)]
    if not bad.empty:
        out.append(f"{len(bad)} triggered alerts whose bars' missed flag is not D-607's missed_L5")
    if not len(m) and len(trig):
        out.append("no triggered alert matched a setup row")
    return out, int(len(mm))


def walk_identity(bars: pd.DataFrame, sessions: list[str]) -> tuple[list[str], int, int]:
    """`walk_bracket` against `fv3_rung_walk.walk` on sampled days (entries at a bar's open): every record equal where
    the breakeven move does not act. (problems, compared, skipped)."""
    from propedge.outcomes.orb_core import NONE
    from propedge.research import fv3_rung_walk as RW

    arrays = day_arrays_of(bars)
    days = sorted({str(d) for d in bars["day"]})
    step = max(1, len(days) // WALK_SAMPLE_DAYS)
    bl = RW.brackets(WALK_STOPS, WALK_RR)
    bad, n_cmp, n_skip = [], 0, 0
    for day in days[::step][:WALK_SAMPLE_DAYS]:
        o, h, l, c = arrays(day)
        end = P.day_end(o)
        if end is None:
            continue
        ent = []
        for t in range(1, end, WALK_SLOT_STEP):
            idx = np.flatnonzero(~np.isnan(o[t:end]))
            if idx.size:
                ent += [(t + int(idx[0]), 1), (t + int(idx[0]), -1)]
        if not ent:
            continue
        res = RW.walk(o, h, l, c, [d for _, d in ent], [j for j, _ in ent], P.TICK, bl)
        for w, (je, d) in enumerate(ent):
            be_ok = res["be_open"][w] != NONE and res["be_favour"][w] > 0
            for b, (S, _R, Tt) in enumerate(bl):
                mine = P.walk_bracket(o, h, l, c, je, o[je], d, S, Tt)
                off = NONE if mine["kind"] == P.FLATTEN else mine["exit"]
                if be_ok and (off == NONE or res["be_open"][w] < off):
                    n_skip += 1
                    continue
                n_cmp += 1
                theirs = (int(res["kind"][w, b]), int(res["exit"][w, b]), int(res["gross"][w, b]),
                          int(res["mae"][w, b]))
                ours = (mine["kind"], mine["exit"], mine["gross"], mine["mae"])
                if theirs != ours and len(bad) < 5:
                    bad.append(f"{day} bar {je} side {d} stop {S} target {Tt}: rung walk {theirs}, this walk {ours}")
    if n_cmp < WALK_MIN_COMPARED:
        bad.append(f"only {n_cmp} walks compared (at least {WALK_MIN_COMPARED})")
    return bad, n_cmp, n_skip


# ------------------------------------------------------------------------------------------------ the readings


def readings(t: pd.DataFrame, a: pd.DataFrame, sessions: list[str], counts: np.ndarray | None,
             day_index: dict[str, int], I: dict[str, Any]) -> dict[str, Any]:
    """The readings of one set of fills `t` (and its attempts `a`): supply, outcomes, e and its bound, the coin."""
    n = len(t)
    out: dict[str, Any] = {"setups": int(len(a)), "filled": n, "sessions": len(sessions),
                           "filled_per_session": P.k1_supply(t["date"], sessions)}
    for reason in P.REASONS:
        out[f"n_{reason}"] = int((a["outcome"] == reason).sum())
    unres = (t["exit_kind"] == "flatten").to_numpy()
    k2 = P.k2_resolution(t["date"], unres, sessions)
    out.update({"unresolved_share": k2["overall"], "unresolved_worst_year": k2["worst"],
                "unresolved_worst_year_is": k2["worst_year"]})
    k3 = P.k3_by_stop(t["S_ticks"], I["risks"], I["allowance"], I["band"])
    k3s = P.k3_single(t["S_ticks"], I["risks"], I["allowance"])
    out.update({"k3_combine_share": k3["combine"]["share"], "k3_funded_share": k3["funded"]["share"],
                "k3_outside_band_share": k3["combine"]["outside"],
                "k3_single_combine_share": k3s["combine"], "k3_single_funded_share": k3s["funded"]})
    for st in ("combine", "funded"):
        col = f"realised_{st}_dollars"
        qs = np.percentile(t[col].to_numpy(float), P.QUANTILES) if n else [np.nan] * len(P.QUANTILES)
        out.update({f"{col}_q{q:02d}": float(v) for q, v in zip(P.QUANTILES, qs)})
    out.update({"filled_missed_share": float(t["missed"].mean()) if n else np.nan,
                "filled_untriggered_alerts": int((t["fate"] != "triggered").sum())})
    if counts is not None and n:
        idx = t["date"].map(day_index).to_numpy()
        e, lb = P.mean_and_bound(idx, t["net_R"], counts)
        ce, clb = P.mean_and_bound(idx, t["coin_net_R"], counts)
    else:
        e = float(t["net_R"].mean()) if n else np.nan
        ce = float(t["coin_net_R"].mean()) if n else np.nan
        lb = clb = np.nan
    def m(c):
        return float(t[c].mean()) if n else np.nan

    def md(c):
        return float(t[c].median()) if n else np.nan
    out.update({"e": e, "e_lb95": lb, "gross_R_mean": m("gross_R"), "cost_R_mean": m("cost_R"),
                "target_share": float((t["exit_kind"] == "target").mean()) if n else np.nan,
                "stop_share": float((t["exit_kind"] == "stop").mean()) if n else np.nan,
                "realised_risk_over_D_mean": m("realised_risk_over_D"),
                "realised_risk_over_D_median": md("realised_risk_over_D"),
                "realised_risk_points_median": md("realised_risk_points"), "reward_to_risk_median": md("reward_to_risk"),
                "reward_to_risk_mean": m("reward_to_risk"), "minutes_held_median": md("minutes_held"),
                "minutes_held_mean": m("minutes_held"), "long_share": float((t["side"] > 0).mean()) if n else np.nan,
                "filled_fomc_days": int((t["day_kind"] == "o").sum()),
                "filled_early_close_days": int((t["day_kind"] == "e").sum()),
                "coin_e": ce, "coin_e_lb95": clb, "coin_gross_R_mean": m("coin_gross_R"),
                "coin_target_share": float((t["coin_exit_kind"] == "target").mean()) if n else np.nan,
                "e_minus_coin_e": (e - ce) if n else np.nan,
                "old_gate_met": bool(n and np.isfinite(lb) and e >= 0.10 and lb >= 0.05)})
    return out


def kill_rows(t: pd.DataFrame, sessions: list[str], I: dict[str, Any]) -> list[dict]:
    """K1-K3 per box on the card's policy, the catapults."""
    rows = []
    for box in P.BOXES:
        g = t[np.isclose(t["box_points"], box) & (t["group"] == P.CATAPULT) & (t["policy"] == P.CARD_POLICY)]
        k1 = P.k1_supply(g["date"], sessions)
        k2 = P.k2_resolution(g["date"], (g["exit_kind"] == "flatten").to_numpy(), sessions)
        k3 = P.k3_by_stop(g["S_ticks"], I["risks"], I["allowance"], I["band"])
        k3s = P.k3_single(g["S_ticks"], I["risks"], I["allowance"])
        k1_ok = bool(np.isfinite(k1) and k1 >= P.K1_MIN)
        k2_ok = not k2["fails"]
        k3_ok = P.k3_passes({st: k3[st]["share"] for st in k3})
        rows.append({"section": "kill", "box_points": box, "group": P.CATAPULT, "policy": P.CARD_POLICY,
                     "filled": int(len(g)), "sessions": len(sessions), "K1_filled_per_session": k1,
                     "K1_line": P.K1_MIN, "K1_passes": k1_ok, "K2_unresolved_share": k2["overall"],
                     "K2_unresolved_worst_year": k2["worst"], "K2_unresolved_worst_year_is": k2["worst_year"],
                     "K2_judged_years": ";".join(k2["judged_years"]), "K2_line": P.K2_MAX, "K2_passes": k2_ok,
                     "K3_reading": "D-312 (1) by stop width (D-612 (1))",
                     "K3_combine_share": k3["combine"]["share"], "K3_funded_share": k3["funded"]["share"],
                     "K3_combine_unsizeable": k3["combine"]["unsizeable"],
                     "K3_funded_unsizeable": k3["funded"]["unsizeable"],
                     "K3_single_combine_share_beside": k3s["combine"], "K3_single_funded_share_beside": k3s["funded"],
                     "K3_combine_risk": I["risks"]["combine"], "K3_funded_risk": I["risks"]["funded"],
                     "K3_combine_cap_micros": I["allowance"]["combine"], "K3_funded_cap_micros": I["allowance"]["funded"],
                     "K3_passes": k3_ok, "survives": bool(k1_ok and k2_ok and k3_ok)})
    return rows


def k3_reference(I: dict[str, Any]) -> dict:
    """K3 read at P-16's own 150-tick stop: by stop width (the line) and the single figure (beside)."""
    sh = P.k3_by_stop([P16_STOP_TICKS], I["risks"], I["allowance"], I["band"])
    single = P.k3_single([P16_STOP_TICKS], I["risks"], I["allowance"])
    return {"section": "k3_reference", "S_ticks": P16_STOP_TICKS, "K3_reading": "D-312 (1) by stop width (D-612 (1))",
            "K3_combine_share": sh["combine"]["share"], "K3_funded_share": sh["funded"]["share"],
            "K3_passes": P.k3_passes({st: sh[st]["share"] for st in sh}),
            "K3_single_combine_share_beside": single["combine"], "K3_single_funded_share_beside": single["funded"],
            "realised_combine": P.realised_dollars(P16_STOP_TICKS, I["risks"]["combine"], I["allowance"]["combine"]),
            "realised_funded": P.realised_dollars(P16_STOP_TICKS, I["risks"]["funded"], I["allowance"]["funded"]),
            "K3_combine_risk": I["risks"]["combine"], "K3_funded_risk": I["risks"]["funded"],
            "note": "P-16's own stop: its card declares exactly these dollars by stop (D-312 (1)), the reading K3 uses"}


def beside_rows(t: pd.DataFrame, a: pd.DataFrame, u: pd.DataFrame, sessions: list[str], counts: np.ndarray,
                I: dict[str, Any]) -> list[dict]:
    """Per cell (and per side within it): the readings over all sessions (with the bound), per year and per window."""
    day_index = {d: i for i, d in enumerate(sessions)}
    years = sorted({d[:4] for d in sessions})
    by_year = {y: [d for d in sessions if d[:4] == y] for y in years}
    ua = u.iloc[a["u"].to_numpy()].reset_index(drop=True)
    a = a.reset_index(drop=True).assign(box_points=ua["box_points"].astype(float).to_numpy(),
                                        group=ua["group"].to_numpy(), kind=ua["kind"].to_numpy(),
                                        date=ua["date"].astype(str).to_numpy())
    rows = []
    for box, group, pol in P.CELLS:
        tc = t[np.isclose(t["box_points"], box) & (t["group"] == group) & (t["policy"] == pol)]
        ac = a[np.isclose(a["box_points"], box) & (a["group"] == group) & (a["policy"] == pol)]
        for kind in (group,) + tuple(P.GROUPS[group]):
            tk = tc if kind == group else tc[tc["kind"] == kind]
            ak = ac if kind == group else ac[ac["kind"] == kind]
            head = {"box_points": box, "group": group, "kind": kind, "policy": pol, "card_policy": pol == P.CARD_POLICY}
            rows.append({"section": "beside", **head, "scope": "all", **readings(tk, ak, sessions, counts, day_index, I)})
            for y in years:
                ty = tk[tk["date"].str[:4] == y]
                ay = ak[ak["date"].str[:4] == y]
                rows.append({"section": "year", **head, "scope": y,
                             **readings(ty, ay, by_year[y], None, day_index, I)})
            for w in P.WINDOWS:
                tw = tk if w == "all" else tk[tk["window"] == w]
                rows.append({"section": "window", **head, "scope": w,
                             **readings(tw, ak.iloc[0:0], sessions, None, day_index, I)})
    return rows


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help=f"{CHECK_SPAN[0]} .. {CHECK_SPAN[1]}: the pins, identities and "
                                                         "every policy on the span; no reading printed or written")
    ap.add_argument("--workers", type=int, default=1, help="accepted; the screen is one pass (1 only)")
    a = ap.parse_args(argv)
    if a.workers != 1:
        print(f"REFUSED ({DECISION}): the screen is one deterministic pass; --workers 1 only.")
        return 2

    import pf_fit as pf_script

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.bars import manifest
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    idents: list[dict] = []
    bad: list[str] = []

    def ident(check: str, problems: list[str]) -> None:
        idents.append({"section": "identity", "holds": not problems, "check": check, "problems": "; ".join(problems)})
        print(("HOLDS: " if not problems else "FAILS: ") + check + ("" if not problems else " -- " + "; ".join(problems)),
              flush=True)
        bad.extend(problems)

    def refuse() -> int:
        print(f"REFUSED ({DECISION}): an identity fails -- " + "; ".join(bad))
        return 3

    cfg_text = (ROOT / P.CONFIG).read_bytes()
    ident(f"{P.CONFIG} is D-611's (sha256 {P.CONFIG_SHA256_LF[:12]} on its LF text) and declares this screen's "
          "constants (PFA, D-611, L = 5, rest / skip / chase, 20 cells, the boxes, the cut, the walk, the kill lines, "
          "the bound's bootstrap and the coin)", config_problems(cfg_text))
    file_rows, prob = setups_file(rd)
    ident(f"results/{P.SETUPS_FILE} is D-609's file (sha256 {P.SETUPS_SHA256[:12]}, its manifest verified)", prob)
    if bad:
        return refuse()
    I = p16_inputs(rd)
    ident(f"P-16's pieces: a {P.ENTRY_SLIP_TICKS}-tick entry slip (config/atlas_a3.yaml), NQ at {P.TICK} points and "
          f"${P.TICK_VALUE} a micro tick, the rung walk's exit ticks; the no-closure table's fresh risks (Combine "
          f"${I['risks']['combine']:,.0f}, funded ${I['risks']['funded']:,.0f}) equal FV3-C's declared fresh legs; under "
          f"the full allowance ({I['allowance']['combine']} / {I['allowance']['funded']} micros) they buy at "
          f"{P16_STOP_TICKS} ticks the dollars P-16's card declares by stop ({P16_CARD})", p16_problems(I))

    start, end = CHECK_SPAN if a.check else (P.DEV_START, P.DEV_END)
    sessions = pf_script.sessions_of(start, end)
    bars = pf_script.load(start, end)
    if len(bars) and str(bars["day"].max()) > P.DEV_END:
        print(f"REFUSED ({DECISION}): the read holds a day after {P.DEV_END}.")
        return 3
    print(f"read {len(bars)} bars, {bars['day'].nunique()} trading days {bars['day'].min()} .. {bars['day'].max()} "
          f"(purpose development); {len(sessions)} sessions in the day list", flush=True)
    a1 = I["days"].copy()
    a1["date"] = a1["date"].astype(str)
    a1_days = sorted(d for d in a1["date"] if start <= d <= end)
    ident(f"A1's day records over the span are the development day list ({len(sessions)} sessions)",
          [] if a1_days == sorted(sessions) else [f"A1 holds {len(a1_days)} days, the day list {len(sessions)}"])
    day_kind = dict(zip(a1["date"], a1["day_kind"].astype(str)))

    t0 = time.time()
    con = bars["contract"].astype(str).to_numpy()
    rows: dict[float, pd.DataFrame] = {}
    alerts: dict[float, pd.DataFrame] = {}
    al_bad: list[str] = []
    fates: dict[str, int] = {}
    for box in P.BOXES:
        res = pnf.scan(bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy(), con, box=box)
        rows[box] = PF.setup_rows(bars, box, result=res)
        alerts[box] = P.alert_rows(bars, box, res)
        al_bad += [f"box {box:g}: {x}" for x in P.alert_problems(res)]
        for f, n in alerts[box]["fate"].value_counts().items():
            fates[f] = fates.get(f, 0) + int(n)
    print(f"the scan at {list(P.BOXES)} points: {time.time() - t0:.0f} s", flush=True)
    ident(f"at boxes {list(P.FIT_BOXES)} the engine's setups{' dated in the span' if a.check else ''} equal "
          f"results/{P.SETUPS_FILE}'s rows, column by column", setups_identity(file_rows, rows, end))
    ident("D-607 (4) and the bracket's construction hold on the 6.25-point box's setups (pf_fit.identity_problems)",
          PF.identity_problems(rows[6.25]))
    ident(f"the engine's alerts (D-612, additive) at every box: the triggered alerts are its setups field for field, "
          f"each other fate is the engine's own count, D >= 5b on every alert ({sum(fates.values())} alerts: "
          + ", ".join(f"{k} {fates.get(k, 0)}" for k in P.FATES) + ")", al_bad)
    t0 = time.time()
    wb, n_cmp, n_skip = walk_identity(bars, sessions)
    ident(f"the walk equals fv3_rung_walk.walk record for record on {n_cmp} walks (entries at a bar's open on sampled "
          f"days, stops {list(WALK_STOPS)} ticks, R {list(WALK_RR)}; {n_skip} walks where FV3's breakeven move acts "
          "left out)", wb)
    print(f"the walk identity: {time.time() - t0:.0f} s", flush=True)
    if bad:
        return refuse()

    t0 = time.time()
    u = universe(alerts)
    coins = P.coin_sides(len(u))
    arrays = day_arrays_of(bars)
    att, _ = attempts(u, arrays, day_kind, coins)
    mi, n_mi = missed_identity(u, att, rows)
    ident(f"on the {n_mi} orders whose alert the engine triggered on the alert's own trading day, the bars' missed flag "
          "(price at T from the alert bar's end slot through alert + 5) equals D-607's missed_L5", mi)
    if bad:
        return refuse()
    filled = att[att["outcome"] == P.FILLED]
    Ss = sorted({int(x) for x in filled["S"]})
    fees = I["A"].fee_by_stop(I["fcfg"], Ss, P.TICK_VALUE) if Ss else {}
    trades = trade_frame(u, att, fees, I)
    leak = trades[(trades["day_kind"] == P.REPORT_DAY_KIND) & (trades["fill_slot"] <= P.RELEASE_CLEAR)]
    ident("no filled trade is a report day's on a bar starting before 07:35 CT (D-533 (2))",
          [] if leak.empty else [f"{len(leak)} report-day fills before 07:35 CT"])
    pol_ok = set(att["outcome"]) <= {P.FILLED, *P.REASONS}
    ident("every attempt ends filled or with a declared reason", [] if pol_ok else [str(set(att["outcome"]))])
    print(f"the policies and walks: {len(u)} orders (alerts in hours), {len(att)} attempts placed, {time.time() - t0:.0f} s", flush=True)
    if bad:
        return refuse()
    if a.check:
        counts = P.boot_counts(len(sessions), reps=20)       # the code path only, at 20 replicates; nothing printed
        kill_rows(trades, sessions, I)
        beside_rows(trades, att, u, sessions, counts, I)
        print(f"--check done: {start} .. {end}; the pins, identities and every policy ran; no reading printed or "
              f"written. {time.time() - t_all:.0f} s")
        return 0

    t0 = time.time()
    counts = P.boot_counts(len(sessions))
    kill = kill_rows(trades, sessions, I)
    ref = k3_reference(I)
    beside = beside_rows(trades, att, u, sessions, counts, I)
    surv = [r["box_points"] for r in kill if r["survives"]]
    verdict = {"section": "verdict", "surviving_boxes": ";".join(f"{b:g}" for b in surv),
               "survivors": len(surv),
               "verdict": ("a box survives K1-K3: its campaign is declared as PFA's family pre-registration (D-611)"
                           if surv else "no box survives K1-K3: arm A closes at contract fit (D-611)"),
               "reading": READING}
    print(f"the readings: {time.time() - t0:.0f} s", flush=True)
    out = pd.concat([pd.DataFrame(idents), pd.DataFrame(kill), pd.DataFrame([ref]), pd.DataFrame(beside),
                     pd.DataFrame([verdict])], ignore_index=True)
    out = out.drop(columns=["reading"], errors="ignore")
    out.insert(1, "reading", READING)
    trades.insert(0, "reading", READING)
    m = manifest(P.MARKET)
    seconds = time.time() - t_all
    params = {"decision": DECISION, "family": P.FAMILY_ID, "market": P.MARKET, "first_day": start, "last_day": end,
              "purpose": "development", "sessions": len(sessions), "bars_read": int(len(bars)),
              "bar_store_sha256": (m or {}).get("parquet_sha256"), "boxes_points": list(P.BOXES),
              "config": P.CONFIG, "config_sha256_lf": P.CONFIG_SHA256_LF, "setups_file": f"results/{P.SETUPS_FILE}",
              "setups_sha256": P.SETUPS_SHA256, "choice": P.FIXED_CHOICE, "latency_minutes": P.LATENCY_MIN,
              "policies": list(P.POLICIES), "card_policy": P.CARD_POLICY, "cells": [list(c) for c in P.CELLS],
              "entry_slip_ticks": P.ENTRY_SLIP_TICKS, "tick": P.TICK, "tick_value": P.TICK_VALUE,
              "exit_ticks": {P.KIND_NAME[k]: v for k, v in P.EXIT_TICKS.items()},
              "walk_end_slot": int(P.FLAT_ENTRY), "release_clear_slot": P.RELEASE_CLEAR,
              "k1_min": P.K1_MIN, "k2_max": P.K2_MAX, "k2_year_min_sessions": P.K2_YEAR_MIN_SESSIONS,
              "k3_risks": I["risks"], "k3_risks_source": "a3_brk30_cb20.noclose_plan (state_policy_v12_noclose), "
                                                         "a3_brk30.fresh_decisions",
              "k3_allowance_micros": I["allowance"], "k3_allowance_source": "model_card.full_allowance (D-289)",
              "seed": P.SEED, "boot_reps": P.BOOT_REPS, "boot_block": P.BOOT_BLOCK, "bound_quantile": P.BOUND_Q,
              "fees_by_stop_ticks": {str(k): v for k, v in fees.items()}, "walk_identity_compared": n_cmp,
              "orders": int(len(u)), "attempts": int(len(att)), "trades": int(len(trades)),
              "correction": P.CORRECTION, "alert_fates": fates,
              "k3_reading": "D-312 (1) by stop width (D-612 (1)); D-611's single figure beside",
              "missed_rule": "price at T on a bar ending from the alert bar's end slot through alert + 5 (D-612 (2))",
              "cancel_rule": "one rule for every policy: a working bar before the fill reaching the stop or the target, "
                             "or 15:08 CT with no fill (D-612 (2))",
              "seconds": round(seconds, 1)}
    notes = {"status": READING, "seed": f"{P.SEED}: the bound's stationary bootstrap and the coin (separate "
                                        "generators, each seeded with it)",
             "variant_count_rule": f"D-611: 20 cells under {P.FAMILY_ID}; with D-607's 20 definitions and S4's 10 in "
                                   "any later N; nothing selected here"}
    write_result(out, P.RESULT, script=SCRIPT, seed=P.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(P.CELLS), parameters=params, notes=notes,
                 description="EXPLORATORY (D-611): family PFA's cheap screen on NQ development bars 2020-01-01 to "
                             "2026-07-16 -- the P&F catapult (r7_low) on its natural bracket at L = 5 under rest, skip "
                             "and chase, the plain triple top / bottom at rest, boxes 2.5 / 5 / 6.25 / 7.5 / 10 points; "
                             "K1-K3 contract-fit kill lines per box on rest; e, its bound, the coin and the rest beside.")
    write_result(trades, P.RESULT_TRADES, script=SCRIPT, seed=P.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(P.CELLS), parameters=params, notes=notes,
                 description="EXPLORATORY (D-611): one row per filled trade of family PFA's cheap screen -- the setup, "
                             "the policy and fill, the walk to stop / target / 15:10, gross and net R at P-16's costs "
                             "and the drift-matched coin twin.")
    counter = VariantCounter(path=rd / "variants.jsonl")
    for box, group, pol in P.CELLS:
        counter.record(prereg_id=P.FAMILY_ID, seed=P.SEED, exploratory=True,
                       params={"study": "D-611 PFA cheap screen", "box_points": box, "group": group, "policy": pol,
                               "reading": P.FIXED_CHOICE if group == P.CATAPULT else "plain",
                               "latency_minutes": P.LATENCY_MIN, "correction": P.CORRECTION},
                       label=f"D-611's PFA screen: box {box:g}, {group}, {pol}")
    print(f"written: {P.RESULT}.csv ({len(out)} rows), {P.RESULT_TRADES}.csv ({len(trades)} trades); 20 cells recorded "
          f"under {P.FAMILY_ID}; {seconds:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
