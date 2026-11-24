"""Write `results/h4_registered_constants.csv` + manifest from the verified identity payload (E-286, E-247 rm-4).

Reads ZERO bars and ZERO held-out data: re-verifies every registered capacity and offered-mark list directly against
the pinned files in `vendor/stage2/results/` by sha256, validates the search-year sub-hash payload emitted by
`identity/h4_registered_constants.py`, and writes `results/h4_registered_constants.csv` via `extended.results.write_result`
from a clean checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from identity import h4_registered_constants as HRC  # noqa: E402

SCRIPT = "scripts/h4_write_registered_constants.py"
_HEX64 = re.compile(r"[0-9a-f]{64}")


def validate_payload(payload: dict[str, Any], vendor_results_dir: Path) -> list[dict[str, Any]]:
    """Re-verify capacities & offered marks directly from `vendor_results_dir` by sha256 and validate sub-hashes."""
    rows = HRC.format_rows(payload.get("rows") or [])
    by = {r["design"]: r for r in rows}

    p14_ref = HRC.read_p14_registered_capacity(vendor_results_dir)
    p15_ref = HRC.read_rc_screen_constants(
        vendor_results_dir, design="p15", screen_file=HRC.P15_SCREEN_FILE,
        expected_sha256=HRC.P15_SCREEN_SHA256, cell=HRC.P15_CELL, stop_ticks=HRC.P15_STOP_TICKS,
    )
    p16_ref = HRC.read_rc_screen_constants(
        vendor_results_dir, design="p16", screen_file=HRC.P16_SCREEN_FILE,
        expected_sha256=HRC.P16_SCREEN_SHA256, cell=HRC.P16_CELL, stop_ticks=HRC.P16_STOP_TICKS,
    )

    for design, ref in (("p14", p14_ref), ("p15", p15_ref), ("p16", p16_ref)):
        got = by[design]
        for k in ("cell", "stop_ticks", "capacity", "marks_count", "offered_marks_slots", "source_file", "source_sha256"):
            if got[k] != ref[k]:
                raise HRC.ConstantsError(f"{design} {k}: payload {got[k]!r} != registered source {ref[k]!r}")
        if "busiest_day" in ref and got["busiest_day"] != ref["busiest_day"]:
            raise HRC.ConstantsError(f"{design} busiest_day: payload {got['busiest_day']!r} != {ref['busiest_day']!r}")
        if int(got["search_trades"]) <= 0:
            raise HRC.ConstantsError(f"{design}: search_trades must be positive")
        if str(got["search_last_date"]) > HRC.SEARCH_END:
            raise HRC.ConstantsError(f"{design}: search_last_date {got['search_last_date']} > {HRC.SEARCH_END}")
        if not _HEX64.fullmatch(str(got["search_trades_sha256"])):
            raise HRC.ConstantsError(f"{design}: invalid search_trades_sha256 {got['search_trades_sha256']!r}")
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--payload", type=Path, required=True, help="JSON payload written by identity/h4_registered_constants.py")
    ap.add_argument("--vendor-root", type=Path, default=ROOT / "vendor" / "stage2")
    ap.add_argument("--out", default=HRC.RESULT_NAME)
    args = ap.parse_args(argv)

    from extended import results as RES

    raw = args.payload.read_bytes()
    payload_sha = hashlib.sha256(raw).hexdigest()
    payload = json.loads(raw.decode("utf-8"))
    rows = validate_payload(payload, args.vendor_root.resolve() / "results")
    df = pd.DataFrame(rows, columns=list(HRC.COLUMNS))
    csv_path, man_path = RES.write_result(
        df,
        args.out,
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id=HRC.DECLARATION_ROW,
        description="H4 registered constants (E-286, E-247 rm-4): P-14/P-15/P-16 capacities, offered marks, and "
                    "search-year trade sub-hashes (<= 2023-12-29)",
        parameters={
            "declaration": HRC.DECLARATION_ROW,
            "search_end": HRC.SEARCH_END,
            "identity_script": HRC.SCRIPT,
            "payload_sha256": payload_sha,
            "p14_manifest_sha256": HRC.P14_GATE_MANIFEST_SHA256,
            "p15_screen_sha256": HRC.P15_SCREEN_SHA256,
            "p16_screen_sha256": HRC.P16_SCREEN_SHA256,
            "identities": payload.get("identities", {}),
        },
    )
    print(f"Wrote {csv_path} and {man_path} ({len(df)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

