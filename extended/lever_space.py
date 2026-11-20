"""Q-151: the lever space of the Topstep $50K design search (`docs/plans/LEVER_TABLE_topstep50k.md`; the restart plan
4.3 to 4.4b; the amendments' CHARTER 3.3 (a) and (g), 3.5; E-208) -- every lever's layer, range, step, source, unit,
dependencies and class, and a loader that reads the rule-derived bounds from the record.

**Sources (3.3 (a)).** A range comes from (1) a verified rule, read by its key; (2) contract arithmetic on verified rules
and the engine's contract constants (tick values, the registered stand-aside floor), computed here; (3) a declared
parameter of this table (`DECLARED`, each citing its row or declaration -- never a rule value); or it is (4) **a
search-year reading, to compute** (2020-01-02 to 2023-12-29, E-208), or (5) **to declare** by a later item. The loader
refuses (4) (`NotComputed`) and (5) (`NotDeclared`) whatever their keys, refuses every lever leaning on a key whose
status is not `verified` (`firm_terms.UnverifiedTerm`: this repository's record first, where it holds the key, else
Stage 2's vendored ledger), and has no range for a dropped lever (`DroppedLever`).

**No rule value is typed here**: every number of a rule-derived bound is read from its key (`rule`) or from the RD-05
build's term loaders (`extended.modes_terms`, `extended.modes_rules`); `tests/test_lever_space.py` scans this file for
the read values outside `DECLARED`. It reads rules and configuration only -- never a bar or a trade -- and one result
file: **S1's search-year reading** (Q-171, `extended.s1_range`), `results/s1_range.csv` with its sidecar manifest.
While that file (or its manifest) does not exist S1 stays `NotComputed`, as before; once it does, it is loaded only
after its manifest is checked (`s1_range.load_range`: its sha256, a clean run of `scripts/s1_range.py` on a clean tree,
the whole search years, both identities held, the caps equal to `stop_caps()` now, the declared share), and any defect
refuses loudly (`LeverRefused`), never as `NotComputed`. T7 has no reading and stays refused.

**The four rows once 'to declare'** (E-NNN pending) load as declared: T2b, the NY AM / NY PM boundary at noon New
York (`ny_boundary`, checked on every search-year weekday); A15, the router's rotations; A16, `by_component`'s pools
dealt in turn (`deal_pools`), the shares derived from the components; A17, the state rule on the mode's dollar risk
(`state_risk`). No lever is 'to declare' now; the kind stays for a later row. A9 and A19 stay refused by key.
T2b's one value is enforced where NY is split: `session_windows()` splits at it, and `check_ny_boundary` (also in
`check_design`) refuses any other boundary a caller passes (the red team's L-M2).
"""
from __future__ import annotations

import functools
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from extended import ROOT
from extended import firm_terms as FT
from extended import modes_rules as MR
from extended import modes_terms as M
from extended.firm_terms import UnverifiedTerm, parse

TABLE = "docs/plans/LEVER_TABLE_topstep50k.md"
TASK = "Q-151"
CONFIGS = ("TS-S", "TS-N")                  # RD-05 2.1: Topstep $50K, the two price paths
TRIGGER, SHAPE, POLICY = "trigger", "trade shape", "account policy"
LAYERS = (TRIGGER, SHAPE, POLICY)
SEARCHED, FIXED, DROPPED = "searched", "declared", "dropped"
CLASSES = (SEARCHED, FIXED, DROPPED)
RULE, ARITH, DECL, COMPUTE, TODECL = "rule", "arithmetic", "declared", "to compute", "to declare"
SOURCES = (RULE, ARITH, DECL, COMPUTE, TODECL)
MINUTES_PER_DAY = 24 * 60                   # clock arithmetic, never a rule value
PM = 12 * 60


class LeverRefused(RuntimeError):
    """A lever whose range may not be loaded at this commit."""


class NotComputed(LeverRefused):
    """The range's source is 'a search-year reading, to compute': no range until that reading exists (3.3 (a))."""


class NotDeclared(LeverRefused):
    """The range's source is 'to declare': a later item fixes it; nothing is chosen here."""


class DroppedLever(LeverRefused):
    """A dropped lever has no range: it is held at its stated setting, or it does not exist."""


# ------------------------------------------------------------------------------------------------ the declared table


@dataclass(frozen=True)
class Declared:
    value: Any
    cite: str


#: the table's own parameters, each citing its source -- never a rule value (a rule value is read by its key)
DECLARED: dict[str, Declared] = {
    "sources": Declared(("coin", "p14", "p16", "rl3"),
                        "E-208: the naive coin; P-14's breakout timing and P-16's marks, coin-sided; RL3's NY AM "
                        "tickets -- the trigger library's sources (Wave 3.3)"),
    "latency": Declared((5, 3, 2), "E-202 (2)(c); CHARTER 3.3 (g) as amended: five the reference, three and two "
                        "counted variants"),
    "latency.reference": Declared(5, "E-202 (2)(c): the five-minute cell, reported beside every finalist"),
    "latency_free": Declared(("p16", "rl3"), "E-203 B-2 (P-16 scheduled); E-204 (RL3: alert 08:30, live 09:00)"),
    "entry_types": Declared(("market", "limit"), "E-202 (2)(d); F-04 6.1 R-4; the triage: a coin-sided limit is "
                            "exact (F-04 5.3)"),
    "limit_window_min": Declared(30, "F-04 6.1: a limit works from its live time to 30 minutes later, a news "
                                 "window's start, or the walk's last entry bar, the earliest"),
    "side_rule": Declared(("coin",), "CHARTER 3.2 and 3.5 as amended: the coin side; the traded side pending O-4"),
    "windows_ct": Declared((("asia", "18:00"), ("london", "02:00"), ("ny", "08:30")),
                           "Stage 2 resolved_coin.WINDOWS (D-525 (3)): asia from 18:00, london from 02:00, us from "
                           "08:30 CT; the hour before 18:00 is 'evening' here (an interpretation, Q-151)"),
    "sessions": Declared(("evening", "asia", "london", "ny_am", "ny_pm"),
                         "the restart plan 4.4b (Asia, London, NY AM, NY PM) and the evening hour the firm allows"),
    "mark_step_min": Declared(5, "Stage 2 D-525 (2), resolved_coin.MARK_STEP: an offer mark every five minutes"),
    "mixes": Declared(("MNQ", "mixed"), "F-04 6.1: micros only, or as many minis as fit and the rest micros "
                      "(D-324); minis only dropped"),
    "policies": Declared(("steady", "flip"), "RD-05 2.6; E-196 (the operator's flip days)"),
    "session_rules": Declared(("one", "all", "cap"), "F-04 6.1 `q`: the operator's 'when to stop'"),
    "price_paths": Declared(("standard", "naf"), "RD-03 2.4 (L-N); RD-05 2.1 (TS-S, TS-N)"),
    "payout_paths": Declared(("standard", "consistency"), "RD-05 2.2 (TS/std, TS/con); chosen at activation"),
    "evals_max": Declared(7, "RD-03 2.2 (L-I): C = 5 (Stage 2 D-34's bound) or 7, two above it; no rule caps "
                          "evaluations (`combine_count_limit`)"),
    "banking": Declared(("on", "off"), "RD-03 2.2: evaluations bought while a pass waits, or not (Stage 2 D-08)"),
    "purchase_rules": Declared(("replace", "house_stop", "house_zero"),
                               "RD-03 2.3 (L-H): the base's replacement, and the two house-money rules (gaming P, "
                               "E-134 (2))"),
    "purchase_budget_max": Declared(20, "Stage 2 D-501: at most 20 evaluation purchases a month; no rule limits "
                                    "starts (`account_start_rate_limit`)"),
    "payout_first": Declared(("elig", "lock"), "RD-02 6.1 L1"),
    "payout_cadence": Declared(("every_eligible_close",), "RD-02 6.1: after the first payout, every eligible close"),
    "payout_method": Declared(("aeropay",), "RD-02 7.1; Stage 2 D-24: Aeropay, the US baseline"),
    "payout_amounts": Declared(("max", "half"), "RD-02 6.1 L2: the maximum, or half of it (`payout_frac` 0.5)"),
    # -- the four rows that were 'to declare' (T2b, A15, A16, A17; E-NNN pending), each fixed before any outcome
    "ny_split_local": Declared(("America/New_York", 12, 0),
                               "T2b: noon on the NY session's own clock. Its open is 09:30 New York (E-231 (3), "
                               "`day_calendar.LOCAL_ANCHORS`), so NY AM runs from the cash open to New York's noon, "
                               "where the conventional lunch lull begins, and NY PM holds the lull, the afternoon and "
                               "the close to the firm's flat. Session structure only; nothing read. The same boundary, "
                               "11:00 CT, starts Stage 2's `late_morning` window (`config/session_setups.yaml`, D-244, "
                               "D-245: fixed before any of its data was read)"),
    "rotations": Declared(("longest_waiting", "round_robin", "by_component"),
                          "A15: the mix router's rotations (Q-169, `router.ROTATIONS`), the base first (Stage 2 "
                          "D-429's longest-waiting account); E-221 O-4: accounts alternate, the rotation a lever, "
                          "one account per trade, never opposite positions at once"),
    "assignment": Declared(("dealt",),
                           "A16: `by_component`'s pools dealt in turn (`deal_pools`); a source's share of the mix is "
                           "its components' (T1 per component, CHARTER 3.4, 3.5), never a separate parameter"),
    "state_rules": Declared(("none", "floor", "target", "floor_target"),
                            "A17: the triage (Q-46's buffer idea enters as a state rule) and the restart plan's lever "
                            "'any state rule (sizing by distance to drawdown or target)': the mode's r, cut by the "
                            "room's share of the start room, by the goal still to make, or by both (`state_risk`)"),
}


def declared(name: str) -> Any:
    return DECLARED[name].value


# ------------------------------------------------------------------------------------------------ the rule reader


def rule(key: str) -> Any:
    """A verified rule's value: this repository's record where it holds the key (its re-read supersedes; any status
    but `verified` is refused), else Stage 2's vendored ledger (refused unless `verified`)."""
    try:
        FT.record_entry(key)
    except KeyError:
        return FT.stage2_value(key)
    return FT.record_value(key)


def rule_status(key: str) -> tuple[str, str]:
    """(ledger, status) of a key, for the table's audit: 'record' or 'stage2'."""
    try:
        return "record", str(FT.record_entry(key).get("status"))
    except KeyError:
        e = FT._stage2().get(key)
        if e is None:
            raise KeyError(f"no rule {key!r} in either ledger") from None
        return "stage2", str(e.get("status"))


def _clock(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def trading_day() -> dict[str, int]:
    """The firm's trading day from `trading_hours` (8284206): the reopen and the flat, wall-clock minutes CT; the last
    new entry from the verified note's 'Avoid opening new positions after h:mm PM CT'; and the day's length."""
    v = rule("trading_hours")
    reopen = _clock(parse(r"reopen_(\d\d:\d\d)_ct", v, "trading_hours").group(1))
    flat = _clock(parse(r"flat_by_(\d\d:\d\d)_ct", v, "trading_hours").group(1))
    m = parse(r"Avoid opening new positions after (?P<clock>\d{1,2}:\d\d) PM CT", M.s2_note("trading_hours"),
              "trading_hours note (8284206)")
    day = MINUTES_PER_DAY
    last_entry = _clock(m.group("clock")) + PM                # a 12-hour clock's PM, as the page writes it
    length = (flat - reopen) % day
    return {"reopen": reopen, "flat": flat, "last_entry": last_entry, "length": length,
            "last_entry_offset": (last_entry - reopen) % day}


def session_windows() -> dict[str, tuple[int, int | None]]:
    """The sessions as [start, end) in minutes after the reopen; `ny` is split at T2b's declared boundary
    (`bounds("T2b")`, the one value it takes; the red team's L-M2), which must lie strictly inside it. Every boundary
    must fall inside the firm's day."""
    td = trading_day()
    starts = [(name, (_clock(t) - td["reopen"]) % MINUTES_PER_DAY) for name, t in declared("windows_ct")]
    for name, off in starts:
        if not 0 < off < td["length"]:
            raise LeverRefused(f"session boundary {name!r} lies outside the firm's trading day (trading_hours)")
    edges = [0] + [off for _, off in starts] + [td["length"]]
    if edges != sorted(edges):
        raise LeverRefused("the declared session boundaries are out of order against the firm's day")
    names = ("evening", "asia", "london", "ny")
    out: dict[str, tuple[int, int | None]] = dict(zip(names, zip(edges, edges[1:])))
    ny_start, ny_end = out.pop("ny")
    b = int(bounds("T2b").values[0])
    if not ny_start < b < ny_end:
        raise LeverRefused(f"T2b's boundary {b} is not inside ny [{ny_start}, {ny_end})")
    out["ny_am"], out["ny_pm"] = (ny_start, b), (b, ny_end)
    return out


# ------------------------------------------------------------------------------------------------ ranges


@dataclass(frozen=True)
class Range:
    """A loaded range: `choices` (values), `interval` (lo, hi, step; step None where it is set by another lever), or
    `fixed` (one value). `read` holds every rule value it was computed from, by key."""

    lever: str
    kind: str
    values: tuple[Any, ...] | None = None
    lo: float | None = None
    hi: float | None = None
    step: float | None = None
    unit: str = ""
    read: dict[str, Any] = field(default_factory=dict)
    detail: dict[str, Any] = field(default_factory=dict)


def _read(*keys: str) -> dict[str, Any]:
    return {k: rule(k) for k in keys}


def stop_caps() -> dict[str, Any]:
    """S1's caps, contract arithmetic (before costs): the narrowest stop is the registered rule's stand-aside floor
    (Stage 2 D-271 (3), D-272, read from its config), and the widest is the stop at which one micro's stop-out fills the
    larger start room (`combine_mll`, `xfa_mll_start`) at the micro's tick value."""
    sa = M.registered_stand_aside()
    floor_ticks = max(int(sa["combine"][1]), int(sa["funded"][1]))
    tv = M.tick_values()["MNQ"]
    room = max(float(rule("combine_mll")), -float(rule("xfa_mll_start")))
    cap_ticks = int(math.floor(room / tv + 1e-9))
    if cap_ticks <= floor_ticks:
        raise LeverRefused("the stop's cap is not above its floor")
    return {"floor_ticks": floor_ticks, "cap_ticks": cap_ticks, "tick_value_mnq": tv, "room": room,
            "source": sa["source"]}


#: S1's search-year reading (Q-171): the result file the lever space loads S1's range from, once it exists
S1_RESULT = "results/s1_range.csv"
S1_PATH = ROOT / S1_RESULT


def _s1_computed() -> bool:
    """Whether S1's reading exists: its file and its sidecar manifest (checked, not read, here)."""
    p = Path(S1_PATH)
    return p.is_file() and Path(str(p) + ".manifest.json").is_file()


def _s1_reading() -> tuple[dict[str, Any], dict[str, Any]]:
    from extended import s1_range as S1R                 # light; imported only once a reading exists

    caps = stop_caps()
    try:
        got = S1R.load_range(S1_PATH, caps=caps)
    except S1R.NotRead as exc:
        raise NotComputed(f"S1 (stop width): {exc}") from None
    except S1R.RangeRefused as exc:
        raise LeverRefused(f"S1 (stop width): {exc}") from None
    missing = [s for s in declared("sessions") if s not in S1R.LEVER_SESSIONS]
    if missing:
        raise LeverRefused(f"S1 (stop width): no reading maps the session(s) {missing}")
    by = {s: got["by_session"][S1R.LEVER_SESSIONS[s]] for s in declared("sessions")}
    return got, {"by_session": by, "share": got["share"], "n_days": got["n_days"], "result": S1_RESULT,
                 "sha256": got["sha256"], "git_commit": got["git_commit"], "caps": caps,
                 "unit": "k x the session's trailing range (ny: trail20_range_pts; an overnight session its own)"}


def _stop_width() -> Range:
    _, det = _s1_reading()
    by = det["by_session"]
    return Range("S1", "interval", lo=min(v[0] for v in by.values()), hi=max(v[1] for v in by.values()), step=None,
                 unit="multiple k of the trailing range (per session in detail['by_session']); continuous",
                 read=_read("combine_mll", "xfa_mll_start"), detail=det)


def stop_width(session: str) -> Range:
    """S1's range for one T2 session (`ny_am` and `ny_pm` take `ny`'s), after `bounds('S1')`'s checks."""
    if session not in declared("sessions"):
        raise ValueError(f"unknown session {session!r}")
    whole = bounds("S1")
    lo, hi = whole.detail["by_session"][session]
    return Range("S1", "interval", lo=lo, hi=hi, step=None, unit=f"multiple k of {session}'s trailing range",
                 read=whole.read, detail={**whole.detail, "session": session})


def _sources() -> Range:
    return Range("T1", "choices", values=tuple(declared("sources")), unit="trigger source")


def _session() -> Range:
    td = trading_day()
    return Range("T2", "choices", values=tuple(declared("sessions")), unit="session of the firm's day",
                 read={"trading_hours": rule("trading_hours")},
                 detail={"windows": session_windows(), "day": td})


def _entry_window() -> Range:
    td = trading_day()
    return Range("T3", "interval", lo=0.0, hi=float(td["last_entry_offset"]), step=float(declared("mark_step_min")),
                 unit="minutes after the reopen (an offer mark's time inside its session)",
                 read={"trading_hours": rule("trading_hours")}, detail={"day": td})


def _latency() -> Range:
    vals = tuple(declared("latency"))
    if vals[0] != declared("latency.reference"):
        raise LeverRefused("the reference latency must come first")
    return Range("T4", "choices", values=vals, unit="clock minutes from alert to order",
                 detail={"reference": declared("latency.reference"), "latency_free": declared("latency_free")})


def _entry_type() -> Range:
    return Range("T5", "choices", values=tuple(declared("entry_types")), unit="order type")


def _limit_window() -> Range:
    return Range("T6", "fixed", values=(declared("limit_window_min"),), unit="minutes a limit works")


def _side() -> Range:
    return Range("T8", "fixed", values=tuple(declared("side_rule")), unit="side rule")


def _ratio() -> Range:
    g = M.grid_w()
    return Range("S2", "interval", lo=min(g), hi=max(g), step=None, unit="target / stop (target floor(w s) ticks)",
                 detail={"rd05_grid": g})


def _risk(kind: str) -> Range:
    caps = stop_caps()
    lo = caps["floor_ticks"] * caps["tick_value_mnq"]
    if kind == M.EVAL:
        key, hi, lid = "combine_mll", float(rule("combine_mll")), "S3"
    else:
        key, hi, lid = "xfa_mll_start", -float(rule("xfa_mll_start")), "S4"
    return Range(lid, "interval", lo=lo, hi=hi, step=None,
                 unit="dollars at the stop (share of the start room beside); whole micros at the trade's stop",
                 read={key: rule(key)}, detail={"lo_share": lo / hi, "hi_share": 1.0, "caps": caps})


def _mix() -> Range:
    return Range("S5", "choices", values=tuple(declared("mixes")), unit="instrument mix",
                 read=_read("combine_position_size_limit", "funded_scaling_plan"),
                 detail={"micros_per_mini": M.micros_per_mini()})


def _policy_eval() -> Range:
    t = M.eval_terms("TS-S")
    k = MR.k_eval(t)
    flips = {w: MR.r_flip(M.EVAL, t, w) for w in M.grid_w()}
    return Range("A1", "choices", values=tuple(declared("policies")), unit="evaluation sizing policy",
                 read=_read("combine_profit_target", "combine_consistency_max_day_frac", "combine_mll"),
                 detail={"k_E": k, "r_flip_by_w": flips})


def _policy_funded() -> Range:
    det = {}
    for mode in ("TS/std", "TS/con"):
        f = M.funded_terms(mode)
        det[mode] = {"k_F": MR.k_funded(f)["k_F"], "b_star": MR.b_star(f)["b_star"],
                     "r_flip_by_w": {w: MR.r_flip(M.FUNDED, f, w) for w in M.grid_w()}}
    return Range("A2", "choices", values=tuple(declared("policies")), unit="funded sizing policy",
                 read=_read("xfa_std_winning_days", "xfa_cons_min_days", "xfa_cons_max_day_frac", "xfa_std_cap",
                            "xfa_cons_cap", "payout_max_frac_of_balance", "xfa_mll_start"), detail=det)


def _session_rule() -> Range:
    return Range("A3", "choices", values=tuple(declared("session_rules")), unit="trades a session",
                 read=_read("combine_consistency_max_day_frac", "xfa_cons_max_day_frac", "combine_profit_target"))


def _price_path() -> Range:
    r = _read("subscription_fee", "activation_fee", "subscription_fee_naf_50k", "activation_fee_naf_50k")
    return Range("A4", "choices", values=tuple(declared("price_paths")), unit="evaluation price path", read=r,
                 detail={"standard": (r["subscription_fee"], r["activation_fee"]),
                         "naf": (r["subscription_fee_naf_50k"], r["activation_fee_naf_50k"])})


def _payout_path() -> Range:
    r = _read("xfa_payout_path_choice", "xfa_std_cap", "xfa_cons_cap", "xfa_std_winning_days",
              "xfa_std_winning_day_min", "xfa_cons_min_days", "xfa_cons_max_day_frac")
    parse(r"chosen_at_activation", r["xfa_payout_path_choice"], "xfa_payout_path_choice")
    return Range("A5", "choices", values=tuple(declared("payout_paths")), unit="funded payout path", read=r)


def _seats() -> Range:
    n = int(rule("max_active_funded_accounts"))
    return Range("A6", "interval", lo=1.0, hi=float(n), step=1.0, unit="funded accounts at once",
                 read={"max_active_funded_accounts": rule("max_active_funded_accounts")})


def _evals() -> Range:
    v = rule("combine_count_limit")
    parse(r"^unlimited$", v, "combine_count_limit")         # a stated cap would bound C instead of the declaration
    return Range("A7", "interval", lo=1.0, hi=float(declared("evals_max")), step=1.0,
                 unit="evaluations running at once", read={"combine_count_limit": v})


def _banking() -> Range:
    v = rule("hold_queue_behaviour")
    parse(r"hold_until_slot_frees", v, "hold_queue_behaviour")
    return Range("A8", "choices", values=tuple(declared("banking")), unit="banking rule",
                 read={"hold_queue_behaviour": v})


def _purchase_rule() -> Range:
    return Range("A10", "choices", values=tuple(declared("purchase_rules")), unit="evaluation-purchase rule",
                 read=_read("combine_cancellation"))


def _purchase_budget() -> Range:
    v = rule("account_start_rate_limit")
    parse(r"^none_stated$", v, "account_start_rate_limit")  # a stated limit would bound the budget instead
    return Range("A11", "interval", lo=1.0, hi=float(declared("purchase_budget_max")), step=1.0,
                 unit="evaluation purchases a month", read={"account_start_rate_limit": v},
                 detail={"month_sessions": M.declared("month")})


def _back2funded() -> Range:
    r = _read("back2funded_max_reactivations", "back2funded_reactivation_fee_50k", "back2funded_window_days",
              "back2funded_eligibility", "back2funded_seat_count")
    return Range("A12", "interval", lo=0.0, hi=float(r["back2funded_max_reactivations"]), step=1.0,
                 unit="reactivations per funded account", read=r,
                 detail={"window_sessions": M.calendar_to_sessions(float(r["back2funded_window_days"]), wait=False)})


def _payout_first() -> Range:
    return Range("A18", "choices", values=tuple(declared("payout_first")), unit="first-request rule",
                 read=_read("xfa_lock_at", "payout_min", "xfa_std_winning_days", "xfa_std_winning_day_min"))


def _payout_amount() -> Range:
    return Range("A19", "choices", values=tuple(declared("payout_amounts")), unit="request amount",
                 read=_read("payout_max_frac_of_balance", "xfa_std_cap", "payout_min",
                            "payout_request_amount_choice"))


def _payout_cadence() -> Range:
    return Range("A20", "fixed", values=tuple(declared("payout_cadence")), unit="request cadence",
                 read=_read("require_profit_since_payout"))


def _payout_method() -> Range:
    r = _read("payout_lag_days_aeropay", "payout_fee", "payout_lag_days_ach", "payout_fee_ach")
    if not (float(r["payout_lag_days_aeropay"]) <= float(r["payout_lag_days_ach"])
            and float(r["payout_fee"]) <= float(r["payout_fee_ach"])):
        raise LeverRefused("Aeropay no longer dominates ACH on the record: the payout method becomes a lever")
    return Range("A21", "fixed", values=tuple(declared("payout_method")), unit="payout method", read=r)


def _hold_expiry() -> Range:
    return Range("A9", "choices", values=("exp_none", "exp_30"), unit="the hold's expiry, both readings",
                 read=_read("hold_expiry_days"))


# ---------------------------------------------- the four rows once 'to declare' (T2b, A15, A16, A17; E-NNN pending)


def _search_weekdays() -> list[Any]:
    """The weekdays of the search years (`day_calendar.SEARCH_START` to `SEARCH_END`, E-208): calendar dates only."""
    import calendar
    from datetime import timedelta

    from extended import day_calendar as DC

    out, d = [], DC.SEARCH_START
    while d <= DC.SEARCH_END:
        if d.weekday() < calendar.SATURDAY:
            out.append(d)
        d += timedelta(days=1)
    return out


def ny_boundary(day: Any) -> int:
    """T2b's boundary on trading day `day` (a date), in minutes after the reopen of the evening before it: the
    declared local time (`ny_split_local`, noon New York) converted for that date by zoneinfo, as the session anchors
    are (`day_calendar.anchored_starts`)."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    from extended import day_calendar as DC

    td = trading_day()
    if td["reopen"] != DC.REOPEN_MIN:
        raise LeverRefused("the anchored times are minutes after a 17:00 CT reopen; this firm reopens at another time")
    tz, h, m = declared("ny_split_local")
    reopen = datetime(day.year, day.month, day.day, tzinfo=DC.CHICAGO) - timedelta(days=1) \
        + timedelta(minutes=td["reopen"])
    t = datetime(day.year, day.month, day.day, int(h), int(m), tzinfo=ZoneInfo(tz))
    return int((t - reopen) // timedelta(minutes=1))


@functools.cache
def _ny_split_days(local: tuple, reopen: int, last_entry: int) -> tuple[frozenset, frozenset, int, str | None]:
    """T2b's boundary and ny's anchored start on every weekday of the search years, for one declared local time and
    one firm's day (cached by both: calendar arithmetic over a thousand days): (boundaries, starts, days, the first
    refusal or None). `reopen` is in the key so that a changed firm's day is never served a stale answer."""
    from extended import day_calendar as DC

    days = _search_weekdays()
    seen: set[int] = set()
    starts: set[int] = set()
    for d in days:
        b, ny = ny_boundary(d), int(DC.anchored_starts(d)["ny"])
        if not ny < b < last_entry:
            return frozenset(), frozenset(), len(days), f"T2b's boundary {b} is not inside NY [{ny}, {last_entry}] on {d}"
        seen.add(b)
        starts.add(ny)
    return frozenset(seen), frozenset(starts), len(days), None


def _ny_split() -> Range:
    """T2b: the boundary on every weekday of the search years; refused unless it is one value there, strictly inside
    `ny` (after its anchored start, before the last new entry) and on the mark grid."""
    from extended import day_calendar as DC

    td = trading_day()
    step = int(declared("mark_step_min"))
    seen_f, starts, n_days, why = _ny_split_days(tuple(declared("ny_split_local")), int(td["reopen"]),
                                                 int(td["last_entry_offset"]))
    if why:
        raise LeverRefused(why)
    seen = set(seen_f)
    if len(seen) != 1:
        raise LeverRefused(f"T2b's boundary takes {len(seen)} values over the search years, not one")
    b = seen.pop()
    if b % step:
        raise LeverRefused(f"T2b's boundary {b} lies off the {step}-minute mark grid")
    clock = (td["reopen"] + b) % MINUTES_PER_DAY
    return Range("T2b", "fixed", values=(b,), unit="minutes after the reopen: NY AM is [ny's start, b), NY PM [b, "
                 "the flat)", read={"trading_hours": rule("trading_hours")},
                 detail={"local": tuple(declared("ny_split_local")), "ct_clock": f"{clock // 60:02d}:{clock % 60:02d}",
                         "ny_am": (min(starts), b), "ny_pm": (b, td["length"]), "days_checked": n_days,
                         "span": (DC.SEARCH_START.isoformat(), DC.SEARCH_END.isoformat())})


def check_ny_boundary(boundary: Any) -> int:
    """Refuse any NY AM / NY PM boundary but T2b's declared one (the red team's L-M2): a caller splitting NY (the
    sampler's `ny_boundary`) passes its value here. Returns it."""
    b = int(bounds("T2b").values[0])
    if isinstance(boundary, bool) or not isinstance(boundary, (int, float)) or boundary != b:
        raise LeverRefused(f"NY boundary {boundary!r} is not T2b's declared {b} (noon New York)")
    return b


def _routing() -> Range:
    vals = tuple(declared("rotations"))
    return Range("A15", "choices", values=vals, unit="rotation: which of a firm's accounts takes its next trade",
                 detail={"base": vals[0], "pools": "by_component's, A16's `deal_pools`",
                         "guards": ("one account per trade (never copied)", "opposite positions refused, tier 1",
                                    "one position at a time across the firm (D-429)")})


def deal_pools(components: Any, accounts: Any, *, opened: Any = None) -> dict[str, tuple[str, ...]]:
    """A16's assignment: `by_component`'s pools for one day. `components` are the design's components in the order of
    their windows' first slots; `accounts` the firm's accounts that day, **dealt in opening order** (the red team's
    L-m1): with `opened` (account -> its opening index), sorted by (index, account id), whatever order they come in;
    without it, the sequence's own order is declared to be the opening order. With at least as many accounts as
    components, the j-th account goes to component j mod m (a partition; pool sizes differ by at most one); with
    fewer, component i takes account i mod n alone. Reads nothing but the lists."""
    comps, accs = tuple(components), tuple(accounts)
    if not comps or not accs:
        raise LeverRefused("A16 deals at least one account to at least one component")
    if len(set(comps)) != len(comps) or len(set(accs)) != len(accs):
        raise LeverRefused("A16: a component or an account repeats")
    if opened is not None:
        missing = [a for a in accs if a not in opened]
        if missing:
            raise LeverRefused(f"A16: no opening index for {missing}")
        accs = tuple(sorted(accs, key=lambda a: (int(opened[a]), str(a))))
    m, n = len(comps), len(accs)
    if n >= m:
        return {c: tuple(accs[j] for j in range(i, n, m)) for i, c in enumerate(comps)}
    return {c: (accs[i % n],) for i, c in enumerate(comps)}


def _assignment() -> Range:
    return Range("A16", "fixed", values=tuple(declared("assignment")), unit="account assignment of by_component's pools",
                 detail={"shares": "derived: a source's share is its components' (T1 per component); no parameter",
                         "rule": "deal_pools"})


def state_risk(rule_name: str, r: float, *, room: float, start_room: float, to_goal: float, stop_ticks: int,
               target_ticks: int, tick_value: float) -> float:
    """A17: a trade's intended dollar risk under the state rule, before the base's cuts (the room cap D-313, the
    allowance and the headroom D-117, D-212's stand-aside -- `modes_rules.size`, unchanged). `r` is the mode's dollar
    risk (S3 or S4; A1's or A2's r where a flip trade); `room` the balance less the floor in force; `start_room` the
    mode's (`modes_rules.start_room`); `to_goal` what is left to the mode's goal (the evaluation's profit target, the
    funded payout path's b*); one micro's risk is `stop_ticks` x `tick_value`, its win `target_ticks` x `tick_value`.

    * `none` -- r in every state;
    * `floor` -- r x the room's share of the start room, capped at one (sizing by distance to the floor);
    * `target` -- the fewest whole micros whose win reaches the goal, where that is below r (by distance to the goal);
    * `floor_target` -- the smaller of the two.
    Never above r, so never more size into news than the mode's own; never below one micro at the stop where r is not
    (the rule itself never stands an account aside; the base's caps still may)."""
    if rule_name not in declared("state_rules"):
        raise ValueError(f"state rule {rule_name!r} is not one of {declared('state_rules')} (A17)")
    if not (r > 0 and start_room > 0 and stop_ticks > 0 and target_ticks > 0 and tick_value > 0):
        raise ValueError("A17 reads a positive r, start room, stop, target and tick value")
    one = float(stop_ticks) * float(tick_value)
    out = float(r)
    if rule_name in ("floor", "floor_target"):
        out = min(out, float(r) * max(0.0, min(1.0, float(room) / float(start_room))))
    if rule_name in ("target", "floor_target") and to_goal > 0:
        n = math.ceil(float(to_goal) / (float(target_ticks) * float(tick_value)) - 1e-9)
        out = min(out, n * one)
    return max(out, min(one, float(r)))


def _state_rule() -> Range:
    t = M.eval_terms("TS-S")
    det: dict[str, Any] = {"eval": {"goal": float(t.target), "start_room": MR.start_room(M.EVAL, t)}}
    for mode in ("TS/std", "TS/con"):
        f = M.funded_terms(mode)
        det[mode] = {"goal": MR.b_star(f)["b_star"], "start_room": MR.start_room(M.FUNDED, f)}
    return Range("A17", "choices", values=tuple(declared("state_rules")),
                 unit="state rule on the mode's dollar risk (both modes, each its own goal and room)",
                 read=_read("combine_profit_target", "combine_mll", "xfa_mll_start"), detail=det)


# ------------------------------------------------------------------------------------------------ the levers


@dataclass(frozen=True)
class Lever:
    id: str
    layer: str
    name: str
    cls: str
    source: str
    keys: tuple[str, ...]
    depends: tuple[str, ...]
    resolver: Callable[[], Range] | None = None


def _L(i, layer, name, cls, source, keys="", depends="", resolver=None) -> Lever:
    return Lever(i, layer, name, cls, source, tuple(keys.split()), tuple(depends.split()), resolver)


#: the table's rows, in its order (the doc's table must list exactly these, `tests/test_lever_space.py`)
LEVERS: dict[str, Lever] = {lv.id: lv for lv in (
    _L("T1", TRIGGER, "signal source", SEARCHED, DECL, "", "T2 T3 T4 T5 A16", _sources),
    _L("T2", TRIGGER, "session", SEARCHED, ARITH, "trading_hours", "T1 T2b T3", _session),
    _L("T2b", TRIGGER, "NY AM / NY PM boundary", FIXED, DECL, "trading_hours", "T2", _ny_split),
    _L("T3", TRIGGER, "entry window (offer marks)", SEARCHED, ARITH, "trading_hours", "T2 T4 A3", _entry_window),
    _L("T4", TRIGGER, "latency L", SEARCHED, DECL, "", "T1 T3 T5", _latency),
    _L("T5", TRIGGER, "entry type", SEARCHED, DECL, "", "T1 T4 T6", _entry_type),
    _L("T6", TRIGGER, "limit working window", FIXED, DECL, "", "T5", _limit_window),
    _L("T7", TRIGGER, "admission by forecast resolution", SEARCHED, COMPUTE, "", "T1 T3 S1 S2"),
    _L("T8", TRIGGER, "side rule", FIXED, DECL, "", "T1 T5 A15", _side),
    _L("S1", SHAPE, "stop width", SEARCHED, COMPUTE, "combine_mll xfa_mll_start", "T2 S2 S3 S4 S5", _stop_width),
    _L("S2", SHAPE, "reward-to-risk w", SEARCHED, DECL, "", "S1 A1 A2", _ratio),
    _L("S3", SHAPE, "dollar risk, evaluation", SEARCHED, ARITH, "combine_mll combine_position_size_limit",
       "S1 S5 A1", lambda: _risk(M.EVAL)),
    _L("S4", SHAPE, "dollar risk, funded", SEARCHED, ARITH, "xfa_mll_start funded_scaling_plan", "S1 S5 A2 A5",
       lambda: _risk(M.FUNDED)),
    _L("S5", SHAPE, "instrument mix", SEARCHED, DECL, "combine_position_size_limit funded_scaling_plan", "S3 S4",
       _mix),
    _L("S6", SHAPE, "maximum hold (time stop)", DROPPED, DECL, "trading_hours", ""),
    _L("S7", SHAPE, "breakeven stop move", DROPPED, DECL, "prohibited_strategy_auto_breakeven_sim_fills", "T1"),
    _L("S8", SHAPE, "partial exits, scaling in", DROPPED, DECL, "", ""),
    _L("S9", SHAPE, "contracts", DROPPED, ARITH, "", "S1 S3 S4 S5"),
    _L("A1", POLICY, "steady or flip, evaluation", SEARCHED, ARITH,
       "combine_profit_target combine_consistency_max_day_frac combine_mll", "S2 S3", _policy_eval),
    _L("A2", POLICY, "steady or flip, funded", SEARCHED, ARITH,
       "xfa_std_winning_days xfa_cons_min_days xfa_cons_max_day_frac xfa_std_cap xfa_cons_cap "
       "payout_max_frac_of_balance xfa_mll_start", "S2 S4 A5", _policy_funded),
    _L("A3", POLICY, "session rule q (when to stop)", SEARCHED, DECL,
       "combine_consistency_max_day_frac xfa_cons_max_day_frac combine_profit_target", "T3 A5", _session_rule),
    _L("A4", POLICY, "price path", SEARCHED, RULE,
       "subscription_fee activation_fee subscription_fee_naf_50k activation_fee_naf_50k", "A12", _price_path),
    _L("A5", POLICY, "payout path", SEARCHED, RULE,
       "xfa_payout_path_choice xfa_std_cap xfa_cons_cap xfa_std_winning_days xfa_std_winning_day_min "
       "xfa_cons_min_days xfa_cons_max_day_frac", "A2 A3 A18 A19", _payout_path),
    _L("A6", POLICY, "funded seats", SEARCHED, RULE, "max_active_funded_accounts", "A7 A8 A15", _seats),
    _L("A7", POLICY, "evaluations at once", SEARCHED, DECL, "combine_count_limit", "A6 A8 A11", _evals),
    _L("A8", POLICY, "banking while a pass waits", SEARCHED, DECL, "hold_queue_behaviour", "A6 A7 A9", _banking),
    _L("A9", POLICY, "the hold's expiry (two readings)", FIXED, DECL, "hold_expiry_days", "A8 A10", _hold_expiry),
    _L("A10", POLICY, "evaluation-purchase rule", SEARCHED, DECL, "combine_cancellation", "A9 A11", _purchase_rule),
    _L("A11", POLICY, "evaluation-purchase budget", SEARCHED, DECL, "account_start_rate_limit", "A7 A10",
       _purchase_budget),
    _L("A12", POLICY, "Back2Funded reactivations", SEARCHED, RULE,
       "back2funded_max_reactivations back2funded_reactivation_fee_50k back2funded_window_days "
       "back2funded_eligibility back2funded_seat_count", "A4 A6 A18", _back2funded),
    _L("A13", POLICY, "resets", DROPPED, DECL, "reset_rebill_push", "A4"),
    _L("A14", POLICY, "daily-loss-limit election", DROPPED, DECL, "dll_offer_status", "S3 S4"),
    _L("A15", POLICY, "routing (which account takes a trade)", SEARCHED, DECL, "", "A6 A7 A16 T8", _routing),
    _L("A16", POLICY, "signal mix: shares and account assignment", FIXED, DECL, "", "T1 A15", _assignment),
    _L("A17", POLICY, "state rule (sizing by distance to floor or target)", SEARCHED, DECL,
       "combine_profit_target combine_mll xfa_mll_start", "S3 S4 A1 A2 A5", _state_rule),
    _L("A18", POLICY, "first payout request (RD-02 L1)", SEARCHED, DECL,
       "xfa_lock_at payout_min xfa_std_winning_days xfa_std_winning_day_min", "A5 A19", _payout_first),
    _L("A19", POLICY, "request amount (RD-02 L2)", SEARCHED, DECL,
       "payout_max_frac_of_balance xfa_std_cap payout_min payout_request_amount_choice", "A5 A18", _payout_amount),
    _L("A20", POLICY, "request cadence", FIXED, DECL, "require_profit_since_payout", "A18", _payout_cadence),
    _L("A21", POLICY, "payout method", FIXED, DECL,
       "payout_lag_days_aeropay payout_fee payout_lag_days_ach payout_fee_ach", "", _payout_method),
)}


#: a 'to compute' lever whose reading can exist, and how to tell that it does
_COMPUTED: dict[str, Callable[[], bool]] = {"S1": _s1_computed}


def bounds(lever_id: str) -> Range:
    """The lever's range, or a refusal: dropped (`DroppedLever`), 'to compute' (`NotComputed`), 'to declare'
    (`NotDeclared`), or any key not verified (`UnverifiedTerm`)."""
    lv = LEVERS[lever_id]
    if lv.cls == DROPPED:
        raise DroppedLever(f"{lever_id} ({lv.name}) is dropped: no range ({TABLE})")
    if lv.source == COMPUTE and (lv.resolver is None or not _COMPUTED.get(lever_id, lambda: False)()):
        raise NotComputed(f"{lever_id} ({lv.name}): its range is a search-year reading, to compute -- refused until "
                          f"it exists (CHARTER 3.3 (a); E-208)")
    if lv.source == TODECL:
        raise NotDeclared(f"{lever_id} ({lv.name}): its range is to declare -- refused ({TABLE})")
    for k in lv.keys:
        rule(k)                                          # refuses any key not verified, before anything is computed
    if lv.resolver is None:
        raise LeverRefused(f"{lever_id} has no resolver")
    return lv.resolver()


def space() -> dict[str, Range]:
    """Every lever whose range loads at this commit."""
    out = {}
    for i in LEVERS:
        try:
            out[i] = bounds(i)
        except (LeverRefused, UnverifiedTerm):
            pass
    return out


def refusals() -> dict[str, str]:
    """Every lever refused at this commit, with its reason's class."""
    out = {}
    for i in LEVERS:
        try:
            bounds(i)
        except (LeverRefused, UnverifiedTerm) as e:
            out[i] = type(e).__name__
    return out


def latency_cells(source: str) -> tuple[int | None, ...]:
    """T4's cells for a source: every declared L, counted (CHARTER 3.3 (g)); one latency-free cell for P-16 and RL3."""
    if source not in declared("sources"):
        raise ValueError(f"unknown source {source!r}")
    return (None,) if source in declared("latency_free") else tuple(declared("latency"))


def check_design(settings: dict[str, Any]) -> None:
    """Refuse a combination no verified rule settles: Back2Funded under the No Activation Fee path
    (`back2funded_fee_by_pricing_path`, RD-03 2.5) is loaded only once that key is verified."""
    if settings.get("A4") == "naf" and float(settings.get("A12", 0) or 0) > 0:
        rule("back2funded_fee_by_pricing_path")
    if settings.get("T2b") is not None:
        check_ny_boundary(settings["T2b"])
    lat = settings.get("T4")
    src = settings.get("T1")
    if src is not None and lat is not None and lat not in latency_cells(src):
        raise LeverRefused(f"latency {lat!r} is not a cell of source {src!r}")


def counts() -> dict[str, dict[str, int]]:
    """Levers by layer and class."""
    out: dict[str, dict[str, int]] = {layer: {c: 0 for c in CLASSES} for layer in LAYERS}
    for lv in LEVERS.values():
        out[lv.layer][lv.cls] += 1
    return out


__all__ = ["TABLE", "LAYERS", "CLASSES", "SOURCES", "LeverRefused", "NotComputed", "NotDeclared", "DroppedLever",
           "Declared", "DECLARED", "declared", "rule", "rule_status", "trading_day", "session_windows", "Range",
           "stop_caps", "Lever", "LEVERS", "bounds", "space", "refusals", "latency_cells", "check_design", "counts",
           "S1_RESULT", "S1_PATH", "stop_width", "ny_boundary", "check_ny_boundary", "deal_pools", "state_risk"]
