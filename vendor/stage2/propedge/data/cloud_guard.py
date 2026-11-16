"""Refuse any cloud run that reaches the confirmation window without authorisation.

`propedge/data/window.py` guards data that arrives *here*. This module guards data touched
*there* -- a backtest launched on QuantConnect reads whatever span its algorithm declares, and
nothing in this repository sees those bars. So the check has to happen before the run starts, on
the algorithm's declared dates.

It is used by two callers that must agree:

  * `scripts/hooks/qc_window_guard.py`, a PreToolUse hook on the MCP tools that upload code or
    create backtests;
  * any API/LEAN script in `analysis/`, which calls `assert_cloud_run_allowed` directly.

One implementation, so the agent route and the scripted route cannot drift apart.

**It fails closed.** An algorithm whose dates cannot be found is refused, not waved through.
A backtest with no `SetStartDate` runs from the dataset's beginning, which is the worst case, and
"I could not find a date" is not evidence that the date is safe.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from propedge.data.window import DEVELOPMENT_END, DEVELOPMENT_END_SOURCE

#: `self.set_start_date(2010, 1, 4)`, `self.SetStartDate(2010,1,4)`, and the C# forms.
_DATE_CALL = re.compile(
    r"\b(?:set_?start_?date|set_?end_?date)\s*\(\s*"
    r"(\d{4})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)",
    re.IGNORECASE,
)
_WHICH = re.compile(r"\bset_?(start|end)_?date\b", re.IGNORECASE)

REGISTRY = Path(__file__).resolve().parents[2] / "prereg" / "REGISTRY.md"
#: Statuses whose pre-registration may authorise a confirmation-window run.
RUNNABLE = ("registered", "running")


class CloudRunRefused(RuntimeError):
    """Raised when a cloud run would read the confirmation window without authorisation."""


@dataclass(frozen=True)
class CloudRunDates:
    start: date | None
    end: date | None

    @property
    def known(self) -> bool:
        return self.start is not None and self.end is not None


def extract_dates(code: str) -> CloudRunDates:
    """Pull the declared start and end dates out of algorithm source.

    Returns `None` for either date it cannot find. It does not guess: a missing date is
    reported as missing so the caller can fail closed.
    """
    start = end = None
    for m in _DATE_CALL.finditer(code or ""):
        kind = _WHICH.search(m.group(0))
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if kind and kind.group(1).lower() == "start":
            start = d if start is None else min(start, d)
        else:
            end = d if end is None else max(end, d)
    return CloudRunDates(start, end)


def confirmation_run_authorised(prereg_id: str | None) -> bool:
    """True only if `prereg_id` is a row in the registry with a runnable status.

    The registry is the same file `propedge/backtest/harness.py` reads, so a confirmation run
    cannot be authorised here by a pre-registration the harness would reject.
    """
    if not prereg_id:
        return False
    if not REGISTRY.exists():
        return False
    wanted = prereg_id.strip().lower()
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0].lower() == wanted and cells[3].lower() in RUNNABLE:
            return True
    return False


def assert_cloud_run_allowed(
    code: str,
    *,
    prereg_id: str | None = None,
    what: str = "cloud backtest",
) -> CloudRunDates:
    """Raise `CloudRunRefused` unless this run stays inside the development window.

    Args:
        code: the algorithm source about to be uploaded or run.
        prereg_id: a registered pre-registration authorising a confirmation-window run.
        what: named in the error.

    Returns:
        The dates found, when the run is allowed.
    """
    dates = extract_dates(code)
    if not dates.known:
        missing = [n for n, v in (("start", dates.start), ("end", dates.end)) if v is None]
        raise CloudRunRefused(
            f"{what}: could not find {' and '.join(missing)} date(s) in the algorithm. "
            f"REFUSED. A backtest with no declared start runs from the beginning of the "
            f"dataset, so a missing date is the worst case, not a safe one. Generate the "
            f"algorithm from the repository template, whose dates come from "
            f"propedge/data/window.py."
        )
    if dates.end < DEVELOPMENT_END and dates.start < DEVELOPMENT_END:
        return dates
    if confirmation_run_authorised(prereg_id):
        return dates
    raise CloudRunRefused(
        f"{what}: the run spans {dates.start.isoformat()} to {dates.end.isoformat()}, which "
        f"reaches the confirmation window opening {DEVELOPMENT_END.isoformat()}. REFUSED: no "
        f"registered pre-registration authorises a confirmation run"
        + (f" (prereg_id={prereg_id!r} is not a runnable row in prereg/REGISTRY.md)"
           if prereg_id else " and none was supplied")
        + f". Development runs must end on or before "
        f"{(DEVELOPMENT_END.toordinal() - 1) and date.fromordinal(DEVELOPMENT_END.toordinal() - 1).isoformat()}. "
        f"{DEVELOPMENT_END_SOURCE}"
    )
