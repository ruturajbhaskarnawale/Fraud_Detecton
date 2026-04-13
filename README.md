# Document Fraud Detection System

A production-grade Document Fraud Detection System designed for KYC and merchant onboarding. This system integrates multiple AI/ML components to verify identity documents, detect tampering, and perform face verification with liveness checks.

## 🚀 Features

- **Document Quality Check**: Automatically detects blur, poor lighting, and orientation issues.
- **OCR Extraction**: Robust text extraction using EasyOCR for PAN and Aadhaar cards.
- **Face Verification**: Matches ID document photos with real-time selfies using ResNet18 embeddings.
- **Fraud Detection**:
  - **ELA Tampering Detection**: Error Level Analysis to identify digitally altered images.
  - **Data Consistency**: Cross-verifies extracted fields across multiple documents.
  - **Duplicate Detection**: Uses Perceptual Hashing (pHash) to flag identical submissions.
- **Risk Scoring Engine**: Aggregates all signals into a final risk score and decision.
- **FastAPI Backend**: Scalable API for integration with web and mobile applications.
- **Next.js Frontend**: A modern, responsive dashboard for managing verifications.

## 🏗️ Project Structure

```text
project_root/
├── backend/
│   ├── api/                # FastAPI application
│   ├── src/                # Core ML and logic (OCR, Face, Fraud, Scoring)
│   ├── uploads/            # Temporary storage for process images
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js Dashboard
├── data/
│   ├── raw/                # Training and validation datasets
│   └── database/           # SQLite persistence layer
├── scripts/                # Utility and test scripts
├── docs/                   # Detailed system documentation
└── models/                 # Model checkpoints and caches
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend)
- SQLite3

### Backend Setup
1. Navigate to the backend directory:
   ```cmd
   cd backend
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Run the API:
   ```cmd
   uvicorn api.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```cmd
   cd frontend
   ```
2. Install dependencies:
   ```cmd
   npm install
   ```
3. Start the development server:
   ```cmd
   npm run dev
   ```

## 🧪 Testing

To run the end-to-end pipeline test:
```cmd
python scripts/test_full_pipeline.py
```

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
