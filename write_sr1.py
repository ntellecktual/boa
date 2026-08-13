"""write_sr1.py — schema_registry.html 7-ideations (part 1/2, write)"""
TMPL = r'boaapp/templates/boaapp/schema_registry.html'
out = open(TMPL, 'w', encoding='utf-8')
out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Schema Registry{% endblock %}
{% block container_class %}sreg-shell{% endblock %}
{% block content %}
<style>
/* ══ base ══ */
.sreg-shell{display:block;width:100%;max-width:100%;padding:0}
:root{--sreg-accent:#f43f5e;--sreg-accent2:#e11d48;--sreg-surface:#fff;--sreg-border:rgba(0,0,0,.07);--sreg-shadow:0 2px 12px rgba(0,0,0,.06);--sreg-muted:#6b7280;--sreg-radius:16px}
[data-theme="dark"]{--sreg-surface:rgba(22,10,14,.97);--sreg-border:rgba(255,255,255,.08);--sreg-shadow:0 2px 12px rgba(0,0,0,.35);--sreg-muted:#94a3b8}
@keyframes sregUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.sreg-wrap{max-width:1200px;margin:0 auto;padding:0 1.5rem 4rem}
/* ══ progress bar ══ */
.sreg-progress{position:fixed;top:0;left:0;right:0;height:3px;background:rgba(244,63,94,.12);z-index:2000}
.sreg-progress-fill{height:100%;width:0%;background:linear-gradient(90deg,#f43f5e,#f97316);transition:width .15s}
/* ══ sticky nav ══ */
.sreg-nav{position:sticky;top:0;z-index:999;display:flex;gap:.35rem;background:var(--sreg-surface);border-bottom:1px solid var(--sreg-border);padding:.55rem 1rem;backdrop-filter:blur(12px);flex-wrap:wrap}
.sreg-nav-btn{padding:.32rem .85rem;border-radius:999px;font-size:.72rem;font-weight:700;border:1px solid transparent;background:transparent;cursor:pointer;color:var(--sreg-muted);transition:all .18s}
.sreg-nav-btn:hover,.sreg-nav-btn.active{background:linear-gradient(135deg,#f43f5e,#f97316);color:#fff;border-color:transparent}
/* ══ section ══ */
.sreg-section{padding:2.4rem 0 1.2rem;animation:sregUp .5s ease both}
.sreg-sec-head{text-align:center;margin-bottom:1.6rem}
.sreg-sec-head h2{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:800;margin-bottom:.3rem}
.sreg-sec-head p{font-size:.88rem;color:var(--sreg-muted);max-width:560px;margin:0 auto;line-height:1.6}
/* ══ hero ══ */
.sreg-hero{text-align:center;padding:2.2rem 0 1.4rem;animation:sregUp .4s ease both}
.sreg-tag{display:inline-block;padding:.22rem .85rem;border-radius:999px;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;background:rgba(244,63,94,.09);border:1px solid rgba(244,63,94,.2);color:var(--sreg-accent);margin-bottom:.65rem}
.sreg-hero h1{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;background:linear-gradient(135deg,#f43f5e,#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.4rem}
.sreg-hero p{font-size:.88rem;color:var(--sreg-muted);max-width:580px;margin:0 auto;line-height:1.6}
/* ══ story ══ */
.sreg-story-steps{display:grid;gap:1rem;max-width:900px;margin:0 auto}
.sreg-step{display:flex;gap:1.1rem;align-items:flex-start;background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);padding:1.1rem 1.3rem;box-shadow:var(--sreg-shadow)}
.sreg-step-num{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#f43f5e,#f97316);color:#fff;font-size:.78rem;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.sreg-step-body h4{font-size:.88rem;font-weight:800;margin:0 0 .25rem}
.sreg-step-body p{font-size:.82rem;color:var(--sreg-muted);margin:0;line-height:1.55}
/* ══ demo mode bar ══ */
.sreg-mode-bar{display:flex;gap:.5rem;max-width:700px;margin:0 auto 1.4rem;background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:999px;padding:.25rem;box-shadow:var(--sreg-shadow)}
.sreg-mode-tab{flex:1;padding:.38rem 0;border-radius:999px;font-size:.75rem;font-weight:700;border:none;background:transparent;cursor:pointer;color:var(--sreg-muted);transition:all .18s}
.sreg-mode-tab.active{background:linear-gradient(135deg,#f43f5e,#f97316);color:#fff}
/* ══ demo panes ══ */
.sreg-pane{display:none}
.sreg-pane.active{display:block}
/* ══ ELI5 ══ */
.sreg-persona-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;max-width:900px;margin:0 auto 1.2rem}
@media(max-width:700px){.sreg-persona-grid{grid-template-columns:1fr 1fr}}
.sreg-persona{background:var(--sreg-surface);border:2px solid var(--sreg-border);border-radius:var(--sreg-radius);padding:.9rem .7rem;text-align:center;cursor:pointer;transition:all .18s}
.sreg-persona:hover,.sreg-persona.selected{border-color:var(--sreg-accent);box-shadow:0 0 0 3px rgba(244,63,94,.12)}
.sreg-persona-icon{font-size:1.6rem;margin-bottom:.35rem}
.sreg-persona-label{font-size:.75rem;font-weight:800;margin-bottom:.15rem}
.sreg-persona-sub{font-size:.63rem;color:var(--sreg-muted)}
.sreg-eli5-run{display:block;margin:.6rem auto 0;padding:.5rem 1.6rem;border-radius:999px;font-size:.78rem;font-weight:700;background:linear-gradient(135deg,#f43f5e,#f97316);color:#fff;border:none;cursor:pointer}
.sreg-eli5-result{display:none;max-width:860px;margin:1.1rem auto 0;background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);padding:1.2rem 1.4rem;box-shadow:var(--sreg-shadow)}
.sreg-eli5-result.show{display:block}
.sreg-eli5-title{font-size:.93rem;font-weight:800;margin-bottom:.65rem}
.sreg-eli5-body{font-size:.83rem;color:var(--sreg-muted);line-height:1.65;margin-bottom:.85rem}
.sreg-eli5-stats{display:flex;flex-wrap:wrap;gap:.5rem}
.sreg-eli5-stat{font-size:.68rem;font-weight:700;padding:.25rem .7rem;border-radius:999px;background:rgba(244,63,94,.09);color:var(--sreg-accent);border:1px solid rgba(244,63,94,.14)}
/* ══ Engineer pane — interactive demo ══ */
.sreg-body{display:grid;grid-template-columns:180px 1fr 220px;gap:1rem}
@media(max-width:900px){.sreg-body{grid-template-columns:1fr 1fr}}
@media(max-width:580px){.sreg-body{grid-template-columns:1fr}}
.sreg-panel{background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);box-shadow:var(--sreg-shadow);padding:1rem}
.sreg-panel-hd{display:flex;align-items:center;gap:.45rem;font-size:.75rem;font-weight:800;margin-bottom:.85rem;padding-bottom:.5rem;border-bottom:1px solid var(--sreg-border)}
.sreg-panel-hd i{color:var(--sreg-accent);opacity:.8}
.sreg-timeline{list-style:none;padding:0;margin:0;position:relative}
.sreg-timeline::before{content:'';position:absolute;left:9px;top:4px;bottom:4px;width:2px;background:var(--sreg-border)}
.sreg-tl-item{display:flex;align-items:flex-start;gap:.6rem;padding:.5rem 0;cursor:pointer;border-radius:8px;position:relative;padding-left:6px;transition:background .15s}
.sreg-tl-item:hover{background:rgba(244,63,94,.04)}
.sreg-tl-dot{width:18px;height:18px;border-radius:50%;border:2px solid var(--sreg-border);background:var(--sreg-surface);flex-shrink:0;margin-top:1px;position:relative;z-index:1;transition:all .2s}
.sreg-tl-item.active .sreg-tl-dot{border-color:var(--sreg-accent);background:var(--sreg-accent)}
.sreg-tl-content{flex:1}
.sreg-tl-ver{font-size:.72rem;font-weight:800;line-height:1.2}
.sreg-tl-ts{font-size:.58rem;color:var(--sreg-muted);margin-top:1px}
.sreg-tl-tag{display:inline-block;font-size:.55rem;font-weight:700;padding:.08rem .35rem;border-radius:4px;margin-top:.25rem}
.sreg-tl-tag--safe{background:rgba(16,185,129,.1);color:#059669}
.sreg-tl-tag--break{background:rgba(244,63,94,.1);color:#e11d48}
.sreg-code{background:rgba(0,0,0,.03);border:1px solid var(--sreg-border);border-radius:10px;padding:.85rem;font-size:.66rem;font-family:'Cascadia Code','JetBrains Mono',monospace;line-height:1.8;white-space:pre-wrap;min-height:260px;overflow-x:auto;position:relative}
[data-theme="dark"] .sreg-code{background:rgba(255,255,255,.03)}
.sreg-code .k{color:#f43f5e;font-weight:600}
.sreg-code .s{color:#10b981}
.sreg-code .n{color:#f59e0b}
.sreg-code .b{color:#3b82f6}
.sreg-code .field-new{background:rgba(16,185,129,.1);border-left:2px solid #10b981;padding-left:.2rem}
.sreg-code .field-del{background:rgba(244,63,94,.1);border-left:2px solid #f43f5e;padding-left:.2rem;text-decoration:line-through;opacity:.7}
.sreg-code .field-mod{background:rgba(245,158,11,.1);border-left:2px solid #f59e0b;padding-left:.2rem}
.sreg-changes{display:flex;flex-direction:column;gap:.45rem;margin-bottom:.85rem}
.sreg-change-btn{display:block;width:100%;padding:.42rem .7rem;border-radius:9px;font-size:.7rem;font-weight:700;border:1px solid var(--sreg-border);background:transparent;cursor:pointer;text-align:left;transition:all .18s}
.sreg-change-btn:hover{border-color:var(--sreg-accent);color:var(--sreg-accent)}
.sreg-change-btn .sreg-cb-tag{display:inline-block;font-size:.58rem;padding:.07rem .4rem;border-radius:4px;float:right;font-weight:700}
.sreg-cb-tag--safe{background:rgba(16,185,129,.15);color:#059669}
.sreg-cb-tag--break{background:rgba(244,63,94,.12);color:#e11d48}
.sreg-compat-row{margin-bottom:.7rem}
.sreg-compat-label{font-size:.65rem;font-weight:700;margin-bottom:.3rem;opacity:.6}
.sreg-mode-group{display:flex;gap:.3rem}
.sreg-mode-btn{flex:1;padding:.28rem 0;border-radius:7px;font-size:.62rem;font-weight:700;border:1px solid var(--sreg-border);background:transparent;cursor:pointer;transition:all .18s;color:var(--sreg-muted)}
.sreg-mode-btn.active{background:linear-gradient(135deg,#f43f5e,#f97316);color:#fff;border-color:transparent}
.sreg-result{border-radius:12px;padding:.85rem;text-align:center;margin-top:.75rem;transition:all .3s}
.sreg-result--compat{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25)}
.sreg-result--incompat{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.25)}
.sreg-result-icon{font-size:1.75rem;margin-bottom:.35rem}
.sreg-result-title{font-size:.78rem;font-weight:800;margin-bottom:.35rem}
.sreg-result--compat .sreg-result-title{color:#059669}
.sreg-result--incompat .sreg-result-title{color:#e11d48}
.sreg-result-issues{list-style:none;padding:0;margin:0;text-align:left}
.sreg-result-issues li{font-size:.64rem;padding:.2rem 0;display:flex;align-items:flex-start;gap:.35rem;color:var(--sreg-muted)}
.sreg-result-issues li::before{content:'&#x2192;';color:var(--sreg-accent);flex-shrink:0}
.sreg-meta{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:.75rem}
.sreg-meta-badge{display:inline-block;font-size:.6rem;font-weight:700;padding:.15rem .5rem;border-radius:6px;background:rgba(244,63,94,.08);color:var(--sreg-accent);border:1px solid rgba(244,63,94,.12)}
.sreg-diff-hint{font-size:.65rem;color:var(--sreg-muted);margin-top:.5rem;display:flex;gap:1rem;flex-wrap:wrap}
.sreg-diff-hint span{display:inline-flex;align-items:center;gap:.3rem}
.sreg-diff-swatch{width:10px;height:10px;border-radius:2px}
/* ══ classroom ══ */
.sreg-cls-wrap{max-width:860px;margin:0 auto}
.sreg-cls-track{position:relative;min-height:260px}
.sreg-cls-slide{display:none;animation:sregUp .35s ease}
.sreg-cls-slide.active{display:block}
.sreg-cls-slide h3{font-size:1.05rem;font-weight:800;margin-bottom:.65rem}
.sreg-cls-slide p{font-size:.84rem;color:var(--sreg-muted);line-height:1.65;margin-bottom:.7rem}
.sreg-cls-slide code{font-size:.78rem;background:rgba(244,63,94,.07);padding:.1rem .35rem;border-radius:4px;color:var(--sreg-accent)}
.sreg-cls-num{font-size:.62rem;font-weight:700;color:var(--sreg-accent);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.45rem}
.sreg-cls-formula{background:rgba(244,63,94,.06);border:1px solid rgba(244,63,94,.14);border-radius:10px;padding:.65rem 1rem;font-size:.74rem;font-family:'Cascadia Code','JetBrains Mono',monospace;color:var(--sreg-accent);margin-top:.7rem}
.sreg-cls-nav{display:flex;align-items:center;justify-content:center;gap:1rem;margin-top:1.2rem}
.sreg-cls-nav-btn{padding:.38rem 1.2rem;border-radius:999px;font-size:.78rem;font-weight:700;border:1px solid var(--sreg-border);background:var(--sreg-surface);cursor:pointer;transition:all .18s}
.sreg-cls-nav-btn:hover{border-color:var(--sreg-accent);color:var(--sreg-accent)}
.sreg-cls-dots{display:flex;gap:.5rem;align-items:center}
.sreg-cls-dot{width:9px;height:9px;border-radius:50%;background:var(--sreg-border);cursor:pointer;transition:all .18s}
.sreg-cls-dot.active{background:var(--sreg-accent);transform:scale(1.2)}
/* ══ key points ══ */
.sreg-kp-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;max-width:900px;margin:0 auto}
@media(max-width:700px){.sreg-kp-grid{grid-template-columns:1fr}}
.sreg-kp{background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);padding:1.2rem 1.4rem;box-shadow:var(--sreg-shadow)}
.sreg-kp-icon{font-size:1.6rem;margin-bottom:.5rem}
.sreg-kp h4{font-size:.9rem;font-weight:800;margin-bottom:.4rem}
.sreg-kp p{font-size:.82rem;color:var(--sreg-muted);margin:0;line-height:1.55}
/* ══ code blocks ══ */
.sreg-code-blocks{max-width:900px;margin:0 auto}
.sreg-code-block{border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);background:var(--sreg-surface);margin-bottom:.85rem;overflow:hidden;box-shadow:var(--sreg-shadow)}
.sreg-code-block summary{padding:.8rem 1.2rem;font-size:.83rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.sreg-code-block summary::-webkit-details-marker{display:none}
.sreg-code-block summary::before{content:'&#x25B6;';font-size:.6rem;transition:transform .2s}
.sreg-code-block[open] summary::before{transform:rotate(90deg)}
.sreg-code-block pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;line-height:1.65;overflow-x:auto;border-top:1px solid var(--sreg-border);font-family:'Cascadia Code','JetBrains Mono',monospace}
.sreg-code-block code{background:none;padding:0;color:inherit}
.sreg-code-block .kw{color:#c4b5fd}.sreg-code-block .fn{color:#6ee7b7}.sreg-code-block .str{color:#fcd34d}.sreg-code-block .cm{color:#64748b;font-style:italic}.sreg-code-block .num{color:#f97316}
/* ══ about ══ */
.sreg-about-card{max-width:600px;margin:0 auto;background:var(--sreg-surface);border:1px solid var(--sreg-border);border-radius:var(--sreg-radius);padding:1.8rem;text-align:center;box-shadow:var(--sreg-shadow)}
.sreg-about-card h3{font-size:1.05rem;font-weight:800;margin-bottom:.6rem}
.sreg-about-card p{font-size:.83rem;color:var(--sreg-muted);line-height:1.6;margin-bottom:.7rem}
.sreg-share-btn{padding:.45rem 1.4rem;border-radius:999px;font-size:.78rem;font-weight:700;border:1px solid var(--sreg-border);background:var(--sreg-surface);cursor:pointer;transition:all .18s}
.sreg-share-btn:hover{border-color:var(--sreg-accent);color:var(--sreg-accent)}
</style>

<div class="sreg-progress"><div class="sreg-progress-fill" id="sregProgressFill"></div></div>

<nav class="sreg-nav" id="sregNav">
  <button class="sreg-nav-btn active" onclick="sregScrollTo('sreg-story')">Story</button>
  <button class="sreg-nav-btn" onclick="sregScrollTo('sreg-demo')">Demo</button>
  <button class="sreg-nav-btn" onclick="sregScrollTo('sreg-classroom')">Classroom</button>
  <button class="sreg-nav-btn" onclick="sregScrollTo('sreg-keypoints')">Key Points</button>
  <button class="sreg-nav-btn" onclick="sregScrollTo('sreg-code')">Code</button>
  <button class="sreg-nav-btn" onclick="sregScrollTo('sreg-about')">About</button>
</nav>

<div class="sreg-wrap">

<div class="sreg-hero">
  <div class="sreg-tag"><i class="fas fa-file-code me-1"></i> Data Contracts</div>
  <h1>Schema Registry</h1>
  <p>Manage event schema evolution with strict backward/forward compatibility checking. Apply field changes and immediately see which consumers break &#8212; before it reaches production.</p>
</div>

<!-- ══ STORY ══ -->
<section class="sreg-section" id="sreg-story">
  <div class="sreg-sec-head">
    <h2>The Story</h2>
    <p>How unmanaged schema evolution brought down a Kafka-based order processing system &#8212; and how the registry fixed it.</p>
  </div>
  <div class="sreg-story-steps">
    <div class="sreg-step">
      <div class="sreg-step-num">1</div>
      <div class="sreg-step-body"><h4>3:17 AM &#8212; Kafka Consumer Exception Storm</h4>
      <p>PagerDuty fires 47 alerts simultaneously. The order processing consumer group is throwing <code>org.apache.avro.AvroTypeException: Expected int, found string</code>. The offending field: <code>user_id</code>. A developer changed it from <code>int</code> to <code>string</code> in a "minor" refactor. Six downstream consumers are crashing on every message.</p></div>
    </div>
    <div class="sreg-step">
      <div class="sreg-step-num">2</div>
      <div class="sreg-step-body"><h4>The Root Cause &#8212; No Schema Contract Enforcement</h4>
      <p>Schemas were embedded in application code and distributed via Git. No central registry, no compatibility checks. Three teams shared the OrderEvent schema &#8212; none knew about each other's assumptions. The producer updated <code>user_id</code> independently because the unit tests passed. The integration tests didn't cover Avro deserialization.</p></div>
    </div>
    <div class="sreg-step">
      <div class="sreg-step-num">3</div>
      <div class="sreg-step-body"><h4>Deploying Confluent Schema Registry</h4>
      <p>The fix: a single Schema Registry as the contract layer between all producers and consumers. Every schema version is registered at deployment time. The registry enforces a compatibility mode &#8212; BACKWARD by default &#8212; that rejects breaking changes before they ever reach the wire. Producers that would break consumers are blocked at registration.</p></div>
    </div>
    <div class="sreg-step">
      <div class="sreg-step-num">4</div>
      <div class="sreg-step-body"><h4>Three Compatibility Modes, Three Use Cases</h4>
      <p><strong>BACKWARD</strong> (default): New consumer can read old messages. Allows adding optional fields with defaults. Used for most event streams. <strong>FORWARD</strong>: Old consumers can read new messages. Used when consumers can't be updated immediately. <strong>FULL</strong>: Both directions simultaneously. Mandatory for financial events subject to 7-year replay requirements.</p></div>
    </div>
    <div class="sreg-step">
      <div class="sreg-step-num">5</div>
      <div class="sreg-step-body"><h4>Canary Migration for Breaking Changes</h4>
      <p>When a MAJOR version change is unavoidable (e.g., splitting one field into two), the migration orchestrator deploys the new schema to 5% of traffic, monitors deserialization error rates for 15 minutes, then promotes to 100% if error rate stays below 0.1%. If it exceeds threshold, it rolls back to the previous version automatically &#8212; no human intervention required.</p></div>
    </div>
    <div class="sreg-step">
      <div class="sreg-step-num">6</div>
      <div class="sreg-step-body"><h4>Zero Breaking Changes in 18 Months</h4>
      <p>After adopting the registry with full CI/CD integration &#8212; schema compatibility check as a required pipeline step &#8212; the team shipped 87 schema versions across 14 subjects with zero production deserialization failures. Dead field detection identified 23 fields no consumer had read in 90 days, enabling a clean MAJOR version that reduced average message size by 31%.</p></div>
    </div>
  </div>
</section>

<!-- ══ DEMO ══ -->
<section class="sreg-section" id="sreg-demo">
  <div class="sreg-sec-head">
    <h2>Interactive Demo</h2>
    <p>Select an ELI5 persona to hear the plain-English story, or switch to Engineer mode for the live schema compatibility simulator.</p>
  </div>
  <div class="sreg-mode-bar">
    <button class="sreg-mode-tab active" data-pane="eli5" onclick="sregSetMode('eli5')">&#x1F4AC; ELI5 Mode</button>
    <button class="sreg-mode-tab" data-pane="engineer" onclick="sregSetMode('engineer')">&#x2699;&#xFE0F; Engineer Mode</button>
  </div>

  <!-- ELI5 pane -->
  <div class="sreg-pane active" data-pane="eli5">
    <div class="sreg-persona-grid">
      <div class="sreg-persona" data-key="backend" onclick="sregSelectPersona('backend')">
        <div class="sreg-persona-icon">&#x1F4BB;</div>
        <div class="sreg-persona-label">Backend Dev</div>
        <div class="sreg-persona-sub">API integration</div>
      </div>
      <div class="sreg-persona" data-key="dataeng" onclick="sregSelectPersona('dataeng')">
        <div class="sreg-persona-icon">&#x1F4E1;</div>
        <div class="sreg-persona-label">Data Engineer</div>
        <div class="sreg-persona-sub">Kafka pipelines</div>
      </div>
      <div class="sreg-persona" data-key="architect" onclick="sregSelectPersona('architect')">
        <div class="sreg-persona-icon">&#x1F3D7;&#xFE0F;</div>
        <div class="sreg-persona-label">Platform Architect</div>
        <div class="sreg-persona-sub">Contract governance</div>
      </div>
      <div class="sreg-persona" data-key="compliance" onclick="sregSelectPersona('compliance')">
        <div class="sreg-persona-icon">&#x2696;&#xFE0F;</div>
        <div class="sreg-persona-label">Compliance Officer</div>
        <div class="sreg-persona-sub">7-year audit replay</div>
      </div>
    </div>
    <button class="sreg-eli5-run" onclick="sregRunELI5()">&#x25B6; Explain It To Me</button>
    <div class="sreg-eli5-result" id="sregELI5Result">
      <div class="sreg-eli5-title" id="sregELI5Title"></div>
      <div class="sreg-eli5-body" id="sregELI5Body"></div>
      <div class="sreg-eli5-stats" id="sregELI5Stats"></div>
    </div>
  </div>

  <!-- Engineer pane — original interactive demo -->
  <div class="sreg-pane" data-pane="engineer">
    <div class="sreg-body">
      <div class="sreg-panel">
        <div class="sreg-panel-hd"><i class="fas fa-history"></i> Versions</div>
        <ul class="sreg-timeline" id="sregTimeline"></ul>
      </div>
      <div class="sreg-panel">
        <div class="sreg-panel-hd"><i class="fas fa-code"></i> Schema &#8212; <span id="sregSubject">OrderEvent</span>
          <span style="margin-left:.5rem;font-size:.68rem;font-weight:600;opacity:.5" id="sregVerBadge">v1</span>
        </div>
        <div class="sreg-meta" id="sregMeta"></div>
        <div class="sreg-code" id="sregCodeView"></div>
        <div class="sreg-diff-hint" id="sregDiffHint" style="display:none">
          <span><span class="sreg-diff-swatch" style="background:rgba(16,185,129,.35)"></span>Added</span>
          <span><span class="sreg-diff-swatch" style="background:rgba(244,63,94,.25)"></span>Removed</span>
          <span><span class="sreg-diff-swatch" style="background:rgba(245,158,11,.25)"></span>Modified</span>
        </div>
      </div>
      <div class="sreg-panel">
        <div class="sreg-panel-hd"><i class="fas fa-shield-halved"></i> Change Simulator</div>
        <div class="sreg-compat-label">Apply a Schema Change</div>
        <div class="sreg-changes">
          <button class="sreg-change-btn" data-change="add_safe">
            <i class="fas fa-plus-circle" style="color:#10b981"></i> Add field w/ default
            <span class="sreg-cb-tag sreg-cb-tag--safe">SAFE</span>
          </button>
          <button class="sreg-change-btn" data-change="remove_required">
            <i class="fas fa-minus-circle" style="color:#f43f5e"></i> Remove required field
            <span class="sreg-cb-tag sreg-cb-tag--break">&#x26A1; BREAKING</span>
          </button>
          <button class="sreg-change-btn" data-change="rename_field">
            <i class="fas fa-pen-to-square" style="color:#f43f5e"></i> Rename field
            <span class="sreg-cb-tag sreg-cb-tag--break">&#x26A1; BREAKING</span>
          </button>
          <button class="sreg-change-btn" data-change="change_type">
            <i class="fas fa-arrows-rotate" style="color:#f43f5e"></i> Change field type
            <span class="sreg-cb-tag sreg-cb-tag--break">&#x26A1; BREAKING</span>
          </button>
          <button class="sreg-change-btn" data-change="reset" style="background:rgba(99,102,241,.06);border-color:rgba(99,102,241,.2)">
            <i class="fas fa-undo" style="color:#6366f1"></i> Reset to v1
          </button>
        </div>
        <div class="sreg-compat-label">Compatibility Mode</div>
        <div class="sreg-mode-group" id="sregModes">
          <button class="sreg-mode-btn active" data-mode="BACKWARD">BACKWARD</button>
          <button class="sreg-mode-btn" data-mode="FORWARD">FORWARD</button>
          <button class="sreg-mode-btn" data-mode="FULL">FULL</button>
        </div>
        <div id="sregResult" style="display:none"></div>
      </div>
    </div>
  </div>
</section>
''')
out.close()
print('sr1 done')
