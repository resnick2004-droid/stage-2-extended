"""Wave 3.2's check run in its own process: `extended.three_way_redraw.race_dollars` at no cost and no lattice equals
the vendored `RandomDraw(policy, edge=0, rng, "truncate", "drift")` -- `adapter.BinaryDraw`'s inner draw -- on the same
uniforms (the search template's "the runner's race reduces to it at x = 0, which a test holds on the same uniforms").
The uniforms are the coin field's (`three_way_keys`), handed to the vendored draw through a stand-in generator whose
`random(n)` returns them. Prints one JSON line. Reads no bar and no result; imports the vendored engine, never edits it."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from propedge.contract.adapter import Policy, RandomDraw  # noqa: E402

from extended import three_way_keys as K  # noqa: E402
from extended import three_way_redraw as RD  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402


class Given:
    """A stand-in generator: `random(n)` returns the next n of the given uniforms."""

    def __init__(self, u: np.ndarray):
        self.u, self.i = np.asarray(u, float), 0

    def random(self, n: int) -> np.ndarray:
        out = self.u[self.i:self.i + int(n)]
        self.i += int(n)
        return out


def main() -> None:
    unit = K.Unit(S.issue("tests"), S.PARTS["tests"], 0, 0, 0)
    equal, n = True, 0
    for j, (risk, rr) in enumerate(((500.0, 1.0), (500.0, 2.0), (250.0, 1.5), (1000.0, 0.5))):
        u = K.uniforms(unit.coin_key(K.moment(j, 900, 0), K.RACE), 400)
        cushion = np.linspace(10.0, 1500.0, 400)
        draw = RandomDraw(Policy(rr=rr, risk=risk), 0.0, Given(u), "truncate", "drift")
        theirs = draw(400, 0, 0, cushion)
        mine = RD.race_dollars(u, risk, rr * risk, cushion)
        equal &= bool(np.allclose(theirs, mine, rtol=0, atol=1e-9))
        n += 400
    # the journey's own race step (`three_way_journey._trade_mc`, the path that decides; the red team's n-4): 400 lanes
    # at the cushions above, one race trade of stop risk / tick dollars and target rr x stop, no cost, the coin read
    # replaced by the same uniforms; the booked change equals the vendored draw's
    from extended import three_way_journey as J

    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=5000, dll=None, activation_fee=1, funded_mll=5000,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    j_equal, j_n = True, 0
    for j, (risk, rr) in enumerate(((500.0, 1.0), (500.0, 2.0), (250.0, 1.5), (1000.0, 0.5))):
        u = K.uniforms(unit.coin_key(K.moment(j, 900, 0), K.RACE), 400)
        cushion = np.linspace(10.0, 1500.0, 400)
        draw = RandomDraw(Policy(rr=rr, risk=risk), 0.0, Given(u), "truncate", "drift")
        theirs = draw(400, 0, 0, cushion)
        tick, l = 5.0, risk / 5.0
        t = J.Trade(session=0, decision=900, entry=905, exit=950, exit_reason="target", g=int(round(rr * l)),
                    l=int(round(l)), tick_value=tick)
        if abs(t.g * tick - rr * risk) > 1e-9 or abs(t.l * tick - risk) > 1e-9:
            raise SystemExit("the bracket is not whole ticks")
        L = J.fresh(400, rules)
        L.bal = cushion - rules.mll
        L.day, L.dead, L.stopped = np.zeros(400), np.zeros(400, bool), np.zeros(400, bool)
        coins = J.CoinLanes(unit.seed, unit.part, 0, 0, range(400), None, False)
        coins.coin = lambda t_, kind, n_=1, lanes=None, _u=u: _u[:, None]
        before = L.bal.copy()
        J._trade_mc(L, t, rules, J.ArmSpec(), coins)
        j_equal &= bool(np.allclose(L.bal - before, theirs, rtol=0, atol=1e-9))
        j_n += 400
    # RB-1 and B-2: a lane whose room is above EPS but at most the trade's costs. The lead's ruling books it as failed at
    # the fill (the race's limit as its barrier goes to zero). The engine races the room it is handed (`lockstep.py`:
    # the draw is called with `room`), books the trade's costs on its exit, clips at the cushion (`max(pnl, -cushion)`)
    # and fails the account at B <= F + EPS: on its losing branch (here forced: every uniform above the race's p) its
    # booked change and breach are the journey's, lane for lane. Its winning branch, of probability c' / (c' + W) with
    # c' at most the costs, is the one the ruling does not keep
    c_equal, c_n = True, 0
    e, xt, xs = 2.12, 2.12, 7.12
    for j, (risk, rr) in enumerate(((200.0, 1.0), (40.0, 1.5), (500.0, 0.5))):
        u = np.full(400, 1.0 - 2.0 ** -53)                          # the engine's losing branch
        room = np.linspace(0.01, e + xs, 400)                       # every room in the window
        draw = RandomDraw(Policy(rr=rr, risk=risk), 0.0, Given(u), "truncate", "drift")
        raw = draw(400, 0, 0, room)
        win = raw > 0
        theirs = np.maximum(raw - e - np.where(win, xt, xs), -room)  # the costs, then the engine's clip
        their_fail = (room + theirs) <= J.EPS
        tick, l = 5.0, risk / 5.0
        t = J.Trade(session=0, decision=900, entry=905, exit=950, exit_reason="target", g=int(round(rr * l)),
                    l=int(round(l)), tick_value=tick, entry_cost=e, x_target=xt, x_stop=xs)
        L = J.fresh(400, rules)
        L.bal = room - rules.mll
        L.day, L.dead, L.stopped = np.zeros(400), np.zeros(400, bool), np.zeros(400, bool)
        coins = J.CoinLanes(unit.seed, unit.part, 0, 0, range(400), None, False)
        coins.coin = lambda t_, kind, n_=1, lanes=None, first=0, record=True, _u=u: _u[:, None]
        before = L.bal.copy()
        J._trade_mc(L, t, rules, J.ArmSpec(), coins)
        c_equal &= bool(np.allclose(L.bal - before, theirs, rtol=0, atol=1e-9)) and bool(np.array_equal(L.dead,
                                                                                                    their_fail))
        c_n += 400
    print(json.dumps({"equal": equal, "n": n, "journey_equal": j_equal, "journey_n": j_n, "clip_equal": c_equal,
                      "clip_n": c_n}))


if __name__ == "__main__":
    main()
