import os
import zipfile
import json
import shutil
from pathlib import Path

def bundle_for_colab():
    root = Path.cwd()
    bundle_name = "forensic_colab_bundle.zip"
    
    # Files to include
    code_files = [
        "backend_v2/models/forensic_unet.py",
        "backend_v2/train/forensic_dataset.py",
        "backend_v2/forensic/utils/signals.py"
    ]
    
    data_dirs = [
        "Dataset/forensic"
    ]
    
    manifest_source = "backend_v2/forensic/data/manifest.json"
    
    print(f"Creating {bundle_name}...")
    
    with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add Code Files (flatten structure for easier imports in Colab)
        for cf in code_files:
            src = root / cf
            if src.exists():
                # We'll put them in the root of the zip for easy import
                zipf.write(src, arcname=src.name)
                print(f"Added code: {src.name}")
        
        # 2. Add Data
        for ddir in data_dirs:
            src_dir = root / ddir
            if src_dir.exists():
                print(f"Adding data directory: {ddir} (this may take time)...")
                for file in src_dir.rglob('*'):
                    if file.is_file():
                        # Preserve relative path from Dataset/forensic
                        zipf.write(file, arcname=os.path.join("data", file.relative_to(src_dir)))
        
        # 3. Handle Manifest (Rewrite paths)
        if os.path.exists(manifest_source):
            print("Rewriting manifest paths...")
            with open(manifest_source, "r") as f:
                samples = json.load(f)
            
            new_samples = []
            for s in samples:
                # Original: c:\...\Dataset\forensic\raw\...
                # New: data/raw/...
                img_path = s["image"]
                mask_path = s["mask"]
                
                # Extract relative part
                # Looking for 'forensic' in the path
                if "forensic" in img_path:
                    rel_img = img_path.split("forensic")[-1].lstrip("\\").lstrip("/")
                    rel_mask = mask_path.split("forensic")[-1].lstrip("\\").lstrip("/")
                    
                    s["image"] = os.path.join("data", rel_img).replace("\\", "/")
                    s["mask"] = os.path.join("data", rel_mask).replace("\\", "/")
                    new_samples.append(s)
            
            # Write temp manifest and add to zip
            with open("manifest_colab.json", "w") as f:
                json.dump(new_samples, f, indent=2)
            zipf.write("manifest_colab.json", arcname="manifest.json")
            os.remove("manifest_colab.json")
            print(f"Added manifest.json with {len(new_samples)} samples")

    print(f"\nSUCCESS: {bundle_name} created.")
    print("Now upload this file to your Google Drive.")

if __name__ == "__main__":
    bundle_for_colab()
