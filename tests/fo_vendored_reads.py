"""F-03's run-1 reads of registered result files after the walk, checked against the files themselves (Q-117f;
`tests/test_fo_vendored_reads.py` runs it in a process of its own, the vendored tree on the path).

    python tests/fo_vendored_reads.py <repository root>        # prints one JSON line last

**What run 1 reads after the walk** (`scripts/fo_opening.py`'s `run1`, after A1's replay identities): `Ctx.mean_dv`
-> `mean_dv_c` (`vendor/stage2/results/u_value_map.csv`, 7.4's mean_dv(c)) and `Ctx.follow_lifts` ->
`extended.opening_stats.amplitude_b` (`s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv`, a*'s (b)), and the
bytes of `vendor/DATA_MANIFEST_stage2.sha256` (a sha256 into the manifest). Everything before them ran in run 1.
Run 2 reads the same two and, further, P-14's start rows in `user_journey.csv` (`p_bound.load_starts`).

**No outcome number leaves this script.** On the vendored files it prints only header names, manifest agreement, row
counts and whether each selected value is finite -- never a value. The synthetic cases (a value map in the vendored
long schema, `tests/fo_value_map_fixture.py`) print their synthetic values.
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import pandas as pd  # noqa: E402

import fo_opening as FO  # noqa: E402
import fo_value_map_fixture as VM  # noqa: E402  (this script's own folder, tests/, is on the path)

from extended import opening_stats as ST  # noqa: E402

VENDORED = REPO / "vendor" / "stage2" / "results"


def attempt(results_dir: Path) -> dict:
    try:
        return {"ok": True, "value": FO.mean_dv_c(results_dir=results_dir)}
    except SystemExit as exc:
        return {"ok": False, "refused": str(exc).startswith("REFUSED (F-03)"), "msg": str(exc)}
    except Exception as exc:                                     # anything else is the defect this file guards against
        return {"ok": False, "refused": False, "error": f"{type(exc).__name__}: {exc}"}


def header(p: Path) -> list[str]:
    import csv

    with open(p, newline="", encoding="utf-8") as fh:
        return next(csv.reader(fh))


def manifest_columns(p: Path) -> list[str]:
    return list(json.loads(Path(str(p) + ".manifest.json").read_text(encoding="utf-8"))["columns"])


out: dict = {"synthetic": {}}
# ---- the synthetic value maps (the vendored header, synthetic rows)
cases = {
    "long": dict(records=VM.rows(1000.0)),
    "missing": dict(records=VM.rows(target=False)),
    "duplicate": dict(records=VM.rows(1000.0, duplicate=True)),
    "nan": dict(records=VM.rows(float("nan"))),
    "blank": dict(records=VM.rows("")),
    "inf": dict(records=VM.rows(float("inf"))),
    "text": dict(records=VM.rows("n/a")),
    "wide": dict(records=[{"section": "place_values", "base": "p16", "place": "c_funded_opening", "mean_dv": 1000.0}],
                 columns=["section", "base", "place", "mean_dv"]),
}
with tempfile.TemporaryDirectory(prefix="q117f_") as tmp:
    for name, kw in cases.items():
        d = Path(tmp) / name
        d.mkdir()
        VM.write(REPO, d, **kw)
        out["synthetic"][name] = attempt(d)
    d = Path(tmp) / "tampered"                                   # the bytes changed after the manifest: refused
    d.mkdir()
    p = VM.write(REPO, d, records=VM.rows(1000.0))
    p.write_bytes(p.read_bytes().replace(b"1000.0", b"1001.0"))
    out["synthetic"]["tampered"] = attempt(d)
    d = Path(tmp) / "fixture_header"
    d.mkdir()
    out["fixture_header"] = header(VM.write(REPO, d))

# ---- the vendored files: names, counts and finiteness only
vm = VENDORED / VM.VALUE_MAP
out["vm_header"] = header(vm)
out["vm_manifest_matches"] = out["vm_header"] == manifest_columns(vm)
_d = pd.read_csv(vm, float_precision="round_trip", low_memory=False)
out["vm_rows_selected"] = int(len(FO.value_map_rows(_d)))
del _d
try:
    out["vm_finite"] = bool(math.isfinite(FO.mean_dv_c()))       # the default: the vendored results folder
except SystemExit as exc:
    out["vm_refused"] = str(exc)
out["follow_lifts_declared"] = [list(x) for x in ST.FOLLOW_LIFTS]
out["follow_schema"] = {}
for name in dict.fromkeys(f for f, _, _ in ST.FOLLOW_LIFTS):
    p = VENDORED / name
    h = header(p)
    need = {"section", "rule", "R", "mean_lift"} | ({"latency"} if any(f == name and lat is not None
                                                                       for f, _, lat in ST.FOLLOW_LIFTS) else set())
    out["follow_schema"][name] = {"manifest_matches": h == manifest_columns(p), "missing": sorted(need - set(h))}
from propedge import RESULTS_DIR as _VR  # noqa: E402

out["vendored_results_dir_is_the_snapshot"] = Path(_VR).resolve() == VENDORED.resolve()
try:
    _rows = ST.amplitude_b(_VR)[1]
    out["follow_keys"] = [[r["file"], r["rule"], r["latency"]] for r in _rows]
    out["follow_finite"] = [bool(math.isfinite(r["abs_mean_lift"])) for r in _rows]
    del _rows
except Exception as exc:
    out["follow_error"] = f"{type(exc).__name__}: {exc}"
out["data_manifest_file"] = (REPO / "vendor" / "DATA_MANIFEST_stage2.sha256").is_file()

# ---- run 2's one further registered read (`Ctx.p14_ahead`, `Ctx.p14_ahead_choice` -> `p_bound.load_starts`): P-14's
# start rows in `user_journey.csv`, both scorecard arms -- the columns it reads and the row counts, nothing else
from extended import p_bound as PB  # noqa: E402

jf = Path(PB.JOURNEY_FILE)
out["journey_is_vendored"] = jf.resolve() == (VENDORED / "user_journey.csv").resolve()
_h = header(jf)
out["journey_manifest_matches"] = _h == manifest_columns(jf)
out["journey_missing"] = sorted({"section", "config", "arm", "start_date", "observed", "net_month_1", "net_month_2",
                                 "net_month_3"} - set(_h))
_j = pd.read_csv(jf, usecols=["section", "config", "arm"], dtype=str, low_memory=False)
out["journey_p14_start_rows"] = {a: int(((_j["section"] == "start") & (_j["config"] == "p14") & (_j["arm"] == a)).sum())
                                 for a in FO.SCORECARD_ARMS}
_l = PB.load_starts(configs=("p14",), arms=tuple(FO.SCORECARD_ARMS))
out["journey_loaded"] = {a: int(len(_l[("p14", a)])) if ("p14", a) in _l else None for a in FO.SCORECARD_ARMS}
del _j, _l
print(json.dumps(out, sort_keys=True, default=str))
