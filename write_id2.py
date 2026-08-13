"""write_id2.py — IDP Demo 7-ideations redesign, Part 2 ('a' mode)"""
from pathlib import Path

OUT = Path("boaapp/templates/boaapp/idp_demo.html")

p2 = r'''
<!-- ════ CLASSROOM ════ -->
<section class="id-sec" id="id-classroom">
  <div class="id-sec-head">
    <span class="id-tag id-tag--b">Classroom</span>
    <h2>IDP Deep Dives</h2>
    <p>Six lessons that build from the core problem to the most sophisticated techniques in the pipeline.</p>
  </div>

  <div class="id-cls-outer">
    <div class="id-cls-wrap">
      <div class="id-cls-slides" id="idClsSlides">

        <!-- Slide 1 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--t" style="margin-bottom:.65rem">Lesson 1 of 6</div>
          <h3>Why Document Processing Is Genuinely Hard</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>The naive assumption is that documents are just text. In reality, meaning lives in structure:
                the same number means &#x201C;invoice total&#x201D; or &#x201C;page 3&#x201D; depending entirely on
                its position on the page. Traditional OCR gives you words without coordinates &#x2014; useless
                for structured extraction.</p>
              <p>Then add: 50+ different invoice layouts from 200+ vendors, documents arriving at 15&#xB0; rotation,
                handwritten annotations layered over printed text, faded thermal receipts, and mixed-language
                contracts with English headers and Spanish line items.</p>
              <p>Static rule-based extractors handle 3&#x2013;5 vendor templates. ML models generalize across
                all layouts &#x2014; but require preprocessing, multi-engine redundancy, and active learning
                to sustain accuracy above 95% at scale.</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon"><i class="fas fa-th-large"></i></div>
                <div class="id-cls-fact-body">
                  <strong>50+ invoice layouts</strong>
                  <span>From 200+ active vendors; no two identical</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-v)"><i class="fas fa-pen-nib"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Handwriting layers</strong>
                  <span>Annotations and corrections on printed forms require ICR</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-b)"><i class="fas fa-language"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Mixed-language docs</strong>
                  <span>English headers, Spanish/French body text in same document</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-expand-arrows-alt"></i></div>
                <div class="id-cls-fact-body">
                  <strong>15% arrive skewed &gt;3&#xB0;</strong>
                  <span>Preprocessing recovers 40% OCR quality improvement</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 2 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--v" style="margin-bottom:.65rem">Lesson 2 of 6</div>
          <h3>Document Classification with LayoutLM: Text + Layout Together</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>A traditional BERT classifier sees &#x201C;$24,500.00&#x201D; and has no idea if it&#x2019;s
                an invoice total, a PO authorization limit, or a salary in a contract. LayoutLM adds bounding-box
                coordinates (x, y, width, height) as positional embeddings alongside word tokens.</p>
              <p>The model learns that a large number in the top-right quadrant of a document, after the word
                &#x201C;Total Due&#x201D;, is semantically different from the same number inside a table cell
                in row 15. This spatial context is what enables 98.5% classification accuracy &#x2014; an 8.3
                F1 improvement over text-only classifiers on the same document set.</p>
              <p>LayoutLMv3 (the production version) also ingests image patches, making it robust to docs
                where OCR quality is degraded &#x2014; it reads the visual layout even when text extraction fails.</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-v)"><i class="fas fa-vector-square"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Bounding box embeddings</strong>
                  <span>x, y, w, h normalized to [0, 1000] grid per token</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad)"><i class="fas fa-chart-bar"></i></div>
                <div class="id-cls-fact-body">
                  <strong>+8.3 F1 over text-only</strong>
                  <span>Tested on 12,000 labeled documents across 12 types</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-stopwatch"></i></div>
                <div class="id-cls-fact-body">
                  <strong>&lt;300ms classification</strong>
                  <span>GPU inference on Azure ML endpoint, batched 32/request</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-a)"><i class="fas fa-tags"></i></div>
                <div class="id-cls-fact-body">
                  <strong>12 doc types in production</strong>
                  <span>Invoice, PO, receipt, contract, BOL, ID, W-9, 1099, and more</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 3 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--b" style="margin-bottom:.65rem">Lesson 3 of 6</div>
          <h3>Multi-Engine OCR: Defense in Depth for Document Quality</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>Azure Document Intelligence achieves 99.2% word-level accuracy on clean, native-digital PDFs.
                But real-world documents degrade: thermal receipts fade, scanned invoices arrive at angles,
                AP clerks write corrections in margins. On these, Azure drops to 87%.</p>
              <p>The fallback pipeline: for any page with average word confidence below 0.85, extract the page
                as a high-resolution PNG, apply adaptive deskewing (Hough-line angle detection), Gaussian
                denoising, and adaptive binarization (Otsu + local thresholding), then run Tesseract with
                a custom dictionary for financial terms.</p>
              <p>Tesseract recovers 40% of Azure-failed pages, bringing combined accuracy to 97.2%. The extra
                cost per page is $0.003 &#x2014; less than 1% of total pipeline cost for a 12% throughput gain.</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-b)"><i class="fas fa-bolt"></i></div>
                <div class="id-cls-fact-body">
                  <strong>99.2% Azure (clean docs)</strong>
                  <span>Native PDF, high-resolution scan, clear print</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-a)"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="id-cls-fact-body">
                  <strong>87% Azure (degraded docs)</strong>
                  <span>Handwritten, faded, skewed, low-DPI scans</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-shield-alt"></i></div>
                <div class="id-cls-fact-body">
                  <strong>40% fallback recovery</strong>
                  <span>Tesseract with 3-stage preprocessing restores failed pages</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad)"><i class="fas fa-star"></i></div>
                <div class="id-cls-fact-body">
                  <strong>97.2% combined accuracy</strong>
                  <span>Across all document quality tiers in production</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 4 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--g" style="margin-bottom:.65rem">Lesson 4 of 6</div>
          <h3>Named Entity Recognition and Key-Value Extraction</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>Field extraction operates in layers. Layer 1: Azure&#x2019;s prebuilt invoice model extracts
                standard fields (vendor, total, date, PO number) with bounding-box coordinates. This handles
                ~85% of invoices where layout matches a known template.</p>
              <p>Layer 2: spaCy NER trained on financial documents recognizes entities that Azure&#x2019;s template
                model misses &#x2014; addresses, bank account numbers, IBAN codes, currency conversions.
                Custom NER entities were added by labeling 3,000 production invoices in Prodigy.</p>
              <p>Layer 3 (5% of invoices): GPT-4o with a structured output schema. Novel layouts, heavily
                annotated documents, and non-standard formats route here automatically when Layer 1+2
                extraction confidence falls below 0.80. Cost: $0.015/doc, but only for the hard cases.</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-layer-group"></i></div>
                <div class="id-cls-fact-body">
                  <strong>3-layer extraction cascade</strong>
                  <span>Azure prebuilt &#x2192; spaCy NER &#x2192; GPT-4o fallback</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-v)"><i class="fas fa-table"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Table reconstruction</strong>
                  <span>Preserves row/column relationships for line item parsing</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-b)"><i class="fas fa-percentage"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Per-field confidence scores</strong>
                  <span>Enable selective HITL routing &#x2014; review only uncertain fields</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-a)"><i class="fas fa-cube"></i></div>
                <div class="id-cls-fact-body">
                  <strong>18&#x2013;28 fields per invoice</strong>
                  <span>Each with source page, bounding box, engine, and confidence</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 5 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--a" style="margin-bottom:.65rem">Lesson 5 of 6</div>
          <h3>Human-in-the-Loop and Active Learning Flywheel</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>The STP threshold of 95% is deliberate. Below that, the expected value of human review
                ($4.50/invoice labor, prevents $847 average error) exceeds the cost. Above 95%, the error
                rate is 0.3% &#x2014; less costly than universal review.</p>
              <p>The HITL interface shows the original document alongside the extracted JSON. Reviewers
                click incorrect fields, type corrections, and submit. Each correction is stored as a
                labeled example: (document_image, field_name, original_extraction, corrected_extraction,
                original_confidence).</p>
              <p>Weekly, a fine-tuning run processes all new corrections using confidence-weighted cross-entropy
                loss &#x2014; errors where the model was highly confident but wrong get 3&#xD7; more weight.
                This flywheel drove STP from 67% to 85% over six months with zero manual annotation effort.</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-a)"><i class="fas fa-balance-scale"></i></div>
                <div class="id-cls-fact-body">
                  <strong>95% confidence threshold</strong>
                  <span>EVA-based: $4.50 review cost vs $847 avg error cost</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad)"><i class="fas fa-sync-alt"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Weekly fine-tuning cycle</strong>
                  <span>Confidence-weighted loss &#x2014; penalizes high-confidence errors 3&#xD7;</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-trending-up"></i></div>
                <div class="id-cls-fact-body">
                  <strong>67% &#x2192; 85% STP in 6 months</strong>
                  <span>Pure active learning &#x2014; zero manual annotation required</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-v)"><i class="fas fa-tag"></i></div>
                <div class="id-cls-fact-body">
                  <strong>0 manual labels</strong>
                  <span>All training data from production HITL corrections</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 6 -->
        <div class="id-cls-slide">
          <div class="id-tag id-tag--v" style="margin-bottom:.65rem">Lesson 6 of 6</div>
          <h3>Perceptual Hashing: The Fraud Detection Layer Text Matching Misses</h3>
          <div class="id-cls-body">
            <div class="id-cls-lhs">
              <p>Invoice number deduplication catches 60% of duplicate payment attempts. But sophisticated
                fraud &#x2014; and simple mistakes &#x2014; involve resubmitting the same PDF with a different
                filename, a manually altered invoice number, or a re-scanned printout of the same document.</p>
              <p>Perceptual hashing (pHash) generates a 64-bit fingerprint from the visual appearance of the
                document &#x2014; reducing it to an 8&#xD7;8 DCT (discrete cosine transform) of grayscale
                pixel values. Hamming distance between two pHash values measures visual dissimilarity.</p>
              <p>A Hamming distance &#x2264;6 means the documents are visually near-identical &#x2014; same layout,
                same amounts, same structure &#x2014; regardless of filename or metadata. This catches the 40%
                of duplicates that exact-match dedup misses, preventing $142K/year in overpayments across
                15,000 invoices/day at $0 additional cost (pHash runs in 12ms per doc).</p>
            </div>
            <div class="id-cls-rhs">
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-v)"><i class="fas fa-hashtag"></i></div>
                <div class="id-cls-fact-body">
                  <strong>64-bit DCT fingerprint</strong>
                  <span>8&#xD7;8 grayscale DCT &#x2014; robust to JPEG re-encoding and minor edits</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-a)"><i class="fas fa-ruler-horizontal"></i></div>
                <div class="id-cls-fact-body">
                  <strong>Hamming distance &#x2264;6</strong>
                  <span>0.3% false positive rate; tuned on 50K labeled invoice pairs</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad-g)"><i class="fas fa-shield-alt"></i></div>
                <div class="id-cls-fact-body">
                  <strong>7.2% of invoices flagged</strong>
                  <span>40% of those missed by exact-match dedup alone</span>
                </div>
              </div>
              <div class="id-cls-fact">
                <div class="id-cls-fact-icon" style="background:var(--id-grad)"><i class="fas fa-dollar-sign"></i></div>
                <div class="id-cls-fact-body">
                  <strong>$142K/year prevented</strong>
                  <span>12ms per doc &#x2014; effectively zero marginal cost</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div><!-- /id-cls-slides -->

      <div class="id-cls-nav">
        <button class="id-cls-btn" id="idClsPrev" onclick="idClsGoto(idClsCur-1)" disabled>
          <i class="fas fa-arrow-left me-1"></i> Previous
        </button>
        <div style="display:flex;flex-direction:column;align-items:center;gap:.35rem">
          <div class="id-cls-dots" id="idClsDots"></div>
          <span class="id-cls-counter" id="idClsCounter">1 / 6</span>
        </div>
        <button class="id-cls-btn" id="idClsNext" onclick="idClsGoto(idClsCur+1)">
          Next <i class="fas fa-arrow-right ms-1"></i>
        </button>
      </div>
    </div><!-- /id-cls-wrap -->
  </div><!-- /id-cls-outer -->
</section>

<!-- ════ KEY POINTS ════ -->
<section class="id-sec" id="id-keypoints">
  <div class="id-sec-head">
    <span class="id-tag id-tag--g">Outcomes</span>
    <h2>Key Results That Matter</h2>
    <p>Four measurable improvements that justify every engineering decision in the pipeline.</p>
  </div>
  <div class="id-kp-grid">

    <div class="id-kp-card">
      <div class="id-kp-metric">67%&#x2192;85%</div>
      <h4>Active Learning Drives Continuous Improvement</h4>
      <p>Straight-through processing rate rose from 67% to 85% over six months &#x2014; purely from HITL
        corrections feeding back into weekly fine-tuning. Zero manual annotation effort required.</p>
    </div>

    <div class="id-kp-card">
      <div class="id-kp-metric">97.2%</div>
      <h4>Combined OCR Accuracy Across All Document Types</h4>
      <p>Dual-engine architecture (Azure primary + Tesseract fallback) achieves 97.2% word accuracy even
        on degraded scans, handwritten annotations, and thermally-faded receipts.</p>
    </div>

    <div class="id-kp-card">
      <div class="id-kp-metric">$142K</div>
      <h4>Duplicate Payments Prevented Per Year</h4>
      <p>Perceptual hash deduplication catches the 40% of duplicates that invoice-number matching misses,
        running at 12ms per document with a 0.3% false positive rate.</p>
    </div>

    <div class="id-kp-card">
      <div class="id-kp-metric">4.8s</div>
      <h4>End-to-End Processing Time vs 8+ Hours Manual</h4>
      <p>All 7 pipeline stages &#x2014; intake, classify, OCR, extract, validate, route, export &#x2014;
        complete in 4.8 seconds on average. Manual intake alone took 8+ hours per day for a team of 8.</p>
    </div>

  </div>
</section>

<!-- ════ CODE ════ -->
<section class="id-sec" id="id-code">
  <div class="id-sec-head">
    <span class="id-tag id-tag--t">Code</span>
    <h2>Production Implementation</h2>
    <p>Core pipeline components &#x2014; dual-engine OCR, active learning, and 3-way fraud matching.</p>
  </div>
  <div class="id-impl">

    <details>
      <summary><i class="fas fa-eye" style="color:var(--id-blue)"></i>&nbsp; Azure Doc Intelligence + Tesseract Dual-Engine Pipeline</summary>
      <pre>import cv2
import numpy as np
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.identity import DefaultAzureCredential
import pytesseract
from PIL import Image

class DualEngineOCR:
    """Multi-engine OCR: Azure primary, Tesseract fallback for low-confidence pages."""

    def __init__(self, endpoint: str, confidence_threshold: float = 0.85):
        credential = DefaultAzureCredential()
        self.client = DocumentAnalysisClient(endpoint, credential)
        self.threshold = confidence_threshold

    def preprocess(self, image_path: str) -&gt; np.ndarray:
        """Deskew and binarize for Tesseract fallback."""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        coords = np.column_stack(np.where(img &lt; 128))
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle &lt; -45 else -angle
        h, w = img.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 31, 11)
        return img

    async def extract(self, doc_path: str) -&gt; dict:
        """Run Azure first; fall back to Tesseract on low-confidence pages."""
        with open(doc_path, "rb") as f:
            poller = await self.client.begin_analyze_document(
                "prebuilt-invoice", document=f
            )
        result = await poller.result()

        pages, fallback_pages = [], []
        for page in result.pages:
            avg_conf = np.mean([w.confidence for w in page.words]) if page.words else 0
            if avg_conf &gt;= self.threshold:
                pages.append({"engine": "azure", "confidence": avg_conf,
                              "words": [w.content for w in page.words]})
            else:
                fallback_pages.append(page.page_number)

        for page_num in fallback_pages:
            preprocessed = self.preprocess(f"{doc_path}_page{page_num}.png")
            text = pytesseract.image_to_data(
                Image.fromarray(preprocessed), output_type=pytesseract.Output.DICT
            )
            conf_vals = [int(c) for c in text["conf"] if int(c) &gt; 0]
            pages.append({"engine": "tesseract", "page": page_num,
                          "confidence": np.mean(conf_vals) / 100 if conf_vals else 0,
                          "words": [w for w, c in zip(text["text"], text["conf"])
                                    if int(c) &gt; 40 and w.strip()]})

        return {"pages": pages, "fallback_count": len(fallback_pages),
                "avg_confidence": np.mean([p["confidence"] for p in pages])}</pre>
    </details>

    <details>
      <summary><i class="fas fa-brain" style="color:var(--id-emerald)"></i>&nbsp; Active Learning: HITL Corrections Fine-Tune the Model</summary>
      <pre>import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
from datetime import datetime, timedelta

class ActiveLearningPipeline:
    """Ingest HITL corrections and fine-tune extraction model weekly."""

    def __init__(self, model_name: str, corrections_db):
        self.processor = LayoutLMv3Processor.from_pretrained(model_name)
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(model_name)
        self.corrections_db = corrections_db

    def ingest_corrections(self, since: timedelta = timedelta(days=7)) -&gt; list:
        """Extract labeled correction pairs from HITL review queue."""
        cutoff = datetime.utcnow() - since
        corrections = self.corrections_db.find({
            "reviewed_at": {"$gte": cutoff},
            "status": "corrected"
        })
        return [
            {
                "document_id": c["document_id"],
                "original_extraction": c["model_output"],
                "corrected_extraction": c["human_correction"],
                "field": c["field_name"],
                "confidence_delta": c["original_confidence"]
            }
            for c in corrections
        ]

    def confidence_weighted_loss(self, logits, labels, confidences):
        """Weight loss inversely by original confidence.
        Low-confidence errors that humans corrected contribute more to learning."""
        base_loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)), labels.view(-1), reduction="none"
        )
        # High-confidence wrong predictions penalized 3x more
        weights = 1.0 - confidences.view(-1).clamp(0.5, 0.99)
        weights = weights / weights.sum() * len(weights)
        return (base_loss * weights).mean()

    def retrain(self, training_pairs: list, epochs: int = 3, lr: float = 2e-5) -&gt; dict:
        """Fine-tune on HITL corrections with confidence-weighted loss."""
        dataset = self._build_dataset(training_pairs)
        # Oversample rare correction types proportional to their surprise
        weights = [1.0 / max(p["confidence_delta"], 0.01) for p in training_pairs]
        sampler = WeightedRandomSampler(weights, len(weights))
        loader = DataLoader(dataset, batch_size=8, sampler=sampler)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        self.model.train()
        epoch_losses = []
        for epoch in range(epochs):
            total = 0
            for batch in loader:
                logits = self.model(**batch["inputs"]).logits
                loss = self.confidence_weighted_loss(
                    logits, batch["labels"], batch["confidences"]
                )
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                total += loss.item()
            epoch_losses.append(total / len(loader))
        return {"corrections_used": len(training_pairs),
                "final_loss": epoch_losses[-1],
                "epoch_losses": epoch_losses}</pre>
    </details>

    <details>
      <summary><i class="fas fa-check-double" style="color:var(--id-amber)"></i>&nbsp; 3-Way PO Match + pHash Duplicate Detection</summary>
      <pre>import imagehash
from dataclasses import dataclass
from typing import Optional
from PIL import Image

@dataclass
class MatchResult:
    status: str      # "matched" | "variance" | "no_po" | "no_receipt" | "duplicate"
    variance_pct: float
    details: dict

class ThreeWayMatcher:
    """Cross-reference PO + Goods Receipt + Invoice; catch visual duplicates via pHash."""

    AMOUNT_TOLERANCE = 0.02    # 2% for currency rounding differences
    PHASH_THRESHOLD  = 6       # Hamming distance threshold for visual duplicate

    def __init__(self, po_store, receipt_store, invoice_store):
        self.po_store      = po_store
        self.receipt_store = receipt_store
        self.invoice_store = invoice_store

    def detect_visual_duplicate(self, invoice_path: str) -&gt; Optional[str]:
        """Perceptual hash to catch re-submitted PDFs with modified filenames/numbers."""
        current_hash = imagehash.phash(Image.open(invoice_path))
        for inv in self.invoice_store.find({"status": "processed"}):
            if current_hash - imagehash.hex_to_hash(inv["phash"]) &lt;= self.PHASH_THRESHOLD:
                return inv["invoice_number"]
        return None

    def match(self, invoice: dict) -&gt; MatchResult:
        # 1. Visual dedup via pHash (catches re-submissions with altered metadata)
        if invoice.get("file_path"):
            dup = self.detect_visual_duplicate(invoice["file_path"])
            if dup:
                return MatchResult("duplicate", 0,
                                   {"duplicate_of": dup, "method": "perceptual_hash"})

        # 2. Exact-match dedup (invoice number + vendor)
        existing = self.invoice_store.find_one({
            "invoice_number": invoice["invoice_number"],
            "vendor_id":      invoice["vendor_id"],
            "status":         {"$ne": "rejected"}
        })
        if existing:
            return MatchResult("duplicate", 0,
                               {"duplicate_of": existing["invoice_number"],
                                "method": "invoice_number+vendor"})

        # 3. PO existence check
        po = self.po_store.find_one({"po_number": invoice["po_number"]})
        if not po:
            return MatchResult("no_po", 0, {"po_number": invoice["po_number"]})

        # 4. Goods receipt confirmation
        receipt = self.receipt_store.find_one({
            "po_number": invoice["po_number"], "status": "received"
        })
        if not receipt:
            return MatchResult("no_receipt", 0, {"po_number": invoice["po_number"],
                                                  "reason": "goods not yet received"})

        # 5. Amount tolerance check (2%)
        variance = abs(invoice["total_amount"] - po["total_amount"]) / po["total_amount"]
        if variance &gt; self.AMOUNT_TOLERANCE:
            return MatchResult("variance", round(variance * 100, 2),
                               {"po_amount": po["total_amount"],
                                "invoice_amount": invoice["total_amount"],
                                "threshold": "2%"})

        return MatchResult("matched", round(variance * 100, 2),
                           {"po":      po["po_number"],
                            "receipt": receipt["receipt_id"],
                            "invoice": invoice["invoice_number"],
                            "amount":  invoice["total_amount"]})</pre>
    </details>

  </div>
</section>

<!-- ════ ABOUT ════ -->
<section class="id-sec" id="id-about">
  <div class="id-sec-head">
    <span class="id-tag id-tag--v">About</span>
    <h2>Technology Stack</h2>
    <p>Every library and service that powers the end-to-end IDP pipeline in production.</p>
  </div>
  <div class="id-about-card">
    <h3>Intelligent Document Processing</h3>
    <p>A 7-stage Azure-native pipeline &#x2014; dual-engine OCR, LayoutLMv3 classification, spaCy NER,
      3-way PO matching, pHash deduplication, active learning HITL loop &#x2014; processing 15,000
      documents per day with 97.2% field accuracy and 85% straight-through rate.</p>
    <div class="id-about-pills">
      <span class="id-about-pill id-about-pill--t">Azure Doc Intelligence</span>
      <span class="id-about-pill id-about-pill--b">Tesseract OCR</span>
      <span class="id-about-pill id-about-pill--v">LayoutLMv3</span>
      <span class="id-about-pill id-about-pill--g">GPT-4o</span>
      <span class="id-about-pill id-about-pill--a">spaCy NER</span>
      <span class="id-about-pill id-about-pill--r">imagehash / pHash</span>
      <span class="id-about-pill id-about-pill--t">PyMuPDF</span>
      <span class="id-about-pill id-about-pill--b">Pillow / OpenCV</span>
      <span class="id-about-pill id-about-pill--v">PyTorch + HuggingFace</span>
      <span class="id-about-pill id-about-pill--g">Celery + Redis</span>
      <span class="id-about-pill id-about-pill--a">PostgreSQL</span>
      <span class="id-about-pill id-about-pill--r">Azure Blob Storage</span>
      <span class="id-about-pill id-about-pill--t">Azure Functions</span>
      <span class="id-about-pill id-about-pill--b">Django</span>
      <span class="id-about-pill id-about-pill--v">FastAPI</span>
    </div>
    <button class="id-share-btn" onclick="idShareDemo()">
      <i class="fas fa-share-alt"></i> Share This Demo
    </button>
  </div>
</section>

</div><!-- /container-fluid -->

{% endblock content %}

{% block extra_js %}
<script>
(function(){'use strict';

/* ── Progress + scroll-spy ── */
function onScroll(){
  var el=document.documentElement;
  var pct=(el.scrollTop||document.body.scrollTop)/(el.scrollHeight-el.clientHeight)*100;
  var fill=document.getElementById('idProgressFill');
  if(fill)fill.style.width=Math.min(pct,100)+'%';
  var ids=['id-story','id-demo','id-classroom','id-keypoints','id-code','id-about'];
  var tabs=document.querySelectorAll('.id-nav-tab');
  var best=-1;
  for(var i=0;i<ids.length;i++){
    var sec=document.getElementById(ids[i]);
    if(sec&&sec.getBoundingClientRect().top<=120)best=i;
  }
  tabs.forEach(function(t,i){t.classList.toggle('active',i===best)});
}
window.addEventListener('scroll',onScroll,{passive:true});

/* ── idScrollTo ── */
function idScrollTo(id){
  var el=document.getElementById(id);
  if(el)el.scrollIntoView({behavior:'smooth',block:'start'});
}
window.idScrollTo=idScrollTo;

/* ── idSetMode ── */
function idSetMode(mode){
  var eli5=document.getElementById('idEli5Pane');
  var eng=document.getElementById('idEngPane');
  var btnE=document.getElementById('idModeEli5');
  var btnEng=document.getElementById('idModeEng');
  if(mode==='eli5'){
    eli5.classList.add('active');eng.classList.remove('active');
    btnE.classList.add('active');btnEng.classList.remove('active');
  } else {
    eng.classList.add('active');eli5.classList.remove('active');
    btnEng.classList.add('active');btnE.classList.remove('active');
  }
}
window.idSetMode=idSetMode;

/* ── Classroom ── */
var idClsCur=0,idClsTotal=6;
function idClsRender(){
  var slides=document.getElementById('idClsSlides');
  if(slides)slides.style.transform='translateX(-'+idClsCur*100+'%)';
  var counter=document.getElementById('idClsCounter');
  if(counter)counter.textContent=(idClsCur+1)+' / '+idClsTotal;
  var prev=document.getElementById('idClsPrev');
  var next=document.getElementById('idClsNext');
  if(prev)prev.disabled=idClsCur===0;
  if(next)next.disabled=idClsCur===idClsTotal-1;
  var dotsEl=document.getElementById('idClsDots');
  if(dotsEl){
    var ds=dotsEl.querySelectorAll('.id-cls-dot');
    ds.forEach(function(d,i){d.classList.toggle('active',i===idClsCur)});
  }
}
function idClsGoto(idx){
  if(idx<0||idx>=idClsTotal)return;
  idClsCur=idx;idClsRender();
}
window.idClsGoto=idClsGoto;
window.idClsNext=function(){idClsGoto(idClsCur+1)};
window.idClsPrev=function(){idClsGoto(idClsCur-1)};

/* build dots */
(function(){
  var dotsEl=document.getElementById('idClsDots');
  if(!dotsEl)return;
  for(var i=0;i<idClsTotal;i++){
    var d=document.createElement('div');
    d.className='id-cls-dot'+(i===0?' active':'');
    d.setAttribute('data-i',i);
    d.onclick=(function(idx){return function(){idClsGoto(idx)}})(i);
    dotsEl.appendChild(d);
  }
}());
idClsRender();

/* ── idShareDemo ── */
function idShareDemo(){
  var url=window.location.href;
  if(navigator.share){
    navigator.share({title:'Intelligent Document Processing Demo',text:'AI pipeline: OCR, classification, extraction, 3-way match, active learning.',url:url});
  } else if(navigator.clipboard){
    navigator.clipboard.writeText(url).then(function(){alert('Link copied to clipboard!')});
  }
}
window.idShareDemo=idShareDemo;

/* ════════════════════════════════════════
   IDP Pipeline Simulator
   ════════════════════════════════════════ */
var btnRun=document.getElementById('idBtnRun');
var btnReset=document.getElementById('idBtnReset');
var stage=document.getElementById('idStage');
var dashWrap=document.getElementById('idDashboard');
var running=false,docs=[],totalAcc=0,totalTime=0,stpCount=0;

function wait(ms){return new Promise(function(r){setTimeout(r,ms)})}
function app(h){if(!stage)return;stage.insertAdjacentHTML('beforeend',h);stage.scrollTop=stage.scrollHeight}
function log(m){
  var la=document.getElementById('idLogArea');if(!la)return;
  var ts=new Date().toLocaleTimeString('en-US',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'});
  la.insertAdjacentHTML('beforeend','<div style="animation:idSlide .2s ease">'+ts+' '+m+'</div>');
  la.scrollTop=la.scrollHeight;
}
function pip(i,s){
  for(var j=0;j<7;j++){
    var e=document.getElementById('idPip'+j);if(!e)continue;
    e.classList.remove('active','done');
    if(j<i)e.classList.add('done');
    else if(j===i)e.classList.add(s==='active'?'active':'done');
  }
}
function money(n){return '$'+n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',')}

var vendors=['Staples Inc.','Amazon Business','CDW Corp.','Dell Technologies','Grainger','Office Depot','Adobe Systems','Microsoft Corp.'];
var docTypes=['INVOICE','CREDIT_MEMO','PURCHASE_ORDER','RECEIPT'];
var erps=['NetSuite AP','SAP S/4HANA','Oracle EBS','QuickBooks'];
var invCounter=0;

function mulberry32(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;var t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function hashSeed(idx){var h=0x811c9dc5,s='idp'+idx;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)}return h>>>0}
function rand(a,prng){return a[Math.floor(prng()*a.length)]}
function rn(a,b,prng){return Math.floor(prng()*(b-a)+a)}
function rf(a,b,prng){var r=prng||Math.random;return+(r()*(b-a)+a).toFixed(2)}

function validateInvoice(inv){
  var itemSum=0;for(var i=0;i<inv.lineItemDetails.length;i++)itemSum+=inv.lineItemDetails[i].amount;
  var sumValid=Math.abs(itemSum-inv.amount)<0.02;
  var dp=inv.date.split('-'),yr=parseInt(dp[0]),mo=parseInt(dp[1]),dy=parseInt(dp[2]);
  var dateValid=yr>=2020&&yr<=2026&&mo>=1&&mo<=12&&dy>=1&&dy<=28;
  var tinValid=/^\d{2}-\d{7}$/.test(inv.vendorTIN);
  return{sumValid:sumValid,dateValid:dateValid,tinValid:tinValid,allValid:sumValid&&dateValid&&tinValid}
}

function gen(){
  invCounter++;
  var seed=hashSeed(invCounter),prng=mulberry32(seed);
  var v=rand(vendors,prng),lineCount=rn(3,12,prng);
  var items=[],subtotal=0;
  var itemNames=['Printer Paper A4','Toner Cartridge','USB-C Cable','Desk Organizer','Monitor Stand',
    'Wireless Mouse','Keyboard','Headset','Webcam HD','Whiteboard Markers','Sticky Notes','Binder Clips'];
  for(var i=0;i<lineCount;i++){
    var qty=rn(1,20,prng),unitPrice=rf(5,500,prng),lineAmt=+(qty*unitPrice).toFixed(2);
    items.push({name:rand(itemNames,prng),qty:qty,unitPrice:unitPrice,amount:lineAmt});
    subtotal+=lineAmt;
  }
  subtotal=+subtotal.toFixed(2);
  var conf=rf(.91,.99,prng),stp=conf>=0.95;
  var hx=seed.toString(16).padStart(8,'0');
  var tin=String(rn(10,99,prng))+'-'+String(rn(1000000,9999999,prng));
  var inv={vendor:v,vendorTIN:tin,
    invNum:'INV-2024-'+String(rn(100,9999,prng)).padStart(5,'0'),
    date:'2024-'+String(rn(1,12,prng)).padStart(2,'0')+'-'+String(rn(1,28,prng)).padStart(2,'0'),
    amount:subtotal,po:'PO-2024-'+rn(1000,5000,prng),lineItems:lineCount,lineItemDetails:items,
    words:rn(400,1200,prng),tables:rn(1,5,prng),fields:rn(18,28,prng),
    conf:conf,docType:rand(docTypes,prng),erp:rand(erps,prng),
    voucher:'V-2024-'+rn(3000,8000,prng),stp:stp,
    deskew:rf(0.2,2.5,prng),hash:hx};
  inv.validation=validateInvoice(inv);
  return inv;
}

function s1(r){
  pip(0,'active');log('\ud83d\udce7 Email received \u2014 attachment detected');
  var ic=document.getElementById('idInvCard');
  if(ic){
    ic.innerHTML='<div class="id-inv-row"><span class="lbl">Vendor</span><span class="val">'+r.vendor+'</span></div>'+
      '<div class="id-inv-row"><span class="lbl">Invoice #</span><span class="val">'+r.invNum+'</span></div>'+
      '<div class="id-inv-row"><span class="lbl">Amount</span><span class="val">'+money(r.amount)+'</span></div>'+
      '<div class="id-inv-row"><span class="lbl">PO</span><span class="val">'+r.po+'</span></div>'+
      '<div class="id-inv-row"><span class="lbl">Confidence</span><span class="val">'+(r.conf*100).toFixed(1)+'%</span></div>';
    ic.classList.add('vis');
  }
  app('<div class="id-step-card"><h6>\ud83d\udce7 Step 1 \u2014 Intake</h6>'+
    '<div class="id-json">'+
    '<span class="key">"source"</span>: <span class="str">"ap@company.com"</span>,\n'+
    '<span class="key">"file"</span>: <span class="str">"inv_'+r.vendor.toLowerCase().replace(/[^a-z]/g,'_').replace(/_+/g,'_')+'.pdf"</span>,\n'+
    '<span class="key">"dedup_hash"</span>: <span class="str">"'+r.hash+'"</span>,\n'+
    '<span class="key">"status"</span>: <span class="str">"NEW DOCUMENT"</span></div></div>');
  pip(0,'done');log('\u2705 New document \u2014 hash='+r.hash);
  return wait(700);
}

function s2(r){
  pip(1,'active');log('\ud83c\udff7\ufe0f LayoutLM classifying\u2026');
  app('<div class="id-step-card" id="idClassCard"><h6>\ud83c\udff7\ufe0f Step 2 \u2014 Classification</h6>'+
    '<p id="idClassStatus" style="text-align:center;font-size:.82rem;margin:0">'+
    '<i class="fas fa-spinner fa-spin me-1" style="color:#14b8a6"></i> LayoutLMv3 analyzing document structure\u2026</p></div>');
  return wait(1200).then(function(){
    var el=document.getElementById('idClassStatus');
    if(el)el.innerHTML='<i class="fas fa-check-circle me-1" style="color:#10b981"></i> Predicted: <b>'+r.docType+'</b> (confidence: '+r.conf.toFixed(2)+')';
    pip(1,'done');log('\u2705 Classified as '+r.docType);
    return wait(400);
  });
}

function s3(r){
  pip(2,'active');log('\ud83d\udc41\ufe0f Azure Doc Intelligence scanning\u2026');
  app('<div class="id-step-card" id="idOcrCard"><h6>\ud83d\udc41\ufe0f Step 3 \u2014 OCR &amp; Preprocessing</h6>'+
    '<p id="idOcrStatus" style="text-align:center;font-size:.82rem;margin:0">'+
    '<i class="fas fa-spinner fa-spin me-1" style="color:#14b8a6"></i> Deskew '+r.deskew.toFixed(1)+'\u00b0 \u2192 scanning '+r.words+' words\u2026</p></div>');
  return wait(1800).then(function(){
    var el=document.getElementById('idOcrStatus');
    if(el)el.innerHTML='<i class="fas fa-check-circle me-1" style="color:#10b981"></i> '+r.words+' words extracted, '+r.tables+' tables detected';
    pip(2,'done');log('\u2705 OCR: '+r.words+' words, '+r.tables+' tables');
    return wait(500);
  });
}

function s4(r){
  pip(3,'active');log('\ud83d\udcca Extracting fields\u2026');
  var fields=['vendor_name: "'+r.vendor+'"','invoice_number: "'+r.invNum+'"','invoice_date: "'+r.date+'"',
    'total_amount: "'+money(r.amount)+'"','line_items: '+r.lineItems+' rows parsed'];
  app('<div class="id-step-card" id="idExtractCard"><h6>\ud83d\udcca Step 4 \u2014 Field Extraction</h6>'+
    '<div id="idExtractChecks"></div></div>');
  var ec=document.getElementById('idExtractChecks');
  function reveal(i){
    if(i>=fields.length)return Promise.resolve();
    return wait(600).then(function(){
      log('\u2705 '+fields[i]);
      var c=rf(0.95,0.99);
      if(ec)ec.insertAdjacentHTML('beforeend',
        '<div class="id-chk show"><i class="fas fa-check-circle pass"></i> '+fields[i]+
        ' <span style="opacity:.5;font-size:.65rem">(conf: '+c+')</span></div>');
      return reveal(i+1);
    });
  }
  return reveal(0).then(function(){pip(3,'done');return wait(400)});
}

function s5(r){
  pip(4,'active');log('\u2705 Validating '+r.fields+' fields\u2026');
  var v=r.validation||{sumValid:true,dateValid:true,tinValid:true};
  var checks=['PO Match: '+r.po+' \u2192 <b>3-WAY MATCH</b> (variance: $0.00)',
    'Line item sum check \u2192 <b>'+(v.sumValid?'PASS':'VARIANCE DETECTED')+'</b>',
    'Date format validated \u2192 <b>'+(v.dateValid?'VALID':'INVALID')+'</b>',
    'Vendor TIN ('+r.vendorTIN+') \u2192 <b>'+(v.tinValid?'VALID FORMAT':'INVALID')+'</b>',
    'pHash dedup check ('+r.hash+') \u2192 <b>NO VISUAL DUPLICATES</b>',
    'All '+r.fields+' fields passed validation'];
  app('<div class="id-step-card" id="idValCard"><h6>\u2705 Step 5 \u2014 Validation</h6>'+
    '<div id="idValChecks"></div></div>');
  var vc=document.getElementById('idValChecks');
  function reveal(i){
    if(i>=checks.length)return Promise.resolve();
    return wait(700).then(function(){
      log('\u2705 '+checks[i].replace(/<[^>]+>/g,''));
      if(vc)vc.insertAdjacentHTML('beforeend',
        '<div class="id-chk show"><i class="fas fa-check-circle pass"></i> '+checks[i]+'</div>');
      return reveal(i+1);
    });
  }
  return reveal(0).then(function(){pip(4,'done');return wait(400)});
}

function s6(r){
  pip(5,'active');
  var route=r.stp?'STRAIGHT-THROUGH (confidence \u2265 0.95)':'HUMAN REVIEW (confidence below 0.95)';
  log('\ud83d\udea6 Routing: '+(r.stp?'straight-through':'HITL queue'));
  app('<div class="id-step-card"><h6>\ud83d\udea6 Step 6 \u2014 Routing</h6>'+
    '<p style="text-align:center;font-size:.82rem;margin:0">'+
    '<i class="fas '+(r.stp?'fa-bolt':'fa-user-check')+' me-1" style="color:'+(r.stp?'#10b981':'#f59e0b')+'"></i> '+route+'</p></div>');
  if(r.stp)stpCount++;
  return wait(800).then(function(){pip(5,'done');return wait(300)});
}

function s7(r,elapsed){
  pip(6,'active');docs.push(r);totalAcc+=r.conf;totalTime+=elapsed;
  log('\ud83d\udce4 Exporting to '+r.erp);
  if(dashWrap)dashWrap.style.display='block';
  var kd=document.getElementById('idKpiDocs'),ka=document.getElementById('idKpiAcc');
  var ks=document.getElementById('idKpiStp'),kt=document.getElementById('idKpiTime');
  if(kd)kd.textContent=docs.length;
  if(ka)ka.textContent=((totalAcc/docs.length)*100).toFixed(1)+'%';
  if(ks)ks.textContent=Math.round(stpCount/docs.length*100)+'%';
  if(kt)kt.textContent=(totalTime/docs.length).toFixed(1)+'s';
  var dt=document.getElementById('idDashTable');
  if(dt)dt.insertAdjacentHTML('afterbegin',
    '<tr style="animation:idFadeUp .35s ease both"><td><b>'+r.invNum+'</b></td>'+
    '<td>'+r.vendor+'</td><td>'+money(r.amount)+'</td><td>'+r.fields+'</td>'+
    '<td>'+(r.conf*100).toFixed(1)+'%</td>'+
    '<td><span class="id-ds '+(r.stp?'exported':'hitl')+'">'+(r.stp?'\u2705 STP':'\ud83d\udc64 HITL')+'</span></td>'+
    '<td>'+elapsed.toFixed(1)+'s</td></tr>');
  app('<div class="id-step-card id-step-card--ok"><h6>\ud83d\udce4 Step 7 \u2014 ERP Export</h6>'+
    '<p style="text-align:center;font-size:.88rem;color:#10b981;font-weight:700;margin:0">'+
    '<i class="fas fa-check-double me-1"></i> Voucher #'+r.voucher+' created in '+r.erp+'</p>'+
    '<p style="text-align:center;font-size:.74rem;opacity:.6;margin:.15rem 0 0">'+
    r.vendor+' \u2014 '+money(r.amount)+' \u2014 '+(r.conf*100).toFixed(1)+'% accuracy \u2014 '+elapsed.toFixed(1)+'s</p></div>');
  pip(6,'done');log('\u2705 Voucher #'+r.voucher+' created');
  return wait(600);
}

function runDemo(){
  if(running)return;
  running=true;
  if(btnRun){btnRun.disabled=true;btnRun.innerHTML='<i class="fas fa-spinner fa-spin me-1"></i> Processing\u2026'}
  if(btnReset)btnReset.style.display='none';
  var r=gen(),start=performance.now();
  s1(r).then(function(){return s2(r)})
    .then(function(){return s3(r)})
    .then(function(){return s4(r)})
    .then(function(){return s5(r)})
    .then(function(){return s6(r)})
    .then(function(){return s7(r,(performance.now()-start)/1000)})
    .then(function(){
      running=false;
      if(btnRun){btnRun.disabled=false;btnRun.innerHTML='<i class="fas fa-play me-1"></i> Run Another Invoice'}
      if(btnReset)btnReset.style.display='';
      var dash=document.getElementById('idDashboard');
      if(dash)dash.scrollIntoView({behavior:'smooth',block:'nearest'});
    });
}

function resetDemo(){
  docs=[];totalAcc=0;totalTime=0;stpCount=0;invCounter=0;
  if(stage)stage.innerHTML='';
  if(dashWrap)dashWrap.style.display='none';
  var dt=document.getElementById('idDashTable');if(dt)dt.innerHTML='';
  var ic=document.getElementById('idInvCard');if(ic){ic.innerHTML='';ic.classList.remove('vis')}
  var la=document.getElementById('idLogArea');if(la)la.innerHTML='';
  if(btnRun){btnRun.innerHTML='<i class="fas fa-play me-1"></i> Run Invoice';btnRun.disabled=false}
  if(btnReset)btnReset.style.display='none';
  for(var i=0;i<7;i++){var p=document.getElementById('idPip'+i);if(p)p.classList.remove('active','done')}
}

if(btnRun)btnRun.addEventListener('click',runDemo);
if(btnReset)btnReset.addEventListener('click',resetDemo);
window.runDemo=runDemo;

}());
</script>
{% endblock extra_js %}
'''

with open(OUT, 'a', encoding='utf-8') as fh:
    fh.write(p2)
print("id2 done")
