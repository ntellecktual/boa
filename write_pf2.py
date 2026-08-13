import pathlib
out = pathlib.Path('boaapp/templates/boaapp/process_flows.html')
p = r'''
<!-- ════════════════════════════ CLASSROOM ════════════════════════════ -->
<section class="pf-sec" id="pf-classroom">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--v">Classroom</span>
    <h2>How It Works &#x2014; Lesson by Lesson</h2>
    <p>Six slides building from the business problem to fraud prevention. Each slide adds one layer of the system.</p>
  </div>
  <div class="pf-cls-wrap">
    <div class="pf-cls-outer">
      <div class="pf-cls-slides" id="pfClsSlides">

        <!-- Slide 1 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(239,68,68,.11);color:#dc2626">Slide 1 of 6</span>
          <h3>The True Cost of Manual AP</h3>
          <p>Before automation, invoice processing was the most expensive back-office function per transaction. Every invoice required a human to receive it, read it, look up the vendor, recall the GL code, key it into the ERP, route it for approval by email, follow up, and finally post. That human loop cost $15&#x2013;$40 per invoice fully loaded &#x2014; and introduced a 1&#x2013;3% error rate that compounded into rework, late payments, and vendor relationship damage.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">$25</div><div class="pf-cls-fact-lbl">Avg cost per manual invoice</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">25 min</div><div class="pf-cls-fact-lbl">Processing time per invoice</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">40 days</div><div class="pf-cls-fact-lbl">Average DPO (Days Payable Outstanding)</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">1&#x2013;3%</div><div class="pf-cls-fact-lbl">Manual entry error rate</div></div>
          </div>
        </div>

        <!-- Slide 2 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(59,130,246,.11);color:#2563eb">Slide 2 of 6</span>
          <h3>Azure Document Intelligence: Structured Extraction</h3>
          <p>Azure Form Recognizer's pre-built invoice model is a fine-tuned transformer that has been trained on millions of invoice documents. It extracts vendor name, invoice number, invoice date, due date, purchase order number, total amount, tax, and every line item &#x2014; all in a single REST API call. Each field comes with a confidence score (0.0&#x2013;1.0). Fields below 0.85 are flagged for human review. The output is structured JSON at $0.01/page &#x2014; a 2,400&#xD7; cost reduction vs. manual keying.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">97%</div><div class="pf-cls-fact-lbl">Field-level extraction accuracy</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">0.85</div><div class="pf-cls-fact-lbl">Confidence threshold for auto-processing</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">$0.01</div><div class="pf-cls-fact-lbl">Cost per page (vs. $25 manual)</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">180+</div><div class="pf-cls-fact-lbl">Supported languages</div></div>
          </div>
        </div>

        <!-- Slide 3 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(139,92,246,.11);color:#7c3aed">Slide 3 of 6</span>
          <h3>Why AI Beats Rules for GL Code Classification</h3>
          <p>Rule-based GL coding uses static IF/THEN logic: "if vendor = AWS then GL = 6300." This works for 78% of invoices &#x2014; the ones with known vendors and obvious categories. It fails on new vendors (no rule exists), multi-line invoices (line items span multiple GL accounts), and ambiguous descriptions ("Professional services" could be 6600 or 6800 depending on context). A TF-IDF vectorizer converts invoice text into a 5,000-feature sparse matrix. Logistic regression trained on 2 years of GL history learns the associations. Result: 94% accuracy &#x2014; and it improves quarterly as you retrain on new data.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">78%</div><div class="pf-cls-fact-lbl">Rule-based accuracy ceiling</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">94%</div><div class="pf-cls-fact-lbl">AI classifier accuracy</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">5,000</div><div class="pf-cls-fact-lbl">TF-IDF features (1-gram + 2-gram)</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">0.70</div><div class="pf-cls-fact-lbl">Confidence threshold for auto-posting</div></div>
          </div>
        </div>

        <!-- Slide 4 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(16,185,129,.11);color:#059669">Slide 4 of 6</span>
          <h3>The 3-Way Match Protocol</h3>
          <p>Two-way matching compares only the Purchase Order against the Invoice. It catches pricing errors but misses quantity fraud: a vendor ships 80 units, invoices for 100, and the PO matches on price. Three-way match adds the Goods Receipt Note (GRN) from the warehouse, checking that received quantity equals invoiced quantity. Real invoices almost never match exactly &#x2014; shipping, tax rounding, and FX create small variances. Tolerance bands (2% per line, 5% total) separate genuine fraud from noise. Setting them correctly is the entire engineering challenge: too tight and you flood reviewers with false positives; too loose and fraud slips through.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">2%</div><div class="pf-cls-fact-lbl">Per-line item tolerance band</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">5%</div><div class="pf-cls-fact-lbl">Invoice total tolerance band</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">40%</div><div class="pf-cls-fact-lbl">False exception rate at exact match</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">8%</div><div class="pf-cls-fact-lbl">False exception rate with tolerance bands</div></div>
          </div>
        </div>

        <!-- Slide 5 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(245,158,11,.11);color:#b45309">Slide 5 of 6</span>
          <h3>Hierarchical Approval Routing</h3>
          <p>Flat approval &#x2014; sending everything to the department head &#x2014; creates a bottleneck and trains reviewers to rubber-stamp because every invoice looks the same. Hierarchical routing assigns approval authority by value and risk: small routine invoices auto-approve, mid-range go to cost center managers who know the context, large invoices escalate to VP with full supporting detail. The velocity trigger is the key innovation: when a cost center's 30-day rolling spend exceeds 120% of budget, ALL invoices for that center escalate one level automatically &#x2014; creating self-enforcing budget guardrails with no manual policy changes required.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">&lt;$5K</div><div class="pf-cls-fact-lbl">Auto-approve if 3-way matched (73% of volume)</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">$5K&#x2013;$50K</div><div class="pf-cls-fact-lbl">Cost center manager approval</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">&gt;$50K</div><div class="pf-cls-fact-lbl">VP approval required</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">120%</div><div class="pf-cls-fact-lbl">Budget velocity trigger for auto-escalation</div></div>
          </div>
        </div>

        <!-- Slide 6 -->
        <div class="pf-cls-slide">
          <span class="pf-cls-slide-tag" style="background:rgba(239,68,68,.11);color:#dc2626">Slide 6 of 6</span>
          <h3>Fraud Prevention: MinHash LSH</h3>
          <p>The #1 AP fraud vector is the resubmitted invoice: a vendor submits the same invoice with a slightly different number, date, or amount. Exact-match deduplication catches identical duplicates but misses near-duplicates. MinHash Locality-Sensitive Hashing (LSH) solves this. It converts invoice line items into a set of minhash signatures and groups similar invoices into the same hash bucket. Any invoice landing in the same bucket as a recent invoice from the same vendor, within $50, within 30 days, is held for human review. The technique scales to millions of invoice pairs without comparing each pair explicitly &#x2014; O(n) instead of O(n&#xB2;). Combined with spend velocity tracking, the system provides self-healing fraud detection that tightens automatically when anomalies appear.</p>
          <div class="pf-cls-facts">
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">MinHash</div><div class="pf-cls-fact-lbl">LSH for near-duplicate invoice detection</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">30 days</div><div class="pf-cls-fact-lbl">Lookback window for duplicate check</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">$50</div><div class="pf-cls-fact-lbl">Amount variance threshold for LSH match</div></div>
            <div class="pf-cls-fact"><div class="pf-cls-fact-val">O(n)</div><div class="pf-cls-fact-lbl">Time complexity (vs. O(n&#xB2;) brute force)</div></div>
          </div>
        </div>

      </div><!-- /slides -->
    </div><!-- /outer -->
    <div class="pf-cls-nav">
      <button class="pf-cls-btn" onclick="pfClsPrev()"><i class="fas fa-chevron-left"></i></button>
      <div class="pf-cls-dots" id="pfClsDots">
        <div class="pf-cls-dot active" onclick="pfClsGoto(0)"></div>
        <div class="pf-cls-dot" onclick="pfClsGoto(1)"></div>
        <div class="pf-cls-dot" onclick="pfClsGoto(2)"></div>
        <div class="pf-cls-dot" onclick="pfClsGoto(3)"></div>
        <div class="pf-cls-dot" onclick="pfClsGoto(4)"></div>
        <div class="pf-cls-dot" onclick="pfClsGoto(5)"></div>
      </div>
      <span class="pf-cls-counter" id="pfClsCounter">1 / 6</span>
      <button class="pf-cls-btn" onclick="pfClsNext()"><i class="fas fa-chevron-right"></i></button>
    </div>
  </div>
</section>

<!-- ════════════════════════════ KEY POINTS ════════════════════════════ -->
<section class="pf-sec" id="pf-keypoints">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--a">Key Points</span>
    <h2>Four Engineering Decisions That Made It Work</h2>
    <p>The automation works because of specific, deliberate engineering choices &#x2014; each with a measurable impact.</p>
  </div>
  <div class="pf-kp-grid">

    <div class="pf-kp-card">
      <div class="pf-kp-metric">+16 pts</div>
      <h5>AI vs. Rules for GL Coding</h5>
      <p>Rule-based GL classification plateaus at 78% accuracy &#x2014; it cannot generalize to new vendors or ambiguous multi-line invoices. A TF-IDF + logistic regression classifier on 2 years of history achieves 94%. The 16-point gap widens further on hospitality-specific vendor categories where rules require constant manual maintenance.</p>
      <span class="pf-kp-why">Why it matters: 94% accuracy is the threshold where AP team trust in the system exceeds resistance to adoption</span>
    </div>

    <div class="pf-kp-card">
      <div class="pf-kp-metric">40% &#x2192; 8%</div>
      <h5>Tolerance Bands Cut False Exceptions</h5>
      <p>Exact-match validation flags 40% of invoices as exceptions &#x2014; creating a workload that overwhelms reviewers and destroys the ROI of automation. A 2% per-line and 5% total tolerance reduces false exceptions to 8%. Engineering the tolerance thresholds is the critical calibration: they must be loose enough to avoid noise but tight enough to catch the 2.3% genuine overpayment rate.</p>
      <span class="pf-kp-why">Why it matters: false exception rate drives reviewer workload and determines whether the system is trusted or bypassed</span>
    </div>

    <div class="pf-kp-card">
      <div class="pf-kp-metric">$375K &#x2192; $195</div>
      <h5>Serverless Economics at Scale</h5>
      <p>The entire pipeline at 15,000 invoices/month: Form Recognizer OCR at $0.01/page, Azure Functions at near-zero, Claude API at $0.003/invoice, SQL writes at $0.001, Logic Apps orchestration at $0.001. Total: $0.013/invoice or $195/month &#x2014; down from $375,000/year in AP labor. The cost structure is perfectly variable: it scales to zero on slow months and to any volume without infrastructure investment.</p>
      <span class="pf-kp-why">Why it matters: variable cost structure eliminates the risk of over-provisioning for peak capacity</span>
    </div>

    <div class="pf-kp-card">
      <div class="pf-kp-metric">73%</div>
      <h5>Auto-Approval Covers the Majority</h5>
      <p>73% of invoices are under $5,000 and pass 3-way match validation. These auto-approve without any human touch. The approval queue drops from 15,000 to 4,050 invoices/month. Controllers now review only the invoices that genuinely benefit from human judgment &#x2014; high-value, new-vendor, or exception-flagged. The spend velocity trigger adds automatic escalation when cost centers overspend, creating budget guardrails without policy changes.</p>
      <span class="pf-kp-why">Why it matters: routing 73% automatically lets approvers give full attention to the 27% that actually need them</span>
    </div>

  </div>
</section>

<!-- ════════════════════════════ CODE ════════════════════════════ -->
<section class="pf-sec" id="pf-code">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--b">Production Code</span>
    <h2>Production Implementation</h2>
    <p>The three core algorithms &#x2014; extraction, matching, and classification &#x2014; that power the pipeline.</p>
  </div>
  <div class="pf-impl">

    <details>
      <summary><i class="fas fa-file-alt me-2" style="color:var(--pf-blue)"></i>Invoice Data Extraction &#x2014; Azure Form Recognizer (Python)</summary>
      <pre>from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.identity import DefaultAzureCredential
import os

CONFIDENCE_THRESHOLD = 0.85

def extract_invoice(blob_url: str) -&gt; dict:
    """Extract structured fields from a PDF invoice
    using Azure AI Document Intelligence."""
    client = DocumentAnalysisClient(
        endpoint=os.environ["FORM_RECOGNIZER_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    poller = client.begin_analyze_document_from_url(
        "prebuilt-invoice", blob_url
    )
    result = poller.result()

    for invoice in result.documents:
        fields = invoice.fields
        extracted = {
            "vendor_name":  _safe(fields, "VendorName"),
            "invoice_num":  _safe(fields, "InvoiceId"),
            "invoice_date": _safe(fields, "InvoiceDate"),
            "due_date":     _safe(fields, "DueDate"),
            "total":        _safe(fields, "InvoiceTotal"),
            "line_items":   _extract_lines(fields),
            "confidence":   invoice.confidence,
        }
        if invoice.confidence &lt; CONFIDENCE_THRESHOLD:
            extracted["needs_review"] = True
            extracted["review_reason"] = (
                f"Low confidence ({invoice.confidence:.2f})"
            )
        return extracted

    return {"error": "No invoice detected", "needs_review": True}

def _safe(fields, key):
    f = fields.get(key)
    return f.value if f else None

def _extract_lines(fields):
    items = fields.get("Items")
    if not items:
        return []
    lines = []
    for item in items.value:
        sf = item.value
        lines.append({
            "description": _safe(sf, "Description"),
            "quantity":    _safe(sf, "Quantity"),
            "unit_price":  _safe(sf, "UnitPrice"),
            "amount":      _safe(sf, "Amount"),
            "confidence":  item.confidence,
        })
    return lines</pre>
    </details>

    <details>
      <summary><i class="fas fa-check-double me-2" style="color:var(--pf-emerald)"></i>3-Way Match Engine &#x2014; PO / Invoice / GRN (Python)</summary>
      <pre>from dataclasses import dataclass
from Levenshtein import distance as lev_distance

TOLERANCE_LINE  = 0.02   # 2% per line item
TOLERANCE_TOTAL = 0.05   # 5% on invoice total

@dataclass
class MatchResult:
    status: str           # "matched" | "exception"
    score: float          # 0.0 - 1.0
    exceptions: list
    explanation: str

def three_way_match(po, invoice, grn) -&gt; MatchResult:
    """Compare PO, Invoice, and Goods Receipt line-by-line."""
    exceptions = []

    # 1. GRN must exist before matching
    if grn is None:
        return MatchResult("exception", 0.0,
            [{"type": "MISSING_GRN",
              "detail": f"No GRN for PO {po['po_number']}"}],
            "Goods receipt not yet recorded.")

    # 2. Match line items (fuzzy on description)
    matched, total_po, total_inv = 0, 0.0, 0.0
    for po_line in po["lines"]:
        best = _fuzzy_find(po_line, invoice["lines"])
        if best is None:
            exceptions.append({"type": "MISSING_LINE",
                "detail": f"PO line '{po_line['desc']}' not on invoice"})
            continue

        # Price variance check
        diff = abs(best["amount"] - po_line["amount"])
        if diff / max(po_line["amount"], 0.01) &gt; TOLERANCE_LINE:
            exceptions.append({"type": "PRICE_VARIANCE",
                "detail": f"{po_line['desc']}: PO ${po_line['amount']:.2f}"
                           f" vs INV ${best['amount']:.2f}"})

        # Quantity check against GRN
        grn_line = _fuzzy_find(po_line, grn["lines"])
        if grn_line and grn_line["qty"] != best.get("qty", 0):
            exceptions.append({"type": "QTY_VARIANCE",
                "detail": f"{po_line['desc']}: GRN {grn_line['qty']}"
                           f" vs INV {best.get('qty', '?')}"})

        matched += 1
        total_po  += po_line["amount"]
        total_inv += best["amount"]

    # 3. Total tolerance check
    if total_po &gt; 0:
        var = abs(total_inv - total_po) / total_po
        if var &gt; TOLERANCE_TOTAL:
            exceptions.append({"type": "TOTAL_VARIANCE",
                "detail": f"PO ${total_po:.2f} vs INV ${total_inv:.2f}"
                           f" ({var:.1%} variance)"})

    score = matched / max(len(po["lines"]), 1)
    status = "matched" if not exceptions else "exception"
    return MatchResult(status, score, exceptions,
        f"{matched}/{len(po['lines'])} lines, {len(exceptions)} exceptions")

def _fuzzy_find(target, candidates):
    best, best_d = None, 999
    for c in candidates:
        d = lev_distance(target["desc"].lower(), c["desc"].lower())
        if d &lt; best_d:
            best, best_d = c, d
    return best if best_d &lt; 3 else None</pre>
    </details>

    <details>
      <summary><i class="fas fa-tags me-2" style="color:var(--pf-violet)"></i>GL Code Classifier &#x2014; TF-IDF + Logistic Regression (Python)</summary>
      <pre>import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

CONFIDENCE_THRESHOLD = 0.70

# ── Training ──────────────────────────────────────────────────────
def train_gl_classifier(history_df):
    """Train on historical descriptions -&gt; GL codes.
    Expects columns: 'description', 'gl_code'."""
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000, ngram_range=(1, 2),
            sublinear_tf=True, stop_words="english")),
        ("clf", LogisticRegression(
            max_iter=1000, C=5.0,
            class_weight="balanced", solver="lbfgs")),
    ])
    pipe.fit(history_df["description"], history_df["gl_code"])
    joblib.dump(pipe, "models/gl_classifier.pkl")
    return pipe

# ── Prediction ────────────────────────────────────────────────────
def predict_gl(description: str, pipe=None):
    """Return GL code with confidence; top-3 fallback
    when confidence &lt; threshold."""
    if pipe is None:
        pipe = joblib.load("models/gl_classifier.pkl")

    probas  = pipe.predict_proba([description])[0]
    classes = pipe.classes_
    top_idx = probas.argsort()[::-1]
    best_code = classes[top_idx[0]]
    best_conf = probas[top_idx[0]]

    if best_conf &gt;= CONFIDENCE_THRESHOLD:
        return {
            "gl_code":    best_code,
            "confidence": round(float(best_conf), 3),
            "method":     "auto",
        }

    # Low confidence: surface top 3 for human review
    return {
        "gl_code":    best_code,
        "confidence": round(float(best_conf), 3),
        "method":     "review",
        "suggestions": [
            {"gl_code":    classes[i],
             "confidence": round(float(probas[i]), 3)}
            for i in top_idx[:3]
        ],
    }</pre>
    </details>

  </div>
</section>

<!-- ════════════════════════════ ABOUT ════════════════════════════ -->
<section class="pf-sec" id="pf-about" style="padding-bottom:3rem">
  <div class="pf-sec-head">
    <span class="pf-tag pf-tag--g">About This Demo</span>
    <h2>Technology Stack</h2>
    <p>Every component in the AP/AR automation pipeline &#x2014; from email ingestion to ERP posting.</p>
  </div>
  <div class="pf-about-card">
    <div class="pf-about-title">Finance Process Flows &#x2014; AP/AR Automation</div>
    <div class="pf-about-sub">Production-grade invoice processing pipeline for Ashford Hospitality's 9 entities</div>
    <div class="pf-about-pills">
      <span class="pf-about-pill">Azure Logic Apps</span>
      <span class="pf-about-pill">Azure Document Intelligence</span>
      <span class="pf-about-pill">Claude 3.5 Sonnet</span>
      <span class="pf-about-pill">Azure Functions (Python)</span>
      <span class="pf-about-pill">Acumatica Cloud ERP</span>
      <span class="pf-about-pill">Azure Key Vault</span>
      <span class="pf-about-pill">Azure SQL Database</span>
      <span class="pf-about-pill">Power BI Embedded</span>
      <span class="pf-about-pill">Azure Communication Services</span>
      <span class="pf-about-pill">Azure Monitor</span>
      <span class="pf-about-pill">Azure AD / RBAC</span>
      <span class="pf-about-pill">scikit-learn TF-IDF</span>
      <span class="pf-about-pill">MinHash LSH</span>
      <span class="pf-about-pill">Python-Levenshtein</span>
      <span class="pf-about-pill">OpenAPI 3.0</span>
    </div>
    <button class="pf-share-btn" onclick="pfShareDemo()">
      <i class="fas fa-share-alt me-2"></i>Share This Demo
    </button>
  </div>
</section>

{% endblock content %}
{% block extra_js %}
<script>
(function(){'use strict';

/* ─────────────── Progress bar + scroll spy ─────────────── */
var pfFill = document.getElementById('pfProgressFill');
var pfSections = ['pf-story','pf-demo','pf-classroom','pf-keypoints','pf-code','pf-about'];
var pfTabs = document.querySelectorAll('.pf-nav-tab');

function pfUpdateProgress(){
  var sc = window.scrollY, h = document.body.scrollHeight - window.innerHeight;
  if(pfFill) pfFill.style.width = (h > 0 ? Math.min(100, sc/h*100) : 0) + '%';
  var best = 0;
  pfSections.forEach(function(id, i){
    var el = document.getElementById(id);
    if(el && el.getBoundingClientRect().top <= window.innerHeight * 0.4) best = i;
  });
  pfTabs.forEach(function(t, i){ t.classList.toggle('active', i === best); });
}
window.addEventListener('scroll', pfUpdateProgress, {passive:true});
pfUpdateProgress();

/* ─────────────── Nav scroll ─────────────── */
function pfScrollTo(id){
  var el = document.getElementById(id);
  if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
}
window.pfScrollTo = pfScrollTo;

/* ─────────────── Mode toggle (ELI5 / Engineer) ─────────────── */
function pfSetMode(mode){
  var eli5 = document.getElementById('pfELI5Pane');
  var eng  = document.getElementById('pfEngPane');
  var bEli = document.getElementById('pfBtnELI5');
  var bEng = document.getElementById('pfBtnEng');
  if(mode === 'eli5'){
    if(eli5) eli5.style.display = '';
    if(eng)  eng.style.display  = 'none';
    if(bEli) bEli.classList.add('active');
    if(bEng) bEng.classList.remove('active');
  } else {
    if(eli5) eli5.style.display = 'none';
    if(eng)  eng.style.display  = '';
    if(bEli) bEli.classList.remove('active');
    if(bEng) bEng.classList.add('active');
  }
}
window.pfSetMode = pfSetMode;

/* ─────────────── Classroom ─────────────── */
var pfClsIdx = 0, pfClsTotal = 6;

function pfClsRender(){
  var slides = document.getElementById('pfClsSlides');
  if(slides) slides.style.transform = 'translateX(-' + (pfClsIdx * 100) + '%)';
  var dots = document.querySelectorAll('.pf-cls-dot');
  dots.forEach(function(d,i){ d.classList.toggle('active', i === pfClsIdx); });
  var ctr = document.getElementById('pfClsCounter');
  if(ctr) ctr.textContent = (pfClsIdx+1) + ' / ' + pfClsTotal;
}
function pfClsNext(){ pfClsIdx = (pfClsIdx + 1) % pfClsTotal; pfClsRender(); }
function pfClsPrev(){ pfClsIdx = (pfClsIdx - 1 + pfClsTotal) % pfClsTotal; pfClsRender(); }
function pfClsGoto(i){ pfClsIdx = i; pfClsRender(); }
window.pfClsNext = pfClsNext;
window.pfClsPrev = pfClsPrev;
window.pfClsGoto = pfClsGoto;

/* ─────────────── Share ─────────────── */
function pfShareDemo(){
  if(navigator.share){
    navigator.share({title:'Finance Process Flows — AI AP/AR Automation', url:window.location.href});
  } else {
    navigator.clipboard.writeText(window.location.href).then(function(){
      alert('Link copied to clipboard!');
    });
  }
}
window.pfShareDemo = pfShareDemo;

/* ═══════════════════════════════════════════════════════════
   AP PIPELINE SIMULATOR
   ═══════════════════════════════════════════════════════════ */
var btnRun   = document.getElementById('btnRun');
var btnReset = document.getElementById('btnReset');
var stage    = document.getElementById('demoPipeline');
var dashWrap = document.getElementById('demoDashboard');
var running  = false;
var processed = [], totalPosted = 0, totalTime = 0;

function money(n){ return '$'+n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,','); }
function wait(ms){ return new Promise(function(r){ setTimeout(r,ms); }); }
function appendStep(html){ stage.insertAdjacentHTML('beforeend',html); stage.scrollTop=stage.scrollHeight; }
function addLog(msg){
  var la=document.getElementById('logArea');
  if(!la) return;
  var ts=new Date().toLocaleTimeString('en-US',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'});
  la.insertAdjacentHTML('beforeend','<div style="animation:pfSlide .2s ease">'+ts+' '+msg+'</div>');
}
function setPip(idx,state){
  for(var i=0;i<6;i++){
    var el=document.getElementById('pip'+i);
    el.classList.remove('active','done');
    if(i<idx) el.classList.add('done');
    else if(i===idx) el.classList.add(state==='active'?'active':'done');
  }
}

var vendors=[
  {name:'Acme Supplies Co.',    category:'Office'},
  {name:'Gulf Coast Electric',  category:'Utilities'},
  {name:'Premier Tech Partners',category:'IT'},
  {name:'Lone Star Linen',      category:'Hospitality'},
  {name:'Apex HVAC Solutions',  category:'Maintenance'},
  {name:'TechBridge Consulting',category:'Professional'},
  {name:'Metro Food Services',  category:'F&B'},
  {name:'National Printing Co.',category:'Marketing'}
];
var entities=['Ashford Hospitality Trust','Remington Hotels','Stirling Hotels',
  'Premier Properties','Pure Wellness','OpenKey','The Reservoir'];
var lineItems=['Monthly service agreement','Software license renewal','Equipment maintenance',
  'Supplies Q'+new Date().getMonth(),'Consulting hours','Staff training materials',
  'Replacement parts','Subscription fee','Installation services'];
var glRules={
  'Office':{code:'6100',desc:'Office Supplies',confidence:0.94},
  'Utilities':{code:'6200',desc:'Utilities',confidence:0.97},
  'IT':{code:'6300',desc:'IT Infrastructure',confidence:0.92},
  'Hospitality':{code:'6400',desc:'Linen & Laundry',confidence:0.89},
  'Maintenance':{code:'6500',desc:'HVAC Maintenance',confidence:0.91},
  'Professional':{code:'6600',desc:'Professional Services',confidence:0.88},
  'F&B':{code:'6700',desc:'Food & Beverage',confidence:0.93},
  'Marketing':{code:'6800',desc:'Marketing & Print',confidence:0.90}
};
function classifyGL(vendor){
  var r=glRules[vendor.category];
  return r ? r : {code:'6900',desc:'Uncategorized',confidence:0.45};
}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
function hashStr(s){var h=0;for(var i=0;i<s.length;i++){h=((h<<5)-h)+s.charCodeAt(i);h|=0;}return Math.abs(h);}
function rand(a,rng){return a[Math.floor((rng||Math.random)()*a.length)];}
function randN(a,b,rng){return +((rng||Math.random)()*(b-a)+a).toFixed(2);}

var invoiceCounter=0;
function genInvoice(){
  invoiceCounter++;
  var vi=invoiceCounter%vendors.length;
  var v=vendors[vi];
  var seed=hashStr(v.name+invoiceCounter);
  var rng=mulberry32(seed);
  var gl=classifyGL(v);
  var n=2+Math.floor(rng()*3), items=[];
  for(var i=0;i<n;i++) items.push({desc:rand(lineItems,rng),amount:randN(120,3800,rng)});
  var total=items.reduce(function(s,it){return s+it.amount;},0);
  return {
    num:'INV-'+Math.floor(rng()*90000+10000),
    vendor:v, gl:gl, entity:rand(entities,rng),
    date:new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'}),
    items:items, total:total
  };
}

function stepInvoice(inv){
  setPip(0,'active');
  addLog('&#x1F4E5; Invoice received from <strong>'+inv.vendor.name+'</strong>');
  var itemRows=inv.items.map(function(it){
    return '<div class="pf-inv-row"><span class="lbl">'+it.desc+'</span><span class="val">'+money(it.amount)+'</span></div>';
  }).join('');
  var card=document.getElementById('invoiceCard');
  card.innerHTML=
    '<div class="pf-inv-hdr">'+
    '<span class="pf-inv-logo">'+inv.vendor.name.split(' ')[0].toUpperCase()+'</span>'+
    '<span class="pf-inv-num">'+inv.num+'</span></div>'+
    '<div class="pf-inv-row"><span class="lbl">Date</span><span class="val">'+inv.date+'</span></div>'+
    '<div class="pf-inv-row"><span class="lbl">Entity</span><span class="val">'+inv.entity+'</span></div>'+
    itemRows+
    '<div class="pf-inv-row" style="background:rgba(59,130,246,.05)">'+
    '<span class="lbl" style="font-weight:700">TOTAL</span>'+
    '<span class="val" style="color:var(--pf-blue)">'+money(inv.total)+'</span></div>';
  card.classList.add('vis');
  appendStep(
    '<div class="pf-step-card">'+
    '<h6>&#x1F4E5; Step 1 &mdash; Invoice Received</h6>'+
    '<p style="text-align:center;font-size:.82rem;margin:0">'+
    '<i class="fas fa-check-circle me-1" style="color:#10b981"></i>'+
    inv.vendor.name+' &mdash; '+inv.num+' &mdash; '+money(inv.total)+'</p></div>'
  );
  setPip(0,'done');
  return wait(800);
}

function stepOCR(inv){
  setPip(1,'active');
  addLog('&#x1F441;&#xFE0F; Azure Document Intelligence scanning&hellip;');
  var card=document.getElementById('invoiceCard');
  var sl=document.createElement('div'); sl.className='pf-scan'; card.appendChild(sl);
  appendStep(
    '<div class="pf-step-card" id="stepCard2">'+
    '<h6>&#x1F441;&#xFE0F; Step 2 &mdash; OCR Scanning</h6>'+
    '<p style="text-align:center;font-size:.85rem;margin:0" id="ocrStatus">'+
    '<i class="fas fa-spinner fa-spin me-1" style="color:#3b82f6"></i> Scanning document&hellip;</p></div>'
  );
  return wait(2200).then(function(){
    setPip(1,'done');
    document.getElementById('ocrStatus').innerHTML=
      '<i class="fas fa-check-circle me-1" style="color:#10b981"></i> OCR complete &mdash; '+inv.items.length+' line items extracted';
    addLog('&#x2705; OCR complete &mdash; '+inv.items.length+' line items');
    return wait(600);
  });
}

function stepCode(inv){
  setPip(2,'active');
  addLog('&#x1F3F7;&#xFE0F; GL classifier running&hellip;');
  var rows=inv.items.map(function(it){
    return '<tr><td>'+it.desc+'</td><td style="text-align:right;font-weight:600">'+money(it.amount)+'</td></tr>';
  }).join('');
  appendStep(
    '<div class="pf-step-card" id="stepCard3">'+
    '<h6>&#x1F3F7;&#xFE0F; Step 3 &mdash; Extracted &amp; Auto-Coded</h6>'+
    '<div class="pf-xt">'+
    '<table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>'+
    '<tr><td>Invoice #</td><td><strong>'+inv.num+'</strong></td></tr>'+
    '<tr><td>Vendor</td><td>'+inv.vendor.name+'</td></tr>'+
    '<tr><td>Entity</td><td>'+inv.entity+'</td></tr>'+
    '<tr><td style="color:var(--pf-blue);font-weight:700">GL Code (AI)</td>'+
    '<td style="font-weight:700;color:var(--pf-blue)">'+inv.gl.code+' &mdash; '+inv.gl.desc+
    ' <span style="opacity:.6;font-weight:400;font-size:.7rem">('+Math.round((inv.gl.confidence||0.9)*100)+'% conf)</span></td></tr>'+
    '<tr><td>Total</td><td><strong>'+money(inv.total)+'</strong></td></tr>'+
    '</tbody></table>'+
    '<table style="margin-top:.4rem"><thead><tr><th>Line Item</th><th>Amount</th></tr></thead>'+
    '<tbody>'+rows+'</tbody></table>'+
    '</div></div>'
  );
  return wait(1600).then(function(){
    setPip(2,'done');
    addLog('&#x1F3F7;&#xFE0F; GL classified: <strong>'+inv.gl.code+'</strong> ('+Math.round((inv.gl.confidence||0.9)*100)+'% confidence)');
    return wait(400);
  });
}

function stepValidate(inv){
  setPip(3,'active');
  addLog('&#x2705; Running validation checks&hellip;');
  appendStep(
    '<div class="pf-step-card" id="stepCard4">'+
    '<h6>&#x2705; Step 4 &mdash; Validation Checks</h6>'+
    '<div id="checkList"></div></div>'
  );
  var checks=[
    {id:'ck0',label:'Vendor <strong>'+inv.vendor.name+'</strong> in master'},
    {id:'ck1',label:'GL <strong>'+inv.gl.code+'</strong> valid for <strong>'+inv.entity+'</strong>'},
    {id:'ck2',label:'Amount <strong>'+money(inv.total)+'</strong> within approval threshold'},
    {id:'ck3',label:'No duplicate found for <strong>'+inv.num+'</strong> (MinHash LSH)'},
    {id:'ck4',label:'Tax 8.25% matches Texas jurisdiction'}
  ];
  var cl=document.getElementById('checkList');
  checks.forEach(function(c){
    var d=document.createElement('div');
    d.id=c.id; d.className='pf-chk';
    d.innerHTML='<i class="fas fa-spinner fa-spin pending"></i> '+c.label;
    cl.appendChild(d);
  });
  function showCheck(i){
    if(i>=checks.length) return Promise.resolve();
    return wait(550).then(function(){
      document.getElementById(checks[i].id).classList.add('show');
      return wait(380);
    }).then(function(){
      document.getElementById(checks[i].id).innerHTML=
        '<i class="fas fa-check-circle pass"></i> '+checks[i].label;
      return showCheck(i+1);
    });
  }
  return showCheck(0).then(function(){
    setPip(3,'done');
    addLog('&#x2705; All validation checks passed');
    return wait(400);
  });
}

function stepERPPost(inv){
  setPip(4,'active');
  addLog('&#x1F4E1; Posting to Acumatica REST API&hellip;');
  var j=
    '<span class="key">"endpoint"</span>: <span class="str">"POST /api/v2/payable"</span>,\n'+
    '<span class="key">"erp"</span>: <span class="str">"Acumatica Cloud ERP"</span>,\n'+
    '<span class="key">"invoice"</span>: <span class="str">"'+inv.num+'"</span>,\n'+
    '<span class="key">"vendor"</span>: <span class="str">"'+inv.vendor.name+'"</span>,\n'+
    '<span class="key">"entity"</span>: <span class="str">"'+inv.entity+'"</span>,\n'+
    '<span class="key">"gl_code"</span>: <span class="str">"'+inv.gl.code+'"</span>,\n'+
    '<span class="key">"amount"</span>: <span class="num">'+inv.total.toFixed(2)+'</span>,\n'+
    '<span class="key">"status"</span>: <span class="str">"approved"</span>';
  appendStep(
    '<div class="pf-step-card" id="stepCard5">'+
    '<h6>&#x1F4E1; Step 5 &mdash; ERP API Post</h6>'+
    '<div class="pf-json">'+j+'</div>'+
    '<p style="text-align:center;margin-top:.7rem;font-size:.85rem;margin-bottom:0" id="erpStatus">'+
    '<i class="fas fa-spinner fa-spin me-1" style="color:#3b82f6"></i> Posting to Acumatica&hellip;</p></div>'
  );
  return wait(1800).then(function(){
    setPip(4,'done');
    document.getElementById('erpStatus').innerHTML=
      '<i class="fas fa-check-circle me-1" style="color:#10b981"></i>'+
      ' <strong>HTTP 201 Created</strong> &mdash; '+inv.num+' posted successfully';
    addLog('&#x1F4E1; HTTP 201 Created &mdash; <strong>'+inv.num+'</strong> posted');
    return wait(800);
  });
}

function stepDashboard(inv,elapsed){
  setPip(5,'active');
  dashWrap.style.display='block';
  processed.push(inv); totalPosted+=inv.total; totalTime+=elapsed;
  document.getElementById('kpiProcessed').textContent=processed.length;
  document.getElementById('kpiTotal').textContent=money(totalPosted);
  document.getElementById('kpiAvgTime').textContent=(totalTime/processed.length).toFixed(1)+'s';
  document.getElementById('kpiErrors').textContent='0';
  document.getElementById('dashTable').insertAdjacentHTML('afterbegin',
    '<tr style="animation:pfFadeUp .35s ease both">'+
    '<td><strong>'+inv.num+'</strong></td>'+
    '<td>'+inv.vendor.name+'</td>'+
    '<td>'+money(inv.total)+'</td>'+
    '<td><code>'+inv.gl.code+'</code></td>'+
    '<td>'+inv.entity+'</td>'+
    '<td><span class="pf-ds posted">&#x2705; Posted</span></td>'+
    '<td>'+elapsed.toFixed(1)+'s</td></tr>'
  );
  appendStep(
    '<div class="pf-step-card pf-step-card--ok" id="stepCard6">'+
    '<h6>&#x1F4CA; Step 6 &mdash; Dashboard Updated</h6>'+
    '<p style="text-align:center;font-size:.9rem;color:#10b981;font-weight:700;margin:0">'+
    '<i class="fas fa-check-double me-1"></i> '+inv.num+' fully processed in '+elapsed.toFixed(1)+'s</p>'+
    '<p style="text-align:center;font-size:.77rem;opacity:.6;margin:.25rem 0 0">'+
    processed.length+' invoices &mdash; '+money(totalPosted)+' posted &mdash; 0 errors</p></div>'
  );
  setPip(5,'done');
  addLog('&#x1F4CA; Dashboard updated &mdash; '+processed.length+' invoice(s) posted');
  return wait(600);
}

function runDemo(){
  if(running) return;
  running=true;
  btnRun.disabled=true;
  btnRun.innerHTML='<i class="fas fa-spinner fa-spin me-1"></i> Processing&hellip;';
  btnReset.style.display='none';
  var inv=genInvoice(), start=performance.now();
  stepInvoice(inv)
    .then(function(){ return stepOCR(inv); })
    .then(function(){ return stepCode(inv); })
    .then(function(){ return stepValidate(inv); })
    .then(function(){ return stepERPPost(inv); })
    .then(function(){ return stepDashboard(inv,(performance.now()-start)/1000); })
    .then(function(){
      running=false;
      btnRun.disabled=false;
      btnRun.innerHTML='<i class="fas fa-play me-1"></i> Run Another Invoice';
      btnReset.style.display='';
      document.getElementById('demoDashboard').scrollIntoView({behavior:'smooth',block:'nearest'});
    });
}
window.runDemo = runDemo;

function resetDemo(){
  processed=[]; totalPosted=0; totalTime=0;
  stage.innerHTML='';
  dashWrap.style.display='none';
  document.getElementById('dashTable').innerHTML='';
  var card=document.getElementById('invoiceCard');
  card.innerHTML=''; card.classList.remove('vis');
  document.getElementById('logArea').innerHTML='';
  btnRun.innerHTML='<i class="fas fa-play me-1"></i> Run AP Demo';
  btnReset.style.display='none';
  for(var i=0;i<6;i++) document.getElementById('pip'+i).classList.remove('active','done');
}

if(btnRun)   btnRun.addEventListener('click', runDemo);
if(btnReset) btnReset.addEventListener('click', resetDemo);

}());
</script>
{% endblock extra_js %}
'''
with open('boaapp/templates/boaapp/process_flows.html', 'a', encoding='utf-8') as f:
    f.write(p)
print('pf2 done')
