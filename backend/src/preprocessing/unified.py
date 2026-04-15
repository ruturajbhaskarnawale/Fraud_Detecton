import cv2
import numpy as np
from PIL import Image, ImageChops
import os

class UnifiedPreprocessor:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def to_opencv(self, image):
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None: raise ValueError(f"Could not read image at {image}")
            return img
        elif isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return image

    def resize_standard(self, image, target_width=1280):
        h, w = image.shape[:2]
        if w == target_width:
            return image
        ratio = target_width / w
        target_height = int(h * ratio)
        return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)

    def denoise(self, image):
        """Bilateral filter preserves edges while removing noise."""
        return cv2.bilateralFilter(image, 9, 75, 75)

    def enhance_contrast(self, image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = self.clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def run_global(self, image_input):
        """Standard preprocessing for all pipeline stages."""
        img = self.to_opencv(image_input)
        img = self.resize_standard(img)
        img = self.denoise(img)
        img = self.enhance_contrast(img)
        return img

    def run_ocr_prep(self, image):
        """Grayscale and Adaptive Thresholding for OCR."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    def generate_ela(self, image_path, quality=90):
        """Compute Error Level Analysis (ELA) map."""
        temp_filename = 'temp_ela.jpg'
        original = Image.open(image_path).convert('RGB')
        
        # Save at a specific quality
        original.save(temp_filename, 'JPEG', quality=quality)
        temporary = Image.open(temp_filename)
        
        # Calculate difference
        ela_img = ImageChops.difference(original, temporary)
        
        # Scale the difference
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        ela_img = ImageChops.multiply(ela_img, Image.new('RGB', ela_img.size, (int(scale), int(scale), int(scale))))
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return ela_img
