"""F-03 (family O) the second build read's minors on synthetic inputs: A9's offsets proportional per kind (n2; on a realistic calendar's kind mix), A3's
cuts with report days and never truncated (n1), and numpy's seed-key zero-padding (note B): no two of the family's
derived keys collide. Seeds `[SEED_TESTS, 1400, ...]` (section 16's test block).
"""
from __future__ import annotations

import itertools
from datetime import date

import numpy as np
import pandas as pd

from extended import opening_stats as ST


def _layout(n=754, seed=0):
    rng = np.random.default_rng([ST.SEED_TESTS, 1400, seed])
    sessions = [str(d.date()) for d in pd.bdate_range("2021-01-04", periods=n)]
    days = pd.bdate_range("2021-01-04", periods=n)
    # a realistic mix: report days the first Friday of each month, eight FOMC days a year, a few early closes
    kinds = np.array(["b" if (d.weekday() == 4 and d.day <= 7) else "n" for d in days], dtype=object)
    kinds[rng.choice(np.flatnonzero(kinds == "n"), size=8 * 3, replace=False)] = "o"
    kinds[rng.choice(np.flatnonzero(kinds == "n"), size=6, replace=False)] = "e"
    kinds = kinds.astype(str)
    rows = [(s, m, k, int(s[:4]), k in ("n", "b")) for s, k in zip(sessions, kinds) for m in (0, 60)]
    pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year", "population"])
    pop["c"] = rng.normal(size=len(pop))
    return ST.layout(pop, sessions, kinds=dict(zip(sessions, kinds)), values=("c",))


def test_a9s_sources_are_about_the_offset_away_on_every_population_kind():
    L = _layout()
    base = np.arange(L.n)
    for o in (63, 200, L.n - 64):
        idx = ST.within_kind_index(L, base, o)
        assert (L.kind[idx] == L.kind[base]).all()
        for k in ("n", "b"):
            m = L.kind == k
            d = (idx[m] - base[m]) % L.n
            d = np.minimum(d, L.n - d)
            want = min(o, L.n - o)
            assert np.median(np.abs(d - want)) <= 12, (o, k)
            assert d.min() >= 40, (o, k)                       # never wrapped near itself (n2)


class _St:
    def __init__(self, days, report):
        self.days = days
        self._sh = np.ones((len(days), 3))

    def share(self, c):
        return self._sh


def test_a3s_cuts_draw_report_days_and_are_never_truncated(monkeypatch):
    import importlib.util
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("fo_opening_minors", root / "scripts" / "fo_opening.py")
    FO = importlib.util.module_from_spec(spec)
    sys.modules["fo_opening_minors"] = FO
    spec.loader.exec_module(FO)
    days = [d.date() for d in pd.bdate_range("2020-06-01", periods=700)]
    report = {i for i, d in enumerate(days) if d.weekday() == 4 and d.day <= 7}
    monkeypatch.setattr(FO, "special_sessions", lambda g: list(range(0, 400, 20)))     # 20 roll/DST sessions first
    cuts = FO.a3_cuts(None, _St(days, report), 200, report)
    cut_days = {d for d, _ in cuts}
    assert len(cut_days & report) >= FO.A3_REPORT_DAYS
    assert any(m == FO.F_slot(7, 40) for d, m in cuts if d in report)
    assert len(cuts) >= 200 and len(cuts) == sum(8 + (d in report) for d in dict.fromkeys(d for d, _ in cuts))


def test_no_two_derived_seed_keys_collide_after_zero_padding():
    """numpy pads a key shorter than four words with zeros (`[a, b]` is `[a, b, 0, 0]`): the family's keys, each
    padded to its generator's entropy, are all distinct (note B)."""
    def state(key):
        return tuple(np.random.SeedSequence(list(key)).generate_state(4))

    assert state([1, 2]) == state([1, 2, 0, 0])                               # the hazard itself
    keys = [(ST.SEED_STAGE_B, i) for i in range(3)] + [(ST.SEED_SHIFT, j) for j in range(5)]
    keys += [(ST.SEED_SHIFT, 10 ** 6)] + [(ST.SEED_SHIFT, 2 * 10 ** 6 + d) for d in range(3)]
    keys += [(ST.SEED_TWIN, c, b, d) for c, b, d in itertools.product(range(4), range(3), range(2))]
    keys += [(ST.SEED_A10, c, s, j) for c, s, j in itertools.product(range(6), range(2), range(4))]
    keys += [(ST.SEED_A10, c, s, j, i) for c, s, j, i in itertools.product(range(6), range(2), range(3), range(3))]
    keys += [(ST.SEED_B2, line, j) for line in (0, 1, 2, 10, 11, 12) for j in range(4)]
    keys += [(ST.SEED_SCORECARD, 0), (ST.SEED_SCORECARD, 1)]
    keys += [(ST.SEED_K0, c, f, j) for c, f, j in itertools.product(range(4), range(5), range(3))]
    keys += [(ST.SEED_TESTS, j) for j in range(10)] + [(ST.SEED_TESTS, 100)]
    keys += [(ST.SEED_TESTS, 200, j, 0) for j in range(3)]          # T-10's data (the declared [.., 200, j] padded)
    keys += [(ST.SEED_TESTS, 200, j, 1, i) for j in range(3) for i in range(3)]
    keys += [(ST.SEED_TESTS, k, 0) for k in (300, 400, 500, 700, 800, 900, 1000, 1100, 1200, 1300, 1400)]
    states = [state(k) for k in keys]
    dup = [(a, b) for (a, sa), (b, sb) in itertools.combinations(zip(keys, states), 2) if sa == sb]
    assert dup == [], dup
