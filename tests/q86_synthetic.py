"""Q-86's synthetic check (`tests/test_user_spend.py` runs it in a process of its own: the vendored tree goes on its
`sys.path`): the day-recorder replay of `extended.user_spend` on a deterministic synthetic campaign through the
vendored engine -- no bar, no atlas, no generator (every value is a function of the day's and the trade's index; the
shared-day seed is `user_beside.SEED_BLOCK[1]`, as `identity/user_beside_identity.py --synthetic` uses it, and a replay
draws nothing with it).

    python tests/q86_synthetic.py <repository root>             # the mechanics; prints one JSON line
    python tests/q86_synthetic.py <repository root> pipeline    # scripts/user_spend.py's main on this campaign

The campaign: 300 sessions in three repeating phases of 40 -- quiet (one trade every sixth session: evaluations live
past their billing days and rebill), winning (passes, payouts, break-even) and losing (break-even lost) -- and a second
run of it with the engine's reset of a failed evaluation on (D-146), so the reset fee is exercised.

What it reports (the test asserts each):

* `_task` on six starts (and two with resets): no ledger problem, the break-even close from the ledger the cash's;
* the recorder changes nothing: each start's plain adapter replay (no recorder) has the same closes, Combines, funded
  accounts and payouts, and the same U1 record (`user_beside.long_record`), as the recorder's;
* `user_spend._arrivals` is U1's `payout_arrivals` on every start;
* rebills, activations, payouts, resets, break-even reached, lost and never reached are all exercised;
* the money against U1-format start rows made by Stage 2's own `user_journey.start_rows` from the same records holds,
  and a planted difference is named;
* `spend_args` refuses the recorder set twice, another activation timing, the placement on;
* the judged block's first year is Stage 2's (`u_select.JUDGED_FIRST_YEAR`).

`pipeline`: `scripts/user_spend.py`'s `main --check --starts 3` with this campaign standing in for the three designs (the
build replaced; U1's file replaced by start rows made by Stage 2's `start_rows` from this campaign's records; the
read's authorisation recorded) -- what it prints, the frame it hands `extended.results.write_result` (into a temporary
folder), and the same run with the U1 comparison failing.
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
from extended import use_vendored_stage2

use_vendored_stage2()
import numpy as np
import pandas as pd

from extended import user_beside as B
from extended import user_spend as US
from propedge.campaign.lockstep import ACTIVATION_ON_PASS, ConductModel
from propedge.campaign.payout_method import payout_method_terms
from propedge.campaign.protocols import Protocol
from propedge.contract.adapter import rules_from_ledger
from propedge.contract.rules import load_rules
from propedge.outcomes.distribution import DayBlock
from propedge.research import user_journey as U

out = {}
N = 300
days = [d.date().isoformat() for d in pd.bdate_range("2023-03-01", periods=N)]
MARKS = (0, 130, 610, 920, 930, 945, 960, 1000)
blocks = []
for i in range(N):
    phase = (i // 40) % 3                # 0 quiet, 1 winning, 2 losing
    k = (1 if i % 6 == 0 else 0) if phase == 0 else (i * 5) % 4
    ms = sorted({MARKS[(i + 3 * j) % len(MARKS)] for j in range(k)})
    et = np.array([m + 1 for m in ms], float)
    if phase == 1:
        win = np.array([((i * 7 + j) % 5) < 3 for j in range(len(ms))])
    elif phase == 2:
        win = np.array([((i * 7 + j) % 5) < 1 for j in range(len(ms))])
    else:
        win = np.array([((i + j) % 2) == 0 for j in range(len(ms))])
    pnl = np.where(win, 1000.0, -500.0)
    sides = np.array([1 if (i + j) % 2 else -1 for j in range(len(ms))], int)
    blocks.append(DayBlock(pnl=pnl, risked=np.full(len(ms), 500.0), exit_reasons=tuple("bracket" for _ in ms),
                           entry_t=et, exit_t=et + 3.0, sides=sides))
rules = rules_from_ledger()
proto = Protocol(name="q86_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                 trades_per_day=4, max_concurrent_accounts=5)
lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
        "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                     subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                     activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                     max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                     funded_horizon_days=100_000),
        "seed": B.SEED_BLOCK[1]}
args_reset = {**args, "path": {**args["path"], "reset_failed_combines": True}}
STARTS = [0, 20, 45, 80, 120, N - 30]
RESET_STARTS = [0, 45]


def pay(lp, obs):
    return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)


def totals(lp):
    return lp.path.total_fees, lp.path.total_payouts


def u1_rows(name: str, arm: str, outs: list) -> list:
    """U1-format start rows made by Stage 2's own `user_journey.start_rows` from these records."""
    import user_journey as UJ

    return UJ.start_rows({"config": name, "label": "", "cell": ""}, arm, outs)


def pipeline() -> dict:
    """`scripts/user_spend.py`'s `main --check --starts 3` on this campaign standing in for the three designs: the build
    replaced, U1's file replaced by Stage 2's `start_rows` of this campaign's own records at the starts run, the read's
    authorisation recorded; then the same with the U1 comparison failing."""
    import contextlib
    import importlib.util
    import io

    import extended.results as XR
    import user_journey as UJ

    spec = importlib.util.spec_from_file_location("q86_script", REPO / "scripts" / "user_spend.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    authorised, compared, saved = [], [], {}
    M.reader.authorise_engine_read = lambda *a, **k: authorised.append(k.get("design"))
    M.I.build = lambda rd, name: ({arm: {"engine": "single", "blocks": blocks, "dates": days, "args": args}
                                   for arm in ("verdict", "point")}, {"config": name, "label": "", "cell": ""}, [])

    def reference(rd, designs):
        rows = []
        chosen = UJ.start_choice(len(blocks), 3)
        recs = US._task(("syn", "verdict", blocks, days, args, chosen))
        for name in designs:
            for arm in ("verdict", "point"):
                rows += u1_rows(name, arm, recs)
        return {"start": pd.DataFrame(rows)}

    M.I.u1_reference = reference
    fail = []

    def compare(name, c, arm, outs, ref, n, starts):
        compared.append([name, arm, len(outs), n, starts])
        return list(fail)

    M.I.u1_compare_outs = compare
    real = XR.write_result

    def keep(df, name, **kw):
        saved["df"], saved["name"] = df.copy(), name
        saved["kw"] = {k: kw.get(k) for k in ("seed", "variant_count", "exploratory", "results_dir")}
        saved["parameters"] = sorted(kw["parameters"])
        return real(df, name, **kw)

    XR.write_result = keep
    got = {"authorised": authorised, "compared": compared}
    for case in ("holds", "fails"):
        if case == "fails":
            fail.append("p14 point first_payout_cash: 1 of 3 starts differ (first: start 5: 123.456 against the "
                        "file's 124.789)")
            saved.clear()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.main(["--check", "--starts", "3"])
        got[case] = {"rc": rc, "stdout": buf.getvalue(), "written": bool(saved)}
        if case == "holds" and saved:
            df = saved["df"]
            got["frame"] = {"name": saved["name"], "columns": list(df.columns), "rows": int(len(df)),
                            "sections": sorted(set(df["section"].astype(str))),
                            "identity_rows": int((df["section"] == "identity").sum()),
                            "designs": sorted(set(df.loc[df["section"] != "identity", "design"].astype(str))),
                            "arms": sorted(set(df.loc[df["section"] == "start", "arm"].astype(str))),
                            "problems": US.output_problems(df), **saved["kw"], "parameters": saved["parameters"],
                            "temp": "user_spend_check_" in str(saved["kw"]["results_dir"])}
    return got


if len(sys.argv) > 2 and sys.argv[2] == "pipeline":
    print(json.dumps(pipeline(), default=str))
    raise SystemExit(0)

res = US._task(("syn", "verdict", blocks, days, args, STARTS))
res_reset = US._task(("syn", "verdict", blocks, days, args_reset, RESET_STARTS))
out["starts"] = len(res) + len(res_reset)
out["problems"] = [p for x in res + res_reset for p in x["problems"]]
out["break_even_same"] = not any("break-even" in p for p in out["problems"])

# -- the recorder changes nothing: the plain adapter's replay gives the same path and the same U1 record
plain = B.response_args(args, B.BY_NAME["off"])
recorded = US.spend_args(args)
same, rec_same, arrivals_same = [], [], []
seen = {"rebills": 0, "activations": 0, "payouts": 0, "resets": 0, "broke_even": 0, "lost": 0, "never": 0}
for x, s in zip(res, STARTS):
    L = min(U.HORIZON, len(blocks) - s)
    p0 = B.replay(blocks[s:s + L], plain, B.start_seed(s))
    p1 = B.replay(blocks[s:s + L], recorded, B.start_seed(s))
    same.append(bool(np.array_equal(p0.path.cash_series, p1.path.cash_series)) and not p0.campaign_days
                and len(p1.campaign_days) == L + 1 and p0.combines == p1.combines and p0.funded == p1.funded
                and p0.path.total_fees == p1.path.total_fees and p0.path.total_payouts == p1.path.total_payouts)
    r0 = B.long_record(s, days[s], p0, pay, totals)
    rec_same.append(json.dumps(r0["rec"], sort_keys=True, default=str) == json.dumps(x["rec"], sort_keys=True,
                                                                                   default=str))
    arrivals_same.append(US._arrivals(p1, lag, L) == pay(p1, L))
    seen["rebills"] += sum(max(0, int(c.subscriptions_paid) - 1) for c in p1.combines)
    seen["activations"] += len(p1.funded)
    seen["payouts"] += len(pay(p1, L))
    sp = x["spend"]
    if math.isnan(sp["break_even_day"]):
        seen["never"] += 1
    else:
        seen["broke_even"] += 1
        seen["lost"] += int(sp["break_even_lost"] == 1.0)
seen["resets"] = int(sum(x["spend"]["resets"] for x in res_reset))
out["path_same"] = same
out["record_same"] = rec_same
out["arrivals_same"] = all(arrivals_same)
out["seen"] = seen

# -- the money against U1-format rows made by Stage 2's own `start_rows` from the same records
rows = u1_rows("syn", "verdict", res)
money = {int(x["rec"]["start_day"]): x["money"] for x in res}
tol = max(x["tol"] for x in res)
out["u1_money_problems"] = US.u1_money_problems(money, rows, tol=tol, what="syn verdict")
planted = [dict(r) for r in rows]
k = next(i for i, r in enumerate(planted) if np.isfinite(float(r["fees_month_2"])))
planted[k]["fees_month_2"] = float(planted[k]["fees_month_2"]) + 1.0
out["u1_money_planted"] = US.u1_money_problems(money, planted, tol=tol, what="syn verdict")

# -- refusals: the recorder set twice; another activation timing; a response switched on
refusals = {}
for name, bad in (("record_days_twice", {**args, "path": {**args["path"], "record_days": False}}),
                  ("activation_on_pass", {**args, "path": {**args["path"], "activation_timing": ACTIVATION_ON_PASS}}),
                  ("placement_on", {**args, "path": {**args["path"], "conduct": ConductModel(rtp=True,
                                                                                             enforcement_p=0.0)}})):
    try:
        US.spend_args(bad)
        refusals[name] = False
    except (US.SpendRefused, ValueError):
        refusals[name] = True
out["refusals"] = refusals
from propedge.research import u_select as S  # noqa: E402

out["judged_first_year"] = int(S.JUDGED_FIRST_YEAR)
print(json.dumps(out, default=str))
