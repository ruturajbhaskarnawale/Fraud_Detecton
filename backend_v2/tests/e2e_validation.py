import os
import sys
import uuid
import json
import logging
from typing import Dict, Any

# Mock setup
if "USERNAME" not in os.environ: os.environ["USERNAME"] = "jotex_user"
sys.path.append(os.getcwd())

from backend_v2.core.orchestrator import PipelineOrchestrator
from backend_v2.core.schemas import EvidenceBundle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2E_HARDEN")

def run_validation():
    print("\n" + "="*50, flush=True)
    print("START: VERIDEX E2E PIPELINE HARDENING TEST", flush=True)
    print("="*50, flush=True)

    orchestrator = PipelineOrchestrator()
    session_id = str(uuid.uuid4())
    
    # Test Data Paths
    data_dir = "backend_v2/tests/data"
    doc_path = os.path.join(data_dir, "clean_id.jpg")
    selfie_path = os.path.join(data_dir, "face_a_1.jpg")
    
    if not os.path.exists(doc_path):
        print(f"[ERROR] Missing test data: {doc_path}", flush=True)
        return

    print(f"\n[PHASE 1] Initializing Session: {session_id}", flush=True)
    bundle = EvidenceBundle(
        session_id=session_id,
        raw_input_path=doc_path,
        selfie_path=selfie_path,
        entity_id="test_user_001",
        metadata={
            "ip_address": "192.168.1.1",
            "device_id": "DEV_TEST_001",
            "ip_location": "IN",
            "resident_country": "IN"
        }
    )

    print("\n[PHASE 2] Executing Pipeline...", flush=True)
    try:
        result = orchestrator.run_with_bundle(bundle)
        print("[SUCCESS] Pipeline execution successful.", flush=True)
    except Exception as e:
        print(f"[ERROR] Pipeline CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return

    print("\n[PHASE 3] Module Output Validation", flush=True)
    
    # 1. OCR
    print(f"  - OCR Text Length: {len(result.ocr.text)}", flush=True)
    print(f"  - OCR Confidence: {result.ocr.confidence}", flush=True)

    # 2. Document Understanding
    print(f"  - Document Type: {result.document.document_type}", flush=True)
    print(f"  - Extracted Fields: {list(result.document.fields.keys())}", flush=True)

    # 3. Biometrics
    print(f"  - Face Similarity: {result.biometrics.face_similarity}", flush=True)
    print(f"  - Liveness Score: {result.biometrics.liveness_score}", flush=True)
    print(f"  - Biometric Status: {result.biometrics.status}", flush=True)

    # 4. Forensics
    print(f"  - Tamper Score: {result.forensics.tamper_score}", flush=True)
    print(f"  - Is Altered: {result.forensics.is_altered}", flush=True)
    
    # 5. Fraud
    print(f"  - Fraud Score: {result.fraud.fraud_score}", flush=True)
    print(f"  - Rules Triggered: {result.fraud.rules_triggered}", flush=True)

    # 6. Final Decision
    print(f"\n[FINAL] Decision: {result.decision}", flush=True)
    print(f"[FINAL] Risk Score: {result.risk_score}", flush=True)

    print("\n[PHASE 4] Database Persistence Check", flush=True)
    from backend_v2.database.persistence import PersistenceService
    persistence = PersistenceService()
    db_res = persistence.get_session_result(session_id)
    if db_res:
        print(f"[SUCCESS] DB Retrieval for {session_id}", flush=True)
        if db_res.decision == result.decision:
            print("[SUCCESS] DB Data Consistency: MATCH", flush=True)
        else:
            print("[ERROR] DB Data Consistency: MISMATCH", flush=True)
    else:
        print("[ERROR] DB Persistence FAILED: Session not found in DB.", flush=True)
    persistence.close()

    print("\n" + "="*50, flush=True)
    print("FINISH: E2E VALIDATION COMPLETE", flush=True)
    print("="*50, flush=True)


if __name__ == "__main__":
    run_validation()
