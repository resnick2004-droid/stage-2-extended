"""Manual-run kits for QuantConnect's free web editor (D-81, D-82).

A kit is a folder `runs/<run-id>/` holding everything a person needs to run one backtest by hand
and bring it back:

  main.py       the algorithm, generated from the template with the confirmation-window guard
                embedded. Pasted into the web editor unchanged.
  RUN.md        exact steps: project name, paste, settings, Backtest, what to download and where
  EXPECTED.md   what the outputs should look like, and what would make the run unusable
  kit.json      the machine-readable record `scripts/ingest_manual_run.py` checks against

Generate with `python scripts/make_run_kit.py <run-id>` (or `--all`), then **commit the kit before
running it**: ingestion refuses a result whose algorithm does not match a committed file.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

from propedge import REPO_ROOT
from propedge.data import qc_algorithms as alg
from propedge.data.manual_runs import normalised_hash
from propedge.data.qc_template import render_algorithm
from propedge.data.window import D144_DEVELOPMENT_END, DEVELOPMENT_END, PREVIOUS_DEVELOPMENT_END

RUNS_DIR = REPO_ROOT / "runs"
DOWNLOADS = "downloads"          # inside each kit; git-ignored -- vendor output, hashed on ingest


@dataclass(frozen=True)
class Download:
    name: str                    # file name under runs/<id>/downloads/
    how: str                     # the click path in the web editor


LOGS = Download("logs.txt", "backtest results page → **Logs** tab → **Download Logs**")
RESULTS = Download("results.json",
                   "backtest results page → **Overview** tab → **Download Results**")
RAN_CODE = Download("ran_main.py",
                    "after the backtest, in the editor: click in `main.py`, select all, copy, and "
                    "paste into a new file saved as this name. It proves which code ran.")


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    title: str
    purpose: str
    class_name: str
    start: date
    end: date
    body: str
    preamble: str
    downloads: tuple[Download, ...]
    parser: str                  # which parser in scripts/ingest_manual_run.py reads it
    expected: str                # Markdown body of EXPECTED.md
    extra: dict = field(default_factory=dict)
    prereg_id: str | None = None # only a confirmation run carries one (D-81)

    @property
    def project_name(self) -> str:
        return f"propedge-{self.run_id}"

    @property
    def boundary(self) -> date:
        """The confirmation start embedded in the kit: the one it was made under (D-144)."""
        if self.run_id in KITS_BEFORE_D144:
            return PREVIOUS_DEVELOPMENT_END
        return D144_DEVELOPMENT_END if self.run_id in KITS_BEFORE_D237 else DEVELOPMENT_END

    def code(self) -> str:
        return render_algorithm(name=self.class_name, start=self.start, end=self.end,
                                body=self.body, preamble=self.preamble,
                                prereg_id=self.prereg_id, boundary=self.boundary)


#: Every kit made before D-144 moved the confirmation boundary to 2020-01-01. Each embeds the
#: 2014-05-28 boundary it was made (and, where run, ran) under, so the committed kit stays
#: byte-identical to the code that ran. Explicit, never computed: a new kit is not on this list.
KITS_BEFORE_D144 = frozenset({
    "R001-dataset-checks", "R002-recon-A", "R003-recon-B", "R004-recon-C", "R005-gc-coverage",
    "R006-recon-A2", "R007-recon-B2", "R008-recon-C2", "R009-leg-GC", "R013-leg-GC2", "R014-leg-CL2",
    "R015-leg-6E2", "R016-leg-ES2", "R017-leg-GC3", "R018-conf-GC1", "R019-conf-GC2", "R020-conf-CL1",
    "R021-conf-CL2", "R022-conf-6E1", "R023-conf-6E2", "R024-conf-ES1", "R025-conf-ES2", "R026-gap-ES",
    "R027-gap-ES2", "R028-openrev-rescore", "R029-openrev-NQ", "R030-atlas-ES", "R031-atlas-NQ",
    "R032-atlas-CL", "R033-atlas-GC", "R034-atlas-6E", "R035-atlas-ZN", "R036-data-extras",
    "R037-data-options", "R038-atlas-context", "R039-gamma-diagnostic", "R040-atlas-context2",
    "R041-atlas-GC2", "R042-atlas-GC3", "R043-atlas-ZN3", "R044-zn-grid-check", "R045-fv1-NQ",
    "R046-fv1-ES",
})


#: Every kit made after D-144 and before D-237 moved the boundary to 2025-07-01 (R047-R088). Each embeds D-144's
#: 2020-01-01 boundary it was made (and, where run, ran) under. Explicit, never computed: a new kit is not on this list.
KITS_BEFORE_D237 = frozenset({
    "R047-fv1-NQ-1419", "R048-fv1-ES-1419", "R049-bmap-NQ-0914", "R050-bmap-NQ-1419", "R051-bmap-ES-0914",
    "R052-bmap-ES-1419", "R053-im2-ES-0914", "R054-im2-ES-1419", "R055-im2-CL-0914", "R056-im2-CL-1419",
    "R057-im2-6E-0914", "R058-im2-6E-1419", "R059-im2-NG-0914", "R060-im2-NG-1419", "R061-release-ES",
    "R062-release-ZN", "R063-im2x-ES-0914", "R064-im2x-ES-1419", "R065-im2x-CL-0914", "R066-im2x-CL-1419",
    "R067-im2x-6E-0914", "R068-im2x-6E-1419", "R069-im2x-NG-0914", "R070-im2x-NG-1419", "R071-rmap-ES-0914",
    "R072-rmap-ES-1419", "R073-rmap-NQ-0914", "R074-rmap-NQ-1419", "R075-rmap-CL-0914", "R076-rmap-CL-1419",
    "R077-rmap-6E-0914", "R078-rmap-6E-1419", "R079-rmap-NG-0914", "R080-rmap-NG-1419", "R081-rmap-NG-0914",
    "R082-rmap-today-ES-0914", "R083-rmap-today-ES-1419", "R084-rmap-today-NQ-0914", "R085-rmap-today-NQ-1419",
    "R086-rmap-today-CL-0914", "R087-rmap-today-CL-1419", "R088-rmap-confirm-NQ-2026",
})


# ------------------------------------------------------------------ the specs

_DATASET_EXPECTED = f"""\
The **Logs** download holds a handful of lines beginning `{alg.DATASET_PREFIX}|`, all written at the
end of the backtest. LEAN adds lines of its own, which the parser ignores.

| line | meaning |
|---|---|
| `{alg.DATASET_PREFIX}\\|HEAD\\|…\\|defaults=…\\|errors=…` | QuantConnect's default continuous-contract settings; `errors=none` if every symbol was added |
| `{alg.DATASET_PREFIX}\\|SYM\\|<ticker>\\|bars=N\\|first=…\\|period=…\\|config=…` | one per symbol: minute bars received, the first bar's time, its period, and the roll settings actually applied |
| `{alg.DATASET_PREFIX}\\|ROLL\\|<ticker>\\|n=K\\|date:contract,…` | one per future: each roll in the span |
| `{alg.DATASET_PREFIX}\\|END\\|…\\|truncated=false` | **must be present and say `truncated=false`** |

**Plausible values, not targets.** Nothing below is a pass mark. The run records what QuantConnect
has, whatever that is.
- `bars` > 0 for SPY and each future. A future with `bars=0` is either absent from the dataset or
  not entitled to this account; the ingestion records it as *no data received*, not as *absent*.
- `period=0:01:00` (or `00:01:00`) everywhere: minute resolution.
- `first` for the futures in or near **May 2009** (D-39's approximation). A first bar on
  {alg.DATASET_START.isoformat()}, the start date, means the data begins **on or before** it.
- `config` shows the mapping mode, normalisation mode and contract depth offset QuantConnect
  applies by default. That is the roll rule this run reads.

**The run is unusable** if the `END` line is missing, if it says `truncated=true`, or if the
backtest stopped with an error. Say which, and count it as a fix-and-rerun round.
"""


def _dataset_spec() -> RunSpec:
    return RunSpec(
        run_id="R001-dataset-checks",
        title="Dataset checks",
        purpose=("SPY in US Equities; ES, NQ, GC, CL, 6E, ZN, HG, NG in US Futures; each "
                 "contract's first available date; the continuous-contract roll rule; minute "
                 "resolution. One compact algorithm on data before 2014-05-28."),
        class_name="DatasetChecks",
        start=alg.DATASET_START, end=alg.DATASET_END,
        body=alg.DATASET_BODY, preamble=alg.DATASET_PREAMBLE,
        downloads=(LOGS, RAN_CODE),
        parser="dataset_checks",
        expected=_DATASET_EXPECTED,
    )


_COVERAGE_EXPECTED = f"""\
R001 received **no GC or HG bars** in {alg.DATASET_START.isoformat()} → {alg.DATASET_END.isoformat()}.
This run asks again over {alg.COVERAGE_START.isoformat()} → {alg.COVERAGE_END.isoformat()}, the rest of
the development period. GC is a C-007 leg, so the answer decides whether C-007 can be measured on
QuantConnect's data at all.

The **Logs** download has the same `{alg.DATASET_PREFIX}|` lines as R001, for SPY, GC, HG and ES.
**ES is the control**: if ES also shows `bars=0`, the run read nothing and is unusable.

What the lines can say about GC and HG, and none of these is a pass mark:
- `bars` > 0 and a `first` date: data exists from that date (a first bar on
  {alg.COVERAGE_START.isoformat()} means **on or before** it);
- `bars=0`: no data received anywhere in the development period, recorded as *no data received*.
  That still does not prove the dataset lacks the contract; it may not be available to this
  account, or it may start after 2014-05-27, which this run is not allowed to read.

**The run is unusable** if the `END` line is missing or says `truncated=true`, if the backtest
stopped with an error, or if ES received no bars.
"""


def _coverage_spec() -> RunSpec:
    return RunSpec(
        run_id="R005-gc-coverage",
        title="GC and HG coverage",
        purpose=(f"GC and HG in US Futures over {alg.COVERAGE_START} to {alg.COVERAGE_END}, after R001 "
                 "received none of either; ES as the control; data before 2014-05-28 only."),
        class_name="CoverageChecks",
        start=alg.COVERAGE_START, end=alg.COVERAGE_END,
        body=alg.COVERAGE_BODY, preamble=alg.COVERAGE_PREAMBLE,
        downloads=(LOGS, RAN_CODE),
        parser="coverage_checks",
        expected=_COVERAGE_EXPECTED,
        extra={"log_budget_bytes": alg.COVERAGE_LOG_BUDGET_BYTES},
    )


#: The propedge fill profile each stage is configured from and compared against (D-83). Stage C
#: runs LEAN's defaults and is compared against stage A's profile: it must disagree.
RECON_PROFILE = {"A": "zero_cost_gap_fill", "B": "assumed", "C": "zero_cost_gap_fill"}


def _recon_inputs(mode: str) -> dict:
    """Tick size, slippage and fees for each mode, from configuration -- never typed."""
    from propedge.data.qc_provenance import config_fingerprint
    from propedge.execution.fills import FillModel
    from propedge.execution.instruments import get_instrument

    es = get_instrument("ES")
    zero = {"entry": 0.0, "stop": 0.0, "target": 0.0, "flatten": 0.0}
    if mode == "C":
        return dict(tick_size=es.tick_size, slip=zero, fee_per_side=0.0,
                    cost_model={"profile": "LEAN defaults + ConstantSlippageModel(0.0001)",
                                "compared_against": RECON_PROFILE["A"]})
    fm = FillModel.load(RECON_PROFILE[mode])
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks,
            "target": fm.target_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    fee = fm.commission_for(1, "ES") / 2.0
    cm = {"profile": fm.name, **slip, "fee_per_side": fee,
          "gap_through_stop": fm.gap_through_stop}
    return dict(tick_size=es.tick_size, slip=slip, fee_per_side=fee, cost_model=cm,
                fingerprint=config_fingerprint(cm))


_RECON_EXPECTED = {
    "A": "zero cost. Every fill is at the intended price, or at the bar's open when a bar opens "
         "through the stop. `fee=0` on every trade.",
    "B": "costs on: adverse slippage in ticks and the per-side fee from `config/fills.yaml` on "
         "every fill.",
    "C": "LEAN's defaults. This is the **negative control**: the comparison must find "
         "disagreements (touch-filled targets, fraction-of-price slippage, the gap handling). A "
         "stage C run that agrees with our model has not shown the comparison works.",
}


def _recon_spec(mode: str) -> RunSpec:
    n = {"A": 2, "B": 3, "C": 4}[mode]
    inputs = _recon_inputs(mode)
    expected = f"""\
Stage **{mode}** of the `docs/PIPELINE.md` §5 reconciliation (D-80): {_RECON_EXPECTED[mode]}

**Logs** holds three lines beginning `{alg.RECON_PREFIX}|`:
`HEAD` (mode, number of trades, exits by reason), `LAST` (the final trade's evidence) and
`END`. Expect roughly one trade per trading day in the year, ending `stop`, `target`, `flatten`
or `flatten_close` (an early close).

**Download Results** (`results.json`) carries the per-trade evidence in the **order tags**. Each
entry order's tag holds the previous trade's record (`prev=`…): entry and exit fills, stop and
target, exit reason, the highest high and lowest low **before** the exit bar, and the exit bar
itself. The comparison with `propedge` reads these tags.

**The run is unusable** if `END` is missing, if the backtest stopped with an error, or if the
number of trades in `HEAD` is far below the number of trading days (the entry never fired).
"""
    return RunSpec(
        run_id=f"R00{n}-recon-{mode}",
        title=f"Reconciliation stage {mode}",
        purpose=f"docs/PIPELINE.md section 5, stage {mode}, on ES {alg.RECON_START} to "
                f"{alg.RECON_END} (D-80).",
        class_name=f"Reconciliation{mode}",
        start=alg.RECON_START, end=alg.RECON_END,
        body=alg.RECON_BODY,
        preamble=alg.recon_preamble(mode=mode, tick_size=inputs["tick_size"],
                                    slip=inputs["slip"], fee_per_side=inputs["fee_per_side"]),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="reconciliation",
        expected=expected,
        extra={"mode": mode, "cost_model": inputs["cost_model"],
               "config_fingerprint": inputs.get("fingerprint")},
    )


#: Reconciliation v2 (D-94): one price series (trade bars) everywhere; stage C runs planted faults.
RECON_V2_RUNS = {"A": "R006-recon-A2", "B": "R007-recon-B2", "C": "R008-recon-C2"}

_RECON_V2_EXPECTED = {
    "A": "zero cost. Every fill is at the intended price, or at the trade bar's open when a bar "
         "opens through the stop. `fee=0` on every trade.",
    "B": "costs on: adverse slippage in ticks and the per-side fee from `config/fills.yaml` on "
         "every fill.",
    "C": "planted faults. This is the **negative control** (D-94): the fill model deliberately "
         "fills a target on a touch (`flt=touch`), fills a gapped stop at the stop price "
         "(`flt=gapstop`), and fills every entry with fraction-of-price slippage. The comparison "
         "must flag every labelled fault. A gap-through-stop may not occur in the year; that is "
         "recorded as *not exercised*, not as caught.",
}


def _recon_v2_inputs(mode: str) -> dict:
    """As `_recon_inputs`, but stage C is zero cost plus planted faults, not LEAN's defaults."""
    if mode != "C":
        return _recon_inputs(mode)
    from propedge.execution.instruments import get_instrument

    zero = {"entry": 0.0, "stop": 0.0, "target": 0.0, "flatten": 0.0}
    return dict(tick_size=get_instrument("ES").tick_size, slip=zero, fee_per_side=0.0,
                cost_model={"profile": "planted faults: touch, gapstop, "
                                       f"frac={alg.RECON_C_FRACTION}",
                            "compared_against": RECON_PROFILE["A"]})


def _recon_v2_spec(mode: str) -> RunSpec:
    inputs = _recon_v2_inputs(mode)
    expected = f"""\
Stage **{mode}** of the `docs/PIPELINE.md` §5 reconciliation, version 2 (D-80, D-94):
{_RECON_V2_EXPECTED[mode]}

Version 2 reads **one price series**, the contract's trade bars, for every fill and every record
(D-93 found version 1 mixed trade bars with quote midpoints). Every recorded price except the
entry fill in stage C must therefore sit on the 0.25 tick grid; the comparison refuses a run where
one does not.

**Logs** holds three lines beginning `{alg.RECON_PREFIX}|`:
`HEAD` (`v=2`, mode, number of trades, exits by reason, `nobar` = slices with no trade bar yet),
`LAST` (the final trade's evidence) and `END`. Expect roughly one trade per trading day in the
year, ending `stop`, `target`, `flatten` or `flatten_close` (an early close).

**Download Results** (`results.json`) carries the per-trade evidence in the **order tags**. Each
entry order's tag holds the previous trade's record (`prev=`…): entry and exit fills, stop and
target, exit reason, the highest high and lowest low **before** the exit bar, the exit bar itself
and its end time (`xbt`), and any planted fault that decided the exit (`flt`).

**The run is unusable** if `END` is missing, if the backtest stopped with an error, or if the
number of trades in `HEAD` is far below the number of trading days (the entry never fired).
"""
    return RunSpec(
        run_id=RECON_V2_RUNS[mode],
        title=f"Reconciliation v2 stage {mode}",
        purpose=f"docs/PIPELINE.md section 5, stage {mode}, version 2 (D-94), on ES "
                f"{alg.RECON_START} to {alg.RECON_END} (D-80).",
        class_name=f"ReconciliationV2{mode}",
        start=alg.RECON_START, end=alg.RECON_END,
        body=alg.RECON_BODY_V2,
        preamble=alg.recon_preamble_v2(mode=mode, tick_size=inputs["tick_size"],
                                       slip=inputs["slip"], fee_per_side=inputs["fee_per_side"]),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="reconciliation",
        expected=expected,
        extra={"mode": mode, "version": 2, "cost_model": inputs["cost_model"],
               "config_fingerprint": inputs.get("fingerprint")},
    )


V2_NOTE = """\
**Version 2 (D-98).** The kit chooses its own contract: at each settlement bar it takes, for the next
session, the contract that traded the most volume since the previous settlement. `HEAD` also reports
`switches`, the number of contract changes. Few `roll` skips are expected; `noprev` marks a day whose
new contract had no same-day price at the switch.

"""

#: C-007 leg evidence for the D-43 sd measurement (D-97), one kit per leg.
LEG_RUNS = {"GC": "R009-leg-GC"}          # v1: only R009 ran; R010-R012 were retired unrun (D-98)
#: Version 2 (D-98): the kit chooses its own contract by prior-session volume.
LEG_V2_RUNS = {"GC": "R013-leg-GC2", "CL": "R014-leg-CL2", "6E": "R015-leg-6E2", "ES": "R016-leg-ES2"}


def _leg_spec(market: str, version: int = 1, *, filter_days: int | None = None,
              run_id: str | None = None) -> RunSpec:
    entry, exit_ = alg.LEG_WINDOWS[market]
    start = alg.LEG_START[market]
    expected = f"""\
Evidence for the D-43 sd measurement of Stage 2B's C-007, **{market} leg**: every development day
from {start} to {alg.LEG_END}, window {entry}–{exit_} CT (exit = the leg's CME settlement, D-50).
Nothing is tested here and no edge is estimated. The kit records prices; the volatility forecast,
stop, sizing and costs are applied in the repository (D-97).

**Logs** holds three lines beginning `{alg.LEG_PREFIX}|`: `HEAD` (market, number of days with an
entry bar, skips by reason: `noprev` no previous settlement yet, `roll` the contract changed since
it, `stale` it is over five days old, `unclosed` the last window never closed), `LAST` (the final
day's record) and `END`. Expect roughly one day per trading day in the span, fewer on holidays and
early closes, a handful of `roll` skips a year.

**Download Results** (`results.json`) carries each day's record in the next entry order's tag
(`rec=`…): previous settlement, entry and exit prices, the window's high and low, the direction
the signal gives, realised variance before and inside the window, and the largest bar gap. The
orders only carry the records; their fills and the backtest's P&L mean nothing and are not used.

{V2_NOTE if version == 2 else ""}**The run is unusable** if `END` is missing, if the backtest stopped with an error, or if `HEAD`
reports far fewer days than the span has trading days.
"""
    return RunSpec(
        run_id=run_id or (LEG_V2_RUNS if version == 2 else LEG_RUNS)[market],
        title=f"C-007 leg evidence{" v2" if version == 2 else ""}: {market}",
        purpose=f"Stage 2B C-007, {market} leg, window {entry}-{exit_} CT, development data "
                f"{start} to {alg.LEG_END} only (D-43, D-97).",
        class_name=f"LegEvidence{market}" + ("V2" if version == 2 else ""),
        start=start, end=alg.LEG_END,
        body=alg.LEG_BODY_V2 if version == 2 else alg.LEG_BODY,
        preamble=(alg.leg_preamble_v2(market, filter_days or alg.LEG_V2_FILTER_DAYS)
                  if version == 2 else alg.leg_preamble(market)),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="leg_evidence",
        expected=expected,
        extra={"market": market, "window_ct": [entry, exit_],
               "source": "Stage 2B C-007; D-50; D-97" + ("; D-98" if version == 2 else ""),
               **({"version": 2} if version == 2 else {}),
               **({"filter_days": filter_days} if filter_days else {})},
    )


#: Opening-gap reversal evidence (D-105): one kit, ES, the whole development span.
GAP_RUN = "R026-gap-ES"
#: Version 2 (D-109): the same kit with extended market hours, so the pre-open bars are present.
GAP_RUN_V2 = "R027-gap-ES2"


def _gap_spec(version: int = 1) -> RunSpec:
    first, last = ("%02d:%02d" % hm for hm in alg.GAP_REC_HM)
    v2 = version == 2
    v2_note = ("" if not v2 else
               "**Version 2 (D-109):** requests extended market hours, so the four pre-open bars "
               "(ending 08:27–08:30 CT) that R026 lacked on every day are present. Expect `full` "
               "close to the day count.\n\n")
    expected = v2_note + f"""\
Evidence for the opening-gap reversal candidate (D-105, `config/gap_reversal.yaml`), **ES**, every
development day from {alg.GAP_START} to {alg.GAP_END}. **Nothing is tested and no trade is computed
in the cloud.** The kit records prices only: the previous settlement and every one-minute bar ending
between {first} and {last} CT. The gap, the trigger, the stop, the target and all twelve variants are
scored in the repository from these bars, so this one run serves the whole design.

**Logs** holds three lines beginning `{alg.GAP_PREFIX}|`: `HEAD` (days recorded, `full` = days with
all {alg.GAP_SLOTS} bars, skips by reason: `noprev` no previous settlement yet, `roll` the contract
changed since it, `stale` it is over five days old; contract switches), `LAST` (the final day's
header, or its whole record if the run ended inside a window) and `END`. Expect roughly one day per
trading day in the span, a handful of `roll` skips a year, and most days `full`.

**Download Results** (`results.json`) carries each day's record in TWO order tags: the buy carries
the header and the first half of the bars (`b1=`), the liquidation the second half (`b2=`). Each bar
is four integers in ticks: open relative to the day's base price, high above open, open above low,
close relative to open. The orders' fills and the backtest's P&L mean nothing and are not used.

**First-run risk, stated now:** an order tag holds about 700 characters. If QuantConnect truncates
tags, the parser refuses the run ("an order tag was cut short") and the kit comes back with the bars
split across more orders. That is a fix-and-rerun round, not a result.

**The run is unusable** if `END` is missing, if the backtest stopped with an error, or if `HEAD`
reports far fewer days than the span has trading days. Do not look at the equity chart; it is
meaningless here.
"""
    return RunSpec(
        run_id=GAP_RUN_V2 if v2 else GAP_RUN,
        title="Opening-gap reversal evidence: ES" + (" v2" if v2 else ""),
        purpose=f"Gap-reversal candidate (D-105), ES minute bars {first}-{last} CT and the previous "
                f"settlement, development data {alg.GAP_START} to {alg.GAP_END} only.",
        class_name="GapEvidenceES" + ("V2" if v2 else ""),
        start=alg.GAP_START, end=alg.GAP_END,
        body=alg.GAP_BODY_V2 if v2 else alg.GAP_BODY,
        preamble=alg.gap_preamble(),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="gap_evidence",
        expected=expected,
        extra={"market": alg.GAP_MARKET, "record_window_ct": [first, last],
               "slots": alg.GAP_SLOTS, "version": version, "filter_days": alg.LEG_V2_FILTER_DAYS,
               "source": "config/gap_reversal.yaml; D-105; D-98" + ("; D-109" if v2 else ""),
               **({"extended_market_hours": True} if v2 else {})},
    )


#: The Test 1 re-score in the cloud (D-122).
OPENREV_RUN = "R028-openrev-rescore"


def _openrev_spec() -> RunSpec:
    expected = f"""\
**The Test 1 re-score (D-122), computed inside QuantConnect.** The algorithm collects ES one-minute bars
exactly as R027 did (same days, same contract choice, extended hours) and, at 10:30 CT each day, scores
every cell of the open-reversion design (`config/open_reversion.yaml`: 6 variants, plain and structural
entry, actual prices and rescaled to ES 4,000) under two fill rules: the Test 1 rule (fill at the
signal bar's close) and the corrected rule (fill at the next bar's open). **No price bar leaves the
cloud** (D-120): each day's order tags carry only the trade outcomes, in units of intended risk.

The `close` results must reproduce Test 1's numbers (`results/test1_diagnosis.csv`); that is the check
that the cloud computes what the repository computed. Only then are the `next_open` results read.

**Logs** holds three lines beginning `{alg.OPENREV_PREFIX}|`: `HEAD` (days recorded, full days, skips,
contract switches, orders placed), `LAST` and `END`. Expect 1,285 days, as R027, and a few thousand
orders. The run takes longer than R027 because it scores every day; if it hits a time limit, say so.

**Download Results** (`results.json`) carries each day's outcomes in one or more order tags. Ignore the
equity chart and statistics; the orders only carry data.

**The run is unusable** if `END` is missing, if the backtest stopped with an error or a time limit, or
if `HEAD` reports a different number of days from R027's 1,285.
"""
    return RunSpec(
        run_id=OPENREV_RUN,
        title="Test 1 re-score in the cloud: open reversion, close vs next-open fills",
        purpose=f"D-122: re-score Test 1 in QuantConnect with only the fill rule changed; development data "
                f"{alg.GAP_START} to {alg.GAP_END} only; exports per-day trade outcomes, never bars.",
        class_name="OpenRevRescoreES",
        start=alg.GAP_START, end=alg.GAP_END,
        body=alg.OPENREV_BODY,
        preamble=alg.openrev_preamble(),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="openrev_rescore",
        expected=expected,
        extra={"market": alg.GAP_MARKET, "record_window_ct": ["08:27", "10:30"], "version": 1,
               "fill_modes": ["close", "next_open"], "scales": ["actual", "P_ref_4000"],
               "exports": "per-day trade outcomes only (D-120)",
               "source": "config/open_reversion.yaml; D-118; D-121; D-122"},
    )


#: The open-reversion model on NQ (D-124): NQ's own contract terms, computed in the cloud.
OPENREV_NQ_RUN = "R029-openrev-NQ"


def _openrev_nq_spec() -> RunSpec:
    import yaml

    nq = yaml.safe_load((REPO_ROOT / "config" / "open_reversion_nq.yaml").read_text(encoding="utf-8"))
    ov = nq["overrides"]
    expected = f"""\
**The open-reversion model on NQ (D-124)**, computed inside QuantConnect. Same model as Test 1
(`config/open_reversion.yaml`), NQ's own terms (`config/open_reversion_nq.yaml`): E-mini Nasdaq-100 bars,
costed as MNQ ($0.50 a tick, $1.22 round turn), stop floor {ov["floor_ticks"]} ticks, price level for era
matching {ov["selection_price_level"]:,}. Every development day from {alg.GAP_START} to {alg.GAP_END}.
**No price bar leaves the cloud** (D-120): each day's order tags carry the trade outcomes of every cell
under both fill rules, the knob-free gate's inputs (four percentages) and integrity counters.

**Logs** holds three lines beginning `{alg.OPENREV_PREFIX_NQ}|`: `HEAD` (v=2, days, full days, skips, contract
switches, orders), `LAST` and `END`. Expect about 1,285 days, as ES (NQ trades the same calendar).

**Download Results** (`results.json`): the orders only carry data; ignore the equity chart and statistics.

**The run is unusable** if `END` is missing, if the backtest stopped with an error or a time limit, or if
`HEAD` reports far fewer days than about 1,285.
"""
    return RunSpec(
        run_id=OPENREV_NQ_RUN,
        title="Open reversion on NQ: in-cloud scoring, NQ's own contract terms",
        purpose=f"D-124: the Test 1 model on NQ/MNQ, development data {alg.GAP_START} to {alg.GAP_END} only; "
                "exports per-day outcomes and measurements, never bars.",
        class_name="OpenRevNQ",
        start=alg.GAP_START, end=alg.GAP_END,
        body=alg.OPENREV_BODY_V2,
        preamble=alg.openrev_preamble(market=nq["instrument"]["market"], vehicle=nq["instrument"]["vehicle"],
                                      floor_ticks=int(ov["floor_ticks"]),
                                      p_ref=float(ov["selection_price_level"]), prefix=alg.OPENREV_PREFIX_NQ),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="openrev_nq",
        expected=expected,
        extra={"market": nq["instrument"]["market"], "vehicle": nq["instrument"]["vehicle"],
               "floor_ticks": int(ov["floor_ticks"]), "p_ref": float(ov["selection_price_level"]),
               "fill_modes": ["close", "next_open"], "record_window_ct": ["08:27", "10:30"], "version": 2,
               "exports": "per-day trade outcomes and measurements only (D-120)",
               "source": "config/open_reversion_nq.yaml; D-124"},
    )


def _atlas_runs() -> dict[str, str]:
    import yaml

    return yaml.safe_load((REPO_ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8"))["runs"]


def _atlas_spec(market: str, run_id: str | None = None) -> RunSpec:
    import yaml

    cfg = yaml.safe_load((REPO_ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8"))
    m = cfg["markets"][market]
    rid = run_id or cfg["runs"][market]
    version = 3 if rid in set(cfg.get("kit_v3", [])) else 2 if rid in set(cfg.get("kit_v2", [])) else 1
    v2 = version >= 2
    v2_note = ("\n**Version 2 contract bookkeeping (D-132):** the contract roll and the settlement reference run at "
               "the first bar at or after the settlement minute, only contracts still in the universe are chosen, and "
               "a contract that leaves it is dropped. `HEAD` also reports `lost` (contracts dropped) and `late` "
               "(sessions rolled at the next session's first bar); expect both near zero. The measurements are "
               "version 1's.\n") if version == 2 else ""
    if version == 3:
        v2_note = ("\n**Version 3 contract bookkeeping (D-132, D-134):** the contract roll and the settlement reference "
                   "run at the first bar from the settlement minute up to CME's 16:00 CT daily break; a session with no "
                   "such bar is rolled at the next date's first bar only if its regular session was recorded; only "
                   "contracts still in the universe are chosen, and a contract that leaves it is dropped. `HEAD` "
                   "(`v=3`) also reports `lost` and `late`; expect both near zero, and `noprev` only on the first day "
                   "and after sessions without a settlement bar. The measurements are version 1's.\n")
    gc = ("\n**GC (D-126):** QuantConnect's GC minute data starts 2012-11-01 (D-90), so this run's days before that "
          "are empty; GC is reported as a short-span description, outside the screened family.\n") if market == "GC" else ""
    expected = f"""\
**Effect atlas, {market} (D-126, amended by D-128).** Every development day from {alg.GAP_START} to {alg.GAP_END}:
the market's bars, volume and bid/ask quotes from its open ({m["open"]} CT) minus 3 minutes to its settlement
({m["settle"]} CT) are recorded **inside QuantConnect**, and about 30 per-day measurements are computed there
(`config/effect_atlas.yaml`, `propedge/research/atlas_core.py`). Only those numbers leave, one order tag per
day (D-120).
{gc}{v2_note}
**Logs** holds three lines beginning `{alg.ATLAS_PREFIX}|`: `HEAD` (days, settled days, skips, contract switches),
`LAST` and `END`. **Download Results** carries the per-day tags; the orders' P&L means nothing.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD`
reports far fewer days than the span has trading days{" (for GC: from 2012-11 only)" if market == "GC" else ""}.
"""
    return RunSpec(
        run_id=rid,
        title=f"Effect atlas: {market}" + (f" (kit v{version})" if v2 else ""),
        purpose=f"D-126 research screen, {market}, development data {alg.GAP_START} to {alg.GAP_END} only; per-day "
                "measurements computed in the cloud, never bars.",
        class_name=f"Atlas{market}" + (f"V{version}" if v2 else ""),
        start=alg.GAP_START, end=alg.GAP_END,
        body={1: alg.ATLAS_BODY, 2: alg.ATLAS_BODY_V2, 3: alg.ATLAS_BODY_V3}[version],
        preamble=alg.atlas_preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="atlas",
        expected=expected,
        extra={"market": market, "open_ct": m["open"], "settle_ct": m["settle"], "tick": float(m["tick"]),
               "exports": "per-day measurements only (D-120)",
               "source": "config/effect_atlas.yaml; D-126; D-128" + ("; D-132" if v2 else "")
                         + ("; D-134" if version == 3 else ""),
               **({"kit_version": version} if v2 else {})},
    )


def _atlas_retired() -> dict[str, str]:
    import yaml

    return yaml.safe_load((REPO_ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8")).get(
        "retired_runs", {})


ATLAS_SPECS: dict[str, Callable[[], RunSpec]] = {
    **{rid: (lambda mk=mk: _atlas_spec(mk)) for mk, rid in _atlas_runs().items()},
    **{rid: (lambda mk=mk, r=rid: _atlas_spec(mk, r)) for rid, mk in _atlas_retired().items()}}


def _context_run() -> str:
    import yaml

    cfg = yaml.safe_load((REPO_ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8"))
    return cfg["amendment_d128"]["context_run"]["run"]


#: D-128's context kit, on record (its gamma unusable, D-129); the atlas reads the run named in the config.
CONTEXT_RUN = "R038-atlas-context"
CONTEXT_V2_RUN = _context_run()


def _context_spec() -> RunSpec:
    expected = f"""\
**The atlas context (D-128)**, daily, every session from {alg.CONTEXT_START} to {alg.CONTEXT_END}: the VIX index
close, and from January 2012 the net gamma exposure of SPX and NDX option market makers (Baltussen et al. 2021:
gamma x open interest x 100 x the index level, calls +, puts -), from each session's options within
{alg.CONTEXT_STRIKES} listed strikes of the money and {alg.CONTEXT_EXPIRY_DAYS} days of expiry
(`propedge/research/gamma_core.py`, embedded). **Only these numbers leave** (D-120): one order tag per session;
the orders are carriers on SPY and their P&L means nothing.

**Logs** holds `{alg.CONTEXT_PREFIX}|HEAD` (sessions; sessions with a VIX close, with SPX and NDX exposure; how
often the Black-Scholes and the platform's gamma agree in sign), `LAST` (the final session), any `NOTE`, and
`END`. Expect about 1,250 sessions, a VIX close on nearly all, and exposures from 2012 only (about 600 sessions).

**Download Results** (`results.json`) carries the per-session tags. This run reads option chains every day, so
it takes longer than R037; if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD`
reports far fewer sessions than about 1,250.
"""
    return RunSpec(
        run_id=CONTEXT_RUN,
        title="Effect atlas context: VIX close and option net gamma exposure",
        purpose=(f"D-128: per session {alg.CONTEXT_START} to {alg.CONTEXT_END}, the VIX close and SPX/NDX option "
                 "market makers' net gamma exposure, joined to the atlas by date; numbers only (D-120)."),
        class_name="AtlasContext",
        start=alg.CONTEXT_START, end=alg.CONTEXT_END,
        body=alg.CONTEXT_BODY, preamble=alg.context_preamble(),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="atlas_context",
        expected=expected,
        extra={"options": alg.CONTEXT_OPTIONS, "strikes": alg.CONTEXT_STRIKES,
               "expiry_days": alg.CONTEXT_EXPIRY_DAYS, "exports": "per-session numbers only (D-120)",
               "source": "config/effect_atlas.yaml amendment_d128; D-128"},
    )


#: Which extra free datasets arrive on this account (D-127), before the atlas is amended to use any.
EXTRAS_RUN = "R036-data-extras"
OPTIONS_RUN = "R037-data-options"

_EXTRAS_COMMON = """\
**Nothing is traded and no price leaves the cloud** (D-120). The algorithm subscribes, counts what
arrives in each calendar year, and writes one compact summary at the end. The answers go into
`config/data_sources.yaml` as facts read by this run, and decide what the effect atlas may be amended to
use (D-127). **None of the counts is a pass mark**: the run records what QuantConnect delivers, whatever
that is.

**Logs** holds lines beginning `{prefix}|`: `HEAD` (run, number of notes), one `SET` line per dataset with
the first day anything arrived, one `Y` line per dataset per year with the counts, `NOTE` lines for any
error caught while subscribing or reading a field, and `END`, which **must say `truncated=false`**.

A dataset this account cannot read may either show zero counts, which is itself the answer (*no data
received*), or stop the whole backtest with an error. **If the backtest stops with an error, copy the error
text exactly and stop**: the text says which dataset is refused, and that is the answer for it. A new kit
then drops that dataset for the rest. Do not look at the equity chart; it is meaningless here.
"""


def _extras_spec() -> RunSpec:
    expected = _EXTRAS_COMMON.format(prefix=alg.EXTRAS_PREFIX) + f"""
**What R036 asks, {alg.EXTRAS_START} to {alg.EXTRAS_END} (minute):**

| set | dataset | counted |
|---|---|---|
| `es`, `nq` | US Futures (AlgoSeek), front contract | trade bars `tb`; quote bars `qb`; quote bars with a bid and an ask `qok`, with both sizes `qsz`; regular-hours spread in ticks: `s0` crossed or locked, `s1`, `s2`, `s3` three or more |
| `vx` | VIX futures (CFE), in the same dataset | the same, without the spread buckets |
| `vix`, `spx`, `ndx` | US Indices | minute bars `tb` from the subscription; daily bars `day` from one history request at the end |

**ES is the control**: if ES received no trade bars, the run read nothing and is unusable. The
documentation says index minute history may be limited to about a year; zero `tb` with non-zero `day` for an
index is that limit, not a failure.

**The run is unusable** if `END` is missing or says `truncated=true`, or if ES received no trade bars.
"""
    return RunSpec(
        run_id=EXTRAS_RUN,
        title="Extra datasets: futures quotes, VIX futures, index values",
        purpose=(f"D-127: which extra free datasets arrive over {alg.EXTRAS_START} to {alg.EXTRAS_END} -- ES and NQ "
                 "quote bars (bid, ask, sizes, spread in ticks), VIX futures, the VIX, SPX and NDX index values. "
                 "Counts only; no price leaves (D-120)."),
        class_name="DataExtras",
        start=alg.EXTRAS_START, end=alg.EXTRAS_END,
        body=alg.EXTRAS_BODY, preamble=alg.EXTRAS_PREAMBLE,
        downloads=(LOGS, RAN_CODE),
        parser="data_extras",
        expected=expected,
        extra={"log_budget_bytes": alg.EXTRAS_LOG_BUDGET_BYTES, "exports": "counts only (D-120)",
               "source": "D-127"},
    )


def _options_spec() -> RunSpec:
    fields = ", ".join(f"`{f}` {name.replace('_', ' ')}" for f, name in alg.OPTIONS_FIELDS.items())
    expected = _EXTRAS_COMMON.format(prefix=alg.OPTIONS_PREFIX) + f"""
**What R037 asks, {alg.OPTIONS_START} to {alg.OPTIONS_END} (daily):** the documentation says index options
and futures options start in January 2012; the run starts a month earlier so the first chain shows where
the data really begins.

| set | dataset | chain |
|---|---|---|
| `spx`, `ndx` | US Index Options (AlgoSeek) | {alg.OPTIONS_STRIKES} strikes either side, expiries within {alg.OPTIONS_EXPIRY_DAYS} days |
| `es`, `nq` | US Future Options (AlgoSeek) | {alg.OPTIONS_STRIKES} strikes either side, on futures expiring within 95 days |

Counted per year: `u` the underlying's daily bars (the control), `days` days with a non-empty chain, `k`
contracts observed, and how many of them carry a non-zero {fields}. `x…` counts an error reading that field;
the first error's text is in a `NOTE`. Gamma and implied volatility may come from QuantConnect's daily
option-universe files or from LEAN's own pricing model; either way this run only says whether they are
populated, not how good they are.

**The ES underlying is the control**: if it received no bars, the run read nothing and is unusable.

**The run is unusable** if `END` is missing or says `truncated=true`, or if the ES underlying received no bars.
"""
    return RunSpec(
        run_id=OPTIONS_RUN,
        title="Extra datasets: index options and futures options",
        purpose=(f"D-127: whether SPX and NDX index options and ES and NQ futures options arrive over "
                 f"{alg.OPTIONS_START} to {alg.OPTIONS_END}, and whether open interest, implied volatility, "
                 "gamma and a price are populated. Daily; counts only; no price leaves (D-120)."),
        class_name="DataOptions",
        start=alg.OPTIONS_START, end=alg.OPTIONS_END,
        body=alg.OPTIONS_BODY, preamble=alg.OPTIONS_PREAMBLE,
        downloads=(LOGS, RAN_CODE),
        parser="data_options",
        expected=expected,
        extra={"log_budget_bytes": alg.EXTRAS_LOG_BUDGET_BYTES, "exports": "counts only (D-120)",
               "source": "D-127"},
    )


def _context_v2_spec() -> RunSpec:
    expected = f"""\
**The atlas context, version 2 (D-129)**, daily, every session from {alg.CONTEXT_START} to {alg.CONTEXT_END}: the VIX
index close, and from January 2012 the net gamma exposure of SPX and NDX option market makers (Baltussen et al.
2021), now read inside the option filter from the platform's end-of-day universe -- **every strike and expiry**,
with its open interest, implied volatility and index level from the session's close. R039 showed R038's route saw
zero open interest on every contract; this route is the one it showed working. **Only these numbers leave**
(D-120): one order tag per session; the orders are carriers on SPY and their P&L means nothing.

**Logs** holds `{alg.CONTEXT_PREFIX}|HEAD|v=2` (sessions; sessions with a VIX close and with SPX and NDX exposure; how
often the Black-Scholes and the platform's gamma agree in sign; `und_gs`/`und_gn`, sessions whose universe index
level equals that session's close; `late`, universes that arrived after their session was written), `LAST`, any
`NOTE`, and `END`. Expect about 1,250 sessions, a VIX close on nearly all, exposures on about 600 (from 2012),
sign agreement and index-level matches on nearly all of those, and `late` near zero.

**Download Results** (`results.json`) carries the per-session tags. Reading the whole chain every day takes longer
than R038; if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports
far fewer sessions than about 1,250.
"""
    return RunSpec(
        run_id=CONTEXT_V2_RUN,
        title="Effect atlas context v2: VIX close and whole-chain option net gamma exposure",
        purpose=(f"D-129: per session {alg.CONTEXT_START} to {alg.CONTEXT_END}, the VIX close and SPX/NDX option "
                 "market makers' net gamma exposure from the filter's end-of-day universe; numbers only (D-120)."),
        class_name="AtlasContextV2",
        start=alg.CONTEXT_START, end=alg.CONTEXT_END,
        body=alg.CONTEXT_BODY_V2, preamble=alg.context_preamble_v2(),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="atlas_context",
        expected=expected,
        extra={"options": alg.CONTEXT_OPTIONS, "chain": "whole (every strike and expiry)", "version": 2,
               "exports": "per-session numbers only (D-120)",
               "source": "config/effect_atlas.yaml amendment_d128.context_run; D-128; D-129"},
    )


def _fv_spec(market: str, extension: bool = False) -> RunSpec:
    q = alg.fv_params(market)
    if extension:
        return _fv_ext_spec(market, q, alg.FV_EXT_START, alg.FV_EXT_END)
    expected = f"""\
**FV1, the fair-value model (D-142), on {market}**, scored inside QuantConnect on every development day from
{alg.GAP_START} to {alg.GAP_END}. The complete model is declared in `config/model_fv.yaml`: fair value at the 08:30
and 13:00 CT opens, continuation trades away from it in each session's first fifteen minutes and reversion trades
back to it afterwards (plus continuations after it is touched), a displacement bar plus a structure break as the
trigger, a 1.5R target, two stop families (JJ's volatility bands; the structural swing), at most two attempts per
phase, no new trade after two losses in a day, next-bar-open fills and the assumed costs. Both stop families are
scored at two price scales (the {market} level of {q['p_ref']:,.0f}, and actual prices). **Only the trades leave**
(D-120): each day's order tags carry its trade records and a few integrity numbers; the orders' P&L means nothing.

**Logs**: `{alg.FV_PREFIX}|HEAD` (days, settled days, trades, orders, skips, contract switches, lost and late
contracts), `LAST`, `END`. Expect about 1,285 days, with `lost` and `late` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than about 1,285.
"""
    return RunSpec(
        run_id=alg.FV_RUNS[market],
        title=f"FV1 fair-value model: {market}",
        purpose=(f"D-142: the complete FV1 model on {market}, development data {alg.GAP_START} to {alg.GAP_END} only; "
                 "trades scored in the cloud, trade records exported, never bars."),
        class_name=f"FV1{market}",
        start=alg.GAP_START, end=alg.GAP_END,
        body=alg.FV_BODY, preamble=alg.fv_preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="fv1",
        expected=expected,
        extra={"market": market, "model": "FV1", "families": list(alg.FV_FAMILIES), "scales": ["p_ref", "actual"],
               "p_ref": q["p_ref"], "exports": "trade records only (D-120)",
               "source": "config/model_fv.yaml; D-142"},
    )


def _fv_ext_spec(market: str, q: dict, start: date, end: date) -> RunSpec:
    expected = f"""\
**FV1 unchanged (D-142) on {market}, on the development block D-144 opened: {start} to {end}.** Same algorithm as
R045/R046 in every line but the dates and the class name: the model in `config/model_fv.yaml`, both stop families,
both price scales, next-bar-open fills, the assumed costs. Declared before any of these days is scored
(`config/model_fv.yaml` `extension_1419`): nothing is selected or tuned on this block; every configuration is
reported, and the configuration selected on 2009-2011 is read once. **Only the trades leave** (D-120).

**Logs**: `{alg.FV_PREFIX}|HEAD` (days, settled days, trades, orders, skips, contract switches, lost and late
contracts), `LAST`, `END`. Expect about 1,440 days, with `lost` and `late` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than about 1,440.
"""
    return RunSpec(
        run_id=alg.FV_EXT_RUNS[market],
        title=f"FV1 fair-value model: {market}, 2014-2019",
        purpose=(f"D-142 model unchanged on {market}, the development block {start} to {end} opened by D-144; trades "
                 "scored in the cloud, trade records exported, never bars."),
        class_name=f"FV1{market}Ext",
        start=start, end=end,
        body=alg.FV_BODY, preamble=alg.fv_preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="fv1",
        expected=expected,
        extra={"market": market, "model": "FV1", "families": list(alg.FV_FAMILIES), "scales": ["p_ref", "actual"],
               "p_ref": q["p_ref"], "exports": "trade records only (D-120)",
               "source": "config/model_fv.yaml extension_1419; D-142; D-144"},
    )


def _bmap_spec(market: str, window: str) -> RunSpec:
    warm, start, end = alg.BMAP_WINDOWS[window]
    q = alg.bmap_params(market)
    expected = f"""\
**The bracket outcome map (D-149), {market}, {start} to {end}** (from {warm} as warm-up, which records nothing).
Declared in `config/bracket_map.yaml`. At every half-hour decision from 08:35 to 14:00 CT, a long and a short
bracket at three stop widths (0.1, 0.2 and 0.4 of the 20-session mean session range), each walked to its stop or the
15:00 CT close: how far it went in its favour before the stop, whether and how the stop was hit, and where it ended.
Every target multiple the prop lifecycle uses (0.5 to 5 times the stop) is read from those three numbers. Each day is
rescaled so its 08:30 open maps to {q['p_ref']:,.0f} (D-106). **Only the path summaries, bucketed features and a few
per-day measurements leave** (D-120): no prices.

**Logs**: `{alg.BMAP_PREFIX}|HEAD` (days in the window, settled days, entries, orders, skips, contract switches, lost
and late contracts, warm-up days), `LAST`, `END`. Expect about 1,250 to 1,450 days, with `lost` and `late` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that.
"""
    return RunSpec(
        run_id=alg.BMAP_RUNS[(market, window)],
        title=f"Bracket outcome map: {market}, {start.year}-{end.year}",
        purpose=(f"D-149: the bracket outcome map on {market}, development data {start} to {end} only; path summaries "
                 "and bucketed features exported, never bars."),
        class_name=f"BMap{market}{window}",
        start=warm, end=end,
        body=alg.BMAP_BODY, preamble=alg.bmap_preamble(market, window),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="bmap",
        expected=expected,
        extra={"market": market, "window": window, "model": "bracket_map", "widths": q["p"]["widths"],
               "times": q["p"]["times"], "p_ref": q["p_ref"], "exports": "path summaries and bucketed features (D-120)",
               "source": "config/bracket_map.yaml; D-149"},
    )


BMAP_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk, w=w: _bmap_spec(mk, w)) for (mk, w), rid in alg.BMAP_RUNS.items()}


def _im2_spec(market: str, window: str) -> RunSpec:
    warm, start, end = alg.im2_windows()[window]
    q = alg.im2_params(market)
    hm = lambda m: f"{m // 60:02d}:{m % 60:02d}"                             # noqa: E731
    expected = f"""\
**IM2 under P-04, {market}, {start} to {end}** (from {warm} as warm-up, which fills the 14-session lookback and records
nothing). The paper's noise-band entries on the {hm(q['open_min'])}-{hm(q['close_min'])} CT session, decided at every
:00 and :30 mark from {hm(q['open_min'] + q['p']['times'][0] + 1)} to {hm(q['open_min'] + q['p']['times'][-1] + 1)} CT: long above
both the upper band and VWAP, short below both the lower band and VWAP; the stop at the opposite band; brackets at 1, 2
and 3 R walked to the target, the stop or the session close; the market waits for the 2:1 bracket plus 5 minutes. Only
full sessions the exchange calendar schedules are traded, each with a complete previous session. Every entry is walked
at the reference price ({q['p_ref']:g}, D-106) and at actual prices, with {q['micro']}'s tick as the fills' tick and the
orders' grid (D-95, P-04); in the minutes of the scheduled releases embedded in the code (P-04's calendar) market orders
fill at the bar's worst price. **Only the entries leave** (D-120): per session its integrity, counts and release
minutes, per entry its decision levels, the lowest price while held, stop distance and per-R outcome and MAE; no bar.

**Logs**: `{alg.IM2_PREFIX}|HEAD` (version 2; sessions in the window, settled and complete sessions, entries, signals, signals
dropped inside the wait, entries through their stop, orders, skips by reason, contract switches, lost and late
contracts, warm-up sessions, the calendar's holidays, early closes and late opens in the window, and scheduled full
sessions with no data), `LAST`, `END`. Expect about 1,250 to 1,450 sessions; `lost` near zero; `late` about the
number of early closes and sessions whose data ends early (each rolls at the next day's first bar), with `noprev`
skips of about the same size; `switches` about 20 for ES and 6E and about 60 for CL and NG (a roll each quarter or
each month); `hol` and `ec` above zero (every year has holidays and early closes); `gone` short -- a US holiday listed
there means the calendar does not list it for this market, which the scorer reports.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer sessions than that, or `hol` or `ec` is zero (the calendar was not read). The ingestion refuses those itself.
"""
    return RunSpec(
        run_id=alg.IM2_RUNS[(market, window)],
        title=f"IM2 under P-04: {market}, {start.year}-{end.year}",
        purpose=(f"P-04: IM2's entries on {market}, development data {start} to {end} only; entries and bracket "
                 "outcomes scored in the cloud and exported, never bars."),
        class_name=f"IM2{market}{window}",
        start=warm, end=end,
        body=alg.IM2_BODY, preamble=alg.im2_preamble(market, window),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="im2",
        expected=expected,
        extra={"market": market, "window": window, "model": "IM2", "prereg": "P-04", "micro": q["micro"],
               "p_ref": q["p_ref"], "times": q["p"]["times"], "rr": q["p"]["rr"],
               "release_days": len(alg.im2_releases(market, window)), "hot_minutes": q["hot_minutes"],
               "exports": "entries, bracket outcomes, release minutes and integrity counts (D-120)",
               "source": "config/model_im2.yaml; config/im2_release_calendar.csv; prereg/P-04_im2_lifecycle_v3.md"},
    )


IM2_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk, w=w: _im2_spec(mk, w)) for (mk, w), rid in alg.IM2_RUNS.items()}


def _im2x_spec(market: str, window: str) -> RunSpec:
    """D-200: IM2's second implementation, written from docs/verification/im2_second_implementation.md without the
    kit's code, on the window of the development run it is compared with."""
    from propedge.verification.im2x_kit import IM2X_BODY, im2x_preamble

    warm, start, end = alg.im2_windows()[window]
    kit_run = alg.IM2_RUNS[(market, window)]
    expected = f"""\
**IM2's second implementation (D-200), {market}, {start} to {end}** (from {warm} as warm-up, which fills the
14-session lookback and records nothing). The same noise band, VWAP and signals as {kit_run}, written again from the
brief without the kit's code, on the same data, so the two can be compared session by session
(`scripts/crosscheck_im2.py`). **Only the band values and the signals leave** (D-120): per session its contract,
calendar code, skip reason, integrity, open, prior close, lookback depth and counts, per signal its decision time,
side, close, bands and VWAP; no bar.

**Logs**: `IMX|HEAD` (version 1; sessions in the window, warm-up sessions, signals, orders, contract switches, the
calendar's holidays, early closes and late opens in the window, and scheduled full sessions with no data) and
`IMX|END`. Expect about the number of sessions {kit_run} reported, `hol` and `ec` above zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `hol` or `ec` is
zero (the calendar was not read). The ingestion refuses those itself. A mismatch with {kit_run} is not a reason to
rerun: it is diagnosed first (D-200).
"""
    return RunSpec(
        run_id=alg.IM2X_RUNS[(market, window)],
        title=f"IM2's second implementation (D-200): {market}, {start.year}-{end.year}",
        purpose=(f"D-200: IM2's band and signals on {market}, development data {start} to {end} only, written "
                 f"independently of the kit and compared with {kit_run}; band values and signals exported, never "
                 "bars."),
        class_name=f"IM2X{market}{window}",
        start=warm, end=end,
        body=IM2X_BODY, preamble=im2x_preamble(market, warm, start, end),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="im2x",
        expected=expected,
        extra={"market": market, "window": window, "model": "IM2", "prereg": "P-04", "decision": "D-200",
               "compared_with": kit_run,
               "exports": "per session its integrity, open, prior close and counts; per signal its levels (D-120)",
               "source": "docs/verification/im2_second_implementation.md; config/model_im2.yaml; "
                         "prereg/P-04_im2_lifecycle_v3.md"},
    )


IM2X_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk, w=w: _im2x_spec(mk, w)) for (mk, w), rid in alg.IM2X_RUNS.items()}


FV_SPECS: dict[str, Callable[[], RunSpec]] = {
    **{rid: (lambda mk=mk: _fv_spec(mk)) for mk, rid in alg.FV_RUNS.items()},
    **{rid: (lambda mk=mk: _fv_spec(mk, extension=True)) for mk, rid in alg.FV_EXT_RUNS.items()},
}


GRID_RUN = "R044-zn-grid-check"


def _grid_spec() -> RunSpec:
    expected = f"""\
**Failure-protocol check for R043's integrity count.** R043 (ZN) flagged most bars "bad" in 2009-2011 and none in
2012-2014; its settlement prices sit off ZN's 1/64 grid by at most the offset of five-decimal rounding. The atlas
counts two conditions together; this run separates them, per year, over every ZN contract's minute bars,
{alg.GAP_START} to {alg.GAP_END}:

| field | meaning |
|---|---|
| `n` | bars counted |
| `ohlc` | bars whose open, high, low and close are inconsistent (low above open or close, high below them) |
| `off` | bars with any price off the grid at all |
| `beyond` | bars off the grid by more than twice five-decimal rounding's largest offset |
| `maxoff` | the largest offset seen, in ticks |

**Logs only.** The run is unusable only if `END` is missing or the backtest stopped with an error. The answer
decides whether ZN passes the atlas's integrity check (a decision recorded before the screen runs).
"""
    return RunSpec(
        run_id=GRID_RUN,
        title="ZN price-grid check",
        purpose=(f"Failure protocol for R043: ZN minute bars by year, inconsistent vs off-grid vs beyond rounding, "
                 f"{alg.GAP_START} to {alg.GAP_END}; logs only."),
        class_name="ZNGridCheck",
        start=alg.GAP_START, end=alg.GAP_END,
        body=alg.GRID_BODY, preamble=alg.GRID_PREAMBLE,
        downloads=(LOGS, RAN_CODE),
        parser="grid_check",
        expected=expected,
        extra={"market": alg.GRID_MARKET, "exports": "log lines only (D-120)", "source": "failure protocol for R043"},
    )


GDIAG_RUN = "R039-gamma-diagnostic"


def _gdiag_spec() -> RunSpec:
    expected = f"""\
**Failure-protocol diagnostic for R038's gamma exposure (D-128).** R038's SPX and NDX exposures shrank toward zero
after January 2012 and its two gamma computations agreed in sign only by chance. This short run
({alg.GDIAG_START} to {alg.GDIAG_END}, SPX only, daily) reads the same sessions three ways and logs what each sees:

| line | route |
|---|---|
| `{alg.GDIAG_PREFIX}\\|SLICE\\|…` | R038's route: the subscribed chain in `on_data`, Greeks from the platform's live price model |
| `{alg.GDIAG_PREFIX}\\|FILTER\\|…` | the universe inside the filter function: the platform's pre-computed values from the previous close |
| `{alg.GDIAG_PREFIX}\\|OC\\|…` | `option_chain()`, the whole chain |

Each line: the object type, contracts seen and read, the index level used (`und`; for SLICE also `cu`, the chain's
own underlying price), the lowest and highest strike, the exposure with both gammas, and one near-the-money
contract's strike, years to expiry, implied volatility, open interest, platform gamma and Black-Scholes gamma.
`NOTE` lines record any route that raised an error; **an error in one route is an answer, not a failure**.

**The run is unusable** only if `END` is missing or the backtest stopped with an error. Nothing is ingested into a
test; the lines decide how the corrected context kit reads gamma.
"""
    return RunSpec(
        run_id=GDIAG_RUN,
        title="Gamma diagnostic: three routes to SPX option gamma",
        purpose=(f"Failure protocol for R038 (D-128): SPX gamma read three ways, {alg.GDIAG_START} to {alg.GDIAG_END}; "
                 "logs only."),
        class_name="GammaDiagnostic",
        start=alg.GDIAG_START, end=alg.GDIAG_END,
        body=alg.GDIAG_BODY, preamble=alg.gdiag_preamble(),
        downloads=(LOGS, RAN_CODE),
        parser="gamma_diagnostic",
        expected=expected,
        extra={"exports": "log lines only (D-120)", "source": "D-128; failure protocol for R038"},
    )


def _release_spec(market: str) -> RunSpec:
    """R061-R062 (D-164): the pre-release drift kit for one market, one order tag per scheduled release."""
    import yaml

    cfg = yaml.safe_load((REPO_ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8"))
    am = cfg["amendment_d164"]
    events = alg.release_events(market)
    n_events = sum(len(v) for v in events.values())
    codes = ", ".join(am["events"][market])
    expected = f"""\
**Pre-release drift, {market} (D-164; 2B F-032).** For each of the {n_events} scheduled releases in
`config/release_calendar.csv` for this market ({codes}; joint releases at one minute are one event), the mapped
contract's minute closes from 30 minutes before the release to 5 minutes after are read **inside QuantConnect**
and two returns are computed there (`propedge/research/release_core.py`): the pre-release return ([t-30, t-1]
minutes) and the release return ([t-1, t+5]). Only those numbers, the bar count, the offsets, one price and the
contract leave, one order tag per event (D-120). Events on days the market had no bars are not emitted and are
counted in `nodata`.

**Logs** holds three lines beginning `{alg.RELEASE_PREFIX}|`: `HEAD` (scheduled, emitted, nodata, contract switches),
`LAST` and `END`. **Download Results** carries the per-event tags; the orders' P&L means nothing.

**Plausible values, not targets.** `emitted` close to `scheduled` (a handful of `nodata` events on holidays or
data gaps); `nb` mostly 36; a few `roll=1` events near contract changes.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `emitted` is
far below `scheduled`.
"""
    return RunSpec(
        run_id=alg.RELEASE_RUNS[market],
        title=f"Pre-release drift: {market}",
        purpose=f"D-164 research screen (2B F-032), {market}, development data {alg.RELEASE_START} to "
                f"{alg.RELEASE_END} only; per-event returns computed in the cloud, never bars.",
        class_name=f"Release{market}",
        start=alg.RELEASE_START, end=alg.RELEASE_END,
        body=alg.RELEASE_BODY,
        preamble=alg.release_preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="release",
        expected=expected,
        extra={"market": market, "events_scheduled": n_events, "tick": float(cfg["markets"][market]["tick"]),
               "exports": "per-event returns, bar count, offsets, one price and the contract (D-120)",
               "source": "config/effect_atlas.yaml amendment_d164; config/release_calendar.csv; D-164"},
    )


RELEASE_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk: _release_spec(mk)) for mk, rid in alg.RELEASE_RUNS.items()}


def _rmap_spec(market: str, half: str, run_id: str | None = None, scale: str = "dev") -> RunSpec:
    from propedge.data import rmap_kit as rk

    today = scale == "today"
    run_id = run_id or (rk.TODAY_RUNS if today else rk.RMAP_RUNS)[(market, half)]
    warm, start, end = rk.windows()[half]
    q = rk.params(market, scale=scale)
    stops = ", ".join(f"${x:,.0f}" for x in q["stop_dollars"])
    lead = ("**EXPLORATORY (D-225): at today's price level** -- the same kit as the development-scale map with only the "
            "reference price changed (`config/resolution_map_today.yaml`).\n\n" if today else "")
    expected = lead + f"""\
**The resolution map (D-214), {market}, {start} to {end}** (from {warm} as warm-up, which records nothing). Declared in
`config/resolution_map.yaml`. On Topstep's trading day -- 17:00 CT the evening before to the 15:10 CT flatten -- at
every hourly decision from 17:00 to 14:00 CT, a long and a short bracket at each fixed stop ({stops} per
{q['micro']}), walked to its target at 1R and 2R, its stop, or the day's last bar. Each day is rescaled so its first
bar's open maps to {q['p_ref']:,g} (D-106). **Only counts leave** (D-120): per year, decision, stop and R the brackets
at the target first, the stop first and still open, the minutes to resolution, and the entry minute's spread.

**Logs**: `{rk.RMAP_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders,
contract switches, lost contracts, early closes, bad bars, bars and quotes recorded) and `END`. Expect about 1,250 to
1,450 days and five or six emits, `lost` near zero, `quotes` close to `bars`.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that.
"""
    return RunSpec(
        run_id=run_id,
        title=(f"Resolution map at today's prices: {market}, {start.year}-{end.year}" if today
               else f"Resolution map: {market}, {start.year}-{end.year}"),
        purpose=((f"D-225 (EXPLORATORY): D-214's map read at today's price level ({q['p_ref']:,g}) on {market}, "
                  f"development data {start} to {end} only; counts exported, never bars.") if today else
                 (f"D-214: how often brackets resolve before Topstep's 15:10 flatten on {market}, development data "
                  f"{start} to {end} only; counts exported, never bars.")),
        class_name=f"RMap{'Today' if today else ''}{market}{half}",
        start=warm, end=end,
        body=rk.body(run_id), preamble=rk.preamble(market, half, scale),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="rmap",
        expected=expected,
        extra={"market": market, "window": half, "model": "resolution_map", "stop_dollars": q["stop_dollars"],
               "times": q["p"]["times"], "rr": list(q["p"]["rr"]), "p_ref": q["p_ref"], "micro": q["micro"],
               "micro_tick": q["micro_tick"], "exports": "counts per year, decision, stop and R (D-120)",
               "ingest": "scripts/ingest_rmap_run.py",
               "source": ("config/resolution_map.yaml, config/resolution_map_today.yaml; D-213, D-214, D-225" if today
                          else "config/resolution_map.yaml; D-213, D-214"),
               **({"scale": "today"} if today else {})},
    )


def _rmap_specs() -> dict[str, Callable[[], RunSpec]]:
    from propedge.data import rmap_kit as rk

    return {**{rid: (lambda mk=mk, h=h, rid=rid: _rmap_spec(mk, h, rid)) for rid, (mk, h) in rk.RMAP_KITS.items()},
            **{rid: (lambda mk=mk, h=h, rid=rid: _rmap_spec(mk, h, rid, "today"))
               for rid, (mk, h) in rk.RMAP_TODAY_KITS.items()}}


RMAP_SPECS: dict[str, Callable[[], RunSpec]] = _rmap_specs()


def _rmap_confirm_spec() -> RunSpec:
    """D-229: NQB1's one confirmation on the held-back window, under its registered pre-registration only."""
    from propedge.data import rmap_kit as rk

    c = rk.confirm_config()
    if not c.get("prereg_id") or str(c["prereg_id"]).lower() == "pending":
        raise ValueError("config/nqb1_confirmation.yaml has no registered prereg_id; the kit is not generated (D-81)")
    q = rk.confirm_params(c)
    warm, start, end = rk.confirm_windows(c)
    legs = ", ".join(f"{k} {v['R']:g}:1 at ${v['stop_dollars']:,.0f} a {q['micro']}" for k, v in c["legs"].items())
    expected = f"""\
**NQB1's confirmation (D-229), under {c['prereg_id']}: {c['market']}, {start} to {end}** (from {warm} as warm-up, which
records nothing). Fixed in `config/nqb1_confirmation.yaml` before any of this window was read. The development map's
kit (version 3) at today's price level ({q['p_ref']:,g}), its decision times cut to the registered
{len(q['p']['times'])} and its brackets to the registered two -- {legs} -- so no other cell of the held-back window is
counted. **Only counts leave** (D-120): per year, decision and bracket the brackets at the target first, the stop first
and still open, and the entry minute's spread.

**Logs**: `{rk.RMAP_PREFIX}|HEAD` and `END`, as the map's kits. Expect about 1,745 days and seven emits, `lost` near
zero, `quotes` close to `bars`.

**The run is unusable** (D-230, the pre-registration's single test, judged from the log before any count is parsed) if
`END` is missing, the log or the operator reports an error or a time limit, or `HEAD` reports fewer than
{c['min_days']:,} days; or if the parser refuses its output. It is recorded in `unusable.json` and its counts are not
used; one fixed kit may follow, and a second unusable run is a FAIL. A refusal of the procedure (a missing or wrong
download, the ran code) is retried on this backtest's own files and is not a new run.
"""
    return RunSpec(
        run_id=rk.CONFIRM_RUN,
        title=f"NQB1 confirmation: {c['market']} brackets at today's prices, {start.year}-{end.year}",
        purpose=(f"D-229, {c['prereg_id']}: NQB1's one confirmation -- how often its two registered brackets resolve "
                 f"before Topstep's 15:10 flatten on {c['market']}, {start} to {end}, the held-back window; counts "
                 "exported, never bars."),
        class_name=f"RMapConfirm{c['market']}",
        start=warm, end=end,
        body=rk.BODY_CONFIRM, preamble=rk.confirm_preamble(c),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="rmap",
        expected=expected,
        extra={"market": c["market"], "window": "confirm", "model": c["model"], "prereg": c["prereg_id"],
               "confirm": True, "scale": "today", "stop_dollars": q["stop_dollars"], "times": q["p"]["times"],
               "rr": list(q["p"]["rr"]), "keep": [list(k) for k in q["keep"]], "p_ref": q["p_ref"],
               "micro": q["micro"], "micro_tick": q["micro_tick"],
               "exports": "counts per year, decision and registered bracket (D-120, D-229)",
               "ingest": "scripts/ingest_rmap_run.py",
               "source": "config/nqb1_confirmation.yaml; D-229; " + str(c["prereg_id"])},
        prereg_id=str(c["prereg_id"]),
    )


def _flip_spec() -> RunSpec:
    """D-343: the flip map -- the fast, time-boxed bracket for the two-stream candidate's flip days, NQ at actual prices."""
    from propedge.data import flip_kit as fk

    cfg = fk.config()
    q = fk.params(cfg)
    warm, start, end = fk.windows(cfg)
    widths = ", ".join(f"{w:g}" for w in q["widths_points"])
    slots = ", ".join(sorted({f"{(17 * 60 + t) % 1440 // 60:02d}:{(17 * 60 + t) % 60:02d}" for t in q["p"]["times"]}))
    expected = f"""\
**The flip map (D-343), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records nothing), at actual
prices. Declared in `config/flip_map.yaml`. On Topstep's trading day -- 17:00 CT the evening before to the 15:10 CT
flatten -- at every hour start from 17:00 to 14:00 CT and at the 08:30 CT open ({len(q['p']['times'])} decisions), a long
and a short bracket in one {q['ticker']} at each fixed width in points ({widths}; 1:1), entered on time (the slot's first
bar's open, one tick adverse) and one minute late (the next bar's open), read for at most {q['box']} bars to its target,
its stop, or a scratch at the box's last bar's close. **Only counts leave** (D-120): per year, slot, width and entry
delay the brackets at the target, at the stop and scratched, the minutes to resolution, how many resolved within
{q['within']} minutes, the scratches' P&L in ticks, and the entry minute's spread.

**Logs**: `{fk.FLIP_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders, contract
switches, lost contracts, early closes, bad bars, bars and quotes recorded) and `END`. Expect about 1,380 days and six
emits, `lost` near zero, `quotes` close to `bars`.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that.
"""
    return RunSpec(
        run_id=fk.FLIP_RUN,
        title=f"Flip map: {q['market']} fast brackets at the hour starts, {start.year}-{end.year}",
        purpose=(f"D-343: how often a fast 1:1 bracket in one {q['ticker']} resolves inside a {q['box']}-minute box at each "
                 f"hour start on {q['market']}, development data {start} to {end} only, actual prices; counts exported, "
                 "never bars."),
        class_name="FlipMapNQ",
        start=warm, end=end,
        body=fk.BODY, preamble=fk.preamble(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="flipmap",
        expected=expected,
        extra={"market": q["market"], "model": "flip_map", "widths_points": q["widths_points"], "times": q["p"]["times"],
               "slots_ct": slots, "delays_min": q["delays"], "box_minutes": q["box"], "within_minutes": q["within"],
               "ticker": q["ticker"], "tick": q["tick"], "point_value": q["point_value"], "scale": "actual",
               "exports": "counts per year, slot, width and entry delay (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/flip_map.yaml; D-343"},
    )


def _flip_seconds_spec() -> RunSpec:
    """D-344: the flip map at second resolution for the two open slots the minute map found."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_seconds()
    q = fk.params_seconds(cfg)
    warm, start, end = fk.windows_seconds(cfg)
    widths = ", ".join(f"{w:g}" for w in q["widths_points"])
    expected = f"""\
**The flip map at second resolution (D-344), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records
nothing), at actual prices. Declared in `config/flip_map_seconds.yaml`. The minute map (R137) found that a fast bracket
resolves inside its box only around the open; its minute bars could not tell a target from a stop inside the entry
minute. This kit measures the same brackets on ONE-SECOND bars: at each trading day's close, one history request brings
the day's second bars from {q['window_ct'][0]} to {q['window_ct'][1]} CT for the day's contract, and at the
{" and ".join(q['slot_labels'])} CT slots a long and a short bracket in one {q['ticker']} at each width in points
({widths}; 1:1) is entered on time (the slot's first second bar's open, one tick adverse) and {q['delays'][1]} seconds
late, read for at most {q['box']} seconds to its target, its stop, or a scratch at the box's last bar's close. **Only
counts leave** (D-120): per year, slot, width and entry delay the brackets at the target, at the stop and scratched, the
seconds to resolution, how many resolved within {q['within']} seconds, the scratches' P&L in ticks. No spread is
recorded here: the scorer reads the minute kit's spread at the same slots.

**Logs**: `{fk.FLIP_SECONDS_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders,
contract switches, lost contracts, early closes, minute bars, `secbars` second bars received, `nosec` days whose window
the history could not serve, `short` days with a thin window) and `END`. Expect about 1,380 days and six emits, `lost`
and `nosec` near zero, `secbars` near 2,500 a day. The run reads about 3.5 million second bars by history and may take
longer than the minute kit; if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer days than that, or `nosec` is a large share of the days.
"""
    return RunSpec(
        run_id=fk.FLIP_SECONDS_RUN,
        title=f"Flip map at second resolution: {q['market']} fast brackets at the open, {start.year}-{end.year}",
        purpose=(f"D-344: the shares of a fast 1:1 bracket in one {q['ticker']} measured on one-second bars at the "
                 f"{' and '.join(q['slot_labels'])} CT slots on {q['market']}, development data {start} to {end} only, actual "
                 "prices; counts exported, never bars."),
        class_name="FlipMapNQSeconds",
        start=warm, end=end,
        body=fk.BODY_SECONDS, preamble=fk.preamble_seconds(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="flipmap",
        expected=expected,
        extra={"market": q["market"], "model": "flip_map", "variant": "seconds", "time_unit": "second",
               "window_ct": q["window_ct"], "slots_ct": q["slot_labels"], "times": q["p"]["times"],
               "widths_points": q["widths_points"], "delays_seconds": q["delays"], "box_seconds": q["box"],
               "within_seconds": q["within"], "ticker": q["ticker"], "tick": q["tick"], "point_value": q["point_value"],
               "scale": "actual", "exports": "counts per year, slot, width and entry delay (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/flip_map_seconds.yaml; D-344"},
    )


def _flipdir_spec() -> RunSpec:
    """D-371: the flip-direction atlas -- the 08:30 CT brackets both ways on one-second bars beside the measures known
    before 08:30, one record a day."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_direction()
    q = fk.params_direction(cfg)
    warm, start, end = fk.windows_direction(cfg)
    expected = f"""\
**The flip-direction atlas (D-371), {q['market']}, {start} to {end}** (from {warm} as warm-up, which feeds the 20-day
average range and the previous day but records nothing), at actual prices. Declared in `config/flip_direction.yaml`.
On every trading day the kit records the minute bars and, at the day's close, brings the {q['window_ct'][0]} to
{q['window_ct'][1]} CT second bars of the day's contract by one history request (R138's) and walks a long and a short
1:1 bracket in one {q['ticker']} at the {q['slot_ct']} CT open -- at {", ".join(q['width_labels'])} (fractions of the
20-day average range, and the declared flip's fixed points) -- on time and {q['delays'][1]} seconds late, each read for
at most {q['box']} seconds. **One record a day leaves** (D-120): the measures known before {q['slot_ct']} CT in ticks
(P, the gap, the overnight move, the last 60, 15 and 1 minutes, the room to the day's high and low, the previous
session's move and its close's room to its high and low), the 20-day range, the widths, each bracket's outcome, and the
seconds and scratch P&L of two widths.

**Logs**: `{fk.FLIPDIR_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders,
contract switches, lost contracts, early closes, minute bars, `secbars` second bars received, `nosec` days whose window
the history could not serve, `short` thin windows, `records` days recorded, `noatr` days without the 20-day range,
`noprev` days without the previous day on the same contract, `nomeas` days without a bar by 08:30) and `END`. Expect
about 3,900 days and sixteen emits, `records` equal to `days`, `noatr` zero, `noprev` a few a year (contract rolls),
`lost` and `nosec` near zero, `secbars` near 780 a day. The run reads about three million second bars by history; if it
hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer days than that, or `nosec` is a large share of the days.
"""
    return RunSpec(
        run_id=fk.FLIPDIR_RUN,
        title=f"Flip-direction atlas: {q['market']} 08:30 brackets both ways beside the pre-open measures, "
              f"{start.year}-{end.year}",
        purpose=(f"D-371: whether anything known before {q['slot_ct']} CT tells the side of the open's first move -- "
                 f"the {q['slot_ct']} CT brackets both ways on one-second bars and the pre-open measures, one record a "
                 f"day, {q['market']} development data {start} to {end} only, actual prices; per-day numbers exported, "
                 "never bars."),
        class_name="FlipDirectionNQ",
        start=warm, end=end,
        body=fk.BODY_DIRECTION, preamble=fk.preamble_direction(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="flipdir",
        expected=expected,
        extra={"market": q["market"], "model": "flip_direction", "variant": "direction", "time_unit": "second",
               "window_ct": q["window_ct"], "slot_ct": q["slot_ct"], "width_labels": q["width_labels"],
               "fractions": q["fractions"], "fixed_ticks": q["fixed_ticks"], "delays_seconds": q["delays"],
               "box_seconds": q["box"], "ticker": q["ticker"], "tick": q["tick"], "point_value": q["point_value"],
               "scale": "actual", "exports": "one record a day: the pre-open measures and the brackets' outcomes (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/flip_direction.yaml; D-371"},
    )


def _flipany_spec() -> RunSpec:
    """D-373: the any-time direction atlas -- the measures and a 1:1 bracket both ways at every half hour of the
    regular session, sized to each slot's typical ten-minute range, one record a day."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_anytime()
    q = fk.params_anytime(cfg)
    warm, start, end = fk.windows_anytime(cfg)
    expected = f"""\
**The any-time direction atlas (D-373), {q['market']}, {start} to {end}** (from {warm} as warm-up, which feeds each
slot's 20-day range history but records nothing), at actual prices. Declared in `config/flip_anytime.yaml`. At each of
{len(q['slots'])} slots ({q['slot_labels'][0]} to {q['slot_labels'][-1]} CT, every half hour) the kit measures what is
known at the slot and, at the day's close, brings that slot's second bars by one history request (R138's) and walks a
long and a short 1:1 bracket in one {q['ticker']} at {" and ".join(q['width_labels'])} of the slot's mean ten-minute
range (never under {q['min_ticks']} ticks), on time and {q['delays'][1]} seconds late, each for at most {q['box']}
seconds. **One record a day leaves** (D-120): per slot the widths, the measures in ticks and each bracket's outcome.

**Logs**: `{fk.FLIPANY_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders,
switches, lost contracts, early closes, minute bars, `secbars`, `nosec` slot windows the history could not serve,
`short` thin windows, `records`, `nomeas`, `small` slot-days whose width is under the minimum, `closed` slots after an
early close, `nohist` slot-days without 20 days of range, `walked` slot-days walked) and `END`. Expect about 1,375 days
and six emits, `records` equal to `days`, `walked` near thirteen a day, `nosec` and `lost` near zero. The run makes about
18,000 second-bar history requests; if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer days than that, or `nosec` is a large share of the slot-days.
"""
    return RunSpec(
        run_id=fk.FLIPANY_RUN,
        title=f"Any-time direction atlas: {q['market']} half-hourly brackets both ways beside the measures, "
              f"{start.year}-{end.year}",
        purpose=(f"D-373: whether a measure known at a moment tells the side of the next move, at every half hour of "
                 f"{q['market']}'s regular session -- brackets both ways on one-second bars and the measures, one record "
                 f"a day, development data {start} to {end} only, actual prices; per-day numbers exported, never bars."),
        class_name="FlipAnytimeNQ",
        start=warm, end=end,
        body=fk.BODY_ANYTIME, preamble=fk.preamble_anytime(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="flipany",
        expected=expected,
        extra={"market": q["market"], "model": "flip_anytime", "variant": "anytime", "time_unit": "second",
               "slots_ct": q["slot_labels"], "slots": q["slots"], "width_labels": q["width_labels"],
               "fractions": q["fractions"], "min_ticks": q["min_ticks"], "delays_seconds": q["delays"],
               "box_seconds": q["box"], "ticker": q["ticker"], "tick": q["tick"], "point_value": q["point_value"],
               "scale": "actual", "exports": "one record a day: per slot the measures and the brackets' outcomes (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/flip_anytime.yaml; D-373"},
    )


def _flipdesign_spec() -> RunSpec:
    """D-375: the flip design map -- the 08:30 flip at widths from 20 to 100 points, both sides, in a thirty-minute box,
    with each bracket's seconds and the marks at the shorter boxes, beside the pre-08:30 measures; one record a day."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_design()
    q = fk.params_design(cfg)
    warm, start, end = fk.windows_design(cfg)
    widths = ", ".join(f"{w:g}" for w in q["widths_points"])
    expected = f"""\
**The flip design map (D-375), {q['market']}, {start} to {end}** (from {warm} as warm-up, which feeds the previous day
but records nothing), at actual prices. Declared in `config/flip_design.yaml`. On every trading day the kit records the
minute bars for D-371's pre-08:30 measures and, at the day's close, brings the {q['window_ct'][0]} to
{q['window_ct'][1]} CT second bars by one history request (R138's) and walks a long and a short 1:1 bracket in one
{q['ticker']} at the {q['slot_ct']} CT open at {widths} points, on time and {q['delays'][1]} seconds late, each for at
most {q['box']} seconds, recording each bracket's seconds to resolution and the price at
{", ".join(str(m) for m in q['marks'])} seconds after the entry. **One record a day leaves** (D-120).

**Logs**: `{fk.FLIPDESIGN_PREFIX}|HEAD` (days, warm-up days, entries, emits -- one per year -- orders, switches, lost
contracts, early closes, minute bars, `secbars`, `nosec` days the history could not serve, `short` thin windows,
`records`, `noprev` days without the previous day on the same contract, `nomeas` days without a bar by 08:30, `noentry`
days without an entry bar) and `END`. Expect about 1,375 days and six emits, `records` equal to `days`, `nosec`, `lost`
and `noentry` near zero, `secbars` near 2,000 a day.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer days than that, or `nosec` is a large share of the days.
"""
    return RunSpec(
        run_id=fk.FLIPDESIGN_RUN,
        title=f"Flip design map: {q['market']} 08:30 brackets of {widths} points both ways in a thirty-minute box, "
              f"{start.year}-{end.year}",
        purpose=(f"D-375: the 08:30 flip's width, box and side -- brackets both ways on one-second bars with their "
                 f"resolution times and marks beside the pre-08:30 measures, one record a day, {q['market']} "
                 f"development data {start} to {end} only, actual prices; per-day numbers exported, never bars."),
        class_name="FlipDesignNQ",
        start=warm, end=end,
        body=fk.BODY_DESIGN, preamble=fk.preamble_design(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="flipdesign",
        expected=expected,
        extra={"market": q["market"], "model": "flip_design", "variant": "design", "time_unit": "second",
               "window_ct": q["window_ct"], "slot_ct": q["slot_ct"], "widths_points": q["widths_points"],
               "marks_seconds": q["marks"], "delays_seconds": q["delays"], "box_seconds": q["box"],
               "ticker": q["ticker"], "tick": q["tick"], "point_value": q["point_value"], "scale": "actual",
               "exports": "one record a day: the measures, each bracket's outcome and seconds, the marks (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/flip_design.yaml; D-375"},
    )


def _collect_spec() -> RunSpec:
    """D-381: the collect map -- uneven brackets whose target makes a winning day, at every slot, in boxes to two hours,
    on minute bars with the tied minutes settled on second bars; counts only."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_collect()
    q = fk.params_collect(cfg)
    warm, start, end = fk.windows_collect(cfg)
    mults = ", ".join(f"{m:g}" for m in q["stop_multiples"])
    targets = ", ".join(f"{t:g} points on {n}" for n, t in zip(q["contracts"], q["targets_points"]))
    boxes = ", ".join(str(b) for b in q["boxes"])
    expected = f"""\
**The collect map (D-381), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records nothing), at actual
prices. Declared in `config/collect_map.yaml`. On every trading day the kit records the minute bars and, at the day's
close, walks a long and a short bracket at each of {len(q['slots'])} slots (every hour start from 17:00 to 14:00 CT and
08:30), on time and a minute late: a ${q['gross_dollars']:g} target ({targets} {q['micro']}) with stops of {mults}
times the target, in boxes of {boxes} minutes. A minute that first reaches a bracket's target and its stop is settled on
its second bars by a history request. FOMC days and early closes carry no bracket; on a BLS 08:30 ET release day a
bracket still open is closed before 07:30 CT. **Only counts leave** (D-120), one emit a year.

**Logs**: `{fk.COLLECT_PREFIX}|HEAD` (days, warm-up days, entries -- walks: a slot, a delay and a side --, emits, orders,
switches, lost contracts, early closes, minute bars, `fomc` and `bls` days, `ties` -- minutes settled by second bars --,
`secreq` history requests, `secbars`, `nosec` requests that returned nothing, `nosecbar` tied minutes without a second
bar, and the history request's form) and `END`. Expect about 1,375 days, six emits, `entries` near 90 a full day,
`nosec` and `nosecbar` small beside `ties`, `lost` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `HEAD` reports far
fewer days than that, or `nosecbar` is a large share of `ties`.
"""
    return RunSpec(
        run_id=fk.COLLECT_RUN,
        title=f"Collect map: {q['market']} ${q['gross_dollars']:g}-target brackets, stops {mults}x, every hour, "
              f"{start.year}-{end.year}",
        purpose=(f"D-381: the XFA's winning-day brackets -- a ${q['gross_dollars']:g} target with stops one to eight times "
                 f"wider, at every hour of the trading day, in boxes to two hours, on time and a minute late, both sides "
                 f"pooled; minute bars with tied minutes settled on second bars, {q['market']} development data {start} to "
                 f"{end} only, actual prices; counts exported, never bars."),
        class_name="CollectMapNQ",
        start=warm, end=end,
        body=fk.BODY_COLLECT, preamble=fk.preamble_collect(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="collect",
        expected=expected,
        extra={"market": q["market"], "model": "collect_map", "variant": "collect", "time_unit": "minute",
               "slots_ct": q["slot_labels"], "contracts": q["contracts"], "targets_points": q["targets_points"],
               "stop_multiples": q["stop_multiples"], "boxes_minutes": q["boxes"], "delays_minutes": q["delays"],
               "ticker": q["ticker"], "tick": q["tick"], "micro": q["micro"], "scale": "actual",
               "exports": "counts per year, slot, contracts, stop multiple, box and delay; ties, gaps and cut boxes (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/collect_map.yaml; D-381"},
    )


def _dst_spec() -> RunSpec:
    """D-386 (7): the clock check across daylight-saving changes -- six one-minute bars' ranges a day."""
    from propedge.data import flip_kit as fk

    cfg = fk.config_dst()
    q = fk.params_dst(cfg)
    warm, start, end = fk.windows_dst(cfg)
    bars = ", ".join(q["bar_labels"])
    expected = f"""\
**The clock check (D-386 (7)), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records nothing), at
actual prices. Declared in `config/dst_check.yaml`. On every trading day the kit records the minute bars on the kits'
own clock and, at the day's close, the high less low in ticks of the one-minute bars starting at {bars} CT. **One short
record a day leaves** (D-120), one emit a year; the release days are the scorer's, from its calendars.

**Logs**: `{fk.DST_PREFIX}|HEAD` (days, warm-up days, entries -- bars read --, emits, orders, switches, lost contracts,
early closes, minute bars, `records`, `missing` bars) and `END`. Expect about 1,420 days, six emits, `records` equal to
`days`, `missing` small (early closes miss the afternoon bars).

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that.
"""
    return RunSpec(
        run_id=fk.DST_RUN,
        title=f"Clock check: {q['market']} one-minute ranges at {bars} CT, {start.year}-{end.year}",
        purpose=(f"D-386 (7): the deployment protocol's clock test across daylight-saving changes -- the scheduled "
                 f"releases' spikes on the kits' own clock; {q['market']} development data {start} to {end} only; "
                 f"six ranges a day exported, never bars."),
        class_name="DstCheckNQ",
        start=warm, end=end,
        body=fk.BODY_DST, preamble=fk.preamble_dst(cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="dst",
        expected=expected,
        extra={"market": q["market"], "model": "dst_check", "variant": "dst", "time_unit": "minute",
               "bars_start_ct": q["bar_labels"], "ticker": q["ticker"], "tick": q["tick"], "scale": "actual",
               "exports": "one record a day: six one-minute ranges in ticks (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/dst_check.yaml; D-386"},
    )


def _t23_spec(run: str) -> RunSpec:
    """D-416: T23's per-trade capture -- brackets at the collect map's fixed times with no box, one record a walk."""
    from propedge.data import t23_kit as tk

    cfg = tk.config_t23()
    q = tk.params_t23(run, cfg)
    warm, start, end = q["warm"], q["start"], q["end"]
    brackets = ", ".join(f"{T:g}/{S:g}" for T, S in q["brackets"])
    expected = f"""\
**T23's per-trade capture (D-416), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records nothing), at
actual prices. Declared in `config/t23_capture.yaml`. On every trading day the kit records the minute bars and, at the
day's close, walks a long and a short entry at each of {len(q['slots'])} fixed times (every hour start from 17:00 to
14:00 CT and 08:30), on time and two bars late, and follows each of nine brackets (target/stop in points: {brackets})
to its target, its stop or the day's end -- no time limit. A minute that first reaches a bracket's target and its stop
is settled on its second bars. FOMC days and early closes carry no walk; on a BLS 08:30 ET release day a bracket still
open is ended before 07:30 CT. **Only records leave** (D-120): one per walk -- each bracket's outcome and minutes --
and one per day (its kind and the last hour's direction at each fixed time), one emit a year.

**Logs**: `{tk.T23_PREFIX}|HEAD` (days, warm-up days, entries -- walks --, emits, orders, switches, lost contracts,
early closes, bars, `fomc` and `bls` days, `ties`, `secreq`, `secbars`, `nosec`, `nosecbar`, `records`, `dayrecs` and
the history request's form) and `END`. Expect `days` near {'760' if end.year == 2022 else '630'}, `entries` near 92 a
full day and equal to `records`, `dayrecs` equal to `days`, `orders` under 10,000, `nosecbar` small beside `ties`,
`lost` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `orders` reached
10,000, `HEAD` reports far fewer days than that, or `nosecbar` is a large share of `ties`.
"""
    return RunSpec(
        run_id=run,
        title=f"T23 capture: {q['market']} brackets at fixed times, no time limit, {start.year}-{end.year}",
        purpose=(f"D-416: per-trade records of nine brackets (20 to 40-point stops at 1:1 and 1.5:1, and a flip) at the "
                 f"collect map's fixed times, both sides, on time and two bars late, each run to its target, stop or the "
                 f"day's end; minute bars with tied minutes settled on second bars; {q['market']} development data "
                 f"{start} to {end} only, actual prices; records exported, never bars."),
        class_name="T23CaptureNQ",
        start=warm, end=end,
        body=tk.BODY_T23, preamble=tk.preamble_t23(run, cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="t23",
        expected=expected,
        extra={"market": q["market"], "model": "t23_capture", "variant": "t23", "time_unit": "minute",
               "slots_ct": q["slot_labels"], "brackets_points": [list(b) for b in q["brackets"]],
               "delays_minutes": q["delays"], "ticker": q["ticker"], "tick": q["tick"], "micro": q["micro"],
               "scale": "actual",
               "exports": "one record per walk (each bracket's outcome and minutes) and per day (kind, A3) (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/t23_capture.yaml; D-416"},
    )


def _t24_spec(run: str) -> RunSpec:
    """D-428: T24's per-trade capture -- T23's kit (D-416) on `config/t24_capture.yaml`: twelve brackets (20, 40 and
    60-point stops at 1:1 to 3:1) at the same fixed times, on time and five bars late, three runs."""
    from propedge.data import t23_kit as tk

    cfg = tk.config_for_run(run)
    q = tk.params_t23(run, cfg)
    warm, start, end = q["warm"], q["start"], q["end"]
    brackets = ", ".join(f"{T:g}/{S:g}" for T, S in q["brackets"])
    near = round(252 * ((end - start).days + 1) / 365.25 * 0.97 / 10) * 10
    expected = f"""**T24's per-trade capture (D-428), {q['market']}, {start} to {end}** (from {warm} as warm-up, which records nothing), at
actual prices. Declared in `config/t24_capture.yaml`; the kit is T23's (D-416). On every trading day the kit records the
minute bars and, at the day's close, walks a long and a short entry at each of {len(q['slots'])} fixed times (every hour
start from 17:00 to 14:00 CT and 08:30), on time and five bars late, and follows each of {len(q['brackets'])} brackets
(target/stop in points: {brackets}) to its target, its stop or the day's end -- no time limit. A minute that first
reaches a bracket's target and its stop is settled on its second bars. FOMC days and early closes carry no walk; on a
BLS 08:30 ET release day a bracket still open is ended before 07:30 CT. **Only records leave** (D-120): one per walk --
each bracket's outcome and minutes -- and one per day (its kind and the last hour's direction at each fixed time), one
emit a year.

**Logs**: `{tk.T23_PREFIX}|HEAD` (days, warm-up days, entries -- walks --, emits, orders, switches, lost contracts,
early closes, bars, `fomc` and `bls` days, `ties`, `secreq`, `secbars`, `nosec`, `nosecbar`, `records`, `dayrecs` and
the history request's form) and `END`. Expect `days` near {near}, `entries` near 92 a full day and equal to `records`,
`dayrecs` equal to `days`, `orders` under 10,000, `nosecbar` small beside `ties`, `lost` near zero.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, `orders` reached
10,000, `HEAD` reports far fewer days than that, or `nosecbar` is a large share of `ties`.
"""
    return RunSpec(
        run_id=run,
        title=f"T24 capture: {q['market']} wide brackets at fixed times, no time limit, {start.year}-{end.year}",
        purpose=(f"D-428: per-trade records of twelve brackets (20, 40 and 60-point stops at 1:1, 1.5:1, 2:1 and 3:1) at "
                 f"the collect map's fixed times, both sides, on time and five bars late, each run to its target, stop or "
                 f"the day's end; minute bars with tied minutes settled on second bars; {q['market']} development data "
                 f"{start} to {end} only, actual prices; records exported, never bars."),
        class_name="T24CaptureNQ",
        start=warm, end=end,
        body=tk.BODY_T23, preamble=tk.preamble_t23(run, cfg),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="t23",
        expected=expected,
        extra={"market": q["market"], "model": "t24_capture", "variant": "t24", "time_unit": "minute",
               "slots_ct": q["slot_labels"], "brackets_points": [list(b) for b in q["brackets"]],
               "delays_minutes": q["delays"], "ticker": q["ticker"], "tick": q["tick"], "micro": q["micro"],
               "scale": "actual",
               "exports": "one record per walk (each bracket's outcome and minutes) and per day (kind, A3) (D-120)",
               "ingest": "scripts/ingest_flip_run.py", "source": "config/t24_capture.yaml; D-428"},
    )


def _t24c_spec(run: str) -> RunSpec:
    """D-439: T24-GF15b's one confirmation capture -- T24's kit on `config/t24_confirm.yaml` (NQ's held-back window),
    its registration embedded (D-81)."""
    from propedge.data import t23_kit as tk

    cfg = tk.config_for_run(run)
    if not cfg.get("prereg_id") or str(cfg["prereg_id"]).lower() == "pending":
        raise ValueError("config/t24_confirm.yaml has no registered prereg_id; the kit is not generated (D-81)")
    base = _t24_spec(run)
    q = tk.params_t23(run, cfg)
    expected = base.expected.replace("T24's per-trade capture (D-428)",
                                     f"T24-GF15b's confirmation capture (D-439), under {cfg['prereg_id']}")
    expected = expected.replace("Declared in `config/t24_capture.yaml`", "Declared in `config/t24_confirm.yaml`")
    from dataclasses import replace

    return replace(base, title=f"T24 confirmation: {q['market']} held-back window, {q['start']} to {q['end']}",
                   purpose=(f"D-439, {cfg['prereg_id']}: T24-GF15b's one confirmation -- the same twelve brackets at the "
                            f"same fixed times, both sides, on time and five bars late, on NQ's held-back window "
                            f"{q['start']} to {q['end']}; records exported, never bars."),
                   class_name="T24ConfirmNQ", expected=expected,
                   extra={**base.extra, "model": "t24_confirm", "variant": "t24c", "prereg": cfg["prereg_id"],
                          "confirm": True, "source": "config/t24_confirm.yaml; D-439; " + str(cfg["prereg_id"])},
                   prereg_id=str(cfg["prereg_id"]))


def _t24_development_continues() -> bool:
    """D-440: T24-GF15b's development test reads PASS or CONTINUE (`results/t24_gf15b_gate.csv`'s verdict row)."""
    import pandas as pd

    from propedge import RESULTS_DIR

    f = RESULTS_DIR / "t24_gf15b_gate.csv"
    if not f.is_file():
        return False
    v = pd.read_csv(f, low_memory=False)
    v = v[v["section"] == "verdict"]
    return bool(len(v)) and str(v.iloc[0]["verdict"]) in ("PASS", "CONTINUE")


def _t24c_specs() -> dict[str, Callable[[], RunSpec]]:
    """As P-05's and P-06's: the kit exists only under a runnable registration; once its outcome is recorded the
    committed kit stays as it ran and leaves SPECS."""
    from propedge.data import t23_kit as tk
    from propedge.data.cloud_guard import confirmation_run_authorised

    cfg = tk.config_t23(tk.fk.CONFIG_DIR / "t24_confirm.yaml")
    if not confirmation_run_authorised(str(cfg.get("prereg_id") or "pending")):
        return {}
    if not _t24_development_continues():                  # D-440: no kit before a development PASS or CONTINUE
        return {}
    return {str(r["run"]): (lambda rid=str(r["run"]): _t24c_spec(rid)) for r in cfg["runs"]}


T24C_SPECS: dict[str, Callable[[], RunSpec]] = _t24c_specs()


FLIP_SPECS: dict[str, Callable[[], RunSpec]] = {"R137-flipmap-NQ": _flip_spec, "R138-flipmap-NQ-seconds": _flip_seconds_spec,
                                                "R142-flipdir-NQ": _flipdir_spec, "R143-flipany-NQ": _flipany_spec,
                                                "R144-flipdesign-NQ": _flipdesign_spec, "R145-collect-NQ": _collect_spec,
                                                "R146-dst-NQ": _dst_spec,
                                                # D-416: T23's per-trade capture, two runs
                                                "R147-t23-NQ-2022": lambda: _t23_spec("R147-t23-NQ-2022"),
                                                "R148-t23-NQ-2025": lambda: _t23_spec("R148-t23-NQ-2025"),
                                                # D-428: T24's per-trade capture, three runs
                                                "R149-t24-NQ-2021": lambda: _t24_spec("R149-t24-NQ-2021"),
                                                "R150-t24-NQ-2023": lambda: _t24_spec("R150-t24-NQ-2023"),
                                                "R151-t24-NQ-2025": lambda: _t24_spec("R151-t24-NQ-2025")}


def _confirm_specs() -> dict[str, Callable[[], RunSpec]]:
    """As C-007's: the confirmation kit is generated only under a runnable registration. Once its outcome is recorded
    (P-05 complete, D-233) the committed kit stays exactly as it ran and is kept out of SPECS."""
    from propedge.data import rmap_kit as rk
    from propedge.data.cloud_guard import confirmation_run_authorised

    pid = str(rk.confirm_config().get("prereg_id") or "pending")
    return {rk.CONFIRM_RUN: _rmap_confirm_spec} if confirmation_run_authorised(pid) else {}


CONFIRM_SPECS: dict[str, Callable[[], RunSpec]] = _confirm_specs()


def _regime_spec(market: str) -> RunSpec:
    """T15, D-238: the whole-day regime map, one market over the whole development period, at actual prices."""
    from propedge.data import regime_kit as rk

    warm, start, end = rk.dates()
    q = rk.params(market)
    pts = ", ".join(f"{x:g}" for x in q["stops_points"])
    mults = ", ".join(f"{x:g}" for x in q["range_multiples"])
    expected = f"""\
**The whole-day regime map (T15, D-238), {market}, {start} to {end}** (from {warm} as warm-up, which only fills the
trailing range). Declared in `config/regime_map.yaml`. On Topstep's trading day -- 17:00 CT the evening before to the
15:10 CT flatten -- at {len(q['times'])} decisions (every 30 minutes from 17:00 to 14:30 CT and every 5 minutes through
{q['open_ct']} CT), a long and a short bracket at each fixed stop ({pts} points) and at {mults} times the trailing
{q['range_days']}-day range, walked to its target at {', '.join(f'{r:g}' for r in q['rr'])}R, its stop, or the day's last
bar, at **actual prices**. **Only counts leave** (D-120): per year, decision and stop the brackets at each target first
and stop first, the stops that gapped and by how much, the minutes to resolution; per decision the entry minute's
spread; per 30-minute window the volume and range; per year the sessions' range and volume.

**Logs**: `{rk.REGIME_PREFIX}|HEAD` (days in the window, warm-up days, entries, emits -- one per year -- orders,
contract switches, lost contracts, early closes, days without a trailing range, bad bars, bars and quotes recorded) and
`END`. Expect about 4,000 days, 17 emits, `lost` near zero, `noatr` small, `quotes` close to `bars`. The run takes
longer than the resolution map's (perhaps half an hour); if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose counts do not add up.
"""
    return RunSpec(
        run_id=rk.REGIME_RUNS[market],
        title=f"Regime map: {market}, {start.year}-{end.year}, the whole day at actual prices",
        purpose=(f"T15, D-238: bracket resolution, stop overshoot, spread, volume and range through the whole trading "
                 f"day on {market}, year by year, development data {start} to {end} only (D-237); counts exported, "
                 "never bars."),
        class_name=f"Regime{market}",
        start=warm, end=end,
        body=rk.BODY, preamble=rk.preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="regime",
        expected=expected,
        extra={"market": market, "model": "regime_map", "stops_points": q["stops_points"],
               "range_multiples": q["range_multiples"], "range_days": q["range_days"], "times": q["times"],
               "rr": list(q["rr"]), "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "counts per year, decision, stop and R; spreads; 30-minute windows; sessions (D-120)",
               "ingest": "scripts/ingest_regime_run.py", "source": "config/regime_map.yaml; D-237, D-238"},
    )


def _regime_specs() -> dict[str, Callable[[], RunSpec]]:
    from propedge.data import regime_kit as rk

    return {rid: (lambda mk=mk: _regime_spec(mk)) for rid, mk in rk.REGIME_KITS.items()}


REGIME_SPECS: dict[str, Callable[[], RunSpec]] = _regime_specs()


def _regime_confirm_spec(run_id: str | None = None) -> RunSpec:
    """D-242: NQB2's one confirmation on the held-back year, under its registered pre-registration only."""
    from propedge.data import regime_kit as rk

    c = rk.confirm_config()
    if not c.get("prereg_id") or str(c["prereg_id"]).lower() == "pending":
        raise ValueError("config/nqb2_confirmation.yaml has no registered prereg_id; the kit is not generated (D-81)")
    run_id = run_id or rk.CONFIRM_RUN
    q = rk.confirm_params(c)
    warm, start, end = rk.confirm_dates(c)
    legs = ", ".join(f"{k} {v['R']:g}:1 on {v['stop_points']:g} points" for k, v in c["legs"].items())
    expected = f"""\
**NQB2's confirmation (D-242), under {c['prereg_id']}: {c['market']}, {start} to {end}** (from {warm} as warm-up, which
records nothing). Fixed in `config/nqb2_confirmation.yaml` before any of this window was read. The regime map's kit at
actual prices, its decision times cut to the registered {len(q['times'])} and its brackets to the registered two --
{legs} -- counted by calendar month, so no other cell of the held-back year is counted. **Only counts leave** (D-120):
per month, decision and leg the brackets at the target first, the stop first and still open, the stops that gapped and
by how much; per month and decision the entry minute's spread; per month the day count.

**Logs**: `{rk.REGIME_PREFIX}|HEAD` and `END`, as the map's kits. Expect about 250 days, two emits, `lost` near zero,
`noatr` 0, `quotes` close to `bars`.

**The run is unusable** (D-230's single test, judged from the log before any count is parsed) if `END` is missing, the
log or the operator reports an error or a time limit, or `HEAD` reports fewer than {c['min_days']:,} days; or if the
parser refuses its output. It is recorded in `unusable.json` and its counts are not used; one fixed kit may follow, and
a second unusable run is a FAIL. A refusal of the procedure (a missing or wrong download, the ran code) is retried on
this backtest's own files and is not a new run.
"""
    return RunSpec(
        run_id=run_id,
        title=f"NQB2 confirmation: {c['market']} brackets at actual prices, {start} to {end}",
        purpose=(f"D-242, {c['prereg_id']}: NQB2's one confirmation -- how often its two registered brackets resolve "
                 f"before Topstep's 15:10 flatten on {c['market']}, {start} to {end}, the held-back year, and at what "
                 "cost; counts exported, never bars."),
        class_name=f"RegimeConfirm{c['market']}",
        start=warm, end=end,
        body=rk.BODY_CONFIRM, preamble=rk.confirm_preamble(c),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="regime",
        expected=expected,
        extra={"market": c["market"], "model": c["model"], "prereg": c["prereg_id"], "confirm": True,
               "scale": "actual", "stops_points": q["stops_points"], "range_multiples": [], "times": q["times"],
               "rr": list(q["rr"]), "keep": [list(x) for x in q["keep"]], "micro": q["micro"],
               "micro_tick": q["micro_tick"], "months": list(c["months"]),
               "exports": "counts per month, decision and registered leg (D-120, D-242)",
               "ingest": "scripts/ingest_regime_run.py",
               "source": "config/nqb2_confirmation.yaml; D-242; " + str(c["prereg_id"])},
        prereg_id=str(c["prereg_id"]),
    )


def _regime_confirm_specs() -> dict[str, Callable[[], RunSpec]]:
    """As NQB1's: the confirmation kit is generated only under a runnable registration (its first run; the fix needs a
    decision first). Once the outcome is recorded the committed kit stays exactly as it ran and is kept out of SPECS."""
    from propedge.data import regime_kit as rk
    from propedge.data.cloud_guard import confirmation_run_authorised

    pid = str(rk.confirm_config().get("prereg_id") or "pending")
    return {rk.CONFIRM_RUN: _regime_confirm_spec} if confirmation_run_authorised(pid) else {}


REGIME_CONFIRM_SPECS: dict[str, Callable[[], RunSpec]] = _regime_confirm_specs()


def _setup_spec(market: str) -> RunSpec:
    """T15 item 8, D-245: the session-setup screen, one market over the whole development period, at actual prices."""
    from propedge.data import setup_kit as sk

    warm, start, end = sk.dates()
    q = sk.params(market)
    wins = ", ".join(f"{w['name']} {w['start_ct']}" for w in sk.config()["windows"])
    expected = f"""\
**The session-setup screen SS1 (T15 item 8, D-245), {market}, {start} to {end}** (from {warm} as warm-up, which only
fills the trailing range). Declared in `config/session_setups.yaml`. On each full session of Topstep's trading day, in
each of {len(q['windows'])} windows -- {wins} CT, signals within {q['windows'][0][1]} minutes of the start -- the first
signal of each of {len(q['rules'])} rules (opening-range breakout and fade, prior-range break and rejection, early
momentum) enters at the next bar's open and its bracket walks at {', '.join(f'{x:g}' for x in q['range_multiples'])} times
the trailing {q['range_days']}-day range to {', '.join(f'{r:g}' for r in q['rr'])}R, its stop, or the day's last bar, at
**actual prices**. **Only counts leave** (D-120): per year, window, rule, direction and stop the trades at each target
first and stop first, the stops that gapped and by how much, the entry minute's spread and the minutes to resolution;
per year the sessions.

**Logs**: `{sk.SETUP_PREFIX}|HEAD` (days, warm-up days, entries, emits -- one per year -- orders, contract switches, lost
contracts, early closes, days without a trailing range, bad bars, bars and quotes recorded) and `END`. Expect about
4,000 days, 17 emits, `lost` near zero, `noatr` small, `quotes` close to `bars`. The run takes about as long as the
regime map's (half an hour or so); if it hits a time limit, copy the message.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose counts do not add up.
"""
    return RunSpec(
        run_id=sk.SETUP_RUNS[market],
        title=f"Session-setup screen: {market}, {start.year}-{end.year}, six windows, eleven rules, actual prices",
        purpose=(f"T15 item 8, D-245: which entry setups, at which times of the day, carry a net edge per trade on "
                 f"{market}; development data {start} to {end} only (D-237); counts exported, never bars."),
        class_name=f"Setups{market}",
        start=warm, end=end,
        body=sk.BODY, preamble=sk.preamble(market),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="setups",
        expected=expected,
        extra={"market": market, "model": "session_setups", "windows": [list(w) for w in q["windows"]],
               "window_names": q["window_names"], "rules": q["rules"], "range_multiples": q["range_multiples"],
               "range_days": q["range_days"], "rr": list(q["rr"]), "micro": q["micro"], "micro_tick": q["micro_tick"],
               "scale": "actual", "exports": "counts per year, window, rule, direction, stop and R; sessions (D-120)",
               "ingest": "scripts/ingest_setup_run.py", "source": "config/session_setups.yaml; D-245"},
    )


def _orb_spec(market: str) -> RunSpec:
    """T15 item 9, D-249, D-250: ORB1's development run, one market, 2009-2019, one record per day, at actual
    prices."""
    from propedge.data import orb_kit as ok
    from propedge.outcomes.orb_core import OR_MINS

    warm, start, end = ok.dates("dev")
    q = ok.params(market)
    expected = f"""\
**ORB1's development run (T15 item 9, D-249, D-250), {market}, {start} to {end}** (from {warm} as warm-up, which only
fills the 14-day histories). Declared in `config/orb_model.yaml`: Zarattini, Barbon & Aziz (2024)'s opening-range
breakout on the 08:30 CT open, on the 5-, 15-, 30- and 60-minute ranges -- direction from the range's candle, a stop
order at the range's edge, a stop at {q['stop_atr']:g} of the 14-day ATR -- recorded once a day: the ATR, the overnight
gap, the pre-open's move and volume, and for each range its relative volume, the signed drift after it, and its
trade's fill, stop, 15:08 close and the first touch of {', '.join(f'{r:g}' for r in q['rr'])}R before the stop, at
**actual prices**. **Only these day records leave** (D-120), never bars. The check years (2020 to June 2025) are a
separate run, made only after the pre-registration.

**Logs**: `{ok.ORB_PREFIX}|HEAD` (version 2; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect about
2,700 days, 11 emits, roughly 1,300 to 2,700 orders (each carries a piece of the records; the orders' own fills mean
nothing), `lost` near zero, `noatr` small.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=ok.ORB_RUNS[market],
        title=(f"ORB1 development: {market}, {start.year}-{end.year}, the opening-range breakout on four ranges, day "
               f"records"),
        purpose=(f"T15 item 9, D-249, D-250: the opening-range breakout's fingerprints and trades on {market}, the 5-, "
                 f"15-, 30- and 60-minute ranges, development data {start} to {end} only; one record per day exported, "
                 f"never bars."),
        class_name=f"Orb{market}Dev",
        start=warm, end=end,
        body=ok.BODY, preamble=ok.preamble(market, "dev"),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="orb",
        expected=expected,
        extra={"market": market, "model": "ORB1", "run": "dev", "ranges": list(OR_MINS), "record_version": 2,
               "rr": list(q["rr"]), "stop_atr": q["stop_atr"],
               "atr_days": q["atr_days"], "rv_days": q["rv_days"], "micro": q["micro"], "micro_tick": q["micro_tick"],
               "scale": "actual", "exports": "one record per day (D-120)", "ingest": "scripts/ingest_orb_run.py",
               "source": "config/orb_model.yaml; D-249; D-250; SSRN 4729284"},
    )


def _orb2_screen_spec(market: str) -> RunSpec:
    """T15 item 9, D-253: ORB2's screen -- ORB1's kit, unchanged, on the check years of config/orb_model.yaml (2020 to
    June 2025, development data under D-237), one market."""
    from propedge.data import orb_kit as ok
    from propedge.outcomes.orb_core import OR_MINS

    warm, start, end = ok.dates("check")
    q = ok.params(market)
    expected = f"""\
**ORB2's screen (T15 item 9, D-253), {market}, {start} to {end}** (from {warm} as warm-up, which only fills the 14-day
histories). ORB1's kit unchanged (`config/orb_model.yaml`; D-249, D-250): the opening-range breakout on the 08:30 CT
open, on the 5-, 15-, 30- and 60-minute ranges, one record per day -- the ATR, the gap, the pre-open, and for each range
its relative volume, the drift after it and its trade's fill, stop, 15:08 close and the first touch of
{', '.join(f'{r:g}' for r in q['rr'])}R before the stop -- at **actual prices**. **Only these day records leave** (D-120),
never bars. Its kill line is fixed in `config/orb2_model.yaml` before this run.

**Logs**: `{ok.ORB_PREFIX}|HEAD` (version 2; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect about
1,400 days, 6 emits, roughly 700 to 1,400 orders (each carries a piece of the records; the orders' own fills mean
nothing), `lost` near zero, `noatr` small.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=ok.ORB2_SCREEN_RUNS[market],
        title=f"ORB2 screen: {market}, {start.year}-{end.year}, ORB1's kit on the check years, day records",
        purpose=(f"T15 item 9, D-253: ORB2's screen -- ORB1's records on {market}, {start} to {end} (development data "
                 f"under D-237); one record per day exported, never bars."),
        class_name=f"Orb{market}Screen",
        start=warm, end=end,
        body=ok.BODY, preamble=ok.preamble(market, "check"),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="orb",
        expected=expected,
        extra={"market": market, "model": "ORB2", "run": "check", "ranges": list(OR_MINS), "record_version": 2,
               "rr": list(q["rr"]), "stop_atr": q["stop_atr"],
               "atr_days": q["atr_days"], "rv_days": q["rv_days"], "micro": q["micro"], "micro_tick": q["micro_tick"],
               "scale": "actual", "exports": "one record per day (D-120)", "ingest": "scripts/ingest_orb_run.py",
               "source": "config/orb_model.yaml; config/orb2_model.yaml; D-253; SSRN 4729284"},
    )


ORB_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk: _orb_spec(mk)) for mk, rid in __import__(
        "propedge.data.orb_kit", fromlist=["ORB_RUNS"]).ORB_RUNS.items()}
ORB_SPECS.update({
    rid: (lambda mk=mk: _orb2_screen_spec(mk)) for mk, rid in __import__(
        "propedge.data.orb_kit", fromlist=["ORB2_SCREEN_RUNS"]).ORB2_SCREEN_RUNS.items()})


def _orb3_spec(run_id: str) -> RunSpec:
    """T15 item 9, D-256: one of ORB3's three NQ runs, the grid's first passages per day, at actual prices."""
    from propedge.data import orb3_kit as k3

    warm, start, end = k3.dates(run_id)
    q = k3.params()
    expected = f"""\
**ORB3's records (T15 item 9, D-256), NQ, {start} to {end}** (from {warm} as warm-up, which only fills the 14-day
histories). ORB1's entry on the 5-, 15-, 30- and 60-minute ranges from 08:30 CT, recorded for ORB3's declared search
(`config/orb3_search.yaml`): for each range and each stop width of {', '.join(f'{s:g}' for s in q['stops'])} x the
14-day ATR, the first bar the stop is reached and the first bars {' and '.join(f'{r:g}' for r in q['favour_rr'])} x the
stop are traded through, the 15:08 close and the fill bar's close and excursions, at **actual prices**. **Only these day
records leave** (D-120), never bars.

**Logs**: `{k3.ORB3_PREFIX}|HEAD` (version 3; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect about
{round((end - start).days * 252 / 365, -1):.0f} days, {end.year - start.year + 1} emits, roughly 800 to 1,500 orders
(each carries a piece of the records; the orders' own fills mean nothing), `lost` near zero, `noatr` small.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=run_id,
        title=f"ORB3 records: NQ, {start.year}-{end.year}, the stop grid's first passages on four ranges",
        purpose=(f"T15 item 9, D-256: ORB3's declared search on NQ, {start} to {end} (development data under D-237); "
                 f"one record per day exported, never bars."),
        class_name=f"Orb3NQ{start.year % 100:02d}{end.year % 100:02d}",
        start=warm, end=end,
        body=k3.BODY, preamble=k3.preamble(run_id),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="orb3",
        expected=expected,
        extra={"market": k3.MARKET, "model": "ORB3", "record_version": 3, "stops": list(q["stops"]),
               "favour_rr": list(q["favour_rr"]), "atr_days": q["atr_days"], "rv_days": q["rv_days"],
               "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "one record per day (D-120)", "ingest": "scripts/ingest_orb3_run.py",
               "source": "config/orb3_search.yaml; D-256; SSRN 4729284"},
    )


ORB_SPECS.update({rid: (lambda rid=rid: _orb3_spec(rid)) for rid in __import__(
    "propedge.data.orb3_kit", fromlist=["ORB3_RUNS"]).ORB3_RUNS})


def _orb5_spec(run_id: str) -> RunSpec:
    """T16 item 3, D-264 to D-267: one of ORB5's three data-capture runs, re-walking an ORB3 run's days."""
    from propedge.data import orb5_kit as k5
    from propedge.data.regime_kit import REGIME_TAG_CHARS as TAG_CHARS
    from propedge.outcomes.orb5_core import ADD_RR, LAT_RR, LATENCY

    warm, start, end = k5.dates(run_id)
    q = k5.params()
    expected = f"""\
**ORB5's data capture (T16 item 3, D-264 to D-267), NQ, {start} to {end}** (from {warm} as warm-up, which only fills
the 14-day histories). It re-walks the days of {k5.ORB5_RUNS[run_id]} -- ORB1's entry on the 5-, 15-, 30- and
60-minute ranges from 08:30 CT -- and records only what those records lack: for each range and each stop width of
{', '.join(f'{s:g}' for s in q['stops'])} x the 14-day ATR, the first bar {', '.join(f'{r:g}' for r in ADD_RR)} x
the stop are traded through; the worst price of 15:07-15:10 CT; the bid-ask spread at the fill and flatten minutes; and
the entry a hand trader takes when the order can work only {LATENCY} minutes after the range closes (the same fill, a
chase at the next open, or a late stop), with its own stop and {', '.join(f'{r:g}' for r in LAT_RR)} x stop passages.
No hypothesis, nothing selected. **Only these day records leave** (D-120), never bars.

**Logs**: `{k5.ORB5_PREFIX}|HEAD` (version 7; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect the
same days, entries, early closes and days without the histories as {k5.ORB5_RUNS[run_id]} (the ingest checks it), and
about two orders per record (each year's records are one stream cut into tags of at most {TAG_CHARS} characters, so
a record spans tags; the orders' own fills mean nothing).

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=run_id,
        title=f"ORB5 capture: NQ, {start.year}-{end.year}, far targets, the 15:07-15:10 window, spreads, hand entry",
        purpose=(f"T16 item 3, D-264: ORB5's data capture on NQ, {start} to {end} (development data under D-237), "
                 f"re-walking {k5.ORB5_RUNS[run_id]}'s days; one record per day exported, never bars."),
        class_name=f"Orb5NQ{start.year % 100:02d}{end.year % 100:02d}",
        start=warm, end=end,
        body=k5.BODY, preamble=k5.preamble(run_id),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="orb5",
        expected=expected,
        extra={"market": k5.MARKET, "model": "ORB5", "record_version": 7, "stops": list(q["stops"]),
               "add_rr": list(ADD_RR), "latency_min": LATENCY, "lat_rr": list(LAT_RR),
               "joins": k5.ORB5_RUNS[run_id], "atr_days": q["atr_days"],
               "rv_days": q["rv_days"], "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "one record per day (D-120)", "ingest": "scripts/ingest_orb5_run.py",
               "source": "config/orb3_search.yaml; D-263; D-264; D-265; D-266; D-267"},
    )


ORB_SPECS.update({rid: (lambda rid=rid: _orb5_spec(rid)) for rid in __import__(
    "propedge.data.orb5_kit", fromlist=["ORB5_RUNS"]).ORB5_RUNS})


def _orb6_spec(run_id: str) -> RunSpec:
    """T16 item 9, D-276 to D-278: one of ORB6's three data-capture runs, re-walking an ORB3 run's days."""
    from propedge.data import orb6_kit as k6
    from propedge.data.regime_kit import REGIME_TAG_CHARS as TAG_CHARS
    from propedge.outcomes.orb5_core import LATENCY
    from propedge.outcomes.orb6_core import BENCH_SLOTS, RANGE_RR, RETEST_RR

    warm, start, end = k6.dates(run_id)
    q = k6.params()
    times = ", ".join(f"{(s + 1020) // 60 % 24:02d}:{s % 60:02d}" for s in BENCH_SLOTS)   # slots: minutes from 17:00
    expected = f"""\
**ORB6's data capture (T16 item 9, D-276 to D-278), NQ, {start} to {end}** (from {warm} as warm-up, which only fills
the 14-day histories). It re-walks the days of {k6.ORB6_RUNS[run_id]} -- ORB1's entry on the 5-, 15-, 30- and
60-minute ranges from 08:30 CT -- and records what ORB6's structural changes need: from the hand-traded entry
{LATENCY} minutes after the range closes, the stop one tick beyond the range's far side and the first bars it and
{', '.join(f'{r:g}' for r in RANGE_RR)} x its distance are reached; the retest -- a limit at the broken edge working
{LATENCY} minutes after the breakout (the operator's alert), filled when a bar trades through it by a tick, at the
level or at a gapped bar's open plus a tick -- with its fill bar, 15:08 close, 15:07-15:10 worst and spread, its range
stop's passages, and for each stop width of {', '.join(f'{s:g}' for s in q['stops'])} x the 14-day ATR the first bars
the stop and {', '.join(f'{r:g}' for r in RETEST_RR)} x the stop are reached; on every day, an unconditional long and
short at the first bar after each of {times} CT, with each bracket's outcome (the per-side drift benchmark, D-277);
and the overnight move, the gap and each range's distance from the Globex session's VWAP. No hypothesis, nothing selected. **Only these day records leave** (D-120), never bars.

**Logs**: `{k6.ORB6_PREFIX}|HEAD` (version 1; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect the
same days, entries, early closes and days without the histories as {k6.ORB6_RUNS[run_id]} (the ingest checks it), and
about two to three orders per record (each year's records are one stream cut into tags of at most {TAG_CHARS}
characters, so a record spans tags; the orders' own fills mean nothing).

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=run_id,
        title=f"ORB6 capture: NQ, {start.year}-{end.year}, the range stop, the retest entry, overnight, gap and VWAP",
        purpose=(f"T16 item 9, D-278: ORB6's data capture on NQ, {start} to {end} (development data under D-237), "
                 f"re-walking {k6.ORB6_RUNS[run_id]}'s days; one record per day exported, never bars."),
        class_name=f"Orb6NQ{start.year % 100:02d}{end.year % 100:02d}",
        start=warm, end=end,
        body=k6.BODY, preamble=k6.preamble(run_id),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="orb6",
        expected=expected,
        extra={"market": k6.MARKET, "model": "ORB6", "record_version": 1, "stops": list(q["stops"]),
               "range_rr": list(RANGE_RR), "retest_rr": list(RETEST_RR), "latency_min": LATENCY,
               "joins": k6.ORB6_RUNS[run_id], "captures": k6.ORB6_CAPTURES[run_id], "atr_days": q["atr_days"],
               "rv_days": q["rv_days"], "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "one record per day (D-120)", "ingest": "scripts/ingest_orb6_run.py",
               "source": "config/orb3_search.yaml; D-266; D-267; D-276; D-277; D-278"},
    )


ORB_SPECS.update({rid: (lambda rid=rid: _orb6_spec(rid)) for rid in __import__(
    "propedge.data.orb6_kit", fromlist=["ORB6_RUNS"]).ORB6_RUNS})


def _fv2_spec(run_id: str) -> RunSpec:
    """T16 item 11, D-279, D-282, D-283: one of FV2's six data-capture runs, re-walking half an ORB3 run's days."""
    from propedge.data import fv2_kit as kf
    from propedge.data.regime_kit import REGIME_TAG_CHARS as TAG_CHARS
    from propedge.outcomes import fv2_core as fc

    warm, start, end = kf.dates(run_id)
    q = kf.params()
    orb3 = kf.FV2_RUNS[run_id][0]
    times = "; ".join(f"{n} from {(s + 1020) // 60 % 24:02d}:{s % 60:02d} CT for {w} minutes" for n, s, w, _ in fc.SESSIONS)
    expected = f"""\
**FV2's data capture (T16 item 11, D-279, D-282, D-283), NQ, {start} to {end}** (from {warm} as warm-up, which only
fills the 14-day histories). It re-walks those days of {orb3} and records, for JJ Simon's fair-value strategy from his
own rules, each session ({times}): its fair value, every break of structure and displacement candle his rules allow (up
to {fc.MAX_SIGNALS} a session, the count beyond kept), each entered at the market {', '.join(map(str, fc.LATS))} minutes
after the signal with the first bars its stop ({fc.STOP_ATR:.4f} x the 14-day ATR, doubled on a large opening candle) and
1R, 1.5R and fair value are reached; and at fixed times an unconditional long and short with each bracket's outcome (the
per-side drift benchmark, D-277). No hypothesis, nothing selected. **Only these day records leave** (D-120), never bars.

**Logs**: `{kf.FV2_PREFIX}|HEAD` (version 1; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect the
same days as {orb3} over these dates (the ingest checks it) and about four to six orders per record (each year's
records are one stream cut into tags of at most {TAG_CHARS} characters; the orders' own fills mean nothing), well under
QuantConnect's 10,000 orders.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=run_id,
        title=f"FV2 capture: NQ, {start.year}-{end.year}, JJ Simon's fair value -- sessions, triggers, entries, benchmark",
        purpose=(f"T16 item 11, D-283: FV2's data capture on NQ, {start} to {end} (development data under D-237), "
                 f"re-walking {orb3}'s days; one record per day exported, never bars."),
        class_name=f"Fv2NQ{start.year % 100:02d}{end.year % 100:02d}",
        start=warm, end=end,
        body=kf.BODY, preamble=kf.preamble(run_id),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="fv2",
        expected=expected,
        extra={"market": kf.MARKET, "model": "FV2", "record_version": 1, "joins": orb3,
               "window": [str(start), str(end)], "stop_atr": fc.STOP_ATR, "latencies": list(fc.LATS),
               "max_signals": fc.MAX_SIGNALS, "sessions": [list(s[:3]) for s in fc.SESSIONS],
               "atr_days": q["atr_days"], "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "one record per day (D-120)", "ingest": "scripts/ingest_fv2_run.py",
               "source": "docs/candidates/fv2/JJ_SIMON_PRACTICE.md; D-266; D-267; D-277; D-279; D-282; D-283"},
    )


ORB_SPECS.update({rid: (lambda rid=rid: _fv2_spec(rid)) for rid in __import__(
    "propedge.data.fv2_kit", fromlist=["FV2_RUNS"]).FV2_RUNS})



def _fv3_spec(run_id: str) -> RunSpec:
    """T17 item 3: one of FV3's twenty data-capture runs, re-walking a piece of an ORB3 run's days."""
    from propedge.data import fv3_kit as kf
    from propedge.data.regime_kit import REGIME_TAG_CHARS as TAG_CHARS
    from propedge.outcomes import fv3_core as fc

    warm, start, end = kf.dates(run_id)
    q = kf.params()
    orb3 = kf.FV3_RUNS[run_id][0]
    times = "; ".join(f"{n} from {(s + 1020) // 60 % 24:02d}:{s % 60:02d} CT for {w} minutes" for n, s, w, _ in fc.SESSIONS)
    expected = f"""\
**FV3's data capture (T17 item 3; the card docs/candidates/cards/drafts/FV3.md), NQ, {start} to {end}** (from {warm}
as warm-up, which only fills the 14-day histories). It re-walks those days of {orb3} and records, for JJ Simon's
fair-value strategy from his own transcripts, each session ({times}): its fair price and its re-anchoring (the 6 PM
gap, Asia to 6 PM, the consolidation, the 8:30 ET release days), every break of structure and displacement candle his
rules allow (up to {fc.MAX_SIGNALS} a session, the count beyond kept) with its attributes -- the component ledger -- each
entered at the market {', '.join(map(str, fc.LATS))} minutes after the signal; the first latency's entry carries the
favourable and adverse profiles from which any stop and target of the ladder settles exactly, its 15:08 close and worst,
and the breakeven fields; and at fixed times an unconditional long and short with their profiles (the per-side drift
benchmark, D-277). No hypothesis, nothing selected. **Only these day records leave** (D-120), never bars.

**Logs**: `{kf.FV3_PREFIX}|HEAD` (version 1; days, warm-up days, records as `entries`, emits -- one per year -- orders,
switches, lost contracts, early closes, days without the histories, bad bars, bars and quotes) and `END`. Expect the
same days as {orb3} over these dates (the ingest checks it) and about ten to twenty orders per record (each year's
records are one stream cut into tags of at most {TAG_CHARS} characters; the orders' own fills mean nothing), under
QuantConnect's 10,000 orders -- the windows are cut to keep them there.

**The run is unusable** if `END` is missing, the backtest stopped with an error or a time limit, or `HEAD` reports far
fewer days than that; the parser also refuses an output whose records do not add up.
"""
    return RunSpec(
        run_id=run_id,
        title=f"FV3 capture: NQ, {start.year}-{end.year}, JJ Simon's fair value from his own rules -- the component ledger",
        purpose=(f"T17 item 3: FV3's data capture on NQ, {start} to {end} (development data under D-237), "
                 f"re-walking {orb3}'s days; one record per day exported, never bars."),
        class_name=f"Fv3NQ{start.year % 100:02d}{end.year % 100:02d}",
        start=warm, end=end,
        body=kf.BODY, preamble=kf.preamble(run_id),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="fv3",
        expected=expected,
        extra={"market": kf.MARKET, "model": "FV3", "record_version": 1, "joins": orb3,
               "window": [str(start), str(end)], "stop_atr": fc.STOP_ATR, "latencies": list(fc.LATS),
               "max_signals": fc.MAX_SIGNALS, "sessions": [list(s[:3]) for s in fc.SESSIONS],
               "news_days": sum(bin(v).count("1") for v in fc.NEWS.values()),
               "atr_days": q["atr_days"], "micro": q["micro"], "micro_tick": q["micro_tick"], "scale": "actual",
               "exports": "one record per day (D-120)", "ingest": "scripts/ingest_fv3_run.py",
               "source": "docs/candidates/cards/drafts/FV3.md; the operator's transcripts (2026-10-05); D-282; D-289; D-290; D-291"},
    )


ORB_SPECS.update({rid: (lambda rid=rid: _fv3_spec(rid)) for rid in __import__(
    "propedge.data.fv3_kit", fromlist=["FV3_RUNS"]).FV3_RUNS})


def _fv3_confirm_spec(run_id: str) -> RunSpec:
    """D-355: one of FV3-C's three confirmation kits on NQ's held-back window, under its registered pre-registration
    only -- the development kits' body and cores (R117-R136), the period's own window, 2026's release days added."""
    from propedge.data import fv3_kit as kf
    from propedge.outcomes import fv3_core as fc

    c = kf.confirm_config()
    pid = str(c.get("prereg_id") or "pending")
    if pid.lower() == "pending":
        raise ValueError(f"{kf.CONFIRM_CONFIG_PATH} has no registered prereg_id; the kit is not generated (D-81, D-355)")
    p = kf.confirm_runs(c)[run_id]
    warm, start, end = kf.confirm_dates(run_id, c)
    q = kf.params()
    expected = f"""\
**FV3-C's confirmation (D-355), under {pid}: period {p['id']}, NQ, {start} to {end}** (from {warm} as warm-up, which only
fills the 14-day histories and records nothing). Fixed in `{kf.CONFIRM_CONFIG_PATH}` before any of this window was read.
FV3's capture -- the body and the embedded cores of the development kits R117-R136 unchanged -- over the period's own
dates, with 2026's BLS 08:30 ET release days added to the cores' table after them. **Only the day records leave**
(D-120), never bars.

This run reads data that can be looked at **once**. Do not open the equity chart or the statistics. Download the files
and hand them over; nothing is computed from this run until every period is in. **Run all three confirmation kits
(R139, R140, R141), in any order, before anything is ingested:** each run is first judged from its own files without
saving a record, and no period's records are saved until every period has a usable run (D-356) -- so a fix kit, if
one is needed, also runs before any of the window is read.

**Logs**: `{kf.FV3_PREFIX}|HEAD` (version 1) and `END`, as the development kits'. Expect one record per full trading
day of the period -- about 120 for a half-year, about 60 for a quarter (a period cut short by the end of QuantConnect's
data has fewer, and is then simply not counted).

**The run is unusable** (D-230's single test, judged from the log before any record is parsed) if `END` is missing, the
log or you report an error or a time limit, or `HEAD` reports fewer than {int(p['min_days'])} days; or if the parser
refuses its output. It is recorded in `unusable.json` and its records are never read; one fixed kit for the period may
follow, recorded in a decision first; a period unusable twice fails the confirmation. A refusal of the procedure (a
missing or wrong download, the ran code) is retried on this backtest's own files and is not a new run.
"""
    return RunSpec(
        run_id=run_id,
        title=f"FV3-C confirmation, period {p['id']}: NQ, {start} to {end}, JJ Simon's fair value under the firm's two rules",
        purpose=(f"D-355, {pid}: FV3-C's one confirmation on NQ's held-back window -- period {p['id']}, {start} to {end}; "
                 "one record per day exported, never bars."),
        class_name=f"Fv3ConfirmNQ{str(p['id'])}",
        start=warm, end=end,
        body=kf.BODY, preamble=kf.confirm_preamble(run_id, c),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="fv3",
        expected=expected,
        extra={"market": kf.MARKET, "model": str(c["model"]), "record_version": 1, "joins": None, "confirm": True,
               "prereg": pid, "period": str(p["id"]), "period_label": int(p["label"]), "min_days": int(p["min_days"]),
               "window": [str(start), str(end)], "stop_atr": fc.STOP_ATR, "latencies": list(fc.LATS),
               "max_signals": fc.MAX_SIGNALS, "sessions": [list(s[:3]) for s in fc.SESSIONS],
               "news_2026": str(c["news_2026"]), "atr_days": q["atr_days"], "micro": q["micro"],
               "micro_tick": q["micro_tick"], "scale": "actual", "exports": "one record per day (D-120)",
               "ingest": "scripts/ingest_fv3_run.py", "source": f"{kf.CONFIRM_CONFIG_PATH}; D-355; {pid}"},
        prereg_id=pid,
    )


def _fv3_confirm_specs() -> dict[str, Callable[[], RunSpec]]:
    """As NQB1's and NQB2's: the confirmation kits are generated only under a runnable registration. Once the outcome is
    recorded the committed kits stay exactly as they ran and are kept out of SPECS."""
    from propedge.data import fv3_kit as kf
    from propedge.data.cloud_guard import confirmation_run_authorised

    c = kf.confirm_config()
    pid = str(c.get("prereg_id") or "pending")
    if not confirmation_run_authorised(pid):
        return {}
    return {rid: (lambda rid=rid: _fv3_confirm_spec(rid)) for rid in kf.confirm_runs(c)}


FV3_CONFIRM_SPECS: dict[str, Callable[[], RunSpec]] = _fv3_confirm_specs()


SETUP_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda mk=mk: _setup_spec(mk)) for mk, rid in __import__(
        "propedge.data.setup_kit", fromlist=["SETUP_RUNS"]).SETUP_RUNS.items()}


SPECS: dict[str, Callable[[], RunSpec]] = {
    **ORB_SPECS,
    **FV3_CONFIRM_SPECS,
    **T24C_SPECS,                       # D-439: only under a runnable registration
    **SETUP_SPECS,
    **REGIME_CONFIRM_SPECS,
    **REGIME_SPECS,
    **CONFIRM_SPECS,
    **FLIP_SPECS,
    **RMAP_SPECS,
    **RELEASE_SPECS,
    **IM2X_SPECS,
    **IM2_SPECS,
    **BMAP_SPECS,
    **FV_SPECS,
    GRID_RUN: _grid_spec,
    CONTEXT_V2_RUN: _context_v2_spec,
    GDIAG_RUN: _gdiag_spec,
    CONTEXT_RUN: _context_spec,
    EXTRAS_RUN: _extras_spec,
    OPTIONS_RUN: _options_spec,
    **ATLAS_SPECS,
    OPENREV_NQ_RUN: _openrev_nq_spec,
    OPENREV_RUN: _openrev_spec,
    GAP_RUN: _gap_spec,
    GAP_RUN_V2: lambda: _gap_spec(2),
    "R001-dataset-checks": _dataset_spec,
    "R002-recon-A": lambda: _recon_spec("A"),
    "R003-recon-B": lambda: _recon_spec("B"),
    "R004-recon-C": lambda: _recon_spec("C"),
    "R005-gc-coverage": _coverage_spec,
    "R006-recon-A2": lambda: _recon_v2_spec("A"),
    "R007-recon-B2": lambda: _recon_v2_spec("B"),
    "R008-recon-C2": lambda: _recon_v2_spec("C"),
    "R009-leg-GC": lambda: _leg_spec("GC"),
    "R013-leg-GC2": lambda: _leg_spec("GC", 2),
    "R014-leg-CL2": lambda: _leg_spec("CL", 2),
    "R015-leg-6E2": lambda: _leg_spec("6E", 2),
    "R016-leg-ES2": lambda: _leg_spec("ES", 2),
    "R017-leg-GC3": lambda: _leg_spec("GC", 2, filter_days=alg.LEG_V2_FILTER_DAYS_GC,
                                      run_id="R017-leg-GC3"),
}


#: C-007 confirmation evidence (T5): the SAME leg algorithm as R013-R017, over the confirmation
#: window, in two parts per leg (config/c007.yaml). Kept out of SPECS: each needs the registered
#: pre-registration id, and until it exists generating one raises.
CONF_RUNS = {(m, p): f"R{18 + 2 * i + p - 1:03d}-conf-{m}{p}"
             for i, m in enumerate(("GC", "CL", "6E", "ES")) for p in (1, 2)}


def _conf_spec(market: str, part: int) -> RunSpec:
    import yaml

    cfg = yaml.safe_load((REPO_ROOT / "config" / "c007.yaml").read_text(encoding="utf-8"))
    conf = cfg["confirmation"]
    spec = next(x for x in conf["parts"] if x["part"] == part)
    start, end = (date.fromisoformat(d) for d in spec["run"])
    own = spec["own"]
    entry, exit_ = alg.LEG_WINDOWS[market]
    filter_days = alg.LEG_V2_FILTER_DAYS_GC if market == "GC" else alg.LEG_V2_FILTER_DAYS
    expected = f"""\
**Confirmation evidence** for Stage 2B's C-007, **{market} leg, part {part}**, under pre-registration
`{conf["prereg_id"]}`. The algorithm is the development kits' (R013-R017) unchanged; only the dates
and the embedded pre-registration id differ. It runs {start} to {end}; the repository uses only the
days {own[0]} to {own[1]}, and the few days before are warm-up (a previous settlement for the first
owned day).

This run reads data that can be looked at **once**. Do not open the equity chart or the
statistics. Download the files and ingest them; nothing is computed from this run until every
part of every leg is in.

**Logs** and **Download Results** as for R013-R017: `HEAD`, `LAST`, `END` lines, and each day's
record in the order tags.

**The run is unusable** if `END` is missing, if the backtest stopped with an error, or if `HEAD`
reports far fewer days than the span has trading days. Report it; do not rerun it on your own.
A rerun is a decision recorded in DECISIONS.md.
"""
    return RunSpec(
        run_id=CONF_RUNS[(market, part)],
        title=f"C-007 confirmation evidence: {market} part {part}",
        purpose=f"Stage 2B C-007, {market} leg, window {entry}-{exit_} CT, CONFIRMATION window "
                f"{own[0]} to {own[1]} under {conf['prereg_id']} (T5).",
        class_name=f"LegConfirm{market}P{part}",
        start=start, end=end,
        body=alg.LEG_BODY_V2,
        preamble=alg.leg_preamble_v2(market, filter_days),
        downloads=(LOGS, RESULTS, RAN_CODE),
        parser="leg_evidence",
        expected=expected,
        extra={"market": market, "window_ct": [entry, exit_], "version": 2,
               "filter_days": filter_days, "part": part, "own": own,
               "source": "Stage 2B C-007; D-50; D-97; D-98; confirmation (T5)"},
        prereg_id=conf["prereg_id"],
    )


CONF_SPECS: dict[str, Callable[[], RunSpec]] = {
    rid: (lambda m=m, p=p: _conf_spec(m, p)) for (m, p), rid in CONF_RUNS.items()}


def get_spec(run_id: str) -> RunSpec:
    if run_id in CONF_SPECS:
        return CONF_SPECS[run_id]()
    try:
        return SPECS[run_id]()
    except KeyError:
        raise KeyError(f"no run {run_id!r}; known: {', '.join(SPECS)}") from None


# ------------------------------------------------------------------ the kit files

def _run_md(spec: RunSpec, code_hash: str) -> str:
    rel = f"runs/{spec.run_id}"
    dl_rows = "\n".join(f"| `{rel}/{DOWNLOADS}/{d.name}` | {d.how} |" for d in spec.downloads)
    files = " ".join(f"{rel}/{DOWNLOADS}/{d.name}" for d in spec.downloads if d is not RAN_CODE)
    return f"""\
# {spec.run_id} — {spec.title}

{spec.purpose}

Free tier is enough: minute resolution, one compact summary at the end (well inside the 10 KB log
limit). **Do not edit the code.** Any edit changes its hash and the result will be refused at
ingestion. If something fails, stop and report it; a fix comes back as a new kit.

Start a timer now. The effort log records your minutes (D-82).

## Steps

1. Go to quantconnect.com and open the **Algorithm Lab**. Create a **new project** and choose
   **Python**.
2. Rename the project to **`{spec.project_name}`**.
3. Open `main.py` in the project. Select all of it and delete it.
4. Open `{rel}/main.py` in this repository, copy **the whole file**, and paste it into the
   editor's `main.py`. Save. Do not add, remove or reformat anything.
5. **Settings to change: none.** The dates, resolution and models are all in the code. Do not set
   a start or end date anywhere in the interface.
6. Press **Backtest**. Wait for it to finish; the progress bar reaches 100 %.
   - If it stops with an error: copy the error text, note that it happened, and stop here. Each
     time this happens and a new kit is run, that is one **fix-and-rerun round**.
   - If any message mentions a **limit** (logs, time, quota), note its exact text.
7. Note two ids:
   - **project id**: the number in the project's address (`…/project/<project id>`);
   - **backtest id**: the id of this backtest, from its results page address or details.
8. Download these files and save them **exactly** here (create the `{DOWNLOADS}` folder):

| save as | how |
|---|---|
{dl_rows}

9. Stop the timer. Run, from the repository root, filling in the angle brackets:

```
python {spec.extra.get("ingest", "scripts/ingest_manual_run.py")} {spec.run_id} --project-id <project id> --backtest-id <backtest id> --run-by "<your name>" --minutes <minutes> --rounds <fix-and-rerun rounds, 0 if none> --limit-hit "<limit message, or none>" --files {files}
```

The command checks that `{DOWNLOADS}/{RAN_CODE.name}` is exactly the committed `main.py`
(normalised sha256 `{code_hash}`), then saves the result with provenance *human-run in
QuantConnect web editor*.

What the outputs should look like: [`EXPECTED.md`](EXPECTED.md).
"""


def write_kit(run_id: str, *, runs_dir: Path = RUNS_DIR) -> Path:
    """Generate (or regenerate) the kit folder for `run_id`. Returns the folder."""
    spec = get_spec(run_id)
    code = spec.code()
    code_hash = normalised_hash(code)
    folder = runs_dir / spec.run_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "main.py").write_text(code, encoding="utf-8", newline="\n")
    (folder / "RUN.md").write_text(_run_md(spec, code_hash), encoding="utf-8", newline="\n")
    (folder / "EXPECTED.md").write_text(
        f"# {spec.run_id} — expected outputs\n\n{spec.expected}", encoding="utf-8", newline="\n")
    kit = {
        "run_id": spec.run_id,
        "title": spec.title,
        "project_name": spec.project_name,
        "class_name": spec.class_name,
        "backtest_start": spec.start.isoformat(),
        "backtest_end": spec.end.isoformat(),
        "algorithm_file": f"runs/{spec.run_id}/main.py",
        "algorithm_sha256_normalised": code_hash,
        "downloads": [d.name for d in spec.downloads],
        "ran_code": RAN_CODE.name,
        "parser": spec.parser,
        "log_budget_bytes": alg.LOG_BUDGET_BYTES,
        **spec.extra,
    }
    (folder / "kit.json").write_text(json.dumps(kit, indent=2) + "\n", encoding="utf-8",
                                     newline="\n")
    return folder
