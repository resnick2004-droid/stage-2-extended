"""E-221: the constitution's text says what the lead's rulings (by the operator's delegation) rule.

Each of the five rulings is present in the files that carry it, inside a block that names E-221, and every phrase it
replaced is gone from CHARTER.md, DIRECTIVE.md, CLAUDE.md and docs/MEASURES.md:

- **O-1:** every model built, tuned and chosen on the search years; the held-out years spent once per market by one
  joint fixed-sequence test of every finalist across the firms searched (Topstep, My Funded Futures, Lucid), held
  until each firm's search has finalists.
- **O-3 and Wave 4.2:** the size that matters, the limits, the bankroll budgets and the weights are the lead's, set
  from H4's search-year results by a rule declared before H4 is read, pinned before the survey, never after a
  held-out read.
- **O-4:** the coin is the evaluation's device, not the playbook's; each design's side from its own trigger under the
  no-harm floor; accounts alternate; the one hard rule is no opposite positions at once; the per-start coin keying of
  MEASURES stays.
- **O-5:** inside each limit at its point estimate, failing one only when the evidence shows it crosses, the single
  margin applied once.
- **O-6:** the long-run gate's quantile over coin seeds on the held-out years, the search years' history-block
  reading beside as a consistency condition.

The operator's hard limits (payments, orders, the confirmation window) are checked untouched. Text is compared with
its whitespace collapsed and its bold markers removed, so a line wrap never hides a phrase.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILES = ("CHARTER.md", "DIRECTIVE.md", "CLAUDE.md", "docs/MEASURES.md")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("**", "")).strip()


def _text(name: str) -> str:
    return _norm((ROOT / name).read_text(encoding="utf-8"))


def _blocks(name: str) -> list[str]:
    """The file's blocks (split at blank lines, and table rows one by one), each normalised."""
    raw = (ROOT / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    out: list[str] = []
    for block in re.split(r"\n\s*\n", raw):
        if block.lstrip().startswith("|"):
            out.extend(_norm(line) for line in block.split("\n") if line.strip())
        else:
            out.append(_norm(block))
    return out


#: (ruling, file, phrase): each phrase must appear in a block of its file that names E-221
PRESENT = (
    # O-1
    ("O-1", "CHARTER.md", "Every model is built, tuned and chosen on the search years only"),
    ("O-1", "CHARTER.md", "one joint fixed-sequence test of every finalist across the firms searched"),
    ("O-1", "CHARTER.md", "the held-out years are held until the Topstep, My Funded Futures and Lucid searches each have finalists"),
    ("O-1", "CHARTER.md", "every finalist across the firms is then tested in one joint fixed-sequence test"),
    ("O-1", "CHARTER.md", "Every firm's finalists enter the one joint sequence of 3.6 (c)"),
    ("O-1", "DIRECTIVE.md", "one joint fixed-sequence test of every finalist across the firms searched"),
    ("O-1", "CLAUDE.md", "by one joint test of every firm's finalists"),
    ("O-1", "docs/MEASURES.md", "the one joint held-out test of every firm's finalists only"),
    # O-3 and Wave 4.2
    ("O-3", "CHARTER.md", "the smallest difference that would change which design a user should run, with the power reported"),
    ("O-3", "CHARTER.md", "The weights are the lead's"),
    ("O-3", "CHARTER.md", "The lead sets the limits on what a user feels from the re-baseline's (H4's) search-year results"),
    ("O-3", "CHARTER.md", "The limits, the bankroll budgets, the weights and the size that matters are the lead's, set from H4's "
                          "search-year results by a rule declared before H4 is read, pinned in this one row before the survey, "
                          "never after a held-out read"),
    ("O-3", "DIRECTIVE.md", "the lead's, set with the bankroll budgets and the weights from H4's search-year results by a rule "
                            "declared before H4 is read"),
    ("O-3", "CLAUDE.md", "the limits, budgets and weights the lead's, from H4's search-year results by a rule declared before H4 is read"),
    ("O-3", "docs/MEASURES.md", "the bankroll budget, the lead's, set in Wave 4.2 from H4's search-year results"),
    ("O-3", "docs/MEASURES.md", "the bankroll budgets, the lead's, set in Wave 4.2 from H4's search-year results"),
    # O-4
    ("O-4", "CHARTER.md", "the coin is the evaluation's device, not the playbook's"),
    ("O-4", "CHARTER.md", "In the playbook, each design's side comes from its own trigger, held by the no-harm floor against the coin on the real path"),
    ("O-4", "CHARTER.md", "Accounts alternate: different accounts take different trades at different moments, the rotation a lever"),
    ("O-4", "CHARTER.md", "no two of the user's accounts or firms hold opposite positions at once"),
    ("O-4", "CHARTER.md", "never that every account copies every trade"),
    ("O-4", "CLAUDE.md", "the coin is the evaluation's, not the playbook's"),
    ("O-4", "CLAUDE.md", "no two of the user's accounts or firms hold opposite positions at once"),
    ("O-4", "docs/MEASURES.md", "no two of the user's accounts or firms hold opposite positions at once"),
    ("O-4", "docs/MEASURES.md", "never that every account copies every trade"),
    ("O-4", "docs/MEASURES.md", "the coin is the evaluation's device, not the playbook's"),
    # O-5
    ("O-5", "CHARTER.md", "the finalist must sit inside each limit at its point estimate, and it fails a limit only when the "
                          "evidence shows it crosses it"),
    ("O-5", "CHARTER.md", "That is the single margin, applied once"),
    ("O-5", "DIRECTIVE.md", "inside each limit at its point estimate, failing a limit only when the evidence shows it crosses, "
                            "the single margin applied once"),
    ("O-5", "CLAUDE.md", "sits inside each limit at its point estimate, failing one only when the evidence shows it crosses, "
                         "the single margin applied once"),
    # O-6
    ("O-6", "CHARTER.md", "over coin seeds on the held-out years; the history-block reading on the search years is read beside, "
                          "as a consistency condition"),
)

#: phrases the rulings replaced: none may remain in any of the four files
GONE = (
    "margin wider than its noise",             # O-5
    "with margin wider",                       # O-5
    "O-5 pending",                             # O-5
    "pending the operator",                    # O-4, O-5
    "the operator's, pending",                 # O-1
    "Until O-4 is ruled",                      # O-4
    "one literal coin draw",                   # O-4
    "the one literal coin draw",               # O-4
    "shared by all the user's accounts and firms",  # O-4
    "accounts and firms share a draw",         # O-4
    "the traded side rule pending",            # O-4
    "operator's limits",                       # Wave 4.2
    "every operator limit",                    # Wave 4.2, O-5
    "whose weights I set",                     # Wave 4.2 (E-207's wording)
    "The operator's weights",                  # Wave 4.2
    "weighted by the operator's trade-off answers",  # Wave 4.2
    "trade-off curves put to the operator",    # Wave 4.2
    "budgets the operator sets",               # Wave 4.2
    "the operator's bankroll budget",          # Wave 4.2
    "the operator's budgets",                  # Wave 4.2
    "the operator's budget who",               # Wave 4.2
    "The operator approves them",              # Wave 4.2
    "set at the operator's value",             # Wave 4.2
    "only if the operator sets one as a limit",  # Wave 4.2
    "the size that matters (the operator's",   # O-3
    "that matters (the operator's",            # O-3
    "coin seeds and history-block resamples pinned",  # O-6
    "is the operator's, pending (O-1)",        # O-1
    "Which firm's search spends NQ's held-out years",  # O-1
)


@pytest.mark.parametrize("ruling,name,phrase", PRESENT, ids=[f"{r}-{n}-{i}" for i, (r, n, _) in enumerate(PRESENT)])
def test_each_ruling_is_present_and_marked(ruling: str, name: str, phrase: str) -> None:
    p = _norm(phrase)
    hits = [b for b in _blocks(name) if p in b]
    assert hits, f"{ruling}: {name} lacks {phrase!r}"
    assert any("E-221" in b for b in hits), f"{ruling}: {name}'s block with {phrase!r} does not name E-221"


@pytest.mark.parametrize("name", FILES)
def test_each_replaced_phrase_is_gone(name: str) -> None:
    t = _text(name)
    left = [g for g in GONE if _norm(g) in t]
    assert not left, f"{name} still says: {left}"


def test_the_per_start_coin_keying_stays() -> None:
    """O-4 keeps MEASURES.md's keying and the three-way design's: draws keyed by start day, no account or firm index."""
    m = _text("docs/MEASURES.md")
    assert "Each user has their own coin draws. The key of every draw carries the start day" in m
    assert "The side coin's key carries no account or firm index" in m
    assert "The pairing. The design and every baseline, deciding at the same moment on the same start under the same seed" in m
    c = _text("CHARTER.md")
    assert "the side coin's key carries no account or firm index" in c
    assert "the scheduler refuses a same-moment opposite side" in c


def test_the_operator_hard_limits_are_untouched() -> None:
    """Payments, orders and the confirmation window stay the operator's (DIRECTIVE Part 1; CHARTER 4)."""
    d = _text("DIRECTIVE.md")
    for phrase in ("No payment, purchase, subscription, billing change or credit draw.",
                   "No live orders, and no automated or API order entry design",
                   "No read of a confirmation window. NQ from 2026-07-17 is reserved",
                   "The objective (Part 3) changes only with the operator."):
        assert phrase in d, phrase
    c = _text("CHARTER.md")
    assert "No automated or API order entry -- the operator's rule" in c
    assert "no payment without the operator's explicit yes" in c
    k = _text("CLAUDE.md")
    assert "except a payment: never authorise a purchase, subscription, billing" in k


def test_the_mapping_table_lists_the_e221_amendment() -> None:
    """DIRECTIVE's preamble lists every amendment in place; E-221's is there and the count of rows matches."""
    d = _text("DIRECTIVE.md")
    assert "amended in place (E-221" in d
    assert "the table's last three rows list" in d
