import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger("fusion_engine")

class FusionEngine:
    def __init__(self):
        self.conflict_threshold = 0.4
        self.version = "v1.0"

    def fuse(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Reconciles multi-modal scores and detects conflicting signals.
        """
        # 1. Signal Normalization (Ensure all are in [0,1])
        # Forensic score is inverted for consistency calculation (1.0 = clean)
        signals = {
            "identity": features.get("identity_score", 0.0),
            "document": features.get("document_score", 0.0),
            "liveness": features.get("liveness_score", 0.0),
            "forensic_inv": 1.0 - features.get("forensic_score", 0.0),
            "metadata_risk": features.get("device_risk", 0.0) # Using device risk as proxy for session integrity
        }

        # 2. Derived Feature Computation
        gaps = {
            "bio_doc_gap": abs(signals["identity"] - signals["document"]),
            "doc_forensic_gap": abs(signals["document"] - signals["forensic_inv"]),
            "liveness_identity_gap": abs(signals["liveness"] - signals["identity"]),
            "meta_forensic_conflict": abs(signals["metadata_risk"] - features.get("forensic_score", 0.0)),
        }
        
        numeric_features = [v for v in features.values() if isinstance(v, (int, float))]
        gaps["risk_density"] = sum(numeric_features) / len(numeric_features) if numeric_features else 0.0

        # 3. Conflict Detection
        conflict_flags = []
        if gaps["doc_forensic_gap"] > self.conflict_threshold:
            conflict_flags.append("DOC_INTEGRITY_MISMATCH")
        if gaps["bio_doc_gap"] > self.conflict_threshold:
            conflict_flags.append("BIOMETRIC_ID_MISMATCH")
        if gaps["liveness_identity_gap"] > self.conflict_threshold:
            conflict_flags.append("LIVENESS_IDENTITY_CONFLICT")

        # 4. Consistency Scoring (1 - Variance)
        sig_values = list(signals.values())
        consistency_score = 1.0 - float(np.var(sig_values)) if sig_values else 0.0
        
        # 5. Signal Agreement (1 - Range)
        agreement = 1.0 - (max(sig_values) - min(sig_values)) if sig_values else 0.0

        return {
            "fused_features": {**features, **gaps},
            "consistency_score": round(max(0, consistency_score), 4),
            "conflict_flags": conflict_flags,
            "signal_agreement": round(max(0, agreement), 4),
            "version": self.version
        }
