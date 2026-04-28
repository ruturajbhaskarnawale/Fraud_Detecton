import os
import sys
import time
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, Any

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class KYCSimulator:
    """
    Simulates the End-to-End KYC journey.
    Supports SAFE MODE (Ground Truth + Noise) and REAL MODE (Live Pipeline).
    """
    def __init__(self, mode="SAFE"):
        self.mode = mode # "SAFE" or "REAL"
        self.schema = [
            "ocr_confidence", "doc_confidence", "doc_completeness",
            "face_similarity", "liveness_score", "forensic_tamper_score",
            "fraud_graph_score", "fraud_tabular_score"
        ]

    def run_session(self, user_id: str) -> Dict[str, Any]:
        """
        Executes a full KYC session simulation.
        """
        print(f"[sim] Starting {self.mode} session for user: {user_id}")
        t0 = time.time()
        
        if self.mode == "SAFE":
            features = self._generate_safe_features()
        else:
            features = self._execute_real_pipeline(user_id)
            
        latency = time.time() - t0
        
        # Decision Logic (Gated)
        decision, reason = self._make_decision(features)
        
        return {
            "session_id": f"sim_{int(time.time())}_{user_id}",
            "user_id": user_id,
            "mode": self.mode,
            "features": features,
            "decision": decision,
            "reason": reason,
            "latency_ms": round(latency * 1000, 2)
        }

    def _generate_safe_features(self) -> Dict[str, float]:
        """SAFE MODE: Generates features based on ground truth + synthetic noise."""
        return {f: round(random.uniform(0.85, 0.99), 4) for f in self.schema}

    def _execute_real_pipeline(self, user_id: str) -> Dict[str, float]:
        """REAL MODE: Placeholder for actual module orchestration."""
        # This will call the actual services once they are fully gated and calibrated.
        return {f: 0.0 for f in self.schema}

    def _make_decision(self, f: Dict[str, float]) -> (str, str):
        """Hard-coded decision logic for simulation validation."""
        if f["ocr_confidence"] < 0.7: return "REJECT", "Low OCR Confidence"
        if f["face_similarity"] < 0.6: return "REJECT", "Face Mismatch"
        if f["liveness_score"] < 0.8: return "REJECT", "Liveness Attack Detected"
        if f["forensic_tamper_score"] < 0.5: return "REVIEW", "Potential Tampering"
        
        return "ACCEPT", "All checks passed"

if __name__ == "__main__":
    sim = KYCSimulator(mode="SAFE")
    
    # Run 5 simulated sessions
    sessions = []
    for i in range(5):
        res = sim.run_session(f"user_{i}")
        sessions.append(res)
        
    print("\n=== SIMULATION SUMMARY ===")
    print(json.dumps(sessions, indent=2))
