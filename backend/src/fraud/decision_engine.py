import os
import cv2
import numpy as np
import xgboost as xgb
import difflib
import logging
from src.preprocessing.unified import UnifiedPreprocessor

logger = logging.getLogger('FraudDecisionEngine')

class FeatureEngineer:
    def __init__(self):
        self.preprocessor = UnifiedPreprocessor()

    def get_name_similarity(self, name_ocr, name_ground_truth):
        if not name_ocr or not name_ground_truth:
            return 0.0
        return difflib.SequenceMatcher(None, str(name_ocr).lower(), str(name_ground_truth).lower()).ratio()

    def extract_features(self, ocr_data, extracted_fields, face_validation, image_path, doc_type="pan", ground_truth=None):
        """
        Extracts multi-signal features for ML classification.
        ocr_data: raw output from OCREngine
        extracted_fields: output from FieldExtractor
        face_validation: dict with face matching results
        image_path: path to document image
        ground_truth: dict with true labels (used during training/eval)
        """
        features = {}

        # 1. OCR Confidence
        if ocr_data:
            features["ocr_confidence_avg"] = sum(d.get("confidence", 0) for d in ocr_data) / len(ocr_data)
        else:
            features["ocr_confidence_avg"] = 0.0

        # 2. Missing Fields
        required_fields = []
        if doc_type == "pan":
            required_fields = ["name", "id_number", "dob"]
        elif doc_type == "aadhaar":
            required_fields = ["name", "id_number", "dob", "gender"]
            
        missing_count = sum(1 for k in required_fields if not extracted_fields.get(k, ""))
        features["missing_fields_count"] = missing_count

        # 3. Identity Features (If ground truth provided - essential for training)
        if ground_truth:
            features["name_similarity"] = self.get_name_similarity(extracted_fields.get("name", ""), ground_truth.get("name", ""))
            
            clean_ex_id = str(extracted_fields.get("id_number", "")).replace(" ", "").upper()
            clean_gt_id = str(ground_truth.get("id_number", "")).replace(" ", "").upper()
            features["id_match"] = 1.0 if clean_ex_id == clean_gt_id and clean_gt_id else 0.0
            
            clean_ex_dob = str(extracted_fields.get("dob", "")).replace(" ", "")
            clean_gt_dob = str(ground_truth.get("dob", "")).replace(" ", "")
            features["dob_match"] = 1.0 if clean_ex_dob == clean_gt_dob and clean_gt_dob else 0.0
        else:
            # During inference without ground truth, we can't reliably do ground truth matching.
            # But normally we would match against the user submitted profile data. 
            # We assume a neutral 1.0 match default if API didn't provide reference profile.
            features["name_similarity"] = 1.0
            features["id_match"] = 1.0
            features["dob_match"] = 1.0

        # 4. Face Features
        if face_validation and face_validation.get("status") != "PENDING_SELFIE":
            features["face_detected"] = 1.0 if face_validation.get("similarity", 0.0) > 0 or face_validation.get("verified", False) else 0.0
            features["face_similarity"] = face_validation.get("similarity", 0.0)
            features["face_quality"] = face_validation.get("quality", 0.5)
        else:
            features["face_detected"] = 1.0 # Assume valid face if pending
            features["face_similarity"] = 0.8 # Neutral high score
            features["face_quality"] = 0.5

        # 5. Image Forensics
        try:
            ela_img = self.preprocessor.generate_ela(image_path)
            ela_array = np.array(ela_img)
            features["ela_variance"] = float(np.var(ela_array))
            features["ela_mean"] = float(np.mean(ela_array))
            
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            features["blur_variance"] = float(cv2.Laplacian(img, cv2.CV_64F).var())
            features["brightness_mean"] = float(np.mean(img))
        except Exception as e:
            logger.warning(f"Forensics failed for {image_path}: {e}")
            features["ela_variance"] = 0.0
            features["ela_mean"] = 0.0
            features["blur_variance"] = 0.0
            features["brightness_mean"] = 0.0

        # Feature vector ordering MUST be consistent
        feature_order = [
            "ocr_confidence_avg", "missing_fields_count", 
            "name_similarity", "id_match", "dob_match",
            "face_detected", "face_similarity", "face_quality",
            "ela_variance", "ela_mean", "blur_variance", "brightness_mean"
        ]
        
        feature_vector = [features[k] for k in feature_order]
        return feature_vector, features

class FraudDecisionEngine:
    def __init__(self, model_path=r"c:\Users\rutur\OneDrive\Desktop\jotex\models\fraud_xgb_model.json"):
        self.feature_eng = FeatureEngineer()
        self.model_path = model_path
        self.clf = None
        
        if os.path.exists(self.model_path):
            self.clf = xgb.XGBClassifier()
            self.clf.load_model(self.model_path)
            logger.info("XGBoost Fraud Model loaded successfully.")
        else:
            logger.warning("XGBoost Fraud Model not found. Will run rules-only until trained.")

    def apply_safety_rules(self, extracted_fields, face_validation, selfie_provided=True):
        """
        Hard rules applied before ML decision.
        """
        reasons = []
        status = None
        
        if not selfie_provided:
            return "PENDING_SELFIE", ["SELFIE_NOT_PROVIDED"]
            
        # Hard Rejects
        if not face_validation.get("verified", True):
            sim = face_validation.get("similarity", 0.0)
            if sim < 0.3:  # Below 0.3 is definitively different person / mismatch
                reasons.append("FACE_MISMATCH_SEVERE")
                status = "FRAUD"
                
        # Missing Critical Fields
        name = extracted_fields.get("name", "")
        id_number = extracted_fields.get("id_number", "")
        if not name or not id_number:
            reasons.append("MISSING_CRITICAL_FIELDS")
            if not status: status = "FRAUD"

        return status, reasons

    def predict(self, ocr_data, extracted_fields, face_validation, image_path, doc_type="pan", ground_truth=None, selfie_provided=True):
        """
        Combines rule-based safety layer and ML classification.
        """
        # 1. Evaluate Rule-Based Safety Layer
        rule_status, rule_reasons = self.apply_safety_rules(extracted_fields, face_validation, selfie_provided)
        
        if rule_status == "FRAUD":
            return {
                "status": "FRAUD",
                "confidence": 1.0,
                "reason": rule_reasons
            }
        elif rule_status == "PENDING_SELFIE":
            return {
                "status": "PENDING_SELFIE",
                "confidence": 0.0,
                "reason": rule_reasons
            }

        # 2. Extract Features
        feature_vector, raw_features = self.feature_eng.extract_features(
            ocr_data, extracted_fields, face_validation, image_path, doc_type, ground_truth
        )

        # 3. High Risk Checks (Post-feature extraction)
        if raw_features["ocr_confidence_avg"] < 0.5:
            rule_reasons.append("LOW_OCR_CONFIDENCE")
            
        if raw_features["name_similarity"] < 0.5 and face_validation.get("similarity", 1.0) < 0.5:
            rule_reasons.append("IDENTITY_INCONSISTENCY")

        # 4. ML Prediction
        if self.clf is None:
            # Fallback if model not trained
            status = "FRAUD" if rule_reasons else "GENUINE"
            return {
                "status": status, 
                "confidence": 0.5, 
                "reason": rule_reasons + ["ML_MODEL_UNAVAILABLE"],
                "tampering_results": [{
                    "tamper_score": raw_features.get("ela_variance", 0.0) / 100.0, # Scaled for display
                    "method": "ELA",
                    "details": f"Variance: {raw_features.get('ela_variance', 0.0):.2f}"
                }]
            }
            
        features = np.array(feature_vector).reshape(1, -1)
        
        fraud_prob = float(self.clf.predict_proba(features)[0][1])
        prediction = int(fraud_prob > 0.5)
        
        final_status = "FRAUD" if prediction == 1 or len(rule_reasons) > 0 else "GENUINE"
        
        # Override confidence if rules triggered it, or use ML probability
        confidence = fraud_prob if prediction == 1 else (1.0 - fraud_prob)
        
        if len(rule_reasons) > 0 and prediction == 0:
            final_status = "FRAUD"
            confidence = 0.85 # High risk rules trigger it
            rule_reasons.append("HIGH_RISK_RULES_TRIGGERED")
            
        return {
            "status": final_status,
            "confidence": round(confidence, 4),
            "reason": rule_reasons if final_status == "FRAUD" else [],
            "tampering_results": [{
                "tamper_score": raw_features.get("ela_variance", 0.0) / 100.0,
                "method": "ELA",
                "details": f"Variance: {raw_features.get('ela_variance', 0.0):.2f}"
            }]
        }
