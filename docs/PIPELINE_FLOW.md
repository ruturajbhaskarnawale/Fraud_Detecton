# End-to-End Pipeline Flow

This document details the step-by-step processing of a KYC verification request.

## 1. Request Initiation
The user submits a request via the `/verify` endpoint with:
- `id_card`: Image of the identification document.
- `selfie` (Optional): A live photo of the user.

## 2. Preprocessing & Quality Assurance
- **File Handling**: PDFs are converted to high-resolution images.
- **Normalizer**: Fixes orientation and scales images to a standard size.
- **Quality Checker**:
  - Checks if the image is too blurry using the Laplacian variance method.
  - Checks for under-exposure or over-exposure.
  - **Action**: If quality is below the threshold, the pipeline returns a `FAILED` status with specific issues.

## 3. OCR & Information Extraction
- **Text Localization**: `EasyOCR` identifies text regions.
- **Document Classification**:
  - Looks for keywords like "Income Tax Department" (PAN) or "Unique Identification Authority" (Aadhaar).
- **Attribute Extraction**:
  - Regex patterns extract the **ID Number**, **Name**, and **DOB**.

## 4. Biometric Matching (Face)
If a selfie is provided:
1.  **Face Localization**: OpenCV Haar Cascades detect faces in both the ID card and the selfie.
2.  **Embedding Generation**: The ResNet18 model generates 512-dimensional vectors for both faces.
3.  **Similarity calculation**: Cosine similarity is computed between vectors.
4.  **Liveness Detection**: Simple heuristic check for face pose and blinking (if video) or lighting consistency (if image).

## 5. Multi-Signal Fraud Audit
- **ELA (Error Level Analysis)**: Identifies if bits have been changed and re-saved at different compression levels.
- **Data Mismatch**: Compares the name/DOB on the ID card with other secondary documents if provided.
- **Duplicate Check**: Compares the pHash of the current image against the database of previous `VerificationRecords`.

## 6. Scoring & Final Decision
The `RiskScoringEngine` aggregates all signals:
- **Major Red Flags**: Tampering detected, Face mismatch, ID in blacklist.
- **Minor Red Flags**: Poor quality, OCR low confidence.
- **Output**:
  - `Decision`: CLEAR, CAUTION, or REJECT.
  - `Risk Score`: 0.0 to 1.0 (Higher is riskier).
  - `Reasons`: List of specific flags raised.
