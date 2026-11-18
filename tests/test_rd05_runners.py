"""RD-05's runners (`prereg/RD-05_firm_modes.md` 18): step 0's tables built in memory (refusing on 7 item 8's inexact
boundary cells, the declaration defect reported in the build's hand-back; every section present once that refusal is
lifted in the test), step 2's pipeline on toy sizes and the `build_toys` seed (every run's oracles, the joins, the
renewal, the flip pairs), and steps 3 to 5 refusing. Nothing is written; no bar is read. Fast.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402

import modes_coin as C  # noqa: E402
import modes_rules as SR  # noqa: E402

from extended import modes_rules as R  # noqa: E402
from extended import modes_terms as M  # noqa: E402

TOYS = M.seed("build_toys")


def test_step0_tables_every_section() -> None:
    df = SR.tables()                                                  # R-a: no refusal on the w = 2 cells
    b = df[df["section"] == "boundary_cells"]
    assert len(b) == 12 and int(b["boundary"].astype(bool).sum()) == 6
    want = {"terms", "flip_days", "stated_check", "flip_sizes", "implied_days", "boundary_cells", "sizing", "allowed",
            "size_binding", "oracle_count", "coin_cells"}
    assert set(df["section"]) == want
    assert set(df["described"]) == {"described, not carried"}
    assert len(df[df["section"] == "terms"]) == len(M.MODE_CORNERS)


def test_step2_pipeline_on_toys() -> None:
    cells = [c for c in R.coin_cells() if c["index"] in (0, 12, 13, 20) and c["w_index"] == 1 and c["r_index"] in (1, 4)]
    acc = C.run(300, R.oracle_count()["N"], set(), cells, seeds=(TOYS, 0, 0))
    summ = acc.pop("_summ")[0]
    j = C.joins(summ)
    assert acc["oracle"] and acc["eval"] and acc["funded"] and acc["flip_pairs"] and acc["large_days"]
    assert j["joined"] and j["renewal"] and j["fees"]
    assert any(v.get("shared") for v in summ.values())            # PRO1 lenient's gross shared with its strict
    assert set(j) == {"fees", "joined", "renewal", "flip_pairs"}   # 18's declared sections only
    fp = j["flip_pairs"]
    assert {r["flip"] for r in fp} == {"flip_E", "flip_F"}
    assert {r["measure"] for r in fp} == {"net_per_attempt", "net_per_journey"}
    assert all(np.isfinite(r["se"]) for r in fp)
    assert all(np.isfinite(r["evaluations_per_21"]) for r in j["renewal"])
    meas = {r["measure"] for r in acc["flip_pairs"]}
    assert {"pass", "sessions_to_pass_mean", "sessions_to_pass_p50", "any_payout", "net",
            "sessions_to_first_payout_mean"} <= meas
    gross = [r for r in acc["eval"] if r["coin"] == "gross"]
    assert all("allowance and scaling not applied" in r["labels"] and "no calendar: no news rule" in r["labels"]
               for r in gross)
    ts_n = [r for r in j["joined"] if r["config"] == "TS-N" and r["what"] == "pair"]
    assert ts_n and all(r["activation"] == float(M.rv("activation_fee_naf_50k")) for r in ts_n)
    assert {r["diagonal"] for r in j["joined"] if r["what"] == "pair"} >= {"one policy in both modes (stage one's form)", ""}


@pytest.mark.parametrize("name,step", [("modes_reading", 3), ("modes_beside", 4), ("modes_gate", 5)])
def test_part_f_runners_refuse(name: str, step: int, capsys: pytest.CaptureFixture[str]) -> None:
    import modes_part_f

    assert modes_part_f.main(step) == 3
    assert "NOT BUILT" in capsys.readouterr().out


def test_a14_coin_composition_and_part_f_refusing() -> None:
    from extended import modes_plans as P

    assert [m.index for m in P.corners_of("TS-S")[M.EVAL]] == [0]
    assert [m.index for m in P.corners_of("TS-N")[M.FUNDED]] == [20, 21]
    pairs = {(e.index, f.index) for e, f in P.join_pairs("RE")}
    assert pairs == {(4, 32), (5, 33)}                                # strict with strict, lenient with lenient
    assert {(e.index, f.index) for e, f in P.join_pairs("PRO1")} == {(12, 38), (13, 39)}
    assert {(e.index, f.index) for e, f in P.join_pairs("L6")} == {(1, 22), (1, 23), (1, 24), (1, 25)}
    with pytest.raises(P.NotBuilt):
        P.replay_args()
    with pytest.raises(P.NotBuilt):
        P.gate_args()


def test_purchase_limit_arithmetic_and_lucid_price() -> None:
    from extended import modes_join as J

    p, c, K = 0.3, 0.1, 5
    q = 1 - p - c
    pl = J.under_purchase_limit(p, c, 100.0, 900.0, 0.0, K)
    assert pl["attempts"] == pytest.approx(sum(q ** j for j in range(K)))
    assert pl["p_pass_within"] == pytest.approx(p * pl["attempts"])
    assert pl["net"] == pytest.approx(-100.0 * pl["attempts"] + pl["p_pass_within"] * 900.0)
    assert M.purchase_limit("L6") == 5 and M.purchase_limit("RE") is None
    lu = M.eval_terms("LU40")
    assert lu.one_time is not None and "price unverified: on the grid" not in lu.labels



def test_s11_a_step_unlocks_only_on_its_own_token() -> None:
    from extended import modes_steps as S

    h = S.head_sha()
    good = "| E-999 | 2026-11-18 | " + S.step_cell(0, h[:12], "results/modes_rules.csv, RD-05 step 0") + " | b |"
    assert S.recorded(0, "results/modes_rules.csv", decisions_text=good)
    assert not S.recorded(1, "results/modes_rules.csv", decisions_text=good)          # another step's token
    assert not S.recorded(0, "results/modes_rules.csv",
                          decisions_text="| E-1 | 2026-11-18 | results/modes_rules.csv for RD-05 | b |")
    assert not S.recorded(0, "results/modes_rules.csv",
                          decisions_text="| E-2 | 2026-11-18 | " + S.step_cell(0, "0" * 12, "results/modes_rules.csv")
                          + " | b |")                                                # not an ancestor
    with pytest.raises(ValueError):
        S.step_cell(0, "zz", "x")


def test_n13_step_zero_rows_compared_cell_for_cell() -> None:
    cells = R.coin_cells()
    sig = C.cell_signature_rows(cells)
    as_file = [{**c, "stop": float("nan") if c["stop"] is None else float(c["stop"]), "runs": str(c["runs"]),
                "why": c["why"] or float("nan")} for c in cells]
    assert C.cell_signature_rows(as_file) == sig
    as_file[5] = {**as_file[5], "runs": str(not cells[5]["runs"])}
    assert C.cell_signature_rows(as_file) != sig


def test_n14_measure_refuses_without_the_lock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from extended import lock_guard

    monkeypatch.setattr(lock_guard, "main_root", lambda *a, **k: tmp_path)
    assert "not held" in C.measure_lock_problem()
    (tmp_path / "run.lock").write_text('{"job": "q132-other"}', encoding="utf-8")
    assert "not an rd05- job" in C.measure_lock_problem()
    (tmp_path / "run.lock").write_text('{"job": "rd05-measure"}', encoding="utf-8")
    assert C.measure_lock_problem() is None


def test_v1_main_assembles_every_paired_measure() -> None:
    """V-1: the sections as `main` assembles them (`assemble`) keep part D's paired readings from `run` and add the
    joins' nets -- the flip_pairs section is extended, never replaced."""
    cells = [c for c in R.coin_cells() if c["index"] in (0, 20) and c["w_index"] == 1 and c["r_index"] == 1]
    acc = C.run(300, R.oracle_count()["N"], set(), cells, seeds=(TOYS, 0, 0))
    before = {r["measure"] for r in acc["flip_pairs"]}
    C.assemble(acc)
    meas = {r["measure"] for r in acc["flip_pairs"]}
    ten = {"pass", "sessions_occupied", "sessions_to_pass_mean", "sessions_to_pass_p50", "any_payout", "net",
           "first_payout_within_21", "first_payout_within_63", "sessions_to_first_payout_mean",
           "sessions_to_first_payout_p50"}
    assert before == ten and ten <= meas and {"net_per_attempt", "net_per_journey"} <= meas
    assert "_summ" not in acc and {"fees", "joined", "renewal"} <= set(acc)
    nets = [r for r in acc["flip_pairs"] if r["measure"].startswith("net_per")]
    assert nets and all(str(r["note"]).startswith("approximate SE") for r in nets)      # V-3
