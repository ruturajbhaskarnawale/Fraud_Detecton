from .tampering import TamperDetector
from .rules import FraudRules
import imagehash
from PIL import Image
import logging

logger = logging.getLogger('FraudEngine')

class FraudEngine:
    def __init__(self):
        self.tamper_detector = TamperDetector()
        self.consistency_rules = FraudRules()

    def check_tampering(self, image_path):
        """Run ELA to detect image tampering."""
        is_tampered, score = self.tamper_detector.is_tampered(image_path)
        return {
            "is_tampered": is_tampered,
            "tamper_score": float(score)
        }

    def check_data_consistency(self, extracted_fields_list):
        """Check for name/dob mismatches across documents."""
        issues = self.consistency_rules.verify_data_consistency(extracted_fields_list)
        return issues

    def get_perceptual_hash(self, image_path):
        """Generate a pHash for duplicate detection."""
        try:
            hash_obj = imagehash.phash(Image.open(image_path))
            return str(hash_obj)
        except Exception as e:
            logger.error(f"Error generating hash: {e}")
            return None

    def run_full_audit(self, primary_doc_data, doc_paths):
        """
        Run all fraud checks for a submission.
        
        Args:
            primary_doc_data: list of dicts from FieldExtractor
            doc_paths: list of image paths
        """
        results = {
            "tampering_results": [],
            "data_consistency_issues": [],
            "hashes": [],
            "overall_status": "PASS"
        }
        
        # 1. Tampering Checks
        for path in doc_paths:
            res = self.check_tampering(path)
            res["path"] = path
            results["tampering_results"].append(res)
            if res["is_tampered"]:
                results["overall_status"] = "WARNING"
                
        # 2. Data Mismatch
        results["data_consistency_issues"] = self.check_data_consistency(primary_doc_data)
        if results["data_consistency_issues"]:
            results["overall_status"] = "WARNING"
            
        # 3. Hash Generation for duplicates
        for path in doc_paths:
            p_hash = self.get_perceptual_hash(path)
            results["hashes"].append({"path": path, "hash": p_hash})
            
        return results
