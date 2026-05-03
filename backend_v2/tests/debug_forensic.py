import os
import torch
import numpy as np
from backend_v2.modules.forensic_service import ForensicService
import logging

logging.basicConfig(level=logging.INFO)

def debug_forensic():
    service = ForensicService()
    # Try to find a sample
    sample_path = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\forensic\raw\casia2_replenished\images\Sp_S_N_N_ani_0001_ani_0002_0001.jpg"
    
    if not os.path.exists(sample_path):
        print(f"Sample not found: {sample_path}")
        return
        
    print(f"Analyzing {sample_path}...")
    res = service.analyze(sample_path)
    print("Result:")
    import json
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    debug_forensic()
