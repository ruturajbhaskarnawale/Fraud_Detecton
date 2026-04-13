# Dataset Documentation

The system utilizes several datasets for development, testing, and validation of individual components. All original files are stored in `data/raw/`.

## 1. KYC Synthetic Dataset
- **Purpose**: Primary dataset for PAN and Aadhaar extraction logic.
- **Type**: Images + Structured JSON Metadata.
- **Content**: 1000+ synthetic Indian ID documents with realistic augmentations (blur, noise, rotation).
- **Fraud Inclusion**: Includes tampered text and face mismatches to test fraud detection.

## 2. LFW (Labeled Faces in the Wild)
- **Purpose**: Face Verification benchmarking.
- **Type**: Portraits (Images).
- **Source**: University of Massachusetts, Amherst.
- **Usage**: Used as a reference for cross-person matching during development.

## 3. CASIA2 (Ground Truth)
- **Purpose**: Tampering Detection (ELA) validation.
- **Type**: Manipulated Images + Ground Truth Masks.
- **Usage**: Testing the sensitivity of the Error Level Analysis engine.

## 4. MIDV-500
- **Purpose**: Mobile ID Capture validation.
- **Type**: Video frames of ID documents in varied environmental conditions.
- **Usage**: Benchmarking the OCR engine's robustness against glare and perspective distortion.

## 5. FUNSD
- **Purpose**: Form Understanding and Document Parsing.
- **Type**: Scanned Documents + Annotations.
- **Usage**: Used to train/tune the field extraction logic for complex form layouts.

## 6. SROIE (Scanned Receipts OCR and Information Extraction)
- **Purpose**: OCR Engine tuning.
- **Type**: Scanned Receipts + Text ground truth.
- **Usage**: Benchmarking the `EasyOCR` engine's character recognition accuracy.

---

## Preprocessing Summary
For all datasets, a normalization pipeline is applied:
1.  **Grayscale conversion** (where applicable).
2.  **Adaptive Thresholding** for OCR enhancement.
3.  **Bilateral Filtering** to remove noise while preserving edges for face detection.
4.  **ELA Transformation** specifically for the Fraud Engine.
