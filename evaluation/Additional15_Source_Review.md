# Renewal Radar — review of the 15 additional contracts

Reviewed 2 October 2026. Input: `more_predictions.csv`, 15 completed rows, frozen v6 prompt. Compared with the pre-run answer key and supplied exhibit text. Original predictions remain unchanged. This is a purposively clearer diagnostic sample, separate from the original 40 and earlier additional 10.

## Results and scoring scope

| Measure | Result | Meaning |
|---|---:|---|
| Stated initial/revised expiry present and correct in `initial_term` | 15/15 (100%) | Every row contains the relevant expiry. This is not a score for every start date, duration or current active term. |
| Exact canonical renewal category | 14/15 (93.3%) | Applied Optoelectronics is By agreement/amendment, not Option. |
| Primary renewal notice amount/unit or explicit date/window, actor and purpose captured in `notice_period` | 15/15 (100%) | Limited to the primary renewal notice; not a score for every secondary notice or every explanation. |
| Fixed renewal-related notice boundary recognized as calculable | 14/15 (93.3%) | TCG incorrectly says No despite identifying the Adviser's fixed annual notice. This does not validate date arithmetic or every date anchor. |
| Model human review flags | 5/15 (33.3%) | Raw model flags; no flags removed after evaluation. |
| Model No-review flags | 10/15 (66.7%) | Not equivalent to ten fully correct, safe or verified-current contracts. |

All 15 have a fixed primary renewal-related notice boundary in the supplied exhibit. For Applied Optoelectronics, this is the boundary to REQUEST renewal; renewal itself requires consent and a separate agreement. For options, successful exercise also depends on conditions. Historical/revised term ends do not establish current contractual status.

## Findings requiring correction

1. **N02 Pacific Select — wrong anchor in explanation.** `notice_period` correctly says 30 days before the NEXT term begins. `deadline_reason` then wrongly substitutes April 30 for that beginning. The next term begins May 1, 2027, so the reference boundary is April 1, 2027. Subtracting from April 30 would produce March 31, one day early. Preserve the next-term-start anchor in normalization.
2. **N05 Enova — contradictory calendar arithmetic.** The correct boundary is February 28, 2034, 365 days before February 28, 2035. The model also offers March 1, 2034, which is incorrect. The prompt expressly forbids calendar cutoff calculation. Keep arithmetic in deterministic code and separately track the 10-business-day response after receipt of the landlord's amendment.
3. **N09 Applied Optoelectronics — category error.** Sections 2.1–2.2 require the other party's consent and execution of a separate written agreement. Therefore the canonical category is **By agreement/amendment**, rather than a unilateral Option. The model captured these conditions and the three-calendar-month notice, but chose the wrong label.
4. **N10 TCG — calculability error and mixed notice label.** The Board's rolling 60-day termination right does not erase the Adviser's fixed 60-day notice before the annual expiry. January 31, 2027 minus 60 days gives December 2, 2026. Keep the rolling right separately; the primary fixed notice is calculable even while human review is flagged. `notice_type` also combines two labels rather than returning a single permitted label.
5. **N12 SS&C — review-policy inconsistency.** The fixed Section 4.1 notice applies to either party, while Section 5.1(c) grants a separate post-initial-term termination right to the Fund or Management. The explanation calls these equivalent in party and purpose because both use 90 days. They differ in actor scope and timing. This merits a manual policy check comparable to the other asymmetric-right cases; No-review is not evidence that every notice is interchangeable.

Some amendment rows infer an original/extended term start from amendment or agreement dates (e.g. N04 Virtus and N05 Enova). Those assertions were not scored as correct merely because the expiry was correct. A known amended expiry can support a boundary without establishing the original commencement date.

## Why the five review flags appeared

| Contract | Assessment |
|---|---|
| Pacific Select | The Adviser has fixed non-renewal and the Trust has rolling termination. Both can coexist; the flag follows v6's conservative asymmetry rule, rather than proving a contract conflict. Correct the date anchor regardless. |
| Enova | Useful operational review: initial option notice and subsequent confirmation/arbitration response must both be tracked. Dates triggered by future receipt are separate from the fixed first notice. |
| Applied Optoelectronics | Useful review: mutual renewal agreement, asymmetric early termination and right of first refusal require separate treatment. Correct the canonical category. |
| TCG | Fixed Adviser notice and rolling Board notice can coexist. Flagging review should not suppress the known fixed boundary. |
| PIMCO | Fixed PIMCO non-renewal and rolling Trust termination can coexist. The current prompt conservatively flags these different rights; this alone does not indicate unclear expiry or conflicting text. |

The frozen v6 prompt explicitly asks for review when different parties/clauses set non-equivalent periods for plausibly the same termination/renewal right. The model tends to interpret “both end the agreement” broadly. This helps explain review flags on clear text. Do not retrospectively rewrite these outputs or mix a changed prompt into the same reported run. A future prompt/schema could represent each notice separately by actor, purpose, anchor, period and receipt requirement, and reserve ambiguity review for unresolved interpretation.

## Per-contract audit

Reference boundaries below are independently calculated or explicitly stated. They are not model-produced deadlines and have not been run through the dashboard's existing normalization/date pipeline in this review. Receipt/delivery buffers, later amendments, actual option eligibility and current renewal cycles are not verified.

| ID | Contract | Expiry | Expected category | Primary notice | Reference boundary | Model review | Finding |
|---|---|---|---|---|---|---|---|
| N01 | City National Rochdale / SEI | 2028-03-31 | Automatic | 180 days before term end | 2027-10-03 | No | Primary expiry/category/notice match |
| N02 | Pacific Select | 2027-04-30 | Automatic | 30 days before NEXT term begins | 2027-04-01 | Yes | Explanation uses wrong anchor |
| N03 | Purple | 2027-12-31 | Automatic | 90 days before expiry | 2027-10-02 | No | Primary expiry/category/notice match; model calculates despite instruction |
| N04 | Virtus / BNY | 2027-12-01 | Automatic | Notice RECEIVED 90 days before expiry | 2027-09-02 | No | Primary match; original commencement not established by amendment date alone |
| N05 | Enova | 2035-02-28 | Option | 365 days before expiry | 2034-02-28 | Yes | Later confirmation required; contradictory arithmetic |
| N06 | Quantum Circuits | 2028-03-31 | Option | 180 days before termination date | 2027-10-03 | No | Primary match; eligibility conditions remain |
| N07 | Nathan's Famous | 2029-03-31 | Option | Explicit June 30, 2028 cutoff | 2028-06-30 | No | Primary match; valuation/default conditions remain |
| N08 | Arbitrage Funds / State Street | 2027-09-30 | Automatic | 90 days before expiry | 2027-07-02 | No | Primary match |
| N09 | Applied Optoelectronics | 2040-10-31 | By agreement/amendment | 3 calendar months before expiry | 2040-07-31 | Yes | Model incorrectly labels Option |
| N10 | TCG | 2027-01-31 | Automatic | Adviser's 60 days before annual expiry | 2026-12-02 | Yes | Model incorrectly suppresses fixed deadline |
| N11 | PIMCO | 2027-10-31 | Automatic | PIMCO's 30 days before expiry | 2027-10-01 | Yes | Primary match; separate Trust rolling termination |
| N12 | HPS / SS&C | 2025-12-31 | Automatic | 90 days before NEXT term begins | 2025-10-03 | No | Primary match; secondary-right equivalence needs review |
| N13 | DURECT | 2027-02-19 | Option | Explicit August 23, 2026 cutoff | 2026-08-23 | No | Correctly selects revised cutoff |
| N14 | UroGen | 2027-04-01 | Automatic | 18 calendar months before expiry | 2025-10-01 | No | Primary match; commercial redactions/base scope remain |
| N15 | Frequency Electronics | 2029-09-30 | Option | Explicit April 1–October 1, 2028 exercise window | 2028-10-01 | No | Captures both earliest and latest exercise dates |

## Implication for the project

The core expiry and primary notice extraction is promising on this selected sample. Classification, date-anchor reasoning and multiple-right handling still need correction before treating every row as automation-ready. Report these field-level results separately. A lower review rate is not a substitute for correct usable deadlines.

Preserve original held-out outcomes and the two supplemental runs as distinct evaluations. The new sample is deliberately clearer and includes recurring fund-service templates, so its percentages do not establish performance across unseen real-world contracts.
