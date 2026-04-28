import os
import sys
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib

class RiskModelTrainer:
    """
    Trains the final Logistic Regression fusion model.
    Includes calibration and explainability.
    """
    def __init__(self, data_path: str = "backend_v2/train/fusion_dataset.csv"):
        self.data_path = Path(data_path)
        self.weights_dir = Path("backend_v2/models/weights")
        self.weights_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.weights_dir / "final_risk_model.joblib"

    def train(self):
        print(f"[risk] Loading fusion dataset from {self.data_path}...")
        df = pd.read_csv(self.data_path)
        
        X = df.drop(columns=['label'])
        y = df['label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("[risk] Training Logistic Regression model...")
        # Use penalty='l2' for stability
        model = LogisticRegression(class_weight='balanced')
        model.fit(X_train, y_train)
        
        # Validation
        scores = cross_val_score(model, X_train, y_train, cv=5)
        print(f"  - CV Accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
        
        probs = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, probs)
        print(f"  - Test ROC-AUC: {auc:.4f}")
        
        # Feature Importance (Explainability)
        importance = pd.Series(model.coef_[0], index=X.columns).sort_values(ascending=False)
        print("\n[risk] Global Feature Importance (Explainability):")
        print(importance)
        
        # Save Model
        joblib.dump(model, self.model_path)
        print(f"\n[risk] Final Risk Model saved to {self.model_path}")
        
        return model, X_test, y_test

if __name__ == "__main__":
    trainer = RiskModelTrainer()
    trainer.train()
