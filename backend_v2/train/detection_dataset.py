import os
import json
import cv2
import torch
import numpy as np
from torch.utils.data import Dataset
from pathlib import Path
from typing import Dict, List, Tuple

class DBNetDataset(Dataset):
    """
    Dataset for DBNet text detection.
    Generates Probability Maps and Threshold Maps from bounding boxes.
    """
    def __init__(self, data_dir: str, manifest_path: str, img_size: int = 640):
        self.data_dir = Path(data_dir)
        self.img_size = img_size
        
        manifest_file = self.data_dir / manifest_path
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
            self.samples = manifest_data.get("paired_samples", [])

        # Filter out non-text fields
        self.ignore_fields = {"photo", "qr", "face"}

    def __len__(self):
        return len(self.samples)

    def _generate_maps(self, bboxes: List[List[float]], img_shape: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        h, w = img_shape
        
        prob_map = np.zeros((h, w), dtype=np.float32)
        threshold_map = np.zeros((h, w), dtype=np.float32)
        threshold_mask = np.zeros((h, w), dtype=np.float32)
        
        shrink_ratio = 0.4
        
        for bbox in bboxes:
            xmin, ymin, xmax, ymax = bbox
            box_w = xmax - xmin
            box_h = ymax - ymin
            
            if box_w <= 0 or box_h <= 0:
                continue
                
            # Area and Perimeter
            A = box_w * box_h
            L = 2 * (box_w + box_h)
            
            # Compute shrink distance
            distance = A * (1 - shrink_ratio**2) / L
            distance = int(distance)
            
            # 1. Probability Map (Shrunk Box)
            s_xmin = max(0, int(xmin + distance))
            s_ymin = max(0, int(ymin + distance))
            s_xmax = min(w, int(xmax - distance))
            s_ymax = min(h, int(ymax - distance))
            
            if s_xmax > s_xmin and s_ymax > s_ymin:
                cv2.rectangle(prob_map, (s_xmin, s_ymin), (s_xmax, s_ymax), 1.0, -1)
                
            # 2. Threshold Map & Mask (Expanded Box for Borders)
            e_xmin = max(0, int(xmin - distance))
            e_ymin = max(0, int(ymin - distance))
            e_xmax = min(w, int(xmax + distance))
            e_ymax = min(h, int(ymax + distance))
            
            if e_xmax > e_xmin and e_ymax > e_ymin:
                cv2.rectangle(threshold_mask, (e_xmin, e_ymin), (e_xmax, e_ymax), 1.0, -1)
                
                # Approximate distance map for the border (highest at actual border, decaying outwards)
                # For simplicity, we assign a fixed gradient or constant high value at border region
                cv2.rectangle(threshold_map, (e_xmin, e_ymin), (e_xmax, e_ymax), 0.7, -1)
                cv2.rectangle(threshold_map, (int(xmin), int(ymin)), (int(xmax), int(ymax)), 0.3, -1)
                
        return prob_map, threshold_map, threshold_mask

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        img_path = self.data_dir / sample["image"]
        ann_path = self.data_dir / sample["annotation"]

        # normalize Windows paths
        img_path = Path(str(img_path).replace("\\", "/"))
        ann_path = Path(str(ann_path).replace("\\", "/"))
        # Load Image
        img = cv2.imread(str(img_path))
        if img is None:
            # Fallback
            img = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
        orig_h, orig_w = img.shape[:2]
        
        # Resize image
        img = cv2.resize(img, (self.img_size, self.img_size))
        img = img.astype(np.float32) / 255.0
        # Normalize with ImageNet mean/std
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std
        img = np.transpose(img, (2, 0, 1)) # (C, H, W)
        
        # Load Annotations
        bboxes = []
        if ann_path.exists():
            with open(ann_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for key, bbox in data.get("bboxes", {}).items():
                if key in self.ignore_fields:
                    continue
                # Scale bbox to resized image
                xmin, ymin, xmax, ymax = bbox
                xmin = (xmin / orig_w) * self.img_size
                xmax = (xmax / orig_w) * self.img_size
                ymin = (ymin / orig_h) * self.img_size
                ymax = (ymax / orig_h) * self.img_size
                bboxes.append([xmin, ymin, xmax, ymax])
                
        prob_map, threshold_map, threshold_mask = self._generate_maps(bboxes, (self.img_size, self.img_size))
        
        return (
            torch.from_numpy(img),
            torch.from_numpy(prob_map).unsqueeze(0),
            torch.from_numpy(threshold_map).unsqueeze(0),
            torch.from_numpy(threshold_mask).unsqueeze(0)
        )

if __name__ == "__main__":
    dataset = DBNetDataset(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\id_cards\synthetic_v3", "manifest.json")
    print(f"Loaded {len(dataset)} DBNet samples.")
    if len(dataset) > 0:
        img, prob, thresh, mask = dataset[0]
        print(f"Img: {img.shape}, Prob: {prob.shape}, Thresh: {thresh.shape}, Mask: {mask.shape}")
