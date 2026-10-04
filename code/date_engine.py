#!/usr/bin/env python3
"""Offline notice arithmetic for checked or model inputs. Supports explicit dates/windows and alternate notice anchors; never calls an LLM."""
import argparse,calendar,csv
from datetime import date,timedelta
from pathlib import Path
def add_months(d,n):
    index=d.year*12+d.month-1+n; y,m=divmod(index,12);m+=1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
def calculate(row,as_of,alert_days=30):
    if alert_days<0:raise ValueError('alert_days must not be negative')
    result={'id':row['id'],'contract':row['contract'],'input_origin':row['input_origin'],'date_certainty':row['date_certainty'],'calculated_term_end':'','window_opens':'','notice_cutoff':'','status':'review_required','needs_human_review':row['needs_human_review'],'days_until_cutoff':'','alert_state':'human_review','reason':''}
    def review(reason):
        result.update(status='review_required',needs_human_review='Yes',alert_state='human_review',reason=reason);return result
    if row['input_ready'].lower()!='yes':return review('Structured date or notice rule missing, redacted, uncertain, or not accepted by normalizer.')
    kind=row['rule_type']
    if kind in {'none','rolling'}:
        result.update(status='no_fixed_cutoff',alert_state='human_review' if result['needs_human_review']=='Yes' else 'not_applicable',reason='No single fixed cutoff for this notice rule.');return result
    try:
        end=date.fromisoformat(row['term_end']);result['calculated_term_end']=end.isoformat()
        anchor=date.fromisoformat(row.get('notice_anchor') or row['term_end'])
        if kind=='days_before_end':
            amount=int(row['lead_amount'])
            if amount<0:raise ValueError('Negative notice amount')
            cutoff=anchor-timedelta(days=amount)
        elif kind=='months_before_end':
            amount=int(row['lead_amount'])
            if amount<0:raise ValueError('Negative notice amount')
            cutoff=add_months(anchor,-amount)
        elif kind=='explicit_date':
            cutoff=date.fromisoformat(row['explicit_cutoff'])
            if row.get('explicit_open'):
                opening=date.fromisoformat(row['explicit_open'])
                if opening>cutoff:raise ValueError('Window opens after cutoff')
                result['window_opens']=opening.isoformat()
        elif kind=='month_range':
            opening,closing=int(row['range_open_months']),int(row['range_close_months'])
            if opening<=closing or closing<0:raise ValueError('Invalid bounded window')
            result['window_opens']=add_months(end,-opening).isoformat();cutoff=add_months(end,-closing)
        else:return review('Unknown or ambiguous notice rule type.')
    except (ValueError,TypeError,KeyError) as exc:return review('Invalid or missing structured input: '+str(exc))
    remaining=(cutoff-as_of).days
    result.update(notice_cutoff=cutoff.isoformat(),status='cutoff_computed',days_until_cutoff=remaining,reason='First-term arithmetic under stated input provenance and calendar convention.')
    if result['needs_human_review']=='Yes':state='human_review'
    elif remaining<0:state='cutoff_passed_verify_current_term'
    elif result['window_opens'] and as_of<date.fromisoformat(result['window_opens']):state='window_not_open'
    elif remaining<=alert_days:state='closing_soon'
    else:state='upcoming'
    result['alert_state']=state
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input_csv',type=Path);p.add_argument('output_csv',type=Path);p.add_argument('--as-of',type=date.fromisoformat,required=True);p.add_argument('--alert-days',type=int,default=30);args=p.parse_args()
    if args.alert_days<0:p.error('--alert-days must not be negative')
    with args.input_csv.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    if not rows:p.error('No rows')
    results=[calculate(r,args.as_of,args.alert_days) for r in rows]
    args.output_csv.parent.mkdir(parents=True,exist_ok=True)
    with args.output_csv.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    print(f'Wrote {len(results)} rows to {args.output_csv}')
if __name__=='__main__':main()
