import unittest
from unittest.mock import MagicMock, patch
from backend_v2.modules.ocr.ocr_engine import OCREngine
from backend_v2.modules.doc_understanding import DocUnderstandingService

def test_i002_ocr_to_doc_understanding_contract():
    service = DocUnderstandingService()
    # Mock OCR output
    ocr_res = {
        "text": "NAME: JOHN DOE DOB: 01/01/1990",
        "tokens": [
            {"text": "NAME:", "bbox": [0,0,10,10]},
            {"text": "JOHN", "bbox": [15,0,25,10]},
            {"text": "DOE", "bbox": [30,0,40,10]}
        ]
    }
    
    # Mock ML model to skip heavy loading
    service.ml_model = MagicMock()
    # Mock rule extraction instead
    res = service.extract("fake.jpg", ocr_res, "ID_CARD")
    assert "fields" in res
    assert res["is_reliable"] == False # Because fake.jpg doesn't exist and ML fails

def test_i018_failed_ocr_propagation():
    service = DocUnderstandingService()
    ocr_res = {"text": "", "tokens": []}
    res = service.extract("fake.jpg", ocr_res, "ID_CARD")
    assert "NO_OCR_TOKENS" in res["flags"]
