#!/usr/bin/env python3
"""Normalize model prose conservatively, without reading source references.
Adds explicit election dates/windows and next-term-start anchors to original parser.
This post-evaluation preprocessing is not native model output or a new LLM run.
"""
import argparse,csv,re
from datetime import date,timedelta
from pathlib import Path
import normalize_original as original
FIELDS=original.fields+['notice_anchor','explicit_cutoff','explicit_open']
def model_row(i,p):
    r=original.model_row(i,p)
    term=p['initial_term'];matches=original.dates(term)
    ends=[v for a,b,v in matches if re.search(r'(?:ending(?:\s+on)?|expires(?:\s+on)?|expiring(?:\s+on)?|through|until|including|\bto)\s*$',term[max(0,a-70):a],re.I)]
    if ends:r['term_end']=ends[-1]
    notice=p['notice_period'];primary=notice.split(';')[0]
    explicit=[v for a,b,v in original.dates(primary) if re.search(r'(?:no later than|on or before|no sooner than)\s*$',primary[max(0,a-30):a],re.I)]
    if p['deadline_calculable'].lower()=='yes':
        if explicit:
            r.update(input_ready='Yes',rule_type='explicit_date',lead_amount='',explicit_cutoff=explicit[-1],explicit_open=explicit[0] if 'no sooner than' in primary.lower() and len(explicit)>1 else '',date_certainty='Model asserted; not PDF verified',normalization_note='Named election date/window read from model notice text; not repaired from reference.')
        if r.get('term_end') and re.search(r'prior to the (?:beginning|commencement) of',notice,re.I):
            r['notice_anchor']=(date.fromisoformat(r['term_end'])+timedelta(days=1)).isoformat()
        if r['input_ready']!='Yes':
            quantity=re.search(r'(\d+)\s+calendar\s+days',primary,re.I)
            if quantity and r.get('term_end'):r.update(input_ready='Yes',rule_type='days_before_end',lead_amount=int(quantity[1]),date_certainty='Model asserted; not PDF verified')
    return {k:r.get(k,'') for k in FIELDS}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('predictions',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
    with args.predictions.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(model_row(i,p) for i,p in enumerate(rows,1))
    print(f'Wrote {len(rows)} model-normalized rows. No reference answers read.')
if __name__=='__main__':main()
