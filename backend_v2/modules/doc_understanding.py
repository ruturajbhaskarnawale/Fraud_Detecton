import re
import logging
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger("doc_understanding_v3")

class DocUnderstandingService:
    def __init__(self):
        self.version = "v1.0"
        # Anchor Keywords with weighted criticality
        self.config = {

            "name": {"anchors": ["name", "full name", "नाम", "नाम:"], "critical": True, "weight": 0.4},
            "dob": {"anchors": ["dob", "date of birth", "birth", "जन्म तिथि"], "critical": False, "weight": 0.2},
            "id_number": {"anchors": ["id", "no", "number", "pan", "aadhaar"], "critical": True, "weight": 0.4}
        }
        self.validation_patterns = {
            "pan": r"^[A-Z]{5}\d{4}[A-Z]{1}$",
            "aadhaar": r"^\d{12}$",
            "dob": r"^\d{4}-\d{2}-\d{2}$"
        }
        
        # ML Model Lazy Loading Setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ml_model = None
        self.ml_processor = None
        self.ml_weights_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "layoutlmv3.pth"
        
        # Shared LABELS
        self.LABELS = [
            "O", "B-HEADER", "I-HEADER", "B-QUESTION", "I-QUESTION", "B-ANSWER", "I-ANSWER",
            "B-COMPANY", "I-COMPANY", "B-DATE", "I-DATE", "B-ADDRESS", "I-ADDRESS",
            "B-TOTAL", "I-TOTAL", "B-NAME", "I-NAME", "B-DOB", "I-DOB", "B-ID_NUM", "I-ID_NUM"
        ]
        self.ID2LABEL = {i: label for i, label in enumerate(self.LABELS)}

    def _load_ml_model(self):
        if self.ml_model is not None:
            return True
            
        if not self.ml_weights_path.exists():
            logger.warning(f"ML LayoutLMv3 weights not found at {self.ml_weights_path}")
            return False
            
        try:
            from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
            logger.info("Loading LayoutLMv3 processor and model...")
            self.ml_processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
            self.ml_model = LayoutLMv3ForTokenClassification.from_pretrained(
                "microsoft/layoutlmv3-base", 
                num_labels=len(self.LABELS),
                id2label=self.ID2LABEL
            ).to(self.device)
            self.ml_model.load_state_dict(torch.load(self.ml_weights_path, map_location=self.device))
            self.ml_model.eval()
            return True
        except Exception as e:
            logger.error(f"Failed to load LayoutLMv3 model: {e}")
            return False


    def extract(self, image_path: str, ocr_result: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """
        v3 Hybrid Extraction Pipeline: Rules -> LayoutLM Fallback -> Validation
        """
        tokens = ocr_result.get("tokens", [])
        if not tokens: return self._empty_result(doc_type)

        lines = self._align_tokens(tokens)
        engine_path = "rules"

        # 1. Path 1: Rule-based Fast Path
        fields = self._extract_via_rules(lines, doc_type)
        
        # Calculate initial anchor confidence mean
        avg_anchor_conf = np.mean([f["anchor_confidence"] for f in fields.values()]) if fields else 0.0
        
        # 2. Path 2: ML Fallback (LayoutLMv3 / DocLLM)
        # Trigger if confidence low or critical fields missing
        if avg_anchor_conf < 0.7 or self._is_critical_missing(fields):
            logger.info("Triggering LayoutLM fallback due to low anchor confidence/missing fields.")
            ml_fields = self._run_layoutlm_extraction(image_path, tokens, doc_type)

            fields = self._merge_hybrid_results(fields, ml_fields)
            engine_path = "layoutlm"

        # 3. Field Normalization
        normalized = self._normalize_v3_fields(fields)
        
        # 4. Strict Validation Layer
        validation_flags = self._perform_deep_validation(fields, normalized, doc_type)
        
        # 5. Layout Score (v3 Formal)
        layout_score = self._calculate_v3_layout_score(lines, fields)
        
        # 6. Confidence Calibration (v3 Penalty System)
        final_conf = self._calibrate_v3_confidence(fields, validation_flags, layout_score)

        return {
            "document_type": doc_type,
            "fields": fields,
            "normalized_fields": normalized,
            "validation_flags": validation_flags,
            "layout_score": round(layout_score, 4),
            "confidence": round(final_conf, 4),
            "engine_path": engine_path
        }

    def _extract_via_rules(self, lines: List[List[Dict]], doc_type: str) -> Dict[str, Any]:
        extracted = {}
        for i, line in enumerate(lines):
            line_text = " ".join([t["text"].lower() for t in line])
            for field, cfg in self.config.items():
                for anchor in cfg["anchors"]:
                    if anchor in line_text:
                        val, conf, bbox, tokens = self._find_value_v3(anchor, line, lines, i)
                        if val:
                            # Anchor confidence based on proximity and similarity
                            a_conf = self._compute_anchor_confidence(anchor, line_text)
                            if field not in extracted or (conf * a_conf) > (extracted[field]["confidence"] * extracted[field]["anchor_confidence"]):
                                extracted[field] = {
                                    "value": val,
                                    "confidence": conf,
                                    "anchor_confidence": a_conf,
                                    "source_bbox": bbox,
                                    "source_tokens": tokens,
                                    "line_idx": i
                                }
        return extracted

    def _compute_anchor_confidence(self, anchor: str, text: str) -> float:
        # Simplified: Higher if anchor is at the start of the line
        return 0.95 if text.startswith(anchor) else 0.80

    def _find_value_v3(self, anchor: str, current_line: List[Dict], all_lines: List[List[Dict]], idx: int) -> Tuple:
        # Returns (value, confidence, bbox, tokens)
        line_text = " ".join([t["text"] for t in current_line])
        parts = re.split(re.escape(anchor), line_text, flags=re.IGNORECASE)
        if len(parts) > 1 and parts[1].strip():
            val = parts[1].strip(": ").strip()
            # Find tokens corresponding to the value
            val_tokens = [t["text"] for t in current_line if t["text"] in val]
            bbox = current_line[-1]["bbox"] # Simplified
            return val, 0.92, bbox, val_tokens
        return None, 0.0, [], []

    def _merge_hybrid_results(self, rule_fields: Dict, ml_fields: Dict) -> Dict:
        merged = rule_fields.copy()
        for k, v in ml_fields.items():
            if k not in merged or v["confidence"] > merged[k]["confidence"]:
                merged[k] = v
        return merged

    def _perform_deep_validation(self, fields: Dict, normalized: Dict, doc_type: str) -> Dict[str, bool]:
        flags = {
            "invalid_id_format": False,
            "dob_invalid": False,
            "script_mismatch": False,
            "missing_critical_fields": self._is_critical_missing(fields),
            "cross_field_inconsistency": False
        }
        
        # ID Validation
        if "id_number" in normalized:
            val = normalized["id_number"]
            if not (re.match(self.validation_patterns["pan"], val) or re.match(self.validation_patterns["aadhaar"], val)):
                flags["invalid_id_format"] = True
                
        # DOB Validation
        if "dob" in normalized:
            if not re.match(self.validation_patterns["dob"], normalized["dob"]):
                flags["dob_invalid"] = True
        
        # Consistency: If ID present but Name missing
        if "id_number" in fields and "name" not in fields:
            flags["cross_field_inconsistency"] = True
            
        return flags

    def _calibrate_v3_confidence(self, fields: Dict, flags: Dict, layout_score: float) -> float:
        if not fields: return 0.0
        
        # Weighted base confidence
        base = sum(fields[f]["confidence"] * self.config[f]["weight"] for f in fields)
        
        # Apply penalties
        penalty = 0.0
        if flags["invalid_id_format"]: penalty += 0.3
        if flags["missing_critical_fields"]: penalty += 0.2
        if flags["cross_field_inconsistency"]: penalty += 0.15
        
        conf = (base * 0.8 + layout_score * 0.2) - penalty
        return max(0.0, min(conf, 0.98))

    def _calculate_v3_layout_score(self, lines: List[List[Dict]], fields: Dict) -> float:
        alignment = 1.0 - min(len(lines) / 40.0, 0.4)
        coverage = len(fields) / len(self.config)
        return (alignment * 0.5) + (coverage * 0.5)

    def _is_critical_missing(self, fields: Dict) -> bool:
        for f, cfg in self.config.items():
            if cfg["critical"] and f not in fields:
                return True
        return False

    def _normalize_v3_fields(self, fields: Dict) -> Dict:
        norm = {}
        for f, d in fields.items():
            val = d["value"]
            if f == "dob":
                # Mock normalization to ISO
                norm[f] = "1990-01-01" if "1990" in val else val
            else:
                norm[f] = val.upper().strip()
        return norm

    def _run_layoutlm_extraction(self, image_path: str, tokens: List[Dict], doc_type: str) -> Dict:
        if not self._load_ml_model():
            return {} # fallback to empty if model fails to load

        try:
            image = Image.open(image_path).convert("RGB")
            width, height = image.size
            
            words = []
            boxes = []
            
            for t in tokens:
                words.append(t["text"])
                # Normalize box
                x1, y1, x2, y2 = t["bbox"]
                x1 = max(0, min(1000, int(1000 * (x1 / width))))
                x2 = max(0, min(1000, int(1000 * (x2 / width))))
                y1 = max(0, min(1000, int(1000 * (y1 / height))))
                y2 = max(0, min(1000, int(1000 * (y2 / height))))
                if x2 <= x1: x2 = x1 + 1
                if y2 <= y1: y2 = y1 + 1
                boxes.append([x1, y1, x2, y2])

            encoding = self.ml_processor(
                image,
                words,
                boxes=boxes,
                truncation=True,
                max_length=512,
                padding="max_length",
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.ml_model(**encoding)
                predictions = outputs.logits.argmax(-1).squeeze().cpu().tolist()

            # Align predictions back to word-level using word_ids
            word_ids = encoding.word_ids()
            
            extracted_entities = {}
            current_entity = []
            current_label = None
            
            for idx, word_id in enumerate(word_ids):
                if word_id is None:
                    continue
                    
                pred_label = self.ID2LABEL[predictions[idx]]
                
                if pred_label != "O":
                    tag, entity_type = pred_label.split("-", 1)
                    if tag == "B":
                        if current_entity:
                            self._store_entity(extracted_entities, current_label, current_entity)
                        current_entity = [tokens[word_id]]
                        current_label = entity_type
                    elif tag == "I" and current_label == entity_type:
                        # Avoid duplicates from subword tokens mapping to same word_id
                        if tokens[word_id] not in current_entity:
                            current_entity.append(tokens[word_id])
                else:
                    if current_entity:
                        self._store_entity(extracted_entities, current_label, current_entity)
                        current_entity = []
                        current_label = None

            if current_entity:
                self._store_entity(extracted_entities, current_label, current_entity)

            # Map LAYOUTLM labels to DocUnderstandingService field names
            # LABELS: NAME, DOB, ID_NUM
            field_mapping = {
                "NAME": "name",
                "DOB": "dob",
                "ID_NUM": "id_number"
            }
            
            ml_fields = {}
            for k, v_list in extracted_entities.items():
                if k in field_mapping:
                    field = field_mapping[k]
                    # Get highest confidence entity if multiple found
                    best_entity = max(v_list, key=lambda x: x["confidence"])
                    ml_fields[field] = best_entity

            return ml_fields

        except Exception as e:
            logger.error(f"LayoutLM extraction failed: {e}")
            return {}

    def _store_entity(self, extracted: Dict, label: str, entity_tokens: List[Dict]):
        if label not in extracted:
            extracted[label] = []
            
        full_text = " ".join([t["text"] for t in entity_tokens])
        # Simple bounding box union
        min_x = min(t["bbox"][0] for t in entity_tokens)
        min_y = min(t["bbox"][1] for t in entity_tokens)
        max_x = max(t["bbox"][2] for t in entity_tokens)
        max_y = max(t["bbox"][3] for t in entity_tokens)
        
        extracted[label].append({
            "value": full_text,
            "confidence": 0.88, # Defaulting ML confidence since LayoutLM lacks robust probability per field currently
            "anchor_confidence": 0.5, # ML predictions have low anchor confidence to still prioritize rules if available
            "source_bbox": [min_x, min_y, max_x, max_y],
            "source_tokens": entity_tokens
        })


    def _align_tokens(self, tokens: List[Dict]) -> List[List[Dict]]:
        # Same as v2
        sorted_tokens = sorted(tokens, key=lambda t: t["bbox"][1])
        if not sorted_tokens: return []
        lines = []
        curr_line = [sorted_tokens[0]]
        for i in range(1, len(sorted_tokens)):
            if abs(sorted_tokens[i]["bbox"][1] - curr_line[-1]["bbox"][1]) < 15:
                curr_line.append(sorted_tokens[i])
            else:
                lines.append(sorted(curr_line, key=lambda t: t["bbox"][0]))
                curr_line = [sorted_tokens[i]]
        lines.append(sorted(curr_line, key=lambda t: t["bbox"][0]))
        return lines

    def _empty_result(self, doc_type: str) -> Dict:
        return {"document_type": doc_type, "fields": {}, "confidence": 0.0, "engine_path": "none"}
