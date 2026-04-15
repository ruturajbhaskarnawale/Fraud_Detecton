class RiskScoringEngine:
    def __init__(self):
        # Weighted points for different failures
        self.weights = {
            "tampering": 50,
            "face_mismatch": 35,
            "name_mismatch": 25,
            "dob_mismatch": 20,
            "low_ocr_confidence": 10,
            "duplicate_detected": 40,
            "multi_face_detected": 15
        }

    def calculate_score(self, audit_results):
        """
        audit_results: dict containing flags from all modules
        """
        score = 0
        reasons = []
        
        # 1. Tampering
        if audit_results.get("tampering_detected"):
            score += self.weights["tampering"]
            reasons.append("Image tampering detected (ELA)")
            
        # 2. Face Matching (Similarity-based)
        face_score = audit_results.get("face_similarity", 0.0)
        threshold = audit_results.get("face_threshold", 0.85)
        if face_score < threshold:
            # We add points for failure. If score is far below threshold, maximum points.
            penalty = self.weights["face_mismatch"]
            if face_score < (threshold - 0.2):
                penalty *= 1.5 # Major mismatch
            score += penalty
            reasons.append(f"Face mismatch between ID and Selfie (Similarity: {face_score:.2f})")
            
        # 3. Data Mismatches
        for issue in audit_results.get("data_consistency_issues", []):
            # Defensive check for string issues (legacy or malformed input)
            if isinstance(issue, str):
                issue = {"type": "data_mismatch", "details": issue}
                
            label = issue.get("type", "data_mismatch")
            impact = self.weights.get(label, 20)
            score += impact
            reasons.append(issue.get("details", "Data consistency issue detected"))
                
        # 4. OCR Confidence
        if audit_results.get("ocr_confidence", 1.0) < 0.4:
            score += self.weights["low_ocr_confidence"]
            reasons.append("Low OCR confidence - data may be unreliable")
            
        # 5. Duplicates
        if audit_results.get("is_duplicate"):
            score += self.weights["duplicate_detected"]
            reasons.append("Document identified as a duplicate (Same perceptual hash)")

        # 6. Multi-face
        if audit_results.get("multi_face"):
            score += self.weights["multi_face_detected"]
            reasons.append("Multiple faces detected in selfie/ID")

        # Cap score at 100
        score = min(score, 100)
        
        # Determine Decision
        if score < 20:
            decision = "VALID"
        elif score <= 50:
            decision = "SUSPICIOUS"
        else:
            decision = "REJECTED"
            
        return {
            "risk_score": score,
            "decision": decision,
            "reasons": reasons
        }
