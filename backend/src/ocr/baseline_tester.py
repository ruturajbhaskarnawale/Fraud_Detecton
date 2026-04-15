import os
import cv2
import easyocr
import logging
import json
from src.ocr.cer_evaluator import OCREvaluator, OCRMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BaselineTester')

class BaselineTester:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'hi'])
        self.test_dir = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\final\test\ocr'
        self.raw_paths = {
            'sroie': r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\sroie\0325updated.task1train(626p)',
            'kyc_json': r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\KYC_Synthetic dataset\annotations.json'
        }
        self.evaluator = OCREvaluator(self.raw_paths)

    def run(self, limit=10):
        test_files = [f for f in os.listdir(self.test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))][:limit]
        results = {}
        
        logger.info(f"Running Baseline (Raw EasyOCR) on {len(test_files)} samples...")
        
        for file in test_files:
            path = os.path.join(self.test_dir, file)
            # Raw extraction
            outputs = self.reader.readtext(path, detail=0) # Only text
            full_text = " ".join(outputs)
            
            logger.info(f"File: {file} | Extracted: {full_text[:50]}...")
            
            results[file] = {
                "text": full_text,
                "fields": {} # No field extraction in baseline
            }
            
        metrics = self.evaluator.evaluate_batch_detailed(results)
        self.report(metrics)

    def report(self, metrics):
        avg_cer = sum(metrics["overall"]["cer"]) / len(metrics["overall"]["cer"]) if metrics["overall"]["cer"] else 1.0
        logger.info(f"--- BASELINE RESULTS ---")
        logger.info(f"Samples: {metrics['overall']['count']}")
        logger.info(f"Average CER: {avg_cer:.4f}")
        
        with open(r'c:\Users\rutur\OneDrive\Desktop\jotex\docs\BASELINE_REPORT.md', 'w') as f:
            f.write(f"# Baseline OCR Report (Raw EasyOCR)\n\n")
            f.write(f"- **Avg CER**: {avg_cer:.4f}\n")
            f.write(f"- **Samples**: {metrics['overall']['count']}\n")

if __name__ == "__main__":
    tester = BaselineTester()
    tester.run(limit=10)
