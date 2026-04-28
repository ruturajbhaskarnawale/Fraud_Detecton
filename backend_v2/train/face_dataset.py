import os
import torch
import cv2
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Tuple

try:
    from facenet_pytorch import MTCNN
except ImportError:
    MTCNN = None

class FaceAlignment:
    def __init__(self, image_size=112):
        self.image_size = image_size
        if MTCNN:
            self.detector = MTCNN(image_size=image_size, margin=0, post_process=False, device='cpu')
        else:
            self.detector = None

    def align(self, img: Image.Image) -> torch.Tensor:
        if self.detector:
            # MTCNN returns a normalized tensor [3, 112, 112]
            face = self.detector(img)
            if face is not None:
                # Normalize to [-1, 1]
                return (face / 127.5) - 1.0
        
        # Fallback: simple resize and normalize
        img = img.resize((self.image_size, self.image_size), Image.BILINEAR)
        arr = np.array(img).transpose(2, 0, 1).astype(np.float32)
        return torch.from_numpy((arr / 127.5) - 1.0)

class TripletFaceDataset(Dataset):
    """
    Yields (Anchor, Positive, Negative) for Triplet Margin Loss
    """
    def __init__(self, data_dir: str, alignment: FaceAlignment):
        self.data_dir = Path(data_dir)
        self.alignment = alignment
        self.classes = [d for d in self.data_dir.iterdir() if d.is_dir()]
        self.class_to_idx = {cls.name: i for i, cls in enumerate(self.classes)}
        
        self.samples = []
        for cls in self.classes:
            imgs = list(cls.glob("*.jpg")) + list(cls.glob("*.png"))
            if len(imgs) >= 2: # Need at least 2 for A-P pair
                self.samples.append((cls.name, imgs))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        # 1. Pick Anchor and Positive from same class
        cls_name, imgs = self.samples[idx]
        a_idx, p_idx = np.random.choice(len(imgs), 2, replace=False)
        
        # 2. Pick Negative from a different class
        neg_cls_idx = np.random.choice([i for i in range(len(self.samples)) if i != idx])
        neg_cls_name, neg_imgs = self.samples[neg_cls_idx]
        n_idx = np.random.choice(len(neg_imgs))
        
        # 3. Load and Align
        a_img = self.alignment.align(Image.open(imgs[a_idx]).convert("RGB"))
        p_img = self.alignment.align(Image.open(imgs[p_idx]).convert("RGB"))
        n_img = self.alignment.align(Image.open(neg_imgs[n_idx]).convert("RGB"))
        
        return a_img, p_img, n_img

class ArcFaceDataset(Dataset):
    """
    Yields (Image, Label) for ArcFace Cross-Entropy
    """
    def __init__(self, data_dir: str, alignment: FaceAlignment):
        self.data_dir = Path(data_dir)
        self.alignment = alignment
        self.samples = []
        self.classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}
        
        for cls_name in self.classes:
            cls_dir = self.data_dir / cls_name
            for img_path in list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png")):
                self.samples.append((img_path, self.class_to_idx[cls_name]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        img = self.alignment.align(Image.open(img_path).convert("RGB"))
        return img, label

if __name__ == "__main__":
    # Test Alignment
    aligner = FaceAlignment()
    dummy_img = Image.new("RGB", (200, 200), (128, 128, 128))
    tensor = aligner.align(dummy_img)
    print(f"Aligned tensor shape: {tensor.shape}")
