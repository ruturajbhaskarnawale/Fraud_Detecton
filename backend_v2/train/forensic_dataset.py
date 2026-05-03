import os
import json
import torch
import numpy as np
import cv2
from PIL import Image, ImageChops
from torch.utils.data import Dataset
from pathlib import Path
from typing import Tuple
from backend_v2.forensic.utils.signals import compute_ela, compute_hpf

class ForensicDataset(Dataset):
    """
    Production-grade Forensic Dataset:
    - Loads from a pre-built manifest.json
    - Generates RGB (3) + ELA (1) + HPF (1) = 5 channel input
    - Supports dynamic resizing and normalization
    """
    def __init__(self, manifest_path: str, img_size=512, mode='train'):
        self.img_size = img_size
        self.mode = mode
        
        with open(manifest_path, "r") as f:
            self.samples = json.load(f)
            
        # Basic split if manifest doesn't have it
        # (Assuming build_manifest.py handles split identification via 'source' or separate files)
        # For simplicity, we just filter by source in this implementation or take all
        print(f"Loaded {len(self.samples)} samples from manifest.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        img_path = sample["image"]
        mask_path = sample["mask"]
        
        try:
            # 1. Load and resize RGB
            img = Image.open(img_path).convert("RGB")
            img_resized = img.resize((self.img_size, self.img_size), Image.BILINEAR)
            img_arr = np.array(img_resized).astype(np.float32) / 255.0
            
            # 2. Compute ELA (Error Level Analysis)
            # We use a lower resolution for ELA calculation to be faster, then upscale if needed
            ela_arr = compute_ela(img_path, quality=90)
            ela_resized = cv2.resize(ela_arr, (self.img_size, self.img_size))
            ela_resized = ela_resized.astype(np.float32) / 255.0
            
            # 3. Compute HPF (High-Pass Filter)
            hpf_arr = compute_hpf(np.array(img_resized))
            hpf_resized = hpf_arr.astype(np.float32) / 255.0
            
            # 4. Combine channels [H, W, 5]
            # Channels: R, G, B, ELA, HPF
            combined = np.concatenate([
                img_arr, 
                ela_resized[:, :, np.newaxis], 
                hpf_resized[:, :, np.newaxis]
            ], axis=2)
            
            # 5. Mask
            if mask_path and os.path.exists(mask_path):
                mask = Image.open(mask_path).convert("L")
                mask = mask.resize((self.img_size, self.img_size), Image.NEAREST)
                mask_arr = np.array(mask).astype(np.float32) / 255.0
                mask_arr = (mask_arr > 0.5).astype(np.float32)
            else:
                mask_arr = np.zeros((self.img_size, self.img_size), dtype=np.float32)
                
            # To Tensors [C, H, W]
            img_tensor = torch.from_numpy(combined).permute(2, 0, 1)
            mask_tensor = torch.from_numpy(mask_arr).unsqueeze(0)
            
            # ImageNet Normalization (only for RGB channels 0-2)
            # mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]
            # We'll do this in the training loop or here
            
            return img_tensor, mask_tensor
            
        except Exception as e:
            # Fallback for corrupt images
            return torch.zeros((5, self.img_size, self.img_size)), torch.zeros((1, self.img_size, self.img_size))

if __name__ == "__main__":
    # Test
    manifest = "backend_v2/forensic/data/manifest.json"
    if os.path.exists(manifest):
        ds = ForensicDataset(manifest, img_size=256)
        print(f"Total samples: {len(ds)}")
        img, mask = ds[0]
        print(f"Input shape: {img.shape}") # Expect [5, 256, 256]
        print(f"Mask shape: {mask.shape}")
