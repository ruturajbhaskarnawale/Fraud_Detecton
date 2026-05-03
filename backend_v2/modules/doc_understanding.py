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
            "name": {"anchors": ["name", "full name", "नाम", "नाम:", "father", "husband"], "critical": True, "weight": 0.4},
            "dob": {"anchors": ["dob", "date of birth", "birth", "जन्म तिथि", "year", "yob"], "critical": False, "weight": 0.2},
            "id_number": {"anchors": ["id", "no", "number", "pan", "aadhaar", "pnd", "acc", "card"], "critical": True, "weight": 0.4}
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
        self.ml_weights_path = Path(__file__).resolve().parent.parent / "models" / "weights" / "layoutlmv3_best copy.pth"
        
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
        Hybrid Document Understanding: LayoutLMv3 (Primary) -> Rules (Fallback) -> Validation
        """
        tokens = ocr_result.get("tokens", [])
        if not tokens:
            return self._empty_result(doc_type, ["NO_OCR_TOKENS"])

        flags = []
        engine_used = "LayoutLMv3"
        start_time = datetime.now()

        # 1. Primary: ML Inference
        fields = self._run_layoutlm_extraction(image_path, tokens, doc_type)
        
        # 2. Fallback: Rules (if ML fails or fields missing)
        if not fields or self._is_critical_missing(fields):
            if not fields:
                flags.append("LAYOUTLM_FAILED_OR_MISSING")
            else:
                flags.append("ML_INCOMPLETE_RESULTS")
            
            rule_fields = self._extract_via_rules(tokens, doc_type)
            fields = self._merge_hybrid_results(fields or {}, rule_fields)
            engine_used = "Hybrid_Fallback"
            flags.append("DOC_MODEL_FALLBACK")

        # 3. Field Normalization
        normalized = self._normalize_fields(fields)
        
        # 4. Field-Level Validation
        validation_results = self._validate_fields(normalized, doc_type)
        flags.extend(validation_results["flags"])
        
        # 5. Reliability Scoring
        avg_field_conf = np.mean([f["confidence"] for f in fields.values()]) if fields else 0.0
        
        has_critical = not self._is_critical_missing(fields)
        if not has_critical:
            flags.append("MISSING_CRITICAL_FIELDS")

        is_reliable = (
            len(fields) >= 2 and 
            has_critical and
            avg_field_conf > 0.6 and 
            not validation_results["critical_failure"] and
            "DOCUMENT_UNRELIABLE" not in flags
        )
        
        if not is_reliable:
            flags.append("DOCUMENT_UNRELIABLE")

        inference_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Extraction complete. Engine: {engine_used}, Reliable: {is_reliable}, Time: {inference_time}s")

        return {
            "document_type": self._classify_doc_type(ocr_result, doc_type),
            "fields": fields,
            "normalized_fields": normalized,
            "overall_confidence": round(float(avg_field_conf), 4),
            "is_reliable": is_reliable,
            "flags": flags,
            "metadata": {
                "engine": engine_used,
                "inference_time": inference_time
            }
        }

    def _extract_via_rules(self, tokens: List[Dict], doc_type: str) -> Dict[str, Any]:
        """
        Robust Regex-based extraction fallback.
        """
        text = " ".join([t["text"] for t in tokens])
        text_upper = text.upper()
        extracted = {}

        # 1. ID Number (PAN / Aadhaar)
        pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text_upper)
        aadhaar_match = re.search(r'\d{4}\s\d{4}\s\d{4}|\d{12}', text)
        
        if pan_match:
            extracted["id_number"] = self._format_rule_field(pan_match.group(), 0.85, tokens)
        elif aadhaar_match:
            extracted["id_number"] = self._format_rule_field(aadhaar_match.group(), 0.85, tokens)

        # 2. DOB
        dob_match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
        if dob_match:
            extracted["dob"] = self._format_rule_field(dob_match.group(), 0.80, tokens)

        # 3. Name (Heuristic)
        name_anchors = ["NAME", "नाम", "FATHER", "HUSBAND"]
        for anchor in name_anchors:
            if anchor in text_upper:
                parts = text_upper.split(anchor)
                if len(parts) > 1:
                    candidate = parts[1].strip(": ").strip()
                    # Split by common next-field anchors to avoid over-capturing
                    stop_words = ["DATE", "DOB", "ID", "NO", "ADDRESS", "FATHER", "नाम", "HUSBAND"]
                    for stop in stop_words:
                        if stop in candidate:
                            candidate = candidate.split(stop)[0].strip()
                    
                    # Cleanup non-alpha noise at start/end
                    candidate = re.sub(r'^[^A-Z]+|[^A-Z]+$', '', candidate)
                    
                    if len(candidate) > 2:
                        extracted["name"] = self._format_rule_field(candidate, 0.75, tokens)
                        break

        return extracted

    def _format_rule_field(self, value: str, conf: float, tokens: List[Dict]) -> Dict:
        return {
            "value": value,
            "confidence": conf,
            "bbox": [0,0,0,0] # Rule-based bbox is hard to pinpoint without complex alignment
        }

    def _normalize_fields(self, fields: Dict) -> Dict:
        normalized = {}
        for k, v in fields.items():
            val = v["value"].strip()
            if k == "dob":
                # Normalize DD/MM/YYYY to YYYY-MM-DD
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
                    try:
                        normalized[k] = datetime.strptime(val, fmt).strftime("%Y-%m-%d")
                        break
                    except: continue
                if k not in normalized: normalized[k] = val # fallback
            elif k == "name":
                normalized[k] = val.upper()
            else:
                normalized[k] = val.replace(" ", "").upper()
        return normalized

    def _validate_fields(self, normalized: Dict, doc_type: str) -> Dict:
        flags = []
        critical_failure = False

        # 1. Name Validation
        if "name" in normalized:
            name = normalized["name"]
            if len(name) < 3 or any(c.isdigit() for c in name):
                flags.append("INVALID_NAME")
        
        # 2. DOB Validation
        if "dob" in normalized:
            dob_val = normalized["dob"]
            try:
                dob_dt = datetime.strptime(dob_val, "%Y-%m-%d")
                age = (datetime.now() - dob_dt).days / 365.25
                if age < 18 or age > 110:
                    flags.append("INVALID_DOB_RANGE")
                    critical_failure = True
            except:
                flags.append("INVALID_DOB_FORMAT")

        # 3. ID Validation
        if "id_number" in normalized:
            id_val = normalized["id_number"]
            is_pan = bool(re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', id_val))
            is_aadhaar = bool(re.match(r'^\d{12}$', id_val))
            if not (is_pan or is_aadhaar):
                flags.append("INVALID_ID_PATTERN")
                critical_failure = True

        return {"flags": flags, "critical_failure": critical_failure}

    def _classify_doc_type(self, ocr_result: Dict, provided_type: str) -> str:
        text = ocr_result.get("text", "").upper()
        if "PAN CARD" in text or "INCOME TAX" in text: return "PAN"
        if "AADHAAR" in text or "UNIQUE IDENTIFICATION" in text: return "AADHAAR"
        return provided_type or "UNKNOWN"

    def _run_layoutlm_extraction(self, image_path: str, tokens: List[Dict], doc_type: str) -> Dict:
        if not self._load_ml_model():
            return {}

        try:
            image = Image.open(image_path).convert("RGB")
            width, height = image.size
            
            words = [t["text"] for t in tokens]
            boxes = []
            for t in tokens:
                x1, y1, x2, y2 = t["bbox"]
                # Normalize to 0-1000
                boxes.append([
                    max(0, min(1000, int(1000 * x1 / width))),
                    max(0, min(1000, int(1000 * y1 / height))),
                    max(0, min(1000, int(1000 * x2 / width))),
                    max(0, min(1000, int(1000 * y2 / height)))
                ])

            encoding = self.ml_processor(
                image, words, boxes=boxes, 
                truncation=True, padding="max_length", return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.ml_model(**encoding)
                predictions = outputs.logits.argmax(-1).squeeze().cpu().tolist()

            word_ids = encoding.word_ids()
            extracted = {}
            
            mapping = {"NAME": "name", "DOB": "dob", "ID_NUM": "id_number"}
            
            for idx, word_id in enumerate(word_ids):
                if word_id is None: continue
                label = self.ID2LABEL[predictions[idx]]
                if label != "O":
                    _, entity = label.split("-")
                    field = mapping.get(entity)
                    if field:
                        if field not in extracted:
                            extracted[field] = {"value": "", "confidence": 0.0, "tokens": []}
                        if tokens[word_id] not in extracted[field]["tokens"]:
                            extracted[field]["tokens"].append(tokens[word_id])
            
            # Post-process extracted clusters
            final_ml = {}
            for field, data in extracted.items():
                sorted_toks = sorted(data["tokens"], key=lambda x: (x["bbox"][1], x["bbox"][0]))
                val = " ".join([t["text"] for t in sorted_toks])
                conf = np.mean([t.get("confidence", 0.9) for t in sorted_toks])
                
                # Bbox union
                min_x = min(t["bbox"][0] for t in sorted_toks)
                min_y = min(t["bbox"][1] for t in sorted_toks)
                max_x = max(t["bbox"][2] for t in sorted_toks)
                max_y = max(t["bbox"][3] for t in sorted_toks)
                
                final_ml[field] = {
                    "value": val,
                    "confidence": round(float(conf), 4),
                    "bbox": [min_x, min_y, max_x, max_y]
                }
            return final_ml

        except Exception as e:
            logger.error(f"LayoutLM Inference failed: {e}")
            return {}

    def _merge_hybrid_results(self, ml: Dict, rules: Dict) -> Dict:
        merged = ml.copy()
        for k, v in rules.items():
            if k not in merged or (v["confidence"] > merged[k]["confidence"]):
                merged[k] = v
        return merged

    def _is_critical_missing(self, fields: Dict) -> bool:
        return "name" not in fields or "id_number" not in fields

    def _empty_result(self, doc_type: str, flags: List[str] = None) -> Dict:
        return {
            "document_type": doc_type,
            "fields": {},
            "normalized_fields": {},
            "overall_confidence": 0.0,
            "is_reliable": False,
            "flags": flags or ["EMPTY_EXTRACTION"]
        }

    def _align_tokens(self, tokens: List[Dict]) -> List[List[Dict]]:
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
