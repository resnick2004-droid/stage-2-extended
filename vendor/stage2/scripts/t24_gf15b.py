"""T24-GF15b (D-438, D-439): T24-GF15 with every state closing the account once its room cannot carry a full trade of
that state's size -- the flip branch too, after a payout as before it -- and the gap beyond a stop booked as a cost, as
P-08 declared; its registered development test.

    python scripts/t24_gf15b.py --prereg P-xx        # refused without a runnable registration

Everything else is T24-GF15's, frozen (D-434): the m40 map, the coin, five bars late, the report-day cut, the strict rule,
the Combine two-shot 1:1 at $1,600, the growth trade $1,600 at 1:1.5 at or below the start, the $240 flip above it, the
engine, its seed and every arm beside the verdict (`scripts/t24_gf15.py`'s registered run with this spec).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t24_gf15b.py"
DECISION = "D-439"
MODEL = "T24-GF15b"
K = 1


def gap_as_cost(t: pd.DataFrame) -> pd.DataFrame:
    """P-08's declared split (its audit's D1): a stop's gross is the stop itself, -1R; the gap beyond it joins the cost.
    The net R is unchanged."""
    t = t.copy()
    for R in (1.0, 1.5, 2.0, 3.0):
        m = t[f"o_{R:g}"].astype(str) == "s"
        gap = -1.0 - t.loc[m, f"g_{R:g}"].astype(float)
        t.loc[m, f"g_{R:g}"] = -1.0
        t.loc[m, f"c_{R:g}"] = t.loc[m, f"c_{R:g}"].astype(float) + gap
    return t


def trades(rd: Path):
    import t24_gf15 as tg

    t, days, rows = tg.trades(rd)
    return gap_as_cost(t), days, rows


def policy():
    """Every state closes the account once its room cannot carry a full trade of that state's size (D-438 (3))."""
    import t24_exec as te
    import t24_screen as ts

    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    G = te.GROWTH["gf15"]
    combine = ts._closing(Leaf("two-shot 1:1", te.TWO_SHOT, 1.0, max_trades=1), te.TWO_SHOT)
    growth = ts._closing(Leaf(f"growth 1:{G:g}", te.GROWTH_RISK, G, max_trades=1), te.GROWTH_RISK)
    flip = ts._closing(Leaf("flip 1:1", te.FLIP[0], te.FLIP[1], max_trades=1), te.FLIP[0])
    funded = Tiers(on="balance", name="the start", tiers=((-1e12, growth), (0.01, flip)))
    p = RiskPolicy(id="t24_gf15b", root=Phase(combine=combine, funded=funded),
                   description="T24-GF15b (D-439): growth 1:1.5 then flips, every state closed once it cannot carry its trade")
    p.validate()
    return p


def identity_with_p08(rd: Path) -> list[str]:
    """D-440: T24-GF15b's trades are P-08's with the gap moved -- each R's net e, sd, count and pooled bound must equal
    P-08's `edge` rows, and gross less cost must equal the net. The problems, empty when it holds."""
    import confirm_fv3 as cf
    import t24_gf15 as tg

    from propedge.reporting.results import read_result

    t, days, _ = trades(rd)
    p08 = read_result(rd / "t24_gf15_gate.csv")
    p08 = p08[p08["section"] == "edge"].set_index("rr")
    st = cf.edge_stats(t, [1.0, 1.5, 2.0, 3.0], days, 21, None)
    out = []
    for R in (1.0, 1.5, 2.0, 3.0):
        for k in ("e", "sd", "n", "lb"):
            if not np.isclose(float(st[R][k]), float(p08.loc[R, k]), rtol=0, atol=1e-12):
                out.append(f"R {R:g} {k}: {st[R][k]!r} against P-08's {p08.loc[R, k]!r}")
        m = np.isfinite(t[f"r_{R:g}"].astype(float))
        if not np.allclose(t.loc[m, f"g_{R:g}"] - t.loc[m, f"c_{R:g}"], t.loc[m, f"r_{R:g}"], atol=1e-9):
            out.append(f"R {R:g}: gross less cost is not the net")
    return out


SPEC = {"model": MODEL, "decision": DECISION, "script": SCRIPT, "result": "t24_gf15b_gate", "k": K, "label": MODEL,
        "policy": policy, "trades": trades}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import t24_gf15 as tg

    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED (D-439): {exc}")
        return 2
    problems = identity_with_p08(rd)
    if problems:
        print("REFUSED (D-440): T24-GF15b's trades are not P-08's -- " + "; ".join(problems))
        return 3
    return tg._registered_run(a.prereg, rd, results_dir, spec=SPEC)


if __name__ == "__main__":
    raise SystemExit(main())
