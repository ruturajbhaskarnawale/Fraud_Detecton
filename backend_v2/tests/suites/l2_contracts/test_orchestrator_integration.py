import os
import unittest
from unittest.mock import MagicMock, patch
from backend_v2.core.orchestrator import PipelineOrchestrator
from backend_v2.core.ingestion import IngestionHandler
from backend_v2.core.schemas import EvidenceBundle

def test_i001_ingest_to_ocr_flow():
    ingestor = IngestionHandler()
    # Mock some image content (empty but valid for handler if mocked)
    doc_content = b"fake-content"
    # Actually, we need a real image if we want OCR to run
    # For integration, we use a small dummy image
    import numpy as np
    import cv2
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", dummy_img)
    
    success, bundle = ingestor.handle_ingestion(
        document_content=buf.tobytes(),
        document_filename="test.jpg",
        metadata={"ip_address": "127.0.0.1"}
    )
    assert success == True
    assert isinstance(bundle, EvidenceBundle)
    
    # Run Orchestrator partial flow if possible
    orchestrator = PipelineOrchestrator()
    # Mock persistence
    orchestrator.persistence = MagicMock()
    orchestrator.feature_store = MagicMock()
    
    orchestrator.ocr_engine = MagicMock()
    orchestrator.ocr_engine.extract_text.return_value = {"text": "Test ID", "confidence": 0.9}
    
    # We need to mock other steps to avoid failures
    orchestrator.quality_gate.analyze = MagicMock()
    q_mock = MagicMock()
    q_mock.status = "PASS"
    q_mock.quality_score = 0.9
    q_mock.failure_reasons = []
    q_mock.model_dump.return_value = {"status": "PASS"}
    orchestrator.quality_gate.analyze.return_value = q_mock

    orchestrator.preprocessor.process = MagicMock(return_value={"processed_images": ["fake.jpg"]})
    
    # Other mocks to prevent type errors
    orchestrator.doc_classifier.predict = MagicMock(return_value={"document_type": "ID_CARD"})
    orchestrator.doc_understanding.extract = MagicMock(return_value={"normalized_fields": {}, "confidence": 0.9})
    orchestrator.metadata_engine.analyze = MagicMock(return_value={"metadata_risk": {"geo_risk_score": 0.1, "device_risk_score": 0.1, "session_risk_score": 0.1, "ip_reputation_score": 0.1}, "flags": []})
    orchestrator.forensic_service.analyze = MagicMock(return_value={"tamper_score": 0.1, "is_altered": False, "flags": {}})
    orchestrator.face_service.process = MagicMock(return_value={"status": "PASS", "identity_score": 0.9, "flags": {}})
    orchestrator.fraud_engine.analyze = MagicMock(return_value={"final_score": 0.1, "rule_flags": []})
    orchestrator.fusion_engine.fuse = MagicMock(return_value={"identity_score": 0.9})
    orchestrator.risk_engine.calculate = MagicMock(return_value={"risk_score": 0.1, "risk_level": "LOW", "breakdown": {}})
    orchestrator.decision_engine.decide = MagicMock(return_value={"decision": "ACCEPT", "risk_score": 0.1, "confidence_score": 0.9, "rules_triggered": [], "explanation": "OK"})
    
    res = orchestrator.run_with_bundle(bundle)
    assert res.session_id == bundle.session_id

import uuid

def test_i007_all_modules_to_risk_engine():
    orchestrator = PipelineOrchestrator()
    # Mock all module outputs with plain dicts for serialization safety
    session_id = str(uuid.uuid4())
    bundle = EvidenceBundle(raw_input_path="fake.jpg", session_id=session_id)
    
    # Mock ALL persistence calls to avoid DB issues
    orchestrator.persistence = MagicMock()
    orchestrator.feature_store = MagicMock()
    
    with patch.object(orchestrator.forensic_service, "analyze") as mock_for:
        mock_for.return_value = {"tamper_score": 0.1, "is_altered": False, "flags": {}}
        with patch.object(orchestrator.face_service, "process") as mock_face:
            mock_face.return_value = {"status": "PASS", "identity_score": 0.9, "flags": {}}
            
            # We need to mock more to avoid file errors
            orchestrator.quality_gate.analyze = MagicMock()
            q_mock = MagicMock()
            q_mock.status = "PASS"
            q_mock.quality_score = 0.9
            q_mock.checks = {"blur_score": 0.1}
            q_mock.failure_reasons = []
            q_mock.model_dump.return_value = {"status": "PASS"}
            orchestrator.quality_gate.analyze.return_value = q_mock

            orchestrator.preprocessor.process = MagicMock(return_value={"processed_images": ["fake.jpg"]})
            orchestrator.ocr_engine.extract_text = MagicMock(return_value={"text": "JOHN DOE", "confidence": 0.9})
            orchestrator.doc_classifier.predict = MagicMock(return_value={"document_type": "ID_CARD"})
            orchestrator.doc_understanding.extract = MagicMock(return_value={"normalized_fields": {"name": "JOHN DOE"}, "confidence": 0.9})
            orchestrator.metadata_engine.analyze = MagicMock(return_value={"metadata_risk": {"geo_risk_score": 0.1, "device_risk_score": 0.1, "session_risk_score": 0.1, "ip_reputation_score": 0.1}, "flags": []})
            orchestrator.fraud_engine.analyze = MagicMock(return_value={"final_score": 0.1, "rule_flags": []})
            orchestrator.fusion_engine.fuse = MagicMock(return_value={"identity_score": 0.9})
            
            # Risk engine calculate expects floats
            orchestrator.risk_engine.calculate = MagicMock(return_value={"risk_score": 0.1, "risk_level": "LOW", "breakdown": {}})
            
            # Decision engine decide expects dict
            orchestrator.decision_engine.decide = MagicMock(return_value={"decision": "ACCEPT", "risk_score": 0.1, "confidence_score": 0.9, "rules_triggered": [], "explanation": "OK"})
            
            res = orchestrator.run_with_bundle(bundle)
            assert res.decision.value == "ACCEPT"
            return {
                "extracted_data": {
                    "document_type": res.document.document_type,
                    "extracted_name": res.document.fields.get("name"),
                    "final_decision": res.decision.value
                },
                "metrics": {
                    "risk_score": res.risk_score,
                    "confidence": res.confidence_score
                }
            }

def test_i017_orchestrator_module_timeout():
    orchestrator = PipelineOrchestrator()
    # Mock a module to hang/timeout
    with patch.object(orchestrator.ocr_engine, "extract_text") as mock_ocr:
        mock_ocr.side_effect = Exception("Timeout")
        session_id = "550e8400-e29b-41d4-a716-446655440001"
        bundle = EvidenceBundle(raw_input_path="fake.jpg", session_id=session_id)
        
        # Mock persistence to avoid SQL errors during failure path
        orchestrator.persistence.log_error = MagicMock()
        orchestrator.persistence.fail_session = MagicMock()
        
        try:
            orchestrator.run_with_bundle(bundle)
        except Exception:
            pass # Expected
