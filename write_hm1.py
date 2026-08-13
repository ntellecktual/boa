TMPL = 'boaapp/templates/boaapp/humana_mdm.html'
with open(TMPL, 'w', encoding='utf-8') as out:
    out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Healthcare MDM &mdash; Azure Databricks{% endblock %}
{% block container_class %}hm-shell{% endblock %}
{% block content %}
<style>
/* ============================================================
   HUMANA MDM PLATFORM — 7-Ideations Framework
   Azure Databricks + PySpark + Kafka + Delta Lake
   ============================================================ */
:root {
  --hm-blue:#0078d4;--hm-spark:#e8590c;--hm-emerald:#10b981;--hm-amber:#f59e0b;
  --hm-violet:#7c3aed;--hm-rose:#ef4444;--hm-teal:#0d9488;
  --hm-grad-main:linear-gradient(135deg,#0078d4 0%,#005a9e 50%,#003e6e 100%);
  --hm-grad-spark:linear-gradient(135deg,#e8590c,#b94400);
  --hm-grad-gold:linear-gradient(135deg,#f59e0b,#b45309);
  --hm-grad-bronze:linear-gradient(135deg,#92400e,#78350f);
  --hm-surface:rgba(255,255,255,.78);--hm-border:rgba(0,0,0,.08);
  --hm-shadow:0 4px 24px rgba(0,0,0,.07);--hm-shadow-lg:0 12px 48px rgba(0,0,0,.13);
  --hm-radius:18px;
}
[data-theme="dark"]{
  --hm-surface:rgba(15,23,42,.82);--hm-border:rgba(255,255,255,.08);
  --hm-shadow:0 4px 24px rgba(0,0,0,.45);--hm-shadow-lg:0 12px 48px rgba(0,0,0,.6);
}
@keyframes hmFadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes hmPulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes hmGlow{0%,100%{box-shadow:0 0 8px rgba(0,120,212,.25)}50%{box-shadow:0 0 22px rgba(0,120,212,.55)}}

/* ── Progress bar ── */
.hm-progress-track{position:fixed;top:0;left:0;right:0;height:3px;z-index:2000;background:rgba(0,0,0,.06)}
[data-theme="dark"] .hm-progress-track{background:rgba(255,255,255,.06)}
.hm-progress-fill{height:100%;width:0;background:linear-gradient(90deg,#0078d4,#e8590c,#f59e0b);transition:width .15s}

/* ── Sticky nav ── */
.hm-sticky-nav{position:sticky;top:56px;z-index:1100;background:var(--c-card,#fff);
  border-bottom:1px solid var(--hm-border);backdrop-filter:blur(12px)}
[data-theme="dark"] .hm-sticky-nav{background:rgba(15,23,42,.9)}
.hm-nav-inner{display:flex;gap:.2rem;padding:.45rem .75rem;overflow-x:auto;
  scrollbar-width:none;max-width:1100px;margin:0 auto}
.hm-nav-inner::-webkit-scrollbar{display:none}
.hm-nav-btn{flex-shrink:0;padding:.32rem .85rem;border-radius:999px;border:1px solid transparent;
  font-size:.72rem;font-weight:700;background:none;cursor:pointer;color:var(--c-text,#1e293b);
  transition:all .2s;white-space:nowrap}
.hm-nav-btn:hover,.hm-nav-btn.active{background:rgba(0,120,212,.1);
  border-color:rgba(0,120,212,.22);color:#0078d4}

/* ── Hero ── */
.hm-hero{text-align:center;padding:3rem 0 2.5rem;position:relative;overflow:hidden}
.hm-hero::before{content:'';position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 85% 50% at 50% -10%,rgba(0,120,212,.13) 0%,transparent 70%),
             radial-gradient(ellipse 40% 30% at 90% 110%,rgba(232,89,12,.08) 0%,transparent 60%)}
.hm-hero-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.28rem .9rem;
  border-radius:999px;background:rgba(0,120,212,.1);border:1px solid rgba(0,120,212,.22);
  font-size:.7rem;font-weight:700;color:#0078d4;text-transform:uppercase;
  letter-spacing:.07em;margin-bottom:.9rem}
.hm-hero h1{font-size:clamp(1.8rem,4vw,3rem);font-weight:800;line-height:1.1;margin-bottom:.7rem;
  background:linear-gradient(135deg,#1e3a5f 0%,#0078d4 40%,#e8590c 70%,#f59e0b 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
[data-theme="dark"] .hm-hero h1{background:linear-gradient(135deg,#93c5fd 0%,#60a5fa 40%,#fb923c 70%,#fcd34d 100%);
  -webkit-background-clip:text;background-clip:text}
.hm-hero .lead{font-size:.96rem;opacity:.68;max-width:640px;margin:0 auto 2rem}
.hm-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.85rem;
  max-width:860px;margin:0 auto 2.5rem}
@media(max-width:600px){.hm-kpis{grid-template-columns:repeat(2,1fr)}}
.hm-kpi{border-radius:16px;border:1px solid var(--hm-border);background:var(--hm-surface);
  backdrop-filter:blur(10px);padding:.9rem .6rem;text-align:center;
  box-shadow:var(--hm-shadow);animation:hmFadeUp .5s ease both}
.hm-kpi-val{font-size:1.5rem;font-weight:800;line-height:1;background:var(--hm-grad-main);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hm-kpi-val.spark{background:var(--hm-grad-spark);-webkit-background-clip:text;background-clip:text}
.hm-kpi-val.gold{background:var(--hm-grad-gold);-webkit-background-clip:text;background-clip:text}
.hm-kpi-lbl{font-size:.58rem;opacity:.52;margin-top:.2rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.05em}

/* ── Shared section utilities ── */
.hm-story,.hm-demo-section,.hm-classroom,.hm-keypoints,.hm-code-section,.hm-about{
  padding:2.5rem 0}
.hm-sec-head{text-align:center;margin-bottom:1.8rem}
.hm-sec-tag{display:inline-block;padding:.22rem .72rem;border-radius:999px;font-size:.63rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.5rem;
  background:rgba(0,120,212,.1);color:#0078d4;border:1px solid rgba(0,120,212,.18)}
.hm-sec-tag.spark{background:rgba(232,89,12,.1);color:#b94400;border-color:rgba(232,89,12,.18)}
.hm-sec-tag.gold{background:rgba(245,158,11,.1);color:#b45309;border-color:rgba(245,158,11,.18)}
.hm-sec-tag.violet{background:rgba(124,58,237,.1);color:#6d28d9;border-color:rgba(124,58,237,.18)}
.hm-sec-tag.emerald{background:rgba(16,185,129,.1);color:#059669;border-color:rgba(16,185,129,.18)}
.hm-sec-head h2{font-size:1.55rem;font-weight:800;margin-bottom:.3rem}
.hm-sec-head p{font-size:.87rem;opacity:.65;max-width:600px;margin:0 auto}

/* ── Story ── */
.hm-story-steps{display:flex;flex-direction:column;gap:1.1rem;max-width:860px;
  margin:0 auto;position:relative}
.hm-story-steps::before{content:'';position:absolute;left:27px;top:28px;bottom:28px;
  width:2px;background:linear-gradient(180deg,#0078d4,#e8590c,#f59e0b);opacity:.25}
@media(max-width:600px){.hm-story-steps::before{display:none}}
.hm-step-card{display:flex;gap:1rem;align-items:flex-start;border-radius:var(--hm-radius);
  border:1px solid var(--hm-border);background:var(--hm-surface);backdrop-filter:blur(8px);
  padding:1.1rem 1.2rem;box-shadow:var(--hm-shadow);transition:transform .2s,box-shadow .2s;
  animation:hmFadeUp .5s ease both}
.hm-step-card:hover{transform:translateY(-3px);box-shadow:var(--hm-shadow-lg)}
.hm-step-num{flex-shrink:0;width:42px;height:42px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;font-weight:800;font-size:.9rem;color:#fff;
  position:relative;z-index:1}
.hm-step-body{flex:1;min-width:0}
.hm-step-body h5{font-size:.92rem;font-weight:800;margin-bottom:.3rem}
.hm-step-body p{font-size:.8rem;opacity:.7;margin:0;line-height:1.55}
.hm-step-stat{font-size:.78rem;font-weight:800;padding:.2rem .55rem;border-radius:8px;
  margin-left:auto;flex-shrink:0;align-self:flex-start;margin-top:.1rem}

/* ── Demo section ── */
.hm-mode-toggle{display:flex;gap:.4rem;justify-content:center;margin-bottom:1.5rem}
.hm-mode-btn{padding:.4rem 1.1rem;border-radius:999px;border:1px solid var(--hm-border);
  font-size:.78rem;font-weight:700;background:none;cursor:pointer;
  color:var(--c-text,#1e293b);transition:all .2s}
.hm-mode-btn.active{background:rgba(0,120,212,.1);border-color:rgba(0,120,212,.28);color:#0078d4}
.hm-pane{display:none}.hm-pane.active{display:block}

/* ELI5 pane */
.hm-eli5-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:.9rem;max-width:980px;margin:0 auto}
.hm-eli5-card{border-radius:var(--hm-radius);border:1px solid var(--hm-border);
  background:var(--hm-surface);backdrop-filter:blur(8px);padding:1.1rem;
  box-shadow:var(--hm-shadow);cursor:pointer;transition:all .2s}
.hm-eli5-card:hover,.hm-eli5-card.active{border-color:rgba(0,120,212,.35);
  box-shadow:0 0 0 3px rgba(0,120,212,.1),var(--hm-shadow-lg)}
.hm-eli5-icon{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:.95rem;color:#fff;margin-bottom:.7rem}
.hm-eli5-card h6{font-size:.82rem;font-weight:800;margin-bottom:.25rem}
.hm-eli5-card .eli5-q{font-size:.75rem;opacity:.6;margin-bottom:.5rem;font-style:italic;
  line-height:1.4}
.hm-eli5-answer{font-size:.76rem;line-height:1.6;opacity:.75;display:none;margin-top:.3rem}
.hm-eli5-card.active .hm-eli5-answer{display:block;opacity:1}
.eli5-run-btn{margin-top:.7rem;padding:.28rem .7rem;border-radius:8px;
  border:1px solid rgba(0,120,212,.22);background:rgba(0,120,212,.07);
  font-size:.7rem;font-weight:700;color:#0078d4;cursor:pointer;display:none}
.hm-eli5-card.active .eli5-run-btn{display:inline-flex;align-items:center;gap:.3rem}

/* Engineer pane — original MDM demo */
.hm-demo{border-radius:22px;border:1px solid var(--hm-border);background:var(--hm-surface);
  backdrop-filter:blur(14px);box-shadow:var(--hm-shadow-lg);overflow:hidden;
  max-width:980px;margin:0 auto}
.hm-demo-bar{padding:.85rem 1.3rem;display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--hm-border);gap:.8rem;flex-wrap:wrap;
  background:rgba(0,120,212,.04)}
.hm-demo-bar h4{font-size:.88rem;font-weight:800;margin:0;flex:1}
.hm-dots{display:flex;gap:.35rem}.hm-dot{width:11px;height:11px;border-radius:50%}
.hm-pip-bar{display:flex;align-items:center;justify-content:center;gap:0;
  padding:.75rem 1rem;border-bottom:1px solid var(--hm-border);flex-wrap:wrap}
.hm-pip{display:flex;flex-direction:column;align-items:center;gap:.25rem;
  position:relative;padding:0 .65rem}
.hm-pip::after{content:'';position:absolute;top:15px;left:calc(50% + 18px);
  width:calc(100% - 12px);height:2px;background:var(--hm-border)}
.hm-pip:last-child::after{display:none}
.hm-pip-dot{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.65rem;background:var(--hm-surface);
  border:2px solid var(--hm-border);color:#94a3b8;transition:all .35s;
  position:relative;z-index:1}
.hm-pip-lbl{font-size:.56rem;font-weight:700;opacity:.5;white-space:nowrap}
.hm-pip.active .hm-pip-dot{border-color:#0078d4;background:rgba(0,120,212,.12);
  color:#0078d4;box-shadow:0 0 0 4px rgba(0,120,212,.12);
  animation:hmPulse 1.2s ease-in-out infinite}
.hm-pip.done .hm-pip-dot{border-color:#10b981;background:#10b981;color:#fff}
.hm-pip.done .hm-pip-lbl,.hm-pip.active .hm-pip-lbl{opacity:1}
.hm-split{display:grid;grid-template-columns:215px 1fr;gap:0;min-height:260px}
@media(max-width:680px){.hm-split{grid-template-columns:1fr}}
.hm-side{border-right:1px solid var(--hm-border);padding:.75rem;font-size:.72rem;
  overflow-y:auto;max-height:480px}
.hm-side-lbl{font-size:.56rem;font-weight:800;text-transform:uppercase;
  letter-spacing:.07em;opacity:.42;margin-bottom:.3rem}
.hm-ctx-card{border-radius:10px;border:1px solid var(--hm-border);
  padding:.5rem .65rem;margin-bottom:.38rem;font-size:.68rem;
  opacity:0;transition:opacity .35s}
.hm-ctx-card.vis{opacity:1}
.hm-ctx-row{display:flex;justify-content:space-between;font-size:.64rem;padding:.08rem 0}
.hm-ctx-row .lbl{opacity:.55}.hm-ctx-row .val{font-weight:600}
.hm-dbody{padding:.8rem;overflow-y:auto;max-height:480px}
.hm-step{border-radius:14px;border:1px solid var(--hm-border);
  background:rgba(255,255,255,.55);padding:.85rem 1rem;margin-bottom:.6rem;
  animation:hmFadeUp .35s ease both}
[data-theme="dark"] .hm-step{background:rgba(255,255,255,.04)}
.hm-step--ok{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.05)}
.hm-step h6{font-size:.82rem;font-weight:800;margin-bottom:.4rem}
.hm-chk{display:flex;align-items:center;gap:.4rem;font-size:.75rem;
  margin-bottom:.28rem;opacity:0;transition:opacity .3s}
.hm-chk.show{opacity:1}
.hm-chk .pass{color:#10b981;font-size:.7rem}
.hm-chk .pending{color:#0078d4;font-size:.68rem}
.hm-log{font-family:monospace;font-size:.64rem;line-height:1.5;max-height:110px;
  overflow-y:auto;padding:.35rem;background:rgba(0,0,0,.03);border-radius:8px;
  margin:.4rem .8rem .8rem}
[data-theme="dark"] .hm-log{background:rgba(255,255,255,.03)}
.hm-dash{border-radius:16px;border:1px solid var(--hm-border);background:var(--hm-surface);
  backdrop-filter:blur(12px);box-shadow:var(--hm-shadow);padding:1rem 1.3rem;
  max-width:980px;margin:1rem auto 0;display:none}
.hm-dash-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin-bottom:.75rem}
@media(max-width:560px){.hm-dash-kpis{grid-template-columns:repeat(2,1fr)}}
.hm-dkpi{text-align:center;padding:.5rem;border-radius:12px;border:1px solid var(--hm-border)}
.hm-dkpi-val{font-size:1.05rem;font-weight:800;background:var(--hm-grad-main);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hm-dkpi-val.spark{background:var(--hm-grad-spark);-webkit-background-clip:text;background-clip:text}
.hm-dkpi-val.gold{background:var(--hm-grad-gold);-webkit-background-clip:text;background-clip:text}
.hm-dkpi-lbl{font-size:.56rem;opacity:.52;margin-top:.06rem}

/* ── Classroom ── */
.hm-cls-wrap{max-width:860px;margin:0 auto}
.hm-cls-progress{display:flex;justify-content:center;gap:.4rem;margin-bottom:1.4rem;flex-wrap:wrap}
.hm-cls-dot{width:8px;height:8px;border-radius:50%;border:2px solid rgba(0,120,212,.3);
  background:transparent;cursor:pointer;transition:all .2s}
.hm-cls-dot.active{background:#0078d4;border-color:#0078d4}
.hm-cls-stage{border-radius:22px;border:1px solid var(--hm-border);background:var(--hm-surface);
  backdrop-filter:blur(12px);box-shadow:var(--hm-shadow-lg);overflow:hidden;min-height:290px}
.hm-cls-head{padding:1.2rem 1.5rem 0}
.hm-cls-badge{display:inline-block;padding:.2rem .6rem;border-radius:8px;font-size:.6rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.5rem;
  background:rgba(0,120,212,.1);color:#0078d4}
.hm-cls-head h3{font-size:1.2rem;font-weight:800;margin-bottom:.3rem}
.hm-cls-head p{font-size:.83rem;opacity:.65;margin-bottom:1rem}
.hm-cls-body{padding:0 1.5rem 1.2rem}
.hm-cls-footer{display:flex;align-items:center;justify-content:space-between;
  padding:.8rem 1.5rem;border-top:1px solid var(--hm-border)}
.hm-cls-counter{font-size:.7rem;opacity:.5;font-weight:700}
.hm-cls-nav{display:flex;gap:.5rem}
.hm-cls-nav button{padding:.3rem .85rem;border-radius:8px;border:1px solid var(--hm-border);
  background:none;font-size:.75rem;font-weight:700;cursor:pointer;transition:all .18s}
.hm-cls-nav button:hover{background:rgba(0,120,212,.1);border-color:rgba(0,120,212,.25);color:#0078d4}
.hm-cls-slide{display:none}.hm-cls-slide.active{display:block}
.hm-cls-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.65rem}
.hm-cls-item{padding:.7rem .85rem;border-radius:12px;border:1px solid var(--hm-border);font-size:.77rem}
.hm-cls-item .ci-label{font-size:.6rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.06em;opacity:.5;margin-bottom:.25rem}
.hm-cls-item .ci-val{font-weight:700}
.hm-cls-item .ci-note{font-size:.68rem;opacity:.6;margin-top:.15rem}
.hm-cls-arch{display:flex;flex-wrap:wrap;align-items:center;
  justify-content:center;gap:.35rem;padding:.5rem 0}
.hm-cls-arch-box{border-radius:10px;padding:.45rem .75rem;text-align:center;
  border:1px solid var(--hm-border);min-width:70px}
.hm-cls-arch-box .ba-lbl{font-size:.52rem;font-weight:800;text-transform:uppercase;
  letter-spacing:.06em;opacity:.5}
.hm-cls-arch-box .ba-name{font-size:.72rem;font-weight:700}
.hm-cls-arch-arrow{font-size:.7rem;opacity:.35}
.hm-vs-row{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin-top:.6rem}
.hm-vs-pill{padding:.18rem .5rem;border-radius:6px;font-size:.67rem;font-weight:700}
.hm-vs-pill--win{background:rgba(16,185,129,.12);color:#059669}
.hm-vs-pill--lose{background:rgba(100,116,139,.12);color:#64748b}
.hm-vs-sep{opacity:.35;font-weight:800;font-size:.75rem}

/* ── Key Points ── */
.hm-kp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:1rem;max-width:980px;margin:0 auto}
.hm-kp-card{border-radius:var(--hm-radius);border:1px solid var(--hm-border);
  background:var(--hm-surface);backdrop-filter:blur(8px);padding:1.2rem;
  box-shadow:var(--hm-shadow);transition:transform .2s,box-shadow .2s}
.hm-kp-card:hover{transform:translateY(-3px);box-shadow:var(--hm-shadow-lg)}
.hm-kp-icon{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:.92rem;color:#fff;margin-bottom:.8rem}
.hm-kp-stat{font-size:1.5rem;font-weight:800;line-height:1;margin-bottom:.25rem}
.hm-kp-card h6{font-size:.82rem;font-weight:800;margin-bottom:.35rem}
.hm-kp-card p{font-size:.75rem;opacity:.7;margin:0;line-height:1.55}

/* ── Code section ── */
.hm-impl{max-width:960px;margin:0 auto}
.hm-impl details{border-radius:14px;border:1px solid var(--hm-border);
  background:var(--hm-surface);margin-bottom:.8rem;overflow:hidden}
.hm-impl summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;
  display:flex;align-items:center;gap:.5rem;list-style:none}
.hm-impl summary::-webkit-details-marker{display:none}
.hm-impl summary::before{content:'\25B6';font-size:.6rem;transition:transform .2s}
.hm-impl details[open] summary::before{transform:rotate(90deg)}
.hm-impl pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;
  font-size:.68rem;line-height:1.6;overflow-x:auto;
  border-top:1px solid rgba(255,255,255,.06);
  font-family:'Cascadia Code','JetBrains Mono',monospace}
.ck{color:#7dd3fc}.cv{color:#6ee7b7}.cs{color:#fcd34d}
.cc{color:#64748b;font-style:italic}.cn{color:#f9a8d4}.cm{color:#fb923c}

/* ── About ── */
.hm-about-card{border-radius:22px;border:1px solid var(--hm-border);
  background:var(--hm-surface);backdrop-filter:blur(12px);
  box-shadow:var(--hm-shadow-lg);padding:2rem;max-width:820px;
  margin:0 auto;text-align:center}
.hm-about-card h3{font-size:1.3rem;font-weight:800;margin-bottom:.5rem}
.hm-about-card p{font-size:.85rem;opacity:.72;max-width:640px;
  margin:0 auto 1.4rem;line-height:1.65}
.hm-share-actions{display:flex;gap:.7rem;justify-content:center;flex-wrap:wrap}
.hm-share-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.55rem 1.4rem;
  border-radius:999px;font-size:.8rem;font-weight:700;cursor:pointer;transition:all .2s;border:none}
.hm-share-btn--primary{background:linear-gradient(135deg,#0078d4,#005a9e);color:#fff}
.hm-share-btn--primary:hover{opacity:.88;transform:translateY(-2px)}
.hm-share-btn--secondary{background:none;border:1px solid var(--hm-border);
  color:var(--c-text,#1e293b)}
.hm-share-btn--secondary:hover{background:rgba(0,120,212,.07);
  border-color:rgba(0,120,212,.22)}
.hm-pills-wrap{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center;margin:1.2rem 0}
.hm-pill{padding:.22rem .65rem;border-radius:999px;font-size:.7rem;font-weight:700}
.hm-pill--az{background:rgba(0,120,212,.1);color:#0078d4}
.hm-pill--db{background:rgba(232,89,12,.1);color:#b94400}
.hm-pill--kf{background:rgba(30,30,30,.08);color:#334155}
[data-theme="dark"] .hm-pill--kf{color:#94a3b8}
.hm-pill--g{background:rgba(16,185,129,.1);color:#059669}
.hm-pill--v{background:rgba(124,58,237,.1);color:#6d28d9}
.hm-pill--t{background:rgba(13,148,136,.1);color:#0d9488}
</style>

<!-- Progress Bar -->
<div class="hm-progress-track"><div class="hm-progress-fill" id="hmProgressFill"></div></div>

<!-- Sticky Nav -->
<nav class="hm-sticky-nav" id="hmStickyNav">
  <div class="hm-nav-inner">
    <button class="hm-nav-btn active" onclick="window.hmScrollTo('hm-story')"><i class="fas fa-book-open me-1"></i>Story</button>
    <button class="hm-nav-btn" onclick="window.hmScrollTo('hm-demo')"><i class="fas fa-play-circle me-1"></i>Demo</button>
    <button class="hm-nav-btn" onclick="window.hmScrollTo('hm-classroom')"><i class="fas fa-graduation-cap me-1"></i>Classroom</button>
    <button class="hm-nav-btn" onclick="window.hmScrollTo('hm-keypoints')"><i class="fas fa-lightbulb me-1"></i>Key Points</button>
    <button class="hm-nav-btn" onclick="window.hmScrollTo('hm-code')"><i class="fas fa-code me-1"></i>Code</button>
    <button class="hm-nav-btn" onclick="window.hmScrollTo('hm-about')"><i class="fas fa-share-alt me-1"></i>About</button>
  </div>
</nav>

<!-- ==================== HERO ==================== -->
<section class="hm-hero">
  <div class="hm-hero-badge"><i class="fas fa-database me-1"></i> Azure Databricks &middot; MDM Platform &middot; Healthcare</div>
  <h1>Enterprise Member<br>Data Management</h1>
  <p class="lead">High-performance MDM pipelines on Azure Databricks &mdash; unifying 8.4M member records across 11 source systems into a single golden record using PySpark, Delta Lake, and Apache Kafka.</p>
  <div class="hm-kpis">
    <div class="hm-kpi"><div class="hm-kpi-val">8.4M</div><div class="hm-kpi-lbl">Member Records</div></div>
    <div class="hm-kpi"><div class="hm-kpi-val spark">99.7%</div><div class="hm-kpi-lbl">Golden Record Accuracy</div></div>
    <div class="hm-kpi"><div class="hm-kpi-val gold">11</div><div class="hm-kpi-lbl">Source Systems</div></div>
    <div class="hm-kpi"><div class="hm-kpi-val">340ms</div><div class="hm-kpi-lbl">Avg Ingest Latency</div></div>
  </div>
</section>

<!-- ==================== STORY ==================== -->
<section class="hm-story" id="hm-story">
  <div class="hm-sec-head">
    <span class="hm-sec-tag"><i class="fas fa-book-open me-1"></i> The Story</span>
    <h2>From 11 Fragmented Systems to One Golden Record</h2>
    <p>How probabilistic MDM eliminated duplicate patient identities across a 40M-member healthcare network &mdash; and why 19 percentage points of match recall is a patient safety issue.</p>
  </div>
  <div class="hm-story-steps">

    <div class="hm-step-card" style="animation-delay:.05s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#6d28d9,#4c1d95)">1</div>
      <div class="hm-step-body">
        <h5>The 8.4M-Record Problem</h5>
        <p>Humana's member database held 8.4 million records &mdash; but cross-system analysis revealed 1.2 million duplicate identities spanning Epic EHR, Salesforce CRM, enrollment services, claims adjudication, and six legacy systems. James Worthington appeared in four systems with four different addresses, two dates of birth, and three phone numbers. A medication allergy documented in Epic could not surface in the claims or CRM systems. Fragmented identity was a patient safety risk, not just a data quality metric.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(239,68,68,.1);color:#ef4444">1.2M dupes</div>
    </div>

    <div class="hm-step-card" style="animation-delay:.1s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#0078d4,#005a9e)">2</div>
      <div class="hm-step-body">
        <h5>11 Upstream Sources &mdash; Zero Agreed Truth</h5>
        <p>Epic EHR (trust 0.97), Salesforce CRM (0.92), enrollment services (0.95), claims adjudication (0.88), provider directory (0.80), and six legacy systems each claimed authority over member data. No single system was right for all attributes &mdash; Epic was authoritative for clinical data; enrollment services for plan IDs; USPS CASS for validated addresses. The architecture needed attribute-level election, not record-level takeover. Source trust scores, derived from field-by-field accuracy audits, drove the survivorship engine.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(0,120,212,.1);color:#0078d4">11 sources</div>
    </div>

    <div class="hm-step-card" style="animation-delay:.15s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#92400e,#78350f)">3</div>
      <div class="hm-step-body">
        <h5>Kafka Streaming + Medallion Architecture</h5>
        <p>Apache Kafka (Azure Event Hubs) streams member update events from all 11 systems &mdash; 2,847 events per micro-batch, Avro-encoded with Schema Registry contracts enforced at every topic boundary. Auto Loader lands events immutably in the Bronze Delta table with Change Data Feed enabled for incremental processing. The Silver layer applies 47 PySpark DQ expectations &mdash; dropping null member IDs, quarantining invalid ZIPs, standardizing phone numbers to E.164 &mdash; then enriches addresses via USPS CASS geospatial broadcast join on a 32K-row reference table.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(146,64,14,.1);color:#92400e">47 DQ rules</div>
    </div>

    <div class="hm-step-card" style="animation-delay:.2s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)">4</div>
      <div class="hm-step-body">
        <h5>Probabilistic Entity Resolution &mdash; Splink Fellegi-Sunter</h5>
        <p>Deterministic rules alone (exact name + DOB match) achieved 78% recall &mdash; missing 22% of real duplicate pairs due to name variations ("Jon" vs "Jonathan"), address reformats, and transcription errors endemic to healthcare data entry. Splink's Fellegi-Sunter model, trained on 500K labeled pairs, evaluates Levenshtein distance on names, exact match on DOB and ZIP, and phone similarity &mdash; computing match probability as sigmoid of summed log-likelihood ratios. At a 0.85 threshold the model achieves 97% recall. That 19-point gain corrects 1.9 million previously missed patient identity links.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(124,58,237,.1);color:#7c3aed">97% recall</div>
    </div>

    <div class="hm-step-card" style="animation-delay:.25s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#b45309,#92400e)">5</div>
      <div class="hm-step-body">
        <h5>Survivorship &mdash; Electing the Golden Record</h5>
        <p>Once entity clusters form, the Gold-layer survivorship engine elects the highest-trust value for each attribute independently. James Worthington's first name comes from Epic (trust 0.97), his plan ID from enrollment services (0.95), his email from Salesforce CRM (0.92), and his validated address from the USPS CASS broadcast join. Every golden record field carries source lineage, confidence score, and timestamp &mdash; enabling field-level audit trails required for CMS network adequacy reporting and HIPAA compliance reviews.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(245,158,11,.1);color:#b45309">99.7% acc.</div>
    </div>

    <div class="hm-step-card" style="animation-delay:.3s">
      <div class="hm-step-num" style="background:linear-gradient(135deg,#10b981,#059669)">6</div>
      <div class="hm-step-body">
        <h5>Results &mdash; 91% Auto-Remediation, Zero PHI Copies</h5>
        <p>The MDM platform processes 2.8M events nightly in under 4 minutes on a 4-node Databricks Job Cluster at ~$18/run. Isolation Forest anomaly detection auto-remediates 91% of DQ exceptions, eliminating 3 FTE data steward roles. Unity Catalog row-level security and column masking enable clinical and non-clinical consumers to share a single gold table &mdash; eliminating 4 manually-maintained de-identified copies. The C# NuGet SDK cut downstream integration time from three-week projects to three-day integrations across 14 consuming systems.</p>
      </div>
      <div class="hm-step-stat" style="background:rgba(16,185,129,.1);color:#059669">91% auto-fix</div>
    </div>

  </div>
</section>

<!-- ==================== DEMO ==================== -->
<section class="hm-demo-section" id="hm-demo">
  <div class="hm-sec-head">
    <span class="hm-sec-tag spark"><i class="fas fa-play-circle me-1"></i> Interactive Demo</span>
    <h2>Explore the MDM Pipeline</h2>
    <p>Walk through the pipeline in plain English across four stakeholder perspectives, or run the full live Azure Databricks simulator.</p>
  </div>

  <div class="hm-mode-toggle">
    <button class="hm-mode-btn active" onclick="window.hmSetMode('eli5')"><i class="fas fa-user me-1"></i>ELI5 &mdash; Plain English</button>
    <button class="hm-mode-btn" onclick="window.hmSetMode('eng')"><i class="fas fa-cog me-1"></i>Engineer &mdash; Live Pipeline</button>
  </div>

  <!-- ELI5 Pane -->
  <div class="hm-pane active" id="hmELI5Pane">
    <div class="hm-eli5-grid">

      <div class="hm-eli5-card" onclick="window.hmToggleELI5(this)">
        <div class="hm-eli5-icon" style="background:linear-gradient(135deg,#0078d4,#005a9e)"><i class="fas fa-user-md"></i></div>
        <h6>Clinician</h6>
        <div class="eli5-q">"Why does my patient have 3 records in the system?"</div>
        <div class="hm-eli5-answer">When James Worthington enrolled online, the CRM created ID CRM-8847. When he had surgery, Epic assigned EHR-4421. When his plan renewed, enrollment created ENR-2291. The MDM engine detects all three share the same date of birth (1978-03-14), ZIP code (40202), and Levenshtein-distance-1 name variants &mdash; and clusters them into enterprise ID HMN-8847201. Now his medication allergy from EHR-4421 surfaces in every downstream system, not just Epic. Without MDM, a prescribing physician in the claims system would never see that allergy flag.</div>
        <button class="eli5-run-btn" onclick="window.hmSetMode('eng');event.stopPropagation()"><i class="fas fa-play me-1"></i>See it run</button>
      </div>

      <div class="hm-eli5-card" onclick="window.hmToggleELI5(this)">
        <div class="hm-eli5-icon" style="background:linear-gradient(135deg,#e8590c,#b94400)"><i class="fas fa-database"></i></div>
        <h6>Data Architect</h6>
        <div class="eli5-q">"How does Splink handle fuzzy matching at 8M-member scale?"</div>
        <div class="hm-eli5-answer">Splink uses Fellegi-Sunter probabilistic matching. Blocking rules reduce 70 trillion candidate pairs to 8.2M via last_name+zip and dob+zip predicates. For each candidate pair, it computes per-column match weights: Levenshtein distance for names mapped to log-likelihood ratios, exact match for DOB/ZIP. Match probability = sigmoid(sum of log-likelihood ratios). "Jon Smith" vs "Jonathan Smith" scores 0.82 alone &mdash; but with matching DOB and ZIP it scores 0.94, clearing the 0.85 threshold. Deterministic rules would reject the first case entirely, producing a phantom duplicate.</div>
        <button class="eli5-run-btn" onclick="window.hmSetMode('eng');event.stopPropagation()"><i class="fas fa-play me-1"></i>Run pipeline</button>
      </div>

      <div class="hm-eli5-card" onclick="window.hmToggleELI5(this)">
        <div class="hm-eli5-icon" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)"><i class="fas fa-chart-line"></i></div>
        <h6>IT Director</h6>
        <div class="eli5-q">"What's the cost, and what ROI does this generate?"</div>
        <div class="hm-eli5-answer">Before MDM: 11 ADF nightly batch jobs, 4-hour data lag, $14M/year in data steward labor to manually resolve DQ issues. After: Kafka micro-batch (5-min lag), DLT pipeline with 47 automated expectations, 91% auto-remediation. The 4-node Databricks cluster runs the full 2.8M-event nightly load in under 4 minutes at ~$18/run. The 91% automation rate eliminated 3 FTE analyst roles ($540K/year salary savings). The C# SDK cut downstream integration from 3-week projects to 3-day integrations &mdash; compounding ROI across 14 consuming systems. Break-even at 7 months.</div>
        <button class="eli5-run-btn" onclick="window.hmSetMode('eng');event.stopPropagation()"><i class="fas fa-play me-1"></i>Run pipeline</button>
      </div>

      <div class="hm-eli5-card" onclick="window.hmToggleELI5(this)">
        <div class="hm-eli5-icon" style="background:linear-gradient(135deg,#ef4444,#b91c1c)"><i class="fas fa-shield-alt"></i></div>
        <h6>Compliance Officer</h6>
        <div class="eli5-q">"How do we prove HIPAA compliance across all 14 consumers?"</div>
        <div class="hm-eli5-answer">Unity Catalog enforces three layered controls: (1) Row-level security &mdash; a SQL predicate policy filters PHI rows for roles without HIPAA training certification, enforced at the query engine level, not application code. (2) Column masking &mdash; SSN, DOB, and diagnosis codes are obfuscated for non-clinical consumers: they see "***-**-6712" instead of the real SSN. (3) Audit trail &mdash; every SELECT on PHI columns is logged in Unity Catalog's system.access.audit table, queryable for CMS audit submissions. Before MDM: 4 de-identified copies maintained manually. After MDM: one gold table, zero copies, automated monthly audit report.</div>
        <button class="eli5-run-btn" onclick="window.hmSetMode('eng');event.stopPropagation()"><i class="fas fa-play me-1"></i>Run pipeline</button>
      </div>

    </div>
  </div>

  <!-- Engineer Pane -->
  <div class="hm-pane" id="hmEngPane">
    <div class="hm-demo" id="hmDemo">
      <div class="hm-demo-bar">
        <div class="hm-dots">
          <div class="hm-dot" style="background:#ef4444"></div>
          <div class="hm-dot" style="background:#f59e0b"></div>
          <div class="hm-dot" style="background:#10b981"></div>
        </div>
        <h4><i class="fas fa-database me-2" style="color:#0078d4"></i>Member MDM Pipeline &middot; Azure Databricks &middot; Delta Live Tables</h4>
        <div style="display:flex;gap:.4rem;flex-shrink:0">
          <button class="btn btn-primary btn-sm" id="hmBtnRun" style="border-radius:8px;font-size:.78rem;background:#0078d4;border-color:#0078d4"><i class="fas fa-play me-1"></i> Run Pipeline</button>
          <button class="btn btn-outline-secondary btn-sm" id="hmBtnReset" style="border-radius:8px;font-size:.78rem;display:none"><i class="fas fa-redo me-1"></i> Reset</button>
        </div>
      </div>
      <div class="hm-pip-bar" id="hmPipBar">
        <div class="hm-pip" id="hmPip0"><div class="hm-pip-dot"><i class="fas fa-rss"></i></div><div class="hm-pip-lbl">Kafka Ingest</div></div>
        <div class="hm-pip" id="hmPip1"><div class="hm-pip-dot"><i class="fas fa-layer-group"></i></div><div class="hm-pip-lbl">Bronze</div></div>
        <div class="hm-pip" id="hmPip2"><div class="hm-pip-dot"><i class="fas fa-filter"></i></div><div class="hm-pip-lbl">Silver / DQ</div></div>
        <div class="hm-pip" id="hmPip3"><div class="hm-pip-dot"><i class="fas fa-link"></i></div><div class="hm-pip-lbl">Entity Link</div></div>
        <div class="hm-pip" id="hmPip4"><div class="hm-pip-dot"><i class="fas fa-trophy"></i></div><div class="hm-pip-lbl">Golden Record</div></div>
        <div class="hm-pip" id="hmPip5"><div class="hm-pip-dot"><i class="fas fa-share-alt"></i></div><div class="hm-pip-lbl">API Egress</div></div>
      </div>
      <div class="hm-split">
        <div class="hm-side">
          <div class="hm-side-lbl">Pipeline Context</div>
          <div class="hm-ctx-card" id="hmCtx0">
            <div style="font-weight:700;margin-bottom:.25rem"><i class="fas fa-rss me-1" style="color:#0078d4"></i>Kafka Batch</div>
            <div class="hm-ctx-row"><span class="lbl">Events</span><span class="val">2,847</span></div>
            <div class="hm-ctx-row"><span class="lbl">Topics</span><span class="val">5 sources</span></div>
            <div class="hm-ctx-row"><span class="lbl">Format</span><span class="val">Avro</span></div>
          </div>
          <div class="hm-ctx-card" id="hmCtx1">
            <div style="font-weight:700;margin-bottom:.25rem"><i class="fas fa-hospital me-1" style="color:#7c3aed"></i>Source Mix</div>
            <div class="hm-ctx-row"><span class="lbl">Epic EHR</span><span class="val" id="hmSrcEhr">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Salesforce</span><span class="val" id="hmSrcCrm">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Enrollment</span><span class="val" id="hmSrcEnr">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Claims</span><span class="val" id="hmSrcClm">&mdash;</span></div>
          </div>
          <div class="hm-ctx-card" id="hmCtx2">
            <div style="font-weight:700;margin-bottom:.25rem"><i class="fas fa-check-circle me-1" style="color:#10b981"></i>DQ Summary</div>
            <div class="hm-ctx-row"><span class="lbl">Passed</span><span class="val" id="hmDqPass">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Quarantined</span><span class="val" id="hmDqQuar">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Rejected</span><span class="val" id="hmDqFail">&mdash;</span></div>
          </div>
          <div class="hm-ctx-card" id="hmCtx3">
            <div style="font-weight:700;margin-bottom:.25rem"><i class="fas fa-link me-1" style="color:#f59e0b"></i>Entity Resolution</div>
            <div class="hm-ctx-row"><span class="lbl">Matched</span><span class="val" id="hmMatched">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">New Members</span><span class="val" id="hmNew">&mdash;</span></div>
            <div class="hm-ctx-row"><span class="lbl">Conflicts</span><span class="val" id="hmConflict">&mdash;</span></div>
          </div>
        </div>
        <div class="hm-dbody" id="hmStage"></div>
      </div>
      <div class="hm-log" id="hmLog"></div>
    </div>
    <div class="hm-dash" id="hmDash">
      <div style="font-size:.82rem;font-weight:800;margin-bottom:.7rem"><i class="fas fa-chart-bar me-2" style="color:#0078d4"></i>Pipeline Metrics</div>
      <div class="hm-dash-kpis">
        <div class="hm-dkpi"><div class="hm-dkpi-val" id="hmKpiRows">0</div><div class="hm-dkpi-lbl">Records Processed</div></div>
        <div class="hm-dkpi"><div class="hm-dkpi-val spark" id="hmKpiGolden">&mdash;</div><div class="hm-dkpi-lbl">Golden Records</div></div>
        <div class="hm-dkpi"><div class="hm-dkpi-val gold" id="hmKpiDq">&mdash;</div><div class="hm-dkpi-lbl">DQ Pass Rate</div></div>
        <div class="hm-dkpi"><div class="hm-dkpi-val" id="hmKpiTime">&mdash;</div><div class="hm-dkpi-lbl">Pipeline Time</div></div>
      </div>
      <div style="overflow-x:auto">
        <table class="table table-sm" style="font-size:.73rem;margin:0">
          <thead><tr style="opacity:.55"><th>Run</th><th>Source</th><th>Events</th><th>DQ Pass</th><th>Golden</th><th>Matched</th><th>Time</th></tr></thead>
          <tbody id="hmRunTable"></tbody>
        </table>
      </div>
    </div>
  </div>
</section>
''')
print('hm1 done')
