"""No tracked or staged result file holds or reveals an NQ price level (Q-131; E-179, E-180; Q-130's scan automated).

The bars are licensed for private use: a committed table that holds a level, or lets one be recomputed (Q-121's
`range_pts` beside `range_pct`), redistributes them. `extended.price_levels` is the check; this file proves it refuses
what it should on synthetic tables built here (nothing licensed is committed or read for a value), runs it over every
tracked and staged CSV outside `vendor/`, keeps the allow-list from going stale, and checks it is wired into the
pre-commit hook. **Nothing here prints a cell's value**: findings carry file and column names and shares only.

Synthetic levels are built by arithmetic, not drawn: no randomness, so no seed.
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

from extended import price_levels as pl
from extended.lock_guard import main_root

ROOT = Path(__file__).resolve().parent.parent
Q121 = "results/q121_vol_descriptive_a1.csv"
#: the whole check over the repository is light: headers and a bounded sample; this bound only catches a regression
#: to reading whole files (measured near one second on this machine)
TIME_BUDGET_S = 120.0


# ------------------------------------------------------------------------------------------------------- helpers

def _levels(n: int, base: float = 14000.0) -> np.ndarray:
    """n distinct levels inside the band on the 0.25 grid, fractional ticks included (deterministic)."""
    k = (np.arange(n) * 7919) % 20000                  # an irregular walk over 20,000 ticks
    return base + 0.25 * k


def _write(path: Path, header: list[str], rows: list[list[object]], comments: tuple[str, ...] = ()) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        for c in comments:
            fh.write(f"# {c}\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([repr(float(v)) if isinstance(v, (float, np.floating)) else v for v in r])
    return path


def _scan(path: Path, name: str | None = None, **kw) -> list[pl.Finding]:
    return pl.scan_path(path, name=name or path.name, **kw)


def _cols(findings, rule: str) -> set[str]:
    return {f.column for f in findings if f.rule == rule}


def _pts_pct_table(n: int = 60) -> tuple[list[str], list[list[object]]]:
    """Q-121's leak in miniature: a range in points and the same range as a percentage of the session's open."""
    lev = _levels(n)
    pts = 0.25 * (40 + (np.arange(n) * 37) % 400)      # ranges on the tick grid
    pct = 100.0 * pts / lev
    shares = (np.arange(n) % 10) / 10.0
    return (["date", "x_pts", "x_pct", "share"],
            [[f"2021-03-{1 + i % 28:02d}", pts[i], pct[i], shares[i]] for i in range(n)])


def _clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items()
            if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX")}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=60, env=_clean_env())


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway git repository with an empty allow-list."""
    r = tmp_path / "repo"
    r.mkdir()
    assert _git(r, "init", "-q").returncode == 0
    _write(r / pl.ALLOWLIST_REL, ["file", "rule", "column", "reason"], [])
    return r


# ------------------------------------------------------------------------------------- positive controls (synthetic)

def test_a_points_column_beside_its_percentage_is_refused(tmp_path):
    header, rows = _pts_pct_table()
    found = _scan(_write(tmp_path / "results" / "leak.csv", header, rows))
    assert "100*x_pts/x_pct" in _cols(found, "pair")
    share = next(f.share for f in found if f.column == "100*x_pts/x_pct")
    assert share == 1.0


def test_a_points_column_over_its_fraction_is_refused(tmp_path):
    lev = _levels(40)
    pts = 0.25 * (8 + np.arange(40) % 50)
    found = _scan(_write(tmp_path / "f.csv", ["move_pts", "move_frac"],
                         [[pts[i], pts[i] / lev[i]] for i in range(40)]))
    assert "move_pts/move_frac" in _cols(found, "pair")


def test_a_sum_of_points_over_a_count_is_refused(tmp_path):
    n = 50
    bars = 3 + np.arange(n) % 17                         # a count of bars per session
    mean_level = _levels(n, base=9000.0)
    total = mean_level * bars                            # the sum of the bars' levels, in points
    found = _scan(_write(tmp_path / "f.csv", ["session", "total_pts", "n_bars"],
                         [[i, total[i], int(bars[i])] for i in range(n)]))
    assert "total_pts/n_bars" in _cols(found, "pair")


def test_a_column_of_levels_is_refused_whatever_its_name(tmp_path):
    lev = _levels(30)
    found = _scan(_write(tmp_path / "f.csv", ["day", "anchor"], [[i, lev[i]] for i in range(30)]))
    assert _cols(found, "level") == {"anchor"}


@pytest.mark.parametrize("name", ["open", "High", "low", "close", "price", "entry_price", "exit_price",
                                  "first_open", "rth_open_slot", "vwap", "settle", "stop_level", "OpenPrice",
                                  "session-close", "bid"])
def test_a_column_named_as_a_level_is_refused(tmp_path, name):
    found = _scan(_write(tmp_path / "f.csv", ["k", name], [[1, "x"], [2, "y"]]))
    assert _cols(found, "name") == {name}


@pytest.mark.parametrize("name", ["openings", "level", "ci_hi", "ci_lo", "lowest_rate", "closed_form", "reps",
                                  "first_mark", "stop_ticks", "entry_t", "share"])
def test_names_that_are_not_levels_pass(tmp_path, name):
    found = _scan(_write(tmp_path / "f.csv", ["k", name], [[1, "x"], [2, "y"]]))
    assert not _cols(found, "name")


def test_intraday_timestamps_beside_a_distance_are_refused(tmp_path):
    rows = [[f"2021-03-01 09:{30 + i:02d}:00", 0.25 * (i % 9)] for i in range(20)]
    found = _scan(_write(tmp_path / "f.csv", ["bar_time", "move_pts"], rows))
    assert _cols(found, "timestamp") == {"bar_time|move_pts"}


def test_intraday_clock_times_beside_a_level_are_refused(tmp_path):
    lev = _levels(20)
    found = _scan(_write(tmp_path / "f.csv", ["t", "anchor"], [[f"10:{i:02d}", lev[i]] for i in range(20)]))
    assert "t|anchor" in _cols(found, "timestamp")


def test_dates_and_clock_times_without_a_price_pass(tmp_path):
    rows = [[f"2021-03-{1 + i:02d}", f"2021-03-{1 + i:02d} 00:00:00", "13:00", i, 0.1 * i] for i in range(20)]
    found = _scan(_write(tmp_path / "f.csv", ["date", "stamp", "time_ct", "count", "share"], rows))
    assert found == []
    # a date written with a midnight time is a date: beside a distance it passes too
    rows = [[f"2021-03-{1 + i:02d} 00:00:00", 0.25 * i] for i in range(20)]
    assert _scan(_write(tmp_path / "g.csv", ["stamp", "stop_pts"], rows)) == []


def test_statistics_and_dollars_with_cents_pass(tmp_path):
    n = 200
    i = np.arange(n)
    rows = [[0.05 / (1 + j % 7), (j * 13) % 97, 10000.01 + 3.17 * j, 0.5 + 0.001 * j, 25.0 * (1 + j % 3)]
            for j in i]
    found = _scan(_write(tmp_path / "f.csv", ["level", "rejections", "net_dollars", "rate", "stop_dollars"], rows))
    assert found == []


def test_out_of_band_values_on_the_grid_pass(tmp_path):
    rows = [[0.25 * j, 40000 + 0.25 * j] for j in range(50)]
    assert _scan(_write(tmp_path / "f.csv", ["a_pts", "b"], rows)) == []


def test_in_band_values_off_the_tick_grid_pass(tmp_path):
    lev = _levels(50)
    found = _scan(_write(tmp_path / "f.csv", ["anchor", "x_pts", "x_pct"],
                         [[lev[i] + 0.1, 0.25 * (5 + i), 100 * 0.25 * (5 + i) / (lev[i] + 0.1)] for i in range(50)]))
    assert found == []


def test_comment_lines_are_skipped_and_the_sample_is_bounded(tmp_path):
    lev = _levels(30)
    p = _write(tmp_path / "f.csv", ["anchor"], [[v] for v in lev], comments=("a header comment", "another"))
    assert _cols(_scan(p), "level") == {"anchor"}
    # levels only after the sample: not seen (the documented bound), seen when the sample reaches them
    rows = [[0.5]] * 20 + [[v] for v in lev]
    q = _write(tmp_path / "g.csv", ["x"], rows)
    assert _scan(q, sample_rows=20) == []
    assert _cols(_scan(q, sample_rows=1000), "level") == {"x"}
    with open(q, encoding="utf-8", newline="") as fh:
        header, sample = pl.read_sample(fh, sample_rows=7)
    assert header == ["x"] and len(sample) == 7


def test_a_tiny_table_is_judged_on_every_row(tmp_path):
    lev = _levels(2)
    found = _scan(_write(tmp_path / "f.csv", ["a"], [[lev[0]], [lev[1]]]))
    assert _cols(found, "level") == {"a"}
    # in a longer table, two hits in a sparse column are not "mostly" (fewer than MIN_HITS); three are
    assert pl.MIN_HITS == 3
    sparse = [[lev[0], ""], [lev[1], ""]] + [["", i] for i in range(50)]
    assert _cols(_scan(_write(tmp_path / "g.csv", ["a", "k"], sparse)), "level") == set()
    lev3 = _levels(3)
    sparse3 = [[v, ""] for v in lev3] + [["", i] for i in range(50)]
    assert _cols(_scan(_write(tmp_path / "h.csv", ["a", "k"], sparse3)), "level") == {"a"}


def test_a_finding_prints_names_and_a_share_only(tmp_path):
    header, rows = _pts_pct_table(30)
    found = _scan(_write(tmp_path / "leak.csv", header, rows))
    text = " ".join(str(f) + repr(f) for f in found)
    for r in rows:
        for v in r[1:3]:
            assert repr(float(v)) not in text
    assert all(set(vars(f)) == {"file", "rule", "column", "share"} for f in found)


# ------------------------------------------------------------------------------------------------- the allow-list

def _allow(*entries: tuple[str, str, str]) -> list[pl.Allow]:
    return [pl.Allow(f, r, c, "a reason") for f, r, c in entries]


def test_the_allow_list_accepts_by_name_and_pattern_and_reports_stale_entries():
    fs = [pl.Finding("results/a.csv", "pair", "100*count_k1/ratio_k1", 1.0),
          pl.Finding("results/a.csv", "level", "reps", 1.0),
          pl.Finding("results/b.csv", "level", "reps", 1.0)]
    allow = _allow(("results/a.csv", "pair", "*count_*/ratio_*"), ("results/a.csv", "level", "reps"),
                   ("results/a.csv", "level", "trades"), ("results/c.csv", "pair", "*"))
    refused, stale = pl.apply_allowlist(fs, allow)
    assert refused == [fs[2]]                            # an entry is for its file only
    assert [a.column for a in stale] == ["trades", "*"]
    # the rule must match as well as the column
    refused, _ = pl.apply_allowlist([pl.Finding("results/a.csv", "name", "reps", 1.0)], allow)
    assert len(refused) == 1


def test_an_allow_listed_column_is_not_price_class_for_the_timestamp_rule(tmp_path):
    lev = _levels(20)
    p = _write(tmp_path / "f.csv", ["t", "count"], [[f"10:{i:02d}", lev[i]] for i in range(20)])
    assert _cols(_scan(p, name="f.csv"), "timestamp") == {"t|count"}
    allow = _allow(("f.csv", "level", "count"))
    assert _cols(_scan(p, name="f.csv", allow=allow), "timestamp") == set()


@pytest.mark.parametrize("rows, message", [
    ([["results/a.csv", "level", "x", ""]], "required"),
    ([["results/a.csv", "levels", "x", "why"]], "not one of"),
    ([["results/a.csv", "level", "x", "why"], ["results/a.csv", "level", "x", "again"]], "duplicate"),
])
def test_the_allow_list_file_is_validated(tmp_path, rows, message):
    p = _write(tmp_path / "allow.csv", ["file", "rule", "column", "reason"], rows)
    with pytest.raises(ValueError, match=message):
        pl.load_allowlist(p)


def test_every_allow_list_entry_has_a_reason_and_names_a_tracked_file():
    allow = pl.load_allowlist(ROOT / pl.ALLOWLIST_REL)
    assert allow, "the allow-list is seeded from Q-130's judged false positives"
    tracked = {p for p, _ in pl.candidate_entries(ROOT)}
    assert {a.file for a in allow} <= tracked
    assert all(len(a.reason) >= 10 for a in allow)


# ------------------------------------------------------------------------------- the check on a repository's index

def test_a_staged_leak_is_refused_from_the_index_and_by_the_hook_script(repo):
    header, rows = _pts_pct_table()
    _write(repo / "results" / "q999_leak.csv", header, rows)
    assert _git(repo, "add", "results/q999_leak.csv", pl.ALLOWLIST_REL).returncode == 0
    for source in ("index", "worktree"):
        rep = pl.check_tree(repo, source=source)
        assert rep.files == [pl.ALLOWLIST_REL, "results/q999_leak.csv"]
        assert ("results/q999_leak.csv", "pair", "100*x_pts/x_pct") in {(f.file, f.rule, f.column)
                                                                        for f in rep.refused}
    # the hook's own command, on the same index; its output names columns and never a value
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_price_levels.py"), "--root", str(repo),
                          "--index", str(repo / ".git" / "index")], capture_output=True, text=True, timeout=120,
                         env=_clean_env())
    assert out.returncode == 1
    text = out.stdout + out.stderr
    assert "results/q999_leak.csv" in text and "100*x_pts/x_pct" in text
    for r in rows:
        for v in r[1:3]:
            assert repr(float(v)) not in text


def test_the_index_mode_reads_what_is_staged_not_the_working_copy(repo):
    header, rows = _pts_pct_table()
    p = _write(repo / "results" / "q999_leak.csv", header, rows)
    assert _git(repo, "add", "-A").returncode == 0
    p.write_text("date,share\n2021-03-01,0.5\n", encoding="utf-8")      # the working copy cleaned, not re-staged
    assert pl.check_tree(repo, source="worktree").refused == []
    assert pl.check_tree(repo, source="index").refused != []


def test_vendor_files_and_untracked_files_are_not_scanned(repo):
    header, rows = _pts_pct_table()
    _write(repo / "vendor" / "stage2" / "results" / "x.csv", header, rows)
    _write(repo / "results" / "untracked.csv", header, rows)
    _write(repo / "docs" / "y.csv", header, rows)
    assert _git(repo, "add", "vendor", "docs", pl.ALLOWLIST_REL).returncode == 0
    rep = pl.check_tree(repo, source="index")
    assert rep.files == [pl.ALLOWLIST_REL, "docs/y.csv"]          # a CSV outside results/ and vendor/ is scanned
    assert {f.file for f in rep.refused} == {"docs/y.csv"}


def test_a_clean_staged_file_passes_the_hook_script(repo):
    _write(repo / "results" / "ok.csv", ["level", "count"], [[0.05, 10000], [0.01, 9000], [0.1, 8000]])
    assert _git(repo, "add", "-A").returncode == 0
    allow = repo / pl.ALLOWLIST_REL
    _write(allow, ["file", "rule", "column", "reason"],
           [["results/ok.csv", "level", "count", "a count of replications"]])
    assert _git(repo, "add", "-A").returncode == 0
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_price_levels.py"), "--root", str(repo)],
                         capture_output=True, text=True, timeout=120, env=_clean_env())
    assert out.returncode == 0, out.stdout + out.stderr


def test_a_stale_entry_fails_the_hook_script(repo):
    _write(repo / "results" / "ok.csv", ["share"], [[0.5], [0.25]])
    _write(repo / pl.ALLOWLIST_REL, ["file", "rule", "column", "reason"],
           [["results/ok.csv", "level", "share", "classed once, no longer found"]])
    assert _git(repo, "add", "-A").returncode == 0
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_price_levels.py"), "--root", str(repo)],
                         capture_output=True, text=True, timeout=120, env=_clean_env())
    assert out.returncode == 1 and "stale" in out.stdout + out.stderr


# ----------------------------------------------------------------------------------------------- this repository

def test_no_tracked_or_staged_csv_reveals_a_price_level_and_the_allow_list_is_not_stale():
    t0 = time.perf_counter()
    rep = pl.check_tree(ROOT)
    elapsed = time.perf_counter() - t0
    print(f"\nprice-level check: {len(rep.files)} files, {len(rep.findings)} findings, "
          f"{len(rep.findings) - len(rep.refused)} allow-listed, {elapsed:.2f} s")
    assert any(f.startswith("results/") for f in rep.files)
    assert not rep.refused, "refused (file: rule column (share)); class each by meaning or remove the file:\n" + \
        "\n".join(map(str, rep.refused))
    assert not rep.stale, "stale allow-list entries (they match nothing):\n" + \
        "\n".join(f"{a.file},{a.rule},{a.column}" for a in rep.stale)
    assert elapsed < TIME_BUDGET_S


def _q121_copies() -> list[Path]:
    roots = [ROOT]
    main = main_root(ROOT)
    if main is not None and main.resolve() != ROOT.resolve():
        roots.append(main)
    return [r / Q121 for r in roots if (r / Q121).is_file()]


def test_the_known_offender_is_flagged_when_present_locally():
    """Q-121's file (git-ignored, never committed) is the real positive control: read here for names and shares
    only, from this tree's results/ or the main tree's."""
    copies = _q121_copies()
    if not copies:
        pytest.skip(f"{Q121} is absent from this tree and the main tree; the synthetic controls above stand alone")
    for p in copies:
        found = pl.scan_path(p, name=Q121)
        refused, _ = pl.apply_allowlist(found, pl.load_allowlist(ROOT / pl.ALLOWLIST_REL))
        assert ("pair", "100*range_pts/range_pct") in {(f.rule, f.column) for f in refused}, \
            f"the check does not flag {p}: " + "; ".join(map(str, refused))


def test_the_known_offender_stays_untracked():
    assert Q121 not in {p for p, _ in pl.candidate_entries(ROOT)}


# ------------------------------------------------------------------------------------------------- the wiring

def test_the_pre_commit_hook_runs_the_check_on_the_commits_index():
    text = (ROOT / "scripts" / "pre-commit").read_text(encoding="utf-8")
    call = 'scripts/check_price_levels.py --index "$COMMIT_INDEX"'
    assert call in text
    keep = text.index('COMMIT_INDEX="${GIT_INDEX_FILE:-}"')
    unset = text.index("unset GIT_INDEX_FILE")
    assert keep < unset < text.index(call), "the commit's index is kept before the environment is cleared"
    assert text.index(call) < text.index('-m pytest'), "the check runs before the fast tier"
    assert "|| price_level_failed" in text
    assert "[ ! -f scripts/check_price_levels.py ]" in text, "a tree without the script is refused, not let through"
    assert b"\r\n" not in (ROOT / "scripts" / "pre-commit").read_bytes()


def test_the_merge_checklist_names_the_check():
    text = (ROOT / ".claude" / "skills" / "merge-checklist" / "SKILL.md").read_text(encoding="utf-8")
    sec4 = text[text.index("## 4."):text.index("## 5.")]
    assert "tests/test_results_no_price_levels.py" in sec4 and "licensed price" in sec4
