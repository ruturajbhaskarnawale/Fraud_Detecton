import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger("decision_engine")

class DecisionEngine:
    def __init__(self):
        self.version = "v1.0"

    def decide(self, risk_res: Dict[str, Any], flags: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates the final terminal decision and reason codes.
        """
        risk_score = risk_res.get("risk_score", 0.0)
        confidence = risk_res.get("confidence", 1.0)
        
        reasons = []
        
        # 1. Terminal Security Blocks (Hard Rules)
        if flags.get("spoof_detected") or flags.get("deepfake_detected"):
            reasons.append("REJ_BIOMETRIC_SPOOF")
        if flags.get("tampered") or flags.get("copy_move_detected"):
            reasons.append("REJ_DOCUMENT_TAMPER")
        if flags.get("text_tamper_detected"):
            reasons.append("REJ_TEXT_ALTERATION")
            
        # 1b. Metadata Security Blocks
        if "VPN_DETECTED" in flags.get("metadata_flags", []) and risk_score > 0.6:
            reasons.append("REJ_VPN_HIGH_RISK")
        if "HIGH_DEVICE_VELOCITY" in flags.get("metadata_flags", []) and risk_score > 0.5:
            reasons.append("REJ_VELOCITY_ABUSE")
            
        if reasons:
            return self._finalize("REJECT", reasons, risk_score, confidence)

        # 2. Incompleteness Blocks (Abstain)
        if flags.get("no_face"):
            return self._finalize("ABSTAIN", ["ABS_FACE_NOT_DETECTED"], risk_score, confidence)
        if flags.get("low_quality_face") and confidence < 0.4:
            return self._finalize("ABSTAIN", ["ABS_IMAGE_QUALITY_LOW"], risk_score, confidence)

        # 3. Threshold Decisions
        if risk_score > 0.70:
            return self._finalize("REJECT", ["REJ_HIGH_RISK_SCORE"], risk_score, confidence)
        
        if risk_score > 0.40 or confidence < 0.60:
            return self._finalize("REVIEW", ["REV_MANUAL_AUDIT_REQUIRED"], risk_score, confidence)

        # 4. Success Path
        return self._finalize("ACCEPT", ["ACC_SYSTEM_PASS"], risk_score, confidence)

    def _finalize(self, decision: str, reason_codes: List[str], risk: float, conf: float) -> Dict[str, Any]:
        return {
            "decision": decision,
            "reason_codes": reason_codes,
            "confidence": round(conf, 4),
            "risk_score": round(risk, 4),
            "explanation": f"Decision {decision} reached via {len(reason_codes)} triggers. Primary: {reason_codes[0] if reason_codes else 'N/A'}"
        }
