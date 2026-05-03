import os
import sys
import logging

if "USERNAME" not in os.environ: os.environ["USERNAME"] = "jotex_user"
sys.path.append(os.getcwd())

from backend_v2.modules.fraud_engine import FraudEngine

logging.basicConfig(level=logging.INFO)

def test_fraud():
    print("Initializing Fraud Engine...")
    engine = FraudEngine()
    print("Fraud Engine initialized.")
    
    intelligence = {
        "identity_score": 0.95,
        "liveness_score": 0.98,
        "forensic_score": 0.05,
        "document_score": 0.99,
        "geo_risk": 0.1,
        "device_risk": 0.0,
        "session_risk": 0.0,
        "ip_rep_risk": 0.0
    }
    
    session_data = {
        "ip_address": "1.1.1.1",
        "device_id": "TEST_DEV",
        "resident_country": "IN",
        "ip_location": "IN"
    }
    
    print("Analyzing...")
    res = engine.analyze(intelligence, session_data)
    print(f"Result: {res}")

if __name__ == "__main__":
    test_fraud()
