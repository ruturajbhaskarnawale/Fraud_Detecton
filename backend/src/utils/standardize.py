import os
import cv2
import logging
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Standardization')

class Standardizer:
    def __init__(self, input_dir, output_dir, target_width=1280):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_width = target_width

    def standardize_image(self, src_path, dst_path):
        # RESUMABILITY: Skip if target already exists
        base_name = os.path.splitext(dst_path)[0]
        final_path = f"{base_name}.jpg"
        if os.path.exists(final_path):
            return True

        try:
            with Image.open(src_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resizing maintaining aspect ratio
                w, h = img.size
                ratio = self.target_width / w
                target_height = int(h * ratio)
                
                img_resized = img.resize((self.target_width, target_height), Image.Resampling.LANCZOS)
                
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                img_resized.save(final_path, 'JPEG', quality=95)
                return True
        except Exception as e:
            logger.error(f"Error standardizing {src_path}: {e}")
            return False

    def run(self):
        logger.info(f"Starting standardization from {self.input_dir}")
        count = 0
        skip_count = 0
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, self.input_dir)
                dst_path = os.path.join(self.output_dir, rel_path)
                
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
                    # Re-check exists inside standardize_image or here
                    base_name = os.path.splitext(dst_path)[0]
                    if os.path.exists(f"{base_name}.jpg"):
                        skip_count += 1
                        continue
                    
                    self.standardize_image(src_path, dst_path)
                    count += 1
                else:
                    # Non-image files (labels), just copy if not exists
                    if os.path.exists(dst_path):
                        skip_count += 1
                        continue
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    try:
                        import shutil
                        shutil.copy2(src_path, dst_path)
                        count += 1
                    except:
                        pass
                
                if (count + skip_count) % 1000 == 0:
                    logger.info(f"Standardized: {count}, Skipped: {skip_count}")

if __name__ == "__main__":
    standardizer = Standardizer(
        input_dir=r'c:\Users\rutur\OneDrive\Desktop\jotex\data\cleaned',
        output_dir=r'c:\Users\rutur\OneDrive\Desktop\jotex\data\standardized'
    )
    standardizer.run()
