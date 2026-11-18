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

import modes_coin as C  # noqa: E402
import modes_rules as SR  # noqa: E402

from extended import modes_rules as R  # noqa: E402
from extended import modes_terms as M  # noqa: E402

TOYS = M.seed("build_toys")


def test_step0_refuses_on_the_inexact_boundary_cells() -> None:
    with pytest.raises(SR.BoundaryDefect, match="overshoots T"):
        SR.tables()


def test_step0_tables_every_section(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(R, "boundary_exact", lambda t, w, r: R.boundary_declared(t, w, r))
    df = SR.tables()
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
    assert set(j) == {"fees", "joined", "renewal"}                 # 18's declared sections only
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
