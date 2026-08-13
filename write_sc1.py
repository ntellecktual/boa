"""write_sc1.py — supply_chain.html 7-ideations (part 1/2, write)"""
TMPL = r'boaapp/templates/boaapp/supply_chain.html'
out = open(TMPL, 'w', encoding='utf-8')
out.write(r'''{% extends 'boaapp/base_generic.html' %}
{% load static %}
{% block title %}Supply Chain — Amazon Fulfillment{% endblock %}
{% block container_class %}sc-shell{% endblock %}
{% block content %}
<style>
/* ══ base ══ */
.sc-shell{display:block;width:100%;max-width:100%;padding:0}
:root{--sc-accent:#ff9900;--sc-accent2:#e88b00;--sc-surface:#fff;--sc-border:rgba(0,0,0,.07);--sc-shadow:0 2px 12px rgba(0,0,0,.06);--sc-muted:#6b7280;--sc-dark:#232f3e;--sc-radius:16px}
[data-theme="dark"]{--sc-surface:rgba(22,20,16,.97);--sc-border:rgba(255,255,255,.08);--sc-shadow:0 2px 12px rgba(0,0,0,.35);--sc-muted:#94a3b8}
@keyframes scUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.sc-wrap{max-width:1200px;margin:0 auto;padding:0 1.5rem 4rem}
/* ══ progress bar ══ */
.sc-progress{position:fixed;top:0;left:0;right:0;height:3px;background:rgba(255,153,0,.12);z-index:2000}
.sc-progress-fill{height:100%;width:0%;background:linear-gradient(90deg,#ff9900,#e88b00);transition:width .15s}
/* ══ sticky nav ══ */
.sc-nav{position:sticky;top:0;z-index:999;display:flex;gap:.35rem;background:var(--sc-surface);border-bottom:1px solid var(--sc-border);padding:.55rem 1rem;backdrop-filter:blur(12px);flex-wrap:wrap}
.sc-nav-btn{padding:.32rem .85rem;border-radius:999px;font-size:.72rem;font-weight:700;border:1px solid transparent;background:transparent;cursor:pointer;color:var(--sc-muted);transition:all .18s}
.sc-nav-btn:hover,.sc-nav-btn.active{background:linear-gradient(135deg,#ff9900,#e88b00);color:#fff;border-color:transparent}
/* ══ section ══ */
.sc-section{padding:2.4rem 0 1.2rem;animation:scUp .5s ease both}
.sc-sec-head{text-align:center;margin-bottom:1.6rem}
.sc-sec-head h2{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:800;margin-bottom:.3rem}
.sc-sec-head p{font-size:.88rem;color:var(--sc-muted);max-width:560px;margin:0 auto;line-height:1.6}
/* ══ hero ══ */
.sc-hero{text-align:center;padding:2.2rem 0 1.4rem;animation:scUp .4s ease both}
.sc-tag{display:inline-block;padding:.22rem .85rem;border-radius:999px;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;background:rgba(255,153,0,.09);border:1px solid rgba(255,153,0,.2);color:var(--sc-accent);margin-bottom:.65rem}
.sc-hero h1{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;background:linear-gradient(135deg,#ff9900,#232f3e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.4rem}
.sc-hero p{font-size:.88rem;color:var(--sc-muted);max-width:580px;margin:0 auto 0;line-height:1.6}
.sc-hero-context{display:inline-flex;align-items:center;gap:.5rem;margin-top:.7rem;padding:.4rem .9rem;border-radius:10px;background:rgba(255,153,0,.04);border:1px solid rgba(255,153,0,.12);font-size:.68rem;color:var(--sc-muted)}
.sc-hero-context strong{color:var(--sc-accent);font-weight:800}
/* ══ story ══ */
.sc-story-steps{display:grid;gap:1rem;max-width:900px;margin:0 auto}
.sc-step{display:flex;gap:1.1rem;align-items:flex-start;background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:var(--sc-radius);padding:1.1rem 1.3rem;box-shadow:var(--sc-shadow)}
.sc-step-num{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#ff9900,#e88b00);color:#fff;font-size:.78rem;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.sc-step-body h4{font-size:.88rem;font-weight:800;margin:0 0 .25rem}
.sc-step-body p{font-size:.82rem;color:var(--sc-muted);margin:0;line-height:1.55}
/* ══ demo mode bar ══ */
.sc-mode-bar{display:flex;gap:.5rem;max-width:700px;margin:0 auto 1.4rem;background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:999px;padding:.25rem;box-shadow:var(--sc-shadow)}
.sc-mode-tab{flex:1;padding:.38rem 0;border-radius:999px;font-size:.75rem;font-weight:700;border:none;background:transparent;cursor:pointer;color:var(--sc-muted);transition:all .18s}
.sc-mode-tab.active{background:linear-gradient(135deg,#ff9900,#e88b00);color:#fff}
/* ══ demo panes ══ */
.sc-pane{display:none}
.sc-pane.active{display:block}
/* ══ ELI5 ══ */
.sc-persona-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;max-width:900px;margin:0 auto 1.2rem}
@media(max-width:700px){.sc-persona-grid{grid-template-columns:1fr 1fr}}
.sc-persona{background:var(--sc-surface);border:2px solid var(--sc-border);border-radius:var(--sc-radius);padding:.9rem .7rem;text-align:center;cursor:pointer;transition:all .18s}
.sc-persona:hover,.sc-persona.selected{border-color:var(--sc-accent);box-shadow:0 0 0 3px rgba(255,153,0,.12)}
.sc-persona-icon{font-size:1.6rem;margin-bottom:.35rem}
.sc-persona-label{font-size:.75rem;font-weight:800;margin-bottom:.15rem}
.sc-persona-sub{font-size:.63rem;color:var(--sc-muted)}
.sc-eli5-run{display:block;margin:.6rem auto 0;padding:.5rem 1.6rem;border-radius:999px;font-size:.78rem;font-weight:700;background:linear-gradient(135deg,#ff9900,#e88b00);color:#fff;border:none;cursor:pointer}
.sc-eli5-result{display:none;max-width:860px;margin:1.1rem auto 0;background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:var(--sc-radius);padding:1.2rem 1.4rem;box-shadow:var(--sc-shadow)}
.sc-eli5-result.show{display:block}
.sc-eli5-title{font-size:.93rem;font-weight:800;margin-bottom:.65rem}
.sc-eli5-body{font-size:.83rem;color:var(--sc-muted);line-height:1.65;margin-bottom:.85rem}
.sc-eli5-stats{display:flex;flex-wrap:wrap;gap:.5rem}
.sc-eli5-stat{font-size:.68rem;font-weight:700;padding:.25rem .7rem;border-radius:999px;background:rgba(255,153,0,.09);color:var(--sc-accent);border:1px solid rgba(255,153,0,.14)}
/* ══ Engineer pane ══ */
.sc-body{display:grid;grid-template-columns:290px 1fr;gap:1rem}
@media(max-width:800px){.sc-body{grid-template-columns:1fr}}
.sc-panel{background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:var(--sc-radius);box-shadow:var(--sc-shadow);padding:1.1rem}
.sc-chart-wrap{position:relative;width:100%;height:260px}
.sc-panel-hd{display:flex;align-items:center;gap:.45rem;font-size:.75rem;font-weight:800;margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:1px solid var(--sc-border)}
.sc-panel-hd i{color:var(--sc-accent);opacity:.8}
.sc-panel-hd .sc-badge{margin-left:auto;font-size:.56rem;font-weight:700;padding:.14rem .5rem;border-radius:999px;background:rgba(255,153,0,.08);color:var(--sc-accent);border:1px solid rgba(255,153,0,.14)}
.sc-sku-row{display:flex;align-items:center;gap:.4rem;margin-bottom:.85rem;flex-wrap:wrap}
.sc-sku-chip{padding:.2rem .55rem;border-radius:7px;font-size:.62rem;font-weight:700;border:1px solid var(--sc-border);cursor:pointer;transition:all .18s;background:transparent;color:var(--sc-muted)}
.sc-sku-chip.active{background:rgba(255,153,0,.1);border-color:rgba(255,153,0,.3);color:var(--sc-accent)}
.sc-sku-chip:hover:not(.active){border-color:rgba(255,153,0,.2)}
.sc-sku-label{font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--sc-muted)}
.sc-slider-row{margin-bottom:.85rem}
.sc-slider-label{display:flex;justify-content:space-between;align-items:center;font-size:.68rem;font-weight:700;margin-bottom:.28rem}
.sc-slider-label span{font-weight:400;color:var(--sc-accent);font-size:.7rem;font-family:'Cascadia Code',monospace}
.sc-slider-sub{font-size:.56rem;color:var(--sc-muted);margin-bottom:.25rem}
input[type="range"].sc-range{width:100%;height:5px;border-radius:3px;appearance:none;-webkit-appearance:none;background:var(--sc-border);outline:none;cursor:pointer}
input[type="range"].sc-range::-webkit-slider-thumb{appearance:none;-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--sc-accent);border:2px solid var(--sc-surface);box-shadow:0 1px 4px rgba(0,0,0,.2)}
.sc-eq{background:rgba(255,153,0,.05);border:1px solid rgba(255,153,0,.12);border-radius:10px;padding:.6rem .8rem;font-size:.66rem;font-family:'Cascadia Code',monospace;line-height:1.75;margin-bottom:.85rem}
.sc-eq-title{font-size:.58rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700;color:var(--sc-muted);margin-bottom:.2rem;font-family:inherit}
.sc-arch{background:rgba(255,153,0,.03);border:1px solid rgba(255,153,0,.1);border-radius:10px;padding:.6rem .75rem;font-size:.6rem;line-height:1.6;color:var(--sc-muted);margin-top:.65rem}
.sc-arch strong{color:var(--sc-accent);font-weight:700}
.sc-arch-title{font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--sc-accent);margin-bottom:.25rem}
.sc-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:.65rem;margin-top:.9rem}
@media(max-width:700px){.sc-kpis{grid-template-columns:repeat(2,1fr)}}
.sc-kpi{background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:14px;box-shadow:var(--sc-shadow);padding:.8rem .65rem;text-align:center}
.sc-kpi-val{font-size:1.3rem;font-weight:900;line-height:1;color:var(--sc-accent)}
.sc-kpi-label{font-size:.58rem;text-transform:uppercase;letter-spacing:.05em;font-weight:600;color:var(--sc-muted);margin-top:.2rem}
.sc-kpi-sub{font-size:.54rem;color:var(--sc-muted);opacity:.6;margin-top:.12rem}
.sc-tabs{display:flex;gap:.35rem;margin-bottom:.75rem}
.sc-tab{padding:.28rem .7rem;border-radius:8px;font-size:.66rem;font-weight:700;border:1px solid var(--sc-border);background:transparent;color:var(--sc-muted);cursor:pointer;transition:all .18s}
.sc-tab.active{background:linear-gradient(135deg,#ff9900,#e88b00);color:#fff;border-color:transparent}
.sc-tab:hover:not(.active){border-color:rgba(255,153,0,.35);color:var(--sc-accent)}
.sc-legend{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:.6rem;font-size:.63rem;color:var(--sc-muted)}
.sc-leg-item{display:flex;align-items:center;gap:.3rem}
.sc-leg-dot{width:10px;height:10px;border-radius:2px;flex-shrink:0}
.sc-stats-row{display:flex;gap:.7rem;font-size:.66rem;color:var(--sc-muted);margin-top:.45rem;flex-wrap:wrap}
.sc-stat{display:flex;align-items:center;gap:.3rem}
.sc-stat strong{color:inherit;font-weight:700}
.sc-stat-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
/* ══ classroom ══ */
.sc-cls-wrap{max-width:860px;margin:0 auto}
.sc-cls-track{position:relative;min-height:260px}
.sc-cls-slide{display:none;animation:scUp .35s ease}
.sc-cls-slide.active{display:block}
.sc-cls-slide h3{font-size:1.05rem;font-weight:800;margin-bottom:.65rem}
.sc-cls-slide p{font-size:.84rem;color:var(--sc-muted);line-height:1.65;margin-bottom:.7rem}
.sc-cls-num{font-size:.62rem;font-weight:700;color:var(--sc-accent);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.45rem}
.sc-cls-formula{background:rgba(255,153,0,.06);border:1px solid rgba(255,153,0,.14);border-radius:10px;padding:.65rem 1rem;font-size:.74rem;font-family:'Cascadia Code','JetBrains Mono',monospace;color:var(--sc-accent);margin-top:.7rem}
.sc-cls-nav{display:flex;align-items:center;justify-content:center;gap:1rem;margin-top:1.2rem}
.sc-cls-nav-btn{padding:.38rem 1.2rem;border-radius:999px;font-size:.78rem;font-weight:700;border:1px solid var(--sc-border);background:var(--sc-surface);cursor:pointer;transition:all .18s}
.sc-cls-nav-btn:hover{border-color:var(--sc-accent);color:var(--sc-accent)}
.sc-cls-dots{display:flex;gap:.5rem;align-items:center}
.sc-cls-dot{width:9px;height:9px;border-radius:50%;background:var(--sc-border);cursor:pointer;transition:all .18s}
.sc-cls-dot.active{background:var(--sc-accent);transform:scale(1.2)}
/* ══ key points ══ */
.sc-kp-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;max-width:900px;margin:0 auto}
@media(max-width:700px){.sc-kp-grid{grid-template-columns:1fr}}
.sc-kp{background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:var(--sc-radius);padding:1.2rem 1.4rem;box-shadow:var(--sc-shadow)}
.sc-kp-icon{font-size:1.6rem;margin-bottom:.5rem}
.sc-kp h4{font-size:.9rem;font-weight:800;margin-bottom:.4rem}
.sc-kp p{font-size:.82rem;color:var(--sc-muted);margin:0;line-height:1.55}
/* ══ code blocks ══ */
.sc-code-blocks{max-width:900px;margin:0 auto}
.sc-code-block{border:1px solid var(--sc-border);border-radius:var(--sc-radius);background:var(--sc-surface);margin-bottom:.85rem;overflow:hidden;box-shadow:var(--sc-shadow)}
.sc-code-block summary{padding:.8rem 1.2rem;font-size:.83rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.5rem;list-style:none}
.sc-code-block summary::-webkit-details-marker{display:none}
.sc-code-block summary::before{content:'&#x25B6;';font-size:.6rem;transition:transform .2s}
.sc-code-block[open] summary::before{transform:rotate(90deg)}
.sc-code-block pre{margin:0;padding:1rem 1.2rem;background:#0f172a;color:#e2e8f0;font-size:.68rem;line-height:1.65;overflow-x:auto;border-top:1px solid var(--sc-border);font-family:'Cascadia Code','JetBrains Mono',monospace}
.sc-code-block code{background:none;padding:0;color:inherit}
.sc-code-block .kw{color:#c4b5fd}.sc-code-block .fn{color:#6ee7b7}.sc-code-block .str{color:#fcd34d}.sc-code-block .cm{color:#64748b;font-style:italic}.sc-code-block .num{color:#f97316}
/* ══ about ══ */
.sc-about-card{max-width:600px;margin:0 auto;background:var(--sc-surface);border:1px solid var(--sc-border);border-radius:var(--sc-radius);padding:1.8rem;text-align:center;box-shadow:var(--sc-shadow)}
.sc-about-card h3{font-size:1.05rem;font-weight:800;margin-bottom:.6rem}
.sc-about-card p{font-size:.83rem;color:var(--sc-muted);line-height:1.6;margin-bottom:.7rem}
.sc-share-btn{padding:.45rem 1.4rem;border-radius:999px;font-size:.78rem;font-weight:700;border:1px solid var(--sc-border);background:var(--sc-surface);cursor:pointer;transition:all .18s}
.sc-share-btn:hover{border-color:var(--sc-accent);color:var(--sc-accent)}
</style>

<div class="sc-progress"><div class="sc-progress-fill" id="scProgressFill"></div></div>

<nav class="sc-nav" id="scNav">
  <button class="sc-nav-btn active" onclick="scScrollTo('sc-story')">Story</button>
  <button class="sc-nav-btn" onclick="scScrollTo('sc-demo')">Demo</button>
  <button class="sc-nav-btn" onclick="scScrollTo('sc-classroom')">Classroom</button>
  <button class="sc-nav-btn" onclick="scScrollTo('sc-keypoints')">Key Points</button>
  <button class="sc-nav-btn" onclick="scScrollTo('sc-code')">Code</button>
  <button class="sc-nav-btn" onclick="scScrollTo('sc-about')">About</button>
</nav>

<div class="sc-wrap">

<div class="sc-hero">
  <div class="sc-tag"><i class="fas fa-warehouse me-1"></i> Amazon &#8212; Fulfillment Center Optimization</div>
  <h1>FC Inventory Optimizer</h1>
  <p>Production EOQ model for Amazon Fulfillment Centers &#8212; optimizes reorder quantity, safety stock, and replenishment timing. Tunes for Prime 2-day SLA compliance while minimizing holding costs across 110+ FCs nationwide.</p>
  <div class="sc-hero-context">
    <i class="fas fa-map-marker-alt" style="color:var(--sc-accent)"></i>
    <span>FC: <strong>BOS5 (Fall River, MA)</strong> &nbsp;|&nbsp; Region: <strong>Northeast</strong> &nbsp;|&nbsp; Prime SLA: <strong>2-Day</strong></span>
  </div>
</div>

<!-- ══ STORY ══ -->
<section class="sc-section" id="sc-story">
  <div class="sc-sec-head">
    <h2>The Story</h2>
    <p>How 47,000 Prime customers received 5-day delivery on Echo Dot &#8212; and the inventory science that fixed it.</p>
  </div>
  <div class="sc-story-steps">
    <div class="sc-step">
      <div class="sc-step-num">1</div>
      <div class="sc-step-body"><h4>The Prime SLA Failure &#8212; Friday Night Stockout</h4>
      <p>At 7 PM on the Friday before Prime Day 2023, BOS5 stocked out of Echo Dot 5th Gen &#8212; the highest-velocity SKU in the Northeast region. 47,000 Prime customers who ordered that weekend received 5-day delivery instead of 2-day. The SLA miss cost $214,000 in shipping credits and generated 8,900 negative reviews. Root cause: safety stock was set manually by a category manager using a spreadsheet, not the demand variance formula.</p></div>
    </div>
    <div class="sc-step">
      <div class="sc-step-num">2</div>
      <div class="sc-step-body"><h4>The Math That Should Have Prevented It &#8212; EOQ</h4>
      <p>The Economic Order Quantity formula &#8212; EOQ = &#x221A;(2DS/H) &#8212; was derived by Ford Harris in 1913. It minimizes total inventory cost by balancing two opposing forces: ordering cost (sending frequent small orders is expensive) and holding cost (warehousing large inventory is expensive). The optimal order size sits at the exact crossover point of these two cost curves. This is not an approximation &#8212; it&#39;s the algebraic minimum of the total cost function.</p></div>
    </div>
    <div class="sc-step">
      <div class="sc-step-num">3</div>
      <div class="sc-step-body"><h4>Safety Stock &#8212; The Probabilistic Buffer</h4>
      <p>EOQ tells you <em>how much</em> to order. Safety stock answers <em>what buffer protects against demand spikes during the lead time window</em>. The formula SS = Z &#183; &#963; &#183; &#x221A;L uses the Z-score for your service level (1.645 for 95% fill rate), the weekly demand standard deviation, and the vendor lead time. The &#x221A;L term is critical: demand uncertainty compounds over the lead time period. A 2-week lead time doesn&#39;t double the risk &#8212; it multiplies by &#x221A;2 &#8594; 41% more buffer needed than a 1-week lead time.</p></div>
    </div>
    <div class="sc-step">
      <div class="sc-step-num">4</div>
      <div class="sc-step-body"><h4>Reorder Point &#8212; When to Pull the Trigger</h4>
      <p>The Reorder Point (ROP = d&#x0305; &#183; L + SS) is the inventory level that triggers a purchase order. When on-hand inventory drops to this level, an order for EOQ units is placed &#8212; and the order arrives exactly when safety stock would be depleted if demand ran at the average rate. The insight: ROP is NOT "when to order so you don&#39;t run out." It&#39;s "when to order so you have a 95% chance of not running out." Setting ROP too high wastes capital; too low and you break the Prime SLA.</p></div>
    </div>
    <div class="sc-step">
      <div class="sc-step-num">5</div>
      <div class="sc-step-body"><h4>Multi-Echelon &#8212; Central Warehouse to Regional DC to FC</h4>
      <p>Amazon&#39;s network is 3-echelon: Central Warehouse (ONT8, CA) &#8594; Regional DC (BOS1) &#8594; Fulfillment Center (BOS5). Each echelon has its own lead time and demand variability. Clark-Scarf decomposition optimizes each echelon independently with nested service levels: 99% at the CW, 97% at the regional DC, 95% at the FC. The key property: by optimizing each stage independently, the total network safety stock is minimized while maintaining the end-to-end Prime SLA.</p></div>
    </div>
    <div class="sc-step">
      <div class="sc-step-num">6</div>
      <div class="sc-step-body"><h4>Zero Prime SLA Misses &#8212; 18 Months After Automation</h4>
      <p>After replacing the spreadsheet-based system with automated EOQ + safety stock computation per SKU per FC, the Northeast region shipped 18 consecutive months with zero Echo Dot SLA misses. Dynamic safety stock now adjusts 48 hours before predicted demand surges (Prime Day, Black Friday) using weather forecasts, social media trend signals, and promotional calendars. Average inventory reduced by 19% while the fill rate improved from 93.2% to 97.4% &#8212; the rare optimization that simultaneously cuts cost and improves service.</p></div>
    </div>
  </div>
</section>

<!-- ══ DEMO ══ -->
<section class="sc-section" id="sc-demo">
  <div class="sc-sec-head">
    <h2>Interactive Demo</h2>
    <p>Select a persona for the plain-English explanation, or switch to Engineer mode for the live EOQ simulation and cost curve.</p>
  </div>
  <div class="sc-mode-bar">
    <button class="sc-mode-tab active" data-pane="eli5" onclick="scSetMode('eli5')">&#x1F4AC; ELI5 Mode</button>
    <button class="sc-mode-tab" data-pane="engineer" onclick="scSetMode('engineer')">&#x2699;&#xFE0F; Engineer Mode</button>
  </div>

  <!-- ELI5 pane -->
  <div class="sc-pane active" data-pane="eli5">
    <div class="sc-persona-grid">
      <div class="sc-persona" data-key="warehouse" onclick="scSelectPersona('warehouse')">
        <div class="sc-persona-icon">&#x1F9F9;</div>
        <div class="sc-persona-label">Warehouse Mgr</div>
        <div class="sc-persona-sub">FC operations</div>
      </div>
      <div class="sc-persona" data-key="planner" onclick="scSelectPersona('planner')">
        <div class="sc-persona-icon">&#x1F4CA;</div>
        <div class="sc-persona-label">Demand Planner</div>
        <div class="sc-persona-sub">Forecast & EOQ</div>
      </div>
      <div class="sc-persona" data-key="finance" onclick="scSelectPersona('finance')">
        <div class="sc-persona-icon">&#x1F4B0;</div>
        <div class="sc-persona-label">Finance Director</div>
        <div class="sc-persona-sub">Capital efficiency</div>
      </div>
      <div class="sc-persona" data-key="prime" onclick="scSelectPersona('prime')">
        <div class="sc-persona-icon">&#x1F4E6;</div>
        <div class="sc-persona-label">Prime Customer</div>
        <div class="sc-persona-sub">Why 5-day delivery?</div>
      </div>
    </div>
    <button class="sc-eli5-run" onclick="scRunELI5()">&#x25B6; Explain It To Me</button>
    <div class="sc-eli5-result" id="scELI5Result">
      <div class="sc-eli5-title" id="scELI5Title"></div>
      <div class="sc-eli5-body" id="scELI5Body"></div>
      <div class="sc-eli5-stats" id="scELI5Stats"></div>
    </div>
  </div>

  <!-- Engineer pane — original interactive demo -->
  <div class="sc-pane" data-pane="engineer">
    <div class="sc-body">
      <div class="sc-panel">
        <div class="sc-panel-hd"><i class="fas fa-sliders-h"></i> SKU Parameters <span class="sc-badge">EOQ + Safety Stock</span></div>
        <div class="sc-sku-row">
          <span class="sc-sku-label">SKU:</span>
          <button class="sc-sku-chip active" data-sku="echo">Echo Dot 5th Gen</button>
          <button class="sc-sku-chip" data-sku="kindle">Kindle Paperwhite</button>
          <button class="sc-sku-chip" data-sku="fire">Fire TV Stick 4K</button>
        </div>
        <div class="sc-slider-row">
          <div class="sc-slider-label">Annual Demand (D) <span id="scValD">52000</span> units</div>
          <div class="sc-slider-sub">Forecasted sell-through for this FC region</div>
          <input type="range" class="sc-range" id="scD" min="5000" max="200000" step="1000" value="52000">
        </div>
        <div class="sc-slider-row">
          <div class="sc-slider-label">Demand Std Dev (&#963;/wk) <span id="scValSigma">85</span> units</div>
          <div class="sc-slider-sub">Weekly demand variability &#8212; spikes during Prime Day, holidays</div>
          <input type="range" class="sc-range" id="scSigma" min="10" max="500" step="5" value="85">
        </div>
        <div class="sc-slider-row">
          <div class="sc-slider-label">Lead Time (L) <span id="scValL">2</span> weeks</div>
          <div class="sc-slider-sub">Inbound shipment from vendor to FC receiving dock</div>
          <input type="range" class="sc-range" id="scL" min="1" max="12" step="1" value="2">
        </div>
        <div class="sc-slider-row">
          <div class="sc-slider-label">Order Cost (S) $<span id="scValS">350</span></div>
          <div class="sc-slider-sub">PO processing, freight, receiving labor per order</div>
          <input type="range" class="sc-range" id="scS" min="50" max="2000" step="25" value="350">
        </div>
        <div class="sc-slider-row">
          <div class="sc-slider-label">Holding Cost (H) $<span id="scValH">8.50</span>/unit/yr</div>
          <div class="sc-slider-sub">FC storage, capital cost, shrinkage, insurance</div>
          <input type="range" class="sc-range" id="scH" min="1" max="40" step="0.5" value="8.5">
        </div>
        <div class="sc-eq">
          <div class="sc-eq-title">Amazon FC Replenishment Model</div>
          EOQ = &#x221A;(2DS / H)<br>
          ROP = d&#x0305;&#xB7;L + Z&#xB7;&#x3C3;&#xB7;&#x221A;L<br>
          SS &nbsp;= 1.645 &#xB7; &#x3C3; &#xB7; &#x221A;L &nbsp;(95% SLA)<br>
          TC &nbsp;= (D/Q)&#xB7;S + (Q/2 + SS)&#xB7;H
        </div>
        <div class="sc-arch">
          <div class="sc-arch-title"><i class="fas fa-brain me-1"></i> Why This Matters at Amazon Scale</div>
          Amazon manages <strong>~12 million</strong> unique ASINs across 110+ FCs. Getting EOQ wrong by 20% on Echo Dot alone wastes <strong>$2.3M/yr</strong> in excess holding or causes Prime SLA misses.
        </div>
      </div>
      <div class="sc-panel">
        <div class="sc-panel-hd"><i class="fas fa-chart-area"></i> 52-Week FC Inventory Simulation <span class="sc-badge" id="scSkuLabel">Echo Dot 5th Gen</span></div>
        <div class="sc-tabs">
          <button class="sc-tab active" id="scTabSim">Simulation</button>
          <button class="sc-tab" id="scTabCurve">Cost Curve</button>
        </div>
        <div class="sc-chart-wrap"><canvas id="scChart"></canvas></div>
        <div class="sc-legend" id="scLegend">
          <span class="sc-leg-item"><span class="sc-leg-dot" style="background:#ff9900"></span>FC On-Hand</span>
          <span class="sc-leg-item"><span class="sc-leg-dot" style="background:#ef4444;opacity:.6"></span>Reorder Point</span>
          <span class="sc-leg-item"><span class="sc-leg-dot" style="background:#3b82f6"></span>Inbound Arrival</span>
          <span class="sc-leg-item"><span class="sc-leg-dot" style="background:#dc2626"></span>Stockout (SLA Miss)</span>
        </div>
        <div class="sc-stats-row" id="scStatsRow"></div>
        <div class="sc-arch" style="margin-top:.65rem">
          <div class="sc-arch-title"><i class="fas fa-truck me-1"></i> FC Network Architecture</div>
          <strong>Inbound:</strong> Vendor ships to FC receiving dock &#8594; stowed by Kiva robots.<br>
          <strong>Demand signal:</strong> Real-time POS + ML forecast (DeepAR / Prophet ensemble).<br>
          <strong>Outbound:</strong> Pick &#8594; Pack &#8594; Ship via AMZL/UPS/USPS. <strong>Prime 2-day</strong> requires &#8805;95% in-stock at nearest regional FC.
        </div>
      </div>
    </div>
    <div class="sc-kpis">
      <div class="sc-kpi"><div class="sc-kpi-val" id="kpiEOQ">&#8212;</div><div class="sc-kpi-label">EOQ</div><div class="sc-kpi-sub">units per PO</div></div>
      <div class="sc-kpi"><div class="sc-kpi-val" id="kpiROP">&#8212;</div><div class="sc-kpi-label">Reorder Point</div><div class="sc-kpi-sub">trigger replenishment</div></div>
      <div class="sc-kpi"><div class="sc-kpi-val" id="kpiSS">&#8212;</div><div class="sc-kpi-label">Safety Stock</div><div class="sc-kpi-sub">Prime SLA buffer</div></div>
      <div class="sc-kpi"><div class="sc-kpi-val" id="kpiTC" style="font-size:1.05rem">&#8212;</div><div class="sc-kpi-label">Annual Cost</div><div class="sc-kpi-sub">order + holding</div></div>
      <div class="sc-kpi"><div class="sc-kpi-val" id="kpiTurns">&#8212;</div><div class="sc-kpi-label">Inv. Turns</div><div class="sc-kpi-sub">D / avg on-hand</div></div>
    </div>
  </div>
</section>
''')
out.close()
print('sc1 done')
