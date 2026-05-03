import os
import torch
import time
from backend_v2.models.forensic_unet import ForensicUNet
from backend_v2.train.forensic_dataset import ForensicDataset
from torch.utils.data import DataLoader

def benchmark_training():
    device = torch.device("cpu")
    manifest = "backend_v2/forensic/data/manifest.json"
    ds = ForensicDataset(manifest, img_size=256)
    loader = DataLoader(ds, batch_size=1)
    
    model = ForensicUNet(in_channels=5).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    criterion = torch.nn.BCELoss()
    
    print("Starting benchmark for 5 iterations...")
    start_time = time.time()
    for i, (imgs, masks) in enumerate(loader):
        if i >= 5: break
        iter_start = time.time()
        
        optimizer.zero_grad()
        preds = model(imgs)
        loss = criterion(preds, masks)
        loss.backward()
        optimizer.step()
        
        print(f"Iteration {i+1} took {time.time() - iter_start:.2f}s")
    
    total_time = time.time() - start_time
    avg_time = total_time / 5
    print(f"Average time per iteration: {avg_time:.2f}s")

if __name__ == "__main__":
    benchmark_training()
