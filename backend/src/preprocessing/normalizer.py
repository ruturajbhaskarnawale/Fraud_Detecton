import cv2
import numpy as np
from PIL import Image
import os

class ImageNormalizer:
    @staticmethod
    def to_opencv(image):
        """Convert PIL Image or path to OpenCV format."""
        if isinstance(image, str):
            image = cv2.imread(image)
        elif isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return image

    @staticmethod
    def resize_to_dpi(image, target_dpi=300):
        """
        Resize image to a standard height while maintaining aspect ratio.
        Assuming most documents are A4 or similar proportions.
        """
        h, w = image.shape[:2]
        # Standard height for 300dpi A4 is around 3500px
        # We'll use a conservative 2000px height for processing speed
        target_h = 2000
        if h != target_h:
            ratio = target_h / h
            target_w = int(w * ratio)
            image = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
        return image

    @staticmethod
    def deskew(image):
        """Deskew the image using Hough Line Transform."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def enhance_contrast(image):
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return final

    def normalize(self, image_input):
        """Full normalization pipeline."""
        img = self.to_opencv(image_input)
        img = self.resize_to_dpi(img)
        img = self.enhance_contrast(img)
        # img = self.deskew(img) # Optional: sometimes deskewing can misinterpret text blocks
        return img
