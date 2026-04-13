import cv2
import numpy as np

class QualityChecker:
    @staticmethod
    def get_blur_score(image):
        """Calculate the Laplacian variance to detect blur."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    @staticmethod
    def get_brightness_score(image):
        """Calculate average brightness of the image."""
        if len(image.shape) == 3:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            _, _, v = cv2.split(hsv)
            return np.mean(v)
        else:
            return np.mean(image)

    def check(self, image, blur_threshold=100, brightness_threshold=(50, 240)):
        """
        Check if image meets quality standards.
        Returns (is_passed, results_dict)
        """
        blur_score = self.get_blur_score(image)
        brightness_score = self.get_brightness_score(image)
        
        results = {
            "blur_score": blur_score,
            "brightness_score": brightness_score,
            "issues": []
        }
        
        is_passed = True
        
        if blur_score < blur_threshold:
            is_passed = False
            results["issues"].append("Image is too blurry.")
            
        if brightness_score < brightness_threshold[0]:
            is_passed = False
            results["issues"].append("Image is too dark.")
        elif brightness_score > brightness_threshold[1]:
            is_passed = False
            results["issues"].append("Image is overexposed.")
            
        return is_passed, results
