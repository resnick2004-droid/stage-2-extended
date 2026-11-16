"""EXPLORATORY (D-621, program U): the program's scoreboard -- pure functions that lay U1's nine configurations and
every lever family's cells side by side on D-621's scorecard, so a document can cite P and its block values from one
result file with a manifest (D-628's finding: for U1's configurations they were rows of none). No engine, no draw, no
file read here: `scripts/user_scoreboard.py` reads the files on record and hands their rows in. It counts no variant
-- every row is a re-reading of a file on record.

Two kinds of row, one per subject x block x measure (section `scorecard`):

* **U1's configurations** (`design_rows`): the scorecard of each configuration at the `verdict` arm, COMPUTED from U1's
  section `start` rows by `u_select`'s own functions (`records_from_start_rows`, `scorecard`, `block` -- the caller's
  call; nothing of the selection rule is written again here), on every start (`all`), the choice block (`early`) and
  the judged block (`late`). A registered design (`u_select.ROWS_TO_BEAT` and `BESIDE_ONLY`) is a `design`, U1's other
  configurations are a `u1_cell`.
* **A family's cells** (`family_cell_rows`): every section `cell` row of a family file that is not a row to beat --
  each base's reference cell (`reference_cell`), the family's cells, the chosen cell at the point arm and, where the
  file holds them, an option's own "beside" record -- then every block value the file holds: its section `choice`
  rows (each cell's P on the block the choice was read on) and its sections `judged` and `reverse` (the chosen cell's
  ten measures on the judged block, and the reverse reading's on the early block, each on the start dates common with
  R*: `paired_with`). Each value is COPIED from the file's row, never recomputed. The rows to beat a family file
  carries (P-14, P-15 and P-16, read from U1's file) are not copied: they are the identity's side
  (`card_differences`) and are reported once, under U1's configurations. The file's per-year rows of line (4)(e) and
  its lines' own figures (differences, limits, tolerances) are not scorecard values and stay in the family file.

A section `scorecard` row is named by `KEY`: the subject's kind, its family (blank for U1's configurations), the
subject, the arm, the block, the measure and the section of the source file the value is from (`start`: computed from
U1's start rows; `cell`, `choice`, `judged`, `reverse`: copied from the family file's section of that name).

Beside every row: whether the subject is an eligible row to beat (D-621 (2): P-14, P-15, P-16 only), whether it is R*
(`rows_to_beat`: the best P of the three on every start, with P on the starts with 63 sessions and with the mean of the
file's three shares -- the caller refuses unless the two agree), the row to beat on the row's own measure, the
family's verdict and first failing line with the cell chosen on the choice block and on the reverse reading marked, and
the source file with its sha256. Section `program` (`program_rows`): one row a family and one for the program's count
of cells, read from the variant ledger (`ledger_counts`) -- a family file's own running count is the ledger's as its
clean checkout held it, so it is carried beside and never used.

Every blank is NaN in a number and the empty text elsewhere.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

from propedge.research import u_select as Sel
from propedge.research import user_journey as U

DECISION = Sel.DECISION
RESULT = "user_scoreboard"
SCRIPT = "scripts/user_scoreboard.py"
READING = ("EXPLORATORY (D-621, program U): the program's scoreboard -- U1's configurations and every lever family's "
           "cells on the scorecard, re-read from the files on record; no engine run, no variant counted; beside the "
           "gate, never a verdict of the gate (D-234)")

IDENTITY, SCORECARD, PROGRAM = "identity", "scorecard", "program"
SECTIONS = (IDENTITY, SCORECARD, PROGRAM)
#: the label of the set of every start (`u_select.block`'s None), as the family files write it
ALL = "all"
BLOCK_LABELS: tuple[tuple[str | None, str], ...] = ((None, ALL), (Sel.EARLY, Sel.EARLY), (Sel.LATE, Sel.LATE))
DESIGN, U1_CELL, FAMILY_CELL, REFERENCE_CELL = "design", "u1_cell", "family_cell", "reference_cell"
SUBJECT_KINDS = (DESIGN, U1_CELL, FAMILY_CELL, REFERENCE_CELL)
#: the kinds of a section `program` row
FAMILY_ROW, PROGRAM_ROW = "family", "program"
#: the two readings of a family's choice (`u_select.judge`), as the family files' section `choice` names them, each
#: with the block the choice is made on
DIRECTIONS = (("forward", Sel.EARLY), ("reverse", Sel.LATE))
#: the tolerance of every comparison between a scorecard computed here and a family file's row
TOL = 1e-9
#: what names one section `scorecard` row
KEY = ("subject_kind", "family", "subject", "arm", "block", "measure", "source_section")
#: a family file's sections that hold the chosen cell's scorecard on a block, paired with R* (`u_family._pair_rows`)
PAIRED_SECTIONS = ("judged", "reverse")
MEASURE_FIELDS = ("what", "unit", "direction", "measure_role")

COLUMNS = ("section", "reading",
           # section identity
           "check", "holds", "compared", "differing", "refuses",
           # section scorecard (and the subject of a section program row)
           "subject", "subject_kind", "arm", "block", "measure", "what", "unit", "direction", "measure_role", "value",
           "n", "paired_with", "family", "family_decision", "k", "base", "overrides", "counted",
           "eligible_row_to_beat", "is_r_star", "row_to_beat_on_measure", "chosen_on_choice_block",
           "chosen_on_reverse", "family_verdict", "family_first_failing", "label", "computed", "source_file",
           "source_sha256", "source_section", "source_role",
           # section program
           "level", "cells_counted", "ledger_records", "families", "chosen_cell", "chosen_cell_reverse",
           "chosen_base", "r_star", "source_program_cells", "source_program_families")

NAN = float("nan")
_BLANKS = ("", "nan", "NaN", "None")


def text(x: Any) -> str:
    return "" if x is None else str(x).strip()


def flag(x: Any) -> bool:
    return x is True or text(x) == "True"


def number(x: Any) -> float:
    s = text(x)
    return NAN if s in _BLANKS else float(s)


def whole(x: Any) -> int | None:
    """A whole number a file wrote as a number or as text (`971.0`); None for a blank."""
    v = number(x)
    return int(v) if math.isfinite(v) else None


def same(a: Any, b: Any, tol: float = TOL) -> bool:
    """Two readings equal: both blank, or both numbers within `tol`."""
    x, y = number(a), number(b)
    if not math.isfinite(x) or not math.isfinite(y):
        return (x != x and y != y) or x == y
    return abs(x - y) <= tol


# ------------------------------------------------------------------------------------------------ blocks and subjects


def block_label(which: str | None) -> str:
    """The label of one of `u_select.block`'s sets of starts: `all` (None: every start), `early` (the choice block)
    or `late` (the judged block)."""
    for w, name in BLOCK_LABELS:
        if which == w:
            return name
    raise ValueError(f"a block is None or one of {Sel.BLOCKS}, got {which!r}")


def subject_kind(config: str) -> str:
    """A configuration of U1's file: a registered design (`u_select.ROWS_TO_BEAT` and `BESIDE_ONLY`) is a `design`,
    its other configurations a `u1_cell`."""
    if config in Sel.ROWS_TO_BEAT or config in Sel.BESIDE_ONLY:
        return DESIGN
    if config in U.CONFIGS:
        return U1_CELL
    raise ValueError(f"{config!r} is not one of U1's configurations {U.CONFIGS}")


def cell_kind(cell: str) -> str:
    """A family file's cell: a base's cell with no override (`u_select.REFERENCE_CELLS`) is a `reference_cell`, any
    other a `family_cell`."""
    return REFERENCE_CELL if cell in Sel.REFERENCE_CELLS.values() else FAMILY_CELL


def measure_fields(key: str) -> dict[str, str]:
    """A scorecard measure's what, unit, direction and role, from `u_select.MEASURES`."""
    m = Sel.BY_KEY[key]
    return {"what": m.what, "unit": m.unit, "direction": m.direction, "measure_role": m.role}


# ------------------------------------------------------------------------------------------------ the rows to beat


def rows_to_beat(cards: Mapping[str, Mapping[str, Mapping[str, Any]]], p_file: Mapping[str, float]) -> dict[str, Any]:
    """D-621 (2) by `u_select.row_to_beat` (the best of P-14, P-15 and P-16 on each measure in its direction, a tie to
    the first in D-621's order, a blank never the best): `by_measure`, and R* under the two readings of P the family
    files' identity names -- `r_star` with P on the starts with 63 sessions (the scorecard's own) and
    `r_star_file_shares` with the mean of the file's three shares (`u_select.p_from_u1`, handed in as `p_file`).
    `cards`: {configuration: its scorecard on every start}."""
    rtb = Sel.row_to_beat(cards)
    other = Sel.row_to_beat({c: {**cards[c], Sel.PRIMARY_KEY: {"value": float(p_file[c]), "n": 0}}
                             for c in Sel.ROWS_TO_BEAT})
    return {"r_star": rtb["r_star"], "r_star_file_shares": other["r_star"], "by_measure": rtb["by_measure"]}


# ------------------------------------------------------------------------------------------------ U1's configurations


def design_rows(config: str, cards: Mapping[str, Mapping[str, Mapping[str, Any]]], *,
                by_measure: Mapping[str, Mapping[str, Any]], r_star: str | None, label: str = "",
                source_file: str = "", source_sha256: str = "") -> list[dict[str, Any]]:
    """One of U1's configurations as section `scorecard` rows: its scorecards on every start, the choice block and the
    judged block (`cards`: {block label: `u_select.scorecard`'s output}), each measure with its unit, direction and
    role. `by_measure`, `r_star`: `rows_to_beat`'s; `label`: U1's own label of the configuration (`lucid_upper_bound`
    where its file carries it)."""
    missing = [name for _, name in BLOCK_LABELS if name not in cards]
    if missing:
        raise ValueError(f"{config}: no scorecard on {missing}")
    kind = subject_kind(config)
    eligible = config in Sel.ROWS_TO_BEAT
    rows = []
    for _, name in BLOCK_LABELS:
        for m in Sel.MEASURES:
            rows.append({"section": SCORECARD, "subject": config, "subject_kind": kind, "arm": Sel.ARM, "block": name,
                         "measure": m.key, **measure_fields(m.key), "value": float(cards[name][m.key]["value"]),
                         "n": int(cards[name][m.key]["n"]), "eligible_row_to_beat": eligible,
                         "is_r_star": bool(eligible and r_star is not None and config == r_star),
                         "row_to_beat_on_measure": by_measure[m.key]["config"] or "", "label": label,
                         "computed": True, "source_file": source_file, "source_sha256": source_sha256,
                         "source_section": "start"})
    return rows


# ------------------------------------------------------------------------------------------------ a family's file


def family_meta(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What a family file says of itself (`scripts/u_family.py`'s `tables`): from its section `verdict` -- the family,
    its decision row, k, level and declared cells, the chosen cell with its base, R* (`reference`), the verdict, the
    first failing line and each line's status, and the file's own running count (`program_cells`, `program_families`:
    the ledger as the run's checkout held it) -- and from its section `choice` the cell chosen on the choice block
    (`chosen`: the forward reading, on `early`) and on the reverse reading (`chosen_reverse`: on `late`). `problems`:
    every way the file is not that (an empty list: it is)."""
    v = [r for r in rows if text(r.get("section")) == "verdict" and text(r.get("line")) == "verdict"]
    if len(v) != 1:
        return {"problems": [f"{len(v)} verdict rows, not one"]}
    v0 = v[0]
    problems: list[str] = []
    chosen: dict[str, str] = {}
    for direction, on in DIRECTIONS:
        c = [r for r in rows if text(r.get("section")) == "choice" and text(r.get("direction")) == direction]
        if not c:
            problems.append(f"no {direction} choice row")
        elif {text(r.get("block")) for r in c} != {on}:
            problems.append(f"the {direction} choice is not read on the {on} block")
        picked = [text(r.get("cell")) for r in c if flag(r.get("chosen"))]
        if len(picked) > 1:
            problems.append(f"{len(picked)} cells chosen on the {direction} reading")
        chosen[direction] = picked[0] if picked else ""
    if text(v0.get("cell")) != chosen["forward"]:
        problems.append("the verdict's cell is not the cell chosen on the choice block")
    family, decision = text(v0.get("family")), text(v0.get("decision"))
    try:
        fid = Sel.family_id(decision, family)
    except ValueError as e:
        fid = ""
        problems.append(str(e))
    k = whole(v0.get("k"))
    if k is None or k < 1:
        problems.append("the verdict row holds no k")
    if text(v0.get("verdict")) not in (Sel.CARRIED, Sel.CLOSED):
        problems.append(f"the verdict is neither {Sel.CARRIED} nor {Sel.CLOSED}")
    status = {text(r.get("line")): text(r.get("status")) for r in rows
              if text(r.get("section")) == "verdict" and text(r.get("line")) in Sel.LINES}
    if set(status) != set(Sel.LINES):
        problems.append("the verdict section does not hold every line of the selection rule")
    return {"family": family, "decision": decision, "family_id": fid, "k": k, "level": number(v0.get("level")),
            "cells": whole(v0.get("cells")), "chosen": chosen["forward"], "chosen_reverse": chosen["reverse"],
            "chosen_base": text(v0.get("base")), "reference": text(v0.get("reference")),
            "verdict": text(v0.get("verdict")), "first_failing": text(v0.get("first_failing")),
            "first_failing_status": text(v0.get("status")), "status": status,
            "program_cells": whole(v0.get("program_cells")), "program_families": whole(v0.get("program_families")),
            "problems": problems}


def _family_fields(meta: Mapping[str, Any], cell: str, kind: str) -> dict[str, Any]:
    picked = kind == FAMILY_CELL
    return {"family": meta["family"], "family_decision": meta["decision"], "k": meta["k"],
            "chosen_on_choice_block": bool(picked and cell == meta["chosen"]),
            "chosen_on_reverse": bool(picked and cell == meta["chosen_reverse"]),
            "family_verdict": meta["verdict"], "family_first_failing": meta["first_failing"]}


def family_cell_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Any], *,
                     by_measure: Mapping[str, Mapping[str, Any]], source_file: str = "", source_sha256: str = ""
                     ) -> tuple[list[dict[str, Any]], list[str]]:
    """A family file's cells as section `scorecard` rows, each value COPIED from the file's row (text to number; never
    recomputed): every section `cell` row but the rows to beat (`u_select.ROWS_TO_BEAT`, reported under U1's
    configurations) -- the reference cells, the family's cells at the arm and block the file names, the chosen cell at
    the point arm, an option's own record (its `measure`, `what`, `unit` and role as the file writes them) -- then every
    section `choice` row -- the cell's P on the block the choice was read on (`early` forward, `late` reverse; at the
    scorecard's arm, D-621 (1)) -- and every row of sections `judged` and `reverse`: the chosen cell's value on the
    judged block (the reverse reading's on `early`), on the start dates common with R* (`paired_with`). A scorecard
    measure's unit, direction and role are `u_select.MEASURES`'; the second output is every row where the file's own
    differ, and every other way the rows are not a family's (an empty list: none)."""
    out: list[dict[str, Any]] = []
    problems: list[str] = []
    seen: dict[str, tuple[str, str]] = {}                   # cell -> (base, overrides), from its section `cell` rows
    src = {"computed": False, "source_file": source_file, "source_sha256": source_sha256, "eligible_row_to_beat": False,
           "is_r_star": False}
    for r in rows:
        if text(r.get("section")) != "cell":
            continue
        cell, key = text(r.get("cell")), text(r.get("measure"))
        if cell in Sel.ROWS_TO_BEAT:
            continue
        kind = cell_kind(cell)
        if key in Sel.BY_KEY:
            fields = measure_fields(key)
            off = [c for c in MEASURE_FIELDS if text(r.get(c)) != fields[c]]
            if off:
                problems.append(f"{cell} {key}: the file's {', '.join(off)} is not u_select.MEASURES'")
            best = by_measure[key]["config"] or ""
        else:
            fields = {c: text(r.get(c)) for c in MEASURE_FIELDS}
            best = ""
        n = whole(r.get("n"))
        if n is None:
            problems.append(f"{cell} {key}: no n")
        seen.setdefault(cell, (text(r.get("base")), text(r.get("overrides"))))
        out.append({"section": SCORECARD, "subject": cell, "subject_kind": kind, "arm": text(r.get("arm")),
                    "block": text(r.get("block")), "measure": key, **fields, "value": number(r.get("value")), "n": n,
                    **_family_fields(meta, cell, kind), "base": text(r.get("base")),
                    "overrides": text(r.get("overrides")), "counted": flag(r.get("counted")),
                    "row_to_beat_on_measure": best, **src, "source_section": "cell",
                    "source_role": text(r.get("role"))})
    p = Sel.PRIMARY_KEY
    for r in rows:
        if text(r.get("section")) != "choice":
            continue
        cell = text(r.get("cell"))
        if text(r.get("measure")) != p:
            problems.append(f"{cell}: a choice row on {text(r.get('measure'))!r}, not {p}")
            continue
        if cell not in seen:
            problems.append(f"{cell}: a choice row of a cell with no cell row")
            continue
        kind = cell_kind(cell)
        n = whole(r.get("n"))
        if n is None:
            problems.append(f"{cell} {p} ({text(r.get('block'))}): no n")
        out.append({"section": SCORECARD, "subject": cell, "subject_kind": kind, "arm": Sel.ARM,
                    "block": text(r.get("block")), "measure": p, **measure_fields(p),
                    "value": number(r.get("value")), "n": n, **_family_fields(meta, cell, kind),
                    "base": seen[cell][0], "overrides": seen[cell][1],
                    "row_to_beat_on_measure": by_measure[p]["config"] or "", **src, "source_section": "choice",
                    "source_role": f"the {text(r.get('direction'))} choice"})
    for r in rows:
        section, cell, key = text(r.get("section")), text(r.get("cell")), text(r.get("measure"))
        if section not in PAIRED_SECTIONS or not cell:              # no cell: the file's note that none was chosen
            continue
        if key not in Sel.BY_KEY:
            problems.append(f"{cell}: a {section} row on {key!r}, not a scorecard measure")
            continue
        if cell not in seen:
            problems.append(f"{cell}: a {section} row of a cell with no cell row")
            continue
        fields = measure_fields(key)
        off = [c for c in ("unit", "direction") if text(r.get(c)) and text(r.get(c)) != fields[c]]
        if off:
            problems.append(f"{cell} {key} ({section}): the file's {', '.join(off)} is not u_select.MEASURES'")
        kind = cell_kind(cell)
        n = whole(r.get("n"))
        if n is None:
            problems.append(f"{cell} {key} ({section}): no n")
        out.append({"section": SCORECARD, "subject": cell, "subject_kind": kind, "arm": Sel.ARM,
                    "block": text(r.get("block")), "measure": key, **fields, "value": number(r.get("value")), "n": n,
                    "paired_with": text(r.get("reference")), **_family_fields(meta, cell, kind),
                    "base": seen[cell][0], "overrides": seen[cell][1],
                    "row_to_beat_on_measure": by_measure[key]["config"] or "", **src, "source_section": section,
                    "source_role": f"{section} at line {text(r.get('line'))}"})
    return out, problems


def paired_reference_differences(rows: Sequence[Mapping[str, Any]],
                                 cards: Mapping[str, Mapping[str, Mapping[str, Any]]], reference: str, *,
                                 tol: float = TOL) -> tuple[int, list[str]]:
    """A family file's sections `judged` and `reverse` against R*'s scorecards computed here (`cards`: {block label:
    R*'s scorecard on that block}): on every row the file's reference value -- R* on the row's block, on the start
    dates common with the chosen cell -- is R*'s own value on that block (to `tol`) on as many starts (line (3)(i)
    holds the common n; line (3)(ii) R*'s own). It holds wherever every base replays R*'s start dates, which the
    family file's own identity says; it ties the block values computed here to the rows a family was judged against.
    (the rows compared, the rows that differ or name another reference.)"""
    n, problems = 0, []
    for r in rows:
        section, key = text(r.get("section")), text(r.get("measure"))
        if section not in PAIRED_SECTIONS or key not in Sel.BY_KEY:
            continue
        n += 1
        where = f"{section} {text(r.get('line'))} {key}"
        block = text(r.get("block"))
        if text(r.get("reference")) != reference:
            problems.append(f"{where}: the reference is {text(r.get('reference'))}, not {reference}")
        elif block not in cards:
            problems.append(f"{where}: no scorecard on the block {block!r}")
        else:
            starts = r.get("n_reference") if text(r.get("line")) == Sel.LINES[1] else r.get("n")
            if not same(r.get("reference_value"), cards[block][key]["value"], tol):
                problems.append(f"{where}: the reference value differs")
            if whole(starts) != int(cards[block][key]["n"]):
                problems.append(f"{where}: the reference's n differs")
    return n, problems


def counted_cells(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """The cells a family file marks as counted (its section `cell` rows with `counted`), in the file's order."""
    out: list[str] = []
    for r in rows:
        if text(r.get("section")) == "cell" and flag(r.get("counted")) and text(r.get("cell")) not in out:
            out.append(text(r.get("cell")))
    return out


def identity_rows_failing(rows: Sequence[Mapping[str, Any]]) -> tuple[int, list[str]]:
    """(a file's section `identity` rows, the checks among them that do not hold)."""
    ident = [r for r in rows if text(r.get("section")) == "identity"]
    return len(ident), [text(r.get("check"))[:100] for r in ident if not flag(r.get("holds"))]


def card_differences(rows: Sequence[Mapping[str, Any]], cell: str, card: Mapping[str, Mapping[str, Any]], *,
                     arm: str = Sel.ARM, block: str = ALL, tol: float = TOL) -> tuple[int, list[str]]:
    """A family file's section `cell` rows of `cell` (at `arm`, on `block`) against a scorecard computed here: (the
    measures compared, every measure whose row is absent, held twice, or differs in value by more than `tol` or in n).
    No value is written into a problem."""
    mine: dict[str, list[Mapping[str, Any]]] = {}
    for r in rows:
        if (text(r.get("section")) == "cell" and text(r.get("cell")) == cell and text(r.get("arm")) == arm
                and text(r.get("block")) == block and text(r.get("measure")) in Sel.BY_KEY):
            mine.setdefault(text(r.get("measure")), []).append(r)
    problems = []
    for m in Sel.MEASURES:
        held = mine.get(m.key, [])
        if len(held) != 1:
            problems.append(f"{cell} {m.key}: {len(held)} rows, not one")
            continue
        if not same(held[0].get("value"), card[m.key]["value"], tol):
            problems.append(f"{cell} {m.key}: the value differs")
        if whole(held[0].get("n")) != int(card[m.key]["n"]):
            problems.append(f"{cell} {m.key}: n differs")
    return len(mine), problems


def flag_differences(rows: Sequence[Mapping[str, Any]], by_measure: Mapping[str, Mapping[str, Any]]
                     ) -> tuple[int, list[str]]:
    """A family file's own `row_to_beat` flags (on its rows to beat) against the best of the three computed here: (the
    flags compared, the rows whose flag differs)."""
    n, problems = 0, []
    for r in rows:
        cell, key = text(r.get("cell")), text(r.get("measure"))
        if text(r.get("section")) != "cell" or cell not in Sel.ROWS_TO_BEAT or key not in Sel.BY_KEY:
            continue
        n += 1
        if flag(r.get("row_to_beat")) != (by_measure[key]["config"] == cell):
            problems.append(f"{cell} {key}: the file's row-to-beat flag differs")
    return n, problems


# ------------------------------------------------------------------------------------------------ the program


def ledger_counts(variants: Iterable[Mapping[str, Any]], ids: Sequence[str]) -> dict[str, Any]:
    """The variant ledger's records under each family's id (`<row id>:u_<family>`): `records` (its lines) and
    `distinct` (its distinct cells, `u_select.program_count`), by family and in all, and `ledger_ids` -- every lever
    family id the ledger holds, whether or not it is one of `ids`."""
    rows = list(variants)
    count = Sel.program_count(rows)
    by = {i: {"records": int(sum(1 for r in rows if str(r.get("prereg_id", "")) == i)),
              "distinct": int(count["by_family"].get(i, 0))} for i in ids}
    return {"by_family": by, "records": int(sum(v["records"] for v in by.values())),
            "distinct": int(sum(v["distinct"] for v in by.values())), "ledger_ids": sorted(count["by_family"])}


def program_rows(metas: Sequence[Mapping[str, Any]], ledger: Mapping[str, Any], sources: Mapping[str, tuple[str, str]],
                 *, ledger_file: str = "", ledger_sha256: str = "") -> list[dict[str, Any]]:
    """Section `program`: one row a family, in the order declared (k) -- its decision row, k, level, the cells counted
    (the ledger's records under its id), the cell chosen on the choice block and on the reverse reading, the verdict
    and the first failing line, R*, and beside them the file's own running count (stale wherever a later family's
    lines were collected after its run) -- then one row for the program: its families and the cells counted across
    them, from the ledger. `sources`: {family id: (file, sha256)}."""
    rows = []
    for m in sorted(metas, key=lambda x: int(x["k"])):
        c = ledger["by_family"][m["family_id"]]
        f, sha = sources[m["family_id"]]
        rows.append({"section": PROGRAM, "subject": m["family"], "subject_kind": FAMILY_ROW, "family": m["family"],
                     "family_decision": m["decision"], "k": m["k"], "level": m["level"],
                     "cells_counted": c["records"], "ledger_records": c["records"], "chosen_cell": m["chosen"],
                     "chosen_cell_reverse": m["chosen_reverse"], "chosen_base": m["chosen_base"],
                     "family_verdict": m["verdict"], "family_first_failing": m["first_failing"],
                     "r_star": m["reference"], "computed": False, "source_file": f, "source_sha256": sha,
                     "source_section": "verdict", "source_program_cells": m["program_cells"],
                     "source_program_families": m["program_families"]})
    rows.append({"section": PROGRAM, "subject": Sel.PROGRAM, "subject_kind": PROGRAM_ROW, "families": len(metas),
                 "cells_counted": ledger["records"], "ledger_records": ledger["records"], "computed": True,
                 "source_file": ledger_file, "source_sha256": ledger_sha256})
    return rows


# ------------------------------------------------------------------------------------------------ the table


def identity_row(check: str, problems: Sequence[str], *, compared: int | None = None, refuses: bool = True
                 ) -> dict[str, Any]:
    """One section `identity` row; `problems` (kept for the caller's printing, never a column) decide `holds`."""
    return {"section": IDENTITY, "check": check, "holds": not problems, "compared": compared,
            "differing": len(problems), "refuses": bool(refuses), "problems": list(problems)}


def key_problems(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Every section `scorecard` row is named once by `KEY` (an empty list: it is)."""
    seen: dict[tuple, int] = {}
    for r in rows:
        if r.get("section") == SCORECARD:
            k = tuple(text(r.get(c)) for c in KEY)
            seen[k] = seen.get(k, 0) + 1
    return [f"{' / '.join(x for x in k if x)}: {n} rows" for k, n in seen.items() if n > 1]


def section_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {s: int(sum(1 for r in rows if r.get("section") == s)) for s in SECTIONS}


def table(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """The result's table: `COLUMNS` in order, a field a row does not carry (or holds as None) blank. A key that is
    not a column is refused."""
    unknown = sorted({k for r in rows for k in r} - set(COLUMNS))
    if unknown:
        raise ValueError(f"not columns of the scoreboard: {unknown}")
    blank = {c: "" for c in COLUMNS}
    df = pd.DataFrame([{**blank, **{k: ("" if v is None else v) for k, v in r.items()}} for r in rows],
                      columns=list(COLUMNS), dtype=object)
    df["reading"] = READING
    return df


__all__ = ["DECISION", "RESULT", "SCRIPT", "READING", "IDENTITY", "SCORECARD", "PROGRAM", "SECTIONS", "ALL",
           "BLOCK_LABELS", "DESIGN", "U1_CELL", "FAMILY_CELL", "REFERENCE_CELL", "SUBJECT_KINDS", "FAMILY_ROW",
           "PROGRAM_ROW", "DIRECTIONS", "TOL", "KEY", "PAIRED_SECTIONS", "MEASURE_FIELDS", "COLUMNS", "text", "flag",
           "number", "whole", "same", "block_label", "subject_kind", "cell_kind", "measure_fields", "rows_to_beat",
           "design_rows", "family_meta", "family_cell_rows", "paired_reference_differences", "counted_cells",
           "identity_rows_failing", "card_differences", "flag_differences", "ledger_counts", "program_rows",
           "identity_row", "key_problems", "section_counts", "table"]
