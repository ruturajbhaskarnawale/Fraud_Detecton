import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fraud.engine import FraudEngine

def test_fraud_engine():
    # Samples
    doc_paths = [
        r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\KYC_Synthetic dataset\images\aadhaar\aadhaar_0001.jpg",
        r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\KYC_Synthetic dataset\images\pan\pan_0000.jpg"
    ]
    
    # Mock extracted fields from Phase 3 for consistency check
    mock_fields = [
        {"name": "Megha Mukhopadhyay", "dob": "08/12/2001", "id_number": "3378 3986 1513"},
        {"name": "Charles Bandi", "dob": "02/05/1973", "id_number": "MCKPB3862Y"}
    ]
    
    engine = FraudEngine()
    
    print("\n--- Running Fraud Audit (Case 1: Different People) ---")
    results = engine.run_full_audit(mock_fields, doc_paths)
    
    print(f"Overall Status: {results['overall_status']}")
    
    print("\nTampering Detection (ELA):")
    for res in results['tampering_results']:
        print(f"  - {os.path.basename(res['path'])}: {'TAMPERED' if res['is_tampered'] else 'Clean'} (Score: {res['tamper_score']:.2f})")

    print("\nData Consistency Issues:")
    if not results['data_consistency_issues']:
        print("  - None detected (as expected for different docs)")
    for issue in results['data_consistency_issues']:
        print(f"  - {issue['details']}")

    print("\nPerceptual Hashes (for Duplicate Detection):")
    for h in results['hashes']:
        print(f"  - {os.path.basename(h['path'])}: {h['hash']}")

    # Case 2: Simulating Name Mismatch (Same person but name slightly different)
    print("\n--- Running Fraud Audit (Case 2: Name Mismatch Simulation) ---")
    mock_fields_mismatch = [
        {"name": "Megha Mukhopadhyay", "dob": "08/12/2001"},
        {"name": "Megha M", "dob": "08/12/2001"} # Mismatch!
    ]
    issues = engine.check_data_consistency(mock_fields_mismatch)
    for issue in issues:
        print(f"  - DETECTED: {issue['details']}")

if __name__ == "__main__":
    test_fraud_engine()
