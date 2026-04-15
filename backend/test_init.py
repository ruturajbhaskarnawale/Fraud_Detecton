import os
import sys
sys.path.append(os.getcwd())
import time
print("Importing HybridOCRPipeline...")
from src.ocr.ocr_pipeline import HybridOCRPipeline
print("Import success")
start = time.time()
print("Initializing pipeline...")
p = HybridOCRPipeline()
print(f"Init success in {time.time()-start:.2f}s")
