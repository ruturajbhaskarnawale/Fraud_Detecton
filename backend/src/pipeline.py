import logging
import os
import cv2
import traceback
from .preprocessing.normalizer import ImageNormalizer
from .preprocessing.quality_check import QualityChecker
from .preprocessing.pdf_handler import PDFHandler
from .ocr.engine import OCREngine
from .parsing.classifier import DocumentClassifier
from .parsing.extractor import FieldExtractor
from .fraud.engine import FraudEngine
from .face.matcher import FaceMatcher
from .face.liveness import LivenessDetector
from .scoring.engine import RiskScoringEngine

logger = logging.getLogger('KYCPipeline')

class KYCPipeline:
    def __init__(self):
        self.normalizer = ImageNormalizer()
        self.quality_checker = QualityChecker()
        self.pdf_handler = PDFHandler()
        self.ocr_engine = OCREngine()
        self.classifier = DocumentClassifier()
        self.extractor = FieldExtractor()
        self.fraud_engine = FraudEngine()
        self.face_matcher = FaceMatcher()
        self.liveness_detector = LivenessDetector()
        self.scoring_engine = RiskScoringEngine()

    def process_verification(self, id_path, selfie_path=None):
        """
        Full end-to-end KYC process.
        """
        results = {
            "id_validation": {},
            "face_validation": {},
            "fraud_validation": {},
            "final_decision": {}
        }

        try:
            # 1. Preprocessing & Quality
            raw_img = cv2.imread(id_path)
            if raw_img is None:
                raise ValueError("Could not read ID image")
                
            # Quality Check
            is_good, q_res = self.quality_checker.check(raw_img)
            results["id_validation"]["quality"] = {"passed": is_good, "message": q_res.get("issues", "Passed")}
            
            # Normalize
            norm_img = self.normalizer.normalize(raw_img)
            
            # 2. OCR & Parsing
            ocr_data = self.ocr_engine.extract_text(norm_img)
            full_text = self.ocr_engine.get_full_text(ocr_data)
            doc_type = self.classifier.classify(full_text)
            fields = self.extractor.extract(full_text, doc_type)
            
            results["id_validation"]["type"] = doc_type
            results["id_validation"]["extracted_fields"] = fields
            
            # 3. Face & Liveness
            if selfie_path:
                liveness_ok, liveness_msg = self.liveness_detector.check_liveness(selfie_path)
                face_res = self.face_matcher.verify(id_path, selfie_path)
                
                results["face_validation"] = {
                    "liveness_passed": liveness_ok,
                    "liveness_message": liveness_msg,
                    "verified": face_res["verified"],
                    "similarity": face_res.get("similarity_score", 0.0),
                    "threshold": face_res.get("threshold", 0.0)
                }

            # 4. Fraud Detection
            # Passing list of extracted fields (just one doc for now, can be expanded)
            fraud_res = self.fraud_engine.run_full_audit([fields], [id_path])
            results["fraud_validation"] = fraud_res
            
            # 5. Risk Scoring
            audit_payload = {
                "tampering_detected": any(r["is_tampered"] for r in fraud_res["tampering_results"]),
                "face_similarity": results["face_validation"].get("similarity", 1.0) if selfie_path else 1.0,
                "face_threshold": results["face_validation"].get("threshold", 0.85) if selfie_path else 0.85,
                "data_consistency_issues": fraud_res["data_consistency_issues"],
                "ocr_confidence": sum(d["confidence"] for d in ocr_data)/len(ocr_data) if ocr_data else 0.0,
                "is_duplicate": False, # Would check against DB in API layer
                "multi_face": not results["face_validation"].get("liveness_passed", True) # Simplified
            }
            
            final = self.scoring_engine.calculate_score(audit_payload)
            results["final_decision"] = final
            
            return results

        except Exception as e:
            logger.error(f"Pipeline failure: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "status": "FAILED"}
