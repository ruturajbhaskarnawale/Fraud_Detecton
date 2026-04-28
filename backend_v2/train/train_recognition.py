"""
CRITICAL OCR RECOGNITION TRAINING (V2)
-------------------------------------
Improvements:
- Mixed Precision (AMP) for T4 acceleration (Point 1)
- Wider sequence capacity (img_width=192) (Point 2)
- Comparative Dataset Modes (Generic/ID/Mixed) (Phase 5)
- Long-run schedule: 60 epochs (Point 1)
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

from backend_v2.models.crnn import CRNN
from backend_v2.train.ocr_dataset import OCRDataset, OCRTokenizer

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────
CFG = dict(
    data_dir       = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\ocr",
    mode           = "mixed",          # "generic", "id_domain", "mixed"
    epochs         = 60,               # Point 1: More epochs
    batch_size     = 64,               # Larger batch for GPU
    accum_steps    = 1,                # Not needed much on GPU
    lr_max         = 3e-4,
    weight_decay   = 1e-4,
    hidden_size    = 256,
    img_width      = 192,              # Point 2: Wider sequence
    val_split      = 0.10,
    early_stop_pat = 12,               # More patience for longer runs
    device         = "cuda" if torch.cuda.is_available() else "cpu",
    num_workers    = 0,
    log_interval   = 20,
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

# Suffix paths by mode for comparative training
BEST_PATH    = WEIGHTS_DIR / f"crnn_{CFG['mode']}_best.pth"
FINAL_PATH   = WEIGHTS_DIR / f"crnn_{CFG['mode']}.pth"


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def collate_fn(batch):
    images, texts, lengths = zip(*batch)
    return torch.stack(images, 0), texts, lengths


def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            prev, dp[j] = dp[j], (prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1]))
    return dp[n]


def validate(model, loader, tokenizer, device, criterion):
    model.eval()
    total_loss, total_dist, total_chars = 0.0, 0, 0

    with torch.no_grad():
        for images, texts, lengths in loader:
            images = images.to(device)
            target_lengths = torch.tensor(lengths, dtype=torch.long)
            targets = torch.cat([t[:l] for t, l in zip(texts, lengths)]).to(device)

            preds        = model(images)
            input_lens   = torch.full((images.size(0),), preds.size(0), dtype=torch.long)
            loss         = criterion(preds, targets, input_lens, target_lengths)
            total_loss  += loss.item()

            for i, (pred_seq, gt_tensor, gt_len) in enumerate(zip(preds.permute(1, 0, 2), texts, lengths)):
                pred_idx  = pred_seq.argmax(dim=1).cpu().numpy()
                pred_str  = tokenizer.ctc_decode(pred_idx)
                gt_str    = tokenizer.ctc_decode(gt_tensor[:gt_len].tolist())
                total_dist  += edit_distance(pred_str, gt_str)
                total_chars += len(gt_str)

    avg_loss = total_loss / len(loader)
    cer      = total_dist / max(total_chars, 1)
    return avg_loss, cer


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def train():
    device = CFG["device"]
    print(f"[train] Mode: {CFG['mode']} | Device: {device} | AMP: Enabled")

    tokenizer    = OCRTokenizer()
    full_dataset = OCRDataset(
        CFG["data_dir"], tokenizer, mode=CFG["mode"], 
        img_width=CFG["img_width"], augment=True
    )

    if len(full_dataset) == 0:
        print(f"[train] ERROR: No samples found for mode {CFG['mode']}.")
        return

    val_size   = max(1, int(CFG["val_split"] * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(
        train_ds, batch_size=CFG["batch_size"], shuffle=True,
        num_workers=CFG["num_workers"], drop_last=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_ds, batch_size=CFG["batch_size"], shuffle=False,
        num_workers=CFG["num_workers"], drop_last=True, collate_fn=collate_fn
    )

    print(f"[train] Samples: {len(full_dataset)} (Train={train_size}, Val={val_size})")

    model = CRNN(img_channels=1, num_classes=tokenizer.vocab_size, hidden_size=CFG["hidden_size"]).to(device)
    
    criterion = nn.CTCLoss(blank=0, zero_infinity=True)
    optimizer = optim.AdamW(model.parameters(), lr=CFG["lr_max"], weight_decay=CFG["weight_decay"])
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=CFG["lr_max"], steps_per_epoch=len(train_loader), 
        epochs=CFG["epochs"], pct_start=0.1
    )

    # Point 1: Mixed Precision Setup
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    best_cer = float("inf")
    no_improve = 0

    for epoch in range(1, CFG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch_idx, (images, texts, lengths) in enumerate(train_loader, 1):
            images = images.to(device)
            target_lengths = torch.tensor(lengths, dtype=torch.long)
            targets = torch.cat([t[:l] for t, l in zip(texts, lengths)]).to(device)

            optimizer.zero_grad()
            
            # Point 1: Mixed Precision Forward Pass
            with torch.cuda.amp.autocast(enabled=(device == "cuda")):
                preds      = model(images)
                input_lens = torch.full((images.size(0),), preds.size(0), dtype=torch.long)
                loss       = criterion(preds, targets, input_lens, target_lengths)
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            scheduler.step()
            epoch_loss += loss.item()

            if batch_idx % CFG["log_interval"] == 0:
                lr = scheduler.get_last_lr()[0]
                print(f"  E{epoch:02d} | B{batch_idx:03d}/{len(train_loader)} "
                      f"| Loss: {loss.item():.4f} | LR: {lr:.2e}")

        # Validation
        val_loss, val_cer = validate(model, val_loader, tokenizer, device, criterion)
        elapsed = time.time() - t0
        avg_train_loss = epoch_loss / len(train_loader)

        print(f"Epoch {epoch:02d} | Train: {avg_train_loss:.4f} | Val: {val_loss:.4f} | CER: {val_cer*100:.2f}% | {elapsed:.1f}s")

        # Checkpointing
        if val_cer < best_cer:
            best_cer = val_cer
            no_improve = 0
            torch.save(model.state_dict(), BEST_PATH)
            print(f"  [*] Best model ({CFG['mode']}) saved: {val_cer*100:.2f}%")
        else:
            no_improve += 1

        torch.save(model.state_dict(), FINAL_PATH)

        if no_improve >= CFG["early_stop_pat"]:
            print(f"[train] Early stop at epoch {epoch}")
            break

    print(f"\nFinal Best CER ({CFG['mode']}): {best_cer*100:.2f}%")
    print(f"Path: {BEST_PATH}")


if __name__ == "__main__":
    # Example: Run 'mixed' by default, or accept sys.argv
    if len(sys.argv) > 1:
        CFG["mode"] = sys.argv[1]
        BEST_PATH = WEIGHTS_DIR / f"crnn_{CFG['mode']}_best.pth"
        FINAL_PATH = WEIGHTS_DIR / f"crnn_{CFG['mode']}.pth"
    
    train()
