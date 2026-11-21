"""Q-172: the exact-run difference count (`extended/exact_run_diffs.py`, `scripts/exact_run_diffs.py`) on synthetic
runner outputs: the starts chosen (the last 252, every 21st earlier); the horizons checked by the runner's rule (h < L,
the caveat near the cut); **a planted difference counted** -- a first payout moved by two sessions and a later pay day
appearing -- and nothing else; the refusals (a differing horizon unchecked or without its exact record, a checked set
off the rule, a chosen start missing or twice, a difference whose days agree); the frame's checks; the nested-cut
identity's logic on toy jobs (equal; a block changed before the shorter cut caught; one after it ignored; a late date
or a moved date caught); the script's refusals before any read. No seed (nothing is drawn).
"""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest

from extended import exact_run_diffs as X

ROOT = Path(__file__).resolve().parent.parent
N = 300                                     # a toy job of 300 search sessions: cut starts 48 .. 299, control 0, 21, 42


def rec(s: int, passes=(5, 30), funded=(31,), pays=(50, 80)) -> dict:
    return {"start_day": s, "start_date": f"d{s}", "pass_days": list(passes), "funded_days": list(funded),
            "pay_days": list(pays)}


def outs(planted: dict[int, dict] | None = None) -> list[dict]:
    out = []
    for s in X.choose_starts(N):
        r = rec(s)
        diffs = []
        for h, alt in (planted or {}).get(s, {}).items():
            r.setdefault("alt", {})[str(h)] = alt
            diffs.append(h)
        out.append({"rec": r, "checked": X.expected_checked(s, N), "differs": diffs})
    return out


def test_the_starts_and_the_horizons_checked():
    st = X.choose_starts(N)
    assert [s for s, g in st.items() if g == "control"] == [0, 21, 42]
    assert [s for s, g in st.items() if g == "cut"] == list(range(48, 300))
    st2 = X.choose_starts(1006)
    assert sum(g == "cut" for g in st2.values()) == 252 and sum(g == "control" for g in st2.values()) == 36
    assert X.expected_checked(0, N) == [21, 63, 90, 126]
    assert X.expected_checked(N - 126, N) == [21, 63, 90]           # L = 126: not checked at 126 (h < L)
    assert X.expected_checked(N - 21, N) == [] and X.expected_checked(N - 22, N) == [21]
    with pytest.raises(ValueError):
        X.choose_starts(252)


def test_a_planted_difference_is_counted():
    alt = rec(21, pays=(52, 60, 80))            # at 63: the first payout 50 -> 52, a second pay day (60) appears
    rows = X.count_rows(outs({21: {63: alt}}), design="p14", arm="point", response="off", n=N)
    f = X.frame(rows)
    assert X.output_problems(f) == []
    ch = f[f["section"] == "checked"].set_index(["group", "horizon"])
    assert int(ch.loc[("control", 63), "differing"]) == 1
    assert int(ch["differing"].sum()) == 1
    assert int(ch.loc[("control", 63), "checked"]) == 3 and int(ch.loc[("control", 63), "starts"]) == 3
    assert int(ch.loc[("cut", 126), "checked"]) == sum(1 for s in range(48, 300) if 126 < min(252, N - s))
    assert int(ch.loc[("cut", 126), "starts"]) == 252
    mv = f[f["section"] == "moved"]
    got = {(e, c, None if x is pd_na() else int(x), int(n)) for e, c, x, n in
           zip(mv["event"], mv["change"], mv["shift"].astype(object), mv["count"])}
    assert got == {("first_payout", "moved", 2, 1), ("later_pay", "appeared", None, 1)}, got
    # the same difference at a horizon before it shows nothing moved at 21 (no event up to 21 differs: refused)
    with pytest.raises(ValueError):
        X.count_rows(outs({21: {21: alt}}), design="p14", arm="point", response="off", n=N)


def pd_na():
    import pandas as pd

    return pd.NA


def test_the_counts_refuse_what_the_runner_would_not_make():
    o = outs()
    o[0]["differs"] = [126]                       # differs, no exact record
    with pytest.raises(ValueError):
        X.count_rows(o, design="p14", arm="point", response="off", n=N)
    o = outs({299: {21: rec(299, pays=(51, 80))}})  # start 299 has L = 1: it checks nothing, so cannot differ
    with pytest.raises(ValueError):
        X.count_rows(o, design="p14", arm="point", response="off", n=N)
    o = outs()
    i = [x["rec"]["start_day"] for x in o].index(250)
    assert o[i]["checked"] == [21]                  # L = 50
    o[i]["checked"] = [21, 63, 90, 126]             # off the rule for a cut start
    with pytest.raises(ValueError):
        X.count_rows(o, design="p14", arm="point", response="off", n=N)
    o = outs()
    with pytest.raises(ValueError):
        X.count_rows(o[:-1], design="p14", arm="point", response="off", n=N)
    with pytest.raises(ValueError):
        X.count_rows(o + [copy.deepcopy(o[0])], design="p14", arm="point", response="off", n=N)
    with pytest.raises(ValueError):
        X.classify(rec(0), rec(0), 126)


def test_the_frame_refuses_a_broken_count():
    f = X.frame(X.count_rows(outs({0: {90: rec(0, passes=(6, 30))}}), design="p14", arm="point", response="off",
                             n=N))
    assert X.output_problems(f) == []
    b = f.copy()
    i = b.index[b["section"] == "checked"][0]
    b.loc[i, "differing"] = int(b.loc[i, "checked"]) + 1
    assert X.output_problems(b)
    b = f.copy()
    b.loc[b.index[b["section"] == "moved"][0], "shift"] = pd_na()
    assert X.output_problems(b)
    b = f[~((f["section"] == "checked") & (f["horizon"] == 21) & (f["group"] == "cut"))]
    assert X.output_problems(b.reset_index(drop=True))


def test_the_nested_cut_logic_on_toys():
    long = {"dates": ["2022-12-28", "2022-12-29", "2022-12-30", "2023-01-03", "2023-01-04"],
            "blocks": [("a", 1.0), ("b", 2.0), ("c", 3.0), ("d", 4.0), ("e", 5.0)]}
    short = {"dates": long["dates"][:3], "blocks": list(long["blocks"][:3])}
    assert X.nested_problems(short, long, "2022-12-30") == []
    changed_after = copy.deepcopy(long)
    changed_after["blocks"][4] = ("e", 9.0)
    assert X.nested_problems(short, changed_after, "2022-12-30") == []
    changed_before = copy.deepcopy(long)
    changed_before["blocks"][1] = ("b", 2.0000001)
    assert X.nested_problems(short, changed_before, "2022-12-30")
    late = {"dates": long["dates"][:4], "blocks": list(long["blocks"][:4])}
    assert X.nested_problems(late, long, "2022-12-30")
    moved = {"dates": ["2022-12-28", "2022-12-30"], "blocks": list(long["blocks"][:2])}
    assert X.nested_problems(moved, long, "2022-12-30")
    assert X.nested_problems({"dates": [], "blocks": []}, long, "2021-01-01") == ["nothing compared"]


def _script(*args: str) -> subprocess.CompletedProcess:
    import os

    env = {k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"}
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "exact_run_diffs.py"), *args], capture_output=True,
                          text=True, timeout=600, cwd=str(ROOT), env=env)


def test_the_script_refuses_before_any_read():
    for args in ((), ("--starts", "3"), ("--check",)):
        r = _script(*args)
        assert r.returncode == 2, (args, r.stdout[-800:], r.stderr[-800:])
        assert "REFUSED" in r.stdout and "built:" not in r.stdout, args


def test_the_script_reads_only_through_the_cut():
    src = (ROOT / "scripts" / "exact_run_diffs.py").read_text(encoding="utf-8")
    for call in ("read_parquet(", "read_bars(", "read_walks(", "read_csv("):
        assert call not in src, call
    ident = (ROOT / "identity" / "search_cut_identity.py").read_text(encoding="utf-8")
    assert "with SC.cut(last) as log:" in ident and "read_parquet(" not in ident
