"""Q-04: this repository's results writer (`extended/results.py`) over the vendored `propedge.reporting.results`.

Each check runs in a child process (CLAUDE.md: anything that imports the vendored engine runs in its own process --
the vendored `sha256_of` puts `vendor/stage2/scripts` on `sys.path`, whose `run_clean.py` and `status.py` would shadow
this repository's). Every write goes to a temporary folder or is refused before it writes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRELUDE = f"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, {str(ROOT)!r})
"""


def child(code: str, tmp: Path, env: dict[str, str] | None = None, drop: tuple[str, ...] = ()) -> dict:
    """Run `code` in its own interpreter (cwd this tree); it prints one JSON object last."""
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", *drop)}
    e.update(env or {})
    e["S2X_TMP"] = str(tmp)
    r = subprocess.run([sys.executable, "-c", PRELUDE + textwrap.dedent(code)], cwd=ROOT, capture_output=True,
                       text=True, timeout=300, env=e)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def test_importing_the_package_leaves_sys_path_alone(tmp_path):
    out = child("""
        before = list(sys.path)
        import extended
        same = sys.path == before
        root = extended.use_vendored_stage2()
        print(json.dumps({"same": same, "vendor": str(root), "path0": sys.path[0], "path1": sys.path[1],
                          "blas": os.environ.get("OPENBLAS_NUM_THREADS"), "omp": os.environ.get("OMP_NUM_THREADS"),
                          "results": str(extended.RESULTS_DIR), "root": str(extended.ROOT)}))
    """, tmp_path, drop=("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"))
    assert out["same"], "importing extended must not touch sys.path (the vendored path is put on only by the function)"
    assert Path(out["vendor"]) == ROOT / "vendor" / "stage2"
    assert Path(out["path0"]) == ROOT / "vendor" / "stage2" / "scripts" and Path(out["path1"]) == ROOT / "vendor" / "stage2"
    assert out["blas"] == "1" and out["omp"] == "1", "one BLAS thread"
    assert Path(out["results"]) == ROOT / "results" and Path(out["root"]) == ROOT


def test_write_read_verify_list_in_a_temporary_folder(tmp_path):
    out = child("""
        import pandas as pd
        import extended.results as X
        d = Path(os.environ["S2X_TMP"]) / "res"
        df = pd.DataFrame({"a": [1, 2], "b": [0.5, 1.25], "t": ["x", "y y"]})
        csv, man = X.write_result(df, "t_one", script="tests/test_extended_results.py", seed=1, parameters={"k": 1},
                                  results_dir=d)
        m = json.loads(Path(man).read_text(encoding="utf-8"))
        back = X.read_result(csv)
        text = X.read_result(csv, text=True)
        ok, msg = X.verify_result(csv)
        listed = X.list_results(d)
        Path(csv).write_text("a,b,t\\n9,9,z\\n", encoding="utf-8")
        ok2, _ = X.verify_result(csv)
        try:
            X.read_result(csv)
            raised = False
        except ValueError:
            raised = True
        print(json.dumps({"commit": m["git_commit"], "seed": m["seed"], "rows": m["rows"], "ok": ok,
                          "back": back.to_dict("list"), "text_t": list(text["t"]), "text_a": list(text["a"]),
                          "listed": [(r["file"], r["verified"]) for r in listed], "ok_after_edit": ok2,
                          "raised": raised, "clean_run": (m.get("provenance") or {}).get("clean_run")}))
    """, tmp_path)
    assert out["commit"].split("-")[0] == head(), "the manifest records this repository's commit (repo=ROOT)"
    assert out["seed"] == 1 and out["rows"] == 2 and out["ok"]
    assert out["back"] == {"a": [1, 2], "b": [0.5, 1.25], "t": ["x", "y y"]}
    assert out["text_a"] == ["1", "2"] and out["text_t"] == ["x", "y y"]
    assert out["listed"] == [["t_one.csv", True]]
    assert not out["ok_after_edit"] and out["raised"], "an edited result fails its manifest and is not read"
    assert out["clean_run"] is None, "a write outside results/ is not stamped as a clean run"


def test_results_dir_refused_outside_a_clean_run(tmp_path):
    out = child("""
        import pandas as pd
        import extended.results as X
        df = pd.DataFrame({"a": [1]})
        got = {}
        for label, d in (("default", None), ("explicit", X.RESULTS_DIR), ("below", X.RESULTS_DIR / "sub")):
            try:
                X.write_result(df, "t_refused_q04", script="t", seed=1, parameters={}, results_dir=d)
                got[label] = "written"
            except X.CleanRunRequired as e:
                got[label] = "refused: " + str(e)[:200]
        exists = (X.RESULTS_DIR / "t_refused_q04.csv").exists() or (X.RESULTS_DIR / "sub").exists()
        print(json.dumps({"got": got, "exists": exists}))
    """, tmp_path)
    assert all(v.startswith("refused") for v in out["got"].values()), out
    assert not out["exists"], "a refused write leaves nothing behind"


def test_marker_alone_is_not_a_clean_run(tmp_path):
    # the marker set, but this tree is not the checkout run_clean.py made under %LOCALAPPDATA%/stage2-extended-runs
    out = child("""
        import pandas as pd
        import extended.results as X
        try:
            X.write_result(pd.DataFrame({"a": [1]}), "t_marker_q04", script="t", seed=1, parameters={})
            print(json.dumps({"got": "written"}))
        except X.CleanRunRequired as e:
            print(json.dumps({"got": "refused", "why": str(e)}))
    """, tmp_path, env={"S2X_CLEAN_RUN": ROOT.name})
    assert out["got"] == "refused", out


def test_another_trees_results_refused(tmp_path):
    tree = tmp_path / "tree"
    (tree / "results").mkdir(parents=True)
    (tree / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
    (tree / "pyproject.toml").write_text('[project]\nname = "stage2-extended"\n', encoding="utf-8")
    out = child("""
        import pandas as pd
        import extended.results as X
        d = Path(os.environ["S2X_TMP"]) / "tree" / "results"
        try:
            X.write_result(pd.DataFrame({"a": [1]}), "t_other", script="t", seed=1, parameters={}, results_dir=d)
            print(json.dumps({"got": "written"}))
        except X.CleanRunRequired as e:
            print(json.dumps({"got": "refused"}))
    """, tmp_path, env={"S2X_CLEAN_RUN": "anything"})
    assert out["got"] == "refused"
    assert not (tree / "results" / "t_other.csv").exists()


def test_clean_run_writes_and_never_overwrites(tmp_path):
    # a simulated clean checkout: ROOT is <runs>/<name>, the marker names it
    out = child("""
        import pandas as pd
        import extended.results as X
        runs = Path(os.environ["S2X_TMP"]) / "runs"
        X.RUNS_DIR = runs
        X.ROOT = runs / "q04-sim"
        X.RESULTS_DIR = X.ROOT / "results"
        X.ROOT.mkdir(parents=True)
        df = pd.DataFrame({"a": [1, 2]})
        csv, man = X.write_result(df, "t_clean", script="t", seed=3, parameters={"p": 1})
        m = json.loads(Path(man).read_text(encoding="utf-8"))
        try:
            X.write_result(df, "t_clean", script="t", seed=3, parameters={"p": 1})
            again = "written"
        except X.ResultExists:
            again = "refused"
        print(json.dumps({"csv": str(csv), "prov": m.get("provenance"), "again": again}))
    """, tmp_path, env={"S2X_CLEAN_RUN": "q04-sim"})
    assert Path(out["csv"]) == tmp_path / "runs" / "q04-sim" / "results" / "t_clean.csv"
    assert out["prov"]["clean_run"]["name"] == "q04-sim"
    assert out["again"] == "refused", "a result file is never overwritten (DIRECTIVE Part 1)"
