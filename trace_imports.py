import time
print("Importing QualityGate...", flush=True)
from backend_v2.modules.quality_gate import QualityGate
print("Importing PreprocessingEngine...", flush=True)
from backend_v2.modules.preprocessing import PreprocessingEngine
print("Importing OCREngine...", flush=True)
from backend_v2.modules.ocr.ocr_engine import OCREngine
print("Importing DocumentClassifier...", flush=True)
from backend_v2.modules.doc_classifier import DocumentClassifier
print("Importing DocUnderstandingService...", flush=True)
from backend_v2.modules.doc_understanding import DocUnderstandingService
print("Importing FaceService...", flush=True)
from backend_v2.modules.face_service import FaceService
print("Importing LivenessService...", flush=True)
from backend_v2.modules.liveness_service import LivenessService
print("Importing RoutingEngine...", flush=True)
from backend_v2.core.routing import RoutingEngine
print("Importing ForensicService...", flush=True)
from backend_v2.modules.forensic_service import ForensicService
print("Importing FraudEngine...", flush=True)
from backend_v2.modules.fraud_engine import FraudEngine
print("All imports complete!", flush=True)
