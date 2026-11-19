"""Wave 3.2: H3's run plan, printed from declared constants only -- no bar, no outcome, no result file, no random
number, no seed value (seeds are named by role; their values are the draft's section 15 and
`extended/three_way_seeds.py`). `prereg/DRAFT_H3_three_way.md` holds this script's output between its markers, line
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
    "H7 held-out, Hoeffding": "the held-out years, once (Wave 6; not H3)",
    "H7 held-out, EB sets": "the held-out years, once (Wave 6; not H3)",
}


def rows():
    return (PROBE,) + tuple(A.parts())


def report() -> str:
    out = [f"H3's parts: part | seed roles | reads | R arms M T h | lane-trades | hours over {A.WORKERS} workers at the"
           " assumed costs " + ", ".join(f"{c} us" for c in A.COSTS_US) + " a lane-trade"]
    for name, R, arms, M, T, h in rows():
        w = A.lane_trades(R, arms, M, T, h)
        hs = "  ".join(f"{A.hours(w, c):.1f}" for c in A.COSTS_US)
        cut = [c for c in A.COSTS_US if A.hours(w, c) > A.PART_CAP_H]
        flag = f"  over {A.PART_CAP_H:g} h from {min(cut)} us: cut M first or split" if cut else ""
        out.append(f"  {name:<26} | {', '.join(ROLES[name])} | {READS[name]} | R={R} arms={arms} M={M} T={T} h={h}"
                   f" | {w:.3e} | {hs}{flag}")
    out.append(f"memory: cap {A.MEM_CAP_GB} GB over {A.WORKERS} workers, base {A.BASE_GB} GB assumed (H3-0 measures"
               f" it), lane {A.LANE_BYTES} B: at most {A.max_lanes()} lanes a worker")
    out.append(f"the cut rule: a part whose estimate at H3-0's measured cost exceeds {A.PART_CAP_H:g} hours is cut, M"
               " first, with the power cost stated, or split into sub-parts each its own heavy slot under run.lock")
    return "\n".join(out)


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
