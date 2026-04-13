import cv2
import numpy as np
import torch
import torchvision.transforms as T
from torchvision.models import resnet18, ResNet18_Weights
import torch.nn.functional as F

class FaceMatcher:
    def __init__(self):
        # 1. OpenCV Face Detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # 2. Torch Model for Embeddings (Lightweight ResNet18)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        self.model = torch.nn.Sequential(*(list(self.model.children())[:-1])) # Remove classification head
        self.model.to(self.device)
        self.model.eval()
        
        self.transform = T.Compose([
            T.ToPILImage(),
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def _get_embedding(self, image_path):
        """Extract face and generate embedding."""
        img = cv2.imread(image_path)
        if img is None: return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0: return None
        
        x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        face_img = img[y:y+h, x:x+w]
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor and pass through model
        input_tensor = self.transform(face_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model(input_tensor)
            
        return embedding.flatten()

    def verify(self, img1_path, img2_path):
        """Compare two faces using Torch embeddings."""
        emb1 = self._get_embedding(img1_path)
        emb2 = self._get_embedding(img2_path)
        
        if emb1 is None or emb2 is None:
            return {"verified": False, "similarity_score": 0.0, "issue": "Face not detected"}
            
        # Cosine Similarity
        similarity = F.cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0))
        similarity_score = float(similarity.item())
        
        # Heuristic threshold for ResNet18 (ImageNet) features:
        # Since it's not trained on faces, the gap might be smaller, but still better than histograms.
        threshold = 0.85 
        
        return {
            "verified": similarity_score > threshold,
            "similarity_score": similarity_score,
            "threshold": threshold
        }

    def detect_faces(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return 0, []
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces), faces
