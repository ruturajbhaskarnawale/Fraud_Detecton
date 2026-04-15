import os
import hashlib
import json
from PIL import Image
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DataAudit')

class DataAudit:
    def __init__(self, raw_dir, output_dir):
        self.raw_dir = raw_dir
        self.output_dir = output_dir
        self.report = {
            "total_files": 0,
            "datasets": {},
            "corrupted": [],
            "duplicates": {},
            "invalid_labels": [],
            "anomalies": []
        }
        self.hashes = {} # hash -> path
        self.cleaning_log = []

    def get_file_hash(self, filepath):
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def audit_image(self, filepath):
        try:
            with Image.open(filepath) as img:
                img.verify() # Basic verification
            # Re-open for resolution check (verify() closes it)
            with Image.open(filepath) as img:
                return {"valid": True, "res": img.size, "mode": img.mode}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def run(self):
        logger.info(f"Starting audit on {self.raw_dir}")
        for root, dirs, files in os.walk(self.raw_dir):
            dataset_name = os.path.relpath(root, self.raw_dir).split(os.sep)[0]
            if dataset_name == ".": continue
            
            if dataset_name not in self.report["datasets"]:
                self.report["datasets"][dataset_name] = {"count": 0, "types": {}, "size": 0}
            
            for file in files:
                self.report["total_files"] += 1
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                size = os.path.getsize(filepath)
                
                self.report["datasets"][dataset_name]["count"] += 1
                self.report["datasets"][dataset_name]["size"] += size
                self.report["datasets"][dataset_name]["types"][ext] = self.report["datasets"][dataset_name]["types"].get(ext, 0) + 1
                
                # Metadata validation if JSON
                if ext == '.json':
                    try:
                        with open(filepath, 'r') as f:
                            json.load(f)
                    except:
                        self.report["invalid_labels"].append(filepath)
                        self.cleaning_log.append({"file": filepath, "issue": "Invalid JSON"})

                # Image validation
                if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # Hash check for duplicates
                    f_hash = self.get_file_hash(filepath)
                    if f_hash in self.hashes:
                        self.report["duplicates"][filepath] = self.hashes[f_hash]
                        self.cleaning_log.append({"file": filepath, "issue": "Duplicate", "original": self.hashes[f_hash]})
                    else:
                        self.hashes[f_hash] = filepath
                    
                    # Corruption check
                    audit_res = self.audit_image(filepath)
                    if not audit_res["valid"]:
                        self.report["corrupted"].append({"path": filepath, "error": audit_res["error"]})
                        self.cleaning_log.append({"file": filepath, "issue": "Corrupted", "error": audit_res["error"]})

        self.generate_reports()

    def generate_reports(self):
        # Generate Markdown Report
        md_path = os.path.join(self.output_dir, 'DATA_AUDIT_REPORT.md')
        with open(md_path, 'w') as f:
            f.write(f"# Data Audit Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Files Scanned**: {self.report['total_files']}\n\n")
            
            f.write("## Dataset Summary\n")
            f.write("| Dataset | File Count | Size (MB) | Major Types |\n")
            f.write("| --- | --- | --- | --- |\n")
            for ds, data in self.report["datasets"].items():
                types_str = ", ".join([f"{k} ({v})" for k, v in data["types"].items()])
                f.write(f"| {ds} | {data['count']} | {data['size']/(1024*1024):.2f} | {types_str} |\n")
            
            f.write(f"\n## Anomaly Summary\n")
            f.write(f"- **Corrupted Images**: {len(self.report['corrupted'])}\n")
            f.write(f"- **Duplicate Files**: {len(self.report['duplicates'])}\n")
            f.write(f"- **Invalid Label Files**: {len(self.report['invalid_labels'])}\n")
            
            if self.report['corrupted']:
                f.write("\n### Corrupted Image Samples\n")
                for c in self.report['corrupted'][:10]:
                    f.write(f"- {c['path']}: {c['error']}\n")
        
        # Generate Cleaning Log
        log_path = os.path.join(self.output_dir, 'CLEANING_LOG.json')
        with open(log_path, 'w') as f:
            json.dump(self.cleaning_log, f, indent=2)
            
        logger.info(f"Reports generated in {self.output_dir}")

if __name__ == "__main__":
    raw_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw'
    output_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\docs'
    if not os.path.exists(output_path): os.makedirs(output_path)
    
    auditor = DataAudit(raw_path, output_path)
    auditor.run()
