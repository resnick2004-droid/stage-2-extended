"""Portfolio measures for a prop-firm campaign (D-304, D-305): the campaign's cash is the portfolio.

The five accounts are instruments on the firm's capital, not five assets: rotation routes each day's trades to
whichever accounts are flat and their days are shared, so the only equity curve that is the operator's is the
campaign's cash -- bankroll plus payouts received less fees paid -- per resampled path. Every measure here is on that
series, against the capital it needed: the deepest loss from the start plus a margin (one Combine's subscription by
default), at the 90th percentile across paths.

Measures, in 21-trading-day blocks (payouts and fees arrive in steps, so a daily Sharpe would be mostly zeros):

* the campaign Sharpe: mean over standard deviation of the block return (the block's change in cash over the
  required bankroll), times the square root of 252 / 21; its one-sided 95 % lower bound with Lo's (2002) standard
  error for an i.i.d. Sharpe, sqrt((1 + SR^2 / 2) / n) on the per-block statistic; and its deflated version for the
  number of configurations tried (Bailey and Lopez de Prado, 2014): the probability that the Sharpe exceeds the
  expected maximum of k trials' Sharpes under the null;
* Calmar: annualised net over the deepest drawdown from a running peak;
* gain-to-pain: the sum of positive block returns over the sum of the negative ones;
* log growth over the horizon, on the stated bankroll (P2's) and on the required bankroll;
* the break-even denial rate: one minus fees over payouts -- the share of payouts the firm could deny before the
  campaign's cash gain is gone (D-304's fragility line P3 asks for at least 25 %);
* activity (D-305): the share of trading days on which at least one account executed a trade, with its one-sided
  95 % Wilson lower bound ("traded more than not, with 95 % confidence" is a bound above one half), and the Sharpe
  recomputed without the blocks in which no trade was executed (the result must not be made by idle periods).

Every per-path measure is reported as the median across paths with the 10th percentile beside it. `hook` packages
them as a `path_hook` for `propedge.campaign.gate.run_gate`, which adds the columns to each gate row.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Sequence

import numpy as np

BLOCK_DAYS = 21
TRADING_DAYS = 252
Z95 = 1.6448536269514722          # one-sided 95 %
EULER_GAMMA = 0.5772156649015329
DEFAULT_MARGIN = 49.0             # one Combine's subscription (config/rules.yaml, subscription_fee)


# ------------------------------------------------------------------------------------------------ primitives

def wilson_lower(k: int, n: int, z: float = Z95) -> float:
    """The one-sided lower confidence bound of a proportion k / n (Wilson's score interval)."""
    if n <= 0:
        return float("nan")
    p = k / n
    d = 1.0 + z * z / n
    centre = p + z * z / (2.0 * n)
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return float((centre - half) / d)


def block_returns(cash: Sequence[float], base: float, start: float, block: int = BLOCK_DAYS) -> np.ndarray:
    """The change in cash over each full block of `block` days, over `base` dollars; the first block is measured
    from `start` (the cash before day 0). Days past the last full block are left out."""
    c = np.asarray(cash, dtype=float)
    if not base > 0:
        raise ValueError(f"base must be positive, got {base}")
    ends = c[block - 1::block]
    starts = np.concatenate([[float(start)], ends[:-1]])
    return (ends - starts) / float(base)


def sharpe(block_ret: Sequence[float], block: int = BLOCK_DAYS) -> float:
    """The annualised Sharpe of block returns; NaN with fewer than three blocks or no dispersion."""
    r = np.asarray(block_ret, dtype=float)
    if len(r) < 3:
        return float("nan")
    sd = float(r.std(ddof=1))
    if not sd > 1e-12 * max(1.0, abs(float(r.mean()))):       # no dispersion (floating-point noise included)
        return float("nan")
    return float(r.mean() / sd * math.sqrt(TRADING_DAYS / block))


def sharpe_lower_bound(block_ret: Sequence[float], block: int = BLOCK_DAYS, z: float = Z95) -> float:
    """The one-sided lower bound of the annualised Sharpe: Lo's i.i.d. standard error on the per-block statistic,
    sqrt((1 + SR^2 / 2) / n), then annualised."""
    r = np.asarray(block_ret, dtype=float)
    if len(r) < 3:
        return float("nan")
    sd = float(r.std(ddof=1))
    if not sd > 1e-12 * max(1.0, abs(float(r.mean()))):       # no dispersion (floating-point noise included)
        return float("nan")
    sr = float(r.mean() / sd)
    se = math.sqrt((1.0 + sr * sr / 2.0) / len(r))
    return float((sr - z * se) * math.sqrt(TRADING_DAYS / block))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """The standard normal quantile (Acklam's rational approximation, refined by one Newton step)."""
    if not 0.0 < p < 1.0:
        return float("inf") if p >= 1.0 else float("-inf")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p <= phigh:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    e = _norm_cdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def deflated_sharpe(block_ret: Sequence[float], trial_sharpes: Sequence[float], block: int = BLOCK_DAYS) -> float:
    """Bailey and Lopez de Prado's deflated Sharpe: the probability that this campaign's per-block Sharpe exceeds the
    expected maximum of the trials' Sharpes under the null, given their number and dispersion (annualised inputs are
    brought to the block scale). NaN with fewer than two trials or three blocks."""
    r = np.asarray(block_ret, dtype=float)
    t = np.asarray(trial_sharpes, dtype=float)
    t = t[np.isfinite(t)]
    if len(r) < 3 or len(t) < 2:
        return float("nan")
    sd = float(r.std(ddof=1))
    if not sd > 1e-12 * max(1.0, abs(float(r.mean()))):       # no dispersion (floating-point noise included)
        return float("nan")
    scale = math.sqrt(TRADING_DAYS / block)
    sr = float(r.mean() / sd)
    k = len(t)
    v = float(np.var(t / scale, ddof=1))
    if not v > 0:
        return float("nan")
    sr0 = math.sqrt(v) * ((1 - EULER_GAMMA) * _norm_ppf(1 - 1.0 / k) + EULER_GAMMA * _norm_ppf(1 - 1.0 / (k * math.e)))
    n = len(r)
    z = (r - r.mean()) / sd
    skew = float(np.mean(z ** 3))
    kurt = float(np.mean(z ** 4))
    denom = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4.0 * sr * sr))
    return float(_norm_cdf((sr - sr0) * math.sqrt(n - 1) / denom))


def max_drawdown(cash: Sequence[float], start: float) -> float:
    """The deepest fall from a running peak (the start counts as the first peak), in dollars."""
    c = np.concatenate([[float(start)], np.asarray(cash, dtype=float)])
    peak = np.maximum.accumulate(c)
    return float((peak - c).max())


def deepest_loss_from_start(cash: Sequence[float], start: float) -> float:
    c = np.asarray(cash, dtype=float)
    return float(max(0.0, float(start) - c.min())) if len(c) else 0.0


def calmar(cash: Sequence[float], start: float, block: int = BLOCK_DAYS) -> float:
    """Annualised net gain over the deepest drawdown from a peak; infinite with no drawdown, NaN with no days."""
    c = np.asarray(cash, dtype=float)
    if not len(c):
        return float("nan")
    net = float(c[-1]) - float(start)
    annual = net * TRADING_DAYS / len(c)
    dd = max_drawdown(c, start)
    if not dd > 0:
        return float("inf") if annual > 0 else float("nan")
    return float(annual / dd)


def gain_to_pain(block_ret: Sequence[float]) -> float:
    r = np.asarray(block_ret, dtype=float)
    gain, pain = float(r[r > 0].sum()), float(-r[r < 0].sum())
    if not pain > 0:
        return float("inf") if gain > 0 else float("nan")
    return float(gain / pain)


def break_even_denial(fees: float, payouts: float) -> float:
    """One minus fees over payouts: the share of payouts the firm could deny before the gain is gone; NaN with no
    payouts, negative when the fees already exceed them."""
    if not payouts > 0:
        return float("nan")
    return float(1.0 - fees / payouts)


def activity(trades_by_day: Sequence[int], block: int = BLOCK_DAYS) -> dict[str, Any]:
    """The share of days with at least one executed trade, its one-sided 95 % Wilson lower bound, and which full
    blocks had no trade at all."""
    t = np.asarray(trades_by_day, dtype=int)
    n = len(t)
    k = int((t > 0).sum())
    nb = n // block
    idle = np.array([t[i * block:(i + 1) * block].sum() == 0 for i in range(nb)], dtype=bool)
    return {"days": n, "days_traded": k, "share": (k / n if n else float("nan")), "bound": wilson_lower(k, n),
            "idle_blocks": idle}


# --------------------------------------------------------------------------------------------- per path / paths

def path_measures(cash: Sequence[float], start: float, base: float, fees: float, payouts: float,
                  trades_by_day: Sequence[int] | None, block: int = BLOCK_DAYS) -> dict[str, float]:
    """One path's measures on `base` dollars of capital; `start` is the cash before day 0."""
    c = np.asarray(cash, dtype=float)
    r = block_returns(c, base, start, block)
    lg = float(math.log((base + (c[-1] - start)) / base)) if len(c) and base + (c[-1] - start) > 0 else float("-inf")
    out = {
        "sharpe": sharpe(r, block), "sharpe_lb": sharpe_lower_bound(r, block), "calmar": calmar(c, start, block),
        "gain_to_pain": gain_to_pain(r), "net": float(c[-1] - start) if len(c) else float("nan"),
        "log_growth_on_base": lg,
        # D-312: the same growth as a year's rate -- the gate's growth when the bankroll is an output of the run
        "growth_on_base": (lg * TRADING_DAYS / len(c)) if len(c) and np.isfinite(lg) else (lg if len(c) else float("nan")),
        "deepest_loss_from_start": deepest_loss_from_start(c, start), "max_drawdown": max_drawdown(c, start),
        "break_even_denial": break_even_denial(fees, payouts),
    }
    if trades_by_day is not None and len(trades_by_day):
        a = activity(trades_by_day, block)
        out.update({"activity_share": a["share"], "activity_bound": a["bound"],
                    "idle_blocks": int(a["idle_blocks"].sum()), "blocks": int(len(r))})
        keep = ~a["idle_blocks"][:len(r)]
        out["sharpe_active"] = sharpe(r[keep], block) if keep.any() else float("nan")
    return out


def _pct(x: list[float], q: float) -> float:
    """The q-th percentile, None and NaN left out. D-319 (the v6 audit, finding 4): a path whose growth is minus
    infinity -- it lost more than the bankroll -- is the worst value, counted, not dropped; a percentile that falls on
    or beside it is minus infinity. Without an infinite value the arithmetic is as before, to the bit. D-334 (the
    audit of D-333, finding 10): "beside" is read from the sorted position numpy interpolates between, (n - 1) q / 100,
    not from the clipped interpolation's size -- that returned about -1e299 for a position just above a minus
    infinity (50 of 500 paths at minus infinity, the p10)."""
    v = np.asarray([y for y in x if y is not None and not np.isnan(y)], dtype=float)
    if not len(v):
        return float("nan")
    if np.isfinite(v).all():
        return float(np.percentile(v, q))
    s = np.sort(v)
    k = (len(s) - 1) * float(q) / 100.0
    lo, hi = s[int(np.floor(k))], s[int(np.ceil(k))]
    if lo == -np.inf:                        # the position falls on, or just above, a minus infinity
        return float("-inf")
    if hi == np.inf:                         # ... or on, or just below, a plus infinity
        return float("inf")
    return float(np.percentile(np.clip(v, -1e300, 1e300), q))   # both neighbours finite: numpy's own interpolation of them


def required_bankroll(paths: Sequence[Any], margin: float = DEFAULT_MARGIN) -> dict[str, float]:
    """The bankroll each path needed (its deepest loss from the start plus `margin`), and its distribution."""
    need = [deepest_loss_from_start(p.path.cash_series, p.path.initial_bankroll) + float(margin) for p in paths]
    return {"required_p50": _pct(need, 50), "required_p90": _pct(need, 90), "required_p99": _pct(need, 99),
            "required_worst": float(max(need)) if need else float("nan")}


def measures(paths: Sequence[Any], *, margin: float = DEFAULT_MARGIN, block: int = BLOCK_DAYS,
             trial_sharpes: Sequence[float] | None = None) -> dict[str, float]:
    """The portfolio measures across resampled paths (`LockstepPath`s: `.path.cash_series`, `.path.initial_bankroll`,
    `.path.total_fees`, `.path.total_payouts`, `.path.trades_by_day`): the capital base is the required bankroll at
    p90; each per-path measure as its median and 10th percentile; `trial_sharpes` (the other configurations'
    annualised campaign Sharpes) deflates the median Sharpe."""
    req = required_bankroll(paths, margin)
    base = req["required_p90"]
    if not np.isfinite(base) or not base > 0:
        base = max(float(margin), 1.0)
    per = [path_measures(p.path.cash_series, p.path.initial_bankroll, base, p.path.total_fees, p.path.total_payouts,
                         getattr(p.path, "trades_by_day", None), block) for p in paths]
    out: dict[str, float] = {"base": float(base), "paths": float(len(per)), **req}
    for key in ("sharpe", "sharpe_lb", "sharpe_active", "calmar", "gain_to_pain", "net", "log_growth_on_base",
                "growth_on_base", "max_drawdown", "break_even_denial", "activity_share", "activity_bound"):
        vals = [m.get(key) for m in per if key in m]
        if vals:
            out[f"{key}_p50"] = _pct(vals, 50)
            out[f"{key}_p10"] = _pct(vals, 10)
    if "idle_blocks" in per[0] if per else False:
        out["idle_blocks_p50"] = _pct([m["idle_blocks"] for m in per], 50)
        flips = [1.0 if (np.isfinite(m["sharpe"]) and np.isfinite(m["sharpe_active"])
                         and np.sign(m["sharpe"]) != np.sign(m["sharpe_active"])) else 0.0 for m in per]
        out["share_sharpe_sign_changed_without_idle"] = float(np.mean(flips)) if flips else float("nan")
    out["return_on_required"] = float(out["net_p50"] * TRADING_DAYS / max(len(paths[0].path.cash_series), 1) / base) if per else float("nan")
    if trial_sharpes is not None and per:
        # deflate the median path's Sharpe: the path whose Sharpe is the median
        srs = np.asarray([m["sharpe"] for m in per], dtype=float)
        i = int(np.argsort(np.where(np.isfinite(srs), srs, -np.inf))[len(srs) // 2])
        p = paths[i]
        r = block_returns(p.path.cash_series, base, p.path.initial_bankroll, block)
        out["sharpe_deflated_p50"] = deflated_sharpe(r, trial_sharpes, block)
    return out


def slot_use(lockstep_path: Any) -> dict[str, float]:
    """D-329: one path's slot use from its account records (a `LockstepPath`: `.combines`, `.funded`) -- the slot-days
    its Combine attempts and XFAs held (a reset attempt's days count with its account), how many of each, and how many
    the policy abandoned. The efficiency measures' input; lives here so the Studio can read it too."""
    combines = tuple(getattr(lockstep_path, "combines", ()) or ())
    funded = tuple(getattr(lockstep_path, "funded", ()) or ())
    c_days = float(sum(int(c.days) for c in combines))
    f_days = float(sum(int(a.days) for a in funded))
    return {"combine_slot_days": c_days, "xfa_slot_days": f_days, "slot_days": c_days + f_days,
            "combine_attempts": float(len(combines)), "xfas": float(len(funded)),
            "combines_abandoned": float(sum(1 for c in combines if getattr(c, "abandoned_by_policy", False))),
            "xfas_abandoned": float(sum(1 for a in funded if getattr(a, "abandoned", False)))}


def hook(*, margin: float = DEFAULT_MARGIN, block: int = BLOCK_DAYS, trial_sharpes: Sequence[float] | None = None,
         prefix: str = "pf_") -> Callable[[str, float, Sequence[Any]], dict[str, float]]:
    """A `path_hook` for `gate.run_gate`: the portfolio measures of each run's paths as columns `pf_*`."""
    def _hook(shift: str, enforcement_p: float, paths: Sequence[Any]) -> dict[str, float]:
        return {prefix + k: v for k, v in measures(paths, margin=margin, block=block, trial_sharpes=trial_sharpes).items()}
    return _hook


__all__ = ["BLOCK_DAYS", "TRADING_DAYS", "Z95", "DEFAULT_MARGIN", "wilson_lower", "block_returns", "sharpe",
           "sharpe_lower_bound", "deflated_sharpe", "max_drawdown", "deepest_loss_from_start", "calmar", "gain_to_pain",
           "break_even_denial", "activity", "path_measures", "required_bankroll", "measures", "slot_use", "hook"]
