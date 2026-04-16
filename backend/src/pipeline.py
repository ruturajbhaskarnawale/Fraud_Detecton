import logging
import os
import cv2
import traceback
from .preprocessing.unified import UnifiedPreprocessor
from .preprocessing.quality_check import QualityChecker
from .preprocessing.pdf_handler import PDFHandler
from .ocr.engine import OCREngine
from .parsing.classifier import DocumentClassifier
from .parsing.extractor import FieldExtractor
from .fraud.decision_engine import FraudDecisionEngine
from .face.matcher import FaceMatcher
from .face.liveness import LivenessDetector
from .scoring.engine import RiskScoringEngine

logger = logging.getLogger('KYCPipeline')

class KYCPipeline:
    def __init__(self):
        self.preprocessor = UnifiedPreprocessor()
        self.quality_checker = QualityChecker()
        self.pdf_handler = PDFHandler()
        self.ocr_engine = OCREngine()
        self.classifier = DocumentClassifier()
        self.extractor = FieldExtractor()
        self.fraud_engine = FraudDecisionEngine()
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
            results["id_validation"]["quality"] = {"passed": bool(is_good), "message": q_res.get("issues", "Passed")}
            
            # Normalize and Preprocess (Unified)
            norm_img = self.preprocessor.run_global(id_path)
            
            # 2. OCR & Parsing
            ocr_data = self.ocr_engine.extract_text(norm_img)
            full_text = self.ocr_engine.get_full_text(ocr_data)
            doc_type = self.classifier.classify(full_text)
            fields = self.extractor.extract(full_text, doc_type)
            
            results["id_validation"]["type"] = doc_type
            results["id_validation"]["extracted_fields"] = fields
            results["id_validation"]["raw_ocr_data"] = ocr_data # Capture raw metadata for audit
            
            # 3. Face & Liveness
            if selfie_path:
                liveness_ok, liveness_msg = self.liveness_detector.check_liveness(selfie_path)
                face_res = self.face_matcher.verify(id_path, selfie_path)
                
                results["face_validation"] = {
                    "liveness_passed": bool(liveness_ok),
                    "liveness_message": liveness_msg,
                    "verified": bool(face_res.get("face_match", False)),
                    "similarity": face_res.get("similarity_score", 0.0),
                    "threshold": face_res.get("threshold", 0.0),
                    "quality": face_res.get("quality", 0.5),
                    "status": "COMPLETED"
                }
            else:
                results["face_validation"] = {"status": "PENDING_SELFIE"}

            # 4. Fraud Detection (Hybrid ML + Rules)
            fraud_res = self.fraud_engine.predict(
                ocr_data, 
                fields, 
                results["face_validation"], 
                id_path, 
                doc_type,
                ground_truth=None,
                selfie_provided=bool(selfie_path)
            )
            results["fraud_validation"] = fraud_res
            
            # 5. Risk Scoring
            consistency_issues = []
            for r in fraud_res.get("reason", []):
                label = "data_mismatch"
                if "FACE" in r: label = "face_mismatch"
                elif "NAME" in r or "IDENTITY" in r: label = "name_mismatch"
                elif "DOB" in r: label = "dob_mismatch"
                
                # We filter for actual consistency issues as per previous logic but format them as dicts
                if any(k in r for k in ["INCONSISTENCY", "MISMATCH", "MISSING"]):
                    consistency_issues.append({"type": label, "details": r})

            audit_payload = {
                "tampering_detected": bool(fraud_res.get("status") == "FRAUD"),
                "face_similarity": float(results["face_validation"].get("similarity", 0.0)) if selfie_path else 1.0,
                "face_threshold": float(results["face_validation"].get("threshold", 0.55)) if selfie_path else 0.55,
                "data_consistency_issues": consistency_issues,
                "ocr_confidence": float(sum(d["confidence"] for d in ocr_data)/len(ocr_data)) if ocr_data else 0.0,
                "is_duplicate": False, 
                "multi_face": bool(not results["face_validation"].get("liveness_passed", True)) if selfie_path else False
            }
            
            final = self.scoring_engine.calculate_score(audit_payload)
            results["final_decision"] = final
            
            return results

        except Exception as e:
            logger.error(f"Pipeline failure: {e}")
            logger.error(traceback.format_exc())
            # Ensure a structured failure response that the frontend can still parse
            return {
                "error": str(e),
                "status": "FAILED",
                "id_validation": {"type": "UNKNOWN", "extracted_fields": {}},
                "face_validation": {"similarity": 0.0, "status": "ERROR"},
                "fraud_validation": {"status": "UNKNOWN", "confidence": 0.0, "reason": [str(e)], "tampering_results": []},
                "final_decision": {"decision": "REJECTED", "risk_score": 100, "reasons": ["Internal Pipeline Error"]}
            }
