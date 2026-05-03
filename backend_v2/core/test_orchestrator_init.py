import logging
import sys
import os

# Mock username if not present
if "USERNAME" not in os.environ: os.environ["USERNAME"] = "jotex_user"

# Set PYTHONPATH
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_init")

try:
    from backend_v2.core.orchestrator import PipelineOrchestrator
    print("Import successful. Initializing orchestrator...")
    orchestrator = PipelineOrchestrator()
    print("Orchestrator initialized successfully.")
    
    # Check key modules
    print(f"OCR Engine: {orchestrator.ocr_engine.version if hasattr(orchestrator.ocr_engine, 'version') else 'Initialized'}")
    print(f"Fraud Engine: {orchestrator.fraud_engine.version if hasattr(orchestrator.fraud_engine, 'version') else 'Initialized'}")
    print(f"Forensic Service: {orchestrator.forensic_service.__class__.__name__}")
    
except Exception as e:
    import traceback
    print(f"Initialization FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)
