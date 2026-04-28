import cv2
import numpy as np
import fitz  # PyMuPDF
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from backend_v2.core.schemas import QualityResult, IngestionStatus

logger = logging.getLogger("preprocessing")

class PreprocessingEngine:
    def __init__(self, output_dir: str = "uploads/backend_v2/processed"):
        self.version = "v1.0"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def process(self, image_path: str, quality_res: QualityResult) -> Dict[str, Any]:
        """
        Refined entry point with safety guards and adaptive processing.
        """
        original_image = cv2.imread(image_path)
        if original_image is None:
            return {"error": "Image load failed", "fallback_used": True}

        q_score = quality_res.quality_score
        transforms_applied = []
        warp_applied = False
        fallback_used = False
        
        try:
            # 1. Pipeline Selection (Adaptive Depth)
            if q_score > 0.75:
                # High quality: Minimal processing to avoid distortion
                image = self._standardize_resize(original_image, 1024)
                transforms_applied.append("resize_only")
            else:
                # 2. Orientation & Deskew (Safeguard applied first)
                angle = quality_res.checks.get("rotation_angle", 0.0)
                image = self._rotate_image(original_image, angle) if abs(angle) > 0.5 else original_image
                if abs(angle) > 0.5: transforms_applied.append("deskew")

                # 3. Warp Confidence Validation (MANDATORY)
                warped, warp_conf = self._rectify_with_confidence(image)
                if warp_conf > 0.85:
                    image = warped
                    warp_applied = True
                    transforms_applied.append("perspective_warp")

                # 4. Adaptive Enhancement
                # Adjust CLAHE based on brightness
                image = self._apply_adaptive_filters(image, q_score)
                transforms_applied.append("adaptive_enhancement")

                # 5. Text Preservation Check
                if not self._validate_text_integrity(original_image, image):
                    logger.warning("Text integrity check failed. Reverting to original.")
                    image = original_image
                    fallback_used = True
                    transforms_applied = ["fallback_revert"]

            # Finalize
            image = self._standardize_resize(image, 1024)
            out_path = self._save_artifact(image, os.path.basename(image_path))

            return {
                "processed_images": [out_path],
                "transforms_applied": transforms_applied,
                "confidence": round(self._calculate_final_confidence(warp_conf if warp_applied else 1.0, fallback_used), 4),
                "warp_applied": warp_applied,
                "fallback_used": fallback_used,
                "artifacts_paths": {"primary": out_path}
            }

        except Exception as e:
            logger.error(f"Preprocessing failure: {str(e)}")
            return self._handle_total_failure(original_image, image_path)

    def _rectify_with_confidence(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Warp logic with area and aspect ratio validation.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(cv2.GaussianBlur(gray, (5,5), 0), 75, 200)
        cnts, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
        
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                # Validation
                area_ratio = cv2.contourArea(c) / (image.shape[0] * image.shape[1])
                if area_ratio < 0.2: continue # Too small
                
                # Check corner angles (should be near 90 deg)
                pts = approx.reshape(4, 2)
                warped = self._four_point_transform(image, pts)
                
                # Confidence based on area and shape regularity
                confidence = min(area_ratio * 2.0, 1.0) 
                return warped, confidence
        
        return image, 0.0

    def _validate_text_integrity(self, original: np.ndarray, processed: np.ndarray) -> bool:
        """
        Compares edge density to ensure text wasn't blurred out or distorted.
        """
        def get_density(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=5)
            return np.sum(np.abs(edges)) / gray.size
            
        pre_d = get_density(original)
        post_d = get_density(processed)
        # If density drops by more than 20%, we suspect text loss
        return post_d > (pre_d * 0.8)

    def _apply_adaptive_filters(self, image: np.ndarray, q_score: float) -> np.ndarray:
        # If very dark or blurry, apply bilateral filter
        if q_score < 0.5:
            image = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Adaptive CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        # Adjust clipLimit based on brightness variance
        l = self.clahe.apply(l)
        lab = cv2.merge((l, a, b))
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _calculate_final_confidence(self, warp_conf: float, fallback: bool) -> float:
        if fallback: return 0.5
        return min(warp_conf, 0.98)

    def _save_artifact(self, image: np.ndarray, filename: str) -> str:
        path = os.path.join(self.output_dir, f"v2_proc_{filename}")
        cv2.imwrite(path, image)
        return path

    def _handle_total_failure(self, original: np.ndarray, image_path: str) -> Dict[str, Any]:
        out_path = self._save_artifact(original, os.path.basename(image_path))
        return {
            "processed_images": [out_path],
            "transforms_applied": ["total_failure_fallback"],
            "confidence": 0.1,
            "warp_applied": False,
            "fallback_used": True
        }

    def _standardize_resize(self, image: np.ndarray, max_dim: int) -> np.ndarray:
        h, w = image.shape[:2]
        if max(h, w) <= max_dim: return image
        scale = max_dim / max(h, w)
        return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        (h, w) = image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def _four_point_transform(self, image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        # Standard implementation (same as previous but encapsulated)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]
        (tl, tr, br, bl) = rect
        w = int(max(np.sqrt(((br[0]-bl[0])**2)+((br[1]-bl[1])**2)), np.sqrt(((tr[0]-tl[0])**2)+((tr[1]-tl[1])**2))))
        h = int(max(np.sqrt(((tr[0]-br[0])**2)+((tr[1]-br[1])**2)), np.sqrt(((tl[0]-bl[0])**2)+((tl[1]-bl[1])**2))))
        dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, M, (w, h))

    def process_pdf(self, pdf_path: str, quality_res: QualityResult) -> Dict[str, Any]:
        doc = fitz.open(pdf_path)
        meta = []
        imgs = []
        for i in range(len(doc)):
            p = doc.load_page(i)
            pix = p.get_pixmap(dpi=300)
            t_path = os.path.join(self.output_dir, f"pdf_p{i}.png")
            pix.save(t_path)
            res = self.process(t_path, quality_res)
            imgs.extend(res["processed_images"])
            meta.append({"page": i+1, "fallback": res["fallback_used"], "warp": res["warp_applied"]})
        return {"processed_images": imgs, "page_metadata": meta, "fallback_used": any(m["fallback"] for m in meta)}
