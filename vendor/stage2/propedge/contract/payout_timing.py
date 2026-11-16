"""When a funded account's payout request is made, against Topstep's 5:00 PM CT day boundary.

Topstep, payout policy (help centre 8284233): "A request submitted after 5:00 PM CT belongs to the next trading day —
that day becomes the Payout request day and is excluded from the new cycle." The page's example: "A Payout request
submitted at 5:59 PM CT on Monday belongs to the Tuesday trading session… The new cycle begins on Wednesday." The
ledger's reading of the same page on 2026-09-22 (`config/rules.yaml`, `xfa_std_winning_days`): "A day locks in at 4:00 PM
CT. The trading day your Payout is requested doesn't count toward your next 5." The fidelity audit of 2026-09-27
(`docs/audits/topstep_rule_fidelity_2026-09-27.md`, finding 6) found the engine requesting at the close of the eligible
day and counting the next day toward the new cycle: one winning day per cycle optimistic.

Two timings:

* `REQUEST_AFTER_5PM` -- the default for the campaign (`lockstep.FundedAccount`, `simulate_lockstep_path`,
  `simulate_lockstep_campaign`, `gate.run_gate`). The request is made after the eligible day's 4:00 PM CT lock, after
  5:00 PM CT, so it belongs to the next trading day. That day is the Payout request day: the account may trade it, its
  P&L moves the balance and the MLL as any day's does, but it does not count toward the new cycle -- not as a winning
  day (Standard path), not as a trading day, and not in the net profit or the best day of the Consistency path.
* `REQUEST_4_TO_5PM` -- the engine's old timing and the vendored engine's (`propsim.simulate_xfa`): the eligible day is
  itself the request day and the next trading day counts toward the new cycle. It REQUIRES THE OPERATOR TO SUBMIT
  BETWEEN 4:00 AND 5:00 PM CT ON THE ELIGIBLE DAY; a protocol that assumes it must say so. The functions that reproduce
  the vendored engine (`funded_dated.simulate_xfa_dated`, `reinvest.outcomes_from_adapter`) keep it as their default,
  because reproducing the engine bit for bit is what licenses them.

What is assumed, because no official page states it (the audit's last line: "Nothing states whether a payout moves the
MLL and the balance at request or at approval"): the engine's convention is kept. The balance falls by the request, and
the MLL is set to $0, when the request is made -- at the eligible day's close, before the request day's session trades.
The payout stays dated on the eligible day (the evening it is submitted) and its cash arrives `payout_lag_days` after
that, as before; only the cycle accounting moves. The net profit since the last payout (Standard's "$0.01 since your
last Payout") includes the request day, which is profit made after the request.
"""
from __future__ import annotations

REQUEST_AFTER_5PM = "after_5pm_ct"
REQUEST_4_TO_5PM = "4_to_5pm_ct"
PAYOUT_TIMINGS = (REQUEST_AFTER_5PM, REQUEST_4_TO_5PM)

#: The campaign's default: the rule as written for a request made after 5:00 PM CT (8284233).
DEFAULT_PAYOUT_TIMING = REQUEST_AFTER_5PM
#: The vendored engine's timing, kept by the functions that reproduce it.
ENGINE_PAYOUT_TIMING = REQUEST_4_TO_5PM

#: What each timing means, for provenance and reports.
PAYOUT_TIMING_NOTES = {
    REQUEST_AFTER_5PM: ("request made after 5:00 PM CT on the eligible day: the next trading day is the Payout request "
                        "day and does not count toward the new cycle (8284233)"),
    REQUEST_4_TO_5PM: ("request made between 4:00 and 5:00 PM CT on the eligible day: requires the operator to submit "
                       "in that hour; the next trading day counts toward the new cycle (8284233)"),
}


def check_payout_timing(timing: str) -> str:
    """Return `timing` if it is a known payout timing; raise otherwise."""
    if timing not in PAYOUT_TIMINGS:
        raise ValueError(f"payout_timing must be one of {PAYOUT_TIMINGS}, got {timing!r}")
    return timing


def request_day_excluded(timing: str) -> bool:
    """Whether the trading day after the eligible day is the Payout request day, left out of the new cycle."""
    return check_payout_timing(timing) == REQUEST_AFTER_5PM


__all__ = [
    "REQUEST_AFTER_5PM",
    "REQUEST_4_TO_5PM",
    "PAYOUT_TIMINGS",
    "DEFAULT_PAYOUT_TIMING",
    "ENGINE_PAYOUT_TIMING",
    "PAYOUT_TIMING_NOTES",
    "check_payout_timing",
    "request_day_excluded",
]
