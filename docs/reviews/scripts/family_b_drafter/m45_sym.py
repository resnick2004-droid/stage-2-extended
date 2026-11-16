# Family B's drafter (Q-65): a scratch check behind prereg/DRAFT_F-B_multifeature.md (fifth version) -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing. Run with PYTHONPATH set to the
# worktree's root and its tests/ folder (it imports tests/test_family_b_b2.py's helpers).
# What it checks: M4-1 and m4-4: (d) over the twin only or over the twin and the model, with the twin-only or the symmetric null; and the symmetric component's advantage by amplitude.

import numpy as np
from scipy import stats
import test_family_b_b2 as T
R = 8000
def d_test(seed, symmetric_d, symmetric_null):
    rng = np.random.default_rng(seed)
    g_judged, g_pre = 0.03, 0.006
    grid = np.round(np.arange(0.004, 0.0801, 0.004), 4)
    q = T.follow_null_quantiles(rng, np.r_[g_pre, grid], 4000, symmetric=symmetric_null)
    gt = g_judged * (1.0 + T.markov(rng, 1 / 250, R, T.FOLLOW_N))
    truth = -2 * T.FOLLOW_Q_DIS * (gt - g_judged) + T.FOLLOW_SIG * rng.standard_normal((R, T.FOLLOW_N))
    twin = gt + T.FOLLOW_SIG * rng.standard_normal((R, T.FOLLOW_N))
    model = g_judged + T.FOLLOW_SIG * rng.standard_normal((R, T.FOLLOW_N))
    ys = (slice(0, 252), slice(252, 504), slice(504, T.FOLLOW_N))
    dy = lambda o: np.max(np.abs(np.stack([o[:, y].mean(1) for y in ys], 1)), 1)
    d = np.maximum(dy(twin), dy(model)) if symmetric_d else dy(twin)
    tb = T.component_t(truth); nom = np.array([stats.t.ppf(1 - T.ALPHA, tb[b][1]) for b in T.COMPONENTS])
    pre = np.array([q[g_pre][b] for b in T.COMPONENTS])
    idx = np.minimum(np.searchsorted(grid, np.maximum(g_pre, d) - 1e-12), len(grid) - 1)
    post = np.array([[q[grid[i]][b] for b in T.COMPONENTS] for i in idx])
    return T._rate(tb, np.maximum(np.maximum(nom, pre), post))
for sd, sn in ((False, False), (False, True), (True, False), (True, True)):
    print("d over twin+model:", sd, "symmetric null:", sn, "rate %.4f" % d_test(9101, sd, sn))
def sym_test(seed, g):
    rng = np.random.default_rng(seed)
    gt = g * (1.0 + T.markov(rng, 1 / 250, R, T.FOLLOW_N)); ht = g * (1.0 + T.markov(rng, 1 / 250, R, T.FOLLOW_N))
    truth = 2 * T.FOLLOW_Q_DIS * ((ht - g) - (gt - g)) + T.FOLLOW_SIG * rng.standard_normal((R, T.FOLLOW_N))
    tb = T.component_t(truth); nom = np.array([stats.t.ppf(1 - T.ALPHA, tb[b][1]) for b in T.COMPONENTS])
    out = []
    for sym in (False, True):
        qq = T.follow_null_quantiles(rng, [g], 4000, symmetric=sym)[g]
        out.append(T._rate(tb, np.tile(np.maximum(nom, [qq[b] for b in T.COMPONENTS]), (R, 1))))
    return out
for g in (0.03, 0.05, 0.08):
    print("symmetric case g %.2f: twin-only %.4f symmetric %.4f" % ((g,) + tuple(sym_test(9201, g))))

# Printed (run 2026-11-16):
# d over twin+model: False symmetric null: False rate 0.0413
# d over twin+model: False symmetric null: True rate 0.0255
# d over twin+model: True symmetric null: False rate 0.0008
# d over twin+model: True symmetric null: True rate 0.0001
# symmetric case g 0.03: twin-only 0.0143 symmetric 0.0060
# symmetric case g 0.05: twin-only 0.0077 symmetric 0.0081
# symmetric case g 0.08: twin-only 0.0051 symmetric 0.0076
