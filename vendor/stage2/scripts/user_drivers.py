"""EXPLORATORY (D-656, program U, U3): the user's journey read as one portfolio outcome -- which of the journey's
variables goes with a user being ahead, how much is the design and how much the start day, the frontier of the designs
on file and a menu by declared limits -- in one result file with a manifest, from the result files on record.

    python scripts/user_drivers.py --check     # everything computed; identity lines and row counts only; no write
    python scripts/user_drivers.py             # writes results/user_drivers.csv with its manifest

**It runs no engine, reads no market data and counts no variant: every row is a re-reading of a result file on
record.** The functions are `propedge/research/user_drivers.py`'s; the scorecard, the start records and the bootstrap's
resamples are `u_select`'s and `user_journey`'s own, imported and never written again. Two seeds, both constants of the
module: the moving-block bootstrap over start days (`BOOT_SEED`) and the family bootstrap (`CLUSTER_SEED`).

What is read (`results/`, each with its manifest; its sha256 is checked against the manifest before anything of it is
read, and pinned in this result's manifest):

* `user_journey.csv` (U1, D-620): each of the nine configurations' section `start` rows at both arms -> the
  within-design statistics, the accounting split and design against luck; its own month rows -> the identities.
* `u_budget.csv`, `u_entry.csv`, `u_seats.csv`, `u_hours.csv`, `u_firms.csv`, `u_consistency.csv`, `u_plan.csv` (the
  lever families 1 to 7): every COUNTED cell's ten scorecard measures at the bound arm on every start, COPIED; the
  cells labelled `hypothetical_hedge` are left out of everything; the cells labelled `lucid_upper_bound` are kept and
  carry the label.
* `user_scoreboard.csv` (D-640): the rows to beat's scorecards and the cells of the families it holds -> identities.
* `u_xfa_day_budget.csv` (U2, D-652): a few funded-account facts, COPIED (`user_drivers.FUNDED_FACTS`).

The identities, each a section `identity` row; **if one does not hold nothing is written and the exit is non-zero**
(D-656 (6)): every source's sha256 is its manifest's; each configuration's start rows carry every record, are
development starts only, and the accounting figures computed here equal U1's own month rows; the scorecards of P-14,
P-15 and P-16 computed from U1's start rows equal the scoreboard's rows (P among them) and R* is P-14; every source's
own identity rows hold; each family file is its family's and counts the cells it declares; its rows to beat and
reference cells equal the scorecards computed here; the cells the scoreboard holds equal its copies; the hypothetical
cells left out and the Lucid cells shown are the counts D-656 names; each cell's measures in the table equal its
family file's; the mean net is the mean payouts less the mean fees; the variance split adds up; no row is of a
hypothetical cell; every row is named once; every row's measure is one its section can hold, with a unit.

Writes `results/user_drivers.csv` with its manifest; EXPLORATORY. No page is built here: the Campaign Studio imports
the file (D-656 (7)).

**The schema: a long file, one row a figure.** The first nine columns after `reading` are the same in every section
and are all an importer needs to place a figure (`user_drivers.CORE`):

* `section` -- which table the row belongs to (the eleven below).
* `subject` -- what the figure is of: a design (`p14`, `budget15_p14`), a set of designs, a menu pick, `parameter`.
* `measure` -- which figure of that subject (the names below; stable, lower case but for the scorecard's keys).
* `value` -- the figure; blank where there is none.
* `n` -- what it was read on: start days, designs, accounts; for a frontier row the designs that beat it.
* `lo`, `hi` -- the ends of its 95% interval; blank where the figure has none.
* `unit` -- `share`, `dollars`, `sessions`, `ratio`, `correlation`, `standardised_weight`, `dollars_squared`,
  `count`, `month`, `seed` or `flag` (1 or 0).
* `note` -- a caution or what the figure is, in plain words.

A row is named once by `section`, `subject_kind`, `subject`, `arm`, `month`, `measure` (`user_drivers.KEY`). The
other columns:
`reading` (the file's status, the same on every row); `subject_kind` (`row_to_beat`, `family_cell`,
`u1_configuration`, `design_set`, `menu_pick`, `parameter`, `identity`; in `definitions`: `convention`, `variable`,
`measure`, `statistic`, `family`, `pick`); `arm` (`verdict`: each trade outcome at its lower bound -- the arm to show;
`point`: beside); `block` (`all`: every start day); `month` (a month is 21 sessions); `statistic`, `outcome`,
`variable` (the parts of a within- or between-design measure's name); `direction` (of a scorecard measure: `higher`
or `lower` is better); `draws`, `draws_valid` (the bootstrap's resamples, and those that held a figure); `mechanical`
(True where the link is partly arithmetic: show it apart); `name` (a design's short label, or a definition's plain
name), `family`, `family_decision`, `base`, `label` (`lucid_upper_bound` on an upper bound), `description` (the
design in a plain sentence), `overrides` (its settings as its family file records them); `pool`, `on_frontier`,
`dominated_by`, `pick` (on a design: in the frontier's pool, on the frontier, the designs that beat it, the menu
picks that name it); `picked`, `limit`, `floor`, `eligible`, `tied` (on a menu row: the design picked, the limit on
S1, the floor on S4b, the designs inside the limit, those sharing the highest
P); `meaning`, `modelled` (a definition's two sentences); `check`, `holds`, `compared`, `differing`, `refuses` (an
identity); `source_file`, `source_sha256`, `source_section` (where a figure is from).

**The sections and their measures:**

* `identity` -- one row a check that held before anything was written. Measure:
  `holds`
* `parameters` -- every constant a figure rests on (subject `parameter`). Measures:
  `month_sessions`, `p_first_month`, `p_last_month`, `boot_block`, `boot_draws`, `boot_seed`, `cluster_seed`,
  `interval_level`, `menu_floor`, `menu_floor_month`, `hypothetical_cells_left_out`, `lucid_cells_shown`,
  `menu_limit_lowest_cost`, `menu_limit_balanced`, `menu_limit_best_result`
* `definitions` -- text, no figure: for every variable, scorecard measure, statistic, convention, family and menu
  pick (`subject_kind` the kind, `subject` its key) a plain `name`, its `meaning` and how it is `modelled`.
* `design_table` -- each design on file (the three rows to beat and every counted cell of families 1 to 7 but the
  `hypothetical_hedge` ones) on the scorecard, the bound arm, every start day; with its `name`, `description`,
  `family`, `label` and its frontier and menu marks. Measures (`docs/USER_MILESTONES.md`):
  `P`, `S1`, `S3a`, `S3b`, `S3c`, `S4a`, `S4b`, `S5a`, `S5b`, `S5c`
* `within_design` -- within one of U1's nine configurations (subject), by `arm` and `month` (1 to 3), across start
  days: `spearman.<outcome>.<variable>` the rank correlation, `beta.<outcome>.<variable>` the standardised
  regression weight, `r2.<outcome>` the share explained; outcomes `net` (net cash) and `ahead` (1 if above zero).
  Measures:
  `spearman.net.bankroll`, `spearman.net.sessions_to_first_pass`, `spearman.net.sessions_to_first_payout`,
  `spearman.net.first_payout_dollars`, `spearman.net.payouts_per_fee_dollar`, `spearman.net.cash_before_first_pass`,
  `spearman.net.paid_by_month`, `spearman.ahead.bankroll`, `spearman.ahead.sessions_to_first_pass`,
  `spearman.ahead.sessions_to_first_payout`, `spearman.ahead.first_payout_dollars`,
  `spearman.ahead.payouts_per_fee_dollar`, `spearman.ahead.cash_before_first_pass`, `spearman.ahead.paid_by_month`,
  `beta.net.bankroll`, `beta.net.sessions_to_first_pass`, `beta.net.sessions_to_first_payout`,
  `beta.net.first_payout_dollars`, `beta.net.payouts_per_fee_dollar`, `beta.net.cash_before_first_pass`,
  `beta.ahead.bankroll`, `beta.ahead.sessions_to_first_pass`, `beta.ahead.sessions_to_first_payout`,
  `beta.ahead.first_payout_dollars`, `beta.ahead.payouts_per_fee_dollar`, `beta.ahead.cash_before_first_pass`,
  `r2.net`, `r2.ahead`
* `accounting` -- the same subjects, by `arm` and `month` (1, 2, 3, 6, 12): the net split into payouts and fees.
  Measures:
  `mean_net`, `mean_payouts`, `mean_fees`, `share_ahead`, `sd_net`, `payouts_per_fee_dollar_pooled`,
  `spread_share_payouts`, `spread_share_fees`
* `design_vs_luck` -- for a set of designs (subject `u1_configurations` or `rows_to_beat`), by `arm` and `month`: the
  net's variance between the designs' means against across start days. Measures:
  `design_share`, `start_day_share`, `between_variance`, `within_variance`, `total_variance`, `sd_of_design_means`,
  `mean_sd_across_starts`, `designs`
* `between_designs` -- across the designs of the table (subject `all_cells`, or `without_lucid`):
  `spearman.<key>` each scorecard measure's rank correlation with P, `beta.<key>` P's standardised regression
  weights, `r2`. Measures:
  `spearman.S1`, `spearman.S3a`, `spearman.S3b`, `spearman.S3c`, `spearman.S4a`, `spearman.S4b`, `spearman.S5a`,
  `spearman.S5b`, `spearman.S5c`, `beta.S1`, `beta.S3a`, `beta.S3c`, `beta.S5a`, `r2`
* `frontier` -- one row a design: 1 where no other design beats it at once on P, S1, S3a and S5a. Measure:
  `on_frontier`
* `menu` -- the three picks (subject `lowest_cost`, `balanced`, `best_result`), each with the scorecard of
  the design `picked`. Measures: the scorecard's ten, as in `design_table`.
* `funded_facts` -- for the three rows to beat, by `arm`: what a funded account's opening trade decides
  (`results/u_xfa_day_budget.csv`, D-652). Measures:
  `won_opening_share`, `won_opening_paid_share`, `lost_opening_lived_share`, `lost_opening_paid_share`,
  `lost_opening_share_of_days`, `won_opening_share_of_days`, `sessions_opening_to_request_p50`,
  `sessions_opening_to_request_p90`
"""
from __future__ import annotations

import argparse
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import u_select as Sel  # noqa: E402
from propedge.research import user_drivers as D  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402
from propedge.research import user_scoreboard as B  # noqa: E402

SCRIPT = D.SCRIPT
DECISION = D.DECISION
U1_FILE = f"{U.RESULT}.csv"
SCOREBOARD_FILE = f"{B.RESULT}.csv"
XFA_FILE = "u_xfa_day_budget.csv"
FAMILY_FILES = tuple(f"{Sel.result_name(f)}.csv" for _, f, _, _ in D.FAMILIES)
SOURCES = (U1_FILE, *FAMILY_FILES, SCOREBOARD_FILE, XFA_FILE)
#: R* as D-626 fixed it: asserted, never assumed
R_STAR_ON_RECORD = "p14"
#: U1's own month rows each accounting figure must equal: (the statistic here, U1's group and measure, its months)
U1_ROWS = (("mean_net", "luck", "net_mean", U.LUCK_MONTHS),
           ("sd_net", "luck", "sd_net_across_starts", U.LUCK_MONTHS),
           ("share_ahead", "periodic", "share_positive", U.PERIODIC_MONTHS),
           ("payouts_per_fee_dollar_pooled", "money_back", "payouts_per_fee_dollar_pooled", U.MONEY_BACK_MONTHS))
REFUSED = 2


def _verified(rd: Path, name: str) -> tuple[list[str], str, Any]:
    """(the problems, the file's sha256, its manifest): the file and its manifest exist and the file's sha256 is the
    manifest's (`propedge.reporting.results.verify_result`)."""
    from propedge.reporting.results import read_manifest, sha256_of, verify_result

    ok, msg = verify_result(rd / name)
    if not ok:
        return [msg], "", None
    return [], sha256_of(rd / name), read_manifest(rd / name)


def _read(rd: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(rd / name, dtype=str, keep_default_na=False, low_memory=False)


def u1_config(df: pd.DataFrame, config: str, arm: str) -> tuple[dict[str, Any] | None, list[str], int]:
    """One of U1's configurations at one arm: its start records (`u_select.records_from_start_rows`), its label, its
    accounting at every outcome month (`user_drivers.accounting` on `money_frame`) -- and the problems: a start whose
    exact run the file names and does not carry, a start after the development window, more than one label, an
    accounting figure that is not U1's own month row (`U1_ROWS`: value to 1e-9, n exactly). (what was read, the
    problems, the figures compared.)"""
    starts = df[(df["section"] == "start") & (df["config"] == config) & (df["arm"] == arm)]
    if not len(starts):
        return None, [f"{config} {arm}: no start row in {U1_FILE}"], 0
    recs, missing = Sel.records_from_start_rows(starts.to_dict("records"))
    problems = []
    if missing:
        problems.append(f"{config} {arm}: {len(missing)} starts were read from an exact-length run the file does not "
                        "carry")
    problems += [f"{config} {arm}: {p}" for p in Sel.window_problems(recs)]
    labels = sorted(set(starts["label"])) if "label" in starts.columns else [""]
    if len(labels) != 1:
        problems.append(f"{config} {arm}: {len(labels)} labels on its start rows, not one")
    frames = {m: D.money_frame(recs, m) for m in D.OUTCOME_MONTHS}
    acct = {m: D.accounting(frames[m]) for m in D.OUTCOME_MONTHS}
    g = df[(df["section"] == "month") & (df["config"] == config) & (df["arm"] == arm)]
    theirs = {str(k): (v, n) for k, v, n in zip(g["key"], g["value"], g["n"])}
    compared = 0
    for stat, group, measure, months in U1_ROWS:
        for m in D.OUTCOME_MONTHS:
            if m not in months:
                continue
            key = f"{group}:{measure}@{U.MONTH * m}"
            compared += 1
            if key not in theirs:
                problems.append(f"{config} {arm} {key}: not in {U1_FILE}")
            elif not (D.same(acct[m][stat], theirs[key][0]) and B.whole(theirs[key][1]) == acct[m]["n"]):
                problems.append(f"{config} {arm} {key}: computed here, it is not the file's row")
    return ({"records": recs, "label": labels[0], "frames": frames, "accounting": acct}, problems, compared)


def _scoreboard_index(sb: pd.DataFrame) -> dict[tuple[str, str, str], dict[str, list[dict[str, Any]]]]:
    """The scoreboard's section `scorecard` rows at the bound arm on every start: {(subject kind, family, subject):
    {measure: [rows]}} -- a configuration's rows computed from U1's start rows, a family cell's copied from its
    file's section `cell`."""
    out: dict[tuple[str, str, str], dict[str, list[dict[str, Any]]]] = {}
    s = sb[(sb["section"] == B.SCORECARD) & (sb["arm"] == D.ARM) & (sb["block"] == D.ALL)
           & sb["source_section"].isin(["start", "cell"]) & sb["measure"].isin(list(Sel.BY_KEY))]
    for r in s.to_dict("records"):
        if r["source_section"] == "cell" and not D.flag(r.get("counted")):
            continue
        out.setdefault((r["subject_kind"], r["family"], r["subject"]), {}).setdefault(r["measure"], []).append(r)
    return out


def build(rd: Path, *, draws: int | None = None) -> dict[str, Any]:
    """Everything the result holds, from the files under `rd`: `idents` (the section `identity` rows, each with its
    `problems`), `rows` (every other section) and `params` and `provenance` (the manifest's). Nothing of a source is
    read unless every source's sha256 is its manifest's; `rows` is empty unless every identity holds. `draws`: the
    bootstrap's resamples -- `user_drivers.BOOT_DRAWS` unless a test hands in fewer."""
    draws = D.BOOT_DRAWS if draws is None else int(draws)
    idents: list[dict[str, Any]] = []
    out: dict[str, Any] = {"idents": idents, "rows": [], "params": {}, "provenance": {}}

    def failed() -> bool:
        return any(i["refuses"] and not i["holds"] for i in idents)

    # ---- the sources: each file's sha256 is its manifest's, before anything of it is read
    shas: dict[str, str] = {}
    manifests: dict[str, Any] = {}
    for name in SOURCES:
        problems, shas[name], manifests[name] = _verified(rd, name)
        idents.append(D.identity_row(f"results/{name}: the file's sha256 is its manifest's", problems, compared=1))
    if failed():
        return out

    # ---- U1's configurations, both arms
    u1 = _read(rd, U1_FILE)
    configs: dict[tuple[str, str], dict[str, Any]] = {}
    for c in U.CONFIGS:
        for arm in D.ARMS:
            got, problems, compared = u1_config(u1, c, arm)
            if got is not None:
                configs[(c, arm)] = got
            idents.append(D.identity_row(
                f"results/{U1_FILE}: {c}'s {arm} start rows carry every record, are development starts only, and "
                "the mean net, its spread, the share ahead and the pooled payouts per fee dollar computed here equal "
                "the file's own month rows (value to 1e-9, n exactly)", problems, compared=compared))
    if failed():
        return out

    # ---- the rows to beat: the scorecards computed here against the scoreboard's rows; R*
    sb = _read(rd, SCOREBOARD_FILE)
    n_ident, failing = B.identity_rows_failing(sb.to_dict("records"))
    idents.append(D.identity_row(f"results/{SCOREBOARD_FILE}: every one of its own identity rows holds",
                                 failing or ([] if n_ident else ["the file holds no identity row"]),
                                 compared=n_ident))
    board = _scoreboard_index(sb)
    cards = {c: Sel.scorecard(configs[(c, D.ARM)]["records"]) for c in Sel.ROWS_TO_BEAT}
    compared, problems = 0, []
    for c in Sel.ROWS_TO_BEAT:
        held = board.get((B.DESIGN, "", c), {})
        for m in Sel.MEASURES:
            compared += 1
            rows_m = held.get(m.key, [])
            if len(rows_m) != 1:
                problems.append(f"{c} {m.key}: {len(rows_m)} scoreboard rows, not one")
            elif not (D.same(rows_m[0]["value"], cards[c][m.key]["value"])
                      and B.whole(rows_m[0]["n"]) == int(cards[c][m.key]["n"])):
                problems.append(f"{c} {m.key}: recomputed from U1's start rows, it is not the scoreboard's row")
    idents.append(D.identity_row(
        f"U1's start rows recompute the scoreboard's P and its nine guarded measures for {', '.join(Sel.ROWS_TO_BEAT)} "
        "(results/user_scoreboard.csv's design rows on every start; value to 1e-9, n exactly)", problems,
        compared=compared))
    r_star = Sel.row_to_beat(cards)["r_star"]
    starred = sorted(set(sb[(sb["section"] == B.SCORECARD) & (sb["is_r_star"] == "True")]["subject"]))
    problems = []
    if r_star != R_STAR_ON_RECORD:
        problems.append(f"R* computed here is {r_star}, not {R_STAR_ON_RECORD}")
    if starred != [R_STAR_ON_RECORD]:
        problems.append(f"the scoreboard marks {starred} as R*, not {R_STAR_ON_RECORD}")
    idents.append(D.identity_row(f"R* -- the best P of {', '.join(Sel.ROWS_TO_BEAT)} on every start (D-621 (2)) -- is "
                                 f"{R_STAR_ON_RECORD} here and in the scoreboard", problems, compared=2))

    # ---- the design table: the rows to beat, then every counted cell of the families
    rows: list[dict[str, Any]] = []
    for c in Sel.ROWS_TO_BEAT:
        rows += D.design_rows(c, D.ROW_TO_BEAT, D.ROWS_FAMILY, cards[c], base=c, source_file=U1_FILE,
                              source_sha256=shas[U1_FILE], source_section="start")
    file_cells: dict[str, tuple[str, dict[str, Any]]] = {}             # design -> (its file, its cell)
    hypothetical: list[str] = []
    lucid: list[str] = []
    for (decision, family, _, _), name in zip(D.FAMILIES, FAMILY_FILES):
        fr = _read(rd, name).to_dict("records")
        n_ident, failing = B.identity_rows_failing(fr)
        idents.append(D.identity_row(f"results/{name}: every one of its own identity rows holds",
                                     failing or ([] if n_ident else ["the file holds no identity row"]),
                                     compared=n_ident))
        v = D.family_verdict(fr)
        cells = D.counted_cells(fr)
        problems = list(v["problems"])
        if not problems:
            if (v["family"], v["decision"]) != (family, decision):
                problems.append(f"the file is {v['decision']}'s {v['family']}, not {decision}'s {family}")
            if v["cells"] != len(cells):
                problems.append(f"the verdict row declares {v['cells']} cells against {len(cells)} counted")
        for c in cells:
            problems += D.cell_problems(c)
            if c["design"] in file_cells or c["design"] in Sel.ROWS_TO_BEAT:
                problems.append(f"{c['design']}: a cell of that name is already in the table")
        idents.append(D.identity_row(
            f"results/{name}: it is {decision}'s family {family}, it counts the cells its verdict row declares, and "
            "each holds every scorecard measure once", problems, compared=len(cells)))
        compared, problems = 0, []
        for c in Sel.ROWS_TO_BEAT:
            n, bad = B.card_differences(fr, c, cards[c])
            compared, problems = compared + n, problems + bad
        held = {D.text(r.get("cell")) for r in fr if D.text(r.get("section")) == "cell"}
        for base in Sel.BASES:
            if Sel.REFERENCE_CELLS[base] in held:
                n, bad = B.card_differences(fr, Sel.REFERENCE_CELLS[base], cards[base])
                compared, problems = compared + n, problems + bad
        idents.append(D.identity_row(
            f"results/{name}: the rows to beat it carries, and its reference cells, equal the scorecards computed "
            "here from U1's start rows (value to 1e-9, n exactly)", problems, compared=compared))
        compared, problems = 0, []
        for c in cells:
            theirs = board.get((B.FAMILY_CELL, family, c["design"]))
            if theirs is None:
                continue
            for m in Sel.MEASURES:
                compared += 1
                mine, got = c["rows"].get(m.key, []), theirs.get(m.key, [])
                if len(mine) != 1 or len(got) != 1 or not D.same(mine[0].get("value"), got[0].get("value")) or (
                        B.whole(mine[0].get("n")) != B.whole(got[0].get("n"))):
                    problems.append(f"{c['design']} {m.key}: the family file's row is not the scoreboard's copy")
        idents.append(D.identity_row(
            f"results/{name}: every counted cell the scoreboard also holds equals its copy there on every measure "
            "(it holds families 1 to 3; none compared elsewhere)", problems, compared=compared))
        if any(i["refuses"] and not i["holds"] for i in idents[-4:]):
            continue
        for c in cells:
            if c["label"] == D.HYPOTHETICAL_LABEL:
                hypothetical.append(c["design"])
                continue
            if c["label"] == D.LUCID_LABEL:
                lucid.append(c["design"])
            file_cells[c["design"]] = (name, c)
            measures = {k: {"value": r[0].get("value"), "n": r[0].get("n")} for k, r in c["rows"].items()}
            rows += D.design_rows(c["design"], D.FAMILY_CELL, family, measures, base=c["base"], label=c["label"],
                                  overrides=c["overrides"], source_file=name, source_sha256=shas[name],
                                  source_section="cell")
    problems = []
    if len(hypothetical) != D.HYPOTHETICAL_DECLARED:
        problems.append(f"{len(hypothetical)} hypothetical cells left out, not the {D.HYPOTHETICAL_DECLARED} of "
                        f"{DECISION} (4)")
    if len(lucid) != D.LUCID_DECLARED:
        problems.append(f"{len(lucid)} Lucid cells shown, not the {D.LUCID_DECLARED} of {DECISION} (4)")
    idents.append(D.identity_row(
        f"the cells labelled {D.HYPOTHETICAL_LABEL} left out of everything are the {D.HYPOTHETICAL_DECLARED} of "
        f"{DECISION} (4), and the cells labelled {D.LUCID_LABEL} shown are its {D.LUCID_DECLARED}", problems,
        compared=len(hypothetical) + len(lucid)))
    if failed():
        return out

    # ---- between designs, the frontier and the menu
    cells = D.cells_of(rows)
    sets = ((D.SET_ALL, cells), (D.SET_NO_LUCID, [c for c in cells if c["label"] != D.LUCID_LABEL]))
    for label, members in sets:
        rows += D.between_rows(members, label, draws=draws)
    front = D.frontier(cells)
    picks = D.menu(cells)
    picked: dict[str, list[str]] = {}
    for p in picks:
        if p["design"]:
            picked.setdefault(p["design"], []).append(p["pick"])
    by_design = {c["design"]: c for c in cells}
    measure_n = {(r["subject"], r["measure"]): r["n"] for r in rows if r["section"] == D.DESIGN_TABLE}
    for r in rows:
        if r["section"] == D.DESIGN_TABLE:
            f = front[r["subject"]]
            r.update(pool=f["pool"], on_frontier=f["on_frontier"], pick=" ".join(picked.get(r["subject"], [])))
    for c in cells:
        f = front[c["design"]]
        rows.append({"section": D.FRONTIER, "subject": c["design"], "subject_kind": c["design_kind"],
                     "measure": D.ON_FRONTIER, "value": 1.0 if f["on_frontier"] else 0.0, "unit": D.FLAG,
                     "n": len(f["dominated_by"]), "arm": D.ARM, "block": D.ALL,
                     "name": c["name"], "family": c["family"], "label": c["label"],
                     "description": c["description"], "pool": f["pool"],
                     "on_frontier": f["on_frontier"], "dominated_by": " ".join(f["dominated_by"]),
                     "note": "" if f["pool"] else (
                         "an upper bound: shown, not in the frontier or the menu" if c["label"] == D.LUCID_LABEL else
                         "a frontier measure is blank: not in the frontier or the menu")})
    for p in picks:
        chosen = by_design.get(p["design"])
        for m in Sel.MEASURES:
            rows.append({"section": D.MENU, "subject": p["pick"], "subject_kind": D.MENU_PICK,
                         "limit": p["limit"], "floor": p["floor"], "arm": D.ARM, "block": D.ALL,
                         "picked": p["design"], "family": chosen["family"] if chosen else "",
                         "label": chosen["label"] if chosen else "",
                         "name": chosen["name"] if chosen else "",
                         "description": chosen["description"] if chosen else "", "eligible": p["eligible"],
                         "tied": p["tied"], "measure": m.key, "unit": m.unit, "direction": m.direction,
                         "value": chosen["measures"][m.key] if chosen else D.NAN,
                         "n": measure_n.get((p["design"], m.key)),
                         "note": "a reading aid on exploratory data, not a candidate; the limits were set after "
                                 "families 1 to 7 were read (D-656 (5))"})

    # ---- within a design, the accounting split, design against luck
    compared, acct_problems = 0, []
    for (c, arm), got in configs.items():
        kind = D.ROW_TO_BEAT if c in Sel.ROWS_TO_BEAT else D.U1_CONFIG
        head = {"subject": c, "subject_kind": kind, "label": got["label"], "arm": arm, "source_file": U1_FILE,
                "source_sha256": shas[U1_FILE], "source_section": "start"}
        for m in D.WITHIN_MONTHS:
            frame = D.start_frame(got["records"], m)
            for r in D.within_rows(frame, draws=draws):
                if frame["dropped"]:
                    r["note"] = (r["note"] + "; " if r["note"] else "") + f"{frame['dropped']} starts dropped (a blank)"
                rows.append({**head, "month": m, **r})
        for m in D.OUTCOME_MONTHS:
            a = got["accounting"][m]
            compared += 1
            if not D.same(a["mean_net"], a["mean_payouts"] - a["mean_fees"], 1e-9) or not D.same(
                    a["spread_share_payouts"] + a["spread_share_fees"], 1.0 if a["n"] > 1 and a["sd_net"] > 0
                    else D.NAN, 1e-9):
                acct_problems.append(f"{c} {arm} month {m}: the split does not add up")
            rows += [{**head, "section": D.ACCOUNTING, "month": m, "measure": s, "unit": D.ACCOUNTING_UNITS[s],
                      "value": a[s], "n": a["n"]} for s in D.ACCOUNTING_STATS]
    idents.append(D.identity_row("the mean net is the mean payouts less the mean fees, and the two shares of the "
                                 "net's spread add to one, for every configuration, arm and month", acct_problems,
                                 compared=compared))
    compared, luck_problems = 0, []
    for label, members in ((D.SET_U1, U.CONFIGS), (D.SET_ROWS, Sel.ROWS_TO_BEAT)):
        for arm in D.ARMS:
            for m in D.OUTCOME_MONTHS:
                split = D.variance_split({c: configs[(c, arm)]["frames"][m]["net"] for c in members})
                compared += 1
                if not D.same(split["between_variance"] + split["within_variance"], split["total_variance"], 1e-9):
                    luck_problems.append(f"{label} {arm} month {m}: between plus within is not the pooled variance")
                rows += [{"section": D.LUCK, "subject": label, "subject_kind": D.DESIGN_SET, "arm": arm, "month": m,
                          "measure": s, "unit": D.LUCK_UNITS[s], "value": split[s], "n": split["n"],
                          "source_file": U1_FILE, "source_sha256": shas[U1_FILE], "source_section": "start"}
                         for s in D.LUCK_STATS]
    idents.append(D.identity_row("the variance between the designs' means plus the variance across start days "
                                 "inside the designs is the pooled variance, for every set, arm and month",
                                 luck_problems, compared=compared))

    # ---- the funded facts, the definitions and the parameters
    xfa = _read(rd, XFA_FILE).to_dict("records")
    ident = [r for r in xfa if D.text(r.get("section")) == "identity"]
    idents.append(D.identity_row(
        f"results/{XFA_FILE}: every one of its own identity rows holds",
        [D.text(r.get("measure")) for r in ident if D.number(r.get("value")) != 1.0]
        or ([] if ident else ["the file holds no identity row"]), compared=len(ident)))
    funded, problems = D.funded_rows(xfa, Sel.ROWS_TO_BEAT, source_file=XFA_FILE, source_sha256=shas[XFA_FILE])
    idents.append(D.identity_row(f"results/{XFA_FILE}: every funded-account fact carried into the file is held once "
                                 f"for {', '.join(Sel.ROWS_TO_BEAT)} at both arms", problems, compared=len(funded)))
    rows += funded
    rows += D.definition_rows() + D.parameter_rows()
    if failed():
        return out

    # ---- the table against its sources, the hypothetical cells, the names
    as_written = D.table(rows).to_dict("records")
    compared, problems = 0, []
    for design, (name, c) in file_cells.items():
        n, bad = D.table_differences(as_written, design, c["rows"])
        compared, problems = compared + n, problems + bad
    idents.append(D.identity_row("each cell's measures in the design table equal its family file's rows (value to "
                                 "1e-9, n exactly)", problems, compared=compared))
    idents.append(D.identity_row(f"no row is of a cell labelled {D.HYPOTHETICAL_LABEL}",
                                 D.hypothetical_problems(rows, hypothetical), compared=len(rows)))
    idents.append(D.identity_row("every row is named once by " + ", ".join(D.KEY) + " and names a subject",
                                 D.key_problems(rows), compared=len(rows)))
    idents.append(D.identity_row("every row's measure is one its section can hold and every figure carries a unit "
                                 "(user_drivers.measure_names)", D.schema_problems(rows), compared=len(rows)))
    if failed():
        return out
    out["rows"] = rows
    out["provenance"] = {"sources": {n: {"sha256": shas[n], "git_commit": manifests[n].git_commit,
                                         "script": manifests[n].script, "rows": manifests[n].rows,
                                         "timestamp": manifests[n].timestamp} for n in SOURCES}}
    out["params"] = {
        "decision": DECISION, "study": D.STUDY, "program": Sel.PROGRAM, "arm": D.ARM, "beside_arm": D.BESIDE_ARM,
        "month_sessions": U.MONTH, "outcome_months": list(D.OUTCOME_MONTHS), "within_months": list(D.WITHIN_MONTHS),
        "variables": list(D.VARIABLES), "indicator_beside": D.PAID, "outcomes": list(D.OUTCOMES),
        "censoring": "a variable not reached by the month's last session is read at it: sessions = that session; "
                     "cash before the first payout or pass = the fees paid by it; first payout dollars = 0",
        "regression": "ordinary least squares on columns rescaled to mean 0 and spread 1; within a design: each "
                      "outcome on the six variables; between designs: P on " + ", ".join(D.BETWEEN_REGRESSORS),
        "bootstrap_within": {"kind": "moving block over start days (user_journey.block_indices)",
                             "block": D.BOOT_BLOCK, "draws": draws, "seed": D.BOOT_SEED, "interval": D.INTERVAL},
        "bootstrap_between": {"kind": "whole families with replacement; the three rows to beat are one family",
                              "draws": draws, "seed": D.CLUSTER_SEED, "interval": D.INTERVAL},
        "configurations": list(U.CONFIGS), "rows_to_beat": list(Sel.ROWS_TO_BEAT), "r_star": r_star,
        "families": [{"family": f, "decision": d, "file": n} for (d, f, _, _), n in zip(D.FAMILIES, FAMILY_FILES)],
        "cells": {"in_the_table": len(cells), "rows_to_beat": len(Sel.ROWS_TO_BEAT),
                  "family_cells": len(file_cells), "lucid_upper_bound": sorted(lucid),
                  "hypothetical_left_out": sorted(hypothetical),
                  "frontier_pool": int(sum(1 for f in front.values() if f["pool"])),
                  "on_frontier": sorted(d for d, f in front.items() if f["on_frontier"])},
        "frontier_measures": [list(x) for x in D.FRONTIER_MEASURES],
        "menu": {"limits": {k: v for k, v in D.MENU_LIMITS}, "limit_measure": D.MENU_LIMIT_MEASURE,
                 "floor": D.MENU_FLOOR, "floor_measure": D.MENU_FLOOR_MEASURE,
                 "picks": {p["pick"]: p["design"] for p in picks},
                 "tie": "highest P, then lower S1, then higher S3a, then higher S5a, then the first in file order"},
        "tolerance": D.TOL,
        "schema": {"core_columns": list(D.CORE), "key": list(D.KEY),
                   "measures": {k: list(v) for k, v in D.measure_names().items()}}}
    return out


def _print_identities(idents: list[dict[str, Any]]) -> None:
    for i in idents:
        tail = "" if i["compared"] is None else f" [{i['compared']} compared]"
        print(f"identity {'holds' if i['holds'] else 'FAILS'}: {i['check']}{tail}", flush=True)
        for p in i["problems"][:6]:
            print(f"    {p}", flush=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, draws: int | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="everything computed; identity lines and row counts only; "
                    "nothing written under results/ (the table goes to a temporary folder and is discarded)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    built = build(rd, draws=draws)
    idents, rows = built["idents"], built["rows"]
    _print_identities(idents)
    bad = [i for i in idents if i["refuses"] and not i["holds"]]
    if bad or not rows:
        print(f"REFUSED ({DECISION}): {len(bad)} of {len(idents)} identities do not hold; nothing written.")
        return REFUSED
    for i in idents:
        i.pop("problems", None)
    res = D.table(idents + rows)
    counts = D.section_counts(idents + rows)
    line = (f"every identity holds ({len(idents)}); rows: " + ", ".join(f"{s} {counts[s]}" for s in D.SECTIONS)
            + f" ({len(res)} in all); cells in the table: {built['params']['cells']['in_the_table']}")
    kw = dict(script=SCRIPT, seed=D.BOOT_SEED, exploratory=True, variant_count=0, parameters=built["params"],
              provenance=built["provenance"],
              notes={"status": D.READING,
                     "variant_count_rule": "none: no engine run and no variant counted -- every row is a re-reading "
                                           "of a result file on record",
                     "seed": f"the moving-block bootstrap over start days ({D.BOOT_SEED}); the family bootstrap "
                             f"between designs has its own ({D.CLUSTER_SEED}); nothing else is drawn",
                     "labels": f"{D.LUCID_LABEL}: carried on the six Lucid cells and on U1's 5 + 1 configuration -- "
                               f"every figure of them is an upper bound; {D.HYPOTHETICAL_LABEL}: those cells are in "
                               "no row",
                     "selection": "none: the menu is a reading aid, no pick is a candidate, no verdict of families 1 "
                                  "to 7 changes; the limits were set after those families were read (D-656 (5))",
                     "between_designs": "a description of related designs, never a test (D-656 (4))"},
              description="EXPLORATORY (D-656, program U, U3): the user's journey as one portfolio outcome. Within "
                          "each of U1's nine configurations across start days: each journey variable's rank "
                          "correlation with the net cash and with being ahead at months 1 to 3, a standardised "
                          "regression, moving-block bootstrap intervals, and the accounting split of the net into "
                          "payouts and fees. Design against luck: the share of the net's variance that is the "
                          "design. Between the cells of families 1 to 7 and the three rows to beat (hypothetical "
                          "cells in no row; Lucid cells marked upper bounds): each scorecard measure's rank "
                          "correlation with P, a standardised regression, intervals from resampling whole families; "
                          "the frontier and a menu by declared limits. No engine, no variant: a re-reading of files "
                          "on record; the identities first.")
    if a.check:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            write_result(res, D.RESULT, results_dir=Path(tmp), **kw)
        print(line + "; nothing written under results/, no reading printed (--check).")
        return 0
    write_result(res, D.RESULT, results_dir=rd, **kw)
    print(line + f"; written: {D.RESULT}.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
