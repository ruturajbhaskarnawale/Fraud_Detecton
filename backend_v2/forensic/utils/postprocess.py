import numpy as np
import cv2

def postprocess_mask(mask, threshold=0.5, min_area_ratio=0.005):
    """
    Cleans up the prediction mask and extracts regions.
    """
    # 1. Threshold
    binary = (mask > threshold).astype(np.uint8) * 255
    
    # 2. Morphological closing to fill holes
    kernel = np.ones((5,5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # 3. Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    clean_regions = []
    total_area = mask.shape[0] * mask.shape[1]
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area / total_area < min_area_ratio:
            continue
            
        x, y, w, h = cv2.boundingRect(cnt)
        # Calculate region-specific score
        region_prob = np.mean(mask[y:y+h, x:x+w])
        
        clean_regions.append({
            "bbox": [x, y, w, h],
            "area_ratio": area / total_area,
            "confidence": float(region_prob)
        })
        
    return binary, clean_regions

def calculate_tamper_score(mask, regions):
    """
    Derives a final calibrated tamper score.
    """
    if not regions:
        # Check for noise if no distinct regions
        return float(np.mean(mask))
        
    mean_prob = np.mean(mask)
    max_region_prob = max([r["confidence"] for r in regions])
    
    # Weighted average: prioritize distinct high-confidence regions
    score = 0.4 * mean_prob + 0.6 * max_region_prob
    return float(score)

def detect_forgery_type(regions, img_size):
    """
    Heuristic-based forgery type classification.
    """
    if not regions:
        return "clean"
        
    # Text edits are usually small and rectangular
    # Splicing is usually larger or irregular
    
    max_area = max([r["area_ratio"] for r in regions])
    
    if max_area < 0.05:
        return "text-edit"
    elif max_area > 0.15:
        return "splicing"
    else:
        return "copy-move" # Default fallback
