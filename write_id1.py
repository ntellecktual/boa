"""write_id1.py — IDP Demo 7-ideations redesign, Part 1 ('w' mode)"""
from pathlib import Path

OUT = Path("boaapp/templates/boaapp/idp_demo.html")

p1 = r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}thenumerix | Intelligent Document Processing{% endblock %}

{% block content %}
<style>
/* ═══════════════════════════════════════════════════
   IDP DEMO — 7-Ideations Framework
   prefix: id-   accent: #14b8a6 teal
   ═══════════════════════════════════════════════════ */
:root{
  --id-teal:#14b8a6;--id-cyan:#0891b2;--id-violet:#8b5cf6;
  --id-emerald:#10b981;--id-amber:#f59e0b;--id-rose:#ef4444;
  --id-blue:#3b82f6;
  --id-grad:linear-gradient(135deg,#14b8a6,#0891b2);
  --id-grad-v:linear-gradient(135deg,#8b5cf6,#6d28d9);
  --id-grad-g:linear-gradient(135deg,#10b981,#059669);
  --id-grad-a:linear-gradient(135deg,#f59e0b,#d97706);
  --id-grad-b:linear-gradient(135deg,#3b82f6,#2563eb);
  --id-surface:rgba(255,255,255,.78);--id-border:rgba(0,0,0,.08);
  --id-shadow:0 4px 24px rgba(0,0,0,.07);--id-shadow-lg:0 12px 48px rgba(0,0,0,.13);
  --id-radius:18px;--id-text:#0f172a;
}
[data-theme="dark"]{
  --id-surface:rgba(22,28,45,.82);--id-border:rgba(255,255,255,.08);
  --id-shadow:0 4px 24px rgba(0,0,0,.4);--id-shadow-lg:0 12px 48px rgba(0,0,0,.55);
  --id-text:#f1f5f9;
}
@keyframes idFadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes idFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes idPulse{0%,100%{opacity:1}50%{opacity:.45}}
@keyframes idSlide{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}

/* ── Progress bar ── */
.id-progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;background:transparent}
.id-progress-fill{height:100%;width:0;background:var(--id-grad);transition:width .1s linear;border-radius:0 2px 2px 0}

/* ── Sticky nav ── */
.id-sticky-nav{position:sticky;top:0;z-index:900;backdrop-filter:blur(18px);
  background:rgba(255,255,255,.85);border-bottom:1px solid var(--id-border);padding:.3rem 0}
[data-theme="dark"] .id-sticky-nav{background:rgba(15,23,42,.88)}
.id-nav-inner{display:flex;justify-content:center;gap:.15rem;flex-wrap:wrap;padding:0 1rem}
.id-nav-tab{padding:.4rem .85rem;border-radius:20px;font-size:.74rem;font-weight:700;
  color:var(--id-text);opacity:.55;cursor:pointer;transition:all .22s;border:none;background:none;
  text-decoration:none;white-space:nowrap}
.id-nav-tab:hover{opacity:.85;background:rgba(20,184,166,.07)}
.id-nav-tab.active{opacity:1;background:rgba(20,184,166,.12);color:var(--id-teal)}

/* ── Hero ── */
.id-hero{text-align:center;padding:3.5rem 0 2.5rem;position:relative;overflow:hidden}
.id-hero::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 55% at 50% -5%,rgba(20,184,166,.11) 0%,transparent 70%),
             radial-gradient(ellipse 45% 35% at 15% 110%,rgba(139,92,246,.08) 0%,transparent 60%);
  pointer-events:none}
.id-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.3rem .9rem;border-radius:999px;
  background:rgba(20,184,166,.1);border:1px solid rgba(20,184,166,.2);font-size:.72rem;font-weight:700;
  color:var(--id-teal);margin-bottom:.9rem;text-transform:uppercase;letter-spacing:.06em}
.id-hero h1{font-size:clamp(1.9rem,4.5vw,3.1rem);font-weight:800;line-height:1.1;margin-bottom:.8rem;
  background:linear-gradient(135deg,#0f766e 0%,#14b8a6 50%,#8b5cf6 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
[data-theme="dark"] .id-hero h1{background:linear-gradient(135deg,#e2e8f0 0%,#2dd4bf 50%,#a78bfa 100%);
  -webkit-background-clip:text;background-clip:text}
.id-hero .lead{font-size:1rem;opacity:.7;max-width:620px;margin:0 auto 2rem}
.id-kpi-strip{display:flex;justify-content:center;flex-wrap:wrap;gap:1rem}
.id-kpi{display:flex;align-items:center;gap:.6rem;padding:.6rem 1.1rem;border-radius:14px;
  background:var(--id-surface);border:1px solid var(--id-border);backdrop-filter:blur(8px);
  box-shadow:var(--id-shadow);animation:idFloat 3s ease-in-out infinite}
.id-kpi:nth-child(2){animation-delay:.5s}.id-kpi:nth-child(3){animation-delay:1s}.id-kpi:nth-child(4){animation-delay:1.5s}
.id-kpi-val{font-size:1.15rem;font-weight:800;background:var(--id-grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.id-kpi-lbl{font-size:.72rem;opacity:.65;line-height:1.3}

/* ── Section shell ── */
.id-sec{padding:2rem 0;animation:idFadeUp .6s ease both}
.id-sec-head{text-align:center;margin-bottom:1.5rem}
.id-sec-head h2{font-size:1.55rem;font-weight:800;margin-bottom:.3rem}
.id-sec-head p{font-size:.88rem;opacity:.65;max-width:560px;margin:0 auto}
.id-tag{display:inline-block;padding:.2rem .75rem;border-radius:999px;font-size:.63rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.5rem}
.id-tag--t{background:rgba(20,184,166,.11);color:#0d9488}
.id-tag--v{background:rgba(139,92,246,.11);color:#7c3aed}
.id-tag--g{background:rgba(16,185,129,.11);color:#059669}
.id-tag--a{background:rgba(245,158,11,.11);color:#b45309}
.id-tag--b{background:rgba(59,130,246,.11);color:#2563eb}

/* ── Story ── */
.id-story-steps{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.1rem;max-width:980px;margin:0 auto}
.id-story-step{border-radius:var(--id-radius);border:1px solid var(--id-border);
  background:var(--id-surface);backdrop-filter:blur(12px);box-shadow:var(--id-shadow);
  padding:1.3rem 1.35rem;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s}
.id-story-step:hover{transform:translateY(-4px);box-shadow:var(--id-shadow-lg)}
.id-story-step::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--id-grad)}
.id-story-step:nth-child(2)::before{background:var(--id-grad-v)}
.id-story-step:nth-child(3)::before{background:var(--id-grad-b)}
.id-story-step:nth-child(4)::before{background:var(--id-grad-g)}
.id-story-step:nth-child(5)::before{background:var(--id-grad-a)}
.id-story-step:nth-child(6)::before{background:linear-gradient(135deg,#ef4444,#dc2626)}
.id-step-num{width:28px;height:28px;border-radius:50%;background:var(--id-grad);color:#fff;
  font-size:.72rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:.7rem}
.id-step-num--2{background:var(--id-grad-v)}
.id-step-num--3{background:var(--id-grad-b)}
.id-step-num--4{background:var(--id-grad-g)}
.id-step-num--5{background:var(--id-grad-a)}
.id-step-num--6{background:linear-gradient(135deg,#ef4444,#dc2626)}
.id-story-step h4{font-size:.92rem;font-weight:800;margin-bottom:.4rem;line-height:1.3}
.id-story-step p{font-size:.78rem;opacity:.72;margin:0 0 .7rem;line-height:1.55}
.id-stat{font-size:1.1rem;font-weight:800;background:var(--id-grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.id-stat-lbl{font-size:.65rem;opacity:.6}

/* ── Mode toggle ── */
.id-mode-toggle{display:flex;justify-content:center;margin-bottom:1.2rem;gap:.4rem}
.id-mode-btn{padding:.45rem 1.2rem;border-radius:22px;font-size:.8rem;font-weight:700;cursor:pointer;
  border:1.5px solid var(--id-border);background:var(--id-surface);color:var(--id-text);
  transition:all .22s;backdrop-filter:blur(8px)}
.id-mode-btn.active{background:var(--id-grad);color:#fff;border-color:transparent}

/* ── ELI5 cards ── */
.id-eli5-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;max-width:960px;margin:0 auto}
.id-eli5-card{border-radius:var(--id-radius);border:1px solid var(--id-border);
  background:var(--id-surface);backdrop-filter:blur(12px);box-shadow:var(--id-shadow);
  padding:1.3rem;transition:transform .25s,box-shadow .25s;position:relative;overflow:hidden}
.id-eli5-card:hover{transform:translateY(-4px);box-shadow:var(--id-shadow-lg)}
.id-eli5-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--id-grad)}
.id-eli5-card:nth-child(2)::before{background:var(--id-grad-v)}
.id-eli5-card:nth-child(3)::before{background:var(--id-grad-b)}
.id-eli5-card:nth-child(4)::before{background:var(--id-grad-g)}
.id-eli5-icon{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:1.1rem;color:#fff;margin-bottom:.85rem}
.id-eli5-role{font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;
  opacity:.5;margin-bottom:.25rem}
.id-eli5-card h4{font-size:.9rem;font-weight:800;margin-bottom:.5rem;line-height:1.3}
.id-eli5-card p{font-size:.79rem;opacity:.75;margin:0;line-height:1.55}
.id-eli5-stat{margin-top:.7rem;padding-top:.6rem;border-top:1px solid var(--id-border)}
.id-eli5-stat .val{font-size:1.1rem;font-weight:800;background:var(--id-grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.id-eli5-stat .lbl{font-size:.67rem;opacity:.6}

/* ── Engineer pane (IDP simulator) ── */
.id-impl-pane{display:none}
.id-impl-pane.active{display:block}
.id-eli5-pane.active{display:block}
.id-eli5-pane{display:none}

.id-demo-shell{border-radius:22px;border:1px solid var(--id-border);background:var(--id-surface);
  backdrop-filter:blur(14px);box-shadow:var(--id-shadow-lg);overflow:hidden;max-width:960px;margin:0 auto}
.id-demo-bar{padding:.85rem 1.4rem;display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--id-border);background:rgba(20,184,166,.03);gap:.8rem;flex-wrap:wrap}
.id-demo-bar h4{font-size:.9rem;font-weight:800;margin:0;flex:1}
.id-dots{display:flex;gap:.38rem}
.id-dot{width:11px;height:11px;border-radius:50%}
.id-dot--r{background:#ef4444}.id-dot--y{background:#f59e0b}.id-dot--g{background:#10b981}

/* pipeline track */
.id-pip-bar{display:flex;align-items:center;justify-content:center;gap:0;
  padding:.75rem 1.2rem;border-bottom:1px solid var(--id-border);flex-wrap:wrap}
.id-pip{display:flex;flex-direction:column;align-items:center;gap:.25rem;cursor:default;
  position:relative;padding:0 .6rem}
.id-pip::after{content:'';position:absolute;top:15px;left:calc(50% + 16px);
  width:calc(100% - 8px);height:2px;background:var(--id-border)}
.id-pip:last-child::after{display:none}
.id-pip-dot{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.7rem;background:var(--id-surface);
  border:2px solid var(--id-border);color:#94a3b8;transition:all .35s;position:relative;z-index:1}
.id-pip-lbl{font-size:.56rem;font-weight:700;opacity:.55;white-space:nowrap}
.id-pip.active .id-pip-dot{border-color:var(--id-teal);background:rgba(20,184,166,.12);
  color:var(--id-teal);box-shadow:0 0 0 4px rgba(20,184,166,.12);animation:idPulse 1.2s ease-in-out infinite}
.id-pip.done .id-pip-dot{border-color:var(--id-emerald);background:var(--id-emerald);color:#fff}
.id-pip.done .id-pip-lbl,.id-pip.active .id-pip-lbl{opacity:1}

/* pipeline body */
.id-i-body{display:grid;grid-template-columns:220px 1fr;gap:0;min-height:260px}
@media(max-width:700px){.id-i-body{grid-template-columns:1fr}}
.id-prev-pane{border-right:1px solid var(--id-border);padding:.7rem;font-size:.73rem;
  overflow-y:auto;max-height:400px}
.id-pane-lbl{font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.07em;
  opacity:.45;margin-bottom:.35rem}
.id-inv-card{border-radius:10px;border:1px solid var(--id-border);padding:.55rem .65rem;
  margin-bottom:.4rem;font-size:.7rem;opacity:0;transition:opacity .3s}
.id-inv-card.vis{opacity:1}
.id-inv-row{display:flex;justify-content:space-between;font-size:.66rem;padding:.1rem 0}
.id-inv-row .lbl{opacity:.6}.id-inv-row .val{font-weight:600}
.id-stage{padding:.8rem;overflow-y:auto;max-height:400px}
.id-step-card{border-radius:14px;border:1px solid var(--id-border);background:rgba(255,255,255,.55);
  padding:.85rem 1rem;margin-bottom:.65rem;animation:idFadeUp .35s ease both}
[data-theme="dark"] .id-step-card{background:rgba(255,255,255,.04)}
.id-step-card--ok{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.05)}
.id-step-card h6{font-size:.82rem;font-weight:800;margin-bottom:.45rem}
.id-chk{display:flex;align-items:center;gap:.4rem;font-size:.76rem;margin-bottom:.3rem;
  opacity:0;transition:opacity .3s}
.id-chk.show{opacity:1}
.id-chk .pass{color:var(--id-emerald);font-size:.72rem}
.id-json{font-family:monospace;font-size:.71rem;background:#0f172a;color:#94a3b8;
  border-radius:10px;padding:.65rem .85rem;line-height:1.55;margin-top:.45rem}
.id-json .key{color:#5eead4}.id-json .str{color:#6ee7b7}.id-json .num{color:#fcd34d}
.id-log2{font-family:monospace;font-size:.67rem;line-height:1.55;max-height:140px;
  overflow-y:auto;padding:.4rem;background:rgba(0,0,0,.03);border-radius:8px;margin-top:.25rem}
[data-theme="dark"] .id-log2{background:rgba(255,255,255,.03)}

/* dashboard */
.id-dash2{border-radius:18px;border:1px solid var(--id-border);background:var(--id-surface);
  backdrop-filter:blur(12px);box-shadow:var(--id-shadow);padding:1rem 1.3rem;
  max-width:960px;margin:1rem auto 0;display:none}
.id-dash2-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin-bottom:.7rem}
@media(max-width:600px){.id-dash2-kpis{grid-template-columns:repeat(2,1fr)}}
.id-dkpi{text-align:center;padding:.55rem;border-radius:12px;border:1px solid var(--id-border)}
.id-dkpi-val{font-size:1.1rem;font-weight:800;background:var(--id-grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.id-dkpi-lbl{font-size:.58rem;opacity:.55;margin-top:.08rem}
.id-ds{display:inline-block;padding:.1rem .38rem;border-radius:6px;font-size:.6rem;font-weight:700}
.id-ds.exported{background:#d1fae5;color:#065f46}.id-ds.hitl{background:#fef3c7;color:#92400e}

/* ── Classroom ── */
.id-cls-outer{position:relative;max-width:960px;margin:0 auto}
.id-cls-wrap{overflow:hidden;border-radius:var(--id-radius);border:1px solid var(--id-border);
  background:var(--id-surface);backdrop-filter:blur(14px);box-shadow:var(--id-shadow-lg)}
.id-cls-slides{display:flex;transition:transform .45s cubic-bezier(.4,0,.2,1)}
.id-cls-slide{min-width:100%;padding:2rem 2.2rem;box-sizing:border-box}
.id-cls-slide h3{font-size:1.15rem;font-weight:800;margin-bottom:.9rem;line-height:1.3}
.id-cls-body{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}
@media(max-width:680px){.id-cls-body{grid-template-columns:1fr}}
.id-cls-lhs p{font-size:.83rem;opacity:.78;line-height:1.65;margin-bottom:.7rem}
.id-cls-rhs{border-radius:14px;border:1px solid var(--id-border);background:rgba(255,255,255,.5);
  padding:1.1rem;display:flex;flex-direction:column;gap:.6rem}
[data-theme="dark"] .id-cls-rhs{background:rgba(255,255,255,.04)}
.id-cls-fact{display:flex;align-items:flex-start;gap:.6rem;font-size:.8rem}
.id-cls-fact-icon{width:28px;height:28px;border-radius:9px;background:var(--id-grad);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:.65rem;flex-shrink:0;margin-top:.05rem}
.id-cls-fact-body strong{display:block;font-size:.82rem;margin-bottom:.1rem}
.id-cls-fact-body span{font-size:.75rem;opacity:.65}
.id-cls-nav{display:flex;justify-content:space-between;align-items:center;padding:.75rem 1.1rem;
  border-top:1px solid var(--id-border)}
.id-cls-btn{padding:.4rem 1.1rem;border-radius:20px;font-size:.78rem;font-weight:700;cursor:pointer;
  border:1.5px solid var(--id-border);background:var(--id-surface);color:var(--id-text);
  transition:all .2s}
.id-cls-btn:hover{background:rgba(20,184,166,.1);border-color:var(--id-teal);color:var(--id-teal)}
.id-cls-btn:disabled{opacity:.3;cursor:not-allowed}
.id-cls-dots{display:flex;gap:.45rem;align-items:center}
.id-cls-dot{width:8px;height:8px;border-radius:50%;background:var(--id-border);cursor:pointer;
  transition:all .25s}
.id-cls-dot.active{background:var(--id-teal);width:22px;border-radius:4px}
.id-cls-counter{font-size:.72rem;opacity:.5;font-weight:600}

/* ── Key Points ── */
.id-kp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:1.1rem;max-width:960px;margin:0 auto}
.id-kp-card{border-radius:var(--id-radius);border:1px solid var(--id-border);
  background:var(--id-surface);backdrop-filter:blur(12px);box-shadow:var(--id-shadow);
  padding:1.4rem;text-align:center;transition:transform .25s,box-shadow .25s;position:relative;overflow:hidden}
.id-kp-card:hover{transform:translateY(-5px);box-shadow:var(--id-shadow-lg)}
.id-kp-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--id-grad)}
.id-kp-card:nth-child(2)::before{background:var(--id-grad-v)}
.id-kp-card:nth-child(3)::before{background:var(--id-grad-a)}
.id-kp-card:nth-child(4)::before{background:var(--id-grad-g)}
.id-kp-metric{font-size:2rem;font-weight:900;line-height:1;margin-bottom:.4rem;
  background:var(--id-grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.id-kp-card:nth-child(2) .id-kp-metric{background:var(--id-grad-v);-webkit-background-clip:text;background-clip:text}
.id-kp-card:nth-child(3) .id-kp-metric{background:var(--id-grad-a);-webkit-background-clip:text;background-clip:text}
.id-kp-card:nth-child(4) .id-kp-metric{background:var(--id-grad-g);-webkit-background-clip:text;background-clip:text}
.id-kp-card h4{font-size:.82rem;font-weight:800;margin-bottom:.35rem}
.id-kp-card p{font-size:.75rem;opacity:.7;margin:0;line-height:1.5}

/* ── Code blocks ── */
.id-impl{max-width:960px;margin:0 auto}
.id-impl details{border-radius:14px;border:1px solid var(--id-border);background:var(--id-surface);
  backdrop-filter:blur(10px);margin-bottom:.85rem;overflow:hidden}
.id-impl summary{padding:.8rem 1.2rem;font-size:.83rem;font-weight:700;cursor:pointer;
  display:flex;align-items:center;gap:.55rem;list-style:none}
.id-impl summary::-webkit-details-marker{display:none}
.id-impl summary::before{content:'\25B6';font-size:.6rem;transition:transform .2s}
.id-impl details[open] summary::before{transform:rotate(90deg)}
.id-impl pre{margin:0;padding:1.1rem 1.3rem;background:#0f172a;color:#e2e8f0;font-size:.69rem;
  line-height:1.65;overflow-x:auto;border-top:1px solid var(--id-border);
  font-family:'Cascadia Code','JetBrains Mono',monospace}

/* ── About ── */
.id-about-card{border-radius:var(--id-radius);border:1px solid var(--id-border);
  background:var(--id-surface);backdrop-filter:blur(14px);box-shadow:var(--id-shadow-lg);
  padding:2rem;text-align:center;max-width:760px;margin:0 auto}
.id-about-card h3{font-size:1.15rem;font-weight:800;margin-bottom:.4rem}
.id-about-card p{font-size:.83rem;opacity:.72;margin-bottom:1.2rem;line-height:1.6}
.id-about-pills{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center;margin-bottom:1.4rem}
.id-about-pill{padding:.28rem .75rem;border-radius:999px;font-size:.72rem;font-weight:700}
.id-about-pill--t{background:rgba(20,184,166,.12);color:#0d9488}
.id-about-pill--b{background:rgba(59,130,246,.12);color:#2563eb}
.id-about-pill--v{background:rgba(139,92,246,.12);color:#7c3aed}
.id-about-pill--g{background:rgba(16,185,129,.12);color:#059669}
.id-about-pill--a{background:rgba(245,158,11,.12);color:#b45309}
.id-about-pill--r{background:rgba(239,68,68,.12);color:#dc2626}
.id-share-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.55rem 1.4rem;
  border-radius:22px;background:var(--id-grad);color:#fff;font-weight:700;font-size:.82rem;
  border:none;cursor:pointer;transition:opacity .2s,transform .2s}
.id-share-btn:hover{opacity:.87;transform:translateY(-2px)}

/* ── Responsive ── */
@media(max-width:640px){
  .id-cls-slide{padding:1.2rem 1rem}
  .id-kp-grid{grid-template-columns:1fr 1fr}
  .id-pip-bar{padding:.5rem .3rem}
  .id-pip{padding:0 .3rem}
}
</style>

<!-- ════ PROGRESS BAR ════ -->
<div class="id-progress"><div class="id-progress-fill" id="idProgressFill"></div></div>

<!-- ════ STICKY NAV ════ -->
<nav class="id-sticky-nav" id="id-sticky-nav">
  <div class="id-nav-inner">
    <button class="id-nav-tab active" onclick="idScrollTo('id-story')">Story</button>
    <button class="id-nav-tab" onclick="idScrollTo('id-demo')">Demo</button>
    <button class="id-nav-tab" onclick="idScrollTo('id-classroom')">Classroom</button>
    <button class="id-nav-tab" onclick="idScrollTo('id-keypoints')">Key Points</button>
    <button class="id-nav-tab" onclick="idScrollTo('id-code')">Code</button>
    <button class="id-nav-tab" onclick="idScrollTo('id-about')">About</button>
  </div>
</nav>

<div class="container-fluid" style="max-width:1100px;padding:0 1.2rem">

<!-- ════ HERO ════ -->
<section class="id-hero">
  <div class="id-badge"><i class="fas fa-brain"></i>&nbsp; Document AI</div>
  <h1>Intelligent Document<br>Processing</h1>
  <p class="lead">AI pipeline from ingestion through classification, dual-engine OCR, entity extraction,
    3-way validation, and active-learning HITL loop &#x2014; built for AP invoices, contracts, and compliance docs.</p>
  <div class="id-kpi-strip">
    <div class="id-kpi"><div><div class="id-kpi-val">97.2%</div><div class="id-kpi-lbl">Extraction Accuracy</div></div></div>
    <div class="id-kpi"><div><div class="id-kpi-val">4.8s</div><div class="id-kpi-lbl">Avg End-to-End</div></div></div>
    <div class="id-kpi"><div><div class="id-kpi-val">85%</div><div class="id-kpi-lbl">Straight-Through Rate</div></div></div>
    <div class="id-kpi"><div><div class="id-kpi-val">$142K</div><div class="id-kpi-lbl">Fraud Prevented / Year</div></div></div>
  </div>
</section>

<!-- ════ STORY ════ -->
<section class="id-sec" id="id-story">
  <div class="id-sec-head">
    <span class="id-tag id-tag--t">The Journey</span>
    <h2>From Document Chaos to Structured Data</h2>
    <p>Six stages that turned 15,000 documents per day from a manual bottleneck into an automated competitive advantage.</p>
  </div>
  <div class="id-story-steps">

    <div class="id-story-step">
      <div class="id-step-num">1</div>
      <h4>The Document Problem: 12 Types, 3 Channels</h4>
      <p>AP, Legal, and Compliance receive 15,000+ documents per day via email, SFTP, and web portals. PDFs, TIFFs,
        scanned handwritten forms, mixed-language invoices &#x2014; zero consistency across 200+ vendors.
        Eight people spent 6 hours daily just on data entry before anything was validated.</p>
      <div><span class="id-stat">15K</span><span class="id-stat-lbl"> docs/day &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">8</span><span class="id-stat-lbl"> FTEs on intake &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">12</span><span class="id-stat-lbl"> doc types</span></div>
    </div>

    <div class="id-story-step">
      <div class="id-step-num id-step-num--2">2</div>
      <h4>Classification First: LayoutLM Reads Layout Signals</h4>
      <p>Before extracting a single field, LayoutLM classifies every document. Unlike text-only classifiers,
        LayoutLM incorporates bounding-box coordinates &#x2014; so it recognizes that a large number in the top-right
        corner is a total amount, not a page number. 98.5% accuracy on 12 doc types in under 300ms.</p>
      <div><span class="id-stat">98.5%</span><span class="id-stat-lbl"> classification accuracy &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">&lt;0.3s</span><span class="id-stat-lbl"> per page</span></div>
    </div>

    <div class="id-story-step">
      <div class="id-step-num id-step-num--3">3</div>
      <h4>Multi-Engine OCR: Azure Primary, Tesseract Fallback</h4>
      <p>Azure Document Intelligence achieves 99.2% accuracy on clean prints but drops to 87% on handwritten
        annotations and faded receipts. Tesseract runs with adaptive deskew + binarization preprocessing on
        all low-confidence pages, recovering 40% of Azure failures. Combined accuracy: 97.2%.</p>
      <div><span class="id-stat">99.2%</span><span class="id-stat-lbl"> Azure clean &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">40%</span><span class="id-stat-lbl"> failures recovered</span></div>
    </div>

    <div class="id-story-step">
      <div class="id-step-num id-step-num--4">4</div>
      <h4>Structured Extraction: 18&#x2013;28 Fields Per Invoice</h4>
      <p>spaCy NER identifies vendor names, amounts, dates, PO numbers, and addresses. Azure&#x2019;s key-value
        extraction captures structured fields with confidence scores. Table parser reconstructs line items
        preserving row/column relationships. GPT-4o handles novel layouts that no template matches.</p>
      <div><span class="id-stat">18&#x2013;28</span><span class="id-stat-lbl"> fields per doc &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">97%</span><span class="id-stat-lbl"> field accuracy</span></div>
    </div>

    <div class="id-story-step">
      <div class="id-step-num id-step-num--5">5</div>
      <h4>3-Way Match + pHash: 8 Validation Rules in 1.5s</h4>
      <p>Every invoice is cross-referenced against Purchase Order and Goods Receipt before payment. Perceptual
        hashing (pHash) catches visually-identical re-submitted invoices even when filenames and numbers change &#x2014;
        a vector that exact-match dedup misses entirely. Catches 94% of AP fraud pre-payment.</p>
      <div><span class="id-stat">7.2%</span><span class="id-stat-lbl"> duplicates caught &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">$142K</span><span class="id-stat-lbl"> fraud prevented/yr</span></div>
    </div>

    <div class="id-story-step">
      <div class="id-step-num id-step-num--6">6</div>
      <h4>Active Learning: HITL Corrections Train the Model</h4>
      <p>Invoices below 95% confidence route to human review. Every correction becomes a labeled training
        example &#x2014; zero manual annotation. Weekly fine-tuning cycles with confidence-weighted loss
        (low-confidence errors count more). STP rate climbed from 67% to 85% over six months with no
        additional engineering effort.</p>
      <div><span class="id-stat">67%&#x2192;85%</span><span class="id-stat-lbl"> STP rate &nbsp;&#x2022;&nbsp; </span>
           <span class="id-stat">0</span><span class="id-stat-lbl"> manual labels</span></div>
    </div>

  </div>
</section>

<!-- ════ DEMO ════ -->
<section class="id-sec" id="id-demo">
  <div class="id-sec-head">
    <span class="id-tag id-tag--v">Interactive</span>
    <h2>Document Processing Demo</h2>
    <p>Select your lens: see what it means for your role, or step through the engineering pipeline.</p>
  </div>

  <!-- Mode toggle -->
  <div class="id-mode-toggle">
    <button class="id-mode-btn active" onclick="idSetMode('eli5')" id="idModeEli5">
      <i class="fas fa-users me-1"></i> Explain to Me
    </button>
    <button class="id-mode-btn" onclick="idSetMode('engineer')" id="idModeEng">
      <i class="fas fa-cogs me-1"></i> Engineering View
    </button>
  </div>

  <!-- ELI5 pane -->
  <div class="id-eli5-pane active" id="idEli5Pane">
    <div class="id-eli5-grid">

      <div class="id-eli5-card">
        <div class="id-eli5-icon" style="background:var(--id-grad)"><i class="fas fa-file-alt"></i></div>
        <div class="id-eli5-role">Document Processor</div>
        <h4>From 8 Hours of Typing to 90 Minutes of Reviewing</h4>
        <p>You used to manually type data from invoices into the ERP for 8 hours a day. Now the AI handles 85%
          automatically &#x2014; you only review the 15% where confidence is below 95%. That&#x2019;s roughly
          2,250 invoices per day handled without you. You review the 405 uncertain ones.</p>
        <div class="id-eli5-stat">
          <div class="val">90 min</div><div class="lbl">daily review time vs 8 hours</div>
        </div>
      </div>

      <div class="id-eli5-card">
        <div class="id-eli5-icon" style="background:var(--id-grad-v)"><i class="fas fa-gavel"></i></div>
        <div class="id-eli5-role">Legal Reviewer</div>
        <h4>Search Contracts Instead of Reading 200 PDFs</h4>
        <p>Every contract and compliance document gets structured extraction &#x2014; parties, effective dates,
          obligations, renewal terms, liability caps. You type &#x201C;contracts expiring this quarter with
          auto-renew clauses&#x201D; and get 12 matches in 0.3 seconds, instead of reading 200 PDFs over two days.</p>
        <div class="id-eli5-stat">
          <div class="val">0.3s</div><div class="lbl">vs 2-day manual review cycle</div>
        </div>
      </div>

      <div class="id-eli5-card">
        <div class="id-eli5-icon" style="background:var(--id-grad-b)"><i class="fas fa-server"></i></div>
        <div class="id-eli5-role">IT Manager</div>
        <h4>Serverless, Zero-VM, Scale to 100K Docs/Day</h4>
        <p>The pipeline is stateless Azure Functions with Redis queues. No VMs to provision, patch, or scale.
          Going from 2,500 to 25,000 documents per day means adjusting one queue concurrency parameter.
          Total infrastructure cost: $0.0031 per document processed end-to-end.</p>
        <div class="id-eli5-stat">
          <div class="val">$0.003</div><div class="lbl">per document, fully serverless</div>
        </div>
      </div>

      <div class="id-eli5-card">
        <div class="id-eli5-icon" style="background:var(--id-grad-g)"><i class="fas fa-project-diagram"></i></div>
        <div class="id-eli5-role">Data Engineer</div>
        <h4>Blob Trigger &#x2192; 7 Functions &#x2192; Full Lineage in Cosmos</h4>
        <p>Blob storage trigger &#x2192; Logic App router &#x2192; Queue &#x2192; 7 Azure Functions in sequence
          (classify, OCR, extract, validate, route, export, audit). Every field has a confidence score,
          bounding box, and source page logged. New doc types: retrain the LayoutLM classifier, zero pipeline changes.</p>
        <div class="id-eli5-stat">
          <div class="val">100%</div><div class="lbl">field-level lineage and audit trail</div>
        </div>
      </div>

    </div>
  </div>

  <!-- Engineer pane (IDP pipeline simulator) -->
  <div class="id-impl-pane" id="idEngPane">
    <div class="id-demo-shell">
      <div class="id-demo-bar">
        <div class="id-dots">
          <div class="id-dot id-dot--r"></div>
          <div class="id-dot id-dot--y"></div>
          <div class="id-dot id-dot--g"></div>
        </div>
        <h4><i class="fas fa-brain me-2" style="color:var(--id-teal)"></i>IDP Pipeline &#x2014; Live Simulator</h4>
        <div style="display:flex;gap:.5rem;flex-shrink:0">
          <button class="btn btn-sm" id="idBtnRun"
            style="border-radius:8px;font-size:.79rem;background:var(--id-teal);border-color:var(--id-teal);color:#fff">
            <i class="fas fa-play me-1"></i> Run Invoice
          </button>
          <button class="btn btn-outline-secondary btn-sm" id="idBtnReset"
            style="border-radius:8px;font-size:.79rem;display:none">
            <i class="fas fa-redo me-1"></i> Reset
          </button>
        </div>
      </div>

      <div class="id-pip-bar">
        <div class="id-pip" id="idPip0"><div class="id-pip-dot"><i class="fas fa-envelope"></i></div><div class="id-pip-lbl">Intake</div></div>
        <div class="id-pip" id="idPip1"><div class="id-pip-dot"><i class="fas fa-tags"></i></div><div class="id-pip-lbl">Classify</div></div>
        <div class="id-pip" id="idPip2"><div class="id-pip-dot"><i class="fas fa-eye"></i></div><div class="id-pip-lbl">OCR</div></div>
        <div class="id-pip" id="idPip3"><div class="id-pip-dot"><i class="fas fa-table"></i></div><div class="id-pip-lbl">Extract</div></div>
        <div class="id-pip" id="idPip4"><div class="id-pip-dot"><i class="fas fa-check-double"></i></div><div class="id-pip-lbl">Validate</div></div>
        <div class="id-pip" id="idPip5"><div class="id-pip-dot"><i class="fas fa-route"></i></div><div class="id-pip-lbl">Route</div></div>
        <div class="id-pip" id="idPip6"><div class="id-pip-dot"><i class="fas fa-file-export"></i></div><div class="id-pip-lbl">Export</div></div>
      </div>

      <div class="id-i-body">
        <div class="id-prev-pane">
          <div class="id-pane-lbl">Document Info</div>
          <div class="id-inv-card" id="idInvCard"></div>
          <div class="id-pane-lbl" style="margin-top:.2rem">Processing Log</div>
          <div class="id-log2" id="idLogArea"></div>
        </div>
        <div class="id-stage" id="idStage"></div>
      </div>
    </div>

    <div class="id-dash2" id="idDashboard">
      <div style="font-size:.84rem;font-weight:800;margin-bottom:.7rem">
        <i class="fas fa-chart-pie me-2" style="color:var(--id-teal)"></i>Processing Dashboard
      </div>
      <div class="id-dash2-kpis">
        <div class="id-dkpi"><div class="id-dkpi-val" id="idKpiDocs">0</div><div class="id-dkpi-lbl">Docs Processed</div></div>
        <div class="id-dkpi"><div class="id-dkpi-val" id="idKpiAcc">&#x2014;</div><div class="id-dkpi-lbl">Avg Accuracy</div></div>
        <div class="id-dkpi"><div class="id-dkpi-val" id="idKpiStp">&#x2014;</div><div class="id-dkpi-lbl">Straight-Through</div></div>
        <div class="id-dkpi"><div class="id-dkpi-val" id="idKpiTime">&#x2014;</div><div class="id-dkpi-lbl">Avg Time</div></div>
      </div>
      <div style="overflow-x:auto">
        <table class="table table-sm" style="font-size:.77rem;margin:0">
          <thead><tr style="opacity:.6">
            <th>Invoice</th><th>Vendor</th><th>Amount</th><th>Fields</th>
            <th>Accuracy</th><th>Status</th><th>Time</th>
          </tr></thead>
          <tbody id="idDashTable"></tbody>
        </table>
      </div>
    </div>
  </div>

</section>
'''

OUT.write_text(p1, encoding='utf-8')
print("id1 done")
