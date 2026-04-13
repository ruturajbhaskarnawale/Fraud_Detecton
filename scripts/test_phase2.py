import sys
import os
import cv2

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing.normalizer import ImageNormalizer
from src.ocr.engine import OCREngine

def test_ocr():
    # Sample paths
    samples = [
        r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\KYC_Synthetic dataset\images\aadhaar\aadhaar_0001.jpg",
        r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\KYC_Synthetic dataset\images\pan\pan_0000.jpg"
    ]
    
    ocr = OCREngine(languages=['en'])
    normalizer = ImageNormalizer()
    
    for img_path in samples:
        if not os.path.exists(img_path):
            print(f"Sample not found: {img_path}")
            continue
            
        print(f"\n--- Testing OCR on: {os.path.basename(img_path)} ---")
        
        # 1. Normalize
        raw_img = cv2.imread(img_path)
        norm_img = normalizer.normalize(raw_img)
        
        # 2. Extract Text
        extracted = ocr.extract_text(norm_img)
        
        # 3. Print Results
        full_text = ocr.get_full_text(extracted)
        print("Extracted Text:")
        print("-" * 30)
        print(full_text)
        print("-" * 30)
        
        # Log to file
        log_name = os.path.basename(img_path).replace('.jpg', '_ocr.txt')
        ocr.log_results(extracted, log_name)
        print(f"Detailed results logged to {log_name}")

if __name__ == "__main__":
    test_ocr()
