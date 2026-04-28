import os
import cv2
import torch
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from pathlib import Path
from typing import Tuple

class ForensicDataset(Dataset):
    """
    Unified Dataset for Image Forensics:
    - CASIA2 Replenished (Professional)
    - Synthetic Tamper (ID Specific)
    - Raw (Bona Fide Clean)
    """
    def __init__(self, data_root: str, img_size=256, compute_ela=True):
        self.data_root = Path(data_root)
        self.img_size = img_size
        self.compute_ela = compute_ela
        self.samples = []
        
        # 1. Load CASIA2
        casia_dir = self.data_root / "raw" / "casia2_replenished"
        if casia_dir.exists():
            img_dir = casia_dir / "images"
            mask_dir = casia_dir / "masks"
            for img_path in img_dir.glob("*.jpg"):
                mask_path = mask_dir / f"{img_path.stem}_mask.png"
                if mask_path.exists():
                    self.samples.append((img_path, mask_path))

        # 2. Load Synthetic Tamper
        synth_dir = self.data_root / "synthetic_tamper"
        if synth_dir.exists():
            for img_path in synth_dir.glob("*.jpg"):
                mask_path = img_path.with_suffix(".png") # assuming mask has same name but .png
                if mask_path.exists():
                    self.samples.append((img_path, mask_path))

        # 3. Load Raw Clean (Negatives)
        raw_dir = self.data_root / "raw"
        if raw_dir.exists():
            for img_path in raw_dir.glob("*.jpg"):
                if "casia" not in str(img_path): # Avoid duplication
                    self.samples.append((img_path, None)) # None means empty mask

    def __len__(self):
        return len(self.samples)

    def _compute_ela(self, image: Image.Image, quality=90) -> np.ndarray:
        """
        Error Level Analysis: Difference between original and resaved JPEG
        """
        temp_path = "temp_ela.jpg"
        image.save(temp_path, "JPEG", quality=quality)
        resaved = Image.open(temp_path)
        
        # Calculate diff
        ela_img = Image.blend(image, resaved, -1.0) # image - resaved
        # Convert to grayscale and normalize
        ela_arr = np.array(ela_img.convert("L"))
        
        # Scale to emphasize differences
        ela_arr = (ela_arr * 10).clip(0, 255)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return ela_arr

    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor]:
        img_path, mask_path = self.samples[idx]
        
        try:
            # 1. Image + ELA
            img = Image.open(img_path).convert("RGB")
            img = img.resize((self.img_size, self.img_size), Image.BILINEAR)
            
            img_arr = np.array(img).astype(np.float32) / 255.0
            
            if self.compute_ela:
                ela_arr = self._compute_ela(img)
                ela_arr = ela_arr.astype(np.float32) / 255.0
                # Combine to 4-channel: [H, W, 4]
                img_combined = np.concatenate([img_arr, ela_arr[:, :, np.newaxis]], axis=2)
            else:
                img_combined = img_arr
            
            # 2. Mask
            if mask_path:
                mask = Image.open(mask_path).convert("L")
                mask = mask.resize((self.img_size, self.img_size), Image.NEAREST)
                mask_arr = np.array(mask).astype(np.float32) / 255.0
                mask_arr = (mask_arr > 0.5).astype(np.float32)
            else:
                mask_arr = np.zeros((self.img_size, self.img_size), dtype=np.float32)
                
            # To Tensors
            img_tensor = torch.from_numpy(img_combined).permute(2, 0, 1)
            mask_tensor = torch.from_numpy(mask_arr).unsqueeze(0)
            
            return img_tensor, mask_tensor
            
        except Exception as e:
            # Fallback
            return torch.zeros((4 if self.compute_ela else 3, self.img_size, self.img_size)), torch.zeros((1, self.img_size, self.img_size))

if __name__ == "__main__":
    # Test
    ds = ForensicDataset(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\forensic")
    print(f"Total forensic samples: {len(ds)}")
    if len(ds) > 0:
        img, mask = ds[0]
        print(f"Combined tensor shape: {img.shape}")
        print(f"Mask shape: {mask.shape}")
