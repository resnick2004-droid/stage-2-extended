# firms/ — one directory per firm

Each firm the project models gets a directory created by copying `_TEMPLATE/`:

```
firms/<firm-slug>/
  RULES_LEDGER.md   # human-readable record: one row per rule, with the exact quote's source
  rules.yaml        # machine-readable copy; propfirms/spec.py loads THIS, and raises on
                    # any rule whose status is not `verified`
```

The two files are written **together** by the rules-verifier agent (`/verify-rule`) and
must never diverge. `tests/` checks every `rules.yaml` parses and respects the schema.

## Status vocabulary

| status | meaning | may code use it? |
|---|---|---|
| `verified` | read on the **firm's official** site or help centre, with page/article id, URL, date read and the exact quoted text recorded | yes |
| `carried_reverify` | carried from another repository's verified ledger (e.g. Stage 2's Topstep ledger) without being re-read here. A copy is not a reading | **no** |
| `unverified_human_input_required` | needed, never verified anywhere | **no** |
| `third_party` | sourced from a non-official page. **Never sufficient**; recorded so the question is not lost | **no** |

## What official means

The firm's own domain(s) and help centre, nothing else. A prop-firm review site, a Reddit
thread, a YouTube summary, an aggregator blog or a cached copy on another domain is a
**lead**, not a source. Stage one's cautionary case: third-party guides said the Topstep
consistency rule was 50 %; the official page said **55 %** (`vendor/propsim/README.md`).

## Existing directories

- `_TEMPLATE/` — the blank pair; copy it to start a firm (T2).
- `topstep/` — the reference firm. Its real, verified ledger lives in the Stage 2
  repository; the copy here is a pointer plus the engine constants, all `carried_reverify`.
  Topstep is not re-researched here (D-02).
