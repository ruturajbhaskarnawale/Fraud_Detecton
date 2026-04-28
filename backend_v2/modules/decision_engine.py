import os
import sys
import torch
import joblib
import numpy as np
from typing import Dict, Any, List
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class DecisionEngine:
    """
    Final Decision Layer of the Veridex KYC Pipeline.
    Takes calibrated features -> computes risk -> outputs decision + explanation.
    """
    def __init__(self):
        self.model_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "final_risk_model.joblib"
        self.model = None
        
        # Adjustable Decision Thresholds
        self.THRESH_ACCEPT = 0.20
        self.THRESH_REJECT = 0.60

    def _ensure_model(self):
        if self.model is None:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(f"Risk model not found at {self.model_path}. Train it first.")

    def decide(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes final risk score and provides a gated decision with an audit trail.
        """
        self._ensure_model()
        
        feature_keys = [
            "ocr_confidence", "doc_confidence", "doc_completeness",
            "face_similarity", "liveness_score", "forensic_tamper_score",
            "fraud_graph_score", "fraud_tabular_score"
        ]
        
        X = np.array([[features.get(k, 0.0) for k in feature_keys]])
        
        # 1. Compute Probabilistic Risk Score
        risk_score = self.model.predict_proba(X)[0, 1]
        
        # 2. Thresholding
        if risk_score < self.THRESH_ACCEPT:
            decision = "ACCEPT"
        elif risk_score >= self.THRESH_REJECT:
            decision = "REJECT"
        else:
            decision = "REVIEW"
            
        # 3. Enhanced Red Flag Detection (Explainability)
        # Red flags: Low Safety scores OR High Fraud scores
        red_flags = []
        
        # Safety checks (Should be high)
        safety_checks = ["ocr_confidence", "doc_confidence", "face_similarity", "liveness_score", "forensic_tamper_score"]
        for s in safety_checks:
            if features.get(s, 1.0) < 0.5:
                red_flags.append(f"LOW_{s.upper()}")
                
        # Fraud checks (Should be low)
        fraud_checks = ["fraud_graph_score", "fraud_tabular_score"]
        for f in fraud_checks:
            if features.get(f, 0.0) > 0.4:
                red_flags.append(f"HIGH_{f.upper()}")

        # 4. Audit Trail
        import time
        audit_trail = {
            "decision": decision,
            "risk_score": round(float(risk_score), 4),
            "top_factors": red_flags,
            "raw_signals": features,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "CERTIFIED"
        }

        return audit_trail


if __name__ == "__main__":
    # Test session
    engine = DecisionEngine()
    
    test_features = {
        "ocr_confidence": 0.95,
        "doc_confidence": 0.98,
        "doc_completeness": 1.0,
        "face_similarity": 0.92,
        "liveness_score": 0.12, # ATTACK!
        "forensic_tamper_score": 0.95,
        "fraud_graph_score": 0.05,
        "fraud_tabular_score": 0.02
    }
    
    try:
        result = engine.decide(test_features)
        print("\n=== SYSTEM DECISION ===")
        print(f"Decision: {result['decision']}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Top Red Flags: {result['factors']}")
    except Exception as e:
        print(f"Decision failed: {e}")
