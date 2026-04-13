import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.face.matcher import FaceMatcher
from src.face.liveness import LivenessDetector

def test_face_phase():
    # Base path for LFW
    lfw_base = r"c:\Users\rutur\OneDrive\Desktop\jotex\Raw_Data\LFW\lfw-deepfunneled\lfw-deepfunneled"
    
    img_a1 = os.path.join(lfw_base, "Aaron_Peirsol", "Aaron_Peirsol_0001.jpg")
    img_a2 = os.path.join(lfw_base, "Aaron_Peirsol", "Aaron_Peirsol_0002.jpg")
    img_b1 = os.path.join(lfw_base, "Aishwarya_Rai", "Aishwarya_Rai_0001.jpg")
    
    matcher = FaceMatcher()
    liveness = LivenessDetector()
    
    print("\n--- Testing Liveness Detection ---")
    is_live, msg = liveness.check_liveness(img_a1)
    print(f"Image A1: {msg} (Pass: {is_live})")
    
    print("\n--- Testing Face Verification (Match) ---")
    print(f"Comparing {os.path.basename(img_a1)} vs {os.path.basename(img_a2)}")
    res_match = matcher.verify(img_a1, img_a2)
    print(f"Verified: {res_match['verified']} (Score: {res_match['similarity_score']:.4f})")
    
    print("\n--- Testing Face Verification (Mismatch) ---")
    print(f"Comparing {os.path.basename(img_a1)} vs {os.path.basename(img_b1)}")
    res_mismatch = matcher.verify(img_a1, img_b1)
    print(f"Verified: {res_mismatch['verified']} (Score: {res_mismatch['similarity_score']:.4f})")

if __name__ == "__main__":
    test_face_phase()
