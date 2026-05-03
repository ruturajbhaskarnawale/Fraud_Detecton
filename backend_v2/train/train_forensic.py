import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.cuda.amp import GradScaler, autocast
from tqdm import tqdm
import numpy as np

from backend_v2.models.forensic_unet import ForensicUNet
from backend_v2.train.forensic_dataset import ForensicDataset

# Loss Functions
class DiceLoss(nn.Module):
    def __init__(self, smooth=1):
        super(DiceLoss, self).__init__()
        self.smooth = smooth
    def forward(self, inputs, targets):
        inputs = inputs.view(-1)
        targets = targets.view(-1)
        intersection = (inputs * targets).sum()
        dice = (2.*intersection + self.smooth)/(inputs.sum() + targets.sum() + self.smooth)
        return 1 - dice

class CombinedLoss(nn.Module):
    def __init__(self, bce_weight=0.5, dice_weight=0.5):
        super().__init__()
        self.bce = nn.BCELoss()
        self.dice = DiceLoss()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight
    def forward(self, inputs, targets):
        return self.bce_weight * self.bce(inputs, targets) + self.dice_weight * self.dice(inputs, targets)

def train_forensic():
    # Config
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    img_size = 512
    batch_size = 4 if device.type == 'cuda' else 1
    epochs = 50
    lr = 1e-4
    manifest_path = "backend_v2/forensic/data/manifest.json"
    save_path = "backend_v2/models/weights/forensic_unet_best.pth"
    
    # Dataset
    full_ds = ForensicDataset(manifest_path, img_size=img_size)
    train_size = int(0.8 * len(full_ds))
    val_size = len(full_ds) - train_size
    train_ds, val_ds = random_split(full_ds, [train_size, val_size])
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Model
    model = ForensicUNet(in_channels=5).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    criterion = CombinedLoss()
    scaler = GradScaler(enabled=(device.type == 'cuda'))
    
    best_iou = 0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for imgs, masks in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            imgs, masks = imgs.to(device), masks.to(device)
            
            optimizer.zero_grad()
            with autocast(enabled=(device.type == 'cuda')):
                preds = model(imgs)
                loss = criterion(preds, masks)
            
            scaler.scale(loss).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            
            train_loss += loss.item()
            
        # Validation
        model.eval()
        val_loss = 0
        total_iou = 0
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                preds = model(imgs)
                val_loss += criterion(preds, masks).item()
                
                # Compute IoU
                preds_bin = (preds > 0.5).float()
                intersection = (preds_bin * masks).sum()
                union = (preds_bin + masks).clamp(0, 1).sum()
                iou = (intersection + 1e-6) / (union + 1e-6)
                total_iou += iou.item()
        
        avg_val_loss = val_loss / len(val_loader)
        avg_iou = total_iou / len(val_loader)
        scheduler.step(avg_val_loss)
        
        print(f"Val Loss: {avg_val_loss:.4f}, Val IoU: {avg_iou:.4f}")
        
        if avg_iou > best_iou:
            best_iou = avg_iou
            torch.save(model.state_dict(), save_path)
            print(f"Saved new best model with IoU {best_iou:.4f}")

if __name__ == "__main__":
    train_forensic()
