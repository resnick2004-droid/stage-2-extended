"""IM2's second implementation against the kit (D-193 as amended by D-200): every session of the eight development
windows compared field by field, and every kit entry looked for among the second implementation's signals.

Both implementations read the same QuantConnect bars, so any disagreement is a mismatch (D-200 (3)) and the pass is
zero mismatches (D-200 (4)). The kit's side is its ingested runs R053-R060 (`im2_score.read_run`); the second's is
R063-R070 (`read_second`), written from `docs/verification/im2_second_implementation.md` without the kit's code.

What is compared, per window:

* **The session set**: a date either side exports and the other does not.
* **Per session**: the contract, calendar code, skip reason, settled, complete, lookback depth, the counts of signals,
  of decisions with no bar and of decisions with no band, and the scheduled sessions with no data listed before it,
  exactly; coverage and the open within `TOL` of the larger magnitude (both absent counts as equal); the prior close
  likewise on the sessions the kit evaluates (skip reason empty or `late`). On a skipped session the kit exports no
  prior close and the second implementation the one it carries (`propedge/verification/IM2X_NOTES.md`, case 12), and
  none is used; the skip reason itself is compared.
* **HEAD's trailing list** of scheduled sessions with no data after the last session.
* **Each kit entry**: a signal at its decision time (the kit's slot t is the bar ending at open + t + 1 minutes) with
  the same side, and the decision close, both bands and VWAP within `TOL`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from propedge import REPO_ROOT, RESULTS_DIR
from propedge.data.qc_algorithms import IM2_RUNS, IM2X_RUNS, im2_params
from propedge.research import im2_score as sc

#: D-200: relative tolerance for prices; the kit prints ten significant digits, the second implementation twelve
TOL = 5e-9
EXACT = ("sym", "cal", "sk", "st", "full", "np", "signals", "missing", "no_band", "gone")
CLOSE = ("cov", "ref", "pc")
EVALUATED = ("", "late")                         # the skip reasons of a session whose decisions are evaluated
LEVELS = ("cl", "ub", "lb", "vw")


def _absent(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def close(a: float, b: float, tol: float = TOL) -> bool:
    """Equal within `tol` of the larger magnitude; two absent values are equal, one absent is not."""
    if _absent(a) or _absent(b):
        return _absent(a) and _absent(b)
    return abs(float(a) - float(b)) <= tol * max(abs(float(a)), abs(float(b)))


def read_second(run_id: str, results_dir: Path | None = None, runs_dir: Path | None = None
                ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """One ingested run of the second implementation: (sessions, signals, the scheduled sessions HEAD lists after the
    last one)."""
    from propedge.reporting.results import verify_result

    path = Path(results_dir or RESULTS_DIR) / f"manual_{run_id.replace('-', '_')}.csv"
    ok, msg = verify_result(path)
    if not ok:
        raise ValueError(msg)
    df = pd.read_csv(path, dtype={c: str for c in ("d", "sk", "cal", "gone", "sym")})
    for c in ("d", "sk", "cal", "gone", "sym"):
        df[c] = df[c].fillna("").astype(str)
    ing = Path(runs_dir or REPO_ROOT / "runs") / run_id / "ingested.json"
    tail = str((json.loads(ing.read_text(encoding="utf-8")).get("summary") or {}).get("gone") or "") \
        if ing.exists() else ""
    return (df[df["kind"] == "day"].reset_index(drop=True), df[df["kind"] == "signal"].reset_index(drop=True),
            [x for x in tail.split(",") if x])


def _norm(x):
    """A field as compared exactly: integers as ints, text as text, absent as ''."""
    if _absent(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def compare_window(market: str, kit: tuple[pd.DataFrame, pd.DataFrame, list[str]],
                   second: tuple[pd.DataFrame, pd.DataFrame, list[str]]) -> tuple[dict, list[dict]]:
    """(summary, mismatches) for one market and window. `kit` is `im2_score.read_run`'s triple, `second` is
    `read_second`'s. Each mismatch is {'d', 'check', 'kit', 'second'}."""
    kd, ke, kt = kit
    xd, xs, xt = second
    open_min = im2_params(market)["open_min"]
    out: list[dict] = []

    def miss(d, check, a, b):
        out.append({"d": d, "check": check, "kit": "" if a is None else str(a), "second": "" if b is None else str(b)})

    kdays = {r["d"]: r for r in kd.to_dict("records")}
    xdays = {r["d"]: r for r in xd.to_dict("records")}
    for d in sorted(set(kdays) - set(xdays)):
        miss(d, "session only in the kit", d, None)
    for d in sorted(set(xdays) - set(kdays)):
        miss(d, "session only in the second", None, d)
    common = sorted(set(kdays) & set(xdays))
    for d in common:
        a, b = kdays[d], xdays[d]
        for f in EXACT:
            if _norm(a[f]) != _norm(b[f]):
                miss(d, f, a[f], b[f])
        for f in CLOSE:
            if f == "pc" and _norm(a["sk"]) not in EVALUATED:
                continue
            if not close(a[f], b[f], TOL if f != "cov" else 1e-9):
                miss(d, f, a[f], b[f])
    if list(kt) != list(xt):
        miss("", "HEAD gone", ",".join(kt), ",".join(xt))

    sig = {(r["d"], int(r["tm"])): r for r in xs.to_dict("records")}
    found = 0
    for e in ke.to_dict("records"):
        tm = open_min + int(e["t"]) + 1
        s = sig.get((e["d"], tm))
        where = f"{e['d']} {tm // 60:02d}:{tm % 60:02d}"
        if s is None:
            miss(e["d"], "entry not among the signals", where, None)
            continue
        ok = True
        if int(s["side"]) != int(e["side"]):
            miss(e["d"], "entry side", f"{where} {int(e['side']):+d}", f"{int(s['side']):+d}")
            ok = False
        for f in LEVELS:
            if not close(float(e[f]), float(s[f])):
                miss(e["d"], f"entry {f}", f"{where} {e[f]!r}", repr(s[f]))
                ok = False
        found += ok
    summary = {"market": market, "sessions_kit": len(kdays), "sessions_second": len(xdays),
               "sessions_compared": len(common), "signals_kit": int(kd["signals"].sum()),
               "signals_second": int(xd["signals"].sum()), "kit_entries": len(ke), "entries_matched": found,
               "mismatches": len(out)}
    return summary, out


def compare_all(results_dir: Path | None = None, runs_dir: Path | None = None,
                runs: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """(one summary row per window with an ingested second run, every mismatch, the windows not yet ingested)."""
    rows, mism, missing = [], [], []
    for key, xid in sorted((runs or IM2X_RUNS).items()):
        market, window = key
        path = Path(results_dir or RESULTS_DIR) / f"manual_{xid.replace('-', '_')}.csv"
        if not path.is_file():
            missing.append(xid)
            continue
        kid = IM2_RUNS[key]
        summary, out = compare_window(market, sc.read_run(kid, results_dir, runs_dir),
                                      read_second(xid, results_dir, runs_dir))
        rows.append({"window": window, "kit_run": kid, "second_run": xid, **summary})
        mism += [{"market": market, "window": window, **m} for m in out]
    cols = ["market", "window", "d", "check", "kit", "second"]
    return pd.DataFrame(rows), pd.DataFrame(mism, columns=cols), missing


__all__ = ["TOL", "close", "read_second", "compare_window", "compare_all"]
