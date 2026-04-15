import insightface
from insightface.app import FaceAnalysis
import cv2
import numpy as np
import os

def test_init():
    print("Testing InsightFace Initialization...")
    try:
        # buffalo_l is the standard model pack (ArcFace + RetinaFace)
        # providers=['CPUExecutionProvider'] handles CPU fallback
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("Success: InsightFace Initialized")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_init()
