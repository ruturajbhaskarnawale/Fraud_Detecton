import os
import easyocr
import logging
import json
from src.ocr.cer_evaluator import OCREvaluator, OCRMetrics

logging.basicConfig(level=logging.ERROR)

test_dir = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\final\test\ocr'
raw_paths = {
    'kyc_json': r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\KYC_Synthetic dataset\annotations.json'
}
evaluator = OCREvaluator(raw_paths)

all_files = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
aadhaar_files = [f for f in all_files if 'aadhaar' in f.lower()][:10]
pan_files = [f for f in all_files if 'pan' in f.lower()][:10]
test_files = aadhaar_files + pan_files

reader = easyocr.Reader(['en', 'hi'])
results = {}

for file in test_files:
    path = os.path.join(test_dir, file)
    outputs = reader.readtext(path, detail=0)
    full_text = ' '.join(outputs)
    results[file] = {
        'text': full_text,
        'fields': {}
    }

metrics = evaluator.evaluate_batch_detailed(results)

print('--- FAST BENCHMARK OVER KYC ---')
print(f"Samples valid: {metrics['overall']['count']}")
if metrics['overall']['count'] > 0:
    avg_cer = sum(metrics['overall']['cer']) / len(metrics['overall']['cer'])
    print(f"Average CER: {avg_cer:.4f}")
else:
    print('No matches found in ground truth.')
