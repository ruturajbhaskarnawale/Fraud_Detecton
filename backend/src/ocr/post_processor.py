import re

class OCRPostProcessor:
    def __init__(self):
        self.patterns = {
            "aadhaar": r"\d{4}\s\d{4}\s\d{4}|\d{12}",
            "pan": r"[A-Z]{5}[0-9]{4}[A-Z]",
            "dob": r"\d{2}[/-]\d{2}[/-]\d{4}"
        }

    def clean_text(self, text):
        """Remove common OCR noise characters."""
        text = re.sub(r"[|'\"_~`]", "", text)
        # Remove lines that are just whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return "\n".join(lines)

    def validate_id(self, text, doc_type):
        """Extract and validate ID format."""
        if doc_type not in self.patterns:
            return None
            
        match = re.search(self.patterns[doc_type], text)
        if match:
            val = match.group().replace(" ", "")
            return val
        return None

    def standardize_date(self, text):
        """Find and standardize date format."""
        match = re.search(self.patterns["dob"], text)
        if match:
            return match.group().replace("-", "/")
        return None

    def extract_name(self, text):
        """Extract Name using a scoring algorithm (Length, Alphabet-only, Keywords)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return None
            
        noise_keywords = ["GOVERNMENT", "INDIA", "INCOME", "TAX", "DEPARTMENT", "PAN", "DOB", "YEAR", "BIRTH", "SIGNATURE", "FATHER", "MALE", "FEMALE", "AADHAAR", "CARD", "ACCOUNT"]
        
        best_name = None
        highest_score = -999
        
        for line in lines:
            # Skip lines with high digit density
            digits = sum(c.isdigit() for c in line)
            if digits > 2:
                continue
                
            line_upper = line.upper()
            score = len(line)
            
            # Plus points for alphabetical purity
            alphas = sum(c.isalpha() for c in line)
            if alphas > 0 and (alphas / len(line)) > 0.8:
                score += 15
                
            # Minus points for OCR Noise/Keywords
            for kw in noise_keywords:
                if kw in line_upper:
                    score -= 50
                    
            if score > highest_score and alphas > 3:
                highest_score = score
                best_name = line.title() # Normalize capitalization
                
        return best_name

    def format_results(self, raw_text, doc_type):
        """Unified extraction logic."""
        cleaned = self.clean_text(raw_text)
        return {
            "name": self.extract_name(cleaned),
            "id_number": self.validate_id(cleaned, doc_type),
            "dob": self.standardize_date(cleaned),
            "full_text": cleaned
        }
