# Renewal Radar final selected dataset

40 contracts: 15 retained from the original held-out set, 10 from the first clear-date sample, and 15 from the second clear-date sample. This is the final project/dashboard dataset, assembled after the earlier evaluations. It is not the original randomly held-out set and must not be described as an untouched hold-out.

The original 40-contract evaluation remains separate and unchanged. The newer 25 were purposively selected for clearer visible dates; recurring fund-service templates limit representativeness. Retained originals include confirmed and provisional dates plus a redacted example. Human review flags are preserved where warranted.

`pdfs/` contains exactly the 40 selected inputs. The 25 newer PDFs are text reading copies of public HTML exhibits; originals are in `sources/`. `predictions/` contains unchanged model CSV rows for the selected documents, separated by run. `reference/` contains checked inputs, separate from model output. `contracts.json` combines the rows for the static dashboard. `prompt_v6.txt` is the frozen extraction prompt. `selection_manifest.json` documents composition and selection timing.

The dashboard compares deadlines using deterministic code; it does not run new API extractions. Explicit election dates/windows and notice anchors at next-term commencement are supported. The AI lane preserves errors and abstentions. The checked lane includes manual source corrections, with notes. A stated initial or revised expiry does not establish the current active term or actual eligibility. No new 40-contract API run has been performed for this assembled set; metrics from separate samples must not be relabelled as a newly evaluated hold-out.

Retained original IDs: 6, 7, 11, 12, 14, 15, 17, 21, 29, 30, 31, 35, 38, 39, 40
