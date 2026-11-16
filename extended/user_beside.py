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

Everything a start reads is made by the vendored functions: `user_journey._one_start` (the record, the exact-length
runs, the checks of every run's payouts and fees against the engine's totals), `customer_journey.single_events`,
`customer_slices.slice_measures`, `user_journey.payout_arrivals`. Added per start: its daily path measures
(`extended.user_measures.daily`, from the long replay's close-by-close cash) and what the response did.
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


def forfeit_class() -> type:
    """`ForfeitFundedAccount`: Topstep's funded account (the vendored `FundedAccount`, unchanged) with the engine's
    household rule (R7) raised by a tier-3 denial -- so the denied account's close ends every other live account, no
    pass waiting is activated and the path buys nothing more (`lockstep.py:1955-1975`, 2043-2046, 2131)."""
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


def response_args(args: dict[str, Any], resp: Response) -> dict[str, Any]:
    """The replay's arguments (`customer_slices.engine_args`) with one response switched on; refuses arguments that are
    not the vendored 0 %, placement-off call."""
    from propedge.campaign.lockstep import ConductModel, FocusedTraderModel

    bad = base_problems(args)
    if bad:
        raise ValueError("REFUSED (Q-17): " + "; ".join(bad))
    path = dict(args["path"])
    path["conduct"] = ConductModel(rtp=bool(resp.rtp), enforcement_p=float(resp.enforcement_p),
                                   rtp_warnings=int(resp.rtp_warnings))
    if resp.kind == "ftp":
        kw = {"combine_purchases": int(resp.ftp_threshold)} if resp.ftp_measure == "combine_purchases" else \
            {"funded_lost": int(resp.ftp_threshold)}
        path["focused_trader"] = FocusedTraderModel(path=str(resp.ftp_path), window_days=FTP_WINDOW, **kw)
    elif resp.kind == "forfeit":
        path["funded_account_cls"] = forfeit_class()
        path["household_closure"] = True
    elif resp.kind not in ("off", "denial", "rtp"):
        raise ValueError(f"unknown response kind {resp.kind!r}")
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
    """(design, arm, response name, blocks, dates, args, starts) -> each start's output: the vendored
    `user_journey._one_start` on this adapter's runs (long and exact-length), with the start's daily path measures and
    what the response did. The heavy parts of `_one_start`'s output (D-518's side) are dropped."""
    import warnings

    import customer_journey as CJ
    import customer_slices as cs
    import user_journey as UJ

    from extended import user_measures as M
    from propedge.research import user_journey as U

    warnings.filterwarnings("ignore")
    design, arm, rname, blocks, dates, args, starts = task
    resp = BY_NAME[rname]
    a = response_args(args, resp)
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

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        long_run, info = run(s, L)
        if len(long_run.path.cash_series) != L + 1:
            raise RuntimeError(f"{design} {arm} {rname} start {s}: {len(long_run.path.cash_series)} closes, not {L + 1}")
        exact = {h: run(s, h)[0] for h in U.EXACT if h < L}
        o = UJ._one_start(design, arm, s, dates[s], long_run, exact, sub, CJ.single_events, pay,
                          lambda lp: (lp.path.total_fees, lp.path.total_payouts), cs.slice_measures)
        rel = np.asarray(long_run.path.cash_series, float) - float(long_run.path.initial_bankroll)
        out.append({"rec": o["rec"], "differs": o["differs"], "checked": o["checked"], "pay_bad": o["pay_bad"],
                    "cash_bad": o["cash_bad"], "fee_bad": o["fee_bad"], "daily": M.daily(rel),
                    "response": response_record(long_run, resp, info), "seed": start_seed(s)})
    return out


def run_starts(design: str, arm: str, resp: Response, job: dict[str, Any], starts: Sequence[int], workers: int,
               chunk: int = 20) -> list[dict[str, Any]]:
    """Every chosen start of one design, arm and response, in start order, across `customer_journey._pool_run`'s
    guarded pool (`workers`; 1 runs in this process)."""
    import customer_journey as CJ

    if job.get("engine") != "single":
        raise ValueError("Q-17 replays single-firm designs only")
    chunks = [list(starts[j:j + chunk]) for j in range(0, len(starts), chunk)]
    tasks = [(design, arm, resp.name, job["blocks"], job["dates"], job["args"], c) for c in chunks]
    res = CJ._pool_run(tasks, _task, int(workers), f"{design} {arm} {resp.name}")
    return [x for part in res for x in part]


__all__ = ["SEED_BLOCK", "DENIAL_SEED", "DENIAL_LEVELS", "FTP_BINDING", "FTP_BUDGET", "Response", "RESPONSES",
           "BY_NAME", "start_seed", "forfeit_class", "base_problems", "response_args", "replay", "binding_ftp",
           "forfeit_view", "response_record", "run_starts"]
