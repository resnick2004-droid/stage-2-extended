"""Q-47's identities (`extended/gate.py`: the gate re-composed so a design can declare another funded-account class),
and Q-71's (the gate's three more seams and the campaign re-composed under it, `extended/campaign.py`), refusing.

    python identity/gate_identity.py --synthetic                # light, the fast tier: synthetic blocks, no bars
    python identity/gate_identity.py --paths 4 --cls all        # slow (the run lock): P-14 and P-16 at 4 paths
    python identity/gate_identity.py --paths 500 --workers 1 --cls all   # heavy, the lead's (the run lock)

**`--paths N`.** The registered gate calls, made exactly as the registered rows were made, through
`extended.gate.run_gate` in place of the vendored `gate.run_gate` -- and so, since Q-71, through
`extended.campaign.simulate_lockstep_campaign` in place of the vendored campaign. The arms (`--cls`):

- `none`: no seam given (the vendored engine call);
- `passthrough`: `extended.gate.PassThroughFundedAccount` (a subclass that overrides nothing) through Q-47's seam;
- `seams` (Q-71): every seam given at Topstep's value -- `PassThroughFundedAccount`, `PassThroughCombineAccount`
  through `combine_account_cls`, `payout_lag_days` at the lag the gate takes when none is given (the Aeropay lag of
  Stage 2's verified ledger, `extended.gate.topstep_payout_lag_days`), and `household_closure=False`.

`both` (the default) is `none` and `passthrough` (Q-51's run); `all` adds `seams`. Each arm is compared on the first N
paths of the registered paths file, both shifts, every `zero_edge_decomposition.PATH_COLS` column to 1e-6, by Stage 2's
own comparison (`zd.path_problems`):

- **P-14** (A3-BRK30-CB20; Stage 2 D-509/D-513). The call is P-14's engine call as `rc_screen.Runner.run` makes it for
  `rc_screen.identity_problems`: `rc_screen.inputs()`, A3-BRK30's cell trades, the era rule's bounds
  (`atlas_a3.bounds`), the gate blocks, `atlas_a3.gate_kwargs` with P-14's seed, strict gap and budget, 0 % only, the
  placement off. The paths are compared against `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run.
- **P-16** (`rc_s150_all_nr`; Stage 2 D-544/D-547). The call is identity/stage2_identity.py's `p16_problems`: the cell
  rebuilt by `rc150_dev_test.SPEC`, its trades' hash against the pinned one, seed 20261206. The paths are compared
  against `results/rc_s150_all_gate_paths.csv`'s `gate` run.

`--cls none|passthrough|both` (default both) chooses the arms; `--only p14|p16` chooses the designs.

**`--synthetic` (light).** On synthetic trade blocks (seed 20261947, F-P's draft section 11: the build's toy
campaigns), through the vendored engine, with the gate's options rotation, flat-account routing, a purchase budget,
the four denial levels and the placement off, eight checks. The strict one-position gap is not used here: the vendored
engine needs each trade's exit at every R for it (D-349, D-351), which synthetic one-R blocks lack. The P-14 and P-16
checks exercise it on the registered trades.

1. **source pinned:** the vendored `run_gate`'s source hashes to `extended.gate.VENDORED_RUN_GATE_SHA256`;
2. **wrong pin refused:** a different pin is refused;
3. **no class:** the adapter's rows equal the vendored gate's exactly, and so does every path's record
   (`portfolio_stage.composed_hook`'s sink, every key);
4. **pass-through class:** the same, the rows apart from the added `funded_account_cls` column, which names the class;
5. **probe reaches the engine:** a probe subclass that is never eligible for a payout leaves every path unpaid, where
   the vendored gate pays some;
6. **probe reaches path workers:** the probe at two workers gives every path's record exactly as at one worker;
7. **non-account class refused;**
8. **unpicklable class refused:** a class defined inside a function, at two workers.

Q-71's checks (the firms draft's T-10), on the same construction of synthetic blocks and gate arguments drawn from seed
20261992 (the draft's section 12: "the build's toy campaigns", T-10 among them):

9. **campaign source pinned:** the vendored `simulate_lockstep_campaign`'s source hashes to
   `extended.campaign.VENDORED_CAMPAIGN_SHA256`;
10. **wrong campaign pin refused;**
11. **re-composed, statement for statement:** `extended.campaign.simulate_lockstep_campaign` with its lines marked Q-71
    removed parses to the vendored campaign, and `extended.gate.run_gate` with its lines marked Q-47 or Q-71 removed to
    the vendored gate (the docstrings aside); and the check is not vacuous: the gate with its Q-71 lines kept is not
    the vendored gate;
12. **campaign, nothing given:** the re-composed campaign's summary and every path (every field of every record, by
    value) equal the vendored campaign's, on independent binary draws;
13. **campaign, pass-through evaluation class:** the same, the summary's provenance apart from the added
    `combine_account_cls`, which names the class;
14. **seams at Topstep's values:** the gate with `PassThroughFundedAccount`, `PassThroughCombineAccount`, the Topstep
    lag given explicitly and `household_closure=False` gives the vendored gate's rows (apart from the four added
    columns, which name the values) and every path's record, all four denial levels;
15. **lag reaches the engine:** with a bankroll that never binds, a lag 7 sessions longer leaves every account's
    requests (days and amounts) as they were and moves the campaign's first payout arrival 7 sessions later on every
    path (or past the horizon); some path is paid and some arrival moves;
16. **household rule reaches the engine:** a probe funded class whose rule's default reading is count-only and whose
    trigger is its first payout: None and False give the same paths (count-only, nothing closed, some trigger); True
    closes the household at the first trigger -- every path with a trigger closes on that day, buys and activates
    nothing after it, and some path ends other live accounts there; True with Topstep's funded class is refused;
17. **evaluation probe reaches the engine:** a probe `CombineAccount` subclass that never passes leaves every path with
    no funded account, where the vendored gate funds some;
18. **evaluation probe reaches path workers:** the probe at two workers gives every path's record exactly as at one;
19. **bad seam arguments refused:** a negative, fractional or boolean lag; a household reading that is not a bool; an
    evaluation class that is not a `CombineAccount`; one that cannot pickle, at two workers.

**The read (Q-48).** With `--paths`, before anything runs, `main` authorises Stage 2's engine's read through
`extended.reader.authorise_engine_read` (purpose `identity`, declaration **E-028**, the window 2020-01-02 to
2026-07-16; the files: A1's events and days and A3's cached walk for P-14, and the bars for P-16's cell); a refusal
ends the run (`EXIT 3`) before anything is read. Ledgered only inside a clean run (E-026). `--synthetic` reads no bar
or walk and authorises nothing.

Exit 0 when every part run holds; 3 when one is refused. Nothing is written (inside a clean run, the read's ledger
line). Peak memory printed last.
"""
from __future__ import annotations

import argparse
import dataclasses
import math
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign.lockstep import CombineAccount, FundedAccount  # noqa: E402

import stage2_identity as SI  # noqa: E402  (identity/stage2_identity.py: P-16's seed and paths file, peak memory)

from extended import campaign as XC  # noqa: E402
from extended import gate as XG  # noqa: E402
from extended import reader  # noqa: E402

#: the Stage 2 tree the engine reads (named for the read's authorisation, Q-48)
VENDOR = ROOT / "vendor" / "stage2"
#: the decision row that registered this identity (Q-47's, merged under E-028)
READ_ROW = "E-028"
#: the synthetic campaigns' seed: F-P's draft section 11 assigns 20261947 to "the build's toy campaigns", and this
#: adapter is F-P's build (its 13.1 item 3; E-025 (2))
SYN_SEED = 20261947
#: Q-71's synthetic campaigns' seed: the firms draft's section 12 assigns 20261992 to "the build's toy campaigns (T-1 to
#: T-7, T-10, T-12, T-13)", and T-10 is A-8's test (this gate's Q-71 seams)
Q71_SEED = 20261992
SYN_DAYS = 160
SYN_PATHS = 6
#: Q-47's two arms (Q-51's run), every arm `--cls` can choose (Q-71 adds `seams`), and the two groups
CLS_ARMS = ("none", "passthrough")
ARMS = ("none", "passthrough", "seams")
ARM_GROUPS = {"both": CLS_ARMS, "all": ARMS}
#: Q-71's lag check: the extra sessions, and a bankroll that never binds (so no purchase depends on when cash arrives)
LAG_EXTRA = 7
BIG_BANKROLL = 1_000_000.0


class NeverPaysFundedAccount(FundedAccount):
    """The synthetic probe: never eligible for a Standard-path payout, so no path is ever paid. It shows that a class
    given to the adapter reaches the engine, and reaches path workers (a module-level class pickles by reference)."""

    def _standard_eligible(self, rules: Any) -> bool:
        return False


class NeverPassesCombineAccount(CombineAccount):
    """Q-71's evaluation probe: a close at the target is undone (as the vendored D-619 example,
    `propedge.research.hedge_cycle.StaticCombineAccount`, undoes one short of its green days), so no evaluation ever
    passes and no path ever funds an account. It shows that `combine_account_cls` reaches the engine, and path
    workers."""

    def trade_day(self, rules: Any, policy: Any, rel_day: int, calendar_day: int,
                  ledger: list[dict[str, Any]] | None = None, need_aware: bool = False,
                  consistency_cap: bool = False) -> None:
        super().trade_day(rules, policy, rel_day, calendar_day, ledger=ledger, need_aware=need_aware,
                          consistency_cap=consistency_cap)
        if self.passed:
            self.passed = False
            self.pass_day = -1
            self.resolved_on = None


class HouseholdProbeFundedAccount(FundedAccount):
    """Q-71's household probe: a funded account that declares a household rule whose default reading is count-only
    (`HOUSEHOLD_CLOSES_AT_LIVE` False), raised by its first payout, at whose close the account ends (as Lucid's ends at
    its fifth, `propedge.contract.lucid.LucidFundedAccount`). It shows that `household_closure` reaches the engine."""

    HOUSEHOLD_CLOSES_AT_LIVE = False

    @property
    def closes_household(self) -> bool:
        return self.n_payouts >= 1

    def _after_payout(self, calendar_day: int) -> None:
        if self.n_payouts >= 1:
            self.ended_on = int(calendar_day)


# ------------------------------------------------------------------------------------------------ synthetic


def syn_blocks(seed: int = SYN_SEED) -> list:
    """SYN_DAYS synthetic days of zero to two trades at $500 risk, won at 1.5R with probability 0.55, each with its
    entry and exit minute (so rotation routes only to a flat account). Q-47's from `SYN_SEED`, Q-71's from
    `Q71_SEED`."""
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng([int(seed), 1])
    out = []
    for _ in range(SYN_DAYS):
        k = int(rng.integers(0, 3))
        win = rng.random(k) < 0.55
        entry = 510.0 + 90.0 * np.arange(k, dtype=float)
        out.append(DayBlock(pnl=np.where(win, 750.0, -500.0).astype(float), risked=np.full(k, 500.0),
                            exit_reasons=tuple("target" if w else "stop" for w in win),
                            entry_t=entry, exit_t=entry + 45.0))
    return out


def syn_kwargs(seed: int = SYN_SEED) -> dict[str, Any]:
    from propedge.campaign.protocols import Protocol
    from propedge.contract.adapter import rules_from_ledger

    proto = Protocol(name="q47_synthetic", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=500.0,
                     trades_per_day=2, max_concurrent_accounts=5)
    return dict(e=0.375, lb=0.10, protocol=proto, bankroll=5000.0, horizon_days=150, n_paths=SYN_PATHS,
                seed=int(seed), accounts=5, sizing=None, rules=rules_from_ledger(), combines=1, total_accounts=5,
                purchase_budget=(20, 21), rtp=False)


def _hook():
    import portfolio_stage as ps

    sink: list[dict] = []
    hook = ps.composed_hook({}, sink=sink)
    ps._label(hook, "q47_synthetic")
    return hook, sink


def _same(a: Any, b: Any) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return type(a) is type(b) and a == b


def sink_problems(a: list[dict], b: list[dict], what: str) -> list[str]:
    if len(a) != len(b):
        return [f"{what}: {len(a)} path records against {len(b)}"]
    out = []
    for i, (x, y) in enumerate(zip(a, b)):
        if set(x) != set(y):
            out.append(f"{what}: record {i}'s keys differ ({sorted(set(x) ^ set(y))})")
            continue
        bad = [k for k in x if not _same(x[k], y[k])]
        if bad:
            out.append(f"{what}: record {i} differs on {bad[:6]}")
    return out[:8]


def rows_problems(a: pd.DataFrame, b: pd.DataFrame, what: str) -> list[str]:
    try:
        pd.testing.assert_frame_equal(a, b, check_exact=True)
    except AssertionError as exc:
        return [f"{what}: the rows differ -- {str(exc).splitlines()[0]}"]
    return []


def synthetic_problems() -> dict[str, list[str]]:
    """Each check's problems (an empty list where it holds), in the docstring's order."""
    from propedge.campaign import gate as vg
    from propedge.campaign.lockstep import path_pool

    out: dict[str, list[str]] = {}
    got = XG.vendored_run_gate_sha256()
    out["source pinned"] = ([] if got == XG.VENDORED_RUN_GATE_SHA256 else
                            [f"the vendored run_gate hashes to {got}, the pin is {XG.VENDORED_RUN_GATE_SHA256}"])
    try:
        XG.check_vendored_source("0" * 64)
        out["wrong pin refused"] = ["a wrong pin was not refused"]
    except RuntimeError:
        out["wrong pin refused"] = []

    blocks = syn_blocks()
    kw = syn_kwargs()
    hv, sv = _hook()
    rows_v, ok_v = vg.run_gate(blocks, path_hook=hv, **kw)
    paid_v = sum(float(r["payouts"]) for r in sv)

    hx, sx = _hook()
    rows_x, ok_x = XG.run_gate(blocks, path_hook=hx, **kw)
    p = rows_problems(rows_v, rows_x, "no class") + sink_problems(sv, sx, "no class")
    if ok_v != ok_x:
        p.append(f"no class: the gate flag {ok_x} against {ok_v}")
    if not paid_v > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["no class: rows and paths equal"] = p

    hp, sp = _hook()
    rows_p, ok_p = XG.run_gate(blocks, path_hook=hp, funded_account_cls=XG.PassThroughFundedAccount, **kw)
    p = []
    name = XG.class_name(XG.PassThroughFundedAccount)
    if "funded_account_cls" not in rows_p.columns or set(rows_p["funded_account_cls"]) != {name}:
        p.append(f"pass-through class: the rows do not name {name}")
    else:
        p += rows_problems(rows_v, rows_p.drop(columns="funded_account_cls"), "pass-through class")
    p += sink_problems(sv, sp, "pass-through class")
    if ok_v != ok_p:
        p.append(f"pass-through class: the gate flag {ok_p} against {ok_v}")
    out["pass-through class: rows and paths equal"] = p

    h1, s1 = _hook()
    XG.run_gate(blocks, path_hook=h1, funded_account_cls=NeverPaysFundedAccount, **kw)
    paid_1 = sum(float(r["payouts"]) for r in s1)
    out["probe reaches the engine"] = ([] if paid_1 == 0.0 and paid_v > 0 else
                                       [f"the probe's paths were paid {paid_1} (vendored: {paid_v})"])

    pool, n = path_pool(2, n_tasks=SYN_PATHS, memory_per_worker_gb=0.5)
    if pool is not None:
        pool.shutdown()
    if int(n) < 2:
        # E-033: the guard's grant depends on the machine's free memory at that moment, so a short machine made this
        # identity -- and every commit's fast tier -- fail with nothing wrong in the code. Said loudly, not counted as a
        # failure; it is not a pass either (the two-worker property is unchecked on this run).
        print(f"NOT CHECKED (not a pass): probe reaches path workers -- the memory guard allows {n} worker(s) now",
              flush=True)
        out["probe reaches path workers"] = []
    else:
        h2, s2 = _hook()
        ran, _ = at_two_workers(lambda: XG.run_gate(blocks, path_hook=h2, funded_account_cls=NeverPaysFundedAccount,
                                                    workers=2, memory_per_worker_gb=0.5, **kw),
                                "probe reaches path workers")
        out["probe reaches path workers"] = sink_problems(s1, s2, "probe, two workers against one") if ran else []

    try:
        XG.run_gate(blocks, funded_account_cls=dict, **kw)
        out["non-account class refused"] = ["a class that is not a funded account was not refused"]
    except TypeError:
        out["non-account class refused"] = []

    def local_class() -> type:
        class LocalFundedAccount(FundedAccount):
            pass

        return LocalFundedAccount

    try:
        XG.run_gate(blocks, funded_account_cls=local_class(), workers=2, **kw)
        out["unpicklable class refused"] = ["a class defined inside a function was not refused at two workers"]
    except TypeError:
        out["unpicklable class refused"] = []
    out.update(q71_synthetic_problems())
    return out


# ------------------------------------------------------------------------------------------------ Q-71, synthetic

#: what the vendored guard (`lockstep.path_pool`) writes to stderr when it grants fewer workers than asked
GUARD_FELL_BACK = "[lockstep] workers 2 -> "


def at_two_workers(call: Any, what: str) -> tuple[bool, Any]:
    """Run `call` (a gate call at `workers=2`) with stderr captured and passed on, and say whether it really ran at two
    workers. The guard is consulted again inside the gate, and the free memory can fall between the caller's look and
    the gate's (Q-71 saw it fall to one worker, which made a two-worker comparison pass in one process): when the
    vendored guard announces a fall-back, the check is printed NOT CHECKED (not a pass), as E-033 asks."""
    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        result = call()
    text = buf.getvalue()
    sys.stderr.write(text)
    ran = GUARD_FELL_BACK not in text
    if not ran:
        print(f"NOT CHECKED (not a pass): {what} -- the memory guard fell back to one worker inside the gate",
              flush=True)
    return ran, result


def deep_difference(a: Any, b: Any, where: str = "") -> str | None:
    """The first place two engine records differ (dataclasses field by field, arrays by dtype, shape and value, dicts
    by keys in order, sequences item by item, a NaN equal to a NaN, everything else by type and value), or None."""
    if dataclasses.is_dataclass(a) and not isinstance(a, type):
        if type(a) is not type(b):
            return f"{where}: {type(a).__name__} against {type(b).__name__}"
        for f in dataclasses.fields(a):
            d = deep_difference(getattr(a, f.name), getattr(b, f.name), f"{where}.{f.name}")
            if d:
                return d
        return None
    if isinstance(a, np.ndarray):
        if not isinstance(b, np.ndarray) or a.dtype != b.dtype or a.shape != b.shape:
            return f"{where}: arrays of different dtype or shape"
        same = (np.array_equal(a, b, equal_nan=True) if a.dtype.kind in "fc" else
                all(deep_difference(x, y) is None for x, y in zip(a.ravel().tolist(), b.ravel().tolist())))
        return None if same else f"{where}: the arrays differ"
    if isinstance(a, dict):
        if not isinstance(b, dict) or list(a) != list(b):
            return f"{where}: the keys differ"
        for k in a:
            d = deep_difference(a[k], b[k], f"{where}[{k!r}]")
            if d:
                return d
        return None
    if isinstance(a, (list, tuple)):
        if type(a) is not type(b) or len(a) != len(b):
            return f"{where}: {type(a).__name__} of {len(a)} against {type(b).__name__} of {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = deep_difference(x, y, f"{where}[{i}]")
            if d:
                return d
        return None
    if isinstance(a, (float, np.floating)) and isinstance(b, (float, np.floating)) and math.isnan(a) and math.isnan(b):
        return None if type(a) is type(b) else f"{where}: {type(a).__name__} against {type(b).__name__}"
    if type(a) is not type(b) or a != b:
        return f"{where}: {a!r} against {b!r}"
    return None


def _capture():
    """A path hook that keeps every run's `LockstepPath`s, (shift, level, paths) in run order, and adds no column."""
    got: list[tuple[str, float, list]] = []

    def hook(shift: str, p: float, paths: Any) -> dict:
        got.append((shift, float(p), list(paths)))
        return {}

    return hook, got


def captured_difference(a: list, b: list, what: str) -> list[str]:
    if [(s, p, len(x)) for s, p, x in a] != [(s, p, len(x)) for s, p, x in b]:
        return [f"{what}: the runs or their path counts differ"]
    for (s, p, xa), (_, _, xb) in zip(a, b):
        for i, (pa, pb) in enumerate(zip(xa, xb)):
            d = deep_difference(pa, pb, f"path {i}")
            if d:
                return [f"{what}: {s} at {p}: {d}"]
    return []


def _requests(path: Any) -> tuple:
    """Every funded account's payout requests on a path: (index, activation day, request days, net amounts)."""
    return tuple((f.index, f.activation_day, f.payout_days, f.payout_cash) for f in path.funded)


def _refused(fn: Any, exc: type) -> bool:
    try:
        fn()
    except exc:
        return True
    return False


def q71_synthetic_problems() -> dict[str, list[str]]:
    """Q-71's checks 9-19 (the docstring), each's problems (an empty list where it holds)."""
    from propedge.campaign import gate as vg
    from propedge.campaign import lockstep as vl
    from propedge.campaign.lockstep import path_pool

    out: dict[str, list[str]] = {}
    got = XC.vendored_campaign_sha256()
    out["campaign source pinned"] = ([] if got == XC.VENDORED_CAMPAIGN_SHA256 else
                                     [f"the vendored campaign hashes to {got}, the pin is {XC.VENDORED_CAMPAIGN_SHA256}"])
    out["wrong campaign pin refused"] = ([] if _refused(lambda: XC.check_vendored_source("0" * 64), RuntimeError)
                                         else ["a wrong campaign pin was not refused"])
    p = [f"campaign: {x}" for x in XC.campaign_recomposition_problems()]
    p += [f"gate: {x}" for x in XG.gate_recomposition_problems()]
    if not XC.recomposition_problems(XG.run_gate, vg.run_gate, ("Q-47",)):
        p.append("the check is vacuous: the gate with its Q-71 lines kept passed as the vendored gate")
    out["re-composed: the vendored bodies plus marked lines"] = p

    # 12, 13: the campaign itself, on independent binary draws
    from propedge.campaign.protocols import Protocol
    from propedge.contract.adapter import rules_from_ledger

    proto = Protocol(name="q71_synthetic", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=500.0,
                     trades_per_day=2, max_concurrent_accounts=5)
    ckw = dict(edge=0.10, seed=Q71_SEED, initial_bankroll=5000.0, rules=rules_from_ledger(), horizon_days=150,
               n_paths=4, max_concurrent_accounts=5, require_verified_cap=False, max_total_accounts=5)
    sv_, pv_ = vl.simulate_lockstep_campaign(proto, **ckw)
    sx_, px_ = XC.simulate_lockstep_campaign(proto, **ckw)
    p = [x for x in (deep_difference(sv_, sx_, "summary"), deep_difference(pv_, px_, "paths")) if x]
    if not sum(float(x.path.total_payouts) for x in pv_) > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["campaign, nothing given: equals the vendored campaign"] = p
    sc_, pc_ = XC.simulate_lockstep_campaign(proto, combine_account_cls=XG.PassThroughCombineAccount, **ckw)
    p = [x for x in (deep_difference(pv_, pc_, "paths"),) if x]
    prov = dict(sc_.provenance)
    named = prov.pop("combine_account_cls", None)
    if named != XG.class_name(XG.PassThroughCombineAccount):
        p.append(f"the provenance names {named!r}, not the pass-through class")
    d = deep_difference(dataclasses.replace(sv_, provenance={}), dataclasses.replace(sc_, provenance={}), "summary")
    p += [x for x in (d, deep_difference(sv_.provenance, prov, "provenance")) if x]
    out["campaign, pass-through evaluation class: equal, named in the provenance"] = p

    # 14: every seam at Topstep's value, all four denial levels, against the vendored gate
    blocks = syn_blocks(Q71_SEED)
    kw = syn_kwargs(Q71_SEED)
    lag0 = XG.topstep_payout_lag_days()
    hv, sv = _hook()
    rows_v, ok_v = vg.run_gate(blocks, path_hook=hv, **kw)
    hs, ss = _hook()
    rows_s, ok_s = XG.run_gate(blocks, path_hook=hs, funded_account_cls=XG.PassThroughFundedAccount,
                               combine_account_cls=XG.PassThroughCombineAccount, payout_lag_days=lag0,
                               household_closure=False, **kw)
    want = {"funded_account_cls": XG.class_name(XG.PassThroughFundedAccount), "payout_lag_days": lag0,
            "household_closure": False, "combine_account_cls": XG.class_name(XG.PassThroughCombineAccount)}
    p = []
    for col, val in want.items():
        if col not in rows_s.columns or list(rows_s[col]) != [val] * len(rows_s):
            p.append(f"the rows do not name {col}={val!r}")
    if not p:
        p += rows_problems(rows_v, rows_s.drop(columns=list(want)), "seams at Topstep's values")
    p += sink_problems(sv, ss, "seams at Topstep's values")
    if ok_v != ok_s:
        p.append(f"the gate flag {ok_s} against {ok_v}")
    if not sum(float(r["payouts"]) for r in sv) > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["seams at Topstep's values: rows and paths equal"] = p

    # 15: the lag, with a bankroll that never binds, at the gate's level only
    lkw = dict(kw, bankroll=BIG_BANKROLL, levels=(0.0,))
    horizon = int(lkw["horizon_days"])
    h0, c0 = _capture()
    r0, _ = XG.run_gate(blocks, path_hook=h0, payout_lag_days=lag0, **lkw)
    h1, c1 = _capture()
    r1, _ = XG.run_gate(blocks, path_hook=h1, payout_lag_days=lag0 + LAG_EXTRA, **lkw)
    p = []
    if list(r1["payout_lag_days"]) != [lag0 + LAG_EXTRA] * len(r1):
        p.append("the rows do not name the lag given")
    moved = paid = 0
    for (s, _, xa), (_, _, xb) in zip(c0, c1):
        for i, (pa, pb) in enumerate(zip(xa, xb)):
            if _requests(pa) != _requests(pb):
                p.append(f"{s} path {i}: the accounts' requests changed with the lag")
                continue
            d0, d1 = pa.path.days_to_first_payout, pb.path.days_to_first_payout
            if d0 is None:
                if d1 is not None:
                    p.append(f"{s} path {i}: paid at {d1} with the longer lag, never with the shorter")
                continue
            paid += 1
            expect = d0 + LAG_EXTRA if d0 + LAG_EXTRA <= horizon - 1 else None
            if d1 != expect:
                p.append(f"{s} path {i}: the first arrival {d1} with the longer lag, not {expect} (from {d0})")
            elif d1 is not None:
                moved += 1
            if float(pb.path.total_payouts) > float(pa.path.total_payouts) + 1e-9:
                p.append(f"{s} path {i}: more cash arrived with the longer lag")
    if not (paid and moved):
        p.append(f"vacuous: {paid} paths paid, {moved} arrivals moved")
    out["lag reaches the engine"] = p[:8]

    # 16: the household rule, through a probe funded class, at the gate's level only
    hkw = dict(kw, levels=(0.0,))
    runs = {}
    for reading in (None, False, True):
        hk, ck = _capture()
        rows, _ = XG.run_gate(blocks, path_hook=hk, funded_account_cls=HouseholdProbeFundedAccount,
                              household_closure=reading, **hkw)
        runs[reading] = (rows, ck)
    p = captured_difference(runs[None][1], runs[False][1], "household None against False")
    if "household_closure" in runs[None][0].columns:
        p.append("household None: the rows name a reading that was not given")
    if list(runs[True][0].get("household_closure", [])) != [True] * len(runs[True][0]):
        p.append("household True: the rows do not name the reading")
    triggered = closed_others = 0
    for s, _, paths in runs[None][1]:
        for i, x in enumerate(paths):
            h = x.household
            if h.get("reading") != "count_only" or h.get("closed_on") != -1:
                p.append(f"household None, {s} path {i}: {h}")
            triggered += int(h.get("triggers", 0) > 0)
    for s, _, paths in runs[True][1]:
        for i, x in enumerate(paths):
            h = x.household
            if h.get("reading") != "closes_household":
                p.append(f"household True, {s} path {i}: the reading is {h.get('reading')!r}")
                continue
            day = int(h.get("closed_on", -1))
            if h.get("triggers", 0) > 0 and day < 0:
                p.append(f"household True, {s} path {i}: a trigger and no closure")
            if day >= 0:
                closed_others += int(h["combines_closed"] + h["funded_closed"] + h["passes_closed"] > 0)
                late_buys = [c.purchase_day for c in x.combines if c.purchase_day > day]
                late_funded = [f.activation_day for f in x.funded if f.activation_day > day]
                if late_buys or late_funded:
                    p.append(f"household True, {s} path {i}: bought {late_buys} or activated {late_funded} after "
                             f"the closure on {day}")
    if not triggered:
        p.append("vacuous: no path raised the household rule")
    if not closed_others:
        p.append("vacuous: no closure ended another live account")
    if not captured_difference(runs[None][1], runs[True][1], "x"):
        p.append("household True gave the count-only paths")
    if not _refused(lambda: XG.run_gate(blocks, household_closure=True, **hkw), ValueError):
        p.append("household True with Topstep's funded class was not refused")
    out["household rule reaches the engine"] = p[:8]

    # 17, 18: the evaluation class, through a probe that never passes, at the gate's level only
    ekw = dict(kw, levels=(0.0,))
    hv0, cv0 = _capture()
    vg.run_gate(blocks, path_hook=hv0, **ekw)
    he, ce = _capture()
    rows_e, _ = XG.run_gate(blocks, path_hook=he, combine_account_cls=NeverPassesCombineAccount, **ekw)
    funded_v = sum(len(x.funded) for _, _, xs in cv0 for x in xs)
    funded_e = sum(len(x.funded) for _, _, xs in ce for x in xs)
    passed_e = sum(int(c.passed) for _, _, xs in ce for x in xs for c in x.combines)
    p = [] if (funded_e == 0 and passed_e == 0 and funded_v > 0) else [
        f"the probe's paths funded {funded_e} accounts and passed {passed_e} evaluations (vendored: {funded_v} funded)"]
    if list(rows_e.get("combine_account_cls", [])) != [XG.class_name(NeverPassesCombineAccount)] * len(rows_e):
        p.append("the rows do not name the evaluation class")
    out["evaluation probe reaches the engine"] = p

    pool, n = path_pool(2, n_tasks=SYN_PATHS, memory_per_worker_gb=0.5)
    if pool is not None:
        pool.shutdown()
    if int(n) < 2:
        # as check 6 (E-033): said loudly, not counted as a failure, and not a pass
        print(f"NOT CHECKED (not a pass): evaluation probe reaches path workers -- the memory guard allows {n} "
              "worker(s) now", flush=True)
        out["evaluation probe reaches path workers"] = []
    else:
        hw, cw = _capture()
        ran, _ = at_two_workers(lambda: XG.run_gate(blocks, path_hook=hw, combine_account_cls=NeverPassesCombineAccount,
                                                    workers=2, memory_per_worker_gb=0.5, **ekw),
                                "evaluation probe reaches path workers")
        out["evaluation probe reaches path workers"] = (captured_difference(ce, cw, "evaluation probe, two workers")
                                                        if ran else [])

    def local_combine() -> type:
        class LocalCombineAccount(CombineAccount):
            pass

        return LocalCombineAccount

    bad = {
        "a negative lag": (lambda: XG.run_gate(blocks, payout_lag_days=-1, **ekw), ValueError),
        "a fractional lag": (lambda: XG.run_gate(blocks, payout_lag_days=2.5, **ekw), TypeError),
        "a boolean lag": (lambda: XG.run_gate(blocks, payout_lag_days=True, **ekw), TypeError),
        "a household reading not a bool": (lambda: XG.run_gate(blocks, household_closure="yes", **ekw), TypeError),
        "an evaluation class not a CombineAccount": (
            lambda: XG.run_gate(blocks, combine_account_cls=FundedAccount, **ekw), TypeError),
        "an evaluation class that cannot pickle, at two workers": (
            lambda: XG.run_gate(blocks, combine_account_cls=local_combine(), workers=2, **ekw), TypeError),
    }
    out["bad seam arguments refused"] = [f"{what} was not refused" for what, (fn, exc) in bad.items()
                                         if not _refused(fn, exc)]
    return out


# ------------------------------------------------------------------------------------------------ the registered paths


def arm_kwargs(arm: str, ledger: Any | None = None) -> dict[str, Any]:
    """The seams an arm gives the gate: none; Q-47's pass-through funded class; or (Q-71's `seams`) every seam at
    Topstep's value -- both pass-through classes, the lag the gate takes when none is given (read from `ledger`, the
    one the call passes, or Stage 2's verified ledger when None, as the campaign reads it), and no household closure."""
    if arm == "none":
        return {}
    if arm == "passthrough":
        return {"funded_account_cls": XG.PassThroughFundedAccount}
    if arm == "seams":
        return {"funded_account_cls": XG.PassThroughFundedAccount,
                "combine_account_cls": XG.PassThroughCombineAccount,
                "payout_lag_days": XG.topstep_payout_lag_days(ledger), "household_closure": False}
    raise ValueError(f"unknown arm {arm!r}; known: {ARMS}")


def arms_of(choice: str) -> tuple[str, ...]:
    """`--cls`'s choice as the arms it runs: one arm, `both` (none and passthrough, Q-51's) or `all` (the three)."""
    return ARM_GROUPS.get(choice, (choice,))


def p14_problems(n: int, workers: int, arms: tuple[str, ...]) -> dict[str, list[str]]:
    """P-14's gate call as `rc_screen.Runner.run` makes it for `rc_screen.identity_problems`, through the adapter."""
    import a3_brk30 as B
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    I = S.inputs()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = B.cell_trades(L)
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        return {a: ["the blocks hold a different number of trades"] for a in arms}
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    ref = read_result(RESULTS_DIR / S.P14_PATHS)
    out = {}
    for arm in arms:
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                                  "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"p14_identity_{arm}"
        ps._label(inner, label)
        kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=S.SEED, n_paths=int(n),
                           horizon=horizon, capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP,
                           purchase_budget=S.BUDGET)
        XG.run_gate(kw.pop("blocks"), workers=int(workers), **arm_kwargs(arm, kw.get("ledger")), **kw)
        out[arm] = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    return out


def p16_problems(n: int, workers: int, arms: tuple[str, ...]) -> dict[str, list[str]]:
    """P-16's gate call as identity/stage2_identity.py's `p16_problems` makes it, through the adapter."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    sp = P.SPEC
    if int(sp.seed) != SI.P16_SEED:
        return {a: [f"P-16's seed in the vendored script is {sp.seed}, not {SI.P16_SEED}"] for a in arms}
    I, b = sp.build()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    th = D.trades_hash(t)
    if th != sp.trades_sha256:
        return {a: [f"P-16's trades hash {th} is not the pinned {sp.trades_sha256}"] for a in arms}
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        return {a: ["the blocks hold a different number of trades"] for a in arms}
    pcfg = fcfg["portfolio"]
    ref = read_result(RESULTS_DIR / SI.P16_PATHS)
    out = {}
    for arm in arms:
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"p16_identity_{arm}"
        ps._label(inner, label)
        kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=SI.P16_SEED, n_paths=int(n),
                           horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,),
                           rtp=False, one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
        XG.run_gate(kw.pop("blocks"), workers=int(workers), **arm_kwargs(arm, kw.get("ledger")), **kw)
        out[arm] = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="the light identity on synthetic blocks (no bars)")
    ap.add_argument("--paths", type=int, default=None, help="the registered gate paths at N paths (slow or heavy)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=("p14", "p16"), default=None)
    ap.add_argument("--cls", choices=ARMS + tuple(ARM_GROUPS), default="both",
                    help="the arms: none, passthrough, seams (Q-71), both (none and passthrough) or all")
    a = ap.parse_args(argv)
    if not a.synthetic and a.paths is None:
        ap.error("give --synthetic or --paths N")
    if a.paths is not None and a.paths < 1:
        ap.error("--paths takes a whole number of at least 1")
    if a.paths is not None:
        names = [n for n in ("P-14", "P-16") if a.only is None or n.replace("-", "").lower() == a.only]
        try:                                        # Q-48: the engine's read authorised (ledgered in a clean run only)
            reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                         declaration=READ_ROW, files=SI.engine_files(VENDOR, bars="P-16" in names),
                                         what=f"{READ_ROW}'s identity (identity/gate_identity.py): "
                                              f"{' and '.join(names)} registered gate paths ({a.paths}) through "
                                              f"extended.gate, arms {a.cls}")
        except (reader.ReadRefused, FileNotFoundError) as exc:
            print(SI.refusal(exc))
            print("EXIT 3", flush=True)
            return 3
    bad = False
    t0 = time.time()
    if a.synthetic:
        res = synthetic_problems()
        for check, probs in res.items():
            if probs:
                bad = True
                print(f"FAILS: {check} -- " + "; ".join(probs))
            else:
                print(f"holds: {check}")
        print(("synthetic identity FAILS" if any(res.values()) else "synthetic identity HOLDS") +
              f" (Q-47 and Q-71, extended.gate and extended.campaign; {time.time() - t0:.0f} s)", flush=True)
    if a.paths is not None:
        arms = arms_of(a.cls)
        designs = [("P-14", p14_problems, "a3_brk30_cb20_gate_paths.csv"),
                   ("P-16", p16_problems, SI.P16_PATHS)]
        for name, fn, ref in designs:
            if a.only is not None and name.replace("-", "").lower() != a.only:
                continue
            t1 = time.time()
            print(f"{name}: the registered gate call through extended.gate, {a.paths} paths, arms {arms}...",
                  flush=True)
            for arm, probs in fn(int(a.paths), int(a.workers), arms).items():
                if probs:
                    bad = True
                    print(f"identity FAILS: {name} gate through extended.gate ({arm}) -- {len(probs)} problem(s): "
                          + "; ".join(probs[:6]), flush=True)
                else:
                    print(f"identity HOLDS: {name} gate through extended.gate ({arm}) -- the first {a.paths} paths of "
                          f"results/{ref}'s gate run, both shifts, every PATH_COLS column to 1e-6", flush=True)
            print(f"  {name}: {time.time() - t1:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
