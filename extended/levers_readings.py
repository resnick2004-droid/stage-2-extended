"""RD-03's readings of the terms no page settles (`prereg/RD-03_contract_levers.md` 4.3, U-1 to U-8): one table of
named constants, each citing its line of 4.3 (14.2). The adapters take every reading from here and type none
(`tests/test_cl_build.py`'s literal check exempts this table alone, and holds every entry to its citation).

Every number here is a reading, not a rule value: the rule values are loaded from their records by
`extended/levers_terms.py`.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    """One declared reading: its name, its value, the line of 4.3 it cites, and the label its rows carry."""

    name: str
    value: object
    cites: str
    label: str


READINGS: tuple[Reading, ...] = (
    Reading("expiry_readings", ("none", "30"), "U-1",
            "both readings run, neither the base: exp_none (a held pass waits, the engine's reading) and exp_30"),
    Reading("expiry_30_calendar_days", 30, "U-1",
            "exp_30: a pass not activated within 30 calendar days of the close it passed at is lost, unpaid and "
            "unseated (21 sessions in the gate); the only number on record is the search summary's"),
    Reading("cancel_at_billing_day", True, "U-2",
            "house money cancels an evaluation only at the last close before a rebill: the engine's abandonment at "
            "the start of the billing day, before that day trades"),
    Reading("reactivation_evening_first", True, "U-3",
            "bought before the 17:00 CT reopening; the base refills a session later by the engine's convention"),
    Reading("reactivated_tier", "entry", "U-4", "the reactivated account at the entry scaling tier"),
    Reading("b2f_barred_under_placement", True, "U-5",
            "no reactivation while a Slowdown or Corrective placement is in force"),
    Reading("reactivation_counted_as_purchase", False, "U-6", "not counted: the optimistic reading"),
    Reading("reactivation_counted_conservative", True, "U-6", "counted: the conservative reading"),
    Reading("requested_payout_taken", True, "U-7",
            "a payout requested in the account's current life is taken: the account is not eligible (one "
            "conservative reading of 'before taking a Payout')"),
    Reading("no_invented_limits", True, "U-8",
            "no limit on evaluations bought a day, on passes held at once, or on reactivations in a window beyond "
            "the per-XFA maximum"),
)
BY_NAME = {r.name: r for r in READINGS}
if len(BY_NAME) != len(READINGS):
    raise RuntimeError("two readings share a name")


def reading(name: str) -> object:
    """A reading's value, by name (`KeyError` for one this table does not declare)."""
    return BY_NAME[name].value


def label(name: str) -> str:
    return BY_NAME[name].label


#: the labels every row of a lever carries (10.1 item 12), from the readings above and G-1
LABEL_FIRST_ORDER = "first-order, the table fixed"
LABEL_GAMING_P = "gaming P (E-134 (2))"
LABEL_FTP_NOT_READ = "Focused Trader models not read"
LABEL_DEPENDS_EXPIRY = "depends on the hold's expiry"
LABEL_NOT_STABLE = "not stable across blocks"
LABEL_NO_EFFECT = "no effect on these trades"
LABEL_DESCRIBED = "described, not carried"
LABEL_SOLVER_VIEW = "the solver's view"
B2F_LABELS = ("bought before the 17:00 CT reopening", "the base refills a session later by the engine's convention",
              BY_NAME["reactivated_tier"].label, BY_NAME["reactivation_counted_as_purchase"].label)
FTP_GAP_REASON = {
    "naf": "identical to its base's under every model, fees aside: its reading is the base's from Q-44's per-start "
           "rows with the fees re-priced",
    "house": "placed no sooner than its base; the gap cannot flatter this lever",
}

__all__ = ["Reading", "READINGS", "BY_NAME", "reading", "label", "LABEL_FIRST_ORDER", "LABEL_GAMING_P",
           "LABEL_FTP_NOT_READ", "LABEL_DEPENDS_EXPIRY", "LABEL_NOT_STABLE", "LABEL_NO_EFFECT", "LABEL_DESCRIBED",
           "LABEL_SOLVER_VIEW", "B2F_LABELS", "FTP_GAP_REASON"]
