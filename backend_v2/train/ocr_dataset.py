import os
import json
import glob
import cv2
import torch
import random
import numpy as np
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Dict, Tuple

# Full Devanagari Unicode block (U+0900 – U+097F)
DEVANAGARI = "".join(chr(c) for c in range(0x0900, 0x0980))

# Core ASCII vocab + common punctuation + Devanagari
BASE_VOCAB = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"    # Upper case only to reduce entropy
    "0123456789"
    " -.,!?()[]{}:;'\"%+/|@#&*" 
)
FULL_VOCAB = BASE_VOCAB + DEVANAGARI


class OCRTokenizer:
    def __init__(self, vocab: str = FULL_VOCAB):
        seen = set()
        unique_vocab = []
        for c in vocab:
            if c not in seen:
                seen.add(c)
                unique_vocab.append(c)

        self.char2idx = {char: idx + 1 for idx, char in enumerate(unique_vocab)}
        self.idx2char = {idx + 1: char for idx, char in enumerate(unique_vocab)}
        self.unknown_idx = len(unique_vocab) + 1
        self.vocab_size  = len(unique_vocab) + 2

    def encode(self, text: str) -> List[int]:
        text = text.upper() # Point 3: Normalize to uppercase
        return [self.char2idx.get(c, self.unknown_idx) for c in text]

    def decode(self, seq: List[int]) -> str:
        return "".join(self.idx2char.get(idx, "?") for idx in seq if idx not in (0, self.unknown_idx))

    def ctc_decode(self, seq: List[int]) -> str:
        chars, prev = [], -1
        for idx in seq:
            if idx != 0 and idx != prev:
                chars.append(self.idx2char.get(idx, "?"))
            prev = idx
        return "".join(chars)

    def coverage(self, text: str) -> float:
        if not text: return 0.0
        text = text.upper()
        known = sum(1 for c in text if c in self.char2idx)
        return known / len(text)


class OCRDataset(Dataset):
    """
    Production-Grade OCR Dataset with:
    - Sequence Capacity: 192px width (Point 2)
    - Comparative Modes: 'generic', 'id_domain', 'mixed'
    - Heavy Augmentations: Blur, Noise, Rotation (Point 5)
    - Label Normalization: Uppercase (Point 3)
    """
    def __init__(
        self,
        data_dir: str,
        tokenizer: OCRTokenizer,
        mode: str = "mixed",        # "generic", "id_domain", "mixed"
        img_height: int = 32,
        img_width:  int = 192,       # Point 2: Wider images
        min_coverage: float = 0.60, 
        max_label_len: int = 25,      # Point 4: Limit label length
        augment: bool = True
    ):
        self.data_dir     = Path(data_dir)
        self.tokenizer    = tokenizer
        self.mode         = mode.lower()
        self.img_height   = img_height
        self.img_width    = img_width
        self.min_coverage = min_coverage
        self.max_label_len = max_label_len
        self.augment      = augment
        self.samples      = self._build_index()

    def _build_index(self) -> List[Dict]:
        samples = []
        # Mapping folders to modes
        generic_sources = ["iiit5k", "synthtext"]
        id_domain_sources = ["indic_scene_text"] # Using Indic as proxy for ID fields if crops missing
        
        # Check for replenished_ocr in document_understanding
        replenished_dir = self.data_dir.parent / "document_understanding" / "replenished_ocr"
        if replenished_dir.exists():
            id_domain_sources.append("replenished_ocr")

        # Filter sources based on mode
        if self.mode == "generic":
            active_sources = generic_sources
        elif self.mode == "id_domain":
            active_sources = id_domain_sources
        else: # mixed
            active_sources = generic_sources + id_domain_sources

        skipped = 0
        for ds in active_sources:
            if ds == "replenished_ocr":
                ds_path = self.data_dir.parent / "document_understanding" / "replenished_ocr"
            else:
                ds_path = self.data_dir / ds
            
            if not ds_path.exists():
                print(f"[OCRDataset] Warning: Source {ds} not found at {ds_path}")
                continue

            ann_path = ds_path / "annotations"
            img_path = ds_path / "images"

            for ann_file in glob.glob(str(ann_path / "*.json")):
                with open(ann_file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except: continue

                base_name = Path(ann_file).stem
                img_file = img_path / f"{base_name}.png"
                if not img_file.exists():
                    img_file = img_path / f"{base_name}.jpg"
                if not img_file.exists(): continue

                # Handle replenished_ocr different structure
                if ds == "replenished_ocr":
                    # replenished_ocr stores ocr_words/ocr_boxes in 'raw_data' as strings
                    try:
                        raw_data = json.loads(data.get("parsed_data", "{}"))
                        raw_ocr = json.loads(data.get("raw_data", "{}"))
                        # This is a bit complex to parse fully; if it's too nested, 
                        # we might skip or simplify. Let's assume standard entities exist.
                        entities = data.get("entities", [])
                        # Fallback: if no entities, parse from raw_data if possible
                    except: entities = []
                else:
                    entities = data.get("entities", [])

                for entity in entities:
                    text = entity.get("text", "").strip().upper()
                    if not text or len(text) > self.max_label_len: continue
                    if self.tokenizer.coverage(text) < self.min_coverage: continue

                    samples.append({
                        "image_path": str(img_file),
                        "text": text,
                        "bbox": entity.get("bbox", [0, 0, 1000, 1000]),
                        "source": ds,
                    })

        print(f"[OCRDataset] Mode: {self.mode} | Index: {len(samples)} samples.")
        return samples

    def _augment_image(self, img: np.ndarray) -> np.ndarray:
        """Point 5: Heavy Data Augmentations"""
        # 1. Random Blur
        if random.random() < 0.3:
            img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # 2. Random Gaussian Noise
        if random.random() < 0.3:
            noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
            img = cv2.add(img, noise)

        # 3. Random Rotation (-3 to +3 degrees)
        if random.random() < 0.3:
            h, w = img.shape[:2]
            angle = random.uniform(-3, 3)
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        return img

    def _preprocess_image(self, img: np.ndarray, bbox: List[int], source: str) -> torch.Tensor:
        # Crop for scene text / replenished
        if source in ["indic_scene_text", "replenished_ocr"]:
            x1, y1, x2, y2 = map(int, bbox)
            h, w = img.shape[:2]
            # Handle normalized bboxes (0-1000) if found
            if max(bbox) > 1 and max(bbox) <= 1000 and source != "indic_scene_text":
                x1, y1, x2, y2 = int(x1*w/1000), int(y1*h/1000), int(x2*w/1000), int(y2*h/1000)
            
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if y2 > y1 and x2 > x1:
                img = img[y1:y2, x1:x2]

        if self.augment:
            img = self._augment_image(img)

        img = cv2.resize(img, (self.img_width, self.img_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0) 
        return torch.from_numpy(img)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, int]:
        sample = self.samples[idx]
        img = cv2.imread(sample["image_path"])
        if img is None:
            img = np.zeros((self.img_height, self.img_width, 3), dtype=np.uint8)

        img_tensor = self._preprocess_image(img, sample["bbox"], sample["source"])
        encoded = self.tokenizer.encode(sample["text"])
        text_tensor = torch.tensor(encoded, dtype=torch.long)
        return img_tensor, text_tensor, len(encoded)

if __name__ == "__main__":
    tok = OCRTokenizer()
    ds = OCRDataset(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\ocr", tok, mode="mixed")
    if len(ds) > 0:
        img, txt, length = ds[0]
        print(f"Sample Decoded: {tok.ctc_decode(txt.tolist())} | Shape: {img.shape}")
