import time
import asyncio
import concurrent.futures
from fastapi.testclient import TestClient
from backend_v2.api.main import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def perform_single_request():
    # We mock the heavy orchestrator but let the API handle the request
    # This tests the FastAPI overhead and concurrency handling
    with patch("backend_v2.api.main.orchestrator") as mock_orch, \
         patch("backend_v2.api.main.ingestor") as mock_ing, \
         patch("backend_v2.api.main._models_ready", True):
        
        mock_ing.handle_ingestion.return_value = (True, MagicMock(session_id="test-perf"))
        mock_orch.run_with_bundle.return_value = MagicMock(
            session_id="test-perf",
            decision="ACCEPT",
            risk_score=0.1,
            model_dump=lambda mode: {"decision": "ACCEPT", "risk_score": 0.1}
        )
        
        start = time.perf_counter()
        files = {"document": ("test.jpg", b"fake-content", "image/jpeg")}
        response = client.post("/verify", files=files)
        latency = (time.perf_counter() - start) * 1000
        return response.status_code, latency

def test_l5_001_concurrency_load():
    """
    Execute 10 concurrent requests and measure mean latency.
    """
    num_requests = 10
    latencies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(perform_single_request) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            assert status == 200
            latencies.append(latency)
    
    mean_latency = sum(latencies) / len(latencies)
    print(f"Mean Latency (10 reqs, 5 workers): {mean_latency:.2f}ms")
    assert mean_latency < 1000 # Target: < 1s for mocked backend

def test_l5_002_resource_stability():
    """
    Check if memory usage remains stable after a burst.
    """
    import os
    import psutil
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024 # MB
    
    # Run a small burst
    test_l5_001_concurrency_load()
    
    mem_after = process.memory_info().rss / 1024 / 1024 # MB
    growth = mem_after - mem_before
    print(f"Memory Growth: {growth:.2f} MB")
    # In a real environment, we'd check for leaks here
    assert growth < 50 # Allow 50MB overhead for caching/buffering
