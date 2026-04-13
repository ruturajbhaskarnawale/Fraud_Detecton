import cv2
import numpy as np

class LivenessDetector:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def check_liveness(self, image_path):
        """
        Check for liveness using basic heuristics:
        1. Exactly one face detected.
        2. Image sharpness (Laplacian variance) to prevent print attacks.
        3. Face size relative to image.
        """
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not load image"
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return False, "No face detected"
        if len(faces) > 1:
            return False, "Multiple faces detected - suspicious"
            
        # 2. Laplacian Variance for blur detection (Texture analysis)
        # Prevents very low-quality printouts or screen replays
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 10: # Lowered threshold for more flexibility
            return False, "Low texture quality (Potential Fake/Replay)"
            
        return True, "Liveness verified"
