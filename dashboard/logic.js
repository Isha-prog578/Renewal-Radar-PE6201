(function(root){
const day=86400000;
function parse(s){if(!/^\d{4}-\d{2}-\d{2}$/.test(s||''))return null;const d=new Date(s+'T00:00:00Z');return !isNaN(d)&&d.toISOString().slice(0,10)===s?d:null}
const iso=d=>d.toISOString().slice(0,10);
function months(s,n){const d=parse(s);if(!d)return null;const date=d.getUTCDate();d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()-n);const last=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,0)).getUTCDate();d.setUTCDate(Math.min(date,last));return iso(d)}
const integer=n=>n!==''&&n!==null&&Number.isInteger(Number(n))&&Number(n)>=0&&Number(n)<100000;
function calculate(r,asof){let out={cutoff:null,open:null,days:null,status:'human_review',kind:'review_required'};if(r.input_ready!=='Yes'||!parse(asof))return out;
if(['none','rolling'].includes(r.rule_type))return {...out,kind:'no_fixed_cutoff',status:r.needs_human_review==='Yes'?'human_review':'not_applicable'};
if(!parse(r.term_end))return out;
const anchor=r.notice_anchor||r.term_end;if(!parse(anchor))return out;
if(r.rule_type==='explicit_date'&&parse(r.explicit_cutoff)){out.cutoff=r.explicit_cutoff;if(r.explicit_open){if(!parse(r.explicit_open)||r.explicit_open>out.cutoff)return {...out,cutoff:null};out.open=r.explicit_open}}
if(r.rule_type==='days_before_end'&&integer(r.lead_amount))out.cutoff=iso(new Date(+parse(anchor)-Number(r.lead_amount)*day));
if(r.rule_type==='months_before_end'&&integer(r.lead_amount))out.cutoff=months(anchor,Number(r.lead_amount));
if(r.rule_type==='month_range'&&integer(r.range_open_months)&&integer(r.range_close_months)&&Number(r.range_open_months)>Number(r.range_close_months)){out.open=months(r.term_end,Number(r.range_open_months));out.cutoff=months(r.term_end,Number(r.range_close_months))}
if(!out.cutoff||!parse(out.cutoff))return {...out,cutoff:null,open:null};out.kind='cutoff_computed';out.days=Math.round((+parse(out.cutoff)-+parse(asof))/day);
out.status=r.needs_human_review==='Yes'||r.date_certainty==='Candidate only'?'human_review':out.days<0?'cutoff_passed_verify_current_term':out.open&&asof<out.open?'window_not_open':out.days<=30?'closing_soon':'upcoming';return out}
const api={parse,months,calculate};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.RadarLogic=api;
})(typeof window!=='undefined'?window:globalThis);
