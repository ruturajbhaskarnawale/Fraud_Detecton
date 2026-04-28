import os
import cv2
import torch
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend_v2.models.dbnet import DBNet
from backend_v2.models.crnn import CRNN
from backend_v2.train.ocr_dataset import OCRTokenizer

logger = logging.getLogger("ocr_module")

class OCREngine:
    def __init__(self):
        self.version = "v1.0"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Initializing OCR Engine on {self.device}")
        
        # Load DBNet
        self.detector = DBNet().to(self.device)
        # 1. Load DBNet (Text Detection)
        db_weights = Path(__file__).resolve().parent.parent.parent / "models" / "weights" / "dbnet_best.pth"
        if db_weights.exists():
            self.detector.load_state_dict(torch.load(db_weights, map_location=self.device))
            logger.info("Loaded DBNet weights")
        else:
            logger.warning(f"DBNet weights not found at {db_weights}")
        self.detector.eval()
        
        # Load CRNN
        self.tokenizer = OCRTokenizer()
        self.recognizer = CRNN(img_channels=1, num_classes=self.tokenizer.vocab_size).to(self.device)
        
        # Prioritize the best mixed-mode weights
        weights_dir = Path(__file__).resolve().parent.parent.parent / "models" / "weights"
        crnn_weights = weights_dir / "crnn_mixed_best.pth"
        if not crnn_weights.exists():
            crnn_weights = weights_dir / "crnn.pth"

        if crnn_weights.exists():
            self.recognizer.load_state_dict(torch.load(crnn_weights, map_location=self.device))
            logger.info(f"Loaded CRNN weights from {crnn_weights.name}")
        else:
            logger.warning(f"No CRNN weights found at {crnn_weights}")
        self.recognizer.eval()

    def _get_boxes_from_binary_map(self, binary_map: np.ndarray) -> List[np.ndarray]:
        # Extract contours
        contours, _ = cv2.findContours((binary_map * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            boxes.append(box)
        return boxes

    def _perspective_crop(self, img: np.ndarray, box: np.ndarray) -> np.ndarray:
        # Order points (top-left, top-right, bottom-right, bottom-left)
        rect = np.zeros((4, 2), dtype="float32")
        s = box.sum(axis=1)
        rect[0] = box[np.argmin(s)]
        rect[2] = box[np.argmax(s)]
        diff = np.diff(box, axis=1)
        rect[1] = box[np.argmin(diff)]
        rect[3] = box[np.argmax(diff)]
        
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        if maxWidth <= 0 or maxHeight <= 0:
            return None
            
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
            
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
        return warped

    def extract_text(self, image_paths: List[str], route: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        End-to-End Extraction Pipeline
        """
        image_path = image_paths[0]
        img = cv2.imread(image_path)
        if img is None:
            return {"status": "ERROR", "reason": "Image not found"}
            
        orig_h, orig_w = img.shape[:2]
        
        # 1. Detection
        det_img = cv2.resize(img, (640, 640))
        det_img = cv2.cvtColor(det_img, cv2.COLOR_BGR2RGB)
        det_img = det_img.astype(np.float32) / 255.0
        # Normalize
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        det_img = (det_img - mean) / std
        det_img = np.transpose(det_img, (2, 0, 1))
        
        det_tensor = torch.from_numpy(det_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            prob_map = self.detector(det_tensor)
            # Thresholding the probability map
            binary_map = (prob_map.squeeze().cpu().numpy() > 0.3).astype(np.float32)
            
        boxes = self._get_boxes_from_binary_map(binary_map)
        
        tokens = []
        for box in boxes:
            # Scale box back to original image
            scaled_box = box.copy()
            scaled_box[:, 0] = scaled_box[:, 0] * (orig_w / 640.0)
            scaled_box[:, 1] = scaled_box[:, 1] * (orig_h / 640.0)
            
            # 2. Crop
            crop = self._perspective_crop(img, scaled_box)
            if crop is None or crop.shape[0] < 4 or crop.shape[1] < 4:
                continue
                
            # 3. Recognition
            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            crop_gray = cv2.resize(crop_gray, (192, 32))
            crop_gray = crop_gray.astype(np.float32) / 255.0
            crop_tensor = torch.from_numpy(crop_gray).unsqueeze(0).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                preds = self.recognizer(crop_tensor) # [seq_len, batch, num_classes]
                
            # Greedy decode
            preds = preds.squeeze(1) # [seq_len, num_classes]
            preds_idx = preds.argmax(dim=1).cpu().numpy()
            
            text = self.tokenizer.ctc_decode(preds_idx)
            
            if text.strip():
                # Convert numpy array to standard python list for JSON serialization
                flat_bbox = [float(x) for x in scaled_box.flatten()]
                
                # Format: [x1, y1, x2, y2] to keep compatibility with old mock format
                x_coords = [flat_bbox[0], flat_bbox[2], flat_bbox[4], flat_bbox[6]]
                y_coords = [flat_bbox[1], flat_bbox[3], flat_bbox[5], flat_bbox[7]]
                simple_bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

                tokens.append({
                    "text": text,
                    "bbox": simple_bbox,
                    "polygon": flat_bbox,
                    "confidence": 0.85
                })
                
        # Sort tokens top-to-bottom, left-to-right loosely
        tokens.sort(key=lambda t: (t["bbox"][1] // 10, t["bbox"][0]))

        coverage = len(tokens) * 0.05
        
        return {
            "text": " ".join([t["text"] for t in tokens]),
            "tokens": tokens,
            "language": route.get("language", "en") if route else "en",
            "coverage": min(round(coverage, 4), 1.0),
            "engine_used": "Custom_DBNet+CRNN",
            "fallback_used": False,
            "confidence": 0.85 if tokens else 0.0,
            "quality_flags": {
                "low_text_density": len(tokens) < 5,
                "low_confidence": False
            }
        }

if __name__ == "__main__":
    # Quick Test
    engine = OCREngine()
    test_img = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\id_cards\synthetic_v3\images\aadhaar_clean_00000.png"
    if Path(test_img).exists():
        res = engine.extract_text([test_img], {"language": "en"})
        print(f"Extracted {len(res['tokens'])} text fields.")
        print("Full Text:", res["text"])
    else:
        print("Test image not found.")
