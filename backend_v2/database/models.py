from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

Base = declarative_base()

# --- Core Identity & Session Tables ---

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    sessions = relationship("Session", back_populates="entity", cascade="all, delete-orphan")
    feature_store = relationship("FeatureStore", uselist=False, back_populates="entity")

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.id', ondelete="CASCADE"), index=True, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    decision = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.0)
    
    device_id = Column(String, index=True)
    ip_address = Column(String, index=True)
    user_agent = Column(Text)
    meta_json = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    entity = relationship("Entity", back_populates="sessions")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="session", cascade="all, delete-orphan")
    document_results = relationship("DocumentResult", back_populates="session", cascade="all, delete-orphan")
    biometric_results = relationship("BiometricResult", back_populates="session", cascade="all, delete-orphan")
    forensic_results = relationship("ForensicResult", back_populates="session", cascade="all, delete-orphan")
    metadata_results = relationship("MetadataResult", back_populates="session", cascade="all, delete-orphan")
    fraud_results = relationship("FraudResult", back_populates="session", cascade="all, delete-orphan")
    risk_results = relationship("RiskResult", back_populates="session", cascade="all, delete-orphan")
    errors = relationship("ModuleError", back_populates="session", cascade="all, delete-orphan")
    decision_history = relationship("DecisionHistory", back_populates="session", cascade="all, delete-orphan")

class Artifact(Base):
    __tablename__ = 'artifacts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    artifact_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String)
    mime_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="artifacts")

# --- AI Module Results ---

class OCRResult(Base):
    __tablename__ = 'ocr_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    raw_text = Column(Text)
    structured_data = Column(JSONB)
    confidence = Column(Float)
    engine_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="ocr_results")

class DocumentResult(Base):
    __tablename__ = 'document_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    document_type = Column(String)
    extracted_fields = Column(JSONB)
    classification_confidence = Column(Float)
    extraction_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="document_results")

class BiometricResult(Base):
    __tablename__ = 'biometric_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    similarity_score = Column(Float)
    liveness_score = Column(Float)
    is_match = Column(Boolean)
    flags = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="biometric_results")

class ForensicResult(Base):
    __tablename__ = 'forensic_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    tamper_score = Column(Float)
    is_altered = Column(Boolean)
    detected_forgeries = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="forensic_results")

class MetadataResult(Base):
    __tablename__ = 'metadata_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    geo_risk = Column(Float)
    device_risk = Column(Float)
    ip_risk = Column(Float)
    is_vpn = Column(Boolean)
    flags = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="metadata_results")

class FraudResult(Base):
    __tablename__ = 'fraud_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    fraud_score = Column(Float)
    signals = Column(JSONB)
    velocity_check = Column(JSONB)
    is_fraudulent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="fraud_results")

class RiskResult(Base):
    __tablename__ = 'risk_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    final_risk_score = Column(Float)
    risk_level = Column(String)
    explanation = Column(JSONB) 
    module_scores = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="risk_results")

# --- Audit & Tracking Tables ---

class ModelVersion(Base):
    __tablename__ = 'model_versions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ModuleError(Base):
    __tablename__ = 'errors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    module_name = Column(String, nullable=False)
    error_message = Column(Text, nullable=False)
    traceback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="errors")

class FeatureStore(Base):
    __tablename__ = 'feature_store'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.id', ondelete="CASCADE"), unique=True, index=True, nullable=False)
    features = Column(JSONB, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    entity = relationship("Entity", back_populates="feature_store")

class DecisionHistory(Base):
    __tablename__ = 'decision_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=False)
    decision = Column(String, nullable=False)
    previous_decision = Column(String)
    actor = Column(String, default="SYSTEM")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="decision_history")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete="CASCADE"), index=True, nullable=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# --- Network & Device Intelligence ---

class DeviceIntelligence(Base):
    __tablename__ = 'device_intelligence'
    device_id = Column(String, primary_key=True)
    fingerprint_hash = Column(String)
    total_attempts = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)

class IPIntelligence(Base):
    __tablename__ = 'ip_intelligence'
    ip_address = Column(String, primary_key=True)
    reputation_score = Column(Float, default=1.0)
    total_sessions = Column(Integer, default=0)
    last_geo_location = Column(String)
    is_proxy_vpn = Column(Boolean, default=False)

# --- JSONB GIN Indexes ---
Index('idx_metadata_results_flags', MetadataResult.flags, postgresql_using='gin')
Index('idx_risk_results_explanation', RiskResult.explanation, postgresql_using='gin')
Index('idx_ocr_results_data', OCRResult.structured_data, postgresql_using='gin')
Index('idx_forensic_results_forgeries', ForensicResult.detected_forgeries, postgresql_using='gin')
Index('idx_fraud_results_signals', FraudResult.signals, postgresql_using='gin')
Index('idx_biometric_results_flags', BiometricResult.flags, postgresql_using='gin')

