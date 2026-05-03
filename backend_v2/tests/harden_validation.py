import sys
from pathlib import Path
import os
import torch
import numpy as np

# Setup path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.modules.ocr.ocr_engine import OCREngine
from backend_v2.modules.face_service import FaceService
from backend_v2.modules.liveness_service import LivenessService
from backend_v2.core.decision_engine import DecisionEngine

def test_ocr_hardening():
    print("\n--- OCR HARDENING TEST ---")
    engine = OCREngine()
    
    # 1. Garbage Text Simulation
    garbage_tokens = [{"text": "AAAAA", "confidence": 0.9}, {"text": "11111", "confidence": 0.8}]
    conf = engine._calibrate_confidence(garbage_tokens)
    valid = engine._validate_text_quality("AAAAA 11111")
    print(f"Garbage Calibration: {conf} (Expected low)")
    print(f"Garbage Validation: {valid['valid']} | Flags: {valid['flags']}")
    
    # 2. Real-ish Text Simulation
    clean_tokens = [{"text": "INCOME TAX DEPT", "confidence": 0.85}, {"text": "JOHN DOE", "confidence": 0.8}, {"text": "01/01/1990", "confidence": 0.9}]
    conf_clean = engine._calibrate_confidence(clean_tokens)
    valid_clean = engine._validate_text_quality("INCOME TAX DEPT JOHN DOE 01/01/1990")
    print(f"Clean Calibration: {conf_clean} (Expected high)")
    print(f"Clean Validation: {valid_clean['valid']} | Flags: {valid_clean['flags']}")

def test_biometric_bypass():
    print("\n--- BIOMETRIC BYPASS TEST ---")
    service = FaceService()
    decision = DecisionEngine()
    
    # Simulate missing selfie
    res = service._result_v2(face_detected=False, status="ABSTAIN", flags={"no_face": True, "BIOMETRIC_MISSING": True})
    print(f"Service Result for Missing Selfie: {res['status']} | Flags: {res['flags']}")
    
    # Decision check
    dec_res = decision.decide({"risk_score": 0.1}, res["flags"], {"identity_score": res["identity_score"]})
    print(f"Decision for Missing Selfie: {dec_res['decision']} | Rules: {dec_res['rules_triggered']}")
    assert dec_res['decision'] == "REJECT" or dec_res['decision'] == "ABSTAIN"

def test_similarity_interpretation():
    print("\n--- SIMILARITY INTERPRETATION TEST ---")
    decision = DecisionEngine()
    
    # Case 1: Similarity 0.1 (Mismatch)
    res_mismatch = decision.decide({"risk_score": 0.2}, {}, {"identity_score": 0.1, "liveness_score": 0.8})
    print(f"Decision for 0.1 Similarity: {res_mismatch['decision']} (Expected REJECT)")
    
    # Case 2: Similarity -1.0 (Not attempted - Bypass)
    res_bypass = decision.decide({"risk_score": 0.2}, {}, {"identity_score": -1.0, "liveness_score": 0.8})
    print(f"Decision for -1.0 Similarity: {res_bypass['decision']} (Expected REJECT)")

if __name__ == "__main__":
    test_ocr_hardening()
    test_biometric_bypass()
    test_similarity_interpretation()
