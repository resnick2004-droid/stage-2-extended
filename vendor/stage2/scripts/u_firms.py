"""EXPLORATORY (D-643 as D-644 widens it, program U's family 5): the JOINT BASES of `scripts/u_family.py` -- P-16's
trades through the joint two-firm engine, Topstep's five seats plus 1, 2 or 5 Lucid seats, the Lucid firm from day 0
or opened only when the campaign's first payout has arrived, under one of three deals. A helper module of the family
runner: it has no `main`, starts no run and writes nothing; `u_family.py` builds, checks, replays, counts and writes.

**The bases** (`propedge.research.u_select.JOINT_BASES`, D-644 (5)'s order: for each K in 1, 2, 5, for each opening,
for each deal -- 18): `l<K>_day0` (5 + K from day 0; `l1_day0` is U1's `p16_5+1`, which it must equal start for
start), `l<K>_seq` (the Lucid firm opened at the first payout's arrival: the joint run's sequencing option,
`propedge.research.second_firm`, D-643 (2)), and each of those under `hedged` and `hedged_combines`
(`l<K>_<opening>_<deal>`). Each is a family cell itself -- no override, counted.

**The deal** (D-644 (2)) is `propedge.research.hypo_hedge`'s by import, none new: `unhedged` (each signal to one
account at one firm, never opposite to a position open at the other), `hedged` (the lead leg as unhedged and the other
firm's account in the lead's slot on the opposite side of the same event when it can take it, else the lead alone,
counted as unpaired) and `hedged_combines` (the pair only when both legs are evaluations). **The six unhedged cells
are eligible** (every row labelled `lucid_upper_bound`). **The twelve hedged cells are HYPOTHETICAL** -- cross-firm
hedging is prohibited at Topstep (13747047, 10296582) and Lucid (11404734), tier 1 -- labelled `hypothetical_hedge` on
every row with `u_select.HYPOTHETICAL_NOTE` (which says upper bound too), counted under `D-644:hypothetical_hedge`,
written with their scorecard at both arms and the share of signals paired (`deal_rows`), and REFUSED in the choice,
the judgement, every guard and the rows to beat (`gate_run` and `coin_jobs` here refuse one; `u_select`'s `choose`,
`judge` and `row_to_beat` and `u_family`'s `coin_guard` and `tables` do).

**Built as U1 builds `p16_5+1`** (`user_journey.build_joint`'s own calls; D-593's conventions by import):
`rc150_firm_split.inputs("lucid")` (P-16's cell by its registered content hash -- refused otherwise --, the opposite
side aligned one for one, P-16's engine arguments, Lucid's verified contract through `lucid_setup` with its two
unpriced fees at zero and the household rule's conservative reading), `arm_blocks` (the verdict arm at the 0.05 bound
through `mirror_shift` -- the cell shifted down, the opposite side mirrored --, the point arm as traded) and
`firm_setups(X, "rep", (5, K))` (each firm's seats and its budget floor(20 x seats / 5) in 21 sessions; Lucid's
household caps) -- the setup `rc150_firm_split`'s Lucid hedged cells ran on. A day-0 UNHEDGED cell's starts run
through U1's OWN task (`user_journey._joint_task`); every other cell's through `joint_starts`, that task's body with
the deal and the option passed (`joint_starts` unhedged without the option is that task, output for output; under a
hedge deal its 126-session journey rows are `rc150_firm_split._journey_task`'s -- both tested).

**Identities** (`u_family.py` settles them): the trades are the screen's row and P-16's registered content hash
(`rc_dev_test.trade_problems`); Lucid's price row verified, its household caps as D-575 read them and the cell inside
them, its open rows the two the upper bound waits for (`rules_problems`); the 5 + 0 cell through the joint engine (the
twin) equal to U1's `p16` start rows start for start; `l1_day0` equal to U1's `p16_5+1` start rows start for start;
for a sequenced cell of any deal, on every start -- its opening day is the twin's first payout day, a start that
never opened carries the twin's record, and an opened start's record before its opening day is the twin's
(`sequence_problems`: no pair exists before the opening); inside the joint run itself, on every opened path, the
first firm through the opening day is the first firm alone (`second_firm.run_sequenced` raises otherwise).

**Line (3)(iii)** (`gate_run`; an eligible cell's only): the joint engine's pooled call, D-593's own
(`rc150_added_lucid._paths_task` and `readings`: growth on the required bankroll at the bound and the point, the
required bankroll) with the campaign seed a parameter. First the DAY-0 call of the cell's seats at the screen's seed,
which at 500 paths must reproduce `results/rc150_added_lucid.csv`'s `5+K` rows (`added_row_problems`) -- the row on
record for `l1_day0`, `l2_day0` and `l5_day0`; a sequenced cell has no row on record, so the call reproduced first is
its day-0 sibling's (the same seats, the option absent) -- then the cell itself at the fresh seed.

**Line (3)(iv)** (`coin_inputs`; an eligible cell's only): under a coin sequence the cell's trades are re-dealt on
P-16's walk (`rc150_routing.coin_cell`), the opposite side by the same walk with every coin side negated and aligned
one for one (`rc150_firm_split.inputs`' construction, as `rc150_added_lucid.build_spans` builds a span's), and the
joint inputs rebuilt on them with that sequence's own bounds (`atlas_a3.bounds`, as `user_journey._rc_campaign` reads
a coin's) and day capacity (`rc150_added_lucid.span_inputs`: `rc150_firm_split.inputs`' construction on given
trades); at the registered coin the construction must rebuild the cell (`coin_problems`).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402

from propedge.research import hypo_hedge as hh  # noqa: E402
from propedge.research import second_firm as sf  # noqa: E402
from propedge.research import u_select as Sel  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402

DECISION = Sel.JOINT_DECISION
ARMS = U.ARMS
#: D-593's result: the day-0 cells' rows on record (the screen's seed, 500 paths), `5+k` for k Lucid seats
ADDED_FILE = "rc150_added_lucid.csv"
#: U1's configuration a joint base is built as, and the 5 + 0 twin's name
U1_CONFIG = "p16_5+1"
TWIN = "twin_5+0"
TWIN_EQUALS_U1 = "p16"
#: `--check --check-base <joint base>[,<joint base>...]`: each named base as one cell of the NULL family
CHECK_CELL = "check_joint"
#: the role of a sequenced cell's rows that read the second firm's opening: beside, never in the selection
OPENING_ROLE = ("joint base: the second firm's opening over each start's long replay (D-643 (2); beside; never in the "
                "selection)")
OPENING_MEASURE_ROLE = "beside"
#: the role of a joint cell's rows that read its deal (the share of signals paired): beside, never in the selection
DEAL_ROLE = ("joint base: the deal over each start's long replay -- the signals dealt as a pair and alone (D-644 "
             "(4); beside; never in the selection)")
DEAL_MEASURE_ROLE = "beside"
#: the role of a hypothetical cell's scorecard rows (the eligible cells' is the runner's "family cell")
HYPOTHETICAL_ROLE = ("hypothetical cell (hypothetical_hedge, D-644 (4)): its scorecard beside the eligible cells; "
                     "never chosen, judged, ranked, a row to beat or a candidate")
#: the task kind `dispatch` takes for itself; every other kind is U1's (`user_journey._dispatch`)
KIND = "joint_u"
UNHEDGED = Sel.JOINT_UNHEDGED
if (Sel.JOINT_OPENS_AT_FIRST_PAYOUT != sf.FIRST_PAYOUT_ARRIVAL or Sel.SEQUENCING_DECISION != sf.DECISION
        or tuple(Sel.JOINT_DEALS) != tuple(hh.MODES) or Sel.JOINT_UNHEDGED != hh.UNHEDGED
        or Sel.HYPOTHETICAL_LABEL != hh.TAG):
    raise RuntimeError("u_select's joint bases do not name the joint run's sequencing option, hypo_hedge's deals or "
                       "its label")


def seats_of(base: str) -> tuple[int, int]:
    return Sel.joint_seats(base)


def opens_of(base: str) -> str | None:
    """A joint base's sequencing option (`second_firm.check_second_firm_opens`): None from day 0."""
    return sf.check_second_firm_opens(Sel.JOINT_BASES[base]["opens"])


def deal_of(base: str) -> str:
    """A joint base's deal: one of `hypo_hedge.MODES`."""
    return Sel.joint_deal(base)


def variant_id_of(decision: str, family: str, base: str) -> str:
    """The id a joint cell is counted under (D-644 (3), (4)): the family's (`<row id>:u_<family>`) for an eligible
    cell, `<row id>:hypothetical_hedge` for a hypothetical one."""
    return Sel.hypothetical_id(decision) if Sel.hypothetical(base) else Sel.family_id(decision, family)


def added_cell(base: str) -> str:
    """The cell of `rc150_added_lucid.csv` a joint base's seats are (`5+k`)."""
    t, k = seats_of(base)
    return f"{t}+{k}"


def base_def(name: str, base: str | None = None) -> dict[str, Any]:
    """A joint cell in U1's configuration form (`user_journey.CONFIG_DEFS`' `p16_5+1` row: its cell, its label), named
    `name`, with no row on record of its own. `base`: the cell's joint base -- its label is the base's
    (`u_select.base_row_label`: `hypothetical_hedge` under a hedge deal); None: U1's own (`lucid_upper_bound`)."""
    import user_journey as UJ

    c = next(x for x in UJ.CONFIG_DEFS if x["config"] == U1_CONFIG)
    if c["label"] != Sel.UPPER_BOUND_LABEL:
        raise SystemExit(f"REFUSED ({DECISION}): U1's {U1_CONFIG} row is not labelled {Sel.UPPER_BOUND_LABEL}.")
    label = c["label"] if base is None else Sel.base_row_label(base)
    return {"config": name, "label": label, "cell": c["cell"], "slices": {}, "starts": None, "journey": {}}


# ------------------------------------------------------------------------------------------------ the inputs


def rules_problems(base: str) -> list[str]:
    """Line (3)(iii)'s "every firm rule it uses is verified" for a joint cell, beyond P-16's own (which lean on no
    unverified rule): Lucid's evaluation price row verified (`lucid_setup` refuses otherwise); its household caps as
    D-575 read them and the cell's Lucid seats inside them; and its open rows exactly the two the cell's upper bound
    waits for (`funded_monthly_fee`, `payout_fee`: charged at zero, which is what `lucid_upper_bound` says -- any
    other open row would be an unverified rule in use)."""
    from propedge.contract.lucid import OPEN_ROWS, STANDARD_40, lucid_price, lucid_terms
    from propedge.research import rc150_added_lucid as M

    out = []
    if not lucid_price(STANDARD_40).verified:
        out.append("Lucid's evaluation price is not verified in the vendored ledger")
    t = lucid_terms()
    caps = {"max_funded": int(t.max_funded), "eval_count_limit": int(t.eval_count_limit),
            "max_total_accounts": int(t.max_total_accounts)}
    if caps != M.LUCID_CAPS:
        out.append(f"Lucid's household caps read {caps}, not D-575's {M.LUCID_CAPS}")
    try:
        M.check_caps(((added_cell(base), seats_of(base)),), caps)
    except ValueError as exc:
        out.append(str(exc))
    if tuple(OPEN_ROWS) != ("funded_monthly_fee", "payout_fee"):
        out.append(f"Lucid's open rows are {tuple(OPEN_ROWS)}, not the two the upper bound waits for")
    return out


def inputs(rd: Path) -> dict[str, Any]:
    """The joint bases' shared inputs, by U1's builder calls (`user_journey.build_joint`): `rc150_firm_split.inputs`
    with Lucid as firm 1 (`X`; refused unless the cell's content hash is P-16's), both arms' doubled blocks
    (`arm_blocks`), the screen's seed -- and the trades' identity against their screen's row
    (`rc_dev_test.trade_problems`, as `user_journey.build_p16` reads P-16's) and whether every offered R resolves."""
    import atlas_a3 as A
    import customer_journey as CJ
    import rc150_dev_test as R
    import rc150_firm_split as F
    import rc_dev_test as D
    import rc_screen as S

    X = F.inputs(F.LUCID)
    trade_bad = D.trade_problems(Path(rd), X["b"], X["I"]["L"]["fcfg"], spec=R.SPEC)
    _, resolves = A.resolution(X["t"], X["b"]["rr_grid"])
    X.pop("b")                                  # the builder's four windows' cells: read above, not needed again (memory)
    return {"X": X, "I": X["I"], "days": list(X["days"]), "dates": list(X["days"]),
            "blocks": {arm: F.arm_blocks(X, CJ.SHIFT_OF[arm]) for arm in ARMS}, "seed": int(S.SEED),
            "trade_problems": trade_bad, "resolves": bool(resolves)}


def jobs(J: dict[str, Any], seats: tuple[int, ...], opens: str | None, deal: str = UNHEDGED, *,
         X: dict | None = None, blocks: dict | None = None) -> dict[str, dict]:
    """A joint cell's two arms as replay jobs, U1's joint job (`user_journey.build_joint`) plus the sequencing option
    and the deal: the arm's doubled blocks, the dates, each firm's replay setup (`rc150_firm_split.firm_setups(X,
    "rep", seats)`), the screen's seed, the dearest firm's evaluation fee. `X`, `blocks`: another coin sequence's
    inputs. A hedge deal needs two firms."""
    import rc150_firm_split as F

    if deal not in hh.MODES or (deal != UNHEDGED and len(tuple(seats)) != 2):
        raise ValueError(f"the deal is one of {hh.MODES} (a hedge deal with two firms), got {deal!r} on {seats!r}")
    X = J["X"] if X is None else X
    blocks = J["blocks"] if blocks is None else blocks
    setups = F.firm_setups(X, "rep", tuple(int(s) for s in seats))
    return {arm: {"engine": "joint", "blocks": blocks[arm], "dates": list(X["days"]), "setups": setups,
                  "seed": int(J["seed"]), "sub": max(float(x.path["subscription"]) for x in setups),
                  "opens": sf.check_second_firm_opens(opens), "deal": deal} for arm in blocks}


# ------------------------------------------------------------------------------------------------ the replay tasks


def joint_starts(task: tuple, opens: str | None, mode: str = UNHEDGED) -> list[dict[str, Any]]:
    """`user_journey._joint_task`'s body with the deal and the joint run's sequencing option passed: (config, arm,
    blocks, dates, setups, seed, starts) -> every start's output (`user_journey._one_start`: the long replay, the
    exact-length runs, the record and its ties to the engine's totals). `mode`: the deal (`hypo_hedge.MODES`; U1's
    task is `unhedged`). With `opens` each output also carries `second_firm` -- the long replay's record of the option
    (`JointPath.second_firm`: the first payout's arrival day at the first firm and the day the second firm opened,
    None when none arrived) and, for each exact-length run, the day it opened there. Under a hedge deal each output
    carries `deal` -- the long replay's deal counts (`HedgeRouter.counts`: signals offered, dealt as a pair, dealt
    alone, refused)."""
    import warnings

    import customer_journey as CJ
    import user_journey as UJ

    warnings.filterwarnings("ignore")
    config, arm, blocks, dates, setups, seed, starts = task
    sub = max(float(x.path["subscription"]) for x in setups)
    lags = [int(x.path["payout_lag_days"]) for x in setups]
    n = len(blocks)
    want = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        want.append((s, L))
        want += [(s, h) for h in U.EXACT if h < L]
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True) for s, h in want]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=mode, doubled=True, firm_setups=setups,
                       **({} if opens is None else {"second_firm_opens": opens}))
    got = dict(zip(want, jps))

    def pay(jp, obs):
        return U.payout_arrivals([(f.activation_day, lags[i], f.payout_days, f.payout_cash)
                                  for i, lp in enumerate(jp.paths) for f in lp.funded], obs)

    def totals(jp):
        return (sum(float(lp.path.total_fees) for lp in jp.paths), sum(float(lp.path.total_payouts) for lp in jp.paths))

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        exact = {h: got[(s, h)] for h in U.EXACT if h < L}
        out.append(UJ._one_start(config, arm, s, dates[s], got[(s, L)], exact, sub, CJ.joint_events, pay, totals,
                                 hh.slice_measures))
        if opens is not None:
            rec = got[(s, L)].second_firm
            out[-1]["second_firm"] = {"opens": rec["opens"], "first_payout_arrival": rec["first_payout_arrival"],
                                      "opened_on": rec["opened_on"], "observed": int(L),
                                      "exact": {str(int(h)): jp.second_firm["opened_on"] for h, jp in exact.items()}}
        if mode != UNHEDGED:
            c = got[(s, L)].router.counts()
            out[-1]["deal"] = {"mode": mode, **{k: int(c.get(k, 0)) for k in DEAL_KEYS}}
    return out


#: the deal counts a hedged cell's start carries (`hypo_hedge.HedgeRouter.counts`' keys)
DEAL_KEYS = ("signals", "hedged", "alone", "skipped_busy", "skipped_opposite", "skipped")


def joint_task(task: tuple) -> list[dict[str, Any]]:
    """(config, arm, blocks, dates, setups, seed, starts, opens, deal): a day-0 UNHEDGED cell's starts by U1's OWN
    task (`user_journey._joint_task`), any other cell's by `joint_starts`."""
    import user_journey as UJ

    *seven, opens, deal = task
    if deal not in hh.MODES:
        raise ValueError(f"the deal is one of {hh.MODES}, got {deal!r}")
    if opens is None and deal == UNHEDGED:
        return UJ._joint_task(tuple(seven))
    return joint_starts(tuple(seven), sf.check_second_firm_opens(opens), deal)


def dispatch(task: tuple) -> list[dict[str, Any]]:
    """A pool task: this module's kind (`KIND`) to `joint_task`, any other to U1's `_dispatch`."""
    import user_journey as UJ

    kind, t = task
    return joint_task(t) if kind == KIND else UJ._dispatch(task)


def tasks_of(job: dict[str, Any], name: str, arm: str, starts: list[int]) -> list[tuple]:
    """A joint job's starts as pool tasks, in chunks of U1's size: plain data (the setups pickle as U1's do)."""
    import user_journey as UJ

    chunks = [starts[j:j + UJ.CHUNK_STARTS] for j in range(0, len(starts), UJ.CHUNK_STARTS)]
    return [(KIND, (name, arm, job["blocks"], job["dates"], job["setups"], job["seed"], c, job.get("opens"),
                    job.get("deal", UNHEDGED))) for c in chunks]


def run_starts(job: dict[str, Any], name: str, arm: str, starts: list[int], workers: int) -> dict[str, Any]:
    """One joint cell and arm on the given starts across the guarded pool (`customer_journey._pool_run`), in start
    order -- `u_family.run_starts` for a joint job."""
    import customer_journey as CJ

    t0 = time.time()
    tasks = tasks_of(job, name, arm, starts)
    res = CJ._pool_run(tasks, dispatch, workers, f"{name} {arm}") if tasks else []
    return {"starts": [x for chunk in res for x in chunk], "seconds": time.time() - t0}


# ------------------------------------------------------------------------------------------------ a sequenced cell


def _blank(x: Any) -> bool:
    return x is None or (isinstance(x, float) and x != x)


def sequence_problems(outs: list[dict[str, Any]], twin: list[dict[str, Any]]) -> list[str]:
    """A sequenced cell's starts against the 5 + 0 twin's (P-16 alone through the joint engine, the same starts), from
    the records: (a) a start's opening day is the twin's first payout day -- the first firm's own first payout, which
    the second firm cannot have moved -- and it never opened where the twin has none; (b) a start that never opened
    carries the twin's record (`user_journey.record_problems`, its exact runs too); (c) an opened start's record BEFORE
    its opening day `a` is the twin's -- its pass, activation and payout days up to `a`, its first pass, first funded
    account and first payout (day and cash), the cash spent before each (the closes before `a`), and every month-end
    net and fee before `a`. A problem names the reading and the count, never a value."""
    by = {int(x["rec"]["start_day"]): x["rec"] for x in twin}
    if sorted(by) != sorted(int(x["rec"]["start_day"]) for x in outs):
        return [f"the starts differ ({len(outs)} against the twin's {len(by)})"]
    bad: dict[str, int] = {}

    def note(what: str) -> None:
        bad[what] = bad.get(what, 0) + 1

    for x in outs:
        r, t = x["rec"], by[int(x["rec"]["start_day"])]
        info = x.get("second_firm")
        if not info:
            note("no record of the option")
            continue
        a = info["opened_on"]
        fy = t["first_payout"]
        if _blank(a) != _blank(fy) or (not _blank(a) and int(a) != int(fy)) or a != info["first_payout_arrival"]:
            note("the opening day is not the twin's first payout day")
            continue
        if _blank(a):
            for k in U.record_problems(r, t) + ([] if sorted(r.get("alt") or {}) == sorted(t.get("alt") or {})
                                                else ["alt"]):
                note(f"never opened, {k} is not the twin's")
            continue
        a = int(a)
        if U.events_upto(r["pass_days"], r["funded_days"], r["pay_days"], a) != U.events_upto(
                t["pass_days"], t["funded_days"], t["pay_days"], a):
            note("the event days up to the opening day")
        for k in ("first_payout", "first_payout_cash", "spent_before_first_payout"):
            if not _money(r[k], t[k]):
                note(k)
        for k, first in (("first_pass", "first_pass"), ("first_funded", "first_funded"),
                         ("spent_before_first_pass", "first_pass")):
            before = not _blank(t[first]) and int(t[first]) <= a
            if before and not _money(r[k], t[k]):
                note(k)
        for m in range(1, U.MONTHS + 1):
            if U.MONTH * m < a:
                for k in ("net_month", "fees_month"):
                    if not _money(r[k][m - 1], t[k][m - 1]):
                        note(f"{k} before the opening day")
    return [f"{k}: {n} starts" for k, n in bad.items()]


def _money(x: Any, y: Any) -> bool:
    if _blank(x) or _blank(y):
        return _blank(x) and _blank(y)
    return abs(float(x) - float(y)) <= U.TOL


def opening_readings(outs: list[dict[str, Any]]) -> list[tuple[str, str, str, float, int]]:
    """A sequenced cell's own record of the second firm's opening over the starts' long replays, as (key, what, unit,
    value, n) -- beside the scorecard, never in the selection: the share of starts where the second firm ever opened,
    and the opening day's 50th and 90th percentiles over the starts where it did (numpy's linear percentile)."""
    recs = [x["second_firm"] for x in outs if x.get("second_firm")]
    days = [float(r["opened_on"]) for r in recs if not _blank(r["opened_on"])]
    nan = float("nan")
    return [("share_starts_opened", "the share of starts whose long replay saw the second firm open (the first "
             "payout arrived within it)", Sel.SHARE, float(len(days) / len(recs)) if recs else nan, len(recs)),
            ("opened_on_p50", "the session the second firm opened on, the median over the starts where it opened",
             Sel.SESSIONS, float(np.percentile(days, 50)) if days else nan, len(days)),
            ("opened_on_p90", "the session the second firm opened on, the 90th percentile over the starts where it "
             "opened", Sel.SESSIONS, float(np.percentile(days, 90)) if days else nan, len(days))]


def opening_rows(cell: str, base: str, arm: str, outs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A sequenced cell's opening record as section `cell` rows beside its scorecard (`OPENING_ROLE`; `measure` is
    `second_firm.<reading>`); no row for a day-0 cell."""
    if opens_of(base) is None:
        return []
    return [{"section": "cell", "cell": cell, "base": base, "role": OPENING_ROLE, "arm": arm, "block": "all",
             "measure": f"second_firm.{key}", "what": what, "direction": "", "unit": unit,
             "measure_role": OPENING_MEASURE_ROLE, "value": value, "n": int(n), "counted": False, "overrides": "{}",
             "label": Sel.base_row_label(base)} for key, what, unit, value, n in opening_readings(outs)]


def deal_readings(outs: list[dict[str, Any]]) -> list[tuple[str, str, str, float, int]]:
    """A hedged cell's own record of its deal over the starts' long replays, pooled over the starts, as (key, what,
    unit, value, n) -- beside the scorecard, never in the selection: of the signals DEALT (to at least one account),
    the share dealt as a pair and the share dealt to one account alone (they sum to one); and of the signals OFFERED,
    the share dealt as a pair (the rest dealt alone or refused: a firm busy, an opposite position open, no account
    able). `n`: the signals the share is of."""
    recs = [x["deal"] for x in outs if x.get("deal")]
    paired = sum(int(r["hedged"]) for r in recs)
    alone = sum(int(r["alone"]) for r in recs)
    offered = sum(int(r["signals"]) for r in recs)
    dealt = paired + alone
    nan = float("nan")
    return [("share_dealt_signals_paired", "of the signals dealt, the share dealt as a pair (the lead leg and the "
             "other firm's account in its slot on the opposite side)", Sel.SHARE, paired / dealt if dealt else nan,
             dealt),
            ("share_dealt_signals_unpaired", "of the signals dealt, the share dealt to one account alone (no partner: "
             "the other firm busy, no account in the slot, not both evaluations, or it could not take it -- and every "
             "signal before the second firm opened)", Sel.SHARE, alone / dealt if dealt else nan, dealt),
            ("share_offered_signals_paired", "of the signals offered, the share dealt as a pair", Sel.SHARE,
             paired / offered if offered else nan, offered)]


def deal_rows(cell: str, base: str, arm: str, outs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A hedged cell's deal record as section `cell` rows beside its scorecard (`DEAL_ROLE`; `measure` is
    `deal.<reading>`), labelled as the cell; no row for an unhedged cell (no signal is ever paired)."""
    if deal_of(base) == UNHEDGED:
        return []
    return [{"section": "cell", "cell": cell, "base": base, "role": DEAL_ROLE, "arm": arm, "block": "all",
             "measure": f"deal.{key}", "what": what, "direction": "", "unit": unit,
             "measure_role": DEAL_MEASURE_ROLE, "value": value, "n": int(n), "counted": False, "overrides": "{}",
             "label": Sel.base_row_label(base)} for key, what, unit, value, n in deal_readings(outs)]


# ------------------------------------------------------------------------------------------------ line (3)(iii)


def paths_task(task: tuple) -> list[dict]:
    """(cell, shift, blocks, setups, [(index, seed)], margin, horizon, opens) -> each path's pooled record: D-593's
    own task (`rc150_added_lucid._paths_task`) for a day-0 cell; for a sequenced cell the same record from the joint
    run with the option, plus the day the second firm opened on that path (`second_firm_opened_on`, -1: never)."""
    import warnings

    import rc150_added_lucid as AL

    from propedge.research import hypo_hedge as hh

    *seven, opens = task
    if opens is None:
        return AL._paths_task(tuple(seven))
    warnings.filterwarnings("ignore")
    cell, shift, blocks, setups, items, margin, horizon = seven
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=hh.UNHEDGED, doubled=True, firm_setups=setups,
                       second_firm_opens=sf.check_second_firm_opens(opens))
    out = []
    for (i, s), jp in zip(items, jps):
        r = hh.path_record(jp, margin=margin)
        r.update({"cell": cell, "shift": shift, "path": int(i), "seed": int(s)})
        hold = [lp.household for lp in jp.paths if lp.household]
        if hold:
            r["household_closed_on"] = int(max(int(h["closed_on"]) for h in hold))
        tps = []
        for lp in jp.paths:
            x = np.asarray(lp.path.trades_by_day, float)
            tps.append(float(x[1:].mean()) if len(x) > 1 else float("nan"))
        r["firm_trades_per_session"] = tps
        r["firm_payouts"] = [len(hh._pay_days(lp.path)) for lp in jp.paths]
        opened = jp.second_firm["opened_on"]
        r["second_firm_opened_on"] = -1 if opened is None else int(opened)
        out.append(r)
    return out


def path_tasks(X: dict, cell: str, seats: tuple[int, ...], blocks: list, shift: str, seed: int, n_paths: int,
               opens: str | None) -> list[tuple]:
    """`rc150_added_lucid.run_paths`' tasks with the campaign seed a parameter (its own is the screen's) and the
    option: the campaign setups of the seats (`firm_setups(X, "camp", seats)`), the engine's path seeds of `seed`."""
    import rc150_firm_split as F

    from propedge.campaign.lockstep import path_seeds

    setups = F.firm_setups(X, "camp", tuple(int(s) for s in seats))
    seeds = list(enumerate(path_seeds(int(seed), int(n_paths))))
    return [(cell, shift, blocks, setups, seeds[j:j + F.CHUNK_PATHS], X["margin"], X["horizon"],
             sf.check_second_firm_opens(opens)) for j in range(0, len(seeds), F.CHUNK_PATHS)]


def gate_run(X: dict, cell: str, seats: tuple[int, ...], opens: str | None, seed: int, n_paths: int, workers: int,
             *, deal: str = UNHEDGED) -> dict[str, Any]:
    """One pooled call of the joint engine on a cell at both shifts -- D-593's (`rc150_added_lucid.run_cell`: the
    arm's blocks, `_paths_task`, `readings`) with the campaign seed a parameter and the sequencing option: the growth
    on the required bankroll at the bound and at the point and the required bankroll at the bound (`u_family`'s
    `gate_reading` keys), and, for a sequenced cell, the paths at the bound on which the second firm opened. The gate
    floor is a guard: a cell under a hedge deal (`deal`; `hypothetical_hedge`) is REFUSED (D-644 (4))."""
    import rc150_added_lucid as AL
    import rc150_firm_split as F

    if deal != UNHEDGED:
        Sel.refuse_labelled([cell], [cell], "a guard (the gate floor)")

    read: dict[str, dict] = {}
    opened = None
    for shift in F.SHIFTS:
        tasks = path_tasks(X, cell, seats, F.arm_blocks(X, shift), shift, seed, n_paths, opens)
        recs = sorted((r for chunk in F._pool(tasks, paths_task, workers, f"{cell} {shift}") for r in chunk),
                      key=lambda r: r["path"])
        read[shift] = AL.readings(recs, X)
        if opens is not None and shift == "lower_bound":
            opened = int(sum(1 for r in recs if int(r["second_firm_opened_on"]) >= 0))
    out = {"growth_at_bound": float(read["lower_bound"]["growth_on_required"]),
           "growth_at_point": float(read["point"]["growth_on_required"]),
           "required_p90": float(read["lower_bound"]["required_p90"]), "paths": int(n_paths), "seed": int(seed)}
    if opened is not None:
        out["paths_opened_at_bound"] = opened
    return out


def added_row_problems(rd: Path, cell: str, reading: dict[str, float]) -> list[str]:
    """A day-0 joint call at the screen's seed, 500 paths, against `rc150_added_lucid.csv`'s rows for `cell` (`5+k`,
    section `cell`): the growth on the required bankroll at the bound and at the point and the required bankroll at
    the bound, to 1e-9 (D-593's own tolerance); a problem names the reading and the size of the difference, never a
    value."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / ADDED_FILE)
    g = d[(d["section"].astype(str) == "cell") & (d["cell"].astype(str) == str(cell))]
    out = []
    for key, shift, col in (("growth_at_bound", "lower_bound", "growth_on_required"),
                            ("growth_at_point", "point", "growth_on_required"),
                            ("required_p90", "lower_bound", "required_p90")):
        r = g[g["shift"].astype(str) == shift]
        if len(r) != 1:
            out.append(f"{ADDED_FILE} holds {len(r)} {cell} cell rows at {shift}")
            continue
        want = float(r[col].astype(float).iloc[0])
        if not abs(float(reading[key]) - want) <= 1e-9:
            out.append(f"{key}: differs from {ADDED_FILE}'s {cell} by {abs(float(reading[key]) - want):.3g}")
    return out


# ------------------------------------------------------------------------------------------------ line (3)(iv)


def walk(J: dict[str, Any]) -> dict[str, Any]:
    """P-16's walk for the coin line (`rc_stop_walkforward.walk_stop` at the 37.5-point stop, `rc150_routing`'s)."""
    import rc150_dev_test as R
    import rc_stop_walkforward as WF

    return WF.walk_stop(J["I"], R.STOP)


def coin_inputs(J: dict[str, Any], W: dict[str, Any], seed: int) -> dict[str, Any]:
    """P-16's cell under the coin sequence `seed` as the joint engine reads it: its trades re-dealt on the walk
    (`rc150_routing.coin_cell`), the opposite side by the same walk with every coin side of that sequence negated
    (`rc_stop_walkforward.cell`), aligned one for one (`hypo_hedge_a3.align_opposite`), and
    `rc150_firm_split.inputs`' construction on them (`rc150_added_lucid.span_inputs`: the blocks, the day capacity,
    P-16's engine arguments, Lucid as firm 1) with that sequence's own e and 0.05 bound by R (`atlas_a3.bounds`, the
    era rule)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import hypo_hedge_a3 as ha
    import rc150_added_lucid as AL
    import rc150_dev_test as R
    import rc150_routing as RT
    import rc_stop_walkforward as WF

    from propedge.research import resolved_coin as rc

    I, days = J["I"], list(J["days"])
    t = RT.coin_cell(W, I, int(seed), days)
    table = rc.coin_table(I["L"]["days"]["date"].astype(str).tolist(), rc.marks(), seed=int(seed))
    f = WF.cell({**W, "coins": {k: -int(v) for k, v in table.items()}}, R.STOP, days)["trades"]
    if t is None or f is None or len(f) != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): coin sequence {seed} leaves the cell or its opposite side no trade, "
                         "or another number of them.")
    fa = ha.align_opposite(t, f)
    _, e_by, lb_by, _, _ = A.bounds(t, days, B.rrs(t), I["L"]["cfg"])
    return AL.span_inputs(I, t, fa, days, e_by, lb_by)


def coin_problems(J: dict[str, Any], W: dict[str, Any]) -> list[str]:
    """The coin line's construction at the REGISTERED coin against the cell itself (`rc150_firm_split.inputs`): the
    trades and the aligned opposite side by content hash, each R's e and bound, the bound's shifts and the day
    capacity -- so a coin sequence's inputs are the cell's own construction with only the coin changed."""
    import rc_dev_test as D

    X = J["X"]
    C = coin_inputs(J, W, Sel.REGISTERED_COIN)
    out = []
    if D.trades_hash(C["t"]) != D.trades_hash(X["t"]):
        out.append("the re-dealt cell at the registered coin is not the cell")
    if D.trades_hash(C["fa"]) != D.trades_hash(X["fa"]):
        out.append("the re-dealt opposite side at the registered coin is not the cell's")
    if C["e_by"] != X["e_by"] or C["lb_by"] != X["lb_by"] or C["delta_by_rr"] != X["delta_by_rr"] or (
            float(C["delta_r"]) != float(X["delta_r"])):
        out.append("the bounds or the bound's shifts at the registered coin are not the cell's")
    if int(C["cap"]) != int(X["cap"]) or list(C["days"]) != list(X["days"]) or int(C["horizon"]) != int(X["horizon"]):
        out.append("the day capacity, the days or the horizon at the registered coin are not the cell's")
    return out


def coin_jobs(J: dict[str, Any], W: dict[str, Any], seed: int, seats: tuple[int, ...], opens: str | None, *,
              deal: str = UNHEDGED) -> dict[str, Any]:
    """A joint cell's verdict-arm job under the coin sequence `seed` (`coin_inputs`, `jobs`). The coin line is a
    guard: a cell under a hedge deal (`deal`; `hypothetical_hedge`) is REFUSED (D-644 (4))."""
    import customer_journey as CJ
    import rc150_firm_split as F

    if deal != UNHEDGED:
        Sel.refuse_labelled([f"{seats[0]}+{seats[-1]} {deal}"], [f"{seats[0]}+{seats[-1]} {deal}"],
                            "a guard (the coin line)")

    C = coin_inputs(J, W, seed)
    return jobs(J, seats, opens, X=C, blocks={Sel.ARM: F.arm_blocks(C, CJ.SHIFT_OF[Sel.ARM])})[Sel.ARM]


__all__ = ["DECISION", "ADDED_FILE", "U1_CONFIG", "TWIN", "TWIN_EQUALS_U1", "CHECK_CELL", "OPENING_ROLE",
           "OPENING_MEASURE_ROLE", "KIND", "seats_of", "opens_of", "added_cell", "base_def", "rules_problems", "inputs",
           "jobs", "joint_starts", "joint_task", "dispatch", "tasks_of", "run_starts", "sequence_problems",
           "opening_readings", "opening_rows", "deal_readings", "deal_rows", "DEAL_ROLE", "DEAL_MEASURE_ROLE", "DEAL_KEYS",
           "HYPOTHETICAL_ROLE", "UNHEDGED", "deal_of", "variant_id_of", "paths_task", "path_tasks", "gate_run", "added_row_problems", "walk",
           "coin_inputs", "coin_problems", "coin_jobs"]
