import re

class DocumentClassifier:
    def __init__(self):
        # Keyword mappings for different document types
        self.keywords = {
            "aadhaar": ["aadhaar", "government of india", "unique identification authority", "vid :", "male", "female"],
            "pan": ["income tax department", "permanent account number", "govt. of india", "signature"],
            "invoice": ["invoice", "tax invoice", "total amount", "description", "qty", "rate", "bill to"],
            "receipt": ["receipt", "bill", "cash", "amount paid", "thank you"]
        }

    def classify(self, text):
        """
        Classify document based on keyword frequency.
        Returns the detected doc_type.
        """
        text_lower = text.lower()
        scores = {doc_type: 0 for doc_type in self.keywords}
        
        for doc_type, kws in self.keywords.items():
            for kw in kws:
                if kw in text_lower:
                    scores[doc_type] += 1
        
        # Get doc_type with highest score
        best_match = max(scores, key=scores.get)
        if scores[best_match] > 0:
            return best_match
        
        return "unknown"
