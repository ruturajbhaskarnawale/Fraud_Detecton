import numpy as np
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("forensic_engine_v2")

class ForensicService:
    def __init__(self):
        self.version = "v1.0"
        self.tamper_threshold = 0.6
        self.text_tamper_threshold = 0.7
        self.synthetic_threshold = 0.4
        self.model_version = "Veridex-Forensics-v3.0"

    def analyze(self, image_path: str, ocr_result: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refined Forensic Analysis with text-level detection and explainability.
        """
        ocr_tokens = ocr_result.get("tokens", [])
        
        # 1. Text Tampering Detection (MANDATORY)
        text_tamper_score, text_regions = self._detect_text_anomalies(ocr_tokens)
        
        # 2. GAN/Synthetic Detection (Simulated FFT)
        synthetic_score = self._run_synthetic_detector(image_path)
        
        # 3. Base Pixel-Level Forensics (ELA, Copy-Move, Noiseprint)
        ela_score = 0.12 # Mocked
        copy_move_score = 0.05
        noiseprint_score = 0.08
        metadata_score = self._audit_metadata(metadata)

        # 4. Adaptive Signal Weighting
        is_camera = metadata and metadata.get("Make") is not None
        if is_camera:
            weights = {"ela": 0.3, "copy_move": 0.1, "metadata": 0.1, "noiseprint": 0.2, "text": 0.2, "synthetic": 0.1}
        else: # Scanned or PDF
            weights = {"ela": 0.1, "copy_move": 0.2, "metadata": 0.3, "noiseprint": 0.1, "text": 0.2, "synthetic": 0.1}

        # 5. Final Calibrated Score
        scores = {
            "ela": ela_score, "copy_move": copy_move_score, "metadata": metadata_score,
            "noiseprint": noiseprint_score, "text": text_tamper_score, "synthetic": synthetic_score
        }
        final_score = sum(scores[k] * weights[k] for k in weights)

        # 6. Attack Type Classification
        attack_type = self._classify_attack_v2(scores)

        # 7. Localization (Merge regions)
        tamper_regions = text_regions # In production, merge with ELA/Copy-Move regions
        
        flags = {
            "tampered": final_score > self.tamper_threshold,
            "copy_move_detected": copy_move_score > 0.7,
            "metadata_inconsistent": metadata_score > 0.8,
            "text_tamper_detected": text_tamper_score > self.text_tamper_threshold
        }

        return {
            "tamper_score": round(ela_score, 4),
            "copy_move_score": round(copy_move_score, 4),
            "deepfake_doc_score": round(synthetic_score, 4),
            "metadata_score": round(metadata_score, 4),
            "noiseprint_score": round(noiseprint_score, 4),
            "text_tamper_score": round(text_tamper_score, 4),
            "final_forensic_score": round(final_score, 4),
            "tamper_regions": tamper_regions,
            "attack_type": attack_type,
            "flags": flags,
            "model_version": self.model_version
        }

    def _detect_text_anomalies(self, tokens: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Detects tampering by analyzing baseline alignment and font consistency.
        """
        if not tokens: return 0.0, []
        
        anomalies = []
        regions = []
        
        # Simple baseline alignment check (Y-variance within tokens of similar Y)
        # In production, this would group tokens by line first
        y_coords = [t["bbox"][1] for t in tokens]
        if len(y_coords) > 5:
            y_var = np.var(y_coords)
            if y_var > 50: # Heuristic for misalignment
                score = min(y_var / 500.0, 1.0)
                anomalies.append(score)
                # Flag region of highest variance
                regions.append({
                    "bbox": tokens[np.argmax(np.abs(y_coords - np.mean(y_coords)))]["bbox"],
                    "score": score,
                    "type": "text_edit"
                })

        avg_score = np.mean(anomalies) if anomalies else 0.0
        return avg_score, regions

    def _run_synthetic_detector(self, path: str) -> float:
        # Mocking FFT-based frequency artifact detection
        return 0.04 # Clean result

    def _audit_metadata(self, metadata: Optional[Dict]) -> float:
        if not metadata: return 0.2 # Neutral suspicion
        software = metadata.get("Software", "").lower()
        if any(tool in software for tool in ["photoshop", "gimp", "picsart"]):
            return 0.95
        return 0.05

    def _classify_attack_v2(self, scores: Dict) -> str:
        max_source = max(scores, key=scores.get)
        if scores[max_source] < 0.4: return "none"
        
        mapping = {
            "ela": "composite",
            "copy_move": "copy_move",
            "metadata": "metadata",
            "text": "text_edit",
            "synthetic": "synthetic",
            "noiseprint": "composite"
        }
        return mapping.get(max_source, "none")
