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


#: E-002's snapshot: 698 files, its manifest's own sha256 (DECISIONS.md E-002)
E002_FILES, E002_MANIFEST_SHA256 = 698, "ea4339bcfb50f87f647228561cd7ff0e0e38c386dfe8a022876d9d4f48d88130"

#: Q-61's six result files (family B's follow amplitude, E-036; P-15's screen, P-13's gate and stop distribution, E-026)
Q61_RESULTS = ("s1_sided_coin.csv", "s3_event_kinds.csv", "s3_latency.csv", "rc_reentry_screen.csv",
               "a3_brk30_gate.csv", "a3_brk30_stop_distribution.csv")


def _manifest_sha(hashes: dict[str, str]) -> str:
    """The sha256 of a manifest holding exactly `hashes`, in `write_manifest`'s form."""
    import hashlib

    return hashlib.sha256("".join(f"{h}  {rel}\n" for rel, h in sorted(hashes.items())).encode("utf-8")).hexdigest()


def test_every_listed_result_is_in_the_snapshot():
    """`RESULTS` and the snapshot agree: every listed result file is pinned, and the source record lists exactly the
    snapshot's result files."""
    have = V.read_manifest(V.MANIFEST)
    missing = [n for n in V.RESULTS if f"results/{n}" not in have]
    assert not missing, missing
    src = json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))
    assert sorted(src["result_files"]) == sorted(k for k in have if k.startswith("results/"))


def test_q61_results_present_with_their_sidecars():
    """The six files and their sidecar manifests are in the snapshot and its manifest, and each CSV's sha256 is the one
    its sidecar recorded when Stage 2 wrote it (so no byte changed on the way, line endings included)."""
    have = V.read_manifest(V.MANIFEST)
    for name in Q61_RESULTS:
        csv, side = f"results/{name}", f"results/{name}.manifest.json"
        assert csv in have and side in have, name
        assert (V.DEST / csv).is_file() and (V.DEST / side).is_file(), name
        meta = json.loads((V.DEST / side).read_text(encoding="utf-8"))
        assert meta["result_file"] == name
        assert V.sha256(V.DEST / csv) == meta["sha256"] == have[csv], name
        assert V.sha256(V.DEST / side) == have[side], name


def test_extensions_kept_e002s_files_byte_identical():
    """Each extension recorded in `STAGE2_SOURCE.json` only added files, from E-002's commit: taking its additions (and
    every later one's) away gives back the manifest it started from, byte for byte, and taking all of them away gives
    back E-002's 698-file manifest (its pinned sha256) -- so no file of E-002's snapshot changed."""
    have = V.read_manifest(V.MANIFEST)
    src = json.loads(V.SOURCE_JSON.read_text(encoding="utf-8"))
    exts = src.get("extensions", [])
    cur = dict(have)
    for ext in reversed(exts):
        assert ext["commit"] == src["commit"]
        assert ext["files_after"] == len(cur)
        assert all(a in cur and a.startswith("results/") for a in ext["added"]), ext["added"]
        cur = {k: v for k, v in cur.items() if k not in set(ext["added"])}
        assert ext["files_before"] == len(cur)
        assert _manifest_sha(cur) == ext["manifest_before_sha256"], ext["task"]
    assert len(cur) == E002_FILES
    assert _manifest_sha(cur) == E002_MANIFEST_SHA256
    assert len(have) == E002_FILES + sum(len(e["added"]) for e in exts)


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
