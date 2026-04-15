import os
import json
import shutil
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataCleaning')

def clean_data(raw_dir, cleaned_dir, log_path):
    if not os.path.exists(cleaned_dir):
        os.makedirs(cleaned_dir)
        
    with open(log_path, 'r') as f:
        cleaning_log = json.load(f)
        
    # Set of files to skip
    skip_files = {item['file'] for item in cleaning_log}
    
    total_copied = 0
    for root, dirs, files in os.walk(raw_dir):
        # Skip MACOSX and hidden dirs
        if '__MACOSX' in root or root.split(os.sep)[-1].startswith('.'):
            continue
            
        for file in files:
            source_path = os.path.join(root, file)
            if source_path in skip_files or file.startswith('.') or file.lower() == 'thumbs.db':
                continue
            
            # Maintain relative directory structure
            rel_path = os.path.relpath(root, raw_dir)
            target_dir = os.path.join(cleaned_dir, rel_path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            target_path = os.path.join(target_dir, file)
            try:
                shutil.copy2(source_path, target_path)
                total_copied += 1
            except Exception as e:
                logger.error(f"Failed to copy {source_path}: {e}")
                
    logger.info(f"Step 2 Complete: Copied {total_copied} clean files to {cleaned_dir}")

if __name__ == "__main__":
    raw_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\raw'
    cleaned_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\data\cleaned'
    log_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\docs\CLEANING_LOG.json'
    
    clean_data(raw_path, cleaned_path, log_path)
