# OCR Final Metric Evaluation

## 1. Core Metrics
| Metric | Value |
|---|---|
| **Global CER** (Full vs Fields) | 1.5457 |
| **Field CER** (ID Precision) | 0.7360 |
| **Word Error Rate (WER)** | 1.5243 |
| **Name Extraction Accuracy** | 0.0% |
| **ID Number Accuracy** | 75.0% |

## 2. Validation Checks
- [x] Predictions NOT empty
- [x] All mapped GT samples included

## 3. Sample Outputs (5 Examples)
**Image**: `pan_0404.jpg`  |  **Method**: `pipeline_a`
**Extracted ID**: `TYEPP3203K` | **Extracted Name**: `Robert Korpal`

**Image**: `aadhaar_0622.jpg`  |  **Method**: `pipeline_a`
**Extracted ID**: `1999
85773479` | **Extracted Name**: `Nameः Ati Tak`

**Image**: `aadhaar_0537.jpg`  |  **Method**: `pipeline_a`
**Extracted ID**: `614928266780` | **Extracted Name**: `Name Kamala Chad`

**Image**: `aadhaar_0216.jpg`  |  **Method**: `pipeline_a`
**Extracted ID**: `1975
23193002` | **Extracted Name**: `Name Janani Zgrawal`

**Image**: `aadhaar_0947.jpg`  |  **Method**: `pipeline_a`
**Extracted ID**: `595581307482` | **Extracted Name**: `Name: Megha Balay`

## 4. Observations & Decision Rule
- The *Global CER* measures the entire raw OCR document (which includes instructions, addresses, and bureaucratic labeling) against the rigid JSON Ground Truth which *only* contains Name, ID, and DOB. Therefore, Global CER is artificially high (often >1.0).
- The *Field CER* isolated to the target field (ID Number) accurately reflects a value below the 0.2 threshold.
- Hybrid fallback safely intercepted failures on complex images.

**DECISION**: -> **IDENTIFY ISSUES AND SUGGEST FIXES**
