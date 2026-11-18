"""RD-03's rules in code (`prereg/RD-03_contract_levers.md` 4.2, 4.3, 14.2; its build Q-119, E-153): every value the
contract levers lean on, read by a loader that refuses an entry not `verified`, and the readings of section 4.3 from
one table of named constants (`extended/levers_readings.py`).

    from extended import levers_terms as LT
    fee = LT.reactivation_fee()                    # back2funded_reactivation_fee_50k, from the record
    sub, act = LT.naf_prices()                     # A-4: subscription_fee_naf_50k, activation_fee_naf_50k

**The loader (14.2).** `record_value(key)` reads this repository's record (`config/rules_extended.yaml`) and refuses
(`UnverifiedTerm`) any entry whose status is not `verified`; a value that is not a number where a number is read is
refused fail-loud (`TermParseError`) -- the record changed shape, so the build stops, never guesses. `stage2_value(key)`
reads Stage 2's vendored ledger through its own loader (`propedge.contract.rules.load_rules`, which refuses an entry not
verified) -- in a process that has the vendored tree on its path.

**The record's Q-115 keys before their merge (4.1; 16 item 2).** The keys this reading adds (Back2Funded's, the No
Activation Fee 50K prices, the hold's expiry, the evaluation's cancellation, the Reset Bank's) are Q-115's, committed on
`wt/wt-firms` at deb45ad and not yet on master (E-135). Until they are merged the loader reads a key the working record
lacks from deb45ad's blob (as T-0 does) and says so: `record_source(key)` is `"record"` or `"deb45ad (not merged)"`, and
`unmerged_keys()` lists every key read the second way. The reading's runner refuses to run while that list is not
empty (`extended/cl_reading.py`, its waits: "Q-115 merged").

**Never loaded (14.2; the red team's m7 (b)).** Stage 2's `hold_expiry_days` is `verified` with the design sentinel
`not_required_under_d34`, which is not a reading of any page; the record's `hold_expiry_days` is `unstated`. Both are in
`NEVER_LOADED`, and the loader refuses them by name whatever their status (`NeverLoaded`). So are `xfa_seat_frees_at`
(unverified; the engine's own next-session convention, U-3), the record's other `unstated` keys and the moot keys.

Pure Python at import (YAML and git only); the engine is imported only by `stage2_value`.
"""
from __future__ import annotations

import math
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "config" / "rules_extended.yaml"
DECLARATION = "prereg/RD-03_contract_levers.md"
#: Q-115's commit on wt/wt-firms (E-135): where the record's new keys live until they merge
Q115_COMMIT = "deb45ad"
#: the source label of a key read from Q-115's commit
UNMERGED = f"{Q115_COMMIT} (not merged)"

#: the keys this reading loads from the record (4.2), each verified
RECORD_KEYS = ("back2funded_reactivation_fee_50k", "back2funded_max_reactivations", "back2funded_window_days",
               "subscription_fee_naf_50k", "activation_fee_naf_50k", "reset_fee_naf_50k")
#: the keys it loads from Stage 2's ledger (4.2), each verified
STAGE2_KEYS = ("subscription_fee", "activation_fee", "reset_fee", "billing_days", "billing_period_calendar_days",
               "max_active_funded_accounts", "xfa_mll_start", "xfa_lock_at", "payout_min", "xfa_std_cap",
               "payout_max_frac_of_balance", "profit_split")
#: 14.2: never loaded, whatever the status -- the sentinel, the unstated and unverified keys, the moot ones (by source)
NEVER_LOADED = {
    "stage2": ("hold_expiry_days", "xfa_seat_frees_at", "xfa_closure_at_request"),
    "record": ("hold_expiry_days", "back2funded_fee_by_pricing_path", "combine_cancellation_account_effect",
               "back2funded_dll_discount", "reset_credit_per_rebill", "reset_credit_expiry"),
}


class UnverifiedTerm(ValueError):
    """A rule the levers would load is not `verified` in its record: it may not be used (CHARTER section 4)."""


class TermParseError(ValueError):
    """A verified value is not of the shape the levers read (a number): the record changed -- re-derive, never guess."""


class NeverLoaded(ValueError):
    """A key 14.2 names as never loaded (Stage 2's `hold_expiry_days` sentinel among them) was asked for."""


# ------------------------------------------------------------------------------------------------ the record


def _git_show(rev: str, rel: str, root: Path = ROOT) -> str | None:
    r = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{rel}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="surrogateescape")


@lru_cache(maxsize=4)
def _record(root: str = str(ROOT)) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """The record's entries (the working `config/rules_extended.yaml`, and Q-115's commit for any key it lacks) and
    each entry's source."""
    rootp = Path(root)
    doc = yaml.safe_load((rootp / "config" / "rules_extended.yaml").read_text(encoding="utf-8"))
    out = {str(e["key"]): e for e in doc["rules"]}
    src = {k: "record" for k in out}
    if any(k not in out for k in RECORD_KEYS):
        text = _git_show(Q115_COMMIT, "config/rules_extended.yaml", rootp)
        if text is None:
            raise UnverifiedTerm(f"Q-115's keys are neither merged into config/rules_extended.yaml nor reachable at "
                                 f"{Q115_COMMIT}")
        text = text.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")
        for e in yaml.safe_load(text)["rules"]:
            k = str(e["key"])
            if k not in out:
                out[k] = e
                src[k] = UNMERGED
    return out, src


def record_entry(key: str, root: Path | str = ROOT) -> dict[str, Any]:
    """The record's entry, whatever its status (inspection only)."""
    entries, _ = _record(str(root))
    if key not in entries:
        raise KeyError(f"no entry {key!r} in the record (config/rules_extended.yaml, or {Q115_COMMIT})")
    return entries[key]


def record_source(key: str, root: Path | str = ROOT) -> str:
    """Where a record key was read: `"record"` (the working file) or `UNMERGED` (Q-115's commit)."""
    record_entry(key, root)
    return _record(str(root))[1][key]


def unmerged_keys(root: Path | str = ROOT) -> list[str]:
    """The keys this reading loads that the working record still lacks (read from Q-115's commit)."""
    return [k for k in RECORD_KEYS if record_source(k, root) != "record"]


def record_value(key: str, root: Path | str = ROOT) -> Any:
    """A verified record entry's value; `UnverifiedTerm` for any other status, `NeverLoaded` for a key 14.2 bars."""
    if key in NEVER_LOADED["record"]:
        raise NeverLoaded(f"the record's {key} is never loaded (14.2): it is read only by a rule of 4.3")
    e = record_entry(key, root)
    if e.get("status") != "verified":
        raise UnverifiedTerm(f"{key}: status {e.get('status')!r}, not 'verified' -- it may not be loaded")
    if e.get("value") is None:
        raise UnverifiedTerm(f"{key}: verified without a value")
    return e["value"]


def record_number(key: str, root: Path | str = ROOT) -> float:
    """A verified record value read as a number, fail-loud (`TermParseError`) for anything else."""
    v = record_value(key, root)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise TermParseError(f"{key}: the value {v!r} is not a number")
    return float(v)


def record_whole(key: str, root: Path | str = ROOT) -> int:
    """A verified record value read as a whole number, fail-loud."""
    v = record_number(key, root)
    if not float(v).is_integer():
        raise TermParseError(f"{key}: the value {v!r} is not a whole number")
    return int(v)


def record_dates(root: Path | str = ROOT) -> dict[str, str]:
    """Each loaded record key's date read (for the manifests)."""
    return {k: str(record_entry(k, root).get("date_read", "")) for k in RECORD_KEYS}


# ------------------------------------------------------------------------------------------------ Stage 2's ledger


def stage2_value(key: str) -> Any:
    """A verified entry of Stage 2's vendored ledger, through its own loader (which refuses an entry not verified);
    `NeverLoaded` for a key 14.2 bars (the `hold_expiry_days` sentinel among them). Needs the vendored tree on the
    path (`extended.use_vendored_stage2`)."""
    if key in NEVER_LOADED["stage2"]:
        raise NeverLoaded(f"Stage 2's {key} is never loaded (14.2): "
                          + ("its value is the design sentinel not_required_under_d34, not a reading of any page"
                             if key == "hold_expiry_days" else "it is not a verified reading of a page"))
    from propedge.contract.rules import load_rules

    return load_rules().value(key)


def stage2_number(key: str) -> float:
    v = stage2_value(key)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise TermParseError(f"Stage 2's {key}: the value {v!r} is not a number")
    return float(v)


def stage2_whole(key: str) -> int:
    v = stage2_number(key)
    if not float(v).is_integer():
        raise TermParseError(f"Stage 2's {key}: the value {v!r} is not a whole number")
    return int(v)


# ------------------------------------------------------------------------------------------------ the values used


def reactivation_fee(root: Path | str = ROOT) -> float:
    """L-B's price (2.1): `back2funded_reactivation_fee_50k`, before sales tax."""
    return record_number("back2funded_reactivation_fee_50k", root)


def max_reactivations(root: Path | str = ROOT) -> int:
    """L-B's verified limit per XFA: `back2funded_max_reactivations`."""
    return record_whole("back2funded_max_reactivations", root)


def reactivation_window_days(root: Path | str = ROOT) -> int:
    """L-B's window in calendar days from the closure: `back2funded_window_days`."""
    return record_whole("back2funded_window_days", root)


def naf_prices(root: Path | str = ROOT) -> tuple[float, float]:
    """A-4: the No Activation Fee path's subscription and activation at 50K (`subscription_fee_naf_50k`,
    `activation_fee_naf_50k`), before sales tax."""
    return record_number("subscription_fee_naf_50k", root), record_number("activation_fee_naf_50k", root)


def naf_reset_fee(root: Path | str = ROOT) -> float:
    """The No Activation Fee reset price (stage 0 (c)'s re-solve only; moot in the replay)."""
    return record_number("reset_fee_naf_50k", root)


def standard_prices() -> tuple[float, float]:
    """The Standard path's subscription and activation (Stage 2's verified `subscription_fee`, `activation_fee`)."""
    return stage2_number("subscription_fee"), stage2_number("activation_fee")


def sessions_for_days(days: int | float) -> int:
    """Stage 2's translation of calendar days into the gate's sessions (U-1, U-8): `billing_days` sessions to
    `billing_period_calendar_days` calendar days, rounded to the nearest session."""
    b, p = stage2_whole("billing_days"), stage2_whole("billing_period_calendar_days")
    return int(round(float(days) * b / p))


def funded_cap() -> int:
    """Topstep's cap on active funded accounts (`max_active_funded_accounts`): the funded cap of every cell."""
    return stage2_whole("max_active_funded_accounts")


__all__ = ["RECORD", "DECLARATION", "Q115_COMMIT", "UNMERGED", "RECORD_KEYS", "STAGE2_KEYS", "NEVER_LOADED",
           "UnverifiedTerm", "TermParseError", "NeverLoaded", "record_entry", "record_source", "unmerged_keys",
           "record_value", "record_number", "record_whole", "record_dates", "stage2_value", "stage2_number",
           "stage2_whole", "reactivation_fee", "max_reactivations", "reactivation_window_days", "naf_prices",
           "naf_reset_fee", "standard_prices", "sessions_for_days", "funded_cap"]
