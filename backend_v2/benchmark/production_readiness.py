import os
import sys
import time
import json
import numpy as np
import threading
from pathlib import Path
from typing import Dict, Any, List

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.modules.safety_engine import SafetyEngine

class ProductionReadinessSuite:
    """
    Absolute final validation suite for pre-production audit.
    Tests Generalization, Stability, and Load.
    """
    def __init__(self):
        self.engine = SafetyEngine()
        self.results = {}

    def run_blind_validation(self):
        """STEP 1: Test on 100 completely unseen synthetic profiles."""
        print("[audit] Running Blind Holdout Validation (N=100)...")
        t0 = time.time()
        
        correct = 0
        for i in range(100):
            # Generate random but structured "Clean" or "Fraud" profile
            is_fraud = (i % 5 == 0) # 20% Fraud rate
            if is_fraud:
                f = {k: np.random.uniform(0.7, 1.0) for k in ["ocr_confidence", "face_similarity"]}
                f["liveness_score"] = np.random.uniform(0.0, 0.3) # Spoof
            else:
                f = {k: np.random.uniform(0.85, 1.0) for k in ["ocr_confidence", "face_similarity", "liveness_score"]}
            
            # Add other signals
            f.update({
                "doc_confidence": 0.95, "doc_completeness": 1.0, 
                "forensic_tamper_score": 0.95, "fraud_graph_score": 0.05, "fraud_tabular_score": 0.05
            })
            
            res = self.engine.decide_with_safety(f)
            if (is_fraud and res["decision"] == "REJECT") or (not is_fraud and res["decision"] == "ACCEPT"):
                correct += 1
                
        accuracy = correct / 100
        print(f"  - Blind Accuracy: {accuracy:.2%}")
        self.results["blind_accuracy"] = accuracy

    def run_stability_test(self):
        """STEP 3: Run same input 100 times to check for variance."""
        print("[audit] Running Decision Stability Test (N=100)...")
        f = {"ocr_confidence": 0.92, "face_similarity": 0.88, "liveness_score": 0.95, "doc_confidence": 0.95, 
             "doc_completeness": 1.0, "forensic_tamper_score": 0.95, "fraud_graph_score": 0.05, "fraud_tabular_score": 0.05}
        
        decisions = []
        scores = []
        for _ in range(100):
            res = self.engine.decide_with_safety(f)
            decisions.append(res["decision"])
            scores.append(res["risk_score"])
            
        variance = np.var(scores)
        consistent = len(set(decisions)) == 1
        print(f"  - Stable: {consistent} | Score Variance: {variance:.8f}")
        self.results["stability"] = {"consistent": consistent, "variance": variance}

    def run_load_test(self, concurrent=50):
        """STEP 4: Simulate concurrent requests."""
        print(f"[audit] Running Load Test (Concurrent Requests: {concurrent})...")
        latencies = []
        
        def call_engine():
            f = {"ocr_confidence": 0.9, "face_similarity": 0.9, "liveness_score": 0.9, "doc_confidence": 0.9, 
                 "doc_completeness": 1.0, "forensic_tamper_score": 0.9, "fraud_graph_score": 0.1, "fraud_tabular_score": 0.1}
            t_start = time.time()
            self.engine.decide_with_safety(f)
            latencies.append(time.time() - t_start)
            
        threads = []
        for _ in range(concurrent):
            t = threading.Thread(target=call_engine)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        p50 = np.percentile(latencies, 50) * 1000
        p95 = np.percentile(latencies, 95) * 1000
        print(f"  - Latency: p50={p50:.2f}ms, p95={p95:.2f}ms")
        self.results["load"] = {"p50": p50, "p95": p95}

    def run_full_audit(self):
        print("\n=== STARTING PRE-PRODUCTION READINESS AUDIT ===")
        self.run_blind_validation()
        self.run_stability_test()
        self.run_load_test()
        
        report_path = Path("backend_v2/reports/production_audit.json")
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=4)
            
        print(f"\n=== AUDIT COMPLETE | REPORT: {report_path} ===")

if __name__ == "__main__":
    suite = ProductionReadinessSuite()
    suite.run_full_audit()
