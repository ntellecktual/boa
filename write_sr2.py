"""write_sr2.py — schema_registry.html 7-ideations (part 2/2, append)"""
TMPL = r'boaapp/templates/boaapp/schema_registry.html'
out = open(TMPL, 'a', encoding='utf-8')
out.write(r'''
<!-- ══ CLASSROOM ══ -->
<section class="sreg-section" id="sreg-classroom">
  <div class="sreg-sec-head">
    <h2>Classroom</h2>
    <p>Six concepts from event serialization basics to transitive compatibility graphs &#8212; building from fundamentals to advanced production patterns.</p>
  </div>
  <div class="sreg-cls-wrap">
    <div class="sreg-cls-track">
      <div class="sreg-cls-slide active" data-slide="0">
        <div class="sreg-cls-num">Slide 1 of 6</div>
        <h3>Why Schema Evolution Matters in Event Streaming</h3>
        <p>In a monolithic application, changing a data structure is a single deployment. In an event-driven microservices architecture, the producer and every consumer deploy independently. A field renamed in the producer breaks every consumer that references the old name &#8212; and there may be 15 consumers you don&#39;t know about.</p>
        <p>Kafka retains messages for days or weeks (or indefinitely in compacted topics). Consumers restart and replay old messages. Even if all consumers are updated simultaneously, replaying old events against new code will fail unless the schema change is backward-compatible. Schema evolution isn&#39;t just a deployment concern &#8212; it&#39;s a data durability concern.</p>
        <div class="sreg-cls-formula">Problem: Producer changes schema &#8594; Consumer crashes on old messages &#8594; Entire Kafka lag backlog must be replayed</div>
      </div>
      <div class="sreg-cls-slide" data-slide="1">
        <div class="sreg-cls-num">Slide 2 of 6</div>
        <h3>Avro vs. Protobuf vs. JSON Schema</h3>
        <p>Three serialization formats, three tradeoffs. <strong>JSON Schema</strong>: human readable, easy to debug, largest payload. No support for union types or schema evolution semantics. Best for REST APIs where developer experience matters more than throughput.</p>
        <p><strong>Protobuf</strong>: smallest payload, fastest serialization, strongly typed. Schema evolution via field number stability &#8212; don&#39;t reuse field numbers. Requires recompilation when schemas change. Best for gRPC inter-service communication. <strong>Avro</strong>: medium payload, schema stored separately from data (in registry), runtime schema resolution without recompile. The native choice for Kafka because the registry integration is first-class. Best for high-cardinality event streams with frequent schema evolution.</p>
        <div class="sreg-cls-formula">Kafka + Avro + Schema Registry = producer stores schema ID (4 bytes) in message header &#8594; consumer fetches schema by ID</div>
      </div>
      <div class="sreg-cls-slide" data-slide="2">
        <div class="sreg-cls-num">Slide 3 of 6</div>
        <h3>Backward Compatibility Deep Dive</h3>
        <p>Backward compatibility answers: <em>can a new consumer version read messages written by an old producer version?</em> This is the most important property for rolling deployments where consumers update before producers (or independently).</p>
        <p>Rules for backward-compatible changes: (1) You may add new fields IF they have a default value. Old messages won&#39;t have the field &#8212; the default fills in. (2) You may remove fields that had a default. Old messages that include the field &#8212; it gets ignored. Forbidden: removing required fields (no default), changing field types, renaming fields (Avro has no rename concept &#8212; it&#39;s a delete + add, which breaks).</p>
        <div class="sreg-cls-formula">Safe: add field with default &#8594; Breaks: remove required field &#8594; Breaks: rename field (delete+add) &#8594; Breaks: type change</div>
      </div>
      <div class="sreg-cls-slide" data-slide="3">
        <div class="sreg-cls-num">Slide 4 of 6</div>
        <h3>Forward Compatibility &#8212; When Producers Upgrade First</h3>
        <p>Forward compatibility answers: <em>can an old consumer version read messages written by a new producer?</em> This scenario occurs when the producer deploys first (canary) and old consumers are still running. The old consumer must be able to parse the new message format.</p>
        <p>Forward-compatible rules mirror backward: new fields must have defaults (so old consumers can ignore them), removed fields must have had defaults (old consumers that reference them get the default). The critical difference from backward: in forward mode, the consumer is the "old" code reading "new" data. You need defaults on the producer side (new schema) so old readers can skip unknown fields.</p>
        <div class="sreg-cls-formula">FORWARD = old consumer + new producer data &#8594; BACKWARD = new consumer + old producer data &#8594; FULL = both simultaneously</div>
      </div>
      <div class="sreg-cls-slide" data-slide="4">
        <div class="sreg-cls-num">Slide 5 of 6</div>
        <h3>Full Compatibility for Financial Event Replay</h3>
        <p>FULL compatibility is the intersection of BACKWARD and FULL &#8212; the most restrictive mode. You can only add optional fields with defaults, and only remove fields that already had defaults. No type changes, no renames, no removing required fields. Ever.</p>
        <p>The financial services use case makes this mandatory: MiFID II, SOX, and Dodd-Frank require 7-year retention and replay of transaction events. A compliance team might replay 5-year-old payment events against today&#39;s fraud models. FULL compatibility guarantees that any consumer version &#8212; from 2019 or 2026 &#8212; can deserialize any message in the topic, regardless of when it was produced. Without FULL compatibility, some version combinations will silently corrupt or crash.</p>
        <div class="sreg-cls-formula">MiFID II: 7-year replay &#8594; FULL compatibility required &#8594; only additive changes with defaults &#8594; no field removal, no type changes</div>
      </div>
      <div class="sreg-cls-slide" data-slide="5">
        <div class="sreg-cls-num">Slide 6 of 6</div>
        <h3>Transitive Compatibility Graphs</h3>
        <p>Standard registry implementations check compatibility only between adjacent versions: v3 vs v4, v4 vs v5. This misses a dangerous edge case: v1&#8594;v3 may be compatible, v3&#8594;v5 may be compatible, but v1&#8594;v5 may NOT be compatible. This happens when a field was removed in v3 with a default, then the default value was changed in v5.</p>
        <p>The fix: build a full pairwise compatibility graph across all registered versions. This is computationally expensive &#8212; O(n&#178;) version checks &#8212; but critical for long-lived topics with many versions. Practical optimization: check compatibility against the earliest version still in the topic retention window, plus all currently active consumer versions (from consumer group lag metrics).</p>
        <div class="sreg-cls-formula">Graph check: check_compat(v1, v_new) &#8594; check_compat(v2, v_new) &#8594; ... &#8594; check_compat(v_latest, v_new) &#8594; all must pass</div>
      </div>
    </div>
    <div class="sreg-cls-nav">
      <button class="sreg-cls-nav-btn" onclick="sregClsPrev()">&#8592; Prev</button>
      <div class="sreg-cls-dots" id="sregClsDots">
        <div class="sreg-cls-dot active" onclick="sregGotoClsDot(0)"></div>
        <div class="sreg-cls-dot" onclick="sregGotoClsDot(1)"></div>
        <div class="sreg-cls-dot" onclick="sregGotoClsDot(2)"></div>
        <div class="sreg-cls-dot" onclick="sregGotoClsDot(3)"></div>
        <div class="sreg-cls-dot" onclick="sregGotoClsDot(4)"></div>
        <div class="sreg-cls-dot" onclick="sregGotoClsDot(5)"></div>
      </div>
      <button class="sreg-cls-nav-btn" onclick="sregClsNext()">Next &#8594;</button>
    </div>
  </div>
</section>

<!-- ══ KEY POINTS ══ -->
<section class="sreg-section" id="sreg-keypoints">
  <div class="sreg-sec-head">
    <h2>Key Engineering Points</h2>
    <p>Four architectural decisions that determine whether schema governance actually works in production.</p>
  </div>
  <div class="sreg-kp-grid">
    <div class="sreg-kp">
      <div class="sreg-kp-icon">&#x26D4;</div>
      <h4>Registry as a CI/CD Gate</h4>
      <p>The most impactful deployment: add schema compatibility check as a required step in the CI/CD pipeline. Before any producer deploys, the pipeline runs <code>test_compatibility()</code> against the registry. If it fails, the build fails. This moves the detection from runtime (production crash) to build time &#8212; a 100x improvement in the cost of catching the defect.</p>
    </div>
    <div class="sreg-kp">
      <div class="sreg-kp-icon">&#x1F9F5;</div>
      <h4>Avro Union Types Enable Gradual Migration</h4>
      <p>When a field type must change, the Avro union type enables gradual migration: change the type from <code>string</code> to <code>["null", "string", "int"]</code>. Producers write both the old and new format. Consumers handle all three variants. After all consumers migrate, the producer removes the old variant. This makes what would be a BREAKING change into a three-phase SAFE migration.</p>
    </div>
    <div class="sreg-kp">
      <div class="sreg-kp-icon">&#x1F480;</div>
      <h4>Dead Field Detection Prevents Schema Bloat</h4>
      <p>After 3 years of schema evolution, topics accumulate fields that no consumer reads. These "dead fields" waste serialization bandwidth and confuse new developers. Correlate Avro deserializer field access patterns with consumer group activity: a field with zero reads in 90 days, from any active consumer, is a dead field. MAJOR version cleanup removes them with a coordinated deprecation cycle.</p>
    </div>
    <div class="sreg-kp">
      <div class="sreg-kp-icon">&#x1F4CA;</div>
      <h4>Schema ID in Message Header, Not Payload</h4>
      <p>The Confluent wire format prepends a 5-byte magic byte + schema ID to every Avro message. Consumers use this ID to fetch the writer schema from the registry, then apply it against their local reader schema for field resolution. This means schema metadata costs only 5 bytes per message (not the full JSON schema), and the registry caches frequently-used schemas in the consumer.</p>
    </div>
  </div>
</section>

<!-- ══ CODE ══ -->
<section class="sreg-section" id="sreg-code">
  <div class="sreg-sec-head">
    <h2>Production Code</h2>
    <p>Four patterns: registry client integration, compatibility checking, canary migration orchestration, and the transitive compatibility graph.</p>
  </div>
  <div class="sreg-code-blocks">
    <details class="sreg-code-block">
      <summary><i class="fas fa-server" style="color:var(--sreg-accent)"></i>&nbsp;Confluent Schema Registry Client (Python)</summary>
      <pre><code><span class="kw">from</span> confluent_kafka.schema_registry <span class="kw">import</span> SchemaRegistryClient, Schema
<span class="kw">import</span> json, logging

logger = logging.getLogger(<span class="str">"schema_registry"</span>)

<span class="kw">class</span> <span class="fn">SchemaManager</span>:
    <span class="cm">"""Manages Avro schema lifecycle against Confluent Schema Registry."""</span>

    <span class="kw">def</span> <span class="fn">__init__</span>(self, registry_url: str, auth: tuple = None):
        conf = {<span class="str">'url'</span>: registry_url}
        <span class="kw">if</span> auth:
            conf[<span class="str">'basic.auth.user.info'</span>] = f<span class="str">"{auth[0]}:{auth[1]}"</span>
        self.client = SchemaRegistryClient(conf)

    <span class="kw">def</span> <span class="fn">register_with_compat_check</span>(self, subject: str, schema_str: str) -> int:
        <span class="cm">"""Register schema only if it passes compatibility check."""</span>
        schema = Schema(schema_str, <span class="str">'AVRO'</span>)
        <span class="kw">try</span>:
            is_compat = self.client.test_compatibility(subject, schema)
            <span class="kw">if not</span> is_compat:
                <span class="kw">raise</span> <span class="fn">ValueError</span>(f<span class="str">"Schema breaks {subject} compatibility"</span>)
        <span class="kw">except</span> Exception <span class="kw">as</span> e:
            <span class="kw">if</span> <span class="str">'40401'</span> <span class="kw">not in</span> str(e):  <span class="cm"># First schema — no prior version</span>
                <span class="kw">raise</span>
        schema_id = self.client.register_schema(subject, schema)
        logger.info(f<span class="str">"Registered {subject} id={schema_id}"</span>)
        <span class="kw">return</span> schema_id

    <span class="kw">def</span> <span class="fn">set_compatibility</span>(self, subject: str, level: str = <span class="str">'BACKWARD'</span>):
        <span class="cm">"""BACKWARD | FORWARD | FULL | NONE — subject-level override."""</span>
        self.client.set_compatibility(subject, level)

    <span class="kw">def</span> <span class="fn">get_all_versions</span>(self, subject: str) -> list[dict]:
        versions = self.client.get_versions(subject)
        <span class="kw">return</span> [json.loads(self.client.get_version(subject, v).schema.schema_str)
                <span class="kw">for</span> v <span class="kw">in</span> versions]</code></pre>
    </details>
    <details class="sreg-code-block">
      <summary><i class="fas fa-shield-halved" style="color:var(--sreg-accent)"></i>&nbsp;Schema Compatibility Checker (Python)</summary>
      <pre><code><span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass
<span class="kw">from</span> typing <span class="kw">import</span> List

@dataclass
<span class="kw">class</span> <span class="fn">CompatIssue</span>:
    field: str; issue_type: str; message: str; breaking: bool = <span class="kw">True</span>

<span class="kw">def</span> <span class="fn">check_backward</span>(writer: dict, reader: dict) -> List[CompatIssue]:
    <span class="cm">"""New reader can read old writer data?"""</span>
    issues = []
    r_fields = {f[<span class="str">'name'</span>]: f <span class="kw">for</span> f <span class="kw">in</span> reader[<span class="str">'fields'</span>]}
    w_fields = {f[<span class="str">'name'</span>]: f <span class="kw">for</span> f <span class="kw">in</span> writer[<span class="str">'fields'</span>]}
    <span class="kw">for</span> name, wf <span class="kw">in</span> w_fields.items():
        <span class="kw">if</span> name <span class="kw">not in</span> r_fields:
            issues.append(<span class="fn">CompatIssue</span>(name, <span class="str">'REMOVED'</span>,
                f<span class="str">'{name} in writer but missing from reader'</span>))
        <span class="kw">elif not</span> _types_compat(wf[<span class="str">'type'</span>], r_fields[name][<span class="str">'type'</span>]):
            issues.append(<span class="fn">CompatIssue</span>(name, <span class="str">'TYPE_CHANGED'</span>,
                f<span class="str">'{name}: {wf["type"]} -> {r_fields[name]["type"]}'</span>))
    <span class="kw">for</span> name, rf <span class="kw">in</span> r_fields.items():
        <span class="kw">if</span> name <span class="kw">not in</span> w_fields <span class="kw">and</span> <span class="str">'default'</span> <span class="kw">not in</span> rf:
            issues.append(<span class="fn">CompatIssue</span>(name, <span class="str">'MISSING_DEFAULT'</span>,
                f<span class="str">'New field {name} has no default (breaks old data)'</span>))
    <span class="kw">return</span> issues

<span class="kw">def</span> <span class="fn">check_full</span>(writer: dict, reader: dict) -> List[CompatIssue]:
    <span class="cm">"""Full: backward + forward combined."""</span>
    <span class="kw">return</span> <span class="fn">check_backward</span>(writer, reader) + <span class="fn">check_backward</span>(reader, writer)

<span class="kw">def</span> <span class="fn">_types_compat</span>(t1, t2) -> bool:
    <span class="kw">if</span> t1 == t2: <span class="kw">return True</span>
    <span class="kw">if</span> isinstance(t1, list) <span class="kw">and</span> t2 <span class="kw">in</span> t1: <span class="kw">return True</span>
    <span class="kw">if</span> isinstance(t2, list) <span class="kw">and</span> t1 <span class="kw">in</span> t2: <span class="kw">return True</span>
    <span class="kw">return False</span></code></pre>
    </details>
    <details class="sreg-code-block">
      <summary><i class="fas fa-rocket" style="color:var(--sreg-accent)"></i>&nbsp;Canary Migration Orchestrator (Python)</summary>
      <pre><code><span class="kw">import</span> time, logging
<span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass

logger = logging.getLogger(<span class="str">"migration"</span>)

@dataclass
<span class="kw">class</span> <span class="fn">MigrationPlan</span>:
    subject: str; old_version: int; new_schema: dict
    canary_pct: float = <span class="num">0.05</span>
    error_threshold: float = <span class="num">0.001</span>
    monitor_window_sec: int = <span class="num">900</span>

<span class="kw">class</span> <span class="fn">MigrationOrchestrator</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self, schema_mgr, metrics):
        self.schema_mgr = schema_mgr; self.metrics = metrics

    <span class="kw">def</span> <span class="fn">execute</span>(self, plan: MigrationPlan) -> bool:
        <span class="cm"># Step 1: full transitive compatibility check</span>
        <span class="kw">for</span> v <span class="kw">in</span> self.schema_mgr.get_all_versions(plan.subject):
            issues = check_full(v, plan.new_schema)
            <span class="kw">if</span> issues:
                logger.error(f<span class="str">"Incompatible: {[i.message for i in issues]}"</span>)
                <span class="kw">return False</span>

        <span class="cm"># Step 2: canary 5%</span>
        logger.info(f<span class="str">"Canary {plan.canary_pct*100:.0f}% for {plan.subject}"</span>)
        self._set_weight(plan.subject, plan.canary_pct)

        <span class="cm"># Step 3: monitor 15 min</span>
        start = time.monotonic()
        <span class="kw">while</span> time.monotonic() - start < plan.monitor_window_sec:
            rate = self.metrics.deser_error_rate(plan.subject)
            <span class="kw">if</span> rate > plan.error_threshold:
                logger.error(f<span class="str">"Error rate {rate:.4f} > threshold — rolling back"</span>)
                self._set_weight(plan.subject, <span class="num">0.0</span>)
                <span class="kw">return False</span>
            time.sleep(<span class="num">30</span>)

        <span class="cm"># Step 4: promote 100%</span>
        self._set_weight(plan.subject, <span class="num">1.0</span>)
        logger.info(<span class="str">"Migration complete"</span>)
        <span class="kw">return True</span>

    <span class="kw">def</span> <span class="fn">_set_weight</span>(self, subject: str, pct: float):
        self.metrics.set_gauge(f<span class="str">'canary_weight{{subject="{subject}"}}'</span>, pct)</code></pre>
    </details>
    <details class="sreg-code-block">
      <summary><i class="fas fa-diagram-project" style="color:var(--sreg-accent)"></i>&nbsp;Transitive Compatibility Graph (Python)</summary>
      <pre><code><span class="kw">from</span> typing <span class="kw">import</span> List, Dict, Tuple

<span class="kw">class</span> <span class="fn">CompatibilityGraph</span>:
    <span class="cm">"""Full pairwise compatibility check across all schema versions.
    Catches transitive incompatibility that adjacent-only checks miss."""</span>

    <span class="kw">def</span> <span class="fn">__init__</span>(self, schema_mgr):
        self.schema_mgr = schema_mgr
        self._cache: Dict[Tuple[int, int], List[CompatIssue]] = {}

    <span class="kw">def</span> <span class="fn">build</span>(self, subject: str) -> Dict[Tuple[int, int], List[CompatIssue]]:
        <span class="cm">"""O(n^2) check — run in CI, not hot path."""</span>
        versions = self.schema_mgr.get_all_versions(subject)
        results = {}
        <span class="kw">for</span> i, v1 <span class="kw">in</span> enumerate(versions):
            <span class="kw">for</span> j, v2 <span class="kw">in</span> enumerate(versions):
                <span class="kw">if</span> i == j: <span class="kw">continue</span>
                key = (i, j)
                <span class="kw">if</span> key <span class="kw">not in</span> self._cache:
                    self._cache[key] = check_full(v1, v2)
                results[key] = self._cache[key]
        <span class="kw">return</span> results

    <span class="kw">def</span> <span class="fn">safe_to_ship</span>(self, subject: str, new_schema: dict) -> bool:
        <span class="cm">"""Returns True only if new schema is compatible with ALL versions."""</span>
        <span class="kw">for</span> v <span class="kw">in</span> self.schema_mgr.get_all_versions(subject):
            <span class="kw">if</span> check_full(v, new_schema):
                <span class="kw">return False</span>
        <span class="kw">return True</span>

    <span class="kw">def</span> <span class="fn">dead_fields</span>(self, subject: str, access_log: Dict[str, int],
                    window_days: int = <span class="num">90</span>) -> List[str]:
        <span class="cm">"""Fields with zero consumer reads in window_days = safe to remove.</span>
        <span class="cm">access_log: {field_name: read_count_in_window}"""</span>
        latest = self.schema_mgr.get_all_versions(subject)[-<span class="num">1</span>]
        <span class="kw">return</span> [
            f[<span class="str">'name'</span>] <span class="kw">for</span> f <span class="kw">in</span> latest[<span class="str">'fields'</span>]
            <span class="kw">if</span> access_log.get(f[<span class="str">'name'</span>], <span class="num">0</span>) == <span class="num">0</span>
        ]</code></pre>
    </details>
  </div>
</section>

<!-- ══ ABOUT ══ -->
<section class="sreg-section" id="sreg-about">
  <div class="sreg-sec-head">
    <h2>About This Demo</h2>
    <p>A live Confluent Schema Registry simulator with real compatibility checking and animated schema diffing.</p>
  </div>
  <div class="sreg-about-card">
    <h3>&#x1F4C4; Kafka Schema Evolution &#8212; Live Simulator</h3>
    <p>Apply breaking and safe changes to an <code>OrderEvent</code> Avro schema, see real-time compatibility assessment across BACKWARD / FORWARD / FULL modes, and explore the production patterns that prevent 3AM incidents.</p>
    <p style="font-size:.72rem;color:var(--sreg-muted)">Stack: JavaScript &#183; Confluent Schema Registry patterns &#183; Django 5.1 &#183; Event-Driven Architecture</p>
    <button class="sreg-share-btn" onclick="sregShareDemo()">&#x1F517; Copy Link</button>
  </div>
</section>

</div><!-- /sreg-wrap -->
{% endblock content %}
{% block extra_js %}
<script>
(function(){
'use strict';

/* ══ 7-ideations nav helpers ══ */
var sregClsCurrent = 0;
var sregELI5Selected = null;

var SREG_ELI5 = {
  backend: {
    label: 'Backend Developer',
    title: 'Why Your API Broke &#8212; and How the Registry Prevents It',
    run: function(){
      return {
        body: 'You changed <code>user_id</code> from <code>int</code> to <code>string</code> because your new user service uses UUIDs. Unit tests passed. You deployed. Three minutes later, six Kafka consumers started crashing with <code>AvroTypeException: Expected int, found string</code>.<br><br>With a Schema Registry, that deployment would never have reached production. The CI/CD pipeline runs <code>test_compatibility()</code> before deployment. Since changing a field type is a BREAKING change under BACKWARD, FORWARD, and FULL modes, the registration fails and the build fails. You get a clear error message listing exactly which consumers would break and why. Fix it with a union type migration instead.',
        stats: ['Type change: int &#8594; string = BREAKING in all modes', 'Registry catches at CI/CD, not at 3AM', 'Union type fix: ["null","string","int"] = gradual migration', '87 schema versions shipped safely after registry adoption']
      };
    }
  },
  dataeng: {
    label: 'Data Engineer',
    title: 'Kafka Consumer Deserialization Errors &#8212; Root Cause',
    run: function(){
      return {
        body: 'Your Kafka consumer is logging <code>org.apache.avro.AvroTypeException</code> at 400 errors/minute. The consumer group lag is growing &#8212; it&#39;s processing zero messages. The problem: a producer deployed a schema change yesterday that removed a field your consumer expects. Your consumer holds a stale reader schema in its local cache.<br><br>With a registry, the consumer fetches the writer schema by ID on every batch. It applies schema resolution: writer schema (what was in the message) vs. reader schema (what your consumer expects). The registry handles field defaults automatically. Even if the producer removed a field with a default, your consumer gets the default value and processes the message successfully.',
        stats: ['Consumer fetches writer schema by 5-byte header ID', 'Schema resolution: writer schema + reader schema &#8594; resolved record', 'Missing field with default: consumer gets default, no crash', 'Schema cache TTL: 60s default &#8212; tune to reduce registry calls']
      };
    }
  },
  architect: {
    label: 'Platform Architect',
    title: 'Schema Registry as the Contract Layer for 50+ Microservices',
    run: function(){
      return {
        body: 'Without a central registry, schema management in a large microservices platform is tribal knowledge: developer A knows OrderEvent v3 added a channel field, developer B doesn&#39;t. Renaming a field in one service cascades into 6 hotfixes across 4 teams. Onboarding a new consumer requires reading 18 months of git history.<br><br>The registry is the single source of truth for every event contract. Each subject (topic name + value/key) has a versioned history, a compatibility mode, and a human-readable description. New consumers can fetch the latest schema, understand the evolution history, and know exactly which fields are stable vs. likely to change. Schema governance becomes a platform concern, not a tribal one.',
        stats: ['Single registry: 14 subjects, 87 schema versions', 'Compatibility mode per subject: BACKWARD (default), FULL (financial)', 'Dead field detection: 23 fields identified for MAJOR cleanup', 'Schema ID in message header: 5 bytes overhead per message']
      };
    }
  },
  compliance: {
    label: 'Compliance Officer',
    title: 'MiFID II 7-Year Replay &#8212; Why FULL Compatibility Is Non-Negotiable',
    run: function(){
      return {
        body: 'MiFID II Article 25 requires investment firms to retain order records for 7 years and produce them on regulatory request. That means replaying 2019 Kafka messages against 2026 consumer code. Without schema governance, that replay will fail: fields have been renamed, types have changed, required fields have been removed.<br><br>FULL compatibility mode enforces that every schema change is non-breaking in both directions. Over 7 years, the only allowed operations are: (1) add fields with defaults, (2) remove fields that previously had defaults. No renames, no type changes. Your 2019 messages will always be readable by any version of the consumer. The schema registry provides an immutable audit trail of every schema version, timestamped, with the identity of who registered it &#8212; admissible evidence of your data governance program.',
        stats: ['MiFID II: 7-year record retention and replay', 'FULL mode: only additive changes with defaults', 'Schema registry: immutable version history with timestamps', 'Regulatory evidence: who registered each schema version']
      };
    }
  }
};

function sregSetMode(mode) {
  document.querySelectorAll('.sreg-mode-tab').forEach(function(b){
    b.classList.toggle('active', b.getAttribute('data-pane') === mode);
  });
  document.querySelectorAll('.sreg-pane').forEach(function(p){
    p.classList.toggle('active', p.getAttribute('data-pane') === mode);
  });
}
function sregSelectPersona(key) {
  sregELI5Selected = key;
  document.querySelectorAll('.sreg-persona').forEach(function(p){
    p.classList.toggle('selected', p.getAttribute('data-key') === key);
  });
  document.getElementById('sregELI5Result').classList.remove('show');
}
function sregRunELI5() {
  if (!sregELI5Selected) { alert('Select a persona first!'); return; }
  var p = SREG_ELI5[sregELI5Selected];
  var data = p.run();
  document.getElementById('sregELI5Title').innerHTML = p.title;
  document.getElementById('sregELI5Body').innerHTML = data.body;
  document.getElementById('sregELI5Stats').innerHTML = data.stats.map(function(s){
    return '<span class="sreg-eli5-stat">' + s + '</span>';
  }).join('');
  document.getElementById('sregELI5Result').classList.add('show');
}
function sregClsShowSlide(n) {
  sregClsCurrent = n;
  document.querySelectorAll('.sreg-cls-slide').forEach(function(s, i){ s.classList.toggle('active', i === n); });
  document.querySelectorAll('.sreg-cls-dot').forEach(function(d, i){ d.classList.toggle('active', i === n); });
}
function sregClsNext() { sregClsShowSlide((sregClsCurrent + 1) % 6); }
function sregClsPrev() { sregClsShowSlide((sregClsCurrent + 5) % 6); }
function sregGotoClsDot(n) { sregClsShowSlide(n); }
function sregShareDemo() {
  navigator.clipboard.writeText(window.location.href).then(function(){
    var btn = document.querySelector('.sreg-share-btn');
    btn.textContent = '\u2713 Copied!';
    setTimeout(function(){ btn.innerHTML = '&#x1F517; Copy Link'; }, 2000);
  });
}
function sregScrollTo(id) {
  var el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  document.querySelectorAll('.sreg-nav-btn').forEach(function(b){
    b.classList.remove('active');
    if (b.getAttribute('onclick') && b.getAttribute('onclick').indexOf(id) > -1)
      b.classList.add('active');
  });
}
function sregInitNav() {
  var fill = document.getElementById('sregProgressFill');
  var secs = Array.from(document.querySelectorAll('.sreg-section'));
  var btns = Array.from(document.querySelectorAll('.sreg-nav-btn'));
  window.addEventListener('scroll', function(){
    var scrolled = window.scrollY;
    var total = document.documentElement.scrollHeight - window.innerHeight;
    fill.style.width = (total > 0 ? Math.min(100, scrolled / total * 100) : 0) + '%';
    var active = 0;
    secs.forEach(function(s, i){ if (s.getBoundingClientRect().top < 100) active = i; });
    btns.forEach(function(b, i){ b.classList.toggle('active', i === active); });
  });
}

/* exports */
window.sregSetMode = sregSetMode;
window.sregSelectPersona = sregSelectPersona;
window.sregRunELI5 = sregRunELI5;
window.sregClsNext = sregClsNext;
window.sregClsPrev = sregClsPrev;
window.sregGotoClsDot = sregGotoClsDot;
window.sregShareDemo = sregShareDemo;
window.sregScrollTo = sregScrollTo;

/* ══ Original interactive demo ══ */
var V1 = {
  ver:1, ts:'2026-01-15 09:00',
  subject:'OrderEvent', namespace:'com.thenumerix.events',
  fields:[
    {name:'order_id',   type:'string',    required:true,  _tag:''},
    {name:'user_id',    type:'int',       required:true,  _tag:''},
    {name:'amount',     type:'double',    required:true,  _tag:''},
    {name:'currency',   type:'string',    default:'USD',  _tag:''},
    {name:'created_at', type:'timestamp', required:true,  _tag:''}
  ]
};
var versions = [JSON.parse(JSON.stringify(V1))];
var currentVer = 0;
var compatMode = 'BACKWARD';

function renderTimeline(){
  var tl = document.getElementById('sregTimeline');
  tl.innerHTML = '';
  versions.forEach(function(v, idx){
    var li = document.createElement('li');
    li.className = 'sreg-tl-item' + (idx === currentVer ? ' active' : '');
    li.dataset.idx = idx;
    var tagHtml = '';
    if (v._changeMeta)
      tagHtml = '<span class="sreg-tl-tag sreg-tl-tag--' + v._changeMeta.tag + '">' + v._changeMeta.tagLabel + '</span>';
    li.innerHTML = '<span class="sreg-tl-dot"></span><div class="sreg-tl-content"><div class="sreg-tl-ver">v' + v.ver + '</div><div class="sreg-tl-ts">' + v.ts + '</div>' + tagHtml + '</div>';
    li.addEventListener('click', function(){ currentVer = idx; renderView(); renderTimeline(); });
    tl.appendChild(li);
  });
}
function renderView(){
  var v = versions[currentVer];
  document.getElementById('sregVerBadge').textContent = 'v' + v.ver;
  var meta = document.getElementById('sregMeta');
  meta.innerHTML = '<span class="sreg-meta-badge">' + v.namespace + '</span>'
    + '<span class="sreg-meta-badge">' + v.fields.length + ' fields</span>'
    + '<span class="sreg-meta-badge">' + new Date(v.ts).toLocaleDateString() + '</span>';
  var lines = [];
  lines.push('<span class="k">schema</span> <span class="s">' + v.subject + '</span> {');
  lines.push('  <span class="k">namespace</span>: <span class="s">"' + v.namespace + '"</span>');
  lines.push('  <span class="k">version</span>:   <span class="n">' + v.ver + '</span>');
  lines.push('  <span class="k">fields</span>: [');
  v.fields.forEach(function(f){
    var parts = ['    { <span class="k">name</span>: <span class="s">"' + f.name + '"</span>'];
    parts.push('<span class="k">type</span>: <span class="n">' + f.type + '</span>');
    if (f.required) parts.push('<span class="k">required</span>: <span class="b">true</span>');
    if (f.default !== undefined) parts.push('<span class="k">default</span>: <span class="s">"' + f.default + '"</span>');
    var line = parts.join(', ') + ' }';
    if (f._tag) line = '<span class="field-' + f._tag + '">' + line + '</span>';
    lines.push(line);
  });
  lines.push('  ]'); lines.push('}');
  document.getElementById('sregCodeView').innerHTML = lines.join('\n');
  var hasDiff = v.fields.some(function(f){ return f._tag; });
  document.getElementById('sregDiffHint').style.display = hasDiff ? 'flex' : 'none';
  document.getElementById('sregResult').style.display = 'none';
}
function checkCompat(oldV, newV){
  var issues = [];
  if (compatMode === 'BACKWARD' || compatMode === 'FULL'){
    oldV.fields.forEach(function(f){
      var n = newV.fields.find(function(x){ return x.name === f.name; });
      if (!n) issues.push('Field "' + f.name + '" removed \u2014 old consumers break.');
      else if (n.type !== f.type) issues.push('Field "' + f.name + '" type changed ' + f.type + '\u2192' + n.type);
    });
    newV.fields.forEach(function(f){
      var o = oldV.fields.find(function(x){ return x.name === f.name; });
      if (!o && f.default === undefined) issues.push('New required field "' + f.name + '" breaks old data.');
    });
  }
  if (compatMode === 'FORWARD' || compatMode === 'FULL'){
    newV.fields.forEach(function(f){
      var o = oldV.fields.find(function(x){ return x.name === f.name; });
      if (!o && f.required) issues.push('New required field "' + f.name + '" \u2014 old consumers can\'t parse.');
    });
    oldV.fields.forEach(function(f){
      var n = newV.fields.find(function(x){ return x.name === f.name; });
      if (n && n.type !== f.type) issues.push('Type change on "' + f.name + '" \u2014 forward readers fail.');
    });
  }
  return issues;
}
function showResult(issues, changed){
  if (!changed){ document.getElementById('sregResult').style.display = 'none'; return; }
  var pass = issues.length === 0;
  var res = document.getElementById('sregResult');
  res.style.display = 'block';
  res.className = 'sreg-result ' + (pass ? 'sreg-result--compat' : 'sreg-result--incompat');
  res.innerHTML = '<div class="sreg-result-icon">' + (pass ? '\u2705' : '\u{1F6A8}') + '</div>'
    + '<div class="sreg-result-title">' + (pass ? compatMode + ' COMPATIBLE' : compatMode + ' INCOMPATIBLE') + '</div>'
    + (pass ? '<div style="font-size:.68rem;color:var(--sreg-muted)">Safe to deploy.</div>'
            : '<ul class="sreg-result-issues">' + issues.map(function(i){ return '<li>' + i + '</li>'; }).join('') + '</ul>');
}
var CHANGE_DEFS = {
  add_safe: function(s){ s.fields.push({name:'channel',type:'string',default:'web',_tag:'new'}); s._changeMeta={tag:'safe',tagLabel:'SAFE'}; },
  remove_required: function(s){ s.fields = s.fields.filter(function(f){ return f.name !== 'amount'; }); s._changeMeta={tag:'break',tagLabel:'BREAKING'}; },
  rename_field: function(s){ s.fields = s.fields.map(function(f){ return f.name==='amount'?Object.assign({},f,{name:'total_amount',_tag:'mod'}):f; }); s._changeMeta={tag:'break',tagLabel:'BREAKING'}; },
  change_type: function(s){ s.fields = s.fields.map(function(f){ return f.name==='user_id'?Object.assign({},f,{type:'string',_tag:'mod'}):f; }); s._changeMeta={tag:'break',tagLabel:'BREAKING'}; },
  reset: null
};
document.querySelectorAll('.sreg-change-btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    var change = this.getAttribute('data-change');
    if (change === 'reset'){ versions=[JSON.parse(JSON.stringify(V1))]; currentVer=0; renderTimeline(); renderView(); document.getElementById('sregResult').style.display='none'; return; }
    var base = JSON.parse(JSON.stringify(V1));
    var newSchema = JSON.parse(JSON.stringify(V1));
    newSchema.ver = versions.length + 1;
    var now = new Date();
    newSchema.ts = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')+' '+now.toTimeString().slice(0,5);
    newSchema.fields = newSchema.fields.map(function(f){ return Object.assign({}, f, {_tag:''}); });
    CHANGE_DEFS[change](newSchema);
    var issues = checkCompat(base, newSchema);
    versions.push(newSchema); currentVer = versions.length - 1;
    renderTimeline(); renderView(); showResult(issues, true);
  });
});
document.querySelectorAll('.sreg-mode-btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    compatMode = this.getAttribute('data-mode');
    document.querySelectorAll('.sreg-mode-btn').forEach(function(b){ b.classList.remove('active'); });
    this.classList.add('active');
    if (versions.length > 1) showResult(checkCompat(versions[0], versions[currentVer]), true);
  });
});

renderTimeline();
renderView();
sregInitNav();
}());
</script>
{% endblock extra_js %}
''')
out.close()
print('sr2 done')
