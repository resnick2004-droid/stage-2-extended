"""Firm ledgers other than Topstep's, loaded from the multi-firm repository's vendored copy (R7, docs/TWO_FIRMS.md).

Topstep's rules stay where they were: `config/rules.yaml` and `RULES_LEDGER.md`, read through
`propedge.contract.rules`. A second firm's rules are not re-captured here. The multi-firm repository
(`Desktop/Stage 1- XFA Eval Repository`, package `propfirms`) verified them on each firm's official pages, one row
per rule with the quote, page id, URL and date read (its D-07, D-22, D-28), and Stage 2 vendors that work read-only
at `vendor/propfirms/`, pinned byte for byte by `vendor/MANIFEST_propfirms.sha256` (the copy's source revision is in
the manifest's header). This module is the only place Stage 2 reads a vendored firm ledger, and it applies Stage 2's
gate to it:

* the ledger file must be the pinned bytes -- a `rules.yaml` whose sha256 is not the manifest's is refused before any
  row is read, so a ledger edited after vendoring cannot reach a simulation;
* `value(key)` answers only for a row whose status is `verified`, and raises `UnverifiedRuleError` (the same class as
  `propedge.contract.rules`) for every other status -- the multi-firm repository's open rows stay unusable here;
* a row marked `verified` must carry a non-null value, its official page id (`article_id`) and the date it was read
  (`date_read`), or the ledger is refused at load: a verified row without its citation is not a verification.

`entry()` and `raw_value()` read a row regardless of status, for reports and tests only, as in
`propedge.contract.rules`. Nothing here computes a number.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from propedge import REPO_ROOT
from propedge.contract.rules import UnknownRuleError, UnverifiedRuleError

#: The vendored multi-firm subset and its pin.
VENDOR_PROPFIRMS = REPO_ROOT / "vendor" / "propfirms"
PROPFIRMS_MANIFEST = REPO_ROOT / "vendor" / "MANIFEST_propfirms.sha256"

#: The multi-firm repository's status vocabulary (`vendor/propfirms/firms/README.md`).
VERIFIED = "verified"
VALID_STATUSES = {VERIFIED, "carried_reverify", "unverified_human_input_required", "third_party"}


class FirmLedgerError(ValueError):
    """A vendored firm ledger is not the pinned file, or a row breaks the schema."""


def pinned_digests(manifest: Path = PROPFIRMS_MANIFEST) -> dict[str, str]:
    """{path relative to vendor/: sha256} from the manifest; '#' lines are its header."""
    if not manifest.is_file():
        raise FirmLedgerError(f"{manifest} is missing: the vendored firm ledgers are unpinned (docs/TWO_FIRMS.md)")
    out: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if not rel:
            raise FirmLedgerError(f"malformed manifest line: {line!r}")
        out[rel] = digest
    return out


def source_revision(manifest: Path = PROPFIRMS_MANIFEST) -> str:
    """The multi-firm repository's revision the vendored copy was taken from (the manifest header's `commit:` line)."""
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.startswith("# commit:"):
            return line.split(":", 1)[1].strip().split()[0]
    raise FirmLedgerError(f"{manifest} names no source revision")


@dataclass(frozen=True)
class FirmRule:
    """One row of a vendored firm ledger."""

    key: str
    value: Any
    status: str
    article_id: str | None
    url: str | None
    date_read: str | None
    verified_by: str | None
    note: str | None

    @property
    def is_verified(self) -> bool:
        return self.status == VERIFIED

    def citation(self) -> str:
        bits = [str(b) for b in (self.article_id, self.url, self.date_read) if b]
        return " | ".join(bits) if bits else "(no citation recorded)"


class FirmLedger:
    """One firm's vendored ledger with Stage 2's verified-status gate on `value()`."""

    def __init__(self, slug: str, firm: str, program: str, rules: dict[str, FirmRule], path: Path, sha256: str):
        self.slug, self.firm, self.program = slug, firm, program
        self._rules = rules
        self.path = path
        self.sha256 = sha256

    @classmethod
    def load(cls, slug: str, *, root: Path | None = None, manifest: Path | None = None) -> "FirmLedger":
        """Load `firms/<slug>/rules.yaml` from the vendored copy, refusing a file that is not the pinned bytes."""
        root = Path(root) if root is not None else VENDOR_PROPFIRMS
        manifest = Path(manifest) if manifest is not None else PROPFIRMS_MANIFEST
        path = root / "firms" / slug / "rules.yaml"
        if not path.is_file():
            known = sorted(p.parent.name for p in (root / "firms").glob("*/rules.yaml"))
            raise FileNotFoundError(f"no vendored ledger for firm {slug!r} at {path}; vendored: {known}")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        rel = f"propfirms/firms/{slug}/rules.yaml"
        pinned = pinned_digests(manifest).get(rel)
        if pinned is None:
            raise FirmLedgerError(f"{rel} is not in {manifest.name}: an unpinned ledger cannot be loaded")
        if pinned != digest:
            raise FirmLedgerError(
                f"{rel} does not match its pin in {manifest.name} ({digest} != {pinned}). The vendored copy is "
                "read-only: restore it from the multi-firm repository's recorded revision, or re-vendor it under a "
                "decision."
            )
        doc = yaml.safe_load(data.decode("utf-8")) or {}
        raw = doc.get("rules")
        if not isinstance(raw, dict):
            raise FirmLedgerError(f"{path} has no top-level `rules:` mapping")
        rules: dict[str, FirmRule] = {}
        for key, body in raw.items():
            if not isinstance(body, dict):
                raise FirmLedgerError(f"{path}: rule {key!r} is not a mapping")
            status = body.get("status")
            if status not in VALID_STATUSES:
                raise FirmLedgerError(f"{path}: rule {key!r} has status {status!r}; valid: {sorted(VALID_STATUSES)}")
            date_read = body.get("date_read")
            rule = FirmRule(
                key=str(key), value=body.get("value"), status=str(status),
                article_id=None if body.get("article_id") is None else str(body.get("article_id")),
                url=body.get("url"),
                date_read=None if date_read is None else str(date_read),
                verified_by=body.get("verified_by"), note=body.get("note"),
            )
            if rule.is_verified and (rule.value is None or not rule.article_id or not rule.date_read):
                raise FirmLedgerError(
                    f"{path}: rule {key!r} is marked verified without its value, page id or date read "
                    f"(value={rule.value!r}, article_id={rule.article_id!r}, date_read={rule.date_read!r}); "
                    "a verified row carries all three"
                )
            rules[str(key)] = rule
        return cls(slug, str(doc.get("firm", slug)), str(doc.get("program", "")), rules, path, digest)

    # ------------------------------------------------------------- inspection
    def __contains__(self, key: str) -> bool:
        return key in self._rules

    def __iter__(self) -> Iterator[FirmRule]:
        return iter(self._rules.values())

    def entry(self, key: str) -> FirmRule:
        """The full row, regardless of status. Inspection only -- never for computation."""
        try:
            return self._rules[key]
        except KeyError:
            raise UnknownRuleError(f"{self.firm}: no rule {key!r} in {self.path}; known: {sorted(self._rules)}") from None

    def raw_value(self, key: str) -> Any:
        """The value regardless of status. Inspection only -- never for computation."""
        return self.entry(key).value

    def verified(self) -> list[FirmRule]:
        return [r for r in self._rules.values() if r.is_verified]

    def unverified(self) -> list[FirmRule]:
        return [r for r in self._rules.values() if not r.is_verified]

    # ------------------------------------------------------------------ gate
    def value(self, key: str) -> Any:
        """The value of a rule, only if it is verified (with its value, page id and date, checked at load)."""
        rule = self.entry(key)
        if not rule.is_verified:
            raise UnverifiedRuleError(
                f"{self.firm}: rule {key!r} has status {rule.status!r}, not 'verified' -- it may not be used.\n"
                f"  citation: {rule.citation()}\n  note: {(rule.note or '').strip()[:400]}\n"
                "Nothing in this repository may depend on a rule that is not verified (CHARTER.md). The multi-firm "
                "repository's rules-verifier records the reading there; re-vendor it under a decision to use it here."
            )
        return rule.value

    def verified_note(self, key: str) -> str:
        """The quoted note of a VERIFIED row -- for a figure the firm's page states inside the quote (the multi-firm
        repository parses FundedNext's lock the same way). Raises like `value()` for any other status."""
        self.value(key)
        return str(self.entry(key).note or "")

    def provenance(self) -> dict[str, Any]:
        """For result manifests: the firm, the program, the vendored ledger, its sha256 and the source revision."""
        try:
            shown = self.path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            shown = str(self.path)
        return {
            "firm": self.firm, "slug": self.slug, "program": self.program,
            "rules_yaml": shown, "rules_yaml_sha256": self.sha256,
            "source": "multi-firm repository (propfirms), vendored read-only",
            "source_revision": source_revision(),
        }


def vendored_firms(root: Path | None = None) -> list[str]:
    """Every firm whose ledger is vendored."""
    root = Path(root) if root is not None else VENDOR_PROPFIRMS
    return sorted(p.parent.name for p in (root / "firms").glob("*/rules.yaml"))


__all__ = ["VENDOR_PROPFIRMS", "PROPFIRMS_MANIFEST", "FirmLedger", "FirmRule", "FirmLedgerError", "pinned_digests",
           "source_revision", "vendored_firms"]
