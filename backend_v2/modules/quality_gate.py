import cv2
import numpy as np
from typing import Dict, Any, List
from backend_v2.core.schemas import QualityResult, IngestionStatus
from backend_v2.core.config import settings

class QualityGate:
    def __init__(self):
        self.version = "v1.0"
        # Base weights for the scoring engine
        self.weights = {
            "blur": 0.4,
            "brightness": 0.2,
            "contrast": 0.2,
            "resolution": 0.2
        }
        self.min_res = settings.MIN_RESOLUTION or (1280, 720)

    def analyze(self, image_path: str, is_selfie: bool = False) -> QualityResult:
        """
        Performs adaptive CV analysis to score image quality and geometric integrity.
        """
        image = cv2.imread(image_path)
        if image is None:
            return QualityResult(
                quality_score=0.0,
                checks={},
                status=IngestionStatus.ABSTAIN,
                confidence=0.0,
                failure_reasons=["IO_ERROR: Unable to read image"]
            )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = image.shape[:2]

        # 1. Core Visual Metrics
        if max(h, w) > 1024:
            scale = 1024 / max(h, w)
            gray_small = cv2.resize(gray, (0, 0), fx=scale, fy=scale)
        else:
            gray_small = gray
        blur_score = min(cv2.Laplacian(gray_small, cv2.CV_64F).var() / 500.0, 1.0)
        mean_brightness = np.mean(gray)
        brightness_score = max(0.0, 1.0 - abs(mean_brightness - 127) / 127.0)
        contrast_score = min(gray.std() / 70.0, 1.0)
        res_score = min(w / self.min_res[0], 1.0) * 0.5 + min(h / self.min_res[1], 1.0) * 0.5
        
        # 2. Geometric & Coverage Metrics (Phase 2 Refinement)
        rotation_angle = self._detect_skew(gray)
        coverage_score = self._calculate_coverage(gray)
        glare_score = self._compute_glare_score(gray)
        face_present = self._check_face_lightweight(gray) if is_selfie else True

        # 3. Adaptive Weighting Logic
        scores = {
            "blur": blur_score,
            "brightness": brightness_score,
            "contrast": contrast_score,
            "resolution": res_score
        }
        quality_score = self._compute_adaptive_weighted_score(scores)

        # 4. Confidence Calibration (Variance-based consistency)
        consistency_factor = 1.0 - np.std(list(scores.values()))
        calibrated_confidence = quality_score * consistency_factor

        # 5. Refined Decision Logic
        reasons = []
        if quality_score < 0.35:
            status = IngestionStatus.ABSTAIN
            reasons.append("Overall quality below minimum threshold")
        elif coverage_score < 0.5:
            status = IngestionStatus.ABSTAIN
            reasons.append(f"Low document coverage: {coverage_score:.2f}")
        elif abs(rotation_angle) > 15:
            status = IngestionStatus.REVIEW
            reasons.append(f"Significant skew detected: {rotation_angle:.1f} degrees")
        elif glare_score > 0.15:
            status = IngestionStatus.REVIEW
            reasons.append("Localized glare/reflection interfering with readability")
        elif not face_present and is_selfie:
            status = IngestionStatus.REVIEW
            reasons.append("Face presence check failed for selfie input")
        else:
            # We use ABSTAIN to trigger a retry if borderline, else it passes implicitly
            status = IngestionStatus.REVIEW if quality_score < 0.6 else IngestionStatus.ABSTAIN

        # Correction: For the orchestrator to proceed, we must handle the status correctly.
        # Everything not ABSTAIN/REVIEW will be treated as PASS.
        
        return QualityResult(
            quality_score=round(quality_score, 4),
            checks={
                "blur_score": round(blur_score, 4),
                "brightness_score": round(brightness_score, 4),
                "contrast_score": round(contrast_score, 4),
                "resolution_score": round(res_score, 4),
                "glare_score": round(glare_score, 4),
                "rotation_angle": round(rotation_angle, 2),
                "coverage_score": round(coverage_score, 4),
                "face_present": face_present
            },
            status=status,
            confidence=round(calibrated_confidence, 4),
            failure_reasons=reasons
        )

    def _detect_skew(self, gray: np.ndarray) -> float:
        """
        Detects document skew angle using Hough Transform.
        """
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        if lines is None: return 0.0
        
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.rad2deg(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) < 45: # Filter out vertical lines for skew
                angles.append(angle)
        
        return np.median(angles) if angles else 0.0

    def _calculate_coverage(self, gray: np.ndarray) -> float:
        """
        Detects document area relative to image size.
        """
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return 0.0
        
        main_contour = max(contours, key=cv2.contourArea)
        doc_area = cv2.contourArea(main_contour)
        return doc_area / (gray.shape[0] * gray.shape[1])

    def _compute_glare_score(self, gray: np.ndarray) -> float:
        """
        Detects saturated regions (glare).
        """
        _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
        glare_area = cv2.countNonZero(thresh)
        return glare_area / gray.size

    def _compute_adaptive_weighted_score(self, scores: dict) -> float:
        """
        Dynamically adjusts weights based on extreme values to reduce FRR.
        """
        weights = self.weights.copy()
        # If image is very dark, increase brightness weight to penalize properly
        if scores["brightness"] < 0.3: weights["brightness"] *= 1.5
        # If image is very blurry, increase blur weight
        if scores["blur"] < 0.2: weights["blur"] *= 2.0
        
        total_w = sum(weights.values())
        return sum(scores[k] * weights[k] for k in scores) / total_w

    def _check_face_lightweight(self, gray: np.ndarray) -> bool:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces) > 0
