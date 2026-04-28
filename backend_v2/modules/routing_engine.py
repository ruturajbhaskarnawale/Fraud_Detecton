import numpy as np
from typing import Dict, Any, List, Optional
from backend_v2.core.schemas import DocumentType, IngestionStatus

class RoutingEngine:
    def __init__(self):
        self.version = "v1.0"
        self.quality_threshold_high = 0.75
        self.quality_threshold_mid = 0.45
        self.ocr_confidence_threshold = 0.85
        self.routing_confidence_threshold = 0.65
        self.routing_version = "v2.0"

    def route_session(self, bundles: List[Any], quality_results: List[Any], prep_results: List[Any]) -> Dict[str, Any]:
        """
        Aggregates routing for multi-document sessions.
        """
        routes = []
        session_forensic = False
        
        for i in range(len(bundles)):
            route_item = self.route(bundles[i], quality_results[i], prep_results[i])
            routes.append(route_item)
            if route_item["forensic_required"]:
                session_forensic = True
                
        return {
            "routes": routes,
            "session_level": {"forensic_required": session_forensic},
            "routing_version": self.routing_version
        }

    def route(self, bundle: Any, quality_res: Any, prep_res: Any, ocr_conf: float = 1.0) -> Dict[str, Any]:
        """
        Refined routing for a single document with uncertainty escalation and feedback support.
        """
        reasoning = []
        q_score = quality_res.quality_score
        doc_type = bundle.doc_type
        fallback_used = prep_res.get("fallback_used", False)
        coverage_score = quality_res.checks.get("coverage_score", 1.0)
        
        # 1. Hard Safety Rules
        if q_score < 0.3:
            ocr_engine = "Donut"
            forensic_required = True
            reasoning.append("Critical quality failure (<0.3) -> Forcing Donut + Forensic audit")
        else:
            # Standard OCR Selection
            if q_score >= self.quality_threshold_high:
                ocr_engine = "PaddleOCR"
                reasoning.append(f"High visual quality ({q_score:.2f}) -> PaddleOCR")
            elif q_score >= self.quality_threshold_mid:
                ocr_engine = "PaddleOCR + Fallback TrOCR"
                reasoning.append(f"Borderline quality ({q_score:.2f}) -> Enabling TrOCR fallback")
            else:
                ocr_engine = "Donut"
                reasoning.append(f"Low quality ({q_score:.2f}) -> Donut")

        # 2. Pipeline Strategy (with Coverage Protection)
        if doc_type == DocumentType.ID_CARD:
            # Only use structured if coverage is sufficient
            doc_pipeline = "structured" if coverage_score > 0.6 else "semantic"
            face_required = True
            reasoning.append(f"ID detected (coverage: {coverage_score:.2f}) -> {doc_pipeline} + Biometrics")
        elif doc_type == DocumentType.INVOICE or doc_type == DocumentType.STATEMENT:
            doc_pipeline = "table"
            face_required = False
            reasoning.append("Financial document -> Table pipeline")
        else:
            doc_pipeline = "semantic"
            face_required = False
            reasoning.append("Generic document -> Semantic pipeline")

        # 3. Confidence Formalization (Variance-based)
        # Signals: Quality, Preprocessing, OCR
        prep_conf = prep_res.get("confidence", 0.0)
        signals = [q_score, prep_conf, ocr_conf]
        routing_confidence = 1.0 - float(np.var(signals))
        
        # 4. Forensic & Escalation Logic
        # Case A: Explicit triggers
        forensic_required = (q_score < 0.4) or (fallback_used and q_score < 0.7) or (ocr_conf < self.ocr_confidence_threshold)
        
        # Case B: Uncertainty escalation
        if routing_confidence < self.routing_confidence_threshold:
            forensic_required = True
            reasoning.append(f"Low routing confidence ({routing_confidence:.2f}) -> Escalating to Forensic audit")

        if forensic_required and "Forensic audit" not in "".join(reasoning):
            reasoning.append("Security audit activated due to signal inconsistency/low quality")

        return {
            "document_id": getattr(bundle, "document_id", "unknown"),
            "ocr_engine": ocr_engine,
            "doc_pipeline": doc_pipeline,
            "face_required": face_required,
            "forensic_required": forensic_required,
            "fallback_mode": fallback_used or (ocr_conf < self.ocr_confidence_threshold),
            "routing_confidence": round(routing_confidence, 4),
            "reasoning": reasoning
        }

    def reroute_on_ocr_failure(self, current_route: Dict[str, Any], ocr_conf: float) -> Dict[str, Any]:
        """
        Feedback loop: Triggered if OCR confidence is low.
        """
        if ocr_conf >= self.ocr_confidence_threshold:
            return current_route
            
        new_route = current_route.copy()
        new_route["fallback_mode"] = True
        new_route["forensic_required"] = True
        
        if current_route["ocr_engine"] == "PaddleOCR":
            new_route["ocr_engine"] = "TrOCR"
            new_route["reasoning"].append(f"Low OCR confidence ({ocr_conf:.2f}) -> Rerouting: PaddleOCR -> TrOCR")
        elif current_route["ocr_engine"] == "TrOCR":
            new_route["ocr_engine"] = "Donut"
            new_route["reasoning"].append(f"Low OCR confidence ({ocr_conf:.2f}) -> Rerouting: TrOCR -> Donut")
            
        return new_route
