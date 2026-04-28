import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.models.fraud_models import FraudGCN, RiskCalibration
from backend_v2.train.fraud_data_hub import FraudDataHub

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
CFG = dict(
    data_root      = r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\fraud",
    gcn_epochs     = 50,
    lr             = 0.001,
    device         = "cuda" if torch.cuda.is_available() else "cpu",
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "models" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
GCN_BEST_PATH = WEIGHTS_DIR / "fraud_gcn_best.pt"

def train_gcn_phase():
    """
    PHASE 1: Pre-train GCN on Elliptic dataset to learn topological embeddings.
    """
    device = CFG["device"]
    print(f"[phase1] Training GCN on Elliptic | Device: {device}")
    
    hub = FraudDataHub(CFG["data_root"])
    x, edge_index, y = hub.load_elliptic()
    
    # Filter out unknown labels (-1)
    mask = y != -1
    x_labeled = x[mask].to(device)
    y_labeled = y[mask].to(device)
    
    # Note: For GCN, we need the whole graph even if some labels are unknown
    x, edge_index = x.to(device), edge_index.to(device)
    
    model = FraudGCN(in_channels=x.shape[1]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=CFG["lr"])

    for epoch in range(1, CFG["gcn_epochs"] + 1):
        model.train()
        optimizer.zero_grad()
        
        logits, _ = model(x, edge_index)
        loss = criterion(logits[mask], y_labeled)
        
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"  Epoch {epoch:02d} | Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), GCN_BEST_PATH)
    print(f"[phase1] GCN weights saved to {GCN_BEST_PATH}")

def train_ensemble_phase():
    """
    PHASE 2: Use GCN Embeddings + PaySim + IEEE features to train final classifier.
    """
    print("[phase2] Starting Ensemble Training (XGBoost)...")
    try:
        import xgboost as xgb
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
    except ImportError:
        print("[phase2] ERROR: xgboost or scikit-learn not installed. Run: pip install xgboost scikit-learn")
        return

    hub = FraudDataHub(CFG["data_root"])
    
    # 1. Load Behavioral Data (PaySim)
    print("[phase2] Loading PaySim data...")
    df_paysim = hub.load_paysim()
    
    if df_paysim is not None:
        # Simple feature selection for demo
        features = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
        X = df_paysim[features]
        y = df_paysim['isFraud']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("[phase2] Training XGBoost model...")
        clf = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, use_label_encoder=False)
        clf.fit(X_train, y_train)
        
        preds = clf.predict(X_test)
        print("\n[phase2] PaySim Performance Report:")
        print(classification_report(y_test, preds))
        
        # Save Model
        XGB_PATH = WEIGHTS_DIR / "fraud_xgb_ensemble.json"
        clf.save_model(str(XGB_PATH))
        print(f"[phase2] Ensemble model saved to {XGB_PATH}")
    else:
        print("[phase2] WARNING: PaySim data not found. Skipping.")

if __name__ == "__main__":
    # Now that the user is ready, we enable the full training pipeline
    print("=== Fraud Engine Training Pipeline ===")
    
    # Run Phase 1: GCN
    try:
        train_gcn_phase()
    except Exception as e:
        print(f"GCN Phase failed: {e}")
        
    # Run Phase 2: Ensemble
    try:
        train_ensemble_phase()
    except Exception as e:
        print(f"Ensemble Phase failed: {e}")
    
    print("=== Pipeline Complete ===")

