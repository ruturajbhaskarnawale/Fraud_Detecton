import cv2
import numpy as np
import random

class SelfieSimulator:
    """
    Simulates selfie conditions by applying augmentations to document face images.
    """
    
    @staticmethod
    def simulate(image):
        """
        Apply a sequence of random augmentations to simulate a selfie.
        """
        img = image.copy()
        h, w = img.shape[:2]
        
        # 1. Random Perspective Distortion (Slight camera angle change)
        if random.random() > 0.5:
            src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
            delta = 0.05 * min(w, h)
            dst_pts = np.float32([
                [random.uniform(0, delta), random.uniform(0, delta)],
                [w - random.uniform(0, delta), random.uniform(0, delta)],
                [random.uniform(0, delta), h - random.uniform(0, delta)],
                [w - random.uniform(0, delta), h - random.uniform(0, delta)]
            ])
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            img = cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        # 2. Random Rotation (±15 degrees)
        angle = random.uniform(-15, 15)
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        # 3. Motion Blur (Lightweight)
        if random.random() > 0.6:
            size = 3 # Fixed small size for realism
            kernel_v = np.zeros((size, size))
            if random.random() > 0.5:
                kernel_v[int((size-1)/2), :] = np.ones(size)
            else:
                kernel_v[:, int((size-1)/2)] = np.ones(size)
            kernel_v /= size
            img = cv2.filter2D(img, -1, kernel_v)
        
        # 4. Advanced Lighting/Contrast
        alpha = random.uniform(0.8, 1.2) # Balanced Contrast
        beta = random.uniform(-20, 20)   # Balanced Brightness
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        
        # 5. Random Blur (Gaussian) - Only if really needed
        if random.random() > 0.8:
            img = cv2.GaussianBlur(img, (3, 3), 0)
            
        # 6. JPEG Compression Artifacts (Realistic 70-90)
        quality = random.randint(70, 90)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode('.jpg', img, encode_param)
        img = cv2.imdecode(encimg, 1)
        
        return img

    @staticmethod
    def apply_batch(images):
        return [SelfieSimulator.simulate(img) for img in images]
