import os
import sys
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

class ThresholdCalibrator:
    """
    Calibration Engine to normalize module outputs to [0, 1].
    Uses Platt Scaling (Logistic Regression) or Isotonic Regression.
    """
    def __init__(self, output_dir: str = "backend_v2/calibration"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.calibrators = {}

    def calibrate_module(self, module_name: str, raw_scores: np.ndarray, labels: np.ndarray):
        """
        Fits a Platt Scaler (Logistic Regression) to map raw scores to probabilities.
        """
        print(f"[calib] Calibrating {module_name}...")
        
        # Reshape for sklearn
        X = raw_scores.reshape(-1, 1)
        y = labels
        
        # Fit Platt Scaler
        lr = LogisticRegression()
        lr.fit(X, y)
        
        # Calculate Calibration Error (Brier Score)
        probs = lr.predict_proba(X)[:, 1]
        brier = brier_score_loss(y, probs)
        
        # Calculate EER (Equal Error Rate)
        # Placeholder for real EER logic
        eer = self._calculate_eer(probs, y)
        
        # Save Calibrator
        save_path = self.output_dir / f"{module_name.lower()}_calibrator.pkl"
        with open(save_path, "wb") as f:
            pickle.dump({
                "model": lr,
                "eer": eer,
                "brier_score": brier
            }, f)
            
        print(f"  - EER: {eer:.4f}")
        print(f"  - Brier Score: {brier:.4f}")
        print(f"  - Saved to: {save_path}")

    def _calculate_eer(self, y_score, y_true):
        """
        Calculates the Equal Error Rate.
        """
        from sklearn.metrics import roc_curve
        fpr, tpr, thresholds = roc_curve(y_true, y_score, pos_label=1)
        fnr = 1 - tpr
        idx = np.nanargmin(np.absolute((fnr - fpr)))
        return fpr[idx]

if __name__ == "__main__":
    calib = ThresholdCalibrator()
    
    # Example Calibration Run (Mock Data for structure)
    # In practice, this is called after benchmarking on the validation set.
    print("\n=== SYSTEM CALIBRATION INITIATED ===")
    
    # Face Calibration
    mock_face_scores = np.random.normal(0.8, 0.1, 100) # Simulating high-match scores
    mock_face_labels = np.ones(100)
    calib.calibrate_module("Face", mock_face_scores, mock_face_labels)
    
    # Liveness Calibration
    mock_live_scores = np.random.uniform(0, 1, 100)
    mock_live_labels = (mock_live_scores > 0.7).astype(int)
    calib.calibrate_module("Liveness", mock_live_scores, mock_live_labels)
    
    print("=== CALIBRATION COMPLETE ===")
