import io
import uuid
import time
import os
import logging
import json
from PIL import Image
import fitz  # PyMuPDF
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from backend_v2.core.schemas import IngestionStatus, IngestionError, EvidenceBundle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

class IngestionHandler:
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    
    # File Signatures (Magic Numbers)
    SIGNATURES = {
        b"\xff\xd8\xff": "image/jpeg",
        b"\x89PNG\r\n\x1a\n": "image/png",
        b"%PDF-": "application/pdf"
    }

    def __init__(self, uploads_dir: str = "uploads/backend_v2"):
        self.uploads_dir = uploads_dir
        os.makedirs(self.uploads_dir, exist_ok=True)

    def handle_ingestion(self, document_content: bytes, document_filename: str, selfie_content: Optional[bytes] = None, selfie_filename: Optional[str] = None, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
        """
        Validates, hardens, and prepares the input for the pipeline.
        Returns (True, EvidenceBundle) or (False, IngestionError).
        """
        start_time = time.time()
        
        # 1. Size Check (Document)
        if len(document_content) > self.MAX_SIZE:
            return self._fail(IngestionStatus.REJECT, "Document size exceeds 10MB limit", "SIZE_EXCEEDED", start_time)

        # 2. Strict Magic Number Validation (Document)
        doc_mime = self._detect_mime(document_content)
        if not doc_mime:
            return self._fail(IngestionStatus.REJECT, "Invalid document signature", "INVALID_MIME", start_time)

        # 3. Corruption Detection (Document)
        is_corrupt, err_msg = self._check_corruption(document_content, doc_mime)
        if is_corrupt:
            return self._fail(IngestionStatus.ABSTAIN, f"Document corrupted: {err_msg}", "FILE_CORRUPTED", start_time)

        # 4. Handle Selfie if provided
        selfie_path = None
        if selfie_content:
            if len(selfie_content) > self.MAX_SIZE:
                return self._fail(IngestionStatus.REJECT, "Selfie size exceeds 10MB limit", "SIZE_EXCEEDED", start_time)
            selfie_mime = self._detect_mime(selfie_content)
            if not selfie_mime or "image" not in selfie_mime:
                return self._fail(IngestionStatus.REJECT, "Invalid selfie signature", "INVALID_MIME", start_time)
            
            selfie_id = str(uuid.uuid4())
            selfie_ext = self._get_ext_from_mime(selfie_mime)
            selfie_path = os.path.join(self.uploads_dir, f"selfie_{selfie_id}{selfie_ext}")
            with open(selfie_path, "wb") as f:
                f.write(selfie_content)

        # 5. Save Document securely
        doc_id = str(uuid.uuid4())
        sess_id = session_id or str(uuid.uuid4())
        doc_ext = self._get_ext_from_mime(doc_mime)
        doc_path = os.path.join(self.uploads_dir, f"{doc_id}{doc_ext}")
        with open(doc_path, "wb") as f:
            f.write(document_content)

        initial_metadata = {
            "timestamp": datetime.now().isoformat(),
            "file_type": doc_mime,
            "source": "api/upload",
            "filename": document_filename,
            "size_bytes": len(document_content)
        }
        if metadata:
            initial_metadata.update(metadata)

        bundle = EvidenceBundle(
            document_id=doc_id,
            session_id=sess_id,
            raw_input_path=doc_path,
            selfie_path=selfie_path,
            metadata=initial_metadata
        )

        logger.info(json.dumps({
            "event": "ingestion",
            "status": "success",
            "document_id": doc_id,
            "latency": (time.time() - start_time) * 1000
        }))

        return True, bundle

    def _detect_mime(self, content: bytes) -> Optional[str]:
        for sig, mime in self.SIGNATURES.items():
            if content.startswith(sig):
                return mime
        return None

    def _check_corruption(self, content: bytes, mime: str) -> Tuple[bool, Optional[str]]:
        try:
            if "image" in mime:
                with Image.open(io.BytesIO(content)) as img:
                    img.verify()
                    # Re-open to check if we can actually read pixels
                    img = Image.open(io.BytesIO(content))
                    img.load()
            elif "pdf" in mime:
                with fitz.open(stream=content, filetype="pdf") as doc:
                    if len(doc) == 0:
                        return True, "Empty PDF document"
            return False, None
        except Exception as e:
            return True, str(e)

    def _get_ext_from_mime(self, mime: str) -> str:
        mapping = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf"}
        return mapping.get(mime, ".bin")

    def _fail(self, status: IngestionStatus, reason: str, code: str, start_time: float) -> Tuple[bool, IngestionError]:
        error = IngestionError(status=status, reason=reason, code=code)
        logger.warning(json.dumps({
            "event": "ingestion",
            "status": "failure",
            "reason": reason,
            "code": code,
            "latency": (time.time() - start_time) * 1000
        }))
        return False, error

import json # For logging
