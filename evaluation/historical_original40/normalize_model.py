import argparse,calendar,csv,re
from datetime import date
from pathlib import Path
MONTHS={name:i for i,name in enumerate(calendar.month_name) if name}
MONTH_PATTERN='(?:'+'|'.join(MONTHS)+')'
def dates(text):
    out=[]
    for m in re.finditer(r'('+MONTH_PATTERN+r')\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s+(\d{4})',text,re.I):
        try: out.append((m.start(),m.end(),date(int(m[3]),MONTHS[m[1].title()],int(m[2])).isoformat()))
        except ValueError: pass
    for m in re.finditer(r'(\d{1,2})\s+('+MONTH_PATTERN+r')\s+(\d{4})',text,re.I):
        try: out.append((m.start(),m.end(),date(int(m[3]),MONTHS[m[2].title()],int(m[1])).isoformat()))
        except ValueError: pass
    for m in re.finditer(r'\b\d{4}-\d{2}-\d{2}\b',text):
        try: out.append((m.start(),m.end(),date.fromisoformat(m[0]).isoformat()))
        except ValueError: pass
    return sorted(out)
def add_months(d,n):
    i=d.year*12+d.month-1+n; y,m=divmod(i,12);m+=1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
fields=['id','contract','input_origin','input_ready','term_end','rule_type','lead_amount','range_open_months','range_close_months','needs_human_review','date_certainty','evidence','normalization_note']
def blank(i,p,origin):
    return dict.fromkeys(fields,'')|{'id':i,'contract':p['filename'],'input_origin':origin,'input_ready':'No','needs_human_review':'Yes','date_certainty':'Unknown'}
def model_row(i,p):
    r=blank(i,p,'model_output_normalized_by_code')
    r['evidence']=p['evidence'];r['needs_human_review']=p['human_review']
    notice=p['notice_period']; kind=p['notice_type'].lower()
    if p['deadline_calculable'].lower()!='yes':
        if kind in {'none stated','rolling termination'}:
            r.update(input_ready='Yes',rule_type='none' if kind=='none stated' else 'rolling',date_certainty='Not applicable',normalization_note='Uses v6 classification. No fixed cutoff. Other notice types are not repaired.')
        else:
            r['normalization_note']='V6 says deadline not calculable. No human correction added to this lane.'
        return r
    if kind=='unclear' or re.search(r'within\s+(?:ninety|90)',notice,re.I):
        r['normalization_note']='Ambiguous notice purpose or within-window wording. Parser abstains.'
        return r
    primary=notice.split(';')[0]
    number=re.search(r'(?:\((\d+)\)|(\d+))\s*(days?|months?)',primary,re.I)
    if not number:
        words={'six':6,'twelve':12,'thirty':30,'sixty':60,'ninety':90}
        match=re.search(r'\b(six|twelve|thirty|sixty|ninety)\s+(days?|months?)',primary,re.I)
        if match:r['lead_amount']=words[match[1].lower()];unit=match[2].lower()
        elif 'at the expiry' in primary.lower() or 'at expiry' in primary.lower():r['lead_amount']=0;unit='days'
        else:r['normalization_note']='No unambiguous numeric primary notice quantity.';return r
    else:r['lead_amount']=int(number[1] or number[2]);unit=number[3].lower()
    r['rule_type']='months_before_end' if unit.startswith('month') else 'days_before_end'
    term=p['initial_term'];matches=dates(term)
    for a,b,d in reversed(matches):
        prefix=term[max(0,a-100):a].lower()
        if re.search(r'(?:ending|ends(?:\s+on)?|expires(?:\s+on)?|terminates(?:\s+on)?|through|until|\bto|i\.e\.,?)\s*$',prefix):
            r['term_end']=d;break
    if not r['term_end'] and 'anniversary' in term.lower():
        # Only explicit anniversary wording authorizes deriving an endpoint here.
        duration=re.search(r'(?:\((\d+)\)|(\d+))\s*(?:year|\)\s*year)',term,re.I)
        if not duration:
            word=re.search(r'\b(five|two|one|twenty)[- ]+year',term,re.I)
            years={'one':1,'two':2,'five':5,'twenty':20}.get(word[1].lower()) if word else None
        else:years=int(duration[1] or duration[2])
        start=dates(p['effective_date'])
        if years and start and len({d for _,_,d in start})==1:
            r['term_end']=add_months(date.fromisoformat(start[0][2]),years*12).isoformat()
    if not r['term_end']:
        r['normalization_note']='No explicit term endpoint recognized. Parser does not infer an endpoint from a duration alone.'
        return r
    r.update(input_ready='Yes',date_certainty='Model asserted; not PDF verified',normalization_note='Deterministic normalization of frozen v6 prose. Not human-verified and not a native structured v6 output.')
    return r


def main():
    parser=argparse.ArgumentParser(description='Conservatively normalize frozen v6 model prose, without reading the PDF reference.')
    parser.add_argument('predictions',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    with args.predictions.open(encoding='utf-8-sig',newline='') as f:predictions=list(csv.DictReader(f))
    rows=[model_row(i,p) for i,p in enumerate(predictions,1)]
    with args.output.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print(f'Wrote {len(rows)} normalized model rows')
if __name__=='__main__':main()
