import torch
import numpy as np
from PIL import Image

try:
    from facenet_pytorch import MTCNN
except ImportError:
    MTCNN = None

class FaceAlignment:
    def __init__(self, image_size=112):
        self.image_size = image_size
        if MTCNN:
            self.detector = MTCNN(image_size=image_size, margin=0, post_process=False, device='cpu')
        else:
            self.detector = None

    def align(self, img: Image.Image) -> torch.Tensor:
        if self.detector:
            # MTCNN returns a normalized tensor [3, 112, 112]
            face = self.detector(img)
            if face is not None:
                # Normalize to [-1, 1]
                return (face / 127.5) - 1.0
        
        # Fallback: simple resize and normalize
        img = img.resize((self.image_size, self.image_size), Image.BILINEAR)
        arr = np.array(img).transpose(2, 0, 1).astype(np.float32)
        return torch.from_numpy((arr / 127.5) - 1.0)
