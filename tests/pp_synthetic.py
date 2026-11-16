"""RD-02's build checks on synthetic campaigns (`prereg/RD-02_payout_policy.md` 13.3; Q-105), run by
`tests/test_pp_build.py`, one section a process (the vendored tree goes on this process's `sys.path`):

    python tests/pp_synthetic.py <repository root> <section>      # prints one JSON line last

No bar, no atlas, no walk: day blocks generated here, through the vendored engine. The toy campaigns draw from section
11's build seed, imported from its one home in code (`identity/gate_identity.py`'s `SYN_SEED`, Q-47's synthetic
identity, which section 11 names), never written here. The registered no-closure table (a vendored configuration, not
an outcome) is read by T-4's walk only.

Sections (each a list of problems; empty when the section holds; notes for checks not made, never a pass):

* `t1` -- with both levers off, the adapter's funded account equals the vendored one bit for bit: every day row
  (balance, floor, request, recorded `eligible` ...), every funded and evaluation record, the cash, the conduct record;
  with a win-day-keyed table and with none; the replay and resampled days. The counters all zero (8.1 item 4).
* `t2` -- `lock`: no first payout while the floor is below the lock; the first request at the first eligible close with
  the floor locked, at the maximum; later requests the base's at every eligible close; a held close recorded `eligible`
  True and `requested` 0, counted by the class; an account whose floor locked and whose balance fell back is not held
  (the class's eligibility directly); under the placement on, no Consistency-path account held by `lock`.
* `t3` -- the early block at every horizon of 5 item 3 is byte-identical when every session from 2024-01-02 is
  replaced, the verdict arm's constant shift held; the late block and an unpurged early selection do change.
* `t4` -- the held-state rule on toy campaigns (fires only after a held close, re-read at every close, never under the
  base's rule; the decision the four-day leaf in the declared mode, the five-day leaf where it trades in the minimal
  rescue) and on the registered table (the four-day leaf trades wherever a held account can be; the bands where it
  equals, rescues, and changes R -- two, the risk unchanged; the minimal rescue differing only there).
* `t5` -- `half`: every request half the maximum and at least the minimum; an eligible balance whose half request is
  under the minimum holds (counted); the tier read from the session's opening balance, after a payout too; under the
  placement on, a Consistency-path account's request half of its own maximum.
* `t7` -- 8.2's oracles on toy campaigns: the zero-edge martingale bound per cell; every request within its bounds and
  paid at the split less the fee; `lock`'s floor; `half`'s exact half.
* `t10r`, `t10g` -- the counters' channel on the U1 replay and the gate, at one worker: with it on, every output
  (replay) and every row and path record (gate) equals it off; the counts equal the class's own (the replay run
  directly; each gate path's, on a table-bearing toy, collected where it ran by `tests/pp_gate_direct.py`); every held
  close followed by its held read; the levers' counts (`LEVER_KEYS`) zero in `ref`, the engine's Consistency counts
  carried under the placement; refusals. `t10w2` (slow): the two legs at two workers (Q-106's M1).
* `absent` -- the adapter with the channel absent equals master's before Q-105 (`git show 4c57ce6:extended/
  user_beside.py`, its text pinned by sha256) bit for bit on all 19 responses; the gate's re-composition proof holds
  with Q-105's marker.
"""
from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import io
import json
import math
import subprocess
import sys
import time
import types
from pathlib import Path
from typing import Any

REPO = Path(sys.argv[1])
SECTION = sys.argv[2]
for _p in (str(REPO), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import gate_identity as GI  # noqa: E402

from extended import payout_policy as PP  # noqa: E402
from extended import pp_reading as RD  # noqa: E402
from propedge.campaign.lockstep import EPS, ConductModel, child_seed, simulate_lockstep_path  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers  # noqa: E402
from propedge.campaign.shared_days import SharedDayDraws  # noqa: E402
from propedge.campaign.sizing import SizingRule  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

#: section 11's build seed (the toys and T-3), from its home in code
SEED = int(GI.SYN_SEED)
RULES = rules_from_ledger()
RISK = 300.0
N_DAYS = 200
#: the adapter before Q-105: master at 4c57ce6 (the file last changed at 4f8b556, Q-100); the sha256 of its LF text
BASE_COMMIT = "4c57ce6"
BASE_SHA256 = "23c26773274287674bf43873a5a3b846649985531ff6630401c9da3ca0a7227d"
problems: list[str] = []
notes: list[str] = []


def _frames():
    f = sys._getframe(1)
    while f is not None:
        yield f
        f = f.f_back


def rng(*key: int) -> np.random.Generator:
    return np.random.default_rng([SEED, *[int(k) for k in key]])


def blocks_for(key: int, n: int = N_DAYS, *, p_win: float = 0.45, bad_every: int = 0, rpc: float | None = None,
               rr: float = 2.0) -> list[DayBlock]:
    """`n` days of one to three trades at RISK, each won at `rr` R with probability `p_win`, else stopped; every
    `bad_every`-th pair of days all lost; `rpc` the risk per micro (tier sizing). At `rr` 1 the losers are not smaller
    than the winners, one of the placement's own triggers (`lockstep.py` 1940-1946), so the placement toys use it."""
    g = rng(10, key)
    out = []
    for i in range(n):
        k = int(g.integers(1, 4))
        win = g.random(k) < p_win
        if bad_every and (i % bad_every) in (bad_every - 2, bad_every - 1):
            win[:] = False
        et = 500.0 + 60.0 * np.arange(k, dtype=float)
        kw: dict[str, Any] = {}
        if rpc is not None:
            kw["risk_per_contract"] = np.full(k, float(rpc))
        out.append(DayBlock(pnl=np.where(win, rr * RISK, -RISK).astype(float), risked=np.full(k, RISK),
                            exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0,
                            **kw))
    return out


def toy_table() -> RiskPolicy:
    """A table keyed on the winning days, so the held rule's three classes all occur: funded below $500 the five-day
    leaf is the four-day one (unchanged); from $500 to $1,000 it trades nothing (rescued); from $1,000 it trades at a
    smaller risk (changed); paid, the same leaf. Risk only (no R): the shared-day draws keep each trade's own R."""
    lf = lambda name, risk, mt=None: Leaf(name, risk, None, mt)  # noqa: E731
    funded = Tiers(on="balance", tiers=(
        (-1e9, Tiers(on="win_days", tiers=((0.0, lf("funded low, 0-4", RISK)), (5.0, lf("funded low, 0-4", RISK))))),
        (500.0, Tiers(on="win_days", tiers=((0.0, lf("funded mid, 0-4", RISK)), (5.0, lf("funded mid, 5", RISK, 0))))),
        (1000.0, Tiers(on="win_days", tiers=((0.0, lf("funded high, 0-4", RISK)),
                                             (5.0, lf("funded high, 5", RISK * 2 / 3))))),
    ))
    paid = Tiers(on="win_days", tiers=((0.0, lf("paid, 0-4", RISK)), (5.0, lf("paid, 5", RISK))))
    return RiskPolicy(id="pp_toy_table", root=Phase(combine=lf("combine", RISK), funded=funded, paid=paid))


def protocol(frac: float = 1.0) -> Protocol:
    p = Protocol(name="pp_toy", combine_rr=2.0, combine_risk=RISK, funded_rr=2.0, funded_risk=RISK, trades_per_day=3,
                 max_concurrent_accounts=5)
    return p if frac == 1.0 else dataclasses.replace(p, payout_frac=frac)


def run(cls: type | None, proto: Protocol, blocks: list, *, table: Any = "toy", path_seed: int = 1,
        replay: bool = True, rtp: bool = False, sizing: Any = None, trades: bool = False):
    sd = SharedDayDraws({0: list(blocks)}, seed=int(child_seed(SEED, 20, path_seed)), replay=replay, protocol=proto,
                        mode="rotation", flip=None, sizing=sizing)
    kw = dict(edge=0.0, rules=RULES, initial_bankroll=1e9, max_concurrent_accounts=5,
              subscription=float(RULES.subscription), billing_days=int(RULES.billing_days),
              activation=float(RULES.activation), payout_lag_days=3, max_concurrent_combines=5, max_total_accounts=5,
              conduct=ConductModel(rtp=bool(rtp), enforcement_p=0.0), combine_max_days=2000,
              funded_horizon_days=100_000, record_days=True, record_trades=bool(trades))
    if table is not None:
        kw["risk_policy"] = toy_table() if table == "toy" else table
    if cls is not None:
        kw["funded_account_cls"] = cls
    return simulate_lockstep_path(proto, seed=int(child_seed(SEED, 21, path_seed)), horizon_days=len(blocks) + 1,
                                  **kw, **sd.lockstep_kwargs())


def counted(cls: type, *a: Any, **k: Any):
    with PP.collecting() as got:
        lp = run(cls, *a, **k)
    return lp, {int(r["index"]): r for r in got}


def funded_rows(lp) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for r in lp.account_days:
        if r["kind"] == "funded":
            out.setdefault(int(r["index"]), []).append(r)
    return {k: sorted(v, key=lambda r: int(r["day"])) for k, v in out.items()}


def closes(lp, rules=RULES, cap: float | None = None) -> dict[int, list[dict[str, Any]]]:
    """Each funded account's closes from the daily recorder, with what the checks read: the close's balance before
    any request, the floor at the close before any request (the engine's 16:00 lock from the previous close), the
    base's request there, whether it was a first request."""
    cap = float(rules.std_cap) if cap is None else cap
    out = {}
    recs = {int(f.index): f for f in lp.funded}
    for idx, rows in funded_rows(lp).items():
        prev_floor = float(rules.xfa_mll_start)
        paid = 0
        cons = bool(recs[idx].consistency_forced) if idx in recs else False
        mine = []
        for r in rows:
            req = float(r["requested"] or 0.0)
            b_close = float(r["balance"]) + req
            f_close = min(float(rules.xfa_lock_at), max(prev_floor, b_close - float(rules.mll)))
            mine.append({"day": int(r["day"]), "eligible": bool(r["eligible"]), "requested": req, "b": b_close,
                         "f": f_close, "base": PP.base_request(b_close, rules, cap), "paid_before": paid,
                         "closed": r["state"] == "closed", "regime": r["regime"], "consistency": cons})
            prev_floor = float(r["floor"])
            paid += int(req > 0)
        out[idx] = mine
    return out


def check(cond: bool, what: str) -> None:
    if not cond:
        problems.append(what)


def zero_counts(rows: dict[int, dict[str, Any]], what: str) -> None:
    """The levers off: the levers' own counts zero (`LEVER_KEYS`; the two `cons_*` counts are the engine's)."""
    tot = PP.lever_totals(rows.values())
    check(not any(tot.values()), f"{what}: the levers' counts are not all zero ({tot})")


# ------------------------------------------------------------------------------------------------ T-1


def section_t1() -> None:
    cases = [("toy table, replay", "toy", True, 1), ("no table, replay", None, True, 2)]
    cases += [(f"toy table, resampled path {k}", "toy", False, k) for k in (3, 4, 5)]
    for what, table, replay, ps in cases:
        blocks = blocks_for(ps)
        base = run(None, protocol(), blocks, table=table, path_seed=ps, replay=replay)
        mine, rows = counted(PP.PPElig, protocol(), blocks, table=table, path_seed=ps, replay=replay)
        for name in ("account_days", "funded", "combines", "path", "conduct", "trades"):
            d = GI.deep_difference(getattr(base, name), getattr(mine, name), name)
            check(d is None, f"T-1 {what}: the adapter at both levers off differs from the vendored account: {d}")
        check(len(base.funded) >= 3 and sum(f.n_payouts for f in base.funded) >= 3,
              f"T-1 {what}: the toy pays too little to test anything ({len(base.funded)} accounts)")
        zero_counts(rows, f"T-1 {what}")
        check(set(rows) == {int(f.index) for f in mine.funded}, f"T-1 {what}: the collection missed an account")


# ------------------------------------------------------------------------------------------------ T-2


def section_t2() -> None:
    lock_at, lock_bal, pmin = float(RULES.xfa_lock_at), PP.lock_balance(RULES), float(RULES.payout_min)
    check(lock_bal == float(RULES.xfa_lock_at) - float(RULES.xfa_mll_start), "T-2: the lock balance is not the ledger's")
    held_total = first_total = fell_back = 0
    for ps in (1, 6, 7):
        lp, rows = counted(PP.PPLock, protocol(), blocks_for(ps), path_seed=ps)
        for idx, cl in closes(lp).items():
            first_seen = False
            held_here = 0
            reached = False
            for c in cl:
                elig_close = c["eligible"] and c["base"] >= pmin - EPS and not c["closed"]
                if c["paid_before"] == 0:
                    if c["requested"] > 0:
                        check(c["f"] >= lock_at - EPS, f"T-2: account {idx} took its first payout on day {c['day']} "
                                                       f"with the floor at {c['f']:.2f}, below the lock")
                        check(abs(c["requested"] - c["base"]) <= 1e-9, f"T-2: account {idx}'s first request on day "
                                                                         f"{c['day']} is not the maximum")
                        check(not first_seen, f"T-2: account {idx} asked late (an earlier eligible close was locked)")
                    elif elig_close:
                        if c["f"] >= lock_at - EPS:
                            first_seen = True
                            problems.append(f"T-2: account {idx} did not ask at day {c['day']}, eligible and locked")
                        else:
                            held_here += 1                     # a held close: recorded eligible True, requested 0
                            check(c["eligible"] is True and c["requested"] == 0.0, "T-2: a held close's record")
                            if reached:
                                fell_back += 1
                else:
                    if elig_close:
                        check(abs(c["requested"] - c["base"]) <= 1e-9,
                              f"T-2: account {idx} at day {c['day']}: a later request is not the base's")
                    else:
                        check(c["requested"] == 0.0, f"T-2: account {idx} asked at day {c['day']}, not eligible")
                reached = reached or c["b"] >= lock_bal - EPS
            held_total += held_here
            first_total += int(rows[idx]["first_requests_held"])
            check(int(rows[idx]["first_request_closes_held"]) == held_here,
                  f"T-2: account {idx}: the class counts {rows[idx]['first_request_closes_held']} closes holding its "
                  f"first request, the record {held_here}")
            check(int(rows[idx]["first_requests_held"]) == int(held_here > 0),
                  f"T-2: account {idx}: first requests held {rows[idx]['first_requests_held']}, per account, is not "
                  f"{int(held_here > 0)}")
        last = len(blocks_for(ps))
        check(not PP.read_problems(rows.values(), last), f"T-2: {PP.read_problems(rows.values(), last)[:2]}")
    check(held_total > 0, "T-2: lock held no first request on the toys (nothing tested)")
    # an account whose floor locked and whose balance fell back is not held: the class's own eligibility
    acct = PP.PPLock(index=0, activation_day=0, draw=types.SimpleNamespace(settlement="pessimistic"),
                     horizon_days=100, floor_start=float(RULES.xfa_mll_start))
    acct.win_days = int(RULES.std_winning_days)
    acct.B, acct.F = lock_bal / 2.0, lock_at                      # reached the lock balance once, fell back
    check(acct._standard_eligible(RULES) is True, "T-2: a locked account that fell back is held")
    acct.F = lock_at - lock_bal / 4.0                              # never locked
    check(acct._standard_eligible(RULES) is False, "T-2: an unlocked, eligible, unpaid account is not held")
    check(acct.__dict__["_pp_firm_elig"] is True, "T-2: the firm's eligibility is not kept beside the policy's")
    # the placement on: Consistency-path accounts are never held by lock
    lp, rows = counted(PP.PPLock, protocol(), blocks_for(8, n=300, rr=1.0, p_win=0.65), path_seed=8, rtp=True)
    cons = [f for f in lp.funded if f.consistency_forced]
    if not cons:
        problems.append("T-2: the placement toy put no account on the Consistency path (nothing tested)")
    for f in cons:
        r = rows[int(f.index)]
        check(r["first_requests_held"] == 0 and r["first_request_closes_held"] == 0 and not r["held_days"]
              and r["elig_differs"] == 0 and r["held_closes"] == 0,
              f"T-2: Consistency account {f.index} was held by lock ({r})")
    would = sum(int(rows[int(f.index)]["cons_first_payout_floor_below_lock"]) for f in cons)
    check(sum(int(f.n_payouts) for f in cons) > 0, "T-2: no Consistency-path account was paid (nothing tested)")
    out["t2"] = {"held_first_requests": held_total, "consistency_accounts": len(cons),
                 "consistency_first_payouts_below_lock": would, "fell_back_then_held": fell_back}


# ------------------------------------------------------------------------------------------------ T-3


def section_t3() -> None:
    days = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", "2026-07-16")]
    n = len(days)
    cut = next(i for i, d in enumerate(days) if d >= "2024-01-02")
    shift = -0.0375                                               # the verdict arm's bound: one constant, both runs
    x = rng(30).normal(0.0, 1.0, n) + shift
    y = x.copy()
    y[cut:] = rng(31).normal(5.0, 3.0, n - cut) + shift           # every session from 2024-01-02 replaced

    def records(v: np.ndarray) -> list[dict[str, Any]]:
        return [{"start_day": s, "start_date": days[s], "observed": n - s, "v": v} for s in range(n)]

    def value(r: dict[str, Any], h: int) -> float:
        s = int(r["start_day"])
        return float(r["v"][s:s + h].sum())

    measures = {h: next(k for k, v in RD.HORIZONS.items() if v == h) for h in RD.HORIZON_SET}
    for h, m in measures.items():
        a = RD.reading(records(x), "early", m, value)
        b = RD.reading(records(y), "early", m, value)
        check(a["starts"] == b["starts"] and a["values"].tobytes() == b["values"].tobytes()
              and all(np.float64(a[k]).tobytes() == np.float64(b[k]).tobytes() for k in ("mean", "p10", "p50", "p90")),
              f"T-3: the early block at h = {h} ({m}) changed when 2024 on was replaced")
        check(max(a["starts"]) + h <= cut, f"T-3: the early block at h = {h} reads a 2024 session")
        la, lb = RD.reading(records(x), "late", m, value), RD.reading(records(y), "late", m, value)
        check(la["values"].tobytes() != lb["values"].tobytes(), f"T-3: the late block at h = {h} did not change")
        naive = [s for s in range(n) if days[s] < "2024-01-01" and n - s >= h]   # the starts of 2023, unpurged
        check(any(value(records(x)[s], h) != value(records(y)[s], h) for s in naive),
              f"T-3: an unpurged early selection at h = {h} would not change (the check is vacuous)")
    check(not RD.card_horizon_problems(), f"T-3: the card's horizons: {RD.card_horizon_problems()}")
    check(not RD.journey_horizon_problems(), f"T-3: Q-17's windows: {RD.journey_horizon_problems()}")
    out["t3"] = {"horizons": sorted(measures), "cut": days[cut]}


# ------------------------------------------------------------------------------------------------ T-4


def _expected_reads(cl: list[dict[str, Any]], last_day: int) -> set[int]:
    """The sessions a held account is read at: the day after each held close, while the account lives."""
    out = set()
    for c in cl:
        held = (c["eligible"] and c["requested"] == 0.0 and c["base"] >= float(RULES.payout_min) - EPS
                and not c["closed"] and not c["consistency"])
        if held and c["day"] + 1 <= last_day:
            out.add(c["day"] + 1)
    return out


def section_t4() -> None:
    table = toy_table()
    cls_seen = {k: 0 for k in PP.HELD_CLASSES}
    hf = PP.held_win_days(RULES)
    check(hf == int(RULES.std_winning_days) - 1, "T-4: the held count is not the ledger's winning days less one")
    for cell, cls, frac in (("lock", PP.PPLock, 1.0), ("half", PP.PPElig, PP.half_fraction()),
                            ("lock minimal", PP.PPLockMinimal, 1.0)):
        for ps in (1, 6):
            lp, rows = counted(cls, protocol(frac), blocks_for(ps), path_seed=ps)
            last_day = max(int(r["day"]) for r in lp.account_days)
            byidx = closes(lp)
            alive_days = {k: {c["day"] for c in v} for k, v in byidx.items()}
            for idx, cl in byidx.items():
                want = {d for d in _expected_reads(cl, last_day) if d in alive_days[idx]}
                got = set(rows[idx]["held_days"])
                check(want <= got <= _expected_reads(cl, last_day),
                      f"T-4 {cell}: account {idx}'s held reads {sorted(got)[:6]} are not its held closes' next "
                      f"sessions {sorted(want)[:6]}")
                for k in PP.HELD_CLASSES:
                    cls_seen[k] += int(rows[idx][f"held_{k}"])
                # the decision the engine took at a held session: the four-day leaf (declared), or in the minimal rescue
                # the five-day leaf wherever it trades
                prev = {c["day"]: c for c in cl}
                for c in cl:
                    if c["day"] not in got or (c["day"] - 1) not in prev:
                        continue
                    p = prev[c["day"] - 1]
                    paid = p["paid_before"] + int(p["requested"] > 0) > 0
                    b = p["b"] - p["requested"]
                    f = float(RULES.xfa_lock_at) if p["requested"] > 0 else p["f"]
                    st = {"phase": "paid" if paid else "funded", "balance": b, "cushion": b - f,
                          "cushion_frac": (b - f) / float(RULES.mll), "days_in_state": 0, "day": c["day"],
                          "win_days": int(RULES.std_winning_days), "line_gap": 1.0 if paid else -1e13,
                          "request_day": 0}
                    d5, d4 = table.decide(st), table.decide(dict(st, win_days=hf))
                    want_reg = d4.regime
                    if cls is PP.PPLockMinimal and PP.held_class(d5, d4) != "rescued":
                        want_reg = d5.regime
                    check(c["regime"] == want_reg, f"T-4 {cell}: account {idx} day {c['day']}: the decision "
                                                   f"{c['regime']!r}, not {want_reg!r}")
        _, ref_rows = counted(PP.PPElig, protocol(), blocks_for(1), path_seed=1)
        zero_counts(ref_rows, "T-4 ref")
    check(all(cls_seen[k] > 0 for k in PP.HELD_CLASSES), f"T-4: the toy did not show every class: {cls_seen}")
    # m2: every held close the account outlives is followed by one held read (the runner refuses otherwise)
    for cls, frac in ((PP.PPLock, 1.0), (PP.PPElig, PP.half_fraction()), (PP.PPLockMinimal, 1.0)):
        n_closes = 0
        for ps in (1, 6):
            blocks = blocks_for(ps)
            _, rows = counted(cls, protocol(frac), blocks, path_seed=ps)
            rp = PP.read_problems(rows.values(), len(blocks))
            check(not rp, f"T-4 {cls.__name__}: {rp[:2]}")
            n_closes += sum(r["held_closes"] for r in rows.values())
        check(n_closes > 0, f"T-4 {cls.__name__}: no held close on the toys (the reads' check tests nothing)")
    # m2: the held read's vendored sources are pinned, and a changed pin refuses
    PP.check_vendored_sources()
    keep = dict(PP.VENDORED_SOURCES_SHA256)
    PP.VENDORED_SOURCES_SHA256["propedge.campaign.risk_policy.account_state"] = "0" * 64
    PP._CACHE.pop("sources_ok", None)
    try:
        PP.check_vendored_sources()
        problems.append("T-4: a changed vendored source was not refused")
    except RuntimeError:
        pass
    finally:
        PP.VENDORED_SOURCES_SHA256.update(keep)
        PP._CACHE.pop("sources_ok", None)
        PP.check_vendored_sources()
    # m1 (X4): an AttributeError inside the held read is refused, never read as the engine's zero days
    import dataclasses as _dc

    @_dc.dataclass(frozen=True)
    class FaultyTable(RiskPolicy):
        def decide(self, state):
            if any(f.f_code.co_name == "_held_read" for f in _frames()):
                raise AttributeError("a planted fault inside the held read")
            return RiskPolicy.decide(self, state)

    faulty = FaultyTable(id="pp_faulty", root=toy_table().root)
    try:
        run(PP.PPLock, protocol(), blocks_for(6), table=faulty, path_seed=6)
        problems.append("T-4: an AttributeError inside the held read was not refused (read as zero days?)")
    except RuntimeError as exc:
        check("REFUSED" in str(exc), f"T-4: the held read's fault refused without its reason: {exc}")
    # the registered table, walked (6.3's read of the vendored file)
    import a3_brk30_cb20 as C

    from propedge import RESULTS_DIR

    pol = C.noclose_plan(RESULTS_DIR)
    pmin, frac, cap = float(RULES.payout_min), float(RULES.payout_max_frac_of_balance), float(RULES.std_cap)
    lock_at, mll = float(RULES.xfa_lock_at), float(RULES.mll)
    bands: dict[tuple, dict[str, Any]] = {}
    for phase in ("funded", "paid"):
        for b in np.arange(0.0, 6200.0, 25.0):
            if min(frac * b, cap) < pmin - EPS:
                continue                                         # no held account at this balance
            floors = [lock_at] if (phase == "paid" or b >= mll) else np.arange(min(lock_at, b - mll), lock_at + 1, 25.0)
            for f in floors:
                f = float(min(f, lock_at))
                if b <= f:
                    continue
                st = {"phase": phase, "balance": float(b), "cushion": float(b - f), "cushion_frac": (b - f) / mll,
                      "days_in_state": 0, "day": 0, "win_days": int(RULES.std_winning_days),
                      "line_gap": 0.01 if phase == "paid" else -1e13, "request_day": 0}
                d5, d4 = pol.decide(st), pol.decide(dict(st, win_days=hf))
                key = (phase, pol._branch(st))
                bands.setdefault(key, {"phase": phase, "balance": float(b), "cushion": float(b - f),
                                       "class": PP.held_class(d5, d4), "d5": d5, "d4": d4})
                check(not (d4.max_trades is not None and int(d4.max_trades) == 0),
                      f"T-4: the four-day leaf trades nothing at {phase} balance {b}, cushion {b - f}")
    by = {k: [v for v in bands.values() if v["class"] == k] for k in PP.HELD_CLASSES}
    changed = by["r_changed"]
    check(len(changed) == 2 and all(v["phase"] == "funded" for v in changed),
          f"T-4: the registered table changes the leaf in {len(changed)} held bands, not the two funded ones: "
          f"{[(v['phase'], v['balance'], v['cushion']) for v in changed]}")
    for v in changed:
        check(v["d5"].risk == v["d4"].risk and v["d5"].rr != v["d4"].rr,
              f"T-4: a changed band changes the risk, or not R: {v['phase']} {v['balance']} {v['cushion']}")
    # the minimal rescue differs from the declared rule only in those bands
    diff = [k for k, v in bands.items() if (v["class"] != "rescued") and PP._decision_key(v["d4"]) != PP._decision_key(
        v["d5"])]
    check(sorted(diff) == sorted(k for k, v in bands.items() if v["class"] == "r_changed"),
          "T-4: the minimal rescue differs from the declared rule outside the changed bands")
    out["t4"] = {"toy_classes": cls_seen,
                 "registered": {k: len(v) for k, v in by.items()},
                 "changed_bands": [{"balance": v["balance"], "cushion": v["cushion"], "risk": v["d5"].risk,
                                    "rr_five": v["d5"].rr, "rr_four": v["d4"].rr} for v in changed]}


# ------------------------------------------------------------------------------------------------ T-5


def section_t5() -> None:
    half = PP.half_fraction()
    check(half == 0.5, f"T-5: L2's half is {half}, not one half (the vendored fast_half arm, D-564's FRACS)")
    pmin = float(RULES.payout_min)
    rule = SizingRule.from_ledger()
    cut = posts = moved = 0
    for ps in (1, 6, 9):
        lp, rows = counted(PP.PPElig, protocol(half), blocks_for(ps, rpc=RISK / 12.0), path_seed=ps,
                           sizing=rule, trades=True)
        led = [r for r in lp.trades if r["kind"] == "funded"]
        first: dict[tuple[int, int], dict[str, Any]] = {}
        for r in led:
            first.setdefault((int(r["index"]), int(r["day"])), r)
        for (idx, day), r in first.items():                  # the tier: the session's opening balance's cap
            if r.get("cap_micros") is not None:
                want = rule.cap_micros("funded", float(r["balance_before"]))
                check(int(r["cap_micros"]) == int(want), f"T-5: account {idx} day {day}: the tier's cap "
                                                         f"{r['cap_micros']} is not the opening balance's {want}")
        for idx, cl in closes(lp).items():
            for c in cl:                                     # the session after a payout: the tier follows the balance
                r = first.get((idx, c["day"] + 1))
                if c["requested"] > 0 and r is not None and r.get("cap_micros") is not None:
                    posts += 1
                    check(abs(float(r["balance_before"]) - (c["b"] - c["requested"])) <= 1e-6,
                          f"T-5: account {idx}: the session after a payout opens at another balance")
                    moved += int(rule.cap_micros("funded", c["b"]) != rule.cap_micros("funded",
                                                                                         float(r["balance_before"])))
            low = 0
            for c in cl:
                if c["requested"] > 0:
                    check(abs(c["requested"] - half * c["base"]) <= 1e-9 and c["requested"] >= pmin - EPS,
                          f"T-5: account {idx} day {c['day']}: the request {c['requested']} is not half of "
                          f"{c['base']}, or under the minimum")
                elif c["eligible"] and c["base"] >= pmin - EPS and not c["closed"]:
                    check(half * c["base"] < pmin - EPS, f"T-5: account {idx} did not ask at day {c['day']}")
                    low += 1
            check(int(rows[idx]["half_cut_below_min"]) == low,
                  f"T-5: account {idx}: the class counts {rows[idx]['half_cut_below_min']} cut requests, the record {low}")
            cut += low
    check(cut > 0, "T-5: no eligible balance had a half request under the minimum (nothing tested)")
    check(posts > 0 and moved > 0, f"T-5: the tier after a payout is not tested ({posts} sessions, {moved} moved)")
    # the placement: a Consistency-path account asks half of its own maximum
    lp, rows = counted(PP.PPElig, protocol(half), blocks_for(8, n=300, rr=1.0, p_win=0.65), path_seed=8, rtp=True)
    cc = 0
    for idx, cl in closes(lp, cap=float(RULES.cons_cap)).items():
        for c in cl:
            if c["consistency"] and c["requested"] > 0:
                cc += 1
                check(abs(c["requested"] - half * c["base"]) <= 1e-9,
                      f"T-5: Consistency account {idx} day {c['day']}: the request is not half of its maximum")
    check(cc > 0, "T-5: no Consistency-path request on the placement toy (nothing tested)")
    out["t5"] = {"cut_below_min": cut, "sessions_after_payout": posts, "tier_moved": moved,
                 "consistency_requests": cc}


# ------------------------------------------------------------------------------------------------ T-7


def section_t7() -> None:
    cushion = float(RULES.xfa_lock_at) - float(RULES.xfa_mll_start)
    split, fee, pmin = float(RULES.profit_split), float(RULES.payout_fee), float(RULES.payout_min)
    half = PP.half_fraction()
    res = {}
    for cell in PP.CELLS:
        cls, frac = PP.cell_class(cell), PP.cell_payout_frac(cell)
        gross, nacct = [], 0
        for ps in range(40):
            # the zero-edge twin: a 2R win with probability one third, so each trade's expectation is zero
            lp = run(cls, protocol(frac), blocks_for(100 + ps, n=150, p_win=1.0 / 3.0), path_seed=100 + ps,
                     replay=False)
            for f in lp.funded:
                gross.append(float(f.gross_paid))
            nacct += len(lp.funded)
            for idx, cl in closes(lp).items():
                f = next(x for x in lp.funded if int(x.index) == idx)
                reqs = [c["requested"] for c in cl if c["requested"] > 0]
                check(len(reqs) == len(f.payout_cash), f"T-7 {cell}: account {idx}: requests and payouts differ")
                for c in cl:
                    if c["requested"] > 0:
                        check(c["requested"] <= c["base"] + 1e-9 and c["requested"] >= pmin - 1e-9,
                              f"T-7 {cell}: a request outside its bounds")
                        if PP.CELL_LEVERS[cell][1] == "half":
                            check(abs(c["requested"] - half * c["base"]) <= 1e-9, f"T-7 {cell}: not half the maximum")
                        if PP.CELL_LEVERS[cell][0] == "lock" and c["paid_before"] == 0:
                            check(c["f"] >= float(RULES.xfa_lock_at) - EPS, f"T-7 {cell}: a first payout below lock")
                for r, cash in zip(reqs, f.payout_cash):
                    check(abs(cash - (split * r - fee)) <= 1e-9, f"T-7 {cell}: a payout not paid at the split less fee")
        g = np.asarray(gross, float)
        se = g.std(ddof=1) / math.sqrt(g.size) if g.size > 1 else float("inf")
        check(g.mean() <= cushion + 3.0 * se, f"T-7 {cell}: the zero-edge mean gross payout per funded account "
                                              f"{g.mean():.1f} exceeds {cushion:.0f} beyond three standard errors")
        res[cell] = {"accounts": int(g.size), "mean_gross": float(g.mean()), "se": float(se)}
    out["t7"] = res


# ------------------------------------------------------------------------------------------------ T-10


def _pool_note(text: str, what: str) -> bool:
    ran = "on 2 process(es)" in text
    if not ran:
        notes.append(f"NOT CHECKED (not a pass): {what} -- the memory guard allowed one worker")
    return ran


def replay_job(frac: float = 1.0, blocks: list | None = None) -> dict[str, Any]:
    from extended import user_beside as B

    blocks = blocks_for(12, n=120) if blocks is None else blocks
    days = [d.date().isoformat() for d in pd.bdate_range("2023-01-02", periods=len(blocks))]
    args = {"draws": {"protocol": protocol(frac), "mode": "rotation", "flip": None},
            "path": dict(edge=0.0, rules=RULES, initial_bankroll=1e9, max_concurrent_accounts=5,
                         subscription=float(RULES.subscription), billing_days=int(RULES.billing_days),
                         activation=float(RULES.activation), payout_lag_days=3, max_concurrent_combines=5,
                         max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                         combine_max_days=2000, funded_horizon_days=100_000, risk_policy=toy_table()),
            "seed": B.SEED_BLOCK[1]}
    return {"engine": "single", "blocks": blocks, "dates": days, "args": args}


def section_t10r() -> None:
    from extended import user_beside as B

    starts = [0, 7, 30, 61, 95]
    for cell in ("lock", "lock_half", "ref"):
        cls, frac = PP.cell_class(cell), PP.cell_payout_frac(cell)
        job = replay_job(frac)
        for rname in ("off", "denial_25", "rtp"):
            resp = B.BY_NAME[rname]
            plain = B.run_starts("toy", "verdict", resp, job, starts, 1, funded_account_cls=cls)
            got = PP.ReplayCounters()
            on = B.run_starts("toy", "verdict", resp, job, starts, 1, funded_account_cls=cls, counters=got)
            d = GI.deep_difference(plain, on, "outputs")
            check(d is None, f"T-10 replay {cell} {rname}: with the channel on the outputs differ: {d}")
            per = got.starts("toy", "verdict", rname)
            check(sorted(per) == starts, f"T-10 replay {cell} {rname}: counted starts {sorted(per)}")
            # the class's own: each start's long replay run directly, inside the collection
            a = B.response_args(job["args"], resp, cls)
            n = len(job["blocks"])
            for s in starts:
                L = min(252, n - s)
                with PP.collecting() as own:
                    B.replay(job["blocks"][s:s + L], a, B.start_seed(s))
                check(GI.deep_difference(own, per[s], "counts") is None,
                      f"T-10 replay {cell} {rname} start {s}: the channel's counts are not the class's own")
            tot = PP.lever_totals(r for v in per.values() for r in v)
            if cell == "ref":
                check(not any(tot.values()), f"T-10 replay ref {rname}: the levers' counts are not zero ({tot})")
            elif rname == "off":
                check(tot["first_requests_held"] > 0 and tot["held_sessions"] > 0,
                      f"T-10 replay {cell}: lock held nothing, or no held read (nothing tested)")
            for s, rows_s in per.items():
                rp = PP.read_problems(rows_s, min(252, n - s))
                check(not rp, f"T-10 replay {cell} {rname} start {s}: {rp[:1]}")
            out.setdefault("t10r", {})[f"{cell} {rname}"] = tot
    # X3: the placement toy -- under `rtp`, `ref`'s levers' counts zero while the engine's Consistency counts are
    # carried and nonzero
    pjob = replay_job(1.0, blocks_for(8, n=300, rr=1.0, p_win=0.65))
    pstarts = [0, 4, 9]
    pc = PP.ReplayCounters()
    B.run_starts("toy", "verdict", B.BY_NAME["rtp"], pjob, pstarts, 1, funded_account_cls=PP.REF_CLASS, counters=pc)
    prow = [r for v in pc.starts("toy", "verdict", "rtp").values() for r in v]
    check(not any(PP.lever_totals(prow).values()), f"T-10 replay ref rtp (placement): {PP.lever_totals(prow)}")
    ctot = PP.total_counters(prow)
    check(any(r["consistency"] for r in prow) and ctot["cons_first_payout_floor_below_lock"] > 0,
          f"T-10 replay ref rtp: no Consistency count carried through the channel ({ctot})")
    out.setdefault("t10r", {})["ref rtp placement"] = ctot
    # with Q-94's recorder too (RD-02 runs its headline replays recorded, 7.1): the outputs and the records are the
    # recorder-only run's, the counts the counters-only run's
    from extended import replay_records as RR

    cls, job = PP.cell_class("lock"), replay_job()
    r1, r2, c1 = RR.ReplayRecorder(), RR.ReplayRecorder(), PP.ReplayCounters()
    rec_only = B.run_starts("toy", "verdict", B.BY_NAME["off"], job, starts, 1, funded_account_cls=cls, recorder=r1)
    both = B.run_starts("toy", "verdict", B.BY_NAME["off"], job, starts, 1, funded_account_cls=cls, recorder=r2,
                        counters=c1)
    cnt_only = PP.ReplayCounters()
    B.run_starts("toy", "verdict", B.BY_NAME["off"], job, starts, 1, funded_account_cls=cls, counters=cnt_only)
    check(GI.deep_difference(rec_only, both, "outputs") is None, "T-10 replay: recorder and counters: outputs differ")
    check(r1.trades().equals(r2.trades()) and r1.accounts().equals(r2.accounts()) and not r2.problems(),
          f"T-10 replay: with the counters on the records differ ({r2.problems()[:3]})")
    check(GI.deep_difference(c1.starts("toy", "verdict", "off"), cnt_only.starts("toy", "verdict", "off")) is None,
          "T-10 replay: with the recorder on the counts differ")
    # refusals, before any start
    job = replay_job()
    for what, kw, exc in (("a collector of the wrong kind", {"counters": PP.GateCounters(),
                                                             "funded_account_cls": PP.PPLock}, TypeError),
                          ("no RD-02 class", {"counters": PP.ReplayCounters()}, TypeError),
                          ("the vendored class", {"counters": PP.ReplayCounters(),
                                                  "funded_account_cls": GI.XG.PassThroughFundedAccount}, TypeError)):
        try:
            B.run_starts("toy", "verdict", B.BY_NAME["off"], job, [0], 1, **kw)
            problems.append(f"T-10 replay: {what} was not refused")
        except exc:
            pass


def _gate_fixture():
    """T-10's gate toy (Q-106's M1): Q-47's synthetic blocks and keywords, with this harness's win-day-keyed table, so
    held reads happen on gate paths."""
    kw = dict(GI.syn_kwargs(), n_paths=6, risk_policy=toy_table())
    return GI.syn_blocks(), kw


def _gate(blocks, kw, cls: type, frac: float, workers: int, counters: Any = None, recorder: Any = None):
    seen: dict[tuple[str, float], list] = {}

    def hook(shift, p, paths):
        seen[(shift, float(p))] = [(x.path, x.funded, x.combines, x.conduct) for x in paths]
        return {}

    k = dict(kw, protocol=dataclasses.replace(kw["protocol"], payout_frac=frac))
    k.pop("levels", None)
    rows, passed = GI.XG.run_gate(blocks, funded_account_cls=cls, workers=workers, path_hook=hook, counters=counters,
                                  recorder=recorder, levels=(0.0, 0.25), **k)
    return rows, passed, seen


def section_t10g() -> None:
    """One worker (the two-worker leg is `t10w2`, slow): with the table on the gate's paths, the channel changes no row
    or path record, and each path's counts -- the held reads by class, their sessions, the held closes, every count --
    equal the path's own counts collected where it ran (`tests/pp_gate_direct.CollectingRecorder`, the channel off)."""
    import pp_gate_direct as GD

    from propedge.campaign.lockstep import path_seeds

    blocks, kw = _gate_fixture()
    for cell in ("lock", "half", "ref"):
        cls, frac = PP.cell_class(cell), PP.cell_payout_frac(cell)
        r0, p0, s0 = _gate(blocks, kw, cls, frac, 1)
        got = PP.GateCounters()
        r1, p1, s1 = _gate(blocks, kw, cls, frac, 1, counters=got)
        check(r0.equals(r1) and p0 == p1, f"T-10 gate {cell}: with the channel on the rows differ")
        check(GI.deep_difference(s0, s1, "paths") is None, f"T-10 gate {cell}: with the channel on the paths differ")
        direct = GD.CollectingRecorder()
        _gate(blocks, kw, cls, frac, 1, recorder=direct)
        seeds = [int(s) for s in path_seeds(kw["seed"], kw["n_paths"])]
        allrows = []
        for (shift, p), paths in s1.items():
            per = got.paths(shift, p)
            check(sorted(per) == sorted(seeds), f"T-10 gate {cell} {shift} {p}: counted paths")
            own = direct.got.get((shift, float(p)), {})
            for seed, (_, funded, _, _) in zip(seeds, paths):
                mine = {(int(r["index"]), int(r["activation_day"])) for r in per[seed]}
                theirs = {(int(f.index), int(f.activation_day)) for f in funded}
                check(mine == theirs, f"T-10 gate {cell} {shift} {p}: path {seed}'s counted accounts are not its own")
                d = GI.deep_difference(per[seed], own.get(seed), "counts")
                check(d is None, f"T-10 gate {cell} {shift} {p} path {seed}: the channel's counts are not the path's "
                                 f"own: {d}")
                rp = PP.read_problems(per[seed], int(kw["horizon_days"]) - 1)
                check(not rp, f"T-10 gate {cell} {shift} {p} path {seed}: {rp[:1]}")
                allrows += per[seed]
        tot = PP.lever_totals(allrows)
        if cell == "ref":
            check(not any(tot.values()), f"T-10 gate ref: the levers' counts are not zero ({tot})")
        else:
            held = sum(tot[f"held_{k}"] for k in PP.HELD_CLASSES)
            check(held > 0 and tot["held_sessions"] > 0, f"T-10 gate {cell}: no held read on a gate path ({tot})")
            if cell == "lock":
                check(tot["first_requests_held"] > 0, "T-10 gate lock: lock held nothing")
        out.setdefault("t10g", {})[cell] = tot
    for what, call, exc in (
            ("a collector of the wrong kind",
             lambda: _gate(blocks, kw, PP.PPLock, 1.0, 1, counters=PP.ReplayCounters()), TypeError),
            ("no RD-02 class", lambda: GI.XG.run_gate(blocks, counters=PP.GateCounters(), **kw), TypeError),
            ("counters with a recorder", lambda: _gate(blocks, kw, PP.PPLock, 1.0, 1, counters=PP.GateCounters(),
                                                       recorder=GD.CollectingRecorder()), ValueError)):
        try:
            call()
            problems.append(f"T-10 gate: {what} was not refused")
        except exc:
            pass
    check(not GI.XG.gate_recomposition_problems() and "Q-105" in GI.XG.GATE_MARKERS,
          f"T-10 gate: the re-composition proof: {GI.XG.gate_recomposition_problems()}")


def section_t10w2() -> None:
    """T-10's two-worker legs (slow: the lead runs it under the lock, with memory, before the reading's run): the U1
    replay and the table-bearing gate at two workers give the one-worker run's outputs, rows, paths and counts. A run
    the memory guard holds to one worker is a problem here, never a pass."""
    from extended import user_beside as B

    starts = [0, 7, 30, 61, 95]
    for cell in ("lock", "lock_half", "ref"):
        cls, frac = PP.cell_class(cell), PP.cell_payout_frac(cell)
        job = replay_job(frac)
        c1, c2 = PP.ReplayCounters(), PP.ReplayCounters()
        one = B.run_starts("toy", "verdict", B.BY_NAME["off"], job, starts, 1, chunk=2, funded_account_cls=cls,
                           counters=c1)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            two = B.run_starts("toy", "verdict", B.BY_NAME["off"], job, starts, 2, chunk=2, funded_account_cls=cls,
                               counters=c2)
        sys.stdout.write(buf.getvalue())
        if "on 2 process(es)" not in buf.getvalue():
            problems.append(f"NOT CHECKED: T-10 replay {cell} at two workers -- the memory guard allowed one worker")
        else:
            check(GI.deep_difference(one, two, "outputs") is None, f"T-10 replay {cell}: two workers' outputs differ")
            check(GI.deep_difference(c1.starts("toy", "verdict", "off"), c2.starts("toy", "verdict", "off"),
                                     "counts") is None, f"T-10 replay {cell}: two workers' counts differ")
    blocks, kw = _gate_fixture()
    for cell in ("lock", "half", "ref"):
        cls, frac = PP.cell_class(cell), PP.cell_payout_frac(cell)
        g1, g2 = PP.GateCounters(), PP.GateCounters()
        r1, p1, s1 = _gate(blocks, kw, cls, frac, 1, counters=g1)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            r2, p2, s2 = _gate(blocks, kw, cls, frac, 2, counters=g2)
        sys.stderr.write(buf.getvalue())
        if GI.GUARD_FELL_BACK in buf.getvalue():
            problems.append(f"NOT CHECKED: T-10 gate {cell} at two workers -- the memory guard allowed one worker")
            continue
        check(r1.equals(r2) and p1 == p2 and GI.deep_difference(s1, s2, "paths") is None,
              f"T-10 gate {cell}: two workers' rows or paths differ")
        check(g1.keys() == g2.keys() and all(GI.deep_difference(g1.paths(*k[:2])[k[2]], g2.paths(*k[:2])[k[2]]) is None
                                             for k in g1.keys()), f"T-10 gate {cell}: two workers' counts differ")


# ------------------------------------------------------------------------------------------------ absent


def _old_adapter() -> types.ModuleType:
    src = subprocess.run(["git", "show", f"{BASE_COMMIT}:extended/user_beside.py"], cwd=REPO, capture_output=True,
                         text=True, check=True).stdout.replace("\r\n", "\n")
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    out["absent_base_sha256"] = sha
    check(sha == BASE_SHA256, f"absent: git show {BASE_COMMIT}:extended/user_beside.py is not the pinned text")
    m = types.ModuleType("user_beside_before_q105")
    m.__file__ = str(REPO / "extended" / "user_beside.py")
    sys.modules[m.__name__] = m
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def section_absent() -> None:
    """The adapter with the channel absent equals master's before Q-105, bit for bit, on all 19 responses, with and
    without the pass-through class (on this harness's replay toy)."""
    from extended import user_beside as B

    old = _old_adapter()
    job = replay_job()
    starts = [0, 9, 44]
    for resp in B.RESPONSES:
        for cls in (None, GI.XG.PassThroughFundedAccount):
            if cls is not None and B.class_problems(cls, resp):
                continue
            kw = {} if cls is None else {"funded_account_cls": cls}
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                a = old.run_starts("toy", "verdict", old.BY_NAME[resp.name], job, starts, 1, **kw)
                b = B.run_starts("toy", "verdict", resp, job, starts, 1, **kw)
            d = GI.deep_difference(a, b, "outputs")
            check(d is None, f"absent: {resp.name} ({'class' if cls else 'no class'}): differs from {BASE_COMMIT}: {d}")
    check(not GI.XG.gate_recomposition_problems(), "absent: the gate's re-composition proof fails")


SECTIONS = {"t1": section_t1, "t2": section_t2, "t3": section_t3, "t4": section_t4, "t5": section_t5,
            "t7": section_t7, "t10r": section_t10r, "t10g": section_t10g, "t10w2": section_t10w2,
            "absent": section_absent}
out: dict[str, Any] = {}

if __name__ == "__main__":
    t0 = time.time()
    SECTIONS[SECTION]()
    out.update({"section": SECTION, "problems": problems[:40], "n_problems": len(problems), "notes": notes,
                "seconds": round(time.time() - t0, 2)})
    print(json.dumps(out, default=str))
