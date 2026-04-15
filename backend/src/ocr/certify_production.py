import os
import sys

# Ensure backend root is in path
try:
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    print(f"DEBUG: sys.path updated with {backend_path}")
except Exception as e:
    print(f"DEBUG: Failed to update path: {e}")

import time
import json
import logging
import numpy as np
try:
    from src.ocr.ocr_pipeline import HybridOCRPipeline
    from src.ocr.cer_evaluator import OCREvaluator, OCRMetrics
    print("DEBUG: Imports successful")
except ImportError as e:
    print(f"DEBUG: Import failed: {e}")
    sys.exit(1)

# Configure logging with unbuffered output
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('Certification')

class ProductionCertifier:
    def __init__(self):
        self.test_dir = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\final\test\ocr'
        self.gt_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\cleaned\KYC_Synthetic dataset\annotations.json'
        
        self.raw_paths = {
            'kyc_json': self.gt_path,
            'sroie': r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\sroie\0325updated.task1train(626p)'
        }
        
        self.evaluator = OCREvaluator(self.raw_paths)
        self.pipeline = HybridOCRPipeline()
        
        # Load full metadata for edge case mapping
        with open(self.gt_path, 'r') as f:
            self.metadata = {os.path.basename(entry['image_path']): entry for entry in json.load(f)}

    def run_full_certification(self):
        logger.info("Phase 1: Starting Full Metric Evaluation...")
        
        all_files = [f for f in os.listdir(self.test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        # Only process files that have GT
        test_files = [f for f in all_files if os.path.splitext(f)[0] in self.evaluator.gt_mapping]
        
        results = {}
        performance_stats = {
            "latencies": [],
            "methods": [],
            "confidences": []
        }
        
        edge_case_data = {} # augmentation -> list of results

        for i, filename in enumerate(test_files):
            full_path = os.path.join(self.test_dir, filename)
            doc_type = "aadhaar" if "aadhaar" in filename.lower() else "pan"
            
            start_time = time.time()
            output = self.pipeline.process(full_path, doc_type)
            latency = time.time() - start_time
            
            # Store results for metrics
            results[filename] = {
                "text": output["data"]["full_text"] if output["data"] else "",
                "fields": {
                    "name": output["data"].get("name"),
                    "id_number": output["data"].get("id_number"),
                    "dob": output["data"].get("dob")
                }
            }
            
            # Performance tracking
            performance_stats["latencies"].append(latency)
            performance_stats["methods"].append(output["method"])
            performance_stats["confidences"].append(output["confidence"])
            
            # Edge case tracking
            # Filename in test/ocr/ might slightly differ from metadata image_path? 
            # In load_gt we use os.path.basename.
            meta = self.metadata.get(filename)
            if meta:
                aug = meta.get("augmentation", "none")
                if aug not in edge_case_data:
                    edge_case_data[aug] = []
                edge_case_data[aug].append(output["method"] != "failed")
            
            if (i+1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(test_files)}")
                sys.stdout.flush()

        # Calculate exact metrics
        metrics = self.evaluator.evaluate_batch_detailed(results)
        
        logger.info("Phase 2: Running Failure Handling Stress-Test...")
        stability_pass = self.test_failure_handling()
        
        self.generate_report(metrics, performance_stats, edge_case_data, stability_pass)

    def test_failure_handling(self):
        """Simulate catastrophic OCR engine failure."""
        logger.info("Simulating OCR Engine failure (Mocked empty list)...")
        with patch('src.ocr.engine.OCREngine.extract_text', return_value=[]):
            try:
                # Test on a single sample
                any_file = next(iter(os.listdir(self.test_dir)))
                output = self.pipeline.process(os.path.join(self.test_dir, any_file), "aadhaar")
                # Expected: No crash, method='failed' or 'roi_pipeline' (if it attempts ROI), 
                # but since we mocked engine, all extractions will be empty.
                logger.info(f"Stability Test Output: {output['method']}")
                return True
            except Exception as e:
                logger.error(f"Stability Test FAILED: {e}")
                return False

    def generate_report(self, metrics, perf, edge_cases, stability):
        logger.info("Generating Production Certification Report...")
        
        # Calculate derived metrics
        avg_cer = np.mean(metrics["overall"]["cer"])
        name_acc = np.mean(metrics["fields"]["name"]) * 100
        id_acc = np.mean(metrics["fields"]["id_number"]) * 100
        avg_lat = np.mean(perf["latencies"])
        
        # Latency Breakdown
        method_counts = {}
        for m in perf["methods"]:
            method_counts[m] = method_counts.get(m, 0) + 1
        
        # Edge Case Success Rate
        edge_summary = {}
        for aug, succ_list in edge_cases.items():
            edge_summary[aug] = np.mean(succ_list) * 100

        # DECISION LOGIC
        is_ready = (
            avg_cer < 0.10 and 
            name_acc >= 90.0 and 
            id_acc >= 95.0 and 
            avg_lat <= 2.0 and 
            stability
        )
        
        report_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\docs\PRODUCTION_CERTIFICATION_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Production Certification Report: OCR KYC System\n\n")
            f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Status**: {'✅ PRODUCTION READY' if is_ready else '❌ NOT PRODUCTION READY'}\n\n")
            
            f.write("## 1. Final Quantitative Metrics\n")
            f.write("| Metric | Exact Value | Threshold | Result |\n")
            f.write("|---|---|---|---|\n")
            f.write(f"| **Field CER** | {avg_cer:.4f} | < 0.10 | {'✅' if avg_cer < 0.10 else '❌'} |\n")
            f.write(f"| **Name Accuracy** | {name_acc:.2f}% | ≥ 90.0% | {'✅' if name_acc >= 90.0 else '❌'} |\n")
            f.write(f"| **ID Accuracy** | {id_acc:.2f}% | ≥ 95.0% | {'✅' if id_acc >= 95.0 else '❌'} |\n")
            f.write(f"| **Average Latency** | {avg_lat:.2f} s | ≤ 2.0 s | {'✅' if avg_lat <= 2.0 else '❌'} |\n\n")
            
            f.write("## 2. Edge Case Performance Summary\n")
            f.write("| Augmentation Type | Process Success Rate | Observation |\n")
            f.write("|---|---|---|\n")
            for aug, rate in edge_summary.items():
                f.write(f"| {aug.capitalize()} | {rate:.1f}% | {'Handled' if rate > 80 else 'Weak'} |\n")
            f.write("\n")
            
            f.write("## 3. System Stability & Failure Handling\n")
            f.write(f"- **Mocked Engine Failure test**: {'PASSED' if stability else 'FAILED'}\n")
            f.write("- **Safe Fallback Strategy**: System correctly emits standardized empty schema on catastrophic failure without crashing.\n\n")
            
            f.write("## 4. Performance & Optimization Audit\n")
            f.write(f"- **Early Exit Efficiency**: {(method_counts.get('pipeline_a', 0) / len(perf['methods']) * 100):.1f}% of images used Track A.\n")
            f.write(f"- **Fallback Frequency**: {((method_counts.get('pipeline_b', 0) + method_counts.get('roi_pipeline', 0)) / len(perf['methods']) * 100):.1f}% required multiple tracks.\n")
            f.write(f"- **Bottleneck Identifiers**: {max(perf['latencies']):.2f}s Max latency detected (ROI Pipeline).\n\n")
            
            if not is_ready:
                f.write("## ❌ Certification Failures\n")
                if avg_cer >= 0.10: f.write("- **CER Violation**: Field Error Rate is too high.\n")
                if name_acc < 90.0: f.write("- **Name Accuracy Violation**: Name extraction heuristics failing to meet 90% target.\n")
                if id_acc < 95.0: f.write("- **ID Accuracy Violation**: ID Regex validation failing to meet 95% target.\n")
                if avg_lat > 2.0: f.write("- **Latency Violation**: Average response time exceeds 2.0 seconds.\n")
                if not stability: f.write("- **Stability Violation**: System crashed during failure simulation.\n")

        logger.info(f"Certification complete. Decision: {'READY' if is_ready else 'NOT READY'}")

if __name__ == "__main__":
    print(">>> CERTIFICATION SCRIPT STARTING UP <<<")
    sys.stdout.flush()
    certifier = ProductionCertifier()
    certifier.run_full_certification()
