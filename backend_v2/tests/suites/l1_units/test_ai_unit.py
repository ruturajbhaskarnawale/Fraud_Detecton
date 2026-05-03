import torch
import numpy as np
from unittest.mock import MagicMock, patch
from backend_v2.models.forensic_unet import ForensicUNet
from backend_v2.modules.fraud_engine import FraudEngine

def test_u012_forensic_unet_shape():
    model = ForensicUNet(in_channels=5)
    dummy_input = torch.randn(1, 5, 512, 512)
    output = model(dummy_input)
    assert output.shape == (1, 1, 512, 512)

def test_u005_risk_scoring_math():
    from backend_v2.modules.decision_engine import DecisionEngine
    engine = DecisionEngine()
    # Mock the internal model
    engine.model = MagicMock()
    engine.model.predict_proba.return_value = np.array([[0.9, 0.1]])
    
    # Use the public decide() method
    res = engine.decide({"risk_score": 0.5, "tamper_score": 0.1})
    assert res["decision"] in ["ACCEPT", "REVIEW", "REJECT"]
    return {
        "extracted_data": {"decision": res["decision"]},
        "metrics": {"risk_score": res["risk_score"]}
    }

def test_u008_quality_gate_blur():
    from backend_v2.modules.quality_gate import QualityGate
    gate = QualityGate()
    with patch("cv2.imread") as mock_read:
        mock_read.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        res = gate.analyze("fake.jpg")
        assert hasattr(res, "quality_score")
        return {
            "extracted_data": {"checks": res.checks},
            "metrics": {"quality_score": res.quality_score}
        }

def test_u009_face_alignment():
    from backend_v2.modules.face_service import FaceService
    service = FaceService()
    with patch.object(service, "_detect_faces_robust") as mock_det:
        mock_det.return_value = [{"bbox": [0,0,10,10], "quality": 0.9, "embedding": np.zeros(512)}]
        res = service.process("fake.jpg")
        assert res["face_detected"] == True
        return {
            "extracted_data": {"flags": res["flags"]},
            "metrics": {"face_quality": res["face_quality_score"]}
        }

def test_u013_fraud_feature_vector():
    engine = FraudEngine()
    # Mock meta
    meta = {"ip_address": "1.2.3.4", "device_id": "xyz"}
    # Mock module results
    intel = {"forensic_score": 0.1}
    # FraudEngine uses feature_builder.build_vector
    features = engine.feature_builder.build_vector(intel, meta)
    assert isinstance(features, np.ndarray)

def test_u018_decision_logic():
    from backend_v2.modules.decision_engine import DecisionEngine
    engine = DecisionEngine()
    # Mock model
    engine.model = MagicMock()
    # Low risk -> ACCEPT
    engine.model.predict_proba.return_value = np.array([[0.9, 0.1]])
    assert engine.decide({})["decision"] == "ACCEPT"
    # High risk -> REJECT
    engine.model.predict_proba.return_value = np.array([[0.2, 0.8]])
    assert engine.decide({})["decision"] == "REJECT"
