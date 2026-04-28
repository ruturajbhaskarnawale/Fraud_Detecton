from typing import Dict
from pydantic import BaseModel, Field

class KYCFeatureSchema(BaseModel):
    """
    Enforced Feature Schema for the Veridex KYC Pipeline.
    All AI modules must return data in this standardized format.
    All scores are normalized to [0, 1].
    """
    ocr_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of text extraction")
    doc_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of document classification")
    doc_completeness: float = Field(..., ge=0.0, le=1.0, description="Completeness of mandatory fields")
    face_similarity: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity of face embeddings")
    liveness_score: float = Field(..., ge=0.0, le=1.0, description="Probability of image being live/real")
    forensic_tamper_score: float = Field(..., ge=0.0, le=1.0, description="Probability of no tampering detected")
    fraud_graph_score: float = Field(..., ge=0.0, le=1.0, description="Risk score from graph topology")
    fraud_tabular_score: float = Field(..., ge=0.0, le=1.0, description="Risk score from tabular session data")
    geo_risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk from geo-anomalies")
    device_risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk from device anomalies")
    session_risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk from session inconsistencies")
    ip_reputation_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk from IP reputation")

def normalize_feature_vector(raw_data: Dict[str, float]) -> Dict[str, float]:
    """
    Ensures all incoming raw module outputs are clipped to [0, 1] 
    and match the frozen schema.
    """
    standard_keys = [
        "ocr_confidence", "doc_confidence", "doc_completeness",
        "face_similarity", "liveness_score", "forensic_tamper_score",
        "fraud_graph_score", "fraud_tabular_score",
        "geo_risk_score", "device_risk_score", "session_risk_score", "ip_reputation_score"
    ]
    
    normalized = {}
    for key in standard_keys:
        val = raw_data.get(key, 0.0)
        normalized[key] = max(0.0, min(1.0, float(val)))
        
    return normalized
