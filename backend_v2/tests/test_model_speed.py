import torch
from backend_v2.models.forensic_unet import ForensicUNet
import time

print("Initializing model...")
start = time.time()
model = ForensicUNet(in_channels=5)
print(f"Model initialized in {time.time() - start:.2f}s")

# Dummy forward pass
x = torch.randn(1, 5, 512, 512)
print("Running forward pass...")
start = time.time()
with torch.no_grad():
    y = model(x)
print(f"Forward pass completed in {time.time() - start:.2f}s")
print(f"Output shape: {y.shape}")
