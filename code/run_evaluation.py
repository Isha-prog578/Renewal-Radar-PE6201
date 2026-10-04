#!/usr/bin/env python3
"""Recompute descriptive scores from frozen outputs and recorded adjudications.
No API calls, PDF relabelling or model reruns. Manual notice judgments stay manual.
"""
import csv,json,sys,importlib.util,subprocess
from pathlib import Path
from datetime import date
import date_engine
from normalize_original import dates
ROOT=Path(__file__).resolve().parent.parent
def rows(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def j(path):return json.loads((ROOT/path).read_text())
def main():
    summary={}
    p=rows('results/historical/original40_predictions.csv');g={r['B']:r['F'] for r in rows('evaluation/historical_original40/frozen_reference_rows.csv')}
    eligible=[r for r in p if g[r['filename']] not in {'Conditional','Unclear'}]
    summary['historical_original40']={'count':len(p),'category_correct':sum(r['renewal_type']==g[r['filename']] for r in p),'category_denominator':len(p),'binary_correct':sum((r['renewal_type']=='Automatic')==(g[r['filename']]=='Automatic') for r in eligible),'binary_denominator':len(eligible),'always_yes_correct':sum(g[r['filename']]=='Automatic' for r in eligible),'model_review_yes':sum(r['human_review']=='Yes' for r in p)}
    baseline=j('evaluation/historical_keyword_and_cost.json');k=[r for r in baseline['rows'] if r['binary_eligible']]
    summary['historical_original40']['recorded_keyword_correct']=sum(r['keyword_match'] is True for r in k)
    summary['historical_original40']['keyword_scope']='Reaggregates archived keyword decisions; full historical unselected PDFs/texts are not enclosed.'
    summary['historical_original40']['estimated_usd']=sum((r['input_tokens']*3+r['output_tokens']*15)/1000000 for r in baseline['rows'])
    compare=rows('evaluation/historical_original40/deadline_comparison.csv');exact=[r for r in compare if r['eligible_exact_cutoff']=='Yes']
    summary['historical_original40']['eligible_cutoffs']=len(exact);summary['historical_original40']['correct_eligible_cutoffs']=sum(r['model_cutoff']==r['reference_cutoff'] for r in exact)
    notices=j('evaluation/primary_notice_adjudication.json')
    for sample in ['additional10','additional15']:
        pp=rows(f'results/historical/{sample}_predictions.csv');gg=j(f'evaluation/{sample}_answer_key.json');assert len(pp)==len(gg)
        summary[sample]={'count':len(pp),'stated_expiry_correct':sum(ref['expiry_date'] in [v for _,_,v in dates(pred['initial_term'])] for pred,ref in zip(pp,gg)),'category_correct':sum(pred['renewal_type']==ref['canonical_renewal_type'] for pred,ref in zip(pp,gg)),'primary_notice_manual_matches':sum(r['primary_notice_match'] for r in notices if r['sample']==sample),'model_review_yes':sum(r['human_review']=='Yes' for r in pp),'scope':'Purposive clearer sample; notice judgments manually adjudicated, not automatically semantically graded.'}
    final=rows('results/final40_saved_predictions.csv');fg={r['filename']:r['category'] for r in j('evaluation/final40_categories.json')}
    summary['final40_selected']={'count':len(final),'category_matches':sum(r['renewal_type']==fg[r['filename']] for r in final),'model_review_flags':sum(r['human_review']=='Yes' for r in final),'scope':'Post-evaluation selection, descriptive reuse of earlier predictions; NOT a newly held-out score.'}
    ref=rows('datasets/final40/reference_inputs.csv');expect=j('evaluation/final40_arithmetic_expectations.json');assert len(ref)==len(expect)==40
    for row,e in zip(ref,expect):
        got=date_engine.calculate(row,date(2026,10,2));assert got['notice_cutoff']==e['expected_boundary'],(row['id'],got,e)
    summary['checked_input_arithmetic_regressions']={'passed':40,'total':40,'scope':'Regression checks on checked inputs; NOT model deadline accuracy.'}
    subprocess.run([sys.executable,'test_alerts.py'],cwd=ROOT/'evaluation/historical_original40',check=True)
    dest=ROOT/'results/reproduced';dest.mkdir(exist_ok=True);(dest/'evaluation_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print('Saved:',dest/'evaluation_summary.json')
if __name__=='__main__':main()
