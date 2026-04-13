from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

Base = declarative_base()

class VerificationRecord(Base):
    __tablename__ = 'verification_records'
    
    id = Column(Integer, primary_key=True)
    tracking_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Doc Info
    doc_type = Column(String)
    id_number = Column(String)
    name = Column(String)
    dob = Column(String)
    
    # Fraud Signals
    risk_score = Column(Float)
    decision = Column(String)
    reasons = Column(JSON)
    tamper_score = Column(Float)
    face_match_distance = Column(Float)
    
    # Files
    image_paths = Column(JSON)
    
# DB Setup
# DB Setup (Relative to current working directory)
DB_URL = "sqlite:///data/database/kyc_verification.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
