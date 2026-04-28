import os
import json
import glob
from typing import List, Dict, Any, Generator
from pathlib import Path

class UniversalDataLoader:
    def __init__(self, root_dir: str = "Dataset"):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "unified" / "unified_manifest.json"
        
    def get_unified_manifest(self) -> List[Dict[str, Any]]:
        if not self.manifest_path.exists():
            return []
        with open(self.manifest_path, 'r') as f:
            return json.load(f)

    def load_document_understanding(self) -> List[Dict[str, Any]]:
        path = self.root / "document_understanding"
        # Logic to scan and return structured data
        return self._scan_dir(path)

    def load_face_data(self) -> List[Dict[str, Any]]:
        path = self.root / "face"
        return self._scan_dir(path)

    def load_forensic_data(self) -> List[Dict[str, Any]]:
        path = self.root / "forensic"
        return self._scan_dir(path)

    def load_fraud_data(self) -> List[Dict[str, Any]]:
        path = self.root / "fraud"
        # Typically tabular/csv
        return list(glob.glob(str(path / "*.csv")))

    def load_id_cards(self) -> List[Dict[str, Any]]:
        path = self.root / "id_cards"
        return self._scan_dir(path)

    def load_ocr_data(self) -> List[Dict[str, Any]]:
        path = self.root / "ocr"
        return self._scan_dir(path)

    def _scan_dir(self, path: Path) -> List[Dict[str, Any]]:
        # Generic scanner for image/json pairs
        data = []
        if not path.exists():
            return data
            
        for ext in ['*.jpg', '*.png', '*.jpeg']:
            for img_path in path.rglob(ext):
                item = {"image": str(img_path)}
                # Look for matching json
                json_path = img_path.with_suffix('.json')
                if json_path.exists():
                    with open(json_path, 'r') as f:
                        item["annotation"] = json.load(f)
                data.append(item)
        return data

# Usage example
# loader = UniversalDataLoader()
# face_samples = loader.load_face_data()
