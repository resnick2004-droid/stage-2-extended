"""Q-132 (E-189, the Q-45 audit's D1, C1, C2, C6, C7): the second breakeven-fidelity reading's own code
(`extended/breakeven_readings.py`, `scripts/breakeven_fidelity_2.py`, P-15's build and gate in `extended/breakeven.py`).
Light: synthetic records and series only; no bar, atlas or engine run (the whole reading is the lead's clean run).

What is asserted:

* **D1, the per-start file** (child process, `tests/breakeven2_checks.py frame`): the frame's columns are
  `START_FILE_COLS`; its CSV text read back gives every start's U1 record bit for bit, its differing exact runs (`alt`)
  included, money unrounded; every scorecard, extra and path row re-made from that text alone equals
  `extended.user_readings.summary`'s (`rederive_problems` empty); three negative controls are refused -- one net's sign
  flipped, the exact runs dropped, a start dropped; P's per-start unit (`p_months_ahead` / 3) averages to the card's P
  on both blocks, and the file's own column does too.
* **C2, the paired rows** (child, `paired`): the mean equals the two cards' P difference on both blocks; identical rule
  sets print "identical on these trades"; the all block prints RD-02 9.2's interval and MDD about the kept mean, the
  judged block (too few windows) prints "too few separated windows for an interval"; with the honesty settings given the
  label and the rare-shape line appear; the honesty series are reproducible from their seed; a start on one side only
  is refused.
* **mdd_P** (child, `mdd`): blank with its reason for P-14 (R* itself) and on the all block; finite and positive for
  another design on the judged block, reproducible from its seed. In process: Q-16's real-null sign flips equal
  `scripts/q16_calibrate.py`'s `_flip_signs` draw for draw; `mdd_p` is scale-equivariant (the shipped statistic is),
  None on an identically zero series, and reproducible.
* **The runner's plumbing** (child, `runner`): `main(--check --paths 4)` with every engine step a fake (the read's
  authorisation, U1's reference, the builders and identities, the gates, the replay on synthetic starts) exits 0; both
  files and manifests verify; the start file holds every design, rule set and arm, its sha256 in the summary's
  manifest; sections paired, honesty and assumptions are written; mdd_P filled (or infinite, with its reason) for P-15
  and P-16 on the judged block and blank for P-14 and the all block; the assumptions in the manifest's parameters and
  notes; the licence guard's scan recorded and logged; nine variants; the log's first line the provenance line.
* **C1, P-15's build** (child, `p15_substitution`): `extended.breakeven.p15_cells` with the vendored inputs and builder
  replaced by probes -- the inputs load under Stage 2's walk, the cells are built under the given one, Stage 2's walk
  is restored after (also after an error), nothing is substituted without a walk; the vendored `build_cells` is the two
  lines reproduced. (Its identities on the real bars -- the screen row, the pinned hash, U1's start rows, the gate row
  at 500 paths -- are the runner's, in the lead's run.)
* **C6** (child, `variants`): nine variants recorded through the vendored `VariantCounter`, distinct ids, exploratory;
  the log's head names the commit and the tree's state (`provenance_line`).
* **C7**: `assumptions` reads the payout lag, timing, path, budget, strict rule and state table from the jobs' engine
  arguments and states the fill profile, the spacing model and the move's latency; the note says each.
* **The seeds**: the block 20262260-20262269 appears in this repository's code and tests only in the three files that
  declare and test it, in no declaration under `prereg/`, and nowhere in the vendored snapshot; the roles are distinct.
* **The runner**: it never writes Q-45's file name; a partial run without `--check` and a design it does not read are
  refused before anything (exit 2), the log's first line the provenance line.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import breakeven_readings as BR  # noqa: E402

CHECKS = ROOT / "tests" / "breakeven2_checks.py"
SCRIPT = ROOT / "scripts" / "breakeven_fidelity_2.py"
BLOCK = re.compile(r"(?<!\d)2026226\d(?!\d)")
#: the code and tests that may hold a seed of the block
DECLARING = {"extended/breakeven_readings.py", "scripts/breakeven_fidelity_2.py", "tests/test_breakeven_fidelity_2.py"}


def child(check: str, timeout: int = 900) -> dict:
    r = subprocess.run([sys.executable, str(CHECKS), check], capture_output=True, text=True, timeout=timeout,
                       env={**__import__("os").environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                            "MKL_NUM_THREADS": "1"})
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------------------------------------------ child checks


def test_the_per_start_file_carries_every_figure():
    out = child("frame")
    assert out["problems"] == [], out
    s = out["seen"]
    assert s["alt_starts"] > 0 and s["eligible_p"] > 0 and s["p_judged_n"] > 0
    assert s["flipped"] > 0 and s["no_alt"] > 0 and s["dropped"] > 0


def test_the_paired_rows():
    out = child("paired")
    assert out["problems"] == [], out
    assert out["seen"]["n_w_all"] >= BR.MIN_WINDOWS and out["seen"]["one_side_refused"] > 0


def test_mdd_p_is_filled_against_p14_on_the_judged_block():
    out = child("mdd")
    assert out["problems"] == [], out
    assert out["seen"]["n"] > 0 and len(out["seen"]["computed"]) == 1


def test_the_variants_are_recorded():
    out = child("variants")
    assert out["problems"] == [] and out["seen"]["lines"] == 9, out


def test_the_runner_end_to_end_on_fakes():
    out = child("runner")
    assert out["problems"] == [], out
    assert out["seen"]["rc"] == 0 and out["seen"]["start_rows"] > 0 and out["seen"]["paired_rows"] > 0


def test_p15s_walk_is_substituted_for_its_one_call():
    out = child("p15_substitution")
    assert out["problems"] == [], out


# ------------------------------------------------------------------------------------------------ in process


def _q16():
    spec = importlib.util.spec_from_file_location("q16_calibrate_for_q132", ROOT / "scripts" / "q16_calibrate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_flips_are_q16s():
    q16 = _q16()
    for n, L, reps in ((300, 63, 50), (595, 63, 7), (130, 21, 3)):
        a = BR.flip_signs(np.random.default_rng([BR.TEST_SEED, n]), n, L, reps)
        b = q16._flip_signs(np.random.default_rng([BR.TEST_SEED, n]), n, L, reps)
        assert a.shape == (n, reps) and np.array_equal(a, b)


def test_mdd_p_scale_zero_and_seed():
    rng = np.random.default_rng([BR.TEST_SEED, 99])
    d = (rng.random(300) < 0.5).astype(float) / 3.0 - (rng.random(300) < 0.5).astype(float) / 3.0
    v = BR.mdd_p(d, np.random.default_rng([BR.TEST_SEED, 1]), reps=300, batch=150)
    w = BR.mdd_p(3.0 * d, np.random.default_rng([BR.TEST_SEED, 1]), reps=300, batch=150)
    again = BR.mdd_p(d, np.random.default_rng([BR.TEST_SEED, 1]), reps=300, batch=150)
    assert v is not None and v > 0 and np.isfinite(v)
    assert w == pytest.approx(3.0 * v, rel=1e-9) and again == v
    assert BR.mdd_p(np.zeros(300), np.random.default_rng(0), reps=10) is None
    assert BR.mdd_p(d[:BR.MDD_MIN_STARTS - 1], np.random.default_rng(0), reps=10) is None    # pcons not formable
    assert BR.mdd_level() == pytest.approx(0.05 / 132)


def test_the_assumptions_are_read_from_the_engine_arguments():
    proto = SimpleNamespace(payout_path="standard", payout_frac=1.0, keep_balance=None)
    jobs = {(d, a): {"args": {"path": {"payout_lag_days": 3, "payout_timing": "after_5pm",
                                       "purchase_budget": (20, 21), "risk_policy": SimpleNamespace(id="tbl_x")},
                              "draws": {"protocol": proto, "one_at_a_time": 5.0}}}
            for d in ("p14", "p15") for a in ("verdict", "point")}
    rules = {"stage2": SimpleNamespace(breakeven_tie="target", breakeven_delay=0),
             "delay5": SimpleNamespace(breakeven_tie="target", breakeven_delay=5)}
    a = BR.assumptions(jobs, rules, "assumed")
    assert set(a) == {"fills", "payout", "state_table", "breakeven_move", "response"}
    assert a["fills"]["profile"] == "assumed"
    p = a["payout"]["by_design_arm"]["p15|point"]
    assert p["payout_lag_days"] == 3 and p["payout_method"] == "aeropay" and p["purchase_budget"] == [20, 21]
    assert p["one_at_a_time_minutes"] == 5.0 and p["payout_path"] == "standard"
    assert a["state_table"]["by_design_arm"]["p14|verdict"] == "tbl_x"
    assert a["breakeven_move"]["rule_sets"]["delay5"]["breakeven_delay"] == 5
    assert "D-266" in a["breakeven_move"]["latency"] and "D-18" in a["payout"]["spacing"]
    note = BR.assumptions_note(a)
    assert a["payout"]["paths"] == {"standard": "5 winning days >= $150 before each request"}
    for s in ("'assumed'", "3 session", "tbl_x", "D-266", "D-18", "0 % payout denial", "5 winning days"):
        assert s in note, (s, note)
    rows = BR.assumption_rows(a)
    assert [r["measure"] for r in rows] == list(a) and all(np.isnan(r["value"]) for r in rows)


def test_the_logs_head():
    st = BR.git_state(ROOT)
    assert re.fullmatch(r"[0-9a-f]{40}", st["commit"] or "") and isinstance(st["clean"], bool)
    line = BR.provenance_line(st, "scripts/breakeven_fidelity_2.py", ["--check"])
    assert line.startswith(f"provenance: commit {st['commit']} (clean {st['clean']}")


def _tracked_with_block() -> set[str]:
    r = subprocess.run(["git", "grep", "-IlE", "2026226[0-9]", "--", "."], cwd=ROOT, capture_output=True, text=True)
    files = {x.strip().replace("\\", "/") for x in r.stdout.splitlines() if x.strip()}
    return {f for f in files if BLOCK.search((ROOT / f).read_text(encoding="utf-8", errors="replace"))}


def test_the_seed_block_is_this_readings_alone():
    assert BR.SEED_BLOCK == tuple(range(20262260, 20262270))
    assert len({BR.HONESTY_SEED, BR.MDD_SEED, BR.TEST_SEED}) == 3 and set(BR.SEED_ROLES) == set(BR.SEED_BLOCK)
    found = _tracked_with_block()
    code = {f for f in found if f.endswith(".py") or f.startswith(("prereg/", "identity/", "config/"))}
    assert code <= DECLARING, code - DECLARING
    assert not any(f.startswith(("prereg/", "vendor/")) for f in found), found
    vend = [p for p in (ROOT / "vendor" / "stage2").rglob("*") if p.is_file() and p.suffix in (".py", ".md", ".yaml",
                                                                                                  ".json", ".txt")
            and "data" not in p.relative_to(ROOT / "vendor" / "stage2").parts[:1]
            and BLOCK.search(p.read_text(encoding="utf-8", errors="replace"))]
    assert vend == []


def test_the_runner_names_new_files_and_refuses_partial_runs():
    src = SCRIPT.read_text(encoding="utf-8")
    assert re.search(r'^RESULT = "breakeven_fidelity_2"$', src, re.M)
    assert re.search(r'^STARTS_RESULT = "breakeven_fidelity_2_starts"$', src, re.M)
    assert '"breakeven_fidelity"' not in src
    env = {**__import__("os").environ, "OPENBLAS_NUM_THREADS": "1"}
    env.pop("S2X_CLEAN_RUN", None)
    for argv in (["--starts", "4"], ["--check", "--designs", "p13"], ["--check", "--designs", "p16,p16"]):
        r = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, timeout=600,
                           cwd=ROOT, env=env)
        assert r.returncode == 2, (argv, r.stdout[-2000:], r.stderr[-2000:])
        lines = r.stdout.splitlines()
        assert lines[0].startswith("provenance: commit ") and "REFUSED (Q-132)" in r.stdout, r.stdout
