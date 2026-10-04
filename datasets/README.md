# Data explainer

## Primary replacement dataset: final40

The final set has 40 PDFs, replacing the original 40 as the main project input. Composition: 15 originals (source IDs 6, 7, 11, 12, 14, 15, 17, 21, 29, 30, 31, 35, 38, 39, 40), previous additions E01–E10 and recent additions N01–N15. Catalog IDs 1–40 identify extraction order; `source_contract_id` preserves the earlier identity. The retained originals comprise the 14 contracts with confirmed/provisional dates and Kitov as a redacted/missing-date example. Final selection happened after evaluation; do not call it an untouched held-out set.

`catalog.json` lists every PDF, extracted text, page count and SHA-256 hash. The newer 25 PDFs are text reading copies of downloaded public exhibits. Their exact original HTML and URLs are enclosed in `sources/` and the catalog; PDF layout, images and original pagination differ. Text files have reading-copy page markers. The selected originals retain their original PDF layout. CUAD/SEC document identifiers remain in filenames. CUAD provenance comes from the original proposal; no private company data were used.

## Other evidence

`development34/` contains the actual 34 development inputs. The proposal planned 138 development contracts, but that planned count was not executed. Historical original40 results and references remain in results/evaluation; the 25 original PDFs excluded from the replacement set are deliberately not included. Consequently, full independent source re-adjudication of those excluded historical cases requires the earlier original dataset. Archived score aggregation and date regression checks remain reproducible from recorded labels/results.

The final40 model CSV is a selection of unchanged rows from three runs, not a newly executed 40-document API run. Checked reference inputs and model-normalized snapshots are separate. Some endpoints are provisional; human-review flags remain. Initial/revised expiry does not establish current active term, actual notice delivery or renewal eligibility. Amendments may reference unenclosed base agreements. Fund-service templates recur in clearer samples.

No confidence score is calibrated. Abstention/review is based on missing, ambiguous and conflicting facts/rules, despite the proposal's earlier confidence-threshold plan.

Catalog IDs are consecutive extraction order. Structured checked/model snapshots retain earlier source IDs; regenerated normalized CSVs use row-order IDs. Use the exact filename for joins across these artifacts.
