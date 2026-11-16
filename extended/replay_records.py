"""Q-94 (E-055, E-059; family O's draft 18.1 item 4 and A2): place recording on Q-17's U1 replay -- the compact records
Q-70 makes for a gate campaign (`extended/place_records.py`: every simulated trade's offer, the table's R, its place,
its account and the account's state, what the engine booked; every funded account's opening and wait), made on the
user's replay over start days (`extended/user_beside.py`), beside each start's output and changing none of it.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import replay_records as RR, user_beside as B
    rec = RR.ReplayRecorder(offer_ids=ids)                       # ids: one a trade, block by block (optional)
    outs = B.run_starts("p16", "verdict", B.BY_NAME["off"], job, starts, workers=1, recorder=rec)
    rec.trades(), rec.accounts(), rec.openings(), rec.counts("p16", "verdict", "off"), rec.problems()

**The option.** `user_beside.run_starts(..., recorder=None)` is a declared keyword, off by default: absent, every task,
replay and output is the adapter's before Q-94 (Q-76's, 50e31d3) bit for bit. Given a `ReplayRecorder`, the recorder is
checked and its reducer made before any start runs, and each task carries the reducer as its tenth item (the ninth is
the declared class or None). In the task, **each start's long replay** -- the start's journey: min(252, sessions left)
sessions from the start, its own path seed -- runs with the engine's per-trade ledger and daily recorder on
(`record_trades=True`, `record_days=True`, nothing else changed), is read where it ran by Q-70's `record_path` over the
start's window of the blocks (`BlockMeta.window`), and is then handed on as the unrecorded call's path (ledger and day
rows dropped) to everything the adapter does with it -- the U1 record, the exact-length checks, the daily measures, the
response's record, the forfeiture's view. The exact-length runs (21, 63, 90, 126 sessions; U1's check of the long run's
event days) are run unrecorded, as before: they are checks of the record, not journeys.

**Why recording changes nothing.** The engine's two recorders only append rows (the ledger, `lockstep.py:485`, `:747`;
the day rows, `:1835`) and nothing reads them back; U2 (Stage 2 D-649) re-ran P-14, P-15 and P-16 with them on and
reproduced the registered paths; Q-70 held the gate with them on equal to it off. Here it is held on the replay: every
start's output with a recorder equals the unrecorded run's bit for bit (`tests/q94_synthetic.py`, all 19 responses, with
and without the pass-through class; `identity/replay_records_identity.py` on U1's start rows).

**What a start's record holds** (`place_fields.REPLAY_TRADE_FIELDS`, `REPLAY_ACCOUNT_FIELDS`): the gate record with its
campaign group replaced by the replay's (design, U1's arm, the response and its level, the start, its date, its seed).
The engine's run is recorded as it happened: under all-accounts forfeiture, the record is of the engine's run, before
the adapter's view takes the forfeited payouts out of the cash record (`user_beside.forfeit_view`) -- an account's
`n_payouts` there is the engine's.

**The per-start checks** (each failure a problem line; `ReplayRecorder.problems`): Q-70's per-path checks
(`record_path`: the ledger numbers the trades, the places are the vendored `records_counts`', the balances chain, every
routed trade is in the start's blocks, R is the table's where the table sets it) and Q-94's own --

1. the openings are the replay ledger's (family O 18.1 item 4: "the openings it records equal the replay ledger's"), by
   Q-35's reading of it (`openings.openings_from_ledger`: each funded account's first ledger row by day, then slot), and
   the ledger passes Q-35's checks (`openings.ledger_problems`: an account's rows number its trades, one opening for
   each account that traded, none before its first session, its calendar day its historical day + 1);
2. every routed trade is on its own session: calendar day = historical day + 1 (`ReplayTable`: a replay plays the
   window's sessions in order, once), so its offer's date is the trade's session;
3. the wait: an opened account's `opening_session` (its recorded sessions before the opening -- `FundedAccount.days` at
   routing, the engine steps every live account every session) is its opening's relative session (`rel_day`, day - the
   account's first session), and its accounts row agrees with its opening trade's row.

**Memory.** A full replay's records (two arms, ~1,700 starts each) are large if every trade column is kept; `columns`
keeps a subset of the trade columns (every check still runs on the full record, where the start ran, before the rest is
dropped); `columns=()` keeps none (the accounts, counts and problems are always kept).

Importing this module puts the vendored tree on `sys.path` (it imports `place_records`, which reads the engine).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Any, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import place_fields as PF  # noqa: E402
from extended import place_records as PR  # noqa: E402

#: the engine's two recorders the replay's long runs turn on
RECORDERS = ("record_trades", "record_days")
#: the trade columns a replay record keeps beside its campaign group (the gate record's, less the gate's campaign)
TRADE_DATA = tuple(c for c in PF.REPLAY_TRADE_COLUMNS if c not in PF.REPLAY_CAMPAIGN_COLUMNS)
ACCOUNT_DATA = tuple(c for c in PF.REPLAY_ACCOUNT_COLUMNS if c not in PF.REPLAY_CAMPAIGN_COLUMNS)
OPENING = "c_funded_opening"
MAX_PROBLEMS = 20


def recording_args(a: dict[str, Any]) -> dict[str, Any]:
    """The replay's arguments with both recorders on, nothing else changed; refuses (`ValueError`) arguments whose path
    already carries either (the caller's own setting would be overridden or kept on the path handed on)."""
    bad = sorted(k for k in RECORDERS if k in a["path"])
    if bad:
        raise ValueError(f"REFUSED (Q-94): the replay's path arguments already carry {bad}")
    return {**a, "path": {**a["path"], "record_trades": True, "record_days": True}}


def opening_problems(lp: Any, rec: dict[str, Any], start_day: int, tag: str) -> list[str]:
    """Q-94's per-start checks (the module's 1 to 3) of a recorded long replay against its record."""
    from extended import openings as O

    out: list[str] = []
    ops = O.openings_from_ledger(lp.trades, int(start_day))
    out += O.ledger_problems(lp.trades, lp.funded, ops, f"{tag}: ")
    t, a = rec["trades"], rec["accounts"]
    is_open = np.asarray(t["place"]) == OPENING
    cols = [np.asarray(t[c])[is_open].tolist() for c in ("account", "day", "historical_day", "trade_index")]
    mine = sorted(zip(*cols))
    theirs = sorted((int(o["account"]), int(o["day"]), int(o["historical_day"]), int(o["trade_index"])) for o in ops)
    if [tuple(int(v) for v in x) for x in mine] != theirs:
        out.append(f"{tag}: the recorded openings {mine[:3]} are not the ledger's {theirs[:3]}")
    routed = np.asarray(t["source"]) == "strategy"
    off = routed & (np.asarray(t["day"]) != np.asarray(t["historical_day"]) + 1)
    if off.any():
        out.append(f"{tag}: {int(off.sum())} routed trades are not on their own session (calendar day = historical "
                   "day + 1)")
    by_acct = {int(acc): i for i, acc in enumerate(np.asarray(t["account"])[is_open].tolist())}
    open_idx = np.flatnonzero(is_open)
    for k in range(len(a["account"])):
        if not bool(a["opened"][k]):
            continue
        acc = int(a["account"][k])
        i = by_acct.get(acc)
        if i is None:
            out.append(f"{tag}: funded {acc} opened but its opening trade is not in the record")
            continue
        j = int(open_idx[i])
        wait, rel = int(a["opening_session"][k]), int(a["opening_rel_day"][k])
        if not (wait == rel == int(a["opening_day"][k]) - int(a["activation_day"][k]) - 1):
            out.append(f"{tag}: funded {acc}'s wait {wait} is not its opening's relative session {rel} (opened on day "
                       f"{a['opening_day'][k]}, activated on {a['activation_day'][k]})")
        if (int(t["day"][j]), int(t["account_session"][j]), int(t["rel_day"][j])) != (int(a["opening_day"][k]), wait,
                                                                                        rel):
            out.append(f"{tag}: funded {acc}'s accounts row does not agree with its opening trade's row")
    return out


class ReplayReducer:
    """One (design, arm, response)'s reducer for the U1 replay, a start at a time. Module level, holding numpy arrays
    only, so it pickles to a worker with its task."""

    def __init__(self, *, design: str, arm: str, response: str, enforcement_p: float, meta: PR.BlockMeta,
                 combine_floor0: float, funded_floor0: float, mll: float, columns: Sequence[str] | None):
        self.design, self.arm, self.response = str(design), str(arm), str(response)
        self.enforcement_p = float(enforcement_p)
        self.meta = meta
        self.combine_floor0, self.funded_floor0, self.mll = float(combine_floor0), float(funded_floor0), float(mll)
        self.columns = None if columns is None else tuple(columns)

    def recording_args(self, a: dict[str, Any]) -> dict[str, Any]:
        return recording_args(a)

    def reduce(self, lp: Any, start_day: int, n_sessions: int, start_seed: int, start_date: str
               ) -> tuple[Any, dict[str, Any]]:
        """A start's recorded long replay -> (the unrecorded call's path: its ledger and day rows dropped, every other
        field the engine's; the start's record)."""
        s, h = int(start_day), int(n_sessions)
        tag = f"{self.design} {self.arm} {self.response} start {s}"
        if len(lp.path.cash_series) != h + 1:
            raise RuntimeError(f"{tag}: {len(lp.path.cash_series)} closes for a replay of {h} sessions")
        rec = PR.record_path(lp, path=s, path_seed=int(start_seed), shift=f"{self.design} {self.arm} {self.response}",
                             enforcement_p=self.enforcement_p, meta=self.meta.window(s, h),
                             combine_floor0=self.combine_floor0, funded_floor0=self.funded_floor0, mll=self.mll)
        problems = list(rec["problems"]) + opening_problems(lp, rec, s, tag)
        keep = TRADE_DATA if self.columns is None else tuple(c for c in TRADE_DATA if c in set(self.columns))
        out = {"design": self.design, "arm": self.arm, "response": self.response, "enforcement_p": self.enforcement_p,
               "start_day": s, "start_date": str(start_date), "start_seed": int(start_seed), "sessions": h,
               "n_trades": int(len(rec["trades"]["place"])),
               "trades": {c: rec["trades"][c] for c in keep},
               "accounts": {c: rec["accounts"][c] for c in ACCOUNT_DATA},
               "counts": {p: int(rec["counts"].get(p, 0)) for p in PR.SINGLE_PLACES},
               "problems": problems[:MAX_PROBLEMS]}
        return replace(lp, trades=(), account_days=(), campaign_days=()), out


def _campaign_values(r: dict[str, Any]) -> dict[str, Any]:
    return {c: r[c] for c in PF.REPLAY_CAMPAIGN_COLUMNS}


def frame(recs: Sequence[dict[str, Any]], part: str, columns: Sequence[str] | None = None) -> pd.DataFrame:
    """Starts' records as one frame (`part`: 'trades' or 'accounts'): the replay's campaign group, then the data
    columns (`columns`, in the schema's order; None: every one the records hold), in record order and row order."""
    fields = PF.REPLAY_TRADE_FIELDS if part == "trades" else PF.REPLAY_ACCOUNT_FIELDS
    data = TRADE_DATA if part == "trades" else ACCOUNT_DATA
    if columns is not None:
        data = tuple(c for c in data if c in set(columns))
    elif recs:
        data = tuple(c for c in data if c in recs[0][part])
    names = list(PF.REPLAY_CAMPAIGN_COLUMNS) + list(data)
    kinds = {"int": np.int64, "float": float, "bool": bool, "str": object, "object": object}
    dtype = {f.name: kinds[f.dtype] for f in fields}
    chunks = []
    for r in recs:
        n = len(next(iter(r[part].values()))) if r[part] else (r["n_trades"] if part == "trades" else
                                                              len(r["accounts"]["account"]))
        cols = {c: np.full(n, v, dtype=dtype[c]) for c, v in _campaign_values(r).items()}
        cols.update({c: r[part][c] for c in data})
        chunks.append(pd.DataFrame(cols, columns=names))
    if not chunks:
        return pd.DataFrame({c: pd.Series(dtype=dtype[c]) for c in names})
    return pd.concat(chunks, ignore_index=True)


class ReplayRecorder:
    """What a run of `user_beside.run_starts(..., recorder=...)` records, and its records afterwards; one recorder may
    record several runs (design, arm, response), each once.

    `offer_ids`: one id a trade, block by block in each block's trade order, over the job's blocks (as
    `place_records.block_offer_ids` builds them from a trade table; None: no ids); `columns`: the trade columns kept
    beside the campaign group (None: all of `place_fields.REPLAY_TRADE_COLUMNS`; `()`: none)."""

    def __init__(self, *, offer_ids: Sequence[Sequence[Any]] | None = None, columns: Sequence[str] | None = None):
        self.offer_ids = None if offer_ids is None else list(offer_ids)
        if columns is not None:
            unknown = [c for c in columns if c not in PF.REPLAY_TRADE_COLUMNS]
            if unknown:
                raise ValueError(f"unknown trade columns {unknown}; the record's are "
                                 "place_fields.REPLAY_TRADE_COLUMNS")
            columns = tuple(c for c in TRADE_DATA if c in set(columns))
        self.columns = columns
        self._recs: dict[tuple[str, str, str], list[dict[str, Any]]] = {}

    def reducer(self, design: str, arm: str, resp: Any, job: dict[str, Any]) -> ReplayReducer:
        """The run's reducer, made (and everything it can refuse refused) before any start runs: a key already held
        (`RuntimeError`), a path already carrying a recorder, offer ids that do not number the job's blocks
        (`ValueError`)."""
        key = (str(design), str(arm), str(resp.name))
        if key in self._recs:
            raise RuntimeError(f"REFUSED (Q-94): the recorder already holds {key}: each run is recorded once")
        path = job["args"]["path"]
        bad = sorted(k for k in RECORDERS if k in path)
        if bad:
            raise ValueError(f"REFUSED (Q-94): the replay's path arguments already carry {bad}")
        rules = path["rules"]
        meta = PR.BlockMeta(job["blocks"], dates=job["dates"], offer_ids=self.offer_ids)
        return ReplayReducer(design=key[0], arm=key[1], response=key[2], enforcement_p=float(resp.enforcement_p),
                             meta=meta, combine_floor0=-float(rules.mll), funded_floor0=float(rules.xfa_mll_start),
                             mll=float(rules.mll), columns=self.columns)

    def collect(self, design: str, arm: str, response: str, recs: Sequence[dict[str, Any]],
                start_days: Sequence[int]) -> None:
        """Take one run's records (one a start, in start order) -- refused unless they are one a start of the run's
        outputs, in their order."""
        key = (str(design), str(arm), str(response))
        if key in self._recs:
            raise RuntimeError(f"the recorder already holds {key}")
        got = [int(r["start_day"]) for r in recs]
        if got != [int(s) for s in start_days]:
            raise RuntimeError(f"{key}: the records' starts {got[:5]}... are not the outputs' "
                               f"{list(start_days)[:5]}...")
        self._recs[key] = list(recs)

    # ---- the records

    def recorded(self) -> list[tuple[str, str, str]]:
        return list(self._recs)

    def _keys(self, design: str | None, arm: str | None, response: str | None) -> list[tuple[str, str, str]]:
        return [k for k in self._recs if (design is None or k[0] == design) and (arm is None or k[1] == arm)
                and (response is None or k[2] == response)]

    def per_start(self, design: str, arm: str, response: str) -> list[dict[str, Any]]:
        """The run's records, one a start, in start order (each: the campaign values, `sessions`, `n_trades`, the kept
        trade columns, the accounts, the counts by place, the problems)."""
        return list(self._recs[(str(design), str(arm), str(response))])

    def trades(self, design: str | None = None, arm: str | None = None, response: str | None = None) -> pd.DataFrame:
        """One row a simulated trade of the runs named (every run when none), in run, start and ledger order."""
        recs = [r for k in self._keys(design, arm, response) for r in self._recs[k]]
        return frame(recs, "trades", TRADE_DATA if self.columns is None else self.columns)

    def accounts(self, design: str | None = None, arm: str | None = None, response: str | None = None
                 ) -> pd.DataFrame:
        """One row a funded account of a start's replay, opened or not: its opening and its wait."""
        recs = [r for k in self._keys(design, arm, response) for r in self._recs[k]]
        return frame(recs, "accounts", ACCOUNT_DATA)

    def openings(self, design: str | None = None, arm: str | None = None, response: str | None = None
                 ) -> pd.DataFrame:
        """The funded openings (place c), one a funded account that traded, each counted once per start in whose
        replay it falls."""
        t = self.trades(design, arm, response)
        if "place" not in t.columns:
            raise ValueError("the kept columns hold no `place`")
        return t[t["place"] == OPENING].reset_index(drop=True)

    def counts(self, design: str, arm: str, response: str) -> Counter:
        """The run's trades by place (the vendored `records_counts`', summed over starts), with (a)."""
        c: Counter = Counter()
        for r in self._recs[(str(design), str(arm), str(response))]:
            c.update(r["counts"])
        c["a_every_trade"] = sum(int(c.get(p, 0)) for p in PR.SINGLE_PLACES)
        return c

    def problems(self) -> list[str]:
        """Every failed per-start check of every recorded run (empty when the records hold)."""
        return [p for recs in self._recs.values() for r in recs for p in r["problems"]]


def check_recorder(recorder: Any) -> ReplayRecorder:
    """Refuse (`TypeError`) anything that is not a `ReplayRecorder` (the gate's `PlaceRecorder` records a gate call)."""
    if not isinstance(recorder, ReplayRecorder):
        raise TypeError(f"recorder must be an extended.replay_records.ReplayRecorder, got a {type(recorder).__name__}")
    return recorder


__all__ = ["RECORDERS", "TRADE_DATA", "ACCOUNT_DATA", "recording_args", "opening_problems", "ReplayReducer", "frame",
           "ReplayRecorder", "check_recorder"]
