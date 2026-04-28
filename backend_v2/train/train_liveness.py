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

from backend_v2.models.liveness_net import LivenessNet
from backend_v2.train.liveness_dataset import LivenessDataset

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
CFG = dict(
    data_root      = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\face",
    epochs         = 20,
    batch_size     = 16,
    lr             = 1e-4,
    weight_decay   = 1e-4,
    val_split      = 0.15,
    device         = "cuda" if torch.cuda.is_available() else "cpu",
    log_interval   = 10,
    # Weight for 'Live' samples to adjust sensitivity
    # High weight on Live helps prevent False Rejection,
    # but for security, we often keep it balanced or slightly bias towards Fake.
    pos_weight     = 1.0 
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
BEST_PATH    = WEIGHTS_DIR / "liveness_mobilenet_best.pth"

def train():
    device = CFG["device"]
    print(f"[train] Starting Liveness Detection Training | Device: {device}")
    
    # 1. Dataset
    full_dataset = LivenessDataset(CFG["data_root"], augment=True)
    
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
    model = LivenessNet(pretrained=True).to(device)
    
    # 3. Loss & Optimizer
    # We use BCEWithLogitsLoss for numerical stability
    # pos_weight helps if classes are imbalanced
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([CFG["pos_weight"]]).to(device))
    optimizer = optim.AdamW(model.parameters(), lr=CFG["lr"], weight_decay=CFG["weight_decay"])
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=CFG["epochs"])

    # 4. Training Loop
    best_val_loss = float("inf")
    
    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()
        
        for batch_idx, (images, labels) in enumerate(train_loader, 1):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
            if batch_idx % CFG["log_interval"] == 0:
                print(f"  E{epoch:02d} | B{batch_idx:03d}/{len(train_loader)} | Loss: {loss.item():.4f}")

        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                preds = (torch.sigmoid(outputs) > 0.5).float()
                total += labels.size(0)
                correct += (preds == labels).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        acc = 100 * correct / total
        elapsed = time.time() - t0
        
        print(f"Epoch {epoch:02d} | Loss: {epoch_loss/len(train_loader):.4f} | Val Loss: {avg_val_loss:.4f} | Acc: {acc:.2f}% | Time: {elapsed:.1f}s")

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] Saved best model to {BEST_PATH}")
            
        scheduler.step()

    print("\nTraining Complete.")

if __name__ == "__main__":
    train()
