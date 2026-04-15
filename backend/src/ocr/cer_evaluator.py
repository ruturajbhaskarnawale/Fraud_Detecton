import Levenshtein
import os
import json

class OCRMetrics:
    @staticmethod
    def calculate_cer(reference, hypothesis):
        """
        Calculate Character Error Rate (CER).
        CER = (I + D + S) / N
        """
        if not reference:
            return 1.0 if hypothesis else 0.0
        
        # Levenshtein distance gives I + D + S
        dist = Levenshtein.distance(reference, hypothesis)
        return dist / len(reference)

    @staticmethod
    def calculate_wer(reference, hypothesis):
        """
        Calculate Word Error Rate (WER).
        """
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        if not ref_words:
            return 1.0 if hyp_words else 0.0
            
        # For word level, we can join with a special char or just compare strings
        # Simplest is to join back with space or use a word-level library
        dist = Levenshtein.distance(" ".join(ref_words), " ".join(hyp_words))
        return dist / len(reference) if len(reference) > 0 else 0

class OCREvaluator:
    def __init__(self, raw_data_paths):
        self.raw_data_paths = raw_data_paths
        self.gt_mapping = {} # filename -> ground_truth_text
        self._load_gt()

    def _load_gt(self):
        # 1. Load SROIE GT (raw text)
        sroie_path = self.raw_data_paths.get('sroie')
        if sroie_path and os.path.exists(sroie_path):
            for root, _, files in os.walk(sroie_path):
                for f in files:
                    if f.endswith('.txt'):
                        base = os.path.splitext(f)[0]
                        with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                            # SROIE format often has bbox info, we just want the text for global CER
                            lines = file.readlines()
                            cleaned_lines = [line.split(',')[-1].strip() for line in lines if len(line.split(',')) >= 9]
                            self.gt_mapping[base] = {
                                "type": "sroie",
                                "full_text": " ".join(cleaned_lines),
                                "fields": {}
                            }

        # 2. Load KYC Synthetic GT (structured)
        kyc_path = self.raw_data_paths.get('kyc_json')
        if kyc_path and os.path.exists(kyc_path):
            with open(kyc_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    img_name = os.path.splitext(os.path.basename(entry['image_path']))[0]
                    self.gt_mapping[img_name] = {
                        "type": entry.get('doc_type', 'unknown'),
                        "full_text": f"{entry.get('name', '')} {entry.get('id_number', '')} {entry.get('dob', '')}",
                        "fields": {
                            "name": entry.get('name'),
                            "id_number": entry.get('id_number'),
                            "dob": entry.get('dob')
                        }
                    }

    def evaluate_batch_detailed(self, predictions):
        """
        predictions: dict of {filename: {text: str, fields: dict}}
        """
        stats = {
            "overall": {"cer": [], "wer": [], "count": 0},
            "fields": {"name": [], "id_number": [], "dob": []},
            "types": {}
        }
        
        for filename, hyp in predictions.items():
            base = os.path.splitext(filename)[0]
            gt = self.gt_mapping.get(base)
            if not gt: continue
            
            # Global Metrics
            cer = OCRMetrics.calculate_cer(gt["full_text"], hyp["text"])
            wer = OCRMetrics.calculate_wer(gt["full_text"], hyp["text"])
            
            stats["overall"]["cer"].append(cer)
            stats["overall"]["wer"].append(wer)
            stats["overall"]["count"] += 1
            
            doc_type = gt["type"]
            if doc_type not in stats["types"]:
                stats["types"][doc_type] = {"cer": [], "count": 0}
            stats["types"][doc_type]["cer"].append(cer)
            stats["types"][doc_type]["count"] += 1
            
            # Field Metrics
            if gt["fields"]:
                for field in stats["fields"].keys():
                    ref_val = gt["fields"].get(field)
                    hyp_val = hyp.get("fields", {}).get(field)
                    if ref_val and hyp_val:
                        # Normalize for comparison
                        match = str(ref_val).lower().replace(" ", "") == str(hyp_val).lower().replace(" ", "")
                        stats["fields"][field].append(1 if match else 0)
        
        return stats

if __name__ == "__main__":
    # Quick test
    ref = "Government of India"
    hyp = "Goverment of Inda"
    print(f"CER: {OCRMetrics.calculate_cer(ref, hyp):.4f}")
