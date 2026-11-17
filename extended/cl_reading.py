"""RD-03's reading (`prereg/RD-03_contract_levers.md`, pinned under E-152; its build Q-119, E-153): A-6 -- the cells of
section 7 in section 15's order, 9.1's checks, 9.2's oracles, 9.3's mechanics, 10.1's readings by RD-02's functions,
the menu with its flags, the guard row beside every P, the "gaming P" labels and the Focused Trader gap named.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import cl_reading as CL
    out3 = CL.run_scorecard(CL.CLInputs(), workers=1)                    # step 3: the scorecard and the gates
    out4 = CL.run_beside(CL.CLInputs(), "ladder", workers=1)             # step 4: the ladder and the placement
    out5 = CL.run_beside(CL.CLInputs(), "ftp", workers=1)                # step 5: the ten Focused Trader models

Every function that reads the bars runs only inside the engine, through RD-02's real inputs (`extended/pp_inputs.py`,
the builders `identity/pp_identity.py` certifies at its reference) and Q-17's adapter with A-2's keyword; the runner
script (`scripts/cl_reading.py`) authorises each judged-block purpose just before its stage and refuses outside a clean
checkout. The toys of the tests run every function here on synthetic campaigns (`tests/cl_synthetic.py`).

**What nothing here does.** No cell carries, passes or fails; no level; no pick (E-023 (1)). Stage 0's view is printed
beside the Back2Funded and `naf` rows and moves no row (6.3): the menu takes it as an input to print and never reads it
for an order or a flag (T-12's "no code path"). House money's P is printed only in its guard row, labelled "gaming P
(E-134 (2))", and never ordered (T-14). The menu's writer refuses a P without its guard row.

**Refusing.** Any failed check of 9.1 or 9.2 raises `Refused` (RD-02's): nothing of a new cell is computed further,
written or printed.
"""
from __future__ import annotations

import dataclasses
import hashlib
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

from extended import levers_path as LP  # noqa: E402
from extended import levers_readings as LR  # noqa: E402
from extended import levers_terms as LT  # noqa: E402
from extended import pp_inputs as PI  # noqa: E402
from extended import pp_reading as RD  # noqa: E402
from extended import pp_run as PR  # noqa: E402
from extended import user_measures as M  # noqa: E402

DECLARATION = "prereg/RD-03_contract_levers.md"
#: before the pin's commit reaches this tree, the draft's name (the same text: T-0 holds the two names to one file)
DRAFT_DECLARATION = "prereg/DRAFT_RD-03_contract_levers.md"
PREREG_ID = "RD-03"
PIN_ROW = "E-152"
#: section 5 item 6's line: the four judged-block purposes, each authorised just before its stage (section 15)
PURPOSES = ("levers_scorecard", "levers_gate_beside", "levers_ladder_beside", "levers_ftp_beside")
STAGE_PURPOSE = {"scorecard": "levers_scorecard", "gate": "levers_gate_beside", "ladder": "levers_ladder_beside",
                 "ftp": "levers_ftp_beside"}
DESIGNS = ("p14", "p16")
ARMS = ("verdict", "point")
B2F_CELLS = ("b2f1", "b2f2")
INV_CELLS = tuple(f"inv{c}_{b}_{e}" for c in ("5", "7") for b in ("bank", "hold") for e in ("none", "30"))
HOUSE_CELLS = tuple(f"house_{r}_{e}" for r in ("stop", "zero") for e in ("none", "30"))
NAF_CELLS = ("naf",)
#: section 7.2's grid, in its order
NEW_CELLS = (*B2F_CELLS, *INV_CELLS, *HOUSE_CELLS, *NAF_CELLS)
#: section 15 step 3 (b)'s order: house money (stop before zero, exp_none before exp_30), the inventory (C = 5 before 7,
#: banking on before off, exp_none before exp_30), Back2Funded (b2f1 before b2f2), naf
STEP3_ORDER = (*HOUSE_CELLS, *INV_CELLS, *B2F_CELLS, *NAF_CELLS)
#: L-I's C relative to the base's own evaluation bound (2.2): D-34's bound kept, and two above it
INV_ABOVE = {"5": 0, "7": 2}
#: the readings beside (10.1 item 8)
LADDER = ("denial_10", "denial_25", "denial_50", "rtp")
FTP_CELLS = (*INV_CELLS, *B2F_CELLS)
#: the variants of a run: the headline, and the Back2Funded cells' counted reading under the models (U-6)
OPTIMISTIC, CONSERVATIVE = "", "counted"
RECORD_COLUMNS = PR.RECORD_COLUMNS
BLOCKS = PR.BLOCKS
CALENDARS = PR.CALENDARS
Refused = PI.Refused
NAN = float("nan")
#: the frontier's measures (10.1 item 1)
FRONTIER = ("P", "S1", "S3a", "S5a")
#: 9.3's horizons for the share of starts differing, and the trigger's
DIFFER_SESSIONS = (63, 126, 252)
TRIGGER_SESSIONS = (21, 63, 126, 252)
#: the files this reading's adapters are (their blob ids go into every manifest)
ADAPTER_FILES = ("extended/levers_path.py", "extended/levers_terms.py", "extended/levers_readings.py",
                 "extended/cl_reading.py", "extended/levers_fit.py", "extended/user_beside.py", "extended/gate.py",
                 "extended/campaign.py", "scripts/cl_reading.py", "scripts/cl_fit.py")
_row = PR._row
_f = PR._f


def lever_of(cell: str) -> str:
    return {"b": "L-B", "i": "L-I", "h": "L-H", "n": "L-N", "r": "--"}[cell[0]]


# ------------------------------------------------------------------------------------------------ the cells


@dataclasses.dataclass(frozen=True)
class CellSpec:
    """One cell's settings (7.2)."""

    cell: str
    lever: str
    reactivations: str = ""        # "1" or "max"
    c: str = ""                    # "5" or "7"
    banking: bool | None = None
    expiry: str = "none"
    house: str = "off"
    naf: bool = False


def spec(cell: str) -> CellSpec:
    if cell == "ref":
        return CellSpec("ref", "--")
    if cell in B2F_CELLS:
        return CellSpec(cell, "L-B", reactivations="1" if cell == "b2f1" else "max")
    if cell in INV_CELLS:
        _, b, e = cell.split("_")
        return CellSpec(cell, "L-I", c=cell[3], banking=(b == "bank"), expiry=e)
    if cell in HOUSE_CELLS:
        _, r, e = cell.split("_")
        return CellSpec(cell, "L-H", house=r, expiry=e)
    if cell == "naf":
        return CellSpec(cell, "L-N", naf=True)
    raise KeyError(f"no cell {cell!r} in section 7.2")


def cell_levers(cell: str, base_combines: int, *, counters: bool = True, count_reactivations: bool = False,
                root: Path | str = ROOT) -> LP.Levers:
    """The cell's `Levers`, every value loaded from its record (`extended/levers_terms.py`) or the readings table
    (`extended/levers_readings.py`); `base_combines` is the base's own evaluation bound, read from its replay's (or its
    gate's) arguments."""
    s = spec(cell)
    kw: dict[str, Any] = {"counters": bool(counters)}
    if s.lever == "L-B":
        days = LT.reactivation_window_days(root)
        kw.update(reactivations=1 if s.reactivations == "1" else LT.max_reactivations(root),
                  reactivation_fee=LT.reactivation_fee(root), reactivation_window_days=days,
                  reactivation_window_sessions=LT.sessions_for_days(days), count_reactivations=bool(count_reactivations))
    elif count_reactivations:
        raise Refused(f"{cell}: the counted reading is Back2Funded's only (U-6)")
    if s.expiry != "none":
        days = int(LR.reading("expiry_30_calendar_days"))
        kw.update(expiry=s.expiry, expiry_days=days, expiry_sessions=LT.sessions_for_days(days))
    if s.lever == "L-I":
        kw.update(max_concurrent_combines=int(base_combines) + INV_ABOVE[s.c], lift_joint_cap=True,
                  stop_buying_when_queued=not bool(s.banking))
    if s.lever == "L-H":
        kw.update(house=s.house)
    if s.naf:
        sub, act = LT.naf_prices(root)
        kw.update(subscription=sub, activation=act)
    return LP.Levers(**kw)


def seat_limit_problems(path_args: Mapping[str, Any], gate_kw: Mapping[str, Any] | None = None) -> list[str]:
    """T-4: each base's three seat limits -- `max_concurrent_accounts`, `max_concurrent_combines`, `max_total_accounts`
    on the replay; `accounts`, `combines`, `total_accounts` on the gate -- are each the funded cap
    (`max_active_funded_accounts`), `reset_failed_combines` is off and the activation is paid on activation; else the
    build stops and reports."""
    cap = LT.funded_cap()
    out = []
    for k in ("max_concurrent_accounts", "max_concurrent_combines", "max_total_accounts"):
        if path_args.get(k) != cap:
            out.append(f"the replay's {k} is {path_args.get(k)!r}, not the funded cap {cap}")
    if path_args.get("reset_failed_combines"):
        out.append("the replay resets failed evaluations")
    if path_args.get("activation_timing") not in (None, "on_activation"):
        from propedge.campaign.lockstep import ACTIVATION_ON_ACTIVATION

        if path_args.get("activation_timing") != ACTIVATION_ON_ACTIVATION:
            out.append(f"the replay's activation timing is {path_args.get('activation_timing')!r}")
    if gate_kw is not None:
        for k in ("accounts", "combines", "total_accounts"):
            if gate_kw.get(k) != cap:
                out.append(f"the gate's {k} is {gate_kw.get(k)!r}, not the funded cap {cap}")
        if gate_kw.get("reset_failed_combines"):
            out.append("the gate resets failed evaluations")
    return out


# ------------------------------------------------------------------------------------------------ the inputs


class CLInputs(PI.RealInputs):
    """RD-02's real inputs at its reference (`extended/pp_inputs.py`, certified by `identity/pp_identity.py`): U1's jobs,
    U1's file, Q-44's per-start file read as text, the registered gate calls and rows. RD-03 adds the Focused Trader
    rows to the preflight (the red team's m6: checked before any purpose is spent)."""

    def preflight(self, designs: Sequence[str]) -> list[str]:
        from extended import user_beside as B

        out = list(super().preflight(designs))
        try:
            f = self.q44()
        except Exception as exc:                          # noqa: BLE001 -- a refusal before any read
            return out + [f"Q-44's per-start file: {exc}"]
        for d in designs:
            for r in B.RESPONSES:
                if r.kind == "ftp" and not ((f["design"] == d) & (f["arm"] == "verdict") & (f["response"] == r.name)).any():
                    out.append(f"Q-44's per-start file has no {d} verdict {r.name} rows (step 5's 9.1 item 6)")
        return out


def cell_gate(inputs: Any, design: str, cell: str, twin: bool, *, count_reactivations: bool = False,
              counters: bool = True) -> dict[str, Any]:
    """The base's registered gate call (`inputs.gate_call(design, "ref", twin)`) with a cell's keywords: its `Levers`
    (A-3), and for the inventory its seat keywords (`combines` C, `total_accounts` None, `stop_buying_when_queued`
    from its banking), for `naf` its prices (A-4). Refused when the call lacks its seat limits (the red team's m2)."""
    g = inputs.gate_call(design, "ref", twin)
    kw = dict(g["kw"])
    probs = seat_limit_problems({"max_concurrent_accounts": LT.funded_cap(), "max_concurrent_combines": LT.funded_cap(),
                                 "max_total_accounts": LT.funded_cap()}, kw)
    if probs:
        raise Refused(f"T-4: {design}'s gate: the build stops and reports -- " + "; ".join(probs))
    lev = cell_levers(cell, int(kw["combines"]), counters=counters, count_reactivations=count_reactivations)
    if lev.max_concurrent_combines is not None:
        kw["combines"] = int(lev.max_concurrent_combines)
    if lev.lift_joint_cap:
        kw["total_accounts"] = None
    if lev.stop_buying_when_queued is not None:
        kw["stop_buying_when_queued"] = bool(lev.stop_buying_when_queued)
    if lev.subscription is not None:
        kw["subscription"] = float(lev.subscription)
    if lev.activation is not None:
        kw["activation"] = float(lev.activation)
    kw["levers"] = lev
    return {**g, "kw": kw, "cell": cell, "levers": lev}


# ------------------------------------------------------------------------------------------------ the runs


def run_key(d: str, arm: str, cell: str, rname: str = "off", variant: str = OPTIMISTIC) -> tuple[str, ...]:
    return (str(d), str(arm), str(cell), str(rname), str(variant))


def replay_run(job: dict[str, Any], d: str, arm: str, cell: str, rname: str, starts: Sequence[int], workers: int,
               *, record: bool, count_reactivations: bool = False) -> dict[str, Any]:
    """One cell's replays through Q-17's adapter with A-2's keyword, the counters on (and the recorder when asked)."""
    from extended import replay_records as RRec
    from extended import user_beside as B

    lev = cell_levers(cell, int(job["args"]["path"]["max_concurrent_combines"]), counters=True,
                      count_reactivations=count_reactivations)
    rec = RRec.ReplayRecorder(columns=RECORD_COLUMNS) if record else None
    sink = LP.LeverSink()
    outs = B.run_starts(d, arm, B.BY_NAME[rname], job, list(starts), int(workers), recorder=rec, levers=lev,
                        lever_sink=sink)
    counts = sink.starts(d, arm, rname)
    return {"outs": outs, "rec": rec, "counts": counts, "job": job, "levers": lev}


def lever_totals(counts: Mapping[int, Mapping[str, Any]], keys: Sequence[str] = LP.LEVER_KEYS) -> dict[str, float]:
    return {k: float(sum(float(c.get(k, 0) or 0) for c in counts.values())) for k in keys}


# ------------------------------------------------------------------------------------------------ 9.1's checks


def bind_day(cell: str, c: Mapping[str, Any], rec: Mapping[str, Any]) -> int | None:
    """9.1 item 7: the first engine day the cell's lever can bind on a start (None: no claim before binding): house
    money's trigger, Back2Funded's first eligible loss, a C = 5 inventory cell's first pass; a start where it never
    binds returns the replay's length (equal throughout)."""
    s = spec(cell)
    cc = c.get("cash_closes")
    n = len(cc) if cc is not None and len(cc) else 10 ** 9
    if s.lever == "L-H":
        t = int(c.get("house_trigger_day", -1))
        return n if t < 0 else t
    if s.lever == "L-B":
        losses = list(c.get("reactivation_loss_days") or ())
        return n if not losses else int(min(losses))
    if s.lever == "L-I" and s.c == "5":
        p = list(rec.get("pass_days") or ())
        return n if not p else int(min(p))
    return None


def before_binding_problems(cell: str, run: Mapping[str, Any], base: Mapping[str, Any]) -> list[str]:
    """9.1 item 7, refusing: on every start, before the cell's lever can bind, every act equals its base's, close for
    close -- the cash, the evaluations running, the live funded accounts, the queue's length and the fees by kind (the
    counters' channel carries each start's closes and acts; the red team's m4)."""
    out = []
    bo = {int(x["rec"]["start_day"]): x for x in base["outs"]}
    for x in run["outs"]:
        s = int(x["rec"]["start_day"])
        c, b = run["counts"].get(s), base["counts"].get(s)
        if c is None or b is None or s not in bo:
            out.append(f"{cell} start {s}: no counts or no base start")
            continue
        k = bind_day(cell, c, x["rec"])
        if k is None:
            continue
        for name in ("cash_closes", "acts", "fee_days"):
            a1, b1 = np.asarray(c[name]), np.asarray(b[name])
            kk = min(int(k), len(a1), len(b1))
            if not np.array_equal(a1[:kk], b1[:kk]):
                i = int(np.flatnonzero((a1[:kk] != b1[:kk]).reshape(kk, -1).any(axis=1))[0])
                out.append(f"{cell} start {s}: {name} at close {i} differs from its base's before the lever binds "
                           f"(day {k})")
                break
    return out


def expiry_pair_problems(cell_none: str, run_none: Mapping[str, Any], run_30: Mapping[str, Any], window: int
                         ) -> list[str]:
    """9.1 item 7's last clause: an inventory or house-money cell's two expiry readings are equal on every start where
    no pass waits more than the window (calendar days) under `exp_none` -- read at every close and at each activation,
    so a pass still waiting when the replay ends counts (`max_queue_wait`) -- act for act (m4)."""
    out = []
    for s, c in run_none["counts"].items():
        if int(c.get("max_queue_wait", 0)) > window:
            continue
        d = run_30["counts"].get(s)
        if d is None or any(not np.array_equal(np.asarray(c[k]), np.asarray(d[k]))
                            for k in ("cash_closes", "acts", "fee_days")):
            out.append(f"{cell_none}: start {s}: exp_30 differs though no pass waited past the window")
    return out


def identity_rows(d: str, arm: str, cell: str, item: str, probs: Sequence[str], n: int, rname: str = "off",
                  variant: str = "") -> list[dict[str, Any]]:
    return [_row(section="identity", design=d, arm=arm, cell=cell, mode=variant or "declared", response=rname,
                 measure=item, stat="holds", value=float(not probs), n=int(n), note="; ".join(list(probs)[:4]))]


# ------------------------------------------------------------------------------------------------ 9.2's oracles


def replay_oracle_problems(cell: str, run: Mapping[str, Any], base: Mapping[str, Any] | None) -> list[str]:
    """9.2 on a cell's replays, from the counters' channel and the start records, each at run time (the red team's m3):
    every reactivation of an eligible account, bought on its breach's evening (or later only after a refusal for cash),
    never under a placement; the purchase budget; house money's fee floor at every act."""
    s = spec(cell)
    lev = run["levers"]
    cap = LT.funded_cap()
    budget = (run.get("job") or {}).get("args", {}).get("path", {}).get("purchase_budget")
    out = []
    for st, c in run["counts"].items():
        tag = f"{cell} start {st}"
        if int(c.get("same_day_bought_and_breached", 0)):
            out.append(f"{tag}: an account bought or reactivated and breached the same trading day (D-549)")
        if c.get("fees_by_kind_problem"):
            out.append(f"{tag}: the fees by kind do not sum to the engine's total")
        if int(c.get("max_funded_live", 0)) > cap:
            out.append(f"{tag}: more than {cap} funded accounts active")
        if budget is not None and rolling_max(c.get("purchase_days") or (), int(budget[1])) > int(budget[0]):
            out.append(f"{tag}: the purchase budget exceeded")
        if s.lever == "L-B":
            ords = list(c.get("reactivation_ordinals") or ())
            if ords and max(ords) > int(lev.reactivations):
                out.append(f"{tag}: an XFA reactivated beyond its limit")
            if abs(float(c["reactivation_fees"]) - float(lev.reactivation_fee) * int(c["reactivations"])) > 1e-6:
                out.append(f"{tag}: a reactivation not at its price")
            for elig, wait, placed, cash_refused in (c.get("reactivation_checks") or ()):
                if not elig:
                    out.append(f"{tag}: a reactivation of an account not eligible (U-7)")
                if int(wait) != 0 and not cash_refused:
                    out.append(f"{tag}: a reactivation not bought on its breach's evening")
                if placed:
                    out.append(f"{tag}: a reactivation under a Focused Trader placement (U-5)")
            if any(int(w) < 1 for w in (c.get("reactivation_wait_sessions") or ())):
                out.append(f"{tag}: a reactivated account traded the session of its loss")
        if s.lever == "L-I" and int(c.get("max_running", 0)) > int(lev.max_concurrent_combines):
            out.append(f"{tag}: more than C evaluations running")
        if s.expiry != "none":
            waits = list(c.get("queue_waits") or ())
            if waits and max(waits) > int(lev.expiry_days):
                out.append(f"{tag}: a pass activated past the expiry")
        if s.lever == "L-H":
            if int(c.get("house_closes_not_ahead", 0)) or int(c.get("house_fees_not_ahead", 0)):
                out.append(f"{tag}: a fee or a close after the trigger not ahead")
            if s.house == "stop" and int(c.get("house_purchases_after_trigger", 0)):
                out.append(f"{tag}: house_stop bought an evaluation after the trigger")
        if s.naf:
            sub = float(lev.subscription)
            k = float(c["fees_subscription"]) / sub if sub else 0.0
            if abs(k - round(k)) > 1e-9 or abs(float(c["fees_activation"])) > 1e-9:
                out.append(f"{tag}: an evaluation fee not {sub} a cycle or an activation not {lev.activation}")
    if s.lever == "L-H" and base is not None:
        bo = {int(x["rec"]["start_day"]): x["rec"] for x in base["outs"]}
        for x in run["outs"]:
            r = x["rec"]
            b = bo.get(int(r["start_day"]))
            if b is None:
                continue
            for m, (u, v) in enumerate(zip(r["net_month"], b["net_month"])):
                if u is not None and v is not None and float(v) > 0 and not float(u) > 0:
                    out.append(f"{cell} start {r['start_day']}: month {m + 1} not ahead where its base is")
                    break
    return out


class CLGateTally:
    """9.2 on a gate (wraps the gate's `path_hook`): RD-02's request oracles and the twin's mean gross payouts per
    funded account (`pp_run.GateTally` at the reference payout rule, P-14's), the pass rate per evaluation, the purchase
    budget never exceeded, and the levers' counts summed over the paths of each shift (A-1 (d))."""

    def __init__(self, inner: Any):
        self.req = PR.GateTally(inner, "ref")
        self.passes = [0, 0]                          # passed, evaluations (the point shift)
        self.budget_over = 0
        self.counts: dict[tuple[str, float], Counter] = {}

    def __call__(self, shift: str, p: float, paths: Sequence[Any]) -> dict[str, Any]:
        cnt = self.counts.setdefault((str(shift), float(p)), Counter())
        for x in paths:
            for k, v in (getattr(x, "lever_counts", None) or {}).items():
                if k in LP.LEVER_KEYS or k in LP.ENGINE_KEYS:
                    cnt[k] += float(v or 0)
            cnt["paths"] += 1
            pb = getattr(x, "purchase_budget", None) or {}
            if pb and int(pb.get("max_purchases_in_window", 0)) > int(pb.get("k", 10 ** 9)):
                self.budget_over += 1
            if str(shift) == "point":
                self.passes[0] += sum(1 for c in x.combines if c.passed)
                self.passes[1] += len(x.combines)
        return self.req(shift, p, paths)


def gate_oracle_rows(key: dict[str, Any], twin: bool, tally: CLGateTally) -> list[dict[str, Any]]:
    """9.2 on one gate. "Beyond its Monte Carlo interval" is read as three standard errors -- a build choice (RD-02's
    reading of the same oracle), not a declared tolerance."""
    rows = PR.gate_oracle_rows(key, twin, tally.req)
    if tally.budget_over:
        raise Refused(f"9.2: {key}: the purchase budget exceeded on {tally.budget_over} paths")
    if twin:
        k, n = tally.passes
        if n:
            q = k / n
            se = math.sqrt(max(q * (1 - q), 0.0) / n)
            if q > 0.4 + 3.0 * se:
                raise Refused(f"9.2: {key} twin: the pass rate per evaluation {q:.4f} exceeds 2/5 + 3 se")
            rows.append(_row(section="oracle", part="gate", **key, measure="zero-edge twin pass rate per evaluation",
                             stat="value", value=q, n=n, note=f"bound 2/5 + 3 x {se:.4f} (propsim D-02); three "
                                                              "standard errors: a build choice, RD-02's reading"))
    return rows


# ------------------------------------------------------------------------------------------------ 9.3's mechanics


def _q(x: Sequence[float], q: float) -> float:
    a = np.asarray([v for v in x if v is not None and np.isfinite(float(v))], float)
    return float(np.quantile(a, q)) if a.size else NAN


def rolling_max(days: Sequence[int], window: int) -> int:
    d = sorted(int(x) for x in days)
    best = 0
    j = 0
    for i in range(len(d)):
        while d[i] - d[j] >= int(window):
            j += 1
        best = max(best, i - j + 1)
    return best


def _rk(k: Mapping[str, Any], **kw: Any) -> dict[str, Any]:
    """A row from a key and its own fields, the row's own `n` and `h` taking precedence over the key's."""
    return _row(**{**k, **kw})


def _ftp_thresholds() -> str:
    from extended import user_beside as B

    return "; ".join(f"{p} {'purchases' if m == 'combine_purchases' else 'lost'} >= {t} in {B.FTP_WINDOW}"
                     for p, m, t in B.FTP_BINDING) + " (user_beside.FTP_BINDING: D-497's grid, D-512 (4))"


#: the mechanics' rates (D-34's "a year"): a start's long replay is U1's horizon, one start's year (the red team's
#: cycle-1 note 1); the counts are read only on starts whose replay is that long (`year_problems`)
PER_YEAR = "per 252 sessions (a start's year): the mean count over starts whose long replay is U1's horizon"


def year_problems(recs: Sequence[Mapping[str, Any]], days: Sequence[int], cell: str) -> None:
    """Refusing: every start a rate is read on has observed exactly U1's horizon (`user_journey.HORIZON`), so its long
    replay -- `min(HORIZON, n - s)` sessions, the counts' run (`StartCounts` keeps it) -- is one start's year."""
    from propedge.research import user_journey as U

    by = {int(r["start_day"]): r for r in recs}
    bad = [d for d in days if int(by[int(d)]["observed"]) != int(U.HORIZON)]
    if bad:
        raise Refused(f"9.3: {cell}: {len(bad)} starts read for a rate per year without U1's horizon observed "
                      f"(first: start {bad[0]})")


def mechanics_rows(key: dict[str, Any], run: Mapping[str, Any], base: Mapping[str, Any]) -> list[dict[str, Any]]:
    """9.3 for one cell and its base, each block: where the lever binds, not whether it helps."""
    from extended import user_beside as B

    cell = key["cell"]
    s = spec(cell)
    out = []
    bo = {int(x["rec"]["start_day"]): x["rec"] for x in base["outs"]}
    recs = [x["rec"] for x in run["outs"]]
    for bname, which in BLOCKS:
        for h in DIFFER_SESSIONS:
            days = PR.block_days(recs, which, h)
            if not days:
                continue
            by = {int(r["start_day"]): r for r in recs}
            v = np.mean([float(PR.differs_within(by[d], bo[d], h)) for d in days if d in bo])
            out.append(_row(section="mechanics", part="mechanics", **key, block=bname,
                            measure=f"share_starts_differing_within_{h}", stat="share", value=float(v), n=len(days),
                            h=h))
        days = PR.block_days(recs, which, 252)
        cs = [run["counts"][d] for d in days if d in run["counts"]]
        bs = [base["counts"][d] for d in days if d in base["counts"]]
        k = dict(section="mechanics", part="mechanics", **key, block=bname, n=len(cs), h=252)
        if not cs:
            continue
        for name, src in (("requests_at_early_close_or_holiday_eve", "tally"),
                          ("executed_open_at_minutes_release_at_allowance", "tally")):
            for who, r in (("cell", run), ("base", base)):
                t = r.get("tally")
                if t is None or name not in t.columns:
                    raise Refused(f"9.3: {cell}: the {who}'s {name} is not counted (the calendars' counts)")
                v = t.set_index("start_day").reindex(days)[name].to_numpy(float)
                out.append(_rk(k, measure=name, stat=who, value=float(np.nansum(v)),
                                note="E-029's calendar (holiday-hours reach)" if "holiday" in name else
                                "E-050's calendar: a count, never a ruling"))
        year_problems(recs, days, cell)
        for name in ("evaluations_bought", "activations", "reactivations"):
            for who, cc in (("cell", cs), ("base", bs)):
                out.append(_rk(k, measure=f"{name}_per_year", stat=who,
                                value=float(np.mean([c.get(name, 0) for c in cc])) if cc else NAN, note=PER_YEAR))
        for name in ("max_accounts_live", "max_trades_one_session"):
            out.append(_rk(k, measure=name, stat="max", value=float(max(c.get(name, 0) for c in cs))))
        for name in ("purchase_days_refused_cash", "activations_refused_cash", "reactivations_refused_cash",
                     "same_day_bought_and_breached"):
            out.append(_rk(k, measure=name, stat="count", value=float(sum(c.get(name, 0) for c in cs)),
                            note="must be zero (D-549)" if name.startswith("same_day") else
                            "the replay's bankroll premise: printed with its rows when nonzero"))
        if s.lever == "L-B":
            for name in ("eligible_losses", "eligible_losses_first_life", "eligible_losses_later_life",
                         "reactivations", "reactivations_first", "reactivations_second", "reactivations_refused_limit",
                         "reactivations_refused_cash", "reactivations_refused_placement", "reactivations_refused_seat",
                         "reactivations_lapsed"):
                out.append(_rk(k, measure=name, stat="per_start", value=float(np.mean([c.get(name, 0) for c in cs])),
                                note="a delayed reactivation refused for want of a free seat on a later evening (the "
                                     "build's reading: never a sixth account)" if name.endswith("seat") else ""))
            waits = [w for c in cs for w in (c.get("reactivation_wait_sessions") or ())]
            out.append(_rk(k, measure="sessions_loss_to_first_trade", stat="median", value=_q(waits, 0.5),
                            n=len(waits)))
            fates = [f for c in cs for f in (c.get("reactivated_fates") or ())]
            for name in ("won_opening", "paid", "lost_before_payout"):
                out.append(_rk(k, measure=f"reactivated_{name}", stat="share",
                                value=float(np.mean([bool(f[name]) for f in fates])) if fates else NAN, n=len(fates)))
            out.append(_rk(k, measure=f"max_reactivations_in_{B.FTP_WINDOW}_sessions", stat="max",
                            value=float(max(rolling_max(c.get("reactivation_days") or (), B.FTP_WINDOW) for c in cs)),
                            note="beside the Focused Trader models' thresholds: " + _ftp_thresholds()))
        if s.lever in ("L-I", "L-H"):
            waits = [w for c in cs for w in (c.get("queue_waits") or ())]
            for stat, q in (("median", 0.5), ("p90", 0.9), ("max", 1.0)):
                out.append(_rk(k, measure="queue_wait_calendar_days", stat=stat, value=_q(waits, q), n=len(waits)))
            for name in ("sessions_five_funded_evals_running", "passes_queued", "passes_expired"):
                out.append(_rk(k, measure=name, stat="per_start", value=float(np.mean([c.get(name, 0) for c in cs]))))
            out.append(_rk(k, measure="evaluations_bought_beyond_base", stat="per_start",
                            value=float(np.mean([c.get("evaluations_bought", 0) for c in cs])
                                        - np.mean([c.get("evaluations_bought", 0) for c in bs]))))
        if s.lever == "L-H":
            trig = [int(c.get("house_trigger_day", -1)) for c in cs]
            for h in TRIGGER_SESSIONS:
                out.append(_rk(k, measure=f"share_reaching_trigger_by_{h}", stat="share",
                                value=float(np.mean([0 <= t <= h for t in trig]))))
            hit = [t for t in trig if t >= 0]
            for stat, q in (("median", 0.5), ("p10", 0.1), ("p90", 0.9)):
                out.append(_rk(k, measure="trigger_session", stat=stat, value=_q(hit, q), n=len(hit)))
            for name in ("house_purchase_days_withheld", "house_rebills_withheld", "house_activations_withheld"):
                out.append(_rk(k, measure=name, stat="per_start", value=float(np.mean([c.get(name, 0) for c in cs]))))
            cw = [w for c in cs for w in (c.get("house_cash_waits") or ())]
            out.append(_rk(k, measure="passes_waited_for_cash_evenings", stat="median", value=_q(cw, 0.5), n=len(cw)))
            fb = [x["daily"].get("fell_back") for x in base["outs"] if int(x["rec"]["start_day"]) in set(days)]
            out.append(_rk(k, measure="base_starts_falling_back_below_zero", stat="share",
                            value=float(np.nanmean([float(v) for v in fb if v is not None])) if fb else NAN,
                            note="the cell keeps them ahead by construction (2.3)"))
        if s.lever == "L-N":
            for name in ("fees_subscription", "fees_activation"):
                out.append(_rk(k, measure=name, stat="cell_less_base",
                                value=float(np.mean([c.get(name, 0) for c in cs]) - np.mean([c.get(name, 0)
                                                                                              for c in bs]))))
    return out


# ------------------------------------------------------------------------------------------------ 10.1: the guard row


GUARD_NETS = ((1, "mean"), (2, "mean"), (3, "mean"), (6, "mean"), (6, "p10"), (6, "p50"), (6, "p90"), (12, "mean"),
              (12, "p10"), (12, "p50"), (12, "p90"))
GUARD_CVAR = (3, 6, 12)


def guard_values(t: pd.DataFrame, which: str | None, base: pd.DataFrame | None = None) -> dict[str, float]:
    """10.1 item 2: the mean net at months 1-3, the month-6 and month-12 net (mean, p10, p50, p90) and CVaR10 at months
    3, 6 and 12 -- each on the block's starts with its month's horizon left (with a base: on the starts both hold, the
    cell's less the base's)."""
    return guard_values_n(t, which, base)[0]


def guard_values_n(t: pd.DataFrame, which: str | None, base: pd.DataFrame | None = None
                   ) -> tuple[dict[str, float], dict[str, int]]:
    """`guard_values` and, beside each entry, the number of starts it reads (a guard entry with none is undefined and
    says why). Both are returned, never kept between calls (the red team's cycle-1 note: the old module-level `NS`
    was safe only while the reading ran on one thread)."""
    out: dict[str, float] = {}
    ns: dict[str, int] = {}
    recs = PR.records_of(t)
    a = t.set_index("start_day")
    b = base.set_index("start_day") if base is not None else None

    def vals(frame: pd.DataFrame, days: list[int], col: str) -> np.ndarray:
        return frame.loc[days, col].to_numpy(float) if days else np.zeros(0)

    for m, stat in GUARD_NETS:
        days = PR.block_days(recs, which, RD.month_horizon(m))
        if b is not None:
            days = [d for d in days if d in b.index]
        col = f"net_month_{m}"

        def f(x: np.ndarray) -> float:
            x = x[np.isfinite(x)]
            if not x.size:
                return NAN
            return float(x.mean()) if stat == "mean" else float(np.quantile(x, {"p10": .1, "p50": .5, "p90": .9}[stat]))

        v = f(vals(a, days, col)) - (f(vals(b, days, col)) if b is not None else 0.0)
        out[f"net_m{m}_{stat}"] = v
        ns[f"net_m{m}_{stat}"] = len(days)
    for m in GUARD_CVAR:
        days = PR.block_days(recs, which, RD.month_horizon(m))
        if b is not None:
            days = [d for d in days if d in b.index]
        col = f"net_month_{m}"
        v = float(M.cvar(vals(a, days, col), 0.10))
        if b is not None:
            v -= float(M.cvar(vals(b, days, col), 0.10))
        out[f"cvar10_m{m}"] = v
        ns[f"cvar10_m{m}"] = len(days)
    return out, ns


def guard_rows(t: pd.DataFrame, key: dict[str, Any], base: pd.DataFrame | None = None, gate: Mapping[str, float]
               | None = None, label: str = "") -> list[dict[str, Any]]:
    out = []
    for bname, which in BLOCKS:
        g, ns = guard_values_n(t, which, base)
        for k, v in g.items():
            n = int(ns.get(k, 0))
            out.append(_row(section="guard", part="guard", **key, block=bname, measure=k,
                            stat="cell_less_base" if base is not None else "value", value=float(v), n=n,
                            note="" if n else "no start with the measure's horizon left on this block"))
        for k, v in (gate or {}).items():
            if k.startswith("_"):
                continue
            out.append(_row(section="guard", part="guard", **key, block=bname, measure=k, stat="gate", value=float(v),
                            note=label or "the gate at 0 %"))
    return out


def frontier_rows(cards: Mapping[str, Mapping[str, Mapping[str, Any]]], key: dict[str, Any], *, with_house: bool
                  ) -> list[dict[str, Any]]:
    """10.1 item 1: the frontier on P, S1, S3a and S5a across a base's cells -- without the house-money cells, and
    beside it the version with them, labelled "gaming P (E-134 (2))" (the red team's m6)."""
    from propedge.research import u_select as US

    cells = [c for c in ("ref", *NEW_CELLS) if c in cards and (with_house or c not in HOUSE_CELLS)]
    out = []
    lab = LR.LABEL_GAMING_P if with_house else "without the house-money cells"
    for bname, _ in BLOCKS:
        pts = {c: [_f(cards[c][bname][k]["value"]) for k in FRONTIER] for c in cells}
        sign = [1.0 if US.BY_KEY[k].direction == US.HIGHER else -1.0 for k in FRONTIER]

        def dom(p: list, q: list) -> bool:
            if not all(math.isfinite(v) for v in p + q):
                return False
            return all(s * x >= s * y for s, x, y in zip(sign, p, q)) and any(s * x > s * y for s, x, y in
                                                                                zip(sign, p, q))

        for c in cells:
            by = [o for o in cells if o != c and dom(pts[o], pts[c])]
            out.append(_row(section="scorecard", part="frontier_with_house" if with_house else "frontier", **key,
                            cell=c, block=bname, measure="on_frontier_P_S1_S3a_S5a", stat="value", value=float(not by),
                            note=lab + ("; dominated by " + ", ".join(by) if by else "")))
    return out


def s6_rows(frames: Mapping[str, pd.DataFrame], key: dict[str, Any], lever: str) -> list[dict[str, Any]]:
    """10.1 item 4, S6's form: across a lever's cells and its base, each measure's start-day share of the variance."""
    cells = [c for c in frames if c == "ref" or lever_of(c) == lever]
    if len(cells) < 2:
        return []
    out = []
    tabs = {c: frames[c].set_index("start_day") for c in cells}
    recs = PR.records_of(frames[cells[0]])
    for bname, which in BLOCKS:
        for m in PR.MEASURES:
            days = [int(r["start_day"]) for r in RD.block(recs, which, m.hkey)
                    if all(int(r["start_day"]) in tabs[c].index for c in cells)]
            X = np.column_stack([tabs[c].loc[days, m.col].to_numpy(float) for c in cells]) if days else \
                np.zeros((0, len(cells)))
            X = X[np.isfinite(X).all(axis=1)]
            tot = float(((X - X.mean()) ** 2).sum()) if len(X) else 0.0
            k = dict(section="scorecard", part="s6", **key, cell=",".join(cells), block=bname, measure=m.name,
                     h=RD.horizon(m.hkey), n=int(len(X)))
            if len(X) < 2 or not tot > 0:
                out.append(_rk(k, stat="start_share", value=NAN, note="no variance or too few starts"))
                continue
            g = X.mean()
            out.append(_rk(k, stat="start_share", value=len(cells) * float(((X.mean(axis=1) - g) ** 2).sum()) / tot,
                            note=f"the start day's share across {lever}'s cells and the base"))
    return out


def evenness_rows(frames: Mapping[str, pd.DataFrame], cards: Mapping[str, Any], key: dict[str, Any], lever: str
                  ) -> list[dict[str, Any]]:
    """10.1 item 11: each lever's cells as points of "ahead" (P) against each evenness measure (E-015's menu form);
    house money's labelled."""
    out = []
    cells = [c for c in frames if (c == "ref" or lever_of(c) == lever) and c in cards]
    for bname, which in BLOCKS:
        for name in PR.EVENNESS:
            m = PR.BY_NAME[name]
            for c in cells:
                t = frames[c]
                days = [int(r["start_day"]) for r in RD.block(PR.records_of(t), which, m.hkey)]
                x = t.set_index("start_day").loc[days, m.col].to_numpy(float) if days else np.zeros(0)
                x = x[np.isfinite(x)]
                note = LR.LABEL_GAMING_P if c in HOUSE_CELLS else ""
                out.append(_row(section="scorecard", part="evenness_tradeoff", **key, cell=c, block=bname,
                                measure=name, stat="evenness_mean", value=float(x.mean()) if x.size else NAN,
                                n=int(x.size), note=note))
                out.append(_row(section="scorecard", part="evenness_tradeoff", **key, cell=c, block=bname,
                                measure=name, stat="P", value=_f(cards[c][bname]["P"]["value"]), note=note))
    return out


def diverge_rows(key: dict[str, Any], run: Mapping[str, Any], base: Mapping[str, Any]) -> list[dict[str, Any]]:
    """10.1 item 6: what diverges per start (long replays, all starts): funded accounts activated, reactivated and lost;
    evaluations bought, abandoned and passed; passes waiting and lost; fees by kind; payouts' count and size."""
    out = []

    def tot(r: Mapping[str, Any], name: str) -> list[float]:
        if name in ("passes", "funded_activated", "payouts", "payout_cash"):
            v = {"passes": [len(x["rec"]["pass_days"]) for x in r["outs"]],
                 "funded_activated": [len(x["rec"]["funded_days"]) for x in r["outs"]],
                 "payouts": [len(x["rec"]["pay_days"]) for x in r["outs"]],
                 "payout_cash": [float(sum(x["rec"]["pay_cash"])) for x in r["outs"]]}[name]
            return [float(a) for a in v]
        if name == "funded_lost":
            t = r.get("tally")
            return [] if t is None or name not in t.columns else [float(v) for v in t[name].to_numpy(float)]
        return [float(c.get(name, 0) or 0) for c in r["counts"].values()]

    for name in ("passes", "funded_activated", "funded_lost", "payouts", "payout_cash", "evaluations_bought",
                 "activations", "reactivations", "house_rebills_withheld", "passes_queued", "passes_expired",
                 "fees_subscription", "fees_activation", "reactivation_fees"):
        x, y = tot(run, name), tot(base, name)
        for stat, v in (("cell_mean", np.mean(x) if x else NAN), ("base_mean", np.mean(y) if y else NAN)):
            out.append(_row(section="diverge", part="diverge", **key, block="all", measure=name, stat=stat,
                            value=float(v), n=len(x)))
        out.append(_row(section="diverge", part="diverge", **key, block="all", measure=name, stat="cell_less_base",
                        value=float(np.mean(x) - np.mean(y)) if x and y else NAN, n=len(x)))
    return out


# ------------------------------------------------------------------------------------------------ the reading


def comparisons(cells: Sequence[str]) -> list[tuple[str, str]]:
    """Each cell against `ref`, and section 7.3's own comparisons (cell, base)."""
    out = [(c, "ref") for c in cells if c != "ref"]
    have = set(cells)
    if {"b2f1", "b2f2"} <= have:
        out.append(("b2f2", "b2f1"))
    for c in INV_CELLS:
        s = spec(c)
        if s.c == "7":
            out.append((c, c.replace("inv7", "inv5")))
        if s.banking:
            out.append((c, c.replace("_bank_", "_hold_")))
        if s.expiry == "30":
            out.append((c, c[:-3] + "_none"))
    for c in HOUSE_CELLS:
        s = spec(c)
        if s.house == "zero":
            out.append((c, c.replace("zero", "stop")))
        if s.expiry == "30":
            out.append((c, c[:-3] + "_none"))
    return [(a, b) for a, b in out if a in have and b in have]


def label_house(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """M4: "gaming P (E-134 (2))" on every row that holds a house-money cell -- as the cell, as the base, or in a list
    of cells -- in every file (card, distribution, paired, guard, mechanics, ...)."""
    for r in rows:
        names = {str(r.get("cell") or ""), str(r.get("base") or "")}
        names |= set(str(r.get("cell") or "").replace("->", ",").split(","))
        if names & set(HOUSE_CELLS) and LR.LABEL_GAMING_P not in str(r.get("note") or ""):
            r["note"] = "; ".join(x for x in (str(r.get("note") or ""), LR.LABEL_GAMING_P) if x)
    return rows


#: U-6's two readings (10.1 item 8): a Back2Funded row carries exactly the one of its variant (the red team's R2)
U6_LABELS = (LR.label("reactivation_counted_as_purchase"), LR.label("reactivation_counted_conservative"))


def u6_label(mode: str) -> str:
    """U-6's label of a row's variant: "counted: the conservative reading" for the counted variant, else (the
    headline, `declared`) "not counted: the optimistic reading"."""
    return U6_LABELS[1] if str(mode) == CONSERVATIVE else U6_LABELS[0]


def _names_b2f(r: Mapping[str, Any]) -> bool:
    names = {str(r.get("cell") or ""), str(r.get("base") or "")}
    names |= set(str(r.get("cell") or "").replace("->", ",").split(","))
    return bool(names & set(B2F_CELLS))


def label_u6(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """R2: every row naming a Back2Funded cell -- as the cell, as the base, or in a list of cells -- carries its
    variant's U-6 label and not the other's (step 5's reading file, `cl_reading_ftp.csv`)."""
    for r in rows:
        if not _names_b2f(r) and str(r.get("mode") or "") != CONSERVATIVE:
            continue
        want = u6_label(str(r.get("mode") or ""))
        parts = [x for x in str(r.get("note") or "").split("; ") if x and x not in U6_LABELS]
        r["note"] = "; ".join([*parts, want])
    return rows


def reading_rows(runs: Mapping[tuple, Mapping[str, Any]], honesty: dict, no_effect: set,
                 gate_guard: Mapping[tuple, Mapping[str, float]] | None = None) -> list[dict[str, Any]]:
    """10.1 on the kept runs: each run's card, distributions and guard row (its gate entry the cell's 0 % gate, `ref`'s
    its registered row, under every response); each pair's paired readings, card, guard row and divergences; across
    each base's cells the frontiers, S6's form and the evenness trade-off. Every house-money row labelled (M4)."""
    rows: list[dict[str, Any]] = []
    frames = {k: PR.start_frame(k[0], k[1], k[3], r["outs"]) for k, r in runs.items()}
    cards = {k: {b: PR.card_of([x["rec"] for x in runs[k]["outs"]], w) for b, w in BLOCKS} for k in runs}
    gg = gate_guard or {}
    for k, t in frames.items():
        d, arm, cell, rname, var = k
        if k in no_effect:
            continue
        key = dict(design=d, arm=arm, cell=cell, mode=var or "declared", response=rname)
        rows += PR.card_rows(cards[k], key)
        rows += PR.distribution_rows(t, key)
        g = gg.get((d, cell))
        rows += guard_rows(t, key, None, g, (g or {}).get("_label", ""))
    groups = sorted({(k[0], k[1], k[3], k[4]) for k in runs})
    for d, arm, rname, var in groups:
        cells = [k[2] for k in runs if (k[0], k[1], k[3], k[4]) == (d, arm, rname, var)]
        if var and "ref" not in cells and (d, arm, "ref", rname, "") in runs:
            cells.append("ref")
        for c, b in comparisons(cells):
            ck = (d, arm, c, rname, var)
            bk = (d, arm, b, rname, var if (d, arm, b, rname, var) in runs else "")
            if ck in no_effect or bk not in runs or ck not in runs:
                continue
            key = dict(design=d, arm=arm, cell=c, mode=var or "declared", response=rname, base=b)
            rows += PR.paired_rows(frames[ck], frames[bk], key, honesty)
            rows += PR.paired_card_rows([x["rec"] for x in runs[ck]["outs"]], [x["rec"] for x in runs[bk]["outs"]], key)
            rows += guard_rows(frames[ck], key, frames[bk], None, "")
            rows += diverge_rows(key, runs[ck], runs[bk])
        cd = {k[2]: cards[k] for k in runs if (k[0], k[1], k[3], k[4]) == (d, arm, rname, var)}
        fr = {k[2]: frames[k] for k in runs if (k[0], k[1], k[3], k[4]) == (d, arm, rname, var)}
        key = dict(design=d, arm=arm, mode=var or "declared", response=rname)
        rows += frontier_rows(cd, key, with_house=False) + frontier_rows(cd, key, with_house=True)
        for lever in ("L-B", "L-I", "L-H", "L-N"):
            rows += s6_rows(fr, key, lever) + evenness_rows(fr, cd, key, lever)
    return label_house(rows)


# ------------------------------------------------------------------------------------------------ the menu


def _first(df: pd.DataFrame, **eq: Any) -> float:
    m = np.ones(len(df), bool)
    for k, v in eq.items():
        m &= (df[k].astype(str) == str(v)).to_numpy()
    s = df[m]
    return float(s["value"].iloc[0]) if len(s) else NAN


GUARD_COLUMNS = tuple(f"net_m{m}_{s}" for m, s in GUARD_NETS) + tuple(f"cvar10_m{m}" for m in GUARD_CVAR)
GATE_GUARD = ("growth_on_required_bankroll", "required_bankroll_p90", "ruin_probability")


def menu_table(reading: pd.DataFrame, approved_limits: Sequence[Mapping[str, Any]], no_effect: set,
               solver_view: pd.DataFrame | str | None = None, ftp_gap: bool = True, *, excuse_guard: bool = False
               ) -> pd.DataFrame:
    """10.1 item 12 (and 8's beside menus): each (design, arm, cell, response, variant) of the reading against `ref`
    under the same response -- its P and paired difference with the guard row beside in the same row, D-34's purchases a
    year beside growth, Back2Funded's reactivations per 21 sessions, the funded accounts lost; the flags (mechanical),
    the labels, E-015's limits; stage 0's view beside the Back2Funded and `naf` rows (printed, never ordering or
    flagging a row: a string or a frame, read nowhere else); the order is the grid's, never P's."""
    rows = []
    paired = reading[(reading["part"] == "paired") & (reading["base"] == "ref")]
    guard = reading[reading["part"] == "guard"]
    mech = reading[reading["part"] == "mechanics"]
    div = reading[reading["part"] == "diverge"]
    card = reading[(reading["part"] == "card") & (reading["stat"] == "value") & (reading["base"].fillna("") == "")]
    n_int = int((reading[reading["part"] == "paired"]["stat"] == "ci90_low").sum())
    seen = list(dict.fromkeys(str(x) for x in card["design"]))
    designs = [d for d in DESIGNS if d in seen] + [d for d in seen if d not in DESIGNS]
    resp = list(dict.fromkeys(str(x) for x in card["response"]))
    modes = list(dict.fromkeys(str(x) for x in card["mode"]))
    combos = [(d, a, c, r, m) for d in designs for r in resp for m in modes for a in ARMS for c in ("ref", *NEW_CELLS)
              if ((card["design"] == d) & (card["arm"] == a) & (card["cell"] == c) & (card["response"] == r)
                  & (card["mode"] == m)).any() or (d, a, c, r, "" if m == "declared" else m) in no_effect]

    def sub(df: pd.DataFrame, d: str, a: str, c: str, r: str, m: str) -> pd.DataFrame:
        return df[(df["design"] == d) & (df["arm"] == a) & (df["cell"] == c) & (df["response"] == r)
                  & (df["mode"] == m)]

    for d, arm, cell, rname, mode in combos:
        s = spec(cell)
        row: dict[str, Any] = {"design": d, "arm": arm, "cell": cell, "lever": s.lever, "response": rname,
                               "variant": mode, "base": "" if cell == "ref" else "ref"}
        lv = sub(card, d, arm, cell, rname, mode)
        gl = sub(guard, d, arm, cell, rname, mode)
        gl = gl[(gl["base"].fillna("") == "") & (gl["block"] == "all")]
        row["P_level"] = _first(lv, block="all", measure="card_P")
        why = []
        for g in GUARD_COLUMNS:
            row[f"guard_{g}"] = _first(gl[gl["stat"] == "value"], measure=g)
            gv = gl[(gl["stat"] == "value") & (gl["measure"] == g)]
            if len(gv) and int(gv["n"].iloc[0]) == 0:
                why.append(g)
        row["guard_reason"] = (f"{', '.join(why)}: no start with the measure's horizon left" if why else "")
        for g in GATE_GUARD:
            row[f"guard_{g}"] = _first(gl[gl["stat"] == "gate"], measure=g)
        gn = gl[gl["stat"] == "gate"]["note"]
        row["guard_gate_label"] = str(gn.iloc[0]) if len(gn) else ""
        mm = sub(mech, d, arm, cell, rname, mode)
        row["evaluations_bought_per_year"] = _first(mm, block="all", measure="evaluations_bought_per_year", stat="cell")
        row["reactivations_per_year"] = _first(mm, block="all", measure="reactivations_per_year", stat="cell")
        row["max_reactivations_in_21_sessions"] = _first(mm, block="all", measure="max_reactivations_in_21_sessions",
                                                          stat="max")
        dv = sub(div, d, arm, cell, rname, mode)
        row["funded_lost_mean"] = _first(dv, measure="funded_lost", stat="cell_mean")
        labels = [LR.LABEL_DESCRIBED, LR.LABEL_FIRST_ORDER]
        flags: list[str] = []
        if cell != "ref":
            pp = sub(paired, d, arm, cell, rname, mode)
            pg = sub(guard, d, arm, cell, rname, mode)
            pg = pg[pg["base"] == "ref"]
            row.update({"P_mean_difference": _first(pp, block="all", measure="P", stat="mean"),
                        "P_ci90_low": _first(pp, block="all", measure="P", stat="ci90_low"),
                        "P_ci90_high": _first(pp, block="all", measure="P", stat="ci90_high"),
                        "P_mdd": _first(pp, block="all", measure="P", stat="mdd"),
                        "P_n_w": _first(pp, block="all", measure="P", stat="n_w")})
            flipped = []
            e, l_ = _first(pp, block="early", measure="P", stat="mean"), _first(pp, block="late", measure="P", stat="mean")
            if np.isfinite(e) and np.isfinite(l_) and np.sign(e) * np.sign(l_) < 0:
                flipped.append("P")
            for g in GUARD_COLUMNS:
                row[f"guard_{g}_difference"] = _first(pg[pg["block"] == "all"], measure=g)
                e = _first(pg[pg["block"] == "early"], measure=g)
                l_ = _first(pg[pg["block"] == "late"], measure=g)
                if np.isfinite(e) and np.isfinite(l_) and np.sign(e) * np.sign(l_) < 0:
                    flipped.append(g)
            if flipped:
                flags.append(LR.LABEL_NOT_STABLE)
            row["flipped_measures"] = "; ".join(flipped)
            if (d, arm, cell, rname, "" if mode == "declared" else mode) in no_effect:
                labels.append(LR.LABEL_NO_EFFECT)
        if s.lever == "L-H":
            flags.append(LR.LABEL_GAMING_P)
        if s.lever == "L-B":
            labels += [x for x in LR.B2F_LABELS if x not in U6_LABELS]
            if rname.startswith("ftp_"):
                labels.append("a reactivation is bought before the evening's placement is read (2.1; the engine's "
                              "placement binds from tomorrow): under a Corrective model the account just bought may be "
                              "closed at once")
            labels.append(u6_label(mode))
        if s.lever in ("L-H", "L-N") and ftp_gap:
            flags.append(LR.LABEL_FTP_NOT_READ)
            labels.append(f"{LR.LABEL_FTP_NOT_READ}: " + (
                "not read (section 4's gap)" if s.naf else LR.FTP_GAP_REASON["house"]))
        if s.expiry != "none":
            labels.append("U-1: the hold's expiry unstated; both readings run")
        row["flags"] = "; ".join(flags)
        row["labels"] = "; ".join(labels)
        row["ordered_on_P"] = False
        if s.lever in ("L-B", "L-N"):
            row["solver_view"] = solver_view_text(solver_view, d, "G-B" if s.lever == "L-B" else "G-N")
            row["solver_view_label"] = LR.LABEL_SOLVER_VIEW + ": deciding nothing, beside the replay's readings"
        crossed = []
        for lim in approved_limits:
            v, b = _f(row.get(lim["column"])), _f(lim["bound"])
            if math.isfinite(v) and ((lim["kind"] == "max" and v > b) or (lim["kind"] == "min" and v < b)):
                crossed.append(f"{lim['row']}: {lim['column']} {v:.6g}")
        row["limits"] = ("; ".join(f"{x['row']}: {x['column']} {x['kind']} {x['bound']}" for x in approved_limits)
                         if approved_limits else "none approved before the run's commit: the menu is read without flags")
        row["limits_crossed"] = "; ".join(crossed)
        rows.append(row)
    menu = pd.DataFrame(rows)
    if len(menu):
        menu["depends_on_expiry"] = False
        for i, r in menu.iterrows():
            if spec(r["cell"]).expiry != "30":
                continue
            other = menu[(menu["design"] == r["design"]) & (menu["arm"] == r["arm"]) & (menu["response"] ==
                                                                                         r["response"])
                         & (menu["variant"] == r["variant"]) & (menu["cell"] == r["cell"][:-3] + "_none")]
            if not len(other):
                continue
            o = other.iloc[0]
            cols = ["P_mean_difference"] + [f"guard_{g}_difference" for g in GUARD_COLUMNS]
            if any(np.isfinite(_f(r.get(c))) and np.isfinite(_f(o.get(c))) and np.sign(_f(r.get(c)))
                   * np.sign(_f(o.get(c))) < 0 for c in cols):
                for j in (i, o.name):
                    menu.at[j, "depends_on_expiry"] = True
                    menu.at[j, "flags"] = "; ".join(x for x in (menu.at[j, "flags"], LR.LABEL_DEPENDS_EXPIRY) if x)
    menu["intervals_printed"] = n_int
    menu["intervals_expected_to_exclude_zero_by_chance"] = n_int / 10.0
    menu["note_intervals"] = ("each a marginal 90 % interval, none simultaneous; a tenth would exclude zero by chance "
                              "alone were there no effect anywhere -- a count, not a level")
    menu["note_in_sample"] = "an in-sample description of the development window; no confirmation (E-023 (1))"
    menu["note_not_modelled"] = ("a user who stops when their own money runs out (except as house money declares it); "
                                 "the user's time; taxes; payouts unavailable in holiday hours; the move to a Live "
                                 "Funded Account; Topstep's unstated news rules (E-034); the gaps of 4.4")
    check_menu(menu, excuse_guard=excuse_guard)
    return menu


def solver_view_text(solver_view: pd.DataFrame | str | None, design: str, rule: str) -> str:
    """M7: stage 0's line for a base and rule, read from `cl_fit.csv`'s `solver_view` section; a string (stage 0
    stopped, its row named) is printed as given; None: stage 0 not read into this menu (said so)."""
    if solver_view is None:
        return "stage 0's view not given to this menu"
    if isinstance(solver_view, str):
        return solver_view
    sv = solver_view[(solver_view["design"].astype(str) == design) & (solver_view["rule"].astype(str) == rule)]
    if not len(sv):                                       # m-b: refused, never printed as a line
        raise Refused(f"stage 0's view has no {rule} line for {design} (cl_fit.csv's solver_view; m-b)")
    return "; ".join(str(x) for x in sv["line"])


def solver_view_problems(solver_view: pd.DataFrame, designs: Sequence[str]) -> list[str]:
    """m-b, before any of the engine's work: `cl_fit.csv`'s `solver_view` section holds a G-B and a G-N line for every
    design read, each with its `design`, `rule` and `line` columns."""
    miss = [c for c in ("design", "rule", "line") if c not in solver_view.columns]
    if miss:
        return [f"stage 0's view lacks the columns {miss}"]
    out = []
    for d in designs:
        for rule in ("G-B", "G-N"):
            sv = solver_view[(solver_view["design"].astype(str) == d) & (solver_view["rule"].astype(str) == rule)]
            if not len(sv) or not sv["line"].astype(str).str.strip().ne("").all():
                out.append(f"stage 0's view has no {rule} line for {d}")
    return out


HEX_TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{7,40}(?![0-9a-fA-F])")


def fit_commit_problem(row_line: str | None, git_commit: str | None) -> str | None:
    """m-b: `cl_fit.csv`'s manifest commit held to the commit the `--stage0-row` row names -- the manifest's
    `git_commit` clean (no `-dirty`, not unknown) and beginning with a hexadecimal token (7 to 40 characters) of the
    row's own line. None when it holds; else why."""
    if not row_line:
        return "the stage-0 row is not in DECISIONS.md, so cl_fit.csv's commit cannot be held to it"
    c = str(git_commit or "").strip()
    if not c or c == "unknown" or c.endswith("-dirty"):
        return f"cl_fit.csv's manifest commit {c or 'none'!r} is not a clean commit"
    tokens = HEX_TOKEN.findall(row_line)
    if not any(c.lower().startswith(t.lower()) for t in tokens):
        return f"cl_fit.csv's manifest commit {c[:12]} is not the commit its row names ({tokens[:3] or 'none'})"
    return None


def solver_view_frame(path: Path, *, row_line: str | None = None, designs: Sequence[str] | None = None,
                      hold_commit: bool = True) -> pd.DataFrame:
    """M7: `cl_fit.csv`'s `solver_view` section, the file verified through its manifest; m-b: its manifest's commit
    held to the commit the stage-0 row (`row_line`, its line of DECISIONS.md) names (`hold_commit`, the real run's),
    and, given `designs`, a G-B and a G-N line for each -- else refused."""
    from extended import results as XR

    ok, msg = XR.verify_result(path)
    if not ok:
        raise Refused(f"{path.name}: {msg}")
    if hold_commit:
        why = fit_commit_problem(row_line, XR.read_manifest(path).git_commit)
        if why:
            raise Refused(f"{why} (m-b)")
    f = XR.read_result(path)
    sv = f[f["section"].astype(str) == "solver_view"].reset_index(drop=True)
    probs = solver_view_problems(sv, designs) if designs is not None else []
    if probs:
        raise Refused("; ".join(probs) + " (m-b)")
    return sv


def excused_names(reason: Any) -> list[str]:
    """The guard entries a menu row's `guard_reason` names ("a, b: no start with the measure's horizon left")."""
    text = "" if reason is None or (isinstance(reason, float) and not math.isfinite(reason)) else str(reason)
    head = text.split(":", 1)[0].strip()
    return [x.strip() for x in head.split(",") if x.strip()] if head else []


def check_menu(menu: pd.DataFrame, *, excuse_guard: bool = False) -> None:
    """T-14, refusing (M2): no finite P or P difference beside a missing or non-finite guard entry -- every net of the
    guard row and the gate's entries; every house-money row labelled "gaming P (E-134 (2))" and never ordered on P;
    every house-money and `naf` row naming the Focused Trader gap.

    The guard excuse (m-a): a net or CVaR entry with no start that has its horizon left is undefined, and a row may
    name it in `guard_reason` -- **only on toys** (`excuse_guard`, the synthetic run's: on the window every block holds
    starts with 252 sessions left). Only `GUARD_COLUMNS`' names are excusable, never a gate entry; the real run (the
    default) refuses any row with a reason at all."""
    if not len(menu):
        return
    need = [f"guard_{g}" for g in (*GUARD_COLUMNS, *GATE_GUARD)]
    for _, r in menu.iterrows():
        named = excused_names(r.get("guard_reason"))
        if named and not excuse_guard:
            raise Refused(f"the menu excuses {r['design']} {r['cell']} ({r.get('response', 'off')})'s guard entries "
                          f"{named[:4]}: no guard entry is excused in the real run (E-134 (2); m-a)")
        bad = [x for x in named if x not in GUARD_COLUMNS]
        if bad:
            raise Refused(f"the menu excuses {r['design']} {r['cell']}'s {bad[:4]}: only the guard row's nets and CVaR "
                          "may be excused, never a gate entry (m-a)")
        has_p = np.isfinite(_f(r.get("P_level"))) or np.isfinite(_f(r.get("P_mean_difference")))
        if has_p:
            missing = [c for c in need if (c not in r.index or not np.isfinite(_f(r.get(c))))
                       and c[len("guard_"):] not in named]
            if missing:
                raise Refused(f"the menu prints {r['design']} {r['cell']} ({r.get('response', 'off')})'s P beside "
                              f"missing guard entries {missing[:4]} (E-134 (2))")
        s = spec(str(r["cell"]))
        if s.lever == "L-H" and (LR.LABEL_GAMING_P not in str(r.get("flags", "")) or bool(r.get("ordered_on_P"))):
            raise Refused(f"{r['cell']}: a house-money row not labelled {LR.LABEL_GAMING_P!r} or ordered on P")
        if s.lever in ("L-H", "L-N") and LR.LABEL_FTP_NOT_READ not in str(r.get("labels", "")):
            raise Refused(f"{r['cell']}: the Focused Trader gap is not named on its row")


# ------------------------------------------------------------------------------------------------ the seeds


def declaration_path(root: Path = ROOT) -> Path:
    p = Path(root) / DECLARATION
    return p if p.is_file() else Path(root) / DRAFT_DECLARATION


def declared_seed(role_prefix: str, root: Path = ROOT, strict: bool = True) -> int:
    """A seed of section 12 read from the declaration itself (so no seed of the block is written in code, T-9): the
    row whose status is 'in use' and whose 'what it draws' starts with `role_prefix`. Strict (the real run): the file
    under its pinned name, hashing to its pin in DECISIONS.md."""
    from extended import reader

    path = Path(root) / DECLARATION if strict else declaration_path(root)
    if strict:
        pins = reader.pins((Path(root) / "DECISIONS.md").read_text(encoding="utf-8")).get(DECLARATION) or set()
        if PR.sha256_lf(path) not in pins:
            raise Refused(f"{DECLARATION} does not hash to its pin in DECISIONS.md")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    sec = text.split("\n## 12.", 1)[1].split("\n## 13.", 1)[0]
    for seed, status, what in re.findall(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", sec, re.MULTILINE):
        if status.strip().lower().startswith("in use") and what.strip().startswith(role_prefix):
            return int(seed)
    raise Refused(f"no seed in use for {role_prefix!r} in the declaration's section 12")


HONESTY_ROLE = "10.2 item 7's honesty series"
TOY_ROLE = "the build's toy campaigns"


# ------------------------------------------------------------------------------------------------ step 3


def _no_effect(runs: Mapping[tuple, Mapping[str, Any]]) -> set:
    out = set()
    for k, r in runs.items():
        d, arm, cell, rname, var = k
        b = runs.get((d, arm, "ref", rname, ""))
        if cell != "ref" and b is not None and PR.identical_outputs(r["outs"], b["outs"]):
            out.add(k)
    return out


def keep_compact(runs: Mapping[tuple, Mapping[str, Any]]) -> None:
    """m9: after 9.1 item 7's checks, each start's closes and acts are kept only for `ref` and the `_none` cells (the
    expiry pair's other half reads them); every other run keeps its counts without them."""
    for k, r in runs.items():
        cell = k[2]
        if cell == "ref" or cell.endswith("_none"):
            continue
        for c in r["counts"].values():
            for name in ("cash_closes", "acts", "fee_days"):
                c.pop(name, None)


def tally_of(x: Mapping[str, Any], d: str, arm: str, rname: str, cal: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """M5: each start's tallies -- RD-02's `start_tallies` (the requests at an early close or a holiday's eve, E-029's
    calendar, E-104 D4's rule) and, with the recorder, `recorder_tallies` (the trades open at the 13:00 CT minutes
    release executed at the full allowance, E-050's calendar; the funded accounts lost)."""
    job = x["job"]
    lag = int(job["args"]["path"]["payout_lag_days"])
    t = PR.start_tallies(x["outs"], job["dates"], lag, PR.holiday_sessions(cal, job["dates"]))
    rt = PR.recorder_tallies(x["rec"], d, arm, rname, cal) if x.get("rec") is not None else None
    return PR.merge_tallies(t, rt)


def run_scorecard(inputs: Any, *, designs: Sequence[str] = DESIGNS, starts: int | None = None, workers: int = 1,
                  gate: bool = True, honesty_reps: int = RD.HONESTY_SERIES, honesty_seed: int | None = None,
                  approved_limits: Sequence[Mapping[str, Any]] = (), solver_view: pd.DataFrame | str | None = None,
                  cells: Sequence[str] = STEP3_ORDER, root: Path = ROOT, authorise_gate: Callable[[], Any] | None = None,
                  log: Callable[[str], None] = print, excuse_guard: bool = False) -> dict[str, Any]:
    """Section 15 step 3, in its order: (a) `ref` on each base at `off`, both arms, the recorder on (9.1 items 2's
    repeat and 4, and T-4's seat limits on the replay and the gate); (b) each new cell in step 3's order, both arms,
    the recorder on, checked under 9.1 items 5 and 7 before anything of it is read; (c) the gates in the same order
    (`authorise_gate`, the runner's authorisation of `levers_gate_beside`, called just before the first); (d) the
    oracles and the mechanics, then the reading and the menu without its beside sections. The two calendars are read,
    each refused unless it hashes to its pin, before the first replay (M5). Raises `Refused` at the first failed check."""
    import user_journey as UJ

    seed = declared_seed(HONESTY_ROLE, root) if honesty_seed is None else int(honesty_seed)
    cal = PR.calendar_frames(root)                       # M5: each refused unless it hashes to E-152's sha256
    jobs = {d: inputs.jobs(d) for d in designs}
    runs: dict[tuple, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for d in designs:
        probs = seat_limit_problems(jobs[d]["verdict"]["args"]["path"])
        if probs:
            raise Refused(f"T-4: {d}: the build stops and reports -- " + "; ".join(probs))
    # (a) the references
    for d in designs:
        for arm in ARMS:
            job = jobs[d][arm]
            chosen = UJ.start_choice(len(job["blocks"]), starts)
            x = replay_run(job, d, arm, "ref", "off", chosen, workers, record=True)
            probs = list(inputs.identity_problems(d, arm, x["outs"]))
            probs += [f"recorder: {p}" for p in x["rec"].problems()]
            tot = lever_totals(x["counts"])
            if any(tot.values()):
                probs.append(f"9.1 item 4: the options are not off in ref ({ {k: v for k, v in tot.items() if v} })")
            rows += identity_rows(d, arm, "ref", "9.1 items 2's repeat and 4", probs, len(x["outs"]))
            if probs:
                raise Refused(f"{d} {arm} ref: " + "; ".join(probs[:6]))
            x["tally"] = tally_of(x, d, arm, "off", cal)
            x["rec"] = None
            runs[run_key(d, arm, "ref")] = x
            log(f"identity HOLDS: {d} {arm} ref (9.1 items 2's repeat and 4), {len(x['outs'])} starts")
    # (b) the new cells
    for d in designs:
        for cell in cells:
            for arm in ARMS:
                job = jobs[d][arm]
                chosen = UJ.start_choice(len(job["blocks"]), starts)
                x = replay_run(job, d, arm, cell, "off", chosen, workers, record=True)
                base = runs[run_key(d, arm, "ref")]
                probs = [f"9.1 item 5 (recorder): {p}" for p in x["rec"].problems()]
                probs += [f"9.1 item 7: {p}" for p in before_binding_problems(cell, x, base)]
                s = spec(cell)
                if s.expiry == "30":
                    probs += [f"9.1 item 7: {p}" for p in expiry_pair_problems(
                        cell[:-3] + "_none", runs[run_key(d, arm, cell[:-3] + "_none")], x,
                        int(x["levers"].expiry_days))]
                rows += identity_rows(d, arm, cell, "9.1 items 5 and 7", probs, len(x["outs"]))
                if probs:
                    raise Refused(f"{d} {arm} {cell}: " + "; ".join(probs[:6]))
                x["tally"] = tally_of(x, d, arm, "off", cal)
                x["rec"] = None                          # the records checked and tallied; the counts kept
                runs[run_key(d, arm, cell)] = x
            log(f"checked: {d} {cell} (9.1 items 5 and 7)")
    keep_compact(runs)
    ref_guard = ref_gate_guard(inputs, designs)
    # (c) the gates
    gates: dict[tuple[str, str, bool], dict[str, Any]] = {}
    if gate:
        from extended import gate as XG

        if authorise_gate is not None:
            authorise_gate()
        for d in designs:
            for cell in cells:
                for twin in (False, True):
                    g = cell_gate(inputs, d, cell, twin)
                    kw = dict(g["kw"])
                    tally = CLGateTally(kw.get("path_hook"))
                    kw["path_hook"] = tally
                    df, _ = XG.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
                    gates[(d, cell, twin)] = {"df": df, "g": g, "tally": tally}
                log(f"gate: {d} {cell} (point, bound, zero-edge twin)")
    # (d) the oracles, the mechanics, the reading, the menu
    for k, r in runs.items():
        d, arm, cell, rname, var = k
        key = dict(design=d, arm=arm, cell=cell, mode="declared", response=rname)
        rows += PR.replay_oracle_rows(key, r["outs"])
        probs = replay_oracle_problems(cell, r, runs.get(run_key(d, arm, "ref")) if cell != "ref" else None)
        if probs:
            raise Refused("9.2: " + "; ".join(probs[:6]))
        rows.append(_row(section="oracle", part="replay", **key, measure="9.2 the levers' oracles", stat="holds",
                         value=1.0, n=len(r["outs"])))
    for (d, cell, twin), gx in gates.items():
        rows += gate_oracle_rows(dict(design=d, cell=cell, mode="declared", block="twin" if twin else "gate"), twin,
                                 gx["tally"])
    no_effect = _no_effect(runs)
    for d in designs:
        rows += PR.stream_rows(d, jobs[d]["verdict"], cal)
    for k, r in runs.items():
        d, arm, cell, rname, var = k
        if cell == "ref":
            continue
        key = dict(design=d, arm=arm, cell=cell, mode="declared", response=rname, base="ref")
        if k in no_effect:
            rows.append(_row(section="mechanics", part="no_effect", **key, block="all", measure=LR.LABEL_NO_EFFECT,
                             stat="identical_on_every_start", value=1.0, n=len(r["outs"])))
            continue
        rows += mechanics_rows(key, r, runs[run_key(d, arm, "ref")])
    log("oracles and mechanics: done")
    gate_frame, gate_guard = gate_table(gates, inputs, ref_guard)
    honesty: dict = {}
    rows += reading_rows(runs, honesty, no_effect, gate_guard)
    hon = PR.honesty_table(list(honesty), seed, honesty_reps)
    PR.label_rows([r for r in rows if r["part"] == "paired"], hon)
    rows += [_row(section="coverage", h=int(r.h), n=int(r.n_w), measure=r.shape, stat=st, value=float(getattr(r, st)),
                  note=f"shape {r.shape_index}; {honesty_reps} series; seed key [declared, 1, {r.shape_index}, {r.h}, "
                       f"{r.n_w}]") for r in hon.itertuples() for st in ("coverage", "miss_above", "miss_below")]
    reading = pd.DataFrame(label_house(rows), columns=list(PI.ROW_KEYS))
    menu = menu_table(reading, approved_limits, no_effect, solver_view, excuse_guard=excuse_guard)
    return {"reading": reading, "gate": gate_frame, "menu": menu, "honesty_seed": seed, "no_effect": sorted(no_effect),
            "runs": sorted(runs), "counts": {k: len(r["outs"]) for k, r in runs.items()},
            "calendars_checked": dict(CALENDARS)}


GATE_COLUMNS = (("growth_on_required_bankroll", "pf_growth_on_base_p50"), ("required_bankroll_p90", "pf_required_p90"),
                ("ruin_probability", "ruin_probability"))


def gate_entry(row: Mapping[str, Any], what: str) -> dict[str, float]:
    """A gate row's guard entries (M1), refused if a column is missing or not finite."""
    out: dict[str, float] = {}
    for name, col in GATE_COLUMNS:
        v = _f(row.get(col))
        if not math.isfinite(v):
            raise Refused(f"{what}: the gate row has no finite {col} for the guard row's {name}")
        out[name] = v
    return out


#: `ref`'s gate label (10.1 item 8 names "the gate at 0 %"; the registered row is at 0 %, the placement off)
REF_GATE_LABEL = "the gate at 0 %: the registered gate row, the placement off (9.1's identity)"


def ref_gate_guard(inputs: Any, designs: Sequence[str]) -> dict[tuple[str, str], dict[str, Any]]:
    """M2: `ref`'s guard entries from its registered gate row (0 %, the placement off, the bound shift) -- 9.1's
    identity, no gate rerun."""
    out = {}
    for d in designs:
        rows = inputs.base_gate_rows(d)
        if "lower_bound" not in rows:
            raise Refused(f"{d}: no registered gate row at the bound for ref's guard row")
        out[(d, "ref")] = {**gate_entry(rows["lower_bound"], f"{d} ref"), "_label": REF_GATE_LABEL}
    return out


def gate_table(gates: Mapping[tuple, Mapping[str, Any]], inputs: Any, ref_guard: Mapping[tuple, Mapping[str, Any]]
               ) -> tuple[pd.DataFrame, dict]:
    """The gates' file (10.1 item 9): each new cell's rows, its pairing with the base's registered paths (weakened, not
    biased, after a cell's first reactivation shifts the funded indices' streams), the levers' counts, and the guard
    entries (part `guard`, every cell and `ref`) that steps 4 and 5 read; and those entries keyed (design, cell)."""
    frames = []
    guard: dict[tuple[str, str], dict[str, Any]] = {k: dict(v) for k, v in ref_guard.items()}
    for (d, cell, twin), gx in gates.items():
        df = gx["df"].copy()
        df.insert(0, "design", d)
        df.insert(1, "cell", cell)
        df.insert(2, "twin", bool(twin))
        df.insert(3, "part", "row")
        frames.append(df)
        for (shift, p), c in gx["tally"].counts.items():
            frames.append(pd.DataFrame([{"design": d, "cell": cell, "twin": bool(twin), "part": "lever_counts",
                                         "shift": shift, "enforcement_p": p, **{k: float(v) for k, v in c.items()}}]))
        pair = inputs.gate_pairing_rows(d, cell, twin, gx["g"])
        if pair:
            frames.append(pd.DataFrame(pair).assign(twin=bool(twin), part="pairing",
                                                    pairing_note="paired with the registered paths; the pairing "
                                                                 "weakens after a reactivation shifts the funded "
                                                                 "indices' streams (not biased)"))
        if not twin:
            b = df[(df["shift"] == "lower_bound") & np.isclose(df["enforcement_p"].astype(float), 0.0)]
            if len(b) != 1:
                raise Refused(f"{d} {cell}: {len(b)} gate rows at the bound at 0 %, not one")
            guard[(d, cell)] = {**gate_entry(b.iloc[0].to_dict(), f"{d} {cell}"), "_label": "the gate at 0 %"}
    frames.append(pd.DataFrame([{"design": d, "cell": c, "part": "guard", "label": v["_label"],
                                 **{k: x for k, x in v.items() if not k.startswith("_")}}
                                for (d, c), v in guard.items()]))
    out = pd.concat(frames, ignore_index=True, sort=False)
    return out, guard


def gate_guard_from_file(df: pd.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    """M3: steps 4 and 5 read each cell's guard entries from step 3's gate file (its part `guard`). Refused unless
    each new cell's entries equal the same file's own gate row -- part `row`, not the twin, at the bound, at 0 % --
    column for column (`GATE_COLUMNS`, to 1e-12 relative; the red team's cycle-1 note 3). `ref`'s entries are its
    registered row (no gate of `ref` is run), so they have no row in the file to be held to."""
    g = df[df["part"].astype(str) == "guard"]
    rows = df[df["part"].astype(str) == "row"]
    if len(rows) and not {"twin", "shift", "enforcement_p"} <= set(df.columns):
        raise Refused("step 3's gate file: its gate rows lack twin, shift or enforcement_p")
    if len(rows):
        rows = rows[(rows["twin"].astype(str).str.lower() == "false") & (rows["shift"].astype(str) == "lower_bound")]
        rows = rows[np.isclose(pd.to_numeric(rows["enforcement_p"], errors="coerce").to_numpy(float), 0.0)]
    out = {}
    for r in g.to_dict("records"):
        d, cell = str(r["design"]), str(r["cell"])
        entry = gate_entry({c: r.get(n) for n, c in GATE_COLUMNS}, f"{d} {cell}")
        if cell != "ref":
            own = rows[(rows["design"].astype(str) == d) & (rows["cell"].astype(str) == cell)]
            if len(own) != 1:
                raise Refused(f"step 3's gate file: {d} {cell}'s guard entry has {len(own)} gate rows at the bound "
                              "at 0 % beside it, not one")
            mine = gate_entry(own.iloc[0].to_dict(), f"{d} {cell} (its gate row)")
            off = [n for n, _ in GATE_COLUMNS if abs(entry[n] - mine[n]) > 1e-12 * max(1.0, abs(mine[n]))]
            if off:
                raise Refused(f"step 3's gate file: {d} {cell}'s guard entries {off} differ from its own gate row")
        out[(d, cell)] = {**entry, "_label": f"{r['label']} (step 3's gate file)"}
    if not out:
        raise Refused("step 3's gate file holds no guard entries")
    return out


# ------------------------------------------------------------------------------------------------ steps 4 and 5


def beside_runs(stage: str) -> list[tuple[str, str, str]]:
    """Step 4's or step 5's runs after `ref`'s checks: (cell, response, variant) in step 3's order."""
    from extended import user_beside as B

    if stage == "ladder":
        return [(c, r, OPTIMISTIC) for c in STEP3_ORDER for r in LADDER]
    if stage == "ftp":
        ftp = [r.name for r in B.RESPONSES if r.kind == "ftp"]
        out = [(c, r, OPTIMISTIC) for c in STEP3_ORDER if c in FTP_CELLS for r in ftp]
        return out + [(c, r, CONSERVATIVE) for c in B2F_CELLS for r in ftp]
    raise KeyError(stage)


def beside_starts(n: int, starts: int | None, every: int | None) -> list[int]:
    """The starts a beside step runs: U1's choice (`user_journey.start_choice`), and with `every` (the synthetic window
    measurement's `--starts`) every `every`-th of them from the first."""
    import user_journey as UJ

    chosen = UJ.start_choice(int(n), starts)
    if every is None:
        return chosen
    if int(every) < 1:
        raise Refused(f"every n-th start: n is at least 1, got {every}")
    return chosen[::int(every)]


def run_beside(inputs: Any, stage: str, *, gate_guard: Mapping[tuple, Mapping[str, Any]],
               designs: Sequence[str] = DESIGNS, starts: int | None = None, workers: int = 1,
               honesty_reps: int = RD.HONESTY_SERIES, honesty_seed: int | None = None,
               cells: Sequence[str] | None = None, root: Path = ROOT, log: Callable[[str], None] = print,
               excuse_guard: bool = False, start_every: int | None = None) -> dict[str, Any]:
    """Section 15 step 4 (`ladder`: the denial ladder and the placement on) or step 5 (`ftp`: the ten Focused Trader
    models, then the Back2Funded cells' counted reading): `ref`'s checks against Q-44 first (9.1 item 6), then every
    cell in step 3's order, verdict arm; each read with the full guard row, its gate entry the cell's 0 % gate from step
    3's gate file (`gate_guard`, M3; refused for a cell it lacks), against `ref` under the same response; the beside
    menu by `menu_table`, refusing a P without its guard. Raises `Refused` at the first failed check."""
    from extended import user_beside as B
    import user_journey as UJ

    if start_every is not None and isinstance(inputs, PI.RealInputs):
        raise Refused("every n-th start is the synthetic window measurement's only (section 15's cost), never the "
                      "reading's")
    seed = declared_seed(HONESTY_ROLE, root) if honesty_seed is None else int(honesty_seed)
    jobs = {d: inputs.jobs(d)["verdict"] for d in designs}
    responses = list(LADDER) if stage == "ladder" else [r.name for r in B.RESPONSES if r.kind == "ftp"]
    todo = [t for t in beside_runs(stage) if cells is None or t[0] in cells]
    lack = sorted({(d, c) for d in designs for c in ("ref", *{t[0] for t in todo}) if (d, c) not in gate_guard})
    if lack:
        raise Refused(f"step 3's gate file lacks the guard entries of {lack[:4]} (M3)")
    runs: dict[tuple, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for d in designs:
        chosen = beside_starts(len(jobs[d]["blocks"]), starts, start_every)
        for rname in responses:
            x = replay_run(jobs[d], d, "verdict", "ref", rname, chosen, workers, record=False)
            probs = list(inputs.ladder_problems(d, rname, x["outs"]))
            tot = lever_totals(x["counts"])
            if any(tot.values()):
                probs.append(f"9.1 item 4 under {rname}: the options are not off in ref")
            rows += identity_rows(d, "verdict", "ref", "9.1 item 6", probs, len(x["outs"]), rname)
            if probs:
                raise Refused(f"{d} ref {rname}: " + "; ".join(probs[:6]))
            runs[run_key(d, "verdict", "ref", rname)] = x
        log(f"identity HOLDS: {d} ref beside under {stage} (9.1 item 6)")
    for d in designs:
        chosen = beside_starts(len(jobs[d]["blocks"]), starts, start_every)
        for cell, rname, var in todo:
            x = replay_run(jobs[d], d, "verdict", cell, rname, chosen, workers, record=False,
                           count_reactivations=(var == CONSERVATIVE))
            probs = replay_oracle_problems(cell, x, runs.get(run_key(d, "verdict", "ref", rname)))
            if probs:
                raise Refused("9.2 beside: " + "; ".join(probs[:6]))
            runs[run_key(d, "verdict", cell, rname, var)] = x
        log(f"beside: {d} {stage} done")
    keep_compact(runs)
    no_effect = _no_effect(runs)
    for k, r in runs.items():
        d, arm, cell, rname, var = k
        if cell != "ref" and k not in no_effect:
            rows += mechanics_rows_beside(dict(design=d, arm=arm, cell=cell, mode=var or "declared", response=rname,
                                               base="ref"), r, runs[run_key(d, arm, "ref", rname)])
    honesty: dict = {}
    rows += reading_rows(runs, honesty, no_effect, gate_guard)
    hon = PR.honesty_table(list(honesty), seed, honesty_reps)
    PR.label_rows([r for r in rows if r["part"] == "paired"], hon)
    for r in rows:
        if r["section"] != "identity":
            r["section"] = "ladder" if (stage == "ladder" and r["response"] != "rtp") else (
                "rtp" if stage == "ladder" else "ftp")
    if stage == "ftp":
        label_u6(rows)                                   # R2: U-6's label on every Back2Funded row, by its variant
    reading = pd.DataFrame(label_house(rows), columns=list(PI.ROW_KEYS))
    menu = menu_table(reading, (), no_effect, None, ftp_gap=True, excuse_guard=excuse_guard)
    return {"reading": reading, "menu": menu, "honesty_seed": seed, "no_effect": sorted(no_effect),
            "runs": sorted(runs), "counts": {k: len(r["outs"]) for k, r in runs.items()},
            "start_every": start_every}


def _ftp_window() -> int:
    from extended import user_beside as B

    return int(B.FTP_WINDOW)


def mechanics_rows_beside(key: dict[str, Any], run: Mapping[str, Any], base: Mapping[str, Any]) -> list[dict[str, Any]]:
    """10.1 item 8's per-model counts beside: purchases and reactivations a year (D-34's caveat, m5), the share of
    starts placed by the Focused Trader model and when, and the accounts it closed."""
    from propedge.research import user_journey as U

    out = []
    cs = list(run["counts"].values())
    k = dict(section="mechanics", part="mechanics", **key, block="all", n=len(cs), h=252)
    # the rates a year on the starts whose long replay is a year (as `mechanics_rows` reads them; before this cycle
    # every start's count was averaged, a shorter replay's too)
    recs = [x["rec"] for x in run["outs"]]
    year = [int(r["start_day"]) for r in recs if int(r["observed"]) >= int(U.HORIZON)]
    year_problems(recs, year, str(key["cell"]))
    cy = [run["counts"][d] for d in year if d in run["counts"]]
    for name in ("evaluations_bought", "reactivations"):
        out.append(_rk(k, measure=f"{name}_per_year", stat="cell", n=len(cy), note=PER_YEAR,
                        value=float(np.mean([c.get(name, 0) for c in cy])) if cy else NAN))
    out.append(_rk(k, measure="max_reactivations_in_21_sessions", stat="max",
                    value=float(max([rolling_max(c.get("reactivation_days") or (), _ftp_window()) for c in cs] or [0]))))
    placed = [float(x["response"].get("ftp_placed_day", NAN)) for x in run["outs"]]
    out.append(_rk(k, measure="share_starts_placed", stat="share",
                    value=float(np.mean([math.isfinite(v) for v in placed])) if placed else NAN))
    out.append(_rk(k, measure="placement_session", stat="median", value=_q([v for v in placed if math.isfinite(v)],
                                                                              0.5)))
    return out


def adapter_provenance(root: Path = ROOT, strict: bool = True) -> dict[str, Any]:
    """The commit run and each adapter file's blob id there; refused (`strict`) if any is changed in the tree."""
    def git(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()

    out = {"commit": git("rev-parse", "HEAD"), "blobs": {}}
    for rel in ADAPTER_FILES:
        out["blobs"][rel] = git("rev-parse", f"HEAD:{rel}") or None
    dirty = git("status", "--porcelain", "--", *ADAPTER_FILES)
    if dirty and strict:
        raise Refused(f"the adapter files are changed in the tree: {dirty[:200]}")
    out["changed_in_tree"] = dirty.splitlines() if dirty else []
    return out


__all__ = ["DECLARATION", "PREREG_ID", "PIN_ROW", "PURPOSES", "STAGE_PURPOSE", "DESIGNS", "ARMS", "B2F_CELLS",
           "INV_CELLS", "HOUSE_CELLS", "NAF_CELLS", "NEW_CELLS", "STEP3_ORDER", "INV_ABOVE", "LADDER", "FTP_CELLS",
           "Refused", "CellSpec", "spec", "cell_levers", "seat_limit_problems", "CLInputs", "cell_gate", "run_key",
           "replay_run", "lever_totals", "bind_day", "before_binding_problems", "expiry_pair_problems",
           "replay_oracle_problems", "CLGateTally", "gate_oracle_rows", "mechanics_rows", "guard_values", "guard_rows",
           "frontier_rows", "s6_rows", "evenness_rows", "diverge_rows", "comparisons", "reading_rows", "menu_table",
           "check_menu", "declared_seed", "run_scorecard", "gate_table", "beside_runs", "run_beside",
           "adapter_provenance", "GUARD_COLUMNS", "GATE_GUARD", "GATE_COLUMNS", "gate_entry", "ref_gate_guard",
           "gate_guard_from_file", "label_house", "solver_view_text", "solver_view_frame", "keep_compact", "tally_of",
           "mechanics_rows_beside", "guard_values_n", "PER_YEAR", "year_problems", "U6_LABELS", "u6_label", "label_u6",
           "excused_names", "solver_view_problems", "fit_commit_problem", "REF_GATE_LABEL", "beside_starts"]
