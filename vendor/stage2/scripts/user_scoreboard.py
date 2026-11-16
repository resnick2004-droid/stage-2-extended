"""EXPLORATORY (D-621, program U): the program's scoreboard -- U1's nine configurations and every lever family's cells
on D-621's scorecard, in one result file with a manifest, so a document can cite P and its block values (D-628's
finding: for U1's configurations they were rows of no result file).

    python scripts/user_scoreboard.py --check     # everything computed; identity lines and row counts only; no write
    python scripts/user_scoreboard.py             # writes results/user_scoreboard.csv with its manifest

**It runs no engine and counts no variant: every row is a re-reading of a result file on record.** It draws nothing
(no seed: the scorecard is an exact reading of the start rows; the bootstrap of line (3)(i) is not run here). The
functions are `propedge/research/user_scoreboard.py`'s; the measures, the blocks and the rows to beat are
`propedge/research/u_select.py`'s own (`records_from_start_rows`, `scorecard`, `block`, `row_to_beat`), imported and
never written again.

What is read (`results/`, each with its manifest but the ledger):

* `user_journey.csv` (U1, D-620): each of the nine configurations' section `start` rows at the `verdict` arm -> its
  scorecard on every start (`all`), the choice block (`early`) and the judged block (`late`); its label
  (`lucid_upper_bound` on the 5 + 1 cell) is carried.
* `u_budget.csv`, `u_entry.csv`, `u_seats.csv` (the lever families of D-629, D-630, D-635; `scripts/u_family.py`):
  every section `cell` row that is not a row to beat and every block value the file holds (its section `choice` rows:
  each cell's P on the choice block of each reading; its sections `judged` and `reverse`: the chosen cell's ten
  measures on the judged block -- `late`, and `early` for the reverse reading -- on the start dates common with R*),
  COPIED; the section `verdict` (the family, its decision row, k, level, chosen cell, verdict, first failing line).
* `variants.jsonl` (the variant ledger): the records under each family's id -- the program's count of cells (its
  sha256 is recorded with LF line ends, `ledger_sha256`: the same in every checkout). A
  family file's own running count is the ledger as its clean checkout held it (stale wherever an earlier family's
  lines were collected after its run), so it is carried beside and never used.

The identities, each a section `identity` row; **if one does not hold nothing is written and the exit is non-zero**:
every source file's sha256 is its manifest's (checked before anything of a file is read); each configuration's start
rows carry every record the scorecard reads, are development starts only, and recompute to U1's own rows; R* is P-14
with P on the starts with 63 sessions and with the mean of the file's three shares (D-621 (2), as the family files'
identity rows say); every family file's identity rows all hold; its section `verdict` is a family's, its id, level and
R* the declared ones; the scorecards of P-14, P-15 and P-16 computed here on every start equal the rows the file
carries for them to 1e-9, and its row-to-beat flags are the best of the three computed here; its reference cells
equal P-16 / P-14 on every measure; R*'s value on its judged and reverse rows is R*'s scorecard on that block
computed here; a scorecard measure's unit, direction and role in the file are `u_select.MEASURES`'; the cells it
counts are the ledger's records under its id; the ledger holds no lever family this file leaves out; every scorecard
row is named once.

Writes `results/user_scoreboard.csv` (sections `identity`, `scorecard`, `program`) with its manifest; EXPLORATORY.
A document cites a value as the `value` (with its `n`) of the one section `scorecard` row named by
`user_scoreboard.KEY` -- `subject_kind`, `family` (blank for U1's configurations), `subject`, `arm`, `block`,
`measure`, `source_section` -- for instance P-14's P on the judged block: `design`, ``, `p14`, `verdict`, `late`,
`P`, `start`; a count of cells as `cells_counted` of a section `program` row.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.research import u_select as Sel  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402
from propedge.research import user_scoreboard as B  # noqa: E402

SCRIPT = B.SCRIPT
DECISION = B.DECISION
U1_FILE = f"{U.RESULT}.csv"
LEDGER = "variants.jsonl"
#: the lever families on record, in the order declared: (the row that declared it, its name) -- D-629, D-630, D-635
FAMILIES = (("D-629", "budget"), ("D-630", "entry"), ("D-635", "seats"))
FAMILY_IDS = tuple(Sel.family_id(d, f) for d, f in FAMILIES)
FAMILY_FILES = tuple(f"{Sel.result_name(f)}.csv" for _, f in FAMILIES)
#: R* as the family files' identity rows and D-621 (2) give it: asserted, never assumed (a configuration's name)
R_STAR_ON_RECORD = "p14"
REFUSED = 2


def _verified(rd: Path, name: str) -> tuple[list[str], str, Any]:
    """(the problems, the file's sha256, its manifest): the file and its manifest exist and the file's sha256 is the
    manifest's (`propedge.reporting.results.verify_result`)."""
    from propedge.reporting.results import read_manifest, sha256_of, verify_result

    ok, msg = verify_result(rd / name)
    if not ok:
        return [msg], "", None
    return [], sha256_of(rd / name), read_manifest(rd / name)


def ledger_sha256(path: Path) -> str:
    """The ledger's sha256 with LF line ends. Git holds `variants.jsonl` as text (it has no manifest and is not pinned
    `-text` as the result CSVs are), so its line ends -- and the raw file's hash -- depend on the checkout; the hash of
    its content with LF line ends is the same in every checkout (`u_select.declaration`'s way with DECISIONS.md)."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _read(rd: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(rd / name, dtype=str, keep_default_na=False, low_memory=False)


def u1_config(df: pd.DataFrame, config: str) -> tuple[dict[str, Any] | None, list[str], int]:
    """One of U1's configurations at the `verdict` arm, as `scripts/u_family.py`'s `u1_side` reads a row to beat: its
    start records (`u_select.records_from_start_rows`), its scorecard on every block, the mean of the file's three
    shares, its label -- and the problems: a start whose exact run the file names and does not carry, a start after
    the development window, a scorecard reading that does not recompute to the file's own row. (what was read, the
    problems, the readings compared.)"""
    starts = df[(df["section"] == "start") & (df["config"] == config) & (df["arm"] == Sel.ARM)]
    if not len(starts):
        return None, [f"{config}: no {Sel.ARM} start row in {U1_FILE}"], 0
    recs, missing = Sel.records_from_start_rows(starts.to_dict("records"))
    problems = []
    if missing:
        problems.append(f"{config}: {len(missing)} starts were read from an exact-length run the file does not carry "
                        f"(first: start {missing[0][0]} at {missing[0][1]} sessions)")
    problems += [f"{config}: {p}" for p in Sel.window_problems(recs)]
    mine = Sel.u1_reading(recs)
    g = df[df["section"].isin(["metric", "month"]) & (df["config"] == config) & (df["arm"] == Sel.ARM)]
    theirs = {str(k): (v, n) for k, v, n in zip(g["key"], g["value"], g["n"])}
    for k, (v, n) in mine.items():
        if k not in theirs:
            problems.append(f"{config} {k}: not in {U1_FILE}")
        elif not (B.same(v, theirs[k][0]) and B.whole(theirs[k][1]) == int(n)):
            problems.append(f"{config} {k}: recomputed from the start rows, it is not the file's row")
    labels = sorted(set(starts["label"])) if "label" in starts.columns else [""]
    if len(labels) != 1:
        problems.append(f"{config}: {len(labels)} labels on its start rows, not one")
    cards = {name: Sel.scorecard(recs, which) for which, name in B.BLOCK_LABELS}
    return ({"records": len(recs), "cards": cards, "p_file": Sel.p_from_u1(mine), "label": labels[0]}, problems,
            len(mine))


def build(rd: Path) -> dict[str, Any]:
    """Everything the scoreboard holds, from the files under `rd`: `idents` (the section `identity` rows, each with its
    `problems`), `rows` (sections `scorecard` and `program`) and `params` (the manifest's). Nothing of a source file is
    read unless every source's sha256 is its manifest's; `rows` is empty unless every identity up to the rows holds."""
    from propedge.backtest.harness import VariantCounter

    idents: list[dict[str, Any]] = []
    out: dict[str, Any] = {"idents": idents, "rows": [], "params": {}}

    def failed() -> bool:
        return any(i["refuses"] and not i["holds"] for i in idents)

    # ---- the sources: each file's sha256 is its manifest's, before anything of it is read
    shas: dict[str, str] = {}
    manifests: dict[str, Any] = {}
    for name in (U1_FILE, *FAMILY_FILES):
        problems, shas[name], manifests[name] = _verified(rd, name)
        idents.append(B.identity_row(f"results/{name}: the file's sha256 is its manifest's", problems, compared=1))
    ledger_problems = [] if (rd / LEDGER).is_file() else [f"results/{LEDGER} is not on file"]
    idents.append(B.identity_row(f"results/{LEDGER}: the variant ledger is on file", ledger_problems, compared=1))
    if failed():
        return out

    # ---- U1's configurations
    u1 = _read(rd, U1_FILE)
    configs: dict[str, dict[str, Any]] = {}
    for c in U.CONFIGS:
        got, problems, compared = u1_config(u1, c)
        if got is not None:
            configs[c] = got
        idents.append(B.identity_row(
            f"results/{U1_FILE}: {c}'s {Sel.ARM} start rows carry every record the scorecard reads, are development "
            "starts only, and its readings recomputed from them (user_journey.metric_rows) equal the file's own rows",
            problems, compared=compared))
    if failed():
        return out
    all_cards = {c: configs[c]["cards"][B.ALL] for c in configs}
    rtb = B.rows_to_beat({c: all_cards[c] for c in Sel.ROWS_TO_BEAT},
                         {c: configs[c]["p_file"] for c in Sel.ROWS_TO_BEAT})
    r_star, by_measure = rtb["r_star"], rtb["by_measure"]
    problems = []
    if r_star != R_STAR_ON_RECORD:
        problems.append(f"R* is {r_star} with P on the starts with {Sel.P_HORIZON} sessions, not {R_STAR_ON_RECORD}")
    if rtb["r_star_file_shares"] != R_STAR_ON_RECORD:
        problems.append(f"R* is {rtb['r_star_file_shares']} with the mean of the file's three shares, not "
                        f"{R_STAR_ON_RECORD}")
    idents.append(B.identity_row(
        f"R* -- the best P of {', '.join(Sel.ROWS_TO_BEAT)} on every start (D-621 (2)) -- is {R_STAR_ON_RECORD} with P "
        f"on the starts with {Sel.P_HORIZON} sessions and with the mean of the file's three shares", problems,
        compared=2))

    # ---- the ledger
    variants = VariantCounter(path=rd / LEDGER).all()
    ledger = B.ledger_counts(variants, FAMILY_IDS)
    extra = [i for i in ledger["ledger_ids"] if i not in FAMILY_IDS]
    idents.append(B.identity_row(
        f"results/{LEDGER} holds no lever family this scoreboard leaves out (it reads {', '.join(FAMILY_IDS)})",
        [f"{i}: in the ledger, not in the scoreboard" for i in extra], compared=len(ledger["ledger_ids"])))

    # ---- the families
    metas: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for c in U.CONFIGS:
        rows += B.design_rows(c, configs[c]["cards"], by_measure=by_measure, r_star=r_star, label=configs[c]["label"],
                              source_file=U1_FILE, source_sha256=shas[U1_FILE])
    sources: dict[str, tuple[str, str]] = {}
    for (decision, family), fid, name in zip(FAMILIES, FAMILY_IDS, FAMILY_FILES):
        fr = _read(rd, name).to_dict("records")
        n_ident, failing = B.identity_rows_failing(fr)
        idents.append(B.identity_row(f"results/{name}: every one of its own identity rows holds",
                                     failing or ([] if n_ident else ["the file holds no identity row"]),
                                     compared=n_ident))
        meta = B.family_meta(fr)
        problems = list(meta["problems"])
        if not problems:
            if meta["family_id"] != fid:
                problems.append(f"the file is {meta['family_id']}'s, not {fid}'s")
            if not B.same(meta["level"], Sel.family_level(meta["k"]), 1e-15):
                problems.append("the level is not 0.05 / (k (k + 1))")
            if meta["reference"] != r_star:
                problems.append(f"the file's R* is {meta['reference']}, not {r_star}")
        idents.append(B.identity_row(
            f"results/{name}: its section verdict is one family's ({fid}) with one cell chosen on each reading, the "
            "verdict's cell the one chosen on the choice block, its level 0.05 / (k (k + 1)) and its R* the one "
            "computed here", problems, compared=1))
        if problems:
            continue
        compared, problems = 0, []
        for c in Sel.ROWS_TO_BEAT:
            n, bad = B.card_differences(fr, c, all_cards[c])
            compared, problems = compared + n, problems + bad
        idents.append(B.identity_row(
            f"results/{name}: the scorecards of {', '.join(Sel.ROWS_TO_BEAT)} computed here on every start equal the "
            f"rows the file carries for them (value to {B.TOL:g}, n exactly)", problems, compared=compared))
        compared, problems = B.flag_differences(fr, by_measure)
        idents.append(B.identity_row(
            f"results/{name}: its row-to-beat flags are the best of the three on each measure computed here "
            "(u_select.row_to_beat: a tie to the first)", problems, compared=compared))
        compared, problems = 0, []
        cells = {B.text(r.get("cell")): B.text(r.get("base")) for r in fr if B.text(r.get("section")) == "cell"}
        for base in Sel.BASES:
            ref = Sel.REFERENCE_CELLS[base]
            if ref in cells:
                n, bad = B.card_differences(fr, ref, all_cards[base])
                compared, problems = compared + n, problems + bad
            elif base in cells.values():
                problems.append(f"a cell on base {base} and no reference cell {ref}")
        if not compared:
            problems.append("the file holds no reference cell")
        idents.append(B.identity_row(
            f"results/{name}: its reference cells equal the scorecards of their bases computed here on every measure "
            f"({', '.join(f'{Sel.REFERENCE_CELLS[b]} = {b}' for b in Sel.BASES)}; value to {B.TOL:g}, n exactly)",
            problems, compared=compared))
        compared, problems = B.paired_reference_differences(fr, configs[r_star]["cards"], r_star)
        idents.append(B.identity_row(
            f"results/{name}: R*'s value on every judged and reverse row (R* on the row's block, on the start dates "
            f"common with the chosen cell) is its scorecard on that block computed here (value to {B.TOL:g}, n "
            "exactly)", problems, compared=compared))
        copied, problems = B.family_cell_rows(fr, meta, by_measure=by_measure, source_file=name,
                                              source_sha256=shas[name])
        idents.append(B.identity_row(
            f"results/{name}: every cell, choice, judged and reverse row is copied, and a scorecard measure's what, "
            "unit, direction and role in the file are u_select.MEASURES'", problems, compared=len(copied)))
        counted = B.counted_cells(fr)
        got = ledger["by_family"][fid]
        problems = []
        if got["records"] != got["distinct"]:
            problems.append(f"{got['records']} ledger records under {fid} are {got['distinct']} distinct cells")
        if got["records"] != len(counted):
            problems.append(f"{got['records']} ledger records under {fid} against {len(counted)} counted cells in the "
                            "file")
        if meta["cells"] != len(counted):
            problems.append(f"the verdict row declares {meta['cells']} cells against {len(counted)} counted")
        if manifests[name].variant_count != len(counted):
            problems.append(f"the manifest counts {manifests[name].variant_count} variants against {len(counted)} "
                            "cells")
        idents.append(B.identity_row(
            f"results/{name}: the cells it counts are the ledger's records under {fid}, each cell once, and its "
            "manifest's variant count", problems, compared=len(counted)))
        metas.append(meta)
        rows += copied
        sources[fid] = (name, shas[name])
    if failed():
        return out
    idents.append(B.identity_row("every scorecard row is named once by " + ", ".join(B.KEY), B.key_problems(rows),
                                 compared=len(rows)))
    if failed():
        return out
    ledger_sha = ledger_sha256(rd / LEDGER)
    rows += B.program_rows(metas, ledger, sources, ledger_file=LEDGER, ledger_sha256=ledger_sha)
    out["rows"] = rows
    out["params"] = {
        "decision": DECISION, "program": Sel.PROGRAM, "arm": Sel.ARM,
        "sources": {n: {"sha256": shas[n], "git_commit": manifests[n].git_commit, "script": manifests[n].script,
                        "rows": manifests[n].rows, "timestamp": manifests[n].timestamp}
                    for n in (U1_FILE, *FAMILY_FILES)},
        "ledger": {"file": LEDGER, "sha256": ledger_sha,
                   "sha256_of": "the file with LF line ends (git holds the ledger as text: the raw file's line ends "
                                "depend on the checkout)",
                   "records_by_family": ledger["by_family"],
                   "records": ledger["records"], "ids_in_ledger": ledger["ledger_ids"]},
        "configurations": {c: {"subject_kind": B.subject_kind(c), "starts": configs[c]["records"],
                               "label": configs[c]["label"]} for c in U.CONFIGS},
        "families": [{"family": m["family"], "decision": m["decision"], "family_id": m["family_id"], "k": m["k"],
                      "file": sources[m["family_id"]][0]} for m in metas],
        "measures": [m.key for m in Sel.MEASURES],
        "blocks": {B.ALL: "every start with the reading's horizon left",
                   Sel.EARLY: f"the choice block: starts to the last start of {Sel.CHOICE_LAST_YEAR} less the "
                              "reading's horizon",
                   Sel.LATE: f"the judged block: starts from the first session of {Sel.JUDGED_FIRST_YEAR} with the "
                             "reading's horizon left"},
        "p": f"months 1 to 3 ending above zero over three, on the starts with {Sel.P_HORIZON} sessions",
        "eligible_rows_to_beat": list(Sel.ROWS_TO_BEAT), "r_star": r_star,
        "r_star_with_the_files_three_shares": rtb["r_star_file_shares"],
        "rows_to_beat": {k: v["config"] for k, v in by_measure.items()},
        "computed": "U1's configurations: u_select.scorecard on u_select.records_from_start_rows of the file's start "
                    "rows",
        "copied": "the families' cells: the family file's own cell, choice, judged and reverse rows, text to number",
        "tolerance": B.TOL, "key": list(B.KEY)}
    return out


def _print_identities(idents: list[dict[str, Any]]) -> None:
    for i in idents:
        tail = "" if i["compared"] is None else f" [{i['compared']} compared]"
        print(f"identity {'holds' if i['holds'] else 'FAILS'}: {i['check']}{tail}", flush=True)
        for p in i["problems"][:6]:
            print(f"    {p}", flush=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="everything computed; identity lines and row counts only; "
                    "nothing written")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    built = build(rd)
    idents, rows = built["idents"], built["rows"]
    _print_identities(idents)
    bad = [i for i in idents if i["refuses"] and not i["holds"]]
    if bad or not rows:
        print(f"REFUSED ({DECISION}): {len(bad)} of {len(idents)} identities do not hold; nothing written.")
        return REFUSED
    for i in idents:
        i.pop("problems", None)
    res = B.table(idents + rows)
    counts = B.section_counts(idents + rows)
    kinds = res[res["section"] == B.SCORECARD]["subject_kind"].value_counts().to_dict()
    line = (f"every identity holds ({len(idents)}); rows: " + ", ".join(f"{s} {counts[s]}" for s in B.SECTIONS)
            + f" ({len(res)} in all); scorecard rows by subject kind: "
            + ", ".join(f"{k} {int(kinds.get(k, 0))}" for k in B.SUBJECT_KINDS))
    if a.check:
        print(line + "; nothing written, no reading printed (--check).")
        return 0
    write_result(res, B.RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=rd,
                 variant_count=0, parameters=built["params"],
                 notes={"status": B.READING,
                        "variant_count_rule": "none: no engine run and no variant counted -- every row is a re-reading "
                                              "of a result file on record (U1's start rows; the families' own rows)",
                        "seed": "none: nothing is drawn (the scorecard is an exact reading of the start rows; the "
                                "bootstrap of line (3)(i) is not run here)",
                        "labels": f"{U.LUCID_LABEL}: carried from U1's file on the configuration that holds it -- "
                                  "every figure of it is an upper bound on Lucid's two unpriced fees",
                        "program_count": f"the cells counted are results/{LEDGER}'s records under the families' ids; a "
                                         "family file's own running count (source_program_cells) is the ledger as its "
                                         "checkout held it and is carried beside, never used",
                        "selection": "none made here: the families' verdicts are their own files' (D-621 (3))"},
                 description="EXPLORATORY (D-621, program U): the program's scoreboard -- the scorecard (P and the "
                             "nine guarded measures, with n) of each of U1's nine configurations at the verdict arm on "
                             "every start, the choice block and the judged block, computed from U1's start rows by "
                             "u_select's own functions, beside every cell of the lever families copied from their own "
                             "files, each with its family, verdict and source sha256; and the program's count of cells "
                             "from the variant ledger. No engine, no seed, no variant: a re-reading of files on "
                             "record; the identities first.")
    print(line + f"; written: {B.RESULT}.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
