"""Q-192: the search engine's minor findings from the red team's final read of Wave 3.4
(`docs/reviews/BUILD_W34_v3_2026-11-20.md`), each under the lead's ruling. Synthetic objectives only: no bar, atlas or
result file is read.

What is asserted:
- **rb2-a**: the protocol's sha256 covers every declared field; the survey's `begin` refuses a protocol whose sha256
  is not the declaration's (`DeclarationMismatch`), a missing one included; a second ledger opened on a weaker protocol
  is refused at its declaration, and when the runner forges the hash of its own weaker protocol, the verdict and the
  variant rows carry that protocol and its sha256, so it is visible beside the declared one;
- **rm3-a**: the size bound under any dependence, k x P(t_{n-1} > c), is recorded beside `size_at`, with the read's
  figures (n = 16, k = 10: c about 2.80, the bound about 0.068);
- **rm3-b**: the re-read seeds have a floor of five, refused below it by name (`TooFewRereadSeeds`); a tolerance with
  no root in the bracket is refused by name (`PlateauRefused`), never a bare ValueError (the quadrature's own test at
  n = 3 and n = 5 with k = 30 is `tests/test_plateau.py`'s);
- **n-1**: a row's design, latencies and library versions and a role's meta are frozen, so an edit after recording
  raises, and the ledger still deep-copies;
- **n-2**: a role closes when its batch returns (the survey, a round, a plateau check), a cell recorded after it is
  refused (`RoleClosed`), and only the drawer that opened the role records into it (`NotTheDrawer`), the caller's
  runner inside a plateau check included;
- **n-3**: a round's `RoundSpec` and limits are its role's meta;
- **F-3** (BUILD_SURVEY_v2, the lead's ruling): a declared limit is read on the fresh re-read seeds, and the
  plateau's verdict exposes the finalist's re-read limits; a finalist lucky on its selection seeds reads outside there.
- **Q-192b** (BUILD_SURVEY_c2 M-1): `protocol_for(limit, reread=True)` is the ledger's re-read under the limit's
  measure for exactly the declared limits; an undeclared measure, stale re-read seeds and a caller's seeds are refused;
  the protocol's sha256, limits included, is what the verdict and the variant rows carry.
Each guard's mutant is run on a scratch copy of the module (the hand-back lists them); every one fails a test here.
"""
from __future__ import annotations

import copy
import dataclasses
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import plateau as PL  # noqa: E402
from extended import proposer as P  # noqa: E402
from extended import search_space as SS  # noqa: E402

SEED, LSEED, ROUND_SEED = 4242, 9, 5151
STEPS = {"x1": 0.05, "x2": 0.05, "x3": 0.05, "n": 1, "c": PL.CELLS}
RULE = PL.PlateauRule(steps=STEPS, radius=1, tolerance_se=3.0, margin=0.0, side="worse", min_share=1.0,
                      min_neighbours=1, min_per_lever=1)
SPEC = P.RoundSpec(batch=2, pool=64, acquisition="ei")
MONTH = SS.Protocol("composite", (("2021-03-01", "2021-03-31"),), (7, 8, 9), 0)    # the read's weaker protocol
WEAK_REREAD = (11, 12, 13, 14, 15)


def survey(n: int = 8, space=None, **declared):
    led = SS.CellLedger()
    ds = SS.Sampler(space or TY.toy_space(), seed=SEED, method="sobol").survey(n, ledger=led,
                                                                             **(declared or TY.SV))
    return ds, led


def flat():
    return TY.evaluator(lambda d: 0.0, 0.2)


# ------------------------------------------------------------------------------------------------ rb2-a


def test_rb2a_the_protocol_sha256_covers_every_declared_field():
    base = SS.protocol_sha256(TY.PROTOCOL, TY.REREAD_SEEDS)
    assert base == TY.SV["declaration_sha256"] and len(base) == 64
    rec = SS.protocol_record(TY.PROTOCOL, TY.REREAD_SEEDS)
    assert set(rec) == {"measure", "blocks", "seeds", "horizon", "libs", "reread_seeds", "measures"}
    early = SS.Protocol("composite", TY.OTHER_BLOCKS, TY.SEEDS, 0)
    others = [SS.protocol_sha256(TY.PROTOCOL.with_measure("ruin"), TY.REREAD_SEEDS),
              SS.protocol_sha256(early, TY.REREAD_SEEDS),
              SS.protocol_sha256(SS.Protocol("composite", TY.OTHER_BLOCKS, TY.SEEDS, 1), TY.REREAD_SEEDS),
              SS.protocol_sha256(TY.PROTOCOL.with_seeds((101, 102)), TY.REREAD_SEEDS),
              SS.protocol_sha256(TY.PROTOCOL, TY.REREAD_SEEDS[:-1]),
              SS.protocol_sha256(TY.PROTOCOL, TY.REREAD_SEEDS, ("reach",))]
    assert len(set(others + [base])) == len(others) + 1                  # every field moves the hash


def test_rb2a_the_survey_refuses_a_protocol_off_its_declaration():
    for sha in (None, "", SS.protocol_sha256(MONTH, WEAK_REREAD), TY.SV["declaration_sha256"].upper()):
        led = SS.CellLedger()
        with pytest.raises(SS.DeclarationMismatch):
            SS.Sampler(TY.toy_space(), seed=SEED, method="sobol").survey(
                4, ledger=led, protocol=TY.PROTOCOL, reread_seeds=TY.REREAD_SEEDS, declaration_sha256=sha)
        assert "survey" not in led.roles and led.counts()["cells"] == 0
    _, led = survey()
    assert led.protocol_sha256 == TY.SV["declaration_sha256"]
    assert SS.thaw(led.declared) == SS.protocol_record(TY.PROTOCOL, TY.REREAD_SEEDS)
    with pytest.raises(SS.LedgerRefused):                                  # only the survey declares
        led.begin("round-1", 1, declaration_sha256=TY.SV["declaration_sha256"])


def test_rb2a_a_second_ledger_on_a_weaker_protocol_is_refused_or_visible_in_its_verdict():
    """The read's probe: ledger B, opened by drawing the same Sobol seed again (the same designs), declares one month
    and other seeds. Under the declaration's sha256 it is refused; under the hash of its own protocol (forged by the
    runner) its verdict and variant rows carry that protocol and sha256, not the declared ones."""
    declared = TY.SV["declaration_sha256"]
    ds_a, a = survey()
    with pytest.raises(SS.DeclarationMismatch):
        survey(protocol=MONTH, reread_seeds=WEAK_REREAD, measures=(), declaration_sha256=declared)
    ds_b, b = survey(**TY.sv(MONTH, WEAK_REREAD))                         # the forged declaration
    assert ds_b == ds_a
    ev = flat()
    va = PL.check(ev(ds_a[0], protocol=TY.PROTOCOL), TY.toy_space(), RULE, ev, ledger=a, ledger_seed=LSEED)
    vb = PL.check(ev(ds_b[0], protocol=MONTH), TY.toy_space(), RULE, ev, ledger=b, ledger_seed=LSEED)
    assert va.protocol_sha256 == declared and va.protocol == SS.protocol_record(TY.PROTOCOL, TY.REREAD_SEEDS)
    assert vb.protocol_sha256 != declared and vb.protocol_sha256 == SS.protocol_sha256(MONTH, WEAK_REREAD)
    assert vb.protocol["blocks"] == [["2021-03-01", "2021-03-31"]] and vb.protocol["seeds"] == [7, 8, 9]
    assert vb.protocol["reread_seeds"] == list(WEAK_REREAD) and vb.protocol["horizon"] == 0
    assert vb.protocol["measure"] == "composite" and vb.reread_seeds == WEAK_REREAD
    for led, v in ((a, va), (b, vb)):
        rows = led.variant_rows("F-XX")
        assert rows and all(r["params"]["_protocol_sha256"] == v.protocol_sha256 for r in rows)
        assert all(r["params"]["_protocol"] == v.protocol for r in rows)


# ------------------------------------------------------------------------------------------------ rm3-a


def test_rm3a_the_dependence_bound_is_recorded_beside_size_at():
    """The read's figures: at n = 16 and k = 10 the tolerance is about 2.80 (2.796 in the read) and the bound under any
    dependence, 10 x P(t_15 > c), about 0.068 against the exact 0.05."""
    c = PL.critical_value(0.05, 10, 16)
    assert c == pytest.approx(2.80, abs=0.01)
    bd = PL.size_bound(c, 10, 16)
    assert bd == pytest.approx(10 * student_t.sf(c, 15), rel=1e-12) and bd == pytest.approx(0.068, abs=0.002)
    assert PL.size_bound(c, 10 ** 6, 16) == 1.0
    ds, led = survey()
    ev = flat()
    r = dataclasses.replace(RULE, tolerance_se=2.5)
    v = PL.check(ev(ds[0], protocol=TY.PROTOCOL), TY.toy_space(), r, ev, ledger=led, ledger_seed=LSEED)
    n = len(TY.REREAD_SEEDS)
    assert v.evaluated > 0
    assert v.size_bound == pytest.approx(PL.size_bound(2.5, v.evaluated, n), rel=1e-12) and v.size_bound >= v.size_at
    assert v.size_at == pytest.approx(1 - PL.p_all_hold(2.5, v.evaluated, n), abs=1e-12)
    assert "exchangeable" in v.size_label and "any dependence" in v.size_label
    assert f"{v.evaluated} x P(t_{n - 1} > 2.5)" in v.size_label
    _, led2 = survey()
    v2 = PL.check(ev(ds[0], protocol=TY.PROTOCOL), TY.toy_space(), dataclasses.replace(RULE, side="two_sided"), ev,
                  ledger=led2, ledger_seed=LSEED)
    assert v2.size_bound != v2.size_bound and v2.size_at != v2.size_at   # no figure off the side 'worse'


# ------------------------------------------------------------------------------------------------ rm3-b


def test_rm3b_the_reread_seeds_have_a_floor_of_five_refused_by_name():
    assert SS.MIN_REREAD_SEEDS == 5
    for k in (2, 3, 4):
        rr = tuple(range(201, 201 + k))
        with pytest.raises(SS.TooFewRereadSeeds, match="the floor is 5"):
            survey(**TY.sv(reread_seeds=rr))
    _, led = survey(**TY.sv(reread_seeds=tuple(range(201, 206))))
    assert led.reread.seeds == tuple(range(201, 206))


def test_rm3b_a_tolerance_out_of_the_bracket_is_refused_by_name():
    with pytest.raises(PL.PlateauRefused, match="no tolerance"):          # at 2 seeds no c up to 60 reaches it
        PL.critical_value(0.05, 30, 2)
    for bad in ((0.05, 10, 1), (0.0, 10, 16), (0.05, 0, 16)):
        with pytest.raises(PL.PlateauRefused):
            PL.critical_value(*bad)


def test_rm3b_the_quadrature_skips_only_negligible_nodes():
    """The delta nodes skipped for speed weigh under 1e-15 in all: they cannot move a probability the tests read."""
    d, w, skipped = PL._gh_nodes()
    assert skipped < 1e-15 and len(d) >= 40 and abs(float(w.sum()) + skipped - 1.0) < 1e-12


# ------------------------------------------------------------------------------------------------ n-1


def test_n1_what_the_ledger_records_is_frozen():
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SEED, method="sobol").survey(8, ledger=led, **TY.SV)
    before = (led.counts(), led.variant_rows("F-XX"))
    row = next(r for r in led.rows if r["latencies"] and r["status"] == "proposed")
    with pytest.raises(TypeError):
        row["design"]["risk"] = 0.123
    with pytest.raises(AttributeError):
        row["latencies"].append("FORGED")
    with pytest.raises(TypeError):
        row["libs"]["numpy"] = "0.0"
    with pytest.raises(TypeError):
        row["status"] = "refused"
    ds[0]["risk"] = 0.123                                                 # the caller's copy; the row is not it
    assert (led.counts(), led.variant_rows("F-XX")) == before
    assert copy.deepcopy(led).rows == led.rows
    # the plateau role's meta, and a round's
    tds, tled = survey(n=16)
    ev = flat()
    PL.check(ev(tds[0], protocol=TY.PROTOCOL), TY.toy_space(), RULE, ev, ledger=tled, ledger_seed=LSEED)
    meta = tled.roles[f"plateau:{SS.design_id(tds[0])}"]["meta"]
    assert meta["reread"] == TY.REREAD_SEEDS
    with pytest.raises(AttributeError):
        meta["reread"].append(999)
    with pytest.raises(TypeError):
        meta["rule"] = "forged"
    P.propose(TY.toy_space(), [TY.reading(d, TY.smooth(d)) for d in tds], spec=SPEC, round_index=1, seed=ROUND_SEED,
              ledger=tled)
    spec = tled.roles["round-1"]["meta"]["spec"]
    with pytest.raises(TypeError):
        spec["batch"] = 99
    with pytest.raises(AttributeError):
        tled.roles["round-1"]["meta"]["limits"].append({})
    assert spec["batch"] == SPEC.batch


# ------------------------------------------------------------------------------------------------ n-2


def test_n2_a_role_closes_when_its_batch_returns_and_only_its_drawer_records():
    sp = TY.toy_space()
    ds, led = survey(n=16)
    never = dict(TY.SMOOTH_ARGMIN)                                        # a design the sampler never drew
    assert led.closed("survey") and led.roles["survey"]["closed"]
    with pytest.raises(SS.RoleClosed):                                    # the read's probe 5
        led.record(sp, never, role="survey", seed=SEED, refusal=None)
    with pytest.raises(SS.Uncounted):
        SS.admit_one(TY.reading(never, 0.0), ledger=led)
    P.propose(sp, [TY.reading(d, TY.smooth(d)) for d in ds], spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led)
    assert led.closed("round-1")
    with pytest.raises(SS.RoleClosed):
        led.record(sp, never, role="round-1", seed=ROUND_SEED, refusal=None, round_index=1)
    role = f"plateau:{SS.design_id(ds[0])}"
    ev = flat()
    tried = []

    def sneaky(design, *, protocol):                                      # the caller's runner, inside the check
        try:
            led.record(sp, never, role=role, seed=LSEED, refusal=None)
        except SS.NotTheDrawer:
            tried.append("refused")
        else:
            tried.append("RECORDED")
        return ev(design, protocol=protocol)

    PL.check(ev(ds[0], protocol=TY.PROTOCOL), sp, RULE, sneaky, ledger=led, ledger_seed=LSEED)
    assert tried and set(tried) == {"refused"}
    assert led.closed(role) and SS.design_id(never) not in {r["id"] for r in led.rows}
    with pytest.raises(SS.RoleClosed):
        led.record(sp, never, role=role, seed=LSEED, refusal=None)
    pen, other = led.begin("plateau:manual", 3), led.begin("plateau:other", 3)
    for p in (None, other):
        with pytest.raises(SS.NotTheDrawer):
            led.record(sp, never, role="plateau:manual", seed=3, refusal=None, pen=p)
    with pytest.raises(SS.NotTheDrawer):
        led._close("plateau:manual", other)
    pen.record(sp, never, refusal=None)                                   # its drawer, while open
    pen.close()
    with pytest.raises(SS.RoleClosed):
        pen.record(sp, never, refusal=None)


# ------------------------------------------------------------------------------------------------ n-3


def test_n3_a_rounds_spec_and_limits_are_in_its_role():
    sp = TY.toy_space()
    lim = P.Limit("reach", 0.4, "<=")
    ds, led = survey(n=16, **TY.sv(measures=("reach",)))
    rs = [TY.reading(d, TY.smooth(d)) for d in ds]
    on = [TY.reading(d, d["x1"], measure="reach") for d in ds]
    P.propose(sp, rs, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led, limits=(lim,),
              limit_readings={"reach": on})
    meta = led.roles["round-1"]["meta"]
    assert meta["spec"] == dataclasses.asdict(SPEC) and SS.thaw(meta["limits"]) == [dataclasses.asdict(lim)]
    spec2 = P.RoundSpec(batch=3, pool=64, acquisition="lcb", kappa=1.5)
    P.propose(sp, rs, spec=spec2, round_index=2, seed=ROUND_SEED, ledger=led)
    m2 = led.roles["round-2"]["meta"]
    assert m2["spec"] == dataclasses.asdict(spec2) and m2["spec"] != meta["spec"] and m2["limits"] == ()


# ------------------------------------------------------------------------------------------------ F-3


TRUE_RISK, RISK_BOUND = 0.6, 0.5


def lucky_risk(design, *, protocol):
    """The caller's runner of F-3's toy: the composite flat with seed noise; the risk truly TRUE_RISK, above
    RISK_BOUND, but 0.3 lower on each selection seed (the lucky draw that selected the design)."""
    if protocol.measure == "risk":
        ps = [TRUE_RISK - 0.3 if s in TY.SEEDS else TRUE_RISK + 0.05 * TY.seed_noise(design, s)
              for s in protocol.seeds]
    else:
        ps = [0.2 * TY.seed_noise(design, s) for s in protocol.seeds]
    return TY.reading(design, float(np.mean(ps)), protocol=protocol, per_seed=ps,
                      se=float(np.std(ps, ddof=1) / np.sqrt(len(ps))))


def test_f3_a_limit_is_read_on_the_reread_seeds_and_the_reread_value_is_exposed():
    """BUILD_SURVEY_v2 F-3 (the lead's ruling): a toy finalist whose true risk sits above its bound reads inside on the
    selection seeds and outside on the fresh re-read seeds, and the verdict exposes the re-read's value. The selection
    reading is left as it was."""
    ds, led = survey(**TY.sv(measures=("risk",)))
    fin = ds[0]
    assert led.protocol_for("risk", reread=True) == TY.REREAD.with_measure("risk")
    sel = SS.admit_one(lucky_risk(fin, protocol=led.protocol_for("risk")), ledger=led, measure="risk")
    assert sel.value <= RISK_BOUND                                       # inside on the selection seeds
    v = PL.check(lucky_risk(fin, protocol=TY.PROTOCOL), TY.toy_space(), RULE, lucky_risk, ledger=led,
                 ledger_seed=LSEED)
    want = lucky_risk(fin, protocol=TY.REREAD.with_measure("risk"))
    assert set(v.reread_limits) == {"risk"}
    assert v.reread_limits["risk"]["value"] == want.value and want.value > RISK_BOUND     # outside on the re-read
    assert v.reread_limits["risk"]["se"] == pytest.approx(want.se)
    with pytest.raises(SS.OffProtocol):
        led.protocol_for("ruin", reread=True)                            # an undeclared measure stays refused
    _, led0 = survey()
    v0 = PL.check(lucky_risk(fin, protocol=TY.PROTOCOL), TY.toy_space(), RULE, lucky_risk, ledger=led0,
                  ledger_seed=LSEED)
    assert v0.reread_limits == {}                                        # no limit declared, none reported


# ------------------------------------------------------------------------------------------------ Q-192b (M-1)


def test_q192b_a_declared_limit_is_read_on_the_ledgers_reread_seeds():
    """BUILD_SURVEY_c2 M-1, the lead's ruling (RB-2, E-247/E-251): `protocol_for(limit, reread=True)` is exactly the
    ledger's re-read protocol under the limit's measure (the survey's stand-in), and a reading on it passes the door."""
    ds, led = survey(**TY.sv(measures=("risk", "ruin")))
    for m in ("risk", "ruin"):
        lp = led.protocol_for(m, reread=True)
        assert lp == led.reread.with_measure(m) and lp.seeds == TY.REREAD_SEEDS and lp.measure == m
        assert lp.blocks == TY.PROTOCOL.blocks and lp.horizon == TY.PROTOCOL.horizon
        r = TY.reading(ds[0], 0.1, protocol=lp, per_seed=[0.1] * len(lp.seeds))
        assert SS.admit_one(r, ledger=led, measure=m, reread=True) is r
    assert led.protocol_for(None, reread=True) == led.protocol_for("composite", reread=True) == led.reread


def test_q192b_an_undeclared_measure_is_refused_on_either_seed_set():
    ds, led = survey(**TY.sv(measures=("risk",)))
    for reread in (False, True):
        with pytest.raises(SS.OffProtocol, match="not declared"):
            led.protocol_for("ruin", reread=reread)
        base = led.reread if reread else led.protocol
        with pytest.raises(SS.OffProtocol):
            SS.admit_one(TY.reading(ds[0], 0.1, protocol=base.with_measure("ruin")), ledger=led, measure="ruin",
                         reread=reread)
    _, bare = survey()                                                    # no limit declared at all
    with pytest.raises(SS.OffProtocol):
        bare.protocol_for("risk", reread=True)


def test_q192b_the_reread_seeds_are_the_ledgers_fresh_ones_never_the_callers():
    """Re-read seeds that are not fresh are refused at the declaration (not by the floor: five of them, one shared
    with the selection seeds); a limit reading offered as the re-read on the selection seeds, or on fresh seeds of the
    caller's choosing, is refused by the door."""
    stale = (TY.SEEDS[0],) + tuple(range(901, 905))
    assert len(stale) >= SS.MIN_REREAD_SEEDS
    with pytest.raises(SS.LedgerRefused, match="fresh") as e:
        survey(**TY.sv(reread_seeds=stale, measures=("risk",)))
    assert type(e.value) is SS.LedgerRefused
    ds, led = survey(**TY.sv(measures=("risk",)))
    for seeds in (TY.SEEDS, tuple(range(901, 906))):
        p = TY.PROTOCOL.with_measure("risk").with_seeds(seeds)
        with pytest.raises(SS.OffProtocol):
            SS.admit_one(TY.reading(ds[0], 0.1, protocol=p, per_seed=[0.1] * len(seeds)), ledger=led,
                         measure="risk", reread=True)
    with pytest.raises(TypeError):
        led.protocol_for("risk", reread=True, seeds=(901, 902, 903, 904, 905))   # no door takes the caller's seeds


def test_q192b_the_protocol_sha256_with_its_limits_is_recorded():
    ds, led = survey(**TY.sv(measures=("risk",)))
    want = SS.protocol_sha256(TY.PROTOCOL, TY.REREAD_SEEDS, ("risk",))
    assert led.protocol_sha256 == want != SS.protocol_sha256(TY.PROTOCOL, TY.REREAD_SEEDS)
    v = PL.check(lucky_risk(ds[0], protocol=TY.PROTOCOL), TY.toy_space(), RULE, lucky_risk, ledger=led,
                 ledger_seed=LSEED)
    assert v.protocol_sha256 == want and v.protocol["measures"] == ["risk"] and set(v.reread_limits) == {"risk"}
    assert {r["params"]["_protocol_sha256"] for r in led.variant_rows("F-XX")} == {want}
