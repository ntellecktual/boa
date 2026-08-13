"""write_dq2.py — data_quality.html 7-ideations (part 2 of 2, append)"""
TMPL = r'boaapp/templates/boaapp/data_quality.html'
out = open(TMPL, 'a', encoding='utf-8')
out.write(r'''
<!-- ══ CLASSROOM ══ -->
<section class="dq-section" id="dq-classroom">
  <div class="dq-sec-head">
    <h2>Classroom</h2>
    <p>Six data quality concepts &#8212; from CVUTC dimensions to SLA-based remediation frameworks.</p>
  </div>
  <div class="dq-cls-wrap">
    <div class="dq-cls-track">
      <div class="dq-cls-slide active" data-slide="0">
        <div class="dq-cls-num">Slide 1 of 6</div>
        <h3>The CVUTC Data Quality Framework</h3>
        <p>Five dimensions, popularized by Loshin (2001) and formalized in ISO 8000: <strong>Completeness</strong> (are required fields populated?), <strong>Validity</strong> (do values conform to rules?), <strong>Uniqueness</strong> (are records deduplicated?), <strong>Timeliness</strong> (is data current?), <strong>Consistency</strong> (do related fields agree?).</p>
        <p>Each dimension maps to a distinct business risk. Measuring them separately enables root-cause triage: a Completeness failure points to front desk training, a Validity failure points to OTA field mapping, a Uniqueness failure points to system sync issues.</p>
        <div class="dq-cls-formula">DQ Score = &#8721;(passing_rules / total_rules) &#215; 100&nbsp;&nbsp;&#8594;&nbsp;&nbsp;Target: &ge;95% for revenue management pipelines</div>
      </div>
      <div class="dq-cls-slide" data-slide="1">
        <div class="dq-cls-num">Slide 2 of 6</div>
        <h3>Great Expectations: Data Quality as Code</h3>
        <p>Great Expectations (GE) defines data quality rules as Python objects: <code>expect_column_values_to_be_between(column="rate", min_value=89, max_value=1500)</code>. Rules execute against DataFrames or database tables and produce machine-readable JSON reports.</p>
        <p>The critical architectural insight: data quality rules belong in version control alongside pipeline code. A breaking change in source data fails the GE suite in CI/CD, just like a breaking unit test. This turns data quality from a reactive monthly report into a proactive gate.</p>
        <div class="dq-cls-formula">Pipeline pattern: Extract &#8594; GE Checkpoint &#8594; [pass] Load / [fail] Quarantine + Alert</div>
      </div>
      <div class="dq-cls-slide" data-slide="2">
        <div class="dq-cls-num">Slide 3 of 6</div>
        <h3>Completeness: The Invisible Quality Problem</h3>
        <p>NULL fields are the most common and most underestimated quality issue. Unlike invalid values, NULLs silently propagate through joins and aggregations. A NULL guest name produces no error &#8212; it just becomes &#34;Unknown&#34; in your loyalty mailing list, wasting a direct mail piece.</p>
        <p>Completeness rules must distinguish between structurally required fields (guest name, check-in date &#8212; always required) and conditionally required fields (loyalty ID &#8212; required only for enrolled members). Blanket NOT NULL rules on conditional fields generate false failures.</p>
        <div class="dq-cls-formula">Completeness rate = (populated_fields / total_fields) &#215; 100&nbsp;&nbsp;Target: 99.5% for PII fields</div>
      </div>
      <div class="dq-cls-slide" data-slide="3">
        <div class="dq-cls-num">Slide 4 of 6</div>
        <h3>Regex Validation: Email as a Case Study</h3>
        <p>Email validation is the canonical regex quality rule &#8212; and also the most commonly over-engineered. The RFC 5322 full regex is 6,394 characters. The practical rule for hospitality data: <code>/^[\w.+-]+@[\w-]+\.[\w.]+$/</code> catches 99.7% of real typos (missing @, incomplete domain, no TLD) without rejecting valid international addresses.</p>
        <p>More important than the regex: <em>what do you do on failure?</em> Hotel strategy: quarantine the row, create a fallback record with hotel-assigned email, and route a data quality ticket to the originating property with the corrected format shown.</p>
        <div class="dq-cls-formula">Common hotel email errors: front-desk typos (p.alvarez@), OTA mapping failures (email={blank}), test records (test@test)</div>
      </div>
      <div class="dq-cls-slide" data-slide="4">
        <div class="dq-cls-num">Slide 5 of 6</div>
        <h3>Consistency Rules: Date Logic in Hospitality</h3>
        <p>Consistency validates relationships between fields, not just individual values. The canonical hospitality example: check-out must be strictly after check-in. Sounds obvious; happens constantly. AM/PM confusion at front desk, midnight check-outs entered as check-ins, OTA date format mismatches (MM/DD vs DD/MM).</p>
        <p>A more subtle consistency rule: check-in date for a historical extract should not be in the far future. OMN-284708 (William Foster, La Costa, Dec 2027) is a real advance reservation &#8212; valid in booking systems, but flags a data timeliness concern when it appears in an April 2026 extract that should only contain current/recent reservations.</p>
        <div class="dq-cls-formula">Consistency score = rows_passing_all_cross_field_rules / total_rows &#215; 100</div>
      </div>
      <div class="dq-cls-slide" data-slide="5">
        <div class="dq-cls-num">Slide 6 of 6</div>
        <h3>SLA-Based Remediation: Closing the Loop</h3>
        <p>A quality report no one acts on is theatre. The remediation SLA assigns criticality by dimension and routes failures to specific teams with response time commitments. Critical failures (rate=$0, checkout&lt;checkin) block the record from loading and page the duty manager. Non-critical failures quarantine the record but allow it to load with a quality flag.</p>
        <p>Trend analytics matter as much as point-in-time scores. A pipeline with 94% quality score that&#39;s trending up from 87% is healthier than one at 96% trending down from 99%. Track &#916;DQ week-over-week. A single property consistently at the bottom of the ranking points to a training or system configuration issue, not just a data entry error.</p>
        <div class="dq-cls-formula">SLA tiers: CRITICAL (&lt;4h) &#183; HIGH (&lt;24h) &#183; MEDIUM (&lt;72h) &#183; LOW (next sprint)</div>
      </div>
    </div>
    <div class="dq-cls-nav">
      <button class="dq-cls-nav-btn" onclick="dqClsPrev()">&#8592; Prev</button>
      <div class="dq-cls-dots" id="dqClsDots">
        <div class="dq-cls-dot active" onclick="dqGotoClsDot(0)"></div>
        <div class="dq-cls-dot" onclick="dqGotoClsDot(1)"></div>
        <div class="dq-cls-dot" onclick="dqGotoClsDot(2)"></div>
        <div class="dq-cls-dot" onclick="dqGotoClsDot(3)"></div>
        <div class="dq-cls-dot" onclick="dqGotoClsDot(4)"></div>
        <div class="dq-cls-dot" onclick="dqGotoClsDot(5)"></div>
      </div>
      <button class="dq-cls-nav-btn" onclick="dqClsNext()">Next &#8594;</button>
    </div>
  </div>
</section>

<!-- ══ KEY POINTS ══ -->
<section class="dq-section" id="dq-keypoints">
  <div class="dq-sec-head">
    <h2>Key Engineering Points</h2>
    <p>Four decisions that separate production-grade hospitality data quality from checkbox exercises.</p>
  </div>
  <div class="dq-kp-grid">
    <div class="dq-kp">
      <div class="dq-kp-icon">&#x1F3E8;</div>
      <h4>Opera PMS is the Source of Truth</h4>
      <p>Opera is deployed at 70%+ of large hotel chains. Its export format has idiosyncrasies: rate fields default to 0 (not NULL) on comp rooms, phone fields use property-specific formats, loyalty tier names vary by brand. Any GE ruleset must be calibrated to Opera&#39;s specific behavior &#8212; not generic SQL patterns.</p>
    </div>
    <div class="dq-kp">
      <div class="dq-kp-icon">&#x1F4E7;</div>
      <h4>Email as a Marketing Revenue Multiplier</h4>
      <p>Omni&#39;s email marketing generates $8.50 per valid address per year in direct booking revenue. At 4% invalid email rate across 2.3M loyalty members, that&#39;s $782K/year in unreachable guests. Email validation in the ETL pipeline pays for the entire data quality program within 3 months.</p>
    </div>
    <div class="dq-kp">
      <div class="dq-kp-icon">&#x1F4C5;</div>
      <h4>Date Consistency Errors Compound</h4>
      <p>A checkout-before-checkin error doesn&#39;t just affect one record. Revenue management models use rolling averages of stay duration. One -3 night stay (checkin April 12, checkout April 9) corrupts the average, distorting rate optimization algorithms that rely on accurate length-of-stay distribution. The cascade is invisible unless you measure it.</p>
    </div>
    <div class="dq-kp">
      <div class="dq-kp-icon">&#x1F9EE;</div>
      <h4>Statistical vs. Rule-Based Validation</h4>
      <p>Rule-based checks (GE expectations) catch known violation types. Statistical checks (Z-score on rate distribution, Kullback-Leibler divergence on daily reservation volumes) catch unknown shifts &#8212; like an OTA suddenly sending room types in a new format that passes all explicit rules but breaks downstream category models.</p>
    </div>
  </div>
</section>

<!-- ══ CODE ══ -->
<section class="dq-section" id="dq-code">
  <div class="dq-sec-head">
    <h2>Production Code</h2>
    <p>Four patterns covering the full data quality stack: validation, profiling, anomaly detection on metrics, and alerting.</p>
  </div>
  <div class="dq-code-blocks">
    <details class="dq-code-block">
      <summary><i class="fas fa-check-double" style="color:var(--dq-accent)"></i>&nbsp;Great Expectations Suite for Hotel Reservations (Python)</summary>
      <pre><code><span class="kw">import</span> great_expectations <span class="kw">as</span> gx
<span class="kw">from</span> great_expectations.core.batch <span class="kw">import</span> RuntimeBatchRequest

context = gx.get_context()

suite = context.add_or_update_expectation_suite(<span class="str">"omni_reservations_suite"</span>)

<span class="kw">def</span> <span class="fn">build_expectation_suite</span>(validator):
    <span class="cm"># Uniqueness</span>
    validator.expect_column_values_to_be_unique(<span class="str">"res_id"</span>)

    <span class="cm"># Completeness — structurally required fields</span>
    <span class="kw">for</span> col <span class="kw">in</span> [<span class="str">"guest_name"</span>, <span class="str">"check_in"</span>, <span class="str">"check_out"</span>, <span class="str">"property"</span>, <span class="str">"room_type"</span>]:
        validator.expect_column_values_to_not_be_null(col)

    <span class="cm"># Validity — rate range ($89–$1500 covers standard to Presidential)</span>
    validator.expect_column_values_to_be_between(<span class="str">"rate"</span>, min_value=<span class="num">89</span>, max_value=<span class="num">1500</span>)

    <span class="cm"># Validity — email regex</span>
    validator.expect_column_values_to_match_regex(
        <span class="str">"email"</span>, regex=<span class="str">r"^[\w.+-]+@[\w-]+\.[\w.]+$"</span>
    )

    <span class="cm"># Validity — loyalty tier set</span>
    validator.expect_column_values_to_be_in_set(
        <span class="str">"loyalty"</span>,
        value_set=[<span class="str">"Select Guest"</span>, <span class="str">"Gold"</span>, <span class="str">"Platinum"</span>]
    )

    <span class="cm"># Consistency — checkout after checkin (custom SQL expectation)</span>
    validator.expect_column_pair_values_to_be_equal(
        column_A=<span class="str">"check_out"</span>, column_B=<span class="str">"check_in"</span>,
        or_equal=<span class="kw">False</span>,
        meta={<span class="str">"description"</span>: <span class="str">"check_out must be after check_in"</span>}
    )

    <span class="kw">return</span> validator.get_expectation_suite()</code></pre>
    </details>
    <details class="dq-code-block">
      <summary><i class="fas fa-chart-bar" style="color:var(--dq-accent)"></i>&nbsp;Automated Data Profiling with pandas-profiling (Python)</summary>
      <pre><code><span class="kw">import</span> pandas <span class="kw">as</span> pd
<span class="kw">from</span> ydata_profiling <span class="kw">import</span> ProfileReport
<span class="kw">import</span> snowflake.connector

<span class="kw">def</span> <span class="fn">profile_reservations</span>(date_range: tuple[str, str]) -> ProfileReport:
    conn = snowflake.connector.connect(
        user=<span class="str">"etl_service"</span>, account=<span class="str">"omni-hotels.us-east-1"</span>,
        warehouse=<span class="str">"ANALYTICS_WH"</span>, database=<span class="str">"OPERA_PROD"</span>
    )
    df = pd.read_sql(<span class="str">f"""
        SELECT res_id, guest_name, email, phone, check_in, check_out,
               room_type, rate, loyalty_tier, property_code
        FROM   reservations
        WHERE  created_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    """</span>, conn)

    profile = ProfileReport(
        df,
        title=<span class="str">f"Omni Reservations {date_range[0]} to {date_range[1]}"</span>,
        explorative=<span class="kw">True</span>,
        correlations={<span class="str">"auto"</span>: {<span class="str">"calculate"</span>: <span class="kw">True</span>}},
        missing_diagrams={<span class="str">"heatmap"</span>: <span class="kw">True</span>, <span class="str">"dendrogram"</span>: <span class="kw">True</span>}
    )

    <span class="cm"># Key stats: missing rates, value distributions, correlations</span>
    completeness = (<span class="num">1</span> - df.isnull().mean()) * <span class="num">100</span>
    <span class="kw">print</span>(completeness.sort_values())          <span class="cm"># spot bottom fields</span>
    <span class="kw">print</span>(df[<span class="str">"rate"</span>].describe())              <span class="cm"># outlier check</span>
    <span class="kw">return</span> profile</code></pre>
    </details>
    <details class="dq-code-block">
      <summary><i class="fas fa-bell" style="color:var(--dq-accent)"></i>&nbsp;Statistical Alert on Daily Quality Score Regression (Python)</summary>
      <pre><code><span class="kw">import</span> numpy <span class="kw">as</span> np
<span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass

@dataclass
<span class="kw">class</span> <span class="fn">QualityAlert</span>:
    date: str; score: float; z_score: float; prev_scores: list[float]

<span class="kw">class</span> <span class="fn">QualityRegressionDetector</span>:
    <span class="str">"""Detect unusual drops in daily DQ score using rolling Z-Score.
    Fires if today's score is >2.5 sigma below the rolling mean."""</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, window: int = <span class="num">14</span>, threshold: float = <span class="num">2.5</span>):
        self.window = window; self.threshold = threshold
        self._history: list[tuple[str, float]] = []

    <span class="kw">def</span> <span class="fn">update</span>(self, date: str, score: float) -> QualityAlert | <span class="kw">None</span>:
        self._history.append((date, score))
        <span class="kw">if</span> len(self._history) <= self.window:
            <span class="kw">return</span> <span class="kw">None</span>

        recent = [s <span class="kw">for</span> _, s <span class="kw">in</span> self._history[-self.window - <span class="num">1</span>:-<span class="num">1</span>]]
        mu = np.mean(recent); sigma = np.std(recent, ddof=<span class="num">1</span>)
        <span class="kw">if</span> sigma == <span class="num">0</span>: <span class="kw">return</span> <span class="kw">None</span>

        z = (score - mu) / sigma
        <span class="kw">if</span> z < -self.threshold:
            <span class="kw">return</span> <span class="fn">QualityAlert</span>(date=date, score=score, z_score=z, prev_scores=recent)
        <span class="kw">return</span> <span class="kw">None</span>

<span class="cm"># Usage: called nightly after GE checkpoint</span>
detector = <span class="fn">QualityRegressionDetector</span>(window=<span class="num">14</span>)
<span class="kw">for</span> date, score <span class="kw">in</span> daily_scores:  <span class="cm"># from DQ metrics table</span>
    alert = detector.update(date, score)
    <span class="kw">if</span> alert: send_pagerduty(alert)   <span class="cm"># page duty manager</span></code></pre>
    </details>
    <details class="dq-code-block">
      <summary><i class="fas fa-filter" style="color:var(--dq-accent)"></i>&nbsp;Quarantine + Remediation Router (Python)</summary>
      <pre><code><span class="kw">from</span> enum <span class="kw">import</span> Enum
<span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass, field

<span class="kw">class</span> <span class="fn">Severity</span>(str, Enum):
    CRITICAL = <span class="str">"critical"</span>   <span class="cm"># blocks load, pages duty manager</span>
    HIGH     = <span class="str">"high"</span>       <span class="cm"># quarantines row, creates Jira P1</span>
    MEDIUM   = <span class="str">"medium"</span>     <span class="cm"># loads with quality flag, Jira P2</span>
    LOW      = <span class="str">"low"</span>        <span class="cm"># logs only, next-sprint backlog</span>

DIMENSION_SLA = {
    <span class="str">"CONSISTENCY"</span>: <span class="fn">Severity</span>.CRITICAL,  <span class="cm"># checkout &lt; checkin</span>
    <span class="str">"RANGE"</span>:       <span class="fn">Severity</span>.HIGH,       <span class="cm"># rate = $0 or $5000+</span>
    <span class="str">"UNIQUE"</span>:      <span class="fn">Severity</span>.HIGH,       <span class="cm"># duplicate res_id</span>
    <span class="str">"NOT NULL"</span>:    <span class="fn">Severity</span>.MEDIUM,     <span class="cm"># missing required field</span>
    <span class="str">"REGEX"</span>:       <span class="fn">Severity</span>.MEDIUM,     <span class="cm"># invalid email/phone</span>
    <span class="str">"SET"</span>:         <span class="fn">Severity</span>.LOW,        <span class="cm"># unexpected loyalty tier</span>
    <span class="str">"DATE PAST"</span>:   <span class="fn">Severity</span>.LOW,        <span class="cm"># future date in historical extract</span>
}

@dataclass
<span class="kw">class</span> <span class="fn">RemediationAction</span>:
    res_id: str; rule_type: str; severity: <span class="fn">Severity</span>; action: str

<span class="kw">def</span> <span class="fn">route_failures</span>(failures: list[dict]) -> list[RemediationAction]:
    actions = []
    <span class="kw">for</span> f <span class="kw">in</span> failures:
        sev = DIMENSION_SLA.get(f[<span class="str">"rule_type"</span>], <span class="fn">Severity</span>.LOW)
        action_map = {
            <span class="fn">Severity</span>.CRITICAL: <span class="str">"BLOCK_LOAD|PAGE_MANAGER"</span>,
            <span class="fn">Severity</span>.HIGH:     <span class="str">"QUARANTINE|CREATE_JIRA_P1"</span>,
            <span class="fn">Severity</span>.MEDIUM:   <span class="str">"LOAD_FLAGGED|CREATE_JIRA_P2"</span>,
            <span class="fn">Severity</span>.LOW:      <span class="str">"LOAD_FLAGGED|LOG_ONLY"</span>,
        }
        actions.append(<span class="fn">RemediationAction</span>(
            res_id=f[<span class="str">"res_id"</span>], rule_type=f[<span class="str">"rule_type"</span>],
            severity=sev, action=action_map[sev]
        ))
    <span class="kw">return</span> actions</code></pre>
    </details>
  </div>
</section>

<!-- ══ ABOUT ══ -->
<section class="dq-section" id="dq-about">
  <div class="dq-sec-head">
    <h2>About This Demo</h2>
    <p>A Great Expectations-style validation suite running against real Omni Hotels reservation patterns.</p>
  </div>
  <div class="dq-about-card">
    <h3>&#x1F3E8; Omni Hotels Data Quality Framework</h3>
    <p>Eight validation rules across five CVUTC dimensions, animated rule-by-rule execution, SVG quality score ring, and per-column failure attribution. Mirrors production Opera PMS &#8594; Snowflake pipeline patterns.</p>
    <p style="font-size:.72rem;color:var(--dq-muted)">Stack: JavaScript &#183; Great Expectations patterns &#183; Django 5.1 &#183; Hospitality Data Engineering</p>
    <button class="dq-share-btn" onclick="dqShareDemo()">&#x1F517; Copy Link</button>
  </div>
</section>

</div><!-- /dq-wrap -->
{% endblock content %}
{% block extra_js %}
<script>
(function(){
'use strict';

/* ══ 7-ideations nav & ELI5 ══ */
var dqClsCurrent=0;
var dqELI5Selected=null;

var DQ_ELI5={
  steward:{
    label:'Data Steward',
    title:'Data Quality Ownership &#8212; Your Role in the Pipeline',
    run:function(){
      return {
        body:'As data steward, you own the quality SLA for the Opera &#8594; Snowflake pipeline. Today&#39;s extract has 6 quality issues across 10 reservations &#8212; a 25% affected-row rate. The most serious: OMN-284704 (Sarah Mitchell) has checkout before checkin. That means her Dallas stay shows as -3 nights in every revenue report until it&#39;s corrected.<br><br>Your dashboard should show this as a CRITICAL failure requiring immediate fix. The loyalty dimensions failed 50% &#8212; two of four loyalty rules &#8212; because walk-in OMN-284703 has no tier. That&#39;s an expected pattern for walk-ins. Your job: distinguish expected NULLs from unexpected ones.',
        stats:['Affected rows: 6/10 (60%)','CRITICAL failures: 1 (date consistency)','HIGH failures: 3 (rate, email, unique)','Expected NULLs: 1 (walk-in guest)']
      };
    }
  },
  analyst:{
    label:'BI Analyst',
    title:'Dashboard Trust Requires Clean Upstream Data',
    run:function(){
      return {
        body:'Your RevPAR dashboard is only as good as the rate data flowing into it. OMN-284709 (Lisa Nakamura, Barton Creek) has rate=$0. If that loads undetected, it drags the property ADR from $284 to $255 &#8212; an 11% apparent decline that will trigger a fire drill from the GM. And OMN-284705 (Robert Kim, San Francisco) at $2,850 is a Presidential Suite &#8212; legitimate, but a statistical outlier that skews average calculations if not flagged.<br><br>The solution: rate range validation ($89&#8211;$1,500) catches both. Outlier-adjusted ADR (trimmed mean at 5%/95% percentiles) handles legitimate luxury rates without distorting the metric.',
        stats:['ADR impact of $0 rate: -11% distortion','Presidential suite rate: $2,850 (valid outlier)','Trimmed-mean approach: standard in hotel BI','Data quality &#8594; dashboard trust &#8594; good decisions']
      };
    }
  },
  dba:{
    label:'DBA',
    title:'Constraint Enforcement Strategy &#8212; Database vs. Application',
    run:function(){
      return {
        body:'The architectural debate: should date consistency (checkout &gt; checkin) be a database CHECK constraint or an application-layer rule? Database constraints are faster and cannot be bypassed &#8212; but Opera PMS sometimes temporarily violates them during multi-step updates, causing load failures.<br><br>Best practice: permissive database schema (no CHECK constraints on business rules), strict application-layer validation via GE, and a separate quarantine table for failed records. This prevents Opera&#39;s transient states from blocking the ETL while still ensuring downstream tables only contain valid data.',
        stats:['Permissive schema: no business-rule CHECK constraints','GE validation: catches Opera transient violations','Quarantine table: holds failures for remediation','Downstream tables: 100% constraint-clean data']
      };
    }
  },
  revenue:{
    label:'Revenue Manager',
    title:'ADR Errors from Bad Dates &#8212; Revenue at Risk',
    run:function(){
      return {
        body:'Revenue managers live and die by ADR (Average Daily Rate) and RevPAR (Revenue Per Available Room). Both are calculated as total_room_revenue / occupied_room_nights. The "room nights" denominator is computed from check-in and check-out dates. OMN-284704&#39;s -3 night stay makes the denominator smaller by 3, inflating the ADR by $319/total_nights &#8212; a subtle distortion that compounds across a full property.<br><br>The ROI of this validation: one prevented ADR miscalculation averts a misguided rate strategy decision. Omni&#39;s Dallas property has 295 rooms; one bad rate decision costs $8,000&#8211;$25,000 in lost RevPAR per night. The entire data quality program is justified by a single prevented strategic error.',
        stats:['ADR denominator corruption per bad date: 3 room-nights','Dallas property: 295 rooms','Cost of misguided rate strategy: $8K&#8211;$25K/night','ROI of DQ program: positive after first prevented error']
      };
    }
  }
};

function dqSetMode(mode){
  document.querySelectorAll('.dq-mode-btn').forEach(function(b){
    b.classList.toggle('active',b.getAttribute('data-mode')===mode);
  });
  document.querySelectorAll('.dq-pane').forEach(function(p){
    p.classList.toggle('active',p.getAttribute('data-pane')===mode);
  });
}
function dqSelectPersona(key){
  dqELI5Selected=key;
  document.querySelectorAll('.dq-persona').forEach(function(p){
    p.classList.toggle('selected',p.getAttribute('data-key')===key);
  });
  document.getElementById('dqELI5Result').classList.remove('show');
}
function dqRunELI5(){
  if(!dqELI5Selected){alert('Select a persona first!');return;}
  var p=DQ_ELI5[dqELI5Selected];
  var data=p.run();
  document.getElementById('dqELI5Title').innerHTML=p.title;
  document.getElementById('dqELI5Body').innerHTML=data.body;
  var statsHtml=data.stats.map(function(s){return '<span class="dq-eli5-stat">'+s+'</span>';}).join('');
  document.getElementById('dqELI5Stats').innerHTML=statsHtml;
  document.getElementById('dqELI5Result').classList.add('show');
}
function dqClsShowSlide(n){
  dqClsCurrent=n;
  document.querySelectorAll('.dq-cls-slide').forEach(function(s,i){s.classList.toggle('active',i===n);});
  document.querySelectorAll('.dq-cls-dot').forEach(function(d,i){d.classList.toggle('active',i===n);});
}
function dqClsNext(){dqClsShowSlide((dqClsCurrent+1)%6);}
function dqClsPrev(){dqClsShowSlide((dqClsCurrent+5)%6);}
function dqGotoClsDot(n){dqClsShowSlide(n);}
function dqShareDemo(){
  navigator.clipboard.writeText(window.location.href).then(function(){
    var btn=document.querySelector('.dq-share-btn');
    btn.textContent='\u2713 Copied!';
    setTimeout(function(){btn.innerHTML='&#x1F517; Copy Link';},2000);
  });
}
function dqScrollTo(id){
  var el=document.getElementById(id);
  if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
  document.querySelectorAll('.dq-nav-btn').forEach(function(b){
    b.classList.remove('active');
    if(b.getAttribute('onclick')&&b.getAttribute('onclick').indexOf(id)>-1) b.classList.add('active');
  });
}
function dqInitNav(){
  var fill=document.getElementById('dqProgressFill');
  var secs=Array.from(document.querySelectorAll('.dq-section'));
  var btns=Array.from(document.querySelectorAll('.dq-nav-btn'));
  window.addEventListener('scroll',function(){
    var scrolled=window.scrollY;
    var total=document.documentElement.scrollHeight-window.innerHeight;
    fill.style.width=(total>0?Math.min(100,scrolled/total*100):0)+'%';
    var active=0;
    secs.forEach(function(s,i){if(s.getBoundingClientRect().top<100)active=i;});
    btns.forEach(function(b,i){b.classList.toggle('active',i===active);});
  });
}

/* exports */
window.dqSetMode=dqSetMode;
window.dqSelectPersona=dqSelectPersona;
window.dqRunELI5=dqRunELI5;
window.dqClsNext=dqClsNext;
window.dqClsPrev=dqClsPrev;
window.dqGotoClsDot=dqGotoClsDot;
window.dqShareDemo=dqShareDemo;
window.dqScrollTo=dqScrollTo;

/* ══ Original data quality interactive suite ══ */
var DATA=[
  {res_id:'OMN-284701',guest:'Margaret Chen',     email:'m.chen@deloitte.com',   phone:'617-555-0142',cin:'2026-04-10',cout:'2026-04-12',room:'Deluxe King',    rate:289, loyalty:'Select Guest',property:'Omni Parker House',       _issues:[]},
  {res_id:'OMN-284702',guest:'James Rodriguez',   email:'j.rodriguez@gmail.com', phone:'312-555-0198',cin:'2026-04-08',cout:'2026-04-11',room:'Premier Suite',   rate:549, loyalty:'Select Guest',property:'Omni Chicago Hotel',      _issues:[]},
  {res_id:'OMN-284703',guest:'',                  email:'walk.in@na',            phone:'',             cin:'2026-04-11',cout:'2026-04-12',room:'Standard Queen',  rate:199, loyalty:'',            property:'Omni Nashville Hotel',    _issues:['guest','email','phone','loyalty']},
  {res_id:'OMN-284704',guest:'Sarah Mitchell',    email:'s.mitchell@amex.com',   phone:'214-555-0267',cin:'2026-04-12',cout:'2026-04-09',room:'Deluxe King',    rate:319, loyalty:'Gold',          property:'Omni Dallas Hotel',       _issues:['cout']},
  {res_id:'OMN-284705',guest:'Robert Kim',        email:'r.kim@jpmorgan.com',    phone:'415-555-0334',cin:'2026-04-09',cout:'2026-04-13',room:'Presidential',    rate:2850,loyalty:'Platinum',      property:'Omni San Francisco',      _issues:['rate']},
  {res_id:'OMN-284701',guest:'Margaret Chen',     email:'m.chen@deloitte.com',   phone:'617-555-0142',cin:'2026-04-10',cout:'2026-04-12',room:'Deluxe King',    rate:289, loyalty:'Select Guest',property:'Omni Parker House',       _issues:['res_id']},
  {res_id:'OMN-284707',guest:'Patricia Alvarez',  email:'p.alvarez@',            phone:'404-555-0411',cin:'2026-04-11',cout:'2026-04-14',room:'Club Level',      rate:429, loyalty:'Gold',          property:'Omni CNN Center',         _issues:['email']},
  {res_id:'OMN-284708',guest:'William Foster',    email:'w.foster@microsoft.com',phone:'858-555-0156',cin:'2027-12-25',cout:'2027-12-28',room:'Oceanfront King', rate:479, loyalty:'Platinum',      property:'Omni La Costa Resort',    _issues:['cin']},
  {res_id:'OMN-284709',guest:'Lisa Nakamura',     email:'l.nakamura@sony.com',   phone:'512-555-0289',cin:'2026-04-07',cout:'2026-04-10',room:'Deluxe Double',   rate:0,   loyalty:'Select Guest',property:'Omni Barton Creek',       _issues:['rate']},
  {res_id:'OMN-284710',guest:'David Thompson',    email:'d.thompson@ge.com',     phone:'202-555-0373',cin:'2026-04-13',cout:'2026-04-15',room:'Standard King',   rate:259, loyalty:'Gold',          property:'Omni Shoreham DC',        _issues:[]}
];
var RULES=[
  {col:'res_id',desc:'expect_column_values_to_be_unique',param:'\u2014',type:'UNIQUE',
   check:function(data){var seen={};return data.filter(function(r){if(seen[r.res_id])return true;seen[r.res_id]=1;return false;}).length;}},
  {col:'guest_name',desc:'expect_column_values_to_not_be_null',param:'\u2014',type:'NOT NULL',
   check:function(data){return data.filter(function(r){return !r.guest||r.guest.trim()==='';}).length;}},
  {col:'email',desc:'expect_column_values_to_match_regex',param:'/^[\\w.+-]+@[\\w-]+\\.[\\w.]+$/',type:'REGEX',
   check:function(data){return data.filter(function(r){return !r.email||!/^[\w.+-]+@[\w-]+\.[\w.]+$/.test(r.email);}).length;}},
  {col:'phone',desc:'expect_column_values_to_not_be_null',param:'\u2014',type:'NOT NULL',
   check:function(data){return data.filter(function(r){return !r.phone||r.phone.trim()==='';}).length;}},
  {col:'rate',desc:'expect_column_values_to_be_between',param:'$89 \u2013 $1,500/night',type:'RANGE',
   check:function(data){return data.filter(function(r){return r.rate<89||r.rate>1500;}).length;}},
  {col:'check_out',desc:'expect_checkout_after_checkin',param:'check_out > check_in',type:'CONSISTENCY',
   check:function(data){return data.filter(function(r){return new Date(r.cout)<=new Date(r.cin);}).length;}},
  {col:'check_in',desc:'expect_column_values_to_be_in_the_past',param:'\u2264 today (in extract)',type:'DATE PAST',
   check:function(data){var cut=new Date('2026-04-15');return data.filter(function(r){return new Date(r.cin)>cut;}).length;}},
  {col:'loyalty',desc:'expect_column_values_to_be_in_set',param:'{Select Guest, Gold, Platinum}',type:'SET',
   check:function(data){var valid=['Select Guest','Gold','Platinum'];return data.filter(function(r){return !r.loyalty||valid.indexOf(r.loyalty)<0;}).length;}}
];
var COLS=['res_id','guest','email','phone','cin','cout','room','rate','loyalty','property'];
var tbody=document.getElementById('dqDataBody');
DATA.forEach(function(row){
  var tr=document.createElement('tr');
  var issues=row._issues||[];
  if(issues.length>1) tr.className='dq-row--bad';
  else if(issues.length===1) tr.className='dq-row--warn';
  COLS.forEach(function(col){
    var td=document.createElement('td');
    var val=row[col];
    if(col==='rate'&&val!==0&&val) td.textContent='$'+val;
    else if(val===''||val===null||val===undefined||val===0){td.textContent=(col==='rate')?'$0':'NULL';td.style.opacity='.4';}
    else td.textContent=val;
    if(issues.indexOf(col)>-1) td.className=issues.length>1?'dq-cell--err':'dq-cell--warn';
    tr.appendChild(td);
  });
  tbody.appendChild(tr);
});
var rulesBody=document.getElementById('dqRulesBody');
RULES.forEach(function(rule,idx){
  var tr=document.createElement('tr');
  tr.id='dq-rule-'+idx;
  tr.innerHTML='<td style="font-weight:700">'+rule.col+'</td>'
    +'<td style="font-size:.6rem;opacity:.7">'+rule.desc+'</td>'
    +'<td><code style="font-size:.58rem">'+rule.param+'</code></td>'
    +'<td id="dq-fail-'+idx+'" style="font-size:.66rem;opacity:.45">\u2014</td>'
    +'<td><span class="dq-rule-status dq-rule-status--pending" id="dq-status-'+idx+'">\u00B7</span></td>';
  rulesBody.appendChild(tr);
});
document.getElementById('dqRunBtn').addEventListener('click',function(){
  this.disabled=true;
  this.innerHTML='<i class="fas fa-spinner fa-spin"></i> Running\u2026';
  var self=this;
  var results=[];
  function runNext(idx){
    if(idx>=RULES.length){
      setTimeout(function(){showReport(results);self.innerHTML='<i class="fas fa-redo"></i> Re-run Suite';self.disabled=false;},400);
      return;
    }
    var statusEl=document.getElementById('dq-status-'+idx);
    statusEl.className='dq-rule-status dq-rule-status--running';
    statusEl.textContent='\u21BB';
    setTimeout(function(){
      try{
        var failures=RULES[idx].check(DATA);
        results.push({rule:RULES[idx],failures:failures});
        document.getElementById('dq-fail-'+idx).textContent=failures>0?failures+' row'+(failures>1?'s':''):'0 rows';
        document.getElementById('dq-fail-'+idx).style.color=failures>0?'#ef4444':'#10b981';
        document.getElementById('dq-fail-'+idx).style.opacity='1';
        statusEl.className='dq-rule-status '+(failures===0?'dq-rule-status--pass':'dq-rule-status--fail');
        statusEl.textContent=failures===0?'\u2713':'\u2715';
      }catch(e){}
      runNext(idx+1);
    },500);
  }
  runNext(0);
});
function showReport(results){
  var panel=document.getElementById('dqScorePanel');
  panel.style.display='block';
  panel.scrollIntoView({behavior:'smooth',block:'start'});
  var passing=results.filter(function(r){return r.failures===0;}).length;
  var score=Math.round(passing/results.length*100);
  var circumference=251.2;
  var offset=circumference*(1-score/100);
  document.getElementById('dqRingPath').style.strokeDashoffset=offset;
  document.getElementById('dqRingPath').style.stroke=score>=80?'#10b981':score>=60?'#f59e0b':'#ef4444';
  setTimeout(function(){document.getElementById('dqScoreNum').textContent=score+'%';},200);
  var colGrid=document.getElementById('dqColGrid');
  colGrid.innerHTML='';
  var colResults={};
  results.forEach(function(r){colResults[r.rule.col]=r.failures;});
  Object.keys(colResults).forEach(function(col){
    var fail=colResults[col]>0;
    var badge=document.createElement('div');
    badge.className='dq-col-badge'+(fail?' dq-col-badge--fail':'');
    badge.innerHTML='<div class="dq-col-badge-name">'+col+'</div><div class="dq-col-badge-stat">'+(fail?'<span style="color:#ef4444">\u2715</span> '+colResults[col]+' issue'+(colResults[col]>1?'s':''):'<span style="color:#10b981">\u2713</span> OK')+'</div>';
    colGrid.appendChild(badge);
  });
  var dims=[
    {name:'Completeness',pass:results.filter(function(r){return r.rule.type==='NOT NULL'&&r.failures===0;}).length,total:results.filter(function(r){return r.rule.type==='NOT NULL';}).length},
    {name:'Validity',pass:results.filter(function(r){return (r.rule.type==='RANGE'||r.rule.type==='REGEX'||r.rule.type==='SET')&&r.failures===0;}).length,total:results.filter(function(r){return r.rule.type==='RANGE'||r.rule.type==='REGEX'||r.rule.type==='SET';}).length},
    {name:'Uniqueness',pass:results.filter(function(r){return r.rule.type==='UNIQUE'&&r.failures===0;}).length,total:results.filter(function(r){return r.rule.type==='UNIQUE';}).length},
    {name:'Timeliness',pass:results.filter(function(r){return r.rule.type==='DATE PAST'&&r.failures===0;}).length,total:results.filter(function(r){return r.rule.type==='DATE PAST';}).length},
    {name:'Consistency',pass:results.filter(function(r){return r.rule.type==='CONSISTENCY'&&r.failures===0;}).length,total:results.filter(function(r){return r.rule.type==='CONSISTENCY';}).length}
  ];
  var dimGrid=document.getElementById('dqDimGrid');
  dimGrid.innerHTML='';
  dims.forEach(function(d){
    var pct=d.total>0?Math.round(d.pass/d.total*100):100;
    var div=document.createElement('div');
    div.className='dq-dim'+(pct<100?' dq-dim-fail':'');
    div.innerHTML='<div class="dq-dim-val">'+pct+'%</div><div class="dq-dim-lbl">'+d.name+'</div>';
    dimGrid.appendChild(div);
  });
}

dqInitNav();
}());
</script>
{% endblock extra_js %}
''')
out.close()
print('dq2 done')
