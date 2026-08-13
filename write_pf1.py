import pathlib
out = pathlib.Path('boaapp/templates/boaapp/process_flows.html')
p = r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}thenumerix | AI Finance Process Flows{% endblock %}
{% block content %}
<style>
/* ══════════════════════════════════════════════════════════
   PROCESS FLOWS — 7-Ideations Design Tokens
   ══════════════════════════════════════════════════════════ */
:root{
  --pf-blue:#3b82f6;--pf-violet:#8b5cf6;--pf-emerald:#10b981;
  --pf-amber:#f59e0b;--pf-rose:#ef4444;
  --pf-grad-b:linear-gradient(135deg,#3b82f6,#8b5cf6);
  --pf-grad-g:linear-gradient(135deg,#10b981,#059669);
  --pf-surface:rgba(255,255,255,.75);--pf-border:rgba(0,0,0,.08);
  --pf-shadow:0 4px 24px rgba(0,0,0,.07);--pf-shadow-lg:0 12px 48px rgba(0,0,0,.13);
  --pf-radius:18px;
}
[data-theme="dark"]{
  --pf-surface:rgba(22,28,45,.8);--pf-border:rgba(255,255,255,.08);
  --pf-shadow:0 4px 24px rgba(0,0,0,.4);--pf-shadow-lg:0 12px 48px rgba(0,0,0,.55);
}
/* ── Keyframes ── */
@keyframes pfFadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes pfFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes pfPulse{0%,100%{opacity:1}50%{opacity:.45}}
@keyframes pfScan{from{top:0}to{top:100%}}
@keyframes pfSlide{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:translateX(0)}}

/* ── Progress bar ── */
.pf-progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;background:rgba(0,0,0,.06);pointer-events:none}
.pf-progress-fill{height:100%;background:var(--pf-grad-b);width:0%;transition:width .2s linear}
[data-theme="dark"] .pf-progress{background:rgba(255,255,255,.06)}

/* ── Sticky nav ── */
.pf-sticky-nav{position:sticky;top:0;z-index:200;
  background:rgba(255,255,255,.88);backdrop-filter:blur(16px);
  border-bottom:1px solid var(--pf-border);padding:.45rem 1rem;
  display:flex;gap:.25rem;overflow-x:auto;scrollbar-width:none;flex-wrap:nowrap}
.pf-sticky-nav::-webkit-scrollbar{display:none}
[data-theme="dark"] .pf-sticky-nav{background:rgba(15,23,42,.88)}
.pf-nav-tab{padding:.35rem .85rem;border-radius:999px;font-size:.72rem;font-weight:700;
  border:none;background:transparent;cursor:pointer;color:inherit;opacity:.55;
  white-space:nowrap;transition:all .2s;letter-spacing:.03em}
.pf-nav-tab:hover{opacity:1;background:rgba(59,130,246,.08)}
.pf-nav-tab.active{opacity:1;background:var(--pf-blue);color:#fff}

/* ── Hero ── */
.pf-hero{text-align:center;padding:3.5rem 0 2.5rem;position:relative;overflow:hidden}
.pf-hero::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 55% at 50% -5%,rgba(59,130,246,.11) 0%,transparent 70%),
             radial-gradient(ellipse 45% 35% at 85% 110%,rgba(139,92,246,.08) 0%,transparent 60%);
  pointer-events:none}
.pf-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.3rem .9rem;border-radius:999px;
  background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.2);font-size:.72rem;font-weight:700;
  color:var(--pf-blue);margin-bottom:.9rem;text-transform:uppercase;letter-spacing:.06em}
.pf-hero h1{font-size:clamp(1.9rem,4.5vw,3.1rem);font-weight:800;line-height:1.1;margin-bottom:.8rem;
  background:linear-gradient(135deg,#1e3a5f 0%,#3b82f6 50%,#8b5cf6 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
[data-theme="dark"] .pf-hero h1{background:linear-gradient(135deg,#e2e8f0 0%,#60a5fa 50%,#a78bfa 100%);
  -webkit-background-clip:text;background-clip:text}
.pf-hero .lead{font-size:1rem;opacity:.7;max-width:580px;margin:0 auto 2rem}
.pf-kpi-strip{display:flex;justify-content:center;flex-wrap:wrap;gap:1rem;margin-top:1rem}
.pf-kpi-chip{display:flex;align-items:center;gap:.6rem;padding:.6rem 1.1rem;border-radius:14px;
  background:var(--pf-surface);border:1px solid var(--pf-border);backdrop-filter:blur(8px);
  box-shadow:var(--pf-shadow);animation:pfFloat 3s ease-in-out infinite}
.pf-kpi-chip:nth-child(2){animation-delay:.5s}
.pf-kpi-chip:nth-child(3){animation-delay:1s}
.pf-kpi-chip:nth-child(4){animation-delay:1.5s}
.pf-kpi-val{font-size:1.15rem;font-weight:800;background:var(--pf-grad-b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.pf-kpi-lbl{font-size:.72rem;opacity:.65;line-height:1.3}

/* ── Section ── */
.pf-sec{padding:2rem 0;animation:pfFadeUp .6s ease both}
.pf-sec-head{text-align:center;margin-bottom:1.6rem}
.pf-sec-head h2{font-size:1.55rem;font-weight:800;margin-bottom:.25rem}
.pf-sec-head p{font-size:.88rem;opacity:.65;max-width:560px;margin:0 auto}
.pf-tag{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.63rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.5rem}
.pf-tag--b{background:rgba(59,130,246,.11);color:#2563eb}
.pf-tag--g{background:rgba(16,185,129,.11);color:#059669}
.pf-tag--v{background:rgba(139,92,246,.11);color:#7c3aed}
.pf-tag--a{background:rgba(245,158,11,.11);color:#b45309}
.pf-tag--r{background:rgba(239,68,68,.11);color:#dc2626}

/* ── Story ── */
.pf-story-steps{display:grid;grid-template-columns:repeat(auto-fill,minmax(265px,1fr));gap:1rem;max-width:940px;margin:0 auto}
.pf-story-step{border-radius:var(--pf-radius);border:1px solid var(--pf-border);
  background:var(--pf-surface);backdrop-filter:blur(12px);box-shadow:var(--pf-shadow);
  padding:1.3rem;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s}
.pf-story-step:hover{transform:translateY(-4px);box-shadow:var(--pf-shadow-lg)}
.pf-story-step::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--pf-grad-b)}
.pf-step-num{width:36px;height:36px;border-radius:50%;background:var(--pf-grad-b);
  color:#fff;font-size:.82rem;font-weight:800;display:flex;align-items:center;
  justify-content:center;margin-bottom:.85rem}
.pf-story-step h4{font-size:.95rem;font-weight:800;margin-bottom:.45rem}
.pf-story-step p{font-size:.78rem;opacity:.72;line-height:1.55;margin:0}
.pf-stat{font-size:1.35rem;font-weight:800;background:var(--pf-grad-b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  line-height:1;margin-bottom:.35rem}

/* ── Mode toggle ── */
.pf-mode-toggle{display:flex;justify-content:center;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap}
.pf-mode-btn{padding:.45rem 1.2rem;border-radius:999px;font-size:.78rem;font-weight:700;
  border:2px solid var(--pf-border);background:var(--pf-surface);cursor:pointer;
  color:inherit;transition:all .2s;backdrop-filter:blur(8px)}
.pf-mode-btn:hover{border-color:var(--pf-blue);color:var(--pf-blue)}
.pf-mode-btn.active{background:var(--pf-blue);border-color:var(--pf-blue);color:#fff}

/* ── ELI5 ── */
.pf-eli5-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;max-width:940px;margin:0 auto}
.pf-eli5-card{border-radius:var(--pf-radius);border:1px solid var(--pf-border);
  background:var(--pf-surface);backdrop-filter:blur(12px);box-shadow:var(--pf-shadow);
  padding:1.3rem;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s}
.pf-eli5-card:hover{transform:translateY(-4px);box-shadow:var(--pf-shadow-lg)}
.pf-eli5-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.pf-eli5-card:nth-child(1)::before{background:linear-gradient(90deg,#3b82f6,#6366f1)}
.pf-eli5-card:nth-child(2)::before{background:linear-gradient(90deg,#10b981,#059669)}
.pf-eli5-card:nth-child(3)::before{background:linear-gradient(90deg,#8b5cf6,#7c3aed)}
.pf-eli5-card:nth-child(4)::before{background:linear-gradient(90deg,#f59e0b,#d97706)}
.pf-eli5-persona{font-size:1.4rem;margin-bottom:.6rem}
.pf-eli5-role{font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
  opacity:.5;margin-bottom:.45rem}
.pf-eli5-card h5{font-size:.88rem;font-weight:800;margin-bottom:.45rem}
.pf-eli5-card p{font-size:.77rem;opacity:.72;line-height:1.55;margin:0}
.pf-eli5-insight{margin-top:.75rem;padding:.5rem .7rem;border-radius:10px;
  background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.12);
  font-size:.73rem;font-weight:600;color:var(--pf-blue)}
[data-theme="dark"] .pf-eli5-insight{background:rgba(59,130,246,.1);border-color:rgba(59,130,246,.2)}

/* ── Pipeline demo (Engineer) ── */
.pf-demo-wrap{max-width:940px;margin:0 auto}
.pf-demo{border-radius:22px;border:1px solid var(--pf-border);background:var(--pf-surface);
  backdrop-filter:blur(14px);box-shadow:var(--pf-shadow-lg);overflow:hidden}
.pf-demo-bar{padding:.85rem 1.4rem;display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--pf-border);background:rgba(59,130,246,.035);gap:.8rem;flex-wrap:wrap}
.pf-demo-bar h4{font-size:.9rem;font-weight:800;margin:0;flex:1}
.pf-dots{display:flex;gap:.38rem}
.pf-dot{width:11px;height:11px;border-radius:50%}
.pf-dot--r{background:#ef4444}.pf-dot--y{background:#f59e0b}.pf-dot--g{background:#10b981}
.pf-pip-bar{display:flex;padding:.75rem 1.4rem;border-bottom:1px solid var(--pf-border);overflow-x:auto;gap:0}
.pf-pip{display:flex;flex-direction:column;align-items:center;gap:.2rem;flex:1;min-width:62px;position:relative}
.pf-pip:not(:last-child)::after{content:'';position:absolute;top:13px;right:-50%;width:100%;height:2px;
  background:var(--pf-border);transition:background .4s;z-index:0}
.pf-pip.done::after,.pf-pip.active::after{background:linear-gradient(90deg,rgba(59,130,246,.35),var(--pf-border))}
.pf-pip-dot{width:28px;height:28px;border-radius:50%;background:rgba(0,0,0,.06);border:2px solid var(--pf-border);
  display:flex;align-items:center;justify-content:center;font-size:.68rem;transition:all .3s;position:relative;z-index:1}
.pf-pip.active .pf-pip-dot{background:var(--pf-blue);border-color:var(--pf-blue);color:#fff;
  box-shadow:0 0 0 4px rgba(59,130,246,.2);animation:pfPulse 1.2s ease-in-out infinite}
.pf-pip.done .pf-pip-dot{background:var(--pf-emerald);border-color:var(--pf-emerald);color:#fff}
.pf-pip-lbl{font-size:.58rem;font-weight:700;text-align:center;opacity:.55;text-transform:uppercase;
  letter-spacing:.04em;transition:opacity .3s}
.pf-pip.active .pf-pip-lbl,.pf-pip.done .pf-pip-lbl{opacity:1}
.pf-demo-body{display:grid;grid-template-columns:230px 1fr;min-height:330px}
@media(max-width:620px){.pf-demo-body{grid-template-columns:1fr}}
.pf-inv-pane{padding:1rem;border-right:1px solid var(--pf-border);display:flex;flex-direction:column;gap:.6rem}
.pf-pane-lbl{font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;opacity:.45}
.pf-inv-card{border-radius:13px;border:1px solid var(--pf-border);background:var(--pf-surface);
  padding:.95rem;position:relative;overflow:hidden;font-size:.76rem;box-shadow:var(--pf-shadow);display:none}
.pf-inv-card.vis{display:block;animation:pfFadeUp .4s ease}
.pf-inv-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:.65rem}
.pf-inv-logo{font-size:.82rem;font-weight:800;color:var(--pf-blue)}
.pf-inv-num{font-size:.62rem;opacity:.45}
.pf-inv-row{display:flex;justify-content:space-between;padding:.18rem 0;border-bottom:1px solid var(--pf-border)}
.pf-inv-row:last-child{border:none}
.pf-inv-row .lbl{opacity:.52;font-size:.68rem}.pf-inv-row .val{font-weight:700;font-size:.73rem}
.pf-scan{position:absolute;left:0;right:0;height:3px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,.75),transparent);
  top:0;animation:pfScan 1.5s ease-in-out;pointer-events:none}
.pf-log{font-size:.68rem;opacity:.6;font-family:monospace;line-height:1.65}
.pf-stage{padding:1rem;overflow-y:auto;max-height:430px;display:flex;flex-direction:column;gap:.55rem}
.pf-step-card{border-radius:12px;border:1px solid var(--pf-border);
  background:rgba(255,255,255,.65);padding:.85rem 1rem;font-size:.81rem;
  animation:pfFadeUp .35s ease both;box-shadow:var(--pf-shadow)}
[data-theme="dark"] .pf-step-card{background:rgba(22,28,45,.7)}
.pf-step-card--ok{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.05)}
.pf-step-card h6{font-size:.84rem;font-weight:700;margin-bottom:.45rem;text-align:center}
.pf-chk{display:flex;align-items:center;gap:.45rem;padding:.28rem .45rem;border-radius:8px;
  font-size:.78rem;transition:background .3s;margin-bottom:.18rem}
.pf-chk.show{background:rgba(16,185,129,.07)}
.pf-chk i.pending{color:var(--pf-blue)}.pf-chk i.pass{color:var(--pf-emerald)}
.pf-json{background:#0f172a;color:#94a3b8;border-radius:9px;padding:.7rem .9rem;
  font-family:monospace;font-size:.73rem;line-height:1.65;white-space:pre-wrap}
.pf-json .key{color:#7dd3fc}.pf-json .str{color:#86efac}.pf-json .num{color:#fcd34d}
.pf-xt table{width:100%;font-size:.77rem;margin-bottom:.4rem}
.pf-xt th{font-size:.68rem;font-weight:700;background:rgba(0,0,0,.04);padding:.22rem .4rem}
.pf-xt td{padding:.18rem .4rem;border-bottom:1px solid var(--pf-border)}
.pf-xt td:last-child{text-align:right}
.label-col{opacity:.6}
.pf-ds{display:inline-block;padding:.13rem .48rem;border-radius:6px;font-size:.67rem;font-weight:700}
.pf-ds.posted{background:#d1fae5;color:#065f46}
.pf-dash{border-radius:18px;border:1px solid var(--pf-border);background:var(--pf-surface);
  backdrop-filter:blur(10px);box-shadow:var(--pf-shadow);padding:1.2rem;margin-top:1rem}
.pf-dash-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin-bottom:1rem}
@media(max-width:480px){.pf-dash-kpis{grid-template-columns:repeat(2,1fr)}}
.pf-dkpi{border-radius:12px;padding:.8rem;text-align:center;border:1px solid var(--pf-border);background:rgba(255,255,255,.55)}
[data-theme="dark"] .pf-dkpi{background:rgba(255,255,255,.04)}
.pf-dkpi-val{font-size:1.4rem;font-weight:800;background:var(--pf-grad-b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.pf-dkpi-lbl{font-size:.63rem;opacity:.6;text-transform:uppercase;letter-spacing:.04em;margin-top:.1rem}

/* ── Classroom ── */
.pf-cls-wrap{max-width:820px;margin:0 auto;position:relative}
.pf-cls-outer{overflow:hidden;border-radius:var(--pf-radius);border:1px solid var(--pf-border)}
.pf-cls-slides{display:flex;transition:transform .45s cubic-bezier(.4,0,.2,1)}
.pf-cls-slide{min-width:100%;padding:2rem;background:var(--pf-surface);backdrop-filter:blur(14px);box-sizing:border-box}
.pf-cls-slide-tag{display:inline-block;padding:.15rem .6rem;border-radius:999px;font-size:.6rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.65rem}
.pf-cls-slide h3{font-size:1.2rem;font-weight:800;margin-bottom:.65rem}
.pf-cls-slide p{font-size:.83rem;opacity:.75;line-height:1.65;margin-bottom:.85rem}
.pf-cls-facts{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:.65rem}
.pf-cls-fact{border-radius:12px;padding:.75rem;border:1px solid var(--pf-border);background:rgba(255,255,255,.55)}
[data-theme="dark"] .pf-cls-fact{background:rgba(255,255,255,.04)}
.pf-cls-fact-val{font-size:1.1rem;font-weight:800;background:var(--pf-grad-b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.2rem}
.pf-cls-fact-lbl{font-size:.7rem;opacity:.65}
.pf-cls-nav{display:flex;align-items:center;justify-content:space-between;margin-top:.9rem}
.pf-cls-btn{width:36px;height:36px;border-radius:50%;border:1px solid var(--pf-border);
  background:var(--pf-surface);cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:.8rem;color:inherit;transition:all .2s}
.pf-cls-btn:hover{background:var(--pf-blue);border-color:var(--pf-blue);color:#fff}
.pf-cls-dots{display:flex;gap:.45rem}
.pf-cls-dot{width:8px;height:8px;border-radius:50%;background:var(--pf-border);cursor:pointer;transition:all .2s}
.pf-cls-dot.active{background:var(--pf-blue);transform:scale(1.3)}
.pf-cls-counter{font-size:.72rem;opacity:.5;font-weight:700}

/* ── Key points ── */
.pf-kp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:1rem;max-width:900px;margin:0 auto}
.pf-kp-card{border-radius:var(--pf-radius);border:1px solid var(--pf-border);
  background:var(--pf-surface);backdrop-filter:blur(12px);box-shadow:var(--pf-shadow);
  padding:1.4rem;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s}
.pf-kp-card:hover{transform:translateY(-4px);box-shadow:var(--pf-shadow-lg)}
.pf-kp-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--pf-grad-b)}
.pf-kp-metric{font-size:1.6rem;font-weight:800;background:var(--pf-grad-b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  line-height:1;margin-bottom:.5rem}
.pf-kp-card h5{font-size:.88rem;font-weight:800;margin-bottom:.4rem}
.pf-kp-card p{font-size:.77rem;opacity:.72;line-height:1.55;margin:0}
.pf-kp-why{margin-top:.7rem;font-size:.72rem;font-weight:700;color:var(--pf-blue);
  padding:.3rem .6rem;border-radius:8px;background:rgba(59,130,246,.06);display:inline-block}
[data-theme="dark"] .pf-kp-why{background:rgba(59,130,246,.12)}

/* ── Code ── */
.pf-impl{max-width:940px;margin:0 auto}
.pf-impl details{border-radius:14px;border:1px solid var(--pf-border);background:var(--pf-surface);margin-bottom:.8rem;overflow:hidden}
.pf-impl summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.pf-impl summary::-webkit-details-marker{display:none}
.pf-impl summary::before{content:'\25B6';font-size:.6rem;transition:transform .2s}
.pf-impl details[open] summary::before{transform:rotate(90deg)}
.pf-impl pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;
  line-height:1.6;overflow-x:auto;border-top:1px solid var(--pf-border);
  font-family:'Cascadia Code','JetBrains Mono',monospace}

/* ── About ── */
.pf-about-card{max-width:740px;margin:0 auto;border-radius:var(--pf-radius);
  border:1px solid var(--pf-border);background:var(--pf-surface);backdrop-filter:blur(14px);
  box-shadow:var(--pf-shadow-lg);padding:2rem;text-align:center}
.pf-about-title{font-size:1.15rem;font-weight:800;margin-bottom:.35rem}
.pf-about-sub{font-size:.83rem;opacity:.65;margin-bottom:1.2rem}
.pf-about-pills{display:flex;flex-wrap:wrap;gap:.45rem;justify-content:center;margin-bottom:1.4rem}
.pf-about-pill{padding:.3rem .75rem;border-radius:999px;font-size:.7rem;font-weight:700;
  border:1px solid var(--pf-border);background:var(--pf-surface);
  backdrop-filter:blur(6px);transition:all .2s}
.pf-about-pill:hover{border-color:var(--pf-blue);color:var(--pf-blue)}
.pf-share-btn{padding:.55rem 1.4rem;border-radius:999px;font-size:.8rem;font-weight:700;
  border:none;background:var(--pf-grad-b);color:#fff;cursor:pointer;transition:opacity .2s}
.pf-share-btn:hover{opacity:.85}
</style>

<!-- ── Progress bar ── -->
<div class="pf-progress"><div class="pf-progress-fill" id="pfProgressFill"></div></div>

<!-- ── Sticky nav ── -->
<nav class="pf-sticky-nav" id="pfStickyNav">
  <button class="pf-nav-tab active" onclick="pfScrollTo('pf-story')"><i class="fas fa-book-open me-1"></i>Story</button>
  <button class="pf-nav-tab" onclick="pfScrollTo('pf-demo')"><i class="fas fa-play-circle me-1"></i>Demo</button>
  <button class="pf-nav-tab" onclick="pfScrollTo('pf-classroom')"><i class="fas fa-chalkboard-teacher me-1"></i>Classroom</button>
  <button class="pf-nav-tab" onclick="pfScrollTo('pf-keypoints')"><i class="fas fa-lightbulb me-1"></i>Key Points</button>
  <button class="pf-nav-tab" onclick="pfScrollTo('pf-code')"><i class="fas fa-code me-1"></i>Code</button>
  <button class="pf-nav-tab" onclick="pfScrollTo('pf-about')"><i class="fas fa-info-circle me-1"></i>About</button>
</nav>

<!-- ════════════════════════════ HERO ════════════════════════════ -->
<section class="pf-hero" id="pf-top">
  <div class="pf-badge"><i class="fas fa-robot"></i>&nbsp; AI-Powered Finance Automation</div>
  <h1>Finance Process Flows<br>Reimagined with AI</h1>
  <p class="lead">AP &amp; AR automation &#x2014; invoice receipt to ERP posting in 3.2 seconds, not 25 minutes. Zero manual data entry on 95% of invoices.</p>
  <div class="pf-kpi-strip">
    <div class="pf-kpi-chip"><div><div class="pf-kpi-val">95%</div><div class="pf-kpi-lbl">Touchless Rate</div></div></div>
    <div class="pf-kpi-chip"><div><div class="pf-kpi-val">3.2s</div><div class="pf-kpi-lbl">Avg Process Time</div></div></div>
    <div class="pf-kpi-chip"><div><div class="pf-kpi-val">9</div><div class="pf-kpi-lbl">Entities Supported</div></div></div>
    <div class="pf-kpi-chip"><div><div class="pf-kpi-val">$0.013</div><div class="pf-kpi-lbl">Cost Per Invoice</div></div></div>
  </div>
</section>

<!-- ════════════════════════════ STORY ════════════════════════════ -->
<section class="pf-sec" id="pf-story">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--b">The Story</span>
    <h2>From Invoice Chaos to Full Automation</h2>
    <p>A six-step transformation from an 8-person AP team to a serverless AI pipeline processing 15,000 invoices per month.</p>
  </div>
  <div class="pf-story-steps">

    <div class="pf-story-step">
      <div class="pf-step-num">1</div>
      <div class="pf-stat">15,000</div>
      <h4>Invoices/Month, 8 People, 25 Minutes Each</h4>
      <p>The AP team received invoices by email, PDF, portal, and fax. Every invoice required manual keying into Acumatica &#x2014; vendor lookup, GL code from memory, entity routing by gut instinct. At $25/invoice fully loaded, that is $375,000 per year in AP labor alone.</p>
    </div>

    <div class="pf-story-step">
      <div class="pf-step-num">2</div>
      <div class="pf-stat">9 Entities</div>
      <h4>200+ Vendors, Zero Consistent Format</h4>
      <p>Ashford's 9 hospitality entities (Stirling, Remington, Premier, OpenKey&#x2026;) each had different GL structures, approval thresholds, and vendor relationships. The same vendor invoiced different entities differently. No OCR tool alone could handle the variance without a judgment layer.</p>
    </div>

    <div class="pf-story-step">
      <div class="pf-step-num">3</div>
      <div class="pf-stat">97%</div>
      <h4>Azure Document Intelligence Extracts in One Call</h4>
      <p>Azure Form Recognizer's pre-built invoice model extracts vendor name, invoice number, amounts, and line items &#x2014; all in one REST call at $0.01/page. Per-field confidence scores flag low-confidence extractions. Output: structured JSON ready for the judgment layer.</p>
    </div>

    <div class="pf-story-step">
      <div class="pf-step-num">4</div>
      <div class="pf-stat">94%</div>
      <h4>Claude AI: The GL Code Judgment Layer</h4>
      <p>Rule-based GL coding works for 78% of invoices. It fails on new vendors, multi-line descriptions, and cross-entity allocations. A TF-IDF + logistic regression classifier trained on 2 years of GL history achieves 94% accuracy &#x2014; 16 percentage points better than hand-coded rules.</p>
    </div>

    <div class="pf-story-step">
      <div class="pf-step-num">5</div>
      <div class="pf-stat">73%</div>
      <h4>3-Way Match + Hierarchical Approval Routing</h4>
      <p>PO vs. Invoice vs. Goods Receipt with 2%/5% tolerance bands. Invoices under $5K that pass 3-way match auto-approve &#x2014; covering 73% of all invoice volume. Only exceptions or high-value invoices require a human decision. Approval queue cut by 73%.</p>
    </div>

    <div class="pf-story-step">
      <div class="pf-step-num">6</div>
      <div class="pf-stat">$0.013</div>
      <h4>Results: 95% Touchless, Full Audit Trail</h4>
      <p>OCR ($0.01) + Claude AI ($0.003) = $0.013/invoice vs. $15&#x2013;$40 manual. 95% of invoices touch zero human hands. Full immutable audit trail in Azure SQL: extraction confidence, GL reasoning, match result, approval chain, ERP response code. DSO dropped 30% on AR.</p>
    </div>

  </div>
</section>

<!-- ════════════════════════════ DEMO ════════════════════════════ -->
<section class="pf-sec" id="pf-demo">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--g">Live Demo</span>
    <h2>See It From Every Angle</h2>
    <p>ELI5 mode explains the value to each stakeholder. Engineer mode runs a live 6-stage AP pipeline simulation with real synthetic invoices.</p>
  </div>

  <div class="pf-mode-toggle">
    <button class="pf-mode-btn active" id="pfBtnELI5" onclick="pfSetMode('eli5')">
      <i class="fas fa-user-circle me-1"></i> ELI5 &#x2014; Plain English
    </button>
    <button class="pf-mode-btn" id="pfBtnEng" onclick="pfSetMode('engineer')">
      <i class="fas fa-terminal me-1"></i> Engineer View
    </button>
  </div>

  <!-- ELI5 Pane -->
  <div id="pfELI5Pane">
    <div class="pf-eli5-grid">

      <div class="pf-eli5-card">
        <div class="pf-eli5-persona">&#x1F4BC;</div>
        <div class="pf-eli5-role">CFO Perspective</div>
        <h5>The Math That Matters</h5>
        <p>AP cost $25/invoice &#xD7; 15,000/month = $375K/year. Now it is $0.013/invoice in compute cost. That is a $370K annual saving with tighter controls, faster month-end close, and a 30% DSO reduction on AR &#x2014; freeing up working capital that was sitting in float.</p>
        <div class="pf-eli5-insight">&#x1F4C9; 40-day DPO &#x2192; same-day posting &#x2022; cash flow optimization</div>
      </div>

      <div class="pf-eli5-card">
        <div class="pf-eli5-persona">&#x1F4CB;</div>
        <div class="pf-eli5-role">AP Clerk Perspective</div>
        <h5>Your Job Got Better</h5>
        <p>You no longer key 15,000 invoices a month. The system handles the 95% that are straightforward. You handle 750 complex, high-value, relationship-sensitive cases per month &#x2014; the ones that actually require human expertise, negotiation, and judgment.</p>
        <div class="pf-eli5-insight">&#x2705; 750 meaningful cases vs. 15,000 routine data entries</div>
      </div>

      <div class="pf-eli5-card">
        <div class="pf-eli5-persona">&#x2699;&#xFE0F;</div>
        <div class="pf-eli5-role">Data Engineer Perspective</div>
        <h5>The Architecture is Serverless</h5>
        <p>Email / blob &#x2192; Logic Apps trigger &#x2192; Form Recognizer REST &#x2192; Azure Function validates &#x2192; GL classifier &#x2192; Acumatica REST POST &#x2192; SQL audit log. Zero VMs. The entire pipeline at 15K invoices/month costs roughly $195 in Azure compute.</p>
        <div class="pf-eli5-insight">&#x26A1; $0.013/invoice &#x2022; 3.2s avg latency &#x2022; 0 servers to manage</div>
      </div>

      <div class="pf-eli5-card">
        <div class="pf-eli5-persona">&#x1F50D;</div>
        <div class="pf-eli5-role">Auditor Perspective</div>
        <h5>Every Decision Is Traceable</h5>
        <p>Every invoice carries an immutable record: OCR field confidence, GL assignment plus model reasoning, 3-way match result with variance details, approval chain with timestamps, and ERP HTTP response code. SOC 2-compatible. No more "who approved this?" investigations.</p>
        <div class="pf-eli5-insight">&#x1F512; Immutable SQL audit trail &#x2022; RBAC per entity &#x2022; AES-256 at rest</div>
      </div>

    </div>
  </div>

  <!-- Engineer Pane -->
  <div id="pfEngPane" style="display:none">
    <div class="pf-demo-wrap">
      <div class="pf-demo">
        <div class="pf-demo-bar">
          <div class="pf-dots">
            <div class="pf-dot pf-dot--r"></div>
            <div class="pf-dot pf-dot--y"></div>
            <div class="pf-dot pf-dot--g"></div>
          </div>
          <h4><i class="fas fa-terminal me-2" style="color:var(--pf-blue)"></i>AP Invoice Pipeline &#x2014; Live Simulator</h4>
          <div style="display:flex;gap:.5rem;flex-shrink:0">
            <button class="btn btn-primary btn-sm" id="btnRun" style="border-radius:8px;font-size:.79rem">
              <i class="fas fa-play me-1"></i> Run AP Demo
            </button>
            <button class="btn btn-outline-secondary btn-sm" id="btnReset" style="border-radius:8px;font-size:.79rem;display:none">
              <i class="fas fa-redo me-1"></i> Reset
            </button>
          </div>
        </div>
        <div class="pf-pip-bar">
          <div class="pf-pip" id="pip0"><div class="pf-pip-dot"><i class="fas fa-file-alt"></i></div><div class="pf-pip-lbl">Invoice</div></div>
          <div class="pf-pip" id="pip1"><div class="pf-pip-dot"><i class="fas fa-eye"></i></div><div class="pf-pip-lbl">OCR</div></div>
          <div class="pf-pip" id="pip2"><div class="pf-pip-dot"><i class="fas fa-tags"></i></div><div class="pf-pip-lbl">GL Code</div></div>
          <div class="pf-pip" id="pip3"><div class="pf-pip-dot"><i class="fas fa-check-circle"></i></div><div class="pf-pip-lbl">Validate</div></div>
          <div class="pf-pip" id="pip4"><div class="pf-pip-dot"><i class="fas fa-cloud-upload-alt"></i></div><div class="pf-pip-lbl">ERP Post</div></div>
          <div class="pf-pip" id="pip5"><div class="pf-pip-dot"><i class="fas fa-chart-bar"></i></div><div class="pf-pip-lbl">Dashboard</div></div>
        </div>
        <div class="pf-demo-body">
          <div class="pf-inv-pane">
            <div class="pf-pane-lbl">Invoice Preview</div>
            <div class="pf-inv-card" id="invoiceCard"></div>
            <div class="pf-pane-lbl" style="margin-top:.3rem">Processing Log</div>
            <div class="pf-log" id="logArea"></div>
          </div>
          <div class="pf-stage" id="demoPipeline"></div>
        </div>
      </div>
      <div class="pf-dash" id="demoDashboard" style="display:none">
        <div style="font-size:.84rem;font-weight:800;margin-bottom:.75rem">
          <i class="fas fa-chart-bar me-2" style="color:var(--pf-blue)"></i>Live AP Dashboard
        </div>
        <div class="pf-dash-kpis">
          <div class="pf-dkpi"><div class="pf-dkpi-val" id="kpiProcessed">0</div><div class="pf-dkpi-lbl">Processed</div></div>
          <div class="pf-dkpi"><div class="pf-dkpi-val" id="kpiTotal">$0</div><div class="pf-dkpi-lbl">Posted Total</div></div>
          <div class="pf-dkpi"><div class="pf-dkpi-val" id="kpiAvgTime">&#x2014;</div><div class="pf-dkpi-lbl">Avg Time</div></div>
          <div class="pf-dkpi"><div class="pf-dkpi-val" id="kpiErrors">0</div><div class="pf-dkpi-lbl">Exceptions</div></div>
        </div>
        <div style="overflow-x:auto">
          <table class="table table-sm" style="font-size:.77rem;margin:0">
            <thead><tr style="opacity:.6"><th>Invoice</th><th>Vendor</th><th>Amount</th><th>GL</th><th>Entity</th><th>Status</th><th>Time</th></tr></thead>
            <tbody id="dashTable"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</section>
'''
out.write_text(p, encoding='utf-8')
print('pf1 done')
