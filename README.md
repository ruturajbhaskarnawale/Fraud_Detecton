# Veridex AI 🛡️
> **Real-time AI Document Fraud Detection & KYC Verification Platform**

[![Stack](https://img.shields.io/badge/Stack-Fullstack-blue.svg)](https://github.com/ruturajbhaskarnawale/Fraud_Detection)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)]()

Veridex AI is a high-performance, production-grade identity verification system designed to combat document forgery and identity theft. By fusing **computer vision**, **biometric matching**, and **forensic analysis**, Veridex provides a multi-layered defense against sophisticated fraud attempts during digital onboarding.

---

## 📸 Preview & Demo

| Dashboard Interface | Verification Workflow |
| :--- | :--- |
| ![Dashboard Overview](screenshots/results_page.png) | ![Verification Process](screenshots/verify_page.png) |

---

## ✨ Key Features

### 🔍 Elite Document Analysis
*   **Intelligent OCR Extraction**: Multi-stage parsing for Indian Aadhaar and PAN cards using **EasyOCR** with post-processing for high accuracy.
*   **Auto-Doc Classification**: Instant identification of document types and layout verification.
*   **Quality Guard**: Real-time feedback on image blur, lighting, and orientation before processing.

### 🤖 Advanced Forensic Engine
*   **ELA Tampering Detection**: Error Level Analysis to identify non-homogeneous compression patterns indicating digital manipulation.
*   **Perceptual Hashing (pHash)**: Massive-scale duplicate detection to prevent "synthetic identity" attacks.
*   **ML-Based Fraud Classifier**: An **XGBoost** model trained on forensic signals to predict document genuineness.

### 🔐 Biometric Security
*   **Face Matcher**: High-precision 1:1 facial verification using **ResNet18/ArcFace** embeddings.
*   **Liveness Detection**: Anti-spoofing logic to detect presentation attacks (photos of photos, masks).
*   **Adaptive Thresholding**: Dynamically adjusts confidence requirements based on image quality.

### 📊 Business Intelligence
*   **Risk Scoring Engine**: Aggregates biometric, forensic, and OCR signals into a single, actionable Risk Score (0-100).
*   **Forensic Audit Trail**: Comprehensive API logs storing raw extraction metadata and liveness signals.

---

## 🛠 Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 16 (App Router), React 19, Tailwind CSS 4, Framer Motion, Lucide Icons |
| **Backend** | FastAPI (Python), SQLAlchemy, Pydantic |
| **AI/ML** | EasyOCR, PyTorch (ResNet18/ArcFace), XGBoost, OpenCV, Scikit-learn |
| **Database** | SQLite3 (Persistence), Perceptual Hashing (pHash) |
| **DevOps** | Uvicorn, Axios, Python-Multipart |

---

## 📂 Project Structure

```text
veridex-ai/
├── backend/
│   ├── api/                # FastAPI Endpoints & Pydantic Schemas
│   ├── src/                # Core AI Engine (OCR, Face, Fraud, Scoring)
│   │   ├── ocr/            # EasyOCR Logic & Benchmarking
│   │   ├── face/           # InsightFace Matcher & Liveness
│   │   ├── fraud/          # ELA Forensics & XGBoost Engine
│   │   └── pipeline.py     # Master Orchestration Brain
│   └── models/             # Pre-trained Checkpoints (ArcFace, XGBoost)
├── frontend/               # Next.js 16 Dashboard & UI Components
├── data/
│   ├── raw/                # Synthetic & Real-world Datasets
│   └── database/           # SQLite persistence layer
├── docs/                   # Engineering design docs & API specs
└── scripts/                # Utility & evaluation scripts
```

---

## ⚙️ Installation & Setup

### 🐍 Backend (Python 3.9+)
```bash
# Clone the repository
git clone https://github.com/ruturajbhaskarnawale/Fraud_Detection.git
cd Fraud_Detection/backend

# Install dependencies
pip install -r requirements.txt

# Launch the API
uvicorn api.main:app --reload --port 8000
```

### ⚛️ Frontend (Node.js 18+)
```bash
cd ../frontend

# Install packages
npm install

# Start development server
npm run dev
```

---

## 🧠 System Architecture

Veridex AI operates on a **Sequential Multi-Signal Fusion** architecture:

1.  **Ingestion**: Files are captured via a low-latency Next.js interface.
2.  **Quality Gate**: Images are checked for forensic suitability.
3.  **Parallel Extraction**: OCR engine extracts text while the Biometric engine generates embeddings.
4.  **Forensic Deep-Dive**: ELA and pHash analysis check for digital tampering and duplication.
5.  **Consensus**: The Risk Scoring Engine fuses all signals into a final `VALID`, `SUSPICIOUS`, or `REJECTED` decision.

---

## 📈 Why Veridex Stands Out
*   **Modular Architecture**: Every component (OCR, Face, Fraud) is independent and swappable.
*   **Production Thinking**: Built-in latency tracking and forensic audit persistence.
*   **Scalable Core**: Designed to handle asynchronous verification pipelines with ease.
*   **Security First**: Implements liveness checks and digital signature verification (ELA).

---

## 🔮 Future Roadmap
- [ ] **Dockerization**: Full containerization for easy deployment.
- [ ] **Advanced Liveness**: Video-based blink and motion detection.
- [ ] **Additional Docs**: Support for Passport and Voter ID.

---

## 👨‍💻 Author
**Ruturaj Nawale**
*   [GitHub](https://github.com/ruturajbhaskarnawale)
*   [LinkedIn](https://www.linkedin.com/in/ruturaj-nawale-863418288)
*   [Portfolio](https://ruturaj-nawale-portfolio.vercel.app/)

---

## 🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Support
If you find this project useful, please consider giving it a **Star** on GitHub! It helps more developers discover and learn from this implementation.

---
*Developed with ❤️ for the AI & Security community.*
