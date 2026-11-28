"""Q-229 corrective cycle 1 (the lead's ruling 3): W42-R1's and W42-R2's freezes checked **on disk**, in the fast tier.

`scripts/wave42_apply.py` and `scripts/wave42_r2_apply.py` refuse a run whose commit's diff from their pins touches any
of their `IMPORTED_FILES`; `extended/h4_audit.check_w42_freeze` (F4-3) does the same at H4-C. Both read commits, so a
staged change to a frozen file passed the pre-commit hook (whose tests saw HEAD) and only the next commit's tier caught
it (Q-229's `extended/results.py`). This test reads each frozen file **as the working tree holds it** -- what the hook's
tier sees of a commit being made -- and compares it, LF-normalised, with that file at its pinned commit:

* W42-R1's eleven files (`IMPORTED_FILES` of `scripts/wave42_apply.py`) against W42-R1's pin (`config/w42_r1_pin.json`)
  and against W42-R2's pin (whose freeze covers them too);
* W42-R2's three (`RULE_MODULE`, `SCRIPT`, `RULE_TEXT` of `scripts/wave42_r2_apply.py`) against W42-R2's pin
  (`config/w42_r2_pin.json`).

The lists are read from the pinned commits' own copies of the two scripts (by `ast`, nothing imported), so an edit on
disk cannot shorten the list it is checked by. Light: `git show` of fourteen files at two commits.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Callable

import pytest

ROOT = Path(__file__).resolve().parent.parent
R1_PIN, R2_PIN = "config/w42_r1_pin.json", "config/w42_r2_pin.json"
R1_SCRIPT, R2_SCRIPT, R2_MODULE = "scripts/wave42_apply.py", "scripts/wave42_r2_apply.py", "extended/wave42_r2.py"


def _show(commit: str, rel: str) -> bytes:
    out = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True, timeout=60)
    assert out.returncode == 0, f"{rel} at {commit[:12]}: {out.stderr.decode('utf-8', 'replace').strip()}"
    return out.stdout


def _lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def _pin(rel: str) -> str:
    c = json.loads(_show("HEAD", rel).decode("utf-8"))["commit"]
    assert isinstance(c, str) and len(c) == 40, rel
    return c


def _assigns(src: bytes) -> dict[str, ast.expr]:
    tree = ast.parse(src.decode("utf-8"))
    return {t.id: node.value for node in tree.body if isinstance(node, ast.Assign)
            for t in node.targets if isinstance(t, ast.Name)}


def frozen() -> dict[str, list[str]]:
    """Each frozen file and the pins it is checked against, the lists read from the pinned scripts."""
    r1, r2 = _pin(R1_PIN), _pin(R2_PIN)
    a1 = _assigns(_show(r1, R1_SCRIPT))
    r1_files = ast.literal_eval(a1["IMPORTED_FILES"])
    a2 = _assigns(_show(r2, R2_SCRIPT))
    assert ast.unparse(a2["IMPORTED_FILES"]) == "tuple(A.IMPORTED_FILES) + (RULE_MODULE, SCRIPT, RULE_TEXT)"
    assert ast.unparse(a2["SCRIPT"]) == "R2.APPLY_SCRIPT"
    script = ast.literal_eval(_assigns(_show(r2, R2_MODULE))["APPLY_SCRIPT"])
    r2_own = [ast.literal_eval(a2["RULE_MODULE"]), script, ast.literal_eval(a2["RULE_TEXT"])]
    assert len(r1_files) == 11 and len(set(r1_files) | set(r2_own)) == 14
    out = {f: [r1, r2] for f in r1_files}
    out.update({f: [r2] for f in r2_own})
    return out


def problems(read: Callable[[str], bytes]) -> list[str]:
    """Every frozen file whose working-tree copy (`read`) differs, LF-normalised, from its copy at a pin."""
    bad = []
    for rel, pins in frozen().items():
        try:
            disk = _lf(read(rel))
        except OSError as exc:
            bad.append(f"{rel}: cannot be read on disk ({exc})")
            continue
        for c in pins:
            if disk != _lf(_show(c, rel)):
                bad.append(f"{rel} differs on disk from its copy at the pin {c[:12]}")
    return bad


def on_disk(rel: str) -> bytes:
    return (ROOT / rel).read_bytes()


def test_the_frozen_files_on_disk_equal_their_pins():
    bad = problems(on_disk)
    assert not bad, ("a file W42-R1 or W42-R2 froze is changed in the working tree; scripts/wave42_apply.py, "
                     "scripts/wave42_r2_apply.py and H4's F4-3 would refuse every run after this commit:\n  "
                     + "\n  ".join(bad))


def test_the_list_covers_the_files_the_freeze_names():
    files = frozen()
    assert "extended/results.py" in files and files["extended/results.py"] == [_pin(R1_PIN), _pin(R2_PIN)]
    assert {"extended/wave42_r2.py", "scripts/wave42_r2_apply.py", "docs/plans/WAVE42_SETTING_RULE_R2.md"} <= set(files)


@pytest.mark.parametrize("rel", ["extended/results.py", "docs/plans/WAVE42_SETTING_RULE_R2.md", "extended/reader.py"])
def test_a_planted_edit_on_disk_fails(rel):
    # the plant: the working tree's copy of one frozen file with a line added (nothing on disk is written)
    def planted(r: str) -> bytes:
        b = on_disk(r)
        return b + b"# planted\n" if r == rel else b

    bad = problems(planted)
    assert bad and all(x.startswith(rel) for x in bad), bad


def test_a_missing_file_fails():
    def gone(r: str) -> bytes:
        if r == "extended/wave42.py":
            raise FileNotFoundError(r)
        return on_disk(r)

    assert problems(gone) == ["extended/wave42.py: cannot be read on disk (extended/wave42.py)"]


def test_line_endings_alone_do_not_fail():
    # the negative control: a CRLF checkout of a frozen file (core.autocrlf) is the same file
    def crlf(r: str) -> bytes:
        b = _lf(on_disk(r))
        return b.replace(b"\n", b"\r\n") if r == "extended/results.py" else b

    assert problems(crlf) == []
