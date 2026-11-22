"""Q-121b (the red team's M4 and M5 on RD-04's draft, `docs/reviews/DRAFT_RD-04_2026-11-17.md`): Q-121's module
`extended/vol_descriptive.py` takes an optional reader `Authorisation` in `check_span`, `check_days`, `describe`,
`summarise` and `output_problems`. On hand-built arrays and a temporary git tree only: no bar of the store is read.

* `test_the_frozen_copy_is_the_module_before_q121b` -- `tests/q121_module_a0cb1ce.py` is a0cb1ce's
  `extended/vol_descriptive.py` byte for byte (its LF sha256 pinned here), so the comparisons below are with the module
  as it was;
* `test_absent_the_behaviour_is_the_modules_before` -- with no authorisation, every refusal and acceptance of
  `check_span` and `check_days` (the same exception class name and message), `describe`'s and `summarise`'s frame on 30
  stub sessions (its CSV text), and `output_problems` on that frame and on tampered copies are the module's before;
* `test_child_script_output_unchanged` -- in a child process, `scripts/vol_descriptive.py` run on a toy half-year with
  the module now and with the frozen module before: the result file's sha256, the manifest's parameters and the printed
  identity and row lines are the same;
* `test_accepts_rd04s_judged_read_to_the_development_windows_last_day` -- an `Authorisation` made by the real
  `extended.reader.authorise` in a temporary tree (RD-04 declared and pinned, a simulated clean run) is accepted: the
  last day is 2026-07-16 (or the authorisation's earlier end), never later;
* `test_refuses_any_other_authorisation_before_anything` -- another purpose, kind, declaration, a choice-block
  authorisation, an unledgered one, one without a sha, a look-alike object: every entry point refuses
  (`AuthorisationRefused`) before it touches its input or computes a day;
* `test_the_confirmation_window_is_refused_always` -- 2026-07-17 refused without an authorisation, with RD-04's, and
  through a forged authorisation whose end reaches it (`ConfirmationWindowRefused`, also the reader's class);
* `test_the_last_day_is_capped_on_its_own` -- with the confirmation check patched out of the way, an authorisation
  ending after 2026-07-16 still describes nothing past 2026-07-16;
* `test_no_band_mark_from_the_judged_block` -- under RD-04's authorisation, on stub sessions from 2023-11 to 2024-02,
  `band_mark` rows cover choice-block sessions only (no 2024 year, no block reaching 2024-01-02, every count the
  choice-block walks'), `session`, `range` and `band` cover 2024; on judged sessions alone no `band_mark` row is
  written; `output_problems` refuses a `band_mark` row reaching the judged block, with or without an authorisation.

Seeds (named by role, outside the 2026xxxx range): `SEED_STUB_PATHS` 4231 (the stub sessions' random walks).
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402
import heldout_verdict_rows as VR  # noqa: E402  (Q-194c: the joint held-out test, ledgered, and its verdict)

SEED_STUB_PATHS = 4231
BEFORE = ROOT / "tests" / "q121_module_a0cb1ce.py"
#: the LF sha256 of `git show a0cb1ce:extended/vol_descriptive.py` (Q-121's module as merged by E-163)
BEFORE_SHA256 = "3f553bf0ac150bac10bca9e29fdcfcd344ebb5a9c6f55067939ee349953e49f6"
RD04 = "prereg/RD-04_volatility_drift.md"
RD03 = "prereg/RD-03_contract_levers.md"
F90 = "prereg/F-90_vol.md"
RUN = "q121b-sim"
N = V.SESSION_END + 1


def before_module():
    spec = importlib.util.spec_from_file_location("q121_module_a0cb1ce", BEFORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def random_day(rng: np.random.Generator, start: float = 13000.0, sd_ticks: float = 5.0) -> tuple[np.ndarray, ...]:
    steps = np.rint(rng.normal(0.0, sd_ticks, (N, 3)))
    path = start / V.TICK + np.cumsum(steps.ravel()).reshape(N, 3)
    o, c = path[:, 0] * V.TICK, path[:, 2] * V.TICK
    h, l = path.max(axis=1) * V.TICK, path.min(axis=1) * V.TICK
    for x in (o, h, l, c):
        x[0] = np.nan
    return o, h, l, c


def stub(first: str, last: str, early: int | None = 3):
    """Stub sessions (business days `first` to `last`): the days, their arrays, a bars frame of one row a day, and a
    `day_arrays` that counts its calls."""
    rng = np.random.default_rng(SEED_STUB_PATHS)
    days = pd.bdate_range(first, last).strftime("%Y-%m-%d").tolist()
    arrays = {d: random_day(rng, sd_ticks=3.0 + (i % 4)) for i, d in enumerate(days)}
    if early is not None:
        o = np.full(N, np.nan)
        o[1: 12 * 60 + 15 + 420 + 1] = 13000.0
        arrays[days[early]] = (o, o.copy(), o.copy(), o.copy())
    bars = pd.DataFrame({"ts": range(len(days)), "day": days, "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0})
    calls: list[str] = []

    def day_arrays(g):
        d = str(g["day"].iloc[0])
        calls.append(d)
        return arrays[d]

    return days, bars, day_arrays, calls


class Untouchable:
    """An input no refused call may touch."""

    def __getattr__(self, name):
        raise AssertionError(f"touched .{name} before refusing")

    def __getitem__(self, key):
        raise AssertionError(f"touched [{key!r}] before refusing")

    def __iter__(self):
        raise AssertionError("iterated before refusing")

    def __len__(self):
        raise AssertionError("measured before refusing")


# ------------------------------------------------------------------------------------------------ the tree


def git(t: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(t), *args], check=True, capture_output=True)


def sha_lf(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


TEXTS = {
    RD04: "# RD-04 (synthetic, Q-121b's tests)\n\n- **Judged-block reads:** `volatility_descriptive`\n",
    RD03: "# RD-03 (synthetic, Q-121b's tests)\n\n- **Judged-block reads:** `volatility_descriptive`\n",
    F90: "# F-90 (synthetic, Q-121b's tests)\n\n- **Judged-block reads:** `volatility_descriptive`\n",
}


@pytest.fixture
def tree(tmp_path, monkeypatch) -> Path:
    """A temporary git tree at `<tmp>/runs/<RUN>`: RD-04, RD-03 and F-90 (synthetic) each naming
    `volatility_descriptive` and each pinned in DECISIONS.md; a simulated clean run of it. Q-158, Q-194c: NQ's joint
    held-out test (the synthetic F-98) is read through the reader and ledgered, then its verdict row, so a described
    reading's judged read is admitted (the reader's held-out rule 4). Q-194e (P10): a family reads no held-out date, so
    the family's authorisation below is built by hand (as it would look), and stays this module's to refuse."""
    t = tmp_path / "runs" / RUN
    (t / "prereg").mkdir(parents=True)
    rows = []
    for i, (rel, text) in enumerate(TEXTS.items()):
        (t / rel).write_bytes(text.encode("utf-8"))
        rows.append(f"| E-{950 + i} | 2026-11-17 | **{rel} declared**, `{rel}` sha256 `{sha_lf(text)}` | test |")
    rows.append(f"| E-961 | 2026-11-17 | heldout-finalists: F-90 @ {sha_lf(TEXTS[F90])} list {'9' * 64} -- F-90's "
                "finalists | test |")
    (t / "DECISIONS.md").write_bytes(("# Decisions (synthetic)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
                                      + "\n".join(rows) + "\n").encode("utf-8"))
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    (t / "stand_in.bin").write_bytes(b"a stand-in for the seed's read, never parsed\n")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the synthetic tree")
    VR.settle(t, [t / "stand_in.bin"])
    monkeypatch.setattr(R, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.setenv("S2X_RUN_ID", "q121b-sim@run-1")
    return t


def rd04(t: Path, start: str = "2020-01-02", end: str = "2026-07-16", **kw) -> R.Authorisation:
    return R.authorise(start, end, purpose="volatility_descriptive", declaration=RD04, repo=t,
                       what="Q-121b test read", **kw)


# ------------------------------------------------------------------------------------------------ absent: unchanged


def test_the_frozen_copy_is_the_module_before_q121b():
    assert hashlib.sha256(BEFORE.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == BEFORE_SHA256
    old = before_module()
    assert old.LAST_DAY == V.LAST_DAY == R.CHOICE_END and old.COLUMNS == V.COLUMNS and old.SECTIONS == V.SECTIONS
    assert not hasattr(old, "check_authorisation"), "the frozen copy is the module before the change"


def _outcome(fn, *args):
    try:
        return ("ok", fn(*args))
    except Exception as exc:                                    # noqa: BLE001 -- compared, not swallowed
        return (type(exc).__name__, str(exc))


def test_absent_the_behaviour_is_the_modules_before():
    old = before_module()
    spans = [("2020-01-02", "2023-12-29"), ("2021-03-01", "2021-03-31"), ("2020-01-02", "2024-01-02"),
             ("2024-01-02", "2024-01-02"), ("2023-12-29", "2023-12-30"), ("2020-01-02", "2026-07-16"),
             ("2026-07-17", "2026-07-17"), ("2019-12-31", "2020-01-10"), ("2021-02-01", "2021-01-01"),
             (date(2022, 5, 2), pd.Timestamp("2022-05-03"))]
    for s, e in spans:
        assert _outcome(V.check_span, s, e) == _outcome(old.check_span, s, e), (s, e)
    for days in (["2023-12-28", "2023-12-29"], ["2023-12-29", "2024-01-02"], ["2026-07-17"], [],
                 ["2021-01-04", "2025-03-03", "2024-01-02"]):
        assert _outcome(V.check_days, days) == _outcome(old.check_days, days), days
    days, bars, arrays_new, calls_new = stub("2021-01-04", "2021-02-12")
    _, _, arrays_old, _ = stub("2021-01-04", "2021-02-12")
    fomc, bls = [V.yymmdd(days[5])], [V.yymmdd(days[7]), V.yymmdd(days[25])]
    s_new, w_new = V.describe(bars, fomc=fomc, bls=bls, day_arrays=arrays_new)
    s_old, w_old = old.describe(bars, fomc=fomc, bls=bls, day_arrays=arrays_old)
    assert s_new.to_csv(index=False) == s_old.to_csv(index=False)
    assert w_new.keys() == w_old.keys() and all(np.array_equal(w_new[k], w_old[k]) for k in V.SETS)
    f_new, f_old = V.summarise(s_new, w_new), old.summarise(s_old, w_old)
    assert f_new.to_csv(index=False) == f_old.to_csv(index=False)
    assert list(f_new.dtypes.astype(str)) == list(f_old.dtypes.astype(str))
    assert V.output_problems(f_new) == old.output_problems(f_old) == []
    for tamper in (lambda f: f.assign(side=1), lambda f: f[f["section"] != "band"],
                   lambda f: f.assign(date=f["date"].where(f.index != f.index[0], "2024-01-02")),
                   lambda f: f.assign(open_share=f["open_share"].where(f.index != f.index[-1], 1.5))):
        assert V.output_problems(tamper(f_new)) == old.output_problems(tamper(f_old))
    bad = pd.DataFrame({"ts": [1, 2], "day": ["2023-12-29", "2024-01-02"], "open": 1.0, "high": 1.0, "low": 1.0,
                        "close": 1.0})
    calls_before = len(calls_new)
    with pytest.raises(V.BeyondChoiceBlock):
        V.describe(bad, fomc=[], bls=[], day_arrays=arrays_new)
    assert len(calls_new) == calls_before, "absent, refused before anything is computed"


def test_child_script_output_unchanged():
    env = {**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    env.pop("S2X_CLEAN_RUN", None)
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "q121_synthetic.py"), "unchanged"], capture_output=True,
                       text=True, timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["after"]["rc"] == 0 and out["before"]["rc"] == 0, out
    assert out["after"]["module"] == "extended.vol_descriptive" and out["before"]["module"] == "q121_module_a0cb1ce"
    assert out["same_file"] and out["after"]["bytes"] > 100_000, out
    assert out["same_parameters"] and out["same_lines"], out
    assert out["after"]["parameters"]["last_day_refused_after"] == "2023-12-29"
    assert out["after"]["spans"] == out["before"]["spans"] == [["2021-01-04", "2021-06-30"]]


# ------------------------------------------------------------------------------------------------ present: RD-04's


def test_accepts_rd04s_judged_read_to_the_development_windows_last_day(tree):
    a = rd04(tree)
    assert (a.judged, a.kind, a.purpose, a.declaration) == (True, "described_reading", "volatility_descriptive", RD04)
    V.check_authorisation(a)
    assert V.last_day(a) == date(2026, 7, 16) == R.JUDGED_END and V.last_day() == V.LAST_DAY == date(2023, 12, 29)
    assert V.check_span("2020-01-02", "2026-07-16", authorised=a) == (date(2020, 1, 2), date(2026, 7, 16))
    assert V.check_span("2024-01-02", "2024-03-01", authorised=a) == (date(2024, 1, 2), date(2024, 3, 1))
    V.check_days(["2023-12-29", "2024-01-02", "2026-07-16"], authorised=a)
    with pytest.raises(V.BeyondChoiceBlock):
        V.check_days(["2024-01-02"])                                    # absent, the judged block is still refused
    short = rd04(tree, end="2024-06-28")
    assert V.last_day(short) == date(2024, 6, 28)
    V.check_days(["2024-06-28"], authorised=short)
    with pytest.raises(V.AuthorisationRefused):
        V.check_days(["2024-07-01"], authorised=short)
    with pytest.raises(V.AuthorisationRefused):
        V.check_span("2024-01-02", "2024-07-01", authorised=short)
    late = rd04(tree, start="2024-01-02")
    with pytest.raises(V.AuthorisationRefused):
        V.check_days(["2023-12-29"], authorised=late)                   # before the authorised span
    days, bars, arrays, calls = stub("2023-12-01", "2024-01-31")
    sessions, walks = V.describe(bars, fomc=[], bls=[], day_arrays=arrays, authorised=a)
    assert sessions["date"].tolist() == days and calls == days
    assert walks["dates"][-1] == days[-1]


def bad_authorisations(t: Path) -> dict[str, object]:
    a = rd04(t)
    choice = R.authorise("2020-01-02", "2023-12-29", purpose="volatility_descriptive", declaration=RD04, repo=t)
    assert not choice.judged
    # Q-194e (P10): no family's judged read is the reader's to make any more; its authorisation, as it would look
    family = dataclasses.replace(a, kind="family", declaration=F90, declaration_sha256=sha_lf(TEXTS[F90]))
    other_rd = R.authorise("2020-01-02", "2026-07-16", purpose="volatility_descriptive", declaration=RD03, repo=t)
    assert family.kind == "family" and other_rd.kind == "described_reading" and other_rd.declaration == RD03
    rep = dataclasses.replace
    return {
        "a choice-block authorisation": choice,
        "a family's judged read": family,
        "another described reading": other_rd,
        "another purpose": rep(a, purpose="stage_D_scorecard"),
        "no purpose": rep(a, purpose=None),
        "kind identity": rep(a, kind="identity"),
        "kind registered_design": rep(a, kind="registered_design", designs=("P-14",)),
        "kind family": rep(a, kind="family"),
        "another declaration path": rep(a, declaration="prereg/RD-04_volatility_drift_v2.md"),
        "an id, not the path": rep(a, declaration="RD-04"),
        "a backslashed path": rep(a, declaration=RD04.replace("/", "\\")),
        "judged False": rep(a, judged=False),
        "no judged block": rep(a, blocks=("choice",)),
        "unledgered": rep(a, ledgered=False),
        "no sha": rep(a, declaration_sha256=None),
        "an end before the start": rep(a, start=date(2025, 1, 2), end=date(2024, 1, 2)),
        "a start before the window": rep(a, start=date(2019, 12, 31)),
        "a look-alike": SimpleNamespace(**dataclasses.asdict(a)),
        "a dict": dataclasses.asdict(a),
        "a string": "volatility_descriptive",
    }


def test_refuses_any_other_authorisation_before_anything(tree):
    for why, bad in bad_authorisations(tree).items():
        with pytest.raises(V.AuthorisationRefused):
            V.check_authorisation(bad)
        with pytest.raises(V.AuthorisationRefused):
            V.last_day(bad)
        with pytest.raises(V.AuthorisationRefused):
            V.check_span("2021-01-04", "2021-01-05", authorised=bad)    # a choice-block span is still refused
        with pytest.raises(V.AuthorisationRefused):
            V.check_days(Untouchable(), authorised=bad)
        _, _, arrays, calls = stub("2021-01-04", "2021-01-08")
        with pytest.raises(V.AuthorisationRefused):
            V.describe(Untouchable(), fomc=Untouchable(), bls=Untouchable(), day_arrays=arrays, authorised=bad)
        assert calls == [], why
        with pytest.raises(V.AuthorisationRefused):
            V.summarise(Untouchable(), Untouchable(), authorised=bad)
        with pytest.raises(V.AuthorisationRefused):
            V.output_problems(Untouchable(), authorised=bad)
    assert issubclass(V.AuthorisationRefused, V.BeyondChoiceBlock), "a caller catching the refusal still catches it"


def test_the_confirmation_window_is_refused_always(tree):
    a = rd04(tree)
    for start, end in (("2026-07-16", "2026-07-17"), ("2026-07-17", "2026-07-17"), ("2020-01-02", "2027-01-04")):
        with pytest.raises(V.BeyondChoiceBlock):
            V.check_span(start, end)
        with pytest.raises(V.ConfirmationWindowRefused):
            V.check_span(start, end, authorised=a)
    with pytest.raises(V.BeyondChoiceBlock):
        V.check_days(["2026-07-17"])
    with pytest.raises(V.ConfirmationWindowRefused) as exc:
        V.check_days(["2026-07-16", "2026-07-17"], authorised=a)
    assert isinstance(exc.value, R.ConfirmationWindowRefused) and isinstance(exc.value, V.BeyondChoiceBlock)
    _, bars, arrays, calls = stub("2026-07-13", "2026-07-20", early=None)
    with pytest.raises(V.ConfirmationWindowRefused):
        V.describe(bars, fomc=[], bls=[], day_arrays=arrays, authorised=a)
    assert calls == [], "nothing is computed for a frame reaching the confirmation window"
    sessions = pd.DataFrame({"date": ["2026-07-16", "2026-07-17"], "day_kind": "n", "bars": 1, "range_pts": 1.0,
                             "range_pct": 0.1, "trail20_range_pts": np.nan, "trail20_range_pct": np.nan,
                             "band_ticks_010": pd.array([None, None], dtype="Int64"),
                             "band_ticks_025": pd.array([None, None], dtype="Int64"), "walked": True})
    with pytest.raises(V.ConfirmationWindowRefused):
        V.summarise(sessions, {"dates": ["2026-07-16", "2026-07-17"]}, authorised=a)
    frame = pd.DataFrame({c: [None] for c in V.COLUMNS})
    frame["section"], frame["date"] = "session", "2026-07-17"
    assert any("confirmation window" in p for p in V.output_problems(frame, authorised=a))
    assert any("choice block" in p for p in V.output_problems(frame))
    # a forged authorisation reaching the window: refused as the window, whatever the days asked for
    for end in (date(2026, 7, 17), date(2027, 1, 4)):
        forged = dataclasses.replace(a, end=end, judged_last=end)
        for call in (lambda: V.check_authorisation(forged), lambda: V.last_day(forged),
                     lambda: V.check_days(["2021-01-04"], authorised=forged),
                     lambda: V.check_span("2021-01-04", "2021-01-05", authorised=forged),
                     lambda: V.describe(Untouchable(), fomc=[], bls=[], authorised=forged),
                     lambda: V.summarise(Untouchable(), Untouchable(), authorised=forged),
                     lambda: V.output_problems(Untouchable(), authorised=forged)):
            with pytest.raises(V.ConfirmationWindowRefused):
                call()
    with pytest.raises(R.ConfirmationWindowRefused):
        rd04(tree, end="2026-07-17")                                    # the reader refuses it first, as ever
    assert V.AUTHORISED_LAST_DAY == R.JUDGED_END < R.CONFIRMATION_START


def test_the_last_day_is_capped_on_its_own(tree, monkeypatch):
    """The cap at 2026-07-16 does not rest on the confirmation check alone: with that check moved out of the way (the
    module's `CONFIRMATION_START` patched later), an authorisation ending after 2026-07-16 still describes nothing
    later."""
    a = rd04(tree)
    monkeypatch.setattr(V, "CONFIRMATION_START", date(2030, 1, 2))
    forged = dataclasses.replace(a, end=date(2026, 12, 31), judged_last=date(2026, 12, 31))
    assert V.last_day(forged) == date(2026, 7, 16)
    V.check_days(["2026-07-16"], authorised=forged)
    with pytest.raises(V.AuthorisationRefused):
        V.check_days(["2026-08-03"], authorised=forged)
    with pytest.raises(V.AuthorisationRefused):
        V.check_span("2026-07-01", "2026-07-20", authorised=forged)


# ------------------------------------------------------------------------------------------------ M5: band_mark


def _band_mark_ok(frame: pd.DataFrame) -> None:
    bm = frame[frame["section"] == "band_mark"]
    assert set(bm["period_kind"]) <= {"block", "year"}
    years = bm.loc[bm["period_kind"] == "year", "period"].astype(str)
    assert (years.astype(int) <= 2023).all()
    ends = bm.loc[bm["period_kind"] == "block", "period"].astype(str).str.split("..", regex=False).str[-1]
    assert (ends <= "2023-12-29").all()


def test_no_band_mark_from_the_judged_block(tree):
    a = rd04(tree)
    days, bars, arrays, _ = stub("2023-11-01", "2024-02-29")
    sessions, walks = V.describe(bars, fomc=[], bls=[], day_arrays=arrays, authorised=a)
    with pytest.raises(V.BeyondChoiceBlock):
        V.summarise(sessions, walks)                                    # absent, a judged session is refused
    frame = V.summarise(sessions, walks, authorised=a)
    assert V.output_problems(frame, authorised=a) == []
    assert any("choice block" in p for p in V.output_problems(frame)), "absent, the frame is not Q-121's"
    _band_mark_ok(frame)
    bm = frame[frame["section"] == "band_mark"]
    assert set(bm.loc[bm["period_kind"] == "year", "period"]) == {"2023"}
    choice = [d for d in walks["dates"] if d <= "2023-12-29"]
    assert len(bm) == 2 * (266 + 22) * 5 * 12
    assert bm["period"][bm["period_kind"] == "block"].iloc[0] == f"{choice[0]}..{choice[-1]}"
    # every band_mark count is the choice-block walks' count
    keep = np.array([d <= "2023-12-29" for d in walks["dates"]])
    E = walks["p16_marks"][keep]
    row = bm[(bm["period_kind"] == "block") & (bm["set"] == "p16_marks") & (bm["mark"] == 600) &
             (bm["band"] == "25pt") & (bm["rr"] == 1.0)].iloc[0]
    codes = E[:, V.P16_MARKS.index(600), :, 1, 3].ravel()
    assert row["n"] == int((codes != V.NONE).sum()) > 0
    # session, range and band reach the judged block
    assert frame.loc[frame["section"] == "session", "date"].max() == days[-1]
    for sec in ("range", "band"):
        assert "2024" in set(frame.loc[(frame["section"] == sec) & (frame["period_kind"] == "year"), "period"])
    # judged sessions alone: no band_mark row at all, and the frame is still the reading's
    _, jbars, jarrays, _ = stub("2024-01-02", "2024-02-29")
    js, jw = V.describe(jbars, fomc=[], bls=[], day_arrays=jarrays, authorised=a)
    jf = V.summarise(js, jw, authorised=a)
    assert (jf["section"] == "band_mark").sum() == 0 and V.output_problems(jf, authorised=a) == []
    assert {"session", "range", "band"} <= set(jf["section"])
    # output_problems refuses a band_mark row reaching the judged block, with or without an authorisation
    tmpl = bm.iloc[[0]].copy()
    for pk, p in (("year", "2024"), ("year", "2026"), ("block", f"{choice[0]}..2024-01-02"), ("quarter", "2023Q4")):
        bad = pd.concat([frame, tmpl.assign(period_kind=pk, period=p)], ignore_index=True)
        assert any("band_mark" in x for x in V.output_problems(bad, authorised=a)), (pk, p)
        q121 = pd.concat([frame[frame["date"].isna() | (frame["date"] <= "2023-12-29")],
                          tmpl.assign(period_kind=pk, period=p)], ignore_index=True)
        assert any("band_mark" in x for x in V.output_problems(q121)), (pk, p)
