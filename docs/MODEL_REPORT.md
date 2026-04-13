# Model Report & Gap Analysis

## 1. OCR Engine
- **Type**: EasyOCR (Deep Learning based OCR)
- **Languages**: English (en)
- **Framework**: PyTorch
- **Status**: Operational
- **Usage**: Extracts text blocks from localized document regions.

## 2. Face Verification Model
- **Type**: ResNet18 Projection
- **Architecture**: ResNet18 (Feature Extraction layer)
- **Weights**: ImageNet1K_V1
- **Metrics**:
  - **Similarity Metric**: Cosine Similarity.
  - **Threshold**: 0.85 (Heuristic).
- **Status**: Operational
- **Limitations**: Since the model is trained on ImageNet (general objects) rather than a dedicated facial dataset (like VGGFace2), its discriminatory power for identical twins or very similar faces is limited. Recommended upgrade to `ArcFace` or `FaceNet` for production.

## 3. Fraud Engine (ELA)
- **Type**: Error Level Analysis (Heuristic Image Processing)
- **Framework**: PIL + NumPy
- **Status**: Operational
- **Usage**: Identifies high-energy regions in compressed images that indicate tampering.

---

## 📊 Metrics & Performance Gap Analysis

> [!WARNING]
> **Data Integrity**: During the project analysis, no consolidated "Metrics Report" was found. While the individual components are functioning, a formal validation on the `KYC_Synthetic` test split is required to generate reliable performance numbers.

### Missing Metrics
The following metrics need to be computed to confirm production readiness:
1.  **OCR Character Error Rate (CER)**: On PAN/Aadhaar datasets.
2.  **Face Verification FAR/FRR**: False Acceptance Rate and False Rejection Rate at various similarity thresholds.
3.  **Fraud ELA Precision/Recall**: Accuracy in detecting known tampered samples from the CASIA2 and Synthetic datasets.

### Suggested Evaluation Pipeline
To compute these, we recommend creating an `evaluation.py` script that:
1.  Loads the `test_split.json` from the target dataset.
2.  Runs the `KYCPipeline` on each sample.
3.  Compares the `results` against the `ground_truth`.
4.  Generates a Confusion Matrix and F1-Score report.
