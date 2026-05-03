import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger("risk_engine")

class RiskScoringEngine:
    def __init__(self):
        self.high_threshold = 0.70
        self.medium_threshold = 0.40
        self.version = "v1.0"

    def calculate(self, fusion_res: Dict[str, Any], fraud_res: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes final calibrated risk score using strict weighted formula and variance boosting.
        """
        # 1. Component Scores Extraction
        fraud_score = fraud_res.get("final_score", 0.1)
        fused = fusion_res.get("fused_features", {})
        
        # 2. Metadata Score (Normalized ip, geo, device, session)
        metadata_score = (
            (0.20 * fused.get("geo_risk", 0.1)) + 
            (0.40 * fused.get("device_risk", 0.1)) + 
            (0.20 * fused.get("session_risk", 0.1)) + 
            (0.20 * fused.get("ip_rep_risk", 0.1))
        )

        # 3. Consistency Score (Agreement between Bio, OCR, and Metadata)
        # Higher is better (more consistent)
        consistency_score = self._calculate_consistency(fusion_res, fraud_res)
        
        # 4. Conflict Score (Contradictions between signals)
        # Higher is worse (more conflicts)
        conflict_score = self._calculate_conflict(fusion_res)

        # 5. Fixed Weighted Formula (Sum of weights = 1.0)
        # RawRisk = (0.35 * fraud) + (0.25 * (1-consistency)) + (0.20 * metadata) + (0.20 * conflict)
        raw_risk = (
            (0.35 * fraud_score) + 
            (0.25 * (1.0 - consistency_score)) + 
            (0.20 * metadata_score) + 
            (0.20 * conflict_score)
        )

        # 6. Variance Boost
        # Amplify fraud, reduce clean
        if fraud_score > 0.7:
            raw_risk = min(1.0, raw_risk * 1.2)
        elif fraud_score < 0.2 and consistency_score > 0.8:
            raw_risk *= 0.8

        # 7. Final Normalization/Calibration
        # Using a steep sigmoid to push scores away from the center (0.5)
        calibrated_risk = 1.0 / (1.0 + np.exp(-12 * (raw_risk - 0.5)))
        
        # 8. Confidence Calculation
        base_confidence = (1.0 - fraud_res.get("uncertainty", 0.1))
        missing_penalty = 0.05 if not fused else 0.0
        final_confidence = max(0.0, base_confidence - missing_penalty)

        return {
            "risk_score": round(float(calibrated_risk), 4),
            "risk_level": self._get_risk_level(calibrated_risk),
            "confidence": round(float(final_confidence), 4),
            "breakdown": {
                "fraud": round(fraud_score, 4),
                "consistency": round(consistency_score, 4),
                "metadata": round(metadata_score, 4),
                "conflicts": round(conflict_score, 4)
            },
            "version": self.version
        }

    def _calculate_consistency(self, fusion_res: Dict, fraud_res: Dict) -> float:
        """Agreement between multiple biometric and document signals."""
        signals = []
        fused = fusion_res.get("fused_features", {})
        
        # 1. Biometrics vs Document (Identity Score)
        id_score = fused.get("identity_score", -1.0)
        if id_score > 0:
            signals.append(id_score)
        elif id_score == 0:
            # Face mismatch or failed detection when selfie provided
            signals.append(0.1) 
            
        # 2. Agreement between Identity and Liveness
        live_score = fused.get("liveness_score", -1.0)
        if id_score > 0 and live_score > 0:
            signals.append(1.0 - abs(id_score - live_score))
        
        # 3. Metadata vs Behavior (Proxy via metadata risk)
        geo_risk = fused.get("geo_risk", 0.0)
        ip_risk = fused.get("ip_rep_risk", 0.0)
        # Low risk in meta = high consistency with normal behavior
        signals.append(1.0 - (geo_risk + ip_risk)/2.0)
            
        # If biometrics attempted but failed, mean will be naturally lower.
        # If biometrics not attempted (id_score == -1), it won't affect mean.
        return np.mean(signals) if signals else 0.3 # Conservative fallback

    def _calculate_conflict(self, fusion_res: Dict) -> float:
        """Measures contradictions, e.g., clean IP but suspicious device."""
        fused = fusion_res.get("fused_features", {})
        ip_risk = fused.get("ip_rep_risk", 0.0)
        device_risk = fused.get("device_risk", 0.0)
        
        conflict = 0.0
        # Contradiction 1: Network vs Device
        if abs(ip_risk - device_risk) > 0.6:
            conflict += 0.4
            
        # Contradiction 2: Forensic vs Quality
        forensic = fusion_res.get("forensic_score", 0.0)
        quality = fusion_res.get("quality_score", 1.0)
        if forensic > 0.7 and quality > 0.8: # high quality image shouldn't have high 'noise' tamper
            conflict += 0.3
            
        # Contradiction 3: Identity vs Liveness
        id_score = fusion_res.get("identity_score", 0.0)
        live_score = fusion_res.get("liveness_score", 0.0)
        if id_score > 0.8 and live_score < 0.2: # Strong match but obvious spoof
            conflict += 0.5
            
        return min(1.0, conflict)

    def _get_risk_level(self, score: float) -> str:
        if score > 0.7: return "high"
        if score > 0.3: return "medium"
        return "low"
