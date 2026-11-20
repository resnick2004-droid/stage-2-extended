"""The restart plan's Wave 3.5: the playbook a user trades a carried design from by hand, the one-trade alert, and the
"not offered" notice (CHARTER 3.5: "The output is a playbook ... plus the exact alert format, so that it can be traded
by hand"; E-221, the operator's O-4 ruling). Corrective cycle 1 (the red team's BUILD_W35 note, R-1 to R-13, N-1 to
N-3, and the lead's rulings).

    from extended import playbook as PB
    carried = PB.load_carried("prereg/<design>_playbook.json")      # pinned, every cited row and result file checked
    page = PB.render_playbook(carried)                               # -> Rendered: .text, .pieces
    msg = PB.render_offer(carried, offer, "pm_brk", "ts_b2", "2021-03-16", sources)   # the alert, or a notice
    note = PB.render_trade(carried, routed)                          # a scheduled (coin-sided) trade: not offered

**Hand entry only** (CLAUDE.md; DIRECTIVE Part 1: no automated or API order entry, it gets prop accounts banned). The
playbook and the alert are plain text for a person to read and act on by hand. Nothing here places, sends, schedules or
formats an order for a machine: no network, no broker, no process, no file written. `Rendered.pieces` (where each
value came from) is for the tests' tracing only and is never to be exported as an order record (N-1).

**The carried design** (`load_carried`, R-7). The declaration is a JSON file whose sha256 (of its bytes, line ends as
LF) is pinned in its carrying row of this repository's `DECISIONS.md` as `` `<path>` sha256 `<hex>` ``; every row id it
cites (`row`, `side.no_harm_row`, `bankroll.row`) is looked up there, and a missing one refuses. The carrying row and
the no-harm row name the design id. Two result files are read (R-6), each only when **all** hold: its manifest is from
a clean run (`provenance.clean_run`), of a named commit (not `unknown`, not `-dirty`, `git_dirty` false), not
exploratory, for this design (`parameters.design_id`) under the expected convention (`parameters.convention`); it
passes `extended.results.verify_result`; the sha256 its manifest records is the one pinned for it in its row; it is
not git-ignored and not on the licence list (`.gitignore`'s licensed-price derivatives, E-179, E-245) and the licence
guard (`extended.price_levels`, Q-131) finds no price level in it. The CSV and its manifest are read from one resolved
path. The files: the **expected journey** (`expected.file`, convention `zero_edge`, pinned in the carrying row) and
the **no-harm floor** (`side.no_harm_file`, convention `no_harm_real_path`, pinned in the no-harm row), whose
`no_harm|search|<component>|verdict` cell must read `pass` for every component: a component whose floor failed or is
absent offers no playbook side, and the design is not carried (CHARTER 3.5).

**The declaration's keys** (`REQUIRED`): `design_id`, `row`, `firm` and `plan` (closed: the firms and plans whose
verified rules this tree loads, `FIRMS`, `PLANS`), `instrument`, `accounts` (each `id`, `role` -- `evaluation` or
`funded`), `side` (`no_harm_row`, `no_harm_file`), `components` (each `name`, `session`, `first`, `last` (live slots:
minutes after 17:00 CT, `walker.slot`), `stop_ticks`, `rr`, `contracts`, `latency` (a timed trigger's L; null for a
latency-free one, its single cell), `side_rule` (a key of the closed vocabulary `trigger_sides.RULES`; RL3's a mapping
level -> fade or break) and `trigger` (`source`, `params`)), `rotation`, `execution`, `news_windows` (each `source`,
`release`, `before`, `after`, `dates`: the release days on the verified record), `void_rules` (the library's whole
set, `VOID_WORDS`), `void_dates`, `session_anchors`, `dates`, `bankroll` (`budget`, `row`), `expected` (`file`,
`rows`: each `label`, `section`, `block` (`search` or `held_out`), `measure`, `stat`). Labels, side rules, roles,
sources and reasons carry no digit and no free figure (R-10): every figure printed is an input value, traced.

**Every number comes from an input, never from this file.** A rendered text is a sequence of pieces (`Piece`): a
template literal, which holds no digit, or a value, which names its transform and the input paths it is computed from
(`TRANSFORMS`). The same input gives byte-identical text.

**The side** (R-1). The playbook offers a side only as `trigger_sides.trigger_side` computes it from the component's
own trigger (a typed `TriggerSide`); it never takes a side from a trade. A scheduled trade (`components.ScheduledTrade`,
`router.RoutedTrade`) is the evaluation's, coin-sided by construction whatever its label says, so `render_trade`
gives it the not-offered notice and never an alert.

**The alert** (`render_alert`, `render_offer`) is rendered from the trigger's `Offer` before execution (R-11): no fill,
no exit, no outcome. It holds the offer to the declaration and the calendar itself (R-2 to R-4), never on the caller's
word: the offer must be one the component's trigger makes (its source, decision, alert, live = alert + L for a timed
trigger or the trigger's own live slot, entry, expiry, tag and group), inside the component's window and before the
firm's last new entry; the account must be the declaration's, in the component's pool under `by_component`; the size
at most the firm's verified limit for the account's plan (`size_cap`). The day's flags come from the void calendar
(`day_calendar`, through `triggers.context_for` with what the trigger reads), its news windows from the declaration's
dated record; `triggers.admit` refuses an offer live inside a window, on a void, FOMC or overnight-refused day; a
component reading the previous day's levels refuses on a `prior_void` day. The flatten time and the working stretches
are the library's (`triggers.rules_for`, `triggers.segments`): a position open when a window starts is closed at its
start. **No price is ever printed** (R-5): an order is stated relative to what the user reads on the platform at the
alert (the alert bar's close, the level, ticks beyond it); the offer's level never enters the text.
"""
from __future__ import annotations

import csv
import fnmatch
import hashlib
import io
import json
import math
import re
from dataclasses import dataclass, field, fields
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extended import ROOT
from extended import components as C
from extended import day_calendar as DC
from extended import lever_space as LS
from extended import modes_terms as M
from extended import router as R
from extended import trigger_sides as TS
from extended import triggers as T
from extended import walker as W

REQUIRED = ("design_id", "row", "firm", "plan", "instrument", "accounts", "side", "components", "rotation", "execution",
            "news_windows", "void_rules", "void_dates", "session_anchors", "dates", "bankroll", "expected")
COMPONENT_KEYS = ("name", "session", "first", "last", "stop_ticks", "rr", "contracts", "latency", "side_rule", "trigger")
EXECUTION_KEYS = ("gap_minutes", "closed_window", "bls_clear", "limit_window_min", "flatten", "last_entry")
SIDE_KEYS = ("no_harm_row", "no_harm_file")
EXPECTED_KEYS = ("label", "section", "block", "measure", "stat")
NEWS_KEYS = ("source", "release", "before", "after", "dates")
ROW_LINE = re.compile(r"^\| (E-\d\d\d+) \|.*$", re.M)
HASH = hashlib.sha256().name                          # the pins' and manifests' hash, by its library name
PIN = re.compile(r"`([^`]+)` " + HASH + r" `([a-f\d]+)`")
IDENT = re.compile(r"[A-Za-z][A-Za-z\d_.-]*$")
DIGIT = re.compile(r"\d")
SHA_LEN = len(hashlib.sha256().hexdigest())

#: the firms whose trading day the library loads: `lever_space.trading_day` reads Topstep's `trading_hours`, and the
#: per-firm loader (`lever_space_firms`, E-249) gives no other firm's day yet (MFFU's T2 and T3 wait on its trading
#: hours' parse; Lucid's hours on the operator's transcription); a firm string is refused unless it is one of these (R-9)
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
#: the micro-to-mini count, from the rule that states it
RATIO_RULE = ("combine_position_size_limit", r"Micros and minis count at a (?P<micro>\d+):(?P<mini>\d+) ratio")
#: the instruments and their underlying (the calendar's market); a micro counts at the firm's ratio
UNDERLYING_OF = {"MNQ": "NQ", "NQ": "NQ"}
MICRO = ("MNQ",)

#: the library's sided trigger classes (P-16 builds but offers no side; the coin is the evaluation's device)
TRIGGERS: dict[str, Callable[..., Any]] = {cls.__dataclass_fields__["source"].default: cls
                                           for cls in (T.P14Breakout, T.P16Marks, T.RL3Tickets)}
SLOT_PARAMS = ("first", "last", "cutoff", "marks")
ANCHOR_OF = {"asia": "asia", "london": "london", "ny_am": "ny", "ny_pm": "ny"}
BLOCKS = {"search": "search years: the years this design was chosen on, so likely better than what follows",
          "held_out": "held-out years, reported beside, never judged"}
#: a result file's convention -> what its figures are, printed with them (R-6: from the manifest, never a constant)
CONVENTIONS = {
    "zero_edge": "These figures were measured with every trade's direction replaced by a fair coin (zero edge), over "
                 "many start days: they are what the account policy gives without any skill in direction. Your own "
                 "journey will differ.",
    "no_harm_real_path": "the trigger's own side against the coin's on the real path, same fills, no redraw",
}
EXPECTED_CONVENTION, NO_HARM_CONVENTION = "zero_edge", "no_harm_real_path"
PASS = "pass"

TRIGGER_WORDS = {
    T.P14Breakout: "a breakout: the first one-minute close above the previous completed reference bar's high, or below "
                   "its low (the reference bar's length in minutes is the parameter k), at most once per reference bar",
    T.RL3Tickets: "pre-session tickets at the day's levels of one kind, fixed when the alert is sent, before the "
                  "regular session's first fill; one ticket per level, the tickets of a kind one-cancels-other, "
                  "unfilled tickets cancelled at the cutoff",
}
ENTRY_WORDS = {
    T.MARKET: "a market order when the order goes live",
    T.LIMIT: "a limit order at the price at the alert (the close of the one-minute bar ending at the alert), "
             "working the limit window from when it goes live, cancelled if unfilled",
    T.TICKET: "each level's ticket by its declared rule: a fade is a limit at the level, a break a stop one tick "
              "beyond it",
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
LEVEL_WORDS = {
    (_PD, "hi"): "the previous day's regular-session high",
    (_PD, "lo"): "the previous day's regular-session low",
    (_ON, "hi"): "the overnight high (from the reopen to the regular open)",
    (_ON, "lo"): "the overnight low (from the reopen to the regular open)",
    (_PDC, "lvl"): "the previous day's regular-session close (its last bar before the regular close)",
    (_RN, "up"): "the next round hundred above the price at the alert",
    (_RN, "dn"): "the next round hundred below the price at the alert",
}
#: the price at RL3's alert is the close of the last bar before the regular open (`triggers.rl3_levels`' P_ref)
ROLE_WORDS = {1: "a resistance: above the price at the alert (the close of the last bar before the regular open) -- "
                 "check it on your chart",
              -1: "a support: below the price at the alert (the close of the last bar before the regular open) -- "
                  "check it on your chart"}
ROTATION_WORDS = {
    "longest_waiting": "the next trade of a firm goes to the account whose last trade ended longest ago (an unused "
                       "account first; ties in the account order below)",
    "round_robin": "the next trade of a firm goes to the account after the one that took the firm's last trade, in the "
                   "account order below",
    "by_component": "each component's trades go to its own pool of accounts below, the one waiting longest first (a "
                    "component without a pool uses every account)",
}
#: the void calendar's rules as the library applies them (`day_calendar.day_flags`, `triggers.admit`, `rl3_levels`)
VOID_WORDS = {
    "fomc": "an FOMC statement day: no trade at all that day",
    "holiday": "an exchange holiday or a scheduled close before the walk's last bar: no trade that day",
    "early_close": "an early end of the day's bars, or a data defect on the calendar: no trade that day",
    "short_overnight": "an overnight session the calendar voids (its data-integrity void days, too many minutes "
                       "missing, or no last bar before the regular open for a component that reads it): no trade from a component "
                       "that reads the overnight bars",
    "prior_abbreviated": "the day after an abbreviated session, a closure, a void day or a contract roll: no trade "
                         "from a component that reads the previous day's levels",
}
WINDOW_WORDS = {"news": "a news window", "closed": "the closed window after the regular open",
                "bls": "the jobs-report window", "unscheduled": "an unscheduled release"}
REASON_WORDS = {
    "position": "a position is already open at this firm (one position at a time)",
    "order": "an entry order is already working at this firm",
    "gap": "the firm's last position closed less than the required flat time ago",
    "fomc": "today is an FOMC statement day",
    "calendar": "the void calendar voids today for this component",
    "declared_void": "today is on the playbook's list of void days",
    "overnight": "the order would go live in the overnight session, which this design does not trade",
    "news": "the order would go live inside a news window",
    "closed": "the order would go live inside the closed window after the regular open",
    "bls": "today is a jobs-report day and the order would go live before the report window ends",
    "unscheduled": "an unscheduled release has closed trading for this order",
    "expired": "nothing of the order's working window is left",
    "prior_void": "the previous day's levels are void today (an abbreviated or void day, a closure or a roll before it)",
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
            "reaches you.")


class PlaybookRefused(ValueError):
    """A declaration or result the playbook cannot stand behind (a missing field, an unpinned file, a row not in the
    log, a value the library or the ledger disagrees with)."""


class AlertRefused(ValueError):
    """An offer the alert is not sent for. `reason` is a key of `REASON_WORDS` when the day or the trigger voids it (a
    not-offered notice is due), or `mismatch` when the offer, the account or the size disagrees with the declaration."""

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
    return DC.label(DC.anchored_starts(date.fromisoformat(day))[ANCHOR_OF[session]])


#: transform name -> function of the resolved input values (in path order)
TRANSFORMS: dict[str, Callable[..., str]] = {
    "text": _text,
    "ct": lambda s: DC.label(int(s)),
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


# ------------------------------------------------------------------------------------------------ the ledger and the firm


def _plain(v: Any, what: str) -> str:
    """Words carrying no figure (R-10): a non-blank string with no digit."""
    if not isinstance(v, str) or not v.strip() or DIGIT.search(v):
        raise PlaybookRefused(f"{what} is plain words with no digit and no figure, got {v!r}")
    return v


def _ident(v: Any, what: str) -> str:
    if not isinstance(v, str) or not IDENT.match(v):
        raise PlaybookRefused(f"{what} is an identifier (a letter, then letters, digits, '_', '.', '-'), got {v!r}")
    return v


def _int(v: Any, what: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise PlaybookRefused(f"{what} is a whole number, got {v!r}")
    return v


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


def decision_log(root: Path | str = ROOT) -> dict[str, str]:
    """The rows of `DECISIONS.md` at `root`: id -> its whole line (a repeated id refuses)."""
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


def _pins(row: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel, sha in PIN.findall(row):
        if len(sha) == SHA_LEN:
            out[rel] = sha
    return out


def _names(row: str, design_id: str, what: str) -> None:
    if not re.search(r"(?<![\w-])" + re.escape(design_id) + r"(?![\w-])", row):
        raise PlaybookRefused(f"{what} does not name the design {design_id}")


# ------------------------------------------------------------------------------------------------ the declaration


def _need(m: Any, keys: Sequence[str], what: str) -> None:
    if not isinstance(m, Mapping):
        raise PlaybookRefused(f"{what} is not a mapping")
    missing = [k for k in keys if k not in m]
    if missing:
        raise PlaybookRefused(f"{what} is missing {missing}")


def _iso(v: Any, what: str) -> str:
    try:
        date.fromisoformat(v)
    except (TypeError, ValueError) as e:
        raise PlaybookRefused(f"{what} is an ISO date, got {v!r}") from e
    return v


def _hhmm(text: str) -> tuple[int, int]:
    h, m = str(text).split(":")
    return int(h), int(m)


def _trigger(comp: Mapping[str, Any]) -> Any:
    trig = comp["trigger"]
    _need(trig, ("source", "params"), f"component {comp['name']}'s trigger")
    src = trig["source"]
    if src in TS.NO_SIDE and src not in TRIGGERS:
        raise PlaybookRefused(f"component {comp['name']}: {TS.NO_SIDE[src]}")
    if src not in TRIGGERS:
        raise PlaybookRefused(f"component {comp['name']}: trigger source {src!r} is not one of {sorted(TRIGGERS)}")
    params = {k: (tuple(v) if isinstance(v, list) else v) for k, v in dict(trig["params"]).items()}
    try:
        obj = TRIGGERS[src](**params)
    except (TypeError, ValueError, RuntimeError) as e:
        raise PlaybookRefused(f"component {comp['name']}: the library refuses its trigger: {e}") from e
    try:
        TS.check_rule(obj, comp["side_rule"])
    except TS.SideRefused as e:
        raise PlaybookRefused(f"component {comp['name']}: {e}") from e
    lat = comp["latency"]
    if obj.latency_free:
        if lat is not None or LS.latency_cells(src) != (None,):
            raise PlaybookRefused(f"component {comp['name']}: a latency-free trigger's L is its single cell (null)")
    else:
        if _int(lat, f"component {comp['name']}'s L") not in LS.latency_cells(src) or int(obj.latency) != lat:
            raise PlaybookRefused(f"component {comp['name']}: its L is not a declared L of its timed trigger's own")
    first, last = _int(comp["first"], "a window's first"), _int(comp["last"], "a window's last")
    if isinstance(obj, T.P14Breakout) and not (first - lat <= int(obj.first) <= int(obj.last) <= last - lat):
        raise PlaybookRefused(f"component {comp['name']}: its trigger's alerts lie outside its window less L")
    if isinstance(obj, T.RL3Tickets) and not first <= T.LIVE_0900 <= last:
        raise PlaybookRefused(f"component {comp['name']}: its tickets' live slot lies outside its window")
    return obj


def _routes(decl: Mapping[str, Any], name: str) -> list[str]:
    """The accounts a component's trades may take (its pool under `by_component`, else every account)."""
    rot = decl["rotation"]
    pools = dict(rot.get("pools", {}))
    if rot["rule"] == "by_component" and name in pools:
        return list(pools[name])
    return [a["id"] for a in decl["accounts"]]


def check_declaration(decl: Mapping[str, Any]) -> C.Design:
    """Every required field present and every value held to the library and the firm's verified ledger; returns the
    design as the scheduler's own object (refuses otherwise). The pins and rows are `load_carried`'s."""
    _need(decl, REQUIRED, "the declaration")
    _ident(decl["design_id"], "the design id")
    _ident(decl["row"], "the carrying row")
    firm = decl["firm"]
    if firm not in FIRMS:
        raise PlaybookRefused(f"firm {firm!r} is not one whose verified trading day this tree loads ({FIRMS})")
    plan_name(firm, decl["plan"])
    if decl["instrument"] not in UNDERLYING_OF:
        raise PlaybookRefused(f"instrument {decl['instrument']!r} is not one of {sorted(UNDERLYING_OF)}")
    side = decl["side"]
    _need(side, SIDE_KEYS, "the side rule")
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
    try:
        R.Routing(rot["rule"], {k: tuple(v) for k, v in dict(rot.get("pools", {})).items()})
    except R.RoutingRefused as e:
        raise PlaybookRefused(str(e)) from e
    names = []
    for c in decl["components"]:
        _need(c, COMPONENT_KEYS, f"component {c.get('name') if isinstance(c, Mapping) else c!r}")
        names.append(c["name"])
    for name, pool in dict(rot.get("pools", {})).items():
        if name not in names or any(a not in ids for a in pool):
            raise PlaybookRefused(f"pool {name!r} names a component or an account the declaration does not hold")
    roles = {a["id"]: a["role"] for a in accounts}
    comps = []
    for c in decl["components"]:
        _ident(c["name"], "a component name")
        n = _int(c["contracts"], f"component {c['name']}'s contracts")
        if n <= 0:
            raise PlaybookRefused(f"component {c['name']}: contracts are positive")
        for acct in _routes(decl, c["name"]):
            if n > size_cap(firm, roles[acct], decl["instrument"]):
                raise PlaybookRefused(f"component {c['name']}: its size exceeds the firm's verified limit for account "
                                      f"{acct}")
        trig = _trigger(c)
        try:
            comps.append(C.Component(c["name"], c["session"], int(c["first"]), int(c["last"]), trig,
                                     _int(c["stop_ticks"], "a stop"), float(c["rr"]), decl["instrument"]))
        except C.DesignRefused as e:
            raise PlaybookRefused(str(e)) from e
    try:
        design = C.Design(firm, tuple(comps))
    except C.DesignRefused as e:
        raise PlaybookRefused(str(e)) from e
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
    for w in decl["news_windows"]:
        _need(w, NEWS_KEYS, "a news window")
        _plain(w["source"], "a news window's source")
        try:
            T.release_window(_int(w["release"], "a release"), _int(w["before"], "a window's before"),
                             _int(w["after"], "a window's after"), w["source"])
        except ValueError as e:
            raise PlaybookRefused(f"news window {w['source']!r}: {e}") from e
        for d in w["dates"]:
            _iso(d, "a release date")
    rules = list(decl["void_rules"])
    if sorted(rules) != sorted(VOID_WORDS) or len(set(rules)) != len(rules):
        raise PlaybookRefused(f"the void rules are the library's whole set {sorted(VOID_WORDS)}, each once")
    for d in decl["void_dates"]:
        _need(d, ("date", "reason"), "a void date")
        _iso(d["date"], "a void date")
        if d["reason"] not in VOID_WORDS:
            raise PlaybookRefused(f"void date {d['date']}: its reason is not one of the void rules")
    anchors = decl["session_anchors"]
    for sess in sorted({c.session for c in comps}):
        key = ANCHOR_OF.get(sess)
        if key is None:
            continue
        if sess not in anchors:
            raise PlaybookRefused(f"session {sess}'s local anchor is not declared")
        tz, hhmm = anchors[sess]
        if (tz, *_hhmm(hhmm)) != DC.LOCAL_ANCHORS[key]:
            raise PlaybookRefused(f"session {sess}'s anchor differs from the void calendar's")
    for d in decl["dates"]:
        _iso(d, "a session-anchor date")
    bank = decl["bankroll"]
    _need(bank, ("budget", "row"), "the bankroll stop")
    if isinstance(bank["budget"], bool) or not isinstance(bank["budget"], (int, float)) or not bank["budget"] > 0:
        raise PlaybookRefused("the bankroll budget is a positive number")
    exp = decl["expected"]
    _need(exp, ("file", "rows"), "the expected journey")
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
    return design


def row_key(e: Mapping[str, Any]) -> str:
    return "|".join(str(e[k]) for k in ("section", "block", "measure", "stat"))


# ------------------------------------------------------------------------------------------------ the result files


@dataclass(frozen=True)
class ResultFile:
    """A result file accepted under R-6: its path relative to the root, its manifest's commit and convention, and
    its rows' cells as text, key 'section|block|measure|stat' -> the value's own text (each key once)."""

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


def _price_findings(name: str, text: str) -> int:
    from extended import price_levels as PL

    return len(PL.scan_lines(name, text.splitlines(), allow=()))


def accept_result(root: Path | str, rel: Any, *, design_id: str, convention: str, pinned: str) -> ResultFile:
    """A result file under R-6 and R-5 (the module docstring), or `PlaybookRefused`."""
    root = Path(root).resolve()
    if not isinstance(rel, str) or not rel.startswith("results/") or not rel.endswith(".csv"):
        raise PlaybookRefused(f"a result file is named results/<name>.csv under the root, got {rel!r}")
    p = (root / rel).resolve()
    if p.parent != (root / "results").resolve():
        raise PlaybookRefused(f"{rel} does not resolve inside the root's results folder")
    if _ignored(rel, (ROOT, root)):
        raise PlaybookRefused(f"{rel} is git-ignored (a licensed-price derivative, on the licence list): it is never printed")
    mpath = Path(str(p) + ".manifest.json")
    if not p.is_file() or not mpath.is_file():
        raise PlaybookRefused(f"{rel} or its manifest is missing")
    ok, msg = _verify_result(p)
    if not ok:
        raise PlaybookRefused(f"{rel} does not verify: {msg}")
    man = json.loads(mpath.read_bytes())
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != man.get(HASH) or man.get(HASH) != pinned:
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
    params = man.get("parameters") or {}
    if params.get("design_id") != design_id or params.get("convention") != convention:
        raise PlaybookRefused(f"{rel} is not this design's {convention} result (parameters design_id, convention)")
    text = raw.decode()
    if _price_findings(p.name, text):
        raise PlaybookRefused(f"{rel}: the licence guard finds a price level in it: it is never printed")
    values: dict[str, str] = {}
    for r in csv.DictReader(io.StringIO(text)):
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
        out[k] = res.values[k]
    return out


# ------------------------------------------------------------------------------------------------ the carried design

_MINT = object()


@dataclass(frozen=True)
class Carried:
    """A carried design as `load_carried` accepted it: the declaration's bytes (re-read on every use, so never edited
    in place), its path and pinned sha256, the cited rows, the design, and the two result files' picked values."""

    decl_file: str
    decl_sha: str
    decl_bytes: bytes
    rows: Mapping[str, str]
    design: C.Design
    expected: ResultFile
    no_harm: ResultFile
    _mint: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not (isinstance(self._mint, tuple) and self._mint and self._mint[0] is _MINT
                and self._mint[-1] == (self.decl_file, self.decl_sha, self.expected, self.no_harm)
                and hashlib.sha256(self.decl_bytes).hexdigest() == self.decl_sha):
            raise PlaybookRefused("a carried design is made only by load_carried, from its pinned declaration")

    @property
    def decl(self) -> dict:
        return json.loads(self.decl_bytes)


def load_carried(decl_file: str, *, root: Path | str = ROOT) -> Carried:
    """The carried design from its pinned declaration (the module docstring; R-1, R-6, R-7), or `PlaybookRefused`."""
    root = Path(root).resolve()
    rows = decision_log(root)
    p = (root / decl_file).resolve()
    try:
        rel = p.relative_to(root).as_posix()
    except ValueError as e:
        raise PlaybookRefused(f"the declaration {decl_file} lies outside the root") from e
    if not p.is_file():
        raise PlaybookRefused(f"no declaration at {rel}")
    data = p.read_bytes().replace(b"\r\n", b"\n")
    sha = hashlib.sha256(data).hexdigest()
    try:
        decl = json.loads(data)
    except ValueError as e:
        raise PlaybookRefused(f"the declaration {rel} is not JSON") from e
    _need(decl, REQUIRED, "the declaration")
    carrying = _cited(rows, decl["row"], "the carrying row")
    pins = _pins(carrying)
    if pins.get(rel) != sha:
        raise PlaybookRefused(f"the declaration {rel} is not the file pinned in {decl['row']} (its hash {sha})")
    design = check_declaration(decl)
    did = decl["design_id"]
    _names(carrying, did, f"the carrying row {decl['row']}")
    nh_row = _cited(rows, decl["side"]["no_harm_row"], "the side's no-harm row")
    _names(nh_row, did, f"the no-harm row {decl['side']['no_harm_row']}")
    _cited(rows, decl["bankroll"]["row"], "the bankroll budget's row")
    exp_rel, nh_rel = decl["expected"]["file"], decl["side"]["no_harm_file"]
    expected = accept_result(root, exp_rel, design_id=did, convention=EXPECTED_CONVENTION,
                             pinned=pins.get(exp_rel, ""))
    expected = ResultFile(expected.file, expected.commit, expected.convention,
                          _picked(expected, [row_key(e) for e in decl["expected"]["rows"]]))
    no_harm = accept_result(root, nh_rel, design_id=did, convention=NO_HARM_CONVENTION,
                            pinned=_pins(nh_row).get(nh_rel, ""))
    verdicts = {}
    for c in decl["components"]:
        k = "|".join(("no_harm", "search", c["name"], "verdict"))
        v = no_harm.values.get(k)
        if v != PASS:
            raise PlaybookRefused(f"component {c['name']}: its no-harm floor {'failed' if v else 'is absent'} "
                                  f"({nh_rel}): it offers no playbook side, and the design is not carried")
        verdicts[k] = v
    no_harm = ResultFile(no_harm.file, no_harm.commit, no_harm.convention, verdicts)
    cited = {r: rows[r] for r in (decl["row"], decl["side"]["no_harm_row"], decl["bankroll"]["row"])}
    return Carried(rel, sha, data, cited, design, expected, no_harm,
                   _mint=(_MINT, (rel, sha, expected, no_harm)))


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
            "max_latency": max(T.LATENCIES), "tickets_alert": T.RTH_OPEN, "tickets_live": T.LIVE_0900,
            "hash": HASH}


# ------------------------------------------------------------------------------------------------ the playbook


def render_playbook(carried: Carried) -> Rendered:
    """The playbook's plain text (the module docstring); refuses anything but a carried design."""
    decl = _carried(carried)
    exp, nh = carried.expected, carried.no_harm
    src = {"design": decl, "library": _library(decl), "file": {"decl": carried.decl_file, "sha": carried.decl_sha},
           "expected": {"file": exp.file, "commit": exp.commit, **exp.values},
           "no_harm": {"file": nh.file, "commit": nh.commit}}
    d = _Doc(src)
    D, L = "design", "library"
    d.line("PLAYBOOK -- design ", _v(D, "design_id"), " (carried under ", _v(D, "row"), ")")
    d.line("The declaration: ", _v("file", "decl"), ", ", _v(L, "hash"), " ", _v("file", "sha"), " (pinned in ", _v(D, "row"),
           ").")
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
        d.line("Component ", _v(*P, "name"), " -- session ", _v(*P, "session"), ": orders go live from ",
               _ct(*P, "first"), " CT to ", _ct(*P, "last"), " CT.")
        d.line("  Trigger (", _v(*P, "trigger", "source"), "): ", TRIGGER_WORDS[cls], ".")
        for k in sorted(c["trigger"]["params"]):
            v = c["trigger"]["params"][k]
            if k in SLOT_PARAMS and isinstance(v, (list, tuple)):
                parts: list[Any] = ["    ", k, ": "]
                for j, _ in enumerate(v):
                    parts += ([", "] if j else []) + [_ct(*P, "trigger", "params", k, j), " CT"]
                d.line(*parts)
            elif k in SLOT_PARAMS:
                d.line("    ", k, ": ", _ct(*P, "trigger", "params", k), " CT")
            elif isinstance(v, bool):
                d.line("    ", k, ": ", ("yesno", (*P, "trigger", "params", k)))
            else:
                d.line("    ", k, ": ", _v(*P, "trigger", "params", k))
        entry = c["trigger"]["params"].get("entry", T.TICKET if cls is T.RL3Tickets else T.MARKET)
        if cls is T.RL3Tickets:
            d.line("  Entry: ", ENTRY_WORDS[entry], ". The tickets are fixed at ", _ct(L, "tickets_alert"),
                   " CT, when the alert is sent, and go live at ", _ct(L, "tickets_live"), " CT.")
        else:
            d.line("  Entry: ", ENTRY_WORDS[entry], ". The alert reaches you ", _v(*P, "latency"),
                   " minutes before the order goes live.")
        d.line("  Side (the trigger's own, cleared by the no-harm floor under ", _v(D, "side", "no_harm_row"), "):")
        if cls is T.RL3Tickets:
            kind = c["trigger"]["params"]["kind"]
            for name in TS.rl3_names(carried.design.components[i].trigger):
                d.line("    at ", LEVEL_WORDS[(kind, name)], ": ", SIDE_RULE_WORDS[c["side_rule"][name]], ".")
        else:
            d.line("    ", SIDE_RULE_WORDS[c["side_rule"]], ".")
        d.line("  Size: ", _v(*P, "contracts"), " contracts of ", _v(D, "instrument"), ".")
        d.line("  Stop: ", _v(*P, "stop_ticks"), " ticks from your fill. Target: ", ("target", P + ("stop_ticks",),
               P + ("rr",)), " ticks (reward to risk ", _v(*P, "rr"), "). Both are placed with the entry as a bracket.")
        key = ANCHOR_OF.get(c["session"])
        if key is None:
            d.line("  The session opens at the reopen.")
        else:
            d.line("  The session's local open: ", _v(D, "session_anchors", c["session"], 1), " ",
                   _v(D, "session_anchors", c["session"], 0), ".")
            for j, _ in enumerate(decl["dates"]):
                d.line("    on ", _v(D, "dates", j), " that is ", ("anchor_ct", (D, "dates", j), P + ("session",)),
                       " CT")
    d.line("The no-harm floor's file: ", _v("no_harm", "file"), " (commit ", _v("no_harm", "commit"), "): ",
           CONVENTIONS[NO_HARM_CONVENTION], "; every component above passed it.")
    d.line("")
    d.line("EXECUTION RULES (every component)")
    E = (D, "execution")
    d.line("- One position or working entry order at a time per firm; after a position closes, wait at least ",
           _v(*E, "gap_minutes"), " minutes before the next entry.")
    d.line("- Limit orders work ", _v(*E, "limit_window_min"), " minutes from going live, then are cancelled.")
    d.line("- Closed window: no entry and no fill from ", _ct(*E, "closed_window", 0), " CT to ",
           _ct(*E, "closed_window", 1), " CT, every day.")
    d.line("- On a jobs-report day: no entry at or before ", _ct(*E, "bls_clear"), " CT.")
    d.line("- No new entry after ", _ct(*E, "last_entry"), " CT. Flatten every position by the bar ending ",
           _ct(*E, "flatten"), " CT at the latest.")
    d.line("- A working order is cancelled when a news or closed window starts; an open position is closed at its "
           "start.")
    d.line("News windows (no entry and no fill inside them):")
    if not decl["news_windows"]:
        d.line("  (none declared)")
    for i, w in enumerate(decl["news_windows"]):
        P = (D, "news_windows", i)
        parts = ["  - ", _v(*P, "source"), ": released at ", _ct(*P, "release"), " CT; the window runs from ",
                 _v(*P, "before"), " minutes before to ", _v(*P, "after"), " minutes after; on "]
        for j, _ in enumerate(w["dates"]):
            parts += ([", "] if j else []) + [_v(*P, "dates", j)]
        d.line(*parts, ".")
    d.line("Void days (no trade from the components named):")
    for r in decl["void_rules"]:
        d.line("  - ", VOID_WORDS[r], ".")
    for i, v in enumerate(decl["void_dates"]):
        d.line("  - ", _v(D, "void_dates", i, "date"), ": ", VOID_WORDS[v["reason"]], ".")
    d.line("")
    d.line("ACCOUNT ROTATION")
    rot = decl["rotation"]
    d.line("Rule ", _v(D, "rotation", "rule"), ": ", ROTATION_WORDS[rot["rule"]], ".")
    names = [c["name"] for c in decl["components"]]
    for name in sorted(dict(rot.get("pools", {}))):
        parts = ["  component ", _v(D, "components", names.index(name), "name"), ": "]
        for j, _ in enumerate(rot["pools"][name]):
            parts += ([", "] if j else []) + [_v(D, "rotation", "pools", name, j)]
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
    d.line("From the result file ", _v("expected", "file"), " (commit ", _v("expected", "commit"), "):")
    rows = decl["expected"]["rows"]
    held = {(e["section"], e["measure"], e["stat"]) for e in rows if e["block"] == "held_out"}
    for i, e in enumerate(rows):
        d.line("  - ", _v(D, "expected", "rows", i, "label"), ": ", _v("expected", row_key(e)), " (",
               BLOCKS[e["block"]], "; ", _v(D, "expected", "rows", i, "stat"), ")")
        if e["block"] == "search" and (e["section"], e["measure"], e["stat"]) not in held:
            d.line("    its held-out reading is not named here: read it beside before trusting this figure.")
    d.line(CONVENTIONS[carried.expected.convention])
    return d.done()


# ------------------------------------------------------------------------------------------------ the alert


def _comp(decl: Mapping[str, Any], name: Any) -> tuple[int, Mapping[str, Any]]:
    for i, c in enumerate(decl["components"]):
        if c["name"] == name:
            return i, c
    raise _mismatch(f"component {name!r} is not one of the declaration's")


def _account(decl: Mapping[str, Any], acct: Any) -> int:
    for i, a in enumerate(decl["accounts"]):
        if a["id"] == acct:
            return i
    raise _mismatch(f"account {acct!r} is not one of the declaration's")


def _check_offer(decl: Mapping[str, Any], c: Mapping[str, Any], trig: Any, off: Any) -> None:
    """The offer must be one the component's trigger makes, in its window (R-2)."""
    if not isinstance(off, T.Offer):
        raise _mismatch("an alert is rendered from the trigger's offer, before execution")
    if off.source != trig.source:
        raise _mismatch("the offer's source is not its component's trigger")
    if isinstance(trig, T.P14Breakout):
        lat = int(trig.latency)
        ok = (int(off.decision) == int(off.alert) and int(off.sub) == 0 and off.entry == trig.entry
              and int(trig.first) <= int(off.alert) <= int(trig.last) and int(off.live) == int(off.alert) + lat
              and off.group == "" and not off.rewrite and int(off.role) == 0
              and off.expires == (int(off.live) + T.LIMIT_WINDOW - 1 if trig.entry == T.LIMIT else None))
        if not ok:
            raise _mismatch("the offer is not one its breakout trigger makes (decision, alert, live = alert + L, "
                            "entry, expiry)")
        if int(off.live) - int(off.alert) < int(c["latency"]):
            raise _mismatch("the alert reaches the user less than L minutes before the order goes live")
    elif isinstance(trig, T.RL3Tickets):
        kind, _, name = off.tag.partition("_")
        ok = (off.entry == T.TICKET and int(off.decision) == int(off.alert) == T.RTH_OPEN
              and int(off.live) == T.LIVE_0900 and kind == trig.kind and name in TS.rl3_names(trig)
              and int(off.sub) == T.RL3_SUBS.get((kind, name), -1) and off.expires == int(trig.cutoff) - 1
              and off.group == trig.source + ":" + trig.kind and off.rewrite)
        if not ok:
            raise _mismatch("the offer is not one its ticket trigger makes (its kind's ticket, alert, live, cutoff)")
        try:
            T.check_latency(off, None)
        except T.TriggerRefused as e:
            raise _mismatch(str(e)) from e
    else:
        raise _mismatch("the component's trigger offers no playbook side")
    if not int(c["first"]) <= int(off.live) <= int(c["last"]):
        raise _mismatch("the order would go live outside its component's window")
    if int(off.live) > int(decl["execution"]["last_entry"]):
        raise _mismatch("the order would go live after the firm's last new entry")


def _day_windows(decl: Mapping[str, Any], day: str) -> tuple[T.Window, ...]:
    """The declaration's news windows on `day`, from its dated record (R-4), never the caller's."""
    return tuple(T.release_window(int(w["release"]), int(w["before"]), int(w["after"]), w["source"])
                 for w in decl["news_windows"] if day in w["dates"])


def _context(trig: Any, decl: Mapping[str, Any], day: str, session: int, sources: Any) -> T.DayContext:
    if not isinstance(sources, DC.Sources):
        raise _mismatch("the day's flags come from the void calendar's sources (day_calendar.Sources), never the "
                        "caller's word")
    try:
        d = date.fromisoformat(day)
        return T.context_for(trig, sources, d, int(session), _day_windows(decl, day),
                             market=UNDERLYING_OF[decl["instrument"]])
    except (DC.HeldOutDay, KeyError, ValueError) as e:
        raise _mismatch(f"the void calendar gives no context for {day}: {e}") from e


def _alert(carried: Carried, offer: Any, component: Any, account: Any, day: Any, sources: Any) -> Rendered:
    decl = _carried(carried)
    ci, c = _comp(decl, component)
    trig = carried.design.components[ci].trigger
    _check_offer(decl, c, trig, offer)
    ai = _account(decl, account)
    if account not in _routes(decl, c["name"]):
        raise _mismatch(f"account {account} is not in component {c['name']}'s pool")
    cap = size_cap(decl["firm"], decl["accounts"][ai]["role"], decl["instrument"])
    if int(c["contracts"]) > cap:
        raise _mismatch("the size exceeds the firm's verified limit for this account")
    if not isinstance(day, str):
        raise _mismatch("the day is an ISO date")
    if any(v["date"] == day for v in decl["void_dates"]):
        raise AlertRefused("declared_void", f"{day} is on the declaration's void list: no alert is sent")
    ctx = _context(trig, decl, day, offer.session, sources)
    kept, refused = T.admit([offer], ctx)
    if refused:
        why = refused[0][1]
        raise AlertRefused(why if why in REASON_WORDS else "calendar", f"the library refuses the offer: {why}")
    if isinstance(trig, T.RL3Tickets) and trig.kind in ("pd", "pdc") and ctx.prior_void:
        raise AlertRefused("prior_void", "the previous day's levels are void today")
    try:
        side = TS.trigger_side(trig, c["side_rule"], offer)
    except TS.SideRefused as e:
        raise _mismatch(str(e)) from e
    if not TS.is_trigger_side(side):
        raise _mismatch("the side was not computed from the trigger")
    kind, price = T.order_for(offer, side.side)
    segs = T.segments(offer, ctx)
    windows = ctx.all_windows()
    stretches = []
    for lv, last in segs:
        rules = T.rules_for(lv, ctx, T.JOURNEY)
        nxt = next((w for w in windows if w.first > int(lv)), None)
        flat_window = int(rules.walk_end) < int(T.JOURNEY.walk_end) and nxt is not None
        stretches.append({"live": int(lv), "last": None if last is None else int(last),
                          "flatten": int(rules.walk_end), "window": flat_window,
                          "window_kind": nxt.kind if flat_window else "", "window_source": nxt.source if flat_window
                          else ""})
    offer_fields = {f.name: getattr(offer, f.name) for f in fields(offer) if f.name != "level"}   # R-5: never a price
    calc = {"side": side.side, "kind": kind, "stretches": stretches, "cap": cap,
            "windows": [{"first": w.first, "last": w.last, "kind": w.kind, "source": w.source} for w in windows]}
    if kind == W.STOP_ENTRY:
        calc["beyond"] = int(round(side.side * (float(price) - float(offer.level)) / W.TICK))
    src = {"design": decl, "offer": offer_fields, "account": account, "day": day, "calc": calc,
           "library": _library(decl)}
    d = _Doc(src)
    D, Cp, K = "design", ("design", "components", ci), "calc"
    d.line("TRADE ALERT -- enter by hand. This message is not an order and nothing sends it anywhere.")
    d.line("Design ", _v(D, "design_id"), " (carried under ", _v(D, "row"), "). Date ", _v("day"), ". Alert ",
           _ct("offer", "alert"), " CT; the order goes live at ", _ct("offer", "live"), " CT.")
    d.line("Firm ", _v(D, "firm"), " (", _v("library", "plan"), "), account ", _v(D, "accounts", ai, "id"), ": ",
           ROLES[decl["firm"]][decl["accounts"][ai]["role"]][1], ".")
    d.line("Instrument ", _v(D, "instrument"), ", ", _v(*Cp, "contracts"), " contracts (the firm's verified limit for "
           "this account: ", _v(K, "cap"), ").")
    if isinstance(trig, T.P14Breakout):
        d.line("Side ", ("side", (K, "side")), ": the breakout was ", SIGN_WORDS[offer.tag[-1]], "; the rule is ",
               SIDE_RULE_WORDS[c["side_rule"]], ".")
    else:
        kind_name = tuple(offer.tag.split("_", maxsplit=1))
        d.line("Side ", ("side", (K, "side")), ": the level is ", LEVEL_WORDS[kind_name], ", ",
               ROLE_WORDS[int(offer.role)], "; the rule at this level is ", SIDE_RULE_WORDS[side.ticket_rule], ".")
    d.line("  The trigger's own side, cleared by the no-harm floor under ", _v(D, "side", "no_harm_row"), ".")
    if kind == W.MARKET:
        d.line("Order ", ("order", (K, "kind")), " at ", _ct("offer", "live"), " CT, when the order goes live.")
    elif isinstance(trig, T.P14Breakout):
        d.line("Order ", ("order", (K, "kind")), " at the price at the alert: the close of the one-minute bar ending ",
               _ct("offer", "alert"), " CT, as your platform shows it when this alert reaches you.")
    elif kind == W.LIMIT_ENTRY:
        d.line("Order ", ("order", (K, "kind")), " at the level itself, read on your chart.")
    else:
        d.line("Order ", ("order", (K, "kind")), " ", _v(K, "beyond"), " tick ", BEYOND_WORDS[side.side],
               " the level, read on your chart.")
    for j, s in enumerate(stretches):
        S = (K, "stretches", j)
        if kind == W.MARKET:
            parts: list[Any] = ["  It fills at the open of the bar at ", _ct(*S, "live"), " CT"]
        elif s["last"] is None:
            parts = ["  Working from ", _ct(*S, "live"), " CT"]
        else:
            parts = ["  Working from ", _ct(*S, "live"), " CT through the bar stamped ", _ct(*S, "last"),
                     " CT, then cancelled if unfilled"]
        if s["window"]:
            parts += ["; a position from it is closed at ", _ct(*S, "flatten"), " CT, when ",
                      WINDOW_WORDS[s["window_kind"]], " starts (", _v(*S, "window_source"), ")."]
        else:
            parts += ["; a position from it is flattened by the bar ending ", _ct(*S, "flatten"), " CT at the latest."]
        d.line(*parts)
    d.line("Stop ", _v(*Cp, "stop_ticks"), " ticks from your fill; target ", ("target", Cp + ("stop_ticks",),
           Cp + ("rr",)), " ticks (reward to risk ", _v(*Cp, "rr"), "); entered with the order as a bracket.")
    d.line("Today's windows (no entry and no fill inside them):")
    for j, _ in enumerate(windows):
        Wp = (K, "windows", j)
        d.line("  - ", WINDOW_WORDS[windows[j].kind], " (", _v(*Wp, "source"), "): the bars from ", _ct(*Wp, "first"),
               " CT through ", _ct(*Wp, "last"), " CT")
    d.line("Why it is offered today: component ", _v(*Cp, "name"), " (", _v(*Cp, "session"), ") fired at ",
           _ct("offer", "decision"), " CT; the void calendar does not void the day for it; no window covers ",
           _ct("offer", "live"), " CT.")
    d.line("Before you enter: enter only if, at this firm, no position is open, no entry order is working, and the last "
           "position closed at least ", _v(D, "execution", "gap_minutes"), " minutes ago -- the firm's state is yours "
           "to check.")
    d.line(OPPOSITE)
    d.line(NO_COPY)
    return d.done()


def render_alert(carried: Carried, offer: T.Offer, component: str, account: str, day: str,
                 sources: DC.Sources) -> Rendered:
    """One offer's alert for a human (the module docstring); `AlertRefused` otherwise (its `reason` says whether a
    not-offered notice is due)."""
    return _alert(carried, offer, component, account, day, sources)


def render_offer(carried: Carried, offer: T.Offer, component: str, account: str, day: str,
                 sources: DC.Sources) -> Rendered:
    """The alert, or the not-offered notice when the day or the trigger voids the offer; a mismatch still refuses."""
    try:
        return _alert(carried, offer, component, account, day, sources)
    except AlertRefused as e:
        if e.reason == "mismatch":
            raise
        return render_not_offered(carried, offer, component, e.reason)


def render_not_offered(carried: Carried, offer: Any, component: str, reason: str) -> Rendered:
    """A skipped or refused offer's notice for a human: what is not to be taken today, and why (`REASON_WORDS`)."""
    decl = _carried(carried)
    ci, c = _comp(decl, component)
    if reason not in REASON_WORDS:
        raise _mismatch(f"reason {reason!r} is not one of the notice's reasons")
    if getattr(offer, "source", None) != c["trigger"]["source"]:
        raise _mismatch("the offer's source is not its component's trigger")
    src = {"design": decl, "offer": {"live": int(offer.live)}}
    d = _Doc(src)
    d.line("NOT OFFERED today: component ", _v("design", "components", ci, "name"), "'s order at ",
           _ct("offer", "live"), " CT -- do not enter it.")
    d.line("Why: ", REASON_WORDS[reason], ".")
    return d.done()


def render_trade(carried: Carried, trade: Any) -> Rendered:
    """A scheduled trade (`components.ScheduledTrade`, or routed): its side is the evaluation's coin whatever its label
    says (`components._trade_row`), so it gets the not-offered notice, never an alert (R-1)."""
    tr = trade.trade if isinstance(trade, R.RoutedTrade) else trade
    if not isinstance(tr, C.ScheduledTrade):
        raise _mismatch("not a scheduled trade")
    return render_not_offered(carried, tr, tr.component, "coin_side")


__all__ = ["REQUIRED", "TRANSFORMS", "FIRMS", "PLANS", "ROLES", "VOID_WORDS", "REASON_WORDS", "CONVENTIONS",
           "PlaybookRefused", "AlertRefused", "Piece", "Rendered", "ResultFile", "Carried", "resolve", "plan_name",
           "micros_per_mini", "size_cap", "decision_log", "check_declaration", "row_key", "accept_result",
           "load_carried", "render_playbook", "render_alert", "render_offer", "render_not_offered", "render_trade"]
