"""Q-188b: H4's fixes after the audit (`docs/audits/AUDIT_E285_E288_2026-11-26.md`) and the red team's c2 note
(`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md`). Synthetic data only: no bar, no held-out read, no write under
`results/`. Every random draw here is a child of the `h4_tests` role (part H4-T, or its `test`-kind keys); no literal
seed.

Each test names the finding it pins and is written to fail on the defect it guards (a positive control beside it):

- F-3: a zero-dispersion window (a locked market) is told apart from "fewer than two changes"; the old value of every
  other alert is unchanged bit for bit; the blocks are rebuilt for either reason.
- B-1: the red team's probe -- an account breached at close 200 read at W = 126 is open (censored), one payout.
- F-2 / M-3 / m-g: the nested-cut comparison catches a planted look-ahead in the coin's run mode, compares raw against
  raw, and every DayBlock field.
- B-2 / m-4: the exact-run classifier's kinds, its sum equal to the m-4 count, and the runner's chunk on the synthetic
  job (in its own process: the vendored engine) -- whose oracle now re-derives every input (m-e).
- m-e: planted wrong G, cost, d, fee, room and R refused; D-324's fee formula held to the vendored one.
- m-f, M-1, N-1 (twin, one-tick arming, the key guard), rc-3, F-6, F-8, F-13, m-h, m-i, the worker count.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
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
from extended import journey_measures as JM  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import walker as W  # noqa: E402
from scripts import h4_exact_diff_classify as XD  # noqa: E402
from scripts import h4_rebaseline as H4R  # noqa: E402
from scripts import h4_worker_identity as WID  # noqa: E402

H4_TEST_SEED = S.issue("h4_tests")
H4_TEST_PART = S.PARTS["H4-T"]
#: this file's `test`-kind ids under the h4_tests role (ids, not seeds)
_RNG_IDS = {"sigma": 1881, "synth_days": 1882, "classify": 1883}


def _rng(name: str, rep: int = 0) -> np.random.Generator:
    return np.random.default_rng(K.seed_key(H4_TEST_SEED, "test", test=_RNG_IDS[name], replicate=int(rep)))


# --------------------------------------------------------------------------------------------- F-3: the sigma drop


def _old_sigma(day_closes, day_idx, decision, lookback=60, tick=0.25):
    """`alert_sigma_cross_session` exactly as it stood at 31c507e (the reference for the value-unchanged test)."""
    n_need, d, dec = int(lookback), int(day_idx), int(decision)
    collected, changes, cur_d = 0, [], d
    while cur_d >= 0 and collected < n_need:
        arr = np.asarray(day_closes[cur_d], dtype=float)
        hi = min(dec, len(arr) - 1) if cur_d == d else (len(arr) - 1)
        if hi >= 1:
            sub = arr[1: hi + 1]
            idx = np.flatnonzero(~np.isnan(sub))
            if idx.size:
                need = n_need - collected
                if idx.size > need:
                    idx = idx[-need:]
                bars = idx + 1
                cs = arr[bars]
                collected += int(bars.size)
                if bars.size >= 2:
                    changes.append((np.diff(cs) / float(tick)) / np.sqrt(np.diff(bars).astype(float)))
        cur_d -= 1
    if not changes:
        return None
    all_ch = np.concatenate(changes)
    if all_ch.size < 2:
        return None
    sd = float(np.std(all_ch, ddof=1))
    if not (math.isfinite(sd) and sd > 0.0):
        rms = float(math.sqrt(float(np.mean(all_ch * all_ch))))
        return rms if (math.isfinite(rms) and rms > 0.0) else None
    return sd


def _closes(rng: np.random.Generator, n: int = 1330, gaps: float = 0.0) -> np.ndarray:
    c = np.full(1441, np.nan)
    c[1:n + 1] = 15000.0 + np.round(np.cumsum(rng.normal(0.0, 2.0, n)) * 4.0) / 4.0
    if gaps:
        drop = rng.random(n) < gaps
        c[1:n + 1][drop] = np.nan
    return c


def test_f3_zero_dispersion_is_not_fewer_than_two_changes():
    rng = _rng("sigma")
    day0 = _closes(rng)
    locked = _closes(rng)
    locked[1:301] = 14000.0                      # a locked market: one price printed for five hours
    locked[150:170] = np.nan                     # with missing minutes inside the lock
    days = [day0, locked]
    # inside the lock: 60 bars behind the alert, all one price -> zero dispersion, NOT "fewer than two changes"
    r = CS.alert_sigma_detail(days, 1, 240)
    assert r.sigma is None and r.reason == CS.SIGMA_ZERO
    assert r.n_bars == 60 and r.n_changes >= 2 and r.n_nonzero == 0 and r.sessions_read == 1
    # the store's first minutes: the declared drop
    r0 = CS.alert_sigma_detail(days, 0, 2)
    assert r0.sigma is None and r0.reason == CS.SIGMA_LT_2 and r0.n_changes == 1
    # early in the lock the window reaches the previous session: a real sigma
    r1 = CS.alert_sigma_detail(days, 1, 30)
    assert r1.reason == CS.SIGMA_OK and r1.sigma > 0 and r1.sessions_read == 2
    # the wrapper's value is unchanged from 31c507e at every alert, the None cases included
    for d_i, dec in [(1, 240), (0, 2), (0, 0), (1, 30), (1, 0), (1, 301)] + [(int(d), int(m)) for d, m in zip(
            rng.integers(0, 2, 300), rng.integers(0, 1331, 300))]:
        assert CS.alert_sigma_cross_session(days, d_i, dec) == _old_sigma(days, d_i, dec)
    # a gappy day too
    gappy = [_closes(rng, gaps=0.4), _closes(rng, gaps=0.7)]
    for dec in range(0, 1331, 7):
        assert CS.alert_sigma_cross_session(gappy, 1, dec) == _old_sigma(gappy, 1, dec)


def _ohlc_from_closes(c: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    o = np.full_like(c, np.nan)
    prev = np.nan
    for x in range(1, len(c)):
        if not math.isnan(c[x]):
            o[x] = c[x] if math.isnan(prev) else prev
            prev = c[x]
    h = np.fmax(o, c) + np.where(np.isnan(c), np.nan, 0.5)
    lo = np.fmin(o, c) - np.where(np.isnan(c), np.nan, 0.5)
    return o, h, lo, c


def _locked_days() -> tuple[list[str], dict[str, tuple]]:
    rng = _rng("synth_days")
    dates = ["2020-03-09", "2020-03-10", "2020-03-11", "2020-03-12", "2020-03-13"]
    arrs = {}
    for k, d in enumerate(dates):
        c = _closes(rng)
        if k == 1:
            c[1:301] = 13500.0                     # the lock on the second day
            c[301:] = c[301:] - c[301] + 13500.0
        arrs[d] = _ohlc_from_closes(c)
    return dates, arrs


def _coin(dates, arrs):
    return CS.build_naive_coin_trades(
        dates, {d: "n" for d in dates}, lambda d: arrs[d],
        lambda d_obj, s_idx: T.DayContext(s_idx, d_obj.isoformat()),
        fee_micro_eq=1.22, seed=H4_TEST_SEED, part=H4_TEST_PART, require_overnight_guard=False)


def test_f3_builder_counts_the_two_reasons_apart_and_lists_dates_only():
    dates, arrs = _locked_days()
    res = _coin(dates, arrs)
    c = res.counts
    assert c["offers_dropped_sigma_lt_2"] == 1                      # 17:00 CT of the store's first day only
    assert c["offers_dropped_sigma_zero"] > 0                       # the lock: undeclared, now counted apart
    rows = c["dropped_sigma_rows"]
    assert len(rows) == c["offers_dropped_sigma_lt_2"] + c["offers_dropped_sigma_zero"]
    assert {r["reason"] for r in rows} == {CS.SIGMA_LT_2, CS.SIGMA_ZERO}
    assert all(r["date"] == "2020-03-10" for r in rows if r["reason"] == CS.SIGMA_ZERO)
    assert all(r["date"] == "2020-03-09" and r["decision_slot_minutes"] == 0 for r in rows if r["reason"] == CS.SIGMA_LT_2)
    for r in rows:                                                  # dates, minutes and counts -- never a price
        assert set(r) == {"date", "decision_slot_minutes", "decision_ct", "reason", "n_bars", "n_changes",
                          "n_nonzero_changes", "sessions_read"}
        assert ":" in r["decision_ct"] and all(isinstance(r[k], int) for k in ("n_bars", "n_changes"))
    # a dropped alert is never in the schedule
    kept = set(zip(res.trades["date"], res.trades["decision_slot_minutes"].astype(int)))
    assert not any((r["date"], r["decision_slot_minutes"]) in kept for r in rows)


def test_f3_blocks_rebuilt_for_either_reason():
    assert H4R.needs_block_rebuild({"dropped_sigma_lt_2": 0, "dropped_sigma_zero": 309})
    assert H4R.needs_block_rebuild({"dropped_sigma_lt_2": 1, "dropped_sigma_zero": 0})
    assert not H4R.needs_block_rebuild({"dropped_sigma_lt_2": 0, "dropped_sigma_zero": 0})


def test_f3_f6_registered_facts_split_reasons_and_years():
    """`_build_facts_for_trades` (the registered baselines' path) on the coin's synthetic trades without their aux:
    the sigma is recomputed there, the lock's alerts dropped as zero dispersion, and the kept schedule hashed."""
    dates, arrs = _locked_days()
    res = _coin(dates, {d: (a if k != 1 else _ohlc_from_closes(_closes(_rng("synth_days", 7))))
                        for k, (d, a) in enumerate(arrs.items())})            # a schedule built on unlocked bars ...
    kept, facts, st = H4R._build_facts_for_trades(res.trades, dates, arrs, tick_value=0.5, entry_ticks=1.0,
                                                  rr_cols=CS.RR_GRID)         # ... its sigma read on the locked ones
    # the coin had already dropped its own 17:00 CT alert of the first day, so only the lock's are left to drop here
    assert st["dropped_sigma_zero"] > 0 and st["dropped_sigma_lt_2"] == 0
    assert len(kept) == len(res.trades) - st["dropped_sigma_zero"] - st["dropped_sigma_lt_2"] == len(facts)
    assert st["kept_trades"] == len(kept) and len(st["kept_trades_sha256"]) == 64
    yrs = [r["date"] for r in st["dropped_sigma_rows"]]
    assert H4R._scope_count(yrs, "2020") == len(yrs) and H4R._scope_count(yrs, "2021") == 0
    assert H4R._scope_count(yrs, "all") == len(yrs)


# --------------------------------------------------------------------------------------------- B-1: (31) at W = 126


def test_b1_funded_account_read_at_its_window():
    """The red team's probe: activated at close 100, breached at close 200, payouts arriving at 110, 150 and 190."""
    acc = {"activation_day": 100, "ended_on": 200, "closed": True, "abandoned": False, "denied": 0,
           "household_closed": False, "ftp_closed": False, "arrivals": (110, 150, 190)}
    enc = HA.encode_funded_accounts([acc])
    direct_126 = JM.account_lifetime(acc, 126)
    assert direct_126 == {"ending": "window", "lost": False, "payouts": 1, "sessions": 26}
    dec_126 = HA.decode_funded_accounts(enc, window=126)
    assert JM.account_lifetime(dec_126[0], 126) == direct_126          # was: breach, lost, 3 payouts, 100 sessions
    dec_252 = HA.decode_funded_accounts(enc, window=252)
    assert JM.account_lifetime(dec_252[0], 252) == JM.account_lifetime(acc, 252) == {
        "ending": "breach", "lost": True, "payouts": 3, "sessions": 100}
    # an account ended by close W keeps its kind at W; one never ended is open at every window
    early = dict(acc, ended_on=120)
    assert JM.account_lifetime(HA.decode_funded_accounts(HA.encode_funded_accounts([early]), window=126)[0], 126) == \
        JM.account_lifetime(early, 126)
    never = dict(acc, ended_on=None, closed=False)
    assert HA.decode_funded_accounts(HA.encode_funded_accounts([never]), window=126)[0]["ending"] is None
    fl = JM.funded_lifetime([HA.decode_funded_accounts(enc, window=126)], 126)
    assert fl["n_censored"] == 1 and fl["n_lost"] == 0
    with pytest.raises(ValueError):
        HA.decode_funded_accounts(enc, window=253)


def test_b1_summariser_reads_each_window():
    rows = []
    enc = HA.encode_funded_accounts([{"activation_day": 100, "ended_on": 200, "closed": True, "arrivals": (110, 150, 190)}])
    for s in range(3):
        for c in range(2):
            rows.append({"baseline": "p14", "arm": "off", "reading": "martingale", "start": f"2020-01-0{s + 2}",
                         "seed": c, "sessions_left": 260, "funded_lifetimes": enc})
    out = H4R.summarise_baseline_readings(pd.DataFrame(rows), [f"2020-01-0{s + 2}" for s in range(3)], "p14")
    r126 = out[out["measure"] == "funded_lifetime_payouts_126"].iloc[0]
    r252 = out[out["measure"] == "funded_lifetime_payouts_252"].iloc[0]
    assert r126["sq_n_censored"] == 6 and math.isnan(r126["r1_p50"])  # all open at 126: no loss, the curve flat
    assert r252["sq_n_censored"] == 0
    assert set(out["record_read"]) == {"long_run"} and out["reading_label"].str.len().min() > 0


# --------------------------------------------------------------------------------------------- F-2, M-3, m-g: nested cuts


@dataclass(frozen=True)
class _Blk:
    pnl: np.ndarray
    entry_t: np.ndarray
    exit_t: np.ndarray
    sides: np.ndarray


def _blocks_of(trades: pd.DataFrame, dates) -> list[_Blk]:
    out = []
    for d in dates:
        g = trades[trades["date"] == d]
        out.append(_Blk(pnl=g["r_1.5"].to_numpy(float), entry_t=g["entry_t"].to_numpy(float),
                        exit_t=g["exit_t"].to_numpy(float), sides=np.where(g["side"] == "long", 1.0, -1.0)))
    return out


def _coin_bundle(dates, arrs, n: int) -> H4R.BaselineBundle:
    ds = list(dates[:n])
    res = _coin(ds, arrs)
    kept, facts, _ = H4R._build_facts_for_trades(res.trades, ds, {d: arrs[d] for d in ds}, tick_value=0.5,
                                                 entry_ticks=1.0, rr_cols=CS.RR_GRID, aux_df=res.aux)
    blocks = _blocks_of(kept, ds)
    return H4R.BaselineBundle(name="naive_coin", dates=tuple(ds), trades=kept, blocks=blocks, args={}, facts=facts,
                              trades_sha256="", meta={}, raw_blocks=blocks)


def test_f2_naive_coin_nested_cut_holds_and_catches_a_planted_lookahead(monkeypatch):
    dates, arrs = _locked_days()
    full, sub = _coin_bundle(dates, arrs, 5), _coin_bundle(dates, arrs, 3)
    cmp = H4R.nested_cut_differences(full, sub)
    assert cmp["days"] == 3 and cmp["differing_days"] == 0, cmp
    rows = H4R._i2_rows("naive_coin", dates[2], cmp, "run mode")
    assert [r["identity"] for r in rows] == [f"I-2@{dates[2]}", f"I-2s@{dates[2]}"] and all(r["holds"] for r in rows)
    # the planted look-ahead: the alert's volatility read one session ahead where one exists
    real = CS.alert_sigma_detail
    monkeypatch.setattr(CS, "alert_sigma_detail",
                        lambda dc, d, dec, **kw: real(dc, min(int(d) + 1, len(dc) - 1), dec, **kw))
    full_l, sub_l = _coin_bundle(dates, arrs, 5), _coin_bundle(dates, arrs, 3)
    bad = H4R.nested_cut_differences(full_l, sub_l)
    assert bad["differing_days"] > 0 and bad["by_part"]["facts"] > 0 and "facts.sigma" in bad["fields"], bad
    assert not H4R._i2_rows("naive_coin", dates[2], bad, "run mode")[1]["holds"]


def test_f2_check_i2_runs_every_baseline_through_one_builder(monkeypatch):
    dates, arrs = _locked_days()
    monkeypatch.setattr(HA, "H4_NESTED_CUTS", (dates[2], dates[3]))
    full = {"naive_coin": _coin_bundle(dates, arrs, 5)}
    built = []

    def builder(b, last):
        built.append((b, last))
        return _coin_bundle(dates, arrs, dates.index(last) + 1)

    rows = H4R._check_i2_nested_cuts(full, ROOT, baselines=("naive_coin",), builder=builder)
    assert built == [("naive_coin", dates[2]), ("naive_coin", dates[3])]
    assert len(rows) == 4 and all(r["holds"] for r in rows)


def test_m3_raw_compared_with_raw_and_mg_every_field():
    a = _Blk(np.array([1.0, 2.0]), np.array([10.0, 20.0]), np.array([15.0, 25.0]), np.array([1.0, -1.0]))
    kept = _Blk(np.array([2.0]), np.array([20.0]), np.array([25.0]), np.array([-1.0]))   # a trade dropped on day 0
    full = H4R.BaselineBundle(name="p15", dates=("2020-01-02", "2020-01-03"), trades=pd.DataFrame({"date": []}),
                              blocks=[kept, a], args={}, facts={}, trades_sha256="", meta={}, raw_blocks=[a, a])
    sub = H4R.BaselineBundle(name="p15", dates=("2020-01-02",), trades=pd.DataFrame({"date": []}), blocks=[kept],
                             args={}, facts={}, trades_sha256="", meta={}, raw_blocks=[a])
    cmp = H4R.nested_cut_differences(full, sub)
    assert cmp["by_part"]["raw_blocks"] == 0 and cmp["by_part"]["blocks"] == 0     # raw vs raw, kept vs kept
    # m-g: a field the old comparison skipped (exit_t, sides) is now a difference
    assert H4R.dayblock_differences(a, dataclasses.replace(a, exit_t=np.array([15.0, 26.0]))) == ["exit_t"]
    assert H4R.dayblock_differences(a, dataclasses.replace(a, sides=np.array([1.0, 1.0]))) == ["sides"]
    sub_bad = dataclasses.replace(sub, raw_blocks=[dataclasses.replace(a, exit_t=np.array([0.0, 0.0]))])
    assert H4R.nested_cut_differences(full, sub_bad)["by_part"]["raw_blocks"] == 1


# --------------------------------------------------------------------------------------------- B-2 / m-4: exact runs


def _cls(h=21, **kw):
    base = dict(first_pass_long=5, first_pay_long=15, rel_long=np.zeros(30), arrivals_long=[(15, 100.0)],
                first_pass_exact=5, first_pay_exact=15, rel_exact=np.zeros(22), arrivals_exact=[(15, 100.0)])
    base.update(kw)
    return HA.classify_exact_difference(h, **base)


def test_b2_classifier_kinds():
    assert _cls()["kind"] == "same"
    assert _cls(first_pass_exact=6)["kind"] == "event_day"
    assert _cls(first_pay_exact=-1)["kind"] == "event_day"
    assert _cls(arrivals_exact=[(16, 100.0)])["kind"] == "event_day"
    assert _cls(arrivals_exact=[(15, 101.0)])["kind"] == "arrival_cash"
    r_h = np.zeros(22)
    r_h[21] = -50.0
    c = _cls(rel_exact=r_h)
    assert c["kind"] == "rel_only_at_h" and c["rel_first_close"] == 21 and c["rel_closes_differing"] == 1
    r_b = np.zeros(22)
    r_b[10] = 0.5
    c = _cls(rel_exact=r_b)
    assert c["kind"] == "rel_only_before_h" and not c["rel_diff_over_1usd"]
    # events past h are not read; a long run's later event is no difference at h
    assert _cls(first_pass_long=30, first_pass_exact=-1)["kind"] == "same"
    with pytest.raises(ValueError):
        _cls(rel_exact=np.zeros(5))


def test_b2_classifier_differs_is_the_m4_count_and_tallies_sum():
    rng = _rng("classify")
    tally: dict = {}
    n_diff = 0
    for k in range(400):
        h = int(rng.choice([21, 63]))
        rl = np.round(rng.normal(0, 1, h + 1), 1) * (rng.random() < 0.5)
        re_ = rl.copy()
        if rng.random() < 0.3:
            re_[int(rng.integers(0, h + 1))] += float(rng.choice([1e-7, 0.5, 3.0]))
        fl, fe = [int(x) for x in rng.integers(-1, h + 3, 2)]
        al = [(int(rng.integers(1, h + 2)), 100.0)]
        ae = al if rng.random() < 0.8 else [(al[0][0], 99.0)]
        c = HA.classify_exact_difference(h, first_pass_long=fl, first_pay_long=-1, rel_long=rl, arrivals_long=al,
                                         first_pass_exact=fe, first_pay_exact=-1, rel_exact=re_, arrivals_exact=ae)
        fp_l = fl if 0 < fl <= h else -1
        fp_e = fe if 0 < fe <= h else -1
        old = (fp_l != fp_e) or float(np.max(np.abs(rl - re_))) > 1e-6 or \
            [(d, round(x, 6)) for d, x in al if d <= h] != [(d, round(x, 6)) for d, x in ae if d <= h]
        assert c["differs"] == old
        n_diff += int(old)
        HA.tally_exact(tally, "off", h, [c["kind"]])
    assert HA.exact_tally_differs(tally) == n_diff
    assert sum(cell["checked_lanes"] for cell in tally["off"].values()) == 400
    merged = HA.merge_exact_tallies([tally, tally])
    assert HA.exact_tally_differs(merged) == 2 * n_diff
    with pytest.raises(ValueError):
        HA.tally_exact({}, "off", 21, ["bogus"])


_CHUNK_CODE = r"""
import datetime as dt, json, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tests"))
from extended import use_vendored_stage2
use_vendored_stage2()
import numpy as np
from extended import h4_audit as HA, three_way_baseline as TB, three_way_seeds as S
import scripts.h4_rebaseline as H4R
import three_way_baseline_checks as TBC
from propedge.campaign.sizing import SizingRule

blocks, args, facts = TBC.job()
CT = {"entry": TBC.E_T, "target": TBC.XT_T, "stop": TBC.XS_T, "flatten": TBC.XF_T}   # the fixture's own ticks
dates = tuple((dt.date(2020, 1, 2) + dt.timedelta(days=k)).isoformat() for k in range(TBC.N_DAYS))
cal = frozenset(dt.date.fromisoformat(d) for d in dates)
ctx = dict(baseline="p16", dates=dates, blocks=blocks, args=args, facts=facts, subs=H4R.subs_of(facts),
           seed_indices=tuple(range(6)), part_id=S.PARTS["H4-T"], seed_role="h4_tests", sample_seed_role="h4_tests",
           sample_part_id=S.PARTS["H4-T"], arms=H4R.ARM_SPECS, calendar_fset=cal, latency=0.0, check_exact=True,
           cost_ticks=CT)
HA.is_sampled_unit = lambda *a, **k: True          # every unit sampled: the oracle re-derives every taken trade
H4R._init_h4b_worker(ctx)
out = H4R._h4b_start_chunk([3, 21])
res = {"exact_checked": out["exact_checked"], "exact_differs": out["exact_differs"],
       "tally_differs": HA.exact_tally_differs(out["exact_tally"]),
       "tally_lanes": sum(c["checked_lanes"] for by in out["exact_tally"].values() for c in by.values()),
       "tally_arms": sorted(out["exact_tally"]), "units_listed": len(out["exact_units"]),
       "oracle_checked": out["oracle_checked"], "peak": out["peak_wset_mb"], "pid": out["pid"],
       "need_logged": sorted({t["need_logged"] for t in out["trades"]})}

# m-e: the engine's own ledger against the race arm's log, every input re-derived
rec = TB.simulate(blocks, args, facts, 3, list(range(6)), 63, seed=S.issue("h4_tests"), part=S.PARTS["H4-T"],
                  history=0, block_sessions=TBC.N_DAYS, dates=dates, calendar=cal, outcome="race", keep_paths=True,
                  log=True)
subs = H4R.subs_of(facts)
tot = {"rows": 0, "R": 0, "d": 0, "fee": 0, "room": 0, "need": 0}
planted = {}
first = None
for j in range(6):
    rows = H4R._format_sampled_trade_rows("p16", "off", "martingale", 3, dates[3], j, dates, blocks, facts, subs,
                                          H4R.ARM_SPECS[0][3], rec.logs[j])
    led = rec.paths[j].trades or []
    c = HA.verify_unit_against_ledger(rows, led, start=3, seed=S.issue("h4_tests"), part=S.PARTS["H4-T"],
                                      fee_schedule=TBC.FEES, cost_ticks=CT)
    for k in tot:
        tot[k] += c[k]
    if first is None and rows:
        first = (rows, led)
rows, led = first
by = HA.ledger_by_trade(led, 3)
r0 = [r for r in rows if r["law"] not in ("missed", "day_end")][0]
k0 = (int(r0["day_idx"]), int(r0["trade_idx"]), r0["acct_kind"], int(r0["acct_index"]))
for name, row, lrow in (
        ("G_up", dict(r0, G=float(r0["G"]) + 1.0), by[k0]),
        ("e_cost", dict(r0, e_cost=float(r0["e_cost"]) + 0.01), by[k0]),
        ("d", r0, dict(by[k0], realised_risk=float(by[k0]["realised_risk"]) * 1.01)),
        ("fee", dict(r0, fee=float(r0["fee"]) + 0.5), by[k0]),
        ("fee_coherent", dict(r0, fee=float(r0["fee"]) + 0.5, e_cost=float(r0["e_cost"]) + 0.5,
                              out=float(r0["out"]) - 0.5),
         dict(by[k0], fee=float(r0["fee"]) + 0.5)),           # a wrong fee carried consistently: only the contracts tell
        ("room", r0, dict(by[k0], room=float(r0["room"]) + 5.0) if "room" in by[k0] else None),
        ("R", r0, dict(by[k0], rr=float(by[k0]["rr"]) + 0.25))):
    if lrow is None:
        planted[name] = "n/a"
        continue
    try:
        HA.verify_race_trade_row(row, seed=S.issue("h4_tests"), part=S.PARTS["H4-T"], ledger=lrow,
                                 fee_fn=lambda n: HA.fee_mini_mix(n, TBC.FEES), require_inputs=True, cost_ticks=CT)
        planted[name] = "passed"
    except HA.H4OracleRefused:
        planted[name] = "refused"
sz = __import__("dataclasses").replace(SizingRule.from_ledger(), fee_schedule=TBC.FEES)
res.update(ledger=tot, planted=planted, room_in_ledger="room" in by[k0],
           fee_same=all(abs(sz.fee_dollars(n) - HA.fee_mini_mix(n, TBC.FEES)) < 1e-12 for n in range(0, 61)))
print(json.dumps(res))
"""


def test_b2_me_runner_chunk_and_ledger_rederivation_on_the_synthetic_job():
    proc = subprocess.run([sys.executable, "-B", "-c", _CHUNK_CODE], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", timeout=600)
    assert proc.returncode == 0, proc.stderr[-3000:]
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    # B-2: the tally covers every lane the m-4 counter checked and sums to its count
    assert out["tally_lanes"] == out["exact_checked"] > 0
    assert out["tally_differs"] == out["exact_differs"] == out["units_listed"]
    assert out["tally_arms"] == ["missed_0.1", "off", "off_as_walked", "worse_1"]
    # m-e: every sampled race row of the chunk passed the oracle with its inputs re-derived (require_inputs)
    assert out["oracle_checked"] > 0 and out["need_logged"] == [1]
    assert out["peak"] > 0 and out["pid"] > 0
    led = out["ledger"]
    assert led["rows"] > 0 and led["R"] == led["d"] == led["fee"] == led["need"] == led["rows"]
    if out["room_in_ledger"]:
        assert led["room"] == led["rows"]
    for name, verdict in out["planted"].items():
        assert verdict in ("refused", "n/a"), (name, verdict)
    assert out["planted"]["G_up"] == out["planted"]["d"] == out["planted"]["fee"] == out["planted"]["R"] == "refused"
    assert out["planted"]["fee_coherent"] == "refused"
    assert out["fee_same"]


# --------------------------------------------------------------------------------------------- m-e: CSV-only re-derivation


def _row(**kw) -> dict[str, Any]:
    d, fee = 2.0, 3.0
    base = {"arm": "off", "R": 2.0, "stop_ticks": 150, "d": d, "fee": fee, "room": 5000.0,
            "e_cost": 1.0 * d + fee, "xt_cost": 0.0, "xs_cost": 1.0 * d, "xf_cost": 2.0 * d,
            "G": 300.0, "L_ticks": 150.0, "law": "race", "need": "", "need_logged": 1}
    base.update(kw)
    return base


def test_me_csv_rederivation_refuses_planted_inputs():
    assert HA.verify_trade_inputs(_row(), require=True)["R"] is False
    for bad in (dict(G=301.0), dict(e_cost=5.5), dict(xs_cost=2.5), dict(L_ticks=149.0),
                dict(arm="worse_1"), dict(G=250.0)):
        with pytest.raises(HA.H4OracleRefused):
            HA.verify_trade_inputs(_row(**bad), require=True)
    # the need-capped G: (need + e + x_t) / d, below the target
    HA.verify_trade_inputs(_row(need=495.0, G=(495.0 + 5.0) / 2.0), require=True)
    with pytest.raises(HA.H4OracleRefused):
        HA.verify_trade_inputs(_row(need=495.0, G=300.0), require=True)
    # a row written before Q-188b (no need logged): only G <= target
    HA.verify_trade_inputs(_row(need_logged="", G=250.0), require=True)
    with pytest.raises(HA.H4OracleRefused, match="above FV3's target"):
        HA.verify_trade_inputs(_row(need_logged="", G=301.0), require=True)
    with pytest.raises(HA.H4OracleRefused):
        HA.verify_trade_inputs(_row(R=2.0), allowed_R=[1.5, 2.5], require=True)
    with pytest.raises(HA.H4OracleRefused):
        HA.verify_trade_inputs({k: v for k, v in _row().items() if k != "fee"}, require=True)
    # a facts set with other ticks is refused at a part's start, never hours in
    f_ok = _move_facts()
    assert HA.check_cost_ticks({(0, 0): f_ok}) == 1
    with pytest.raises(HA.H4AuditRefused, match="m-e"):
        HA.check_cost_ticks({(0, 0): dataclasses.replace(f_ok, e_ticks=0.5)})
    # the costs' declared ticks are Stage 2's and the arms' extras the runner's
    assert HA.H4_COST_TICKS == {"entry": 1.0, "target": float(W.EXIT_TICKS[W.TARGET]),
                                "stop": float(W.EXIT_TICKS[W.STOP]), "flatten": float(W.EXIT_TICKS[W.FLATTEN])}
    assert HA.H4_ARM_WORSE_TICKS == {a[0]: float(a[3].worse_ticks) for a in H4R.ARM_SPECS}
    # the zero-gross identity is labelled an identity and no longer called by the oracle
    assert "identity, not a check" in HA.check_race_exact_zero_gross.__doc__
    import inspect
    assert "check_race_exact_zero_gross(" not in inspect.getsource(HA.verify_race_trade_row)


# --------------------------------------------------------------------------------------------- m-f, M-1, N-1


def test_mf_realised_risk_gate_refuses_missing_input():
    b = H4R.BaselineBundle(name="p15", dates=(), trades=pd.DataFrame(), blocks=[], args={}, facts={},
                           trades_sha256="", meta={})
    sub = pd.DataFrame({"S": [100, 100]})
    with pytest.raises(HA.H4AuditRefused, match="m-f"):
        H4R._realised_risk_gate(sub, b)
    with pytest.raises(HA.H4AuditRefused, match="m-f"):
        H4R._realised_risk_gate(sub, dataclasses.replace(b, args={"draws": {"sizing": object()}}))
    share, ok = H4R._realised_risk_gate(sub.iloc[0:0], b)
    assert math.isnan(share) and ok is False


def test_m1_probe_logs_real_race_laws():
    out = H4R._synthetic_h4_0_probe(H4_TEST_SEED, H4_TEST_PART, j_tb=4, h_tb=25)
    laws = set(out["tb_race_laws"].split(";"))
    assert out["tb_race_log_rows_raw"] > 0                       # the raw count, never max(1, ...)
    assert laws & {"race", "walk", "move"} and laws <= {"race", "walk", "move", "fill_fail", "day_end", "missed"}


class _Inner:
    settlement = "mae"
    key = ("combine", 0)

    def __init__(self):
        self.last_trade = {"historical_day": 0, "trade_index": 0, "realised_risk": 75.0, "rr": 2.0, "contracts": 1,
                           "risk_per_contract": 75.0, "fee": 1.22, "need": None, "u": 2.0, "mae": 0.0}

    def __call__(self, n, day, slot, cushion, **kw):
        return np.array([150.0])


class _MvBlk:
    entry_t = np.array([940.0])
    exit_t = np.array([1100.0])
    exit_by_rr = {2.0: np.array([1100.0])}


def _move_facts(sigma: float = 1.0) -> TB.TradeFacts:
    return TB.TradeFacts(decision=935, entry=940, stop_ticks=150, tick_value=0.5, kinds={2.0: "t"}, limit=1328,
                         sigma=sigma, be_open=TB.move_bar(940), e_ticks=1.0, xt_ticks=0.0, xs_ticks=1.0, xf_ticks=2.0,
                         fee_per_contract=1.22)


def test_n1_one_tick_arming_and_the_key_guard():
    """N1e and N1h (the red team's m-a): phase 1 on a one-tick lattice (s1 = 1) ending at exactly one tick in the
    trade's favour arms the move (`x >= 1`), and every walk key is recorded in the key guard; the independent oracle
    agrees on every lane."""
    f = _move_facts()
    lanes = list(range(64))
    guard = K.KeyGuard.sampled([0], lanes)
    coins = J.CoinLanes(H4_TEST_SEED, H4_TEST_PART, 0, 0, lanes, guard, False)
    unit = TB._Unit({(0, 0): f}, [_MvBlk()], 0, coins, J.ArmSpec())
    at_one = 0
    for lane in lanes:
        log: list = []
        ro = TB.RaceOver(_Inner(), unit, lane, "race", log, None)
        ro.begin_session(5000.0, 0.0)
        out = float(ro(1, 0, 0, np.array([5000.0]))[0])
        r = log[0]
        assert r["law"] == "move" and r["s1"] == 1
        d = r["d"]
        row = {"start": 0, "seed_index": lane, "day_idx": 0, "decision": f.decision, "sub": 0, "underlying": "NQ",
               "fill_bar": f.entry, "time_limit": f.limit, "be_open": f.be_open, "sigma": f.sigma,
               "stop_ticks": f.stop_ticks, "G": r["G"], "L_ticks": r["L_ticks"], "room": 5000.0, "d": d,
               "e_cost": 1.0 * d + 1.22, "xt_cost": 0.0, "xs_cost": d, "xf_cost": 2.0 * d, "law": "move",
               "exit_code": r["exit"], "s1": r["s1"], "n1": r["n1"], "s2": r["s2"], "n2": r["n2"],
               "move_x": r["move_x"] if math.isfinite(r["move_x"]) else "", "move_moved": int(bool(r["move_moved"])),
               "move_G2": r["move_G2"] if math.isfinite(r["move_G2"]) else "",
               "move_down2": r["move_down2"] if math.isfinite(r["move_down2"]) else "", "out": out,
               "arm": "off", "R": 2.0, "fee": 1.22, "need": "", "need_logged": 1}
        HA.verify_race_trade_row(row, seed=H4_TEST_SEED, part=H4_TEST_PART, require_inputs=True)
        if math.isfinite(r["move_x"]) and r["move_x"] == 1.0:
            at_one += 1
            assert r["move_moved"] is True and r["move_down2"] == 1.0
    assert at_one >= 1                                   # the arming threshold itself was exercised
    assert guard.checked >= len(lanes)                   # every lane's walk key went through the guard


def test_n1_twin_walk_uniforms_are_the_complements():
    """N1d (m-a): `_walk_uniforms` on a twin coin field reads the antithetic complements, 1 - u bit for bit."""
    f = _move_facts()
    lanes = list(range(8))
    plain = TB._Unit({(0, 0): f}, [_MvBlk()], 0, J.CoinLanes(H4_TEST_SEED, H4_TEST_PART, 0, 0, lanes, None, False),
                     J.ArmSpec())
    twin = TB._Unit({(0, 0): f}, [_MvBlk()], 0, J.CoinLanes(H4_TEST_SEED, H4_TEST_PART, 0, 0, lanes, None, True),
                    J.ArmSpec())
    lt = _Inner().last_trade
    for lane in lanes:
        k_p, _ = plain.key(0, 0, lt)
        k_t, _ = twin.key(0, 0, lt)
        u_p = TB.RaceOver(_Inner(), plain, lane, "race", None, None)._walk_uniforms(k_p, 300)
        u_t = TB.RaceOver(_Inner(), twin, lane, "race", None, None)._walk_uniforms(k_t, 300)
        assert np.array_equal(u_p + u_t, np.ones(300)) and not np.array_equal(u_p, u_t)
        ref = plain.coins.coin(k_p, K.WALK, 300, np.asarray([lane]), first=0, record=False)[0]
        assert np.array_equal(u_p, ref)


# --------------------------------------------------------------------------------------------- rc-3, F-8, F-13, m-h, m-i, workers


def test_rc3_disk_sized_at_the_true_row_cost(tmp_path):
    assert HA.H4_TRADE_ROW_BYTES == 231
    assert HA.trade_log_disk_need(4 * HA.H4_TRADE_ROWS_PER_BASELINE) == 4 * HA.H4_TRADE_ROWS_PER_BASELINE * 231 * 2
    with pytest.raises(HA.H4AuditRefused, match="rc-3"):
        HA.check_trade_log_disk(tmp_path, 10 ** 15)
    got = HA.check_trade_log_disk(tmp_path, 10)
    assert got["need_bytes"] == 10 * 231 * 2 and got["free_bytes"] >= got["need_bytes"]


def test_f8_gate_labels_and_mi_reading_labels_are_scan_safe():
    row = {"trades": 100, "resolves_5pct": False, "passes_realised_risk_90pct": True, "outside_stop_band": 3,
           "outside_funded_below_2000_band": 100, "below_cost_drag_floor": 0, "dropped_sigma_zero": 2}
    lab = H4R.supply_gate_labels(row)
    for k in ("resolution", "stop_band", "funded_band", "sigma_zero"):
        assert H4R.GATE_LABELS[k] in lab
    assert H4R.GATE_LABELS["realised_risk"] not in lab
    assert H4R.supply_gate_labels({"trades": 0}) == H4R.GATE_LABELS["no_trades"]
    assert H4R.supply_gate_labels({"trades": 5, "resolves_5pct": True, "passes_realised_risk_90pct": True}) == ""
    assert set(H4R.READING_LABELS) == {a[0] for a in H4R.ARM_SPECS}
    assert "rc-11" in H4R.READING_LABELS["off_as_walked"] and "need-capped" in H4R.READING_LABELS["off_as_walked"]
    for txt in [*H4R.GATE_LABELS.values(), *H4R.READING_LABELS.values()]:
        assert ":" not in txt and "$" not in txt        # the results' timestamp and price scans read every cell


def test_f13_thread_env_recorded(monkeypatch):
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.delenv("MKL_NUM_THREADS", raising=False)
    te = H4R.thread_env()
    assert te["OMP_NUM_THREADS"] == "1" and te["MKL_NUM_THREADS"] is None and set(te) == set(H4R.THREAD_ENV_KEYS)
    src = (ROOT / "scripts" / "h4_rebaseline.py").read_text(encoding="utf-8")
    assert src.count('"threads": thread_env()') >= 6                 # H4-0, H4-S, H4-S checks, H4-A, H4-B, merge


def test_mh_i3_seeds_by_role_only():
    a = [H4R.i3_regime_seed(H4_TEST_SEED, r) for r in range(3)]
    assert len(set(a)) == 3 and all(0 <= x < 2 ** 32 for x in a)
    assert a == [int(K.key_state(K.seed_key(H4_TEST_SEED, "test", test=H4R.I3_TEST_ID, replicate=r), 1)[0])
                 for r in range(3)]
    with pytest.raises(S.ProvenanceRefused):
        H4R.i3_regime_seed(int(H4_TEST_SEED), 0)                    # the literal value, not the issued seed
    with pytest.raises(S.ProvenanceRefused):
        H4R.i3_regime_seed(S.issue("h4_0_probe"), 0)                # another role
    with pytest.raises(S.ProvenanceRefused):
        H4R.i3_regime_seed(S.issue("tests"), 0)                     # H3's tests role, which may draw test keys
    src = (ROOT / "scripts" / "h4_rebaseline.py").read_text(encoding="utf-8")
    assert not re.search(r"\b7000[1-3]\b", src)
    # the id is I-3's alone among the repository's h4_tests test-kind keys
    hits = [p for p in (ROOT / "tests").glob("*.py") if re.search(rf"test={H4R.I3_TEST_ID}\b", p.read_text(encoding="utf-8"))]
    assert hits == []


def test_workers_flag_and_peaks():
    assert H4R.MAX_WORKERS == 2 and H4R.H4B_MAX_WORKERS == 4
    peaks = H4R._worker_peaks([{"pid": 7, "peak_wset_mb": 100.0}, {"pid": 7, "peak_wset_mb": 150.0},
                               {"pid": 9, "peak_wset_mb": float("nan")}, {"pid": 8, "peak_wset_mb": 90.0}])
    assert peaks == {"7": 150.0, "8": 90.0}
    assert H4R._peak_mb() > 0
    # the order the scout relies on: batches submitted, then each result collected in submission order
    src = (ROOT / "scripts" / "h4_rebaseline.py").read_text(encoding="utf-8")
    assert "futs = [(idx_c, ch, ex.submit(_h4b_start_chunk, ch)) for idx_c, ch in enumerate(chunks, 1)]" in src
    assert "for idx_c, ch, fut in futs:\n                results_chunks.append(fut.result())" in src.replace("\r\n", "\n")


def test_worker_identity_script(tmp_path):
    hdr = "baseline,arm,start_idx,seed,net_month_1"
    ref_rows = [f"p14,off,{s},{c},{s * 10 + c}.5" for s in range(4) for c in range(2)]
    ref = tmp_path / "ref.csv"
    ref.write_bytes(("\n".join([hdr, *ref_rows]) + "\n").encode())
    new = tmp_path / "new.csv"
    new.write_bytes(("\n".join([hdr, *ref_rows[:4]]) + "\n").encode())          # starts 0 and 1
    assert WID.units_identity(new, ref)["holds"] is True
    bad = tmp_path / "bad.csv"
    bad.write_bytes(("\n".join([hdr, *ref_rows[:3], ref_rows[3].replace(".5", ".50")]) + "\n").encode())
    r = WID.units_identity(bad, ref)
    assert r["holds"] is False and r["rows_differing"] == 1
    with pytest.raises(WID.IdentityRefused):
        WID._checked(new)                                                         # no manifest


def test_exact_classify_samples_the_audit_units():
    got = XD.sampled_units(60, range(16))                       # the audit sample's own role (h4_sample, H4-U)
    want = {s: [c for c in range(16) if HA.is_sampled_unit(s, c)] for s in range(60)}
    assert got == {s: v for s, v in want.items() if v}
