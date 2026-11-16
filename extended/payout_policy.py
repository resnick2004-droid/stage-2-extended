"""RD-02's adapter (`prereg/RD-02_payout_policy.md`, pinned under E-082; its build Q-105): the payout policy of a funded
account -- when the first payout is asked (L1) and how much each request takes (L2) -- and the held-state rule, as a
declared funded-account class and the design's own `protocol`, never a substituted vendored attribute.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import payout_policy as PP
    cls, protocol = PP.cell_class("lock_half"), PP.cell_protocol(base_protocol, "lock_half")
    outs = B.run_starts(design, arm, B.BY_NAME["off"], job_with(protocol), starts, workers, funded_account_cls=cls)

**The levers (6.1).** L1 is the class: `elig` (P-14's) asks at the first close at which the account is eligible by the
firm's Standard rule; `lock` asks the first payout only at an eligible close at which the account's loss limit (MLL) has
locked at the ledger's `xfa_lock_at` -- the engine's own floor `F`, which reaches it once a close's balance has reached
`xfa_lock_at - xfa_mll_start` (8284204) -- and until then asks nothing. L1 acts on the first request only. L2 is the
protocol's own `payout_frac`: `max` the Protocol's 1.0, `half` the value of the vendored `fast_half` arm
(`protocols.py`, the fast-payout family), which is D-564's half request too (`rc150_payout_screen.FRACS`).

**The held-state rule (6.3), a declared design choice.** An account is *held* at a close when (a) it is on the Standard
path, eligible by the firm's rule, and the base's request -- min(`payout_max_frac_of_balance` x balance, the cap) --
would reach `payout_min`, and (b) the cell's policy makes no request there (L1's hold, or L2's request below the
minimum). At the next session's start the table's decision for a held account is read **with its winning days counted
as the ledger's `std_winning_days` less one** -- the table's own leaf for an account one winning day short, at the same
balance, cushion, line gap and request-day flag. Nothing else changes: the firm's count and eligibility, and every
leaf, are the engine's.

*How the read is made.* The engine reads an account's winning days in exactly one place for the table:
`risk_policy.account_state`, which takes `getattr(account, "win_days")`. This class keeps the firm's count in
`win_days`' own storage and answers that one caller -- recognised by its code object -- with the held count while the
account is held; every other reader (the firm's eligibility, the count's own increments and resets, the router's
progress, the second-trade and collect gates) reads the firm's count. The decision the engine then takes is the table's
own `decide` on the state `account_state` builds: nothing of the engine is substituted. The read refuses
(`RuntimeError`) if it cannot find the engine's risk policy in the caller's frame, where it classifies the read.

*The minimal rescue (6.3's alternative, run beside on P-14 only):* the held count only where the table's five-day leaf
is no-trade (`max_trades` 0); elsewhere the firm's count, so the table's own five-day leaf.

**The firm's eligibility recorded (F7).** `lock` overrides `_standard_eligible` and returns the policy's eligibility to
the engine; after `trade_day` the class puts the firm's back in `last_eligible`, which only the daily recorder reads.

**The counters (13.1 item 1; T-10).** Each account counts, at its closes and reads: the held reads by 6.3's class
(`unchanged`, `rescued`, `r_changed`) and the sessions they fall on; the first requests L1 holds; the requests L2 cuts
below the minimum; the closes at which the policy's eligibility differs from the firm's; and, on Consistency-path
accounts (the placement's), the first payouts taken with the floor below `xfa_lock_at` and the sessions that start
eligible and unpaid. The engine's records do not carry a subclass's fields (`lockstep._record_funded`), so the counters
come out through a declared channel, off by default: `collecting()` around one path in the process that runs it --
`extended.user_beside.run_starts(..., counters=ReplayCounters())` for the U1 replay, and
`extended.gate.run_gate(..., counters=GateCounters())` for the gate (its draws wrapped by `CountingDraws`, which
carries a worker's counts home through the draws' own export and import). With the channel off nothing is registered
and nothing is collected.

**The rules in code (13.2).** Every value is the ledger's, read by the engine's loader (`rules_from_ledger`) or handed
to `trade_day` by the engine (`rules`, `cap`): the lock balance `xfa_lock_at - xfa_mll_start`, the minimum
`payout_min`, the maximum from `payout_max_frac_of_balance` and the cap. No rule value is written here.

Importing this module puts the vendored tree on `sys.path` (it subclasses the engine's `FundedAccount`).
"""
from __future__ import annotations

import dataclasses
import sys
from collections import Counter
from typing import Any, Iterable, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

from propedge.campaign import risk_policy as _rp  # noqa: E402
from propedge.campaign.lockstep import EPS, FundedAccount  # noqa: E402

#: RD-02 6.1-6.2: the levers' values and the grid
L1_VALUES = ("elig", "lock")
L2_VALUES = ("max", "half")
CELLS = ("ref", "lock", "half", "lock_half")
CELL_LEVERS = {"ref": ("elig", "max"), "lock": ("lock", "max"), "half": ("elig", "half"), "lock_half": ("lock", "half")}
#: RD-02 6.3: the declared rule, and the minimal rescue (run beside on P-14's three new cells, never on the menu)
HELD_MODES = ("declared", "minimal")
#: RD-02 6.3: the held reads' classes
HELD_CLASSES = ("unchanged", "rescued", "r_changed")
#: the counters each account carries (13.1 item 1), in this order
COUNTER_KEYS = ("held_unchanged", "held_rescued", "held_r_changed", "first_requests_held", "half_cut_below_min",
                "elig_differs", "cons_first_payout_floor_below_lock", "cons_eligible_unpaid_sessions")

_ACCOUNT_STATE_CODE = _rp.account_state.__code__


# ------------------------------------------------------------------------------------------------ the ledger's values


def ledger_rules() -> Any:
    """The engine's `Rules` from Stage 2's verified ledger (`propedge.contract.adapter.rules_from_ledger`), once a
    process."""
    r = _CACHE.get("rules")
    if r is None:
        from propedge.contract.adapter import rules_from_ledger

        r = _CACHE["rules"] = rules_from_ledger()
    return r


_CACHE: dict[str, Any] = {}


def lock_balance(rules: Any | None = None) -> float:
    """13.2: the balance at which the MLL locks, `xfa_lock_at - xfa_mll_start` (8284204)."""
    r = ledger_rules() if rules is None else rules
    return float(r.xfa_lock_at) - float(r.xfa_mll_start)


def base_request(balance: float, rules: Any, cap: float) -> float:
    """13.2: the base's (P-14's) request at a balance: min(`payout_max_frac_of_balance` x balance, the cap)."""
    return min(float(rules.payout_max_frac_of_balance) * float(balance), float(cap))


def held_win_days(rules: Any | None = None) -> int:
    """6.3: the winning days a held account is read at -- the ledger's `std_winning_days` less one."""
    r = ledger_rules() if rules is None else rules
    return int(r.std_winning_days) - 1


def half_fraction() -> float:
    """L2's `half`: the `payout_frac` of the vendored `fast_half` arm (`propedge.campaign.protocols`, the fast-payout
    family registered beside the buffer, D-02) -- D-564's half request (`rc150_payout_screen.FRACS`)."""
    from propedge.campaign.protocols import REGISTRY

    arm = REGISTRY.get("fast_half")
    if arm.family != "fast_payout" or float(arm.keep_balance) != 0.0 or not 0.0 < float(arm.payout_frac) < 1.0:
        raise RuntimeError(f"REFUSED (RD-02 6.1): the vendored fast_half arm is not a half request: {arm!r}")
    return float(arm.payout_frac)


# ------------------------------------------------------------------------------------------------ the collection


_OPEN: list | None = None


def open_collection() -> None:
    """Start registering this process's policy accounts (one path's): the channel's own call, never the engine's."""
    global _OPEN
    _OPEN = []


def close_collection() -> list[dict[str, Any]]:
    """Stop registering and return the accounts registered since `open_collection`, each as `account_counters`; an
    empty list when none was open."""
    global _OPEN
    accts, _OPEN = (_OPEN or []), None
    return [account_counters(a) for a in accts]


class collecting:
    """`with collecting() as got:` -- the accounts created in the block are counted; `got` is filled at the exit."""

    def __enter__(self) -> list[dict[str, Any]]:
        self.got: list[dict[str, Any]] = []
        open_collection()
        return self.got

    def __exit__(self, *exc: Any) -> None:
        self.got.extend(close_collection())


def account_counters(a: "PayoutPolicyFundedAccount") -> dict[str, Any]:
    """One account's counters, with what identifies it on its path."""
    c = a.__dict__.get("_pp_counts") or Counter()
    return {"index": int(a.index), "activation_day": int(a.activation_day),
            "consistency": bool(a.policy_override is not None),
            **{k: int(c.get(k, 0)) for k in COUNTER_KEYS},
            "held_days": tuple(sorted(a.__dict__.get("_pp_held_days") or ()))}


def total_counters(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    """The counters summed over accounts (the held days counted)."""
    out = {k: 0 for k in COUNTER_KEYS}
    out["held_sessions"] = 0
    for r in rows:
        for k in COUNTER_KEYS:
            out[k] += int(r[k])
        out["held_sessions"] += len(r["held_days"])
    return out


# ------------------------------------------------------------------------------------------------ the account


def _decision_key(d: Any) -> tuple:
    return (float(d.risk), None if d.rr is None else float(d.rr), d.max_trades, bool(d.abandon), str(d.source))


def held_class(five: Any, four: Any) -> str:
    """6.3's class of a held read: `rescued` where the five-day leaf is no-trade (`max_trades` 0), else `unchanged`
    where the four-day leaf is the five-day leaf, else `r_changed`."""
    if five.max_trades is not None and int(five.max_trades) == 0:
        return "rescued"
    return "unchanged" if _decision_key(five) == _decision_key(four) else "r_changed"


class PayoutPolicyFundedAccount(FundedAccount):
    """The vendored `FundedAccount` with RD-02's L1 (`LOCK`), the held-state rule (`HELD_MODE`) and the counters. Not
    run itself: the cells' classes below set the two class attributes."""

    LOCK: bool = False
    HELD_MODE: str = "declared"

    def __post_init__(self) -> None:
        super().__post_init__()
        d = self.__dict__
        d.setdefault("_pp_held", False)
        d["_pp_counts"] = Counter()
        d["_pp_held_days"] = set()
        d["_pp_firm_elig"] = None
        d["_pp_reading"] = False
        if _OPEN is not None:
            _OPEN.append(self)

    # ---- the firm's winning days, and the one read that sees the held count
    @property
    def win_days(self) -> int:                                       # type: ignore[override]
        d = self.__dict__
        wd = d.get("_pp_win_days", 0)
        if not d.get("_pp_held", False) or d.get("_pp_reading", False):
            return wd
        f = sys._getframe(1)
        if f.f_code is not _ACCOUNT_STATE_CODE:
            return wd
        return self._held_read(f, wd)

    @win_days.setter
    def win_days(self, value: int) -> None:
        self.__dict__["_pp_win_days"] = value

    def _held_read(self, frame: Any, wd: int) -> int:
        """The table's read of a held account (6.3): classify it against the five-day leaf, count it once a session,
        and answer the held count (in the minimal rescue only where the five-day leaf is no-trade)."""
        loc = frame.f_locals
        if loc.get("kind") != "funded":
            return wd
        caller = frame.f_back
        rp = caller.f_locals.get("risk_policy") if caller is not None else None
        if rp is None:
            raise RuntimeError("REFUSED (RD-02 13.1 item 2): the held-state read found no risk policy in the engine's "
                               "frame; the rule reads the table the engine reads, or nothing")
        d = self.__dict__
        d["_pp_reading"] = True
        try:
            five = _rp.account_state(self, kind="funded", day=loc["day"], mll=loc["mll"], cents=loc["cents"])
        finally:
            d["_pp_reading"] = False
        held = held_win_days()
        d5, d4 = rp.decide(five), rp.decide(dict(five, win_days=held))
        cls = held_class(d5, d4)
        day = int(loc["day"])
        if day not in d["_pp_held_days"]:                       # the close's look-ahead read and the session's read
            d["_pp_held_days"].add(day)                         # are one session's: counted once
            d["_pp_counts"][f"held_{cls}"] += 1
        if self.HELD_MODE == "minimal" and cls != "rescued":
            return wd
        return held

    # ---- L1, and the firm's eligibility kept
    def _standard_eligible(self, rules: Any) -> bool:
        firm = bool(super()._standard_eligible(rules))
        self.__dict__["_pp_firm_elig"] = firm
        policy = firm
        if self.LOCK and firm and not self.paid_once and float(self.F) < float(rules.xfa_lock_at) - EPS:
            policy = False
        if policy != firm:
            self.__dict__["_pp_counts"]["elig_differs"] += 1
        return policy

    def trade_day(self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int, *args: Any,
                  **kwargs: Any) -> float | None:
        d = self.__dict__
        d["_pp_firm_elig"] = None
        floor_before = float(self.F)
        paid_before = int(self.n_payouts)
        net = super().trade_day(rules, policy, cap, rel_day, calendar_day, *args, **kwargs)
        requested = int(self.n_payouts) > paid_before
        firm = d["_pp_firm_elig"]
        if firm is not None:                                    # F7: the recorder's `eligible` is the firm's
            self.last_eligible = bool(firm)
        standard = str(policy.payout_path) == "standard"
        balance = float(self.B) + (float(self.last_request) if requested else 0.0)   # the close's, before a request
        allowed = base_request(balance, rules, cap)
        reaches = allowed >= float(rules.payout_min) - EPS
        cell_req = float(policy.payout_frac) * allowed
        if float(policy.keep_balance) > 0:
            cell_req = min(cell_req, max(balance - float(policy.keep_balance), 0.0))
        c = d["_pp_counts"]
        held = False
        if standard and firm and not requested and not self.closed and reaches:
            held = True
            blocked = self.LOCK and paid_before == 0 and float(self.F) < float(rules.xfa_lock_at) - EPS
            if blocked and cell_req >= float(rules.payout_min) - EPS:
                c["first_requests_held"] += 1
            if not blocked and cell_req < float(rules.payout_min) - EPS:
                c["half_cut_below_min"] += 1
        if not standard:
            if requested and paid_before == 0:
                f_close = min(float(rules.xfa_lock_at), max(floor_before, balance - float(rules.mll)))
                if f_close < float(rules.xfa_lock_at) - EPS:
                    c["cons_first_payout_floor_below_lock"] += 1
            if bool(self.last_eligible) and not requested and not self.closed:
                c["cons_eligible_unpaid_sessions"] += 1
        d["_pp_held"] = held
        return net


class PPElig(PayoutPolicyFundedAccount):
    """L1 `elig` (P-14's), the declared held-state rule: the `ref` and `half` cells."""


class PPLock(PayoutPolicyFundedAccount):
    """L1 `lock`, the declared held-state rule: the `lock` and `lock_half` cells."""

    LOCK = True


class PPEligMinimal(PayoutPolicyFundedAccount):
    """L1 `elig` under the minimal rescue: `half`'s rule-sensitivity run (P-14 only)."""

    HELD_MODE = "minimal"


class PPLockMinimal(PayoutPolicyFundedAccount):
    """L1 `lock` under the minimal rescue: `lock`'s and `lock_half`'s rule-sensitivity runs (P-14 only)."""

    LOCK = True
    HELD_MODE = "minimal"


#: the reference policy's class (8.1; `identity/pp_identity.py` runs it alone)
REF_CLASS = PPElig


def cell_class(cell: str, held_mode: str = "declared") -> type:
    """The funded-account class of a cell (6.2) under a held-state mode (6.3)."""
    if cell not in CELLS:
        raise ValueError(f"cell is one of {CELLS}, got {cell!r}")
    if held_mode not in HELD_MODES:
        raise ValueError(f"held_mode is one of {HELD_MODES}, got {held_mode!r}")
    if held_mode == "minimal" and cell == "ref":
        raise ValueError("the minimal rescue is run beside the three new cells only (6.3), never on ref")
    lock = CELL_LEVERS[cell][0] == "lock"
    if held_mode == "declared":
        return PPLock if lock else PPElig
    return PPLockMinimal if lock else PPEligMinimal


def cell_payout_frac(cell: str) -> float:
    """L2's `payout_frac` for a cell: the Protocol's own field -- `max` 1.0 (the base's), `half` `half_fraction()`."""
    if cell not in CELLS:
        raise ValueError(f"cell is one of {CELLS}, got {cell!r}")
    return half_fraction() if CELL_LEVERS[cell][1] == "half" else 1.0


def cell_protocol(base: Any, cell: str) -> Any:
    """A cell's protocol: the base's, with only `payout_frac` replaced (`dataclasses.replace`, as D-565 did). Refused
    unless the base asks the maximum with no balance kept (P-14's and P-16's do: `payout_frac` 1.0, `keep_balance` 0)."""
    if float(getattr(base, "payout_frac", float("nan"))) != 1.0 or float(getattr(base, "keep_balance", 1.0)) != 0.0:
        raise ValueError("RD-02's cells start from a base that asks the maximum with no balance kept (payout_frac 1.0, "
                         f"keep_balance 0); got payout_frac {getattr(base, 'payout_frac', None)!r}, keep_balance "
                         f"{getattr(base, 'keep_balance', None)!r}")
    frac = cell_payout_frac(cell)
    return base if frac == 1.0 else dataclasses.replace(base, payout_frac=frac)


def levers_off(cls: type, protocol: Any) -> bool:
    """Both levers off: L1 `elig` (no lock) and L2 `max` (`payout_frac` 1.0, no balance kept)."""
    return (isinstance(cls, type) and issubclass(cls, PayoutPolicyFundedAccount) and not cls.LOCK
            and float(protocol.payout_frac) == 1.0 and float(protocol.keep_balance) == 0.0)


# ------------------------------------------------------------------------------------------------ the channel


class ReplayCounters:
    """The U1 replay's counters (`extended.user_beside.run_starts(..., counters=...)`): one list of account counters a
    start's long replay, keyed (design, arm, response, start)."""

    def __init__(self) -> None:
        self._got: dict[tuple[str, str, str, int], list[dict[str, Any]]] = {}

    def collect(self, design: str, arm: str, response: str, per_start: Sequence[tuple[int, list]]) -> None:
        for s, rows in per_start:
            key = (str(design), str(arm), str(response), int(s))
            if key in self._got:
                raise RuntimeError(f"REFUSED (Q-105): {key} was already counted")
            self._got[key] = list(rows)

    def starts(self, design: str, arm: str, response: str) -> dict[int, list[dict[str, Any]]]:
        return {k[3]: v for k, v in self._got.items() if k[:3] == (design, arm, response)}

    def keys(self) -> list[tuple[str, str, str, int]]:
        return sorted(self._got)


class CountingDraws:
    """The gate's draw factory with the counters' channel: each path's call opens a collection in the process that runs
    the path, the next path's call (or the end) closes it under the path's seed; a worker's counts travel home with the
    draws' own `export_state` and are taken in by `import_state`, which hands the wrapped factory's own state on
    unchanged. Every other attribute is the wrapped factory's (the gate reads its `tallies`)."""

    def __init__(self, inner: Any) -> None:
        self.__dict__["_inner"] = inner
        self.__dict__["_bag"] = {}
        self.__dict__["_cur"] = None

    def __call__(self, path_seed: int) -> Any:
        self._close()
        open_collection()
        self.__dict__["_cur"] = int(path_seed)
        return self._inner(path_seed)

    def _close(self) -> None:
        cur = self.__dict__.get("_cur")
        if cur is not None:
            self._bag[cur] = close_collection()
            self.__dict__["_cur"] = None

    def export_state(self) -> dict[str, Any]:
        self._close()
        exp = getattr(self._inner, "export_state", None)
        out = {"inner": exp() if callable(exp) else None, "counters": dict(self._bag)}
        self._bag.clear()
        return out

    def import_state(self, state: dict[str, Any]) -> None:
        imp = getattr(self._inner, "import_state", None)
        if state.get("inner") is not None and callable(imp):
            imp(state["inner"])
        self._bag.update(state.get("counters") or {})

    def finish(self) -> dict[int, list[dict[str, Any]]]:
        """The counts by path seed (the last path closed here)."""
        self._close()
        return dict(self._bag)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__") or name in ("_inner", "_bag", "_cur"):
            raise AttributeError(name)
        return getattr(self.__dict__["_inner"], name)

    def __getstate__(self) -> dict[str, Any]:
        return dict(self.__dict__)

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__dict__.update(state)


class GateCounters:
    """The gate's counters (`extended.gate.run_gate(..., counters=...)`): one list of account counters a path, keyed
    (shift, enforcement level, path seed)."""

    def __init__(self) -> None:
        self._got: dict[tuple[str, float, int], list[dict[str, Any]]] = {}

    def wrap(self, draws: Any) -> CountingDraws:
        return CountingDraws(draws)

    def collect(self, shift: str, enforcement_p: float, draws: CountingDraws) -> None:
        for seed, rows in draws.finish().items():
            key = (str(shift), float(enforcement_p), int(seed))
            if key in self._got:
                raise RuntimeError(f"REFUSED (Q-105): {key} was already counted")
            self._got[key] = list(rows)

    def paths(self, shift: str, enforcement_p: float) -> dict[int, list[dict[str, Any]]]:
        return {k[2]: v for k, v in self._got.items() if k[:2] == (shift, float(enforcement_p))}

    def keys(self) -> list[tuple[str, float, int]]:
        return sorted(self._got)


def check_counters(counters: Any, kind: type) -> None:
    """None, or the channel's collector of `kind` (`TypeError` otherwise)."""
    if counters is not None and not isinstance(counters, kind):
        raise TypeError(f"counters must be an extended.payout_policy.{kind.__name__}, got {type(counters).__name__}")


def check_counted_class(funded_account_cls: Any) -> None:
    """The channel counts this module's accounts only: refused (`TypeError`) for any other funded class, or none."""
    if not (isinstance(funded_account_cls, type) and issubclass(funded_account_cls, PayoutPolicyFundedAccount)):
        raise TypeError("the counters' channel counts RD-02's accounts: funded_account_cls must be a subclass of "
                        f"extended.payout_policy.PayoutPolicyFundedAccount, got {funded_account_cls!r}")


__all__ = ["L1_VALUES", "L2_VALUES", "CELLS", "CELL_LEVERS", "HELD_MODES", "HELD_CLASSES", "COUNTER_KEYS",
           "ledger_rules", "lock_balance", "base_request", "held_win_days", "half_fraction", "open_collection",
           "close_collection", "collecting", "account_counters", "total_counters", "held_class",
           "PayoutPolicyFundedAccount", "PPElig", "PPLock", "PPEligMinimal", "PPLockMinimal", "REF_CLASS",
           "cell_class", "cell_payout_frac", "cell_protocol", "levers_off", "ReplayCounters", "CountingDraws",
           "GateCounters", "check_counters", "check_counted_class"]
