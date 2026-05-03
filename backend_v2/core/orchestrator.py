from typing import List, Dict, Any
from backend_v2.core.schemas import (
    EvidenceBundle, PipelineResult, Decision, DocumentType, IngestionStatus,
    OCRData, DocumentData, BiometricData, ForensicData, MetadataData, FraudData, RiskData
)
from backend_v2.modules.quality_gate import QualityGate
from backend_v2.modules.preprocessing import PreprocessingEngine
from backend_v2.modules.ocr.ocr_engine import OCREngine
from backend_v2.modules.document_classifier import DocumentClassifier
from backend_v2.modules.doc_understanding import DocUnderstandingService
from backend_v2.modules.face_service import FaceService
from backend_v2.modules.liveness_service import LivenessService
from backend_v2.modules.routing_engine import RoutingEngine
from backend_v2.modules.forensic_service import ForensicService
from backend_v2.modules.fraud_engine import FraudEngine
from backend_v2.modules.metadata_engine import MetadataIntelligenceEngine
from .feature_store import FeatureStore
from .fusion_engine import FusionEngine
from .risk_engine import RiskScoringEngine
from .decision_engine import DecisionEngine
from backend_v2.database.persistence import PersistenceService
from backend_v2.database.intelligence_cache import IntelligenceCache
import logging
from backend_v2.core.config import settings

logger = logging.getLogger("orchestrator_v2")






class PipelineOrchestrator:
    def __init__(self):
        print("[ORCHESTRATOR] Initializing Phase 1 Modules...", flush=True)
        # Phase 1 Modules
        self.quality_gate = QualityGate()
        self.preprocessor = PreprocessingEngine()
        self.ocr_engine = OCREngine()
        
        print("[ORCHESTRATOR] Initializing Phase 2 Modules...", flush=True)
        # Phase 2 Modules
        self.doc_classifier = DocumentClassifier()
        self.doc_understanding = DocUnderstandingService()
        self.face_service = FaceService()
        self.liveness_service = LivenessService()
        self.routing_engine = RoutingEngine()
        self.forensic_service = ForensicService()
        self.fraud_engine = FraudEngine()
        self.metadata_engine = MetadataIntelligenceEngine()
        self.feature_store = FeatureStore()
        self.fusion_engine = FusionEngine()
        self.risk_engine = RiskScoringEngine()
        self.decision_engine = DecisionEngine()
        self.persistence = PersistenceService()
        print("[ORCHESTRATOR] Initialization Complete.", flush=True)





    def run(self, input_path: str, session_id: str = None) -> PipelineResult:
        # Legacy entry point - creates a bundle
        bundle = EvidenceBundle(raw_input_path=input_path, session_id=session_id or "")
        return self.run_with_bundle(bundle)

    def run_with_bundle(self, bundle: EvidenceBundle) -> PipelineResult:
        # 1. Initialize Persistence Session
        try:
            print("[TRACE] Step 1: Persistence Session", flush=True)
            self.persistence.create_session({
                "session_id": bundle.session_id,
                "entity_id": bundle.entity_id,
                "metadata": bundle.metadata
            })
            self.persistence.mark_session_processing(bundle.session_id)
            self.persistence.log_audit(bundle.session_id, "START_PIPELINE", {"doc_type": bundle.doc_type})
            
            # Log Model Versions
            self.persistence.log_model_versions(bundle.session_id, {
                "ocr": self.ocr_engine.version,
                "face": self.face_service.version,
                "liveness": self.liveness_service.version,
                "orchestrator": "v1.1.1-final"
            })
            
            # 1b. Cache Session in Redis
            print("[TRACE] Step 1b: Redis Cache", flush=True)
            try:
                IntelligenceCache.cache_session(bundle.session_id, {
                    "entity_id": bundle.entity_id,
                    "status": "PROCESSING",
                    "metadata": bundle.metadata
                })
            except Exception as e:
                logger.warning(f"Redis cache failure: {e}")

            input_path = bundle.raw_input_path
            
            # 2. Quality Gate
            print("[TRACE] Step 2: Quality Gate", flush=True)
            quality_res = self.quality_gate.analyze(input_path)
            bundle.quality_gate = quality_res

            if quality_res.status == IngestionStatus.ABSTAIN:
                res = PipelineResult(
                    session_id=bundle.session_id,
                    decision=Decision.ABSTAIN,
                    confidence_score=0.0,
                    explanation=f"Quality Gate Failed: {', '.join(quality_res.failure_reasons)}",
                    module_breakdown={"quality_gate": quality_res.model_dump()}
                )
                self.persistence.save_module_results(bundle.session_id, res.model_dump(mode='json'))
                return res

            # 3. Preprocessing
            print("[TRACE] Step 3: Preprocessing", flush=True)
            if bundle.metadata.get("file_type") == "application/pdf":
                prep_res = self.preprocessor.process_pdf(input_path, quality_res)
            else:
                prep_res = self.preprocessor.process(input_path, quality_res)
                
            normalized_paths = prep_res["processed_images"]
            bundle.normalized_images_paths = normalized_paths
            primary_image = normalized_paths[0]

            # 4. OCR & Classification
            print("[TRACE] Step 4: OCR", flush=True)
            ocr_result = self.ocr_engine.extract_text(normalized_paths)
            print("[TRACE] Step 4b: Classification", flush=True)
            classifier_res = self.doc_classifier.predict(primary_image)
            bundle.doc_type = classifier_res["document_type"]

            # 5. Routing & Understanding
            print("[TRACE] Step 5: Routing & Understanding", flush=True)
            route_info = self.routing_engine.route(bundle, quality_res, prep_res, ocr_result.get("confidence", 0.0))
            doc_res = self.doc_understanding.extract(primary_image, ocr_result, bundle.doc_type)

            # 6. Specialized Processing
            print("[TRACE] Step 6: Forensics", flush=True)
            forensic_res = self.forensic_service.analyze(primary_image, ocr_result, bundle.metadata)

            print("[TRACE] Step 6b: Metadata Engine", flush=True)
            metadata_res = self.metadata_engine.analyze(bundle.metadata)

            print("[TRACE] Step 6c: Biometrics", flush=True)
            biometrics_res = {"status": "ABSTAIN", "identity_score": -1.0, "liveness_score": -1.0, "flags": {}}
            if bundle.selfie_path:
                face_res = self.face_service.process(bundle.selfie_path, primary_image)
                liveness_res = self.liveness_service.analyze(bundle.selfie_path, face_res)

                biometrics_res = {
                    "status": face_res["status"],
                    "identity_score": face_res["identity_score"],
                    "liveness_score": liveness_res["liveness_score"],
                    "flags": {**face_res["flags"], **liveness_res["flags"]}
                }

            # 7. Intelligence Layer & Fraud Analysis
            intelligence_layer = {
                "identity_score": biometrics_res.get("identity_score", -1.0),
                "liveness_score": biometrics_res.get("liveness_score", -1.0),
                "forensic_score": forensic_res.get("tamper_score", 0.0),
                "document_score": ocr_result.get("confidence", 0.0),
                "is_reliable": ocr_result.get("is_reliable", True),
                "quality_score": quality_res.quality_score,
                "geo_risk": metadata_res["metadata_risk"]["geo_risk_score"],
                "device_risk": metadata_res["metadata_risk"]["device_risk_score"],
                "session_risk": metadata_res["metadata_risk"]["session_risk_score"],
                "ip_rep_risk": metadata_res["metadata_risk"]["ip_reputation_score"],
                "metadata_flags": metadata_res["flags"],
                "fused_features": metadata_res["metadata_risk"] 
            }
            
            fraud_res = self.fraud_engine.analyze(intelligence_layer, {**bundle.metadata, **intelligence_layer})
            fusion_res = self.fusion_engine.fuse(intelligence_layer)
            risk_res = self.risk_engine.calculate(fusion_res, fraud_res)
            
            # 8. Final Decision
            def get_flag_dict(data, key):
                val = data.get(key, {})
                if isinstance(val, list):
                    return {k: True for k in val}
                return val if isinstance(val, dict) else {}

            combined_flags = {
                **get_flag_dict(biometrics_res, "flags"), 
                **get_flag_dict(forensic_res, "flags"),
                **get_flag_dict(ocr_result, "quality_flags"),
                "tampered": forensic_res.get("is_altered", False)
            }
            decision_res = self.decision_engine.decide(risk_res, combined_flags, intelligence_layer)

            # 9. Result Construction
            final_result = PipelineResult(
                session_id=bundle.session_id,
                tracking_id=bundle.session_id,
                entity_id=bundle.entity_id,
                decision=decision_res["decision"],
                risk_score=decision_res["risk_score"],
                confidence_score=decision_res["confidence_score"],
                rules_triggered=decision_res["rules_triggered"],
                explanation=decision_res["explanation"],
                ocr=OCRData(text=ocr_result["text"], confidence=ocr_result.get("confidence", 0.0)),
                document=DocumentData(
                    document_type=bundle.doc_type or "UNKNOWN",
                    fields=doc_res.get("normalized_fields", {}),
                    confidence=doc_res.get("confidence", 0.0)
                ),
                biometrics=BiometricData(
                    face_similarity=max(0.0, biometrics_res.get("identity_score", 0.0)),
                    liveness_score=max(0.0, biometrics_res.get("liveness_score", 0.0)),
                    status=biometrics_res["status"],
                    flags=[k for k, v in biometrics_res.get("flags", {}).items() if v]
                ),
                forensics=ForensicData(
                    tamper_score=forensic_res.get("tamper_score", 0.0),
                    is_altered=forensic_res.get("is_altered", False),
                    forgery_flags=[k for k, v in forensic_res.get("flags", {}).items() if v]
                ),
                metadata=MetadataData(
                    ip_risk=metadata_res["metadata_risk"]["ip_reputation_score"],
                    device_risk=metadata_res["metadata_risk"]["device_risk_score"],
                    geo_anomaly="GEO_ANOMALY" in metadata_res["flags"],
                    flags=metadata_res["flags"]
                ),
                fraud=FraudData(
                    fraud_score=fraud_res.get("final_score", 0.0),
                    is_fraudulent=fraud_res.get("final_score", 0.0) > 0.7,
                    rules_triggered=fraud_res.get("rule_flags", [])
                ),
                risk=RiskData(
                    score=risk_res.get("risk_score", 0.0),
                    level=risk_res.get("risk_level", "UNKNOWN"),
                    breakdown=risk_res.get("breakdown", {})
                ),
                image_paths={
                    "id_card": bundle.raw_input_path.split("backend_v2")[-1].replace("\\", "/"),
                    "selfie": bundle.selfie_path.split("backend_v2")[-1].replace("\\", "/") if bundle.selfie_path else ""
                }
            )

            # 10. Final Persistence & Feature Store
            self.feature_store.push(
                entity_id=bundle.entity_id or "unknown",
                session_id=bundle.session_id,
                module_outputs=final_result.model_dump(mode='json')
            )
            self.persistence.save_artifact(bundle.session_id, "id_card", bundle.raw_input_path)
            if bundle.selfie_path:
                self.persistence.save_artifact(bundle.session_id, "selfie", bundle.selfie_path)
            self.persistence.save_module_results(bundle.session_id, final_result.model_dump(mode='json'))
            self.persistence.log_audit(bundle.session_id, "COMPLETE_PIPELINE", {"decision": str(final_result.decision.value)})

            return final_result

        except Exception as e:
            logger.error(f"Pipeline failure for session {bundle.session_id}: {e}")
            self.persistence.log_error(bundle.session_id, "ORCHESTRATOR", str(e))
            self.persistence.fail_session(bundle.session_id, str(e))
            raise



