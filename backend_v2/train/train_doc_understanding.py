import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, ConcatDataset
from pathlib import Path

# Fix python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.train.doc_dataset import (
    FUNSDDataset, SROIEDataset, IDCardDataset, 
    LABEL2ID, ID2LABEL, LABELS
)

try:
    from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
except ImportError:
    print("Please install transformers: pip install transformers")
    sys.exit(1)

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
CFG = dict(
    data_dir       = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\document_understanding",
    model_name     = "microsoft/layoutlmv3-base",
    epochs         = 10,
    batch_size     = 4,
    accum_steps    = 8,          # effective batch = 4*8 = 32
    lr_max         = 2e-5,
    weight_decay   = 1e-4,
    val_split      = 0.10,
    device         = "cuda" if torch.cuda.is_available() else "cpu",
    num_workers    = 0,
    log_interval   = 10,
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
BEST_PATH    = WEIGHTS_DIR / "layoutlmv3_best.pth"
FINAL_PATH   = WEIGHTS_DIR / "layoutlmv3.pth"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def collate_fn(batch):
    # Each item in batch is a dictionary of tensors
    # Filter out empty encodings
    batch = [b for b in batch if "input_ids" in b and b["input_ids"].sum() > 0]
    if not batch: return None
    
    collated = {
        key: torch.stack([item[key] for item in batch])
        for key in batch[0].keys()
    }
    return collated

def compute_metrics(preds, labels):
    # Basic sequence accuracy
    preds = preds.argmax(dim=2)
    mask = labels != -100
    correct = (preds[mask] == labels[mask]).sum().item()
    total = mask.sum().item()
    return correct / max(total, 1)

def validate(model, loader, device):
    model.eval()
    total_loss = 0.0
    total_acc = 0.0
    valid_batches = 0
    
    with torch.no_grad():
        for batch in loader:
            if batch is None: continue
            
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            logits = outputs.logits
            
            total_loss += loss.item()
            total_acc += compute_metrics(logits, batch["labels"])
            valid_batches += 1
            
    avg_loss = total_loss / max(valid_batches, 1)
    avg_acc = total_acc / max(valid_batches, 1)
    return avg_loss, avg_acc

# ---------------------------------------------------------
# Main Training Loop
# ---------------------------------------------------------
def train():
    device = CFG["device"]
    print(f"[train] Device: {device} | Torch: {torch.__version__}")
    
    print("[train] Loading Processor...")
    processor = LayoutLMv3Processor.from_pretrained(CFG["model_name"], apply_ocr=False)
    
    print("[train] Loading Datasets...")
    funsd_ds = FUNSDDataset(CFG["data_dir"], processor)
    sroie_ds = SROIEDataset(CFG["data_dir"], processor)
    id_ds = IDCardDataset(CFG["data_dir"], processor)
    
    datasets = []
    if len(funsd_ds) > 0: datasets.append(funsd_ds)
    if len(sroie_ds) > 0: datasets.append(sroie_ds)
    if len(id_ds) > 0: datasets.append(id_ds)
    
    if not datasets:
        print("[train] ERROR: No datasets loaded.")
        return
        
    full_dataset = ConcatDataset(datasets)
    print(f"[train] Combined Dataset Size: {len(full_dataset)}")
    
    val_size = max(1, int(CFG["val_split"] * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_ds, batch_size=CFG["batch_size"], shuffle=True, 
                              num_workers=CFG["num_workers"], collate_fn=collate_fn)
    val_loader = DataLoader(val_ds, batch_size=CFG["batch_size"], shuffle=False, 
                            num_workers=CFG["num_workers"], collate_fn=collate_fn)
                            
    print(f"[train] Train: {train_size}  Val: {val_size}  Batches/epoch: {len(train_loader)}")
    
    # ── Model
    print(f"[train] Initializing Model {CFG['model_name']} ...")
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        CFG["model_name"],
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[train] LayoutLMv3 params: {total_params:,}")
    
    optimizer = optim.AdamW(model.parameters(), lr=CFG["lr_max"], weight_decay=CFG["weight_decay"])
    
    # ── Training Loop
    best_acc = 0.0
    
    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()
        optimizer.zero_grad()
        valid_batches = 0
        
        for batch_idx, batch in enumerate(train_loader, 1):
            if batch is None: continue
            
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            
            # Loss accumulation
            loss = loss / CFG["accum_steps"]
            loss.backward()
            epoch_loss += loss.item() * CFG["accum_steps"]
            valid_batches += 1
            
            if valid_batches % CFG["accum_steps"] == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad()
                
            if valid_batches % CFG["log_interval"] == 0:
                print(f"  Epoch {epoch:02d} | Batch {batch_idx:03d}/{len(train_loader)} "
                      f"| Loss: {loss.item()*CFG['accum_steps']:.4f}")
                      
        # Validation
        val_loss, val_acc = validate(model, val_loader, device)
        avg_train_loss = epoch_loss / max(valid_batches, 1)
        elapsed = time.time() - t0
        
        print(f"Epoch {epoch:02d}/{CFG['epochs']} | "
              f"Train Loss: {avg_train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Val Acc: {val_acc*100:.2f}% | "
              f"Time: {elapsed:.1f}s")
              
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] Best model saved (Acc={best_acc*100:.2f}%)")
            
        torch.save(model.state_dict(), FINAL_PATH)

    print("\n" + "=" * 50)
    print(f"Training complete. Best Val Acc: {best_acc*100:.2f}%")
    import shutil
    if BEST_PATH.exists():
        shutil.copy(BEST_PATH, FINAL_PATH)
        print("Copied best -> layoutlmv3.pth for inference.")

if __name__ == "__main__":
    train()
