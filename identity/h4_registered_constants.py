"""H4's registered-constants extractor (`prereg/DRAFT_H4_rebaseline.md` section 2 & Appendix C; E-247 rm-4, E-286).

Writes `results/h4_registered_constants.csv` once from a clean checkout under `run.lock`, in the on-record
whole-window identity run (`extended.reader.IDENTITY`, E-247 rm-4's exception for the parents' registered
reproductions):

- **Copied by sha256 from registered Stage 2 result files** (never re-resolved on the search years):
  - P-14: `trades_per_day_capacity` from `vendor/stage2/results/a3_brk30_cb20_gate.csv.manifest.json`
    (sha256 `c9c3356760f33fa3bb5aaff8e59175bff5fd9824d004086398ed529993d003e1`, rc-10);
  - P-15: offered-mark slot list (`section == 'marks'`, `stop_ticks == 100`, `offered == True`) plus `busiest_day`
    and `capacity` (`section == 'cell'`, `cell == 'rc_s100_all'`) from `vendor/stage2/results/rc_reentry_screen.csv`
    (sha256 `dfd93c46deca5651e125ba63a8616b3b6f627beea87097593dbac27df4c37df1`);
  - P-16: offered-mark slot list (`section == 'marks'`, `stop_ticks == 150`, `offered == True`) plus `busiest_day`
    and `capacity` (`section == 'cell'`, `cell == 'rc_s150_all'`) from `vendor/stage2/results/rc_width_screen.csv`
    (sha256 `7b4b65d1130c524874de874ff242dbe3cb74fe3aa456ccd3d9fef2e9758c855d`).
- **Computed only:** the search-year sub-hash (`rc_dev_test.trades_hash`'s exact form) of each registered design's
  trigger-level trades whose trading day (A1's `date`) is on or before `2023-12-29`, after verifying every design's
  whole-window registered trades identity (`p13_trade_problems` / `trade_problems`) holds.

Slots, counts, dates (search years only), and sha256 hashes only -- zero bar prices.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCRIPT = "identity/h4_registered_constants.py"
RESULT_NAME = "h4_registered_constants.csv"
DECLARATION_ROW = "E-286"
SEARCH_END = "2023-12-29"

P14_GATE_MANIFEST = "a3_brk30_cb20_gate.csv.manifest.json"
P14_GATE_MANIFEST_SHA256 = "c9c3356760f33fa3bb5aaff8e59175bff5fd9824d004086398ed529993d003e1"

P15_SCREEN_FILE = "rc_reentry_screen.csv"
P15_SCREEN_SHA256 = "dfd93c46deca5651e125ba63a8616b3b6f627beea87097593dbac27df4c37df1"
P15_CELL = "rc_s100_all"
P15_STOP_TICKS = 100

P16_SCREEN_FILE = "rc_width_screen.csv"
P16_SCREEN_SHA256 = "7b4b65d1130c524874de874ff242dbe3cb74fe3aa456ccd3d9fef2e9758c855d"
P16_CELL = "rc_s150_all"
P16_STOP_TICKS = 150

DESIGNS = ("p14", "p15", "p16")
COLUMNS: tuple[str, ...] = (
    "design",
    "cell",
    "stop_ticks",
    "busiest_day",
    "capacity",
    "marks_count",
    "offered_marks_slots",
    "search_trades",
    "search_first_date",
    "search_last_date",
    "search_trades_sha256",
    "source_file",
    "source_sha256",
)


class ConstantsError(RuntimeError):
    """Refused: registered file hash mismatch, failed whole-window identity, or malformed constant."""


def sha256_file(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trades_content_hash(t: pd.DataFrame) -> str:
    """Exact `rc_dev_test.trades_hash` form: sorted columns, row order as built."""
    cols = sorted(t.columns)
    h = pd.util.hash_pandas_object(t[cols].reset_index(drop=True), index=False).to_numpy()
    return hashlib.sha256(h.tobytes() + "|".join(cols).encode()).hexdigest()


def search_year_subhash(t: pd.DataFrame, *, last_day: str = SEARCH_END) -> dict[str, Any]:
    """Filter trigger-level trades to trading days <= `last_day` and compute `trades_content_hash`."""
    if "date" not in t.columns:
        raise ConstantsError("trades DataFrame missing required 'date' column")
    ds = t["date"].astype(str)
    sub = t[ds <= str(last_day)].reset_index(drop=True)
    if sub.empty:
        raise ConstantsError(f"no trades with trading day <= {last_day}")
    sub_dates = sub["date"].astype(str)
    last_seen = str(sub_dates.max())
    if last_seen > str(last_day):
        raise ConstantsError(f"filtered trades still hold trading day {last_seen} > {last_day}")
    return {
        "search_trades": int(len(sub)),
        "search_first_date": str(sub_dates.min()),
        "search_last_date": last_seen,
        "search_trades_sha256": trades_content_hash(sub),
    }


def read_p14_registered_capacity(rd: Path, *, expected_sha256: str = P14_GATE_MANIFEST_SHA256) -> dict[str, Any]:
    """Read P-14's `trades_per_day_capacity` from its pinned Stage 2 gate manifest (rc-10)."""
    p = Path(rd) / P14_GATE_MANIFEST
    if not p.is_file():
        raise ConstantsError(f"missing P-14 manifest: {p}")
    got = sha256_file(p)
    if got != expected_sha256:
        raise ConstantsError(f"{P14_GATE_MANIFEST} sha256 {got} != expected {expected_sha256}")
    man = json.loads(p.read_text(encoding="utf-8"))
    params = man.get("parameters") or {}
    cap = params.get("trades_per_day_capacity")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0:
        raise ConstantsError(f"{P14_GATE_MANIFEST} invalid trades_per_day_capacity: {cap!r}")
    return {
        "design": "p14",
        "cell": "a3_brk30_cb20",
        "stop_ticks": 0,
        "capacity": int(cap),
        "marks_count": 0,
        "offered_marks_slots": "",
        "source_file": P14_GATE_MANIFEST,
        "source_sha256": got,
    }


def read_rc_screen_constants(
    rd: Path,
    *,
    design: str,
    screen_file: str,
    expected_sha256: str,
    cell: str,
    stop_ticks: int,
) -> dict[str, Any]:
    """Read P-15 or P-16 registered `busiest_day`, `capacity`, and `offered_marks` slot list by sha256."""
    p = Path(rd) / screen_file
    if not p.is_file():
        raise ConstantsError(f"missing screen file: {p}")
    got = sha256_file(p)
    if got != expected_sha256:
        raise ConstantsError(f"{screen_file} sha256 {got} != expected {expected_sha256}")
    df = pd.read_csv(p, low_memory=False)
    cell_rows = df[(df["section"].astype(str) == "cell") & (df["cell"].astype(str) == cell)]
    if len(cell_rows) != 1:
        raise ConstantsError(f"{screen_file}: expected 1 cell row for {cell}, found {len(cell_rows)}")
    r = cell_rows.iloc[0]
    busiest = int(round(float(r["busiest_day"])))
    cap = int(round(float(r["capacity"])))
    marks_offered = int(round(float(r["marks_offered"])))
    if busiest <= 0 or cap < busiest:
        raise ConstantsError(f"{screen_file} {cell}: invalid busiest_day={busiest}, capacity={cap}")

    mk = df[df["section"].astype(str) == "marks"].copy()
    mk = mk[pd.to_numeric(mk["stop_ticks"], errors="coerce") == float(stop_ticks)]
    offered_mask = mk["offered"].astype(str).str.strip().str.lower().isin(("true", "1", "1.0"))
    slots = sorted(int(round(float(x))) for x in mk.loc[offered_mask, "slot"])
    if len(slots) != marks_offered or len(set(slots)) != len(slots):
        raise ConstantsError(
            f"{screen_file} {cell}: offered marks count {len(slots)} != cell marks_offered {marks_offered}"
        )
    return {
        "design": design,
        "cell": cell,
        "stop_ticks": int(stop_ticks),
        "busiest_day": busiest,
        "capacity": cap,
        "marks_count": len(slots),
        "offered_marks_slots": " ".join(str(s) for s in slots),
        "source_file": screen_file,
        "source_sha256": got,
    }


def parse_slots(text: str) -> tuple[int, ...]:
    s = str(text or "").strip()
    if not s:
        return ()
    out = tuple(int(tok) for tok in s.split())
    if list(out) != sorted(set(out)):
        raise ConstantsError(f"offered_marks_slots must be strictly increasing unique ints: {text!r}")
    return out


def format_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_design = {str(r["design"]): dict(r) for r in rows}
    if tuple(by_design) != DESIGNS and set(by_design) != set(DESIGNS):
        raise ConstantsError(f"constants must cover exactly {DESIGNS}, got {sorted(by_design)}")
    ordered = []
    for d in DESIGNS:
        r = by_design[d]
        missing = [c for c in COLUMNS if c not in r]
        if missing:
            raise ConstantsError(f"{d}: missing columns {missing}")
        ordered.append({c: r[c] for c in COLUMNS})
    return ordered


def load_registered_constants(path: Path | str, *, expected_sha256: str | None = None) -> dict[str, dict[str, Any]]:
    """Load `results/h4_registered_constants.csv`, checking its sidecar manifest sha256 (and `expected_sha256`)."""
    p = Path(path)
    if not p.is_file():
        raise ConstantsError(f"missing registered-constants file: {p}")
    raw = p.read_bytes()
    file_sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and file_sha != expected_sha256:
        raise ConstantsError(f"{p.name}: sha256 {file_sha} != expected {expected_sha256}")
    side = Path(str(p) + ".manifest.json")
    if not side.is_file():
        raise ConstantsError(f"{p.name}: missing sidecar manifest {side.name}")
    man = json.loads(side.read_text(encoding="utf-8"))
    if man.get("sha256") != file_sha:
        raise ConstantsError(f"{p.name}: sha256 {file_sha} != manifest sha256 {man.get('sha256')}")

    with p.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if tuple(rd.fieldnames or ()) != COLUMNS:
            raise ConstantsError(f"{p.name}: columns {tuple(rd.fieldnames or ())} != {COLUMNS}")
        rows = list(rd)

    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        d = str(r["design"])
        if d in out:
            raise ConstantsError(f"{p.name}: duplicate design {d!r}")
        slots = parse_slots(r["offered_marks_slots"])
        marks_count = int(r["marks_count"])
        if len(slots) != marks_count:
            raise ConstantsError(f"{p.name} {d}: marks_count {marks_count} != parsed slots {len(slots)}")
        last_d = str(r["search_last_date"])
        if last_d > SEARCH_END:
            raise ConstantsError(f"{p.name} {d}: search_last_date {last_d} > {SEARCH_END}")
        out[d] = {
            "design": d,
            "cell": str(r["cell"]),
            "stop_ticks": int(r["stop_ticks"]),
            "busiest_day": int(r["busiest_day"]),
            "capacity": int(r["capacity"]),
            "marks_count": marks_count,
            "offered_marks": slots,
            "search_trades": int(r["search_trades"]),
            "search_first_date": str(r["search_first_date"]),
            "search_last_date": last_d,
            "search_trades_sha256": str(r["search_trades_sha256"]),
            "source_file": str(r["source_file"]),
            "source_sha256": str(r["source_sha256"]),
            "file_sha256": file_sha,
        }
    if tuple(out) != DESIGNS:
        raise ConstantsError(f"{p.name}: expected designs {DESIGNS}, got {tuple(out)}")
    return out


def _setup_vendor(vendor_root: Path) -> None:
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    sys.path.insert(0, str(vendor_root))
    sys.path.insert(0, str(vendor_root / "scripts"))
    sys.dont_write_bytecode = True


def collect_from_vendor(vendor_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build P-14, P-15, P-16 whole-window trades, verify every registered identity, and extract H4 constants."""
    _setup_vendor(vendor_root)
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_screen as S
    from propedge.research import resolved_coin as rc

    rd = vendor_root / "results"
    rows: list[dict[str, Any]] = []
    ident_checks: dict[str, Any] = {}

    # --- P-14 ---
    p14_meta = read_p14_registered_capacity(rd)
    I_p14 = S.inputs()
    t_p14, days_p14 = B.cell_trades(I_p14["L"])
    bad_p14 = C.p13_trade_problems(rd, t_p14, days_p14, I_p14["L"])
    if bad_p14:
        raise ConstantsError(f"P-14 registered trades identity failed: {bad_p14[:4]}")
    p14_busiest = int(B.busiest(t_p14))
    p14_cap_got = int(B.capacity(t_p14, I_p14["L"]["fcfg"]))
    if p14_cap_got != p14_meta["capacity"]:
        raise ConstantsError(f"P-14 capacity {p14_cap_got} != manifest {p14_meta['capacity']}")
    p14_sub = search_year_subhash(t_p14)
    if p14_sub["search_trades_sha256"] != D.trades_hash(t_p14[t_p14["date"].astype(str) <= SEARCH_END]):
        raise ConstantsError("internal error: trades_content_hash diverged from rc_dev_test.trades_hash")
    rows.append({**p14_meta, "busiest_day": p14_busiest, **p14_sub})
    ident_checks["p14"] = {"whole_trades": int(len(t_p14)), "whole_days": int(len(days_p14)),
                           "capacity_matched": True, "p13_trade_problems": 0}

    # --- P-15 ---
    p15_meta = read_rc_screen_constants(
        rd, design="p15", screen_file=P15_SCREEN_FILE, expected_sha256=P15_SCREEN_SHA256,
        cell=P15_CELL, stop_ticks=P15_STOP_TICKS,
    )
    I_p15, b_p15 = D.build_cells()
    bad_p15 = D.trade_problems(rd, b_p15, I_p15["L"]["fcfg"], spec=D.P15)
    if bad_p15:
        raise ConstantsError(f"P-15 registered trades identity failed: {bad_p15[:4]}")
    t_p15 = b_p15["cells"][P15_CELL]["trades"]
    marks_p15_got = rc.offered_marks(b_p15["table"], P15_STOP_TICKS)
    if tuple(marks_p15_got) != parse_slots(p15_meta["offered_marks_slots"]):
        raise ConstantsError("P-15 built offered_marks != rc_reentry_screen.csv offered marks")
    if int(B.capacity(t_p15, I_p15["L"]["fcfg"])) != p15_meta["capacity"]:
        raise ConstantsError("P-15 built capacity != rc_reentry_screen.csv capacity")
    p15_sub = search_year_subhash(t_p15)
    rows.append({**p15_meta, **p15_sub})
    ident_checks["p15"] = {"whole_trades": int(len(t_p15)), "whole_days": int(len(b_p15["days"])),
                           "marks_matched": True, "capacity_matched": True, "trade_problems": 0}

    # --- P-16 ---
    p16_meta = read_rc_screen_constants(
        rd, design="p16", screen_file=P16_SCREEN_FILE, expected_sha256=P16_SCREEN_SHA256,
        cell=P16_CELL, stop_ticks=P16_STOP_TICKS,
    )
    I_p16, b_p16 = R150.build_cells()
    bad_p16 = D.trade_problems(rd, b_p16, I_p16["L"]["fcfg"], spec=R150.SPEC)
    if bad_p16:
        raise ConstantsError(f"P-16 registered trades identity failed: {bad_p16[:4]}")
    t_p16 = b_p16["cells"][P16_CELL]["trades"]
    marks_p16_got = rc.offered_marks(b_p16["table"], P16_STOP_TICKS)
    if tuple(marks_p16_got) != parse_slots(p16_meta["offered_marks_slots"]):
        raise ConstantsError("P-16 built offered_marks != rc_width_screen.csv offered marks")
    if int(B.capacity(t_p16, I_p16["L"]["fcfg"])) != p16_meta["capacity"]:
        raise ConstantsError("P-16 built capacity != rc_width_screen.csv capacity")
    p16_sub = search_year_subhash(t_p16)
    rows.append({**p16_meta, **p16_sub})
    ident_checks["p16"] = {"whole_trades": int(len(t_p16)), "whole_days": int(len(b_p16["days"])),
                           "marks_matched": True, "capacity_matched": True, "trade_problems": 0}

    return format_rows(rows), ident_checks


def _ensure_outside_results(path: Path) -> Path:
    parts = [p.lower() for p in path.resolve().parts]
    if "results" in parts:
        raise ConstantsError(f"REFUSED (IDENTITY_WRITE_RULE): payload path must be outside results/: {path}")
    return path


def _require_run_lock(root: Path) -> None:
    """Verify run.lock exists at main_root(root) and matches S2X_LOCK_HOLDER (scripts/run_clean.py --hours/--mem-gb)."""
    from extended import lock_guard as LG

    holder = os.environ.get(LG.LOCK_HOLDER_ENV, "").strip()
    if not holder:
        raise ConstantsError(
            f"REFUSED: {LG.LOCK_HOLDER_ENV} is unset (run under run.lock via scripts/run_clean.py --hours --mem-gb --task)"
        )
    mroot = LG.main_root(root)
    if mroot is None:
        raise ConstantsError(f"REFUSED: cannot resolve main repository root for run.lock from {root}")
    lock_file = mroot / LG.LOCK_NAME
    if not lock_file.is_file():
        raise ConstantsError(f"REFUSED: run.lock not found at {lock_file}")
    try:
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConstantsError(f"REFUSED: cannot read run.lock: {exc}") from exc
    if not isinstance(lock_data, dict) or lock_data.get("job") != holder:
        raise ConstantsError(
            f"REFUSED: run.lock job {lock_data.get('job') if isinstance(lock_data, dict) else None!r} != {holder!r}"
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vendor-root", type=Path, default=ROOT / "vendor" / "stage2")
    ap.add_argument("--out-payload", type=Path, required=True, help="JSON payload path outside results/")
    args = ap.parse_args(argv)

    from extended import reader
    from identity import stage2_identity as S2I

    out_path = _ensure_outside_results(args.out_payload)
    _require_run_lock(ROOT)
    vroot = args.vendor_root.resolve()
    files = S2I.engine_files(vroot, a3=True, bars=True)
    reader.authorise_engine_read(
        reader.CHOICE_START,
        reader.JUDGED_END,
        purpose=reader.IDENTITY,
        declaration=DECLARATION_ROW,
        files=files,
        what="E-286 / H4 registered constants (E-247 rm-4): verify registered identities and extract search-year "
             "sub-hashes for P-14, P-15, P-16 (writes no result file)",
    )

    rows, ident_checks = collect_from_vendor(vroot)
    payload = {
        "script": SCRIPT,
        "declaration": DECLARATION_ROW,
        "search_end": SEARCH_END,
        "p14_manifest_sha256": P14_GATE_MANIFEST_SHA256,
        "p15_screen_sha256": P15_SCREEN_SHA256,
        "p16_screen_sha256": P16_SCREEN_SHA256,
        "identities": ident_checks,
        "rows": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"identity HOLDS: P-14, P-15, P-16 verified; wrote {len(rows)} registered-constant rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

