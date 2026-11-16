"""Loader for `config/rules.yaml` -- the machine-readable copy of RULES_LEDGER.md.

The charter rule is: **nothing in this repository may depend on a rule whose status is not
"verified"**. This module enforces it at the point of use. `RulesLedger.value(name)` raises
`UnverifiedRuleError` unless the rule's status is `verified`, so a run that depends on an
unverified rule fails loudly instead of producing a plausible number.

On day one **every** rule was `carried_from_stage_one_reverify` or
`unverified_human_input_required`, so every call to `value()` raised. That was the intended
state: stage one had verified these rules a year earlier on pages that change, and the two
rules the campaign model rests on (the 5-account cap and the payout processing time) had never
been established at all. T1 (2026-09-22) read every rule the code loads on the official help
centre, so `value()` now answers for all of them. The gate itself is unchanged: a rule added
later starts unverified and raises until it has been read.

Reading a rule without the gate -- to report on it, to compare the ledger with the Markdown,
or to write a test at stage-one defaults -- goes through `entry()` or `raw_value()`, which
never raise on status. Those are for inspection, not for computation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from propedge import CONFIG_DIR

VERIFIED = "verified"
CARRIED = "carried_from_stage_one_reverify"
UNVERIFIED = "unverified_human_input_required"
THIRD_PARTY = "third_party"

VALID_STATUSES = {VERIFIED, CARRIED, UNVERIFIED, THIRD_PARTY}

_STATUS_EXPLANATION = {
    CARRIED: (
        "stage one verified it (see the article id and date on the entry) but stage two has "
        "not re-read it. Rules change; a stage-one reading is a lead, not a verification"
    ),
    UNVERIFIED: "needed by stage two and never verified by either stage",
    THIRD_PARTY: "sourced from a non-official page, which is never sufficient",
}


class UnverifiedRuleError(RuntimeError):
    """Raised when code asks for a rule that is not marked `verified`."""


class UnknownRuleError(KeyError):
    """Raised when code asks for a rule that is not in the ledger at all."""


@dataclass(frozen=True)
class RuleEntry:
    """One row of the ledger."""

    name: str
    value: Any
    status: str
    units: str | None = None
    article_id: str | None = None
    url: str | None = None
    date_read: str | None = None
    verified_by: str | None = None
    note: str | None = None

    @property
    def is_verified(self) -> bool:
        return self.status == VERIFIED

    def citation(self) -> str:
        """Article id, URL and date, for a report or a result manifest."""
        # str() because PyYAML parses an unquoted `2026-09-20` into a datetime.date.
        bits = [str(b) for b in (self.article_id, self.url, self.date_read) if b]
        return " | ".join(bits) if bits else "(no citation recorded)"


class RulesLedger:
    """The rules ledger, with the verified-status gate on `value()`."""

    def __init__(self, entries: dict[str, RuleEntry], meta: dict[str, Any], path: Path):
        self._entries = entries
        self.meta = meta
        self.path = path

    # ---------------------------------------------------------------- loading
    @classmethod
    def load(cls, path: Path | str | None = None) -> "RulesLedger":
        path = Path(path) if path is not None else CONFIG_DIR / "rules.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"rules config not found: {path}")
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        raw = doc.get("rules") or {}
        entries: dict[str, RuleEntry] = {}
        for name, body in raw.items():
            if not isinstance(body, dict):
                raise ValueError(f"rule {name!r} in {path} is not a mapping")
            status = body.get("status")
            if status not in VALID_STATUSES:
                raise ValueError(
                    f"rule {name!r} in {path} has status {status!r}; "
                    f"expected one of {sorted(VALID_STATUSES)}"
                )
            date_read = body.get("date_read")
            entries[name] = RuleEntry(
                name=name,
                value=body.get("value"),
                status=status,
                units=body.get("units"),
                article_id=body.get("article_id"),
                url=body.get("url"),
                # PyYAML turns an unquoted `2026-09-20` into a datetime.date; normalise to
                # a string so every consumer (citations, manifests, reports) sees one type.
                date_read=None if date_read is None else str(date_read),
                verified_by=body.get("verified_by"),
                note=body.get("note"),
            )
        return cls(entries, doc.get("meta") or {}, path)

    # ------------------------------------------------------------- inspection
    def __contains__(self, name: str) -> bool:
        return name in self._entries

    def __iter__(self) -> Iterator[RuleEntry]:
        return iter(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)

    def entry(self, name: str) -> RuleEntry:
        """The full row, regardless of status. Inspection only -- never for computation."""
        try:
            return self._entries[name]
        except KeyError:
            raise UnknownRuleError(
                f"no rule named {name!r} in {self.path}. Known rules: "
                f"{', '.join(sorted(self._entries))}"
            ) from None

    def raw_value(self, name: str) -> Any:
        """The value regardless of status. Inspection only -- never for computation.

        Use this to report on the ledger, to compare it with RULES_LEDGER.md, or to write a
        test that deliberately runs at stage-one defaults. Using it to compute a reported
        number defeats the entire gate; `value()` exists for that.
        """
        return self.entry(name).value

    def status(self, name: str) -> str:
        return self.entry(name).status

    def is_verified(self, name: str) -> bool:
        return self.entry(name).is_verified

    def unverified(self) -> list[RuleEntry]:
        """Every rule not marked verified, for `/status` and `/close-check`."""
        return [e for e in self._entries.values() if not e.is_verified]

    def verified(self) -> list[RuleEntry]:
        return [e for e in self._entries.values() if e.is_verified]

    # ------------------------------------------------------------------ gate
    def value(self, name: str) -> Any:
        """The value of a rule, **only** if it is verified.

        Raises:
            UnknownRuleError: no such rule.
            UnverifiedRuleError: the rule exists but its status is not `verified`.
        """
        entry = self.entry(name)
        if not entry.is_verified:
            why = _STATUS_EXPLANATION.get(entry.status, "not verified")
            raise UnverifiedRuleError(
                f"rule {name!r} has status {entry.status!r}: {why}.\n"
                f"  current value in the ledger: {entry.value!r}\n"
                f"  citation: {entry.citation()}\n"
                f"  note: {(entry.note or '').strip()}\n"
                f"Nothing in this repository may depend on a rule that is not verified "
                f"(CHARTER.md; RULES_LEDGER.md). Run `/verify-rule {name}` to read the "
                f"official article and record the value, article id, URL and date, or use "
                f"`raw_value({name!r})` if you are only inspecting the ledger."
            )
        if entry.value is None:
            raise UnverifiedRuleError(
                f"rule {name!r} is marked verified but its value is null in {self.path}. "
                "A verified rule must carry the value that was read."
            )
        return entry.value

    def require_verified(self, *names: str) -> None:
        """Assert several rules up front, so a long run fails before it starts.

        Reports every offending rule at once rather than one per run.
        """
        bad = [n for n in names if not self.entry(n).is_verified]
        if bad:
            lines = [
                f"  - {n}: {self.entry(n).status} ({self.entry(n).citation()})" for n in bad
            ]
            raise UnverifiedRuleError(
                "these rules must be verified before this run can proceed:\n"
                + "\n".join(lines)
                + "\nRun `/verify-rule <name>` for each, or see T1 in NEXT_STEPS.md."
            )


_CACHE: RulesLedger | None = None


def load_rules(path: Path | str | None = None, *, reload: bool = False) -> RulesLedger:
    """Process-wide cached ledger. Pass `reload=True` after `/verify-rule` edits the file."""
    global _CACHE
    if reload or _CACHE is None or path is not None:
        ledger = RulesLedger.load(path)
        if path is None:
            _CACHE = ledger
        return ledger
    return _CACHE
