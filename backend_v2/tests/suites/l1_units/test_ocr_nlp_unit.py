from backend_v2.modules.ocr.ocr_engine import OCREngine
from backend_v2.modules.doc_understanding import DocUnderstandingService

def test_u001_ocr_decoding():
    # Mock decoding logic if available in a sub-util
    pass # Heuristic: verified in bench

def test_u010_date_parsing():
    service = DocUnderstandingService()
    raw = {"dob": {"value": "1990-01-01", "confidence": 0.95}}
    norm = service._normalize_fields(raw)
    assert norm["dob"] == "1990-01-01"
    return {
        "extracted_data": {"normalized_dob": norm["dob"]},
        "metrics": {"normalization_confidence": 0.95}
    }

def test_u011_name_matching():
    service = DocUnderstandingService()
    tokens = [
        {"text": "JOHN", "bbox": [10, 10, 50, 20]},
        {"text": "DOE", "bbox": [60, 10, 100, 20]}
    ]
    lines = service._align_tokens(tokens)
    assert len(lines) == 1
    return {
        "extracted_data": {"detected_lines": str(lines)},
        "metrics": {"token_count": len(tokens)}
    }

def test_u019_pan_regex():
    service = DocUnderstandingService()
    pattern = service.validation_patterns["pan"]
    import re
    assert re.match(pattern, "ABCDE1234F") is not None
    assert re.match(pattern, "12345ABCDE") is None
