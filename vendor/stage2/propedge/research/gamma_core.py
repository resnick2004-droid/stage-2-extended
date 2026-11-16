"""Net gamma exposure of option market makers, per session (D-128), in plain Python for the R038 kit.

Baltussen, Da, Lammers and Martens (2021), "Hedging demand and market intraday momentum", Journal of
Financial Economics 142, eq. 13-15: for every contract, gamma x open interest x 100 x the index level,
counted + for calls and - for puts (their assumption: option market makers are long calls and short puts).
The paper divides by the index's market value; only the sign is tested here (their Table 7), so the sum is
reported in billions, unnormalised.

Gamma is Black-Scholes with r = q = 0 from each contract's implied volatility (`nge_b`, the tested one);
the platform's own gamma gives `nge_l` beside it as a check (config/effect_atlas.yaml, amendment_d128).
The QuantConnect kit embeds this module's source verbatim (`propedge/data/qc_algorithms.context_preamble`).
"""
from math import exp as _exp, log as _ln, pi as _pi, sqrt as _sqrt   # _ln: never mistaken for a log call


def bs_gamma(s, k, t, iv):
    """Black-Scholes gamma per index point, r = q = 0; None when an input is unusable."""
    if not (s > 0 and k > 0 and t > 0 and iv > 0):
        return None
    vt = iv * _sqrt(t)
    d1 = (_ln(s / k) + 0.5 * vt * vt) / vt
    return _exp(-0.5 * d1 * d1) / _sqrt(2.0 * _pi) / (s * vt)


def nge(rows, s):
    """(nge_b, nge_l, n_used) for one session. `rows` are (is_call, strike, years_to_expiry, implied_vol,
    open_interest, platform_gamma or None); `s` is the index level. Values in billions."""
    b, pl, n = 0.0, 0.0, 0
    for is_call, k, t, iv, oi, g_platform in rows:
        if not (oi is not None and oi > 0):
            continue
        sign = 1.0 if is_call else -1.0
        g = bs_gamma(s, k, t, iv)
        if g is not None:
            b += sign * g * oi * 100.0 * s
            n += 1
        if g_platform is not None and g_platform == g_platform:
            pl += sign * g_platform * oi * 100.0 * s
    return b / 1e9, pl / 1e9, n
