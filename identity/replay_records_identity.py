"""Q-94's identity (`extended/replay_records.py`: place recording on Q-17's U1 replay, through
`extended/user_beside.py`'s `recorder` keyword), refusing. Recording must change nothing, and the records must hold.

    python identity/replay_records_identity.py --u1-starts 4 --row E-NNN                # slow (the lock)
    python identity/replay_records_identity.py --u1-starts all --row E-NNN              # heavy (the lock; the lead's)
    python identity/replay_records_identity.py --u1-starts all --row E-NNN --and-off    # heavier: also bit for bit

**`--u1-starts N|all`.** With every response off (`off`: the vendored 0 %, placement-off call) and a
`ReplayRecorder` given, the adapter's replay reproduces `vendor/stage2/results/user_journey.csv`'s section `start` for
each configuration (P-16 and P-14 by default) and arm (verdict, point), **every column of the file**, by the comparison
E-010's identity uses (`identity/user_beside_identity.py`'s `u1_compare_outs`: `identity/stage2_identity.py`'s
`u1_compare` -- money and the ratio to 1e-6, counts and days exactly, dates and text exactly), on N starts spread as
`user_journey.py --check --starts N` spreads them, or on every start (then the file's starts must all be reproduced);
beside it the study's own refusing checks on the same runs (D-620's declaration, the builders' identity rows, every
run's payouts and fees against the engine's totals). Then **the records hold**: one record a start, in start order; no
per-start problem (Q-70's per-path checks -- the ledger numbers the trades, the places are the vendored
`records_counts`', the balances chain, every routed trade is in the start's blocks, R is the table's -- and Q-94's: the
openings equal the replay ledger's by Q-35's reading, every routed trade on its own session, the wait its opening's
relative session); some funded account opened. Printed: the trades by place summed over starts, the openings, the
funded accounts that never opened.

`--and-off` also runs the same starts with recording off and holds every output of the recorded run equal to it **bit
for bit** (Q-76's canonical form: every float by its hex) -- about twice the time. `--funded-cls pass_through` gives the
gate's `PassThroughFundedAccount` as the declared class (Q-76) on every run (the outputs then name it; the comparison
with the file is the same). `--workers` as Q-17's identity (default 1).

**What is kept.** Every check runs where the start ran, on the full record; the identity keeps no trade column
(`columns=()`): one recorder a configuration and arm holds its accounts, counts and problems (a few kilobytes a start).

**The read (Q-48).** Before anything runs, the engine's read is authorised through
`extended.reader.authorise_engine_read` (purpose `identity`, the window 2020-01-02 to 2026-07-16, the files E-024's U1
identity names: A1's events and days and A3's cached walk for every configuration, the bars for P-16's walk) under this
identity's decision row: `--row E-NNN`, else `READ_ROW`, else the first row of `DECISIONS.md` that names Q-94 and an
identity; none -- refused (`EXIT 3`). Ledgered only inside a clean run (E-026).

**Cost** (estimates; the lead measures). The anchor is E-010's run of the same replays (P-14 and P-16, 1,691 starts
each, both arms, the exact-length runs on every start: 33 minutes, peak 1.36 GB). On the synthetic P-14-table replay
(126 starts, the response off) recording added about 27 % to a long replay's time and 12 to 16 % to a whole start's (the
exact-length runs stay unrecorded; at U1's 252-session horizon the long run is under half a start's sessions). So:
`--u1-starts 4` a few minutes (the builders dominate); `--u1-starts all` about 40 to 50 minutes, peak about 1.4 to
1.5 GB (one start's ledger and day rows at a time, a few kilobytes kept a start); `--and-off` about 75 to 90 minutes.

Exit 0 when every part holds; 3 when one fails or is refused; 2 for bad arguments (before anything is read). Nothing is
written (inside a clean run, the read's ledger line). Peak memory printed last.
"""
from __future__ import annotations

import argparse
import gc
import re
import sys
import time
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import stage2_identity as SI  # noqa: E402  (identity/stage2_identity.py: the file's name, engine files, peak memory)
import user_beside_identity as UBI  # noqa: E402  (identity/user_beside_identity.py: U1's reference, builders, compare)

from extended import reader  # noqa: E402

VENDOR = ROOT / "vendor" / "stage2"
#: this identity's decision row (Q-48's read authorisation) -- the row that merges Q-94, set by the lead; until then
#: `--row`, or the first decision row naming Q-94 and an identity
READ_ROW: str | None = None
ITEM = "Q-94"
U1_CONFIGS = ("p16", "p14")
FUNDED_CLS = ("none", "pass_through")


def decision_row(given: str | None) -> str | None:
    """This identity's decision row: given, else READ_ROW, else the first row naming Q-94 and an identity."""
    if given:
        return given
    if READ_ROW:
        return READ_ROW
    p = ROOT / "DECISIONS.md"
    text = p.read_text(encoding="utf-8") if p.is_file() else ""
    for line in text.splitlines():
        m = re.match(r"^\|\s*(E-\d{3,})\s*\|", line)
        if m and re.search(rf"(?<![\w-]){re.escape(ITEM)}(?!\d)", line) and "identit" in line.lower():
            return m.group(1)
    return None


def record_problems(rec: Any, key: tuple[str, str, str], outs: list[dict[str, Any]], what: str) -> list[str]:
    """The records of one run: one a start of the outputs, in their order; no per-start problem; some opening."""
    probs = [f"{what}: {p}" for p in rec.problems()[:8]]
    if key not in rec.recorded():
        return probs + [f"{what}: nothing was recorded"]
    per = rec.per_start(*key)
    if [r["start_day"] for r in per] != [x["rec"]["start_day"] for x in outs]:
        probs.append(f"{what}: the records are not one a start of the outputs, in their order")
    acc = rec.accounts(*key)
    if not len(acc) or not bool(acc["opened"].any()):
        probs.append(f"{what}: no funded account opened on any start -- the openings' checks would be vacuous")
    return probs


def summary(rec: Any, key: tuple[str, str, str]) -> str:
    c = rec.counts(*key)
    acc = rec.accounts(*key)
    opened = int(acc["opened"].sum()) if len(acc) else 0
    places = {p: int(c.get(p, 0)) for p in ("b_evaluation", "c_funded_opening", "d_funded_later", "e_paid")}
    return f"trades by place {places}, {opened} openings of {len(acc)} funded accounts"


def run_config(name: str, ref: dict[str, Any], starts: int | None, workers: int, funded_cls: str, and_off: bool
               ) -> dict[str, Any]:
    import user_journey as UJ

    from extended import replay_records as RR
    from extended import user_beside as B

    from propedge import RESULTS_DIR

    t0 = time.time()
    print(f"Q-94 identity {name}: the inputs (user_journey.BUILDERS)...", flush=True)
    jobs, c, probs = UBI.build(RESULTS_DIR, name)
    cls = UBI.funded_cls_of(funded_cls)
    kw = {} if cls is None else {"funded_account_cls": cls}
    ran = of = 0
    notes: list[str] = []
    record_probs: list[str] = []
    off = B.BY_NAME["off"]
    for arm in UJ.ARMS:
        job = jobs[arm]
        of = len(job["blocks"])
        chosen = UJ.start_choice(of, starts)
        rec = RR.ReplayRecorder(columns=())
        outs = B.run_starts(name, arm, off, job, chosen, workers, recorder=rec, **kw)
        ran = len(outs)
        probs += UBI.u1_compare_outs(name, c, arm, outs, ref, of, starts)
        if cls is not None:
            want = B.class_name(cls)
            if not all(x.get(UBI.CLASS_KEY) == want and list(x)[-1] == UBI.CLASS_KEY for x in outs):
                probs.append(f"{name} {arm}: a start's output does not name the class {want} in its last key")
        key = (name, arm, "off")
        record_probs += record_problems(rec, key, outs, f"{name} {arm}")
        notes.append(f"{arm}: {summary(rec, key)}")
        if and_off:
            plain = B.run_starts(name, arm, off, job, chosen, workers, **kw)
            if len(plain) != len(outs):
                probs.append(f"{name} {arm}: {len(outs)} starts recorded against {len(plain)} without")
            for i, (x, y) in enumerate(zip(plain, outs)):
                d = UBI.first_difference(x, y, f"start index {i}")
                if d:
                    probs.append(f"{name} {arm}: with recording on the outputs are not recording off's -- {d}")
                    break
            del plain
        del outs, rec
        gc.collect()
    del jobs
    gc.collect()
    return {"problems": probs, "records": record_probs, "starts": ran, "of": of, "seconds": time.time() - t0,
            "columns": len(ref["columns"]), "notes": notes}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--u1-starts", default=None, help="N starts a configuration and arm (N >= 1), or 'all'")
    ap.add_argument("--configs", default=",".join(U1_CONFIGS))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--funded-cls", default="none", choices=FUNDED_CLS,
                    help="the declared funded-account class on every run: none (the default) or the gate's "
                    "pass-through class")
    ap.add_argument("--and-off", action="store_true", help="also run recording off and hold the outputs equal bit for "
                    "bit (about twice the time)")
    ap.add_argument("--row", default=None, help="this identity's decision row (E-NNN) for the read's authorisation")
    a = ap.parse_args(argv)
    if a.u1_starts is None:
        ap.error("give --u1-starts N or --u1-starts all")
    if a.u1_starts != "all" and not (a.u1_starts.isdigit() and int(a.u1_starts) >= 1):
        ap.error("--u1-starts takes a whole number of at least 1, or 'all'")
    if a.workers < 1:
        ap.error("--workers takes a whole number of at least 1")
    configs = tuple(x for x in a.configs.split(",") if x)
    unknown = [x for x in configs if x not in UBI.U1_CONFIGS + ("p15",)]
    if not configs or unknown:
        ap.error(f"--configs takes some of p16, p14 (and p15), got {a.configs!r}")
    row = decision_row(a.row)
    try:                                            # Q-48: the engine's read authorised (ledgered in a clean run only)
        if row is None:
            raise reader.ReadRefused(f"REFUSED: {ITEM}'s identity names no decision row: give --row E-NNN (the row "
                                     "that merges Q-94) or set READ_ROW")
        root = VENDOR / "data"
        if not ((root / "bars").is_dir() and (root / "atlas").is_dir()):
            raise FileNotFoundError("REFUSED: no bars or atlas (scripts/vendor_stage2.py --data)")
        files = SI.engine_files(VENDOR, bars=any(c in SI.U1_WALKED for c in configs))
        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                     declaration=row, files=files,
                                     what=f"{row}'s identity (identity/replay_records_identity.py): U1's start rows "
                                          f"for {', '.join(configs)} ({a.u1_starts} starts) through Q-17's adapter "
                                          "with the replay's place recording on (Q-94), every response off"
                                          + ("" if a.funded_cls == "none" else ", the pass-through class given"))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc), flush=True)
        print("EXIT 3", flush=True)
        return 3
    from propedge import RESULTS_DIR

    starts = None if a.u1_starts == "all" else int(a.u1_starts)
    ref = UBI.u1_reference(RESULTS_DIR, configs)
    bad = False
    extra = ("" if a.funded_cls == "none" else ", the pass-through class (Q-76) given") + \
        (", every output recording off's bit for bit" if a.and_off else "")
    for name in configs:
        r = run_config(name, ref, starts, a.workers, a.funded_cls, a.and_off)
        if r["problems"]:
            bad = True
            print(f"REFUSED: Q-94 U1 {name.upper()} is not reproduced with recording on ({r['seconds']:.0f} s) -- "
                  + "; ".join(r["problems"][:12]), flush=True)
        else:
            print(f"identity HOLDS: Q-94 U1 {name.upper()} = results/{SI.U1_FILE}'s start rows for {name}, both arms, "
                  f"{r['starts']} of {r['of']} starts each, all {r['columns']} columns, through the adapter with the "
                  f"replay's place recording on{extra} ({r['seconds']:.0f} s)", flush=True)
        if r["records"]:
            bad = True
            print(f"records FAIL: Q-94 {name.upper()} -- " + "; ".join(r["records"][:12]), flush=True)
        else:
            print(f"records HOLD: Q-94 {name.upper()} -- one record a start, no per-start problem (Q-70's checks and "
                  f"Q-94's: the openings the replay ledger's, the routed trades on their sessions, the waits); "
                  + "; ".join(r["notes"]), flush=True)
    mem = SI.peak_memory()
    if mem:
        print(mem, flush=True)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
