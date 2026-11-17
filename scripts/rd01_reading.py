"""RD-01's reading (`prereg/RD-01_firm_contracts.md`): a described reading, unnumbered (E-023 (1)) -- other firms'
contracts on the registered trades, the user scorecard per plan paired with Topstep by month, and beside it E-007
(e)'s readings, the denial ladder and the gate. Nothing is chosen, nothing carried; no pass line.

    python scripts/run_clean.py --name rd01-reading --task <Q> --hours <h> --mem-gb 3.5 -- \\
        python scripts/rd01_reading.py
    python scripts/rd01_reading.py --plan          # light: prints the guard's findings and what would run; reads nothing

**The run is section 15's one run.** Its three judged-block purposes (section 6 item 6) are taken **in order**, each
authorised through `extended.reader.authorise_engine_read` (declaration `prereg/RD-01_firm_contracts.md`, pinned; the
development window; the engine's files) **immediately before its stage**, so a refusal leaves the later purposes
unread: `firm_scorecard` (the 30 replays of 7.3, or 34 when P-16's count of 5.5 is not zero -- decided from the trades'
times before any outcome), `firm_ladder_beside` (the 27 denial-ladder replays), `firm_gate_beside` (the 16 gates with
their zero-edge twins). A purpose ledgered by an earlier clean run is refused unless `--repeat E-NNN` names a decision
row naming the declaration (the reader's once-rule).

**Before anything is read** (9.1, R3, D1): the decision log's identity tokens have no breach and every identity the
reading waits on is held -- by the shared parser, `extended.identity_tokens.held` (Q-110) through
`extended.identity_rows`: a row whose third cell begins with the positional holding (identity-holds: <id> in
documents) at a sha that is the commit being run or an ancestor of it, none of that identity's covered paths changed
since (`waited()`, each by `cover`: Q-80's 500-path gate identities and Q-93's U1-adapter identity exactly as
`extended.identity_cover` declares them, RD-01's identity stage `identity/firms_identity.py` as Q-104 by the same rule
-- the package root, `config/` whole, both vendored manifests, its script and its imports' closure by the shared
model, held to it by `identity_cover.uncovered`: V2, V4); the
declaration's text is the one its pinning row pins; no E-015 limit row exists that this runner would not apply; and
all three purposes pass `reader.authorise`, which reads and writes nothing, before the first is ledgered (m7). Each
check is printed by `--plan`. Otherwise exit 3.

**Order** (15): the identities first (above); then, per cell, 9.1 items 4 and 5, **9.2's oracles** and **9.3's
mechanics**, then the reading; **any refusing check stops the run at once** (r5), nothing written, exit 3.

**What it writes** (through `extended.results`, each file with its manifest; only inside a clean run; never over an
existing file):

* `results/fc_reading.csv` -- sections `identity` (the waited identities' rows, the pin, items 4-5 and A-9's equality
  per cell), `oracle` (9.2 per cell, the twins' oracles), `mechanics` (9.3: G-3's count by release and year, the
  offered trades' zero checks, every cell's counts by block), `scorecard` (U1's card, E-007 (e)'s measures, the path
  and response measures per run, arm and block, and one row a start: the journey variables, 10.1 item 6's fields),
  `paired` (each plan less TS by month and block with 10.2's reading; the paired card), `diverge` (10.1 item 6),
  `grid` (A-10's price grid and break-even prices), `ladder` (the denial ladder's readings and one row a start),
  `coverage` (10.2 item 7 at every setting read);
* `results/fc_gate.csv` -- the 16 corners' gate rows (point, bound, the zero-edge twin), the paths paired with TS's
  registered ones, and each path's row;
* `results/fc_menu.csv` -- the menu (`extended.firm_menu`): a declared light step on the two files just written,
  read back through their manifests' hashes -- flags, labels, items 3, 4 and 10.

Every row carries "described, not carried"; every manifest the pinning row, the waited identities' rows, the run
counts as run, each plan's cost schedule and table inputs, every seed (the reserved and retired with them), section 5's
readings and their labels, each plan's record entries with their dates read, the sha256 of
`vendor/DATA_MANIFEST_stage2.sha256`, `prereg_id` RD-01 and `exploratory=False`.

**One pass, its cost measured** (the third read's (g)): each cell runs once through A-9, its own replays' records kept
in-process (`firm_reading.run_cell`), no second replay; the break-even search shares one recomposition a price with
the grid and reads a midpoint's side from the grid where the measure's fall in price decides it (the same answers);
Quick Pay's gates at one worker (its per-run class does not pickle; two workers would need an identity RD-01 has not
declared). `scripts/rd01_cost_probe.py` measures seconds a start-run and peak memory per stage on synthetic campaigns
of the window's length, no bars read; the lead's hand-back carries its table. Each cell's rows leave memory as it
finishes (a spill under the run's own folder, read back once at the end), and each finished cell is kept outside the
checkout keyed by the commit, so a restart resumes (a restart is a rerun under the once-rule: `--repeat`).
"""
from __future__ import annotations

import argparse
import dataclasses
import gc
import hashlib
import os
import pickle
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import RUNS_DIR, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import firm_menu as FM  # noqa: E402
from extended import firm_reading as R  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import identity_rows as IR  # noqa: E402
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_readings as UR  # noqa: E402

SCRIPT = "scripts/rd01_reading.py"
VENDOR = ROOT / "vendor" / "stage2"
FILES = ("fc_reading", "fc_gate", "fc_menu")
SECTIONS = ("identity", "oracle", "mechanics", "scorecard", "paired", "diverge", "grid", "ladder", "coverage")
READING = ("DESCRIBED (RD-01, E-023 (1)): other firms' contracts on the registered trades; no pass line, nothing chosen "
           "or carried; 0 % denial and the placement off in the headline (E-008)")
LADDER_PLANS = ("LU", "DT", "FP", "QP")
PATHS = 500
#: the build's readings printed in every manifest (the red team's n1, n2, n4, n8; E-092)
CONVENTIONS = {
    "dt_inactivity": "windows of 30 calendar days from the purchase (an evaluation) or the activation (a Pro account): "
                     "the first [that date, that date + 29 days]; a later purchase dated its session's date, a day-0 "
                     "purchase the calendar day before the first session; the account ends at the first close at which "
                     "a window has ended, or will end before the next session, without a $200 day; 21 sessions in the "
                     "gate",
    "dt_30_percent": "the cycle's best day and profit as the engine's Consistency path keeps them (w_best, w_profit): "
                     "the request day's P&L out of the cycle",
    "qp_ceiling": "read at the close (an intraday crossing that falls back by the close is not a pause)",
    "dt_inactivity_flag": "an evaluation closed for inactivity carries the engine's `abandoned` flag; counted as "
                          "`inactive_closed`, never as a cash refusal",
    "qp_bracket": "A-7 classifies won-at-R on the run's point outcomes on every arm (M3)",
    "a4_logging": "a day-logging trade at one micro under the design's own stand-aside (refused if its share is "
                  "positive, n4), its intended risk the table's",
    "month_9": "6 item 4 names no horizon for month 9: read at 252 sessions, the conservative choice (n1)",
    "counts_blocks": "9.3's counts by block: all -- every start's long replay; early and late -- u_select.block at the "
                     "long replay's 252 sessions, so no early count reads a 2024 session",
    "g10": "G-10: sessions with no trade per funded account (its live sessions less its trading ones); idle 30 calendar "
           "days -- at least the record's 30 days with no trade between its activation, its trading days and its end "
           "(dates at least 31 days apart, n3); drained -- an account left open at the replay's end, not breached and "
           "not ended by a ceiling, a fifth request or a closure, whose cushion at its last close is below one micro at "
           "the smallest stop of the design's offered trades (m2)",
    "g12": "G-12: the trades the router dealt to a DayTraders session's later slots after the daily limit ended it",
    "fp_forced_signals": "on a Fast Pass session forced untraded (A-5) the router passes the account over: the day's "
                         "offered signals dealt to some account and to none are counted (the forced account's own "
                         "signals are not recorded apart by the engine)",
    "fp_uncapped": "the trades an uncapped Fast Pass ladder (two contracts plus one per $2,000, no cap) would size "
                   "differently at the session's balance, the trade's own intended risk, allowance and room; its "
                   "control: the same rebuild under the plan's own ladder gives every trade its own contracts, refusing "
                   "(m3)",
    "items_4_5_ladder": "9.1 item 5 on every ladder replay (A-9's own account counts); item 4 on the ladder's DayTraders "
                        "cells (their replays read for A-10); for the others item 4 is checked on the scorecard's "
                        "replays of the same classes (n6: the ladder's denials change which accounts exist, so its "
                        "trades are not the scorecard's)",
    "twin_interval": "9.2's twin oracles: a ratio of sums over the gate's paths with its delta-method standard error, "
                     "refusing only beyond the two-sided 99.9 % normal interval; the pass rate over resolved "
                     "evaluations (passed or failed), the others counted beside (m5)",
    "twin_fees": "the zero-edge twin priced at the log's own per-trade fees (no plan schedule re-prices it), so its game "
                 "is exactly fair and 9.2's ceilings test the contract's mechanics alone (m4)",
    "single_pass": "one pass through A-9 per cell (the third read's (g)): A-9's own replays kept in-process -- the long "
                   "run's ledger through A-9's Q-94 recorder seam, the exact-length runs as user_beside.replay returns "
                   "them -- read for 9.1 items 4-5, 9.2, 9.3 and A-10; no second replay; each start's output composed "
                   "again from them must be A-9's bit for bit; the recorder's own per-start checks read and refusing "
                   "(V5); TS-16 and TS-14 on this route held to U1's registered start rows by E-010's comparison, "
                   "both arms, every start, before any plan cell (7.1, V1)",
    "break_even": "10.1 item 9's break-even: bisection on $0 to $250 to a cent, as built; one recomposition a price "
                  "shared by the grid and the three searches, and a midpoint's side read from the grid where the "
                  "measure's fall in price decides it -- the same answers as the plain search (the toys)",
    "u1_reported": "10.1 item 1's S2, S3d, S6 and Q by U1's own readings (user_journey.metric_rows through Views, a "
                   "start's exact-length run read where it differs), each on its block at its own horizon; S6's part "
                   "across runs by user_journey.luck_rows over each stream and arm's runs (M1)",
    "menu_windows": "the menu's 10.2 readings window each block's starts by position (a start with no value stays in "
                    "its window; each kept window's mean is over its defined values; a kept window with none prints no "
                    "interval); the coverage of every block's (h, n_w) computed in the run (m6)",
    "verdict_delta": "the TradeDay verdict arm shifted by the campaign's registered lb - e and lb_by_rr - e_by_rr "
                     "(captured as U1's builder makes the arm), refused unless every untouched day is U1's bit for bit "
                     "(r6)",
}
#: section 12's block, every seed with its status and what it draws (the reserved and retired ones never drawn)
SEED_BLOCK = {R.F.LADDER_SEED + i: st for i, st in enumerate(
    ("in use: the denial ladder's per-start path seeds (A-9's seed base, 10.1 item 7)",
     "in use: 10.2 item 7's synthetic coverage series, and T-9",
     "in use: the build's toy campaigns (T-1 to T-7, T-10, T-12 to T-14)",
     "reserved, unused: never drawn, not reassigned (it was Q-16's comparison, dropped)",
     "reserved, unused", "reserved, unused", "reserved, unused", "reserved, unused",
     "retired, found in use: a red team's scratch seed (docs/reviews/DRAFT_F-P_payout_policy_2026-11-16.md)",
     "retired, found in use: a red team's scratch seed (the same review)"))}
#: the identities the reading waits on (R3; 15's waits), each with the files whose code it held on
CODE = ("scripts/rd01_reading.py", "extended/__init__.py", "extended/firm_reading.py", "extended/firm_menu.py",
        "extended/firms.py", "extended/firm_accounts.py", "extended/firm_terms.py", "extended/firm_counts.py",
        "extended/firm_uncertainty.py", "extended/identity_rows.py", "extended/identity_tokens.py",
        "extended/user_beside.py",
        "extended/replay_records.py", "extended/place_records.py", "extended/user_readings.py",
        "extended/user_measures.py", "extended/gate.py", "extended/campaign.py", "extended/walker.py",
        "extended/reader.py", "extended/results.py", "extended/calendar_fomc_minutes.py",
        "extended/calendar_early_closes.py", "identity/user_beside_identity.py", "config/rules_extended.yaml",
        "config/calendar_fomc_minutes.csv", "config/calendar_early_closes.csv", "prereg/RD-01_firm_contracts.md",
        "vendor/MANIFEST_stage2.sha256", "vendor/DATA_MANIFEST_stage2.sha256")
#: the waits and their covers (9.1, 15's waits; E-113, E-117, Q-111): the shared identities by
#: `extended.identity_cover.cover`, RD-01's own by the same rule (`identity_rows.cover`, `identity_rows.waited`)
cover = IR.cover
waited = IR.waited


def _commit() -> str:
    out = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or "nocommit"


def code_blobs() -> dict[str, str]:
    """{path: git blob id} of each file the reading runs, hashed from the file on disk (`git hash-object`)."""
    out = {}
    paths: list[str] = []
    for rel in dict.fromkeys(CODE + tuple(f for w in waited() for f in w.files)):
        if rel.endswith("/"):                             # a covered folder: every tracked file under it
            ls = subprocess.run(["git", "ls-files", rel.rstrip("/")], cwd=ROOT, capture_output=True, text=True)
            paths += [x for x in ls.stdout.splitlines() if x.strip()]
        else:
            paths.append(rel)
    for rel in dict.fromkeys(paths):
        r = subprocess.run(["git", "hash-object", str(ROOT / rel)], cwd=ROOT, capture_output=True, text=True)
        out[rel] = r.stdout.strip() if r.returncode == 0 else "missing"
    return out


# ------------------------------------------------------------------------------------------------ the guards


def identity_problems(repo: Path = ROOT, decisions_text: str | None = None) -> tuple[list[str], dict[str, Any]]:
    """R3: every waited identity's row (`extended.identity_rows`), or why not; and V4: RD-01's own cover meets the
    shared rule (`identity_cover.uncovered`), refusing otherwise."""
    probs, found = IR.waited_problems(repo, waited(), decisions_text=decisions_text)
    return IR.cover_problems() + probs, found


E015_ROW = re.compile(r"^\|\s*(E-\d+)\s*\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*e015-limits:")


def e015_problems(repo: Path = ROOT) -> list[str]:
    """10.1 item 11 and E-104: limits approved before the run's commit flag the menu, read only from a row beginning its
    third cell `e015-limits:`. This runner builds no limit flags, so such a row refuses the run until it does (a build
    change); with none, the menu says none was approved."""
    rows = [m.group(1) for m in map(E015_ROW.match, reader._decisions(repo).splitlines()) if m]
    return [f"E-015's limits are approved ({', '.join(rows)}) and this runner applies none: the menu's limit flags "
            "need building before the run"] if rows else []


def precheck(repeat: str | None) -> list[str]:
    """m7: every purpose authorised in order without a read (`reader.authorise` reads and writes nothing), so a purpose
    that would be refused stops the run before the first is ledgered."""
    out = []
    for purpose in R.PURPOSES:
        try:
            reader.authorise(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=R.DECLARATION,
                             repeat=repeat, what=f"RD-01's {purpose} (pre-check)")
        except (reader.ReadRefused, ValueError, FileNotFoundError) as exc:
            out.append(f"{purpose}: {exc}")
    return out


def pin_row(repo: Path = ROOT) -> tuple[dict[str, str] | None, list[str]]:
    """The decision row that pins the declaration, and its sha256; refused unless the file's LF text hashes to it."""
    text = reader._decisions(repo)
    rel = R.DECLARATION
    for line in text.splitlines():
        m = reader.ROW.match(line)
        if not m:
            continue
        for p, h in reader.PIN.findall(line):
            if p == rel:
                have = reader.sha256_lf(repo / rel)
                if have != h:
                    return None, [f"{rel} hashes to {have[:12]}, its pinning row {m.group(1)} to {h[:12]}"]
                return {"row": m.group(1), "sha256": h}, []
    return None, [f"no decision row pins {rel}"]


def data_manifest_sha256(repo: Path = ROOT) -> str:
    p = repo / "vendor" / "DATA_MANIFEST_stage2.sha256"
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "missing"


APPENDIX_ROW = re.compile(r"^\| `([^`]+)` \| (stage2|lucid|record) \| ([a-z_]+) \|")


def record_entries(repo: Path = ROOT) -> tuple[list[dict[str, Any]], list[str]]:
    """Appendix R's every key with its record's status and date read (15: each plan's record entries with their dates
    read), and the keys whose record status is not the appendix's (refusing: the record changed under the reading)."""
    import yaml

    text = (repo / R.DECLARATION).read_text(encoding="utf-8")
    rec = {str(e["key"]): e for e in yaml.safe_load(T.RECORD.read_text(encoding="utf-8"))["rules"]}
    st2 = yaml.safe_load(T.STAGE2_LEDGER.read_text(encoding="utf-8"))["rules"]
    lu = yaml.safe_load(T.LUCID_LEDGER.read_text(encoding="utf-8"))["rules"]
    out, bad = [], []
    for line in text.split("## Appendix R", 1)[-1].splitlines():
        m = APPENDIX_ROW.match(line)
        if not m:
            continue
        key, src, status = m.groups()
        e = {"stage2": st2, "lucid": lu, "record": rec}[src].get(key)
        if e is None:
            bad.append(f"{key}: not in its record ({src})")
            continue
        plan = ("TS" if src == "stage2" else "LU" if src == "lucid" or key.startswith("lucid.") else
                "DT" if key.startswith("daytraders.") else "FP" if ".fastpass_" in key else
                "QP" if ".quickpay_" in key else "FP, QP")
        out.append({"key": key, "source": src, "plan": plan, "status": e.get("status"),
                    "date_read": str(e.get("date_read")), "article_id": str(e.get("article_id", ""))})
        if str(e.get("status")) != status:
            bad.append(f"{key}: the record reads {e.get('status')!r}, Appendix R {status!r}")
    return out, bad


def plan_manifest(base_rules: Any) -> dict[str, Any]:
    """Each plan's cost schedule (4.8), table inputs (4.9: what its accounts hand the table, and its `Rules` winning-
    day fields as the run sets them) and request rule (2.3, 5.3, 5.6)."""
    inputs = {
        "TS": "the engine's own win_days, since_pay and request_day_next (REQUEST_AFTER_5PM)",
        "LU": "the engine's own, with Lucid's $1 net in its gate; request_day_next 0 (no session excluded)",
        "DT": "Qualifying Days q, 0 to 8 (a $200 day whose close has the cycle's best day at most 30 % of the cycle's "
              "profit, the request day excluded); win_days min(5, max(0, q - 3)); 4 while q = 8 and the balance is "
              "below $2,600 or the 30 % rule blocks; request_day_next the engine's; an evaluation at target with "
              "Qualifying Days owed reads the table's lookup as it stands",
        "FP": "the engine's own; win_days 4 while five days are counted and the 45 % rule blocks; request_day_next the "
              "engine's, the session also untraded (A-5); an evaluation at target with days owed takes at most one "
              "trade a session at one micro and the table's R (A-4)",
        "QP": "every close: no days counted, win_days 5 from the account's second session (0 before), request_day_next "
              "0; the reference's cadence: the engine's own count of $150 days since the last request, every session "
              "counted; an evaluation at target with days owed as Fast Pass's (A-4)",
    }
    out: dict[str, Any] = {}
    for plan in T.PLANS:
        corners = [T.STRICT, T.LENIENT] if plan != "TS" else ["reference"]
        sched = {c: list(T.fee_schedule(plan, T.settings_for(plan, c).fee_basis)) for c in corners} \
            if plan == "DT" else {"all": list(T.fee_schedule(plan))}
        fields = {}
        if plan in ("DT", "FP", "QP"):
            rr = R.F.plan_rules(base_rules, T.settings_for(plan, T.STRICT))
            fields = {"std_winning_days": int(rr.std_winning_days), "std_winning_day_min": float(rr.std_winning_day_min)}
        elif plan == "TS":
            fields = {"std_winning_days": int(base_rules.std_winning_days),
                      "std_winning_day_min": float(base_rules.std_winning_day_min)}
        out[plan] = {"cost_schedule_round_turn_micro_mini": sched, "table_inputs": inputs[plan],
                     "rules_winning_day_fields": fields or "Stage 2's lucid_rules (5, $150)",
                     "request_rule": ("min(0.5 B, $2,000) cut to the plan's cap, remaining-balance rule and increment; "
                                      "none below its minimum" + ("; QP-16-req: the same at the reference's cadence"
                                                                  if plan == "QP" else ""))}
    return out


def readings_manifest() -> dict[str, Any]:
    """Section 5's readings: the declared constants (each with its line of 5.2), every run's settings, the labels."""
    return {"declared": {k: {"value": v.value, "cite": v.cite} for k, v in T.DECLARED.items()},
            "runs": {r.name: dataclasses.asdict(T.settings_for(r.plan, r.corner, r.flip)) for r in T.RUNS},
            "labels": {k: list(v) for k, v in FM.LABELS.items()}, "e015": FM.E015}


class Resume:
    """Each finished cell kept outside the checkout, keyed by the commit (D-540's pattern)."""

    def __init__(self, folder: Path | None):
        self.folder = folder
        if folder is not None:
            folder.mkdir(parents=True, exist_ok=True)

    def get(self, key: str):
        p = None if self.folder is None else self.folder / (key.replace("|", "__") + ".pkl")
        if p is None or not p.is_file():
            return None
        with p.open("rb") as f:
            return pickle.load(f)

    def put(self, key: str, value) -> None:
        if self.folder is None:
            return
        p = self.folder / (key.replace("|", "__") + ".pkl")
        tmp = p.with_suffix(".tmp")
        with tmp.open("wb") as f:
            pickle.dump(value, f)
        os.replace(tmp, p)


class Spill:
    """Each finished cell's rows, spilled out of memory as it finishes (m7) -- one pickled frame a cell under `folder`
    (the run's own, emptied when the run starts), or kept in memory when `folder` is None (the toys) -- and read back
    once, at the end, as one frame."""

    def __init__(self, folder: Path | None = None):
        self.folder = folder
        self.parts: list[Any] = []
        if folder is not None:
            folder.mkdir(parents=True, exist_ok=True)
            for old in folder.glob("*.pkl"):
                old.unlink()

    def add(self, rows: list[dict]) -> None:
        if not rows:
            return
        df = pd.DataFrame(rows)
        if self.folder is None:
            self.parts.append(df)
            return
        path = self.folder / f"{len(self.parts):05d}.pkl"
        df.to_pickle(path)
        self.parts.append(path)

    def frames(self):
        for x in self.parts:
            yield pd.read_pickle(x) if isinstance(x, Path) else x

    def frame(self) -> pd.DataFrame:
        return pd.concat(list(self.frames()), ignore_index=True, sort=False) if self.parts else pd.DataFrame()


# ------------------------------------------------------------------------------------------------ the scorecard


def _tag(rows: list[dict], **head: Any) -> list[dict]:
    """Rows under a run's head: the head wins over a reading's own `kind` (U1's response kind is kept apart)."""
    out = []
    for r in rows:
        r = dict(r)
        if "kind" in r:
            r["response_kind"] = r.pop("kind")
        out.append({**r, **head})
    return out


def _ur_rows(rows: list[dict], section: str) -> list[dict]:
    """U1's summary rows under 15's section: their own section is the subsection (`card` for U1's card)."""
    return [{**{k: v for k, v in r.items() if k != "section"}, "section": section,
             "subsection": "card" if r["section"] == "scorecard" else r["section"]} for r in rows]


def _start_rows(table: pd.DataFrame, stats: dict[int, dict[str, float]], section: str,
                recs: list[dict] | None = None) -> list[dict]:
    """One row a start: U1's start table, 10.1 item 6's fields (money to the cent), and U1's own months ahead over the
    first three months (`u_select.months_ahead`, through `Views`: the card's P on the start's year, m3)."""
    from propedge.research import u_select as S

    ahead = {} if recs is None else S.months_ahead(recs)
    t = UR.rounded(table)
    out = []
    for r in t.to_dict("records"):
        x = stats.get(int(r["start_day"]), {})
        r = {k: v for k, v in r.items() if k not in ("design",)}
        r["response_name"] = r.pop("response")
        r["months_ahead_u1"] = float(ahead.get(str(r["start_date"]), float("nan")))
        out.append({"section": section, "subsection": "start", **r,
                    **{k: (round(float(x[k]), 2) if k.startswith(("fees_", "payouts_g", "payouts_n", "realised"))
                           else float(x[k])) for k in R.DIVERGE if k in x}})
    return out


def scorecard_reading(streams: dict[str, dict[str, Any]], runs: list[T.Run], starts: int | None, *,
                      coverage: bool = True, coverage_series: int = R.COVERAGE_SERIES, resume: Resume | None = None,
                      spill: Spill | None = None, reference: Any = None, log=print) -> tuple[Spill, dict[str, Any]]:
    """The 7.3 runs, TS's first on each stream (its cells are the pairing's other side): (the spilled rows, what ran).
    Each cell's rows leave memory as it finishes (m7); TS's cells keep only what the pairing reads. **V1 (7.1):** each
    TS reference cell, on the reading's own route, must reproduce U1's registered start rows -- `reference(design, arm,
    outs, n_window, starts)` returns E-010's comparison's problems (`user_beside_identity.u1_compare_outs` in the run),
    refusing, before any plan's cell is computed. Raises `firm_reading.Refused` at the first refusing problem (r5)."""
    import user_journey as UJ

    resume = resume or Resume(None)
    spill = spill if spill is not None else Spill(None)
    off = B.BY_NAME["off"]
    rows: list[dict] = []
    ctxs = {}
    u1_by: dict[tuple[str, str], dict[str, list[dict]]] = {}
    R._COVERAGE.update(resume.get("coverage|settings") or {})
    for name, st in streams.items():
        pt = st["jobs"]["point"]
        rows += _tag(R.tier1_count_rows(name, pt["blocks"], pt["dates"]), section="mechanics", stream=name)
        rows += [{"section": "mechanics", "subsection": "offered", "stream": name, "measure": k, "stat": "value",
                  "value": float(v)} for k, v in R.exit_problems(pt["blocks"], pt["dates"]).items()]
        ctxs[name] = R.stream_context(name, pt)
        for arm, dl in (st.get("delta") or {}).items():
            bad = R.delta_problems(pt["blocks"], st["jobs"][arm]["blocks"], dl)
            if bad:
                raise R.Refused(f"r6: {name} {arm}: " + "; ".join(bad))
    conditional = R.p16_count_nonzero([r for r in rows if r.get("subsection") == "tier1_count"])
    spill.add(rows)
    runs = [r for r in runs if not r.conditional or conditional]
    runs = sorted(runs, key=lambda r: (r.plan != "TS",))
    ts_cells: dict[tuple[str, str], dict] = {}
    pending_grid: dict[tuple[str, str, str], tuple[list[dict] | None, float]] = {}
    for run in runs:
        s = T.settings_for(run.plan, run.corner, run.flip)
        name = R.stream_of(run)
        st = streams[name]
        for arm in UJ.ARMS:
            key = f"{run.name}|{arm}"
            got = resume.get(key)
            t0 = time.time()
            head = {"run": run.name, "plan": run.plan, "stream": run.stream, "arm": arm, "corner": run.corner,
                    "flip": run.flip or "", "kind": run.kind, "request_rule": s.request or ""}
            if got is None:
                job = st["jobs"][arm]
                chosen = UJ.start_choice(len(job["blocks"]), starts)
                blocks, point_ref, a11 = R.arm_inputs(st["jobs"]["point"], job, s, arm,
                                                      (st.get("delta") or {}).get(arm))
                cjob, kw = R.cell_job(job, s, blocks)
                ts = ts_cells.get((name, arm))
                grid_cell = run.plan != "TS" and (run.kind == "corner" or run.flip == "price")
                cell = R.run_cell(name, arm, off, cjob, s, chosen, kw, point_ref, direct=True, ctx=ctxs[name],
                                  ts=None if ts is None else ts["compact"], keep_ts=run.plan == "TS",
                                  keep_directs=run.plan == "DT" or grid_cell)
                if cell["problems"]:
                    raise R.Refused(f"{key}: " + "; ".join(cell["problems"][:6]))
                outs = R.reading_outs(cell, name, arm, off, s)
                srows, table = UR.summary(name, arm, off, outs, blocks=UR.READING_BLOCKS)
                probs = UR.consistency_problems(srows, outs, key, blocks=UR.READING_BLOCKS)
                if probs:
                    raise R.Refused("; ".join(probs[:6]))
                v1 = []
                if run.plan == "TS":                    # V1: the reference reproduces U1's registered rows, refusing
                    if reference is None:
                        raise R.Refused(f"{key}: no U1 reference to hold TS's registered rows to (7.1, V1)")
                    bad = reference(name, arm, outs, len(job["blocks"]), starts)
                    if bad:
                        raise R.Refused(f"{key}: TS on the reading's route is not U1's registered start rows (7.1): "
                                        + "; ".join(bad[:6]))
                    v1 = [{"section": "identity", "subsection": "u1_reference", "measure": "u1_start_rows",
                           "stat": "starts", "value": float(len(outs)),
                           "note": "held (7.1, V1): E-010's comparison of every start's row on the reading's route"}]
                recs = [o["rec"] for o in outs]
                u1 = R.u1_reported_rows(recs)
                crows = _tag(_ur_rows(srows, "scorecard"), **head)
                crows += _tag([{"section": "scorecard", **r} for r in u1], **head)            # M1
                crows += _tag(_start_rows(table, cell["stats"], "scorecard", recs), **head)
                crows += _tag([{"section": "mechanics", **r} for r in R.count_rows(cell["stats"], recs)], **head)
                crows += _tag([{"section": "mechanics", "subsection": "a11", "measure": f"a11_{k}", "stat": "value",
                                "value": float(v)} for k, v in a11.items()], **head)
                crows += _tag([{"section": "identity", "subsection": "items_4_5", "measure": k, "stat": "value",
                                "value": float(v)} for k, v in cell["checks"].items()] + v1, **head)
                n_req = sum(float(x.get("oracle_requests_checked", 0)) for x in cell["stats"].values())
                n_fee = sum(float(x.get("oracle_trades_fee_checked", 0)) for x in cell["stats"].values())
                crows += _tag([{"section": "oracle", "subsection": "replay", "measure": m, "stat": "checked",
                                "value": v, "note": "held (9.2): every one inside its bounds"}
                               for m, v in (("requests_bounds_and_split", n_req), ("trade_fees_schedule", n_fee),
                                            ("fees_by_kind_total", float(len(cell["stats"]))))], **head)
                if s.plan == "QP":
                    crows += _tag([{"section": "oracle", "subsection": "replay", "measure": "qp_floor_every_close",
                                    "stat": "breaches", "value": 0.0, "note": "held (9.2)"}], **head)
                got = {"rows": crows, "recs": recs, "head": head, "stats": cell["stats"], "u1": u1,
                       "compact": cell["ts"] if run.plan == "TS" else None}
                if run.plan != "TS":
                    ts = ts_cells[(name, arm)]
                    got["rows"] += _tag([{"section": "paired", **r} for r in
                                         R.paired_rows(recs, ts["recs"], coverage=coverage,
                                                       coverage_series=coverage_series)
                                         + R.paired_scorecard_rows(recs, ts["recs"])], **head)
                    got["rows"] += _tag([{"section": "paired", **r, "stat": side, "milestone": r["stat"]}
                                         for side, mine, other in (("plan", recs, ts["recs"]), ("ts", ts["recs"], recs))
                                         for r in R.u1_reported_rows(mine, paired_with=other)], **head)   # M1
                    got["rows"] += _tag([{"section": "diverge", **r} for r in
                                         R.diverge_rows(cell["stats"], ts["stats"], recs)], **head)
                    if run.kind == "corner" or run.flip == "price":
                        grows, at = R.grid_rows(cell, name, arm, off, s, ts["recs"])
                        got["rows"] += _tag([{"section": "grid", **r} for r in grows], **head)
                        if run.corner == T.STRICT and run.flip is None and run.plan in ("DT", "FP", "QP"):
                            other = T.price_ends(run.plan)[1]
                            got["grid_other"] = (at.get(other), other)        # r2: kept for a restart
                        if run.flip == "price":
                            pend = pending_grid.pop((run.plan, name, arm), None)
                            if pend is None:
                                raise R.Refused(f"{key}: A-10's check has no strict corner's arithmetic to compare")
                            gp = R.grid_problems({pend[1]: pend[0]}, {"outs": outs}, pend[1])
                            if gp:
                                raise R.Refused(f"{key}: A-10 " + "; ".join(gp[:6]))
                            got["rows"] += _tag([{"section": "oracle", "subsection": "a10", "measure":
                                                  "grid_reproduces_the_price_run", "stat": "starts",
                                                  "value": float(len(outs)), "note": "held (10.1 item 9)"}], **head)
                got["coverage"] = dict(R._COVERAGE)
                resume.put(key, got)
                del cell
            R._COVERAGE.update(got.get("coverage") or {})
            if got.get("grid_other") is not None:
                pending_grid[(run.plan, name, arm)] = got["grid_other"]
            if run.plan == "TS":                         # what the pairing reads, the rows not held (m7)
                ts_cells[(name, arm)] = {k: got[k] for k in ("recs", "stats", "compact")}
            u1_by.setdefault((run.stream, arm), {})[run.name] = got.get("u1") or []
            spill.add(got["rows"])
            del got
            log(f"timing: {run.name} {arm}: {time.time() - t0:.0f} s", flush=True)
            gc.collect()
    for (stream, arm), by_run in sorted(u1_by.items()):             # M1: S6 across each stream and arm's runs
        spill.add(_tag([{"section": "scorecard", **r} for r in R.luck_across(by_run)], stream=stream, arm=arm))
    if coverage:                                                    # m6: every block's setting, before the menu
        for (name, arm), ts in sorted(ts_cells.items()):
            for h, nw in sorted(R.coverage_settings(ts["recs"])):
                R.coverage_shapes_at(h, nw, coverage_series)
        resume.put("coverage|settings", dict(R._COVERAGE))
    spill.add(R.coverage_rows())
    ran = {"runs": [r.name for r in runs], "replays": len(runs), "references": sum(r.kind == "reference" for r in runs),
           "conditional_runs": bool(conditional)}
    ran["new"] = ran["replays"] - ran["references"]
    return spill, ran


# ------------------------------------------------------------------------------------------------ the ladder


def ladder_reading(streams: dict[str, dict[str, Any]], starts: int | None, *, resume: Resume | None = None,
                   spill: Spill | None = None, log=print) -> tuple[Spill, dict[str, Any]]:
    """10.1 item 7: 10, 25 and 50 % on TS-16 and P-16's eight corners, verdict arm, A-9's seed base (section 12's
    ladder seed), every block, one row a start. Item 5 on every replay; item 4 where run directly (DT). Raises
    `firm_reading.Refused` at the first refusal."""
    import user_journey as UJ

    resume = resume or Resume(None)
    spill = spill if spill is not None else Spill(None)
    st = streams["p16"]
    job = st["jobs"]["verdict"]
    chosen = UJ.start_choice(len(job["blocks"]), starts)
    cells = [("TS-16", T.settings_for("TS", "reference"), "reference")]
    cells += [(f"{p}-16-{c[0]}", T.settings_for(p, c), c) for p in LADDER_PLANS for c in (T.STRICT, T.LENIENT)]
    n = 0
    for name, s, corner in cells:
        blocks, point_ref, _ = R.arm_inputs(st["jobs"]["point"], job, s, "verdict", (st.get("delta") or {}).get("verdict"))
        cjob, kw = R.cell_job(job, s, blocks, ladder=True)
        for resp_name in R.LADDER:
            key = f"ladder|{name}|{resp_name}"
            t0 = time.time()
            got = resume.get(key)
            if got is None:
                resp = B.BY_NAME[resp_name]
                cell = R.run_cell("p16", "verdict", resp, cjob, s, chosen, kw, point_ref, direct=s.plan == "DT")
                if cell["problems"]:
                    raise R.Refused(f"{key}: " + "; ".join(cell["problems"][:6]))
                outs = R.reading_outs(cell, "p16", "verdict", resp, s)
                srows, table = UR.summary("p16", "verdict", resp, outs, blocks=UR.READING_BLOCKS)
                probs = UR.consistency_problems(srows, outs, f"{name} {resp_name}", blocks=UR.READING_BLOCKS)
                if probs:
                    raise R.Refused("; ".join(probs[:6]))
                head = {"run": name, "plan": s.plan, "stream": "P-16", "arm": "verdict", "corner": corner,
                        "seed_base": R.F.LADDER_SEED, "response_name": resp_name}
                got = _tag(_ur_rows(srows, "ladder") + _start_rows(table, {}, "ladder", [o["rec"] for o in outs]),
                           **head)
                got += _tag([{"section": "identity", "subsection": "items_4_5_ladder", "measure": k, "stat": "value",
                              "value": float(v)} for k, v in cell["checks"].items()], **head)
                resume.put(key, got)
                del cell
            spill.add(got)
            del got
            n += 1
            log(f"timing: ladder {name} {resp_name}: {time.time() - t0:.0f} s", flush=True)
            gc.collect()
    return spill, {"ladder_replays": n}


# ------------------------------------------------------------------------------------------------ the gate


def registered_gate(design: str, n_paths: int) -> dict[str, Any]:
    """The stream's registered gate call, made as `identity/gate_identity.py` makes it (P-16: its registered gate seed
    after its trades' hash; P-14: its own), with a hook factory so each call has its own sink; TS's registered paths;
    and the design's fresh R (the zero-edge twin's P&L shift, r8)."""
    import a3_brk30 as B3
    import a3_brk30_cb20 as C3
    import atlas_a3 as A3
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import rc_screen as S
    import score_fv3_grid as gf
    import stage2_identity as SI

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    if design == "p16":
        sp = P.SPEC
        I, b = sp.build()
        t, days = b["cells"][sp.cell]["trades"], b["days"]
        if D.trades_hash(t) != sp.trades_sha256:
            raise SystemExit("REFUSED: P-16's trades are not its registered trades")
        seed, gap, budget, ref_file = SI.P16_SEED, C3.STRICT_GAP, C3.BUDGET, SI.P16_PATHS
    else:
        I = S.inputs()
        t, days = B3.cell_trades(I["L"])
        seed, gap, budget, ref_file = S.SEED, S.STRICT_GAP, S.BUDGET, S.P14_PATHS
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    keys = B3.rrs(t)
    _, e_by, lb_by, _, _ = A3.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the gate blocks hold a different number of trades")
    pcfg = fcfg["portfolio"]

    def hook_factory(label: str):
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
        ps._label(inner, f"rd01_{design}_{label}")
        return lt.lever_hook(inner), sink

    hook, _ = hook_factory("unused")
    kw = A3.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=seed, n_paths=int(n_paths),
                        horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=B3.capacity(t, fcfg),
                        levels=(0.0,), rtp=False, one_at_a_time=gap, purchase_budget=budget)
    return {"blocks": kw.pop("blocks"), "kw": kw, "hook_factory": hook_factory, "seed": int(seed),
            "fresh_rr": float(B3.fresh_rr(L)[1]), "ref": read_result(RESULTS_DIR / ref_file)}   # rc_dev_test's route


def paired_paths(sink: list[dict], ref: pd.DataFrame, shift: str, n: int) -> list[dict]:
    """The plan's gate paths against TS's registered ones, path for path (same seeds), each PATH_COLS column."""
    import zero_edge_decomposition as zd

    a = pd.DataFrame([r for r in sink if r["shift"] == shift and float(r["enforcement_p"]) == 0.0])
    b = ref[(ref["run"].astype(str) == "gate") & (ref["shift"].astype(str) == shift)
            & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(n)
    if a.empty or len(b) != len(a):
        return [{"section": "gate_paired", "shift": shift, "measure": "paths", "stat": "unpaired", "value": float(len(a))}]
    a = a.sort_values("path").reset_index(drop=True)
    b = b.reset_index(drop=True)
    out = []
    for c in zd.PATH_COLS:
        x, y = pd.to_numeric(a[c], errors="coerce").to_numpy(float), pd.to_numeric(b[c], errors="coerce").to_numpy(float)
        d = x - y
        out += [{"section": "gate_paired", "shift": shift, "measure": c, "stat": "plan_mean", "value": float(np.nanmean(x))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "ts_mean", "value": float(np.nanmean(y))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "mean_diff", "value": float(np.nanmean(d))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "share_above",
                 "value": float(np.mean(d > 1e-9))}]
    return out


def gate_reading(n_paths: int, workers: int, gates: dict[str, dict] | None = None, run_gate=None, *,
                 resume: Resume | None = None, log=print) -> tuple[list[dict], list[dict], dict[str, Any]]:
    """10.1 item 8 on the 16 corners, one call each and the zero-edge twin: (gate rows and paths, the twins' oracle
    rows, what ran). Raises `firm_reading.Refused` at the first oracle beyond its interval (9.2)."""
    if run_gate is None:
        from extended.gate import run_gate
    resume = resume or Resume(None)
    rows, oracle, n = [], [], 0
    for design in ("p16", "p14"):
        g = (gates or {}).get(design) or registered_gate(design, n_paths)
        for plan in LADDER_PLANS:
            for corner in (T.STRICT, T.LENIENT):
                key = f"gate|{design}|{plan}|{corner}"
                head = {"run": f"{plan}-{design[1:]}-{corner[0]}", "plan": plan, "stream": design, "corner": corner}
                t0 = time.time()
                got = resume.get(key)
                if got is None:
                    s = T.settings_for(plan, corner)
                    w = 1 if plan == "QP" else int(workers)          # Quick Pay's per-run classes do not pickle
                    grows, sinks, labels, probs = R.gate_rows(g["blocks"], g["kw"], s, run_gate, workers=w,
                                                              fresh_rr=g["fresh_rr"], hook_factory=g.get("hook_factory"))
                    if probs:
                        raise R.Refused(f"{key}: " + "; ".join(probs))
                    got = {"rows": _tag(grows, **head), "oracle": [], "paths": []}
                    for r in grows:
                        if r.get("reading") != "zero_edge":
                            continue
                        for m in ("twin_gross_per_funded", "twin_pass_rate"):
                            got["oracle"] += _tag([{"section": "oracle", "subsection": "twin", "measure": m,
                                                    "stat": stat, "value": float(r.get(col, np.nan)),
                                                    "note": "held (9.2): not above its ceiling beyond the interval"}
                                                   for stat, col in (("value", m), ("se", f"{m}_se"),
                                                                     ("ceiling", f"{m}_ceiling"))], **head)
                    for label, sink in sinks.items():
                        if sink:
                            got["paths"] += _tag([{"section": "gate_path", "call": label, **x} for x in sink], **head)
                        ref = g.get("ref")
                        if ref is not None and label == "plan":
                            for shift in ("point", "lower_bound"):
                                got["rows"] += _tag(paired_paths(sink, ref, shift, int(n_paths)), **head)
                    resume.put(key, got)
                rows += got["rows"] + got["paths"]
                oracle += got["oracle"]
                n += 1
                log(f"timing: gate {key}: {time.time() - t0:.0f} s", flush=True)
                gc.collect()
    return rows, oracle, {"gates": n}


# ------------------------------------------------------------------------------------------------ the files


def streams_of(rd: Path) -> dict[str, dict[str, Any]]:
    """P-16 and P-14 as U1 builds them, each with its verdict arm's registered shift (r6), checked."""
    import user_beside_identity as UBI

    out = {}
    for name in ("p16", "p14"):
        (jobs, c, probs), seen = R.build_with_deltas(lambda name=name: UBI.build(rd, name))
        if probs:
            raise SystemExit("REFUSED: " + "; ".join(probs[:4]))
        uniq = {(float(dr), None if by is None else tuple(sorted(by.items()))) for dr, by in seen}
        if len(uniq) != 1:
            raise SystemExit(f"REFUSED (r6): {name}'s builder shifted its arms by {len(uniq)} different deltas, not one")
        out[name] = {"jobs": jobs, "config": c, "delta": {"verdict": seen[0]}}   # checked against the arm's blocks
    return out


HEAD_COLS = ("section", "subsection", "run", "plan", "stream", "arm", "corner", "flip", "kind", "request_rule",
             "response_name", "block", "month", "horizon", "measure", "stat", "value", "n", "note", "labels", "status")


def frame(rows: Any, sections: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Rows (a list of rows, a frame, or a `Spill`) as one file's frame: the head columns first, every row "described,
    not carried", the sections 15's."""
    df = rows.frame() if isinstance(rows, Spill) else rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    df["status"] = R.STATUS
    if sections is not None:
        bad = sorted(set(df["section"].astype(str)) - set(sections))
        if bad:
            raise ValueError(f"sections {bad} are not 15's {sections}")
    cols = [c for c in HEAD_COLS if c in df] + [c for c in df.columns if c not in HEAD_COLS]
    return df[cols]


def identity_rows(found: dict[str, Any], pin: dict[str, str]) -> list[dict]:
    """The `identity` section's waits and pin: each admitted row, its sha and HEAD -- never the token string (D1)."""
    rows = [{"section": "identity", "subsection": "waited", "measure": task, "stat": "row", "value": float("nan"),
             "row": v["row"], "sha": v["sha"], "head": v["head"], "note": v["what"]} for task, v in found.items()]
    rows.append({"section": "identity", "subsection": "pin", "measure": R.DECLARATION, "stat": "row",
                 "value": float("nan"), "note": f"{pin['row']} pins sha256 {pin['sha256']} (its LF text, checked)"})
    return rows


def write_all(reading_rows: Any, gate_rows: list[dict], params: dict[str, Any], target: Path | None,
              counts: dict[str, Any]) -> list[str]:
    """15's three files with their manifests: the reading (rows, or the run's `Spill`) and the gate, then the menu as a
    declared step on those two as written (read back through their hashes, each frame freed first)."""
    from extended.results import read_result, write_result

    wrote = []
    fr, fg = frame(reading_rows, SECTIONS), frame(gate_rows)
    seeds = {"block": {str(k): v for k, v in SEED_BLOCK.items()}, "inherited_gate_seeds": params.get("gate_seeds", {})}
    common = {**params, "seeds": seeds, "run_counts": counts}
    for nm, df, seed, vc, what in (
            ("fc_reading", fr, R.F.LADDER_SEED, counts.get("replays", 0),
             "the identities, oracles, mechanics, scorecard, pairing, divergence, price grid, ladder and coverage"),
            ("fc_gate", fg, int(params.get("gate_seeds", {}).get("p16", 0)) or R.F.LADDER_SEED, counts.get("gates", 0),
             "the gate beside on the 16 corners, with the zero-edge twins and the paths paired with TS's")):
        p, m = write_result(df, nm, script=SCRIPT, seed=seed, parameters={**common, "file": nm}, results_dir=target,
                            prereg_id="RD-01", description=f"RD-01 {what}: {READING}", exploratory=False,
                            variant_count=int(vc), notes={"status": R.STATUS, "reading": READING})
        wrote += [p.name, m.name]
    del fr, fg, df
    gc.collect()
    base = target if target is not None else None
    from extended import RESULTS_DIR

    folder = Path(base) if base is not None else RESULTS_DIR
    fm = FM.menu(read_result(folder / "fc_reading.csv"), read_result(folder / "fc_gate.csv"))
    p, m = write_result(fm, "fc_menu", script=SCRIPT, seed=None, require_seed=False,
                        parameters={**common, "file": "fc_menu", "step": "extended.firm_menu.menu on fc_reading.csv "
                                    "and fc_gate.csv as written (their sha256 verified on read)"},
                        results_dir=target, prereg_id="RD-01",
                        description=f"RD-01 the menu, its flags and labels, items 3, 4 and 10 -- a declared light step "
                                    f"on the run's own files; no randomness: {READING}", exploratory=False,
                        variant_count=int(counts.get("replays", 0)), notes={"status": R.STATUS, "reading": READING})
    wrote += [p.name, m.name]
    return wrote


def manifest_params(found: dict[str, Any], pin: dict[str, str], entries: list[dict], base_rules: Any,
                    a: argparse.Namespace, commit: str) -> dict[str, Any]:
    return {"declaration": R.DECLARATION, "pinning_row": pin, "identity_rows": found, "commit_read": commit,
            "purposes_in_order": list(R.PURPOSES), "repeat": a.repeat, "starts": "every start", "paths": PATHS,
            "workers": a.workers, "cost_and_table_inputs": plan_manifest(base_rules), "readings": readings_manifest(),
            "record_entries": entries, "data_manifest_sha256": data_manifest_sha256(),
            "conventions": CONVENTIONS, "horizon_of_month": R.HORIZON_OF_MONTH, "count_horizon": R.COUNT_HORIZON,
            "coverage_series": R.COVERAGE_SERIES, "status": R.STATUS, "code_blobs": code_blobs(),
            "exploratory": False}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repeat", default=None, help="E-NNN: a decision row naming the declaration (a further read)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--plan", action="store_true", help="print the guards' findings and what would run; read nothing")
    a = ap.parse_args(argv)
    bad, found = identity_problems()                 # D1: the shared parser, before anything else
    pin, pbad = pin_row()
    entries, ebad = record_entries()
    lbad = e015_problems()
    if a.plan:
        print("waited identities: " + ("; ".join(bad) if bad else
                                       "; ".join(f"{k} at {v['row']} {v['sha'][:12]}" for k, v in found.items())))
        print("the pin: " + ("; ".join(pbad) if pbad else f"{pin['row']} {pin['sha256'][:12]}"))
        print(f"record entries: {len(entries)}" + (" -- " + "; ".join(ebad[:4]) if ebad else ""))
        print("E-015's limits: " + ("; ".join(lbad) if lbad else "none approved: the menu flags none"))
        pre = precheck(a.repeat)
        print("the purposes' pre-check (reader.authorise, no read): " + ("; ".join(pre) if pre else "every one clear"))
        print(f"would run, in order: {', '.join(R.PURPOSES)}; {len(T.RUNS)} runs declared")
        return 0
    if bad or pbad or ebad or lbad:
        print("REFUSED (RD-01 9.1, 15): " + "; ".join(bad + pbad + ebad + lbad), flush=True)
        return 3
    pre = precheck(a.repeat)                           # m7: all three, before the first is ledgered
    if pre:
        print("REFUSED (RD-01 6 item 6, before any read): " + "; ".join(pre), flush=True)
        return 3
    import stage2_identity as SI

    from propedge import RESULTS_DIR
    from propedge.contract.adapter import rules_from_ledger

    t0 = time.time()
    commit = _commit()
    params = manifest_params(found, pin, entries, rules_from_ledger(), a, commit)
    folder = None if a.no_resume else RUNS_DIR / "resume" / f"rd01-reading_{commit}"
    resume = Resume(folder)
    spill = Spill(RUNS_DIR / "resume" / f"rd01-reading_{commit}_rows")          # m7: the rows out of memory
    spill.add(identity_rows(found, pin))

    def authorise(purpose: str) -> None:
        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose,
                                     declaration=R.DECLARATION, repeat=a.repeat,
                                     files=SI.engine_files(VENDOR, bars=True),
                                     what=f"RD-01's {purpose} ({SCRIPT}): every start, every run, {PATHS} paths")

    try:
        authorise("firm_scorecard")
        streams = streams_of(RESULTS_DIR)
        import user_beside_identity as UBI

        u1 = UBI.u1_reference(RESULTS_DIR, ("p16", "p14"))      # U1's registered start rows (7.1, V1)

        def reference(design: str, arm: str, outs: list, n_window: int, starts_: Any) -> list[str]:
            return UBI.u1_compare_outs(design, streams[design]["config"], arm, outs, u1, n_window, starts_)

        _, ran = scorecard_reading(streams, list(T.RUNS), None, resume=resume, spill=spill, reference=reference)
        del u1
        authorise("firm_ladder_beside")
        _, lran = ladder_reading(streams, None, resume=resume, spill=spill)
        del streams
        gc.collect()
        authorise("firm_gate_beside")
        grows, orows, gran = gate_reading(PATHS, a.workers, resume=resume)
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}", flush=True)
        return 3
    except R.Refused as exc:
        print(f"REFUSED (RD-01): nothing written -- {exc}", flush=True)
        return 3
    counts = {**ran, **lran, **gran}
    params["seconds"] = round(time.time() - t0, 1)
    import rc_screen as RS

    params["gate_seeds"] = {"p16": int(SI.P16_SEED), "p14": int(RS.SEED)}
    spill.add(orows)
    wrote = write_all(spill, grows, params, None, counts)
    print(f"written: {wrote} ({time.time() - t0:.0f} s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
