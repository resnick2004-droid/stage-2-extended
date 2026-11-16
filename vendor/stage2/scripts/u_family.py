"""EXPLORATORY (D-621, program U): one lever family on P-16's replay setup and, since D-626 (8), on P-14's, judged on
the user's milestones by the declared selection rule (`propedge/research/u_select.py`). Beside the gate, never a
verdict of the gate; a CARRIED cell is a new candidate for its own registered test.

    python scripts/u_family.py --check --starts 4 --workers 1     # the identities that can run and the whole pipeline
                                                                  #   on four starts with the built-in NULL family
                                                                  #   (BOTH bases' reference cells); prints identity
                                                                  #   and timing lines only; nothing written to
                                                                  #   results/
    python scripts/u_family.py --family <name> --workers 2        # a registered family (from a clean checkout, D-474)
    python scripts/u_family.py --check --starts 4 --check-overrides '{"wallet_stop": 1000.0}' [--check-base p14]
                                                                  # --check only: the given overrides as one cell of
                                                                  #   the NULL family on that base (p16 when absent) --
                                                                  #   its replays, its gate call at the base's
                                                                  #   registered seed and, on p16, its coin replays;
                                                                  #   never counted, nothing written, nothing of the
                                                                  #   cell printed but identity and timing lines
    python scripts/u_family.py --check --starts 4 --check-base s100_us[,s150_us,...]
                                                                  # --check only (D-639): each named WINDOW base as one
                                                                  #   cell of the NULL family -- its identities, its
                                                                  #   FACTS table (supply and resolution inputs, the
                                                                  #   cap), its replays, its gate calls at the screen's
                                                                  #   seed and its coin replays; never counted, nothing
                                                                  #   written, nothing of the cell printed but
                                                                  #   identity, timing and fact lines
    python scripts/u_family.py --trades-hash                      # D-639: every window base's content hashes from the
                                                                  #   screens' own builders beside their pins; no
                                                                  #   campaign, nothing written
    python scripts/u_family.py --check --starts 4 --check-base l1_day0[,l1_seq_hedged,l5_day0_hedged_combines,...]
                                                                  # --check only (D-643, D-644): each named JOINT base
                                                                  #   (any of the 18) as one cell of the NULL family --
                                                                  #   its identities (the 5 + 0 twin, U1's 5 + 1 rows,
                                                                  #   the sequenced cell's opening), its replays
                                                                  #   through the joint engine at both arms and, for
                                                                  #   an unhedged base, its pooled gate call(s) at the
                                                                  #   screen's seed and its coin replays (a hedged
                                                                  #   base's guards are refused); never counted,
                                                                  #   nothing written, nothing of the cell printed
                                                                  #   but identity and timing lines

**A family** is a registry entry (`REGISTRY`), added only after its decision row declares it (D-621 (6); the grid is
contract arithmetic and verified rule values, fixed in that row before any code, D-621 (4)(d)):

    REGISTRY["seats"] = {                        # AN EXAMPLE OF THE FORM ONLY -- not a declared family, not registered
        "family": "seats",                       # the result is results/u_seats.csv
        "decision": "D-630",                     # the row that declared it: its cells are counted under D-630:u_seats
        "k": 1,                                  # its number in the order declared: judged one-sided at 0.05 / (k (k + 1))
        "cells": (
            {"name": "seats4", "overrides": {"accounts": 4, "combines": 4, "total_accounts": 4}},
            {"name": "budget10", "overrides": {"purchase_budget": (10, 21)}},
            {"name": "cap2of3", "overrides": {"funded_cap_share": 100 / 150}, "equals_u1": "p16_funded_cap"},
            {"name": "keep1000", "overrides": {"protocol": {"keep_balance": 1000.0}}},
            {"name": "budget30_p14", "base": "p14", "overrides": {"purchase_budget": (30, 21)}},   # on P-14's setup
            {"name": "seats4_p14", "base": "p14",
             "overrides": {"accounts": 4, "combines": 4, "total_accounts": 4}},
        ),
    }

**A cell** is a name plus plain-data overrides on its base's replay setup (`apply_overrides`; nothing callable, no
engine change): the three seat keys together (`accounts`, `combines`, `total_accounts` -- the single engine's, the
base's budget kept unless the cell overrides it; U1's four-seat cell ran through the joint engine with the budget scaled
to 16 in 21); `purchase_budget` (K, window) or None; `funded_cap_share` (the funded leg's micro cap scaled,
`resolved_coin.FundedCapRule`); `protocol` (`keep_balance`, `payout_frac`, `payout_path`); `payout_timing`; and D-630's
three entry options, on either base (`u_select.ENTRY_KINDS`; the engine's own, `propedge.campaign.lockstep`) --
`wallet_stop` (dollars above zero: no evaluation bought while the cash out of pocket is above it), `pause_after_funded`
(a whole number F: none bought at a purchase step where F funded accounts are held and no payout has arrived, D-632)
and `seat_ramp` (a whole number below the cell's seats: that many accounts at first, one more for each payout arrived):

    {"name": "wallet1000", "overrides": {"wallet_stop": 1000.0}}
    {"name": "pause1_p14", "base": "p14", "overrides": {"pause_after_funded": 1}}
    {"name": "ramp2_p14", "base": "p14", "overrides": {"seat_ramp": 2}}

They are set on the campaign's gate arguments, so they reach the replay (`customer_slices.engine_args` reads them
there) and the gate floor (`gate.run_gate`'s own arguments) alike; they lean on no firm rule (D-630 (4)). A cell with
one carries, beside its scorecard, the option's own record over each start's long replay (section `cell` rows of role
`ENTRY_ROLE`, never in the selection), and its gate floor's row the gate's columns for the option.

**The funded plan** (D-653, family 7; `funded_plan`, on either base, alone or with the protocol's payout path):

    {"name": "flat500", "overrides": {"funded_plan": {"risk": 500.0, "rr": 1.0}}}
    {"name": "flat500_cons_p14", "base": "p14", "rules": CONSISTENCY_RULES,
     "overrides": {"funded_plan": {"risk": 500.0, "rr": 1.0}, "protocol": {"payout_path": "consistency"}}}

The cell runs on the base's table with its FUNDED phase -- a funded account from activation to its first payout --
replaced by ONE leaf: `risk` dollars at 1R, one routed trade a session (`flat_plan`: `u_select.funded_plan_policy_dict`
rebuilt by `RiskPolicy.from_dict`, which refuses a tier-1 breach; the evaluation's leaves and the paid phase's leaves
are the base's, compared subtree for subtree; the table is not re-solved; no engine file changes). **With
`"paid": true`** (`{"risk": 500.0, "rr": 1.0, "paid": True}`; D-653 as amended before its run, the Consistency cells')
the same leaf replaces the PAID phase too -- one trade a session in every state after a first payout, the request day
and the base's no-trade states included: a paid phase solved for the Standard path sits out states a Standard account
leaves at the close (five winning days: it is paid) and would hold a Consistency account there for good; the table's
id ends `_flat<X>_paid`, and only the evaluation's leaves are then the base's. **Payout requests
are not a leaf's:** the engine requests at the close an account is eligible (`lockstep`'s funded account: the
protocol's `payout_path`, `payout_frac` and `keep_balance` against the verified rule values), so the plan removes
none; `request_day` is 1 only on the session after a request, when the account is already in the paid phase. **Edges
and bounds:** every trade is read at the R its leaf asks for and, on the bound arm, shifted by that R's own gap
(`gate.shifted_blocks`' `delta_by_rr`), so the plan's trades take R = 1's edge and bound, the evaluation's and the
paid phase's trades theirs, as on the base; the campaign's two scalars (`e`, `lb`: the gap the blocks' base column
takes, which `atlas_a3.gate_kwargs` reads at the table's FRESH funded R) and the protocol's funded leg are re-pointed
to the plan's own fresh funded decision -- R = 1 at `risk` dollars -- as D-641's window bases re-point theirs; a plan
whose R the campaign carries no bound for is refused. **Identities** (refusing): the table that reaches the replay is
the base's with that one phase replaced, it asks for no R the blocks do not carry, on the bound arm the blocks' base
column is their R = 1 column, and the plan's dollars buy a micro at every stop and every tier (`plan_cell_problems`;
the realised dollars are printed as `fact:` lines, inputs from the sizing rule); **each start's record up to the
base's first funded account is the base's** -- the plan changes nothing before a funded account exists
(`evaluation_leg_problems`); the gate's rows carry the plan's table id. A Consistency plan cell names D-645's four
rules (`rules_problems`); a Standard one leans on no rule beyond the base's. One such cell is exercised, uncounted, by
`--check --check-overrides '{"funded_plan": {"risk": 500.0, "rr": 1.0}, "protocol": {"payout_path": "consistency"}}'
[--check-base p14]`. Optional:
`base` (below), `rules` -- the ledger's names of the firm rules the overrides lean on beyond the base's own, each of
which must be verified for line (3)(iii) -- and `equals_u1` -- a configuration of U1's file the cell must equal start
for start.

**The crippled funded account resolved at once** (D-659, family 9; `funded_resolve`, on either base):

    {"name": "resolve3", "overrides": {"funded_resolve": {"rr": 3.0}}}
    {"name": "resolve1_5_p14", "base": "p14", "overrides": {"funded_resolve": {"rr": 1.5}}}

The cell runs on the base's table with, in its FUNDED phase -- activation to the first payout -- every state whose
balance is BELOW the account's starting balance (`balance` < 0 in the table's variables; a fresh funded account is
balance 0, cushion 2,000) decided by a bold leaf: the dollars of the cushion band's LOWER edge on the table's own
cushion grid (so never more than the room), never less than one micro's dollars at the base's widest stop
(`one_micro_dollars`: every trade buys a micro), at R = `rr`, one routed trade a session (`resolve_plan`:
`u_select.funded_resolve_policy_dict` rebuilt by `RiskPolicy.from_dict`, which refuses a tier-1 breach). The table's
balance bands and cushion bands are kept as they are: a band that starts at or above zero keeps the base's own
subtree, so an account at exactly its starting balance -- the fresh account's opening among them -- is the base's,
and an account one cent under it is the bold leaf's. The paid phase and the evaluation are the base's subtrees. Not
re-solved; no engine file changes. **Only the lowest cushion band can ask for more than the room** (its edge is zero,
its leaf one micro's dollars): with a room under one micro the trade is still one micro and the loss limit sits inside
its stop -- settled by the engine's mid-trade rule (D-156), as any trade that risks more than the room. **The size
limit still binds:** the realised risk is the smaller of the leaf's dollars and the entry tier's allowance at the
trade's stop, in whole micros (`resolve_sizing`, printed as `fact:` lines). **Edges and bounds:** nothing is
re-pointed -- the table's fresh funded decision is the base's, so the campaign's `e` and `lb` and the protocol's
funded leg stand; an `rr` the campaign carries no edge and bound for is refused. **Identities** (refusing): the table
is the base's but for those states, over the table's whole grid of states, and reaches the replay with nothing else
changed (`resolve_cell_problems`); each start's record up to the base's first funded account is the base's
(`evaluation_leg_problems`); and, on every 21st start with the engine's daily recorder on, **the cell's run and the
base's are one through the close of the first session at which a funded account stands below its starting balance**
(`under_water_problems`: the counted replays keep no account's daily balance, so the identity replays its starts
again -- the reason it is thinned). The cell leans on no firm rule beyond the base's. Exercised, uncounted, by
`--check --check-overrides '{"funded_resolve": {"rr": 3.0}}' [--check-base p14]`.

**A base** (`"base": "p16" | "p14"`, `p16` when absent; a family may mix them) is the replay setup the overrides are
put on. `p16`: P-16's (the 37.5-point coin, `rc_s150_all`), as before. `p14`: exactly U1's `p14` configuration
(`p14_inputs`, `p14_jobs`: D-518's `p14` row handed to `customer_journey.Inputs` and `customer_journey.replay_jobs`, the
calls of `user_journey.build_d518`) -- A3-BRK30's breakout trades, the no-closure table, the budget (20, 21), the strict
rule. **On `p14`** the three seat keys, `purchase_budget`, the `protocol` fields and `payout_timing` reach the same
engine arguments as on `p16` (both setups are `atlas_a3.gate_kwargs`' arguments); `funded_cap_share` is REFUSED there
(`u_select.BASE_REFUSED_KINDS`): it would scale the funded micro cap of both of P-14's rungs (12.5 and 25 points) alike,
which is not D-544's reading (the reference stop over the coin's one wider stop). A `p14`-based cell is not a coin
design: line (3)(iv) is `not applicable` to it (never held, never run); D-621's order of lines is otherwise unchanged.
Its gate floor is the registered test's gate campaign (`gate_run_p14`: `a3_brk30_cb20._registered_run`'s `go("gate")`
as D-518 re-ran it at 0 % denial, `customer_journey.resampled_single`) with the cell's overrides -- first, without
overrides at the registered seed 20261131, its paths must equal the first paths of `a3_brk30_cb20_gate_paths.csv`'s
`gate` run path for path and, at the full 500, its rows must reproduce `a3_brk30_cb20_gate.csv`'s section `gate` rows at
0 % (the growth at the bound and at the point, the required bankroll at the bound); then the fresh seed. Resolution is
read as the registered test read it (`a3_brk30.resolution_rows`). The choice across a mixed family is unchanged (the
best P on the choice block, whatever the base) and so is R* (U1's file, D-621 (2)); the paired readings are on common
start DATES, and the bases' windows -- and R*'s start rows in U1's file -- are asserted to be the same session dates.

**Identities first, refused otherwise:** D-621's row and D-620's by their pins; P-16's trades by their screen row and
registered content hash (`rc_dev_test.trade_problems`; the walk is `rc_stop_walkforward`'s, the coin guard's); the
reference cell (P-16, no override) replayed here by U1's own task (`user_journey._single_task`) equal to
`results/user_journey.csv`'s `p16` start rows start for start -- so every cell is paired with the file on record -- and
to P-16's registered slices; in every replay the payouts and fees tied to the engine's totals; the scorecard's readings
recomputed from the file's `p14`, `p15` and `p16` start rows equal to the file's own rows; R* the same whether P is read
on the starts with 63 sessions or as the mean of the file's three shares; the coin swap at the registered coin
rebuilding each coin design's registered trades; the scoreboard holding one P-06 row. Without U1's file the run is
refused (in `--check` those identities are reported NOT RUN and the reference stands in for R*). **For base `p14`:**
P-14's trades by the registered test's two pins (`a3_brk30.identity_with_screen`, `a3_brk30_cb20.p13_trade_problems`);
its setup the registered test's (the no-closure table by `a3_brk30_cb20.noclose_plan`'s hashes, the budget, the strict
rule, the seed); its reference cell (`reference_p14`, no override, never counted) replayed here equal to
`results/user_journey.csv`'s `p14` start rows start for start and, per start, to P-14's registered slices
(`a3_brk30_cb20_gate_slices.csv`) and D-518's start rows (`customer_journey.csv`); the bases' windows the same dates.
Only the bases a family's cells name are built and replayed.

**A window base** (D-639, the user's hours; `u_select.WINDOW_BASES`: `s100_london`, `s100_us`, `s100_asia`,
`s150_london`, `s150_us`, `s150_asia`) is a coin cell restricted to one session window and is a family cell ITSELF:

    {"name": "us25", "base": "s100_us", "overrides": {}}         # THE FORM: no override, counted, the base named once

It takes no override; its cell is counted and carries its own scorecard; `p16` and `p14` keep their uncounted
references. **Built** (`window_inputs`) from its stop's walk (`rc_stop_walkforward.walk_stop`, one stop held at a time)
as `rc_width_screen.build` builds a cell -- `rc_reentry_screen.build` with the stop a parameter (the news-safe 07:30 CT
report-day cut, every five-minute mark of the window, the cutoff of D-525 (4) at every R the table offers, the
registered coin, re-entry when flat) and then D-533's cut (no report-day entry before 07:35 CT) at BOTH stops --
**identities first:** the cell as its screen's file records it (`rc_dev_test.trade_problems`:
`rc_reentry_screen.csv`'s `rc_s100_<window>` row, D-525's build without D-533's cut; `rc_width_screen.csv`'s
`rc_s150_<window>` row, with it) by the file's sha256, the row's facts and a pinned content hash; the trades the
family runs by a second pinned content hash (`WINDOW_PINS`, from `--trades-hash`: the screens' own builders, no
campaign; the two are one hash where the cut removes nothing); the coin swap at the registered coin rebuilding them;
`s150_london` equal to U1's `rc_s150_london` start rows start for start. **Its own** 0.05 bounds (`atlas_a3.bounds`,
the era rule) and day capacity, P-14's protocol as P-15 and P-16 (`user_journey._rc_campaign`: the no-closure table,
the budget (20, 21), the strict rule, five seats). **The R cap** (D-639 (2); `passes_by_r`, `u_select.r_cap`): each
offered R's pass or fail on D-212's line is `atlas_a3.resolution`'s own, read from the cell's exit-kind columns only;
where an R fails, the offered R are capped at the largest that passes -- the trades and the marks stay the screen's
(the cutoff was read at every R the table offers), every per-R column above the cap is dropped (`capped_trades`), so
the campaign's keys, bounds, blocks and resolution check are the capped list's, and the table is rebuilt from plain
data with every leaf's R above the cap at the cap, dollar risk unchanged, not re-solved (`capped_plan`,
`u_select.capped_policy_dict`); the config's two fresh R follow the capped table's own fresh decisions
(`capped_inputs`). A cell with no passing R above the collect leaf's (`collect_leaf_r`), or with fewer offered trades
than sessions, is NOT RUNNABLE: recorded (its facts), never replayed, never counted. **The FACTS** (`window_facts`,
`facts_lines`: marks, offered trades a session, capacity, each R's unresolved share overall and in its worst year,
the cap, runnable or not) are inputs from supply and resolution columns, printed before anything runs and kept as
section `cell` rows of role `FACT_ROLE` and in the manifest. **Line (3)(iii):** first `gate_run` on the screen's own
cell with the table as it is at the screen's seed, which at 500 paths must reproduce the cell's row in its screen's
file (`window_row_problems`); then the cell's trades, bounds, capacity and capped table at the fresh seed.
**Line (3)(iv):** each sequence re-deals the cell's own window on the same walk with the cell's cap
(`window_coin_campaign`); R* must not be a coin design (it is P-14, D-626), refused otherwise.

**A joint base** (D-643 as D-644 widens it, the multi-firm portfolio by sequence; `u_select.JOINT_BASES`, 18:
`l<K>_day0` and `l<K>_seq` for K = 1, 2, 5 Lucid seats, each also as `..._hedged` and `..._hedged_combines`; the
machinery is `scripts/u_firms.py`) is P-16's trades through the joint two-firm engine -- Topstep's five seats plus K
Lucid seats, the Lucid firm from day 0 or opened only when the campaign's first payout has arrived (the joint run's
sequencing option, `propedge.research.second_firm`), under one of `hypo_hedge`'s three deals -- and is a family cell
ITSELF, as a window base is:

    {"name": "l1_seq", "base": "l1_seq", "overrides": {}}        # THE FORM: no override, counted, the base named once

**Built** as U1 builds its `p16_5+1` configuration (`u_firms.inputs`, `u_firms.jobs`: `user_journey.build_joint`'s own
calls -- `rc150_firm_split.inputs("lucid")`, `arm_blocks`, `firm_setups(X, "rep", (5, K))`); a day-0 unhedged cell's
starts run through U1's own task, any other cell's through the same task's body with the deal and the option passed.
**Identities first:** the trades by their screen row and P-16's registered content hash, the opposite side aligned one
for one; Lucid's price row, household caps and open rows (`u_firms.rules_problems`); the 5 + 0 cell through the joint
engine (the twin, replayed here, never counted) equal to U1's `p16` start rows start for start; `l1_day0` equal to
U1's `p16_5+1` start rows start for start; a sequenced cell's opening day on every start the twin's first payout day,
a start that never opened the twin's record, and an opened start's record before its opening day the twin's
(`u_firms.sequence_problems`; inside the joint run, on every opened path, the first firm through the opening day is
the first firm alone or the run raises).

**Eligible and hypothetical** (D-644 (3), (4)). The six UNHEDGED cells are eligible: every row labelled
`lucid_upper_bound`, counted under the family's id, in the choice and the judgement. The twelve HEDGED cells are
HYPOTHETICAL (cross-firm hedging is prohibited at both firms, tier 1): every row labelled `hypothetical_hedge` with
`u_select.HYPOTHETICAL_NOTE` in `label_note` (which says upper bound too), counted under
`<row id>:hypothetical_hedge` (in the program's count with their family), written with their scorecard at BOTH arms
(role `u_firms.HYPOTHETICAL_ROLE`) and the share of signals paired and unpaired (role `u_firms.DEAL_ROLE`) -- and
REFUSED in the choice and the judgement (`u_select.judge(refused=...)`), in every guard (`coin_guard`,
`u_firms.gate_run`, `u_firms.coin_jobs`), as a row to beat (`u_select.row_to_beat`, `tables`) and as the verdict's
cell (`tables`); no row of one is written without the label (`hypo_hedge.require_label`). A sequenced cell carries,
beside its scorecard, the second firm's opening (role `u_firms.OPENING_ROLE`). None of these beside rows is in the
selection.

**Line (3)(iii)** (an eligible cell's) is the joint engine's pooled call (`u_firms.gate_run`, D-593's): first the
DAY-0 call of the cell's seats at the screen's seed, which at 500 paths must reproduce `rc150_added_lucid.csv`'s `5+K`
rows -- a sequenced cell has no row on record: the call reproduced is its day-0 sibling's --, then the cell itself at
the fresh seed; the rules it leans on are Lucid's as verified (`u_firms.rules_problems`). **Line (3)(iv)** applies
(P-16's coin): each sequence re-deals the cell and its opposite side on P-16's walk and replays them through the joint
engine (`u_firms.coin_jobs`); R* must not be a coin design. **The verdict of a joint cell is never CARRIED** (D-643
(3)): every figure of it is an upper bound while Lucid's funded monthly fee and payout fee are unpriced, so a cell that
holds every line returns `u_select.HOLDS_AS_UPPER_BOUND`, recorded with what it waits for; a line that does not hold
closes the family as ever.

**The run:** every cell on every start at the `verdict` arm; R* from U1's file by D-621 (2) (the best P among `p14`,
`p15`, `p16` on all starts; each measure's own best beside) with R*'s start records; the choice on the early block and
the judgement on the late one, the reverse beside (`u_select.judge`); the year rule. **For the chosen cell only:** the
cell at `point`, beside; then, each only while every line before it holds (the verdict is the first failing line in
D-621's order, so nothing after a failed line is needed): line (3)(iii), the gate floor -- one `gate.run_gate` call in
`rc_screen.Runner`'s form at the fresh campaign seed 20261801, 500 paths, against P-06's row of
`results/scoreboard.csv`, after the same call without overrides at the screen's seed has reproduced
`rc_width_screen.csv`'s row -- and line (3)(iv), the coin guard -- the cell and R* replayed under D-568's fifty
sequences (`rc150_routing.coin_cell`, each sequence its own bounds and capacity as `rc150_routing`'s guard 2) on every
21st start day of the judged block's common dates; R* = P-14 is not a coin design, so its P is the same under every
sequence (read once from U1's records on those dates). A chosen cell on base `p14` takes its gate floor from
`gate_run_p14` and has no coin guard. In `--check` the expensive lines are exercised for the first declared cell of
each base (the NULL family: both references), never for the chosen cell as such, so no line printed depends on a
reading.

Writes `results/u_<family>.csv` (sections `identity`, `cell`, `choice`, `judged`, `reverse`, `guards`, `verdict`; each
`cell` row of a cell replayed here carries its `base`, U1's rows to beat a blank one) with its manifest (the bases
listed); EXPLORATORY; every cell counted under `<row id>:u_<family>`. A resume file outside the checkout, keyed by the
code's commit and the family, keeps every finished replay (D-540).
"""
from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import u_select as Sel  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402

SCRIPT = Sel.SCRIPT
DECISION = Sel.DECISION
U1_FILE = f"{U.RESULT}.csv"
SCOREBOARD = "scoreboard.csv"
REFERENCE = Sel.REFERENCE_CELL              # P-16 with no override: the identity's side, never counted
P16, P15, P14 = "p16", "p15", "p14"
ARM, BESIDE_ARM = Sel.ARM, Sel.BESIDE_ARM
NULL = "null"
#: each base's reference cell (no override: the identity's side, never counted) and its label
REFERENCES = Sel.REFERENCE_CELLS
LABEL = Sel.BASE_LABEL
#: the built-in NULL family (`--check`'s): BOTH bases' reference cells only; never judged, never written to results/
NULL_FAMILY: dict[str, Any] = {"family": NULL, "decision": DECISION, "k": 1,
                               "cells": ({"name": REFERENCE, "overrides": {}},
                                         {"name": REFERENCES[P14], "base": P14, "overrides": {}})}
#: P-14's registered test's files (D-513): its gate campaign's rows -- section `gate` at 0 %, the row the gate call
#: without overrides must reproduce at the registered seed -- and its per-path record (run `gate`)
P14_GATE_FILE = "a3_brk30_cb20_gate.csv"
P14_PATHS_FILE = "a3_brk30_cb20_gate_paths.csv"
P14_GATE_SECTION = P14_GATE_RUN = "gate"
#: the registered rows' readings reproduced, as (shift, column) -- the three `rc150_payout_screen.IDENT_COLS` reads
#: for P-16: the growth on the required bankroll at the bound and at the point, the required bankroll at the bound
P14_IDENT_COLS = (("lower_bound", "pf_growth_on_base_p50"), ("point", "pf_growth_on_base_p50"),
                  ("lower_bound", "pf_required_p90"))
#: the registered families -- NONE yet: a family is declared in its own decision row first (D-621 (6)); the module
#: docstring shows the form
REGISTRY: dict[str, dict[str, Any]] = {}

#: family 1 (D-629): the purchase budget -- K = 10, 15, 30 and none at 21 sessions, on P-16's trades and on P-14's;
#: 20 in 21, each base's own, is its reference and is not a cell
REGISTRY["budget"] = {
    "family": "budget", "decision": "D-629", "k": 1,
    "cells": (
        {"name": "budget10", "overrides": {"purchase_budget": (10, 21)}},
        {"name": "budget15", "overrides": {"purchase_budget": (15, 21)}},
        {"name": "budget30", "overrides": {"purchase_budget": (30, 21)}},
        {"name": "nobudget", "overrides": {"purchase_budget": None}},
        {"name": "budget10_p14", "base": "p14", "overrides": {"purchase_budget": (10, 21)}},
        {"name": "budget15_p14", "base": "p14", "overrides": {"purchase_budget": (15, 21)}},
        {"name": "budget30_p14", "base": "p14", "overrides": {"purchase_budget": (30, 21)}},
        {"name": "nobudget_p14", "base": "p14", "overrides": {"purchase_budget": None}},
    ),
}

#: family 2 (D-630, its pause as D-632 corrects it): the cost of entry -- a wallet stop, a purchase pause until the
#: first payout arrives, a seat ramp -- one setting a cell, on P-16's trades and on P-14's; the base's budget stays on
REGISTRY["entry"] = {
    "family": "entry", "decision": "D-630", "k": 2,
    "cells": (
        {"name": "wallet1000", "overrides": {"wallet_stop": 1000.0}},
        {"name": "wallet1500", "overrides": {"wallet_stop": 1500.0}},
        {"name": "wallet2000", "overrides": {"wallet_stop": 2000.0}},
        {"name": "pause1", "overrides": {"pause_after_funded": 1}},
        {"name": "pause2", "overrides": {"pause_after_funded": 2}},
        {"name": "ramp2", "overrides": {"seat_ramp": 2}},
        {"name": "ramp3", "overrides": {"seat_ramp": 3}},
        {"name": "wallet1000_p14", "base": "p14", "overrides": {"wallet_stop": 1000.0}},
        {"name": "wallet1500_p14", "base": "p14", "overrides": {"wallet_stop": 1500.0}},
        {"name": "wallet2000_p14", "base": "p14", "overrides": {"wallet_stop": 2000.0}},
        {"name": "pause1_p14", "base": "p14", "overrides": {"pause_after_funded": 1}},
        {"name": "pause2_p14", "base": "p14", "overrides": {"pause_after_funded": 2}},
        {"name": "ramp2_p14", "base": "p14", "overrides": {"seat_ramp": 2}},
        {"name": "ramp3_p14", "base": "p14", "overrides": {"seat_ramp": 3}},
    ),
}

#: family 3 (D-635): the number of seats -- 1 to 4 accounts on the single engine, the three seat limits
#: together, on P-16's trades and on P-14's; the base's budget unchanged
REGISTRY["seats"] = {
    "family": "seats", "decision": "D-635", "k": 3,
    "cells": (
        {"name": "seats1", "overrides": {"accounts": 1, "combines": 1, "total_accounts": 1}},
        {"name": "seats2", "overrides": {"accounts": 2, "combines": 2, "total_accounts": 2}},
        {"name": "seats3", "overrides": {"accounts": 3, "combines": 3, "total_accounts": 3}},
        {"name": "seats4", "overrides": {"accounts": 4, "combines": 4, "total_accounts": 4}},
        {"name": "seats1_p14", "base": "p14", "overrides": {"accounts": 1, "combines": 1, "total_accounts": 1}},
        {"name": "seats2_p14", "base": "p14", "overrides": {"accounts": 2, "combines": 2, "total_accounts": 2}},
        {"name": "seats3_p14", "base": "p14", "overrides": {"accounts": 3, "combines": 3, "total_accounts": 3}},
        {"name": "seats4_p14", "base": "p14", "overrides": {"accounts": 4, "combines": 4, "total_accounts": 4}},
    ),
}

#: family 4 (D-639, its readings D-641): the user's hours -- the coin in one session window at the 25-point and
#: the 37.5-point stop; each cell is its window base itself (own trades, bounds, capacity; the R cap where D-212
#: asks for one), with no override
REGISTRY["hours"] = {
    "family": "hours", "decision": "D-639", "k": 4,
    "cells": (
        {"name": "london25", "base": "s100_london", "overrides": {}},
        {"name": "london37_5", "base": "s150_london", "overrides": {}},
        {"name": "us25", "base": "s100_us", "overrides": {}},
        {"name": "us37_5", "base": "s150_us", "overrides": {}},
        {"name": "asia25", "base": "s100_asia", "overrides": {}},
        {"name": "asia37_5", "base": "s150_asia", "overrides": {}},
    ),
}
#: family 6 (D-646): the Consistency payout path chosen at activation, on the tables on file (solved for the Standard
#: path) -- P-16 and P-14 on the path, and P-16 on the path with the funded leg's micro cap at 2/3 and 1/3 (the
#: stand-in for a table solved for the path); every cell names the verified rules it leans on
CONSISTENCY_RULES = ("xfa_payout_path_choice", "xfa_cons_min_days", "xfa_cons_max_day_frac", "xfa_cons_cap")
REGISTRY["consistency"] = {
    "family": "consistency", "decision": "D-646", "k": 6,
    "cells": (
        {"name": "cons", "overrides": {"protocol": {"payout_path": "consistency"}}, "rules": CONSISTENCY_RULES},
        {"name": "cons_p14", "base": "p14", "overrides": {"protocol": {"payout_path": "consistency"}},
         "rules": CONSISTENCY_RULES},
        {"name": "cons_cap2of3", "overrides": {"protocol": {"payout_path": "consistency"},
                                               "funded_cap_share": 100 / 150}, "rules": CONSISTENCY_RULES},
        {"name": "cons_cap1of3", "overrides": {"protocol": {"payout_path": "consistency"},
                                               "funded_cap_share": 50 / 150}, "rules": CONSISTENCY_RULES},
    ),
}
#: family 5 (D-643 as D-644 widens it; built D-647): the multi-firm portfolio -- Lucid seats 1, 2 or 5 beside P-16's
#: five Topstep seats, opened on day 0 or at the first payout's arrival, under three deals; each cell is its joint
#: base itself, with no override. The six unhedged cells are eligible (`lucid_upper_bound`); the twelve hedged cells
#: are `hypothetical_hedge` -- written beside, refused wherever a cell is chosen or judged
REGISTRY["firms"] = {
    "family": "firms", "decision": "D-644", "k": 5,
    "cells": tuple({"name": b, "base": b, "overrides": {}} for b in Sel.JOINT_BASES),
}
#: family 7 (D-653, as D-654 amends it before its run): the funded plan with no bold opening -- the base's table with
#: its funded phase (activation to the first payout) replaced by one leaf, X dollars at 1R; X = 250, 500, 1,000 on the
#: Standard path (the paid phase the base's) and on the Consistency path chosen at activation (the paid phase the same
#: leaf), on P-16's trades and on P-14's. The Consistency cells name D-645's four rules
REGISTRY["plan"] = {
    "family": "plan", "decision": "D-653", "k": 7,
    "cells": tuple(
        {"name": f"flat{x}" + ("_cons" if cons else "") + ("" if base == P16 else f"_{base}"),
         **({} if base == P16 else {"base": base}),
         "overrides": {"funded_plan": {"risk": float(x), "rr": 1.0, **({"paid": True} if cons else {})},
                       **({"protocol": {"payout_path": "consistency"}} if cons else {})},
         **({"rules": CONSISTENCY_RULES} if cons else {})}
        for base in (P16, P14) for cons in (False, True) for x in (250, 500, 1000)),
}
#: family 8 (D-658; chosen after family 7 was read): the flat funded plan at the size limit on P-16's trades --
#: $1,500 at 1R (the entry tier's allowance at the 37.5-point stop), on the Consistency path (the paid phase the same
#: leaf) and on the Standard path (the paid phase the base's)
REGISTRY["limit"] = {
    "family": "limit", "decision": "D-658", "k": 8,
    "cells": (
        {"name": "flat1500_cons",
         "overrides": {"funded_plan": {"risk": 1500.0, "rr": 1.0, "paid": True},
                       "protocol": {"payout_path": "consistency"}}, "rules": CONSISTENCY_RULES},
        {"name": "flat1500", "overrides": {"funded_plan": {"risk": 1500.0, "rr": 1.0}}},
    ),
}
#: family 9 (D-659, as D-662 amends it before its run): the crippled funded account resolved at once -- in the
#: base's table's funded phase every state whose balance is below the account's starting balance risks its room (the
#: cushion band's lower edge) at R = r, one trade a session; the band from a room of zero keeps the base's own leaves
#: (they already ask at least the room); r = 1.5 and 3 on P-16's trades and on P-14's, the Standard path
REGISTRY["resolve"] = {
    "family": "resolve", "decision": "D-659", "k": 9,
    "cells": tuple(
        {"name": f"resolve{tag}" + ("" if base == P16 else f"_{base}"), **({} if base == P16 else {"base": base}),
         "overrides": {"funded_resolve": {"rr": r, "lowest": "base"}}}
        for base in (P16, P14) for tag, r in (("1_5", 1.5), ("3", 3.0))),
}
#: `--check-overrides`' cell: one cell of the NULL family, never counted outside the check's temporary folder
CHECK_CELL = "check_overrides"
#: D-630's entry options: the key of each option's value in its `LockstepPath` record and in the gate's columns
ENTRY_RECORD_KEY = {"wallet_stop": "w", "pause_after_funded": "f", "seat_ramp": "s0"}
ENTRY_GATE_KEY = {"wallet_stop": "wallet_stop_w", "pause_after_funded": "pause_after_funded_f",
                  "seat_ramp": "seat_ramp_s0"}
#: the role and measure role of a cell's rows that read an entry option's own record: beside, never in the selection
ENTRY_ROLE = "family cell: the option's own record over each start's long replay (beside; never in the selection)"
ENTRY_MEASURE_ROLE = "beside"
#: columns of U1's start rows that name the configuration, not the start
NAME_COLS = ("section", "config", "arm", "label", "cell")


# ------------------------------------------------------------------------------------------------ the overrides


def funded_cap(rule: Any, share: float) -> Any:
    """The sizing rule with the funded leg's micro cap scaled by `share` (floor) -- `resolved_coin.FundedCapRule`, as
    `resolved_coin.funded_cap_rule` builds it from two stops; the rule itself at a share of 1."""
    from propedge.campaign.sizing import SizingRule
    from propedge.research import resolved_coin as rc

    if isinstance(rule, rc.FundedCapRule):
        raise ValueError("the base sizing rule already carries a funded cap")
    if float(share) == 1.0:
        return rule
    return rc.FundedCapRule(**{f.name: getattr(rule, f.name) for f in dataclasses.fields(SizingRule)},
                            funded_scale=float(share))


def apply_overrides(kw: dict[str, Any], budget: tuple[int, int] | None, overrides: dict[str, Any], *,
                    base: str = Sel.DEFAULT_BASE, plan: Any = None, blocks: Any = None
                    ) -> tuple[dict[str, Any], tuple[int, int] | None]:
    """A cell's overrides on `gate.run_gate`'s arguments (`kw`, as `customer_slices.Campaign.kw` or
    `atlas_a3.gate_kwargs` holds them) and the purchase budget: (the new arguments -- a copy; the base is untouched --
    and the cell's budget). No override: the arguments and budget as they were. `base`: the setup the arguments are
    (`u_select.BASES`); a kind refused on it (`funded_cap_share` on `p14`) raises. D-630's entry options
    (`u_select.ENTRY_KINDS`) are set on the arguments under their own names -- `gate.run_gate` takes them as they are
    and `customer_slices.engine_args` reads them from the campaign's arguments for the replay; a `seat_ramp` is below
    the cell's seats, and without a seat override those must be the base's (`u_select.BASE_SEATS`).

    `plan`: the base's TABLE -- needed by D-653's `funded_plan` only, and then required (the campaign's own
    `risk_policy` argument may be another table: P-13's v12 under P-14's no-closure plan). The cell's table
    (`flat_plan`) is set as the arguments' `risk_policy` -- the caller hands THAT to the replay (`cell_table`) -- and
    the funded leg's keys follow the plan's fresh funded decision, as D-641's window bases re-point theirs: `e` and
    `lb` (the gap the blocks' base column takes on the bound arm) are the plan's R's, and the protocol's funded leg is
    the plan's R and dollars. Every trade is still read at its own leaf's R and shifted by that R's own gap
    (`e_by_rr`, `lb_by_rr`, untouched); a plan whose R -- or any R its table asks for -- has no bound there raises.

    D-659's `funded_resolve` needs `plan` too, and the base's trades -- `blocks`, or the arguments' own `blocks` where
    they carry them (the gate's) -- for one micro's dollars at the base's stop (`one_micro_dollars`). The cell's table
    (`resolve_plan`) is set as the arguments' `risk_policy` and NOTHING ELSE moves: the table's fresh funded decision
    is the base's own (a fresh account stands at its starting balance, which the plan leaves to the base), so `e`,
    `lb` and the protocol's funded leg -- which follow that decision -- are already right; every trade is read at its
    own leaf's R and shifted by that R's own gap, and an R the table asks for with no edge and bound there raises."""
    from propedge.campaign.lockstep import (
        check_pause_after_funded,
        check_purchase_budget,
        check_seat_ramp,
        check_wallet_stop,
    )
    from propedge.contract.payout_timing import check_payout_timing

    bad = Sel.override_problems(overrides, base)
    if bad:
        raise ValueError("; ".join(bad))
    out = dict(kw)
    for k in Sel.SEAT_KEYS:
        if k in overrides:
            out[k] = int(overrides[k])
    if "funded_cap_share" in overrides:
        out["sizing"] = funded_cap(kw["sizing"], float(overrides["funded_cap_share"]))
    if "protocol" in overrides:
        out["protocol"] = dataclasses.replace(kw["protocol"], **dict(overrides["protocol"]))
    if "payout_timing" in overrides:
        out["payout_timing"] = check_payout_timing(overrides["payout_timing"])
    if "purchase_budget" in overrides:
        b = overrides["purchase_budget"]
        budget = None if b is None else check_purchase_budget(tuple(int(x) for x in b))
    if Sel.FUNDED_PLAN in overrides:                        # D-653: the base's table, its funded phase one leaf
        import zero_edge_decomposition as zd

        spec = overrides[Sel.FUNDED_PLAN]
        if plan is None:
            raise ValueError(f"{Sel.FUNDED_PLAN} is built from the base's table: hand it in (plan=) -- the campaign's "
                             "own risk_policy argument may be another table")
        flat, _ = flat_plan(plan, spec)
        rr = float(spec["rr"])
        e_by = {float(k): float(v) for k, v in (kw.get("e_by_rr") or {}).items()}
        lb_by = {float(k): float(v) for k, v in (kw.get("lb_by_rr") or {}).items()}
        missing = sorted({rr, *zd.policy_rrs(flat)} - (set(e_by) & set(lb_by)))
        if missing:
            raise ValueError(f"{Sel.FUNDED_PLAN}: the campaign carries no edge and bound at "
                             + ", ".join(f"{R:g}R" for R in missing) + " -- an R the plan's table asks for")
        out["risk_policy"] = flat
        out["e"], out["lb"] = e_by[rr], lb_by[rr]
        out["protocol"] = dataclasses.replace(out["protocol"], funded_rr=rr, funded_risk=float(spec["risk"]))
    if Sel.FUNDED_RESOLVE in overrides:                     # D-659: the base's table, bold below the starting balance
        import zero_edge_decomposition as zd

        spec = overrides[Sel.FUNDED_RESOLVE]
        if plan is None:
            raise ValueError(f"{Sel.FUNDED_RESOLVE} is built from the base's table: hand it in (plan=) -- the "
                             "campaign's own risk_policy argument may be another table")
        blk = blocks if blocks is not None else kw.get("blocks")
        if blk is None:
            raise ValueError(f"{Sel.FUNDED_RESOLVE} needs the base's trades for one micro's dollars at the base's "
                             "stop: hand them in (blocks=)")
        table, _ = resolve_plan(plan, spec, one_micro_dollars(blk))
        e_by = {float(k) for k in (kw.get("e_by_rr") or {})}
        lb_by = {float(k) for k in (kw.get("lb_by_rr") or {})}
        missing = sorted({float(spec["rr"]), *zd.policy_rrs(table)} - (e_by & lb_by))
        if missing:
            raise ValueError(f"{Sel.FUNDED_RESOLVE}: the campaign carries no edge and bound at "
                             + ", ".join(f"{R:g}R" for R in missing) + " -- an R the cell's table asks for")
        out["risk_policy"] = table                          # e, lb and the protocol's funded leg: the base's, unmoved
    if "wallet_stop" in overrides:                          # D-630 (a)
        out["wallet_stop"] = check_wallet_stop(float(overrides["wallet_stop"]))
    if "pause_after_funded" in overrides:                   # D-630 (b), D-632
        out["pause_after_funded"] = check_pause_after_funded(overrides["pause_after_funded"])
    if "seat_ramp" in overrides:                            # D-630 (c)
        seats = out.get("total_accounts")
        if not any(k in overrides for k in Sel.SEAT_KEYS) and (seats is None or int(seats) != Sel.BASE_SEATS[base]):
            raise ValueError(f"the base's total accounts are {seats!r}, not u_select.BASE_SEATS' "
                             f"{Sel.BASE_SEATS[base]}: seat_ramp ramps up to the base's seats")
        out["seat_ramp"] = check_seat_ramp(overrides["seat_ramp"], seats)
        if out["seat_ramp"] >= int(seats):
            raise ValueError(f"seat_ramp {out['seat_ramp']} is not below the cell's seats ({int(seats)})")
    return out, budget


# ------------------------------------------------------------------------------------------------ D-653: the funded plan

#: the role of a plan cell's fact rows: inputs read from the table and the sizing rule, never a reading
PLAN_FACT_ROLE = ("funded plan: the table's replaced phase and the plan's dollars at each stop and tier (D-653 (1), "
                  "(2); inputs from the table and the sizing rule, fixed before anything runs; never a reading, never "
                  "in the selection)")


def funded_plan_of(overrides: dict[str, Any] | None) -> dict[str, Any] | None:
    """A cell's `funded_plan` override (D-653), or None."""
    return (overrides or {}).get(Sel.FUNDED_PLAN)


def funded_resolve_of(overrides: dict[str, Any] | None) -> dict[str, Any] | None:
    """A cell's `funded_resolve` override (D-659), or None."""
    return (overrides or {}).get(Sel.FUNDED_RESOLVE)


def own_table_kind(overrides: dict[str, Any] | None) -> str | None:
    """The override kind that gives a cell a table of its own -- `funded_plan` (D-653) or `funded_resolve` (D-659;
    never both, `u_select.override_problems`) -- or None: the cell runs on its base's table."""
    if funded_plan_of(overrides) is not None:
        return Sel.FUNDED_PLAN
    return Sel.FUNDED_RESOLVE if funded_resolve_of(overrides) is not None else None


#: the decision row each own-table kind is declared in (for a refusal's words)
OWN_TABLE_DECISION = {Sel.FUNDED_PLAN: Sel.FUNDED_PLAN_DECISION, Sel.FUNDED_RESOLVE: Sel.FUNDED_RESOLVE_DECISION}


def cell_table(kw: dict[str, Any], plan: Any, overrides: dict[str, Any] | None) -> Any:
    """The table a cell's replay is handed: the base's `plan`, or -- for a `funded_plan` or a `funded_resolve` cell --
    the cell's own table, which `apply_overrides` set on the arguments (`kw`)."""
    return kw["risk_policy"] if own_table_kind(overrides) is not None else plan


def _plan_states() -> list[dict[str, Any]]:
    """A spread of account states over every variable a table reads (balance, cushion, winning days, the request
    day, the payout-line gap, the days in state), in each phase -- for comparing two tables' decisions."""
    from propedge.campaign.risk_policy import MLL, NO_LINE

    out = []
    balances = (-1900.0, -750.0, -0.01, 0.0, 0.01, 260.0, 990.0, 1500.0, 2010.0, 2999.99, 4400.0, 9000.0)
    for phase in ("combine", "funded", "paid"):
        for i, bal in enumerate(balances):
            for j, cush in enumerate((0.0, 240.0, 760.0, 1250.0, 2000.0)):
                for win in ((0,) if phase == "combine" else (0, 2, 4, 5)):
                    for req in ((0,) if phase == "combine" else (0, 1)):
                        gap = NO_LINE if phase != "paid" else (-1200.0, -300.0, 0.0, 0.01, 800.0)[(i + j + win) % 5]
                        out.append({"phase": phase, "balance": bal, "cushion": cush, "cushion_frac": cush / MLL,
                                    "days_in_state": (i * 7 + j) % 40, "day": 0, "win_days": win, "line_gap": gap,
                                    "request_day": req})
    return out


def flat_plan_problems(plan: Any, flat: Any, spec: dict[str, Any]) -> list[str]:
    """Every way `flat` is not `plan` with its funded phase replaced by D-653's one leaf and nothing else changed: the
    plain data (`u_select.funded_plan_dict_problems`: the evaluation's and the paid phase's subtrees equal to the
    base's, the funded phase one trading leaf at the plan's dollars and R, the id, the version); over a spread of
    states (`_plan_states`) every funded state decides the plan's dollars and R, a routed strategy trade that neither
    abandons nor sits out -- whatever the winning days, the cushion or the request day -- and every evaluation and
    paid state decides exactly what the base decides; plain data that pickles. With the spec's `"paid": true` the
    paid phase is the plan's too: its subtree is the one leaf under the paid phase's name and every paid state --
    the request day and five winning days among them -- decides the plan's dollars and R; only the evaluation's
    states are then compared with the base's."""
    import pickle

    risk, rr, paid = float(spec["risk"]), float(spec["rr"]), Sel.funded_plan_paid(spec)
    a, b = plan.as_dict(), flat.as_dict()
    out = Sel.funded_plan_dict_problems(a, b, risk, rr, paid)
    for s in _plan_states():
        d = flat.decide(s)
        if s["phase"] == "funded" or (paid and s["phase"] == "paid"):
            if (float(d.risk) != risk or d.rr is None or float(d.rr) != rr or d.abandon or d.source != "strategy"
                    or d.max_trades == 0 or d.regime != f"{s['phase']} / "
                    + Sel.funded_plan_leaf_name(risk, rr, s["phase"])):
                out.append(f"a {s['phase']} state does not decide the plan's dollars and R")
                break
        else:
            w = plan.decide(s)
            if (d.regime, d.risk, d.rr, d.max_trades, d.abandon, d.source) != (
                    w.regime, w.risk, w.rr, w.max_trades, w.abandon, w.source):
                out.append(f"a {s['phase']} state does not decide what the base decides")
                break
    if not Sel._plain(b) or pickle.loads(pickle.dumps(flat)).as_dict() != b:
        out.append("the plan's table is not plain data that pickles")
    return out


def flat_plan(plan: Any, spec: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    """(the table a `funded_plan` cell runs on, what it replaced): the base's table rebuilt from
    `u_select.funded_plan_policy_dict`'s plain data by `RiskPolicy.from_dict` -- which validates it: a tier-1 breach
    raises `ConductViolation` and is a stop, never worked around -- refused unless `flat_plan_problems` finds nothing.
    With the spec's `"paid": true` the paid phase is replaced too (`u_select.funded_plan_policy_dict(paid=True)`).
    The record: the leaves the one leaf replaces, the no-trade leaves among them, the trade limit it carries, and the
    table's tier-2 conduct flags (allowed, reported: a 1R leaf's "winners not larger than losers") -- the plan's, those
    of them the base's table does not carry, and the base's count."""
    from propedge.campaign.risk_policy import RiskPolicy

    paid = Sel.funded_plan_paid(spec)
    d, n = Sel.funded_plan_policy_dict(plan.as_dict(), spec["risk"], spec["rr"], paid)
    out = RiskPolicy.from_dict(d)
    out.validate()
    bad = flat_plan_problems(plan, out, spec)
    if bad:
        raise ValueError(f"REFUSED ({Sel.FUNDED_PLAN_DECISION}): the plan's table is not the base's with its funded "
                         "phase replaced -- " + "; ".join(bad[:4]))
    flags = [f.replace(f"policy {out.id!r}, ", "") for f in out.conduct_flags()]
    was = [f.replace(f"policy {plan.id!r}, ", "") for f in plan.conduct_flags()]
    return out, {**n, "table": out.id, "base_table": plan.id,
                 "leaf": Sel.funded_plan_leaf_name(spec["risk"], spec["rr"]),
                 "paid_leaf": Sel.funded_plan_leaf_name(spec["risk"], spec["rr"], "paid") if paid else "",
                 "conduct_flags": flags, "conduct_flags_new": [f for f in flags if f not in was],
                 "conduct_flags_base": len(was)}


def plan_sizing(sizing: Any, blocks: list, risk: float) -> list[dict[str, Any]]:
    """The plan's dollars as micros, from the SIZING RULE alone (no campaign, no outcome): for every risk per micro
    the cell's trades carry (their stops) and every tier of the funded ladder, `sizing.size_trade` under the funded
    cap at that tier's balance, and whether the engine would take the trade (`TierSizedDraw._plain_size`'s
    stand-aside: the cost floor, the least share of the risk) -- {risk_per_micro, from_balance, cap_micros, micros,
    realised, at_cap, taken}."""
    from propedge.campaign.sizing import size_trade

    rpcs = sorted({float(x) for b in blocks if len(b) for x in np.asarray(b.risk_per_contract, float)})
    sa = sizing.stand_aside_for("funded")
    out = []
    for rpc in rpcs:
        for lo in sizing.ladder.thresholds:
            cap = sizing.cap_micros("funded", float(lo))
            s = size_trade(float(risk), rpc, cap)
            stood = sa is not None and (s.realised_risk + 1e-9 < sa[0] * s.intended_risk
                                        or s.risk_per_contract + 1e-9 < sa[1])
            out.append({"risk_per_micro": rpc, "from_balance": float(lo), "cap_micros": cap, "micros": int(s.contracts),
                        "realised": float(s.realised_risk), "at_cap": bool(s.at_cap),
                        "taken": bool(s.contracts >= 1 and not stood)})
    return out


def plan_cell_problems(jobs: dict[str, dict], plan: Any, spec: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """A `funded_plan` cell's jobs (both arms) against D-653 (1): (the problems, the cell's facts). The table in the
    replay's engine arguments is `flat_plan(plan, spec)`'s at each arm; every R it asks for is carried by every day's
    block (the outcomes and, by `apply_overrides`, the bounds); the protocol's funded leg is the plan's R and dollars;
    **on the bound arm the blocks' base column is their own column at the plan's R** -- the campaign's `e` and `lb`
    were re-pointed to the plan's R, so the base column took that R's gap (on the base it takes the fresh funded
    R's); and the plan's dollars buy at least one micro at every stop the trades carry and every tier of the funded
    ladder, none standing aside (`plan_sizing`). A problem names the check, never a value."""
    import zero_edge_decomposition as zd

    flat, info = flat_plan(plan, spec)
    risk, rr = float(spec["risk"]), float(spec["rr"])
    want = flat.as_dict()
    need = set(zd.policy_rrs(flat))
    bad: list[str] = []
    sizing = None
    for arm, job in jobs.items():
        got = job["args"]["path"].get("risk_policy")
        if getattr(got, "id", None) != flat.id or got.as_dict() != want:
            bad.append(f"{arm}: the replay's table is not the plan's")
        proto = job["args"]["draws"]["protocol"]
        if float(proto.funded_rr) != rr or float(proto.funded_risk) != risk:
            bad.append(f"{arm}: the protocol's funded leg is not the plan's R and dollars")
        if any(len(b) and not need <= {float(k) for k in (b.r_by_rr or {})} for b in job["blocks"]):
            bad.append(f"{arm}: a day's block does not carry an R the plan's table asks for")
        elif arm == ARM and not all(np.allclose(np.asarray(b.pnl, float),
                                                np.asarray(b.r_by_rr[rr], float) * np.asarray(b.risked, float),
                                                rtol=0.0, atol=1e-9, equal_nan=True)
                                    for b in job["blocks"] if len(b)):
            bad.append(f"{arm}: the blocks' base column is not their column at the plan's R (the edge and bound keys "
                       "were not re-pointed)")
        sizing = job["args"]["draws"]["sizing"]
    sized = plan_sizing(sizing, next(iter(jobs.values()))["blocks"], risk) if sizing is not None else []
    if not sized or not all(x["taken"] for x in sized):
        bad.append("the plan's dollars do not buy a micro at every stop and tier, or a trade stands aside")
    return bad, {**info, "risk": risk, "rr": rr, "paid": Sel.funded_plan_paid(spec), "sizing": sized}


def plan_lines(name: str, base: str, facts: dict[str, Any]) -> list[str]:
    """A plan cell's facts as the lines printed before anything runs: inputs from the table and the sizing rule."""
    out = [f"fact: {name} on base {base} ({Sel.FUNDED_PLAN_DECISION} (1)): the table {facts['table']} -- "
           f"{facts['base_table']} with its funded phase's {facts['funded_leaves']} leaves "
           f"({facts['funded_no_trade_leaves']} of them no-trade states) replaced by the one leaf "
           f"{facts['leaf']!r}"
           + (f" and its paid phase's {facts['paid_leaves']} leaves ({facts['paid_no_trade_leaves']} of them "
              f"no-trade states) by the one leaf {facts['paid_leaf']!r}" if facts.get("paid_replaced") else
              "; the paid phase the base's")
           + f", {facts['max_trades']} trade(s) a session; tier 1 none (the table validates); tier-2 "
           f"conduct flags {len(facts['conduct_flags'])} against the base table's {facts['conduct_flags_base']}, "
           f"{len(facts['conduct_flags_new'])} of them new with the plan"]
    out += [f"    fact: tier-2 flag (allowed, reported{', new' if f in facts['conduct_flags_new'] else ''}): {f}"
            for f in facts["conduct_flags"]]
    for rpc in sorted({x["risk_per_micro"] for x in facts["sizing"]}):
        out.append(f"    fact: ${facts['risk']:,.0f} on a ${rpc:g}-a-micro stop"
                   + (" (before and after a first payout)" if facts.get("paid_replaced") else "") + ": " + "; ".join(
            f"balance from ${x['from_balance']:,.0f}: {x['micros']} micros, ${x['realised']:,.0f}"
            + (" (at the cap)" if x["at_cap"] else "") + ("" if x["taken"] else " -- NOT TAKEN")
            for x in facts["sizing"] if x["risk_per_micro"] == rpc))
    return out


def plan_rows(cell: str, base: str, facts: dict[str, Any], overrides: dict[str, Any]) -> list[dict[str, Any]]:
    """A plan cell's facts as section `cell` rows beside its scorecard (`PLAN_FACT_ROLE`; `measure` is
    `plan.<key>`)."""
    vals = [("risk", "the plan's dollars a funded trade before the first payout", Sel.DOLLARS, facts["risk"]),
            ("rr", "the plan's R", "R", facts["rr"]),
            ("funded_leaves_replaced", "the base table's funded leaves the one leaf replaces", "leaves",
             facts["funded_leaves"]),
            ("funded_no_trade_leaves_replaced", "the no-trade leaves among them", "leaves",
             facts["funded_no_trade_leaves"]),
            ("paid_replaced", "the plan's leaf replaces the paid phase too (1) or the paid phase is the base's (0)",
             "flag", int(bool(facts.get("paid_replaced")))),
            ("paid_leaves_replaced", "the base table's paid leaves the one leaf replaces", "leaves",
             facts.get("paid_leaves", 0)),
            ("paid_no_trade_leaves_replaced", "the no-trade leaves among them", "leaves",
             facts.get("paid_no_trade_leaves", 0)),
            ("conduct_flags", "the table's tier-2 conduct flags (allowed, reported)", "flags",
             len(facts["conduct_flags"])),
            ("conduct_flags_base", "the base table's tier-2 conduct flags", "flags", facts["conduct_flags_base"]),
            ("conduct_flags_new", "the tier-2 flags the base's table does not carry", "flags",
             len(facts["conduct_flags_new"]))]
    vals += [(f"realised_rpc{x['risk_per_micro']:g}_from{x['from_balance']:g}",
              f"the plan's realised dollars on a ${x['risk_per_micro']:g}-a-micro stop at a balance from "
              f"${x['from_balance']:,.0f} ({x['micros']} micros under a cap of {x['cap_micros']})", Sel.DOLLARS,
              x["realised"]) for x in facts["sizing"]]
    return [{"section": "cell", "cell": cell, "base": base, "role": PLAN_FACT_ROLE, "arm": "", "block": "all",
             "measure": f"plan.{k}", "what": what, "direction": "", "unit": unit, "measure_role": FACT_MEASURE_ROLE,
             "value": float(v), "n": 0, "counted": False, "overrides": json.dumps(overrides, sort_keys=True)}
            for k, what, unit, v in vals]


def evaluation_leg_problems(outs: list[dict[str, Any]], ref: list[dict[str, Any]]) -> list[str]:
    """D-653 (7): a `funded_plan` cell's starts against its base's reference (the same starts, the same arm) -- the
    plan changes only what a funded account trades, so **nothing differs before a funded account exists**. Per start,
    with `a` the base's first funded account's activation day (it trades from the next session): (i) the cell's first
    funded account is activated on `a` too; (ii) the pass, activation and payout days up to `a` are the base's; (iii)
    the first pass and the cash spent before it are the base's; (iv) every month-end net and fee at or before `a`
    (and the 30-session net) is the base's. A start whose base never funds an account carries the base's record whole
    (`user_journey.record_problems`, its exact-length runs too). From the records the runner keeps: the long replay's.
    A problem names the reading and the count, never a value."""
    by = {int(x["rec"]["start_day"]): x["rec"] for x in ref}
    if sorted(by) != sorted(int(x["rec"]["start_day"]) for x in outs):
        return [f"the starts differ ({len(outs)} against the reference's {len(by)})"]
    bad: dict[str, int] = {}

    def note(what: str) -> None:
        bad[what] = bad.get(what, 0) + 1

    def blank(x: Any) -> bool:
        return Sel._blank(x)

    def money(x: Any, y: Any) -> bool:
        return (blank(x) and blank(y)) if (blank(x) or blank(y)) else abs(float(x) - float(y)) <= U.TOL

    for x in outs:
        r, t = x["rec"], by[int(x["rec"]["start_day"])]
        a = t["first_funded"]
        if blank(a):
            for k in U.record_problems(r, t) + ([] if sorted(r.get("alt") or {}) == sorted(t.get("alt") or {})
                                                else ["alt"]):
                note(f"no funded account on the base, {k} is not the base's")
            continue
        a = int(a)
        if blank(r["first_funded"]) or int(r["first_funded"]) != a:
            note("the first funded account's activation day")
            continue
        if U.events_upto(r["pass_days"], r["funded_days"], r["pay_days"], a) != U.events_upto(
                t["pass_days"], t["funded_days"], t["pay_days"], a):
            note("the event days up to the first funded account")
        for k in ("first_pass", "spent_before_first_pass"):
            if not money(r[k], t[k]):
                note(k)
        for m in range(1, U.MONTHS + 1):
            if U.MONTH * m <= a:
                for k in ("net_month", "fees_month"):
                    if not money(r[k][m - 1], t[k][m - 1]):
                        note(f"{k} up to the first funded account")
        if U.EXTRA_NET_DAY <= a and not money(r["net_30"], t["net_30"]):
            note("net_30 up to the first funded account")
    return [f"{k}: {n} starts" for k, n in bad.items()]


# ---------------------------------------------------------------------------------------------- D-659: resolved at once

#: the role of a resolve cell's fact rows: inputs read from the table and the sizing rule, never a reading
RESOLVE_FACT_ROLE = ("funded resolve: the table's replaced states and the bold leaf's dollars at each cushion band and "
                     "stop (D-659 (1); inputs from the table and the sizing rule, fixed before anything runs; never a "
                     "reading, never in the selection)")
#: the under-water identity's starts in a family run: every 21st start (every start of a check) -- a thinning declared
#: for cost, as the coin line's is (D-621 (3)(iv)): the identity needs the engine's daily recorder, which the counted
#: replays run without, so each of its starts is replayed twice more (the cell and its base, the long replay only)
RESOLVE_IDENTITY_EVERY = Sel.COIN_EVERY
#: (the base's table, the R, one micro's dollars) -> the cell's table and its record: the base's table is held, so its
#: id cannot be reused; the table is built and checked over its whole grid once, not once a coin sequence
_RESOLVE_MEMO: dict[tuple, tuple] = {}
#: how a bold leaf reads in a recorded regime (`u_select.funded_resolve_leaf_name`, the last name of the path)
_BOLD = " / " + Sel.funded_resolve_leaf_name(1.0, 1.0).split("$")[0]


def one_micro_dollars(blocks: Any) -> float:
    """D-659 (1)'s "one micro at the base's stop", in dollars: the LARGEST risk per micro among the base's trades --
    its widest stop -- so the least a bold leaf asks for buys a whole micro on every trade the base routes (P-16 trades
    one stop; P-14 two rungs, and its wider one is taken). From the trades' stops alone, never an outcome."""
    top = 0.0
    for b in blocks:
        if len(b):
            if b.risk_per_contract is None:
                raise ValueError("the base's trades carry no risk per micro: one micro's dollars cannot be read")
            top = max(top, float(np.max(np.asarray(b.risk_per_contract, float))))
    if not (np.isfinite(top) and top > 0):
        raise ValueError("the base's trades carry no stop: one micro's dollars cannot be read")
    return float(top)


def _resolve_states(plan: Any) -> list[dict[str, Any]]:
    """The funded states two tables are compared on, from the base table's OWN grid: every funded balance band's edge,
    a cent under it and a cent over it (the starting balance's among them) and each band's middle, a balance under the
    lowest band and one over the highest; every cushion band's edge likewise and a room over the highest; every count
    of winning days from none to one past the table's last; the request day on and off."""
    from propedge.campaign.risk_policy import MLL, NO_LINE

    funded = plan.as_dict()["root"]["funded"]
    b_edges = sorted({float(x["from"]) for x in funded["tiers"]})
    c_edges = sorted({float(y["from"]) for x in funded["tiers"] if x["policy"].get("type") == "tiers"
                      and x["policy"].get("on") == "cushion" for y in x["policy"]["tiers"]})
    balances = sorted({round(e + k, 2) for e in b_edges for k in (-0.01, 0.0, 0.01)}
                      | {round((x + y) / 2.0, 2) for x, y in zip(b_edges, b_edges[1:]) if y - x > 0.05}
                      | {b_edges[0] - 500.0, b_edges[-1] + 3000.0})
    cushions = sorted({round(e + k, 2) for e in c_edges for k in (-0.01, 0.0, 0.01) if e + k >= 0.0}
                      | {round((x + y) / 2.0, 2) for x, y in zip(c_edges, c_edges[1:])} | {c_edges[-1] + 500.0})
    return [{"phase": "funded", "balance": bal, "cushion": cush, "cushion_frac": cush / MLL,
             "days_in_state": (i + j) % 40, "day": 0, "win_days": win, "line_gap": NO_LINE, "request_day": req}
            for i, bal in enumerate(balances) for j, cush in enumerate(cushions) for win in range(7) for req in (0, 1)]


def resolve_plan_problems(plan: Any, table: Any, spec: dict[str, Any], min_risk: float) -> list[str]:
    """Every way `table` is not `plan` with D-659's bold leaves below the starting balance and nothing else changed:
    (a) the plain data (`u_select.funded_resolve_dict_problems`: the evaluation's and the paid phase's subtrees and
    every funded band at or above the starting balance equal to the base's; every band below it the bold leaves on
    the base's cushion grid; the id, the version); (b) over the table's whole grid of funded states
    (`_resolve_states`), through `RiskPolicy.decide` on both tables, **every state at or above the starting balance
    decides exactly what the base decides** -- regime, dollars, R, trade limit, abandon, source; the fresh account's
    opening among them -- and (c) **every state below it decides the bold leaf**: the dollars of its room's band's
    lower edge on that balance band's own cushion grid -- above zero, never more than the room, except where they are
    the one-micro least (`min_risk`) -- at the plan's R, one routed strategy trade, never abandon, never a no-trade
    state; every evaluation and paid state of `_plan_states` decides what the base decides; (d) plain data that
    pickles."""
    import pickle
    from bisect import bisect_right

    rr, least, lowest = float(spec["rr"]), float(min_risk), Sel.funded_resolve_lowest(spec)
    a, b = plan.as_dict(), table.as_dict()
    out = Sel.funded_resolve_dict_problems(a, b, rr, least, lowest)
    if out:
        return out                                          # the grids below are read from a table of that shape
    tiers = b["root"]["funded"]["tiers"]
    froms = [float(x["from"]) for x in tiers]

    def edge(bal: float, cush: float) -> float:
        i = max(bisect_right(froms, bal) - 1, 0)
        cf = [float(y["from"]) for y in tiers[i]["policy"]["tiers"]]
        return cf[max(bisect_right(cf, cush) - 1, 0)]

    def dec(d: Any) -> tuple:
        return (d.regime, d.risk, d.rr, d.max_trades, d.abandon, d.source)

    seen = {"bold": 0, "base": 0}
    for s in _resolve_states(plan):
        d = table.decide(s)
        if s["balance"] >= Sel.FUNDED_RESOLVE_START:
            seen["base"] += 1
            if dec(d) != dec(plan.decide(s)):
                out.append("a funded state at or above the starting balance does not decide what the base decides")
                break
        elif lowest == "base" and edge(s["balance"], s["cushion"]) < least:
            if dec(d) != dec(plan.decide(s)):               # the band under one micro, left to the base
                out.append("a funded state in the band under one micro does not decide what the base decides")
                break
        else:
            seen["bold"] += 1
            risk = Sel.funded_resolve_risk(edge(s["balance"], s["cushion"]), least)
            if not (float(d.risk) == risk and risk > 0 and (risk <= s["cushion"] + 1e-9 or risk == least)
                    and d.rr is not None and float(d.rr) == rr and d.max_trades == Sel.FUNDED_RESOLVE_TRADES
                    and not d.abandon and d.source == "strategy" and d.regime.startswith("funded / ")
                    and d.regime.endswith(" / " + Sel.funded_resolve_leaf_name(risk, rr))):
                out.append("a funded state below the starting balance does not decide the bold leaf (its room's "
                           "band's lower edge, never more than the room but for the one-micro least, at the plan's R, "
                           "one trade)")
                break
    if not (seen["bold"] and seen["base"]):
        out.append("the states compared do not lie on both sides of the starting balance")
    for s in _plan_states():
        if s["phase"] != "funded" and dec(table.decide(s)) != dec(plan.decide(s)):
            out.append(f"a {s['phase']} state does not decide what the base decides")
            break
    if not Sel._plain(b) or pickle.loads(pickle.dumps(table)).as_dict() != b:
        out.append("the cell's table is not plain data that pickles")
    return out


def resolve_plan(plan: Any, spec: dict[str, Any], min_risk: float) -> tuple[Any, dict[str, Any]]:
    """(the table a `funded_resolve` cell runs on, what it replaced): the base's table rebuilt from
    `u_select.funded_resolve_policy_dict`'s plain data by `RiskPolicy.from_dict` -- which validates it: a tier-1
    breach raises `ConductViolation` and is a stop, never worked around -- refused unless `resolve_plan_problems`
    finds nothing. `min_risk`: one micro's dollars at the base's widest stop (`one_micro_dollars`). The record: the
    balance bands and the leaves replaced, the bold leaves by cushion band (`bands`: each band's lower edge and its
    leaf's dollars), the bands whose leaf is the one-micro least (`floored_bands`), and the table's tier-2 conduct
    flags (allowed, reported: a bold leaf above half the drawdown is an account-deciding position) -- the cell's,
    those of them the base's table does not carry, and the base's count. Built once for a base's table, an R and a
    least risk (`_RESOLVE_MEMO`)."""
    from propedge.campaign.risk_policy import RiskPolicy

    lowest = Sel.funded_resolve_lowest(spec)
    key = (id(plan), float(spec["rr"]), float(min_risk), lowest)
    hit = _RESOLVE_MEMO.get(key)
    if hit is not None and hit[0] is plan:
        return hit[1], hit[2]
    d, n = Sel.funded_resolve_policy_dict(plan.as_dict(), spec["rr"], min_risk, lowest)
    out = RiskPolicy.from_dict(d)
    out.validate()
    bad = resolve_plan_problems(plan, out, spec, min_risk)
    if bad:
        raise ValueError(f"REFUSED ({Sel.FUNDED_RESOLVE_DECISION}): the cell's table is not the base's with the bold "
                         "leaves below the starting balance -- " + "; ".join(bad[:4]))
    flags = [f.replace(f"policy {out.id!r}, ", "") for f in out.conduct_flags()]
    was = [f.replace(f"policy {plan.id!r}, ", "") for f in plan.conduct_flags()]
    info = {**{k: v for k, v in n.items() if k != "cushion_bands"},
            "bands": [{"from": float(c), "risk": float(r)} for c, r in n["cushion_bands"].items()],
            "table": out.id, "base_table": plan.id, "rr": float(spec["rr"]), "conduct_flags": flags,
            "conduct_flags_new": [f for f in flags if f not in was], "conduct_flags_base": len(was)}
    _RESOLVE_MEMO[key] = (plan, out, info)
    return out, info


def resolve_sizing(sizing: Any, blocks: list, info: dict[str, Any]) -> list[dict[str, Any]]:
    """The bold leaves' dollars as micros, from the SIZING RULE alone (no campaign, no outcome): for every risk per
    micro the cell's trades carry (their stops) and every cushion band, `sizing.size_trade` of the band's leaf under
    the funded cap of the ENTRY tier (a balance below the starting balance is below the ladder's first step), and
    whether the engine would take the trade (`TierSizedDraw._plain_size`'s stand-aside) -- {risk_per_micro,
    cushion_from, leaf_risk, cap_micros, micros, realised, at_cap, taken, floored}. `floored`: the leaf is the
    one-micro least, above its band's lower edge -- there a room under the leaf's dollars is risked beyond, and the
    loss limit sits inside the trade's stop."""
    from propedge.campaign.sizing import size_trade

    rpcs = sorted({float(x) for b in blocks if len(b) for x in np.asarray(b.risk_per_contract, float)})
    sa = sizing.stand_aside_for("funded")
    cap = sizing.cap_micros("funded", Sel.FUNDED_RESOLVE_START - 0.01)
    out = []
    for rpc in rpcs:
        for band in info["bands"]:
            s = size_trade(float(band["risk"]), rpc, cap)
            stood = sa is not None and (s.realised_risk + 1e-9 < sa[0] * s.intended_risk
                                        or s.risk_per_contract + 1e-9 < sa[1])
            out.append({"risk_per_micro": rpc, "cushion_from": float(band["from"]), "leaf_risk": float(band["risk"]),
                        "cap_micros": cap, "micros": int(s.contracts), "realised": float(s.realised_risk),
                        "at_cap": bool(s.at_cap), "taken": bool(s.contracts >= 1 and not stood),
                        "floored": bool(float(band["risk"]) > float(band["from"]))})
    return out


def _same_arg(x: Any, y: Any) -> bool:
    """Two engine arguments are one: the same object, the same printed value, or equal."""
    if x is y or repr(x) == repr(y):
        return True
    try:
        return bool(x == y)
    except Exception:  # noqa: BLE001 -- an argument that cannot be compared is not shown to be the same
        return False


def resolve_cell_problems(jobs: dict[str, dict], ref_jobs: dict[str, dict], plan: Any, spec: dict[str, Any]
                          ) -> tuple[list[str], dict[str, Any]]:
    """A `funded_resolve` cell's jobs (both arms) against D-659 (1) and its base's own jobs (`ref_jobs`: the same
    base, no override): (the problems, the cell's facts). The table in the replay's engine arguments is
    `resolve_plan`'s at the base's one-micro dollars, at each arm; **nothing else the replay is handed differs from
    the base's** -- the draws' arguments (the protocol's funded leg among them), the path's arguments but the table,
    the seed, the sessions and every day's block, column for column (so no edge or bound key moved: the fresh funded
    decision is the base's); every R the table asks for is carried by every day's block; below the starting balance
    the funded cap is one tier's; and every bold leaf buys at least one micro at every stop the trades carry, none
    standing aside (`resolve_sizing`). A problem names the check, never a value."""
    import zero_edge_decomposition as zd

    first = next(iter(jobs.values()))
    least = one_micro_dollars(first["blocks"])
    table, info = resolve_plan(plan, spec, least)
    want = table.as_dict()
    need = set(zd.policy_rrs(table))
    bad: list[str] = []
    sizing = None

    def same(x: Any, y: Any) -> bool:
        if x is None or y is None:
            return x is None and y is None
        return bool(np.array_equal(np.asarray(x, float), np.asarray(y, float), equal_nan=True))

    for arm, job in jobs.items():
        ref = ref_jobs.get(arm)
        if ref is None:
            bad.append(f"{arm}: the base has no such arm")
            continue
        a, r = job["args"], ref["args"]
        got = a["path"].get("risk_policy")
        if getattr(got, "id", None) != table.id or got.as_dict() != want:
            bad.append(f"{arm}: the replay's table is not the cell's")
        if getattr(r["path"].get("risk_policy"), "id", None) != plan.id:
            bad.append(f"{arm}: the base's replay is not on the base's table")
        diff = ({f"draws.{k}" for k in set(a["draws"]) | set(r["draws"])
                 if not _same_arg(a["draws"].get(k), r["draws"].get(k))}
                | {f"path.{k}" for k in set(a["path"]) | set(r["path"])
                   if k != "risk_policy" and not _same_arg(a["path"].get(k), r["path"].get(k))}
                | {k for k in set(a) | set(r) if k not in ("draws", "path") and not _same_arg(a.get(k), r.get(k))})
        if diff:
            bad.append(f"{arm}: the replay's arguments differ from the base's beyond the table ({len(diff)} of them)")
        if list(job["dates"]) != list(ref["dates"]) or len(job["blocks"]) != len(ref["blocks"]) or not all(
                same(x.pnl, y.pnl) and same(x.risked, y.risked) and same(x.risk_per_contract, y.risk_per_contract)
                and sorted(x.r_by_rr or {}) == sorted(y.r_by_rr or {})
                and all(same(x.r_by_rr[k], y.r_by_rr[k]) for k in (x.r_by_rr or {}))
                for x, y in zip(job["blocks"], ref["blocks"])):
            bad.append(f"{arm}: the sessions or a day's block are not the base's (an edge or bound key moved)")
        if any(len(b) and not need <= {float(k) for k in (b.r_by_rr or {})} for b in job["blocks"]):
            bad.append(f"{arm}: a day's block does not carry an R the cell's table asks for")
        if one_micro_dollars(job["blocks"]) != least:
            bad.append(f"{arm}: one micro's dollars at the base's stop differ between the arms")
        sizing = a["draws"]["sizing"]
    sized = resolve_sizing(sizing, first["blocks"], info) if sizing is not None else []
    if sizing is not None and len({sizing.cap_micros("funded", float(x)) for x in
                                   (Sel.FUNDED_RESOLVE_START - 0.01, min(info["balance_bands"]) - 500.0)}) != 1:
        bad.append("the funded cap is not one tier's below the starting balance")
    if sizing is not None and sizing.room_capped("funded"):
        bad.append("the funded leg is cut to the room: the bold leaf's dollars would not be the sizing rule's")
    if not sized or not all(x["taken"] for x in sized):
        bad.append("a bold leaf does not buy a micro at every stop, or a trade stands aside")
    return bad, {**info, "sizing": sized}


def resolve_lines(name: str, base: str, facts: dict[str, Any]) -> list[str]:
    """A resolve cell's facts as the lines printed before anything runs: inputs from the table and the sizing rule."""
    out = [f"fact: {name} on base {base} ({Sel.FUNDED_RESOLVE_DECISION} (1)): the table {facts['table']} -- "
           f"{facts['base_table']} with the {facts['replaced_leaves']} leaves ({facts['replaced_no_trade_leaves']} of "
           f"them no-trade states) of its {len(facts['balance_bands'])} funded balance bands below the starting "
           f"balance replaced by {facts['leaves']} bold leaves at {facts['rr']:g}R, {facts['max_trades']} trade a "
           f"session; one micro at the base's widest stop is ${facts['min_risk']:g}"
           + ("" if not facts.get("base_bands") else "; a room from "
              + ", ".join(f"${c:,.0f}" for c in facts["base_bands"]) + " (a band under one micro) left to the base's "
              "own leaves") + "; every other state the base's; "
           f"tier 1 none (the table validates); tier-2 conduct flags {len(facts['conduct_flags'])} against the base "
           f"table's {facts['conduct_flags_base']}, {len(facts['conduct_flags_new'])} of them new with the plan"]
    out += [f"    fact: tier-2 flag (allowed, reported{', new' if f in facts['conduct_flags_new'] else ''}): {f}"
            for f in facts["conduct_flags"]]
    for rpc in sorted({x["risk_per_micro"] for x in facts["sizing"]}):
        rows = [x for x in facts["sizing"] if x["risk_per_micro"] == rpc]
        out.append(f"    fact: the bold leaf on a ${rpc:g}-a-micro stop (the entry tier's cap, {rows[0]['cap_micros']} "
                   "micros): " + "; ".join(
            f"room from ${x['cushion_from']:,.0f}: ${x['leaf_risk']:,.0f} asked, {x['micros']} micros, "
            f"${x['realised']:,.0f}" + (" (at the cap)" if x["at_cap"] else "")
            + (" (the one-micro least: more than a room under it)" if x["floored"] else "")
            + ("" if x["taken"] else " -- NOT TAKEN") for x in rows))
    return out


def resolve_rows(cell: str, base: str, facts: dict[str, Any], overrides: dict[str, Any]) -> list[dict[str, Any]]:
    """A resolve cell's facts as section `cell` rows beside its scorecard (`RESOLVE_FACT_ROLE`; `measure` is
    `resolve.<key>`)."""
    vals = [("rr", "the bold leaf's R", "R", facts["rr"]),
            ("min_risk", "one micro's dollars at the base's widest stop (the least a bold leaf asks for)", Sel.DOLLARS,
             facts["min_risk"]),
            ("balance_bands_replaced", "the base table's funded balance bands below the starting balance", "bands",
             len(facts["balance_bands"])),
            ("leaves_replaced", "the base table's funded leaves the bold leaves replace", "leaves",
             facts["replaced_leaves"]),
            ("no_trade_leaves_replaced", "the no-trade leaves among them", "leaves",
             facts["replaced_no_trade_leaves"]),
            ("bold_leaves", "the bold leaves written (one a cushion band of each replaced balance band)", "leaves",
             facts["leaves"]),
            ("conduct_flags", "the table's tier-2 conduct flags (allowed, reported)", "flags",
             len(facts["conduct_flags"])),
            ("conduct_flags_base", "the base table's tier-2 conduct flags", "flags", facts["conduct_flags_base"]),
            ("conduct_flags_new", "the tier-2 flags the base's table does not carry", "flags",
             len(facts["conduct_flags_new"]))]
    vals += [(f"asked_room_from{x['from']:g}", f"the bold leaf's dollars with a room from ${x['from']:,.0f}",
              Sel.DOLLARS, x["risk"]) for x in facts["bands"]]
    vals += [(f"realised_rpc{x['risk_per_micro']:g}_room_from{x['cushion_from']:g}",
              f"the bold leaf's realised dollars on a ${x['risk_per_micro']:g}-a-micro stop with a room from "
              f"${x['cushion_from']:,.0f} ({x['micros']} micros under a cap of {x['cap_micros']})", Sel.DOLLARS,
              x["realised"]) for x in facts["sizing"]]
    return [{"section": "cell", "cell": cell, "base": base, "role": RESOLVE_FACT_ROLE, "arm": "", "block": "all",
             "measure": f"resolve.{k}", "what": what, "direction": "", "unit": unit, "measure_role": FACT_MEASURE_ROLE,
             "value": float(v), "n": 0, "counted": False, "overrides": json.dumps(overrides, sort_keys=True)}
            for k, what, unit, v in vals]


# ---- the under-water identity: nothing differs before a funded account stands below its starting balance

#: what the two recorded runs are compared on, day by day (`LockstepPath.account_days`, `.campaign_days`, D-146)
_UW_ACCOUNT_KEYS = ("day", "kind", "index", "state", "balance", "floor", "day_pnl", "eligible", "requested", "regime",
                    "policy_risk")
_UW_CAMPAIGN_KEYS = ("day", "fee_subscription", "fee_activation", "fee_reset", "payouts_in", "cash", "active_funded",
                     "breaches")


def recorded_replay(blocks: list, args: dict[str, Any]) -> Any:
    """`customer_slices.replay` of `blocks` with the engine's daily recorder on (D-146: one row an account a session,
    one a campaign day) -- the same call otherwise; a recorder reads the run, it decides nothing in it."""
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    sd = SharedDayDraws({0: list(blocks)}, seed=args["seed"], replay=True, **args["draws"])
    return simulate_lockstep_path(args["draws"]["protocol"], seed=args["seed"], horizon_days=len(blocks) + 1,
                                  record_days=True, **args["path"], **sd.lockstep_kwargs())


def first_under_water(lp: Any) -> int | None:
    """The first session at whose close a funded account that is live and not yet paid stands below its starting
    balance (any amount below: the table may read cents, and a balance it reads as the start is then counted early,
    never late) -- the first close after which D-659's bold leaf can decide anything. None: no such close."""
    days = [int(r["day"]) for r in lp.account_days if r["kind"] == "funded" and r["state"] == "funded"
            and float(r["balance"]) < Sel.FUNDED_RESOLVE_START]
    return min(days) if days else None


def _same_rows(a: list[dict], b: list[dict], keys: tuple[str, ...]) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        for k in keys:
            u, v = x.get(k), y.get(k)
            if u is None or v is None:
                if u is not v:
                    return False
            elif isinstance(u, (bool, str)) or isinstance(v, (bool, str)):
                if u != v:
                    return False
            elif abs(float(u) - float(v)) > 1e-9:
                return False
    return True


def under_water_compare(cell: Any, base: Any, bold_from: float = 0.0) -> dict[str, Any]:
    """One start's two recorded runs -- the cell's table and the base's, the same sessions -- against D-659's "the
    plan cannot differ before a funded account is under water". With `d` the base's `first_under_water` close (the
    last session where there is none): (i) the cell's is the same close; (ii) every account's day up to `d` is the
    same in both (its state, balance, loss limit, result, eligibility, request, the leaf that decided it and its
    dollars); (iii) the campaign's day up to `d` is the same (each fee, the payouts in, the cash, the funded accounts
    held, the breaches); (iv) every purchase, pass, failure and activation up to `d` is the same; (v) no bold leaf
    decides a session up to `d` in the cell, and none at all in the base; (vi) at session `d` + 1 every funded account
    the base shows live, unpaid and at least a cent under its start at the close of `d` -- with a room of at least
    `bold_from`, the lowest room the cell's table has a bold leaf for -- is decided by a bold leaf in the cell.
    {day, problems (the checks that fail, never a value), bold (a bold leaf decided a session), and the
    recorded cell run's passes, activations and month-end cash for tying it to the counted replay}."""
    import customer_journey as CJ

    d = first_under_water(base)
    last = len(base.path.cash_series) - 1
    upto = last if d is None else int(d)
    bad = []
    if first_under_water(cell) != d:
        bad.append("the first close a funded account is under water")

    def acct(lp: Any) -> list[dict]:
        return [r for r in lp.account_days if int(r["day"]) <= upto]

    def camp(lp: Any) -> list[dict]:
        return [r for r in lp.campaign_days if int(r["day"]) <= upto]

    def events(lp: Any) -> tuple:
        return ([(int(c.index), int(c.purchase_day)) for c in lp.combines if int(c.purchase_day) <= upto],
                sorted((int(c.index), int(c.resolved_on), bool(c.passed), bool(c.failed)) for c in lp.combines
                       if c.resolved_on is not None and int(c.resolved_on) <= upto),
                [(int(f.index), int(f.activation_day)) for f in lp.funded if int(f.activation_day) <= upto])

    if not _same_rows(acct(cell), acct(base), _UW_ACCOUNT_KEYS):
        bad.append("the accounts' days up to it")
    if not _same_rows(camp(cell), camp(base), _UW_CAMPAIGN_KEYS):
        bad.append("the campaign's cash, fees and payouts up to it")
    if events(cell) != events(base):
        bad.append("the purchases, passes, failures and activations up to it")
    bold = [int(r["day"]) for r in cell.account_days if r["kind"] == "funded" and _BOLD in str(r["regime"])]
    if any(x <= upto for x in bold):
        bad.append("a bold leaf decided a session before a funded account was under water")
    if any(_BOLD in str(r["regime"]) for r in base.account_days):
        bad.append("the base's replay decided a bold leaf")
    if d is not None:
        under = {int(r["index"]) for r in base.account_days if int(r["day"]) == d and r["kind"] == "funded"
                 and r["state"] == "funded" and round(float(r["balance"]), 2) < Sel.FUNDED_RESOLVE_START
                 and round(float(r["room"]), 2) >= float(bold_from)}
        nxt = {int(r["index"]): r for r in cell.account_days if int(r["day"]) == d + 1 and r["kind"] == "funded"}
        if any(i in nxt and _BOLD not in str(nxt[i]["regime"]) for i in under):
            bad.append("an account under water at that close is not decided by a bold leaf the next session")
    cash, init, passes, funded, _ = CJ.single_events(cell)
    rel = np.asarray(cash, float) - float(init)
    return {"day": None if d is None else int(d), "problems": bad, "bold": bool(bold),
            "pass_days": sorted(int(x) for x in passes), "funded_days": sorted(int(x) for x in funded),
            "net_month": [float(rel[U.MONTH * k]) for k in range(1, U.MONTHS + 1) if U.MONTH * k <= len(rel) - 1]}


def resolve_identity_task(task: tuple) -> list[dict[str, Any]]:
    """(cell, arm, blocks, dates, the cell's engine arguments, the base's, the lowest room with a bold leaf, starts)
    -> each start's `under_water_compare` on its long replay (the counted replays' own length), both runs with the
    daily recorder on. Plain data in and out: it runs in the guarded pool."""
    import warnings

    warnings.filterwarnings("ignore")
    _name, _arm, blocks, _dates, args, ref_args, bold_from, starts = task
    out = []
    for s in starts:
        L = min(U.HORIZON, len(blocks) - int(s))
        got = under_water_compare(recorded_replay(blocks[s:s + L], args), recorded_replay(blocks[s:s + L], ref_args),
                                  float(bold_from))
        out.append({"start_day": int(s), **got})
    return out


def record_upto_problems(r: dict[str, Any], t: dict[str, Any], day: int | None) -> list[str]:
    """Two counted records of one start (the cell's, its base's reference's) up to session `day`: the event days up
    to it, every month-end net and fee at or before it and the 30-session net where it is; whole records
    (`user_journey.record_problems`) when `day` is None."""
    if day is None:
        return U.record_problems(r, t)
    out = []
    if U.events_upto(r["pass_days"], r["funded_days"], r["pay_days"], day) != U.events_upto(
            t["pass_days"], t["funded_days"], t["pay_days"], day):
        out.append("the event days")

    def money(x: Any, y: Any) -> bool:
        if Sel._blank(x) or Sel._blank(y):
            return bool(Sel._blank(x) and Sel._blank(y))
        return abs(float(x) - float(y)) <= U.TOL

    for m in range(1, U.MONTHS + 1):
        if U.MONTH * m <= day:
            out += [k for k in ("net_month", "fees_month") if not money(r[k][m - 1], t[k][m - 1])]
    if U.EXTRA_NET_DAY <= day and not money(r["net_30"], t["net_30"]):
        out.append("net_30")
    return sorted(set(out))


def under_water_problems(rows: list[dict[str, Any]], outs: list[dict[str, Any]], ref: list[dict[str, Any]]
                         ) -> list[str]:
    """D-659's stronger identity over the sampled starts: each start's `under_water_compare` finds nothing; the
    recorded cell run is the counted one (its passes and activations are the start's record's, its month-end cash the
    record's nets); and the counted records of the cell and its base's reference agree up to the under-water close
    (`record_upto_problems`). A problem names the check and the count of starts, never a value."""
    mine = {int(x["rec"]["start_day"]): x["rec"] for x in outs}
    theirs = {int(x["rec"]["start_day"]): x["rec"] for x in ref}
    bad: dict[str, int] = {}

    def note(what: str) -> None:
        bad[what] = bad.get(what, 0) + 1

    for x in rows:
        s = int(x["start_day"])
        for p in x["problems"]:
            note(p)
        r, t = mine.get(s), theirs.get(s)
        if r is None or t is None:
            note("a sampled start has no counted record")
            continue
        nets = [v for v in r["net_month"] if not Sel._blank(v)]
        if ([int(d) for d in r["pass_days"]] != [int(d) for d in x["pass_days"]]
                or [int(d) for d in r["funded_days"]] != [int(d) for d in x["funded_days"]]
                or len(nets) != len(x["net_month"])
                or any(abs(float(u) - float(v)) > U.TOL for u, v in zip(nets, x["net_month"]))):
            note("the recorded replay is not the counted one")
        for k in record_upto_problems(r, t, x["day"]):
            note(f"the counted records up to the under-water close: {k}")
    return [f"{k}: {n} starts" for k, n in bad.items()]


# ------------------------------------------------------------------------------------------------ D-630's entry options


def entry_overrides(overrides: dict[str, Any]) -> dict[str, Any]:
    """A cell's entry options (`u_select.ENTRY_KINDS`) among its overrides, in their declared order."""
    return {k: overrides[k] for k in Sel.ENTRY_KINDS if k in (overrides or {})}


def entry_problems(overrides: dict[str, Any], outs: list[dict[str, Any]]) -> list[str]:
    """The override reached the replay's engine: every start's long replay carries each of the cell's entry options'
    own record (`user_journey._single_task`'s `entry`) at the declared value. A problem names the option and the count,
    never a reading."""
    out = []
    for k, v in entry_overrides(overrides).items():
        bad = [x["rec"]["start_day"] for x in outs
               if ((x.get("entry") or {}).get(k) or {}).get(ENTRY_RECORD_KEY[k]) is None
               or float(x["entry"][k][ENTRY_RECORD_KEY[k]]) != float(v)]
        if bad:
            out.append(f"{k}: {len(bad)} starts' long replays carry no record at the declared value (first: start "
                       f"{bad[0]})")
    return out


def entry_readings(kind: str, recs: list[dict[str, Any]]) -> list[tuple[str, str, str, float]]:
    """One entry option's own record over the starts' long replays (each min(`user_journey.HORIZON`, sessions left)
    sessions), as (key, what, unit, value) -- read beside a cell's scorecard, never in the selection. A day counts as
    refused when the option alone refused a purchase the campaign could otherwise make (`lockstep`'s
    `purchase_days_blocked`)."""
    n = len(recs)
    nan = float("nan")

    def share(key: str) -> float:
        return float(np.mean([int(r.get(key, -1)) >= 0 for r in recs])) if n else nan

    def mean(key: str) -> float:
        return float(np.mean([float(r.get(key, 0) or 0) for r in recs])) if n else nan

    first = "paused_on" if kind == "pause_after_funded" else "first_blocked_day"
    out = [("share_starts_refused", "the share of starts where the option alone ever refused a purchase", Sel.SHARE,
            share(first)),
           ("mean_purchase_days_blocked", "the days the option alone refused a purchase, a start's mean", Sel.SESSIONS,
            mean("purchase_days_blocked"))]
    if kind == "wallet_stop":
        out += [("share_starts_on_at_end", "the share of starts whose long replay ends with the cash out of pocket "
                 "above W (the stop on)", Sel.SHARE, mean("on_at_end")),
                ("share_starts_final", "the share of starts where the stop became final (above W with nothing live and "
                 "no payout on its way)", Sel.SHARE, share("final_on"))]
    elif kind == "pause_after_funded":
        out += [("mean_in_force_days", "the purchase steps at which F funded accounts were held with no payout "
                 "arrived, a start's mean", Sel.SESSIONS, mean("in_force_days")),
                ("mean_spells", "the separate spells of such steps, a start's mean", "spells", mean("spells")),
                ("share_starts_resumed_below_f", "the share of starts where purchases resumed because fewer than F "
                 "funded accounts were held, before any payout", Sel.SHARE,
                 float(np.mean([int(r.get("resumed_below_f", 0)) > 0 for r in recs])) if n else nan),
                ("share_starts_released", "the share of starts where the option had refused and the first payout then "
                 "arrived", Sel.SHARE, share("released_on"))]
    elif kind == "seat_ramp":
        out += [("share_starts_full", "the share of starts where the ramp reached the base's seats", Sel.SHARE,
                 share("full_on")),
                ("mean_seats_at_end", "the seats the ramp ended on, a start's mean", "seats", mean("seats_at_end"))]
    else:
        raise ValueError(f"{kind!r} is not an entry option ({Sel.ENTRY_KINDS})")
    return out


def entry_rows(cell: str, base: str, arm: str, overrides: dict[str, Any], outs: list[dict[str, Any]]
               ) -> list[dict[str, Any]]:
    """A cell's entry options' own records as section `cell` rows beside its scorecard (`ENTRY_ROLE`,
    `ENTRY_MEASURE_ROLE`; `measure` is `<option>.<reading>`): no row for a cell without one."""
    rows = []
    for k in entry_overrides(overrides):
        recs = [x["entry"][k] for x in outs if (x.get("entry") or {}).get(k)]
        for key, what, unit, value in entry_readings(k, recs):
            rows.append({"section": "cell", "cell": cell, "base": base, "role": ENTRY_ROLE, "arm": arm, "block": "all",
                         "measure": f"{k}.{key}", "what": what, "direction": "", "unit": unit,
                         "measure_role": ENTRY_MEASURE_ROLE, "value": value, "n": len(recs), "counted": False,
                         "overrides": json.dumps(overrides, sort_keys=True)})
    return rows


def gate_entry(df: pd.DataFrame, overrides: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """(the gate's columns for the cell's entry options at the bound's row, 0 % denial -- `gate.entry_columns`' names;
    the problems: a column the gate's rows do not carry, or an option's value there not the declared one). Empty for a
    cell without an entry option."""
    from propedge.campaign import gate

    want = entry_overrides(overrides)
    if not want:
        return {}, []
    names = list(gate.entry_columns([], **want))
    missing = [c for c in names if c not in df.columns]
    at = df[(df["shift"] == "lower_bound") & np.isclose(df["enforcement_p"].astype(float), 0.0)]
    if missing or len(at) != 1:
        return {}, [f"the gate's rows carry no {', '.join(missing[:4])}" if missing
                    else f"{len(at)} rows at the bound and 0 %"]
    bad = [f"{k}: the gate's rows carry {ENTRY_GATE_KEY[k]} at another value" for k, v in want.items()
           if not all(float(x) == float(v) for x in df[ENTRY_GATE_KEY[k]])]
    row = at.iloc[0]
    return {c: (row[c].item() if hasattr(row[c], "item") else row[c]) for c in names}, bad


def cell_jobs(camp: Any, plan: Any, budget: tuple[int, int] | None, overrides: dict[str, Any]) -> dict[str, dict]:
    """A cell's two arms as U1's replay jobs (`user_journey._single_jobs`): the campaign with the overrides applied;
    a `funded_plan` cell (D-653) or a `funded_resolve` cell (D-659) on its own table, built from `plan`
    (`cell_table`) -- the latter with one micro's dollars read from the campaign's own trades."""
    import customer_slices as cs
    import user_journey as UJ

    kw, b = apply_overrides(camp.kw, budget, overrides, plan=plan, blocks=camp.blocks)
    return UJ._single_jobs(cs.Campaign(camp.name, camp.blocks, camp.dates, kw), cell_table(kw, plan, overrides), b)


# ------------------------------------------------------------------------------------------------ base p14


def bases_of(fam: dict[str, Any]) -> tuple[str, ...]:
    """The bases a family's cells name, in `u_select.BASES`' order (then the window bases, then the joint bases):
    only these are built and replayed."""
    used = {Sel.base_of(c) for c in fam["cells"]}
    return tuple(b for b in Sel.EVERY_BASE if b in used)


def count_params(fam: dict[str, Any], cell: dict[str, Any], window: dict[str, Any] | None = None) -> dict[str, Any]:
    """What a counted cell records in the variant ledger (its identity there). A cell on the default base records
    exactly what it did before bases existed -- no `base` -- so it is counted as before; a cell on another base
    records its base (the same overrides on P-14's setup are another cell). `window`: a window base's facts
    (`window_facts`) -- its cell also records its screen cell, stop, window and the cap it takes (D-639 (2)). A cell
    on a joint base (D-643, D-644) also records its seats per firm, when the second firm opens, its deal and its label
    (`hypothetical_hedge` under a hedge deal: such a cell is recorded under `u_select.hypothetical_id`)."""
    b = Sel.base_of(cell)
    return {"study": f"program U's lever family {fam['family']} ({fam['decision']}; D-621)", "cell": cell["name"],
            "overrides": cell["overrides"], "arm": ARM, "horizon": U.HORIZON,
            **({} if b == Sel.DEFAULT_BASE else {"base": b}),
            **({} if not Sel.is_joint_base(b) else {
                "seats": list(Sel.joint_seats(b)), "second_firm": "lucid",
                "second_firm_opens": Sel.JOINT_BASES[b]["opens"] or "day 0", "deal": Sel.joint_deal(b),
                "label": Sel.base_row_label(b)}),
            **({} if window is None else {"window_cell": window["cell"], "stop_ticks": int(window["stop_ticks"]),
                                          "window": window["window"], "r_cap": window["cap"]})}


def p14_inputs(rd: Path) -> dict[str, Any]:
    """P-14's replay setup exactly as U1 builds its `p14` configuration -- `user_journey.build_d518`'s calls: D-518's
    `p14` row of `customer_journey.CONFIGS` handed to `customer_journey.Inputs` (P-13's campaign from the A3 rung
    cache, the no-closure table, P-13's gate inputs); the jobs come from `customer_journey.replay_jobs` (`p14_jobs`) --
    with its identities' problems:

    * `trade_problems` -- the trades by the registered test's two pins (`a3_brk30_cb20.registered`): the screen's
      rank-1 cell (`a3_brk30.identity_with_screen`: the screen file's sha256, the rung walk's cache inputs, every fact,
      edge and era row) and P-13's (`a3_brk30_cb20.p13_trade_problems`: each R's e, bounds, count, blocks and sd and
      the trade and day counts of `a3_brk30_gate.csv`, its sha256 pinned);
    * `setup_problems` -- the table is the no-closure policy D-509 fixed (`a3_brk30_cb20.noclose_plan`'s hashes), the
      budget, strict rule and campaign seed are the registered test's, the placement is off, and the campaign's
      sessions are the pinned trades' day set.

    `resolves`: every offered R resolves, as the registered test read it (`a3_brk30.resolution_rows`, D-212)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import customer_journey as CJ

    c = next(x for x in CJ.CONFIGS if x["config"] == P14)
    I = CJ.Inputs(Path(rd), [c])
    camp = I.single[c["kind"]]
    L, ci = I.p13_L, I.p13_ci
    t, days = B.cell_trades(L)
    trade_bad = B.identity_with_screen(Path(rd), t, days, L) + C.p13_trade_problems(Path(rd), t, days, L)
    setup_bad = []
    plan = I.plan(c["kind"], c["table"])
    try:
        pinned = C.noclose_plan(Path(rd))
        if plan.id != C.NOCLOSE_ID or plan.as_dict() != pinned.as_dict():
            setup_bad.append(f"the table is {plan.id}, not the no-closure policy {C.NOCLOSE_ID} D-509 fixed")
    except SystemExit as e:
        setup_bad.append(str(e))
    if c["table"] != "noclose" or tuple(c["budget"] or ()) != tuple(C.BUDGET) or int(c["seed"]) != int(C.SEED):
        setup_bad.append(f"D-518's {P14} row is not the no-closure table, the budget {tuple(C.BUDGET)} and the seed "
                         f"{C.SEED}")
    gap = camp.kw.get("one_at_a_time")
    if gap is None or float(gap) != float(C.STRICT_GAP) or float(B.STRICT_GAP) != float(C.STRICT_GAP):
        setup_bad.append(f"the strict rule is {gap!r}, not the registered test's {C.STRICT_GAP}")
    if bool(camp.kw.get("rtp", True)):
        setup_bad.append("the placement is not off")
    if (list(camp.dates) != [str(d) for d in days] or len(camp.blocks) != len(days) or len(ci["blocks"]) != len(days)
            or int(ci["trades"]) != len(t) or int(ci["days"]) != len(days)):
        setup_bad.append("the campaign's sessions or trades are not the pinned trades' day set")
    resolves = all(bool(r["resolves"]) for r in B.resolution_rows(t, B.rrs(t)))
    return {"I": I, "c": c, "camp": camp, "dates": list(camp.dates), "budget": c["budget"],
            "trade_problems": trade_bad, "setup_problems": setup_bad, "resolves": bool(resolves)}


def p14_jobs(X14: dict[str, Any], overrides: dict[str, Any]) -> dict[str, dict]:
    """A `p14`-based cell's two arms as U1's replay jobs: `user_journey.build_d518`'s loop over
    `customer_journey.replay_jobs` (its table, its seed, the arm's blocks and engine arguments), with the cell's
    overrides applied as plain data to what that builder reads -- the campaign's `gate.run_gate` arguments
    (`apply_overrides` on base `p14`) and D-518's row's budget. No override: the builder's own objects, untouched (the
    reference cell's jobs are U1's `p14` jobs). A `funded_plan` cell (D-653) or a `funded_resolve` cell (D-659): the
    builder's table on the copied inputs is the cell's own (`flat_plan` or `resolve_plan` of the no-closure table)."""
    import copy

    import customer_journey as CJ
    import customer_slices as cs

    I, c = X14["I"], X14["c"]
    camp = I.single[c["kind"]]
    table = I.plan(c["kind"], c["table"])
    kw, budget = apply_overrides(camp.kw, c["budget"], overrides, base=P14, plan=table, blocks=camp.blocks)
    if overrides:
        I = copy.copy(I)                        # a shallow copy: the built inputs are shared, never changed
        I.single = {**I.single, c["kind"]: cs.Campaign(camp.name, camp.blocks, camp.dates, kw)}
        c = {**c, "budget": budget}
        own = own_table_kind(overrides)
        if own is not None:                                 # D-653, D-659: the builder reads its table from the inputs
            if c["table"] != "noclose" or I.noclose is not table:
                raise SystemExit(f"REFUSED ({OWN_TABLE_DECISION[own]}): {c['config']}'s table is not the inputs' "
                                 "no-closure table; the plan cannot be handed to D-518's job builder.")
            I.noclose = cell_table(kw, table, overrides)    # on the copy only
            if I.plan(c["kind"], c["table"]) is not kw["risk_policy"]:
                raise SystemExit(f"REFUSED ({OWN_TABLE_DECISION[own]}): the plan's table did not reach D-518's job "
                                 "builder.")
    per = {}
    for kind, t in CJ.replay_jobs(I, c, 1):
        if kind != "single":
            raise SystemExit(f"REFUSED ({DECISION}): {c['config']} is not a single-firm replay.")
        _, arm, blk, dates, args, _ = t
        per[arm] = {"engine": "single", "blocks": blk, "dates": dates, "args": args, "sub": I.subscription(c)}
    return per


def gate_run_p14(X14: dict[str, Any], overrides: dict[str, Any], seed: int, n_paths: int, workers: int, label: str
                 ) -> tuple[pd.DataFrame, list[dict]]:
    """One `gate.run_gate` call on P-14's campaign in the registered test's form -- `a3_brk30_cb20._registered_run`'s
    `go("gate", ...)` as D-518 re-ran it at 0 % denial (`customer_journey.resampled_single`, whose paths equal the
    registered per-path file's): P-13's blocks, the era rule's 0.05 bounds and the day capacity
    (`a3_compliance.campaign_inputs`), the no-closure table, the 20-in-21 budget, the strict rule, the placement off,
    the registered run's path hook -- with the campaign seed a parameter and a cell's overrides applied to the gate's
    arguments (`apply_overrides` on base `p14`). (the gate's rows; every path's record, labelled `label`)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps

    from propedge.campaign import gate

    I, c = X14["I"], X14["c"]
    ci, L = I.p13_ci, I.p13_L
    fcfg = L["fcfg"]
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                              "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    ps._label(inner, label)
    kw = A.gate_kwargs(ci["blocks"], fcfg, float(L["tv"]), I.plan(c["kind"], c["table"]), ci["e_by"], ci["lb_by"],
                       hook, seed=int(seed), n_paths=int(n_paths),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=ci["cap"], levels=(0.0,),
                       rtp=False, one_at_a_time=B.STRICT_GAP, purchase_budget=c["budget"])
    kw, budget = apply_overrides(kw, tuple(c["budget"]), overrides, base=P14, plan=I.plan(c["kind"], c["table"]))
    if budget is None:
        kw.pop("purchase_budget", None)
    else:
        kw["purchase_budget"] = budget
    df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    return df, sink


def p14_registered_rows(rd: Path) -> dict[str, pd.Series]:
    """P-14's registered gate rows: `a3_brk30_cb20_gate.csv`'s section `gate` at 0 % denial, {shift: the row} (its
    manifest checked) -- the campaign at the registered seed 20261131, 500 paths."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / P14_GATE_FILE)
    g = d[(d["section"].astype(str) == P14_GATE_SECTION)
          & np.isclose(pd.to_numeric(d["enforcement_p"], errors="coerce"), 0.0)]
    out = {}
    for s in ("lower_bound", "point"):
        r = g[g["shift"].astype(str) == s]
        if len(r) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {P14_GATE_FILE} holds {len(r)} {P14_GATE_SECTION} rows at 0 % "
                             f"for {s}.")
        out[s] = r.iloc[0]
    return out


def p14_row_problems(df: pd.DataFrame, rows: dict[str, Any]) -> list[str]:
    """This script's gate rows against the registered ones (`P14_IDENT_COLS`, to 1e-9, as
    `rc150_payout_screen.growth_problems` reads P-16's); a problem names the reading and the size of the difference,
    never a value."""
    out = []
    for shift, col in P14_IDENT_COLS:
        g = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        if len(g) != 1:
            out.append(f"{shift} {col}: {len(g)} rows at 0 %")
            continue
        mine, want = float(g[col].iloc[0]), float(rows[shift][col])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{shift} {col}: differs from {P14_GATE_FILE}'s by {abs(mine - want):.3g}")
    return out


def p14_path_problems(rd: Path, sink: list[dict], label: str, n: int) -> list[str]:
    """The gate call's `n` paths (point and bound, 0 %) against the first `n` of the registered per-path record's
    `gate` run (`zero_edge_decomposition.path_problems`, the registered test's own comparison of P-13's paths): every
    `PATH_COLS` column to 1e-6; a problem names the column and the count, never a value."""
    import re

    import zero_edge_decomposition as zd

    from propedge.reporting.results import read_result

    ref = read_result(Path(rd) / P14_PATHS_FILE)
    bad = zd.path_problems(sink, ref, [(label, s, P14_GATE_RUN, s) for s in ("point", "lower_bound")], int(n))
    return [re.sub(r": path \d+ .*? against .*? \((\d+ of \d+ differ)\)$", r": \1", p) for p in bad]


def date_problems(dates: dict[str, list[str]], u1_records: dict[str, list[dict]] | None = None, *,
                  whole: bool = True) -> list[str]:
    """The paired readings are on common start DATES, so the windows must be the same dates: every base's session
    dates equal the first base's, in order; and, with U1's records ({configuration: its start records}), each row to
    beat's start dates in U1's file equal them too (`whole`) -- so no start is dropped from a pairing by its date."""
    out = []
    names = list(dates)
    if not names:
        return ["no base"]
    first = [str(d) for d in dates[names[0]]]
    if len(set(first)) != len(first):
        out.append(f"{names[0]}: its session dates repeat")
    for b in names[1:]:
        mine = [str(d) for d in dates[b]]
        if mine != first:
            diff = len(set(mine) ^ set(first))
            out.append(f"{b}: {len(mine)} session dates against {names[0]}'s {len(first)} ({diff} not shared"
                       + ("" if diff else "; the order differs") + ")")
    if whole:
        for cfg, recs in (u1_records or {}).items():
            theirs = [str(r["start_date"]) for r in sorted(recs, key=lambda r: int(r["start_day"]))]
            if theirs != first:
                out.append(f"{U1_FILE}'s {cfg}: {len(theirs)} start dates against {names[0]}'s {len(first)} "
                           f"({len(set(theirs) ^ set(first))} not shared)")
    return out


def rules_problems(cell: dict[str, Any], ledger: Any = None) -> list[str]:
    """Line (3)(iii)'s "every firm rule it uses is verified" for a cell on either base's setup (P-16 and P-14
    themselves lean on no unverified rule, D-621 (2)): every rule the cell names (`rules`) is in the ledger and
    verified; seats above the
    verified cap on active funded accounts, a payout path other than the Standard one and a payout timing other than
    the default each need the rule that allows them named -- an override whose rule is not named is not verified.
    D-630's entry options (`u_select.ENTRY_KINDS`) lean on no firm rule (D-630 (4): each only withholds a purchase the
    trader is free not to make), so they need none named and add no problem. D-653's `funded_plan` leans on none
    either on the Standard path (a size and an R inside the verified allowance, the base's own rules); on the
    Consistency path its cell names each of D-645's four rules (`CONSISTENCY_RULES`; D-653 (3)) -- one named rule does
    not cover the others. D-659's `funded_resolve` leans on none beyond the base's (D-659 (3): a size inside the
    verified allowance and an R the base already trades; the closure at request it stands in for is NOT used)."""
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING
    from propedge.contract.rules import load_rules

    L = load_rules() if ledger is None else ledger
    ov = cell.get("overrides") or {}
    named = tuple(cell.get("rules") or ())
    out = []
    for n in named:
        try:
            if not L.is_verified(n):
                out.append(f"rule {n!r} is not verified")
        except KeyError:
            out.append(f"rule {n!r} is not in the ledger")
    if any(k in ov for k in Sel.SEAT_KEYS):
        try:
            cap = int(L.value("max_active_funded_accounts"))
        except Exception as e:  # noqa: BLE001 -- an unverified or unknown cap is a problem, not a crash
            cap = None
            out.append(f"the cap on active funded accounts cannot be read ({type(e).__name__})")
        if cap is not None and max(int(ov[k]) for k in Sel.SEAT_KEYS if k in ov) > cap and not named:
            out.append(f"seats above the verified cap of {cap} need the rule that allows them named in `rules`")
    path = (ov.get("protocol") or {}).get("payout_path")
    if path not in (None, "standard") and not named:
        out.append("a payout path other than the Standard one needs the rule that lets it be chosen named in `rules`")
    if funded_plan_of(ov) is not None and path == "consistency":        # D-653 (3): the four, each by name
        missing = [r for r in CONSISTENCY_RULES if r not in named]
        if missing:
            out.append(f"a funded plan on the Consistency path leans on {', '.join(missing)} "
                       f"({Sel.FUNDED_PLAN_DECISION} (3)): each is named in `rules`")
    if ov.get("payout_timing") not in (None, DEFAULT_PAYOUT_TIMING) and not named:
        out.append("a payout timing other than the default needs the rule it rests on named in `rules`")
    return out


# ------------------------------------------------------------------------------------------------ D-639: window bases

#: which of `rc_width_screen.build`'s two trade sets each stop's SCREEN FILE recorded: at 100 ticks
#: `rc_reentry_screen.csv`'s rows are D-525's build (`raw`: the 07:30 CT report-day cut only); at 150 ticks
#: `rc_width_screen.csv`'s rows carry D-533's news-safe cut (`trades`). The family always RUNS `trades`
WINDOW_SCREEN_KIND = {100: "raw", 150: "trades"}
#: each window base's content hashes (`rc_dev_test.trades_hash`), pinned from `--trades-hash` on a clean checkout (the
#: screens' own builders; a content hash, no campaign run): `screen` -- the cell as its screen's result file records it
#: (`WINDOW_SCREEN_KIND`), the side of the screen-row identity and of the registered gate call -- and `trades` -- the
#: cell the family runs, with D-533's news-safe cut at both stops. The two are one hash wherever the cut removes no
#: entry. `s150_london`'s is U1's pin (`user_journey.LONDON_TRADES_SHA256`, checked at run time)
WINDOW_PINS: dict[str, dict[str, str]] = {
    "s100_london": {"screen": "b58b38d081d161861980cdb8bec08f334144dbadb052f1ae59b9465632249714",
                    "trades": "34d249c495175ce24d9c08a8148b95a5f514b4e9c2dd385fb0aae912b3f02a22"},
    "s100_us": {"screen": "a02939f9977eeb8b8dabf21303fcd80a07be92d66358e96dfebc130669c7a73c",
                "trades": "a02939f9977eeb8b8dabf21303fcd80a07be92d66358e96dfebc130669c7a73c"},
    "s100_asia": {"screen": "94c2a0ea491fa8ae47fa5e941d19ac774b5f660497a396de603b7d0e564e46fb",
                  "trades": "94c2a0ea491fa8ae47fa5e941d19ac774b5f660497a396de603b7d0e564e46fb"},
    "s150_london": {"screen": "6a421c7e1bc9fd69e4880381544e14d1777bf84bdef7f9fd5004f4f024ea8557",
                    "trades": "6a421c7e1bc9fd69e4880381544e14d1777bf84bdef7f9fd5004f4f024ea8557"},
    "s150_us": {"screen": "1897ee52706e4dd6df9d66e122f4c07116ce5a8502e345deac59935edde46658",
                "trades": "1897ee52706e4dd6df9d66e122f4c07116ce5a8502e345deac59935edde46658"},
    "s150_asia": {"screen": "72552fbd621b592fabeb901e86b72b26a32732d2863acd5668f14dc4310903fd",
                  "trades": "72552fbd621b592fabeb901e86b72b26a32732d2863acd5668f14dc4310903fd"},
}
#: `--check --check-base <window base>[,<window base>...]`: each named base as one cell of the NULL family, never
#: counted outside the check's temporary folder
WINDOW_CHECK_CELL = "check_window"
#: the role of a window base's fact rows: inputs read from resolution and supply columns, never a reading
FACT_ROLE = ("window base: resolution and supply inputs and the cap taken (D-639 (2); fixed before anything runs; "
             "never a reading, never in the selection)")
FACT_MEASURE_ROLE = "input"
#: the per-R columns of a cell's trades (`resolved_coin.cell_trades`): `<prefix>_<R>`
_PER_R = ("r", "g", "c", "mae", "exit_t", "o")
if set(WINDOW_PINS) != set(Sel.WINDOW_BASES) or {int(w["stop_ticks"]) for w in Sel.WINDOW_BASES.values()} != set(
        WINDOW_SCREEN_KIND):
    raise RuntimeError("the window bases' pins or stops are not u_select.WINDOW_BASES'")


def label_of(base: str) -> str:
    """A base in words: `u_select.BASE_LABEL`'s for `p16` and `p14`, a window base's stop and window, a joint base's
    seats and opening."""
    if Sel.is_joint_base(base):
        return Sel.joint_label(base)
    return LABEL[base] if base in LABEL else Sel.window_label(base)


def window_cell_name(base: str) -> str:
    """A window base's cell in the screens' naming (`resolved_coin.reentry_cell_name`)."""
    from propedge.research import resolved_coin as rc

    w = Sel.WINDOW_BASES[base]
    return rc.reentry_cell_name(int(w["stop_ticks"]), str(w["window"]))


def window_spec(base: str, which: str = "trades"):
    """A window base's `rc_dev_test.Spec`: its stop's registered spec (P-15's at 100 ticks, P-16's at 150 -- the
    screen file and its sha256, the seed the replay's arguments carry; a replay draws nothing) with the window's cell
    and its pin (`WINDOW_PINS[base][which]`), as U1 built the London cell's (`user_journey.build_p16`)."""
    import rc150_dev_test as R
    import rc_dev_test as D

    by_stop = {int(D.P15.stop_ticks): D.P15, int(R.SPEC.stop_ticks): R.SPEC}
    return dataclasses.replace(by_stop[int(Sel.WINDOW_BASES[base]["stop_ticks"])], cell=window_cell_name(base),
                               trades_sha256=WINDOW_PINS[base][which], windows_beside=())


def window_cell(W: dict[str, Any], stop: int, window: str, coins: dict | None = None) -> dict[str, Any]:
    """One window's cell from a stop's walk (`rc_stop_walkforward.walk_stop`), as `rc_width_screen.build` builds it
    (`rc_reentry_screen.build` with the stop a parameter, then D-533's cut): the cutoff's offered marks at every R the
    table offers (`resolved_coin.mark_resolution`, kind columns only), the window's marks, `resolved_coin.cell_trades`
    -- `raw`, D-525's build -- and `trades`, with no report-day entry before 07:35 CT
    (`resolved_coin.drop_release_minute`). `coins`: the coin table (None: the registered coin's, the walk's own). The
    constructions are tied at run time: at the registered coin each must carry its pinned content hash
    (`WINDOW_PINS`, pinned from the screens' own builders)."""
    import zero_edge_decomposition as zd

    from propedge.research import resolved_coin as rc

    stop = int(stop)
    w = W["walks"]
    cache = W.setdefault("_offered_marks", {})
    if stop not in cache:                       # the cutoff reads no coin: one reading serves every coin sequence
        cols = ["date", "slot"] + rc.mark_resolution_columns((stop,), W["offered_rr"])
        cache[stop] = rc.offered_marks(rc.mark_resolution(w[cols], (stop,), W["offered_rr"]), stop)
    wm = rc.window_marks(cache[stop], window)
    raw = (rc.cell_trades(w, W["kinds"], wm, stop, W["coins"] if coins is None else coins, W["fees"],
                          rr_grid=W["rr_grid"], fresh_rr=W["crr"], tick_value=W["tv"], entry_ticks=W["slip"],
                          cut=W["cut"]) if wm else pd.DataFrame())
    raw = zd.pad(raw, W["keys"]) if len(raw) else None
    nr = rc.drop_release_minute(raw, W["clear"]) if raw is not None else None
    nr = nr if (nr is not None and len(nr)) else None
    return {"stop_ticks": stop, "window": window, "marks": wm, "raw": raw, "trades": nr,
            "removed_release": 0 if raw is None else int(len(raw) - (0 if nr is None else len(nr)))}


def passes_by_r(t: pd.DataFrame, rr_grid) -> tuple[dict[str, float], dict[float, bool]]:
    """(each offered R's unresolved share overall and in its worst year -- `atlas_a3.resolution`'s columns --, {R:
    whether it passes D-212's line}) from the cell's RESOLUTION columns only: the trades are cut to their year and
    each R's exit-kind column before anything is read, so no outcome can reach the cap. The line is
    `atlas_a3.resolution`'s own, applied to one R at a time -- no second rule is written here; an R no trade carries
    is not offered and has no entry."""
    import atlas_a3 as A

    grid = [float(R) for R in rr_grid if f"o_{float(R):g}" in t.columns]
    view = t[["year"] + [f"o_{R:g}" for R in grid]]
    res, ok = A.resolution(view, grid)
    passes = {}
    for R in grid:
        one, ok_r = A.resolution(view, [R])
        if one:
            passes[R] = bool(ok_r)
    if bool(ok) != all(passes.values()):
        raise RuntimeError("the R-by-R reading of atlas_a3.resolution disagrees with its reading of every R")
    return res, passes


def collect_leaf_r(plan: Any) -> float:
    """D-639 (2)'s "the collect leaf's" R: the smallest R any trading leaf of the table asks for
    (`rc_width_screen.policy_leaves`) -- on the no-closure table the Combine's $250 leaf at 0.25R, its one leaf below
    1R. (No leaf of that table carries `source == "collect"`, D-379's sense of the word.)"""
    import rc_width_screen as WS

    rs = [float(rr) for _, _, _, rr in WS.policy_leaves(plan) if rr is not None]
    if not rs:
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): the table's trading leaves set no R.")
    return min(rs)


def capped_trades(t: pd.DataFrame, cap: float | None, fresh_rr: float) -> pd.DataFrame:
    """The cell's trades as the capped cell offers them (D-639 (2)): every per-R column (`r_`, `g_`, `c_`, `mae_`,
    `exit_t_`, `o_`) of an R above `cap` dropped -- every row and every other column as built -- so the campaign's R
    keys, its bounds, its blocks and the resolution check read the capped list and nothing the engine draws can come
    from an R above the cap. No cap: the trades themselves. REFUSED where the cap is below the fresh Combine's R (the
    trades' single `exit_t` and `flat` columns are read at it) or below 1R (the blocks' base column)."""
    import re

    if cap is None:
        return t
    floor = max(1.0, float(fresh_rr))
    if float(cap) + 1e-12 < floor:
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): a cap of {float(cap):g}R is below {floor:g}R, the R the "
                         "trades' single exit column and the blocks' base column are built at; this builder cannot "
                         "express the cell.")
    pat = re.compile(r"^(?:" + "|".join(_PER_R) + r")_(\d+(?:\.\d+)?)$")
    drop = [c for c in t.columns if (m := pat.match(str(c))) and float(m.group(1)) > float(cap) + 1e-12]
    return t.drop(columns=drop)


def plan_cap_problems(plan: Any, capped: Any, cap: float) -> list[str]:
    """Every way `capped` is not `plan` with each leaf's R above `cap` set to `cap` and nothing else changed: the two
    trees equal once every leaf's R and name are set aside; leaf for leaf the phases, dollar risk, trade limit,
    abandon and source equal and the R the smaller of the leaf's and the cap; plain data that pickles."""
    import pickle

    from propedge.campaign.risk_policy import PHASES

    def strip(n: dict) -> dict:
        if n.get("type") == "fixed":
            return {k: v for k, v in n.items() if k not in ("rr", "name")}
        if n.get("type") == "tiers":
            return {**n, "tiers": [{**x, "policy": strip(x["policy"])} for x in n["tiers"]]}
        return {**n, **{k: strip(n[k]) for k in ("combine", "funded", "paid") if n.get(k)}}

    out = []
    a, b = plan.as_dict(), capped.as_dict()
    if strip(a["root"]) != strip(b["root"]) or int(a.get("version", 1)) != int(b.get("version", 1)):
        out.append("the capped table differs from the table in more than its leaves' R and names")
    if b["id"] != Sel.capped_policy_id(a["id"], cap):
        out.append("the capped table's id is not u_select.capped_policy_id's")
    la, lb = list(plan.root.leaves(frozenset(PHASES))), list(capped.root.leaves(frozenset(PHASES)))
    if len(la) != len(lb):
        return out + [f"{len(lb)} leaves against the table's {len(la)}"]
    for (x, px), (y, py) in zip(la, lb):
        want = None if x.rr is None else min(float(x.rr), float(cap))
        if (px != py or float(x.risk) != float(y.risk) or x.max_trades != y.max_trades or x.abandon != y.abandon
                or x.source != y.source or (None if y.rr is None else float(y.rr)) != want):
            out.append(f"leaf {x.name!r}: its R is not the smaller of its own and the cap, or another field changed")
            break
    if not Sel._plain(b) or pickle.loads(pickle.dumps(capped)).as_dict() != b:
        out.append("the capped table is not plain data that pickles")
    return out


def capped_plan(plan: Any, cap: float | None) -> tuple[Any, dict[str, int]]:
    """(the table a window cell runs on, {leaves, leaves_capped}): the table itself without a cap; with one, the table
    rebuilt from `u_select.capped_policy_dict`'s plain data (`RiskPolicy.from_dict`: every leaf asking for more than
    the cap takes the cap, its dollar risk unchanged, the table not re-solved), refused unless `plan_cap_problems`
    finds nothing."""
    from propedge.campaign.risk_policy import PHASES, RiskPolicy

    if cap is None:
        return plan, {"leaves": sum(1 for _ in plan.root.leaves(frozenset(PHASES))), "leaves_capped": 0}
    d, n = Sel.capped_policy_dict(plan.as_dict(), float(cap))
    out = RiskPolicy.from_dict(d)
    bad = plan_cap_problems(plan, out, float(cap))
    if bad:
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): the capped table is not the table with its leaves' R "
                         "capped -- " + "; ".join(bad[:4]))
    return out, n


def capped_inputs(I: dict[str, Any], cap: float | None) -> tuple[dict[str, Any], dict[str, int]]:
    """P-14's inputs as a capped cell reads them (a copy; `I` untouched), and the leaf counts: the table capped
    (`capped_plan`) and FV3-C's config with its two fresh R -- which only the engine call's pooled `e` and `lb` and the
    protocol's two legs are read at (`atlas_a3.gate_kwargs`, `portfolio_stage.protocol_of`) -- at the capped table's
    own fresh decisions (`a3_brk30.fresh_decisions`), as the config's are the table's own before the cap (refused
    otherwise). No cap: `I` itself."""
    import copy

    import a3_brk30 as B

    plan, n = capped_plan(I["plan"], cap)
    if cap is None:
        return I, n
    L = I["L"]
    fresh = L["fcfg"]["state_policy"]["fresh"]
    was, now = B.fresh_decisions(I["plan"]), B.fresh_decisions(plan)
    if any(was[ph]["rr"] is None or float(was[ph]["rr"]) != float(fresh[f"{ph}_rr"]) for ph in ("combine", "funded")):
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): the config's fresh R are not the table's own fresh "
                         "decisions; the capped cell's fresh R cannot be read from its table.")
    fcfg = copy.deepcopy(L["fcfg"])
    for ph in ("combine", "funded"):
        fcfg["state_policy"]["fresh"][f"{ph}_rr"] = float(now[ph]["rr"])
    return {**I, "plan": plan, "L": {**L, "fcfg": fcfg}}, n


def window_facts(base: str, c: dict[str, Any], days: list[str], rr_grid, plan: Any, fcfg: dict) -> dict[str, Any]:
    """A window base's FACTS (D-639 (2)), every one from the cell's supply counts and resolution columns -- the marks
    the cutoff admits, the offered trades and their count a session, the busiest day and the day capacity, the
    report-day entries D-533's cut removed, the sessions with no offered trade, each offered R's unresolved share
    overall and in its worst year (`passes_by_r`) -- and what follows from them alone: the cap (`u_select.r_cap`
    against the collect leaf's R), the offered R the cell runs with, the leaves that take the cap, and whether the
    cell is runnable (`u_select.supply_problem`, `r_cap`'s `runnable`). No outcome, no campaign."""
    import a3_brk30 as B

    from propedge.research import resolved_coin as rc

    t, wm = c["trades"], list(c["marks"])
    out: dict[str, Any] = {"base": base, "cell": window_cell_name(base), "stop_ticks": int(c["stop_ticks"]),
                           "window": str(c["window"]), "marks": len(wm), "first_mark": rc.ct(wm[0]) if wm else "",
                           "last_mark": rc.ct(wm[-1]) if wm else "", "candidates": 0 if t is None else int(len(t)),
                           "days": int(len(days)), "removed_release": int(c["removed_release"])}
    out["candidates_per_day"] = float(out["candidates"] / len(days))
    supply = Sel.supply_problem(out["marks"], out["candidates"], len(days))
    if t is None:
        return {**out, "busiest_day": 0, "capacity": 0, "sessions_without_candidate": int(len(days)), "resolution": {},
                "passes": {}, "cap": None, "capped": False, "offered": [], "failing": [], "failing_below_cap": [],
                "collect_r": collect_leaf_r(plan), "leaves": 0, "leaves_capped": 0, "runnable": False,
                "reason": supply or Sel.NOT_RUNNABLE_SUPPLY}
    res, passes = passes_by_r(t, rr_grid)
    cap = Sel.r_cap(passes, collect_leaf_r(plan))
    _, n = (capped_plan(plan, cap["cap"]) if cap["runnable"] else (None, {"leaves": 0, "leaves_capped": 0}))
    return {**out, "busiest_day": int(B.busiest(t)), "capacity": int(B.capacity(t, fcfg)),
            "sessions_without_candidate": int(len(days) - t["date"].astype(str).nunique()),
            "resolution": {k: float(v) for k, v in res.items()}, "passes": {f"{R:g}": bool(v) for R, v in passes.items()},
            "cap": cap["cap"], "capped": bool(cap["capped"]), "offered": [float(R) for R in cap["offered"]],
            "failing": [float(R) for R in cap["failing"]],
            "failing_below_cap": [float(R) for R in cap["failing_below_cap"]], "collect_r": float(cap["collect_r"]),
            "leaves": int(n["leaves"]), "leaves_capped": int(n["leaves_capped"]),
            "runnable": bool(cap["runnable"] and not supply), "reason": supply or cap["reason"]}


def facts_lines(facts: dict[str, dict[str, Any]]) -> list[str]:
    """The window bases' facts as the lines `--check` and a run print before anything runs: inputs, labelled so."""
    out = [f"FACTS ({Sel.WINDOW_DECISION} (2)) -- each window base's supply and resolution INPUTS and the cap it takes, "
           "read from its marks, its counts and its exit-kind columns only; fixed before anything runs; not readings:"]
    for b, f in facts.items():
        cap = "none (every offered R passes)" if f["cap"] is None and not f["failing"] else (
            "none passes" if f["cap"] is None else f"{f['cap']:g}R")
        out.append(f"  fact: {b} ({f['cell']}): marks {f['marks']}"
                   + (f" ({f['first_mark']}-{f['last_mark']} CT)" if f["marks"] else "")
                   + f"; offered trades {f['candidates']} on {f['days']} sessions, {f['candidates_per_day']:.2f} a "
                   f"session; busiest day {f['busiest_day']}; day capacity {f['capacity']}; report-day entries removed "
                   f"by D-533's cut {f['removed_release']}; sessions with no offered trade "
                   f"{f['sessions_without_candidate']}; cap {cap}; "
                   + ("RUNNABLE" if f["runnable"] else f"NOT RUNNABLE ({f['reason']})"))
        rs = sorted((float(k) for k in f["passes"]))
        if rs:
            out.append("    unresolved, overall:    " + " ".join(
                f"{R:g}R {f['resolution'][f'unresolved_{R:g}']:.4f}" for R in rs))
            out.append("    unresolved, worst year: " + " ".join(
                f"{R:g}R {f['resolution'][f'unresolved_worst_year_{R:g}']:.4f}" for R in rs))
        if f["failing"]:
            out.append("    fails D-212 (above 5 % overall or in the worst year): "
                       + ", ".join(f"{R:g}R" for R in f["failing"])
                       + (f"; offered R capped at {f['cap']:g}R ({', '.join(f'{R:g}' for R in f['offered'])}); "
                          f"{f['leaves_capped']} of the table's {f['leaves']} leaves take the cap, dollar risk unchanged"
                          if f["cap"] is not None and f["runnable"] else "")
                       + (f"; BELOW THE CAP AND FAILING: {', '.join(f'{R:g}R' for R in f['failing_below_cap'])}"
                          if f["failing_below_cap"] else ""))
    return out


def fact_rows(cell: str, base: str, f: dict[str, Any]) -> list[dict[str, Any]]:
    """A window base's facts as section `cell` rows beside the scorecards (`FACT_ROLE`; `measure` is `fact.<key>`)."""
    nan = float("nan")
    vals = [("marks", "the marks the cutoff admits in the window", "marks", f["marks"]),
            ("candidates", "the offered trades", "trades", f["candidates"]),
            ("candidates_per_day", "the offered trades a session", "trades", f["candidates_per_day"]),
            ("busiest_day", "the busiest day's offered trades", "trades", f["busiest_day"]),
            ("capacity", "the day capacity", "trades", f["capacity"]),
            ("removed_release", "report-day entries before 07:35 CT removed (D-533)", "trades", f["removed_release"]),
            ("sessions_without_candidate", "sessions with no offered trade", Sel.SESSIONS,
             f["sessions_without_candidate"]),
            ("r_cap", "the cap on the offered R (blank: none)", "R", nan if f["cap"] is None else f["cap"]),
            ("leaves_capped", "the table's leaves that take the cap", "leaves", f["leaves_capped"]),
            ("runnable", "runnable (1) or not (0), D-639 (2)", "flag", int(bool(f["runnable"])))]
    vals += [(k, "an offered R's unresolved share (atlas_a3.resolution)", Sel.SHARE, v)
             for k, v in sorted(f["resolution"].items())]
    return [{"section": "cell", "cell": cell, "base": base, "role": FACT_ROLE, "arm": "", "block": "all",
             "measure": f"fact.{k}", "what": what, "direction": "", "unit": unit, "measure_role": FACT_MEASURE_ROLE,
             "value": float(v), "n": int(f["days"]), "counted": False, "overrides": "{}"}
            for k, what, unit, v in vals]


def window_inputs(rd: Path, base: str, I: dict[str, Any], W: dict[str, Any]) -> dict[str, Any]:
    """One window base, built and checked (D-639 (1), (2)): its cell from its stop's walk (`window_cell`), its
    identities' rows (`idents`) -- the cell as its screen's file records it (`rc_dev_test.trade_problems`: the file's
    sha256, the row's count, busiest day, capacity, long share, candidates a day and every R's unresolved share, the
    pinned `screen` content hash); the trades the family runs by their pinned `trades` hash; the coin swap at the
    registered coin rebuilding them; the capped list being what the campaign carries --, its FACTS (`window_facts`)
    and, where it is runnable, its campaign as U1 builds an RC cell's (`user_journey._rc_campaign`: its own trades,
    its own 0.05 bounds by the era rule, its own day capacity, P-14's protocol) on the capped list and table
    (`capped_trades`, `capped_inputs`). `t`: the trades the campaign carries (capped where a cap is taken)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc_dev_test as D
    import user_journey as UJ
    import zero_edge_decomposition as zd

    w = Sel.WINDOW_BASES[base]
    stop, window, cell = int(w["stop_ticks"]), str(w["window"]), window_cell_name(base)
    fcfg = I["L"]["fcfg"]
    days = list(W["days"])
    c = window_cell(W, stop, window)
    spec = window_spec(base)
    idents, t = [], c["trades"]
    screen = c[WINDOW_SCREEN_KIND[stop]]
    sspec = window_spec(base, "screen")
    bad = (["the cutoff admits no mark in the window"] if screen is None else
           D.trade_problems(Path(rd), {"cells": {cell: {"trades": screen}}, "days": days, "rr_grid": W["rr_grid"]},
                            fcfg, spec=sspec))
    idents.append(UJ._ident(base, "", f"the cell as its screen built it is results/{sspec.screen_file}'s {cell} (the "
                            "file's sha256, the row's count, busiest day, capacity, long share, candidates a day and "
                            "every R's unresolved share) and its content hash is the pinned "
                            f"{WINDOW_PINS[base]['screen'] or '(none yet)'}", bad))
    bad = []
    if t is None or D.trades_hash(t) != WINDOW_PINS[base]["trades"]:
        bad.append("the trades' content hash is not the pinned one")
    if base in Sel.WINDOW_EQUALS_U1 and WINDOW_PINS[base]["trades"] != UJ.LONDON_TRADES_SHA256:
        bad.append("the pin is not U1's London cell's (user_journey.LONDON_TRADES_SHA256)")
    idents.append(UJ._ident(base, "", "the trades the family runs (the cell with D-533's news-safe cut: no report-day "
                            f"entry before 07:35 CT; {c['removed_release']} entries removed) carry the pinned content "
                            f"hash {WINDOW_PINS[base]['trades'] or '(none yet)'}", bad))
    again = window_cell(W, stop, window, coins=coin_table({"I": I}, Sel.REGISTERED_COIN))["trades"]
    idents.append(UJ._ident(base, "", "the coin guard's construction (the same walk, the coin table re-dealt) at the "
                            f"registered coin {Sel.REGISTERED_COIN} rebuilds the cell's trades",
                            [] if (again is not None and t is not None and D.trades_hash(again) == D.trades_hash(t))
                            else ["the re-dealt cell at the registered coin is not the cell"]))
    facts = window_facts(base, c, days, W["rr_grid"], I["plan"], fcfg)
    out = {"base": base, "cell": cell, "stop": stop, "window": window, "spec": spec, "days": days, "dates": days,
           "facts": facts, "idents": idents, "runnable": bool(facts["runnable"]), "budget": tuple(C.BUDGET),
           "cap": facts["cap"], "crr": float(W["crr"])}
    if not out["runnable"]:
        return out
    Ic, _ = capped_inputs(I, facts["cap"])
    tc = capped_trades(t, facts["cap"], W["crr"])
    camp = UJ._rc_campaign(Ic, {"cells": {cell: {"trades": tc}}, "days": days}, cell, spec)
    keys = [float(R) for R in B.rrs(tc)]
    _, resolves = A.resolution(tc, keys)
    bad = []
    if facts["cap"] is not None and (not keys or max(keys) > float(facts["cap"]) + 1e-12):
        bad.append("the campaign's R keys reach above the cap")
    want = [float(R) for R in W["keys"] if facts["cap"] is None or float(R) <= float(facts["cap"]) + 1e-12]
    if sorted(keys) != sorted(want) or not set(float(R) for R in facts["offered"]) <= set(keys):
        bad.append("the campaign's R keys are not the offered list")
    if any(len(blk) and sorted(float(k) for k in blk.r_by_rr) != sorted(keys) for blk in camp.blocks):
        bad.append("a day's block carries another R list")
    if not set(float(R) for R in zd.policy_rrs(Ic["plan"])) <= set(keys):
        bad.append("a leaf of the table asks for an R the campaign does not carry")
    if sorted(float(k) for k in camp.kw["e_by_rr"]) != sorted(keys) or getattr(camp.kw["risk_policy"], "id", None) != Ic[
            "plan"].id:
        bad.append("the bounds or the table of the campaign are not the capped list's")
    jobs = UJ._single_jobs(camp, Ic["plan"], out["budget"])
    if any(getattr(jobs[arm]["args"]["path"]["risk_policy"], "id", None) != Ic["plan"].id for arm in jobs):
        bad.append("the replay's table is not the cell's")
    idents.append(UJ._ident(base, "", "the offered R the cell runs with ("
                            + ("every R of the grid: no cap" if facts["cap"] is None else
                               f"capped at {facts['cap']:g}R; {facts['leaves_capped']} of the table's "
                               f"{facts['leaves']} leaves take the cap, dollar risk unchanged, the table not re-solved")
                            + ") are the R the campaign's blocks and 0.05 bounds carry, no leaf of its table asks "
                            "for another, and the table reaches the replay's engine arguments", bad))
    idents.append(UJ._ident(base, "", "development start days only and the campaign's sessions are the walk's day set",
                            [] if list(camp.dates) == [str(d) for d in days] else ["the sessions differ"]))
    return {**out, "I": Ic, "t": tc, "camp": camp, "plan": Ic["plan"], "resolves": bool(resolves)}


def window_screen_cell(X: dict[str, Any], I: dict[str, Any], W: dict[str, Any]) -> dict[str, Any]:
    """The side of a window base's registered gate call: the cell as its screen ran it (`WINDOW_SCREEN_KIND`), on the
    table as it is (no cap) -- `gate_run`'s inputs. Rebuilt from the walk when needed, not kept (memory)."""
    c = window_cell(W, X["stop"], X["window"])
    return {"I": I, "t": c[WINDOW_SCREEN_KIND[int(X["stop"])]], "days": list(X["days"])}


def window_coin_campaign(X: dict[str, Any], W: dict[str, Any], seed: int):
    """A window base's campaign under the coin sequence `seed`: its window's trades re-dealt on the same walk
    (`window_cell`: the same marks -- the cutoff reads no coin), the cell's own cap on the offered R
    (`capped_trades`; the cap is the registered coin's cell's, fixed before anything ran), its own bounds and day
    capacity under that sequence (`user_journey._rc_campaign`, as the guard reads P-16's)."""
    import user_journey as UJ

    t = window_cell(W, X["stop"], X["window"], coins=coin_table(X, seed))["trades"]
    if t is None:
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): coin sequence {seed} leaves {X['cell']} no trade.")
    return UJ._rc_campaign(X["I"], {"cells": {X["cell"]: {"trades": capped_trades(t, X["cap"], X["crr"])}},
                                    "days": X["days"]}, X["cell"], X["spec"])


def window_row_problems(rd: Path, base: str, reading: dict[str, float]) -> list[str]:
    """A window base's registered gate call (the screen's seed, 500 paths, no cap) against its row in its screen's
    file: the growth on the required bankroll at the bound and at the point and the required bankroll, to 1e-9; a
    problem names the reading and the size of the difference, never a value."""
    import a3_brk30 as B

    sp = window_spec(base, "screen")
    s = B._exact(Path(rd) / sp.screen_file)
    row = s[(s["section"].astype(str) == "cell") & (s["cell"].astype(str) == sp.cell)]
    if len(row) != 1:
        return [f"{sp.screen_file} holds {len(row)} cell rows for {sp.cell}"]
    row = row.iloc[0]
    out = []
    for col, key in (("growth_on_required", "growth_at_bound"), ("growth_on_required_point", "growth_at_point"),
                     ("required_p90", "required_p90")):
        want = float(pd.to_numeric(row[col], errors="coerce"))
        if not np.isclose(float(reading[key]), want, rtol=0, atol=1e-9):
            out.append(f"{col}: differs from {sp.screen_file}'s by {abs(float(reading[key]) - want):.3g}")
    return out


def gate_policy_problems(df: pd.DataFrame, policy_id: str) -> list[str]:
    """The gate's rows carry the table's id on every row: the cell's (capped) table reached the gate."""
    if "risk_policy" not in df.columns:
        return ["the gate's rows carry no risk_policy"]
    other = sorted({str(x) for x in df["risk_policy"]} - {str(policy_id)})
    return [f"the gate's rows carry another table ({len(other)} other ids)"] if other else []


def plan_gate_problems(df: pd.DataFrame, overrides: dict[str, Any] | None, plan: Any, min_risk: float | None = None
                       ) -> list[str] | None:
    """D-653: a `funded_plan` cell's gate rows carry its own table's id on every row (`gate_policy_problems` against
    `u_select.funded_plan_policy_id`). D-659: a `funded_resolve` cell's likewise, against
    `u_select.funded_resolve_policy_id` at the base's one-micro dollars (`min_risk`: `one_micro_dollars` of the base's
    trades -- the id names them, so a table built on other dollars is another id). None for a cell on its base's
    table."""
    spec = funded_plan_of(overrides)
    if spec is not None:
        return gate_policy_problems(df, Sel.funded_plan_policy_id(plan.id, spec["risk"], Sel.funded_plan_paid(spec)))
    spec = funded_resolve_of(overrides)
    if spec is None:
        return None
    if min_risk is None:
        return ["the resolve table's id needs the base's one-micro dollars"]
    return gate_policy_problems(df, Sel.funded_resolve_policy_id(plan.id, spec["rr"], min_risk,
                                                                 Sel.funded_resolve_lowest(spec)))


def window_trades_hash() -> int:
    """`--trades-hash`: every window base's content hashes from the screens' OWN builders -- at 100 ticks
    `rc_reentry_screen.build` (the `screen` side) and `rc_width_screen.build` at that stop (its `raw` must be the same
    trades; its `trades` carry D-533's cut), at 150 ticks `rc_width_screen.build` (`rc150_dev_test.build_cells`) --
    beside their pins. A content hash of trades: no campaign, no reading; nothing written."""
    import rc_dev_test as D
    import rc_reentry_screen as RS
    import rc_screen as S
    import rc_width_screen as WS
    import user_journey as UJ

    I = S.inputs()
    for stop in sorted(WINDOW_SCREEN_KIND):
        bases = [b for b, w in Sel.WINDOW_BASES.items() if int(w["stop_ticks"]) == stop]
        own: dict[str, str] = {}
        if WINDOW_SCREEN_KIND[stop] == "raw":
            b0 = RS.build(I)
            own = {b: D.trades_hash(b0["cells"][window_cell_name(b)]["trades"]) for b in bases}
            del b0
            gc.collect()
        bw = WS.build(I, (stop,))
        for b in bases:
            c = bw["cells"][window_cell_name(b)]
            got = {k: ("no trade" if c[k] is None else D.trades_hash(c[k])) for k in ("raw", "trades")}
            screen = own.get(b, got[WINDOW_SCREEN_KIND[stop]])
            note = "" if b not in own else (" (rc_reentry_screen.build's; rc_width_screen.build's raw is "
                                            + ("the same" if own[b] == got["raw"] else "ANOTHER: " + got["raw"]) + ")")
            print(f"{b} screen: content hash {screen} (pinned: {WINDOW_PINS[b]['screen'] or 'none yet'}){note}")
            print(f"{b} trades: content hash {got['trades']} (pinned: {WINDOW_PINS[b]['trades'] or 'none yet'}); "
                  f"{c['removed_release']} report-day entries removed by D-533's cut"
                  + (f"; U1's London pin is {UJ.LONDON_TRADES_SHA256}" if b in Sel.WINDOW_EQUALS_U1 else ""),
                  flush=True)
        del bw
        gc.collect()
    print("nothing written (--trades-hash).")
    return 0


def family_of(name: str | None, check: bool) -> dict[str, Any]:
    """The family to run: a registered one by name; the NULL family for `--check` without a name."""
    if name is None or name == NULL:
        if not check:
            raise SystemExit(f"REFUSED ({DECISION}): name a registered family (--family); the NULL family is --check's. "
                             f"Registered: {sorted(REGISTRY) or 'none'}.")
        return NULL_FAMILY
    if name not in REGISTRY:
        raise SystemExit(f"REFUSED ({DECISION}): {name!r} is not a registered family ({sorted(REGISTRY) or 'none'}); a "
                         "family is declared in its own decision row first.")
    fam = REGISTRY[name]
    bad = Sel.family_problems(fam) + ([] if fam.get("family") == name else ["its registry key is not its name"])
    if bad:
        raise SystemExit(f"REFUSED ({DECISION}): the family {name!r} is not well formed -- " + "; ".join(bad[:8]))
    return fam


# ------------------------------------------------------------------------------------------------ U1's file


def u1_table(rd: Path) -> pd.DataFrame | None:
    """U1's result as text, its manifest checked (`user_journey._text`); None when it is not on file."""
    import user_journey as UJ

    if not (Path(rd) / U1_FILE).is_file():
        return None
    return UJ._text(Path(rd), U1_FILE)


def u1_starts(df: pd.DataFrame, config: str, arm: str) -> pd.DataFrame:
    return df[(df["section"] == "start") & (df["config"] == config) & (df["arm"] == arm)]


def u1_start_problems(mine: list[dict[str, Any]], ref: pd.DataFrame, what: str, *, whole: bool) -> list[str]:
    """Our start rows (`user_journey.start_rows` on this run's records) against the file's, start for start on every
    column of a start (`NAME_COLS` aside); `whole`: the two must also hold the same starts."""
    import customer_journey as CJ

    by = {int(float(d)): i for i, d in enumerate(ref["start_day"])}
    missing = [r["start_day"] for r in mine if int(r["start_day"]) not in by]
    if missing:
        return [f"{what}: {len(missing)} starts not in the file (first: {missing[0]})"]
    out = []
    if whole and len(by) != len(mine):
        out.append(f"{what}: {len(mine)} starts here against {len(by)} in the file")
    cols = [c for c in (mine[0] if mine else {}) if c not in NAME_COLS]
    absent = [c for c in cols if c not in ref.columns]
    if absent:
        return out + [f"{what}: the file has no column {absent[:4]}"]
    for c in cols:
        bad = [r["start_day"] for r in mine if not CJ._same(r.get(c), ref[c].iloc[by[int(r["start_day"])]])]
        if bad:
            out.append(f"{what} {c}: {len(bad)} starts differ (first: start {bad[0]})")
    return out


def u1_side(df: pd.DataFrame) -> dict[str, Any]:
    """U1's file as D-621 (2) reads it: each row to beat's start records (the `verdict` arm), its scorecard on every
    start, the rows to beat and R*; and the problems -- a start whose exact run the file names and does not carry, a
    scorecard reading that does not recompute to the file's own row, R* differing between the two readings of P."""
    import customer_journey as CJ

    records, cards, p_u1, problems = {}, {}, {}, []
    for c in Sel.ROWS_TO_BEAT:
        rows = u1_starts(df, c, ARM)
        if not len(rows):
            problems.append(f"{c}: no {ARM} start row in {U1_FILE}")
            continue
        recs, missing = Sel.records_from_start_rows(rows.to_dict("records"))
        if missing:
            problems.append(f"{c}: {len(missing)} starts were read from an exact-length run the file does not carry "
                            f"(first: start {missing[0][0]} at {missing[0][1]} sessions)")
        problems += [f"{c}: {p}" for p in Sel.window_problems(recs)]
        mine = Sel.u1_reading(recs)
        g = df[df["section"].isin(["metric", "month"]) & (df["config"] == c) & (df["arm"] == ARM)]
        theirs = {str(k): (v, n) for k, v, n in zip(g["key"], g["value"], g["n"])}
        for k, (v, n) in mine.items():
            if k not in theirs:
                problems.append(f"{c} {k}: not in {U1_FILE}")
            elif not (CJ._same(v, theirs[k][0]) and CJ._same(n, theirs[k][1])):
                problems.append(f"{c} {k}: recomputed from the start rows, it is not the file's row")
        records[c], cards[c], p_u1[c] = recs, Sel.scorecard(recs), Sel.p_from_u1(mine)
    if problems:
        return {"records": records, "cards": cards, "problems": problems, "r_star": None, "by_measure": {}}
    rtb = Sel.row_to_beat(cards)
    other = Sel.row_to_beat({c: {**cards[c], Sel.PRIMARY_KEY: {"value": p_u1[c], "n": 0}} for c in cards})["r_star"]
    if rtb["r_star"] is None:
        problems.append("no row to beat holds a P")
    elif other != rtb["r_star"]:
        problems.append(f"R* is {rtb['r_star']} with P on the starts with {Sel.P_HORIZON} sessions and {other} with "
                        "the mean of the file's three shares: the row to beat is not fixed mechanically")
    return {"records": records, "cards": cards, "problems": problems, "r_star": rtb["r_star"],
            "by_measure": rtb["by_measure"], "p_u1": p_u1}


def p06_growth(rd: Path) -> tuple[float, list[str]]:
    """The scoreboard's row to beat (D-365, D-382): P-06's growth on the required bankroll at the bound, from
    `results/scoreboard.csv` (its manifest checked)."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / SCOREBOARD)
    g = d[d["run"].astype(str) == Sel.GATE_ROW_TO_BEAT]
    if len(g) != 1:
        return float("nan"), [f"{SCOREBOARD} holds {len(g)} {Sel.GATE_ROW_TO_BEAT} rows"]
    v = float(pd.to_numeric(g["growth_bound"], errors="coerce").iloc[0])
    return v, ([] if math.isfinite(v) else [f"{SCOREBOARD}'s {Sel.GATE_ROW_TO_BEAT} row holds no growth at the bound"])


# ------------------------------------------------------------------------------------------------ the replays


def run_starts(job: dict[str, Any], name: str, arm: str, starts: list[int], workers: int) -> dict[str, Any]:
    """One cell and arm on the given starts: U1's own per-start task (`user_journey._single_task` -- the long replay,
    the exact-length runs, the record and its ties to the engine's totals) in chunks across the guarded pool
    (`customer_journey._pool_run`), in start order. Every task is plain data. A joint base's job (D-643: `engine`
    `joint`) runs through the joint engine's task instead (`u_firms.run_starts`)."""
    import customer_journey as CJ
    import user_journey as UJ

    if job.get("engine") == "joint":
        import u_firms as UF

        return UF.run_starts(job, name, arm, starts, workers)
    t0 = time.time()
    chunks = [starts[j:j + UJ.CHUNK_STARTS] for j in range(0, len(starts), UJ.CHUNK_STARTS)]
    tasks = [("single", (name, arm, job["blocks"], job["dates"], job["args"], c)) for c in chunks]
    res = CJ._pool_run(tasks, UJ._dispatch, workers, f"{name} {arm}") if tasks else []
    return {"starts": [x for chunk in res for x in chunk], "seconds": time.time() - t0}


def inputs(rd: Path) -> dict[str, Any]:
    """P-16's cell by `rc150_routing`'s construction (`rc_stop_walkforward.walk_stop` and `cell`: one walk serves the
    cell and the coin guard), its identity (`rc_dev_test.trade_problems`: the screen's row and the registered content
    hash), its campaign as U1 builds it (`user_journey._rc_campaign`) and the coin swap's identity at the registered
    coin."""
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc150_dev_test as R
    import rc150_routing as RT
    import rc_dev_test as D
    import rc_screen as S
    import rc_stop_walkforward as WF
    import user_journey as UJ

    I = S.inputs()
    W = WF.walk_stop(I, R.STOP)
    days = list(W["days"])
    t = WF.cell(W, R.STOP, days)["trades"]
    if t is None:
        raise SystemExit(f"REFUSED ({DECISION}): the walk admits no trade for {R.CELL}.")
    b = {"cells": {R.CELL: {"trades": t}}, "days": days, "rr_grid": W["rr_grid"]}
    bad = D.trade_problems(Path(rd), b, I["L"]["fcfg"], spec=R.SPEC)
    swap = [] if D.trades_hash(RT.coin_cell(W, I, Sel.REGISTERED_COIN, days)) == R.TRADES_SHA256 else [
        "rc150_routing.coin_cell at the registered coin does not rebuild P-16's trades"]
    _, resolves = A.resolution(t, W["rr_grid"])
    camp = None if bad else UJ._rc_campaign(I, b, R.SPEC.cell, R.SPEC)
    return {"I": I, "W": W, "days": days, "t": t, "b": b, "camp": camp, "plan": I["plan"], "budget": tuple(C.BUDGET),
            "trade_problems": bad, "swap_problems": swap, "resolves": bool(resolves)}


def p15_walk(X: dict[str, Any]) -> dict[str, Any]:
    """P-15's walk (the 25-point rung) for the coin guard, by `rc_stop_walkforward.walk_stop`."""
    import rc_dev_test as D
    import rc_stop_walkforward as WF

    return WF.walk_stop(X["I"], D.P15.stop_ticks)


def p15_trades(W: dict[str, Any], coins: dict | None = None) -> pd.DataFrame | None:
    """P-15's cell (`rc_s100_all`) from its walk, as `rc_reentry_screen.build` builds it -- the cutoff's offered marks,
    the all-day window, `resolved_coin.cell_trades`, no news-safe cut -- with the coin table a parameter (None: the
    registered coin's). Its content hash at the registered coin must be P-15's registered one (`p15_swap_problems`)."""
    import rc_dev_test as D
    import zero_edge_decomposition as zd

    from propedge.research import resolved_coin as rc

    stop = int(D.P15.stop_ticks)
    w = W["walks"]
    cols = ["date", "slot"] + rc.mark_resolution_columns((stop,), W["offered_rr"])
    table = rc.mark_resolution(w[cols], (stop,), W["offered_rr"])          # kind columns only
    wm = rc.window_marks(rc.offered_marks(table, stop), "all")
    if not wm:
        return None
    t = rc.cell_trades(w, W["kinds"], wm, stop, W["coins"] if coins is None else coins, W["fees"],
                       rr_grid=W["rr_grid"], fresh_rr=W["crr"], tick_value=W["tv"], entry_ticks=W["slip"],
                       cut=W["cut"])
    return zd.pad(t, W["keys"]) if len(t) else None


def p15_swap_problems(W15: dict[str, Any]) -> list[str]:
    import rc_dev_test as D

    t = p15_trades(W15)
    if t is None or D.trades_hash(t) != D.P15.trades_sha256:
        return ["the P-15 coin swap at the registered coin does not rebuild P-15's registered trades"]
    return []


def coin_table(X: dict[str, Any], seed: int) -> dict:
    """The coin sequence `seed` over the development days and every mark (`rc150_routing.coin_cell`'s table)."""
    from propedge.research import resolved_coin as rc

    return rc.coin_table(X["I"]["L"]["days"]["date"].astype(str).tolist(), rc.marks(), seed=int(seed))


def coin_campaign(X: dict[str, Any], design: str, seed: int, W15: dict[str, Any] | None = None):
    """A coin design's campaign under the coin sequence `seed`: its trades re-dealt on the same walk
    (`rc150_routing.coin_cell` for P-16; `p15_trades` for P-15), its own bounds and day capacity
    (`user_journey._rc_campaign`, as `rc150_routing`'s guard 2 read each coin)."""
    import rc150_dev_test as R
    import rc150_routing as RT
    import rc_dev_test as D
    import user_journey as UJ

    if design == P16:
        t, spec = RT.coin_cell(X["W"], X["I"], int(seed), X["days"]), R.SPEC
    elif design == P15:
        if W15 is None:
            raise ValueError("P-15's walk is needed for its coin swap")
        t, spec = p15_trades(W15, coin_table(X, seed)), D.P15
    else:
        raise ValueError(f"{design!r} is not a coin design ({Sel.COIN_DESIGNS})")
    return UJ._rc_campaign(X["I"], {"cells": {spec.cell: {"trades": t}}, "days": X["days"]}, spec.cell, spec)


def _p(outs: list[dict[str, Any]]) -> tuple[float, int]:
    return Sel.p_of(Sel.months_ahead([x["rec"] for x in outs]).values())


def coin_dates(cell: list[dict], reference: list[dict]) -> list[str]:
    """The coin guard's start dates: every 21st of the judged block's common start dates (the cell's and R*'s, at P's
    horizon), from the first."""
    a = {str(r["start_date"]) for r in Sel.block(cell, Sel.LATE, Sel.P_HORIZON)}
    b = {str(r["start_date"]) for r in Sel.block(reference, Sel.LATE, Sel.P_HORIZON)}
    return sorted(a & b)[::Sel.COIN_EVERY]


def coin_guard(X: dict[str, Any], cell: dict[str, Any], r_star: str, reference: list[dict], dates: list[str],
               seeds: tuple[int, ...], workers: int, cached, W15: dict[str, Any] | None, *,
               camp_of: Any = None, job_of: Any = None, refused: Any = ()) -> list[dict[str, Any]]:
    """Line (3)(iv)'s replays: under each coin sequence the cell (its overrides on P-16's setup, on that sequence's
    trades) and R* on the start dates given; one row a sequence -- the two P's and the starts read. R* = P-14 is not a
    coin design: its P is the same under every sequence, read once from its records on those dates. A cell on base
    `p14` is not a coin design either: the line is not applicable to it and this is never called for one (refused).
    `camp_of` (D-639, a window base): the cell's own campaign under a sequence (`window_coin_campaign`: its window
    re-dealt, its cap) in place of P-16's -- `X` is then the window base's inputs, and R* must not be a coin design
    (its campaign is not this base's; refused). `job_of` (D-643, a joint base): the cell's own verdict-arm JOB under
    a sequence (`u_firms.coin_jobs`: the cell and its opposite side re-dealt, the joint engine's setups, the
    sequencing option) -- its starts run through the joint engine's task; R* must not be a coin design either.
    `refused` (D-644 (4)): the cells labelled `hypothetical_hedge` -- the coin line is a guard, so a cell on a
    hypothetical base, or one named there (as the cell or as R*), is REFUSED."""
    import customer_journey as CJ
    import user_journey as UJ

    Sel.refuse_labelled([cell["name"], r_star], [*refused, *([cell["name"]] if Sel.hypothetical(Sel.base_of(cell))
                                                             else [])], "a guard (the coin line)")
    if not Sel.coin_design(Sel.base_of(cell)):
        raise ValueError(f"the coin guard is a coin design's only: {cell['name']} is on base {Sel.base_of(cell)}")
    if camp_of is not None and r_star in Sel.COIN_DESIGNS:
        raise SystemExit(f"REFUSED ({Sel.WINDOW_DECISION}): R* is the coin design {r_star}; a window base's coin guard "
                         "is built for an R* that is not one (P-14, D-626).")
    if job_of is not None and r_star in Sel.COIN_DESIGNS:
        raise SystemExit(f"REFUSED ({Sel.JOINT_DECISION}): R* is the coin design {r_star}; a joint base's coin guard "
                         "is built for an R* that is not one (P-14, D-626).")
    want = set(dates)
    fixed = None
    if r_star not in Sel.COIN_DESIGNS:
        fixed = Sel.p_of(Sel.months_ahead([r for r in reference if str(r["start_date"]) in want]).values())
    rows = []
    for s in seeds:
        def make(s=s) -> dict[str, Any]:
            t0 = time.time()
            if job_of is not None:              # D-643: a joint base -- the cell's own job under the sequence
                import u_firms as UF

                job = job_of(s)
                starts = [i for i, d in enumerate(job["dates"]) if str(d) in want]
                tasks = UF.tasks_of(job, f"cell coin {s}", ARM, starts)
                owner = ["cell"] * len(tasks)
                jobs = {"cell": job}
                res = CJ._pool_run(tasks, UF.dispatch, workers, f"coin {s}")
            else:
                camp = coin_campaign(X, P16, s) if camp_of is None else camp_of(s)
                jobs = {"cell": cell_jobs(camp, X["plan"], X["budget"], cell["overrides"])[ARM]}
                if r_star == P16:
                    jobs["ref"] = UJ._single_jobs(camp, X["plan"], X["budget"])[ARM]
                elif r_star == P15:
                    jobs["ref"] = UJ._single_jobs(coin_campaign(X, P15, s, W15), X["plan"], X["budget"])[ARM]
                tasks, owner = [], []
                for side, job in jobs.items():
                    starts = [i for i, d in enumerate(job["dates"]) if str(d) in want]
                    for j in range(0, len(starts), UJ.CHUNK_STARTS):
                        tasks.append(("single", (f"{side} coin {s}", ARM, job["blocks"], job["dates"], job["args"],
                                                 starts[j:j + UJ.CHUNK_STARTS])))
                        owner.append(side)
                res = CJ._pool_run(tasks, UJ._dispatch, workers, f"coin {s}")
            outs = {side: [x for o, chunk in zip(owner, res) if o == side for x in chunk] for side in jobs}
            bad = int(sum(x["pay_bad"] + x["cash_bad"] + x["fee_bad"] for v in outs.values() for x in v))
            pc, nc = _p(outs["cell"])
            pr, nr = _p(outs["ref"]) if "ref" in outs else fixed
            return {"coin_seed": int(s), "value": pc, "n": nc, "reference_value": pr, "n_reference": nr,
                    "ties_failing": bad, "seconds": time.time() - t0}

        r = cached(f"coin|{s}|{cell['name']}|{r_star}|{len(dates)}", make)
        print(f"timing: coin {s}: {float(r['seconds']):.1f} s", flush=True)
        rows.append(r)
    return rows


def gate_run(X: dict[str, Any], overrides: dict[str, Any], seed: int, n_paths: int, workers: int, label: str
             ) -> pd.DataFrame:
    """One `gate.run_gate` call on P-16's cell in `rc_screen.Runner.run`'s form (its hook, the era rule's bounds, the
    day capacity, the no-closure plan, the 20-in-21 budget, the strict rule, the placement off, 0 % denial) with the
    campaign seed a parameter and a cell's overrides applied to the gate's arguments (`apply_overrides`)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf

    from propedge.campaign import gate

    I, t, days = X["I"], X["t"], X["days"]
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    Rn = S.Runner(I, workers)
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    ps._label(Rn.inner, label)
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, Rn.hook, seed=int(seed), n_paths=int(n_paths),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=B.capacity(t, fcfg),
                       levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP, purchase_budget=S.BUDGET)
    kw, budget = apply_overrides(kw, tuple(S.BUDGET), overrides, plan=I["plan"])
    if budget is None:
        kw.pop("purchase_budget", None)
    else:
        kw["purchase_budget"] = budget
    df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    return df


def gate_reading(df: pd.DataFrame) -> dict[str, float]:
    at = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
          for s in ("point", "lower_bound")}
    return {"growth_at_bound": float(at["lower_bound"]["pf_growth_on_base_p50"]),
            "growth_at_point": float(at["point"]["pf_growth_on_base_p50"]),
            "required_p90": float(at["lower_bound"]["pf_required_p90"])}


# ------------------------------------------------------------------------------------------------ the tables


def _card_rows(cell: str, role: str, arm: str, card: dict[str, dict], *, overrides: Any = None, counted: bool = False,
               best: dict[str, dict] | None = None, base: str = "") -> list[dict[str, Any]]:
    """A scorecard as section `cell` rows. `base`: the base of a cell replayed here (`u_select.BASES`); blank for a row
    to beat read from U1's file."""
    out = []
    for m in Sel.MEASURES:
        r = {"section": "cell", "cell": cell, "base": base, "role": role, "arm": arm, "block": "all", "measure": m.key,
             "what": m.what, "direction": m.direction, "unit": m.unit, "measure_role": m.role,
             "value": card[m.key]["value"], "n": card[m.key]["n"], "counted": bool(counted),
             "overrides": "" if overrides is None else json.dumps(overrides, sort_keys=True)}
        if best is not None:
            r["row_to_beat"] = bool(best[m.key]["config"] == cell)
        out.append(r)
    return out


def _pair_rows(section: str, d: dict[str, Any], r_star: str, k: int, best: dict[str, dict]) -> list[dict[str, Any]]:
    """Lines (3)(i) and (3)(ii) of one direction (`u_select.judge`'s `forward` or `reverse`) as rows."""
    if d["chosen"] is None:
        return [{"section": section, "line": Sel.LINES[0], "note": f"no cell holds a P on the {d['choice_block']} block"}]
    i = d["i"]
    rows = [{"section": section, "line": Sel.LINES[0], "cell": d["chosen"], "reference": r_star,
             "measure": Sel.PRIMARY_KEY, "block": d["judged_block"], "value": i["value"],
             "reference_value": i["reference"], "difference": i["difference"], "lower": i["lower"],
             "level": i["level"], "k": int(k), "n": i["n"], "boot_block": i["boot_block"], "draws": i["draws"],
             "seed": i["seed"], "first_date": i["first_date"], "last_date": i["last_date"], "holds": i["holds"]}]
    for g in d["ii"]:
        own = best.get(g["measure"], {})
        rows.append({"section": section, "line": Sel.LINES[1], "cell": d["chosen"], "reference": r_star,
                     "measure": g["measure"], "block": d["judged_block"], "direction": g["direction"],
                     "unit": g["unit"], "value": g["value"], "reference_value": g["reference"],
                     "worse_by": g["worse_by"], "allowed": g["allowed"], "blank": g["blank"], "n": g["n"],
                     "n_reference": g["n_reference"], "holds": g["holds"],
                     "own_row_to_beat": own.get("config") or "", "own_row_to_beat_value": own.get("value", float("nan"))})
    return rows


def tables(fam: dict[str, Any], J: dict[str, Any], r_star: str, best: dict[str, dict], cards: list[dict],
           coin_rows: list[dict] | None, coin: dict | None, floor: dict | None, lines: dict[str, bool | None],
           count: dict[str, Any], *, chosen_base: str | None = None, labels: dict[str, str] | None = None,
           notes: dict[str, str] | None = None, refused: Any = ()) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The result's rows after the identities (sections `cell`, `choice`, `judged`, `reverse`, `guards`, `verdict`) and
    the verdict (`u_select.verdict`). `J`: `u_select.judge`'s output; `cards`: the `cell` rows; `coin_rows`, `coin`,
    `floor`: lines (3)(iv) and (3)(iii) where they ran; `lines`: every line's state. `chosen_base`: the chosen cell's
    base (None: `p16`'s reading, a coin design) -- on a base that is not a coin design line (3)(iv) is `not applicable`
    (one `guards` row says so; coin rows, if any were handed in, are not written) and never counts as held. On a
    base whose every figure is an upper bound (`u_select.upper_bound`: a joint base, D-643 (3)) the verdict is never
    CARRIED: with every line held it is `u_select.HOLDS_AS_UPPER_BOUND`, and the verdict row says what the cell waits
    for. `labels` ({cell: label}; D-643): every row of a labelled cell carries its label in a `label` column -- with no
    labelled cell the rows carry no such column, as before. `notes` ({cell: note}; D-644 (4)): the same in a
    `label_note` column (a hypothetical cell's `u_select.HYPOTHETICAL_NOTE`). `refused` (D-644 (4)): the cells labelled
    `hypothetical_hedge` -- REFUSED as the chosen cell, in a choice row, as R* or as a measure's row to beat, and on
    a hypothetical `chosen_base`: such a cell's rows here are its `cell` rows only."""
    refused = list(refused)
    if chosen_base is not None and Sel.hypothetical(chosen_base):
        Sel.refuse_labelled([J["chosen"]], [J["chosen"]], "the judgement")
    Sel.refuse_labelled([J["chosen"]], refused, "the judgement")
    Sel.refuse_labelled([r["cell"] for d in ("forward", "reverse") for r in J[d]["choice"]["rows"]], refused,
                        "the choice")
    Sel.refuse_labelled([r_star, *[v.get("config") for v in best.values()]], refused, "the rows to beat")
    coin_applies = True if chosen_base is None else Sel.coin_design(chosen_base)
    bound = False if chosen_base is None else Sel.upper_bound(chosen_base)
    rows = list(cards)
    for direction in ("forward", "reverse"):
        rows += [{"section": "choice", "direction": direction, "block": r["block"], "cell": r["cell"],
                  "measure": Sel.PRIMARY_KEY, "value": r["p"], "n": r["n"], "chosen": r["chosen"]}
                 for r in J[direction]["choice"]["rows"]]
    rows += _pair_rows("judged", J["forward"], r_star, fam["k"], best)
    rows += _pair_rows("reverse", J["reverse"], r_star, fam["k"], best)
    if J["years"] is not None:
        y = J["years"]
        rows += [{"section": "guards", "line": Sel.LINES[4], "cell": J["chosen"], "reference": r_star,
                  "measure": Sel.PRIMARY_KEY, "year": r["year"], "value": r["value"], "reference_value": r["reference"],
                  "n": r["n"], "blank": r["blank"], "worse": r["worse"]} for r in y["rows"]]
        rows.append({"section": "guards", "line": Sel.LINES[4], "cell": J["chosen"], "reference": r_star,
                     "measure": "summary", "years_worse": y["years_worse"], "allowed": y["allowed"],
                     "holds": y["holds"]})
    if not coin_applies and J["chosen"] is not None:
        rows.append({"section": "guards", "line": Sel.LINES[3], "cell": J["chosen"], "reference": r_star,
                     "measure": "summary",
                     "note": f"not applicable: the cell's base {chosen_base} is not a coin design"})
    if coin_applies and coin_rows is not None and coin is not None:
        rows += [{"section": "guards", "line": Sel.LINES[3], "cell": J["chosen"], "reference": r_star,
                  "measure": Sel.PRIMARY_KEY, "coin_seed": r["coin_seed"], "value": r["value"],
                  "reference_value": r["reference_value"], "n": r["n"], "n_reference": r["n_reference"],
                  "win": bool(float(r["value"]) > float(r["reference_value"]))} for r in coin_rows]
        rows.append({"section": "guards", "line": Sel.LINES[3], "cell": J["chosen"], "reference": r_star,
                     "measure": "summary", "sequences": coin["sequences"], "wins": coin["wins"],
                     "wins_needed": coin["wins_needed"], "holds": coin["holds"],
                     "note": "" if r_star in Sel.COIN_DESIGNS else f"{r_star} is not a coin design: its P is the same "
                                                                   "under every sequence"})
    if floor is not None:
        rows.append({"section": "guards", "line": Sel.LINES[2], "cell": J["chosen"],
                     "reference": Sel.GATE_ROW_TO_BEAT, "measure": "growth on the required bankroll at the bound",
                     **{k: floor[k] for k in ("growth_at_bound", "row_to_beat_growth", "every_r_resolves",
                                              "rules_verified", "holds")},
                     "growth_at_point": floor.get("growth_at_point", float("nan")),
                     "required_p90": floor.get("required_p90", float("nan")), "seed": floor.get("seed"),
                     "paths": floor.get("paths"), "note": "; ".join(floor["problems"]),
                     **dict(floor.get("entry") or {})})         # D-630: the gate's columns for the cell's entry options
    v = Sel.verdict(lines, coin_design=coin_applies, upper_bound=bound)
    rows += [{"section": "verdict", "line": line, "status": v["status"][line]} for line in Sel.LINES]
    rows.append({"section": "verdict", "line": "verdict", "verdict": v["verdict"], "first_failing": v["first_failing"],
                 "status": v["first_failing_status"], "family": fam["family"], "decision": fam["decision"],
                 "k": int(fam["k"]), "level": J["level"], "cells": len(fam["cells"]), "cell": J["chosen"] or "",
                 "base": chosen_base or "",
                 "reference": r_star, "program_cells": count["program"], "program_families": count["families"],
                 **({"note": Sel.UPPER_BOUND_WAITS_FOR} if bound else {})})
    if labels:                                  # D-643: every row of a labelled cell says so
        for r in rows:
            if r.get("cell") in labels and not r.get("label"):
                r["label"] = labels[r["cell"]]
    if notes:                                   # D-644 (4): and a hypothetical cell's rows say what the label means
        for r in rows:
            if r.get("cell") in notes:
                r["label_note"] = notes[r["cell"]]
    return rows, v


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import subprocess
    import tempfile

    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import customer_journey as CJ
    import rc150_dev_test as R
    import rc150_firm_split as F
    import rc150_payout_screen as PS
    import rc_dev_test as D
    import rc_screen as S
    import user_journey as UJ

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import sha256_of, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", default=None, help="a registered family's name")
    ap.add_argument("--check", action="store_true", help="the identities that can run and the whole pipeline on a few "
                    "starts; identity and timing lines only; nothing written to results/")
    ap.add_argument("--starts", type=int, default=None, help="with --check: this many starts, spread evenly")
    ap.add_argument("--coins", type=int, default=None, help="with --check: the first coin sequences of the guard")
    ap.add_argument("--paths", type=int, default=None, help="with --check: the gate floor's paths (at the screen's "
                    "seed; the fresh seed is never drawn in a check)")
    ap.add_argument("--workers", type=int, default=1, help="replay workers (the memory guard may grant fewer)")
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs are kept (outside the checkout)")
    ap.add_argument("--check-overrides", default=None, help=argparse.SUPPRESS)    # --check only: a JSON overrides dict
    ap.add_argument("--check-base", default=None, help=argparse.SUPPRESS)         # ... and the base it is put on
    ap.add_argument("--trades-hash", action="store_true", help="D-639: every window base's content hashes from the "
                    "screens' own builders beside their pins; no campaign, nothing written")
    a = ap.parse_args(argv)
    if a.trades_hash:
        return window_trades_hash()
    if not a.check and (a.starts is not None or a.coins is not None or a.paths is not None):
        print(f"REFUSED ({DECISION}): a family runs every start, the fifty coin sequences and {Sel.GATE_PATHS} paths; a "
              "smaller run is --check.")
        return 2
    window_check = [b for b in str(a.check_base or "").split(",") if b] if a.check_overrides is None else []
    joint_check = window_check if (window_check and all(Sel.is_joint_base(b) for b in window_check)) else []
    if not (window_check and all(Sel.is_window_base(b) for b in window_check)):
        window_check = []
    if joint_check:
        # D-643: each named joint base as one cell of the NULL family -- built, its identities, its replays through
        # the joint engine and its pooled gate calls exercised; nothing registered, counted or written
        import u_firms as UF

        bad = []
        if not a.check:
            bad.append("--check-overrides and --check-base are --check's")
        if a.family is not None:
            bad.append("--check-base runs on the NULL family: name no family")
        if len(set(joint_check)) != len(joint_check):
            bad.append("a joint base is named once")
        fam = {"family": NULL, "decision": DECISION, "k": 1,
               "cells": tuple({"name": f"{UF.CHECK_CELL}_{b}", "base": b, "overrides": {}} for b in joint_check)}
        bad = bad or Sel.family_problems(fam)
        if bad:
            print(f"REFUSED ({DECISION}): " + "; ".join(bad[:6]))
            return 2
    elif window_check:
        # D-639: each named window base as one cell of the NULL family -- built, its identities and facts, its
        # replays and gate calls exercised; nothing registered, counted or written, nothing of the cell printed
        bad = []
        if not a.check:
            bad.append("--check-overrides and --check-base are --check's")
        if a.family is not None:
            bad.append("--check-base runs on the NULL family: name no family")
        if len(set(window_check)) != len(window_check):
            bad.append("a window base is named once")
        fam = {"family": NULL, "decision": DECISION, "k": 1,
               "cells": tuple({"name": f"{WINDOW_CHECK_CELL}_{b}", "base": b, "overrides": {}} for b in window_check)}
        bad = bad or Sel.family_problems(fam)
        if bad:
            print(f"REFUSED ({DECISION}): " + "; ".join(bad[:6]))
            return 2
    elif a.check_overrides is not None or a.check_base is not None:
        # the given overrides as one cell of the NULL family: the kinds exercised on real data with nothing registered,
        # counted or written, and nothing of the cell printed but identity and timing lines
        bad = []
        if not a.check:
            bad.append("--check-overrides and --check-base are --check's")
        if a.family is not None:
            bad.append("--check-overrides runs on the NULL family: name no family")
        if a.check_overrides is None:
            bad.append("--check-base needs --check-overrides")
        check_base = Sel.DEFAULT_BASE if a.check_base is None else a.check_base
        check_ov: Any = None
        if not bad:
            try:
                check_ov = json.loads(a.check_overrides)
            except ValueError:
                bad.append("--check-overrides is not JSON")
        if not bad:
            bad = Sel.override_problems(check_ov, check_base) or ([] if check_ov else ["no override given"])
        if bad:
            print(f"REFUSED ({DECISION}): " + "; ".join(bad[:6]))
            return 2
        fam = {"family": NULL, "decision": DECISION, "k": 1,
               "cells": ({"name": CHECK_CELL, **({} if check_base == Sel.DEFAULT_BASE else {"base": check_base}),
                          "overrides": check_ov},)}
        bad = Sel.family_problems(fam)
        if bad:
            print(f"REFUSED ({DECISION}): " + "; ".join(bad[:6]))
            return 2
    else:
        try:
            fam = family_of(a.family, a.check)
        except SystemExit as e:
            print(e)
            return 2
    rd = RESULTS_DIR
    t_all = time.time()
    n_starts = (4 if a.starts is None else int(a.starts)) if a.check else None
    seeds = Sel.COIN_SEQUENCES[:(2 if a.coins is None else int(a.coins))] if a.check else Sel.COIN_SEQUENCES
    gate_paths = (4 if a.paths is None else int(a.paths)) if a.check else Sel.GATE_PATHS
    family_id = Sel.family_id(fam["decision"], fam["family"])
    bases = bases_of(fam)                       # the bases the family's cells name: only these are built and replayed

    idents: list[dict] = []
    failures: list[str] = []
    not_run: list[str] = []

    def settle(rows: list[dict]) -> bool:
        ok = True
        for r in rows:
            idents.append(r)
            who = " ".join(x for x in (r["config"], r["arm"]) if x) or DECISION
            count = "" if r["compared"] is None else f" [{r['compared']} compared, {r['differing']} differing]"
            if r["holds"]:
                print(f"identity HOLDS: {who}: {r['check']}{count}", flush=True)
            elif not r["refuses"]:
                print(f"identity DIFFERS (read from the exact-length run, not a refusal): {who}: {r['check']}{count}",
                      flush=True)
            else:
                print(f"identity FAILS: {who}: {r['check']}{count} -- {r['problems']}", flush=True)
                failures.append(f"{who}: {r['problems']}")
                ok = False
        return ok

    def refused() -> int:
        print(f"REFUSED ({DECISION}): {len(failures)} identities fail; nothing read, nothing written -- "
              + "; ".join(failures[:8]))
        return 3

    # ---- the declarations
    decl = Sel.declaration()
    bad = Sel.declaration_problems(decl) + U.declaration_problems(U.declaration())
    if tuple(Sel.SECTIONS[:1]) != ("identity",) or Sel.COIN_SEQUENCES[0] != 20261600:
        bad.append("the sections or the coin sequences are not the module's")
    if not settle([UJ._ident("", "", f"DECISIONS.md's {DECISION} row (sha256 {decl['sha256']}) and every phrase "
                             f"u_select's constants rest on; {U.DECISION}'s row by U1's pin", bad)]):
        return refused()

    # ---- U1's file: the rows to beat
    df = u1_table(rd)
    if df is None:
        if not a.check:
            print(f"REFUSED ({DECISION}): results/{U1_FILE} is not on file -- U1 (D-620) has not been run and read. A "
                  "family is paired with that file start for start and takes R* from it; nothing run, nothing written.")
            return 3
        not_run += [f"results/{U1_FILE} is absent: the reference cell against its {b} start rows start for start"
                    for b in bases if not Sel.is_window_base(b) and not Sel.is_joint_base(b)]
        not_run += [f"results/{U1_FILE} is absent: the joint base {b} against its {Sel.JOINT_EQUALS_U1[b]} start rows "
                    "start for start" for b in bases if b in Sel.JOINT_EQUALS_U1]
        if any(Sel.is_joint_base(b) for b in bases):
            not_run.append(f"results/{U1_FILE} is absent: the 5 + 0 cell through the joint engine against its p16 "
                           "start rows start for start")
        not_run += [f"results/{U1_FILE} is absent: the window base {b} against its {Sel.WINDOW_EQUALS_U1[b]} start "
                    "rows start for start" for b in bases if b in Sel.WINDOW_EQUALS_U1]
        not_run += [f"results/{U1_FILE} is absent: the scorecard's readings recomputed from its {', '.join(Sel.ROWS_TO_BEAT)} "
                    "start rows against its own rows; R* by D-621 (2)",
                    f"results/{U1_FILE} is absent: a cell's `equals_u1` twin"]
        side = None
    else:
        side = u1_side(df)
        settle([UJ._ident("", ARM, f"results/{U1_FILE}: each row to beat's ({', '.join(Sel.ROWS_TO_BEAT)}) start rows "
                          "carry every record the scorecard reads; its readings recomputed from them "
                          "(user_journey.metric_rows) equal the file's own rows; R* is the same with P on the starts "
                          f"with {Sel.P_HORIZON} sessions and with the mean of the file's three shares", side["problems"],
                          compared=int(sum(len(v) for v in side["records"].values())))])
    g06, bad = p06_growth(rd)
    settle([UJ._ident("", "", f"results/{SCOREBOARD} holds one {Sel.GATE_ROW_TO_BEAT} row with a growth at the bound "
                      "(the gate floor's row to beat, D-365, D-382)", bad)])
    if failures:
        return refused()

    # ---- the inputs, base by base (only the bases the family's cells name)
    XS: dict[str, dict[str, Any]] = {}
    W15 = None
    if P16 in bases:
        print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
        t0 = time.time()
        X = inputs(rd)
        print(f"timing: the inputs: {time.time() - t0:.0f} s", flush=True)
        settle([UJ._ident(P16, "", f"the trades are results/{R.SPEC.screen_file}'s {R.SPEC.cell} (count, busiest day, "
                          "capacity, long share, candidates a day, every R's unresolved share) and their content hash "
                          f"is P-16's registered {R.SPEC.trades_sha256}", X["trade_problems"]),
                UJ._ident(P16, "", "the coin guard's construction (the same walk, the coin table re-dealt: "
                          f"rc150_routing.coin_cell) at the registered coin {Sel.REGISTERED_COIN} rebuilds P-16's "
                          "trades", X["swap_problems"])])
        if failures:
            return refused()
        if a.check or (side is not None and side["r_star"] == P15):
            t0 = time.time()
            W15 = p15_walk(X)
            settle([UJ._ident(P15, "", "the coin guard's construction for P-15 (rc_stop_walkforward.walk_stop at the "
                              "25-point rung, the cell as rc_reentry_screen.build builds it) at the registered coin "
                              f"rebuilds P-15's registered {D.P15.trades_sha256}", p15_swap_problems(W15))])
            print(f"timing: P-15's walk and cell: {time.time() - t0:.0f} s", flush=True)
            if a.check and not (side is not None and side["r_star"] == P15):
                W15 = None                      # the identity ran; the check's guard does not need the walk
                gc.collect()
        if failures:
            return refused()
        X["dates"] = list(X["camp"].dates)
        XS[P16] = X
    if P14 in bases:
        print("P-14's replay setup as U1 builds it (D-518's job builder) and its trades' pins...", flush=True)
        t0 = time.time()
        X14 = p14_inputs(rd)
        print(f"timing: the inputs of base {P14}: {time.time() - t0:.0f} s", flush=True)
        settle([UJ._ident(P14, "", f"the trades are results/{B.SCREEN}'s rank-1 cell {B.cell_label()} (its file's "
                          "sha256, the rung walk's cache inputs, every fact, edge and era row: "
                          f"a3_brk30.identity_with_screen) and P-13's (results/{C.P13_RESULT}'s edge and verdict rows, "
                          "its sha256 pinned: a3_brk30_cb20.p13_trade_problems) -- the registered test's two pins",
                          X14["trade_problems"]),
                UJ._ident(P14, "", f"the setup is U1's {P14} configuration (D-518's row through "
                          "customer_journey.Inputs, as user_journey.build_d518) and the registered test's: the "
                          f"no-closure table {C.NOCLOSE_ID} by a3_brk30_cb20.noclose_plan's hashes, the budget "
                          f"{tuple(C.BUDGET)}, the strict rule {C.STRICT_GAP:g}, the campaign seed {C.SEED}, the "
                          "placement off; its sessions are the pinned trades' day set", X14["setup_problems"])])
        if failures:
            return refused()
        XS[P14] = X14
        built = [b for b in bases if b in XS]           # the window bases are built below, with their own line
        settle([UJ._ident("", "", "the paired readings are on common start dates: every base in use ("
                          + ", ".join(built) + ") replays the same session dates in the same order"
                          + ("" if side is None else f", and each row to beat's start dates in results/{U1_FILE} "
                                                     "are those dates"),
                          date_problems({b: XS[b]["dates"] for b in built}, None if side is None else side["records"]),
                          compared=len(XS[built[0]]["dates"]))])
        if failures:
            return refused()
    # ---- D-639: the window bases -- each built from its stop's walk, its identities, its FACTS before anything runs
    win = [b for b in bases if Sel.is_window_base(b)]
    wcell = {Sel.base_of(c): c for c in fam["cells"] if Sel.is_window_base(Sel.base_of(c))}
    walks: dict[int, dict[str, Any]] = {}
    I0: dict[str, Any] | None = None

    def walk_of(stop: int) -> dict[str, Any]:
        """A stop's walk, one held at a time (memory); P-16's own walk, kept for its coin guard, where that base is
        built."""
        import rc_stop_walkforward as WF

        if P16 in XS and int(stop) == int(R.STOP):
            return XS[P16]["W"]
        if int(stop) not in walks:
            walks.clear()
            gc.collect()
            t0 = time.time()
            walks[int(stop)] = WF.walk_stop(I0, int(stop))
            print(f"timing: the walk at {int(stop) / 4:g} points: {time.time() - t0:.0f} s", flush=True)
        return walks[int(stop)]

    if win:
        print(f"the window bases ({Sel.WINDOW_DECISION}): P-14's inputs, the no-closure plan and each stop's walk...",
              flush=True)
        I0 = XS[P16]["I"] if P16 in XS else S.inputs()
        for b in win:
            t0 = time.time()
            XS[b] = window_inputs(rd, b, I0, walk_of(Sel.WINDOW_BASES[b]["stop_ticks"]))
            print(f"timing: the inputs of base {b}: {time.time() - t0:.0f} s", flush=True)
            settle(XS[b].pop("idents"))
        for line in facts_lines({b: XS[b]["facts"] for b in win}):
            print(line, flush=True)
        if failures:
            return refused()
        settle([UJ._ident("", "", "the paired readings are on common start dates: every base in use ("
                          + ", ".join(bases) + ") replays the same session dates in the same order"
                          + ("" if side is None else f", and each row to beat's start dates in results/{U1_FILE} "
                                                     "are those dates"),
                          date_problems({b: XS[b]["dates"] for b in bases}, None if side is None else side["records"]),
                          compared=len(XS[bases[0]]["dates"]))])
        if failures:
            return refused()
    # ---- D-643: the joint bases -- one set of inputs (U1's builder calls) serves the four; identities first
    joint = [b for b in bases if Sel.is_joint_base(b)]
    jcell = {Sel.base_of(c): c for c in fam["cells"] if Sel.is_joint_base(Sel.base_of(c))}
    JX: dict[str, Any] | None = None
    if joint:
        import u_firms as UF

        print(f"the joint bases ({Sel.JOINT_DECISION}): P-16's cell, its opposite side and the two firms' setups "
              "(rc150_firm_split.inputs, Lucid as firm 1)...", flush=True)
        t0 = time.time()
        JX = UF.inputs(rd)
        print(f"timing: the inputs of the joint bases: {time.time() - t0:.0f} s", flush=True)
        settle([UJ._ident("joint", "", f"the trades are results/{R.SPEC.screen_file}'s {R.SPEC.cell} (count, busiest "
                          "day, capacity, long share, candidates a day, every R's unresolved share) and their content "
                          f"hash is P-16's registered {R.SPEC.trades_sha256}; the opposite side is aligned one for "
                          "one on the other side of every event (rc150_firm_split.inputs, refused otherwise)",
                          JX["trade_problems"])])
        for b in joint:
            n_top, n_luc = Sel.joint_seats(b)
            settle([UJ._ident(b, "", f"seats {n_top}+{n_luc}, each firm's budget floor(20 x seats / 5) in 21 trading days; "
                              "firm 1 Lucid's verified contract -- its evaluation price row verified, its household "
                              "caps as D-575 read them and the cell inside them, its open rows the two unpriced fees "
                              f"charged at zero ({Sel.UPPER_BOUND_LABEL}: every figure an upper bound on them)"
                              + ("" if UF.opens_of(b) is None else f"; the Lucid firm opens at the first payout's "
                                 f"arrival ({Sel.SEQUENCING_DECISION} (2): the joint run's sequencing option)")
                              + ("" if not Sel.hypothetical(b) else f"; the {UF.deal_of(b)} deal -- HYPOTHETICAL "
                                 f"({Sel.HYPOTHETICAL_LABEL}: prohibited at both firms; never chosen, judged, a "
                                 "guard's cell or a row to beat)"),
                              UF.rules_problems(b))])
            XS[b] = {"dates": list(JX["dates"]), "resolves": bool(JX["resolves"]), "seats": (n_top, n_luc),
                     "opens": UF.opens_of(b), "deal": UF.deal_of(b),
                     "cell": UF.base_def(jcell[b]["name"], b)["cell"]}
        if failures:
            return refused()
        settle([UJ._ident("", "", "the paired readings are on common start dates: every base in use ("
                          + ", ".join(bases) + ") replays the same session dates in the same order"
                          + ("" if side is None else f", and each row to beat's start dates in results/{U1_FILE} "
                                                     "are those dates"),
                          date_problems({b: XS[b]["dates"] for b in bases}, None if side is None else side["records"]),
                          compared=len(XS[bases[0]]["dates"]))])
        if failures:
            return refused()
    #: the bases replayed: every base but a window base that is not runnable (recorded, never a cell: D-639 (2))
    live = [b for b in bases if not Sel.is_window_base(b) or XS[b]["runnable"]]
    for b in bases:
        if b not in live:
            print(f"not runnable ({Sel.WINDOW_DECISION} (2)): {wcell[b]['name']} on base {b} -- "
                  f"{XS[b]['facts']['reason']}; recorded, not a cell, never replayed or counted", flush=True)
    if not live:
        print(f"REFUSED ({DECISION}): no cell of the family is runnable; nothing run, nothing written.")
        return 3
    #: the name each base's own replay runs under: a window base's is its cell's (the base IS the cell)
    ref_name = {b: (wcell[b]["name"] if Sel.is_window_base(b) else jcell[b]["name"] if Sel.is_joint_base(b) else b)
                for b in bases}
    defs = {b: ({"config": ref_name[b], "label": "", "cell": XS[b]["cell"], "slices": {}, "starts": None,
                 "journey": {}} if Sel.is_window_base(b) else UF.base_def(ref_name[b], b) if Sel.is_joint_base(b)
                else next(c for c in UJ.CONFIG_DEFS if c["config"] == b))
            for b in bases}

    resume = None
    if not a.check and not a.no_resume:
        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = F.Resume(folder, f"{commit}_{fam['family']}", Sel.result_name(fam["family"]))

    def cached(label: str, make) -> Any:
        return F._cached(resume, label, make)

    n_days = len(XS[live[0]]["dates"])
    chosen_starts = UJ.start_choice(n_days, n_starts)
    timing: dict[str, dict[str, Any]] = {}

    def jobs_of(base: str, overrides: dict) -> dict[str, dict]:
        """A cell's two arms on its base: P-16's campaign with the overrides (`cell_jobs`), U1's `p14` jobs with
        them (`p14_jobs`), or a window base's own campaign, table and budget (`cell_jobs`; it takes no override)."""
        if base == P14:
            return p14_jobs(XS[P14], overrides)
        if joint and base == UF.TWIN:           # D-643: the 5 + 0 cell through the joint engine (the identity's side)
            return UF.jobs(JX, (Sel.JOINT_TOPSTEP_SEATS,), None)
        if Sel.is_joint_base(base):             # D-643, D-644: U1's joint job for the base's seats, option and deal
            return UF.jobs(JX, XS[base]["seats"], XS[base]["opens"], XS[base]["deal"])
        return cell_jobs(XS[base]["camp"], XS[base]["plan"], XS[base]["budget"], overrides)

    def replay(name: str, arm: str, overrides: dict, c_def: dict, base: str = P16) -> list[dict]:
        """A cell and arm on the run's starts, with its identities (kept together: a resumed run reads both back)."""
        def make() -> dict[str, Any]:
            job = jobs_of(base, overrides)[arm]
            v = run_starts(job, name, arm, chosen_starts, a.workers)
            rows, notes = UJ.config_identities(c_def, arm, v["starts"], float(job["sub"]), rd, n_starts is None)
            return {"starts": [{"rec": x["rec"], "differs": x["differs"],
                                **({"entry": x["entry"]} if x.get("entry") else {}),     # D-630: only when one is on
                                **({"second_firm": x["second_firm"]} if x.get("second_firm") else {}),    # D-643
                                **({"deal": x["deal"]} if x.get("deal") else {})}                         # D-644
                               for x in v["starts"]], "idents": rows,
                    "notes": notes, "n": len(v["starts"]), "seconds": v["seconds"]}

        v = cached(f"cell|{name}|{arm}", make)
        n, secs = int(v["n"]), float(v["seconds"])
        timing[f"{name}|{arm}"] = {"starts": n, "seconds": round(secs, 1)}
        print(f"timing: {name} {arm}: {n} starts in {secs:.1f} s ({secs / max(n, 1):.2f} s a start)", flush=True)
        not_run.extend(v["notes"])
        settle(list(v["idents"]))
        return v["starts"]

    def cell_def(name: str, base: str) -> dict[str, Any]:
        return {"config": name, "label": "", "cell": defs[base]["cell"], "slices": {}, "starts": None, "journey": {}}

    def base_table(base: str) -> Any:
        """The table a base's cells run on (the no-closure plan on either override base)."""
        if base == P14:
            return XS[P14]["I"].plan(XS[P14]["c"]["kind"], XS[P14]["c"]["table"])
        return XS[base]["plan"]

    def micro_of(base: str) -> float | None:
        """One micro's dollars at an override base's widest stop (D-659's least risk); None for another base."""
        return one_micro_dollars(XS[base]["camp"].blocks) if base in (P16, P14) else None

    # ---- D-653: each funded-plan cell's table, keys and sizes -- checked, and its facts printed, before anything runs
    plan_facts: dict[str, dict[str, Any]] = {}
    for c in fam["cells"]:
        spec = funded_plan_of(c["overrides"])
        if spec is None or Sel.base_of(c) not in live:
            continue
        b = Sel.base_of(c)
        bad, plan_facts[c["name"]] = plan_cell_problems(jobs_of(b, dict(c["overrides"])), base_table(b), spec)
        for line in plan_lines(c["name"], b, plan_facts[c["name"]]):
            print(line, flush=True)
        both = Sel.funded_plan_paid(spec)
        settle([UJ._ident(c["name"], "", f"the cell's table is {LABEL[b]}'s with its funded phase (activation to the "
                          "first payout) " + ("and its paid phase (after a first payout) each " if both else "")
                          + "replaced by one leaf -- "
                          f"{Sel.funded_plan_leaf_name(spec['risk'], spec['rr'])}"
                          + (f" and {Sel.funded_plan_leaf_name(spec['risk'], spec['rr'], 'paid')}" if both else "")
                          + ", a routed trade, the base's trade limit -- the evaluation's "
                          + ("leaves" if both else "and the paid phase's leaves")
                          + " the base's subtree for subtree, the "
                          "table validated (no tier-1 breach) and not re-solved; it reaches the replay's engine "
                          "arguments at both arms; every day's block carries every R it asks for; the protocol's "
                          "funded leg is the plan's; on the bound arm the blocks' base column is their own column at "
                          "the plan's R (the edge and bound keys re-pointed, as D-641's window bases); and the plan's "
                          "dollars buy a micro at every stop the trades carry and every tier of the funded ladder, "
                          "none standing aside", bad)])
    # ---- D-659: each resolve cell's table, arguments and sizes -- checked, and its facts printed, before anything runs
    resolve_facts: dict[str, dict[str, Any]] = {}
    for c in fam["cells"]:
        spec = funded_resolve_of(c["overrides"])
        if spec is None or Sel.base_of(c) not in live:
            continue
        b = Sel.base_of(c)
        bad, resolve_facts[c["name"]] = resolve_cell_problems(jobs_of(b, dict(c["overrides"])), jobs_of(b, {}),
                                                               base_table(b), spec)
        for line in resolve_lines(c["name"], b, resolve_facts[c["name"]]):
            print(line, flush=True)
        settle([UJ._ident(c["name"], "", f"the cell's table is {LABEL[b]}'s with, in its funded phase (activation to "
                          "the first payout), every state whose balance is below the account's starting balance "
                          "decided by a bold leaf -- the cushion band's lower edge on the table's own grid (never more "
                          "than the room), "
                          + ("never less than one micro at the base's widest stop" if Sel.funded_resolve_lowest(spec)
                             != "base" else "the band under one micro left to the base's own leaves") + ", at "
                          f"{float(spec['rr']):g}R, one routed trade a session -- every funded state at or above the "
                          "starting balance (the fresh account's among them), every paid state and every evaluation "
                          "state deciding exactly what the base decides, over the table's whole grid of balance and "
                          "cushion bands, winning days and request days; the table validated (no tier-1 breach) and "
                          "not re-solved; it reaches the replay's engine arguments at both arms and NOTHING else of "
                          "them differs from the base's (the edge and bound keys, the protocol's funded leg and every "
                          "day's block the base's own: the fresh funded decision is unchanged); every day's block "
                          "carries every R it asks for; and every bold leaf buys a micro at every stop the trades "
                          "carry, none standing aside", bad)])
    if failures:
        return refused()
    gc.collect()

    # ---- each base's reference cell (the base itself, no override): the identity's side
    ref_outs: dict[str, list[dict]] = {}
    reference_records: dict[str, list[dict]] = {}
    twin_outs: list[dict] = []
    if joint:                                   # D-643: the 5 + 0 cell through the joint engine -- P-16 alone
        twin_def = {**UF.base_def(UF.TWIN), "label": ""}
        twin_outs = replay(UF.TWIN, ARM, {}, twin_def, UF.TWIN)
        if df is not None:
            settle([UJ._ident(UF.TWIN, ARM, "the 5 + 0 cell through the joint engine (the joint cells' twin, never "
                              f"counted) replayed here equals results/{U1_FILE}'s {UF.TWIN_EQUALS_U1} start rows -- "
                              "P-16's single-engine records -- start for start (every column of a start)",
                              u1_start_problems(UJ.start_rows(twin_def, ARM, twin_outs),
                                                u1_starts(df, UF.TWIN_EQUALS_U1, ARM), f"{UF.TWIN} {ARM}",
                                                whole=n_starts is None), compared=len(twin_outs))])
        if failures:
            return refused()
    for b in live:
        ref_outs[b] = replay(ref_name[b], ARM, {}, defs[b], b)
        ref_rows = UJ.start_rows(defs[b], ARM, ref_outs[b])
        if Sel.is_joint_base(b):                # D-643: the base IS the cell; U1 holds one (5 + 1 from day 0)
            twin = Sel.JOINT_EQUALS_U1.get(b)
            if twin and df is not None:
                settle([UJ._ident(ref_name[b], ARM, f"the joint base {b} replayed here equals results/{U1_FILE}'s "
                                  f"{twin} start rows start for start (every column of a start)",
                                  u1_start_problems(ref_rows, u1_starts(df, twin, ARM), f"{ref_name[b]} {ARM}",
                                                    whole=n_starts is None), compared=len(ref_rows))])
            if XS[b]["opens"] is not None:
                settle([UJ._ident(ref_name[b], ARM, "the second firm opens at the first payout's arrival: on every "
                                  "start the opening day is the 5 + 0 twin's first payout day (the first firm's own); "
                                  "a start that never opened carries the twin's record (P-16 alone); an opened start's "
                                  "record before its opening day -- its event days, first pass, first funded account "
                                  "and first payout, the cash spent before them, every month-end net and fee -- is "
                                  "the twin's (inside the joint run the first firm through the opening day is the "
                                  "first firm alone on every opened path, or the run raises)",
                                  UF.sequence_problems(ref_outs[b], twin_outs), compared=len(ref_outs[b]))])
                if not any((x.get("second_firm") or {}).get("opened_on") is not None for x in ref_outs[b]):
                    not_run.append(f"{ref_name[b]}: no start of this run saw the second firm open -- the opened "
                                   "path's identities were not exercised")
        elif Sel.is_window_base(b):             # D-639: the base IS the cell; U1 holds one (London at 37.5 points)
            twin = Sel.WINDOW_EQUALS_U1.get(b)
            if twin and df is not None:
                settle([UJ._ident(ref_name[b], ARM, f"the window base {b} replayed here equals results/{U1_FILE}'s "
                                  f"{twin} start rows start for start (every column of a start)",
                                  u1_start_problems(ref_rows, u1_starts(df, twin, ARM), f"{ref_name[b]} {ARM}",
                                                    whole=n_starts is None), compared=len(ref_rows))])
        elif df is not None:
            settle([UJ._ident(b, ARM, f"the reference cell ({LABEL[b]}, no override) replayed here equals "
                              f"results/{U1_FILE}'s {b} start rows start for start (every column of a start)",
                              u1_start_problems(ref_rows, u1_starts(df, b, ARM), f"{b} {ARM}", whole=n_starts is None),
                              compared=len(ref_rows))])
        if failures:
            return refused()
        reference_records[b] = [x["rec"] for x in ref_outs[b]]

    # ---- the family's cells
    records: dict[str, list[dict]] = {}
    cell_outs: dict[str, list[dict]] = {}
    for c in fam["cells"]:
        name, ov, b = c["name"], dict(c["overrides"]), Sel.base_of(c)
        if b not in live:                       # D-639 (2): not runnable -- recorded above, not a cell
            continue
        c_def = cell_def(name, b)
        if not ov:                              # a base's own cell (a reference, or a window base): the replay above
            outs = ref_outs[b]
        else:
            outs = replay(name, ARM, ov, c_def, b)
        records[name] = [x["rec"] for x in outs]
        cell_outs[name] = outs
        if own_table_kind(ov) is not None:      # D-653 (7), D-659 (7): nothing differs before a funded account exists
            n_funded = sum(1 for x in ref_outs[b] if not Sel._blank(x["rec"]["first_funded"]))
            settle([UJ._ident(name, ARM, "the evaluation leg is the base's: on every start the cell's record up to "
                              f"the first funded account of {LABEL[b]}'s reference replay (the same start, the same "
                              "arm) is the reference's -- that account's activation day, the pass, activation and "
                              "payout days up to it, the first pass and the cash spent before it, every month-end net "
                              "and fee up to it -- and a start whose reference funds no account carries the "
                              "reference's record whole (the plan changes only what a funded account trades; the "
                              f"reference funds an account on {n_funded} of these starts)",
                              evaluation_leg_problems(outs, ref_outs[b]), compared=len(outs))])
            if not any(U.record_problems(x["rec"], y["rec"]) for x, y in zip(outs, ref_outs[b])):
                not_run.append(f"{name}: on no start of this run does the cell's record differ from its base's "
                               "reference -- the plan's leaf decided nothing a record shows, so the identity above "
                               "compared whole records only")
        if funded_resolve_of(ov) is not None:   # D-659: nothing differs before a funded account is under water
            sample = list(chosen_starts) if a.check else list(chosen_starts)[::RESOLVE_IDENTITY_EVERY]

            def under(name=name, b=b, ov=ov, sample=sample) -> dict[str, Any]:
                t0 = time.time()
                job, ref_job = jobs_of(b, ov)[ARM], jobs_of(b, {})[ARM]
                low = min(float(x["from"]) for x in resolve_facts[name]["bands"])
                tasks = [(name, ARM, job["blocks"], job["dates"], job["args"], ref_job["args"], low,
                          sample[j:j + UJ.CHUNK_STARTS]) for j in range(0, len(sample), UJ.CHUNK_STARTS)]
                import u_family as runner       # by its importable name: a pool's workers find the task there
                res = (CJ._pool_run(tasks, runner.resolve_identity_task, a.workers, f"{name} under water")
                       if tasks else [])
                return {"rows": [x for chunk in res for x in chunk], "seconds": time.time() - t0}

            uw = cached(f"underwater|{name}", under)
            timing[f"{name}|under_water"] = {"starts": len(uw["rows"]), "seconds": round(float(uw["seconds"]), 1)}
            print(f"timing: {name} under water: {len(uw['rows'])} starts in {float(uw['seconds']):.1f} s", flush=True)
            n_under = sum(1 for x in uw["rows"] if x["day"] is not None)
            settle([UJ._ident(name, ARM, "nothing differs before a funded account is under water: on "
                              + ("every start of this check" if a.check else
                                 f"every {RESOLVE_IDENTITY_EVERY}th start (a thinning declared for cost: the identity "
                                 "needs the engine's daily recorder, which the counted replays run without)")
                              + f", the cell and {LABEL[b]} replayed again with the recorder on, the two runs are one "
                              "through the close of the first session at which an unpaid, live funded account stands "
                              "below its starting balance -- every account's day (balance, loss limit, the day's "
                              "result, the request, the leaf that decided it), the campaign's cash, fees and payouts "
                              "each day, every purchase, pass, failure and activation -- and whole where none ever "
                              "does; no bold leaf decides a session up to that close, none ever on the base, and at "
                              "the next session every such account (with a room the table has a bold leaf for) is "
                              "decided by a bold leaf; the recorded replay is "
                              "the counted one (its passes, activations and month-end cash are the start's record); "
                              "and the counted records of the cell and the reference agree up to that close ("
                              f"a funded account is under water on {n_under} of these starts)",
                              under_water_problems(uw["rows"], outs, ref_outs[b]), compared=len(uw["rows"]))])
            if not n_under:
                not_run.append(f"{name}: on no start of the under-water identity's sample did a funded account stand "
                               "below its starting balance -- it compared whole runs only")
            elif not any(x["bold"] for x in uw["rows"]):
                not_run.append(f"{name}: on no start of the under-water identity's sample did a bold leaf decide a "
                               "session")
        if entry_overrides(ov):                 # D-630: the override reached the replay's engine
            settle([UJ._ident(name, ARM, "each entry option's own record ("
                              + ", ".join(entry_overrides(ov)) + ") is on every start's long replay at its declared "
                              "value: the override reached the replay's engine", entry_problems(ov, outs),
                              compared=len(outs))])
        bad = Sel.window_problems(records[name])
        if bad:
            settle([UJ._ident(name, ARM, f"development start days only (to {Sel.WINDOW_END}, D-621 (4)(a))", bad)])
        if c.get("equals_u1") and df is not None:
            twin = u1_starts(df, c["equals_u1"], ARM)
            settle([UJ._ident(name, ARM, f"the cell equals results/{U1_FILE}'s {c['equals_u1']} start rows start for "
                              "start", u1_start_problems(UJ.start_rows(c_def, ARM, outs), twin, f"{name} {ARM}",
                                                         whole=n_starts is None), compared=len(outs))])
    for line in not_run:
        print(f"identity NOT RUN: {line}", flush=True)
    if failures:
        return refused()

    # ---- R* and the lines that need the records only (the readings start here)
    if side is not None and side["r_star"] is not None:
        r_star, best = side["r_star"], side["by_measure"]
        star_records = side["records"][r_star]
        stand_in = False
    else:                                       # --check without U1's file: the first base's reference stands in for R*
        r_star, best, star_records, stand_in = live[0], {}, reference_records[live[0]], True
    #: D-644 (4): the cells labelled hypothetical_hedge -- written beside, REFUSED in the choice, the judgement, every
    #: guard and the rows to beat
    hypo = [c["name"] for c in fam["cells"] if Sel.hypothetical(Sel.base_of(c))]
    Sel.refuse_labelled([r_star, *Sel.ROWS_TO_BEAT, *[v.get("config") for v in best.values()]], hypo,
                        "the rows to beat")
    cells = [(c["name"], records[c["name"]]) for c in fam["cells"] if c["name"] in records and c["name"] not in hypo]
    J = Sel.judge(cells, star_records, int(fam["k"]), refused=hypo)     # the choice: the best P on its block
    lines: dict[str, bool | None] = dict(J["lines"])
    chosen = next((c for c in fam["cells"] if c["name"] == J["chosen"]), None)
    chosen_base = None if chosen is None else Sel.base_of(chosen)
    cards = []
    if side is not None:
        for c in Sel.ROWS_TO_BEAT:
            if c in side["cards"]:
                cards += _card_rows(c, f"row to beat (results/{U1_FILE})", ARM, side["cards"][c], best=best or None)
    for b in live:
        if Sel.is_window_base(b) or Sel.is_joint_base(b):   # no reference: such a base's cell is a family cell (below)
            continue
        cards += _card_rows(REFERENCES[b], f"the reference cell ({LABEL[b]}, no override; the identity's side, not "
                                           "counted)", ARM, Sel.scorecard(reference_records[b]), base=b)
    for c in fam["cells"]:
        if Sel.counted(c) and c["name"] in records:
            cards += _card_rows(c["name"], UF.HYPOTHETICAL_ROLE if c["name"] in hypo else "family cell", ARM,
                                Sel.scorecard(records[c["name"]]), overrides=c["overrides"], counted=True,
                                base=Sel.base_of(c))
            cards += entry_rows(c["name"], Sel.base_of(c), ARM, c["overrides"], cell_outs[c["name"]])    # beside
            if c["name"] in plan_facts:                 # D-653: the plan's table and sizes -- inputs, beside
                cards += plan_rows(c["name"], Sel.base_of(c), plan_facts[c["name"]], c["overrides"])
            if c["name"] in resolve_facts:              # D-659: the bold leaves and their sizes -- inputs, beside
                cards += resolve_rows(c["name"], Sel.base_of(c), resolve_facts[c["name"]], c["overrides"])
            if Sel.is_joint_base(Sel.base_of(c)):       # D-643: a sequenced cell's opening record, beside; D-644:
                cards += UF.opening_rows(c["name"], Sel.base_of(c), ARM, cell_outs[c["name"]])   # a hedged cell's deal
                cards += UF.deal_rows(c["name"], Sel.base_of(c), ARM, cell_outs[c["name"]])
    for b in win:                               # D-639 (2): each window base's facts, runnable or not -- inputs
        cards += fact_rows(wcell[b]["name"], b, XS[b]["facts"])

    # ---- the point arm beside, the gate floor and the coin guard: for the chosen cell only. In --check they are
    #      exercised for the first declared cell of each base instead -- never for the chosen cell as such, so no
    #      printed line depends on a reading; the chosen cell's own lines reach the (temporary) file where it is one
    #      of those.
    coin_rows = coin = floor = None
    # D-644 (4): every hypothetical cell's scorecard at the point arm too (beside its verdict arm's; the bound's shift
    # partly cancels inside a mirrored pair, D-516) -- its own replay, read into no line
    for c in fam["cells"]:
        if c["name"] in hypo and c["name"] in records:
            hb = Sel.base_of(c)
            pt = replay(c["name"], BESIDE_ARM, {}, defs[hb], hb)
            cards += _card_rows(c["name"], UF.HYPOTHETICAL_ROLE, BESIDE_ARM, Sel.scorecard([x["rec"] for x in pt]),
                                overrides=c["overrides"], counted=True, base=hb)
            cards += UF.deal_rows(c["name"], hb, BESIDE_ARM, pt)
            if failures:
                return refused()
    if a.check:                                 # a hypothetical cell's guards are refused: none is exercised for one
        exercised = [c for c in (next(c for c in fam["cells"] if Sel.base_of(c) == b) for b in live)
                     if c["name"] not in hypo]
        for c in fam["cells"]:
            if c["name"] in hypo and c["name"] in records:
                print(f"identity NOT RUN: {c['name']}: the gate floor and the coin line -- guards, refused for a cell "
                      f"labelled {Sel.HYPOTHETICAL_LABEL} ({Sel.JOINT_DECISION} (4))", flush=True)
    else:
        exercised = [] if chosen is None else [chosen]
    for e in exercised:
        b, ov = Sel.base_of(e), dict(e["overrides"])
        is_chosen = chosen is not None and e["name"] == chosen["name"]
        pt = (replay(e["name"], BESIDE_ARM, ov, cell_def(e["name"], b), b) if ov
              else replay(ref_name[b], BESIDE_ARM, {}, defs[b], b))
        if is_chosen:
            cards += _card_rows(e["name"], "the chosen cell at the point arm (beside)", BESIDE_ARM,
                                Sel.scorecard([x["rec"] for x in pt]), overrides=e["overrides"], base=b)
        if failures:
            return refused()
        # the verdict is the first failing line in D-621's order, so a line is run only while every line before it holds
        if not (a.check or (lines[Sel.LINES[0]] is True and lines[Sel.LINES[1]] is True)):
            continue
        # line (3)(iii), the gate floor: first the base's registered gate call without overrides at ITS seed
        used = ov if a.check else {}
        if b == P16:
            def screen_identity(used=used) -> dict[str, Any]:
                t0 = time.time()
                d = gate_run(XS[P16], used, S.SEED, gate_paths, a.workers, "u_family identity")
                read = gate_reading(d)              # the reading's form is exercised; nothing of it is kept or shown
                bad = None
                if int(gate_paths) == S.N_PATHS and not used:
                    bad = PS.growth_problems(d, PS.screen_row(rd))
                return {"problems": bad, "read": sorted(read), "seconds": time.time() - t0,
                        "entry_problems": gate_entry(d, used)[1],
                        "table_problems": plan_gate_problems(d, used, base_table(P16), micro_of(P16))}

            gi = cached("gate|identity", screen_identity)
            timing["gate|identity"] = {"paths": int(gate_paths), "seconds": round(float(gi["seconds"]), 1)}
            print(f"timing: the gate call at the screen's seed, {gate_paths} paths: {float(gi['seconds']):.0f} s",
                  flush=True)
            if gi["problems"] is None:
                print(f"identity NOT RUN: the gate call without overrides at the screen's seed against "
                      f"{PS.SCREEN_FILE}'s {PS.CELL} row needs {S.N_PATHS} paths and no override ({gate_paths} run)",
                      flush=True)
            else:
                settle([UJ._ident(P16, "", f"this script's gate call without overrides at the screen's seed {S.SEED}, "
                                  f"{S.N_PATHS} paths, reproduces results/{PS.SCREEN_FILE}'s {PS.CELL} growth at the "
                                  "bound and point and its required bankroll", list(gi["problems"]))])
        elif b == P14:
            def registered_identity(used=used) -> dict[str, Any]:
                t0 = time.time()
                d, sink = gate_run_p14(XS[P14], used, C.SEED, gate_paths, a.workers, "u_family identity")
                read = gate_reading(d)              # the reading's form is exercised; nothing of it is kept or shown
                paths_bad = rows_bad = None
                if not used:
                    paths_bad = p14_path_problems(rd, sink, "u_family identity", gate_paths)
                    if int(gate_paths) == C.N_PATHS:
                        rows_bad = p14_row_problems(d, p14_registered_rows(rd))
                return {"path_problems": paths_bad, "row_problems": rows_bad, "read": sorted(read),
                        "seconds": time.time() - t0, "entry_problems": gate_entry(d, used)[1],
                        "table_problems": plan_gate_problems(d, used, base_table(P14), micro_of(P14))}

            gi = cached(f"gate|identity|{P14}", registered_identity)
            timing[f"gate|identity|{P14}"] = {"paths": int(gate_paths), "seconds": round(float(gi["seconds"]), 1)}
            print(f"timing: the {LABEL[P14]} gate call at the registered seed, {gate_paths} paths: "
                  f"{float(gi['seconds']):.0f} s", flush=True)
            if gi["path_problems"] is None:
                print(f"identity NOT RUN: the {LABEL[P14]} gate call at the registered seed against "
                      f"{P14_PATHS_FILE}'s {P14_GATE_RUN} run path for path needs no override", flush=True)
            else:
                settle([UJ._ident(P14, "", f"this script's {LABEL[P14]} gate call without overrides at the registered "
                                  f"seed {C.SEED} equals the first {gate_paths} paths of results/{P14_PATHS_FILE}'s "
                                  f"{P14_GATE_RUN} run path for path, point and bound at 0 % "
                                  "(zero_edge_decomposition.PATH_COLS, to 1e-6)", list(gi["path_problems"]),
                                  compared=2 * int(gate_paths))])
            if gi["row_problems"] is None:
                print(f"identity NOT RUN: the {LABEL[P14]} gate call without overrides at the registered seed against "
                      f"{P14_GATE_FILE}'s section {P14_GATE_SECTION} rows at 0 % needs {C.N_PATHS} paths and no "
                      f"override ({gate_paths} run)", flush=True)
            else:
                settle([UJ._ident(P14, "", f"this script's {LABEL[P14]} gate call without overrides at the registered "
                                  f"seed {C.SEED}, {C.N_PATHS} paths, reproduces results/{P14_GATE_FILE}'s section "
                                  f"{P14_GATE_SECTION} rows at 0 %: the growth on the required bankroll at the bound "
                                  "and at the point and the required bankroll at the bound", list(gi["row_problems"]))])
        elif Sel.is_joint_base(b):              # D-643: the joint engine's pooled call -- first the day-0 call of the
            added = UF.added_cell(b)            #   cell's seats at the screen's seed (the row on record)

            def joint_identity(b=b, added=added, e=e) -> dict[str, Any]:
                t0 = time.time()
                d0 = UF.gate_run(JX["X"], added, XS[b]["seats"], None, S.SEED, gate_paths, a.workers,
                                 deal=XS[b]["deal"])
                bad = UF.added_row_problems(rd, added, d0) if int(gate_paths) == S.N_PATHS else None
                seq = None
                if a.check and XS[b]["opens"] is not None:   # the sequenced call's form at the screen's seed, never
                    ds = UF.gate_run(JX["X"], e["name"], XS[b]["seats"], XS[b]["opens"], S.SEED, gate_paths,
                                     a.workers, deal=XS[b]["deal"])     # the fresh; nothing of it is kept or shown
                    seq = sorted(ds)
                return {"problems": bad, "read": sorted(d0), "sequenced_read": seq, "seconds": time.time() - t0}

            gi = cached(f"gate|identity|joint|{added}" + ("" if not a.check else f"|{b}"), joint_identity)
            timing[f"gate|identity|{b}"] = {"paths": int(gate_paths), "seconds": round(float(gi["seconds"]), 1)}
            print(f"timing: the {b} joint gate call(s) at the screen's seed, {gate_paths} paths at each shift: "
                  f"{float(gi['seconds']):.0f} s", flush=True)
            what = ("the day-0 joint call of the cell's seats" if XS[b]["opens"] is None else
                    "the day-0 joint call of the cell's seats (its day-0 sibling: a sequenced cell has no row on record)")
            if gi["problems"] is None:
                print(f"identity NOT RUN: {b}: {what} at the screen's seed against {UF.ADDED_FILE}'s {added} rows "
                      f"needs {S.N_PATHS} paths ({gate_paths} run)", flush=True)
            else:
                settle([UJ._ident(b, "", f"{what} ({added}, unhedged, the option absent) at the screen's seed {S.SEED}, "
                                  f"{S.N_PATHS} paths, reproduces results/{UF.ADDED_FILE}'s {added} growth on the "
                                  "required bankroll at the bound and at the point and its required bankroll",
                                  list(gi["problems"]))])
        else:                                   # D-639: a window base -- first its screen's own gate call
            Xw, sp = XS[b], window_spec(b, "screen")

            def window_identity(b=b, Xw=Xw) -> dict[str, Any]:
                t0 = time.time()
                sc = window_screen_cell(Xw, I0, walk_of(Xw["stop"]))
                d = gate_run(sc, {}, S.SEED, gate_paths, a.workers, "u_family identity")
                read = gate_reading(d)              # the reading's form is exercised; nothing of it is kept or shown
                bad = window_row_problems(rd, b, read) if int(gate_paths) == S.N_PATHS else None
                del sc, d
                capped_bad = None
                if a.check and Xw["cap"] is not None:    # the capped call's form at the screen's seed, never the fresh
                    dc = gate_run(Xw, {}, S.SEED, gate_paths, a.workers, "u_family capped check")
                    gate_reading(dc)
                    capped_bad = gate_policy_problems(dc, Xw["plan"].id)
                return {"problems": bad, "capped_problems": capped_bad, "read": sorted(read),
                        "seconds": time.time() - t0}

            gi = cached(f"gate|identity|{b}", window_identity)
            timing[f"gate|identity|{b}"] = {"paths": int(gate_paths), "seconds": round(float(gi["seconds"]), 1)}
            print(f"timing: the {b} gate call(s) at the screen's seed, {gate_paths} paths: {float(gi['seconds']):.0f} s",
                  flush=True)
            if gi["problems"] is None:
                print(f"identity NOT RUN: the {b} gate call on the screen's own cell (no cap) at the screen's seed "
                      f"against {sp.screen_file}'s {sp.cell} row needs {S.N_PATHS} paths ({gate_paths} run)", flush=True)
            else:
                settle([UJ._ident(b, "", "this script's gate call on the screen's own cell (the table as it is, no "
                                  f"cap) at the screen's seed {S.SEED}, {S.N_PATHS} paths, reproduces "
                                  f"results/{sp.screen_file}'s {sp.cell} growth at the bound and point and its "
                                  "required bankroll", list(gi["problems"]))])
            if gi.get("capped_problems") is not None:
                settle([UJ._ident(b, "", "this script's gate call on the cell's capped list carries the capped table's "
                                  "id on every row: the cap reached the gate", list(gi["capped_problems"]))])
        if entry_overrides(used):               # D-630: the override reached the gate
            settle([UJ._ident(e["name"], "", "this script's gate call with the cell's overrides carries each entry "
                              "option's columns (" + ", ".join(entry_overrides(used)) + ") at its declared value on "
                              "every row: the override reached the gate", list(gi.get("entry_problems") or []))])
        if own_table_kind(used) is not None:    # D-653, D-659: the cell's own table reached the gate
            settle([UJ._ident(e["name"], "", "this script's gate call with the cell's overrides carries the plan's "
                              "table on every row: the plan reached the gate",
                              list(gi.get("table_problems") if gi.get("table_problems") is not None
                                   else ["the gate call recorded no table"]))])
        if failures:
            return refused()
        rp = rules_problems(e) + (UF.rules_problems(b) if Sel.is_joint_base(b) else [])
        resolves = bool(XS[b]["resolves"])
        if a.check:
            fl = {**Sel.gate_floor(float("nan"), g06, resolves, not rp), "seed": None, "paths": int(gate_paths)}
            print("identity NOT RUN: the " + ("" if b == P16 else f"{LABEL.get(b, b)} ") + "gate floor at the fresh "
                  "campaign seed (never drawn in a check)", flush=True)
        else:
            def fresh(b=b, ov=ov, e=e) -> dict[str, Any]:
                t0 = time.time()
                label = f"u_{fam['family']} {e['name']}"
                if Sel.is_joint_base(b):         # D-643: the joint engine's pooled call, the cell with its option
                    g = UF.gate_run(JX["X"], e["name"], XS[b]["seats"], XS[b]["opens"], Sel.GATE_SEED,
                                    Sel.GATE_PATHS, a.workers, deal=XS[b]["deal"])
                    opened = ({} if "paths_opened_at_bound" not in g else          # beside, in the guards row
                              {"second_firm_paths_opened_at_bound": int(g["paths_opened_at_bound"])})
                    return {**g, "seconds": time.time() - t0, "entry": opened, "entry_problems": [],
                            "table_problems": []}
                if b == P14:
                    d, _ = gate_run_p14(XS[P14], ov, Sel.GATE_SEED, Sel.GATE_PATHS, a.workers, label)
                else:                           # P-16's cell; or a window base's own trades, bounds, capacity and table
                    d = gate_run(XS[b], ov, Sel.GATE_SEED, Sel.GATE_PATHS, a.workers, label)
                cols, bad = gate_entry(d, ov)
                return {**gate_reading(d), "seconds": time.time() - t0, "entry": cols, "entry_problems": bad,
                        "table_problems": (gate_policy_problems(d, XS[b]["plan"].id) if Sel.is_window_base(b)
                                           else (plan_gate_problems(d, ov, base_table(b), micro_of(b)) or []))}

            g = cached(f"gate|floor|{e['name']}", fresh)
            timing["gate|floor"] = {"paths": Sel.GATE_PATHS, "seconds": round(float(g["seconds"]), 1)}
            print(f"timing: the gate floor: {float(g['seconds']):.0f} s", flush=True)
            if Sel.is_window_base(b):           # D-639: the cell's (capped) table reached the gate floor's call
                settle([UJ._ident(e["name"], "", "the gate floor's call carries the cell's table on every row (its R "
                                  "capped where the cell takes a cap)", list(g.get("table_problems") or []))])
                if failures:
                    return refused()
            if own_table_kind(ov) is not None:  # D-653, D-659: the cell's own table reached the gate floor's call
                settle([UJ._ident(e["name"], "", "the gate floor's call carries the plan's table on every row",
                                  list(g.get("table_problems") or []))])
                if failures:
                    return refused()
            if entry_overrides(ov):             # D-630: the override reached the gate floor's call
                settle([UJ._ident(e["name"], "", "the gate floor's call carries each entry option's columns ("
                                  + ", ".join(entry_overrides(ov)) + ") at its declared value on every row",
                                  list(g.get("entry_problems") or []))])
                if failures:
                    return refused()
            fl = {**Sel.gate_floor(float(g["growth_at_bound"]), g06, resolves, not rp),
                  "growth_at_point": float(g["growth_at_point"]), "required_p90": float(g["required_p90"]),
                  "seed": Sel.GATE_SEED, "paths": Sel.GATE_PATHS, "entry": dict(g.get("entry") or {})}
        fl["problems"] = fl["problems"] + rp
        if is_chosen:
            floor = fl
            lines[Sel.LINES[2]] = bool(fl["holds"])
        # line (3)(iv), the coin guard: a coin design's only -- not applicable to a cell on P-14's trades, never run
        if not Sel.coin_design(b) or not (a.check or bool(fl["holds"])):
            continue
        dates = coin_dates(records[e["name"]], star_records)
        if a.check and not dates:               # a check on a few starts may hold none in the judged block
            dates = [str(r["start_date"]) for r in Sel.eligible(records[e["name"]], Sel.P_HORIZON)][:1]
        if W15 is None and r_star == P15 and P16 in XS:
            W15 = p15_walk(XS[P16])
        if Sel.is_joint_base(b):                # D-643: each sequence re-deals the cell and its opposite side on
            if "walk" not in JX:                #   P-16's walk and replays them through the joint engine
                t0 = time.time()
                JX["walk"] = UF.walk(JX)
                print(f"timing: P-16's walk for the joint coin line: {time.time() - t0:.0f} s", flush=True)
                settle([UJ._ident("joint", "", "the coin line's joint construction (the same walk, the coin table "
                                  "re-dealt for the cell and negated for its opposite side, aligned one for one, "
                                  "rc150_firm_split.inputs' construction on them) at the registered coin "
                                  f"{Sel.REGISTERED_COIN} rebuilds the cell: its trades and opposite side by content "
                                  "hash, each R's e and bound, the bound's shifts and the day capacity",
                                  UF.coin_problems(JX, JX["walk"]))])
                if failures:
                    return refused()
            cr = coin_guard(XS[b], e, r_star, star_records, dates, tuple(seeds), a.workers, cached, None,
                            job_of=lambda s, b=b: UF.coin_jobs(JX, JX["walk"], s, XS[b]["seats"], XS[b]["opens"],
                                                               deal=XS[b]["deal"]), refused=hypo)
        elif Sel.is_window_base(b):             # D-639: each sequence re-deals the cell's own window, with its cap
            Wb = walk_of(XS[b]["stop"])
            cr = coin_guard(XS[b], e, r_star, star_records, dates, tuple(seeds), a.workers, cached, None,
                            camp_of=lambda s, b=b, Wb=Wb: window_coin_campaign(XS[b], Wb, s))
        else:
            cr = coin_guard(XS[P16], e, r_star, star_records, dates, tuple(seeds), a.workers, cached, W15)
        ties = int(sum(int(r["ties_failing"]) for r in cr))
        settle([UJ._ident(e["name"], ARM, "in every coin sequence's replays the payouts' arrival days and cash and "
                          "the fees tie to the engine's totals", [f"{ties} runs"] if ties else [],
                          compared=len(cr), differing=ties)])
        if failures:
            return refused()
        cl = Sel.coin_line([r["value"] for r in cr], [r["reference_value"] for r in cr])
        if is_chosen:
            coin_rows, coin = cr, cl
            lines[Sel.LINES[3]] = bool(cl["holds"])
        secs = float(sum(float(r["seconds"]) for r in cr))
        timing["coin_guard"] = {"sequences": len(cr), "start_days": len(dates), "seconds": round(secs, 1)}
        print(f"timing: the coin guard: {len(cr)} sequences on {len(dates)} start days, {secs:.0f} s "
              f"({secs / max(len(cr), 1):.1f} s a sequence)", flush=True)

    # ---- the file
    for r in idents:
        r.pop("problems", None)
    seconds = time.time() - t_all
    counted = [c for c in fam["cells"] if Sel.counted(c) and c["name"] in records]

    def write(target: Path | None) -> tuple[int, dict[str, Any]]:
        counter = VariantCounter(path=(Path(target) if target is not None else rd) / "variants.jsonl")
        for c in counted:
            wb = Sel.base_of(c) if Sel.is_window_base(Sel.base_of(c)) else None
            jb = Sel.base_of(c) if Sel.is_joint_base(Sel.base_of(c)) else None
            counter.record(prereg_id=(family_id if jb is None else                     # D-644 (4): a hypothetical
                                      UF.variant_id_of(fam["decision"], fam["family"], jb)),   # cell under its own id
                           seed=U.CAMPAIGN_SEED, exploratory=True,
                           params=count_params(fam, c, None if wb is None else XS[wb]["facts"]),
                           label=f"{fam['decision']}'s lever family {fam['family']}: {c['name']}"
                                 + ("" if jb is None else f" ({Sel.base_row_label(jb)})"))
        count = Sel.program_count(counter.all(), family_id)
        labels = {c["name"]: Sel.base_row_label(Sel.base_of(c)) for c in fam["cells"]
                  if Sel.is_joint_base(Sel.base_of(c))}
        cell_notes = {name: Sel.HYPOTHETICAL_NOTE for name in hypo}
        for r in idents:                        # D-643: every row of a joint cell carries its label, identities too
            if r.get("config") in labels:
                r["label"] = labels[r["config"]]
                if r["config"] in cell_notes:
                    r["label_note"] = cell_notes[r["config"]]
        rows, v = tables(fam, J, r_star, best, cards, coin_rows, coin, floor, lines, count, chosen_base=chosen_base,
                         labels=labels or None, notes=cell_notes or None, refused=hypo)
        if hypo:                                # D-644 (4): no row of a hypothetical cell leaves without the label
            UF.hh.require_label([r for r in idents + rows if (r.get("cell") or r.get("config")) in hypo])
        res = pd.DataFrame(idents + rows)
        res.insert(1, "reading", Sel.READING)
        ref_files = [U1_FILE, SCOREBOARD]
        if P16 in bases:
            ref_files += ["rc_s150_all_gate_slices.csv", R.SPEC.screen_file]
        if P14 in bases:
            ref_files += [P14_GATE_FILE, P14_PATHS_FILE, defs[P14]["slices"][ARM][0], defs[P14]["starts"][0],
                          B.SCREEN, C.P13_RESULT]
        ref_files += sorted({window_spec(b, "screen").screen_file for b in win} - set(ref_files))
        if joint:
            ref_files += [f for f in (UF.ADDED_FILE, R.SPEC.screen_file) if f not in ref_files]
        params = {"decision": DECISION, "family": fam["family"], "family_decision": fam["decision"],
                  "family_id": family_id, "k": int(fam["k"]), "level": J["level"],
                  "declaration_sha256": decl["sha256"],
                  "cells": [{"name": c["name"], "base": Sel.base_of(c), "overrides": c["overrides"],
                             "rules": list(c.get("rules", ())), "equals_u1": c.get("equals_u1")}
                            for c in fam["cells"]],
                  "bases": {b: {"setup": f"U1's {b} configuration ({LABEL[b]})", "reference_cell": REFERENCES[b],
                                "coin_design": Sel.coin_design(b), "override_kinds": list(Sel.override_kinds(b)),
                                "refused_kinds": dict(Sel.BASE_REFUSED_KINDS[b])}
                            for b in bases if not Sel.is_window_base(b) and not Sel.is_joint_base(b)},
                  **({} if not joint else {"joint_bases": {
                      b: {"cell": jcell[b]["name"], "setup": Sel.joint_label(b) + " (D-643; D-593's conventions; "
                          "U1's p16_5+1 builder)", "seats": list(XS[b]["seats"]), "second_firm": "lucid",
                          "second_firm_opens": XS[b]["opens"] or "day 0", "deal": XS[b]["deal"],
                          "label": Sel.base_row_label(b), "eligible": not Sel.hypothetical(b),
                          "counted_under": UF.variant_id_of(fam["decision"], fam["family"], b),
                          "equals_u1": Sel.JOINT_EQUALS_U1.get(b), "added_lucid_row": UF.added_cell(b),
                          "waits_for": Sel.UPPER_BOUND_WAITS_FOR} for b in joint},
                      "hypothetical": {"cells": list(hypo), "label": Sel.HYPOTHETICAL_LABEL,
                                       "note": Sel.HYPOTHETICAL_NOTE,
                                       "refused_in": ["the choice", "the judgement", "the guards", "the rows to beat"],
                                       "written": "the scorecard at both arms and the deal's shares, section cell"}}),
                  **({} if not win else {"window_bases": {
                      b: {"cell": wcell[b]["name"], "setup": Sel.window_label(b) + " on its own trades, bounds and "
                          "capacity, P-14's protocol (D-639)", "pins": dict(WINDOW_PINS[b]),
                          "screen_file": window_spec(b, "screen").screen_file, "replayed": b in live,
                          "table": getattr(XS[b].get("plan"), "id", None), "facts": XS[b]["facts"]} for b in win}}),
                  **({} if not plan_facts else {"funded_plans": {
                      "decision": Sel.FUNDED_PLAN_DECISION,
                      "what": "the base's table with its funded phase (activation to the first payout) replaced by "
                              "one leaf; the evaluation's and the paid phase's leaves the base's; not re-solved; the "
                              "funded leg's edge and bound keys and the protocol's funded leg re-pointed to the "
                              "plan's R and dollars; payout requests are the engine's, not a leaf's",
                      "cells": plan_facts}}),
                  **({} if not resolve_facts else {"funded_resolves": {
                      "decision": Sel.FUNDED_RESOLVE_DECISION,
                      "what": "the base's table with, in its funded phase, every state whose balance is below the "
                              "account's starting balance decided by a bold leaf -- the cushion band's lower edge, "
                              "never less than one micro at the base's widest stop, at the cell's R, one trade a "
                              "session; every other state the base's; not re-solved; the edge and bound keys and the "
                              "protocol's funded leg the base's, unmoved (the fresh funded decision is unchanged)",
                      "under_water_identity_every": RESOLVE_IDENTITY_EVERY,
                      "cells": resolve_facts}}),
                  "chosen_base": chosen_base,
                  "arm": ARM, "r_star": r_star, "r_star_is_a_stand_in": bool(stand_in),
                  "rows_to_beat": {k: v_["config"] for k, v_ in best.items()},
                  "blocks": {"early": f"starts to the last start of {Sel.CHOICE_LAST_YEAR} less the reading's horizon",
                             "late": f"starts from the first session of {Sel.JUDGED_FIRST_YEAR} with the reading's "
                                     "horizon left"},
                  "p": f"months 1 to 3 ending above zero over three, on the starts with {Sel.P_HORIZON} sessions",
                  "bootstrap": {"seed": U.BOOT_SEED, "draws": U.BOOT_DRAWS, "block": Sel.BOOT_BLOCK,
                                "interval": "one-sided: the lower limit is the level's quantile"},
                  "tolerances": {"share": Sel.SHARE_TOLERANCE, "relative": Sel.RELATIVE_TOLERANCE,
                                 "blank": "a blank on either side fails the line",
                                 "zero_reference": "no relative tolerance"},
                  "coin_guard": {"sequences": [int(s) for s in seeds], "every": Sel.COIN_EVERY,
                                 "wins_needed": Sel.COIN_WINS_NEEDED, "registered_coin": Sel.REGISTERED_COIN,
                                 "starts": "every 21st of the judged block's common start dates",
                                 "applies": "a coin design's only: not applicable to a cell on base p14",
                                 "ran": coin_rows is not None},
                  "gate_floor": {"seed": Sel.GATE_SEED, "paths": Sel.GATE_PATHS, "row_to_beat": Sel.GATE_ROW_TO_BEAT,
                                 "registered_call": {
                                     P16: f"rc_screen.Runner's form at seed {S.SEED}, {S.N_PATHS} paths, against "
                                          f"{PS.SCREEN_FILE}'s {PS.CELL} row",
                                     P14: f"a3_brk30_cb20's gate campaign at seed {C.SEED}, {C.N_PATHS} paths, against "
                                          f"{P14_GATE_FILE}'s section {P14_GATE_SECTION} rows at 0 % and "
                                          f"{P14_PATHS_FILE}'s {P14_GATE_RUN} run path for path",
                                     **{b: f"rc_screen.Runner's form on the screen's own cell (no cap) at seed {S.SEED}, "
                                           f"{S.N_PATHS} paths, against {window_spec(b, 'screen').screen_file}'s "
                                           f"{window_cell_name(b)} row; then the cell's trades, bounds, capacity and "
                                           "(capped) table at the fresh seed" for b in win}},
                                 "ran": floor is not None and floor.get("seed") is not None},
                  "expensive_lines": "the gate floor and the coin guard run for the chosen cell only, each only while "
                                     "every line before it holds (the verdict is the first failing line)",
                  "seeds": {"bootstrap": U.BOOT_SEED, "campaign": U.CAMPAIGN_SEED, "coin": U.COIN_SEED,
                            "note": "a replay draws nothing"},
                  "references": {f: sha256_of(rd / f) for f in ref_files if (rd / f).is_file()},
                  "program_cells": count["program"], "program_by_family": count["by_family"], "timing": timing,
                  "workers": int(a.workers), "seconds": round(seconds, 1)}
        write_result(res, Sel.result_name(fam["family"]), script=SCRIPT, seed=U.BOOT_SEED, exploratory=True,
                     results_dir=target, variant_count=len(counted), parameters=params,
                     notes={"status": Sel.READING,
                            "variant_count_rule": f"one per cell, under {family_id}; the reference cell, the chosen "
                                                  "cell's point arm, coin replays and gate floor are readings of cells "
                                                  "already counted",
                            "selection": "D-621 (3): CARRIED only if every line holds; a carried cell is a new "
                                         "candidate for its own registered development test"},
                     description=f"EXPLORATORY (D-621, program U): the lever family {fam['family']} "
                                 f"({fam['decision']}) on " + " and ".join(f"{label_of(b)}'s" for b in bases)
                                 + " replay setup -- every cell on every start day, the "
                                 "scorecard, the choice on the early block and the judgement on the late one against "
                                 "R*, the reverse beside, the year rule, and for the chosen cell the coin guard and the "
                                 "gate floor; the identities first.")
        return len(res), v

    if a.check:
        with tempfile.TemporaryDirectory(prefix="u_family_check_") as td:
            n_rows, _ = write(Path(td))
            wrote = sorted(p.name for p in Path(td).iterdir())
        if a.check_overrides is not None:
            c0 = fam["cells"][0]
            print(f"check-overrides ran: {', '.join(c0['overrides'])} on base {Sel.base_of(c0)} -- the cell replayed "
                  f"on {len(chosen_starts)} start(s) at both arms, its gate call at {gate_paths} path(s)"
                  + (f" and its replays under {len(seeds)} coin sequence(s)" if Sel.coin_design(Sel.base_of(c0))
                     else "") + "; not counted, nothing of it printed or kept", flush=True)
        if joint_check:
            print(f"check-base ran: the joint base(s) {', '.join(joint_check)} -- each cell and the 5 + 0 twin "
                  f"replayed through the joint engine on {len(chosen_starts)} start(s) (the cell at both arms) and, "
                  f"for an unhedged base, its pooled gate call(s) at {gate_paths} path(s) a shift at the screen's seed "
                  f"and its replays under {len(seeds)} coin sequence(s); not counted, nothing of a cell printed or "
                  "kept but identity and timing lines", flush=True)
        if window_check:
            print(f"check-base ran: the window base(s) {', '.join(window_check)} -- each cell replayed on "
                  f"{len(chosen_starts)} start(s) at both arms, its gate call(s) at {gate_paths} path(s) at the "
                  f"screen's seed and its replays under {len(seeds)} coin sequence(s); not counted, nothing of a cell "
                  "printed or kept but identity, timing and fact lines", flush=True)
        print(f"every identity that ran holds; the pipeline ran on {len(chosen_starts)} start(s), {len(seeds)} coin "
              f"sequence(s) and {gate_paths} gate path(s) with the family {fam['family']!r} on base(s) "
              f"{', '.join(bases)} and wrote {wrote} "
              f"({n_rows} rows) to a temporary folder, since removed; nothing written to results/, no reading printed "
              f"(--check). {seconds:.0f} s")
        return 0
    n_rows, v = write(results_dir)
    print(f"written: {Sel.result_name(fam['family'])}.csv ({n_rows} rows); the family is {v['verdict']}"
          + (f" at line {v['first_failing']} ({v['first_failing_status']})" if v["first_failing"] else "")
          + f"; {seconds:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
