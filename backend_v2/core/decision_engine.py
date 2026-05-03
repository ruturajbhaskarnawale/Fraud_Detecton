import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger("decision_engine")

class DecisionEngine:
    def __init__(self):
        self.version = "v1.0"

    def decide(self, risk_res: Dict[str, Any], flags: Dict[str, Any], intelligence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates the final terminal decision with hard overrides and strict thresholds.
        """
        risk_score = risk_res.get("risk_score", 0.0)
        confidence = risk_res.get("confidence", 1.0)
        intelligence = intelligence or {}
        breakdown = risk_res.get("breakdown", {})
        
        identity_score = intelligence.get("identity_score", -1.0)
        liveness_score = intelligence.get("liveness_score", -1.0)
        forensic_score = intelligence.get("forensic_score", 0.0)
        document_score = intelligence.get("document_score", 0.0)
        fraud_score = breakdown.get("fraud", 0.0)
        
        rules_triggered = []
        
        # 1. MANDATORY HARD REJECTS (Identity & Safety)
        
        # 1a. Biometric Failures
        if flags.get("BIOMETRIC_MISSING") or identity_score == -1.0:
            rules_triggered.append("REJ_BIOMETRIC_BYPASS_ATTEMPT")
            
        if identity_score >= 0.0 and identity_score < 0.45:
            rules_triggered.append("REJ_IDENTITY_MISMATCH")
            
        if liveness_score >= 0.0 and liveness_score < 0.3:
            rules_triggered.append("REJ_LIVENESS_FAILURE")
            
        if flags.get("INVALID_FACE_EMBEDDING"):
            rules_triggered.append("REJ_INVALID_FACE_EMBEDDING")

        # 1b. Tamper & Fraud
        if forensic_score > 0.6 or flags.get("tampered"):
            rules_triggered.append("REJ_TAMPER_DETECTED")
            
        if fraud_score > 0.85:
            rules_triggered.append("REJ_CRITICAL_FRAUD_SIGNAL")

        # 1c. Document Reliability
        if not intelligence.get("is_reliable", True) and document_score < 0.3:
            rules_triggered.append("REJ_UNRELIABLE_OCR")

        if rules_triggered:
            return self._finalize("REJECT", rules_triggered, risk_score, confidence, breakdown)

        # 2. ABSTAIN / REVIEW (Uncertainty)
        if flags.get("no_face") or flags.get("ID_FACE_MISSING"):
            return self._finalize("ABSTAIN", ["ABS_MISSING_VISUAL_SIGNALS"], risk_score, confidence, breakdown)
            
        if risk_score > 0.7:
            return self._finalize("REJECT", ["REJ_HIGH_RISK_SCORE"], risk_score, confidence, breakdown)

        # 3. FORCE ACCEPT (Strong Evidence)
        if (identity_score > 0.8 and 
            liveness_score > 0.75 and 
            forensic_score < 0.2 and 
            document_score > 0.75 and
            fraud_score < 0.2):
            return self._finalize("ACCEPT", ["ACC_STRONG_EVIDENCE_OVERRIDE"], risk_score, confidence, breakdown)

        # 4. DETERMINISTIC THRESHOLD LOGIC
        if risk_score < 0.35:
            # Final check for any negative flags
            if any([flags.get("multiple_faces"), flags.get("low_quality_face"), flags.get("uncertain_liveness")]):
                return self._finalize("REVIEW", ["REV_UNCERTAIN_SIGNAL_QUALTIY"], risk_score, confidence, breakdown)
            return self._finalize("ACCEPT", ["ACC_SYSTEM_PASS"], risk_score, confidence, breakdown)

        return self._finalize("REVIEW", ["REV_MANUAL_AUDIT_REQUIRED"], risk_score, confidence, breakdown)

    def _finalize(self, decision: str, rules: List[str], risk: float, conf: float, breakdown: Dict = None) -> Dict[str, Any]:
        return {
            "decision": decision,
            "risk_score": round(risk, 4),
            "confidence_score": round(conf, 4),
            "breakdown": breakdown or {},
            "rules_triggered": rules,
            "explanation": f"Decision {decision} reached. Primary Trigger: {rules[0] if rules else 'THRESHOLD'}"
        }
