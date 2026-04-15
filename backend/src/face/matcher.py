import cv2
import numpy as np
import os
import logging
from insightface.app import FaceAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FaceMatcher')

class FaceMatcher:
    def __init__(self, model_name='buffalo_l', det_size=(320, 320)):
        """
        Initialize InsightFace models (ArcFace + RetinaFace).
        """
        logger.info(f"Initializing FaceMatcher with {model_name}...")
        try:
            # We use CPU providers as default for compatibility
            # Optimization: Load ONLY detection and recognition to save memory and latency
            self.app = FaceAnalysis(
                name=model_name, 
                providers=['CPUExecutionProvider'],
                allowed_modules=['detection', 'recognition']
            )
            self.app.prepare(ctx_id=0, det_size=det_size)
            self.default_det_size = det_size
            logger.info(f"FaceMatcher initialized. Def Det Size: {det_size}")
        except Exception as e:
            logger.error(f"Failed to initialize FaceMatcher: {e}")
            raise

    def get_face(self, img, det_size=None):
        """
        Detect faces with Fast Detection Path and fallback logic.
        """
        if img is None:
            return None, "INVALID_IMAGE", 0.0
            
        current_det_size = det_size if det_size else self.default_det_size
        self.app.prepare(ctx_id=0, det_size=current_det_size)
        
        # --- Fast Detection Path: Downscale for detection engine speed ---
        h, w = img.shape[:2]
        max_dim = current_det_size[0]
        scale = 1.0
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img_small = cv2.resize(img, (int(w * scale), int(h * scale)))
        else:
            img_small = img
            
        faces = self.app.get(img_small)
        
        # FALLBACK: If no face detected at 320x320, try 640x640
        if not faces and current_det_size == (320, 320):
            logger.info("No face at 320x320, falling back to 640x640...")
            return self.get_face(img, det_size=(640, 640))
        
        if not faces:
            return None, "NO_FACE_DETECTED", 0.0
            
        # Select largest face
        selected_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        
        # Scale back coordinates
        if scale != 1.0:
            selected_face.bbox = selected_face.bbox / scale
            selected_face.kps = selected_face.kps / scale
            
        # Compute Quality Score
        q_score, _ = self._compute_quality_score(img, selected_face)
        
        # Size Check
        face_w = selected_face.bbox[2] - selected_face.bbox[0]
        if face_w < 30:
            return None, "FACE_TOO_SMALL", q_score
        
        return selected_face, "SUCCESS", q_score

    def _compute_quality_score(self, img, face):
        """
        Derive a unified quality score (0.0-1.0).
        """
        face_img = self._crop_face(img, face.bbox)
        if face_img is None: return 0.0, {}
        
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # A. Blur Score
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = np.clip(variance / 60.0, 0, 1)
        
        # B. Brightness Score
        mean_brightness = np.mean(gray)
        bright_score = 1.0 - (min(abs(mean_brightness - 100), abs(mean_brightness - 180)) / 100.0)
        bright_score = np.clip(bright_score, 0, 1)
        
        # C. Size Score
        size_score = np.clip(face_img.shape[1] / 112.0, 0, 1)
        
        # Weighted Quality Score
        total_q = (0.3 * blur_score) + (0.2 * bright_score) + (0.3 * size_score) + (0.2 * face.det_score)
        return round(float(total_q), 4), {}

    def _preprocess_face(self, face_img, q_score=0.5):
        """
        Pure Biometric Path: Only Resize to 112x112.
        Removed all synthetic sharpening/denoising to prevent signal degradation.
        """
        if face_img.shape[0] != 112 or face_img.shape[1] != 112:
            face_img = cv2.resize(face_img, (112, 112), interpolation=cv2.INTER_LANCZOS4)
        
        return face_img

    def _crop_face(self, img, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
        if x2 - x1 <= 0 or y2 - y1 <= 0: return None
        return img[y1:y2, x1:x2]

    def _get_custom_embedding(self, img, face, q_score=0.5):
        """
        Extract embedding using the recognition model directly.
        """
        from insightface.utils import face_align
        aimg = face_align.norm_crop(img, landmark=face.kps, image_size=112)
        aimg = self._preprocess_face(aimg, q_score=q_score)
        rec_model = self.app.models['recognition']
        embedding = rec_model.get_feat(aimg).flatten()
        norm = np.linalg.norm(embedding)
        return embedding / norm

    def verify(self, img1_path, img2_path):
        """
        Optimized verify with Fast Detection and early exit.
        """
        import time
        t0 = time.time()
        
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        if img1 is None or img2 is None:
            return {"face_match": False, "reason": "INVALID_IMAGE_PATH"}

        face1, _, q1 = self.get_face(img1)
        face2, _, q2 = self.get_face(img2)
        if face1 is None or face2 is None: 
            return {"face_match": False, "reason": "NO_FACE_DETECTED", "quality": min(q1, q2)}
        
        # Fast Initial Pass
        sim = float(np.dot(face1.normed_embedding, face2.normed_embedding))
        
        # Early Exit for clear matches
        if sim > 0.88:
            return {
                "face_match": True, "similarity_score": round(sim, 4), "threshold": 0.50,
                "latency_ms": round((time.time()-t0)*1000, 2), "reason": "EARLY_EXIT"
            }
            
        # Full Analysis Path
        emb1 = self._get_custom_embedding(img1, face1, q_score=q1)
        emb2 = self._get_custom_embedding(img2, face2, q_score=q2)
        sim_custom = float(np.dot(emb1, emb2))
        
        # Blend scores if quality is questionable
        if q1 < 0.5 or q2 < 0.5:
            sim_final = (0.7 * sim_custom) + (0.3 * sim)
        else:
            sim_final = sim_custom

        # Balanced Adaptive Threshold
        base_threshold = 0.52
        adj = np.clip((0.5 - ((q1 + q2) / 2)) * 0.08, -0.03, 0.03)
        final_thresh = base_threshold + adj
        
        return {
            "face_match": bool(sim_final >= final_thresh),
            "similarity_score": round(sim_final, 4),
            "threshold": round(final_thresh, 4),
            "latency_ms": round((time.time()-t0)*1000, 2),
            "reason": "MATCH_CONFIRMED" if sim_final >= final_thresh else "IDENTITY_MISMATCH"
        }

    def detect_faces(self, image_path):
        """Legacy compatibility wrapper."""
        img = cv2.imread(image_path)
        if img is None: return 0, []
        faces = self.app.get(img)
        return len(faces), [f.bbox for f in faces]
