import sys
import os
import cv2

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing.normalizer import ImageNormalizer
from src.preprocessing.quality_check import QualityChecker

def test_preprocessing():
    # Sample path (adjust if needed)
    sample_dir = r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\KYC_Synthetic dataset\images\aadhaar"
    
    if not os.path.exists(sample_dir):
        print(f"Sample directory not found: {sample_dir}")
        return

    # Get first 3 images
    images = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.png'))][:3]
    
    normalizer = ImageNormalizer()
    checker = QualityChecker()
    
    for img_name in images:
        img_path = os.path.join(sample_dir, img_name)
        print(f"\n--- Testing: {img_name} ---")
        
        # Load and verify
        raw_img = cv2.imread(img_path)
        if raw_img is None:
            print(f"Failed to load {img_path}")
            continue
            
        # 1. Quality Check on Raw
        passed, results = checker.check(raw_img)
        print(f"Initial Quality Check: {'PASSED' if passed else 'FAILED'}")
        print(f"Scores: Blur={results['blur_score']:.2f}, Brightness={results['brightness_score']:.2f}")
        if results['issues']:
            print(f"Issues: {results['issues']}")
            
        # 2. Normalize
        norm_img = normalizer.normalize(raw_img)
        print(f"Normalized Size: {norm_img.shape}")
        
        # 3. Quality Check on Normalized
        passed_norm, results_norm = checker.check(norm_img)
        print(f"Post-Norm Quality Check: {'PASSED' if passed_norm else 'FAILED'}")
        
    print("\nPhase 1 Testing Complete.")

if __name__ == "__main__":
    test_preprocessing()
