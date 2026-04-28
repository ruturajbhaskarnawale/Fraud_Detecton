import os
import torch
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from pathlib import Path
from torchvision import transforms

class LivenessDataset(Dataset):
    """
    Combines:
    - Dataset/face/liveness (real vs spoof)
    - Dataset/face/deepfake (real vs fake)
    """
    def __init__(self, data_root: str, img_size=224, augment=True):
        self.data_root = Path(data_root)
        self.img_size = img_size
        self.samples = []
        
        # 1. Map Paths
        liveness_dir = self.data_root / "liveness"
        deepfake_dir = self.data_root / "deepfake"
        
        # Real Samples (Label: 1)
        if liveness_dir.exists():
            for img in (liveness_dir / "real").glob("*.*"):
                self.samples.append((img, 1))
            for img in (liveness_dir / "spoof").glob("*.*"):
                self.samples.append((img, 0))
                
        if deepfake_dir.exists():
            for img in (deepfake_dir / "real").glob("*.*"):
                self.samples.append((img, 1))
            for img in (deepfake_dir / "fake").glob("*.*"):
                self.samples.append((img, 0))

        # 2. Transforms
        if augment:
            self.transform = transforms.Compose([
                transforms.Resize((img_size + 32, img_size + 32)),
                transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize((img_size, img_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            img = Image.open(img_path).convert("RGB")
            img_tensor = self.transform(img)
            return img_tensor, torch.tensor([label], dtype=torch.float32)
        except Exception as e:
            # Fallback for broken images
            return torch.zeros((3, self.img_size, self.img_size)), torch.tensor([0], dtype=torch.float32)

if __name__ == "__main__":
    # Quick Test
    ds = LivenessDataset(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\face", augment=False)
    print(f"Total liveness samples: {len(ds)}")
    if len(ds) > 0:
        img, lbl = ds[0]
        print(f"Tensor shape: {img.shape} | Label: {lbl}")
