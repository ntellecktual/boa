"""write_dq1.py — data_quality.html 7-ideations redesign (part 1 of 2)"""
TMPL = r'boaapp/templates/boaapp/data_quality.html'
out = open(TMPL, 'w', encoding='utf-8')
out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Data Quality — Omni Hotels{% endblock %}
{% block container_class %}dq-shell{% endblock %}
{% block content %}
<style>
/* ══ existing dq vars ══ */
.dq-shell{display:block;width:100%;max-width:100%;padding:0}
:root{--dq-accent:#10b981;--dq-accent2:#059669;--dq-surface:#fff;--dq-border:rgba(0,0,0,.07);--dq-shadow:0 2px 12px rgba(0,0,0,.06);--dq-muted:#6b7280;--dq-brand:#1a3c5e}
[data-theme="dark"]{--dq-surface:rgba(10,22,16,.97);--dq-border:rgba(255,255,255,.08);--dq-shadow:0 2px 12px rgba(0,0,0,.35);--dq-muted:#94a3b8}
@keyframes dqUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes dqSpin{to{transform:rotate(360deg)}}
.dq-wrap{max-width:1280px;margin:0 auto;padding:0 1.5rem 3rem}
.dq-hero{text-align:center;padding:1.4rem 0 1rem;animation:dqUp .4s ease both}
.dq-tag{display:inline-block;padding:.22rem .85rem;border-radius:999px;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;background:rgba(16,185,129,.09);border:1px solid rgba(16,185,129,.2);color:var(--dq-accent);margin-bottom:.65rem}
.dq-hero h1{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:800;background:linear-gradient(135deg,#10b981,#1a3c5e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.3rem}
.dq-hero p{font-size:.84rem;color:var(--dq-muted);max-width:640px;margin:0 auto;line-height:1.6}
.dq-hero-context{display:inline-flex;align-items:center;gap:.5rem;margin-top:.7rem;padding:.4rem .9rem;border-radius:10px;background:rgba(16,185,129,.04);border:1px solid rgba(16,185,129,.12);font-size:.68rem;color:var(--dq-muted)}
.dq-hero-context strong{color:var(--dq-accent);font-weight:800}
.dq-grid{display:grid;grid-template-columns:1fr;gap:1rem;margin-top:1rem}
.dq-panel{background:var(--dq-surface);border:1px solid var(--dq-border);border-radius:16px;box-shadow:var(--dq-shadow);padding:1.1rem}
.dq-panel-hd{display:flex;align-items:center;gap:.45rem;font-size:.75rem;font-weight:800;margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:1px solid var(--dq-border)}
.dq-panel-hd i{color:var(--dq-accent);opacity:.8}
.dq-panel-hd .dq-badge{margin-left:auto;font-size:.56rem;font-weight:700;padding:.14rem .5rem;border-radius:999px;background:rgba(16,185,129,.08);color:var(--dq-accent);border:1px solid rgba(16,185,129,.14)}
.dq-dt{width:100%;font-size:.62rem;border-collapse:separate;border-spacing:0;overflow:hidden;border-radius:10px;border:1px solid var(--dq-border)}
.dq-dt th{background:rgba(16,185,129,.06);font-size:.56rem;text-transform:uppercase;letter-spacing:.05em;font-weight:700;padding:.35rem .5rem;text-align:left;white-space:nowrap}
.dq-dt td{padding:.32rem .5rem;border-top:1px solid var(--dq-border);font-size:.62rem;white-space:nowrap}
.dq-dt tr.dq-row--bad td{background:rgba(239,68,68,.04)}
.dq-dt tr.dq-row--warn td{background:rgba(245,158,11,.04)}
.dq-cell--err{color:#ef4444;font-weight:700}
.dq-cell--warn{color:#d97706;font-weight:700}
.dq-rules{width:100%;font-size:.66rem;border-collapse:separate;border-spacing:0}
.dq-rules th{font-size:.58rem;text-transform:uppercase;letter-spacing:.05em;font-weight:700;padding:.35rem .55rem;text-align:left;opacity:.5;border-bottom:1px solid var(--dq-border)}
.dq-rules td{padding:.4rem .55rem;border-bottom:1px solid var(--dq-border);vertical-align:middle}
.dq-rules tr:last-child td{border-bottom:none}
.dq-rule-badge{display:inline-block;padding:.1rem .45rem;border-radius:6px;font-size:.58rem;font-weight:700;background:rgba(16,185,129,.1);color:var(--dq-accent);border:1px solid rgba(16,185,129,.15)}
.dq-rule-status{display:inline-block;width:22px;height:22px;border-radius:50%;font-size:.7rem;text-align:center;line-height:22px}
.dq-rule-status--pass{background:rgba(16,185,129,.15);color:#059669}
.dq-rule-status--fail{background:rgba(239,68,68,.15);color:#dc2626}
.dq-rule-status--pending{background:rgba(107,114,128,.1);color:#9ca3af}
.dq-rule-status--running{background:rgba(99,102,241,.15);color:#6366f1;animation:dqSpin .6s linear infinite;display:inline-block}
.dq-run-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.55rem 1.5rem;border-radius:10px;font-size:.78rem;font-weight:800;border:none;cursor:pointer;background:linear-gradient(135deg,#10b981,#059669);color:#fff;transition:all .2s}
.dq-run-btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 4px 16px rgba(16,185,129,.3)}
.dq-run-btn:disabled{opacity:.55;cursor:not-allowed}
.dq-score-wrap{display:grid;grid-template-columns:auto 1fr;gap:1.5rem;align-items:center}
@media(max-width:600px){.dq-score-wrap{grid-template-columns:1fr}}
.dq-score-ring{position:relative;width:100px;height:100px;flex-shrink:0}
.dq-score-ring svg{transform:rotate(-90deg)}
.dq-score-ring-text{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.dq-score-num{font-size:1.6rem;font-weight:900;color:var(--dq-accent);line-height:1}
.dq-score-pct{font-size:.6rem;opacity:.5;font-weight:600}
.dq-col-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:.5rem}
.dq-col-badge{background:rgba(16,185,129,.05);border:1px solid var(--dq-border);border-radius:10px;padding:.5rem .6rem;font-size:.63rem}
.dq-col-badge--fail{background:rgba(239,68,68,.05);border-color:rgba(239,68,68,.15)}
.dq-col-badge-name{font-weight:700;margin-bottom:.2rem}
.dq-col-badge-stat{font-size:.58rem;display:flex;align-items:center;gap:.3rem;color:var(--dq-muted)}
.dq-dimension-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem;margin-top:.75rem}
@media(max-width:600px){.dq-dimension-grid{grid-template-columns:repeat(2,1fr)}}
.dq-dim{text-align:center;background:rgba(16,185,129,.04);border:1px solid var(--dq-border);border-radius:10px;padding:.6rem .4rem}
.dq-dim-val{font-size:1rem;font-weight:800;color:var(--dq-accent)}
.dq-dim-fail .dq-dim-val{color:#ef4444}
.dq-dim-lbl{font-size:.58rem;text-transform:uppercase;letter-spacing:.04em;color:var(--dq-muted);margin-top:.2rem;font-weight:600}
.dq-arch{background:rgba(16,185,129,.03);border:1px solid rgba(16,185,129,.1);border-radius:10px;padding:.6rem .75rem;font-size:.6rem;line-height:1.6;color:var(--dq-muted);margin-top:.75rem}
.dq-arch strong{color:var(--dq-accent);font-weight:700}
.dq-arch-title{font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--dq-accent);margin-bottom:.25rem}

/* ══ 7-ideations wrapper ══ */
:root{--dq2-radius:16px}
.dq-progress{position:fixed;top:0;left:0;right:0;height:3px;background:rgba(16,185,129,.12);z-index:9999}
.dq-progress-fill{height:100%;background:linear-gradient(90deg,#10b981,#059669);width:0%;transition:width .2s}
.dq-nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--dq-border);display:flex;overflow-x:auto;padding:0 1rem}
[data-theme="dark"] .dq-nav{background:rgba(10,22,16,.92)}
.dq-nav-btn{flex-shrink:0;padding:.7rem 1rem;font-size:.72rem;font-weight:700;border:none;background:transparent;color:var(--dq-muted);cursor:pointer;border-bottom:2px solid transparent;transition:all .2s}
.dq-nav-btn.active{color:var(--dq-accent);border-bottom-color:var(--dq-accent)}
.dq-section{padding:2rem 0;min-height:38vh}
.dq-sec-head{text-align:center;margin-bottom:1.6rem}
.dq-sec-head h2{font-size:1.35rem;font-weight:800;margin-bottom:.3rem}
.dq-sec-head p{font-size:.82rem;color:var(--dq-muted);max-width:600px;margin:0 auto;line-height:1.6}
/* story */
.dq-story-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin-top:1.5rem}
.dq-step{background:var(--dq-surface);border:1px solid var(--dq-border);border-radius:var(--dq2-radius);padding:1.1rem 1.2rem}
.dq-step-num{font-size:.6rem;font-weight:800;color:var(--dq-accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem}
.dq-step h4{font-size:.82rem;font-weight:800;margin-bottom:.35rem}
.dq-step p{font-size:.72rem;color:var(--dq-muted);line-height:1.6;margin:0}
/* ELI5 */
.dq-mode-bar{display:flex;gap:.5rem;margin-bottom:1.5rem;justify-content:center}
.dq-mode-btn{padding:.45rem 1.4rem;border-radius:999px;font-size:.78rem;font-weight:700;border:2px solid var(--dq-border);background:transparent;color:var(--dq-muted);cursor:pointer;transition:all .2s}
.dq-mode-btn.active{background:var(--dq-accent);border-color:var(--dq-accent);color:#fff}
.dq-pane{display:none}.dq-pane.active{display:block}
.dq-persona-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.75rem;margin-bottom:1.2rem}
.dq-persona{border:2px solid var(--dq-border);border-radius:var(--dq2-radius);padding:.9rem 1rem;cursor:pointer;transition:all .2s;background:var(--dq-surface);text-align:center}
.dq-persona:hover{transform:translateY(-2px)}
.dq-persona.selected{border-color:var(--dq-accent);background:rgba(16,185,129,.05)}
.dq-persona-icon{font-size:1.6rem;margin-bottom:.4rem}
.dq-persona-label{font-size:.75rem;font-weight:700}
.dq-persona-sub{font-size:.65rem;color:var(--dq-muted);margin-top:.15rem}
.dq-eli5-run{display:block;margin:.8rem auto 1rem;padding:.5rem 2rem;background:linear-gradient(135deg,#10b981,#059669);color:#fff;border:none;border-radius:999px;font-size:.8rem;font-weight:700;cursor:pointer}
.dq-eli5-result{background:var(--dq-surface);border:1px solid var(--dq-border);border-radius:var(--dq2-radius);padding:1.2rem 1.4rem;display:none;animation:dqUp .3s ease both}
.dq-eli5-result.show{display:block}
.dq-eli5-title{font-size:.88rem;font-weight:800;margin-bottom:.5rem;color:var(--dq-accent)}
.dq-eli5-body{font-size:.78rem;line-height:1.7;color:var(--dq-muted)}
.dq-eli5-stat{display:inline-block;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.18);border-radius:8px;padding:.3rem .7rem;font-size:.72rem;font-weight:700;color:var(--dq-accent);margin:.4rem .3rem 0 0}
/* classroom */
.dq-cls-wrap{max-width:780px;margin:0 auto}
.dq-cls-track{overflow:hidden;border-radius:var(--dq2-radius);border:1px solid var(--dq-border)}
.dq-cls-slide{display:none;padding:2rem 2.2rem;background:var(--dq-surface);min-height:260px}
.dq-cls-slide.active{display:block;animation:dqUp .3s ease both}
.dq-cls-num{font-size:.6rem;font-weight:800;color:var(--dq-accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem}
.dq-cls-slide h3{font-size:1.05rem;font-weight:800;margin-bottom:.7rem}
.dq-cls-slide p{font-size:.8rem;line-height:1.72;color:var(--dq-muted);margin-bottom:.7rem}
.dq-cls-formula{font-family:'Cascadia Code',monospace;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.14);border-radius:10px;padding:.7rem 1rem;font-size:.75rem;color:var(--dq-accent);margin:.5rem 0}
.dq-cls-nav{display:flex;align-items:center;justify-content:space-between;margin-top:1rem}
.dq-cls-nav-btn{padding:.4rem .9rem;border-radius:8px;border:1px solid var(--dq-border);background:var(--dq-surface);font-size:.72rem;font-weight:700;cursor:pointer;color:var(--dq-muted);transition:all .2s}
.dq-cls-nav-btn:hover{background:var(--dq-accent);color:#fff;border-color:var(--dq-accent)}
.dq-cls-dots{display:flex;gap:.4rem}
.dq-cls-dot{width:7px;height:7px;border-radius:50%;background:var(--dq-border);cursor:pointer;transition:all .2s}
.dq-cls-dot.active{background:var(--dq-accent);transform:scale(1.2)}
/* keypoints */
.dq-kp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}
.dq-kp{background:var(--dq-surface);border:1px solid var(--dq-border);border-radius:var(--dq2-radius);padding:1.2rem;position:relative;overflow:hidden}
.dq-kp::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#10b981,#059669)}
.dq-kp-icon{font-size:1.4rem;margin-bottom:.5rem}
.dq-kp h4{font-size:.82rem;font-weight:800;margin-bottom:.4rem}
.dq-kp p{font-size:.72rem;color:var(--dq-muted);line-height:1.6;margin:0}
/* code */
.dq-code-blocks{max-width:940px;margin:0 auto}
.dq-code-block{border-radius:14px;border:1px solid var(--dq-border);background:var(--dq-surface);margin-bottom:.8rem;overflow:hidden}
.dq-code-block summary{padding:.75rem 1.1rem;font-size:.82rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.dq-code-block summary::-webkit-details-marker{display:none}
.dq-code-block summary::before{content:'&#9654;';font-size:.6rem;transition:transform .2s}
.dq-code-block[open] summary::before{transform:rotate(90deg)}
.dq-code-block pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;line-height:1.6;overflow-x:auto;border-top:1px solid var(--dq-border);font-family:'Cascadia Code','JetBrains Mono',monospace}
.dq-code-block .kw{color:#c4b5fd}.dq-code-block .fn{color:#6ee7b7}.dq-code-block .cm{color:#64748b;font-style:italic}.dq-code-block .str{color:#fcd34d}.dq-code-block .num{color:#f97316}
/* about */
.dq-about-card{max-width:560px;margin:0 auto;background:var(--dq-surface);border:1px solid var(--dq-border);border-radius:24px;padding:2rem;text-align:center}
.dq-about-card h3{font-size:1.05rem;font-weight:800;margin-bottom:.4rem}
.dq-about-card p{font-size:.78rem;color:var(--dq-muted);line-height:1.6;margin-bottom:1rem}
.dq-share-btn{padding:.5rem 1.4rem;border-radius:999px;background:var(--dq-accent);color:#fff;border:none;font-size:.78rem;font-weight:700;cursor:pointer;transition:all .2s}
</style>

<div class="dq-progress"><div class="dq-progress-fill" id="dqProgressFill"></div></div>

<nav class="dq-nav" id="dqNav">
  <button class="dq-nav-btn active" onclick="dqScrollTo('dq-story')">&#128218; Story</button>
  <button class="dq-nav-btn" onclick="dqScrollTo('dq-demo')">&#9658; Demo</button>
  <button class="dq-nav-btn" onclick="dqScrollTo('dq-classroom')">&#127979; Classroom</button>
  <button class="dq-nav-btn" onclick="dqScrollTo('dq-keypoints')">&#128161; Key Points</button>
  <button class="dq-nav-btn" onclick="dqScrollTo('dq-code')">&#128187; Code</button>
  <button class="dq-nav-btn" onclick="dqScrollTo('dq-about')">&#127760; About</button>
</nav>

<div class="dq-wrap">

<!-- ══ STORY ══ -->
<section class="dq-section" id="dq-story">
  <div class="dq-sec-head">
    <div class="dq-tag"><i class="fas fa-shield-alt me-1"></i> Omni Hotels &amp; Resorts &#8212; Data Quality</div>
    <h2>Reservation Data Quality Framework</h2>
    <p>Validate Omni Hotels reservation data against a production rule suite &#8212; powering reliable revenue management and personalized guest experiences across 50+ properties.</p>
  </div>
  <div class="dq-story-steps">
    <div class="dq-step">
      <div class="dq-step-num">Step 1 &#8212; The Stakes</div>
      <h4>Bad Data, Broken Stays</h4>
      <p>A single invalid check-out date cascades into wrong ADR calculations, broken forecasting models, and misrouted loyalty rewards. Omni processes 4,000+ reservations per night across 50 properties. At 2% error rate, that&#39;s 80 corrupted records per night compounding into the data warehouse.</p>
    </div>
    <div class="dq-step">
      <div class="dq-step-num">Step 2 &#8212; The Data Flow</div>
      <h4>Opera PMS &#8594; Snowflake &#8594; Analytics</h4>
      <p>Opera Property Management System (the industry-standard hotel PMS) pushes reservation records nightly via ETL into Snowflake. Revenue management, marketing, and loyalty systems all read from this warehouse. Data quality must be enforced at ingestion &#8212; before downstream systems consume corrupt data.</p>
    </div>
    <div class="dq-step">
      <div class="dq-step-num">Step 3 &#8212; The Framework</div>
      <h4>Great Expectations: Rules as Code</h4>
      <p>Great Expectations defines data quality rules declaratively (&#34;expect_column_values_to_be_between&#34;) and executes them as unit tests against each batch. Rules are version-controlled alongside pipeline code &#8212; breaking data is caught in CI just like breaking code.</p>
    </div>
    <div class="dq-step">
      <div class="dq-step-num">Step 4 &#8212; 5 Dimensions</div>
      <h4>Completeness, Validity, Uniqueness, Timeliness, Consistency</h4>
      <p>The CVUTC framework maps each rule to a business risk: Completeness gaps break loyalty profiles. Validity failures skew revenue reports. Uniqueness violations cause double-billing. Timeliness failures corrupt forecasting models. Consistency failures break date-range analytics.</p>
    </div>
    <div class="dq-step">
      <div class="dq-step-num">Step 5 &#8212; Root Cause</div>
      <h4>Where Errors Actually Come From</h4>
      <p>72% of hotel data errors originate at front desk entry (walk-in guests, rate overrides, manual corrections). 18% come from OTA (booking.com, Expedia) field mapping mismatches. 10% are system sync glitches (duplicate res_id on failover). Each error type needs a different remediation strategy.</p>
    </div>
    <div class="dq-step">
      <div class="dq-step-num">Step 6 &#8212; The Feedback Loop</div>
      <h4>From Report to Fix in 4 Hours</h4>
      <p>Quality failures generate Jira tickets, tagged by dimension and source system, routed to the owning team. Revenue management failures alert the RM director directly. SLA: critical failures (rate = $0, checkout &lt; checkin) fixed within 4 hours. Non-critical within 24. Trend dashboard shows improvement over time.</p>
    </div>
  </div>
</section>

<!-- ══ DEMO ══ -->
<section class="dq-section" id="dq-demo">
  <div class="dq-sec-head">
    <h2>Interactive Demo</h2>
    <p>Run the validation suite against 10 real Omni Hotels reservations with intentional quality issues.</p>
  </div>
  <div class="dq-mode-bar">
    <button class="dq-mode-btn active" data-mode="eli5" onclick="dqSetMode('eli5')">&#x1F4A1; ELI5</button>
    <button class="dq-mode-btn" data-mode="engineer" onclick="dqSetMode('engineer')">&#x2699; Engineer</button>
  </div>

  <!-- ELI5 pane -->
  <div class="dq-pane active" data-pane="eli5">
    <div class="dq-persona-grid">
      <div class="dq-persona" data-key="steward" onclick="dqSelectPersona('steward')">
        <div class="dq-persona-icon">&#x1F4CB;</div>
        <div class="dq-persona-label">Data Steward</div>
        <div class="dq-persona-sub">&#8220;I own the quality of this pipeline&#8221;</div>
      </div>
      <div class="dq-persona" data-key="analyst" onclick="dqSelectPersona('analyst')">
        <div class="dq-persona-icon">&#x1F4CA;</div>
        <div class="dq-persona-label">BI Analyst</div>
        <div class="dq-persona-sub">&#8220;My dashboards depend on clean data&#8221;</div>
      </div>
      <div class="dq-persona" data-key="dba" onclick="dqSelectPersona('dba')">
        <div class="dq-persona-icon">&#x1F5C3;</div>
        <div class="dq-persona-label">DBA</div>
        <div class="dq-persona-sub">&#8220;Enforce constraints at the source&#8221;</div>
      </div>
      <div class="dq-persona" data-key="revenue" onclick="dqSelectPersona('revenue')">
        <div class="dq-persona-icon">&#x1F4B0;</div>
        <div class="dq-persona-label">Revenue Manager</div>
        <div class="dq-persona-sub">&#8220;Bad rates destroy my ADR metric&#8221;</div>
      </div>
    </div>
    <button class="dq-eli5-run" onclick="dqRunELI5()">&#9654; Run Simulation</button>
    <div class="dq-eli5-result" id="dqELI5Result">
      <div class="dq-eli5-title" id="dqELI5Title"></div>
      <div class="dq-eli5-body" id="dqELI5Body"></div>
      <div id="dqELI5Stats"></div>
    </div>
  </div>

  <!-- Engineer pane — existing interactive demo -->
  <div class="dq-pane" data-pane="engineer">
  <div class="dq-grid">
    <div class="dq-panel">
      <div class="dq-panel-hd"><i class="fas fa-table"></i> Reservation Extract &#8212; Omni Hotels
        <span class="dq-badge">10 rows &#183; 10 columns &#183; issues highlighted</span>
      </div>
      <div style="overflow-x:auto">
        <table class="dq-dt">
          <thead><tr><th>res_id</th><th>guest_name</th><th>email</th><th>phone</th><th>check_in</th><th>check_out</th><th>room_type</th><th>rate</th><th>loyalty</th><th>property</th></tr></thead>
          <tbody id="dqDataBody"></tbody>
        </table>
      </div>
      <div class="dq-arch">
        <div class="dq-arch-title"><i class="fas fa-hotel me-1"></i> Why This Matters at Omni</div>
        Omni Hotels operates <strong>50+ properties</strong> across North America. Reservation data flows from
        <strong>Opera PMS</strong> into the data warehouse nightly. Revenue management models depend on accurate
        rates, dates, and loyalty tiers. A single invalid check-out date can cascade into
        <strong>incorrect ADR calculations</strong>, broken forecasting models, and misrouted loyalty rewards.
      </div>
    </div>
    <div class="dq-panel">
      <div class="dq-panel-hd"><i class="fas fa-list-check"></i> Validation Suite &#8212; Great Expectations Style
        <span style="margin-left:auto">
          <button class="dq-run-btn" id="dqRunBtn"><i class="fas fa-play"></i> Run Suite</button>
        </span>
      </div>
      <table class="dq-rules">
        <thead><tr><th>Column</th><th>Expectation</th><th>Parameter</th><th>Failures</th><th></th></tr></thead>
        <tbody id="dqRulesBody"></tbody>
      </table>
    </div>
    <div class="dq-panel" id="dqScorePanel" style="display:none">
      <div class="dq-panel-hd"><i class="fas fa-chart-pie"></i> Quality Report</div>
      <div class="dq-score-wrap">
        <div style="text-align:center">
          <div class="dq-score-ring">
            <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="40" stroke="var(--dq-border)" stroke-width="10"/>
              <circle cx="50" cy="50" r="40" stroke="var(--dq-accent)" stroke-width="10"
                stroke-dasharray="251.2" stroke-dashoffset="251.2" stroke-linecap="round"
                id="dqRingPath" style="transition:stroke-dashoffset 1s ease"/>
            </svg>
            <div class="dq-score-ring-text"><span class="dq-score-num" id="dqScoreNum">0</span><span class="dq-score-pct">DQ Score</span></div>
          </div>
        </div>
        <div>
          <div style="font-size:.72rem;font-weight:800;margin-bottom:.5rem">Per-Column Results</div>
          <div class="dq-col-grid" id="dqColGrid"></div>
        </div>
      </div>
      <div style="font-size:.72rem;font-weight:800;margin-top:.9rem;margin-bottom:.5rem">Quality Dimensions</div>
      <div class="dq-dimension-grid" id="dqDimGrid"></div>
      <div class="dq-arch" style="margin-top:.65rem">
        <div class="dq-arch-title"><i class="fas fa-chart-line me-1"></i> Downstream Impact</div>
        Quality failures directly affect: <strong>Revenue Management</strong> (ADR, RevPAR miscalculations),
        <strong>Loyalty Program</strong> (incorrect tier assignments),
        <strong>Marketing</strong> (invalid emails = wasted campaign spend),
        and <strong>Operations</strong> (overbooking from date errors).
      </div>
    </div>
  </div>
  </div><!-- /engineer pane -->
</section>
''')
out.close()
print('dq1 done')
