from fastapi.testclient import TestClient
from backend_v2.api.main import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_e2e_001_happy_path():
    # Mock orchestrator and ingestor and _models_ready
    with patch("backend_v2.api.main.orchestrator") as mock_orch, \
         patch("backend_v2.api.main.ingestor") as mock_ing, \
         patch("backend_v2.api.main._models_ready", True):
        
        mock_ing.handle_ingestion.return_value = (True, MagicMock(session_id="test"))
        mock_orch.run_with_bundle.return_value = MagicMock(
            session_id="test-session-e2e",
            decision="ACCEPT",
            risk_score=0.1,
            model_dump=lambda mode: {"decision": "ACCEPT", "risk_score": 0.1}
        )
        
        files = {"document": ("test.jpg", b"fake-content", "image/jpeg")}
        response = client.post("/verify", files=files, data={"doc_type": "ID_CARD"})
        
        assert response.status_code == 200
        assert response.json()["decision"] == "ACCEPT"

def test_l4_001_tamper_detection():
    # Scenario: Tampered document detected by Forensic Engine
    with patch("backend_v2.api.main.orchestrator") as mock_orch, \
         patch("backend_v2.api.main.ingestor") as mock_ing, \
         patch("backend_v2.api.main._models_ready", True):
        
        mock_ing.handle_ingestion.return_value = (True, MagicMock(session_id="test-tamper"))
        mock_orch.run_with_bundle.return_value = MagicMock(
            session_id="test-tamper",
            decision="REJECT",
            risk_score=0.9,
            explanation="TAMPER_DETECTED",
            model_dump=lambda mode: {"decision": "REJECT", "risk_score": 0.9}
        )
        
        files = {"document": ("tampered.jpg", b"fake-content", "image/jpeg")}
        response = client.post("/verify", files=files)
        
        assert response.status_code == 200
        assert response.json()["decision"] == "REJECT"

def test_l5_001_system_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
