import numpy as np
from typing import Dict, Any, List, Optional

class FeatureBuilder:
    """
    Transforms session data and historical context into a structured feature vector
    for the Fraud Engine.
    """
    def __init__(self):
        self.feature_names = [
            "face_similarity", "liveness_score", "tamper_score",
            "ocr_confidence", "metadata_risk", "ip_velocity",
            "device_velocity", "geo_mismatch", "proxy_score"
        ]

    def build_vector(self, intelligence_data: Dict[str, Any], metadata: Dict[str, Any]) -> np.ndarray:
        """
        Creates a normalized feature vector [0, 1].
        """
        features = []
        
        # 1. Identity Features
        features.append(float(intelligence_data.get("identity_score", 0.0)))
        features.append(float(intelligence_data.get("liveness_score", 0.0)))
        
        # 2. Forensic Features
        features.append(float(intelligence_data.get("forensic_score", 0.0)))
        
        # 3. OCR Features
        features.append(float(intelligence_data.get("document_score", 0.5)))
        
        # 4. Metadata Risk
        features.append(float(intelligence_data.get("device_risk", 0.0)))
        
        # 5. Velocity Features (from metadata/redis integration)
        ip_velocity = 1.0 if "IP_VELOCITY_SPIKE" in metadata.get("flags", []) else 0.0
        device_velocity = 1.0 if "HIGH_DEVICE_REUSE" in metadata.get("flags", []) else 0.0
        features.append(ip_velocity)
        features.append(device_velocity)
        
        # 6. Geo & Proxy
        geo_mismatch = 1.0 if "GEO_MISMATCH" in metadata.get("flags", []) else 0.0
        proxy_score = 1.0 if metadata.get("ip_address") == "vpn_detected" else 0.0
        features.append(geo_mismatch)
        features.append(proxy_score)
        
        return np.array(features, dtype=np.float32)

    def get_feature_names(self) -> List[str]:
        return self.feature_names
