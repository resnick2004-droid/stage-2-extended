"""Machine check of a model card, the research protocol's steps 1-4 on one page (D-155).

Every new model is written down before any QuantConnect kit is built for it: the hypothesis, its fit to the contract,
the cheap screen on data already on hand, every parameter classed as fixed, searched or dropped, and what would kill
it (`docs/RESEARCH_PROTOCOL.md`; the form is `prereg/MODEL_CARD_TEMPLATE.md`; cards live in `docs/candidates/cards/`).
A model's pre-registration names its card, and `propedge.backtest.prereg.validate_prereg` refuses it unless this check
passes with `for_prereg=True`.

What is enforced, beyond every field and section being filled in:

* **D-154's setups per day.** The card's Combine size must be one `results/setups_per_day.csv` tabulates (its sizes
  come from stage one), and the setups each account sees -- the setups of every market the card trades, shared out
  across its accounts -- must reach that file's `min_setups_per_day` at the tabulated edge nearest the card's
  assumed edge.
* **No copier across accounts (D-157).** The project's edge is that accounts carry different trades, so one can fail
  while another passes; copying every trade to every account makes them one bet. A card that feeds more than one
  account spreads its trades across them (`rotation`, or `partitioned` by market).
* **Every parameter classed.** A searched parameter means more than one variant, so `k` must be above one.
* **The screen said continue.** A card whose screen killed the model is a record, not a candidate.

From D-201, for every card but those that pre-date it (`PRE_D201`: IM1 and IM2, recorded, not rewritten):

* **Entry, Stop and Exit sections** (`D201_SECTIONS`), the Stop section citing the sizeable stop band
  (`results/stop_band.csv`).
* **The stop band**: the screen's stops (`stop_distribution`: a result file with `market` and `stop_ticks` in the
  micro's ticks, or `none: <why>`) may not fall outside the band, on either side, for more than 25 % of them in any
  lifecycle state (D-190 extended; `propedge/research/stop_band.py`).
* **Wait-for-entry rules**: `entry_type` is `market` (at the decision bar) or `wait` (a retrace or level touch); a
  `wait` card declares `max_wait_bars` and its screen's `fill_rate`, and D-154's check reads setups a day x fill rate.
* **Zero micros (D-190)**: more than 25 % of the screen's stops beyond the state's wide edge -- a stop that buys no
  whole micro at the state's dollar risk -- in any lifecycle state fails the card on its own, stated beside the band's
  two-sided share.

From D-191 (step 0), for every card but the pre-door entries (`PRE_D191`: IM1 and IM2, recorded under D-155 with no
retroactive grade), the card carries its **candidate record** (`D191_FIELDS`): the result file and row of the replicated
atlas row it comes from, a mechanism grade A-D, the screen's k, its setups a day per market and its conduct tiers; and
the **prop-fit score** is computed here, never declared: it passes only when D-154's minimum is met pooled and in at
least three of every four markets the card trades (each market's own setups a day against the minimum), the
zero-micro share is at most 25 % in every state (so the card needs a stop distribution), and all three conduct tiers
pass (tier 1 declared `none` and no tier-1 finding on the card's sizes; every tier-2 flag the sizes raise declared;
tier 3 declared priced).

From D-212, for every card but IM1 and IM2 (`PRE_D212`), three execution rules (the operator's, after IM2's trades
mostly ran to the session close at uneven sizes):

* **Consistent risk**: in every lifecycle state at least 90 % of the screen's stops realise at least 90 % of the
  state's dollar risk -- contracts = min(floor(risk / (stop ticks x tick value)), the state's cap), the band file's
  values -- so whole-micro rounding and the cap cost under 10 % on nine trades in ten.
* **Trades resolve**: `time_stop` is `none` (the model holds every trade to its stop or target), and the screen's
  stop distribution carries each entry's `exit` (target, stop or flatten) and `date`: at most 5 % reach Topstep's
  15:10 CT flatten, overall, in each market and in each year, so the outliers are not a pattern (D-308 raised the
  ceiling from D-212's 2 %; cards validated before it keep their 2 % reading).
* **A declared trading window**: `trading_window` as HH:MM-HH:MM CT inside Topstep's hours, resuming at 17:00 and
  flat by 15:10 (8284206).

One exception (D-263, generalising D-256 and D-257): a card whose `exit_mode` is `direction` -- a direction-style
model, held to its stop or the flatten -- has its flatten share reported, not enforced; brackets are not spared.

**Risk declared by stop width** (D-312 (1), built by D-355): a card may declare each state's dollar risk at each stop
width -- `combine_risk_by_stop` and `funded_risk_by_stop`, 'N ticks R, ...' -- exactly what D-289's full verified
allowance carries at the state's single figure (the Combine's position limit, 8284197; a fresh XFA's entry tier,
8284223; read through the rule gate). Such a card's stop distribution carries each trade's `state`, and every check that
reads a state's risk reads each trade against its own stop's declared risk at the full allowance: D-212 (1)'s consistent
risk (D-312 (1)), and D-201's band and D-190's zero micros (D-242's 'each card's own sizes', for a card whose sizes are
by stop). A declaration that is not what the allowance carries, or a trade whose stop the card does not declare, is
refused. A single-figure card is checked as before.

From D-266, for every card but those written before it (`PRE_D266`: IM1, IM2, NQB1, NQB2 and the ORB2 and ORB3
drafts, recorded, not rewritten), the **execution declaration** (`D266_FIELDS`; the operator trades every signal by
hand):

* **Manual execution**: `execution` is `manual`; `automated` is recognised but refused, since D-266 declares every card
  manual.
* **The latency**: `latency_minutes`, L from the signal to a working order, a positive number and at least the
  operator's 5 minutes -- every model is scored at the operator's latency, so a card may declare more, never less.
  Results are reported at L = 0 and at L; the verdict is the one at L.
* **The missed-trigger policy**: a resting stop or limit entry (`entry_type` `wait`) traded by hand declares what
  happens to a trigger before the order works -- `skip`, `rest` at its level, or `chase` at the market -- before any
  run; a policy outside those three is refused wherever it is declared.
* **The hours**: `trading_hours` is `unconstrained` (the operator's: no hours constraint) or a window HH:MM-HH:MM CT,
  which must hold the card's `trading_window`.

From D-271 (with D-269), for every model from ORB5 on (`PRE_D271`: the same six cards), an **Eras and today's
economics** section (`D271_SECTIONS`) stating each of D-271's rules (`D271_ELEMENTS`) -- their presence is checked,
never their numbers, which come from result files: the per-era report, 2009-2017 against 2018 on; the bootstrap that
resamples whole years, its seed fixed; the lower of the two eras' bounds when they are flagged; gross and net R at
today's cost in R; today's regime by the stop's stand-aside floor; sizing from today's regime's stop widths; the
drift-matched no-skill baseline. A model with several entries a day (`setups_per_day` above 1) declares its
`coordination` (D-269): `one_at_a_time` (D-160, the rule for every model but ORB5 and ORB6, D-278), or ORB5's option `own_account`
beside it -- each entry to its own free account, direction-locked -- which needs more than one account in rotation.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from propedge import RESULTS_DIR
from propedge.backtest.prereg import _is_placeholder, _parse_fields, _section_bodies

#: (key, why) -- every row of the card's machine-checked table.
REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("model", "an id the kits, results and pre-registration will carry"),
    ("markets", "the markets the model trades"),
    ("money_source", "edge, the contract's shape, or both -- said before any data is read"),
    ("combine_rr", "the Combine's R, from stage one's results for the edge assumed"),
    ("combine_risk", "the Combine's dollar risk per trade, from stage one's results"),
    ("funded_rr", "the funded account's R, from stage one's results"),
    ("funded_risk", "the funded account's dollar risk per trade, from stage one's results"),
    ("edge_assumed", "the low end of the edge the model is expected to have; D-154 reads it"),
    ("setups_per_day", "setups a day the mechanism produces, per market, known before any kit"),
    ("accounts", "how many accounts the model feeds"),
    ("layout", "rotation or partitioned (by market) across accounts; copier only for a single account (D-157)"),
    ("k", "variants: the product of the searched parameters' grids, across markets"),
    ("screen", "the cheap screen's result file, or 'none: <why no data on hand bears on it>'"),
    ("screen_verdict", "continue or kill, against the kill line declared before the screen ran"),
    ("prereg", "the registered P-id, or 'pending' until the gatekeeper registers it"),
)
NUMERIC = ("combine_rr", "combine_risk", "funded_rr", "funded_risk", "edge_assumed", "setups_per_day", "accounts", "k")
REQUIRED_SECTIONS: tuple[tuple[str, str], ...] = (
    ("hypothesis", "what should make money, why it should exist, and who pays"),
    ("contract fit", "sizes per state from stage one, setups per day against D-154, the layout, the conduct tiers"),
    ("cheap screen", "the check on data already on hand and the kill line declared before it ran"),
    ("parameters", "every parameter with its value or grid, its class and its source"),
    ("kill criteria", "what result ends the model at each later step"),
)
LAYOUTS = ("rotation", "partitioned", "copier")
CLASSES = ("fixed", "searched", "dropped")
SETUPS_FILE = RESULTS_DIR / "setups_per_day.csv"
BAND_FILE = RESULTS_DIR / "stop_band.csv"

#: D-201: cards written before the rule, recorded as pre-dating it and not rewritten
PRE_D201 = ("IM1", "IM2")
D201_FIELDS: tuple[tuple[str, str], ...] = (
    ("entry_type", "market (at the decision bar) or wait (a retrace or level touch)"),
    ("stop_distribution", "the screen's stops: a result file with market and stop_ticks (micro ticks), or 'none: <why>'"),
)
D201_SECTIONS: tuple[tuple[str, str], ...] = (
    ("entry", "the feature, the signal rule, the session and time-of-day conditions"),
    ("stop", "the structural location rule and its size distribution in ticks, against results/stop_band.csv"),
    ("exit", "the target as R x stop, the time stop in bars, the session-flat rule"),
)
ENTRY_TYPES = ("market", "wait")

#: D-191: the pre-door entries (D-155), recorded without a retroactive grade
PRE_D191 = ("IM1", "IM2")
D191_FIELDS: tuple[tuple[str, str], ...] = (
    ("candidate_record", "the result file (with its manifest) holding the replicated atlas row the model comes from"),
    ("atlas_row", "the row in it, as market:test (or a key the file holds)"),
    ("mechanism_grade", "A forced flow with a named counterparty; B behavioural, two independent published results and "
                        "persistence after publication; C a regime or filter; D mined, unconfirmed out of sample"),
    ("screen_k", "the screen's own k: every filter and threshold it tried"),
    ("setups_by_market", "setups a day each market produces, e.g. 'ES 3, CL 2.5'"),
    ("conduct_tier1", "'none': no hedging, simulator fills, off-book fills, size into news, coordination or "
                      "concealment"),
    ("conduct_tier2", "the Responsible Trading Program flags the sizes raise, or 'none'"),
    ("conduct_tier3", "'priced': stacking and purchase patterns carry the gate's denial probability"),
)
GRADES = ("A", "B", "C", "D")
SHARE_OF_MARKETS = 0.75                 # D-191: "at least three of four markets"

#: D-212: the execution rules, for every card but those that pre-date them
PRE_D212 = ("IM1", "IM2")
D212_FIELDS: tuple[tuple[str, str], ...] = (
    ("trading_window", "HH:MM-HH:MM CT inside Topstep's hours: resume at 17:00, flat by 15:10 (8284206)"),
    ("time_stop", "'none': every trade is held to its stop or its target"),
)
RISK_TOLERANCE = 0.10                   # D-212: realised risk at least 90 % of the state's dollar risk ...
RISK_SHARE = 0.90                       # ... on at least 90 % of the screen's trades, in every state
MAX_FLATTEN_SHARE = 0.05                # D-212 (2) as amended by D-308: at most 5 % reach the 15:10 flatten, overall, per market, per year (2 % before 2026-10-06)
EXITS = ("target", "stop", "flatten")
FUNDED_CAP_STATE = "funded_below_2000"  # D-229: a funded account starts below +$2,000, under the scaling plan's smaller cap
#: D-263 (from D-256, D-257): a card whose `exit_mode` is `direction` -- a direction-style model, each trade held to its
#: stop or the session's flatten, which reaches the flatten by construction -- is spared D-212's 2 % flatten share; the
#: share is reported in a note, never enforced. Consistent risk and the trading window stand. Brackets are not spared.
FLATTEN_EXEMPT_MODE = "direction"
FLATTEN_EXEMPT_WHY = ("D-263: a direction-style model (held to its stop or the flatten) reaches the flatten by "
                      "construction; the share is reported, not enforced")
FLATTEN_MIN, REOPEN_MIN = 15 * 60 + 10, 17 * 60

#: D-266: the execution declaration, for every card but those written before it (recorded, not rewritten)
PRE_D266 = ("IM1", "IM2", "NQB1", "NQB2", "ORB2", "ORB3")
D266_FIELDS: tuple[tuple[str, str], ...] = (
    ("execution", "'manual': the operator trades every signal by hand"),
    ("latency_minutes", "L, minutes from the signal to a working order: positive, the operator's 5"),
    ("trading_hours", "the hours the operator can trade: 'unconstrained' (the operator's), or HH:MM-HH:MM CT"),
)
EXECUTIONS = ("manual", "automated")
OPERATOR_LATENCY_MINUTES = 5.0          # D-266: the operator, "About 5 minutes"
#: D-282: inside fixed sessions the operator sits for, "1-2 minutes" -- the conservative end, per model agreed with them
#: FV3-C (D-355): FV3's frozen cell under the firm's two rules -- the same scheduled sessions
SEATED_LATENCY = {"FV2": 2.0, "FV3": 2.0, "FV3-C": 2.0,      # D-282: scheduled sessions the operator sits for
                  "FV3-S": 2.0,                              # D-405: FV3-C's trades and sessions, re-sized
                  "T23-D20": 2.0}                            # D-419: fixed, announced times the operator sits for
MISSED_TRIGGER_POLICIES = ("skip", "rest", "chase")
RESTING_ENTRY_TYPES = ("wait",)         # D-201's wait: a retrace or level touch, a resting limit or stop order
UNCONSTRAINED_HOURS = "unconstrained"   # D-266: "Any hours that perform the best I can be available"

#: D-271 (with D-269): for every model from ORB5 on; the cards written before it are recorded, not rewritten
PRE_D271 = ("IM1", "IM2", "NQB1", "NQB2", "ORB2", "ORB3")
D271_SECTIONS: tuple[tuple[str, str], ...] = (
    ("eras", "D-271: the per-era report and its bootstrap rule, gross and net R at today's cost, today's regime by the "
             "stop floor, sizing from today's stop widths, the drift-matched baseline; D-269's coordination"),
)
#: (what the section must state, the patterns that must all appear in it) -- presence only, never a number's value
D271_ELEMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("the per-era report, 2009-2017 against 2018 on", (r"2009\s*(?:-|–|to)\s*2017", r"2018")),
    ("the bootstrap that resamples whole years, its seed fixed", (r"bootstrap", r"seed")),
    ("the lower of the two eras' bounds used when they are flagged", (r"\blower\b", r"\bflag")),
    ("gross and net R at today's cost in R", (r"\bgross\b", r"\bnet\b")),
    ("today's regime by the stop's stand-aside floor", (r"\bfloor\b",)),
    ("sizing drawn from today's regime's stop widths", (r"stop widths?",)),
    ("the drift-matched no-skill baseline", (r"\bdrift", r"\bbaseline\b")),
)
COORDINATIONS = ("one_at_a_time", "own_account")
#: D-269: each entry to its own free account is ORB5's declared option; "D-160 stays ... the rule for other models";
#: D-278 extends it to ORB6, whose search the operator agreed with the option in it (2026-10-04)
COORDINATION_OPTION_MODELS = ("ORB5", "ORB6")


@dataclass
class CardValidation:
    """The result of checking one model card."""

    path: str | None
    fields: dict[str, str] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.problems)

    def report(self) -> str:
        if self.ok:
            return "\n".join(["model card is complete."] + [f"  note: {n}" for n in self.notes])
        lines = ["REFUSED -- this model card is incomplete."]
        lines += [f"  missing: {m}" for m in self.missing]
        lines += [f"  problem: {p}" for p in self.problems]
        lines += [f"  note: {n}" for n in self.notes]
        return "\n".join(lines)


def _number(value: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", (value or "").replace(",", ""))
    return float(m.group(0)) if m else None


def _parameter_rows(body: str) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "parameter" or set(cells[0]) <= set("-: "):
            continue
        rows.append(cells)
    return rows


def setups_minimum(rr: float, risk: float, edge: float, setups_file: Path = SETUPS_FILE) -> float | None:
    """D-154's minimum setups a day for a Combine size at the tabulated edge nearest `edge`; None if not tabulated."""
    from propedge.reporting.results import read_result

    t = read_result(setups_file).drop_duplicates(["rr", "risk", "edge"])
    t = t[(t["rr"].sub(rr).abs() < 1e-9) & (t["risk"].sub(risk).abs() < 1e-6)]
    if t.empty:
        return None
    dist = (t["edge"] - edge).abs()
    row = t[dist == dist.min()].sort_values("edge").iloc[-1]
    return float(row["min_setups_per_day"])


def unsizeable_shares(stops, band) -> dict[str, float]:
    """D-190: {state: the share of `stops` beyond its market's wide edge -- no whole micro at the state's risk}. A stop
    in a market the band does not cover counts as unsizeable. A `state` column in `stops` checks each of the band's
    states on its own stops only (D-242; a state with none counts as wholly unsizeable)."""
    out = {}
    for state, b in band.groupby("state", sort=False):
        s = stops[stops["state"].astype(str) == state] if "state" in stops.columns else stops
        if not len(s):
            out[state] = 1.0 if "state" in stops.columns else float("nan")
            continue
        hi = s["market"].map(b.set_index("market")["wide_ticks"])
        out[state] = float((~(s["stop_ticks"] <= hi)).mean())
    return out


def card_sizes(fields: dict[str, str]) -> dict[str, tuple[float, str]] | None:
    """{state: (the card's dollar risk, the band state whose size cap applies)} from its fields, or None (D-229)."""
    cr, fr = _number(fields.get("combine_risk") or ""), _number(fields.get("funded_risk") or "")
    return {"combine": (cr, "combine"), "funded": (fr, FUNDED_CAP_STATE)} if cr and fr else None


#: D-312 (1), built by D-355: the by-stop declaration's fields, per lifecycle state
BY_STOP_FIELDS: tuple[tuple[str, str], ...] = (("combine", "combine_risk_by_stop"), ("funded", "funded_risk_by_stop"))
_SINGLE_FIGURE = {"combine": "combine_risk", "funded": "funded_risk"}


def risk_by_stop(fields: dict[str, str]) -> tuple[dict[str, dict[float, float]] | None, str | None]:
    """D-312 (1): ({state: {stop ticks: dollar risk}}, None) from a card's by-stop fields ('50 ticks 1250, 100 ticks
    2000'; anything from the first parenthesis on is commentary); (None, None) for a single-figure card, which declares
    neither; (None, a problem) when only one is declared or one cannot be read."""
    given = {s: fields.get(k) for s, k in BY_STOP_FIELDS
             if fields.get(k) is not None and not _is_placeholder(fields.get(k))}
    if not given:
        return None, None
    if len(given) != len(BY_STOP_FIELDS):
        return None, ("D-312 (1): a card declaring risk by stop width declares it for both states "
                      f"({', '.join(k for _, k in BY_STOP_FIELDS)})")
    out: dict[str, dict[float, float]] = {}
    for state, value in given.items():
        body = value.split("(")[0]
        pairs = re.findall(r"(\d+(?:\.\d+)?)\s*ticks?\s*\$?\s*(\d[\d,]*(?:\.\d+)?)", body)
        rest = re.sub(r"(\d+(?:\.\d+)?)\s*ticks?\s*\$?\s*(\d[\d,]*(?:\.\d+)?)", "", body)
        if not pairs or re.search(r"\d", rest):
            return None, f"D-312 (1): {state}'s risk by stop must read 'N ticks R, ...', got {value!r}"
        m: dict[float, float] = {}
        for st, r in pairs:
            if float(st) in m:
                return None, f"D-312 (1): {state}'s risk by stop declares {st} ticks twice"
            m[float(st)] = float(r.replace(",", ""))
        out[state] = m
    return out, None


def full_allowance() -> dict[str, int]:
    """D-289's full verified allowance in micros, through the rule gate: the Combine's position limit (8284197) and a
    fresh XFA's entry tier (8284223)."""
    from propedge.campaign.sizing import SizingRule

    rule = SizingRule.from_ledger(headroom_frac=1.0)
    return {"combine": int(rule.allowance_micros("combine", 0.0)), "funded": int(rule.ladder.entry_allowance_micros)}


def _by_stop_frame(stops, by_stop: dict[str, dict[float, float]], band, allowance: dict[str, int]):
    """Each trade of a by-stop card's states with its declared risk, tick value, cost floor and cap."""
    import pandas as pd

    m = band.drop_duplicates("market").set_index("market")
    parts = []
    for state, decl in by_stop.items():
        s = stops[stops["state"].astype(str) == state].copy()
        s["risk"] = s["stop_ticks"].astype(float).map(lambda x, d=decl: d.get(float(x), float("nan")))
        s["tick_value"] = s["market"].map(m["tick_value"]).astype(float)
        s["floor_ticks"] = s["market"].map(m["cost_drag_floor_ticks"]).astype(float)
        s["cap"] = float(allowance[state])
        parts.append(s)
    return pd.concat(parts) if parts else stops.iloc[0:0]


def by_stop_shares(stops, by_stop: dict[str, dict[float, float]], band,
                   allowance: dict[str, int] | None = None) -> dict[str, dict[str, float]]:
    """D-312 (1): per state of a by-stop card, each trade against its own stop's declared risk at the full allowance --
    {state: {outside: D-201's two-sided share, unsizeable: D-190's beyond the wide edge, risk_ok: D-212 (1)'s share
    realising 90 % of its risk, undeclared: the share whose stop the card does not declare, n}}. A state with no trades
    fails every share; a market the band does not cover counts against it."""
    import numpy as np

    allowance = allowance or full_allowance()
    f = _by_stop_frame(stops, by_stop, band, allowance)
    out = {}
    for state in by_stop:
        s = f[f["state"].astype(str) == state]
        if not len(s):
            out[state] = {"outside": 1.0, "unsizeable": 1.0, "risk_ok": 0.0, "undeclared": 0.0, "n": 0}
            continue
        st, risk, tv, cap = s["stop_ticks"].astype(float), s["risk"], s["tick_value"], s["cap"]
        narrow = np.maximum(np.ceil(risk / (cap * tv)), s["floor_ticks"])
        wide = np.floor(risk / tv)
        inside = (st >= narrow) & (st <= wide)
        per = st * tv
        n = np.minimum(np.floor(risk / per), cap)
        ok = (n * per) >= (1.0 - RISK_TOLERANCE) * risk
        out[state] = {"outside": float((~inside).mean()), "unsizeable": float((~(st <= wide)).mean()),
                      "risk_ok": float(ok.mean()), "undeclared": float(risk.isna().mean()), "n": int(len(s))}
    return out


def by_stop_declaration_problems(fields: dict[str, str], by_stop: dict[str, dict[float, float]], stops, band,
                                 allowance: dict[str, int] | None = None) -> list[str]:
    """D-312 (1): each declared risk must be exactly what the full allowance carries at the state's single figure --
    min(floor(figure / stop $), the allowance) x stop $ -- in every market the stops trade; and every trade's stop is
    declared."""
    import math as _m

    allowance = allowance or full_allowance()
    m = band.drop_duplicates("market").set_index("market")
    out = []
    for state, decl in by_stop.items():
        figure = _number(fields.get(_SINGLE_FIGURE[state]) or "")
        s = stops[stops["state"].astype(str) == state]
        undeclared = sorted({float(x) for x in s["stop_ticks"]} - set(decl))
        if undeclared:
            out.append(f"D-312 (1): {state} trades at stops the card does not declare: "
                       + ", ".join(f"{x:g} ticks" for x in undeclared))
        if figure is None:
            out.append(f"D-312 (1): {state}'s single figure ({_SINGLE_FIGURE[state]}) is needed to check its risk by stop")
            continue
        for market in sorted(set(s["market"].astype(str))):
            if market not in m.index:
                continue
            tv = float(m.loc[market, "tick_value"])
            for st, r in sorted(decl.items()):
                per = st * tv
                carried = min(_m.floor(figure / per + 1e-9), allowance[state]) * per
                if abs(carried - r) > 0.005:
                    out.append(f"D-312 (1): {state} declares ${r:,.2f} at {st:g} ticks on {market}; the full allowance "
                               f"({allowance[state]} micros) carries ${carried:,.2f} at its ${figure:,.0f}")
    return out


def card_band(band, sizes: dict[str, tuple[float, str]]):
    """D-242: D-201's band at a card's own sizes -- one row per market and card state, built as
    `stop_band.band_rows` builds the committed band: the wide edge floor(risk / tick value); the narrow edge the larger
    of ceil(risk / (cap x tick value)), the cap being the band state's, and the market's cost-drag floor. The committed
    band holds stage one's lifecycle family's risks only; a card sized from another of stage one's results (T5 2a) is
    checked at its own."""
    import pandas as pd

    rows = []
    for state, (risk, cap_state) in sizes.items():
        for _, b in band[band["state"] == cap_state].iterrows():
            cap, tv = int(b["cap_micros"]), float(b["tick_value"])
            cap_ticks = math.ceil(float(risk) / (cap * tv))
            rows.append({**b.to_dict(), "state": state, "risk": float(risk), "cap_stop_ticks": cap_ticks,
                         "narrow_ticks": max(cap_ticks, int(b["cost_drag_floor_ticks"])),
                         "wide_ticks": math.floor(float(risk) / tv)})
    return pd.DataFrame(rows)


def _share_outside_own(stops, band) -> dict[str, float]:
    """D-201's share outside the band, each of the band's states on its own stops only (D-242)."""
    from propedge.research.stop_band import share_outside

    out = {}
    for state, b in band.groupby("state", sort=False):
        s = stops[stops["state"].astype(str) == state]
        out[state] = share_outside(s, b)[state] if len(s) else 1.0
    return out


def _stops(stop_distribution: str):
    """(stops, None) from a stop-distribution field, or (None, a problem), or (None, None) for 'none: <why>'."""
    from propedge import REPO_ROOT
    from propedge.reporting.results import read_result

    value = stop_distribution.strip().strip("`")
    if value.lower().startswith("none:"):
        return None, None
    path = Path(value) if Path(value).is_absolute() else REPO_ROOT / value
    if not path.is_file():
        return None, f"stop_distribution {value!r} is not a file"
    stops = read_result(path)
    if not {"market", "stop_ticks"} <= set(stops.columns):
        return None, f"stop_distribution {value!r} needs the columns market and stop_ticks (the micro's ticks)"
    return stops, None


def band_problems(stop_distribution: str, band_file: Path = BAND_FILE,
                  sizes: dict[str, tuple[float, str]] | None = None,
                  by_stop: dict[str, dict[float, float]] | None = None) -> tuple[list[str], list[str]]:
    """(problems, notes) for D-201's stop band -- the share of the screen's stops outside the band in each state -- and
    D-190's share beyond its wide edge alone. With the card's own `sizes` and a `state` column in its stops, the band
    is the card's (`card_band`) and each state is checked on its own stops (D-242); with `by_stop` (D-312 (1)), each
    trade against its own stop's declared risk at the full allowance (`by_stop_shares`)."""
    from propedge.reporting.results import read_result
    from propedge.research.stop_band import MAX_OUTSIDE, share_outside

    stops, problem = _stops(stop_distribution)
    if problem:
        return [problem], []
    if stops is None:
        return [], [f"no stop distribution to check against the band ({stop_distribution.strip()})"]
    band = read_result(band_file)
    where = ""
    if by_stop is not None:
        if "state" not in stops.columns:
            return [f"D-312 (1): a card declaring risk by stop width needs its stops' `state` ({stop_distribution.strip()})"], []
        sh = by_stop_shares(stops, by_stop, band)
        shares = {s: x["outside"] for s, x in sh.items()}
        zero = {s: x["unsizeable"] for s, x in sh.items()}
        where = " (each trade at its own stop's declared risk, the full allowance; D-312 (1))"
    elif sizes and "state" in stops.columns:
        band = card_band(band, sizes)
        shares, zero = _share_outside_own(stops, band), unsizeable_shares(stops, band)
    else:
        shares, zero = share_outside(stops, band), unsizeable_shares(stops, band)
    problems, notes = [], []
    bad = {s: x for s, x in shares.items() if x > MAX_OUTSIDE}
    if bad:
        problems.append(f"D-201: more than {MAX_OUTSIDE:.0%} of the screen's stops fall outside the sizeable stop band "
                        "in " + ", ".join(f"{s} ({x:.0%})" for s, x in bad.items()) + f" ({band_file.name}){where}")
    else:
        notes.append("D-201 band met: " + ", ".join(f"{s} {x:.0%} outside" for s, x in shares.items()) + where)
    bad0 = {s: x for s, x in zero.items() if x > MAX_OUTSIDE}
    if bad0:
        problems.append(f"D-190: more than {MAX_OUTSIDE:.0%} of the screen's entries buy zero whole micros in "
                        + ", ".join(f"{s} ({x:.0%})" for s, x in bad0.items()) + f" ({band_file.name}){where}")
    else:
        notes.append("D-190 met: " + ", ".join(f"{s} {x:.0%} unsizeable" for s, x in zero.items()) + where)
    return problems, notes


def risk_consistency(stops, band, sizes: dict[str, tuple[float, str]] | None = None) -> dict[str, float]:
    """D-212: {state: the share of `stops` whose whole-micro size, capped, realises at least 90 % of the state's risk}.
    `sizes` -- {state: (dollar risk, the band state whose size cap applies)} -- are the card's own states (D-229);
    without it, the band's states at the band's risks. A `state` column in `stops` checks each state on its own stops
    only (a state with none fails). A stop in a market the band does not cover counts against it."""
    import numpy as np
    import pandas as pd

    out = {}
    states = sizes or {s: (None, s) for s in band["state"].drop_duplicates()}
    for state, (risk_of_state, cap_state) in states.items():
        m = band[band["state"] == cap_state].set_index("market")
        s = stops[stops["state"].astype(str) == state] if "state" in stops.columns else stops
        if not len(s):
            out[state] = 0.0 if "state" in stops.columns else float("nan")
            continue
        risk = s["market"].map(m["risk"]) if risk_of_state is None else pd.Series(float(risk_of_state), index=s.index)
        per = s["stop_ticks"] * s["market"].map(m["tick_value"])
        n = np.minimum(np.floor(risk / per), s["market"].map(m["cap_micros"]))
        ok = (n * per) >= (1.0 - RISK_TOLERANCE) * risk
        out[state] = float(ok.fillna(False).mean())
    return out


def flatten_shares(stops) -> dict[str, float]:
    """D-212: the share of the screen's entries that reached the 15:10 flatten -- overall, per market and per year."""
    flat = stops["exit"].astype(str).str.lower() == "flatten"
    year = stops["date"].astype(str).str.replace("-", "").str[:4]
    out = {"all": float(flat.mean())}
    out.update({f"market {m}": float(f.mean()) for m, f in flat.groupby(stops["market"])})
    out.update({f"year {y}": float(f.mean()) for y, f in flat.groupby(year)})
    return out


def _window_span(value: str) -> tuple[int, int] | None:
    """(start, end) in minutes after midnight from 'HH:MM-HH:MM', or None if it does not read so."""
    m = re.search(r"(\d{1,2}):(\d{2})\s*(?:-|–|to)\s*(\d{1,2}):(\d{2})", value or "")
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)) * 60 + int(m.group(4))


def _window_minutes(a: int, b: int) -> set[int]:
    """The minutes of a window from `a` to `b`, wrapping past midnight when `b` is earlier."""
    return set(range(a, b)) if a < b else set(range(a, 1440)) | set(range(0, b))


def window_problem(value: str) -> str | None:
    """D-212: None when `value` (HH:MM-HH:MM CT) lies inside Topstep's hours, 17:00 to 15:10; else why not."""
    span = _window_span(value)
    if span is None:
        return f"trading_window must read HH:MM-HH:MM (CT), got {value!r}"
    a, b = span
    if not (0 <= a < 1440 and 0 <= b < 1440) or a == b:
        return f"trading_window {value!r} is not a window"
    inside = (b <= FLATTEN_MIN or a >= REOPEN_MIN) if a < b else (a >= REOPEN_MIN and b <= FLATTEN_MIN)
    if not inside:
        return (f"trading_window {value!r} crosses Topstep's closed hours: flat by 15:10 CT, trading resumes at 17:00 "
                "(8284206)")
    return None


def execution_problems(fields: dict[str, str], *, band_file: Path = BAND_FILE) -> tuple[list[str], list[str]]:
    """D-212's three rules. (problems, notes)."""
    from propedge.reporting.results import read_result

    problems, notes = [], []
    w = window_problem(fields["trading_window"])
    if w:
        problems.append("D-212: " + w)
    if fields["time_stop"].strip().strip("`*").lower() != "none":
        problems.append(f"D-212: time_stop must be 'none' -- every trade is held to its stop or target -- got "
                        f"{fields['time_stop']!r}")
    stops, problem = _stops(fields.get("stop_distribution", "none: not declared"))
    if problem:
        problems.append("D-212: " + problem)
        return problems, notes
    if stops is None:
        problems.append("D-212: the execution rules need the screen's stop distribution with each entry's exit and date")
        return problems, notes
    band = read_result(band_file)
    by_stop, by_problem = risk_by_stop(fields)
    if by_problem:
        problems.append(by_problem)
        return problems, notes
    if by_stop is not None:                                # D-312 (1): each trade against its own stop's declared risk
        if "state" not in stops.columns:
            problems.append("D-312 (1): a card declaring risk by stop width needs its stops' `state`")
            return problems, notes
        rc = {s: x["risk_ok"] for s, x in by_stop_shares(stops, by_stop, band).items()}
    else:
        rc = risk_consistency(stops, band, card_sizes(fields))
    bad = {s: x for s, x in rc.items() if x < RISK_SHARE}
    if bad:
        problems.append(f"D-212: fewer than {RISK_SHARE:.0%} of the screen's trades realise {1 - RISK_TOLERANCE:.0%} of "
                        "the state's risk in " + ", ".join(f"{s} ({x:.0%})" for s, x in bad.items()))
    else:
        notes.append("D-212 risk met: " + ", ".join(f"{s} {x:.0%} within {RISK_TOLERANCE:.0%}" for s, x in rc.items()))
    if not {"exit", "date"} <= set(stops.columns):
        problems.append("D-212: the stop distribution needs `exit` (target, stop or flatten) and `date` per entry")
        return problems, notes
    unknown = set(stops["exit"].astype(str).str.lower()) - set(EXITS)
    if unknown:
        problems.append(f"D-212: exits must be one of {EXITS}, got {sorted(unknown)}")
        return problems, notes
    fs = flatten_shares(stops)
    over = {k: x for k, x in fs.items() if x > MAX_FLATTEN_SHARE + 1e-12}
    mode = (fields.get("exit_mode") or "").strip().strip("`").lower()
    if mode == FLATTEN_EXEMPT_MODE:
        notes.append(f"D-212 flatten share reported, not enforced ({fs['all']:.1%} reach the flatten; worst "
                     f"{max(fs.values()):.1%}): {FLATTEN_EXEMPT_WHY}")
    elif over:
        problems.append(f"D-212: more than {MAX_FLATTEN_SHARE:.0%} of the screen's trades reach the 15:10 flatten -- "
                        + ", ".join(f"{k} {x:.1%}" for k, x in over.items()))
    else:
        notes.append(f"D-212 resolution met: {fs['all']:.1%} of trades reach the 15:10 flatten, at most "
                     f"{MAX_FLATTEN_SHARE:.0%} in every market and year")
    return problems, notes


def _word(value: str) -> str:
    """The first word of a field's value, lower-cased, emphasis and code ticks stripped ('' if none)."""
    m = re.match(r"([a-z_]+)", re.sub(r"[*`]", "", value or "").strip().lower())
    return m.group(1) if m else ""


def _declared(fields: dict[str, str], key: str) -> str | None:
    """A field's value, or None when it is absent or a placeholder."""
    value = fields.get(key)
    return None if value is None or _is_placeholder(value) else value


def declaration_problems(fields: dict[str, str]) -> tuple[list[str], list[str]]:
    """D-266's execution declaration: manual, the latency L, the missed-trigger policy of a resting entry, the hours.
    (problems, notes)."""
    problems, notes = [], []
    execution = _word(fields["execution"])
    if execution not in EXECUTIONS:
        problems.append(f"D-266: execution must be one of {EXECUTIONS}, got {fields['execution']!r}")
    elif execution != "manual":
        problems.append("D-266: execution is manual -- the operator trades every signal by hand; an automated model "
                        "needs its own decision before its card")
    latency = _number(fields["latency_minutes"])
    if latency is None or latency <= 0:
        problems.append("D-266: latency_minutes, L from the signal to a working order, is a positive number for manual "
                        f"execution, got {fields['latency_minutes']!r}")
    elif latency + 1e-9 < SEATED_LATENCY.get(re.sub(r"[*`]", "", fields.get("model", "")).strip().upper(),
                                             OPERATOR_LATENCY_MINUTES):
        floor = SEATED_LATENCY.get(re.sub(r"[*`]", "", fields.get("model", "")).strip().upper(), OPERATOR_LATENCY_MINUTES)
        problems.append(f"D-266: every model is scored at the operator's latency, {floor:g} minutes; a card may declare "
                        f"more, never less (got {latency:g})")
    value = _declared(fields, "missed_trigger_policy")
    policy = _word(value) if value is not None else None
    resting = _word(fields.get("entry_type", "")) in RESTING_ENTRY_TYPES
    if policy is not None and policy not in MISSED_TRIGGER_POLICIES:
        problems.append(f"D-266: missed_trigger_policy must be one of {MISSED_TRIGGER_POLICIES}, got {value!r}")
    elif policy is None and resting and execution == "manual":
        problems.append("D-266: a resting stop or limit entry traded by hand declares its missed_trigger_policy -- a "
                        "trigger before the order works is skipped, left resting at its level or chased at the market "
                        "-- before any run")
    hours = re.sub(r"[*`]", "", fields["trading_hours"]).strip().lower()
    if not hours.startswith(UNCONSTRAINED_HOURS):
        span = _window_span(hours)
        if span is None or not (0 <= span[0] < 1440 and 0 <= span[1] < 1440) or span[0] == span[1]:
            problems.append("D-266: trading_hours is 'unconstrained' (the operator's: no hours constraint) or a window "
                            f"HH:MM-HH:MM CT, got {fields['trading_hours']!r}")
        else:
            model = _window_span(fields.get("trading_window", ""))
            if model is not None and not _window_minutes(*model) <= _window_minutes(*span):
                problems.append(f"D-266: the trading_window {fields['trading_window']!r} falls outside the hours the "
                                f"operator can trade ({fields['trading_hours']!r}); an order placed by hand needs the "
                                "operator there")
    if not problems:
        notes.append(f"D-266 met: manual, L = {latency:g} minutes (results at L = 0 and at L, the verdict at L), "
                     f"missed triggers {policy or 'not applicable (no resting entry)'}, hours {hours}")
    return problems, notes


def era_problems(body: str, fields: dict[str, str], *, model: str, setups: float | None, accounts: float | None,
                 layout: str) -> tuple[list[str], list[str]]:
    """D-271's section states each of its rules (presence only, never a number's value), and D-269's coordination is
    declared, and consistent, where the model has several entries a day. (problems, notes)."""
    problems, notes = [], []
    absent = [label for label, patterns in D271_ELEMENTS
              if not all(re.search(p, body or "", re.IGNORECASE) for p in patterns)]
    if absent:
        problems.append("D-271: the eras section does not state " + "; ".join(absent))
    value = _declared(fields, "coordination")
    if value is None:
        if setups is not None and setups > 1:
            problems.append("D-269: a model with several entries a day declares its coordination -- one_at_a_time "
                            "(D-160) or, ORB5's option beside it, own_account (each entry to its own free account, "
                            "direction-locked)")
    else:
        options = [o for o in COORDINATIONS if re.search(rf"\b{o}\b", value.lower())]
        if not options:
            problems.append(f"D-269: coordination must be among {COORDINATIONS}, got {value!r}")
        elif "own_account" in options:
            if model not in COORDINATION_OPTION_MODELS:
                problems.append(f"D-269: own_account is ORB5's declared option; D-160's one position at a time stays "
                                f"the rule for other models ({model})")
            if accounts is None or accounts <= 1 or layout != "rotation":
                problems.append("D-269: own_account sends each entry to the next free account, so it needs more than "
                                "one account in rotation (D-157)")
    if not problems:
        notes.append("D-271 section states every rule" + (f"; coordination {value.strip()}" if value else ""))
    return problems, notes


def _by_market(value: str) -> dict[str, float] | None:
    """'ES 3, CL 2.5' -> {'ES': 3.0, 'CL': 2.5}; None if any part does not read as a market and a number."""
    out = {}
    for part in (p.strip() for p in (value or "").split(",") if p.strip()):
        m = re.fullmatch(r"([A-Za-z0-9]+)\s*[:=]?\s*(-?\d+(?:\.\d+)?)", part)
        if not m:
            return None
        out[m.group(1).upper()] = float(m.group(2))
    return out or None


def candidate_record_problems(fields: dict[str, str], markets: list[str], *, need: float | None, accounts: float,
                              layout: str, band_file: Path = BAND_FILE) -> tuple[list[str], list[str]]:
    """D-191's step 0: the candidate record's fields and the computed prop-fit score. (problems, notes)."""
    from propedge import REPO_ROOT
    from propedge.campaign.conduct import leg_findings
    from propedge.reporting.results import read_result
    from propedge.research.stop_band import MAX_OUTSIDE

    problems, notes = [], []
    rec = fields["candidate_record"].strip().strip("`")
    path = Path(rec) if Path(rec).is_absolute() else REPO_ROOT / rec
    if not path.is_file():
        problems.append(f"D-191: candidate_record {rec!r} is not a file")
    else:
        try:
            table = read_result(path)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(f"D-191: candidate_record {rec!r} does not verify against its manifest: {exc}")
        else:
            key = fields["atlas_row"].strip().strip("`")
            mk, _, test = key.partition(":")
            if test and {"market", "test"} <= set(table.columns):
                found = bool(((table["market"].astype(str) == mk) & (table["test"].astype(str) == test)).any())
            else:
                found = bool(table.astype(str).apply(lambda col: col.str.fullmatch(re.escape(key))).any().any())
            if not found:
                problems.append(f"D-191: atlas_row {key!r} is not a row of {path.name}")
    grade = fields["mechanism_grade"].strip().strip("`*").upper()[:1]
    if grade not in GRADES:
        problems.append(f"D-191: mechanism_grade must be one of {GRADES}, got {fields['mechanism_grade']!r}")
    if _number(fields["screen_k"]) is None or _number(fields["screen_k"]) < 1:
        problems.append(f"D-191: screen_k must be a number of at least 1, got {fields['screen_k']!r}")

    fit = []                                                       # the prop-fit score's failures
    by = _by_market(fields["setups_by_market"])
    if by is None or set(by) != {m.strip().upper() for m in markets}:
        problems.append(f"D-191: setups_by_market must give each of the card's markets ({', '.join(markets)}) a number, "
                        f"got {fields['setups_by_market']!r}")
    elif need is not None and need == need:                    # pooled, D-154's own check above covers it
        met = [m for m, x in by.items() if x + 1e-9 >= need]
        required = math.ceil(SHARE_OF_MARKETS * len(by) - 1e-9)
        if len(met) < required:
            fit.append(f"D-154 by market: {len(met)} of {len(by)} markets reach {need:g} a day on their own, "
                       f"{required} needed")
    stops, problem = _stops(fields.get("stop_distribution", "none: not declared"))
    if problem:
        fit.append(problem)
    elif stops is None:
        fit.append("the zero-micro share needs the screen's stop distribution (D-190); none is given")
    else:
        band, sizes = read_result(band_file), card_sizes(fields)
        by_stop, _ = risk_by_stop(fields)                      # its problem, if any, is the validator's (once)
        if by_stop is not None and "state" in stops.columns:   # D-312 (1): each trade at its own stop's declared risk
            zero = {s: x["unsizeable"] for s, x in by_stop_shares(stops, by_stop, band).items()}
        elif sizes and "state" in stops.columns:               # D-242: the card's own states and sizes
            band = card_band(band, sizes)
            zero = unsizeable_shares(stops, band)
        else:
            zero = unsizeable_shares(stops, band)
        bad = {s: x for s, x in zero.items() if x > MAX_OUTSIDE}
        if bad:
            fit.append("D-190: " + ", ".join(f"{s} {x:.0%}" for s, x in bad.items()) + " unsizeable")
    t1 = fields["conduct_tier1"].strip().strip("`*").lower()
    if t1 != "none":
        fit.append(f"tier 1 must be declared 'none', got {fields['conduct_tier1']!r}")
    findings1, findings2 = [], []
    for name, rr, risk, funded in (("combine", fields.get("combine_rr"), fields.get("combine_risk"), False),
                                   ("funded", fields.get("funded_rr"), fields.get("funded_risk"), True)):
        a, b = leg_findings(name, _number(rr), _number(risk) or 0.0, funded=funded)
        findings1 += a
        findings2 += b
    if findings1:
        fit.append("tier 1 on the card's sizes: " + "; ".join(findings1))
    t2 = fields["conduct_tier2"].strip().strip("`*").lower()
    if findings2 and t2 == "none":
        fit.append("tier 2 flags raised by the card's sizes are not declared: " + "; ".join(findings2))
    if "priced" not in fields["conduct_tier3"].lower():
        fit.append(f"tier 3 must be declared priced, got {fields['conduct_tier3']!r}")
    if fit:
        problems.append("D-191: the prop-fit score fails -- " + " | ".join(fit))
    else:
        notes.append(f"D-191 prop-fit passes (grade {grade}, screen k {fields['screen_k'].strip()})")
    return problems, notes


def validate_card(source: str | Path, *, for_prereg: bool = False, setups_file: Path = SETUPS_FILE,
                  band_file: Path = BAND_FILE) -> CardValidation:
    """Check a model card (a path or its text). `for_prereg` also requires the screen to have said continue."""
    path = None
    if isinstance(source, Path) or (isinstance(source, str) and "\n" not in source and source.endswith(".md")):
        p = Path(source)
        if not p.is_file():
            raise FileNotFoundError(f"model card not found: {p}")
        path, text = str(p), p.read_text(encoding="utf-8")
    else:
        text = str(source)
    v = CardValidation(path=path)
    v.fields = _parse_fields(text)
    for key, why in REQUIRED_FIELDS:
        value = v.fields.get(key)
        if value is None or _is_placeholder(value):
            v.missing.append(f"{key} ({why})")
        elif key in NUMERIC and _number(value) is None:
            v.problems.append(f"{key} must be a number, got {value!r}")
    model = (v.fields.get("model") or "").strip().strip("`")
    d201 = model not in PRE_D201
    if d201:
        for key, why in D201_FIELDS:
            value = v.fields.get(key)
            if value is None or _is_placeholder(value):
                v.missing.append(f"{key} ({why}; D-201)")
    else:
        v.notes.append(f"{model} pre-dates D-201: no Entry, Stop and Exit sections or stop band required")
    d191 = model not in PRE_D191
    if d191:
        for key, why in D191_FIELDS:
            value = v.fields.get(key)
            if value is None or _is_placeholder(value):
                v.missing.append(f"{key} ({why}; D-191)")
    else:
        v.notes.append(f"{model} is a pre-door entry (D-155): no candidate record or grade required (D-191)")
    d212 = model not in PRE_D212
    if d212:
        for key, why in D212_FIELDS:
            value = v.fields.get(key)
            if value is None or _is_placeholder(value):
                v.missing.append(f"{key} ({why}; D-212)")
    d266 = model not in PRE_D266
    if d266:
        for key, why in D266_FIELDS:
            value = v.fields.get(key)
            if value is None or _is_placeholder(value):
                v.missing.append(f"{key} ({why}; D-266)")
    else:
        v.notes.append(f"{model} pre-dates D-266: no execution declaration required")
    d271 = model not in PRE_D271
    if not d271:
        v.notes.append(f"{model} pre-dates D-271: no eras and today's economics section required")
    sections = _section_bodies(text)
    bodies = {}
    for name, why in REQUIRED_SECTIONS + (D201_SECTIONS if d201 else ()) + (D271_SECTIONS if d271 else ()):
        body = next((b for h, b in sections.items() if name in h), None)
        if body is None or len(re.sub(r"[\s*_>|\-]", "", body)) < 40:
            v.missing.append(f"section '{name}' ({why})")
        bodies[name] = body or ""
    if d201 and bodies.get("stop") and "stop_band" not in bodies["stop"]:
        v.problems.append("D-201: the Stop section cites the sizeable stop band (results/stop_band.csv) and says where "
                          "the stops fall in it")
    if v.missing:
        return v

    f = {k: v.fields[k] for k, _ in REQUIRED_FIELDS}
    layout = f["layout"].strip().lower()
    if layout not in LAYOUTS:
        v.problems.append(f"layout must be one of {LAYOUTS}, got {f['layout']!r}")
    verdict = f["screen_verdict"].strip().lower()
    if verdict not in ("continue", "kill"):
        v.problems.append(f"screen_verdict must be continue or kill, got {f['screen_verdict']!r}")
    elif verdict == "kill" and for_prereg:
        v.problems.append("the cheap screen killed this model; a killed model is not pre-registered (D-155)")

    rows = _parameter_rows(bodies["parameters"])
    if not rows:
        v.problems.append("the parameters table has no rows")
    for cells in rows:
        if cells[2].strip().strip("*`").lower() not in CLASSES:
            v.problems.append(f"parameter {cells[0]!r} has class {cells[2]!r}; each is one of {CLASSES}")
        if _is_placeholder(cells[3]):
            v.problems.append(f"parameter {cells[0]!r} has no source")
    k = _number(f["k"])
    if any(c[2].strip().strip("*`").lower() == "searched" for c in rows) and k is not None and k <= 1:
        v.problems.append("a searched parameter means more than one variant, so k must be above 1")

    rr, risk, edge = _number(f["combine_rr"]), _number(f["combine_risk"]), _number(f["edge_assumed"])
    setups, accounts = _number(f["setups_per_day"]), _number(f["accounts"])
    if d201:
        entry_type = v.fields["entry_type"].strip().strip("`").lower()
        if entry_type not in ENTRY_TYPES:
            v.problems.append(f"entry_type must be one of {ENTRY_TYPES}, got {v.fields['entry_type']!r}")
        elif entry_type == "wait":                             # D-201 (3): a fixed wait, and only filled setups count
            wait, rate = _number(v.fields.get("max_wait_bars", "")), _number(v.fields.get("fill_rate", ""))
            if wait is None or wait <= 0:
                v.problems.append("D-201: a wait-for-entry rule declares max_wait_bars, a fixed execution parameter")
            if rate is None or not 0 < rate <= 1:
                v.problems.append("D-201: a wait-for-entry rule declares its screen's fill_rate within the wait, "
                                  "between 0 and 1")
            elif setups is not None:
                v.notes.append(f"D-201: {setups:g} signals a day x fill rate {rate:g} = {setups * rate:.2f} setups")
                setups = setups * rate
        by_stop, by_problem = risk_by_stop(v.fields)          # D-312 (1): risk declared by stop width
        if by_problem:
            v.problems.append(by_problem)
        problems, notes = band_problems(v.fields["stop_distribution"], band_file, card_sizes(v.fields), by_stop)
        v.problems += problems
        v.notes += notes
        stops_bs, _ = _stops(v.fields["stop_distribution"]) if by_stop is not None else (None, None)
        if by_stop is not None and stops_bs is not None and "state" in stops_bs.columns:
            from propedge.reporting.results import read_result

            decl = by_stop_declaration_problems(v.fields, by_stop, stops_bs, read_result(band_file))
            v.problems += decl
            if not decl:
                v.notes.append("D-312 (1): each state's risk declared by stop width is what the full allowance carries "
                               f"({', '.join(f'{s} {n} micros' for s, n in full_allowance().items())})")
    markets = [m for m in re.sub(r"\(.*?\)", "", f["markets"]).split(",") if m.strip()]
    if layout == "copier" and accounts is not None and accounts > 1:
        v.problems.append("D-157: copying every trade to every account makes the accounts one bet; a card that feeds "
                          "more than one account spreads its trades across them (rotation or partitioned)")
    need = setups_minimum(rr, risk, edge, setups_file)
    if need is None:
        v.problems.append(f"the Combine size {rr:g}:1 at ${risk:,.0f} is not in {setups_file.name}; add it to "
                          "scripts/setups_per_day.py (its sizes come from stage one) before declaring (D-154)")
    elif need != need:                                          # NaN: no tabulated frequency reaches it
        v.problems.append(f"no tabulated frequency resolves a {rr:g}:1 ${risk:,.0f} Combine inside a billing period")
    elif setups is None:                                        # a draft whose setups are pending
        v.notes.append("D-154: setups_per_day pending -- checked when the card is completed")
    else:
        total = setups * max(len(markets), 1)                   # setups a day across every market the card trades
        per_account = total if layout == "copier" else total / max(accounts, 1.0)
        if per_account + 1e-9 < need:
            v.problems.append(
                f"D-154: each account sees {per_account:.2f} setups a day ({total:g} across {len(markets)} market(s), "
                f"{layout}, {accounts:g} accounts) but a {rr:g}:1 ${risk:,.0f} Combine needs at least {need:g} at "
                f"edge {edge:g} ({setups_file.name})")
        else:
            v.notes.append(f"D-154 met: {per_account:.2f} setups a day per account against a minimum of {need:g}")
    if d191:
        problems, notes = candidate_record_problems(v.fields, markets, need=need, accounts=accounts or 1.0,
                                                    layout=layout, band_file=band_file)
        v.problems += problems
        v.notes += notes
    if d212:
        problems, notes = execution_problems(v.fields, band_file=band_file)
        v.problems += problems
        v.notes += notes
    if d266:
        problems, notes = declaration_problems(v.fields)
        v.problems += problems
        v.notes += notes
    if d271:
        problems, notes = era_problems(bodies["eras"], v.fields, model=model, setups=_number(f["setups_per_day"]),
                                       accounts=accounts, layout=layout)
        v.problems += problems
        v.notes += notes
    return v


__all__ = ["CardValidation", "REQUIRED_FIELDS", "REQUIRED_SECTIONS", "PRE_D201", "D201_FIELDS", "D201_SECTIONS",
           "PRE_D191", "D191_FIELDS", "GRADES", "PRE_D212", "D212_FIELDS", "PRE_D266", "D266_FIELDS", "EXECUTIONS",
           "MISSED_TRIGGER_POLICIES", "PRE_D271", "D271_SECTIONS", "D271_ELEMENTS", "COORDINATIONS", "setups_minimum",
           "unsizeable_shares", "card_sizes", "BY_STOP_FIELDS", "risk_by_stop", "full_allowance", "by_stop_shares",
           "by_stop_declaration_problems", "card_band", "band_problems", "candidate_record_problems",
           "risk_consistency", "flatten_shares", "window_problem", "execution_problems", "declaration_problems",
           "era_problems", "validate_card"]
