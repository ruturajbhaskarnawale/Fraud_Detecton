from thefuzz import fuzz

class FraudRules:
    @staticmethod
    def verify_data_consistency(extracted_data_list):
        """
        Check if name/dob matches across multiple documents.
        extracted_data_list: list of results from FieldExtractor.extract()
        """
        issues = []
        if len(extracted_data_list) < 2:
            return issues
            
        names = [d["name"] for d in extracted_data_list if d["name"]]
        dobs = [d["dob"] for d in extracted_data_list if d["dob"]]
        
        # 1. Name Check
        if len(names) >= 2:
            for i in range(len(names)-1):
                score = fuzz.token_sort_ratio(names[i].lower(), names[i+1].lower())
                if score < 80:
                    issues.append({
                        "type": "name_mismatch",
                        "details": f"Name mismatch between documents: '{names[i]}' vs '{names[i+1]}' (Score: {score})",
                        "severity": "high"
                    })
                    
        # 2. DOB Check
        if len(dobs) >= 2:
            for i in range(len(dobs)-1):
                if dobs[i] != dobs[i+1]:
                    issues.append({
                        "type": "dob_mismatch",
                        "details": f"DOB mismatch: '{dobs[i]}' vs '{dobs[i+1]}'",
                        "severity": "high"
                    })
                    
        return issues
