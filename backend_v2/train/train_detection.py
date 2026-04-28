"""
DBNet Text Detection Training — CPU Optimized (V2)
--------------------------------------------------
- Reverted to BCELoss (Model has Sigmoid head)
- CPU-friendly settings: epochs=10, batch_size=1
- Local data path restored
"""

import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from pathlib import Path

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
        # Model has Sigmoid at the end, so use BCELoss, not BCEWithLogitsLoss
        self.bce = nn.BCELoss(reduction='mean')
        self.l1 = nn.L1Loss(reduction='none')

    def forward(self, preds, targets):
        # preds: (prob_map, thresh_map, binary_map)
        # targets: (gt_prob_map, gt_thresh_map, gt_thresh_mask)
        pred_prob, pred_thresh, pred_binary = preds
        gt_prob, gt_thresh, gt_mask = targets
        
        # L_s: Probability Map Loss (BCE)
        loss_s = self.bce(pred_prob, gt_prob)
        
        # L_b: Binary Map Loss (BCE)
        loss_b = self.bce(pred_binary, gt_prob)
        
        # L_t: Threshold Map Loss (L1 masked)
        l1_loss = self.l1(pred_thresh, gt_thresh)
        loss_t = (l1_loss * gt_mask).sum() / (gt_mask.sum() + 1e-6)
        
        loss = loss_s + self.alpha * loss_b + self.beta * loss_t
        return loss


# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────

CFG = dict(
    data_dir       = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\id_cards\synthetic_v3",
    epochs         = 10,                 # User request: 10 epochs
    batch_size     = 1,                  # CPU friendly
    accum_steps    = 4,                  # Effective batch = 4
    lr_max         = 1e-3,
    weight_decay   = 1e-4,
    val_split      = 0.1,
    device         = "cpu",              # User request: CPU
    log_interval   = 1,
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
BEST_PATH    = WEIGHTS_DIR / "dbnet_best.pth"
FINAL_PATH   = WEIGHTS_DIR / "dbnet.pth"


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def train():
    device = CFG["device"]
    print(f"[train] Device: {device} | Epochs: {CFG['epochs']}")

    # ── Dataset
    full_dataset = DBNetDataset(CFG["data_dir"], "manifest.json", img_size=640)
    
    if len(full_dataset) == 0:
        print("[train] ERROR: No samples found.")
        return

    val_size   = max(1, int(CFG["val_split"] * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=CFG["batch_size"], shuffle=True, num_workers=0)
    val_loader   = DataLoader(val_ds, batch_size=CFG["batch_size"], shuffle=False, num_workers=0)

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

    best_loss = float("inf")

    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch_idx, (images, gt_probs, gt_threshes, gt_masks) in enumerate(train_loader, 1):
            images = images.to(device)
            gt_probs = gt_probs.to(device)
            gt_threshes = gt_threshes.to(device)
            gt_masks = gt_masks.to(device)

            optimizer.zero_grad()
            preds = model(images)
            targets = (gt_probs, gt_threshes, gt_masks)
            loss = criterion(preds, targets)
            loss = loss / CFG["accum_steps"]

            loss.backward()

            if batch_idx % CFG["accum_steps"] == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()
                scheduler.step()

            epoch_loss += loss.item() * CFG["accum_steps"]

            if batch_idx % CFG["log_interval"] == 0:
                print(f"  E{epoch:02d} | B{batch_idx:03d}/{len(train_loader)} | Loss: {loss.item()*CFG['accum_steps']:.4f}")

        # ── Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, gt_probs, gt_threshes, gt_masks in val_loader:
                images, gt_probs = images.to(device), gt_probs.to(device)
                gt_threshes, gt_masks = gt_threshes.to(device), gt_masks.to(device)
                
                preds = model(images)
                targets = (gt_probs, gt_threshes, gt_masks)
                loss = criterion(preds, targets)
                val_loss += loss.item()

        val_loss /= len(val_loader)
        avg_train_loss = epoch_loss / len(train_loader)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:02d} | Train: {avg_train_loss:.4f} | Val: {val_loss:.4f} | Time: {elapsed:.1f}s")

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] Best model saved (Loss: {best_loss:.4f})")
        
        torch.save(model.state_dict(), FINAL_PATH)

    print(f"\nTraining Complete. Best Val Loss: {best_loss:.4f}")

if __name__ == "__main__":
    train()
