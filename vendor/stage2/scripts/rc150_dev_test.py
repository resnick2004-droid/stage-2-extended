"""RC150 (rc_s150_all_nr, D-544): the registered development test of the 37.5-point news-safe coin -- P-15's test
(`scripts/rc_dev_test.py`, its runner reused through `rc_dev_test.Spec`) with D-538's 37.5-point all-day cell.

    python scripts/rc150_dev_test.py --check --paths 4 --starts 6   # every identity and arm at 4 paths, the slices and
                                                                     #   journey on the first 6 starts; nothing written,
                                                                     #   no reading printed
    python scripts/rc150_dev_test.py --planning-sd                  # the planning sd by R; nothing written
    python scripts/rc150_dev_test.py --prereg P-xx --workers 4      # the registered test; refused without a registration

**The candidate** (D-538, D-542, D-544): `scripts/rc_width_screen.py`'s `rc_s150_all` cell exactly -- the walk at every
five-minute mark from 17:00 CT at a 150-tick (37.5-point) stop, the cutoff (unresolved at most 5 % at every offered R,
kind columns only), the coin seeded 20261102 per date and mark, every quarter R to 3R, FV3's costs at that stop, a report
day's marks before 07:30 CT dropped and then every report-day entry before 07:35 CT (D-533's news-safe cut) -- sized by
the engine as the table sizes it (no funded cap), through P-14's engine call (the no-closure table, 20 Combine purchases
and resets in any 21 trading days, the strict one-at-a-time rule at 5 minutes, five Topstep seats, the placement off,
0 % denial in the gate), each R's 0.05 bound by the era rule and at 0.05/N.

**The seed:** every resampled arm draws at a FRESH campaign seed, `SEED` = 20261206, used nowhere else in the repository
(checked by a test) and read at nothing before registration except the build's `--check` smoke at 4 paths, which prints
and writes nothing: D-538's screen ran this cell at the screen's seed, and D-542's diagnostic at the same seed, so -- as
D-512 ruled for P-14 and D-529 (2) for P-15 -- the registered gate must not reuse it. The screen's seed survives only in
the identities (a) and (c).

**The planning sd** (D-529 (4)'s form): `assumed_sd` is the 3R value printed by `--planning-sd` (each offered R's net
outcome's sample sd over the cell's offered candidates) and recorded in the registered manifest (`planning_sd`); a
planning input, not a result; it decides nothing.

**Identities first, each refusing:** (a) P-14's trades through this engine call reproduce
`results/a3_brk30_cb20_gate_paths.csv`; (b) the cell's trades are the screen's -- count, busiest day, capacity, long
share, candidates a day and every R's unresolved share equal `results/rc_width_screen.csv`'s `rc_s150_all` row (the file's
sha256 pinned) and their content hash equals `TRADES_SHA256` (pinned by D-543's diagnostic and recomputed here); (c) at
500 paths the cell at the screen's seed reproduces the screen's growth at the bound and the point and its required
bankroll; (d) FV3-C's slices equal `results/customer_slices.csv`'s `fv3c` rows.

**The arms are P-15's** (the gate at 0 / 10 / 25 / 50 % denial, point and bound; the bound at 0.05/N; the placement on;
the zero-edge twin; the fixed-legs twin; the T24-GF15b reading; the check period; the Focused Trader Program's 16 models;
the campaign without the strict rule; the three other customer windows beside; D-509's four slice lines against FV3-C;
D-518's journey on the verdict arm) **plus two beside readings, never deciding:** `funded_cap_beside` and
`funded_cap_twin` -- the same cell with the funded leg's realised risk held to the 25-point cell's
(`resolved_coin.funded_cap_rule`, D-542's cap), so the confound D-539 (2) named (a wider stop raises the funded leg's
realised risk) is read in the registered file; and the share of paths with a day on which two or more accounts hit the
loss limit (`share_paths_with_same_day_multi_breach`, every gate row), promised by P-13's and P-14's files and missing from
their rows (the audits' repeated finding).

**The verdict** is P-15's rule (D-509 (3), D-419): PASS at 0.05/N with the resolution and fidelity lines and all four
slice lines; the gate's PASS with a line failed is CONTINUE (consistency); CONTINUE at 0.05; FAIL below.

Writes `results/rc_s150_all_gate.csv`, `_paths.csv` and `_slices.csv` with manifests (not exploratory, the P-id).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import rc_dev_test as D  # noqa: E402
import rc_screen as S  # noqa: E402

SCRIPT = "scripts/rc150_dev_test.py"
DECISION = "D-544"
MODEL = "RC150"
CELL = "rc_s150_all"
STOP = 150
WINDOWS_BESIDE = ("rc_s150_asia", "rc_s150_london", "rc_s150_us")
#: the registered arms' campaign seed: fresh, used nowhere else (a test checks), fixed before anything is read at it
SEED = 20261206
SCREEN_FILE = "rc_width_screen.csv"
SCREEN_SHA256 = "7b4b65d1130c524874de874ff242dbe3cb74fe3aa456ccd3d9fef2e9758c855d"
#: the cell's trades (D-538's build with D-533's cut), as `rc_width_diag.CELL_TRADES_SHA256` pinned them (D-543)
TRADES_SHA256 = "17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f"


def build_cells() -> tuple[dict, dict]:
    """(P-14's inputs and the no-closure plan, `rc_width_screen.build` at the 150-tick stop: the walk, the cutoff and the
    four windows' cells, each with D-533's news-safe cut in `trades`)."""
    import rc_width_screen as W

    I = S.inputs()
    return I, W.build(I, (STOP,))


SPEC = D.Spec(script=SCRIPT, decision=DECISION, model=MODEL, cell=CELL, windows_beside=WINDOWS_BESIDE, seed=SEED,
              screen_seed=S.SEED, screen_file=SCREEN_FILE, screen_sha256=SCREEN_SHA256, trades_sha256=TRADES_SHA256,
              stop_ticks=STOP, build=build_cells, funded_cap=True, multi_breach=True, news_safe=True,
              describe="the {cell} coin -- offered every five minutes all session at a 37.5-point stop, no report-day "
                       "entry before 07:35 CT, taken when every account is flat")


STOPS_RESULT = "rc150_stop_distribution"


def write_stop_distribution(results_dir: Path | None = None) -> int:
    """The card's stops (`--stop-distribution`; a reading of the trades, no campaign): the selected cell's offered
    trades at the fresh Combine's and fresh XFA's R in A3-BRK30's form, on D-526's deterministic subsample (every 10th
    trading day in date order, `resolved_coin.subsample_days`), written EXPLORATORY with its manifest. Run from a clean
    checkout (D-474) before the card is validated for registration."""
    import rc_reentry_screen as RS

    from propedge.reporting.results import write_result
    from propedge.research import resolved_coin as rc

    I, b = build_cells()
    c = b["cells"][CELL]
    bad = D.trade_problems(Path(results_dir) if results_dir is not None else _results_dir(), b, I["L"]["fcfg"],
                           spec=SPEC)
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not {SCREEN_FILE}'s {CELL} -- " + "; ".join(bad[:6]))
        return 3
    sd = RS.stop_distribution({CELL: c}, I["L"]["fcfg"])
    csv, _ = write_result(sd, STOPS_RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                          results_dir=results_dir,
                          parameters={"decision": DECISION, "cell": CELL, "stop_ticks": STOP,
                                      "trades_sha256": D.trades_hash(c["trades"]), "subsample": RS.SUBSAMPLE,
                                      "every_days": rc.STOPS_EVERY_DAYS,
                                      "exit_mapping": "target at the state's R; flatten at 15:10; stop or breakeven "
                                                      "-> stop"},
                          notes={"status": "RC150's card stop distribution (a reading of the trades, no campaign); "
                                           "A3-BRK30's form, D-526's subsample"},
                          description=f"EXPLORATORY: {CELL}'s offered trades (the 37.5-point news-safe coin, all-day) at "
                                      "the fresh Combine's and fresh XFA's R, on every 10th trading day -- the card's "
                                      "stops for D-201's band, D-190's zero micros and D-212's checks.")
    print(f"written: {Path(csv).name} ({len(sd)} rows)")
    return 0


def _results_dir() -> Path:
    from propedge import RESULTS_DIR

    return RESULTS_DIR


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--stop-distribution" in args:
        return write_stop_distribution(results_dir)
    return D.main(args, results_dir=results_dir, spec=SPEC)


if __name__ == "__main__":
    raise SystemExit(main())
