# Module guide

| File/module | Purpose and limits |
|---|---|
| code/run_extract.py | Frozen model/prompt/schema API payload, catalog/hash checks, certificate handling, hidden local key input, sequential retries and resumable new CSV/JSONL results. Never reads reference labels. |
| code/normalize_original.py | Historical conservative parser retained for traceability; extracts explicit endpoints/anniversary wording and primary numeric notices. |
| code/normalize.py | Current headless wrapper supporting explicit election dates/windows and next-term-start anchors. Reads only model prose. Can abstain; is not an automatic legal interpreter. |
| code/date_engine.py | Pure deterministic days/months arithmetic, window checks and review-first alert priority; command-line CSV input/output. |
| code/check_package.py | File/catalog integrity and confirmation of the 40 replacement PDFs; offline only. |
| code/run_evaluation.py | Reaggregates archived outputs/labels and manual judgments, executes regression checks, saves descriptive summaries. |
| evaluation/historical_original40/date_rules_heldout.py | Original date implementation preserved with its original input records. |
| evaluation/historical_original40/test_alerts.py | Thirteen original boundary, leap-month, review-priority and invalid-input checks. |

Standard-library Python is enough for offline use. Certifi is optional for live HTTPS calls. Pre-extracted text is supplied, so rerunning extraction needs no PDF/OCR package. New scanned contracts require a separate text/OCR preparation step and are outside this frozen-catalog runner.

## Final dashboard

`dashboard/index.html` defines the card UI; `styles.css` controls responsive styling; `app.js` handles filters, dates, details, source links and CSV export; `logic.js` implements browser date arithmetic. `data.json` contains the final selected 40 with separate checked/model values. `contracts/` contains the linked PDFs. The supplied design was preserved, with PDF links enabled for original contracts and review copy corrected to include known dates with unresolved rules.
