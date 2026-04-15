import os
import joblib
import numpy as np
import cv2
from backend.src.preprocessing.unified import UnifiedPreprocessor
from backend.src.ocr.engine import OCREngine
from backend.src.parsing.classifier import DocumentClassifier
from backend.src.parsing.extractor import FieldExtractor
from backend.src.face.matcher import FaceMatcher

class RF_FraudEngine:
    def __init__(self):
        self.model_path = r"c:\Users\rutur\OneDrive\Desktop\jotex\models\fraud_rf_model.pkl"
        if os.path.exists(self.model_path):
            self.clf = joblib.load(self.model_path)
        else:
            self.clf = None
            
        self.preprocessor = UnifiedPreprocessor()
        self.ocr_engine = OCREngine()
        self.doc_classifier = DocumentClassifier()
        self.field_extractor = FieldExtractor()
        self.face_matcher = FaceMatcher()

    def detect_fraud(self, image_path, ground_truth=None):
        """
        Extract signals and predict fraud using the Random Forest model.
        ground_truth: optional dict for consistency checks during evaluation.
        """
        if self.clf is None:
            return {"fraud_probability": 0.5, "issue": "Model not found"}
            
        # 1. ELA Score
        ela_img = self.preprocessor.generate_ela(image_path)
        ela_score = np.mean(np.array(ela_img))
        
        # 2. OCR & Consistency
        img = self.preprocessor.run_global(image_path)
        ocr_data = self.ocr_engine.extract_text(img)
        full_text = self.ocr_engine.get_full_text(ocr_data)
        doc_type = self.doc_classifier.classify(full_text)
        fields = self.field_extractor.extract(full_text, doc_type)
        
        avg_conf = sum(d['confidence'] for d in ocr_data) / len(ocr_data) if ocr_data else 0
        
        # 3. Face
        count, _ = self.face_matcher.detect_faces(image_path)
        has_face = 1 if count > 0 else 0
        
        # 4. Consistency logic (if ground truth available, or internal rule matching)
        # Using a default matching (self-consistency) if no ground truth
        # For evaluation, we use the ground truth from annotations.
        if ground_truth:
            name_match = 1 if str(ground_truth.get('name', '')).lower() in str(fields.get('name', '')).lower() else 0
            id_match = 1 if str(ground_truth.get('id_number', '')).replace(' ', '') == str(fields.get('id_number', '')).replace(' ', '') else 0
        else:
            name_match = 1 # Neutral
            id_match = 1
            
        features = np.array([[ela_score, name_match, id_match, avg_conf, has_face]])
        
        prob = self.clf.predict_proba(features)[0][1]
        prediction = int(self.clf.predict(features)[0])
        
        return {
            "is_fraud": bool(prediction),
            "fraud_probability": prob,
            "signals": {
                "ela_score": ela_score,
                "name_match": name_match,
                "id_match": id_match,
                "ocr_confidence": avg_conf,
                "face_detected": bool(has_face)
            }
        }
