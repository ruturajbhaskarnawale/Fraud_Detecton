from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import uuid
import time
import logging
import datetime
import traceback

from src.pipeline import KYCPipeline
from src.database.models import SessionLocal, VerificationRecord, init_db

# Pydantic Schemas
class RecordSchema(BaseModel):
    id: int
    tracking_id: str
    timestamp: datetime.datetime
    doc_type: Optional[str] = "UNKNOWN"
    id_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    risk_score: Optional[float] = 0.0
    decision: Optional[str] = "UNKNOWN"
    reasons: Optional[List[str]] = []
    fraud_confidence: Optional[float] = 0.0
    fraud_status: Optional[str] = "UNKNOWN"
    face_match_distance: Optional[float] = 0.0
    # New Forensic Fields
    quality_check: Optional[Dict[str, Any]] = None
    liveness_status: Optional[str] = None
    raw_ocr_data: Optional[List[Any]] = None
    image_paths: Dict[str, Optional[str]]

    class ConfigDict:
        from_attributes = True

class VerifyResponse(BaseModel):
    status: str
    tracking_id: str
    latency_ms: float
    image_paths: Dict[str, Optional[str]]
    results: Dict[str, Any]

class ErrorResponse(BaseModel):
    status: str
    tracking_id: Optional[str] = None
    error: str

# Initialize DB
init_db()

app = FastAPI(title="CampusHub Document Fraud Detection API (Phase 4)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = KYCPipeline()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount uploads directory to serve images via web URLs
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def transform_record_paths(record: VerificationRecord):
    """Convert absolute system paths to relative web URLs."""
    if not record.image_paths:
        return record
    
    new_paths = {}
    for key, path in record.image_paths.items():
        if path:
            filename = os.path.basename(path)
            new_paths[key] = f"/uploads/{filename}"
        else:
            new_paths[key] = None
    
    record.image_paths = new_paths
    return record

@app.post("/verify", response_model=VerifyResponse, responses={500: {"model": ErrorResponse}})
async def verify_kyc(
    id_card: UploadFile = File(...),
    selfie: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    tracking_id = str(uuid.uuid4())
    
    try:
        # Save files asynchronously
        id_ext = id_card.filename.split(".")[-1]
        id_filename = f"{tracking_id}_id.{id_ext}"
        id_path = os.path.join(UPLOAD_DIR, id_filename)
        
        id_contents = await id_card.read()
        with open(id_path, "wb") as f:
            f.write(id_contents)
            
        selfie_filename = None
        selfie_path = None
        if selfie:
            self_ext = selfie.filename.split(".")[-1]
            selfie_filename = f"{tracking_id}_selfie.{self_ext}"
            selfie_path = os.path.join(UPLOAD_DIR, selfie_filename)
            self_contents = await selfie.read()
            with open(selfie_path, "wb") as f:
                f.write(self_contents)
                
        image_paths = {"id_card": id_path, "selfie": selfie_path}
                
        # Run Pipeline
        results = pipeline.process_verification(id_path, selfie_path)
        
        if "error" in results:
            return JSONResponse(status_code=500, content=ErrorResponse(status="FAILED", tracking_id=tracking_id, error=results["error"]).model_dump())
            
        fraud_val = results.get("fraud_validation", {})
        fraud_conf = fraud_val.get("confidence", 0.0)
        fraud_status = fraud_val.get("status", "UNKNOWN")
        
        # Extract Advanced Forensic Signals
        quality = results.get("id_validation", {}).get("quality", {})
        liveness_val = results.get("face_validation", {})
        liveness_str = "PENDING"
        if selfie:
            liveness_str = "PASSED" if liveness_val.get("liveness_passed") else f"FAILED: {liveness_val.get('liveness_message', 'No Face Detected')}"
            
        # Save to Database
        db_record = VerificationRecord(
            tracking_id=tracking_id,
            doc_type=results["id_validation"].get("type", "UNKNOWN"),
            id_number=results["id_validation"].get("extracted_fields", {}).get("id_number"),
            name=results["id_validation"].get("extracted_fields", {}).get("name"),
            dob=results["id_validation"].get("extracted_fields", {}).get("dob"),
            risk_score=results["final_decision"].get("risk_score", 0.0),
            decision=results["final_decision"].get("decision", "MANUAL_REVIEW"),
            reasons=results["final_decision"].get("reasons", []),
            fraud_confidence=fraud_conf,
            fraud_status=fraud_status,
            face_match_distance=results["face_validation"].get("similarity", 0.0),
            # New Forensic Persistence
            quality_check=quality,
            liveness_status=liveness_str,
            raw_ocr_data=results.get("id_validation", {}).get("raw_ocr_data"),
            image_paths=image_paths
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # Return relative web paths for immediate frontend use
        web_image_paths = {
            "id_card": f"/uploads/{id_filename}",
            "selfie": f"/uploads/{selfie_filename}" if selfie_filename else None
        }
        
        return VerifyResponse(
            status="SUCCESS",
            tracking_id=tracking_id,
            latency_ms=latency_ms,
            image_paths=web_image_paths,
            results=results
        )
        
    except Exception as e:
        logging.error(f"Failed to process API call: {e}")
        logging.error(traceback.format_exc()) # Added for better debug
        return JSONResponse(status_code=500, content=ErrorResponse(status="FAILED", tracking_id=tracking_id, error=str(e)).model_dump())

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "CampusHub Document Fraud Detection API",
        "documentation": "/docs"
    }

@app.get("/records", response_model=List[RecordSchema])
def list_records(db: Session = Depends(get_db)):
    """Retrieve the last 100 verification records from the database."""
    records = db.query(VerificationRecord).order_by(VerificationRecord.timestamp.desc()).limit(100).all()
    return [transform_record_paths(record) for record in records]

@app.get("/records/{tracking_id}", response_model=RecordSchema)
def get_record(tracking_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific verification record by tracking ID."""
    record = db.query(VerificationRecord).filter(VerificationRecord.tracking_id == tracking_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return transform_record_paths(record)
