"""Q-213's identity (the lead's ruling 4): `extended.design_trades`, fed P-16's own registered marks and its
`coin_table` sides, reproduces P-16's registered search-year trades -- `rc_dev_test.trades_hash` of the padded table
equal to `results/h4_registered_constants.csv`'s `p16` `search_trades_sha256`, and its count to `search_trades` --
as H4's I-5 holds the naive coin's source to it (`scripts/h4_rebaseline.py::_check_i5_coin_vs_p16`). Beside, the
table is compared frame for frame with `h4_coin_source.build_p16_i5_trades`' (I-5's own builder).

    python scripts/run_clean.py --name q213-identity --hours 1 --mem-gb 3 --task Q-213 -- python -m pytest -q -o addopts= -p no:cacheprovider -m heavy tests/test_design_trades_identity.py

Heavy (it reads the search years' bars, inside `extended.search_cut`, after `search_cut.authorise`). Prints one JSON
line; exits 0 when the identity holds, 1 when it does not. Writes no file.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LAST = "2023-12-29"


def main() -> int:
    t0 = time.perf_counter()
    from extended import VENDOR_STAGE2, use_vendored_stage2
    from extended import design_trades as DT
    from extended import h4_audit as HA
    from extended import h4_coin_source as CS
    from extended import search_cut as SC
    from extended import triggers as T

    use_vendored_stage2()
    import atlas_a3 as A
    import pandas as pd
    import rc_dev_test as D
    import rc_screen as RS
    import zero_edge_decomposition as zd
    from propedge.research import resolved_coin as rc

    reg = SC.load_constants(ROOT / HA.H4_REG_CONSTANTS_REL, expected_sha256=HA.H4_REG_CONSTANTS_SHA256)
    SC.authorise(purpose="design_trades_identity", declaration=None,
                 what="Q-213 identity: design_trades in P-16's mode against P-16's search-year trades hash",
                 last=LAST, bars=True, root=VENDOR_STAGE2)
    with SC.cut(last=LAST, root=VENDOR_STAGE2) as cut_log:
        I_in = RS.inputs()
        L = I_in["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        days_df = L["days"].copy()
        days_df["date"] = days_df["date"].astype(str)
        days_df = days_df.sort_values("date", kind="stable").reset_index(drop=True)
        days = days_df["date"].tolist()
        walked = days_df[days_df["day_kind"].astype(str).isin(("n", "b"))].reset_index(drop=True)
        wdays = walked["date"].tolist()
        arr_fn = A.bar_arrays(dict(cfg), list(wdays))
        arrays = {str(d): arr_fn(str(d)) for d in wdays}
        rr_grid = A.rrs(cfg)
        keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I_in["plan"])))
        fees = A.fee_by_stop(fcfg, (CS.P16_STOP_TICKS,), tv)
        crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
        coins = rc.coin_table(days, rc.marks())
        problems = cut_log.problems()
    if problems:
        print(json.dumps({"identity": "Q-213", "holds": False, "why": f"search_cut problems: {problems}"}))
        return 1
    kinds = dict(zip(walked["date"], walked["day_kind"].astype(str)))
    hist = DT.history_from_arrays(wdays, arrays)
    spec = DT.registered_spec(reg["p16"]["offered_marks"], coins, CS.P16_STOP_TICKS,
                              report_clear=CS.RELEASE_CLEAR_SLOT, name="p16_registered")
    out = DT.build_trades(spec, hist, lambda i: T.DayContext(i, wdays[i], bls=kinds[wdays[i]] == "b"),
                          day_kinds=kinds, rr_grid=rr_grid, fresh_rr=crr, fee_micro_eq=float(fees[CS.P16_STOP_TICKS]),
                          tick_value=tv, market_entry_ticks=float(cfg["slip_ticks"]), tick=float(cfg["contract"]["tick"]))
    t_pad = zd.pad(out.trades, keys)
    got = D.trades_hash(t_pad)
    want, n_want = str(reg["p16"]["search_trades_sha256"]), int(reg["p16"]["search_trades"])
    ref = CS.build_p16_i5_trades(days_df, lambda d: arrays[d], reg["p16"]["offered_marks"], coins,
                                 fee_micro_eq=float(fees[CS.P16_STOP_TICKS]), tick=float(cfg["contract"]["tick"]),
                                 tick_value=tv, entry_ticks=float(cfg["slip_ticks"]), stop_ticks=CS.P16_STOP_TICKS,
                                 rr_grid=rr_grid, fresh_rr=crr)
    try:
        pd.testing.assert_frame_equal(out.trades.reset_index(drop=True), ref.reset_index(drop=True), check_exact=True)
        same_frame = True
    except AssertionError:
        same_frame = False
    holds = got == want and len(t_pad) == n_want and same_frame
    print(json.dumps({"identity": "Q-213 design_trades vs P-16 search-year trades", "holds": bool(holds),
                      "trades": int(len(t_pad)), "trades_registered": n_want, "hash": got, "hash_registered": want,
                      "same_frame_as_i5_builder": same_frame, "tolerance": 0, "counts": out.counts,
                      "seconds": round(time.perf_counter() - t0, 1)}, sort_keys=True))
    return 0 if holds else 1


if __name__ == "__main__":
    raise SystemExit(main())
