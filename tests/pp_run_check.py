"""The reading's runner checked on synthetic inputs (RD-02 section 14; Q-105b, Q-105d), run by `tests/test_pp_run.py`,
one section a process (the vendored engine on this process's `sys.path`):

    python tests/pp_run_check.py <repository root> <section> [<temporary folder>]      # one JSON line last

* `e2e` -- `scripts/pp_reading.py --synthetic` (two designs) into a temporary folder: exit 0, the three files and their
  manifests verifying; the manifests' `prereg_id` RD-02, `exploratory` False, the 11 runs and their counts, the honesty
  seed read from the pinned file, the retired seeds, the adapter's commit and blob ids, the calendars' and the data
  manifest's sha256, the limits, the recorder's columns; the identity rows all holding in 14 step 2's order across both
  designs (R2); every section of 14 and only those; **every declared output present** (`pp_run.DECLARED_OUTPUTS`, the
  second read's R5 remedy); `lock`'s held requests counted, the oracles' counts checked; the menu's labels and notes;
  the gate file's parts.
* `refusals` -- a planted identity failure and a planted ladder failure each refuse and write nothing; the real mode
  outside a clean run refuses before anything; a protected results folder is refused; `--limit` is the real run's.
* `waits` -- R3, r4, r5 on text only: on this tree's DECISIONS.md every wait is refused; E-068, E-059 and E-049 (rows
  that owe or mention the identities) are refused; the exact tokens are accepted and their rows named; near misses
  are refused; workers above 2, and 2 without `identity-holds: t10w2`, are refused; the limits' rows and columns.
* `authorise` -- n1: every purpose checked before any is ledgered; a refusal of the second, or a missing file, leaves
  nothing ledgered.
* `labels` -- the paired readings on synthetic per-start frames long enough for intervals: the kept windows' interval
  and MDD printed, each interval labelled from the honesty table, the menu counting the intervals.
* `t3` -- R1: T-3 on the runner's composed reading, its per-start frames built through `start_frame` from session-level
  toy records whose events fall after h: every early-block row of `reading_rows` is byte-identical when every session
  from 2024-01-02 on is replaced; the late block's rows change; and a frame with the events left uncut (the defect)
  changes the early block, so the check can see it.
* `order` -- R2: two synthetic designs, the second design's `ref` planted to fail (ladder, then identity): refused, and
  no new run of either design replayed.
* `q44` -- R4: Q-44-shaped per-start rows written by `write_result` and read back as text compare equal, empty and
  numeric-looking text fields included; `RealInputs.ladder_problems` against such a file holds, and sees a cent; the
  default read's comparison fails (the defect).
* `oracles` -- r1: the gate's request oracles on engine-shaped funded records (a correct `half` and `max` request, a
  wrong one, `lock`'s first payout below the lock), the twin's bound, and the replay's bounds, each refusing.
* `holiday` -- r2: requests dated on their own session (`dates[s + k - 1]`) on toy records whose requests fall on known
  early closes and holiday eves.

Every draw here is from section 11's build seed (`identity/gate_identity.py`'s `SYN_SEED`), under keys of its own.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(sys.argv[1])
SECTION = sys.argv[2]
TMP = Path(sys.argv[3]) if len(sys.argv) > 3 else None
for _p in (str(REPO), str(REPO / "identity"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

problems: list[str] = []
out: dict = {}


def check(cond: bool, what: str) -> None:
    if not cond:
        problems.append(what)


def script(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    env.pop("S2X_CLEAN_RUN", None)
    return subprocess.run([sys.executable, str(REPO / "scripts" / "pp_reading.py"), *args], cwd=REPO,
                          capture_output=True, text=True, timeout=900, env=env)


def build_seed() -> int:
    """Section 11's build seed (the toys and T-3's synthetic late block), from its one home in code."""
    import gate_identity as GI

    return int(GI.SYN_SEED)


# ------------------------------------------------------------------------------------------------ toy start records


def toy_outs(dates: list[str], g_pay: np.ndarray, g_cash: np.ndarray, g_fee: np.ndarray, g_pass: np.ndarray,
             differs: dict[int, list[int]] | None = None) -> list[dict]:
    """Session-level toy outputs in `user_beside.run_starts`' form: start s's session k is the global session s + k - 1
    (calendar day = historical day + 1); each start's record from `user_journey.start_record` on its own cash path, so
    a start's events after its h sessions are real events of later sessions."""
    from extended import user_measures as M
    from propedge.research import user_journey as U

    n = len(dates)
    outs = []
    for s in range(n):
        L = min(252, n - s)
        i = np.arange(s, s + L)
        flow = np.where(g_pay[i], g_cash[i], 0.0) - g_fee[i]
        flow[0] -= 49.0                                   # the purchase's fee, booked at the first close
        rel = np.concatenate([[0.0], np.cumsum(flow)])
        passes = [int(k) for k in np.flatnonzero(g_pass[i]) + 1]
        funded = [k + 1 for k in passes if k + 1 <= L]
        pays = [(int(k) + 1, float(g_cash[s + k])) for k in np.flatnonzero(g_pay[i])]
        rec = {"start_day": s, "start_date": dates[s], **U.start_record(1e6 + rel, 1e6, passes, funded, pays)}
        outs.append({"rec": rec, "daily": M.daily(rel), "differs": list((differs or {}).get(s, [])),
                     "checked": [], "pay_bad": 0, "cash_bad": 0, "fee_bad": 0, "record_same": None,
                     "response": {"response_day": float("nan"), "payouts_denied": 0.0, "cash_forfeited": float("nan")}})
    return outs


def toy_world(dates: list[str], key: list[int]) -> tuple[np.ndarray, ...]:
    """Per-session payouts (with their cash), fees and passes, on the global session axis."""
    g = np.random.default_rng(key)
    n = len(dates)
    return (g.random(n) < 1 / 90, np.round(g.uniform(400, 1600, n), 2), np.where(g.random(n) < 0.05, 49.0, 0.0),
            g.random(n) < 1 / 70)


# ------------------------------------------------------------------------------------------------ e2e


def section_e2e() -> None:
    from extended import pp_run as RUN
    from extended import results as XR

    d = TMP / "e2e"
    d.mkdir(parents=True, exist_ok=True)
    r = script("--synthetic", "--results-dir", str(d))
    check(r.returncode == 0 and "EXIT 0" in r.stdout, f"the synthetic run did not finish: {r.stdout[-1500:]}"
                                                      f"{r.stderr[-1500:]}")
    names = ("pp_reading_synthetic", "pp_gate_synthetic", "pp_menu_synthetic")
    for n in names:
        ok, msg = XR.verify_result(d / f"{n}.csv") if (d / f"{n}.csv").is_file() else (False, "absent")
        check(ok, f"{n}: {msg}")
    if problems:
        return
    man = json.loads((d / "pp_reading_synthetic.csv.manifest.json").read_text(encoding="utf-8"))
    par = man.get("parameters", {})
    check(man.get("prereg_id") == "RD-02", f"prereg_id {man.get('prereg_id')!r}")
    check(man.get("exploratory") is False, "the manifest is not exploratory=False")
    check(par.get("run_count") == 11, f"the synthetic run counts {par.get('run_count')} runs, not 11 (two designs: "
                                      "2 references, 6 new, 3 rule sensitivity)")
    check(par.get("run_counts") == {"policy_runs": 8, "new": 6, "references": 2, "rule_sensitivity": 3,
                                    "replays_beside": 32, "gates": 12}, f"the run counts {par.get('run_counts')}")
    import test_pp_draft as D

    check(par.get("seeds", {}).get("honesty_series") == D.COVERAGE_SEED,
          "the honesty seed is not section 11's (read from the pinned file)")
    check(RUN.declared_seed("9.2 item 7's honesty series", REPO) == D.COVERAGE_SEED, "declared_seed")
    check(len(par.get("seeds", {}).get("retired", [])) == 7, "the retired seeds are not listed")
    ad = par.get("adapter", {})
    check(len(ad.get("commit", "")) == 40 and all(ad.get("blobs", {}).get(f) for f in
                                                  ("extended/payout_policy.py", "extended/user_beside.py",
                                                   "extended/gate.py")), f"the adapter's provenance: {ad}")
    check(par.get("calendars") == RUN.CALENDARS and len(par.get("data_manifest_sha256", "")) == 64,
          "the calendars' or the data manifest's sha256")
    check(par.get("limits") == "none approved before the run's commit", f"limits {par.get('limits')!r}")
    check(par.get("recorder_columns") == list(RUN.RECORD_COLUMNS), "the recorder's columns (7.1)")
    check("waits" in par, "the waits are not in the manifest (r4)")
    rd = pd.read_csv(d / "pp_reading_synthetic.csv", low_memory=False)
    gt = pd.read_csv(d / "pp_gate_synthetic.csv", low_memory=False)
    mn = pd.read_csv(d / "pp_menu_synthetic.csv")
    secs = set(rd["section"])
    check(secs <= set(RUN.SECTIONS), f"sections outside 14's: {sorted(secs - set(RUN.SECTIONS))}")
    check("gate" not in secs, "gate rows in pp_reading.csv (n6: they are pp_gate.csv's)")
    ids = rd[rd["section"] == "identity"]
    check(len(ids) == 30 and ids["value"].eq(1.0).all(), f"identity rows: {len(ids)}, all holding "
                                                         f"{ids['value'].eq(1.0).all()}")
    order = list(zip(ids["design"], ids["arm"], ids["measure"]))
    want_a = [(d_, a_, "8.1 items 2 and 4") for d_ in ("syn", "syn2") for a_ in ("verdict", "point")]
    want_b = [(d_, "verdict", "8.1 item 6") for d_ in ("syn", "syn2") for _ in range(4)]
    check(order[:4] == want_a and order[4:12] == want_b and {m for _, _, m in order[12:]} == {"8.1 item 5"},
          f"the order is not 14 step 2's across both designs (R2): {order[:13]}")
    # the declared outputs (R5): every item present
    no_interval = not par.get("honesty", {}).get("settings")
    for item, fname, sec, part, meas, stat in RUN.DECLARED_OUTPUTS:
        if part == "coverage" and no_interval:
            continue                                     # the toy's blocks are too short for an interval: see `labels`
        f = rd if fname == "pp_reading" else gt
        m = (f["part"] == part)
        if sec is not None:
            m &= f["section"] == sec
        if meas != "*":
            m &= f["measure"].astype(str).str.startswith(meas[:-1]) if meas.endswith("*") else f["measure"] == meas
        if stat is not None:
            m &= f["stat"] == stat
        check(bool(m.any()), f"declared output missing: {item} ({fname}, {sec}, {part}, {meas}, {stat})")
    for base in ("lock", "half"):
        check(len(rd[(rd["part"] == "paired") & (rd["cell"] == "lock_half") & (rd["base"] == base)]) > 0,
              f"lock_half is not paired with {base} (9.1 item 5)")
    check(len(rd[(rd["part"] == "paired") & (rd["mode"] == "minimal") & (rd["base"].fillna("").astype(str).str.contains("declared"))]) > 0,
          "the minimal rescue is not paired with its declared cell (n5)")
    for blk in ("all", "early", "late"):
        check(len(rd[(rd["section"] == "mechanics") & (rd["part"] == "mechanics") & (rd["block"] == blk)]) > 0,
              f"no mechanics on the {blk} block (8.3, per block)")
    mech = rd[(rd["section"] == "mechanics") & (rd["cell"] == "lock") & (rd["arm"] == "verdict")
              & (rd["block"] == "all")]
    held = mech[mech["measure"] == "first_requests_held"]["value"]
    check(len(held) and float(held.sum()) > 0, "lock held no first request on the toy (the counts' route)")
    check(rd[(rd["section"] == "mechanics") & (rd["cell"] == "ref")].empty, "ref has mechanics against itself")
    oc = rd[(rd["section"] == "oracle") & (rd["part"] == "gate")]
    check(oc[oc["measure"] == "first_requests_checked"]["value"].sum() > 0, "the gate's request oracle checked nothing")
    check(oc[oc["measure"] == "lock_first_payouts_checked"]["value"].sum() > 0, "lock's oracle checked nothing")
    check(len(mn) and mn["labels"].str.contains("described, not carried").all(), "a menu row is not labelled")
    check(mn[mn["cell"].str.contains("half")]["labels"].str.contains("assumption").all(), "half's label")
    lk = mn[(mn["response"] == "rtp") & mn["cell"].str.startswith("lock")]
    check(len(lk) and lk["labels"].str.contains("L1 on Standard-path accounts only").all(), "lock under rtp's label")
    check(mn["note_focused_trader"].str.contains("half").all(), "the Focused Trader gap does not name half")
    check(set(mn["mode"]) == {"declared"}, "the minimal rescue is on the menu (6.3: never)")
    check(set(mn["cell"]) == set(RUN.POLICY_CELLS), f"the menu's cells {sorted(set(mn['cell']))}")
    check(all(f"{g}_difference" in mn.columns for g in RUN.GUARDED[1:]), "the guarded measures are not on the menu")
    gr = gt[gt["part"] == "gate_row"]
    check(set(gr["cell"]) == {"lock", "half", "lock_half"} and set(gr["twin"].astype(str)) == {"True", "False"},
          "the gate rows are not the three new cells with their twins")
    rdg = gt[(gt["part"] == "reading") & (gt["measure"] == "growth_on_required_bankroll")]
    check(len(rdg) and np.isfinite(rdg["value"].astype(float)).all(),
          "the gate's growth on the required bankroll, the cell's and the base's")
    out["e2e"] = {"rows": len(rd), "sections": sorted(secs), "menu_rows": len(mn), "gate_rows": len(gt)}


def section_refusals() -> None:
    for plant in ("identity", "ladder"):
        d = TMP / f"plant_{plant}"
        d.mkdir(parents=True, exist_ok=True)
        r = script("--synthetic", "--results-dir", str(d), "--plant", plant)
        check(r.returncode == 3 and "nothing written" in r.stdout, f"the planted {plant} failure did not refuse")
        check(not any(d.iterdir()), f"the planted {plant} failure wrote {list(d.iterdir())}")
    r = script()
    check(r.returncode == 3 and "clean checkout" in r.stdout, f"the real mode outside a clean run: {r.stdout[-400:]}")
    r = script("--synthetic", "--results-dir", str(REPO / "results"))
    check(r.returncode == 3 and "never writes" in r.stdout, "a protected results folder was not refused")
    d = TMP / "limit"
    d.mkdir(parents=True, exist_ok=True)
    r = script("--synthetic", "--results-dir", str(d), "--limit", "E-015", "P_level", "min", "0.1")
    check(r.returncode == 2 and not any(d.iterdir()), "--limit was accepted in the synthetic run")


# ------------------------------------------------------------------------------------------------ waits (R3, r4, r5)


def section_waits() -> None:
    import pp_reading as S

    from extended import reader

    text = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
    probs = S.wait_problems(text, 1)
    check(sum("no row of DECISIONS.md carries" in p for p in probs) == len(S.WAITS),
          f"on this tree's DECISIONS.md not every wait was refused: {probs}")
    for rid in ("E-068", "E-059", "E-049"):                       # Y3: rows that owe or mention the identities
        row = reader.decision_row(text, rid)
        check(row is not None, f"{rid} is not in DECISIONS.md")
        if row is None:
            continue
        p = S.wait_problems(row, 1)
        check(sum("no row of DECISIONS.md carries" in q for q in p) == len(S.WAITS), f"{rid} met a wait: {p}")
    ok_text = "\n".join(f"| E-9{i:02d} | 2026-11-17 | **{k} held.** `{tok}` -- the run's HOLDS line. | basis |"
                        for i, (k, tok) in enumerate(S.WAITS.items()))
    check(S.wait_problems(ok_text, 1) == [], f"the exact tokens were refused: {S.wait_problems(ok_text, 1)}")
    check(S.wait_problems(ok_text, 2) == [], "two workers with t10w2 held were refused")
    rows = S.wait_rows(ok_text)
    check(all(len(rows.get(k, [])) == 1 for k in S.WAITS), f"the rows named: {rows}")
    check(rows.get("Q-80") == ["E-901"], f"the row carrying Q-80's token: {rows.get('Q-80')}")
    for bad in ("identity-holds: Q-8", "identity-holds: Q-800", "identity holds: Q-80", "Q-80 holds",
                "identity-holds: Q-80x", "identity-holds:Q-80", "not-identity-holds: Q-80"):
        t = "\n".join(line for line in ok_text.splitlines() if "Q-80`" not in line)
        t += f"\n| E-990 | 2026-11-17 | **{bad}** | basis |"
        check(any("Q-80" in p for p in S.wait_problems(t, 1)), f"a near miss met Q-80's wait: {bad!r}")
    no_t10 = "\n".join(line for line in ok_text.splitlines() if "t10w2" not in line)
    p = S.wait_problems(no_t10, 2)
    check(any("two workers need" in q for q in p), f"two workers without t10w2 were not refused: {p}")
    check(any("one or 2 only" in q for q in S.wait_problems(ok_text, 3)), "three workers were not refused")
    lim_text = ok_text + "\n| E-950 | 2026-11-17 | **E-015's limits approved** | basis |\n| E-951 | x | other | y |"
    lims, lp = S.parse_limits([["E-950", "card_S1_level", "max", "2500"]], lim_text)
    check(lp == [] and lims[0]["bound"] == 2500.0, f"a good limit was refused: {lp}")
    for args, want in ((["E-999", "P_level", "min", "0.1"], "no such"), (["E-951", "P_level", "min", "0.1"], "E-015"),
                       (["E-950", "P_nothing", "min", "0.1"], "column"), (["E-950", "P_level", "below", "0.1"], "kind"),
                       (["E-950", "P_level", "min", "x"], "bound")):
        _, lp = S.parse_limits([args], lim_text)
        check(any(want in q for q in lp), f"a bad limit {args} was accepted: {lp}")
    out["waits"] = {"tokens": list(S.WAITS.values())}


def section_authorise() -> None:
    import pp_reading as S

    from extended import pp_run as RUN

    f = TMP / "engine_file"
    f.write_text("x", encoding="utf-8")
    for refuse_at, files in ((None, [f]), ("payout_ladder_beside", [f]), (None, [f, TMP / "absent"])):
        log: list[tuple[str, str]] = []

        def chk(*a, purpose, _r=refuse_at, _log=log, **kw):
            _log.append(("check", purpose))
            if purpose == _r:
                raise RuntimeError(f"refused {purpose}")

        def led(*a, purpose, _log=log, **kw):
            _log.append(("ledger", purpose))

        try:
            S.authorise_all(RUN.PURPOSES, files=files, declaration=RUN.DECLARATION, repeat=None, what="t",
                            check=chk, ledger=led)
            raised = False
        except (RuntimeError, FileNotFoundError):
            raised = True
        kinds = [k for k, _ in log]
        if refuse_at is None and len(files) == 1:
            check(not raised and kinds == ["check"] * 3 + ["ledger"] * 3, f"n1: the order {log}")
        else:
            check(raised and "ledger" not in kinds, f"n1: a refusal ({refuse_at}, {len(files)} files) ledgered: {log}")
    out["authorise"] = "every purpose checked before any is ledgered"


# ------------------------------------------------------------------------------------------------ labels


def section_labels() -> None:
    from extended import pp_reading as RD
    from extended import pp_run as RUN

    g = np.random.default_rng([build_seed(), 900])
    n = 1500
    days = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", periods=n)]
    obs = np.arange(n, 0, -1)
    base = pd.DataFrame({"start_day": np.arange(n), "start_date": days, "observed": obs})
    cols = sorted({m.col for m in RUN.MEASURES})
    for c in cols:
        base[c] = g.normal(size=n)
    cell = base.copy()
    for c in cols:
        cell[c] = base[c] + g.normal(0.05, 0.5, size=n)
    key = dict(design="syn", arm="verdict", cell="lock", mode="declared", response="off", base="ref")
    honesty: dict = {}
    rows = RUN.paired_rows(cell, base, key, honesty)
    hon = RUN.honesty_table(list(honesty), build_seed(), 30)
    RUN.label_rows(rows, hon)
    p = pd.DataFrame(rows)
    ci = p[p["stat"] == "ci90_low"]
    lab = p[p["stat"] == "interval_label"]
    check(len(ci) > 0 and len(lab) == len(ci), f"{len(ci)} intervals, {len(lab)} labels")
    check(lab["note"].str.contains("gauss/ahead/paired").all() and lab["note"].str.contains("rare and lumpy").all(),
          "a label without its two readings")
    check(not lab["note"].str.contains("pending").any(), "a label left pending")
    for (h, n_w) in honesty:
        check(len(hon[(hon["h"] == h) & (hon["n_w"] == n_w)]) == 21, f"setting ({h}, {n_w}): not 21 shapes")
    nw = p[(p["stat"] == "n_w") & (p["part"] == "paired")].set_index(["block", "measure"])["value"]
    for r in lab.itertuples():
        sub = hon[(hon["h"] == r.h) & (hon["n_w"] == int(nw.loc[(r.block, r.measure)]))]
        want = RD.label(dict(zip(sub["shape"], sub["coverage"])))
        check(bool(r.value) == want, f"{r.block} {r.measure}: the label {bool(r.value)} is not the rule's {want}")
    check(len(p[p["stat"] == "mdd"]) == len(ci), "an interval without its MDD")
    reading = pd.DataFrame(rows + [RUN._row(section="scorecard", part="card", design="syn", arm="verdict", cell="lock",
                                            mode="declared", block="all", measure="card_P", stat="value", value=0.5)])
    menu = RUN.menu_table(reading, [])
    check(int(menu["intervals_printed"].iloc[0]) == len(ci) and
          float(menu["intervals_expected_to_exclude_zero_by_chance"].iloc[0]) == len(ci) / 10.0,
          "the menu's interval count")
    check(menu["P_label"].iloc[0] != "", "the menu's P label is empty")
    out["labels"] = {"intervals": len(ci), "settings": sorted(honesty)}


# ------------------------------------------------------------------------------------------------ T-3 (R1)


def _rowkey(r: dict) -> tuple:
    return (r["section"], r["part"], r["design"], r["arm"], r["cell"], r["mode"], r["response"], r["base"], r["block"],
            r["measure"], r["stat"], int(r["n"]), r["note"])


def _differ(a: list[dict], b: list[dict]) -> tuple | None:
    if len(a) != len(b):
        return ("count", len(a), len(b))
    for x, y in zip(a, b):
        if _rowkey(x) != _rowkey(y) or np.float64(x["value"]).tobytes() != np.float64(y["value"]).tobytes():
            return (_rowkey(x), x["value"], y["value"])
    return None


DROUGHT = 200


def section_t3() -> None:
    """R1 (the second read's Y1): T-3 through `start_frame` from session-level toy records -- events after h included."""
    from extended import pp_run as RUN

    days = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", "2026-07-16")]
    cut = next(i for i, d in enumerate(days) if d >= "2024-01-02")
    worlds, replaced = {}, {}
    for ci, cell in enumerate(RUN.POLICY_CELLS):
        w = toy_world(days, [build_seed(), 902, ci])
        r = toy_world(days, [build_seed(), 903, ci])
        for j in (0, 3):                                  # no payout and no pass in the last 200 sessions of 2023, so
            w[j][cut - DROUGHT:cut] = False               # an early start's first ones fall after its session 126, in
                                                          # 2024 (the second read's Y1) -- the leak, were it uncut
        worlds[cell] = w
        replaced[cell] = tuple(np.concatenate([a[:cut], b[cut:]]) for a, b in zip(w, r))

    def toy_runs(ws: dict) -> dict:
        got = {}
        for cell, w in ws.items():
            o = toy_outs(days, *w)
            got[("syn", "verdict", cell, "declared", "off")] = {"outs": o, "tally": RUN.start_tallies(o, days, 3, set())}
        return got

    ra, rb = toy_runs(worlds), toy_runs(replaced)
    ax, ay = RUN.reading_rows(ra, ["syn"], {}), RUN.reading_rows(rb, ["syn"], {})
    ex = [r for r in ax if r["block"] == "early"]
    ey = [r for r in ay if r["block"] == "early"]
    dif = _differ(ex, ey)
    check(dif is None, f"T-3 (composed): an early-block row changed when 2024 on was replaced: {dif}")
    lx = [r["value"] for r in ax if r["block"] == "late"]
    ly = [r["value"] for r in ay if r["block"] == "late"]
    check(np.float64(lx).tobytes() != np.float64(ly).tobytes(), "T-3 (composed): the late block did not change")
    check(any(r["stat"] == "ci90_low" for r in ex), "T-3 (composed): no early-block interval was tested")
    parts = sorted({r["part"] for r in ex})
    for part in ("distribution", "paired", "card", "s6", "frontier", "evenness_tradeoff", "cvar10", "diverge"):
        check(part in parts, f"T-3 (composed): no early-block {part} row was tested")
    # the defect itself (the second read's R1): the event measures left uncut read 2024 sessions in the early block
    k, kb = ("syn", "verdict", "lock", "declared", "off"), ("syn", "verdict", "ref", "declared", "off")

    def uncut(t: pd.DataFrame) -> pd.DataFrame:
        t = t.copy()
        for ev, spent in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
            ok = t["observed"] >= 126
            t[f"{ev}_by_126"] = np.where(ok, t[ev], np.nan)
            t[f"{spent}_by_126"] = np.where(ok, t[spent], np.nan)
        return t

    fa = [uncut(RUN.start_frame("syn", "verdict", "off", ra[x]["outs"])) for x in (k, kb)]
    fb = [uncut(RUN.start_frame("syn", "verdict", "off", rb[x]["outs"])) for x in (k, kb)]
    key = dict(design="syn", arm="verdict", cell="lock", mode="declared", response="off", base="ref")
    da = [r for r in RUN.paired_rows(fa[0], fa[1], key, {}) + RUN.distribution_rows(fa[0], key) if r["block"] == "early"]
    db = [r for r in RUN.paired_rows(fb[0], fb[1], key, {}) + RUN.distribution_rows(fb[0], key) if r["block"] == "early"]
    check(_differ(da, db) is not None, "T-3 cannot see the defect: with the events uncut the early block did not change")
    out["t3"] = {"early_rows": len(ex), "early_intervals": sum(r["stat"] == "ci90_low" for r in ex), "parts": parts}


# ------------------------------------------------------------------------------------------------ the order (R2)


def section_order() -> None:
    from extended import payout_policy as PP
    from extended import pp_run as RUN
    from extended import pp_run_synthetic as SYN
    from extended import user_beside as B

    calls: list[tuple[str, str, str, bool]] = []
    orig = B.run_starts

    def spy(design, arm, resp, job, starts, workers, *a, funded_account_cls=None, **kw):
        if funded_account_cls is not None:            # a reference run: the reference class, both levers off
            proto = job["args"]["draws"]["protocol"]
            calls.append((design, arm, resp.name, funded_account_cls is PP.REF_CLASS
                          and PP.levers_off(funded_account_cls, proto)))
        return orig(design, arm, resp, job, starts, workers, *a, funded_account_cls=funded_account_cls, **kw)

    B.run_starts = spy
    try:
        for plant in ("ladder", "identity"):
            calls.clear()
            inp = SYN.SyntheticInputs(plant=plant, plant_design="syn2", n_paths=2)
            try:
                RUN.run_reading(inp, designs=SYN.DESIGNS, starts=2, honesty_reps=5, sensitivity_design="syn",
                                time_window=("08:30", "15:10"), log=lambda s: None)
                check(False, f"the planted {plant} failure of syn2's ref did not refuse")
            except RUN.Refused as exc:
                check("syn2" in str(exc), f"the refusal names {exc}")
            new = [c for c in calls if not c[3]]
            check(not new, f"R2: with syn2's ref failing ({plant}), new runs were replayed: {new[:4]}")
            if plant == "ladder":
                check(("syn", "verdict", "denial_10", True) in calls and ("syn2", "verdict", "denial_10", True) in calls,
                      f"(b) did not reach syn2's ref: {calls}")
            else:
                check(calls and not any(c[2] != "off" for c in calls), f"(b) ran before every (a) held: {calls}")
    finally:
        B.run_starts = orig
    out["order"] = "a failure at the second design's ref replays no new run of either design"


# ------------------------------------------------------------------------------------------------ Q-44 (R4)


def section_q44() -> None:
    from extended import pp_run as RUN
    from extended import results as XR
    from extended import user_readings as R

    days = [d.date().isoformat() for d in pd.bdate_range("2023-01-02", periods=320)]
    outs = toy_outs(days, *toy_world(days, [build_seed(), 904]), differs={0: [63], 21: [21, 63], 42: [126]})
    mine = R.rounded(R.start_table("syn", "verdict", "denial_10", outs))
    check((mine["exact_runs_differing"] == "").any() and (mine["exact_runs_differing"] == "63").any() and
          mine["net_month_12"].isna().any(), "the toy lacks an empty text field, a one-number text field or a blank")
    d = TMP / "q44"
    d.mkdir(parents=True, exist_ok=True)
    csv, _ = XR.write_result(mine, "user_beside_starts_toy", script="tests/pp_run_check.py", seed=build_seed(),
                             parameters={"toy": True}, results_dir=d, description="a toy Q-44 per-start file",
                             exploratory=True)
    theirs = XR.read_result(csv, text=True)
    check(theirs["exact_runs_differing"].iloc[0] == "63" and "" in set(theirs["exact_runs_differing"]),
          "the text read did not keep the text fields as text")
    p = RUN.q44_problems(mine, theirs, "toy", all_starts=True)
    check(p == [], f"R4: the round trip differs: {p[:3]}")
    ri = RUN.RealInputs(q44_path=csv)
    check(ri.ladder_problems("syn", "denial_10", outs) == [], "R4: RealInputs.ladder_problems refuses an exact file")
    i = 200                                               # a start with 120 sessions: its month-1 net, no evenness
    nudged = [dict(x, rec=dict(x["rec"], net_month=[x["rec"]["net_month"][0] + 0.01] + list(x["rec"]["net_month"][1:])))
              if j == i else x for j, x in enumerate(outs)]
    pn = ri.ladder_problems("syn", "denial_10", nudged)
    check(any("net_month_1" in q and " 1 of " in q for q in pn), f"R4: a cent was not seen: {pn}")
    raw = XR.read_result(csv)                             # the defect (the second read's B.2): the default read
    check(not all(str(a) == str(b) for a, b in zip(mine["exact_runs_differing"], raw["exact_runs_differing"])),
          "the control: the default read did not break the text comparison")
    out["q44"] = {"starts": len(mine), "file": csv.name}


# ------------------------------------------------------------------------------------------------ oracles (r1)


def section_oracles() -> None:
    from extended import payout_policy as PP
    from extended import pp_run as RUN

    r = PP.ledger_rules()
    split, fee, cap, mfrac = float(r.profit_split), float(r.payout_fee), float(r.std_cap), \
        float(r.payout_max_frac_of_balance)
    lock_b = PP.lock_balance()

    def acct(b1: float, frac: float, peak: float, later=(), bad: float = 0.0):
        req = frac * min(mfrac * b1, cap) + bad
        cash = [split * req - fee] + [split * q - fee for q in later]
        return SimpleNamespace(gross_paid=req + sum(later), n_payouts=len(cash), consistency_forced=False,
                               payout_cash=tuple(cash), balance_at_first_payout=b1, peak_before_payout=peak)

    def path(*a):
        return SimpleNamespace(funded=tuple(a))

    half = PP.cell_payout_frac("half")
    good = {"half": path(acct(3000.0, half, 3000.0), acct(5000.0, half, 5000.0, later=(600.0,))),
            "ref": path(acct(3000.0, 1.0, 2500.0)), "lock": path(acct(2600.0, 1.0, lock_b + 1.0))}
    for cell, p in good.items():
        t = RUN.GateTally(None, cell)
        t(cell, 0.0, [p])
        try:
            rows = RUN.gate_oracle_rows(dict(design="syn", cell=cell, mode="declared", block="gate"), False, t)
            check(any(x["measure"] == "first_requests_checked" and x["value"] > 0 for x in rows), f"{cell}: none checked")
        except RUN.Refused as exc:
            check(False, f"r1: a correct {cell} request was refused: {exc}")
    for cell, p, what in (("half", path(acct(3000.0, 1.0, 3000.0)), "a full request under half"),
                          ("ref", path(acct(3000.0, half, 3000.0)), "a half request under max"),
                          ("half", path(acct(3000.0, half, 3000.0, bad=1e-6)), "a request off by a millionth"),
                          ("lock", path(acct(2600.0, 1.0, lock_b - 50.0)), "lock's first payout below the lock"),
                          ("half", path(acct(3000.0, half, 3000.0, later=(cap + 10.0,))), "a later request over the cap")):
        t = RUN.GateTally(None, cell)
        t(cell, 0.0, [p])
        try:
            RUN.gate_oracle_rows(dict(design="syn", cell=cell, mode="declared", block="gate"), False, t)
            check(False, f"r1: {what} was not refused")
        except RUN.Refused:
            pass
    big = RUN.GateTally(None, "ref")
    big("point", 0.0, [path(*[acct(9000.0, 1.0, 9000.0, later=(cap,) * 3) for _ in range(40)])])
    try:
        RUN.gate_oracle_rows(dict(design="syn", cell="ref", mode="declared", block="twin"), True, big)
        check(False, "8.2: the twin's martingale bound did not refuse")
    except RUN.Refused:
        pass
    outs = [{"rec": {"pay_cash": [split * 1000.0 - fee]}}, {"rec": {"pay_cash": [split * (cap + 50.0) - fee]}}]
    try:
        RUN.replay_oracle_rows(dict(design="syn"), outs)
        check(False, "8.2: a replay's payout over the cap was not refused")
    except RUN.Refused:
        pass
    rows = RUN.replay_oracle_rows(dict(design="syn"), outs[:1])
    check(any(x["stat"] == "not_checkable" for x in rows), "the replay's unchecked oracles are not stated")
    out["oracles"] = "the gate's request oracles, the twin's bound and the replay's bounds refuse"


# ------------------------------------------------------------------------------------------------ holiday (r2)


def section_holiday() -> None:
    from extended import pp_run as RUN

    dates = [d.date().isoformat() for d in pd.bdate_range("2023-11-01", periods=60)]
    lag, s = 3, 4
    early = {dates[s + 10 - 1], dates[s + 20 - 1]}             # the sessions of requests on campaign days 10 and 20
    arrivals = [10 + lag, 20 + lag, 30 + lag]                  # the third request's session is not early
    rec = {"start_day": s, "start_date": dates[s], "observed": 50, "pass_days": [], "funded_days": [],
           "pay_days": arrivals, "pay_cash": [100.0] * 3, "fees_month": [0.0, 0.0]}
    t = RUN.start_tallies([{"rec": rec}], dates, lag, early)
    check(int(t["requests_dated"].iloc[0]) == 3, f"r2: {int(t['requests_dated'].iloc[0])} requests dated, not 3")
    check(int(t["requests_at_early_close_or_holiday_eve"].iloc[0]) == 2,
          f"r2: {int(t['requests_at_early_close_or_holiday_eve'].iloc[0])} requests on the early sessions, not 2")
    late = {dates[s + 10], dates[s + 20]}                      # the session after each: the old reading's
    t2 = RUN.start_tallies([{"rec": rec}], dates, lag, late)
    check(int(t2["requests_at_early_close_or_holiday_eve"].iloc[0]) == 0, "r2: a request dated one session late")
    cal = {"config/calendar_early_closes.csv": pd.DataFrame({"date": [dates[12], dates[30]],
                                                             "kind": ["early_close", "holiday"]})}
    hs = RUN.holiday_sessions(cal, dates)
    check(hs == {dates[12], dates[30], dates[29]}, f"the holiday sessions {sorted(hs)}")
    out["holiday"] = "each request on its own session"


SECTIONS = {"e2e": section_e2e, "refusals": section_refusals, "waits": section_waits, "authorise": section_authorise,
            "labels": section_labels, "t3": section_t3, "order": section_order, "q44": section_q44,
            "oracles": section_oracles, "holiday": section_holiday}

if __name__ == "__main__":
    SECTIONS[SECTION]()
    out.update({"section": SECTION, "problems": problems[:40], "n_problems": len(problems)})
    print(json.dumps(out, default=str))
