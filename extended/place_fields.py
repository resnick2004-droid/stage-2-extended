"""Q-70: the place records' fields -- what `extended/place_records.py` records for every simulated trade and every
funded account of a gate campaign, each field with its engine source and the draft lines that need it. Engine-free
(no vendored import), so the test runner can read it in its own process.

**Why a place record.** Two family drafts value a lift **where the campaign uses it**: family B's C2 (the value line)
prices each simulated trade at its place's dollars per unit of win probability, and family O's value line prices each
funded opening. Both need, for every trade the gate campaign simulates, the offer it took, the R the table asked for and
the place it fell in -- the union of the two drafts' asks is the field list below. Recording changes nothing: the paths,
rows and every `PATH_COLS` column are those of the same call with recording off (the identity,
`identity/place_records_identity.py`).

**The places** are Stage 2's D-668 (2) (`propedge.research.u_value_map.PLACES`, U5's value map): (b) `b_evaluation`
every Combine trade; (c) `c_funded_opening` a funded account's first trade; (d) `d_funded_later` its later trades up to
and including the session of its first payout request; (e) `e_paid` its trades after that session -- classified exactly
as the vendored `u_value_map.records_counts` classifies them (checked path by path against it).

**The draft sources** (`SOURCES`): the drafts are still drafts; the citations are by section and phrase, so a
renumbered item can still be found. A field needed by neither draft but asked by Q-70's brief ("its place (path,
account, the account's state, session, time) and what the engine booked") cites `brief`.

**Q-94: the same records on the U1 replay** (`extended/replay_records.py`, through Q-17's adapter
`extended/user_beside.py`). A replay's record is the gate's record with its campaign group -- the gate's arm, level,
path and path seed (`GATE_CAMPAIGN`), which a replay does not have -- replaced by the replay's own
(`REPLAY_CAMPAIGN_FIELDS`: the design, U1's arm, the firm response and its level, the start, its date and its path
seed); every other column is the gate record's, read the same way: `day` is the engine's calendar session on the
start's replay (day t is the session `dates[start_day + t - 1]`, `ReplayTable`), `historical_day` the block of the
start's own window (the window's session `start_day + historical_day`, the same session as the trade's in a replay),
`account_session` the account's live sessions before this one (`FundedAccount.days` at routing; a funded opening's
wait). `REPLAY_TRADE_FIELDS` and `REPLAY_ACCOUNT_FIELDS` are the two schemas.
"""
from __future__ import annotations

from dataclasses import dataclass

#: the draft lines a field is needed by, by key (family B: prereg/DRAFT_F-B_multifeature.md; family O:
#: prereg/DRAFT_F-O_opening_timing.md; both as merged on master at 68f3762, both still drafts)
SOURCES: dict[str, str] = {
    "B-C2": "family B section 13, C2: the gate campaigns of design (i) and design (ii) 'each record, for every "
            "simulated trade j: the offer i(j), the table's R R_j, and the place p(j)' at 'the bound arm'; 'S_j, N_j "
            "per judged session over the paths' trades on it'; the bound 'multiplied by that routing's trades a year'",
    "B-20": "family B section 20 item 10 (item 9 in its fourth version): re-running P-16's registered gate campaign as "
            "U2 did (100 paths, the bound arm, its seed) 'records trades by place whose counts reproduce "
            "u_value_map.csv's trades_per_year_records for p16, and P-14's for p14'; 'records design (ii)'s routing "
            "as it does design (i)'s'",
    "B-11": "family B section 11 (stage B's ranking): the places (b) to (e) by the R they ask, and cap(p, R) from "
            "u_value_map.csv's records_leaf (the table's leaf by phase)",
    "O-18": "family O section 18.1 item 4: 'every simulated trade's offer, R and place, and for each opening its wait "
            "and whether it was a fallback'; its identity against trades_per_year_records for p16; and 'on the U1 "
            "replay as well as the gate' -- 'the openings it records equal the replay ledger's' (the replay is wired "
            "by Q-94: extended/replay_records.py)",
    "O-A2": "family O section 9, A2 ('on the U1 replay in history's order'): the counts of where the openings fall "
            "for P-16, each cell's design and its two twin designs -- by mark, hour, day kind, the sessions from "
            "activation, each design's wait distribution -- and 5.5: 'each opening is counted once per start in whose "
            "replay it falls (a start is one user's journey)'",
    "O-5.5": "family O section 5.5 and A2 (stage A, on the U1 replay in history's order): every funded opening's "
             "'(date, mark), hour, day kind, whether it is at 08:30-09:00, whether at the report-day 07:35:00 entry, "
             "the sessions from activation, and whether the offer is in each cell's state'; 'each opening's wait and "
             "whether it was a fallback'",
    "O-7.4": "family O section 7.4: each funded opening j is one use -- 'its offer i(j)', its value 'and its session'; "
             "u_d the design's openings a year; V_other over 'the designs' trades at places (b), (d) and (e), each at "
             "its own R'",
    "O-5.4": "family O section 5.4 / T-5: a waiting account's 'first W live sessions are those with "
             "FundedAccount.days 0 to W - 1 at routing' (its wait and fallback are counted in those sessions)",
    "O-A1": "family O A1 item 6: 'every in-wait opening's (date, mark), read by the place-recording adapter, is in the "
            "placebo's set'",
    "brief": "Q-70's brief: 'its place (path, account, the account's state, session, time) and what the engine booked'",
    "brief-Q94": "Q-94's brief: on Q-17's U1 replay, 'the same compact records (offer, the table's R, place, account "
                 "and state, booking; each funded account's opening and wait)', riding out beside each start's output",
}

#: the field groups, in the record's column order
GROUPS = ("campaign", "account", "offer", "state", "booked")


@dataclass(frozen=True)
class Field:
    """One recorded column: its name, group, dtype ('int', 'float', 'bool', 'str', 'object'), meaning, where the engine
    gives it, and the draft lines that need it (`SOURCES` keys)."""

    name: str
    group: str
    dtype: str
    meaning: str
    engine: str
    needed_by: tuple[str, ...]


def _f(name: str, group: str, dtype: str, meaning: str, engine: str, *needed_by: str) -> Field:
    return Field(name, group, dtype, meaning, engine, tuple(needed_by))


#: one row a simulated trade (an executed trade on the engine's per-trade ledger), in column order
TRADE_FIELDS: tuple[Field, ...] = (
    # ---- the campaign: which run of the gate the trade is in
    _f("shift", "campaign", "str", "the gate's arm: 'point' (as measured) or 'lower_bound' (every R shifted to its "
       "bound; the gate row's arm)", "extended.gate.run_gate's loop", "B-C2", "B-20", "O-18"),
    _f("enforcement_p", "campaign", "float", "the campaign's payout-denial level (0.0 in every run the drafts name)",
       "extended.gate.run_gate's loop", "B-C2", "O-18"),
    _f("path", "campaign", "int", "the path's index in the campaign (0-based, the campaign seed's stream order)",
       "lockstep.path_seeds order", "B-C2", "brief"),
    _f("path_seed", "campaign", "int", "the path's own seed (lockstep.path_seeds(seed, n)[path])",
       "lockstep.path_seeds", "brief"),
    _f("day", "campaign", "int", "the engine's calendar session of the trade on its path (0 .. horizon - 1)",
       "ledger row `day`", "brief", "O-5.5"),
    # ---- the account: which account took it, and where in its life
    _f("kind", "account", "str", "'combine' (an evaluation) or 'funded' (an Express Funded Account)",
       "ledger row `kind`", "B-C2", "brief"),
    _f("account", "account", "int", "the account's number: a Combine's in purchase order, a funded account's in "
       "activation order", "ledger row `index`", "brief", "O-18"),
    _f("attempt", "account", "int", "a Combine's resets before this session (0 for a funded account): the attempt "
       "the trade is in", "daily recorder `attempt`", "brief"),
    _f("activation_day", "account", "int", "a funded account's activation session on its path (its first trading "
       "session is the next); -1 for a Combine", "FundedRecord.activation_day", "O-5.5"),
    _f("rel_day", "account", "int", "the session counted from the account's first session (the engine's relative "
       "day: day - start_day)", "ledger row `rel_day`", "O-5.5", "O-18"),
    _f("account_session", "account", "int", "the account's live sessions before this one: its position among its "
       "own recorded sessions (FundedAccount.days at routing; within the attempt for a Combine) -- a funded "
       "opening's wait", "daily recorder rows, by account", "O-18", "O-5.4", "O-5.5"),
    _f("phase", "account", "str", "the session's phase: 'combine', 'funded' (before or on the session of the first "
       "payout request) or 'paid' (after it) -- records_counts' phase", "u_value_map.records_counts' rule",
       "B-11", "brief"),
    _f("place", "account", "str", "D-668 (2)'s place: b_evaluation, c_funded_opening, d_funded_later or e_paid",
       "u_value_map.records_counts' rule (checked against it)", "B-C2", "B-20", "B-11", "O-18", "O-7.4"),
    _f("opening", "account", "bool", "the funded account's first trade (place c)", "u_value_map.records_counts' rule",
       "O-18", "O-7.4", "O-5.5", "B-C2"),
    # ---- the offer: which historical trade the router handed it
    _f("historical_day", "offer", "int", "the index of the day block the trade was drawn from (the campaign's "
       "blocks; -1 for a flip trade, which has none)", "draw's last_trade `historical_day`", "B-C2", "O-7.4"),
    _f("trade_index", "offer", "int", "the trade's index within that day block (the block's entry order; -1 for a "
       "flip)", "draw's last_trade `trade_index`", "B-C2", "O-18"),
    _f("date", "offer", "str", "the historical session of the offer -- the caller's date of that block ('' when no "
       "dates were given)", "the caller's `dates`, by historical_day", "B-C2", "O-5.5", "O-7.4"),
    _f("offer", "offer", "object", "the caller's id of the offer i(j) -- its (date, mark) or any key the family "
       "joins on (None when no ids were given)", "the caller's `offer_ids`, by (historical_day, trade_index)",
       "B-C2", "O-7.4", "O-5.5", "O-A1"),
    _f("side", "offer", "int", "the offer's side in the routing's own blocks (+1 long, -1 short, 0 not carried) -- "
       "design (ii)'s coin side on its own campaign", "DayBlock.sides", "B-C2", "B-20"),
    _f("entry_t", "offer", "float", "the offer's entry time as its block carries it (gate_blocks: the trade table's "
       "`entry_t`); the hour of the place", "DayBlock.entry_t", "O-5.5", "brief"),
    _f("exit_t", "offer", "float", "the offer's single logged exit time as its block carries it",
       "DayBlock.exit_t", "brief"),
    _f("source", "offer", "str", "'strategy' (a routed offer) or 'flip' (the account's own flip bracket, D-339)",
       "ledger row `source`", "brief"),
    # ---- the account's state when it took the trade
    _f("session_balance", "state", "float", "the account's balance at the session's start (its previous recorded "
       "close; 0 on its first session) -- the state the table reads", "daily recorder rows", "brief", "B-11"),
    _f("session_floor", "state", "float", "its loss floor at the session's start (the starting floor on its first)",
       "daily recorder rows", "brief", "B-11"),
    _f("balance_before", "state", "float", "the balance just before the trade", "ledger row `balance_before`",
       "brief"),
    _f("floor", "state", "float", "the loss floor when the trade was taken", "ledger row `floor`", "brief"),
    _f("room", "state", "float", "the room the draw was handed (the nearer of the floor and a daily limit); NaN when "
       "the draw does not report it", "draw's last_trade `room`", "brief"),
    _f("regime", "state", "str", "the table's leaf for the session (the risk policy's decision path; '' without a "
       "policy)", "ledger row stamp `regime`", "B-11", "brief"),
    _f("policy_risk", "state", "float", "the table's dollar risk for the session (NaN without a policy)",
       "ledger row stamp `policy_risk`", "brief"),
    _f("policy_rr", "state", "float", "the table's R for the session (NaN without a policy or when it keeps the "
       "log's)", "ledger row stamp `policy_rr`", "B-C2", "brief"),
    _f("policy_max_trades", "state", "float", "the table's trades a session (NaN for the protocol's)",
       "ledger row stamp `policy_max_trades`", "brief"),
    _f("rr", "state", "float", "R_j, the R the table asked of the trade (the draw's `rr`, else policy_rr; NaN when "
       "the log's own R was traded)", "draw's last_trade `rr`", "B-C2", "O-18", "O-7.4"),
    # ---- what the engine booked
    _f("rr_used", "booked", "float", "the R of the bracket the trade was closed on (a need exit walks to a lower one; "
       "NaN when not reported)", "draw's last_trade `rr_used`", "brief"),
    _f("at_need", "booked", "bool", "closed at the need (the pass or the day's consistency allowance; D-306, D-313)",
       "draw's last_trade `at_need`", "brief"),
    _f("exit_kind", "booked", "str", "'pass' or 'consistency' for a need exit, '' otherwise",
       "draw's last_trade `exit_kind`", "brief"),
    _f("pnl", "booked", "float", "the dollars the engine booked (after its floor and daily-limit clips)",
       "ledger row `pnl`", "brief"),
    _f("balance_after", "booked", "float", "the balance just after the trade", "ledger row `balance_after`", "brief"),
    _f("u", "booked", "float", "the draw's outcome in R at the R used, before the engine's clips (NaN when not "
       "reported)", "draw's last_trade `u`", "brief"),
    _f("contracts", "booked", "float", "the micro-equivalent contracts (NaN when the draw sizes in dollars)",
       "draw's last_trade `contracts`", "brief"),
    _f("realised_risk", "booked", "float", "the dollars risked at the contracts held", "draw's last_trade",
       "brief"),
    _f("intended_risk", "booked", "float", "the dollars the table intended", "draw's last_trade", "brief"),
    _f("intended_capped_risk", "booked", "float", "the intention capped by the tier and the room",
       "draw's last_trade", "brief"),
    _f("risk_per_contract", "booked", "float", "the stop's dollars a micro", "draw's last_trade", "brief"),
    _f("fee", "booked", "float", "the fee at the contracts held where re-priced (D-324; NaN otherwise)",
       "draw's last_trade `fee`", "brief"),
    _f("room_capped", "booked", "bool", "the size was cut to the room above the floor (D-313)",
       "draw's last_trade `room_capped`", "brief"),
    _f("at_cap", "booked", "bool", "the size was at the tier's cap", "draw's last_trade `at_cap`", "brief"),
    _f("mae", "booked", "float", "the trade's adverse excursion in dollars as the draw settled it (NaN unknown)",
       "draw's last_trade `mae`", "brief"),
    _f("settlement", "booked", "str", "how a trade risking more than the room settles (D-156)",
       "draw's last_trade `settlement`", "brief"),
)

#: one row a funded account of a recorded path (whether or not it ever traded): its opening and its wait
ACCOUNT_FIELDS: tuple[Field, ...] = (
    _f("shift", "campaign", "str", "the gate's arm", "extended.gate.run_gate's loop", "O-18"),
    _f("enforcement_p", "campaign", "float", "the denial level", "extended.gate.run_gate's loop", "O-18"),
    _f("path", "campaign", "int", "the path's index", "lockstep.path_seeds order", "O-18"),
    _f("account", "account", "int", "the funded account's number in activation order", "FundedRecord.index", "O-18"),
    _f("activation_day", "account", "int", "its activation session", "FundedRecord.activation_day", "O-5.5"),
    _f("days", "account", "int", "its live sessions", "FundedRecord.days", "O-18", "O-5.4"),
    _f("trades", "account", "int", "its trades", "FundedRecord.trades", "brief"),
    _f("n_payouts", "account", "int", "its payouts", "FundedRecord.n_payouts", "brief"),
    _f("first_payout_day", "account", "int", "the relative session of its first payout request (-1 none)",
       "FundedRecord.first_payout_day", "B-C2", "O-7.4"),
    _f("closed", "account", "bool", "ended at its floor or by the policy", "FundedRecord.closed", "brief"),
    _f("abandoned", "account", "bool", "closed at the policy's request (D-329)", "FundedRecord.abandoned", "brief"),
    _f("opened", "account", "bool", "it took a first trade (an opening) on the path", "the ledger", "O-18", "O-5.5"),
    _f("opening_day", "account", "int", "the session of its opening (-1 none)", "the ledger", "O-5.5"),
    _f("opening_rel_day", "account", "int", "the opening's relative session (-1 none)", "the ledger", "O-5.5"),
    _f("opening_session", "account", "int", "its live sessions before the opening -- the wait (-1 none: the wait "
       "is censored at `days`)", "daily recorder rows", "O-18", "O-5.4"),
)

TRADE_COLUMNS = tuple(f.name for f in TRADE_FIELDS)
ACCOUNT_COLUMNS = tuple(f.name for f in ACCOUNT_FIELDS)

# ---- Q-94: the U1 replay's records (`extended/replay_records.py`)

#: the gate record's campaign columns, which a replay does not have and its record replaces
GATE_CAMPAIGN = ("shift", "enforcement_p", "path", "path_seed")

#: a replay record's campaign group: which replay, which start
REPLAY_CAMPAIGN_FIELDS: tuple[Field, ...] = (
    _f("design", "campaign", "str", "the replayed configuration (U1's configuration name, as `user_beside.run_starts` "
       "was given it)", "extended.user_beside.run_starts' design", "O-A2", "O-18"),
    _f("arm", "campaign", "str", "U1's arm the replay ran: 'verdict' (every R shifted to its bound, the gate row's "
       "lower-bound arm) or 'point' (as traded)", "extended.user_beside.run_starts' arm", "O-A2"),
    _f("response", "campaign", "str", "the firm response the replay ran under ('off': the vendored 0 %, "
       "placement-off call; `user_beside.RESPONSES`)", "extended.user_beside.Response.name", "O-A2", "brief-Q94"),
    _f("enforcement_p", "campaign", "float", "the response's payout-denial level (0.0 for 'off')",
       "extended.user_beside.Response.enforcement_p", "brief-Q94"),
    _f("start_day", "campaign", "int", "the start's index in the configuration's window: the replay's first session "
       "is the window's session start_day (one start is one user's journey)", "extended.user_beside._task's start",
       "O-A2", "O-5.5"),
    _f("start_date", "campaign", "str", "the start's first session (the job's dates[start_day])", "the job's dates",
       "O-A2", "brief-Q94"),
    _f("start_seed", "campaign", "int", "the start's path seed (`user_beside.start_seed`: it drives only the "
       "enforcement stream)", "extended.user_beside.start_seed", "brief-Q94"),
)
#: one row a simulated trade of a start's replay: the replay's campaign group, then the gate record's other columns
REPLAY_TRADE_FIELDS: tuple[Field, ...] = REPLAY_CAMPAIGN_FIELDS + tuple(f for f in TRADE_FIELDS
                                                                        if f.name not in GATE_CAMPAIGN)
#: one row a funded account of a start's replay (opened or not): its opening and its wait
REPLAY_ACCOUNT_FIELDS: tuple[Field, ...] = REPLAY_CAMPAIGN_FIELDS + tuple(f for f in ACCOUNT_FIELDS
                                                                          if f.name not in GATE_CAMPAIGN)
REPLAY_CAMPAIGN_COLUMNS = tuple(f.name for f in REPLAY_CAMPAIGN_FIELDS)
REPLAY_TRADE_COLUMNS = tuple(f.name for f in REPLAY_TRADE_FIELDS)
REPLAY_ACCOUNT_COLUMNS = tuple(f.name for f in REPLAY_ACCOUNT_FIELDS)


def by_name(fields: tuple[Field, ...] = TRADE_FIELDS) -> dict[str, Field]:
    return {f.name: f for f in fields}


def problems() -> list[str]:
    """The schema's own checks: unique names, known groups and dtypes, every field needed by a known source, and every
    draft source used by some field; and (Q-94) the replay schemas are the gate's with the campaign group replaced."""
    out = []
    for fields, what in ((TRADE_FIELDS, "trade"), (ACCOUNT_FIELDS, "account"),
                         (REPLAY_TRADE_FIELDS, "replay trade"), (REPLAY_ACCOUNT_FIELDS, "replay account")):
        names = [f.name for f in fields]
        if len(set(names)) != len(names):
            out.append(f"{what} fields: a name repeats")
        for f in fields:
            if f.group not in GROUPS:
                out.append(f"{what} field {f.name}: unknown group {f.group!r}")
            if f.dtype not in ("int", "float", "bool", "str", "object"):
                out.append(f"{what} field {f.name}: unknown dtype {f.dtype!r}")
            if not f.needed_by:
                out.append(f"{what} field {f.name}: needed by nothing")
            bad = [k for k in f.needed_by if k not in SOURCES]
            if bad:
                out.append(f"{what} field {f.name}: unknown sources {bad}")
            if not f.meaning or not f.engine:
                out.append(f"{what} field {f.name}: undocumented")
    used = {k for f in TRADE_FIELDS + ACCOUNT_FIELDS + REPLAY_CAMPAIGN_FIELDS for k in f.needed_by}
    unused = sorted(set(SOURCES) - used)
    if unused:
        out.append(f"sources no field cites: {unused}")
    for gate, replay, what in ((TRADE_FIELDS, REPLAY_TRADE_FIELDS, "trade"),
                               (ACCOUNT_FIELDS, REPLAY_ACCOUNT_FIELDS, "account")):
        rest = tuple(f for f in gate if f.name not in GATE_CAMPAIGN)
        k = len(REPLAY_CAMPAIGN_FIELDS)
        if replay[k:] != rest or replay[:k] != REPLAY_CAMPAIGN_FIELDS:
            out.append(f"the replay {what} fields are not the replay's campaign group and the gate's other fields")
        if not set(GATE_CAMPAIGN) & {f.name for f in gate}:
            out.append(f"the gate {what} fields carry none of the gate's campaign columns")
    return out


def describe() -> str:
    """The field list as text: name, group, dtype, the draft keys, the meaning."""
    lines = []
    for fields, what in ((TRADE_FIELDS, "trades"), (ACCOUNT_FIELDS, "funded accounts"),
                         (REPLAY_CAMPAIGN_FIELDS, "a U1 replay's campaign group (Q-94; in place of the gate's)")):
        lines.append(f"# {what}")
        for f in fields:
            lines.append(f"{f.name:22s} {f.group:9s} {f.dtype:6s} [{', '.join(f.needed_by)}] {f.meaning}")
    return "\n".join(lines)


__all__ = ["SOURCES", "GROUPS", "Field", "TRADE_FIELDS", "ACCOUNT_FIELDS", "TRADE_COLUMNS", "ACCOUNT_COLUMNS",
           "GATE_CAMPAIGN", "REPLAY_CAMPAIGN_FIELDS", "REPLAY_TRADE_FIELDS", "REPLAY_ACCOUNT_FIELDS",
           "REPLAY_CAMPAIGN_COLUMNS", "REPLAY_TRADE_COLUMNS", "REPLAY_ACCOUNT_COLUMNS", "by_name", "problems",
           "describe"]
