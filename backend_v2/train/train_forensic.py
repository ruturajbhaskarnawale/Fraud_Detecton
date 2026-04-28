import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.models.forensic_unet import ForensicUNet
from backend_v2.train.forensic_dataset import ForensicDataset

class DiceBCELoss(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(DiceBCELoss, self).__init__()

    def forward(self, inputs, targets, smooth=1):
        # Flatten label and prediction tensors
        inputs = torch.sigmoid(inputs)       
        inputs = inputs.view(-1)
        targets = targets.view(-1)
        
        intersection = (inputs * targets).sum()                            
        dice_loss = 1 - (2.*intersection + smooth)/(inputs.sum() + targets.sum() + smooth)  
        BCE = nn.functional.binary_cross_entropy(inputs, targets, reduction='mean')
        Dice_BCE = BCE + dice_loss
        
        return Dice_BCE

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
CFG = dict(
    data_root      = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\forensic",
    epochs         = 30,
    batch_size     = 4, # U-Net is memory intensive
    lr             = 3e-4,
    weight_decay   = 1e-4,
    val_split      = 0.15,
    device         = "cuda" if torch.cuda.is_available() else "cpu",
    log_interval   = 5,
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
BEST_PATH    = WEIGHTS_DIR / "forensic_unet_best.pth"

def train():
    device = CFG["device"]
    print(f"[train] Starting Forensic Engine Training | Device: {device}")
    
    # 1. Dataset
    full_dataset = ForensicDataset(CFG["data_root"], img_size=256, compute_ela=True)
    
    if len(full_dataset) == 0:
        print(f"[train] ERROR: No data found in {CFG['data_root']}")
        return

    val_size = int(CFG["val_split"] * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=CFG["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=CFG["batch_size"], shuffle=False, num_workers=0)

    print(f"[train] Samples: {len(full_dataset)} (Train={train_size}, Val={val_size})")

    # 2. Model
    model = ForensicUNet(in_channels=4, out_channels=1).to(device)
    
    # 3. Loss & Optimizer
    criterion = DiceBCELoss()
    optimizer = optim.AdamW(model.parameters(), lr=CFG["lr"], weight_decay=CFG["weight_decay"])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    # 4. Training Loop
    best_val_loss = float("inf")
    
    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()
        
        for batch_idx, (images, masks) in enumerate(train_loader, 1):
            images, masks = images.to(device), masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
            if batch_idx % CFG["log_interval"] == 0:
                print(f"  E{epoch:02d} | B{batch_idx:03d}/{len(train_loader)} | Loss: {loss.item():.4f}")

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        elapsed = time.time() - t0
        
        print(f"Epoch {epoch:02d} | Loss: {epoch_loss/len(train_loader):.4f} | Val Loss: {avg_val_loss:.4f} | Time: {elapsed:.1f}s")

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] Saved best model to {BEST_PATH}")
            
        scheduler.step(avg_val_loss)

    print("\nTraining Complete.")

if __name__ == "__main__":
    train()
