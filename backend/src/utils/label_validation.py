import json
import os
import re

class LabelValidator:
    def __init__(self, kyc_json, sroie_dir):
        self.kyc_json = kyc_json
        self.sroie_dir = sroie_dir
        self.results = {
            "kyc": {"total": 0, "invalid": [], "missing_fields": 0},
            "sroie": {"total": 0, "invalid": []}
        }

    def validate_kyc(self):
        if not os.path.exists(self.kyc_json):
            return
        with open(self.kyc_json, 'r') as f:
            data = json.load(f)
            self.results["kyc"]["total"] = len(data)
            for entry in data:
                required = ["id", "doc_type", "id_number", "image_path"]
                missing = [r for r in required if r not in entry or not entry[r]]
                if missing:
                    self.results["kyc"]["missing_fields"] += 1
                    self.results["kyc"]["invalid"].append({"id": entry.get("id"), "missing": missing})
                
                # Format check for ID number if possible
                if entry.get("doc_type") == "pan":
                    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', str(entry.get("id_number", ""))):
                        self.results["kyc"]["invalid"].append({"id": entry.get("id"), "issue": "Invalid PAN format"})

    def validate_sroie(self):
        if not os.path.exists(self.sroie_dir):
            return
        files = [f for f in os.listdir(self.sroie_dir) if f.endswith('.txt')]
        self.results["sroie"]["total"] = len(files)
        for f in files:
            path = os.path.join(self.sroie_dir, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                if not lines:
                    self.results["sroie"]["invalid"].append(f)
                    continue
                # SROIE check: each line should have at least 8 commas (bbox) or follow the format
                # (Simple check for existence of text)
                valid_lines = 0
                for line in lines:
                    if len(line.split(',')) >= 9:
                        valid_lines += 1
                if valid_lines == 0:
                    self.results["sroie"]["invalid"].append(f)

    def report(self, output_dir):
        md_path = os.path.join(output_dir, 'LABEL_VALIDATION_REPORT.md')
        with open(md_path, 'w') as f:
            f.write("# Label Validation Report\n\n")
            f.write(f"## KYC Synthetic\n")
            f.write(f"- Total Samples: {self.results['kyc']['total']}\n")
            f.write(f"- Samples with missing fields: {self.results['kyc']['missing_fields']}\n")
            f.write(f"- Invalid Entries: {len(self.results['kyc']['invalid'])}\n")
            
            f.write(f"\n## SROIE\n")
            f.write(f"- Total Files: {self.results['sroie']['total']}\n")
            f.write(f"- Empty/Corrupt Files: {len(self.results['sroie']['invalid'])}\n")
            
            if self.results["kyc"]["invalid"]:
                f.write("\n### KYC Invalid Samples (Top 10)\n")
                for entry in self.results["kyc"]["invalid"][:10]:
                    f.write(f"- {entry}\n")

if __name__ == "__main__":
    kyc_json = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\KYC_Synthetic dataset\annotations.json'
    sroie_dir = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw\sroie\0325updated.task1train(626p)'
    output_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\docs'
    
    validator = LabelValidator(kyc_json, sroie_dir)
    validator.validate_kyc()
    validator.validate_sroie()
    validator.report(output_path)
