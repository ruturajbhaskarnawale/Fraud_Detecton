import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

def generate_synthetic_fraud_data(n_samples=1000):
    """
    Generates balanced synthetic data for Fraud Engine training.
    """
    np.random.seed(42)
    
    # Features: face_sim, liveness, tamper, ocr_conf, meta_risk, ip_vel, dev_vel, geo, proxy
    # 0 -> Genuine, 1 -> Fraud
    
    # 1. Genuine Samples
    genuine = np.random.normal(0.2, 0.1, (n_samples // 2, 9))
    # Genuine face similarity should be high
    genuine[:, 0] = np.random.normal(0.85, 0.05, n_samples // 2)
    # Genuine liveness high
    genuine[:, 1] = np.random.normal(0.9, 0.05, n_samples // 2)
    # Genuine tamper low
    genuine[:, 2] = np.random.normal(0.1, 0.05, n_samples // 2)
    
    # 2. Fraud Samples
    fraud = np.random.normal(0.7, 0.2, (n_samples // 2, 9))
    # Fraud tamper high
    fraud[:, 2] = np.random.normal(0.8, 0.1, n_samples // 2)
    # Fraud velocity high
    fraud[:, 5] = np.random.choice([0.0, 1.0], n_samples // 2, p=[0.2, 0.8])
    
    X = np.clip(np.vstack([genuine, fraud]), 0, 1)
    y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    cols = ["face_similarity", "liveness_score", "tamper_score", "ocr_confidence", 
            "metadata_risk", "ip_velocity", "device_velocity", "geo_mismatch", "proxy_score"]
    
    return pd.DataFrame(X, columns=cols), y

def train_fraud_model():
    print("Generating training dataset...")
    X, y = generate_synthetic_fraud_data(2000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        objective='binary:logistic',
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # Eval
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    print("\nModel Evaluation:")
    print(classification_report(y_test, preds))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, probs):.4f}")
    
    # Save
    weight_dir = "backend_v2/models/weights/fraud"
    os.makedirs(weight_dir, exist_ok=True)
    save_path = os.path.join(weight_dir, "fraud_xgb_v1.pkl")
    
    joblib.dump(model, save_path)
    print(f"\nModel weights saved to {save_path}")

if __name__ == "__main__":
    train_fraud_model()
