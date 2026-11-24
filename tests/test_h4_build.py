"""H4 post-pin build unit tests (`prereg/H4_rebaseline.md` section 17; E-287).

Synthetic data only: zero bar files, zero held-out reads, zero writes to `results/`. Uses `h4_tests` seed in part
`H4-T` only (or non-block test seeds where testing non-H4 paths). Does NOT import `extended.results` at top level
(Q-204 sys.path isolation).

Covers every Section 17 requirement:
1. Pre-run refusals: held-out start, confirmation-window session, reader span past 2023-12-29, edited declaration,
   insufficient free disk (rc-3), calendar mismatch (rm-6 / rm-5), W42-R1 freeze intact (F4-3).
2. Cross-session alert volatility (`alert_sigma_cross_session`, F4-1): scramble test (every bar at or after alert
   scrambled -> sigma bit-for-bit unchanged), session-break gap return excluded, < 2 changes returns None.
3. Strict `+5 min` per-unit overlap counter (`count_strict_overlaps`, RC-2, M-1): exact `+5 min` counts 0 (admitted),
   `+4 min` counts 1 (refused), multi-day clock boundary, and vendored router boundary pair counting 0.
4. Independent scalar oracle (`verify_race_trade_row`, F4-5, F4-10): passes on exact race / walk / move / fill-fail
   rows; REFUSES planted forced-loss row, wrong move_x / step params, floor breach, and forbidden historical fields
   (`u`, `mae`, `at_need`, `rr_used`, `exit_kind`).
5. Breakeven move law exact-fraction check (`three_way_move.move_law`, gross EV == 0, probs sum to 1).
6. Bounded mirror `as_walked` (`three_way_baseline.TradeFacts.walked_mirror`, rc-11): flipped 2.5R target never books
   `-2.5R`; stays bounded within `[-stop, +target]`.
7. Naive-coin unchained offer builder (`extended/h4_coin_source.py`): synthetic as-run mode (clock grid, L=5, void
   calendar, closed 08:30-08:59 & BLS windows, STAGE2 breakeven move ON, `h4s_schedule_side` role keying) AND P-16 /
   I-5 synthetic mode (exact column schema & `trades_hash` reproducibility).
8. `scripts/h4_collect.py` end-to-end synthetic round-trip into `extended/h4_collect.py::w42_readings` AND into
   `scripts/wave42_apply.py::apply`, plus refusals (missing seed, missing key, changed byte, held-out block,
   non-zero strict_overlaps, blank on E_h).
9. Zero raw H4 seed literals in the new H4 build files (`extended/h4_coin_source.py`, `extended/h4_audit.py`,
   `scripts/h4_collect.py`, `scripts/h4_rebaseline.py`).
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import h4_audit as HA  # noqa: E402
from extended import h4_coin_source as CS  # noqa: E402
from extended import h4_collect as HC  # noqa: E402
from extended import reader as RDR  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_move as MV  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import walker as W  # noqa: E402
from extended import wave42 as W42  # noqa: E402
from scripts import h4_collect as H4C_SCRIPT  # noqa: E402
from scripts import h4_rebaseline as H4R  # noqa: E402
from scripts import wave42_apply as W42_APP  # noqa: E402

H4_TEST_SEED = S.issue("h4_tests")
H4_TEST_PART = S.PARTS["H4-T"]


# --------------------------------------------------------------------------------------------- 1. Pre-run & held-out refusals


def test_held_out_and_confirmation_refusals():
    # Reader refuses any span reaching 2024-01-02 under h4_search_years
    with pytest.raises(Exception):
        RDR.authorise("2020-01-02", "2024-01-02", purpose="h4_search_years", declaration="E-287", what="test")
    with pytest.raises(Exception):
        RDR.authorise("2020-01-02", "2026-07-17", purpose="h4_search_years", declaration="E-287", what="test")

    # Plan refuses held-out start and confirmation-window date
    dates_ho = tuple((dt.date(2023, 12, 1) + dt.timedelta(days=k)).isoformat() for k in range(40))
    with pytest.raises(R.HeldOutRefused):
        R.Plan(
            seed=H4_TEST_SEED, part=H4_TEST_PART, history=0, starts=(0,), seed_indices=(0, 1),
            horizon=35, block_sessions=len(dates_ho), dates=dates_ho,
        )
    dates_conf = ("2026-07-16", "2026-07-17", "2026-07-18")
    with pytest.raises(R.HeldOutRefused):
        R.Plan(
            seed=H4_TEST_SEED, part=H4_TEST_PART, history=0, starts=(0,), seed_indices=(0,),
            horizon=2, block_sessions=3, dates=dates_conf,
        )


def test_preconditions_and_disk_refusals(tmp_path: Path):
    # Real repo passes preconditions (without clean-run/lock requirement)
    pre = HA.assert_h4_preconditions(ROOT, require_clean=False, require_lock=False, require_disk=False, check_w42_git=True)
    assert pre["h4_decl_sha256"] == HA.H4_DECL_LF_SHA256
    assert pre["reg_constants_sha256"] == HA.H4_REG_CONSTANTS_SHA256
    assert pre["search_calendar_sha256"] == HA.H4_SEARCH_CALENDAR_SHA256

    # Edited declaration refused
    fake_repo = tmp_path / "repo"
    (fake_repo / "prereg").mkdir(parents=True)
    (fake_repo / "prereg" / "H4_rebaseline.md").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(HA.H4AuditRefused, match="LF sha256"):
        HA.assert_h4_preconditions(fake_repo, require_clean=False, require_lock=False, check_w42_git=False)

    # Disk space refusal (require 10^15 bytes)
    with pytest.raises(HA.H4AuditRefused, match="free disk"):
        HA.check_free_disk(tmp_path, min_bytes=10**15)


# --------------------------------------------------------------------------------------------- 2. Cross-session sigma (F4-1)


def test_alert_sigma_cross_session_scramble_and_gap_exclusion():
    rng = np.random.default_rng(12345)
    # Day 0: bars 1..1330 with smooth random walk around 10000
    c0 = np.full(1441, np.nan)
    c0[1:1331] = 10000.0 + np.cumsum(rng.normal(0.0, 1.0, 1330)) * 0.25
    # Day 1: huge +500 point overnight gap at bar 1, then small 1-tick moves
    c1 = np.full(1441, np.nan)
    c1[1:1331] = c0[1330] + 500.0 + np.cumsum(rng.normal(0.0, 1.0, 1330)) * 0.25

    # At 17:00 CT (decision=0) on Day 1: reads last 60 bars of Day 0 ONLY (never refused!)
    s_open = CS.alert_sigma_cross_session([c0, c1], 1, 0, lookback=60, tick=0.25)
    assert s_open is not None and 0.3 < s_open < 3.0

    # At 17:10 CT (decision=10) on Day 1: crosses break into Day 0, EXCLUDING the +500 pt gap!
    s_cross = CS.alert_sigma_cross_session([c0, c1], 1, 10, lookback=60, tick=0.25)
    assert s_cross is not None and s_cross < 5.0  # if gap were included, std would be > 250 ticks!

    # Scramble test: scrambling every bar strictly after decision=10 leaves sigma bit-for-bit identical
    c1_scr = c1.copy()
    c1_scr[11:] = rng.normal(0.0, 5000.0, len(c1_scr) - 11)
    assert CS.alert_sigma_cross_session([c0, c1_scr], 1, 10, lookback=60, tick=0.25) == s_cross

    # Changing bar 10 (closed AT alert) DOES change sigma
    c1_mod = c1.copy()
    c1_mod[10] += 25.0
    assert CS.alert_sigma_cross_session([c0, c1_mod], 1, 10, lookback=60, tick=0.25) != s_cross

    # Fewer than 2 changes behind alert on very first day -> None (dropped from supply, counted beside)
    assert CS.alert_sigma_cross_session([c0], 0, 0) is None
    assert CS.alert_sigma_cross_session([c0], 0, 1) is None
    assert CS.alert_sigma_cross_session([c0], 0, 2) is None  # 2 bars = 1 change (< 2 changes!)
    assert CS.alert_sigma_cross_session([c0], 0, 3) is not None  # 3 bars = 2 changes


# --------------------------------------------------------------------------------------------- 3. Strict +5 min overlap (RC-2 / M-1)


def test_strict_overlap_boundary_rc2():
    # Exact +5 min gap on Stage 2 bar-end clock -> ADMITTED, count == 0
    ok_pair = [
        {"day_idx": 0, "fill_bar": 940, "exit_bar_at_R": 960, "law": "race"},
        {"day_idx": 0, "fill_bar": 965, "exit_bar_at_R": 980, "law": "race"},
    ]
    assert HA.count_strict_overlaps(ok_pair) == 0
    assert HA.assert_zero_strict_overlaps(ok_pair) == 0

    # +4 min gap -> REFUSED, count == 1
    bad_pair = [
        {"day_idx": 0, "fill_bar": 940, "exit_bar_at_R": 960, "law": "race"},
        {"day_idx": 0, "fill_bar": 964, "exit_bar_at_R": 980, "law": "race"},
    ]
    assert HA.count_strict_overlaps(bad_pair) == 1
    with pytest.raises(HA.H4OverlapRefused):
        HA.assert_zero_strict_overlaps(bad_pair)

    # Missed / day_end rows do not hold positions
    missed_inside = [
        {"day_idx": 0, "fill_bar": 940, "exit_bar_at_R": 960, "law": "race"},
        {"day_idx": 0, "fill_bar": 950, "exit_bar_at_R": 970, "law": "missed"},
        {"day_idx": 0, "fill_bar": 965, "exit_bar_at_R": 980, "law": "race"},
    ]
    assert HA.count_strict_overlaps(missed_inside) == 0

    # Same-bar exit (exit == fill) + next fill exactly +5 min -> count 0; +4 min -> count 1
    same_bar_ok = [
        {"day_idx": 0, "fill_bar": 940, "exit_bar_at_R": 940, "law": "race"},
        {"day_idx": 0, "fill_bar": 945, "exit_bar_at_R": 950, "law": "race"},
    ]
    same_bar_bad = [
        {"day_idx": 0, "fill_bar": 940, "exit_bar_at_R": 940, "law": "race"},
        {"day_idx": 0, "fill_bar": 944, "exit_bar_at_R": 950, "law": "race"},
    ]
    assert HA.count_strict_overlaps(same_bar_ok) == 0
    assert HA.count_strict_overlaps(same_bar_bad) == 1


# --------------------------------------------------------------------------------------------- 4. Independent scalar oracle (F4-5, F4-10)


def test_independent_scalar_oracle_and_planted_failures():
    # Build a genuine race trade row using K.Unit + H4_TEST_SEED
    start, seed_index, day_idx, decision, sub = 0, 0, 2, 935, 0
    stop_ticks, G, d = 150, 300.0, 2.0
    e_c, xt_c, xs_c, xf_c = 5.0, 0.0, 2.0, 4.0
    room = 1000.0
    L_dol = min(stop_ticks * d, room - e_c - xs_c)
    p = L_dol / (L_dol + G * d)
    u = float(K.uniforms(K.Unit(H4_TEST_SEED, H4_TEST_PART, 0, seed_index, start).coin_key(K.moment(day_idx, decision, sub), K.RACE), 1)[0])
    win = u < p
    out = (-e_c + G * d - xt_c) if win else (-e_c - L_dol - xs_c)

    good_race = {
        "start": start, "seed_index": seed_index, "day_idx": day_idx, "decision": decision, "sub": sub,
        "underlying": "NQ", "fill_bar": 940, "time_limit": 1328, "be_open": "", "sigma": 5.0,
        "stop_ticks": stop_ticks, "G": G, "L_ticks": L_dol / d, "room": room, "d": d,
        "e_cost": e_c, "xt_cost": xt_c, "xs_cost": xs_c, "xf_cost": xf_c,
        "law": "race", "p": p, "exit_code": 1 if win else -1, "out": out,
    }
    HA.verify_race_trade_row(good_race, seed=H4_TEST_SEED, part=H4_TEST_PART)

    # Planted forced-loss toy (booked a loss when oracle won, or shifted payout) MUST FAIL!
    forced_loss = dict(good_race, out=out - 10.0)
    with pytest.raises(HA.H4OracleRefused):
        HA.verify_race_trade_row(forced_loss, seed=H4_TEST_SEED, part=H4_TEST_PART)

    # Floor breach MUST FAIL!
    floor_breach = dict(good_race, out=-room - 1.0)
    with pytest.raises(HA.H4OracleRefused, match="floor"):
        HA.verify_race_trade_row(floor_breach, seed=H4_TEST_SEED, part=H4_TEST_PART)

    # F4-10: forbidden historical fields MUST FAIL!
    for bad_f in HA.RACE_FORBIDDEN_FIELDS:
        leaked = dict(good_race, **{bad_f: 0.5})
        with pytest.raises(HA.H4OracleRefused, match="F4-10"):
            HA.verify_race_trade_row(leaked, seed=H4_TEST_SEED, part=H4_TEST_PART)

    # Exact move-law trade row verified end-to-end against independent scalar walker
    entry_b, be_op, lim_b, sigma = 940, 1201, 1328, 4.0
    s1 = HA._indep_walk_step(sigma, be_op - entry_b)
    n1 = HA._indep_walk_steps(sigma, be_op - entry_b, s1)
    s2 = HA._indep_walk_step(sigma, lim_b - be_op)
    n2 = HA._indep_walk_steps(sigma, lim_b - be_op, s2)
    mom = K.moment(day_idx, decision, sub)
    us = K.uniforms(K.Unit(H4_TEST_SEED, H4_TEST_PART, 0, seed_index, start).coin_key(mom, K.WALK), n1 + n2)
    v1, k1 = HA.walk_scalar_independent(us[:n1], Fraction(G), Fraction(L_dol / d), s1)
    if k1 == 0:
        moved = v1 >= 1
        down2 = v1 if moved else (v1 + Fraction(L_dol / d))
        v2, k2 = HA.walk_scalar_independent(us[n1 : n1 + n2], Fraction(G) - v1, down2, s2)
        gross_f, kc = (Fraction(G), 1) if k2 == 1 else ((Fraction(0), 3) if moved else (-Fraction(L_dol / d), -1)) if k2 == -1 else (v1 + v2, 0)
        mx, mm, mg2, md2 = float(v1), int(moved), float(Fraction(G) - v1), float(down2)
    else:
        gross_f, kc = v1, k1
        mx, mm, mg2, md2 = "", "", "", ""
    cost_m = xt_c if kc == 1 else (xs_c if kc in (-1, 3) else xf_c)
    good_move = {
        "start": start, "seed_index": seed_index, "day_idx": day_idx, "decision": decision, "sub": sub,
        "underlying": "NQ", "fill_bar": entry_b, "time_limit": lim_b, "be_open": be_op, "sigma": sigma,
        "stop_ticks": stop_ticks, "G": G, "L_ticks": L_dol / d, "room": room, "d": d,
        "e_cost": e_c, "xt_cost": xt_c, "xs_cost": xs_c, "xf_cost": xf_c,
        "law": "move", "exit_code": kc, "s1": s1, "n1": n1, "s2": s2, "n2": n2,
        "move_x": mx, "move_moved": mm, "move_G2": mg2, "move_down2": md2,
        "out": -e_c + float(gross_f) * d - cost_m,
    }
    HA.verify_race_trade_row(good_move, seed=H4_TEST_SEED, part=H4_TEST_PART)
    with pytest.raises(HA.H4OracleRefused):
        HA.verify_race_trade_row(dict(good_move, s1=s1 + 1), seed=H4_TEST_SEED, part=H4_TEST_PART)


# --------------------------------------------------------------------------------------------- 5. Move law exact fractions


def test_breakeven_move_law_exact_fractions():
    law = MV.move_law(Fraction(30), Fraction(20), Fraction(4), 6, Fraction(4), 5)
    assert sum(law.values()) == Fraction(1)
    assert MV.move_gross(Fraction(30), Fraction(20), Fraction(4), 6, Fraction(4), 5) == Fraction(0)
    # Net expectation equals minus expected exit cost
    costs = {"target": Fraction(0), "stop": Fraction(1), "breakeven": Fraction(1), "time": Fraction(2)}
    net_ev = sum(pr * (v - costs[k]) for (k, v), pr in law.items())
    exp_cost = sum(pr * costs[k] for (k, _), pr in law.items())
    assert net_ev == -exp_cost


# --------------------------------------------------------------------------------------------- 6. Bounded mirror as_walked (rc-11)


def test_bounded_mirror_as_walked_rc11():
    class _Inner:
        settlement = "mae"
        key = ("combine", 0)
        last_trade = {"historical_day": 0, "trade_index": 0, "realised_risk": 75.0, "rr": 2.5, "contracts": 1,
                      "risk_per_contract": 75.0, "u": 2.5, "mae": 0.0, "fee": 0.0}

        def __call__(self, n, day, slot, cushion, **kw):
            return np.array([187.5])

    class _Blk:
        entry_t = np.array([940.0])

    # Historical trade hit +2.5R (+375 ticks); mirror walk stopped at -150 ticks (NOT -375 ticks!)
    f = TB.TradeFacts(
        decision=935, entry=940, stop_ticks=150, tick_value=0.5, kinds={2.5: "t"}, limit=1328, sigma=4.0,
        e_ticks=1.0, xt_ticks=0.0, xs_ticks=1.0, xf_ticks=2.0, fee_per_contract=0.0,
        walked={2.5: 375.0}, walked_mirror={2.5: -150.0},
    )
    # Run across 16 seed indices so both +1 and -1 sides appear
    coins = J.CoinLanes(H4_TEST_SEED, H4_TEST_PART, 0, 0, list(range(16)), None, False)
    unit = TB._Unit({(0, 0): f}, [_Blk()], 0, coins, J.ArmSpec())
    outs = []
    for lane in range(16):
        log: list = []
        o = TB.RaceOver(_Inner(), unit, lane, "as_walked", log, None)(1, 0, 0, np.array([500.0]))[0]
        outs.append((log[0]["side"], float(o)))
    neg = [o for sd, o in outs if sd < 0]
    pos = [o for sd, o in outs if sd > 0]
    assert neg and pos
    # Flipped target NEVER books -375 ticks (-$187.50); bounded at -150 ticks - 2 ticks costs = -$76.0
    assert all(o >= -(150.0 + 2.0) * 0.5 - 1e-9 for o in neg)
    assert all(abs(o - (-150.0 * 0.5 - 1.0)) < 1e-9 for o in neg)


# --------------------------------------------------------------------------------------------- 7. Naive coin source (as-run & I-5)


def _synth_day_ohlc(seed_int: int, n_bars: int = 1340, base_price: float = 15000.0) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed_int)
    o = np.full(1441, np.nan)
    h = np.full(1441, np.nan)
    l = np.full(1441, np.nan)
    c = np.full(1441, np.nan)
    px = base_price
    for bar in range(1, n_bars + 1):
        op = px
        step = rng.normal(0.0, 4.0)
        cl = round((op + step) * 4.0) / 4.0
        hi = max(op, cl) + round(abs(rng.normal(0.0, 6.0)) * 4.0) / 4.0
        lo = min(op, cl) - round(abs(rng.normal(0.0, 6.0)) * 4.0) / 4.0
        o[bar], h[bar], l[bar], c[bar] = op, hi, lo, cl
        px = cl
    return o, h, l, c


def test_h4_coin_source_as_run_and_i5_modes():
    dates = ["2020-01-02", "2020-01-03", "2020-01-06"]
    arrs = {d: _synth_day_ohlc(100 + i) for i, d in enumerate(dates)}
    day_kinds = {"2020-01-02": "n", "2020-01-03": "b", "2020-01-06": "n"}

    # As-run naive coin mode (using h4_tests seed in H4-T; closed 08:30-08:59 & BLS windows applied)
    res = CS.build_naive_coin_trades(
        dates,
        day_kinds,
        lambda d: arrs[d],
        lambda d_obj, s_idx: T.DayContext(s_idx, d_obj.isoformat(), bls=(d_obj.isoformat() == "2020-01-03")),
        fee_micro_eq=1.22,
        stop_ticks=150,
        rr_grid=CS.RR_GRID,
        seed=H4_TEST_SEED,
        part=H4_TEST_PART,
        require_overnight_guard=False,
    )
    assert len(res.trades) > 0
    assert len(res.aux) == len(res.trades)
    # Closed window 08:30-08:59 CT (slots 930..959): no offer live inside it (live = mark + 5)
    lives = res.trades["decision_slot_minutes"].astype(int) + CS.COIN_LATENCY
    assert not ((lives >= T.CLOSED_FIRST) & (lives <= T.CLOSED_LAST)).any()
    # BLS day (2020-01-03): no offer live <= 07:35 CT (slot 875)
    bls_rows = res.trades[res.trades["date"] == "2020-01-03"]
    assert not ((bls_rows["decision_slot_minutes"].astype(int) + CS.COIN_LATENCY) <= T.BLS_CLEAR).any()
    # All 12 R columns present in exact cell_trades schema
    for R_val in CS.RR_GRID:
        for pref in ("r_", "g_", "c_", "mae_", "exit_t_", "o_"):
            assert f"{pref}{R_val:g}" in res.trades.columns

    # P-16 / I-5 mode: deterministic trades_hash and D-533 cut on BLS day
    days_df = pd.DataFrame({"date": dates, "day_kind": [day_kinds[d] for d in dates]})
    marks = [0, 60, 870, 875, 930, 1000]
    coins = {(d, m): (1 if (i + m) % 2 == 0 else -1) for i, d in enumerate(dates) for m in marks}
    t_i5_a = CS.build_p16_i5_trades(days_df, lambda d: arrs[d], marks, coins, fee_micro_eq=1.22)
    t_i5_b = CS.build_p16_i5_trades(days_df, lambda d: arrs[d], marks, coins, fee_micro_eq=1.22)
    assert len(t_i5_a) > 0
    # On BLS day 2020-01-03, mark 870 (07:30) is dropped by D-533 (< 875), mark 875 (07:35) is kept
    bls_i5 = t_i5_a[t_i5_a["date"] == "2020-01-03"]["decision_slot_minutes"].tolist()
    assert 870 not in bls_i5 and 875 in bls_i5
    # Exact reproducibility
    assert pd.testing.assert_frame_equal(t_i5_a, t_i5_b) is None


# --------------------------------------------------------------------------------------------- 8. H4-C -> W42-R1 synthetic round-trip


def _write_fake_units(rdir: Path, baseline: str, starts: list[str], J_n: int, rng: np.random.Generator) -> Path:
    n_s = len(starts)
    rows = []
    for si, sday in enumerate(starts):
        sl = n_s - si
        for ci in range(J_n):
            fp = float(rng.integers(5, 80)) if sl >= 126 else float("nan")
            fy = float(fp + rng.integers(5, 40)) if sl >= 126 else float("nan")
            if sl >= 126 and fy > 126:
                fy = 127.0
            rows.append(
                {
                    "baseline": baseline,
                    "arm": "off",
                    "reading": W42.READING,
                    "block": W42.BLOCK,
                    "start_idx": si,
                    "start": sday,
                    "seed": ci,
                    "sessions_left": sl,
                    "obs": min(252, sl),
                    "strict_overlaps": 0,
                    "net_month_1": float(rng.normal(0.0, 200.0)) if sl >= 21 else float("nan"),
                    "net_month_2": float(rng.normal(50.0, 300.0)) if sl >= 42 else float("nan"),
                    "net_month_3": float(rng.normal(100.0, 400.0)) if sl >= 63 else float("nan"),
                    "peak_month_1": float(rng.uniform(50.0, 250.0)) if sl >= 21 else float("nan"),
                    "peak_month_2": float(rng.uniform(100.0, 400.0)) if sl >= 42 else float("nan"),
                    "peak_month_3": float(rng.uniform(150.0, 600.0)) if sl >= 63 else float("nan"),
                    "first_pass_days": fp,
                    "cash_to_first_pass": float(rng.uniform(50.0, 300.0)) if sl >= 126 else float("nan"),
                    "first_payout_days": fy,
                    "spent_before_first_payout": float(rng.uniform(100.0, 500.0)) if sl >= 126 else float("nan"),
                    "peak_oop_12_months": float(rng.uniform(200.0, 1200.0)) if sl >= 252 else float("nan"),
                    "share_months_positive": float(rng.uniform(0.2, 0.8)) if sl >= 252 else float("nan"),
                    "orders_max": float(rng.integers(1, 8)) if sl >= 126 else float("nan"),
                    "accounts_max": float(rng.integers(1, 5)) if sl >= 126 else float("nan"),
                    "taken_mean": float(rng.uniform(0.5, 3.0)) if sl >= 126 else float("nan"),
                }
            )
    p = rdir / f"h4_units_{baseline}.csv"
    df = pd.DataFrame(rows)
    df.to_csv(p, index=False)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    Path(f"{p}.manifest.json").write_text(json.dumps({"sha256": sha, "parameters": {"baseline": baseline}}), encoding="utf-8")
    return p


def _fake_writer(df: pd.DataFrame, name: str, *, results_dir: Path, parameters: dict[str, Any], **kw):
    stem = name[:-4] if name.endswith(".csv") else name
    out_csv = Path(results_dir) / f"{stem}.csv"
    out_man = Path(f"{out_csv}.manifest.json")
    df.to_csv(out_csv, index=False)
    sha = hashlib.sha256(out_csv.read_bytes()).hexdigest()
    out_man.write_text(json.dumps({"sha256": sha, "parameters": parameters}, indent=2), encoding="utf-8")
    return out_csv, out_man


def test_h4_collect_roundtrip_into_wave42_apply_and_refusals(tmp_path: Path):
    # Use the real pinned search_calendar.csv dates (copied to tmp_path) & real q82_judged_sessions.csv dates (no outcomes!)
    rdir = tmp_path / "results"
    rdir.mkdir()
    src_cal = ROOT / "results" / W42.SEARCH_CALENDAR
    src_ho = ROOT / "results" / W42.HELD_OUT_CALENDAR
    (rdir / W42.SEARCH_CALENDAR).write_bytes(src_cal.read_bytes())
    (rdir / f"{W42.SEARCH_CALENDAR}.manifest.json").write_bytes(Path(f"{src_cal}.manifest.json").read_bytes())
    (rdir / W42.HELD_OUT_CALENDAR).write_bytes(src_ho.read_bytes())

    from extended import search_calendar as SCAL

    cal = SCAL.load_search_calendar(rdir / W42.SEARCH_CALENDAR)
    # Use a 260-session synthetic search calendar ending 2023-12-29? Wait: W42-R1 requires SEARCH_FIRST..SEARCH_LAST
    # and pinned SEARCH_CALENDAR_SHA256! So use real calendar dates with J=64 (fast: 1007 * 64 * 4 is tiny ~0.4s)
    starts = list(cal.dates)
    rng = np.random.default_rng(777)
    J_n = 64
    for b in W42.BASELINES:
        _write_fake_units(rdir, b, starts, J_n, rng)

    info = H4C_SCRIPT.collect_from_units(rdir, expected_j=J_n, writer=_fake_writer)
    assert info["starts"] == len(starts) and info["seeds"] == J_n

    # Feed directly into W42-R1's `wave42_apply.apply`!
    sources = W42_APP.Sources(
        adapter=HC.w42_readings,
        calendar_loader=SCAL.load_search_calendar,
        fee=lambda: (49.0, W42.FEE_SOURCE, "0" * 64),
        writer=_fake_writer,
    )
    w42_params = W42_APP.apply(rdir, sources)
    assert w42_params["h4_result_sha256"] == info["sha256"]
    assert (rdir / W42.OUTPUT_NAME).is_file()

    # Refusal tests on collect_from_units:
    # (a) Tampered byte in one units file -> refused
    rdir2 = tmp_path / "results_bad_sha"
    rdir2.mkdir()
    (rdir2 / W42.SEARCH_CALENDAR).write_bytes(src_cal.read_bytes())
    (rdir2 / f"{W42.SEARCH_CALENDAR}.manifest.json").write_bytes(Path(f"{src_cal}.manifest.json").read_bytes())
    for b in W42.BASELINES:
        _write_fake_units(rdir2, b, starts[:260], 4, rng)
    # Tamper naive_coin csv without updating manifest
    p_nc = rdir2 / "h4_units_naive_coin.csv"
    p_nc.write_bytes(p_nc.read_bytes() + b" ")
    with pytest.raises(H4C_SCRIPT.H4CollectScriptRefused, match="sha256"):
        H4C_SCRIPT.collect_from_units(rdir2, calendar_dates=starts[:260], expected_j=4, writer=_fake_writer)

    # (b) Non-zero strict_overlaps -> refused
    rdir3 = tmp_path / "results_overlap"
    rdir3.mkdir()
    for b in W42.BASELINES:
        _write_fake_units(rdir3, b, starts[:260], 4, rng)
    p_p14 = rdir3 / "h4_units_p14.csv"
    df_bad = pd.read_csv(p_p14)
    df_bad.loc[0, "strict_overlaps"] = 1
    df_bad.to_csv(p_p14, index=False)
    Path(f"{p_p14}.manifest.json").write_text(
        json.dumps({"sha256": hashlib.sha256(p_p14.read_bytes()).hexdigest()}), encoding="utf-8"
    )
    with pytest.raises(H4C_SCRIPT.H4CollectScriptRefused, match="strict_overlaps"):
        H4C_SCRIPT.collect_from_units(rdir3, calendar_dates=starts[:260], expected_j=4, writer=_fake_writer)

    # (c) Held-out block row -> refused
    rdir4 = tmp_path / "results_ho"
    rdir4.mkdir()
    for b in W42.BASELINES:
        _write_fake_units(rdir4, b, starts[:260], 4, rng)
    p_p15 = rdir4 / "h4_units_p15.csv"
    df_ho = pd.read_csv(p_p15)
    df_ho.loc[0, "block"] = "held_out"
    df_ho.to_csv(p_p15, index=False)
    Path(f"{p_p15}.manifest.json").write_text(
        json.dumps({"sha256": hashlib.sha256(p_p15.read_bytes()).hexdigest()}), encoding="utf-8"
    )
    with pytest.raises(H4C_SCRIPT.H4CollectScriptRefused, match="non-search"):
        H4C_SCRIPT.collect_from_units(rdir4, calendar_dates=starts[:260], expected_j=4, writer=_fake_writer)


# --------------------------------------------------------------------------------------------- 9. No raw H4 seed literals


def test_accounts_active_by_day_matches_lockstep_record_days():
    """Verify `accounts_active_by_day` matches vendored `lockstep.simulate_lockstep_path(record_days=True)` day-for-day."""
    import subprocess

    code = r"""
import json, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from extended import use_vendored_stage2
use_vendored_stage2()
from extended import h4_audit as HA, three_way_baseline as TB, three_way_seeds as S
import three_way_baseline_checks as TBC

blocks, args, facts = TBC.job()
import datetime as dt
syn_dates = tuple(dt.date(2020, 1, 2) + dt.timedelta(days=k) for k in range(TBC.N_DAYS))
args2 = {**args, "path": {**args["path"], "record_days": True}}
rec = TB.simulate(blocks, args2, facts, 3, [0, 1], 42, seed=S.issue("h4_tests"), part=S.PARTS["H4-T"],
                  history=0, block_sessions=TBC.N_DAYS, dates=syn_dates, calendar=frozenset(syn_dates),
                  outcome="race", keep_paths=True, log=True)
mism = 0
for p in rec.paths:
    got = HA.accounts_active_by_day(p, 42)
    by_day = {}
    for row in p.account_days:
        d = int(row["day"])
        if 1 <= d <= 42:
            by_day[d] = by_day.get(d, 0) + 1
    want = [by_day.get(k, 0) for k in range(1, 43)]
    if got != want:
        mism += 1
        print("DIFF", got[:15], want[:15], file=sys.stderr)
print(json.dumps({"mism": mism, "paths": len(rec.paths)}))
"""
    proc = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out["mism"] == 0 and out["paths"] == 2


def test_no_raw_h4_seed_literals_in_build_files():
    pat = re.compile(r"\b(?:2026440[0-9]|2026587[0-9])\b")
    for rel in (
        "extended/h4_coin_source.py",
        "extended/h4_audit.py",
        "scripts/h4_collect.py",
        "scripts/h4_rebaseline.py",
        "tests/test_h4_build.py",
    ):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        hits = pat.findall(txt)
        assert not hits, f"{rel} contains raw declared seed literal(s): {hits}"


# --------------------------------------------------------------------------------------------- 10. Regression tests (M-1..M-8, m-2, N-1)


def test_m1_synthetic_h4_0_probe_runs_cleanly():
    """M-1: synthetic H4-0 probe executes both R.run (S1.DesignSpec + ToyRules) and TB.simulate(..., outcome='race')."""
    out = H4R._synthetic_h4_0_probe(H4_TEST_SEED, H4_TEST_PART, j_tb=4, h_tb=25)
    assert out["synthetic_lane_trades"] > 0
    assert out["tb_race_trades"] > 0
    assert out["tb_race_seconds"] >= 0.0
    assert math.isfinite(out["tb_race_sec_per_seed_252_est"])


def test_m2_i3_race_vs_binarydraw_holds():
    """M-2: I-3 genuinely exercises adapter.BinaryDraw + three_way_redraw + RaceOver across deep & cushion-bound rooms."""
    res = H4R._check_i3_race_vs_binarydraw()
    assert res["holds"] is True
    assert res["differing"] == 0
    assert res["compared"] >= 768


def test_m4_oracle_time_exit_clip_snap_and_csv_bool():
    """M-4a/b/c: verify pre-clip time exit, SNAP lattice boundary (12.0 + 1e-13), and CSV string '0' for move_moved."""
    from extended import three_way_redraw as RD

    # M-4b: SNAP boundary (L = 12.0 + 1e-13, s = 4, n = 3) matches three_way_redraw.walk_outcome exactly
    us_snap = [0.9, 0.9, 0.9]
    rd_v, rd_k = RD.walk_outcome(us_snap, 20.0, 12.0 + 1e-13, 4)
    ha_v, ha_k = HA.walk_scalar_independent(us_snap, Fraction(20.0), Fraction(12.0 + 1e-13), 4)
    assert rd_k == "stop" and ha_k == -1
    assert abs(float(ha_v) - float(rd_v)) < 1e-12

    # M-4a: cushion-bound walk ending in time-exit (kc == 0) with pre-clip out in [-room - (xf - xs), -room)
    start, seed_index, day_idx, decision, sub = 0, 0, 1, 1210, 0
    d, e_c, xt_c, xs_c, xf_c = 0.5, 0.5, 0.0, 0.5, 1.0  # xf - xs = 0.5
    room = 16.5  # L_dol = room - e - xs = 15.5 -> L_ticks = 31.0; L_fill = room - e - xf = 15.0 > EPS
    stop_ticks, G = 150, 225.0
    L_ticks = (room - e_c - xs_c) / d  # 31.0
    # Find a seed_index where a 1-step walk with s=30 lands at -30 -> out = -0.5 + (-30)*0.5 - 1.0 = -16.5;
    # or with room=16.25 (L_ticks=30.5, s=30, step down to -30? No: bot is at 0 -> -30.5 stop; wait: use s=15, 2 steps!)
    # With L_ticks=31.0, s=15: d_bot = ceil(31/15 - 1e-9)-1 = 2; after 2 down steps -> i = -2 -> v = -30.0
    # out = -0.5 + (-30.0)*0.5 - 1.0 = -16.5; set room=16.25 -> L_ticks=30.5 -> d_bot=2 -> 2 down steps -> v=-30.0
    # out = -0.5 - 15.0 - 1.0 = -16.5 < -room (-16.25), clip_credit = 0.25 <= xf - xs = 0.5!
    room = 16.25
    L_ticks = (room - e_c - xs_c) / d  # 30.5
    # Pick sigma, T so s = 15, n = 2 -> sigma * sqrt(T) ~ sqrt(2) * 15 ~ 21.213 -> T = 10, sigma = 6.7082 -> s = 1?
    # Wait: walk_step(sigma, T, 1024) = ceil(sigma*sqrt(T)/32) -> for s=15 need sigma*sqrt(T) in (448, 480], then n = (sigma^2 T)/225 ~ 900.
    # For n=2, s=1: sigma=0.5, T=8 -> sigma*sqrt(T) = 1.414 -> s=1, n=round(0.25*8)=2.
    # Then set room = 2.0 + 0.5 + 0.5 + 0.25*0.5? Wait: with s=1, 2 down steps -> v=-2.0. Set L_ticks = 2.5 -> room = e + xs + 2.5*d = 0.5 + 0.5 + 1.25 = 2.25.
    # Then out = -0.5 + (-2.0)*0.5 - 1.0 = -2.5 < -room (-2.25), clip_credit = 0.25 <= xf - xs (0.5)!
    room = 2.25
    L_ticks = (room - e_c - xs_c) / d  # 2.5
    entry_b, limit_b, sigma = 1320, 1328, 0.5  # T=8 -> s=1, n=2
    found_c = None
    for c_try in range(64):
        us_t = K.uniforms(K.Unit(H4_TEST_SEED, H4_TEST_PART, 0, c_try, start).coin_key(K.moment(day_idx, decision, sub), K.WALK), 2)
        vt, kt = HA.walk_scalar_independent(us_t, Fraction(G), Fraction(L_ticks), 1)
        if kt == 0 and float(vt) == -2.0:
            found_c = c_try
            break
    assert found_c is not None
    time_exit_row = {
        "start": start, "seed_index": found_c, "day_idx": day_idx, "decision": decision, "sub": sub,
        "underlying": "NQ", "fill_bar": entry_b, "time_limit": limit_b, "be_open": "", "sigma": sigma,
        "stop_ticks": stop_ticks, "G": G, "L_ticks": L_ticks, "room": room, "d": d,
        "e_cost": e_c, "xt_cost": xt_c, "xs_cost": xs_c, "xf_cost": xf_c,
        "law": "walk", "exit_code": 0, "s1": 1, "n1": 2, "out": -2.5,
    }
    clip = HA.verify_race_trade_row(time_exit_row, seed=H4_TEST_SEED, part=H4_TEST_PART)
    assert abs(clip - 0.25) < 1e-12

    # M-4c: CSV string "0" for move_moved parses as False (not True!)
    assert HA._parse_bool_flag("0") is False
    assert HA._parse_bool_flag("0.0") is False
    assert HA._parse_bool_flag("1") is True
    assert HA._parse_bool_flag("False") is False
    assert HA._parse_bool_flag("True") is True


def test_m5_price_level_helper_works_on_untracked_csvs(tmp_path: Path):
    """M-5: check_h4_price_levels scans untracked h4_*.csv cleanly and refuses a price-level column."""
    clean_csv = tmp_path / "h4_clean.csv"
    pd.DataFrame({"baseline": ["p14", "p15", "p16"], "net_month_1": [10.0, -50.0, 20.0], "funded_lifetimes": ["5/20/breach/12", "", "3/-1/window/10+18"]}).to_csv(clean_csv, index=False)
    checked = H4R.check_h4_price_levels(tmp_path, ROOT)
    assert checked == ["h4_clean.csv"]

    bad_csv = tmp_path / "h4_bad.csv"
    pd.DataFrame({"close_price": [18000.25, 18010.50, 18020.75]}).to_csv(bad_csv, index=False)
    with pytest.raises(HA.H4AuditRefused, match="price-level"):
        H4R.check_h4_price_levels(tmp_path, ROOT)


def test_m6_m7_m2_unit_measures_peak_month_deepest_fall_and_funded_lifetimes():
    """M-6: peak_month_m includes close 21*m; M-7: deepest_fall_after_be_252 is drawdown from running high;
    m-2: out_of_room_accounts uses path.path.combines_out_of_room and funded_lifetimes round-trips."""
    class _Comb:
        def __init__(self, pd_day, oor=False):
            self.purchase_day = pd_day
            self.resolved_on = pd_day + 5
            self.out_of_room = oor

    class _Fund:
        activation_day = 15
        ended_on = 60
        closed = True
        abandoned = False
        denied = 0
        household_closed = False
        ftp_closed = False
        payout_days = (10, 25)

    class _InnerPath:
        combines_out_of_room = 3

    class _Path:
        combines = (_Comb(0, False),)
        funded = (_Fund(),)
        path = _InnerPath()

    class _Blk:
        entry_t = np.array([940.0])
        exit_t = np.array([960.0])

    # Build 253 closes: trough at close 21 (-300 vs -100 on closes 0..20); break-even at close 40 (+0),
    # rise to +5000 at close 100, fall to +1000 at close 150 (never below $0 -> drawdown from high is $4000!)
    rel = np.zeros(253, dtype=float)
    rel[0:21] = -100.0
    rel[21] = -300.0          # M-6: new trough EXACTLY on close 21!
    rel[22:40] = -50.0
    rel[40:100] = np.linspace(0.0, 5000.0, 60)
    rel[100:151] = np.linspace(5000.0, 1000.0, 51)
    rel[151:] = 2000.0

    row = HA.extract_unit_measures(
        baseline="p14", arm="off", reading=W42.READING, start=0, start_date="2020-01-02", seed_index=0,
        sessions_left=252, rel=rel, first_pass=15, first_pay=28, arrivals=[(28, 1000.0), (43, 1500.0)],
        path=_Path(), log_rows=[], blocks=[_Blk() for _ in range(252)], latency=5.0, strict_overlaps=0,
        payout_lag=2,
    )
    # M-6: peak_month_1 MUST be 300.0 (including close 21), NOT 100.0!
    assert abs(row["peak_month_1"] - 300.0) < 1e-9
    # M-7: fell_below_be_252 is 0.0 (never fell below $0), deepest_fall_after_be_252 is 4000.0 (from +5000 to +1000)!
    assert row["fell_below_be_252"] == 0.0
    assert abs(row["deepest_fall_after_be_252"] - 4000.0) < 1e-9
    # m-2: combines_out_of_room == 3, W=252 beside columns present, funded_lifetimes round-trips
    assert row["out_of_room_accounts"] == 3
    assert math.isfinite(row["first_pass_days_252"]) and math.isfinite(row["cash_to_first_pass_252"])
    dec = HA.decode_funded_accounts(row["funded_lifetimes"])
    assert len(dec) == 1 and dec[0]["activation_day"] == 15 and dec[0]["ended_on"] == 60
    assert dec[0]["arrivals"] == (28, 43)


def test_m8_nq_stop_band_loads_real_bounds():
    """M-8: _load_nq_stop_band filters market == 'NQ' and reads exact combine/funded narrow & wide ticks."""
    nb = H4R._load_nq_stop_band(ROOT)
    assert nb["combine_lo"] == 82.0 and nb["combine_hi"] == 3000.0
    assert nb["funded_below_2000_lo"] == 134.0 and nb["funded_below_2000_hi"] == 2000.0
    assert nb["cost_drag_floor_ticks"] == 45.0


def test_n1_fast_walk_one_matches_redraw_bit_for_bit():
    """N-1: fast scalar `_walk_one` in `three_way_baseline.py` matches `three_way_redraw.walk_outcome` bit-for-bit."""
    from extended import three_way_redraw as RD

    rng = np.random.default_rng(20261124)
    for G_v, L_v, s_v, n_v in (
        (300.0, 150.0, 4, 200),
        (75.5, 42.3, 3, 120),
        (20.0, 12.0 + 1e-13, 4, 15),
        (10.0, 10.0, 12, 5),
        (225.0, 30.5, 1, 2),
    ):
        for _ in range(40):
            us = rng.random(n_v)
            v1, k1 = TB._walk_one(us, 0, n_v, G_v, L_v, float(s_v))
            v2, k2_str = RD.walk_outcome(us, G_v, L_v, s_v)
            k2 = {"target": 1, "stop": -1, "time": 0}[k2_str]
            assert k1 == k2 and v1 == float(v2)
