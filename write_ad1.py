"""write_ad1.py — anomaly_detection.html 7-ideations redesign (part 1 of 2)"""
TMPL = r'''boaapp/templates/boaapp/anomaly_detection.html'''
out = open(TMPL, 'w', encoding='utf-8')
out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Real-Time Anomaly Detection{% endblock %}
{% block container_class %}anom-shell{% endblock %}
{% block content %}
<style>
/* ══ existing anom vars ══ */
.anom-shell{display:block;width:100%;max-width:100%;padding:0}
:root{--anom-accent:#06b6d4;--anom-accent2:#0891b2;--anom-surface:#fff;--anom-card:#fff;--anom-border:rgba(0,0,0,.07);--anom-shadow:0 2px 12px rgba(0,0,0,.06);--anom-muted:#6b7280}
[data-theme="dark"]{--anom-surface:rgba(10,20,30,.97);--anom-card:rgba(10,20,30,.97);--anom-border:rgba(255,255,255,.08);--anom-shadow:0 2px 12px rgba(0,0,0,.35);--anom-muted:#94a3b8}
@keyframes anomUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes anomPulse{0%,100%{opacity:1}50%{opacity:.4}}
.anom-wrap{max-width:1200px;margin:0 auto;padding:0 1.5rem 3rem}
.anom-hero{text-align:center;padding:1.4rem 0 1rem;animation:anomUp .4s ease both}
.anom-tag{display:inline-block;padding:.22rem .85rem;border-radius:999px;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;background:rgba(6,182,212,.09);border:1px solid rgba(6,182,212,.2);color:var(--anom-accent);margin-bottom:.65rem}
.anom-hero h1{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:800;background:linear-gradient(135deg,#06b6d4,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.3rem}
.anom-hero p{font-size:.84rem;color:var(--anom-muted);max-width:560px;margin:0 auto;line-height:1.6}
.anom-body{display:grid;grid-template-columns:1fr 300px;gap:1rem;margin-top:1rem}
@media(max-width:860px){.anom-body{grid-template-columns:1fr}}
.anom-panel{background:var(--anom-surface);border:1px solid var(--anom-border);border-radius:16px;box-shadow:var(--anom-shadow);padding:1.1rem;min-height:0;overflow:hidden}
.anom-chart-wrap{position:relative;width:100%;height:220px}
.anom-panel-hd{display:flex;align-items:center;gap:.45rem;font-size:.75rem;font-weight:800;margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:1px solid var(--anom-border)}
.anom-panel-hd i{color:var(--anom-accent);opacity:.8}
.anom-status-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin-bottom:.85rem}
@media(max-width:600px){.anom-status-grid{grid-template-columns:repeat(2,1fr)}}
.anom-stat{background:rgba(6,182,212,.04);border:1px solid rgba(6,182,212,.12);border-radius:10px;padding:.55rem .65rem;text-align:center}
.anom-stat-val{font-size:1.1rem;font-weight:900;color:var(--anom-accent);line-height:1;font-family:'Cascadia Code',monospace}
.anom-stat-lbl{font-size:.58rem;text-transform:uppercase;letter-spacing:.05em;font-weight:600;color:var(--anom-muted);margin-top:.2rem}
.anom-stat.is-alert .anom-stat-val{color:#ef4444;animation:anomPulse .8s infinite}
.anom-controls{display:flex;flex-wrap:wrap;align-items:center;gap:.55rem;margin-bottom:.85rem}
.anom-btn{display:inline-flex;align-items:center;gap:.4rem;padding:.38rem .95rem;border-radius:9px;font-size:.72rem;font-weight:700;border:none;cursor:pointer;transition:all .18s;white-space:nowrap}
.anom-btn--start{background:linear-gradient(135deg,#06b6d4,#3b82f6);color:#fff}
.anom-btn--start.is-running{background:linear-gradient(135deg,#64748b,#475569)}
.anom-btn--spike{background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.25);color:#d97706}
.anom-btn--drift{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:#dc2626}
.anom-btn--reset{background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);color:#6366f1}
.anom-btn:hover{transform:translateY(-1px);opacity:.88}
.anom-algo-group{display:flex;gap:.3rem;background:var(--anom-border);border-radius:9px;padding:2px}
.anom-algo-btn{padding:.28rem .7rem;border-radius:7px;font-size:.65rem;font-weight:700;border:none;cursor:pointer;background:transparent;color:var(--anom-muted);transition:all .18s}
.anom-algo-btn.active{background:var(--anom-surface);color:var(--anom-accent);box-shadow:0 1px 4px rgba(0,0,0,.1)}
.anom-log{height:300px;overflow-y:auto;background:rgba(0,0,0,.03);border-radius:10px;padding:.65rem;font-size:.65rem;font-family:'Cascadia Code',monospace;line-height:1.6}
[data-theme="dark"] .anom-log{background:rgba(255,255,255,.03)}
.anom-log-entry{padding:.2rem 0;border-bottom:1px solid var(--anom-border);display:flex;gap:.5rem}
.anom-log-entry:last-child{border:none}
.anom-log-time{opacity:.4;white-space:nowrap}
.anom-log-msg{color:#ef4444;font-weight:600}
.anom-log-msg.warn{color:#f59e0b}
.anom-log-empty{text-align:center;opacity:.35;padding-top:1rem}
.anom-drift-badge{display:none;font-size:.65rem;font-weight:700;padding:.2rem .6rem;border-radius:999px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);color:#dc2626;animation:anomPulse 1s infinite}
.anom-drift-badge.visible{display:inline-block}
.anom-leg{display:flex;flex-wrap:wrap;gap:.65rem;font-size:.65rem;color:var(--anom-muted);margin-top:.5rem}
.anom-leg-item{display:flex;align-items:center;gap:.3rem}
.anom-leg-dot{width:20px;height:3px;border-radius:2px}

/* ══ 7-ideations wrapper CSS ══ */
:root{--ad-accent:#06b6d4;--ad-text:#0f172a;--ad-muted:#64748b;--ad-surface:#fff;--ad-border:rgba(0,0,0,.07);--ad-radius:16px}
[data-theme="dark"]{--ad-text:#f1f5f9;--ad-surface:rgba(10,20,30,.97);--ad-border:rgba(255,255,255,.08)}
/* progress bar */
.ad-progress{position:fixed;top:0;left:0;right:0;height:3px;background:rgba(6,182,212,.15);z-index:9999}
.ad-progress-fill{height:100%;background:linear-gradient(90deg,#06b6d4,#3b82f6);width:0%;transition:width .2s}
/* sticky nav */
.ad-nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--ad-border);display:flex;gap:0;overflow-x:auto;padding:0 1rem}
[data-theme="dark"] .ad-nav{background:rgba(10,20,30,.92)}
.ad-nav-btn{flex-shrink:0;padding:.7rem 1rem;font-size:.72rem;font-weight:700;border:none;background:transparent;color:var(--ad-muted);cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;letter-spacing:.03em}
.ad-nav-btn.active{color:var(--ad-accent);border-bottom-color:var(--ad-accent)}
/* section anchors */
.ad-section{padding:2rem 0;min-height:40vh}
/* story steps */
.ad-story-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin-top:1.5rem}
.ad-step{background:var(--ad-surface);border:1px solid var(--ad-border);border-radius:var(--ad-radius);padding:1.1rem 1.2rem;position:relative}
.ad-step-num{font-size:.6rem;font-weight:800;color:var(--ad-accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem}
.ad-step h4{font-size:.82rem;font-weight:800;margin-bottom:.35rem}
.ad-step p{font-size:.72rem;color:var(--ad-muted);line-height:1.6;margin:0}
/* ELI5 / Engineer mode */
.ad-mode-bar{display:flex;gap:.5rem;margin-bottom:1.5rem;justify-content:center}
.ad-mode-btn{padding:.45rem 1.4rem;border-radius:999px;font-size:.78rem;font-weight:700;border:2px solid var(--ad-border);background:transparent;color:var(--ad-muted);cursor:pointer;transition:all .2s}
.ad-mode-btn.active{background:var(--ad-accent);border-color:var(--ad-accent);color:#fff}
.ad-pane{display:none}.ad-pane.active{display:block}
/* ELI5 persona grid */
.ad-persona-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.75rem;margin-bottom:1.2rem}
.ad-persona{border:2px solid var(--ad-border);border-radius:var(--ad-radius);padding:.9rem 1rem;cursor:pointer;transition:all .2s;background:var(--ad-surface);text-align:center}
.ad-persona:hover{transform:translateY(-2px)}
.ad-persona.selected{border-color:var(--ad-accent);background:rgba(6,182,212,.05)}
.ad-persona-icon{font-size:1.6rem;margin-bottom:.4rem}
.ad-persona-label{font-size:.75rem;font-weight:700}
.ad-persona-sub{font-size:.65rem;color:var(--ad-muted);margin-top:.15rem}
.ad-eli5-run{display:block;margin:.8rem auto 1rem;padding:.5rem 2rem;background:linear-gradient(135deg,#06b6d4,#3b82f6);color:#fff;border:none;border-radius:999px;font-size:.8rem;font-weight:700;cursor:pointer;transition:all .2s}
.ad-eli5-run:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(6,182,212,.3)}
.ad-eli5-result{background:var(--ad-surface);border:1px solid var(--ad-border);border-radius:var(--ad-radius);padding:1.2rem 1.4rem;display:none;animation:anomUp .3s ease both}
.ad-eli5-result.show{display:block}
.ad-eli5-title{font-size:.88rem;font-weight:800;margin-bottom:.5rem;color:var(--ad-accent)}
.ad-eli5-body{font-size:.78rem;line-height:1.7;color:var(--ad-muted)}
.ad-eli5-stat{display:inline-block;background:rgba(6,182,212,.08);border:1px solid rgba(6,182,212,.18);border-radius:8px;padding:.3rem .7rem;font-size:.72rem;font-weight:700;color:var(--ad-accent);margin:.4rem .3rem 0 0}
/* classroom */
.ad-cls-wrap{max-width:780px;margin:0 auto}
.ad-cls-track{overflow:hidden;border-radius:var(--ad-radius);border:1px solid var(--ad-border)}
.ad-cls-slide{display:none;padding:2rem 2.2rem;background:var(--ad-surface);min-height:260px}
.ad-cls-slide.active{display:block;animation:anomUp .3s ease both}
.ad-cls-num{font-size:.6rem;font-weight:800;color:var(--ad-accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem}
.ad-cls-slide h3{font-size:1.05rem;font-weight:800;margin-bottom:.7rem}
.ad-cls-slide p{font-size:.8rem;line-height:1.72;color:var(--ad-muted);margin-bottom:.7rem}
.ad-cls-slide .ad-cls-formula{font-family:'Cascadia Code',monospace;background:rgba(6,182,212,.06);border:1px solid rgba(6,182,212,.14);border-radius:10px;padding:.7rem 1rem;font-size:.75rem;color:var(--ad-accent);margin:.5rem 0}
.ad-cls-nav{display:flex;align-items:center;justify-content:space-between;margin-top:1rem}
.ad-cls-nav-btn{padding:.4rem .9rem;border-radius:8px;border:1px solid var(--ad-border);background:var(--ad-surface);font-size:.72rem;font-weight:700;cursor:pointer;color:var(--ad-muted);transition:all .2s}
.ad-cls-nav-btn:hover{background:var(--ad-accent);color:#fff;border-color:var(--ad-accent)}
.ad-cls-dots{display:flex;gap:.4rem}
.ad-cls-dot{width:7px;height:7px;border-radius:50%;background:var(--ad-border);cursor:pointer;transition:all .2s}
.ad-cls-dot.active{background:var(--ad-accent);transform:scale(1.2)}
/* keypoints */
.ad-kp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}
.ad-kp{background:var(--ad-surface);border:1px solid var(--ad-border);border-radius:var(--ad-radius);padding:1.2rem;position:relative;overflow:hidden}
.ad-kp::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#06b6d4,#3b82f6)}
.ad-kp-icon{font-size:1.4rem;margin-bottom:.5rem}
.ad-kp h4{font-size:.82rem;font-weight:800;margin-bottom:.4rem}
.ad-kp p{font-size:.72rem;color:var(--ad-muted);line-height:1.6;margin:0}
/* code */
.ad-code-blocks{max-width:940px;margin:0 auto}
.ad-code-block{border-radius:14px;border:1px solid var(--ad-border);background:var(--ad-surface);margin-bottom:.8rem;overflow:hidden}
.ad-code-block summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.ad-code-block summary::-webkit-details-marker{display:none}
.ad-code-block summary::before{content:'&#9654;';font-size:.6rem;transition:transform .2s}
.ad-code-block[open] summary::before{transform:rotate(90deg)}
.ad-code-block pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;line-height:1.6;overflow-x:auto;border-top:1px solid var(--ad-border);font-family:'Cascadia Code','JetBrains Mono',monospace}
.ad-code-block .kw{color:#c4b5fd}.ad-code-block .fn{color:#6ee7b7}.ad-code-block .cm{color:#64748b;font-style:italic}.ad-code-block .str{color:#fcd34d}.ad-code-block .num{color:#f97316}
/* section heading */
.ad-sec-head{text-align:center;margin-bottom:1.6rem}
.ad-sec-head h2{font-size:1.35rem;font-weight:800;margin-bottom:.3rem}
.ad-sec-head p{font-size:.82rem;color:var(--ad-muted);max-width:560px;margin:0 auto;line-height:1.6}
/* about */
.ad-about-card{max-width:560px;margin:0 auto;background:var(--ad-surface);border:1px solid var(--ad-border);border-radius:24px;padding:2rem;text-align:center}
.ad-about-card h3{font-size:1.05rem;font-weight:800;margin-bottom:.4rem}
.ad-about-card p{font-size:.78rem;color:var(--ad-muted);line-height:1.6;margin-bottom:1rem}
.ad-share-btn{padding:.5rem 1.4rem;border-radius:999px;background:var(--ad-accent);color:#fff;border:none;font-size:.78rem;font-weight:700;cursor:pointer;transition:all .2s}
.ad-share-btn:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(6,182,212,.3)}
</style>

<div class="ad-progress"><div class="ad-progress-fill" id="adProgressFill"></div></div>

<nav class="ad-nav" id="adNav">
  <button class="ad-nav-btn active" onclick="adScrollTo('ad-story')">&#128218; Story</button>
  <button class="ad-nav-btn" onclick="adScrollTo('ad-demo')">&#9658; Demo</button>
  <button class="ad-nav-btn" onclick="adScrollTo('ad-classroom')">&#127979; Classroom</button>
  <button class="ad-nav-btn" onclick="adScrollTo('ad-keypoints')">&#128161; Key Points</button>
  <button class="ad-nav-btn" onclick="adScrollTo('ad-code')">&#128187; Code</button>
  <button class="ad-nav-btn" onclick="adScrollTo('ad-about')">&#127760; About</button>
</nav>

<div class="anom-wrap">

<!-- ══ STORY ══ -->
<section class="ad-section" id="ad-story">
  <div class="ad-sec-head">
    <div class="anom-tag"><i class="fas fa-wave-square me-1"></i> Stream Processing</div>
    <h2>Real-Time Anomaly Detection</h2>
    <p>Live sensor stream with Z-score, EWMA, and CUSUM algorithms. Inject spikes and drift &#8212; watch each algorithm detect differently in real time.</p>
  </div>
  <div class="ad-story-steps">
    <div class="ad-step">
      <div class="ad-step-num">Step 1 &#8212; The Problem</div>
      <h4>The $4M/Hour Failure Nobody Sees</h4>
      <p>Unplanned industrial downtime costs $4M/hour on average. 73% of failures give advance warning &#8212; subtle sensor drift that nobody&#39;s watching. IoT generates 2TB/day per facility. Human monitoring at scale is impossible.</p>
    </div>
    <div class="ad-step">
      <div class="ad-step-num">Step 2 &#8212; The Definition</div>
      <h4>What Makes a Reading &#34;Anomalous&#34;?</h4>
      <p>A value statistically inconsistent with recent history. But &#34;inconsistent&#34; depends on the distribution, the time horizon, and how many false alarms you can tolerate. Every threshold is a business decision.</p>
    </div>
    <div class="ad-step">
      <div class="ad-step-num">Step 3 &#8212; Z-Score</div>
      <h4>The Baseline: Standard Deviations from the Mean</h4>
      <p>Z = (x &#8722; &#956;) / &#963;. Triggers when a reading is 3&#963; or more from the rolling mean. Fast, transparent, audit-friendly. Fails at gradual drifts &#8212; the single biggest gap in point-anomaly detection.</p>
    </div>
    <div class="ad-step">
      <div class="ad-step-num">Step 4 &#8212; EWMA</div>
      <h4>Exponential Smoothing: Memory for the Mean</h4>
      <p>EWMA keeps a weighted average where recent readings matter more. &#945; = 0.15 means the last reading gets 15% weight &#8212; the model &#34;remembers&#34; trends across dozens of samples instead of triggering on noise.</p>
    </div>
    <div class="ad-step">
      <div class="ad-step-num">Step 5 &#8212; CUSUM</div>
      <h4>Accumulating Evidence of Drift</h4>
      <p>CUSUM adds up small deviations over time. A 0.2&#963; shift every sample goes undetected by Z-Score for 43 readings &#8212; CUSUM catches it in 10. Purpose-built for bearing wear, calibration drift, and seasonal bias.</p>
    </div>
    <div class="ad-step">
      <div class="ad-step-num">Step 6 &#8212; Production</div>
      <h4>Alert &#8594; Triage &#8594; Work Order in &lt;30 Seconds</h4>
      <p>Real systems pair detectors with CMMS integration &#8212; auto-creating maintenance tickets, routing to the right technician, and tracking Mean Time to Detect (MTTD). The algorithm is 5% of the value; the integration is 95%.</p>
    </div>
  </div>
</section>

<!-- ══ DEMO ══ -->
<section class="ad-section" id="ad-demo">
  <div class="ad-sec-head">
    <h2>Interactive Demo</h2>
    <p>Choose how you want to explore the detector &#8212; plain-language explanation or the live algorithm.</p>
  </div>
  <div class="ad-mode-bar">
    <button class="ad-mode-btn active" data-mode="eli5" onclick="adSetMode('eli5')">&#x1F4A1; ELI5</button>
    <button class="ad-mode-btn" data-mode="engineer" onclick="adSetMode('engineer')">&#x2699;&#xFE0F; Engineer</button>
  </div>

  <!-- ELI5 pane -->
  <div class="ad-pane active" data-pane="eli5">
    <div class="ad-persona-grid">
      <div class="ad-persona" data-key="operator" onclick="adSelectPersona('operator')">
        <div class="ad-persona-icon">&#x1F3ED;</div>
        <div class="ad-persona-label">Plant Operator</div>
        <div class="ad-persona-sub">&#8220;My machines need to keep running&#8221;</div>
      </div>
      <div class="ad-persona" data-key="scientist" onclick="adSelectPersona('scientist')">
        <div class="ad-persona-icon">&#x1F9EA;</div>
        <div class="ad-persona-label">Data Scientist</div>
        <div class="ad-persona-sub">&#8220;Show me the math and tradeoffs&#8221;</div>
      </div>
      <div class="ad-persona" data-key="devops" onclick="adSelectPersona('devops')">
        <div class="ad-persona-icon">&#x2699;&#xFE0F;</div>
        <div class="ad-persona-label">DevOps Engineer</div>
        <div class="ad-persona-sub">&#8220;What does this do at 3am on-call?&#8221;</div>
      </div>
      <div class="ad-persona" data-key="analyst" onclick="adSelectPersona('analyst')">
        <div class="ad-persona-icon">&#x1F4CA;</div>
        <div class="ad-persona-label">Business Analyst</div>
        <div class="ad-persona-sub">&#8220;What&#39;s the ROI of all this?&#8221;</div>
      </div>
    </div>
    <button class="ad-eli5-run" onclick="adRunELI5()">&#9654; Run Simulation</button>
    <div class="ad-eli5-result" id="adELI5Result">
      <div class="ad-eli5-title" id="adELI5Title"></div>
      <div class="ad-eli5-body" id="adELI5Body"></div>
      <div id="adELI5Stats"></div>
    </div>
  </div>

  <!-- Engineer pane — existing interactive demo -->
  <div class="ad-pane" data-pane="engineer">
  <div class="anom-status-grid">
    <div class="anom-stat" id="sValBox"><div class="anom-stat-val" id="sVal">&#8212;</div><div class="anom-stat-lbl">Current Value</div></div>
    <div class="anom-stat" id="sZBox"><div class="anom-stat-val" id="sZ">&#8212;</div><div class="anom-stat-lbl">Z-Score</div></div>
    <div class="anom-stat"><div class="anom-stat-val" id="sEWMA">&#8212;</div><div class="anom-stat-lbl">EWMA (&#945;=0.15)</div></div>
    <div class="anom-stat"><div class="anom-stat-val" id="sStatus" style="font-size:.85rem">NORMAL</div><div class="anom-stat-lbl">Detection Status</div></div>
  </div>
  <div class="anom-body">
    <div class="anom-panel">
      <div class="anom-panel-hd">
        <i class="fas fa-chart-line"></i> Live Sensor Stream
        <span class="anom-drift-badge" id="driftBadge">DRIFT ACTIVE</span>
        <span style="margin-left:auto;font-size:.6rem;font-weight:500;opacity:.4" id="sAlgoName">ALGORITHM: Z-SCORE</span>
      </div>
      <div class="anom-controls">
        <button class="anom-btn anom-btn--start" id="btnToggle"><i class="fas fa-play"></i> Start Stream</button>
        <button class="anom-btn anom-btn--spike" id="btnSpike" disabled><i class="fas fa-bolt"></i> Inject Spike</button>
        <button class="anom-btn anom-btn--drift" id="btnDrift" disabled><i class="fas fa-arrow-trend-up"></i> Inject Drift</button>
        <button class="anom-btn anom-btn--reset" id="btnReset" disabled><i class="fas fa-undo"></i> Reset</button>
        <div class="anom-algo-group">
          <button class="anom-algo-btn active" data-algo="zscore">Z-Score</button>
          <button class="anom-algo-btn" data-algo="ewma">EWMA</button>
          <button class="anom-algo-btn" data-algo="cusum">CUSUM</button>
        </div>
      </div>
      <div class="anom-chart-wrap"><canvas id="anomChart"></canvas></div>
      <div class="anom-leg">
        <span class="anom-leg-item"><span class="anom-leg-dot" style="background:#06b6d4"></span>Signal</span>
        <span class="anom-leg-item"><span class="anom-leg-dot" style="background:rgba(239,68,68,.4)"></span>3&#963; Upper</span>
        <span class="anom-leg-item"><span class="anom-leg-dot" style="background:rgba(239,68,68,.4)"></span>3&#963; Lower</span>
        <span class="anom-leg-item"><span class="anom-leg-dot" style="background:rgba(245,158,11,.45)"></span>2&#963; Band</span>
        <span class="anom-leg-item"><span class="anom-leg-dot" style="background:#a78bfa"></span>EWMA Trend</span>
      </div>
    </div>
    <div class="anom-panel">
      <div class="anom-panel-hd"><i class="fas fa-bell"></i> Alert Log</div>
      <div class="anom-log" id="anomLog">
        <div class="anom-log-empty">Start stream to see alerts&#8230;</div>
      </div>
    </div>
  </div>
  </div><!-- /engineer pane -->
</section>
''')
out.close()
print('ad1 done')
