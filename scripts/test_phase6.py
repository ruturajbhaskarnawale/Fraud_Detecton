import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scoring.engine import RiskScoringEngine

def test_scoring():
    engine = RiskScoringEngine()
    
    scenarios = [
        {
            "name": "Scenario 1: Perfect Match",
            "data": {
                "tampering_detected": False,
                "face_similarity": 0.92,
                "face_threshold": 0.85,
                "data_consistency_issues": [],
                "ocr_confidence": 0.95,
                "is_duplicate": False
            }
        },
        {
            "name": "Scenario 2: Suspicious Name Mismatch",
            "data": {
                "tampering_detected": False,
                "face_similarity": 0.88,
                "face_threshold": 0.85,
                "data_consistency_issues": [
                    {"type": "name_mismatch", "details": "Name mismatch: 'Megha Mukhopadhyay' vs 'Megha M'"}
                ],
                "ocr_confidence": 0.88,
                "is_duplicate": False
            }
        },
        {
            "name": "Scenario 3: REJECTED (Tampering + Face Mismatch)",
            "data": {
                "tampering_detected": True,
                "face_similarity": 0.65,
                "face_threshold": 0.85,
                "data_consistency_issues": [
                    {"type": "dob_mismatch", "details": "DOB mismatch detected"}
                ],
                "ocr_confidence": 0.90,
                "is_duplicate": False
            }
        }
    ]
    
    for scene in scenarios:
        print(f"\n--- {scene['name']} ---")
        result = engine.calculate_score(scene['data'])
        print(f"Risk Score: {result['risk_score']}")
        print(f"Decision:   {result['decision']}")
        print("Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")

if __name__ == "__main__":
    test_scoring()
