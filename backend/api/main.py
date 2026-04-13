from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
import shutil
import logging
from typing import List, Optional

from ..src.pipeline import KYCPipeline
from ..src.database.models import SessionLocal, VerificationRecord, init_db

# Initialize DB
init_db()

app = FastAPI(title="CampusHub Document Fraud Detection API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = KYCPipeline()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/verify")
async def verify_kyc(
    id_card: UploadFile = File(...),
    selfie: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    tracking_id = str(uuid.uuid4())
    
    # Save files
    id_ext = id_card.filename.split(".")[-1]
    id_path = os.path.join(UPLOAD_DIR, f"{tracking_id}_id.{id_ext}")
    with open(id_path, "wb") as buffer:
        shutil.copyfileobj(id_card.file, buffer)
        
    selfie_path = None
    if selfie:
        self_ext = selfie.filename.split(".")[-1]
        selfie_path = os.path.join(UPLOAD_DIR, f"{tracking_id}_selfie.{self_ext}")
        with open(selfie_path, "wb") as buffer:
            shutil.copyfileobj(selfie.file, buffer)
            
    # Run Pipeline
    results = pipeline.process_verification(id_path, selfie_path)
    
    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])
        
    # Save to Database
    db_record = VerificationRecord(
        tracking_id=tracking_id,
        doc_type=results["id_validation"].get("type"),
        id_number=results["id_validation"].get("extracted_fields", {}).get("id_number"),
        name=results["id_validation"].get("extracted_fields", {}).get("name"),
        dob=results["id_validation"].get("extracted_fields", {}).get("dob"),
        risk_score=results["final_decision"].get("risk_score"),
        decision=results["final_decision"].get("decision"),
        reasons=results["final_decision"].get("reasons"),
        tamper_score=results["fraud_validation"]["tampering_results"][0]["tamper_score"] if results["fraud_validation"]["tampering_results"] else 0.0,
        face_match_distance=results["face_validation"].get("similarity", 0.0),
        image_paths={"id": id_path, "selfie": selfie_path}
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return {
        "status": "success",
        "tracking_id": tracking_id,
        "results": results
    }

@app.get("/records")
def list_records(db: Session = Depends(get_db)):
    return db.query(VerificationRecord).order_by(VerificationRecord.timestamp.desc()).all()

@app.get("/records/{tracking_id}")
def get_record(tracking_id: str, db: Session = Depends(get_db)):
    record = db.query(VerificationRecord).filter(VerificationRecord.tracking_id == tracking_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
