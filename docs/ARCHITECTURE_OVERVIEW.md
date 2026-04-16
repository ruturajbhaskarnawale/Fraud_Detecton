# ARCHITECTURE_OVERVIEW.md

## 🏗️ Clean Architecture Design
The system follows a modular "Clean Architecture" pattern, segregating concerns between API delivery, domain logic, and data persistence.

```text
Project Root
├── /backend
│   ├── /api           # FastAPI Routes & Schemas
│   ├── /src           # Core Domain Logic (Orchestrator)
│   │   ├── /ocr       # EasyOCR Engine & Benchmarking
│   │   ├── /face      # InsightFace Matcher & Liveness
│   │   ├── /fraud     # XGBoost Model & Rule Engine
│   │   ├── /scoring     # Risk Aggregator
│   │   └── pipeline.py # Master Pipeline Orchestrator
│   └── /database      # SQLite/SQLAlchemy Models
└── /frontend
    ├── /src/app       # Next.js App Router (Dashboard)
    ├── /src/services  # API Communication Layer
    └── /src/components# UI Components (Dropzone, Results)
```

## 🔄 End-to-End Data Flow
The process is designed as a sequential pipeline with defensive checks at every stage.

1. **Ingestion**: User uploads ID Card (Aadhaar/PAN) and an optional Selfie via the Next.js frontend.
2. **API Layer**: FastAPI receives files, generates a Unique `tracking_id`, and saves raw assets to `/uploads`.
3. **Preprocessing**: 
   - `QualityChecker` validates image resolution and blur.
   - `UnifiedPreprocessor` normalizes the document for OCR.
4. **Extraction (OCR)**:
   - `OCREngine` extracts text blocks.
   - `DocumentClassifier` identifies the ID type (PAN vs Aadhaar).
   - `FieldExtractor` parses name, ID number, DOB, and gender.
5. **Biometric Path**:
   - `FaceMatcher` detects faces in both ID and Selfie.
   - `ArcFace` generates 512-D embeddings.
   - Cosine similarity is calculated with **Adaptive Thresholding**.
6. **Decision Layer**:
   - `FraudDecisionEngine` extracts ELA forensics and ML features.
   - **XGBoost Classifer** predicts tampering probability.
   - **Hard Rules** flags severe mismatches or missing fields.
7. **Consensus (Risk Scoring)**:
   - `RiskScoringEngine` aggregates all signals into a 0-100 score.
   - "VALID", "SUSPICIOUS", or "REJECTED" decision is reached.
8. **Persistence & Delivery**: Result is saved to SQLite and returned to the frontend as a structured JSON.

## 📡 API Response Structure
`POST /verify` returns a `VerifyResponse` object:
```json
{
  "status": "SUCCESS",
  "tracking_id": "uuid-v4-string",
  "latency_ms": 1245.5,
  "results": {
    "id_validation": {
      "type": "pan",
      "extracted_fields": { "name": "...", "id_number": "..." }
    },
    "face_validation": {
      "verified": true,
      "similarity": 0.88,
      "threshold": 0.55
    },
    "fraud_validation": {
      "status": "GENUINE",
      "confidence": 0.98,
      "reason": []
    },
    "final_decision": {
      "decision": "VALID",
      "risk_score": 5,
      "reasons": []
    }
  }
}
```

## 🛡️ Key Components
- **Pipeline Orchestrator (`pipeline.py`)**: The central brain that handles component Fail-Fast logic and error recovery.
- **Selfie Simulator**: Used during training to generate realistic biometric pairs from ID photos.
- **Error Level Analysis (ELA)**: Forensic tool used to detect non-homogeneous compression patterns indicating digital tampering.
