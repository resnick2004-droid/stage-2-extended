"""Q-172: the search cut at the read (`extended/search_cut.py`), on a toy vendored tree written here (no licensed file is
read): every wrapped table's rows after the cut's day are dropped as they are read, whatever filters or columns the
reader asks for; the bars manifest's `day_list` is read whole; any other parquet, and any other file under the data
folders (by `open`, `Path.read_text` or pandas' CSV reader), is refused; a cut past 2023-12-29 is refused; the patches
are undone on exit, even after a refusal; `check_dates` refuses a later day; the log's `problems` names a wrapped file
never read. Pure pandas; fast; no seed (nothing is drawn).

**How the tests read.** What the cut must catch is a vendored builder calling `pd.read_parquet` on a whole file
(`a3_resolution_map.load_a1`, `atlas_a3.cached_walk`). The tests stand in for that builder with a toy module written
into the temporary folder -- outside this repository, as the vendored tree's code is to it -- whose one function calls
`pandas.read_parquet` by name (the fixture `rp`). This repository's own code never calls a parquet reader here, so the
one-door scan (`tests/test_reader.py`) holds; the toy tables are synthetic, never Stage 2's.
"""
from __future__ import annotations

import builtins
import io
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

from extended import reader as R
from extended import search_cut as SC

DAYS = [(date(2022, 12, 26) + timedelta(days=i)).isoformat() for i in range(0, 420, 3)]   # 2022-12-26 .. 2024-02


#: the toy vendored builder's source: one function reading a parquet file whole, as `load_a1` and `cached_walk` do
BUILDER = "import pandas as pd\n\n\ndef read(path, **kw):\n    return pd.read_parquet(path, **kw)\n"


@pytest.fixture
def rp(tmp_path):
    """The toy builder's reader (a module outside this repository, as a vendored builder is)."""
    import importlib.util

    f = tmp_path / "toy_vendored_builder.py"
    f.write_text(BUILDER, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("toy_vendored_builder", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read


def toy_tree(root: Path) -> Path:
    a1, a3, bars = root / "data/atlas/A1", root / "data/atlas/A3", root / "data/bars/NQ"
    for d in (a1, a3, bars):
        d.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"date": DAYS, "slot": range(len(DAYS))}).to_parquet(a1 / "events.parquet", index=False)
    pd.DataFrame({"date": DAYS, "day_kind": ["n"] * len(DAYS)}).to_parquet(a1 / "days.parquet", index=False)
    pd.DataFrame({"date": DAYS, "x": [1.0] * len(DAYS)}).to_parquet(a3 / "walks.parquet", index=False)
    pd.DataFrame({"ts": range(len(DAYS)), "day": DAYS, "open": [1.0] * len(DAYS)}).to_parquet(bars / "bars.parquet",
                                                                                               index=False)
    pd.DataFrame({"x": [1, 2]}).to_parquet(a1 / "other.parquet", index=False)
    pd.DataFrame({"nodate": [1]}).to_parquet(a3 / "walks_nokey.parquet", index=False)
    (bars / "manifest.json").write_text(json.dumps({"day_list": DAYS}), encoding="utf-8")
    (a1 / "manifest.json").write_text(json.dumps({"inputs": {"days": len(DAYS), "last": DAYS[-1]}}), encoding="utf-8")
    (bars / "notes.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    return root


def test_the_cut_drops_every_later_row_as_it_is_read(tmp_path, rp):
    root = toy_tree(tmp_path / "v")
    with SC.cut(root=root) as log:
        for rel, key in (("data/atlas/A1/events.parquet", "date"), ("data/atlas/A1/days.parquet", "date"),
                         ("data/atlas/A3/walks.parquet", "date"), ("data/bars/NQ/bars.parquet", "day")):
            df = rp(root / rel)
            assert len(df) and df[key].max() <= "2023-12-29" and df[key].min() == DAYS[0], rel
            assert set(df[key]) == {d for d in DAYS if d <= "2023-12-29"}, rel
        # the reader's own filters, both shapes, and a column list without the key: still cut
        a = rp(root / "data/bars/NQ/bars.parquet", filters=[("day", ">=", "2023-06-01")])
        assert a["day"].max() <= "2023-12-29" and a["day"].min() >= "2023-06-01"
        b = rp(root / "data/bars/NQ/bars.parquet",
                            filters=[[("day", "<=", "2023-01-10")], [("day", ">=", "2023-12-01")]])
        assert b["day"].max() <= "2023-12-29" and (b["day"] <= "2023-01-10").any() and (b["day"] >= "2023-12-01").any()
        c = rp(root / "data/atlas/A1/events.parquet", columns=["slot"])
        assert len(c) == sum(d <= "2023-12-29" for d in DAYS)
        # the bars manifest's day_list is read whole, never cut
        m = json.loads((root / "data/bars/NQ/manifest.json").read_text(encoding="utf-8"))
        assert m["day_list"] == DAYS and m["day_list"][-1] > "2023-12-29"
    assert log.problems(["data/atlas/A1/events.parquet", "data/bars/*/bars.parquet"]) == []
    assert "data/bars/NQ/manifest.json" in log.files_read("passthrough")
    assert all(r.last_key <= "2023-12-29" for r in log.reads if r.kind == "cut" and r.last_key)
    assert log.problems(["data/atlas/A1/walks.parquet"]) == ["data/atlas/A1/walks.parquet: never read through the cut"]
    # outside the cut nothing is touched
    assert rp(root / "data/atlas/A1/days.parquet")["date"].max() == DAYS[-1]


def test_a_nested_cut_and_a_cut_past_the_search_years(tmp_path, rp):
    root = toy_tree(tmp_path / "v")
    with SC.cut(date(2022, 12, 30), root=root):
        assert rp(root / "data/atlas/A3/walks.parquet")["date"].max() <= "2022-12-30"
    for bad in (date(2023, 12, 30), date(2024, 1, 2), date(2026, 7, 17)):
        with pytest.raises(SC.LateRow):
            with SC.cut(bad, root=root):
                pass
    with pytest.raises(SC.LateRow):
        SC.authorise(purpose="x", declaration="E-232", what="t", last=date(2024, 1, 2))


def test_an_unwrapped_read_is_refused_and_the_patches_undone(tmp_path, rp):
    root = toy_tree(tmp_path / "v")
    real = (pd.read_parquet, builtins.open, io.open)
    for read in (lambda: rp(root / "data/atlas/A1/other.parquet"),
                 lambda: rp(root / "data/atlas/A3/walks_nokey.parquet"),
                 lambda: rp(tmp_path / "elsewhere.parquet"),
                 lambda: open(root / "data/bars/NQ/notes.csv", encoding="utf-8").read(),
                 lambda: (root / "data/bars/NQ/notes.csv").read_text(encoding="utf-8"),
                 lambda: pd.read_csv(root / "data/bars/NQ/notes.csv")):
        pd.DataFrame({"x": [1]}).to_parquet(tmp_path / "elsewhere.parquet", index=False)
        with pytest.raises(SC.UnwrappedRead):
            with SC.cut(root=root) as log:
                read()
        assert log.refused and log.problems()
        assert (pd.read_parquet, builtins.open, io.open) == real
    # a file outside the data folders (a config, a result) is not the cut's business
    (tmp_path / "config.yaml").write_text("a: 1\n", encoding="utf-8")
    with SC.cut(root=root) as log:
        assert (tmp_path / "config.yaml").read_text(encoding="utf-8") == "a: 1\n"
    assert log.problems() == []


def test_check_dates_is_the_backstop():
    SC.check_dates(["2020-01-02", "2023-12-29"])
    for late in ("2023-12-30", "2024-01-02", "2026-07-17"):
        with pytest.raises(SC.LateRow):
            SC.check_dates(["2023-12-28", late])
    with pytest.raises(SC.LateRow):
        SC.check_dates(["2022-12-30", "2023-01-03"], date(2022, 12, 30))


def test_the_wrapped_set_and_nothing_switched_off():
    assert SC.switched_off() == {}
    assert SC.LAST_DAY == R.CHOICE_END
    assert SC.wrapped_key("data/bars/NQ/bars.parquet") == "day"
    assert SC.wrapped_key("data/atlas/A1/events.parquet") == "date" and SC.wrapped_key("data/atlas/A2/x.parquet") is None
    assert SC.is_passthrough("data/bars/NQ/manifest.json") and not SC.is_passthrough("data/bars/NQ/bars.parquet")


def _junction(link: Path, target: Path) -> bool:
    import os
    import subprocess

    if os.name != "nt":
        return False
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, text=True)
    return r.returncode == 0


def test_the_cut_sees_through_the_data_junctions(tmp_path, rp):
    """In a worktree and a clean checkout `data/bars` and `data/atlas` are junctions into the main tree: a read
    through them resolves to the target, and is still cut (wrapped) or refused (unwrapped) -- the Q-172 check's first
    run refused A1's own events file here, failing closed."""
    store = toy_tree(tmp_path / "main")                      # the "main tree"'s data
    root = tmp_path / "wt" / "vendor"
    (root / "data").mkdir(parents=True)
    ok = all(_junction(root / "data" / g, store / "data" / g) for g in ("atlas", "bars"))
    if not ok:
        pytest.skip("no directory junctions here")
    try:
        with SC.cut(root=root) as log:
            df = rp(root / "data/atlas/A1/events.parquet")
            assert len(df) and df["date"].max() <= "2023-12-29"
            assert rp(root / "data/bars/NQ/bars.parquet")["day"].max() <= "2023-12-29"
            assert json.loads((root / "data/bars/NQ/manifest.json").read_text(encoding="utf-8"))["day_list"] == DAYS
        assert log.problems(["data/atlas/A1/events.parquet", "data/bars/*/bars.parquet"]) == []
        assert "data/atlas/A1/events.parquet" in log.files_read("cut")
        with pytest.raises(SC.UnwrappedRead):
            with SC.cut(root=root):
                rp(root / "data/atlas/A1/other.parquet")
        with pytest.raises(SC.UnwrappedRead):
            with SC.cut(root=root):
                (root / "data/bars/NQ/notes.csv").read_text(encoding="utf-8")
    finally:
        import os

        for g in ("atlas", "bars"):                          # unlink the junctions, never through them
            os.rmdir(root / "data" / g)
