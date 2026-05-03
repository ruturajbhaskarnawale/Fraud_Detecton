import os
import json
import torch
from backend_v2.modules.forensic_service import ForensicService
from tqdm import tqdm

def validate_forensic_engine():
    service = ForensicService()
    manifest_path = "backend_v2/forensic/data/manifest.json"
    
    if not os.path.exists(manifest_path):
        print("Manifest not found. Run build_manifest.py first.")
        return
        
    with open(manifest_path, "r") as f:
        samples = json.load(f)
        
    # Select a few samples from each category
    categories = {}
    for s in samples:
        lbl = s["label"]
        if lbl not in categories: categories[lbl] = []
        categories[lbl].append(s)
        
    test_samples = []
    for lbl, smpls in categories.items():
        test_samples.extend(smpls[:5]) # 5 samples per type
        
    print(f"Running validation on {len(test_samples)} samples...")
    
    results = []
    for sample in tqdm(test_samples):
        res = service.analyze(sample["image"])
        results.append({
            "expected": sample["label"],
            "predicted_score": res["tamper_score"],
            "is_altered": res["is_altered"],
            "forgery_type": res["forgery_type"],
            "flags": res["flags"]
        })
        
    # Summary
    print("\nValidation Results Summary:")
    for r in results:
        status = "PASS" if (r["is_altered"] and r["expected"] != "clean") or (not r["is_altered"] and r["expected"] == "clean") else "FAIL"
        print(f"[{status}] Expected: {r['expected']:<12} | Score: {r['predicted_score']:.4f} | Type: {r['forgery_type']}")

if __name__ == "__main__":
    validate_forensic_engine()
