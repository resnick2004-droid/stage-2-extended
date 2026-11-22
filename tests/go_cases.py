"""Q-212: the go token's case table -- logs and declaration files with their expected `go_problems` rows and
`membership_event` row, each expectation written by hand from the lead's rulings (never computed by the reader). The
golden fixture `tests/data/go_token_golden.json` is this table, committed (`python tests/go_cases.py` rewrites it);
`tests/test_reader_go.py` replays the fixture and holds the table equal to it. Synthetic only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MARKER = "**Declaration kind: design search.**"
HT_MARKER = "**Declaration kind: held-out test.**"
RUNNER, RUNNER2 = "1" * 40, "2" * 40
DECIDING = "`extended/reader.py`, `scripts/survey.py`"


def search(title: str = "F-NN", market: str = "NQ", firm: str = "Topstep, 50K Combine", deciding: str = DECIDING,
           marker: str = MARKER, extra: str = "") -> str:
    """A design search's text with the fields the go token reads."""
    return (f"# {title}: a synthetic design search (Q-212's tests)\n\n{marker} A synthetic declaration.\n\n"
            f"- **The market:** {market} -- the one market this search reads\n"
            f"- **The firm and account:** {firm}\n- **The deciding files:** {deciding}\n{extra}")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


F13, F14, F15 = search("F-13"), search("F-14", firm="MFFU, Rapid 50K"), search("F-15", firm="Lucid, LucidFlex 50K")
A, B, C = sha(F13), sha(F14), sha(F15)
OTHER = "f" * 64
FILES = {"F-13_x.md": F13, "F-14_x.md": F14, "F-15_x.md": F15}


def pin(row: str, decl: str, s: str, day: str = "2026-12-01") -> str:
    return f"| {row} | {day} | **Search {decl}.** `prereg/{decl}_x.md` sha256 `{s}` | b |"


def go(row: str, decl: str, s: str, day: str = "2026-12-03", run: str = RUNNER, text: str = "the go row") -> str:
    return f"| {row} | {day} | go: {decl} @ {s} -- runner {run} -- {text} | b |"


def void(row: str, target: str, day: str = "2026-12-09") -> str:
    return f"| {row} | {day} | heldout-void: {target} -- recovery | b |"


def closed(row: str, decl: str, s: str, cause: str = "power-gate-failed", day: str = "2026-12-02") -> str:
    return f"| {row} | {day} | heldout-closed: {decl} @ {s} -- {cause} -- x | b |"


def fin(row: str, decl: str, s: str, day: str = "2026-12-05") -> str:
    return f"| {row} | {day} | heldout-finalists: {decl} @ {s} list {'9' * 64} -- the list | b |"


P13, P14, P15 = pin("E-900", "F-13", A), pin("E-901", "F-14", B), pin("E-903", "F-15", C)
G13 = go("E-902", "F-13", A)

#: name -> (log rows, files ({} = FILES), the problem rows (None: the unclosed fence), the event row or None)
CASES: dict[str, tuple[list[str], dict[str, str], list, str | None]] = {
    "good": ([P13, P14, G13, P15], {}, [], "E-902"),
    # finding 1, R1 to R7: each problem cleared by a later void, the next correct row then counted
    "R1 wrong sha": ([P13, P14, go("E-902", "F-13", OTHER)], {}, ["E-902"], None),
    "R1 wrong sha, voided, correct go": ([P13, P14, go("E-902", "F-13", OTHER), void("E-903", "E-902"),
                                          go("E-904", "F-13", A, "2026-12-10")], {}, [], "E-904"),
    "R2 unpinned F-31": ([P13, P14, go("E-902", "F-31", A)], {}, ["E-902"], None),
    "R2 voided, correct go": ([P13, P14, go("E-902", "F-31", A), void("E-903", "E-902"),
                               go("E-904", "F-13", A, "2026-12-10")], {}, [], "E-904"),
    "R3 second go": ([P13, P14, G13, go("E-903", "F-13", A, text="again")], {}, ["E-903"], None),
    "R3 second go voided": ([P13, P14, G13, go("E-903", "F-13", A, text="again"), void("E-904", "E-903")], {}, [],
                            "E-902"),
    "R4 go after closing": ([P13, closed("E-901", "F-13", A), go("E-902", "F-13", A)], {}, ["E-902"], None),
    "R4 voided": ([P13, closed("E-901", "F-13", A), go("E-902", "F-13", A), void("E-903", "E-902")], {}, [], None),
    "R5 go in its own pin's row": ([go("E-900", "F-13", A, text=f"pinned `prereg/F-13_x.md` sha256 `{A}`")], {},
                                   ["E-900"], None),
    "R5 voided, then a correct go": ([go("E-900", "F-13", A, text=f"pinned `prereg/F-13_x.md` sha256 `{A}`"),
                                      void("E-901", "E-900"), go("E-902", "F-13", A)], {}, [], "E-902"),
    "R6 malformed go carrying a pin": ([P13, go("E-902", "F-13", A, run=RUNNER[:39],
                                                text=f"with `prereg/F-14_x.md` sha256 `{B}`")], {}, ["E-902"], None),
    "R6 voided, F-14 still pinned": ([P13, go("E-902", "F-13", A, run=RUNNER[:39],
                                              text=f"with `prereg/F-14_x.md` sha256 `{B}`"), void("E-903", "E-902"),
                                      go("E-904", "F-14", B, "2026-12-10")], {}, [], "E-904"),
    "R7 a premature void, then malformed, then a void": ([void("E-899", "E-902", "2026-11-30"), P13,
                                                          go("E-902", "F-13", A, run=RUNNER[:39]),
                                                          void("E-903", "E-902"), go("E-904", "F-13", A, "2026-12-10")],
                                                         {}, [], "E-904"),
    "R7 the premature void alone": ([void("E-899", "E-902", "2026-11-30"), P13, go("E-902", "F-13", A, run=RUNNER[:39])],
                                    {}, ["E-902"], None),
    "R8 stray fence after a heading, voided": ([P13, "", "### notes", "```", G13, void("E-903", "E-900")], {}, [],
                                               None),
    "unclosed fence": ([P13, G13, "```", P14], {}, [None], None),
    # closing rows (finding 3)
    "C1 cause with spaces": ([P13, closed("E-901", "F-13", A, "power gate failed"), go("E-902", "F-13", A)], {},
                             ["E-901"], None),
    "C1 voided: the go counts": ([P13, closed("E-901", "F-13", A, "power gate failed"), void("E-903", "E-901"),
                                  go("E-904", "F-13", A, "2026-12-10")], {}, [], "E-904"),
    "C2 a cause outside the eight": ([P13, closed("E-901", "F-13", A, "preference"), go("E-902", "F-13", A)], {},
                                     ["E-901"], None),
    "C2 voided: the go counts (g27)": ([P13, closed("E-901", "F-13", A, "preference"), void("E-902", "E-901"),
                                        go("E-904", "F-13", A, "2026-12-10")], {}, [], "E-904"),
    "C3 closing at another sha": ([P13, closed("E-901", "F-13", OTHER), go("E-902", "F-13", A)], {}, ["E-901"], None),
    "C4 Heldout-closed capitalised": ([P13, closed("E-901", "F-13", A).replace("heldout-closed", "Heldout-closed"),
                                       go("E-902", "F-13", A)], {}, ["E-901"], None),
    "a valid closing row, its void a no-op": ([P13, closed("E-901", "F-13", A), void("E-902", "E-901"),
                                               go("E-904", "F-13", A, "2026-12-10")], {}, ["E-904"], None),
    "a fenced closing row, voided, does not close (g29)": ([P13, "```", closed("E-905", "F-13", A), "```",
                                                            void("E-906", "E-905"), G13], {}, [], "E-902"),
    "a closing row after the finalists": ([P13, G13, fin("E-904", "F-13", A), closed("E-905", "F-13", A)], {},
                                          ["E-905"], None),
    "withdrawn after the event": ([P13, P14, G13, closed("E-904", "F-14", B, "withdrawn")], {}, ["E-904"], None),
    "withdrawn before the event": ([P13, P14, closed("E-902", "F-14", B, "withdrawn"), go("E-904", "F-13", A)], {}, [],
                                   "E-904"),
    "a second closing row": ([P13, closed("E-901", "F-13", A), closed("E-902", "F-13", A, "withdrawn")], {},
                             ["E-902"], None),
    # voids
    "a void of the counted go row is a no-op": ([P13, P14, G13, P15, void("E-905", "E-902")], {}, [], "E-902"),
    "a void of that void": ([P13, P14, G13, void("E-905", "E-902"), void("E-906", "E-905")], {}, [], "E-902"),
    "a void of a pin row is a no-op": ([P13, G13, void("E-905", "E-900")], {}, [], "E-902"),
    "a void without its tail is no void (r07)": ([P13, go("E-902", "F-13", A, run=RUNNER[:39]),
                                                 "| E-903 | 2026-12-09 | heldout-void: E-902 | b |"], {}, ["E-902"],
                                                None),
    # pins (Q-212 (e))
    "a fenced pin is no pin (g30)": (["```", P13, "```", G13, pin("E-903", "F-13", A, "2026-12-04")], {}, ["E-902"],
                                     None),
    "an upper-case-hex pin is no pin (r06)": ([pin("E-900", "F-13", A.upper()), G13], {}, ["E-902"], None),
    "an early citation at another sha is no pin": ([pin("E-899", "F-13", OTHER, "2026-11-30"), P13, G13], {}, [],
                                                   "E-902"),
    "a pin in a non-row line is no pin": ([f"cited: `prereg/F-13_x.md` sha256 `{A}`", G13], {}, ["E-902"], None),
    "the reader's looser row spacing pins": ([P13.replace("| E-900 |", "|E-900|"), G13], {}, [], "E-902"),
    # the go row's form
    "M1 an impossible date": ([P13, go("E-902", "F-13", A, "2026-13-45")], {}, ["E-902"], None),
    "M2 an HTML comment, read as the reader reads it": ([P13, "<!--", G13, "-->"], {}, [], "E-902"),
    "M3 CRLF": ([P13 + "\r", P14 + "\r", G13 + "\r"], {}, [], "E-902"),
    "M6 NBSP after go:": ([P13, G13.replace("go: ", "go: ")], {}, ["E-902"], None),
    "M7 go spaced": ([P13, G13.replace("go: ", "go : ")], {}, ["E-902"], None),
    "Go: capital": ([P13, G13.replace("go:", "Go:")], {}, ["E-902"], None),
    "bold": ([P13, G13.replace("go: F-13", "**go: F-13").replace(" | b |", "** | b |")], {}, ["E-902"], None),
    "row start not exact": ([P13, G13.replace("| E-902 |", "|  E-902 |")], {}, ["E-902"], None),
    "no runner": ([P13, G13.replace(f" -- runner {RUNNER}", "")], {}, ["E-902"], None),
    "a fenced go row, voided": ([P13, "```", go("E-950", "F-13", A), "```", void("E-951", "E-950"), G13], {}, [],
                                "E-902"),
    "a fenced go row": ([P13, "```", go("E-950", "F-13", A), "```", G13], {}, ["E-950"], None),
    # the declaration's file and scope (Q-212 (c))
    "two files for one F-number (g31)": ([P13, G13], {"F-13_x.md": F13, "F-13_y.md": F13}, ["E-902"], None),
}

#: the scope's refusals: a declaration F-20 in each form, its pin and go row; the expectation is a problem at E-902
SCOPE_REFUSED = {
    "market ES": search("F-20", "ES"), "market NQZ6": search("F-20", "NQZ6"), "market NQH26": search("F-20", "NQH26"),
    "market ENQ": search("F-20", "ENQ"), "market NQQ": search("F-20", "NQQ"), "market `NQ`": search("F-20", "`NQ`"),
    "market **NQ**": search("F-20", "**NQ**"), "market nq": search("F-20", "nq"), "market NQ, ES": search("F-20", "NQ, ES"),
    "firm MFF": search("F-20", firm="MFF, Rapid 50K"), "firm Top step": search("F-20", firm="Top step, 50K"),
    "firm MyFundedFutures": search("F-20", firm="MyFundedFutures, Rapid 50K"),
    "firm My Funded Futures (MFFU)": search("F-20", firm="My Funded Futures (MFFU), Rapid 50K"),
    "firm TS": search("F-20", firm="TS, 50K"), "firm Topstep.": search("F-20", firm="Topstep. 50K"),
    "firm topstep": search("F-20", firm="topstep, 50K"), "firm TopstepX": search("F-20", firm="TopstepX, 50K"),
    "firm Lucid Trading": search("F-20", firm="Lucid Trading, 50K"), "firm **Topstep**": search("F-20", firm="**Topstep**, 50K"),
    "firm Apex": search("F-20", firm="Apex, 50K"),
    "two firms Lucid, Topstep": search("F-20", firm="Lucid, Topstep 50K"),
    "two firms Topstep -- and MFFU": search("F-20", firm="Topstep -- and MFFU 50K"),
    "firm placeholder": search("F-20", firm="<firm, plan>"),
    "two firm lines (g11)": search("F-20", extra="- **The firm and account:** Topstep, 50K\n"),
    "two market lines": search("F-20", extra="- **The market:** NQ -- again\n"),
    "renamed market field": search("F-20").replace("- **The market:** NQ", "- **Market:** NQ"),
    "no deciding files": search("F-20").replace("- **The deciding files:** " + DECIDING + "\n", ""),
    "deciding files without the reader": search("F-20", deciding="`scripts/survey.py`"),
    "a deciding path outside": search("F-20", deciding="`extended/reader.py`, `../x.py`"),
    "marker in a blockquote": search("F-20", marker="> " + MARKER),
    "marker period outside bold": search("F-20", marker="**Declaration kind: design search**."),
    "marker rewritten": search("F-20", marker="**Declaration kind:** design search."),
    "marker mid-line (g33)": search("F-20", marker="It says " + MARKER),
    "marker only fenced (g24)": "# F-20\n\n```\n" + MARKER + "\n```\n\n- **The market:** NQ -- x\n"
                                "- **The firm and account:** Topstep, 50K\n- **The deciding files:** " + DECIDING + "\n",
    "no marker, a search's headings": "# F-20\n\n## 5. The zero-edge convention\n\n- **The market:** NQ -- x\n",
    "both markers": search("F-20", extra=HT_MARKER + " also\n"),
}
SCOPE_ALLOWED = {
    "Topstep": search("F-20"), "MFFU": search("F-20", firm="MFFU, Rapid 50K"),
    "Lucid": search("F-20", firm="Lucid, LucidFlex 50K"), "MNQ": search("F-20", "MNQ"),
    "a fenced ES field above the real one": search("F-20").replace("- **The market:** NQ",
                                                                   "```\n- **The market:** ES\n```\n- **The market:** NQ",
                                                                   1),
    "firm then em text": search("F-20", firm="Topstep -- the 50K Combine"),
}


def scope_case(body: str) -> tuple[list[str], dict[str, str]]:
    s = sha(body)
    return [pin("E-900", "F-20", s), go("E-902", "F-20", s)], {"F-20_x.md": body}


def golden() -> list[dict]:
    out = []
    for name, (rows, files, probs, event) in CASES.items():
        out.append({"name": name, "log": "\n".join(rows), "files": files or FILES, "problem_rows": probs,
                    "event": event})
    for name, body in SCOPE_REFUSED.items():
        rows, files = scope_case(body)
        out.append({"name": "scope refused: " + name, "log": "\n".join(rows), "files": files, "problem_rows": ["E-902"],
                    "event": None})
    for name, body in SCOPE_ALLOWED.items():
        rows, files = scope_case(body)
        out.append({"name": "scope allowed: " + name, "log": "\n".join(rows), "files": files, "problem_rows": [],
                    "event": "E-902"})
    return out


GOLDEN = Path(__file__).resolve().parent / "data" / "go_token_golden.json"

if __name__ == "__main__":
    GOLDEN.write_text(json.dumps(golden(), indent=1, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(GOLDEN, len(golden()))
