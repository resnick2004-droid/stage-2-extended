"""Q-154 (H2): `extended.overnight_bars_check` on synthetic bars only -- no real bar is read.

Held here: the gap runs; the trading-day clock across both US daylight-saving changes (the reopen stays at slot 0,
the UTC offset moves, no slot shifts or repeats); a session that traded through a change is caught (a repeated or
skipped CT hour is a clock break and a duplicate slot); the void and special rules on hand-built days; the calendar
contexts; the abroad session clocks; the refusal of a confirmation-window bar; the flag CSV's columns (no price); and
the report's verdict line, rendered end to end from synthetic inputs. Run with a time limit (`timeout 600`).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from extended import overnight_bars_check as K
from extended.price_levels import LEVEL_TOKENS, name_tokens

CT = K.CHICAGO


def _ts(d: date, hh: int, mm: int) -> int:
    return int(datetime(d.year, d.month, d.day, hh, mm, tzinfo=CT).timestamp())


def session(day: date, *, skip: set[int] = frozenset(), extra: list[int] = (), contract: str = "NQH3",
            end_slot: int = 1379) -> pd.DataFrame:
    """A trading day's bars, every minute from 17:00 CT the evening before to `end_slot`, except the slots in `skip`;
    `extra` adds bars at those slots again (duplicates) or in the halt. Prices synthetic, on the tick."""
    eve = day - timedelta(days=1)
    start = _ts(eve, 17, 0)
    slots = [s for s in range(end_slot + 1) if s not in skip] + list(extra)
    ts = []
    for s in slots:
        # walk the wall clock: 17:00 CT of the evening + s minutes, localised in CT (DST-aware)
        wall = datetime(eve.year, eve.month, eve.day, 17, 0) + timedelta(minutes=s)
        ts.append(int(wall.replace(tzinfo=CT).timestamp()))
    ts = np.array(ts, dtype=np.int64)
    n = len(ts)
    base = 100.0 + 0.25 * (np.arange(n) % 7)
    df = pd.DataFrame({"ts": ts, "contract": contract, "open": base, "high": base + 0.5, "low": base - 0.25,
                       "close": base + 0.25, "volume": np.full(n, 10, dtype=np.int64)})
    d, _, _ = K.clock(ts)
    df["day"] = np.datetime_as_string(d, unit="D")
    assert start == ts[0] or 0 in skip
    return df


def ctx_for(days):
    return K.contexts(days, [])


# --------------------------------------------------------------------------------------------------- gaps


def test_missing_runs():
    p = np.array([1, 1, 0, 0, 1, 0, 1, 1, 0], dtype=bool)
    assert K.missing_runs(p).tolist() == [[2, 2], [5, 1], [8, 1]]
    assert K.missing_runs(np.ones(5, bool)).tolist() == []
    assert K.missing_runs(np.zeros(3, bool)).tolist() == [[0, 3]]
    assert [K.gap_bin(x) for x in (1, 2, 4, 5, 14, 15, 29, 30, 300)] == \
        ["1", "2-4", "2-4", "5-14", "5-14", "15-29", "15-29", ">=30", ">=30"]


def test_gaps_and_void_rules_on_a_built_day():
    d = date(2023, 6, 7)                                   # a Wednesday, CDT, no change near
    gap3 = set(range(K.slot(20, 10), K.slot(20, 13)))      # 3 minutes
    gap6 = set(range(K.slot(1, 0), K.slot(1, 6)))          # 6 minutes: special, not void
    df = session(d, skip=gap3 | gap6)
    hours = K.HourAgg()
    recs, _ = K.day_records(df, ctx_for([d]), hours)
    (r,) = recs
    assert r.first_slot == 0 and r.n_on == K.ON_N - 9 and r.n_halt == 0 and r.dup_slot == 0
    assert sorted(r.runs) == [(K.slot(20, 10), 3), (K.slot(1, 0), 6)]
    v, s = K.classify(r, ctx_for([d])[d], roll=False, dst_session=False, bls=False, degraded=False, seam=False)
    assert v == [] and "gap_5_14" in s and "no_0829_bar" not in s
    # a 15-minute gap voids it; a missing 08:29 bar is flagged for RL3
    df2 = session(d, skip=set(range(K.slot(23, 0), K.slot(23, 15))) | {K.ON_LAST})
    (r2,), _ = K.day_records(df2, ctx_for([d]), K.HourAgg())
    v2, s2 = K.classify(r2, ctx_for([d])[d], roll=False, dst_session=False, bls=False, degraded=False, seam=False)
    assert "long_gap" in v2 and "no_0829_bar" in s2
    # hour aggregates: the 20:00 hour lost three minutes of sixty
    h20 = K.slot(20, 0) // 60
    assert hours.slots[h20] == 60 and hours.present[h20] == 57


def test_late_reopen_duplicate_halt_and_malformed():
    d = date(2023, 6, 7)
    df = session(d, skip=set(range(0, 7)), extra=[K.slot(22, 0), K.slot(16, 30)])
    df.loc[df.index[5], "high"] = df.loc[df.index[5], "open"] - 0.25      # high below the open: malformed
    (r,), _ = K.day_records(df, ctx_for([d]), K.HourAgg())
    v, _ = K.classify(r, ctx_for([d])[d], roll=False, dst_session=False, bls=False, degraded=False, seam=False)
    assert {"late_reopen", "duplicate", "outside_hours", "malformed"} <= set(v)
    assert r.first_slot == 7 and r.dup_slot == 1 and r.n_halt == 1
    assert r.halt_slots == [K.slot(16, 30)]


def test_off_tick_is_malformed():
    d = date(2023, 6, 7)
    df = session(d)
    df.loc[df.index[100], "close"] += 0.1
    (r,), _ = K.day_records(df, ctx_for([d]), K.HourAgg())
    assert r.malformed == 1


# --------------------------------------------------------------------------------------------------- the DST clock


@pytest.mark.parametrize("before, after, off_before, off_after", [
    (date(2023, 3, 10), date(2023, 3, 13), -360, -300),    # spring: Friday CST, Monday (Sunday open) CDT
    (date(2023, 11, 3), date(2023, 11, 6), -300, -360),    # autumn: Friday CDT, Monday CST
])
def test_dst_clock_is_continuous_across_the_weekend_change(before, after, off_before, off_after):
    df = pd.concat([session(before), session(after)], ignore_index=True)
    recs, _ = K.day_records(df, ctx_for([before, after]), K.HourAgg())
    rb, ra = recs
    assert (rb.day, ra.day) == (before, after)
    assert rb.first_slot == 0 and ra.first_slot == 0                     # 17:00 CT both sides
    assert (rb.first_offset, ra.first_offset) == (off_before, off_after)
    assert rb.clock_breaks == ra.clock_breaks == 0 and rb.offsets_on == ra.offsets_on == 1
    assert ra.dup_slot == 0 and ra.n_on == K.ON_N and ra.runs == []
    assert ra.day_label_bad == 0
    chg = K.us_dst_changes([2023])
    assert chg == [date(2023, 3, 12), date(2023, 11, 5)]
    (ch,) = [c for c in chg if before < c < after]
    assert K.first_session_after(ch, [before, after]) == after


def _through(start_local: datetime, minutes: int) -> pd.DataFrame:
    """Bars every real (UTC) minute from a CT start: a session that trades through a DST change."""
    t0 = int(start_local.replace(tzinfo=CT).timestamp())
    ts = t0 + 60 * np.arange(minutes, dtype=np.int64)
    d, _, _ = K.clock(ts)
    n = len(ts)
    return pd.DataFrame({"ts": ts, "day": np.datetime_as_string(d, unit="D"), "contract": "NQZ3",
                         "open": 100.0, "high": 100.25, "low": 100.0, "close": 100.0, "volume": 1})


def test_a_session_through_the_autumn_change_repeats_an_hour():
    df = _through(datetime(2023, 11, 4, 17, 0), 16 * 60)    # Saturday 17:00 CDT to Sunday 08:00 CST, real minutes
    recs, _ = K.day_records(df, {}, K.HourAgg())
    (r,) = recs
    assert r.day == date(2023, 11, 5) and r.dup_slot == 60 and r.offsets_on == 2
    v, _ = K.classify(r, None, roll=False, dst_session=False, bls=False, degraded=False, seam=False)
    assert {"duplicate", "clock_break", "outside_hours"} <= set(v)


def test_a_session_through_the_spring_change_skips_an_hour():
    df = _through(datetime(2023, 3, 11, 17, 0), 14 * 60)
    (r,), _ = K.day_records(df, {}, K.HourAgg())
    assert r.clock_breaks == 1 and r.offsets_on == 2
    assert (K.slot(2, 0), 60) in r.runs                     # 02:00-02:59 CT never exists that night


def test_abroad_session_clocks():
    assert K.london_open_ct(date(2023, 1, 10)) == "02:00"
    assert K.london_open_ct(date(2023, 7, 10)) == "02:00"
    assert K.london_open_ct(date(2023, 3, 20)) == "03:00"   # US on CDT, UK not yet on BST
    assert K.london_open_ct(date(2023, 10, 31)) == "03:00"  # UK back on GMT, US still CDT
    assert K.tokyo_open_ct(date(2023, 1, 10)) == "18:00"
    assert K.tokyo_open_ct(date(2023, 7, 10)) == "19:00"


# --------------------------------------------------------------------------------------------------- the calendar


def test_contexts():
    cal = [{"date": "2023-11-23", "kind": "holiday", "close_ct": "12:00", "source": "x"},
           {"date": "2023-11-24", "kind": "early_close", "close_ct": "12:15", "source": "x"},
           {"date": "2023-12-25", "kind": "holiday", "close_ct": "", "source": "x"},
           {"date": "2021-04-02", "kind": "holiday", "close_ct": "08:15", "source": "x"},
           {"date": "2023-12-27", "kind": "data_defect_candidate", "close_ct": "", "source": "store: purchase edge"}]
    days = [date(2023, 11, 22), date(2023, 11, 23), date(2023, 11, 24), date(2023, 11, 27), date(2023, 12, 22),
            date(2023, 12, 26), date(2023, 12, 27)]
    cx = K.contexts(days, cal)
    assert cx[date(2023, 11, 23)].abbreviated_day and cx[date(2023, 11, 23)].on_end == K.ON_LAST
    assert cx[date(2023, 11, 24)].after_abbreviated and cx[date(2023, 11, 24)].abbreviated_day
    assert cx[date(2023, 11, 27)].sunday_open and cx[date(2023, 11, 27)].after_abbreviated
    assert cx[date(2023, 12, 26)].after_closure and not cx[date(2023, 12, 26)].sunday_open
    assert cx[date(2023, 12, 27)].defect
    gf = K.contexts([date(2021, 4, 1), date(2021, 4, 2)], cal)[date(2021, 4, 2)]
    assert gf.on_end == K.slot(8, 14)                       # the session closes 08:15: the overnight ends 08:14


def test_degraded_dates_map_to_overnights():
    # trading day 2023-06-07's overnight is 22:00 UTC 06-06 to 13:29 UTC 06-07
    assert K.overnight_utc_dates(date(2023, 6, 7)) == (date(2023, 6, 6), date(2023, 6, 7))
    assert K.degraded_days([date(2023, 6, 7), date(2023, 6, 9)], {"2023-06-06": "degraded"}) == {date(2023, 6, 7)}


# --------------------------------------------------------------------------------------------------- the guard


def test_confirmation_window_is_refused():
    ok = _ts(date(2026, 7, 16), 15, 59)
    K.assert_loaded(np.array([ok]), ["2026-07-16"], K.HELD_OUT[1])
    with pytest.raises(RuntimeError, match="REFUSED"):
        K.assert_loaded(np.array([_ts(date(2026, 7, 16), 17, 0)]), ["2026-07-17"], K.HELD_OUT[1])
    with pytest.raises(RuntimeError, match="REFUSED"):
        K.assert_loaded(np.array([ok]), ["2024-01-02"], K.SEARCH[1])


# --------------------------------------------------------------------------------------------------- end to end


def _manifest(days):
    return {"day_list": [d.isoformat() for d in days],
            "day_bounds": {d.isoformat(): ["17:00", "15:59"] for d in days},
            "short_days": {}, "late_start_days": [], "early_end_days": [], "rolls": [],
            "imports": [{"condition": {"not_available": {}}}]}


def test_aggregate_flags_and_render_end_to_end():
    days = [date(2023, 3, 9), date(2023, 3, 10), date(2023, 3, 13), date(2023, 3, 14)]
    frames = [session(days[0]), session(days[1], skip=set(range(K.slot(0, 0), K.slot(0, 20)))),
              session(days[2], contract="NQM3"), session(days[3], contract="NQM3")]
    df = pd.concat(frames, ignore_index=True)
    ctx = ctx_for(days)
    hours = K.HourAgg()
    recs, _ = K.day_records(df, ctx, hours)
    block = (date(2023, 3, 1), date(2023, 3, 31))
    summ, rows = K.aggregate(recs, ctx, block=block, rolls=["2023-03-13"], dst_changes=K.us_dst_changes([2023]),
                             bls_days={date(2023, 3, 10)}, not_available={}, seams=[],
                             bounds=_manifest(days)["day_bounds"], hours=hours)
    assert summ["void_days"] == {"2023-03-10": ["long_gap"]}
    assert summ["roll"]["rolls_seen_in_bars"] == ["2023-03-13"] and summ["roll"]["agree"]
    assert summ["special_days"]["us_dst_session"] == ["2023-03-13"]
    assert summ["clock_breaks"] == 0 and summ["dup_slot"] == 0 and summ["halt_bars"] == 0
    assert summ["manifest_bounds_agree"] == 4
    assert summ["halt_bar_times"] == [] and summ["most_missing_days"][0][:2] == ("2023-03-10", 20)
    assert summ["bls_clock"]["early_release"]["days"] == 1
    text = K.flags_csv(rows)
    header = text.splitlines()[0].split(",")
    assert header == list(K.FLAG_COLUMNS)
    assert not any(set(name_tokens(c)) & LEVEL_TOKENS for c in header)
    man = _manifest(days)
    held = K.manifest_block(man, ctx, block=block, dst_changes=K.us_dst_changes([2023]), bls_days=set())
    pw = K.power(man, [{"R": "2.0", "true_edge": "0.1", "trades_lower_bound_above_half_edge": "2263",
                        "trades_lower_bound_above_0": "566"}], k=13)
    assert pw["blocks_needed_for_signflip"] == 12 and pw["level"] == pytest.approx(0.05 / 182)
    res = {"search": summ, "held_out": held, "power": pw, "held_out_bar_checked": False,
           "meta": {"date": "2026-11-18", "commit": "x", "tree": "clean", "ran": "t", "verify": "exit 0",
                    "schema": "ok", "trading_day": {"reopen_ct": "17:00", "flat_ct": "15:10"},
                    "manifest": {"decision": "D-458", "licence": "l", "tick": 0.25, "parquet_sha256": "0" * 64,
                                 "first_day": "2023-03-09", "last_day": "2023-03-14", "days": 4, "rows": 1,
                                 "rolls": [], "imports": []}}}
    md = K.render(res)
    assert md.splitlines()[0] == "**Verdict: BLOCKED**"
    assert "2023-03-10: long_gap" in md
    v, why = K.verdict(summ, True)
    assert v == "BLOCKED" and len(why) == 1
    clean = dict(summ, void_day_count=0)
    assert K.verdict(clean, True) == ("VALIDATED", [])


def test_verdict_counts_other_failed_checks():
    clean = {"void_day_count": 0}
    assert K.verdict(clean, True) == ("VALIDATED", [])
    v, why = K.verdict(clean, True, ["the data's hashes do not match"])
    assert v == "BLOCKED" and why == ["the data's hashes do not match"]


def test_the_runner_renders_from_a_json_without_reading_a_bar(tmp_path):
    import importlib.util
    import json as _json
    from pathlib import Path as _P

    days = [date(2023, 3, 9), date(2023, 3, 10)]
    df = pd.concat([session(days[0]), session(days[1])], ignore_index=True)
    ctx = ctx_for(days)
    hours = K.HourAgg()
    recs, _ = K.day_records(df, ctx, hours)
    block = (date(2023, 3, 1), date(2023, 3, 31))
    summ, _ = K.aggregate(recs, ctx, block=block, rolls=[], dst_changes=K.us_dst_changes([2023]), bls_days=set(),
                          not_available={}, seams=[], bounds=_manifest(days)["day_bounds"], hours=hours)
    man = _manifest(days)
    res = {"search": summ, "power": K.power(man, []), "held_out_bar_checked": True, "extra_reasons": [],
           "held_out": K.manifest_block(man, ctx, block=block, dst_changes=[], bls_days=set()),
           "meta": {"date": "2026-11-18", "commit": "x", "tree": "clean", "ran": "t", "verify": "exit 0",
                    "schema": "ok", "trading_day": {"reopen_ct": "17:00", "flat_ct": "15:10"},
                    "manifest": {"decision": "D-458", "licence": "l", "tick": 0.25, "parquet_sha256": "0" * 64,
                                 "first_day": "a", "last_day": "b", "days": 2, "rows": 1, "rolls": [],
                                 "imports": []}}}
    js = tmp_path / "r.json"
    js.write_text(_json.dumps(res, default=str), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "h2_runner", _P(__file__).resolve().parents[1] / "scripts" / "h2_overnight_bars.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = tmp_path / "r.md"
    assert mod.main(["--render", str(js), "--report", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "**Verdict: VALIDATED**" and "Re-rendered without reading a bar" in text
