"""Loader for `config/data_sources.yaml` -- facts about the QuantConnect data source (D-78).

This is the data-source counterpart of `propedge/contract/rules.py`, with the same gate: a fact
whose status is not `read` cannot be used. `DataSources.value(key)` raises `UnreadFactError`
unless the fact was read **with its provenance** -- what was read, how (method and identifier),
when, and by whom.

It is deliberately a separate file from the rules ledger. The ledger's evidence is an article on
the Topstep help centre; a dataset's start date or roll rule has no such article, and its
evidence is a tool call or a scripted API run. Mixing them would let one kind of evidence pass
for the other.

`requires` fixes the method before the fact is read: one method, or a list of acceptable ones.
Dataset facts accept `api_script` or `manual_run` (D-82) -- both are committed code with a
manifest -- and never `mcp_tool`, because an answer whose only provenance is an agent
conversation has no manifest (`docs/QUANTCONNECT_MCP.md`). Loading **refuses** a `read` fact whose provenance is incomplete or
whose method differs from `requires`, so a half-recorded fact fails at load, not at use.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from propedge import CONFIG_DIR

READ = "read"
UNREAD = "unread"
VALID_STATUSES = {READ, UNREAD}

MCP_TOOL = "mcp_tool"
API_SCRIPT = "api_script"
MANUAL_RUN = "manual_run"          # a kit in runs/<run-id>/, run by hand and ingested (D-82)
VALID_METHODS = {MCP_TOOL, API_SCRIPT, MANUAL_RUN}

#: Fields a `read` fact must carry. A fact without any one of them has no provenance.
PROVENANCE_FIELDS = ("what_read", "method", "identifier", "date_read", "read_by")

ROOT = Path(__file__).resolve().parents[2]


class UnreadFactError(RuntimeError):
    """Raised when code asks for a data-source fact that has not been read."""


class UnknownFactError(KeyError):
    """Raised when code asks for a fact that is not in the record at all."""


class ProvenanceError(ValueError):
    """Raised at load when a fact marked `read` does not carry its full provenance."""


@dataclass(frozen=True)
class FactEntry:
    """One row of the data-source record."""

    key: str
    question: str
    requires: tuple[str, ...]
    value: Any
    status: str
    what_read: str | None = None
    method: str | None = None
    identifier: str | None = None
    date_read: str | None = None
    read_by: str | None = None
    note: str | None = None

    @property
    def is_read(self) -> bool:
        return self.status == READ

    def citation(self) -> str:
        """Method, identifier and date, for a report or a result manifest."""
        bits = [str(b) for b in (self.method, self.identifier, self.date_read) if b]
        return " | ".join(bits) if bits else "(not read)"


def _validate(key: str, body: dict, path: Path) -> None:
    status = body.get("status")
    if status not in VALID_STATUSES:
        raise ValueError(
            f"fact {key!r} in {path} has status {status!r}; expected one of {sorted(VALID_STATUSES)}"
        )
    requires = _requires(body.get("requires"))
    if not requires or not set(requires) <= VALID_METHODS:
        raise ValueError(
            f"fact {key!r} in {path} requires {body.get('requires')!r}; expected one or more of "
            f"{sorted(VALID_METHODS)}"
        )
    if status == UNREAD:
        if body.get("value") is not None:
            raise ProvenanceError(
                f"fact {key!r} is unread but carries a value ({body['value']!r}). A value with no "
                "provenance is exactly what this record exists to prevent."
            )
        return
    missing = [f for f in PROVENANCE_FIELDS if not body.get(f)]
    if body.get("value") is None:
        missing.insert(0, "value")
    if missing:
        raise ProvenanceError(
            f"fact {key!r} in {path} is marked read but lacks {missing}. A read fact records what "
            "was read, how (method and identifier), when, and by whom."
        )
    if body["method"] not in requires:
        raise ProvenanceError(
            f"fact {key!r} requires method {' or '.join(requires)} but was read by "
            f"{body['method']!r}. The route is fixed before the fact is read (D-77, D-78, D-82)."
        )
    if body["method"] == MANUAL_RUN:
        kit = str(body["identifier"]).split()[0]
        if not (ROOT / kit / "kit.json").is_file():
            raise ProvenanceError(
                f"fact {key!r} cites manual run {kit!r}, which is not a run kit in this "
                "repository. A manual_run identifier opens with runs/<run-id>."
            )
    if body["method"] == API_SCRIPT:
        script = str(body["identifier"]).split()[0]
        if not (ROOT / script).is_file():
            raise ProvenanceError(
                f"fact {key!r} cites script {script!r}, which is not a file in this repository. "
                "An api_script identifier opens with the committed script's path."
            )


def _requires(raw) -> tuple[str, ...]:
    if isinstance(raw, str):
        return (raw,)
    if isinstance(raw, (list, tuple)):
        return tuple(str(r) for r in raw)
    return ()


class DataSources:
    """The data-source record, with the read-status gate on `value()`."""

    def __init__(self, entries: dict[str, FactEntry], meta: dict[str, Any], path: Path):
        self._entries = entries
        self.meta = meta
        self.path = path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "DataSources":
        path = Path(path) if path is not None else CONFIG_DIR / "data_sources.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"data-source record not found: {path}")
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries: dict[str, FactEntry] = {}
        for key, body in (doc.get("facts") or {}).items():
            if not isinstance(body, dict):
                raise ValueError(f"fact {key!r} in {path} is not a mapping")
            _validate(key, body, path)
            date_read = body.get("date_read")
            entries[key] = FactEntry(
                key=key,
                question=body.get("question") or "",
                requires=_requires(body["requires"]),
                value=body.get("value"),
                status=body["status"],
                what_read=body.get("what_read"),
                method=body.get("method"),
                identifier=body.get("identifier"),
                # PyYAML parses an unquoted date into datetime.date; one type for every consumer.
                date_read=None if date_read is None else str(date_read),
                read_by=body.get("read_by"),
                note=body.get("note"),
            )
        return cls(entries, doc.get("meta") or {}, path)

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __iter__(self) -> Iterator[FactEntry]:
        return iter(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)

    def entry(self, key: str) -> FactEntry:
        """The full row, regardless of status. Inspection only -- never for computation."""
        try:
            return self._entries[key]
        except KeyError:
            raise UnknownFactError(
                f"no fact named {key!r} in {self.path}. Known: {', '.join(sorted(self._entries))}"
            ) from None

    def unread(self) -> list[FactEntry]:
        return [e for e in self._entries.values() if not e.is_read]

    def value(self, key: str) -> Any:
        """The value of a fact, **only** if it was read with provenance."""
        entry = self.entry(key)
        if not entry.is_read:
            raise UnreadFactError(
                f"data-source fact {key!r} has not been read: {entry.question}. It must be read "
                f"by {' or '.join(entry.requires)} and recorded in {self.path.name} with what was read, the "
                f"method and identifier, the date and the reader before anything may use it."
            )
        return entry.value
