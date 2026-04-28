import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.modules.decision_engine import DecisionEngine

class AdversarialTester:
    """
    Rigorously tests the KYC pipeline against edge cases and attacks.
    """
    def __init__(self):
        self.engine = DecisionEngine()
        self.results = []

    def run_adversarial_suite(self):
        print("\n=== INITIATING ADVERSARIAL STRESS TEST ===")
        
        # Test Case 1: The 'Masterpiece' Forgery
        # Valid face, valid liveness, but expert-level document tampering
        self._test_case(
            name="Expert Document Tampering",
            features={
                "ocr_confidence": 0.98,
                "doc_confidence": 0.95,
                "doc_completeness": 1.0,
                "face_similarity": 0.92,
                "liveness_score": 0.95,
                "forensic_tamper_score": 0.12, # DETECTED TAMPERING
                "fraud_graph_score": 0.05,
                "fraud_tabular_score": 0.02
            },
            expected="REJECT",
            reason_contain="forensic_tamper_score"
        )

        # Test Case 2: High-Quality Deepfake
        # Valid ID, valid forensics, but fake face
        self._test_case(
            name="High-Quality Deepfake",
            features={
                "ocr_confidence": 0.99,
                "doc_confidence": 0.99,
                "doc_completeness": 1.0,
                "face_similarity": 0.88,
                "liveness_score": 0.08, # DETECTED DEEPFAKE
                "forensic_tamper_score": 0.98,
                "fraud_graph_score": 0.01,
                "fraud_tabular_score": 0.01
            },
            expected="REJECT",
            reason_contain="liveness_score"
        )

        # Test Case 3: Conflicting Signals (Mule Account)
        # Everything looks perfect, but Graph Fraud is high
        self._test_case(
            name="Suspicious Money Mule",
            features={
                "ocr_confidence": 0.95,
                "doc_confidence": 0.95,
                "doc_completeness": 1.0,
                "face_similarity": 0.98,
                "liveness_score": 0.98,
                "forensic_tamper_score": 0.95,
                "fraud_graph_score": 0.72, # HIGH RISK CLUSTER
                "fraud_tabular_score": 0.45
            },
            expected="REJECT",
            reason_contain="fraud_graph_score"
        )

        # Test Case 4: Ambiguous Input (Review)
        # Medium quality across the board
        self._test_case(
            name="Ambiguous Signal Fusion",
            features={
                "ocr_confidence": 0.72,
                "doc_confidence": 0.75,
                "doc_completeness": 0.80,
                "face_similarity": 0.65,
                "liveness_score": 0.70,
                "forensic_tamper_score": 0.68,
                "fraud_graph_score": 0.15,
                "fraud_tabular_score": 0.10
            },
            expected="REVIEW",
            reason_contain=""
        )

        print("\n=== ADVERSARIAL TEST SUMMARY ===")
        self._print_summary()

    def _test_case(self, name, features, expected, reason_contain):
        print(f"[test] Case: {name}")
        res = self.engine.decide(features)
        
        passed = res["decision"] == expected
        if reason_contain and reason_contain not in str(res["factors"]):
            passed = False
            
        self.results.append({
            "name": name,
            "decision": res["decision"],
            "expected": expected,
            "risk_score": res["risk_score"],
            "factors": res["factors"],
            "status": "PASS" if passed else "FAIL"
        })

    def _print_summary(self):
        for r in self.results:
            print(f"{r['status']} | {r['name']} -> Decision: {r['decision']} (Risk: {r['risk_score']})")

if __name__ == "__main__":
    tester = AdversarialTester()
    tester.run_adversarial_suite()
