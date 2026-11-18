"""RD-05's terms (`prereg/RD-05_firm_modes.md` 2.1-2.2, 4.1-4.5, 5, 15, 17.2; Appendices M and R): every configuration's
evaluation and funded rules read from the record by key, the U-rules' figures parsed from their entries' quotes (A-19),
the mode-corners of Appendix M, the keys of Appendix R, and the declared constants of the reading in one table.

**The loaders (17.2).** `extended.firm_terms.record_value` (this repository's record, refusing every entry that is not
`verified`) and `stage2_value` (Stage 2's vendored ledger, the same); the vendored Lucid ledger only through Stage 2's
adapter (`propedge.contract.lucid.lucid_terms`, imported in the process that runs it). A value stated in text is parsed
fail-loud (`TermParseError`). **No rule value is typed here**: the numbers come from the record; the U-rules' ends from
`U_RULES` (5.1), their figures from A-19's parser on the named quote (`quote_figure`), never from a non-verified entry's
`value` (which is `None` for every such entry at 1c9f34f).

**A-19 (`quote_figure`, `A19`).** A U-rule end's figure that the record holds only in an unverified entry's `quote` is
parsed from that quote by a pattern declared beside the rule, fail-loud; the entry must be non-verified (a verified
entry is read by its value). Each named figure has a test (T-5).

**The declared constants (`DECLARED`, 17.2).** The grid of 2.6, the horizons and account counts of 9.1, the oracle level
of 9.6, U-2's price grid, the renewal window of 9.5, the stacking window of 4.7 item 5, the seeds of section 15 -- each
citing its line of the declaration. They are the reading's own constants, not rule values.

Pure Python: the records are read as YAML; Lucid's terms and Stage 2's operating constants (`sizing.MICROS_PER_MINI`,
`DEFAULT_HEADROOM_FRAC`, the registered rule's stand-aside) are read through the vendored modules only inside the
functions that need them (`lucid()`, `registered_sizing()`), each in the calling process.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from extended import firm_terms as FT
from extended.firm_terms import TermParseError, UnverifiedTerm, parse, record_entry, record_value, stage2_value

ROOT = Path(__file__).resolve().parent.parent
DECLARATION = "prereg/RD-05_firm_modes.md"
#: the pin of the declaration (E-200): the sha256 of its LF text
DECLARATION_SHA256 = "be7f90fb56af6e09c92c0277ce83c228f2e2fbeca8fc26b87d90ccf50239659c"
PINNING_ROW = "E-200"
PREREG_ID = "RD-05"
STRICT, LENIENT, SINGLE = "strict", "lenient", "single"
EVAL, FUNDED = "evaluation", "funded"


# ------------------------------------------------------------------------------------------------ the declared table


@dataclass(frozen=True)
class Declared:
    value: Any
    cite: str


#: the reading's own constants, each citing its line of the declaration (17.2): never a rule value
DECLARED: dict[str, Declared] = {
    "grid.w": Declared((1.0, 1.5, 2.0, 3.0), "2.6: w, reward-to-risk, 1.0 1.5 2.0 3.0"),
    "grid.r": Declared((250.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0), "2.6: r, dollar risk, $250 to $2,000"),
    "grid.s_part_b": Declared((10, 400, 10), "2.6: s for part B, every multiple of 10 from 10 to 400 ticks"),
    "grid.s_costed": Declared((50, 100, 150), "2.6 / 9.1: the costed coin's stops, 50, 100 and 150 ticks"),
    "accounts": Declared(50_000, "9.1: accounts per run, 50,000"),
    "horizon.eval": Declared(504, "9.1: the evaluation runs to its resolution or 504 sessions"),
    "horizon.funded": Declared(504, "9.1: the funded account to its ending or 504 sessions from activation"),
    "oracle.level": Declared(0.01, "9.6: the family-wise level 0.01, Bonferroni over N"),
    "oracle.n_max": Declared(7489, "9.6 / 16: N is at most 7,489"),
    "price.grid": Declared((25.0, 500.0, 25.0), "5.1 U-2: an unverified price on $25 to $500 in steps of $25"),
    "renewal.window": Declared(2520, "9.5: the renewal's law on sessions 0 to 2,520"),
    "stacking.window": Declared(21, "4.7 item 5: two floor breaches in the 21 trading sessions ending on the request day"),
    "stacking.breaches": Declared(2, "4.7 item 5: at least two floor breaches"),
    "month": Declared(21, "6 item 3: a month is 21 sessions"),
    "first_payout.within": Declared((21, 63), "9.3: a first payout within 21 and 63 sessions of activation"),
    "large_days.bins": Declared((1, 2, 3, 4, 5), "10.1: k* at 1, 2, 3, 4, 5 and more"),
    "sessions.percentiles": Declared((10, 50, 90), "9.3: sessions to a pass, p10, p50, p90"),
    "part_a.first_day": Declared(("c", 0.75, 1.0, 1.5), "7 item 2: X at c T, 0.75 T, T and 1.5 T"),
    "ladder.denial": Declared((0.10, 0.25, 0.50), "4.7 item 4 / 12.3: the denial ladder 10, 25, 50 %"),
    "shift.se": Declared(8.0, "9.6: a check shifted by eight of its standard errors"),
    "workers.max": Declared(2, "18: step 2 at most 2 workers"),
    "exact.tol": Declared(1e-9, "9.6's exact checks, to 1e-9: the relative tolerance on a balance change, a payout "
                          "or a forfeiture (V-6, W-1)"),
    "memory.bound_gb": Declared({0: 0.5, 1: 2.5, 2: 2.5, 3: 2.5, 4: 2.5, 5: 2.5}, "18: the steps' summed memory bounds"),
    "time.bound_h": Declared({0: 1, 1: 8, 2: 12, 3: 48, 4: 24, 5: 24}, "18: the steps' time bounds"),
}


#: structure and units, never a rule value (17.2's literal check skips this table by name)
NOT_RULE_VALUES: dict[str, float] = {"half": 0.5, "percent": 100.0, "pair": 2, "never": 10 ** 9, "uniform_var": 12.0}


def declared(name: str) -> Any:
    return DECLARED[name].value


def grid_w() -> tuple[float, ...]:
    return tuple(float(x) for x in declared("grid.w"))


def grid_r() -> tuple[float, ...]:
    return tuple(float(x) for x in declared("grid.r"))


def grid_s_part_b() -> tuple[int, ...]:
    lo, hi, step = declared("grid.s_part_b")
    return tuple(range(int(lo), int(hi) + 1, int(step)))


def price_grid() -> tuple[float, ...]:
    lo, hi, step = declared("price.grid")
    n = int(round((hi - lo) / step))
    return tuple(float(lo + i * step) for i in range(n + 1))


# ------------------------------------------------------------------------------------------------ section 15's seeds

#: section 15's block: role -> seed. The one place in the build that holds them (T-0's DECLARED_USES, T-13)
SEEDS: dict[str, int] = {
    "coin_eval": 20262380,
    "coin_funded": 20262381,
    "coin_peak": 20262382,
    "build_toys": 20262383,
    "coin_identity": 20262384,
    "honesty": 20262385,
}
#: the four reserved, unused (section 15)
RESERVED_SEEDS: tuple[int, ...] = (20262386, 20262387, 20262388, 20262389)
#: the timing measurement's seed, outside the block, no meaning (section 15, S7)
TIMING_SEED = 0


def seed(role: str) -> int:
    if role not in SEEDS:
        raise KeyError(f"{role!r} is no seed role of section 15 ({', '.join(SEEDS)})")
    return SEEDS[role]


# ------------------------------------------------------------------------------------------------ A-19: the quote parser


@dataclass(frozen=True)
class QuoteFigure:
    """One figure a U-rule end needs, held only in a non-verified entry's quote (A-19): the entry, the pattern, the
    group, and the rule it serves."""

    key: str
    pattern: str
    group: int
    rule: str
    what: str


#: A-19's declared parses (4.3 A-19; 5.1): each is tested on its entry's quote (T-5)
A19: dict[str, QuoteFigure] = {
    "U-16.lock": QuoteFigure("mffu.pro50k.funded_drawdown_lock", r"starting balance plus \$(\d+)", 1, "U-16",
                             "Pro's funded lock level above the start"),
    "U-29.lock": QuoteFigure("mffu.rapid50k.funded_drawdown_lock", r"Once your trailing Max Loss reaches \$(\d+), it locks",
                             1, "U-29", "Rapid's funded lock level above the start"),
    "U-17.buffer": QuoteFigure("mffu.pro50k.payout_buffer", r'"Payout Buffer Requirement" \| "\$([\d,]+)"', 1, "U-17",
                               "Pro's buffer"),
    "U-17.share": QuoteFigure("mffu.pro50k.payout_buffer", r"withdraw up to (\d+)% of your profits before fully clearing "
                              r"the buffer", 1, "U-17", "Pro's within-buffer share (lenient)"),
    "U-22.min_high": QuoteFigure("labs.010_011_50k_dpp.daily_path_min", r'"\$(\d+) minimum, \$[\d,]+ maximum"', 1,
                                 "U-22", "the Daily path's higher minimum (strict)"),
    "U-22.min_low": QuoteFigure("labs.010_011_50k_dpp.daily_path_min", r'"A \$(\d+) minimum\."', 1, "U-22",
                                "the Daily path's lower minimum (lenient)"),
    "U-24.limit_006": QuoteFigure("labs.006_50k_static.purchase_limit", r'"Purchase Limit" \| "(\d+) per Trader"', 1,
                                  "U-24", "Labs #006's purchase limit"),
    "U-24.limit_dpp": QuoteFigure("labs.010_011_50k_dpp.purchase_limit", r'"Purchase Limit" \| "(\d+) total per Trader',
                                  1, "U-24", "Labs Daily Payouts+'s purchase limit"),
    "U-28.dll": QuoteFigure("mffu.builder50k.daily_loss_limit", r'"Daily Loss Limit" \| "\$([\d,]+) - soft pause"', 1,
                            "U-28", "Builder's daily loss limit (strict)"),
    "U-30.minis": QuoteFigure("mffu.rapid50k.funded_position_limit", r"\((\d+) minis OR \d+ micros\) due to the scaling "
                              r"plan", 1, "U-30", "Rapid's funded starting allowance, minis (strict)"),
    "U-30.micros": QuoteFigure("mffu.rapid50k.funded_position_limit", r"\(\d+ minis OR (\d+) micros\) due to the scaling "
                               r"plan", 1, "U-30", "Rapid's funded starting allowance, micros (strict)"),
}


def quote_figure(name: str) -> float:
    """A-19: the named figure parsed from its entry's recorded quote, fail-loud. Refused for a verified entry (whose
    value is read by the loader) and for a figure no pattern finds."""
    q = A19[name]
    e = record_entry(q.key)
    if e.get("status") == "verified":
        raise TermParseError(f"{q.key} is verified now: {q.rule}'s figure is read from its value, not its quote "
                             "(a change after the pin is a new declaration, 4.1)")
    m = parse(q.pattern, e.get("quote"), f"{q.key} quote ({q.rule}, A-19)")
    return float(m.group(q.group).replace(",", ""))


# ------------------------------------------------------------------------------------------------ small parsers


def _num(s: str) -> float:
    return float(str(s).replace(",", ""))


def rv(key: str) -> Any:
    return record_value(key)


def rv_num(key: str, pattern: str | None = None, group: int = 1) -> float:
    v = rv(key)
    if pattern is None:
        return float(v)
    return _num(parse(pattern, v, key).group(group))


def rv_has(key: str, pattern: str) -> bool:
    try:
        parse(pattern, rv(key), key)
        return True
    except TermParseError:
        return False


def status(key: str) -> str:
    return str(record_entry(key).get("status"))


def s2(key: str) -> Any:
    return stage2_value(key)


def s2_note(key: str) -> str:
    e = FT._stage2().get(key)
    if e is None or e.get("status") != "verified":
        raise UnverifiedTerm(f"Stage 2's {key} is not verified")
    return " ".join(str(e.get("note", "")).split())


def micros_per_mini() -> int:
    """Stage 2's 10:1 counting (`propedge.campaign.sizing.MICROS_PER_MINI`, D-52), read from the module."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.sizing import MICROS_PER_MINI

    return int(MICROS_PER_MINI)


def calendar_to_sessions(days: float, *, wait: bool) -> int:
    """2.6's rounding (the red team's N-1): `days x billing_days / billing_period_calendar_days` (Stage 2's keys),
    up for a wait that must pass before something the user wants, down for a window whose end harms the user."""
    x = float(days) * float(s2("billing_days")) / float(s2("billing_period_calendar_days"))
    return int(math.ceil(x - 1e-12)) if wait else int(math.floor(x + 1e-12))


def soft_dll_general_article() -> bool:
    """U-13: the daily limit's softness from Topstep's general article (10490293, in Stage 2's verified
    `dll_offer_status` note): "Triggering it is not a rule violation"; "No new trades until 5 PM CT next session"."""
    note = s2_note("dll_offer_status")
    parse(r"Triggering it is not a rule violation", note, "dll_offer_status note (10490293)")
    parse(r"No new trades until 5 PM CT next session", note, "dll_offer_status note (10490293)")
    return True


# ------------------------------------------------------------------------------------------------ the terms


@dataclass(frozen=True)
class Allowance:
    """A position limit in contracts: `minis` and `micros` at most; `counting` "ratio" (micros at Stage 2's 10:1
    against the minis, D-52) or "each" (U-26's strict end: a micro counts as a mini). `ladder` (balance above start,
    minis) for a funded mode with a scaling plan; None: flat."""

    minis: int
    micros: int
    counting: str = "ratio"
    ladder: tuple[tuple[float, int], ...] | None = None


@dataclass(frozen=True)
class EvalTerms:
    """One evaluation mode-corner, money relative to the start (the engine's convention)."""

    config: str
    corner: str
    target: float
    mll: float
    floor: str                     # "trail" (end-of-day trailing to its lock) or "static"
    lock: float | None             # the trailing floor's lock above the start (None: no lock)
    consistency: float | None
    consistency_semantics: str     # "extends" (the recorded one at every plan here) or "fails"
    consistency_base: str          # "net" (the engine's) or "wins" (U-15's lenient end)
    min_days: int | None
    dll: float | None              # a soft daily loss limit (A-1)
    lifespan: int | None           # sessions (A-3, rounded down)
    inactivity: int | None         # sessions of no trade that end the account (A-3, rounded down)
    close_only: bool               # U-27's lenient end: the floor checked only at the close
    subscription: float | None     # a recurring price per `billing` sessions (Topstep)
    one_time: float | None         # a one-time price; None with `subscription` None: unverified (U-2's grid)
    billing: int | None
    allowance: Allowance
    commission: str                # "topstep" or "mffu" (U-32's strict end)
    stated_fewest: int | None      # the firm's own statement of the fewest days (7, the stated-fewest check)
    labels: tuple[str, ...] = ()
    keys: tuple[str, ...] = ()


@dataclass(frozen=True)
class FundedTerms:
    """One funded mode-corner, money relative to the start."""

    config: str
    mode: str                      # the funded mode's label (2.2)
    corner: str
    floor_start: float             # the floor at activation (negative)
    mll: float                     # the trailing distance
    floor: str                     # "trail" (EOD), "static" (A-5), "intraday" (A-6)
    lock: float | None             # the lock level above start (None: none)
    lock_timing: str               # "reach" (the engine's), "first_payout" (U-29 strict), "pro_strict" (U-16 strict)
    floor_at_payout: float | None  # where a payout sets the floor (the engine sets `xfa_lock_at`); None: unchanged
    dll: float | None
    gate: str                      # "ts_std", "ts_con", "labs_daily", "labs_5wd", "mffu_buffer", "pro_clock",
                                   # "builder", "lucid"
    winning_days: int | None
    winning_day_min: float | None
    cons_min_days: int | None
    cons_share: float | None
    cap: float | None              # the plan's per-request cap (None: none stated)
    frac: float | None             # the share of the balance a request may take (Topstep's, Lucid's)
    payout_min: float
    split: float
    buffer: float | None           # the balance that must remain after a request (A-8, A-9, A-10)
    first_profit_above_buffer: float | None   # Builder's first-payout profit above the buffer
    wait_first: int | None         # sessions after the first trade before a request (A-8, A-9, A-10)
    wait_between: int | None       # sessions between requests (A-9's clock)
    since_min: float | None        # profit since the last request (A-8, A-10, Lucid)
    profit_since_required: bool    # Topstep's `require_profit_since_payout`
    cycle_days: int | None         # Builder's trading days in the cycle
    cycle_share: float | None      # Builder's cycle consistency share
    first_cycle_base: str | None   # U-18: "above_buffer" (strict) or "all" (lenient)
    max_payouts: int | None        # an end by count (A-11 Builder; A-17 Lucid)
    ceiling: float | None          # the verified single-day ceiling (A-11)
    request: str                   # the coin's request rule: "engine", "u25_strict", "u25_lenient", "labs_daily_strict",
                                   # "labs_daily_lenient", "builder", "lucid"
    within_buffer_share: float | None   # U-17's lenient end
    request_day_excluded: bool     # A-16
    activation: float
    inactivity: int | None
    allowance: Allowance
    commission: str
    labels: tuple[str, ...] = ()
    keys: tuple[str, ...] = ()


# ------------------------------------------------------------------------------------------------ the configurations

#: 2.1's fourteen configurations, in its order
CONFIGS = ("TS-S", "TS-N", "L6", "L10", "L11", "RE", "RED", "RI", "PRO", "PRO1", "B20", "B15", "LU40", "LU50")
#: each evaluation mode's configuration (2.2): TS-S and TS-N share one evaluation mode
EVAL_MODES = ("TS", "L6", "L10", "L11", "RE", "RED", "RI", "PRO", "PRO1", "B20", "B15", "LU40", "LU50")
FUNDED_MODES = ("TS/std", "TS/con", "L6/std", "L6/con", "L10/day", "L10/5wd", "L11/day", "L11/5wd", "RE", "RED", "RI",
                "PRO", "B20", "B15", "LU")
#: which funded modes follow each configuration's pass (2.2)
FUNDED_OF = {"TS-S": ("TS/std", "TS/con"), "TS-N": ("TS/std", "TS/con"), "L6": ("L6/std", "L6/con"),
             "L10": ("L10/day", "L10/5wd"), "L11": ("L11/day", "L11/5wd"), "RE": ("RE",), "RED": ("RED",),
             "RI": ("RI",), "PRO": ("PRO",), "PRO1": ("PRO",), "B20": ("B20",), "B15": ("B15",), "LU40": ("LU",),
             "LU50": ("LU",)}
EVAL_OF = {"TS-S": "TS", "TS-N": "TS", **{c: c for c in CONFIGS if not c.startswith("TS")}}


@dataclass(frozen=True)
class ModeCorner:
    """One row of Appendix M."""

    index: int
    kind: str                      # EVAL or FUNDED
    mode: str
    corner: str
    terms: tuple[str, ...]         # the two-ended terms at it
    shares_gross: bool             # its gross cells are its strict corner's (N-4)
    close_only: bool


def _mc(i: int, kind: str, mode: str, corner: str, terms: str = "", shares: bool = False, close: bool = False):
    return ModeCorner(i, kind, mode, corner, tuple(t for t in terms.split() if t), shares, close)


#: Appendix M, in run order
MODE_CORNERS: tuple[ModeCorner, ...] = (
    _mc(0, EVAL, "TS", SINGLE), _mc(1, EVAL, "L6", SINGLE), _mc(2, EVAL, "L10", SINGLE), _mc(3, EVAL, "L11", SINGLE),
    _mc(4, EVAL, "RE", STRICT, "U-15 U-32"), _mc(5, EVAL, "RE", LENIENT, "U-15 U-32"),
    _mc(6, EVAL, "RED", STRICT, "U-15 U-32"), _mc(7, EVAL, "RED", LENIENT, "U-15 U-32"),
    _mc(8, EVAL, "RI", STRICT, "U-15 U-32"), _mc(9, EVAL, "RI", LENIENT, "U-15 U-32"),
    _mc(10, EVAL, "PRO", STRICT, "U-15 U-32"), _mc(11, EVAL, "PRO", LENIENT, "U-15 U-32"),
    _mc(12, EVAL, "PRO1", STRICT, "U-32"), _mc(13, EVAL, "PRO1", LENIENT, "U-32", shares=True),
    _mc(14, EVAL, "B20", STRICT, "U-27 U-28 U-32"), _mc(15, EVAL, "B20", LENIENT, "U-27 U-28 U-32", close=True),
    _mc(16, EVAL, "B15", STRICT, "U-27 U-28 U-32"), _mc(17, EVAL, "B15", LENIENT, "U-27 U-28 U-32", close=True),
    _mc(18, EVAL, "LU40", SINGLE), _mc(19, EVAL, "LU50", SINGLE),
    _mc(20, FUNDED, "TS/std", SINGLE), _mc(21, FUNDED, "TS/con", SINGLE),
    _mc(22, FUNDED, "L6/std", STRICT, "U-20"), _mc(23, FUNDED, "L6/std", LENIENT, "U-20", shares=True),
    _mc(24, FUNDED, "L6/con", STRICT, "U-20"), _mc(25, FUNDED, "L6/con", LENIENT, "U-20", shares=True),
    _mc(26, FUNDED, "L10/day", STRICT, "U-22"), _mc(27, FUNDED, "L10/day", LENIENT, "U-22"),
    _mc(28, FUNDED, "L10/5wd", SINGLE),
    _mc(29, FUNDED, "L11/day", STRICT, "U-22"), _mc(30, FUNDED, "L11/day", LENIENT, "U-22"),
    _mc(31, FUNDED, "L11/5wd", SINGLE),
    _mc(32, FUNDED, "RE", STRICT, "U-25 U-32"), _mc(33, FUNDED, "RE", LENIENT, "U-25 U-32"),
    _mc(34, FUNDED, "RED", STRICT, "U-25 U-32"), _mc(35, FUNDED, "RED", LENIENT, "U-25 U-32"),
    _mc(36, FUNDED, "RI", STRICT, "U-25 U-29 U-30 U-32"), _mc(37, FUNDED, "RI", LENIENT, "U-25 U-29 U-30 U-32"),
    _mc(38, FUNDED, "PRO", STRICT, "U-16 U-17 U-25 U-26 U-32"), _mc(39, FUNDED, "PRO", LENIENT, "U-16 U-17 U-25 U-26 U-32"),
    _mc(40, FUNDED, "B20", STRICT, "U-18 U-28 U-32"), _mc(41, FUNDED, "B20", LENIENT, "U-18 U-28 U-32"),
    _mc(42, FUNDED, "B15", STRICT, "U-18 U-28 U-32"), _mc(43, FUNDED, "B15", LENIENT, "U-18 U-28 U-32"),
    _mc(44, FUNDED, "LU", SINGLE),
)

#: the terms that act on the costed coin alone (5.2's "costed coin only")
COSTED_ONLY = frozenset({"U-20", "U-26", "U-30", "U-32"})


def close_only_corners() -> tuple[int, ...]:
    """7 item 9: the mode-corners at which the floor is checked only at the close (U-27's lenient end)."""
    return tuple(m.index for m in MODE_CORNERS if m.kind == EVAL and "U-27" in m.terms and m.corner == LENIENT)


def shared_gross_corners() -> tuple[int, ...]:
    """5.2 / N-4: the lenient corners whose only two-ended terms act on the costed coin alone."""
    out = []
    for m in MODE_CORNERS:
        if m.corner == LENIENT and m.terms and set(m.terms) <= COSTED_ONLY:
            out.append(m.index)
    return tuple(out)


def strict_twin(m: ModeCorner) -> ModeCorner:
    for x in MODE_CORNERS:
        if x.kind == m.kind and x.mode == m.mode and x.corner == STRICT:
            return x
    raise KeyError(m)


# ------------------------------------------------------------------------------------------------ U-rules (5.1)

#: 5.1's rules new here, each end named (the readings of section 5 in one table, 17.2)
U_RULES: dict[str, Declared] = {
    "U-13": Declared(None, "a Labs term the Labs page leaves unstated: Topstep's general article, labelled"),
    "U-14": Declared((STRICT, LENIENT), "a pass at a funded cap: strict closed by inactivity; lenient waits (part F)"),
    "U-15": Declared(("net", "wins"), "MFFU evaluation consistency base: strict the net profit; lenient winning days"),
    "U-16": Declared(("pro_strict", "reach"), "Pro's funded floor: strict trails uncapped then set at the first payout; "
                     "lenient locks on reaching"),
    "U-17": Declared((False, True), "Pro's buffer: strict no request inside it; lenient at the quoted share while "
                     "the balance is inside the buffer (read literally, R-d)"),
    "U-18": Declared(("above_buffer", "all"), "Builder's first-cycle base: strict profit above the buffer; lenient all"),
    "U-20": Declared(("entry_tier", "ladder"), "Labs #006's funded scaling: strict the entry tier; lenient the ladder "
                     "to the Labs cap"),
    "U-22": Declared((STRICT, LENIENT), "Labs' Daily path: strict the higher minimum, the session's own profit, the next "
                     "close; lenient the lower, any profit, the same close"),
    "U-24": Declared(("total", "monthly"), "a Labs purchase limit: strict in total; lenient each calendar month"),
    "U-25": Declared(("u25_strict", "u25_lenient"), "the request where no cap is stated: strict the reference amount; "
                     "lenient the whole withdrawable balance"),
    "U-26": Declared(("each", "ratio"), "Pro's funded cap counting: strict a micro as a mini; lenient 10:1"),
    "U-27": Declared((False, True), "Builder's evaluation breach basis: strict intraday; lenient the close only"),
    "U-28": Declared((True, False), "Builder's daily loss limit: strict the soft limit; lenient none"),
    "U-29": Declared(("first_payout", "reach"), "Rapid's funded lock: strict at the first payout; lenient on reaching"),
    "U-30": Declared(("start", "eval"), "Rapid's funded allowance: strict the example's start; lenient the evaluation's"),
    "U-31": Declared((True, False), "Rapid EOD's funded news rule: strict reaches; lenient does not (part F)"),
    "U-32": Declared(("mffu", "topstep"), "MFFU per-plan commission: strict the firm-wide figures; lenient the "
                     "engine's own (Topstep's schedule)"),
}


def end(rule: str, corner: str) -> Any:
    """A U-rule's reading at a corner (strict: the first end; lenient: the second)."""
    s, l = U_RULES[rule].value
    if corner in (STRICT, SINGLE):
        return s
    if corner == LENIENT:
        return l
    raise ValueError(f"corner {corner!r}")


# ------------------------------------------------------------------------------------------------ evaluation terms


def _labs_mll(key: str) -> tuple[float, str]:
    v = rv(key)
    amt = _num(parse(r"^(\d+) USD", v, key).group(1))
    kind = "static" if re.search(r"static", str(v)) else "trail"
    if kind == "trail":
        parse(r"trailing the end-of-day balance|end-of-day trailing", v, key)
    return amt, kind


def _contracts(key: str) -> tuple[int, int]:
    m = parse(r"^(\d+) minis? / (\d+) micros?", rv(key), key)
    return int(m.group(1)), int(m.group(2))


def _mffu_eval_lock() -> float:
    return rv_num("mffu.eval_drawdown_lock", r"starting balance plus \$(\d+)")


def _mffu_inactivity_sessions() -> int:
    days = rv_num("mffu.inactivity_rule", r"no trade for (\d+) consecutive calendar days")
    return calendar_to_sessions(days, wait=False)


def _labs_window(key: str) -> int:
    return calendar_to_sessions(float(rv(key)), wait=False)


def _commission_eval(corner: str) -> str:
    return "mffu" if end("U-32", corner) == "mffu" else "topstep"


def eval_terms(config: str, corner: str = SINGLE) -> EvalTerms:
    """The evaluation mode of `config` at `corner` (Appendix M), every value by key."""
    mode = EVAL_OF.get(config, config)
    if mode == "TS":
        return _ts_eval(config)
    if mode in ("L6", "L10", "L11"):
        return _labs_eval(mode)
    if mode in ("RE", "RED", "RI", "PRO", "PRO1"):
        return _mffu_eval(mode, corner)
    if mode in ("B20", "B15"):
        return _builder_eval(mode, corner)
    if mode in ("LU40", "LU50"):
        return _lucid_eval(mode)
    raise ValueError(f"unknown evaluation mode {config!r}")


#: English number words, for a page that states a count in words (language, never a rule value)
NUMBER_WORDS: dict[str, int] = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def _ts_stated_fewest() -> int:
    note = s2_note("combine_min_trading_days")
    words = NUMBER_WORDS
    m = parse(r"You can pass in as few as (\w+) days", note, "combine_min_trading_days note (8284197)")
    g = m.group(1)
    return int(g) if g.isdigit() else words[g]


def _ts_eval(config: str) -> EvalTerms:
    mpm = micros_per_mini()
    minis = int(s2("combine_position_size_limit"))
    if str(s2("combine_min_trading_days")) != "none_stated":
        raise TermParseError("Topstep's combine_min_trading_days is no longer 'none_stated' -- re-derive")
    sub = float(s2("subscription_fee")) if config == "TS-S" else float(rv("subscription_fee_naf_50k"))
    return EvalTerms(
        config=config, corner=SINGLE, target=float(s2("combine_profit_target")), mll=float(s2("combine_mll")),
        floor="trail", lock=float(s2("combine_mll_lock_at")), consistency=float(s2("combine_consistency_max_day_frac")),
        consistency_semantics="extends", consistency_base="net", min_days=None, dll=None, lifespan=None,
        inactivity=None, close_only=False, subscription=sub, one_time=None, billing=int(s2("billing_days")),
        allowance=Allowance(minis, minis * mpm), commission="topstep", stated_fewest=_ts_stated_fewest(),
        keys=("combine_profit_target", "combine_mll", "combine_mll_lock_at", "combine_consistency_max_day_frac",
              "combine_min_trading_days", "combine_position_size_limit", "subscription_fee", "billing_days",
              "subscription_fee_naf_50k"))


def _labs_eval(mode: str) -> EvalTerms:
    p = {"L6": "labs.006_50k_static.", "L10": "labs.010_50k_dpp_eod.", "L11": "labs.011_50k_dpp_static."}[mode]
    common = "labs.006_50k_static." if mode == "L6" else "labs.010_011_50k_dpp."
    soft_dll_general_article()
    dll = rv_num(common + "eval_daily_loss_limit", r"^(\d+) USD, mandatory")
    mll, kind = _labs_mll(p + "eval_mll")
    minis, micros = _contracts(common + "eval_position_limit")
    fee_key = p + "eval_fee"
    one_time = rv_num(fee_key, r"^(\d+) USD, one-time") if status(fee_key) == "verified" else None
    lock = None if kind == "static" else float(s2("combine_mll_lock_at"))       # U-13: Topstep's general lock
    labels = ("from the general article",) + (("price unverified: on the grid",) if one_time is None else ())
    cons_key = common + "eval_consistency"
    return EvalTerms(
        config=mode, corner=SINGLE, target=float(rv(p + "eval_profit_target")), mll=mll, floor=kind, lock=lock,
        consistency=float(rv(cons_key)), consistency_semantics="extends", consistency_base="net", min_days=None,
        dll=dll, lifespan=_labs_window(common + "eval_lifespan_days"),
        inactivity=_labs_window(common + "eval_inactivity_days"), close_only=False, subscription=None,
        one_time=one_time, billing=None, allowance=Allowance(minis, micros), commission="topstep",
        stated_fewest=None, labels=labels,
        keys=(p + "eval_profit_target", p + "eval_mll", common + "eval_daily_loss_limit", cons_key,
              common + "eval_position_limit", common + "eval_lifespan_days", common + "eval_inactivity_days", fee_key))


def _mffu_eval(mode: str, corner: str) -> EvalTerms:
    lock = _mffu_eval_lock()
    rv("mffu.eval_drawdown_open_equity")                                       # verified: an intraday breach
    if mode == "PRO1":
        t = rv("mffu.pro50k_oneday.eval_terms")
        parse(r"no consistency rule", t, "mffu.pro50k_oneday.eval_terms")
        parse(r"no DLL", t, "mffu.pro50k_oneday.eval_terms")
        target = _num(parse(r"profit target (\d+) USD", t, "mffu.pro50k_oneday.eval_terms").group(1))
        min_days = int(_num(parse(r"minimum (\d+) trading day", t, "mffu.pro50k_oneday.eval_terms").group(1)))
        mll = _num(parse(r"drawdown (\d+) EOD", t, "mffu.pro50k_oneday.eval_terms").group(1))
        m = parse(r"(\d+) mini / (\d+) micro", t, "mffu.pro50k_oneday.eval_terms")
        q = " ".join(str(record_entry("mffu.pro50k_oneday.eval_terms").get("quote", "")).split())
        word = parse(r"\(Pro Plan (\w+) day pass has no consistency rule\)", q, "mffu.pro50k_oneday.eval_terms quote")
        stated = NUMBER_WORDS[word.group(1).lower()]                     # N-11: the firm's own sentence, not the field
        return EvalTerms(
            config="PRO1", corner=corner, target=target, mll=mll, floor="trail", lock=lock, consistency=None,
            consistency_semantics="extends", consistency_base="net", min_days=min_days, dll=None, lifespan=None,
            inactivity=_mffu_inactivity_sessions(), close_only=False, subscription=None, one_time=None, billing=None,
            allowance=Allowance(int(m.group(1)), int(m.group(2))), commission=_commission_eval(corner),
            stated_fewest=stated, labels=("price unverified: on the grid",),
            keys=("mffu.pro50k_oneday.eval_terms", "mffu.eval_drawdown_lock", "mffu.inactivity_rule"))
    p = {"RE": "mffu.rapideod50k.", "RED": "mffu.rapideod50k.", "RI": "mffu.rapid50k.", "PRO": "mffu.pro50k."}[mode]
    mll = rv_num(p + "eval_drawdown", r"^(\d+) USD, end-of-day trailing")
    if mode in ("RE", "RED"):
        dkey = p + "eval_daily_loss_limit"
        parse(r"^none on the default version", rv(dkey), dkey)
        dll = rv_num(dkey, r"the DLL version .*? has a (\d+) USD soft pause") if mode == "RED" else None
    elif mode == "RI":
        dkey = "mffu.rapid50k.daily_loss_limit"
        parse(r"^none", rv(dkey), dkey)
        dll = None
    else:
        dkey = p + "eval_daily_loss_limit"
        parse(r"^none", rv(dkey), dkey)
        dll = None
    pos = p + "eval_position_limit"
    m = parse(r"^(\d+) mini / (\d+) micro", rv(pos), pos)
    rv("mffu.eval_consistency_breach")                                         # verified: extends
    parse(r"trades more days until it is met", rv("mffu.eval_consistency_breach"), "mffu.eval_consistency_breach")
    return EvalTerms(
        config=mode, corner=corner, target=float(rv(p + "eval_profit_target")), mll=mll, floor="trail", lock=lock,
        consistency=float(rv(p + "eval_consistency")), consistency_semantics="extends",
        consistency_base=end("U-15", corner), min_days=int(rv(p + "eval_min_days")), dll=dll, lifespan=None,
        inactivity=_mffu_inactivity_sessions(), close_only=False, subscription=None, one_time=None, billing=None,
        allowance=Allowance(int(m.group(1)), int(m.group(2))), commission=_commission_eval(corner),
        stated_fewest=None, labels=("price unverified: on the grid",),
        keys=(p + "eval_profit_target", p + "eval_drawdown", p + "eval_consistency", p + "eval_min_days", pos, dkey,
              "mffu.eval_drawdown_lock", "mffu.eval_consistency_base", "mffu.inactivity_rule"))


def _builder_dd(add_on: bool) -> tuple[float, float]:
    v = rv("mffu.builder50k.eval_drawdown")
    m = parse(r"^(\d+) USD end-of-day trailing from a \$[\d,]+ minimum \(Add-On: (\d+), \$[\d,]+\); locks once it "
              r"reaches \$(\d+) above the starting balance", v, "mffu.builder50k.eval_drawdown")
    return (_num(m.group(2)) if add_on else _num(m.group(1))), _num(m.group(3))


def _builder_eval(mode: str, corner: str) -> EvalTerms:
    add_on = mode == "B15"
    mll, lock = _builder_dd(add_on)
    fee = rv("mffu.builder50k.eval_fee")
    m = parse(r"^(\d+) USD one-time \(Default, .*?\); (\d+) USD \(Add-On", fee, "mffu.builder50k.eval_fee")
    if str(rv("mffu.builder50k.eval_consistency")) != "none":
        raise TermParseError("mffu.builder50k.eval_consistency is no longer 'none'")
    minis, micros = _contracts("mffu.builder50k.position_limit")
    dll = quote_figure("U-28.dll") if end("U-28", corner) else None
    return EvalTerms(
        config=mode, corner=corner, target=float(rv("mffu.builder50k.eval_profit_target")), mll=mll, floor="trail",
        lock=lock, consistency=None, consistency_semantics="extends", consistency_base="net",
        min_days=int(rv("mffu.builder50k.eval_min_days")), dll=dll, lifespan=None,
        inactivity=_mffu_inactivity_sessions(), close_only=bool(end("U-27", corner)), subscription=None,
        one_time=_num(m.group(2) if add_on else m.group(1)), billing=None, allowance=Allowance(minis, micros),
        commission=_commission_eval(corner), stated_fewest=int(rv("mffu.builder50k.eval_min_days")),
        keys=("mffu.builder50k.eval_profit_target", "mffu.builder50k.eval_drawdown", "mffu.builder50k.eval_fee",
              "mffu.builder50k.eval_consistency", "mffu.builder50k.position_limit", "mffu.builder50k.eval_min_days",
              "mffu.builder50k.daily_loss_limit", "mffu.builder50k.eval_drawdown_breach_basis", "mffu.inactivity_rule"))


@lru_cache(maxsize=1)
def lucid() -> Any:
    """Stage 2's Lucid adapter's terms (`propedge.contract.lucid.lucid_terms`), imported (A-17)."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.contract.lucid import lucid_terms

    return lucid_terms()


def _lucid_config(mode: str) -> str:
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.contract.lucid import ADDON_50, STANDARD_40

    return STANDARD_40 if mode in ("LU40", "LU") else ADDON_50


def lucid_one_time(cfg: str) -> float | None:
    """Lucid's evaluation price at a configuration, from Stage 2's adapter (`lucid_price`): its verified price rows,
    or None (then U-2's grid) were they open."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.contract.lucid import ENGINE_CHECKS_ONLY, lucid_price

    p = lucid_price(cfg, unpriced=ENGINE_CHECKS_ONLY)
    return float(p.eval_fee) if p.verified else None


def purchase_limit(config: str) -> int | None:
    """U-24's limit (A-19's parse of the unverified entry's quote) for a Labs configuration; None elsewhere."""
    if config == "L6":
        return int(quote_figure("U-24.limit_006"))
    if config in ("L10", "L11"):
        return int(quote_figure("U-24.limit_dpp"))
    return None


def _lucid_eval(mode: str) -> EvalTerms:
    t = lucid()
    cfg = _lucid_config(mode)
    mpm = micros_per_mini()
    price = lucid_one_time(cfg)
    return EvalTerms(
        config=mode, corner=SINGLE, target=float(t.eval_target), mll=float(t.eval_mll), floor="trail",
        lock=float(t.eval_lock), consistency=float(t.consistency(cfg)), consistency_semantics="extends",
        consistency_base="net", min_days=int(t.min_days(cfg)), dll=None, lifespan=None, inactivity=None,
        close_only=False, subscription=None, one_time=price, billing=None,
        allowance=Allowance(int(t.eval_position_micros) // mpm, int(t.eval_position_micros)), commission="topstep",
        stated_fewest=int(t.min_days(cfg)),
        labels=("upper bound in fees",) + (("price unverified: on the grid",) if price is None else ()),
        keys=("lucid:" + cfg,))


# ------------------------------------------------------------------------------------------------ funded terms


def _ladder(spec: str) -> tuple[tuple[float, int], ...]:
    out = []
    for part in str(spec).split(","):
        a, b = part.split(":")
        out.append((float(a), int(b)))
    return tuple(out)


def _ts_ladder() -> tuple[tuple[float, int], ...]:
    return _ladder(s2("funded_scaling_plan"))


def funded_terms(mode: str, corner: str = SINGLE) -> FundedTerms:
    """The funded mode `mode` (2.2's label) at `corner`, every value by key."""
    if mode in ("TS/std", "TS/con"):
        return _ts_funded(mode)
    if mode in ("L6/std", "L6/con"):
        return _l6_funded(mode, corner)
    if mode in ("L10/day", "L10/5wd", "L11/day", "L11/5wd"):
        return _dpp_funded(mode, corner)
    if mode in ("RE", "RED", "RI"):
        return _rapid_funded(mode, corner)
    if mode == "PRO":
        return _pro_funded(corner)
    if mode in ("B20", "B15"):
        return _builder_funded(mode, corner)
    if mode == "LU":
        return _lucid_funded()
    raise ValueError(f"unknown funded mode {mode!r}")


def _ts_common() -> dict[str, Any]:
    mpm = micros_per_mini()
    lad = _ts_ladder()
    return dict(
        floor_start=float(s2("xfa_mll_start")), mll=-float(s2("xfa_mll_start")), floor="trail",
        lock=float(s2("xfa_lock_at")), lock_timing="reach", floor_at_payout=float(s2("xfa_lock_at")), dll=None,
        winning_days=int(s2("xfa_std_winning_days")), winning_day_min=float(s2("xfa_std_winning_day_min")),
        cons_min_days=int(s2("xfa_cons_min_days")), cons_share=float(s2("xfa_cons_max_day_frac")),
        frac=float(s2("payout_max_frac_of_balance")), payout_min=float(s2("payout_min")),
        split=float(s2("profit_split")), buffer=None, first_profit_above_buffer=None, wait_first=None,
        wait_between=None, since_min=None, profit_since_required=bool(s2("require_profit_since_payout")),
        cycle_days=None, cycle_share=None, first_cycle_base=None, max_payouts=None, ceiling=None, request="engine",
        within_buffer_share=None, activation=float(s2("activation_fee")), inactivity=None,
        allowance=Allowance(lad[-1][1], lad[-1][1] * mpm, ladder=lad), commission="topstep")


def _ts_funded(mode: str) -> FundedTerms:
    c = _ts_common()
    std = mode == "TS/std"
    if std:
        parse(r"chosen_at_activation", s2("xfa_payout_path_choice"), "xfa_payout_path_choice")
    return FundedTerms(config="TS", mode=mode, corner=SINGLE, gate="ts_std" if std else "ts_con",
                       cap=float(s2("xfa_std_cap")) if std else float(s2("xfa_cons_cap")), request_day_excluded=std,
                       keys=("xfa_mll_start", "xfa_lock_at", "xfa_std_winning_days", "xfa_std_winning_day_min",
                             "xfa_std_cap", "xfa_cons_min_days", "xfa_cons_max_day_frac", "xfa_cons_cap", "payout_min",
                             "payout_max_frac_of_balance", "profit_split", "require_profit_since_payout",
                             "activation_fee", "funded_scaling_plan"), **c)


def _l6_funded(mode: str, corner: str) -> FundedTerms:
    p = "labs.006_50k_static."
    c = _ts_common()                                                    # U-13: Topstep's general terms
    soft_dll_general_article()
    mll_v = rv(p + "funded_mll")
    amt = _num(parse(r"^(\d+) USD, static \(non-trailing\); after the first payout the MLL is set to \$(\d+)", mll_v,
                     p + "funded_mll").group(1))
    at_pay = _num(parse(r"after the first payout the MLL is set to \$(\d+)", mll_v, p + "funded_mll").group(1))
    dll = rv_num(p + "funded_daily_loss_limit", r"^(\d+) USD, mandatory")
    path = rv(p + "funded_payout_path")
    con_share = _num(parse(r"Consistency \((\d+)%\)", path, p + "funded_payout_path").group(1)) / NOT_RULE_VALUES["percent"]
    parse(r"Standard \(no consistency\)", path, p + "funded_payout_path")
    pos = rv(p + "funded_position_limit")
    m = parse(r"^(\d+) mini / (\d+) micro; scaling plan '(\d+)/(\d+)/(\d+)' \(balance thresholds not stated\)", pos,
              p + "funded_position_limit")
    top, mpm = int(m.group(1)), micros_per_mini()
    ts_lad = _ts_ladder()
    if end("U-20", corner) == "entry_tier":
        lad = ((0.0, int(m.group(3))),)
    else:                                                               # the standard ladder's thresholds, Labs' top
        steps = (int(m.group(3)), int(m.group(4)), int(m.group(5)))
        if len(ts_lad) != len(steps):
            raise TermParseError("the standard ladder and Labs' scaling plan have different numbers of tiers")
        lad = tuple((ts_lad[i][0], min(steps[i], top)) for i in range(len(steps)))
    c.update(floor_start=-amt, mll=amt, floor="static", lock=None, floor_at_payout=at_pay, dll=dll,
             allowance=Allowance(top, int(m.group(2)), ladder=lad), activation=float(rv(p + "activation_fee")))
    std = mode == "L6/std"
    if not std:
        c.update(cons_share=con_share)
    return FundedTerms(config="L6", mode=mode, corner=corner, gate="ts_std" if std else "ts_con",
                       cap=float(rv(p + "funded_payout_cap")), request_day_excluded=std,
                       labels=("from the general article",) + (
                           ("A-16 by U-13: Topstep's Standard path's request-day exclusion",) if std else ()),
                       keys=(p + "funded_mll", p + "funded_daily_loss_limit", p + "funded_payout_path",
                             p + "funded_payout_cap", p + "funded_position_limit", p + "activation_fee",
                             p + "funded_payout_terms_other"), **c)


def _dpp_funded(mode: str, corner: str) -> FundedTerms:
    plan, path = mode.split("/")
    q = "labs.010_011_50k_dpp."
    p = "labs.010_50k_dpp_eod." if plan == "L10" else "labs.011_50k_dpp_static."
    c = _ts_common()
    soft_dll_general_article()
    mv = rv(p + "funded_mll")
    amt = _num(parse(r"^(\d+) USD", mv, p + "funded_mll").group(1))
    kind = "static" if re.search(r"static", str(mv)) else "trail"
    if str(rv(q + "funded_consistency")) != "none":
        raise TermParseError(f"{q}funded_consistency is no longer 'none'")
    pos = rv(q + "funded_position_limit")
    m = parse(r"^(\d+) mini / (\d+) micro, on the standard \$50K XFA scaling plan", pos, q + "funded_position_limit")
    lad = tuple((t, min(n, int(m.group(1)))) for t, n in _ts_ladder())
    parse(r"picked at each payout request", rv(q + "payout_path_choice"), q + "payout_path_choice")
    c.update(floor_start=-amt, mll=amt, floor=kind, lock=None if kind == "static" else c["lock"],
             dll=float(rv(q + "funded_daily_loss_limit")), split=float(rv(q + "payout_split")),
             allowance=Allowance(int(m.group(1)), int(m.group(2)), ladder=lad), activation=float(rv(q + "activation_fee")),
             cons_min_days=None, cons_share=None)
    keys = (p + "funded_mll", q + "funded_daily_loss_limit", q + "funded_consistency", q + "funded_position_limit",
            q + "payout_split", q + "activation_fee", q + "payout_path_choice")
    if path == "day":
        g = rv(q + "daily_path_gate")
        buf = _num(parse(r"after the \$([\d,]+) profit buffer is cleared", g, q + "daily_path_gate").group(1))
        parse(r"after the first payout, net positive since the last payout", g, q + "daily_path_gate")
        parse(r"^1 payout per trading day", rv(q + "daily_path_timing"), q + "daily_path_timing")
        at_pay = _num(parse(r"sets the XFA's Maximum Loss Limit to \$(\d+)", rv(q + "daily_path_mll_effect"),
                            q + "daily_path_mll_effect").group(1))
        strict = corner in (STRICT, SINGLE)
        pmin = quote_figure("U-22.min_high" if strict else "U-22.min_low")
        c.update(buffer=buf, payout_min=pmin, floor_at_payout=at_pay, frac=None, winning_days=None,
                 winning_day_min=None, profit_since_required=True, request="labs_daily_strict" if strict else
                 "labs_daily_lenient")
        return FundedTerms(config=plan, mode=mode, corner=corner, gate="labs_daily",
                           cap=float(rv(q + "daily_path_max")), request_day_excluded=False,
                           keys=keys + (q + "daily_path_gate", q + "daily_path_max", q + "daily_path_timing",
                                        q + "daily_path_mll_effect", q + "daily_path_min"), **c)
    g = rv(q + "wd5_path_gate")
    m = parse(r"^(\d+) winning days of \$(\d+) or more since the last payout; no buffer", g, q + "wd5_path_gate")
    parse(r"any payout \(either path\) resets the 5 Winning Days count", rv(q + "payout_resets_wd5_count"),
          q + "payout_resets_wd5_count")
    c.update(winning_days=int(m.group(1)), winning_day_min=_num(m.group(2)), frac=float(rv(q + "wd5_path_amount")),
             profit_since_required=False, labels=())
    return FundedTerms(config=plan, mode=mode, corner=corner, gate="labs_5wd", cap=float(rv(p + "wd5_path_cap")),
                       request_day_excluded=True,
                       keys=keys + (q + "wd5_path_gate", q + "wd5_path_amount", p + "wd5_path_cap",
                                    q + "payout_resets_wd5_count"), **c)


def _mffu_hours_to_sessions(text: str, key: str) -> int:
    h = _num(parse(r"(\d+) hours after the first trade", text, key).group(1))
    return calendar_to_sessions(h / 24.0, wait=True)


def _rapid_funded(mode: str, corner: str) -> FundedTerms:
    p = "mffu.rapideod50k." if mode in ("RE", "RED") else "mffu.rapid50k."
    gate = rv(p + "payout_gate")
    buf = _num(parse(r"\$([\d,]+) (?:of realised profit \(the buffer\)|buffer of realised profit)", gate,
                     p + "payout_gate").group(1))
    wait = _mffu_hours_to_sessions(gate, p + "payout_gate")
    ceil = rv_num(p + "funded_single_day_profit_ceiling", r"^(\d+) USD net profit in a single trading day")
    parse(r"moves it to Live automatically, and any profit above \d+ USD for that day is forfeited",
          rv(p + "funded_single_day_profit_ceiling"), p + "funded_single_day_profit_ceiling")
    mpm = micros_per_mini()
    if mode in ("RE", "RED"):
        dd = rv(p + "funded_drawdown")
        amt = _num(parse(r"starts at a \$0 balance, (\d+) USD below it; end-of-day trailing", dd, p + "funded_drawdown")
                   .group(1))
        lock = rv_num(p + "funded_drawdown_lock", r"^locks at \$(\d+) \(start \+ \$\d+\)")
        dkey = p + "funded_daily_loss_limit"
        parse(r"^none on the default version", rv(dkey), dkey)
        dll = rv_num(dkey, r"(\d+) USD soft pause on the DLL version") if mode == "RED" else None
        since = rv_num(p + "payout_gate", r"each later payout: net profit since the last payout of at least \$(\d+)")
        if str(rv(p + "funded_consistency")) != "none":
            raise TermParseError(f"{p}funded_consistency is no longer 'none'")
        minis, micros = _contracts(p + "funded_position_limit")
        floor, timing, labels = "trail", "reach", ()
        allowance = Allowance(minis, micros)
        keys = (p + "funded_drawdown", p + "funded_drawdown_lock", dkey, p + "funded_position_limit")
    else:
        dd = rv(p + "funded_drawdown")
        amt = _num(parse(r"starts at a \$0 balance; (\d+) USD below the equity high-water mark, trailing intraday on "
                         r"equity", dd, p + "funded_drawdown").group(1))
        lock = quote_figure("U-29.lock")
        timing = end("U-29", corner)
        dkey = "mffu.rapid50k.daily_loss_limit"
        parse(r"^none, evaluation and sim funded", rv(dkey), dkey)
        dll = None
        parse(r"a profit-since-last-payout requirement is not stated", gate, p + "payout_gate")
        since = None                                                    # U-10: none invented
        if end("U-30", corner) == "start":
            allowance = Allowance(int(quote_figure("U-30.minis")), int(quote_figure("U-30.micros")))
        else:
            minis, micros = _contracts("mffu.rapid50k.eval_position_limit")
            allowance = Allowance(minis, micros)
        floor, labels = "intraday", ()
        keys = (p + "funded_drawdown", p + "funded_drawdown_lock", dkey, p + "funded_position_limit",
                "mffu.rapid50k.eval_position_limit")
    if mode in ("RE", "RED"):
        parse(r"^no cap per payout cycle", rv(p + "payout_cap"), p + "payout_cap")
        cap_keys = (p + "payout_cap", p + "payout_request_amount")
    else:
        cap_keys = (p + "payout_cap",)
    return FundedTerms(
        config=mode, mode=mode, corner=corner, floor_start=-amt, mll=amt, floor=floor, lock=lock, lock_timing=timing,
        floor_at_payout=lock, dll=dll, gate="mffu_buffer", winning_days=None, winning_day_min=None, cons_min_days=None,
        cons_share=None, cap=None, frac=float(s2("payout_max_frac_of_balance")), payout_min=float(rv(p + "payout_min")),
        split=float(rv(p + "payout_split")), buffer=buf, first_profit_above_buffer=None, wait_first=wait,
        wait_between=None, since_min=since, profit_since_required=False, cycle_days=None, cycle_share=None,
        first_cycle_base=None, max_payouts=None, ceiling=ceil, request=end("U-25", corner), within_buffer_share=None,
        request_day_excluded=False, activation=float(rv("mffu.activation_fee")), inactivity=_mffu_inactivity_sessions(),
        allowance=allowance, commission=_commission_eval(corner),
        labels=labels + ("strict: no Live credit", "lenient end at Topstep's schedule; zero-commission reading not run"),
        keys=keys + cap_keys + (p + "payout_gate", p + "payout_min", p + "payout_split",
                                p + "funded_single_day_profit_ceiling", "mffu.activation_fee", "mffu.inactivity_rule"))


def _pro_funded(corner: str) -> FundedTerms:
    p = "mffu.pro50k."
    amt = rv_num(p + "funded_drawdown", r"^(\d+) USD, end-of-day trailing, not intraday")
    lock = quote_figure("U-16.lock")
    parse(r"^none", rv(p + "funded_daily_loss_limit"), p + "funded_daily_loss_limit")
    t = rv(p + "payout_timing")
    first = _num(parse(r"first request (\d+) calendar days from the day of the first trade", t, p + "payout_timing")
                 .group(1))
    between = _num(parse(r"then every (\d+) calendar days", t, p + "payout_timing").group(1))
    pos = rv(p + "funded_position_limit")
    m = parse(r"^(\d+) mini / (\d+) micro \(as printed; how a micro counts against the limit is not stated in words\)",
              pos, p + "funded_position_limit")
    counting = end("U-26", corner)
    if counting == "each":
        allowance = Allowance(int(m.group(1)), int(m.group(2)), counting="each")
    else:
        minis = int(m.group(1))
        allowance = Allowance(minis, minis * micros_per_mini(), counting="ratio")
    lenient17 = bool(end("U-17", corner))
    parse(r"Consistent Trading Policy", rv(p + "funded_conduct_policy"), p + "funded_conduct_policy")
    return FundedTerms(
        config="PRO", mode="PRO", corner=corner, floor_start=-amt, mll=amt, floor="trail", lock=lock,
        lock_timing=end("U-16", corner), floor_at_payout=lock, dll=None, gate="pro_clock", winning_days=None,
        winning_day_min=None, cons_min_days=None, cons_share=None, cap=None,
        frac=float(s2("payout_max_frac_of_balance")), payout_min=float(rv(p + "payout_min")),
        split=float(rv(p + "payout_split")), buffer=quote_figure("U-17.buffer"), first_profit_above_buffer=None,
        wait_first=calendar_to_sessions(first, wait=True), wait_between=calendar_to_sessions(between, wait=True),
        since_min=None, profit_since_required=False, cycle_days=None, cycle_share=None, first_cycle_base=None,
        max_payouts=None, ceiling=None, request=end("U-25", corner),
        within_buffer_share=(quote_figure("U-17.share") / NOT_RULE_VALUES["percent"]) if lenient17 else None, request_day_excluded=False,
        activation=float(rv("mffu.activation_fee")), inactivity=_mffu_inactivity_sessions(), allowance=allowance,
        commission=_commission_eval(corner),
        labels=("lenient end at Topstep's schedule; zero-commission reading not run",)
        + (("U-17 lenient read literally (R-d): the quoted share only while the balance is inside the buffer",)
           if lenient17 else ()),
        keys=(p + "funded_drawdown", p + "funded_drawdown_lock", p + "funded_daily_loss_limit", p + "payout_timing",
              p + "funded_position_limit", p + "payout_buffer", p + "payout_min", p + "payout_split", p + "payout_cap",
              p + "funded_conduct_policy", "mffu.activation_fee", "mffu.inactivity_rule"))


def _builder_funded(mode: str, corner: str) -> FundedTerms:
    p = "mffu.builder50k."
    add_on = mode == "B15"
    dd = rv(p + "funded_drawdown")
    m = parse(r"starts at a \$0 balance with the floor at -\$([\d,]+) \(Add-On -\$([\d,]+)\); end-of-day trailing; "
              r"locks at \$(\d+) above the start; after the first payout the MLL resets to \$(\d+)", dd,
              p + "funded_drawdown")
    amt = _num(m.group(2) if add_on else m.group(1))
    gate = rv(p + "payout_gate")
    g = parse(r"first payout: at least \$(\d+) net profit above the buffer \(\$([\d,]+); Add-On \$([\d,]+)\), so a "
              r"balance of at least \$[\d,]+, and (\d+) hours after the first trade; later payouts: at least \$(\d+) net "
              r"profit since the last approved payout; at least (\d+) trading days in the cycle", gate, p + "payout_gate")
    buf = _num(g.group(3) if add_on else g.group(2))
    minis, micros = _contracts(p + "position_limit")
    dll = quote_figure("U-28.dll") if end("U-28", corner) else None
    return FundedTerms(
        config=mode, mode=mode, corner=corner, floor_start=-amt, mll=amt, floor="trail", lock=_num(m.group(3)),
        lock_timing="reach", floor_at_payout=_num(m.group(4)), dll=dll, gate="builder", winning_days=None,
        winning_day_min=None, cons_min_days=None, cons_share=None, cap=float(rv(p + "payout_cap")), frac=None,
        payout_min=float(rv(p + "payout_min")), split=float(rv(p + "payout_split")), buffer=buf,
        first_profit_above_buffer=_num(g.group(1)), wait_first=calendar_to_sessions(_num(g.group(4)) / 24.0, wait=True),
        wait_between=None, since_min=_num(g.group(5)), profit_since_required=False, cycle_days=int(g.group(6)),
        cycle_share=float(rv(p + "funded_consistency")), first_cycle_base=end("U-18", corner),
        max_payouts=int(rv(p + "max_sim_payouts")), ceiling=None, request="builder", within_buffer_share=None,
        request_day_excluded=False, activation=float(rv("mffu.activation_fee")), inactivity=_mffu_inactivity_sessions(),
        allowance=Allowance(minis, micros), commission=_commission_eval(corner),
        labels=("lenient end at Topstep's schedule; zero-commission reading not run",
                "the buffer left after every request (A-8's My Funded Futures form)"),
        keys=(p + "funded_drawdown", p + "payout_gate", p + "position_limit", p + "daily_loss_limit", p + "payout_cap",
              p + "payout_min", p + "payout_split", p + "funded_consistency", p + "max_sim_payouts",
              "mffu.activation_fee", "mffu.inactivity_rule"))


def _lucid_funded() -> FundedTerms:
    t = lucid()
    mpm = micros_per_mini()
    lad = tuple((float(a), int(b)) for a, b in t.funded_ladder)
    return FundedTerms(
        config="LU", mode="LU", corner=SINGLE, floor_start=-float(t.funded_mll), mll=float(t.funded_mll), floor="trail",
        lock=float(t.funded_lock), lock_timing="reach", floor_at_payout=float(t.funded_lock), dll=None, gate="lucid",
        winning_days=int(t.winning_days), winning_day_min=float(t.winning_day_min), cons_min_days=None,
        cons_share=None, cap=float(t.request_cap), frac=float(t.payout_frac_of_profit), payout_min=float(t.payout_min),
        split=float(t.split), buffer=None, first_profit_above_buffer=None, wait_first=None, wait_between=None,
        since_min=float(t.cycle_net_min), profit_since_required=False, cycle_days=None, cycle_share=None,
        first_cycle_base=None, max_payouts=int(t.max_payouts), ceiling=None, request="lucid", within_buffer_share=None,
        request_day_excluded=False, activation=float(t.activation_fee), inactivity=None,
        allowance=Allowance(lad[-1][1], lad[-1][1] * mpm, ladder=lad), commission="topstep",
        labels=("upper bound in fees",), keys=("lucid:funded",))


def mode_corner_terms(m: ModeCorner) -> EvalTerms | FundedTerms:
    """The terms at one row of Appendix M."""
    if m.kind == EVAL:
        cfg = "TS-S" if m.mode == "TS" else m.mode
        return eval_terms(cfg, m.corner)
    return funded_terms(m.mode, m.corner)


# ------------------------------------------------------------------------------------------------ commissions, costs


@lru_cache(maxsize=1)
def topstep_round_turn() -> tuple[float, float]:
    """4.5: Topstep's all-in round turn (MNQ, NQ), `fills.yaml`'s `round_turn_by_instrument` (8284213)."""
    d = yaml.safe_load(FT.STAGE2_FILLS.read_text(encoding="utf-8"))["round_turn_by_instrument"]["values"]
    return float(d["MNQ"]), float(d["NQ"])


def mffu_round_turn() -> tuple[float, float]:
    """U-32's strict end: the firm-wide `mffu.commissions` figures (MNQ, NQ), per contract, round trip."""
    v = rv("mffu.commissions")
    parse(r"per contract, round trip", v, "mffu.commissions")
    nq = _num(parse(r"NQ ([\d.]+) USD", v, "mffu.commissions").group(1))
    mnq = _num(parse(r"MNQ ([\d.]+) USD", v, "mffu.commissions").group(1))
    return mnq, nq


def round_turn(schedule: str) -> tuple[float, float]:
    if schedule == "topstep":
        return topstep_round_turn()
    if schedule == "mffu":
        return mffu_round_turn()
    raise ValueError(schedule)


@lru_cache(maxsize=1)
def fill_slippage() -> dict[str, float]:
    """4.5: `fills.yaml`'s active profile's entry, stop and flatten slippage in ticks (a target fills at its limit)."""
    d = yaml.safe_load(FT.STAGE2_FILLS.read_text(encoding="utf-8"))
    prof = d["meta"]["active_profile"]
    body = d["profiles"][prof]
    return {"profile": prof, **{k: float(body[k]) for k in ("entry_slippage_ticks", "stop_slippage_ticks",
                                                            "target_slippage_ticks", "flatten_slippage_ticks")}}


@lru_cache(maxsize=1)
def tick_values() -> dict[str, float]:
    """`vendor/stage2/config/instruments.yaml`'s tick values, read (MNQ, NQ)."""
    d = yaml.safe_load((ROOT / "vendor" / "stage2" / "config" / "instruments.yaml").read_text(encoding="utf-8"))
    ins = d["instruments"]
    return {"MNQ": float(ins["MNQ"]["tick_value"]), "NQ": float(ins["NQ"]["tick_value"])}


@lru_cache(maxsize=1)
def registered_stand_aside() -> dict[str, Any]:
    """D-212's and D-272's stand-aside of the registered designs' sizing rule (17.2, N10): the rule
    `score_fv3_grid.sizing_rule` builds from `config/fv3_corrected_portfolio.yaml` (the A3 / RC150 gates' rule,
    `atlas_a3.gate_kwargs`), read from its config: per kind (share, floor ticks), its headroom, and Stage 2's
    `DEFAULT_HEADROOM_FRAC` (D-117) beside."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.sizing import DEFAULT_HEADROOM_FRAC

    cfg = yaml.safe_load((ROOT / "vendor" / "stage2" / "config" / "fv3_corrected_portfolio.yaml").read_text(
        encoding="utf-8"))
    sa = cfg["state_policy"]["stand_aside"]
    return {"combine": (float(sa["combine"]["min_risk_share"]), int(sa["combine"]["floor_ticks"])),
            "funded": (float(sa["funded"]["min_risk_share"]), int(sa["funded"]["floor_ticks"])),
            "headroom": float(cfg["gate"]["campaign"]["headroom"]), "d117_headroom": float(DEFAULT_HEADROOM_FRAC),
            "source": "vendor/stage2/config/fv3_corrected_portfolio.yaml state_policy.stand_aside, gate.campaign"}


# ------------------------------------------------------------------------------------------------ Appendix R's keys

#: Appendix R's record keys (`labs.*`, `mffu.*` and the record's Topstep keys) with the status the text states at
#: 1c9f34f; T-0 maps each against the record (an entry whose status differs is a change after the pin, 4.1)
RECORD_KEYS: dict[str, str] = {}
for _k in ("labs.006_50k_static.eval_profit_target labs.010_50k_dpp_eod.eval_profit_target "
           "labs.011_50k_dpp_static.eval_profit_target labs.006_50k_static.eval_mll labs.010_50k_dpp_eod.eval_mll "
           "labs.011_50k_dpp_static.eval_mll labs.006_50k_static.eval_daily_loss_limit "
           "labs.010_011_50k_dpp.eval_daily_loss_limit labs.006_50k_static.eval_consistency "
           "labs.010_011_50k_dpp.eval_consistency labs.006_50k_static.eval_position_limit "
           "labs.010_011_50k_dpp.eval_position_limit labs.006_50k_static.eval_lifespan_days "
           "labs.006_50k_static.eval_inactivity_days labs.010_011_50k_dpp.eval_lifespan_days "
           "labs.010_011_50k_dpp.eval_inactivity_days labs.006_50k_static.eval_fee labs.011_50k_dpp_static.eval_fee "
           "labs.006_50k_static.eval_reset labs.006_50k_static.activation_fee labs.010_011_50k_dpp.activation_fee "
           "labs.006_50k_static.funded_mll labs.010_50k_dpp_eod.funded_mll labs.011_50k_dpp_static.funded_mll "
           "labs.010_011_50k_dpp.daily_path_mll_effect labs.006_50k_static.funded_daily_loss_limit "
           "labs.010_011_50k_dpp.funded_daily_loss_limit labs.006_50k_static.funded_payout_path "
           "labs.010_011_50k_dpp.funded_consistency labs.010_011_50k_dpp.payout_path_choice "
           "labs.010_011_50k_dpp.daily_path_gate labs.010_011_50k_dpp.wd5_path_gate "
           "labs.010_011_50k_dpp.payout_resets_wd5_count labs.010_011_50k_dpp.daily_path_timing "
           "labs.006_50k_static.funded_payout_cap labs.010_011_50k_dpp.daily_path_max labs.010_011_50k_dpp.wd5_path_amount "
           "labs.010_50k_dpp_eod.wd5_path_cap labs.011_50k_dpp_static.wd5_path_cap labs.010_011_50k_dpp.payout_split "
           "labs.010_011_50k_dpp.funded_position_limit labs.006_50k_static.funded_seats "
           "labs.010_011_50k_dpp.funded_seats labs.50k_static.tier1_news_cap "
           "mffu.rapideod50k.eval_profit_target mffu.rapid50k.eval_profit_target mffu.pro50k.eval_profit_target "
           "mffu.builder50k.eval_profit_target mffu.pro50k_oneday.eval_terms mffu.rapideod50k.eval_drawdown "
           "mffu.rapid50k.eval_drawdown mffu.pro50k.eval_drawdown mffu.builder50k.eval_drawdown mffu.eval_drawdown_lock "
           "mffu.eval_drawdown_open_equity mffu.rapideod50k.eval_daily_loss_limit mffu.pro50k.eval_daily_loss_limit "
           "mffu.rapid50k.daily_loss_limit mffu.rapideod50k.eval_consistency mffu.rapid50k.eval_consistency "
           "mffu.pro50k.eval_consistency mffu.builder50k.eval_consistency mffu.eval_consistency_breach "
           "mffu.rapideod50k.eval_min_days mffu.rapid50k.eval_min_days mffu.pro50k.eval_min_days "
           "mffu.builder50k.eval_min_days mffu.rapideod50k.eval_position_limit mffu.rapid50k.eval_position_limit "
           "mffu.pro50k.eval_position_limit mffu.builder50k.position_limit mffu.inactivity_rule mffu.builder50k.eval_fee "
           "mffu.billing_basis mffu.max_eval_accounts mffu.activation_fee mffu.rapideod50k.funded_drawdown "
           "mffu.rapideod50k.funded_drawdown_lock mffu.rapid50k.funded_drawdown mffu.pro50k.funded_drawdown "
           "mffu.builder50k.funded_drawdown mffu.rapideod50k.funded_daily_loss_limit mffu.pro50k.funded_daily_loss_limit "
           "mffu.rapideod50k.funded_consistency mffu.rapid50k.funded_consistency mffu.pro50k.funded_consistency "
           "mffu.builder50k.funded_consistency mffu.rapideod50k.payout_gate mffu.rapid50k.payout_gate "
           "mffu.pro50k.payout_timing mffu.builder50k.payout_gate mffu.rapideod50k.payout_cap mffu.rapideod50k.payout_min "
           "mffu.rapideod50k.payout_split mffu.rapid50k.payout_min mffu.rapid50k.payout_split mffu.pro50k.payout_min "
           "mffu.pro50k.payout_split mffu.builder50k.payout_cap mffu.builder50k.payout_min mffu.builder50k.payout_split "
           "mffu.builder50k.max_sim_payouts mffu.pro50k.live_review_triggers mffu.rapideod50k.funded_position_limit "
           "mffu.max_funded_accounts mffu.builder50k.funded_seats mffu.commissions "
           "mffu.rapideod50k.funded_single_day_profit_ceiling mffu.rapid50k.funded_single_day_profit_ceiling "
           "mffu.rapid50k.funded_news mffu.pro50k.funded_news mffu.builder50k.news mffu.news_tier1_rule mffu.hedging_rule "
           "mffu.coordinated_trading_rule mffu.automation_and_sim_fills mffu.pro50k.funded_conduct_policy "
           "mffu.pro50k.funded_position_limit labs.006_50k_static.funded_position_limit subscription_fee_naf_50k tou_s8_relative_position_size").split():
    RECORD_KEYS[_k] = "verified"
for _k in ("labs.010_50k_dpp_eod.eval_fee labs.006_50k_static.purchase_limit labs.010_011_50k_dpp.purchase_limit "
           "labs.010_011_50k_dpp.daily_path_min mffu.builder50k.eval_drawdown_breach_basis mffu.builder50k.daily_loss_limit "
           "mffu.eval_consistency_base mffu.rapideod50k.eval_fee mffu.rapid50k.eval_fee mffu.pro50k.eval_fee "
           "mffu.pro50k_oneday.eval_fee mffu.reset_fee mffu.rapid50k.funded_drawdown_lock mffu.pro50k.funded_drawdown_lock "
           "mffu.pro50k.payout_buffer mffu.pro50k.payout_cap mffu.builder50k.live_trigger "
           "mffu.rapid50k.funded_position_limit mffu.payout_processing_time mffu.rapideod50k.funded_news "
           "mffu.rapideod50k.commissions mffu.rapid50k.commissions mffu.pro50k.commissions mffu.pro50k_oneday.commissions "
           "mffu.builder50k.commissions mffu.copy_trading_own_accounts mffu.news_all_releases_protocol "
           "mffu.one_time_cutover_date").split():
    RECORD_KEYS[_k] = "unverified"
for _k in ("labs.006_50k_static.funded_payout_terms_other labs.010_011_50k_dpp.tier1_news_cap "
           "mffu.rapideod50k.payout_request_amount mffu.rapid50k.payout_cap mffu.hold_queue_behaviour mffu.payout_fee "
           "mffu.rapideod50k.eval_single_day_profit_ceiling mffu.builder50k.eval_single_day_profit_ceiling "
           "mffu.builder50k.funded_single_day_profit_ceiling mffu.pro50k.eval_single_day_profit_ceiling "
           "mffu.pro50k.funded_single_day_profit_ceiling mffu.pro50k_oneday.eval_single_day_profit_ceiling "
           "mffu.pro50k_oneday.funded_single_day_profit_ceiling mffu.rapid50k.eval_single_day_profit_ceiling").split():
    RECORD_KEYS[_k] = "unstated"
RECORD_KEYS["activation_fee_naf_50k"] = "verified"
RECORD_KEYS["tier1_news_events_restriction"] = "changed"

#: Appendix R's Stage 2 keys (each must be verified in Stage 2's ledger)
STAGE2_KEYS: tuple[str, ...] = (
    "combine_profit_target", "combine_mll", "combine_mll_lock_at", "combine_consistency_max_day_frac",
    "combine_min_trading_days", "combine_position_size_limit", "subscription_fee", "billing_days",
    "billing_period_calendar_days", "combine_count_limit", "activation_fee", "xfa_activation_latency", "xfa_mll_start",
    "xfa_lock_at", "xfa_payout_path_choice", "xfa_std_winning_days", "xfa_std_winning_day_min",
    "require_profit_since_payout", "payout_max_frac_of_balance", "xfa_std_cap", "payout_min", "profit_split",
    "funded_scaling_plan", "scaling_tier_after_payout", "max_active_funded_accounts", "hold_queue_behaviour",
    "payout_fee", "payout_lag_days_aeropay", "cross_account_opposite_positions", "responsible_trading_program",
    "prohibited_trading_strategies", "prohibited_conduct")

#: 5.2's two-ended terms by U-rule: the record keys whose non-verified status (or verified with an unstated reach)
#: makes the term two-ended, and the mode-corners it splits (Appendix M); T-0 recomputes the corners from the record
TWO_ENDED: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "U-15": (("mffu.eval_consistency_base",), ("E:RE", "E:RED", "E:RI", "E:PRO"), "coin"),
    "U-32": (("mffu.rapideod50k.commissions", "mffu.rapid50k.commissions", "mffu.pro50k.commissions",
              "mffu.pro50k_oneday.commissions", "mffu.builder50k.commissions"),
             ("E:RE", "E:RED", "E:RI", "E:PRO", "E:PRO1", "E:B20", "E:B15", "F:RE", "F:RED", "F:RI", "F:PRO", "F:B20",
              "F:B15"), "costed"),
    "U-27": (("mffu.builder50k.eval_drawdown_breach_basis",), ("E:B20", "E:B15"), "coin"),
    "U-28": (("mffu.builder50k.daily_loss_limit",), ("E:B20", "E:B15", "F:B20", "F:B15"), "coin"),
    "U-20": (("labs.006_50k_static.funded_position_limit",), ("F:L6/std", "F:L6/con"), "costed"),
    "U-22": (("labs.010_011_50k_dpp.daily_path_min",), ("F:L10/day", "F:L11/day"), "coin"),
    "U-25": (("mffu.rapideod50k.payout_request_amount", "mffu.rapid50k.payout_cap", "mffu.pro50k.payout_cap"),
             ("F:RE", "F:RED", "F:RI", "F:PRO"), "coin"),
    "U-29": (("mffu.rapid50k.funded_drawdown_lock",), ("F:RI",), "coin"),
    "U-30": (("mffu.rapid50k.funded_position_limit",), ("F:RI",), "costed"),
    "U-16": (("mffu.pro50k.funded_drawdown_lock",), ("F:PRO",), "coin"),
    "U-17": (("mffu.pro50k.payout_buffer",), ("F:PRO",), "coin"),
    "U-26": (("mffu.pro50k.funded_position_limit",), ("F:PRO",), "costed"),
    "U-18": (("mffu.builder50k.payout_gate",), ("F:B20", "F:B15"), "coin"),
}
#: the verified entries whose reach is unstated (5.2: "verified, thresholds not stated", "verified; base implied",
#: "verified, counting not stated"), read by their U-rule whatever their status
VERIFIED_WITH_UNSTATED_REACH = frozenset({"labs.006_50k_static.funded_position_limit", "mffu.builder50k.payout_gate",
                                          "mffu.pro50k.funded_position_limit"})


def recomputed_corners() -> dict[str, int]:
    """5.2's mode-corners recomputed from the record (T-0 at the pin): a mode has two corners if any of its terms is
    two-ended by the record's statuses; counted with the shared-gross rule."""
    two: dict[str, set[str]] = {}
    for rule, (keys, modes, _scope) in TWO_ENDED.items():
        open_ = any(status(k) in ("unverified", "unstated") or k in VERIFIED_WITH_UNSTATED_REACH for k in keys)
        if open_:
            for m in modes:
                two.setdefault(m, set()).add(rule)
    two_c = int(NOT_RULE_VALUES["pair"])                          # a two-ended mode has two corners
    ev = sum(two_c if f"E:{m}" in two else 1 for m in EVAL_MODES)
    fu = sum(two_c if f"F:{m}" in two else 1 for m in FUNDED_MODES)
    shared = sum(1 for m, rules in two.items() if rules <= COSTED_ONLY)
    return {"evaluation": ev, "funded": fu, "shared": shared}


__all__ = ["DECLARATION", "DECLARATION_SHA256", "PINNING_ROW", "PREREG_ID", "STRICT", "LENIENT", "SINGLE", "EVAL",
           "FUNDED", "Declared", "DECLARED", "declared", "grid_w", "grid_r", "grid_s_part_b", "price_grid", "SEEDS",
           "RESERVED_SEEDS", "TIMING_SEED", "seed", "QuoteFigure", "A19", "quote_figure", "calendar_to_sessions",
           "soft_dll_general_article", "Allowance", "EvalTerms", "FundedTerms", "CONFIGS", "EVAL_MODES", "FUNDED_MODES",
           "FUNDED_OF", "EVAL_OF", "ModeCorner", "MODE_CORNERS", "COSTED_ONLY", "close_only_corners",
           "shared_gross_corners", "strict_twin", "U_RULES", "end", "eval_terms", "funded_terms", "lucid",
           "mode_corner_terms", "topstep_round_turn", "mffu_round_turn", "round_turn", "fill_slippage", "tick_values",
           "registered_stand_aside", "RECORD_KEYS", "STAGE2_KEYS", "TWO_ENDED", "VERIFIED_WITH_UNSTATED_REACH",
           "recomputed_corners", "micros_per_mini", "status", "TermParseError", "UnverifiedTerm"]
