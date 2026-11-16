"""Q-94's synthetic check (`tests/test_replay_records.py` runs it in a process of its own: the vendored tree goes on its
`sys.path`): place recording on Q-17's U1 replay (`extended/replay_records.py`, through `extended/user_beside.py`'s
declared, off-by-default `recorder` keyword), on synthetic inputs through the vendored engine -- no bar, no atlas.

    python tests/q94_synthetic.py <repository root>             # prints one JSON line last

Two fixtures:

* **simple** -- Q-76's deterministic campaign (`tests/q76_synthetic.py`'s: 160 sessions, every value a function of the
  day's and the trade's index, the shared-day seed `user_beside.SEED_BLOCK[1]`), the offers named `<date>#<index>`;
* **the P-14 table** -- Q-70's walked synthetic trades under P-14's own table, sizing, strict rule and budget
  (`identity/place_records_identity.py`'s `p14_table_inputs`: `extended/synthetic_bars.py`'s bars, seed 20262070), laid
  out as U1 lays a campaign out for the replay (`customer_slices.Campaign`, `user_journey._single_jobs`: both arms), the
  offers the trade table's index -- so the table's R is exercised.

What it reports (the test asserts each):

* **absent = the adapter before Q-94, bit for bit** -- `git show 50e31d3:extended/user_beside.py` (Q-76's adapter, its
  text pinned by sha256) and the adapter now give the same per-start outputs on all 19 responses (Q-76's canonical
  form) and the same tasks, also with the pass-through class given;
* **recording changes nothing** -- with a recorder, every start's output (its U1 record and everything else) is the
  unrecorded run's bit for bit, on all 19 responses, and with the gate's pass-through class on the 9 it can run; the
  tasks are the unrecorded ones plus (the class or None, the reducer); the records with the class equal those without;
  on the P-14 table, both arms;
* **records consistent with the trades** -- the columns exactly `place_fields`' replay schemas; no per-start problem
  (Q-70's per-path checks and Q-94's: the openings equal the replay ledger's by Q-35's reading, the ledger's own checks,
  every routed trade on its own session, the wait the opening's relative session); one record a start, in start order;
  every place (b) to (e) reached; against a direct replay of the start with both recorders on, the trade rows are the
  ledger's rows in order (account, day, P&L, balances, the place by Q-70's rule) and the accounts the engine's funded
  records; Q-35's replay (`extended.openings.run_starts`, the ledger alone on) gives the same openings and U1 records;
* **the wait** -- a probe class (the vendored `FundedAccount`, recording `days` as each opening session starts, nothing
  else) shows every recorded opening's `account_session` is `FundedAccount.days` at that routing, and the probe's run
  is otherwise the pass-through's;
* **a hand-checked start** -- start 14 of the simple campaign, its funded accounts' openings and waits (reported in
  full, pinned in the test after a check by hand);
* **the P-14 table** -- every routed trade's R is its session's table R and on the table's menu (two or more used); the
  offers are rows of the walked trade table on the record's date at its entry time;
* **the checks bite** -- a ledger with an opening row taken out, a day row taken out and a recorded run's trade moved to
  another session each raise problems;
* **refusals**, each before any start runs: a recorder that is not one; a path already carrying `record_trades` or
  `record_days`; offer ids that do not number the blocks; an unknown column; a (design, arm, response) recorded twice;
* **a worker's task** pickles back with its reducer and gives the same outputs and records.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import pickle
import subprocess
import sys
import time
import types
from dataclasses import replace
from pathlib import Path
from typing import Any

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import customer_journey as CJ  # noqa: E402
import user_beside_identity as I  # noqa: E402

from extended import gate as XG  # noqa: E402
from extended import openings as O  # noqa: E402
from extended import place_fields as PF  # noqa: E402
from extended import place_records as PR  # noqa: E402
from extended import replay_records as RR  # noqa: E402
from extended import user_beside as B  # noqa: E402
from propedge.campaign.lockstep import ConductModel, FundedAccount  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402

#: the adapter before Q-94: Q-76's, as merged on master at 50e31d3; the sha256 of its LF text
BASE_COMMIT = "50e31d3"
BASE_SHA256 = "9d2f00e0e926b3a13f78c8f7557c1ed518b117b5ad0d43e23a63e6af9d06b63c"
N_DAYS = 160
STARTS = [0, 5, 14, 21, 40, 77, N_DAYS - 3]
HAND_START = 14
PT = XG.PassThroughFundedAccount


class DaysProbeFundedAccount(FundedAccount):
    """The vendored funded account, recording `days` (its live sessions before this one) on every session it starts
    with no trade yet, and the session's calendar day -- the engine's own count at routing. Nothing else."""

    SEEN: list[tuple[int, int, int]] = []

    def trade_day(self, rules, policy, cap, rel_day, calendar_day, ledger=None, second_trade=False, collect=False):
        if int(self.trades) == 0:
            DaysProbeFundedAccount.SEEN.append((int(self.index), int(calendar_day), int(self.days)))
        return super().trade_day(rules, policy, cap, rel_day, calendar_day, ledger=ledger, second_trade=second_trade,
                                 collect=collect)


# ------------------------------------------------------------------------------------------------ the simple campaign

days = [d.date().isoformat() for d in pd.bdate_range("2023-01-02", periods=N_DAYS)]
blocks = []
for i in range(N_DAYS):
    k = 1 + (i % 4)
    et = np.array([500.0 + 60.0 * j for j in range(k)])
    bad = (i % 13) in (11, 12)                         # a bad spell: every trade lost (breaches, so stacking shows)
    win = np.array([(not bad) and ((i * 7 + j) % 5) < 3 for j in range(k)])
    pnl = np.where(win, 1000.0, -500.0)
    blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0),
                           exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
offer_ids = [[f"{days[i]}#{j}" for j in range(len(b))] for i, b in enumerate(blocks)]
rules = rules_from_ledger()
proto = Protocol(name="q94_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                 trades_per_day=4, max_concurrent_accounts=5)
lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
        "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                     subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                     activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                     max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                     funded_horizon_days=100_000, purchase_budget=(20, 21)),
        "seed": B.SEED_BLOCK[1]}
job = {"engine": "single", "blocks": blocks, "dates": days, "args": args}
out: dict[str, Any] = {}
t_all = time.time()


def before_module() -> tuple[types.ModuleType, str]:
    raw = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:extended/user_beside.py"],
                         capture_output=True, check=True).stdout
    src = raw.decode("utf-8").replace("\r\n", "\n")
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    mod = types.ModuleType("user_beside_before_q94")
    mod.__file__ = f"<{BASE_COMMIT}:extended/user_beside.py>"
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod, sha


OLD, sha = before_module()
out["base_sha_ok"] = sha == BASE_SHA256
out["base_had_no_recorder"] = "recorder" not in inspect.signature(OLD.run_starts).parameters


class Pool:
    """`customer_journey._pool_run` recorded: the tasks each call hands it."""

    def __init__(self):
        self.calls: list[list[tuple]] = []
        self.real = CJ._pool_run

    def __call__(self, tasks, fn, workers, what):
        self.calls.append(list(tasks))
        return self.real(tasks, fn, workers, what)


POOL = Pool()
CJ._pool_run = POOL


def run(mod, resp_name: str, j: dict = job, starts: list[int] = STARTS, design: str = "syn", arm: str = "point",
        **kw) -> list[dict]:
    return mod.run_starts(design, arm, mod.BY_NAME[resp_name], j, starts, 1, **kw)


def diff(a, b) -> str | None:
    return I.first_difference(a, b)


def same_frames(a: pd.DataFrame, b: pd.DataFrame) -> str | None:
    try:
        pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True), check_exact=True)
    except AssertionError as exc:
        return str(exc).splitlines()[0][:300]
    return None


# -- absent = before Q-94, bit for bit: every response, and with the class
absent: dict[str, list[dict]] = {}
absent_diff: dict[str, str | None] = {}
tasks_same: dict[str, bool] = {}
for r in B.RESPONSES:
    POOL.calls.clear()
    old = run(OLD, r.name)
    new = run(B, r.name)
    absent[r.name] = new
    absent_diff[r.name] = diff(old, new)
    t_old, t_new = POOL.calls
    tasks_same[r.name] = (len(t_old) == len(t_new) and all(
        len(a) == len(b) == 8 and a[:3] == b[:3] and a[6:] == b[6:] and all(x is y for x, y in zip(a[3:6], b[3:6]))
        for a, b in zip(t_old, t_new)))
out["absent_diff"] = absent_diff
out["absent_tasks_same"] = tasks_same
non_ftp = [r.name for r in B.RESPONSES if r.kind != "ftp"]
absent_pt: dict[str, list[dict]] = {}
cls_diff = {}
for name in non_ftp:
    POOL.calls.clear()
    old = run(OLD, name, funded_account_cls=PT)
    absent_pt[name] = run(B, name, funded_account_cls=PT)
    t_old, t_new = POOL.calls
    cls_diff[name] = (diff(old, absent_pt[name]) is None and len(t_old) == len(t_new)
                      and all(len(a) == len(b) == 9 and a[8] is b[8] is PT for a, b in zip(t_old, t_new)))
out["absent_with_class_same"] = cls_diff

# -- recording changes nothing: every response; and with the pass-through class
on_diff: dict[str, str | None] = {}
on_tasks: dict[str, bool] = {}
recorders: dict[str, RR.ReplayRecorder] = {}
for r in B.RESPONSES:
    rec = RR.ReplayRecorder(offer_ids=offer_ids)
    POOL.calls.clear()
    got = run(B, r.name, recorder=rec)
    on_diff[r.name] = diff(absent[r.name], got)
    (t_on,) = POOL.calls
    POOL.calls.clear()
    run(B, r.name)
    (t_off,) = POOL.calls
    on_tasks[r.name] = (len(t_on) == len(t_off) and all(
        len(a) == 10 and len(b) == 8 and a[:3] == b[:3] and a[6:8] == b[6:8]
        and all(x is y for x, y in zip(a[3:6], b[3:6])) and a[8] is None and isinstance(a[9], RR.ReplayReducer)
        for a, b in zip(t_on, t_off)))
    recorders[r.name] = rec
out["on_diff"] = on_diff
out["on_tasks"] = on_tasks
pt_on_diff, pt_rec_same, pt_tasks = {}, {}, {}
for name in non_ftp:
    rec = RR.ReplayRecorder(offer_ids=offer_ids)
    POOL.calls.clear()
    got = run(B, name, funded_account_cls=PT, recorder=rec)
    (t_on,) = POOL.calls
    pt_tasks[name] = all(len(a) == 10 and a[8] is PT and isinstance(a[9], RR.ReplayReducer) for a in t_on)
    pt_on_diff[name] = diff(absent_pt[name], got)
    pt_rec_same[name] = (same_frames(recorders[name].trades(), rec.trades()) or
                         same_frames(recorders[name].accounts(), rec.accounts()))
out["pt_on_diff"], out["pt_tasks"], out["pt_records_same_as_without"] = pt_on_diff, pt_tasks, pt_rec_same

# -- the records: columns, problems, one a start in start order, places
off = recorders["off"]
out["columns"] = {"trades": list(off.trades().columns) == list(PF.REPLAY_TRADE_COLUMNS),
                  "accounts": list(off.accounts().columns) == list(PF.REPLAY_ACCOUNT_COLUMNS)}
out["problems"] = {name: rec.problems()[:3] for name, rec in recorders.items()}
out["starts_in_order"] = {name: [x["start_day"] for x in rec.per_start("syn", "point", name)] == STARTS
                          for name, rec in recorders.items()}
out["recorded_keys"] = {name: rec.recorded() == [("syn", "point", name)] for name, rec in recorders.items()}
cnt: dict[str, int] = {}
for p in PR.SINGLE_PLACES:
    cnt[p] = int(sum(int(rec.counts("syn", "point", n).get(p, 0)) for n, rec in recorders.items()))
out["places_all_responses"] = cnt
out["places_off"] = {p: int(off.counts("syn", "point", "off").get(p, 0)) for p in PR.PLACES}
t_off = off.trades()
out["places_rows_agree"] = all(int((t_off["place"] == p).sum()) == out["places_off"][p] for p in PR.SINGLE_PLACES)
out["campaign_columns"] = bool(
    (t_off["design"] == "syn").all() and (t_off["arm"] == "point").all() and (t_off["response"] == "off").all()
    and (t_off["enforcement_p"] == 0.0).all()
    and all((t_off.loc[t_off["start_day"] == s, "start_seed"] == B.start_seed(s)).all() for s in STARTS)
    and all((t_off.loc[t_off["start_day"] == s, "start_date"] == days[s]).all() for s in STARTS))
d50 = recorders["denial_50"].trades()
out["level_column"] = bool(len(d50) and (d50["enforcement_p"] == 0.5).all())

# -- against a direct replay of each start with both recorders on (response off)
direct: dict[str, Any] = {"rows": True, "accounts": True, "openings": True, "routed_own_session": True,
                          "offer_names": True, "wait_rel_day": True, "n_trades": 0, "n_openings": 0}
a_off = B.response_args(args, B.BY_NAME["off"])
a_both = {**a_off, "path": {**a_off["path"], "record_trades": True, "record_days": True}}
for s in STARTS:
    L = min(U.HORIZON, N_DAYS - s)
    lp = B.replay(blocks[s:s + L], a_both, B.start_seed(s))
    tr = t_off[t_off["start_day"] == s].reset_index(drop=True)
    led = list(lp.trades)
    direct["n_trades"] += len(led)
    if len(tr) != len(led) or not all(
            (str(r["kind"]), int(r["index"]), int(r["day"]), float(r["pnl"]), float(r["balance_before"]),
             float(r["balance_after"])) == (tr.at[i, "kind"], int(tr.at[i, "account"]), int(tr.at[i, "day"]),
                                             float(tr.at[i, "pnl"]), float(tr.at[i, "balance_before"]),
                                             float(tr.at[i, "balance_after"])) for i, r in enumerate(led)):
        direct["rows"] = False
    ac = off.accounts()
    ac = ac[ac["start_day"] == s].reset_index(drop=True)
    if len(ac) != len(lp.funded) or not all(
            (int(f.index), int(f.activation_day), int(f.days), int(f.trades), int(f.n_payouts)) ==
            (int(ac.at[i, "account"]), int(ac.at[i, "activation_day"]), int(ac.at[i, "days"]),
             int(ac.at[i, "trades"]), int(ac.at[i, "n_payouts"])) for i, f in enumerate(lp.funded)):
        direct["accounts"] = False
    ops = O.openings_from_ledger(led, s)
    direct["n_openings"] += len(ops)
    mine = tr[tr["place"] == "c_funded_opening"]
    if sorted((int(o["account"]), int(o["day"]), int(o["historical_day"]), int(o["trade_index"])) for o in ops) != \
            sorted(zip(mine["account"].astype(int), mine["day"].astype(int), mine["historical_day"].astype(int),
                       mine["trade_index"].astype(int))):
        direct["openings"] = False
    st = tr[tr["source"] == "strategy"]
    if not (st["day"].astype(int) == st["historical_day"].astype(int) + 1).all():
        direct["routed_own_session"] = False
    want = [f"{days[s + int(h)]}#{int(j)}" for h, j in zip(st["historical_day"], st["trade_index"])]
    if list(st["offer"]) != want or list(st["date"]) != [days[s + int(h)] for h in st["historical_day"]]:
        direct["offer_names"] = False
    op = ac[ac["opened"]]
    if not ((op["opening_session"] == op["opening_rel_day"]).all()
            and (op["opening_rel_day"] == op["opening_day"] - op["activation_day"] - 1).all()):
        direct["wait_rel_day"] = False
out["direct"] = direct

# -- Q-35's replay (the ledger alone on): the same openings and U1 records
q35 = O.run_starts("syn", "point", job, STARTS, 1)
q35_ops = sorted((int(o["start_day"]), int(o["account"]), int(o["day"]), int(o["historical_day"]),
                  int(o["trade_index"])) for x in q35 for o in x["openings"])
op_rows = off.openings()
mine_ops = sorted(zip(op_rows["start_day"].astype(int), op_rows["account"].astype(int), op_rows["day"].astype(int),
                      op_rows["historical_day"].astype(int), op_rows["trade_index"].astype(int)))
out["q35"] = {"openings_same": q35_ops == mine_ops, "n": len(q35_ops),
              "records_same": all(not U.record_problems(x["rec"], {k: v for k, v in y["rec"].items() if k != "alt"})
                                  for x, y in zip(q35, absent["off"])),
              "no_problems": all(not x["problems"] for x in q35)}

# -- the wait, through the engine's own count (a probe class recording FundedAccount.days)
probe_wait = {"checked": 0, "equal": True, "outputs_as_pass_through": True}
for s in STARTS:
    DaysProbeFundedAccount.SEEN.clear()
    rp = RR.ReplayRecorder(offer_ids=offer_ids)
    got = run(B, "off", starts=[s], funded_account_cls=DaysProbeFundedAccount, recorder=rp)
    ref = [x for x in absent_pt["off"] if x["rec"]["start_day"] == s]
    if diff([{k: v for k, v in x.items() if k != "funded_account_cls"} for x in got],
            [{k: v for k, v in x.items() if k != "funded_account_cls"} for x in ref]):
        probe_wait["outputs_as_pass_through"] = False
    seen = {(a, d): k for a, d, k in DaysProbeFundedAccount.SEEN}
    for _, row in rp.openings().iterrows():
        probe_wait["checked"] += 1
        if seen.get((int(row["account"]), int(row["day"]))) != int(row["account_session"]):
            probe_wait["equal"] = False
out["probe_wait"] = probe_wait

# -- the hand-checked start: everything the check by hand reads
h_tr = t_off[t_off["start_day"] == HAND_START]
h_ac = off.accounts()
h_ac = h_ac[h_ac["start_day"] == HAND_START]
h_rec = next(x["rec"] for x in absent["off"] if x["rec"]["start_day"] == HAND_START)
out["hand"] = {
    "start_date": days[HAND_START],
    "first_pass": h_rec["first_pass"], "first_funded": h_rec["first_funded"], "funded_days": h_rec["funded_days"],
    "accounts": [{k: (v.item() if hasattr(v, "item") else v) for k, v in r.items()}
                 for r in h_ac[["account", "activation_day", "days", "trades", "opened", "opening_day",
                                "opening_rel_day", "opening_session"]].to_dict("records")],
    "openings": [{k: (v.item() if hasattr(v, "item") else v) for k, v in r.items()}
                 for r in h_tr[h_tr["place"] == "c_funded_opening"][
                     ["account", "day", "historical_day", "trade_index", "date", "offer", "entry_t", "rel_day",
                      "account_session", "pnl", "balance_before"]].to_dict("records")],
    "trades_by_place": {p: int((h_tr["place"] == p).sum()) for p in PR.SINGLE_PLACES},
    # the slot (a funded account's opening shares its session with other accounts' trades): the trades of each opening
    # session, in ledger order, as (kind, account, trade index)
    "opening_sessions": {int(d): [(str(k), int(a), int(j)) for k, a, j in
                                  zip(g["kind"], g["account"], g["trade_index"])]
                         for d, g in h_tr[h_tr["day"].isin(h_tr.loc[h_tr["place"] == "c_funded_opening", "day"])
                                          ].groupby("day")},
    "block_sizes": {int(d): len(blocks[HAND_START + int(d) - 1]) for d in
                    h_tr.loc[h_tr["place"] == "c_funded_opening", "day"]},
}

# -- the P-14 table: R, offers, both arms, on = off
import place_records_identity as PRI  # noqa: E402  (identity/: Q-70's fixture)
import a3_brk30_cb20 as C  # noqa: E402
import customer_slices as cs  # noqa: E402
import user_journey as UJ  # noqa: E402

t0 = time.time()
P = PRI.p14_table_inputs()
camp = cs.Campaign(name="q94_syn", blocks=P["blocks"], dates=P["days"], kw=P["kw"])
jobs = UJ._single_jobs(camp, P["kw"]["risk_policy"], C.BUDGET)
ids = PR.block_offer_ids(P["t"], P["days"], P["blocks"])
n14 = len(P["blocks"])
s14 = UJ.start_choice(n14, 4)
tab: dict[str, Any] = {"starts": s14, "sessions": n14, "offers": len(P["t"])}
for arm in UJ.ARMS:
    jb = jobs[arm]
    off_outs = run(B, "off", j=jb, starts=s14, design="p14syn", arm=arm)
    rec = RR.ReplayRecorder(offer_ids=ids)
    on_outs = run(B, "off", j=jb, starts=s14, design="p14syn", arm=arm, recorder=rec)
    tr = rec.trades()
    st = tr[tr["source"] == "strategy"]
    tab[arm] = {
        "on_equals_off": diff(off_outs, on_outs),
        "problems": rec.problems()[:3],
        "places": {p: int(rec.counts("p14syn", arm, "off").get(p, 0)) for p in PR.SINGLE_PLACES},
        "rr_finite": bool(len(st) and np.isfinite(st["rr"].to_numpy(float)).all()),
        "rr_is_table": bool(len(st) and np.allclose(st["rr"].to_numpy(float), st["policy_rr"].to_numpy(float),
                                                    rtol=0, atol=1e-12)),
        "rr_on_menu": bool(set(np.round(st["rr"].unique(), 9)) <= set(np.round(P["menu"], 9))),
        "rr_used": sorted(float(x) for x in set(np.round(st["rr"], 9))),
        "rr_used_le": bool((np.isnan(st["rr_used"].to_numpy(float))
                            | (st["rr_used"].to_numpy(float) <= st["rr"].to_numpy(float) + 1e-12)).all()),
        "offers": PRI.offer_problems(st.assign(historical_day=st["start_day"] + st["historical_day"]),
                                     P["t"], P["days"], f"P-14 table {arm}"),
        "trades": int(len(tr)), "openings": int(len(rec.openings()))}
    # with the pass-through class too
    rec_pt = RR.ReplayRecorder(offer_ids=ids)
    pt_outs = run(B, "off", j=jb, starts=s14, design="p14syn", arm=arm, funded_account_cls=PT, recorder=rec_pt)
    tab[arm]["pt_on_equals_off"] = diff(run(B, "off", j=jb, starts=s14, design="p14syn", arm=arm,
                                            funded_account_cls=PT), pt_outs)
    tab[arm]["pt_records_same"] = same_frames(tr, rec_pt.trades()) or same_frames(rec.accounts(), rec_pt.accounts())
tab["seconds"] = round(time.time() - t0, 1)
out["p14_table"] = tab

# -- the checks bite: a tampered run is refused
red = RR.ReplayRecorder(offer_ids=offer_ids).reducer("syn", "point", B.BY_NAME["off"], job)
s = HAND_START
L = min(U.HORIZON, N_DAYS - s)
raw = B.replay(blocks[s:s + L], a_both, B.start_seed(s))
_, clean = red.reduce(raw, s, L, B.start_seed(s), days[s])
led = list(raw.trades)
first_f = next(i for i, r in enumerate(led) if r["kind"] == "funded")
acct = int(led[first_f]["index"])
no_open = replace(raw, trades=tuple(r for i, r in enumerate(led) if i != first_f))
first_row = next(i for i, r in enumerate(raw.account_days) if r["kind"] == "funded" and int(r["index"]) == acct)
no_day = replace(raw, account_days=tuple(r for i, r in enumerate(raw.account_days) if i != first_row))
moved = list(led)
moved[first_f] = {**led[first_f], "historical_day": int(led[first_f]["historical_day"]) + 1}
off_session = replace(raw, trades=tuple(moved))
out["bite"] = {"clean": clean["problems"],
               "opening_removed": red.reduce(no_open, s, L, B.start_seed(s), days[s])[1]["problems"][:4],
               "day_row_removed": red.reduce(no_day, s, L, B.start_seed(s), days[s])[1]["problems"][:4],
               "trade_moved": red.reduce(off_session, s, L, B.start_seed(s), days[s])[1]["problems"][:4]}
plain, _ = red.reduce(raw, s, L, B.start_seed(s), days[s])
unrec = B.replay(blocks[s:s + L], a_off, B.start_seed(s))
out["plain_is_unrecorded"] = (all(getattr(plain, k) == () == getattr(unrec, k)
                                  for k in ("trades", "account_days", "campaign_days"))
                              and repr(plain) == repr(unrec) and len(raw.trades) > 0 and len(raw.account_days) > 0)


# -- refusals, each before any start runs
def refused(call, exc: type) -> bool:
    n = len(POOL.calls)
    try:
        call()
    except exc:
        return len(POOL.calls) == n
    except Exception:  # noqa: BLE001
        return False
    return False


carrying = {k: {**job, "args": {**args, "path": {**args["path"], k: False}}} for k in ("record_trades", "record_days")}
twice = RR.ReplayRecorder(offer_ids=offer_ids)
run(B, "off", starts=[0], recorder=twice)
out["refused"] = {
    "not_a_recorder": refused(lambda: run(B, "off", recorder=object()), TypeError),
    "gate_recorder": refused(lambda: run(B, "off", recorder=PR.PlaceRecorder()), TypeError),
    "path_carrying_record_trades": refused(lambda: run(B, "off", j=carrying["record_trades"],
                                                       recorder=RR.ReplayRecorder()), ValueError),
    "path_carrying_record_days": refused(lambda: run(B, "off", j=carrying["record_days"],
                                                     recorder=RR.ReplayRecorder()), ValueError),
    "offer_ids_short": refused(lambda: run(B, "off", recorder=RR.ReplayRecorder(offer_ids=offer_ids[:-1])),
                               ValueError),
    "offer_ids_bad_block": refused(lambda: run(B, "off", recorder=RR.ReplayRecorder(
        offer_ids=[x[:-1] if i == 7 else x for i, x in enumerate(offer_ids)])), ValueError),
    "unknown_column": refused(lambda: RR.ReplayRecorder(columns=("no_such",)), ValueError),
    "recorded_twice": refused(lambda: run(B, "off", starts=[0], recorder=twice), RuntimeError),
    "reduce_args_carrying": refused(lambda: red.recording_args({**a_off, "path": {**a_off["path"],
                                                                                  "record_days": True}}), ValueError),
}
# without a recorder a path carrying the recorders runs as before (the keyword off changes nothing)
out["carrying_without_recorder_runs"] = len(run(B, "off", starts=[0], j=carrying["record_days"])) == 1

# -- kept columns
keep = ("place", "account", "day", "account_session", "offer")
rk = RR.ReplayRecorder(offer_ids=offer_ids, columns=keep)
run(B, "off", recorder=rk)
order = list(PF.REPLAY_CAMPAIGN_COLUMNS) + [c for c in PF.REPLAY_TRADE_COLUMNS if c in keep]
out["kept"] = {"columns": list(rk.trades().columns) == order,
               "equal": same_frames(rk.trades(), t_off[order]) is None,
               "accounts_whole": same_frames(rk.accounts(), off.accounts()) is None,
               "none_kept": list(RR.ReplayRecorder(columns=()).trades().columns) == list(PF.REPLAY_CAMPAIGN_COLUMNS)}

# -- a worker's task: pickles back with its reducer; the same outputs and records
POOL.calls.clear()
run(B, "denial_25", recorder=RR.ReplayRecorder(offer_ids=offer_ids), funded_account_cls=PT)
(task,) = POOL.calls[-1]
back = pickle.loads(pickle.dumps(task))
o1, r1 = B._task(task)
o2, r2 = B._task(back)
out["task_given"] = {"length": len(task), "class": task[8] is PT, "pickles_back": back[8] is PT,
                     "reducer": isinstance(back[9], RR.ReplayReducer),
                     "same_outputs": diff(o1, o2) is None,
                     "same_records": diff([{k: v for k, v in x.items() if k not in ("trades", "accounts", "counts")}
                                           for x in r1],
                                          [{k: v for k, v in x.items() if k not in ("trades", "accounts", "counts")}
                                           for x in r2]) is None
                     and same_frames(RR.frame(r1, "trades"), RR.frame(r2, "trades")) is None
                     and same_frames(RR.frame(r1, "accounts"), RR.frame(r2, "accounts")) is None
                     and len(RR.frame(r1, "trades")) > 0}
out["signature"] = inspect.signature(B.run_starts).parameters["recorder"].default is None
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
