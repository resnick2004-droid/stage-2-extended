"""F-03 (family O): the waiting opening (section 5.4; build items 18.1 items 3 and 4) -- a funded-account class whose
fresh accounts take, during their first W live sessions, only an offer in the cell's state.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import opening_wait as OW
    spec = OW.WaitSpec.for_blocks("s1", blocks, in_state, W=5)     # the U1 replay: offers found by their block
    cls = OW.waiting_class(spec)                                   # a FundedAccount subclass, picklable to workers
    rec = OW.FamilyRecorder(offer_ids=ids)                         # Q-94's recorder, with the declined offers
    outs = user_beside.run_starts("p16", "verdict", B.BY_NAME["off"], job, starts, 2, funded_account_cls=cls,
                                  recorder=rec)
    opens = OW.openings(rec, "p16", "verdict", "off", population, W=5)

**The seam** (5.4, 18.1 item 3). Under P-16's `able` routing the router asks the draw registered under each account's
key whether it can take a trade (`TradeRouter.begin_day`, `TierSizedDraw.can_take`). The class's `__post_init__` wraps
the vendored draw in a `GateWrapper`, registers the wrapper under the draw's key in the router's place, and holds it
strongly (the router keeps draws weakly). The wrapper answers `can_take` with the vendored draw's answer **and** "the
offer is in state, or the account has traded, or its wait is over": waiting means `FundedAccount.trades == 0` and
`FundedAccount.days < W` at routing (the router routes before the session's accounts step, so `days` is the account's
live sessions before this one: "its first W live sessions" are those with `days` 0 to W - 1, T-5). Everything else the
router asks of the draw (`trade_dollars`, `can_stretch`) is the vendored draw's; `can_stretch` is gated the same way
(a waiting account never reaches the collect phase; the gate is there so no question can bypass it). The vendored
draw, its sizing and the account are never changed: with the state always on, or W = 0, nothing is declined and every
path is the vendored one (A1, T-5). Refused: a draw that is not the vendored `TierSizedDraw` or a router without
`able` routing (the gate would be silently open).

**Which offer.** `can_take` receives (historical day, trade index). On the gate (`mode="index"`) the historical day
indexes the campaign's blocks. On the U1 replay a start replays a window of the job's blocks, so its historical day
is the window's (`ReplayTable`): the wrapper finds the window's first session in the job by the window's content --
the sequence of its sessions' fingerprints (each session's from the arrays the draw holds of it, the log's dollar P&L
and risk, `TierSizedDraw._pnl`, `_risked`), matched whole against the job's sequence taken from its blocks when the
spec is built (`mode="blocks"`); found once a path (the path's router names it) and cached. A single session's
fingerprint can repeat (a few trades a day, each a stop or a target); a whole window's sequence matched at two places
is refused unless the state flags agree over the window (then the lookup cannot be wrong).

**The declined offers** (5.4; E-055 (4): a declined offer is not a trade, so no place recorder sees it). The wrapper
counts every offer it declines -- one the vendored draw would have taken, out of state, while waiting -- with the
account, the historical day, the trade index and the account's wait session. On the replay they ride out of each
start's long replay beside Q-94's records: `FamilyRecorder` is Q-94's `ReplayRecorder` whose reducer, right after the
recorded long replay ran, attaches that path's declined offers to the start's record (`declined`).

**Pickling.** The class carries its spec; a class made here reduces to `(waiting_class, (spec,))` by `copyreg`, so it
reaches a worker with its task and is rebuilt there (cached by the spec's digest). Q-76's forfeiture composes over it
(`user_beside.forfeit_class(cls)`, made where the replay runs); the class has no household rule of its own.
"""
from __future__ import annotations

import copyreg
import hashlib
import pickle
import weakref
from typing import Any, Mapping, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign.lockstep import FundedAccount  # noqa: E402

from extended import replay_records as RR  # noqa: E402

W_DECLARED = 5
OPENING = RR.OPENING
MODES = ("index", "blocks")
#: the most recent paths whose declined offers are kept in a process (only the latest is ever read)
KEEP_PATHS = 8


class AmbiguousOffer(ValueError):
    """A window's fingerprints match the job at two places that differ in state: an offer could be attributed to the
    wrong session."""


class GateOpen(RuntimeError):
    """The gate cannot work here: the router would never ask the wrapper (no `able` routing, or another draw)."""


def block_fingerprint(pnl: Any, risked: Any) -> str:
    """A session's fingerprint from the arrays a `TierSizedDraw` holds of it (float64 bytes, in trade order)."""
    a = np.ascontiguousarray(np.asarray(pnl, dtype=float))
    b = np.ascontiguousarray(np.asarray(risked, dtype=float))
    return hashlib.sha1(len(a).to_bytes(4, "little") + a.tobytes() + b.tobytes()).hexdigest()


class WaitSpec:
    """What a waiting class needs: its label, W, the mode and one in-state array a session (in each block's trade
    order; `None` = the state always on); in `blocks` mode one fingerprint a session of the job."""

    def __init__(self, label: str, W: int, mode: str, in_state: Sequence[np.ndarray] | None,
                 fingerprints: Sequence[str] | None = None):
        if mode not in MODES:
            raise ValueError(f"mode is one of {MODES}, not {mode!r}")
        if int(W) < 0:
            raise ValueError("W is a whole number of sessions, at least 0")
        self.label, self.W, self.mode = str(label), int(W), str(mode)
        self.always = in_state is None
        self.in_state = None if in_state is None else tuple(np.asarray(x, dtype=bool) for x in in_state)
        self.fingerprints = None if fingerprints is None else tuple(str(f) for f in fingerprints)
        self.positions: dict[str, list[int]] = {}
        if self.mode == "blocks" and not self.always:
            if self.fingerprints is None or len(self.fingerprints) != len(self.in_state):
                raise ValueError("a blocks-mode spec needs one fingerprint a session")
            for g, f in enumerate(self.fingerprints):
                self.positions.setdefault(f, []).append(g)
        d = hashlib.sha256(f"{self.label}|{self.W}|{self.mode}|{self.always}".encode())
        for x in self.in_state or ():
            d.update(len(x).to_bytes(4, "little") + np.packbits(x).tobytes())
        for f in self.fingerprints or ():
            d.update(f.encode())
        self.digest = d.hexdigest()

    @classmethod
    def for_blocks(cls, label: str, blocks: Sequence[Any], in_state: Sequence[np.ndarray] | None, W: int = W_DECLARED
                   ) -> "WaitSpec":
        """A U1 replay's spec: `in_state[h]` the flags of block h's trades; each block's fingerprint from its own
        `pnl` and `risked` (as `TierSizedDraw` reads them)."""
        if in_state is not None:
            if len(in_state) != len(blocks) or any(len(x) != len(b) for x, b in zip(in_state, blocks)):
                raise ValueError("one in-state flag a trade, block by block")
        fps = [block_fingerprint(b.pnl, b.risked) for b in blocks]
        return cls(label, W, "blocks", in_state, fps)

    @classmethod
    def for_index(cls, label: str, in_state: Sequence[np.ndarray] | None, W: int = W_DECLARED,
                  blocks: Sequence[Any] | None = None) -> "WaitSpec":
        """A gate campaign's spec: `in_state[h]` the flags of the campaign's block h (its historical day), checked
        against the campaign's `blocks` (one flag a trade, block by block) when given -- refused without them for a
        real state."""
        if in_state is not None:
            if blocks is None:
                raise ValueError("an index-mode spec with a state is checked against the campaign's blocks")
            if len(in_state) != len(blocks) or any(len(x) != len(b) for x, b in zip(in_state, blocks)):
                raise ValueError("one in-state flag a trade, block by block (the gate's blocks)")
        return cls(label, W, "index", in_state)

    def window_offset(self, window: Sequence[str]) -> int:
        """The job session of a window's first block: where the window's whole fingerprint sequence matches the
        job's; refused (`KeyError`) when nowhere, (`AmbiguousOffer`) at two places that differ in state."""
        L, fps = len(window), self.fingerprints
        hits = [s for s in self.positions.get(window[0], []) if s + L <= len(fps) and list(fps[s:s + L]) == list(window)]
        if not hits:
            raise KeyError("the replay's window is no window of the spec's sessions")
        for s in hits[1:]:
            if any(not np.array_equal(self.in_state[hits[0] + h], self.in_state[s + h]) for h in range(L)):
                raise AmbiguousOffer(f"the window matches sessions {hits[0]} and {s}, which differ in state")
        return hits[0]

    def __reduce__(self):
        return (WaitSpec, (self.label, self.W, self.mode, None if self.always else list(self.in_state),
                           None if self.fingerprints is None else list(self.fingerprints)))


# ------------------------------------------------------------------------------------------------ the declined offers

_PATHS: dict[int, dict[str, Any]] = {}


def _path_entry(router: Any) -> dict[str, Any]:
    key = id(router)
    e = _PATHS.get(key)
    if e is None or e["router"]() is not router:
        _PATHS.pop(key, None)
        e = {"router": weakref.ref(router), "wrappers": 0, "declined": []}
        _PATHS[key] = e
        while len(_PATHS) > KEEP_PATHS:
            _PATHS.pop(next(iter(_PATHS)))
    return e


def take_latest_declined(n_funded: int) -> tuple[list[tuple[int, int, int, int]], list[str]]:
    """The most recent path's declined offers, (account, historical day, trade index, wait session) each, and the
    problems of the attribution (the path made `n_funded` funded accounts; its wrappers must be as many). Clears the
    process's record."""
    problems: list[str] = []
    if n_funded == 0:
        _PATHS.clear()
        return [], problems
    if not _PATHS:
        return [], [f"no waiting account's wrapper was made on a path with {n_funded} funded accounts"]
    e = _PATHS[next(reversed(_PATHS))]
    if int(e["wrappers"]) != int(n_funded):
        problems.append(f"the latest path made {e['wrappers']} wrappers for {n_funded} funded accounts: its declined "
                        "offers cannot be attributed")
    out = list(e["declined"])
    _PATHS.clear()
    return out, problems


# ------------------------------------------------------------------------------------------------ the wrapper


class GateWrapper:
    """The gating answer over the vendored draw (the module docstring); held strongly by its account."""

    def __init__(self, inner: Any, account: FundedAccount, spec: WaitSpec):
        from propedge.campaign.sizing import TierSizedDraw

        if not isinstance(inner, TierSizedDraw):
            raise GateOpen(f"the waiting class gates the vendored TierSizedDraw's answer; this draw is a "
                           f"{type(inner).__name__}, which the router never asks")
        router = getattr(inner, "router", None)
        if router is None or not bool(getattr(router, "able", False)) or getattr(inner, "key", None) is None:
            raise GateOpen("the router does not route by `able` (D-318): it would never ask the wrapper, and the wait "
                           "would be silently open")
        self.inner = inner
        self.spec = spec
        self._account = weakref.ref(account)
        self.declined: list[tuple[int, int, int, int]] = []
        self._path = _path_entry(router)
        self._path["wrappers"] += 1
        router.register(inner.key, self)

    def __getattr__(self, name: str) -> Any:            # every other question is the vendored draw's
        if name == "inner" or (name.startswith("__") and name.endswith("__")):
            raise AttributeError(name)
        return getattr(self.inner, name)

    def _session(self, h: int) -> int:
        if self.spec.mode == "index":
            return int(h)
        off = self._path.get("offset")
        if off is None:
            window = [block_fingerprint(p, r) for p, r in zip(self.inner._pnl, self.inner._risked)]
            off = self._path["offset"] = self.spec.window_offset(window)
        return int(off) + int(h)

    def in_state(self, h: int, j: int) -> bool:
        if self.spec.always:
            return True
        flags = self.spec.in_state[self._session(h)]
        if not 0 <= int(j) < len(flags):
            raise IndexError(f"trade {j} of historical day {h} is outside the spec's flags ({len(flags)})")
        return bool(flags[int(j)])

    def waiting(self) -> bool:
        a = self._account()
        return a is not None and int(a.trades) == 0 and int(a.days) < int(self.spec.W)

    def _gate(self, ok: bool, h: int, j: int) -> bool:
        if not ok or not self.waiting() or self.in_state(h, j):
            return bool(ok)
        a = self._account()
        rec = (int(a.index), int(h), int(j), int(a.days))
        self.declined.append(rec)
        self._path["declined"].append(rec)
        return False

    def can_take(self, h: int, j: int, balance: float, floor: float) -> bool:
        return self._gate(self.inner.can_take(h, j, balance, floor), h, j)

    def can_stretch(self, h: int, j: int, *args: Any, **kw: Any) -> bool:
        return self._gate(self.inner.can_stretch(h, j, *args, **kw), h, j)


# ------------------------------------------------------------------------------------------------ the class


class _WaitingMeta(type):
    """The waiting classes' metaclass: a class made by `waiting_class` pickles as `(waiting_class, (spec,))`."""


def _reduce_class(cls: type):
    spec = cls.__dict__.get("_fo_spec")
    if spec is None:
        raise pickle.PicklingError(f"{cls.__qualname__} is not a class waiting_class made (a subclass of one, such as "
                                   "the forfeiture composed over it, is made where the replay runs and never pickles)")
    return (waiting_class, (spec,))


copyreg.pickle(_WaitingMeta, _reduce_class)

_CLASSES: dict[str, type] = {}


def _post_init(self) -> None:
    FundedAccount.__post_init__(self)
    self._fo_gate = GateWrapper(self.draw, self, _spec_of(type(self)))


def waiting_class(spec: WaitSpec) -> type:
    """The `FundedAccount` subclass for `spec` (one a spec digest, cached): its accounts gate their draw by the spec."""
    if not isinstance(spec, WaitSpec):
        raise TypeError("waiting_class takes a WaitSpec")
    cls = _CLASSES.get(spec.digest)
    if cls is None:
        ns = {"__module__": __name__, "__qualname__": f"WaitingFundedAccount[{spec.label}:W={spec.W}:{spec.digest[:12]}]",
              "__doc__": f"P-16's funded account waiting at most {spec.W} live sessions for {spec.label}'s state.",
              "_fo_spec": spec, "__post_init__": _post_init}
        cls = _WaitingMeta("WaitingFundedAccount", (FundedAccount,), ns)
        _CLASSES[spec.digest] = cls
    return cls


def _spec_of(cls: type) -> WaitSpec:
    for k in cls.__mro__:
        s = k.__dict__.get("_fo_spec")
        if s is not None:
            return s
    raise TypeError(f"{cls.__qualname__} carries no wait spec")


def spec_of(cls: type) -> WaitSpec:
    return _spec_of(cls)


# ------------------------------------------------------------------------------------------------ the recorder


class FamilyReducer(RR.ReplayReducer):
    """Q-94's reducer, plus the start's declined offers (attached right after its recorded long replay)."""

    @classmethod
    def from_base(cls, base: RR.ReplayReducer) -> "FamilyReducer":
        obj = cls.__new__(cls)
        obj.__dict__.update(base.__dict__)
        return obj

    def reduce(self, lp: Any, start_day: int, n_sessions: int, start_seed: int, start_date: str):
        declined, problems = take_latest_declined(len(lp.funded))
        plain, out = super().reduce(lp, start_day, n_sessions, start_seed, start_date)
        out["declined"] = [tuple(int(v) for v in x) for x in declined]
        out["problems"] = list(out["problems"]) + [f"{out['design']} start {start_day}: {p}" for p in problems]
        return plain, out


class FamilyRecorder(RR.ReplayRecorder):
    """Q-94's `ReplayRecorder` (it passes `user_beside`'s check), its reducer the family's."""

    def reducer(self, design: str, arm: str, resp: Any, job: dict[str, Any]) -> FamilyReducer:
        return FamilyReducer.from_base(super().reducer(design, arm, resp, job))

    def declined(self, design: str, arm: str, response: str) -> pd.DataFrame:
        """Every declined offer of the run: start, account, historical day (the start's window), trade index, wait
        session -- the gating wrapper's own count."""
        rows = [(int(r["start_day"]), *x) for r in self.per_start(design, arm, response) for x in r.get("declined", [])]
        return pd.DataFrame(rows, columns=["start_day", "account", "historical_day", "trade_index", "wait_session"])


# ------------------------------------------------------------------------------------------------ the joins


def openings(rec: RR.ReplayRecorder, design: str, arm: str, response: str, offers: pd.DataFrame | None = None,
             W: int = W_DECLARED) -> pd.DataFrame:
    """The run's funded openings (18.1 item 4: what Q-94 leaves to this family): each with its account's wait
    (`opening_session`), the **fallback** flag (`opening_session >= W`), and -- joined by the offer id
    (`opening_population.offer_id`, the recorder's `offer`) to `offers` (the population and labels: one row an offer,
    indexed by `offer`) -- its mark, hour, day kind and any further columns of `offers`. Refused when an opening's
    offer is not in `offers`."""
    t = rec.trades(design, arm, response)
    a = rec.accounts(design, arm, response)
    o = t[t["place"] == OPENING][["start_day", "start_date", "account", "day", "rel_day", "account_session",
                                  "historical_day", "trade_index", "date", "offer", "entry_t", "rr"]].copy()
    acc = a[["start_day", "account", "opening_session", "opening_day", "days", "activation_day"]]
    o = o.merge(acc, on=["start_day", "account"], how="left", validate="one_to_one")
    if (o["opening_session"].to_numpy() != o["account_session"].to_numpy()).any():
        raise ValueError("an opening's account row disagrees with its trade row (the wait)")
    o["fallback"] = o["opening_session"].astype(int) >= int(W)
    o["in_wait"] = ~o["fallback"]
    if offers is not None:
        missing = ~o["offer"].isin(offers.index)
        if missing.any():
            raise ValueError(f"{int(missing.sum())} openings' offers are not in the offer table (the join by id)")
        j = offers.loc[o["offer"].to_numpy()].reset_index(drop=True)
        o = pd.concat([o.reset_index(drop=True), j.drop(columns=[c for c in j.columns if c in o.columns])], axis=1)
    return o.reset_index(drop=True)


def censored(rec: RR.ReplayRecorder, design: str, arm: str, response: str, W: int = W_DECLARED) -> pd.DataFrame:
    """A7's censored waits: funded accounts that never opened before their start's history ended, with their live
    sessions (`days`) and whether they were still inside the wait (`days < W`)."""
    a = rec.accounts(design, arm, response)
    c = a[~a["opened"].astype(bool)][["start_day", "account", "activation_day", "days"]].copy()
    c["inside_wait"] = c["days"].astype(int) < int(W)
    return c.reset_index(drop=True)


def wait_problems(opens: pd.DataFrame, declined: pd.DataFrame, in_set: Mapping[str, bool] | None = None,
                  W: int = W_DECLARED) -> list[str]:
    """A1 items 4 and 5 on a run's openings and declined offers: every in-wait opening's offer is in state (`in_set`:
    offer id -> flag; None skips it), and every declined offer was declined inside the wait."""
    out = []
    if in_set is not None:
        iw = opens[opens["in_wait"]]
        bad = [x for x in iw["offer"] if not bool(in_set.get(x, False))]
        if bad:
            out.append(f"{len(bad)} in-wait openings are out of state (first {bad[0]})")
    if len(declined) and (declined["wait_session"].astype(int) >= int(W)).any():
        out.append("an offer was declined after the account's wait was over")
    return out


__all__ = ["W_DECLARED", "AmbiguousOffer", "GateOpen", "block_fingerprint", "WaitSpec", "take_latest_declined",
           "GateWrapper", "waiting_class", "spec_of", "FamilyReducer", "FamilyRecorder", "openings", "censored",
           "wait_problems"]
