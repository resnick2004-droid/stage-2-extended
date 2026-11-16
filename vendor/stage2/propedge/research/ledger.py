"""The P1 trial ledger (D-197) and D-189's trial count N.

`prereg/models.yaml` records every model, registration, withdrawal, protocol option, screen and atlas family this
stage ran or declared: what data it touched (markets, windows, bar resolution), how many trials it holds and which
selection pools it sat in. D-189 counts from it:

    N = the registration's own k
        + every ledger row that (a) read a window overlapping the registration's development window, in one of its
          markets, at its bar resolution, and (b) sat in the selection pool the model was chosen from;
    a row counts once unless its internal tests were themselves selection steps (`count_tests: true`), when each
    counted test -- on the registration's markets -- is a trial.

The registration's own model rows (its registrations, withdrawn or not, and its own screen when the registration's k
already counts it) are not counted twice: a row whose `model` is the registration's model and whose `in_k` is true is
covered by k. Everything else in the pool counts, the model's own screen included unless `in_k` says otherwise.

The ledger is data, checked here (`load_ledger`) and by `tests/test_ledger.py`; the counting judgements -- which pool a
row sat in, whether its tests were selection steps -- are written into each row with their reason, so N can be
recounted by hand from the file alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import yaml

from propedge import REPO_ROOT

LEDGER_FILE = REPO_ROOT / "prereg" / "models.yaml"
#: `model` rows name a model and the pool it was chosen from (`chosen_from`); they hold no trials themselves. A model
#: that was searched on data without a registration (C-007, the gap and open-reversion models, FV1) has its search as a
#: `development` row.
KINDS = ("model", "registration", "withdrawn_registration", "development", "screen", "atlas_family", "first_look",
         "outcome_check", "protocol_option", "hypothetical", "diagnostic")
RESOLUTIONS = ("minute", "daily", "none")
ROW_KEYS = ("id", "kind", "title", "decisions", "date", "resolution", "windows", "markets", "count_tests", "pools",
            "reason")


class LedgerError(ValueError):
    """The ledger file is malformed; N cannot be counted from it."""


def _d(x: Any) -> date:
    return x if isinstance(x, date) else date.fromisoformat(str(x))


@dataclass(frozen=True)
class Row:
    id: str
    kind: str
    title: str
    resolution: str
    windows: tuple[tuple[date, date], ...]
    markets: dict[str, int]                 # market -> internal tests on it (1 for a single look)
    count_tests: bool
    pools: tuple[str, ...]
    reason: str
    model: str | None = None
    in_k: bool = False
    k: int | None = None
    chosen_from: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def overlaps(self, window: tuple[date, date]) -> bool:
        lo, hi = window
        return any(a <= hi and b >= lo for a, b in self.windows)


@dataclass(frozen=True)
class Ledger:
    pools: dict[str, dict[str, Any]]
    rows: tuple[Row, ...]

    def row(self, row_id: str) -> Row:
        for r in self.rows:
            if r.id == row_id:
                return r
        raise KeyError(f"no ledger row {row_id!r}")

    def model(self, model_id: str) -> Row:
        for r in self.rows:
            if r.kind == "model" and r.id == model_id:
                return r
        raise KeyError(f"no model row {model_id!r} in the ledger; add it, with the pool it was chosen from, before "
                       "registering (D-189, D-197)")


def load_ledger(path: Path | None = None) -> Ledger:
    """Read and check the ledger: every row has the keys, a known kind and resolution, well-formed windows and market
    counts, and names only pools the file declares; ids are unique; every model names a declared pool."""
    p = Path(path) if path is not None else LEDGER_FILE
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "pools" not in doc or "rows" not in doc:
        raise LedgerError(f"{p.name}: needs top-level 'pools' and 'rows'")
    pools = {str(x["id"]): dict(x) for x in doc["pools"]}
    rows, seen = [], set()
    for raw in doc["rows"]:
        missing = [k for k in ROW_KEYS if k not in raw]
        rid = str(raw.get("id", "?"))
        if missing:
            raise LedgerError(f"row {rid!r}: missing {missing}")
        if rid in seen:
            raise LedgerError(f"row {rid!r} appears twice")
        seen.add(rid)
        if raw["kind"] not in KINDS:
            raise LedgerError(f"row {rid!r}: kind {raw['kind']!r} not one of {KINDS}")
        if raw["resolution"] not in RESOLUTIONS:
            raise LedgerError(f"row {rid!r}: resolution {raw['resolution']!r} not one of {RESOLUTIONS}")
        wins = []
        for w in raw["windows"] or []:
            a, b = _d(w[0]), _d(w[1])
            if a > b:
                raise LedgerError(f"row {rid!r}: window {a}..{b} ends before it starts")
            wins.append((a, b))
        mk = {str(m): int(n) for m, n in (raw["markets"] or {}).items()}
        if any(n < 1 for n in mk.values()):
            raise LedgerError(f"row {rid!r}: every market listed holds at least one test")
        if (raw["resolution"] == "none") != (not wins):
            raise LedgerError(f"row {rid!r}: a row reads windows exactly when its resolution is not 'none'")
        bad = [x for x in raw["pools"] or [] if x not in pools]
        if bad:
            raise LedgerError(f"row {rid!r}: undeclared pool(s) {bad}")
        if raw["kind"] == "model" and raw.get("chosen_from") not in pools:
            raise LedgerError(f"model {rid!r}: chosen_from must name a declared pool")
        if not str(raw["reason"]).strip():
            raise LedgerError(f"row {rid!r}: the reason for its pools and count is written down")
        known = set(ROW_KEYS) | {"model", "in_k", "k", "chosen_from"}
        rows.append(Row(id=rid, kind=raw["kind"], title=str(raw["title"]), resolution=raw["resolution"],
                        windows=tuple(wins), markets=mk, count_tests=bool(raw["count_tests"]),
                        pools=tuple(raw["pools"] or ()), reason=str(raw["reason"]),
                        model=raw.get("model"), in_k=bool(raw.get("in_k", False)),
                        k=int(raw["k"]) if raw.get("k") is not None else None, chosen_from=raw.get("chosen_from"),
                        extra={k: v for k, v in raw.items() if k not in known}))
    return Ledger(pools=pools, rows=tuple(rows))


def count_n(ledger: Ledger, *, model: str, k: int, markets: Sequence[str], window: tuple[Any, Any],
            resolution: str = "minute") -> dict[str, Any]:
    """D-189's N for a registration of `model` with its own `k`, on `markets` over the development `window` at
    `resolution`: {'N', 'k', 'pool', 'rows': [(row id, trials counted, markets counted)]}."""
    pool = ledger.model(model).chosen_from
    win = (_d(window[0]), _d(window[1]))
    ms = {str(m) for m in markets}
    counted = []
    for r in ledger.rows:
        if r.kind == "model" or pool not in r.pools:
            continue
        if r.model == model and r.in_k:
            continue                                            # covered by the registration's own k
        if r.resolution != resolution or not r.overlaps(win):
            continue
        hit = {m: n for m, n in r.markets.items() if m in ms}
        if not hit:
            continue
        trials = sum(hit.values()) if r.count_tests else 1
        counted.append((r.id, int(trials), sorted(hit)))
    return {"N": int(k) + sum(t for _, t, _ in counted), "k": int(k), "pool": pool, "rows": counted}


def count_for_registration(ledger: Ledger, registration: str) -> dict[str, Any]:
    """N for a registration row of the ledger (its model, k, markets, development window and resolution)."""
    r = ledger.row(registration)
    if r.kind not in ("registration", "withdrawn_registration") or r.model is None or r.k is None:
        raise LedgerError(f"{registration!r} is not a registration row with a model and a k")
    dev = r.extra.get("development_window")
    if not dev:
        raise LedgerError(f"{registration!r}: no development_window")
    return count_n(ledger, model=r.model, k=r.k, markets=list(r.extra.get("registered_markets") or r.markets),
                   window=(dev[0], dev[1]), resolution=r.extra.get("registered_resolution", "minute"))


__all__ = ["LEDGER_FILE", "KINDS", "RESOLUTIONS", "LedgerError", "Row", "Ledger", "load_ledger", "count_n",
           "count_for_registration"]
