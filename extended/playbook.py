"""The restart plan's Wave 3.5: the playbook a user trades a carried design from by hand, the one-trade alert, and the
"not offered" notice (CHARTER 3.5: "The output is a playbook ... plus the exact alert format, so that it can be traded
by hand"; E-221, the operator's O-4 ruling). Corrective cycle 2 and the final read's fixes (the red team's BUILD_W35,
BUILD_W35_v2 and BUILD_W35_c2 notes, the lead's rulings).

    from extended import playbook as PB
    carried = PB.load_carried("prereg/<design>_carried.json")          # the carrying record; everything checked
    page = PB.render_playbook(carried)                                  # -> Rendered: .text, .pieces
    msg = PB.render_offer(carried, "pm_brk", hist, i, at, sources, router, accounts)  # the alert, or a notice
    note = PB.render_trade(carried, routed)                             # a scheduled (coin-sided) trade: not offered

**Hand entry only** (CLAUDE.md; DIRECTIVE Part 1: no automated or API order entry, it gets prop accounts banned). The
playbook and the alert are plain text for a person to read and act on by hand. Nothing here places, sends, schedules or
formats an order for a machine: no network, no broker, no file written, no process but read-only `git` at load
(`extended.pin_order`: `log`, `cat-file`, `merge-base`). `Rendered.pieces` (where each
value came from) is for the tests' tracing only and is never to be exported as an order record. An RL3 kind's tickets
are rested by hand as plain orders in one account, each with the platform's own Auto-OCO bracket set to the
component's stop and target, the other cancelled by hand when one fills; a double fill closes every position and
cancels every working order at once (C2-6, C3-6: no Topstep page says TopstepX holds two entry orders as
one-cancels-other; TopstepX articles 14434175 and 8765442, read 2026-11-21).

**Two pinned files** (C2-5). The **declaration** (`prereg/<design>_playbook.json`: the design, its components, side
rules, margin and account policy, no registration and no carrying row) is pinned as `` `<path>` sha256 `<hex>` `` in a
row **before** the no-harm row, so the side rules are fixed before the floor is read; it needs no registration then.
The **carrying record** (`prereg/<design>_carried.json`: the design id, the declaration's path and sha256, the
registration id, the carrying row, and the joint held-out test's accepted result file with its script and family) is
pinned in the carrying row, after the no-harm row, which also pins that held-out file and holds the structured token
`carried: <design id> @ <declaration sha256> -- <registration> -- <held-out result sha256>` (C2-7, C3-7) and no
negated, conditional, withdrawn or reverted wording. Exactly one row of the log states the no-harm margin, and it comes
before the declaration's first pin (C3-5). Both are JSON with duplicate keys, NaN and Infinity refused; every cited row id is looked up; a row pinning one
path twice refuses.

**The two result files** (B-1, B-3; R-6, m-1), each accepted only when all hold: its CSV and its manifest are both
pinned in their row; its manifest is from a clean run of a named commit, not exploratory, written by the declared
script under the declaration's family (`prereg_id`), and its `parameters` carry this design's id, the convention, the
declaration's path and sha256; it passes `extended.results.verify_result` on one resolved path; it is not git-ignored
(the licence list); its columns are on the pinned list `RESULT_COLUMNS` (C2-8: a label column holding a number of the
price band refuses, on the tick grid or off it, with a unit or without; a figure or count column may hold any figure;
any other column refuses); every printed value is a bare finite number.
* **The no-harm floor** (`side.no_harm_file`, convention `no_harm_real_path`; the format the floor's runner must
  write): `parameters.margin` is the declaration's `side.margin`, which must equal the margin its `margin_row` pins
  (`` no-harm margin `<value>` ``, C2-1); for each component the rows `no_harm|search|<component>|side_rule`,
  `|margin`, `|trigger_composite`, `|coin_composite`. The playbook **recomputes** the pass and refuses a component that
  fails or is absent. Its run's commit must **descend from the commit that first pinned the declaration** and lie
  on HEAD's line (C2-2, C3-4, `extended.pin_order`): the floor read after the pin, in git, on the merged history.
  **The no-harm runner's brief** (C3-4): it refuses to run from a commit whose `DECISIONS.md` does not already pin the
  declaration.
* **The expected journey** (`expected.file`, convention `zero_edge`), under the same pin-order check (N-c3-3).
* **The joint held-out test's accepted result** (the record's `heldout_file`, convention `heldout_joint_test`): its
  `heldout|joint|<design id>|verdict` cell reads `accepted`.

**The windows** (C2-3) are what the evaluated designs' are: offsets from each session's local open, read per date by
`search_space.Space.windows_on` (the starts of `search_space.session_spans`, anchored to their local market times,
E-231 (3)), checked by `Space.check` (bounds over the search years, collisions, RL3's live slot, the closed window), and
built per date as `components.Design(day=...)`; a P-14 component's alerts are its window less L on each date,
clipped to P-14's span (17:00 to 14:00 CT, C3-2). NY is split at T2b (Q-188b, noon New York, `lever_space.ny_boundary`):
`ny_am` runs from the 08:30 CT open to the split, `ny_pm` from the split (its offsets count from it), and a component
whose window crosses noon is `ny`, the whole session from 08:30 CT (`components.session_bounds`).

**The side** (R-1, B-2). The playbook offers a side only as `trigger_sides.trigger_side` computes it, from an offer the
module **recomputes itself** from the day's bars cut at the alert, through the trigger's own `offers()`. A scheduled
trade is the evaluation's, coin-sided by construction: `render_trade` gives it the not-offered notice.

**The day** (B-5, N-c2-2). "Offered today" reads only what is known before the alert (`day_calendar.alert_context`):
FOMC and BLS days, a scheduled close, the previous **session by the calendar** (`day_calendar.prior_session`, C3-1: a
roll, a scheduled closure, a scheduled close on it, whether or not the store holds it), the declaration's dated news
record, and the bars closed by the alert. A component reading the previous day refuses as a data mismatch when the
bars' previous day is not that session: no role, side or void is computed from another day. The data-defect filters
are research-only. The live path (a declared live calendar, today's bars) is not built: dates after
the search years refuse.

**The account** (m-5, N-c2-1) is the router's pick (`router.Router.peek`, the declaration's rotation, for `firm=`;
under `by_component` the pools are the router's own, dealt each day over the design's components in window order,
`router.window_order`: a declaration holds no pools) among the accounts alive that day. **Dates** (B-6) are strict ISO. **Bar times** (m-6) are stated by the bar's stamp; every level
is defined by the bars it is made from (C2-9). A resting order's alert states the walker's void-at-live rule each
time the order is placed, and under an RL3 pair per ticket (C2-4, C3-3).

**Every number comes from an input, never from this file.** A rendered text is a sequence of pieces (`Piece`): a
template literal, which holds no digit, or a value, which names its transform and the input paths it is computed from
(`TRANSFORMS`). The same input gives byte-identical text.
"""
from __future__ import annotations

import csv
import fnmatch
import functools
import hashlib
import io
import json
import math
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extended import ROOT
from extended import components as C
from extended import day_calendar as DC
from extended import lever_space as LS
from extended import modes_terms as M
from extended import router as R
from extended import search_space as SS
from extended import trigger_sides as TS
from extended import triggers as T
from extended import walker as W

REQUIRED = ("design_id", "family", "firm", "plan", "instrument", "accounts", "side", "components", "rotation",
            "execution", "news_source", "news_windows", "void_rules", "research_filters", "void_dates",
            "session_anchors", "dates", "bankroll", "expected")
COMPONENT_KEYS = ("name", "session", "first", "last", "stop_ticks", "rr", "contracts", "latency", "side_rule", "trigger")
EXECUTION_KEYS = ("gap_minutes", "closed_window", "bls_clear", "limit_window_min", "flatten", "last_entry")
SIDE_KEYS = ("no_harm_row", "no_harm_file", "no_harm_script", "margin", "margin_row")
EXPECTED_TOP = ("file", "script", "rows")
EXPECTED_KEYS = ("label", "section", "block", "measure", "stat")
NEWS_KEYS = ("source", "release", "before", "after", "dates")
HASH = hashlib.sha256().name                          # the pins' and manifests' hash, by its library name
DECL_SHA_KEY = "declaration_" + HASH
RECORD_KEYS = ("design_id", "declaration", DECL_SHA_KEY, "registration", "row", "heldout_file", "heldout_script",
               "heldout_family")
P14_PARAMS = ("latency", "entry", "k")
ROW_LINE = re.compile(r"^\| (E-\d\d\d+) \|.*$", re.M)
PIN = re.compile(r"`([^`]+)` " + HASH + r" `([a-f\d]+)`")
#: an identifier carries no figure (m-7, C2-10): letters, '_' and '-', a digit only in one trailing index `_v<d>`;
#: matched in full (no trailing newline)
IDENT = re.compile(r"[A-Za-z][A-Za-z_-]*(?:_v\d)?")
ISO = re.compile(r"\d\d\d\d-\d\d-\d\d")
BARE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
NUMBER_IN = re.compile(r"\d[\d,]*(?:\.\d+)?")
DIGIT = re.compile(r"\d")
SHA_LEN = len(hashlib.sha256().hexdigest())
#: the carrying row's structured token (C2-7) and the wording it may not hold
CARRIED_TOKEN = re.compile(r"carried: (\S+) @ ([a-f\d]+) -- (\S+) -- ([a-f\d]+)(?=[\s;,.|)]|$)")
NOT_CARRIED = re.compile(r"\bnot\s+(?:yet\s+)?carried\b|\bto be carried\b|\bcarried\s+only\b|\bcarried\s+if\b|\bif\b|"
                         r"\bunless\b|\bpending\b|\bdraft\b|\bprovisional\b|\bconditional|\bwithdrawn\b|"
                         r"\brevert(?:ed|s)?\b|\bwould be\b|\bnot run\b", re.I)
#: the margin's row states it (C2-1)
MARGIN_TOKEN = re.compile(r"no-harm margin `([^`]+)`")
MANIFEST_SUFFIX = ".manifest.json"
#: the result files' columns, classed (C2-8): a label column may hold no number of the price band; a figure or a
#: count column holds figures; no other column is accepted
LABEL, FIGURE, COUNT = "label", "figure", "count"
RESULT_COLUMNS = {"section": LABEL, "block": LABEL, "measure": LABEL, "stat": LABEL, "value": FIGURE, "n": COUNT}
#: the pinned measures whose unit is dollars or a count (`docs/MEASURES.md` (6) S1, (7) S3d, (26) S5a; C3-8): only
#: theirs may hold a `value` inside the price band, and only their ids may carry such a figure in a label; any other
#: measure's band number refuses. Identifiers, not figures (the module test allow-lists this assignment by name).
FIGURE_MEASURES = ("S1", "S3d", "S5a")
#: the platform pages the RL3 hand instruction follows (C3-6; the lead's verification, read 2026-11-21): citations, not
#: figures (the module test allow-lists this assignment by name)
PLATFORM_SOURCES = {"auto_oco": "14434175", "title": "TopstepX", "order_types": "8765442", "read": "2026-11-21"}

FIRMS = ("topstep",)
#: each firm's plans, from its verified ledger: the plan's name parsed from the rule that states it
PLANS: dict[str, dict[str, tuple[str, str]]] = {
    "topstep": {"trading_combine": ("combine_mll", r"\(e\.g\., \$[\d,]+ for a (\d+K Trading Combine)\)")},
}
#: an account's role -> (the verified rule bounding its open size, in minis; the words printed)
ROLES: dict[str, dict[str, tuple[str, str]]] = {
    "topstep": {"evaluation": ("combine_position_size_limit", "an evaluation account (the Trading Combine)"),
                "funded": ("funded_scaling_entry_tier_minis", "a funded account (the Express Funded Account; its "
                           "scaling plan's entry tier, the lowest, bounds the size)")},
}
RATIO_RULE = ("combine_position_size_limit", r"Micros and minis count at a (?P<micro>\d+):(?P<mini>\d+) ratio")
UNDERLYING_OF = {"MNQ": "NQ", "NQ": "NQ"}
MICRO = ("MNQ",)

TRIGGERS: dict[str, Callable[..., Any]] = {cls.__dataclass_fields__["source"].default: cls
                                           for cls in (T.P14Breakout, T.P16Marks, T.RL3Tickets)}
P14, RL3 = (cls.__dataclass_fields__["source"].default for cls in (T.P14Breakout, T.RL3Tickets))
SOURCE_LEVER = SS.SLOT_LEVERS[0]                       # the search space's source lever (T1)
SLOT_PARAMS = ("first", "last", "cutoff", "marks")
ANCHOR_OF = {"asia": "asia", "london": "london", "ny_am": "ny", "ny": "ny", "ny_pm": "ny_pm"}
#: the scheduler's session names -> the search space's (`search_space.session_spans`: one NY session until T2b)
SPACE_SESSION = {"evening": "evening", "asia": "asia", "london": "london", "ny_am": "ny_am", "ny_pm": "ny_pm",
                 "ny": "ny"}
BLOCKS = {"search": "search years: the years this design was chosen on, so likely better than what follows",
          "held_out": "held-out years, reported beside, never judged"}
CONVENTIONS = {
    "zero_edge": "These figures were measured with every trade's direction replaced by a fair coin (zero edge), over "
                 "many start days: they are what the account policy gives without any skill in direction. Your own "
                 "journey will differ.",
    "no_harm_real_path": "the trigger's own side against the coin's on the real path, same fills, no redraw",
}
EXPECTED_CONVENTION, NO_HARM_CONVENTION, HELDOUT_CONVENTION = "zero_edge", "no_harm_real_path", "heldout_joint_test"
HELDOUT_ACCEPTED = "accepted"
NO_HARM_STATS = ("side_rule", "margin", "trigger_composite", "coin_composite")

TRIGGER_WORDS = {
    T.P14Breakout: "a breakout: the first one-minute close above the previous completed reference bar's high, or below "
                   "its low (the reference bar's length in minutes is the parameter k), at most once per reference bar",
    T.RL3Tickets: "pre-session tickets at the day's levels of one kind, fixed when the alert is sent, before the "
                  "regular session's first fill; the tickets of a kind make one trade (the first to fill), unfilled "
                  "tickets cancelled at the cutoff",
}
ENTRY_WORDS = {
    T.MARKET: "a market order when the order goes live",
    T.LIMIT: "a limit order at the price at the alert (the close of the last bar closed when the alert is sent), "
             "working the limit window from when it goes live, cancelled if unfilled",
    T.TICKET: "each level's ticket by its declared rule (a fade is a limit at the level, a break a stop one tick "
              "beyond it), the kind's tickets rested together in one account as plain orders, each with its own "
              "bracket, the others cancelled by hand the moment one fills",
}
SIDE_RULE_WORDS = {
    "with_breakout": "with the breakout: BUY after a close above the reference bar's high, SELL after a close below "
                     "its low",
    "against_breakout": "against the breakout: SELL after a close above the reference bar's high, BUY after a close "
                        "below its low",
    "fade": "fade: a limit at the level against the approach (SELL at a level above the price at the alert, BUY at "
            "one below it)",
    "break": "break: a stop one tick beyond the level (BUY above a level above the price at the alert, SELL below "
             "one below it)",
}
SIGN_WORDS = {"+": "a close above the previous completed reference bar's high",
              "-": "a close below the previous completed reference bar's low"}
_PD, _ON, _PDC, _RN = T.RL3_KINDS                       # the library's level kinds, never retyped here
#: RL3's kinds that read the previous session's bars (`triggers.rl3_levels`)
PRIOR_KINDS = (_PD, _PDC)
_L = "library"
#: each level, defined by the bars it is made from (C2-9; `triggers.rl3_levels`); parts as `_Doc.line` takes them
LEVEL_PARTS: dict[tuple[str, str], tuple[Any, ...]] = {
    (_PD, "hi"): ("the high of the previous day's bars stamped ", ("ct", (_L, "prior_first")), " CT to ",
                  ("ct", (_L, "prior_last")), " CT"),
    (_PD, "lo"): ("the low of the previous day's bars stamped ", ("ct", (_L, "prior_first")), " CT to ",
                  ("ct", (_L, "prior_last")), " CT"),
    (_ON, "hi"): ("the high of the bars from yesterday's ", ("ct", (_L, "reopen")), " CT reopen to the bar stamped ",
                  ("ct", (_L, "pre_open")), " CT (the overnight)"),
    (_ON, "lo"): ("the low of the bars from yesterday's ", ("ct", (_L, "reopen")), " CT reopen to the bar stamped ",
                  ("ct", (_L, "pre_open")), " CT (the overnight)"),
    (_PDC, "lvl"): ("the close of the previous day's bar stamped ", ("ct", (_L, "prior_last")), " CT"),
    (_RN, "up"): ("the next round hundred above the close of the bar stamped ", ("ct", (_L, "pre_open")), " CT"),
    (_RN, "dn"): ("the next round hundred below the close of the bar stamped ", ("ct", (_L, "pre_open")), " CT"),
}
ROLE_PARTS = {1: ("a resistance: above the price at the alert (the close of the bar stamped ", ("ct", (_L, "pre_open")),
                  " CT) -- check it on your chart"),
              -1: ("a support: below the price at the alert (the close of the bar stamped ", ("ct", (_L, "pre_open")),
                   " CT) -- check it on your chart")}
PLATFORM_LEVEL = ("Your platform's own \"previous day high\", \"low\" or \"close\" may be made from other bars: use the "
                  "level made from exactly the bars named here.")
ROTATION_WORDS = {
    "longest_waiting": "the next trade of a firm goes to the account whose last trade ended longest ago (an unused "
                       "account first; ties in the account order below)",
    "round_robin": "the next trade of a firm goes to the account after the one that took the firm's last trade, in the "
                   "account order below",
    "by_component": "each day the router deals the accounts you hold, in the order you opened them, over the "
                    "components in the order of their windows below (the first account to the first component, the "
                    "next to the next, round again; with fewer accounts than components, each component takes one "
                    "account in turn), and a component's trade goes to its pool's account waiting longest",
}
VOID_WORDS = {
    "fomc": "an FOMC statement day: no trade at all that day",
    "early_close": "an exchange holiday or a scheduled early close before the day's flatten: no trade that day",
    "prior_abbreviated": "the day after a scheduled early close, a scheduled closure (a weekday the exchange is shut) "
                         "or a contract roll: no trade from a component that reads the previous day's levels",
}
RESEARCH_WORDS = {
    "short_bars": "days whose stored bars end before the walk's last bar, end early or carry a data defect, and the "
                  "day after one, or after a gap in the stored days",
    "overnight_missing": "overnight sessions with too many stored minutes missing",
}
WINDOW_WORDS = {"news": "a news window", "closed": "the closed window after the regular open",
                "bls": "the jobs-report window", "unscheduled": "an unscheduled release"}
REASON_WORDS = {
    "position": "a position is already open at this firm (one position at a time)",
    "order": "an entry order is already working at this firm",
    "gap": "the firm's last position closed less than the required flat time ago",
    "fomc": "today is an FOMC statement day",
    "calendar": "today is an exchange holiday or closes early before the flatten",
    "declared_void": "today is on the playbook's list of void days",
    "overnight": "the order would go live in the overnight session, which this design does not trade",
    "news": "the order would go live inside a news window",
    "closed": "the order would go live inside the closed window after the regular open",
    "bls": "today is a jobs-report day and the order would go live before the report window ends",
    "unscheduled": "an unscheduled release has closed trading for this order",
    "expired": "nothing of the order's working window is left",
    "prior_void": "the previous day's levels are void today (the first stored day, or a scheduled early close, a "
                  "scheduled closure or a roll before it)",
    "coin_side": "this trade's side came from the evaluation's coin, not from the trigger: the playbook offers no side "
                 "for it",
    "no_reference": "the trigger had no price at its alert",
    "no_ref_bar": "the last bar before the regular open is missing, so the tickets have no reference",
    "no_prior_day": "there is no previous day to take the levels from",
    "no_prior_session": "the previous day has no regular session",
    "no_prior_close": "the previous day has no last regular-session bar",
    "at_reference": "the level sits exactly at the reference price, so it is neither above nor below it",
    "oco_cancelled": "its other ticket was taken first (one-cancels-other)",
    "oco_tie_cancelled": "its other ticket was taken on the same bar (one-cancels-other)",
}
SIDE_WORDS = {1: "BUY (long)", -1: "SELL (short)"}
ORDER_WORDS = {W.MARKET: "MARKET", W.LIMIT_ENTRY: "LIMIT", W.STOP_ENTRY: "STOP"}
BEYOND_WORDS = {1: "above", -1: "below"}

HAND_ENTRY = ("HAND ENTRY ONLY. You enter every order yourself, by hand, on the firm's platform. Nothing in this "
              "playbook or its alerts places, sends or automates an order: no automated or API order entry, ever "
              "(it gets prop accounts banned).")
OPPOSITE = ("NEVER HOLD OPPOSITE POSITIONS AT ONCE across your accounts or firms. While any position is open in any "
            "of your accounts, a new trade is taken only on that position's side; otherwise skip it.")
NO_COPY = "One trade goes to one account. Never copy a trade to several accounts."
NO_NEWS_SIZE = ("Never put size into major news: no entry and no working order inside a news window; a position open "
                "when a window starts is closed at its start.")
NO_PRICE = ("No price is printed here: every order is stated against what you read on your platform when the alert "
            "reaches you. Bars are named by their stamp, the minute they open, as platforms label them.")
#: RL3's tickets by hand (C2-6): Topstep documents OCO only as exit legs around a position and Auto-OCO brackets per
#: entry, never two entry orders as one-cancels-other
PAIR_WORDS = ("TWO ENTRY ORDERS, ONE TRADE: before you place them, turn the platform's Auto-OCO brackets on while you "
              "are flat (and OCO on in the DOM), and set the Auto-OCO stop and target to the ticks given below for "
              "each ticket, so each entry carries its own bracket. Rest the tickets below as plain stop or limit "
              "orders, by hand, in this one account. The moment one fills, cancel the other by hand. A fast move can "
              "fill both before you cancel: if it does, close every position and cancel every working order in this "
              "account, brackets included, at once. Never split them across accounts.")
VOID_AT_LIVE = ("compare the market with your order: if a BUY limit is at or above the market, a SELL limit at or "
                "below it, a BUY stop at or below it or a SELL stop at or above it, ")
VOID_END = {False: "do not place it: no trade today.",
            True: "do not place this ticket: the other ticket stands or falls by its own check."}


class PlaybookRefused(ValueError):
    """A declaration or result the playbook cannot stand behind (a missing field, an unpinned file, a row not in the
    log, a binding that does not match, a value the library or the ledger disagrees with)."""


class AlertRefused(ValueError):
    """An alert not sent. `reason` is a key of `REASON_WORDS` when the day or the trigger voids it (a not-offered notice
    is due), `no_offer` when the trigger makes no offer at that moment, or `mismatch` when the input disagrees with
    the declaration."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def _mismatch(message: str) -> AlertRefused:
    return AlertRefused("mismatch", message)


# ------------------------------------------------------------------------------------------------ the pieces


def _text(v: Any) -> str:
    """A value's own text: an int as written, a float as Python's shortest round-trip form, a string unchanged."""
    if isinstance(v, bool):
        raise PlaybookRefused(f"a yes/no value {v!r} is not printed as a number")
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if not math.isfinite(v):
            raise PlaybookRefused(f"a value {v!r} is not finite")
        return repr(v)
    if isinstance(v, str):
        return v
    raise PlaybookRefused(f"a value of type {type(v).__name__} has no text")


def _anchor_ct(day: str, session: str) -> str:
    d = date.fromisoformat(day)
    if ANCHOR_OF[session] == "ny_pm":                 # NY PM opens at T2b's split (noon New York), per date
        return DC.label(LS.ny_boundary(d))
    return DC.label(DC.anchored_starts(d)[ANCHOR_OF[session]])


def _local_anchor(session: str) -> tuple[str, int, int]:
    """A session's local open: the void calendar's anchors; NY PM's is T2b's split (`ny_split_local`)."""
    if ANCHOR_OF[session] == "ny_pm":
        tz, h, m = LS.declared("ny_split_local")
        return str(tz), int(h), int(m)
    return DC.LOCAL_ANCHORS[ANCHOR_OF[session]]


#: transform name -> function of the resolved input values (in path order)
TRANSFORMS: dict[str, Callable[..., str]] = {
    "text": _text,
    "ct": lambda s: DC.label(int(s)),
    "stamp": lambda s: DC.label(int(s) - 1),          # the bar ending at slot s is stamped a minute before
    "target": lambda stop, rr: str(W.target_ticks(float(rr), int(stop))),
    "anchor_ct": _anchor_ct,
    "side": lambda s: SIDE_WORDS[int(s)],
    "order": lambda k: ORDER_WORDS[k],
    "yesno": lambda b: "yes" if bool(b) else "no",
}


@dataclass(frozen=True)
class Piece:
    """A template literal (`transform` None, no digit) or a value computed by `transform` from the inputs at `paths`."""

    text: str
    transform: str | None = None
    paths: tuple[tuple, ...] = ()


@dataclass(frozen=True)
class Rendered:
    pieces: tuple[Piece, ...]

    @property
    def text(self) -> str:
        return "".join(p.text for p in self.pieces)


def resolve(src: Mapping[str, Any], path: Sequence[Any]) -> Any:
    """The input at `path` (keys and list indices) in `src`; a missing one refuses."""
    cur: Any = src
    for k in path:
        try:
            cur = cur[k]
        except (KeyError, IndexError, TypeError) as e:
            raise PlaybookRefused(f"input {'/'.join(map(str, path))} is missing") from e
    return cur


class _Doc:
    def __init__(self, src: Mapping[str, Any]):
        self.src = src
        self.pieces: list[Piece] = []

    def lit(self, s: str) -> None:
        if s:
            self.pieces.append(Piece(s))

    def val(self, transform: str, *paths: tuple) -> None:
        args = [resolve(self.src, p) for p in paths]
        self.pieces.append(Piece(TRANSFORMS[transform](*args), transform, tuple(tuple(p) for p in paths)))

    def line(self, *parts: Any) -> None:
        """Parts: a str is a literal; a tuple is (transform, path, ...)."""
        for p in parts:
            if isinstance(p, str):
                self.lit(p)
            else:
                self.val(p[0], *p[1:])
        self.lit("\n")

    def done(self) -> Rendered:
        return Rendered(tuple(self.pieces))


def _v(*path: Any) -> tuple:
    return ("text", path)


def _ct(*path: Any) -> tuple:
    return ("ct", path)


def _st(*path: Any) -> tuple:
    return ("stamp", path)


# ------------------------------------------------------------------------------------------------ small checks


def _plain(v: Any, what: str) -> str:
    """Words carrying no figure (R-10): a non-blank string with no digit."""
    if not isinstance(v, str) or not v.strip() or DIGIT.search(v):
        raise PlaybookRefused(f"{what} is plain words with no digit and no figure, got {v!r}")
    return v


def _ident(v: Any, what: str) -> str:
    if not isinstance(v, str) or not IDENT.fullmatch(v):
        raise PlaybookRefused(f"{what} is an identifier (letters, '_', '-', a digit only in a trailing index form), "
                              f"got {v!r}")
    return v


def _int(v: Any, what: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise PlaybookRefused(f"{what} is a whole number, got {v!r}")
    return v


def _num(v: Any, what: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise PlaybookRefused(f"{what} is a finite number, got {v!r}")
    return float(v)


def _bare(text: Any, what: str) -> float:
    """A printed figure is a bare finite number (C2-8): no unit, no '$', no ','."""
    if not isinstance(text, str) or not BARE.fullmatch(text):
        raise PlaybookRefused(f"{what} is not a bare number")
    x = float(text)
    if not math.isfinite(x):
        raise PlaybookRefused(f"{what} is not finite")
    return x


def parse_day(v: Any, what: str = "a date") -> date:
    """Strict ISO `YYYY-MM-DD` only (B-6): the basic form, a padded or a short date refuses."""
    if not isinstance(v, str) or not ISO.fullmatch(v):
        raise PlaybookRefused(f"{what} is an ISO date YYYY-MM-DD, got {v!r}")
    try:
        d = date.fromisoformat(v)
    except ValueError as e:
        raise PlaybookRefused(f"{what} is not a calendar date: {v!r}") from e
    if d.isoformat() != v:
        raise PlaybookRefused(f"{what} is not in its ISO form: {v!r}")
    return d


def _no_dupes(pairs: list[tuple[str, Any]]) -> dict:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise PlaybookRefused(f"a key {k!r} appears twice in one object")
        out[k] = v
    return out


def _no_constant(name: str) -> Any:
    raise PlaybookRefused(f"a non-finite number {name} is not a value")


def strict_json(data: bytes) -> Any:
    """JSON with duplicate keys, NaN and Infinity refused (m-4)."""
    try:
        return json.loads(data, object_pairs_hook=_no_dupes, parse_constant=_no_constant)
    except PlaybookRefused:
        raise
    except ValueError as e:
        raise PlaybookRefused(f"not JSON: {e}") from e


def _lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def plan_name(firm: str, plan: str) -> str:
    """The plan's name as the firm's verified ledger states it (R-9)."""
    if firm not in PLANS or plan not in PLANS[firm]:
        raise PlaybookRefused(f"plan {plan!r} of firm {firm!r} is not one whose verified rules this tree loads")
    key, pattern = PLANS[firm][plan]
    m = re.search(pattern, M.s2_note(key))
    if m is None:
        raise PlaybookRefused(f"the verified rule {key} no longer states the plan's name: re-derive, never guess")
    return m.group(1)


def micros_per_mini(firm: str) -> int:
    key, pattern = RATIO_RULE
    m = re.search(pattern, M.s2_note(key))
    if m is None or int(m.group("mini")) != 1:
        raise PlaybookRefused(f"the verified rule {key} no longer states the micro-to-mini count")
    return int(m.group("micro"))


def size_cap(firm: str, role: str, instrument: str) -> int:
    """The most contracts of `instrument` an account of `role` may hold open, from the firm's verified ledger (R-4)."""
    if firm not in ROLES or role not in ROLES[firm]:
        raise PlaybookRefused(f"role {role!r} is not one of firm {firm!r}'s ({sorted(ROLES.get(firm, {}))})")
    minis = LS.rule(ROLES[firm][role][0])
    if isinstance(minis, bool) or not isinstance(minis, int) or minis <= 0:
        raise PlaybookRefused(f"the verified size rule {ROLES[firm][role][0]} is not a positive whole count")
    return minis * micros_per_mini(firm) if instrument in MICRO else minis


# ------------------------------------------------------------------------------------------------ the decision log


def decision_log(root: Path | str = ROOT) -> dict[str, str]:
    """The rows of `DECISIONS.md` at `root`, in the log's order: id -> its whole line (a repeated id refuses)."""
    p = Path(root) / "DECISIONS.md"
    if not p.is_file():
        raise PlaybookRefused(f"no decision log at {p}")
    rows: dict[str, str] = {}
    for m in ROW_LINE.finditer(p.read_bytes().decode()):
        if m.group(1) in rows:
            raise PlaybookRefused(f"row {m.group(1)} appears twice in the decision log")
        rows[m.group(1)] = m.group(0)
    return rows


def _cited(rows: Mapping[str, str], rid: Any, what: str) -> str:
    if not isinstance(rid, str) or rid not in rows:
        raise PlaybookRefused(f"{what} {rid!r} is not a row of the decision log")
    return rows[rid]


def _pins(row: str, strict: bool = True) -> dict[str, str]:
    """A row's pins, path -> hash; in a cited row a path pinned twice refuses (N-3); `strict` False (scanning the
    whole log for a declaration's first pin) keeps a twice-pinned path out instead."""
    out: dict[str, str] = {}
    twice: set[str] = set()
    for rel, sha in PIN.findall(row):
        if len(sha) != SHA_LEN:
            continue
        if rel in out:
            if strict:
                raise PlaybookRefused(f"a row pins {rel} twice")
            twice.add(rel)
        out[rel] = sha
    return {k: v for k, v in out.items() if k not in twice}


def _names(row: str, word: str, what: str) -> None:
    if not re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", row):
        raise PlaybookRefused(f"{what} does not name {word}")


def _margin_of(row: str, what: str) -> float:
    """The no-harm margin the 3.9 row pins (C2-1): `` no-harm margin `<value>` ``, stated once, a bare number."""
    found = MARGIN_TOKEN.findall(row)
    if len(found) != 1:
        raise PlaybookRefused(f"{what} does not state the no-harm margin exactly once")
    return _bare(found[0], f"{what}'s no-harm margin")


def _margin_rows(rows: Mapping[str, str]) -> list[str]:
    """The rows of the whole log that state a no-harm margin (C3-5: exactly one may)."""
    return [r for r, text in rows.items() if MARGIN_TOKEN.search(text)]


def _run_after_pin(root: Path, pin_text: str, commit: str) -> bool:
    """Whether `commit` descends from the commit that first pinned `pin_text` in the log (`extended.pin_order`)."""
    from extended import pin_order as PO

    try:
        return PO.descends(root, PO.pin_commit(root, pin_text), commit)
    except PO.PinOrderError:
        return False


# ------------------------------------------------------------------------------------------------ the windows (C2-3)


@functools.lru_cache(maxsize=1)
def _split() -> int:
    """T2b's declared NY boundary (`lever_space.bounds("T2b")`, noon New York), the evaluation's `ny_boundary`."""
    return int(LS.ny_boundary(SS.search_days()[0]))     # T2b's declared value, equal on every date (Q-188b)


@functools.lru_cache(maxsize=None)
def _starts(day: date) -> dict[str, int]:
    """The search space's session starts on `day`, slots after the reopen: `search_space.session_spans` split at T2b
    (`ny_am`, `ny_pm`), and its whole NY session (`ny`, for a window crossing noon)."""
    out = {k: int(a) for k, (a, _) in SS.session_spans(day, _split()).items()}
    out["ny"] = int(SS.session_spans(day)["ny"][0])
    return out


@functools.lru_cache(maxsize=1)
def _bounds() -> dict[str, tuple[int, int, int]]:
    """Each session's window offsets (first, last, step) valid on every search-year weekday
    (`search_space.session_slots`, split at T2b; and the whole NY session's)."""
    out = dict(SS.session_slots(_split()))
    out["ny"] = SS.session_slots()["ny"]
    return out


@functools.lru_cache(maxsize=1)
def _start_dates() -> tuple[tuple[tuple[tuple[str, int], ...], date], ...]:
    """One search-year weekday for each distinct set of session starts (the designs a window can make)."""
    seen: dict[tuple[tuple[str, int], ...], date] = {}
    for d in SS.search_days():
        seen.setdefault(tuple(sorted(_starts(d).items())), d)
    return tuple(seen.items())


def _space_design(decl: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for c in decl["components"]:
        out[SS.slot_dim(c["name"], "on")] = SS.ON
        out[SS.slot_dim(c["name"], SOURCE_LEVER)] = c["trigger"]["source"]
        out[SS.slot_dim(c["name"], "first")] = c["first"]
        out[SS.slot_dim(c["name"], "last")] = c["last"]
    return out


def window_space(decl: Mapping[str, Any]) -> SS.Space:
    """The declaration's windows as the search space holds them: one slot per component, offsets from its session's
    start (`search_space.Space`, `windows_on`), RL3's live slot and the closed window as the space's own constraints."""
    b = _bounds()
    slots, dims, cons = [], [], []
    for c in decl["components"]:
        sess = SPACE_SESSION.get(c["session"])
        if sess is None or sess not in b:
            raise PlaybookRefused(f"component {c['name']}: unknown session {c['session']!r}")
        lo, hi, step = b[sess]
        name = c["name"]
        slots.append(SS.Slot(name, sess, lo, hi, step))
        dims += [SS.Dim(SS.slot_dim(name, "on"), SS.CAT, values=(SS.ON,), slot=name),
                 SS.Dim(SS.slot_dim(name, SOURCE_LEVER), SS.CAT, values=(c["trigger"]["source"],), slot=name),
                 SS.Dim(SS.slot_dim(name, "first"), SS.INT, lo=lo, hi=hi, step=step, slot=name),
                 SS.Dim(SS.slot_dim(name, "last"), SS.INT, lo=lo, hi=hi, step=step, after=SS.slot_dim(name, "first"),
                        slot=name)]
        session_starts = sorted({dict(st)[sess] for st, _ in _start_dates()})
        if c["trigger"]["source"] == RL3:
            cons.append(SS.Constraint(f"{name} tickets live", "session", SS._rl3_live(name, session_starts)))
        cons.append(SS.Constraint(f"{name} closed window", "session", SS._closed_first(name, session_starts)))
    return SS.Space(tuple(dims), slots=tuple(slots), constraints=tuple(cons), starts=_starts, days=SS.search_days())


def _trigger_on(c: Mapping[str, Any], first: int, last: int) -> Any:
    """The component's trigger on a date whose window is [first, last] (slots): P-14's alerts are the window less L."""
    params = dict(c["trigger"]["params"])
    if c["trigger"]["source"] == P14:
        lat = int(c["latency"])
        lo = min(max(int(first) - lat, 0), T.P14_LAST)            # C3-2: clipped to P-14's span, as a full-span
        hi = max(min(int(last) - lat, T.P14_LAST), lo)            # P-14 and the window's filter give
        return T.P14Breakout(latency=lat, entry=params.get("entry", T.MARKET), first=lo, last=hi,
                             k=int(params.get("k", T.P14_K)))
    return TRIGGERS[c["trigger"]["source"]](**{k: (tuple(v) if isinstance(v, list) else v) for k, v in params.items()})


def design_on(decl: Mapping[str, Any], space: SS.Space, day: date) -> C.Design:
    """The design on trading day `day`, as the evaluation builds it: `Space.windows_on` per date, then
    `components.Design(day=day)`."""
    by = {c["name"]: c for c in decl["components"]}
    comps = []
    for name, _, a, b in space.windows_on(_space_design(decl), day):
        c = by[name]
        try:
            comps.append(C.Component(name, c["session"], int(a), int(b), _trigger_on(c, a, b), int(c["stop_ticks"]),
                                     float(c["rr"]), decl["instrument"]))
        except (C.DesignRefused, T.TriggerRefused, ValueError, TypeError) as e:
            raise PlaybookRefused(f"component {name} on {day}: {e}") from e
    try:
        return C.Design(decl["firm"], tuple(comps), day=day)
    except C.DesignRefused as e:
        raise PlaybookRefused(f"the design on {day}: {e}") from e


# ------------------------------------------------------------------------------------------------ the declaration


def _need(m: Any, keys: Sequence[str], what: str) -> None:
    if not isinstance(m, Mapping):
        raise PlaybookRefused(f"{what} is not a mapping")
    missing = [k for k in keys if k not in m]
    if missing:
        raise PlaybookRefused(f"{what} is missing {missing}")


def _hhmm(text: str) -> tuple[int, int]:
    h, m = str(text).split(":")
    return int(h), int(m)


def canonical_rule(rule: Any) -> str:
    """A side rule's text as the no-harm file records it: P-14's word, or RL3's `level=rule` pairs sorted by level."""
    if isinstance(rule, Mapping):
        return ";".join(f"{k}={rule[k]}" for k in sorted(rule))
    return str(rule)


def _check_trigger(comp: Mapping[str, Any]) -> Any:
    """The component's trigger, its side rule and its L held to the library (on a nominal window: the per-date
    triggers are `design_on`'s)."""
    trig = comp["trigger"]
    _need(trig, ("source", "params"), f"component {comp['name']}'s trigger")
    src = trig["source"]
    if src in TS.NO_SIDE and src not in TRIGGERS:
        raise PlaybookRefused(f"component {comp['name']}: {TS.NO_SIDE[src]}")
    if src not in TRIGGERS:
        raise PlaybookRefused(f"component {comp['name']}: trigger source {src!r} is not one of {sorted(TRIGGERS)}")
    params = dict(trig["params"])
    if src == P14 and any(k not in P14_PARAMS for k in params):
        raise PlaybookRefused(f"component {comp['name']}: the breakout's parameters are {P14_PARAMS}; its alerts are "
                              "the window less L on each date")
    lat = comp["latency"]
    if src == P14 and "latency" in params and params["latency"] != lat:
        raise PlaybookRefused(f"component {comp['name']}: its L is not its timed trigger's own")
    try:
        if src == P14:
            obj = T.P14Breakout(latency=_int(lat, f"component {comp['name']}'s L"), entry=params.get("entry", T.MARKET),
                                first=T.RTH_OPEN, last=T.P14_LAST, k=int(params.get("k", T.P14_K)))
        else:
            obj = TRIGGERS[src](**{k: (tuple(v) if isinstance(v, list) else v) for k, v in params.items()})
    except (TypeError, ValueError, RuntimeError) as e:
        if isinstance(e, PlaybookRefused):
            raise
        raise PlaybookRefused(f"component {comp['name']}: the library refuses its trigger: {e}") from e
    if isinstance(obj, T.P14Breakout) and int(obj.k) != T.P14_K:
        raise PlaybookRefused(f"component {comp['name']}: the breakout's reference bar is the registered k")
    try:
        TS.check_rule(obj, comp["side_rule"])
    except TS.SideRefused as e:
        raise PlaybookRefused(f"component {comp['name']}: {e}") from e
    if obj.latency_free:
        if lat is not None or LS.latency_cells(src) != (None,):
            raise PlaybookRefused(f"component {comp['name']}: a latency-free trigger's L is its single cell (null)")
    elif lat not in LS.latency_cells(src) or int(obj.latency) != lat:
        raise PlaybookRefused(f"component {comp['name']}: its L is not a declared L of its timed trigger's own")
    return obj


def _routes(decl: Mapping[str, Any], name: str) -> list[str]:
    """The accounts a component's trades may take: every account (under `by_component` the router deals the pools each
    day over the accounts alive, so any account may take any component)."""
    return [a["id"] for a in decl["accounts"]]


def _routing(decl: Mapping[str, Any], design: C.Design) -> R.Routing:
    """The declaration's rotation as the router holds it: `Routing(rule, firm=, design=)` (`by_component` deals over the
    design's components in window order; another rotation takes no design)."""
    rule = decl["rotation"]["rule"]
    try:
        return R.Routing(rule, firm=decl["firm"], design=design if rule == "by_component" else None)
    except R.RoutingRefused as e:
        raise PlaybookRefused(str(e)) from e


def _legs(trig: Any) -> int:
    """How many entry orders one offer of the trigger places at once: an RL3 kind's tickets together, else one."""
    return len(TS.rl3_names(trig)) if isinstance(trig, T.RL3Tickets) else 1


def check_declaration(decl: Mapping[str, Any]) -> SS.Space:
    """Every required field present and every value held to the library, the search space and the firm's verified
    ledger; returns the windows' space (refuses otherwise). The pins, rows and bindings are `load_carried`'s."""
    _need(decl, REQUIRED, "the declaration")
    for k in ("row", "registration"):
        if k in decl:
            raise PlaybookRefused(f"the declaration holds no {k}: it is the carrying record's")
    _ident(decl["design_id"], "the design id")
    _ident(decl["family"], "the family")
    firm = decl["firm"]
    if firm not in FIRMS:
        raise PlaybookRefused(f"firm {firm!r} is not one whose verified trading day this tree loads ({FIRMS})")
    plan_name(firm, decl["plan"])
    if decl["instrument"] not in UNDERLYING_OF:
        raise PlaybookRefused(f"instrument {decl['instrument']!r} is not one of {sorted(UNDERLYING_OF)}")
    side = decl["side"]
    _need(side, SIDE_KEYS, "the side rule")
    if _num(side["margin"], "the no-harm margin") < 0:
        raise PlaybookRefused("the no-harm margin is not negative")
    if not isinstance(side["no_harm_script"], str) or not side["no_harm_script"].strip():
        raise PlaybookRefused("the no-harm floor's script is named")
    accounts = list(decl["accounts"])
    if not accounts:
        raise PlaybookRefused("the declaration holds no account")
    for a in accounts:
        _need(a, ("id", "role"), "an account")
        _ident(a["id"], "an account id")
        size_cap(firm, a["role"], decl["instrument"])
    ids = [a["id"] for a in accounts]
    if len(set(ids)) != len(ids):
        raise PlaybookRefused(f"account ids repeat: {ids}")
    rot = decl["rotation"]
    _need(rot, ("rule",), "the rotation")
    if sorted(rot) != ["rule"]:
        raise PlaybookRefused("the rotation is its rule alone: hand-built pools are refused (the router deals them)")
    if rot["rule"] not in R.ROTATIONS:
        raise PlaybookRefused(f"rotation {rot['rule']!r} is not one of the declared values {R.ROTATIONS}")
    names = []
    for c in decl["components"]:
        _need(c, COMPONENT_KEYS, f"component {c.get('name') if isinstance(c, Mapping) else c!r}")
        names.append(c["name"])
    if not names or len(set(names)) != len(names):
        raise PlaybookRefused(f"component names are present and distinct: {names}")
    roles = {a["id"]: a["role"] for a in accounts}
    for c in decl["components"]:
        _ident(c["name"], "a component name")
        n = _int(c["contracts"], f"component {c['name']}'s contracts")
        if n <= 0:
            raise PlaybookRefused(f"component {c['name']}: contracts are positive")
        _num(c["rr"], f"component {c['name']}'s R")
        _int(c["stop_ticks"], "a stop")
        _int(c["first"], "a window's first offset")
        _int(c["last"], "a window's last offset")
        trig = _check_trigger(c)
        for acct in _routes(decl, c["name"]):
            if n * _legs(trig) > size_cap(firm, roles[acct], decl["instrument"]):
                raise PlaybookRefused(f"component {c['name']}: its size (every ticket of one order together) exceeds "
                                      f"the firm's verified limit for account {acct}")
    space = window_space(decl)
    why = space.check(_space_design(decl))
    if why is not None:
        raise PlaybookRefused(f"the windows: the search space refuses them ({why[0]}: {why[1]})")
    for _, d in _start_dates():                       # every distinct set of session starts of the search years
        _routing(decl, design_on(decl, space, d))
    ex = decl["execution"]
    _need(ex, EXECUTION_KEYS, "the execution rules")
    td = LS.trading_day()
    library = {"gap_minutes": T.GAP_MINUTES, "closed_window": [T.CLOSED_FIRST, T.CLOSED_LAST],
               "bls_clear": T.BLS_CLEAR, "limit_window_min": T.LIMIT_WINDOW, "flatten": int(T.JOURNEY.walk_end),
               "last_entry": int(td["last_entry_offset"])}
    for k, want in library.items():
        got = [int(x) for x in ex[k]] if isinstance(want, list) else int(ex[k])
        if got != want:
            raise PlaybookRefused(f"execution rule {k}: the declaration's value differs from the library's")
    _plain(decl["news_source"], "the news record's source")
    if not list(decl["news_windows"]):
        if "news_none" not in decl:
            raise PlaybookRefused("no news window is declared: the declaration says why, under news_none")
        _plain(decl["news_none"], "the reason no news window is declared")
    for w in decl["news_windows"]:
        _need(w, NEWS_KEYS, "a news window")
        _plain(w["source"], "a news window's source")
        try:
            T.release_window(_int(w["release"], "a release"), _int(w["before"], "a window's before"),
                             _int(w["after"], "a window's after"), w["source"])
        except ValueError as e:
            if isinstance(e, PlaybookRefused):
                raise
            raise PlaybookRefused(f"news window {w['source']!r}: {e}") from e
        if not list(w["dates"]):
            raise PlaybookRefused(f"news window {w['source']!r} names no release day")
        for d in w["dates"]:
            parse_day(d, "a release date")
    rules = list(decl["void_rules"])
    if sorted(rules) != sorted(VOID_WORDS) or len(set(rules)) != len(rules):
        raise PlaybookRefused(f"the void rules are those known at the alert, {sorted(VOID_WORDS)}, each once")
    filters = list(decl["research_filters"])
    if sorted(filters) != sorted(RESEARCH_WORDS) or len(set(filters)) != len(filters):
        raise PlaybookRefused(f"the research filters are the library's, {sorted(RESEARCH_WORDS)}, each once")
    for d in decl["void_dates"]:
        _need(d, ("date", "reason"), "a void date")
        parse_day(d["date"], "a void date")
        if d["reason"] not in VOID_WORDS:
            raise PlaybookRefused(f"void date {d['date']}: its reason is not one of the void rules")
    anchors = decl["session_anchors"]
    for sess in sorted({c["session"] for c in decl["components"]}):
        key = ANCHOR_OF.get(sess)
        if key is None:
            continue
        if not isinstance(anchors, Mapping) or sess not in anchors:
            raise PlaybookRefused(f"session {sess}'s local anchor is not declared")
        tz, hhmm = anchors[sess]
        if (tz, *_hhmm(hhmm)) != _local_anchor(sess):
            raise PlaybookRefused(f"session {sess}'s anchor differs from the void calendar's")
    if not list(decl["dates"]):
        raise PlaybookRefused("the playbook names at least one date to show its windows on")
    for d in decl["dates"]:
        parse_day(d, "a session-anchor date")
    bank = decl["bankroll"]
    _need(bank, ("budget", "row"), "the bankroll stop")
    if not _num(bank["budget"], "the bankroll budget") > 0:
        raise PlaybookRefused("the bankroll budget is a positive number")
    exp = decl["expected"]
    _need(exp, EXPECTED_TOP, "the expected journey")
    if not isinstance(exp["script"], str) or not exp["script"].strip():
        raise PlaybookRefused("the expected journey's script is named")
    if not list(exp["rows"]):
        raise PlaybookRefused("the expected journey names no measure")
    keys = []
    for e in exp["rows"]:
        _need(e, EXPECTED_KEYS, "an expected-journey row")
        _plain(e["label"], "an expected-journey label")
        if e["block"] not in BLOCKS:
            raise PlaybookRefused(f"an expected row's block is one of {sorted(BLOCKS)}, got {e['block']!r}")
        keys.append(row_key(e))
    if len(set(keys)) != len(keys):
        raise PlaybookRefused("the expected journey names a result row twice")
    return space


def row_key(e: Mapping[str, Any]) -> str:
    return "|".join(str(e[k]) for k in ("section", "block", "measure", "stat"))


# ------------------------------------------------------------------------------------------------ the result files


@dataclass(frozen=True)
class ResultFile:
    """A result file accepted under R-6, B-1, B-3, C2-8: its path relative to the root, its manifest's commit and
    convention, and its rows' cells as text, key 'section|block|measure|stat' -> the value's own text (each key once)."""

    file: str
    commit: str
    convention: str
    values: Mapping[str, str]


def _verify_result(path: Path) -> tuple[bool, str]:
    """`extended.results.verify_result` on the resolved path (imported here: it puts the vendored tree on
    `sys.path`)."""
    from extended import results as RS

    return RS.verify_result(path)


def _ignored(rel: str, roots: Sequence[Path]) -> bool:
    """Whether `rel` matches a pattern of a `.gitignore` at any of `roots` (the licence list is its licensed-price
    block, E-179, E-245)."""
    for root in roots:
        gi = Path(root) / ".gitignore"
        if not gi.is_file():
            continue
        for line in gi.read_bytes().decode().splitlines():
            pat = line.strip()
            if not pat or pat.startswith("#") or pat.startswith("!"):
                continue
            if pat.endswith("/") and (rel + "/").startswith(pat):
                return True
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel.rsplit("/", maxsplit=-1)[-1], pat):
                return True
    return False


def _column_problem(fields: Sequence[str] | None, rows: Sequence[Mapping[str, str]]) -> str | None:
    """C2-8: every column on the pinned list; no number of the price band in a label column (on the grid or off it,
    with or without a unit); figures and counts allowed in their columns."""
    from extended import price_levels as PL

    if not fields:
        return "it has no header"
    off = [f for f in fields if f not in RESULT_COLUMNS]
    if off:
        return f"its columns {off} are not on the pinned list"
    lo, hi = PL.BAND
    for r in rows:
        listed = r.get("measure") in FIGURE_MEASURES
        for f in fields:
            cell = str(r.get(f, ""))
            if RESULT_COLUMNS[f] == LABEL:
                if f == "measure" and listed:
                    continue
                for tok in NUMBER_IN.findall(cell):
                    x = float(tok.replace(",", ""))
                    if lo <= x <= hi:
                        return f"its label column {f} holds a number of the price band"
            elif RESULT_COLUMNS[f] == FIGURE and not listed and BARE.fullmatch(cell):
                if lo <= float(cell) <= hi:
                    return "its value column holds a number of the price band for a measure not on the pinned list"
    return None


def accept_result(root: Path | str, rel: Any, *, carried_pins: Mapping[str, str], design_id: str, convention: str,
                  decl_file: str, decl_sha: str, script: str, family: str,
                  extra: Mapping[str, Any] | None = None) -> ResultFile:
    """A result file under the module docstring's conditions, or `PlaybookRefused`."""
    root = Path(root).resolve()
    if not isinstance(rel, str) or not rel.startswith("results/") or not rel.endswith(".csv"):
        raise PlaybookRefused(f"a result file is named results/<name>.csv under the root, got {rel!r}")
    p = (root / rel).resolve()
    if p.parent != (root / "results").resolve():
        raise PlaybookRefused(f"{rel} does not resolve inside the root's results folder")
    if _ignored(rel, (ROOT, root)):
        raise PlaybookRefused(f"{rel} is git-ignored (a licensed-price derivative, on the licence list): it is never printed")
    mpath = Path(str(p) + MANIFEST_SUFFIX)
    if not p.is_file() or not mpath.is_file():
        raise PlaybookRefused(f"{rel} or its manifest is missing")
    ok, msg = _verify_result(p)
    if not ok:
        raise PlaybookRefused(f"{rel} does not verify: {msg}")
    mraw = mpath.read_bytes()
    if hashlib.sha256(_lf(mraw)).hexdigest() != carried_pins.get(rel + MANIFEST_SUFFIX):
        raise PlaybookRefused(f"{rel}'s manifest is not the one pinned in its row")
    man = strict_json(mraw)
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != man.get(HASH) or man.get(HASH) != carried_pins.get(rel):
        raise PlaybookRefused(f"{rel}: its bytes, its manifest and its row's pin do not agree on its hash")
    prov = man.get("provenance") or {}
    commit = man.get("git_commit")
    if not (isinstance(prov, Mapping) and isinstance(prov.get("clean_run"), Mapping) and prov["clean_run"].get("name")):
        raise PlaybookRefused(f"{rel} is not from a clean run (its manifest has no provenance.clean_run)")
    if (not isinstance(commit, str) or not commit or commit == "unknown" or commit.endswith("-dirty")
            or man.get("git_dirty") is not False):
        raise PlaybookRefused(f"{rel} is not from a named clean commit (commit {commit!r})")
    if man.get("exploratory") is not False:
        raise PlaybookRefused(f"{rel} is exploratory (chosen after a look): never printed as a carried design's")
    if man.get("script") != script or man.get("prereg_id") != family:
        raise PlaybookRefused(f"{rel} was not written by the declared script under the declaration's family")
    params = man.get("parameters") or {}
    want = {"design_id": design_id, "convention": convention, "declaration_file": decl_file,
            DECL_SHA_KEY: decl_sha, **dict(extra or {})}
    bad = sorted(k for k, v in want.items() if params.get(k) != v)
    if bad:
        raise PlaybookRefused(f"{rel} is not bound to this pinned declaration ({', '.join(bad)} differ)")
    text = raw.decode()
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    why = _column_problem(reader.fieldnames, rows)
    if why:
        raise PlaybookRefused(f"{rel}: {why}: it is never printed")
    values: dict[str, str] = {}
    for r in rows:
        k = row_key(r)
        if k in values:
            raise PlaybookRefused(f"{rel} holds the row {k} twice")
        values[k] = str(r["value"])
    return ResultFile(rel, commit, convention, values)


def _picked(res: ResultFile, keys: Sequence[str]) -> dict[str, str]:
    out = {}
    for k in keys:
        if k not in res.values:
            raise PlaybookRefused(f"{res.file} holds no row {k}")
        if not res.values[k].strip():
            raise PlaybookRefused(f"{res.file}'s value for {k} is blank")
        _bare(res.values[k], f"{res.file}'s value for {k}")
        out[k] = res.values[k]
    return out


def _no_harm(res: ResultFile, decl: Mapping[str, Any]) -> dict[str, str]:
    """The floor recomputed per component (B-1): the recorded rule and margin are the declaration's, and the trigger
    side's composite is not below the coin side's by more than the margin."""
    margin = float(decl["side"]["margin"])
    out = {}
    for c in decl["components"]:
        k = {s: "|".join(("no_harm", "search", c["name"], s)) for s in NO_HARM_STATS}
        if any(k[s] not in res.values for s in NO_HARM_STATS):
            raise PlaybookRefused(f"component {c['name']}: its no-harm floor is absent ({res.file}): it offers no "
                                  "playbook side, and the design is not carried")
        if res.values[k["side_rule"]] != canonical_rule(c["side_rule"]):
            raise PlaybookRefused(f"component {c['name']}: the no-harm floor was read on another side rule")
        if _bare(res.values[k["margin"]], "the recorded margin") != margin:
            raise PlaybookRefused(f"component {c['name']}: the no-harm floor was read with another margin")
        tc = _bare(res.values[k["trigger_composite"]], "the trigger side's composite")
        cc = _bare(res.values[k["coin_composite"]], "the coin side's composite")
        if tc < cc - margin:
            raise PlaybookRefused(f"component {c['name']}: its no-harm floor failed ({res.file}): it offers no "
                                  "playbook side, and the design is not carried")
        out.update({k[s]: res.values[k[s]] for s in NO_HARM_STATS})
    return out


# ------------------------------------------------------------------------------------------------ the carried design

_MINT = object()


@dataclass(frozen=True)
class Carried:
    """A carried design as `load_carried` accepted it: the carrying record (its path, sha256, registration and row),
    the declaration's bytes (re-read on every use), its path and pinned sha256, the cited rows, the windows' space,
    and the three result files' picked values (the expected journey, the no-harm floor, the held-out acceptance)."""

    record_file: str
    record_sha: str
    registration: str
    row: str
    decl_file: str
    decl_sha: str
    decl_bytes: bytes
    rows: Mapping[str, str]
    space: SS.Space
    expected: ResultFile
    no_harm: ResultFile
    heldout: ResultFile
    _mint: Any = field(default=None, repr=False, compare=False)

    def _bound(self) -> tuple:
        return (self.record_file, self.record_sha, self.registration, self.row, self.decl_file, self.decl_sha,
                self.expected, self.no_harm, self.heldout)

    def __post_init__(self) -> None:
        if not (isinstance(self._mint, tuple) and self._mint and self._mint[0] is _MINT
                and self._mint[-1] == self._bound()
                and hashlib.sha256(self.decl_bytes).hexdigest() == self.decl_sha):
            raise PlaybookRefused("a carried design is made only by load_carried, from its pinned files")

    @property
    def decl(self) -> dict:
        return strict_json(self.decl_bytes)


def _rel(root: Path, f: str, what: str) -> tuple[Path, str]:
    p = (root / f).resolve()
    try:
        rel = p.relative_to(root).as_posix()
    except ValueError as e:
        raise PlaybookRefused(f"{what} {f} lies outside the root") from e
    if not p.is_file():
        raise PlaybookRefused(f"no {what} at {rel}")
    return p, rel


def load_carried(record_file: str, *, root: Path | str = ROOT) -> Carried:
    """The carried design from its carrying record (the module docstring), or `PlaybookRefused`."""
    root = Path(root).resolve()
    rows = decision_log(root)
    order = list(rows)
    rp, rrel = _rel(root, record_file, "carrying record")
    rdata = _lf(rp.read_bytes())
    rsha = hashlib.sha256(rdata).hexdigest()
    record = strict_json(rdata)
    if not isinstance(record, Mapping) or sorted(record) != sorted(RECORD_KEYS):
        raise PlaybookRefused(f"the carrying record holds exactly {RECORD_KEYS}")
    did, reg, crow = record["design_id"], record["registration"], record["row"]
    _ident(did, "the design id")
    _ident(reg, "the registration id")
    carrying = _cited(rows, crow, "the carrying row")
    pins = _pins(carrying)
    if pins.get(rrel) != rsha:
        raise PlaybookRefused(f"the carrying record {rrel} is not the file pinned in {crow}")
    p, rel = _rel(root, record["declaration"], "declaration")
    data = _lf(p.read_bytes())
    sha = hashlib.sha256(data).hexdigest()
    if record[DECL_SHA_KEY] != sha:
        raise PlaybookRefused(f"the declaration {rel} is not the one the carrying record binds (its hash {sha})")
    ho_rel = record["heldout_file"]
    tokens = CARRIED_TOKEN.findall(carrying)
    if not isinstance(ho_rel, str) or tokens != [(did, sha, reg, pins.get(ho_rel, ""))]:
        raise PlaybookRefused(f"the carrying row {crow} does not hold the one token `carried: {did} @ <the declaration's "
                              f"hash> -- {reg} -- <the held-out result's hash pinned in it>`")
    if NOT_CARRIED.search(carrying):
        raise PlaybookRefused(f"the carrying row {crow} holds negated or conditional wording: the design is not carried")
    decl = strict_json(data)
    _need(decl, REQUIRED, "the declaration")
    if decl["design_id"] != did:
        raise PlaybookRefused("the carrying record names another design than its declaration")
    space = check_declaration(decl)
    nh_id = decl["side"]["no_harm_row"]
    nh_row = _cited(rows, nh_id, "the side's no-harm row")
    _names(nh_row, did, f"the no-harm row {nh_id}")
    first = next((r for r in order if _pins(rows[r], strict=False).get(rel) == sha), None)
    if first is None or not order.index(first) < order.index(nh_id) < order.index(crow):
        raise PlaybookRefused("the declaration is pinned in a row before its no-harm row, and that before the carrying "
                              "row (the side rules fixed before the floor is read)")
    margins = _margin_rows(rows)
    if margins != [decl["side"]["margin_row"]] or not order.index(margins[0]) < order.index(first):
        raise PlaybookRefused("exactly one row of the log states the no-harm margin, the declaration's margin row, and "
                              "it comes before the declaration's pin")
    m_row = _cited(rows, decl["side"]["margin_row"], "the no-harm margin's row")
    if _margin_of(m_row, f"the margin row {decl['side']['margin_row']}") != float(decl["side"]["margin"]):
        raise PlaybookRefused("the declaration's no-harm margin is not the one its margin row pins")
    _cited(rows, decl["bankroll"]["row"], "the bankroll budget's row")
    bind = dict(design_id=did, decl_file=rel, decl_sha=sha, family=decl["family"])
    exp_rel, nh_rel = decl["expected"]["file"], decl["side"]["no_harm_file"]
    expected = accept_result(root, exp_rel, carried_pins=pins, convention=EXPECTED_CONVENTION,
                             script=decl["expected"]["script"], **bind)
    pin_text = "`" + rel + "` " + HASH + " `" + sha + "`"
    if not _run_after_pin(root, pin_text, expected.commit):
        raise PlaybookRefused(f"{exp_rel}'s run commit does not descend from the commit that pinned the declaration, on "
                              "HEAD's line: the journey was not read after the pin")
    expected = ResultFile(expected.file, expected.commit, expected.convention,
                          _picked(expected, [row_key(e) for e in decl["expected"]["rows"]]))
    no_harm = accept_result(root, nh_rel, carried_pins=_pins(nh_row), convention=NO_HARM_CONVENTION,
                            script=decl["side"]["no_harm_script"], extra={"margin": decl["side"]["margin"]}, **bind)
    if not _run_after_pin(root, pin_text, no_harm.commit):
        raise PlaybookRefused(f"{nh_rel}'s run commit does not descend from the commit that pinned the declaration, on "
                              "HEAD's line: the floor was not read after the pin")
    no_harm = ResultFile(no_harm.file, no_harm.commit, no_harm.convention, _no_harm(no_harm, decl))
    heldout = accept_result(root, ho_rel, carried_pins=pins, convention=HELDOUT_CONVENTION,
                            script=record["heldout_script"], **{**bind, "family": record["heldout_family"]})
    hk = "|".join(("heldout", "joint", did, "verdict"))
    if heldout.values.get(hk) != HELDOUT_ACCEPTED:
        raise PlaybookRefused(f"{ho_rel} does not record the joint held-out test as accepted for {did}: not carried")
    heldout = ResultFile(heldout.file, heldout.commit, heldout.convention, {hk: heldout.values[hk]})
    cited = {r: rows[r] for r in (crow, nh_id, decl["side"]["margin_row"], decl["bankroll"]["row"])}
    bound = (rrel, rsha, reg, crow, rel, sha, expected, no_harm, heldout)
    return Carried(rrel, rsha, reg, crow, rel, sha, data, cited, space, expected, no_harm, heldout,
                   _mint=(_MINT, bound))


def _carried(carried: Any) -> dict:
    if not isinstance(carried, Carried):
        raise PlaybookRefused("the playbook renders only a carried design loaded by load_carried")
    decl = carried.decl
    check_declaration(decl)
    return decl


def _library(decl: Mapping[str, Any]) -> dict[str, Any]:
    firm = decl["firm"]
    return {"plan": plan_name(firm, decl["plan"]),
            "cap": {a["id"]: size_cap(firm, a["role"], decl["instrument"]) for a in decl["accounts"]},
            "tickets_alert": T.RTH_OPEN, "tickets_live": T.LIVE_0900, "hash": HASH,
            "prior_first": T.PRIOR_RTH[0], "prior_last": T.PRIOR_RTH[1], "reopen": 0, "pre_open": T.RTH_OPEN - 1,
            "breakout_last": T.P14_LAST, "sources": dict(PLATFORM_SOURCES)}


# ------------------------------------------------------------------------------------------------ the playbook


def render_playbook(carried: Carried) -> Rendered:
    """The playbook's plain text (the module docstring); refuses anything but a carried design."""
    decl = _carried(carried)
    exp, nh = carried.expected, carried.no_harm
    days = [parse_day(x) for x in decl["dates"]]
    windows = [{c.name: (int(c.first), int(c.last)) for c in design_on(decl, carried.space, d).components}
               for d in days]
    src = {"design": decl, "library": _library(decl),
           "file": {"decl": carried.decl_file, "sha": carried.decl_sha, "record": carried.record_file,
                    "heldout": carried.heldout.file, "heldout_commit": carried.heldout.commit},
           "carry": {"row": carried.row, "registration": carried.registration},
           "calc": {"windows": windows, "order": list(R.window_order(design_on(decl, carried.space, days[0])))},
           "expected": {"file": exp.file, "commit": exp.commit, **exp.values},
           "no_harm": {"file": nh.file, "commit": nh.commit, **nh.values}}
    d = _Doc(src)
    D, L = "design", "library"
    d.line("PLAYBOOK -- design ", _v(D, "design_id"), " (carried under ", _v("carry", "row"), ", registration ",
           _v("carry", "registration"), ")")
    d.line("The declaration: ", _v("file", "decl"), ", ", _v(L, "hash"), " ", _v("file", "sha"), "; its carrying "
           "record: ", _v("file", "record"), " (pinned in ", _v("carry", "row"), "); the joint held-out test's "
           "accepted result: ", _v("file", "heldout"), " (commit ", _v("file", "heldout_commit"), ").")
    d.line("")
    d.line(HAND_ENTRY)
    d.line(OPPOSITE)
    d.line(NO_COPY)
    d.line(NO_NEWS_SIZE)
    d.line(NO_PRICE)
    d.line("")
    d.line("FIRM AND PLAN")
    d.line("Firm: ", _v(D, "firm"), "; plan: ", _v(L, "plan"), " (as the firm's verified rules name it); instrument: ",
           _v(D, "instrument"), ".")
    d.line("Accounts, in the account order:")
    for i, a in enumerate(decl["accounts"]):
        d.line("  - ", _v(D, "accounts", i, "id"), ": ", ROLES[decl["firm"]][a["role"]][1], "; at most ",
               _v(L, "cap", a["id"]), " contracts of ", _v(D, "instrument"), " open at once (the firm's verified "
               "limit).")
    d.line("")
    d.line("COMPONENTS (one session window each; times in CT, Chicago)")
    for i, c in enumerate(decl["components"]):
        P = (D, "components", i)
        cls = TRIGGERS[c["trigger"]["source"]]
        key = ANCHOR_OF.get(c["session"])
        d.line("Component ", _v(*P, "name"), " -- session ", _v(*P, "session"), ": orders go live on the bars stamped ",
               _v(*P, "first"), " to ", _v(*P, "last"), " minutes after the session's start",
               *((" (its local open, ", _v(D, "session_anchors", c["session"], 1), " ",
                  _v(D, "session_anchors", c["session"], 0), ", converted on each date)") if key else
                 (" (the reopen)",)), ":")
        for j, _ in enumerate(decl["dates"]):
            parts: list[Any] = ["    on ", _v(D, "dates", j)]
            if key:
                parts += [" (the open at ", ("anchor_ct", (D, "dates", j), P + ("session",)), " CT)"]
            d.line(*parts, ": ", _ct("calc", "windows", j, c["name"], 0), " CT to ",
                   _ct("calc", "windows", j, c["name"], 1), " CT")
        d.line("  Trigger (", _v(*P, "trigger", "source"), "): ", TRIGGER_WORDS[cls], ".")
        for k in sorted(c["trigger"]["params"]):
            v = c["trigger"]["params"][k]
            if k in SLOT_PARAMS:
                d.line("    ", k, ": ", _ct(*P, "trigger", "params", k), " CT")
            elif isinstance(v, bool):
                d.line("    ", k, ": ", ("yesno", (*P, "trigger", "params", k)))
            else:
                d.line("    ", k, ": ", _v(*P, "trigger", "params", k))
        entry = c["trigger"]["params"].get("entry", T.TICKET if cls is T.RL3Tickets else T.MARKET)
        if cls is T.RL3Tickets:
            d.line("  Entry: ", ENTRY_WORDS[entry], ". The tickets are fixed at ", _ct(L, "tickets_alert"),
                   " CT, when the alert is sent, and go live on the bar stamped ", _ct(L, "tickets_live"), " CT.")
            d.line(*_SOURCE_LINE)
        else:
            d.line("  Entry: ", ENTRY_WORDS[entry], ". The alert reaches you ", _v(*P, "latency"),
                   " minutes before the order goes live; the alerts run from the window's start less that to its end "
                   "less that, on each date, never after ", _ct(L, "breakout_last"), " CT (the breakout's last event).")
        d.line("  Side (the trigger's own, cleared by the no-harm floor under ", _v(D, "side", "no_harm_row"), "):")
        if cls is T.RL3Tickets:
            kind = c["trigger"]["params"]["kind"]
            for name in TS.rl3_names(T.RL3Tickets(kind, int(c["trigger"]["params"]["cutoff"]))):
                d.line("    at ", *LEVEL_PARTS[(kind, name)], ": ", SIDE_RULE_WORDS[c["side_rule"][name]], ".")
            d.line("    ", PLATFORM_LEVEL)
        else:
            d.line("    ", SIDE_RULE_WORDS[c["side_rule"]], ".")
        NH = "no_harm|search|" + c["name"] + "|"
        d.line("    On the search years (the years this design was chosen on): the trigger side's composite ",
               _v("no_harm", NH + "trigger_composite"), ", the coin side's ", _v("no_harm", NH + "coin_composite"),
               ", the margin ", _v("no_harm", NH + "margin"), ".")
        d.line("  Size: ", _v(*P, "contracts"), " contracts of ", _v(D, "instrument"),
               (" on each ticket." if cls is T.RL3Tickets else "."))
        d.line("  Stop: ", _v(*P, "stop_ticks"), " ticks from your fill. Target: ", ("target", P + ("stop_ticks",),
               P + ("rr",)), " ticks (reward to risk ", _v(*P, "rr"), "). Both are placed with the entry as a bracket.")
    d.line("The no-harm floor's file: ", _v("no_harm", "file"), " (commit ", _v("no_harm", "commit"), "): ",
           CONVENTIONS[NO_HARM_CONVENTION], "; the margin ", _v(D, "side", "margin"), " is the one pinned under ",
           _v(D, "side", "margin_row"), "; each component's side passed: its composite not below the coin's by more "
           "than the margin.")
    d.line("")
    d.line("EXECUTION RULES (every component)")
    E = (D, "execution")
    d.line("- One position or working entry order at a time per firm (one level kind's tickets count as one order); "
           "after a position closes, wait at least ", _v(*E, "gap_minutes"), " minutes before the next entry.")
    d.line("- Limit orders work ", _v(*E, "limit_window_min"), " minutes from going live, then are cancelled.")
    d.line("- A limit or stop that would fill at once when it goes live (a BUY limit at or above the market, a SELL limit "
           "at or below it, a BUY stop at or below it, a SELL stop at or above it) is not placed: no trade.")
    d.line("- Closed window: no entry and no fill on the bars stamped ", _ct(*E, "closed_window", 0), " CT through ",
           _ct(*E, "closed_window", 1), " CT, every day.")
    d.line("- On a jobs-report day: no fill on the bars stamped up to ", _ct(*E, "bls_clear"), " CT.")
    d.line("- No new entry after ", _ct(*E, "last_entry"), " CT. Flatten every position by the close of the bar stamped ",
           _st(*E, "flatten"), " CT (it ends at ", _ct(*E, "flatten"), " CT) at the latest.")
    d.line("- A working order is cancelled when a news or closed window starts; an open position is closed at its "
           "start.")
    d.line("News windows (no entry and no fill inside them), from ", _v(D, "news_source"), ":")
    if not decl["news_windows"]:
        d.line("  (none: ", _v(D, "news_none"), ")")
    for i, w in enumerate(decl["news_windows"]):
        P = (D, "news_windows", i)
        parts = ["  - ", _v(*P, "source"), ": released at ", _ct(*P, "release"), " CT; the window covers the bars "
                 "stamped from ", _v(*P, "before"), " minutes before the release to ", _v(*P, "after"),
                 " minutes after it; on "]
        for j, _ in enumerate(w["dates"]):
            parts += ([", "] if j else []) + [_v(*P, "dates", j)]
        d.line(*parts, ".")
    d.line("Void days (no trade from the components named; all known before the alert):")
    for r in decl["void_rules"]:
        d.line("  - ", VOID_WORDS[r], ".")
    for i, v in enumerate(decl["void_dates"]):
        d.line("  - ", _v(D, "void_dates", i, "date"), ": ", VOID_WORDS[v["reason"]], ".")
    d.line("")
    d.line("ACCOUNT ROTATION")
    rot = decl["rotation"]
    d.line("Rule ", _v(D, "rotation", "rule"), ": ", ROTATION_WORDS[rot["rule"]], ". Each alert names the account the "
           "rule picks among the accounts you hold that day.")
    if rot["rule"] == "by_component":
        parts = ["  the components in the order of their windows: "]
        for j, _ in enumerate(src["calc"]["order"]):
            parts += ([", "] if j else []) + [_v("calc", "order", j)]
        d.line(*parts)
    d.line(NO_COPY)
    d.line("")
    d.line("THE BANKROLL STOP")
    d.line("Budget: $", _v(D, "bankroll", "budget"), " (set under ", _v(D, "bankroll", "row"),
           "). When your total spending on this plan reaches it before a first payout, stop: buy no further "
           "evaluation and no reset, add no money, and keep trading only the accounts you already hold until each is "
           "passed or lost.")
    d.line("")
    d.line("THE EXPECTED JOURNEY")
    d.line("From the result file ", _v("expected", "file"), " (commit ", _v("expected", "commit"),
           "), measured on this declaration:")
    rows = decl["expected"]["rows"]
    held = {(e["section"], e["measure"], e["stat"]) for e in rows if e["block"] == "held_out"}
    for i, e in enumerate(rows):
        d.line("  - ", _v(D, "expected", "rows", i, "label"), ": ", _v("expected", row_key(e)), " (",
               BLOCKS[e["block"]], "; ", _v(D, "expected", "rows", i, "stat"), ")")
        if e["block"] == "search" and (e["section"], e["measure"], e["stat"]) not in held:
            d.line("    its held-out reading is not named here: read it beside before trusting this figure.")
    d.line(CONVENTIONS[carried.expected.convention])
    d.line("The backtests behind these figures also left out, for data reasons you cannot see and need not judge "
           "(research filters, not trading rules):")
    for r in decl["research_filters"]:
        d.line("  - ", RESEARCH_WORDS[r], ".")
    return d.done()


# ------------------------------------------------------------------------------------------------ the alert


_SOURCE_LINE = ("  (The platform steps follow Topstep's help centre: article ", ("text", (_L, "sources", "auto_oco")),
                " (\"", ("text", (_L, "sources", "title")), "\") for the Auto-OCO brackets and the DOM's OCO switch, article ",
                ("text", (_L, "sources", "order_types")), " for the order types; read ",
                ("text", (_L, "sources", "read")), ".)")


def _comp(decl: Mapping[str, Any], name: Any) -> tuple[int, Mapping[str, Any]]:
    for i, c in enumerate(decl["components"]):
        if c["name"] == name:
            return i, c
    raise _mismatch(f"component {name!r} is not one of the declaration's")


def cut_history(hist: T.History, i: int, at: int) -> T.History:
    """The bars a user has at an alert at slot `at` of day `i` (feature-rules section 1): the days up to `i`, and of day
    `i` only the bars closed by `at` (the walker's columns 1..at, the bars stamped before `at`); every later bar NaN."""
    import numpy as np

    arrs = []
    for x in (hist.o, hist.h, hist.l, hist.c):
        y = np.array(x[: i + 1], dtype=float, copy=True)
        y[i, int(at) + 1:] = np.nan
        arrs.append(y)
    return T.History(tuple(hist.days[: i + 1]), tuple(hist.contract[: i + 1]), *arrs)


def _day_windows(decl: Mapping[str, Any], day: date) -> tuple[T.Window, ...]:
    """The declaration's news windows on `day`, dates compared as dates (R-4, B-6), never the caller's."""
    return tuple(T.release_window(int(w["release"]), int(w["before"]), int(w["after"]), w["source"])
                 for w in decl["news_windows"] if day in {parse_day(x) for x in w["dates"]})


def _today(decl: Mapping[str, Any], accounts: Any) -> tuple[str, ...]:
    """The accounts alive today (N-c2-1): a non-empty set of the declaration's, in the declaration's order."""
    ids = [a["id"] for a in decl["accounts"]]
    if isinstance(accounts, str) or not isinstance(accounts, (list, tuple)) or not accounts:
        raise _mismatch("the accounts alive today are a non-empty list of the declaration's")
    if len(set(accounts)) != len(accounts) or any(a not in ids for a in accounts):
        raise _mismatch(f"the accounts alive today {list(accounts)} are not distinct accounts of the declaration's")
    return tuple(a for a in ids if a in accounts)


def _alert(carried: Carried, component: Any, hist: Any, i: Any, at: Any, sources: Any, router: Any,
           accounts: Any) -> Rendered:
    decl = _carried(carried)
    ci, c = _comp(decl, component)
    if c["trigger"]["source"] not in (P14, RL3):
        raise _mismatch("the component's trigger offers no playbook side")
    if not isinstance(hist, T.History) or isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(hist):
        raise _mismatch("an alert is computed from the day's bars (a triggers.History and the day's index), never from "
                        "a caller's offer")
    if isinstance(at, bool) or not isinstance(at, int) or not 0 <= at < T.DAY_SLOTS:
        raise _mismatch("the alert's moment is a slot of the trading-day clock")
    try:
        day = parse_day(hist.days[i], "the day")
    except PlaybookRefused as e:
        raise _mismatch(str(e)) from e
    if not isinstance(sources, DC.Sources):
        raise _mismatch("the day's flags come from the void calendar's sources (day_calendar.Sources), never the "
                        "caller's word")
    if not isinstance(router, R.Router):
        raise _mismatch("the account is the router's pick (router.Router), never the caller's")
    held = getattr(router, "routings", {}).get(decl["firm"])
    try:
        want = _routing(decl, design_on(decl, carried.space, day))
    except PlaybookRefused as e:
        raise _mismatch(str(e)) from e
    if not isinstance(held, R.Routing) or (held.rotation, tuple(held.components)) != (want.rotation,
                                                                                    tuple(want.components)):
        raise _mismatch("the router's rotation for this firm is not the declaration's")
    today = _today(decl, accounts)
    try:
        ctx = DC.alert_context(sources, UNDERLYING_OF[decl["instrument"]], day, i, windows=_day_windows(decl, day))
    except (DC.HeldOutDay, KeyError, ValueError) as e:
        raise _mismatch(f"the calendar known at the alert gives no context for {day}: {e}") from e
    try:
        comp = next(x for x in design_on(decl, carried.space, day).components if x.name == c["name"])
    except PlaybookRefused as e:
        raise _mismatch(str(e)) from e
    trig = comp.trigger
    if isinstance(trig, T.RL3Tickets) and trig.kind in PRIOR_KINDS and not ctx.prior_void:
        prev = DC.prior_session(sources, day)
        if i == 0 or prev is None or parse_day(hist.days[i - 1], "the previous day") != prev:
            raise _mismatch(f"the bars do not hold the previous session ({prev}) by the calendar: no level, role or "
                            "side is computed from another day")
        if DC.data_void(sources, prev):
            raise _mismatch(f"the previous session ({prev}) is a data-void day: no level is taken from its bars")
    try:
        offers = trig.offers(cut_history(hist, i, at), i, ctx)
    except T.TriggerRefused as e:
        raise _mismatch(f"the trigger refuses the day: {e}") from e
    group = [o for o in offers if int(o.alert) == int(at) and int(comp.first) <= int(o.live) <= int(comp.last)]
    if not group:
        raise AlertRefused("no_offer", f"component {c['name']}'s trigger makes no offer at {DC.label(at)} CT")
    live = int(group[0].live)
    if any(parse_day(v["date"]) == day for v in decl["void_dates"]):
        raise AlertRefused("declared_void", f"{day} is on the declaration's void list: no alert is sent")
    kept, refused = T.admit(group, ctx)
    if not kept:
        why = refused[0][1]
        raise AlertRefused(why if why in REASON_WORDS else "calendar", f"the library refuses the offer: {why}")
    try:
        account = router.peek(decl["firm"], c["name"], today)
    except R.RoutingRefused as e:
        raise _mismatch(str(e)) from e
    ai = [a["id"] for a in decl["accounts"]].index(account)
    cap = size_cap(decl["firm"], decl["accounts"][ai]["role"], decl["instrument"])
    if int(c["contracts"]) * len(kept) > cap:
        raise _mismatch("the order's size (every ticket together) exceeds the firm's verified limit for this account")
    windows = ctx.all_windows()
    tickets = []
    for off in kept:
        try:
            side = TS.trigger_side(trig, c["side_rule"], off)
        except TS.SideRefused as e:
            raise _mismatch(str(e)) from e
        kind, price = T.order_for(off, side.side)
        t: dict[str, Any] = {"side": side.side, "kind": kind, "rule": side.ticket_rule, "tag": off.tag,
                             "role": int(off.role), "stretches": []}
        if kind == W.STOP_ENTRY:
            if not (math.isfinite(float(price)) and math.isfinite(float(off.level))):
                raise _mismatch("a stop ticket's level is not finite")
            t["beyond"] = int(round(side.side * (float(price) - float(off.level)) / W.TICK))
        for lv, last in T.segments(off, ctx):
            rules = T.rules_for(lv, ctx, T.JOURNEY)
            nxt = next((w for w in windows if w.first > int(lv)), None)
            flat_window = int(rules.walk_end) < int(T.JOURNEY.walk_end) and nxt is not None
            t["stretches"].append({"live": int(lv), "last": None if last is None else int(last),
                                   "flatten": int(rules.walk_end), "window": flat_window,
                                   "window_kind": nxt.kind if flat_window else "",
                                   "window_source": nxt.source if flat_window else ""})
        tickets.append(t)
    dropped = [(o.tag, why) for o, why in refused]
    calc = {"tickets": tickets, "cap": cap, "count": len(tickets), "number": list(range(1, len(tickets) + 1)),
            "total": int(c["contracts"]) * len(tickets), "decision": int(group[0].decision), "alert": int(at),
            "live": live, "account": account,
            "windows": [{"first": w.first, "last": w.last, "kind": w.kind, "source": w.source} for w in windows]}
    src = {"design": decl, "day": day.isoformat(), "calc": calc, "library": _library(decl)}
    d = _Doc(src)
    D, Cp, K = "design", ("design", "components", ci), "calc"
    pair = len(tickets) > 1
    d.line("TRADE ALERT -- enter by hand. This message is not an order and nothing sends it anywhere.")
    d.line("Design ", _v(D, "design_id"), ". Date ", _v("day"), ". Alert ", _ct(K, "alert"),
           " CT; the order goes live on the bar stamped ", _ct(K, "live"), " CT.")
    d.line("Firm ", _v(D, "firm"), " (", _v("library", "plan"), "), account ", _v(K, "account"), ": ",
           ROLES[decl["firm"]][decl["accounts"][ai]["role"]][1], " -- the rotation's pick (", _v(D, "rotation", "rule"),
           ") among the accounts you hold today.")
    if pair:
        d.line("Instrument ", _v(D, "instrument"), ", ", _v(*Cp, "contracts"), " contracts on each ticket, ",
               _v(K, "total"), " for the tickets together (the firm's verified limit for this account: ", _v(K, "cap"),
               ").")
        d.line(PAIR_WORDS)
        d.line(*_SOURCE_LINE)
    else:
        d.line("Instrument ", _v(D, "instrument"), ", ", _v(*Cp, "contracts"), " contracts (the firm's verified limit "
               "for this account: ", _v(K, "cap"), ").")
    for j, t in enumerate(tickets):
        T_ = (K, "tickets", j)
        lead: list[Any] = ["Ticket ", _v(K, "number", j), " of ", _v(K, "count"), ": "] if pair else []
        if isinstance(trig, T.P14Breakout):
            d.line(*lead, "Side ", ("side", T_ + ("side",)), ": the breakout was ", SIGN_WORDS[t["tag"][-1]],
                   "; the rule is ", SIDE_RULE_WORDS[c["side_rule"]], ".")
        else:
            kind_name = tuple(t["tag"].split("_", maxsplit=1))
            d.line(*lead, "Side ", ("side", T_ + ("side",)), ": the level is ", *LEVEL_PARTS[kind_name], ", ",
                   *ROLE_PARTS[t["role"]], "; the rule at this level is ", SIDE_RULE_WORDS[t["rule"]], ".")
        if t["kind"] == W.MARKET:
            d.line("  Order ", ("order", T_ + ("kind",)), " at the open of the bar stamped ", _ct(K, "live"), " CT.")
        else:
            if isinstance(trig, T.P14Breakout):
                d.line("  Order ", ("order", T_ + ("kind",)), " at the price at the alert: the close of the bar stamped ",
                       _st(K, "alert"), " CT (it ends at ", _ct(K, "alert"), " CT), as your platform shows it when "
                       "this alert reaches you.")
            elif t["kind"] == W.LIMIT_ENTRY:
                d.line("  Order ", ("order", T_ + ("kind",)), " at the level itself, read on your chart.")
            else:
                d.line("  Order ", ("order", T_ + ("kind",)), " ", _v(*T_, "beyond"), " tick ", BEYOND_WORDS[t["side"]],
                       " the level, read on your chart.")
        for k, s in enumerate(t["stretches"]):
            S = T_ + ("stretches", k)
            if t["kind"] == W.MARKET:
                parts: list[Any] = ["  It fills at the open of that bar"]
            elif s["last"] is None:
                parts = ["  Working from the bar stamped ", _ct(*S, "live"), " CT"]
            else:
                parts = ["  Working on the bars stamped ", _ct(*S, "live"), " CT through ", _ct(*S, "last"),
                         " CT, then cancelled if unfilled"]
            if s["window"]:
                parts += ["; a position from it is closed at the close of the bar stamped ", _st(*S, "flatten"),
                          " CT (it ends at ", _ct(*S, "flatten"), " CT), when ", WINDOW_WORDS[s["window_kind"]],
                          " starts (", _v(*S, "window_source"), ")."]
            else:
                parts += ["; a position from it is flattened by the close of the bar stamped ", _st(*S, "flatten"),
                          " CT (it ends at ", _ct(*S, "flatten"), " CT) at the latest."]
            d.line(*parts)
            if t["kind"] != W.MARKET:
                d.line("  Each time you place it (", ("again, " if k else ""), "the bar stamped ", _ct(*S, "live"),
                       " CT), ", VOID_AT_LIVE, VOID_END[pair])
    for tag, why in dropped:
        kind_name = tuple(tag.split("_", maxsplit=1))
        d.line("Not offered today: the ticket at ", *LEVEL_PARTS[kind_name], " -- ", REASON_WORDS.get(why, why), ".")
    if isinstance(trig, T.RL3Tickets):
        d.line(PLATFORM_LEVEL)
    d.line("The trigger's own side, cleared by the no-harm floor under ", _v(D, "side", "no_harm_row"), ".")
    d.line("Stop ", _v(*Cp, "stop_ticks"), " ticks from your fill; target ", ("target", Cp + ("stop_ticks",),
           Cp + ("rr",)), " ticks (reward to risk ", _v(*Cp, "rr"), "); entered with the order as a bracket.")
    d.line("Today's windows (no entry and no fill inside them):")
    for j, w in enumerate(windows):
        Wp = (K, "windows", j)
        d.line("  - ", WINDOW_WORDS[w.kind], " (", _v(*Wp, "source"), "): the bars stamped ", _ct(*Wp, "first"),
               " CT through ", _ct(*Wp, "last"), " CT")
    d.line("Why it is offered today: component ", _v(*Cp, "name"), " (", _v(*Cp, "session"), ") fired at ",
           _ct(K, "decision"), " CT, on the bars closed by then; the calendar known before the alert does not void the "
           "day for it; no window covers the bar stamped ", _ct(K, "live"), " CT.")
    d.line("Before you enter: enter only if, at this firm, no position is open, no entry order is working",
           (" (these tickets count as one order)" if pair else ""), ", and the last position closed at least ",
           _v(D, "execution", "gap_minutes"), " minutes ago -- the firm's state is yours to check.")
    d.line(OPPOSITE)
    d.line(NO_COPY)
    return d.done()


def render_alert(carried: Carried, component: str, hist: T.History, i: int, at: int, sources: DC.Sources,
                 router: R.Router, accounts: Sequence[str]) -> Rendered:
    """The alert of `component`'s trigger at slot `at` of day `i` of `hist` (the module docstring), the account the
    router's pick among `accounts` (those alive today); `AlertRefused` otherwise (its `reason` says whether a
    not-offered notice is due)."""
    return _alert(carried, component, hist, i, at, sources, router, accounts)


def render_offer(carried: Carried, component: str, hist: T.History, i: int, at: int, sources: DC.Sources,
                 router: R.Router, accounts: Sequence[str]) -> Rendered:
    """The alert, or the not-offered notice when the day or the trigger voids the offer; a mismatch, or no offer at
    that moment, still refuses."""
    try:
        return _alert(carried, component, hist, i, at, sources, router, accounts)
    except AlertRefused as e:
        if e.reason in ("mismatch", "no_offer"):
            raise
        return _notice(carried, component, _live_of(carried, component, hist, i, at, sources), e.reason)


def _live_of(carried: Carried, component: str, hist: T.History, i: int, at: int, sources: DC.Sources) -> int:
    decl = carried.decl
    _, c = _comp(decl, component)
    day = parse_day(hist.days[i], "the day")
    trig = next(x for x in design_on(decl, carried.space, day).components if x.name == c["name"]).trigger
    ctx = DC.alert_context(sources, UNDERLYING_OF[decl["instrument"]], day, i, windows=_day_windows(decl, day))
    offs = [o for o in trig.offers(cut_history(hist, i, at), i, ctx) if int(o.alert) == int(at)]
    return int(offs[0].live)


def _notice(carried: Carried, component: str, live: int, reason: str) -> Rendered:
    decl = _carried(carried)
    ci, _ = _comp(decl, component)
    if reason not in REASON_WORDS:
        raise _mismatch(f"reason {reason!r} is not one of the notice's reasons")
    src = {"design": decl, "offer": {"live": int(live)}}
    d = _Doc(src)
    d.line("NOT OFFERED today: component ", _v("design", "components", ci, "name"), "'s order on the bar stamped ",
           _ct("offer", "live"), " CT -- do not enter it.")
    d.line("Why: ", REASON_WORDS[reason], ".")
    return d.done()


def render_trade(carried: Carried, trade: Any) -> Rendered:
    """A scheduled trade (`components.ScheduledTrade`, or routed): its side is the evaluation's coin whatever its label
    says (`components._trade_row`), so it gets the not-offered notice, never an alert (R-1)."""
    tr = trade.trade if isinstance(trade, R.RoutedTrade) else trade
    if not isinstance(tr, C.ScheduledTrade):
        raise _mismatch("not a scheduled trade")
    decl = _carried(carried)
    _, c = _comp(decl, tr.component)
    if tr.source != c["trigger"]["source"]:
        raise _mismatch("the trade's source is not its component's trigger")
    return _notice(carried, tr.component, int(tr.live), "coin_side")


__all__ = ["REQUIRED", "TRANSFORMS", "FIRMS", "PLANS", "ROLES", "VOID_WORDS", "RESEARCH_WORDS", "REASON_WORDS",
           "CONVENTIONS", "RESULT_COLUMNS", "PlaybookRefused", "AlertRefused", "Piece", "Rendered", "ResultFile",
           "Carried", "resolve", "parse_day", "strict_json", "plan_name", "micros_per_mini", "size_cap",
           "decision_log", "canonical_rule", "window_space", "design_on", "check_declaration", "row_key",
           "accept_result", "load_carried", "cut_history", "render_playbook", "render_alert", "render_offer",
           "render_trade"]
