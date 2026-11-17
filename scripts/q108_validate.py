"""Q-108 (E-115): the validation of the statistic the calibration chose -- one heavy run, on the validation seeds only,
from the pinned plan `docs/calibration/Q-108_one_sample_plan.md` (its 4.3 and 6.3). Nothing is re-chosen.

    python scripts/run_clean.py --name q108-validate --task Q-108 --hours <from the build's measurement> --mem-gb 1.5 -- python scripts/q108_validate.py

**When:** only after a decision row records the choice. The row is found in `DECISIONS.md` as a row naming both
calibration files by path and sha256, in the form

    `results/q108_choice.csv` sha256 `<64 hex>` ... `results/q108_sn_table.csv` sha256 `<64 hex>`

(the choice file the validation reads, and C8's reference, which the choosing row pins: the plan's 2.2). Until such a
row exists, and the two files match it and their manifests, the run refuses.

**What it computes:** the same 2,293 nulls (and 84 beside) as the calibration -- `scripts/q108_calibrate.py`'s null
plan, generators, re-decision and exact enumeration, imported -- on the validation block's seeds, for the chosen
statistic (in scope D, the chosen procedure) and C0 beside, both scopes. A scalar re-decision disagreement stops the
run with no verdict (E-115 (R1)).

**The criterion (the plan's 4.3, fixed before either run):** the chosen statistic HOLDS if, at every k in 13..20, on
every one of the 2,293 validation nulls, a Monte Carlo null's 95 % Clopper-Pearson interval (recomputed from its
counts) does not lie wholly above nominal, and an exact null's exact size is at or below nominal (on the alternating
models: no configuration rejects, the same thing at their granularity); it FAILS if any null breaks either; it is NOT
CHECKED -- never a pass -- if any null is missing. It prints `criterion (Q-108) <name> (scope <s>): HOLDS | FAILS |
NOT CHECKED`. Beside, never in the verdict: C0 on the same draws, the count-persistent nulls, the `flat` form, the
power on the validation toys.

**Writes** (`extended.results.write_result`; only inside a clean run): `q108_val_size.csv`, `q108_val_power.csv`,
`q108_val_criterion.csv`.

**Refusals (exit 3, before any step):** outside a clean run; a result file that exists; no choosing row, or the
calibration's files not matching it or their manifests, or not written by a clean run of the calibration; the choice
NONE (the validation block is then retired, never drawn: the plan's 7 item 1); `lift_one_sample.py` other than the
blob the calibration ran; `lift_bound.py` or the plan other than their pins; a seed map other than the validation
block's; either block named or derived outside the allow-list (the calibration's guard). **A failed check (exit 5):**
a scalar disagreement, a nesting violation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import CLEAN_RUN_ENV, RESULTS_DIR, RUNS_DIR  # noqa: E402
from extended import lift_bound as LB  # noqa: E402
from extended import lift_one_sample as O  # noqa: E402


def _load_calibrate():
    name = "q108_calibrate_for_validate"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "q108_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


#: the calibration runner, imported (its null plan, generators, re-decision, exact enumeration and guard)
CAL = _load_calibrate()

SCRIPT = "scripts/q108_validate.py"
DECISION = CAL.DECISION
RUN_CMD = ("python scripts/run_clean.py --name q108-validate --task Q-108 --hours <measured> --mem-gb 1.5 -- "
           "python scripts/q108_validate.py")

# ---- the validation seed map (the plan's 4.1) ----
SEEDS = {
    "tests": 20262120,           # the validation build's tests
    "fixed_mc": 20262121,        # as the calibration's fixed_mc
    "subsets": 20262122,         # as the calibration's subsets
    "subset_mc": 20262123,       # as the calibration's subset_mc
    "synthetic": 20262124,       # as the calibration's synthetic
    "beside_cp": 20262125,       # the count-persistent nulls beside
    "beside_flat": 20262126,     # the `flat` form beside
    "exact_sample": 20262127,    # as the calibration's exact_sample
}
SPARE = (20262128, 20262129)
# ---- end of the validation seed map ----

VAL_ROLES = CAL.DRAW_ROLES
RESULT_FILES = ("q108_val_size", "q108_val_power", "q108_val_criterion")
CHOICE_FILE = "results/q108_choice.csv"
SN_FILE = "results/q108_sn_table.csv"
CHOICE_PIN = re.compile(r"`results/q108_choice\.csv` sha256 `([0-9a-f]{64})`")
SN_PIN = re.compile(r"`results/q108_sn_table\.csv` sha256 `([0-9a-f]{64})`")
ROW = re.compile(r"^\|\s*(E-\d+)\s*\|", re.MULTILINE)
REFUSED, FAILED_CHECK = CAL.REFUSED, CAL.FAILED_CHECK
VERDICTS = ("HOLDS", "FAILS", "NOT CHECKED")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


# ================================================================================================ the choosing row


def choosing_row(decisions_text: str) -> tuple[str | None, str | None, str | None]:
    """(row id, the choice file's pinned sha256, the reference table's) of the last decision row naming both."""
    found = (None, None, None)
    for line in decisions_text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        c, s = CHOICE_PIN.search(line), SN_PIN.search(line)
        if c and s:
            found = (m.group(1), c.group(1), s.group(1))
    return found


def _sha(p: Path) -> str:
    import hashlib

    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def choice_problems(repo: Path = ROOT) -> tuple[list[str], dict]:
    """The choosing row and the calibration's files: (problems, what was read)."""
    from extended import results as XR

    repo = Path(repo)
    probs = []
    dec = (repo / "DECISIONS.md").read_text(encoding="utf-8") if (repo / "DECISIONS.md").is_file() else ""
    row, pin_c, pin_s = choosing_row(dec)
    if row is None:
        return [f"no decision row records the choice: the validation runs only after a row naming `{CHOICE_FILE}` "
                f"sha256 and `{SN_FILE}` sha256 (the plan's 6.3)"], {}
    info = {"row": row}
    for rel, pin in ((CHOICE_FILE, pin_c), (SN_FILE, pin_s)):
        p = repo / rel
        if not p.is_file():
            probs.append(f"{rel} is not in this tree")
            continue
        ok, msg = XR._vendored.verify_result(p)
        if not ok:
            probs.append(f"{rel}: {msg}")
            continue
        man = json.loads(Path(str(p) + XR.MANIFEST_SUFFIX).read_text(encoding="utf-8"))
        if man.get("script") != CAL.SCRIPT:
            probs.append(f"{rel} was written by {man.get('script')!r}, not {CAL.SCRIPT}")
        if not (man.get("provenance") or {}).get("clean_run"):
            probs.append(f"{rel} was not written inside a clean run")
        if man.get("exploratory"):
            probs.append(f"{rel} is marked exploratory")
        if _sha(p) != pin:
            probs.append(f"{rel} does not hash to {row}'s pin")
        info[rel] = man
    if probs:
        return probs, info
    ch = pd.read_csv(repo / CHOICE_FILE, low_memory=False)
    d = ch[ch["row"] == "decision"]
    if len(d) != 1:
        return [f"{CHOICE_FILE} holds {len(d)} decision rows, not one"], info
    line = str(d["decision"].iloc[0])
    info["decision"] = line
    if line == "NONE":
        return ["the calibration chose NONE: the validation block is retired, never drawn (the plan's 7 item 1)"], info
    m = re.fullmatch(r"CHOSEN (\S+) \(scope ([QD])\)", line)
    if not m or m.group(1) not in O.NAMES:
        return [f"{CHOICE_FILE}'s decision {line!r} is not a choice the plan allows"], info
    info["chosen"], info["scope"] = m.group(1), m.group(2)
    want = (info[CHOICE_FILE].get("parameters") or {}).get("blobs", {}).get(CAL.MODULE)
    got = CAL.blob_id(repo / CAL.MODULE)
    if want != got:
        probs.append(f"{CAL.MODULE} is blob {got[:12]}, not the {str(want)[:12]} the calibration ran (the chosen "
                     "statistic is that code)")
    return probs, info


# ================================================================================================ the criterion


def criterion(size: pd.DataFrame, chosen: str, scope: str, want: dict | None = None) -> pd.DataFrame:
    """The plan's 4.3 on the chosen statistic in its scope, per k and over k = 13..20 (row k = "13-20"): a Monte Carlo
    null fails at k when its 95 % Clopper-Pearson interval lies wholly above nominal; an exact null when its exact size
    is above nominal. NOT CHECKED when any of the rule's nulls is missing."""
    want = CAL.EXPECTED if want is None else want
    d = size[(size["candidate"] == chosen) & (size["scope"] == scope)
             & size["in_rule"].astype(str).str.lower().isin(["true", "1"]) & (size.get("row", "null") != "spread")]
    nulls = d["null"].nunique()
    complete = nulls == want["rule"] and len(d) == nulls
    rows = []
    for lab, k in zip(CAL.FAM_LABELS, O.K_RANGE_1S):
        a = LB.family_level(k)
        fa = O.level_fraction(a)
        bad = []
        worst, worst_null = -1.0, None
        for _, r in d.iterrows():
            den, x = int(r["denominator"]), int(r[f"count_{lab}"])
            if r["kind"] == "mc":
                lo, _ = LB.clopper_pearson(x, den)
                fails = lo > a
                if den == CAL.REPS and fails != (x >= CAL.FAIL[k]):
                    raise AssertionError("the interval and the failure count disagree")
            else:
                fails = Fraction(x, den) > fa
            if fails:
                bad.append(str(r["null"]))
            ratio = (x / den) / a
            if ratio > worst:
                worst, worst_null = ratio, r["null"]
        verdict = "NOT CHECKED" if not complete else ("FAILS" if bad else "HOLDS")
        rows.append({"section": "criterion", "candidate": chosen, "scope": scope, "k": k, "level": a,
                     "expected_nulls": want["rule"], "nulls": nulls, "nulls_failing": len(bad),
                     "failing_nulls": ";".join(bad[:50]), "worst_ratio": worst, "worst_null": worst_null,
                     "verdict": verdict})
    vs = [r["verdict"] for r in rows]
    overall = "FAILS" if "FAILS" in vs else ("NOT CHECKED" if "NOT CHECKED" in vs else "HOLDS")
    rows.append({"section": "criterion", "candidate": chosen, "scope": scope, "k": "13-20", "level": math.nan,
                 "expected_nulls": want["rule"], "nulls": nulls, "nulls_failing": sum(r["nulls_failing"] for r in rows),
                 "failing_nulls": ";".join(f"k{r['k']}:{r['failing_nulls']}" for r in rows if r["failing_nulls"]),
                 "worst_ratio": max(r["worst_ratio"] for r in rows), "worst_null": None, "verdict": overall})
    return pd.DataFrame(rows)


def beside(size: pd.DataFrame, cands) -> pd.DataFrame:
    """Beside, no verdict: per candidate, scope, group and k, how many nulls sit above nominal (by the criterion's
    tests) and the largest ratio."""
    out = []
    d = size[size.get("row", "null") != "spread"] if "row" in size else size
    for c in cands:
        for s_ in CAL.SCOPES:
            for grp in ("fixed", "subset", "synthetic", "beside_cp", "beside_flat"):
                g = d[(d["candidate"] == c) & (d["scope"] == s_) & (d["group"] == grp)]
                if g.empty:
                    continue
                for lab, k in zip(CAL.FAM_LABELS, O.K_RANGE_1S):
                    a = LB.family_level(k)
                    above = 0
                    for _, r in g.iterrows():
                        den, x = int(r["denominator"]), int(r[f"count_{lab}"])
                        above += int(LB.clopper_pearson(x, den)[0] > a) if r["kind"] == "mc" \
                            else int(Fraction(x, den) > O.level_fraction(a))
                    out.append({"section": "beside", "candidate": c, "scope": s_, "group": grp, "k": k, "level": a,
                                "nulls": int(g["null"].nunique()), "nulls_above": above,
                                "worst_ratio": float(g[f"ratio_{lab}"].astype(float).max()),
                                "verdict": "beside: not the criterion"})
    return pd.DataFrame(out)


def validate_tables(parts_out: list[dict], chosen: str, scope: str, cands, want: dict | None = None) -> dict:
    """From the parts' outputs: the checks (R1, nesting), then the criterion and the beside tables. Writes nothing."""
    size = pd.DataFrame([r for p in parts_out for r in p["size"]])
    power = pd.DataFrame([r for p in parts_out for r in p["power"]])
    mism = [m for p in parts_out for m in p["mismatches"]]
    nest = [x for p in parts_out for x in p["meta"]["nesting_violations"]]
    failed = []
    if mism:
        failed.append(f"the scalar re-decision DIFFERS in {len(mism)} decisions (E-115 (R1)): first {mism[0]}")
    if nest:
        failed.append(f"the nesting assertion fails on {len(nest)}: first {nest[0]}")
    out = {"size": size, "power": power, "mismatches": mism, "failed": failed}
    if failed:
        return out
    crit = criterion(size, chosen, scope, want)
    out.update({"criterion": crit, "beside": beside(size, cands),
                "verdict": str(crit[crit["k"].astype(str) == "13-20"]["verdict"].iloc[0]),
                "size_out": pd.concat([size, pd.DataFrame(CAL.spread_rows(size))], ignore_index=True, sort=False)
                if len(size) else size})
    return out


# ================================================================================================ the commands


def preflight(target: Path, repo: Path = ROOT) -> tuple[list[str], dict]:
    """The refusals before any step, in order."""
    from extended import results as XR

    bad = XR.clean_run_problem()
    if bad:
        return [f"this process is not a clean run -- {bad}. Run it as: {RUN_CMD}"], {}
    clash = [x for x in RESULT_FILES if (target / f"{x}.csv").exists() or (target / f"{x}.csv.manifest.json").exists()]
    if clash:
        return [f"{clash} exist in {target}; a result file is never overwritten"], {}
    probs, info = choice_problems(repo)
    if probs:
        return probs, info
    probs = CAL.pin_problems() + CAL.seed_map_problems(SEEDS, CAL.VAL_BLOCK, VAL_ROLES + ("tests",))
    return probs, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--compute", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--work", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--calendar", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--pairs-file", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--sn-table", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--candidates", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--reps", type=int, default=CAL.REPS, help=argparse.SUPPRESS)
    ap.add_argument("--reps-beside", type=int, default=CAL.REPS_BESIDE, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    from extended import results as XR

    if a.compute is not None:
        if XR.clean_run_problem() or a.compute == "sn":
            print("REFUSED: a part runs only inside the clean run that started it, and the validation draws no "
                  "reference table", flush=True)
            return REFUSED
        return CAL.compute_main(a, SCRIPT, SEEDS)
    t0 = time.time()
    target = RESULTS_DIR
    probs, info = preflight(target)
    if probs:
        print("REFUSED: " + "; ".join(probs), flush=True)
        return REFUSED
    chosen, scope = info["chosen"], info["scope"]
    cands = [chosen] + (["cons"] if chosen != "cons" else [])
    seed_probs, seed_notes = CAL.seed_block_problems(ROOT)
    for x in seed_notes:
        _log(f"seed blocks: {x}")
    if seed_probs:
        print("REFUSED: the plan's seed blocks are not unused -- " + "; ".join(seed_probs[:10]), flush=True)
        return REFUSED
    _log(f"the choice ({info['row']}): {info['decision']}; validating {chosen} in scope {scope}, C0 beside; "
         f"seed map {SEEDS}")
    name = os.environ.get(CLEAN_RUN_ENV)
    work = Path(RUNS_DIR) / f"{name}.work" if name else Path(tempfile.mkdtemp(prefix="q108v_"))
    work.mkdir(parents=True, exist_ok=True)
    if not CAL._outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return REFUSED
    cal, cal_sha, cal_src = CAL.read_calendar()
    bad = CAL.calendar_problems(cal, cal_sha)
    if bad:
        print("REFUSED: " + "; ".join(bad), flush=True)
        return REFUSED
    calf = work / "judged_sessions.csv"
    pd.DataFrame({"date": cal}).to_csv(calf, index=False)
    pairs = work / "pairs"
    if CAL._step("pairs", ["scripts/q16_p16_pairs.py", "--out", str(pairs)]):
        return 1
    pq = pairs / "p16_pairs.parquet"
    pairs_meta = json.loads((pairs / "p16_pairs.json").read_text(encoding="utf-8"))
    snf = ROOT / SN_FILE
    rc_all = {}
    for part in CAL.PARTS:
        rc = CAL._step(part, [SCRIPT, "--compute", part, "--work", str(work), "--calendar", str(calf),
                              "--pairs-file", str(pq), "--sn-table", str(snf), "--candidates", ",".join(cands)])
        rc_all[part] = rc
        if rc == FAILED_CHECK:
            break
        if rc:
            return 1
    outs = [CAL.read_part(work, p) for p in CAL.PARTS if (work / p / "meta.json").is_file()]
    res = validate_tables(outs, chosen, scope, cands)
    if res["failed"] or any(v == FAILED_CHECK for v in rc_all.values()):
        for f in res["failed"] or ["a part stopped on a failed check"]:
            print(f"FAILED CHECK: {f}", flush=True)
        print("FAILED CHECK: no verdict is accepted and no result is written; the record is in " + str(work),
              flush=True)
        print(f"EXIT {FAILED_CHECK}", flush=True)
        return FAILED_CHECK
    _log(f"read ledger: {XR.note_ledger_appends()}")
    blobs = {rel: CAL.blob_id(ROOT / rel) for rel in ("extended/lift_bound.py", CAL.MODULE, CAL.SCRIPT, SCRIPT,
                                                      "scripts/q16_calibrate.py", "scripts/q82_validation.py")}
    common = {"decision": DECISION, "plan": CAL.PLAN, "plan_sha256": CAL.PLAN_SHA256, "task": "Q-108",
              "choosing_row": info["row"], "choice": info["decision"], "chosen": chosen, "scope": scope,
              "choice_sha256": _sha(ROOT / CHOICE_FILE), "sn_table_sha256": _sha(snf),
              "candidates": cands, "reps": CAL.REPS, "reps_beside": CAL.REPS_BESIDE, "n_sessions": len(cal),
              "calendar_sha256": cal_sha, "calendar_source": cal_src, "pairs_sha256": pairs_meta.get("parquet_sha256"),
              "blobs": blobs, "seed_map": {k: int(v) for k, v in SEEDS.items()}, "spare_seeds": list(SPARE),
              "seed_block": list(CAL.VAL_BLOCK), "versions": CAL._versions(),
              "scalar_redecision": {"checked": sum(m["meta"]["scalar_checked"] for m in outs), "mismatched": 0},
              "criterion": "the plan's 4.3: at every k in 13..20, on every one of the 2,293 nulls, no Monte Carlo "
                           "null's 95 % interval wholly above nominal and no exact size above nominal"}
    crit_all = pd.concat([res["criterion"], res["beside"]], ignore_index=True, sort=False)
    out = {"q108_val_size": (res["size_out"], SEEDS["fixed_mc"], CAL.DRAW_ROLES,
                             "Q-108 (E-115): the validation's nulls x the chosen statistic and C0 x scope x level"),
           "q108_val_power": (res["power"], SEEDS["subset_mc"], ("subsets", "subset_mc", "synthetic"),
                              "Q-108 (E-115): the validation toys' MDLs, beside"),
           "q108_val_criterion": (crit_all, None, (),
                                  f"Q-108 (E-115): the plan's 4.3 on {chosen} (scope {scope}) -- {res['verdict']}; "
                                  "computed from the size table beside, no randomness of its own")}
    for nm, (df, seed, roles, desc) in out.items():
        params = {**common, "seeds": {r: int(SEEDS[r]) for r in roles}}
        csv, man = XR.write_result(df, nm, script=SCRIPT, seed=seed, parameters=params, description=desc,
                                   exploratory=False, require_seed=seed is not None)
        _log(f"wrote {csv} ({len(df)} rows) and {man.name}")
    print(f"criterion (Q-108) {chosen} (scope {scope}): {res['verdict']}", flush=True)
    _log(f"EXIT 0 ({time.time() - t0:.0f} s)")
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
