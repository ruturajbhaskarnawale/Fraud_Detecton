"""
OCR Pipeline Evaluation Script (V2)
----------------------------------
- Supports 192px width (Point 2)
- Supports comparative mode selection via sys.argv[1]
- Normalizes GT labels to UPPERCASE for fair comparison (Point 3)
"""

import os
import json
import glob
import cv2
import torch
import numpy as np
import time
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.models.crnn import CRNN
from backend_v2.train.ocr_dataset import OCRTokenizer


# ---------------------------------------------
#  Metrics
# ---------------------------------------------

def edit_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[n]


def compute_wer(preds: list, gts: list) -> float:
    total_dist, total_words = 0, 0
    for pred, gt in zip(preds, gts):
        pred_words = pred.lower().split()
        gt_words   = gt.lower().split()
        total_dist  += edit_distance(pred_words, gt_words)
        total_words += len(gt_words)
    return total_dist / max(total_words, 1)


def compute_cer(preds: list, gts: list) -> float:
    total_dist, total_chars = 0, 0
    for pred, gt in zip(preds, gts):
        total_dist  += edit_distance(pred, gt)
        total_chars += len(gt)
    return total_dist / max(total_chars, 1)


# ---------------------------------------------
#  CRNN Inference Helper
# ---------------------------------------------

def crnn_predict(model: CRNN, tokenizer: OCRTokenizer, img_bgr: np.ndarray, device) -> str:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Point 2: Width=192
    gray = cv2.resize(gray, (192, 32)).astype(np.float32) / 255.0
    tensor = torch.from_numpy(gray).unsqueeze(0).unsqueeze(0).to(device)

    with torch.no_grad():
        preds = model(tensor).squeeze(1)
        idxs  = preds.argmax(dim=1).cpu().numpy()

    return tokenizer.ctc_decode(idxs)


# ---------------------------------------------
#  Evaluation 1: Recognition (CER / WER)
# ---------------------------------------------

def evaluate_recognition(model, tokenizer, device, n_samples=200):
    print("\n-- Recognition Evaluation (CER / WER) ------------------")
    # Using iiit5k for generic baseline
    data_dir = Path(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\ocr\iiit5k")
    ann_files = list(glob.glob(str(data_dir / "annotations" / "*.json")))
    img_dir   = data_dir / "images"

    np.random.seed(42)
    np.random.shuffle(ann_files)
    ann_files = ann_files[:n_samples]

    preds_all, gts_all = [], []
    skipped = 0

    for ann_file in ann_files:
        with open(ann_file, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: continue

        gt_text = ""
        if data.get("entities"):
            gt_text = data["entities"][0].get("text", "").strip().upper() # Point 3: upper()
        if not gt_text:
            skipped += 1
            continue

        stem     = Path(ann_file).stem
        img_path = img_dir / f"{stem}.jpg"
        if not img_path.exists():
            img_path = img_dir / f"{stem}.png"
        img = cv2.imread(str(img_path))
        if img is None:
            skipped += 1
            continue

        pred = crnn_predict(model, tokenizer, img, device)
        preds_all.append(pred)
        gts_all.append(gt_text)

    cer = compute_cer(preds_all, gts_all)
    wer = compute_wer(preds_all, gts_all)

    print(f"  Samples evaluated: {len(preds_all)}  |  Skipped: {skipped}")
    print(f"  CER: {cer*100:.2f}%  |  WER: {wer*100:.2f}%")
    
    print(f"\n  {'GT':30s}  {'PRED':30s}  {'MATCH'}")
    print(f"  {'-'*30}  {'-'*30}  {'-'*5}")
    for gt, pr in list(zip(gts_all, preds_all))[:10]:
        match = "OK" if gt.replace(" ","") == pr.replace(" ","") else "XX"
        print(f"  {gt:30s}  {pr:30s}  {match}")

    return cer, wer, len(preds_all)


# ---------------------------------------------
#  Evaluation 2: Field-Level Detection (Synthetic IDs)
# ---------------------------------------------

def evaluate_field_level(model, tokenizer, device, n_samples=50):
    print("\n-- Field-Level Presence Detection (ID Cards) -----------")
    data_dir = Path(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\id_cards\synthetic_v3")
    if not (data_dir / "manifest.json").exists():
        print("  [SKIP] synthetic_v3 not found")
        return 0, 0

    manifest = json.loads((data_dir / "manifest.json").read_text(encoding='utf-8'))
    samples  = manifest["paired_samples"][:n_samples]

    detected_fields, total_fields = 0, 0
    IGNORE = {"photo", "qr", "face"}

    for s in samples:
        img_path = data_dir / s["image"]
        ann_path = data_dir / s["annotation"]
        img = cv2.imread(str(img_path))
        if img is None: continue
        ann = json.loads(ann_path.read_text(encoding='utf-8'))
        h, w = img.shape[:2]

        for field, bbox in ann.get("bboxes", {}).items():
            if field in IGNORE: continue
            x1, y1, x2, y2 = [int(v) for v in bbox]
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
            if x2 <= x1 or y2 <= y1: continue

            crop = img[y1:y2, x1:x2]
            pred = crnn_predict(model, tokenizer, crop, device)
            total_fields += 1
            if pred.strip(): detected_fields += 1

    detection_rate = detected_fields / max(total_fields, 1)
    print(f"  Field Presence Rate (produced ANY text): {detection_rate*100:.1f}%")
    return detection_rate, total_fields


# ---------------------------------------------
#  Main
# ---------------------------------------------

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mode = "mixed"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    print(f"OCR Evaluation - Mode: {mode} - Device: {device}")

    tokenizer    = OCRTokenizer()
    model        = CRNN(img_channels=1, num_classes=tokenizer.vocab_size).to(device)
    
    # Try multiple naming conventions
    weights_dir = Path(__file__).resolve().parent.parent / "models" / "weights"
    options = [
        weights_dir / f"crnn_{mode}_best.pth",
        weights_dir / f"crnn_{mode}.pth",
        weights_dir / "crnn_best.pth",
        weights_dir / "crnn.pth"
    ]
    
    loaded = False
    for p in options:
        if p.exists():
            model.load_state_dict(torch.load(p, map_location=device))
            print(f"[OK] Loaded weights from: {p.name}")
            loaded = True
            break
    
    if not loaded:
        print("[WARN] No trained weights found -- running baseline evaluation")

    model.eval()
    cer, wer, n_eval = evaluate_recognition(model, tokenizer, device)
    field_rate, total_fields = evaluate_field_level(model, tokenizer, device)
    
    print("\nSummary:")
    print(f"  CER: {cer*100:.2f}%")
    print(f"  WER: {wer*100:.2f}%")
    print(f"  Field Presence: {field_rate*100:.1f}%")

if __name__ == "__main__":
    main()
