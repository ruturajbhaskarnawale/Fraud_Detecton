import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from backend_v2.database.models import (
    Entity, Session, Artifact, OCRResult, 
    BiometricResult, ForensicResult, RiskResult,
    AuditLog, DeviceIntelligence, IPIntelligence,
    DecisionHistory, ModuleError, FeatureStore,
    DocumentResult, FraudResult
)
from backend_v2.database.manager import SessionLocal
from datetime import datetime
import uuid

from backend_v2.core.schemas import (
    PipelineResult, Decision, OCRData, DocumentData, 
    BiometricData, ForensicData, MetadataData, FraudData, RiskData
)

logger = logging.getLogger("persistence_service")

class PersistenceService:
    def __init__(self):
        self.db: DBSession = SessionLocal()

    def create_session(self, bundle_data: Dict[str, Any]) -> str:
        """Creates a new session in the database with status CREATED."""
        session_id = bundle_data.get("session_id") or str(uuid.uuid4())
        
        try:
            # Ensure entity exists
            entity_id = bundle_data.get("entity_id") or "unknown-entity"
            entity = self.db.query(Entity).filter(Entity.external_id == entity_id).first()
            if not entity:
                entity = Entity(external_id=entity_id)
                self.db.add(entity)
                self.db.commit()
                self.db.refresh(entity)

            # Create Session
            new_session = Session(
                id=uuid.UUID(session_id),
                entity_id=entity.id,
                status="CREATED",
                device_id=bundle_data.get("metadata", {}).get("device_id", "unknown"),
                ip_address=bundle_data.get("metadata", {}).get("ip_address", "0.0.0.0"),
                user_agent=bundle_data.get("metadata", {}).get("user_agent", ""),
                meta_json=bundle_data.get("metadata", {})
            )
            self.db.add(new_session)
            
            # Track Device/IP Intelligence (Postgres side)
            self._update_intelligence(new_session.device_id, new_session.ip_address)
            
            self.db.commit()
            return session_id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise

    def mark_session_processing(self, session_id: str):
        """Updates session status to PROCESSING."""
        sess = self.db.query(Session).filter(Session.id == uuid.UUID(session_id)).first()
        if sess:
            sess.status = "PROCESSING"
            self.db.commit()

    def fail_session(self, session_id: str, error_message: str):
        """Marks session as FAILED and rolls back any pending changes."""
        try:
            self.db.rollback()
            sess = self.db.query(Session).filter(Session.id == uuid.UUID(session_id)).first()
            if sess:
                sess.status = "FAILED"
                sess.meta_json = {**(sess.meta_json or {}), "error": error_message}
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to mark session as failed: {e}")


    def save_artifact(self, session_id: str, artifact_type: str, file_path: str):
        """Saves an artifact reference."""
        artifact = Artifact(
            session_id=uuid.UUID(session_id),
            artifact_type=artifact_type,
            file_path=file_path
        )
        self.db.add(artifact)
        self.db.commit()

    def save_module_results(self, session_id: str, results: Dict[str, Any]):
        """Persists all AI module outputs from the standardized result schema."""
        sess_uuid = uuid.UUID(session_id)
        
        # 1. OCR
        ocr = results.get("ocr")
        if ocr:
            ocr_res = OCRResult(
                session_id=sess_uuid,
                raw_text=ocr.get("text", ""),
                structured_data=results.get("document", {}).get("fields", {}),
                confidence=ocr.get("confidence", 0.0)
            )
            self.db.add(ocr_res)

        # 2. Document Understanding
        doc = results.get("document")
        if doc:
            doc_res = DocumentResult(
                session_id=sess_uuid,
                document_type=doc.get("document_type"),
                extracted_fields=doc.get("fields", {}),
                classification_confidence=doc.get("confidence", 0.0),
                extraction_confidence=doc.get("confidence", 0.0)
            )
            self.db.add(doc_res)

        # 3. Biometrics
        bio = results.get("biometrics")
        if bio:
            bio_res = BiometricResult(
                session_id=sess_uuid,
                similarity_score=bio.get("face_similarity", 0.0),
                liveness_score=bio.get("liveness_score", 0.0),
                is_match=bio.get("status") == "PASS",
                flags={f: True for f in bio.get("flags", [])}
            )
            self.db.add(bio_res)

        # 4. Forensics
        forensic = results.get("forensics")
        if forensic:
            for_res = ForensicResult(
                session_id=sess_uuid,
                tamper_score=forensic.get("tamper_score", 0.0),
                is_altered=forensic.get("is_altered", False),
                detected_forgeries={f: True for f in forensic.get("forgery_flags", [])}
            )
            self.db.add(for_res)

        # 5. Fraud Engine
        fraud = results.get("fraud")
        if fraud:
            fraud_res = FraudResult(
                session_id=sess_uuid,
                fraud_score=fraud.get("fraud_score", 0.0),
                signals={
                    "is_fraudulent": fraud.get("is_fraudulent", False),
                    "rules_triggered": fraud.get("rules_triggered", [])
                },
                velocity_check=results.get("metadata", {}), 
                is_fraudulent=fraud.get("is_fraudulent", False)
            )
            self.db.add(fraud_res)

        # 6. Final Risk
        risk = results.get("risk")
        if risk:
            risk_res = RiskResult(
                session_id=sess_uuid,
                final_risk_score=risk.get("score", 0.0),
                risk_level=risk.get("level", "UNKNOWN"),
                explanation={"text": results.get("explanation", "")},
                module_scores=risk.get("breakdown", {})
            )
            self.db.add(risk_res)

            # Update Session Status
            sess = self.db.query(Session).filter(Session.id == sess_uuid).first()
            if sess:
                sess.status = "COMPLETED"
                sess.decision = results.get("decision")
                sess.confidence_score = results.get("confidence_score", 0.0)

            # Record Decision History
            history = DecisionHistory(
                session_id=sess_uuid,
                decision=results.get("decision"),
                previous_decision=None,
                actor="SYSTEM"
            )
            self.db.add(history)

        self.db.commit()


    def log_audit(self, session_id: str, action: str, details: Dict):
        """Logs a system action."""
        log = AuditLog(
            session_id=uuid.UUID(session_id) if session_id else None,
            action=action,
            actor="SYSTEM",
            details=details
        )
        self.db.add(log)
        self.db.commit()

    def log_model_versions(self, session_id: str, versions: Dict[str, str]):
        """Logs the versions of AI models used for a session."""
        self.log_audit(session_id, "MODEL_VERSIONS", versions)
        
    def log_error(self, session_id: str, module: str, message: str, traceback: Optional[str] = None):

        """Logs a module-level failure."""
        err = ModuleError(
            session_id=uuid.UUID(session_id),
            module_name=module,
            error_message=message,
            traceback=traceback
        )
        self.db.add(err)
        self.db.commit()

    def update_feature_store(self, entity_id: str, features: Dict):
        """Updates the long-term feature store for an entity."""
        # Find UUID for external_id
        entity = self.db.query(Entity).filter(Entity.external_id == entity_id).first()
        if not entity: return

        store = self.db.query(FeatureStore).filter(FeatureStore.entity_id == entity.id).first()
        if not store:
            store = FeatureStore(entity_id=entity.id, features=features)
            self.db.add(store)
        else:
            store.features.update(features)
        self.db.commit()

    def _update_intelligence(self, device_id: str, ip_address: str):
        """Updates device/IP velocity and reputation tracking."""
        # Device
        dev = self.db.query(DeviceIntelligence).filter(DeviceIntelligence.device_id == device_id).first()
        if not dev:
            dev = DeviceIntelligence(device_id=device_id, total_attempts=1)
            self.db.add(dev)
        else:
            dev.total_attempts += 1
            dev.last_seen = datetime.utcnow()

        # IP
        ip = self.db.query(IPIntelligence).filter(IPIntelligence.ip_address == ip_address).first()
        if not ip:
            ip = IPIntelligence(ip_address=ip_address, total_sessions=1)
            self.db.add(ip)
        else:
            ip.total_sessions += 1
            
    def get_session_result(self, session_id: str) -> Optional[PipelineResult]:
        """Reconstructs the full PipelineResult from stored data."""
        try:
            sess_uuid = uuid.UUID(session_id)
            sess = self.db.query(Session).filter(Session.id == sess_uuid).first()
            if not sess: return None

            # Fetch all module results
            ocr = self.db.query(OCRResult).filter(OCRResult.session_id == sess_uuid).first()
            doc = self.db.query(DocumentResult).filter(DocumentResult.session_id == sess_uuid).first()
            bio = self.db.query(BiometricResult).filter(BiometricResult.session_id == sess_uuid).first()
            forn = self.db.query(ForensicResult).filter(ForensicResult.session_id == sess_uuid).first()
            fraud = self.db.query(FraudResult).filter(FraudResult.session_id == sess_uuid).first()
            risk = self.db.query(RiskResult).filter(RiskResult.session_id == sess_uuid).first()

            # Safely parse JSON fields that might be strings
            import json
            
            def safe_dict(val):
                if not val: return {}
                if isinstance(val, str):
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, dict):
                            return parsed
                        return {}
                    except: return {}
                if isinstance(val, dict):
                    return val
                return {}

            risk_exp = safe_dict(risk.explanation if risk else None)
            doc_fields = safe_dict(doc.extracted_fields if doc else None)
            bio_flags = safe_dict(bio.flags if bio else None)
            forn_forgeries = safe_dict(forn.detected_forgeries if forn else None)
            fraud_signals = safe_dict(fraud.signals if fraud else None)
            risk_scores = safe_dict(risk.module_scores if risk else None)

            return PipelineResult(
                session_id=str(sess_uuid),
                entity_id=str(sess.entity_id),
                decision=sess.decision or Decision.ABSTAIN,
                confidence_score=sess.confidence_score or 0.0,
                explanation=risk_exp.get("text", "No explanation available"),
                ocr=OCRData(
                    text=ocr.raw_text if ocr else "",
                    confidence=ocr.confidence if ocr else 0.0
                ),
                document=DocumentData(
                    document_type=doc.document_type if doc else "UNKNOWN",
                    fields=doc_fields,
                    confidence=doc.classification_confidence if doc else 0.0
                ),
                biometrics=BiometricData(
                    face_similarity=bio.similarity_score if bio else 0.0,
                    liveness_score=bio.liveness_score if bio else 0.0,
                    status="PASS" if bio and bio.is_match else "FAIL",
                    flags=list(bio_flags.keys())
                ),
                forensics=ForensicData(
                    tamper_score=forn.tamper_score if forn else 0.0,
                    is_altered=forn.is_altered if forn else False,
                    forgery_flags=list(forn_forgeries.keys())
                ),
                metadata=MetadataData(
                    ip_risk=0.0,
                    device_risk=0.0,
                    geo_anomaly=False,
                    flags=[]
                ),
                fraud=FraudData(
                    fraud_score=fraud.fraud_score if fraud else 0.0,
                    is_fraudulent=fraud.is_fraudulent if fraud else False,
                    rules_triggered=fraud_signals.get("rules_triggered", [])
                ),
                risk=RiskData(
                    score=risk.final_risk_score if risk else 0.0,
                    level=risk.risk_level if risk else "UNKNOWN",
                    breakdown=risk_scores
                ),
                timestamp=sess.created_at
            )
        except Exception as e:
            logger.error(f"Failed to fetch session results: {e}")
            return None

    def close(self):
        self.db.close()

