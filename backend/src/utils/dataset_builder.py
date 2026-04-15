import os
import shutil
import random
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

class DatasetBuilder:
    def __init__(self, processed_dir, final_dir):
        self.processed_dir = processed_dir
        self.final_dir = final_dir
        self.splits = ["train", "val", "test"]
        for s in self.splits:
            os.makedirs(os.path.join(final_dir, s), exist_ok=True)

    def augment_image(self, img_path, output_path):
        """Apply stochastic augmentation to training samples."""
        try:
            with Image.open(img_path) as img:
                # 1. Random Brightness
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(random.uniform(0.7, 1.3))
                
                # 2. Random Contrast
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(random.uniform(0.7, 1.3))
                
                # 3. Random Blur (subtle)
                if random.random() > 0.7:
                    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 1)))
                
                # 4. Save
                img.save(output_path, 'JPEG', quality=90)
        except Exception as e:
            print(f"Augment error: {e}")
            shutil.copy2(img_path, output_path)

    def split_and_copy(self, task_subdir, train_pct=0.8, val_pct=0.1):
        """Split a processed subdirectory and move to final/."""
        source_dir = os.path.join(self.processed_dir, task_subdir)
        if not os.path.exists(source_dir):
            print(f"Skipping {task_subdir}: Empty")
            return

        files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(files)
        
        n_train = int(len(files) * train_pct)
        n_val = int(len(files) * val_pct)
        
        splits_map = {
            "train": files[:n_train],
            "val": files[n_train:n_train+n_val],
            "test": files[n_train+n_val:]
        }
        
        for s, f_list in splits_map.items():
            target_dir = os.path.join(self.final_dir, s, task_subdir)
            os.makedirs(target_dir, exist_ok=True)
            
            for f in f_list:
                src = os.path.join(source_dir, f)
                dst = os.path.join(target_dir, f)
                
                if s == "train":
                    # Apply augmentation for train set
                    self.augment_image(src, dst)
                else:
                    shutil.copy2(src, dst)
                    
        print(f"Split {task_subdir}: {len(files)} items distributed.")

    def build_metadata(self):
        """Consolidate info for DATA_QUALITY_REPORT."""
        stats = {}
        for s in self.splits:
            stats[s] = {}
            for task in ["ocr", "face", "fraud", "unified"]:
                task_path = os.path.join(self.final_dir, s, task)
                if os.path.exists(task_path):
                    stats[s][task] = len(os.listdir(task_path))
        
        report_path = r'c:\Users\rutur\OneDrive\Desktop\jotex\docs\DATA_QUALITY_REPORT.md'
        with open(report_path, 'w') as f:
            f.write("# Data Quality Report\n\n")
            f.write("## Dataset Split Distribution\n")
            f.write("| Split | OCR | Face | Fraud | Unified |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            for s in self.splits:
                f.write(f"| {s} | {stats[s].get('ocr', 0)} | {stats[s].get('face', 0)} | {stats[s].get('fraud', 0)} | {stats[s].get('unified', 0)} |\n")
        
        print(f"Quality Report generated: {report_path}")

if __name__ == "__main__":
    builder = DatasetBuilder(
        processed_dir=r'c:\Users\rutur\OneDrive\Desktop\jotex\data\processed',
        final_dir=r'c:\Users\rutur\OneDrive\Desktop\jotex\data\final'
    )
    # Split all processed categories
    for task in ["ocr", "face", "fraud", "unified"]:
        builder.split_and_copy(task)
    
    builder.build_metadata()
