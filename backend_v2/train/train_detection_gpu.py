"""
DBNet Text Detection Training — GPU/Colab Optimized (V3)
-------------------------------------------------------
- Mixed Precision (AMP) for T4/A100 acceleration
- OneCycleLR Scheduler for rapid convergence
- Automatic Path Normalization for Windows/Linux compatibility
- Best-model checkpointing (dbnet_best.pth)
"""

import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.models.dbnet import DBNet
from backend_v2.train.detection_dataset import DBNetDataset

# ─────────────────────────────────────────────
#  Loss Function
# ─────────────────────────────────────────────

class DBLoss(nn.Module):
    def __init__(self, alpha=1.0, beta=10.0):
        super(DBLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        # Model has Sigmoid heads, so we use BCELoss
        self.bce = nn.BCELoss(reduction='mean')
        self.l1 = nn.L1Loss(reduction='none')

    def forward(self, preds, targets):
        pred_prob, pred_thresh, pred_binary = preds
        gt_prob, gt_thresh, gt_mask = targets
        
        loss_s = self.bce(pred_prob, gt_prob)
        loss_b = self.bce(pred_binary, gt_prob)
        
        l1_loss = self.l1(pred_thresh, gt_thresh)
        loss_t = (l1_loss * gt_mask).sum() / (gt_mask.sum() + 1e-6)
        
        return loss_s + self.alpha * loss_b + self.beta * loss_t


# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────

CFG = dict(
    # Set this to your dataset location (works on both local and Colab)
    data_dir       = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\id_cards\synthetic_v3", 
    epochs         = 30,                
    batch_size     = 8,                 # Increased for GPU
    accum_steps    = 1,                 # No need to accumulate if batch=8 on GPU
    lr_max         = 1e-3,
    weight_decay   = 1e-4,
    val_split      = 0.1,
    device         = "cuda" if torch.cuda.is_available() else "cpu",
    log_interval   = 10,
)

# Colab Fallback: if local path doesn't exist, try Colab path
if not os.path.exists(CFG["data_dir"]):
    CFG["data_dir"] = "/content/Dataset/id_cards/synthetic_v3"

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
BEST_PATH    = WEIGHTS_DIR / "dbnet_best.pth"


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def train():
    device = CFG["device"]
    print(f"[train] Device: {device} | AMP: Enabled")
    print(f"[train] Data: {CFG['data_dir']}")

    # ── Dataset
    full_dataset = DBNetDataset(CFG["data_dir"], "manifest.json", img_size=640)
    
    if len(full_dataset) == 0:
        print("[train] ERROR: No samples found. Check your data_dir path.")
        return

    val_size   = max(1, int(CFG["val_split"] * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=CFG["batch_size"], shuffle=True, num_workers=4 if device=="cuda" else 0)
    val_loader   = DataLoader(val_ds, batch_size=CFG["batch_size"], shuffle=False, num_workers=4 if device=="cuda" else 0)

    print(f"[train] Samples: {len(full_dataset)} (Train={train_size}, Val={val_size})")

    # ── Model
    model = DBNet().to(device)
    
    # ── Loss + Optimizer + Scheduler
    criterion = DBLoss()
    optimizer = optim.AdamW(model.parameters(), lr=CFG["lr_max"], weight_decay=CFG["weight_decay"])
    
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=CFG["lr_max"], steps_per_epoch=len(train_loader), 
        epochs=CFG["epochs"], pct_start=0.1
    )

    # ── Mixed Precision (AMP)
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    best_loss = float("inf")

    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch_idx, (images, gt_probs, gt_threshes, gt_masks) in enumerate(train_loader, 1):
            images, gt_probs = images.to(device), gt_probs.to(device)
            gt_threshes, gt_masks = gt_threshes.to(device), gt_masks.to(device)

            optimizer.zero_grad()
            
            with torch.cuda.amp.autocast(enabled=(device == "cuda")):
                preds = model(images)
                loss = criterion(preds, (gt_probs, gt_threshes, gt_masks))

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            
            scheduler.step()
            epoch_loss += loss.item()

            if batch_idx % CFG["log_interval"] == 0:
                print(f"  E{epoch:02d} | B{batch_idx:03d}/{len(train_loader)} | Loss: {loss.item():.4f}")

        # ── Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, gt_probs, gt_threshes, gt_masks in val_loader:
                images, gt_probs = images.to(device), gt_probs.to(device)
                gt_threshes, gt_masks = gt_threshes.to(device), gt_masks.to(device)
                
                preds = model(images)
                loss = criterion(preds, (gt_probs, gt_threshes, gt_masks))
                val_loss += loss.item()

        val_loss /= len(val_loader)
        avg_train_loss = epoch_loss / len(train_loader)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:02d} | Train: {avg_train_loss:.4f} | Val: {val_loss:.4f} | Time: {elapsed:.1f}s")

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] BEST model saved to {BEST_PATH}")

    print(f"\nTraining Complete. Best Val Loss: {best_loss:.4f}")

if __name__ == "__main__":
    train()
