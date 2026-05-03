import os
import sys
import torch
from pathlib import Path
from torch.utils.data import DataLoader
from tqdm import tqdm

# Fix python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.train.doc_dataset import (
    FUNSDDataset, SROIEDataset, IDCardDataset, 
    LABEL2ID, ID2LABEL, LABELS
)
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor

def compute_metrics(preds, labels):
    preds = preds.argmax(dim=2)
    mask = labels != -100
    correct = (preds[mask] == labels[mask]).sum().item()
    total = mask.sum().item()
    return correct, total

def evaluate():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data_dir = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\document_understanding"
    weights_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "layoutlmv3_best.pth"
    
    if not weights_path.exists():
        print(f"ERROR: Weights not found at {weights_path}")
        return

    print(f"Evaluating on {device}...")
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    
    # Load a small validation set
    funsd_ds = FUNSDDataset(data_dir, processor, split="testing_data")
    if len(funsd_ds) == 0:
        print("WARN: FUNSD testing data not found, using a subset of training data for eval demo")
        funsd_ds = FUNSDDataset(data_dir, processor, split="training_data")
        # take a small slice
        funsd_ds.samples = funsd_ds.samples[:20]

    loader = DataLoader(funsd_ds, batch_size=4)
    
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        "microsoft/layoutlmv3-base",
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    ).to(device)
    
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()
    
    total_correct = 0
    total_tokens = 0
    
    with torch.no_grad():
        for batch in tqdm(loader, desc="Evaluating"):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            correct, total = compute_metrics(outputs.logits, batch["labels"])
            total_correct += correct
            total_tokens += total
            
    accuracy = total_correct / max(total_tokens, 1)
    print(f"\nFinal Accuracy: {accuracy*100:.2f}%")
    
    # Save report
    report = {
        "timestamp": str(torch.utils.data.datetime.datetime.now()),
        "accuracy": accuracy,
        "total_tokens": total_tokens,
        "weights_used": str(weights_path)
    }
    
    report_path = Path(__file__).resolve().parent / "doc_understanding_eval.json"
    import json
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    evaluate()
