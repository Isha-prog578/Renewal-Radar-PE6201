import csv
from datetime import date
import date_rules_heldout as engine
from normalize_model import blank
with open('reference_inputs.csv',encoding='utf-8-sig',newline='') as f:reference=list(csv.DictReader(f))
with open('model_inputs.csv',encoding='utf-8-sig',newline='') as f:model=list(csv.DictReader(f))
tests=[]
def check(name,row,asof,expected_state,expected_cutoff=None):
    got=engine.calculate(row,date.fromisoformat(asof),30)
    ok=got['alert_state']==expected_state and (expected_cutoff is None or got['notice_cutoff']==expected_cutoff)
    tests.append({'test':name,'as_of':asof,'expected_alert':expected_state,'actual_alert':got['alert_state'],'expected_cutoff':expected_cutoff or '', 'actual_cutoff':got['notice_cutoff'],'result':'PASS' if ok else 'FAIL'})
    assert ok,(name,got)
neo=reference[20]
check('31 days before cutoff',neo,'2001-09-18','upcoming','2001-10-19')
check('30 days before cutoff',neo,'2001-09-19','closing_soon','2001-10-19')
check('On cutoff day',neo,'2001-10-19','closing_soon','2001-10-19')
check('Day after cutoff',neo,'2001-10-20','cutoff_passed_verify_current_term','2001-10-19')
check('Review overrides closing alert',reference[14],'2001-03-01','human_review','2001-03-17')
check('Rolling notice has no cutoff',model[7],'2026-10-01','not_applicable','')
check('Missing event date',reference[21],'2026-10-01','human_review','')
check('Ambiguous notice unit',reference[36],'2026-10-01','human_review','')
synthetic=blank(0,{'filename':'Synthetic bounded-window test'},'synthetic_test')|{'input_ready':'Yes','needs_human_review':'No','rule_type':'month_range','term_end':'2027-06-30','range_open_months':6,'range_close_months':2}
check('Before bounded window',synthetic,'2026-12-29','window_not_open','2027-04-30')
check('Inside bounded window, far from cutoff',synthetic,'2027-01-01','upcoming','2027-04-30')
check('Closing bounded window',synthetic,'2027-04-01','closing_soon','2027-04-30')
leap=synthetic|{'rule_type':'months_before_end','term_end':'2024-03-31','lead_amount':1}
check('Leap-year month clamping',leap,'2024-02-01','closing_soon','2024-02-29')
invalid=neo|{'term_end':'bad-date'}
check('Invalid date routes to review',invalid,'2026-10-01','human_review','')

print(f'{len(tests)}/{len(tests)} alert checks passed')
