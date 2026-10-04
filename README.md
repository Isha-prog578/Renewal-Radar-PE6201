# Renewal Radar — final submission

Isha Kirti Ghia · NTU PE6201 · packaged 3 October 2026

This package includes your final uploaded card dashboard in `dashboard/`. The main input dataset is the replacement set of 40 contracts: 15 retained original contracts, 10 earlier clearer-date additions and 15 recent additions. Earlier predictions and evaluations are retained as historical evidence, not relabelled as an untouched final hold-out.

## Submission contents

Read `report/Renewal_Radar_Final_Report.pdf` for the final analysis. The published UI is https://renewal-radar-isha.ghiaisha.chatgpt.site and its complete offline source is in `dashboard/`. The code, data and evaluation files are all included. Add your recorded demo video to `video/` before submission. No demo guide is included.

## Start here on your Mac

Unzip the archive. Open Terminal, type `cd ` (include the space), drag the unzipped `Renewal_Radar_Final_Submission` folder into Terminal and press Return. Python 3.11 or newer is recommended.

Run offline, without an API key or paid calls:

```bash
python3 code/check_package.py
python3 code/run_extract.py --check
python3 code/run_evaluation.py
python3 code/date_engine.py datasets/final40/reference_inputs.csv results/reproduced/checked_deadlines.csv --as-of 2026-10-02
python3 code/normalize.py results/final40_saved_predictions.csv results/reproduced/model_inputs.csv
python3 code/date_engine.py results/reproduced/model_inputs.csv results/reproduced/model_deadlines.csv --as-of 2026-10-02
```

The evaluation prints scores and saves `results/reproduced/evaluation_summary.json`. Checked deadlines are based on source-reviewed inputs. Model deadlines use a conservative post-evaluation parser of unchanged model output; missing or ambiguous inputs route to review. They are separate outputs and must not be combined as model-only accuracy.

## Run the final dashboard

From the package folder, run:

```bash
python3 -m http.server 8000 --directory dashboard
```

Open http://localhost:8000 and keep Terminal running. No API key is needed. The dashboard displays saved results; it does not run extraction or send reminders. The Python commands above reproduce code/data/evaluations separately.

## Optional live extraction (paid API calls)

Saved model results are already included. You do not need to rerun the LLM to inspect or evaluate the project. To make a fresh extraction of the replacement 40:

```bash
python3 -m pip install -r requirements.txt
python3 code/run_extract.py --one
python3 code/run_extract.py --all
```

At the prompt, paste your OpenRouter key and press Return. Input is hidden. Do not put a key in code, the submission or chat. Calls use your account credits. The first command extracts one unprocessed contract; `--all` resumes and skips completed JSONL rows. Fresh outputs go to `results/live_final40/predictions.csv` and `.jsonl`, leaving saved historical outputs intact. Certifi is used automatically when installed; HTTPS verification remains enabled. If needed, the previous Mac workaround is `export SSL_CERT_FILE="$(python3 -m certifi)"`.

An optional alternate catalog can be supplied, for example `--catalog datasets/development34/catalog.json --output-dir results/live_development34`. This runs the same frozen v6 request; it is a fresh run, not the historical development record.

The runner reads only catalogued page-numbered text and the extraction prompt. Reference labels are never sent to the model. The supplied PDFs are retained for source checking; the API receives their extracted text rather than PDF binaries.

## Main folders

- `code/`: extraction, model-output normalization, date arithmetic, package checks and evaluation aggregation.
- `prompts/`: frozen v6 prompt.
- `datasets/final40/`: exactly the 40 replacement PDFs, text, original HTML for newer exhibits, catalog and separate checked/model input snapshots.
- `datasets/development34/`: separate development evidence used before the original hold-out run.
- `results/`: selected saved predictions and clearly separated historical runs; reproduced offline outputs.
- `evaluation/`: source references, manual adjudications, historical checks and existing review workbooks.
- `dashboard/`: final card UI, saved data and source PDFs.
- `report/`: final report PDF and editable Word.
- `video/`: destination for the required recording, not yet supplied.
- `docs/`: product architecture, module guide, targets/results, proposal and professor feedback.

Read `datasets/README.md` and `evaluation/README.md` before interpreting percentages. The final report is included in `report/` as PDF and editable Word. The recorded face-and-screen demo video must be added to `video/` before submission; it has not been supplied. The final card dashboard is included separately from the extraction and evaluation code.
