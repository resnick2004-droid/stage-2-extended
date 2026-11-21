"""Q-197: `extended.search_calendar` and `scripts/search_calendar.py` -- the pinned search-year session calendar, on
synthetic sources only (no bar, no result file of this repository): the rows against `day_calendar`'s rules, the
session counting (the start session is session 1), the columns' form, the refusals of a held-out and a
confirmation-window date, the two identities refusing, W42-R1's digest, the loader's refusals, and the script end to
end in a child process writing into a temporary folder. Run with a time limit (`timeout 900`).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from extended import ROOT
from extended import day_calendar as DC
from extended import search_calendar as SC

D = date.fromisoformat
SCRIPT = ROOT / "scripts" / "search_calendar.py"

#: the synthetic search years: the first and last search dates, a Good Friday jobs day, a VOID overnight, a roll, a
#: closure, a data defect, an early close, a rule (2) day
DAYS = ["2020-01-02", "2020-01-03", "2020-03-13", "2020-03-16", "2020-11-27", "2020-11-30", "2021-04-01", "2021-04-02",
        "2021-04-05", "2022-03-17", "2022-03-18", "2023-12-27", "2023-12-29"]
CAL = {"2021-04-02": {"kind": "holiday", "close_ct": "08:15", "source": "H4b"},
       "2020-11-27": {"kind": "early_close", "close_ct": "12:15", "source": "E1"},
       "2020-03-16": {"kind": "data_defect_candidate", "close_ct": "", "source": "store"}}
LAST_BAR = {"2021-04-02": "08:14", "2020-11-27": "12:14"}
ROLLS = ["2022-03-18"]


def _flag(missing=0, verdict="OK", void="", special=""):
    return {"missing_after_reopen": str(missing), "verdict": verdict, "void": void, "special": special}


FLAGS = {"2020-03-16": _flag(762, "VOID", "long_gap;manifest_defect"), "2020-03-13": _flag(5),
         "2022-03-17": _flag(2, special="no_0829_bar"), "2023-12-27": _flag(4)}   # rule (2)'s threshold: 4


def make(days=DAYS, flags=FLAGS, flag_days=None):
    ds = [D(d) for d in days]
    cal = {D(k): {"date": k, **v} for k, v in CAL.items() if k in days}
    lb = {d: "15:59" for d in ds}
    lb.update({D(k): v for k, v in LAST_BAR.items() if k in days})
    fl = {D(d): _flag() for d in (flag_days if flag_days is not None else days)}
    fl.update({D(k): v for k, v in flags.items() if D(k) in fl})
    return DC.Sources(ds, cal, frozenset(D(x) for x in ROLLS), frozenset(), lb, frozenset({D("2021-04-02")}),
                      frozenset({D("2020-03-16")}), fl)


def by_date(rows):
    return {r["date"]: r for r in rows}


# ------------------------------------------------------------------------------------------------------- the rows


def test_rows_session_counting_and_kinds():
    rows = SC.build_rows(make())
    n = len(DAYS)
    assert [r["date"] for r in rows] == DAYS
    assert [r["session"] for r in rows] == list(range(1, n + 1))
    assert [r["sessions_left"] for r in rows] == list(range(n, 0, -1))     # the start session counted
    assert rows[-1]["sessions_left"] == 1 and rows[0]["sessions_left"] == n
    b = by_date(rows)
    assert b["2021-04-02"]["day_kind"] == "holiday" and b["2020-11-27"]["day_kind"] == "early_close"
    assert b["2020-03-16"]["day_kind"] == "data_defect_candidate" and b["2020-01-03"]["day_kind"] == "regular"
    assert b["2022-03-18"]["roll"] == 1 and b["2022-03-17"]["roll"] == 0
    assert b["2021-04-02"]["bls"] == 1 and b["2020-03-16"]["fomc"] == 1 and b["2020-01-03"]["bls"] == 0
    assert b["2020-01-03"]["weekday"] == "Fri" and b["2020-11-30"]["weekday"] == "Mon"
    assert tuple(rows[0]) == SC.COLUMNS


def test_rows_void_flags_per_reading_class():
    b = by_date(SC.build_rows(make()))
    gf = b["2021-04-02"]                                   # abbreviated: day-wide void, plus no 08:29 bar
    assert gf["void_day"] == 1 and gf["why_void_day"] == "early_close|no_bar_at_15:07"
    assert gf["why_void_overnight"] == "early_close|no_bar_at_15:07"
    assert gf["why_void_overnight_0829"] == "early_close|no_bar_at_15:07|no_0829_bar"
    ec = b["2020-11-27"]
    assert ec["why_void_day"] == "early_close|no_bar_at_15:07"
    v = b["2020-03-16"]                                    # data defect (day-wide) and H2's VOID (overnight)
    assert v["why_void_day"] == "data_defect"
    assert v["why_void_overnight"] == "data_defect|h2_void:long_gap;manifest_defect|h2_missing"
    r2 = b["2020-03-13"]                                   # rule (2): 5 > 4 (the most outside March 2020)
    assert (r2["void_day"], r2["void_overnight"], r2["void_overnight_0829"]) == (0, 1, 1)
    assert r2["why_void_overnight"] == "h2_missing" == r2["why_void_overnight_0829"]
    n8 = b["2022-03-17"]                                   # H2's no_0829_bar: the 08:29 class only
    assert (n8["void_day"], n8["void_overnight"], n8["void_overnight_0829"]) == (0, 0, 1)
    assert n8["why_void_overnight_0829"] == "no_0829_bar"
    assert b["2023-12-27"]["void_overnight"] == 0          # 4 is not more than 4
    ok = b["2020-01-03"]
    assert (ok["void_day"], ok["void_overnight"], ok["void_overnight_0829"], ok["prior_void"]) == (0, 0, 0, 0)
    assert b["2020-01-02"]["why_prior_void"] == "first_day"
    assert b["2020-11-30"]["why_prior_void"] == "after_abbreviated|prior_day_void"
    assert b["2021-04-05"]["why_prior_void"] == "after_abbreviated|prior_day_void"
    assert b["2022-03-18"]["why_prior_void"] == "roll"
    assert b["2023-12-29"]["why_prior_void"] == "after_closure"          # 2023-12-28 a weekday without a session
    assert b["2020-03-16"]["why_prior_void"] == ""


def test_rows_match_day_calendar_for_every_day_and_class():
    src = make()
    for r in SC.build_rows(src):
        for c, (on, b829) in SC.CLASSES.items():
            f = DC.day_flags(src, "NQ", D(r["date"]), reads_overnight=on, reads_0829=b829)
            assert r[f"why_void_{c}"] == "|".join(f.void) and r[f"void_{c}"] == int(bool(f.void))
        assert r["why_prior_void"] == "|".join(DC.day_flags(src, "NQ", D(r["date"])).prior_void)


# ------------------------------------------------------------------------------------------------------- the form


def test_columns_hold_dates_labels_and_integers_only():
    rows = SC.build_rows(make())
    assert SC.check_rows(rows) == DAYS
    for r in rows:
        for k in SC.INT_COLUMNS + SC.FLAG_COLUMNS:
            assert type(r[k]) is int
        for k in SC.LABEL_COLUMNS:
            assert isinstance(r[k], str)
    assert not any(k in c for c in SC.COLUMNS for k in ("price", "open", "high", "low", "close", "_ct", "time"))
    v = DAYS.index("2020-03-16")                           # a void day: its reasons are not blank
    assert rows[v]["void_day"] == 1 and rows[1]["void_day"] == 0 and rows[1]["prior_void"] == 0
    # each case is refused by one check alone (the others would pass it), so each check is held on its own
    for i, k, bad in ((1, "session", 1.0), (1, "bls", 2), (1, "bls", False), (v, "void_day", True),
                      (v, "why_void_day", "data_defect 12.5"), (1, "weekday", "Tue"), (1, "day_kind", "halt"),
                      (1, "prior_void", 1), (1, "void_day", 1), (v, "why_void_overnight", "")):
        rr = [dict(r) for r in rows]
        rr[i][k] = bad
        with pytest.raises(SC.CalendarRefused):
            SC.check_rows(rr)
    rr = [dict(r) for r in rows]
    rr[0]["price"] = 1
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(rr)


def test_session_ordinals_and_span_refused_when_wrong():
    rows = SC.build_rows(make())
    rr = [dict(r) for r in rows]
    rr[3]["session"] += 1
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(rr)
    rr = [dict(r) for r in rows]
    rr[3]["sessions_left"] -= 1                           # the start not counted
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(rr)
    short = SC.build_rows(make(DAYS[:-1]))
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(short)                               # does not reach 2023-12-29
    assert SC.check_rows(short, require_span=False) == DAYS[:-1]
    late = SC.build_rows(make(DAYS[1:]))
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(late)                                # does not start at 2020-01-02
    swapped = [dict(r) for r in rows]
    swapped[2]["date"], swapped[3]["date"] = swapped[3]["date"], swapped[2]["date"]
    with pytest.raises(SC.CalendarRefused):
        SC.check_rows(swapped, require_span=False)


def test_held_out_and_confirmation_dates_refused():
    rows = SC.build_rows(make())
    for d, exc in (("2024-01-02", DC.HeldOutDay), ("2026-07-17", DC.ConfirmationDay),
                   ("2027-01-04", DC.ConfirmationDay)):
        rr = [dict(r) for r in rows] + [dict(rows[-1], date=d)]
        with pytest.raises(exc):
            SC.check_rows(rr, require_span=False)
        with pytest.raises(exc):
            SC.guard_date(D(d))
    with pytest.raises(DC.HeldOutDay) as e:
        SC.guard_date(D("2023-12-30"))
    assert not isinstance(e.value, DC.ConfirmationDay)
    SC.guard_date(D("2023-12-29"))
    with pytest.raises(SC.CalendarRefused):
        SC.guard_date(D("2019-12-31"))
    with pytest.raises(DC.HeldOutDay):                    # the sources refuse a later day before any row is built
        make(DAYS + ["2024-01-02"])


def test_csv_round_trip():
    rows = SC.build_rows(make())
    text = SC.to_csv_text(rows)
    assert text.splitlines()[0] == ",".join(SC.COLUMNS)
    assert SC.parse_csv_text(text) == rows
    assert SC.parse_csv_text(text.replace("\n", "\r\n")) == rows
    with pytest.raises(SC.CalendarRefused):
        SC.parse_csv_text(text.replace("sessions_left", "left", 1))
    with pytest.raises(SC.CalendarRefused):
        SC.parse_csv_text(text.replace("\n2020-01-03,Fri,2,", "\n2020-01-03,Fri,x,", 1))


# ---------------------------------------------------------------------------------------------------- the identities


def test_identities_hold_on_the_built_rows():
    src = make()
    rows = SC.build_rows(src)
    rec = SC.identities(SC.parse_csv_text(SC.to_csv_text(rows)), src)
    assert rec["I-1"] == {"dates": len(DAYS), "h2_flags_dates": len(DAYS), "held": True}
    i2 = rec["I-2"]
    assert i2["held"] and i2["days"] == len(DAYS) and i2["h2_void_days"] == 1
    assert i2["void_days"] == {c: sum(r[f"void_{c}"] for r in rows) for c in SC.CLASSES}
    assert i2["void_days"] == {"day": 3, "overnight": 4, "overnight_0829": 5} and i2["prior_void_days"] == 10


def test_identity_1_refuses_a_count_or_a_date_differing_from_h2():
    src = make()
    rows = SC.build_rows(src)
    extra = make(flag_days=DAYS + ["2021-06-01"])          # H2 holds a date the store does not
    with pytest.raises(SC.CalendarIdentityError, match=r"\(I-1\).*14 search-year"):
        SC.identities(rows, extra)
    moved = make(flag_days=DAYS[:5] + ["2020-11-26"] + DAYS[6:])   # same count, one date moved
    with pytest.raises(SC.CalendarIdentityError, match=r"\(I-1\) the dates differ"):
        SC.identities(rows, moved)
    with pytest.raises(SC.CalendarIdentityError, match=r"\(I-1\)"):
        SC.identities(rows[:-1], src)


@pytest.mark.parametrize("col,val", [("void_day", 0), ("void_overnight", 0), ("void_overnight_0829", 0),
                                     ("why_void_overnight", "h2_missing"), ("prior_void", 1),
                                     ("why_prior_void", "roll"), ("bls", 1), ("fomc", 0)])
def test_identity_2_refuses_a_flag_differing_from_day_calendar(col, val):
    src = make()
    rows = SC.build_rows(src)
    i = DAYS.index("2020-03-16") if col != "prior_void" and col != "why_prior_void" else DAYS.index("2020-01-03")
    if col == "bls":
        i = DAYS.index("2020-01-03")
    rr = [dict(r) for r in rows]
    assert rr[i][col] != val
    rr[i][col] = val
    with pytest.raises(SC.CalendarIdentityError, match=r"\(I-2\)"):
        SC.identities(rr, src)


def test_identity_2_refuses_h2_void_day_not_void_overnight(monkeypatch):
    """The H2 cross-check stands on its own: a table that agrees day for day with a day_calendar which (wrongly)
    dropped H2's VOID verdict is still refused."""
    import dataclasses

    src = make(flags={**FLAGS, "2020-01-03": _flag(0, "VOID", "outside_hours")})
    assert SC.identities(SC.build_rows(src), src)["I-2"]["h2_void_days"] == 2
    real = DC.day_flags

    def no_h2(*a, **k):
        f = real(*a, **k)
        return dataclasses.replace(f, void=tuple(x for x in f.void if not x.startswith("h2_void")))

    monkeypatch.setattr(DC, "day_flags", no_h2)
    rows = SC.build_rows(src)
    assert by_date(rows)["2020-01-03"]["void_overnight"] == 0
    with pytest.raises(SC.CalendarIdentityError, match="H2's VOID days"):
        SC.identities(rows, src)


# --------------------------------------------------------------------------------------------------------- the digest


def test_calendar_digest_is_w42_r1s_form():
    ds = ["2020-01-02", "2020-01-03"]
    assert SC.calendar_digest(ds) == hashlib.sha256(b"2020-01-02\n2020-01-03\n").hexdigest()
    assert SC.calendar_digest([D(x) for x in ds]) == SC.calendar_digest(ds)
    assert SC.calendar_digest(ds) != SC.calendar_digest(ds[:1])
    try:
        from extended import wave42                          # on master once W42-R1 merges
    except ImportError:
        return
    assert SC.calendar_digest(DAYS) == wave42.calendar_digest(DAYS)


def test_data_manifest_lookup(tmp_path):
    f = tmp_path / "DATA.sha256"
    f.write_text("a" * 64 + "  data/atlas/A1/days.parquet\n" + "b" * 64 + " *data/bars/NQ/manifest.json\n",
                 encoding="utf-8")
    assert SC.data_manifest_sha(f, "data/bars/NQ/manifest.json") == "b" * 64
    assert SC.data_manifest_sha(f, "data/atlas/A1/days.parquet") == "a" * 64
    assert SC.data_manifest_sha(f, "data/bars/NQ/bars.parquet") is None
    assert SC.data_manifest_sha(tmp_path / "absent", "data/bars/NQ/manifest.json") is None


# --------------------------------------------------------------------------------------------------------- the loader


def _write_fixture(folder: Path, rows, *, digest=None, sha=None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / SC.RESULT_NAME
    p.write_bytes(SC.to_csv_text(rows).encode("utf-8"))
    man = {"sha256": sha or hashlib.sha256(p.read_bytes()).hexdigest(),
           "parameters": {"calendar_sha256": digest or SC.calendar_digest([r["date"] for r in rows])}}
    Path(str(p) + ".manifest.json").write_text(json.dumps(man), encoding="utf-8")
    return p


def test_loader_returns_the_calendar_and_its_digest(tmp_path):
    rows = SC.build_rows(make())
    p = _write_fixture(tmp_path / "ok", rows)
    cal = SC.load_search_calendar(p)
    assert cal.dates == tuple(DAYS) and cal.calendar_sha256 == SC.calendar_digest(DAYS)
    assert cal.file_sha256 == hashlib.sha256(p.read_bytes()).hexdigest()
    assert list(cal.rows) == rows
    assert cal.session("2020-01-02") == 1 and cal.sessions_left("2020-01-02") == len(DAYS)
    assert cal.sessions_left("2023-12-29") == 1 and cal.sessions_left(D("2023-12-27")) == 2
    with pytest.raises(KeyError):
        cal.session("2020-01-06")


def test_loader_refusals(tmp_path):
    rows = SC.build_rows(make())
    p = _write_fixture(tmp_path / "a", rows)
    p.write_bytes(p.read_bytes().replace(b"Fri", b"Thu", 1))            # bytes not the manifest's
    with pytest.raises(SC.CalendarRefused, match="sha256"):
        SC.load_search_calendar(p)
    p = _write_fixture(tmp_path / "b", rows, digest="0" * 64)
    with pytest.raises(SC.CalendarRefused, match="calendar_sha256"):
        SC.load_search_calendar(p)
    p = _write_fixture(tmp_path / "c", rows)
    Path(str(p) + ".manifest.json").unlink()
    with pytest.raises(SC.CalendarRefused, match="manifest"):
        SC.load_search_calendar(p)
    p = _write_fixture(tmp_path / "d", SC.build_rows(make(DAYS[:-1])))   # short of 2023-12-29
    with pytest.raises(SC.CalendarRefused):
        SC.load_search_calendar(p)
    late = [dict(r) for r in rows] + [dict(rows[-1], date="2024-01-02", session=len(rows) + 1)]
    p = _write_fixture(tmp_path / "e", late)
    with pytest.raises(DC.HeldOutDay):
        SC.load_search_calendar(p)
    conf = [dict(r) for r in rows] + [dict(rows[-1], date="2026-07-17", session=len(rows) + 1)]
    p = _write_fixture(tmp_path / "f", conf)
    with pytest.raises(DC.ConfirmationDay):
        SC.load_search_calendar(p)


# ---------------------------------------------------------------------------------------------- the script, end to end


def _inputs(folder: Path, *, days=DAYS, flag_extra=()) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    later = ["2024-01-02", "2026-07-17"]                       # the store lists later days; nothing of them is kept
    man = {"day_list": days + later, "rolls": ROLLS + ["2024-03-15"], "early_end_days": ["2024-01-02"],
           "day_bounds": {d: ["17:00", LAST_BAR.get(d, "15:59")] for d in days + later},
           "parquet_sha256": "f" * 64}
    m = folder / "manifest.json"
    m.write_text(json.dumps(man), encoding="utf-8")
    c = folder / "calendar_early_closes.csv"
    c.write_text("# synthetic\ndate,kind,close_ct,source\n" + "".join(
        f"{k},{v['kind']},{v['close_ct']},{v['source']}\n" for k, v in sorted(CAL.items())), encoding="utf-8")
    f = folder / "h2_overnight_flags.csv"
    lines = ["day,verdict,void,special,missing_after_reopen"]
    for d in list(days) + list(flag_extra):
        r = FLAGS.get(d, _flag())
        lines.append(f"{d},{r['verdict']},\"{r['void']}\",{r['special']},{r['missing_after_reopen']}")
    f.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    Path(str(f) + ".manifest.json").write_text(json.dumps({"sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                                                           "git_commit": "abc1234"}), encoding="utf-8")
    return {"manifest": m, "calendar": c, "flags": f}


def _run(args, cwd):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    env.pop("S2X_CLEAN_RUN", None)
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=600)


def test_script_writes_the_calendar_with_every_input_hash(tmp_path):
    inp = _inputs(tmp_path / "in")
    out = tmp_path / "out"
    p = _run(["--manifest", inp["manifest"], "--calendar", inp["calendar"], "--flags", inp["flags"],
              "--out-dir", out], tmp_path)
    assert p.returncode == 0, p.stdout + p.stderr
    assert p.stdout.strip().splitlines()[-1] == "EXIT 0"
    csv_path = out / SC.RESULT_NAME
    cal = SC.load_search_calendar(csv_path)
    assert cal.dates == tuple(DAYS)
    man = json.loads(Path(str(csv_path) + ".manifest.json").read_text(encoding="utf-8"))
    par = man["parameters"]
    assert par["calendar_sha256"] == SC.calendar_digest(DAYS) == cal.calendar_sha256
    assert par["sessions"] == len(DAYS) and par["first"] == DAYS[0] and par["last"] == DAYS[-1]
    sha = lambda q: hashlib.sha256(Path(q).read_bytes()).hexdigest()  # noqa: E731
    ins = par["inputs"]
    assert ins["bars_manifest"]["sha256"] == sha(inp["manifest"]) and ins["bars_manifest"]["bars_read"] is False
    assert ins["calendar_early_closes"]["sha256"] == sha(inp["calendar"])
    assert ins["h2_flags"]["sha256"] == sha(inp["flags"]) == ins["h2_flags"]["manifest_records"]
    assert ins["h2_flags"]["manifest_sha256"] == sha(str(inp["flags"]) + ".manifest.json")
    assert ins["a1_days"] == "not read"
    assert len(ins["vendored_calendars"]) == 5 and all(len(v) == 64 for v in ins["vendored_calendars"].values())
    assert par["identities"]["I-1"]["held"] and par["identities"]["I-2"]["held"]
    assert par["rule2_threshold"] == 4 and par["walk_last_stamp"] == "15:07"
    assert man["columns"] == list(SC.COLUMNS) and man["rows"] == len(DAYS)
    text = csv_path.read_text(encoding="utf-8")
    assert "2024-01-02" not in text and "2026-07-17" not in text


def test_script_refuses_held_out_flags_and_a_missing_flags_manifest(tmp_path):
    inp = _inputs(tmp_path / "late", flag_extra=["2024-01-02"])
    p = _run(["--manifest", inp["manifest"], "--calendar", inp["calendar"], "--flags", inp["flags"],
              "--out-dir", tmp_path / "o1"], tmp_path)
    assert p.returncode == 2 and p.stdout.strip().splitlines()[-1] == "EXIT 2", p.stdout + p.stderr
    assert "HeldOutDay" in p.stdout and not (tmp_path / "o1").exists()
    inp = _inputs(tmp_path / "nomani")
    Path(str(inp["flags"]) + ".manifest.json").unlink()
    p = _run(["--manifest", inp["manifest"], "--calendar", inp["calendar"], "--flags", inp["flags"],
              "--out-dir", tmp_path / "o2"], tmp_path)
    assert p.returncode == 2 and not (tmp_path / "o2").exists(), p.stdout + p.stderr


def test_script_refuses_on_identity_1(tmp_path):
    inp = _inputs(tmp_path / "id1", flag_extra=["2021-06-01"])          # H2 holds a date the store does not
    p = _run(["--manifest", inp["manifest"], "--calendar", inp["calendar"], "--flags", inp["flags"],
              "--out-dir", tmp_path / "o"], tmp_path)
    assert p.returncode == 3 and "(I-1)" in p.stdout, p.stdout + p.stderr
    assert not (tmp_path / "o").exists()


def test_script_refuses_a_short_span(tmp_path):
    inp = _inputs(tmp_path / "short", days=DAYS[:-1])
    p = _run(["--manifest", inp["manifest"], "--calendar", inp["calendar"], "--flags", inp["flags"],
              "--out-dir", tmp_path / "o"], tmp_path)
    assert p.returncode == 2 and not (tmp_path / "o").exists(), p.stdout + p.stderr
