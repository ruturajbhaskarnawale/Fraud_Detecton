import os
if "USERNAME" not in os.environ: os.environ["USERNAME"] = "jotex_user"
if "USER" not in os.environ: os.environ["USER"] = "jotex_user"

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from backend_v2.core.orchestrator import PipelineOrchestrator
from backend_v2.core.ingestion import IngestionHandler
from backend_v2.core.schemas import PipelineResult, IngestionError
from backend_v2.core.config import settings
import json
import logging
logging.basicConfig(level=logging.INFO)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME, version=settings.API_VERSION)
logger = logging.getLogger("api_main")

@app.middleware("http")
async def crash_logger_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        from datetime import datetime
        with open("CRASH.txt", "a") as f:
            f.write(f"\n--- CRASH AT {datetime.now()} ---\n")
            f.write(traceback.format_exc())
            f.write("-" * 30 + "\n")
        raise e

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = PipelineOrchestrator()
ingestor = IngestionHandler()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": settings.API_VERSION,
        "timestamp": os.getenv("CURRENT_TIME", "2026-04-27T14:12:00Z")
    }

@app.post("/verify")
async def verify_identity(
    document: UploadFile = File(...),
    selfie: UploadFile = File(None),
    metadata: str = Form(None)
):
    """
    Main KYC verification endpoint.
    Standardized to handle multi-modal evidence and return structured results.
    """
    # 1. Read content
    doc_content = await document.read()
    selfie_content = await selfie.read() if selfie else None
    
    # Parse metadata JSON
    import json
    metadata_dict = {}
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    
    # Add network context if missing
    if "ip_address" not in metadata_dict:
        metadata_dict["ip_address"] = "127.0.0.1" # Fallback
    
    # 2. Ingestion & Pre-processing
    success, result = ingestor.handle_ingestion(
        document_content=doc_content, 
        document_filename=document.filename,
        selfie_content=selfie_content,
        selfie_filename=selfie.filename if selfie else None,
        metadata=metadata_dict
    )
    
    if not success:
        error: IngestionError = result
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if error.status == "REJECT" else status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.model_dump()
        )
    
    # 3. Execution
    bundle = result
    try:
        pipeline_res = orchestrator.run_with_bundle(bundle)
        return pipeline_res.model_dump(mode='json')
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "module": "ORCHESTRATOR"
        }
        logger.error(f"Pipeline Execution Failed: {json.dumps(error_detail)}")
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/sessions", response_model=List[PipelineResult])
async def list_sessions():
    """
    Returns a history of all verification sessions.
    """
    from backend_v2.database.persistence import PersistenceService
    persistence = PersistenceService()
    try:
        # In a real app, we'd use pagination. For now, return recent ones.
        from backend_v2.database.models import Session
        session_ids = [str(s.id) for s in persistence.db.query(Session).order_by(Session.created_at.desc()).limit(50).all()]
        results = []
        for sid in session_ids:
            res = persistence.get_session_result(sid)
            if res: results.append(res)
        return results
    finally:
        persistence.close()

@app.get("/session/{session_id}", response_model=PipelineResult)
async def get_session(session_id: str):
    """
    Retrieves stored verification results for a specific session.
    """
    from backend_v2.database.persistence import PersistenceService
    persistence = PersistenceService()
    
    try:
        result = persistence.get_session_result(session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return result
    finally:
        persistence.close()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
