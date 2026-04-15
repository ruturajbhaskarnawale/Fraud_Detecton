import os
import cv2
import numpy as np
from PIL import Image
import sys

# Project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.preprocessing.unified import UnifiedPreprocessor
from src.face.matcher import FaceMatcher

class PreprocessStep:
    def __init__(self, input_dir, output_root):
        self.input_dir = input_dir
        self.output_root = output_root
        self.preprocessor = UnifiedPreprocessor()
        self.face_matcher = FaceMatcher()
        
        self.dirs = {
            "ocr": os.path.join(output_root, "ocr"),
            "face": os.path.join(output_root, "face"),
            "fraud": os.path.join(output_root, "fraud"),
            "unified": os.path.join(output_root, "unified")
        }
        for d in self.dirs.values(): os.makedirs(d, exist_ok=True)

    def process(self, limit=5000):
        count = 0
        for root, _, files in os.walk(self.input_dir):
            if count >= limit: break
            
            for file in files:
                if count >= limit: break
                
                ext = os.path.splitext(file)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']: continue
                
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, self.input_dir).lower()
                
                # Load images
                img_cv = cv2.imread(src_path)
                if img_cv is None: continue
                
                # 1. Unified Prep (Always)
                unified_target = os.path.join(self.dirs["unified"], file)
                if not os.path.exists(unified_target):
                    unified_img = self.preprocessor.run_global(src_path)
                    cv2.imwrite(unified_target, unified_img)
                else:
                    unified_img = cv2.imread(unified_target)
                
                # 2. OCR Prep (SROIE, Funsd, KYC)
                if 'sroie' in rel_path or 'funsd' in rel_path or 'kyc' in rel_path:
                    ocr_target = os.path.join(self.dirs["ocr"], file)
                    if not os.path.exists(ocr_target) and unified_img is not None:
                        ocr_img = self.preprocessor.run_ocr_prep(unified_img)
                        cv2.imwrite(ocr_target, ocr_img)
                    
                # 3. Fraud Prep (ELA)
                if 'casia' in rel_path or 'kyc' in rel_path:
                    fraud_target = os.path.join(self.dirs["fraud"], file)
                    if not os.path.exists(fraud_target):
                        ela_img = self.preprocessor.generate_ela(src_path)
                        ela_img.save(fraud_target)
                
                # 4. Face Prep (LFW, KYC, MIDV)
                if 'lfw' in rel_path or 'kyc' in rel_path:
                    face_target = os.path.join(self.dirs["face"], file)
                    if not os.path.exists(face_target) and img_cv is not None:
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                        faces = self.face_matcher.face_cascade.detectMultiScale(gray, 1.3, 5)
                        if len(faces) > 0:
                            x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
                            face_crop = img_cv[y:y+h, x:x+w]
                            face_crop = cv2.resize(face_crop, (160, 160))
                            cv2.imwrite(face_target, face_crop)
                
                count += 1
                if count % 100 == 0:
                    print(f"Processed {count} images...")

if __name__ == "__main__":
    input_dir = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\standardized'
    output_root = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\processed'
    
    step = PreprocessStep(input_dir, output_root)
    # Process a representative subset of 2000 images across datasets
    step.process(limit=2000)
