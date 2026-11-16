"""Q-61: `scripts/vendor_stage2.py --extend` adds result files to the existing snapshot from the same commit, and
leaves every file already in it byte-identical -- on a synthetic Stage 2 (a temporary git repository), never the real
one. Each refusal leaves the snapshot, its manifest and its source record untouched."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import vendor_stage2 as V  # noqa: E402

CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True,
                          env=CLEAN_ENV).stdout.strip()


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def _result(repo: Path, name: str, body: str) -> None:
    _write(repo / "results" / name, body)
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    _write(repo / "results" / f"{name}.manifest.json", json.dumps({"result_file": name, "sha256": sha}, indent=2))


@pytest.fixture
def stage2(tmp_path, monkeypatch):
    """A synthetic Stage 2 with two commits (the second changes the engine) and this repository's paths pointed at a
    temporary tree; the snapshot taken from the first commit with one result file."""
    src = tmp_path / "Stage 2"
    src.mkdir()
    _git(src, "init", "-q")
    # Stage 2's own line-ending rules (its .gitattributes at f1b42e2): result CSVs are never converted, so `git
    # archive` gives their committed bytes whatever core.autocrlf says
    _write(src / ".gitattributes", "* text=auto\nresults/*.csv -text\n")
    _write(src / "propedge" / "engine.py", "X = 1\n")
    _write(src / "CHARTER.md", "charter\n")
    _result(src, "x.csv", "a,b\n1,2\n")
    _result(src, "y.csv", "c\n3\n")
    _result(src, "z.csv", "d\n4\n")
    _git(src, "add", "-A")
    _git(src, "commit", "-q", "-m", "first")
    first = _git(src, "rev-parse", "HEAD")
    _write(src / "propedge" / "engine.py", "X = 2\n")
    _git(src, "commit", "-q", "-am", "second")
    second = _git(src, "rev-parse", "HEAD")

    root = tmp_path / "repo"
    monkeypatch.setattr(V, "ROOT", root)
    monkeypatch.setattr(V, "DEST", root / "vendor" / "stage2")
    monkeypatch.setattr(V, "MANIFEST", root / "vendor" / "MANIFEST_stage2.sha256")
    monkeypatch.setattr(V, "DATA_MANIFEST", root / "vendor" / "DATA_MANIFEST_stage2.sha256")
    monkeypatch.setattr(V, "SOURCE_JSON", root / "vendor" / "STAGE2_SOURCE.json")
    monkeypatch.setattr(V, "COMMIT", first[:7])
    monkeypatch.setattr(V, "CODE", ("propedge", "CHARTER.md"))
    monkeypatch.setattr(V, "RESULTS", ("x.csv",))
    assert V.snapshot(src) == 0
    return {"src": src, "first": first, "second": second, "root": root}


def _state() -> dict:
    """Every byte the snapshot holds, its manifest's and its source record's."""
    files = {p.relative_to(V.DEST).as_posix(): p.read_bytes() for p in sorted(V.DEST.rglob("*")) if p.is_file()}
    return {"files": files, "manifest": V.MANIFEST.read_bytes(), "source": V.SOURCE_JSON.read_bytes()}


def test_extend_adds_only_the_new_results_and_keeps_every_old_byte(stage2, monkeypatch):
    before = _state()
    old = V.read_manifest(V.MANIFEST)
    old_sha = hashlib.sha256(before["manifest"]).hexdigest()
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 0
    after = _state()
    for rel, data in before["files"].items():                  # every old file byte-identical
        assert after["files"][rel] == data, rel
    added = sorted(set(after["files"]) - set(before["files"]))
    assert added == ["results/y.csv", "results/y.csv.manifest.json"]
    new = V.read_manifest(V.MANIFEST)
    assert {k: v for k, v in new.items() if k in old} == old    # the old entries unchanged
    assert sorted(set(new) - set(old)) == added
    assert new["results/y.csv"] == hashlib.sha256(b"c\n3\n").hexdigest()
    src = json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))
    assert src["commit"] == stage2["first"]                    # the same commit, never the second
    assert src["files"] == len(new)
    assert src["result_files"] == ["results/x.csv", "results/x.csv.manifest.json", "results/y.csv",
                                   "results/y.csv.manifest.json"]
    (ext,) = src["extensions"]
    assert ext["task"] == "Q-TEST" and ext["added"] == added
    assert ext["files_before"] == len(old) and ext["files_after"] == len(new)
    assert ext["manifest_before_sha256"] == old_sha
    assert ext["commit"] == stage2["first"]
    assert V.verify() == 0


def test_extend_twice_adds_nothing_the_second_time(stage2, monkeypatch):
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 0
    once = _state()
    assert V.extend(stage2["src"], "Q-TEST") == 0
    assert _state() == once


def test_a_second_extension_is_recorded_beside_the_first(stage2, monkeypatch):
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-A") == 0
    mid = hashlib.sha256(V.MANIFEST.read_bytes()).hexdigest()
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv", "z.csv"))
    assert V.extend(stage2["src"], "Q-B") == 0
    exts = json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))["extensions"]
    assert [e["task"] for e in exts] == ["Q-A", "Q-B"]
    assert exts[1]["manifest_before_sha256"] == mid
    assert exts[1]["added"] == ["results/z.csv", "results/z.csv.manifest.json"]


def test_extend_refuses_an_edited_snapshot(stage2, monkeypatch):
    (V.DEST / "propedge" / "engine.py").write_bytes(b"X = 99\n")
    before = _state()
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 3
    assert _state() == before


def test_extend_refuses_another_commit(stage2, monkeypatch):
    before = _state()
    monkeypatch.setattr(V, "COMMIT", stage2["second"][:7])
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 3
    assert _state() == before


def test_extend_refuses_when_the_commit_does_not_reproduce_the_snapshot(stage2, monkeypatch):
    """A snapshot consistent with its own manifest but not with the commit's archive (a file and its manifest line
    rewritten together) is refused before anything is added."""
    p = V.DEST / "propedge" / "engine.py"
    p.write_bytes(b"X = 7\n")
    m = V.read_manifest(V.MANIFEST)
    m["propedge/engine.py"] = V.sha256(p)
    V.write_manifest(V.MANIFEST, m)
    assert V.verify() == 0
    before = _state()
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 3
    assert _state() == before


def test_extend_refuses_a_result_the_commit_lacks(stage2, monkeypatch):
    before = _state()
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "missing.csv"))
    assert V.extend(stage2["src"], "Q-TEST") == 3
    assert _state() == before


def test_extend_refuses_without_a_snapshot(tmp_path, monkeypatch):
    root = tmp_path / "empty"
    monkeypatch.setattr(V, "ROOT", root)
    monkeypatch.setattr(V, "DEST", root / "vendor" / "stage2")
    monkeypatch.setattr(V, "MANIFEST", root / "vendor" / "MANIFEST_stage2.sha256")
    monkeypatch.setattr(V, "SOURCE_JSON", root / "vendor" / "STAGE2_SOURCE.json")
    assert V.extend(tmp_path, "Q-TEST") == 3
    assert not root.exists()


def test_main_takes_extend_with_its_task(stage2, monkeypatch):
    monkeypatch.setattr(V, "RESULTS", ("x.csv", "y.csv"))
    assert V.main(["--source", str(stage2["src"]), "--extend", "Q-MAIN"]) == 0
    assert json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))["extensions"][0]["task"] == "Q-MAIN"
