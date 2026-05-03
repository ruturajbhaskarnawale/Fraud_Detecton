import asyncio
import time
import requests
import json
import os
import logging
from sqlalchemy import create_engine, text
from typing import Dict, Any, List

# Configuration
API_URL = "http://127.0.0.1:8000/verify"
DB_URL = "postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("deep_audit")

class DeepAuditor:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.results = []

    def hit_api(self, doc_name: str, metadata: Dict, send_selfie: bool = False, selfie_name: str = None):
        doc_path = os.path.join(DATA_DIR, doc_name)
        if not os.path.exists(doc_path):
            return None, f"File not found: {doc_path}"
        
        files = {'document': open(doc_path, 'rb')}
        if send_selfie:
            s_name = selfie_name or doc_name
            s_path = os.path.join(DATA_DIR, s_name)
            if os.path.exists(s_path):
                files['selfie'] = open(s_path, 'rb')
        
        data = {"metadata": json.dumps(metadata)}
        try:
            start = time.time()
            r = requests.post(API_URL, files=files, data=data, timeout=30.0)
            latency = (time.time() - start) * 1000
            return r, latency
        except Exception as e:
            return None, str(e)

    def verify_db(self, session_id: str):
        try:
            with self.engine.connect() as conn:
                # 1. Check main session
                res = conn.execute(text("SELECT status, decision FROM sessions WHERE id = :sid"), {"sid": session_id}).fetchone()
                if not res:
                    return {"stored": False, "reason": "Session ID not found"}
                
                status, decision = res
                
                # 2. Check if at least some result tables have entries
                ocr = conn.execute(text("SELECT COUNT(*) FROM ocr_results WHERE session_id = :sid"), {"sid": session_id}).scalar()
                risk = conn.execute(text("SELECT COUNT(*) FROM risk_results WHERE session_id = :sid"), {"sid": session_id}).scalar()
                
                return {
                    "stored": True,
                    "status": status,
                    "decision": decision,
                    "has_results": (ocr > 0 and risk > 0)
                }
        except Exception as e:
            return {"stored": False, "error": str(e)}

    async def run_audit(self):
        scenarios = self._get_scenarios()
        logger.info(f"Starting Deep Audit with {len(scenarios)} scenarios...")
        
        for scenario in scenarios:
            logger.info(f"Executing Scenario: {scenario['id']} - {scenario['name']}")
            r, info = self.hit_api(
                scenario['file'], 
                scenario['metadata'], 
                scenario.get('send_selfie', False),
                scenario.get('selfie_file')
            )
            
            audit_entry = {
                "id": scenario["id"],
                "scenario": scenario["name"],
                "expected": scenario["expected"],
                "input_files": [scenario["file"]],
                "api_status": "FAIL",
                "modules": {},
                "db_verification": {},
                "latency_ms": 0,
                "status": "FAIL"
            }
            
            if scenario.get('send_selfie'):
                audit_entry["input_files"].append(scenario.get('selfie_file') or scenario["file"])

            if isinstance(r, requests.Response):
                audit_entry["api_status"] = r.status_code
                audit_entry["latency_ms"] = info
                if r.status_code == 200:
                    res = r.json()
                    audit_entry["modules"] = res
                    audit_entry["actual_decision"] = res.get("decision")
                    
                    # DB Check
                    sid = res.get("session_id")
                    if sid:
                        audit_entry["db_verification"] = self.verify_db(sid)
                    
                    # Success criteria
                    if res.get("decision") == scenario["expected"]:
                        audit_entry["status"] = "PASS"
                    elif scenario["expected"] == "REJECT" and res.get("decision") == "REJECT":
                         audit_entry["status"] = "PASS"
                    elif scenario["expected"] == "REVIEW" and res.get("decision") == "REVIEW":
                         audit_entry["status"] = "PASS"
                    else:
                         audit_entry["status"] = "FAIL"
                else:
                    audit_entry["error"] = r.text
            else:
                audit_entry["error"] = info
            
            self.results.append(audit_entry)
            
        self.generate_report()

    def _get_scenarios(self):
        # 30 scenarios as requested
        base = [
            # Clean ID cases
            {"id": "AUD-001", "name": "Valid User - Mobile App", "file": "clean_id.jpg", "metadata": {"ip": "103.21.54.12", "device_id": "APP_001", "source": "mobile"}, "expected": "ACCEPT"},
            {"id": "AUD-002", "name": "Valid User - Web Browser", "file": "clean_id.jpg", "metadata": {"ip": "152.1.4.11", "device_id": "WEB_001", "source": "web"}, "expected": "ACCEPT"},
            {"id": "AUD-003", "name": "Valid User - High Trust IP", "file": "clean_id.jpg", "metadata": {"ip": "8.8.8.8", "device_id": "TRUST_01"}, "expected": "ACCEPT"},
            {"id": "AUD-004", "name": "Valid User - Scanned PDF Path", "file": "clean_id.jpg", "metadata": {"file_type": "application/pdf"}, "expected": "ACCEPT"},
            {"id": "AUD-005", "name": "Valid User - Low Metadata Suspicion", "file": "clean_id.jpg", "metadata": {"ip": "1.1.1.1"}, "expected": "ACCEPT"},
            
            # Tamper cases
            {"id": "AUD-006", "name": "Tampered Doc - Pixel Edit", "file": "tampered_id.jpg", "metadata": {"filename": "tampered_pixel.jpg"}, "expected": "REJECT"},
            {"id": "AUD-007", "name": "Tampered Doc - Metadata Wipe", "file": "tampered_id.jpg", "metadata": {"Software": "ExifTool", "filename": "forgery.jpg"}, "expected": "REJECT"},
            {"id": "AUD-008", "name": "Tampered Doc - Photoshop Artifacts", "file": "tampered_id.jpg", "metadata": {"Software": "Adobe Photoshop"}, "expected": "REJECT"},
            {"id": "AUD-009", "name": "Tampered Doc - Copy-Move Detected", "file": "tampered_id.jpg", "metadata": {"forensic_override": "COPY_MOVE"}, "expected": "REJECT"},
            {"id": "AUD-010", "name": "Tampered Doc - Text Alteration", "file": "tampered_id.jpg", "metadata": {"text_tamper": 0.9}, "expected": "REJECT"},

            # Biometrics
            {"id": "AUD-011", "name": "Face Mismatch - Real Persons", "file": "clean_id.jpg", "send_selfie": True, "selfie_file": "mismatch_face.jpg", "metadata": {}, "expected": "REJECT"},
            {"id": "AUD-012", "name": "Liveness Failure - Replay", "file": "clean_id.jpg", "send_selfie": True, "selfie_file": "clean_id.jpg", "metadata": {"liveness_score": 0.1}, "expected": "REJECT"},
            {"id": "AUD-013", "name": "Deepfake Face", "file": "clean_id.jpg", "send_selfie": True, "selfie_file": "deepfake_face.jpg", "metadata": {}, "expected": "REJECT"},
            {"id": "AUD-014", "name": "No Face Detected in Selfie", "file": "clean_id.jpg", "send_selfie": True, "selfie_file": "fake_id.jpg", "metadata": {"no_face": True}, "expected": "ABSTAIN"},
            
            # Metadata & Fraud
            {"id": "AUD-015", "name": "High Risk - VPN Detected", "file": "clean_id.jpg", "metadata": {"ip": "vpn_detected"}, "expected": "REVIEW"},
            {"id": "AUD-016", "name": "Critical Risk - TOR Node", "file": "clean_id.jpg", "metadata": {"ip": "tor_exit_node"}, "expected": "REJECT"},
            {"id": "AUD-017", "name": "Fraud - Device Blocklisted", "file": "clean_id.jpg", "metadata": {"device_id": "BLOCKLISTED"}, "expected": "REJECT"},
            {"id": "AUD-018", "name": "Fraud - Geo Mismatch (Extreme)", "file": "clean_id.jpg", "metadata": {"ip_location": "RU", "resident_country": "US"}, "expected": "REVIEW"},
            {"id": "AUD-019", "name": "Velocity - IP Spike", "file": "clean_id.jpg", "metadata": {"metadata_flags": ["IP_VELOCITY_SPIKE"]}, "expected": "REJECT"},
            {"id": "AUD-020", "name": "Mixed Signal - Clean Doc + Proxy", "file": "clean_id.jpg", "metadata": {"ip": "proxy_detected"}, "expected": "REVIEW"},

            # Quality & OCR
            {"id": "AUD-021", "name": "Low Quality - Blurred Input", "file": "clean_id.jpg", "metadata": {"quality_score": 0.15}, "expected": "ABSTAIN"},
            {"id": "AUD-022", "name": "OCR Failure - Unreadable Text", "file": "clean_id.jpg", "metadata": {"ocr_confidence": 0.2}, "expected": "REVIEW"},
            {"id": "AUD-023", "name": "Partial ID Detection", "file": "clean_id.jpg", "metadata": {"coverage_score": 0.4}, "expected": "REVIEW"},
            
            # Synthetic/Edge
            {"id": "AUD-024", "name": "Synthetic ID - AI Generated", "file": "fake_id.jpg", "metadata": {"synthetic_score": 0.9}, "expected": "REJECT"},
            {"id": "AUD-025", "name": "Mixed Fraud - Device Swap + VPN", "file": "clean_id.jpg", "metadata": {"ip": "vpn_detected", "device_risk": 0.8}, "expected": "REJECT"},
            {"id": "AUD-026", "name": "Valid User - Multiple Documents", "file": "clean_id.jpg", "metadata": {"session_id": "MULTI_001"}, "expected": "ACCEPT"},
            {"id": "AUD-027", "name": "Forensic Escalation - Scanned doc + Low Confidence", "file": "clean_id.jpg", "metadata": {"Software": "Scanner", "ocr_confidence": 0.6}, "expected": "REVIEW"},
            {"id": "AUD-028", "name": "Conflict - Real Face + Fake Doc", "file": "fake_id.jpg", "send_selfie": True, "selfie_file": "clean_id.jpg", "metadata": {}, "expected": "REJECT"},
            {"id": "AUD-029", "name": "Liveness - Mask Attack", "file": "clean_id.jpg", "send_selfie": True, "selfie_file": "mismatch_face.jpg", "metadata": {"liveness_status": "SPOOF"}, "expected": "REJECT"},
            {"id": "AUD-030", "name": "Sanity Check - System Default", "file": "clean_id.jpg", "metadata": {}, "expected": "ACCEPT"},
        ]
        return base

    def generate_report(self):
        report_path = os.path.join(os.path.dirname(__file__), "reports", "deep_audit_report.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        total = len(self.results)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Veridex Deep E2E Pipeline Audit Report\n\n")
            f.write(f"**Audit Timestamp**: {time.ctime()}\n")
            f.write(f"**Total Scenarios**: {total}\n")
            f.write(f"**Passed**: {passed}\n")
            f.write(f"**Failed**: {total - passed}\n")
            f.write(f"**Success Rate**: {(passed/total)*100:.2f}%\n\n")
            
            f.write("## Detailed Audit Results\n\n")
            
            for r in self.results:
                f.write(f"### Test ID: {r['id']}\n")
                f.write(f"**Scenario**: {r['scenario']}\n")
                f.write(f"**Input Files**: {', '.join(r['input_files'])}\n\n")
                
                mods = r.get("modules", {})
                
                f.write("#### [INGESTION]\n")
                f.write(f"Status: {r['api_status']}\n")
                f.write(f"Observations: {'Accepted' if r['api_status'] == 200 else 'Failed'}\n\n")
                
                f.write("#### [OCR]\n")
                ocr = mods.get("ocr", {})
                f.write(f"Extracted Text: `{ocr.get('text', 'N/A')[:100]}...`\n")
                f.write(f"Confidence: {ocr.get('confidence', 0.0)}\n")
                f.write(f"Issues: {'Low confidence' if ocr.get('confidence', 1.0) < 0.7 else 'None'}\n\n")
                
                f.write("#### [DOCUMENT]\n")
                doc = mods.get("document", {})
                f.write(f"Fields Extracted: {list(doc.get('fields', {}).keys())}\n")
                f.write(f"Accuracy: {doc.get('confidence', 0.0)}\n\n")
                
                f.write("#### [BIOMETRICS]\n")
                bio = mods.get("biometrics", {})
                f.write(f"Similarity: {bio.get('face_similarity', 0.0)}\n")
                f.write(f"Liveness: {bio.get('liveness_score', 0.0)}\n")
                f.write(f"Issues: {bio.get('flags', [])}\n\n")
                
                f.write("#### [FORENSICS]\n")
                forn = mods.get("forensics", {})
                f.write(f"Tamper Score: {forn.get('tamper_score', 0.0)}\n")
                f.write(f"Flags: {forn.get('forgery_flags', [])}\n\n")
                
                f.write("#### [METADATA]\n")
                meta = mods.get("metadata", {})
                f.write(f"Risk Scores: IP: {meta.get('ip_risk')}, Device: {meta.get('device_risk')}\n")
                f.write(f"Flags: {meta.get('flags', [])}\n\n")
                
                f.write("#### [FRAUD]\n")
                fraud = mods.get("fraud", {})
                f.write(f"Score: {fraud.get('fraud_score', 0.0)}\n")
                f.write(f"Rules Triggered: {fraud.get('rules_triggered', [])}\n\n")
                
                f.write("#### [FUSION]\n")
                risk_breakdown = mods.get("risk", {}).get("breakdown", {})
                f.write(f"Consistency Score: {risk_breakdown.get('consistency', 0.0)}\n")
                f.write(f"Conflicts: {risk_breakdown.get('conflicts', 0.0)}\n\n")
                
                f.write("#### [RISK]\n")
                risk = mods.get("risk", {})
                f.write(f"Score: {risk.get('score', 0.0)}\n")
                f.write(f"Breakdown: {risk.get('breakdown', {})}\n\n")
                
                f.write("#### [DECISION]\n")
                f.write(f"Expected: {r['expected']}\n")
                f.write(f"Actual: {r.get('actual_decision', 'N/A')}\n")
                f.write(f"Correct/Incorrect: {'PASS' if r['status'] == 'PASS' else 'FAIL'}\n\n")
                
                f.write("#### [DATABASE]\n")
                db = r.get("db_verification", {})
                f.write(f"Stored: {db.get('stored', False)}\n")
                f.write(f"Integrity Check: {'OK' if db.get('has_results') else 'Failed'}\n\n")
                
                f.write("#### [API]\n")
                f.write(f"Response Valid: {True if r['api_status'] == 200 else False}\n\n")
                
                f.write("#### PERFORMANCE\n")
                f.write(f"Latency (ms): {r['latency_ms']:.2f}\n")
                f.write(f"Bottlenecks: {'High' if r['latency_ms'] > 5000 else 'None'}\n\n")
                
                f.write(f"**FINAL STATUS: {r['status']}**\n")
                f.write("---\n\n")

        logger.info(f"Report generated at {report_path}")

if __name__ == "__main__":
    auditor = DeepAuditor()
    asyncio.run(auditor.run_audit())
