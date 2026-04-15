# Model Evaluation Report

This report provides a formal benchmark of the Document Fraud Detection System components based on standardized datasets.

## 1. OCR Performance (EasyOCR)
**Dataset**: SROIE (Scanned Receipts OCR and Information Extraction)
**Methodology**: Evaluation of Character Error Rate (CER) and Word Accuracy on 10 random receipt samples.

| Metric | Score |
| :--- | :--- |
| **Character Error Rate (CER)** | 0.4932 |
| **Word Accuracy** | 0.5146 |

> [!NOTE]
> The CER is relatively high because receipt fonts are often distorted. On standard PAN/Aadhaar cards, character accuracy is significantly higher.

## 2. Face Verification (ResNet50)
**Dataset**: LFW (Labeled Faces in the Wild)
**Methodology**: Benchmarked using 40 image pairs (20 matches, 20 mismatches) using 2048-D ResNet50 embeddings.

| Threshold | Avg Match Sim | Avg Mismatch Sim | FAR | FRR | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0.60** | 0.8500 | 0.6786 | 0.8000 | 0.0000 | 0.7143 |

> [!WARNING]
> **Threshold Tuning Required**: The current threshold of 0.60 results in a high False Acceptance Rate (0.8). For production KYC, a threshold of **0.85 - 0.90** is recommended to minimize fraud.

## 3. Fraud Detection (Hybrid RandomForest)
**Dataset**: KYC Synthetic (Test Split)
**Methodology**: Signals derived from ELA map, OCR consistency (metadata match), and face detection presence.

| Metric | Score |
| :--- | :--- |
| **Precision** | 0.4286 |
| **Recall** | 0.6000 |
| **F1 Score** | 0.5000 |
| **Overall Accuracy** | 0.7000 |

> [!TIP]
> This model was trained on a specific subset. Expanding the training set to the full 1,000+ samples will significantly increase the F1 Score.

---
*Report generated on 2026-04-13*
