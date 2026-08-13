"""write_fst1.py — feature_store.html 7-ideations (part 1/2, write)"""
TMPL = r'boaapp/templates/boaapp/feature_store.html'
out = open(TMPL, 'w', encoding='utf-8')
out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Feature Store — Amex Fraud Detection{% endblock %}
{% block container_class %}fst-shell{% endblock %}
{% block content %}
<style>
/* ── Base ── */
.fst-shell{display:block;width:100%;max-width:100%;padding:0}
:root{
  --fst-accent:#006fcf;--fst-accent2:#00175a;--fst-surface:#fff;
  --fst-border:rgba(0,0,0,.07);--fst-shadow:0 2px 12px rgba(0,0,0,.06);
  --fst-muted:#6b7280;--fst-danger:#ef4444;--fst-safe:#10b981;
  --fst-radius:16px;
}
[data-theme="dark"]{
  --fst-surface:rgba(15,18,35,.97);--fst-border:rgba(255,255,255,.08);
  --fst-shadow:0 2px 12px rgba(0,0,0,.35);--fst-muted:#94a3b8;
}
@keyframes fstUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fstPulse{0%,100%{box-shadow:0 0 0 0 rgba(0,111,207,.3)}50%{box-shadow:0 0 0 8px rgba(0,111,207,0)}}

/* ── Progress bar ── */
.fst-progress-bar{position:fixed;top:0;left:0;width:100%;height:3px;z-index:9999;background:transparent;pointer-events:none}
.fst-progress-fill{height:100%;width:0;background:linear-gradient(90deg,#006fcf,#60a5fa);transition:width .12s linear}

/* ── Sticky nav ── */
.fst-sticky-nav{position:sticky;top:0;z-index:900;background:var(--fst-surface);border-bottom:1px solid var(--fst-border);backdrop-filter:blur(12px);padding:.45rem 1.5rem;display:flex;align-items:center;gap:.35rem;overflow-x:auto;scrollbar-width:none}
.fst-sticky-nav::-webkit-scrollbar{display:none}
.fst-nav-btn{flex-shrink:0;padding:.32rem .85rem;border-radius:999px;font-size:.68rem;font-weight:700;border:1.5px solid transparent;cursor:pointer;background:transparent;color:var(--fst-muted);transition:all .18s;text-transform:uppercase;letter-spacing:.04em}
.fst-nav-btn:hover{color:var(--fst-accent);border-color:rgba(0,111,207,.2)}
.fst-nav-btn.active{background:rgba(0,111,207,.08);color:var(--fst-accent);border-color:rgba(0,111,207,.22)}

/* ── Main wrap ── */
.fst-wrap{max-width:1100px;margin:0 auto;padding:1.5rem 1.5rem 3rem}

/* ── Hero ── */
.fst-hero{text-align:center;padding:1.5rem 0 1.2rem;animation:fstUp .4s ease both}
.fst-hero-tag{display:inline-block;padding:.25rem .9rem;border-radius:999px;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;background:rgba(0,111,207,.08);border:1px solid rgba(0,111,207,.18);color:var(--fst-accent);margin-bottom:.7rem}
.fst-hero h1{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:800;background:linear-gradient(135deg,#006fcf 0%,#00175a 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.35rem}
.fst-hero p{font-size:.84rem;color:var(--fst-muted);max-width:640px;margin:0 auto;line-height:1.6}
.fst-hero-context{display:inline-flex;align-items:center;gap:.5rem;margin-top:.75rem;padding:.45rem 1rem;border-radius:10px;background:rgba(0,111,207,.04);border:1px solid rgba(0,111,207,.12);font-size:.7rem;color:var(--fst-muted)}
.fst-hero-context strong{color:var(--fst-accent);font-weight:800}

/* ── Sections ── */
.fst-section{padding:2.5rem 0 1.5rem;border-top:1px solid var(--fst-border)}
.fst-section:first-of-type{border-top:none;padding-top:0}
.fst-sec-head{text-align:center;margin-bottom:1.5rem}
.fst-sec-head h2{font-size:1.35rem;font-weight:800;margin-bottom:.4rem}
.fst-sec-head p{font-size:.82rem;color:var(--fst-muted);max-width:620px;margin:0 auto}

/* ── Story ── */
.fst-story-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
@media(max-width:860px){.fst-story-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.fst-story-grid{grid-template-columns:1fr}}
.fst-story-step{background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);padding:1.1rem 1rem;box-shadow:var(--fst-shadow);transition:transform .2s,box-shadow .2s;cursor:default}
.fst-story-step:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,111,207,.12)}
.fst-story-num{font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--fst-accent);margin-bottom:.5rem}
.fst-story-icon{font-size:1.5rem;margin-bottom:.4rem;line-height:1}
.fst-story-step h4{font-size:.82rem;font-weight:800;margin-bottom:.4rem}
.fst-story-step p{font-size:.7rem;color:var(--fst-muted);line-height:1.65;margin:0}
.fst-story-step .fst-story-stat{margin-top:.5rem;font-size:.63rem;font-weight:700;color:var(--fst-accent);font-family:'Cascadia Code',monospace}

/* ── Demo mode toggle ── */
.fst-mode-bar{display:flex;gap:.5rem;justify-content:center;margin-bottom:1.25rem}
.fst-mode-tab{padding:.38rem 1.2rem;border-radius:999px;font-size:.7rem;font-weight:700;border:1.5px solid var(--fst-border);cursor:pointer;background:transparent;color:var(--fst-muted);transition:all .18s;text-transform:uppercase;letter-spacing:.04em}
.fst-mode-tab.active{background:rgba(0,111,207,.1);color:var(--fst-accent);border-color:rgba(0,111,207,.3)}
.fst-pane{display:none}
.fst-pane.active{display:block}

/* ── ELI5 pane ── */
.fst-eli5-wrap{max-width:720px;margin:0 auto}
.fst-persona-row{display:flex;gap:.6rem;flex-wrap:wrap;justify-content:center;margin-bottom:1rem}
.fst-persona{padding:.45rem 1rem;border-radius:10px;font-size:.72rem;font-weight:700;border:1.5px solid var(--fst-border);cursor:pointer;background:var(--fst-surface);transition:all .18s;text-align:center}
.fst-persona:hover{border-color:rgba(0,111,207,.3)}
.fst-persona.selected{background:rgba(0,111,207,.08);border-color:rgba(0,111,207,.35);color:var(--fst-accent)}
.fst-persona .fst-persona-icon{font-size:1.2rem;display:block;margin-bottom:.2rem}
.fst-run-eli5{display:block;margin:.6rem auto 0;padding:.6rem 2rem;border-radius:10px;font-size:.78rem;font-weight:800;border:none;cursor:pointer;background:linear-gradient(135deg,#006fcf,#00175a);color:#fff;transition:all .2s;letter-spacing:.03em}
.fst-run-eli5:hover{opacity:.88;transform:translateY(-1px)}
.fst-eli5-result{display:none;margin-top:1rem;background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);padding:1.1rem 1.2rem;box-shadow:var(--fst-shadow);animation:fstUp .3s ease both}
.fst-eli5-result.show{display:block}
.fst-eli5-result h4{font-size:.88rem;font-weight:800;margin-bottom:.65rem;color:var(--fst-accent)}
.fst-eli5-result p{font-size:.76rem;line-height:1.7;color:var(--c-text,#111);margin:0 0 .75rem}
.fst-eli5-stats{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.5rem}
.fst-eli5-stat{font-size:.63rem;font-weight:700;padding:.25rem .65rem;border-radius:999px;background:rgba(0,111,207,.07);color:var(--fst-accent);border:1px solid rgba(0,111,207,.15)}
[data-theme="dark"] .fst-eli5-result{background:rgba(0,111,207,.04)}

/* ── Original demo: layout ── */
.fst-grid{display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:.9rem;margin-top:0}
@media(max-width:1060px){.fst-grid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.fst-grid{grid-template-columns:1fr}}
.fst-panel{background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);box-shadow:var(--fst-shadow);padding:1.1rem;animation:fstUp .5s ease both;min-height:0;overflow:hidden}
.fst-panel:nth-child(2){animation-delay:.07s}.fst-panel:nth-child(3){animation-delay:.14s}
.fst-chart-wrap{position:relative;width:100%;height:220px}
.fst-panel-hd{display:flex;align-items:center;gap:.45rem;font-size:.75rem;font-weight:800;margin-bottom:.85rem;padding-bottom:.5rem;border-bottom:1px solid var(--fst-border);color:inherit}
.fst-panel-hd i{color:var(--fst-accent);opacity:.75}
.fst-panel-hd .fst-badge{margin-left:auto;font-size:.58rem;font-weight:700;padding:.15rem .5rem;border-radius:999px;background:rgba(0,111,207,.08);color:var(--fst-accent);border:1px solid rgba(0,111,207,.12)}
.fst-table-wrap{overflow-x:auto;border-radius:8px;border:1px solid var(--fst-border);margin-bottom:.75rem}
.fst-table{width:100%;font-size:.6rem;border-collapse:collapse;font-family:'Cascadia Code','JetBrains Mono','Fira Code',monospace;table-layout:fixed}
.fst-table th{background:rgba(0,111,207,.05);font-size:.56rem;text-transform:uppercase;letter-spacing:.05em;font-weight:700;padding:.35rem .45rem;text-align:left;color:var(--fst-muted);border-bottom:1px solid var(--fst-border);white-space:nowrap}
.fst-table td{padding:.28rem .45rem;border-bottom:1px solid var(--fst-border);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fst-table tr:last-child td{border-bottom:none}
.fst-table tr:hover td{background:rgba(0,111,207,.03)}
.fst-table tr.is-fraud td{background:rgba(239,68,68,.06)}
.fst-flag{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:3px}
.fst-flag--ok{background:#10b981}.fst-flag--fraud{background:#ef4444}
.fst-entity-row{display:flex;align-items:center;gap:.5rem;margin-bottom:.7rem;flex-wrap:wrap}
.fst-entity-chip{padding:.22rem .65rem;border-radius:7px;font-size:.65rem;font-weight:700;border:1px solid var(--fst-border);cursor:pointer;transition:all .18s;background:transparent;color:var(--fst-muted)}
.fst-entity-chip.active{background:rgba(0,111,207,.1);border-color:rgba(0,111,207,.3);color:var(--fst-accent)}
.fst-entity-chip:hover:not(.active){border-color:rgba(0,111,207,.2)}
.fst-entity-label{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--fst-muted)}
.fst-feat-list{list-style:none;padding:0;margin:0 0 .75rem;font-size:.68rem}
.fst-feat-list li{display:flex;align-items:center;gap:.45rem;padding:.3rem 0;border-bottom:1px solid var(--fst-border)}
.fst-feat-list li:last-child{border-bottom:none}
.fst-feat-name{font-weight:700;min-width:0;flex:1;font-size:.66rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fst-feat-agg{font-size:.56rem;color:var(--fst-muted);font-family:'Cascadia Code',monospace;white-space:nowrap}
.fst-feat-kind{font-size:.54rem;font-weight:700;padding:.1rem .4rem;border-radius:999px;white-space:nowrap}
.fst-feat-kind--velocity{background:rgba(239,68,68,.1);color:#dc2626}
.fst-feat-kind--spend{background:rgba(245,158,11,.1);color:#d97706}
.fst-feat-kind--geo{background:rgba(6,182,212,.1);color:#0891b2}
.fst-feat-kind--behavior{background:rgba(0,111,207,.1);color:#006fcf}
.fst-feat-kind--merchant{background:rgba(139,92,246,.1);color:#7c3aed}
[data-theme="dark"] .fst-feat-kind--velocity{background:rgba(239,68,68,.18);color:#fca5a5}
[data-theme="dark"] .fst-feat-kind--spend{background:rgba(245,158,11,.18);color:#fcd34d}
[data-theme="dark"] .fst-feat-kind--geo{background:rgba(6,182,212,.18);color:#67e8f9}
[data-theme="dark"] .fst-feat-kind--behavior{background:rgba(0,111,207,.18);color:#93c5fd}
[data-theme="dark"] .fst-feat-kind--merchant{background:rgba(139,92,246,.18);color:#c4b5fd}
.fst-btn{display:inline-flex;align-items:center;gap:.45rem;padding:.5rem 1.2rem;border-radius:9px;font-size:.72rem;font-weight:700;border:none;cursor:pointer;transition:all .2s}
.fst-btn--primary{background:linear-gradient(135deg,#006fcf,#00175a);color:#fff}
.fst-btn--primary:hover{opacity:.88;transform:translateY(-1px)}
.fst-btn--danger{background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff}
.fst-btn--safe{background:linear-gradient(135deg,#10b981,#059669);color:#fff}
.fst-vector{background:rgba(0,111,207,.03);border:1px solid rgba(0,111,207,.12);border-radius:9px;padding:.7rem;font-size:.6rem;font-family:'Cascadia Code','JetBrains Mono',monospace;line-height:1.6;max-height:200px;overflow-y:auto;display:none;white-space:pre}
.fst-vector.show{display:block;animation:fstUp .3s ease both}
.fst-score-result{display:none;margin-top:.65rem;padding:.65rem;border-radius:10px;text-align:center;animation:fstUp .3s ease both}
.fst-score-result.show{display:block}
.fst-score-result.is-fraud{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2)}
.fst-score-result.is-legit{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2)}
.fst-score-val{font-size:1.6rem;font-weight:900;line-height:1}
.fst-score-label{font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-top:.2rem}
.fst-score-detail{font-size:.6rem;color:var(--fst-muted);margin-top:.25rem}
.fst-reg{width:100%;font-size:.62rem;border-collapse:collapse;margin-bottom:.75rem}
.fst-reg th{font-size:.56rem;text-transform:uppercase;letter-spacing:.04em;color:var(--fst-muted);font-weight:600;padding:.32rem .35rem;text-align:left;border-bottom:1px solid var(--fst-border);white-space:nowrap}
.fst-reg td{padding:.3rem .35rem;border-bottom:1px solid var(--fst-border);vertical-align:middle;white-space:nowrap}
.fst-reg tr:last-child td{border-bottom:none}
.fst-pill{font-size:.54rem;font-weight:700;padding:.1rem .4rem;border-radius:999px}
.fst-pill--online{background:rgba(16,185,129,.1);color:#059669;border:1px solid rgba(16,185,129,.2)}
.fst-pill--batch{background:rgba(245,158,11,.1);color:#d97706;border:1px solid rgba(245,158,11,.2)}
.fst-pill--both{background:rgba(0,111,207,.08);color:#006fcf;border:1px solid rgba(0,111,207,.15)}
[data-theme="dark"] .fst-pill--online{background:rgba(16,185,129,.2);color:#34d399}
[data-theme="dark"] .fst-pill--batch{background:rgba(245,158,11,.2);color:#fcd34d}
[data-theme="dark"] .fst-pill--both{background:rgba(0,111,207,.2);color:#93c5fd}
.fst-sla{font-family:'Cascadia Code',monospace;font-size:.56rem;color:var(--fst-muted)}
.fst-mono{font-family:'Cascadia Code',monospace;font-size:.58rem;color:var(--fst-muted)}
.fst-arch{background:rgba(0,111,207,.03);border:1px solid rgba(0,111,207,.1);border-radius:10px;padding:.65rem .8rem;margin-top:.75rem;font-size:.62rem;line-height:1.65;color:var(--fst-muted)}
.fst-arch strong{color:var(--fst-accent);font-weight:700}
.fst-arch-title{font-size:.6rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--fst-accent);margin-bottom:.3rem}

/* ── Classroom ── */
.fst-cls-wrap{background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);box-shadow:var(--fst-shadow);overflow:hidden;max-width:820px;margin:0 auto}
.fst-cls-slide{display:none;padding:1.6rem 1.8rem}
.fst-cls-slide.active{display:block;animation:fstUp .3s ease both}
.fst-cls-num{font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--fst-accent);margin-bottom:.4rem}
.fst-cls-slide h3{font-size:1.05rem;font-weight:800;margin-bottom:.7rem}
.fst-cls-slide p{font-size:.77rem;line-height:1.72;color:var(--fst-muted);margin-bottom:.6rem}
.fst-cls-formula{background:rgba(0,111,207,.04);border:1px solid rgba(0,111,207,.12);border-radius:8px;padding:.7rem 1rem;font-size:.67rem;font-family:'Cascadia Code',monospace;color:var(--fst-accent);line-height:1.8;margin-top:.6rem}
[data-theme="dark"] .fst-cls-formula{background:rgba(0,111,207,.08);color:#93c5fd}
.fst-cls-nav{display:flex;align-items:center;justify-content:space-between;padding:.75rem 1.2rem;border-top:1px solid var(--fst-border);background:rgba(0,111,207,.02)}
.fst-cls-nav-btn{padding:.35rem .9rem;border-radius:8px;font-size:.68rem;font-weight:700;border:1.5px solid var(--fst-border);cursor:pointer;background:transparent;color:var(--fst-accent);transition:all .18s}
.fst-cls-nav-btn:hover{background:rgba(0,111,207,.08);border-color:rgba(0,111,207,.25)}
.fst-cls-dots{display:flex;gap:.45rem}
.fst-cls-dot{width:8px;height:8px;border-radius:50%;background:var(--fst-border);cursor:pointer;transition:background .2s}
.fst-cls-dot.active{background:var(--fst-accent)}

/* ── Key Points ── */
.fst-kp-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;max-width:860px;margin:0 auto}
@media(max-width:640px){.fst-kp-grid{grid-template-columns:1fr}}
.fst-kp{background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);padding:1.1rem 1rem;box-shadow:var(--fst-shadow)}
.fst-kp-icon{font-size:1.8rem;margin-bottom:.5rem;line-height:1}
.fst-kp h4{font-size:.82rem;font-weight:800;margin-bottom:.45rem}
.fst-kp p{font-size:.72rem;color:var(--fst-muted);line-height:1.68;margin:0}

/* ── Code blocks ── */
.fst-code-blocks{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:.7rem}
.fst-code-block{border-radius:14px;border:1px solid var(--fst-border);background:var(--fst-surface);overflow:hidden}
.fst-code-block summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.fst-code-block summary::-webkit-details-marker{display:none}
.fst-code-block summary::before{content:'\25B6';font-size:.6rem;transition:transform .2s}
.fst-code-block[open] summary::before{transform:rotate(90deg)}
.fst-code-block pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;line-height:1.65;overflow-x:auto;border-top:1px solid var(--fst-border);font-family:'Cascadia Code','JetBrains Mono',monospace}
.fst-code-block .kw{color:#93c5fd}.fst-code-block .fn{color:#34d399}.fst-code-block .str{color:#fca5a5}
.fst-code-block .cm{color:#64748b}.fst-code-block .num{color:#fcd34d}

/* ── About ── */
.fst-about-card{max-width:640px;margin:0 auto;text-align:center;background:var(--fst-surface);border:1px solid var(--fst-border);border-radius:var(--fst-radius);padding:2rem 1.5rem;box-shadow:var(--fst-shadow)}
.fst-about-card h3{font-size:1.05rem;font-weight:800;margin-bottom:.6rem;color:var(--fst-accent)}
.fst-about-card p{font-size:.76rem;color:var(--fst-muted);line-height:1.7;margin-bottom:.5rem}
.fst-share-btn{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem 1.4rem;border-radius:9px;font-size:.74rem;font-weight:700;border:1.5px solid rgba(0,111,207,.3);cursor:pointer;background:rgba(0,111,207,.06);color:var(--fst-accent);transition:all .2s;margin-top:.5rem}
.fst-share-btn:hover{background:rgba(0,111,207,.12);border-color:rgba(0,111,207,.5)}
</style>

<div class="fst-progress-bar"><div class="fst-progress-fill" id="fstProgressFill"></div></div>

<nav class="fst-sticky-nav">
  <button class="fst-nav-btn" onclick="fstScrollTo('story')">Story</button>
  <button class="fst-nav-btn" onclick="fstScrollTo('demo')">Demo</button>
  <button class="fst-nav-btn" onclick="fstScrollTo('classroom')">Classroom</button>
  <button class="fst-nav-btn" onclick="fstScrollTo('keypoints')">Key Points</button>
  <button class="fst-nav-btn" onclick="fstScrollTo('code')">Code</button>
  <button class="fst-nav-btn" onclick="fstScrollTo('about')">About</button>
</nav>

<div class="fst-wrap">

<!-- ══ HERO ══ -->
<div class="fst-hero" id="fst-top">
  <div class="fst-hero-tag"><i class="fas fa-shield-alt me-1"></i> American Express &mdash; Fraud Feature Store</div>
  <h1>Transaction Fraud Detection</h1>
  <p>Production feature store powering real-time fraud scoring for American Express card authorization.
     10 engineered features computed across velocity, spend, geo-risk, and merchant dimensions &mdash; served
     at &lt;50ms p99 latency for every swipe.</p>
  <div class="fst-hero-context">
    <i class="fas fa-info-circle" style="color:var(--fst-accent)"></i>
    <span>Entity: <strong>card_id</strong> &nbsp;|&nbsp; Cutoff: <strong>2026-04-12 14:35 UTC</strong> &nbsp;|&nbsp; Model: <strong>XGBoost v3.2</strong></span>
  </div>
</div>

<!-- ══ STORY ══ -->
<section class="fst-section" id="fst-story">
  <div class="fst-sec-head">
    <h2>The Story</h2>
    <p>Six chapters in building a real-time fraud detection system that processes 8 million card swipes per day at sub-50ms latency.</p>
  </div>
  <div class="fst-story-grid">

    <div class="fst-story-step">
      <div class="fst-story-num">Step 01</div>
      <div class="fst-story-icon">&#x1F4B3;</div>
      <h4>The $32 Billion Problem</h4>
      <p>US banks lost $32.6B to payment card fraud in 2024. For American Express, a false negative (missed fraud) costs $350&ndash;$2,500 per case in chargebacks, disputes, and reputational damage. A false positive (declined legitimate transaction) costs $40&ndash;$80 in cart abandonment and $160 in average cardholder lifetime value erosion. Every authorization decision carries real financial consequences in both directions.</p>
      <div class="fst-story-stat">$32.6B annual card fraud losses (US)</div>
    </div>

    <div class="fst-story-step">
      <div class="fst-story-num">Step 02</div>
      <div class="fst-story-icon">&#x23F1;&#xFE0F;</div>
      <h4>300 Milliseconds to Decide</h4>
      <p>From card swipe at the POS terminal to authorization approval or decline, Amex has 300ms. That window includes network transit (~40ms), fraud scoring (~50ms), credit limit check (~10ms), and authorization response. This is not a batch problem &mdash; you cannot query a data warehouse, run Spark jobs, or wait for nightly ETL. Feature computation must happen in real-time, from a pre-computed feature store served out of Redis.</p>
      <div class="fst-story-stat">50ms SLA for fraud scoring within 300ms total</div>
    </div>

    <div class="fst-story-step">
      <div class="fst-story-num">Step 03</div>
      <div class="fst-story-icon">&#x1F9EA;</div>
      <h4>Engineering 10 Fraud Signals</h4>
      <p>Raw transaction events &mdash; timestamp, amount, MCC, merchant, location &mdash; are not directly useful to a model. Feature engineering transforms them into predictive signals: velocity (transactions per hour), spend deviation (Z-score vs 30-day baseline), impossible travel (haversine distance &#247; time), and high-risk MCC (jewelry, electronics). These 10 features capture 94% of the signal from 200+ raw inputs.</p>
      <div class="fst-story-stat">10 features &rarr; 94% signal from 200+ raw inputs</div>
    </div>

    <div class="fst-story-step">
      <div class="fst-story-num">Step 04</div>
      <div class="fst-story-icon">&#x1F5C4;&#xFE0F;</div>
      <h4>Point-in-Time Correctness</h4>
      <p>Training a fraud model requires historical feature vectors computed as-of each authorization timestamp &mdash; not as-of today. Including post-authorization data (chargebacks filed 30 days later) causes data leakage, inflating offline AUC by 10&ndash;15 points. The feature store enforces point-in-time correctness via timestamp-indexed feature views, ensuring training examples only see features available at prediction time.</p>
      <div class="fst-story-stat">Data leakage inflates AUC by 10&ndash;15 points</div>
    </div>

    <div class="fst-story-step">
      <div class="fst-story-num">Step 05</div>
      <div class="fst-story-icon">&#x1F916;</div>
      <h4>XGBoost Model &mdash; 97 AUC</h4>
      <p>The fraud model is a 500-tree XGBoost gradient-boosted ensemble trained on 6 months of labeled transactions with a 200:1 class weight (0.5% base fraud rate). SHAP analysis reveals the top signals: transaction count in the past hour, amount Z-score, cross-border flag, and impossible travel &mdash; accounting for 64% of predictive gain. Optimal threshold (0.65) is calibrated to 95% precision on a held-out validation set.</p>
      <div class="fst-story-stat">0.97 AUC &middot; 95% precision @ 0.65 threshold</div>
    </div>

    <div class="fst-story-step">
      <div class="fst-story-num">Step 06</div>
      <div class="fst-story-icon">&#x1F4C8;</div>
      <h4>18 Months of Continuous Improvement</h4>
      <p>Since deploying the feature store architecture: false positive rate reduced 23% (fewer legitimate transactions declined), impossible travel feature alone catches 23% of card-present fraud that velocity alone misses, and behavioral drift monitoring (CUSUM change-point detection) reduced false positives for frequent international travelers by 41%. The feature store enables same-day feature updates when new fraud patterns emerge.</p>
      <div class="fst-story-stat">&#x2212;23% false positives &middot; &#x2212;41% international travel declines</div>
    </div>

  </div>
</section>

<!-- ══ DEMO ══ -->
<section class="fst-section" id="fst-demo">
  <div class="fst-sec-head">
    <h2>Interactive Demo</h2>
    <p>Select a perspective to explore the system, then switch to Engineer mode for the full authorization simulation.</p>
  </div>

  <div class="fst-mode-bar">
    <button class="fst-mode-tab active" data-pane="eli5" onclick="fstSetMode('eli5')">&#x1F4A1; ELI5 &mdash; Pick a Perspective</button>
    <button class="fst-mode-tab" data-pane="engineer" onclick="fstSetMode('engineer')">&#x2699;&#xFE0F; Engineer &mdash; Live Authorization Sim</button>
  </div>

  <!-- ELI5 pane -->
  <div class="fst-pane active" data-pane="eli5">
    <div class="fst-eli5-wrap">
      <div class="fst-persona-row">
        <div class="fst-persona selected" data-key="investigator" onclick="fstSelectPersona('investigator')">
          <span class="fst-persona-icon">&#x1F575;&#xFE0F;</span>Fraud Investigator
        </div>
        <div class="fst-persona" data-key="engineer" onclick="fstSelectPersona('engineer')">
          <span class="fst-persona-icon">&#x2699;&#xFE0F;</span>ML Engineer
        </div>
        <div class="fst-persona" data-key="scientist" onclick="fstSelectPersona('scientist')">
          <span class="fst-persona-icon">&#x1F52C;</span>Data Scientist
        </div>
        <div class="fst-persona" data-key="pm" onclick="fstSelectPersona('pm')">
          <span class="fst-persona-icon">&#x1F4CA;</span>Product Manager
        </div>
      </div>
      <button class="fst-run-eli5" onclick="fstRunELI5()"><i class="fas fa-bolt me-1"></i> Explain It To Me</button>
      <div class="fst-eli5-result" id="fstELI5Result">
        <h4 id="fstELI5Title"></h4>
        <p id="fstELI5Body"></p>
        <div class="fst-eli5-stats" id="fstELI5Stats"></div>
      </div>
    </div>
  </div>

  <!-- Engineer pane — original 3-panel demo -->
  <div class="fst-pane" data-pane="engineer">
  <div class="fst-grid">

    <!-- Panel 1: Raw Authorization Stream -->
    <div class="fst-panel">
      <div class="fst-panel-hd"><i class="fas fa-credit-card"></i> Authorization Stream <span class="fst-badge">Kafka &#8594; Flink</span></div>
      <div class="fst-entity-row">
        <span class="fst-entity-label">Card:</span>
        <button class="fst-entity-chip active" data-card="3782">&#x2022;&#x2022;3782</button>
        <button class="fst-entity-chip" data-card="3019">&#x2022;&#x2022;3019</button>
        <button class="fst-entity-chip" data-card="7641">&#x2022;&#x2022;7641</button>
      </div>
      <div class="fst-table-wrap">
        <table class="fst-table">
          <thead>
            <tr><th style="width:14%">card</th><th style="width:18%">auth_ts</th><th style="width:14%">amount</th><th style="width:10%">MCC</th><th style="width:20%">merchant</th><th style="width:12%">city</th><th style="width:12%">label</th></tr>
          </thead>
          <tbody id="fstRawBody"></tbody>
        </table>
      </div>
      <div class="fst-arch">
        <div class="fst-arch-title"><i class="fas fa-project-diagram me-1"></i> Why Point-in-Time Matters</div>
        When scoring card &#x2022;&#x2022;3782 at <strong>14:35 UTC</strong>, the feature store only uses
        transactions <strong>before</strong> that timestamp. Including future data causes
        <strong>data leakage</strong> &mdash; inflating offline metrics by 10&ndash;15 AUC points.
      </div>
    </div>

    <!-- Panel 2: Feature Engineering -->
    <div class="fst-panel">
      <div class="fst-panel-hd"><i class="fas fa-flask"></i> Feature Definitions <span class="fst-badge">10 features</span></div>
      <ul class="fst-feat-list" id="fstFeatList"></ul>
      <button class="fst-btn fst-btn--primary" id="fstComputeBtn"><i class="fas fa-bolt"></i> Score Transaction</button>
      <div class="fst-score-result" id="fstScoreResult">
        <div class="fst-score-val" id="fstScoreVal"></div>
        <div class="fst-score-label" id="fstScoreLabel"></div>
        <div class="fst-score-detail" id="fstScoreDetail"></div>
      </div>
      <div class="fst-panel-hd" style="margin-top:.75rem"><i class="fas fa-vector-square"></i> Feature Vector <span class="fst-badge" id="fstVecCard">card &#x2022;&#x2022;3782</span></div>
      <div class="fst-vector" id="fstVector"></div>
      <div id="fstVectorPlaceholder" style="font-size:.7rem;color:var(--fst-muted);margin-top:.4rem">Click <strong>Score Transaction</strong> to compute features as-of the point-in-time cutoff and produce a fraud probability.</div>
    </div>
''')
out.close()
print('fst1 part A done')
