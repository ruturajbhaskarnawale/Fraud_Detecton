# Data Processing Report

This report outlines the transformation of raw datasets into production-ready inputs for the KYC pipeline.

## 1. Unified Preprocessing Pipeline
To ensure high model accuracy, all images undergo a multi-stage unified preprocessing flow:

| Stage | Algorithm | Purpose |
| :--- | :--- | :--- |
| **Noise Reduction** | Bilateral Filter | Edge-preserving smoothing to remove sensor noise without blurring text boundaries. |
| **Contrast Enhancement** | CLAHE | Contrast Limited Adaptive Histogram Equalization to normalize lighting conditions. |
| **Resizing** | Lanczos4 Interpolation | Standardization to 1280px width to maintain detail for OCR. |
| **Fraud Analysis** | ELA Transform | Error Level Analysis map generation at 90% quality level. |

## 2. Dataset Partitioning
The system was trained and validated using a structured split of the **KYC Synthetic Dataset**:

- **Training Set (80%)**: Used to extract signals for the RandomForest fraud classifier.
- **Test Set (20%)**: 283 samples reserved for final accuracy reporting (ID-matched to ensure no leakage).

## 3. OCR-Specific Preprocessing
For the OCR engine, a secondary adaptive thresholding step was added:
- **Technique**: Adaptive Gaussian Thresholding (11x11 block size).
- **Result**: Significant reduction in background shadows from physical document scans.

## 4. Biometric Preprocessing
- **Face Alignment**: Automatic rotation and cropping of facial regions using OpenCV Cascades.
- **Normalization**: RGB normalization to ImageNet mean/std for ResNet50 compatibility.

---
*Report generated on 2026-04-13*
