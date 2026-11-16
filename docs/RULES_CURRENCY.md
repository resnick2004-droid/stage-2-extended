# Rules currency -- firm rules verified or re-verified in this repository

The human-readable table behind [`config/rules_extended.yaml`](../config/rules_extended.yaml): one row per entry there,
keyed the same, written together with it by the **rules-verifier** agent (`/verify-rule <rule>`) and never apart.
Stage 2's verified ledger -- `vendor/stage2/RULES_LEDGER.md` and `vendor/stage2/config/rules.yaml`, read on official
pages up to 2026-11-14 -- is vendored read-only (E-002) and is the source of every rule this repository loads until a
row here, under its decision row, says otherwise (CLAUDE.md, "Firm rules").

**What may be used.** A rule is usable only if it is `verified` in Stage 2's ledger, or `verified` here with its
decision row in `DECISIONS.md`. A `changed` row is a verified reading that differs from Stage 2's value: the vendored
engine still carries the old one, and anything resting on the rule is flagged until the lead's row decides. An
`unverified` row is never used.

**Sources.** Official pages only: Topstep's `help.topstep.com` and `topstep.com`; another firm, its own official pages,
whose domains are listed in the yaml's `meta.official_domains` before the first read. Never a third-party guide,
review site, forum, video or cached copy. The verbatim quote is in the yaml's `quote`; agreement with Stage 2's reading
is not evidence about today.

| key | firm | value | status | article id | url | date read | verified by | Stage 2 key | Stage 2 value | row |
|---|---|---|---|---|---|---|---|---|---|---|
