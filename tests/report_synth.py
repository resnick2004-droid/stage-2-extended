"""Synthetic start rows in the form of Stage 2's U1 file (section `start`; `vendor/stage2/results/user_journey.csv`)
for the report's tests (Q-27). Plain Python and `random.Random(seed)`: nothing here reads the bars or a result.

Each design is a toy account process, not a model of anything: day 0 buys an evaluation (a fee), each later session may
buy another (a fee), the first pass comes on a random session, and from the pass on a payout may arrive (more than one
on the same session at times), each withheld with the ladder's denial probability. The rows are consistent the way
U1's are: the net path is the cumulative cash, the month-end nets are the path at sessions 21, 42, ..., the fees by a
month end are the payouts received by it less the net (to the millionth), the cash before an event is the deepest the
path went below zero on the closes before it. Late start days have fewer sessions left (`observed`), so every reading's
eligibility is exercised; some designs leave start days never paid or never back to break-even.

Seeds (Q-27 tests): 20262701, 20262702, 20262703 -- fixed here, used nowhere else.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

MONTH, MONTHS = 21, 12
YEAR = MONTH * MONTHS
SEEDS = (20262701, 20262702, 20262703)

#: toy designs: (fee, re-buy probability a session, pass probability a session, payout probability a session after the
#: pass, payout cash range, probability that a payout session pays twice)
DESIGNS = {
    "steady": (150.0, 0.05, 0.35, 0.12, (300.0, 900.0), 0.10),
    "lumpy": (150.0, 0.08, 0.15, 0.03, (500.0, 4000.0), 0.30),
    "poor": (200.0, 0.10, 0.05, 0.01, (200.0, 600.0), 0.0),
}


def _dates(n: int) -> list[str]:
    d, out = date(2021, 1, 4), []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def _fmt(x: float) -> str:
    return repr(float(x))


def start_row(rng: random.Random, design: str, observed: int, denial: float) -> dict:
    fee, rebuy, p_pass, p_pay, (lo, hi), p_two = DESIGNS[design]
    rel = [-fee]
    passed = None
    pays: list[tuple[int, float]] = []
    for k in range(1, observed + 1):
        x = rel[-1]
        if rng.random() < rebuy:
            x -= fee
        if passed is None and rng.random() < p_pass:
            passed = k
        if passed is not None and k > passed and rng.random() < p_pay:
            for _ in range(2 if rng.random() < p_two else 1):
                cash = round(rng.uniform(lo, hi), 2)
                if rng.random() >= denial:
                    pays.append((k, cash))
                    x += cash
        rel.append(x)
    return _row(rel, passed, pays, observed)


def explicit_row(*, observed: int, fees: dict[int, float], payouts: list[tuple[int, float]],
                 pass_day: int | None) -> dict:
    """A start row from explicit events: `fees` {session: dollars paid at its close}, `payouts` [(session, cash)] in
    arrival order, the first pass's session (or None). For the hand-worked case."""
    rel = []
    for k in range(observed + 1):
        rel.append(-sum(v for d, v in fees.items() if d <= k) + sum(c for d, c in payouts if d <= k))
    return _row(rel, pass_day, list(payouts), observed)


def _row(rel: list[float], passed: int | None, pays: list[tuple[int, float]], observed: int) -> dict:
    def spent_before(day: int) -> float:
        return 0.0 if day <= 0 else max(0.0, -min(rel[:day]))

    def received(day: int) -> float:
        return sum(c for d, c in pays if d <= day)

    fp = float(passed) if passed is not None else float("nan")
    fy = float(pays[0][0]) if pays else float("nan")
    row = {
        "section": "start", "observed": float(observed),
        "pass_days": "" if passed is None else str(passed), "funded_days": "" if passed is None else str(passed),
        "pay_days": " ".join(str(d) for d, _ in pays), "pay_cash": " ".join(_fmt(c) for _, c in pays),
        "payouts": float(len(pays)), "first_pass": fp, "first_funded": fp, "first_payout": fy,
        "first_payout_cash": pays[0][1] if pays else float("nan"),
        "spent_before_first_pass": spent_before(passed) if passed is not None else float("nan"),
        "spent_before_first_payout": spent_before(pays[0][0]) if pays else float("nan"),
        "net_30": rel[30] if observed >= 30 else float("nan"),
        "net_by_session": " ".join(_fmt(x) for x in rel),
        "exact_runs_differing": "",
    }
    for m in range(1, MONTHS + 1):
        d = MONTH * m
        row[f"net_month_{m}"] = rel[d] if d <= observed else float("nan")
        row[f"fees_month_{m}"] = round(received(d) - rel[d], 6) if d <= observed else float("nan")
    return row


def rows(seed: int, *, designs=("steady", "lumpy"), starts: int = 260, sessions: int = 280,
         ladder: tuple[float, ...] | None = (0.0, 0.10, 0.25, 0.50), arm: str = "verdict") -> list[dict]:
    """Start rows for each design (and ladder level): `starts` start days, start s observing min(252, sessions - s)."""
    dates = _dates(starts)
    out = []
    for i, design in enumerate(designs):
        for level in (ladder if ladder is not None else (None,)):
            rng = random.Random(f"{seed}:{design}:{level}")
            for s in range(starts):
                observed = min(YEAR, sessions - s)
                r = start_row(rng, design, observed, 0.0 if level is None else level)
                r.update(config=design, arm=arm, start_day=float(s), start_date=dates[s])
                if level is not None:
                    r["denial"] = level
                out.append(r)
    return out


def frame(seed: int, *, daily: bool = True, cash: bool = True, **kw):
    """The rows as a DataFrame in a fixed column order; without `daily` / `cash` the optional columns are dropped."""
    import pandas as pd

    df = pd.DataFrame(rows(seed, **kw))
    drop = [c for c, keep in (("net_by_session", daily), ("pay_cash", cash)) if not keep]
    return df.drop(columns=drop)
