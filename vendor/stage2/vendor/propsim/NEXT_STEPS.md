# Finishing this repository

## Charter (revised 2026-09-21, D-38)
- **Question:** What does the Topstep 50K contract do to a trading process, which uses of it are permitted, and how much is a genuine edge worth inside those limits?
- **Finding that reshaped it:** the zero-edge campaign is prohibited (account stacking; "not a viable strategy") — D-34. The structural EV is the prohibited mechanism.
- **In scope:** contract engine; rule reconciliation; optimality results (closed); conduct-constrained geometry (D-36); value-of-edge table for admissible profiles; handoff spec for the research stage; one final rebuild of the document and deck.
- **Out of scope:** any zero-edge or fail-and-repurchase campaign model (retired); ranking by detectability (D-35); strategy research itself; measuring s or costs; live pilot; operations. Ideas go to `PARKING_LOT.md`.
- **Exit criterion:** documented no-go at zero edge + conduct constraints + value-of-edge table + a handoff spec telling the research stage what edge a strategy must demonstrate and how to evaluate a candidate in the engine.

## Tasks (revised under D-41: this repository and conversation only)

| # | Task | Output | Status |
|---|---|---|---|
| T1 | Conduct terms vs ridge candidates | no-go at e = 0; constraints D-36 | **closed** (D-34, D-36) |
| T1b | Verify the Responsible Trading Program claims | verified | **closed** (D-43) |
| T2 | Rules: propsim vs official text (R-1 lock, R-2 net-positive, R-3 $125 minimum, R-7 21-day billing, R-9 day counting) | all consistent | **closed** (D-41) |
| T3 | R-9 test in propsim | golden test | **closed** |
| T4 | Validation: internal only — ceilings, exact 16/49, DP supremum vs MC (D-40), identities, 32 tests | validated engine | **closed** (D-41) |
| T5 | **Value-of-edge table** for the D-36-admissible profiles (Combine: 2:1 $750, 1.5:1 $1,000 and other R > 1 members at ≤ 50 % of the drawdown; XFA: static profiles, no single deciding position), one account at a time, e = 0 to 0.20: P(pass), EV per attempt, days to pass, days to first payout, payouts per XFA, EV per month of one account; plus the edge at which the choice between admissible profiles changes | table + script + CSV | **closed** (D-44–D-46; `edge/T5_RESULTS.md`) |
| T6 | `HANDOFF.md` for the research stage: definition of a demonstrated edge (out of sample, after realistic costs and fills — not SIM-favourable stop fills — with a confidence interval excluding 0); how a candidate strategy is expressed as (e, s, trade distribution) and run through the engine; the T5 edge levels that make it worthwhile; the D-36 constraints | handoff spec | **closed** (`HANDOFF.md`, D-47) |
| T7 | Final rebuild of document and deck: apply C-01 to C-14 (with C-14 as the headline reframing), add T5, remove the zero-edge campaign framing; visual QA of every page and slide | deliverables | **in progress** — document done and page-checked; deck built, checked to slide 12 of 38; see deliverables/BUILD.md (D-48) |
| T8 | Close: README status set to CLOSED with a five-sentence conclusion; zip built; its SHA-256 recorded in `CLOSED.md` | closed repository | last |

## Closing checklist (D-42) — the repository is closed when every line is true

- [ ] Test suite passes (`python -m pytest test_propsim.py -q`), count recorded
- [ ] Every task above is closed, or moved to `PARKING_LOT.md` with a reason
- [ ] `PENDING_DELIVERABLE_CORRECTIONS.md` has an empty "Queued" table (every item applied or withdrawn)
- [ ] Every number in the document and deck traces to a result file produced by a script listed in the README (checked by script)
- [ ] `HANDOFF.md` exists and states the research stage's target in numbers
- [ ] README opens with status CLOSED and the final conclusions
- [ ] `CLOSED.md` records the date, test count, and the zip's SHA-256
