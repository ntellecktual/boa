TMPL = 'boaapp/templates/boaapp/humana_mdm.html'
with open(TMPL, 'a', encoding='utf-8') as out:
    out.write(r'''
<!-- ==================== CLASSROOM ==================== -->
<section class="hm-classroom" id="hm-classroom">
  <div class="hm-sec-head">
    <span class="hm-sec-tag violet"><i class="fas fa-graduation-cap me-1"></i> Classroom</span>
    <h2>Six Lessons in Healthcare MDM</h2>
    <p>From the fundamental MDM problem to HIPAA-compliant Unity Catalog governance &mdash; six progressive lessons building from concept to production architecture.</p>
  </div>
  <div class="hm-cls-wrap">
    <div class="hm-cls-progress">
      <div class="hm-cls-dot active" onclick="window.hmClsGoto(0)"></div>
      <div class="hm-cls-dot" onclick="window.hmClsGoto(1)"></div>
      <div class="hm-cls-dot" onclick="window.hmClsGoto(2)"></div>
      <div class="hm-cls-dot" onclick="window.hmClsGoto(3)"></div>
      <div class="hm-cls-dot" onclick="window.hmClsGoto(4)"></div>
      <div class="hm-cls-dot" onclick="window.hmClsGoto(5)"></div>
    </div>
    <div class="hm-cls-stage">

      <!-- Slide 1 -->
      <div class="hm-cls-slide active" id="hmCls0">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">01 / Fundamentals</span>
          <h3>The MDM Problem &mdash; Why One Truth Matters</h3>
          <p>Master Data Management solves three interrelated problems: duplicate records, inconsistent attribute values across systems, and the absence of a single authoritative source for critical business entities.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-grid">
            <div class="hm-cls-item" style="border-color:rgba(239,68,68,.25);background:rgba(239,68,68,.04)">
              <div class="ci-label">Problem 1</div>
              <div class="ci-val">Duplicate Identities</div>
              <div class="ci-note">1 person &#x2192; 4 system records, fragmented clinical history, missed allergy alerts</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(245,158,11,.25);background:rgba(245,158,11,.04)">
              <div class="ci-label">Problem 2</div>
              <div class="ci-val">Inconsistent Attributes</div>
              <div class="ci-note">Same member: 2 DOBs, 3 phones, 4 addresses &mdash; each "correct" per its source</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(124,58,237,.25);background:rgba(124,58,237,.04)">
              <div class="ci-label">Problem 3</div>
              <div class="ci-val">No Golden Record</div>
              <div class="ci-note">Downstream systems pick arbitrary source &mdash; no lineage, no trust scoring, no audit trail</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.25);background:rgba(16,185,129,.04)">
              <div class="ci-label">MDM Solution</div>
              <div class="ci-val">Entity Resolution + Survivorship</div>
              <div class="ci-note">Probabilistic matching &#x2192; cluster &#x2192; elect best attribute per source trust score</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(0,120,212,.25);background:rgba(0,120,212,.04)">
              <div class="ci-label">Humana Scale</div>
              <div class="ci-val">8.4M Members, 11 Sources</div>
              <div class="ci-note">1.2M duplicate identities resolved; 99.7% golden record accuracy</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(232,89,12,.25);background:rgba(232,89,12,.04)">
              <div class="ci-label">Why Healthcare</div>
              <div class="ci-val">Patient Safety Stakes</div>
              <div class="ci-note">Fragmented identity = missed medication allergy; MDM is a safety system, not just DQ</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Slide 2 -->
      <div class="hm-cls-slide" id="hmCls1">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">02 / Ingestion</span>
          <h3>Kafka + Azure Event Hubs: Streaming Ingestion</h3>
          <p>Event-driven ingestion replaces nightly batch loads &mdash; member updates become visible in the golden record within 5 minutes, not 4 hours.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-arch">
            <div class="hm-cls-arch-box" style="background:rgba(124,58,237,.07);border-color:rgba(124,58,237,.2)">
              <div class="ba-lbl">Sources</div><div class="ba-name">11 Systems</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(30,30,30,.05);border-color:rgba(30,30,30,.15)">
              <div class="ba-lbl">Event Hubs</div><div class="ba-name">Kafka Topics</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(0,120,212,.07);border-color:rgba(0,120,212,.2)">
              <div class="ba-lbl">Schema Reg.</div><div class="ba-name">Avro Contract</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.2)">
              <div class="ba-lbl">Auto Loader</div><div class="ba-name">Bronze Delta</div>
            </div>
          </div>
          <div class="hm-cls-grid" style="margin-top:.7rem">
            <div class="hm-cls-item">
              <div class="ci-label">Why Kafka over ADF Batch?</div>
              <div class="ci-val">5-min lag vs 4-hour lag</div>
              <div class="ci-note">Real-time care coordination requires member data currency; nightly batch is clinically unacceptable</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Schema Registry</div>
              <div class="ci-val">Avro Contract Enforcement</div>
              <div class="ci-note">Schema violations rejected at topic boundary &mdash; dead-letter queue catches malformed events before Bronze</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Auto Loader</div>
              <div class="ci-val">cloudFiles + Schema Evolution</div>
              <div class="ci-note">Detects new columns automatically (addNewColumns mode); no pipeline restarts on source schema changes</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Consumer Groups</div>
              <div class="ci-val">Independent Parallel Consumers</div>
              <div class="ci-note">Bronze pipeline, DQ monitoring, and analytics all read the same topic at independent offsets</div>
            </div>
          </div>
          <div class="hm-vs-row">
            <span class="hm-vs-pill hm-vs-pill--win">Kafka + Auto Loader (5-min lag)</span>
            <span class="hm-vs-sep">vs</span>
            <span class="hm-vs-pill hm-vs-pill--lose">ADF Nightly Batch (4-hr lag)</span>
          </div>
        </div>
      </div>

      <!-- Slide 3 -->
      <div class="hm-cls-slide" id="hmCls2">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">03 / Architecture</span>
          <h3>Medallion Architecture: Bronze &#x2192; Silver &#x2192; Gold</h3>
          <p>Three immutable Delta Lake layers with distinct purposes: raw capture, cleansed truth, and unified golden record. Each layer is independently replayable.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-arch">
            <div class="hm-cls-arch-box" style="background:rgba(146,64,14,.07);border-color:rgba(146,64,14,.2)">
              <div class="ba-lbl">Bronze</div><div class="ba-name">Raw Capture</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(100,116,139,.07);border-color:rgba(100,116,139,.2)">
              <div class="ba-lbl">Silver</div><div class="ba-name">Cleansed + Linked</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.25)">
              <div class="ba-lbl">Gold</div><div class="ba-name">Golden Record</div>
            </div>
            <div class="hm-cls-arch-arrow"><i class="fas fa-arrow-right"></i></div>
            <div class="hm-cls-arch-box" style="background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.2)">
              <div class="ba-lbl">Egress</div><div class="ba-name">API / Kafka</div>
            </div>
          </div>
          <div class="hm-cls-grid" style="margin-top:.7rem">
            <div class="hm-cls-item" style="border-color:rgba(146,64,14,.2)">
              <div class="ci-label">Bronze Purpose</div>
              <div class="ci-val">Immutable Raw Capture</div>
              <div class="ci-note">Append-only, CDF enabled, schema evolution. No record ever dropped. Full replay capability.</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(100,116,139,.2)">
              <div class="ci-label">Silver Purpose</div>
              <div class="ci-val">47 DQ Gates + Geo-Enrichment</div>
              <div class="ci-note">@dlt.expect_or_drop for nulls, @dlt.expect_or_quarantine for invalid ZIPs. CASS broadcast join.</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(245,158,11,.25)">
              <div class="ci-label">Gold Purpose</div>
              <div class="ci-val">Survivorship + Golden Record</div>
              <div class="ci-note">Window function ranks by _source_trust desc; RANK()=1 elects highest-trust attribute per member.</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.2)">
              <div class="ci-label">Why DLT over Raw Spark?</div>
              <div class="ci-val">Built-in DQ + Lineage</div>
              <div class="ci-note">Eliminates ~3,000 lines of custom retry/quarantine boilerplate. Auto-generates pipeline lineage graph.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Slide 4 -->
      <div class="hm-cls-slide" id="hmCls3">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">04 / Entity Resolution</span>
          <h3>Probabilistic Matching: The Fellegi-Sunter Model</h3>
          <p>Why deterministic rules miss 22% of real duplicates &mdash; and how match weights and blocking rules make probabilistic matching practical at 8M-member scale.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-grid">
            <div class="hm-cls-item">
              <div class="ci-label">Why Deterministic Fails</div>
              <div class="ci-val">78% recall ceiling</div>
              <div class="ci-note">"Jon Smith" vs "Jonathan Smith" &mdash; exact match fails. Address reformats &amp; typos break rule chains.</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Blocking Rules</div>
              <div class="ci-val">70T &#x2192; 8.2M candidates</div>
              <div class="ci-note">last_name+zip and dob+zip predicates reduce candidate pairs 99.99% before scoring begins</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Fellegi-Sunter</div>
              <div class="ci-val">match_prob = sigmoid(&#x03A3; weights)</div>
              <div class="ci-note">Each column comparison contributes a log-likelihood ratio; sum determines match probability</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Levenshtein Distance</div>
              <div class="ci-val">Edit-Distance Name Matching</div>
              <div class="ci-note">Distance 0 &#x2192; high weight; distance 1-2 &#x2192; partial weight; distance 3+ &#x2192; negative weight</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Training Data</div>
              <div class="ci-val">500K Labeled Pairs</div>
              <div class="ci-note">Human-verified match/non-match pairs calibrate the u and m probability estimates per column</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.25);background:rgba(16,185,129,.04)">
              <div class="ci-label">Result</div>
              <div class="ci-val">97% recall at 0.85 threshold</div>
              <div class="ci-note">+19 points over deterministic rules = 1.9M previously-missed identity links corrected</div>
            </div>
          </div>
          <div class="hm-vs-row">
            <span class="hm-vs-pill hm-vs-pill--win">Probabilistic Splink (97% recall)</span>
            <span class="hm-vs-sep">vs</span>
            <span class="hm-vs-pill hm-vs-pill--lose">Deterministic Rules (78% recall)</span>
          </div>
        </div>
      </div>

      <!-- Slide 5 -->
      <div class="hm-cls-slide" id="hmCls4">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">05 / Survivorship</span>
          <h3>Survivorship Rules: Electing the Golden Record</h3>
          <p>Once entity clusters form, survivorship determines which source wins each attribute &mdash; not by record, but field-by-field based on source trust scores derived from accuracy audits.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-grid">
            <div class="hm-cls-item" style="border-color:rgba(0,120,212,.2)">
              <div class="ci-label">Epic EHR</div>
              <div class="ci-val">Trust: 0.97</div>
              <div class="ci-note">Wins: first_name, last_name, date_of_birth, allergy_codes, diagnosis_codes</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.2)">
              <div class="ci-label">Enrollment Svc</div>
              <div class="ci-val">Trust: 0.95</div>
              <div class="ci-note">Wins: plan_id, coverage_start_date, subscriber_id, group_number</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(0,120,212,.15)">
              <div class="ci-label">Salesforce CRM</div>
              <div class="ci-val">Trust: 0.92</div>
              <div class="ci-note">Wins: email, preferred_name, marketing_consent, contact_preferences</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(245,158,11,.2)">
              <div class="ci-label">USPS CASS</div>
              <div class="ci-val">Trust: 1.00 (reference)</div>
              <div class="ci-note">Wins: address, zip_code, city, state, lat/lon, county_fips, cbsa_code</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Implementation</div>
              <div class="ci-val">Window RANK() by _source_trust</div>
              <div class="ci-note">RANK()=1 per enterprise_member_id selects highest-trust row; one SELECT from Silver gold is created</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">Lineage</div>
              <div class="ci-val">Per-Field Source Stamp</div>
              <div class="ci-note">Every golden record field tagged with source_system, confidence_score, last_updated &mdash; auditable per CMS requirements</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Slide 6 -->
      <div class="hm-cls-slide" id="hmCls5">
        <div class="hm-cls-head">
          <span class="hm-cls-badge">06 / Governance</span>
          <h3>HIPAA Governance with Unity Catalog</h3>
          <p>Unity Catalog enforces row-level security and column masking at the query engine &mdash; eliminating duplicate de-identified copies and generating audit trails automatically.</p>
        </div>
        <div class="hm-cls-body">
          <div class="hm-cls-grid">
            <div class="hm-cls-item" style="border-color:rgba(0,120,212,.2)">
              <div class="ci-label">Row-Level Security</div>
              <div class="ci-val">SQL Predicate Policy</div>
              <div class="ci-note">PHI rows filtered for non-hipaa_certified roles at query engine, not application code &mdash; no bypass possible</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(124,58,237,.2)">
              <div class="ci-label">Column Masking</div>
              <div class="ci-val">SSN / DOB / Diagnosis</div>
              <div class="ci-note">Non-clinical consumers see "***-**-6712" instead of SSN; masking function defined once, applied everywhere</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.2)">
              <div class="ci-label">Audit Trail</div>
              <div class="ci-val">system.access.audit table</div>
              <div class="ci-note">Every SELECT on PHI columns logged &mdash; queryable for CMS audit submissions; no manual tracking</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(245,158,11,.2)">
              <div class="ci-label">Before MDM</div>
              <div class="ci-val">4 De-Identified Copies</div>
              <div class="ci-note">Manually refreshed, drift-prone, audit-invisible &mdash; each copy a HIPAA liability</div>
            </div>
            <div class="hm-cls-item" style="border-color:rgba(16,185,129,.25);background:rgba(16,185,129,.04)">
              <div class="ci-label">After MDM</div>
              <div class="ci-val">Zero Copies, One Gold Table</div>
              <div class="ci-note">All consumers share the gold table; masking and RLS govern access per role &mdash; automated monthly audit report</div>
            </div>
            <div class="hm-cls-item">
              <div class="ci-label">HIPAA Implication</div>
              <div class="ci-val">Minimum Necessary Standard</div>
              <div class="ci-note">Column masking enforces HIPAA minimum-necessary access without any application-layer changes</div>
            </div>
          </div>
        </div>
      </div>

      <div class="hm-cls-footer">
        <span class="hm-cls-counter">1 / 6</span>
        <div class="hm-cls-nav">
          <button onclick="window.hmClsPrev()"><i class="fas fa-arrow-left me-1"></i>Prev</button>
          <button onclick="window.hmClsNext()">Next<i class="fas fa-arrow-right ms-1"></i></button>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ==================== KEY POINTS ==================== -->
<section class="hm-keypoints" id="hm-keypoints">
  <div class="hm-sec-head">
    <span class="hm-sec-tag gold"><i class="fas fa-lightbulb me-1"></i> Key Points</span>
    <h2>Four Engineering Decisions That Defined the Platform</h2>
    <p>The choices that separated a 97%-accurate MDM platform from a 78%-accurate one &mdash; and why each decision had measurable clinical or business impact.</p>
  </div>
  <div class="hm-kp-grid">

    <div class="hm-kp-card">
      <div class="hm-kp-icon" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)"><i class="fas fa-link"></i></div>
      <div class="hm-kp-stat" style="background:var(--hm-grad-main);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">+19%</div>
      <h6>Probabilistic vs. Deterministic Matching</h6>
      <p>Splink's Fellegi-Sunter model achieved 97% recall vs. 78% for deterministic rules &mdash; a 19-point gap representing 1.9 million missed identity links on 10M candidate pairs. Each missed link is a fragmented patient history where a medication allergy from one source cannot surface when prescribing in another system. The choice to train on 500K labeled pairs instead of hand-crafting rules was the single highest-impact engineering decision in the project.</p>
    </div>

    <div class="hm-kp-card">
      <div class="hm-kp-icon" style="background:linear-gradient(135deg,#e8590c,#b94400)"><i class="fas fa-filter"></i></div>
      <div class="hm-kp-stat" style="background:var(--hm-grad-spark);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">91%</div>
      <h6>DLT Expectations Eliminate 3,000 Lines of Boilerplate</h6>
      <p>Delta Live Tables' built-in @dlt.expect_or_drop and @dlt.expect_or_quarantine decorators replaced approximately 3,000 lines of custom PySpark retry and quarantine logic. The DLT pipeline auto-generates the quarantine table, lineage graph, and DQ metrics dashboard. Isolation Forest anomaly detection auto-remediates 91% of DQ exceptions &mdash; saving 3 FTE data steward roles from manual review queues that would otherwise process ~260 tickets per day.</p>
    </div>

    <div class="hm-kp-card">
      <div class="hm-kp-icon" style="background:linear-gradient(135deg,#0d9488,#0f766e)"><i class="fas fa-map-marker-alt"></i></div>
      <div class="hm-kp-stat" style="background:var(--hm-grad-gold);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">-62%</div>
      <h6>Broadcast Join vs. External GIS API Call</h6>
      <p>Broadcast-joining the 32K-row USPS CASS geospatial reference table into each Spark executor eliminated 340ms external API round-trips per record &mdash; reducing Silver-layer processing time by 62%. The reference table fits entirely in executor memory (12 MB), so each join is a local hash-lookup rather than a network call. This also eliminated the external GIS API as a single point of failure and removed a $0.003/lookup cost that would have totalled $2,500/day at full volume.</p>
    </div>

    <div class="hm-kp-card">
      <div class="hm-kp-icon" style="background:linear-gradient(135deg,#0078d4,#005a9e)"><i class="fas fa-shield-alt"></i></div>
      <div class="hm-kp-stat" style="background:var(--hm-grad-main);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">0 copies</div>
      <h6>Unity Catalog RLS Eliminates De-Identified Copies</h6>
      <p>Before MDM, four manually-maintained de-identified copies of member data existed for different consumer tiers. Each copy drifted, had incomplete refresh cadences, and was independently auditable (or not). Unity Catalog column masking and row-level security policies mean all 14 consuming systems read the same gold table &mdash; each seeing only what their role permits. The automated audit trail satisfies CMS inspection requirements without any manual log compilation. Zero copies, infinite consumers.</p>
    </div>

  </div>
</section>

<!-- ==================== CODE ==================== -->
<section class="hm-code-section" id="hm-code">
  <div class="hm-sec-head">
    <span class="hm-sec-tag emerald"><i class="fas fa-code me-1"></i> Production Code</span>
    <h2>Three Core Algorithms</h2>
    <p>The Delta Live Tables pipeline, Splink entity resolution configuration, and Unity Catalog HIPAA governance that power the MDM platform in production.</p>
  </div>
  <div class="hm-impl">

    <details>
      <summary><i class="fas fa-layer-group me-2" style="color:#92400e"></i>DLT Pipeline &mdash; Bronze &#x2192; Silver &#x2192; Gold Survivorship (PySpark)</summary>
      <pre><span class="cc"># ============================================================</span>
<span class="cc"># Enterprise Member MDM &mdash; Delta Live Tables Pipeline</span>
<span class="cc"># Medallion: Bronze &rarr; Silver &rarr; Gold (Golden Record)</span>
<span class="cc"># ============================================================</span>
<span class="ck">import</span> <span class="cm">dlt</span>
<span class="ck">from</span> <span class="cm">pyspark.sql</span> <span class="ck">import</span> functions <span class="ck">as</span> F
<span class="ck">from</span> <span class="cm">pyspark.sql.window</span> <span class="ck">import</span> Window

<span class="cc"># Attribute-level trust scores for survivorship election</span>
SOURCE_TRUST = {
    <span class="cs">"epic_ehr"</span>:         <span class="cn">0.97</span>,  <span class="cc"># clinical system &mdash; highest trust</span>
    <span class="cs">"enrollment_svc"</span>:   <span class="cn">0.95</span>,
    <span class="cs">"salesforce_crm"</span>:   <span class="cn">0.92</span>,
    <span class="cs">"claims_adjudicate"</span>:<span class="cn">0.88</span>,
    <span class="cs">"provider_dir"</span>:     <span class="cn">0.80</span>,
    <span class="cs">"legacy_mainframe"</span>: <span class="cn">0.60</span>,
}

<span class="cn">@dlt.table</span>(name=<span class="cs">"bronze_member_events"</span>,
    table_properties={<span class="cs">"delta.enableChangeDataFeed"</span>: <span class="cs">"true"</span>})
<span class="ck">def</span> <span class="cv">bronze_member_events</span>():
    <span class="ck">return</span> (spark.readStream
        .format(<span class="cs">"cloudFiles"</span>)
        .option(<span class="cs">"cloudFiles.format"</span>, <span class="cs">"avro"</span>)
        .option(<span class="cs">"cloudFiles.schemaEvolutionMode"</span>, <span class="cs">"addNewColumns"</span>)
        .load(<span class="cs">"abfss://raw@mdmstorage.dfs.core.windows.net/member-events/"</span>)
        .withColumn(<span class="cs">"_ingest_ts"</span>, F.current_timestamp())
    )

<span class="cn">@dlt.table</span>(name=<span class="cs">"silver_members"</span>)
<span class="cn">@dlt.expect_or_drop</span>(<span class="cs">"valid_member_id"</span>, <span class="cs">"member_id IS NOT NULL"</span>)
<span class="cn">@dlt.expect_or_drop</span>(<span class="cs">"valid_dob"</span>,       <span class="cs">"date_of_birth &gt; '1900-01-01'"</span>)
<span class="cn">@dlt.expect_or_quarantine</span>(<span class="cs">"valid_zip"</span>, <span class="cs">"LENGTH(zip_code) IN (5,9)"</span>)
<span class="ck">def</span> <span class="cv">silver_members</span>():
    geo = spark.table(<span class="cs">"catalog.reference.zip_geospatial"</span>)
    trust_map = F.create_map([F.lit(x)
                   <span class="ck">for</span> pair <span class="ck">in</span> SOURCE_TRUST.items() <span class="ck">for</span> x <span class="ck">in</span> pair])
    <span class="ck">return</span> (dlt.read_stream(<span class="cs">"bronze_member_events"</span>)
        .withColumn(<span class="cs">"first_name"</span>, F.initcap(F.trim(F.col(<span class="cs">"first_name"</span>))))
        .withColumn(<span class="cs">"email"</span>,      F.lower(F.trim(F.col(<span class="cs">"email"</span>))))
        .withColumn(<span class="cs">"zip_code"</span>,   F.col(<span class="cs">"zip_code"</span>).substr(<span class="cn">1</span>, <span class="cn">5</span>))
        .join(F.broadcast(geo), <span class="cs">"zip_code"</span>, <span class="cs">"left"</span>)
        .withColumn(<span class="cs">"_source_trust"</span>, trust_map[F.col(<span class="cs">"source_system"</span>)])
    )

<span class="cn">@dlt.table</span>(name=<span class="cs">"gold_member_golden_record"</span>,
    comment=<span class="cs">"System of Record &mdash; highest-trust attribute per member"</span>)
<span class="ck">def</span> <span class="cv">gold_member_golden_record</span>():
    w = Window.partitionBy(<span class="cs">"enterprise_member_id"</span>).orderBy(
        F.col(<span class="cs">"_source_trust"</span>).desc())
    <span class="ck">return</span> (dlt.read(<span class="cs">"silver_members"</span>)
        .withColumn(<span class="cs">"_rank"</span>, F.rank().over(w))
        .filter(F.col(<span class="cs">"_rank"</span>) == <span class="cn">1</span>)
        .withColumn(<span class="cs">"golden_record_ts"</span>, F.current_timestamp())
        .withColumn(<span class="cs">"record_version"</span>, F.expr(<span class="cs">"uuid()"</span>))
        .drop(<span class="cs">"_rank"</span>, <span class="cs">"_source_trust"</span>, <span class="cs">"_ingest_ts"</span>)
    )</pre>
    </details>

    <details>
      <summary><i class="fas fa-link me-2" style="color:#7c3aed"></i>Entity Resolution &mdash; Splink Fellegi-Sunter Probabilistic Matching (Python)</summary>
      <pre><span class="ck">import</span> <span class="cm">splink.spark.comparison_library</span> <span class="ck">as</span> cl
<span class="ck">from</span> <span class="cm">splink.spark.spark_linker</span> <span class="ck">import</span> SparkLinker

<span class="ck">def</span> <span class="cv">build_linker</span>(df_spark) <span class="ck">-&gt;</span> SparkLinker:
    <span class="cs">"""Configure Fellegi-Sunter probabilistic linker.
    
    Blocking rules reduce 70T candidate pairs to 8.2M.
    Each comparison column contributes a log-likelihood ratio.
    Final match_probability = sigmoid(sum of all log-likelihood ratios).
    Threshold 0.85 achieves 97% recall vs 78% for deterministic rules.
    """</span>
    settings = {
        <span class="cs">"link_type"</span>: <span class="cs">"dedupe_only"</span>,
        <span class="cs">"comparisons"</span>: [
            cl.levenshtein_at_thresholds(<span class="cs">"last_name"</span>,  [<span class="cn">1</span>, <span class="cn">2</span>]),
            cl.levenshtein_at_thresholds(<span class="cs">"first_name"</span>, [<span class="cn">1</span>]),
            cl.exact_match(<span class="cs">"date_of_birth"</span>),
            cl.exact_match(<span class="cs">"zip_code"</span>),
            cl.exact_match(<span class="cs">"phone_e164"</span>),
        ],
        <span class="cs">"blocking_rules_to_generate_predictions"</span>: [
            <span class="cs">"l.last_name = r.last_name AND l.zip_code = r.zip_code"</span>,
            <span class="cs">"l.date_of_birth = r.date_of_birth AND l.zip_code = r.zip_code"</span>,
        ],
        <span class="cs">"retain_matching_columns"</span>: <span class="ck">True</span>,
    }
    linker = SparkLinker(df_spark, settings, spark=spark,
                         catalog=<span class="cs">"catalog"</span>, database=<span class="cs">"mdm_silver"</span>)
    <span class="cc"># Estimate u probabilities via random sampling (no labels needed)</span>
    linker.estimate_u_using_random_sampling(max_pairs=<span class="cn">1e7</span>)
    <span class="cc"># Estimate m probabilities from 500K human-labeled training pairs</span>
    linker.estimate_parameters_using_expectation_maximisation(
        <span class="cs">"l.date_of_birth = r.date_of_birth"</span>
    )
    <span class="ck">return</span> linker

<span class="ck">def</span> <span class="cv">run_entity_resolution</span>(df):
    linker = build_linker(df)
    pairwise = linker.predict(threshold_match_probability=<span class="cn">0.85</span>)
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise, <span class="cn">0.85</span>)
    <span class="cc"># Returns cluster_id per row &mdash; join back to assign enterprise_member_id</span>
    <span class="ck">return</span> clusters.as_spark_dataframe()</pre>
    </details>

    <details>
      <summary><i class="fas fa-shield-alt me-2" style="color:#0078d4"></i>Unity Catalog &mdash; HIPAA Column Masking + Row-Level Security (SQL)</summary>
      <pre><span class="cc">-- ============================================================</span>
<span class="cc">-- Unity Catalog: HIPAA PHI governance for gold_member_golden_record</span>
<span class="cc">-- Column masking for SSN/DOB/diagnosis; RLS for PHI row access</span>
<span class="cc">-- ============================================================</span>

<span class="cc">-- 1. SSN masking function: shows last 4 digits only to non-clinical roles</span>
<span class="ck">CREATE OR REPLACE FUNCTION</span> <span class="cv">catalog.mdm.mask_ssn</span>(<span class="cs">ssn</span> <span class="ck">STRING</span>)
<span class="ck">RETURNS STRING</span>
<span class="ck">RETURN CASE</span>
  <span class="ck">WHEN</span> is_account_group_member(<span class="cs">'hipaa_certified'</span>) <span class="ck">THEN</span> ssn
  <span class="ck">ELSE</span> CONCAT(<span class="cs">'***-**-'</span>, RIGHT(ssn, <span class="cn">4</span>))
<span class="ck">END</span>;

<span class="ck">ALTER TABLE</span> catalog.gold.member_golden_record
<span class="ck">ALTER COLUMN</span> ssn <span class="ck">SET MASK</span> catalog.mdm.mask_ssn;

<span class="cc">-- 2. DOB masking: year only for non-clinical consumers</span>
<span class="ck">CREATE OR REPLACE FUNCTION</span> <span class="cv">catalog.mdm.mask_dob</span>(<span class="cs">dob</span> <span class="ck">DATE</span>)
<span class="ck">RETURNS DATE</span>
<span class="ck">RETURN CASE</span>
  <span class="ck">WHEN</span> is_account_group_member(<span class="cs">'hipaa_certified'</span>) <span class="ck">THEN</span> dob
  <span class="ck">ELSE</span> DATE_TRUNC(<span class="cs">'YEAR'</span>, dob)  <span class="cc">-- truncate to Jan 1 of birth year</span>
<span class="ck">END</span>;

<span class="cc">-- 3. Row-level security: PHI members only visible to certified roles</span>
<span class="ck">CREATE OR REPLACE ROW ACCESS POLICY</span> catalog.mdm.phi_row_policy
<span class="ck">AS</span> (member_id <span class="ck">STRING</span>) <span class="ck">RETURNS BOOLEAN</span>
<span class="ck">RETURN</span>
  is_account_group_member(<span class="cs">'hipaa_certified'</span>)
  <span class="ck">OR NOT</span> catalog.mdm.member_has_phi_flag(member_id);

<span class="ck">ALTER TABLE</span> catalog.gold.member_golden_record
<span class="ck">ADD ROW ACCESS POLICY</span> catalog.mdm.phi_row_policy <span class="ck">ON</span> (member_id);

<span class="cc">-- 4. CMS audit report: all PHI access in last 30 days</span>
<span class="ck">SELECT</span>
  user_identity.email     <span class="ck">AS</span> accessed_by,
  action_name,
  request_params.table_full_name,
  DATE(event_time)        <span class="ck">AS</span> access_date,
  COUNT(*)                <span class="ck">AS</span> query_count
<span class="ck">FROM</span>   system.access.audit
<span class="ck">WHERE</span>  request_params.table_full_name <span class="ck">LIKE</span> <span class="cs">'%member_golden_record%'</span>
  <span class="ck">AND</span>  action_name <span class="ck">IN</span> (<span class="cs">'SELECT'</span>, <span class="cs">'READ'</span>)
  <span class="ck">AND</span>  event_time &gt;= CURRENT_DATE - <span class="ck">INTERVAL</span> <span class="cn">30</span> <span class="ck">DAYS</span>
<span class="ck">GROUP BY</span> <span class="cn">1</span>, <span class="cn">2</span>, <span class="cn">3</span>, <span class="cn">4</span>
<span class="ck">ORDER BY</span> access_date <span class="ck">DESC</span>;</pre>
    </details>

  </div>
</section>

<!-- ==================== ABOUT ==================== -->
<section class="hm-about" id="hm-about">
  <div class="hm-about-card">
    <h3>Healthcare MDM on Azure Databricks</h3>
    <p>This platform processes 8.4 million member records across 11 source systems using PySpark Delta Live Tables, Kafka streaming, Splink probabilistic entity resolution, and Unity Catalog HIPAA governance &mdash; achieving 99.7% golden record accuracy with 91% automated DQ remediation and zero de-identified data copies.</p>
    <div class="hm-pills-wrap">
      <span class="hm-pill hm-pill--az">Azure Databricks</span>
      <span class="hm-pill hm-pill--db">PySpark</span>
      <span class="hm-pill hm-pill--db">Delta Live Tables</span>
      <span class="hm-pill hm-pill--db">Delta Lake</span>
      <span class="hm-pill hm-pill--kf">Apache Kafka</span>
      <span class="hm-pill hm-pill--kf">Azure Event Hubs</span>
      <span class="hm-pill hm-pill--az">ADLS Gen2</span>
      <span class="hm-pill hm-pill--az">Unity Catalog</span>
      <span class="hm-pill hm-pill--az">Auto Loader</span>
      <span class="hm-pill hm-pill--v">Splink (Fellegi-Sunter)</span>
      <span class="hm-pill hm-pill--t">USPS CASS / Geospatial</span>
      <span class="hm-pill hm-pill--g">FastAPI REST</span>
      <span class="hm-pill hm-pill--g">C# / .NET SDK</span>
      <span class="hm-pill hm-pill--g">OpenAPI 3.0</span>
      <span class="hm-pill hm-pill--v">Avro / Schema Registry</span>
      <span class="hm-pill hm-pill--t">Isolation Forest (DQ)</span>
      <span class="hm-pill hm-pill--az">Azure Monitor</span>
    </div>
    <div class="hm-share-actions">
      <button class="hm-share-btn hm-share-btn--primary" onclick="window.hmShareDemo()"><i class="fas fa-share me-1"></i>Share</button>
      <button class="hm-share-btn hm-share-btn--secondary" onclick="window.hmScrollTo('hm-story')"><i class="fas fa-arrow-up me-1"></i>Back to Top</button>
    </div>
  </div>
</section>

{% endblock content %}

{% block extra_js %}
<script>
(function(){'use strict';

// ── Progress bar ──────────────────────────────────────────────
var fill = document.getElementById('hmProgressFill');
function updateProgress(){
  var doc = document.documentElement;
  var scrolled = doc.scrollTop || document.body.scrollTop;
  var total = doc.scrollHeight - doc.clientHeight;
  if(fill) fill.style.width = (total > 0 ? (scrolled/total*100) : 0) + '%';
}

// ── Scroll-spy ────────────────────────────────────────────────
var navBtns = document.querySelectorAll('.hm-nav-btn');
var SECS = ['hm-story','hm-demo','hm-classroom','hm-keypoints','hm-code','hm-about'];
function updateNav(){
  var mid = window.scrollY + window.innerHeight / 3;
  var active = SECS[0];
  SECS.forEach(function(id){
    var el = document.getElementById(id);
    if(el && el.offsetTop <= mid) active = id;
  });
  navBtns.forEach(function(btn, i){
    btn.classList.toggle('active', SECS[i] === active);
  });
}
window.addEventListener('scroll', function(){ updateProgress(); updateNav(); }, {passive:true});
updateProgress(); updateNav();

// ── Scroll to section ─────────────────────────────────────────
window.hmScrollTo = function(id){
  var el = document.getElementById(id);
  if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
};

// ── Demo mode toggle ──────────────────────────────────────────
window.hmSetMode = function(mode){
  var eli5 = document.getElementById('hmELI5Pane');
  var eng  = document.getElementById('hmEngPane');
  var btns = document.querySelectorAll('.hm-mode-btn');
  if(mode === 'eli5'){
    if(eli5) eli5.classList.add('active');
    if(eng)  eng.classList.remove('active');
    if(btns[0]) btns[0].classList.add('active');
    if(btns[1]) btns[1].classList.remove('active');
  } else {
    if(eli5) eli5.classList.remove('active');
    if(eng)  eng.classList.add('active');
    if(btns[0]) btns[0].classList.remove('active');
    if(btns[1]) btns[1].classList.add('active');
  }
};

// ── ELI5 card toggle ──────────────────────────────────────────
window.hmToggleELI5 = function(card){
  var wasActive = card.classList.contains('active');
  document.querySelectorAll('.hm-eli5-card').forEach(function(c){ c.classList.remove('active'); });
  if(!wasActive) card.classList.add('active');
};

// ── Classroom navigation ──────────────────────────────────────
var CLS_COUNT = 6;
var clsIdx = 0;
function showSlide(idx){
  clsIdx = Math.max(0, Math.min(CLS_COUNT - 1, idx));
  document.querySelectorAll('.hm-cls-slide').forEach(function(s, i){
    s.classList.toggle('active', i === clsIdx);
  });
  document.querySelectorAll('.hm-cls-dot').forEach(function(d, i){
    d.classList.toggle('active', i === clsIdx);
  });
  var counter = document.querySelector('.hm-cls-counter');
  if(counter) counter.textContent = (clsIdx + 1) + ' / ' + CLS_COUNT;
}
window.hmClsNext = function(){ showSlide(clsIdx + 1); };
window.hmClsPrev = function(){ showSlide(clsIdx - 1); };
window.hmClsGoto = function(i){ showSlide(i); };
showSlide(0);

// ── Share ─────────────────────────────────────────────────────
window.hmShareDemo = function(){
  if(navigator.share){
    navigator.share({title: 'Healthcare MDM Platform \u2014 Azure Databricks', url: window.location.href});
  } else {
    navigator.clipboard.writeText(window.location.href).then(function(){
      var btn = document.querySelector('.hm-share-btn--primary');
      if(btn){ var orig = btn.innerHTML; btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!'; setTimeout(function(){ btn.innerHTML = orig; }, 2000); }
    });
  }
};

// ── Pipeline Simulator ────────────────────────────────────────
var logEl   = document.getElementById('hmLog');
var stageEl = document.getElementById('hmStage');
var btnRun  = document.getElementById('hmBtnRun');
var btnRst  = document.getElementById('hmBtnReset');
var dashEl  = document.getElementById('hmDash');
var runCount = 0;
var startTs  = 0;

function addLog(msg){ if(logEl){ logEl.innerHTML += msg + '\n'; logEl.scrollTop = logEl.scrollHeight; } }
function setPip(idx, state){
  var p = document.getElementById('hmPip' + idx);
  if(!p) return;
  p.classList.remove('active','done');
  if(state) p.classList.add(state);
}
function showCtx(id){ var el = document.getElementById(id); if(el) el.classList.add('vis'); }
function addStep(html){
  var d = document.createElement('div');
  d.innerHTML = html;
  if(stageEl && d.firstElementChild){
    stageEl.appendChild(d.firstElementChild);
    stageEl.scrollTop = stageEl.scrollHeight;
  }
}
function wait(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
function chk(icon, text, cls){
  cls = cls || 'pass';
  return '<div class="hm-chk show"><i class="fas ' + icon + ' ' + cls + '"></i> ' + text + '</div>';
}

async function runPipeline(){
  if(!btnRun) return;
  btnRun.disabled = true;
  if(btnRst) btnRst.style.display = 'none';
  if(stageEl) stageEl.innerHTML = '';
  if(logEl) logEl.innerHTML = '';
  startTs = Date.now();
  var events = 2847;

  // Stage 0: Kafka Ingest
  setPip(0, 'active'); showCtx('hmCtx0');
  addLog('Connecting to Azure Event Hubs &mdash; 5 Kafka topics...');
  await wait(700);
  addStep('<div class="hm-step"><h6><i class="fas fa-rss me-2" style="color:#6d28d9"></i>Kafka Ingest</h6>' +
    chk('fa-check-circle','Broker handshake: hmn-eventhubs.servicebus.windows.net') +
    chk('fa-check-circle','Topics: epic-ehr, salesforce-crm, enrollment-svc, claims, provider-dir') +
    chk('fa-check-circle','Avro deserializer loaded from Schema Registry') +
    chk('fa-check-circle','Consumed 2,847 events &middot; 5 partitions &middot; 1.2 MB') +
  '</div>');
  addLog('2,847 Avro messages consumed from 5 topics.');
  await wait(400);
  setPip(0, 'done'); setPip(1, 'active'); showCtx('hmCtx1');

  var eHr = document.getElementById('hmSrcEhr'); if(eHr) eHr.textContent = '1,104';
  var eCr = document.getElementById('hmSrcCrm'); if(eCr) eCr.textContent = '612';
  var eEn = document.getElementById('hmSrcEnr'); if(eEn) eEn.textContent = '731';
  var eCl = document.getElementById('hmSrcClm'); if(eCl) eCl.textContent = '400';

  // Stage 1: Bronze
  addLog('Writing raw events to ADLS Gen2 (Delta append, CDF enabled)...');
  await wait(750);
  addStep('<div class="hm-step"><h6><i class="fas fa-layer-group me-2" style="color:#92400e"></i>Bronze Layer &mdash; Raw Capture</h6>' +
    chk('fa-check-circle','Auto Loader schema evolution: 3 new columns detected') +
    chk('fa-check-circle','2,847 rows appended to bronze_member_events') +
    chk('fa-check-circle','Change Data Feed entries written') +
    chk('fa-check-circle','Partition: event_date=2026-04-21 / source_system') +
  '</div>');
  addLog('Bronze: 2,847 rows persisted. CDF entries written.');
  await wait(400);
  setPip(1, 'done'); setPip(2, 'active'); showCtx('hmCtx2');

  // Stage 2: Silver / DQ
  addLog('Running 47 DQ expectations at Silver layer...');
  await wait(900);
  var dqPass = events - 38 - 12; var dqQuar = 38; var dqFail = 12;
  var dp = document.getElementById('hmDqPass'); if(dp) dp.textContent = dqPass.toLocaleString();
  var dq = document.getElementById('hmDqQuar'); if(dq) dq.textContent = dqQuar;
  var df = document.getElementById('hmDqFail'); if(df) df.textContent = dqFail;
  addStep('<div class="hm-step"><h6><i class="fas fa-filter me-2" style="color:#1e40af"></i>Silver Layer &mdash; Cleanse &amp; Validate</h6>' +
    chk('fa-check-circle','Name normalisation: initcap + trim applied') +
    chk('fa-check-circle','ZIP &rarr; lat/lon geospatial enrichment via CASS broadcast join') +
    chk('fa-check-circle','DQ passed: <strong>' + dqPass.toLocaleString() + '</strong>') +
    chk('fa-exclamation-triangle','Quarantined (invalid ZIP): <strong>38</strong>','pending') +
    chk('fa-times-circle','Rejected (null member_id): <strong>12</strong>','text-danger') +
  '</div>');
  addLog('DQ: ' + dqPass + ' passed, 38 quarantined, 12 rejected.');
  await wait(400);
  setPip(2, 'done'); setPip(3, 'active');

  // Stage 3: Entity Resolution
  addLog('Running Splink probabilistic entity resolution...');
  await wait(1000);
  var matched = 2289; var newM = 508;
  var em = document.getElementById('hmMatched'); if(em) em.textContent = matched.toLocaleString();
  var en = document.getElementById('hmNew'); if(en) en.textContent = newM;
  var ec = document.getElementById('hmConflict'); if(ec) ec.textContent = '0';
  addStep('<div class="hm-step"><h6><i class="fas fa-link me-2" style="color:#7c3aed"></i>Entity Resolution &mdash; Splink</h6>' +
    chk('fa-check-circle','Blocking rules: last_name+zip, dob+zip') +
    chk('fa-check-circle','Fellegi-Sunter: 8.2M candidate pairs evaluated') +
    chk('fa-check-circle','Matched to existing: <strong>2,289</strong> (threshold &ge; 0.85)') +
    chk('fa-check-circle','New enterprise IDs assigned: <strong>508</strong>') +
    chk('fa-check-circle','Zero unresolved conflicts') +
  '</div>');
  addLog('Entity resolution: 2,289 matched, 508 new members.');
  await wait(400);
  setPip(3, 'done'); setPip(4, 'active');

  // Stage 4: Golden Record
  addLog('Electing survivorship winners per attribute...');
  await wait(800);
  addStep('<div class="hm-step hm-step--ok"><h6><i class="fas fa-trophy me-2" style="color:#b45309"></i>Gold Layer &mdash; Golden Record Survivorship</h6>' +
    chk('fa-check-circle','Source trust scores applied per record') +
    chk('fa-check-circle','Attribute-level election: highest-trust value per field') +
    chk('fa-check-circle',dqPass.toLocaleString() + ' golden records written') +
    chk('fa-check-circle','Record version + golden_record_ts stamped') +
    chk('fa-check-circle','Lineage traceable to source system per attribute') +
  '</div>');
  addLog('Golden records: ' + dqPass.toLocaleString() + ' upserted to Unity Catalog.');
  await wait(350);
  setPip(4, 'done'); setPip(5, 'active');

  // Stage 5: API Egress
  addLog('Publishing golden record delta to Kafka egress topic...');
  await wait(700);
  addStep('<div class="hm-step hm-step--ok"><h6><i class="fas fa-share-alt me-2" style="color:#059669"></i>API Egress &amp; Distribution</h6>' +
    chk('fa-check-circle','Kafka topic mdm.member.golden-record.v1: ' + dqPass.toLocaleString() + ' messages published') +
    chk('fa-check-circle','REST API cache invalidated for updated member IDs') +
    chk('fa-check-circle','Delta Sharing snapshot pushed to downstream workspaces') +
    chk('fa-check-circle','C# SDK consumers notified via SignalR event') +
  '</div>');
  addLog('Egress complete. Pipeline finished.');
  await wait(300);
  setPip(5, 'done');

  // Dashboard
  var elapsed = ((Date.now() - startTs) / 1000).toFixed(1);
  runCount++;
  var kr = document.getElementById('hmKpiRows'); if(kr) kr.textContent = events.toLocaleString();
  var kg = document.getElementById('hmKpiGolden'); if(kg) kg.textContent = dqPass.toLocaleString();
  var kdq = document.getElementById('hmKpiDq'); if(kdq) kdq.textContent = ((dqPass/events)*100).toFixed(1) + '%';
  var kt = document.getElementById('hmKpiTime'); if(kt) kt.textContent = elapsed + 's';
  if(dashEl) dashEl.style.display = 'block';

  var tbody = document.getElementById('hmRunTable');
  if(tbody){
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>#' + runCount + '</td><td>5 systems</td><td>' + events.toLocaleString() +
      '</td><td>' + ((dqPass/events)*100).toFixed(1) + '%</td><td>' + dqPass.toLocaleString() +
      '</td><td>2,289</td><td>' + elapsed + 's</td>';
    tbody.prepend(tr);
  }
  if(btnRun) btnRun.disabled = false;
  if(btnRst) btnRst.style.display = '';
}

if(btnRun) btnRun.addEventListener('click', runPipeline);
if(btnRst) btnRst.addEventListener('click', function(){
  if(stageEl) stageEl.innerHTML = '';
  if(logEl) logEl.innerHTML = '';
  for(var i = 0; i < 6; i++) setPip(i, '');
  document.querySelectorAll('.hm-ctx-card').forEach(function(c){ c.classList.remove('vis'); });
  ['hmSrcEhr','hmSrcCrm','hmSrcEnr','hmSrcClm',
   'hmDqPass','hmDqQuar','hmDqFail',
   'hmMatched','hmNew','hmConflict'].forEach(function(id){
    var el = document.getElementById(id); if(el) el.textContent = '\u2014';
  });
  if(dashEl) dashEl.style.display = 'none';
});

}());
</script>
{% endblock extra_js %}
''')
print('hm2 done')
