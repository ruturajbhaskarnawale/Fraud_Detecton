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
        Computes final calibrated risk score using configurable weights and neutral fallbacks.
        """
        from backend_v2.core.config import settings
        weights = settings.RISK_WEIGHTS
        
        # 1. Inputs with Neutral Fallback (0.5 if missing)
        fraud_score = fraud_res.get("final_score", 0.5)
        consistency = fusion_res.get("consistency_score", 0.5)
        conflicts = len(fusion_res.get("conflict_flags", []))
        uncertainty = fraud_res.get("uncertainty", 0.5)
        
        # 2. Metadata Signal Mapping
        fused = fusion_res.get("fused_features", {})
        meta_geo = fused.get("geo_risk", settings.METADATA_FALLBACK_RISK)
        meta_device = fused.get("device_risk", settings.METADATA_FALLBACK_RISK)
        meta_session = fused.get("session_risk", settings.METADATA_FALLBACK_RISK)
        meta_ip = fused.get("ip_rep_risk", settings.METADATA_FALLBACK_RISK)
        
        metadata_contribution = (
            (0.20 * meta_geo) + 
            (0.40 * meta_device) + 
            (0.20 * meta_session) + 
            (0.20 * meta_ip)
        )

        # 3. Weighted Aggregation
        raw_risk = (
            (weights["fraud"] * fraud_score) + 
            (weights["consistency"] * (1.0 - consistency)) + 
            (weights["conflicts"] * min(conflicts * 0.4, 1.0)) +
            (weights["metadata"] * metadata_contribution)
        )

        # 4. Sigmoid Calibration
        calibrated_risk = 1.0 / (1.0 + np.exp(-10 * (raw_risk - 0.45)))
        
        # 5. Confidence with Missing Signal Penalty
        # Base confidence from uncertainty
        base_confidence = (1.0 - uncertainty)
        
        # Penalty for missing critical modules
        missing_penalty = 0.0
        if "fraud" not in fraud_res: missing_penalty += 0.1
        if not fused: missing_penalty += 0.2
        
        final_confidence = max(0.0, base_confidence - missing_penalty)

        return {
            "risk_score": round(float(calibrated_risk), 4),
            "risk_level": self._get_risk_level(calibrated_risk),
            "confidence": round(float(final_confidence), 4),
            "breakdown": {
                "fraud_weight": weights["fraud"],
                "metadata_bias": "CONSERVATIVE" if "metadata_risk" not in fusion_res else "NORMAL",
                "missing_signals": missing_penalty > 0
            },
            "version": self.version
        }


    def _get_risk_level(self, score: float) -> str:
        if score > self.high_threshold: return "high"
        if score > self.medium_threshold: return "medium"
        return "low"
