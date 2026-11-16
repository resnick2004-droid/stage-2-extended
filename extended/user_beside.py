"""Q-17 (E-007 (e)): the user's replay under the firm's responses -- an adapter over Stage 2's vendored U1 replay
(`vendor/stage2/scripts/user_journey.py`, `customer_slices.replay`), never an edit of it.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import user_beside as B
    outs = B.run_starts("p14", "verdict", B.BY_NAME["denial_25"], job, starts, workers=1)

**Why an adapter.** The vendored replay hands the engine `ConductModel(rtp=..., enforcement_p=0.0)`
(`customer_slices.py:232`), so every U1 reading is at 0 % denial with the placement off and without the Focused Trader
Program (Stage 2 D-234, D-289; the Phase 0 audit C's C-1, M-2 and its proposal E1). Here the same engine call is made
with one response switched on, and nothing else changed:

* **`off`** -- the vendored call exactly (`ConductModel(rtp=False, enforcement_p=0.0)`): the identity arm. With every
  response off this adapter reproduces `results/user_journey.csv`'s `start` rows (`identity/user_beside_identity.py`).
* **`denial_10/25/50`** -- the engine's tier-3 model (`lockstep.ConductModel`, `lockstep.py:1922-1936`): a payout
  requested while the campaign shows the stacking pattern (two or more MLL breaches in the last 21 sessions) is
  exposed; an exposed payout is denied, and that account closed, when its uniform from the path's enforcement stream
  falls below p. Seeded (below).
* **`forfeit_10/25/50`** -- all-accounts forfeiture (Terms of Use s.27 as the audit read it: a denied payout forfeits
  withdrawals from every account on the profile): the same coin decides the denied payout; at that close every live
  account ends, no pass waiting is activated, nothing more is bought (the engine's own household mechanism, R7,
  raised by the denied account: `ForfeitFundedAccount`), and every payout whose cash would arrive after that close is
  denied (`forfeit_view`: the engine books arrivals regardless of the account, so they are taken out of the path's
  record afterwards -- cash, totals, the campaign's pay days and each account's payout lists). Cash that arrives on the
  forfeiture close itself is kept (the engine books arrivals after that day's requests and denials, as the Focused
  Trader Corrective Path's denial of pending payouts treats them).
* **`rtp`** -- the Responsible Trading Program's placement on, exactly as the gate's `placement_on` arm runs it
  (`gate.py:286`: `ConductModel(rtp=True, enforcement_p=0.0)`, `rtp_warnings` 0, the strictest reading); **`rtp_w3`**
  -- the softer declared reading the audit proposed (three trigger days answered by a warning first, D-220).
* **`ftp_*`** -- the binding Focused Trader models (Stage 2 D-495, D-497, D-498): `ftp_sweep.models()`' sixteen less
  those that cannot place under the design's purchase budget (`a3_brk30_cb20.model_can_bind`, D-512 (4)): purchases
  >= 10 and >= 20 in 21 sessions, funded accounts lost >= 3, 5, 10 in 21 sessions, on the Slowdown and the Corrective
  path -- ten models, checked against the vendored grid at run time.

**Seeds** (the brief's block 20261920-20261929; only the first is used here). The engine draws one uniform per
exposed payout from `child_seed(path seed, 9, 0)`. The vendored replay passes every start the same campaign seed, so
every start would share one uniform sequence; here each start's path seed is `lockstep.child_seed(DENIAL_SEED, 0,
start_day)` (`start_seed`) -- independent across starts, the same for a start's long and exact-length runs and for
every response, design and arm (common random numbers: the ladder's levels and the forfeiture arms share them, as the
engine intends). The shared day draws keep the replay's own seed. The path seed drives nothing else in a replay
without a flip stream (`lockstep.py:1417, 1436, 1496`); a design with one is refused.

**The exact-length runs** (U1's runs of exactly 21, 63, 90 and 126 sessions, read where their event days differ from
the long replay's): on every start of `off`; for the other responses on every `EXACT_EVERY`-th start index, as a
check whose differing count is reported (U1 found none at 0 %; they are over half of a start's cost).

Everything a start reads is made by the vendored functions: `user_journey._one_start` (the record, the exact-length
runs, the checks of every run's payouts and fees against the engine's totals), `customer_journey.single_events`,
`customer_slices.slice_measures`, `user_journey.payout_arrivals`. Added per start: its daily path measures
(`extended.user_measures.daily`, from the long replay's close-by-close cash) and what the response did.

**Q-76 (E-046 (3)): a declared funded-account class.** `run_starts(..., funded_account_cls=C)` (and
`response_args(..., funded_account_cls=C)`) replays a design whose funded accounts are `C` -- the vendored
`FundedAccount` or a subclass of it, the keyword named after `extended.gate.run_gate`'s (Q-47) and checked by the
gate's own check (`TypeError` for anything else, and, at more than one worker, for a class that cannot pickle; it
travels to the workers in the task). With the keyword absent (None) every behaviour is as before Q-76: the same tasks,
the same replay arguments, the same outputs bit for bit, and `base_problems` still refuses a path that already carries
`funded_account_cls` -- with the keyword given too: the keyword is the one way in. When given:

* the class is passed to every replay's path (`funded_account_cls`) as given -- except under the next two kinds of
  response;
* **forfeiture** composes over it: `forfeit_class(C)` is `C` with the forfeiture's household rule raised by a denial
  (the default `ForfeitFundedAccount`'s three members over `C`); refused (`ValueError`) for a class with a household
  rule of its own (`HOUSEHOLD_CLOSES_AT_LIVE` or `closes_household`), whose reading the forfeiture would override;
* **the Focused Trader models** are refused (`ValueError`) for any class but the vendored `FundedAccount` itself -- the
  engine's own rule (`simulate_lockstep_path`: "the Focused Trader Program is Topstep's ... it applies to Topstep's
  FundedAccount only"), raised here before any start runs;
* every start's output gains one last key, `funded_account_cls` (the class's module and name, `class_name`), and
  `class_parameters(C)` is the entry a runner puts in its result's parameters (empty when absent): named only when
  given, as the engine names a class in its provenance only when given.

Its identities: `tests/q76_synthetic.py` (absent = the adapter before Q-76 bit for bit on all 19 responses; a
pass-through class equal apart from naming; a probe class's documented effect; the refusals) and
`identity/user_beside_identity.py --funded-cls` (U1's start rows at the default and with the gate's pass-through class).
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

#: the brief's seed block (Q-17 / Q-20): 20261920-20261929; this module uses the first
SEED_BLOCK = tuple(range(20261920, 20261930))
DENIAL_SEED = SEED_BLOCK[0]
#: the child-seed kind of a start's path seed (`lockstep.child_seed(DENIAL_SEED, START_KIND, start_day)`)
START_KIND = 0
DENIAL_LEVELS = (0.10, 0.25, 0.50)
FTP_WINDOW = 21
#: the binding Focused Trader models under a purchase budget of 20 in 21 sessions (D-512 (4)), path-major, purchases
#: before losses -- `ftp_sweep.models()` filtered by `a3_brk30_cb20.model_can_bind` (checked at run time)
FTP_BINDING = (("slowdown", "combine_purchases", 10), ("slowdown", "combine_purchases", 20),
               ("slowdown", "funded_lost", 3), ("slowdown", "funded_lost", 5), ("slowdown", "funded_lost", 10),
               ("corrective", "combine_purchases", 10), ("corrective", "combine_purchases", 20),
               ("corrective", "funded_lost", 3), ("corrective", "funded_lost", 5), ("corrective", "funded_lost", 10))
FTP_BUDGET = (20, 21)
#: the exact-length runs (U1's 21, 63, 90, 126 sessions; D-620 (3)(f)) are made on every start of the `off` arm (the
#: identity needs them) and, for every other response, on the starts whose index is a multiple of this -- a check, its
#: count of differing runs reported: U1 found none differing at 0 % on any configuration and arm
#: (`user_journey.csv`'s manifest, `starts_read_from_an_exact_run`), and they are over half of a start's cost
EXACT_EVERY = 21


@dataclass(frozen=True)
class Response:
    """One firm response, or none (`off`)."""

    name: str
    kind: str                      # off | denial | forfeit | rtp | ftp
    enforcement_p: float = 0.0
    rtp: bool = False
    rtp_warnings: int = 0
    ftp_path: str | None = None
    ftp_measure: str | None = None
    ftp_threshold: int | None = None

    @property
    def ftp_label(self) -> str:
        if self.kind != "ftp":
            return ""
        short = "purchases" if self.ftp_measure == "combine_purchases" else "lost"
        return f"{self.ftp_path} {short}>={int(self.ftp_threshold)}/{FTP_WINDOW}d"

    def as_dict(self) -> dict[str, Any]:
        return {**dataclasses.asdict(self), "ftp_label": self.ftp_label}


def _pct(p: float) -> int:
    return int(round(100 * p))


RESPONSES: tuple[Response, ...] = (
    Response("off", "off"),
    *(Response(f"denial_{_pct(p)}", "denial", enforcement_p=p) for p in DENIAL_LEVELS),
    *(Response(f"forfeit_{_pct(p)}", "forfeit", enforcement_p=p) for p in DENIAL_LEVELS),
    Response("rtp", "rtp", rtp=True),
    Response("rtp_w3", "rtp", rtp=True, rtp_warnings=3),
    *(Response(f"ftp_{path}_{'purchases' if m == 'combine_purchases' else 'lost'}_{t}", "ftp", ftp_path=path,
               ftp_measure=m, ftp_threshold=t) for path, m, t in FTP_BINDING),
)
BY_NAME = {r.name: r for r in RESPONSES}
if len(BY_NAME) != len(RESPONSES):
    raise RuntimeError("two responses share a name")


# ------------------------------------------------------------------------------------------------ the engine call


def start_seed(start_day: int, base: int = DENIAL_SEED) -> int:
    """A start's path seed: `lockstep.child_seed(base, START_KIND, start_day)`."""
    from propedge.campaign.lockstep import child_seed

    return int(child_seed(int(base), START_KIND, int(start_day)))


_FORFEIT_CLS: list[type] = []
#: Q-76: the forfeiture composed over a declared class, one a class (made in the process that replays, never pickled)
_FORFEIT_OVER: dict[type, type] = {}


def forfeit_class(base: type | None = None) -> type:
    """`ForfeitFundedAccount`: Topstep's funded account (the vendored `FundedAccount`, unchanged) with the engine's
    household rule (R7) raised by a tier-3 denial -- so the denied account's close ends every other live account, no
    pass waiting is activated and the path buys nothing more (`lockstep.py:1955-1975`, 2043-2046, 2131).

    Q-76: with `base` (a declared funded-account class) the same three members over `base` instead (`forfeit_over`);
    None is the class above, unchanged."""
    if base is not None:
        return forfeit_over(base)
    if not _FORFEIT_CLS:
        from propedge.campaign.lockstep import FundedAccount

        class ForfeitFundedAccount(FundedAccount):
            """A denied payout forfeits the profile (Terms of Use s.27 as audit C read it)."""

            HOUSEHOLD_CLOSES_AT_LIVE = True
            closes_household = False

            def deny_last_payout(self, calendar_day: int) -> None:
                super().deny_last_payout(calendar_day)
                self.closes_household = True

        _FORFEIT_CLS.append(ForfeitFundedAccount)
    return _FORFEIT_CLS[0]


# ------------------------------------------------------------------------------------------------ Q-76: the class


def check_funded_account_cls(funded_account_cls: type | None, workers: int = 1) -> None:
    """Q-76: the gate's check (`extended.gate.check_funded_account_cls`, Q-47): None passes; a class that is not the
    vendored `FundedAccount` or a subclass of it is refused (`TypeError`), and so, at more than one worker, is one that
    cannot pickle (the class travels to the workers in the task; one defined inside a function cannot). Anything that
    is not a class is refused first by its type's name alone (the gate's message shows the object's `repr`, which an
    object can fail to make -- a half-built dataclass instance raises `AttributeError` there)."""
    if funded_account_cls is None:
        return
    if not isinstance(funded_account_cls, type):
        raise TypeError("funded_account_cls must be the vendored FundedAccount or a subclass of it (a class), got a "
                        f"{type(funded_account_cls).__name__}")
    from extended.gate import check_funded_account_cls as gate_check

    gate_check(funded_account_cls, int(workers))


def class_name(funded_account_cls: type) -> str:
    """The class's module and name: the gate's `class_name`, as it names a class on its rows (and the engine in its
    provenance)."""
    from extended.gate import class_name as gate_name

    return gate_name(funded_account_cls)


def class_parameters(funded_account_cls: type | None) -> dict[str, Any]:
    """Q-76: the entry naming the class in a result's parameters (and provenance) -- `{"funded_account_cls": <its
    module and name>}` when given, empty when absent (named only when given, as the engine does)."""
    return {} if funded_account_cls is None else {"funded_account_cls": class_name(funded_account_cls)}


def own_household_rule(funded_account_cls: type) -> bool:
    """Whether a funded class carries a household rule of its own (`HOUSEHOLD_CLOSES_AT_LIVE`, or `closes_household`
    raised by its own accounts) -- which the forfeiture's rule would override."""
    return hasattr(funded_account_cls, "HOUSEHOLD_CLOSES_AT_LIVE") or hasattr(funded_account_cls, "closes_household")


def forfeit_over(base: type) -> type:
    """The forfeiture over a declared class: `base` with `ForfeitFundedAccount`'s three members (the household rule
    declared on, the account's flag off, raised by `deny_last_payout` after `base`'s own). One a class, cached, made
    where the replay runs (inside the task), so it never has to pickle. Refused for a class that is not a
    `FundedAccount` subclass (`TypeError`) and for one with a household rule of its own (`ValueError`): the forfeiture
    would override that rule's reading, a combination no declaration has made."""
    check_funded_account_cls(base, 1)
    if own_household_rule(base):
        raise ValueError(f"REFUSED (Q-76): {class_name(base)} has a household rule of its own; all-accounts forfeiture "
                         "over it would override that rule's reading -- not declared")
    if base not in _FORFEIT_OVER:

        class ForfeitFundedAccount(base):
            """A denied payout forfeits the profile (Terms of Use s.27 as audit C read it), over a declared class."""

            HOUSEHOLD_CLOSES_AT_LIVE = True
            closes_household = False

            def deny_last_payout(self, calendar_day: int) -> None:
                super().deny_last_payout(calendar_day)
                self.closes_household = True

        ForfeitFundedAccount.__qualname__ = f"forfeit_over.<locals>.ForfeitFundedAccount[{class_name(base)}]"
        _FORFEIT_OVER[base] = ForfeitFundedAccount
    return _FORFEIT_OVER[base]


def class_problems(funded_account_cls: type | None, resp: Response) -> list[str]:
    """Q-76: why a response cannot run with the declared class (empty when absent): a Focused Trader model with any
    class but the vendored `FundedAccount` (the engine's own rule, `simulate_lockstep_path`), the forfeiture over a
    class with a household rule of its own."""
    if funded_account_cls is None:
        return []
    from propedge.campaign.lockstep import FundedAccount

    out = []
    if resp.kind == "ftp" and funded_account_cls is not FundedAccount:
        out.append(f"{resp.name}: the Focused Trader Program is Topstep's and the engine applies it to the vendored "
                   f"FundedAccount only (simulate_lockstep_path), not {class_name(funded_account_cls)}")
    if resp.kind == "forfeit" and own_household_rule(funded_account_cls):
        out.append(f"{resp.name}: {class_name(funded_account_cls)} has a household rule of its own; all-accounts "
                   "forfeiture over it would override that rule's reading -- not declared")
    return out


def check_class_response(funded_account_cls: type | None, resp: Response, workers: int = 1) -> None:
    """Q-76: the class checked (`TypeError`), then against the response (`ValueError`); nothing when absent."""
    if funded_account_cls is None:
        return
    check_funded_account_cls(funded_account_cls, int(workers))
    bad = class_problems(funded_account_cls, resp)
    if bad:
        raise ValueError("REFUSED (Q-76): " + "; ".join(bad))


def base_problems(args: dict[str, Any]) -> list[str]:
    """Why a design's replay arguments are not the vendored replay's 0 %, placement-off call this adapter changes."""
    from propedge.campaign.lockstep import ConductModel

    out = []
    c = args["path"].get("conduct")
    if c != ConductModel(rtp=False, enforcement_p=0.0):
        out.append(f"the replay's conduct is {c!r}, not ConductModel(rtp=False, enforcement_p=0.0)")
    for k in ("focused_trader", "funded_account_cls", "household_closure", "seed", "horizon_days"):
        if k in args["path"]:
            out.append(f"the replay's path arguments already carry {k!r}")
    if args["draws"].get("flip") is not None:
        out.append("the design has a flip stream: its path seed would drive the flips' direction, not only the "
                   "enforcement stream")
    return out


def response_args(args: dict[str, Any], resp: Response, funded_account_cls: type | None = None) -> dict[str, Any]:
    """The replay's arguments (`customer_slices.engine_args`) with one response switched on; refuses arguments that are
    not the vendored 0 %, placement-off call. Q-76: `funded_account_cls` (default None: as before) is the declared
    funded-account class, checked (`check_class_response`) and put on the path -- for the forfeiture, composed
    (`forfeit_class(funded_account_cls)`)."""
    from propedge.campaign.lockstep import ConductModel, FocusedTraderModel

    bad = base_problems(args)
    if bad:
        raise ValueError("REFUSED (Q-17): " + "; ".join(bad))
    check_class_response(funded_account_cls, resp)                              # Q-76: nothing when absent
    path = dict(args["path"])
    path["conduct"] = ConductModel(rtp=bool(resp.rtp), enforcement_p=float(resp.enforcement_p),
                                   rtp_warnings=int(resp.rtp_warnings))
    if resp.kind == "ftp":
        kw = {"combine_purchases": int(resp.ftp_threshold)} if resp.ftp_measure == "combine_purchases" else \
            {"funded_lost": int(resp.ftp_threshold)}
        path["focused_trader"] = FocusedTraderModel(path=str(resp.ftp_path), window_days=FTP_WINDOW, **kw)
    elif resp.kind == "forfeit":
        path["funded_account_cls"] = forfeit_class(funded_account_cls)          # Q-76: None -> the default, as before
        path["household_closure"] = True
    elif resp.kind not in ("off", "denial", "rtp"):
        raise ValueError(f"unknown response kind {resp.kind!r}")
    if funded_account_cls is not None and resp.kind != "forfeit":               # Q-76: on the path only when given
        path["funded_account_cls"] = funded_account_cls
    return {**args, "path": path}


def replay(blocks: Sequence[Any], args: dict[str, Any], path_seed: int):
    """`customer_slices.replay(blocks, args)` with the path's own seed `path_seed` (the shared day draws keep
    `args["seed"]`): the as-happened replay of every block from a fresh start."""
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    n = len(blocks)
    sd = SharedDayDraws({0: list(blocks)}, seed=args["seed"], replay=True, **args["draws"])
    return simulate_lockstep_path(args["draws"]["protocol"], seed=int(path_seed), horizon_days=n + 1, **args["path"],
                                  **sd.lockstep_kwargs())


def binding_ftp(budget: Any) -> list[tuple[str, str, int]]:
    """The vendored grid's models that can place under `budget` (D-512 (4)), as (path, measure, threshold)."""
    import a3_brk30_cb20 as C
    import ftp_sweep as fs

    out = []
    for m in fs.models():
        if not C.model_can_bind(m, tuple(budget)):
            continue
        if m.combine_purchases is not None:
            out.append((m.path, "combine_purchases", int(m.combine_purchases)))
        else:
            out.append((m.path, "funded_lost", int(m.funded_lost)))
        if int(m.window_days) != FTP_WINDOW:
            raise ValueError(f"the vendored grid's window is {m.window_days}, not {FTP_WINDOW}")
    return out


# ------------------------------------------------------------------------------------------------ forfeiture


def forfeit_view(lp: Any, lag: int) -> tuple[Any, dict[str, Any]]:
    """The forfeiture arm's path: the engine's run with every payout whose cash would arrive after the forfeiture close
    taken out -- from the cash closes (each from its arrival day on), the total payouts, the campaign's pay days and
    each funded record's payout lists. (The path itself, unchanged, when no payout was denied.) Returns (the path, what
    was forfeited)."""
    closed = int((lp.household or {}).get("closed_on", -1))
    info = {"forfeit_day": float(closed) if closed >= 0 else float("nan"), "cash_forfeited": 0.0,
            "payouts_forfeited": 0}
    if closed < 0:
        return lp, info
    cash = np.asarray(lp.path.cash_series, float).copy()
    last = len(cash) - 1
    funded, gone = [], []
    for f in lp.funded:
        keep_d, keep_c = [], []
        for r, c in zip(f.payout_days, f.payout_cash):
            arrival = int(f.activation_day) + 1 + int(r) + int(lag)
            if arrival > closed:
                gone.append((arrival, float(c)))
            else:
                keep_d.append(r)
                keep_c.append(c)
        funded.append(dataclasses.replace(f, payout_days=tuple(keep_d), payout_cash=tuple(keep_c),
                                          n_payouts=len(keep_d)) if len(keep_d) != len(f.payout_days) else f)
    days = []
    if lp.path.days_to_first_payout is not None:
        days = [int(lp.path.days_to_first_payout)]
        for g in lp.path.payout_gaps:
            days.append(days[-1] + int(g))
    removed = 0.0
    for a, c in sorted(gone):
        if a <= last:
            cash[a:] -= c
            removed += c
            days.remove(a)                       # the engine booked this arrival on that campaign day
            info["payouts_forfeited"] += 1
            info["cash_forfeited"] += c
    if any(d > closed for d in days):
        raise RuntimeError("an arrival after the forfeiture close is left in the campaign's pay days")
    path = dataclasses.replace(lp.path, cash_series=cash, final_cash=float(cash[-1]),
                               total_payouts=float(lp.path.total_payouts) - removed,
                               days_to_first_payout=days[0] if days else None,
                               payout_gaps=tuple(int(b - a) for a, b in zip(days, days[1:])))
    return dataclasses.replace(lp, path=path, funded=tuple(funded)), info


# ------------------------------------------------------------------------------------------------ one start


def response_record(lp: Any, resp: Response, info: dict[str, Any] | None = None) -> dict[str, Any]:
    """What the response did on a start's long replay: the payouts requested, exposed and denied (tier 3); the first
    denial's close; the placement's close (RTP, FTP); the forfeiture's close and the cash it took."""
    c = dict(lp.conduct or {})
    ftp = dict(lp.focused_trader or {})
    denied_days = [int(f.ended_on) for f in lp.funded if int(getattr(f, "denied", 0)) > 0 and f.ended_on is not None]
    out = {"payouts_requested": float(c.get("payouts_requested", np.nan)),
           "payouts_exposed": float(c.get("payouts_exposed", np.nan)),
           "payouts_denied": float(c.get("payouts_denied", np.nan)),
           "first_denial_day": float(min(denied_days)) if denied_days else float("nan"),
           "rtp_placed_day": float(c["rtp_placed_day"]) if c.get("rtp_placed_day", -1) >= 0 else float("nan"),
           "ftp_placed_day": float(ftp["first_placed_day"]) if ftp.get("first_placed_day", -1) >= 0 else float("nan"),
           "ftp_payouts_denied": float(ftp.get("payouts_denied", 0)) if ftp else float("nan"),
           "forfeit_day": float("nan"), "cash_forfeited": float("nan"), "payouts_forfeited": float("nan")}
    if info is not None:
        out.update({k: float(v) for k, v in info.items()})
    day = {"off": float("nan"), "denial": out["first_denial_day"], "forfeit": out["forfeit_day"],
           "rtp": out["rtp_placed_day"], "ftp": out["ftp_placed_day"]}[resp.kind]
    out["response_day"] = day
    return out


def _task(task: tuple) -> list[dict[str, Any]]:
    """(design, arm, response name, blocks, dates, args, starts, exact_every[, funded_account_cls]) -> each start's
    output: the vendored `user_journey._one_start` on this adapter's runs (long and exact-length), with the start's
    daily path measures and what the response did. The heavy parts of `_one_start`'s output (D-518's side) are
    dropped. Q-76: the ninth item, present only when a class is declared, is that class; each output then names it
    (its last key, `funded_account_cls`)."""
    import warnings

    import customer_journey as CJ
    import customer_slices as cs
    import user_journey as UJ

    from extended import user_measures as M
    from propedge.research import user_journey as U

    warnings.filterwarnings("ignore")
    design, arm, rname, blocks, dates, args, starts, exact_every = task[:8]
    cls = task[8] if len(task) > 8 else None                                    # Q-76
    named = class_parameters(cls)                                               # Q-76: empty when absent
    resp = BY_NAME[rname]
    a = response_args(args, resp) if cls is None else response_args(args, resp, cls)
    sub = float(args["path"]["subscription"])
    lag = int(args["path"]["payout_lag_days"])
    n = len(blocks)

    def run(s: int, h: int):
        lp = replay(blocks[s:s + h], a, start_seed(s))
        if resp.kind == "forfeit":
            return forfeit_view(lp, lag)
        return lp, None

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        long_run, info = run(s, L)
        if len(long_run.path.cash_series) != L + 1:
            raise RuntimeError(f"{design} {arm} {rname} start {s}: {len(long_run.path.cash_series)} closes, not {L + 1}")
        mine = long_record(s, dates[s], long_run, pay, totals)
        if int(s) % int(exact_every) == 0:
            exact = {h: run(s, h)[0] for h in U.EXACT if h < L}
            o = UJ._one_start(design, arm, s, dates[s], long_run, exact, sub, CJ.single_events, pay, totals,
                              cs.slice_measures)
            # the record composed here must be `_one_start`'s on every start both are made (refused otherwise)
            r0 = {k: v for k, v in o["rec"].items() if k != "alt"}
            same = not U.record_problems(r0, mine["rec"]) and r0["start_date"] == mine["rec"]["start_date"] and                 all(o[f"{k}_bad"] == mine[f"{k}_bad"] for k in ("pay", "cash", "fee"))
            o = {**o, "record_same": bool(same)}
        else:
            o = {**mine, "differs": [], "checked": [], "record_same": None}
        rel = np.asarray(long_run.path.cash_series, float) - float(long_run.path.initial_bankroll)
        out.append({"rec": o["rec"], "differs": o["differs"], "checked": o["checked"], "pay_bad": o["pay_bad"],
                    "cash_bad": o["cash_bad"], "fee_bad": o["fee_bad"], "record_same": o["record_same"],
                    "daily": M.daily(rel), "response": response_record(long_run, resp, info), "seed": start_seed(s),
                    **named})                                                   # Q-76: named only when given
    return out


def long_record(s: int, date: str, run: Any, pay, totals) -> dict[str, Any]:
    """A start's record from its long replay alone -- `user_journey._one_start`'s own `record` step (the vendored
    `customer_journey.single_events`, `user_journey.payout_arrivals`, `fees_paid` and `start_record`, composed as it
    composes them), with its three checks against the engine's totals; for a start whose exact-length runs are not
    made. `_task` holds it equal to `_one_start`'s on every start where both are made."""
    import customer_journey as CJ

    from propedge.research import user_journey as U

    cash, init, passes, funded, pays = CJ.single_events(run)
    obs = len(cash) - 1
    arr = pay(run, obs)
    fees, paid = totals(run)
    got = float(sum(c for _, c in arr))
    bad = {"pay_bad": int(sorted(d for d, _ in arr) != sorted(int(d) for d in pays)),
           "cash_bad": int(abs(got - float(paid)) > U.TOL),
           "fee_bad": int(abs(U.fees_paid(float(cash[-1]) - float(init), got) - float(fees)) > U.TOL)}
    return {"rec": {"start_day": int(s), "start_date": str(date), **U.start_record(cash, init, passes, funded, arr)},
            **bad}


def run_starts(design: str, arm: str, resp: Response, job: dict[str, Any], starts: Sequence[int], workers: int,
               chunk: int = 20, exact_every: int | None = None,
               funded_account_cls: type | None = None) -> list[dict[str, Any]]:
    """Every chosen start of one design, arm and response, in start order, across `customer_journey._pool_run`'s
    guarded pool (`workers`; 1 runs in this process). The exact-length runs on every start for `off`, on every
    `exact_every`-th start index otherwise (default `EXACT_EVERY`; 1: every start).

    Q-76: `funded_account_cls` (default None: every behaviour as before) is the design's declared funded-account class
    on every replay; checked, with the design's arguments, before any start runs (`TypeError` for a class that is not
    a `FundedAccount` subclass or, at more than one worker, cannot pickle; `ValueError` for a response it cannot run
    with, or a path already carrying a class); added to each task as its ninth item, and named on every start's
    output, only when given."""
    import customer_journey as CJ

    if job.get("engine") != "single":
        raise ValueError("Q-17 replays single-firm designs only")
    if funded_account_cls is not None:                                          # Q-76: refused before any start
        check_class_response(funded_account_cls, resp, int(workers))
        response_args(job["args"], resp, funded_account_cls)
    every = 1 if resp.kind == "off" else int(EXACT_EVERY if exact_every is None else exact_every)
    chunks = [list(starts[j:j + chunk]) for j in range(0, len(starts), chunk)]
    tasks = [(design, arm, resp.name, job["blocks"], job["dates"], job["args"], c, every) for c in chunks]
    if funded_account_cls is not None:                                          # Q-76: the ninth item, only when given
        tasks = [(*t, funded_account_cls) for t in tasks]
    res = CJ._pool_run(tasks, _task, int(workers), f"{design} {arm} {resp.name}")
    return [x for part in res for x in part]


__all__ = ["SEED_BLOCK", "DENIAL_SEED", "DENIAL_LEVELS", "EXACT_EVERY", "FTP_BINDING", "FTP_BUDGET", "Response",
           "RESPONSES", "BY_NAME", "start_seed", "forfeit_class", "base_problems", "response_args", "replay",
           "binding_ftp", "forfeit_view", "response_record", "long_record", "run_starts",
           "check_funded_account_cls", "class_name", "class_parameters", "own_household_rule", "forfeit_over",
           "class_problems", "check_class_response"]
