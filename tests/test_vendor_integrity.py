"""E-002: the vendored Stage 2 tree is byte-for-byte the snapshot its manifest pins, from the commit it names."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import vendor_stage2 as V  # noqa: E402


def test_manifest_matches_tree():
    want = V.read_manifest(V.MANIFEST)
    have = V.tree_hashes(V.DEST, skip=V.DATA_DIRS)
    assert set(want) == set(have), (sorted(set(want) ^ set(have)))[:10]
    changed = [k for k in want if want[k] != have[k]]
    assert not changed, changed[:10]


def test_source_is_the_handoff_commit():
    src = json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))
    assert src["commit"].startswith(V.COMMIT)
    assert src["files"] == len(V.read_manifest(V.MANIFEST))


def test_licensed_data_never_tracked():
    import subprocess

    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "vendor/stage2/data/bars", "vendor/stage2/data/atlas"],
                         capture_output=True, text=True, check=True).stdout
    assert out.strip() == ""


def test_data_matches_its_manifest_when_present():
    if not all((V.DEST / d).is_dir() for d in V.DATA_DIRS):
        import pytest

        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    have = {}
    for d in V.DATA_DIRS:
        have.update({f"{d}/{k}": v for k, v in V.tree_hashes(V.DEST / d).items()})
    assert have == V.read_manifest(V.DATA_MANIFEST)
