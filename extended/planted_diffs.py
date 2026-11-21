"""Q-196: the exact-run difference comparator shown to fire on real paths, so that Q-172's zero means something (the
Q-172 audit's caveat C2, `docs/audits/Q-172_exact_run_diffs_2026-11-20.md`). A check, like an identity: it plants
differences in the engine's input on a few declared search-year starts, runs them through the same runner Q-172 ran
(`user_beside.run_starts(..., journey=True, journey_block="search")`, whose `_task` calls the vendored
`user_journey._one_start` -- the comparator: the event days up to h of the exact h-session run against the long
run's), and asserts that each planted difference is reported at its start and at exactly its horizons, and that the
unperturbed control reports none. It writes no file; `scripts/planted_diffs.py` runs it on P-14's point arm and exits
non-zero if any planted difference is missed.

    from extended import planted_diffs as PD
    report = PD.run_check(job, "p14", "point")      # job: user_beside's single-firm job, search-year dates only
    report["failures"], report["cannot"]            # both empty: every plant reported where it was planted

Every choice below is fixed here, before any run; nothing is drawn (the runs' seeds are the runner's own,
`user_beside.start_seed`, and a replay draws nothing else).

**The declared starts** (`declared_starts`, from Q-172's own `exact_run_diffs.choose_starts(n)` of a job of n search
sessions): three of the control group -- its first, its middle (`len // 2`) and its last -- and three of the cut
group, n - 252, n - 160 and n - 100 (`CUT_OFFSETS`; the first uncut, the other two cut at the job's end, checked at
four and three horizons). Six starts; at n = 1034 (the search cut's P-14 job) they are 0, 399, 777, 782, 874 and 934.

**The responses**: Q-172's own, `off` and `denial_25` (`RESPONSES`). Every plan runs under each.

**The control**: the declared starts run unperturbed; every start must report no difference, its checked horizons
must be the runner's rule's (h < L, `exact_run_diffs.expected_checked`), and `exact_run_diffs.count_rows` must count
zero. Its records also give each start's **first event day** d (`first_event`: the least of its pass, funded-activation
and pay days, all within its long run of L sessions) -- read inside the check to place the plants, never printed.

**The plants** (`KINDS`; `plans` makes them from the control; each run alone, on one start, under `Planter`, which
replaces `user_beside.replay` for the call and perturbs exactly the one replay the plan names):

| kind | the replay perturbed | the perturbation | expected `differs` |
|---|---|---|---|
| `blank_exact` | the exact run at hp | sessions 0 .. min(d, hp - 1) emptied (no trade) | {hp} |
| `stops_exact` | the exact run at hp | every trade of sessions 0 .. min(d, hp - 1) closed at its full stop | {hp} |
| `blank_long` | the long run | sessions 0 .. min(d, L - 1) emptied | {h checked : h >= d} |
| `shift_exact` | the exact run at hmax | the run started one session later: sessions s + 1 .. s + hmax | the oracle's |
| `late_long` | the long run | sessions hmax + 1 .. L - 1 emptied | {} |

hp is the least checked horizon at or after d (`plant_horizon`); hmax the largest checked horizon. **Why the first
three must fire:** an event (a pass, and so an activation or a payout) needs profit, and with no trade -- or only
losses -- in every session up to and including d, no account can have made any by day d, so the perturbed run holds
no event on or before d while the unperturbed one holds d (whether day d is read as session d or as the close after
session d - 1, the emptied span covers it). At the horizons not perturbed the runs are the control's, which reported
nothing; for `blank_long` at h < d neither run holds an event up to h. **The assumption under `stops_exact`, declared:**
a full stop (-1 R at every carried target, the pnl minus its risk, the MAE its risk) stays a loss after the engine's
fee re-pricing (D-324: it adds back at most the log's own priced-in fee, far below a trade's risk). `blank_exact` and
`blank_long` rest on no such assumption. **`shift_exact`** ("move one start by one session") is not forced to differ:
its expectation is computed by an oracle outside the comparator -- the planted and long replays captured by the
planter, their event days (`customer_journey.single_events`) read up to hmax by this module's own code
(`events_upto`), not the vendored `events_upto` -- and the comparator must agree with it, either way. **`late_long`**
is the specificity check: a perturbation after the last horizon compared must not be reported (causality at h).
A start whose long run holds no event up to its largest checked horizon carries only `shift_exact` and `late_long`.

**What each plan asserts** (`plan_problems`): the planter applied exactly its one perturbation to the start's own
slice of the job (every replayed block the job's own object, by identity, before the perturbation); the start's
checked horizons the control's; `differs` equal to the expectation; `count_rows` on the start's output counting one
differing start at each expected horizon of the start's group and none elsewhere (its classification of the
difference refusing nothing); the engine's payout, cash and fee checks and the record check clean.

**The requirement for power** (`cannot`): under each response at least `MIN_FORCED` starts must carry the forced
plants, at least one in each group; otherwise the check cannot show the comparator firing and says so (the script's
exit 6), distinct from a plant missed (exit 1).

**Dates** (`date_problems`, refused before anything runs): every date of the job on or before 2023-12-29 (E-208's
search years' last session), none on or after 2026-07-17 (the confirmation window, said separately), and every
session a plan replays -- the shifted run's last among them -- inside the job's search block.

This module imports no engine at import time; `run_check` needs the vendored tree on `sys.path`
(`extended.use_vendored_stage2`) and `workers` 1 (the planter replaces a function in this process).
"""
from __future__ import annotations

import contextlib
import dataclasses
import io
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from extended import exact_run_diffs as X

TASK = "Q-196"
#: E-208: the search years' last session; nothing after it is replayed
LAST_DAY = date(2023, 12, 29)
#: the confirmation window's first day: never read
CONFIRMATION_START = date(2026, 7, 17)
#: the cut group's declared starts, as offsets from the job's end (n - k)
CUT_OFFSETS = (252, 160, 100)
#: the control group's declared starts, by position in its list
CONTROL_POSITIONS = ("first", "middle", "last")
RESPONSES = X.RESPONSES
FORCED = ("blank_exact", "stops_exact", "blank_long")
PREDICTED = ("shift_exact",)
SPECIFIC = ("late_long",)
KINDS = FORCED + PREDICTED + SPECIFIC
#: under each response, at least this many starts carry the forced plants (one or more in each group)
MIN_FORCED = 3


class PlantRefused(ValueError):
    """A date past the search years or in the confirmation window, or a plan the runner cannot make."""


# ------------------------------------------------------------------------------------------------ dates and starts


def _day(x: Any) -> date:
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x)[:10])


def date_problems(dates: Sequence[Any], spans: Sequence[tuple[int, int]] = ()) -> list[str]:
    """Why a job's dates, or the sessions `spans` (first index, last index, inclusive) a plan replays, may not be read:
    a date past 2023-12-29, a date on or after 2026-07-17, a span outside the job."""
    out = []
    ds = [_day(d) for d in dates]
    conf = [d for d in ds if d >= CONFIRMATION_START]
    if conf:
        out.append(f"{len(conf)} date(s) in the confirmation window (from {CONFIRMATION_START}; first {conf[0]})")
    late = [d for d in ds if d > LAST_DAY]
    if late:
        out.append(f"{len(late)} date(s) past {LAST_DAY} (first {late[0]})")
    for a, b in spans:
        if not (0 <= int(a) <= int(b) < len(ds)):
            out.append(f"sessions {a} .. {b} lie outside the job's {len(ds)} sessions")
        elif ds[int(b)] > LAST_DAY:
            out.append(f"sessions {a} .. {b} reach {ds[int(b)]}, past {LAST_DAY}")
    return out


def refuse_dates(dates: Sequence[Any], spans: Sequence[tuple[int, int]] = (), what: str = "the job") -> None:
    bad = date_problems(dates, spans)
    if bad:
        raise PlantRefused(f"REFUSED ({TASK}): {what}: " + "; ".join(bad))


def declared_starts(n: int) -> dict[int, str]:
    """{start: group}: the control group's first, middle and last start, and the cut group's n - 252, n - 160 and
    n - 100 (the module's docstring), all from `exact_run_diffs.choose_starts(n)`."""
    groups = X.choose_starts(n)
    control = [s for s, g in groups.items() if g == "control"]
    pos = {"first": 0, "middle": len(control) // 2, "last": len(control) - 1}
    out = {control[pos[p]]: "control" for p in CONTROL_POSITIONS}
    for k in CUT_OFFSETS:
        s = int(n) - int(k)
        if groups.get(s) != "cut":
            raise PlantRefused(f"REFUSED ({TASK}): start n - {k} = {s} is not a cut start of a job of {n}")
        out[s] = "cut"
    if len(out) != len(CONTROL_POSITIONS) + len(CUT_OFFSETS):
        raise PlantRefused(f"REFUSED ({TASK}): a job of {n} sessions has too few control starts for three")
    return dict(sorted(out.items()))


def long_length(s: int, n: int) -> int:
    """A search start's long-run length in a job of search sessions only: min(252, n - s)."""
    return int(min(X.LONG, int(n) - int(s)))


# ------------------------------------------------------------------------------------------------ the plans


def first_event(rec: Mapping[str, Any]) -> int | None:
    """The least of a record's pass, funded-activation and pay days, or None when it holds none."""
    days = [int(d) for k in ("pass_days", "funded_days", "pay_days") for d in rec[k]]
    return min(days) if days else None


def plant_horizon(d: int | None, checked: Sequence[int]) -> int | None:
    """The least checked horizon at or after the first event day d (None: no event, or none checked that late)."""
    if d is None:
        return None
    hs = [int(h) for h in checked if int(h) >= int(d)]
    return min(hs) if hs else None


@dataclass(frozen=True)
class Plan:
    """One planted perturbation: `kind` on start `s` (its `group`), on the replay `target` -- the exact run of `length`
    sessions, or the long run (`length` its L) -- over the sessions `span` (first, last; inclusive, of the replay);
    `expected` the horizons the comparator must report (None: the oracle's, `shift_exact`)."""

    kind: str
    s: int
    group: str
    target: str                      # "exact" | "long"
    length: int
    span: tuple[int, int]
    expected: tuple[int, ...] | None
    checked: tuple[int, ...] = field(default=())

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def plans_for(s: int, group: str, n: int, checked: Sequence[int], d: int | None) -> list[Plan]:
    """A start's plans (the module's table), from its checked horizons and its first event day d."""
    L = long_length(s, n)
    ch = tuple(sorted(int(h) for h in checked))
    if list(ch) != X.expected_checked(s, n):
        raise PlantRefused(f"REFUSED ({TASK}): start {s} checked at {list(ch)}, not the runner's rule's")
    out: list[Plan] = []
    if not ch:
        return out
    hp = plant_horizon(d, ch)
    if hp is not None:
        out.append(Plan("blank_exact", s, group, "exact", hp, (0, min(int(d), hp - 1)), (hp,), ch))
        out.append(Plan("stops_exact", s, group, "exact", hp, (0, min(int(d), hp - 1)), (hp,), ch))
        out.append(Plan("blank_long", s, group, "long", L, (0, min(int(d), L - 1)),
                        tuple(h for h in ch if h >= int(d)), ch))
    hmax = max(ch)
    out.append(Plan("shift_exact", s, group, "exact", hmax, (0, hmax - 1), None, ch))
    if hmax + 1 <= L - 1:
        out.append(Plan("late_long", s, group, "long", L, (hmax + 1, L - 1), (), ch))
    return out


def forced_starts(plans: Sequence[Plan]) -> dict[str, set[int]]:
    """{group: the starts carrying the forced plans}."""
    out: dict[str, set[int]] = {g: set() for g in X.GROUPS}
    for p in plans:
        if p.kind in FORCED:
            out[p.group].add(p.s)
    return out


def cannot_problems(plans: Sequence[Plan], response: str) -> list[str]:
    """Why the plans cannot show the comparator firing under `response`: fewer than `MIN_FORCED` starts carrying the
    forced plants, or a group without one."""
    f = forced_starts(plans)
    out = []
    total = sum(len(v) for v in f.values())
    if total < MIN_FORCED:
        out.append(f"{response}: {total} start(s) carry the forced plants, fewer than {MIN_FORCED}")
    for g in X.GROUPS:
        if not f[g]:
            out.append(f"{response}: no {g} start carries the forced plants")
    return out


# ------------------------------------------------------------------------------------------------ the perturbations


def _fields(b: Any) -> list[str]:
    if not dataclasses.is_dataclass(b) or isinstance(b, type):
        raise PlantRefused(f"REFUSED ({TASK}): a day block that is not a dataclass ({type(b).__name__})")
    return [f.name for f in dataclasses.fields(b)]


def blank_block(b: Any) -> Any:
    """The day block with no trade: every per-trade array cut to length 0 (a dict of them likewise), every per-trade
    tuple empty, nothing else changed."""
    kw = {}
    for name in _fields(b):
        v = getattr(b, name)
        if isinstance(v, np.ndarray):
            kw[name] = v[:0].copy()
        elif isinstance(v, dict):
            kw[name] = {k: np.asarray(x)[:0].copy() for k, x in v.items()}
        elif isinstance(v, tuple):
            kw[name] = ()
    out = dataclasses.replace(b, **kw)
    if len(out) != 0:
        raise PlantRefused(f"REFUSED ({TASK}): a blanked block holds {len(out)} trades")
    return out


def stops_block(b: Any) -> Any:
    """The day block with every trade closed at its full stop: pnl minus its risk, -1 R at every carried target (a
    target not permitted, NaN, stays NaN), the MAE its risk (1 R), every exit reason `stop`; nothing else changed."""
    names = _fields(b)
    risked = np.asarray(b.risked, float)
    pnl = np.asarray(b.pnl, float)
    kw: dict[str, Any] = {"pnl": np.where(np.isfinite(pnl), -risked, pnl)}
    if "exit_reasons" in names and b.exit_reasons is not None:
        kw["exit_reasons"] = tuple("stop" for _ in b.exit_reasons)
    if getattr(b, "mae", None) is not None:
        m = np.asarray(b.mae, float)
        kw["mae"] = np.where(np.isfinite(m), risked, m)
    if getattr(b, "r_by_rr", None) is not None:
        kw["r_by_rr"] = {k: np.where(np.isfinite(np.asarray(v, float)), -1.0, np.asarray(v, float))
                         for k, v in b.r_by_rr.items()}
    if getattr(b, "mae_by_rr", None) is not None:
        kw["mae_by_rr"] = {k: np.where(np.isfinite(np.asarray(v, float)), 1.0, np.asarray(v, float))
                           for k, v in b.mae_by_rr.items()}
    return dataclasses.replace(b, **kw)


PERTURB: dict[str, Callable[[Any], Any]] = {"blank_exact": blank_block, "stops_exact": stops_block,
                                            "blank_long": blank_block, "late_long": blank_block}


def perturbed(plan: Plan, job_blocks: Sequence[Any], given: Sequence[Any]) -> list[Any]:
    """The replay's blocks under `plan`, from the blocks the runner handed it (`given`, the start's own slice)."""
    s = int(plan.s)
    if plan.kind == "shift_exact":
        out = list(job_blocks[s + 1:s + 1 + plan.length])
        if len(out) != plan.length:
            raise PlantRefused(f"REFUSED ({TASK}): start {s} moved by one session runs past the job")
        return out
    a, b = plan.span
    f = PERTURB[plan.kind]
    return [f(x) if a <= i <= b else x for i, x in enumerate(given)]


class Planter:
    """`user_beside.replay` replaced, for one start's run, by one that perturbs the replay `plan` names and hands
    every other replay through unchanged; it refuses a replay that is not the start's (its seed, its slice of the job's
    blocks by identity) and records what it did (`applied`, and the replays' results for the oracle)."""

    def __init__(self, B: Any, job: Mapping[str, Any], plan: Plan, perturb: Callable | None = None):
        self.B, self.job, self.plan = B, job, plan
        self.perturb = perturb or perturbed
        self.seed = int(B.start_seed(plan.s))
        self.applied = 0
        self.calls: list[int] = []
        self.planted_run: Any = None
        self.long_run: Any = None
        self._orig: Any = None

    def _replay(self, blocks, args, path_seed):
        p, jb = self.plan, self.job["blocks"]
        s, h = int(p.s), len(blocks)
        if int(path_seed) != self.seed:
            raise PlantRefused(f"REFUSED ({TASK}): a replay of another start (seed {path_seed}) under start {s}'s plan")
        if not all(x is y for x, y in zip(blocks, jb[s:s + h])) or s + h > len(jb):
            raise PlantRefused(f"REFUSED ({TASK}): a replay of {h} sessions that is not start {s}'s slice of the job")
        self.calls.append(h)
        is_long = h == long_length(s, len(jb))
        hit = (p.target == "long" and is_long) or (p.target == "exact" and not is_long and h == p.length)
        if hit:
            self.applied += 1
            blocks = self.perturb(p, jb, blocks)
            if len(blocks) != h:
                raise PlantRefused(f"REFUSED ({TASK}): a perturbation changed the run's length")
        run = self._orig(blocks, args, path_seed)
        if hit:
            self.planted_run = run
        if is_long:
            self.long_run = run
        return run

    def __enter__(self) -> "Planter":
        self._orig = self.B.replay
        self.B.replay = self._replay
        return self

    def __exit__(self, *exc) -> None:
        self.B.replay = self._orig


# ------------------------------------------------------------------------------------------------ the oracle and checks


def events_upto(ev: Sequence[Any], h: int) -> tuple[tuple[int, ...], ...]:
    """This module's own reading of a run's event days up to h, from `customer_journey.single_events`' tuple (cash,
    initial, pass days, funded days, pay days)."""
    return tuple(tuple(sorted(int(d) for d in days if int(d) <= int(h))) for days in ev[2:5])


def oracle_differs(ev_planted: Sequence[Any], ev_long: Sequence[Any], h: int) -> tuple[int, ...]:
    return (int(h),) if events_upto(ev_planted, h) != events_upto(ev_long, h) else ()


def run_problems(o: Mapping[str, Any], what: str) -> list[str]:
    out = [f"{what}: the engine's {k} check fails" for k in ("pay", "cash", "fee") if int(o[f"{k}_bad"])]
    if o.get("record_same") is not True:
        out.append(f"{what}: _one_start's record is not the adapter's")
    return out


def count_problems(o: Mapping[str, Any], plan: Plan, n: int, expected: Sequence[int], design: str, arm: str,
                   response: str) -> list[str]:
    """Q-172's counting layer on the plan's one output: one differing start at each expected horizon of its group,
    none elsewhere; a refusal of the count is a problem."""
    what = f"{response} start {plan.s} {plan.kind}"
    try:
        rows = X.count_rows([o], design=design, arm=arm, response=response, n=n, groups={plan.s: plan.group})
    except ValueError as exc:
        return [f"{what}: the count refused: {exc}"]
    got = {(r["group"], int(r["horizon"])): int(r["differing"]) for r in rows if r["section"] == "checked"}
    want = {(g, h): int(g == plan.group and h in set(expected)) for g in X.GROUPS for h in X.HORIZONS}
    return [] if got == want else [f"{what}: counted {sorted(k for k, v in got.items() if v)}, planted "
                                   f"{sorted(k for k, v in want.items() if v)}"]


def plan_problems(o: Mapping[str, Any], plan: Plan, planter: Planter, n: int, design: str, arm: str, response: str,
                  ev_fn: Callable | None = None) -> tuple[list[str], tuple[int, ...]]:
    """(problems, the expected horizons) of one planted run's output (the module's docstring)."""
    what = f"{response} start {plan.s} {plan.kind}"
    out = []
    if int(o["rec"]["start_day"]) != int(plan.s):
        out.append(f"{what}: the output is start {o['rec']['start_day']}'s")
    if planter.applied != 1:
        out.append(f"{what}: the perturbation applied {planter.applied} times, not once")
    if sorted(int(h) for h in o["checked"]) != list(plan.checked):
        out.append(f"{what}: checked at {sorted(o['checked'])}, the control at {list(plan.checked)}")
    expected = plan.expected
    if expected is None:
        if planter.planted_run is None or planter.long_run is None or ev_fn is None:
            out.append(f"{what}: the oracle has no runs")
            expected = ()
        else:
            expected = oracle_differs(ev_fn(planter.planted_run), ev_fn(planter.long_run), plan.length)
    got = tuple(sorted(int(h) for h in o["differs"]))
    if got != tuple(sorted(expected)):
        out.append(f"{what}: reported {list(got)}, planted {list(expected)}")
    out += count_problems(o, plan, n, expected, design, arm, response)
    out += run_problems(o, what)
    return out, tuple(expected)


# ------------------------------------------------------------------------------------------------ the check


def _quiet(f: Callable, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def run_check(job: Mapping[str, Any], design: str, arm: str, responses: Sequence[str] = RESPONSES,
              workers: int = 1, perturb: Callable | None = None) -> dict[str, Any]:
    """The check on one job (the module's docstring): {"starts", "control", "plants", "failures", "cannot"}, the
    plants' lines {response, start, group, kind, expected count, held} -- no event day, no horizon, no measure.
    Refused (`PlantRefused`) before any run for a date past the search years or in the confirmation window, or
    `workers` other than 1. `perturb` replaces `perturbed` (the tests' mutants only)."""
    import customer_journey as CJ

    from extended import user_beside as B

    if int(workers) != 1:
        raise PlantRefused(f"REFUSED ({TASK}): the planter replaces a function in this process; workers must be 1")
    dates = list(job["dates"])
    refuse_dates(dates, what=f"{design} {arm}'s job")
    n = len(dates)
    starts = declared_starts(n)
    refuse_dates(dates, [(s, s + long_length(s, n) - 1) for s in starts], what="the declared starts' long runs")
    report: dict[str, Any] = {"task": TASK, "design": design, "arm": arm, "n_sessions": n,
                              "starts": dict(starts), "control": {}, "plants": [], "failures": [], "cannot": []}
    for rname in responses:
        resp = B.BY_NAME[rname]
        ctrl = _quiet(B.run_starts, design, arm, resp, job, list(starts), 1, journey=True, journey_block="search")
        bad = []
        for o in ctrl:
            bad += run_problems(o, f"{rname} control start {o['rec']['start_day']}")
            if o["differs"]:
                bad.append(f"{rname} control start {o['rec']['start_day']}: reports {sorted(o['differs'])} unplanted")
        try:
            rows = X.count_rows(ctrl, design=design, arm=arm, response=rname, n=n, groups=starts)
            total = sum(int(r["differing"]) for r in rows if r["section"] == "checked")
            if total:
                bad.append(f"{rname} control: the count holds {total} differing")
        except ValueError as exc:
            bad.append(f"{rname} control: the count refused: {exc}")
        report["control"][rname] = {"starts": len(ctrl), "held": not bad}
        report["failures"] += bad
        if bad:
            continue
        plans = []
        for o in ctrl:
            s = int(o["rec"]["start_day"])
            plans += plans_for(s, starts[s], n, o["checked"], first_event(o["rec"]))
        report["cannot"] += cannot_problems(plans, rname)
        refuse_dates(dates, [(p.s, p.s + p.length) if p.kind == "shift_exact" else (p.s, p.s + p.length - 1)
                             for p in plans], what=f"{rname}'s plans")
        for p in plans:
            with Planter(B, job, p, perturb) as pl:
                outs = _quiet(B.run_starts, design, arm, resp, job, [p.s], 1, journey=True, journey_block="search")
            if len(outs) != 1:
                probs, exp = [f"{rname} start {p.s} {p.kind}: {len(outs)} outputs"], ()
            else:
                probs, exp = plan_problems(outs[0], p, pl, n, design, arm, rname, CJ.single_events)
            report["failures"] += probs
            report["plants"].append({"response": rname, "start": p.s, "group": p.group, "kind": p.kind,
                                     "expected": len(exp), "held": not probs})
    return report


def summary_lines(report: Mapping[str, Any]) -> list[str]:
    """The printable summary: per response and kind, the plants made, the planted differences expected and whether
    every one held -- counts only."""
    out = []
    for rname, c in report["control"].items():
        out.append(f"  {rname} control: {c['starts']} starts unperturbed -- {'HELD (0 reported)' if c['held'] else 'FAILED'}")
        for k in KINDS:
            ps = [p for p in report["plants"] if p["response"] == rname and p["kind"] == k]
            if not ps:
                continue
            ok = all(p["held"] for p in ps)
            out.append(f"  {rname} {k}: {len(ps)} plants on {len({p['start'] for p in ps})} starts, "
                       f"{sum(p['expected'] for p in ps)} differing horizon(s) expected -- {'HELD' if ok else 'FAILED'}")
    return out


def verdict(report: Mapping[str, Any]) -> int:
    """0 every plant reported where planted and the control zero; 1 a failure; 6 the plants cannot show power."""
    if report["failures"]:
        return 1
    if report["cannot"]:
        return 6
    return 0


__all__ = ["TASK", "LAST_DAY", "CONFIRMATION_START", "CUT_OFFSETS", "CONTROL_POSITIONS", "RESPONSES", "FORCED",
           "PREDICTED", "SPECIFIC", "KINDS", "MIN_FORCED", "PlantRefused", "date_problems", "refuse_dates",
           "declared_starts", "long_length", "first_event", "plant_horizon", "Plan", "plans_for", "forced_starts",
           "cannot_problems", "blank_block", "stops_block", "perturbed", "Planter", "events_upto", "oracle_differs",
           "run_problems", "count_problems", "plan_problems", "run_check", "summary_lines", "verdict"]
