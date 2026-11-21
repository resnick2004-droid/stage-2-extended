"""W42-R1's one application (`docs/plans/WAVE42_SETTING_RULE.md` section 9; the red team's second read V-1 and V-2, the
lead's rulings): the declared, pinned way to apply `extended.wave42.setting_rule`, once, to H4's one output.

    python scripts/run_clean.py --name w42-r1 -- python scripts/wave42_apply.py

It takes no argument: every path is a declared name in this repository's `results/`. In order, refusing
(`ApplyRefused`, or the rule's own `Wave42Refused`) before anything is written:

1. **Applied once.** `results/w42_r1_values.csv` (`OUTPUT_NAME`) or its manifest exists, or any other `results/w42_*`
   file: refused. `extended.results.write_result` refuses to overwrite as well, and refuses outside a clean run.
2. **H4's collection result** (`results/h4_w42_input.csv`, `COLLECTION_RESULT`) and its sidecar are read from disk.
   The script computes the file's sha256 and the sidecar's own sha256 (its bytes with CRLF normalised to LF, R3-2),
   and refuses a sidecar whose recorded sha256 is not the file's. The binding's fields are the sidecar's parameters (`H4_MANIFEST_KEYS`), the file's sha256 its
   `sha256`.
3. **The search calendar** is Q-197's pinned result (`results/search_calendar.csv`), read through its loader
   (`extended.search_calendar.load_search_calendar`). Its file's sha256 must be `SEARCH_CALENDAR_SHA256`, which is
   filled in before the pin; while it is unset the script refuses.
4. **The held-out start counts** are `complete_starts` of the pinned held-out session calendar
   (`results/q82_judged_sessions.csv`, `HELD_OUT_CALENDAR`): its bytes must hash to `HELD_OUT_CALENDAR_SHA256`, and
   only its `date` column is read, every date inside 2024-01-02..2026-07-16 and increasing (the rule's held-out read
   ledger entry, section 10). No outcome is read.
5. **The fee unit** is the Standard path's monthly subscription, read through `extended.levers_terms.standard_prices`
   (Stage 2's verified `subscription_fee`); the ledger file's sha256 is recorded.
6. **The readings** are built by the one named adapter (`ADAPTER`, `extended.h4_collect.w42_readings`, H4's, with its
   bit-for-bit round-trip test), from the collection file and its sidecar.
7. `setting_rule` is applied, and its values are written once, to `OUTPUT_NAME`, through `write_result`, with every
   hash in the manifest's parameters: H4's file and sidecar, the readings, both calendars, the ledger, the rule text,
   the rule's module and this script.

`apply` takes its sources as one `Sources` value so that its tests can run it on synthetic files; `main`, the declared
application, passes only `declared_sources()`.
"""
from __future__ import annotations

import csv
import hashlib
import importlib
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import wave42 as R  # noqa: E402  (pure: no engine, no file)

SCRIPT = "scripts/wave42_apply.py"
RULE_TEXT = "docs/plans/WAVE42_SETTING_RULE.md"
RULE_MODULE = "extended/wave42.py"
LEDGER_FILE = "vendor/stage2/config/rules.yaml"
MANIFEST_SUFFIX = ".manifest.json"
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


class ApplyRefused(RuntimeError):
    """W42-R1's application refuses before anything is written."""


def _refuse(msg: str) -> ApplyRefused:
    return ApplyRefused(f"W42-R1's application refuses: {msg}")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path | str) -> str:
    return sha256_bytes(Path(p).read_bytes())


def sidecar_sha256(b: bytes) -> str:
    """R3-2: the sidecar's sha256 over its bytes with every CRLF normalised to LF -- the bytes the writer wrote and git
    stores, the same on any checkout under `core.autocrlf`; any other difference changes it."""
    return sha256_bytes(b.replace(b"\r\n", b"\n"))


@dataclass(frozen=True)
class Sources:
    """Where the application's inputs come from: the adapter (collection csv path, sidecar dict) -> readings; the
    search calendar's loader (path) -> an object with `dates`, `calendar_sha256` and `file_sha256`; the fee () ->
    (fee unit, its source, the ledger file's sha256); the writer, `write_result`'s signature."""
    adapter: Callable[[Path, Mapping[str, Any]], Any]
    calendar_loader: Callable[[Path], Any]
    fee: Callable[[], tuple[float, str, str]]
    writer: Callable[..., Any]


def _import(dotted: str) -> Callable[..., Any]:
    mod, _, attr = dotted.partition(":")
    try:
        return getattr(importlib.import_module(mod), attr)
    except (ImportError, AttributeError) as e:
        raise _refuse(f"{dotted} is not built on this commit ({e.__class__.__name__}: {e})") from e


def _declared_fee() -> tuple[float, str, str]:
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from extended.levers_terms import standard_prices

    subscription, _activation = standard_prices()
    return float(subscription), R.FEE_SOURCE, sha256_file(ROOT / LEDGER_FILE)


def _declared_writer(*a: Any, **kw: Any) -> Any:
    from extended.results import write_result      # puts the vendored tree on the path: this process only

    return write_result(*a, **kw)


def declared_sources() -> Sources:
    """The declared sources: H4's adapter, Q-197's loader, the ledger's fee through `standard_prices`, `write_result`."""
    return Sources(adapter=_import(R.ADAPTER),
                   calendar_loader=_import("extended.search_calendar:load_search_calendar"),
                   fee=_declared_fee, writer=_declared_writer)


# ------------------------------------------------------------------------------------------------------ the steps
def refuse_if_applied(results_dir: Path) -> None:
    out = results_dir / R.OUTPUT_NAME
    if out.exists() or Path(f"{out}{MANIFEST_SUFFIX}").exists():
        raise _refuse(f"{out.name} exists: W42-R1 is applied once (a second application is refused)")
    other = sorted(p.name for p in results_dir.glob("w42_*"))
    if other:
        raise _refuse(f"a Wave 4.2 output already exists in {results_dir}: {other}")


def read_collection(results_dir: Path) -> tuple[Path, dict[str, Any], str, str, dict[str, Any]]:
    """H4's collection result and its sidecar from disk: (path, sidecar, file sha256, sidecar sha256, binding)."""
    csv_path = results_dir / R.COLLECTION_RESULT
    side = Path(f"{csv_path}{MANIFEST_SUFFIX}")
    if not csv_path.is_file() or not side.is_file():
        raise _refuse(f"H4's collection result {csv_path.name} and its sidecar are both required")
    file_sha = sha256_file(csv_path)
    side_bytes = side.read_bytes()
    side_sha = sidecar_sha256(side_bytes)
    man = json.loads(side_bytes.decode("utf-8"))
    if man.get("sha256") != file_sha:
        raise _refuse(f"{csv_path.name}'s bytes hash to {file_sha[:12]}..., not its sidecar's {str(man.get('sha256'))[:12]}")
    params = dict(man.get("parameters") or {})
    binding = {k: params[k] for k in R.H4_MANIFEST_KEYS if k != "sha256" and k in params}
    binding["sha256"] = man["sha256"]
    return csv_path, man, file_sha, side_sha, binding


def search_calendar(results_dir: Path, loader: Callable[[Path], Any]) -> tuple[tuple[str, ...], str, str]:
    """Q-197's calendar through its loader, bound by its file's pinned sha256: (dates, its digest, its file sha256)."""
    if R.SEARCH_CALENDAR_SHA256 is None:
        raise _refuse("SEARCH_CALENDAR_SHA256 is not pinned yet (Q-197's result, filled before W42-R1's pin)")
    cal = loader(results_dir / R.SEARCH_CALENDAR)
    if cal.file_sha256 != R.SEARCH_CALENDAR_SHA256:
        raise _refuse(f"{R.SEARCH_CALENDAR}'s sha256 {cal.file_sha256[:12]}... is not the pinned one")
    dates = tuple(str(d) for d in cal.dates)
    if R.calendar_digest(dates) != cal.calendar_sha256:
        raise _refuse(f"{R.SEARCH_CALENDAR}: its dates' digest is not the one its loader recorded")
    return dates, cal.calendar_sha256, cal.file_sha256


def held_out_sessions(results_dir: Path) -> tuple[int, str]:
    """The pinned held-out session calendar's session count, its dates only (the rule's held-out ledger entry)."""
    p = results_dir / R.HELD_OUT_CALENDAR
    if not p.is_file():
        raise _refuse(f"the pinned held-out session calendar {p.name} is required")
    raw = p.read_bytes()
    sha = sha256_bytes(raw)
    if sha != R.HELD_OUT_CALENDAR_SHA256:
        raise _refuse(f"{p.name}'s sha256 {sha[:12]}... is not the pinned {R.HELD_OUT_CALENDAR_SHA256[:12]}...")
    rows = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    if "date" not in (rows.fieldnames or []):
        raise _refuse(f"{p.name} has no date column")
    dates = [r["date"] for r in rows]                      # the date column only; nothing else is read
    if not dates or any(not _ISO.fullmatch(d) for d in dates) or dates != sorted(set(dates)) \
            or dates[0] < R.HELD_OUT_FIRST or dates[-1] > R.HELD_OUT_LAST:
        raise _refuse(f"{p.name}'s dates are not strictly increasing inside {R.HELD_OUT_FIRST}..{R.HELD_OUT_LAST}")
    return len(dates), sha


def apply(results_dir: Path | str, sources: Sources) -> dict[str, Any]:
    """The whole application, refusing before any write; returns the written values' parameters."""
    results_dir = Path(results_dir)
    refuse_if_applied(results_dir)
    csv_path, man, file_sha, side_sha, binding = read_collection(results_dir)
    dates, cal_digest, cal_file_sha = search_calendar(results_dir, sources.calendar_loader)
    n_ho, ho_sha = held_out_sessions(results_dir)
    counts = {h: R.complete_starts(n_ho, h) for h in R.HORIZONS}
    fee, fee_source, ledger_sha = sources.fee()
    readings = sources.adapter(csv_path, man)
    values = R.setting_rule(readings, h4=R.H4Binding(file_sha, binding), search_calendar=dates, fee_unit=fee,
                            fee_source=fee_source, test_starts=counts,
                            test_starts_source={"file": R.HELD_OUT_CALENDAR, "sha256": ho_sha, "sessions": n_ho})
    v = values.values
    import pandas as pd

    df = pd.DataFrame({"key": sorted(v),
                       "value_json": [json.dumps(v[k], sort_keys=True, separators=(",", ":"), allow_nan=False)
                                      for k in sorted(v)]})
    params = {"rule_id": R.RULE_ID, "values_sha256": values.digest(), "input_sha256": v["input_sha256"],
              "h4_collection": R.COLLECTION_RESULT, "h4_result_sha256": file_sha, "h4_sidecar_sha256": side_sha,
              "readings_sha256": binding.get("readings_sha256"), "h4_starts": len(binding.get("starts", ())),
              "h4_seeds": len(binding.get("seeds", ())), "search_calendar": R.SEARCH_CALENDAR,
              "search_calendar_file_sha256": cal_file_sha, "search_calendar_sha256": cal_digest,
              "held_out_calendar": R.HELD_OUT_CALENDAR, "held_out_calendar_sha256": ho_sha,
              "held_out_sessions": n_ho, "test_starts": {str(h): c for h, c in counts.items()},
              "fee_unit": fee, "fee_source": fee_source, "fee_via": "extended.levers_terms.standard_prices",
              "ledger_sha256": ledger_sha, "power_target": R.POWER_TARGET,
              "rule_text_sha256": sha256_file(ROOT / RULE_TEXT), "rule_module_sha256": sha256_file(ROOT / RULE_MODULE),
              "script_sha256": sha256_file(ROOT / SCRIPT)}
    sources.writer(df, R.OUTPUT_NAME, script=SCRIPT, seed=None, require_seed=False, parameters=params,
                   results_dir=results_dir,
                   description="W42-R1's values (the limits, the budgets, the weights, delta*), applied once to H4's "
                               "collection result (docs/plans/WAVE42_SETTING_RULE.md)")
    return params


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        raise SystemExit("scripts/wave42_apply.py takes no argument: its inputs are declared names in results/")
    from extended import RESULTS_DIR

    params = apply(RESULTS_DIR, declared_sources())
    print(f"W42-R1 applied: {R.OUTPUT_NAME}, values sha256 {params['values_sha256']}, "
          f"input sha256 {params['input_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
