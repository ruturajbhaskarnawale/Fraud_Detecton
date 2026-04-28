import os
import sys
from typing import Dict, Any, List
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.modules.decision_engine import DecisionEngine

class SafetyEngine(DecisionEngine):
    """
    Enhanced Decision Engine with Safety Fallbacks.
    Implements ABSTAIN logic for low-confidence or high-noise scenarios.
    """
    def __init__(self):
        super().__init__()
        # Threshold below which we refuse to make an automated decision
        self.MIN_CONFIDENCE_GATE = 0.40 
        # Number of mandatory modules that must be present
        self.MANDATORY_MODULES = ["ocr_confidence", "face_similarity", "liveness_score"]

    def decide_with_safety(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Decision logic with added safety layers:
        1. Check for missing signals.
        2. Check for extreme noise.
        3. Abstain if necessary.
        """
        # Layer 1: Mandatory Signal Check
        missing = [m for m in self.MANDATORY_MODULES if m not in features]
        if missing:
            return {
                "decision": "ABSTAIN",
                "risk_score": 1.0,
                "factors": ["MISSING_DATA"],
                "reason": f"Missing mandatory signals: {missing}"
            }

        # Layer 2: Quality Check (Extreme Noise)
        # If OCR is essentially zero, the document is unreadable
        if features["ocr_confidence"] < 0.1:
            return {
                "decision": "ABSTAIN",
                "risk_score": 1.0,
                "factors": ["UNREADABLE_DOC"],
                "reason": "Document quality too low for reliable processing"
            }

        # Layer 3: Normal Decision
        try:
            base_decision = self.decide(features)
            
            # Layer 4: Ambiguity Check
            # If the risk score is right in the middle (e.g., 0.5), it might be a noisy failure
            if 0.45 < base_decision["risk_score"] < 0.55:
                base_decision["decision"] = "REVIEW"
                base_decision["factors"].append("HIGH_AMBIGUITY")
                
            return base_decision
            
        except Exception as e:
            return {
                "decision": "ABSTAIN",
                "risk_score": 1.0,
                "factors": ["SYSTEM_ERROR"],
                "reason": str(e)
            }

if __name__ == "__main__":
    safety = SafetyEngine()
    
    # Test case: Missing Face
    res = safety.decide_with_safety({"ocr_confidence": 0.95, "liveness_score": 0.98})
    print(f"\nMissing Signal Test: {res['decision']} ({res['reason']})")
    
    # Test case: Unreadable Doc
    res = safety.decide_with_safety({"ocr_confidence": 0.05, "face_similarity": 0.9, "liveness_score": 0.9})
    print(f"Unreadable Doc Test: {res['decision']} ({res['reason']})")
