"""Q-70: the place-recording adapter -- a design's gate campaign re-run through `extended/gate.py` while recording, for
every simulated trade and every funded account, the offer it took, its R, its place and what the engine booked (the
fields and the draft lines that need each: `extended/place_fields.py`). Generic engine infrastructure, as Q-47's
`extended/gate.py` and Q-71's `extended/campaign.py` are: no family, feature or model is built here.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import gate as XG, place_records as PR
    rec = PR.PlaceRecorder(shifts=("lower_bound",), dates=days, offer_ids=PR.block_offer_ids(t, days, blocks, "id"))
    rows, passed = XG.run_gate(blocks, ..., recorder=rec)       # every argument of the gate, plus the recorder
    rec.trades(), rec.accounts(), rec.openings(), rec.per_year("lower_bound", 0.0), rec.problems()

**What it needs from the engine, and why recording changes nothing.** The engine already keeps a per-trade ledger and a
daily account recorder (`simulate_lockstep_path(record_trades=True, record_days=True)`, D-130, D-146); both only append
rows and change no account's evolution (U2, D-649, re-ran P-14, P-15 and P-16 with them on and reproduced the
registered paths). A campaign returns every path at once, so with them on, 500 paths would hold every ledger in memory.
Here each path's ledger and day rows are read into compact columns **where the path ran** (in this process or in its
path worker) and dropped: the path comes back as a `RecordedPath` -- the unrecorded call's path, its `trades`,
`account_days` and `campaign_days` as the caller asked (empty in the gate), with the record beside it -- and the gate
hands its hooks and rows the plain path (`PlaceRecorder.collect`). So the gate's rows, its hooks and every `PATH_COLS`
column are those of the unrecorded run.

**The seams, all marked Q-70 and inside the re-composition proofs:**

1. `extended.gate.run_gate(recorder=...)`: for each (shift, level) the recorder records, the campaign gets the keyword
   `path_reducer` (`gate.recorder_arguments`), and its paths go through `gate.recorded_paths` before the gate reads
   them; `gate.gate_recomposition_problems` strips Q-47, Q-71 and Q-70;
2. `extended.campaign.simulate_lockstep_campaign(path_reducer=...)`: one statement chooses the paths' runner
   (`campaign.path_runner`) -- the vendored `_run_paths` without a reducer, this module's `_run_paths` with one;
   `campaign.campaign_recomposition_problems` strips Q-71 and Q-70;
3. this module's `_run_paths` and `_path_chunk`: the vendored functions' text (`vendor/stage2/propedge/campaign/
   lockstep.py`), with lines marked Q-70 that turn both recorders on and run each path through the reducer
   (`PathReducer.one_path`: the vendored `_one_path`, then the record); `runner_recomposition_problems` proves each
   is the vendored function plus its marked lines, statement for statement. **The guard, refusing:** every recorded
   run checks that the two vendored functions' source texts hash to `VENDORED_RUNNER_SHA256` (a newer snapshot is a
   new decision row; this module is then re-composed and re-checked under it).

**The place rule** is D-668 (2)'s, as `propedge.research.u_value_map.records_counts` applies it to U2's records: a
Combine's trades are (b); a funded account's first trade (by session, then slot) is (c); its others are (e) on a session
whose position among the account's recorded sessions is after its first payout request's relative session, else (d).
`record_path` labels each trade by that rule and **checks every path's counts against the vendored function's**; a
difference is a problem (`PlaceRecorder.problems`), never silently kept.

**The per-path checks** (each failure a problem line naming the path): the ledger's rows number the path's trades
(`trades_by_day`) and its accounts' trades; the places equal `records_counts`'; one opening for each funded account that
traded; every trade's P&L is its balance change and an account's trades in a session chain; every trade has its day row;
every routed trade's (historical day, trade index) is in the blocks; R equals the table's where the table sets it.

**The U1 replay** (Q-17's adapter, `extended/user_beside.py`) is wired by Q-94: `extended/replay_records.py` records a
replay's long runs through `user_beside.run_starts(recorder=...)` and reads each with `record_path` over the start's
window of the blocks (`BlockMeta.window`). **Not here:** offers a waiting account declines are not trades and are not
recorded (family O's own gating wrapper sees them).
"""
from __future__ import annotations

import copy
import functools
import hashlib
import inspect
from collections import Counter
from dataclasses import dataclass, field, fields, replace
from typing import Any, Callable, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign import lockstep as _vl  # noqa: E402
from propedge.campaign.lockstep import (  # noqa: E402  -- every name the vendored runner's body uses (vendored)
    LockstepPath,
    Protocol,
    _one_path,
    _WorkerEnvironment,
    check_parallel_inputs,
    path_pool,
)
from propedge.research import u_value_map as _UV  # noqa: E402

from extended import place_fields as PF  # noqa: E402

#: sha256 of the vendored path runner's source texts (LF), from which `_run_paths` and `_path_chunk` below were composed
#: (Stage 2 f1b42e2, vendored under E-002; `propedge/campaign/lockstep.py`)
VENDORED_RUNNER_SHA256 = {
    "_run_paths": "2845d418ae962d3adf52814558ba0c9da7cd105845399eb2d709b8a4e0c5b378",
    "_path_chunk": "bec2e5139447eb9f500694e6f92f190823b3f8021d1368627c9b0f8602ca7d56",
}
#: the comment marker on every added line of this module's re-composed functions (and of the gate's and campaign's)
MARKER = "Q-70"
#: the gate's two arms
SHIFTS = ("point", "lower_bound")
#: D-668 (2)'s places, the vendored names (`u_value_map.PLACES`): (a) is their sum
PLACES = tuple(_UV.PLACES)
SINGLE_PLACES = tuple(_UV.SINGLE_PLACES)
SESSIONS_PER_YEAR = float(_UV.SESSIONS_PER_YEAR)
#: the bands `records_counts` keys its day counts by -- they decide no place, so any positive values serve
_BAND = 500.0
TOL = 1e-6


def _source_sha256(fn: Callable) -> str:
    return hashlib.sha256(inspect.getsource(fn).replace("\r\n", "\n").encode("utf-8")).hexdigest()


def vendored_runner_sha256() -> dict[str, str]:
    """The sha256 of each vendored runner function's source text, line endings normalised to LF."""
    return {name: _source_sha256(getattr(_vl, name)) for name in VENDORED_RUNNER_SHA256}


def check_vendored_runner_source(expected: dict[str, str] | None = None) -> None:
    """Refuse (`RuntimeError`) unless the vendored `_run_paths` and `_path_chunk` are the ones this module's runner was
    composed from."""
    want = VENDORED_RUNNER_SHA256 if expected is None else dict(expected)
    got = vendored_runner_sha256()
    bad = sorted(k for k in want if got.get(k) != want[k])
    if bad:
        raise RuntimeError(f"REFUSED (Q-70): the vendored lockstep {bad} source hashes to "
                           f"{[got.get(k) for k in bad]}, not the {[want[k] for k in bad]} this adapter was composed "
                           "from; re-compose extended/place_records.py under the new snapshot's row")


def runner_recomposition_problems() -> list[str]:
    """This module's `_run_paths` and `_path_chunk` against the vendored ones, statement for statement, with every line
    marked Q-70 removed (`extended.campaign.recomposition_problems`); empty when the only differences are the marked
    lines."""
    from extended import campaign as XC

    return ([f"_run_paths: {x}" for x in XC.recomposition_problems(_run_paths, _vl._run_paths, (MARKER,))]
            + [f"_path_chunk: {x}" for x in XC.recomposition_problems(_path_chunk, _vl._path_chunk, (MARKER,))])


# ------------------------------------------------------------------------------------------------ the blocks' offers


class BlockMeta:
    """What a record needs of a campaign's day blocks, flattened so it pickles small: each block's trade count and
    offset, every trade's entry and exit time and side, and the caller's dates (one a block) and offer ids (one a trade,
    in each block's trade order)."""

    def __init__(self, blocks: Sequence[Any], *, dates: Sequence[Any] | None = None,
                 offer_ids: Sequence[Sequence[Any]] | None = None):
        n = np.array([len(b) for b in blocks], dtype=np.int64)
        self.lengths = n
        self.offsets = np.concatenate([[0], np.cumsum(n)]).astype(np.int64)
        total = int(self.offsets[-1])

        def flat(attr: str, fill: float) -> np.ndarray:
            parts = []
            for b in blocks:
                v = getattr(b, attr, None)
                parts.append(np.full(len(b), fill) if v is None else np.asarray(v, dtype=float).reshape(-1))
            return np.concatenate(parts) if parts else np.zeros(0)

        self.entry_t = flat("entry_t", np.nan)
        self.exit_t = flat("exit_t", np.nan)
        self.side = flat("sides", 0.0).astype(np.int64)
        if len(self.entry_t) != total or len(self.side) != total:
            raise ValueError("a block's entry times or sides do not number its trades")
        self.dates: np.ndarray | None = None
        if dates is not None:
            d = [str(x) for x in dates]
            if len(d) != len(blocks):
                raise ValueError(f"{len(d)} dates for {len(blocks)} day blocks: one date a block")
            self.dates = np.asarray(d, dtype=object)
        self.offers: np.ndarray | None = None
        if offer_ids is not None:
            ids = list(offer_ids)
            if len(ids) != len(blocks):
                raise ValueError(f"offer ids for {len(ids)} blocks, the campaign has {len(blocks)}")
            bad = [h for h, (x, b) in enumerate(zip(ids, blocks)) if len(x) != len(b)]
            if bad:
                raise ValueError(f"the offer ids of blocks {bad[:5]} do not number their trades")
            arr = np.empty(total, dtype=object)
            for h, x in enumerate(ids):
                arr[self.offsets[h]:self.offsets[h + 1]] = list(x)
            self.offers = arr

    @property
    def n_blocks(self) -> int:
        return int(len(self.lengths))

    def window(self, start: int, length: int) -> "BlockMeta":
        """Q-94: blocks `start` .. `start + length - 1` as a meta of their own (views of these arrays, nothing copied)
        -- what a replay of that window of the blocks sees: its historical day 0 is the window's first block, its dates
        and offer ids the window's. Refuses (`ValueError`) a window that is not inside the blocks."""
        s, n = int(start), int(length)
        if s < 0 or n < 0 or s + n > self.n_blocks:
            raise ValueError(f"the window {s} .. {s + n - 1} is not inside the {self.n_blocks} blocks")
        a, b = int(self.offsets[s]), int(self.offsets[s + n])
        w = object.__new__(BlockMeta)
        w.lengths = self.lengths[s:s + n]
        w.offsets = self.offsets[s:s + n + 1] - a
        w.entry_t, w.exit_t, w.side = self.entry_t[a:b], self.exit_t[a:b], self.side[a:b]
        w.dates = None if self.dates is None else self.dates[s:s + n]
        w.offers = None if self.offers is None else self.offers[a:b]
        return w

    def at(self, h: int, j: int) -> int | None:
        """The flat position of block h's trade j, or None when it is not in the blocks."""
        if not (0 <= h < self.n_blocks and 0 <= j < int(self.lengths[h])):
            return None
        return int(self.offsets[h] + j)


def block_offer_ids(t: pd.DataFrame, days: Sequence[Any], blocks: Sequence[Any], column: str | None = None
                    ) -> list[np.ndarray]:
    """Each block's offer ids in its trade order, for a trade table laid on its blocks as
    `score_fv3_grid.gate_blocks` lays it -- one block a day of `days`, a day's trades in stable `entry_t` order.
    `column` names the id (None: the table's index). Refuses (`ValueError`) unless the blocks number each day's
    trades and carry the same entry times, so an id can never be attached to another trade."""
    by = ({str(d): g.sort_values("entry_t", kind="stable") for d, g in t.groupby(t["date"].astype(str))}
          if len(t) else {})
    if len(days) != len(blocks):
        raise ValueError(f"{len(days)} days for {len(blocks)} blocks")
    out = []
    for h, (d, b) in enumerate(zip(days, blocks)):
        g = by.get(str(d))
        n = 0 if g is None else len(g)
        if n != len(b):
            raise ValueError(f"block {h} ({d}) holds {len(b)} trades, the table {n} on that day")
        if n and getattr(b, "entry_t", None) is not None:
            if not np.array_equal(np.asarray(b.entry_t, dtype=float), g["entry_t"].to_numpy(float), equal_nan=True):
                raise ValueError(f"block {h} ({d}): the entry times are not the table's in its order")
        ids = (g.index.to_numpy() if column is None else g[column].to_numpy()) if n else np.zeros(0, dtype=object)
        out.append(np.asarray(ids, dtype=object))
    return out


# ------------------------------------------------------------------------------------------------ one path's record


def _num(x: Any) -> float:
    try:
        return float("nan") if x is None else float(x)
    except (TypeError, ValueError):
        return float("nan")


def _empty_columns(fields: Sequence[PF.Field]) -> dict[str, list]:
    return {f.name: [] for f in fields}


def _as_arrays(cols: dict[str, list], fields: Sequence[PF.Field]) -> dict[str, np.ndarray]:
    kinds = {"int": np.int64, "float": float, "bool": bool, "str": object, "object": object}
    return {f.name: np.asarray(cols[f.name], dtype=kinds[f.dtype]) for f in fields}


def record_path(x: LockstepPath, *, path: int, path_seed: int, shift: str, enforcement_p: float, meta: BlockMeta,
                combine_floor0: float, funded_floor0: float, mll: float) -> dict[str, Any]:
    """One path's place record from its ledger and daily recorder (both on): `trades` (one entry a trade, the columns
    of `place_fields.TRADE_FIELDS`), `accounts` (one a funded account, `ACCOUNT_FIELDS`), `counts` (its trades by place,
    the vendored `records_counts`') and `problems` (every check that fails, as text)."""
    problems: list[str] = []
    tag = f"{shift} p={enforcement_p:g} path {path}"
    ledger = list(x.trades)
    days = list(x.account_days)
    n_trades = int(sum(int(v) for v in getattr(x.path, "trades_by_day", ()) or ()))
    by_acct_trades = sum(int(c.trades) for c in x.combines) + sum(int(f.trades) for f in x.funded)
    if len(ledger) != by_acct_trades:
        problems.append(f"{tag}: {len(ledger)} ledger rows against the accounts' {by_acct_trades} trades")
    if len(getattr(x.path, "trades_by_day", ()) or ()) and len(ledger) != n_trades:
        problems.append(f"{tag}: {len(ledger)} ledger rows against the path's {n_trades} trades")
    if by_acct_trades and not days:
        problems.append(f"{tag}: the daily recorder is off (no day rows)")

    # each account's recorded sessions: (kind, index, day) -> (attempt, position, session-start balance and floor)
    fmap = {int(f.index): f for f in x.funded}
    keyed: dict[tuple, list] = {}
    for r in days:
        kind = str(r["kind"])
        keyed.setdefault((kind, int(r["index"]), int(r.get("attempt") or 0) if kind == "combine" else 0), []).append(r)
    sess: dict[tuple, tuple] = {}
    for (kind, index, attempt), rows in keyed.items():
        rows = sorted(rows, key=lambda r: int(r["day"]))
        prev_b, prev_f = 0.0, (combine_floor0 if kind == "combine" else funded_floor0)
        for k, r in enumerate(rows):
            key = (kind, index, int(r["day"]))
            if key in sess:
                problems.append(f"{tag}: {kind} {index} has two day rows on day {r['day']}")
            sess[key] = (attempt, k, prev_b, prev_f)
            prev_b, prev_f = float(r["balance"]), float(r["floor"])

    def fp_of(index: int) -> int | None:
        f = fmap.get(index)
        return int(f.first_payout_day) if (f is not None and int(f.n_payouts) > 0) else None

    order = sorted(range(len(ledger)), key=lambda i: (int(ledger[i]["day"]), int(ledger[i].get("slot") or 0)))
    first_of: dict[int, int] = {}
    for i in order:
        r = ledger[i]
        if str(r["kind"]) == "funded" and int(r["index"]) not in first_of:
            first_of[int(r["index"])] = i
    cols = _empty_columns(PF.TRADE_FIELDS)
    places: Counter = Counter()
    last_after: dict[tuple, float] = {}
    for i, r in enumerate(ledger):
        kind, index, day = str(r["kind"]), int(r["index"]), int(r["day"])
        s = sess.get((kind, index, day))
        if s is None:
            problems.append(f"{tag}: the {kind} {index}'s trade on day {day} has no day row")
            s = (0, -1, float("nan"), float("nan"))
        attempt, k, sb, sf = s
        if kind == "combine":
            phase, place = "combine", "b_evaluation"
        elif kind == "funded":
            fp = fp_of(index)
            phase = "paid" if (fp is not None and k > fp) else "funded"
            place = ("c_funded_opening" if first_of.get(index) == i else
                     "e_paid" if (fp is not None and k > fp) else "d_funded_later")
        else:
            phase, place = kind, "other"
        places[place] += 1
        h = -1 if r.get("historical_day") is None else int(r["historical_day"])
        j = -1 if r.get("trade_index") is None else int(r["trade_index"])
        source = str(r.get("source") or "strategy")
        pos = meta.at(h, j)
        if pos is None and source != "flip":
            problems.append(f"{tag}: the {kind} {index}'s trade on day {day} is not in the blocks (day block {h}, "
                            f"trade {j})")
        before, after, pnl = float(r["balance_before"]), float(r["balance_after"]), float(r["pnl"])
        if not abs((after - before) - pnl) <= TOL:
            problems.append(f"{tag}: the {kind} {index}'s trade on day {day} booked {pnl} but moved the balance "
                            f"{after - before}")
        chain = (kind, index, day)
        if chain in last_after and not abs(last_after[chain] - before) <= TOL:
            problems.append(f"{tag}: the {kind} {index}'s trades on day {day} do not chain")
        last_after[chain] = after
        prr = _num(r.get("policy_rr"))
        rr = _num(r.get("rr")) if r.get("rr") is not None else prr
        if np.isfinite(prr) and np.isfinite(rr) and source == "strategy" and abs(rr - prr) > 1e-12:
            problems.append(f"{tag}: the {kind} {index}'s trade on day {day} traded R {rr}, the table's {prr}")
        fr = fmap.get(index) if kind == "funded" else None
        vals = {
            "shift": shift, "enforcement_p": float(enforcement_p), "path": int(path), "path_seed": int(path_seed),
            "day": day, "kind": kind, "account": index, "attempt": int(attempt),
            "activation_day": int(fr.activation_day) if fr is not None else -1,
            "rel_day": int(r.get("rel_day", -1)), "account_session": int(k), "phase": phase, "place": place,
            "opening": place == "c_funded_opening",
            "historical_day": h, "trade_index": j,
            "date": str(meta.dates[h]) if (meta.dates is not None and 0 <= h < meta.n_blocks) else "",
            "offer": meta.offers[pos] if (meta.offers is not None and pos is not None) else None,
            "side": int(meta.side[pos]) if pos is not None else 0,
            "entry_t": float(meta.entry_t[pos]) if pos is not None else float("nan"),
            "exit_t": float(meta.exit_t[pos]) if pos is not None else float("nan"),
            "source": source,
            "session_balance": float(sb), "session_floor": float(sf), "balance_before": before,
            "floor": float(r["floor"]), "room": _num(r.get("room")), "regime": str(r.get("regime") or ""),
            "policy_risk": _num(r.get("policy_risk")), "policy_rr": prr,
            "policy_max_trades": _num(r.get("policy_max_trades")), "rr": rr,
            "rr_used": _num(r.get("rr_used")) if r.get("rr_used") is not None else rr,
            "at_need": bool(r.get("at_need") or False), "exit_kind": str(r.get("exit_kind") or ""),
            "pnl": pnl, "balance_after": after, "u": _num(r.get("u")), "contracts": _num(r.get("contracts")),
            "realised_risk": _num(r.get("realised_risk", r.get("risk"))), "intended_risk": _num(r.get("intended_risk")),
            "intended_capped_risk": _num(r.get("intended_capped_risk")),
            "risk_per_contract": _num(r.get("risk_per_contract")), "fee": _num(r.get("fee")),
            "room_capped": bool(r.get("room_capped") or False), "at_cap": bool(r.get("at_cap") or False),
            "mae": _num(r.get("mae")), "settlement": str(r.get("settlement") or ""),
        }
        for name in cols:
            cols[name].append(vals[name])
    if places.get("other", 0):
        problems.append(f"{tag}: {places['other']} trades of an unknown kind")

    # the vendored classification, as U2 and U5 counted it
    ref = _UV.records_counts(days, ledger, list(x.funded), combine_floor0=combine_floor0, funded_floor0=funded_floor0,
                             balance_band=_BAND, cushion_band=_BAND, mll=mll)["places"]
    for p in SINGLE_PLACES + ("other",):
        if int(places.get(p, 0)) != int(ref.get(p, 0)):
            problems.append(f"{tag}: {places.get(p, 0)} trades at {p}, records_counts counts {ref.get(p, 0)}")

    acols = _empty_columns(PF.ACCOUNT_FIELDS)
    traded = 0
    for f in x.funded:
        index = int(f.index)
        i = first_of.get(index)
        opened = i is not None
        traded += int(int(f.trades) > 0)
        if opened != (int(f.trades) > 0):
            problems.append(f"{tag}: funded {index} has {f.trades} trades and {'an' if opened else 'no'} opening")
        o = ledger[i] if opened else None
        o_sess = sess.get(("funded", index, int(o["day"]))) if opened else None
        if opened and o_sess is not None and not o_sess[1] < int(f.days):
            problems.append(f"{tag}: funded {index}'s opening is at its session {o_sess[1]} of {f.days}")
        vals = {
            "shift": shift, "enforcement_p": float(enforcement_p), "path": int(path), "account": index,
            "activation_day": int(f.activation_day), "days": int(f.days), "trades": int(f.trades),
            "n_payouts": int(f.n_payouts), "first_payout_day": int(f.first_payout_day), "closed": bool(f.closed),
            "abandoned": bool(getattr(f, "abandoned", False)), "opened": bool(opened),
            "opening_day": int(o["day"]) if opened else -1,
            "opening_rel_day": int(o.get("rel_day", -1)) if opened else -1,
            "opening_session": int(o_sess[1]) if (opened and o_sess is not None) else -1,
        }
        for name in acols:
            acols[name].append(vals[name])
    if int(places.get("c_funded_opening", 0)) != traded:
        problems.append(f"{tag}: {places.get('c_funded_opening', 0)} openings for {traded} funded accounts that traded")
    return {"trades": _as_arrays(cols, PF.TRADE_FIELDS), "accounts": _as_arrays(acols, PF.ACCOUNT_FIELDS),
            "counts": Counter({p: int(ref.get(p, 0)) for p in SINGLE_PLACES}), "problems": problems[:20]}


@dataclass(frozen=True)
class RecordedPath(LockstepPath):
    """A path as the recorded runner hands it back: the unrecorded call's path, and beside it its place record (what
    `record_path` read from its ledger and day rows before they were dropped)."""

    place_record: dict = field(default_factory=dict)


def plain_path(x: LockstepPath) -> LockstepPath:
    """The vendored `LockstepPath` of a path, its record (if any) left behind."""
    return LockstepPath(**{f.name: getattr(x, f.name) for f in fields(LockstepPath)})


class PathReducer:
    """One campaign's (shift, level) reducer, a path at a time (module level, so it pickles to a path worker): reads
    the path's record (`record_path`), keeps the columns asked for, and hands back the path as the caller asked for it
    (`keep_trades`, `keep_days`: the campaign's own `record_trades` and `record_days`)."""

    def __init__(self, *, shift: str, enforcement_p: float, meta: BlockMeta, combine_floor0: float,
                 funded_floor0: float, mll: float, columns: Sequence[str] | None = None):
        self.shift = str(shift)
        self.enforcement_p = float(enforcement_p)
        self.meta = meta
        self.combine_floor0 = float(combine_floor0)
        self.funded_floor0 = float(funded_floor0)
        self.mll = float(mll)
        self.columns = None if columns is None else tuple(columns)
        self.keep_trades = False
        self.keep_days = False

    def told(self, *, keep_trades: bool, keep_days: bool) -> "PathReducer":
        """A copy told what the campaign's caller asked to keep on its paths."""
        r = copy.copy(self)
        r.keep_trades, r.keep_days = bool(keep_trades), bool(keep_days)
        return r

    def runner(self, *, keep_trades: bool, keep_days: bool) -> Callable:
        """The campaign's path runner with this reducer: this module's `_run_paths`, told what the caller keeps."""
        return functools.partial(_run_paths, reducer=self.told(keep_trades=keep_trades, keep_days=keep_days))

    def __call__(self, path_index: int, path_seed: int, x: LockstepPath) -> tuple[LockstepPath, dict[str, Any]]:
        rec = record_path(x, path=int(path_index), path_seed=int(path_seed), shift=self.shift,
                          enforcement_p=self.enforcement_p, meta=self.meta, combine_floor0=self.combine_floor0,
                          funded_floor0=self.funded_floor0, mll=self.mll)
        if self.columns is not None:
            rec["trades"] = {k: v for k, v in rec["trades"].items() if k in self.columns}
        kw: dict[str, Any] = {}
        if not self.keep_trades:
            kw["trades"] = ()
        if not self.keep_days:
            kw["account_days"] = ()
            kw["campaign_days"] = ()
        return (replace(x, **kw) if kw else x), rec

    def one_path(self, protocol: Any, path_index: int, path_seed: int, path_kwargs: dict[str, Any],
                 draw_factories_for_path: Any, flip_for_path: Any, wallet_for_path: Any) -> RecordedPath:
        """One path as the vendored `_one_path` runs it (the recorders on in `path_kwargs`), read and reduced here."""
        x = _one_path(protocol, path_index, path_seed, path_kwargs, draw_factories_for_path, flip_for_path,
                      wallet_for_path)
        kept, rec = self(path_index, path_seed, x)
        return RecordedPath(**{f.name: getattr(kept, f.name) for f in fields(LockstepPath)}, place_record=rec)


# ------------------------------------------------------------------------------------------------ the path runner


def _path_chunk(task: tuple,
                reducer: Any,                                                   # Q-70
                ) -> tuple[list[LockstepPath], Any]:
    """The vendored `_path_chunk`, each path run through the reducer (Q-70): a worker's share, its paths in order, and
    the draw factory's `export_state()` after them (None without one)."""
    _one_path = reducer.one_path                                                # Q-70: each path read where it ran
    protocol, path_kwargs, factories, flip_for_path, items = task
    out = [_one_path(protocol, i, s, path_kwargs, factories, flip_for_path, None) for i, s in items]
    export = getattr(factories, "export_state", None)
    return out, (export() if callable(export) else None)


_recorded_path_chunk = _path_chunk


def _run_paths(protocol: Protocol, path_kwargs: dict[str, Any], seeds: Sequence[int],
               draw_factories_for_path: Callable[[int], tuple] | None, flip_for_path: Callable[[int], tuple] | None,
               wallet_for_path: Callable[[int], Any] | None, *, workers: int = 1, pool: Any = None,
               memory_per_worker_gb: float | None = None,
               reducer: Any,                                                    # Q-70
               ) -> list[LockstepPath]:
    """The vendored `_run_paths` (Q-70: with the ledger and the day recorder on, and every path read by the reducer
    where it ran -- here, or in its worker): the paths in path order, each a `RecordedPath`."""
    check_vendored_runner_source()                                              # Q-70: refused unless pinned
    path_kwargs = dict(path_kwargs, record_trades=True, record_days=True)       # Q-70: both recorders on
    _one_path = reducer.one_path                                                # Q-70: each path read where it ran
    _path_chunk = functools.partial(_recorded_path_chunk, reducer=reducer)     # Q-70: and in a worker
    items = list(enumerate(seeds))
    if int(workers) > 1 or pool is not None:         # refused whatever the memory guard then allows
        check_parallel_inputs(protocol, path_kwargs, draw_factories_for_path, flip_for_path,
                              wallet_for_path=wallet_for_path)
    own = None
    n = 1
    if pool is not None:
        n = max(1, int(workers))
    elif int(workers) > 1 and len(items) > 1:
        own, n = path_pool(int(workers), n_tasks=len(items), memory_per_worker_gb=memory_per_worker_gb)
    if (pool is None and own is None) or len(items) <= 1:
        if own is not None:
            own.shutdown()
        return [_one_path(protocol, i, s, path_kwargs, draw_factories_for_path, flip_for_path, wallet_for_path)
                for i, s in items]
    k = min(len(items), 4 * n)                        # a few chunks a worker, so a slow chunk does not idle the rest
    bounds = [round(j * len(items) / k) for j in range(k + 1)]
    tasks = [(protocol, path_kwargs, draw_factories_for_path, flip_for_path, items[bounds[j]:bounds[j + 1]])
             for j in range(k)]
    try:
        with _WorkerEnvironment():                    # workers start during the submissions, with one BLAS thread
            futures = [(pool or own).submit(_path_chunk, task) for task in tasks]
        done = [f.result() for f in futures]
    finally:
        if own is not None:
            own.shutdown()
    results: list[LockstepPath] = []
    absorb = getattr(draw_factories_for_path, "import_state", None)
    for chunk, state in done:
        results.extend(chunk)
        if state is not None and callable(absorb):
            absorb(state)
    return results


# ------------------------------------------------------------------------------------------------ the recorder


class PlaceRecorder:
    """What one gate call records, and its records afterwards. Give it to `extended.gate.run_gate(recorder=...)`; one
    recorder a gate call (a second campaign at a (shift, level) it already holds is refused).

    `shifts`: the arms recorded (default both); `levels`: the denial levels recorded (None: every level the gate runs);
    `dates`: one date a day block (the campaign's blocks, the gate's order); `offer_ids`: one id a trade, block by block
    in each block's trade order (`block_offer_ids` builds them from a trade table); `columns`: the trade columns kept,
    in the schema's order (None: every one of `place_fields.TRADE_COLUMNS`; a subset saves memory on a 500-path run --
    every check still runs on the full record before the rest is dropped)."""

    def __init__(self, *, shifts: Sequence[str] = SHIFTS, levels: Sequence[float] | None = None,
                 dates: Sequence[Any] | None = None, offer_ids: Sequence[Sequence[Any]] | None = None,
                 columns: Sequence[str] | None = None):
        bad = [s for s in shifts if s not in SHIFTS]
        if bad or not len(shifts):
            raise ValueError(f"shifts must be some of {SHIFTS}, got {tuple(shifts)!r}")
        self.shifts = tuple(str(s) for s in shifts)
        self.levels = None if levels is None else tuple(float(p) for p in levels)
        self.dates = None if dates is None else list(dates)
        self.offer_ids = None if offer_ids is None else list(offer_ids)
        if columns is not None:
            unknown = [c for c in columns if c not in PF.TRADE_COLUMNS]
            if unknown:
                raise ValueError(f"unknown trade columns {unknown}; the record's are place_fields.TRADE_COLUMNS")
            columns = tuple(c for c in PF.TRADE_COLUMNS if c in set(columns))
        self.columns = columns
        self._recs: dict[tuple[str, float], list[dict[str, Any]]] = {}
        self._runs: dict[tuple[str, float], dict[str, int]] = {}

    def wants(self, shift: str, enforcement_p: float) -> bool:
        return str(shift) in self.shifts and (self.levels is None or float(enforcement_p) in self.levels)

    def reducer(self, shift: str, enforcement_p: float, blk: Sequence[Any], rules: Any) -> PathReducer:
        """The campaign's `path_reducer` for one recorded (shift, level). The arm's own blocks give the offers' times
        and sides (`gate.shifted_blocks` moves outcomes only, so both arms carry the same)."""
        return PathReducer(shift=shift, enforcement_p=enforcement_p,
                           meta=BlockMeta(blk, dates=self.dates, offer_ids=self.offer_ids),
                           combine_floor0=-float(rules.mll), funded_floor0=float(rules.xfa_mll_start),
                           mll=float(rules.mll), columns=self.columns)

    def collect(self, shift: str, enforcement_p: float, paths: Sequence[LockstepPath], *, n_paths: int,
                horizon_days: int, seed: int) -> list[LockstepPath]:
        """Take one recorded campaign's records off its paths (each a `RecordedPath`, in path order) and hand back the
        plain paths -- the unrecorded campaign's."""
        key = (str(shift), float(enforcement_p))
        if key in self._recs:
            raise RuntimeError(f"the recorder already holds {key}: one recorder a gate call")
        not_rec = [i for i, x in enumerate(paths) if not isinstance(x, RecordedPath)]
        if not_rec:
            raise RuntimeError(f"paths {not_rec[:5]} of {key} came back unrecorded")
        self._recs[key] = [x.place_record for x in paths]
        self._runs[key] = {"n_paths": int(n_paths), "horizon_days": int(horizon_days), "seed": int(seed)}
        return [plain_path(x) for x in paths]

    # ---- the records

    def recorded(self) -> list[tuple[str, float]]:
        return list(self._recs)

    def run_of(self, shift: str, enforcement_p: float) -> dict[str, int]:
        return dict(self._runs[(str(shift), float(enforcement_p))])

    def _frame(self, part: str, fields_: Sequence[PF.Field], keys: Sequence[tuple[str, float]] | None) -> pd.DataFrame:
        names = [f.name for f in fields_]
        if part == "trades" and self.columns is not None:
            names = list(self.columns)
        chunks = []
        for key in (self.recorded() if keys is None else keys):
            for r in self._recs.get(key, []):
                chunks.append(pd.DataFrame({k: r[part][k] for k in names}))
        if not chunks:
            return pd.DataFrame({k: pd.Series(dtype=object) for k in names})
        return pd.concat(chunks, ignore_index=True)

    def trades(self, shift: str | None = None, enforcement_p: float | None = None) -> pd.DataFrame:
        """One row a simulated trade (`place_fields.TRADE_FIELDS`, or the kept columns), every recorded campaign or
        the one named, in path and ledger order."""
        return self._frame("trades", PF.TRADE_FIELDS, self._keys(shift, enforcement_p))

    def accounts(self, shift: str | None = None, enforcement_p: float | None = None) -> pd.DataFrame:
        """One row a funded account of a recorded path (`place_fields.ACCOUNT_FIELDS`), opened or not."""
        return self._frame("accounts", PF.ACCOUNT_FIELDS, self._keys(shift, enforcement_p))

    def openings(self, shift: str | None = None, enforcement_p: float | None = None) -> pd.DataFrame:
        """The funded openings (place c): one a funded account that traded."""
        t = self.trades(shift, enforcement_p)
        if "place" not in t.columns:
            raise ValueError("the kept columns hold no `place`")
        return t[t["place"] == "c_funded_opening"].reset_index(drop=True)

    def _keys(self, shift: str | None, enforcement_p: float | None) -> list[tuple[str, float]]:
        return [k for k in self.recorded() if (shift is None or k[0] == shift)
                and (enforcement_p is None or k[1] == float(enforcement_p))]

    def counts(self, shift: str, enforcement_p: float) -> Counter:
        """The campaign's trades by place, as the vendored `records_counts` counts them (summed over paths), with
        (a)."""
        c: Counter = Counter()
        for r in self._recs[(str(shift), float(enforcement_p))]:
            c.update(r["counts"])
        c["a_every_trade"] = sum(int(c.get(p, 0)) for p in SINGLE_PLACES)
        return c

    def per_year(self, shift: str, enforcement_p: float) -> dict[str, float]:
        """Trades a year by place (D-668 (2)'s records basis: the campaign's trades of the place over paths x horizon /
        252 sessions -- a five-seat campaign's year, as `u_value_map.csv`'s `trades_per_year_records`)."""
        run = self.run_of(shift, enforcement_p)
        years = float(run["n_paths"]) * float(run["horizon_days"]) / SESSIONS_PER_YEAR
        c = self.counts(shift, enforcement_p)
        return {p: float(c.get(p, 0)) / years for p in PLACES}

    def problems(self) -> list[str]:
        """Every failed per-path check of every recorded campaign (empty when the records hold)."""
        return [p for recs in self._recs.values() for r in recs for p in r["problems"]]


def run_gate_recorded(blocks: Sequence[Any], *, recorder: PlaceRecorder | None = None, **gate_kwargs: Any
                      ) -> tuple[pd.DataFrame, bool, PlaceRecorder]:
    """`extended.gate.run_gate` with a recorder (a fresh one recording both arms at every level when None): (rows,
    passed, recorder)."""
    from extended import gate as XG

    rec = PlaceRecorder() if recorder is None else recorder
    rows, passed = XG.run_gate(blocks, recorder=rec, **gate_kwargs)
    return rows, passed, rec


__all__ = ["VENDORED_RUNNER_SHA256", "MARKER", "SHIFTS", "PLACES", "SINGLE_PLACES", "SESSIONS_PER_YEAR",
           "vendored_runner_sha256", "check_vendored_runner_source", "runner_recomposition_problems", "BlockMeta",
           "block_offer_ids", "record_path", "RecordedPath", "plain_path", "PathReducer", "PlaceRecorder",
           "run_gate_recorded"]
