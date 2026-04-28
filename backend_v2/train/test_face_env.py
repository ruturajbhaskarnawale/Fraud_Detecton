import torch
from PIL import Image
import sys
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from facenet_pytorch import MTCNN
    print("[OK] facenet-pytorch found")
except ImportError:
    print("[FAIL] facenet-pytorch missing")
    sys.exit(1)

try:
    from backend_v2.train.face_dataset import FaceAlignment
    aligner = FaceAlignment(image_size=112)
    print("[OK] FaceAlignment class initialized")
    
    # Test with dummy image
    dummy = Image.new("RGB", (300, 300), (200, 200, 200))
    tensor = aligner.align(dummy)
    print(f"[OK] Alignment result shape: {tensor.shape}")
except Exception as e:
    print(f"[FAIL] Error during alignment: {e}")
    sys.exit(1)
