import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsing.classifier import DocumentClassifier
from src.parsing.extractor import FieldExtractor

def test_extraction():
    # Load previously saved OCR results
    # aadhaar_0001_ocr.txt and pan_0000_ocr.txt
    sample_ocr_files = [
        "aadhaar_0001_ocr.txt",
        "pan_0000_ocr.txt"
    ]
    
    classifier = DocumentClassifier()
    extractor = FieldExtractor()
    
    for ocr_file in sample_ocr_files:
        if not os.path.exists(ocr_file):
            print(f"OCR log not found: {ocr_file}. Please run Phase 2 test first.")
            continue
            
        print(f"\n--- Testing Extraction on: {ocr_file} ---")
        
        with open(ocr_file, 'r', encoding='utf-8') as f:
            # The log format is "[0.XX] Text", we need to extract only the text
            lines = f.readlines()
            full_text = "\n".join([line.split('] ', 1)[1].strip() for line in lines if '] ' in line])
            
        # 1. Classify
        doc_type = classifier.classify(full_text)
        print(f"Detected Document Type: {doc_type.upper()}")
        
        # 2. Extract Fields
        fields = extractor.extract(full_text, doc_type)
        print("Extracted Fields:")
        for k, v in fields.items():
            if k != "raw_text":
                print(f"  - {k}: {v}")

if __name__ == "__main__":
    test_extraction()
