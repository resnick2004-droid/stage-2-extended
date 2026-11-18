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
recorded long replay ran, attaches that path's declined offers to the start's record (`declined`). On the gate
(index mode) `GateRecorder` is Q-70's `PlaceRecorder` whose path reducer does the same for each gate path, and
`gate_wait_problems` holds a recorded campaign to the wait: every in-wait opening in the set, every declined offer out
of it, inside the wait and before its account's opening (the build read's m3, before floor (iii)).

**Pickling.** The class carries its spec; a class made here reduces to `(waiting_class, (spec,))` by `copyreg`, so it
reaches a worker with its task and is rebuilt there (cached by the spec's digest). Q-76's forfeiture composes over it
(`user_beside.forfeit_class(cls)`, made where the replay runs); the class has no household rule of its own.
"""
from __future__ import annotations

import copyreg
import hashlib
import pickle
import weakref
from dataclasses import replace
from typing import Any, Mapping, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign.lockstep import FundedAccount  # noqa: E402

from extended import place_records as PR  # noqa: E402
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


# ------------------------------------------------------------------------------------------------ the gate's recorder


class GateReducer(PR.PathReducer):
    """Q-70's gate path reducer (`place_records.PathReducer`), plus the path's declined offers: right after the path
    ran (here or in its path worker), the wrapper's own count of that path (`take_latest_declined`) is attached to its
    place record (`declined`: (account, historical day, trade index, wait session) each); an attribution problem joins
    the record's problems."""

    @classmethod
    def from_base(cls, base: PR.PathReducer) -> "GateReducer":
        obj = cls.__new__(cls)
        obj.__dict__.update(base.__dict__)
        return obj

    def one_path(self, protocol: Any, path_index: int, path_seed: int, path_kwargs: dict[str, Any],
                 draw_factories_for_path: Any, flip_for_path: Any, wallet_for_path: Any) -> Any:
        x = super().one_path(protocol, path_index, path_seed, path_kwargs, draw_factories_for_path, flip_for_path,
                             wallet_for_path)
        declined, problems = take_latest_declined(len(x.funded))
        rec = dict(x.place_record)
        rec["declined"] = [tuple(int(v) for v in d) for d in declined]
        rec["problems"] = list(rec.get("problems", [])) + [f"{self.shift} p={self.enforcement_p:g} path {path_index}: "
                                                           f"{p}" for p in problems]
        return replace(x, place_record=rec)


class GateRecorder(PR.PlaceRecorder):
    """Q-70's `PlaceRecorder` for a gate call with the waiting class (index mode): its reducer the family's
    (`GateReducer`), so each recorded path carries the wrapper's declined offers beside its trades and accounts."""

    def reducer(self, shift: str, enforcement_p: float, blk: Sequence[Any], rules: Any) -> GateReducer:
        return GateReducer.from_base(super().reducer(shift, enforcement_p, blk, rules))

    def declined(self, shift: str | None = None, enforcement_p: float | None = None) -> pd.DataFrame:
        """Every declined offer of the recorded campaigns: shift, level, path, account, historical day (the gate's
        block), trade index, wait session -- the gating wrapper's own count."""
        rows = [(k[0], k[1], i, *d) for k in self._keys(shift, enforcement_p)
                for i, r in enumerate(self._recs.get(k, [])) for d in r.get("declined", [])]
        return pd.DataFrame(rows, columns=["shift", "enforcement_p", "path", "account", "historical_day", "trade_index",
                                           "wait_session"])


def gate_wait_problems(rec: GateRecorder, in_state: Sequence[np.ndarray], *, shift: str, enforcement_p: float = 0.0,
                       W: int = W_DECLARED) -> tuple[list[str], dict[str, int]]:
    """5.4's wait on a recorded gate campaign in index mode (the read's m3; A1 item 5's form on the gate): every in-wait
    opening (`opening_session < W`) is in the set, every fallback opening at or after session W, every declined offer
    out of the set, declined inside the wait and no later than its account's opening; refused when the campaign shows
    no in-wait opening or no decline (the identity must bite). `in_state[h]`: the flags of the gate's block h in its
    trade order. (problems, counts)."""
    out: list[str] = []
    acc = rec.accounts(shift, enforcement_p)
    ops = rec.openings(shift, enforcement_p)
    dec = rec.declined(shift, enforcement_p)
    flag = lambda h, j: bool(in_state[int(h)][int(j)])                                      # noqa: E731
    if len(ops) and (ops["account_session"].astype(int).to_numpy()
                     != ops.merge(acc[["path", "account", "opening_session"]], on=["path", "account"], how="left",
                                  validate="many_to_one")["opening_session"].astype(int).to_numpy()).any():
        out.append("an opening's trade row disagrees with its account row (the wait)")
    iw = ops[ops["account_session"].astype(int) < int(W)]
    fb = ops[ops["account_session"].astype(int) >= int(W)]
    bad = [(int(p), int(a)) for p, a, h, j in zip(iw["path"], iw["account"], iw["historical_day"], iw["trade_index"])
           if not flag(h, j)]
    if bad:
        out.append(f"{len(bad)} in-wait openings are out of the set (first path, account {bad[0]})")
    inset = [(int(p), int(a)) for p, a, h, j in zip(dec["path"], dec["account"], dec["historical_day"],
                                                     dec["trade_index"]) if flag(h, j)]
    if inset:
        out.append(f"{len(inset)} declined offers are in the set (first path, account {inset[0]})")
    if len(dec) and (dec["wait_session"].astype(int) >= int(W)).any():
        out.append("an offer was declined after the account's wait was over")
    opened = {(int(p), int(a)): int(s) for p, a, s in zip(acc["path"], acc["account"], acc["opening_session"])
              if int(s) >= 0}
    late = [(int(p), int(a)) for p, a, s in zip(dec["path"], dec["account"], dec["wait_session"])
            if (int(p), int(a)) in opened and int(s) > opened[(int(p), int(a))]]
    if late:
        out.append(f"{len(late)} offers were declined after their account's opening (first {late[0]})")
    counts = {"openings": int(len(ops)), "in_wait": int(len(iw)), "fallback": int(len(fb)), "declined": int(len(dec)),
              "paths": int(acc["path"].nunique()) if len(acc) else 0}
    if not counts["in_wait"] or not counts["declined"]:
        out.append(f"{counts['declined']} declines and {counts['in_wait']} in-wait openings on the gate -- the identity "
                   "must see both")
    out += [p for p in rec.problems()]
    return out, counts


def gate_state_problems(rec: GateRecorder, shift: str, in_set: Mapping[str, bool], enforcement_p: float = 0.0,
                        W: int = W_DECLARED) -> tuple[list[str], dict[str, int]]:
    """W2 (the third build read): floor (iii)'s recorded gate campaign held to the pick's state **by offer id** -- every
    in-wait opening's offer (the record's `offer`, from the recorder's offer ids) is in `in_set` (offer id -> in
    state), every declined offer's id (`offer_ids[h][j]`) out of it, and every opening's recorded date its offer id's
    date. Independent of the flags the waiting class was built with. (problems, counts)."""
    out: list[str] = []
    if rec.offer_ids is None:
        return ["the recorder holds no offer ids: the gate's offers cannot be named"], {}
    ops = rec.openings(shift, enforcement_p)
    iw = ops[ops["account_session"].astype(int) < int(W)]
    bad = [str(o) for o in iw["offer"] if not bool(in_set.get(str(o), False))]
    if bad:
        out.append(f"{len(bad)} in-wait openings' offers are out of the pick's state (first {bad[0]})")
    wrong = [str(o) for o, d in zip(ops["offer"], ops["date"]) if str(o).split("|")[0] != str(d)]
    if wrong:
        out.append(f"{len(wrong)} openings' recorded dates are not their offer ids' (first {wrong[0]})")
    dec = rec.declined(shift, enforcement_p)
    ids = [str(rec.offer_ids[int(h)][int(j)]) for h, j in zip(dec["historical_day"], dec["trade_index"])]
    ins = [x for x in ids if bool(in_set.get(x, False))]
    if ins:
        out.append(f"{len(ins)} declined offers are in the pick's state (first {ins[0]})")
    return out, {"openings": int(len(ops)), "in_wait": int(len(iw)), "declined": int(len(dec))}


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


def lookup_problems(spec: WaitSpec, job: dict, starts: Sequence[int]) -> list[str]:
    """m3: the wrapper's offer lookup on real data, before any replay -- every start's window (and each exact-length
    window U1 reads) is found at its own start."""
    from propedge.research import user_journey as U

    n = len(job["blocks"])
    fps = spec.fingerprints
    bad = []
    for s_ in starts:
        for L_ in {min(U.HORIZON, n - s_), *[h for h in U.EXACT if h < min(U.HORIZON, n - s_)]}:
            try:
                got = spec.window_offset(list(fps[s_:s_ + L_]))
            except (KeyError, ValueError) as exc:
                bad.append(f"the lookup: start {s_} ({L_} sessions): {exc}")
                continue
            if got != s_:
                bad.append(f"the lookup: start {s_}'s window ({L_} sessions) is found at {got}")
        if len(bad) > 3:
            break
    return bad



__all__ = ["lookup_problems", "W_DECLARED", "AmbiguousOffer", "GateOpen", "block_fingerprint", "WaitSpec", "take_latest_declined",
           "GateWrapper", "waiting_class", "spec_of", "FamilyReducer", "FamilyRecorder", "GateReducer", "GateRecorder",
           "gate_wait_problems", "gate_state_problems", "openings", "censored", "wait_problems"]
