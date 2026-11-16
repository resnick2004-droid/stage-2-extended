"""F-03 (family O, `prereg/F-03_opening_timing.md`) the runs' refusing guards, T-9, T-11 and the reads (sections 9 A1,
12, 16, 19; E-052, E-094, E-095, E-098, E-104). Engine-free parts in this process; the guards that read Q-83's result file
through `extended.results` and the runner's command line in a process of their own.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from extended import lift_bound as LB
from extended import opening_run as R
from extended import opening_states as OS
from extended import reader

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
ENV = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
for _k in ("S2X_CLEAN_RUN", "S2X_RUN_ID"):
    ENV.pop(_k, None)


#: the token's lead-in (E-104); every token below is built at run time as `identity-holds: <id> @ <sha>`
LEAD = "identity-holds:"


def token_row(e: str, ident: str, sha: str, text: str = "the identity holds", date: str = "2026-11-17") -> str:
    """A row in E-104's positional form, built from its parts."""
    return f"| {e} | {date} | {LEAD} {ident} @ {sha} -- {text} | basis |"


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True,
                       env={**ENV, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                            "GIT_COMMITTER_EMAIL": "t@t"})
    return r.stdout.strip()


@pytest.fixture(scope="module")
def history(tmp_path_factory):
    """A toy repository: c1 (a.py, b.py), c2 (b.py changed), c3 (a.py changed) on main; a side commit off c1."""
    repo = tmp_path_factory.mktemp("tokens")
    _git(repo, "init", "-q", "-b", "main")
    (repo / "a.py").write_text("a = 1\n")
    (repo / "b.py").write_text("b = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c1")
    c1 = _git(repo, "rev-parse", "HEAD")
    (repo / "b.py").write_text("b = 2\n")
    _git(repo, "commit", "-q", "-am", "c2")
    c2 = _git(repo, "rev-parse", "HEAD")
    (repo / "a.py").write_text("a = 3\n")
    _git(repo, "commit", "-q", "-am", "c3")
    c3 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "-b", "side", c1)
    (repo / "c.py").write_text("c = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "side")
    side = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "main")
    return {"repo": repo, "c1": c1, "c2": c2, "c3": c3, "side": side}


def test_the_pinned_constants_are_e095s_and_e052s():
    assert R.K == 12 and R.LEVEL == LB.family_level(12) == 0.05 / 156
    assert R.DECLARATION_SHA256 == "fc64ae3cccf648ff5bf90f8cc7772ebb351c78763064ec0f856edb789860898a"
    assert R.PINNED_BLOBS == {"extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2",
                              "extended/p_bound.py": "f5b29710e243f97a2795e57f6458512fea99199b"}
    assert R.WAITED == ("Q-89", "Q-93", "Q-101", "Q-80")
    assert R.CELL_COUNTS == {"cells": 4, "dropped_at_pin": ["s3"], "searched": 0, "fitted_values": 11}


def test_the_pass_line_blobs_hold_at_head_and_a_changed_module_is_refused(tmp_path):
    assert R.blob_problems(ROOT) == []
    bad = R.blob_problems(ROOT, {"extended/lift_bound.py": "0" * 40})
    assert bad and "not the pinned" in bad[0]


def test_the_level_must_be_family_level_12():
    assert R.level_problems(R.LEVEL) == []
    assert R.level_problems(LB.family_level(13))
    assert R.level_problems(0.05 / 156 + 1e-15)


def test_the_declaration_is_pinned_unchanged_and_names_the_four_purposes():
    assert R.declaration_problems(ROOT, DECISIONS) == []
    assert reader.declared_purposes((ROOT / R.DECLARATION).read_text(encoding="utf-8")) == frozenset(R.PURPOSES)
    assert R.declaration_problems(ROOT, DECISIONS.replace(R.DECLARATION_SHA256, "f" * 64))
    for p in R.PURPOSES:
        assert not set(p.lower().split("_")) & reader.CHOICE_WORDS


def test_the_waits_read_the_one_parser_and_count_only_at_head_or_an_ancestor(history):
    from extended import identity_tokens as IT

    repo, c1, c2, c3, side = (history[k] for k in ("repo", "c1", "c2", "c3", "side"))
    head = "main"
    assert IT.held(token_row("E-1", "Q-89", c1), "Q-89", repo, head, ["a.py"]) is None   # a.py changed in c3
    assert IT.held(token_row("E-1", "Q-89", c2), "Q-89", repo, head, ["b.py"]).row == "E-1"
    assert IT.held(token_row("E-1", "Q-89", side), "Q-89", repo, head, ["b.py"]) is None  # not an ancestor
    two = "\n".join([token_row("E-1", "Q-89", c1), token_row("E-2", "Q-89", c2)])
    bad, rows = R.waited_problems(two, {"Q-89": ("b.py",), "Q-80": ("a.py",)}, repo, head)
    assert rows == {"Q-89": ["E-2"], "Q-80": []} and len(bad) == 1 and bad[0].startswith("Q-80 is not on record")
    lab = token_row("E-3", R.A0_ID, c3)
    assert R.waited_problems(lab, {R.A0_ID: ("a.py", "b.py")}, repo, head) == ([], {R.A0_ID: ["E-3"]})
    # a breach anywhere refuses before any wait is read; a covered path not at HEAD is refused
    quoted = f"| E-9 | 2026-11-17 | `{LEAD} Q-80 @ {c3}` -- quoted, held | b |"
    bad, rows = R.waited_problems(two + "\n" + quoted, {"Q-89": ("b.py",)}, repo, head)
    assert rows == {} and bad and "breaches the token rule" in bad[0]
    bad, _ = R.waited_problems(two, {"Q-89": ("nope.py",)}, repo, head)
    assert bad and "not in" in bad[0]
    assert R.A0_ID == "f03_a0" and IT.ID.fullmatch(R.A0_ID) and not IT.ID.fullmatch("f03-a0")


def test_every_wait_covers_the_base_its_script_and_every_module_it_imports():
    w = R.waits()
    assert set(w) == {*R.WAITED, R.A0_ID}
    for ident, covered in w.items():
        assert set(R.COVER_BASE) <= set(covered) and R.SCRIPTS[ident] in covered, ident
        assert all((ROOT / c).is_file() for c in covered), ident
        assert not any(c.startswith("vendor/stage2/") for c in covered)
    assert {"extended/opening_population.py", "extended/opening_wait.py", "extended/user_beside.py",
            "identity/user_beside_identity.py", "identity/stage2_identity.py"} <= set(w[R.A0_ID])
    assert {"extended/walker.py", "extended/features.py", "identity/gate_identity.py"} <= set(w["Q-89"])
    assert "extended/user_measures.py" in w["Q-93"] and "identity/user_beside_identity.py" in w["Q-101"]


def test_this_branch_waits_for_its_identities():
    """The infrastructure identities and A0 are not on record as holding at this build's commit: the runs refuse."""
    bad, _ = R.waited_problems(DECISIONS, R.waits(), ROOT)
    assert any(b.startswith(R.A0_ID) for b in bad)


def test_t9_the_judge_reads_the_pick_and_forecast_by_their_pinned_hashes_and_cannot_fit():
    run1, fsha = "a" * 64, "b" * 64
    assert R.pinned_run1_problems("| E-400 | d | F-03's run 1 " + run1 + " forecast " + fsha + " | b |", run1, fsha) == []
    assert R.pinned_run1_problems("| E-400 | d | F-03's run 1 " + run1 + " | b |", run1, fsha)
    assert R.pinned_run1_problems("| E-400 | d | F-02 " + run1 + " " + fsha + " | b |", run1, fsha)
    from datetime import date

    from extended import features as F
    from extended import synthetic_bars as sb

    g = F.grid(sb.generate(sb.Spec(date(2020, 6, 1), date(2021, 2, 26), seed=20261988, holidays=frozenset(),
                                   early_closes=frozenset())))
    st = OS.compute(g)
    frozen = OS.compute(g, frozen=st.forecast.final, test_years=())
    assert frozen.forecast.folds == {} and frozen.forecast.final == st.forecast.final
    assert frozen.forecast.coefficients_sha256 == st.forecast.coefficients_sha256


def test_the_result_frame_refuses_a_section_the_run_does_not_write():
    with pytest.raises(R.RunRefused):
        R.frame([{"section": "judged", "x": 1}], R.RUN1_SECTIONS)
    df = R.frame(R.rows("choice", [{"kind": "pick", "cell": "s2", "killed": False}]), R.RUN1_SECTIONS)
    assert R.choice_pick(df) == {"pick": "s2", "killed": False}
    assert set(R.RUN1_SECTIONS) <= set(R.SECTIONS) and len(R.SECTIONS) == 15


def test_t11_the_seeds_appear_only_in_the_familys_files_and_the_records_that_quote_them():
    pat = "2026198[0-9]"
    hits = set()
    for extra in ([], ["--untracked"]):
        r = subprocess.run(["git", "-C", str(ROOT), "grep", "-I", "-l", "-E", *extra, pat, "--", ".",
                            ":(exclude)vendor"], capture_output=True, text=True)
        hits |= set(r.stdout.split())
    allowed = re.compile(r"^(prereg/F-03_opening_timing\.md|DECISIONS\.md|STATUS\.md|TASK_QUEUE\.md|PROGRESS\.md|"
                         r"docs/(reviews|briefs|audits)/.*|extended/opening_[a-z]+\.py|scripts/fo_opening\.py|"
                         r"identity/family_o_identity\.py|tests/test_family_o_[a-z0-9_]+\.py|tests/fo_[a-z0-9_]+\.py|"
                         r"tests/test_family_r_band_exit\.py)$")
    stray = sorted(h for h in hits if not allowed.match(h.replace("\\", "/")))
    assert stray == [], stray
    fr = (ROOT / "tests" / "test_family_r_band_exit.py").read_text(encoding="utf-8")
    assert set(re.findall(r"\b2026198\d\b", fr)) <= {"20261980"}       # family R's own range's exclusive end


def test_the_section_16_seed_table_is_the_codes():
    from extended import opening_stats as ST

    text = (ROOT / R.DECLARATION).read_text(encoding="utf-8")
    table = {int(s) for s in re.findall(r"^\| (2026198\d) \|", text, flags=re.MULTILINE)}
    assert table == set(ST.SEEDS) == set(range(20261980, 20261990))
    assert (ST.SEED_TWIN, ST.SEED_A10, ST.SEED_B2, ST.SEED_K0, ST.SEED_GATE) == (20261982, 20261984, 20261985,
                                                                                  20261989, 20261983)


def _script(*args: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "fo_opening.py"), *args], capture_output=True,
                          text=True, timeout=timeout, cwd=str(ROOT), env=ENV)


def test_the_runner_refuses_without_the_waited_identities_and_reads_nothing():
    r = _script("--run", "1", "--check-guards")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "REFUSED (F-03)" in r.stdout and "Q-89 is not on record as holding" in r.stdout
    assert r.stdout.strip().endswith("EXIT 2")
    assert "AUTHORISED" not in r.stdout


def test_the_runner_refuses_more_than_two_workers():
    r = _script("--run", "1", "--check-guards", "--workers", "3")
    assert r.returncode == 2 and "at most two workers" in r.stdout


GUARDS = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from extended import opening_run as R
import subprocess
text = (root / "DECISIONS.md").read_text(encoding="utf-8")
head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
lead = "identity-holds:"
tok = "\n".join(f"| E-{900 + i} | 2026-11-17 | {lead} {q} @ {head} -- held | b |" for i, q in enumerate(R.WAITS))
out = {}
try:
    pre = R.pre_run(root, need_clean=False, decisions_text=text + "\n" + tok)
    out["holds"] = True
    out["rows"] = pre.rows
    out["sessions"] = len(pre.judged_sessions)
    out["params"] = sorted(pre.parameters())
except R.RunRefused as exc:
    out["holds"] = False
    out["why"] = str(exc)
try:
    R.pre_run(root, need_clean=False, decisions_text=text + "\n" + tok, level=0.05 / 182)
    out["level_refused"] = False
except R.RunRefused as exc:
    out["level_refused"] = "family_level(12)" in str(exc)
try:
    R.pre_run(root, need_clean=True, decisions_text=text + "\n" + tok)
    out["clean_refused"] = False
except R.RunRefused:
    out["clean_refused"] = True
print(json.dumps(out))
'''


def test_the_guards_hold_with_the_tokens_and_refuse_a_wrong_level_or_an_unclean_tree():
    r = subprocess.run([sys.executable, "-c", GUARDS, str(ROOT)], capture_output=True, text=True, timeout=600,
                       cwd=str(ROOT), env=ENV)
    assert r.returncode == 0, r.stdout + r.stderr
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["holds"], got.get("why")
    assert got["sessions"] == 657 and got["rows"]["Q-89"] == ["E-900"]
    assert {"identity_rows", "identity_covered", "judged_sessions_sha256", "pinned_blobs", "level",
            "cells"} <= set(got["params"])
    assert got["level_refused"] and got["clean_refused"]


def test_run_2s_reads_are_the_four_purposes_through_the_reader():
    src = (ROOT / "scripts" / "fo_opening.py").read_text(encoding="utf-8")
    assert "reader.authorise(reader.JUDGED_START, reader.JUDGED_END, purpose=p, declaration=R.DECLARATION" in src
    assert "repeat=a.repeat" in src
    assert not re.search(r"read_parquet|pq\.read_table", src)
    assert np.isclose(R.LEVEL, 0.05 / 156)
