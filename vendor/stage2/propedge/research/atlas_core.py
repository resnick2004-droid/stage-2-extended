"""The effect atlas's per-day measurements, in plain Python, shared by the repository and the kits.

`config/effect_atlas.yaml` fixes the definitions (D-126). The QuantConnect kits embed this module's
source verbatim (`propedge/data/qc_algorithms.atlas_preamble`); tests compute the same numbers on
synthetic bars. Only these per-day numbers leave the cloud (D-120).

Bar slots are indexed by END time from REC_FIRST = open - 3 minutes: slots 0..3 are the pre-open bars,
slot 4 is the open bar (ending open + 1), slot 3 + m ends at open + m, and the last slot ends at the
settlement minute. Missing bars are None. Returns are 100 x ln(ratio), in percent; realised variances
are sums of squared percent returns.
"""
from math import log as _ln   # natural log; aliased so it is never mistaken for a log call

PRE = 3                               # pre-open bars end at open-3 .. open (slots 0..3)
OPEN_SLOT = PRE + 1                   # the bar ending at open + 1


def _ffill_at(c, j):
    for k in range(j, -1, -1):
        if c[k] is not None:
            return c[k]
    return None


def _lr(a, b):
    return 100.0 * _ln(a / b)


def _median(xs):
    s = sorted(xs)
    n = len(s)
    return None if n == 0 else (s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2]))


def extra_measures(o, h, l, c, tick, settle_slot, v=None, qb=None, qa=None, qbs=None, qas=None):
    """D-128's extra per-day measures: session high and low, opening-range close location, volume and the
    quoted spread and top-of-book imbalance (config/effect_atlas.yaml, amendment_d128.extra_measures).
    `v` is each slot's volume; `qb`, `qa`, `qbs`, `qas` each slot's closing bid, ask, bid size and ask size."""
    out = {}
    O = o[OPEN_SLOT]
    if O is None:
        return out
    n_slots = settle_slot + 1
    sess = [j for j in range(OPEN_SLOT, n_slots) if o[j] is not None]
    out["hi"] = _lr(max(h[j] for j in sess), O)
    out["lo"] = _lr(min(l[j] for j in sess), O)
    first = [j for j in range(OPEN_SLOT, PRE + 31) if o[j] is not None]
    H30, L30 = max(h[j] for j in first), min(l[j] for j in first)
    p30 = _ffill_at(c, PRE + 30)
    out["cl30"] = (p30 - L30) / (H30 - L30) if H30 > L30 else None
    if v is not None:
        out["v30"] = sum(v[j] for j in range(OPEN_SLOT, PRE + 31) if v[j] is not None)
        out["vd"] = sum(v[j] for j in range(OPEN_SLOT, n_slots) if v[j] is not None)
    if qb is not None:
        spreads, sp30, imb = [], [], []
        for j in range(OPEN_SLOT, n_slots):
            b, a = qb[j], qa[j]
            if b is None or a is None or not (b > 0 and a >= b):
                continue
            s = (a - b) / tick
            spreads.append(s)
            if j <= PRE + 30:
                sp30.append(s)
                bs, as_ = qbs[j], qas[j]
                if bs is not None and as_ is not None and bs + as_ > 0:
                    imb.append((bs - as_) / (bs + as_))
        expected = n_slots - OPEN_SLOT
        out["qcov"] = len(spreads) / expected
        out["sp"] = _median(spreads)
        out["sp30"] = sum(sp30) / len(sp30) if sp30 else None
        out["spw"] = sum(1 for s in spreads if s > 1.0 + 1e-9) / len(spreads) if spreads else None
        out["imb30"] = sum(imb) / len(imb) if imb else None
    return out


def atlas_measures(o, h, l, c, s0, tick, settle_slot):
    """The per-day measurement dict for one market and one day (see config/effect_atlas.yaml)."""
    out = {}
    n_slots = settle_slot + 1
    bad = 0
    for i in range(n_slots):
        if o[i] is None:
            continue
        vals = (o[i], h[i], l[i], c[i])
        if (not (l[i] <= min(o[i], c[i]) and max(o[i], c[i]) <= h[i])
                or any(abs(v / tick - round(v / tick)) > 1e-6 for v in vals)):
            bad += 1
    out["bad"] = bad
    pre = [(h[i] - l[i]) / tick for i in range(0, OPEN_SLOT) if o[i] is not None]
    out["rp"] = sum(pre) / len(pre) if pre else None
    out["r0"] = (h[OPEN_SLOT] - l[OPEN_SLOT]) / tick if o[OPEN_SLOT] is not None else None
    expected = settle_slot - OPEN_SLOT + 1
    out["cov"] = sum(1 for i in range(OPEN_SLOT, n_slots) if o[i] is not None) / expected
    out["st"] = 1 if o[settle_slot] is not None else 0
    O = o[OPEN_SLOT]
    out["op"] = 1 if O is not None else 0
    if O is None:
        return out
    p30 = _ffill_at(c, PRE + 30)
    p60 = _ffill_at(c, PRE + 60)
    pm = _ffill_at(c, settle_slot - 30)
    S = _ffill_at(c, settle_slot)
    out["S"] = S
    out["on"] = _lr(O, s0) if s0 else None
    out["r30"] = _lr(p30, O)
    out["r60"] = _lr(p60, O)
    out["rr30"] = _lr(S, p30)
    out["mid"] = _lr(pm, p30)
    out["l30"] = _lr(S, pm)
    out["day"] = _lr(S, O)
    seq30 = [O] + [_ffill_at(c, j) for j in range(OPEN_SLOT, PRE + 31)]
    out["rv30"] = sum(_lr(b, a) ** 2 for a, b in zip(seq30, seq30[1:]))
    seqd = [O] + [_ffill_at(c, j) for j in range(OPEN_SLOT, n_slots)]
    out["rvd"] = sum(_lr(b, a) ** 2 for a, b in zip(seqd, seqd[1:]))
    hs = [h[j] for j in range(OPEN_SLOT, PRE + 31) if h[j] is not None]
    ls = [l[j] for j in range(OPEN_SLOT, PRE + 31) if l[j] is not None]
    H30, L30 = max(hs), min(ls)
    out["rg30"] = 100.0 * (H30 - L30) / O
    if s0:
        out["gf"] = 1 if any(l[j] <= s0 <= h[j] for j in range(OPEN_SLOT, n_slots) if o[j] is not None) else 0
    bd, ba, br = 0, 0, None
    for j in range(PRE + 31, n_slots):
        if o[j] is None:
            continue
        up, dn = h[j] > H30, l[j] < L30
        if up and dn:
            ba = 1
            break
        if up or dn:
            bd = 1 if up else -1
            br = bd * _lr(S, c[j])
            break
    out["bd"], out["ba"], out["br"] = bd, ba, br
    return out
