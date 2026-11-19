"""Wave 3.4: the lever-space sampler, the cell ledger and the readings door (`extended/search_space.py`), on synthetic
spaces and on the Topstep $50K lever space as `extended/lever_space.py` loads it (rules and configuration only; no bar).

What is asserted: every returned design passes every constraint, each checked here independently of the module
(windows on the mark grid, inside their sessions and never colliding; the loader's combination rules; latency cells as
`lever_space.latency_cells` gives them; conduct tier 1 never returned); **every cell proposed is in the ledger**, the
refused ones included, shown by replaying the sampler's unit points by hand; the sampler is reproducible from its seed
and space-filling (stratified marginals, lower discrepancy than independent draws); the door refuses anything tagged
held-out or touching the held-out years. **Mutations** (each a planted defect a test here must catch): the collision
check removed, refused cells left unrecorded, the tier-1 check removed, the seed ignored, the door left open.
"""
from __future__ import annotations

import sys
import warnings
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import qmc

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import components as C  # noqa: E402
from extended import day_calendar as DC  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import search_space as SS  # noqa: E402
from extended import triggers as T  # noqa: E402

SEED = 4242
SLOTS = {"london": 1, "ny": 2}


@pytest.fixture(scope="module")
def lever():
    return SS.from_lever_space(slots=SLOTS)


# ------------------------------------------------------------------------------------------------ independent checks


def constraint_problems(space: SS.Space, designs) -> list[str]:
    """Every constraint, re-checked here without `Space.check`."""
    out = []
    for d in designs:
        w = []
        for s in space.slots:
            if d[SS.slot_dim(s.name, "on")] != SS.ON:
                continue
            a, b = d[SS.slot_dim(s.name, "first")], d[SS.slot_dim(s.name, "last")]
            if not (s.lo <= a <= b <= s.hi) or (a - s.lo) % s.step or (b - s.lo) % s.step:
                out.append(f"window {s.name} [{a}, {b}] off its session or grid")
            w.append((s.session, a, b, s.name))
        w.sort()                                        # offsets compare within a session (absolute: `day_problems`)
        out += [f"collision {x[3]} {y[3]}" for x, y in zip(w, w[1:]) if x[0] == y[0] and y[1] <= x[2]]
        if space.slots and not w:
            out.append("no component on")
        for v in d.values():
            if isinstance(v, str) and v in SS.TIER_ONE:
                out.append(f"tier-1 value {v}")
    return out


#: a winter day, a summer day, and the two US/UK mismatch weeks (London at 03:00 CT)
DAYS = (date(2021, 1, 15), date(2021, 7, 15), date(2021, 3, 17), date(2021, 11, 2))


def day_problems(space: SS.Space, designs, days) -> list[str]:
    """Each design's windows read on each date: inside that date's session (`components.session_bounds(day)`, from
    `lever_space.session_windows(day)`), at or before the last new entry, on the mark grid, never colliding."""
    out = []
    for day in days:
        b = C.session_bounds(day)
        for d in designs:
            ws = space.windows_on(d, day)
            for name, sess, a, z in ws:
                lo, hi = b["ny_am" if sess == "ny" else sess]
                if not (lo <= a <= z < hi) or z > b["_last_entry"][1] or a % 5 or z % 5:
                    out.append(f"{day} {name} [{a}, {z}] leaves {sess} [{lo}, {hi})")
            out += [f"{day} collision {x[0]} {y[0]}" for x, y in zip(ws, ws[1:]) if y[2] <= x[3]]
            if any(s == "rl3" for s in (d.get(SS.slot_dim(w[0], "T1")) for w in ws)):
                for name, sess, a, z in ws:
                    if d[SS.slot_dim(name, "T1")] == "rl3" and not a <= T.LIVE_0900 <= z:
                        out.append(f"{day} rl3 window misses 09:00")
    return out


def lever_problems(space: SS.Space, designs) -> list[str]:
    out = constraint_problems(space, designs) + day_problems(space, designs, DAYS)
    for d in designs:
        try:
            LS.check_design({k: d[k] for k in ("A4", "A12")})
        except Exception as e:                                          # noqa: BLE001
            out.append(f"rule: {e}")
        for s in space.slots:
            if d[SS.slot_dim(s.name, "on")] != SS.ON:
                continue
            src, lat, ent = (d[SS.slot_dim(s.name, k)] for k in ("T1", "T4", "T5"))
            if lat not in LS.latency_cells(src):
                out.append(f"latency {lat} off {src}'s cells")
            if (src == "rl3" and ent != SS.TICKET) or (src != "rl3" and ent not in LS.bounds("T5").values):
                out.append(f"entry {ent} for {src}")
            if s.session != "ny" and not T.overnight_allowed() and not getattr(space, "_test_overnight", False):
                out.append(f"overnight slot {s.name} on before H2")
    return out


def replay_problems(space: SS.Space, ledger: SS.CellLedger, seed: int, method: str, designs) -> list[str]:
    """The sampler's unit points replayed by hand: the ledger holds exactly one row a point consumed, in order, each
    with the status the space gives it, and the returned designs are the passing rows."""
    rng = SS.child_rng(seed, SS.STREAM_SURVEY, 0)
    pts = SS.UnitPoints(method, space.d, rng)
    want, n, got = [], len(designs), 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        while got < n:                                   # the sampler asks for the designs still wanted
            for u in pts.next(n - got):
                if got == n:
                    break
                x = space.decode(u)
                want.append(x)
                got += space.check(x) is None
    out = []
    if [r["design"] for r in ledger.rows] != want:
        out.append("ledger rows differ from the points consumed")
    for r in ledger.rows:
        st = "refused" if space.check(r["design"]) is not None else "proposed"
        if st != r["status"]:
            out.append(f"cell {r['cell']} recorded {r['status']}, is {st}")
    if [r["design"] for r in ledger.rows if r["status"] == "proposed"] != list(designs):
        out.append("returned designs are not the passing rows")
    # the last row must be the last returned design: nothing was consumed after it without a row
    if ledger.rows and ledger.rows[-1]["status"] != "proposed":
        out.append("the survey's last cell is not its last design")
    c = ledger.counts()
    if c["cells"] != c["proposed"] + c["refused"]:
        out.append("cells != proposed + refused")
    return out


# ------------------------------------------------------------------------------------------------ the lever space


def test_the_lever_space_loads_what_the_loader_loads_and_carries_its_refusals(lever):
    names = set(lever.names())
    for k in LS.refusals():
        assert k not in names and k in lever.refused                   # S1, T7, A9, A19, T2b, A15-A17, dropped
    for k in ("S3", "S4", "S5", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10", "A11", "A12", "A18"):
        assert k in names
    for k in ("T6", "T8", "A20", "A21"):
        assert lever.fixed[k] == LS.bounds(k).values
    assert lever.fixed["overlap"] == "refused"
    for k in ("A6", "A7", "A11", "A12"):
        r = LS.bounds(k)
        assert lever.dim(k).kind == SS.INT and (lever.dim(k).lo, lever.dim(k).hi) == (r.lo, r.hi)
    assert lever.dim("S3").kind == SS.REAL and (lever.dim("S3").lo, lever.dim("S3").hi) == (LS.bounds("S3").lo,
                                                                                         LS.bounds("S3").hi)
    sess = SS.session_slots()                                           # offsets from each date's session start
    assert set(sess) == {"evening", "asia", "london", "ny"}            # T2b undeclared: NY is one session
    assert all(v[0] == 0 for v in sess.values())
    every = C.session_bounds()                                          # the bounds holding on every search-year day
    for name, (lo, hi, step) in sess.items():
        a, b = every["ny_am" if name == "ny" else name]
        assert (b - a - 1) // step * step == hi or (name == "ny" and hi == (every["_last_entry"][1] - a) // 5 * 5)
    assert lever.days == SS.search_days() and len(lever.days) == len(LS.trading_dates(DC.SEARCH_START,
                                                                                      DC.SEARCH_END))
    if not T.overnight_allowed():
        assert lever.dim("london.0.on").values == (SS.OFF,) and lever.refused["london.0"] == "OvernightRefused"
    with pytest.raises(SS.SpaceRefused):
        SS.from_lever_space(slots={"ny_am": 1})                       # T2b is to declare
    split = SS.session_slots(ny_boundary=1080)
    assert 930 + split["ny_am"][1] < 1080 and SS.session_spans(DAYS[0], ny_boundary=1080)["ny_pm"][0] == 1080


def test_the_sampler_respects_every_constraint_on_the_lever_space(lever):
    led = SS.CellLedger()
    ds = SS.Sampler(lever, seed=SEED, method="sobol").survey(128, ledger=led)
    assert len(ds) == 128
    assert lever_problems(lever, ds) == []
    assert all(lever.check(d) is None for d in ds)
    c = led.counts()
    assert c["proposed"] == 128 and c["refused"] > 0 and c["cells"] == c["proposed"] + c["refused"]
    assert c["by_class"].get("rule", 0) > 0                              # Back2Funded under the No Activation Fee path
    assert c["by_class"].get("collision", 0) > 0 and c["by_class"].get("session", 0) > 0
    for r in led.rows:
        if r["class"] == "rule":
            assert r["design"]["A4"] == "naf" and r["design"]["A12"] > 0
    assert replay_problems(lever, led, SEED, "sobol", ds) == []


@pytest.fixture(scope="module")
def anchored(monkeypatch_module):
    """The space with its overnight slots open (the guard patched, a construction check only: no overnight source
    runs here), so the sessions whose starts move with the dates -- asia, london -- are sampled."""
    monkeypatch_module.setattr(SS, "_overnight_allowed", lambda: True)
    sp = SS.from_lever_space(slots={"evening": 1, "asia": 1, "london": 2, "ny": 2})
    object.__setattr__(sp, "_test_overnight", True)
    return sp


@pytest.fixture(scope="module")
def monkeypatch_module():
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()


def test_window_levers_are_read_per_date_and_never_leave_their_session(anchored):
    """The lead's addition (E-231 (3), Q-166): a winter day, a summer day and both mismatch weeks; then the first
    date of every distinct set of session windows in the search years, so every date's pattern is read."""
    ds = SS.Sampler(anchored, seed=SEED, method="sobol").survey(96, ledger=SS.CellLedger())
    assert lever_problems(anchored, ds) == []
    every = [date.fromisoformat(x["first"]) for x in LS.session_window_range(DC.SEARCH_START,
                                                                             DC.SEARCH_END)["distinct"]]
    assert len(every) > 1 and day_problems(anchored, ds, every) == []
    asia = [d for d in ds if d["asia.0.on"] == SS.ON]
    assert asia
    for d in asia:                                     # the same offsets, read at the date's own start
        w = {x[0]: x for x in anchored.windows_on(d, DAYS[0])}["asia.0"]
        s = {x[0]: x for x in anchored.windows_on(d, DAYS[1])}["asia.0"]
        a0, a1 = (LS.session_windows(x)["asia"][0] for x in DAYS[:2])
        assert s[2] - w[2] == a1 - a0 != 0 and d["asia.0.first"] == w[2] - a0
    lon = [d for d in ds if d["london.0.on"] == SS.ON]
    assert lon and all({x[0]: x for x in anchored.windows_on(d, DAYS[2])}["london.0"][2]
                       == LS.session_windows(DAYS[2])["london"][0] + d["london.0.first"] for d in lon)


def test_mutation_bounds_from_one_date_only_is_caught(monkeypatch):
    """The offsets bounded on a winter day only (asia then runs to 475 minutes from 18:00 CT): read on a summer day,
    asia starts at 19:00 CT and such a window leaves its session."""
    monkeypatch.setattr(SS, "_overnight_allowed", lambda: True)
    sp = SS.from_lever_space(slots={"asia": 1, "ny": 1}, days=(DAYS[0],))
    object.__setattr__(sp, "_test_overnight", True)
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(64, ledger=SS.CellLedger())
    assert day_problems(sp, ds, (DAYS[0],)) == []
    assert any("leaves asia" in p for p in day_problems(sp, ds, (DAYS[1],)))


def test_latency_cells_are_the_loaders_and_every_one_is_counted(lever):
    led = SS.CellLedger()
    SS.Sampler(lever, seed=SEED, method="lhs").survey(96, ledger=led)
    recount = Counter()
    for r in led.rows:
        d = r["design"]
        for s in lever.slots:
            if d[SS.slot_dim(s.name, "on")] == SS.ON:
                recount[str(d[SS.slot_dim(s.name, "T4")])] += 1
    assert dict(recount) == led.counts()["latency"]
    assert set(recount) == {"5", "3", "2", "None"}
    for r in led.rows:
        d = r["design"]
        for s in lever.slots:
            if d[SS.slot_dim(s.name, "on")] == SS.ON and r["class"] != "invalid":
                assert d[SS.slot_dim(s.name, "T4")] in LS.latency_cells(d[SS.slot_dim(s.name, "T1")])


# ------------------------------------------------------------------------------------------------ synthetic spaces


@pytest.mark.parametrize("method", SS.METHODS)
def test_every_cell_is_counted_refused_ones_included(method):
    sp = TY.slot_space()
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method=method).survey(48, ledger=led)
    assert constraint_problems(sp, ds) == []
    assert replay_problems(sp, led, SEED, method, ds) == []
    c = led.counts()
    assert c["by_class"]["tier1"] > 0 and c["by_class"]["collision"] > 0
    assert c["by_role"] == {"survey": c["cells"]}
    assert {r["seed"] for r in led.rows} == {SEED}
    v = led.variant_rows("F-XX")
    assert len(v) == c["cells"] and sum(":refused" in x["label"] for x in v) == c["refused"]


def test_conduct_tier_one_is_refused_at_sampling():
    sp = TY.slot_space()
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(32, ledger=led)
    assert all(d["routing"] != "copy_trade_across_accounts" for d in ds)
    drew = [r for r in led.rows if r["design"]["routing"] == "copy_trade_across_accounts"]
    assert drew and all(r["status"] == "refused" and r["class"] == "tier1" for r in drew)
    good = ds[0]
    assert sp.check(dict(good, firms=2))[0] == "tier1"                  # one firm a design
    assert sp.check(dict(good, overlap="allowed"))[0] == "tier1"        # m-2: overlap refused
    with pytest.raises(SS.SpaceRefused):
        SS.Space(sp.dims, slots=sp.slots, fixed={"overlap": "allowed"})


def test_the_sampler_is_reproducible_from_its_seed_and_needs_one():
    sp = TY.slot_space()
    for method in SS.METHODS:
        a, b, c = SS.CellLedger(), SS.CellLedger(), SS.CellLedger()
        da = SS.Sampler(sp, seed=SEED, method=method).survey(24, ledger=a)
        db = SS.Sampler(sp, seed=SEED, method=method).survey(24, ledger=b)
        dc = SS.Sampler(sp, seed=SEED + 1, method=method).survey(24, ledger=c)
        assert da == db and a.rows == b.rows
        assert da != dc
    for bad in (None, 1.5, "7", True):
        with pytest.raises(SS.SpaceRefused):
            SS.Sampler(sp, seed=bad, method="sobol")
    with pytest.raises(SS.SpaceRefused):
        SS.Sampler(sp, seed=SEED, method="random")


def test_the_survey_is_space_filling():
    sp = TY.toy_space()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for method in SS.METHODS:
            u = SS.UnitPoints(method, sp.d, SS.child_rng(SEED, SS.STREAM_SURVEY, 0)).next(64)[:64]
            assert len(u) == 64
            for j in range(sp.d):                                        # one point in each 1/64 stratum
                assert sorted(np.floor(u[:, j] * 64).astype(int).tolist()) == list(range(64))
            cats = Counter(sp.decode(x)["c"] for x in u)
            assert max(cats.values()) - min(cats.values()) <= 1          # the categorical stratified
            iid = SS.child_rng(SEED, 99).random((64, sp.d))
            assert qmc.discrepancy(u) < qmc.discrepancy(iid)


def test_cross_enumerates_every_combination():
    sp = TY.toy_space()
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(5, ledger=led, cross=("c",))
    assert Counter(d["c"] for d in ds) == {"a": 5, "b": 5, "c": 5}
    with pytest.raises(SS.SpaceRefused):
        SS.Sampler(TY.slot_space(), seed=SEED, method="sobol").survey(2, ledger=led, cross=("s1.0.T4",))


def test_unit_of_decodes_back_to_the_design():
    for sp in (TY.toy_space(), TY.slot_space()):
        led = SS.CellLedger()
        for d in SS.Sampler(sp, seed=SEED, method="sobol").survey(16, ledger=led):
            back = sp.decode(sp.unit_of(d))
            for k, v in d.items():
                assert back[k] == pytest.approx(v) if isinstance(v, float) else back[k] == v


# ------------------------------------------------------------------------------------------------ the door


def test_the_door_refuses_anything_held_out():
    d = SS.Sampler(TY.toy_space(), seed=SEED, method="sobol").survey(1, ledger=SS.CellLedger())[0]
    assert SS.admit([TY.reading(d, 1.0)])
    for tag in ("held_out", "heldout", "HELD-OUT", "judged", "holdout", "confirmation", "", "other"):
        with pytest.raises(SS.HeldOutInput):
            SS.admit([TY.reading(d, 1.0), TY.reading(d, 1.0, tag=tag)])
    for blocks in ((("2023-06-01", "2024-01-05"),), (("2024-01-02", "2024-12-31"),), (("2023-12-30", "2023-12-31"),),
                   (("2026-07-17", "2026-08-01"),), (("2019-12-01", "2020-03-01"),), ()):
        with pytest.raises(SS.HeldOutInput):
            SS.admit_one(TY.reading(d, 1.0, blocks=blocks))
    for bad in (TY.reading(d, float("nan")), TY.reading(d, 1.0, seeds=()), TY.reading(d, 1.0, seeds=(1.5,)),
                TY.reading(d, 1.0, se=-1.0), {"design": d, "value": 1.0}):
        with pytest.raises(SS.HeldOutInput):
            SS.admit_one(bad)


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_collision_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(SS.Space, "_collision", lambda self, design: None)
    sp = TY.slot_space()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(48, ledger=SS.CellLedger())
    assert any(p.startswith("collision") for p in constraint_problems(sp, ds))


def test_mutation_refused_cells_unrecorded_is_caught(monkeypatch):
    real = SS.CellLedger.record

    def skip_refused(self, space, design, *, role, seed, refusal, round_index=None):
        if refusal is None:
            return real(self, space, design, role=role, seed=seed, refusal=refusal, round_index=round_index)
        return None

    monkeypatch.setattr(SS.CellLedger, "record", skip_refused)
    sp = TY.slot_space()
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(24, ledger=led)
    assert replay_problems(sp, led, SEED, "sobol", ds) != []


def test_mutation_tier_one_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(SS.Space, "_tier_one", lambda self, design: None)
    sp = TY.slot_space()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(32, ledger=SS.CellLedger())
    assert any(p.startswith("tier-1") for p in constraint_problems(sp, ds))


def test_mutation_seed_ignored_is_caught(monkeypatch):
    monkeypatch.setattr(SS, "child_rng", lambda seed, *key: np.random.default_rng())
    sp = TY.slot_space()
    da = SS.Sampler(sp, seed=SEED, method="sobol").survey(8, ledger=SS.CellLedger())
    db = SS.Sampler(sp, seed=SEED, method="sobol").survey(8, ledger=SS.CellLedger())
    assert da != db                                                     # the reproducibility test would fail


def test_mutation_door_left_open_is_caught(monkeypatch):
    monkeypatch.setattr(SS, "admit_one", lambda r: r)
    d = SS.Sampler(TY.toy_space(), seed=SEED, method="sobol").survey(1, ledger=SS.CellLedger())[0]
    with pytest.raises(pytest.fail.Exception):
        with pytest.raises(SS.HeldOutInput):
            SS.admit([TY.reading(d, 1.0, tag="held_out")])
