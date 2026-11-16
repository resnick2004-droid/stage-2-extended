"""The development/confirmation boundary, enforced in code rather than remembered.

D-49 split the design: a fully specified combination may use the **entire** post-publication
window for confirmation, and development is whatever precedes it. The boundary is
**2025-07-01** (D-237). Everything before it is development and may be measured on freely;
everything from that date on is confirmation and **must not be touched** until the
pre-registered test runs.

D-237 moved it from 2020-01-01 (D-144) at the operator's request, so that development includes today's markets
(2020-2025) and confirmation is the held-back year from 2025-07-01, then data as it arrives. Every kit up to R088 was made
under D-144's boundary and keeps it (`D144_DEVELOPMENT_END`), so each stays exactly the code that ran.

Until D-144 the boundary was 2014-05-28, Stage 2B's post-publication date (D-49, D-72). D-144
moved it forward, before anything dated from 2014-05-28 had been looked at, so that stage two's
own models are built on a market nearer today's and confirmed on a fully modern one. Every kit
up to R046 and every result recorded before D-144 was made under the old boundary; those kits
keep it (`PREVIOUS_DEVELOPMENT_END`), so each stays exactly the code that ran.

This module exists because that boundary is the one thing in the whole design that cannot be
recovered once broken. A leaked look at confirmation data does not announce itself: the numbers
still compute, the tests still pass, and the only evidence is a date range nobody checked. So
the check is a function that raises, not a note in a document.

Use `assert_development_only(...)` on any frame or index before it reaches a measurement, and
`DEVELOPMENT_END` wherever a request window is constructed.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable

#: The first instant of the confirmation window (D-49, moved by D-144 and D-237). Development is strictly
#: before this.
DEVELOPMENT_END = date(2025, 7, 1)

#: D-144's boundary, before D-237 moved it: kits R047-R088 embed it (`propedge.data.run_kit.KITS_BEFORE_D237`).
D144_DEVELOPMENT_END = date(2020, 1, 1)

#: The boundary before D-144: Stage 2B's post-publication date (D-49, D-72). Kits generated under
#: it keep it embedded (`propedge.data.run_kit.KITS_BEFORE_D144`).
PREVIOUS_DEVELOPMENT_END = date(2014, 5, 28)

#: Where the confirmation window came from, named in every refusal.
DEVELOPMENT_END_SOURCE = (
    "D-237 (operator, 2026-10-02): confirmation opens 2025-07-01; D-144 had it at 2020-01-01, and before D-144 it "
    "opened 2014-05-28, Stage 2B's supplied post-publication date (D-35, D-49), NOT verified by this repository."
)


class ConfirmationWindowLeak(RuntimeError):
    """Raised when data at or after `DEVELOPMENT_END` reaches a development-period measurement.

    This is not a validation nicety. Measuring sd (D-43) on confirmation data would make the
    confirmation test an in-sample test while leaving every number looking identical, which is
    the one failure the pre-registration discipline cannot detect after the fact.
    """


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    text = str(value)
    return datetime.fromisoformat(text.replace("Z", "+00:00")).date()


def is_development(value) -> bool:
    """True if `value` falls strictly before the confirmation window opens."""
    return _as_date(value) < DEVELOPMENT_END


def assert_development_only(timestamps: Iterable, *, what: str = "measurement") -> None:
    """Raise `ConfirmationWindowLeak` if any timestamp is on or after `DEVELOPMENT_END`.

    Args:
        timestamps: anything iterable of dates, datetimes or ISO strings. A pandas
            `DatetimeIndex` or a Series works.
        what: named in the error, so the message says which measurement was about to leak.
    """
    latest = None
    count = 0
    for ts in timestamps:
        d = _as_date(ts)
        if d >= DEVELOPMENT_END:
            count += 1
            if latest is None or d > latest:
                latest = d
    if count:
        raise ConfirmationWindowLeak(
            f"{what}: {count} observation(s) fall on or after the confirmation boundary "
            f"{DEVELOPMENT_END.isoformat()}, the latest {latest.isoformat()}. Development-period "
            f"measurements (D-43) must use data strictly before it. {DEVELOPMENT_END_SOURCE}"
        )


def development_request_window(start: date | str) -> tuple[date, date]:
    """The (start, end) a data request may ask for, clipped to the development period.

    `end` is the last date that may be requested -- the day before the boundary -- so a caller
    that passes this straight to a vendor API cannot request confirmation data by construction.
    """
    s = _as_date(start)
    if s >= DEVELOPMENT_END:
        raise ConfirmationWindowLeak(
            f"requested start {s.isoformat()} is on or after the confirmation boundary "
            f"{DEVELOPMENT_END.isoformat()}; there is no development period after it."
        )
    from datetime import timedelta

    return s, DEVELOPMENT_END - timedelta(days=1)
