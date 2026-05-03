import sys
from pathlib import Path
import os
import torch

# Setup path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.modules.doc_understanding import DocUnderstandingService

def test_extraction_rules_fallback():
    print("\n--- TEST: RULE-BASED FALLBACK ---")
    service = DocUnderstandingService()
    
    # Mock OCR tokens (simulating a PAN card)
    ocr_tokens = [
        {"text": "INCOME TAX DEPARTMENT", "bbox": [100, 50, 400, 100], "confidence": 0.9},
        {"text": "NAME", "bbox": [100, 150, 200, 180], "confidence": 0.9},
        {"text": "JOHN DOE", "bbox": [250, 150, 450, 180], "confidence": 0.9},
        {"text": "DATE OF BIRTH", "bbox": [100, 200, 300, 230], "confidence": 0.9},
        {"text": "01/01/1990", "bbox": [320, 200, 500, 230], "confidence": 0.9},
        {"text": "ABCDE1234F", "bbox": [100, 300, 400, 350], "confidence": 0.9}
    ]
    
    ocr_result = {
        "text": "INCOME TAX DEPARTMENT NAME JOHN DOE DATE OF BIRTH 01/01/1990 ABCDE1234F",
        "tokens": ocr_tokens,
        "confidence": 0.9
    }
    
    # Run extraction (should fallback to rules if weights missing)
    res = service.extract("dummy_path.jpg", ocr_result, "PAN")
    
    print(f"Doc Type: {res['document_type']}")
    print(f"Engine Used: {res['metadata']['engine']}")
    print(f"Reliable: {res['is_reliable']}")
    print(f"Fields: {res['normalized_fields']}")
    print(f"Flags: {res['flags']}")
    
    assert res['document_type'] == "PAN"
    assert "name" in res['normalized_fields']
    assert res['normalized_fields']['name'] == "JOHN DOE"
    assert res['normalized_fields']['id_number'] == "ABCDE1234F"
    assert res['normalized_fields']['dob'] == "1990-01-01"

def test_invalid_data_flags():
    print("\n--- TEST: INVALID DATA FLAGS ---")
    service = DocUnderstandingService()
    
    # Mock OCR tokens with invalid DOB and ID
    ocr_tokens = [
        {"text": "NAME: J0HN D0E", "bbox": [100, 150, 400, 180], "confidence": 0.9},
        {"text": "DOB: 01/01/1850", "bbox": [100, 200, 400, 230], "confidence": 0.9},
        {"text": "ID: 12345", "bbox": [100, 300, 400, 350], "confidence": 0.9}
    ]
    
    ocr_result = {
        "text": "NAME: J0HN D0E DOB: 01/01/1850 ID: 12345",
        "tokens": ocr_tokens,
        "confidence": 0.9
    }
    
    res = service.extract("dummy_path.jpg", ocr_result, "AADHAAR")
    
    print(f"Reliable: {res['is_reliable']}")
    print(f"Flags: {res['flags']}")
    
    assert res['is_reliable'] == False
    assert "INVALID_NAME" in res['flags']
    assert "INVALID_DOB_RANGE" in res['flags']
    assert "MISSING_CRITICAL_FIELDS" in res['flags']

if __name__ == "__main__":
    test_extraction_rules_fallback()
    test_invalid_data_flags()
