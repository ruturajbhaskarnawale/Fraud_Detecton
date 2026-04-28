import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("fraud_engine_v2")

class FraudEngine:
    def __init__(self):
        self.decay_factor = 30 # days
        self.drift_threshold = 0.15
        self.model_version = "Veridex-Fraud-v3.0"

    def analyze(self, intelligence_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refined Fraud Analysis with score calibration and uncertainty estimation.
        """
        meta = metadata or {}
        
        # 1. Score Calibration (MANDATORY)
        # Calibrates raw signals into probabilistic space
        calibrated = self._calibrate_signals(intelligence_data)
        
        # 2. Deep Feature Engineering
        # Derived features: gaps, density, velocity
        derived = self._engineer_features(calibrated, meta)
        
        # 3. Uncertainty Estimation
        # variance across signals
        uncertainty = self._estimate_uncertainty(calibrated, derived)
        
        # 4. Tabular & Graph Aggregation
        tabular_score = derived["tabular_risk"]
        graph_score = derived["graph_risk"]
        
        # 5. Tiered Rule Engine
        rule_factors = self._run_tiered_rules(calibrated, meta)
        rule_penalty = sum(f["impact"] for f in rule_factors)

        # 6. Final Fused Score
        final_score = self._fuse_signals(tabular_score, graph_score, rule_penalty)

        return {
            "fraud_score": round(tabular_score, 4),
            "graph_risk_score": round(graph_score, 4),
            "rule_flags": [f["description"] for f in rule_factors],
            "final_score": round(min(final_score, 1.0), 4),
            "uncertainty": round(uncertainty, 4),
            "decision_hint": self._get_risk_hint(final_score),
            "explanation": {
                "risk_factors": rule_factors
            },
            "model_version": self.model_version
        }

    def _calibrate_signals(self, data: Dict) -> Dict[str, float]:
        """
        Simulated Platt scaling (Sigmoid calibration).
        """
        calibrated = {}
        for k, v in data.items():
            if isinstance(v, (int, float)):
                # Sigmoid calibration: 1 / (1 + exp(A*v + B))
                calibrated[k] = 1.0 / (1.0 + np.exp(-10 * (v - 0.5)))
        return calibrated

    def _engineer_features(self, calibrated: Dict, meta: Dict) -> Dict[str, float]:
        doc = calibrated.get("document_score", 0.0)
        forensic = calibrated.get("forensic_score", 0.0)
        identity = calibrated.get("identity_score", 0.0)
        
        # Feature A: Document-Forensic Gap
        # High gap = Clean forgery suspicion
        score_gap_doc_forensic = abs(doc - (1.0 - forensic))
        
        # Feature B: Bio-Doc Gap
        bio_doc_gap = abs(identity - doc)
        
        # Feature C: Risk Density
        risk_density = (score_gap_doc_forensic + bio_doc_gap) / 2.0

        # Feature D: Graph Risk (Simulated temporal weighting)
        graph_risk = 0.05
        if meta.get("ip_address") == "vpn_detected":
            graph_risk = 0.85
        
        return {
            "tabular_risk": risk_density,
            "graph_risk": graph_risk,
            "gap_df": score_gap_doc_forensic,
            "gap_bd": bio_doc_gap
        }

    def _estimate_uncertainty(self, calibrated: Dict, derived: Dict) -> float:
        signals = [v for k, v in calibrated.items()] + [derived["tabular_risk"]]
        return float(np.var(signals))

    def _run_tiered_rules(self, calibrated: Dict, meta: Dict) -> List[Dict]:
        factors = []
        # High Severity
        if meta.get("device_id") == "BLOCKLISTED":
            factors.append({"type": "rule", "description": "DEVICE_BLOCKLISTED", "impact": 0.9, "severity": "high"})
        
        # Medium Severity
        if meta.get("ip_location") != meta.get("resident_country"):
            factors.append({"type": "rule", "description": "GEO_MISMATCH", "impact": 0.4, "severity": "medium"})
            
        # 1c. Velocity / Redis-backed Intelligence
        if meta.get("device_risk", 0.0) > 0.5:
             factors.append({"type": "rule", "description": "HIGH_DEVICE_REUSE", "impact": 0.3, "severity": "medium"})
        
        if meta.get("metadata_flags") and "IP_VELOCITY_SPIKE" in meta.get("metadata_flags", []):
             factors.append({"type": "rule", "description": "IP_VELOCITY_ABUSE", "impact": 0.5, "severity": "high"})

        # Low Severity
        if calibrated.get("quality_score", 1.0) < 0.4:
            factors.append({"type": "rule", "description": "LOW_INPUT_QUALITY", "impact": 0.1, "severity": "low"})
            
        return factors

    def _fuse_signals(self, tabular: float, graph: float, rule_penalty: float) -> float:
        # Monotonic constraint: Risk can only increase
        base = max(tabular, graph)
        return min(base + rule_penalty, 1.0)

    def _get_risk_hint(self, score: float) -> str:
        if score > 0.7: return "high risk"
        if score > 0.4: return "medium risk"
        return "low risk"
