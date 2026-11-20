"""Wave 3.4: the lever-space sampler, the cell ledger and the readings door (`extended/search_space.py`), on synthetic
spaces and on the Topstep $50K lever space as `extended/lever_space.py` loads it (rules and configuration only; no bar).

What is asserted: every returned design passes every constraint, each checked here independently of the module
(windows on the mark grid, inside their sessions and never colliding; the loader's combination rules; latency cells as
`lever_space.latency_cells` gives them; conduct tier 1 never returned); **every cell proposed is in the ledger**, the
refused ones included, shown by replaying the sampler's unit points by hand; the sampler is reproducible from its seed
and space-filling (stratified marginals, lower discrepancy than independent draws); a role is begun once, under one
seed; **the door** (ledger and protocol, the red team's B-1) refuses anything tagged held-out (naming the held-out
years), touching the held-out years in a block or an outcome session (m-3), off the declared protocol, not exactly a
frozen `Reading` (m-4), or of a design that is not a counted cell; tier 1 matches case-insensitively and refuses
`firms=True` (m-5); NY windows whose first mark is inside the closed 08:30-08:59 window are refused and counted (n-3);
`to_components` gives `components.Design(day=...)` on each date pattern (m-11). **Mutations** (each a planted defect
a test here must catch): the collision check removed, refused cells left unrecorded, the tier-1 check removed, the seed
ignored, the door left open, the ledger check dropped, the held-out word check dropped, offsets bounded on one date.
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
    else:                                                               # H2's row (E-231): overnight admitted
        assert lever.dim("london.0.on").values == (SS.OFF, SS.ON) and "london.0" not in lever.refused
    with pytest.raises(SS.SpaceRefused):
        SS.from_lever_space(slots={"ny_am": 1})                       # T2b is to declare
    split = SS.session_slots(ny_boundary=1080)
    assert 930 + split["ny_am"][1] < 1080 and SS.session_spans(DAYS[0], ny_boundary=1080)["ny_pm"][0] == 1080


def test_a_computed_s1_becomes_a_per_slot_lever(monkeypatch):
    """Q-171 on master: once S1's search-year reading loads, each slot takes its own session's range of k (`ny` reads
    `ny_am`'s, the whole NY session); while it does not, S1 is carried as refused."""
    assert "S1" in SS.from_lever_space(slots={"ny": 1}).refused or "ny.0.S1" in SS.from_lever_space(
        slots={"ny": 1}).names()
    real = LS.space()
    fake = dict(real, S1=LS.Range("S1", "interval", lo=0.5, hi=3.0, step=None))
    monkeypatch.setattr(LS, "space", lambda: fake)
    monkeypatch.setattr(LS, "stop_width", lambda s: LS.Range("S1", "interval", lo={"london": 0.4}.get(s, 0.6),
                                                             hi={"london": 2.0}.get(s, 2.5), step=None))
    sp = SS.from_lever_space(slots={"london": 1, "ny": 1})
    assert (sp.dim("ny.0.S1").lo, sp.dim("ny.0.S1").hi) == (0.6, 2.5)
    assert (sp.dim("london.0.S1").lo, sp.dim("london.0.S1").hi) == (0.4, 2.0)
    d = SS.Sampler(sp, seed=SEED, method="sobol").survey(4, ledger=SS.CellLedger(), **TY.SV)
    assert all(x["ny.0.S1"] is None or 0.6 <= x["ny.0.S1"] <= 2.5 for x in d)


def test_the_sampler_respects_every_constraint_on_the_lever_space(lever):
    led = SS.CellLedger()
    ds = SS.Sampler(lever, seed=SEED, method="sobol").survey(128, ledger=led, **TY.SV)
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
    ds = SS.Sampler(anchored, seed=SEED, method="sobol").survey(96, ledger=SS.CellLedger(), **TY.SV)
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
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(64, ledger=SS.CellLedger(), **TY.SV)
    assert day_problems(sp, ds, (DAYS[0],)) == []
    assert any("leaves asia" in p for p in day_problems(sp, ds, (DAYS[1],)))


def test_latency_cells_are_the_loaders_and_every_one_is_counted(lever):
    led = SS.CellLedger()
    SS.Sampler(lever, seed=SEED, method="lhs").survey(96, ledger=led, **TY.SV)
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
    ds = SS.Sampler(sp, seed=SEED, method=method).survey(48, ledger=led, **TY.SV)
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
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(32, ledger=led, **TY.SV)
    assert all(d["routing"] != "copy_trade_across_accounts" for d in ds)
    drew = [r for r in led.rows if r["design"]["routing"] == "copy_trade_across_accounts"]
    assert drew and all(r["status"] == "refused" and r["class"] == "tier1" for r in drew)
    good = ds[0]
    for bad in (dict(good, firms=2), dict(good, firms=True), dict(good, firms=1.0), dict(good, overlap="allowed"),
                dict(good, routing="Copy_Trade_Across_Accounts"), dict(good, routing="COPY_TRADE_ACROSS_ACCOUNTS")):
        assert sp.check(bad)[0] == "tier1", bad                          # m-5: one firm, the integer; names casefolded
    with pytest.raises(SS.SpaceRefused):
        SS.Space(sp.dims, slots=sp.slots, fixed={"overlap": "allowed"})
    mixed = TY.slot_space(routing=("longest_wait", "Copy_Trade_Across_Accounts"))
    got = SS.Sampler(mixed, seed=SEED, method="sobol").survey(16, ledger=SS.CellLedger(), **TY.SV)
    assert all(d["routing"] == "longest_wait" for d in got)


def test_conduct_tier_one_on_the_real_lever_space(lever):
    """The real space offers no tier-1 value (m-5): tier 1 there is the fixed overlap and firm values, refused here,
    and a tier-1 name injected into a real design."""
    d = SS.Sampler(lever, seed=SEED, method="sobol").survey(4, ledger=SS.CellLedger(), **TY.SV)[0]
    assert lever.fixed["overlap"] == "refused" and lever.fixed["firms"] == 1
    for bad in (dict(d, overlap="allowed"), dict(d, firms=2), dict(d, firms=True),
                dict(d, A10="Max_Size_Into_Major_News"), dict(d, A3="hedge_across_firms")):
        assert lever.check(bad)[0] == "tier1", bad
    assert not any(isinstance(v, str) and v.casefold() in {t.casefold() for t in SS.TIER_ONE}
                   for dim in lever.dims for v in dim.every_value())


def test_the_sampler_is_reproducible_from_its_seed_and_needs_one():
    sp = TY.slot_space()
    for method in SS.METHODS:
        a, b, c = SS.CellLedger(), SS.CellLedger(), SS.CellLedger()
        da = SS.Sampler(sp, seed=SEED, method=method).survey(24, ledger=a, **TY.SV)
        db = SS.Sampler(sp, seed=SEED, method=method).survey(24, ledger=b, **TY.SV)
        dc = SS.Sampler(sp, seed=SEED + 1, method=method).survey(24, ledger=c, **TY.SV)
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
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(5, ledger=led, cross=("c",), **TY.SV)
    assert Counter(d["c"] for d in ds) == {"a": 5, "b": 5, "c": 5}
    with pytest.raises(SS.SpaceRefused):
        SS.Sampler(TY.slot_space(), seed=SEED, method="sobol").survey(2, ledger=led, cross=("s1.0.T4",), **TY.SV)


def test_unit_of_decodes_back_to_the_design():
    for sp in (TY.toy_space(), TY.slot_space()):
        led = SS.CellLedger()
        for d in SS.Sampler(sp, seed=SEED, method="sobol").survey(16, ledger=led, **TY.SV):
            back = sp.decode(sp.unit_of(d))
            for k, v in d.items():
                assert back[k] == pytest.approx(v) if isinstance(v, float) else back[k] == v


# ------------------------------------------------------------------------------------------------ the door


def one_counted(space=None):
    led = SS.CellLedger()
    d = SS.Sampler(space or TY.toy_space(), seed=SEED, method="sobol").survey(1, ledger=led, **TY.SV)[0]
    return d, led


def test_the_door_refuses_anything_held_out():
    d, led = one_counted()
    kw = dict(ledger=led)
    assert SS.admit([TY.reading(d, 1.0)], **kw)
    for tag in ("held_out", "heldout", "HELD-OUT", "judged", "holdout", "confirmation"):
        with pytest.raises(SS.HeldOutInput, match="is held-out"):          # survivor 6: the refusal names it
            SS.admit([TY.reading(d, 1.0), TY.reading(d, 1.0, tag=tag)], **kw)
    for tag in ("", "other"):
        with pytest.raises(SS.HeldOutInput, match="only 'search'"):
            SS.admit_one(TY.reading(d, 1.0, tag=tag), **kw)
    for blocks in ((("2023-06-01", "2024-01-05"),), (("2024-01-02", "2024-12-31"),), (("2023-12-30", "2023-12-31"),),
                   (("2026-07-17", "2026-08-01"),), (("2019-12-01", "2020-03-01"),), ()):
        with pytest.raises(SS.HeldOutInput):
            SS.admit_one(TY.reading(d, 1.0, blocks=blocks), **kw)
    for h in (1, 5, 400):                       # m-3, rn-3: sessions after 2023-12-29, derived from the horizon
        with pytest.raises(SS.HeldOutInput, match="read through"):
            SS.admit_one(TY.reading(d, 1.0, horizon=h), **kw)
    for bad in (TY.reading(d, float("nan")), TY.reading(d, 1.0, seeds=()), TY.reading(d, 1.0, seeds=(1.5,)),
                TY.reading(d, 1.0, se=-1.0), TY.reading(d, 1.0, per_seed=[1.0]), {"design": d, "value": 1.0}):
        with pytest.raises(SS.HeldOutInput):
            SS.admit_one(bad, **kw)


def test_the_door_is_bound_to_the_ledger_and_the_protocol():
    """The red team's B-1: (1) a design never drawn; (2) a reading on a month and other seeds; (3) a design of another
    role; (4) every protocol field."""
    d, led = one_counted()
    kw = dict(ledger=led)
    with pytest.raises(SS.Uncounted):
        SS.admit_one(TY.reading(TY.SMOOTH_ARGMIN, 0.0), **kw)
    month = SS.Protocol("composite", (("2021-03-01", "2021-03-31"),), (5, 6), 0)
    with pytest.raises(SS.OffProtocol):
        SS.admit_one(TY.reading(d, 0.0, protocol=month), **kw)
    for over in (dict(measure="ruin"), dict(blocks=TY.OTHER_BLOCKS), dict(seeds=(1, 2, 3)), dict(horizon=True)):
        with pytest.raises(SS.OffProtocol):
            SS.admit_one(TY.reading(d, 0.0, **over), **kw)
    with pytest.raises(SS.Uncounted):
        SS.admit_one(TY.reading(d, 0.0), ledger=led, roles=lambda r: r == "round-1")
    with pytest.raises(SS.ReadingRefused):
        SS.admit_one(TY.reading(d, 0.0), ledger=None)
    led2 = SS.CellLedger()
    SS.Sampler(TY.slot_space(), seed=SEED, method="sobol").survey(8, ledger=led2, **TY.SV)
    rfz = [r["design"] for r in led2.rows if r["status"] == "refused"]
    assert rfz
    with pytest.raises(SS.Uncounted):                                      # a refused cell is no reading's design
        SS.admit_one(TY.reading(rfz[0], 0.0), ledger=led2)


def test_a_protocol_is_validated_and_pins_the_library_versions():
    for bad in (dict(measure=""), dict(blocks=(("2024-01-02", "2024-03-01"),)), dict(seeds=(1, 1)),
                dict(seeds=(1.5,)), dict(horizon=-1), dict(horizon=1.0), dict(libs=(("numpy", "0.0"),)),
                dict(horizon=1)):                                         # its outcomes would read 2024
        f = dict(measure="composite", blocks=TY.BLOCKS, seeds=TY.SEEDS, horizon=0)
        f.update(bad)
        with pytest.raises(SS.ReadingRefused):
            SS.Protocol(**f)
    assert TY.PROTOCOL.libs == SS.LIBS and dict(SS.LIBS)["numpy"] == np.__version__
    d, led = one_counted()
    other_libs = SS.Reading(d, 0.0, TY.BLOCKS, TY.SEEDS, "search", "composite", 0,
                            libs=(("numpy", "0.0"), ("scipy", "0.0")))
    with pytest.raises(SS.OffProtocol):
        SS.admit_one(other_libs, ledger=led)
    assert all(r["libs"] == dict(SS.LIBS) for r in led.rows)
    assert all(v["params"]["_libs"] == dict(SS.LIBS) for v in led.variant_rows("F-XX"))


def test_a_reading_is_frozen_and_of_the_exact_type():
    d, led = one_counted()
    r = TY.reading(d, 1.0)
    d["x1"] = 0.123456                                                    # the caller's dict changes; the reading not
    assert r.design["x1"] != 0.123456
    with pytest.raises(TypeError):
        r.design["x1"] = 0.5                                             # m-4: a read-only mapping
    assert isinstance(r.blocks, tuple) and isinstance(r.seeds, tuple)

    class Sneaky(SS.Reading):
        @property
        def tag(self):                                                    # noqa: D401
            return "search"

    s = Sneaky.__new__(Sneaky)
    object.__setattr__(s, "__dict__", dict(r.__dict__))
    with pytest.raises(SS.HeldOutInput, match="exactly"):
        SS.admit_one(s, ledger=led)


def test_reads_through_is_derived_from_the_blocks_and_the_horizon():
    """rn-3: the last session read is the last block's end advanced by the horizon on Q-40's session calendar (a
    full closure is no session); the caller never reports it."""
    assert SS.session_after(date(2023, 12, 22), 4) == date(2023, 12, 29)      # 25 December closed
    assert SS.session_after(date(2023, 12, 22), 5) == date(2024, 1, 2)        # 1 January closed: it crosses
    assert SS.session_after(date(2023, 12, 23), 0) == date(2023, 12, 22)      # a Saturday: the session before
    assert SS.session_after(date(2021, 1, 15), 1) == date(2021, 1, 18)        # a Monday with an early close counts
    early = SS.Protocol("composite", (("2020-01-02", "2023-12-15"),), (1, 2), 5)
    d, led = one_counted()
    r = TY.reading(d, 0.0, protocol=early)
    assert r.reads_through == date(2023, 12, 22)
    assert not hasattr(SS.Reading, "__dataclass_fields__") or "reads_through" not in SS.Reading.__dataclass_fields__
    with pytest.raises(SS.HeldOutInput):
        SS.Protocol("composite", (("2020-01-02", "2023-12-22"),), (1, 2), 5)


def test_the_survey_declares_the_protocol_and_the_ledger_holds_it_read_only():
    """RB-2 and rn-4: the survey (only) declares the protocol, the re-read seeds and the limit measures; the door
    reads them from the ledger; the ledger's roles, rows and protocol are read-only."""
    sp = TY.toy_space()
    for bad in (dict(), dict(protocol=TY.PROTOCOL), dict(reread_seeds=TY.REREAD_SEEDS),
                dict(protocol=TY.PROTOCOL, reread_seeds=TY.SEEDS[:2]),
                dict(protocol=TY.PROTOCOL, reread_seeds=TY.REREAD_SEEDS, measures=("composite",))):
        with pytest.raises((SS.LedgerRefused, TypeError)):
            SS.Sampler(sp, seed=SEED, method="sobol").survey(2, ledger=SS.CellLedger(), **bad)
    led = SS.CellLedger()
    with pytest.raises(SS.LedgerRefused):
        led.protocol                                                       # nothing declared yet
    SS.Sampler(sp, seed=SEED, method="sobol").survey(4, ledger=led, **TY.sv(measures=("reach",)))
    assert led.protocol == TY.PROTOCOL and led.reread == TY.REREAD and led.measures == ("reach",)
    assert led.protocol_for("reach") == TY.PROTOCOL.with_measure("reach")
    with pytest.raises(SS.OffProtocol):
        led.protocol_for("ruin")
    with pytest.raises(SS.OffProtocol):
        led.protocol_for("reach", reread=True)
    with pytest.raises(SS.LedgerRefused):
        led.begin("round-1", 5, protocol=TY.PROTOCOL.with_seeds((7, 8)))  # only the survey declares
    with pytest.raises(TypeError):
        led.roles["round-1"] = {"seed": 1, "meta": {}}
    with pytest.raises(AttributeError):
        led.roles.pop("survey")
    with pytest.raises(TypeError):
        led.roles["survey"]["seed"] = 2
    with pytest.raises(AttributeError):
        led.protocol = TY.PROTOCOL.with_seeds((7, 8))
    with pytest.raises((TypeError, AttributeError)):
        led.rows.append({})
    with pytest.raises(TypeError):
        led.rows[0]["status"] = "refused"
    assert led.counts()["cells"] == 4


def test_a_role_is_begun_once_under_one_seed():
    sp = TY.toy_space()
    led = SS.CellLedger()
    SS.Sampler(sp, seed=SEED, method="sobol").survey(4, ledger=led, **TY.SV)
    with pytest.raises(SS.LedgerRefused):
        SS.Sampler(sp, seed=SEED, method="sobol").survey(4, ledger=led, **TY.SV)                  # a second survey
    with pytest.raises(SS.LedgerRefused):
        led.record(sp, led.rows[0]["design"], role="survey", seed=SEED + 1, refusal=None)  # off its seed
    with pytest.raises(SS.LedgerRefused):
        led.record(sp, led.rows[0]["design"], role="round-9", seed=SEED, refusal=None)     # never begun
    with pytest.raises(SS.LedgerRefused):
        led.begin("round-2", SEED)                                                           # out of order
    led.begin("round-1", 5)
    with pytest.raises(SS.LedgerRefused):
        led.begin("round-1", 6)


def test_ny_windows_inside_the_closed_window_are_refused_and_counted(lever):
    led = SS.CellLedger()
    ds = SS.Sampler(lever, seed=SEED, method="sobol").survey(64, ledger=led, **TY.SV)
    for d in ds:
        for s in lever.slots:
            if s.session == "ny" and d[SS.slot_dim(s.name, "on")] == SS.ON:
                assert d[SS.slot_dim(s.name, "first")] >= 30                       # 09:00 CT and after
    closed = [r for r in led.rows if "closed window" in r["reason"]]
    assert closed and all(r["class"] == "session" for r in closed)
    assert all(any(r["design"][f"ny.{i}.on"] == SS.ON and r["design"][f"ny.{i}.first"] < 30 for i in (0, 1))
               for r in closed)


def test_to_components_gives_the_schedulers_design_on_each_date_pattern(anchored):
    from extended import components as C

    ds = [d for d in SS.Sampler(anchored, seed=SEED, method="sobol").survey(48, ledger=SS.CellLedger(), **TY.SV)
          if d["asia.0.on"] == SS.ON]
    assert ds

    def build(slot, levers):
        return T.P14Breakout(latency=5, entry=T.MARKET), 40

    patterns = [date.fromisoformat(x["first"]) for x in LS.session_window_range(DC.SEARCH_START,
                                                                                DC.SEARCH_END)["distinct"]]
    assert len(patterns) == 3
    for d in ds[:6]:
        for day in patterns:
            cd = SS.to_components(anchored, d, day, firm="topstep", build=build)
            assert isinstance(cd, C.Design) and cd.day == day
            want = {(w[0], w[2], w[3]) for w in anchored.windows_on(d, day)}
            assert {(c.name, c.first, c.last) for c in cd.components} == want
            assert {c.session for c in cd.components} <= {"evening", "asia", "london", "ny_am"}
    early = [d for d in ds if d["asia.0.first"] < 60]                        # inside asia only from its own start
    if early:
        with pytest.raises(C.DesignRefused):
            C.Design("topstep", SS.to_components(anchored, early[0], DAYS[0], firm="topstep",
                                                 build=build).components)    # day=None: the every-day bounds


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_collision_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(SS.Space, "_collision", lambda self, design: None)
    sp = TY.slot_space()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(48, ledger=SS.CellLedger(), **TY.SV)
    assert any(p.startswith("collision") for p in constraint_problems(sp, ds))


def test_mutation_refused_cells_unrecorded_is_caught(monkeypatch):
    real = SS.CellLedger.record

    def skip_refused(self, space, design, *, role, seed, refusal, round_index=None, pen=None):
        if refusal is None:
            return real(self, space, design, role=role, seed=seed, refusal=refusal, round_index=round_index, pen=pen)
        return None

    monkeypatch.setattr(SS.CellLedger, "record", skip_refused)
    sp = TY.slot_space()
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(24, ledger=led, **TY.SV)
    assert replay_problems(sp, led, SEED, "sobol", ds) != []


def test_mutation_tier_one_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(SS.Space, "_tier_one", lambda self, design: None)
    sp = TY.slot_space()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(32, ledger=SS.CellLedger(), **TY.SV)
    assert any(p.startswith("tier-1") for p in constraint_problems(sp, ds))


def test_mutation_seed_ignored_is_caught(monkeypatch):
    monkeypatch.setattr(SS, "child_rng", lambda seed, *key: np.random.default_rng())
    sp = TY.slot_space()
    da = SS.Sampler(sp, seed=SEED, method="sobol").survey(8, ledger=SS.CellLedger(), **TY.SV)
    db = SS.Sampler(sp, seed=SEED, method="sobol").survey(8, ledger=SS.CellLedger(), **TY.SV)
    assert da != db                                                     # the reproducibility test would fail


def test_mutation_door_left_open_is_caught(monkeypatch):
    d, led = one_counted()
    monkeypatch.setattr(SS, "admit_one", lambda r, **kw: r)
    got = SS.admit([TY.reading(d, 1.0, tag="held_out")], ledger=led)
    assert len(got) == 1 and got[0].tag == "held_out"                      # the door test would fail


def test_mutation_ledger_check_dropped_is_caught(monkeypatch):
    """B-1's mutation: the ledger's ids ignored -- the never-drawn design is admitted."""
    d, led = one_counted()
    monkeypatch.setattr(SS.CellLedger, "proposed_ids", lambda self, roles: frozenset([TY.reading(
        TY.SMOOTH_ARGMIN, 0.0).id, SS.design_id(d)]))
    assert SS.admit_one(TY.reading(TY.SMOOTH_ARGMIN, 0.0), ledger=led)


def test_mutation_held_out_word_check_dropped_is_caught(monkeypatch):
    """Survivor 6 (n-1): without the word check a held-out tag is refused only as 'not search', and the refusal no
    longer names the held-out years -- the door test's message check fails."""
    d, led = one_counted()
    real = SS.admit_one

    def no_words(r, **kw):
        if type(r) is SS.Reading and r.tag != SS.SEARCH_TAG:
            raise SS.HeldOutInput(f"REFUSED: a reading tagged {r.tag!r}; only 'search' is admitted")
        return real(r, **kw)

    monkeypatch.setattr(SS, "admit_one", no_words)
    with pytest.raises(SS.HeldOutInput) as e:
        SS.admit([TY.reading(d, 1.0, tag="held_out")], ledger=led)
    assert "is held-out" not in str(e.value)
