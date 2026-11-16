# Family pre-registration — what a signal-atlas family adds to `prereg/TEMPLATE.md` (R5, D-460)

> A family is pre-registered once, not model by model (the handoff's §7 item 3). Copy `prereg/TEMPLATE.md` as usual
> (`/prereg <title>`), fill every field there, and add the sections below. The gatekeeper reads both. Nothing in a
> family's registration may be chosen after its development data is read; what is, is exploratory and reported apart.

## F1. The family's declaration

- **The atlas config** (`config/atlas_<family>.yaml`): its sha256 at registration, and the commit it was fixed in —
  before the family read any bar.
- **The grid**: the patterns (each with its mechanical definition in `propedge/outcomes/atlas_core.py` and its test on
  synthetic bars), the side rules, the entry delay, the stop map, the plan. Every cell is one trial: `k` in the table is
  the number of cells.
- **The runner and its data**: the local walk on the operator's Databento bars (D-458, D-460) or a QuantConnect kit;
  the identity of the runner against QuantConnect's capture (`results/atlas_identity_<family>.csv`) cited with its
  measured differences.

## F2. The selection rule, fixed now

- The screen's ranking (growth on the required bankroll at each R's bound, the screen's path count) and which cell goes
  to the verdict (the top one; every cell reported).
- The anchored yearly walk-forward of the selection (D-382 (A)): the folds, and the rule a fold's pick must meet.
- The development verdict: the gate at 0.05/N with the resolution lines (`docs/SUCCESS_CRITERIA.md` §2-§3).
- **Beat FV3-C's row or stop** (D-455): the cell's development growth at the bound against FV3-C's development
  baseline on the scoreboard; the FLAG levels of §5 beside.

## F3. The confirmation, declared before any development read

- **The window**: the market's `confirmation` window in `config/windows.yaml` (D-459), or several markets' windows
  pooled for a family defined in market-relative units; added to `registered_reads` under this registration.
- **Its length**: the 21-session block count of the window beside development's (§3 of the criteria); a window too
  short for the bound to read anything but its own width is not registered.
- **The Combine's headroom** over its target against the window's bound, with the numbers (D-451 (3)): how many of
  the plan's Combine passes survive the gate's shift at that window's bound width.
- **The window's count** on its market (D-107: at most three registered confirmation tests per market).

## F4. What a result leads to

- PASS (development) → the confirmation registered here, read once; PASS (confirmation) → the shadow-period queue
  behind FV3-C, no levers (D-419).
- CONTINUE → the confirmation decides it (D-189).
- FAIL → the failure protocol's diagnosis; the family closes.
- A family takes about a week (the handoff's §7 item 5); the ledger's N counts it whatever it says.
