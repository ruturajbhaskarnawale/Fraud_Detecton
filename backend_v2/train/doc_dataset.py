import os
import json
import glob
import cv2
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset
from PIL import Image

try:
    from transformers import LayoutLMv3Processor, LayoutLMv3TokenizerFast
except ImportError:
    pass  # We will install it if missing

# ---------------------------------------------------------
# Unified Label Space
# ---------------------------------------------------------
LABELS = [
    "O",
    "B-HEADER", "I-HEADER",
    "B-QUESTION", "I-QUESTION",
    "B-ANSWER", "I-ANSWER",
    "B-COMPANY", "I-COMPANY",
    "B-DATE", "I-DATE",
    "B-ADDRESS", "I-ADDRESS",
    "B-TOTAL", "I-TOTAL",
    "B-NAME", "I-NAME",
    "B-DOB", "I-DOB",
    "B-ID_NUM", "I-ID_NUM"
]

LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for i, label in enumerate(LABELS)}

# ---------------------------------------------------------
# Normalization Helper
# ---------------------------------------------------------
def normalize_bbox(bbox, width, height):
    """
    LayoutLM requires bounding boxes in 0-1000 scale.
    bbox: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = bbox
    x1 = max(0, min(1000, int(1000 * (x1 / width))))
    x2 = max(0, min(1000, int(1000 * (x2 / width))))
    y1 = max(0, min(1000, int(1000 * (y1 / height))))
    y2 = max(0, min(1000, int(1000 * (y2 / height))))
    # ensure x2 > x1 and y2 > y1
    if x2 <= x1: x2 = x1 + 1
    if y2 <= y1: y2 = y1 + 1
    return [x1, y1, x2, y2]


# ---------------------------------------------------------
# Base Parser
# ---------------------------------------------------------
class DocDataset(Dataset):
    def __init__(self, data_dir: str, processor, max_seq_length=512):
        self.data_dir = Path(data_dir)
        self.processor = processor
        self.max_seq_length = max_seq_length
        self.samples = []  # List of dicts: {"image_path": str, "words": [str], "boxes": [[x1,y1,x2,y2]], "labels": [str]}

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image_path = sample["image_path"]
        words = sample["words"]
        boxes = sample["boxes"]
        word_labels = sample["labels"]

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception:
            # Fallback to a blank image if missing/corrupt
            image = Image.new("RGB", (224, 224), (255, 255, 255))
            words, boxes, word_labels = ["error"], [[0,0,1000,1000]], ["O"]

        width, height = image.size
        
        # Normalize boxes
        normalized_boxes = [normalize_bbox(b, width, height) for b in boxes]
        
        # Convert string labels to IDs
        label_ids = [LABEL2ID.get(lbl, 0) for lbl in word_labels]

        # Use processor
        # Since token classification requires aligning labels with subword tokens,
        # we let processor handle it.
        try:
            encoding = self.processor(
                image,
                words,
                boxes=normalized_boxes,
                word_labels=label_ids,
                truncation=True,
                max_length=self.max_seq_length,
                padding="max_length",
                return_tensors="pt"
            )
            # Remove batch dim
            encoding = {k: v.squeeze(0) for k, v in encoding.items()}
            return encoding
        except Exception as e:
            # On error, return an empty padded tensor
            print(f"Error processing {image_path}: {e}")
            return self._empty_encoding()

    def _empty_encoding(self):
        # Create dummy tensors for failure cases
        return {
            "input_ids": torch.zeros(self.max_seq_length, dtype=torch.long),
            "attention_mask": torch.zeros(self.max_seq_length, dtype=torch.long),
            "bbox": torch.zeros((self.max_seq_length, 4), dtype=torch.long),
            "labels": torch.full((self.max_seq_length,), -100, dtype=torch.long),
            "pixel_values": torch.zeros((3, 224, 224), dtype=torch.float)
        }


# ---------------------------------------------------------
# FUNSD Parser
# ---------------------------------------------------------
class FUNSDDataset(DocDataset):
    def __init__(self, data_dir: str, processor, split="training_data"):
        super().__init__(data_dir, processor)
        ann_dir = self.data_dir / "Funsd" / "dataset" / split / "annotations"
        img_dir = self.data_dir / "Funsd" / "dataset" / split / "images"
        
        if not ann_dir.exists():
            return
            
        for ann_file in glob.glob(str(ann_dir / "*.json")):
            stem = Path(ann_file).stem
            img_path = img_dir / f"{stem}.png"
            
            with open(ann_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            words, boxes, labels = [], [], []
            for item in data.get("form", []):
                label_type = item.get("label", "other").upper()
                if label_type == "OTHER":
                    bio_tag = "O"
                else:
                    bio_tag = f"B-{label_type}"  # E.g., B-QUESTION, B-ANSWER, B-HEADER
                    
                for i, word in enumerate(item.get("words", [])):
                    text = word.get("text", "").strip()
                    if not text: continue
                    
                    words.append(text)
                    boxes.append(word["box"])
                    
                    if i == 0:
                        labels.append(bio_tag if bio_tag != "O" else "O")
                    else:
                        labels.append(f"I-{label_type}" if bio_tag != "O" else "O")
            
            if words:
                self.samples.append({
                    "image_path": str(img_path),
                    "words": words,
                    "boxes": boxes,
                    "labels": labels
                })
        print(f"Loaded {len(self.samples)} FUNSD samples from {split}")


# ---------------------------------------------------------
# SROIE Parser
# ---------------------------------------------------------
class SROIEDataset(DocDataset):
    def __init__(self, data_dir: str, processor):
        super().__init__(data_dir, processor)
        base_sroie = self.data_dir / "sroie"
        task1_dir = base_sroie / "0325updated.task1train(626p)"
        task2_dir = base_sroie / "0325updated.task2train(626p)"
        
        if not task1_dir.exists():
            return
            
        # We need to map task2 JSON fields back to task1 bounding boxes.
        # This requires string matching. For simplicity in this plan, we do a basic substring match.
        
        for txt_file in glob.glob(str(task1_dir / "*.txt")):
            stem = Path(txt_file).stem
            img_path = task1_dir / f"{stem}.jpg"
            json_file = task2_dir / f"{stem}.txt"
            
            if not img_path.exists() or not json_file.exists():
                continue
                
            with open(json_file, "r", encoding="utf-8") as f:
                try:
                    gt_entities = json.load(f)
                except json.JSONDecodeError:
                    continue
                    
            words, boxes, labels = [], [], []
            
            with open(txt_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                parts = line.strip().split(",", 8)
                if len(parts) < 9: continue
                
                # 8-point to 4-point
                x_coords = [int(parts[i]) for i in [0, 2, 4, 6]]
                y_coords = [int(parts[i]) for i in [1, 3, 5, 7]]
                box = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                text = parts[8].strip()
                
                if not text: continue
                
                # Match against gt_entities
                matched_label = "O"
                for key, val in gt_entities.items():
                    if isinstance(val, str) and text in val:
                        matched_label = key.upper() # COMPANY, DATE, ADDRESS, TOTAL
                        break
                
                # Tokenize by space for BIO tagging
                text_tokens = text.split()
                if not text_tokens: continue
                
                for i, token in enumerate(text_tokens):
                    words.append(token)
                    boxes.append(box) # Duplicate box for all tokens in the segment
                    if matched_label == "O":
                        labels.append("O")
                    else:
                        labels.append(f"B-{matched_label}" if i == 0 else f"I-{matched_label}")
                        
            if words:
                self.samples.append({
                    "image_path": str(img_path),
                    "words": words,
                    "boxes": boxes,
                    "labels": labels
                })
                
        print(f"Loaded {len(self.samples)} SROIE samples")


# ---------------------------------------------------------
# Synthetic ID Cards Parser
# ---------------------------------------------------------
class IDCardDataset(DocDataset):
    def __init__(self, data_dir: str, processor):
        super().__init__(data_dir, processor)
        # The id_cards dir is technically parallel to document_understanding in Dataset/
        id_dir = self.data_dir.parent / "id_cards" / "synthetic_v3"
        manifest_path = id_dir / "manifest.json"
        
        if not manifest_path.exists():
            return
            
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        for item in manifest.get("paired_samples", []):
            img_path = id_dir / item["image"]
            ann_path = id_dir / item["annotation"]
            
            if not img_path.exists() or not ann_path.exists():
                continue
                
            with open(ann_path, "r", encoding="utf-8") as f:
                ann = json.load(f)
                
            words, boxes, labels = [], [], []
            
            # ann["bboxes"] maps field name to [x1, y1, x2, y2]
            # ann["text"] maps field name to text value
            for field, box in ann.get("bboxes", {}).items():
                if field in ["photo", "qr", "face", "signature"]:
                    continue # Ignore visual non-text elements
                    
                text = str(ann.get("text", {}).get(field, "")).strip()
                if not text: continue
                
                # field names: name, dob, id_number, etc.
                matched_label = field.upper()
                if matched_label not in ["NAME", "DOB", "ID_NUM"]:
                    # Map any other text fields to O or handle specifically
                    matched_label = "O"
                
                text_tokens = text.split()
                if not text_tokens: continue
                
                for i, token in enumerate(text_tokens):
                    words.append(token)
                    boxes.append([int(v) for v in box])
                    if matched_label == "O":
                        labels.append("O")
                    else:
                        labels.append(f"B-{matched_label}" if i == 0 else f"I-{matched_label}")
                        
            if words:
                self.samples.append({
                    "image_path": str(img_path),
                    "words": words,
                    "boxes": boxes,
                    "labels": labels
                })
                
        print(f"Loaded {len(self.samples)} ID Card samples")

# Quick test
if __name__ == "__main__":
    import transformers
    print(f"Transformers version: {transformers.__version__}")
    
    # Needs pip install transformers
    try:
        from transformers import LayoutLMv3Processor
        # Using layoutlmv2 as fallback if v3 not fully supported in local transformers env
        processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
        print("Processor loaded")
        
        ds = FUNSDDataset(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\document_understanding", processor)
        if len(ds) > 0:
            print("First item keys:", ds[0].keys())
    except Exception as e:
        print("Error loading processor or dataset:", e)
