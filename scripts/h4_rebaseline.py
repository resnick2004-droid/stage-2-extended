"""H4: the re-baseline runner (`prereg/H4_rebaseline.md`, pinned in E-287; LF sha256
`a2c1408e8f22a3d4926248a3bf53f311f65234ce1e15399dc378ed35d4aa913c`).

Parts (one heavy slot at a time from a clean checkout under `run.lock`, `OMP_NUM_THREADS=1`, max 2 workers):
- `H4-0`   : synthetic cost/memory probe (`h4_0_probe`, part `H4-0`) + P-14 first 21 real search-year starts on
             `arm="point"` built through `search_cut.pass_through`, written SEALED (only sha256 recorded).
- `H4-S`   : build all 4 search-year schedules (`naive_coin`, `p14`, `p15`, `p16`) through `search_cut.pass_through`,
             verify identities I-1 (search sub-hash), I-2 (nested cuts 2022-12-30 / 2023-06-30 / 2023-09-29 vs
             2023-12-29), I-3 (race vs `BinaryDraw`), and I-5 (coin source in P-16 mode `trades_hash`), count supply,
             resolution, realised risk, breakeven, same-bar, schedule-overlap, coverage (38), idle (39) -> write
             `results/h4_supply.csv` and `results/h4_identities.csv`.
- `H4-A`   : as-traded replays of `p14`, `p15`, `p16` via `user_beside.run_starts(..., "point", BY_NAME["off"],
             journey=True, journey_block="search")` built through `search_cut.pass_through`, verify H4-0 sealed hash
             and identity I-4 (`three_way_baseline` `outcome="vendored"` matches H4-A) -> write `results/h4_as_traded.csv`.
- `H4-B`   : seed-paired firm-path readings for one baseline (`--baseline naive_coin|p14|p15|p16`) over disjoint start
             range `[--start-lo, --start-hi)` and ALL `J_H4 = 128` seeds (`0..127`), all 4 arm-runs (`off` deciding,
             `as_walked` beside, `worse_1`, `missed_0.1`), enforcing strict `+ 5 min` overlap == 0 on every unit and
             independent scalar oracle on every 1% `h4_sample` unit -> write `results/h4_units_<b[_tag]>.csv`,
             `results/h4_readings_<b[_tag]>.csv`, `results/h4_trades_<b[_tag]>.csv`.
- `merge`  : combine split `H4-B` parts for one baseline into unified `results/h4_units_<baseline>.csv`,
             `results/h4_readings_<baseline>.csv`, and `results/h4_trades_<baseline>.csv` with full MEASURES 1.4,
             variance decomposition (34), by-year (32), and Section 12 beside summary rows.
- `audit`  : Section 16 item 6 independent auditor re-derivation before W42-R1 reads anything.

Zero raw H4 seed literals appear here or in any manifest; all H4 seeds are issued by role through
`extended.three_way_seeds.issue`.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import gc
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import h4_audit as HA  # noqa: E402
from extended import h4_coin_source as CS  # noqa: E402
from extended import journey_measures as JM  # noqa: E402
from extended import search_calendar as SCAL  # noqa: E402
from extended import search_cut as SC  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import walker as W  # noqa: E402
from extended import wave42 as W42  # noqa: E402

SCRIPT = "scripts/h4_rebaseline.py"
#: the declared worker cap (H4 section 7's part-cap row: "at most 2 workers, one BLAS thread"); H4-A keeps it
MAX_WORKERS = 2
#: the lead's ruling on the sizing scout (Q-188b, 2026-11-27): H4-B's worker count is a run flag up to 4 -- an execution
#: resource, not a rule of the result (batches are submitted and collected in order, each batch's keys only its own
#: (start, seed index)), recorded under the lead's row once the units identity at the new count holds
H4B_MAX_WORKERS = 4
BATCH_STARTS = 21
EXACT_HORIZONS = (21, 63, 90, 126)
EXACT_EVERY = 21
BASELINES = ("naive_coin", "p14", "p15", "p16")
REGISTERED = ("p14", "p15", "p16")
#: (arm_name, reading_tag, outcome_mode, ArmSpec, exact_every_start)
ARM_SPECS: tuple[tuple[str, str, str, J.ArmSpec, bool], ...] = (
    ("off", W42.READING, "race", J.ArmSpec(), True),
    ("off_as_walked", "as_walked", "as_walked", J.ArmSpec(), True),
    ("worse_1", W42.READING, "race", J.ArmSpec(worse_ticks=1), False),
    ("missed_0.1", W42.READING, "race", J.ArmSpec(missed_q=0.10), False),
)
#: m-i (Q-188b): each arm's label, written beside every reading row (no colon: the results' timestamp scan reads cells)
READING_LABELS: dict[str, str] = {
    "off": "deciding - the martingale race on the firm path, response off",
    "off_as_walked": (
        "as-walked, beside - the historical outcome reflected by the side coin; the rc-11 clamp bounds the mirror AND "
        "the unflipped side within [-stop, +G] with G the need-capped target where the need caps it, so a need-capped "
        "trade's as-walked long side books at most the capped target (m-i)"
    ),
    "worse_1": "stress, beside - one extra tick of cost a side",
    "missed_0.1": "stress, beside - each signal missed with chance 0.10",
}
#: m-8 (Q-188b; section 12 "the record each horizon read"): every reading at every horizon reads the unit's long run
#: (one replay of min(252, sessions left) closes); the exact-length runs at `EXACT_HORIZONS` are compared beside it and
#: their differences classified by kind in each part's manifest (`exact_differs_by_kind`). The treatment rule for a
#: difference is the lead's (B-2), not this runner's.
RECORD_READ: str = "long_run"
#: Latency in minutes per baseline (for measure (30) screen_hours)
BASELINE_LATENCY: dict[str, float] = {"naive_coin": 5.0, "p14": 5.0, "p15": 0.0, "p16": 0.0}
#: Trade log CSV columns (ticks & times only, NO prices, NO historical u/mae/at_need/rr_used/exit_kind on race arms)
TRADE_LOG_COLS: tuple[str, ...] = (
    "baseline",
    "arm",
    "reading",
    "start",
    "start_date",
    "seed_index",
    "day_idx",
    "trade_date",
    "trade_idx",
    "acct_kind",
    "acct_index",
    "decision",
    "sub",
    "underlying",
    "fill_bar",
    "exit_bar_at_R",
    "exit_bar_latest",
    "time_limit",
    "be_open",
    "sigma",
    "stop_ticks",
    "R",
    "kind_hist",
    "G",
    "L_ticks",
    "room",
    "d",
    "fee",
    "e_cost",
    "xt_cost",
    "xs_cost",
    "xf_cost",
    "law",
    "exit_code",
    "p",
    "s1",
    "n1",
    "s2",
    "n2",
    "move_x",
    "move_moved",
    "move_G2",
    "move_down2",
    "race_need",
    "out",
    # m-e (Q-188b): the engine's need for the trade (blank where it had none), so the oracle re-derives G
    "need",
    "need_logged",
)


# --------------------------------------------------------------------------------------------- bundle builder (search cut)


@dataclass
class BaselineBundle:
    """Search-year schedule, vendored DayBlocks, replay args, and per-trade `TradeFacts` for one baseline."""

    name: str
    dates: tuple[str, ...]
    trades: pd.DataFrame
    blocks: list[Any]
    args: dict[str, Any]
    facts: dict[tuple[int, int], TB.TradeFacts]
    trades_sha256: str
    meta: dict[str, Any]
    raw_blocks: list[Any] | None = None


def _setup_vendor() -> Path:
    from extended import VENDOR_STAGE2, use_vendored_stage2

    use_vendored_stage2()
    return VENDOR_STAGE2


def _peak_mb() -> float:
    """The lead's ruling (Q-188b): this process's peak working set since it started, in MB -- Windows' psapi through
    `extended.procmem` (psutil is not installed here); NaN on another platform."""
    from extended import procmem as PM

    return float(PM.working_set_mb(peak=True))


def _rss_mb() -> float:
    """This process's working set now, in MB. F-4 (Q-188b): psutil is not installed on this machine, so the psutil
    form returned NaN and H4-0's three memory columns were blank; `extended.procmem` reads Windows' psapi."""
    from extended import procmem as PM

    return float(PM.working_set_mb(peak=False))


def _extract_day_arrays_search(dates: Sequence[str], cfg: Mapping[str, Any]) -> dict[str, tuple[np.ndarray, ...]]:
    """Read search-year bars through the active `search_cut` into Stage 2's walker array layout per day."""
    import atlas_a3 as A

    arr_fn = A.bar_arrays(dict(cfg), list(dates))
    return {str(d): arr_fn(str(d)) for d in dates}


def _build_facts_for_trades(
    trades: pd.DataFrame,
    dates: Sequence[str],
    day_arrs: Mapping[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    *,
    tick_value: float,
    entry_ticks: float,
    rr_cols: Sequence[float],
    aux_df: pd.DataFrame | None = None,
    tick: float = W.TICK,
) -> tuple[pd.DataFrame, dict[tuple[int, int], TB.TradeFacts], dict[str, Any]]:
    """Compute causal cross-session `sigma` (F4-1), `be_open`, `be_vendored`, mirror walk gross ticks (rc-11),
    and `TradeFacts` for every trade in `trades`, dropping any trade whose alert has `< 2` prior close changes
    (F4-1, counted beside). Returns `(kept_trades, facts_by_day_idx, stats)`."""
    date_to_idx = {str(d): i for i, d in enumerate(dates)}
    day_closes = [day_arrs[str(d)][3] for d in dates]
    bl_cache: dict[tuple[int, tuple[float, ...]], list[tuple[int, float, int]]] = {}

    keep_mask = np.ones(len(trades), dtype=bool)
    sigmas: list[float] = []
    be_vends: list[int | None] = []
    limits: list[int] = []
    limit_differs = 0
    limit_differs_dates: list[str] = []
    dropped_sigma = 0
    dropped_sigma_zero = 0
    rms_fallback = 0
    dropped_rows: list[dict[str, Any]] = []

    # Pre-compute sigma, limit, be_vendored per row
    for idx_r in range(len(trades)):
        r = trades.iloc[idx_r]
        d_str = str(r["date"])
        d_i = date_to_idx[d_str]
        dec = int(r["decision_slot_minutes"])
        ent = int(round(float(r["entry_t"])))
        o = day_arrs[d_str][0]
        last_b = W.last_bar(o)
        if aux_df is not None and not aux_df.empty:
            lim = int(aux_df.iloc[idx_r]["time_limit"])
            sig = float(aux_df.iloc[idx_r]["sigma"])
            bv_raw = aux_df.iloc[idx_r]["be_vendored"]
            bv = None if pd.isna(bv_raw) else int(bv_raw)
        else:
            lim = max(ent, int(W.FLAT_ENTRY))
            if last_b is not None and last_b < lim:
                limit_differs += 1
                limit_differs_dates.append(d_str)
            # F-3 (Q-188b): the reading's reason, so the declared drop (< 2 changes) and a zero dispersion are
            # counted apart; which trades are kept is unchanged from 31c507e
            sr = CS.alert_sigma_detail(day_closes, d_i, dec, tick=tick)
            sig_opt = sr.sigma
            if sig_opt is None:
                keep_mask[idx_r] = False
                if sr.reason == CS.SIGMA_ZERO:
                    dropped_sigma_zero += 1
                else:
                    dropped_sigma += 1
                dropped_rows.append(CS.sigma_drop_row(d_str, dec, sr))
                sigmas.append(float("nan"))
                be_vends.append(None)
                limits.append(lim)
                continue
            rms_fallback += int(sr.rms_fallback)
            sig = float(sig_opt)
            eff_end = int(W.walk_end(o, W.STAGE2) or lim)
            bv = CS.vendored_move_bar(o, ent, eff_end)
        sigmas.append(sig)
        be_vends.append(bv)
        limits.append(lim)

    kept_idx = np.flatnonzero(keep_mask)
    kept_trades = trades.iloc[kept_idx].reset_index(drop=True)
    kept_aux = aux_df.iloc[kept_idx].reset_index(drop=True) if (aux_df is not None and not aux_df.empty) else None
    sigmas_kept = [sigmas[i] for i in kept_idx]
    be_vends_kept = [be_vends[i] for i in kept_idx]
    limits_kept = [limits[i] for i in kept_idx]

    # m-5: stable-sort kept_trades (and parallel metadata) on ["date", "entry_t"] so (d_i, j) always matches gate_blocks
    if len(kept_trades) > 1:
        order = kept_trades.sort_values(["date", "entry_t"], kind="stable").index.to_numpy(dtype=int)
        kept_trades = kept_trades.iloc[order].reset_index(drop=True)
        if kept_aux is not None:
            kept_aux = kept_aux.iloc[order].reset_index(drop=True)
        sigmas_kept = [sigmas_kept[i] for i in order]
        be_vends_kept = [be_vends_kept[i] for i in order]
        limits_kept = [limits_kept[i] for i in order]

    # Compute mirror walk gross ticks per day for registered baselines (when aux_df doesn't already hold mirr_g_R)
    mirror_by_row: dict[int, dict[float, float]] = {}
    if kept_aux is not None and f"mirr_g_{rr_cols[0]:g}" in kept_aux.columns:
        for row_pos in range(len(kept_trades)):
            mirror_by_row[row_pos] = {
                float(R): float(kept_aux.iloc[row_pos][f"mirr_g_{R:g}"]) for R in rr_cols if f"mirr_g_{R:g}" in kept_aux.columns
            }
    else:
        for d_str, grp in kept_trades.groupby("date", sort=False):
            o, h, l, c = day_arrs[str(d_str)]
            eff_end = W.walk_end(o, W.STAGE2)
            for stop_val, sgrp in grp.groupby("S", sort=False):
                S_int = int(stop_val)
                key_bl = (S_int, tuple(float(R) for R in rr_cols))
                if key_bl not in bl_cache:
                    bl_cache[key_bl] = W.brackets((S_int,), rr_cols)
                bl = bl_cache[key_bl]
                row_positions = sgrp.index.to_numpy(dtype=int)
                fbs = np.round(sgrp["entry_t"].to_numpy(dtype=float)).astype(int)
                # Mirror walks the opposite side (-side) on the exact same fill bars under STAGE2
                sides_m = np.where(sgrp["side"].astype(str).to_numpy() == "long", -1.0, 1.0)
                valid = (fbs >= 1) & (fbs < (eff_end or 0)) & (~np.isnan(o[np.clip(fbs, 0, len(o) - 1)]))
                if valid.any():
                    v_fbs = fbs[valid]
                    v_fps = o[v_fbs]
                    mres = W.walk(
                        o, h, l, c, v_fbs, v_fps, sides_m[valid], np.zeros(len(v_fbs), dtype=bool), bl, tick=tick, rules=W.STAGE2
                    )
                    v_pos = row_positions[valid]
                    for k_local, rpos in enumerate(v_pos):
                        mirror_by_row[int(rpos)] = {
                            float(R): float(mres["gross"][k_local, bi]) for bi, R in enumerate(rr_cols)
                        }
                for rpos in row_positions[~valid]:
                    mirror_by_row[int(rpos)] = {}

    # Build TradeFacts keyed by (block_day_index, trade_index_within_day) matching `score_fv3_grid.gate_blocks` order
    facts: dict[tuple[int, int], TB.TradeFacts] = {}
    per_day_j: dict[int, int] = {}
    for pos_in_kept in range(len(kept_trades)):
        r = kept_trades.iloc[pos_in_kept]
        d_i = date_to_idx[str(r["date"])]
        j = per_day_j.get(d_i, 0)
        per_day_j[d_i] = j + 1

        dec = int(r["decision_slot_minutes"])
        ent = int(round(float(r["entry_t"])))
        S_int = int(r["S"])
        lim = max(ent, int(limits_kept[pos_in_kept]))
        sig = float(sigmas_kept[pos_in_kept])
        be_op = TB.move_bar(ent)
        bv = be_vends_kept[pos_in_kept]
        fee_m = float(r["fee_micro_eq"])

        kinds: dict[float, str] = {}
        walked: dict[float, float] = {}
        mirr: dict[float, float] = {}
        m_row = mirror_by_row.get(pos_in_kept, {})
        for R in rr_cols:
            ok_col = f"o_{R:g}"
            g_col = f"g_{R:g}"
            if ok_col in kept_trades.columns and pd.notna(r[ok_col]) and str(r[ok_col]) in TB.KINDS:
                k_code = str(r[ok_col])
                # Guard: if be_open is None or >= lim, a historical 'b' cannot occur under clock limit; keep valid
                if k_code == "b" and (be_op is None or be_op >= lim):
                    k_code = "f"
                kinds[float(R)] = k_code
                g_val = float(r[g_col]) * S_int if (g_col in kept_trades.columns and pd.notna(r[g_col])) else 0.0
                walked[float(R)] = g_val
                if float(R) in m_row:
                    mirr[float(R)] = float(m_row[float(R)])
                else:
                    # Fallback bounded mirror if bar missing
                    mirr[float(R)] = max(-float(S_int), min(float(TB.target_ticks(R, S_int)), -g_val))

        facts[(d_i, j)] = TB.TradeFacts(
            decision=dec,
            entry=ent,
            stop_ticks=S_int,
            tick_value=float(tick_value),
            kinds=kinds,
            limit=lim,
            sigma=sig,
            be_open=be_op,
            be_vendored=bv,
            e_ticks=float(entry_ticks),
            xt_ticks=float(W.EXIT_TICKS[W.TARGET]),
            xs_ticks=float(W.EXIT_TICKS[W.STOP]),
            xf_ticks=float(W.EXIT_TICKS[W.FLATTEN]),
            fee_per_contract=fee_m,
            walked=walked,
            walked_mirror=mirr,
            underlying="NQ",
        )

    stats = {
        "dropped_sigma_lt_2": dropped_sigma,
        # F-3 (Q-188b): alerts with two or more changes behind them, every one zero (sigma = 0): dropped as before,
        # never again counted as "fewer than two changes"; their treatment is the lead's (not declared)
        "dropped_sigma_zero": dropped_sigma_zero,
        "sigma_rms_fallback": rms_fallback,
        "dropped_sigma_rows": dropped_rows,
        "limit_differs_from_last_bar": limit_differs,
        "limit_differs_dates": limit_differs_dates,
        "facts_count": len(facts),
        # F-3: the schedule the firm path actually consumes (after the sigma drop), hashed in the I-1 form
        "kept_trades": int(len(kept_trades)),
        "kept_trades_sha256": SC.trades_subhash(kept_trades) if len(kept_trades) else None,
    }
    return kept_trades, facts, stats


def needs_block_rebuild(f_stats: Mapping[str, Any]) -> bool:
    """F-3 (Q-188b): the DayBlocks are rebuilt from the kept trades whenever the sigma drop removed any trade, for
    either reason -- so the blocks' trade indices stay one to one with the facts."""
    return int(f_stats.get("dropped_sigma_lt_2", 0)) + int(f_stats.get("dropped_sigma_zero", 0)) > 0


def build_registered_bundle(
    design: str,
    *,
    last_day: str = W42.SEARCH_LAST,
    verify_i1: bool = True,
    with_facts: bool = True,
    root: Path = ROOT,
) -> BaselineBundle:
    """Build P-14, P-15, or P-16 inside `search_cut.pass_through`, verifying `check_calendar` (rm-6) and I-1 sub-hash."""
    if design not in REGISTERED:
        raise ValueError(f"registered design must be one of {REGISTERED}, got {design!r}")
    vroot = _setup_vendor()
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import customer_slices as cs
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_screen as RS
    import score_fv3_grid as gf
    import user_journey as UJ

    reg_path = root / HA.H4_REG_CONSTANTS_REL
    reg = SC.load_constants(reg_path, expected_sha256=HA.H4_REG_CONSTANTS_SHA256)
    SC.authorise(
        purpose="h4_search_years",
        declaration="E-287",
        what=f"H4 build {design} through search_cut.pass_through up to {last_day}",
        last=last_day,
        bars=True,
        root=vroot,
    )

    with SC.pass_through(
        design,
        reg_path,
        expected_sha256=HA.H4_REG_CONSTANTS_SHA256,
        last=last_day,
        root=vroot,
    ) as cut_log:
        if design == "p14":
            I_in = RS.inputs()
            L = I_in["L"]
            t_raw, days_list = B.cell_trades(L)
            # Build P-14 campaign job via UJ.build_d518 (point arm)
            jobs_d518, _ = UJ.build_d518(vroot / "results", ["p14"])
            job = jobs_d518["p14"]["point"]
            days = [str(d) for d in job["dates"]]
            rr_cols = tuple(float(R) for R in B.rrs(t_raw))
            cfg, tv = L["cfg"], float(L["tv"])
        elif design == "p15":
            I_in, b_p15 = D.build_cells()
            L = I_in["L"]
            t_raw = b_p15["cells"][D.P15.cell]["trades"]
            days = [str(d) for d in b_p15["days"]]
            camp = UJ._rc_campaign(I_in, b_p15, D.P15.cell, D.P15)
            job = UJ._single_jobs(camp, I_in["plan"], C.BUDGET)["point"]
            rr_cols = tuple(float(R) for R in B.rrs(t_raw))
            cfg, tv = L["cfg"], float(L["tv"])
        else:  # p16
            I_in, b_p16 = R150.build_cells()
            L = I_in["L"]
            t_raw = b_p16["cells"][R150.SPEC.cell]["trades"]
            days = [str(d) for d in b_p16["days"]]
            camp = UJ._rc_campaign(I_in, b_p16, R150.SPEC.cell, R150.SPEC)
            job = UJ._single_jobs(camp, I_in["plan"], C.BUDGET)["point"]
            rr_cols = tuple(float(R) for R in B.rrs(t_raw))
            cfg, tv = L["cfg"], float(L["tv"])

        # rm-6: cut A1 day list == Q-197 pinned search calendar up to last_day
        SC.check_calendar(days, calendar_path=root / HA.H4_SEARCH_CALENDAR_REL, last=last_day)
        # I-1: search-year sub-hash matches registered constants
        raw_hash = SC.verify_subhash(design, t_raw, reg, last=last_day) if verify_i1 else SC.trades_subhash(t_raw, last=last_day)

        day_arrs = _extract_day_arrays_search(days, cfg) if with_facts else {}
        cut_probs = cut_log.problems()
        if cut_probs:
            raise HA.H4AuditRefused(f"REFUSED (search_cut): {design} cut log problems: {cut_probs}")
        cut_summary = cut_log.manifest_summary()

    raw_blocks = list(job["blocks"])
    if not with_facts:
        return BaselineBundle(
            name=design,
            dates=tuple(days),
            trades=t_raw,
            blocks=raw_blocks,
            args=dict(job["args"]),
            facts={},
            trades_sha256=raw_hash,
            meta={"cut": cut_summary, "raw_trades": len(t_raw)},
            raw_blocks=raw_blocks,
        )

    kept_trades, facts, f_stats = _build_facts_for_trades(
        t_raw,
        days,
        day_arrs,
        tick_value=tv,
        entry_ticks=float(cfg["slip_ticks"]),
        rr_cols=rr_cols,
    )
    if needs_block_rebuild(f_stats):
        # Rebuild DayBlocks from kept_trades so block trade indices align 1-to-1 with `facts`! (either reason: F-3
        # split the count, never the set of trades dropped)
        blocks_kept, n_used = gf.gate_blocks(kept_trades, days, tv, list(rr_cols), require_sides=True, require_exits=True)
        if n_used != len(kept_trades):
            raise HA.H4AuditRefused(f"{design}: gate_blocks used {n_used} != {len(kept_trades)}")
        blocks_use = list(blocks_kept)
    else:
        blocks_use = raw_blocks

    return BaselineBundle(
        name=design,
        dates=tuple(days),
        trades=kept_trades,
        blocks=blocks_use,
        args=dict(job["args"]),
        facts=facts,
        trades_sha256=raw_hash,
        meta={"cut": cut_summary, "raw_trades": len(t_raw), **f_stats},
        raw_blocks=raw_blocks,
    )


def build_naive_coin_bundle(
    *,
    last_day: str = W42.SEARCH_LAST,
    root: Path = ROOT,
) -> BaselineBundle:
    """Build H4's unchained naive coin schedule & P-16-shaped campaign bundle on search years only."""
    vroot = _setup_vendor()
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_screen as RS
    import user_journey as UJ
    import zero_edge_decomposition as zd

    from extended import day_calendar as DC

    reg_path = root / HA.H4_REG_CONSTANTS_REL
    reg = SC.load_constants(reg_path, expected_sha256=HA.H4_REG_CONSTANTS_SHA256)
    cal_src = DC.load_sources(
        flags=root / "results" / "h2_overnight_flags.csv",
        manifest=vroot / "data" / "bars" / "NQ" / "manifest.json",
        calendar=root / "config" / "calendar_early_closes.csv",
    )

    SC.authorise(
        purpose="h4_search_years",
        declaration="E-287",
        what=f"H4 build naive_coin through search_cut up to {last_day}",
        last=last_day,
        bars=True,
        root=vroot,
    )
    with SC.cut(last=last_day, root=vroot) as cut_log:
        I_in = RS.inputs()
        L = I_in["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        days_df = L["days"].copy()
        days_df["date"] = days_df["date"].astype(str)
        days_df = days_df.sort_values("date", kind="stable").reset_index(drop=True)
        days = days_df["date"].tolist()
        SC.check_calendar(days, calendar_path=root / HA.H4_SEARCH_CALENDAR_REL, last=last_day)
        day_kinds = dict(zip(days_df["date"], days_df["day_kind"].astype(str)))
        day_arrs = _extract_day_arrays_search(days, cfg)
        fees = A.fee_by_stop(fcfg, (CS.P16_STOP_TICKS,), tv)
        crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
        rr_grid = A.rrs(cfg)
        keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I_in["plan"])))
        cut_probs = cut_log.problems()
        if cut_probs:
            raise HA.H4AuditRefused(f"REFUSED (search_cut): naive_coin cut log problems: {cut_probs}")
        cut_summary = cut_log.manifest_summary()

    res = CS.build_naive_coin_trades(
        days,
        day_kinds,
        lambda d: day_arrs[d],
        lambda d_obj, s_idx: DC.day_context(cal_src, "NQ", d_obj, s_idx, reads_overnight=True, rules=W.STAGE2),
        fee_micro_eq=float(fees[CS.P16_STOP_TICKS]),
        tick=float(cfg["contract"]["tick"]),
        tick_value=tv,
        entry_ticks=float(cfg["slip_ticks"]),
        stop_ticks=CS.P16_STOP_TICKS,
        rr_grid=rr_grid,
        fresh_rr=crr,
        latency=CS.COIN_LATENCY,
        data_void_fn=lambda d_obj: DC.data_void(cal_src, d_obj, rules=W.STAGE2),
    )
    t_pad = zd.pad(res.trades, keys) if len(res.trades) else res.trades
    th = SC.trades_subhash(t_pad, last=last_day)

    # P-16's registered job's money side (noclose table, 20/21 budget, 5 seats, strict gap 5.0)
    _, e_by, lb_by, _, _ = A.bounds(t_pad, days, B.rrs(t_pad), cfg)
    cap = max(int(reg["p16"]["capacity"]), int(B.capacity(t_pad, fcfg)))
    camp = D.rc_campaign(I_in, t_pad, days, e_by, lb_by, cap, R150.SPEC)
    job = UJ._single_jobs(camp, I_in["plan"], C.BUDGET)["point"]

    kept_trades, facts, f_stats = _build_facts_for_trades(
        t_pad,
        days,
        day_arrs,
        tick_value=tv,
        entry_ticks=float(cfg["slip_ticks"]),
        rr_cols=tuple(float(R) for R in B.rrs(t_pad)),
        aux_df=res.aux,
    )
    # m-1: propagate naive_coin's own dropped_sigma_lt_2 and limit_differs_from_last_bar into top-level meta
    meta_nc = {
        "cut": cut_summary,
        "coin_counts": res.counts,
        "capacity": cap,
        **f_stats,
        "dropped_sigma_lt_2": int(res.counts.get("offers_dropped_sigma_lt_2", 0)) + int(f_stats["dropped_sigma_lt_2"]),
        "dropped_sigma_zero": int(res.counts.get("offers_dropped_sigma_zero", 0)) + int(f_stats["dropped_sigma_zero"]),
        "sigma_rms_fallback": int(res.counts.get("sigma_rms_fallback", 0)) + int(f_stats["sigma_rms_fallback"]),
        "dropped_sigma_rows": list(res.counts.get("dropped_sigma_rows", [])) + list(f_stats["dropped_sigma_rows"]),
        "limit_differs_from_last_bar": int(res.counts.get("limit_differs_from_last_bar", 0))
        + int(f_stats["limit_differs_from_last_bar"]),
        "limit_differs_dates": list(res.counts.get("limit_differs_dates", [])) + list(f_stats["limit_differs_dates"]),
        "data_defect_lookahead_dates": list(res.counts.get("data_defect_lookahead_dates", [])),
    }
    raw_blks = list(job["blocks"])
    return BaselineBundle(
        name="naive_coin",
        dates=tuple(days),
        trades=kept_trades,
        blocks=raw_blks,
        args=dict(job["args"]),
        facts=facts,
        trades_sha256=th,
        meta=meta_nc,
        raw_blocks=raw_blks,
    )


def build_bundle(baseline: str, *, last_day: str = W42.SEARCH_LAST, root: Path = ROOT) -> BaselineBundle:
    if baseline == "naive_coin":
        return build_naive_coin_bundle(last_day=last_day, root=root)
    return build_registered_bundle(baseline, last_day=last_day, root=root)


# --------------------------------------------------------------------------------------------- H4-0: probe


def _synthetic_h4_0_probe(probe_seed: Any, probe_part: int, *, j_tb: int = 16, h_tb: int = 63) -> dict[str, Any]:
    """M-1: synthetic cost/memory probe timing BOTH vectorized `R.run` (ToyRules) AND `TB.simulate(..., outcome='race')`
    (with move + walk + race laws) on synthetic data only (no bars read)."""
    import datetime as _dt
    from extended import three_way_s1 as S1

    _setup_vendor()
    from propedge.campaign.lockstep import ConductModel
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import RiskPolicy
    from propedge.campaign.sizing import SizingRule
    from propedge.contract.adapter import rules_from_ledger
    from propedge.outcomes.distribution import DayBlock

    # Part A: vectorized three_way_runner probe (40 starts x 64 seeds x 63 sessions)
    s1p = S1.S1Params(n_sessions=110)
    hist = S1.generate(probe_seed, probe_part, 0, s1p)
    spec = S1.DesignSpec("probe_race", stream="A", fixed_stop=40, rr=2.0, per_session=4)
    sched = S1.schedule(spec, hist)
    toy_rules = J.ToyRules(
        combine_fee=49.0,
        billing=21,
        target=3000.0,
        mll=2000.0,
        dll=None,
        activation_fee=149.0,
        funded_mll=2000.0,
        win_day=150.0,
        payout_days=5,
        payout_share=0.5,
        payout_cap=2000.0,
        split=0.9,
        payout_lag=2,
    )
    plan = R.Plan(
        seed=probe_seed,
        part=probe_part,
        history=0,
        starts=range(40),
        seed_indices=range(64),
        horizon=63,
        block_sessions=s1p.n_sessions,
        budget=1000.0,
    )
    t0 = time.perf_counter()
    _ = R.run(sched, toy_rules, plan, J.ArmSpec())
    syn_s = time.perf_counter() - t0
    lane_trades = max(1, len(sched.trades) * 64)
    us_per_lane_trade = (syn_s * 1e6) / lane_trades

    # Part B: real-protocol synthetic TB.simulate(..., outcome="race") timing probe (with move + walk + race)
    n_days = max(int(h_tb) + 10, 80)
    syn_dates = tuple((_dt.date(2020, 1, 2) + _dt.timedelta(days=k)).isoformat() for k in range(n_days))
    syn_cal = frozenset(_dt.date.fromisoformat(d) for d in syn_dates)
    stop_t = 150
    tick_v = 0.5
    rs_syn = (1.5, 2.0)
    blocks_s: list[Any] = []
    facts_s: dict[tuple[int, int], TB.TradeFacts] = {}
    for d_i in range(n_days):
        et = np.array([940.0, 1060.0, 1215.0], dtype=float)  # 2 move-law trades (< 1200) + 1 post-13:00 race/walk trade
        r_by: dict[float, np.ndarray] = {}
        ex_by: dict[float, np.ndarray] = {}
        for R_v in rs_syn:
            gt = TB.target_ticks(R_v, stop_t)
            r_by[R_v] = np.array([gt / stop_t, -1.0, 0.2], dtype=float)
            ex_by[R_v] = et + 35.0
        blocks_s.append(
            DayBlock(
                pnl=r_by[1.5] * 1500.0,
                risked=np.full(3, 1500.0),
                exit_reasons=("t", "s", "f"),
                risk_per_contract=np.full(3, stop_t * tick_v),
                mae=np.full(3, 300.0),
                entry_t=et,
                exit_t=ex_by[1.5],
                r_by_rr=r_by,
                mae_by_rr={R_v: np.full(3, 0.3) for R_v in rs_syn},
                fee=np.full(3, 1.22),
                sides=np.ones(3),
                exit_by_rr=ex_by,
            )
        )
        for j_t in range(3):
            ent = int(et[j_t])
            be_op = TB.move_bar(ent)
            kinds_t = {R_v: ("t" if j_t == 0 else ("s" if j_t == 1 else "f")) for R_v in rs_syn}
            facts_s[(d_i, j_t)] = TB.TradeFacts(
                decision=ent - 5,
                entry=ent,
                stop_ticks=stop_t,
                tick_value=tick_v,
                kinds=kinds_t,
                limit=1328,
                sigma=5.0,
                be_open=be_op,
                be_vendored=be_op,
                e_ticks=1.0,
                xt_ticks=0.0,
                xs_ticks=1.0,
                xf_ticks=2.0,
                fee_per_contract=1.22,
                walked={R_v: float(TB.target_ticks(R_v, stop_t) if j_t == 0 else -stop_t) for R_v in rs_syn},
                walked_mirror={R_v: float(-stop_t if j_t == 0 else TB.target_ticks(R_v, stop_t)) for R_v in rs_syn},
            )
    import dataclasses as _dc
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.contract.rules import load_rules

    rules_v = rules_from_ledger()
    proto_v = Protocol(
        name="h4_0_tb_probe",
        combine_rr=1.5,
        combine_risk=1500.0,
        funded_rr=2.0,
        funded_risk=1000.0,
        trades_per_day=3,
        max_concurrent_accounts=5,
        params={"need_aware_exits": True, "consistency_cap_exits": True},
    )
    lag_v = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    rp_v = RiskPolicy.from_protocol(proto_v, with_rr=True)
    sr_v = _dc.replace(SizingRule.from_ledger(), fee_schedule=(1.22, 3.78))
    args_v = {
        "seed": 1,
        "draws": {
            "protocol": proto_v,
            "mode": "rotation",
            "flip": None,
            "sizing": sr_v,
            "route_able": True,
            "one_at_a_time": 5.0,
            "hold_to_own_exit": True,
        },
        "path": {
            "edge": 0.0,
            "rules": rules_v,
            "initial_bankroll": 1_000_000.0,
            "max_concurrent_accounts": 5,
            "subscription": float(rules_v.subscription),
            "billing_days": int(rules_v.billing_days),
            "activation": float(rules_v.activation),
            "payout_lag_days": lag_v,
            "max_concurrent_combines": 2,
            "max_total_accounts": 5,
            "conduct": ConductModel(rtp=False, enforcement_p=0.0),
            "combine_max_days": 2000,
            "funded_horizon_days": 100_000,
            "record_trades": True,
            "risk_policy": rp_v,
        },
    }
    t_tb0 = time.perf_counter()
    rec_tb = TB.simulate(
        blocks_s,
        args_v,
        facts_s,
        0,
        list(range(int(j_tb))),
        int(h_tb),
        seed=probe_seed,
        part=probe_part,
        history=0,
        block_sessions=n_days,
        dates=syn_dates,
        calendar=syn_cal,
        outcome="race",
        log=True,
    )
    tb_s = time.perf_counter() - t_tb0
    # m-b (Q-188b): the raw count and the laws logged, so a test can fail (the max(1, ...) below only guards a division)
    tb_rows_raw = int(sum(len(lg) for lg in rec_tb.logs))
    tb_laws = sorted({str(r.get("law", "")) for lg in rec_tb.logs for r in lg})
    tb_trades = max(1, tb_rows_raw)
    tb_ms_per_trade = (tb_s * 1000.0) / tb_trades
    tb_sec_per_seed_252 = (tb_s / max(1, int(j_tb))) * (252.0 / max(1, int(h_tb)))
    return {
        "synthetic_lane_trades": lane_trades,
        "synthetic_seconds": round(syn_s, 4),
        "us_per_lane_trade": round(us_per_lane_trade, 4),
        "tb_race_seeds": int(j_tb),
        "tb_race_horizon": int(h_tb),
        "tb_race_trades": int(tb_trades),
        "tb_race_log_rows_raw": tb_rows_raw,
        "tb_race_laws": ";".join(tb_laws),
        "tb_race_seconds": round(tb_s, 4),
        "tb_race_ms_per_trade": round(tb_ms_per_trade, 4),
        "tb_race_sec_per_seed_252_est": round(tb_sec_per_seed_252, 4),
    }


def run_h4_0(*, root: Path = ROOT, results_dir: Path | None = None, sealed_dir: Path | None = None) -> dict[str, Any]:
    """H4-0 (section 11 & Appendix A): synthetic cost/memory probe (`h4_0_probe`, part `H4-0`) + P-14 first 21
    real search-year starts replayed on `arm="point"`, built through `search_cut.pass_through`, written SEALED."""
    from extended import RESULTS_DIR
    from extended import results as RES
    from extended import user_beside as UB

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=False)

    # 1. Synthetic firm-path / race / walk / TB.simulate cost probe (h4_0_probe, part H4-0)
    probe_seed = S.issue("h4_0_probe")
    probe_part = S.PARTS["H4-0"]
    rss_base = _rss_mb()
    syn = _synthetic_h4_0_probe(probe_seed, probe_part, j_tb=16, h_tb=63)
    rss_after_syn = _rss_mb()

    # 2. Real read: P-14 first 21 search-year starts, point arm, built through search_cut.pass_through, written SEALED
    bundle_p14 = build_registered_bundle("p14", verify_i1=True, with_facts=False, root=root)
    HA.check_job_ends_search_window(bundle_p14.dates, "H4-0 p14")
    job_p14 = {
        "engine": "single",
        "blocks": bundle_p14.blocks,
        "dates": list(bundle_p14.dates),
        "args": bundle_p14.args,
        "sub": float(bundle_p14.args["path"]["subscription"]),
    }
    starts_21 = list(range(EXACT_EVERY))
    t1 = time.perf_counter()
    outs_21 = UB.run_starts(
        "p14", "point", UB.BY_NAME["off"], job_p14, starts_21, workers=1, journey=True, journey_block="search"
    )
    real_s = time.perf_counter() - t1
    sec_per_start = real_s / len(starts_21)
    rss_after_real = _rss_mb()

    # Sealed output: write outside results/ and record ONLY its sha256 (file unopened!)
    sealed_payload = json.dumps(
        [
            {
                "start_day": int(o["rec"]["start_day"]),
                "start_date": str(o["rec"]["start_date"]),
                "observed": int(o["rec"]["observed"]),
                "first_pass": o["rec"]["first_pass"],
                "first_payout": o["rec"]["first_payout"],
                "rel": [round(float(v), 9) for v in o["journey"]["rel"]],
                "differs": list(o["differs"]),
            }
            for o in outs_21
        ],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    sealed_sha = hashlib.sha256(sealed_payload).hexdigest()
    sdir = Path(sealed_dir) if sealed_dir is not None else (root / ".h4_dev")
    sdir.mkdir(parents=True, exist_ok=True)
    sealed_path = sdir / "h4_0_p14_first21_sealed.json"
    sealed_path.write_bytes(sealed_payload)

    df = pd.DataFrame(
        [
            {
                "part": "H4-0",
                **syn,
                "real_p14_starts": len(starts_21),
                "real_p14_seconds": round(real_s, 4),
                "real_p14_sec_per_start": round(sec_per_start, 4),
                "rss_base_mb": round(rss_base, 2),
                "rss_after_syn_mb": round(rss_after_syn, 2),
                "rss_after_real_mb": round(rss_after_real, 2),
                "sealed_p14_first21_sha256": sealed_sha,
                "p14_trades_sha256": bundle_p14.trades_sha256,
            }
        ]
    )
    params = {
        "part": "H4-0",
        "seed_roles": ["h4_0_probe"],
        "sealed_p14_first21_sha256": sealed_sha,
        "sealed_note": "outputs written sealed (hash recorded, file unopened); H4-A must reproduce this hash",
        "preconditions": pre,
        "threads": thread_env(),  # F-13 (Q-188b)
        "cut": bundle_p14.meta["cut"],
    }
    csv_p, man_p = RES.write_result(
        df,
        "h4_0_probe",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description="H4-0 probe (E-287): synthetic R.run & TB.simulate cost/memory probe and sealed P-14 first-21-starts replay timing.",
    )
    return {
        "csv": str(csv_p),
        "manifest": str(man_p),
        "sealed_sha256": sealed_sha,
        "sec_per_start": sec_per_start,
        "tb_race_sec_per_seed_252_est": syn["tb_race_sec_per_seed_252_est"],
    }


# --------------------------------------------------------------------------------------------- H4-S: schedules & identities


def _schedule_overlap_count(trades: pd.DataFrame, rr_cols: Sequence[float]) -> int:
    """Section 5 (RB-2): trigger-level offers falling inside another offer's span
    `[fill bar end, exit bar end at largest R + 5 min)` (beside, never a kill)."""
    if trades.empty:
        return 0
    ex_cols = [f"exit_t_{R:g}" for R in rr_cols if f"exit_t_{R:g}" in trades.columns]
    latest = trades[ex_cols].max(axis=1).to_numpy(dtype=float)
    ents = trades["entry_t"].to_numpy(dtype=float)
    dates = trades["date"].astype(str).to_numpy()
    overlaps = 0
    for d in pd.unique(dates):
        m = dates == d
        spans = sorted(zip(ents[m].tolist(), latest[m].tolist()))
        max_end = -math.inf
        for a, b in spans:
            if a < max_end + 5.0 - 1e-12:
                overlaps += 1
            if b > max_end:
                max_end = b
    return overlaps


#: m-h (Q-188b): the `test`-kind id of I-3's uniforms under the `h4_tests` role (an id, not a seed; no other H4 key
#: uses it -- `tests/test_h4_build.py` checks)
I3_TEST_ID: int = 43


def i3_regime_seed(role_seed: Any, regime: int) -> int:
    """m-h: I-3's integer seed for one regime -- the first word of numpy's `SeedSequence` of the `h4_tests` role's
    `test` key (`I3_TEST_ID`, replicate = the regime), refused unless the role seed was issued by
    `three_way_seeds.issue` (`seed_key`'s provenance check)."""
    if not (S.is_issued(role_seed) and role_seed.role == "h4_tests"):
        raise S.ProvenanceRefused("REFUSED (m-h): I-3's uniforms come from the issued h4_tests role seed only")
    key = K.seed_key(role_seed, "test", test=I3_TEST_ID, replicate=int(regime))
    return int(K.key_state(key, 1)[0])


def _check_i3_race_vs_binarydraw() -> dict[str, Any]:
    """M-2 / I-3: firm path's zero-cost race (`three_way_redraw.race_dollars` + zero-cost `RaceOver`) matches
    Stage 2 `adapter.BinaryDraw` / `p_race` across deep (`room > risk`) and cushion-bound (`room < risk`) regimes
    on identical uniforms.

    m-h (Q-188b): the uniforms' seeds come by role, never as literals. The declaration names no seed for I-3 (its
    section 15 block has none, and section 16 item 3 says only "on the same uniforms"), and its `h4_tests` role is "the
    unit tests, H4's T-0 and H4's build (synthetic toys only; the part H4-T)" -- I-3 is a build identity on synthetic
    toys, so its uniforms are that role's `test`-kind children (`I3_TEST_ID`, one replicate a regime), each turned into
    the integer `BinaryDraw` takes by `three_way_keys.key_state` (numpy's own `SeedSequence` of the key). The identity
    must hold on any uniforms, so no result depends on which."""
    _setup_vendor()
    from extended import three_way_redraw as RD
    from propedge.contract.adapter import BinaryDraw, Policy, Rules, p_race, theta_from_edge

    n_check = 256
    regimes = (
        (500.0, 2.0, 2000.0),   # deep cushion (room > risk)
        (500.0, 2.0, 300.0),    # cushion-bound (room < risk)
        (500.0, 1.5, 120.0),    # tight cushion-bound
    )
    rules = Rules(floor_mode="truncate", edge_mode="drift")
    total_compared = 0
    diffs = 0
    role_seed = S.issue("h4_tests")

    for r_idx, (risk, rr, room) in enumerate(regimes):
        seed_i3 = i3_regime_seed(role_seed, r_idx)
        pol = Policy(rr=rr, risk=risk)
        bd = BinaryDraw(pol, edge=0.0, seed=seed_i3, rules=rules)
        cush = np.full(n_check, room, dtype=float)
        theirs = bd(n_check, 0, 0, cush)
        # Re-read the exact same uniform stream that BinaryDraw drew internally
        us = np.random.default_rng(seed_i3).random(n_check)
        win_d = risk * rr
        c_eff = min(risk, room)
        p_bd = float(p_race(c_eff, win_d, theta_from_edge(risk, win_d, 0.0)))
        p_mine = c_eff / (c_eff + win_d)
        if abs(p_bd - p_mine) > 1e-12:
            diffs += 1
        # Compare against three_way_redraw.race_outcome at zero cost
        wins_rd = RD.race_outcome(us, np.full(n_check, p_mine), 0.0)
        mine_rd = np.where(wins_rd, win_d, -c_eff)
        diffs += int(np.sum(np.abs(mine_rd - theirs) > 1e-9))
        # Also verify zero-cost RaceOver on identical uniforms via a tiny stub coin source
        stop_t = int(round(risk / 0.5))
        f0 = TB.TradeFacts(
            decision=1210, entry=1215, stop_ticks=stop_t, tick_value=0.5, kinds={rr: "t"},
            limit=1328, sigma=4.0, be_open=None, e_ticks=0.0, xt_ticks=0.0, xs_ticks=0.0, xf_ticks=0.0,
            fee_per_contract=0.0,
        )

        class _Blk0:
            entry_t = np.array([1215.0])
            exit_t = np.array([1230.0])

        class _Coins0:
            def __init__(self, u_arr):
                self._u = np.asarray(u_arr, float).reshape(-1, 1)

            def coin(self, k, kind):
                return self._u

        unit0 = TB._Unit({(0, 0): f0}, [_Blk0()], 0, _Coins0(us), J.ArmSpec())
        for lane in range(min(32, n_check)):
            class _Inner0:
                settlement = "mae"
                key = ("combine", 0)
                last_trade = {"historical_day": 0, "trade_index": 0, "realised_risk": risk, "rr": rr,
                              "contracts": 1, "risk_per_contract": risk, "fee": 0.0, "u": rr, "mae": 0.0}

                def __call__(self, n, day, slot, cushion, **kw):
                    return np.array([win_d])

            ro = TB.RaceOver(_Inner0(), unit0, lane, "race", None, None)
            ro.begin_session(room, 0.0)
            got = float(ro(1, 0, 0, np.array([room]))[0])
            if abs(got - float(theirs[lane])) > 1e-9:
                diffs += 1
        total_compared += n_check

    return {
        "identity": "I-3",
        "baseline": "all",
        "compared": total_compared,
        "differing": diffs,
        "tolerance": 1e-9,
        "holds": diffs == 0,
        "note": "firm-path race (RD + zero-cost RaceOver) vs adapter.BinaryDraw across deep & cushion-bound rooms",
    }


def _check_i5_coin_vs_p16(root: Path, p16_bundle: BaselineBundle) -> dict[str, Any]:
    """I-5: naive-coin source in P-16 mode reproduces P-16's search-year trades by `rc_dev_test.trades_hash`."""
    vroot = _setup_vendor()
    import atlas_a3 as A
    import rc_dev_test as D
    import rc_screen as RS
    import zero_edge_decomposition as zd
    from propedge.research import resolved_coin as rc

    reg = SC.load_constants(root / HA.H4_REG_CONSTANTS_REL, expected_sha256=HA.H4_REG_CONSTANTS_SHA256)
    with SC.cut(last=W42.SEARCH_LAST, root=vroot):
        I_in = RS.inputs()
        L = I_in["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        days_df = L["days"].copy()
        days_df["date"] = days_df["date"].astype(str)
        days = sorted(days_df["date"].tolist())
        day_arrs = _extract_day_arrays_search(days, cfg)
        rr_grid = A.rrs(cfg)
        keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I_in["plan"])))
        fees = A.fee_by_stop(fcfg, (CS.P16_STOP_TICKS,), tv)
        crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
        coins = rc.coin_table(days, rc.marks())
        cut_slot = CS.BLS_CUT_SLOT
        clear_slot = CS.RELEASE_CLEAR_SLOT

    t_i5 = CS.build_p16_i5_trades(
        days_df,
        lambda d: day_arrs[d],
        reg["p16"]["offered_marks"],
        coins,
        fee_micro_eq=float(fees[CS.P16_STOP_TICKS]),
        tick=float(cfg["contract"]["tick"]),
        tick_value=tv,
        entry_ticks=float(cfg["slip_ticks"]),
        stop_ticks=CS.P16_STOP_TICKS,
        rr_grid=rr_grid,
        fresh_rr=crr,
        bls_cut=cut_slot,
        release_clear=clear_slot,
    )
    t_i5_pad = zd.pad(t_i5, keys)
    h_i5 = D.trades_hash(t_i5_pad)
    want_h = str(reg["p16"]["search_trades_sha256"])
    holds = (h_i5 == want_h) and (len(t_i5_pad) == int(reg["p16"]["search_trades"]))
    return {
        "identity": "I-5",
        "baseline": "naive_coin_vs_p16",
        "compared": int(len(t_i5_pad)),
        "differing": 0 if holds else 1,
        "tolerance": 0.0,
        "holds": bool(holds),
        "note": f"coin_p16_hash={h_i5[:16]} vs p16_reg={want_h[:16]} (n={len(t_i5_pad)} vs {reg['p16']['search_trades']})",
    }


def _same_value(a: Any, b: Any) -> bool:
    """Exact equality of two field values (arrays element for element, NaN equal to NaN; dicts by float key; tuples
    and lists element for element; floats bit for bit up to NaN)."""
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, Mapping) or isinstance(b, Mapping):
        if not (isinstance(a, Mapping) and isinstance(b, Mapping)):
            return False
        ka = {float(k): v for k, v in a.items()}
        kb = {float(k): v for k, v in b.items()}
        return set(ka) == set(kb) and all(_same_value(ka[k], kb[k]) for k in ka)
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        xa, xb = np.asarray(a), np.asarray(b)
        if xa.shape != xb.shape:
            return False
        if xa.dtype.kind in "fc" or xb.dtype.kind in "fc":
            try:
                return bool(np.array_equal(xa.astype(float), xb.astype(float), equal_nan=True))
            except (TypeError, ValueError):
                return False
        return bool(np.array_equal(xa, xb))
    if isinstance(a, (tuple, list)) or isinstance(b, (tuple, list)):
        if not (isinstance(a, (tuple, list)) and isinstance(b, (tuple, list))) or len(a) != len(b):
            return False
        return all(_same_value(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return bool(a == b)


def _record_fields(x: Any) -> list[str]:
    import dataclasses as _dc

    if _dc.is_dataclass(x):
        return [f.name for f in _dc.fields(x)]
    return sorted(k for k in vars(x) if not k.startswith("_"))


def dayblock_differences(a: Any, b: Any) -> list[str]:
    """m-g (Q-188b): the names of every DayBlock field on which two blocks differ -- every field of the vendored
    `DayBlock` (pnl, risked, exit_reasons, risk_per_contract, mae, entry_t, exit_t, r_by_rr, mae_by_rr, markets, fee,
    sides, exit_by_rr, ...), never only pnl, entry_t and r_by_rr."""
    names = sorted(set(_record_fields(a)) | set(_record_fields(b)))
    return [n for n in names if not _same_value(getattr(a, n, None), getattr(b, n, None))]


def _same_dayblock(a: Any, b: Any) -> bool:
    return not dayblock_differences(a, b)


def facts_differences(a: TB.TradeFacts, b: TB.TradeFacts) -> list[str]:
    """The `TradeFacts` fields on which two trades' facts differ (every field: sigma, limit, the move bars, costs, the
    historical and mirror gross at every R, ...)."""
    return dayblock_differences(a, b)


def nested_cut_differences(full: BaselineBundle, sub: BaselineBundle) -> dict[str, Any]:
    """I-2's comparison, one nested cut (section 4; F-2, F-3, F-10, m-g; Q-188b): `sub` built on a cut ending before
    `full`'s must equal `full` day for day on every day it holds -- **the raw DayBlocks** (every field), **the schedule
    the firm path consumes** (the kept trades after the sigma drop, row for row and column for column; the kept
    DayBlocks, every field) and **the trades' facts** (`TradeFacts`, every field: sigma, limit, move bars, costs,
    historical and mirror gross). Returns the days compared, the days differing on any part, and each part's count."""
    n_sub = len(sub.dates)
    out: dict[str, Any] = {"days": n_sub, "differing_days": 0,
                           "by_part": {"dates": 0, "raw_blocks": 0, "blocks": 0, "trades": 0, "facts": 0},
                           "fields": {}}
    if list(sub.dates) != list(full.dates[:n_sub]):
        out["by_part"]["dates"] = n_sub
        out["differing_days"] = n_sub
        return out
    bad_days: set[int] = set()

    def _note_fields(names: Sequence[str]) -> None:
        for nm in names:
            out["fields"][nm] = out["fields"].get(nm, 0) + 1

    full_raw = full.raw_blocks if full.raw_blocks is not None else full.blocks
    sub_raw = sub.raw_blocks if sub.raw_blocks is not None else sub.blocks
    for part, fb, sb in (("raw_blocks", full_raw, sub_raw), ("blocks", full.blocks, sub.blocks)):
        if len(sb) != n_sub or len(fb) < n_sub:
            out["by_part"][part] = n_sub
            bad_days.update(range(n_sub))
            continue
        for i in range(n_sub):
            dif = dayblock_differences(sb[i], fb[i])
            if dif:
                out["by_part"][part] += 1
                bad_days.add(i)
                _note_fields([f"{part}.{d}" for d in dif])

    last = str(sub.dates[-1]) if n_sub else ""
    ft = full.trades[full.trades["date"].astype(str) <= last] if len(full.trades) else full.trades
    st = sub.trades
    d_idx = {str(d): i for i, d in enumerate(sub.dates)}
    if list(ft.columns) != list(st.columns):
        out["by_part"]["trades"] = n_sub
        bad_days.update(range(n_sub))
    else:
        f_by = {str(d): g.reset_index(drop=True) for d, g in ft.groupby(ft["date"].astype(str), sort=False)} if len(ft) else {}
        s_by = {str(d): g.reset_index(drop=True) for d, g in st.groupby(st["date"].astype(str), sort=False)} if len(st) else {}
        for d in sorted(set(f_by) | set(s_by)):
            a, b = f_by.get(d), s_by.get(d)
            if a is None or b is None or not a.equals(b):
                out["by_part"]["trades"] += 1
                bad_days.add(d_idx.get(d, -1))

    fk = {k for k in full.facts if int(k[0]) < n_sub}
    sk = set(sub.facts)
    for k in sorted(fk | sk):
        if k not in full.facts or k not in sub.facts:
            out["by_part"]["facts"] += 1
            bad_days.add(int(k[0]))
            continue
        dif = facts_differences(sub.facts[k], full.facts[k])
        if dif:
            out["by_part"]["facts"] += 1
            bad_days.add(int(k[0]))
            _note_fields([f"facts.{d}" for d in dif])
    out["differing_days"] = len(bad_days)
    return out


def _i2_rows(bname: str, cut_d: str, cmp: Mapping[str, Any], mode: str) -> list[dict[str, Any]]:
    """Two rows a (cut, baseline): `I-2@cut` (the raw DayBlocks, every field: the form E-288 recorded, widened by m-g)
    and `I-2s@cut` (the schedule consumed: kept trades, facts and kept DayBlocks; F-3, F-10)."""
    bp = cmp["by_part"]
    raw_bad = int(bp["dates"]) + int(bp["raw_blocks"])
    sched_bad = int(cmp["differing_days"])
    fields = ",".join(f"{k}={v}" for k, v in sorted(cmp["fields"].items())) or "none"
    return [
        {"identity": f"I-2@{cut_d}", "baseline": bname, "compared": int(cmp["days"]), "differing": raw_bad,
         "tolerance": 0.0, "holds": raw_bad == 0,
         "note": f"nested cut {cut_d} vs {W42.SEARCH_LAST} ({cmp['days']} days, raw DayBlocks, every field; {mode})"},
        {"identity": f"I-2s@{cut_d}", "baseline": bname, "compared": int(cmp["days"]), "differing": sched_bad,
         "tolerance": 0.0, "holds": sched_bad == 0,
         "note": (f"nested cut {cut_d} vs {W42.SEARCH_LAST}: the schedule consumed (kept trades, facts, kept DayBlocks; "
                  f"{mode}); days differing by part {dict(bp)}; fields {fields}")},
    ]


def _check_i2_nested_cuts(
    bundles_full: Mapping[str, BaselineBundle],
    root: Path,
    *,
    baselines: Sequence[str] = REGISTERED,
    builder: Any = None,
) -> list[dict[str, Any]]:
    """M-3 / I-2 (section 4 & 16): every baseline's schedule built on the nested cuts 2022-12-30, 2023-06-30 and
    2023-09-29 must equal 2023-12-29's on every day it holds (`nested_cut_differences`). The registered baselines are
    rebuilt **with their facts** (the sigma drop included, so the schedule H4-B consumes is checked, F-3/F-10); the naive
    coin **in its run mode** (L = 5, the clock grid, the void calendar, its own sigma and schedule side; F-2) by
    `build_naive_coin_bundle`. `builder(bname, last_day)` replaces the builders (the synthetic tests)."""
    rows: list[dict[str, Any]] = []

    def _build(bname: str, last_day: str) -> BaselineBundle:
        if builder is not None:
            return builder(bname, last_day)
        if bname == "naive_coin":
            return build_naive_coin_bundle(last_day=last_day, root=root)
        return build_registered_bundle(bname, last_day=last_day, verify_i1=False, with_facts=True, root=root)

    for cut_d in HA.H4_NESTED_CUTS:
        for bname in baselines:
            full = bundles_full[bname]
            sub = _build(bname, cut_d)
            mode = "run mode (L=5, clock grid, void calendar, own sigma)" if bname == "naive_coin" else "with facts"
            rows.extend(_i2_rows(bname, cut_d, nested_cut_differences(full, sub), mode))
            del sub
            gc.collect()
    return rows


def _load_nq_stop_band(root: Path) -> dict[str, float]:
    """M-8: load NQ's declared narrow/wide/cost-floor stop bands from `vendor/stage2/results/stop_band.csv`."""
    stop_band_path = root / "vendor" / "stage2" / "results" / "stop_band.csv"
    if not stop_band_path.is_file():
        raise HA.H4AuditRefused(f"missing stop_band.csv at {stop_band_path}")
    sb = pd.read_csv(stop_band_path)
    nq = sb[sb["market"].astype(str) == "NQ"]
    if nq.empty:
        raise HA.H4AuditRefused("stop_band.csv contains no market == 'NQ' rows")
    comb = nq[nq["state"].astype(str) == "combine"].iloc[0]
    fb = nq[nq["state"].astype(str) == "funded_below_2000"].iloc[0]
    fa = nq[nq["state"].astype(str) == "funded_at_or_above_2000"].iloc[0]
    return {
        "combine_lo": float(comb["narrow_ticks"]),
        "combine_hi": float(comb["wide_ticks"]),
        "funded_below_2000_lo": float(fb["narrow_ticks"]),
        "funded_below_2000_hi": float(fb["wide_ticks"]),
        "funded_ge_2000_lo": float(fa["narrow_ticks"]),
        "funded_ge_2000_hi": float(fa["wide_ticks"]),
        "cost_drag_floor_ticks": float(comb["cost_drag_floor_ticks"]),
    }


def _realised_risk_gate(sub: pd.DataFrame, bundle: BaselineBundle) -> tuple[float, bool]:
    """m-6: D-212 realised-risk gate (realised risk within 10% of intended risk on >= 90% of trades) evaluated at
    each baseline's stop distribution under its fresh Combine sizing rule (`resolved_coin.width_sizing`).

    m-f (Q-188b): a gate never passes on missing input -- a job without its sizing rule or protocol is REFUSED
    (`H4AuditRefused`), and a scope with no trades does not pass (share NaN, `False`; the supply gate labels it)."""
    if sub.empty:
        return float("nan"), False
    draws = bundle.args.get("draws", {}) if isinstance(bundle.args, Mapping) else {}
    srule = draws.get("sizing") if isinstance(draws, Mapping) else None
    proto = draws.get("protocol") if isinstance(draws, Mapping) else None
    if srule is None or proto is None:
        raise HA.H4AuditRefused(
            f"REFUSED (m-f): {bundle.name}'s realised-risk gate needs the job's sizing rule and protocol "
            f"(draws.sizing={srule is not None}, draws.protocol={proto is not None}); a gate never passes on missing input"
        )
    _setup_vendor()
    from propedge.research import resolved_coin as rc

    stops_vc = sub["S"].astype(int).value_counts()
    leaves = [("combine", "fresh", float(proto.combine_risk), float(proto.combine_rr))]
    ws = rc.width_sizing(srule, leaves, sorted(stops_vc.index.tolist()), tick_value=0.5)
    ok_by_stop = {
        int(r["stop_ticks"]): bool(
            (not bool(r["cannot_size"])) and (abs(float(r["realised_share"]) - 1.0) <= 0.10 + 1e-9)
        )
        for _, r in ws.iterrows()
    }
    n_ok = sum(int(cnt) for st, cnt in stops_vc.items() if ok_by_stop.get(int(st), False))
    share = float(n_ok) / float(len(sub))
    return share, bool(share >= 0.90 - 1e-12)


def _scope_count(dates: Sequence[str], scope: str) -> int:
    """F-6 (Q-188b): how many of the dated records fall in `scope` ("all", or a calendar year "YYYY") -- a year's beside
    count computed from the records, never a typed zero."""
    if scope == "all":
        return int(len(dates))
    return int(sum(1 for d in dates if str(d)[:4] == str(scope)))


#: F-8 (Q-188b): each H4-S gate's label, written beside its counts in `h4_supply.csv` (section 11: "a comparator failing
#: one kept and labelled"; section 3's rows for the band and the resolution). No colon and no dollar figure in a
#: label: the results' price-level and timestamp scans read every cell.
GATE_LABELS: dict[str, str] = {
    "resolution": "fails the resolution gate (over 5 pct of trades at the session flatten at some R) - kept and "
                  "labelled, never dropped",
    "realised_risk": "fails the realised-risk gate (under 90 pct of trades within 10 pct) - kept and labelled",
    "no_trades": "no trades in this scope - the supply gate fails here",
    "stop_band": "trades outside the Combine stop band (stop_band.csv state combine, the trades' own S column) - "
                 "counted beside",
    "funded_band": "trades outside the funded_below_2000 stop band (the trades' own S column) - counted beside",
    "cost_floor": "trades below the cost-drag floor - counted beside",
    "sigma_zero": "alerts with zero dispersion behind them dropped (sigma 0, not a declared drop, F-3) - counted beside",
}


def supply_gate_labels(row: Mapping[str, Any]) -> str:
    """F-8: the labels of every gate a supply row fails or counts beside, `;`-joined (blank when none)."""
    out: list[str] = []
    if int(row.get("trades", 0)) == 0:
        out.append(GATE_LABELS["no_trades"])
    if int(row.get("trades", 0)) > 0 and not bool(row.get("resolves_5pct", True)):
        out.append(GATE_LABELS["resolution"])
    if int(row.get("trades", 0)) > 0 and not bool(row.get("passes_realised_risk_90pct", False)):
        out.append(GATE_LABELS["realised_risk"])
    if int(row.get("outside_stop_band", 0)) > 0:
        out.append(GATE_LABELS["stop_band"])
    if int(row.get("outside_funded_below_2000_band", 0)) > 0:
        out.append(GATE_LABELS["funded_band"])
    if int(row.get("below_cost_drag_floor", 0)) > 0:
        out.append(GATE_LABELS["cost_floor"])
    if int(row.get("dropped_sigma_zero", 0)) > 0:
        out.append(GATE_LABELS["sigma_zero"])
    return "; ".join(out)


#: F-13 (Q-188b): the thread settings every H4 manifest records (the process's own environment at the write)
THREAD_ENV_KEYS: tuple[str, ...] = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")


def thread_env() -> dict[str, str | None]:
    """F-13: the BLAS/OpenMP thread variables as this process sees them (None where unset)."""
    return {k: os.environ.get(k) for k in THREAD_ENV_KEYS}


def run_h4_s(*, root: Path = ROOT, results_dir: Path | None = None) -> dict[str, Any]:
    """H4-S (sections 5, 11, 16): build all 4 search-year schedules, verify I-1, I-2, I-3, I-5, count supply/gates,
    and write `results/h4_supply.csv` and `results/h4_identities.csv`."""
    from extended import RESULTS_DIR
    from extended import results as RES

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=False)

    # M-8: filter stop_band.csv on market == "NQ" and read narrow_ticks / wide_ticks / cost_drag_floor_ticks
    nq_band = _load_nq_stop_band(root)

    bundles: dict[str, BaselineBundle] = {}
    ident_rows: list[dict[str, Any]] = []
    for bname in BASELINES:
        b = build_bundle(bname, last_day=W42.SEARCH_LAST, root=root)
        bundles[bname] = b
        if bname in REGISTERED:
            ident_rows.append(
                {
                    "identity": "I-1",
                    "baseline": bname,
                    "compared": int(b.meta["raw_trades"]),
                    "differing": 0,
                    "tolerance": 0.0,
                    "holds": True,
                    "note": f"search_trades_sha256={b.trades_sha256}",
                }
            )

    # I-2 on every baseline: the registered three with their facts (the schedule consumed, F-3/F-10) and the naive
    # coin in its run mode (F-2, Q-188b)
    ident_rows.extend(_check_i2_nested_cuts(bundles, root, baselines=(*REGISTERED, "naive_coin")))
    ident_rows.append(_check_i3_race_vs_binarydraw())
    ident_rows.append(_check_i5_coin_vs_p16(root, bundles["p16"]))

    failed = [r for r in ident_rows if not r["holds"]]
    if failed:
        raise HA.H4AuditRefused(f"REFUSED (H4-S kill): identity check(s) failed: {failed}")

    # Supply, resolution, realised-risk, breakeven, same-bar, schedule-overlap, coverage (38), idle (39)
    supply_rows: list[dict[str, Any]] = []
    windows_38 = {"asia": (60.0, 540.0), "london": (540.0, 930.0), "us": (930.0, 1330.0)}
    for bname in BASELINES:
        b = bundles[bname]
        t = b.trades
        rr_cols = [float(c[2:]) for c in t.columns if c.startswith("o_")]
        date_to_yr = {d: int(d[:4]) for d in b.dates}
        years = sorted(set(date_to_yr.values()))
        for scope in ("all", *[str(y) for y in years]):
            if scope == "all":
                sub = t
                n_days = len(b.dates)
                sub_dates = list(b.dates)
            else:
                yr = int(scope)
                sub = t[t["year"].astype(int) == yr]
                sub_dates = [d for d in b.dates if date_to_yr[d] == yr]
                n_days = len(sub_dates)
            n_tr = int(len(sub))
            flat_shares: list[float] = []
            be_shares: list[float] = []
            same_bar_shares: list[float] = []
            for R_v in rr_cols:
                oc = f"o_{R_v:g}"
                ec = f"exit_t_{R_v:g}"
                if n_tr and oc in sub.columns:
                    # M-8: exclude unoffered blank/NaN R entries (e.g. P-14) from the denominator
                    valid_o = sub[oc].notna() & (sub[oc].astype(str).str.strip() != "")
                    if valid_o.any():
                        vals_o = sub.loc[valid_o, oc].astype(str)
                        flat_shares.append(float((vals_o == "f").mean()))
                        be_shares.append(float((vals_o == "b").mean()))
                        if ec in sub.columns:
                            ex_v = pd.to_numeric(sub.loc[valid_o, ec], errors="coerce")
                            en_v = pd.to_numeric(sub.loc[valid_o, "entry_t"], errors="coerce")
                            same_bar_shares.append(float((ex_v == en_v).mean()))
            s_vals = sub["S"].astype(float) if n_tr else pd.Series(dtype=float)
            out_comb = int(((s_vals < nq_band["combine_lo"]) | (s_vals > nq_band["combine_hi"])).sum()) if n_tr else 0
            out_fb = int(((s_vals < nq_band["funded_below_2000_lo"]) | (s_vals > nq_band["funded_below_2000_hi"])).sum()) if n_tr else 0
            below_floor = int((s_vals < nq_band["cost_drag_floor_ticks"]).sum()) if n_tr else 0
            rr_share, rr_pass = _realised_risk_gate(sub, b)
            # Multi-trade moments (F4-14)
            multi_m = int((sub.groupby(["date", "decision_slot_minutes"]).size() >= 2).sum()) if n_tr else 0
            # Coverage (38) and idle (39) on offered schedules
            by_d = {d: g for d, g in sub.groupby("date", sort=False)} if n_tr else {}
            days_for_38 = [
                {
                    "accounts": 1,
                    "taken": tuple(
                        (float(r_e), float(r_x))
                        for r_e, r_x in zip(by_d[d]["entry_t"], by_d[d]["exit_t"])
                    )
                    if d in by_d
                    else (),
                    "offered": tuple(float(r_e) for r_e in by_d[d]["entry_t"]) if d in by_d else (),
                }
                for d in sub_dates
            ]
            cov = JM.coverage(days_for_38, windows_38)
            idl = JM.idle(days_for_38, 1330.0)
            supply_rows.append(
                {
                    "baseline": bname,
                    "year": scope,
                    "sessions": n_days,
                    "trades": n_tr,
                    "trades_per_session": float(n_tr / n_days) if n_days else float("nan"),
                    "max_flatten_share_across_R": float(max(flat_shares)) if flat_shares else float("nan"),
                    "resolves_5pct": bool(max(flat_shares) <= 0.05 + 1e-12) if flat_shares else True,
                    "realised_risk_within_10pct_share": rr_share,
                    "passes_realised_risk_90pct": rr_pass,
                    "mean_be_share_across_R": float(np.mean(be_shares)) if be_shares else float("nan"),
                    "max_be_share_across_R": float(max(be_shares)) if be_shares else float("nan"),
                    "mean_same_bar_share": float(np.mean(same_bar_shares)) if same_bar_shares else float("nan"),
                    "outside_stop_band": out_comb,
                    "outside_funded_below_2000_band": out_fb,
                    "below_cost_drag_floor": below_floor,
                    "multi_trade_moments": multi_m,
                    "schedule_overlaps_beside": _schedule_overlap_count(sub, rr_cols),
                    # F-6 (Q-188b): every year's beside count computed from the dated records, never a typed 0
                    "dropped_sigma_lt_2": _scope_count(
                        [r["date"] for r in b.meta.get("dropped_sigma_rows", []) if r["reason"] == CS.SIGMA_LT_2], scope
                    ),
                    "dropped_sigma_zero": _scope_count(
                        [r["date"] for r in b.meta.get("dropped_sigma_rows", []) if r["reason"] == CS.SIGMA_ZERO], scope
                    ),
                    "limit_differs_from_last_bar": _scope_count(b.meta.get("limit_differs_dates", []), scope),
                    "days_data_defect_lookahead": _scope_count(b.meta.get("data_defect_lookahead_dates", []), scope),
                    "cov_offered_asia": cov["offered_asia"],
                    "cov_offered_london": cov["offered_london"],
                    "cov_offered_us": cov["offered_us"],
                    "no_signal_idle_median": idl["no_signal_median"],
                    "no_signal_idle_max": idl["no_signal_max"],
                }
            )
    # F-8 (Q-188b): a comparator failing a gate is kept and labelled (section 11), the label beside its counts
    for row_s in supply_rows:
        row_s["gate_labels"] = supply_gate_labels(row_s)

    sched_hashes = {bname: bundles[bname].trades_sha256 for bname in BASELINES}
    params = {
        "part": "H4-S",
        "seed_roles": ["h4s_schedule_side", "h4_tests (I-3's synthetic uniforms only, part H4-T; m-h)"],
        "schedules_sha256": sched_hashes,
        # F-3 (Q-188b): the schedule H4-B consumes (after the sigma drop), its count and hash beside the registered one
        "kept_schedules_sha256": {bname: bundles[bname].meta.get("kept_trades_sha256") for bname in BASELINES},
        "kept_trades": {bname: bundles[bname].meta.get("kept_trades") for bname in BASELINES},
        "dropped_sigma": {bname: {"lt_2_changes": int(bundles[bname].meta.get("dropped_sigma_lt_2", 0)),
                                  "zero_dispersion": int(bundles[bname].meta.get("dropped_sigma_zero", 0)),
                                  "rms_fallback": int(bundles[bname].meta.get("sigma_rms_fallback", 0))}
                          for bname in BASELINES},
        # F-9 (Q-188b): each schedule's cut summary (the last day, the files read and cut, what was passed through)
        "cut": {bname: bundles[bname].meta.get("cut") for bname in BASELINES},
        "nq_stop_band": nq_band,
        "preconditions": pre,
        "nested_cuts": list(HA.H4_NESTED_CUTS),
        "coin_counts": bundles["naive_coin"].meta.get("coin_counts", {}),
        "threads": thread_env(),
    }
    sup_p, _ = RES.write_result(
        pd.DataFrame(supply_rows),
        "h4_supply",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description="H4-S search-year schedule supply, resolution, breakeven, same-bar, overlap, coverage (38), and idle (39) counts.",
    )
    id_p, _ = RES.write_result(
        pd.DataFrame(ident_rows),
        "h4_identities",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description="H4-S pre-outcome identities I-1 (search sub-hashes), I-2 (nested cuts), I-3 (race vs BinaryDraw), and I-5 (coin source vs P-16).",
    )
    return {"supply_csv": str(sup_p), "identities_csv": str(id_p), "schedules_sha256": sched_hashes}


# --------------------------------------------------------------------------------------------- H4-S checks (Q-188b)


def run_h4_s_checks(
    baselines: Sequence[str] = BASELINES,
    *,
    nested: bool = True,
    tag: str = "",
    root: Path = ROOT,
    results_dir: Path | None = None,
) -> dict[str, Any]:
    """Q-188b's heavy checks, one slot (F-2, F-3, F-10): for each of `baselines`, its search-year schedule as H4-B
    builds it, then (`nested`) I-2 on the three nested cuts -- the registered baselines with their facts (the schedule
    consumed), the naive coin in its run mode -- and every alert its volatility dropped (date, alert minute, reason, the
    bars, changes and non-zero changes behind it; never a price). Writes `results/h4_sigma_drops[_tag].csv` and, with
    `nested`, `results/h4_identities_i2[_tag].csv`. One bundle held at a time (memory)."""
    from extended import RESULTS_DIR
    from extended import results as RES

    bad = [b for b in baselines if b not in BASELINES]
    if bad or not baselines:
        raise ValueError(f"baselines must be among {BASELINES}, got {list(baselines)}")
    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=False)
    drop_rows: list[dict[str, Any]] = []
    ident_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    t0 = time.perf_counter()
    for bname in baselines:
        b = build_bundle(bname, last_day=W42.SEARCH_LAST, root=root)
        for r in b.meta.get("dropped_sigma_rows", []):
            drop_rows.append({"baseline": bname, **r})
        summary[bname] = {
            "schedule_sha256": b.trades_sha256,
            "kept_trades": b.meta.get("kept_trades"),
            "kept_trades_sha256": b.meta.get("kept_trades_sha256"),
            "dropped_sigma_lt_2": int(b.meta.get("dropped_sigma_lt_2", 0)),
            "dropped_sigma_zero": int(b.meta.get("dropped_sigma_zero", 0)),
            "sigma_rms_fallback": int(b.meta.get("sigma_rms_fallback", 0)),
            "cut": b.meta.get("cut"),
        }
        if nested:
            ident_rows.extend(_check_i2_nested_cuts({bname: b}, root, baselines=(bname,)))
        print(f"  [H4-S checks] {bname}: {len(b.meta.get('dropped_sigma_rows', []))} dropped alerts, "
              f"{time.perf_counter() - t0:.0f}s", flush=True)
        del b
        gc.collect()
    suf = f"_{tag}" if tag else ""
    params = {
        "part": f"H4-S-checks{suf}",
        "baselines": list(baselines),
        "nested_cuts": list(HA.H4_NESTED_CUTS) if nested else [],
        "summary": summary,
        "sigma_reasons": list(CS.SIGMA_REASONS),
        "seed_roles": ["h4s_schedule_side"] if "naive_coin" in baselines else [],
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "peak_wset_mb": round(_peak_mb(), 1),
        "preconditions": pre,
        "threads": thread_env(),
    }
    # `sessions_read` stays out of the file: 100 x n_bars / sessions_read (60 / 1) lands on the price-level guard's band
    # and grid, a false "level" pair; the manifest's rows are the dates and minutes alone
    cols = ["baseline", "date", "decision_slot_minutes", "decision_ct", "reason", "n_bars", "n_changes",
            "n_nonzero_changes"]
    d_p, _ = RES.write_result(
        pd.DataFrame(drop_rows, columns=cols), f"h4_sigma_drops{suf}", script=SCRIPT, seed=None, require_seed=False,
        exploratory=False, prereg_id="H4", results_dir=rdir, parameters=params,
        description="Q-188b F-3: every search-year alert whose F4-1 volatility was refused -- its date, alert minute and "
                    "reason (fewer than two changes, or zero dispersion), with the counts behind it; no price.",
    )
    out = {"sigma_drops_csv": str(d_p), "summary": summary}
    if nested:
        i_p, _ = RES.write_result(
            pd.DataFrame(ident_rows), f"h4_identities_i2{suf}", script=SCRIPT, seed=None, require_seed=False,
            exploratory=False, prereg_id="H4", results_dir=rdir, parameters=params,
            description="Q-188b F-2/F-10/m-g: I-2 on the nested cuts for every baseline named -- raw DayBlocks (every "
                        "field) and the schedule consumed (kept trades, facts, kept DayBlocks); the naive coin in run mode.",
        )
        out["identities_csv"] = str(i_p)
        out["failed"] = [r for r in ident_rows if not r["holds"]]
    return out


# --------------------------------------------------------------------------------------------- H4-A: as-traded replays


def run_h4_a(
    *,
    workers: int = 2,
    root: Path = ROOT,
    results_dir: Path | None = None,
    require_h4_0: bool = True,
) -> dict[str, Any]:
    """H4-A (sections 11 & 16): as-traded point-arm replays of P-14, P-15, P-16 via `user_beside.run_starts`,
    built through `search_cut.pass_through`, verifying H4-0's sealed hash and identity I-4."""
    from extended import RESULTS_DIR
    from extended import journey_readings as JR
    from extended import results as RES
    from extended import user_beside as UB

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=False)
    w = max(1, min(int(workers), MAX_WORKERS))

    # m-3: require h4_0_probe.csv in production H4-A
    h40_path = rdir / "h4_0_probe.csv"
    want_h40_sha: str | None = None
    if h40_path.is_file():
        want_h40_sha = str(pd.read_csv(h40_path).iloc[0]["sealed_p14_first21_sha256"])
    elif require_h4_0:
        raise HA.H4AuditRefused(f"REFUSED (m-3): H4-A requires H4-0 output {h40_path} for sealed hash check")

    all_rows: list[dict[str, Any]] = []
    i4_rows: list[dict[str, Any]] = []
    h40_matched: bool | None = None

    for design in REGISTERED:
        bundle = build_registered_bundle(design, verify_i1=True, with_facts=False, root=root)
        HA.check_job_ends_search_window(bundle.dates, f"H4-A {design}")
        job = {
            "engine": "single",
            "blocks": bundle.blocks,
            "dates": list(bundle.dates),
            "args": bundle.args,
            "sub": float(bundle.args["path"]["subscription"]),
        }
        starts_all = list(range(len(bundle.dates)))
        outs = UB.run_starts(
            design, "point", UB.BY_NAME["off"], job, starts_all, workers=w, journey=True, journey_block="search"
        )

        # Verify H4-0 sealed hash on P-14's first 21 starts
        if design == "p14" and want_h40_sha is not None:
            got_payload = json.dumps(
                [
                    {
                        "start_day": int(o["rec"]["start_day"]),
                        "start_date": str(o["rec"]["start_date"]),
                        "observed": int(o["rec"]["observed"]),
                        "first_pass": o["rec"]["first_pass"],
                        "first_payout": o["rec"]["first_payout"],
                        "rel": [round(float(v), 9) for v in o["journey"]["rel"]],
                        "differs": list(o["differs"]),
                    }
                    for o in outs[:EXACT_EVERY]
                ],
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            got_sha = hashlib.sha256(got_payload).hexdigest()
            if got_sha != want_h40_sha:
                raise HA.H4AuditRefused(f"REFUSED (H4-A): P-14 first 21 starts hash {got_sha} != H4-0 sealed {want_h40_sha}")
            h40_matched = True

        # I-4 (m-3): verify three_way_baseline.replay(..., outcome="vendored") matches H4-A start-for-start
        # on rel (<= 1e-6) AND event days (first_pass, first_pay, pass_days, pay_days)!
        from extended import three_way_firm as TF

        i4_diffs = 0
        bankroll = float(bundle.args["path"]["initial_bankroll"])
        lag = int(bundle.args["path"]["payout_lag_days"])
        for s_idx, o in enumerate(outs):
            obs = int(o["rec"]["observed"])
            lp = TB.replay(bundle.blocks[s_idx : s_idx + obs], bundle.args, obs, outcome="vendored")
            rec_tb = TF.records_of(lp, bankroll=bankroll, lag=lag, horizon=obs, budget=None)
            rel_tb = np.asarray(rec_tb["rel"], float)
            rel_ub = np.asarray(o["journey"]["rel"], float)
            fp_tb = int(rec_tb["first_pass"]) if int(rec_tb["first_pass"]) > 0 else None
            fy_tb = int(rec_tb["first_pay"]) if int(rec_tb["first_pay"]) > 0 else None
            fp_ub = None if (o["rec"]["first_pass"] is None or (isinstance(o["rec"]["first_pass"], float) and math.isnan(o["rec"]["first_pass"]))) else int(o["rec"]["first_pass"])
            fy_ub = None if (o["rec"]["first_payout"] is None or (isinstance(o["rec"]["first_payout"], float) and math.isnan(o["rec"]["first_payout"]))) else int(o["rec"]["first_payout"])
            pass_days_tb = sorted(int(c.resolved_on) for c in lp.combines if getattr(c, "passed", False) and c.resolved_on is not None and int(c.resolved_on) <= obs)
            pass_days_ub = sorted(int(a["activation_day"]) for a in o["journey"]["accounts"] if int(a["activation_day"]) <= obs)
            pay_days_tb = sorted(int(d) for d, _ in rec_tb["arrivals"] if int(d) <= obs)
            pay_days_ub = sorted(int(d) for a in o["journey"]["accounts"] for d in a["arrivals"] if int(d) <= obs)
            if (
                rel_tb.shape != rel_ub.shape
                or float(np.max(np.abs(rel_tb - rel_ub))) > 1e-6
                or fp_tb != fp_ub
                or fy_tb != fy_ub
                or pass_days_tb != pass_days_ub
                or pay_days_tb != pay_days_ub
            ):
                i4_diffs += 1
        if i4_diffs > 0:
            raise HA.H4AuditRefused(f"REFUSED (I-4): {design} vendored replay differed from H4-A on {i4_diffs} start(s)")
        i4_rows.append(
            {
                "identity": "I-4",
                "baseline": design,
                "compared": len(outs),
                "differing": i4_diffs,
                "tolerance": 1e-6,
                "holds": True,
                "note": "three_way_baseline vendored vs user_beside.run_starts point off search block (rel + event days)",
            }
        )

        rows, _ = JR.summary(design, "point", UB.BY_NAME["off"], outs, blocks=("search",))
        for r in rows:
            all_rows.append(
                {
                    **r,
                    "comparator_label": "whole-window-derived registered comparator",
                    "reading_kind": "as_traded",
                }
            )

    params = {
        "part": "H4-A",
        "designs": list(REGISTERED),
        "arm": "point",
        "response": "off",
        "h4_0_sealed_hash_matched": h40_matched,
        "i4_identities": i4_rows,
        "preconditions": pre,
        "threads": thread_env(),  # F-13 (Q-188b)
    }
    csv_p, man_p = RES.write_result(
        pd.DataFrame(all_rows),
        "h4_as_traded",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description="H4-A as-traded point-arm search-year replays of P-14, P-15, and P-16 (whole-window-derived registered comparators; I-4 verified).",
    )
    return {"csv": str(csv_p), "manifest": str(man_p), "i4": i4_rows, "h4_0_matched": h40_matched}


# --------------------------------------------------------------------------------------------- H4-B: seed-paired baseline runs

_WORKER_CTX: dict[str, Any] = {}


def _init_h4b_worker(ctx: dict[str, Any]) -> None:
    _setup_vendor()
    _WORKER_CTX.clear()
    _WORKER_CTX.update(ctx)


def _format_sampled_trade_rows(
    baseline: str,
    arm_name: str,
    reading_tag: str,
    start: int,
    start_date: str,
    seed_index: int,
    dates: Sequence[str],
    blocks: Sequence[Any],
    facts: Mapping[tuple[int, int], TB.TradeFacts],
    subs: Mapping[tuple[int, int], int],
    arm_spec: J.ArmSpec,
    log_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Format one sampled unit's taken-trade log rows (ticks & times only, NO prices, NO forbidden historical fields)."""
    out_rows: list[dict[str, Any]] = []
    for r in log_rows:
        law = str(r.get("law", ""))
        if law in ("missed", "day_end"):
            continue
        i = int(r["i"])
        j = int(r["j"])
        f = facts[(i, j)]
        b = blocks[i]
        R_val = float(r["R"])
        ex_by = getattr(b, "exit_by_rr", None)
        if ex_by is not None and R_val in ex_by and math.isfinite(float(ex_by[R_val][j])):
            ex_at_R = float(ex_by[R_val][j])
        else:
            ex_at_R = float(b.exit_t[j])
        ex_latest = float(max(float(arr[j]) for arr in ex_by.values() if math.isfinite(float(arr[j])))) if ex_by else ex_at_R
        d_val = float(r["d"])
        fee_val = float(r["fee"])
        extra = float(arm_spec.worse_ticks) * d_val
        e_c = f.e_ticks * d_val + fee_val + extra
        xt_c = f.xt_ticks * d_val + extra
        xs_c = f.xs_ticks * d_val + extra
        xf_c = f.xf_ticks * d_val + extra
        acct = r.get("acct")
        ak, ai = (str(acct[0]), int(acct[1])) if isinstance(acct, tuple) and len(acct) == 2 else ("", -1)

        row: dict[str, Any] = {
            "baseline": baseline,
            "arm": arm_name,
            "reading": reading_tag,
            "start": int(start),
            "start_date": str(start_date),
            "seed_index": int(seed_index),
            "day_idx": i,
            "trade_date": str(dates[i]),
            "trade_idx": j,
            "acct_kind": ak,
            "acct_index": ai,
            "decision": int(f.decision),
            "sub": int(subs[(i, j)]),
            "underlying": str(f.underlying),
            "fill_bar": int(f.entry),
            "exit_bar_at_R": ex_at_R,
            "exit_bar_latest": ex_latest,
            "time_limit": int(f.limit),
            "be_open": "" if f.be_open is None else int(f.be_open),
            "sigma": float(f.sigma),
            "stop_ticks": int(f.stop_ticks),
            "R": R_val,
            "kind_hist": str(r.get("kind", "")),
            "G": float(r["G"]),
            "L_ticks": "" if r.get("L_ticks") is None else float(r["L_ticks"]),
            "room": float(r["room"]),
            "d": d_val,
            "fee": fee_val,
            "e_cost": e_c,
            "xt_cost": xt_c,
            "xs_cost": xs_c,
            "xf_cost": xf_c,
            "law": law,
            "exit_code": "" if r.get("exit") is None else int(r["exit"]),
            "p": "" if r.get("p") is None else float(r["p"]),
            "s1": "" if (r.get("s1") is None and r.get("s") is None) else int(r.get("s1", r.get("s"))),
            "n1": "" if (r.get("n1") is None and r.get("n") is None) else int(r.get("n1", r.get("n"))),
            "s2": "" if r.get("s2") is None else int(r["s2"]),
            "n2": "" if r.get("n2") is None else int(r["n2"]),
            "move_x": "" if (r.get("move_x") is None or not math.isfinite(float(r["move_x"]))) else float(r["move_x"]),
            "move_moved": "" if r.get("move_moved") is None else int(bool(r["move_moved"])),
            "move_G2": "" if (r.get("move_G2") is None or not math.isfinite(float(r["move_G2"]))) else float(r["move_G2"]),
            "move_down2": ""
            if (r.get("move_down2") is None or not math.isfinite(float(r["move_down2"])))
            else float(r["move_down2"]),
            "race_need": int(bool(r.get("need_hit", False))),
            "out": float(r["out"]),
            "need": "" if (r.get("need") is None or not math.isfinite(float(r["need"]))) else float(r["need"]),
            "need_logged": 1,
        }
        out_rows.append(row)
    return out_rows


def _h4b_start_chunk(starts_chunk: list[int]) -> dict[str, Any]:
    """Worker function: run all 4 arm-runs across all `J` seeds for a batch of starts."""
    ctx = _WORKER_CTX
    baseline: str = ctx["baseline"]
    dates: tuple[str, ...] = ctx["dates"]
    blocks: list[Any] = ctx["blocks"]
    args: dict[str, Any] = ctx["args"]
    facts: dict[tuple[int, int], TB.TradeFacts] = ctx["facts"]
    subs: dict[tuple[int, int], int] = ctx["subs"]
    seed_indices: tuple[int, ...] = ctx["seed_indices"]
    part_id: int = ctx["part_id"]
    seed_role: str = ctx["seed_role"]
    sample_seed_role: str = ctx["sample_seed_role"]
    sample_part_id: int = ctx["sample_part_id"]
    arms_to_run: tuple[tuple[str, str, str, J.ArmSpec, bool], ...] = ctx["arms"]
    calendar_fset: frozenset = ctx["calendar_fset"]
    latency: float = ctx["latency"]
    check_exact: bool = ctx["check_exact"]

    coin_seed = S.issue(seed_role)
    sample_seed = S.issue(sample_seed_role)
    n_sess = len(dates)

    unit_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    exact_checked = 0
    exact_differs = 0
    exact_tally = HA.new_exact_tally()
    exact_units: list[list[Any]] = []
    oracle_checked = 0
    rung_alerts_sum = 0
    guard = K.KeyGuard.sampled(starts_chunk, seed_indices)

    for s_idx in starts_chunk:
        sl = n_sess - int(s_idx)
        obs = min(JM.YEAR, sl)
        s_date = dates[s_idx]
        for arm_name, reading_tag, outcome_mode, arm_spec, exact_every_start in arms_to_run:
            rec = TB.simulate(
                blocks,
                args,
                facts,
                s_idx,
                seed_indices,
                obs,
                seed=coin_seed,
                part=part_id,
                history=0,
                block_sessions=n_sess,
                dates=dates,
                arm=arm_spec,
                guard=guard,
                outcome=outcome_mode,
                keep_paths=True,
                log=True,
                calendar=calendar_fset,
            )
            rung_alerts_sum += int(rec.rung_alerts)

            # Exact-length run verification (section 7 & 12 m-8)
            if check_exact and (exact_every_start or (int(s_idx) % EXACT_EVERY == 0)):
                for h_ex in EXACT_HORIZONS:
                    if h_ex < obs:
                        rec_ex = TB.simulate(
                            blocks,
                            args,
                            facts,
                            s_idx,
                            seed_indices,
                            h_ex,
                            seed=coin_seed,
                            part=part_id,
                            history=0,
                            block_sessions=n_sess,
                            dates=dates,
                            arm=arm_spec,
                            outcome=outcome_mode,
                            calendar=calendar_fset,
                        )
                        for j_lane in range(len(seed_indices)):
                            exact_checked += 1
                            fp_long = int(rec.first_pass[j_lane]) if 0 < int(rec.first_pass[j_lane]) <= h_ex else -1
                            fy_long = int(rec.first_pay[j_lane]) if 0 < int(rec.first_pay[j_lane]) <= h_ex else -1
                            fp_ex = int(rec_ex.first_pass[j_lane]) if 0 < int(rec_ex.first_pass[j_lane]) <= h_ex else -1
                            fy_ex = int(rec_ex.first_pay[j_lane]) if 0 < int(rec_ex.first_pay[j_lane]) <= h_ex else -1
                            # m-4: check rel[:h_ex + 1] (<= 1e-6) AND arrivals up to h_ex in addition to first_pass/first_pay
                            rel_diff = float(np.max(np.abs(rec.rel[j_lane, : h_ex + 1] - rec_ex.rel[j_lane, : h_ex + 1])))
                            arr_long = [(int(d), round(float(c), 6)) for d, c in rec.arrivals[j_lane] if int(d) <= h_ex]
                            arr_ex = [(int(d), round(float(c), 6)) for d, c in rec_ex.arrivals[j_lane] if int(d) <= h_ex]
                            if (fp_long, fy_long) != (fp_ex, fy_ex) or rel_diff > 1e-6 or arr_long != arr_ex:
                                exact_differs += 1
                        # B-2 (Q-188b): each lane's difference classified by kind, by arm and horizon, starts counted
                        kinds_h = _exact_kinds(rec, rec_ex, h_ex, len(seed_indices))
                        HA.tally_exact(exact_tally, arm_name, h_ex, kinds_h)
                        for j_lane, k_h in enumerate(kinds_h):
                            if k_h != "same":
                                exact_units.append([arm_name, int(s_idx), int(seed_indices[j_lane]), int(h_ex), k_h])

            for j_lane, c_idx in enumerate(seed_indices):
                lg = rec.logs[j_lane]
                # Enforce strict +5 min per-unit overlap count == 0 on EVERY unit & arm (RC-2 / M-1)
                t_check = [
                    {
                        "day_idx": int(r["i"]),
                        "fill_bar": int(facts[(int(r["i"]), int(r["j"]))].entry),
                        "exit_bar_at_R": float(blocks[int(r["i"])].exit_by_rr[float(r["R"])][int(r["j"])])
                        if (
                            getattr(blocks[int(r["i"])], "exit_by_rr", None) is not None
                            and float(r["R"]) in blocks[int(r["i"])].exit_by_rr
                            and math.isfinite(float(blocks[int(r["i"])].exit_by_rr[float(r["R"])][int(r["j"])]))
                        )
                        else float(blocks[int(r["i"])].exit_t[int(r["j"])]),
                        "law": r.get("law"),
                    }
                    for r in lg
                    if r.get("law") not in ("missed", "day_end")
                ]
                ov = HA.assert_zero_strict_overlaps(
                    t_check, what=f"{baseline}/{arm_name}/start={s_date}/seed={c_idx}"
                )

                beside = {
                    "move_trades": int(rec.move_trades[j_lane]),
                    "b_redrawn": int(rec.b_redrawn[j_lane]),
                    "b_historical": int(rec.b_historical[j_lane]),
                    "be_differs": int(rec.be_differs[j_lane]),
                    "be_unrecorded": int(rec.be_unrecorded[j_lane]),
                    "tb_overlaps": int(rec.overlaps[j_lane]),
                }
                urow = HA.extract_unit_measures(
                    baseline=baseline,
                    arm=arm_name,
                    reading=reading_tag,
                    start=s_idx,
                    start_date=s_date,
                    seed_index=c_idx,
                    sessions_left=sl,
                    rel=rec.rel[j_lane],
                    first_pass=int(rec.first_pass[j_lane]),
                    first_pay=int(rec.first_pay[j_lane]),
                    arrivals=rec.arrivals[j_lane],
                    path=rec.paths[j_lane],
                    log_rows=lg,
                    blocks=blocks,
                    latency=latency,
                    strict_overlaps=ov,
                    beside_counts=beside,
                    payout_lag=int(args["path"]["payout_lag_days"]),
                )
                unit_rows.append(urow)

                # Audit sample (1%, h4_sample in part H4-U): write full taken-trade log & run independent oracle!
                if HA.is_sampled_unit(s_idx, c_idx, seed=sample_seed, part=sample_part_id):
                    trows = _format_sampled_trade_rows(
                        baseline, arm_name, reading_tag, s_idx, s_date, c_idx, dates, blocks, facts, subs, arm_spec, lg
                    )
                    if outcome_mode == "race":
                        for tr in trows:
                            HA.verify_race_trade_row(
                                tr, seed=coin_seed, part=part_id, history=0,
                                allowed_R=list(facts[(int(tr["day_idx"]), int(tr["trade_idx"]))].kinds),
                                worse_ticks=float(arm_spec.worse_ticks), require_inputs=True,
                                cost_ticks=ctx.get("cost_ticks"),
                            )
                            oracle_checked += 1
                    trade_rows.extend(trows)

    return {
        "units": unit_rows,
        "trades": trade_rows,
        "exact_checked": exact_checked,
        "exact_differs": exact_differs,
        "exact_tally": exact_tally,
        "exact_units": exact_units,
        "oracle_checked": oracle_checked,
        "rung_alerts_sum": rung_alerts_sum,
        "keys_checked": guard.checked,
        # the lead's ruling (Q-188b): which process ran the batch and its peak working set when the batch ended
        "pid": int(os.getpid()),
        "peak_wset_mb": _peak_mb(),
    }


def _worker_peaks(chunks: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """Each worker process's largest reported peak working set (MB) over the batches it ran, keyed by its pid."""
    out: dict[str, float] = {}
    for ch in chunks:
        pid, mb = ch.get("pid"), ch.get("peak_wset_mb")
        if pid is None or mb is None or not math.isfinite(float(mb)):
            continue
        out[str(pid)] = round(max(out.get(str(pid), 0.0), float(mb)), 1)
    return out


def subs_of(facts: Mapping[tuple[int, int], TB.TradeFacts]) -> dict[tuple[int, int], int]:
    """Each trade's `sub` (F4-14): two trades at one moment numbered 0, 1, ... in index order (`_Unit`'s rule)."""
    subs: dict[tuple[int, int], int] = {}
    at: dict[tuple[int, int], int] = {}
    for i, j in sorted(facts):
        m = (int(i), int(facts[(i, j)].decision))
        subs[(int(i), int(j))] = at.get(m, 0)
        at[m] = at.get(m, 0) + 1
    return subs


def _exact_kinds(rec: Any, rec_ex: Any, h: int, n_lanes: int) -> list[str]:
    """B-2: each lane's `HA.classify_exact_difference` kind between the long run `rec` and the exact run `rec_ex` of
    `h` closes (records of `TB.simulate`)."""
    out: list[str] = []
    for j in range(int(n_lanes)):
        c = HA.classify_exact_difference(
            int(h),
            first_pass_long=int(rec.first_pass[j]),
            first_pay_long=int(rec.first_pay[j]),
            rel_long=rec.rel[j],
            arrivals_long=rec.arrivals[j],
            first_pass_exact=int(rec_ex.first_pass[j]),
            first_pay_exact=int(rec_ex.first_pay[j]),
            rel_exact=rec_ex.rel[j],
            arrivals_exact=rec_ex.arrivals[j],
        )
        out.append(str(c["kind"]))
    return out


def summarise_baseline_readings(
    units_df: pd.DataFrame,
    dates: Sequence[str],
    baseline: str,
) -> pd.DataFrame:
    """Compute MEASURES 1.4 coin readings, strict_quantiles 'at least' flags, variance decomposition (34),
    by-year (32), design-level (27 CVaR10, 31 funded_lifetime), and Section 12 beside summaries."""
    from extended import user_measures as UM

    rows: list[dict[str, Any]] = []
    share_after_252 = HA.share_window_sessions_after_last_cut(dates, 252)
    share_after_126 = HA.share_window_sessions_after_last_cut(dates, 126)

    # (col, horizon, is_share, bad_dir, censored_flag_col_or_None)
    per_unit_measures: tuple[tuple[str, int, bool, str, str | None], ...] = (
        ("net_month_1", 21, False, "low", None),
        ("net_month_2", 42, False, "low", None),
        ("net_month_3", 63, False, "low", None),
        ("net_month_6", 126, False, "low", None),
        ("net_month_12", 252, False, "low", None),
        ("first_pass_days", 126, False, "high", None),
        ("cash_to_first_pass", 126, False, "high", "cash_to_first_pass_censored"),
        ("evaluations_before_first_pass", 126, False, "high", "evaluations_before_first_pass_censored"),
        ("first_payout_days", 126, False, "high", None),
        ("spent_before_first_payout", 126, False, "high", "spent_before_first_payout_censored"),
        ("first_payout_size", 126, False, "low", None),
        ("break_even_days_126", 126, False, "high", None),
        ("peak_oop_126", 126, False, "high", None),
        ("longest_wait_126", 126, False, "high", "longest_wait_126_censored"),
        ("first_pass_days_252", 252, False, "high", None),
        ("cash_to_first_pass_252", 252, False, "high", "cash_to_first_pass_252_censored"),
        ("evaluations_before_first_pass_252", 252, False, "high", "evaluations_before_first_pass_252_censored"),
        ("first_payout_days_252", 252, False, "high", None),
        ("spent_before_first_payout_252", 252, False, "high", "spent_before_first_payout_252_censored"),
        ("first_payout_size_252", 252, False, "low", None),
        ("longest_wait_252", 252, False, "high", "longest_wait_252_censored"),
        ("break_even_days_252", 252, False, "high", None),
        ("fell_below_be_252", 252, False, "high", None),
        ("deepest_fall_after_be_252", 252, False, "high", None),
        ("peak_oop_12_months", 252, False, "high", None),
        ("return_on_money_at_risk", 252, False, "low", None),
        ("share_months_positive", 252, False, "low", None),
        ("monthly_net_4_12_median", 252, False, "low", None),
        ("monthly_net_4_12_mean", 252, False, "low", None),
        ("spread_monthly_net", 252, False, "high", None),
        ("payouts_per_month", 252, False, "low", None),
        ("payouts_per_fee", 252, False, "low", None),
        ("longest_no_payout_months", 252, False, "high", None),
        ("largest_month_payout_share", 252, False, "high", None),
        ("orders_max", 126, False, "high", None),
        ("accounts_max", 126, False, "high", None),
        ("screen_hours_mean", 126, False, "high", None),
        ("taken_mean", 126, False, "low", None),
        ("passed_by_21", 21, True, "low", None),
        ("paid_by_21", 21, True, "low", None),
    )

    arm_groups = list(units_df.groupby(["arm", "reading"], sort=True))
    deciding_medians: dict[str, float] = {}
    comp_lbl = "naive_coin" if baseline == "naive_coin" else "whole-window-derived registered comparator"

    def _beside_totals(eh: pd.DataFrame) -> dict[str, Any]:
        return {
            "fill_failures_total": int(eh["fill_failures"].sum()) if "fill_failures" in eh.columns else 0,
            "day_ends_total": int(eh["day_ends"].sum()) if "day_ends" in eh.columns else 0,
            "out_of_room_total": int(eh["out_of_room_accounts"].sum()) if "out_of_room_accounts" in eh.columns else 0,
            "time_exit_clip_credit_total": float(eh["time_exit_clip_credit"].sum()) if "time_exit_clip_credit" in eh.columns else 0.0,
            "move_trades_total": int(eh["move_trades"].sum()) if "move_trades" in eh.columns else 0,
            "b_redrawn_total": int(eh["b_redrawn"].sum()) if "b_redrawn" in eh.columns else 0,
            "b_historical_total": int(eh["b_historical"].sum()) if "b_historical" in eh.columns else 0,
            "be_differs_total": int(eh["be_differs"].sum()) if "be_differs" in eh.columns else 0,
            "tb_overlaps_total": int(eh["tb_overlaps"].sum()) if "tb_overlaps" in eh.columns else 0,
            "strict_overlaps_total": int(eh["strict_overlaps"].sum()) if "strict_overlaps" in eh.columns else 0,
        }

    for (arm_name, reading_tag), grp in arm_groups:
        g = grp.sort_values(["start", "seed"], kind="stable")
        n_seeds = int(g["seed"].nunique())
        for m_name, hz, is_share, bad_dir, cens_col in per_unit_measures:
            if m_name not in g.columns:
                continue
            eh = g[g["sessions_left"].astype(int) >= hz]
            if eh.empty:
                continue
            piv = eh.pivot(index="start", columns="seed", values=m_name).sort_index()
            mat = piv.to_numpy(dtype=float)
            sh_after = share_after_252 if hz == 252 else (share_after_126 if hz == 126 else 0.0)
            if np.isfinite(mat).all():
                cr = JM.coin_readings(mat, share=is_share, lag=min(hz, max(1, mat.shape[0] - 1)))
                vd = JM.variance_decomposition(mat) if (mat.shape[0] >= 2 and mat.shape[1] >= 2) else {}
                yrs = [int(str(d)[:4]) for d in piv.index]
                by_y = JM.by_year(mat.mean(axis=1), yrs, np.mean if is_share else np.median, bad=bad_dir)
                sq_info: dict[str, Any] = {}
                if cens_col and cens_col in eh.columns:
                    piv_c = eh.pivot(index="start", columns="seed", values=cens_col).sort_index()
                    c_arr = piv_c.to_numpy(dtype=float)
                    if np.isfinite(c_arr).all():
                        sq = JM.strict_quantiles(mat.ravel(), c_arr.ravel() > 0.5)
                        sq_info = {
                            "sq_n_censored": int(sq["n_censored"]),
                            "sq_p10_exact": bool(sq["p10_exact"]),
                            "sq_p50_exact": bool(sq["p50_exact"]),
                            "sq_p90_exact": bool(sq["p90_exact"]),
                        }
            else:
                # Conditional measures (e.g. first_payout_size, fell_below_be_252, deepest_fall_after_be_252, largest_month_payout_share)
                fin = mat[np.isfinite(mat)]
                if not fin.size:
                    continue
                cr = {
                    "n_starts": int(mat.shape[0]),
                    "n_seeds": n_seeds,
                    "r1_p10": float(np.percentile(fin, 10)),
                    "r1_p50": float(np.percentile(fin, 50)),
                    "r1_p90": float(np.percentile(fin, 90)),
                    "n_finite": int(fin.size),
                }
                vd = {}
                by_y = {}
                sq_info = {}
            r_dict: dict[str, Any] = {
                "baseline": baseline,
                "arm": str(arm_name),
                "reading": str(reading_tag),
                "comparator_label": comp_lbl,
                "measure": m_name,
                "horizon": int(hz),
                "n_starts": int(mat.shape[0]),
                "n_seeds": n_seeds,
                "share_window_after_last_cut": sh_after,
                **cr,
                **sq_info,
                "var_within": vd.get("within", float("nan")),
                "var_between": vd.get("between", float("nan")),
                "share_start_day": vd.get("share_start_day", float("nan")),
                "worst_year": by_y.get("worst_year"),
                "worst_year_val": by_y.get("worst", float("nan")),
                **_beside_totals(eh),
            }
            if arm_name == "off" and reading_tag == W42.READING:
                deciding_medians[m_name] = float(cr.get("r1_share" if is_share else "r1_p50", float("nan")))
            elif arm_name == "off_as_walked" and m_name in deciding_medians:
                aw_v = float(cr.get("r1_share" if is_share else "r1_p50", float("nan")))
                r_dict["path_structure_edge"] = aw_v - deciding_medians[m_name]
            rows.append(r_dict)

        # Design-level Measure (27): CVaR10 of net_month_6 (126) and net_month_12 (252)
        for src_col, m_label, hz in (("net_month_6", "cvar10_net_month_6", 126), ("net_month_12", "cvar10_net_month_12", 252)):
            if src_col not in g.columns:
                continue
            eh = g[g["sessions_left"].astype(int) >= hz]
            if eh.empty:
                continue
            piv = eh.pivot(index="start", columns="seed", values=src_col).sort_index()
            mat = piv.to_numpy(dtype=float)
            if not np.isfinite(mat).all():
                continue
            dc = JM.design_coin_readings(mat, lambda x: UM.cvar(x, 10))
            rows.append(
                {
                    "baseline": baseline,
                    "arm": str(arm_name),
                    "reading": str(reading_tag),
                    "comparator_label": comp_lbl,
                    "measure": m_label,
                    "horizon": int(hz),
                    "n_starts": int(mat.shape[0]),
                    "n_seeds": n_seeds,
                    "share_window_after_last_cut": share_after_252 if hz == 252 else share_after_126,
                    "r1_p50": float(dc["r1"]),
                    "r3_p10": float(dc["r3_p10"]),
                    "r3_p50": float(dc["r3_p50"]),
                    "r3_p90": float(dc["r3_p90"]),
                    **_beside_totals(eh),
                }
            )

        # Design-level Measure (31): funded-account lifetime via JM.funded_lifetime (W = 126 and W = 252)
        if "funded_lifetimes" in g.columns:
            for hz in (126, 252):
                eh = g[g["sessions_left"].astype(int) >= hz]
                if eh.empty:
                    continue
                # B-1 (Q-188b): each account's ending re-read at the reading's own window hz (open at hz: censored)
                unit_accs = [HA.decode_funded_accounts(v, window=hz) for v in eh["funded_lifetimes"].tolist()]
                fl = JM.funded_lifetime(unit_accs, hz)
                for kind_lbl, curve_k in (("funded_lifetime_payouts", "curve_payouts"), ("funded_lifetime_sessions", "curve_sessions")):
                    curve = fl[curve_k]
                    rows.append(
                        {
                            "baseline": baseline,
                            "arm": str(arm_name),
                            "reading": str(reading_tag),
                            "comparator_label": comp_lbl,
                            "measure": f"{kind_lbl}_{hz}",
                            "horizon": int(hz),
                            "n_starts": int(eh["start"].nunique()),
                            "n_seeds": n_seeds,
                            "share_window_after_last_cut": share_after_252 if hz == 252 else share_after_126,
                            "r1_p10": float(JM.km_quantile(curve, 0.10)),
                            "r1_p50": float(JM.km_quantile(curve, 0.50)),
                            "r1_p90": float(JM.km_quantile(curve, 0.90)),
                            "sq_n_censored": int(fl["n_censored"]),
                            "n_finite": int(fl["n_accounts"]),
                            **_beside_totals(eh),
                        }
                    )

    out_df = pd.DataFrame(rows)
    if len(out_df):
        # m-i and m-8 (Q-188b): every reading row carries its arm's label and the record it read, beside
        out_df["reading_label"] = out_df["arm"].astype(str).map(lambda a: READING_LABELS.get(a, ""))
        out_df["record_read"] = RECORD_READ
    return out_df


def run_h4_b(
    baseline: str,
    *,
    start_lo: int = 0,
    start_hi: int | None = None,
    part_tag: str = "",
    workers: int = 2,
    arms_filter: str = "all",
    j_seeds: int = HA.H4_J,
    check_exact: bool = True,
    root: Path = ROOT,
    results_dir: Path | None = None,
) -> dict[str, Any]:
    """H4-B: run one baseline over starts `[start_lo, start_hi)` and ALL `j_seeds` seeds (`0..j_seeds-1`)."""
    from extended import RESULTS_DIR
    from extended import results as RES

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=True)
    # rc-3 (Q-188b): beside the declared 5.51 GB refusal, the disk sized from the log's true row cost (231 B, not
    # Appendix A's 128 B): two copies (a part's and the merge's) of all four baselines' declared rows
    disk_rc3 = HA.check_trade_log_disk(
        root, len(BASELINES) * HA.H4_TRADE_ROWS_PER_BASELINE, copies=2,
        what="H4-B's audit-sample trade logs (four baselines, each part's copy and the merge's)",
    )

    bundle = build_bundle(baseline, last_day=W42.SEARCH_LAST, root=root)
    HA.check_job_ends_search_window(bundle.dates, f"H4-B {baseline}")
    HA.check_cost_ticks(bundle.facts)          # m-e: the oracle's declared cost ticks, checked at the part's start
    n_sess = len(bundle.dates)
    lo = max(0, int(start_lo))
    hi = n_sess if start_hi is None else min(n_sess, int(start_hi))
    if not (0 <= lo < hi <= n_sess):
        raise ValueError(f"invalid start range [{lo}, {hi}) for {n_sess} sessions")

    # Pre-compute sub-indices per (day, trade) matching three_way_baseline._Unit
    subs = subs_of(bundle.facts)

    arms = ARM_SPECS if arms_filter == "all" else tuple(a for a in ARM_SPECS if a[0] in arms_filter.split(","))
    if not arms:
        raise ValueError(f"no matching arms for {arms_filter!r}")

    starts = list(range(lo, hi))
    chunks = [starts[k : k + BATCH_STARTS] for k in range(0, len(starts), BATCH_STARTS)]
    cal_fset = frozenset(date.fromisoformat(d) for d in bundle.dates)

    ctx = {
        "baseline": baseline,
        "dates": bundle.dates,
        "blocks": bundle.blocks,
        "args": bundle.args,
        "facts": bundle.facts,
        "subs": subs,
        "seed_indices": tuple(range(int(j_seeds))),
        "part_id": S.PARTS["H4-B"],
        "seed_role": "h4b_coins",
        "sample_seed_role": "h4_sample",
        "sample_part_id": S.PARTS["H4-U"],
        "arms": arms,
        "calendar_fset": cal_fset,
        "latency": BASELINE_LATENCY[baseline],
        "check_exact": bool(check_exact),
    }

    t0 = time.perf_counter()
    if not 1 <= int(workers) <= H4B_MAX_WORKERS:
        raise ValueError(f"H4-B's worker count is 1 .. {H4B_MAX_WORKERS}, got {workers}")
    w = int(workers)
    results_chunks: list[dict[str, Any]] = []
    if w == 1 or len(chunks) <= 1:
        _init_h4b_worker(ctx)
        for idx_c, ch in enumerate(chunks, 1):
            results_chunks.append(_h4b_start_chunk(ch))
            print(f"  [H4-B {baseline}{part_tag}] batch {idx_c}/{len(chunks)} ({ch[0]}..{ch[-1]}), {time.perf_counter() - t0:.1f}s", flush=True)
    else:
        with cf.ProcessPoolExecutor(max_workers=w, initializer=_init_h4b_worker, initargs=(ctx,)) as ex:
            futs = [(idx_c, ch, ex.submit(_h4b_start_chunk, ch)) for idx_c, ch in enumerate(chunks, 1)]
            for idx_c, ch, fut in futs:
                results_chunks.append(fut.result())
                print(f"  [H4-B {baseline}{part_tag}] batch {idx_c}/{len(chunks)} ({ch[0]}..{ch[-1]}), {time.perf_counter() - t0:.1f}s", flush=True)

    unit_rows = [r for ch in results_chunks for r in ch["units"]]
    trade_rows = [r for ch in results_chunks for r in ch["trades"]]
    units_df = pd.DataFrame(unit_rows)
    trades_df = pd.DataFrame(trade_rows, columns=list(TRADE_LOG_COLS))
    readings_df = summarise_baseline_readings(units_df, bundle.dates, baseline)

    suf = f"_{part_tag}" if part_tag else ""
    params = {
        "part": f"H4-B{suf}",
        "baseline": baseline,
        "start_lo": lo,
        "start_hi": hi,
        "starts_count": len(starts),
        "J": int(j_seeds),
        "arms": [a[0] for a in arms],
        "seed_roles": ["h4b_coins", "h4_sample"] + (["h4s_schedule_side"] if baseline == "naive_coin" else []),
        "schedules_sha256": bundle.trades_sha256,
        "exact_checked": int(sum(ch["exact_checked"] for ch in results_chunks)),
        "exact_differs": int(sum(ch["exact_differs"] for ch in results_chunks)),
        # B-2 (Q-188b): the exact-run differences by arm, horizon and kind (lanes), with the starts checked and the
        # starts differing (section 12's "count of starts where they differ"), and every differing unit listed
        "exact_differs_by_kind": HA.merge_exact_tallies([ch.get("exact_tally", {}) for ch in results_chunks]),
        "exact_differing_units_fields": ["arm", "start", "seed", "h", "kind"],
        "exact_differing_units": [u for ch in results_chunks for u in ch.get("exact_units", [])],
        # m-8 (section 12): the record every reading of this file reads, and what was compared beside it
        "record_read": {"readings": RECORD_READ, "exact_horizons": list(EXACT_HORIZONS),
                        "exact_every_start_arms": [a[0] for a in arms if a[4]], "exact_every": EXACT_EVERY},
        "oracle_checked_trades": int(sum(ch["oracle_checked"] for ch in results_chunks)),
        "rung_alerts_sum": int(sum(ch["rung_alerts_sum"] for ch in results_chunks)),
        "keys_checked": int(sum(ch["keys_checked"] for ch in results_chunks)),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        # the lead's ruling on the sizing scout (Q-188b): the worker count run, and each worker's peak working set
        "workers": int(w),
        "workers_declared_cap": MAX_WORKERS,
        "worker_peak_wset_mb": _worker_peaks(results_chunks),
        "parent_peak_wset_mb": round(_peak_mb(), 1),
        "preconditions": pre,
        "threads": thread_env(),  # F-13 (Q-188b)
        # rc-3 (Q-188b): the trade log's measured size beside the disk check made at the part's start
        "trade_log": {"rows": int(len(trades_df)), "row_bytes_assumed": HA.H4_TRADE_ROW_BYTES,
                      "declared_rows_per_baseline": HA.H4_TRADE_ROWS_PER_BASELINE, "disk_check": disk_rc3},
        "bundle_meta": {k: v for k, v in bundle.meta.items() if k != "cut"},
    }

    u_p, _ = RES.write_result(
        units_df,
        f"h4_units_{baseline}{suf}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B per-unit scorecard readings for {baseline} (starts {lo}..{hi - 1}, J={j_seeds}, E-287).",
    )
    r_p, _ = RES.write_result(
        readings_df,
        f"h4_readings_{baseline}{suf}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B summary readings (MEASURES 1.4, variance decomposition, by-year, beside) for {baseline} (starts {lo}..{hi - 1}).",
    )
    t_p, _ = RES.write_result(
        trades_df,
        f"h4_trades_{baseline}{suf}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B 1% audit-sample taken-trade log for {baseline} (starts {lo}..{hi - 1}; ticks and times only, no prices).",
    )
    gc.collect()
    return {"units_csv": str(u_p), "readings_csv": str(r_p), "trades_csv": str(t_p), "elapsed_s": params["elapsed_s"]}


def merge_h4_b_parts(
    baseline: str,
    part_tags: Sequence[str],
    *,
    root: Path = ROOT,
    results_dir: Path | None = None,
) -> dict[str, Any]:
    """Combine disjoint `H4-B` start-range parts for `baseline` into `results/h4_units_<baseline>.csv`,
    `results/h4_readings_<baseline>.csv`, and `results/h4_trades_<baseline>.csv`, verifying full search-calendar
    coverage, zero duplicate `(arm, start, seed)` rows, and every part file's manifest sha256."""
    from extended import RESULTS_DIR
    from extended import results as RES

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=False, require_disk=False)
    cal = SCAL.load_search_calendar(rdir / W42.SEARCH_CALENDAR)
    dates = tuple(str(d) for d in cal.dates)

    u_parts, t_parts = [], []
    part_shas: dict[str, dict[str, str]] = {}
    agg_exact_checked = 0
    agg_exact_differs = 0
    agg_oracle_checked = 0
    agg_rung_alerts = 0
    agg_keys_checked = 0
    sched_hashes_seen: set[str] = set()
    kept_hashes_seen: set[str] = set()
    tallies: list[Mapping[str, Any]] = []
    tally_missing: list[str] = []
    part_bytes = 0
    for tag in part_tags:
        up = rdir / f"h4_units_{baseline}_{tag}.csv"
        tp = rdir / f"h4_trades_{baseline}_{tag}.csv"
        for p in (up, tp):
            if not p.is_file():
                raise HA.H4AuditRefused(f"missing part file: {p}")
            side = Path(f"{p}.manifest.json")
            man = json.loads(side.read_text(encoding="utf-8"))
            sha = HA.raw_sha256(p)
            if man.get("sha256") != sha:
                raise HA.H4AuditRefused(f"{p.name}: sha256 mismatch vs manifest")
            part_shas.setdefault(tag, {})[p.name] = sha
            part_bytes += int(p.stat().st_size)
            if p == up:
                pm = man.get("parameters", {})
                agg_exact_checked += int(pm.get("exact_checked", 0))
                agg_exact_differs += int(pm.get("exact_differs", 0))
                agg_oracle_checked += int(pm.get("oracle_checked_trades", 0))
                agg_rung_alerts += int(pm.get("rung_alerts_sum", 0))
                agg_keys_checked += int(pm.get("keys_checked", 0))
                if pm.get("schedules_sha256"):
                    sched_hashes_seen.add(str(pm["schedules_sha256"]))
                kh = (pm.get("bundle_meta") or {}).get("kept_trades_sha256")
                if kh:
                    kept_hashes_seen.add(str(kh))
                if "exact_differs_by_kind" in pm:
                    tallies.append(pm["exact_differs_by_kind"])
                else:
                    tally_missing.append(str(tag))
        u_parts.append(pd.read_csv(up))
        t_parts.append(pd.read_csv(tp))
    if len(sched_hashes_seen) > 1:
        raise HA.H4AuditRefused(f"{baseline} merge: parts built on different schedules_sha256: {sorted(sched_hashes_seen)}")
    if len(kept_hashes_seen) > 1:
        raise HA.H4AuditRefused(f"{baseline} merge: parts built on different kept schedules: {sorted(kept_hashes_seen)}")
    # rc-3 (Q-188b): the merge writes a second full copy of the parts; refuse unless the disk holds it
    disk_merge = {"need_bytes": int(part_bytes), "free_bytes": HA.check_free_disk(rdir, int(part_bytes))}

    units_df = pd.concat(u_parts, ignore_index=True).sort_values(["arm", "start", "seed"], kind="stable").reset_index(drop=True)
    trades_df = pd.concat(t_parts, ignore_index=True)

    # Verify complete disjoint coverage on deciding `off` arm
    off_df = units_df[(units_df["arm"] == W42.ARM) & (units_df["reading"] == W42.READING)]
    got_starts = sorted(off_df["start"].astype(str).unique().tolist())
    if got_starts != list(dates):
        raise HA.H4AuditRefused(f"{baseline} merge: covered {len(got_starts)} starts != {len(dates)} search calendar starts")
    if off_df.duplicated(["start", "seed"]).any():
        raise HA.H4AuditRefused(f"{baseline} merge: duplicate (start, seed) rows across parts")
    if (units_df["strict_overlaps"].astype(int) > 0).any():
        raise HA.H4OverlapRefused(f"{baseline} merge: non-zero strict_overlaps in merged units")

    readings_df = summarise_baseline_readings(units_df, dates, baseline)
    params = {
        "part": "H4-B-merge",
        "baseline": baseline,
        "merged_parts": list(part_tags),
        "part_files_sha256": part_shas,
        "schedules_sha256": next(iter(sched_hashes_seen), None),
        "kept_schedule_sha256": next(iter(kept_hashes_seen), None),
        "exact_checked": agg_exact_checked,
        "exact_differs": agg_exact_differs,
        # B-2: the by-kind tally over the parts that carry it (parts run before Q-188b carry none: listed, and their
        # kinds come from scripts/h4_exact_diff_classify.py on the audit sample)
        "exact_differs_by_kind": HA.merge_exact_tallies(tallies),
        "exact_differs_by_kind_missing_parts": tally_missing,
        "record_read": {"readings": RECORD_READ, "exact_horizons": list(EXACT_HORIZONS)},
        "disk_check": disk_merge,
        "oracle_checked_trades": agg_oracle_checked,
        "rung_alerts_sum": agg_rung_alerts,
        "keys_checked": agg_keys_checked,
        "seed_roles": ["h4b_coins", "h4_sample"] + (["h4s_schedule_side"] if baseline == "naive_coin" else []),
        "preconditions": pre,
        "threads": thread_env(),  # F-13 (Q-188b)
    }
    u_p, _ = RES.write_result(
        units_df,
        f"h4_units_{baseline}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B complete merged per-unit readings for {baseline} (all search starts, J={HA.H4_J}, E-287).",
    )
    r_p, _ = RES.write_result(
        readings_df,
        f"h4_readings_{baseline}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B complete summary readings for {baseline} (MEASURES 1.4, variance decomposition, by-year, beside, E-287).",
    )
    t_p, _ = RES.write_result(
        trades_df,
        f"h4_trades_{baseline}",
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=f"H4-B complete 1% audit-sample taken-trade log for {baseline} (ticks and times only, no prices).",
    )
    return {"units_csv": str(u_p), "readings_csv": str(r_p), "trades_csv": str(t_p)}


# --------------------------------------------------------------------------------------------- auditor (section 16.6)


def check_h4_price_levels(results_dir: Path, root: Path = ROOT) -> list[str]:
    """M-5: scan every `h4_*.csv` in `results_dir` via `extended.price_levels.scan_path` + `apply_allowlist`
    (checking untracked result files too, without passing invalid positional args to `scripts/check_price_levels.py`)."""
    from extended import price_levels as PL

    allow = PL.load_allowlist(Path(root) / PL.ALLOWLIST_REL)
    h4_csvs = sorted(p for p in Path(results_dir).glob("h4_*.csv"))
    all_findings = []
    for p in h4_csvs:
        try:
            rel_name = p.resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            rel_name = p.name
        all_findings.extend(PL.scan_path(p, name=rel_name, allow=allow))
    refused, _ = PL.apply_allowlist(all_findings, allow)
    if refused:
        raise HA.H4AuditRefused("price-level guard refused: " + "; ".join(str(f) for f in refused))
    return [p.name for p in h4_csvs]


def run_h4_audit(
    *,
    root: Path = ROOT,
    results_dir: Path | None = None,
    verify_replay: bool = True,
) -> dict[str, Any]:
    """Section 16 item 6: independent auditor re-derivation of H4 outputs before W42-R1 reads anything.

    Checks:
    1. Verifies H4-0 sealed hash & H4-A match (`m-3`), then re-reads `results/h4_w42_input.csv` through the frozen
       adapter `extended.h4_collect.w42_readings` and verifies `units_files_sha256` + full value parity vs
       `results/h4_units_<baseline>.csv`;
    2. Recomputes every summary row from `results/h4_units_<baseline>.csv` and verifies against `h4_readings_<baseline>.csv`;
    3. Independently recomputes strict `+5 min` overlaps and replays the scalar zero-edge oracle on every row of
       `results/h4_trades_<baseline>.csv` without calling `three_way_baseline`;
    4. When `verify_replay=True`, recomputes every search year's first start under the first `K.SAMPLE_SEEDS` (64)
       seed indices for every baseline and arm from the schedules and keys, verifying bit-for-bit equality;
    5. Scans every `h4_*.csv` result file via `extended.price_levels.scan_path` + `apply_allowlist` (`M-5`).
    """
    from extended import RESULTS_DIR
    from extended import h4_collect as HC

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    HA.assert_h4_preconditions(root, require_clean=False, require_lock=False, require_disk=False)

    # m-3: verify H4-0 sealed hash & H4-A match when present (required in production)
    h40_csv = rdir / "h4_0_probe.csv"
    h4a_csv = rdir / "h4_as_traded.csv"
    if not h40_csv.is_file() or not h4a_csv.is_file():
        raise HA.H4AuditRefused(f"REFUSED (m-3): auditor requires both {h40_csv.name} and {h4a_csv.name}")
    h40_man = json.loads(Path(f"{h40_csv}.manifest.json").read_text(encoding="utf-8"))
    if h40_man.get("sha256") != HA.raw_sha256(h40_csv):
        raise HA.H4AuditRefused("REFUSED (m-3): h4_0_probe.csv sha256 mismatch vs manifest")
    h4a_man = json.loads(Path(f"{h4a_csv}.manifest.json").read_text(encoding="utf-8"))
    if h4a_man.get("sha256") != HA.raw_sha256(h4a_csv):
        raise HA.H4AuditRefused("REFUSED (m-3): h4_as_traded.csv sha256 mismatch vs manifest")
    if h4a_man.get("parameters", {}).get("h4_0_sealed_hash_matched") is not True:
        raise HA.H4AuditRefused("REFUSED (m-3): h4_as_traded manifest does not confirm h4_0_sealed_hash_matched == True")

    # 1. Verify h4_w42_input.csv through frozen adapter
    w42_csv = rdir / W42.COLLECTION_RESULT
    w42_man = json.loads(Path(f"{w42_csv}.manifest.json").read_text(encoding="utf-8"))
    readings = HC.w42_readings(w42_csv, w42_man)
    cal_dates = tuple(str(d) for d in w42_man["parameters"]["starts"])
    w42_units_shas = w42_man.get("parameters", {}).get("units_files_sha256", {})

    # 2 & 3. Recompute summary rows + strict overlaps + scalar oracle from units & trades CSVs
    coin_seed = S.issue("h4b_coins")
    part_id = S.PARTS["H4-B"]
    checked_trades = 0
    checked_units = 0
    summary_rows_checked = 0
    replay_units_checked = 0
    ledger_rows_checked = 0

    # First start of each search year (2020..2023)
    first_of_year: list[int] = []
    seen_yrs: set[str] = set()
    for idx_d, d_str in enumerate(cal_dates):
        yr = d_str[:4]
        if yr not in seen_yrs:
            seen_yrs.add(yr)
            first_of_year.append(idx_d)

    for bname in BASELINES:
        up = rdir / f"h4_units_{bname}.csv"
        rp = rdir / f"h4_readings_{bname}.csv"
        tp = rdir / f"h4_trades_{bname}.csv"
        # m-3: verify units_files_sha256 recorded in h4_w42_input manifest matches h4_units_<baseline>.csv
        got_u_sha = HA.raw_sha256(up)
        if w42_units_shas.get(bname) != got_u_sha:
            raise HA.H4AuditRefused(
                f"REFUSED (m-3): h4_w42_input units_files_sha256[{bname}]={w42_units_shas.get(bname)} != {got_u_sha}"
            )
        udf = pd.read_csv(up)
        rdf = pd.read_csv(rp)
        tdf = pd.read_csv(tp)

        # m-3: full value parity between h4_w42_input.csv (`readings[bname]`) and h4_units_<bname>.csv (off/martingale)
        off_u = udf[(udf["arm"] == W42.ARM) & (udf["reading"] == W42.READING)].sort_values(["start", "seed"], kind="stable")
        for req_k in W42.REQUIRED:
            piv_u = off_u.pivot(index="start", columns="seed", values=req_k).loc[list(cal_dates)].to_numpy(dtype=float)
            arr_w = np.asarray(readings[bname][req_k], dtype=float)
            if piv_u.shape != arr_w.shape or not np.allclose(piv_u, arr_w, atol=1e-9, rtol=1e-9, equal_nan=True):
                raise HA.H4AuditRefused(f"REFUSED (m-3): h4_w42_input mismatch vs h4_units_{bname} on {req_k}")

        # Recompute summary rows from units CSV
        recomp_r = summarise_baseline_readings(udf, cal_dates, bname)
        if len(recomp_r) != len(rdf):
            raise HA.H4AuditRefused(f"auditor summary length mismatch for {bname}: {len(recomp_r)} != {len(rdf)}")
        for col in ("r1_p50", "r1_share", "r3_p50", "share_start_day"):
            if col in recomp_r.columns and col in rdf.columns:
                a = pd.to_numeric(recomp_r[col], errors="coerce").to_numpy(float)
                b = pd.to_numeric(rdf[col], errors="coerce").to_numpy(float)
                if not np.allclose(a, b, atol=1e-9, rtol=1e-9, equal_nan=True):
                    raise HA.H4AuditRefused(f"auditor summary mismatch for {bname} column {col}")
        summary_rows_checked += len(recomp_r)

        # Map unit -> runner's logged strict_overlaps
        ov_map = {
            (str(r["arm"]), int(r["start_idx"]), int(r["seed"])): int(r["strict_overlaps"])
            for _, r in udf.iterrows()
        }
        for (arm_name, s_idx, c_idx), grp in tdf.groupby(["arm", "start", "seed_index"], sort=False):
            recs = grp.to_dict("records")
            recomp_ov = HA.count_strict_overlaps(recs)
            want_ov = ov_map.get((str(arm_name), int(s_idx), int(c_idx)), -1)
            if recomp_ov != 0 or recomp_ov != want_ov:
                raise HA.H4OverlapRefused(
                    f"auditor overlap mismatch on {bname}/{arm_name}/start={s_idx}/seed={c_idx}: "
                    f"recomputed={recomp_ov}, runner={want_ov}"
                )
            checked_units += 1
            for r in recs:
                if str(r["reading"]) == W42.READING:
                    # m-e: the costs, G <= target and L re-derived from the log's d and fee (the arm's worse ticks
                    # by its name); the full re-derivation from the engine's ledger is the replay's, below
                    HA.verify_race_trade_row(r, seed=coin_seed, part=part_id, history=0, require_inputs=True)
                    checked_trades += 1

        # 4. Recompute every search year's first start under first K.SAMPLE_SEEDS (64) seed indices, every arm
        if verify_replay:
            bundle = build_bundle(bname, last_day=W42.SEARCH_LAST, root=root)
            cal_fset = frozenset(date.fromisoformat(d) for d in bundle.dates)
            # m-e (Q-188b): the replay keeps the engine's own ledger (logging only; the unit equality below would
            # refuse any change it made), so the oracle re-derives every taken trade's inputs from the engine
            args_led = {**bundle.args, "path": {**bundle.args["path"], "record_trades": True}}
            subs_b = subs_of(bundle.facts)
            srule = (bundle.args.get("draws") or {}).get("sizing")
            fee_sched = getattr(srule, "fee_schedule", None)
            sample_seeds = tuple(range(min(K.SAMPLE_SEEDS, int(udf["seed"].max()) + 1)))
            by_key = {
                (str(r["arm"]), int(r["start_idx"]), int(r["seed"])): r
                for _, r in udf[udf["start_idx"].isin(first_of_year) & udf["seed"].isin(sample_seeds)].iterrows()
            }
            for s_idx in first_of_year:
                sl = len(bundle.dates) - s_idx
                obs = min(JM.YEAR, sl)
                for arm_name, reading_tag, outcome_mode, arm_spec, _ in ARM_SPECS:
                    rec = TB.simulate(
                        bundle.blocks,
                        args_led,
                        bundle.facts,
                        s_idx,
                        sample_seeds,
                        obs,
                        seed=coin_seed,
                        part=part_id,
                        history=0,
                        block_sessions=len(bundle.dates),
                        dates=bundle.dates,
                        arm=arm_spec,
                        outcome=outcome_mode,
                        keep_paths=True,
                        log=True,
                        calendar=cal_fset,
                    )
                    for j_lane, c_idx in enumerate(sample_seeds):
                        u_rec = HA.extract_unit_measures(
                            baseline=bname,
                            arm=arm_name,
                            reading=reading_tag,
                            start=s_idx,
                            start_date=bundle.dates[s_idx],
                            seed_index=c_idx,
                            sessions_left=sl,
                            rel=rec.rel[j_lane],
                            first_pass=int(rec.first_pass[j_lane]),
                            first_pay=int(rec.first_pay[j_lane]),
                            arrivals=rec.arrivals[j_lane],
                            path=rec.paths[j_lane],
                            log_rows=rec.logs[j_lane],
                            blocks=bundle.blocks,
                            latency=BASELINE_LATENCY[bname],
                            strict_overlaps=0,
                            payout_lag=int(bundle.args["path"]["payout_lag_days"]),
                        )
                        if outcome_mode == "race":
                            t_rows = _format_sampled_trade_rows(
                                bname, arm_name, reading_tag, s_idx, bundle.dates[s_idx], c_idx, bundle.dates,
                                bundle.blocks, bundle.facts, subs_b, arm_spec, rec.logs[j_lane],
                            )
                            led_c = HA.verify_unit_against_ledger(
                                t_rows, getattr(rec.paths[j_lane], "trades", None) or [], start=s_idx,
                                seed=coin_seed, part=part_id, fee_schedule=fee_sched,
                            )
                            ledger_rows_checked += int(led_c["rows"])
                        logged = by_key.get((arm_name, s_idx, c_idx))
                        if logged is None:
                            raise HA.H4AuditRefused(f"auditor replay missing unit {bname}/{arm_name}/{s_idx}/{c_idx}")
                        for req_k, (h_req, _, _) in W42.REQUIRED.items():
                            if sl >= h_req:
                                a_v, b_v = float(u_rec[req_k]), float(logged[req_k])
                                if abs(a_v - b_v) > 1e-9:
                                    raise HA.H4AuditRefused(
                                        f"auditor replay mismatch {bname}/{arm_name}/{s_idx}/{c_idx} {req_k}: "
                                        f"{a_v} != {b_v}"
                                    )
                        replay_units_checked += 1

    # 5. M-5: Price-level guard on every H4 CSV in results/
    checked_names = check_h4_price_levels(rdir, root)

    return {
        "audit_holds": True,
        "w42_baselines": sorted(readings.keys()),
        "summary_rows_verified": summary_rows_checked,
        "sampled_units_verified": checked_units,
        "sampled_race_trades_verified": checked_trades,
        "replay_units_verified": replay_units_checked,
        "ledger_rederived_trades_verified": ledger_rows_checked,
        "price_checked_files": checked_names,
    }


# --------------------------------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", required=True, choices=("H4-0", "H4-S", "H4-S-checks", "H4-A", "H4-B", "merge", "audit"))
    ap.add_argument("--baselines", default=",".join(BASELINES), help="H4-S-checks: comma-separated baselines")
    ap.add_argument("--no-nested", action="store_true", help="H4-S-checks: the dropped alerts only, no I-2")
    ap.add_argument("--baseline", choices=BASELINES, default=None)
    ap.add_argument("--start-lo", type=int, default=0)
    ap.add_argument("--start-hi", type=int, default=None)
    ap.add_argument("--part-tag", default="")
    ap.add_argument("--merge-tags", default="", help="comma-separated part tags for --part merge")
    ap.add_argument("--arms", default="all", help="'all' or comma-separated subset of arms")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--sealed-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    if args.part == "H4-0":
        res = run_h4_0(sealed_dir=args.sealed_dir)
        print(f"H4-0 done: sec/start={res['sec_per_start']:.4f}, sealed_sha256={res['sealed_sha256'][:16]}...")
    elif args.part == "H4-S-checks":
        bl = [b.strip() for b in args.baselines.split(",") if b.strip()]
        res = run_h4_s_checks(bl, nested=not args.no_nested, tag=args.part_tag)
        print(f"H4-S checks done: {res['sigma_drops_csv']} {res.get('identities_csv', '')}; "
              f"I-2 failed rows: {len(res.get('failed', []))}")
        for b_name, sm in res["summary"].items():
            print(f"  {b_name}: lt_2={sm['dropped_sigma_lt_2']} zero={sm['dropped_sigma_zero']} kept={sm['kept_trades']}")
    elif args.part == "H4-S":
        res = run_h4_s()
        print(f"H4-S done: {res['supply_csv']}, {res['identities_csv']}")
    elif args.part == "H4-A":
        res = run_h4_a(workers=args.workers)
        print(f"H4-A done: {res['csv']} (I-4 all hold, H4-0 matched={res['h4_0_matched']})")
    elif args.part == "H4-B":
        if not args.baseline:
            ap.error("--part H4-B requires --baseline")
        res = run_h4_b(
            args.baseline,
            start_lo=args.start_lo,
            start_hi=args.start_hi,
            part_tag=args.part_tag,
            workers=args.workers,
            arms_filter=args.arms,
        )
        print(f"H4-B {args.baseline} done in {res['elapsed_s']:.1f}s -> {res['units_csv']}")
    elif args.part == "merge":
        if not args.baseline or not args.merge_tags:
            ap.error("--part merge requires --baseline and --merge-tags")
        tags = [t.strip() for t in args.merge_tags.split(",") if t.strip()]
        res = merge_h4_b_parts(args.baseline, tags)
        print(f"H4-B merge {args.baseline} done -> {res['units_csv']}")
    else:
        res = run_h4_audit()
        print(
            f"H4 audit HOLDS: {res['sampled_units_verified']} sampled units, "
            f"{res['sampled_race_trades_verified']} race trades verified, "
            f"{len(res['price_checked_files'])} files clean."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
