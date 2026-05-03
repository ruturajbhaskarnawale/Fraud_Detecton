import os
import numpy as np
import cv2
from PIL import Image, ImageChops
import torch

def compute_ela(image_path, quality=90):
    """
    Computes Error Level Analysis (ELA) map.
    Returns a grayscale image where bright pixels indicate high error.
    """
    original = Image.open(image_path).convert('RGB')
    
    # Resave at specified quality
    tmp_path = "backend_v2/forensic/data/ela_tmp.jpg"
    # Ensure directory exists
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    
    original.save(tmp_path, 'JPEG', quality=quality)
    resaved = Image.open(tmp_path)
    
    # Compute absolute difference
    ela = ImageChops.difference(original, resaved)
    
    # Convert to grayscale numpy
    ela_np = np.array(ela.convert('L'), dtype=np.float32)
    
    # Scale for visibility
    max_diff = np.max(ela_np)
    if max_diff > 0:
        ela_np = (ela_np / max_diff) * 255.0
    
    # Clean up
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
        
    return ela_np.astype(np.uint8)

def compute_hpf(image_np):
    """
    Computes High-Pass Filter (HPF) to capture noise residuals.
    Uses a standard Laplacian filter.
    """
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_np
        
    laplacian = cv2.Laplacian(gray, cv2.CV_32F)
    # Normalize to [0, 255]
    hpf = np.absolute(laplacian)
    max_h = hpf.max()
    if max_h > 0:
        hpf = (hpf / max_h * 255)
    return hpf.astype(np.uint8)
