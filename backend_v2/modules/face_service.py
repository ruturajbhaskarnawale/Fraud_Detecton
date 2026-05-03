import numpy as np
import logging
import torch
import cv2
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from backend_v2.core.face_alignment import FaceAlignment

logger = logging.getLogger("face_service_v2")

class FaceService:
    def __init__(self):
        self.version = "v1.0"
        self.base_match_threshold = 0.65
        self.quality_threshold = 0.70
        self.pose_threshold_yaw = 30
        self.pose_threshold_pitch = 25
        
        # Real Model setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.aligner = FaceAlignment(image_size=112)
        
        # Load weights lazily or now? Let's do lazy check
        self.weights_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "arcface_resnet50_best.pth"
        self.model = None

    def _ensure_model(self, num_classes=51): # num_classes is only for training, inference only uses backbone
        if self.model is None:
            from backend_v2.models.resnet_arcface import ArcFaceResNet50
            self.model = ArcFaceResNet50(num_classes=num_classes).to(self.device)
            if self.weights_path.exists():
                self.model.load_state_dict(torch.load(self.weights_path, map_location=self.device), strict=False)
                logger.info(f"Loaded face weights from {self.weights_path}")
            self.model.eval()


    def process(self, selfie_path: str, id_face_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Hardened face processing with multi-scale detection and MediaPipe fallback.
        """
        selfie_faces = self._detect_faces_robust(selfie_path)
        
        if not selfie_faces:
            # CRITICAL FIX: Explicitly flag missing face to prevent bypass
            return self._result_v2(face_detected=False, status="ABSTAIN", flags={"no_face": True, "BIOMETRIC_MISSING": True})
            
        # Select most prominent face (largest area)
        primary_face = sorted(selfie_faces, key=lambda x: (x["bbox"][2]-x["bbox"][0]) * (x["bbox"][3]-x["bbox"][1]), reverse=True)[0]
        
        quality_score = primary_face["quality"]
        
        flags = {
            "multiple_faces": len(selfie_faces) > 1,
            "no_face": False,
            "low_quality_face": quality_score < self.quality_threshold,
            "INVALID_FACE_EMBEDDING": np.all(primary_face["embedding"] == 0)
        }

        # 2. Matching logic (Improved calibration)
        match_score = -1.0 # Use -1.0 to distinguish from 0.0 (mismatch)
        if id_face_path:
            id_faces = self._detect_faces_robust(id_face_path)
            if id_faces:
                # Compare primary selfie face with primary ID face
                match_score = self._compute_match(primary_face["embedding"], id_faces[0]["embedding"])
            else:
                logger.warning("ID Face not detected after robust attempts.")
                flags["ID_FACE_MISSING"] = True

        # 3. Status Determination
        # Thresholds: > 0.8 (Strong), 0.5-0.8 (Weak), < 0.5 (Mismatch)
        status = "FAIL"
        if match_score > 0.65:
            status = "PASS"
        elif match_score == -1.0:
            status = "ABSTAIN"
        elif 0.4 < match_score <= 0.65:
            status = "REVIEW"
            
        # Fail-safe: Any critical flag forces non-ACCEPT
        if flags["multiple_faces"] or flags["low_quality_face"] or flags.get("ID_FACE_MISSING"):
            if status == "PASS": status = "REVIEW"

        return {
            "face_detected": True,
            "face_count": len(selfie_faces),
            "face_quality_score": round(quality_score, 4),
            "face_match_score": round(max(0.0, match_score), 4),
            "identity_score": round(match_score, 4), # Keep -1.0 for orchestrator
            "status": status,
            "flags": flags
        }

    def _detect_faces_robust(self, image_path: str) -> List[Dict]:
        """
        Attempts face detection with multiple scales and fallbacks.
        """
        self._ensure_model()
        from PIL import Image
        import torch
        
        # 1. Load and Preprocess
        cv_img = cv2.imread(image_path)
        if cv_img is None: return []
        
        # Normalize brightness/contrast for detection
        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        cv_img_norm = cv2.cvtColor(cv2.merge((cl,a,b)), cv2.COLOR_LAB2BGR)
        
        scales = [1.0, 0.5, 2.0] # Try original, downscaled, and upscaled
        for scale in scales:
            if scale != 1.0:
                h, w = cv_img_norm.shape[:2]
                scaled_img = cv2.resize(cv_img_norm, (int(w*scale), int(h*scale)))
            else:
                scaled_img = cv_img_norm
                
            pil_img = Image.fromarray(cv2.cvtColor(scaled_img, cv2.COLOR_BGR2RGB))
            
            # Primary: MTCNN
            boxes, probs, points = self.aligner.detector.detect(pil_img, landmarks=True)
            
            if boxes is not None:
                faces = []
                for i in range(len(boxes)):
                    # Align and embed
                    # Scale boxes back to 1.0
                    box = (boxes[i] / scale).tolist()
                    prob = float(probs[i])
                    
                    # Align requires Image
                    orig_pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                    face_tensor = self.aligner.align(orig_pil) 
                    
                    with torch.no_grad():
                        embedding = self.model.backbone(face_tensor.unsqueeze(0).to(self.device))
                        embedding = embedding.squeeze().cpu().numpy()
                    
                    faces.append({
                        "bbox": box,
                        "embedding": embedding,
                        "quality": prob
                    })
                return faces

        # Fallback: MediaPipe (very robust for small faces)
        try:
            import mediapipe as mp
            mp_face_detection = mp.solutions.face_detection
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
                results = face_detection.process(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                if results.detections:
                    faces = []
                    for detection in results.detections:
                        # Extract embedding using aligner fallback
                        orig_pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                        face_tensor = self.aligner.align(orig_pil)
                        with torch.no_grad():
                            embedding = self.model.backbone(face_tensor.unsqueeze(0).to(self.device))
                            embedding = embedding.squeeze().cpu().numpy()
                        
                        faces.append({
                            "bbox": [0,0,0,0], # MP uses relative, we just need the embedding
                            "embedding": embedding,
                            "quality": float(detection.score[0])
                        })
                    return faces
        except Exception as e:
            logger.warning(f"MediaPipe fallback failed: {e}")

        return []

    def _compute_match(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        if np.all(emb1 == 0) or np.all(emb2 == 0): return 0.0
        return float(np.dot(emb1, emb2))


    def _result_v2(self, face_detected: bool, status: str, flags: Dict) -> Dict:
        return {
            "face_detected": face_detected,
            "face_count": 0,
            "face_quality_score": 0.0,
            "face_match_score": 0.0,
            "identity_score": -1.0, # CRITICAL: default to -1
            "status": status,
            "flags": flags
        }
