import os
path = r'boaapp\templates\boaapp\nfl_draft.html'
with open(path, 'w', encoding='utf-8') as f:
  f.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}thenumerix | NFL Fantasy Draft Analytics{% endblock %}
{% block content %}
<style>
/* ══════════════════════════════════════════════════════════════
   NFL FANTASY DRAFT — 7-Ideations Demo
   Wrapper: --nd-*   Simulator: --dr-* / --dfr-*
   ══════════════════════════════════════════════════════════════ */
:root{
  --nd-navy:#013369;--nd-red:#d50a0a;--nd-gold:#c9b037;
  --nd-text:#0f172a;--nd-muted:#64748b;--nd-card:#fff;
  --nd-border:rgba(0,0,0,.08);--nd-shadow:0 4px 24px rgba(0,0,0,.07);
  --nd-shadow-lg:0 12px 48px rgba(0,0,0,.13);--nd-radius:20px;
  --dr-blue:#3b82f6;--dr-violet:#8b5cf6;--dr-emerald:#10b981;
  --dr-amber:#f59e0b;--dr-rose:#ef4444;
  --dr-navy:#013369;--dr-red:#d50a0a;--dr-gold:#c9b037;
  --dr-surface:rgba(255,255,255,.92);--dr-border:rgba(0,0,0,.08);
  --dr-shadow:0 4px 24px rgba(0,0,0,.07);--dr-shadow-lg:0 12px 48px rgba(0,0,0,.13);
  --dfr-bg:#f0f2f5;--dfr-card:#fff;--dfr-text:#0f172a;--dfr-muted:#64748b;
  --dfr-header:#013369;--dfr-header-text:#fff;--dfr-accent:#3b82f6;
  --dfr-row-hover:rgba(59,130,246,.04);--dfr-user-bg:rgba(1,51,105,.06);
  --dfr-user-border:#013369;--dfr-timer-warn:#ef4444;
}
[data-theme="dark"]{
  --nd-text:#e2e8f0;--nd-muted:#94a3b8;--nd-card:#1a1f2e;--nd-border:rgba(255,255,255,.08);
  --nd-shadow:0 4px 24px rgba(0,0,0,.4);--nd-shadow-lg:0 12px 48px rgba(0,0,0,.6);
  --dr-surface:rgba(22,28,45,.92);--dr-border:rgba(255,255,255,.08);
  --dr-shadow:0 4px 24px rgba(0,0,0,.42);--dr-shadow-lg:0 12px 48px rgba(0,0,0,.58);
  --dfr-bg:#0f1219;--dfr-card:#1a1f2e;--dfr-text:#e2e8f0;--dfr-muted:#94a3b8;
  --dfr-header:#1e293b;--dfr-header-text:#e2e8f0;--dfr-accent:#60a5fa;
  --dfr-row-hover:rgba(59,130,246,.08);--dfr-user-bg:rgba(59,130,246,.1);
  --dfr-user-border:#60a5fa;
}
/* ── Keyframes ── */
@keyframes ndFadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes dfrFadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes dfrSlideIn{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}
@keyframes dfrPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
@keyframes dfrFlash{0%{background:rgba(59,130,246,.15)}100%{background:transparent}}
@keyframes dfrTimerWarn{0%,100%{color:var(--dfr-timer-warn)}50%{color:transparent}}
@keyframes dfrGlow{0%,100%{box-shadow:0 0 20px rgba(59,130,246,.3)}50%{box-shadow:0 0 40px rgba(59,130,246,.6)}}
/* ══ PROGRESS BAR ══ */
.nd-progress{position:fixed;top:0;left:0;width:100%;height:3px;z-index:1060;pointer-events:none}
.nd-progress-fill{height:3px;width:0;background:linear-gradient(90deg,#013369,#d50a0a,#c9b037);transition:width .25s}
/* ══ STICKY NAV ══ */
.nd-nav{position:sticky;top:0;z-index:1050;background:var(--nd-card);border-bottom:1px solid var(--nd-border);
  padding:.5rem 1rem;display:flex;gap:.25rem;overflow-x:auto}
.nd-nav::-webkit-scrollbar{display:none}
.nd-nav-item{display:inline-flex;align-items:center;gap:.35rem;padding:.38rem .85rem;border-radius:8px;
  border:1px solid transparent;font-size:.72rem;font-weight:700;cursor:pointer;text-decoration:none;
  color:var(--nd-muted);transition:all .2s;white-space:nowrap;font-family:inherit;background:transparent}
.nd-nav-item:hover{color:var(--nd-text);background:rgba(1,51,105,.05);text-decoration:none}
.nd-nav-item.active{background:var(--nd-navy);color:#fff;border-color:var(--nd-navy)}
[data-theme="dark"] .nd-nav-item.active{background:#3b82f6;border-color:#3b82f6}
.nd-nav-item i{font-size:.63rem}
/* ══ HERO ══ */
.nd-hero{max-width:780px;margin:3.5rem auto 2.5rem;padding:0 1.5rem;text-align:center;animation:ndFadeUp .6s ease both}
.nd-tag{display:inline-flex;align-items:center;gap:.35rem;padding:.3rem .75rem;border-radius:20px;
  background:linear-gradient(135deg,rgba(1,51,105,.08),rgba(213,10,10,.06));
  border:1px solid rgba(1,51,105,.15);font-size:.65rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.07em;color:var(--nd-navy);margin-bottom:1.1rem}
[data-theme="dark"] .nd-tag{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.12);color:#60a5fa}
.nd-hero h1{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:900;line-height:1.15;margin:0 0 .9rem;
  background:linear-gradient(135deg,#013369 0%,#d50a0a 55%,#013369 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
[data-theme="dark"] .nd-hero h1{background:linear-gradient(135deg,#e2e8f0,#d50a0a,#60a5fa);
  -webkit-background-clip:text;background-clip:text}
.nd-hero .lead{font-size:1rem;color:var(--nd-muted);line-height:1.65;max-width:560px;margin:0 auto 1.5rem}
.nd-kpi-strip{display:flex;justify-content:center;flex-wrap:wrap;gap:.5rem .8rem;margin:.8rem 0}
.nd-kpi{font-size:.68rem;font-weight:700;color:var(--nd-navy);
  background:rgba(1,51,105,.06);border:1px solid rgba(1,51,105,.12);border-radius:20px;padding:.28rem .75rem}
[data-theme="dark"] .nd-kpi{color:#60a5fa;background:rgba(59,130,246,.08);border-color:rgba(59,130,246,.15)}
/* ══ STORY ══ */
.nd-story{max-width:940px;margin:0 auto 3rem;padding:0 1.25rem}
.nd-section-label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--nd-red);margin-bottom:.45rem}
.nd-section-title{font-size:1.45rem;font-weight:900;margin:0 0 .35rem;color:var(--nd-text)}
.nd-section-sub{font-size:.87rem;color:var(--nd-muted);margin-bottom:1.8rem;line-height:1.6}
.nd-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
@media(max-width:700px){.nd-steps{grid-template-columns:1fr}}
@media(min-width:701px) and (max-width:920px){.nd-steps{grid-template-columns:1fr 1fr}}
.nd-step{background:var(--nd-card);border-radius:var(--nd-radius);border:1px solid var(--nd-border);
  padding:1.2rem;box-shadow:var(--nd-shadow);animation:ndFadeUp .5s ease both;transition:transform .2s}
.nd-step:hover{transform:translateY(-3px)}
.nd-step-icon{font-size:1.6rem;margin-bottom:.6rem;display:block}
.nd-step-num{font-size:.55rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;
  color:var(--nd-red);margin-bottom:.25rem}
.nd-step h3{font-size:.9rem;font-weight:800;margin:0 0 .4rem;color:var(--nd-text)}
.nd-step p{font-size:.76rem;color:var(--nd-muted);line-height:1.6;margin:0}
/* ══ DEMO SECTION ══ */
.nd-demo{max-width:1200px;margin:0 auto 3rem;padding:0 1.25rem}
.nd-mode-bar{display:flex;gap:.5rem;margin-bottom:1.5rem}
.nd-mode-btn{border:1px solid var(--nd-border);background:transparent;border-radius:10px;
  padding:.45rem 1.1rem;font-size:.8rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--nd-muted);transition:all .2s}
.nd-mode-btn.active{background:var(--nd-navy);color:#fff;border-color:var(--nd-navy)}
[data-theme="dark"] .nd-mode-btn.active{background:#3b82f6;border-color:#3b82f6}
.nd-pane{display:none}
.nd-pane.active{display:block}
/* ── ELI5 Pane ── */
.nd-eli5-wrap{text-align:center;padding:2rem 1rem}
.nd-eli5-wrap h3{font-size:1.15rem;font-weight:800;margin:0 0 .5rem;color:var(--nd-text)}
.nd-eli5-sub{color:var(--nd-muted);font-size:.85rem;margin-bottom:1.5rem}
.nd-persona-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:.75rem;
  max-width:560px;margin:0 auto 1.5rem;text-align:left}
@media(max-width:480px){.nd-persona-grid{grid-template-columns:1fr}}
.nd-persona{border:2px solid var(--nd-border);border-radius:14px;padding:1rem 1.1rem;cursor:pointer;
  background:var(--nd-card);transition:all .25s}
.nd-persona:hover{transform:translateY(-2px);box-shadow:var(--nd-shadow)}
.nd-persona.selected{border-color:var(--nd-navy);background:rgba(1,51,105,.04)}
[data-theme="dark"] .nd-persona.selected{border-color:#3b82f6;background:rgba(59,130,246,.08)}
.nd-persona-icon{font-size:1.5rem;margin-bottom:.4rem;display:block}
.nd-persona-name{font-size:.85rem;font-weight:800;margin:0 0 .2rem;color:var(--nd-text)}
.nd-persona-desc{font-size:.72rem;color:var(--nd-muted);line-height:1.5}
.nd-persona-strat{font-size:.62rem;font-weight:700;color:var(--nd-red);margin-top:.35rem}
.nd-eli5-btn{border:none;background:linear-gradient(135deg,#013369,#d50a0a);color:#fff;
  border-radius:12px;padding:.65rem 2rem;font-size:.9rem;font-weight:800;cursor:pointer;
  font-family:inherit;transition:transform .2s;box-shadow:0 6px 20px rgba(1,51,105,.25)}
.nd-eli5-btn:hover:not(:disabled){transform:translateY(-2px)}
.nd-eli5-btn:disabled{opacity:.4;cursor:default}
.nd-eli5-result{display:none;margin-top:1.5rem;text-align:left;max-width:680px;
  margin-left:auto;margin-right:auto}
.nd-eli5-picks{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:.5rem;margin-bottom:1rem}
.nd-eli5-pick{background:var(--nd-card);border:1px solid var(--nd-border);border-radius:12px;
  padding:.6rem .75rem;display:flex;align-items:center;gap:.5rem}
.nd-eli5-pick .rnd{font-size:.55rem;font-weight:800;color:var(--nd-muted);width:18px;flex-shrink:0}
.nd-eli5-pick .info .name{font-size:.72rem;font-weight:700;color:var(--nd-text)}
.nd-eli5-pick .info .meta{font-size:.6rem;color:var(--nd-muted)}
.nd-eli5-grade-card{background:var(--nd-card);border:1px solid var(--nd-border);border-radius:16px;
  padding:1rem 1.2rem;display:flex;align-items:center;gap:1rem;margin-top:.75rem}
.nd-eli5-grade-circle{width:56px;height:56px;border-radius:50%;
  background:linear-gradient(135deg,#013369,#d50a0a);color:#fff;
  font-size:1.3rem;font-weight:900;display:flex;align-items:center;justify-content:center;flex-shrink:0}
/* ── Engineer Pane ── */
.nd-pane[data-pane="engineer"] .dfr-room{min-height:600px;border-radius:12px;overflow:hidden}
/* ══ CLASSROOM ══ */
.nd-cls{max-width:940px;margin:0 auto 3rem;padding:0 1.25rem}
.nd-cls-wrap{border-radius:var(--nd-radius);overflow:hidden;border:1px solid var(--nd-border);
  background:var(--nd-card);box-shadow:var(--nd-shadow)}
.nd-cls-slides{position:relative;min-height:380px}
.nd-cls-slide{display:none;padding:1.8rem 2rem;animation:ndFadeUp .35s ease both}
.nd-cls-slide.active{display:block}
.nd-cls-slide-icon{font-size:2rem;margin-bottom:.6rem;display:block}
.nd-cls-slide-num{font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--nd-red);margin-bottom:.25rem}
.nd-cls-slide h3{font-size:1.15rem;font-weight:900;margin:0 0 .7rem;color:var(--nd-text)}
.nd-cls-slide p{font-size:.82rem;color:var(--nd-muted);line-height:1.7;margin:0 0 .8rem}
.nd-cls-nav{display:flex;align-items:center;justify-content:space-between;padding:.75rem 1.5rem;
  border-top:1px solid var(--nd-border)}
.nd-cls-dots{display:flex;gap:.4rem}
.nd-cls-dot{width:8px;height:8px;border-radius:50%;background:var(--nd-border);
  cursor:pointer;transition:all .2s;border:none;padding:0}
.nd-cls-dot.active{width:20px;border-radius:4px;background:var(--nd-navy)}
[data-theme="dark"] .nd-cls-dot.active{background:#3b82f6}
.nd-cls-btn{border:1px solid var(--nd-border);background:transparent;border-radius:8px;
  padding:.35rem .85rem;font-size:.72rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--nd-text);transition:all .2s}
.nd-cls-btn:hover{border-color:var(--nd-navy);color:var(--nd-navy)}
[data-theme="dark"] .nd-cls-btn:hover{border-color:#3b82f6;color:#3b82f6}
.nd-cls-code{background:#0f172a;border-radius:10px;padding:.8rem 1rem;font-size:.68rem;
  font-family:'Cascadia Code','JetBrains Mono',monospace;color:#e2e8f0;
  line-height:1.6;margin:.6rem 0;overflow-x:auto;white-space:pre}
.nd-cls-table{width:100%;border-collapse:collapse;font-size:.73rem;margin:.6rem 0}
.nd-cls-table th{font-size:.6rem;font-weight:700;text-transform:uppercase;color:var(--nd-muted);
  padding:.3rem .5rem;text-align:left;border-bottom:2px solid var(--nd-border)}
.nd-cls-table td{padding:.3rem .5rem;border-bottom:1px solid var(--nd-border)}
.nd-cls-table tr:last-child td{border-bottom:none}
.nd-strat-pill{display:inline-block;padding:.15rem .45rem;border-radius:5px;font-size:.6rem;
  font-weight:700;background:rgba(1,51,105,.08);color:var(--nd-navy)}
[data-theme="dark"] .nd-strat-pill{background:rgba(59,130,246,.1);color:#60a5fa}
/* ══ KEY POINTS ══ */
.nd-kps{max-width:940px;margin:0 auto 3rem;padding:0 1.25rem}
.nd-kps-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}
@media(max-width:600px){.nd-kps-grid{grid-template-columns:1fr}}
.nd-kp{background:var(--nd-card);border-radius:var(--nd-radius);border:1px solid var(--nd-border);
  padding:1.25rem;box-shadow:var(--nd-shadow);animation:ndFadeUp .5s ease both}
.nd-kp-icon{font-size:1.5rem;margin-bottom:.5rem;display:block}
.nd-kp-label{font-size:.55rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;
  color:var(--nd-red);margin-bottom:.25rem}
.nd-kp h4{font-size:.95rem;font-weight:800;margin:0 0 .4rem;color:var(--nd-text)}
.nd-kp p{font-size:.76rem;color:var(--nd-muted);line-height:1.65;margin:0}
/* ══ CODE SECTION ══ */
.nd-code{max-width:940px;margin:0 auto 3rem;padding:0 1.25rem}
.nd-code details{border-radius:14px;border:1px solid var(--nd-border);background:var(--nd-card);
  margin-bottom:.8rem;overflow:hidden}
.nd-code summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;
  display:flex;align-items:center;gap:.5rem;list-style:none;color:var(--nd-text)}
.nd-code summary::-webkit-details-marker{display:none}
.nd-code summary::before{content:'\25B6';font-size:.6rem;transition:transform .2s;color:var(--nd-muted)}
.nd-code details[open] summary::before{transform:rotate(90deg)}
.nd-code pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;
  line-height:1.6;overflow-x:auto;border-top:1px solid var(--nd-border);
  font-family:'Cascadia Code','JetBrains Mono',monospace}
/* ══ ABOUT ══ */
.nd-about{max-width:560px;margin:0 auto 3.5rem;padding:0 1.25rem;text-align:center}
.nd-about-card{background:var(--nd-card);border-radius:var(--nd-radius);border:1px solid var(--nd-border);
  padding:2rem 2rem 1.75rem;box-shadow:var(--nd-shadow)}
.nd-about-card h3{font-size:1.1rem;font-weight:800;margin:0 0 .5rem;color:var(--nd-text)}
.nd-about-card p{font-size:.82rem;color:var(--nd-muted);line-height:1.65;margin:0 0 1.2rem}
.nd-share-btn{border:none;background:linear-gradient(135deg,#013369,#d50a0a);color:#fff;
  border-radius:10px;padding:.5rem 1.4rem;font-size:.8rem;font-weight:700;cursor:pointer;
  font-family:inherit;transition:transform .2s}
.nd-share-btn:hover{transform:translateY(-1px)}
/* ══ EXISTING: Lobby ══ */
.dfr-lobby{max-width:800px;margin:0 auto;padding:2rem 1rem;text-align:center}
.dfr-lobby-hero{margin-bottom:2rem}
.dfr-lobby-icon{font-size:3rem;margin-bottom:.5rem}
.dfr-lobby-hero h1{font-size:2.2rem;font-weight:900;margin:0;
  background:linear-gradient(135deg,#013369 0%,#d50a0a 50%,#013369 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
[data-theme="dark"] .dfr-lobby-hero h1{background:linear-gradient(135deg,#e2e8f0,#d50a0a,#60a5fa);
  -webkit-background-clip:text;background-clip:text}
.dfr-lobby-hero p{font-size:.95rem;color:var(--dfr-muted);margin:.5rem 0 0}
.dfr-lobby-stats{display:flex;justify-content:center;gap:1.5rem;margin:1.2rem 0;flex-wrap:wrap}
.dfr-lobby-stat .val{font-size:1.4rem;font-weight:800;color:var(--dfr-accent)}
.dfr-lobby-stat .lbl{font-size:.65rem;color:var(--dfr-muted);text-transform:uppercase;letter-spacing:.05em}
.dfr-settings{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;max-width:650px;margin:0 auto 1.5rem;text-align:left}
@media(max-width:600px){.dfr-settings{grid-template-columns:1fr}}
.dfr-setting{background:var(--dfr-card);border:1px solid var(--dr-border);border-radius:14px;padding:1rem}
.dfr-setting label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  color:var(--dfr-muted);display:block;margin-bottom:.5rem}
.dfr-setting select{width:100%;border:1px solid var(--dr-border);border-radius:8px;padding:.45rem .5rem;
  font-size:.82rem;font-weight:600;background:var(--dfr-bg);font-family:inherit;color:var(--dfr-text)}
.dfr-fmt-btns{display:flex;border-radius:10px;border:1px solid var(--dr-border);overflow:hidden}
.dfr-fmt-btns button{flex:1;border:none;background:transparent;padding:.45rem;font-size:.75rem;
  font-weight:700;cursor:pointer;font-family:inherit;color:var(--dfr-text);opacity:.45;transition:all .2s}
.dfr-fmt-btns button.active{background:var(--dr-navy);color:#fff;opacity:1}
[data-theme="dark"] .dfr-fmt-btns button.active{background:#3b82f6}
.dfr-enter-btn{display:inline-flex;align-items:center;gap:.6rem;padding:.9rem 2.5rem;border:none;
  border-radius:14px;background:linear-gradient(135deg,#013369,#d50a0a);color:#fff;font-size:1.1rem;
  font-weight:800;font-family:inherit;cursor:pointer;letter-spacing:.03em;
  box-shadow:0 8px 32px rgba(1,51,105,.3);transition:all .3s;margin-bottom:2rem}
.dfr-enter-btn:hover{transform:translateY(-3px);box-shadow:0 12px 40px rgba(1,51,105,.4)}
.dfr-team-preview{margin-top:1rem}
.dfr-team-preview h3{font-size:.85rem;font-weight:700;color:var(--dfr-muted);margin-bottom:.8rem}
.dfr-team-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:.5rem;text-align:left}
.dfr-team-card{border-radius:10px;border:1px solid var(--dr-border);padding:.55rem .65rem;
  background:var(--dfr-card);display:flex;align-items:center;gap:.4rem;font-size:.72rem}
.dfr-team-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.dfr-team-card .name{font-weight:700;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dfr-team-card .strat{font-size:.58rem;color:var(--dfr-muted)}
/* ══ EXISTING: Draft Room ══ */
.dfr-room{display:flex;flex-direction:column;background:var(--dfr-bg);margin:-1rem -0.75rem;border-radius:0}
.dfr-topbar{display:flex;align-items:center;gap:.5rem;padding:.5rem .8rem;
  background:var(--dfr-header);color:var(--dfr-header-text);flex-shrink:0;flex-wrap:wrap}
.dfr-topbar-brand{font-weight:800;font-size:.8rem;display:flex;align-items:center;gap:.4rem;margin-right:.5rem}
.dfr-topbar-brand i{color:#d50a0a}
.dfr-round-badge{background:rgba(255,255,255,.12);border-radius:8px;padding:.25rem .6rem;font-size:.72rem;font-weight:700}
.dfr-pick-badge{background:rgba(255,255,255,.08);border-radius:8px;padding:.25rem .6rem;font-size:.68rem}
.dfr-otc{display:flex;align-items:center;gap:.5rem;flex:1;justify-content:center;min-width:200px}
.dfr-otc-label{font-size:.55rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.6}
.dfr-otc-team{font-size:1rem;font-weight:900;display:flex;align-items:center;gap:.4rem}
.dfr-otc-dot{width:14px;height:14px;border-radius:50%;border:2px solid rgba(255,255,255,.3)}
.dfr-timer{display:flex;align-items:center;gap:.3rem;padding:.2rem .7rem;border-radius:10px;
  background:rgba(255,255,255,.1);font-variant-numeric:tabular-nums}
.dfr-timer-val{font-size:1.5rem;font-weight:900;line-height:1}
.dfr-timer.warning .dfr-timer-val{color:#ef4444;animation:dfrPulse .5s ease infinite}
.dfr-topbar-controls{display:flex;align-items:center;gap:.4rem}
.dfr-top-btn{border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.08);border-radius:8px;
  padding:.3rem .6rem;font-size:.68rem;font-weight:700;color:#fff;cursor:pointer;font-family:inherit;
  transition:all .2s;display:flex;align-items:center;gap:.3rem}
.dfr-top-btn:hover{background:rgba(255,255,255,.15)}
.dfr-top-btn.active-toggle{background:rgba(59,130,246,.4);border-color:rgba(59,130,246,.6)}
.dfr-ticker{display:flex;align-items:center;gap:0;padding:.3rem .5rem;background:var(--dfr-card);
  border-bottom:1px solid var(--dr-border);overflow-x:auto;flex-shrink:0;min-height:44px}
.dfr-ticker::-webkit-scrollbar{height:3px}
.dfr-ticker::-webkit-scrollbar-thumb{background:var(--dr-border);border-radius:2px}
.dfr-tick{display:flex;flex-direction:column;align-items:center;padding:.2rem .35rem;
  border-radius:8px;min-width:58px;font-size:.58rem;text-align:center;flex-shrink:0;transition:all .2s}
.dfr-tick.current{background:var(--dfr-user-bg);border:1px solid var(--dfr-user-border);font-weight:700}
.dfr-tick.user-tick{border-bottom:2px solid var(--dr-navy)}
[data-theme="dark"] .dfr-tick.user-tick{border-bottom-color:#60a5fa}
.dfr-tick.done{opacity:.4}
.dfr-tick .tick-pick{font-size:.5rem;color:var(--dfr-muted)}
.dfr-tick .tick-team{font-weight:700;font-size:.62rem;white-space:nowrap}
.dfr-tick .tick-player{font-size:.52rem;color:var(--dfr-muted);white-space:nowrap;
  max-width:60px;overflow:hidden;text-overflow:ellipsis}
.dfr-tick-dot{width:8px;height:8px;border-radius:50%;margin-bottom:.1rem}
.dfr-tick-arr{color:var(--dfr-muted);font-size:.55rem;flex-shrink:0;padding:0 .1rem}
.dfr-main{display:grid;grid-template-columns:210px 1fr 230px;flex:1;overflow:hidden}
@media(max-width:900px){.dfr-main{grid-template-columns:180px 1fr 200px}}
@media(max-width:700px){.dfr-main{grid-template-columns:1fr;grid-template-rows:auto 1fr auto}}
.dfr-panel{display:flex;flex-direction:column;border-right:1px solid var(--dr-border);overflow:hidden}
.dfr-panel:last-child{border-right:none;border-left:1px solid var(--dr-border)}
.dfr-panel-hd{padding:.5rem .6rem;font-size:.68rem;font-weight:800;text-transform:uppercase;
  letter-spacing:.06em;background:var(--dfr-card);border-bottom:1px solid var(--dr-border);
  display:flex;align-items:center;justify-content:space-between}
.dfr-panel-hd i{margin-right:.3rem;opacity:.5}
.dfr-panel-hd .count{font-size:.6rem;opacity:.5;font-weight:600}
.dfr-roster{flex:1;overflow-y:auto;padding:.3rem;background:var(--dfr-card)}
.dfr-slot{display:flex;align-items:center;gap:.3rem;padding:.3rem .4rem;border-radius:8px;
  border:1px dashed var(--dr-border);margin-bottom:.2rem;min-height:34px;font-size:.66rem;transition:all .2s}
.dfr-slot.filled{border-style:solid;background:var(--dfr-row-hover)}
.dfr-slot.filled.just-drafted{animation:dfrFlash .6s ease}
.dfr-slot-pos{width:28px;font-weight:800;font-size:.6rem;text-align:center;flex-shrink:0}
.dfr-slot-pos.pos-qb{color:#dc2626}.dfr-slot-pos.pos-rb{color:#2563eb}
.dfr-slot-pos.pos-wr{color:#7c3aed}.dfr-slot-pos.pos-te{color:#059669}
.dfr-slot-pos.pos-k{color:#ca8a04}.dfr-slot-pos.pos-dst{color:#e11d48}
.dfr-slot-img{width:22px;height:22px;border-radius:50%;object-fit:cover;flex-shrink:0}
.dfr-slot-info{flex:1;min-width:0}
.dfr-slot-name{font-weight:700;font-size:.64rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dfr-slot-meta{font-size:.52rem;color:var(--dfr-muted)}
.dfr-slot-pts{font-weight:700;font-size:.6rem;flex-shrink:0}
.dfr-roster-footer{padding:.4rem .6rem;font-size:.65rem;font-weight:700;border-top:1px solid var(--dr-border);
  background:var(--dfr-card);display:flex;justify-content:space-between}
.dfr-players{display:flex;flex-direction:column;overflow:hidden;background:var(--dfr-bg)}
.dfr-toolbar{display:flex;align-items:center;gap:.5rem;padding:.4rem .6rem;background:var(--dfr-card);
  border-bottom:1px solid var(--dr-border);flex-wrap:wrap}
.dfr-search{border:1px solid var(--dr-border);border-radius:8px;padding:.35rem .55rem;font-size:.75rem;
  font-family:inherit;flex:1;min-width:120px;max-width:220px;background:var(--dfr-bg);color:var(--dfr-text)}
.dfr-search::placeholder{color:var(--dfr-muted)}
.dfr-pos-btns{display:flex;gap:.2rem}
.dfr-pos-btns button{border:1px solid var(--dr-border);background:transparent;border-radius:7px;
  padding:.2rem .45rem;font-size:.62rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--dfr-text);opacity:.45;transition:all .15s}
.dfr-pos-btns button.active{opacity:1;border-color:var(--dfr-accent);background:rgba(59,130,246,.08)}
.dfr-sort-lbl{font-size:.58rem;color:var(--dfr-muted);margin-left:auto}
.dfr-tbl-wrap{flex:1;overflow-y:auto;overflow-x:auto}
.dfr-tbl{width:100%;border-collapse:collapse;font-size:.7rem}
.dfr-tbl thead{position:sticky;top:0;z-index:2}
.dfr-tbl th{padding:.35rem .4rem;text-align:left;font-size:.58rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.05em;color:var(--dfr-muted);background:var(--dfr-card);border-bottom:2px solid var(--dr-border);
  white-space:nowrap;cursor:pointer;user-select:none}
.dfr-tbl th:hover{color:var(--dfr-text)}
.dfr-tbl th.sort-active{color:var(--dfr-accent)}
.dfr-tbl td{padding:.3rem .4rem;border-bottom:1px solid var(--dr-border);white-space:nowrap;vertical-align:middle}
.dfr-tbl tr{transition:background .15s}
.dfr-tbl tbody tr:hover{background:var(--dfr-row-hover)}
.dfr-tbl tbody tr.drafted{opacity:.25;text-decoration:line-through}
.dfr-tbl-name{display:flex;align-items:center;gap:.35rem}
.dfr-tbl-img{width:28px;height:28px;border-radius:50%;object-fit:cover;flex-shrink:0;background:#e2e8f0}
.dfr-tbl-player{font-weight:700}.dfr-tbl-stats{font-size:.55rem;color:var(--dfr-muted);max-width:140px;overflow:hidden;text-overflow:ellipsis}
.dr-pick-pos{padding:.1rem .35rem;border-radius:6px;font-size:.58rem;font-weight:700;display:inline-block}
.dr-pick-pos--qb{background:rgba(239,68,68,.12);color:#dc2626}
.dr-pick-pos--rb{background:rgba(59,130,246,.12);color:#2563eb}
.dr-pick-pos--wr{background:rgba(139,92,246,.12);color:#7c3aed}
.dr-pick-pos--te{background:rgba(16,185,129,.12);color:#059669}
.dr-pick-pos--k{background:rgba(234,179,8,.12);color:#ca8a04}
.dr-pick-pos--dst{background:rgba(244,63,94,.12);color:#e11d48}
.dfr-draft-btn{border:1px solid var(--dfr-accent);background:rgba(59,130,246,.08);border-radius:7px;
  padding:.2rem .5rem;font-size:.62rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--dfr-accent);transition:all .15s}
.dfr-draft-btn:hover{background:var(--dfr-accent);color:#fff}
.dfr-draft-btn:disabled{opacity:.2;cursor:default;background:transparent;color:var(--dfr-muted);border-color:var(--dr-border)}
.dfr-ctrl-bar{display:flex;align-items:center;gap:.5rem;padding:.35rem .6rem;border-top:1px solid var(--dr-border);
  background:var(--dfr-card);flex-wrap:wrap}
.dfr-ctrl-btn{border:1px solid var(--dr-border);background:var(--dfr-bg);border-radius:8px;
  padding:.25rem .55rem;font-size:.65rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--dfr-text);transition:all .15s;display:flex;align-items:center;gap:.25rem}
.dfr-ctrl-btn:hover{border-color:var(--dfr-accent);background:rgba(59,130,246,.05)}
.dfr-ctrl-btn.active{background:var(--dfr-accent);color:#fff;border-color:var(--dfr-accent)}
.dfr-ctrl-btn:disabled{opacity:.3;cursor:default}
.dfr-speed-grp{display:flex;align-items:center;gap:.15rem;margin-left:.3rem}
.dfr-speed-grp span{font-size:.6rem;color:var(--dfr-muted);font-weight:600}
.dfr-speed-btn{border:1px solid var(--dr-border);background:transparent;border-radius:6px;
  padding:.15rem .3rem;font-size:.65rem;cursor:pointer;transition:all .15s}
.dfr-speed-btn.active{background:var(--dfr-accent);color:#fff;border-color:var(--dfr-accent)}
.dfr-progress{flex:1;display:flex;align-items:center;gap:.3rem;justify-content:flex-end}
.dfr-progress-bar{width:120px;height:5px;background:var(--dr-border);border-radius:3px;overflow:hidden}
.dfr-progress-fill{height:100%;background:var(--dfr-accent);border-radius:3px;transition:width .3s}
.dfr-progress-text{font-size:.58rem;color:var(--dfr-muted);font-weight:600}
.dfr-feed{flex:1;overflow-y:auto;padding:.3rem;background:var(--dfr-card)}
.dfr-feed-item{display:flex;align-items:center;gap:.3rem;padding:.25rem .35rem;border-radius:7px;
  font-size:.62rem;margin-bottom:.15rem;animation:dfrSlideIn .25s ease both;transition:background .2s}
.dfr-feed-item:hover{background:var(--dfr-row-hover)}
.dfr-feed-item.user-feed{background:var(--dfr-user-bg);font-weight:700}
.dfr-feed-item.round-hd{font-weight:800;font-size:.58rem;color:var(--dfr-muted);text-transform:uppercase;
  letter-spacing:.06em;padding:.4rem .35rem .15rem;border-bottom:1px solid var(--dr-border);margin-bottom:.2rem}
.dfr-feed-num{width:20px;font-weight:800;font-size:.55rem;opacity:.3;flex-shrink:0;text-align:center}
.dfr-feed-img{width:20px;height:20px;border-radius:50%;object-fit:cover;flex-shrink:0}
.dfr-feed-info{flex:1;min-width:0}
.dfr-feed-name{font-weight:700;font-size:.62rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dfr-feed-meta{font-size:.5rem;color:var(--dfr-muted)}
.dfr-board-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.7);
  display:flex;align-items:center;justify-content:center;padding:1rem}
.dfr-board-modal{background:var(--dfr-card);border-radius:16px;max-width:95vw;max-height:90vh;
  overflow:auto;box-shadow:var(--dr-shadow-lg);width:100%}
.dfr-board-hd{display:flex;align-items:center;justify-content:space-between;padding:.7rem 1rem;
  border-bottom:1px solid var(--dr-border);position:sticky;top:0;background:var(--dfr-card);z-index:1}
.dfr-board-hd h4{font-size:.85rem;font-weight:800;margin:0}
.dfr-board-close{border:none;background:transparent;font-size:1.2rem;cursor:pointer;opacity:.5;color:var(--dfr-text)}
.dfr-board-close:hover{opacity:1}
.dfr-board-grid{display:grid;font-size:.58rem;padding:.5rem}
.dfr-board-cell{padding:.2rem .3rem;border:1px solid var(--dr-border);border-radius:4px;
  min-width:75px;text-align:center;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.dfr-board-cell.header{font-weight:800;background:var(--dfr-header);color:#fff;position:sticky;top:0}
.dfr-board-cell.round-hd{font-weight:700;background:var(--dfr-bg);position:sticky;left:0}
.dfr-board-cell.user-col{background:var(--dfr-user-bg)}
.dfr-board-cell.picked{font-weight:600}
.dfr-post{max-width:900px;margin:0 auto;padding:1.5rem 1rem}
.dfr-post-header{text-align:center;margin-bottom:1.5rem}
.dfr-post-header h2{font-size:1.5rem;font-weight:900;margin:0}
.dfr-post-header p{color:var(--dfr-muted);margin:.3rem 0 0}
.dfr-post-grade{display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;
  border-radius:50%;font-size:2rem;font-weight:900;margin:.8rem 0;
  background:linear-gradient(135deg,#013369,#d50a0a);color:#fff;box-shadow:0 8px 32px rgba(1,51,105,.3)}
.dfr-post-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;margin-bottom:1.2rem}
@media(max-width:600px){.dfr-post-kpis{grid-template-columns:repeat(2,1fr)}}
.dfr-post-kpi{text-align:center;padding:.6rem;border-radius:12px;border:1px solid var(--dr-border);background:var(--dfr-card)}
.dfr-post-kpi .val{font-size:1.1rem;font-weight:800;color:var(--dfr-accent)}
.dfr-post-kpi .lbl{font-size:.58rem;color:var(--dfr-muted);margin-top:.1rem}
.dfr-post-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}
@media(max-width:600px){.dfr-post-grid{grid-template-columns:1fr}}
.dfr-post-panel{border-radius:14px;border:1px solid var(--dr-border);padding:.8rem;background:var(--dfr-card)}
.dfr-post-panel h5{font-size:.78rem;font-weight:800;margin:0 0 .5rem}
.dfr-pos-bar{display:flex;align-items:center;gap:.35rem;margin-bottom:.3rem;font-size:.65rem}
.dfr-pos-bar-label{width:26px;font-weight:700;flex-shrink:0}
.dfr-pos-bar-track{flex:1;background:var(--dr-border);border-radius:4px;overflow:hidden;height:14px}
.dfr-pos-bar-fill{height:100%;border-radius:4px;transition:width .4s}
.dfr-pos-bar-val{font-weight:600;font-size:.6rem;color:var(--dfr-muted);width:32px;text-align:right}
.dfr-bye-grid{display:flex;gap:.2rem;flex-wrap:wrap}
.dfr-bye-cell{width:28px;height:28px;border-radius:6px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;border:1px solid var(--dr-border);font-size:.55rem;font-weight:700}
.dfr-bye-cell .wk{font-size:.42rem;color:var(--dfr-muted);font-weight:400}
.dfr-bye-cell.conflict{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);color:#dc2626}
.dfr-post-roster{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.3rem;margin-bottom:1rem}
.dfr-post-player{display:flex;align-items:center;gap:.3rem;padding:.3rem .4rem;border-radius:8px;
  border:1px solid var(--dr-border);background:var(--dfr-card);font-size:.66rem}
.dfr-post-player .rnd{font-size:.55rem;opacity:.3;width:16px;font-weight:700}
.dfr-post-player img{width:24px;height:24px;border-radius:50%;object-fit:cover}
.dfr-post-player .nm{font-weight:700;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dfr-post-player .pt{font-weight:600;font-size:.6rem;color:var(--dfr-muted)}
.dfr-post-table{width:100%;border-collapse:collapse;font-size:.7rem;margin-top:.5rem}
.dfr-post-table th{font-size:.58rem;font-weight:700;text-transform:uppercase;color:var(--dfr-muted);
  padding:.35rem .4rem;text-align:left;border-bottom:2px solid var(--dr-border)}
.dfr-post-table td{padding:.3rem .4rem;border-bottom:1px solid var(--dr-border)}
.dfr-post-table tr.user-row{background:var(--dfr-user-bg);font-weight:700}
.dfr-post-actions{display:flex;gap:.5rem;justify-content:center;margin-top:1rem;flex-wrap:wrap}
.dfr-action-btn{border:1px solid var(--dr-border);background:var(--dfr-card);border-radius:10px;
  padding:.45rem 1rem;font-size:.78rem;font-weight:700;cursor:pointer;font-family:inherit;
  color:var(--dfr-text);transition:all .2s;display:flex;align-items:center;gap:.3rem}
.dfr-action-btn:hover{border-color:var(--dfr-accent);background:rgba(59,130,246,.05)}
.dfr-action-btn.primary{background:var(--dr-navy);color:#fff;border-color:var(--dr-navy)}
.dfr-action-btn.primary:hover{background:#014a99}
</style>

<!-- ═══ PROGRESS BAR ═══ -->
<div class="nd-progress"><div class="nd-progress-fill" id="ndProgressFill"></div></div>

<!-- ═══ STICKY NAV ═══ -->
<nav class="nd-nav" aria-label="Section navigation">
  <a href="#nd-story"    class="nd-nav-item active" data-nav="nd-story"><i class="fas fa-football-ball"></i> Story</a>
  <a href="#nd-demo"     class="nd-nav-item"         data-nav="nd-demo"><i class="fas fa-play-circle"></i> Demo</a>
  <a href="#nd-classroom" class="nd-nav-item"        data-nav="nd-classroom"><i class="fas fa-chalkboard-teacher"></i> Classroom</a>
  <a href="#nd-keypoints" class="nd-nav-item"        data-nav="nd-keypoints"><i class="fas fa-lightbulb"></i> Key Points</a>
  <a href="#nd-code"     class="nd-nav-item"         data-nav="nd-code"><i class="fas fa-code"></i> Code</a>
  <a href="#nd-about"    class="nd-nav-item"         data-nav="nd-about"><i class="fas fa-user"></i> About</a>
</nav>

<!-- ═══ HERO ═══ -->
<section id="nd-story">
<div class="nd-hero">
  <div class="nd-tag"><i class="fas fa-football-ball me-1"></i> 7-IDEATIONS DEMO &middot; FANTASY DRAFT ANALYTICS</div>
  <h1>The Algorithm Behind<br>Every Pick.</h1>
  <p class="lead">A 12-team snake draft simulator powered by VOR-based ranking, 9 AI strategy archetypes, a real-time pick engine, and live NFL projections from SportsData.io.</p>
  <div class="nd-kpi-strip">
    <span class="nd-kpi">&#x1F4CA; 220+ Players</span>
    <span class="nd-kpi">&#x1F916; 9 AI Strategies</span>
    <span class="nd-kpi">&#x1F4C8; VOR-Ranked</span>
    <span class="nd-kpi">&#x26A1; Live API Data</span>
    <span class="nd-kpi">&#x1F3C6; Post-Draft Grade</span>
  </div>
</div>

<!-- ═══ STORY ═══ -->
<div class="nd-story">
  <div class="nd-section-label">The Story</div>
  <h2 class="nd-section-title">228 Picks. 9 Strategies. 1 Algorithm.</h2>
  <p class="nd-section-sub">What looks like a game is actually a multi-agent optimization problem &mdash; every AI bot runs a different strategy, reacts to positional scarcity, and competes on a shared ranking surface built from projected statistics.</p>
  <div class="nd-steps">
    <div class="nd-step">
      <span class="nd-step-icon">&#x1F4CA;</span>
      <div class="nd-step-num">Step 01</div>
      <h3>Player Pool Assembled</h3>
      <p>220+ players loaded with projected stats for 2026 &mdash; or live data from SportsData.io if available. Each player gets 5 raw stats mapped by position: pass yards, rush TDs, receptions, etc.</p>
    </div>
    <div class="nd-step">
      <span class="nd-step-icon">&#x1F522;</span>
      <div class="nd-step-num">Step 02</div>
      <h3>VOR Rankings Computed</h3>
      <p>Value Over Replacement normalizes fantasy points across positions. A RB scoring 280 pts outranks a QB at 350 pts once scarcity is factored &mdash; the drop-off from elite to replacement RBs is far steeper.</p>
    </div>
    <div class="nd-step">
      <span class="nd-step-icon">&#x1F916;</span>
      <div class="nd-step-num">Step 03</div>
      <h3>9 AI Archetypes Ready</h3>
      <p>Each bot runs a named strategy (Robust RB, Zero RB, Hero RB, TE Premium, Late QB, Stars &amp; Scrubs, Balanced BPA, Contrarian, Anchor RB) with distinct positional weight multipliers.</p>
    </div>
    <div class="nd-step">
      <span class="nd-step-icon">&#x26A1;</span>
      <div class="nd-step-num">Step 04</div>
      <h3>Snake Draft Executes</h3>
      <p>19 rounds, 12 teams, 228 picks. Pick order reverses each round &mdash; the snake format. A real-time engine fires picks with a configurable timer, live ticker, and feed showing every selection.</p>
    </div>
    <div class="nd-step">
      <span class="nd-step-icon">&#x1F4C9;</span>
      <div class="nd-step-num">Step 05</div>
      <h3>Positional Runs Emerge</h3>
      <p>When 3+ players at a position are drafted in a short window, the AI urgency multiplier kicks in for remaining players at that spot &mdash; simulating the cascading runs seen in real draft rooms.</p>
    </div>
    <div class="nd-step">
      <span class="nd-step-icon">&#x1F3C6;</span>
      <div class="nd-step-num">Step 06</div>
      <h3>Draft Grade Calculated</h3>
      <p>Post-draft analytics rank all 12 teams on starter projected points, total VOR captured, bye week concentration, and bench depth. Grades A+ through D are assigned by rank position.</p>
    </div>
  </div>
</div>
</section>

<!-- ═══ DEMO ═══ -->
<section id="nd-demo">
<div class="nd-demo">
  <div class="nd-section-label">Live Demo</div>
  <h2 class="nd-section-title">Try It: Two Ways to Explore</h2>
  <p class="nd-section-sub">ELI5 explains the draft strategy concept in plain English. Engineer mode runs the full 19-round simulator with live data, real-time pick feed, and post-draft analytics.</p>
  <div class="nd-mode-bar">
    <button class="nd-mode-btn active" data-mode="eli5" onclick="ndSetMode('eli5')">
      <i class="fas fa-comments me-1"></i> ELI5 &mdash; Explain It Simply
    </button>
    <button class="nd-mode-btn" data-mode="engineer" onclick="ndSetMode('engineer')">
      <i class="fas fa-cogs me-1"></i> Engineer &mdash; Full Simulator
    </button>
  </div>

  <!-- ELI5 PANE -->
  <div class="nd-pane active" data-pane="eli5">
    <div class="nd-eli5-wrap">
      <h3>Pick Your Draft Strategy</h3>
      <p class="nd-eli5-sub">Each archetype bets differently on where value hides. Pick one and see which players your algorithm would target in the first 8 rounds.</p>
      <div class="nd-persona-grid">
        <div class="nd-persona" id="nd-persona-casual" onclick="ndSelectPersona('casual')">
          <span class="nd-persona-icon">&#x1F3C8;</span>
          <div class="nd-persona-name">The Casual Fan</div>
          <div class="nd-persona-desc">Big names, run-first. Take elite RBs early and fill out from there.</div>
          <div class="nd-persona-strat">Strategy: Robust RB (RB weight: 1.55&times;)</div>
        </div>
        <div class="nd-persona" id="nd-persona-analyst" onclick="ndSelectPersona('analyst')">
          <span class="nd-persona-icon">&#x1F4CA;</span>
          <div class="nd-persona-name">The Analyst</div>
          <div class="nd-persona-desc">Pure algorithm. Best VOR available regardless of position.</div>
          <div class="nd-persona-strat">Strategy: Balanced BPA (all weights: 1.0&times;)</div>
        </div>
        <div class="nd-persona" id="nd-persona-zerorb" onclick="ndSelectPersona('zerorb')">
          <span class="nd-persona-icon">&#x26A1;</span>
          <div class="nd-persona-name">Zero RB</div>
          <div class="nd-persona-desc">Punt RBs early, stack elite WRs, find RBs on waivers.</div>
          <div class="nd-persona-strat">Strategy: Zero RB (RB weight: 0.45&times;, WR: 1.5&times;)</div>
        </div>
        <div class="nd-persona" id="nd-persona-contrarian" onclick="ndSelectPersona('contrarian')">
          <span class="nd-persona-icon">&#x1F3AF;</span>
          <div class="nd-persona-name">The Contrarian</div>
          <div class="nd-persona-desc">Fade the crowd. Target positions others ignore, find undervalued QBs and TEs.</div>
          <div class="nd-persona-strat">Strategy: Contrarian (QB: 1.15&times;, TE: 1.25&times;)</div>
        </div>
      </div>
      <button class="nd-eli5-btn" id="nd-eli5-run" onclick="ndRunELI5()" disabled>
        <i class="fas fa-bolt me-1"></i> Simulate My First 8 Picks
      </button>
      <div class="nd-eli5-result" id="nd-eli5-result"></div>
    </div>
  </div>

  <!-- ENGINEER PANE -->
  <div class="nd-pane" data-pane="engineer">
''')
