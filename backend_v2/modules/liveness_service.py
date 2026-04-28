import torch
from torchvision import transforms
from PIL import Image
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger("liveness_service_v2")

class LivenessService:
    def __init__(self):
        self.version = "v1.0"
        self.base_liveness_threshold = 0.85
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.weights_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "liveness_mobilenet_best.pth"
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _ensure_model(self):
        if self.model is None:
            from backend_v2.models.liveness_net import LivenessNet
            self.model = LivenessNet(pretrained=False).to(self.device)
            if self.weights_path.exists():
                self.model.load_state_dict(torch.load(self.weights_path, map_location=self.device))
                logger.info(f"Loaded liveness weights from {self.weights_path}")
            self.model.eval()

    def analyze(self, image_path: str, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Production liveness analysis using unified MobileNetV3 model.
        """
        self._ensure_model()
        
        if not face_data.get("face_detected"):
            return {"liveness_score": 0.0, "status": "ABSTAIN", "flags": {"no_face": True}, "attack_type": "none"}

        try:
            img = Image.open(image_path).convert("RGB")
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                logit = self.model(img_tensor)
                liveness_score = torch.sigmoid(logit).item()
            
            # Since our model is trained on both deepfakes and spoofs,
            # 'liveness_score' represents the probability of being REAL.
            
            status = "PASS" if liveness_score > self.base_liveness_threshold else "FAIL"
            
            # Attack Classification (Inferred from score depth)
            attack_type = "none"
            if liveness_score < 0.3: attack_type = "spoof_physical"
            elif liveness_score < 0.6: attack_type = "spoof_digital"
            
            return {
                "liveness_score": round(liveness_score, 4),
                "confidence": round(liveness_score, 4),
                "status": status,
                "flags": {
                    "spoof_detected": liveness_score < self.base_liveness_threshold,
                    "low_confidence": 0.7 < liveness_score < self.base_liveness_threshold
                },
                "attack_type": attack_type
            }
        except Exception as e:
            logger.error(f"Liveness analysis failed: {e}")
            return {"liveness_score": 0.0, "status": "ERROR", "flags": {"error": True}, "attack_type": "none"}


    def _classify_attack(self, liveness_score: float, deepfake_score: float) -> str:
        if deepfake_score > 0.15: return "deepfake"
        if liveness_score < 0.4: return "screen" # Moiré proxy
        if liveness_score < 0.7: return "print" # Texture proxy
        return "none"

    def _mock_cdcn_score(self, path: str) -> float:
        return 0.94
        
    def _mock_vit_score(self, path: str) -> float:
        return 0.03
