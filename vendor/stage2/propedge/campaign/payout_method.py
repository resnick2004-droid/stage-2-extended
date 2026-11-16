"""Payout method terms: the fee and the processing lag are one joint choice (D-24).

Topstep's payout page (article 8284233) gives a fee and a processing time **per method**, and
never a combined request-to-receipt total: internal approval ("1-3 business days") and the
transfer are two stages. The ledger records the slow-end sums as loadable values -- Aeropay
3 trading days at no fee, ACH 6 trading days at $30 -- and this module is the one place they
are paired, so that no simulation can run the two halves of different methods: ($30, 3) and
($0, 6) do not exist. Business days map about 1:1 to the engine's trading-day index.

Zero lag is not a supported default (D-24): `propedge.campaign.reinvest.simulate_campaign`
resolves the lag here when the caller does not state one, and `simulate_path` has no default
at all.

Every value is read through the verified-rule gate (`propedge.contract.rules`), so a method
whose terms are not on the ledger cannot be simulated.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

#: The US baseline: no Topstep fee, about three trading days end to end.
AEROPAY = "aeropay"
#: The conservative US case: $30 per payout, about six trading days end to end.
ACH = "ach"

#: method -> (fee rule key, lag rule key) in `config/rules.yaml`. Both keys of a method were
#: verified together from the same article, which is what makes the pairing legitimate.
_METHOD_KEYS: dict[str, tuple[str, str]] = {
    AEROPAY: ("payout_fee", "payout_lag_days_aeropay"),
    ACH: ("payout_fee_ach", "payout_lag_days_ach"),
}


@dataclass(frozen=True)
class PayoutMethodTerms:
    """Fee and lag for one payout method, with the ledger keys they came from."""

    method: str
    fee: float          # dollars per payout; charged inside the funded engine (Rules.payout_fee)
    lag_days: int       # trading days from eligibility to cash; applied by the campaign clock
    fee_key: str
    lag_key: str
    article_id: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def available_methods() -> tuple[str, ...]:
    """Methods whose fee and lag are both on the ledger."""
    return tuple(_METHOD_KEYS)


def payout_method_terms(method: str = AEROPAY, *, ledger: Any | None = None) -> PayoutMethodTerms:
    """The fee and lag for `method`, read through the verified-rule gate.

    Raises:
        ValueError: unknown method. A lag is never combined with another method's fee.
        UnverifiedRuleError: a term is on the ledger but not verified.
    """
    try:
        fee_key, lag_key = _METHOD_KEYS[method]
    except KeyError:
        raise ValueError(
            f"unknown payout method {method!r}; known: {sorted(_METHOD_KEYS)}. Fee and lag are "
            "one joint choice per method (D-24), so a lag cannot be paired with another "
            "method's fee."
        ) from None
    if ledger is None:
        from propedge.contract.rules import load_rules

        ledger = load_rules()
    fee = float(ledger.value(fee_key))
    lag = int(ledger.value(lag_key))
    article = str(ledger.entry(lag_key).article_id or "")
    return PayoutMethodTerms(
        method=method, fee=fee, lag_days=lag, fee_key=fee_key, lag_key=lag_key,
        article_id=article,
    )


def rules_for_method(method: str = AEROPAY, *, ledger: Any | None = None, **overrides: Any):
    """Engine `Rules` from the ledger with `payout_fee` set to the method's fee.

    Use this to build the attempt pool for a campaign that names `payout_method`, so the fee
    inside the funded engine and the lag applied by the campaign clock belong to the same
    method. `payout_fee` may not be overridden here: choose the method instead.
    """
    if "payout_fee" in overrides:
        raise ValueError("payout_fee is set by the payout method; choose the method instead")
    from propedge.contract.adapter import rules_from_ledger

    terms = payout_method_terms(method, ledger=ledger)
    return rules_from_ledger(payout_fee=terms.fee, **overrides)


__all__ = [
    "AEROPAY",
    "ACH",
    "PayoutMethodTerms",
    "available_methods",
    "payout_method_terms",
    "rules_for_method",
]
