# Evaluation explainer

## Definitions

Score fields separately. Stated expiry is correct when the relevant supplied initial/revised term-end appears correctly in `initial_term`; this does not validate every start-date or duration assertion. Category uses exact canonical label matching. A primary notice match requires the correct amount/unit or explicit date/window, giving/receiving actor and renewal-related purpose. Manual source adjudications are stored separately; automatic aggregation does not prove semantic correctness. Secondary notices and all explanation text are outside that primary-notice score.

A usable fixed deadline also needs the correct anchor. Counting before the NEXT term begins differs from counting before the old term ends. Calendar months differ from a fixed day count. Review status and known-date calculability are separate. Do not infer current renewed terms from historical dates.

## Historical original40

Frozen renewal-category agreement is 38/40. Binary auto-renewal agreement is 34/34 eligible cases, excluding five Conditional and one Unclear reference. Always Yes is 21/34; recorded retrospective keyword baseline is 30/34. These are not complete-contract accuracy. The keyword rule and recorded decisions are enclosed; excluded historical source PDFs are not, so aggregation is reproduced from archived decisions rather than rescanning every source.

Exact cutoff comparison is 4/4 eligible confirmed reference cutoffs, not 40/40. Nineteen settled numeric notice amount/unit matches were descriptive selected cases, not an overall notice accuracy estimate. Raw notice-type agreement of 34/40 in provisional scoring is limited by reference omissions and scope disputes; do not use it as a validated primary-notice score. Frozen model review flags were 27/40; normalized model queue and reference review can differ.

Token-priced cost estimate: input 699,981 and output 32,524, using the recorded 1 October 2026 rates of US$3/US$15 per million. About US$2.59 for that original40 pass, US$0.065/contract or US$9.70 for 150 similar documents. These are archived estimates, not a current price quote or billing total.

## Additional10 and additional15

Both were selected for visible expiry/notice wording before their model runs, but are purposive clearer diagnostics, not representative random tests. Additional10: expiry/category/stated-term notice amount-unit 10/10, model review 2/10. Source review adds VerifyMe because later quarterly notice scope is not established. Additional15: expiry 15/15, category 14/15, manually adjudicated primary notice 15/15 and model review 5/15. See Additional15_Source_Review.md for wrong anchor in Pacific Select, contradictory Enova arithmetic, Applied Optoelectronics category error, TCG missed calculability and SS&C review inconsistency.

## Final40 and reproduction

The assembled final40 uses previous outputs after seeing their results. Any combined percentage is descriptive selection performance, not new held-out accuracy. `run_evaluation.py` clearly labels it that way. Source-corrected inputs must not be counted as raw model success.

Run `python3 code/run_evaluation.py`. It reaggregates frozen category/binary outcomes, recorded baseline decisions, manual primary-notice adjudications and four eligible historical cutoffs. It executes the original 13 alert checks and 40 current checked-input arithmetic regressions. These regression checks test calendar behavior from supplied structured inputs, not model extraction accuracy.

Earlier reference gaps and adjudication workbooks are preserved. No reference answer is sent to the live extraction runner. Reference labels were manually prepared/refined; independence and subjective scope decisions are limitations, not hidden sources of truth.
