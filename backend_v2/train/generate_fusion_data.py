import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class FusionDataGenerator:
    """
    Generates the unified training dataset for the final Risk Model.
    Aggregates calibrated signals from all modules.
    """
    def __init__(self, output_path: str = "backend_v2/train/fusion_dataset.csv"):
        self.output_path = Path(output_path)
        self.schema = [
            "ocr_confidence", "doc_confidence", "doc_completeness",
            "face_similarity", "liveness_score", "forensic_tamper_score",
            "fraud_graph_score", "fraud_tabular_score", "label"
        ]

    def generate(self, num_samples=1000):
        """
        Simulates the collection of module outputs for the fusion dataset.
        In a production environment, this would run the real pipeline on 
        ground-truth datasets.
        """
        print(f"[fusion] Generating {num_samples} samples for risk model training...")
        
        data = []
        for _ in range(num_samples):
            # Simulate a mix of 'Clean' (label 0) and 'Fraud' (label 1)
            is_fraud = np.random.choice([0, 1], p=[0.8, 0.2])
            
            if is_fraud == 0:
                # Clean users: High confidence across all modules
                row = {
                    "ocr_confidence": np.random.uniform(0.85, 1.0),
                    "doc_confidence": np.random.uniform(0.9, 1.0),
                    "doc_completeness": np.random.uniform(0.95, 1.0),
                    "face_similarity": np.random.uniform(0.8, 1.0),
                    "liveness_score": np.random.uniform(0.9, 1.0),
                    "forensic_tamper_score": np.random.uniform(0.9, 1.0),
                    "fraud_graph_score": np.random.uniform(0.0, 0.2), # Low risk
                    "fraud_tabular_score": np.random.uniform(0.0, 0.1),
                    "label": 0 # ACCEPT
                }
            else:
                # Fraudulent users: Anomalies in one or more modules
                attack_type = np.random.choice(["face", "liveness", "tamper", "graph"])
                
                row = {
                    "ocr_confidence": np.random.uniform(0.5, 0.9),
                    "doc_confidence": np.random.uniform(0.6, 1.0),
                    "doc_completeness": np.random.uniform(0.8, 1.0),
                    "face_similarity": np.random.uniform(0.2, 0.7) if attack_type == "face" else np.random.uniform(0.8, 1.0),
                    "liveness_score": np.random.uniform(0.1, 0.6) if attack_type == "liveness" else np.random.uniform(0.8, 1.0),
                    "forensic_tamper_score": np.random.uniform(0.0, 0.4) if attack_type == "tamper" else np.random.uniform(0.8, 1.0),
                    "fraud_graph_score": np.random.uniform(0.6, 1.0) if attack_type == "graph" else np.random.uniform(0.0, 0.3),
                    "fraud_tabular_score": np.random.uniform(0.5, 1.0) if attack_type == "graph" else np.random.uniform(0.0, 0.2),
                    "label": 1 # REJECT
                }
            
            data.append(row)
            
        df = pd.DataFrame(data)
        df.to_csv(self.output_path, index=False)
        print(f"[fusion] Dataset saved to {self.output_path}")
        return df

if __name__ == "__main__":
    gen = FusionDataGenerator()
    gen.generate()
