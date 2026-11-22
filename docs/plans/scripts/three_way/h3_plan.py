"""Wave 3.2: H3's run plan, printed from declared constants only -- no bar, no outcome, no result file, no random
number, no seed value (seeds are named by role; their values are the draft's section 15 and
`extended/three_way_seeds.py`). `prereg/H3_three_way.md` holds this script's output between its markers, line
for line (`tests/test_h3_draft.py`).

Every part's sizes are the design note's proposals (`three_way_arith.parts()`, the note's Appendix A), with H3-0's probe
added; the work is lane-trades (histories x arm-runs x seeds x starts x horizon x trades a session); the hours are at
the note's assumed per-lane-trade costs, never a measurement -- H3-0 measures the real cost c (the declared
generator's keyed draws included) and the process base M_0, and the cut rule is applied at the measured c before any
other part starts.

    python docs/plans/scripts/three_way/h3_plan.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _arith():
    spec = importlib.util.spec_from_file_location("three_way_arith_for_h3_plan", HERE / "three_way_arith.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _arith()

#: H3-0, the probe: synthetic toys, a few hundred lanes (the note's 6.1); its sizes are this plan's
PROBE = ("H3-0 probe", 1, 5, 64, 40, 63)
#: each part's seed roles (`extended/three_way_seeds.py` ROLES) and what it reads
ROLES = {
    "H3-0 probe": ("h3_0_probe",),
    "A1 same-design nulls": ("h3a_histories", "h3a_coins"),
    "A2 exact-centred toy null": ("h3a_histories", "h3a_coins"),
    "A3 history null": ("h3a3_history_null",),
    "A4 plants, copy-stagger": ("h3a_histories", "h3a_coins"),
    "D1 same-design nulls": ("h3d_histories", "h3d_coins"),
    "D2 history null": ("h3d_histories", "h3d2_history_null"),
    "D3 power gate plants": ("h3d_histories", "h3d_coins", "h3d3_plants"),
    "D3 full-J check (EB)": ("h3d_histories", "h3d_coins"),
    "H7 held-out, Hoeffding": ("the search declaration's own",),
    "H7 held-out, EB sets": ("the search declaration's own",),
}
READS = {
    "H3-0 probe": "synthetic toys",
    "A1 same-design nulls": "S1, stylised",
    "A2 exact-centred toy null": "S1 toys, the exact program",
    "A3 history null": "S1, stylised",
    "A4 plants, copy-stagger": "S1, stylised",
    "D1 same-design nulls": "S1 fitted to the search years; S2",
    "D2 history null": "S1 fitted to the search years; S2",
    "D3 power gate plants": "H4's search-year outputs; S1 fitted; S2",
    "D3 full-J check (EB)": "S1 fitted to the search years",
    "H7 held-out, Hoeffding": "the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger)",
    "H7 held-out, EB sets": "the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger)",
}


#: the splits (the lead's ruling on the red team's m-5): each part too large for one heavy slot is split into sub-parts
#: each its own slot under run.lock, by histories (R) where it holds several, else by seed indices (M, disjoint ranges);
#: a sub-part keeps its part's id and seed roles. The counts are sized so every sub-part fits the cap at the
#: vectorised generator's race cost with a margin (`h3_cost.py` prints the measured cost against each c_max)
SPLITS = {"D1 same-design nulls": 2, "D2 history null": 4, "D3 power gate plants": 2, "D3 full-J check (EB)": 5,
          "H7 held-out, EB sets": 3}
#: the held-out test's split needs its crash rule, declared before it starts (E-195's part ledger): no statistic is
#: read until every sub-part has completed; a sub-part that crashes is re-run whole from its own declared seeds,
#: never resumed, and its crash is recorded in the ledger
CRASH_RULE = ("no statistic is read until every sub-part completes; a crashed sub-part is re-run whole from its"
              " declared seeds, never resumed; each crash is recorded in the part ledger (E-195)")


def _pieces(n: int, k: int) -> list[int]:
    q, r = divmod(int(n), int(k))
    return [q + (1 if i < r else 0) for i in range(int(k))]


def rows():
    """Every heavy slot: H3-0, the note's parts, and each split part's sub-parts (name, R, arms, M, T, h)."""
    out = [PROBE]
    for name, R, arms, M, T, h in A.parts():
        k = SPLITS.get(name, 1)
        if k == 1:
            out.append((name, R, arms, M, T, h))
        elif R >= k:
            out += [(f"{name} [{i + 1}/{k}]", r, arms, M, T, h) for i, r in enumerate(_pieces(R, k))]
        else:
            out += [(f"{name} [{i + 1}/{k}]", R, arms, m, T, h) for i, m in enumerate(_pieces(M, k))]
    return tuple(out)


def base(name: str) -> str:
    return name.split(" [")[0]


def c_max_us(work: int) -> float:
    """The largest cost a lane-trade at which a slot fits the cap over the workers."""
    return A.PART_CAP_H * 3600.0 * 1e6 * A.WORKERS / work


def report() -> str:
    out = [f"H3's heavy slots: part | seed roles | reads | R arms M T h | lane-trades | hours over {A.WORKERS} workers"
           " at the assumed costs " + ", ".join(f"{c} us" for c in A.COSTS_US) + f" a lane-trade | c_max (the largest"
           f" cost a lane-trade that fits {A.PART_CAP_H:g} h)"]
    for name, R, arms, M, T, h in rows():
        w = A.lane_trades(R, arms, M, T, h)
        hs = "  ".join(f"{A.hours(w, c):.1f}" for c in A.COSTS_US)
        out.append(f"  {name:<30} | {', '.join(ROLES[base(name)])} | {READS[base(name)]} | R={R} arms={arms} M={M}"
                   f" T={T} h={h} | {w:.3e} | {hs} | c_max={c_max_us(w):.2f} us")
    out.append(f"memory: cap {A.MEM_CAP_GB} GB over {A.WORKERS} workers, base {A.BASE_GB} GB assumed (H3-0 measures"
               f" it), lane {A.LANE_BYTES} B: at most {A.max_lanes()} lanes a worker")
    out.append(f"the cut rule: a slot runs only if H3-0's measured cost a lane-trade (the race's and the walks' terms,"
               f" `h3_cost.py`) is at most its c_max; otherwise it is cut, M first, with the power cost stated, or"
               f" split further, before it starts")
    out.append(f"the held-out test's split: {CRASH_RULE}")
    return "\n".join(out)


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
