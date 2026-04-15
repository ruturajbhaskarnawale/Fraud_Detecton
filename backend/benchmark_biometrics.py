import os
import cv2
import numpy as np
import json
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, confusion_matrix, accuracy_score, f1_score
import logging
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.face.matcher import FaceMatcher
from src.utils.selfie_simulator import SelfieSimulator

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('BiometricBenchmark')

class BiometricBenchmark:
    def __init__(self, matcher):
        self.matcher = matcher
        self.results = []

    def load_lfw_pairs(self, lfw_dir):
        """
        Load LFW pairs using match and mismatch CSV files.
        """
        match_csv = os.path.join(lfw_dir, "matchpairsDevTest.csv")
        mismatch_csv = os.path.join(lfw_dir, "mismatchpairsDevTest.csv")
        
        pairs = []
        
        # Positives
        if os.path.exists(match_csv):
            df_match = pd.read_csv(match_csv)
            for _, row in df_match.sample(min(50, len(df_match))).iterrows():
                p1 = os.path.join(lfw_dir, "lfw-deepfunneled", "lfw-deepfunneled", row['name'], f"{row['name']}_{str(row['imagenum1']).zfill(4)}.jpg")
                p2 = os.path.join(lfw_dir, "lfw-deepfunneled", "lfw-deepfunneled", row['name'], f"{row['name']}_{str(row['imagenum2']).zfill(4)}.jpg")
                if os.path.exists(p1) and os.path.exists(p2):
                    pairs.append((p1, p2, True))
        
        # Negatives
        if os.path.exists(mismatch_csv):
            df_mismatch = pd.read_csv(mismatch_csv)
            for _, row in df_mismatch.sample(min(100, len(df_mismatch))).iterrows():
                p1 = os.path.join(lfw_dir, "lfw-deepfunneled", "lfw-deepfunneled", row['name'], f"{row['name']}_{str(row['imagenum1']).zfill(4)}.jpg")
                p2 = os.path.join(lfw_dir, "lfw-deepfunneled", "lfw-deepfunneled", row['name.1'], f"{row['name.1']}_{str(row['imagenum2']).zfill(4)}.jpg")
                if os.path.exists(p1) and os.path.exists(p2):
                    pairs.append((p1, p2, False))
                
        return pairs

    def load_kyc_pairs(self, base_dir, annotations_json, n_pairs=100):
        """
        Load KYC Aadhaar/PAN pairs with Hard Negative Mining (Gender + Age ±5 yrs).
        """
        from datetime import datetime
        with open(annotations_json, 'r') as f:
            data = json.load(f)
            
        positives = []
        groups = {}
        processed_data = [] # List of dicts with calculated age
        
        current_year = datetime.now().year
        
        for item in data:
            rel_path = item['image_path'].replace('\\', '/')
            if rel_path.startswith('dataset/'): rel_path = rel_path[len('dataset/'):]
            full_path = os.path.join(base_dir, rel_path)
            
            if not os.path.exists(full_path): continue
            
            # Calculate Age
            try:
                dob_year = datetime.strptime(item['dob'], '%d/%m/%Y').year
                age = current_year - dob_year
            except:
                age = 30 # Default if failed
                
            item['full_path'] = full_path
            item['age'] = age
            processed_data.append(item)
            
            gid = item.get('duplicate_group_id')
            if gid:
                if gid not in groups: groups[gid] = []
                groups[gid].append(full_path)
        
        # 1. Positives
        for gid, files in groups.items():
            if len(files) >= 2:
                for i in range(len(files)):
                    for j in range(i + 1, len(files)):
                        positives.append((files[i], files[j], True))
        
        if len(positives) > n_pairs:
            import random
            positives = random.sample(positives, n_pairs)
            
        # 2. Hard Negatives (Same Gender, Same Age ± 5)
        negatives = []
        target_neg = len(positives)
        
        print(f"KYC Loader: Mining {target_neg} Hard Negatives...")
        
        attempts = 0
        while len(negatives) < target_neg and attempts < 2000:
            attempts += 1
            idx1, idx2 = np.random.choice(len(processed_data), 2, replace=False)
            i1, i2 = processed_data[idx1], processed_data[idx2]
            
            # Must be different persons
            if i1.get('duplicate_group_id') and i1.get('duplicate_group_id') == i2.get('duplicate_group_id'):
                continue
            if not i1.get('duplicate_group_id') and i1['name'] == i2['name']:
                continue
                
            # Hard Negative criteria
            same_gender = i1['gender'] == i2['gender']
            similar_age = abs(i1['age'] - i2['age']) <= 5
            
            if same_gender and similar_age:
                negatives.append((i1['full_path'], i2['full_path'], False))
        
        # Fill remaining with random negatives if mining is too slow
        while len(negatives) < target_neg:
            idx1, idx2 = np.random.choice(len(processed_data), 2, replace=False)
            negatives.append((processed_data[idx1]['full_path'], processed_data[idx2]['full_path'], False))
            
        print(f"KYC Loader: {len(positives)} Positives, {len(negatives)} Negatives mined.")
        return positives + negatives

    def run_benchmark(self, pairs, name="Benchmark", simulate_selfie=False):
        """
        Run verification on pairs.
        """
        scores = []
        labels = []
        quality_history = []
        
        print(f"Running {name} on {len(pairs)} pairs (Simulate Selfie: {simulate_selfie})...")
        
        tmp_dir = "temp_selfies_2_5"
        if simulate_selfie and not os.path.exists(tmp_dir): os.makedirs(tmp_dir)
        
        success_count = 0
        fail_count = 0
        for i, (p1, p2, is_same) in enumerate(tqdm(pairs)):
            path1, path2 = p1, p2
            
            if simulate_selfie:
                img2 = cv2.imread(p2)
                if img2 is not None:
                    selfie = SelfieSimulator.simulate(img2)
                    tmp_path = os.path.join(tmp_dir, f"sim_{i}.jpg")
                    cv2.imwrite(tmp_path, selfie)
                    path2 = tmp_path
            
            res = self.matcher.verify(path1, path2)
            if "similarity_score" in res:
                scores.append(res["similarity_score"])
                labels.append(1 if is_same else 0)
                quality_history.append(res.get("quality_scores", [0.5, 0.5]))
                success_count += 1
            else:
                fail_count += 1
            
            if simulate_selfie and os.path.exists(path2) and tmp_dir in path2:
                os.remove(path2)
        
        print(f"Benchmark {name} done. Success: {success_count}, Failed: {fail_count}")
        return np.array(scores), np.array(labels), np.array(quality_history)

    def analyze_results(self, scores, labels, name="Report", output_prefix=""):
        if len(labels) == 0: return {"name": name, "error": "No data"}
        
        fpr, tpr, thresholds = roc_curve(labels, scores)
        roc_auc = auc(fpr, tpr)
        
        # 1. Plot ROC
        plt.figure(figsize=(10, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:0.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
        plt.xlabel('False Positive Rate (FAR)')
        plt.ylabel('True Positive Rate (1 - FRR)')
        plt.title(f'ROC - {name}')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_prefix}ROC_P25_{name}.png")
        plt.close()
        
        # 2. Find Threshold for FAR < 1%
        if len(np.unique(labels)) < 2:
            return {"name": name, "error": "Single class"}

        # Use 1% FAR target
        idx = np.where(fpr <= 0.01)[0][-1]
        best_threshold = thresholds[idx]
        actual_far = fpr[idx]
        actual_tpr = tpr[idx]
        actual_frr = 1 - actual_tpr
        
        preds = (scores >= best_threshold).astype(int)
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds)
        
        # 3. Score distribution
        plt.figure(figsize=(10, 6))
        plt.hist(scores[labels==1], bins=30, alpha=0.5, label='Positive Scores')
        plt.hist(scores[labels==0], bins=30, alpha=0.5, label='Negative Scores')
        plt.axvline(best_threshold, color='red', linestyle='--', label=f'Threshold @ {best_threshold:.3f}')
        plt.title(f'Score Distribution - {name}')
        plt.legend()
        plt.savefig(f"{output_prefix}DIST_P25_{name}.png")
        plt.close()

        metrics = {
            "name": name,
            "auc": round(roc_auc, 4),
            "threshold": round(best_threshold, 4),
            "far": round(actual_far * 100, 2),
            "frr": round(actual_frr * 100, 2),
            "accuracy": round(acc * 100, 2),
            "f1": round(f1, 4),
            "avg_pos_score": round(float(np.mean(scores[labels==1])), 4) if any(labels==1) else 0,
            "avg_neg_score": round(float(np.mean(scores[labels==0])), 4) if any(labels==0) else 0
        }
        
        return metrics

if __name__ == "__main__":
    if not os.path.exists("reports"): os.makedirs("reports")
    
    matcher = FaceMatcher()
    bench = BiometricBenchmark(matcher)
    
    optimized_reports = []
    
    # A. LFW Consistency Check
    lfw_dir = "../data/raw/LFW"
    if os.path.exists(lfw_dir):
        lfw_pairs = bench.load_lfw_pairs(lfw_dir)
        if lfw_pairs:
            s, l, q = bench.run_benchmark(lfw_pairs, name="LFW_Consist")
            optimized_reports.append(bench.analyze_results(s, l, name="LFW_Consist", output_prefix="reports/"))
    
    # B. KYC Benchmark (After Optimization)
    kyc_dir = "../data/raw/KYC_Synthetic dataset"
    kyc_json = "../data/cleaned/KYC_Synthetic dataset/annotations.json"
    
    if os.path.exists(kyc_json):
        # We increase samples to 200 for better calibration stats
        kyc_pairs = bench.load_kyc_pairs(kyc_dir, kyc_json, n_pairs=200)
        
        # Run optimized KYC Standard
        s, l, q = bench.run_benchmark(kyc_pairs, name="KYC_Standard_Opt")
        optimized_reports.append(bench.analyze_results(s, l, name="KYC_Standard_Opt", output_prefix="reports/"))
        
        # Run optimized KYC Selfie Simulated
        s_sim, l_sim, q_sim = bench.run_benchmark(kyc_pairs, name="KYC_Selfie_Sim_Opt", simulate_selfie=True)
        optimized_reports.append(bench.analyze_results(s_sim, l_sim, name="KYC_Selfie_Sim_Opt", output_prefix="reports/"))

    # Generate Optimization Results JSON
    with open("reports/FACE_KYC_OPTIMIZATION_METRICS.json", "w") as f:
        json.dump(optimized_reports, f, indent=4)
    
    print("\nPhase 2.5 Benchmarking Complete.")
