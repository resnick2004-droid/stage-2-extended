---
description: Verify one firm rule on the firm's official help pages and record it in this repository's rules record
argument-hint: <rule key, e.g. max_active_funded_accounts, or a new firm's rule>
allowed-tools: Read, Edit, Write, Grep, Glob, WebFetch, WebSearch, Agent
---

Verify this rule: **$ARGUMENTS**

1. Find it in Stage 2's vendored ledger (`vendor/stage2/config/rules.yaml`, `vendor/stage2/RULES_LEDGER.md`, read-only)
   and in this repository's record (`config/rules_extended.yaml`, `docs/RULES_CURRENCY.md`). If the name matches no
   key in either and is not clearly a new rule (another firm's contract), list the nearest keys and ask which is meant
   rather than guessing -- verifying the wrong rule and marking it done is worse than verifying nothing.
2. Invoke the **rules-verifier** agent on that one rule.
3. Report its result: the value, the article id and URL, the date read, the status it set (verified / changed /
   unverified), the exact quoted text from the official page, that `config/rules_extended.yaml` and
   `docs/RULES_CURRENCY.md` were both written, and its proposed decision row.
4. If the reading **differs** from Stage 2's value (`changed`), say so prominently and say what it changes: the vendored
   engine still loads Stage 2's value, so every reading resting on the rule is flagged until the lead's row decides,
   and a rule that moves fees or payouts moves S3c and P directly.
5. If the outcome is `unverified` -- the official page does not state the rule, or states it ambiguously -- that is a
   successful outcome, not a failure. Report what was looked at and what it did not say. Never let a rule be marked
   verified on third-party evidence.

The lead appends the proposed row with `/decide`; until then the reading is recorded but not used. No code of this
repository loads a rule that is not verified in Stage 2's ledger or, with its row, in this repository's record.
