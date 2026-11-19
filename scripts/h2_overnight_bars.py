"""Q-154 (H2, E-208): the data-integrity check of NQ's overnight 1-minute bars (17:00 to 08:29 CT), and its report.

    python scripts/run_clean.py --name q154-h2 -- python scripts/h2_overnight_bars.py      # the run (the lead's)
    python scripts/h2_overnight_bars.py --render docs/audits/H2_overnight_bars_2026-11-18.json  # re-render, no bar
    python scripts/h2_overnight_bars.py --held-out --purpose <p> --declaration <d>      # only once a row allows it

**Outputs, relative to the repository root of the tree it runs in** (so a clean run writes them inside its own
checkout, for `scripts/run_clean.py --collect`): the report `docs/audits/H2_overnight_bars_2026-11-18.md` (`--report`),
its JSON beside it (`--json`: counts, shares, clock labels and dates), and, inside a clean run only, the per-day flags
`results/h2_overnight_flags.csv` through `extended.results.write_result` (sidecar manifest; no price column). Outside
a clean run the flags are written only where `--flags` names (never `results/`).

**Exit status is the verdict:** 0 VALIDATED, 3 BLOCKED (a check failed or could not run -- with the held-out years
sealed, this is the expected status), 1 an error. The last line printed is one summary line:
`H2 <VERDICT>: <reasons> | report <path>`.

**Heavy** (it reads the search years' full bars): run it under the run lock (`scripts/run_lock.py`), one at a time,
with `OMP_NUM_THREADS=1`. The search years (2020-01-02 to 2023-12-29) are read through `extended.reader.read_bars` one
calendar year at a time; every frame is refused if it holds a bar at or after 16:00 CT on 2026-07-16
(`extended.overnight_bars_check.assert_loaded`). The held-out years are sealed by the reader: by default their section
is built from the store's manifest only; `--held-out` passes `--purpose` and `--declaration` to the reader, which
refuses unless a pinned declaration names that purpose and the process runs in a clean run (Q-158). The logic and the
void rules are `extended/overnight_bars_check.py`'s; this file only reads, assembles and writes.

Outputs: the JSON (counts, shares, clock labels, dates), the per-day flag CSV (no price column) and the report.
"""
from __future__ import annotations

import argparse
import hashlib
import csv
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import overnight_bars_check as K  # noqa: E402
from extended import reader  # noqa: E402

MANIFEST = ROOT / "vendor" / "stage2" / "data" / "bars" / "NQ" / "manifest.json"
SAMPLE_SIZE = ROOT / "vendor" / "stage2" / "vendor" / "propsim" / "edge" / "results_sample_size.csv"
COLUMNS = ["ts", "day", "contract", "open", "high", "low", "close", "volume"]
SCHEMA = {"ts": "int64", "day": "string", "contract": "string", "open": "float64", "high": "float64",
          "low": "float64", "close": "float64", "volume": "int64"}
#: pandas names a text column `object`, `str` or `string` by version and option: all are README's "string"
TEXT_DTYPES = {"object", "str", "string"}


def dtype_name(s) -> str:
    n = str(s.dtype)
    return "string" if n in TEXT_DTYPES or n.startswith("string") else n


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def year_spans(start: date, end: date) -> list[tuple[str, str]]:
    out = []
    y = start.year
    while y <= end.year:
        a = max(start, date(y, 1, 1))
        b = min(end, date(y, 12, 31))
        out.append((a.isoformat(), b.isoformat()))
        y += 1
    return out


def read_block(block: tuple[date, date], ctx, hours, *, purpose=None, declaration=None):
    """Every day record of a block, read a year at a time; the schema seen; the last day loaded."""
    if block[1] > K.LAST_DEV_DAY:
        raise SystemExit("REFUSED: the block ends after 2026-07-16 (the confirmation window)")
    recs, carry, schema = [], None, None
    for a, b in year_spans(*block):
        df = reader.read_bars(a, b, purpose=purpose, declaration=declaration, columns=COLUMNS,
                              what=f"Q-154 H2 overnight bars check {a}..{b}")
        K.assert_loaded(df["ts"].to_numpy(), df["day"].unique(), block[1])
        seen = {c: dtype_name(df[c]) for c in COLUMNS}
        schema = seen if schema is None else schema
        if seen != schema:
            raise SystemExit(f"the dtypes changed between years: {schema} then {seen}")
        r, carry = K.day_records(df, ctx, hours, carry)
        recs.extend(r)
        print(f"read {a}..{b}: {len(r)} days", flush=True)
        del df
    return recs, schema


REPORT_REL = "docs/audits/H2_overnight_bars_2026-11-18.md"
JSON_REL = "docs/audits/H2_overnight_bars_2026-11-18.json"
FLAGS_RESULT = "h2_overnight_flags.csv"
EXIT_VALIDATED, EXIT_BLOCKED = 0, 3


def _under_root(p: Path) -> Path:
    return p if p.is_absolute() else ROOT / p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", type=Path, default=Path(JSON_REL), help="the summary JSON (relative to the root)")
    ap.add_argument("--flags", type=Path, default=None,
                    help="outside a clean run: write the per-day flag CSV here (never results/)")
    ap.add_argument("--report", type=Path, default=Path(REPORT_REL), help="the report (relative to the root)")
    ap.add_argument("--render", type=Path, help="re-render the report from this JSON (reads no bar)")
    ap.add_argument("--held-out", action="store_true", help="read the held-out years' bars (the reader decides)")
    ap.add_argument("--purpose", default=None)
    ap.add_argument("--declaration", default=None)
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args(argv)

    args.json, args.report = _under_root(args.json), _under_root(args.report)
    if args.render:
        args.render = _under_root(args.render)
        res = json.loads(args.render.read_text(encoding="utf-8"))
        res.setdefault("meta", {})["rendered"] = {
            "json": args.render.name, "json_sha256": hashlib.sha256(args.render.read_bytes()).hexdigest(),
            "renderer_sha256": hashlib.sha256((ROOT / "extended" / "overnight_bars_check.py").read_bytes()).hexdigest()}
        args.report.write_text(K.render(res), encoding="utf-8", newline="\n")
        v, why = K.verdict(res["search"], res.get("held_out_bar_checked", False), res.get("extra_reasons", ()))
        print(f"rendered {args.report.relative_to(ROOT) if ROOT in args.report.parents else args.report}: H2 {v}")
        return 0

    from extended import features as F
    from extended import lever_space as LS
    from extended.calendar_early_closes import read_calendar

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["last_day"] >= K.CONFIRMATION_START.isoformat():
        raise SystemExit("REFUSED: the store's manifest lists a day in the confirmation window")
    days_all = [date.fromisoformat(d) for d in manifest["day_list"]]
    cal = read_calendar()
    ctx = K.contexts(days_all, cal)
    cals = F.load_calendars()
    bls, bls_major = cals.bls, cals.bls_major
    dst = K.us_dst_changes(range(2019, 2027))
    na: dict[str, str] = {}
    for imp in manifest["imports"]:
        na.update(((imp.get("condition") or {}).get("not_available")) or {})
    seams = [d for d in days_all if ctx[d].defect and "purchase edge" in ctx[d].defect]

    verify = subprocess.run([sys.executable, str(ROOT / "scripts" / "vendor_stage2.py"), "--verify"], cwd=ROOT,
                            capture_output=True, text=True, timeout=1800)
    vlines = [x for x in (verify.stdout + verify.stderr).splitlines() if x.strip()]
    verify_txt = f"exit {verify.returncode}; " + (vlines[-1] if vlines else "no output")
    extra: list[str] = []
    if verify.returncode != 0:
        extra.append(f"the data's hashes do not match vendor/DATA_MANIFEST_stage2.sha256 ({verify_txt}): these are "
                     "not the data the identities were proved on (E-002, E-004)")

    hours = K.HourAgg()
    recs, schema = read_block(K.SEARCH, ctx, hours)
    summary, rows = K.aggregate(recs, ctx, block=K.SEARCH, rolls=manifest["rolls"], dst_changes=dst, bls_days=bls,
                                bls_major_days=bls_major, not_available=na, seams=[d.isoformat() for d in seams],
                                bounds=manifest["day_bounds"], hours=hours)
    held_rows = []
    if args.held_out:
        hh = K.HourAgg()
        hrecs, _ = read_block(K.HELD_OUT, ctx, hh, purpose=args.purpose, declaration=args.declaration)
        held, held_rows = K.aggregate(hrecs, ctx, block=K.HELD_OUT, rolls=manifest["rolls"], dst_changes=dst,
                                      bls_days=bls, bls_major_days=bls_major, not_available=na, seams=[d.isoformat() for d in seams],
                                      bounds=manifest["day_bounds"], hours=hh)
    else:
        held = K.manifest_block(manifest, ctx, block=K.HELD_OUT, dst_changes=dst, bls_days=bls, not_available=na)

    with SAMPLE_SIZE.open(encoding="utf-8") as fh:
        ss = list(csv.DictReader(fh))
    td = LS.trading_day()
    hm = lambda m: f"{m // 60:02d}:{m % 60:02d}"  # noqa: E731
    if schema != SCHEMA:
        extra.append(f"the columns or dtypes differ from README section 5 ({schema})")
    res = {
        "held_out_bar_checked": bool(args.held_out), "extra_reasons": extra,
        "search": summary, "held_out": held, "power": K.power(manifest, ss),
        "meta": {
            "date": args.date, "commit": _git("rev-parse", "HEAD"),
            "tree": "clean" if not _git("status", "--porcelain", "--untracked-files=no") else "uncommitted changes",
            "ran": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "verify": verify_txt,
            "code_sha256": {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
                            for rel in ("scripts/h2_overnight_bars.py", "extended/overnight_bars_check.py")},
            "schema": ("columns and dtypes as README section 5: " + ", ".join(f"`{k}` {v}" for k, v in schema.items())
                       if schema == SCHEMA else f"DIFFERS from README section 5: {schema}"),
            "trading_day": {"reopen_ct": hm(td["reopen"]), "flat_ct": hm(td["flat"])},
            "manifest": {k: manifest[k] for k in ("decision", "licence", "tick", "parquet_sha256", "first_day",
                                                  "last_day", "days", "rows", "rolls")}
            | {"imports": [{"source": i["source"], "csv": i["csv"], "dataset": i["query"]["dataset"],
                            "schema": i["query"]["schema"], "symbols": i["query"]["symbols"],
                            "imported": i["imported"], "days_dropped_by_window": i["days_dropped_by_window"],
                            "first_dropped_day": i["first_dropped_day"]} for i in manifest["imports"]]},
        },
    }
    flag_rows = rows + held_rows
    from extended import CLEAN_RUN_ENV
    from extended.results import clean_run_problem
    flags_out = None
    if os.environ.get(CLEAN_RUN_ENV) and clean_run_problem() is None:
        import pandas as pd
        from extended.results import write_result
        csv_path, _ = write_result(
            pd.DataFrame(flag_rows, columns=list(K.FLAG_COLUMNS)), FLAGS_RESULT, script="scripts/h2_overnight_bars.py",
            seed=None, require_seed=False, description="Q-154 (H2): per trading day of the search years, the "
            "overnight's (17:00-08:29 CT) counts, clock labels and void / special flags; no price column",
            parameters={"void_gap_min": K.VOID_GAP, "reopen_tol_min": K.REOPEN_TOL, "special_gap_min": K.SPECIAL_GAP,
                        "blocks": {"search": [str(x) for x in K.SEARCH],
                                   "held_out_bars_read": bool(args.held_out)}})
        flags_out = Path(csv_path)
    elif args.flags is not None:
        flags_out = _under_root(args.flags)
        if "results" in flags_out.relative_to(ROOT).parts if ROOT in flags_out.parents else False:
            raise SystemExit("REFUSED: the flags go to results/ only through extended.results inside a clean run")
        flags_out.write_text(K.flags_csv(flag_rows), encoding="utf-8", newline="\n")
    res["meta"]["flags"] = str(flags_out.relative_to(ROOT)) if flags_out and ROOT in flags_out.parents else (
        str(flags_out) if flags_out else None)
    text = json.dumps(res, indent=1, default=str)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(text + "\n", encoding="utf-8", newline="\n")
    args.report.write_text(K.render(json.loads(text)), encoding="utf-8", newline="\n")
    v, why = K.verdict(summary, bool(args.held_out), extra)
    rel = args.report.relative_to(ROOT) if ROOT in args.report.parents else args.report
    print(f"H2 {v}: " + (" | ".join(why) or "every check passed") + f" | report {rel}", flush=True)
    return EXIT_VALIDATED if v == "VALIDATED" else EXIT_BLOCKED


if __name__ == "__main__":
    try:
        code = main()
    except SystemExit:
        raise
    except Exception as exc:                          # an error is not a verdict: exit 1, one line
        print(f"H2 ERROR: {type(exc).__name__}: {exc}", flush=True)
        raise SystemExit(1) from exc
    sys.exit(code)
