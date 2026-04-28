import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
import json

logger = logging.getLogger("feature_store_v2")

class FeatureStore:
    def __init__(self):
        self.current_version = "v2.0"
        self.registry = {
            "v1.0": ["identity_score", "document_score", "liveness_score"],
            "v2.0": ["identity_score", "document_score", "liveness_score", "forensic_score", "fraud_score", "id_velocity_24h"]
        }
        # Storage Layers
        self.online_store: Dict[str, Dict] = {}
        self.offline_store: List[Dict] = []
        
        # v2 Refinements
        self.written_keys: Set[Tuple[str, str, str]] = set() # (entity, session, version)
        self.retention_days = 30

    def push(self, entity_id: str, session_id: str, module_outputs: Dict[str, Any]):
        """
        Refined push with idempotency and schema validation.
        """
        start_time = time.time()
        
        # 1. Idempotency Check
        key = (entity_id, session_id, self.current_version)
        if key in self.written_keys:
            logger.warning(f"Duplicate write detected for {key}. Skipping.")
            return

        # 2. Feature Building
        features = self._build_features(module_outputs)
        
        # 3. Schema Validation
        self._validate_schema(features)

        # 4. Record Construction with Lineage
        record = {
            "entity_id": entity_id,
            "session_id": session_id,
            "features": features,
            "version": self.current_version,
            "timestamp": time.time(),
            "lineage": self._generate_lineage(module_outputs),
            "ttl": time.time() + (self.retention_days * 86400)
        }

        # 5. Storage
        self.online_store[entity_id] = record
        self.offline_store.append(record)
        self.written_keys.add(key)
        
        logger.info(f"FSv2 push complete: {entity_id} in {(time.time() - start_time)*1000:.2f}ms")

    def get_features(self, entity_id: str) -> Optional[Dict[str, Any]]:
        # Check TTL before returning
        record = self.online_store.get(entity_id)
        if record and record["ttl"] < time.time():
            del self.online_store[entity_id]
            return None
        return record

    def get_features_batch(self, entity_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        High-performance batch retrieval.
        """
        return {eid: self.get_features(eid) for eid in entity_ids}

    def get_features_as_of(self, entity_id: str, as_of_timestamp: float) -> Optional[Dict]:
        """
        Point-in-time historical query.
        """
        history = [r for r in self.offline_store if r["entity_id"] == entity_id]
        snapshot = [r for r in history if r["timestamp"] <= as_of_timestamp]
        return snapshot[-1] if snapshot else None

    def _validate_schema(self, features: Dict):
        """
        Strict schema enforcement against registry.
        """
        allowed = set(self.registry[self.current_version])
        actual = set(features.keys())
        if not actual.issubset(allowed):
            missing = actual - allowed
            raise ValueError(f"Feature schema violation: Unexpected fields {missing}")

    def _build_features(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        intel = outputs.get("intelligence_layer", {})
        return {
            "identity_score": intel.get("identity_score", 0.0),
            "document_score": intel.get("document_score", 0.0),
            "liveness_score": intel.get("liveness_score", 0.0),
            "forensic_score": intel.get("forensic_score", 0.0),
            "fraud_score": outputs.get("fraud", {}).get("final_score", 0.0),
            "id_velocity_24h": 1
        }

    def _generate_lineage(self, outputs: Dict) -> Dict:
        return {
            "source": "PipelineOrchestrator_v2",
            "modules": list(outputs.keys())
        }
