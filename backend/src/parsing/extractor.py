import re
from thefuzz import fuzz

class FieldExtractor:
    def __init__(self):
        self.patterns = {
            "aadhaar_id": r"\d{4}\s\d{4}\s\d{4}",
            "pan_id": r"[A-Z]{5}\d{4}[A-Z]{1}",
            "dob": r"\d{2}[/-]\d{2}[/-]\d{4}",
            "pincode": r"\b\d{6}\b"
        }

    def extract(self, text, doc_type):
        """
        Extract fields based on doc_type.
        """
        results = {
            "id_number": None,
            "dob": None,
            "name": None,
            "pincode": None,
            "raw_text": text
        }
        
        # 1. Regex for IDs
        if doc_type == "aadhaar":
            match = re.search(self.patterns["aadhaar_id"], text)
            if match:
                results["id_number"] = match.group()
        elif doc_type == "pan":
            match = re.search(self.patterns["pan_id"], text)
            if match:
                results["id_number"] = match.group()
                
        # 2. Regex for DOB
        match = re.search(self.patterns["dob"], text)
        if match:
            results["dob"] = match.group()
            
        # 3. Regex for Pincode
        match = re.search(self.patterns["pincode"], text)
        if match:
            results["pincode"] = match.group()
            
        # 4. Heuristic for Name
        results["name"] = self._heuristics_name(text, doc_type)
        
        return results

    def _heuristics_name(self, text, doc_type):
        """
        Attempt to find the name using heuristics.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if doc_type == "pan":
            for i, line in enumerate(lines):
                line_lower = line.lower()
                # Check if "name" is in the line but "father" is NOT
                if "name" in line_lower and "father" not in line_lower:
                    # If it's a "Name: Value" format, split and return value
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) > 1 and len(parts[1].strip()) > 3:
                            return parts[1].strip()
                    # Otherwise return the next line
                    if i + 1 < len(lines):
                        return lines[i+1]
            return lines[0] if lines else None
            
        if doc_type == "aadhaar":
            for line in lines:
                if any(x in line.lower() for x in ["aadhaar", "government", "india", "unique", "gender", "dob"]):
                    continue
                # Hanlde "Name: Value" format
                if ":" in line:
                    parts = line.split(":", 1)
                    if "name" in parts[0].lower() and len(parts) > 1:
                        return parts[1].strip()
                # First non-keyword line with multiple words
                if len(line.split()) >= 2:
                    return line
        
        return None

    def compare_names(self, name1, name2, threshold=80):
        """Compare two names using fuzzy match."""
        if not name1 or not name2:
            return 0
        return fuzz.token_sort_ratio(name1.lower(), name2.lower())
