"""Load a firm's rules from `firms/<firm>/rules.yaml`, enforcing the verified-only gate.

The charter rule is "nothing in this repository may depend on a rule whose status is not
`verified`" (CLAUDE.md). This module is the enforcement: `FirmSpec.value()` raises for any
rule that is not marked verified, so unverified numbers cannot reach a simulation quietly.
The human-readable record behind each yaml is `firms/<firm>/RULES_LEDGER.md`; the two are
written together by the rules-verifier agent (`/verify-rule`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from propfirms import FIRMS_DIR

VALID_STATUSES = {
    "verified",
    "carried_reverify",
    "unverified_human_input_required",
    "third_party",
}


class UnverifiedRuleError(RuntimeError):
    """A rule was requested whose status is not `verified`."""


class SpecFormatError(ValueError):
    """A rules.yaml does not follow the schema in `firms/_TEMPLATE/rules.yaml`."""


@dataclass(frozen=True)
class Rule:
    key: str
    value: Any
    status: str
    article_id: str | None
    url: str | None
    date_read: str | None
    verified_by: str | None
    note: str | None


@dataclass(frozen=True)
class FirmSpec:
    """One firm's rules, as read from its `rules.yaml`."""

    firm: str
    program: str
    official_domains: tuple[str, ...]
    rules: dict[str, Rule]
    path: Path

    @classmethod
    def load(cls, firm_slug: str, firms_dir: Path | None = None) -> "FirmSpec":
        firms_dir = firms_dir or FIRMS_DIR
        path = firms_dir / firm_slug / "rules.yaml"
        if not path.is_file():
            available = sorted(
                p.parent.name for p in firms_dir.glob("*/rules.yaml")
            )
            raise FileNotFoundError(
                f"no rules.yaml for firm {firm_slug!r} at {path}. "
                f"Available: {available}. New firms are created by copying "
                "firms/_TEMPLATE/ (T2 in NEXT_STEPS.md)."
            )
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "rules" not in raw:
            raise SpecFormatError(f"{path} has no top-level `rules:` mapping")

        rules: dict[str, Rule] = {}
        for key, entry in (raw["rules"] or {}).items():
            if not isinstance(entry, dict):
                raise SpecFormatError(f"{path}: rule {key!r} is not a mapping")
            status = entry.get("status")
            if status not in VALID_STATUSES:
                raise SpecFormatError(
                    f"{path}: rule {key!r} has status {status!r}; "
                    f"valid statuses are {sorted(VALID_STATUSES)}"
                )
            if status == "verified" and entry.get("value") is None:
                raise SpecFormatError(
                    f"{path}: rule {key!r} is marked verified with a null value — "
                    "that combination is always an error"
                )
            rules[key] = Rule(
                key=key,
                value=entry.get("value"),
                status=status,
                article_id=entry.get("article_id"),
                url=entry.get("url"),
                date_read=entry.get("date_read"),
                verified_by=entry.get("verified_by"),
                note=entry.get("note"),
            )
        return cls(
            firm=str(raw.get("firm", firm_slug)),
            program=str(raw.get("program", "")),
            official_domains=tuple(raw.get("official_domains") or ()),
            rules=rules,
            path=path,
        )

    def value(self, key: str) -> Any:
        """The verified value of a rule. Raises unless its status is `verified`.

        That is the point: an unverified rule must fail loudly at the point of use, not
        flow into a simulation as if it were settled. Verify it first with
        `/verify-rule <firm> <key>`.
        """
        if key not in self.rules:
            raise KeyError(
                f"{self.firm}: no rule {key!r} in {self.path.name}; "
                f"known keys: {sorted(self.rules)}"
            )
        rule = self.rules[key]
        if rule.status != "verified":
            raise UnverifiedRuleError(
                f"{self.firm}: rule {key!r} has status {rule.status!r}, not `verified` — "
                "it may not be used. Verify it on the firm's official pages with "
                f"/verify-rule, recording the quote, page id, URL and date, in both "
                f"{self.path.name} and RULES_LEDGER.md."
            )
        return rule.value

    def unverified(self) -> list[str]:
        """Keys whose status is not `verified` — what `/status` reports."""
        return sorted(k for k, r in self.rules.items() if r.status != "verified")

    def provenance(self) -> dict[str, Any]:
        """For result-file manifests: the spec file, its firm and its sha256."""
        import sys

        scripts = str(self.path.parents[2] / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from hashes import sha256_file  # type: ignore

        return {
            "firm": self.firm,
            "program": self.program,
            "rules_yaml": str(self.path),
            "rules_yaml_sha256": sha256_file(self.path),
        }


def list_firms(firms_dir: Path | None = None) -> list[str]:
    """Every firm directory holding a rules.yaml, template excluded."""
    firms_dir = firms_dir or FIRMS_DIR
    return sorted(
        p.parent.name
        for p in firms_dir.glob("*/rules.yaml")
        if p.parent.name != "_TEMPLATE"
    )
