'use strict';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const renewalLabels = {
  "Automatic": "Auto-renews", "Conditional": "Renews if conditions are met",
  "Option": "Choice to renew", "By agreement/amendment": "Renew by agreement",
  "Rolling continuation": "Continues until cancelled", "Unclear": "Not clear"
};
const renewalLabel = v => renewalLabels[v] || v || 'Not clear';

// status -> [badge label, css suffix, deadline-box class]
const statusMeta = {
  closing_soon: ['Act within 30 days', 'urgent'],
  human_review: ['Needs a person to check', 'review'],
  upcoming: ['Upcoming', 'upcoming'],
  cutoff_passed_verify_current_term: ['Check latest contract', 'review'],
  window_not_open: ['Window not open yet', 'upcoming'],
  not_applicable: ['No fixed deadline', 'clear']
};

const state = { lane: 'reference', asof: '2026-10-02', filter: 'all', search: '', id: null, tab: 'due' };
let contracts = [];
let toastTimer;

const format = s => RadarLogic.parse(s)
  ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(RadarLogic.parse(s))
  : null;

const input = c => state.lane === 'reference' ? c.reference : c.model;
const calc = c => RadarLogic.calculate(input(c), state.asof);
const renewalType = c => state.lane === 'reference' ? c.referenceType : c.renewalType;

function matchesFilter(c, o) {
  if (state.filter === 'all') return true;
  return o.status === state.filter;
}

function filtered() {
  return contracts.filter(c => {
    const o = calc(c);
    const text = `${c.name} ${c.filename}`.toLowerCase();
    return matchesFilter(c, o) && (!state.search || text.includes(state.search.toLowerCase()));
  }).sort((a, b) => a.id - b.id);
}

function buildTimeline() {
  const start = RadarLogic.parse(state.asof) || new Date();
  const months = [];
  for (let i = 0; i < 12; i++) {
    const d = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth() + i, 1));
    months.push({ y: d.getUTCFullYear(), m: d.getUTCMonth(), label: d.toLocaleString('en-GB', { month: 'short', timeZone: 'UTC' }), urgent: 0, upcoming: 0 });
  }
  contracts.forEach(c => {
    const o = calc(c);
    if (!o.cutoff) return;
    const cd = RadarLogic.parse(o.cutoff);
    if (!cd) return;
    const bucket = months.find(mo => mo.y === cd.getUTCFullYear() && mo.m === cd.getUTCMonth());
    if (!bucket) return;
    if (o.status === 'closing_soon' || o.status === 'cutoff_passed_verify_current_term') bucket.urgent++;
    else bucket.upcoming++;
  });
  const max = Math.max(1, ...months.map(m => m.urgent + m.upcoming));
  $('#timeline').innerHTML = months.map(m => {
    const total = m.urgent + m.upcoming;
    const h = total ? Math.max(10, Math.round((total / max) * 90)) : 4;
    const cls = m.urgent ? 'has-urgent' : (m.upcoming ? 'has-upcoming' : '');
    return `<div class="timeline-month">
      ${total ? `<span class="timeline-count">${total}</span>` : ''}
      <div class="timeline-bar ${cls}" style="height:${h}px"></div>
      <span class="timeline-label">${m.label}</span>
    </div>`;
  }).join('');
}

function render() {
  $('#lane').value = state.lane;
  $('#asof').value = state.asof;

  const urgent = contracts.filter(c => ['closing_soon', 'cutoff_passed_verify_current_term'].includes(calc(c).status)).length;
  const review = contracts.filter(c => calc(c).status === 'human_review').length;
  const upcoming = contracts.filter(c => ['upcoming', 'window_not_open'].includes(calc(c).status)).length;
  const clear = contracts.filter(c => calc(c).status === 'not_applicable').length;

  $('#stat-urgent').textContent = urgent;
  $('#stat-review').textContent = review;
  $('#stat-upcoming').textContent = upcoming;
  $('#stat-clear').textContent = clear;
  $('#hero-count').textContent = contracts.length;

  const needsAttention = urgent + review;
  $('#hero-headline').textContent = needsAttention
    ? `${needsAttention} contract${needsAttention === 1 ? '' : 's'} need${needsAttention === 1 ? 's' : ''} your attention`
    : `Nothing needs your attention right now`;
  $('#hero-sub').textContent = `As of ${format(state.asof) || state.asof} — ${urgent} with a notice window closing within 30 days, ${review} that need a person to check dates or notice rules.`;

  $$('.stat-pill').forEach(p => p.classList.toggle('active', p.dataset.filter === state.filter));
  $$('.chip').forEach(p => p.classList.toggle('active', p.dataset.filter === state.filter));

  buildTimeline();

  const rows = filtered();
  $('#result-count').textContent = `${rows.length} of ${contracts.length} contracts`;
  $('#empty-state').hidden = rows.length > 0;
  $('#card-grid').innerHTML = rows.map(c => {
    const o = calc(c);
    const [label, cls] = statusMeta[o.status] || ['Unknown', 'review'];
    let deadlineValue;
    if (o.cutoff) {
      const days = o.days;
      deadlineValue = `${format(o.cutoff)}${days >= 0 ? ` · ${days} day${days === 1 ? '' : 's'} away` : ' · passed, verify current term'}`;
    } else if (o.status === 'human_review') {
      deadlineValue = 'Not enough in the contract to set a date';
    } else {
      deadlineValue = 'No notice deadline applies';
    }
    return `<button class="contract-card cc-${cls}" data-id="${c.id}">
      <div class="cc-top">
        <div>
          <div class="cc-name">${esc(c.name)}</div>
          <div class="cc-type">${esc(renewalLabel(renewalType(c)))}</div>
        </div>
        <span class="badge badge-${cls}">${label}</span>
      </div>
      <div class="cc-deadline">
        <div class="cc-deadline-label">Notice deadline</div>
        <div class="cc-deadline-value">${deadlineValue}</div>
      </div>
    </button>`;
  }).join('');

  $$('.contract-card').forEach(el => el.addEventListener('click', () => openDrawer(Number(el.dataset.id))));
}

function openDrawer(id) {
  state.id = id;
  state.tab = 'due';
  $('#drawer-backdrop').hidden = false;
  $('#drawer').hidden = false;
  renderDrawer();
}
function closeDrawer() {
  $('#drawer-backdrop').hidden = true;
  $('#drawer').hidden = true;
  state.id = null;
}

function renderDrawer() {
  const c = contracts.find(x => x.id === state.id);
  if (!c) return;
  const o = calc(c);
  const r = input(c);
  const [label, cls] = statusMeta[o.status] || ['Unknown', 'review'];
  $('#detail-eyebrow').textContent = `Contract ${String(c.id).padStart(2, '0')}`;
  $('#detail-title').textContent = c.name;
  $$('.drawer-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === state.tab);
    t.setAttribute('aria-selected', t.dataset.tab === state.tab);
  });

  const deadlineReason = state.lane === 'reference' ? (r.normalization_note || '') : (c.modelDeadlineReason || '');
  const evidenceText = state.lane === 'reference' ? (r.evidence || 'No evidence note recorded for the checked result.') : (c.modelEvidence || '');

  let body = '';
  if (state.tab === 'due') {
    let big;
    if (o.cutoff) big = `${format(o.cutoff)}${o.days >= 0 ? ` (${o.days} day${o.days === 1 ? '' : 's'} from now)` : ' — already passed'}`;
    else if (o.status === 'human_review') big = 'No fixed date available — needs a person';
    else big = 'No notice deadline applies';
    body += `<div class="deadline-box box-${cls}">
      <span class="badge badge-${cls}">${label}</span>
      <div class="deadline-big">${big}</div>
      <p>${esc(deadlineReason || 'This is the last day to act, based on the term end date and notice period stated in the contract.')}</p>
    </div>`;
    body += `<div class="detail-grid">
      <div class="detail-item"><dt>Renewal type</dt><dd>${esc(renewalLabel(renewalType(c)))}</dd></div>
      <div class="detail-item"><dt>Effective date</dt><dd>${esc(c.effectiveDate || 'Not stated')}</dd></div>
    </div>`;
  } else if (state.tab === 'terms') {
    body += `<div class="detail-section"><h3>Initial term</h3><p>${esc(c.initialTerm || 'Not stated')}</p></div>`;
    body += `<div class="detail-section"><h3>Renewal condition</h3><p>${esc(c.renewalCondition || 'None stated')}</p></div>`;
    body += `<div class="detail-section"><h3>Notice period</h3><p>${esc(c.noticePeriod || 'Not stated')}</p></div>`;
  } else if (state.tab === 'evidence') {
    body += `<div class="detail-section"><h3>Supporting passages</h3><div class="evidence-quote">${esc(evidenceText)}</div></div>`;
    body += `<a class="pdf-link" href="contracts/${c.id}.pdf" target="_blank" rel="noopener">${esc(c.pdfLabel || 'Open original PDF')} →</a>`;
  }
  $('#drawer-content').innerHTML = body;
}

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 2600);
}

function exportCSV() {
  const rows = filtered();
  const header = ['Company', 'Renewal type', 'Notice deadline', 'Status'];
  const lines = [header.join(',')];
  rows.forEach(c => {
    const o = calc(c);
    const [label] = statusMeta[o.status] || ['Unknown'];
    lines.push([c.name, renewalLabel(renewalType(c)), o.cutoff || '', label].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','));
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'renewal_radar_export.csv';
  a.click();
  toast('CSV exported');
}

function wire() {
  $('#search').addEventListener('input', e => { state.search = e.target.value; render(); });
  $('#lane').addEventListener('change', e => { state.lane = e.target.value; render(); });
  $('#asof').addEventListener('change', e => { if (RadarLogic.parse(e.target.value)) { state.asof = e.target.value; render(); } });
  $('#export').addEventListener('click', exportCSV);
  $('#reset-filters').addEventListener('click', () => { state.filter = 'all'; state.search = ''; $('#search').value = ''; render(); });
  $$('.stat-pill, .chip').forEach(el => el.addEventListener('click', () => { state.filter = el.dataset.filter; render(); }));
  $('#close-drawer').addEventListener('click', closeDrawer);
  $('#drawer-backdrop').addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('#drawer').hidden) closeDrawer(); });
  $$('.drawer-tab').forEach(t => t.addEventListener('click', () => { state.tab = t.dataset.tab; renderDrawer(); }));
}

fetch('data.json').then(r => r.json()).then(d => {
  contracts = d.contracts;
  wire();
  render();
}).catch(() => {
  $('#hero-headline').textContent = 'Could not load data.json';
  $('#hero-sub').textContent = 'Run this with "python3 -m http.server" from this folder, then open it at localhost — opening index.html directly blocks the data file from loading.';
});
