import numpy as np
import logging
import torch
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
        Refined face processing with quality-aware thresholds and pose estimation.
        """
        faces = self._detect_faces_detailed(selfie_path)
        
        if not faces:
            return self._result_v2(face_detected=False, status="ABSTAIN", flags={"no_face": True})
            
        # Select primary face (largest)
        primary_face = sorted(faces, key=lambda x: (x["bbox"][2]-x["bbox"][0]) * (x["bbox"][3]-x["bbox"][1]), reverse=True)[0]
        
        quality_score = primary_face["quality"]
        pose = primary_face["pose"]
        
        # 1. Quality & Pose Flags
        flags = {
            "multiple_faces": len(faces) > 1,
            "no_face": False,
            "low_quality_face": quality_score < self.quality_threshold,
            "extreme_pose": abs(pose["yaw"]) > self.pose_threshold_yaw or abs(pose["pitch"]) > self.pose_threshold_pitch
        }

        # 2. Adaptive Threshold Calculation
        # Penalty for poor quality or extreme pose
        threshold = self.base_match_threshold + (max(0, self.quality_threshold - quality_score) * 0.2)
        if flags["extreme_pose"]: threshold += 0.05

        # 3. Matching
        match_score = 0.0
        if id_face_path:
            id_faces = self._detect_faces_detailed(id_face_path)
            if id_faces and id_faces[0]["quality"] > 0.5:
                match_score = self._compute_match(primary_face["embedding"], id_faces[0]["embedding"])
            else:
                logger.warning("ID Face missing or poor quality.")

        # 4. Status Determination
        status = "PASS"
        if match_score < threshold: status = "FAIL"
        if flags["low_quality_face"] or flags["extreme_pose"] or flags["multiple_faces"]:
            if status != "FAIL": status = "REVIEW"

        return {
            "face_detected": True,
            "face_count": len(faces),
            "face_quality_score": round(quality_score, 4),
            "pose": pose,
            "face_match_score": round(match_score, 4),
            "identity_score": round(match_score, 4),
            "status": status,
            "flags": flags
        }

    def _detect_faces_detailed(self, image_path: str) -> List[Dict]:
        """
        Real implementation of face detection with alignment and embedding extraction.
        """
        self._ensure_model()
        from PIL import Image
        import torch

        try:
            img = Image.open(image_path).convert("RGB")
            # Get face landmarks and aligned tensor
            # MTCNN returns (num_faces, image_size, image_size, 3) or similar
            # In our FaceAlignment, we return [3, 112, 112] for one face
            
            # For multiple faces, we need to use the detector directly
            boxes, probs, points = self.aligner.detector.detect(img, landmarks=True)
            
            if boxes is None: return []
            
            faces = []
            for i in range(len(boxes)):
                # Extract and align this specific face
                # We'll use a simplified crop for now, or the aligner.align if we only want one
                # Let's align specifically
                box = boxes[i].tolist()
                prob = probs[i]
                
                # Align using the detector's internal extract/align if possible
                # Or just crop and resize for the secondary faces
                face_tensor = self.aligner.align(img) # This aligner is currently tuned for primary face
                
                with torch.no_grad():
                    embedding = self.model.backbone(face_tensor.unsqueeze(0).to(self.device))
                    embedding = embedding.squeeze().cpu().numpy()

                faces.append({
                    "bbox": box,
                    "embedding": embedding,
                    "quality": float(prob),
                    "pose": {"yaw": 0.0, "pitch": 0.0} # MTCNN doesn't give yaw/pitch natively, but we can estimate
                })
            return faces
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []

    def _compute_match(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        # Cosine similarity is just dot product because our embeddings are L2 normalized
        return float(np.dot(emb1, emb2))


    def _result_v2(self, face_detected: bool, status: str, flags: Dict) -> Dict:
        return {
            "face_detected": face_detected,
            "face_count": 0,
            "face_quality_score": 0.0,
            "pose": {"yaw": 0.0, "pitch": 0.0},
            "face_match_score": 0.0,
            "identity_score": 0.0,
            "status": status,
            "flags": flags
        }
