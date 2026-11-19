"""Q-166: `extended.day_calendar` -- each rule on a synthetic calendar, the session anchors across the US and UK
daylight-saving weeks, the held-out and confirmation refusals, and one check against H2's flags file (the clean run
q154-h2 of 3cf3453): the overnight void set on the search years is the file's VOID set plus the lead's rule (2).
No bar is read. Run with a time limit (`timeout 600`).
"""
from __future__ import annotations

from datetime import date

import pytest

from extended import day_calendar as DC
from extended import triggers as T
from extended import walker as W


def _row(missing=0, verdict="OK", void="", special=""):
    return {"missing_after_reopen": str(missing), "verdict": verdict, "void": void, "special": special}


def make(days, *, calendar=None, rolls=(), early_end=(), last_bar=None, bls=(), fomc=(), flags=None):
    days = [date.fromisoformat(d) for d in days]
    cal = {date.fromisoformat(k): {"date": k, **v} for k, v in (calendar or {}).items()}
    lb = {d: "15:59" for d in days}
    lb.update({date.fromisoformat(k): v for k, v in (last_bar or {}).items()})
    fl = {d: _row() for d in days}
    fl.update({date.fromisoformat(k): v for k, v in (flags or {}).items()})
    return DC.Sources(days, cal, frozenset(date.fromisoformat(x) for x in rolls),
                      frozenset(date.fromisoformat(x) for x in early_end), lb,
                      frozenset(date.fromisoformat(x) for x in bls), frozenset(date.fromisoformat(x) for x in fomc), fl)


D = date.fromisoformat


def test_the_journey_day_end_voids_a_day_without_a_bar_at_1507():
    src = make(["2021-06-01", "2021-06-02", "2021-06-03"], last_bar={"2021-06-02": "15:06"})
    assert DC.day_flags(src, "NQ", D("2021-06-02")).void == ("no_bar_at_15:07",)
    assert DC.day_flags(src, "NQ", D("2021-06-01")).void == ()
    assert DC.day_context(src, "NQ", D("2021-06-02"), 1).void
    # the threshold follows the walk: a walk ending on the bar ending 15:10 needs one stamped 15:09
    late = W.Rules("late", W.C_FLAT, "close", False)
    src2 = make(["2021-06-01", "2021-06-02"], last_bar={"2021-06-02": "15:08"})
    assert DC.day_flags(src2, "NQ", D("2021-06-02")).void == ()
    assert DC.day_flags(src2, "NQ", D("2021-06-02"), rules=late).void == ("no_bar_at_15:09",)
    assert DC._walk_last_stamp(T.JOURNEY) == DC.slot_of("15:07")


def test_scheduled_closes_defects_and_early_ends_void_every_source():
    src = make(["2021-11-24", "2021-11-26", "2021-11-29", "2021-11-30"],
               calendar={"2021-11-26": {"kind": "early_close", "close_ct": "12:15", "source": "E1"},
                         "2021-11-30": {"kind": "data_defect_candidate", "close_ct": "", "source": "x"}},
               early_end=["2021-11-26"], last_bar={"2021-11-26": "12:14"})
    f = DC.day_flags(src, "NQ", D("2021-11-26"))
    assert set(f.void) == {"early_close", "early_end", "no_bar_at_15:07"}
    assert DC.day_flags(src, "NQ", D("2021-11-30")).void == ("data_defect",)
    nxt = DC.day_flags(src, "NQ", D("2021-11-29"))          # the Monday after the abbreviated Friday
    assert nxt.void == () and {"after_abbreviated", "prior_day_void"} <= set(nxt.prior_void)
    assert "sunday_open" in nxt.noted


def test_overnight_voids_h2_and_rule_2():
    flags = {"2020-03-09": _row(241, special="no_0829_bar"), "2020-03-11": _row(3),
             "2020-03-16": _row(762, "VOID", "long_gap"), "2021-02-01": _row(5), "2021-02-02": _row(8)}
    src = make(["2020-03-09", "2020-03-11", "2020-03-16", "2021-02-01", "2021-02-02"], flags=flags)
    assert DC.rule2_threshold(src.flags) == 8 and src.threshold() == 8   # the most outside March 2020
    on = lambda d, **k: DC.day_flags(src, "NQ", D(d), reads_overnight=True, **k)  # noqa: E731
    assert on("2020-03-09").void == ("h2_missing",)
    assert on("2020-03-09", reads_0829=True).void == ("h2_missing", "no_0829_bar")
    assert on("2020-03-16").void == ("h2_void:long_gap", "h2_missing")
    assert on("2020-03-11").void == () and on("2021-02-02").void == ()   # 8 is not more than 8
    assert DC.day_flags(src, "NQ", D("2020-03-09")).void == ()            # an RTH source: not void
    assert not DC.day_context(src, "NQ", D("2020-03-09"), 0).void
    assert DC.day_context(src, "NQ", D("2020-03-09"), 0, reads_overnight=True).void


def test_good_friday_jobs_day_overnight_ends_0814():
    src = make(["2021-04-01", "2021-04-02", "2021-04-05"],
               calendar={"2021-04-02": {"kind": "holiday", "close_ct": "08:15", "source": "H4b"}},
               last_bar={"2021-04-02": "08:14"})
    f = DC.day_flags(src, "NQ", D("2021-04-02"), reads_overnight=True, reads_0829=True)
    assert "overnight_ends_08:14" in f.noted and "no_0829_bar" in f.void and "no_bar_at_15:07" in f.void
    g = DC.day_flags(src, "NQ", D("2021-04-02"), reads_overnight=True)
    assert "no_0829_bar" not in g.void                     # a source not reading the 08:29 bar
    assert "after_abbreviated" in DC.day_flags(src, "NQ", D("2021-04-05")).prior_void


def test_prior_void_rolls_closures_and_the_first_day():
    src = make(["2022-12-23", "2022-12-27", "2023-03-13", "2023-03-14"], rolls=["2023-03-14"])
    assert DC.day_flags(src, "NQ", D("2022-12-23")).prior_void == ("first_day",)
    assert DC.day_flags(src, "NQ", D("2022-12-27")).prior_void == ("after_closure",)   # Monday 26th closed
    assert DC.day_flags(src, "NQ", D("2023-03-14")).prior_void == ("roll",)
    c = DC.day_context(src, "NQ", D("2023-03-14"), 3)
    assert c.prior_void and not c.void and c.session == 3 and c.date == "2023-03-14"


def test_bls_and_fomc_flags():
    src = make(["2021-03-12", "2021-03-17"], bls=["2021-03-12"], fomc=["2021-03-17"])
    a, b = DC.day_context(src, "NQ", D("2021-03-12"), 0), DC.day_context(src, "NQ", D("2021-03-17"), 1)
    assert a.bls and not a.fomc and b.fomc and not b.bls


def test_refusals():
    src = make(["2023-12-28", "2023-12-29"])
    with pytest.raises(DC.HeldOutDay):
        DC.day_flags(src, "NQ", D("2024-01-02"))
    with pytest.raises(DC.ConfirmationDay):
        DC.day_flags(src, "NQ", D("2026-07-17"))
    with pytest.raises(ValueError):
        DC.day_flags(src, "ES", D("2023-12-29"))
    with pytest.raises(KeyError):
        DC.day_flags(src, "NQ", D("2023-12-27"))          # a search-year date that is not stored
    with pytest.raises(DC.HeldOutDay):
        make(["2023-12-29", "2024-01-02"])
    with pytest.raises(KeyError):                           # an overnight source on a day without H2's row
        s = make(["2023-12-28"])
        s.flags.clear()
        DC.day_flags(s, "NQ", D("2023-12-28"), reads_overnight=True)


@pytest.mark.parametrize("day, asia, london", [
    ("2021-01-12", 60, 540),        # both on standard time: Tokyo 09:00 = 18:00 CT, London 08:00 = 02:00 CT
    ("2021-07-12", 120, 540),       # both on summer time: Tokyo 19:00 CT, London 02:00 CT
    ("2021-03-15", 120, 600),       # the US changed, the UK not yet: London 03:00 CT
    ("2021-11-01", 120, 600),       # the UK changed back, the US not yet: London 03:00 CT
    ("2021-03-29", 120, 540),       # both changed
])
def test_session_anchors_follow_local_time(day, asia, london):
    s = DC.anchored_starts(D(day))
    assert s == {"asia": asia, "london": london, "ny": 930}
    assert 0 < s["asia"] < s["london"] < s["ny"]


def test_the_flags_file_void_set_is_reproduced_on_the_search_years():
    path = DC.default_flags_path()
    if not path.is_file():
        pytest.skip(f"H2's flags file is not on this machine ({path})")
    src = DC.load_sources(path)
    assert src.days[0] == DC.SEARCH_START and src.days[-1] == DC.SEARCH_END
    assert all(d <= DC.SEARCH_END for d in list(src.last_bar) + list(src.calendar) + list(src.rolls))
    file_void = {d for d, r in src.flags.items() if r["verdict"] == "VOID"}
    thr = max(int(r["missing_after_reopen"]) for d, r in src.flags.items() if d.strftime("%Y-%m") != "2020-03")
    rule2 = {d for d, r in src.flags.items() if int(r["missing_after_reopen"]) > thr}
    got_h2 = {d for d in src.days
              if any(x.startswith("h2_void:") for x in DC.day_flags(src, "NQ", d, reads_overnight=True).void)}
    got_r2 = {d for d in src.days if "h2_missing" in DC.day_flags(src, "NQ", d, reads_overnight=True).void}
    assert got_h2 == file_void and len(file_void) == 6
    assert got_r2 == rule2 and all(d.strftime("%Y-%m") == "2020-03" for d in rule2)
    assert src.threshold() == thr
