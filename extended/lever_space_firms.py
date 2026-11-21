"""Q-151b: the lever spaces of My Funded Futures (MFFU) and Lucid, beside Topstep's (`extended/lever_space.py`;
`docs/plans/LEVER_TABLE_mffu.md`, `docs/plans/LEVER_TABLE_lucid.md`). The operator's direction is that each firm is
traded on its own execution protocol: a Topstep-tuned design is never carried unchanged to another firm. So each firm
gets its own lever space, with the same 39 lever ids, so that the design search runs per firm.

**The plans** (both $50K, Topstep's size): MFFU's **Rapid EOD 50K**, its default version without a daily loss limit
(RD-05's `RE`); Lucid's **LucidFlex 50K**, daily loss limit off, in its two consistency configurations (RD-05's `LU40`
and `LU50`). Each table says why.

**The rule readers.** `rule(firm, key)`: for `topstep` it is `lever_space.rule` itself (this repository's record first,
else Stage 2's ledger). For `mffu` the key is read from this repository's record (`config/rules_extended.yaml`) only;
nothing of MFFU is in Stage 2's ledger. For `lucid` the record wins where it holds the key (its re-reads,
`lucid.flex50k.funded_monthly_fee` and `lucid.flex50k.payout_fee`, supersede Stage 2's), else a `lucid.flex50k.<k>` key
is Stage 2's verified Lucid ledger's `<k>` (`vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml`, Stage 2
D-30, D-31; E-197 keeps LucidFlex on it). Lucid's terms now forbid automated reading (E-197), so a Lucid rule not in
these records is verified only from the operator's own transcription (`docs/OPERATOR_SETUP.md` item 11). A key absent
from the firm's records, or present with any status but `verified`, is refused: **`NotVerified`** (a subclass of
`firm_terms.UnverifiedTerm`), never guessed.

**No rule value is typed here**: every number of a rule-derived bound is read from its key and parsed fail-loud
(`firm_terms.parse`, with named groups); the only typed parameters are `FIRM_DECLARED`'s, each citing its source
(`tests/test_lever_space_firms.py` scans this file for the read values outside it). It reads rules and configuration
only -- never a bar, a trade or a result file.

**Conduct tier 1** (Stage 2 D-145; CHARTER 4; 3.4) is refused for every firm by `check_design`, which `sample` runs on
every draw: hedging (opposite positions across accounts or firms), simulator-fill exploitation, maximum size into major
news, one trade copied across accounts, anything that conceals a pattern -- **whatever a firm's own page permits** (Lucid
permits trade copiers, `copy_trading_terms`; the tier is ours). Automated or API order entry is refused as the
operator's hard limit (`HardLimitRefused`).
"""
from __future__ import annotations

import dataclasses
import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from types import SimpleNamespace
from typing import Any, Callable
from zoneinfo import ZoneInfo

import numpy as np
import yaml

from extended import day_calendar as DC
from extended import firm_terms as FT
from extended import lever_space as LS
from extended import modes_rules as MR
from extended import modes_terms as M
from extended.firm_terms import UnverifiedTerm, parse
from extended.lever_space import (ARITH, COMPUTE, DECL, DROPPED, FIXED, POLICY, RULE, SEARCHED, SHAPE, TODECL, TRIGGER,
                                  DroppedLever, Lever, LeverRefused, NotComputed, NotDeclared, Range, declared)

TASK = "Q-151b"
FIRMS = ("topstep", "mffu", "lucid")
TABLES = {"topstep": LS.TABLE, "mffu": "docs/plans/LEVER_TABLE_mffu.md", "lucid": "docs/plans/LEVER_TABLE_lucid.md"}
PLANS = {"topstep": "Topstep Trading Combine $50K and its funded account (RD-05 TS-S, TS-N)",
         "mffu": "My Funded Futures Rapid EOD 50K, the default version without a daily loss limit (RD-05 RE)",
         "lucid": "LucidFlex 50K, daily loss limit off, standard or add-on consistency (RD-05 LU40, LU50)"}
MFFU_P = "mffu.rapideod50k."
LUCID_P = "lucid.flex50k."
LUCID_CONFIGS = ("LU40", "LU50")             # RD-05 2.1's names: the standard and the add-on consistency checkout
IDENTICAL, DIFFERS, REFUSED = "identical", "differs", "refused"


class NotVerified(UnverifiedTerm):
    """A rule a lever leans on is not verified in its firm's records: absent from them, or of any status but
    `verified`. Refused, never guessed; the key is a work-list item for `/verify-rule` (or, for Lucid, the operator's
    transcription, OPERATOR_SETUP item 11)."""


class TierOneRefused(LeverRefused):
    """A design that is conduct tier 1 (Stage 2 D-145; CHARTER 4): refused for every firm, whatever its pages allow."""


class HardLimitRefused(LeverRefused):
    """A design outside the operator's hard limits (no automated or API order entry; CLAUDE.md, CHARTER 4)."""


# ------------------------------------------------------------------------------------------------ the declared table


#: this module's own parameters, each citing its source -- never a rule value
FIRM_DECLARED: dict[str, LS.Declared] = {
    "mffu.payout_path": LS.Declared(("buffer_then_daily",),
                                    "Rapid EOD 50K has one payout path (`mffu.rapideod50k.payout_gate`): the label "
                                    "only; every figure is read from the key"),
    "lucid.payout_path": LS.Declared(("lucid_cycle",), "LucidFlex has one payout path (`payout_frequency_gate`): the "
                                     "label only; every figure is read from the key"),
    "clock.reference_days": LS.Declared((date(2023, 1, 17), date(2023, 7, 17)),
                                        "Q-181b: the two search-year days (winter and summer time) on which a day-free "
                                        "call converts a firm's New York clock to CT; both must agree, or it refuses"),
    "sample.max_redraws": LS.Declared(10_000, "Q-151b: a draw refused by a combination rule (never a tier-1 refusal) is "
                                      "redrawn at most this many times per design before sampling stops"),
}


def fdeclared(name: str) -> Any:
    return FIRM_DECLARED[name].value


#: conduct tier 1 (Stage 2 D-145), as design settings: a truthy marker refuses the design for every firm
TIER1_MARKERS: dict[str, str] = {
    "opposing_positions": "hedging: opposite positions across accounts or firms",
    "copy_across_accounts": "one trade copied across accounts",
    "sim_fill_exploit": "simulator-fill exploitation (auto-breakeven, tight brackets, several limits at one price)",
    "max_size_into_news": "maximum size into major news",
    "conceal_pattern": "anything that conceals a pattern",
}
#: lever values that are tier 1 wherever they appear (a tampered or extended space is refused at sampling)
TIER1_VALUES: dict[str, dict[Any, str]] = {
    "T8": {"opposite": "hedging", "hedge": "hedging"},
    "T5": {"multiple_limits_one_price": "simulator-fill exploitation"},
    "S7": {"on": "simulator-fill exploitation (auto-breakeven)"},
    "A15": {"copy": "one trade copied across accounts", "all_accounts": "one trade copied across accounts"},
}


def conduct_check(settings: dict[str, Any]) -> None:
    """Refuse conduct tier 1 and the operator's hard limits, for every firm (CHARTER 4; Stage 2 D-145)."""
    for marker, what in TIER1_MARKERS.items():
        if settings.get(marker):
            raise TierOneRefused(f"REFUSED (conduct tier 1): {what} ({marker})")
    if int(settings.get("accounts_per_trade", 1)) > 1:                # one account per trade
        raise TierOneRefused("REFUSED (conduct tier 1): one trade copied across accounts (accounts_per_trade)")
    for lever, bad in TIER1_VALUES.items():
        v = settings.get(lever)
        if v in bad:
            raise TierOneRefused(f"REFUSED (conduct tier 1): {lever} = {v!r} is {bad[v]}")
    entry = settings.get("order_entry")
    if entry not in (None, "hand"):
        raise HardLimitRefused(f"REFUSED (hard limit): order entry {entry!r} -- every order is placed by hand")


# ------------------------------------------------------------------------------------------------ the rule readers


@lru_cache(maxsize=1)
def _lucid_ledger() -> dict[str, dict[str, Any]]:
    return yaml.safe_load(FT.LUCID_LEDGER.read_text(encoding="utf-8"))["rules"]


def _record_has(key: str) -> bool:
    try:
        FT.record_entry(key)
    except KeyError:
        return False
    return True


def _record(key: str) -> Any:
    try:
        return FT.record_value(key)
    except UnverifiedTerm as exc:
        raise NotVerified(str(exc)) from None


def _lucid_entry(key: str) -> dict[str, Any] | None:
    return _lucid_ledger().get(key[len(LUCID_P):]) if key.startswith(LUCID_P) else None


def rule(firm: str, key: str) -> Any:
    """A verified rule of `firm` by its key; `NotVerified` for an absent key or any status but `verified`."""
    if firm == "topstep":
        return LS.rule(key)
    if firm == "mffu":
        if not key.startswith("mffu."):
            raise ValueError(f"{key!r} is not an MFFU key")
        if not _record_has(key):
            raise NotVerified(f"{key}: not on the record (config/rules_extended.yaml) -- to verify (/verify-rule)")
        return _record(key)
    if firm == "lucid":
        if not key.startswith("lucid."):
            raise ValueError(f"{key!r} is not a Lucid key")
        if _record_has(key):                                   # the record's re-read supersedes Stage 2's
            return _record(key)
        e = _lucid_entry(key)
        if e is None:
            raise NotVerified(f"{key}: on neither the record nor Stage 2's Lucid ledger -- to verify from the "
                              f"operator's transcription (OPERATOR_SETUP item 11; E-197)")
        if e.get("status") != "verified" or e.get("value") is None:
            raise NotVerified(f"{key}: status {e.get('status')!r} in Stage 2's Lucid ledger, not 'verified'")
        return e["value"]
    raise ValueError(f"unknown firm {firm!r}")


def note(firm: str, key: str) -> str:
    """A verified Lucid ledger entry's note, flattened (its value read first, so its status is checked)."""
    if firm != "lucid":
        raise ValueError("only Stage 2's Lucid ledger carries the notes this loader reads")
    rule(firm, key)
    if _record_has(key):
        e = FT.record_entry(key)
        return " ".join(str(e.get("quote", "")).split())
    return " ".join(str(_lucid_entry(key).get("note", "")).split())


def rule_status(firm: str, key: str) -> tuple[str, str]:
    """(ledger, status): 'record', 'stage2', 'stage2_lucid', or ('absent', 'absent')."""
    if firm == "topstep":
        return LS.rule_status(key)
    if _record_has(key):
        return "record", str(FT.record_entry(key).get("status"))
    if firm == "lucid":
        e = _lucid_entry(key)
        if e is not None:
            return "stage2_lucid", str(e.get("status"))
    return "absent", "absent"


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def _p(firm: str, key: str, pattern: str) -> re.Match[str]:
    return parse(pattern, rule(firm, key), key)


# ------------------------------------------------------------------------------------------------ MFFU's terms


def _mffu_eval_room() -> float:
    return _num(_p("mffu", MFFU_P + "eval_drawdown", r"^(?P<d>\d+) USD, end-of-day trailing").group("d"))


def _mffu_funded_room() -> float:
    m = _p("mffu", MFFU_P + "funded_drawdown",
           r"^starts at a \$0 balance, (?P<d>\d+) USD below it; end-of-day trailing, never intraday")
    return _num(m.group("d"))


def _mffu_contracts(key: str) -> tuple[int, int]:
    m = _p("mffu", key, r"^(?P<minis>\d+) mini / (?P<micros>\d+) micro$")
    return int(m.group("minis")), int(m.group("micros"))


def _mffu_eval() -> SimpleNamespace:
    """RE's evaluation, as `modes_rules.k_eval` and `r_flip` read it."""
    _p("mffu", "mffu.eval_consistency_breach", r"trades more days until it is met")          # 'extends'
    _p("mffu", MFFU_P + "eval_daily_loss_limit", r"^none on the default version")
    return SimpleNamespace(target=float(rule("mffu", MFFU_P + "eval_profit_target")), mll=_mffu_eval_room(),
                           consistency=float(rule("mffu", MFFU_P + "eval_consistency")),
                           min_days=int(rule("mffu", MFFU_P + "eval_min_days")), lifespan=None,
                           consistency_semantics="extends", dll=None)


def _mffu_gate() -> dict[str, float]:
    m = _p("mffu", MFFU_P + "payout_gate",
           r"^first payout: at least \$(?P<buffer>[\d,]+) of realised profit \(the buffer\), (?P<hours>\d+) hours after "
           r"the first trade; each later payout: net profit since the last payout of at least \$(?P<since>[\d,]+); "
           r"daily")
    return {"buffer": _num(m.group("buffer")), "wait_hours": _num(m.group("hours")), "since_min": _num(m.group("since"))}


NEW_YORK = ZoneInfo("America/New_York")
_MFFU_HOURS = "mffu.trading_hours"


def _ny_pm_to_ct(h: int, m: int, d: date) -> int:
    """A New York 12-hour PM clock time on day `d`, as wall-clock minutes CT (zoneinfo, DST-aware on both sides)."""
    t = datetime(d.year, d.month, d.day, h + LS.PM // 60, m, tzinfo=NEW_YORK).astimezone(DC.CHICAGO)
    return t.hour * 60 + t.minute


def mffu_trading_day(day: date | None = None) -> dict[str, Any]:
    """MFFU's trading day from `mffu.trading_hours` (H9558251, H9735811; Q-181b): the reopen at the Globex open and the
    automatic close, both printed as "EST" and read as New York local time (the verifier's labelled reading), converted
    to wall-clock minutes CT for `day` -- or, day-free, on both `clock.reference_days`, which must agree. No last-entry
    time apart from the close is stated, so the last new entry is the close. The reopen must equal the exchange's open
    in the same entry (H9735811), which checks the time-zone reading. Keys as `lever_space.trading_day`'s."""
    v = rule("mffu", _MFFU_HOURS)
    op = parse(r"from (?P<h>\d{1,2}):(?P<m>\d\d) PM \(the Globex open\)", v, _MFFU_HOURS)
    cl = parse(r"closed automatically at (?P<h>\d{1,2}):(?P<m>\d\d) PM on regular \(non-holiday\) trading days", v,
               _MFFU_HOURS)
    parse(r"times printed as EST", v, _MFFU_HOURS)
    parse(r"no last-entry time separate from the", v, _MFFU_HOURS)
    hol = parse(r"on holidays there is no auto-liquidation at the early close", v, _MFFU_HOURS)
    ex = parse(r"NQ and MNQ trade Sunday - Friday (?P<o>\d\d:\d\d) - (?P<c>\d\d:\d\d) CT", v, _MFFU_HOURS)
    days = (day,) if day is not None else tuple(fdeclared("clock.reference_days"))
    got = set()
    for d in days:
        reopen = _ny_pm_to_ct(int(op.group("h")), int(op.group("m")), d - timedelta(days=1))
        flat = _ny_pm_to_ct(int(cl.group("h")), int(cl.group("m")), d)
        got.add((reopen, flat))
    if len(got) != 1:
        raise LeverRefused("MFFU's New York clock converts to different CT times on the reference days")
    reopen, flat = got.pop()
    if reopen != LS._clock(ex.group("o")):
        raise LeverRefused("MFFU's reopen, read as New York time, is not the exchange's open in the same entry -- "
                           "the time-zone reading fails")
    length = (flat - reopen) % LS.MINUTES_PER_DAY
    return {"reopen": reopen, "flat": flat, "last_entry": flat, "length": length, "last_entry_offset": length,
            "clock": "EST read as New York local time (the verifier's labelled reading)",
            "holiday": hol.group(0), "day": day}


def mffu_session_windows(day: date) -> dict[str, tuple[int, int | None]]:
    """Trading day `day`'s MFFU sessions as [start, end) in minutes after MFFU's reopen: each start its local market
    time converted for that date (`day_calendar.anchored_starts`, E-231 (3); minutes after the 17:00 CT reopen, shifted
    to MFFU's reopen on that date), as `lever_space.session_windows(day)` does for Topstep. `ny` is split at T2b's
    boundary (to declare for this firm). Every boundary must fall inside MFFU's day."""
    if not isinstance(day, date):
        raise TypeError(f"mffu_session_windows reads one trading day's date, not {type(day).__name__}")
    td = mffu_trading_day(day)
    shift = DC.REOPEN_MIN - td["reopen"]
    a = DC.anchored_starts(day)
    starts = [(n, (int(a[n]) + shift) % LS.MINUTES_PER_DAY) for n in ("asia", "london", "ny")]
    for name, off in starts:
        if not 0 < off < td["length"]:
            raise LeverRefused(f"session boundary {name!r} lies outside MFFU's trading day ({_MFFU_HOURS})")
    edges = [0] + [off for _, off in starts] + [td["length"]]
    if edges != sorted(edges):
        raise LeverRefused("the session boundaries are out of order against MFFU's day")
    out: dict[str, tuple[int, int | None]] = dict(zip(("evening", "asia", "london", "ny"), zip(edges, edges[1:])))
    ny_start, ny_end = out.pop("ny")
    out["ny_am"], out["ny_pm"] = (ny_start, None), (None, ny_end)
    return out


def mffu_session_window_range(start: date, end: date) -> dict[str, Any]:
    """MFFU's sessions over the weekdays from `start` to `end` (`lever_space.trading_dates`), in the form of
    `lever_space.session_window_range`: each session's earliest and latest start and end (None where T2b leaves a
    boundary undeclared), and every distinct set of windows with its first date and day count."""
    rng: dict[str, dict[str, Any]] = {}
    distinct: dict[tuple, dict[str, Any]] = {}
    for d in LS.trading_dates(start, end):
        w = mffu_session_windows(d)
        e = distinct.setdefault(tuple(sorted(w.items())), {"first": d.isoformat(), "days": 0, "windows": w})
        e["days"] += 1
        for name, (a, b) in w.items():
            r = rng.setdefault(name, {"start": [a, a], "end": [b, b]})
            for k, v in (("start", a), ("end", b)):
                if v is not None:
                    lo, hi = r[k]
                    r[k] = [v if lo is None else min(lo, v), v if hi is None else max(hi, v)]
    return {"span": (start.isoformat(), end.isoformat()),
            "range": {k: {"start": tuple(v["start"]), "end": tuple(v["end"])} for k, v in rng.items()},
            "distinct": list(distinct.values())}


def _mffu_session() -> Range:
    return Range("T2", "choices", values=tuple(declared("sessions")), unit="session of MFFU's day",
                 detail={"windows": mffu_session_window_range(DC.SEARCH_START, DC.SEARCH_END),
                         "day": mffu_trading_day()})


def _mffu_entry_window() -> Range:
    td = mffu_trading_day()
    return Range("T3", "interval", lo=0.0, hi=float(td["last_entry_offset"]), step=float(declared("mark_step_min")),
                 unit="minutes after MFFU's reopen (an offer mark's time inside its session)", detail={"day": td})


# ------------------------------------------------------------------------------------------------ Lucid's terms


def _lucid_eod(phase: str) -> None:
    if str(rule("lucid", LUCID_P + f"{phase}_drawdown_type")) != "eod_trailing":
        raise FT.TermParseError(f"Lucid's {phase} drawdown is no longer end-of-day trailing -- re-derive")


def _lucid_room(phase: str) -> float:
    _lucid_eod(phase)
    return float(rule("lucid", LUCID_P + f"{phase}_drawdown_amount"))


def _lucid_consistency() -> dict[str, dict[str, Any]]:
    """Each configuration's share and fewest days: the standard from the entries' values, the add-on from their
    verified notes (Stage 2's adapter's reading, `propedge.contract.lucid.lucid_terms`)."""
    k = LUCID_P + "eval_consistency_rule"
    std = float(rule("lucid", k))
    n = note("lucid", k)
    pct = parse(r"Consistency Percentage must be (?P<p>\d+)% or less to be eligible to upgrade", n, k)
    add = parse(r"If you added the (?P<a>\d+)% consistency add-on at checkout, it must be (?P<b>\d+)% or less", n, k)
    if not math.isclose(_num(pct.group("p")) / M.NOT_RULE_VALUES["percent"], std) or add.group("a") != add.group("b"):
        raise FT.TermParseError(f"{k}: its value and its note disagree -- re-derive")
    kd = LUCID_P + "eval_min_days"
    fast = parse(r"Pass in as few as (?P<d>\d+) days with (?P<p>\d+)% consistency, or (?P<da>\d+) days with the "
                 r"(?P<pa>\d+)% consistency add-on", note("lucid", kd), kd)
    if int(fast.group("d")) != int(rule("lucid", kd)) or fast.group("pa") != add.group("b"):
        raise FT.TermParseError(f"{kd}: its value and its note disagree -- re-derive")
    return {"LU40": {"consistency": std, "min_days": int(rule("lucid", kd))},
            "LU50": {"consistency": _num(add.group("b")) / M.NOT_RULE_VALUES["percent"], "min_days": int(fast.group("da"))}}


def _lucid_eval(config: str) -> SimpleNamespace:
    c = _lucid_consistency()[config]
    return SimpleNamespace(target=float(rule("lucid", LUCID_P + "eval_profit_target")), mll=_lucid_room("eval"),
                           consistency=c["consistency"], min_days=c["min_days"], lifespan=None,
                           consistency_semantics="extends", dll=None)


def _lucid_eval_contracts() -> tuple[int, int]:
    m = _p("lucid", LUCID_P + "eval_position_limit", r"^(?P<minis>\d+) minis / (?P<micros>\d+) micros$")
    return int(m.group("minis")), int(m.group("micros"))


def _lucid_ladder() -> tuple[tuple[float, int], ...]:
    v = rule("lucid", LUCID_P + "funded_position_limit")
    lad = tuple((_num(t), int(n)) for n, t in re.findall(r"(\d+) at \$([\d,]+)", str(v)))
    if not lad or lad[0][0] != 0.0 or list(lad) != sorted(lad):
        raise FT.TermParseError(f"Lucid's funded scaling ladder no longer parses: {v!r}")
    return lad


def _lucid_gate() -> dict[str, float]:
    k = LUCID_P + "payout_frequency_gate"
    v = rule("lucid", k)
    return {"winning_days": int(parse(r"(?P<n>\d+) days with daily profit", v, k).group("n")),
            "winning_day_min": _num(parse(r"daily profit >= \$(?P<m>[\d,]+)", v, k).group("m")),
            "cycle_net_min": _num(parse(r"net profit >= \$(?P<m>[\d,]+)", v, k).group("m")),
            "max_payouts": int(parse(r"max (?P<n>\d+) payouts per account", v, k).group("n"))}


def _lucid_cap() -> dict[str, float]:
    m = _p("lucid", LUCID_P + "payout_cap", r"^min\((?P<frac>0\.\d+) \* profits, (?P<cap>\d+)\) per request$")
    return {"frac": float(m.group("frac")), "cap": float(m.group("cap"))}


def _lucid_funded() -> SimpleNamespace:
    g, c = _lucid_gate(), _lucid_cap()
    if str(rule("lucid", LUCID_P + "funded_consistency_rule")) != "none":
        raise FT.TermParseError("Lucid's funded account now has a consistency rule -- re-derive")
    return SimpleNamespace(mode="LU", corner=M.SINGLE, gate="lucid", request="lucid", winning_days=g["winning_days"],
                           frac=c["frac"], cap=c["cap"], floor_start=-_lucid_room("funded"), dll=None)


def _lucid_accounts() -> dict[str, int]:
    k = LUCID_P + "max_accounts"
    n = note("lucid", k)
    total = int(parse(r"maximum of (?P<n>\d+) accounts in total", n, k).group("n"))
    reserve = parse(r"You may keep (?P<e>\d+) evaluation accounts in reserve while you have (?P<f>\d+) funded "
                    r"accounts", n, k)
    ke = LUCID_P + "eval_count_limit"
    parse(r"You may trade evaluation accounts while they are in reserve", note("lucid", ke), ke)
    return {"funded": int(rule("lucid", k)), "evaluations": int(rule("lucid", ke)),
            "total": total, "reserve_evaluations": int(reserve.group("e")), "reserve_with_funded": int(reserve.group("f"))}


_LUCID_PRICE_LINE = {"LU40": r"DLL OFF \+ 40 %: \$(?P<p>[\d,]+(?:\.\d+)?)",
                     "LU50": r"DLL OFF \+ 50 % add-on: \$(?P<p>[\d,]+(?:\.\d+)?)"}


def _lucid_prices() -> dict[str, float]:
    """Each configuration's one-time evaluation price: `eval_fee`'s value (the standard), and the add-on's line in its
    verified note (the operator's card read, Stage 2 D-31; `propedge.contract.lucid._PRICE_LINE`)."""
    k = LUCID_P + "eval_fee"
    v = float(rule("lucid", k))
    n = note("lucid", k)
    for pat in (r"W/ COUPON AT CHECKOUT", r"multiple time thing", r"one-time", r"DLL OFF"):
        parse(pat, n, k)
    out = {c: _num(parse(p, n, k).group("p")) for c, p in _LUCID_PRICE_LINE.items()}
    if not math.isclose(out["LU40"], v):
        raise FT.TermParseError(f"{k}: its value and its note's standard line disagree -- re-derive")
    return out


# ------------------------------------------------------------------------------------------------ shared arithmetic


def stop_caps(firm: str) -> dict[str, Any]:
    """S1's caps for a firm, contract arithmetic before costs (as `lever_space.stop_caps`): the registered stand-aside
    floor (Stage 2 D-271 (3)), and the widest stop at which one micro's stop-out fills the firm's larger start room."""
    if firm == "topstep":
        return LS.stop_caps()
    sa = M.registered_stand_aside()
    floor_ticks = max(int(sa["combine"][1]), int(sa["funded"][1]))
    tv = M.tick_values()["MNQ"]
    room = max(_eval_room(firm), _funded_room(firm))
    cap_ticks = int(math.floor(room / tv + 1e-9))
    if cap_ticks <= floor_ticks:
        raise LeverRefused("the stop's cap is not above its floor")
    return {"floor_ticks": floor_ticks, "cap_ticks": cap_ticks, "tick_value_mnq": tv, "room": room,
            "source": sa["source"]}


def _eval_room(firm: str) -> float:
    return _mffu_eval_room() if firm == "mffu" else _lucid_room("eval")


def _funded_room(firm: str) -> float:
    return _mffu_funded_room() if firm == "mffu" else _lucid_room("funded")


# ------------------------------------------------------------------------------------------------ resolvers


def _risk(firm: str, lid: str) -> Range:
    caps = stop_caps(firm)
    lo = caps["floor_ticks"] * caps["tick_value_mnq"]
    hi = _eval_room(firm) if lid == "S3" else _funded_room(firm)
    return Range(lid, "interval", lo=lo, hi=hi, step=None,
                 unit="dollars at the stop (share of the start room beside); whole micros at the trade's stop",
                 detail={"lo_share": lo / hi, "hi_share": 1.0, "caps": caps})


def _mix(firm: str) -> Range:
    if firm == "mffu":
        pos = {"evaluation": _mffu_contracts(MFFU_P + "eval_position_limit"),
               "funded": _mffu_contracts(MFFU_P + "funded_position_limit"), "funded_ladder": None}
    else:
        lad = _lucid_ladder()
        pos = {"evaluation": _lucid_eval_contracts(), "funded": (lad[-1][1], None), "funded_ladder": lad}
    return Range("S5", "choices", values=tuple(declared("mixes")), unit="instrument mix",
                 detail={"micros_per_mini": M.micros_per_mini(), "contracts": pos})


def _policy_eval(firm: str) -> Range:
    configs = {"RE": _mffu_eval()} if firm == "mffu" else {c: _lucid_eval(c) for c in LUCID_CONFIGS}
    det = {c: {"k_E": MR.k_eval(t), "r_flip_by_w": {w: MR.r_flip(M.EVAL, t, w) for w in M.grid_w()}}
           for c, t in configs.items()}
    return Range("A1", "choices", values=tuple(declared("policies")), unit="evaluation sizing policy", detail=det)


def _policy_funded_lucid() -> Range:
    f = _lucid_funded()
    det = {"LU": {"k_F": MR.k_funded(f)["k_F"], "b_star": MR.b_star(f)["b_star"],
                  "r_flip_by_w": {w: MR.r_flip(M.FUNDED, f, w) for w in M.grid_w()}}}
    return Range("A2", "choices", values=tuple(declared("policies")), unit="funded sizing policy", detail=det)


def _session_rule(firm: str) -> Range:
    if firm == "mffu":
        t = _mffu_eval()
        if str(rule("mffu", MFFU_P + "funded_consistency")) != "none":
            raise FT.TermParseError("Rapid EOD's funded account now has a consistency rule -- re-derive")
        ev = {"RE": t.consistency * t.target}
    else:
        ev = {c: _lucid_eval(c).consistency * _lucid_eval(c).target for c in LUCID_CONFIGS}
        _lucid_funded()
    return Range("A3", "choices", values=tuple(declared("session_rules")), unit="trades a session",
                 detail={"cap_evaluation": ev, "cap_funded": None})


def _price_path_lucid() -> Range:
    parse(r"No activation fees to upgrade to funded account", note("lucid", LUCID_P + "funded_type"),
          LUCID_P + "funded_type")
    _lucid_consistency()
    return Range("A4", "choices", values=LUCID_CONFIGS, unit="checkout configuration (price and consistency)",
                 detail={"one_time_price": _lucid_prices(), "activation": 0.0})


def _payout_path(firm: str) -> Range:
    if firm == "mffu":
        _p("mffu", MFFU_P + "payout_cap", r"^no cap per payout cycle")
        det = {**_mffu_gate(), "payout_min": float(rule("mffu", MFFU_P + "payout_min")),
               "split": float(rule("mffu", MFFU_P + "payout_split"))}
        vals = fdeclared("mffu.payout_path")
    else:
        det = {**_lucid_gate(), **_lucid_cap(), "payout_min": float(rule("lucid", LUCID_P + "payout_min")),
               "split": float(rule("lucid", LUCID_P + "payout_split"))}
        vals = fdeclared("lucid.payout_path")
    return Range("A5", "fixed", values=tuple(vals), unit="funded payout path (one path)", detail=det)


def _seats(firm: str) -> Range:
    if firm == "mffu":
        n = int(_p("mffu", "mffu.max_funded_accounts", r"Rapid EOD 50K at most (?P<n>\d+)").group("n"))
        det: dict[str, Any] = {}
    else:
        acc = _lucid_accounts()
        n, det = acc["funded"], {"accounts": acc}
    return Range("A6", "interval", lo=1.0, hi=float(n), step=1.0, unit="funded accounts at once", detail=det)


def _evals(firm: str) -> Range:
    cap = int(rule("mffu", "mffu.max_eval_accounts")) if firm == "mffu" else _lucid_accounts()["evaluations"]
    hi = min(int(declared("evals_max")), cap)
    return Range("A7", "interval", lo=1.0, hi=float(hi), step=1.0, unit="evaluations running at once",
                 detail={"declared_max": declared("evals_max"), "firm_cap": cap})


def _banking_lucid() -> Range:
    return Range("A8", "choices", values=tuple(declared("banking")), unit="banking rule",
                 detail={"accounts": _lucid_accounts()})


def _purchase_rule(firm: str) -> Range:
    if firm == "mffu":
        _p("mffu", "mffu.billing_basis", r"^one-time payment for new purchases")
    else:
        if str(rule("lucid", LUCID_P + "eval_time_limit")) != "none":
            raise FT.TermParseError("LucidFlex's evaluation now has a time limit -- re-derive")
        parse(r"One-time fee, no monthly rebilling", note("lucid", LUCID_P + "eval_time_limit"),
              LUCID_P + "eval_time_limit")
    return Range("A10", "choices", values=tuple(declared("purchase_rules")), unit="evaluation-purchase rule")


def _payout_first_lucid() -> Range:
    lock = _num(_p("lucid", LUCID_P + "eval_drawdown_lock", r"^locks_at_start_plus_(?P<x>\d+)$").group("x"))
    forced = _num(_p("lucid", LUCID_P + "payout_balance_consequence",
                     r"MLL locks at start \+ \$(?P<x>\d+) .*upon payout request").group("x"))
    if forced != lock:
        raise FT.TermParseError("Lucid's payout lock and its trailing lock differ -- re-derive")
    return Range("A18", "choices", values=tuple(declared("payout_first")), unit="first-request rule",
                 detail={"lock_above_start": lock, "request_forces_lock": True, **_lucid_gate(),
                         "payout_min": float(rule("lucid", LUCID_P + "payout_min"))})


def _payout_cadence(firm: str) -> Range:
    det = _mffu_gate() if firm == "mffu" else _lucid_gate()
    return Range("A20", "fixed", values=tuple(declared("payout_cadence")), unit="request cadence", detail=det)


def _entry_type(firm: str) -> Range:
    if firm == "mffu":
        _p("mffu", "mffu.automation_and_sim_fills", r"multiple limit orders at one price")
    else:
        _p("lucid", LUCID_P + "prohibited_conduct", r"exploiting platform/sim mechanics")
    return LS._entry_type()


def _side(firm: str) -> Range:
    if firm == "mffu":
        _p("mffu", "mffu.hedging_rule", r"^prohibited: buy and sell positions on the same underlying")
    else:
        _p("lucid", LUCID_P + "prohibited_conduct", r"cross-account, cross-user, cross-firm")
    return LS._side()


def _owed(what: str) -> Callable[[], Range]:
    def f() -> Range:
        raise LeverRefused(f"{what}: the parse is owed once its key is verified")
    return f


# ------------------------------------------------------------------------------------------------ the levers


def _L(i, layer, name, cls, source, keys="", depends="", resolver=None) -> Lever:
    return Lever(i, layer, name, cls, source, tuple(keys.split()), tuple(depends.split()), resolver)


def _mffu_levers() -> dict[str, Lever]:
    P = MFFU_P
    f = "mffu"
    return {lv.id: lv for lv in (
        _L("T1", TRIGGER, "signal source", SEARCHED, DECL, "", "T2 T3 T4 T5 A16", LS._sources),
        _L("T2", TRIGGER, "session", SEARCHED, ARITH, "mffu.trading_hours", "T1 T2b T3", _mffu_session),
        _L("T2b", TRIGGER, "NY AM / NY PM boundary", FIXED, TODECL, "", "T2"),
        _L("T3", TRIGGER, "entry window (offer marks)", SEARCHED, ARITH, "mffu.trading_hours", "T2 T4 A3",
           _mffu_entry_window),
        _L("T4", TRIGGER, "latency L", SEARCHED, DECL, "", "T1 T3 T5", LS._latency),
        _L("T5", TRIGGER, "entry type", SEARCHED, DECL, "mffu.automation_and_sim_fills", "T1 T4 T6",
           lambda: _entry_type(f)),
        _L("T6", TRIGGER, "limit working window", FIXED, DECL, "", "T5", LS._limit_window),
        _L("T7", TRIGGER, "admission by forecast resolution", SEARCHED, COMPUTE, "", "T1 T3 S1 S2"),
        _L("T8", TRIGGER, "side rule", FIXED, DECL, "mffu.hedging_rule", "T1 T5 A15", lambda: _side(f)),
        _L("S1", SHAPE, "stop width", SEARCHED, COMPUTE, f"{P}eval_drawdown {P}funded_drawdown", "T2 S2 S3 S4 S5"),
        _L("S2", SHAPE, "reward-to-risk w", SEARCHED, DECL, "", "S1 A1 A2", LS._ratio),
        _L("S3", SHAPE, "dollar risk, evaluation", SEARCHED, ARITH, f"{P}eval_drawdown {P}eval_position_limit",
           "S1 S5 A1", lambda: _risk(f, "S3")),
        _L("S4", SHAPE, "dollar risk, funded", SEARCHED, ARITH, f"{P}funded_drawdown {P}funded_position_limit",
           "S1 S5 A2 A5", lambda: _risk(f, "S4")),
        _L("S5", SHAPE, "instrument mix", SEARCHED, DECL, f"{P}eval_position_limit {P}funded_position_limit "
           "mffu.hedging_rule", "S3 S4", lambda: _mix(f)),
        _L("S6", SHAPE, "maximum hold (time stop)", DROPPED, DECL, "", ""),
        _L("S7", SHAPE, "breakeven stop move", DROPPED, DECL, "mffu.automation_and_sim_fills", "T1"),
        _L("S8", SHAPE, "partial exits, scaling in", DROPPED, DECL, "", ""),
        _L("S9", SHAPE, "contracts", DROPPED, ARITH, "", "S1 S3 S4 S5"),
        _L("A1", POLICY, "steady or flip, evaluation", SEARCHED, ARITH,
           f"{P}eval_profit_target {P}eval_consistency {P}eval_min_days {P}eval_drawdown "
           f"{P}eval_daily_loss_limit mffu.eval_consistency_breach", "S2 S3", lambda: _policy_eval(f)),
        _L("A2", POLICY, "steady or flip, funded", SEARCHED, ARITH,
           f"{P}payout_gate {P}payout_min {P}payout_cap {P}payout_request_amount {P}funded_drawdown", "S2 S4 A5",
           _owed("A2")),
        _L("A3", POLICY, "session rule q (when to stop)", SEARCHED, DECL,
           f"{P}eval_consistency {P}eval_profit_target {P}funded_consistency", "T3 A5", lambda: _session_rule(f)),
        _L("A4", POLICY, "price path", FIXED, RULE, f"{P}eval_fee mffu.activation_fee mffu.billing_basis", "A12",
           _owed("A4")),
        _L("A5", POLICY, "payout path", FIXED, RULE, f"{P}payout_gate {P}payout_min {P}payout_cap {P}payout_split",
           "A2 A3 A18 A19", lambda: _payout_path(f)),
        _L("A6", POLICY, "funded seats", SEARCHED, RULE, "mffu.max_funded_accounts", "A7 A8 A15", lambda: _seats(f)),
        _L("A7", POLICY, "evaluations at once", SEARCHED, DECL, "mffu.max_eval_accounts", "A6 A8 A11",
           lambda: _evals(f)),
        _L("A8", POLICY, "banking while a pass waits", SEARCHED, DECL, "mffu.hold_queue_behaviour", "A6 A7 A9",
           _owed("A8")),
        _L("A9", POLICY, "the hold's expiry (two readings)", FIXED, DECL,
           "mffu.hold_queue_behaviour mffu.hold_expiry_days", "A8 A10", _owed("A9")),
        _L("A10", POLICY, "evaluation-purchase rule", SEARCHED, DECL, "mffu.billing_basis", "A9 A11",
           lambda: _purchase_rule(f)),
        _L("A11", POLICY, "evaluation-purchase budget", SEARCHED, DECL, "mffu.account_start_rate_limit", "A7 A10",
           _owed("A11")),
        _L("A12", POLICY, "Back2Funded reactivations", DROPPED, DECL, "", "A4 A6 A18"),
        _L("A13", POLICY, "resets", DROPPED, DECL, "mffu.reset_fee", "A4"),
        _L("A14", POLICY, "daily-loss-limit election", DROPPED, DECL, f"{P}eval_daily_loss_limit", "S3 S4"),
        _L("A15", POLICY, "routing (which account takes a trade)", SEARCHED, TODECL, "", "A6 A7 A16 T8"),
        _L("A16", POLICY, "signal mix: shares and account assignment", SEARCHED, TODECL, "", "T1 A15"),
        _L("A17", POLICY, "state rule (sizing by distance to floor or target)", SEARCHED, TODECL, "", "S3 S4 A1 A2"),
        _L("A18", POLICY, "first payout request (RD-02 L1)", SEARCHED, DECL,
           f"{P}payout_gate {P}payout_min {P}funded_drawdown_lock {P}payout_request_amount", "A5 A19", _owed("A18")),
        _L("A19", POLICY, "request amount (RD-02 L2)", SEARCHED, DECL,
           f"{P}payout_request_amount {P}payout_cap {P}payout_min", "A5 A18", _owed("A19")),
        _L("A20", POLICY, "request cadence", FIXED, DECL, f"{P}payout_gate", "A18", lambda: _payout_cadence(f)),
        _L("A21", POLICY, "payout method", FIXED, DECL, "mffu.payout_fee mffu.payout_processing_time", "",
           _owed("A21")),
    )}


def _lucid_levers() -> dict[str, Lever]:
    P = LUCID_P
    f = "lucid"
    return {lv.id: lv for lv in (
        _L("T1", TRIGGER, "signal source", SEARCHED, DECL, "", "T2 T3 T4 T5 A16", LS._sources),
        _L("T2", TRIGGER, "session", SEARCHED, ARITH, f"{P}trading_hours", "T1 T2b T3", _owed("T2")),
        _L("T2b", TRIGGER, "NY AM / NY PM boundary", FIXED, TODECL, "", "T2"),
        _L("T3", TRIGGER, "entry window (offer marks)", SEARCHED, ARITH, f"{P}trading_hours", "T2 T4 A3",
           _owed("T3")),
        _L("T4", TRIGGER, "latency L", SEARCHED, DECL, "", "T1 T3 T5", LS._latency),
        _L("T5", TRIGGER, "entry type", SEARCHED, DECL, f"{P}prohibited_conduct", "T1 T4 T6", lambda: _entry_type(f)),
        _L("T6", TRIGGER, "limit working window", FIXED, DECL, "", "T5", LS._limit_window),
        _L("T7", TRIGGER, "admission by forecast resolution", SEARCHED, COMPUTE, "", "T1 T3 S1 S2"),
        _L("T8", TRIGGER, "side rule", FIXED, DECL, f"{P}prohibited_conduct", "T1 T5 A15", lambda: _side(f)),
        _L("S1", SHAPE, "stop width", SEARCHED, COMPUTE, f"{P}eval_drawdown_amount {P}funded_drawdown_amount",
           "T2 S2 S3 S4 S5"),
        _L("S2", SHAPE, "reward-to-risk w", SEARCHED, DECL, "", "S1 A1 A2", LS._ratio),
        _L("S3", SHAPE, "dollar risk, evaluation", SEARCHED, ARITH,
           f"{P}eval_drawdown_amount {P}eval_drawdown_type {P}eval_position_limit", "S1 S5 A1",
           lambda: _risk(f, "S3")),
        _L("S4", SHAPE, "dollar risk, funded", SEARCHED, ARITH,
           f"{P}funded_drawdown_amount {P}funded_drawdown_type {P}funded_position_limit", "S1 S5 A2 A5",
           lambda: _risk(f, "S4")),
        _L("S5", SHAPE, "instrument mix", SEARCHED, DECL, f"{P}eval_position_limit {P}funded_position_limit",
           "S3 S4", lambda: _mix(f)),
        _L("S6", SHAPE, "maximum hold (time stop)", DROPPED, DECL, "", ""),
        _L("S7", SHAPE, "breakeven stop move", DROPPED, DECL, f"{P}prohibited_conduct", "T1"),
        _L("S8", SHAPE, "partial exits, scaling in", DROPPED, DECL, "", ""),
        _L("S9", SHAPE, "contracts", DROPPED, ARITH, "", "S1 S3 S4 S5"),
        _L("A1", POLICY, "steady or flip, evaluation", SEARCHED, ARITH,
           f"{P}eval_profit_target {P}eval_consistency_rule {P}eval_min_days {P}eval_drawdown_amount", "S2 S3 A4",
           lambda: _policy_eval(f)),
        _L("A2", POLICY, "steady or flip, funded", SEARCHED, ARITH,
           f"{P}payout_frequency_gate {P}payout_cap {P}funded_drawdown_amount {P}funded_consistency_rule",
           "S2 S4 A5", _policy_funded_lucid),
        _L("A3", POLICY, "session rule q (when to stop)", SEARCHED, DECL,
           f"{P}eval_consistency_rule {P}eval_profit_target {P}funded_consistency_rule", "T3 A4 A5",
           lambda: _session_rule(f)),
        _L("A4", POLICY, "checkout configuration (price path)", SEARCHED, RULE,
           f"{P}eval_fee {P}eval_consistency_rule {P}eval_min_days {P}funded_type", "A1 A3", _price_path_lucid),
        _L("A5", POLICY, "payout path", FIXED, RULE,
           f"{P}payout_frequency_gate {P}payout_cap {P}payout_min {P}payout_split", "A2 A3 A18 A19",
           lambda: _payout_path(f)),
        _L("A6", POLICY, "funded seats", SEARCHED, RULE, f"{P}max_accounts {P}eval_count_limit", "A7 A8 A15",
           lambda: _seats(f)),
        _L("A7", POLICY, "evaluations at once", SEARCHED, DECL, f"{P}eval_count_limit {P}max_accounts", "A6 A8 A11",
           lambda: _evals(f)),
        _L("A8", POLICY, "banking while a pass waits", SEARCHED, DECL, f"{P}max_accounts {P}eval_count_limit",
           "A6 A7 A9", _banking_lucid),
        _L("A9", POLICY, "the hold's expiry (two readings)", FIXED, DECL, f"{P}hold_expiry_days", "A8 A10",
           _owed("A9")),
        _L("A10", POLICY, "evaluation-purchase rule", SEARCHED, DECL, f"{P}eval_time_limit", "A9 A11",
           lambda: _purchase_rule(f)),
        _L("A11", POLICY, "evaluation-purchase budget", SEARCHED, DECL, f"{P}account_start_rate_limit", "A7 A10",
           _owed("A11")),
        _L("A12", POLICY, "Back2Funded reactivations", DROPPED, DECL, "", "A4 A6 A18"),
        _L("A13", POLICY, "resets", DROPPED, DECL, f"{P}eval_reset_fee", "A4"),
        _L("A14", POLICY, "daily-loss-limit election", DROPPED, DECL, f"{P}eval_daily_loss_limit", "S3 S4"),
        _L("A15", POLICY, "routing (which account takes a trade)", SEARCHED, TODECL, "", "A6 A7 A16 T8"),
        _L("A16", POLICY, "signal mix: shares and account assignment", SEARCHED, TODECL, "", "T1 A15"),
        _L("A17", POLICY, "state rule (sizing by distance to floor or target)", SEARCHED, TODECL, "", "S3 S4 A1 A2"),
        _L("A18", POLICY, "first payout request (RD-02 L1)", SEARCHED, DECL,
           f"{P}payout_frequency_gate {P}payout_min {P}eval_drawdown_lock {P}payout_balance_consequence", "A5 A19",
           _payout_first_lucid),
        _L("A19", POLICY, "request amount (RD-02 L2)", SEARCHED, DECL,
           f"{P}payout_request_amount_choice {P}payout_cap {P}payout_min", "A5 A18", _owed("A19")),
        _L("A20", POLICY, "request cadence", FIXED, DECL, f"{P}payout_frequency_gate", "A18",
           lambda: _payout_cadence(f)),
        _L("A21", POLICY, "payout method", FIXED, DECL, f"{P}payout_fee {P}payout_processing_days", "",
           _owed("A21")),
    )}


@lru_cache(maxsize=None)
def levers(firm: str) -> dict[str, Lever]:
    """The firm's lever rows, in the table's order (Topstep's are `lever_space.LEVERS`, unchanged)."""
    if firm == "topstep":
        return LS.LEVERS
    if firm == "mffu":
        return _mffu_levers()
    if firm == "lucid":
        return _lucid_levers()
    raise ValueError(f"unknown firm {firm!r}")


#: the rules every design of the firm needs before the engine can run it, though no lever's range rests on them
PREREQUISITES: dict[str, tuple[tuple[str, str], ...]] = {
    "topstep": (),
    "mffu": (
        ("mffu.trading_hours", "the firm's trading day: its reopen, any flat-by time and last-entry time (T2, T3)"),
        ("mffu.eval_consistency_base", "the evaluation's consistency base (net profit, or winning days): whether a "
                                       "flip or a losing day passes (RD-05 U-15)"),
        (MFFU_P + "funded_news", "whether Tier 1 news trading is allowed on the Rapid EOD sim funded account"),
        ("mffu.news_all_releases_protocol", "the protocol for every other release"),
        (MFFU_P + "commissions", "the per-trade cost on this plan (the firm-wide table names no plan)"),
        (MFFU_P + "eval_fee", "the evaluation's price: every journey's cost (A4)"),
    ),
    "lucid": (
        (LUCID_P + "trading_hours", "the firm's trading day: its reopen, any flat-by time and last-entry time (T2, T3)"),
        (LUCID_P + "funded_monthly_fee", "a recurring funded-account fee, if any: every journey's cost (Stage 2 "
                                         "charges none and labels every Lucid result an upper bound)"),
    ),
}


def prerequisites(firm: str) -> dict[str, str]:
    """Each prerequisite rule with its status ('verified' or the reason it is not)."""
    out = {}
    for key, _what in PREREQUISITES[firm]:
        try:
            rule(firm, key)
            out[key] = "verified"
        except UnverifiedTerm as e:
            out[key] = f"{type(e).__name__}: {rule_status(firm, key)[1]}"
    return out


def ready(firm: str) -> None:
    """Refuse (`NotVerified`) a firm whose engine prerequisites are not all verified."""
    bad = {k: v for k, v in prerequisites(firm).items() if v != "verified"}
    if bad:
        raise NotVerified(f"{firm}: the engine cannot run a design until these rules are verified: {sorted(bad)}")


# ------------------------------------------------------------------------------------------------ the loader


def bounds(firm: str, lever_id: str) -> Range:
    """The firm's lever range, or a refusal: dropped (`DroppedLever`), 'to compute' (`NotComputed`; no firm but Topstep
    has a search-year reading yet), 'to declare' (`NotDeclared`), or a key not verified (`NotVerified`). Every key
    the lever leans on is read before anything is computed, and the loaded range's `read` holds each by key."""
    if firm == "topstep":
        return LS.bounds(lever_id)
    lv = levers(firm)[lever_id]
    table = TABLES[firm]
    if lv.cls == DROPPED:
        raise DroppedLever(f"{firm} {lever_id} ({lv.name}) is dropped: no range ({table})")
    if lv.source == COMPUTE:
        raise NotComputed(f"{firm} {lever_id} ({lv.name}): its range is a search-year reading of this firm's own, to "
                          f"compute -- refused until it exists (CHARTER 3.3 (a); E-208)")
    if lv.source == TODECL:
        raise NotDeclared(f"{firm} {lever_id} ({lv.name}): its range is to declare -- refused ({table})")
    read = {k: rule(firm, k) for k in lv.keys}          # refuses any key not verified, before anything is computed
    if lv.resolver is None:
        raise LeverRefused(f"{firm} {lever_id} has no resolver")
    r = lv.resolver()
    return dataclasses.replace(r, read={**read, **r.read})


def load(firm: str) -> dict[str, Range]:
    """Every lever of the firm whose range loads at this commit (Topstep's: `lever_space.space()`)."""
    if firm == "topstep":
        return LS.space()
    out = {}
    for i in levers(firm):
        try:
            out[i] = bounds(firm, i)
        except (LeverRefused, UnverifiedTerm):
            pass
    return out


space = load


def refusals(firm: str) -> dict[str, str]:
    """Every lever of the firm refused at this commit, with its refusal's class."""
    if firm == "topstep":
        return LS.refusals()
    out = {}
    for i in levers(firm):
        try:
            bounds(firm, i)
        except (LeverRefused, UnverifiedTerm) as e:
            out[i] = type(e).__name__
    return out


def unverified_keys(firm: str) -> dict[str, list[str]]:
    """The work list: each key not verified, with the levers it refuses (and 'engine' for a prerequisite)."""
    out: dict[str, list[str]] = {}
    for i, lv in levers(firm).items():
        if lv.cls == DROPPED or lv.source in (COMPUTE, TODECL):
            continue
        for k in lv.keys:
            try:
                rule(firm, k)
            except UnverifiedTerm:
                out.setdefault(k, []).append(i)
    for k, v in prerequisites(firm).items():
        if v != "verified":
            out.setdefault(k, []).append("engine")
    return out


def _outcome(firm: str, lever_id: str) -> tuple[str, Any]:
    try:
        r = bounds(firm, lever_id)
    except UnverifiedTerm as e:
        return "UnverifiedTerm", type(e).__name__
    except LeverRefused as e:
        return type(e).__name__, None
    return "loaded", (r.kind, r.values, r.lo, r.hi, r.step)


def vs_topstep(firm: str, lever_id: str) -> str:
    """`refused`: refused for want of a verified rule; `identical`: the same outcome as Topstep's (the same refusal,
    or the same range) without any rule of the firm's (a dropped lever is identical when Topstep's is dropped too);
    `differs` otherwise -- the firm's own rules enter, the outcome is not Topstep's, or the lever is **to declare for
    this firm** (T2b, A15, A16, A17: a per-firm declaration, never Topstep's values carried over, whatever Topstep's
    row declares; refused `NotDeclared` until it exists)."""
    mine, ts = _outcome(firm, lever_id), _outcome("topstep", lever_id)
    if mine[0] == "UnverifiedTerm":
        return REFUSED
    lv = levers(firm)[lever_id]
    if lv.source == TODECL:                 # to declare for this firm: never Topstep's carried over (the lead's ruling)
        return DIFFERS
    if mine[0] == ts[0] == "DroppedLever":
        return IDENTICAL
    if mine == ts and not lv.keys:
        return IDENTICAL
    return DIFFERS


def compare(firm: str) -> dict[str, str]:
    return {i: vs_topstep(firm, i) for i in levers(firm)}


def counts(firm: str) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {layer: {c: 0 for c in LS.CLASSES} for layer in LS.LAYERS}
    for lv in levers(firm).values():
        out[lv.layer][lv.cls] += 1
    return out


# ------------------------------------------------------------------------------------------------ designs and sampling


def _inside(r: Range, v: Any) -> bool:
    if r.kind in ("choices", "fixed"):
        return v in (r.values or ())
    if v is None or not (r.lo - 1e-9 <= float(v) <= r.hi + 1e-9):
        return False
    if r.step:
        k = (float(v) - r.lo) / r.step
        return abs(k - round(k)) < 1e-9
    return True


def check_design(firm: str, settings: dict[str, Any], sp: dict[str, Range] | None = None) -> None:
    """Refuse a design: conduct tier 1 and the hard limits (`conduct_check`, every firm); a setting of a lever that is
    refused at this commit, or outside its loaded range; and the combinations no verified rule settles (Topstep's
    `lever_space.check_design`; at Lucid, funded seats and evaluations beyond the household's total accounts)."""
    conduct_check(settings)
    sp = load(firm) if sp is None else sp
    lv = levers(firm)
    for i, v in settings.items():
        if i not in lv or (i == "T4" and v is None):
            continue
        if i not in sp:
            raise LeverRefused(f"{firm} {i} is set ({v!r}) but refused at this commit")
        if not _inside(sp[i], v):
            raise LeverRefused(f"{firm} {i} = {v!r} lies outside its loaded range")
    if firm == "topstep":
        LS.check_design(settings)
        return
    lat, src = settings.get("T4"), settings.get("T1")
    if src is not None and lat is not None and lat not in LS.latency_cells(src):
        raise LeverRefused(f"latency {lat!r} is not a cell of source {src!r}")
    if firm == "lucid" and settings.get("A6") is not None and settings.get("A7") is not None:
        total = _lucid_accounts()["total"]
        if float(settings["A6"]) + float(settings["A7"]) > total:
            raise LeverRefused(f"lucid: {settings['A6']} funded and {settings['A7']} evaluations exceed the "
                               f"household's {total} accounts in total (`{LUCID_P}max_accounts`)")


def _draw(r: Range, rng: np.random.Generator) -> Any:
    if r.kind in ("choices", "fixed"):
        return r.values[int(rng.integers(len(r.values)))]
    if r.step:
        n = int(math.floor((r.hi - r.lo) / r.step + 1e-9))
        return r.lo + r.step * int(rng.integers(n + 1))
    return float(rng.uniform(r.lo, r.hi))


def sample(firm: str, *, seed: int, n: int = 1) -> list[dict[str, Any]]:
    """`n` designs drawn uniformly from the firm's loaded space (searched levers drawn, fixed levers at their value;
    T4 one cell for a latency-free source), each passed through `check_design`. A conduct tier-1 or hard-limit refusal
    is raised, never redrawn (the space must not contain one); a combination refusal is redrawn, at most
    `sample.max_redraws` times. The seed is the caller's, fixed in its declaration (CLAUDE.md). Topstep's A15 and A17
    are **held until wired** (`lever_space.HELD_UNTIL_WIRED`, the red team's m4): set at their bases, never drawn."""
    rng = np.random.default_rng(int(seed))
    sp = load(firm)
    lv = levers(firm)
    held = {i: sp[i].values[0] for i in LS.HELD_UNTIL_WIRED if firm == "topstep" and i in sp}  # m4: the base
    use = [i for i in lv if i in sp and lv[i].cls in (SEARCHED, FIXED) and i not in held]
    out = []
    for _ in range(int(n)):
        for _attempt in range(int(fdeclared("sample.max_redraws"))):
            d = {i: _draw(sp[i], rng) for i in use if i != "T4"}
            d.update(held)
            if "T4" in sp:
                cells = LS.latency_cells(d["T1"]) if "T1" in d else tuple(sp["T4"].values)
                d["T4"] = cells[int(rng.integers(len(cells)))]
            try:
                check_design(firm, d, sp)
            except (TierOneRefused, HardLimitRefused):
                raise
            except (LeverRefused, UnverifiedTerm):           # a combination no verified rule settles: redrawn
                continue
            out.append(d)
            break
        else:
            raise LeverRefused(f"{firm}: no admissible design in {fdeclared('sample.max_redraws')} draws")
    return out


__all__ = ["TASK", "FIRMS", "TABLES", "PLANS", "MFFU_P", "LUCID_P", "LUCID_CONFIGS", "IDENTICAL", "DIFFERS", "REFUSED",
           "NotVerified", "TierOneRefused", "HardLimitRefused", "FIRM_DECLARED", "TIER1_MARKERS", "TIER1_VALUES",
           "conduct_check", "rule", "note", "rule_status", "mffu_trading_day", "mffu_session_windows", "mffu_session_window_range", "stop_caps", "levers", "PREREQUISITES", "prerequisites",
           "ready", "bounds", "load", "space", "refusals", "unverified_keys", "vs_topstep", "compare", "counts",
           "check_design", "sample"]
