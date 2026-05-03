import joblib
import os
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from backend_v2.modules.fraud.feature_builder import FeatureBuilder

logger = logging.getLogger("fraud_engine_v2")

class FraudEngine:
    def __init__(self):
        self.feature_builder = FeatureBuilder()
        self.model_path = "backend_v2/models/weights/fraud/fraud_xgb_v1.pkl"
        self.model = None
        self.version = "v3.1-ML"
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded Fraud XGBoost model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load fraud model: {e}")
        else:
            logger.warning("Fraud model not found. Using fallback heuristics.")

    def analyze(self, intelligence_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Production-grade Fraud Analysis using ML Inference + Rule Safeguards.
        """
        meta = metadata or {}
        
        # 1. Feature Engineering
        feature_vector = self.feature_builder.build_vector(intelligence_data, meta)
        
        # 2. ML Inference
        fraud_score = 0.0
        if self.model:
            try:
                # Expecting 2D array for XGBoost
                fraud_score = float(self.model.predict_proba(feature_vector.reshape(1, -1))[0][1])
            except Exception as e:
                logger.error(f"Inference failed: {e}")
                fraud_score = self._fallback_heuristic(intelligence_data, meta)
        else:
            # Fallback heuristic if no model
            fraud_score = self._fallback_heuristic(intelligence_data, meta)

        # 3. Rule Engine (Safety Layer)
        rule_factors = self._run_tiered_rules(intelligence_data, meta)
        rule_penalty = sum(f["impact"] for f in rule_factors)

        # 4. Hybrid Fusion
        # Rules can only increase the risk
        final_score = min(fraud_score + rule_penalty, 1.0)

        # 5. Explainability (Feature Importance Mapping)
        feature_contributions = self._get_feature_contributions(feature_vector)

        return {
            "fraud_score": round(fraud_score, 4),
            "final_score": round(final_score, 4),
            "is_fraudulent": final_score > 0.7,
            "rules_triggered": [f["description"] for f in rule_factors],
            "feature_contributions": feature_contributions,
            "model_version": self.version,
            "decision_hint": "REJECT" if final_score > 0.7 else "REVIEW" if final_score > 0.4 else "PASS"
        }

    def _fallback_heuristic(self, intel: Dict, meta: Dict) -> float:
        # Simple weighted sum of known risk factors
        score = 0.0
        if float(intel.get("forensic_score", 0)) > 0.6: score += 0.5
        if meta.get("ip_address") == "vpn_detected": score += 0.3
        return min(score, 1.0)

    def _get_feature_contributions(self, vector: np.ndarray) -> Dict[str, float]:
        # In production, use SHAP. Here we provide a simplified mapping.
        names = self.feature_builder.get_feature_names()
        contributions = {}
        for i, val in enumerate(vector):
            if val > 0.5: # Simple heuristic for "significant" features
                contributions[names[i]] = round(float(val), 2)
        return contributions

    def _run_tiered_rules(self, intelligence: Dict, meta: Dict) -> List[Dict]:
        factors = []
        # High Severity
        if meta.get("device_id") == "BLOCKLISTED":
            factors.append({"type": "rule", "description": "DEVICE_BLOCKLISTED", "impact": 0.9, "severity": "high"})
        
        # Medium Severity
        if meta.get("ip_location") != meta.get("resident_country"):
            factors.append({"type": "rule", "description": "GEO_MISMATCH", "impact": 0.4, "severity": "medium"})
            
        # Velocity Signals
        if float(meta.get("device_risk", 0.0)) > 0.5:
             factors.append({"type": "rule", "description": "HIGH_DEVICE_REUSE", "impact": 0.3, "severity": "medium"})
        
        if "IP_VELOCITY_SPIKE" in meta.get("flags", []):
             factors.append({"type": "rule", "description": "IP_VELOCITY_ABUSE", "impact": 0.5, "severity": "high"})

        return factors
