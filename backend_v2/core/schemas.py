from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime

class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REVIEW = "REVIEW"
    ABSTAIN = "ABSTAIN"

class IngestionStatus(str, Enum):
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"
    REVIEW = "REVIEW"

class IngestionError(BaseModel):
    status: IngestionStatus
    reason: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.now)


class DocumentType(str, Enum):
    ID_CARD = "ID_CARD"
    INVOICE = "INVOICE"
    STATEMENT = "STATEMENT"
    CONTRACT = "CONTRACT"
    OTHER = "OTHER"

class QualityResult(BaseModel):
    quality_score: float
    checks: Dict[str, Any]
    status: IngestionStatus
    confidence: float
    failure_reasons: List[str] = []

class EvidenceBundle(BaseModel):

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    raw_input_path: str
    selfie_path: Optional[str] = None
    normalized_images_paths: List[str] = []
    extracted_text: Optional[str] = None
    layout_tokens: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    session_context: Dict[str, Any] = {}
    
    doc_type: Optional[DocumentType] = None
    quality_gate: Optional[QualityResult] = None
    
    # Scores from modules
    scores: Dict[str, float] = {}
    module_details: Dict[str, Any] = {}

class OCRData(BaseModel):
    text: str
    confidence: float
    engine: str = "v1-standard"

class DocumentData(BaseModel):
    document_type: str
    fields: Dict[str, Any]
    confidence: float

class BiometricData(BaseModel):
    face_similarity: float
    liveness_score: float
    status: str
    flags: List[str] = []

class ForensicData(BaseModel):
    tamper_score: float
    is_altered: bool
    forgery_flags: List[str] = []

class MetadataData(BaseModel):
    ip_risk: float
    device_risk: float
    geo_anomaly: bool
    flags: List[str] = []

class FraudData(BaseModel):
    fraud_score: float
    is_fraudulent: bool
    rules_triggered: List[str] = []

class RiskData(BaseModel):
    score: float
    level: str
    breakdown: Dict[str, Any]

class PipelineResult(BaseModel):
    session_id: str
    entity_id: Optional[str] = None
    decision: Decision
    confidence_score: float
    explanation: str
    
    # Standardized Module Results
    ocr: Optional[OCRData] = None
    document: Optional[DocumentData] = None
    biometrics: Optional[BiometricData] = None
    forensics: Optional[ForensicData] = None
    metadata: Optional[MetadataData] = None
    fraud: Optional[FraudData] = None
    risk: Optional[RiskData] = None

    
    module_breakdown: Dict[str, Any] = {} # Legacy support
    image_paths: Dict[str, str] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


