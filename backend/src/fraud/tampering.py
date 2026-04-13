import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import os

class TamperDetector:
    @staticmethod
    def run_ela(image_path, quality=90):
        """
        Run Error Level Analysis (ELA) on an image.
        Returns the ELA image and a average error score.
        """
        temp_file = "temp_ela.jpg"
        
        # 1. Save at lower quality
        original = Image.open(image_path).convert('RGB')
        original.save(temp_file, 'JPEG', quality=quality)
        
        # 2. Re-open and find diff
        temporary = Image.open(temp_file)
        diff = ImageChops.difference(original, temporary)
        
        # 3. Enhance diff
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        ela_image = ImageEnhance.Brightness(diff).enhance(scale)
        
        # 4. Calculate average error
        # High error areas suggest manipulation
        error_score = np.array(ela_image).mean()
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return ela_image, error_score

    def is_tampered(self, image_path, threshold=20):
        """
        Heuristic: if average error score > threshold, flag as suspicious.
        Note: Threshold needs calibration with real data.
        """
        _, score = self.run_ela(image_path)
        return bool(score > threshold), float(score)
