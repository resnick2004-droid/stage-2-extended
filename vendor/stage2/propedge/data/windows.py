"""Per-market data windows (R4, D-459): what a read of a market's trading days is allowed to touch, by purpose.

`config/windows.yaml` declares, for each market, its development window, any held-back windows already read (spent),
its unread confirmation window and its reserve. `assert_readable` raises `ConfirmationWindowLeak` -- the error
`propedge.data.window` raises for D-237's global boundary -- when a requested span reaches a day its purpose may not
read. This is the per-market tightening of D-237: the global boundary still holds everywhere it is enforced, and a
market whose declared development ends earlier (GC) is held to its own.

Purposes:

* ``development`` -- the market's development windows only.
* ``exploratory`` -- development and spent windows (a study of data already read, labelled exploratory).
* ``confirmation`` -- development, spent and the market's confirmation window, and only with the id of a pre-registration
  that `prereg/REGISTRY.md` lists as registered (not complete, not abandoned) and that names this market's window in
  `config/windows.yaml`'s ``registered_reads``; the reserve never.

A reserved window is read by nothing until a decision row turns it into a confirmation window.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR
from propedge.data.window import ConfirmationWindowLeak, _as_date

WINDOWS_PATH = CONFIG_DIR / "windows.yaml"
STATUSES = ("development", "spent", "confirmation", "reserved")
PURPOSES = {"development": ("development",), "exploratory": ("development", "spent"),
            "confirmation": ("development", "spent", "confirmation")}


@dataclass(frozen=True)
class Window:
    market: str
    name: str
    status: str
    start: date
    end: date | None
    read_by: tuple[str, ...] = ()

    def holds(self, day: date) -> bool:
        return self.start <= day and (self.end is None or day <= self.end)


def _date(x: Any) -> date | None:
    return None if x is None else _as_date(x)


@lru_cache(maxsize=4)
def _load(path: str) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load(path: Path | str = WINDOWS_PATH) -> dict[str, tuple[Window, ...]]:
    """Each market's windows, in date order, checked: known statuses, no gap, no overlap, at most one open end (last)."""
    cfg = _load(str(path))
    out: dict[str, tuple[Window, ...]] = {}
    for market, spec in (cfg.get("markets") or {}).items():
        ws = tuple(sorted((Window(market=str(market), name=str(w["name"]), status=str(w["status"]),
                                  start=_date(w["start"]), end=_date(w.get("end")),
                                  read_by=tuple(str(x) for x in (w.get("read_by") or ())))
                           for w in spec["windows"]), key=lambda w: w.start))
        for w in ws:
            if w.status not in STATUSES:
                raise ValueError(f"{market} {w.name}: unknown status {w.status!r}")
            if w.end is not None and w.end < w.start:
                raise ValueError(f"{market} {w.name}: ends before it starts")
        for a, b in zip(ws, ws[1:]):
            if a.end is None:
                raise ValueError(f"{market}: {a.name} is open-ended but {b.name} follows it")
            if (b.start - a.end).days != 1:
                raise ValueError(f"{market}: {a.name} ends {a.end} and {b.name} starts {b.start} -- windows must be "
                                 "contiguous calendar days, with no gap and no overlap")
        out[str(market)] = ws
        for alias in [spec.get("micro")] if spec.get("micro") else []:
            out[str(alias)] = ws
    return out


def windows_of(market: str, path: Path | str = WINDOWS_PATH) -> tuple[Window, ...]:
    ws = load(path)
    if market not in ws:
        raise ConfirmationWindowLeak(f"{market}: no windows are declared in config/windows.yaml (R4, D-459); a market "
                                     "is read only after its windows are declared")
    return ws[market]


def window_of(market: str, day: Any, path: Path | str = WINDOWS_PATH) -> Window:
    d = _as_date(day)
    for w in windows_of(market, path):
        if w.holds(d):
            return w
    first = windows_of(market, path)[0]
    raise ConfirmationWindowLeak(f"{market} {d}: before the first declared window ({first.name} from {first.start})")


def registered_reads(path: Path | str = WINDOWS_PATH) -> dict[str, dict[str, str]]:
    """`registered_reads` in the yaml: {prereg id: {market: window name}} -- added by a decision row at registration."""
    return {str(k): {str(m): str(w) for m, w in (v or {}).items()}
            for k, v in (_load(str(path)).get("registered_reads") or {}).items()}


def _registered(prereg: str) -> bool:
    from propedge.data.cloud_guard import confirmation_run_authorised
    return bool(confirmation_run_authorised(prereg))


def readable(market: str, purpose: str, *, prereg: str | None = None,
             path: Path | str = WINDOWS_PATH) -> tuple[Window, ...]:
    """The windows of `market` a read for `purpose` may touch."""
    if purpose not in PURPOSES:
        raise ValueError(f"purpose must be one of {sorted(PURPOSES)}, not {purpose!r}")
    allowed = PURPOSES[purpose]
    ws = windows_of(market, path)
    out = []
    for w in ws:
        if w.status not in allowed:
            continue
        if w.status == "confirmation":
            if not prereg:
                continue
            if registered_reads(path).get(prereg, {}).get(market) != w.name and \
                    registered_reads(path).get(prereg, {}).get(_root_alias(market, path)) != w.name:
                continue
            if not _registered(prereg):
                continue
        out.append(w)
    return tuple(out)


def _root_alias(market: str, path: Path | str) -> str:
    cfg = _load(str(path))
    for root, spec in (cfg.get("markets") or {}).items():
        if spec.get("micro") == market:
            return str(root)
    return market


def assert_readable(market: str, start: Any, end: Any, purpose: str, *, prereg: str | None = None,
                    path: Path | str = WINDOWS_PATH, what: str = "read") -> None:
    """Raise `ConfirmationWindowLeak` unless every day from `start` to `end` (inclusive) lies in a window `purpose` may
    read for `market` -- a read past a window raises (R4's acceptance)."""
    s, e = _as_date(start), _as_date(end)
    if e < s:
        raise ValueError(f"{what}: {e} is before {s}")
    ok = readable(market, purpose, prereg=prereg, path=path)
    day = s
    for w in windows_of(market, path):                     # walk the declared windows across [s, e]
        if w.end is not None and w.end < day:
            continue
        if not w.holds(day):
            break
        if w not in ok:
            raise ConfirmationWindowLeak(
                f"{what} on {market} reaches {max(day, w.start)} in the {w.status} window {w.name!r} "
                f"({w.start} to {w.end or 'open'}), which a {purpose} read"
                + (f" under {prereg}" if prereg else "") + " may not touch (config/windows.yaml, R4, D-459)")
        if w.end is None or e <= w.end:
            return
        day = date.fromordinal(w.end.toordinal() + 1)
    raise ConfirmationWindowLeak(f"{what} on {market} reaches {day}, outside every declared window")


def clear_cache() -> None:
    _load.cache_clear()
