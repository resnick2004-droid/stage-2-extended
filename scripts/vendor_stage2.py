"""Vendor Stage 2 read-only (E-002): a byte-exact snapshot of one committed Stage 2 tree, pinned by a manifest.

    python scripts/vendor_stage2.py --source "../Stage 2"            # the snapshot (refused if one exists)
    python scripts/vendor_stage2.py --source "../Stage 2" --data     # also the licensed bars and the atlas walks
    python scripts/vendor_stage2.py --verify                         # the snapshot and the data against their manifests
    python scripts/vendor_stage2.py --source "../Stage 2" --extend Q-61   # add listed results, same commit (Q-61)

**What is taken.** `git archive` of Stage 2 at `COMMIT` (never the working copy, so nothing uncommitted can enter) for
the paths in `CODE` (the engine, its scripts, its configuration and rules, stage one's vendored tree, the protocol
documents and the registrations) and the result files in `RESULTS` with their sidecar manifests: the inputs of the
identity (`identity/stage2_identity.py`; the list was taken by running it against Stage 2 with every opened file
logged), the registered gate rows of P-14, P-15 and P-16, and every file the handoff
(`docs/HANDOFF_NEW_REPO_2026-11-15.md`, vendored) cites. Written to `vendor/stage2/`; its sha256 list to
`vendor/MANIFEST_stage2.sha256` (native `sha256sum` format, paths relative to `vendor/stage2/`); the source commit and
the path lists to `vendor/STAGE2_SOURCE.json`.

**The data (`--data`).** `data/bars/` (the operator's Databento NQ 1-minute bars, licensed for private use) and
`data/atlas/` (walks derived from them) are copied from Stage 2's working tree into `vendor/stage2/data/` -- ignored by
git, never committed -- and their hashes written to `vendor/DATA_MANIFEST_stage2.sha256` (names and hashes only), or,
when that manifest already exists, checked against it.

**Adding result files (`--extend TASK`, Q-61).** A result file of the same commit that later work needs is added to
`RESULTS` (with a comment naming why) and taken by `--extend`: from the snapshot's own commit only, after a fresh
archive of the whole snapshot's paths has reproduced every file already in it hash for hash; nothing already vendored
is rewritten, and `STAGE2_SOURCE.json` records the extension (task, files added, counts, the prior manifest's sha256).

Nothing under `vendor/stage2/` is ever edited; a newer Stage 2 is a new snapshot under a new decision row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "vendor" / "stage2"
MANIFEST = ROOT / "vendor" / "MANIFEST_stage2.sha256"
DATA_MANIFEST = ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"
SOURCE_JSON = ROOT / "vendor" / "STAGE2_SOURCE.json"

#: Stage 2's master at the handoff (f1b42e2, D-669 and docs/HANDOFF_NEW_REPO_2026-11-15.md)
COMMIT = "f1b42e2"

CODE = (
    "propedge", "scripts", "config", "vendor", "prereg", "data/README.md",
    "data/release_days_0830_2009_2025.csv", "data/release_days_0830_2026.csv",
    "data/releases_bls_0830_2009_2025.csv", "data/releases_bls_0830_2009_2025.provenance.json",
    "data/releases_bls_0830_2026.csv", "data/releases_bls_0830_2026.provenance.json",
    "data/releases_bls_all_2009_2025.csv",
    "pyproject.toml", "CHARTER.md", "DECISIONS.md", "RULES_LEDGER.md", "CLAUDE.md",
    "docs/HANDOFF_NEW_REPO_2026-11-15.md", "docs/HANDOFF_SEARCH_PROGRAM.md", "docs/RESEARCH_PROTOCOL.md",
    "docs/SUCCESS_CRITERIA.md", "docs/USER_MILESTONES.md", "docs/OPERATOR_SETUP.md", "docs/AUTONOMOUS_PROGRAM.md",
    "docs/research_inbox/EDGE_LITERATURE_2026-11-15.md",
)

#: result files (each taken with its `.manifest.json` where one exists)
RESULTS = (
    # the identity's inputs (logged by identity/stage2_identity.py --log-reads against Stage 2)
    "a3_brk30_cb20_gate_paths.csv", "rc_s150_all_gate_paths.csv", "a3_resolution_map.csv",
    "state_policy_v12_noclose.csv", "state_policy_v12_noclose_policies.json", "state_policy_v12_policies.json",
    # the registered gate rows: P-14, P-15, P-16, and the scoreboard
    "a3_brk30_cb20_gate.csv", "rc_s100_all_gate.csv", "rc_s150_all_gate.csv", "scoreboard.csv",
    # the handoff's sources
    "user_journey.csv", "user_drivers.csv", "u_budget.csv", "u_entry.csv", "u_seats.csv", "u_hours.csv",
    "u_firms.csv", "u_consistency.csv", "u_plan.csv", "u_limit.csv", "u_resolve.csv", "u_size_fit.csv",
    "u_value_map.csv", "u_xfa_day_budget.csv", "stop_band.csv", "setups_per_day.csv", "rc_width_screen.csv",
    "v1_validation_a0.csv", "v1_validation_a1.csv", "v1_validation_a2.csv", "v1_validation_b1.csv",
    "v1_validation_b2.csv", "v1_validation_b3.csv", "v1_validation_c1.csv", "v1_validation_c2.csv",
    # --- added by `--extend Q-61` from the same commit (E-002's 698 files unchanged) ---
    # family B's follow amplitude (E-036): Stage 2's sided coin (batch S1) and the event-kind and latency screens (S3)
    "s1_sided_coin.csv", "s3_event_kinds.csv", "s3_latency.csv",
    # P-15's screen file, so its own builder runs (`user_journey.build_p15` -> `rc_dev_test.trade_problems`, which
    # checks the file against the pinned `rc_dev_test.SCREEN_SHA256`; E-026)
    "rc_reentry_screen.csv",
    # P-13's gate row and stop distribution, so Stage 2's own P-14-against-P-13 checks run (`a3_brk30_cb20`'s
    # `P13_RESULT` against its pinned sha256, and `P13_STOPS`' fresh decisions; E-026)
    "a3_brk30_gate.csv", "a3_brk30_stop_distribution.csv",
    # --- added by `--extend Q-129` from the same commit (E-172; landed in the sequenced merge Q-140, E-156) ---
    # v12's `rungs` block inputs, read by the solver RD-03's stage 0 re-runs (RD-03 sections 6.1 (a) and 6.4 item 1)
    "fv3_rung_shares_2020.csv", "fv3_rung_availability_2021.csv",
    # D-559's one-rung table and its policies, which the vendored `scripts/u_size_fit.py` runner also requires
    # (RD-03 section 6.1; the runner's lines 102-103, 183-187, 313-316, 411-428)
    "rc150_table_screen.csv", "rc150_table_screen_policies.json",
)

DATA_DIRS = ("data/bars", "data/atlas")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hashes(base: Path, skip: tuple[str, ...] = ()) -> dict[str, str]:
    out = {}
    for p in sorted(base.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if any(rel == s or rel.startswith(s + "/") for s in skip) or "/__pycache__/" in f"/{rel}":
            continue
        out[rel] = sha256(p)
    return out


def write_manifest(path: Path, hashes: dict[str, str]) -> None:
    path.write_text("".join(f"{h}  {rel}\n" for rel, h in sorted(hashes.items())), encoding="utf-8", newline="\n")


def read_manifest(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, rel = line.split("  ", 1)
            out[rel] = h
    return out


def git(source: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True).stdout


def result_paths(source: Path, full: str) -> list[str] | None:
    """`RESULTS` as paths in Stage 2's tree at `full`, each followed by its `.manifest.json` where one exists; None
    (refused, printed) when a listed file is not in that tree."""
    listed = set(git(source, "ls-tree", "-r", "--name-only", full).decode().splitlines())
    res = []
    for name in RESULTS:
        for rel in (f"results/{name}", f"results/{name}.manifest.json"):
            if rel in listed:
                res.append(rel)
        if f"results/{name}" not in listed:
            print(f"REFUSED: results/{name} is not in Stage 2's tree at {full[:7]}")
            return None
    return res


def archive_into(source: Path, full: str, paths: list[str], dest: Path) -> None:
    """`git archive` of `paths` at commit `full` (the committed tree, never the working copy), extracted into `dest`.
    The tar goes through a temporary file, not memory."""
    with tempfile.TemporaryFile() as fh:
        subprocess.run(["git", "-C", str(source), "archive", "--format=tar", full, "--", *paths], check=True,
                       stdout=fh, stderr=subprocess.PIPE)
        fh.seek(0)
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=fh) as tf:
            tf.extractall(dest, filter="data")


def snapshot(source: Path) -> int:
    if DEST.exists() and any(DEST.iterdir()):
        print(f"REFUSED: {DEST} exists; the snapshot is read-only (a newer Stage 2 is a new decision row)")
        return 3
    full = git(source, "rev-parse", f"{COMMIT}^{{commit}}").decode().strip()
    res = result_paths(source, full)
    if res is None:
        return 3
    archive_into(source, full, list(CODE) + res, DEST)
    hashes = tree_hashes(DEST, skip=DATA_DIRS)
    write_manifest(MANIFEST, hashes)
    SOURCE_JSON.write_text(json.dumps({
        "source": "Stage 2 (C:/Users/resni/OneDrive/Desktop/Stage 2; GitHub remote stage-2-propedge, private)",
        "commit": full, "taken": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": "git archive of the commit (the committed tree, never the working copy)",
        "decision": "E-002", "code_paths": list(CODE), "result_files": res, "files": len(hashes),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "data_not_committed": list(DATA_DIRS),
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"snapshot: {len(hashes)} files from Stage 2 {full[:7]} into {DEST.relative_to(ROOT)}; manifest written")
    return 0


def extend(source: Path, task: str) -> int:
    """Add to the existing snapshot the result files `RESULTS` lists that it lacks, from **the snapshot's own commit**,
    leaving every file already in it byte-identical. Refusing, with nothing written, unless (1) the snapshot matches
    its manifest, (2) `COMMIT` is the commit `STAGE2_SOURCE.json` records, (3) every listed result is in that commit's
    tree, and (4) a fresh `git archive` of the whole snapshot's paths at that commit reproduces every file already in
    the snapshot, hash for hash, and holds nothing beyond them but the files to add. Only then are the new files
    copied from that archive; the tree is hashed again and every old file's hash must be unchanged and every new
    file's the archive's before the manifest and the source record are rewritten. The record keeps each extension:
    its task, the files added, the counts before and after and the sha256 of the manifest it started from."""
    if not (DEST.is_dir() and MANIFEST.is_file() and SOURCE_JSON.is_file()):
        print(f"REFUSED: no snapshot to extend at {DEST} (take one first)")
        return 3
    old = read_manifest(MANIFEST)
    if tree_hashes(DEST, skip=DATA_DIRS) != old:
        print(f"REFUSED: {DEST} differs from {MANIFEST.name} (scripts/vendor_stage2.py --verify); nothing added")
        return 3
    rec = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    full = git(source, "rev-parse", f"{COMMIT}^{{commit}}").decode().strip()
    if rec.get("commit") != full:
        print(f"REFUSED: the snapshot is of Stage 2 {str(rec.get('commit'))[:7]} but COMMIT names {full[:7]}; an "
              "extension takes files from the snapshot's own commit (a newer Stage 2 is a new snapshot under a new "
              "decision row); nothing added")
        return 3
    res = result_paths(source, full)
    if res is None:
        return 3
    new = [r for r in res if r not in old]
    if not new:
        print(f"extend: nothing to add; vendor/stage2 holds every listed result ({len(old)} files)")
        return 0
    with tempfile.TemporaryDirectory(prefix="vendor_stage2_extend_") as tmp:
        fresh_dir = Path(tmp) / "stage2"
        archive_into(source, full, list(CODE) + res, fresh_dir)
        fresh = tree_hashes(fresh_dir)
        differ = sorted(k for k in old if fresh.get(k) != old[k])
        if differ:
            print(f"REFUSED: Stage 2 {full[:7]}'s archive does not reproduce {len(differ)} of the snapshot's "
                  f"{len(old)} files (e.g. {differ[:3]}; a different git core.autocrlf would do it); nothing added")
            return 3
        extra, missing = sorted(set(fresh) - set(old) - set(new)), sorted(set(new) - set(fresh))
        if extra or missing:
            print(f"REFUSED: the archive holds {extra[:3]} beyond the snapshot, or lacks {missing[:3]}; nothing added")
            return 3
        there = [r for r in new if (DEST / r).exists()]
        if there:
            print(f"REFUSED: {there[:3]} already exist under {DEST}; nothing is overwritten")
            return 3
        for rel in new:
            (DEST / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fresh_dir / rel, DEST / rel)
    after = tree_hashes(DEST, skip=DATA_DIRS)
    changed = sorted(k for k in old if after.get(k) != old[k])
    wrong = sorted(set(after) ^ (set(old) | set(new))) + sorted(r for r in new if after.get(r) != fresh[r])
    if changed or wrong:
        print(f"FAILED: after the copy, old files changed {changed[:3]} or new ones are wrong {wrong[:3]}; the "
              "manifest is not rewritten (the tree now fails --verify)")
        return 3
    before_sha = sha256(MANIFEST)
    write_manifest(MANIFEST, after)
    rec["result_files"] = res
    rec["files"] = len(after)
    rec.setdefault("extensions", []).append({
        "task": task, "taken": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": full,
        "method": "git archive of the same commit; every file already in the snapshot reproduced hash for hash by the "
                  "archive and unchanged after the copy; only the added files copied",
        "added": new, "files_before": len(old), "files_after": len(after), "manifest_before_sha256": before_sha,
    })
    SOURCE_JSON.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"extend ({task}): {len(new)} files added from Stage 2 {full[:7]}; {len(old)} files unchanged; manifest "
          f"{len(old)} -> {len(after)} files, sha256 {sha256(MANIFEST)}")
    return 0


def copy_data(source: Path) -> int:
    for d in DATA_DIRS:
        src, dst = source / d, DEST / d
        if not src.is_dir():
            print(f"REFUSED: {src} does not exist")
            return 3
        if not dst.exists():
            shutil.copytree(src, dst)
    hashes = {}
    for d in DATA_DIRS:
        hashes.update({f"{d}/{k}": v for k, v in tree_hashes(DEST / d).items()})
    if DATA_MANIFEST.exists():
        want = read_manifest(DATA_MANIFEST)
        if want != hashes:
            bad = sorted(set(want) ^ set(hashes)) + sorted(k for k in set(want) & set(hashes) if want[k] != hashes[k])
            print(f"REFUSED: the data differ from {DATA_MANIFEST.name} ({len(bad)} files, e.g. {bad[:3]})")
            return 3
        print(f"data: {len(hashes)} files match {DATA_MANIFEST.name}")
    else:
        write_manifest(DATA_MANIFEST, hashes)
        print(f"data: {len(hashes)} files copied; {DATA_MANIFEST.name} written")
    return 0


def verify() -> int:
    want = read_manifest(MANIFEST)
    have = tree_hashes(DEST, skip=DATA_DIRS)
    if want != have:
        extra, missing = sorted(set(have) - set(want)), sorted(set(want) - set(have))
        changed = sorted(k for k in set(want) & set(have) if want[k] != have[k])
        print(f"FAILED: vendor/stage2 differs from its manifest -- changed {changed[:5]}, missing {missing[:5]}, "
              f"extra {extra[:5]}")
        return 3
    print(f"vendor/stage2: {len(have)} files match {MANIFEST.name}")
    if DATA_MANIFEST.exists() and all((DEST / d).is_dir() for d in DATA_DIRS):
        hashes = {}
        for d in DATA_DIRS:
            hashes.update({f"{d}/{k}": v for k, v in tree_hashes(DEST / d).items()})
        if hashes != read_manifest(DATA_MANIFEST):
            print("FAILED: the bars or the atlas differ from their manifest")
            return 3
        print(f"data: {len(hashes)} files match {DATA_MANIFEST.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", type=Path, default=ROOT.parent / "Stage 2")
    ap.add_argument("--data", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--extend", metavar="TASK", help="add the listed results the snapshot lacks, from its own commit "
                                                    "(TASK, e.g. Q-61, is recorded in STAGE2_SOURCE.json)")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    src = a.source.resolve()
    if a.extend:
        rc = extend(src, a.extend)
        if rc:
            return rc
    elif not (DEST.exists() and any(DEST.iterdir())):
        rc = snapshot(src)
        if rc:
            return rc
    return copy_data(src) if a.data else 0


if __name__ == "__main__":
    sys.exit(main())
