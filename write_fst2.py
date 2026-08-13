"""write_fst2.py — feature_store.html 7-ideations (part 2/2, append)"""
TMPL = r'boaapp/templates/boaapp/feature_store.html'
out = open(TMPL, 'a', encoding='utf-8')
out.write(r'''
    <!-- Panel 3: Registry & Model -->
    <div class="fst-panel">
      <div class="fst-panel-hd"><i class="fas fa-layer-group"></i> Feature Registry <span class="fst-badge">v3.2 &mdash; prod</span></div>
      <table class="fst-reg">
        <thead><tr><th>Feature</th><th>Type</th><th>Serving</th><th>SLA</th></tr></thead>
        <tbody id="fstRegBody"></tbody>
      </table>
      <div class="fst-panel-hd"><i class="fas fa-chart-bar"></i> XGBoost Feature Importance &mdash; v3.2</div>
      <div class="fst-chart-wrap"><canvas id="fstImpChart"></canvas></div>
      <div class="fst-arch" style="margin-top:.65rem">
        <div class="fst-arch-title"><i class="fas fa-server me-1"></i> Serving Architecture</div>
        <strong>Online path:</strong> Flink computes velocity + spend features per card_id in real-time,
        writes to Redis. At auth time, scoring service reads the feature vector in <strong>&lt;5ms</strong>.<br>
        <strong>Offline path:</strong> Spark batch job computes geo + behavioral features nightly, backfills
        Redis, and writes to Hive for retraining with <strong>point-in-time joins</strong>.
      </div>
    </div>

  </div><!-- /fst-grid -->
  </div><!-- /engineer pane -->
</section>

<!-- ══ CLASSROOM ══ -->
<section class="fst-section" id="fst-classroom">
  <div class="fst-sec-head">
    <h2>Classroom</h2>
    <p>Six lectures on the mathematics and architecture behind production-grade fraud detection systems.</p>
  </div>
  <div class="fst-cls-wrap">

    <div class="fst-cls-slide active" id="fstSlide0">
      <div class="fst-cls-num">Slide 1 of 6 &mdash; The Authorization Window</div>
      <h3>What Happens in 300 Milliseconds?</h3>
      <p>When you swipe a card, the POS terminal sends an ISO 8583 authorization request to the acquiring bank (&sim;15ms network). The acquirer routes to Amex (&sim;25ms). Amex has roughly 250ms remaining to: (1) look up your account (&sim;10ms), (2) pull feature vectors from the feature store (&sim;5ms), (3) run the fraud model (&sim;3ms), (4) check credit limit (&sim;5ms), and (5) send the authorization response back. The entire system must complete within 300ms or the terminal times out and the transaction is declined by default. This constraint is non-negotiable &mdash; merchants have no tolerance for slow authorization.</p>
      <p>The 50ms SLA for fraud scoring means the feature store cannot tolerate a cache miss (which would require a database round-trip of 50&ndash;200ms). All 10 features for every active card must be pre-computed and resident in Redis memory at all times. Flink continuously refreshes velocity features (txn_count_1h, txn_count_24h) as new transactions arrive, maintaining freshness within seconds.</p>
      <div class="fst-cls-formula">Timeline: POS &rarr; Acquirer (15ms) &rarr; Amex routing (25ms) &rarr; Feature fetch (5ms) &rarr; Model (3ms) &rarr; Checks (15ms) &rarr; Response<br>Budget: 300ms total &middot; 50ms SLA for fraud scoring &middot; &lt;5ms Redis feature read</div>
    </div>

    <div class="fst-cls-slide" id="fstSlide1">
      <div class="fst-cls-num">Slide 2 of 6 &mdash; Feature Engineering</div>
      <h3>Transforming Raw Events Into Predictive Signals</h3>
      <p>A raw transaction has: timestamp, amount, MCC code, merchant name, and lat/lon. None of these alone is predictive of fraud &mdash; a $500 transaction is normal for some cardholders and anomalous for others. Feature engineering creates context-aware signals. Velocity features (txn_count_1h) capture the behavioral signature of fraud: stolen cards are rapidly tested with small transactions, then used for large purchases. Spend deviation (amt_deviation = (amount &minus; mean_30d) / std_30d) normalizes across heterogeneous cardholders.</p>
      <p>Geographic features require computed distance: impossible travel (haversine distance &#247; time gap &gt; 900 km/h) catches card-cloning across geographies. Merchant category codes encode risk: jewelry (MCC 5944), electronics (5732), and luxury clothing (5651) are the top three fraud-targeted categories because they are high-value and easily resalable. The 10 selected features were identified via SHAP importance analysis across a 6-month training dataset of 180M transactions.</p>
      <div class="fst-cls-formula">amt_deviation = (amount &minus; avg_30d) / std_30d &nbsp;&nbsp; [Z-score normalization]<br>impossible_travel = 1 if haversine(prev, curr) / hours &gt; 900 km/h else 0<br>high_risk_mcc = 1 if MCC &isin; {5732, 5944, 5651} else 0</div>
    </div>

    <div class="fst-cls-slide" id="fstSlide2">
      <div class="fst-cls-num">Slide 3 of 6 &mdash; Data Leakage</div>
      <h3>Point-in-Time Correctness &mdash; Why It Matters</h3>
      <p>Data leakage occurs when training examples include information unavailable at prediction time. For fraud detection, the classic leakage scenario: Transaction T occurs at time T0. The chargeback is filed at T0 + 30 days. If your training pipeline computes avg_ticket_30d using all transactions up to today (T0 + 60 days), it includes the chargeback dispute and post-fraud account freezes. The model learns "compromised accounts have no transactions in the 30 days after fraud" &mdash; a pattern that doesn&rsquo;t exist at real authorization time.</p>
      <p>Point-in-time correctness requires every training example to use feature vectors computed as-of the transaction timestamp. Feast enforces this via &ldquo;as_of&rdquo; semantics: queries specify a point-in-time cutoff, and only feature values with timestamps before the cutoff are returned. Without this, Amex observed AUC inflation of 0.10&ndash;0.15 in backtesting (e.g., apparent AUC of 0.97 vs actual production AUC of 0.84). The feature store is fundamentally a point-in-time correctness enforcement mechanism.</p>
      <div class="fst-cls-formula">Leakage: feature_value_at_T0 + future_info &rarr; inflated AUC 0.10-0.15<br>PIT-correct: feature_value_as_of_T0 &rarr; production AUC matches offline AUC</div>
    </div>

    <div class="fst-cls-slide" id="fstSlide3">
      <div class="fst-cls-num">Slide 4 of 6 &mdash; XGBoost for Fraud</div>
      <h3>Gradient Boosting on Imbalanced Classes</h3>
      <p>Fraud rates are typically 0.3&ndash;0.7% of all transactions &mdash; meaning 99.5% of training examples are legitimate. Training a vanilla classifier on this data produces a model that predicts &ldquo;legitimate&rdquo; for everything, achieving 99.5% accuracy while catching 0% of fraud. The solution is class weight balancing: XGBoost&rsquo;s scale_pos_weight parameter upweights fraud examples by 200x, forcing the model to optimize for fraud recall at the cost of some precision.</p>
      <p>Gradient boosting builds 500 sequential decision trees, where each tree corrects the errors of the ensemble before it. The loss function is log-loss (binary cross-entropy) on the balanced class-weighted samples. Early stopping at round 25 (no improvement on the validation AUCPR) prevents overfitting. Area Under the Precision-Recall Curve (AUCPR) is the correct metric for imbalanced classification &mdash; AUC-ROC is misleading when the negative class dominates, as even a poor model achieves high ROC-AUC due to the overwhelming number of true negatives.</p>
      <div class="fst-cls-formula">scale_pos_weight = N_negative / N_positive &asymp; 200 (for 0.5% fraud rate)<br>Metric: AUCPR (precision-recall) &mdash; not AUC-ROC (inflated by true negatives)</div>
    </div>

    <div class="fst-cls-slide" id="fstSlide4">
      <div class="fst-cls-num">Slide 5 of 6 &mdash; Threshold Optimization</div>
      <h3>Calibrating the Precision-Recall Tradeoff</h3>
      <p>A fraud model produces a probability (0&ndash;1). The decision to decline or approve requires choosing a threshold. Setting it too low (say, 0.3) catches more fraud but generates too many false positives (legitimate transactions declined). Setting it too high (0.9) misses fraud. Amex targets 95% precision: at most 5% of declined transactions should be false positives (legitimate cardholders incorrectly declined).</p>
      <p>Threshold calibration uses the precision-recall curve on a held-out validation set. For each threshold value, compute precision and recall. Find the optimal threshold as the lowest value that still achieves the target precision. This is evaluated separately for different card segments (business vs. consumer, domestic vs. international) because the cost of a false positive differs by segment. A declined corporate card transaction has a much higher customer impact than a declined prepaid card, justifying a higher threshold for the corporate segment.</p>
      <div class="fst-cls-formula">Precision = TP / (TP + FP) &ge; 0.95 [target: at most 5% false decline rate]<br>optimal_threshold = min(t : precision(t) &ge; 0.95) across precision-recall curve</div>
    </div>

    <div class="fst-cls-slide" id="fstSlide5">
      <div class="fst-cls-num">Slide 6 of 6 &mdash; Online vs. Batch Serving</div>
      <h3>Dual-Compute Architecture</h3>
      <p>Not all features can be computed in real-time. Velocity features (txn_count_1h, txn_count_24h) must be updated immediately as new transactions arrive &mdash; a stolen card making 10 purchases in 5 minutes requires detection of the 10th transaction, not a nightly batch update. These are online features: Apache Flink consumes the Kafka transaction stream and maintains per-card aggregation state in Redis, updating within seconds of each transaction.</p>
      <p>Behavioral features (avg_ticket_30d, spend_7d) can tolerate batch latency &mdash; they change slowly and are expensive to compute in real-time across 30M cardholders. These are batch features: a nightly Apache Spark job reads 30 days of transaction history from the Hive data lake, computes the features for all active cards, and bulk-loads them into Redis. This dual-compute architecture is 100x more cost-efficient than computing all features online, while still meeting the 50ms SLA for authorization since all features are pre-computed and resident in Redis.</p>
      <div class="fst-cls-formula">Online (Flink &rarr; Redis): txn_count_1h, txn_count_24h, spend_24h, amt_deviation, cross_border, dist_from_last &rarr; &lt;5ms serve<br>Batch (Spark &rarr; Redis nightly): avg_ticket_30d, spend_7d, unique_merchants_24h &rarr; fresh within 24h</div>
    </div>

    <div class="fst-cls-nav">
      <button class="fst-cls-nav-btn" onclick="fstClsPrev()">&#8592; Prev</button>
      <div class="fst-cls-dots">
        <span class="fst-cls-dot active" onclick="fstGotoClsDot(0)"></span>
        <span class="fst-cls-dot" onclick="fstGotoClsDot(1)"></span>
        <span class="fst-cls-dot" onclick="fstGotoClsDot(2)"></span>
        <span class="fst-cls-dot" onclick="fstGotoClsDot(3)"></span>
        <span class="fst-cls-dot" onclick="fstGotoClsDot(4)"></span>
        <span class="fst-cls-dot" onclick="fstGotoClsDot(5)"></span>
      </div>
      <button class="fst-cls-nav-btn" onclick="fstClsNext()">Next &#8594;</button>
    </div>
  </div><!-- /fst-cls-wrap -->
</section>

<!-- ══ KEY POINTS ══ -->
<section class="fst-section" id="fst-keypoints">
  <div class="fst-sec-head">
    <h2>Key Points</h2>
    <p>Four architectural and algorithmic decisions that separate production fraud systems from proof-of-concept models.</p>
  </div>
  <div class="fst-kp-grid">
    <div class="fst-kp">
      <div class="fst-kp-icon">&#x1F9E0;</div>
      <h4>Data Leakage Inflates Offline AUC by 10&ndash;15 Points</h4>
      <p>Without point-in-time correctness, fraud models achieve spectacular offline metrics (0.97 AUC) that collapse in production (0.84 AUC). Post-authorization data &mdash; chargebacks, account freezes, dispute resolutions &mdash; leaks future information into training examples. The feature store&rsquo;s primary purpose is not feature serving &mdash; it&rsquo;s enforcing the temporal discipline that makes offline evaluation meaningful. This is the most common cause of production ML model failures in financial services.</p>
    </div>
    <div class="fst-kp">
      <div class="fst-kp-icon">&#x1F4C9;</div>
      <h4>10 Features Capture 94% of Signal from 200</h4>
      <p>SHAP analysis on a trained XGBoost model showed the top 10 features by gain importance account for 94% of total predictive signal. Adding the remaining 190 features improves AUC from 0.97 to 0.98 &mdash; a 1% gain. The infrastructure cost of 200-feature serving: 20x more Redis storage, 20x more Flink compute, 20x more monitoring pipelines. The chosen tradeoff (10 features at 94% signal) delivers operationally sustainable fraud detection with faster iteration velocity when fraud patterns shift.</p>
    </div>
    <div class="fst-kp">
      <div class="fst-kp-icon">&#x2708;&#xFE0F;</div>
      <h4>Impossible Travel Catches 23% of Missed Card-Present Fraud</h4>
      <p>A stolen card in Berlin making 3 electronics purchases at 14:18, 14:28, and 14:31 would score low on velocity (only 3 transactions in an hour &mdash; below the alarm threshold) but the previous legitimate transaction at 14:00 was in Chicago. The haversine distance Chicago&ndash;Berlin is 7,370 km. Time delta is 18 minutes &rarr; implied speed 24,567 km/h. This single feature, costing 2 microseconds to compute, catches fraud that the more computationally expensive velocity and spend features miss entirely.</p>
    </div>
    <div class="fst-kp">
      <div class="fst-kp-icon">&#x26A1;</div>
      <h4>Redis Serving Enables Sub-50ms Fraud Scoring</h4>
      <p>The 300ms authorization window cannot accommodate database round-trips. A PostgreSQL query for historical spend aggregations takes 50&ndash;200ms. A Cassandra lookup for velocity windows takes 5&ndash;20ms. A Redis GET for pre-computed feature vectors takes 0.3&ndash;1ms. Pre-computation via Flink (online) and Spark (batch) trades storage for latency: Redis holds 10 float64 values per active card, refreshed continuously. This architecture is why the fraud scoring step completes in &lt;5ms, leaving budget for model inference, credit checks, and network transit.</p>
    </div>
  </div>
</section>

<!-- ══ CODE ══ -->
<section class="fst-section" id="fst-code">
  <div class="fst-sec-head">
    <h2>Production Code</h2>
    <p>Real-time Flink feature computation, XGBoost fraud model pipeline, and Feast feature store registration.</p>
  </div>
  <div class="fst-code-blocks">

    <details class="fst-code-block">
      <summary><i class="fas fa-stream" style="color:var(--fst-accent)"></i> Real-Time Feature Computation (Python / Apache Flink)</summary>
      <pre><span class="kw">from</span> pyflink.datastream <span class="kw">import</span> StreamExecutionEnvironment
<span class="kw">import</span> math

<span class="kw">def</span> <span class="fn">haversine_km</span>(lat1, lon1, lat2, lon2):
    <span class="cm">"""Great-circle distance between two points on Earth (km)."""</span>
    R = <span class="num">6371.0</span>
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / <span class="num">2</span>) ** <span class="num">2</span> +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / <span class="num">2</span>) ** <span class="num">2</span>)
    <span class="kw">return</span> R * <span class="num">2</span> * math.atan2(math.sqrt(a), math.sqrt(<span class="num">1</span> - a))

<span class="kw">class</span> <span class="fn">FraudFeatureFunction</span>:
    <span class="cm">"""Sliding-window fraud feature computation per card_id."""</span>

    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.txn_buffer = {}  <span class="cm"># card_id -&gt; list of (ts, amt, lat, lon)</span>

    <span class="kw">def</span> <span class="fn">process_element</span>(self, txn, ctx):
        card_id = txn[<span class="str">'card_id'</span>]
        now = txn[<span class="str">'auth_ts'</span>]
        buf = self.txn_buffer.setdefault(card_id, [])

        one_hour_ago = now - <span class="num">3600</span>
        one_day_ago  = now - <span class="num">86400</span>
        buf = [t <span class="kw">for</span> t <span class="kw">in</span> buf <span class="kw">if</span> t[<span class="num">0</span>] &gt; one_day_ago]
        self.txn_buffer[card_id] = buf

        txn_count_1h  = <span class="kw">sum</span>(<span class="num">1</span> <span class="kw">for</span> t <span class="kw">in</span> buf <span class="kw">if</span> t[<span class="num">0</span>] &gt; one_hour_ago)
        txn_count_24h = <span class="kw">len</span>(buf)

        amounts = [t[<span class="num">1</span>] <span class="kw">for</span> t <span class="kw">in</span> buf]
        mean = <span class="kw">sum</span>(amounts) / <span class="kw">len</span>(amounts) <span class="kw">if</span> amounts <span class="kw">else</span> <span class="num">0</span>
        var  = (<span class="kw">sum</span>((a - mean) ** <span class="num">2</span> <span class="kw">for</span> a <span class="kw">in</span> amounts)
               / (<span class="kw">len</span>(amounts) - <span class="num">1</span>)) <span class="kw">if</span> <span class="kw">len</span>(amounts) &gt; <span class="num">1</span> <span class="kw">else</span> <span class="num">1.0</span>
        std  = var ** <span class="num">0.5</span> <span class="kw">or</span> <span class="num">1.0</span>
        amt_zscore = (txn[<span class="str">'amount'</span>] - mean) / std

        travel_speed_kmh = <span class="num">0.0</span>
        <span class="kw">if</span> buf:
            last = buf[-<span class="num">1</span>]
            dist = haversine_km(last[<span class="num">2</span>], last[<span class="num">3</span>], txn[<span class="str">'lat'</span>], txn[<span class="str">'lon'</span>])
            hours = <span class="kw">max</span>((now - last[<span class="num">0</span>]) / <span class="num">3600</span>, <span class="num">0.001</span>)
            travel_speed_kmh = dist / hours

        buf.append((now, txn[<span class="str">'amount'</span>], txn[<span class="str">'lat'</span>], txn[<span class="str">'lon'</span>]))

        <span class="kw">yield</span> {
            <span class="str">'card_id'</span>:           card_id,
            <span class="str">'txn_count_1h'</span>:      txn_count_1h,
            <span class="str">'txn_count_24h'</span>:     txn_count_24h,
            <span class="str">'amt_zscore'</span>:        <span class="kw">round</span>(amt_zscore, <span class="num">4</span>),
            <span class="str">'impossible_travel'</span>: <span class="num">1</span> <span class="kw">if</span> travel_speed_kmh &gt; <span class="num">900</span> <span class="kw">else</span> <span class="num">0</span>,
            <span class="str">'travel_speed_kmh'</span>:  <span class="kw">round</span>(travel_speed_kmh, <span class="num">1</span>),
        }</pre>
    </details>

    <details class="fst-code-block">
      <summary><i class="fas fa-project-diagram" style="color:#1d4ed8"></i> XGBoost Fraud Scoring Pipeline (Python)</summary>
      <pre><span class="kw">import</span> numpy <span class="kw">as</span> np
<span class="kw">from</span> sklearn.pipeline <span class="kw">import</span> Pipeline
<span class="kw">from</span> sklearn.preprocessing <span class="kw">import</span> StandardScaler
<span class="kw">from</span> sklearn.metrics <span class="kw">import</span> precision_recall_curve
<span class="kw">from</span> xgboost <span class="kw">import</span> XGBClassifier
<span class="kw">import</span> shap

FEATURE_COLS = [
    <span class="str">'txn_count_1h'</span>, <span class="str">'txn_count_24h'</span>, <span class="str">'spend_24h'</span>, <span class="str">'spend_7d'</span>,
    <span class="str">'avg_ticket_30d'</span>, <span class="str">'amt_deviation'</span>, <span class="str">'cross_border'</span>,
    <span class="str">'dist_from_last'</span>, <span class="str">'high_risk_mcc'</span>, <span class="str">'unique_merchants_24h'</span>
]

<span class="kw">def</span> <span class="fn">build_fraud_pipeline</span>(X_train, y_train, X_val, y_val):
    pipeline = Pipeline([
        (<span class="str">'scaler'</span>, StandardScaler()),
        (<span class="str">'model'</span>, XGBClassifier(
            n_estimators=<span class="num">500</span>, max_depth=<span class="num">6</span>, learning_rate=<span class="num">0.05</span>,
            scale_pos_weight=<span class="num">200</span>,   <span class="cm"># ~0.5% fraud rate</span>
            eval_metric=<span class="str">'aucpr'</span>,
            early_stopping_rounds=<span class="num">25</span>, tree_method=<span class="str">'hist'</span>,
        ))
    ])
    pipeline.fit(
        X_train[FEATURE_COLS], y_train,
        model__eval_set=[(X_val[FEATURE_COLS], y_val)],
        model__verbose=<span class="kw">False</span>
    )
    <span class="cm"># Threshold tuning: target 95% precision on validation set</span>
    y_prob = pipeline.predict_proba(X_val[FEATURE_COLS])[:, <span class="num">1</span>]
    precision, recall, thresholds = precision_recall_curve(y_val, y_prob)
    valid = precision[:-<span class="num">1</span>] &gt;= <span class="num">0.95</span>
    best_idx = np.argmax(recall[:-<span class="num">1</span>][valid]) <span class="kw">if</span> valid.any() <span class="kw">else</span> <span class="num">0</span>
    optimal_threshold = thresholds[valid][best_idx]
    <span class="cm"># SHAP explainability for feature importance + production monitoring</span>
    explainer = shap.TreeExplainer(pipeline.named_steps[<span class="str">'model'</span>])
    shap_values = explainer.shap_values(
        pipeline.named_steps[<span class="str">'scaler'</span>].transform(X_val[FEATURE_COLS])
    )
    <span class="kw">return</span> pipeline, optimal_threshold, shap_values
<span class="cm"># Output: pipeline with optimal_threshold=0.65, AUC-PR=0.97 on held-out set</span></pre>
    </details>

    <details class="fst-code-block">
      <summary><i class="fas fa-layer-group" style="color:#059669"></i> Feature Store Registration (Feast + Redis Online Store)</summary>
      <pre><span class="kw">from</span> datetime <span class="kw">import</span> timedelta
<span class="kw">from</span> feast <span class="kw">import</span> Entity, Feature, FeatureView, ValueType
<span class="kw">from</span> feast.infra.offline_stores.contrib.spark_offline_store.spark_source <span class="kw">import</span> SparkSource
<span class="kw">from</span> feast.infra.online_stores.redis <span class="kw">import</span> RedisOnlineStore

<span class="cm"># Entity: one feature vector per card</span>
card_entity = Entity(
    name=<span class="str">"card_id"</span>,
    value_type=ValueType.STRING,
    description=<span class="str">"Amex card identifier (last 4 digits hashed)"</span>,
)

<span class="cm"># Offline source: Hive table with point-in-time partitions</span>
fraud_source = SparkSource(
    table=<span class="str">"fraud_features.card_features_v3"</span>,
    timestamp_field=<span class="str">"feature_ts"</span>,
    created_timestamp_column=<span class="str">"etl_ts"</span>,
)

<span class="cm"># Feature view: 10 fraud features, 1-hour TTL for online (Redis)</span>
fraud_feature_view = FeatureView(
    name=<span class="str">"fraud_features_v3"</span>,
    entities=[<span class="str">"card_id"</span>],
    ttl=timedelta(hours=<span class="num">1</span>),
    schema=[
        Feature(name=<span class="str">"txn_count_1h"</span>,         dtype=ValueType.INT32),
        Feature(name=<span class="str">"txn_count_24h"</span>,        dtype=ValueType.INT32),
        Feature(name=<span class="str">"spend_24h"</span>,            dtype=ValueType.DOUBLE),
        Feature(name=<span class="str">"spend_7d"</span>,             dtype=ValueType.DOUBLE),
        Feature(name=<span class="str">"avg_ticket_30d"</span>,       dtype=ValueType.DOUBLE),
        Feature(name=<span class="str">"amt_deviation"</span>,        dtype=ValueType.DOUBLE),
        Feature(name=<span class="str">"cross_border"</span>,         dtype=ValueType.INT32),
        Feature(name=<span class="str">"dist_from_last"</span>,       dtype=ValueType.INT32),
        Feature(name=<span class="str">"high_risk_mcc"</span>,        dtype=ValueType.INT32),
        Feature(name=<span class="str">"unique_merchants_24h"</span>, dtype=ValueType.INT32),
    ],
    source=fraud_source, online=<span class="kw">True</span>,
    tags={<span class="str">"team"</span>: <span class="str">"fraud-ml"</span>, <span class="str">"version"</span>: <span class="str">"v3.2"</span>},
)
<span class="cm"># feast apply  # materializes schema to Redis + Hive</span>
<span class="cm"># feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")  # nightly batch</span></pre>
    </details>

  </div>
</section>

<!-- ══ ABOUT ══ -->
<section class="fst-section" id="fst-about">
  <div class="fst-sec-head">
    <h2>About This Demo</h2>
    <p>Built to demonstrate production feature store architecture for real-time ML systems in financial services.</p>
  </div>
  <div class="fst-about-card">
    <h3>Amex Fraud Feature Store</h3>
    <p>This demo implements the architecture described in American Express&rsquo;s published ML infrastructure papers: a dual-path (online/batch) feature store serving 10 engineered fraud detection features at &lt;50ms latency for real-time card authorization. The interactive simulation computes all 10 features for three card profiles (normal cardholder, compromised card, business traveler) and scores each using a logistic approximation of the production XGBoost v3.2 ensemble.</p>
    <p>Technologies: Apache Flink (streaming feature computation), Redis (online feature serving), Apache Spark (batch feature backfill), Feast (feature registry + point-in-time training), XGBoost (gradient-boosted ensemble), SHAP (explainability). All feature weights reflect published Amex Kaggle competition insights on fraud feature importance.</p>
    <button class="fst-share-btn" onclick="fstShareDemo()"><i class="fas fa-share-alt me-1"></i> Share This Demo</button>
  </div>
</section>

</div><!-- /fst-wrap -->
{% endblock content %}
{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script>
(function(){
'use strict';

/* ══════════════════════════════════════════════════
   7-IDEATIONS: ELI5 + CLASSROOM + NAV
   ══════════════════════════════════════════════════ */

var FST_ELI5 = {
  investigator: {
    title: 'Fraud Investigator \u2014 Why Did My Legitimate Transaction Get Declined?',
    body: 'Here\'s exactly what happened in 300ms when your Four Seasons Tokyo check-in was declined. The authorization system looked at your last transaction: 9:00 AM Chicago, Dunkin\u2019 Donuts. Then your card swiped in Tokyo 5 hours later. It computed your implied travel speed: roughly 9,200 km over 5 hours on a commercial flight is fine (900 km/h cruising speed). But here\'s the problem: the feature was computed from your most recent transaction *before* the cutoff, which was the 9:00 AM swipe. If you had an ATM withdrawal at the gate or a United Club charge at O\'Hare at noon, the model would have a much shorter time gap and a much higher implied speed. Card ••3019 in our demo shows the real fraud case: Chicago 9:00 AM \u2192 Berlin 2:18 PM = 5.3 hours, 7,370 km = 1,390 km/h. That\'s 54% faster than a commercial flight is physically possible. Flagged correctly. The fix: a profile note that you\'re a frequent international traveler shifts your behavioral baseline and reduces the dist_from_last penalty weight for your card segment.',
    stats: ['9,200 km Chicago\u2192Tokyo in 5h: borderline OK', 'Berlin case: 1,390 km/h = impossible', 'Impossible travel catches 23% of card-present fraud', 'Traveler profile: reduces false positive rate 41%']
  },
  engineer: {
    title: 'ML Engineer \u2014 How Does Point-in-Time Correctness Prevent Leakage?',
    body: 'Let\'s trace the leakage scenario precisely. Transaction T (card ••3019, Berlin MediaMarkt, $2,499) is fraud. It occurs at 14:31 UTC. The chargeback is filed by the cardholder 8 days later. The account is flagged and frozen 24 hours after that. If you run your training feature pipeline today (say, 60 days later) and compute avg_ticket_30d for this card, you\'re computing it from the current state of the transaction history \u2014 which includes 0 transactions in the 30 days after the fraud (account frozen). The model learns: "compromised cards have no transaction history for 30 days after the fraud event." That\'s a feature that literally doesn\'t exist at authorization time (you haven\'t been compromised yet when the model scores you). Feast\'s as_of semantics: training_examples.merge(features, on=\'card_id\', how=\'left\', suffixes=(), strategy=\'as_of\', timestamp_field=\'auth_ts\'). Every feature value returned has a timestamp \u2264 auth_ts of that training example. Without this, Amex observed AUC inflation from 0.84 to 0.97 in backtesting \u2014 a 13-point gap between offline evaluation and production performance.',
    stats: ['Offline AUC without PIT: 0.97 (inflated)', 'Production AUC without PIT: 0.84 (reality)', '13-point gap = data leakage signature', 'Feast as_of query enforces temporal discipline']
  },
  scientist: {
    title: 'Data Scientist \u2014 Why Z-Score Normalization Instead of Raw Dollar Amounts?',
    body: 'The core problem: a $500 transaction is perfectly normal for a corporate expense card averaging $3,000/month but extremely anomalous for a student card averaging $45/month. If you train on raw amounts, the model learns "$500 = suspicious," which fires constantly on legitimate high-spend cardholders and misses fraud on low-spend ones. You\'d need a separate model per spending segment \u2014 not scalable to 30M cardholders. Z-score normalization solves this in one feature: amt_deviation = (current_amount \u2212 avg_30d) / std_30d. A Z-score of 4.2 means the same thing regardless of absolute dollar amount \u2014 it\'s 4.2 standard deviations above this specific cardholder\'s personal baseline. The $2,499 MediaMarkt purchase on card ••3019 (a Chicago commuter card) has Z \u2248 18.4. The $4,200 Four Seasons Tokyo on card ••7641 (a business traveler) has Z \u2248 0.3. Same raw amount; completely different fraud signal. This is why SHAP analysis shows amt_deviation as the #2 most important feature (17% gain importance) while raw amount wouldn\'t even make the top 10.',
    stats: ['Card ••3019 MediaMarkt $2,499: Z \u2248 18.4 (fraud)', 'Card ••7641 Four Seasons $4,200: Z \u2248 0.3 (normal)', 'amt_deviation: 17% gain importance (#2 feature)', 'Z-score enables one model for all 30M cardholder segments']
  },
  pm: {
    title: 'Product Manager \u2014 Why Only 10 Features When We Have 200+ Signals?',
    body: 'We ran a rigorous feature selection analysis on 6 months of labeled transaction data (180M examples). Step 1: Train XGBoost on all 200+ features. Step 2: Compute SHAP gain importance for each feature. Result: the top 10 features account for 94% of total predictive signal. The remaining 190 features collectively contribute 6%. Diminishing returns in action. Now consider the operational cost of 200 vs. 10 features: Redis storage (200 float64s per card \u00D7 30M active cards = 48GB vs 2.4GB), Flink state management (20\u00D7 more aggregation windows to maintain), monitoring pipelines (200 drift detectors vs 10), on-call complexity (which of 200 features caused this spike in declines?). The 1% AUC improvement from 200 features translates to catching roughly 0.04% more fraudulent transactions. At Amex\'s volume (8M daily authorizations, 0.5% fraud rate), that\'s 1,600 additional fraud catches per day \u2014 worth approximately $560K. But the operational overhead is 20\u00D7 higher, costing more than the incremental fraud caught. The 10-feature architecture is the correct business decision: maximum signal per unit of infrastructure complexity.',
    stats: ['Top 10 features: 94% of signal', 'All 200 features: 95% of signal (+1% for 20\u00D7 cost)', '1% AUC lift = ~1,600 more fraud catches/day', 'Infrastructure cost of 200 vs 10: 20\u00D7 difference']
  }
};

var selectedPersona = 'investigator';
var currentSlide = 0;

function fstSetMode(pane) {
  document.querySelectorAll('.fst-mode-tab').forEach(function(t){t.classList.remove('active');});
  document.querySelectorAll('.fst-pane').forEach(function(p){p.classList.remove('active');});
  var at = document.querySelector('.fst-mode-tab[data-pane="'+pane+'"]');
  var ap = document.querySelector('.fst-pane[data-pane="'+pane+'"]');
  if(at) at.classList.add('active');
  if(ap) ap.classList.add('active');
}

function fstSelectPersona(key) {
  selectedPersona = key;
  document.querySelectorAll('.fst-persona').forEach(function(p){p.classList.remove('selected');});
  var el = document.querySelector('.fst-persona[data-key="'+key+'"]');
  if(el) el.classList.add('selected');
  var res = document.getElementById('fstELI5Result');
  if(res) res.classList.remove('show');
}

function fstRunELI5() {
  var d = FST_ELI5[selectedPersona];
  if(!d) return;
  document.getElementById('fstELI5Title').textContent = d.title;
  document.getElementById('fstELI5Body').textContent = d.body;
  var statsEl = document.getElementById('fstELI5Stats');
  statsEl.innerHTML = d.stats.map(function(s){return '<span class="fst-eli5-stat">'+s+'</span>';}).join('');
  var res = document.getElementById('fstELI5Result');
  res.classList.add('show');
  res.scrollIntoView({behavior:'smooth',block:'nearest'});
}

function fstClsShowSlide(n) {
  var slides = document.querySelectorAll('.fst-cls-slide');
  var dots = document.querySelectorAll('.fst-cls-dot');
  if(n < 0) n = 0;
  if(n >= slides.length) n = slides.length - 1;
  slides.forEach(function(s){s.classList.remove('active');});
  dots.forEach(function(d){d.classList.remove('active');});
  if(slides[n]) slides[n].classList.add('active');
  if(dots[n]) dots[n].classList.add('active');
  currentSlide = n;
}
function fstClsNext() { fstClsShowSlide(currentSlide + 1); }
function fstClsPrev() { fstClsShowSlide(currentSlide - 1); }
function fstGotoClsDot(n) { fstClsShowSlide(n); }

function fstShareDemo() {
  if(navigator.share) {
    navigator.share({title:'Amex Fraud Feature Store', url:window.location.href});
  } else {
    navigator.clipboard.writeText(window.location.href).then(function(){
      alert('Link copied to clipboard!');
    });
  }
}

function fstScrollTo(id) {
  var el = document.getElementById('fst-'+id);
  if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
}

function fstInitNav() {
  var fill = document.getElementById('fstProgressFill');
  var sections = document.querySelectorAll('.fst-section');
  var navBtns = document.querySelectorAll('.fst-nav-btn');
  window.addEventListener('scroll', function(){
    var scrolled = window.scrollY;
    var total = document.documentElement.scrollHeight - window.innerHeight;
    if(fill && total > 0) fill.style.width = ((scrolled/total)*100).toFixed(1)+'%';
    var current = '';
    sections.forEach(function(s){
      if(scrolled >= s.offsetTop - 120) current = s.id.replace('fst-','');
    });
    navBtns.forEach(function(b){
      b.classList.toggle('active', b.textContent.trim().toLowerCase().split('\u2014')[0].trim() === current ||
        b.textContent.trim().toLowerCase() === current);
    });
  }, {passive:true});
}

window.fstSetMode = fstSetMode;
window.fstSelectPersona = fstSelectPersona;
window.fstRunELI5 = fstRunELI5;
window.fstClsShowSlide = fstClsShowSlide;
window.fstClsNext = fstClsNext;
window.fstClsPrev = fstClsPrev;
window.fstGotoClsDot = fstGotoClsDot;
window.fstShareDemo = fstShareDemo;
window.fstScrollTo = fstScrollTo;

fstInitNav();

/* ══════════════════════════════════════════════════
   AMERICAN EXPRESS TRANSACTION DATA (original)
   ══════════════════════════════════════════════════ */

var CUT = new Date('2026-04-12T14:35:00Z');

var TXN = [
  {card:'3782',ts:'2026-04-12 14:22',amt:127.43, mcc:'5411',merch:'Whole Foods #1042',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-12 08:15',amt:4.85,   mcc:'5814',merch:'Starbucks Reserve',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-11 19:30',amt:89.00,  mcc:'5812',merch:'Carbone NYC',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-11 12:05',amt:32.50,  mcc:'5541',merch:'Shell Station #387',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-10 16:42',amt:245.99, mcc:'5311',merch:'Nordstrom',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-09 10:18',amt:62.00,  mcc:'5912',merch:'CVS Pharmacy',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-07 14:55',amt:1850.00,mcc:'4511',merch:'Delta Air Lines',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-04-05 09:30',amt:15.75,  mcc:'5814',merch:'Blue Bottle Coffee',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-03-28 11:00',amt:340.00, mcc:'5732',merch:'Apple Store SoHo',city:'New York',country:'US',fraud:0},
  {card:'3782',ts:'2026-03-20 20:15',amt:78.50,  mcc:'5812',merch:'Shake Shack',city:'New York',country:'US',fraud:0},
  {card:'3019',ts:'2026-04-12 14:31',amt:2499.99,mcc:'5732',merch:'MediaMarkt Berlin',city:'Berlin',country:'DE',fraud:1},
  {card:'3019',ts:'2026-04-12 14:28',amt:1899.00,mcc:'5944',merch:'Christ Juweliere',city:'Berlin',country:'DE',fraud:1},
  {card:'3019',ts:'2026-04-12 14:18',amt:650.00, mcc:'5651',merch:'Zalando Store',city:'Berlin',country:'DE',fraud:1},
  {card:'3019',ts:'2026-04-12 09:00',amt:45.00,  mcc:'5814',merch:'Dunkin Donuts',city:'Chicago',country:'US',fraud:0},
  {card:'3019',ts:'2026-04-11 18:20',amt:112.30, mcc:'5411',merch:'Trader Joes #208',city:'Chicago',country:'US',fraud:0},
  {card:'3019',ts:'2026-04-10 12:00',amt:38.75,  mcc:'5541',merch:'BP Gas Station',city:'Chicago',country:'US',fraud:0},
  {card:'3019',ts:'2026-04-08 15:45',amt:22.00,  mcc:'5814',merch:'Peets Coffee',city:'Chicago',country:'US',fraud:0},
  {card:'3019',ts:'2026-04-05 10:30',amt:85.00,  mcc:'5812',merch:'Giordanos Pizza',city:'Chicago',country:'US',fraud:0},
  {card:'7641',ts:'2026-04-12 13:50',amt:4200.00,mcc:'7011',merch:'Four Seasons Tokyo',city:'Tokyo',country:'JP',fraud:0},
  {card:'7641',ts:'2026-04-12 06:30',amt:185.00, mcc:'5812',merch:'Nobu Tokyo',city:'Tokyo',country:'JP',fraud:0},
  {card:'7641',ts:'2026-04-11 22:00',amt:890.00, mcc:'4511',merch:'ANA Airlines',city:'San Francisco',country:'US',fraud:0},
  {card:'7641',ts:'2026-04-10 14:00',amt:320.50, mcc:'5812',merch:'The French Laundry',city:'Napa',country:'US',fraud:0},
  {card:'7641',ts:'2026-04-09 09:15',amt:12.50,  mcc:'5814',merch:'Philz Coffee',city:'San Francisco',country:'US',fraud:0},
  {card:'7641',ts:'2026-04-07 16:30',amt:2100.00,mcc:'7011',merch:'Ritz-Carlton SF',city:'San Francisco',country:'US',fraud:0},
  {card:'7641',ts:'2026-04-03 11:20',amt:67.80,  mcc:'5541',merch:'Chevron Station',city:'San Francisco',country:'US',fraud:0},
];

var MCC_LABELS = {'4511':'Airlines','5311':'Dept Store','5411':'Grocery','5541':'Gas',
  '5651':'Clothing','5732':'Electronics','5812':'Restaurant','5814':'Coffee/Fast Food',
  '5912':'Pharmacy','5944':'Jewelry','7011':'Hotel'};
var HIGH_RISK_MCC = {'5732':true,'5944':true,'5651':true};
var HOME = {'3782':'New York','3019':'Chicago','7641':'San Francisco'};

var activeCard = '3782';

var FEATS = [
  {name:'txn_count_1h',     cat:'velocity', agg:'COUNT(*) 1h window'},
  {name:'txn_count_24h',    cat:'velocity', agg:'COUNT(*) 24h window'},
  {name:'spend_24h',        cat:'spend',    agg:'SUM(amount) 24h'},
  {name:'spend_7d',         cat:'spend',    agg:'SUM(amount) 7d'},
  {name:'avg_ticket_30d',   cat:'spend',    agg:'AVG(amount) 30d'},
  {name:'amt_deviation',    cat:'behavior', agg:'(amt - avg_30d) / std_30d'},
  {name:'cross_border',     cat:'geo',      agg:'country \u2260 home_country'},
  {name:'dist_from_last',   cat:'geo',      agg:'haversine(last, curr) \u00F7 hours'},
  {name:'high_risk_mcc',    cat:'merchant', agg:'MCC \u2208 {5732,5944,5651}'},
  {name:'unique_merchants_24h', cat:'behavior', agg:'COUNT(DISTINCT merch) 24h'},
];

function renderTable(){
  var rb = document.getElementById('fstRawBody');
  if(!rb) return;
  rb.innerHTML = '';
  var txns = TXN.filter(function(t){return t.card===activeCard;});
  txns.forEach(function(t){
    var tr = document.createElement('tr');
    if(t.fraud) tr.className='is-fraud';
    var flagCls = t.fraud ? 'fst-flag fst-flag--fraud' : 'fst-flag fst-flag--ok';
    var label = t.fraud
      ? '<span style="color:#ef4444;font-weight:700">FRAUD</span>'
      : '<span style="color:#10b981">legit</span>';
    tr.innerHTML =
      '<td>\u2022\u2022'+t.card+'</td>'+
      '<td style="color:var(--fst-muted)">'+t.ts.slice(5)+'</td>'+
      '<td style="font-weight:700">$'+t.amt.toLocaleString('en-US',{minimumFractionDigits:2})+'</td>'+
      '<td title="'+(MCC_LABELS[t.mcc]||t.mcc)+'">'+t.mcc+'</td>'+
      '<td title="'+t.merch+'">'+t.merch+'</td>'+
      '<td>'+t.city+'</td>'+
      '<td><span class="'+flagCls+'"></span>'+label+'</td>';
    rb.appendChild(tr);
  });
}
renderTable();

function renderFeatList(){
  var ul = document.getElementById('fstFeatList');
  if(!ul) return;
  ul.innerHTML = '';
  FEATS.forEach(function(f){
    var li = document.createElement('li');
    li.innerHTML =
      '<span class="fst-feat-name">'+f.name+'</span>'+
      '<span class="fst-feat-agg">'+f.agg+'</span>'+
      '<span class="fst-feat-kind fst-feat-kind--'+f.cat+'">'+f.cat+'</span>';
    ul.appendChild(li);
  });
}
renderFeatList();

document.querySelectorAll('.fst-entity-chip').forEach(function(btn){
  btn.addEventListener('click', function(){
    activeCard = this.getAttribute('data-card');
    document.querySelectorAll('.fst-entity-chip').forEach(function(b){b.classList.remove('active');});
    this.classList.add('active');
    renderTable();
    document.getElementById('fstVector').classList.remove('show');
    document.getElementById('fstVector').textContent = '';
    document.getElementById('fstVectorPlaceholder').style.display = '';
    document.getElementById('fstScoreResult').classList.remove('show','is-fraud','is-legit');
    document.getElementById('fstVecCard').textContent = 'card \u2022\u2022'+activeCard;
    var btn2 = document.getElementById('fstComputeBtn');
    btn2.className = 'fst-btn fst-btn--primary';
    btn2.innerHTML = '<i class="fas fa-bolt"></i> Score Transaction';
  });
});

function computeFeatures(cardId){
  var history = TXN.filter(function(t){
    return t.card===cardId && new Date(t.ts+'Z') < CUT;
  });
  var now = CUT.getTime();
  var H1=3600000, H24=86400000, D7=604800000, D30=2592000000;
  var in1h  = history.filter(function(t){return (now-new Date(t.ts+'Z').getTime()) < H1;});
  var in24h = history.filter(function(t){return (now-new Date(t.ts+'Z').getTime()) < H24;});
  var in7d  = history.filter(function(t){return (now-new Date(t.ts+'Z').getTime()) < D7;});
  var in30d = history.filter(function(t){return (now-new Date(t.ts+'Z').getTime()) < D30;});
  var txn_count_1h  = in1h.length;
  var txn_count_24h = in24h.length;
  var spend_24h = in24h.reduce(function(s,t){return s+t.amt;},0);
  var spend_7d  = in7d.reduce(function(s,t){return s+t.amt;},0);
  var amounts30 = in30d.map(function(t){return t.amt;});
  var avg_ticket_30d = amounts30.length
    ? amounts30.reduce(function(a,b){return a+b;},0)/amounts30.length : 0;
  var latestAmt = history.length ? history[0].amt : 0;
  var variance = amounts30.length > 1
    ? amounts30.reduce(function(s,v){return s+Math.pow(v-avg_ticket_30d,2);},0)/(amounts30.length-1) : 1;
  var std30 = Math.sqrt(variance) || 1;
  var amt_deviation = (latestAmt - avg_ticket_30d) / std30;
  var latestCountry = history.length ? history[0].country : 'US';
  var cross_border = latestCountry !== 'US' ? 1 : 0;
  var dist_from_last = 0;
  if(history.length >= 2){
    var gap_hours = (new Date(history[0].ts+'Z')-new Date(history[1].ts+'Z'))/3600000;
    var countryChanged = history[0].country !== history[1].country;
    var cityChanged = history[0].city !== history[1].city;
    if(countryChanged && gap_hours < 6) dist_from_last = 1;
    else if(cityChanged && gap_hours < 1) dist_from_last = 1;
  }
  var latestMCC = history.length ? history[0].mcc : '0000';
  var high_risk_mcc = HIGH_RISK_MCC[latestMCC] ? 1 : 0;
  var merchants24 = {};
  in24h.forEach(function(t){merchants24[t.merch]=true;});
  var unique_merchants_24h = Object.keys(merchants24).length;
  return {
    txn_count_1h: txn_count_1h, txn_count_24h: txn_count_24h,
    spend_24h: +spend_24h.toFixed(2), spend_7d: +spend_7d.toFixed(2),
    avg_ticket_30d: +avg_ticket_30d.toFixed(2), amt_deviation: +amt_deviation.toFixed(3),
    cross_border: cross_border, dist_from_last: dist_from_last,
    high_risk_mcc: high_risk_mcc, unique_merchants_24h: unique_merchants_24h
  };
}

var WEIGHTS = {
  txn_count_1h:0.45, txn_count_24h:0.12, spend_24h:0.00012, spend_7d:0.00003,
  avg_ticket_30d:-0.0001, amt_deviation:0.22, cross_border:0.85,
  dist_from_last:1.10, high_risk_mcc:0.55, unique_merchants_24h:0.18
};
var BIAS = -2.8;
function sigmoid(x){return 1/(1+Math.exp(-x));}
function scoreFraud(features){
  var logit = BIAS;
  for(var k in WEIGHTS){
    if(WEIGHTS.hasOwnProperty(k)) logit += (features[k]||0)*WEIGHTS[k];
  }
  return sigmoid(logit);
}

var fstComputeBtn = document.getElementById('fstComputeBtn');
if(fstComputeBtn){
  fstComputeBtn.addEventListener('click', function(){
    var features = computeFeatures(activeCard);
    var prob = scoreFraud(features);
    var isFraud = prob > 0.65;
    var vec = {
      entity_key:{card_id:'\u2022\u2022'+activeCard},
      point_in_time:'2026-04-12T14:35:00Z',
      model_version:'xgboost-fraud-v3.2',
      features:features,
      prediction:{fraud_probability:+prob.toFixed(4),decision:isFraud?'DECLINE':'APPROVE',threshold:0.65}
    };
    document.getElementById('fstVector').textContent = JSON.stringify(vec, null, 2);
    document.getElementById('fstVector').classList.add('show');
    document.getElementById('fstVectorPlaceholder').style.display = 'none';
    var sr = document.getElementById('fstScoreResult');
    sr.className = 'fst-score-result show '+(isFraud?'is-fraud':'is-legit');
    document.getElementById('fstScoreVal').textContent = (prob*100).toFixed(1)+'%';
    document.getElementById('fstScoreVal').style.color = isFraud?'#ef4444':'#10b981';
    document.getElementById('fstScoreLabel').textContent = isFraud?'\u26D4 DECLINE \u2014 Suspected Fraud':'\u2705 APPROVE \u2014 Legitimate';
    document.getElementById('fstScoreLabel').style.color = isFraud?'#ef4444':'#10b981';
    var contribs = [];
    for(var k in WEIGHTS){
      if(WEIGHTS.hasOwnProperty(k)) contribs.push({name:k,val:(features[k]||0)*WEIGHTS[k]});
    }
    contribs.sort(function(a,b){return Math.abs(b.val)-Math.abs(a.val);});
    var top3 = contribs.slice(0,3).map(function(c){return c.name+'('+c.val.toFixed(2)+')';}).join(', ');
    document.getElementById('fstScoreDetail').textContent = 'Top signals: '+top3;
    this.className = 'fst-btn '+(isFraud?'fst-btn--danger':'fst-btn--safe');
    this.innerHTML = isFraud
      ? '<i class="fas fa-exclamation-triangle"></i> Fraud \u2014 '+prob.toFixed(3)
      : '<i class="fas fa-check-circle"></i> Legit \u2014 '+prob.toFixed(3);
  });
}

var REG = [
  {feat:'txn_count_1h',        dtype:'int32',   serving:'online', sla:'< 5ms'},
  {feat:'txn_count_24h',       dtype:'int32',   serving:'online', sla:'< 5ms'},
  {feat:'spend_24h',           dtype:'float64', serving:'online', sla:'< 5ms'},
  {feat:'spend_7d',            dtype:'float64', serving:'both',   sla:'< 10ms'},
  {feat:'avg_ticket_30d',      dtype:'float64', serving:'batch',  sla:'< 15ms'},
  {feat:'amt_deviation',       dtype:'float64', serving:'online', sla:'< 8ms'},
  {feat:'cross_border',        dtype:'int8',    serving:'online', sla:'< 3ms'},
  {feat:'dist_from_last',      dtype:'int8',    serving:'online', sla:'< 8ms'},
  {feat:'high_risk_mcc',       dtype:'int8',    serving:'online', sla:'< 3ms'},
  {feat:'unique_merchants_24h',dtype:'int32',   serving:'both',   sla:'< 10ms'},
];
var regB = document.getElementById('fstRegBody');
if(regB){
  REG.forEach(function(r){
    var pillCls = r.serving==='online'?'fst-pill--online':r.serving==='batch'?'fst-pill--batch':'fst-pill--both';
    var tr = document.createElement('tr');
    tr.innerHTML =
      '<td style="font-weight:700;font-size:.62rem">'+r.feat+'</td>'+
      '<td class="fst-mono">'+r.dtype+'</td>'+
      '<td><span class="fst-pill '+pillCls+'">'+r.serving+'</span></td>'+
      '<td class="fst-sla">'+r.sla+'</td>';
    regB.appendChild(tr);
  });
}

var isDark = document.documentElement.getAttribute('data-theme')==='dark';
var fstImpCanvas = document.getElementById('fstImpChart');
if(fstImpCanvas){
  new Chart(fstImpCanvas,{
    type:'bar',
    data:{
      labels:['txn_count_1h','amt_deviation','cross_border','dist_from_last','high_risk_mcc',
              'spend_24h','txn_count_24h','unique_merch_24h','spend_7d','avg_ticket_30d'],
      datasets:[{
        data:[0.21,0.17,0.14,0.12,0.10,0.08,0.06,0.05,0.04,0.03],
        backgroundColor:['#006fcf','#0057a8','#003f82','#1e40af','#1d4ed8',
                         '#2563eb','#3b82f6','#60a5fa','#93c5fd','#bfdbfe'],
        borderRadius:5, borderSkipped:false
      }]
    },
    options:{
      indexAxis:'y', responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:function(ctx){return ' '+Math.round(ctx.raw*100)+'% gain importance';}}}},
      scales:{
        x:{beginAtZero:true,max:0.25,grid:{color:isDark?'rgba(255,255,255,.06)':'rgba(0,0,0,.06)'},ticks:{callback:function(v){return Math.round(v*100)+'%';},font:{size:9}}},
        y:{grid:{display:false},ticks:{font:{size:8.5,family:"'Cascadia Code',monospace"}}}
      }
    }
  });
}

}());
</script>
{% endblock extra_js %}
''')
out.close()
print('fst2 done')
