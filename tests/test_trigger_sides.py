"""The trigger's own side (`extended/trigger_sides.py`; CHARTER 3.5, E-221 O-4, the lead's R-1 ruling on Wave 3.5): on
synthetic offers only -- no bar is read.

What is held:
* P-14's side is the breakout's sign from the offer's tag (`brk30+` / `brk30-`), with or against it, by the declared
  rule; a tag that is not the trigger's refuses;
* RL3's side is the declared fade-or-break rule of the ticket's level and the ticket's role (fade against the role,
  break with it), and the order it gives is `triggers.order_for`'s own (a fade limit at the level, a break stop one tick
  beyond);
* a source with no declared side rule (P-16) and the coin refuse; a rule outside the closed vocabulary refuses;
* the typed provenance: a `TriggerSide` is made only by `trigger_side` (a hand-built one refuses), and it carries
  `provenance == "trigger"`;
* the coin-sided schedule is untouched: `components._trade_row` still stamps `side_source="coin"`.
"""
from __future__ import annotations

import inspect

import pytest

from extended import components as C
from extended import trigger_sides as TS
from extended import triggers as T
from extended import walker as W


def _p14(tag: str, **kw) -> T.Offer:
    f = dict(source="p14", session=3, decision=1101, sub=0, alert=1101, live=1104, entry=T.LIMIT, level=18000.0,
             expires=1104 + T.LIMIT_WINDOW - 1, tag=tag)
    f.update(kw)
    return T.Offer(**f)


def _rl3(kind: str, name: str, role: int, level: float = 18000.0) -> T.Offer:
    return T.Offer("rl3", 3, T.RTH_OPEN, T.RL3_SUBS[(kind, name)], T.RTH_OPEN, T.LIVE_0900, T.TICKET, level, role,
                   expires=T.RL3_CUTOFFS[2] - 1, group=f"rl3:{kind}", rewrite=True, tag=f"{kind}_{name}")


P14 = T.P14Breakout(latency=3, entry="limit", first=1077, last=1257)
RL3 = T.RL3Tickets("pd", T.RL3_CUTOFFS[2])


@pytest.mark.parametrize("tag,rule,want", [("brk30+", "with_breakout", 1), ("brk30-", "with_breakout", -1),
                                           ("brk30+", "against_breakout", -1), ("brk30-", "against_breakout", 1)])
def test_p14_side_is_the_breakouts_sign(tag, rule, want):
    s = TS.trigger_side(P14, rule, _p14(tag))
    assert s.side == want and s.provenance == "trigger" and s.rule == rule and s.tag == tag and s.source == "p14"


@pytest.mark.parametrize("tag", ["brk30", "brk15+", "mark", "", "brk30+x", "coin"])
def test_p14_tag_not_the_triggers_refuses(tag):
    with pytest.raises(TS.SideRefused):
        TS.trigger_side(P14, "with_breakout", _p14(tag))


@pytest.mark.parametrize("name,role,rule,side,kind", [
    ("hi", 1, "fade", -1, W.LIMIT_ENTRY), ("hi", 1, "break", 1, W.STOP_ENTRY),
    ("lo", -1, "fade", 1, W.LIMIT_ENTRY), ("lo", -1, "break", -1, W.STOP_ENTRY),
    ("hi", -1, "fade", 1, W.LIMIT_ENTRY), ("lo", 1, "break", 1, W.STOP_ENTRY)])
def test_rl3_side_is_the_declared_rule_of_the_level(name, role, rule, side, kind):
    rules = {"hi": "fade", "lo": "break"}
    rules[name] = rule
    off = _rl3("pd", name, role)
    s = TS.trigger_side(RL3, rules, off)
    assert s.side == side and s.provenance == "trigger" and s.ticket_rule == rule
    got_kind, price = T.order_for(off, s.side)
    assert got_kind == kind
    assert price == (off.level + s.side * W.TICK if rule == "break" else off.level)


def test_rl3_rule_must_cover_exactly_the_kinds_levels():
    for bad in ({"hi": "fade"}, {"hi": "fade", "lo": "break", "up": "fade"}, {"hi": "fade", "lo": "coin"},
                {"hi": "fade", "lo": ""}, "fade", None):
        with pytest.raises(TS.SideRefused):
            TS.check_rule(RL3, bad)
    TS.check_rule(RL3, {"hi": "fade", "lo": "break"})


def test_rl3_ticket_of_another_kind_or_without_role_refuses():
    rules = {"hi": "fade", "lo": "break"}
    with pytest.raises(TS.SideRefused):
        TS.trigger_side(RL3, rules, _rl3("on", "hi", 1))
    with pytest.raises(TS.SideRefused):
        TS.trigger_side(RL3, rules, _rl3("pd", "hi", 0))


def test_no_side_rule_for_p16_and_the_coin():
    p16 = T.P16Marks((960, 990))
    coin = T.CoinMarks(960, 990)
    for trig in (p16, coin):
        with pytest.raises(TS.SideRefused):
            TS.check_rule(trig, "with_breakout")
    with pytest.raises(TS.SideRefused, match="evaluation's device"):
        TS.check_rule(coin, "with_breakout")


@pytest.mark.parametrize("rule", ["toss a fair coin", "coin", "", None, "WITH_BREAKOUT", ["with_breakout"]])
def test_p14_rule_outside_the_vocabulary_refuses(rule):
    with pytest.raises(TS.SideRefused):
        TS.check_rule(P14, rule)


def test_offer_of_another_source_refuses():
    with pytest.raises(TS.SideRefused):
        TS.trigger_side(P14, "with_breakout", _p14("brk30+", source="coin"))


def test_a_trigger_side_is_made_only_by_trigger_side():
    with pytest.raises(TS.SideRefused):
        TS.TriggerSide("p14", "with_breakout", "brk30+", 1)
    s = TS.trigger_side(P14, "with_breakout", _p14("brk30+"))
    assert TS.is_trigger_side(s)
    assert not TS.is_trigger_side(object())
    import dataclasses
    for kw in (dict(side=-1), dict(tag="brk30-"), dict(rule="against_breakout")):
        with pytest.raises(TS.SideRefused):                     # a minted side altered by replace
            dataclasses.replace(s, **kw)


def test_the_schedule_stays_coin_sided():
    """The scheduler's only trade row is the coin's: the playbook never takes a side from it (R-1)."""
    src = inspect.getsource(C._trade_row)
    assert 'side_source="coin"' in src and src.count("side_source=") == 1
