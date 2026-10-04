# Renewal Radar — final dashboard (card UI + updated dataset)

This is the card-based, visual redesign running on your updated data: the 40-contract
demonstration set, the extended `logic.js` (explicit election dates/windows, next-term
notice anchors), and the full `contracts/` PDF set.

## Run on your Mac

Unzip this archive. Open Terminal, type `cd ` (with a space), drag the unzipped
`Renewal_Radar_Final_UI` folder into Terminal, and press Return. Then run:

```bash
python3 -m http.server 8000
```

Keep Terminal running and open **http://localhost:8000** in your browser (not
`index.html` directly — the page loads `data.json` with `fetch`, which browsers block
for files opened straight from disk). Press Control+C in Terminal to stop.

## What's in this version

- **Card-first dashboard**, colour-coded by urgency, instead of a dense table — see each
  contract at a glance rather than scanning rows.
- **A plain-language headline** ("X contracts need your attention") and a 12-month
  timeline of upcoming deadlines, instead of KPI tiles and a donut chart.
- **A provenance banner on the dashboard itself**, not just in `DATASET.md` — this
  40-contract set was assembled after seeing evaluation results and is a demonstration
  set, not a blind held-out test. The banner and DATASET.md both say so, so anyone
  clicking through it (including a grader) sees that distinction immediately rather than
  having to find it in a separate file.
- Kept: search, the "checked vs AI results" toggle, the as-of date override, CSV export,
  and the terms/evidence detail drawer with a link to the source PDF.

## Files

- `index.html`, `styles.css`, `app.js` — the redesigned dashboard.
- `logic.js` — unchanged from what you provided: deterministic date parsing, calendar-
  month subtraction, explicit election dates/windows, next-term notice anchors, and
  review/alert priority.
- `data.json` — unchanged from what you provided: the 40 selected contracts.
- `contracts/` — unchanged: the 40 linked PDFs.
- `DATASET.md` — unchanged: full composition and interpretation of this selected set.
- `Renewal_Radar_Final_Dataset.zip` — unchanged: the downloadable data bundle (PDFs,
  prediction CSVs, HTML sources, references, frozen prompt).

## Scope

This UI displays saved extraction results. It does not upload contracts, call an LLM,
send reminders, or renew/cancel anything. Checked results and AI results are shown
separately. Review edits last only for the current browser session. For the actual
accuracy numbers to report on your project, use the real 34-contract development run
and the untouched 40-contract held-out run — not this demonstration set.
