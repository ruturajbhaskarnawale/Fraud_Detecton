import cv2
import numpy as np
from PIL import Image

class OCRPreprocessor:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def pipeline_a(self, image_input):
        """CLAHE + Bilateral Filtering (Noise Reduction while preserving edges)"""
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        else:
            image = image_input
            
        if image is None: return None
        
        # 1. Bilateral filter
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # 2. CLAHE on L channel
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = self.clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        return enhanced

    def pipeline_b(self, image_input):
        """Grayscale + Adaptive Thresholding (Strict Binarization)"""
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        else:
            image = image_input
            
        if image is None: return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Gaussian blur to reduce high-frequency noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive Threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh

    def pipeline_c(self, image_input, doc_type):
        """ROI-based Field Extraction (Aadhaar/PAN Layouts)"""
        if not doc_type:
            logger.warning("No doc_type provided for ROI pipeline. Skipping.")
            return []
            
        image = self.pipeline_a(image_input) # Start with base enhancement
        if image is None: 
            return []
        
        if not isinstance(image, np.ndarray):
            logger.warning(f"ROI pipeline expected numpy array, got {type(image)}")
            return []
            
        h, w = image.shape[:2]
        rois = []
        
        try:
            if doc_type == "pan":
                # PAN Card Layout (Slightly wider bounds to avoid cropping text)
                rois.append({
                    "label": "pan_number",
                    "crop": image[int(h*0.35):int(h*0.70), int(w*0.02):int(w*0.85)]
                })
                rois.append({
                    "label": "name",
                    "crop": image[int(h*0.10):int(h*0.40), int(w*0.02):int(w*0.85)]
                })
                
            elif doc_type == "aadhaar":
                # Aadhaar Card Layout (Slightly wider bounds)
                rois.append({
                    "label": "aadhaar_number",
                    "crop": image[int(h*0.70):int(h*0.98), int(w*0.05):int(w*0.95)]
                })
                rois.append({
                    "label": "details",
                    "crop": image[int(h*0.15):int(h*0.65), int(w*0.25):int(w*1.0)]
                })
        except Exception as e:
            logger.error(f"Error during ROI cropping for {doc_type}: {e}")
            return []
            
        # Final safety check: ensure every ROI has crop and label
        valid_rois = [r for r in rois if isinstance(r, dict) and "crop" in r and "label" in r]
        return valid_rois

if __name__ == "__main__":
    # Test stub
    pass
