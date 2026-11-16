"""RD-02's reading (`prereg/RD-02_payout_policy.md`, pinned under E-082; section 14): payout policy in a user's first
months, described, never carried -- the 11 runs on both arms, the 32 replays and 8 gates beside, from a clean checkout,
its reads authorised under the declaration's three purposes, after its identities.

    python scripts/run_clean.py --name pp-reading --commit <the run's commit> --task Q-105 --hours 8 --mem-gb 2.5 \\
        -- python scripts/pp_reading.py --workers 2
    python scripts/pp_reading.py --synthetic --results-dir <a temporary folder>    # the pipeline on a synthetic toy

**Refusing, before any of the engine's work** (exit 3, nothing written, nothing ledgered):

* outside a clean run (`extended.results.clean_run_problem`), in the real mode;
* **section 14's waits (the third read's D1; the lead's ruling E-104)**: unless, for each waited identity (`WAITS`:
  RD-02's own identity `pp_identity`, Q-80, Q-93, Q-101 and the two-worker check `t10w2`), a row of `DECISIONS.md`
  records it holding, by position -- the row beginning `| E-NNN | YYYY-MM-DD | identity-holds: <id> @ <sha> -- <text> |`,
  no backticks, `<sha>` the 40-hex commit it held at -- at a commit that is this run's HEAD or an ancestor of it, with
  none of the files that identity covers (the code it certifies, `WAITS`) changed since (`held`). A string of that shape
  anywhere else in a row is never a token. The rows met are named in every manifest (r4). `--workers` above 2 is
  refused, and 2 only once `t10w2` is met (r5);
* unless Q-44's per-start file is on the tree and verifies (8.1 item 6), and the inputs' preflight holds (Q-44's file
  read as text with its columns and rows; each design's registered gate row, one a shift);
* **E-015's limits (D5)**: read only from the rows recording the operator's approval
  (`| E-NNN | YYYY-MM-DD | e015-limits: <COLUMN> max|min <BOUND>; ... -- <text> |`, `pp_run.limit_rows`), each column one
  of the menu's (`pp_run.limit_columns`); a malformed limits row refuses. No bound is typed on the command line; with no
  such row the menu is read without flags;
* unless the adapter's files are the commit's (their blob ids are recorded, Q-102's m7);
* unless the reads are authorised under each of `payout_scorecard`, `payout_ladder_beside` and `payout_gate_beside`
  with the declaration -- **all three checked first by `reader.authorise` (which reads and writes nothing) and the
  engine's files found, before any is ledgered by `reader.authorise_engine_read`** (n1); once each; a further run only
  with `--repeat E-NNN`, a row naming the file (E-053).

**Then** `extended.pp_run.run_reading` (its order and checks: that module's docstring); any failed check refuses and
writes nothing. **Written** through `extended.results.write_result`, each with its manifest: `pp_reading.csv` (sections
identity, oracle, mechanics, scorecard, paired, diverge, coverage and beside, each row's `part` within it),
`pp_gate.csv` (the gate rows, the pairing with the base's registered paths, the gate's reading and divergences, the held
counts) and `pp_menu.csv` (the menu) -- `prereg_id` RD-02, the pinning row, the waited rows and their commits, the run
counts, every seed with the retired ones, the parameters and section 4's assumptions, the class, the adapter's commit
and blob ids, the data manifest's and the calendars' sha256, the E-015 limits and their rows, `exploratory=False`,
every cell "described, not carried".
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import reader, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

SCRIPT = "scripts/pp_reading.py"
VENDOR = ROOT / "vendor" / "stage2"
RESULTS = ("pp_reading", "pp_gate", "pp_menu")
MAX_WORKERS = 2
#: D1 (E-104): a row recording that an identity holds, by position -- its id, its date, then the text column beginning
#: with the prefix, the identity's id (a queue id or a lowercase label), " @ ", the 40-hex commit it held at, " -- "
#: and the row's own words
TOKEN_PREFIX = "identity-holds:"
TOKEN_ROW = re.compile(r"^\| (E-\d+) \| (\d{4}-\d{2}-\d{2}) \| " + re.escape(TOKEN_PREFIX)
                       + r" (Q-\d+[a-z]?|[a-z][a-z0-9_]*) @ ([0-9a-f]{40}) -- \S")
VENDOR_PINS = ("vendor/MANIFEST_stage2.sha256", "vendor/DATA_MANIFEST_stage2.sha256")
#: section 14's waits: each waited identity, what it certifies, and the files it covers -- the code it certifies, so a
#: wait is met only at a commit with none of them changed since (D1)
WAITS: dict[str, tuple[str, tuple[str, ...]]] = {
    "pp_identity": ("RD-02's own identity (8.1 items 1 to 3, item 4 on its paths and starts, item 6 at ref): the "
                    "reference policy through the whole adapter and RealInputs, the reading's step 1",
                    ("extended/pp_inputs.py", "extended/payout_policy.py", "extended/user_beside.py", "extended/gate.py",
                     "extended/campaign.py", "extended/user_readings.py", "extended/user_measures.py",
                     "extended/results.py", "identity/user_beside_identity.py", "identity/stage2_identity.py",
                     *VENDOR_PINS)),
    "Q-80": ("the gate through its re-composed campaign, 500 paths, every arm (E-049)",
             ("extended/gate.py", "extended/campaign.py", *VENDOR_PINS)),
    "Q-93": ("U1's start rows through run_starts with a declared class, every start (E-059 (1))",
             ("extended/user_beside.py", "extended/user_measures.py", *VENDOR_PINS)),
    "Q-101": ("U1's start rows with the replay recorder on, every start (E-068)",
              ("extended/replay_records.py", "extended/place_records.py", "extended/place_fields.py",
               "extended/openings.py", "extended/user_beside.py", "extended/user_measures.py", *VENDOR_PINS)),
    "t10w2": ("T-10 at two workers: the counters' channel on the replay and the table-bearing gate (13.1 item 1)",
              ("extended/payout_policy.py", "extended/user_beside.py", "extended/gate.py", "extended/campaign.py",
               *VENDOR_PINS)),
}


def _git(repo: Path | str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def tokens(text: str) -> list[dict[str, str]]:
    """Every positional identity token of `text` (DECISIONS.md): {row, date, id, sha}, in the file's order."""
    out = []
    for line in text.splitlines():
        m = TOKEN_ROW.match(line)
        if m:
            out.append({"row": m.group(1), "date": m.group(2), "id": m.group(3), "sha": m.group(4)})
    return out


def held(text: str, ident: str, repo: Path | str, head: str, covered: Sequence[str]) -> list[str]:
    """D1, in the shared parser's form (Q-110's `extended/identity_tokens.held` replaces this when it reaches master):
    the ids of the rows of `text` whose positional token records `ident` holding at a commit that is `head` or an
    ancestor of it in `repo`, with none of the `covered` paths changed between that commit and `head`. Empty when the
    wait is not met; an unknown commit is not met."""
    if not covered:
        raise ValueError(f"{ident}: a wait covers at least one file")
    out = []
    for t in tokens(text):
        if t["id"] != ident:
            continue
        if _git(repo, "merge-base", "--is-ancestor", t["sha"], head).returncode != 0:
            continue
        if _git(repo, "diff", "--quiet", t["sha"], head, "--", *covered).returncode != 0:
            continue
        out.append(t["row"])
    return out


def wait_rows(text: str, repo: Path | str, head: str, waits: dict | None = None) -> dict[str, list[str]]:
    """{waited identity: the rows meeting its wait at `head`} (`waits`: `WAITS`, or a test's)."""
    return {k: held(text, k, repo, head, cov) for k, (_, cov) in (WAITS if waits is None else waits).items()}


def wait_problems(text: str, workers: int, repo: Path | str, head: str, waits: dict | None = None) -> list[str]:
    """Section 14's waits (D1, r5): each met at `head`, every covered file present there; one or two workers, two only
    once `t10w2` is met (`waits`: `WAITS`, or a test's)."""
    waits = WAITS if waits is None else waits
    out = []
    for k, (_, cov) in waits.items():
        absent = [f for f in cov if _git(repo, "cat-file", "-e", f"{head}:{f}").returncode != 0]
        if absent:
            out.append(f"the wait for {k}: its covered files {absent} are not in {head[:12]}")
    got = wait_rows(text, repo, head, waits)
    for k, (what, _) in waits.items():
        if got.get(k):
            continue
        stale = [t["row"] for t in tokens(text) if t["id"] == k]
        out.append(f"the wait for {k} ({what}) is not met at {head[:12]}" +
                   (f": rows {stale} record it at a commit that is not this run's or its ancestor, or since which its "
                    "covered files changed" if stale else ": no row records it holding"))
    if int(workers) < 1 or int(workers) > MAX_WORKERS:
        out.append(f"--workers {workers}: one or {MAX_WORKERS} only (the machine's rule)")
    if int(workers) > 1 and not got.get("t10w2"):
        out.append(f"--workers {workers}: two workers need T-10 held at two workers (the wait for t10w2, r5)")
    return out


def authorise_all(purposes: Sequence[str], *, files: Sequence[Path], declaration: str, repeat: str | None, what: str,
                  check: Callable[..., Any] | None = None, ledger: Callable[..., Any] | None = None) -> list[Any]:
    """n1: every purpose checked by `reader.authorise` (reads nothing, writes nothing) and every file found before any
    purpose is ledgered by `reader.authorise_engine_read`; a refusal leaves nothing ledgered."""
    check = reader.authorise if check is None else check
    ledger = reader.authorise_engine_read if ledger is None else ledger
    for purpose in purposes:
        check(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=declaration, repeat=repeat,
              what=f"{what}: {purpose}")
    absent = [str(f) for f in files if not Path(f).is_file()]
    if absent:
        raise FileNotFoundError(f"{what}: {absent[:3]} do not exist")
    return [ledger(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=declaration, repeat=repeat,
                   files=files, what=f"{what}: {purpose}") for purpose in purposes]


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repeat", default=None, help="a further run's row (E-NNN) naming the declaration (E-053)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--synthetic", action="store_true", help="the pipeline on a synthetic toy into --results-dir")
    ap.add_argument("--results-dir", default=None, help="with --synthetic: where the three files go")
    ap.add_argument("--plant", choices=("identity", "ladder"), default=None, help="with --synthetic: a failing check")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    import stage2_identity as SI

    from extended import payout_policy as PP
    from extended import pp_run as RUN
    from extended import results as XR

    t0 = time.time()
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    waits: dict[str, list[str]] = {}
    limit_rows_used: list[str] = []
    head = _git(ROOT, "rev-parse", "HEAD").stdout.strip()
    if a.synthetic:
        if not a.results_dir:
            print("REFUSED (RD-02): --synthetic writes to --results-dir only")
            return 2
        if XR.protected(a.results_dir):
            print("REFUSED (RD-02): --synthetic never writes to a results/ folder of this repository")
            return 3
        from extended import pp_run_synthetic as SYN

        inputs, designs, starts, reps = SYN.SyntheticInputs(plant=a.plant, n_paths=3), SYN.DESIGNS, SYN.STARTS, 20
        sens, window, target = SYN.DESIGNS[0], ("08:30", "15:10"), Path(a.results_dir)
        limits: list = []
    else:
        if a.results_dir or a.plant:
            print("REFUSED (RD-02): --results-dir and --plant are the synthetic run's only")
            return 2
        prob = XR.clean_run_problem()
        if prob:
            print(f"REFUSED (RD-02, section 14): the reading runs only from a clean checkout -- {prob}")
            print("EXIT 3", flush=True)
            return 3
        probs = wait_problems(text, a.workers, ROOT, head)
        waits = wait_rows(text, ROOT, head)
        limits, limit_rows_used, lp = RUN.limit_rows(text)        # D5: from the operator's approving rows only
        probs += lp
        q44 = ROOT / "results" / "user_beside_starts.csv"
        ok, msg = XR.verify_result(q44) if q44.is_file() else (False, "absent")
        if not ok:
            probs.append(f"Q-44's per-start file (8.1 item 6): {msg}")
        inputs, designs, starts, reps = RUN.RealInputs(), RUN.DESIGNS, None, None
        if not probs:
            probs += inputs.preflight(designs)
        if probs:
            print("REFUSED (RD-02, 8.1 and section 14's waits): " + "; ".join(probs))
            print("EXIT 3", flush=True)
            return 3
        try:
            RUN.adapter_provenance(ROOT, strict=True)
            authorise_all(RUN.PURPOSES, files=SI.engine_files(VENDOR, bars=True), declaration=RUN.DECLARATION,
                          repeat=a.repeat, what=f"RD-02's reading ({SCRIPT})")
        except (reader.ReadRefused, FileNotFoundError, ValueError, RUN.Refused) as exc:
            print(SI.refusal(exc) if isinstance(exc, (reader.ReadRefused, FileNotFoundError)) else f"REFUSED: {exc}")
            print("EXIT 3", flush=True)
            return 3
        sens, window, target = RUN.SENSITIVITY_DESIGN, ("08:30", "15:10"), None
    try:
        prov = RUN.adapter_provenance(ROOT, strict=not a.synthetic)
        kw = {} if reps is None else {"honesty_reps": reps}
        out = RUN.run_reading(inputs, designs=designs, starts=starts, workers=a.workers, approved_limits=limits,
                              sensitivity_design=sens, time_window=window, **kw)
    except RUN.Refused as exc:
        print(f"REFUSED (RD-02): {exc} -- nothing written", flush=True)
        print("EXIT 3", flush=True)
        return 3
    from propedge.reporting.results import sha256_of

    sec11 = RUN.section_11(ROOT)
    runs = out["runs"]
    params = {
        "reading": "RD-02 (reading PP): described, not carried", "pinning_row": RUN.PIN_ROW,
        "declaration": RUN.DECLARATION, "declaration_sha256_lf": RUN.sha256_lf(ROOT / RUN.DECLARATION),
        "waits": ({k: {"what": what, "covered": list(cov), "rows": waits.get(k, []),
                       "commits": [t["sha"] for t in tokens(text) if t["row"] in waits.get(k, []) and t["id"] == k]}
                   for k, (what, cov) in WAITS.items()} if not a.synthetic else "the synthetic run waits for nothing"),
        "head": head,
        "runs": [list(r) for r in runs], "run_count": len(runs),
        "run_counts": {"policy_runs": sum(1 for r in runs if r[2] == "declared"),
                       "new": sum(1 for r in runs if r[2] == "declared" and r[1] != "ref"),
                       "references": sum(1 for r in runs if r[1] == "ref"),
                       "rule_sensitivity": sum(1 for r in runs if r[2] == "minimal"),
                       "replays_beside": len(RUN.BESIDE) * sum(1 for r in runs if r[2] == "declared"),
                       "gates": len(RUN.NEW_CELLS) * len(designs),        # the new cells' gates (section 12),
                       "gate_twins": len(RUN.NEW_CELLS) * len(designs)},  # each with its zero-edge twin (9.1 item 8)
        "beside": {"responses": list(RUN.BESIDE), "arm": "verdict", "cells": "the policy cells (not the sensitivity)"},
        "gates": {"cells": list(RUN.NEW_CELLS), "paths": int(inputs.n_paths()), "twin": True, "levels": [0.0]},
        "recorder_columns": list(RUN.RECORD_COLUMNS),
        "seeds": {"honesty_series": out["honesty_seed"], "section_11": sec11,
                  "retired": [r["seed"] for r in sec11 if r["status"].lower().startswith("retired")],
                  "ladder": "Q-17's lockstep.child_seed(20261920, 0, start_day), as run_starts draws them",
                  "inherited": "P-14's 20261131, P-16's 20261206 and 20261102 (their registered gate calls)"},
        "honesty": {"settings": [list(s) for s in out["honesty_settings"]],
                    "series_per_setting": int(reps or RUN.RD.HONESTY_SERIES)},
        "assumptions": ["the request's timing: after 5:00 PM CT (Stage 2 D-175)",
                        "the request's amount: any amount from the minimum to the maximum (E-034: unstated; half "
                        "needs it)", "the payout method: Aeropay, $0, 3 trading days (D-24)",
                        "the placement off (D-289) and 0 % denial (D-234) in the headline"],
        "no_effect_on_these_trades": [list(k) for k in out["no_effect"]],
        "funded_account_cls": {c: f"{PP.cell_class(c).__module__}.{PP.cell_class(c).__qualname__}" for c in PP.CELLS},
        "adapter": prov, "calendars": dict(RUN.CALENDARS),
        "data_manifest_sha256": sha256_of(ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"),
        "limits": ({"rows": limit_rows_used, "limits": limits} if limits else
                   "none approved before the run's commit: no e015-limits row in DECISIONS.md"), "repeat": a.repeat,
        "workers": int(a.workers), "synthetic": bool(a.synthetic), "seconds": round(time.time() - t0, 1),
    }
    notes = {"status": "described, not carried (E-023 (1)): no level, no pass line, no pick",
             "not_modelled": out["menu"]["note_not_modelled"].iloc[0] if len(out["menu"]) else ""}
    frames = {"pp_reading": out["reading"], "pp_gate": out["gate"], "pp_menu": out["menu"]}
    desc = {"pp_reading": "RD-02's reading: identity, oracle, mechanics, scorecard, paired, diverge, coverage, beside",
            "pp_gate": "RD-02's gates beside: the new cells' rows, their pairing with the base's registered paths, the "
                       "gate reading and divergences beside the base's registered row, the held counts",
            "pp_menu": "RD-02's menu: each cell's headline, guarded measures, flags and labels, the counts, the notes"}

    def write(where: Path | None) -> list[str]:
        import pandas as pd

        names = []
        for name in RESULTS:
            df = frames[name]
            if name == "pp_gate" and df.empty:
                df = pd.DataFrame({"note": ["no gate run"]})
            csv, man = XR.write_result(df, name if not a.synthetic else f"{name}_synthetic", script=SCRIPT,
                                       seed=int(out["honesty_seed"]), parameters=params, results_dir=where,
                                       description=desc[name], exploratory=False, prereg_id=RUN.PREREG_ID,
                                       variant_count=len(runs), notes=notes)
            XR.read_result(csv)
            names += [csv.name, man.name]
        return names

    wrote = write(target)
    print(f"written: {wrote}; {time.time() - t0:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
