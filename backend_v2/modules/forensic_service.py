import os
import torch
import numpy as np
import cv2
from PIL import Image
import logging
from typing import Dict, Any, List, Optional, Tuple

from backend_v2.models.forensic_unet import ForensicUNet
from backend_v2.forensic.utils.signals import compute_ela, compute_hpf
from backend_v2.forensic.utils.postprocess import postprocess_mask, calculate_tamper_score, detect_forgery_type

logger = logging.getLogger("forensic_service")

class ForensicService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ForensicService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model_path = "backend_v2/models/weights/forensic_unet_best.pth"
            self.img_size = 512
            self.threshold = 0.45
            self.initialized = True
            logger.info(f"ForensicService initialized on {self.device}")

    def _load_model(self):
        if self._model is None:
            self._model = ForensicUNet(in_channels=5).to(self.device)
            if os.path.exists(self.model_path):
                try:
                    self._model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                    logger.info(f"Loaded Forensic weights from {self.model_path}")
                except Exception as e:
                    logger.error(f"Failed to load Forensic weights: {e}. Using untrained model (MOCK ALERT).")
            else:
                logger.warning(f"Forensic weights not found at {self.model_path}. Running with random initialization.")
            self._model.eval()

    def analyze(self, image_path: str, ocr_result: Optional[Dict] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for forensic analysis.
        Uses Hybrid Signal-Visual UNet + Metadata/OCR heuristics.
        """
        self._load_model()
        
        try:
            # 1. Preprocessing (5-channel input)
            img = Image.open(image_path).convert("RGB")
            img_resized = img.resize((self.img_size, self.img_size), Image.BILINEAR)
            img_arr = np.array(img_resized).astype(np.float32) / 255.0
            
            ela_arr = compute_ela(image_path, quality=90)
            ela_resized = cv2.resize(ela_arr, (self.img_size, self.img_size)).astype(np.float32) / 255.0
            
            hpf_arr = compute_hpf(np.array(img_resized)).astype(np.float32) / 255.0
            
            combined = np.concatenate([
                img_arr, 
                ela_resized[:, :, np.newaxis], 
                hpf_arr[:, :, np.newaxis]
            ], axis=2)
            
            input_tensor = torch.from_numpy(combined).permute(2, 0, 1).unsqueeze(0).to(self.device)
            
            # 2. Inference
            with torch.no_grad():
                mask = self._model(input_tensor).squeeze().cpu().numpy()
            
            # 3. Post-processing
            clean_mask, regions = postprocess_mask(mask)
            model_score = calculate_tamper_score(mask, regions)
            forgery_type = detect_forgery_type(regions, self.img_size)
            
            # 4. Heuristic Overrides (Metadata/OCR)
            metadata_score = self._audit_metadata(metadata)
            
            # Combine scores (Model is primary)
            final_score = 0.8 * model_score + 0.2 * metadata_score
            
            # 5. Flags
            flags = {
                "tampered_high_confidence": final_score > 0.7,
                "metadata_suspicious": metadata_score > 0.8,
                "many_alterations": len(regions) > 5,
                "text_edit_detected": forgery_type == "text-edit",
                "splicing_detected": forgery_type == "splicing"
            }
            
            return {
                "tamper_score": round(final_score, 4),
                "is_altered": final_score > self.threshold,
                "forgery_type": forgery_type,
                "regions": [r["bbox"] for r in regions],
                "confidence": round(model_score, 4),
                "metadata_score": round(metadata_score, 4),
                "flags": flags,
                "model_version": "Hybrid-UNet-v1-5ch"
            }
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {
                "tamper_score": 0.0,
                "is_altered": False,
                "forgery_type": "unknown",
                "regions": [],
                "confidence": 0.0,
                "flags": {"INFERENCE_FAILED": True},
                "error": str(e)
            }

    def _audit_metadata(self, metadata: Optional[Dict]) -> float:
        if not metadata: return 0.0
        software = str(metadata.get("Software", "")).lower()
        if any(tool in software for tool in ["photoshop", "gimp", "picsart", "exiftool", "adobe"]):
            return 0.95
        return 0.0
