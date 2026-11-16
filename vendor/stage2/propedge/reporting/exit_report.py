"""Stage two's exit (B) report and deck, built from result files (T9, D-138, D-139, D-140).

One data module, as stage one's deliverables had (`vendor/propsim/deliverables/data.js`): `evidence()` reads every
number, every outcome word and every label from a result CSV through `read_result` (so each file's manifest is
verified first), from a result manifest (parameters, notes, the exploratory flag) or from configuration, and
`render_report` / `render_deck` place them. No result number or outcome is typed here; the text around them is.
`scripts/build_report.py` writes `docs/REPORT.md` and `docs/DECK.md`; `propedge/reporting/trace.py` recomputes the
headline numbers independently and looks for them in both documents.
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR, REPO_ROOT, RESULTS_DIR
from propedge.reporting.results import read_manifest, read_result
from propedge.research.atlas_screen import prepare

REPORT_PATH = "docs/REPORT.md"
DECK_PATH = "docs/DECK.md"

from propedge.data.window import D144_DEVELOPMENT_END as _NEW_END, PREVIOUS_DEVELOPMENT_END as _OLD_END  # noqa: E402

_NEW, _OLD = _NEW_END.isoformat(), _OLD_END.isoformat()


def _r(name: str) -> pd.DataFrame:
    return read_result(RESULTS_DIR / f"{name}.csv")


def _m(name: str) -> dict:
    m = read_manifest(RESULTS_DIR / f"{name}.csv")
    return {"parameters": m.parameters or {}, "notes": m.notes or {}, "exploratory": bool(m.exploratory)}


def _label(name: str) -> str:
    """How the report names a source file's standing: its manifest's exploratory flag and status note."""
    m = _m(name)
    status = str(m["notes"].get("status", "")).strip()
    first, _, rest = status.partition(" ")
    if first.isupper():                                   # "EXPLORATORY research screen" -> "exploratory research screen"
        status = first.lower() + (" " + rest if rest else "")
    if m["exploratory"]:
        text = status if status.lower().startswith("exploratory") else ("exploratory" + ("; " + status if status else ""))
    else:
        text = status or "declared development search"
    return f"`results/{name}.csv` ({text})"


def f(x: float, d: int = 4) -> str:
    """A number as the documents print it (an ASCII minus, so the trace check can read it)."""
    return f"{x:,.{d}f}"


def i(x: float) -> str:
    return f"{int(round(x)):,}"


def _count_words(k: int, n: int) -> str:
    return f"all {n}" if k == n else f"{k} of {n}"


# ------------------------------------------------------------------------------------------------ the numbers

def evidence() -> dict:
    ev: dict = {}
    atlas_cfg = yaml.safe_load((CONFIG_DIR / "effect_atlas.yaml").read_text(encoding="utf-8"))

    # data: the atlas's market runs
    cov = []
    for market, rid in atlas_cfg["runs"].items():
        d = prepare(_r("manual_" + rid.replace("-", "_")))
        cov.append({"market": market, "run": rid, "days": len(d), "scoreable": int(d["ok"].sum()),
                    "first": d["date"].min().date().isoformat(), "last": d["date"].max().date().isoformat()})
    ev["coverage"] = cov
    dev = atlas_cfg["development"]
    ev["dev"] = {"start": str(dev["start"]), "end": str(dev["end"]), "screen_end": str(dev["screen_half_end"]),
                 "check_start": str(dev["check_half_start"])}
    oh = atlas_cfg["amendment_d128"]["o_halves"]
    ev["o_halves"] = {k: str(v) for k, v in oh.items()}
    ev["fdr_q"] = float(atlas_cfg["amendment_d128"]["fdr_q"])

    # candidate line 1: the opening-gap reversal (D-112)
    g = _r("gap_gate")
    gate = g[(g["table"] == "gate") & (g["scope"] == "up|whole")].iloc[0]
    grid = _r("gap_grid")
    ev["gap"] = {"n_days": float(gate["n_days"]), "G": float(gate["G"]), "G_lb": float(gate["G_lb"]),
                 "grant_G": float(gate["grant_G"]), "passes": bool(gate["passes"]),
                 "eligible": int(grid["eligible"].astype(bool).sum()), "cells": int(grid["variant"].nunique()),
                 "k": int(_m("gap_gate")["parameters"]["k"]), "label": _label("gap_gate")}

    # candidate line 2: reversion to the opening price on ES (D-116, D-121 to D-123)
    t = _r("test1_rescore")
    dd = t[t["statistic"] == "directional_d"]
    close_d = dd[dd["fill"] == "close"]
    nxt_d = dd[dd["fill"] == "next_open"]
    rises = t["rises_above_test1_upper"].dropna().astype(bool)
    ev["es_openrev"] = {"cells": len(close_d), "negative": int((close_d["mean"] < 0).sum()),
                        "configs": int(close_d[["variant", "entry"]].drop_duplicates().shape[0]),
                        "variants": int(close_d["variant"].nunique()), "entries": int(close_d["entry"].nunique()),
                        "compared_entries": sorted({"baseline": "plain"}.get(e, e) for e in
                                                   t.loc[t["rises_above_test1_upper"].notna(), "entry"].unique()),
                        "scales": int(close_d["scale"].nunique()),
                        "plain_max_hi_close": float(close_d.loc[close_d["entry"] == "baseline", "hi90"].max()),
                        "plain_max_hi_next": float(nxt_d.loc[nxt_d["entry"] == "baseline", "hi90"].max()),
                        "negative_next": int((nxt_d["mean"] < 0).sum()), "cells_next": len(nxt_d),
                        "required": float(_m("test1_rescore")["parameters"]["required_directional"]),
                        "port_check": str(t.loc[t["statistic"] == "D-122", "port_check"].iloc[0]),
                        "compared": len(rises), "rose": int(rises.sum()), "label": _label("test1_rescore")}

    # candidate line 3: the same model on NQ (D-124, D-125)
    q = _r("openrev_nq")
    qn = q[(q["statistic"] == "directional_d") & (q["fill"] == "next_open")]
    qd, qs = qn[qn["entry"] == "baseline"], qn[qn["entry"] == "structural"]
    top_s = qs.loc[qs["hi90"].idxmax()]
    ev["nq_openrev"] = {"plain_cells": len(qd), "plain_negative": int((qd["mean"] < 0).sum()),
                        "plain_below_zero": int((qd["hi90"] < 0).sum()), "plain_max_hi": float(qd["hi90"].max()),
                        "struct_cells": len(qs), "struct_negative": int((qs["mean"] < 0).sum()),
                        "struct_max_hi": float(top_s["hi90"]), "struct_max_n": int(top_s["n"]),
                        "configs": int(qn[["variant", "entry"]].drop_duplicates().shape[0]),
                        "required": float(_m("openrev_nq")["parameters"]["required_directional_part"]),
                        "verdict": str(q.loc[q["section"] == "verdict", "variant"].iloc[0]),
                        "label": _label("openrev_nq")}

    # the effect atlas (D-126, D-128, D-136)
    a = _r("effect_atlas")
    fam = a[a["family"].astype(bool)]
    surv = fam[fam["survivor"].astype(bool)]
    fa = _r("effect_atlas_features")
    fin = fa[fa["in_family"].astype(bool)]
    ev["atlas_h"] = {"size": int(a["family_size"].iloc[0]), "survivors": len(surv),
                     "passed": int(surv["check_pass"].astype(bool).sum()),
                     "survivor_list": [(r.market, r.test, bool(r.check_pass)) for r in surv.itertuples()]}
    fams = {}
    for name in ("F", "R", "O"):
        x = fin[fin["family"] == name]
        fams[name] = {"size": int(x["family_size"].max()), "survivors": int(x["survivor"].astype(bool).sum()),
                      "passed": int(x["check_pass"].astype(bool).sum()), "markets": sorted(x["market"].unique())}
    ev["atlas_f"] = fams
    screened = sorted(set(fam["market"]) | set(fin["market"]))
    described = sorted((set(a["market"]) | set(fa["market"])) - set(screened))
    ev["atlas_markets"] = {"screened": screened, "described": described,
                           "described_tests": int((~a["family"].astype(bool)).sum()
                                                  + (~fa["in_family"].astype(bool)).sum())}
    o01 = fa[fa["test"] == "O01_gamma_intraday_momentum"].set_index("market")
    ev["o01"] = {m: {"est": float(o01.loc[m, "est"]), "p": float(o01.loc[m, "p"]),
                     "check_est": float(o01.loc[m, "check_est"]), "check_p1": float(o01.loc[m, "check_p1"]),
                     "check_pass": bool(o01.loc[m, "check_pass"]), "survivor": bool(o01.loc[m, "survivor"])}
                 for m in ("ES", "NQ")}
    r01 = fin[fin["test"] == "R01_vix_level_vol"]
    ev["r01_passed_markets"] = sorted(r01.loc[r01["check_pass"].astype(bool), "market"])
    ev["atlas_total"] = ev["atlas_h"]["size"] + sum(v["size"] for v in fams.values())
    ev["atlas_labels"] = {"main": _label("effect_atlas"), "features": _label("effect_atlas_features")}

    # measured spreads, day-weighted over years (T2 input; D-135's caveats)
    s = _r("atlas_spreads")
    sp = []
    for m, g_ in s.groupby("market"):
        w = g_["days"]
        sp.append({"market": m, "sp_median": float(np.average(g_["sp_median"], weights=w)),
                   "sp30": float(np.average(g_["sp30_mean"], weights=w)),
                   "spw": float(np.average(g_["spw_mean"], weights=w))})
    ev["spreads"] = sp
    ev["spread_notes"] = _m("atlas_spreads")["notes"]
    ev["spread_label"] = _label("atlas_spreads")

    # the variant log (the configurations the backtest harness recorded)
    lines = [json.loads(x) for x in (RESULTS_DIR / "variants.jsonl").read_text(encoding="utf-8").splitlines() if x]
    ev["variants"] = {"runs": len(lines), "distinct": len({x["variant_id"] for x in lines}),
                      "labels": sorted({str(x.get("prereg_id", "")) for x in lines})}

    # the decision log's extent
    ids = [int(x) for x in re.findall(r"^\| D-(\d+) ", (REPO_ROOT / "DECISIONS.md").read_text(encoding="utf-8"),
                                      re.M)]
    ev["decisions_last"] = max(ids)

    # the scoreboard (R2): every registered run's gate rows side by side, FV3-C's rows the ones to beat
    sb = _r("scoreboard")
    ev["scoreboard"] = sb.to_dict("records")
    ev["scoreboard_label"] = _label("scoreboard")

    # FV1 (D-142) through the D-145 campaign gate, per market, on development data
    ev["fv1"] = {}
    for mk in ("NQ", "ES"):
        c = _r(f"fv1_{mk}_campaign_d156")          # D-156: settled from each trade's MAE (the pre-D-156 file is kept)
        ev["fv1"][mk] = {"gate": bool(c["gate_passed"].any()), "old": bool(c["old_gate_met"].any()),
                         "label": _label(f"fv1_{mk}_campaign_d156")}
    return ev


def _fx(x, d: int = 3) -> str:
    """A scoreboard cell: the number to d places, or "n/a" where the run's engine has no such column."""
    return "n/a" if x is None or x != x else f(float(x), d)


def _ix(x) -> str:
    return "n/a" if x is None or x != x else "$" + i(float(x))


def _scoreboard_table(ev: dict) -> str:
    head = ("| run | candidate | kind | window | verdict | growth on required bankroll, bound | same, point | "
            "required bankroll p90 | break-even denial, bound | days to first payout (median) | payouts a month "
            "(median) | beats FV3-C's row |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for r in ev["scoreboard"]:
        if r["engine"] != "portfolio":
            continue
        rows.append(f"| {r['run']} | {r['candidate']} | {r['kind']} | {r['window']} | {r['verdict']} | "
                    f"{_fx(r['growth_bound'])} | {_fx(r['growth_point'])} | {_ix(r['required_p90'])} | "
                    f"{_fx(r['break_even_denial_bound'])} | {_fx(r['days_to_first_payout_p50'], 1)} | "
                    f"{_fx(r['payouts_per_month_p50'], 2)} | {r['beats_row_to_beat']} |")
    return head + "\n" + "\n".join(rows)


def _scoreboard_notional(ev: dict) -> str:
    out = []
    for r in ev["scoreboard"]:
        if r["engine"] == "notional":
            out.append(f"{r['run']} ({r['candidate']}, {r['kind']}, {r['verdict']}): median log growth on a "
                       f"notional bankroll {_fx(r['notional_growth_min'])} to {_fx(r['notional_growth_max'])}")
    return "; ".join(out)


def _scoreboard_passes(ev: dict, kind: str) -> str:
    runs = [r["run"] for r in ev["scoreboard"] if r["kind"] == kind and str(r["verdict"]).upper().startswith("PASS")]
    return ", ".join(runs) if runs else "none"


def _verdict(passed: bool) -> str:
    return "passes" if passed else "fails"


# ------------------------------------------------------------------------------------------------ the report

def _survivor_lines(ev: dict) -> str:
    out = []
    for market, test, passed in ev["atlas_h"]["survivor_list"]:
        out.append(f"  - {market} `{test}`: {'passed' if passed else 'failed'} its check")
    return "\n".join(out)


def _coverage_table(ev: dict) -> str:
    rows = ["| market | run | days recorded | scoreable days | first | last |", "|---|---|---|---|---|---|"]
    for c in ev["coverage"]:
        rows.append(f"| {c['market']} | {c['run']} | {i(c['days'])} | {i(c['scoreable'])} | {c['first']} | {c['last']} |")
    return "\n".join(rows)


def _spread_table(ev: dict) -> str:
    rows = ["| market | median spread (ticks) | opening 30 min, mean (ticks) | share of minutes wider than one tick |",
            "|---|---|---|---|"]
    for s in ev["spreads"]:
        rows.append(f"| {s['market']} | {f(s['sp_median'], 2)} | {f(s['sp30'], 3)} | {f(s['spw'], 3)} |")
    return "\n".join(rows)


def _o01_line(o: dict) -> str:
    if not o["survivor"]:
        return "did not survive the screen"
    return "passed its check" if o["check_pass"] else "failed its check"


def _mk(ms) -> str:
    return ", ".join(ms)


def render_report(ev: dict) -> str:
    gap, es, nq, h, fa, o = ev["gap"], ev["es_openrev"], ev["nq_openrev"], ev["atlas_h"], ev["atlas_f"], ev["o01"]
    am, dv, oh = ev["atlas_markets"], ev["dev"], ev["o_halves"]
    n_screened = len(am["screened"])
    return f"""# Stage two — interim evidence report

> An exit (B) close was recorded on 2026-09-25 (D-138) and withdrawn the same day (D-141): no complete trading
> model had yet been built and backtested end to end. This report is the evidence so far; the stage continues.

*Generated by `scripts/build_report.py` from the result files named below; do not edit by hand. Every number, outcome
and label is read from a result CSV with a sidecar manifest, that manifest, or the configuration, and the headline
numbers are re-derived by `propedge/reporting/trace.py`. Section 1 is the scoreboard of the registered runs (R2);
sections 2 to 6 are the development-window research of September 2026 ({dv['start']} to {dv['end']}), most of it
**exploratory** by its manifest (each source below is labelled) and none of it a pre-registered test.*

## 1. The answer

Stage two asks whether any candidate **campaign** — a strategy executed realistically, plus a protocol — makes money
over time from the prop firms' contract shape, and, if so, which protocol grows cash fastest under reinvestment
(D-145, D-452). A signal's own edge is a bonus, reported beside the verdict, never required (D-452). **The gate
(D-145 as amended by D-234, D-289, D-312, D-454):** out of sample, the median path's growth on the bankroll the run
itself required, with each R's trade outcomes shifted to the one-sided 95 % lower bound of e, fees and payout latency
applied, the Standard payout path, the Responsible Trading Program's placement off and 0 % payout denial. Denial at
10 / 25 / 50 % and the break-even denial, the placement on, the zero-edge twin and stage one's criterion (propsim
D-47) are reported beside it, never as it.

**The scoreboard** ({ev['scoreboard_label']}): every registered run's gate row, read from its own result file; FV3-C's
row of the same kind is the one to beat (its development baseline for a development run, P-06 for a confirmation).

{_scoreboard_table(ev)}

Before the portfolio engine (D-312), the older engine's runs: {_scoreboard_notional(ev)} — not comparable with the
growth column above.

**Confirmed on held-back data: {_scoreboard_passes(ev, 'confirmation')}.** Development passes:
{_scoreboard_passes(ev, 'development')}. A development pass is not a confirmation: the confirmation window reads a
wider bound (D-451). Earlier, before any registered run, FV1 (D-142) {_verdict(ev['fv1']['NQ']['gate'])} the D-145
gate on NQ and {_verdict(ev['fv1']['ES']['gate'])} it on ES on development data ({ev['fv1']['NQ']['label']};
{ev['fv1']['ES']['label']}).

## 2. What was tried, and what it showed

**2.1 C-007, intraday momentum in four markets (Stage 2B's S-001).** Withdrawn before any confirmation data was
spent (D-103): 2B's own assessment put it below the criterion, and the criterion was confirmed to apply to time-exit
trades as to every other shape (D-104). Development measurements: `results/c007_leg_sd.csv`.

**2.2 Opening-gap reversal on ES (D-105, D-112).** A declared existence gate came first: the effect had to reach
half of the published size (Grant et al. 2005) before any trade variant was searched.
- Gate effect G on {i(gap['n_days'])} gap days: **{f(gap['G'])} %**, one-sided lower bound **{f(gap['G_lb'])} %**,
  against a published size of {f(gap['grant_G'])} % — the gate {'passed' if gap['passes'] else 'failed'}.
- Of the {gap['cells']} declared trade variants (k = {gap['k']}), {'none' if gap['eligible'] == 0 else i(gap['eligible'])} became eligible.
- Source: {gap['label']}; also `results/gap_grid.csv`, `results/gap_null.csv`.

**2.3 Reversion to the opening price on ES (JJ Simon-inspired; D-116, D-118, D-121 to D-123).** A learning exercise
on development data, recorded as exploratory (D-118). {es['configs']} configurations ({es['variants']} stop-and-target variants, each
with {es['entries']} entry rules, plain and structural), each measured at {es['scales']} price scales. Every trade was split into its
directional part (the only possible source of edge) and a symmetric part (what any rule with the same geometry earns).
- Directional part negative in {_count_words(es['negative'], es['cells'])} cells (fill at the signal bar's close) and
  in {_count_words(es['negative_next'], es['cells_next'])} (fill at the next bar's open).
- Largest 90 % upper bound for a plain entry: **{f(es['plain_max_hi_close'])}** (close fill) and
  **{f(es['plain_max_hi_next'])}** (next-open fill), against the **{f(es['required'], 2)}** the criterion needs
  after costs.
- The in-cloud re-score's port check: {es['port_check']}. Correcting the fill moved {es['rose']} of {es['compared']}
  compared cells ({_mk(es['compared_entries'])} entry) above their earlier upper bound.
- Source: {es['label']}.

**2.4 The same model on NQ (D-124, D-125).** NQ's own contract terms (MNQ, a 40-tick floor); {nq['configs']}
configurations, as on ES.
- Plain entry, the verdict-bearing cells: {_count_words(nq['plain_negative'], nq['plain_cells'])} have a negative
  directional part and {nq['plain_below_zero']} lie entirely below zero. The largest upper bound is
  **{f(nq['plain_max_hi'])}** against **{f(nq['required'], 2)}** required. Verdict by the declared rule:
  **{nq['verdict']}**.
- Structural entry, reported but not verdict-bearing (D-124): {nq['struct_negative']} of {nq['struct_cells']} cells
  negative. The widest upper bound, {f(nq['struct_max_hi'])}, comes from {nq['struct_max_n']} trades.
- Correction: D-125 stated seven cells entirely below zero; the file gives {nq['plain_below_zero']} (D-139).
- Source: {nq['label']}.

**2.5 The effect atlas: {i(ev['atlas_total'])} declared tests across {n_screened} markets ({_mk(am['screened'])})
(D-126, D-128, D-136).** A research screen, not a candidate test: every statistic was fixed before any bar was read.
Each family was corrected with Benjamini-Hochberg at q = {f(ev['fdr_q'], 2)}.
- **Screen and check halves.** The D-126, F and R families were screened on {dv['start']} to {dv['screen_end']} and
  checked on {dv['check_start']} to {dv['end']}. The options family used its own halves, {oh['start']} to
  {oh['screen_end']} and {oh['check_start']} to {dv['end']}. Each survivor was checked once.
- **Described, not screened.** {_mk(am['described'])} ({am['described_tests']} tests reported over its short span,
  outside every family).

| family | tests | survived the screen | passed the check |
|---|---|---|---|
| classic intraday effects (D-126) | {h['size']} | {h['survivors']} | {h['passed']} |
| directional features, e.g. strong-closure location (F) | {fa['F']['size']} | {fa['F']['survivors']} | {fa['F']['passed']} |
| size features, for sizing only (R) | {fa['R']['size']} | {fa['R']['survivors']} | {fa['R']['passed']} |
| options gamma ({_mk(fa['O']['markets'])}) (O) | {fa['O']['size']} | {fa['O']['survivors']} | {fa['O']['passed']} |

- The D-126 survivors:
{_survivor_lines(ev)}
- CL's "ES leads" is a **design error**, not an effect. ES's first-30-minute window lies inside CL's rest-of-day
  window, so the test measured same-time co-movement (D-136).
- {'No directional feature (F) survived.' if fa['F']['survivors'] == 0 else f"{fa['F']['survivors']} directional features (F) survived."}
- The options family tested Baltussen, Da, Lammers and Martens (2021): intraday momentum on days after negative
  dealer gamma.
  - NQ: screen slope difference **{f(o['NQ']['est'])}**, check **{f(o['NQ']['check_est'])}** (one-sided p
    {f(o['NQ']['check_p1'])}); {_o01_line(o['NQ'])}.
  - ES: **{f(o['ES']['est'])}**, check **{f(o['ES']['check_est'])}**; {_o01_line(o['ES'])}.
  - 2B translated NQ's size into a trade under the contract's rules and found it near zero net, not a candidate
    (D-137).
- **Size features: real, for sizing only.** The previous day's VIX predicts the next day's realised volatility
  beyond its own history (passed the check in {_mk(ev['r01_passed_markets'])}). They cannot create an edge.
- Sources: {ev['atlas_labels']['main']}; {ev['atlas_labels']['features']}.

## 3. Why these lines came back negative

Stage one's criterion, the gate until D-145, asks for a lot. For an intraday trade that exits on time or at the close, e = 0.10 R net implies an
edge several times stronger than published intraday effects have shown (Stage 2B's analysis, its D-38, confirmed
on the atlas's gamma lead in its D-64). The atlas then looked directly for any simple, declared intraday regularity
in {n_screened} markets and found none that survives correction and a held-out check. The two findings agree: the
data show no intraday edge of the size the prop-firm criterion needs.

## 4. What the data can and cannot show

- **Coverage.** Minute bars and top-of-book quotes from QuantConnect's cloud (free tier); only per-day measurements
  left the cloud (D-120).

{_coverage_table(ev)}

- **Not available.** Order-book depth, market-by-order data, tick data on the free tier, VIX futures (R036). GC
  starts in 2012-11 (D-90), so it was described, never screened.
- **Scale of the search.**
  - The backtest harness recorded {i(ev['variants']['distinct'])} distinct configurations over
    {i(ev['variants']['runs'])} runs (`results/variants.jsonl`). These cover only the searches run through the
    harness: the gap reversal and the ES open-reversion search.
  - Each line above states its own configuration count: {gap['cells']} gap variants, {es['configs']} ES and
    {nq['configs']} NQ open-reversion configurations, and the atlas's {i(ev['atlas_total'])} declared tests.
  - Nothing was pre-registered for confirmation, so there are no confirmation outcomes to report. The C-007 and T7
    drafts were never registered.
- **Known limits.** The development window is five years. Slippage stays an operator-instructed assumption (D-95);
  the measured spreads below are the evidence beside it.

## 5. What stays useful

**Measured spreads** (quoted top-of-book, regular hours, day-weighted over the development years). Source:
{ev['spread_label']}.

{_spread_table(ev)}

Notes from the file's manifest: {ev['spread_notes']['units']}; {ev['spread_notes']['caveat']}.

- **The pipeline.** The manual-run kits with an embedded confirmation-window guard, and in-cloud scoring that
  exports only numbers. Kit failures were kept on record and diagnosed rather than rerun until they passed
  (for example D-109, D-129, D-132, D-134, D-135).
- **The campaign engine.** Lockstep accounts, shared-day draws, tier sizing, replay and a per-trade ledger (T7a,
  D-119; T7b, D-130). It is complete and tested, and consumed by Stage 2C. It was never used for a ranking, because
  no edge passed.
- **Risk predictors for sizing.** The VIX level and gamma sign predict afternoon and next-day volatility (R and O
  families).
- **The confirmation window, {_NEW} onward (D-144), untouched; nothing from {_OLD} on has been read.**

## 6. The record

- Every decision is in `DECISIONS.md`, append-only; the withdrawn exit (B) is D-138, its withdrawal D-141.
- Task list: `NEXT_STEPS.md`. The withdrawn close record: `docs/archive/CLOSED_withdrawn_2026-09-25.md`.
"""


# ------------------------------------------------------------------------------------------------ the deck

def render_deck(ev: dict) -> str:
    gap, es, nq, h, fa, o = ev["gap"], ev["es_openrev"], ev["nq_openrev"], ev["atlas_h"], ev["atlas_f"], ev["o01"]
    am = ev["atlas_markets"]
    return f"""---
title: Stage two — evidence so far
---

<!-- Generated by scripts/build_report.py from result files; do not edit by hand. -->

# Stage two — evidence so far (the stage continues, D-141)

- Gate (D-145 as amended): growth on the required bankroll at the lower bound of e, out of sample, placement off, 0 % denial
- Stage one's criterion (propsim D-47): e ≥ 0.10 R net per trade, one-sided 95 % lower bound ≥ 0.05 R, reported beside it
- Confirmed on held-back data: {_scoreboard_passes(ev, 'confirmation')}; development passes: {_scoreboard_passes(ev, 'development')}
- The slides after the scoreboard are the development-window research of September 2026, mostly exploratory

---

# The scoreboard (R2)

{_scoreboard_table(ev)}

---

# Opening-gap reversal (ES)

- Gate effect {f(gap['G'])} %, lower bound {f(gap['G_lb'])} %, on {i(gap['n_days'])} gap days
- Needed at least half of the published {f(gap['grant_G'])} %: {'passed' if gap['passes'] else 'failed'}
- {'None' if gap['eligible'] == 0 else i(gap['eligible'])} of {gap['cells']} trade variants became eligible

---

# Reversion to the open (ES, then NQ; exploratory)

- ES: directional part negative in {_count_words(es['negative'], es['cells'])} cells; best plain-entry upper bound
  {f(es['plain_max_hi_close'])} against {f(es['required'], 2)} needed
- NQ: {_count_words(nq['plain_negative'], nq['plain_cells'])} plain-entry cells negative; best upper bound
  {f(nq['plain_max_hi'])} against {f(nq['required'], 2)} needed; {nq['verdict']}

---

# The effect atlas: {i(ev['atlas_total'])} declared tests, {len(am['screened'])} markets (exploratory)

| family | tests | survived | passed check |
|---|---|---|---|
| classic intraday | {h['size']} | {h['survivors']} | {h['passed']} (CL's is a design error, not an effect) |
| directional features | {fa['F']['size']} | {fa['F']['survivors']} | {fa['F']['passed']} |
| size (sizing only) | {fa['R']['size']} | {fa['R']['survivors']} | {fa['R']['passed']} |
| options gamma | {fa['O']['size']} | {fa['O']['survivors']} | {fa['O']['passed']} |

{_mk(am['described'])} described over its short span, outside every family

---

# The one directional lead (exploratory)

- NQ intraday momentum after negative dealer gamma: {f(o['NQ']['est'])} on the screen, {f(o['NQ']['check_est'])}
  on the check (p {f(o['NQ']['check_p1'])}); {_o01_line(o['NQ'])}
- ES: {f(o['ES']['est'])} then {f(o['ES']['check_est'])}; {_o01_line(o['ES'])}
- Translated into a trade under the contract's rules: about zero net (2B, D-137)

---

# Why these lines came back negative

- Time-exit intraday trades need an edge several times stronger than published intraday effects to reach
  e = 0.10 R net (2B)
- The atlas found no simple intraday regularity that survives correction and a held-out check

---

# What stays useful

- Measured spreads for {len(ev['spreads'])} markets (T2 cost evidence)
- Volatility predictors for sizing under the daily loss limit
- The run pipeline and the campaign engine (consumed by Stage 2C)
- NQ's held-back window is spent (P-06, P-10); NQ from 2026-07-17 is reserved for the next confirmation
"""
