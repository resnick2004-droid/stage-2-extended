# Building the document and the deck

Status: **T7 in progress** (see ../NEXT_STEPS.md). `report.docx` is rebuilt and fully page-checked; `deck.pptx` is rebuilt
and valid, visually checked through slide 12 of 38. Old delivered versions are in `previous_version/` for reference only.

## Prerequisites
- Node.js with `npm install docx pptxgenjs`
- Python 3 with `numpy pandas matplotlib tabulate` (and the engine one folder up)
- LibreOffice (`soffice`) — used only to paginate the document so the table of contents gets real page numbers.
  Set `SOFFICE_PY` to your `soffice` binary (or a Python wrapper ending in `.py`) if it is not on PATH.

## Build order (run inside `deliverables/`)
1. Figures: `python make_figs.py` · `python deck_figs.py` · `python edge_figs.py` (all read the result CSVs one folder up)
2. Document: `node build_report.js` → writes `report_raw.docx`, `headings.json`, `refs.json`
3. `python inject_toc.py` → resolves `{{E:key}}` / `{{T:key}}` / `{{F:key}}` reference tokens, writes the populated,
   hyperlinked TOC, iterates until page numbers are stable → `report.docx`. Fails on any unresolved token.
4. Deck: `node build_deck.js` → `deck.pptx`, then `python resolve_deck_tokens.py` (uses the document's `refs.json`, so
   equation / table / figure numbers are shared). Always build the document first.

## How the sources are organised
- `data.js` — the single source of numbers: every value is read from a result CSV; nothing is typed in.
  Helpers: `N.ce` (exact Combine chain by profile and edge), `N.bestPair`, `N.bestBuf`, `N.evBestBuffer`, `N.evExact`
  (EV with exact 16/49), `N.hz` (horizon), `N.dllRow`, `N.sup` (supremum), `N.ss` (sample sizes).
- `report_p1.js` front matter, Parts I–II · `report_p2.js` Parts III–V (equation registry `E`) · `report_p3.js` Part VI ·
  `report_p4.js` Parts VII–XI and appendices (Appendix D reads `../test_propsim.py`; Appendix E reads `../DECISIONS.md`).
- `lib.js` — helpers. `eq`, `table`, `figure` accept `{ key }`; cite them in text as `{{E:key}}`, `{{T:key}}`, `{{F:key}}`.
- `build_deck.js` — slides; cite document numbers with the same tokens.

## Rule for any edit
Never type a result number into a source file: add the result file to `data.js` and compute it. The one stale number found
so far (slide 12's z-value from an older run) came from exactly that.

## Remaining T7 work (deck)
- Slides 2 and 6: cards half empty — shorten the cards / raise text to about 15 pt.
- Visually check slides 13–38 (12 of them are new: proven optimum, methods, Finding 7, zero-edge results, conduct ×2,
  value of edge ×5, sensitivity, limitations, interpretation, conclusions, criterion, appendices).
- Traceability check (closing checklist): a script that recomputes each headline number from its CSV and confirms it
  appears in both `report.docx` and `deck.pptx`.
