# Veridex AI 🛡️
> **Production-Grade AI Document Fraud Detection & KYC Verification Platform**

[![Stack](https://img.shields.io/badge/Stack-Fullstack-blue.svg)](https://github.com/ruturajbhaskarnawale/Fraud_Detection)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15.0-black.svg)](https://nextjs.org/)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Veridex AI is an advanced identity verification ecosystem engineered to detect sophisticated document forgery and identity fraud in real-time. By orchestrating **Computer Vision (EasyOCR)**, **Biometric Matching (InsightFace/ArcFace)**, and **Digital Forensics (ELA)**, Veridex provides a multi-layered defense pipeline suitable for fintech, banking, and high-trust digital onboarding.

---

## 📸 Preview & Demo

| Dashboard Interface | Verification Workflow |
| :--- | :--- |
| ![Dashboard Overview](screenshots/results_page.png) | ![Verification Process](screenshots/verify_page.png) |

---

## 🔄 System Workflow

Veridex employs a **Sequential Multi-Signal Fusion** architecture to process every verification request:

```mermaid
graph TD
    A[User Upload: ID + Selfie] --> B[Quality Gate: Blur/Lighting/Size Check]
    B --> C{Good Quality?}
    C -- Yes --> D[OCR Extraction: EasyOCR]
    C -- No --> E[Reject/Request Retake]
    D --> F[Face Matching: ArcFace 1:1]
    F --> G[Forensic Analysis: ELA + Perceptual Hashing]
    G --> H[Risk Scoring Engine: Weighted Logic]
    H --> I[Final Decision: VALID / SUSPICIOUS / REJECTED]
```

### The Pipeline Steps:
1.  **Ingestion & Quality Gate**: Validates forensic suitability (resolution, lighting, and blur).
2.  **OCR & Classification**: Identifies document type (Aadhaar/PAN) and extracts key PII.
3.  **Biometric Verification**: Computes face embeddings from the ID and Selfie for comparison.
4.  **Forensic Deep-Dive**: Performs Error Level Analysis (ELA) to detect compression inconsistencies (tampering).
5.  **Consensus Engine**: Aggregates all signals into a final risk posture.

---

## 🧪 Example Output
When a document is processed, the system returns a comprehensive JSON response detailing every signal:

```json
{
  "status": "SUCCESS",
  "tracking_id": "98b50e2d-dc99-43ef-b387-052637738f61",
  "results": {
    "document_type": "Aadhaar",
    "extracted_fields": {
      "name": "RUTURAJ NAWALE",
      "id_number": "XXXX-XXXX-XXXX",
      "dob": "01/01/2000"
    },
    "face_match": {
      "verified": true,
      "similarity_score": 0.87,
      "threshold": 0.52
    },
    "fraud_validation": {
      "status": "GENUINE",
      "tampering_detected": false,
      "confidence": 0.94
    },
    "final_decision": {
        "risk_score": 12,
        "decision": "VALID",
        "reasons": []
    }
  },
  "latency_ms": 2450.0
}
```
*   **risk_score**: Normalized 0-100 score (lower is safer).
*   **similarity_score**: Biometric confidence (0.0 to 1.0).
*   **tampering_detected**: Boolean flag from ELA forensic engine.

---

## 🔌 API Documentation

| Endpoint | Method | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `/verify` | `POST` | Primary verification pipeline | `id_card` (File), `selfie` (File, Optional) |
| `/records` | `GET` | List verification history | - |
| `/records/{id}` | `GET` | Fetch specific verification detail | - |
| `/` | `GET` | System health check | - |

---

## 🧠 Decision Logic (Weighted Risk)

Veridex doesn't rely on a single signal. It uses a weighted scoring engine to handle ambiguity:

| Signal | Logic | Weight (Penalty) |
| :--- | :--- | :--- |
| **Image Tampering** | ELA reveals high compression variance | 50 points |
| **Face Mismatch** | Similarity < Threshold (Adaptive) | 35 points |
| **Identity Inconsistency** | Mismatch between OCR and Context | 25 points |
| **Duplicate Detected** | Perceptual Hash match in DB | 40 points |
| **Low Quality** | High blur or low lighting | 10 points |

### 🚦 Thresholds:
*   🟢 **0–20 → VALID**: Trusted document, automated approval.
*   🟡 **20–50 → SUSPICIOUS**: Needs manual reviewer oversight.
*   🔴 **50+ → REJECTED**: High probability of fraud/tampering.

---

## 🤖 AI Modules & Engineering Choices

*   **EasyOCR (OCR)**: Selected for its robust support for varied Indian document layouts and high tolerance for low-light noise.
*   **InsightFace / ArcFace (Biometrics)**: Uses a ResNet backbone to achieve state-of-the-art 1:1 facial matching with sub-100ms latency on CPU.
*   **ELA Forensics**: Error Level Analysis (ELA) identifies areas of an image at different compression levels, exposing local digital edits (text or photo swaps).
*   **XGBoost Classifier**: A secondary ML layer trained on historical forensic signals to predict `FRAUD` vs `GENUINE` status based on extracted features.

---

## 📊 Performance & Evaluation
*   **Speed**: End-to-end verification (OCR + Face + Fraud) averages **2.5s - 3.5s** on standard hardware.
*   **Accuracy**: High precision in spotting "Photo-on-Photo" and "Text Overlay" tampering due to ELA sensitivity.
*   **Resilience**: Adaptive thresholding allows the system to remain accurate even with moderately blurry mobile uploads.

---

## ⚠️ Engineering Constraints & Limitations
*   **Lighting Sensitivity**: Very low-light environments can degrade face matching accuracy.
*   **Liveness Limitations**: Currently optimized for 2D presentation attack detection; 3D/Video-based liveness is in the roadmap.
*   **OCR Sensitivity**: Extremely skewed or heavily folded documents may require a retake.

---

## 🛠 Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 15 (App Router), React 19, Tailwind CSS 4, Framer Motion |
| **Backend** | FastAPI (Python), SQLAlchemy, Pydantic |
| **AI/ML** | EasyOCR, InsightFace (ArcFace), XGBoost, OpenCV, PyTorch |
| **Database** | SQLite3 (Persistence), Perceptual Hashing (pHash) |
| **DevOps** | Uvicorn, Axios, Python-Multipart |

---

## ⚙️ Installation & Production Readiness

### Environment Setup
Create a `.env` in the root (optional, for custom model paths):
```env
MODEL_PATH=./models/fraud_xgb_model.json
UPLOAD_DIR=./uploads
```

### 🐍 Backend
```bash
# From the root directory
pip install -r requirements.txt
$env:PYTHONPATH="."
python backend_v2/api/main.py
```

### ⚛️ Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 👨‍💻 Author
**Ruturaj Nawale**
*   [GitHub](https://github.com/ruturajbhaskarnawale)
*   [LinkedIn](https://www.linkedin.com/in/ruturaj-nawale-863418288)
*   [Portfolio](https://ruturaj-nawale-portfolio.vercel.app/)

---

## ⭐ Support
If you find this project useful, please consider giving it a **Star** on GitHub!
## Face Model Training
```bash
python backend_v2/train/train_face.py
python backend_v2/train/benchmark_face.py
```

## Liveness Model Training
```bash
python backend_v2/train/train_liveness.py
python backend_v2/train/benchmark_liveness.py
```

## Forensic Model Training
```bash
# Ensure you are in the project root (jotex)
$env:PYTHONPATH = "."; python backend_v2/train/train_forensic.py
```

## Fraud Model Training
```bash
# Ensure you are in the project root (jotex)
$env:PYTHONPATH = "."; python backend_v2/train/train_fraud.py
```

## Environment Variables
```env
DATABASE_URL=postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db
REDIS_URL=redis://localhost:6379/0
```

## Running the Backend
```bash
python -m uvicorn backend_v2.api.main:app --host 0.0.0.0 --port 8000
```
