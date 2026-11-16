# Corrections queued for the next document / deck rebuild

The deliverables in `deliverables/` are **frozen** (D-22) at the 2026-09-21 build. Nothing below has been applied to them.
Apply all items in one rebuild once results are verified; then move each item to "Applied" with the build date.

## Queued

> **In the rebuilt sources (2026-09-21, D-48):** C-01 to C-10 and C-13 to C-15 are applied in `deliverables/report_p*.js` and `build_deck.js`; C-11 is applied as withdrawn (only the payout-trace timeline kept); C-12 was withdrawn earlier. Move each row to "Applied" once the deck's visual check (slides 13–38) is complete.

| # | Source | Where | Correction |
|---|---|---|---|
| C-01 | D-18 | Doc §35 robustness bullet "Horizon does not bind"; deck slide 24 | Horizon does not bind **without** frictions; with the net-positive rule it binds at R ≥ 3 (P(closed) 0.981 / 0.946 at 250 d) |
| C-02 | D-18, D-19 | Doc Finding 7 card, Table 12 note, Exec Summary item 5, Conclusion 5; deck slides 20, 22, 27 | Replace "5:1 adds nothing over 3:1 once frictions are charged" with: at a long horizon 5:1 nets ≈ $1,446 vs 3:1 ≈ $1,316; frictions cost time, not money; choice deferred to the campaign model |
| C-03 | D-10, D-19 | Doc §39 decision rule; deck slide 28 | Third branch (s ≥ 3) pending the campaign model; state it as provisional |
| C-04 | D-16 | Doc Exec Summary, Table 3, Finding 7, Conclusion 6; deck slides 5, 20, 27 | Net-positive rule: "missing from A0's field list and propsim's earlier copy; already enforced by E1" — not "absent from the project" |
| C-05 | D-15 | Doc new subsection in Part IV (after §19) + Appendix C equation; Finding 6 card; deck slide 12 or new slide | Add the supremum result: 0.327131 over all fair strategies (concave-envelope DP), 16/49 is 0.06 pp below; two-day bound derivation; DLL leaves it unchanged. Upgrade "no tested policy beats it" to "no policy can beat it by more than 0.06 pp" |
| C-06 | audit | Doc Finding 2 headline, Table 8 text; deck slide 15 title | Top static cells ($197 / $196 / $187) are not separable at 2 SE: present as a ridge (R × $risk ≈ $1,500), not a winner |
| C-07 | audit | Doc §21 worked example, Table 14, Exec Summary; deck slide 22 | Use exact 16/49 in EV per attempt: 3:1 → $346 (not $343); recompute the other EV rows the same way and state it |
| C-08 | D-21 | Doc §37, Table 16 (firm discretion row), A9; deck slides 6, 25, 26, 28 | Prohibited Conduct / Prohibited Trading Strategies apply to the Combine profile too, not only the funded all-in |
| C-09 | D-17, D-30 | Doc Part II scope (DLL excluded) → new sensitivity subsection; deck slide 24 | DLL result: official $1,000 DLL, doubled cap $4,000; all-in identity holds; gain ≈ $0 / $4 / $49 per XFA at 2:1 / 3:1 / 5:1; limited-time offer |
| C-10 | D-20, D-31 | Doc Table 3 (number of accounts, payout fee, subscription rows); deck slide 5 | Combines unlimited (official); ≤ 5 XFAs with passes held in queue; $30 fee only for ACH/wire; billing modelled as 21 trading days, official text "every 30 days" cited |
| C-13 | D-28 | Doc Finding 2 / Part VIII; deck slides 15, 26 | Present conduct exposure as a selection criterion along the ridge with each profile's largest single-position risk, not as a property of one profile |
| C-14 | D-34–D-38 | Doc: Executive Summary, new conduct section, Part VIII–IX, decision rule §39; deck: title status line, slides 2, 22, 26–28 | **Headline correction:** the zero-edge campaign is prohibited (account stacking, official 10305426 / 10296582). Reframe the study as what the contract does and what a genuine edge is worth within the terms; present D-36 constraints and the value-of-edge table. The "five results" and "make money" framing must not survive the rebuild |
| C-15 | D-43–D-47 | Doc: new Part (value of a demonstrated edge) + handoff summary; deck: 3–4 new slides | Add T5 (pre-registered table, validation V1–V3, edge share, churn), the payout-buffer finding (exploratory, labelled), the sample-size table and the research-stage criterion; RTP verified |
| C-11 | bankroll/ | — | **Withdrawn in substance** (D-34): the fee-bankroll ruin model describes the prohibited campaign. Keep only the payout-trace timeline (valid for any funded account) |

## Withdrawn

| # | Date | Item | Reason |
|---|---|---|---|
| C-12 | 2026-09-21 | Funded profile as a 75 %-capped all-in | D-24 retired (D-27); nothing to change in the deliverables |

## Applied

| # | Build date | Item |
|---|---|---|
| A-01 | 2026-09-21 | Deck equation numbers 21–23 aligned with the document |
| A-02 | 2026-09-21 | Doc figure references (§19 → Figure 4; experiment register → Figure 9) |
| A-03 | 2026-09-21 | Slide 18 / doc §18: harvest recovers the balance *in expectation*, first payout ≈ $1,800 by ≈ day 8, rest over ≈ 6 weeks |
| A-04 | 2026-09-21 | Deck image alt text (was file paths); Markov diagram redrawn; Markov equation no longer wraps |
