import sys
import os

# Add src to path
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.pipeline import KYCPipeline
import json

def test_full_pipeline():
    pipeline = KYCPipeline()
    
    # Files (New standardized paths)
    base_data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
    id_card = os.path.join(base_data, "KYC_Synthetic dataset", "images", "aadhaar", "aadhaar_0001.jpg")
    selfie = os.path.join(base_data, "LFW", "lfw-deepfunneled", "lfw-deepfunneled", "Aaron_Peirsol", "Aaron_Peirsol_0001.jpg")
    
    if not os.path.exists(id_card):
        print(f"Error: ID Card not found at {id_card}")
        return
    if not os.path.exists(selfie):
        print(f"Error: Selfie not found at {selfie}")
        return

    print("\n>>> STARTING FULL END-TO-END VERIFICATION <<<")
    results = pipeline.process_verification(id_card, selfie)
    
    print(json.dumps(results, indent=2))
    
    print("\n>>> FINAL DECISION <<<")
    decision = results.get("final_decision", {})
    print(f"DECISION: {decision.get('decision')}")
    print(f"SCORE:    {decision.get('risk_score')}")
    print("REASONS:")
    for r in decision.get("reasons", []):
        print(f"  - {r}")

if __name__ == "__main__":
    test_full_pipeline()
