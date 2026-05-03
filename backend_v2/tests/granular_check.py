import os
import sys
import torch
import numpy as np
from PIL import Image

if "USERNAME" not in os.environ: os.environ["USERNAME"] = "jotex_user"
sys.path.append(os.getcwd())

def test_modules():
    print("--- STARTING GRANULAR MODULE CHECK ---", flush=True)
    
    # 1. OCR
    try:
        from backend_v2.modules.ocr.ocr_engine import OCREngine
        print("Initializing OCR Engine...", flush=True)
        ocr = OCREngine()
        print("OCR Engine Initialized.", flush=True)
    except Exception as e:
        print(f"OCR Error: {e}", flush=True)

    # 2. Doc Understanding
    try:
        from backend_v2.modules.doc_understanding import DocUnderstandingService
        print("Initializing DocUnderstandingService...", flush=True)
        doc = DocUnderstandingService()
        print("DocUnderstandingService Initialized.", flush=True)
    except Exception as e:
        print(f"DocUnderstanding Error: {e}", flush=True)

    # 3. Fraud Engine
    try:
        from backend_v2.modules.fraud_engine import FraudEngine
        print("Initializing FraudEngine...", flush=True)
        fraud = FraudEngine()
        print("FraudEngine Initialized.", flush=True)
    except Exception as e:
        print(f"Fraud Error: {e}", flush=True)

    # 4. Forensic Service
    try:
        from backend_v2.modules.forensic_service import ForensicService
        print("Initializing ForensicService...", flush=True)
        forensic = ForensicService()
        print("ForensicService Initialized.", flush=True)
    except Exception as e:
        print(f"Forensic Error: {e}", flush=True)

    print("--- GRANULAR MODULE CHECK COMPLETE ---", flush=True)

if __name__ == "__main__":
    test_modules()
