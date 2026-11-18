"""Q-71 (the other-firms reading's A-8, `prereg/DRAFT_RD_firms.md` 4.6; E-038): Stage 2's lockstep campaign,
re-composed so that every path can take another evaluation-account class.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import campaign as XC
    summary, paths = XC.simulate_lockstep_campaign(protocol, ..., combine_account_cls=MyCombineAccount)

**Why it exists.** The vendored path takes an evaluation class (`simulate_lockstep_path(combine_account_cls=...)`,
Stage 2 D-619); the vendored campaign, `propedge.campaign.lockstep.simulate_lockstep_campaign`
(`vendor/stage2/propedge/campaign/lockstep.py`, lines 2653-2861 of the snapshot of Stage 2 f1b42e2, vendored under
E-002), does not pass one on. The reading's DayTraders and TradeDay evaluations (its A-2 and A-4) are `CombineAccount`
subclasses, so the gate (`extended/gate.py`, A-8) needs a campaign that passes the class to its paths.

The vendored tree is read-only (E-002), and a module attribute of it substituted during a call is not done (Q-47;
E-011). So `simulate_lockstep_campaign` below is the vendored function's text, copied verbatim, with exactly three
additions, each on lines that carry the comment marker Q-71:

1. the guard below, first in the body;
2. the keyword `combine_account_cls` (default None), last in the signature, put in the paths' keywords only when
   given -- so with None every path is called with the vendored keywords, argument for argument;
3. the summary's provenance names the class (`combine_account_cls`, its module and name) only when given, as the
   vendored campaign names a funded class only when given.

Every helper the body calls is the vendored one, imported from the vendored module, never copied: the payout-timing
check, the ledger's lag, the purchase-budget and entry-option checks, the path seeds, the path runner (`_run_paths`,
and through it `simulate_lockstep_path`, workers and pool included) and the summary. The class itself is checked by the
vendored path (`TypeError` for one that is not `CombineAccount` or a subclass of it); with more than one worker the
vendored input check refuses one that does not pickle. The summary's provenance still names the vendored function as
the simulation: with no class the call is the vendored one, and a class given is named beside it.

**The guard, refusing.** The text was composed from the vendored function whose source (LF line endings) has the sha256
`VENDORED_CAMPAIGN_SHA256`. Every call checks it first and refuses (`RuntimeError`) if the vendored function has
changed -- a newer Stage 2 snapshot is a new decision row, and this module is re-composed and re-checked under it.
`recomposition_problems` checks the composition itself: this function with its marked lines removed parses to the
vendored function, statement for statement (the docstrings aside).

**Q-70 (the place recorder, `extended/place_records.py`)** adds, on lines marked Q-70, the keyword `path_reducer`
(default None, last in the signature) and one statement choosing the paths' runner (`path_runner`): the vendored
`_run_paths` without a reducer, so with None every call is as before; with one, the vendored runner re-composed so each
path is recorded and read where it ran. The proof strips both markers (`MARKERS`).

**Q-119 (RD-03's A-3, `prereg/RD-03_contract_levers.md` 14.1)** adds, on lines marked Q-119, the keyword `levers`
(default None, last in the signature): given, it goes into every path's keywords and the paths run through
`extended.levers_path`'s copy of the vendored path runner and path (`lever_runner`); the summary's provenance names it.
None: every call as before. The proof strips the three markers.

**The identities** (`identity/gate_identity.py`, through `extended.gate.run_gate`, which calls this campaign):
synthetic in the fast tier; P-14's and P-16's registered gate paths at 4 paths (slow) and at 500 (heavy, the lead's).
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import re
import textwrap
from typing import Any, Callable, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

from propedge.campaign import lockstep as _vl  # noqa: E402
from propedge.campaign.lockstep import (  # noqa: E402,F401  -- every name the vendored body uses, the vendored objects
    ACTIVATION_ON_ACTIVATION,
    DEFAULT_PAYOUT_TIMING,
    PAYOUT_TIMING_NOTES,
    CampaignSummary,
    ConductModel,
    FocusedTraderModel,
    LockstepPath,
    Protocol,
    _run_paths,
    check_pause_after_funded,
    check_payout_timing,
    check_purchase_budget,
    check_seat_ramp,
    check_wallet_stop,
    path_seeds,
    summarise_paths,
)

#: sha256 of the vendored `propedge.campaign.lockstep.simulate_lockstep_campaign`'s source text (LF), from which
#: `simulate_lockstep_campaign` below was composed (Stage 2 f1b42e2, vendored under E-002; lockstep.py lines 2653-2861)
VENDORED_CAMPAIGN_SHA256 = "0bb321f521e99dfcf560ea128de7cf9df2bf621c1878482cb9860e08f8285f90"
#: the comment marker on every added line of this module's re-composed function
MARKER = "Q-71"
#: every marker the re-composition proof strips: Q-71's evaluation class, Q-70's place recorder, Q-119's levers
MARKERS = (MARKER, "Q-70", "Q-119")


def source_sha256(fn: Callable) -> str:
    """The sha256 of a function's source text, with line endings normalised to LF."""
    src = inspect.getsource(fn).replace("\r\n", "\n")
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def vendored_campaign_sha256() -> str:
    """The sha256 of the vendored `simulate_lockstep_campaign`'s source text (LF)."""
    return source_sha256(_vl.simulate_lockstep_campaign)


def check_vendored_source(expected: str | None = None) -> None:
    """Refuse (`RuntimeError`) unless the vendored `simulate_lockstep_campaign` is the one this module was composed
    from."""
    want = VENDORED_CAMPAIGN_SHA256 if expected is None else str(expected)
    got = vendored_campaign_sha256()
    if got != want:
        raise RuntimeError(f"REFUSED (Q-71): the vendored lockstep.simulate_lockstep_campaign's source hashes to {got}, "
                           f"not the {want} this adapter was composed from; re-compose extended/campaign.py under the "
                           "new snapshot's row")


def _function_node(src: str) -> ast.FunctionDef:
    mod = ast.parse(textwrap.dedent(src))
    fns = [n for n in mod.body if isinstance(n, ast.FunctionDef)]
    if len(fns) != 1:
        raise ValueError(f"expected one function definition, found {len(fns)}")
    return fns[0]


def _statements(fn: ast.FunctionDef) -> list[ast.stmt]:
    body = list(fn.body)
    if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]                                   # the docstring is not code
    return body


def _dump(node: ast.AST | None) -> str | None:
    return None if node is None else ast.dump(node)


def recomposition_problems(ours: Callable, theirs: Callable, markers: Sequence[str]) -> list[str]:
    """`ours` (a re-composed function) against `theirs` (the vendored one it was composed from), statement for
    statement: our source with every line that carries a comment marker in `markers` (Q-47, Q-71) removed, parsed,
    against theirs parsed -- the name, the signature, the decorators, the return annotation, and every statement of
    the body after the docstring (`ast.dump`: comments and layout aside). Empty when they are the same code."""
    names = [str(m) for m in markers if str(m)]
    pat = re.compile(r"#\s*(?:" + "|".join(re.escape(m) for m in names) + r")\b") if names else None
    our_src = inspect.getsource(ours).replace("\r\n", "\n")
    kept = "\n".join(line for line in our_src.split("\n") if pat is None or not pat.search(line))
    try:
        a = _function_node(kept)
    except SyntaxError as exc:
        return [f"{ours.__qualname__} with its marked lines removed does not parse ({exc}): a marked addition is not "
                "whole statements"]
    b = _function_node(inspect.getsource(theirs).replace("\r\n", "\n"))
    out: list[str] = []
    if a.name != b.name:
        out.append(f"the name {a.name!r} against {b.name!r}")
    if _dump(a.args) != _dump(b.args):
        out.append("the signature differs once the marked keywords are removed")
    if [ast.dump(d) for d in a.decorator_list] != [ast.dump(d) for d in b.decorator_list]:
        out.append("the decorators differ")
    if _dump(a.returns) != _dump(b.returns):
        out.append("the return annotation differs")
    sa, sb = _statements(a), _statements(b)
    for i, (x, y) in enumerate(zip(sa, sb)):
        if ast.dump(x) != ast.dump(y):
            out.append(f"statement {i} of the body differs (ours at line {x.lineno} of the stripped text, the "
                       f"vendored at line {y.lineno} of its function)")
            break
    if len(sa) != len(sb):
        out.append(f"the body has {len(sa)} statements against the vendored {len(sb)}")
    return out


def campaign_recomposition_problems() -> list[str]:
    """`recomposition_problems` for this module's campaign against the vendored one (markers Q-71 and Q-70)."""
    return recomposition_problems(simulate_lockstep_campaign, _vl.simulate_lockstep_campaign, MARKERS)


def path_runner(path_reducer: Any, *, record_trades: bool, record_days: bool) -> Callable:
    """Q-70: the paths' runner for one campaign -- the vendored `_run_paths` without a reducer; with one (an
    `extended.place_records.PathReducer`), its runner: the vendored `_run_paths` re-composed so that every path runs
    with the ledger and day recorder on and is read where it ran (`extended.place_records._run_paths`), the caller's
    own `record_trades` and `record_days` deciding what the paths keep."""
    if path_reducer is None:
        return _run_paths
    from extended.place_records import PathReducer

    if not isinstance(path_reducer, PathReducer):
        raise TypeError(f"path_reducer must be an extended.place_records.PathReducer, got "
                        f"{type(path_reducer).__name__}")
    return path_reducer.runner(keep_trades=record_trades, keep_days=record_days)


def simulate_lockstep_campaign(
    protocol: Protocol,
    *,
    edge: float,
    seed: int,
    initial_bankroll: float,
    rules: Any | None = None,
    horizon_days: int = 504,
    n_paths: int = 500,
    subscription: float | None = None,
    billing_days: int | None = None,
    activation: float | None = None,
    payout_lag_days: int | None = None,
    payout_method: str = "aeropay",
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    max_concurrent_accounts: int | None = None,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    stop_buying_when_queued: bool = True,
    combine_max_days: int = 2000,
    funded_horizon_days: int = 504,
    draw_factories_for_path: Callable[[int], tuple] | None = None,
    record_trades: bool = False,
    require_verified_cap: bool = True,
    ledger: Any | None = None,
    conduct: ConductModel | None = None,
    record_days: bool = False,
    near_miss_frac: float = 0.2,
    reset_failed_combines: bool = False,
    reset_fee: float | None = None,
    risk_policy: Any = None,
    max_total_accounts: int | None = None,
    payout_timing: str = DEFAULT_PAYOUT_TIMING,
    wallet_for_path: Callable[[int], Any] | None = None,
    flip_for_path: Callable[[int], tuple] | None = None,
    funded_account_cls: type | None = None,
    household_closure: bool | None = None,
    focused_trader: FocusedTraderModel | None = None,
    purchase_budget: tuple[int, int] | None = None,
    workers: int = 1,
    pool: Any = None,
    memory_per_worker_gb: float | None = None,
    wallet_stop: float | None = None,
    pause_after_funded: int | None = None,
    seat_ramp: int | None = None,
    combine_account_cls: type | None = None,                                    # Q-71
    path_reducer: Any = None,                                                   # Q-70
    levers: Any = None,                                                         # Q-119
) -> tuple[CampaignSummary, list[LockstepPath]]:
    """The vendored `propedge.campaign.lockstep.simulate_lockstep_campaign` (its docstring holds every argument's
    meaning), plus `combine_account_cls`: the evaluation account's class on every path -- the vendored `CombineAccount`
    or a subclass of it (D-619) -- passed to every path (`simulate_lockstep_path`) only when given, and named in the
    summary's provenance (`combine_account_cls`) only when given. None runs the vendored campaign exactly.

    `path_reducer` (Q-70; `extended.place_records`): every path recorded and read where it ran, its record riding on
    the path handed back (`extended.place_records.RecordedPath`); the summary is the unrecorded campaign's. None runs
    the paths with the vendored runner.

    `levers` (Q-119; `extended.levers_path.Levers`): RD-03's options on every path, through the levers' path runner
    (refused with a path reducer). None: as before."""
    check_vendored_source()                               # Q-71: refused unless the vendored function is the pinned one
    # ---- from here to the end, the vendored body; its two additions are marked Q-71, the recorder's runner Q-70
    from propedge.contract.adapter import Rules

    check_payout_timing(payout_timing)
    rules = rules or Rules()
    subscription = float(rules.subscription if subscription is None else subscription)
    billing_days = int(rules.billing_days if billing_days is None else billing_days)
    activation = float(rules.activation if activation is None else activation)

    need_ledger = (max_concurrent_accounts is None and require_verified_cap) or (
        payout_lag_days is None
    )
    if need_ledger and ledger is None:
        from propedge.contract.rules import load_rules

        ledger = load_rules()
    if max_concurrent_accounts is None:
        if require_verified_cap:
            max_concurrent_accounts = int(ledger.value("max_active_funded_accounts"))
        else:
            max_concurrent_accounts = protocol.max_concurrent_accounts
    if payout_lag_days is None:
        from propedge.campaign.payout_method import payout_method_terms

        terms = payout_method_terms(payout_method, ledger=ledger)
        payout_lag_days = terms.lag_days
        lag_source = f"ledger {terms.lag_key} (article {terms.article_id})"
    else:
        lag_source = "explicit argument"

    path_kwargs = dict(
        edge=edge, rules=rules,
        initial_bankroll=initial_bankroll, horizon_days=horizon_days,
        max_concurrent_accounts=max_concurrent_accounts,
        subscription=subscription, billing_days=billing_days, activation=activation,
        payout_lag_days=int(payout_lag_days),
        max_concurrent_combines=max_concurrent_combines, reinvest=reinvest,
        max_attempts=max_attempts, stop_buying_when_queued=stop_buying_when_queued,
        activation_timing=activation_timing, combine_max_days=combine_max_days,
        funded_horizon_days=funded_horizon_days,
        record_trades=record_trades, conduct=conduct,
        record_days=record_days, near_miss_frac=near_miss_frac,
        reset_failed_combines=reset_failed_combines, reset_fee=reset_fee,
        risk_policy=risk_policy, max_total_accounts=max_total_accounts,
        payout_timing=payout_timing,
        funded_account_cls=funded_account_cls,                                  # R7
        household_closure=household_closure,                                    # R7 (multi-firm D-30)
    )
    if focused_trader is not None:                        # D-495 (4): passed only when given
        path_kwargs["focused_trader"] = focused_trader
    if purchase_budget is not None:                       # D-501: passed only when given
        budget = check_purchase_budget(purchase_budget)
        path_kwargs["purchase_budget"] = budget
    entry: dict[str, Any] = {}                            # D-630: each passed only when given
    if wallet_stop is not None:
        entry["wallet_stop"] = check_wallet_stop(wallet_stop)
    if pause_after_funded is not None:
        entry["pause_after_funded"] = check_pause_after_funded(pause_after_funded)
    if seat_ramp is not None:
        entry["seat_ramp"] = check_seat_ramp(seat_ramp, max_total_accounts)
    path_kwargs.update(entry)
    if combine_account_cls is not None:                   # Q-71: passed only when given, so None is the vendored call
        path_kwargs["combine_account_cls"] = combine_account_cls                                # Q-71
    if levers is not None:                                # Q-119: RD-03's levers on every path (A-3), only when given
        from extended import levers_path as _lp                                 # Q-119
        path_kwargs["levers"] = _lp.check_levers(levers)                        # Q-119
    seeds = path_seeds(seed, n_paths)
    _run_paths = path_runner(path_reducer, record_trades=record_trades, record_days=record_days)  # noqa: F811  # Q-70
    if levers is not None:                                                      # Q-119: the paths through A-1's path
        _run_paths = _lp.lever_runner(levers, _run_paths, path_reducer)         # noqa: F811  # Q-119
    results = _run_paths(protocol, path_kwargs, seeds, draw_factories_for_path, flip_for_path, wallet_for_path,
                         workers=workers, pool=pool, memory_per_worker_gb=memory_per_worker_gb)

    provenance_extra: dict[str, Any] = {}
    if funded_account_cls is not None:                    # R7: named only when given, so Topstep's provenance is as before
        provenance_extra["funded_account_cls"] = f"{funded_account_cls.__module__}.{funded_account_cls.__qualname__}"
        if hasattr(funded_account_cls, "HOUSEHOLD_CLOSES_AT_LIVE"):      # R7 (multi-firm D-30): the reading taken
            provenance_extra["household_closure"] = bool(
                funded_account_cls.HOUSEHOLD_CLOSES_AT_LIVE if household_closure is None else household_closure)
    if focused_trader is not None:                        # D-495 (4): named only when given
        provenance_extra["focused_trader"] = {"decision": "D-495", **focused_trader.as_dict()}
    if purchase_budget is not None:                       # D-501: named only when given
        provenance_extra["purchase_budget"] = {"decision": "D-501", "k": budget[0], "window_days": budget[1]}
    for name, value in entry.items():                     # D-630: named only when given
        provenance_extra[name] = {"decision": "D-630", "value": value}
    if combine_account_cls is not None:                   # Q-71: named only when given, as funded_account_cls is
        provenance_extra["combine_account_cls"] = (                                            # Q-71
            f"{combine_account_cls.__module__}.{combine_account_cls.__qualname__}")                 # Q-71
    if levers is not None:                                # Q-119: named only when given                # Q-119
        provenance_extra["levers"] = {"decision": "RD-03 A-1", **levers.as_dict()}                  # Q-119
    summary = summarise_paths(
        [r.path for r in results],
        protocol=protocol, edge=edge, seed=seed, initial_bankroll=initial_bankroll,
        horizon_days=horizon_days, n_paths=n_paths, payout_lag_days=int(payout_lag_days),
        payout_schedule="exact (lockstep, trade-level)",
        max_concurrent_accounts=int(max_concurrent_accounts),
        payout_method=payout_method, activation_timing=activation_timing,
        provenance={
            "simulation": "propedge.campaign.lockstep.simulate_lockstep_campaign",
            "subscription": subscription,
            "billing_days": billing_days,
            "activation": activation,
            "activation_timing": activation_timing,
            "payout_method": payout_method,
            "payout_lag_source": lag_source,
            "reinvest": reinvest,
            "max_concurrent_combines": max_concurrent_combines,
            "max_attempts": max_attempts,
            "combine_max_days": combine_max_days,
            "funded_horizon_days": funded_horizon_days,
            "conduct": None if conduct is None else {"decision": "D-145", **conduct.as_dict()},
            "payout_timing": payout_timing,
            "payout_timing_note": PAYOUT_TIMING_NOTES[payout_timing],
            "draws": (
                "independent binary draws per account (validation limit)"
                if draw_factories_for_path is None
                else "caller-supplied draw factories"
            ),
            "note": (
                "Every account is stepped through each calendar day by its own state machine "
                "(Combine and funded rules as the vendored engine applies them). With "
                "independent streams this reproduces reinvest.simulate_path exactly "
                "(tests/test_lockstep.py)."
            ),
            **provenance_extra,
        },
    )
    return summary, results


__all__ = ["VENDORED_CAMPAIGN_SHA256", "MARKER", "MARKERS", "source_sha256", "vendored_campaign_sha256",
           "check_vendored_source", "recomposition_problems", "campaign_recomposition_problems", "path_runner",
           "simulate_lockstep_campaign"]
